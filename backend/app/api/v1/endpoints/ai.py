from __future__ import annotations

from typing import Any
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.services.binance_service import BinanceService
from app.services.market_data_service import MarketDataService
from app.services.gemini_service import GeminiService

router = APIRouter(tags=["ai"])
gemini_service = GeminiService()
binance_service = BinanceService()
market_data_service = MarketDataService()


class AIChatRequest(BaseModel):
    message: str | None = Field(default=None)
    prompt: str | None = Field(default=None)
    question: str | None = Field(default=None)
    text: str | None = Field(default=None)
    market: str = "crypto"
    symbol: str | None = None
    timeframe: str | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)
    context: str | None = None

    def get_text(self) -> str:
        return (self.message or self.prompt or self.question or self.text or "").strip()


def _fallback_reply(user_text: str) -> str:
    lowered = user_text.lower()
    if any(word in lowered for word in ["btc", "bitcoin", "eth", "crypto", "bull", "bear"]):
        return (
            "I could not reach Gemini just now, but here is a safe trading read: "
            "wait for confirmation, keep risk small, and avoid entering on emotional spikes. "
            "Check trend, volume, and your invalidation level before acting."
        )
    if any(word in lowered for word in ["eur", "usd", "forex", "gbp", "jpy", "gold"]):
        return (
            "I could not reach Gemini just now, but for forex keep position size small, "
            "respect session volatility, and only trade when structure and momentum agree."
        )
    return (
        "I could not reach Gemini just now. Please try again in a moment, or use the "
        "dashboard and scanner while the model service recovers."
    )


def _looks_like_price_query(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in [
            "current btc price",
            "btc price",
            "bitcoin price",
            "current bitcoin price",
            "what is btc price",
            "what is bitcoin price",
            "btc usdt price",
        ]
    )


def _extract_crypto_symbol(text: str) -> str | None:
    normalized = text.upper()
    matches = re.findall(r"\b[A-Z0-9]{2,12}\b", normalized)
    crypto_candidates = {
        "BTC",
        "BITCOIN",
        "ETH",
        "ETHER",
        "BNB",
        "SOL",
        "XRP",
        "ADA",
        "DOGE",
        "AVAX",
        "LINK",
        "SUI",
        "LTC",
        "TRX",
        "TON",
        "DOT",
        "MATIC",
        "PEPE",
        "SHIB",
        "UNI",
        "XLM",
        "ATOM",
        "AAVE",
        "NEAR",
        "ARB",
        "OP",
        "FIL",
        "TIA",
        "INJ",
        "APT",
    }
    for candidate in matches:
        if candidate in crypto_candidates:
            return f"{'BTC' if candidate in {'BTC', 'BITCOIN'} else candidate}USDT"
    return None


async def _build_live_context(request: AIChatRequest) -> str:
    parts: list[str] = []

    symbol = (request.symbol or "BTCUSDT").upper()
    market = (request.market or "crypto").lower()

    try:
        if market == "crypto":
            price = await binance_service.get_price(symbol)
            ticker = await binance_service.get_ticker_24h(symbol)
            parts.append(
                f"Live crypto data: {symbol} price={price:.2f}, "
                f"24h change={ticker['price_change_percent']:.2f}%, "
                f"high={ticker['high_price']:.2f}, low={ticker['low_price']:.2f}."
            )
        else:
            parts.append(f"User is asking about forex symbol/pair: {symbol}.")
    except Exception as exc:
        parts.append(f"Live price lookup failed for {symbol}: {exc}")

    try:
        overview = await market_data_service.get_enhanced_market_overview()
        parts.append(
            "Market backdrop: "
            f"Fear & Greed={overview['fear_greed_index']} ({overview['fear_greed_classification']}), "
            f"BTC dominance={overview['btc_dominance']}%, "
            f"market cap={overview['market_cap']}."
        )
    except Exception as exc:
        parts.append(f"Market backdrop unavailable: {exc}")

    return "\n".join(parts)


@router.post("/chat")
async def chat(request: AIChatRequest, current_user: dict = Depends(get_current_user)) -> dict:
    user_text = request.get_text()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message is required")

    live_context = await _build_live_context(request)
    detected_symbol = _extract_crypto_symbol(user_text)

    if _looks_like_price_query(user_text) or detected_symbol:
        try:
            symbol = detected_symbol or (request.symbol or "BTCUSDT").upper()
            price = await binance_service.get_price(symbol)
            return {
                "reply": f"{symbol} is currently trading at ${price:,.2f} USD.",
                "mode": "market_data",
                "model": "binance",
                "symbol": symbol,
                "price": price,
            }
        except Exception as exc:
            return {
                "reply": _fallback_reply(user_text),
                "mode": "fallback",
                "model": "fallback",
                "error": str(exc),
            }

    try:
        reply = await gemini_service.chat(
            user_text,
            history=request.history,
            context="\n".join(
                part for part in [request.context, live_context] if part and part.strip()
            ),
        )
        return {
            "reply": reply,
            "mode": "gemini",
            "model": "gemini",
        }
    except Exception as exc:
        return {
            "reply": _fallback_reply(user_text),
            "mode": "fallback",
            "model": "fallback",
            "error": str(exc),
        }


@router.post("/analyze")
async def analyze(request: AIChatRequest, current_user: dict = Depends(get_current_user)) -> dict:
    user_text = request.get_text()
    if not user_text:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        detected_symbol = _extract_crypto_symbol(user_text)
        reply = await gemini_service.analyze_market(
            user_text,
            history=request.history,
            context="\n".join(
                part
                for part in [
                    request.context,
                    await _build_live_context(
                        AIChatRequest(
                            message=request.message,
                            prompt=request.prompt,
                            question=request.question,
                            text=request.text,
                            history=request.history,
                            context=(request.context or "")
                            + (f"\nDetected symbol: {detected_symbol}" if detected_symbol else ""),
                        )
                    ),
                ]
                if part and part.strip()
            ),
        )
        return {
            "reply": reply,
            "mode": "gemini",
            "model": "gemini",
        }
    except Exception as exc:
        return {
            "reply": _fallback_reply(user_text),
            "mode": "fallback",
            "model": "fallback",
            "error": str(exc),
        }

# TradeMind AI API Contracts (v1)

Base URL: `/api/v1`
Auth: `Authorization: Bearer <supabase_jwt>`
Response convention:

```json
{
  "success": true,
  "data": {}
}
```

## Health

### `GET /health`
- Public
- Returns service status and UTC timestamp.

## Market

### `GET /market/overview`
- User
- Returns:
  - `btc_price`
  - `eth_price`
  - `market_cap`
  - `fear_greed_index`
  - `btc_dominance`
  - `updated_at`

### `GET /market/trending`
- User
- Returns top gainers and losers list.

## News

### `GET /news`
- User
- Query:
  - `limit` (default 20, max 100)
  - `sentiment` (`bullish|bearish|neutral`, optional)
  - `category` (`crypto|forex|macro`, optional)
- Returns latest news list.

## Signals

### `GET /signals`
- User
- Query:
  - `status` (`open|tp_hit|sl_hit|closed`, optional)
  - `limit` (default 20)

### `GET /signals/{signal_id}`
- User
- Returns signal detail.

### `POST /signals`
- Admin
- Body:
```json
{
  "pair": "BTCUSDT",
  "trade_type": "long",
  "entry": 103500,
  "sl": 102800,
  "tp": 105000,
  "risk_level": "medium"
}
```

### `PATCH /signals/{signal_id}`
- Admin
- Body: partial update for `entry/sl/tp/status/pnl`.

## Devices

### `POST /devices/register`
- User
- Body:
```json
{
  "token": "fcm_device_token",
  "platform": "android"
}
```
- Registers/upserts notification token for signal alerts.

## AI (Phase 2)

### `POST /ai/analyze`
- User
- Body:
```json
{
  "symbol": "BTCUSDT",
  "market": "crypto",
  "timeframe": "4h",
  "question": "Should I long BTC?"
}
```
- Returns AI analysis text + confidence + key indicator summary.

### `POST /ai/chat`
- User
- Body:
```json
{
  "message": "Should I long BTC?",
  "market": "crypto",
  "symbol": "BTCUSDT",
  "timeframe": "4h",
  "context": "TradeMind AI trading assistant",
  "history": []
}
```
- Returns a TradeMind-style response with reply, confidence, bias, and risk notes.

## Scanner (Phase 2)

### `GET /scanner/mtf`
- User
- Query:
  - `market` (`crypto|forex`)
  - `symbols` (`BTCUSDT,ETHUSDT`)
- Returns timeframe alignment and setup strength.

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SignalStatus = Literal["open", "tp_hit", "sl_hit", "closed"]
TradeType = Literal["long", "short"]
RiskLevel = Literal["low", "medium", "high"]


class SignalCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pair: str
    trade_type: TradeType = Field(alias="tradeType")
    entry: float
    sl: float
    tp: float
    risk_level: RiskLevel = Field(alias="riskLevel")


class SignalUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    entry: float | None = None
    sl: float | None = None
    tp: float | None = None
    status: SignalStatus | None = None
    pnl: float | None = None


class SignalOut(BaseModel):
    id: str
    pair: str
    trade_type: TradeType
    entry: float
    sl: float
    tp: float
    status: SignalStatus
    pnl: float
    risk_level: RiskLevel
    created_at: datetime

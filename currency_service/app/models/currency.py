from datetime import datetime

from pydantic import BaseModel


class CurrencyGET(BaseModel):
    symbol: str
    current_price: float
    change_24h: float
    volatility_percent: float
    volume_usd: float
    trades_count: int
    relative_change: float
    volume_ratio: float
    volatility_ratio: float
    trades_ratio: float
    momentum_score: float
    avg_trade_size_usd: float
    intraday_change: float
    distance_from_high: float
    distance_from_low: float
    deviation_from_avg: float
    daily_range_percent: float
    market_state: str
    action_suggestion: str
    raw_processing_time: datetime
    processing_time: datetime


class CurrencySubscription(BaseModel):
    symbol: str

from datetime import datetime

from sqlalchemy import String, Float, BigInteger, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CurrencyStatistic(Base):
    __tablename__ = "currencies_statistics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(10))
    current_price: Mapped[float] = mapped_column(Float)
    change_24h: Mapped[float] = mapped_column(Float)
    volatility_percent: Mapped[float] = mapped_column(Float)
    volume_usd: Mapped[float] = mapped_column(Float)
    trades_count: Mapped[int] = mapped_column(BigInteger)
    relative_change: Mapped[float] = mapped_column(Float)
    volume_ratio: Mapped[float] = mapped_column(Float)
    volatility_ratio: Mapped[float] = mapped_column(Float)
    trades_ratio: Mapped[float] = mapped_column(Float)
    momentum_score: Mapped[float] = mapped_column(Float)
    avg_trade_size_usd: Mapped[float] = mapped_column(Float)
    intraday_change: Mapped[float] = mapped_column(Float)
    distance_from_high: Mapped[float] = mapped_column(Float)
    distance_from_low: Mapped[float] = mapped_column(Float)
    deviation_from_avg: Mapped[float] = mapped_column(Float)
    daily_range_percent: Mapped[float] = mapped_column(Float)
    market_state: Mapped[str] = mapped_column(String)
    action_suggestion: Mapped[str] = mapped_column(String)
    raw_processing_time: Mapped[datetime] = mapped_column(DateTime)
    processing_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )
    valid_from: Mapped[datetime]
    valid_to: Mapped[datetime] = mapped_column(
        server_default=text("'2999-12-31 00:00:00'::timestamp")
    )

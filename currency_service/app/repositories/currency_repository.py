from datetime import datetime
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.currency import CurrencySubscription
from app.tables.currency import CurrencyStatistic, SubscriptionCurrency


class CurrencyRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self.session = session_factory

    async def get_stable_currency_rate(self, email: str) -> Sequence[CurrencyStatistic]:
        async with self.session() as session:
            query = (
                select(CurrencyStatistic)
                .join(
                    SubscriptionCurrency,
                    SubscriptionCurrency.symbol == CurrencyStatistic.symbol,
                )
                .where(
                    func.date(CurrencyStatistic.valid_to)
                    == datetime(2999, 12, 31).date(),
                    SubscriptionCurrency.email == email,
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

    async def create_currency_subscription(self, dto: CurrencySubscription, email: str):
        async with self.session() as session:
            stmt = (
                insert(SubscriptionCurrency)
                .values(**dto.model_dump(), email=email)
                .returning(SubscriptionCurrency)
            )
            result = await session.execute(stmt)
            subscription = result.scalars().one()
            await session.commit()
            return subscription

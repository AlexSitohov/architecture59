from datetime import datetime
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.tables.currency import CurrencyStatistic


class CurrencyRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self.session = session_factory

    async def get_stable_currency_rate(self) -> Sequence[CurrencyStatistic]:
        async with self.session() as session:
            query = select(CurrencyStatistic).where(
                func.date(CurrencyStatistic.valid_to) == datetime(2999, 12, 31).date()
            )
            result = await session.execute(query)
            return result.scalars().all()

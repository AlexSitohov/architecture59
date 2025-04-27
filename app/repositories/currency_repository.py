from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.tables import Currency


class CurrencyRepository:
    def __init__(self, session_factory: AsyncSession):
        self.session = session_factory

    async def get_stable_currency_rate(self):
        return "!!!!!test response"

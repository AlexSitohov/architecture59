from app.repositories.currency_repository import CurrencyRepository


class CurrencyService:
    def __init__(self, currency_repository: CurrencyRepository):
        self.currency_repository = currency_repository

    async def get_stable_currency_rate(self):
        return await self.currency_repository.get_stable_currency_rate()

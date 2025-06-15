from app.models.currency import CurrencySubscription, UserData
from app.repositories.currency_repository import CurrencyRepository


class CurrencyService:
    def __init__(self, currency_repository: CurrencyRepository):
        self.currency_repository = currency_repository

    async def get_stable_currency_rate(self, user_data: UserData):
        return await self.currency_repository.get_stable_currency_rate(user_data.email)

    async def create_currency_subscription(
        self, dto: CurrencySubscription, user_data: UserData
    ):
        return await self.currency_repository.create_currency_subscription(
            dto, user_data.email
        )

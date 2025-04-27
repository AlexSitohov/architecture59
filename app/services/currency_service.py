from app.repositories.currency_repository import CurrencyRepository


class CurrencyService:
    def __init__(self, currency_repository: CurrencyRepository):
        self.__currency_repository = currency_repository

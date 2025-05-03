from datetime import datetime


from app.kafka_service.kafka_service import KafkaService
from app.repositories.currency_repository import CurrencyRepository


class CurrencyService:
    def __init__(
        self, currency_repository: CurrencyRepository, kafka_service: KafkaService
    ):
        self.repository = currency_repository
        self.kafka_service = kafka_service
        self.batch_size = 100
        self.current_batch = []

    async def process_ticker_stream(self):
        """Основной метод обработки потока ticker-сообщений"""
        async for raw_message in self.kafka_service.consume_message():
            try:
                message = raw_message
                print("message", message)
                if message.get("stream", "").endswith("@ticker"):
                    ticker_data = self._transform_ticker_data(message["data"])
                    self.current_batch.append(ticker_data)

                    if len(self.current_batch) >= self.batch_size:
                        await self._flush_batch()
            except Exception as e:
                print(f"Error processing message: {e}")

    @staticmethod
    def _transform_ticker_data(data: dict) -> dict:
        def strip_microseconds(dt: datetime) -> str:
            return dt.replace(microsecond=0).isoformat(sep=" ")

        return {
            "symbol": data["s"],
            "event_time": strip_microseconds(datetime.fromtimestamp(data["E"] / 1000)),
            "price_change": float(data["p"]),
            "price_change_percent": float(data["P"]),
            "weighted_avg_price": float(data["w"]),
            "last_price": float(data["c"]),
            "last_quantity": float(data["Q"]),
            "open_price": float(data["o"]),
            "high_price": float(data["h"]),
            "low_price": float(data["l"]),
            "total_traded_volume": float(data["v"]),
            "total_traded_quote_volume": float(data["q"]),
            "open_time": strip_microseconds(datetime.fromtimestamp(data["O"] / 1000)),
            "close_time": strip_microseconds(datetime.fromtimestamp(data["C"] / 1000)),
            "first_trade_id": data["F"],
            "last_trade_id": data["L"],
            "total_trades": data["n"],
            "processing_time": strip_microseconds(datetime.now()),
        }

    async def _flush_batch(self):
        if not self.current_batch:
            return
        try:
            await self.repository.bulk_insert_ticker_data(self.current_batch)
            print(f"Inserted batch of {len(self.current_batch)} tickers")
            self.current_batch = []
        except Exception as e:
            print(f"Failed to insert batch: {e}")

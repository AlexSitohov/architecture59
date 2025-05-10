from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text


class CurrencyRepository:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def bulk_insert_ticker_data(self, batch: list[dict]):
        if not batch:
            return

        def format_value(value):
            if isinstance(value, str):
                return f"'{value}'"
            return str(value)

        values_rows = []
        for item in batch:
            row = ",".join(
                format_value(item[field])
                for field in [
                    "symbol",
                    "event_time",
                    "price_change",
                    "price_change_percent",
                    "weighted_avg_price",
                    "last_price",
                    "last_quantity",
                    "open_price",
                    "high_price",
                    "low_price",
                    "total_traded_volume",
                    "total_traded_quote_volume",
                    "open_time",
                    "close_time",
                    "first_trade_id",
                    "last_trade_id",
                    "total_trades",
                ]
            )
            values_rows.append(f"({row})")

        values_sql = ",\n".join(values_rows)

        insert_query = f"""
            INSERT INTO binance_ticker_data (
                symbol, event_time, price_change, price_change_percent,
                weighted_avg_price, last_price, last_quantity, open_price,
                high_price, low_price, total_traded_volume, total_traded_quote_volume,
                open_time, close_time, first_trade_id, last_trade_id, total_trades
            )
            VALUES
            {values_sql}
        """

        async with self.session_factory() as session:
            await session.execute(text(insert_query))

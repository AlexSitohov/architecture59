import datetime
import os
import sys
import tempfile

import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

from apache.airflow.providers.clickhouse.hooks.ClickhouseHook import ClickhouseHook

sys.path.insert(0, (os.path.join(os.path.dirname(__file__), "..")))

from src.config import (
    DagGlobalConfig,
)


class UploadProvider:
    def __init__(self, global_config: DagGlobalConfig):
        self.global_config = global_config
        self.__clickhouse_hook = ClickhouseHook.get_connection(
            global_config.clickhouse.connection_id
        ).get_hook()

        self.__postgres_hook = PostgresHook.get_connection(
            global_config.postgresql.connection_id
        ).get_hook()

    def execute(self):
        self.upload()

    def upload(self):
        now = datetime.datetime.utcnow()

        columns = [
            "symbol",
            "current_price",
            "change_24h",
            "volatility_percent",
            "volume_usd",
            "trades_count",
            "relative_change",
            "volume_ratio",
            "volatility_ratio",
            "trades_ratio",
            "momentum_score",
            "avg_trade_size_usd",
            "intraday_change",
            "distance_from_high",
            "distance_from_low",
            "deviation_from_avg",
            "daily_range_percent",
            "raw_processing_time",
            "market_state",
            "action_suggestion",
            "valid_from",
        ]

        query = f"""
            WITH market_metrics AS (SELECT median(price_change_percent)                        AS market_median_change,
                                           avg(total_traded_quote_volume)                      AS market_avg_volume,
                                           median((high_price - low_price) / last_price * 100) AS market_median_volatility,
                                           median(total_trades)                                AS market_median_trades,
                                           quantile(0.9)(price_change_percent)                 AS top_10_percent_change
                                    FROM {self.global_config.clickhouse.table_name}
                                    WHERE event_time > now() - INTERVAL 1 HOUR),
            
                 pair_metrics AS (SELECT symbol,
                                         anyLast(last_price)                                                AS current_price,
                                         anyLast(price_change_percent)                                      AS daily_change_percent,
                                         anyLast((high_price - low_price) / last_price * 100)               AS volatility_percent,
                                         anyLast(total_traded_quote_volume)                                 AS volume_usd,
                                         anyLast(total_trades)                                              AS trades_count,
                                         anyLast(weighted_avg_price)                                        AS avg_price,
                                         anyLast(high_price)                                                AS daily_high,
                                         anyLast(low_price)                                                 AS daily_low,
                                         anyLast(open_price)                                                AS daily_open,
                                         count()                                                            AS updates_count,
                                         avg(if(price_change_percent > 0, total_traded_quote_volume, null)) AS avg_positive_volume,
                                         avg(if(price_change_percent < 0, total_traded_quote_volume, null)) AS avg_negative_volume,
                                         anyLast(processing_time)                                           as processing_time
                                  FROM {self.global_config.clickhouse.table_name}
                                  WHERE event_time > now() - INTERVAL 1 HOUR
                                  GROUP BY symbol
                                  HAVING updates_count > 10
                                     AND volume_usd > 100000),
            
                 enhanced_stats AS (SELECT pm.*,
                                           mm.market_median_change,
                                           mm.market_avg_volume,
                                           mm.market_median_volatility,
                                           mm.market_median_trades,
                                           mm.top_10_percent_change,
            
                                           pm.daily_change_percent - mm.market_median_change              AS relative_change,
                                           pm.volume_usd / mm.market_avg_volume                           AS volume_ratio,
                                           pm.volatility_percent / mm.market_median_volatility            AS volatility_ratio,
                                           pm.trades_count / mm.market_median_trades                      AS trades_ratio,
            
                                           log10(pm.volume_usd + 1) * pm.daily_change_percent             AS momentum_score,
            
            
                                           (pm.current_price - pm.avg_price) / pm.avg_price * 100         AS deviation_from_avg,
                                           if(pm.trades_count = 0, null, pm.volume_usd / pm.trades_count) AS avg_trade_size_usd,
                                           if(pm.daily_low = 0, null, (pm.daily_high - pm.daily_low) / pm.daily_low *
                                                                      100)                                AS daily_range_percent
                                    FROM pair_metrics pm
                                             CROSS JOIN market_metrics mm)
            SELECT symbol,
                   current_price,
                   daily_change_percent                              AS change_24h,
                   volatility_percent,
                   volume_usd,
                   trades_count,
                   relative_change,
                   volume_ratio,
                   volatility_ratio,
                   trades_ratio,
                   momentum_score,
                   avg_trade_size_usd,
                   (current_price - daily_open) / daily_open * 100   AS intraday_change,
                   (daily_high - current_price) / daily_high * 100   AS distance_from_high,
                   (current_price - daily_low) / current_price * 100 AS distance_from_low,
                   deviation_from_avg,
                   daily_range_percent,
                   processing_time as raw_processing_time,
            
                   CASE
                       WHEN daily_change_percent > 10 AND volume_ratio > 3 THEN 'strong_uptrend'
                       WHEN daily_change_percent < -10 AND volume_ratio > 3 THEN 'strong_downtrend'
                       WHEN relative_change > top_10_percent_change AND volume_ratio > 2 THEN 'top_performer'
                       WHEN relative_change < -5 AND volume_ratio > 2 THEN 'underperforming'
                       WHEN volatility_ratio > 3 AND volume_ratio > 1 THEN 'high_volatility'
                       WHEN avg_trade_size_usd > 10000 THEN 'whale_activity'
                       ELSE 'neutral'
                       END                                           AS market_state,
            
            
                   CASE
                       WHEN daily_change_percent > 10 AND volume_ratio > 3 AND volatility_ratio < 2 THEN
                           'Strong uptrend with healthy volume - consider buying on dips'
                       WHEN daily_change_percent < -10 AND volume_ratio > 3 AND volatility_ratio > 2 THEN
                           'Strong downtrend - avoid catching the falling knife'
                       WHEN volatility_ratio > 3 AND volume_ratio > 1.5 THEN
                           'High volatility with volume - potential breakout opportunity'
                       WHEN relative_change > top_10_percent_change THEN
                           'Top performer with bullish volume - strong momentum'
                       ELSE 'No strong signal - monitor for changes'
                       END                                           AS action_suggestion,
                       '{now}' AS valid_from
            FROM enhanced_stats
            ORDER BY CASE
                         WHEN market_state IN ('strong_uptrend', 'top_performer') THEN 0
                         WHEN market_state = 'bullish_volume' THEN 1
                         ELSE 2
                         END,
                     abs(momentum_score) DESC,
                     volume_usd DESC
            LIMIT 500;
            """
        print("!!!!!!!", query)
        records = self.__clickhouse_hook.get_records(query)[0]

        df = pd.DataFrame(
            [list(row) for row in records],
            columns=columns,
        )
        sql = f"""
            UPDATE {self.global_config.postgresql.schema_name}.{self.global_config.postgresql.table_name}
            SET valid_to = '{now}'
            WHERE valid_to = '2999-12-31 00:00:00';
        """

        self.__postgres_hook.run(sql)

        copy_query = f"""
            COPY {self.global_config.postgresql.schema_name}.{self.global_config.postgresql.table_name}
            ({", ".join(columns)})
            FROM STDIN WITH CSV DELIMITER ',' NULL '\\N'
            """

        with tempfile.NamedTemporaryFile() as tmp:
            df.to_csv(
                tmp,
                index=False,
                index_label=False,
                sep=",",
                header=False,
                encoding="utf-8",
                na_rep="\\N",
            )
            self.__postgres_hook.copy_expert(copy_query, tmp.name)

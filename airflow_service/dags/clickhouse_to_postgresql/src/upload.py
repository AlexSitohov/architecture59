import os
import sys
from io import StringIO

import pandas as pd
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook

sys.path.insert(0, (os.path.join(os.path.dirname(__file__), "..")))

from src.source_to_target import (
    DagGlobalConfig,
)


class UploadProvider:
    def __init__(self, global_config: DagGlobalConfig):
        self.global_config = global_config
        self.ch_hook = ClickHouseHook.get_connection(
            global_config.clickhouse.connection_id
        ).get_hook()

    def execute(self):
        total_records = self.count_rows()
        self.upload(total_records)

    def count_rows(self) -> int:
        count_query = f"""
        SELECT COUNT(*) 
        FROM {self.global_config.clickhouse.table_name}
        """

        return self.ch_hook.get_first(count_query)[0]

    def upload(self, total_records: int):
        pg_conn = self.ch_hook.get_conn()
        cursor = pg_conn.cursor()

        offset = 0
        batch_count = 0

        while offset < total_records:
            ch_query = f"""
                SELECT {", ".join([row.source_name for row in self.global_config.rows])}
                FROM {self.global_config.clickhouse.table_name}
                LIMIT {self.global_config.clickhouse.batch_size} OFFSET {offset}
                """

            records = self.ch_hook.get_records(ch_query)
            if not records:
                break

            batch_count += 1

            df = pd.DataFrame(
                records,
                columns=[row.source_name for row in self.global_config.rows],
            )

            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, header=False, na_rep="\\N")
            csv_buffer.seek(0)

            copy_query = f"""
                COPY {self.global_config.postgresql.schema_name}.{self.global_config.postgresql.table_name}_stage
                ({", ".join([row.source_name for row in self.global_config.rows])})
                FROM STDIN WITH CSV DELIMITER ',' NULL '\\N'
                """
            cursor.copy_expert(copy_query, csv_buffer)

            offset += self.global_config.clickhouse.batch_size

import os
import sys

from airflow.providers.postgres.hooks.postgres import PostgresHook

sys.path.insert(0, (os.path.join(os.path.dirname(__file__), "..")))

from src.source_to_target import (
    DagGlobalConfig,
)


class PrepareProvider:
    def __init__(self, global_config: DagGlobalConfig):
        self.global_config = global_config

        self.pg_hook = PostgresHook.get_connection(
            global_config.postgresql.connection_id
        ).get_hook()

    def execute(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.global_config.postgresql.schema_name}.{self.global_config.postgresql.table_name}_stage(
        {"TEXT, ".join([row.source_name for row in self.global_config.rows])}
        )
        """
        self.pg_hook.run(sql)

import json
import os
from dataclasses import dataclass
from typing import List


@dataclass
class RowConfig:
    name: str
    source_name: str


@dataclass
class PostgresqlConfig:
    connection_id: str
    schema_name: str
    table_name: str


@dataclass
class ClickhouseConfig:
    connection_id: str
    table_name: str
    batch_size: int


@dataclass
class DagGlobalConfig:
    clickhouse: ClickhouseConfig
    postgresql: PostgresqlConfig
    rows: List[RowConfig]

    def __post_init__(self):
        if isinstance(self.postgresql, dict):
            self.target_s2t = PostgresqlConfig(**self.postgresql)
        if isinstance(self.clickhouse, dict):
            self.clickhouse = ClickhouseConfig(**self.clickhouse)
        if isinstance(self.rows, dict):
            self.rows = [
                RowConfig(name=key, source_name=value["source_name"])
                for key, value in self.rows.items()
            ]


class DagConfig:
    def __init__(self, dag_folder: str, dag_config: str = "config.json"):
        self.__payload = self.__read_json(os.path.join(dag_folder, dag_config))
        self.__global_config = DagGlobalConfig(**self.__payload)

    @staticmethod
    def __read_json(filename: str) -> dict:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Config file not found: {filename}")
        with open(filename, "r") as f:
            return json.load(f)

    @property
    def default_args(self) -> dict:
        return {
            "owner": "airflow",
            "depends_on_past": True,
            "retries": 1,
            "provide_context": True,
        }

    @property
    def global_config(self) -> DagGlobalConfig:
        return self.__global_config

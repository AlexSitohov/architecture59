import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServiceConfig:
    base_url: str
    prefix: str
    health_check: str
    public_endpoints: list[str] = None


@dataclass
class ServicesConfig:
    currency_service: ServiceConfig

    @classmethod
    def from_json_file(cls, file_path: str):
        config_path = Path(file_path)
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls(currency_service=ServiceConfig(**data["currency_service"]))

    def get_service_config(self, service: str) -> ServiceConfig:
        service = service.lower()
        if service == "currency_service":
            return self.currency_service

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CurrencyGET(BaseModel):
    id: UUID
    name: str
    code: str
    current_rate: float
    relevant_time: datetime

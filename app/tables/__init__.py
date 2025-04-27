from datetime import datetime

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Currency(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    current_rate: Mapped[float] = mapped_column(nullable=False)
    relevant_time: Mapped[datetime] = mapped_column(nullable=False)

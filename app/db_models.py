from typing import Annotated

from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

metadata = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]
crypto = Annotated[int, mapped_column(default=0, nullable=True)]


class UsersTable(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    coin_id: Mapped[int] = mapped_column(primary_key=True)
    min: Mapped[float] = mapped_column(default=None, nullable=True)
    max: Mapped[float] = mapped_column(default=None, nullable=True)



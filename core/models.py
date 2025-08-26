from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)

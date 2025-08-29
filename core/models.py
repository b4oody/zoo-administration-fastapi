from typing import List, Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)


class Animal(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    species: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(32))

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("animals.id"),
        nullable=True
    )
    parent: Mapped[Optional["Animal"]] = relationship(
        "Animal",
        remote_side="Animal.id",
        back_populates="children"
    )
    children: Mapped[List["Animal"]] = relationship(
        "Animal",
        back_populates="parent"
    )

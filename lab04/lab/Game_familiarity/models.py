from typing import List

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True


class Images(Base):
    __tablename__ = "images"
    VECTOR_LENGTH = 512

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_path: Mapped[str] = mapped_column(String(256))
    image_embedding: Mapped[List[float]] = mapped_column(Vector(VECTOR_LENGTH))


class Games(Base):
    __tablename__ = "games"
    __table_args__ = {"extend_existing": True}

    VECTOR_LENGTH = 512

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    windows: Mapped[bool] = mapped_column(Boolean)
    linux: Mapped[bool] = mapped_column(Boolean)
    mac: Mapped[bool] = mapped_column(Boolean)
    price: Mapped[float] = mapped_column(Float)
    game_description_embedding: Mapped[List[float]] = mapped_column(Vector(VECTOR_LENGTH))
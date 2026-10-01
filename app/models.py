from typing import Optional

from sqlalchemy import BigInteger, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Work(Base):
    __tablename__ = "work"

    work_id: Mapped[int] = mapped_column(
        "workid",
        BigInteger,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        "title",
        Text,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        "description",
        Text,
        nullable=True
    )

    original_year: Mapped[Optional[int]] = mapped_column(
        "originalyear",
        nullable=True
    )

    cover_image_url: Mapped[Optional[str]] = mapped_column(
        "coverimageurl",
        Text,
        nullable=True
    )

    original_language: Mapped[Optional[str]] = mapped_column(
        "originallanguage",
        Text,
        nullable=True
    )


class Author(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(
        "authorid",
        BigInteger,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        "name",
        Text,
        nullable=False
    )

    birth: Mapped[Optional[Date]] = mapped_column(
        "birth",
        Date,
        nullable=True
    )

    death: Mapped[Optional[Date]] = mapped_column(
        "death",
        Date,
        nullable=True
    )

    image_url: Mapped[Optional[str]] = mapped_column(
        "imageurl",
        Text,
        nullable=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        "description",
        Text,
        nullable=True
    )


class AuthorWork(Base):
    __tablename__ = "authorwork"

    work_id: Mapped[int] = mapped_column(
        "workid",
        BigInteger,
        ForeignKey("work.workid"),
        primary_key=True
    )

    author_id: Mapped[int] = mapped_column(
        "authorid",
        BigInteger,
        ForeignKey("author.authorid"),
        primary_key=True
    )


class Series(Base):
    __tablename__ = "series"

    series_id: Mapped[int] = mapped_column(
        "seriesid",
        BigInteger,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        "name",
        Text,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        "description",
        Text,
        nullable=True
    )


class SeriesWork(Base):
    __tablename__ = "serieswork"

    series_id: Mapped[int] = mapped_column(
        "seriesid",
        BigInteger,
        ForeignKey("series.seriesid"),
        primary_key=True
    )

    work_id: Mapped[int] = mapped_column(
        "workid",
        BigInteger,
        ForeignKey("work.workid"),
        primary_key=True
    )

    position: Mapped[Optional[float]] = mapped_column(
        "position",
        Numeric,
        nullable=True
    )
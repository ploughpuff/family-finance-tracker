import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Category(Base):
    """A category like Food, Entertainment, Mortgage, to assign to each transaction."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]]

    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="category",  # match Transaction.category
        cascade="all, delete-orphan",
    )

    learnt_category_mappings: Mapped[List["LearntCategoryMapping"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class LearntCategoryMapping(Base):
    """Learnt mapping from merchant to category, offered automatically during reconciliation."""

    __tablename__ = "learnt_category_mappings"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(
        back_populates="learnt_category_mappings"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    merchant: Mapped[str] = mapped_column(String, nullable=False)
    account_name: Mapped[str] = mapped_column(String, nullable=False)
    trans_hash: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")

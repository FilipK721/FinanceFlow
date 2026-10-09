"""SQLAlchemy ORM models for persisting application data."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all FinanceFlow database models."""
    pass

class ExpenseRow(Base):
    """Database row representing a single expense transaction."""

    __tablename__ = 'expenses'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    category: Mapped[str]
    date: Mapped[str]
    description: Mapped[str] = mapped_column(default='')


class CategoryLimitRow(Base):
    """Database row storing a spending limit for one category."""

    __tablename__ = 'category_limits'
    category: Mapped[str] = mapped_column(primary_key=True)
    limit: Mapped[float]


class SettingRow(Base):
    """Database row storing a single application setting by key."""

    __tablename__ = 'settings'
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
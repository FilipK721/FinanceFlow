from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class ExpenseRow(Base):
    __tablename__ = 'expenses'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    category: Mapped[str]
    date: Mapped[str]
    description: Mapped[str] = mapped_column(default='')

class CategoryLimitRow(Base):
    __tablename__ = 'category_limits'
    category: Mapped[str] = mapped_column(primary_key=True)
    limit: Mapped[float]

class SettingRow(Base):
    __tablename__ = 'settings'
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
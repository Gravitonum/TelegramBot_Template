from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    wheels: Mapped[list["Wheel"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Wheel(Base):
    __tablename__ = "wheels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    llm_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    user: Mapped[User] = relationship(back_populates="wheels")
    categories: Mapped[list["WheelCategory"]] = relationship(back_populates="wheel", cascade="all, delete-orphan")


class WheelCategory(Base):
    __tablename__ = "wheel_categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wheel_id: Mapped[int] = mapped_column(ForeignKey("wheels.id", ondelete="CASCADE"), index=True)
    category_name: Mapped[str] = mapped_column(String(255))
    value: Mapped[int] = mapped_column(Integer)
    order: Mapped[int] = mapped_column(Integer)
    wheel: Mapped[Wheel] = relationship(back_populates="categories")


class WheelComparison(Base):
    __tablename__ = "wheel_comparisons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wheel_id_1: Mapped[int] = mapped_column(ForeignKey("wheels.id", ondelete="CASCADE"))
    wheel_id_2: Mapped[int] = mapped_column(ForeignKey("wheels.id", ondelete="CASCADE"))
    comparison_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserActionLog(Base):
    __tablename__ = "user_action_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(255))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    wheel_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

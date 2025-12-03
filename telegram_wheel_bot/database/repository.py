from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, User, Wheel, WheelCategory, UserActionLog
from datetime import datetime
from typing import Iterable
from telegram_wheel_bot.config import DATABASE_URL


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> User:
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user:
            return user
        user = User(telegram_id=telegram_id, username=username, first_name=first_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_wheel_with_categories(user_id: int, name: str, scores_ordered: list[tuple[str, int]]) -> Wheel:
    with SessionLocal() as session:
        wheel = Wheel(user_id=user_id, name=name, created_at=datetime.utcnow())
        session.add(wheel)
        session.flush()
        for idx, (cat, val) in enumerate(scores_ordered):
            session.add(WheelCategory(wheel_id=wheel.id, category_name=cat, value=val, order=idx))
        session.commit()
        session.refresh(wheel)
        return wheel


def update_wheel_analysis(wheel_id: int, analysis: str) -> None:
    with SessionLocal() as session:
        wheel = session.get(Wheel, wheel_id)
        if not wheel:
            return
        wheel.llm_analysis = analysis
        session.commit()


def list_user_wheels(user_id: int) -> list[Wheel]:
    with SessionLocal() as session:
        return list(session.execute(select(Wheel).where(Wheel.user_id == user_id).order_by(desc(Wheel.created_at))).scalars())


def get_wheel_scores(wheel_id: int) -> dict[str, int]:
    with SessionLocal() as session:
        cats = list(session.execute(select(WheelCategory).where(WheelCategory.wheel_id == wheel_id).order_by(WheelCategory.order)).scalars())
        return {c.category_name: c.value for c in cats}


def get_latest_wheel(user_id: int) -> Wheel | None:
    with SessionLocal() as session:
        return session.execute(select(Wheel).where(Wheel.user_id == user_id).order_by(desc(Wheel.created_at))).scalars().first()


def get_wheel_by_id(wheel_id: int) -> Wheel | None:
    with SessionLocal() as session:
        return session.get(Wheel, wheel_id)


def log_user_action(user_id: int, action: str, details: str | None = None, wheel_id: int | None = None) -> None:
    with SessionLocal() as session:
        log = UserActionLog(user_id=user_id, action=action, details=details, wheel_id=wheel_id, created_at=datetime.utcnow())
        session.add(log)
        session.commit()


def delete_wheels_by_ids(user_id: int, wheel_ids: Iterable[int]) -> int:
    ids = list(wheel_ids)
    if not ids:
        return 0
    with SessionLocal() as session:
        subq = session.query(Wheel.id).filter(Wheel.user_id == user_id, Wheel.id.in_(ids))
        session.query(WheelCategory).filter(WheelCategory.wheel_id.in_(subq)).delete(synchronize_session=False)
        deleted = session.query(Wheel).filter(Wheel.user_id == user_id, Wheel.id.in_(ids)).delete(synchronize_session=False)
        session.commit()
        return deleted


def delete_all_user_wheels(user_id: int) -> int:
    with SessionLocal() as session:
        subq = session.query(Wheel.id).filter(Wheel.user_id == user_id)
        session.query(WheelCategory).filter(WheelCategory.wheel_id.in_(subq)).delete(synchronize_session=False)
        deleted = session.query(Wheel).filter(Wheel.user_id == user_id).delete(synchronize_session=False)
        session.commit()
        return deleted

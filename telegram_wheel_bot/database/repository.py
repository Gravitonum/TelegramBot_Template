from sqlalchemy import create_engine, select, desc, func
from sqlalchemy.orm import sessionmaker
from .models import Base, User, Wheel, WheelCategory, UserActionLog
from datetime import datetime, timedelta
from typing import Iterable, Optional
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


# Admin panel functions
def get_all_users_with_last_action() -> list[dict]:
    """Get all users with their last action date from wheel history."""
    with SessionLocal() as session:
        users = session.execute(select(User)).scalars().all()
        result = []
        for user in users:
            # Get last wheel creation date
            last_wheel = session.execute(
                select(Wheel).where(Wheel.user_id == user.id).order_by(desc(Wheel.created_at))
            ).scalars().first()
            
            # Get last action log date
            last_action = session.execute(
                select(UserActionLog).where(UserActionLog.user_id == user.id).order_by(desc(UserActionLog.created_at))
            ).scalars().first()
            
            # Use the most recent date
            last_action_date = None
            if last_wheel and last_action:
                last_action_date = max(last_wheel.created_at, last_action.created_at)
            elif last_wheel:
                last_action_date = last_wheel.created_at
            elif last_action:
                last_action_date = last_action.created_at
            
            result.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_action_date': last_action_date.isoformat() if last_action_date else None
            })
        return result


def get_user_wheels(user_id: int) -> list[dict]:
    """Get all wheels for a user, sorted by creation date (newest first)."""
    with SessionLocal() as session:
        wheels = session.execute(
            select(Wheel).where(Wheel.user_id == user_id).order_by(desc(Wheel.created_at))
        ).scalars().all()
        
        result = []
        for wheel in wheels:
            result.append({
                'id': wheel.id,
                'name': wheel.name,
                'created_at': wheel.created_at.isoformat() if wheel.created_at else None,
                'has_analysis': bool(wheel.llm_analysis)
            })
        return result


def get_statistics_30_days() -> dict:
    """Get statistics for the last 30 days."""
    with SessionLocal() as session:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        # Users who joined in last 30 days
        new_users = session.execute(
            select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
        ).scalar() or 0
        
        # Wheels created in last 30 days
        wheels_created = session.execute(
            select(func.count(Wheel.id)).where(Wheel.created_at >= thirty_days_ago)
        ).scalar() or 0
        
        # Users who were active in previous month (30-60 days ago) but not in last 30 days
        users_active_previous_month = session.execute(
            select(func.count(func.distinct(Wheel.user_id))).where(
                Wheel.created_at >= sixty_days_ago,
                Wheel.created_at < thirty_days_ago
            )
        ).scalar() or 0
        
        users_active_last_month = session.execute(
            select(func.count(func.distinct(Wheel.user_id))).where(
                Wheel.created_at >= thirty_days_ago
            )
        ).scalar() or 0
        
        inactive_users = max(0, users_active_previous_month - users_active_last_month)
        
        return {
            'new_users': new_users,
            'wheels_created': wheels_created,
            'inactive_users': inactive_users,
            'period_start': thirty_days_ago.isoformat(),
            'period_end': datetime.utcnow().isoformat()
        }


def get_new_users_30_days() -> list[dict]:
    """Get list of users who joined in the last 30 days."""
    with SessionLocal() as session:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        users = session.execute(
            select(User).where(User.created_at >= thirty_days_ago).order_by(desc(User.created_at))
        ).scalars().all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return result


def get_users_with_wheels_30_days() -> list[dict]:
    """Get list of users who created wheels in the last 30 days."""
    with SessionLocal() as session:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        # Получаем уникальных пользователей, которые создали колеса за последние 30 дней
        user_ids = session.execute(
            select(func.distinct(Wheel.user_id)).where(Wheel.created_at >= thirty_days_ago)
        ).scalars().all()
        
        result = []
        for user_id in user_ids:
            user = session.get(User, user_id)
            if user:
                # Получаем количество колес пользователя за последние 30 дней
                wheels_count = session.execute(
                    select(func.count(Wheel.id)).where(
                        Wheel.user_id == user_id,
                        Wheel.created_at >= thirty_days_ago
                    )
                ).scalar() or 0
                
                # Получаем дату последнего колеса
                last_wheel = session.execute(
                    select(Wheel).where(
                        Wheel.user_id == user_id,
                        Wheel.created_at >= thirty_days_ago
                    ).order_by(desc(Wheel.created_at))
                ).scalars().first()
                
                result.append({
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'wheels_count': wheels_count,
                    'last_wheel_date': last_wheel.created_at.isoformat() if last_wheel else None
                })
        
        # Сортируем по дате последнего колеса (новые сверху)
        result.sort(key=lambda x: x['last_wheel_date'] or '', reverse=True)
        return result


def get_inactive_users() -> list[dict]:
    """Get list of users who were active in previous month but not in last 30 days."""
    with SessionLocal() as session:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        # Пользователи, активные в предыдущем месяце (30-60 дней назад)
        users_active_previous = session.execute(
            select(func.distinct(Wheel.user_id)).where(
                Wheel.created_at >= sixty_days_ago,
                Wheel.created_at < thirty_days_ago
            )
        ).scalars().all()
        
        # Пользователи, активные в последние 30 дней
        users_active_recent = session.execute(
            select(func.distinct(Wheel.user_id)).where(
                Wheel.created_at >= thirty_days_ago
            )
        ).scalars().all()
        
        # Находим неактивных (были активны раньше, но не сейчас)
        inactive_user_ids = set(users_active_previous) - set(users_active_recent)
        
        result = []
        for user_id in inactive_user_ids:
            user = session.get(User, user_id)
            if user:
                # Получаем дату последнего колеса
                last_wheel = session.execute(
                    select(Wheel).where(Wheel.user_id == user_id).order_by(desc(Wheel.created_at))
                ).scalars().first()
                
                result.append({
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_wheel_date': last_wheel.created_at.isoformat() if last_wheel else None
                })
        
        # Сортируем по дате последнего колеса (старые сверху)
        result.sort(key=lambda x: x['last_wheel_date'] or '', reverse=False)
        return result

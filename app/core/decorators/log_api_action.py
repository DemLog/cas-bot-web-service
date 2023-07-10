from sqlalchemy.orm import Session

from app.database.models.admin import ActivityLog


def log_api_action(db: Session, user_from, user_to, action: str):
    log_entry = ActivityLog(
        user_from=user_from,
        user_to=user_to,
        action=action,
    )
    db.add(log_entry)
    db.commit()

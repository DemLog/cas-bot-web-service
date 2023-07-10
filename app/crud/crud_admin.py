from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models.admin import ActivityLog
from app.database.models.user import User


class CRUDAdmin:
    def get_activity_user(self, user_id, db: Session) -> [Any]:
        try:
            data = db.query(ActivityLog).filter(ActivityLog.user_to == user_id).all()
            return data
        except SQLAlchemyError as e:
            print(e)
            return None

    def get_all_activity(self, db: Session) -> [Any]:
        try:
            data = db.query(ActivityLog).all()
            return data
        except SQLAlchemyError as e:
            return None

    def get_all_new_users(self, db: Session) -> [Any]:
        try:
            query = db.query(func.count(User.id).label("user_count"),
                             func.DATE_TRUNC('day', User.created_profile).label("registration_date")) \
                .group_by(func.DATE_TRUNC('day', User.created_profile))

            return query.all()
        except SQLAlchemyError as e:
            return None


crud_admin = CRUDAdmin()

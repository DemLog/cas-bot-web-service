from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.schemas import UserUpdate, UserCreate
from app.database.models.user import User


class CRUDUsers:
    def create_user(self, user: UserCreate, db: Session) -> Any:
        try:
            db_user = User(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                is_accept_terms=user.is_accept_terms
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def update_user(self, user_id: int, user: UserUpdate, db: Session) -> Any:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if user.first_name is not None:
                db_user.first_name = user.first_name
            if user.last_name is not None:
                db_user.last_name = user.last_name
            if user.username is not None:
                db_user.username = user.username
            if user.role is not None:
                db_user.role = user.role
            if user.tokens is not None:
                db_user.tokens = user.tokens
            if user.is_active is not None:
                db_user.is_active = user.is_active
            if user.is_accept_terms is not None:
                db_user.is_accept_terms = user.is_accept_terms

            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def delete_user(self, user_id: int, db: Session) -> Any:
        try:
            db.query(User).filter(User.id == user_id).delete()
            db.commit()
            return True
        except SQLAlchemyError as e:
            return None

    def user_status_update(self, user_id, active: bool, db: Session) -> Any:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            db_user.is_active = active
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def user_add_tokens(self, user_id, tokens: int, db: Session) -> Any:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            db_user.tokens += tokens
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def user_change_role(self, user_id, role: str, db: Session) -> Any:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            db_user.role = role
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def user_accept_terms(self, user_id: int, db: Session) -> Any:
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            db_user.is_accept_terms = True
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def get_user_id(self, user_id: int, db: Session) -> Any:
        try:
            data = db.query(User).filter(User.id == user_id).first()
            return data
        except SQLAlchemyError as e:
            return None

    def get_all_user(self, db: Session) -> [Any]:
        try:
            query = db.query(User).order_by(User.created_profile).all()
            return query
        except SQLAlchemyError as e:
            return None


crud_users = CRUDUsers()

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

    def update_user(self,
                    db_user: User,
                    *,
                    update: UserUpdate,
                    db: Session):
        try:
            if update.first_name is not None:
                db_user.first_name = update.first_name
            if update.last_name is not None:
                db_user.last_name = update.last_name
            if update.username is not None:
                db_user.username = update.username
            if update.role is not None:
                db_user.role = update.role
            if update.tokens is not None:
                db_user.tokens = update.tokens
            if update.is_active is not None:
                db_user.is_active = update.is_active
            if update.is_accept_terms is not None:
                db_user.is_accept_terms = update.is_accept_terms

            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def update_user_by_id(self, user_id: int, user: UserUpdate, db: Session) -> Any:
        db_user: User = db.query(User).filter(User.id == user_id).first()
        return self.update_user(db_user,
                                update=user,
                                db=db)

    def delete_user(self,
                    db_user: User,
                    *,
                    db: Session):
        try:
            db.delete(db_user)
            db.commit()
            return True
        except SQLAlchemyError as e:
            return None

    def delete_user_by_id(self, user_id: int, db: Session) -> Any:
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

    def user_accept_terms(self,
                          db_user: User,
                          *,
                          db: Session):
        try:
            db_user.is_accept_terms = True
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            return None

    def user_accept_terms_by_id(self, user_id: int, db: Session) -> Any:
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

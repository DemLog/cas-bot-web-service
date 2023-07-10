from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.schemas import HistoryCreate
from app.database.models.history import History


class CRUDHistory:
    def create_history(self, user_id: int, history: HistoryCreate, db: Session) -> Any:
        try:
            db_history = History(
                title=history.title,
                url=history.url,
                user_id=user_id
            )
            db.add(db_history)
            db.commit()
            db.refresh(db_history)
            return db_history

        except SQLAlchemyError as e:
            return None

    def get_histories(self, user_id: int, db: Session) -> [Any]:
        try:
            db_history = db.query(History).filter(History.user_id == user_id).order_by(History.date).all()
            return db_history

        except SQLAlchemyError as e:
            print(e)
            return None

    def delete_all(self, user_id: int, db: Session) -> Any:
        try:
            db_history = db.query(History).filter(History.user_id == user_id).delete()
            db.commit()
            return True

        except SQLAlchemyError as e:
            print(e)
            return None


crud_history = CRUDHistory()

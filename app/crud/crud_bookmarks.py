from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.schemas import ProductSave
from app.database.models.bookmarks import Bookmark


class CRUDBookmarks:
    def add_bookmark(self, user_id: int, product: ProductSave, db: Session) -> Any:
        try:
            db_bookmark = Bookmark(
                product_id=product.product_id,
                title=product.title,
                url=product.url,
                url_photo=product.photo_url,
                user_id=user_id
            )
            db.add(db_bookmark)
            db.commit()
            db.refresh(db_bookmark)
            return db_bookmark

        except SQLAlchemyError as e:
            return None

    def get_bookmark(self, bookmark_id: int, db: Session) -> Any:
        try:
            db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
            return db_bookmark
        except SQLAlchemyError as e:
            return None

    def get_all_bookmarks(self, user_id: int, db: Session) -> Any:
        try:
            db_bookmark = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
            return db_bookmark
        except SQLAlchemyError as e:
            return None

    def delete_bookmark(self, bookmark_id: int, db: Session) -> Any:
        try:
            db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).delete()
            db.commit()
            return True

        except SQLAlchemyError as e:
            return None


crud_bookmarks = CRUDBookmarks()

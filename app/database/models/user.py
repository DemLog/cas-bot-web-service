from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base
from app.database.models.admin import ActivityLog


class UserRoleEnum(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

    @staticmethod
    def get_access_level(level):
        match level:
            case UserRoleEnum.MANAGER:
                return 1
            case UserRoleEnum.ADMIN:
                return 2
        return 0


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRoleEnum.USER)
    tokens = Column(Integer, nullable=False, default=10)

    is_active = Column(Boolean, nullable=False, default=True)
    is_accept_terms = Column(Boolean, nullable=False, default=False)

    created_profile = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    histories = relationship("History", back_populates="user")

    bookmarks = relationship("Bookmark", back_populates="user")

    activity_logs_from = relationship("ActivityLog", back_populates="user_from_id",
                                      foreign_keys="ActivityLog.user_from")
    activity_logs_to = relationship("ActivityLog", back_populates="user_to_id", foreign_keys="ActivityLog.user_to")

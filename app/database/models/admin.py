from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_from = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    user_from_id = relationship("User", back_populates="activity_logs_from", foreign_keys=[user_from])
    user_to_id = relationship("User", back_populates="activity_logs_to", foreign_keys=[user_to])

from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, Integer, ForeignKey, Enum as SaEnum, func, TIMESTAMP, Boolean, Text, String, Uuid, text

from app.database import Base


class AccessType(str, Enum):
    PUBLIC = "public"
    BOT_USERS = "bot_users"
    PRIVATE = "private"


class AnalysisReport(Base):
    __tablename__ = "analysis_report"

    id = Column(Uuid, primary_key=True, index=True, default=uuid4, server_default=text("gen_random_uuid()"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_type = Column(SaEnum(AccessType), nullable=False, default=AccessType.BOT_USERS)
    formation_date = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_exist = Column(Boolean, nullable=False, default=True)

    product_name_id = Column(String, nullable=False)
    product_image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)

    analysis_interests_reviewers_data_json = Column(Text, nullable=True)
    analysis_interests_commentators_data_json = Column(Text, nullable=True)

    analysis_sentiment_reviewers_region_data_json = Column(Text, nullable=True)
    analysis_sentiment_commentators_region_data_json = Column(Text, nullable=True)

    analysis_sentiment_reviewers_category_data_json = Column(Text, nullable=True)
    analysis_sentiment_commentators_category_data_json = Column(Text, nullable=True)

    analysis_similarity_reviewers_category_data_json = Column(Text, nullable=True)
    analysis_similarity_commentators_category_data_json = Column(Text, nullable=True)

    analysis_similarity_reviewers_reputation_data_json = Column(Text, nullable=True)
    analysis_similarity_commentators_reputation_data_json = Column(Text, nullable=True)

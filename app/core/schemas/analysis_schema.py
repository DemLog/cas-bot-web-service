from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from app.core.schemas import UserInfo
from app.database.models.analysis_report import AccessType


class ProductSearch(BaseModel):
    text: str
    is_category: bool


class ProductSave(BaseModel):
    product_id: str
    title: str
    url: str
    photo_url: str


class ProductInfo(BaseModel):
    product_name_id: str
    product_image_url: HttpUrl
    title: str


class AnalysisReport(BaseModel):
    id: UUID
    owner: UserInfo
    access_type: AccessType
    product: ProductInfo
    formation_date: datetime

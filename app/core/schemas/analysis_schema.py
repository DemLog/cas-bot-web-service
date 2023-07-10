from typing import List

from pydantic import BaseModel


class ProductSearch(BaseModel):
    text: str
    is_category: bool


class ProductInfo(BaseModel):
    id: str
    title: str
    categories: List[str]
    url: str
    photo_url: str
    disabled: bool


class ProductSave(BaseModel):
    product_id: str
    title: str
    url: str
    photo_url: str

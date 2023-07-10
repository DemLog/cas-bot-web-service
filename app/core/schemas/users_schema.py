from typing import Optional

from pydantic import BaseModel

from app.database.models.user import UserRoleEnum


class UserBase(BaseModel):
    id: int


class UserCreate(UserBase):
    first_name: str
    last_name: str
    username: str
    is_accept_terms: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str | None] = None
    last_name: Optional[str | None] = None
    username: Optional[str | None] = None
    role: Optional[str | None] = UserRoleEnum.USER
    tokens: Optional[int | None] = None
    is_active: Optional[bool | None] = True
    is_accept_terms: Optional[bool | None] = True

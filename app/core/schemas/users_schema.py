from typing import Optional

from pydantic import BaseModel

from app.database.models.user import UserRoleEnum


class UserBase(BaseModel):
    id: int


class UserCreate(UserBase):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    is_accept_terms: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    role: Optional[str] = UserRoleEnum.USER
    tokens: Optional[int] = None
    is_active: Optional[bool] = True
    is_accept_terms: Optional[bool] = True


class UserInfo(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = UserRoleEnum.USER


class UserData(BaseModel):
    id: Optional[int]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    role: Optional[str] = UserRoleEnum.USER
    tokens: Optional[int] = None
    is_active: Optional[bool] = True
    is_accept_terms: Optional[bool] = False


class UserAuth(BaseModel):
    user_data: UserData
    token: Optional[str] = None

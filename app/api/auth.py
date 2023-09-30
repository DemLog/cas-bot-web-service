import hmac
from asyncio import iscoroutinefunction
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256
from typing import Optional

from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette import status

from app.api.exceptions import CasWebError
from app.core.config import ProjectSettings
from app.core.deps import get_db, create_access_token, get_key
from app.core.schemas import UserCreate
from app.core.schemas.security import TelegramLoginData
from app.crud import crud_users
from app.database.models.user import UserRoleEnum, User

router = APIRouter()


@router.get("/login")
def signin(return_to: str, response: Response, data: TelegramLoginData = Depends(), db: Session = Depends(get_db)):
    """Route for obtaining a JWT token"""
    is_valid: bool = validate(data, ProjectSettings.BOT_TOKEN)
    if is_valid:
        user = crud_users.get_user_by_id(data.id, db)
        if user is not None:
            pass
        else:
            user = crud_users.create_user(UserCreate(id=data.id,
                                                     first_name=data.first_name,
                                                     last_name=data.last_name,
                                                     username=data.username), db)
        response.set_cookie(key="api-token", value=create_access_token({"user_id": user.id}))
        return RedirectResponse(url=return_to, status_code=303)
    else:
        raise CasWebError(message="TelegramLoginData no valid", http_status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/signup")
def signup(return_to: str,
           response: Response,
           user: UserCreate = Depends(),
           api_key: str = Depends(get_key),
           db: Session = Depends(get_db)):
    """
    Route for user registration in the system via telegram bot.
    The user will be automatically added to the system via the Web when logging in via telegram.
    """
    user = crud_users.get_user_by_id(user.id, db)
    if user is not None:
        raise CasWebError(message="User already exists", http_status_code=status.HTTP_409_CONFLICT)
    else:
        user = crud_users.create_user(user, db)
        response.set_cookie(key="api-token", value=create_access_token({"user_id": user.id}))
        return RedirectResponse(url=return_to, status_code=303)


def validate(data: TelegramLoginData, bot_token: str) -> bool:
    telegram_data = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude_defaults=True
    )
    data_check_string = "\n".join(sorted([
        f"{key}={value or 'null'}"
        for key, value in telegram_data.items()
        if key != "hash" and value is not None
    ]))
    secret_key = sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode(),
        digestmod=sha256
    ).hexdigest()

    return data.hash == calculated_hash and \
        datetime.fromtimestamp(data.auth_date) + timedelta(minutes=ProjectSettings.TELEGRAM_DATA_EXPIRE_MINUTES) >= datetime.now()


def manage_role_access(access_level: UserRoleEnum):
    def decorator(f):
        @wraps(f)
        async def wrapped_f(*args, **kwargs):
            user: Optional[User] = kwargs.get("user")
            if user is not None:
                if UserRoleEnum.get_access_level(access_level) > UserRoleEnum.get_access_level(user.role):
                    raise CasWebError(message="The user does not have sufficient access rights to perform the action",
                                      http_status_code=status.HTTP_403_FORBIDDEN)
                else:
                    if iscoroutinefunction(f):
                        result = await f(*args, **kwargs)
                    else:
                        result = f(*args, **kwargs)
                    return result
            else:
                raise CasWebError(message="Failed to define user access level",
                                  http_status_code=status.HTTP_403_FORBIDDEN)

        return wrapped_f

    return decorator


def manage_tokens_access(cost_tokens: int):
    """
    Performs token charging from regular users
    (managers and administrators are not subject to the restriction)

    :param cost_tokens:
    :return:
    """
    def decorator(f):
        @wraps(f)
        async def wrapped_f(*args, **kwargs):
            user: Optional[User] = kwargs.get("user")
            error_message: str = "Not enough tokens to perform the operation"
            if user is not None:
                if user.tokens < cost_tokens and user.role == UserRoleEnum.USER:
                    raise CasWebError(message=error_message,
                                      http_status_code=status.HTTP_403_FORBIDDEN)
                else:
                    if iscoroutinefunction(f):
                        result = await f(*args, **kwargs)
                    else:
                        result = f(*args, **kwargs)
                    crud_users.user_subtract_tokens(user, cost_tokens, kwargs["db"])
                    return result
            else:
                raise CasWebError(message=error_message,
                                  http_status_code=status.HTTP_403_FORBIDDEN)

        return wrapped_f

    return decorator

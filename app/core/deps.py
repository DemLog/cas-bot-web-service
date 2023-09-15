from datetime import datetime, timedelta

from fastapi import Security, Depends
from fastapi.security import APIKeyHeader, APIKeyCookie
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status

from app.api.exceptions import CasWebError
from app.core.config import ProjectSettings
from app.crud import crud_users
from app.database import SessionLocal
from app.database.models.user import User


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="Cas Web Service API Key", auto_error=False)
telegram_user_id = APIKeyHeader(name="Telegram-User-Id", scheme_name="Active telegram user ID",  auto_error=False)
api_token = APIKeyCookie(name="api-token", scheme_name="Cas Web JWT Token", auto_error=False)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ProjectSettings.AUTH_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ProjectSettings.AUTH_SECRET, algorithm=ProjectSettings.AUTH_ALGORITHM)

    return encoded_jwt


def get_user(key: str = Security(api_key_header),
             user_id: str = Security(telegram_user_id),
             token: str = Security(api_token),
             db: Session = Depends(get_db)):
    """Dependency for access verification by api key or telegram data"""
    if key == ProjectSettings.WEB_SERVICE_API_KEY:
        user: User = crud_users.get_user_id(user_id, db)
        if user is not None:
            return user
        else:
            raise CasWebError(message="Telegram user not yet registered", http_status_code=status.HTTP_401_UNAUTHORIZED)
    elif token is not None:
        payload: dict = jwt.decode(token, ProjectSettings.AUTH_SECRET, algorithms=[ProjectSettings.AUTH_ALGORITHM])
        exp = payload.get("exp")
        if exp is not None:
            exp = datetime.fromtimestamp(float(exp))
            now = datetime.utcnow()
            if exp > now:
                raise CasWebError(message="The access token was expired", http_status_code=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = payload.get("user_id")
                if user_id is not None:
                    user: User = crud_users.get_user_id(user_id, db)
                    if user is not None:
                        return user
                    else:
                        raise CasWebError(message="Telegram user not yet registered", http_status_code=status.HTTP_401_UNAUTHORIZED)
                else:
                    raise CasWebError(message="User incorrect", http_status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            raise CasWebError(message="The access token is not valued", http_status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        raise CasWebError(message="Invalid or missing API Key", http_status_code=status.HTTP_401_UNAUTHORIZED)


def get_key(key: str = Security(api_key_header)):
    """Dependency for checking access by api key only"""
    if key == ProjectSettings.WEB_SERVICE_API_KEY:
        return key
    else:
        raise CasWebError(message="Invalid or missing API Key", http_status_code=status.HTTP_401_UNAUTHORIZED)

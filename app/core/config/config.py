import json
import os
from pathlib import Path
from typing import Dict


def get_config() -> Dict:
    with open(str(Path(
            __file__).parent.parent) + os.sep + "config" + os.sep + "conf.json",
              'r') as fp:
        return json.load(fp)


class DBSettings:
    __DATA = get_config()['DATABASE_CONF']
    SQLALCHEMY_DATABASE_URL = __DATA["DATABASE"] + '://' + \
                              __DATA["POSTGRES_USER"] + ':' + __DATA[
                                  "POSTGRES_PASSWORD"] + '@' + __DATA[
                                  "POSTGRES_SERVER"] + ':' + \
                              __DATA["POSTGRES_PORT"] + '/' + __DATA[
                                  "POSTGRES_DB"]


class ProjectSettings:
    """ Project Configuration"""
    __DATA = get_config()['PROJECT_CONF']
    PROJECT_NAME = __DATA["PROJECT_NAME"]
    PROJECT_DESCRIPTION = __DATA["PROJECT_DESCRIPTION"]
    API_VERSION = __DATA["API_VERSION"]
    API_VERSION_PATH = __DATA["API_VERSION_PATH"]
    WEB_SERVICE_API_KEY = __DATA["WEB_SERVICE_API_KEY"]
    SERVER_NAME = __DATA["SERVER_NAME"]
    SERVER_HOST = __DATA["SERVER_HOST"]
    BACKEND_CORS_ORIGINS = __DATA["BACKEND_CORS_ORIGINS"]
    ACCESS_TOKEN_EXPIRE_MINUTES = __DATA["ACCESS_TOKEN_EXPIRE_MINUTES"]
    SESSION_TOKEN_EXPIRE_SECONDS = __DATA["SESSION_TOKEN_EXPIRE_SECONDS"]
    AUTH_SECRET = __DATA["AUTH_SECRET"]
    AUTH_ALGORITHM = __DATA["AUTH_ALGORITHM"]
    AUTH_EXPIRE_MINUTES = int(__DATA["AUTH_EXPIRE_MINUTES"])
    TELEGRAM_DATA_EXPIRE_MINUTES = int(__DATA["TELEGRAM_DATA_EXPIRE_MINUTES"])
    BOT_TOKEN = __DATA["BOT_TOKEN"]


class CasApiSettings:
    __DATA = get_config()["CAS_API_CONF"]
    SERVER_HOST = __DATA["SERVER_HOST"]
    VERSION_PATH = __DATA["VERSION_PATH"]
    CAS_API_KEY = __DATA["CAS_API_KEY"]

    @classmethod
    def get_cas_api_url(cls) -> str:
        return f"{cls.SERVER_HOST}{cls.VERSION_PATH}"

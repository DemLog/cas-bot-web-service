"""
Alternative implementation of APIKeyHeader, APIKeyCookie call from fastapi.security.
Necessary to work not only with Request, but also with WebSocket
"""

from typing import Optional

from fastapi import Request, WebSocket
from fastapi.security import (
    APIKeyHeader as FastapiAPIKeyHeader,
    APIKeyCookie as FastapiAPIKeyCookie
)
from starlette.exceptions import HTTPException, WebSocketException
from starlette.status import HTTP_403_FORBIDDEN


class APIKeyHeader(FastapiAPIKeyHeader):
    async def __call__(self, request: Request = None, websocket: WebSocket = None) -> Optional[str]:
        # This implementation is necessary because we need to specify the type explicitly
        api_key = None
        if websocket is not None:
            api_key = websocket.headers.get(self.model.name)
            connection = websocket
        elif request is not None:
            api_key = request.headers.get(self.model.name)
            connection = request

        if not api_key:
            if self.auto_error:
                if isinstance(connection, WebSocket):
                    raise WebSocketException(code=HTTP_403_FORBIDDEN, reason="Not authenticated")
                else:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                    )
            else:
                return None
        return api_key


class APIKeyCookie(FastapiAPIKeyCookie):
    async def __call__(self, request: Request = None, websocket: WebSocket = None) -> Optional[str]:
        # This implementation is necessary because we need to specify the type explicitly
        api_key = None
        if websocket is not None:
            api_key = websocket.cookies.get(self.model.name)
            connection = websocket
        elif request is not None:
            api_key = request.cookies.get(self.model.name)
            connection = request

        if not api_key:
            if self.auto_error:
                if isinstance(connection, WebSocket):
                    raise WebSocketException(code=HTTP_403_FORBIDDEN, reason="Not authenticated")
                else:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                    )
            else:
                return None
        return api_key

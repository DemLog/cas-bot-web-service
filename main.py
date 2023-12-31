from http import HTTPStatus

import uvicorn
import yaml
from fastapi import FastAPI, Request, WebSocket
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app import database
from app.api import api_router
from app.api.exceptions import CasWebError
from app.core.config import ProjectSettings
from app.database import dbconf

app = FastAPI(
    title=ProjectSettings.PROJECT_NAME,
    description=ProjectSettings.PROJECT_DESCRIPTION,
    version="1.0.0",
    openapi_url=f"{ProjectSettings.API_VERSION_PATH}",
    docs_url=f"{ProjectSettings.API_VERSION_PATH}/docs",
    redoc_url=f"{ProjectSettings.API_VERSION_PATH}/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ProjectSettings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=ProjectSettings.API_VERSION_PATH)


@app.get(f"/swagger.yaml", include_in_schema=False)
async def get_swagger():
    openapi_schema = get_openapi(title=f"{ProjectSettings.PROJECT_NAME} API", version="0.1.0", routes=app.routes)
    with open("./docs/swagger.yaml", "w") as file:
        yaml.dump(openapi_schema, file)
    return openapi_schema


@app.on_event("startup")
def startup_event():
    database.Base.metadata.create_all(bind=dbconf.engine)


@app.get(ProjectSettings.API_VERSION_PATH, include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(status_code=200,
                        content={
                            "message": "Welcome to Sample Server"})


@app.exception_handler(CasWebError)
async def cas_exception_handler(connection: Request | WebSocket, exc: CasWebError):
    if isinstance(connection, WebSocket):
        await connection.close(reason=exc.message)
    else:
        return JSONResponse(
            status_code=int(exc.http_status_code),
            content={"message": exc.message}
        )


@app.exception_handler(Exception)
async def unhandled_exception_handler(connection: Request | WebSocket, ex: Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    if isinstance(connection, WebSocket):
        await connection.close(reason=status.name)
    else:
        return JSONResponse(
            status_code=status.value, content={"message": status.name}
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)

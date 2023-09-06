import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app import database
from app.api import api_router
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


@app.on_event("startup")
def startup_event():
    database.Base.metadata.create_all(bind=dbconf.engine)


@app.get(ProjectSettings.API_VERSION_PATH, include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(status_code=200,
                        content={
                            "message": "Welcome to Sample Server"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
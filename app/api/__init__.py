from fastapi import APIRouter
from . import auth
from . import users
from . import history
from . import analysis
from . import admin
from . import bookmarks
from . import analysis_report

api_router = APIRouter()

api_router.include_router(auth.router, prefix="", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(history.router, prefix="/history", tags=["Histories"])
api_router.include_router(analysis.router, prefix="/analysis/ws", tags=["Analysis"])
api_router.include_router(analysis_report.router, prefix="/analysis_report", tags=["Report"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admins"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])

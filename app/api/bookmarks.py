from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.api.auth import manage_role_access
from app.core import deps
from app.core.deps import get_user
from app.crud import crud_bookmarks
from app.database.models.user import User, UserRoleEnum

router = APIRouter()


@router.get("/")
@manage_role_access(UserRoleEnum.USER)
def get_bookmark(bookmark_id: int,
                 db: Session = Depends(deps.get_db),
                 user: User = Depends(get_user)) -> JSONResponse:
    data = crud_bookmarks.get_bookmark(bookmark_id, db)
    if data is not None:
        return JSONResponse(status_code=404,
                            content={"message": "Элемент по данному id отсуствует"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.get("/all")
@manage_role_access(UserRoleEnum.USER)
def ger_all_bookmarks(user_id: int,
                      db: Session = Depends(deps.get_db),
                      user: User = Depends(get_user)) -> JSONResponse:
    data = crud_bookmarks.get_all_bookmarks(user_id, db)
    if data is not None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


def delete_bookmark(bookmark_id: int,
                    db: Session = Depends(deps.get_db),
                    user: User = Depends(get_user)) -> JSONResponse:
    data = crud_bookmarks.delete_bookmark(bookmark_id, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})

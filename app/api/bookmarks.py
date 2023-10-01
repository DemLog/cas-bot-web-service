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
    if data is None:
        return JSONResponse(status_code=404,
                            content={"message": "Элемент по данному id отсуствует"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.delete("/")
@manage_role_access(UserRoleEnum.USER)
def delete_bookmark(bookmark_id: int,
                    db: Session = Depends(deps.get_db),
                    user: User = Depends(get_user)) -> JSONResponse:
    bookmark = crud_bookmarks.get_bookmark(bookmark_id, db)
    if bookmark is None:
        return JSONResponse(status_code=404,
                            content={"message": "Элемент по данному id отсуствует"})
    if bookmark.user_id != user.id:
        return JSONResponse(status_code=403,
                            content={"message": "Вы не можете удалить чужую закладку!"})
    data = crud_bookmarks.delete_bookmark(bookmark_id, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})


@router.get("/all")
@manage_role_access(UserRoleEnum.USER)
def ger_all_bookmarks(db: Session = Depends(deps.get_db),
                      user: User = Depends(get_user)) -> JSONResponse:
    data = crud_bookmarks.get_all_bookmarks(user.id, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)

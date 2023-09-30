from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.api.auth import manage_role_access
from app.core import deps
from app.core.deps import get_user
from app.crud import crud_admin, crud_users
from app.database.models.user import User, UserRoleEnum

router = APIRouter()


@router.get("/stats")
@manage_role_access(UserRoleEnum.MANAGER)
def get_new_users_stats(db: Session = Depends(deps.get_db),
                        user: User = Depends(get_user)) -> JSONResponse:
    data = crud_admin.get_all_new_users(db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Активностей нет"})
    result = [{"user_count": row.user_count, "registration_date": row.registration_date} for row in data]
    json_compatible_item_data = jsonable_encoder(result)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.get("/activity/all")
@manage_role_access(UserRoleEnum.MANAGER)
def get_all_users_activity(db: Session = Depends(deps.get_db),
                           user: User = Depends(get_user)) -> JSONResponse:
    data = crud_admin.get_all_activity(db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Активностей нет"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.get("/activity")
@manage_role_access(UserRoleEnum.MANAGER)
def get_user_activity(user_id: int,
                      db: Session = Depends(deps.get_db),
                      user: User = Depends(get_user)) -> JSONResponse:
    if user_id is None:
        return JSONResponse(status_code=422,
                            content={"message": "Не указан user_id"})
    data = crud_admin.get_activity_user(user_id, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Активностей нет"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.post("/ban")
@manage_role_access(UserRoleEnum.MANAGER)
def ban_user(user_id: int,
             db: Session = Depends(deps.get_db),
             user: User = Depends(get_user)) -> JSONResponse:
    if user_id is None:
        return JSONResponse(status_code=422,
                            content={"message": "Не указан user_id"})
    data = crud_users.user_status_update(user_id=user_id, active=False, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})


@router.post("/token")
@manage_role_access(UserRoleEnum.MANAGER)
def add_user_token(user_id: int,
                   tokens: int,
                   db: Session = Depends(deps.get_db),
                   user: User = Depends(get_user)) -> JSONResponse:
    if user_id is None:
        return JSONResponse(status_code=422,
                            content={"message": "Не указан user_id"})
    data = crud_users.user_add_tokens(user_id, tokens, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})


@router.post("/role")
@manage_role_access(UserRoleEnum.ADMIN)
def change_user_role(user_id: int,
                     role: str,
                     db: Session = Depends(deps.get_db),
                     user: User = Depends(get_user)) -> JSONResponse:
    if user_id is None:
        return JSONResponse(status_code=422,
                            content={"message": "Не указан user_id"})
    data = crud_users.user_change_role(user_id, role, db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi import Request
from starlette.responses import JSONResponse

from app.api.auth import manage_role_access
from app.core import deps
from app.core.decorators import log_api_action
from app.core.deps import get_user
from app.core.schemas import response_schemas, UserCreate, UserUpdate
from app.crud import crud_users
from app.database.models.user import User, UserRoleEnum

router = APIRouter()


# @router.post("/register", responses=response_schemas.general_responses)
# def register_user(user: UserCreate,
#                   db: Session = Depends(deps.get_db)
#                   ) -> JSONResponse:
#     data = crud_users.get_user_by_id(user_id=user.id, db=db)
#     if data is not None:
#         return JSONResponse(status_code=400,
#                             content={"message": "Пользователь уже есть в базе"})
#     data = crud_users.create_user(user=user, db=db)
#     if data is None:
#         return JSONResponse(status_code=500,
#                             content={"message": "Internal Server Error"})
#
#     log_api_action(db, user_from=None, user_to=data.id, action="Зарегистрировался в системе")
#
#     return JSONResponse(status_code=200,
#                         content={"message": "success"})


@router.get("/", responses=response_schemas.single_users_responses)
def get_user_me(user: User = Depends(get_user)) -> JSONResponse:
    if user is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    json_compatible_item_data = jsonable_encoder(user)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


# @router.get("/all", responses=response_schemas.all_users_responses)
# @manage_role_access(UserRoleEnum.MANAGER)
# def get_all_user(db: Session = Depends(deps.get_db),
#                  user: User = Depends(get_user)) -> JSONResponse:
#     db_users = crud_users.get_all_user(db=db)
#     if db_users is None:
#         return JSONResponse(status_code=500,
#                             content={"message": "Пользователи не найдены"})
#     json_compatible_item_data = jsonable_encoder(db_users)
#     return JSONResponse(status_code=200,
#                         content=json_compatible_item_data)


@router.put("/", responses=response_schemas.single_users_responses)
@manage_role_access(UserRoleEnum.MANAGER)
def update_user(user_id: int,
                data: UserUpdate,
                db: Session = Depends(deps.get_db)) -> JSONResponse:
    user = crud_users.get_user_by_id(user_id, db)
    if user is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    data = crud_users.update_user(user, update=data, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.delete("/", responses=response_schemas.general_responses)
@manage_role_access(UserRoleEnum.MANAGER)
def delete_user(user_id: int, db: Session = Depends(deps.get_db)) -> JSONResponse:
    user = crud_users.get_user_by_id(user_id, db)
    if user is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    data = crud_users.delete_user(user, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})


# @router.get("/ban", responses=response_schemas.general_responses)
# def change_active_user(user_id: int, active: bool, db: Session = Depends(deps.get_db),
#                        ) -> JSONResponse:
#     data = crud_users.user_status_update(user_id=user_id, active=active, db=db)
#     if data is None:
#         return JSONResponse(status_code=500,
#                             content={"message": "Internal Server Error"})
#     return JSONResponse(status_code=200,
#                         content={"message": "success"})


@router.get("/accept-terms", responses=response_schemas.general_responses)
@manage_role_access(UserRoleEnum.USER)
def accept_terms_user(db: Session = Depends(deps.get_db),
                      user: User = Depends(get_user)) -> JSONResponse:
    data = crud_users.user_accept_terms(user, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})

    log_api_action(db, user_from=None, user_to=data.id, action="Принял пользовательское соглашение")

    return JSONResponse(status_code=200,
                        content={"message": "success"})


@router.get("/", responses=response_schemas.single_users_responses)
@manage_role_access(UserRoleEnum.MANAGER)
def get_user_id(user_id: int, db: Session = Depends(deps.get_db)) -> JSONResponse:
    user = crud_users.get_user_by_id(user_id, db)
    if user is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    json_compatible_item_data = jsonable_encoder(user)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)

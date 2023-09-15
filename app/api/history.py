from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.api.auth import manage_role_access
from app.core import deps
from app.core.decorators import log_api_action
from app.core.deps import get_user
from app.core.schemas import response_schemas, HistoryCreate
from app.crud import crud_history
from app.database.models.user import User, UserRoleEnum

router = APIRouter()


@router.post("/", responses=response_schemas.general_responses)
@manage_role_access(UserRoleEnum.USER)
def create_history(user_id: int,
                   history: HistoryCreate,
                   db: Session = Depends(deps.get_db),
                   user: User = Depends(get_user)) -> JSONResponse:
    data = crud_history.create_history(user_id=user_id, history=history, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})

    log_api_action(db, user_from=None, user_to=user_id, action=f"Начал поиск продукта {data.title}")

    return JSONResponse(status_code=200,
                        content={"message": "success"})


@router.get("/all", responses=response_schemas.all_histories_responses)
@manage_role_access(UserRoleEnum.USER)
def get_all_histories(user_id: int,
                      db: Session = Depends(deps.get_db),
                      user: User = Depends(get_user)) -> JSONResponse:
    db_histories = crud_history.get_histories(user_id=user_id, db=db)
    if db_histories is None:
        return JSONResponse(status_code=500,
                            content={"message": "Истории запросов не найдены"})
    json_compatible_item_data = jsonable_encoder(db_histories)

    log_api_action(db, user_from=None, user_to=user_id, action="Просмотрел историю запросов")

    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.delete("/all", responses=response_schemas.general_responses)
@manage_role_access(UserRoleEnum.USER)
def delete_all_histories(user_id: int, db: Session = Depends(deps.get_db),
                         user: User = Depends(get_user)) -> JSONResponse:
    data = crud_history.delete_all(user_id=user_id, db=db)
    if data is None:
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})

    log_api_action(db, user_from=None, user_to=user_id, action="Удалил все свои истории запросов")

    return JSONResponse(status_code=200,
                        content={"message": "success"})

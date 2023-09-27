import asyncio

import httpx
from aiohttp import ClientResponse, ClientConnectorError
from fastapi import APIRouter, Depends, WebSocket
from pydantic import UUID4
from starlette.responses import JSONResponse, Response

from app.api.auth import manage_role_access
from app.core.deps import get_user, get_cas_api_client
from app.core.schemas import response_schemas, ProductSearch, ProductSave
from app.crud import crud_bookmarks
from app.database.models.user import User, UserRoleEnum
from app.services import analysis_service
from shared.cas_api_client import CasApiClient
from shared.schemas.task import CasTask, CasPipeline
from shared.schemas.visualizer import AnalysisVisualizationType

router = APIRouter()

url_analysis = "https://4d3a-185-103-110-235.ngrok-free.app/"


# @router.post("/search", responses=response_schemas.search_products_responses)
@router.websocket("/search")
@manage_role_access(UserRoleEnum.USER)
async def search_product(websocket: WebSocket,
                         search_input: str = "ЧелГу",
                         cas_api_client: CasApiClient = Depends(get_cas_api_client),
                         user: User = Depends(get_user)
                         ) -> JSONResponse:
    await websocket.accept()
    cas_task: CasTask = await cas_api_client.run_search_products(search_input)
    await _get_task_result(websocket, cas_api_client, cas_task.task_id)


async def _get_task_result(websocket: WebSocket, cas_api_client: CasApiClient, task_id: UUID4):
    try:
        result = await cas_api_client.get_task_result(task_id)
        while result is None:
            await asyncio.sleep(3)
            result = await cas_api_client.get_task_result(task_id)
        result = result.decode(encoding="utf-8")
        await websocket.send_text(result)
        await websocket.close(code=200)
        return result
    except Exception:
        await websocket.close(code=500, reason="Error in CAS API")


@router.websocket("/task_result")
@manage_role_access(UserRoleEnum.USER)
async def task_result(websocket: WebSocket,
                      task_id: UUID4,
                      cas_api_client: CasApiClient = Depends(get_cas_api_client),
                      user: User = Depends(get_user)):
    await _get_task_result(websocket, cas_api_client, task_id)


@router.websocket("/pipeline_analysis")
@manage_role_access(UserRoleEnum.USER)
async def start_pipeline_analysis(websocket: WebSocket,
                                  product_name_id: str,
                                  analysis_vis_type: AnalysisVisualizationType = AnalysisVisualizationType.all,
                                  cas_api_client: CasApiClient = Depends(get_cas_api_client),
                                  user: User = Depends(get_user)) -> JSONResponse:
    await websocket.accept()
    cas_pipeline: CasPipeline = await cas_api_client.run_pipeline_analysis(product_name_id,
                                                                           analysis_vis_type)
    await websocket.send_text({"pipeline_id": cas_pipeline.pipeline_id})
    await _get_task_result(websocket, cas_api_client, cas_pipeline.pipeline_id)


@router.websocket("/save_report")
@manage_role_access(UserRoleEnum.USER)
async def save_report(websocket: WebSocket,
                      pipeline_id: UUID4,
                      cas_api_client: CasApiClient = Depends(get_cas_api_client),
                      user: User = Depends(get_user)):
    pass
    # получаем CasPipelineComponent
    # по id получаем json для каждого анализа и сохраняем в отчёт в БД


# @router.websocket("/product")
# @manage_role_access(UserRoleEnum.USER)
# async def get_product(websocket: WebSocket,
#                       product_name_id: str,
#                       cas_api_client: CasApiClient = Depends(get_cas_api_client),
#                       user: User = Depends(get_user)) -> JSONResponse:
#     await websocket.accept()
#     cas_task: CasTask = await cas_api_client
    # data = analysis_service.get_product_id(product_id)
    # if data is None:
    #     return JSONResponse(status_code=404,
    #                         content={"message": "Продукт не найден"})
    # json_compatible_item_data = jsonable_encoder(data)
    # return JSONResponse(status_code=200,
    #                     content=json_compatible_item_data)


# @router.get("/product/save")
# @manage_role_access(UserRoleEnum.USER)
# def save_product(user_id: int,
#                  product: ProductSave,
#                  user: User = Depends(get_user)) -> JSONResponse:
#     data = crud_bookmarks.add_bookmark(user_id, product)
#     if data is None:
#         return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
#     return JSONResponse(status_code=200,
#                         content={"message": "success"})


# async def get_analysis_data(url: str, product_id: str):
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url_analysis + url.format(product_id=product_id))
#         print(response)
#         if response.status_code == 200:
#             data = response.json()
#             return data
#         else:
#             return None


# @router.get("/interests/comments")
# @manage_role_access(UserRoleEnum.USER)
# async def get_analysis_interests_comments(product_id: str,
#                                           is_bot: bool = False,
#                                           user: User = Depends(get_user)) -> JSONResponse:
#     url = "analysis_interests/comments?product_name_id={product_id}"
#     data = await get_analysis_data(url, product_id)
#     if data is None:
#         print(1)
#         return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
#
#     if is_bot:
#         img = analysis_service.get_analysis_interests_comments(data)
#         Response(content=img.getvalue(), media_type="image/png")
#     else:
#         json_compatible_item_data = jsonable_encoder(data)
#         return JSONResponse(status_code=200,
#                             content=json_compatible_item_data)


# @router.get("/interests/reviews")
# async def get_analysis_interests_reviews(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_interests/reviews?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/sentimentss/comments/category")
# async def get_analysis_sentiments_comments_category(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_sentiments/comments/category?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/sentimentss/comments/region")
# async def get_analysis_sentiments_comments_region(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_sentiments/comments/region?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/sentimentss/reviews/category")
# async def get_analysis_sentiments_reviews_category(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_sentiments/reviews/category?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/sentimentss/reviews/region")
# async def get_analysis_sentiments_reviews_region(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_sentiments/reviews/region?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/similarity/comments")
# async def get_analysis_similarity_comments(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_similarity/comments?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)
#
#
# @router.get("/similarity/reviews")
# async def get_analysis_similarity_reviews(product_id: str, is_bot: bool = False) -> JSONResponse:
#     url = "analysis_similarity/reviews?product_name_id={product_id}"
#     return await get_analysis_data(url, product_id, is_bot)

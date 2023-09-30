import asyncio
from http import HTTPStatus

from fastapi import APIRouter, Depends, WebSocket
from pydantic import UUID4, TypeAdapter
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.api.auth import manage_role_access, manage_tokens_access
from app.api.exceptions import CasWebError
from app.core.deps import get_user, get_cas_api_client, get_db
from app.crud import crud_analysis_report
from app.database.models.analysis_report import AccessType, AnalysisReport
from app.database.models.user import User, UserRoleEnum
from shared.cas_api_client import CasApiClient
from shared.schemas.analysis import (
    CustomersForAllCategoriesAnalysis,
    GroupRegionallyAllCustomerAnalysis,
    CustomerReputationAnalysisValue
)
from shared.schemas.base import TunedModel
from shared.schemas.product import FoundProduct
from shared.schemas.task import CasTask, CasPipeline, CasPipelineComponent, ResultType
from shared.schemas.visualizer import AnalysisVisualizationType, VisualizationType

router = APIRouter()


@router.websocket("/search")
@manage_role_access(UserRoleEnum.USER)
@manage_tokens_access(5)
async def search_product(websocket: WebSocket,
                         search_input: str = "ЧелГу",
                         cas_api_client: CasApiClient = Depends(get_cas_api_client),
                         user: User = Depends(get_user)
                         ) -> JSONResponse:
    await websocket.accept()
    cas_task: CasTask = await cas_api_client.run_search_products(search_input)
    await _send_task_result(websocket, cas_api_client, cas_task.task_id, ResultType.text)
    await websocket.close()


async def _send_task_result(websocket: WebSocket,
                            cas_api_client: CasApiClient,
                            task_id: UUID4,
                            result_type: ResultType):
    result = await _get_task_result(cas_api_client, task_id)
    if result_type == ResultType.text:
        await websocket.send_text(result.decode(encoding="utf-8"))
    else:
        await websocket.send_bytes(result)
    return result


async def _get_task_result(cas_api_client: CasApiClient, task_id: UUID4):
    try:
        result = await cas_api_client.get_task_result(task_id)
        while result is None:
            await asyncio.sleep(3)
            result = await cas_api_client.get_task_result(task_id)
        return result
    except Exception:
        pass


@router.websocket("/task_result")
@manage_role_access(UserRoleEnum.USER)
async def task_result(websocket: WebSocket,
                      task_id: UUID4,
                      result_type: ResultType,
                      cas_api_client: CasApiClient = Depends(get_cas_api_client),
                      user: User = Depends(get_user)):
    await _send_task_result(websocket, cas_api_client, task_id, result_type)
    await websocket.close(code=200)


@router.websocket("/pipeline_analysis")
@manage_role_access(UserRoleEnum.USER)
@manage_tokens_access(30)
async def start_pipeline_analysis(websocket: WebSocket,
                                  product_name_id: str,
                                  access_type: AccessType = AccessType.BOT_USERS,
                                  analysis_vis_type: AnalysisVisualizationType = AnalysisVisualizationType.all,
                                  db: Session = Depends(get_db),
                                  cas_api_client: CasApiClient = Depends(get_cas_api_client),
                                  user: User = Depends(get_user)) -> JSONResponse:
    await websocket.accept()
    cas_pipeline: CasPipeline = await cas_api_client.run_pipeline_analysis(product_name_id,
                                                                           analysis_vis_type)
    await websocket.send_text(f"\"pipeline_id\": {cas_pipeline.pipeline_id}")
    found_product: FoundProduct = await cas_api_client.get_product_info(product_name_id)
    if found_product is not None:
        report = crud_analysis_report.create_report(owner_id=user.id,
                                                    access_type=access_type,
                                                    product_name_id=found_product.name_id,
                                                    product_image_url=str(found_product.image_url),
                                                    title_report=found_product.fullname,
                                                    db=db)
        if report is None:
            raise CasWebError(message=f"Report creation error.", http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        await websocket.send_text(f"\"report_id\": {report.id}")
        await _send_task_result(websocket, cas_api_client, cas_pipeline.pipeline_id, ResultType.text)
        await websocket.close()
    else:
        raise CasWebError(message=f"Product {product_name_id} is not found.", http_status_code=HTTPStatus.NOT_FOUND)


@router.websocket("/save_report")
@manage_role_access(UserRoleEnum.USER)
@manage_tokens_access(30)
async def save_report(websocket: WebSocket,
                      pipeline_id: UUID4,
                      report_id: UUID4,
                      db: Session = Depends(get_db),
                      cas_api_client: CasApiClient = Depends(get_cas_api_client),
                      user: User = Depends(get_user)):
    await websocket.accept()
    report: AnalysisReport = crud_analysis_report.get_report(report_id, db)
    if report is not None:
        if report.owner_id != user.id:
            raise CasWebError(message="You can't save this report because you don't own it.",
                              http_status_code=HTTPStatus.FORBIDDEN)
        pipeline_json = await _get_task_result(cas_api_client, pipeline_id)
        CasPipelineComponentListValidator = TypeAdapter(list[CasPipelineComponent])
        pipeline: list[CasPipelineComponent] = CasPipelineComponentListValidator.validate_json(pipeline_json.decode(encoding="utf-8"))
        for item in pipeline:
            result = await _get_task_result(cas_api_client, item.analysis_task_id)
            if result is None:
                raise CasWebError(message=f"Analysis data for pipeline {pipeline_id} is not found.",
                                  http_status_code=HTTPStatus.NOT_FOUND)
            item_json = result.decode(encoding="utf-8")
            crud_analysis_report.update_analysis_data_report(report.id,
                                                             analysis_type=item.analysis_type,
                                                             json=item_json,
                                                             db=db)
        await websocket.send_text("{\"save_report\": success}")
        await websocket.close()
    else:
        raise CasWebError(message=f"Analysis report {report_id} is not found.", http_status_code=HTTPStatus.NOT_FOUND)


@router.websocket("/visualise_analysis_value_category")
@manage_role_access(UserRoleEnum.USER)
async def visualise_analysis_value_category(websocket: WebSocket,
                                            vis_type: VisualizationType,
                                            title: str,
                                            title_object_count: str,
                                            title_analysis_value: str,
                                            cas_api_client: CasApiClient = Depends(get_cas_api_client),
                                            user: User = Depends(get_user)):
    await websocket.accept()
    await _visualise(websocket,
                     cas_api_client,
                     CustomersForAllCategoriesAnalysis,
                     await websocket.receive_text(),
                     cas_api_client.run_visualise_analysis_value_category,
                     vis_type=vis_type,
                     title=title,
                     title_object_count=title_object_count,
                     title_analysis_value=title_analysis_value)


@router.websocket("/visualise_analysis_value_region")
@manage_role_access(UserRoleEnum.USER)
async def visualise_analysis_value_region(websocket: WebSocket,
                                          vis_type: VisualizationType,
                                          title: str,
                                          title_object_count: str,
                                          title_analysis_value: str,
                                          cas_api_client: CasApiClient = Depends(get_cas_api_client),
                                          user: User = Depends(get_user)):
    await websocket.accept()
    await _visualise(websocket,
                     cas_api_client,
                     GroupRegionallyAllCustomerAnalysis,
                     await websocket.receive_text(),
                     cas_api_client.run_visualise_analysis_value_region,
                     vis_type=vis_type,
                     title=title,
                     title_object_count=title_object_count,
                     title_analysis_value=title_analysis_value)


async def _visualise(websocket: WebSocket,
                     cas_api_client: CasApiClient,
                     model: type[TunedModel],
                     json: str,
                     vis_func,
                     **kwargs):
    validator = TypeAdapter(list[model])
    data: list[model] = validator.validate_json(json)
    cas_task: CasTask = await vis_func(data, **kwargs)
    if kwargs["vis_type"] == VisualizationType.image:
        await _send_task_result(websocket, cas_api_client, cas_task.task_id, ResultType.bytes)
    else:
        await _send_task_result(websocket, cas_api_client, cas_task.task_id, ResultType.text)
    await websocket.close()


@router.websocket("/visualise_histogram")
@manage_role_access(UserRoleEnum.USER)
async def visualise_histogram(websocket: WebSocket,
                              vis_type: VisualizationType,
                              title: str,
                              title_object_count: str,
                              title_analysis_value: str,
                              cas_api_client: CasApiClient = Depends(get_cas_api_client),
                              user: User = Depends(get_user)):
    await websocket.accept()
    await _visualise(websocket,
                     cas_api_client,
                     CustomerReputationAnalysisValue,
                     await websocket.receive_text(),
                     cas_api_client.run_visualise_histogram,
                     vis_type=vis_type,
                     title=title,
                     title_object_count=title_object_count,
                     title_analysis_value=title_analysis_value)


@router.websocket("/visualise_quantity_category")
@manage_role_access(UserRoleEnum.USER)
async def visualise_quantity_category(websocket: WebSocket,
                                      vis_type: VisualizationType,
                                      title: str,
                                      title_object_count: str,
                                      cas_api_client: CasApiClient = Depends(get_cas_api_client),
                                      user: User = Depends(get_user)):
    await websocket.accept()
    await _visualise(websocket,
                     cas_api_client,
                     CustomerReputationAnalysisValue,
                     await websocket.receive_text(),
                     cas_api_client.run_visualise_quantity_category,
                     vis_type=vis_type,
                     title=title,
                     title_object_count=title_object_count)


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

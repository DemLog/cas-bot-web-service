import httpx
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, Response

from app.core.schemas import response_schemas, ProductSearch, ProductSave
from app.crud import crud_bookmarks
from app.services import analysis_service

router = APIRouter()

url_analysis = "https://4d3a-185-103-110-235.ngrok-free.app/"


@router.post("/search", responses=response_schemas.search_products_responses)
def search_product(search_product: ProductSearch) -> JSONResponse:
    data = analysis_service.get_products_search(product_search=search_product)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.get("/product")
def get_product(product_id: str) -> JSONResponse:
    data = analysis_service.get_product_id(product_id)
    if data is None:
        return JSONResponse(status_code=404,
                            content={"message": "Продукт не найден"})
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(status_code=200,
                        content=json_compatible_item_data)


@router.get("/product/save")
def save_product(user_id: int, product: ProductSave) -> JSONResponse:
    data = crud_bookmarks.add_bookmark(user_id, product)
    if data is None:
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200,
                        content={"message": "success"})


async def get_analysis_data(url: str, product_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url_analysis + url.format(product_id=product_id))
        print(response)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None


@router.get("/interests/comments")
async def get_analysis_interests_comments(product_id: str, is_bot: bool = False) -> JSONResponse:
    url = "analysis_interests/comments?product_name_id={product_id}"
    data = await get_analysis_data(url, product_id)
    if data is None:
        print(1)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    if is_bot:
        img = analysis_service.get_analysis_interests_comments(data)
        Response(content=img.getvalue(), media_type="image/png")
    else:
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(status_code=200,
                            content=json_compatible_item_data)


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

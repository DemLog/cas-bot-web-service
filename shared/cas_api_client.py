from functools import wraps
from http.client import BAD_GATEWAY
from typing import Optional
from uuid import UUID

from aiohttp import ClientSession, ClientError, ClientResponse
from aiohttp.web_response import Response

from app.api.exceptions import CasWebError
from shared.schemas.analysis import (
    CustomersForAllCategoriesAnalysis,
    GroupRegionallyAllCustomerAnalysis,
    CustomerReputationAnalysisValue,
    CustomersForAllCategoriesBaseAnalysis,
    AnalysisObjectType,
    AnalysisPrepareSimilarityObjectType,
    SentimentAnalysisType,
    SimilarityAnalysisType
)
from shared.schemas.base import TunedModel
from shared.schemas.product import FoundProduct
from shared.schemas.task import CasTask, CasPipeline
from shared.schemas.visualizer import AnalysisVisualizationType, VisualizationType


class CasApiClient:
    """
    API-client for Customer Analysis Service interaction.

    Предполагаемый сценарий использования (без скрапинга и запуска моделей):
    1. Выполнять поиск через run_search_products, получить результат, как он будет готов - get_task_result;
    2. Запускать конвеер для выбранного продукта, который сгруппирует готовые данные и запустит визуализацию через run_pipeline_analysis
    3. Получаем результат - get_task_result. Формат:
    UUID4 - идентификаторы отдельных задач конвеера
    [
        {
            "analysis_task_id": "UUID4", // задача агрегирования данных для визуализации
            "analysis_title": "Название запущенного анализа, которое можно показывать пользователю",
            "visualization_html_task_id": "UUID4",
            "visualization_html_title": "Надпись: Визуализация html",
            "visualization_image_task_id": "UUID4",
            "visualization_image_title": "Надпись: Визуализация растрового изображения"
        },
        ...
    ]

    Если какое-то поле ..._task_id оказалось null - это либо ошибка, либо такая задач не была запрошена (например, визуализация html)

    Предполагаю отображать пользователю в формате:

    Анализ настроений комментаторов продукта:
        - подготовка данных: ✅
        - Визуализация html: 🛠
        - Визуализация растрового изображения: ✅

    ... И так по всем задачам конвеера
    4. Переодически выполнять проверку готовности этапов конвеера.
    5. По мере готовности начинать отдавать данные:
        - растровое изобраение в качестве обложки;
        - html, когда он готов, добавлять кнопку,
        которая откроет интерактивную диаграмму в новой вкладки (для бота telegram web app)
    как только все задачи выполнятся и данные будут доступны на клиенте, скрыть список

    Вышеописанный сценарий - это только вывод готовых данных без их сбора.
    При выполнении может произойти ошибка, в случае нехватки данных -> предлагать пользователю запустить сбор и анализ.

    Сценарий подготовки данных и анализа:
    1. run_scraper_product_data - запуск скрапера для сбора всех необходимых данных по продукту
    2. run_sentiment_analysis_preparer - подготовка анализа настроений
    3. run_similarity_analysis_preparer - подготовка анализа сходства

    после этого, по продукту можно получить анализ по собранным и подготовленным данным

    Формирование отчёта:
    В отчёте анализа сохраняются только данные в формате json, без визуализации.
    Для их получения использовать UUID4 данных анализа get_task_result
    Данные сохранять в БД
    В дальнейшем, при открытии отчёта для отображения использовать:
    run_visualise_analysis_value_category
    run_visualise_analysis_value_region
    run_visualise_histogram
    run_visualise_quantity_category
    """

    _x_api_header = "X-API-Key"

    def __init__(self,
                 cas_api_url: str,
                 *,
                 api_key: str,
                 session: Optional[ClientSession] = None):
        if session is None:
            session = ClientSession()

        self.session = session
        self.cas_api_url = cas_api_url
        self.api_key = api_key

    async def _post(self, path: str, data: any):
        return await self.session.post(f"{self.cas_api_url}{path}",
                                       json=data,
                                       headers={self._x_api_header: self.api_key})

    async def _get(self, path: str):
        return await self.session.get(f"{self.cas_api_url}{path}",
                                      headers={self._x_api_header: self.api_key})

    async def get_task_result(self, task_id: UUID | str):
        response: ClientResponse = await self._get(path=f"result?task_id={task_id}")
        match response.status:
            case 200:
                return await response.content.read()
            case 202:
                return None
        raise Exception

    async def get_product_info(self, product_name_id: str) -> Optional[FoundProduct]:
        response: ClientResponse = await self._get(path=f"product/info?product_name_id={product_name_id}")
        if response.status == 200:
            return FoundProduct.model_validate_json(await response.content.read())
        else:
            return None

    async def run_pipeline_analysis(self, product_name_id: str, analysis_vis_type: AnalysisVisualizationType) -> CasPipeline:
        response: ClientResponse = await self._get(path=f"pipeline/shaper/comprehensive_analysis?"
                                                   f"product_name_id={product_name_id}&"
                                                   f"analysis_vis_type={analysis_vis_type.value}")
        if response.status == 200:
            return CasPipeline.model_validate_json((await response.content.read()).decode(encoding="utf-8"))
        else:
            raise Exception

    @staticmethod
    def _menage_run_task():
        def decorator(f):
            @wraps(f)
            async def wrapped_f(self, *args, **kwargs):
                try:
                    response: ClientResponse = await f(self, *args, **kwargs)
                except ClientError as ex:
                    print(ex)
                    raise CasWebError(message="Error in CAS API", http_status_code=BAD_GATEWAY)

                if response.status == 200:
                    return CasTask.model_validate_json(await response.content.read())
                else:
                    raise Exception

            return wrapped_f

        return decorator

    @_menage_run_task()
    async def _run_visualise(self,
                             data: list[TunedModel],
                             *,
                             vis_path: str,
                             vis_type: VisualizationType,
                             title: str,
                             title_object_count: str,
                             title_analysis_value: Optional[str] = None):
        path = (f"visualizer/{vis_path}?" +
                f"vis_type={vis_type.value}&" +
                f"title={title}&" +
                f"title_object_count={title_object_count}&")
        if title_analysis_value is not None:
            path += f"title_analysis_value={title_analysis_value}"
        return await self._post(path=path,
                                data=[item.model_dump() for item in data])

    async def run_visualise_analysis_value_category(self,
                                                    data: list[CustomersForAllCategoriesAnalysis],
                                                    *,
                                                    vis_type: VisualizationType,
                                                    title: str,
                                                    title_object_count: str,
                                                    title_analysis_value: str):
        return await self._run_visualise(data,
                                         vis_path="analysis_value/category",
                                         vis_type=vis_type,
                                         title=title,
                                         title_object_count=title_object_count,
                                         title_analysis_value=title_analysis_value)

    async def run_visualise_analysis_value_region(self,
                                                  data: list[GroupRegionallyAllCustomerAnalysis],
                                                  *,
                                                  vis_type: VisualizationType,
                                                  title: str,
                                                  title_object_count: str,
                                                  title_analysis_value: str):
        return await self._run_visualise(data,
                                         vis_path="analysis_value/region",
                                         vis_type=vis_type,
                                         title=title,
                                         title_object_count=title_object_count,
                                         title_analysis_value=title_analysis_value)

    async def run_visualise_histogram(self,
                                      data: list[CustomerReputationAnalysisValue],
                                      *,
                                      vis_type: VisualizationType,
                                      title: str,
                                      title_object_count: str,
                                      title_analysis_value: str):
        return await self._run_visualise(data,
                                         vis_path="histogram",
                                         vis_type=vis_type,
                                         title=title,
                                         title_object_count=title_object_count,
                                         title_analysis_value=title_analysis_value)

    async def run_visualise_quantity_category(self,
                                              data: list[CustomersForAllCategoriesBaseAnalysis],
                                              *,
                                              vis_type: VisualizationType,
                                              title: str,
                                              title_object_count: str):
        return await self._run_visualise(data,
                                         vis_path="quantity/category",
                                         vis_type=vis_type,
                                         title=title,
                                         title_object_count=title_object_count)

    @_menage_run_task()
    async def run_search_products(self, search_input: str = "ЧелГу", max_count_items: int = 5):
        return await self._get(path=f"scraper/search?"
                                    f"search_input={search_input}&"
                                    f"max_count_items={max_count_items}")

    @_menage_run_task()
    async def run_scraper_product_data(self,
                                       product_name_id: str = "chelyabinskiy_gosudarstvenniy_universitet_russia_chelyabinsk"):
        return await self._get(path=f"scraper/products_data?"
                                    f"product_name_id={product_name_id}")

    @_menage_run_task()
    async def run_scraper_category_data(self,
                                        href_product_path: str = "/in_town/education_companies/"):
        return await self._get(path=f"scraper/category_data?"
                                    f"href_product_path={href_product_path}")

    @_menage_run_task()
    async def run_sentiment_analysis_preparer(self,
                                              analysis_object_type: AnalysisObjectType,
                                              version_mark: str = "v1",
                                              is_override: bool = False):
        return await self._get(path=f"analysis/preparer/sentiment?"
                                    f"analysis_object_type={analysis_object_type}&"
                                    f"version_mark={version_mark}&"
                                    f"is_override={is_override}")

    @_menage_run_task()
    async def run_similarity_analysis_preparer(self,
                                               analysis_object_type: AnalysisPrepareSimilarityObjectType,
                                               version_mark: str = "v1",
                                               is_override: bool = False):
        return await self._get(path=f"analysis/preparer/similarity?"
                                    f"analysis_object_type={analysis_object_type}&"
                                    f"version_mark={version_mark}&"
                                    f"is_override={is_override}")

    @_menage_run_task()
    async def run_interests_analysis_provider(self,
                                              product_name_id: str,
                                              analysis_object_type: AnalysisObjectType):
        return await self._get(path=f"analysis/provider/interests?"
                                    f"product_name_id={product_name_id}"
                                    f"analysis_object_type={analysis_object_type}")

    @_menage_run_task()
    async def run_sentiment_analysis_provider(self,
                                              product_name_id: str,
                                              analysis_object_type: AnalysisObjectType,
                                              sentiment_analysis_type: SentimentAnalysisType):
        return await self._get(path=f"analysis/provider/sentiment?"
                                    f"product_name_id={product_name_id}"
                                    f"analysis_object_type={analysis_object_type}&"
                                    f"sentiment_analysis_type={sentiment_analysis_type}")

    @_menage_run_task()
    async def run_similarity_analysis_provider(self,
                                               product_name_id: str,
                                               analysis_object_type: AnalysisObjectType,
                                               similarity_analysis_type: SimilarityAnalysisType):
        return await self._get(path=f"analysis/provider/similarity?"
                                    f"product_name_id={product_name_id}"
                                    f"analysis_object_type={analysis_object_type}&"
                                    f"similarity_analysis_type={similarity_analysis_type}")

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> "CasApiClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

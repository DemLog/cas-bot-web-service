from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import manage_role_access
from app.api.exceptions import CasWebError
from app.core.deps import get_user, get_db
from app.core.schemas import AnalysisReport as AnalysisReportSchema, UserInfo, ProductInfo, AnalysisReportData, \
    ReportJsonData
from app.crud import crud_analysis_report
from app.database.models.analysis_report import AnalysisReport
from app.database.models.user import User, UserRoleEnum
from shared.schemas.analysis import AnalysisType

router = APIRouter()


@router.get(
    "/list",
    response_model=list[AnalysisReportSchema]
)
@manage_role_access(UserRoleEnum.USER)
async def get_list_reports(db: Session = Depends(get_db),
                           user: User = Depends(get_user)) -> list[AnalysisReportSchema]:
    db_reports: list[AnalysisReport] = crud_analysis_report.get_reports_for_user(user, db)
    reports: list[AnalysisReportSchema] =\
        [AnalysisReportSchema(
            id=item.id,
            owner=UserInfo(first_name=user.first_name,
                           last_name=user.last_name,
                           role=user.role),
            access_type=item.access_type,
            product=ProductInfo(product_name_id=item.product_name_id,
                                product_image_url=item.product_image_url,
                                title=item.title),
            formation_date=item.formation_date
        ) for item in db_reports]

    return reports


@router.get(
    "/info/{report_id}",
    response_model=AnalysisReportSchema
)
@manage_role_access(UserRoleEnum.USER)
async def get_info_report(report_id: UUID,
                          db: Session = Depends(get_db),
                          user: User = Depends(get_user)) -> AnalysisReportSchema:
    return _get_info_report(report_id, db, user)


def _get_info_report(report_id: UUID, db: Session, user: User):
    db_report: AnalysisReport = crud_analysis_report.get_report(report_id, db)
    if db_report is None:
        raise CasWebError(message="Report not found", http_status_code=HTTPStatus.NOT_FOUND)
    else:
        return AnalysisReportSchema(
            id=db_report.id,
            owner=UserInfo(first_name=user.first_name,
                           last_name=user.last_name,
                           role=user.role),
            access_type=db_report.access_type,
            product=ProductInfo(product_name_id=db_report.product_name_id,
                                product_image_url=db_report.product_image_url,
                                title=db_report.title),
            formation_date=db_report.formation_date
        )


@router.get(
    "/data/{report_id}",
    response_model=AnalysisReportSchema
)
@manage_role_access(UserRoleEnum.USER)
async def get_data_report(report_id: UUID,
                          db: Session = Depends(get_db),
                          user: User = Depends(get_user)) -> AnalysisReportData:
    db_report: AnalysisReport = crud_analysis_report.get_report(report_id, db)
    if db_report is None:
        raise CasWebError(message="Report not found", http_status_code=HTTPStatus.NOT_FOUND)
    else:
        return AnalysisReportData(
            id=db_report.id,
            owner=UserInfo(first_name=user.first_name,
                           last_name=user.last_name,
                           role=user.role),
            access_type=db_report.access_type,
            product=ProductInfo(product_name_id=db_report.product_name_id,
                                product_image_url=db_report.product_image_url,
                                title=db_report.title),
            formation_date=db_report.formation_date,
            data=[
                ReportJsonData(analysis_type=AnalysisType.interest_reviewers,
                               json_data=db_report.analysis_interests_reviewers_data_json),
                ReportJsonData(analysis_type=AnalysisType.interest_commentators,
                               json_data=db_report.analysis_interests_commentators_data_json),
                ReportJsonData(analysis_type=AnalysisType.sentiment_category_reviewers,
                               json_data=db_report.analysis_sentiment_reviewers_category_data_json),
                ReportJsonData(analysis_type=AnalysisType.sentiment_category_commentators,
                               json_data=db_report.analysis_sentiment_commentators_category_data_json),
                ReportJsonData(analysis_type=AnalysisType.sentiment_region_reviewers,
                               json_data=db_report.analysis_sentiment_reviewers_region_data_json),
                ReportJsonData(analysis_type=AnalysisType.sentiment_region_commentators,
                               json_data=db_report.analysis_sentiment_commentators_region_data_json),
                ReportJsonData(analysis_type=AnalysisType.similarity_reputation_reviewers,
                               json_data=db_report.analysis_similarity_reviewers_reputation_data_json),
                ReportJsonData(analysis_type=AnalysisType.similarity_reputation_commentators,
                               json_data=db_report.analysis_similarity_commentators_reputation_data_json),
                ReportJsonData(analysis_type=AnalysisType.similarity_category_reviewers,
                               json_data=db_report.analysis_similarity_reviewers_category_data_json),
                ReportJsonData(analysis_type=AnalysisType.similarity_category_commentators,
                               json_data=db_report.analysis_similarity_commentators_category_data_json),
            ]
        )

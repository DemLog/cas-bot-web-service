from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from app.api.exceptions import CasWebError
from app.database.models.analysis_report import AnalysisReport, AccessType
from shared.schemas.analysis import AnalysisType


class CRUDAnalysisReport:
    def get_report(self, report_id: str, db: Session):
        try:
            data = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
            return data
        except SQLAlchemyError as e:
            return None

    def create_report(self,
                      pipeline_id: str,
                      owner_id: str,
                      access_type: AccessType,
                      product_name_id: str,
                      product_image_url: str,
                      title_report: str,
                      db: Session):
        report = self.get_report(pipeline_id, db)
        if report is not None:
            raise CasWebError(message="Such a report already exists", http_status_code=status.CONFLICT)
        else:
            try:
                report = AnalysisReport(
                    id=pipeline_id,
                    owner_id=owner_id,
                    access_type=access_type,
                    product_name_id=product_name_id,
                    product_image_url=product_image_url,
                    title=title_report
                )
                db.add(report)
                db.commit()
                db.refresh(report)
                return report
            except SQLAlchemyError as e:
                return None

    def update_analysis_data_report(self, report_id: str, analysis_type: AnalysisType, json: str, db: Session):
        report: AnalysisReport = self.get_report(report_id, db)
        if report is None or not report.is_exist:
            raise CasWebError(message="The report doesn't exist", http_status_code=status.HTTP_404_NOT_FOUND)
        else:
            if json is None or analysis_type is None:
                raise CasWebError(message="The data for the report is not correct", http_status_code=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    match analysis_type:
                        case AnalysisType.interest_reviewers:
                            report.analysis_interests_reviewers_data_json = json
                        case AnalysisType.interest_commentators:
                            report.analysis_interests_commentators_data_json = json
                        case AnalysisType.sentiment_category_reviewers:
                            report.analysis_sentiment_reviewers_category_data_json = json
                        case AnalysisType.sentiment_category_commentators:
                            report.analysis_sentiment_commentators_category_data_json = json
                        case AnalysisType.sentiment_region_reviewers:
                            report.analysis_sentiment_reviewers_region_data_json = json
                        case AnalysisType.sentiment_region_commentators:
                            report.analysis_sentiment_commentators_region_data_json = json
                        case AnalysisType.similarity_reputation_reviewers:
                            report.analysis_similarity_reviewers_reputation_data_json = json
                        case AnalysisType.similarity_reputation_commentators:
                            report.analysis_similarity_commentators_reputation_data_json = json
                        case AnalysisType.similarity_category_reviewers:
                            report.analysis_similarity_reviewers_category_data_json = json
                        case AnalysisType.similarity_category_commentators:
                            report.analysis_similarity_commentators_category_data_json = json
                    db.commit()
                    db.refresh(report)
                    return report
                except SQLAlchemyError as e:
                    return None

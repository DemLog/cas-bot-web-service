from typing import Optional

from pydantic import UUID4

from shared.schemas.base import TunedModel


class CasTask(TunedModel):
    task_id: UUID4
    task_status: str


class CasPipelineComponent(TunedModel):
    analysis_task_id: UUID4
    analysis_title: str
    visualization_image_task_id: Optional[UUID4]
    visualization_image_title: str
    visualization_html_task_id: Optional[UUID4]
    visualization_html_title: str


class CasPipeline(TunedModel):
    pipeline_id: UUID4
    pipeline_status: str

from enum import StrEnum


class VisualizationType(StrEnum):
    image: str = "image"
    html: str = "html"


class AnalysisVisualizationType(StrEnum):
    image: str = "image"
    html: str = "html"
    all: str = "all"
    none: str = "none"

from pydantic import BaseModel


class HistoryCreate(BaseModel):
    title: str
    url: str


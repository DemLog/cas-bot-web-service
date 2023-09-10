from pydantic import BaseModel
from typing import Generator


class TunedModel(BaseModel):
    @classmethod
    def example(cls) -> dict:
        return {key: value.type_.__name__ for key, value in cls.__fields__.items()}

    class Config:
        orm_mode = True

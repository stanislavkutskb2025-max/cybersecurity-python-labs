from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class CategoryCreate(StrictModel):
    name: str = Field(min_length=1, max_length=50)


class CategoryRead(CategoryCreate):
    id: int = Field(gt=0)


class RecordCreate(StrictModel):
    code: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=120)
    category_id: int = Field(gt=0)
    value: float = Field(ge=0)
    status: Literal["new", "in_progress", "done"]


class RecordReplace(RecordCreate):
    pass


class RecordRead(RecordCreate):
    id: int = Field(gt=0)
    category_name: str

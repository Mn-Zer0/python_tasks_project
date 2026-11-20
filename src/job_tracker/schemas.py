import re

from pydantic import BaseModel, Field, field_validator

from .domain import Status


class ValidatedVacancy(BaseModel):
    """Pydantic модель для валидации"""

    id: str = Field(description="ID в формате VID-XXXXXX")
    title: str = Field(min_length=1, max_length=200, description="Название вакансии")
    salary: int = Field(ge=0, description="Зарплата, не может быть отрицательной")
    status: Status = Field(description="Статус: open или closed")

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        if not re.fullmatch(r"VID-\d{6}", v):
            raise ValueError(f"id должен быть в формате VAC-XXXXXX, получено: {v!r}")
        return v

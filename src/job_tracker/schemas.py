import re

from pydantic import BaseModel, Field, field_validator

from .domain import Status


class ValidatedVacancy(BaseModel):
    """Pydantic модель для валидации"""

    id: int = Field(description="ID")
    title: str = Field(min_length=1, max_length=200, description="Название вакансии")
    salary: int = Field(ge=0, description="Зарплата, не может быть отрицательной")
    status: Status = Field(description="Статус: open или closed")

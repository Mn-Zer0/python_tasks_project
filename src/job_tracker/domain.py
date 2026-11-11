from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    """Статус вакансии"""

    OPEN = "open"
    CLOSED = "closed"


class DomainError(Exception):
    """Кастомный Exception"""

    pass


@dataclass
class Vacancy:
    """Вакансия - доменная сущность"""

    ID: str
    title: str
    salary: int
    status: Status

    def close(self) -> None:
        """Перевести вакансию в статус CLOSED"""
        if self.status is Status.CLOSED:
            raise DomainError("Вакансия уже закрыта")
        self.status = Status.CLOSED

    def open(self) -> None:
        """Перевести вакансию в статус OPEN"""
        if self.status is Status.OPEN:
            raise DomainError("Вакансия уже открыта")
        self.status = Status.OPEN

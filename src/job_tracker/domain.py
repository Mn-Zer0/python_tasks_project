from dataclasses import dataclass
from enum import StrEnum


from typing import Protocol


class Status(StrEnum):
    """Статус вакансии"""
    OPEN = "open"
    CLOSED = "closed"


class ApplicationStatus(StrEnum):
    """Статус вашей заявки на вакансию."""
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class DomainError(Exception):
    """Кастомный Exception"""
    pass


@dataclass
class Vacancy:
    """Вакансия - доменная сущность"""

    id: str
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


@dataclass
class Application:
    id: str
    status: ApplicationStatus = ApplicationStatus.SAVED

    def move_to(self, new: ApplicationStatus) -> None:  # метод сущности Application
        if new == self.status:
            return  # повтор ничего не меняет
        if new not in ALLOWED[self.status]:
            raise TransitionError(
                f"нельзя перейти из {self.status} в {new}; "
                f"из {self.status} разрешено: {ALLOWED[self.status]}")
        self.status = new


class SourceError(Exception):
    """Источник не смог отдать данные"""
    pass


class VacancySource(Protocol):
    """Источник вакансий
    Реализации возвращают готовые доменные объекты
    """
    def fetch(self) -> list[Vacancy]: ...


class TransitionError(Exception):
    """Переход между этими состояниями запрещён правилами домена"""
    pass

ALLOWED: dict[ApplicationStatus, frozenset[ApplicationStatus]] = {
    ApplicationStatus.SAVED: frozenset({ApplicationStatus.APPLIED}),
    ApplicationStatus.APPLIED: frozenset({ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED}),
    ApplicationStatus.INTERVIEW: frozenset({ApplicationStatus.OFFER, ApplicationStatus.REJECTED}),
    ApplicationStatus.REJECTED: frozenset({}),
    ApplicationStatus.OFFER: frozenset({}),
}



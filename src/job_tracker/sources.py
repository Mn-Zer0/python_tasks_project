from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from .application import to_vacancy
from .domain import SourceError, Status, Vacancy, VacancySource
from .schemas import ValidatedVacancy
from .storage import StorageFormatError, read_json


class FixedSource:
    """Фиксированный источник вакансий"""

    def fetch(self) -> list[Vacancy]:
        return [
            Vacancy(id="VID-000001", title="Python", salary=120000, status=Status.OPEN),
            Vacancy(id="VID-000002", title="Java", salary=150000, status=Status.CLOSED),
        ]


class JsonFileSource:
    """Источник вакансий из JSON-файла.
    Читает данные, валидирует через ValidatedVacancy и возвращает
    доменные объекты
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def fetch(self) -> list[Vacancy]:
        try:
            data = read_json(self._path)
            raw_vacancies = [ValidatedVacancy(**record) for record in data]
            vacancies = [to_vacancy(i) for i in raw_vacancies]

            return vacancies
        except StorageFormatError as e:
            raise SourceError(f"Не удалось прочитать {self._path}: {e}") from e
        except ValidationError as e:
            raise SourceError(f"Данные в {self._path} не прошли валидацию: {e}") from e


def make_source(config: Literal["json", "fixed"], path: Path | None = None) -> VacancySource:
    """Выбрать реализацию VacancySource по конфигурации"""
    match config:
        case "fixed":
            return FixedSource()
        case "json":
            if path is None:
                raise ValueError("для источника 'json' нужен путь к файлу")
            return JsonFileSource(path)
        case _:
            raise ValueError("неизвестный источник")

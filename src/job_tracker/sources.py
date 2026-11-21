from pathlib import Path
from typing import Literal

from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

from .application import to_vacancy
from .domain import SourceError, Status, Vacancy, VacancySource, ApplicationSource, Application, ApplicationStatus, \
    VacancyWriter, VacancyReader
from .schemas import ValidatedVacancy
from .storage import StorageFormatError, read_json
from .db import VacancyRow, ApplicationRow

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

class FixedSource:
    """Фиксированный источник вакансий"""

    def fetch(self) -> list[Vacancy]:
        return [
            Vacancy(id=1, title="Python", salary=120000, status=Status.OPEN),
            Vacancy(id=2, title="Java", salary=150000, status=Status.CLOSED),
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

class DatabaseVacancySource:
    """Источник вакансий из базы данных"""
    def fetch(self) -> list[Vacancy]:
        vacancies = []

        with Session(engine) as session:
            r = select(VacancyRow)
            result = session.scalars(r)
            rows = result.all()

            for row in rows:
                v = Vacancy(
                    id=row.id,
                    title=row.title,
                    salary=row.salary,
                    status=Status(row.status)
                )
                vacancies.append(v)

            return vacancies

def make_vacancy_source(config: Literal["json", "fixed", "db"], path: Path | None = None) -> VacancySource:
    """Фабирика Vacancy. Выбрать реализацию VacancySource по конфигурации"""
    match config:
        case "fixed":
            return FixedSource()
        case "json":
            if path is None:
                raise ValueError("для источника 'json' нужен путь к файлу")
            return JsonFileSource(path)
        case "db":
            return DatabaseVacancySource()
        case _:
            raise ValueError("неизвестный источник")


class DatabaseApplicationSource:
    """Источник application из базы данных"""
    def get_by_id(self, vacancy_id: int) -> Application | None:
        with Session(engine) as session:
            r = select(ApplicationRow).where(ApplicationRow.vacancy_id == vacancy_id)
            row = session.scalars(r).first()

            if row is not None:
                a = Application(
                    id=row.id,
                    vacancy_id=row.vacancy_id,
                    status=ApplicationStatus(row.status)
                )
                return a
            return None

    def save(self, application: Application) -> None:
        with Session(engine) as session:
            r = select(ApplicationRow).where(ApplicationRow.vacancy_id == application.vacancy_id)
            result = session.scalars(r).first()
            if result is not None:
                result.status = application.status
            else:
                row = ApplicationRow(
                    vacancy_id=application.vacancy_id,
                    status=application.status
                )
                session.add(row)
            session.commit()

    def fetch(self) -> list[Application]:
        with Session(engine) as session:
            r = select(ApplicationRow)
            result = session.scalars(r)
            rows = result.all()

            applications = []

            for row in rows:
                a = Application(
                    id=row.id,
                    vacancy_id=row.vacancy_id,
                    status=ApplicationStatus(row.status)
                )
                applications.append(a)

            return applications

def make_application_source() -> ApplicationSource:
    return DatabaseApplicationSource()


class VacancyDatabaseWriter:
    """Источник вакансий из базы данных для записи в бд
    Нужен для того чтобы не ломать фабрику make_vacancy_source и
    все её источники
    """
    def seed(self, vacancy: Vacancy) -> bool:
        with Session(engine) as session:
            try:
                row = VacancyRow(
                    id=vacancy.id,
                    title=vacancy.title,
                    salary=vacancy.salary,
                    status=Status(vacancy.status)
                )
                session.add(row)
                session.commit()
                return True
            except IntegrityError as e:
                session.rollback()
        return False


def make_source_vacancy_writer() -> VacancyWriter:
    return VacancyDatabaseWriter()


class VacancyDatabaseReader:
    """Источник вакансий из базы данных, возвращает отсортированные вакансии"""

    def fetch(self,
              status: str | None = None,
              sort_by: str = "id",
              order: str = "asc",
              limit: int = 10,
              offset: int = 0
              ) -> list[Vacancy]:
        with Session(engine) as session:
            r = select(VacancyRow)

            if status is not None:
                r = r.where(VacancyRow.status == status)

            column = getattr(VacancyRow, sort_by)
            direction = getattr(column, order)()

            r = r.order_by(direction, VacancyRow.id.asc())
            r = r.limit(limit).offset(offset)

            rows = session.scalars(r).all()

            vacancies = []

            for row in rows:
                v = Vacancy(
                    id = row.id,
                    title = row.title,
                    salary = row.salary,
                    status = Status(row.status)
                )
                vacancies.append(v)

            return vacancies


def make_source_vacancy_reader() -> VacancyReader:
    return VacancyDatabaseReader()
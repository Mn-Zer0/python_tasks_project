import pytest
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from pathlib import Path
from sqlalchemy.orm import Session

from job_tracker.domain import Status, Vacancy
from job_tracker.schemas import ValidatedVacancy
from job_tracker.db import Base


load_dotenv()


@pytest.fixture
def valid_vacancy_model() -> ValidatedVacancy:
    return ValidatedVacancy(
        id=1, title="Python Разработчик", salary=100000, status=Status.OPEN
    )


@pytest.fixture
def open_vacancy() -> Vacancy:
    return Vacancy(id=1, title="Python Разработчик", salary=100000, status=Status.OPEN)


@pytest.fixture
def closed_vacancy() -> Vacancy:
    return Vacancy(id=1, title="Python Разработчик", salary=100000, status=Status.CLOSED)

@pytest.fixture
def isolated_task_file(tmp_path) -> Path:
    tmp_task = tmp_path / "task.json"
    tmp_task.write_text('[{"id": "VID-000001", "title": "Test", "salary": 100, "status": "open"}]', encoding="utf-8")
    return tmp_task

@pytest.fixture
def database_session():
    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)
import pytest

from job_tracker.domain import Status, Vacancy
from job_tracker.schemas import ValidatedVacancy


@pytest.fixture
def valid_vacancy_model() -> ValidatedVacancy:
    return ValidatedVacancy(
        id="VID-000001", title="Python Разработчик", salary=100000, status=Status.OPEN
    )


@pytest.fixture
def open_vacancy() -> Vacancy:
    return Vacancy(id="VID-000001", title="Python Разработчик", salary=100000, status=Status.OPEN)


@pytest.fixture
def closed_vacancy() -> Vacancy:
    return Vacancy(id="VID-000001", title="Python Разработчик", salary=100000, status=Status.CLOSED)

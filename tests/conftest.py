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

@pytest.fixture
def isolated_task_file(tmp_path):
    tmp_task = tmp_path / "task.json"
    tmp_task.write_text('[{"id": "VID-000001", "title": "Test", "salary": 100, "status": "open"}]', encoding="utf-8")
    return tmp_task

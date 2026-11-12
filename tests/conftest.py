import pytest
from job_tracker.schemas import ValidatedVacancy
from job_tracker.domain import Vacancy, Status

@pytest.fixture
def valid_vacancy_model() -> ValidatedVacancy:
    return ValidatedVacancy(
        id="VID-000001",
        title="Python Developer",
        salary=100_000,
        status=Status.OPEN,
    )
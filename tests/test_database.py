import pytest
from sqlalchemy import select
from job_tracker.domain import Status

from job_tracker.db import VacancyRow, ApplicationRow


@pytest.mark.integration
def test_insert_vacancy(database_session):
    row = VacancyRow(id=1, title="Test Vacancy", salary=8888, status=Status.OPEN)
    database_session.add(row)
    database_session.commit()

    result = database_session.scalars(select(VacancyRow)).all()
    assert len(result) == 1
    assert result[0].title == "Test Vacancy"
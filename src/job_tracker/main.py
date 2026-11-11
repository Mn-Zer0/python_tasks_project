import sys
from pathlib import Path

from .domain import SourceError, VacancySource, Application, ApplicationStatus
from .sources import make_source
from .application import filter_records, is_rule


file = Path(__file__).parent / "task.json"


def main() -> None:
    source: VacancySource = make_source("json", file)

    try:
        vacancies = source.fetch()
    except SourceError as e:
        print(e)
        sys.exit(1)

    filtered = filter_records(vacancies, is_rule, key="status", value="open", limit=10)

    if filtered:
        for vacancy in filtered:
            print(vacancy.ID, vacancy.title, vacancy.salary, vacancy.status)
    else:
        print("Записи не найдены")

    app = Application(vacancy_id="VID-000001")
    app.move_to(ApplicationStatus.APPLIED)
    print(app.status)


if __name__ == "__main__":
    main()

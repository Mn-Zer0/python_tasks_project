import sys
from pathlib import Path

from .application import filter_records, is_rule
from .domain import Application, ApplicationStatus, SourceError, VacancySource
from .sources import make_source

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
            print(vacancy.id, vacancy.title, vacancy.salary, vacancy.status)
    else:
        print("Записи не найдены")

    app = Application(id="VID-000001")
    app.move_to(ApplicationStatus.APPLIED)
    print(app.status)


if __name__ == "__main__":
    main()

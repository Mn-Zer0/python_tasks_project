import sys
from pathlib import Path

from pydantic import ValidationError

from .application import filter_records, is_rule, to_vacancy
from .schemas import ValidatedVacancy
from .storage import read_json

file = Path(__file__).parent / "task.json"


def main():
    data = read_json(file)

    try:
        raw_vacancies = [ValidatedVacancy(**record) for record in data]
    except ValidationError as e:
        print(e)
        sys.exit(1)

    vacancies = [to_vacancy(i) for i in raw_vacancies]
    filtered = filter_records(vacancies, is_rule, key="status", value="open", limit=10)

    if filtered:
        for vacancy in filtered:
            print(vacancy.ID, vacancy.title, vacancy.salary, vacancy.status)
    else:
        print("Записи не найдены")


if __name__ == "__main__":
    main()

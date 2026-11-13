import typer
from typing import Annotated
from pathlib import Path
import json

from .sources import make_source
from .domain import Application, ApplicationStatus, TransitionError

app = typer.Typer(help="Трекер поиска работы")

file_cli = Path(__file__).parent / "cli.json"

def read_cli() -> dict[str, str]:
    with open(file_cli, "r", encoding="utf-8") as f:
        return json.load(f)

def write_cli(data: dict[str, str]) -> None:
    with open(file_cli, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4))


@app.command("list")
def get_list(
        file: Path = Path(__file__).parent / "task.json",
        limit: int = 10
):
    source = make_source("json", file)
    vacancies = source.fetch()

    for v in vacancies[:limit]:
        print(v)

@app.command("move")
def move_status(vacancy_id: str, new_status: ApplicationStatus):
    data = read_cli()

    current_status_str = data.get(vacancy_id, ApplicationStatus.SAVED.value)
    current_status = ApplicationStatus(current_status_str)

    status_app = Application(id=vacancy_id, status=current_status)

    try:
        status_app.move_to(new_status)

        data[vacancy_id] = status_app.status
        write_cli(data)

        print(f"Новый статус: {status_app.status}")
    except TransitionError as e:
        print(e)

@app.command("demo")
def demo():
    """Демонстрация полного сценария"""
    print("Запуск demo")

    # Загружаем фиксированные данные
    source = make_source("fixed")
    vacancies = source.fetch()
    print(f"1 загружено вакансий: {len(vacancies)}")

    # Берем первую вакансию
    vacancy = vacancies[0]
    print(f"2 выбрана вакансия: {vacancy.title}")

    # Создаем отклик в памяти
    status_app = Application(id=vacancy.id)
    print(f"3 создан отклик. Статус: {status_app.status}")

    # Делаем успешный переход
    status_app.move_to(ApplicationStatus.APPLIED)
    print(f"4 успешный переход. Новый статус: {status_app.status}")

    # Проверяем запрещенный переход
    print("5 попытка запрещенного перехода (APPLIED -> OFFER)...")
    try:
        status_app.move_to(ApplicationStatus.OFFER)
    except TransitionError as e:
        print(f"Ошибка: {e}")

    print("Конец demo")

if __name__ == "__main__":
    app()
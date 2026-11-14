import typer
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
import logging

from .sources import make_source
from .domain import Application, ApplicationStatus, TransitionError


app = typer.Typer(help="Трекер поиска работы")
console = Console()
err_console = Console(stderr=True)
log = logging.getLogger(__name__)

file_cli = Path(__file__).parent / "cli.json"


def read_cli() -> dict[str, str]:
    """Функция чтения cli.json"""
    with open(file_cli, "r", encoding="utf-8") as f:
        return json.load(f)

def write_cli(data: dict[str, str]) -> None:
    """Функция записи в cli.json"""
    with open(file_cli, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4))


@app.command("list")
def get_list(
        file: Path = Path(__file__).parent / "task.json",
        limit: int = 10,
        status: str | None = None
):
    """Функция, возврата списка вакансий в виде таблицы"""
    source = make_source("json", file)
    vacancies = source.fetch()

    if status:
        vacancies = [v for v in vacancies if v.status == status]

    vacancies = vacancies[:limit]

    saved_applications = read_cli()

    table = Table(title="Список вакансий")

    table.add_column("ID", style="blue")
    table.add_column("Название", style="purple")
    table.add_column("Зарплата", style="green")
    table.add_column("Статус вакансии")

    for v in vacancies:
        table.add_row(
            v.id,
            v.title,
            str(v.salary),
            v.status
        )

        # 6. Выводим на экран
    console.print(table)

@app.command("move")
def move_status(vacancy_id: str, new_status: ApplicationStatus):
    """Функция изменения статуса вакансии"""
    data = read_cli()

    current_status_str = data.get(vacancy_id, ApplicationStatus.SAVED.value)
    current_status = ApplicationStatus(current_status_str)

    status_app = Application(id=vacancy_id, status=current_status)

    try:
        status_app.move_to(new_status)

        data[vacancy_id] = status_app.status
        write_cli(data)

        log.info("Новый статус: %s", status_app.status)
    except TransitionError as e:
        err_console.print(e)
        raise typer.Exit(code=1)

@app.command("demo")
def demo():
    """Демонстрация полного сценария"""
    log.info("Запуск demo")

    # Загружаем фиксированные данные
    source = make_source("fixed")
    vacancies = source.fetch()
    log.info("1 загружено вакансий: %s", len(vacancies))

    # Берем первую вакансию
    vacancy = vacancies[0]
    log.info("2 выбрана вакансия: %s", vacancy.title)

    # Создаем отклик в памяти
    status_app = Application(id=vacancy.id)
    log.info("3 создан отклик. Статус: %s", status_app.status)

    # Делаем успешный переход
    status_app.move_to(ApplicationStatus.APPLIED)
    log.info("4 успешный переход. Новый статус: %s", status_app.status)

    # Проверяем запрещенный переход
    log.info("5 попытка запрещенного перехода (APPLIED -> OFFER)...")
    try:
        status_app.move_to(ApplicationStatus.OFFER)
    except TransitionError as e:
        err_console.print(e)
        raise typer.Exit(code=2)

    log.info("Конец demo")

if __name__ == "__main__":
    app()
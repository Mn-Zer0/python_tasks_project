import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
import logging

from .sources import make_vacancy_source, make_application_source, make_source_vacancy_writer, make_source_vacancy_reader
from .domain import Application, ApplicationStatus, TransitionError, Vacancy
from .storage import read_json

app = typer.Typer(help="Трекер поиска работы")
console = Console()
err_console = Console(stderr=True)
log = logging.getLogger(__name__)

file_cli = Path(__file__).parent / "cli.json"


@app.command("list_vacancies")
def get_list_vacancies(
        limit: int = 10,
        status: str | None = None
):
    """Функция, возврата списка вакансий в виде таблицы"""
    source = make_vacancy_source("db")
    vacancies = source.fetch()

    if status:
        vacancies = [v for v in vacancies if v.status == status]

    vacancies = vacancies[:limit]

    table = Table(title="Список вакансий")

    table.add_column("ID", style="blue")
    table.add_column("Название", style="purple")
    table.add_column("Зарплата", style="green")
    table.add_column("Статус вакансии")

    for v in vacancies:
        table.add_row(
            str(v.id),
            v.title,
            str(v.salary),
            v.status
        )

    console.print(table)

@app.command("list_applications")
def get_list_applications(
        limit: int = 10,
        status: str | None = None
):
    """Функция, возврата списка applications в виде таблицы"""
    source = make_application_source()
    applications = source.fetch()

    if status:
        applications = [a for a in applications if a.status == status]

    applications = applications[:limit]

    table = Table(title="Список вакансий")

    table.add_column("ID application", style="blue")
    table.add_column("ID вакансии", style="purple")
    table.add_column("Статус", style="green")

    for a in applications:
        table.add_row(
            str(a.id),
            str(a.vacancy_id),
            a.status
        )

    console.print(table)

@app.command("application_move")
def move_status(vacancy_id: int, new_status: ApplicationStatus):
    """Изменение статуса application"""
    source = make_application_source()

    status_app = source.get_by_id(vacancy_id)

    try:
        status_app.move_to(new_status)
        source.save(status_app)

        log.info("Новый статус: %s", status_app.status)
    except TransitionError as e:
        err_console.print(e)
        raise typer.Exit(code=1)

@app.command("seed_vacancies")
def seed_vacancies(file: Path):
    """Пополнение базы данных вакансий из json файла"""
    vacancies = read_json(file)

    writer = make_source_vacancy_writer()

    added = 0
    skipped = 0

    for v in vacancies:
        vacancy = Vacancy(
            id=v["id"],
            title=v["title"],
            salary=v["salary"],
            status=v["status"]
        )

        if writer.seed(vacancy):
            added += 1
        else:
            skipped += 1

    console.print(f"Добавлено: {added}, пропущено: {skipped}")

@app.command("read_vacancies")
def read_vacancies(
        sort_by: str = "id",
        order: str = "asc",
        limit: int = 10,
        offset: int = 0,
        status: str | None = None,
):
    """Получение списка вакансий по заданному фильтру"""
    vacancies = make_source_vacancy_reader().fetch(status, sort_by, order, limit, offset)

    table = Table(title="Список вакансий")

    table.add_column("ID", style="blue")
    table.add_column("Название", style="purple")
    table.add_column("Зарплата", style="green")
    table.add_column("Статус вакансии")

    for v in vacancies:
        table.add_row(
            str(v.id),
            v.title,
            str(v.salary),
            v.status
        )

    console.print(table)


if __name__ == "__main__":
    app()
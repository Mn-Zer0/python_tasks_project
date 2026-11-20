import json
from pathlib import Path


class StorageFormatError(Exception):
    """Кастомный Exception для read_json"""

    pass


def read_json(file: Path) -> list[dict]:
    """Фунция чтения json файла"""
    try:
        with open(file, encoding="UTF-8") as f:
            try:
                data: list[dict] = json.load(f)
            except json.decoder.JSONDecodeError as exception:
                raise StorageFormatError(
                    f"{file}: неверный JSON в строке {exception.lineno}, столбец {exception.colno}"
                ) from exception
    except FileNotFoundError as exception:
        raise StorageFormatError(f"Файл {file} не найден") from exception

    return data

from .domain import Vacancy
from .schemas import ValidatedVacancy


def to_vacancy(raw: ValidatedVacancy) -> Vacancy:
    """Преобразует валидированную внешнюю модель в доменную сущность"""
    return Vacancy(
        id=raw.id,
        title=raw.title,
        salary=raw.salary,
        status=raw.status,
    )


def filter_records(
    records: list[Vacancy], rule, *, key: str, value: str, limit=None
) -> list[Vacancy]:
    """Функция фильтрации вакансий по соответствию key: value"""
    # print(records)
    filtered = [record for record in records if rule(record, key, value)]
    if limit is None:
        return filtered
    else:
        return filtered[:limit]


def is_rule(record: Vacancy, key: str, value: str) -> bool:
    """Правило фильтрации, проверяет соответствует ли значение key входному value
    (вроде исправил)
    """
    attr = getattr(record, key)
    return bool(attr == value)

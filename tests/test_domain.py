import pytest
from pydantic import ValidationError
from job_tracker.schemas import ValidatedVacancy
from job_tracker.domain import Status, DomainError, Application, ApplicationStatus, TransitionError, Vacancy
from job_tracker.application import to_vacancy


# Тесты ValidatedVacancy (Pydantic модель)

def test_vacancy_salary():
    """Тест отрицательного salary"""
    with pytest.raises(ValidationError):
        ValidatedVacancy(id="VID-000001", title="X", salary=-100, status=Status.OPEN)

def test_vacancy_id():
    """Тест неправильного id (в данном случае недостаточной длины"""
    with pytest.raises(ValidationError):
        ValidatedVacancy(id="VID-00001", title="X", salary=100, status=Status.OPEN)

def test_vacancy_title():
    """Тест отсутствующего title"""
    with pytest.raises(ValidationError):
        ValidatedVacancy(id="VID-000001", title="", salary=100, status=Status.OPEN)

def test_vacancy_title_length():
    """Тест слишком длинного title"""
    with pytest.raises(ValidationError):
        ValidatedVacancy(id="VID-000001", title="a" * 201, salary=100, status=Status.OPEN)

def test_vacancy_status():
    """Тест неправильного status"""
    with pytest.raises(ValidationError):
        ValidatedVacancy(id="VID-000001", title="X", salary=100, status="opne")

def test_vacancy_types():
    """Тест соответствия типов (id, title, salary, status)"""
    v = ValidatedVacancy(id="VID-000001", title="title", salary=100, status="open")
    assert v.id == "VID-000001"
    assert v.title == "title"
    assert v.salary == 100
    assert v.status is Status.OPEN


# Тесты to_vacancy (преобразование ValidatedVacancy - pydantic модели в Vacancy)

def test_to_vacancy_id():
    """Тест соответствия ValidatedVacancy.id и Vacancy.id"""
    pydantic_model = ValidatedVacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    vacancy_model = to_vacancy(pydantic_model)
    assert pydantic_model.id == vacancy_model.id

def test_to_vacancy_title():
    """Тест соответствия ValidatedVacancy.title и Vacancy.title"""
    pydantic_model = ValidatedVacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    vacancy_model = to_vacancy(pydantic_model)
    assert pydantic_model.title == vacancy_model.title

def test_to_vacancy_salary():
    """Тест соответствия ValidatedVacancy.salary и Vacancy.salary"""
    pydantic_model = ValidatedVacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    vacancy_model = to_vacancy(pydantic_model)
    assert pydantic_model.salary == vacancy_model.salary

def test_to_vacancy_status():
    """Тест соответствия ValidatedVacancy.status и Vacancy.status"""
    pydantic_model = ValidatedVacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    vacancy_model = to_vacancy(pydantic_model)
    assert pydantic_model.status is vacancy_model.status


# Тесты Vacancy (close/open)

def test_vacancy_status_closed():
    """Проверка закрытия Vacancy"""
    v = Vacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    v.close()
    assert v.status is Status.CLOSED

def test_vacancy_status_open():
    """Проверка открытия Vacancy"""
    v = Vacancy(id="VID-000001", title="title", salary=100, status=Status.CLOSED)
    v.open()
    assert v.status is Status.OPEN

def test_vacancy_status_closed_to_closed():
    """Проверка закрытия Vacancy когда статус уже closed"""
    v = Vacancy(id="VID-000001", title="title", salary=100, status=Status.CLOSED)
    with pytest.raises(DomainError):
        v.close()
    assert v.status is Status.CLOSED

def test_vacancy_status_open_to_open():
    """Проверка открытия Vacancy когда статус уже open"""
    v = Vacancy(id="VID-000001", title="title", salary=100, status=Status.OPEN)
    with pytest.raises(DomainError):
        v.open()
    assert v.status is Status.OPEN


## Тесты таблицы переходов (Application)

# Допустимые переходы

@pytest.mark.parametrize(
    ("current", "new"),
    [
        (ApplicationStatus.SAVED, ApplicationStatus.APPLIED),
        (ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.APPLIED, ApplicationStatus.REJECTED),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED)
    ],
    ids=["saved-applied", "applied-interview", "applied-rejected", "interview-offer", "interview-rejected"],
)
def test_application_allowed(current, new):
    """Тестирование разрешенных переходов"""
    app = Application(id="VID-000001", status=current)
    app.move_to(new)
    assert app.status is new

# Недопустимые переходы и проверка сохранения их предыдущего допустимого состояния

@pytest.mark.parametrize(
    ("current", "new"),
    [
        (ApplicationStatus.SAVED, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.SAVED, ApplicationStatus.OFFER),
        (ApplicationStatus.SAVED, ApplicationStatus.REJECTED),

        (ApplicationStatus.APPLIED, ApplicationStatus.SAVED),
        (ApplicationStatus.APPLIED, ApplicationStatus.OFFER),

        (ApplicationStatus.INTERVIEW, ApplicationStatus.SAVED),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.APPLIED),

        (ApplicationStatus.OFFER, ApplicationStatus.SAVED),
        (ApplicationStatus.OFFER, ApplicationStatus.APPLIED),
        (ApplicationStatus.OFFER, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.OFFER, ApplicationStatus.REJECTED),

        (ApplicationStatus.REJECTED, ApplicationStatus.SAVED),
        (ApplicationStatus.REJECTED, ApplicationStatus.APPLIED),
        (ApplicationStatus.REJECTED, ApplicationStatus.INTERVIEW),
        (ApplicationStatus.REJECTED, ApplicationStatus.OFFER)
    ],
    ids=["saved-interview", "saved-offer", "saved-rejected",
         "applied-saved", "applied-offer",
         "interview-saved", "interview-applied",
         "offer-saved", "offer-applied", "offer-interview", "offer-rejected",
         "rejected-saved", "rejected-applied", "rejected-interview", "rejected-offer"
         ],
)
def test_application_forbidden(current, new):
    """Тестирование запрещенных переходов"""
    app = Application(id="VID-000001", status=current)
    with pytest.raises(TransitionError):
        app.move_to(new)
    assert app.status is current

# Переходы в текущее состояние
"""P.S. в данном случае не стал использовать @pytest.mark.parametrize 
мне показалось что это излишне для буквально 5 функций, да и в 
test_application_allowed я бы тоже убрал честно говоря, до этого читалось
как будто бы лучше, мне показалось pytest.mark.parametrize  - очень ситуативная вещь
"""

def test_application_saved_to_saved():
    """Проверка перехода сохранен -> сохранен"""
    app = Application(id="VID-000001", status=ApplicationStatus.SAVED)
    app.move_to(ApplicationStatus.SAVED)
    assert app.status is ApplicationStatus.SAVED

def test_application_applied_to_applied():
    """Проверка перехода откликнулся -> откликнулся"""
    app = Application(id="VID-000001", status=ApplicationStatus.APPLIED)
    app.move_to(ApplicationStatus.APPLIED)
    assert app.status is ApplicationStatus.APPLIED

def test_application_interview_to_interview():
    """Проверка перехода собеседование -> собеседование"""
    app = Application(id="VID-000001", status=ApplicationStatus.INTERVIEW)
    app.move_to(ApplicationStatus.INTERVIEW)
    assert app.status is ApplicationStatus.INTERVIEW

def test_application_offer_to_offer():
    """Проверка перехода оффер -> оффер"""
    app = Application(id="VID-000001", status=ApplicationStatus.OFFER)
    app.move_to(ApplicationStatus.OFFER)
    assert app.status is ApplicationStatus.OFFER

def test_application_rejected_to_rejected():
    """Проверка перехода отказ -> отказ"""
    app = Application(id="VID-000001", status=ApplicationStatus.REJECTED)
    app.move_to(ApplicationStatus.REJECTED)
    assert app.status is ApplicationStatus.REJECTED
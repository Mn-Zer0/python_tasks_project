import pytest

from job_tracker.sources import FixedSource, JsonFileSource, make_source

# Тестирование фабрики


def test_make_fixed_source():
    """Проверка make_source - FixedSource"""
    source = make_source("fixed")
    assert isinstance(source, FixedSource)


def test_make_json_file_source(tmp_path):
    """Проверка make_source - JsonFileSource"""
    file = tmp_path / "source.json"
    source = make_source("json", file)
    assert isinstance(source, JsonFileSource)


def test_make_without_path():
    """Проверка make_source JsonFileSource без указания файла"""
    with pytest.raises(ValueError):
        make_source("json")


def test_make_unknown_source():
    """Проверка make source указывая неизвестный источник"""
    with pytest.raises(ValueError):
        make_source("xml")

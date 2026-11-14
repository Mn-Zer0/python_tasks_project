from typer.testing import CliRunner
from job_tracker.cli import app

runner = CliRunner()

def test_list_returns_zero():
    """Тест команды list"""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Список вакансий" in result.stdout
    assert "VID-000001" in result.stdout

def test_move_success(isolated_task_file):
    """Тест команды move (позитивный)"""
    result = runner.invoke(app, ["list", "--file", str(isolated_task_file)])
    assert result.exit_code == 0

def test_move_forbidden_transition():
    """Тест команды move (негативный)"""
    runner.invoke(app, ["move", "VID-000001", "applied"])
    result = runner.invoke(app, ["move", "VID-000001", "saved"])
    assert result.exit_code == 1
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "dev-commander" / "scripts"
DIRS = ["journal", "plans", "increments", "reviews", "debug", "handoff"]


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True,
    )


def test_init_creates_workspace(tmp_path):
    result = run("init_workspace.py", tmp_path)
    assert result.returncode == 0, result.stderr
    ws = tmp_path / ".dev-commander"
    assert (ws / "project.md").is_file()
    for d in DIRS:
        assert (ws / d).is_dir(), f"missing {d}/"


def test_init_is_idempotent(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "project.md").write_text("edited\n")
    result = run("init_workspace.py", tmp_path)
    assert result.returncode == 0
    assert (tmp_path / ".dev-commander" / "project.md").read_text() == "edited\n"


def test_status_reports_counts(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "plans" / "0001-example.md").write_text("# plan\n")
    result = run("status.py", tmp_path)
    assert result.returncode == 0
    assert "plans: 1" in result.stdout


def test_status_fails_without_workspace(tmp_path):
    result = run("status.py", tmp_path)
    assert result.returncode == 1


def test_journal_appends_dated_entry(tmp_path):
    run("init_workspace.py", tmp_path)
    result = run("journal.py", tmp_path, "Chose pdm over poetry")
    assert result.returncode == 0
    entries = list((tmp_path / ".dev-commander" / "journal").glob("*.md"))
    assert len(entries) == 1
    assert "Chose pdm over poetry" in entries[0].read_text()


def test_next_recommends_plan_when_no_plans(tmp_path):
    run("init_workspace.py", tmp_path)
    result = run("next_step.py", tmp_path)
    assert result.returncode == 0
    assert "/dc:plan" in result.stdout


def test_next_recommends_implement_when_plan_exists(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "plans" / "0001-example.md").write_text("- [ ] Task 1\n")
    result = run("next_step.py", tmp_path)
    assert result.returncode == 0
    assert "/dc:implement" in result.stdout

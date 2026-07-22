import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "dev-commander" / "scripts"
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "handoff",
]


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


def test_status_counts_handoff_bundles(tmp_path):
    run("init_workspace.py", tmp_path)
    bundle = tmp_path / ".dev-commander" / "handoff" / "0001-example"
    bundle.mkdir()
    (bundle / "summary.md").write_text("# summary\n")
    result = run("status.py", tmp_path)
    assert "handoff: 1" in result.stdout


def _reviewed_plan(ws):
    (ws / "plans" / "0001-example.md").write_text("- [x] Task 1\n")
    (ws / "reviews" / "0001-example.md").write_text("approve\n")


def test_next_recommends_review_when_increments_done(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    (ws / "plans" / "0001-example.md").write_text("- [x] Task 1\n")
    result = run("next_step.py", tmp_path)
    assert result.returncode == 0
    assert "/dc:review" in result.stdout


def test_next_recommends_handoff_when_reviewed(tmp_path):
    run("init_workspace.py", tmp_path)
    _reviewed_plan(tmp_path / ".dev-commander")
    result = run("next_step.py", tmp_path)
    assert "/dc:handoff-to-tc" in result.stdout


def test_next_recommends_learn_after_handoff(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    result = run("next_step.py", tmp_path)
    assert "/dc:learn" in result.stdout


def test_next_recommends_release_when_cycle_complete(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    result = run("next_step.py", tmp_path)
    assert "Cycle complete" in result.stdout
    assert "/dc:release" in result.stdout

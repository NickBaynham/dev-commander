import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "dev-commander" / "scripts" / "bump_version.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True,
    )


def test_bumps_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0.1.0"\n')
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 0, result.stderr
    assert 'version = "0.2.0"' in (tmp_path / "pyproject.toml").read_text()


def test_bumps_package_json(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "x", "version": "0.1.0"}\n')
    result = run(tmp_path, "1.0.0")
    assert result.returncode == 0
    assert json.loads((tmp_path / "package.json").read_text())["version"] == "1.0.0"


def test_rejects_non_semver(tmp_path):
    (tmp_path / "pyproject.toml").write_text('version = "0.1.0"\n')
    result = run(tmp_path, "v2")
    assert result.returncode == 1


def test_fails_when_no_version_files(tmp_path):
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1


def test_bumps_project_section_not_first_version_line(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.other]\nversion = "9.9.9"\n\n[project]\nname = "x"\nversion = "0.1.0"\n'
    )
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 0, result.stderr
    text = (tmp_path / "pyproject.toml").read_text()
    assert '[tool.other]\nversion = "9.9.9"' in text
    assert 'version = "0.2.0"' in text


def test_reports_missing_project_version_field(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1
    assert "no project version field" in result.stdout


def test_invalid_package_json_fails_cleanly(tmp_path):
    (tmp_path / "package.json").write_text("{not json")
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1
    assert "not valid JSON" in result.stdout
    assert "Traceback" not in result.stderr

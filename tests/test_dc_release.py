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

"""Tests for the bootstrap.sh prerequisite verifier.

bootstrap.sh is idempotent verification only: it checks that the tools needed
to build and install Dev Commander are present and exits non-zero if any are
missing. It never installs anything.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = ROOT / "bootstrap.sh"


def run(required=None):
    env = dict(os.environ)
    if required is not None:
        env["DC_REQUIRED_COMMANDS"] = required
    return subprocess.run(
        ["sh", str(BOOTSTRAP)], capture_output=True, text=True, env=env,
    )


def test_bootstrap_is_a_posix_shell_script():
    assert BOOTSTRAP.is_file()
    assert BOOTSTRAP.read_text().startswith("#!/bin/sh")


def test_bootstrap_passes_when_required_command_is_present():
    # git is present wherever the suite runs; restrict the set to it so the
    # test does not depend on pdm/claude being installed.
    result = run(required="git")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "make install" in result.stdout


def test_bootstrap_reports_a_missing_command():
    result = run(required="dc_no_such_tool_zzz")
    assert result.returncode == 1
    assert "dc_no_such_tool_zzz" in result.stdout
    assert "missing" in result.stdout.lower()


def test_bootstrap_verifies_python_version():
    # python3 on PATH is 3.12+ in any environment that can run this suite
    # (the project requires it), so the python check reports ok with a version.
    result = run(required="python3")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "python3" in result.stdout

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "dev-commander"
DOCKER = PLUGIN / "templates" / "docker"

STACKS = ["python", "node-ts", "go"]


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_template_exists(stack):
    assert (DOCKER / stack / "Dockerfile.tmpl").is_file()


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_has_from_and_uses_project_name(stack):
    text = (DOCKER / stack / "Dockerfile.tmpl").read_text()
    assert "FROM " in text
    assert "{{project_name}}" in text

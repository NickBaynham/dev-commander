from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
CI = ROOT / "plugins" / "dev-commander" / "templates" / "ci" / "github"
SCAFFOLD = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"
STACKS = ["python", "node-ts", "go"]
DEP_SCANNER = {"python": "pip-audit", "node-ts": "npm audit", "go": "govulncheck"}


def _load(stack):
    text = (CI / stack / "ci.yml.tmpl").read_text().replace("{{project_name}}", "demo-app")
    return text, yaml.safe_load(text)


@pytest.mark.parametrize("stack", STACKS)
def test_ci_template_exists(stack):
    assert (CI / stack / "ci.yml.tmpl").is_file(), f"missing {stack} CI template"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_template_is_valid_yaml(stack):
    _text, doc = _load(stack)
    assert isinstance(doc, dict)


@pytest.mark.parametrize("stack", STACKS)
def test_ci_triggers_on_push_and_pull_request(stack):
    _text, doc = _load(stack)
    # PyYAML parses a bare `on:` key as the boolean True (YAML 1.1).
    triggers = doc.get("on", doc.get(True))
    assert "push" in triggers and "pull_request" in triggers


@pytest.mark.parametrize("stack", STACKS)
def test_ci_runs_uniform_make_targets(stack):
    text, _doc = _load(stack)
    for target in ["make install", "make lint", "make test", "make build"]:
        assert target in text, f"{stack} CI missing '{target}'"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_includes_dependency_and_secret_scanners(stack):
    text, _doc = _load(stack)
    assert DEP_SCANNER[stack] in text, f"{stack} CI missing {DEP_SCANNER[stack]}"
    assert "gitleaks" in text, f"{stack} CI missing gitleaks"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_make_targets_exist_in_scaffold(stack):
    text, _doc = _load(stack)
    makefile = (SCAFFOLD / stack / "Makefile.tmpl").read_text()
    for target in ["install", "lint", "test", "build"]:
        if f"make {target}" in text:
            assert f"{target}:" in makefile, (
                f"{stack} CI runs 'make {target}' but its Makefile.tmpl lacks it"
            )

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"

COMMON = ["README.md.tmpl", "CHANGELOG.md.tmpl", "TODO.md.tmpl"]

# Tasks 13-14 append entries as their stack families ship.
STACKS = {
    "python": [
        "Makefile.tmpl", "pyproject.toml.tmpl", "docker-compose.yml.tmpl",
        "tests/test_smoke.py.tmpl",
    ],
    "node-ts": [
        "Makefile.tmpl", "package.json.tmpl", "tsconfig.json.tmpl",
        "tsconfig.build.json.tmpl", "src/index.ts.tmpl", "tests/smoke.test.ts.tmpl",
    ],
    "go": [
        "Makefile.tmpl", "go.mod.tmpl", "main.go.tmpl", "main_test.go.tmpl",
    ],
}


def test_common_templates_exist():
    for name in COMMON:
        assert (SCAFFOLD / "common" / name).is_file(), f"missing common/{name}"


@pytest.mark.parametrize("stack", STACKS)
def test_stack_family_complete(stack):
    for name in STACKS[stack]:
        assert (SCAFFOLD / stack / name).is_file(), f"missing {stack}/{name}"


@pytest.mark.parametrize("stack", STACKS)
def test_stack_makefile_has_required_targets(stack):
    text = (SCAFFOLD / stack / "Makefile.tmpl").read_text()
    for target in ["install:", "lint:", "test:", "build:", "run:"]:
        assert target in text, f"{stack}/Makefile.tmpl missing {target}"


def test_scaffold_root_has_only_family_dirs():
    entries = {p.name for p in SCAFFOLD.iterdir() if p.is_dir()}
    assert entries == {"common"} | set(STACKS)


def test_python_pyproject_uses_pdm():
    assert "pdm" in (SCAFFOLD / "python" / "pyproject.toml.tmpl").read_text()


def test_templates_use_placeholders():
    assert "{{project_name}}" in (SCAFFOLD / "common" / "README.md.tmpl").read_text()


def test_skill_exists():
    skill = ROOT / "plugins" / "dev-commander" / "skills" / "dc-scaffold" / "SKILL.md"
    assert skill.is_file()
    assert "/dc:scaffold" in skill.read_text()

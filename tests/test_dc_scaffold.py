from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"
REQUIRED = [
    "Makefile.tmpl", "pyproject.toml.tmpl", "docker-compose.yml.tmpl",
    "README.md.tmpl", "CHANGELOG.md.tmpl", "TODO.md.tmpl",
]


def test_all_templates_exist():
    for name in REQUIRED:
        assert (TEMPLATES / name).is_file(), f"missing {name}"


def test_makefile_template_has_required_targets():
    text = (TEMPLATES / "Makefile.tmpl").read_text()
    for target in ["install:", "lint:", "test:", "build:", "run:"]:
        assert target in text, f"Makefile.tmpl missing {target}"


def test_pyproject_template_uses_pdm():
    text = (TEMPLATES / "pyproject.toml.tmpl").read_text()
    assert "pdm" in text


def test_templates_use_placeholders():
    text = (TEMPLATES / "README.md.tmpl").read_text()
    assert "{{project_name}}" in text


def test_skill_exists():
    skill = ROOT / "plugins" / "dev-commander" / "skills" / "dc-scaffold" / "SKILL.md"
    assert skill.is_file()
    assert "/dc:scaffold" in skill.read_text()

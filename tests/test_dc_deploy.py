from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "dev-commander"
DOCKER = PLUGIN / "templates" / "docker"
DEPLOY = PLUGIN / "templates" / "deploy"
IMAGE_REF = "ghcr.io/{{repo_owner}}/{{project_name}}"

STACKS = ["python", "node-ts", "go"]


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_template_exists(stack):
    assert (DOCKER / stack / "Dockerfile.tmpl").is_file()


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_has_from_and_uses_project_name(stack):
    text = (DOCKER / stack / "Dockerfile.tmpl").read_text()
    assert "FROM " in text
    assert "{{project_name}}" in text


def _render(path):
    return path.read_text().replace(
        "{{project_name}}", "demo-app"
    ).replace("{{repo_owner}}", "demo-owner")


def test_deploy_templates_exist():
    assert (DEPLOY / "docker-compose.prod.yml.tmpl").is_file()
    assert (DEPLOY / "release.yml.tmpl").is_file()


def test_compose_references_the_image():
    text = (DEPLOY / "docker-compose.prod.yml.tmpl").read_text()
    assert IMAGE_REF in text


def test_compose_is_valid_yaml():
    doc = yaml.safe_load(_render(DEPLOY / "docker-compose.prod.yml.tmpl"))
    assert "services" in doc


def test_release_workflow_references_the_image():
    text = (DEPLOY / "release.yml.tmpl").read_text()
    assert IMAGE_REF in text


def test_release_workflow_is_valid_yaml_and_triggers_on_tag():
    doc = yaml.safe_load(_render(DEPLOY / "release.yml.tmpl"))
    # PyYAML parses a bare `on:` key as the boolean True (YAML 1.1).
    triggers = doc.get("on", doc.get(True))
    assert "push" in triggers
    assert "tags" in triggers["push"]


def test_release_workflow_has_build_push_and_deploy():
    text = (DEPLOY / "release.yml.tmpl").read_text()
    assert "build-push-action" in text
    assert "ssh-action" in text


def test_compose_raw_template_is_valid_yaml():
    doc = yaml.safe_load((DEPLOY / "docker-compose.prod.yml.tmpl").read_text())
    assert "services" in doc


def test_release_raw_template_is_valid_yaml():
    doc = yaml.safe_load((DEPLOY / "release.yml.tmpl").read_text())
    assert "jobs" in doc


@pytest.mark.parametrize("name", ["docker-compose.prod.yml.tmpl", "release.yml.tmpl"])
def test_deploy_template_has_no_unsubstituted_placeholders(name):
    text = _render(DEPLOY / name)
    # Our mustache placeholders are {{project_name}} and {{repo_owner}};
    # GitHub Actions ${{ ... }} expressions are legitimate and must survive.
    assert "{{project_name}}" not in text
    assert "{{repo_owner}}" not in text

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "dev-commander" / "skills"

# Tasks 6-9 append one entry each as their skills ship, so make verify
# stays green between tasks.
EXPECTED = {
    "dc-plan": ["/dc:plan", "/dc:review-plan", "plans/"],
    "dc-implement": ["/dc:implement", "increments/", "failing test"],
    "dc-review": ["/dc:review", "reviews/", "rubric"],
    "dc-debug": ["/dc:debug", "debug/", "root cause"],
    "dc-design": ["/dc:design", "design/", "ADR"],
    "dc-handoff": ["/dc:handoff-to-tc", "handoff/", "learn-from"],
    "dc-release": ["/dc:release", "bump_version", "CHANGELOG"],
    "dc-branch": ["/dc:branch", "/dc:pr", "increment records"],
    "dc-learning": ["/dc:learn", "learning/", "candidate"],
}


@pytest.mark.parametrize("name", EXPECTED)
def test_skill_has_frontmatter_and_required_content(name):
    skill = SKILLS / name / "SKILL.md"
    assert skill.is_file(), f"missing {name}/SKILL.md"
    text = skill.read_text()
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert f"name: {name}" in front
    assert "description:" in front
    for marker in EXPECTED[name]:
        assert marker in text, f"{name}: missing '{marker}'"

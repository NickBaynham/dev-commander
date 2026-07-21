"""Verify every shipped SKILL.md has valid frontmatter and resolvable local links."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "dev-commander" / "skills"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def verify_skills(root: Path) -> list[str]:
    problems = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        text = skill_md.read_text()
        if not text.startswith("---\n"):
            problems.append(f"{skill_md}: missing frontmatter")
            continue
        front = text.split("---", 2)[1]
        fields = {
            m.group(1): m.group(2).strip()
            for m in re.finditer(r"^(name|description):\s*(.+)$", front, re.MULTILINE)
        }
        for field in ("name", "description"):
            if field not in fields:
                problems.append(f"{skill_md}: frontmatter missing {field}")
        name = skill_md.parent.name
        if fields.get("name", name) != name:
            problems.append(f"{skill_md}: frontmatter name != directory name {name}")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            if not (skill_md.parent / target.split("#")[0]).exists():
                problems.append(f"{skill_md}: broken link {target}")
    return problems


def main() -> int:
    problems = verify_skills(SKILLS) if SKILLS.is_dir() else []
    for p in problems:
        print(p)
    print(f"verify_skills: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

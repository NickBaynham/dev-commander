"""Bump the project version in pyproject.toml and package.json where present."""
import json
import re
import sys
from pathlib import Path


PROJECT_SECTION = re.compile(r"^\[project\]$\n(.*?)(?=^\[|\Z)", re.MULTILINE | re.DOTALL)


def bump(root: Path, version: str) -> list[str]:
    updated = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text()
        match = PROJECT_SECTION.search(text)
        if match:
            section, count = re.subn(
                r'^version = "[^"]+"', f'version = "{version}"',
                match.group(1), count=1, flags=re.MULTILINE,
            )
            if count:
                text = text[:match.start(1)] + section + text[match.end(1):]
                pyproject.write_text(text)
                updated.append("pyproject.toml")
            else:
                print("pyproject.toml has no project version field")
        else:
            print("pyproject.toml has no project version field")
    package = root / "package.json"
    if package.is_file():
        try:
            data = json.loads(package.read_text())
        except json.JSONDecodeError:
            print("package.json is not valid JSON")
        else:
            if "version" in data:
                data["version"] = version
                package.write_text(json.dumps(data, indent=2) + "\n")
                updated.append("package.json")
            else:
                print("package.json has no version field")
    return updated


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: bump_version.py <project-root> <version>")
        return 1
    root, version = Path(sys.argv[1]), sys.argv[2]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"not a semantic version: {version}")
        return 1
    no_candidates = not (root / "pyproject.toml").is_file() and not (root / "package.json").is_file()
    updated = bump(root, version)
    if not updated:
        if no_candidates:
            print("no version files found (pyproject.toml, package.json)")
        return 1
    for name in updated:
        print(f"updated {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Bump the project version in pyproject.toml and package.json where present."""
import json
import re
import sys
from pathlib import Path


def bump(root: Path, version: str) -> list[str]:
    updated = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text, count = re.subn(
            r'^version = "[^"]+"', f'version = "{version}"',
            pyproject.read_text(), count=1, flags=re.MULTILINE,
        )
        if count:
            pyproject.write_text(text)
            updated.append("pyproject.toml")
    package = root / "package.json"
    if package.is_file():
        data = json.loads(package.read_text())
        if "version" in data:
            data["version"] = version
            package.write_text(json.dumps(data, indent=2) + "\n")
            updated.append("package.json")
    return updated


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: bump_version.py <project-root> <version>")
        return 1
    root, version = Path(sys.argv[1]), sys.argv[2]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"not a semantic version: {version}")
        return 1
    updated = bump(root, version)
    if not updated:
        print("no version files found (pyproject.toml, package.json)")
        return 1
    for name in updated:
        print(f"updated {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

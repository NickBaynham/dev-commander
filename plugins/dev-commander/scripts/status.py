"""Summarize a .dev-commander/ workspace: artifact counts per directory."""
import sys
from pathlib import Path

DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff", "deployments",
]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = root / ".dev-commander"
    if not ws.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    print(f"workspace: {ws}")
    for d in DIRS:
        if d == "handoff":
            count = len([p for p in (ws / d).iterdir() if p.is_dir()])
        else:
            count = len([p for p in (ws / d).glob("*.md")])
        print(f"  {d}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

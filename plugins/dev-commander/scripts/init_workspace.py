"""Initialize a .dev-commander/ workspace. Idempotent: existing files are preserved."""
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "workspace"


def init_workspace(project_root: Path) -> Path:
    ws = project_root / ".dev-commander"
    for src in TEMPLATE.rglob("*"):
        dest = ws / src.relative_to(TEMPLATE)
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    return ws


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = init_workspace(root)
    print(f"workspace ready at {ws}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

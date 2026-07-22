"""Append a dated decision-journal entry to .dev-commander/journal/."""
import sys
from datetime import date
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: journal.py <project-root> <entry text>")
        return 1
    root, text = Path(sys.argv[1]), " ".join(sys.argv[2:])
    journal = root / ".dev-commander" / "journal"
    if not journal.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    today = date.today().isoformat()
    used = [
        int(p.stem.rsplit("-", 1)[-1])
        for p in journal.glob(f"{today}-*.md")
        if p.stem.rsplit("-", 1)[-1].isdigit()
    ]
    seq = (max(used) + 1) if used else 1
    entry = journal / f"{today}-{seq:02d}.md"
    entry.write_text(f"# {today} entry {seq:02d}\n\n{text}\n")
    print(f"journal entry written: {entry.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Recommend the next /dc: command from workspace state."""
import sys
from pathlib import Path


def recommend(ws: Path) -> str:
    plans = [p for p in (ws / "plans").glob("*.md")]
    if not plans:
        return "No plans yet. Run /dc:plan to produce an implementation plan."
    open_boxes = any("- [ ]" in p.read_text() for p in plans)
    if open_boxes:
        return "Open increments remain. Run /dc:implement to execute the next one."
    reviews = [p for p in (ws / "reviews").glob("*.md") if "plan-review" not in p.name]
    if len(reviews) < len(plans):
        return "All increments complete. Run /dc:review for a rubric-driven review."
    return "Reviewed and complete. Run /dc:handoff-to-tc to package for Test Commander."


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = root / ".dev-commander"
    if not ws.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    print(recommend(ws))
    return 0


if __name__ == "__main__":
    sys.exit(main())

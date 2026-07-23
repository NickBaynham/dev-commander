"""Recommend the next /dc: command from workspace state."""
import sys
from pathlib import Path


def recommend(ws: Path) -> str:
    plans = [p for p in (ws / "plans").glob("*.md")]
    if not plans:
        return ("No plans yet. Run /dc:plan to produce an implementation plan, "
                "or /dc:design first for architecturally significant work.")
    if any("- [ ]" in p.read_text() for p in plans):
        return ("Open increments remain. Run /dc:implement to execute the next one; "
                "use /dc:branch first to isolate the work on a feature branch.")
    reviews = [p for p in (ws / "reviews").glob("*.md") if "plan-review" not in p.name]
    if len(reviews) < len(plans):
        return "All increments complete. Run /dc:review for a rubric-driven review."
    if not [p for p in (ws / "handoff").iterdir() if p.is_dir()]:
        return ("Reviewed and complete. Run /dc:handoff-to-tc to package for Test "
                "Commander, or /dc:pr to open a pull request.")
    if not list((ws / "learning").glob("*.md")):
        return ("Handed off. Run /dc:learn to capture lessons from this cycle, "
                "then /dc:release to cut a version.")
    if not list((ws / "security").glob("*.md")):
        return ("Lessons captured. Run /dc:scan for a security scan (and "
                "/dc:ci to set up the CI pipeline) before cutting a release.")
    if not list((ws / "deployments").glob("*.md")):
        return ("Scanned. Run /dc:release to tag the version, then /dc:publish "
                "to build and push the image and /dc:deploy to ship it.")
    return ("Cycle complete. Run /dc:plan to start the next feature, or "
            "/dc:release for the next version.")


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

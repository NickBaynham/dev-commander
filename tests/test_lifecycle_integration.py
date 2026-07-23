"""End-to-end integration test for the Dev Commander workspace lifecycle.

Drives a temp workspace through init, plan, implement, review, handoff,
learn, and release using the real dc-core helper CLIs and the exact artifact
formats the Markdown skills (dc-plan, dc-implement, dc-review, dc-handoff,
dc-learning, dc-design) are specified to produce. This locks in the
cross-skill contract that individual unit tests only cover in isolation.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "dev-commander" / "scripts"
WORKSPACE_DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff", "deployments",
]


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True,
    )


def test_full_lifecycle(tmp_path):
    ws = tmp_path / ".dev-commander"

    # init: workspace and every directory exist, all artifact counts zero.
    assert run("init_workspace.py", tmp_path).returncode == 0
    assert (ws / "project.md").is_file()
    for d in WORKSPACE_DIRS:
        assert (ws / d).is_dir(), f"missing {d}/"
    status = run("status.py", tmp_path)
    assert status.returncode == 0
    for d in WORKSPACE_DIRS:
        assert f"{d}: 0" in status.stdout, f"{d} not zero at init"
    assert "/dc:plan" in run("next_step.py", tmp_path).stdout

    # design (optional, per DC8): a design doc must not derail the
    # plan-less recommendation.
    (ws / "design" / "0001-architecture.md").write_text("# Goal\n")
    assert "/dc:plan" in run("next_step.py", tmp_path).stdout
    assert "design: 1" in run("status.py", tmp_path).stdout

    # plan (dc-plan): an open increment checkbox routes to implement.
    (ws / "plans" / "0001-feature.md").write_text("- [ ] Increment 1\n")
    assert "/dc:implement" in run("next_step.py", tmp_path).stdout

    # implement (dc-implement): check off the box and record the increment.
    (ws / "plans" / "0001-feature.md").write_text("- [x] Increment 1\n")
    (ws / "increments" / "0001-feature-1.md").write_text("# built\n")
    assert "/dc:review" in run("next_step.py", tmp_path).stdout

    # a plan-review (from /dc:review-plan) must NOT satisfy the code-review
    # gate: the recommendation stays at /dc:review.
    (ws / "reviews" / "0001-plan-review-feature.md").write_text("ready\n")
    assert "/dc:review" in run("next_step.py", tmp_path).stdout

    # review (dc-review): a code review satisfies the gate; next is handoff.
    (ws / "reviews" / "0001-feature.md").write_text("approve\n")
    assert "/dc:handoff-to-tc" in run("next_step.py", tmp_path).stdout

    # handoff (dc-handoff): a bundle is a DIRECTORY, and status must count
    # it as one (regression guard: status.py once counted only *.md here).
    bundle = ws / "handoff" / "0001-feature"
    bundle.mkdir()
    (bundle / "summary.md").write_text("# summary\n")
    (bundle / "features.md").write_text("# features\n")
    (bundle / "acceptance-criteria.md").write_text("# criteria\n")
    assert "handoff: 1" in run("status.py", tmp_path).stdout
    assert "/dc:learn" in run("next_step.py", tmp_path).stdout

    # learn (dc-learning): a captured lesson leaves one hardening step.
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    assert "/dc:scan" in run("next_step.py", tmp_path).stdout

    # scan (dc-secscan): a security report leaves the ship step.
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    assert "/dc:publish" in run("next_step.py", tmp_path).stdout

    # ship (dc-publish + dc-deploy): a deployment record completes the cycle.
    (ws / "deployments" / "0001-ship.md").write_text("deployed\n")
    final = run("next_step.py", tmp_path)
    assert "Cycle complete" in final.stdout

    # journal (dc-core): an entry is written and counted.
    assert run("journal.py", tmp_path, "Shipped the feature").returncode == 0
    end = run("status.py", tmp_path)
    assert "journal: 1" in end.stdout
    assert "plans: 1" in end.stdout
    assert "increments: 1" in end.stdout
    # reviews counts both the code review and the plan-review file.
    assert "reviews: 2" in end.stdout
    assert "learning: 1" in end.stdout
    assert "security: 1" in end.stdout
    assert "deployments: 1" in end.stdout

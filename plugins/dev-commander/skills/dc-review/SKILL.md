---
name: dc-review
description: Rubric-driven code review for Dev Commander. Use when the user runs /dc:review or asks for a review of an increment, a diff, or recent changes. Produces a structured review report under .dev-commander/reviews/ with severity-rated findings and a verdict.
---

# dc-review

Reviews code against a fixed rubric so findings are consistent across
sessions. Reviews the most recent increment by default; the user may
name a diff, branch, or file set instead.

## /dc:review

1. Establish scope: the latest increment record in
   `.dev-commander/increments/`, or the diff the user names.
2. Review against the rubric. One finding per violation, each with
   file:line, severity (blocker, major, minor), evidence, and a
   concrete repair.

Rubric:
   - Correctness: does the code do what the increment record claims?
     Is every claim backed by a passing test?
   - Simplicity: no over-engineering, no defensive programming, no
     speculative abstractions. Exception handlers only where needed.
   - DRY: repeated logic factored into functions or methods.
   - Size: short modules, classes, and methods; focused files.
   - Clarity: clear names over comments; docstrings concise; no emojis.
   - Tests: behavior-focused, failing-first evidence recorded, no
     assertions weakened to force a pass.
3. Write the report to `.dev-commander/reviews/NNNN-<slug>.md`, where
   NNNN is the next zero-padded sequence number, with a verdict:
   approve, approve with repairs, or request changes.
4. Do not modify code during review. Repairs are applied by
   /dc:implement or by the user.

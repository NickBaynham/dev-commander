---
name: dc-implement
description: Test-first increment execution for Dev Commander. Use when the user runs /dc:implement or asks to execute the next increment of a plan under .dev-commander/plans/. Executes exactly one increment per invocation with a failing test written first, then stops for review.
---

# dc-implement

Executes one plan increment at a time. One invocation, one increment,
then stop. This keeps work incremental and reviewable.

## /dc:implement

1. Locate the active plan: the lowest-numbered file in
   `.dev-commander/plans/` that still contains a `- [ ]` checkbox. If
   the user names a plan, use that one.
2. Take the first unchecked increment. Do not skip ahead or batch.
3. Execute the increment test-first:
   - Write the failing test named by the increment; run it; confirm it
     fails for the expected reason before writing implementation code.
   - Write the minimal implementation; run the test; confirm it passes.
   - Run the project's full verify command (make verify, or make lint
     test when no verify target exists).
4. Record the increment at
   `.dev-commander/increments/NNNN-<slug>-<increment>.md`: what was
   built, test evidence (command and output summary), files touched,
   and any deviations from the plan with reasons.
5. Update the project's CHANGELOG.md, and TODO.md when scope changed.
6. Check off the increment's `- [ ]` box in the plan file.
7. Commit with the message given in the plan, then stop and report.
   The user decides whether to continue with the next increment.

If the increment cannot be completed as planned, stop, record the
blocker in the increment file, and recommend /dc:plan to revise the
plan. Never silently improvise a different design.

---
name: dc-plan
description: Implementation planning for Dev Commander. Use when the user runs /dc:plan or /dc:review-plan, or asks to turn requirements or a feature idea into a small-increment implementation plan. Produces plans under .dev-commander/plans/ where every increment is independently buildable, testable, and committable.
---

# dc-plan

Turns requirements into a small-increment implementation plan stored in
the workspace. Plans are the contract dc-implement executes.

## /dc:plan

1. Gather inputs: a feature request, user story, BRD, or reviewed
   requirements. If a business-requirements BRD exists, consume it
   rather than re-deriving requirements.
2. Write the plan to `.dev-commander/plans/NNNN-<slug>.md` where NNNN is
   the next zero-padded sequence number.
3. Plan format:
   - Header: Goal (one sentence), Architecture (2-3 sentences),
     Tech Stack, Global Constraints.
   - Increments as third-level headings, each with a `- [ ]` checkbox
     line, exact file paths, the failing test to write first, the
     minimal implementation, the verify command, and the commit message.
4. Increment rubric — every increment must be:
   - Small: one deliverable, one test cycle, roughly 2-5 minutes per step.
   - Independent: buildable and testable without later increments.
   - Test-first: names the failing test before the implementation.
   - Committed: ends with a commit.
5. No placeholders. "TBD", "add error handling", or steps without code
   are plan failures.

## /dc:review-plan

Review an existing plan file against the increment rubric above. Report
one finding per violated rubric item with the increment heading and a
concrete repair. Write the review to
`.dev-commander/reviews/NNNN-plan-review-<slug>.md` and give an overall
verdict: ready, ready with repairs, or not ready.

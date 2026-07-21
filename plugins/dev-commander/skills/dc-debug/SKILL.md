---
name: dc-debug
description: Root-cause-first debugging for Dev Commander. Use when the user runs /dc:debug or reports a bug, test failure, or unexpected behavior. Reproduces the problem, isolates it with a failing test, proves the root cause with evidence, fixes it, and records preventive documentation.
---

# dc-debug

A disciplined debugging workflow. The root cause is identified and
proven before any fix is written. Guesswork and workarounds are not
fixes.

## /dc:debug

1. Reproduce: run the failing scenario and capture the exact command
   and output. If it cannot be reproduced consistently, investigate
   until it can; do not proceed on an unreproduced bug.
2. Isolate: write the smallest failing test that captures the defect.
   This test is the proof of the problem and later the proof of the fix.
3. Diagnose: trace from symptom to cause with evidence (logs, values,
   bisection). State the root cause as a falsifiable claim and show the
   evidence that confirms it. Do not jump to conclusions.
4. Fix: make the minimal change that addresses the root cause. Run the
   isolating test (now passing) and the full suite.
5. Prevent: update documentation so the problem is not reintroduced —
   add preventive verbiage to the project's agent file or docs, and
   note the lesson in the workspace journal.
6. Record the investigation at `.dev-commander/debug/NNNN-<slug>.md`:
   symptom, reproduction, isolating test, root cause with evidence,
   fix, prevention.

Never fix before step 3 is complete. If pressed for a quick fix,
explain that an unproven fix is a guess and continue the workflow.

---
name: dc-handoff
description: Test Commander handoff for Dev Commander. Use when the user runs /dc:handoff-to-tc or asks to package what was built for testing. Assembles plans, increment records, and reviews into documents Test Commander's /tc:learn-from-docs and /tc:learn-from-specs commands can ingest.
---

# dc-handoff

Packages development artifacts into a bundle Test Commander can learn
from. Dev Commander never invokes Test Commander directly; it produces
documents and tells the user which /tc: commands to run next.

## /dc:handoff-to-tc

1. Establish scope: everything since the last handoff bundle, or the
   plan the user names.
2. Assemble the bundle at `.dev-commander/handoff/NNNN-<slug>/`:
   - `summary.md`: what was built and why, in plain prose; links to
     the source plans, increments, and reviews.
   - `features.md`: one section per shipped feature with entry points
     (commands, endpoints, or screens) and observable behavior.
   - `acceptance-criteria.md`: verifiable statements per feature,
     derived from the increment tests, written as behavior (given,
     when, then prose) rather than implementation detail.
3. Use universal software-engineering vocabulary; no internal jargon
   the testing side would need this conversation to decode.
4. Report the bundle path and recommend next steps: copy or point
   Test Commander at the bundle and run /tc:learn-from-docs, then
   /tc:learn-from-specs, in the consuming project.

---
name: dc-design
description: Architecture design and decision records for Dev Commander. Use when the user runs /dc:design or /dc:adr, or asks for a design document or an architecture decision record before planning a feature. Produces design docs and ADRs under .dev-commander/design/ that dc-plan consumes.
---

# dc-design

Fills the lifecycle phase between requirements and planning. Design is
optional per feature: small increments may go straight to /dc:plan;
features with architectural weight get a design doc or an ADR first.

## /dc:design

1. Gather inputs: the feature request, BRD, or user story, plus the
   parts of the codebase the feature touches.
2. Write a short design doc to `.dev-commander/design/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number, with sections:
   Goal (one sentence), Context, Approach (2-3 paragraphs),
   Alternatives considered with one-line reasons for rejection,
   Interfaces (exact names and types other components will consume),
   and Risks.
3. Keep it short. A design doc that exceeds two screens should be
   split or simplified before planning proceeds.
4. Recommend /dc:plan next, pointing it at the design doc.

## /dc:adr

Record one architecture decision at
`.dev-commander/design/adr-NNNN-<slug>.md`, where NNNN is the next
zero-padded sequence number, with sections: Status (proposed,
accepted, superseded), Context, Decision, Consequences. One decision
per record. ADRs are never deleted; a reversed decision gets a new
ADR that names and supersedes the old one.

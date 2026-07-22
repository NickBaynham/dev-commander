---
name: dc-learning
description: Governed lesson capture for Dev Commander. Use when the user runs /dc:learn or /dc:promote-lesson, or asks to record a lesson from a debugging session, review, or release. Captures candidate lessons under .dev-commander/learning/ and promotes them into project guidance only with human approval.
---

# dc-learning

The improvement loop. Lessons start as candidates and change project
guidance only when a human approves the promotion (DC10).

## /dc:learn

1. Capture one lesson at `.dev-commander/learning/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number, with sections:
   Status (candidate), Source (the debug report, review, or event
   that produced it), Lesson (one paragraph), and Proposed guidance
   (the exact wording that would be added to the project's agent
   file or docs if accepted).
2. Candidates change nothing by themselves. Do not edit any guidance
   file during capture.

## /dc:promote-lesson

1. Show the named candidate (or list all candidates if none named)
   and its proposed guidance to the user.
2. Only with the user's explicit approval: apply the proposed
   guidance edit, set the lesson's Status to accepted, and journal
   the promotion with the dc-core journal helper.
3. If the user declines, set Status to rejected and record their
   reason in the lesson file.

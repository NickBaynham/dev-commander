# The development lifecycle

Dev Commander models software development as a sequence of small, reviewable
steps, each owned by a skill and each leaving a durable artifact in the
`.dev-commander/` workspace. This guide explains how the pieces fit and how
`/dc:next` threads them together.

## Principles

- **Small increments.** Work advances one increment at a time, each built
  test-first and committed before the next begins.
- **Everything is an artifact.** Plans, reviews, design notes, security
  scans, and lessons are files in the workspace, committed alongside the
  code. Nothing important lives only in a conversation.
- **The plan is the source of truth.** When the plan and the code disagree,
  the plan is fixed first.
- **Human approval for outward and irreversible actions.** Dev Commander
  prepares branches, pull requests, releases, and guidance changes, but does
  not push, merge, or rewrite guidance without your direction.

## The phases

A feature moves through these phases. Design, CI, and the handoff/learn tail
are optional per feature; the core spine is plan → implement → review.

| Phase | Command(s) | Produces |
| --- | --- | --- |
| Design | `/dc:design`, `/dc:adr` | A design doc or ADR under `design/`. |
| Plan | `/dc:plan`, `/dc:review-plan` | A checkbox plan under `plans/`. |
| Branch | `/dc:branch` | A `dc/NNNN-<slug>` feature branch. |
| Implement | `/dc:implement` | An increment record under `increments/`; a checked-off plan box. |
| Review | `/dc:review` | A review report under `reviews/`. |
| Scan | `/dc:scan` | A security report under `security/`. |
| CI | `/dc:ci` | `.github/workflows/ci.yml`. |
| Pull request | `/dc:pr` | A drafted PR (pushed only on your approval). |
| Release | `/dc:release` | A version bump, changelog section, and tag. |
| Handoff | `/dc:handoff-to-tc` | A bundle under `handoff/` for Test Commander. |
| Learn | `/dc:learn`, `/dc:promote-lesson` | A candidate lesson under `learning/`. |

Debugging (`/dc:debug`) is not a phase but a workflow you invoke whenever a
bug appears: it reproduces the problem, isolates it with a failing test,
proves the root cause with evidence, fixes it, and records a prevention note
under `debug/`.

## How `/dc:next` decides

`/dc:next` reads only the workspace state — never git or the network — and
recommends the next command by walking these rules in order:

1. No plans yet → `/dc:plan` (or `/dc:design` first for weighty work).
2. Any plan has an open `- [ ]` increment → `/dc:implement` (with
   `/dc:branch` to isolate the work).
3. Fewer code reviews than plans → `/dc:review`.
4. No handoff bundle yet → `/dc:handoff-to-tc` or `/dc:pr`.
5. A bundle exists but no lessons captured → `/dc:learn`.
6. No security scan report yet → `/dc:scan` (and `/dc:ci` to set up the
   pipeline).
7. Otherwise the cycle is complete → `/dc:release`, or `/dc:plan` for the
   next feature.

Because the recommendation is derived from files on disk, it survives across
sessions and is always accurate to what has actually been done. `/dc:ci` is
advice rather than a gated step, because a generated workflow lives in
`.github/`, outside the workspace `/dc:next` reads.

## Where this sits

Dev Commander is the development-side counterpart to
[Test Commander](https://github.com/NickBaynham/test-commander), which owns
the testing lifecycle. `/dc:handoff-to-tc` is the bridge: it packages what
shipped into documents Test Commander's `/tc:learn-from-docs` and
`/tc:review-acceptance-criteria` commands can ingest. Dev Commander never
invokes Test Commander directly.

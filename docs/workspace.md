# Workspace reference

`/dc:init` creates a `.dev-commander/` directory in your project. It is
committed to git alongside the code it describes, so the project's plans,
reviews, and decisions travel with its history.

## Layout

```
.dev-commander/
├── project.md      # project identity, stack, and constraints
├── journal/        # dated decision-journal entries
├── plans/          # implementation plans from /dc:plan
├── increments/     # per-increment records from /dc:implement
├── reviews/        # plan and code review reports
├── debug/          # root-cause investigation reports from /dc:debug
├── design/         # design docs and ADRs from /dc:design
├── learning/       # candidate and promoted lessons from /dc:learn
├── security/       # security scan reports from /dc:scan
└── handoff/        # bundles for Test Commander from /dc:handoff-to-tc
```

`/dc:status` prints the artifact count in each of these directories.

## Directories

| Directory | Written by | Holds |
| --- | --- | --- |
| `journal/` | `/dc:journal`, and other commands that record decisions | Dated entries, `YYYY-MM-DD-NN.md`. |
| `plans/` | `/dc:plan` | Plans with `- [ ]` increment checkboxes. |
| `increments/` | `/dc:implement` | One record per executed increment, with test evidence. |
| `reviews/` | `/dc:review`, `/dc:review-plan` | Code reviews (`NNNN-<slug>.md`) and plan reviews (`NNNN-plan-review-<slug>.md`). |
| `debug/` | `/dc:debug` | Investigation reports: symptom, isolating test, root cause, fix, prevention. |
| `design/` | `/dc:design`, `/dc:adr` | Design docs (`NNNN-<slug>.md`) and ADRs (`adr-NNNN-<slug>.md`). |
| `learning/` | `/dc:learn`, `/dc:promote-lesson` | Lessons carrying a `Status:` line (candidate, accepted, rejected). |
| `security/` | `/dc:scan` | Scan reports listing findings by severity and a verdict. |
| `handoff/` | `/dc:handoff-to-tc` | Bundle directories (`NNNN-<slug>/`) for Test Commander. |

`project.md` is a single file at the workspace root describing the project's
identity, stack, and constraints.

## Naming conventions

- Most artifacts are named `NNNN-<slug>.md`, where `NNNN` is the next
  zero-padded sequence number in that artifact's series.
- Series are numbered independently. In `design/`, design docs and `adr-`
  records each count from one; in `reviews/`, plan reviews and code reviews
  each count from one, distinguished by the `plan-review` infix.
- Handoff artifacts are **directories** (`NNNN-<slug>/`), each holding
  `summary.md`, `features.md`, and `acceptance-criteria.md`.
- Journal entries are dated: `YYYY-MM-DD-NN.md`, numbered per day from the
  highest existing entry for that date.

## Lifecycle signal

`/dc:next` derives its recommendation entirely from what these directories
contain — an open checkbox in a plan, a handoff bundle without a lesson, a
missing security report. Because the signal is the files themselves, the
recommendation is correct across sessions without any hidden state. See
[the lifecycle guide](lifecycle.md).

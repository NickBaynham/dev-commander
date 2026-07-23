# Command reference

Every `/dc:*` command, grouped by the skill that owns it. Each skill's
`SKILL.md` under `plugins/dev-commander/skills/` is the authoritative
runtime spec; this reference summarizes it.

Artifacts follow one convention: `NNNN-<slug>.md`, where `NNNN` is the next
zero-padded sequence number in that artifact's series. Handoff bundles are
directories rather than single files.

## dc-core — workspace orchestration

| Command | Purpose |
| --- | --- |
| `/dc:init` | Create the `.dev-commander/` workspace from a bundled template. Idempotent; never overwrites existing files. |
| `/dc:status` | Print artifact counts for every workspace directory. |
| `/dc:journal` | Append a dated decision-journal entry under `journal/`. |
| `/dc:next` | Recommend the next command from workspace state. See [the lifecycle guide](lifecycle.md). |

These four are backed by small Python helpers bundled in the plugin; the
others below are Markdown skills that Claude performs directly.

## dc-scaffold — project scaffolding

| Command | Purpose |
| --- | --- |
| `/dc:scaffold` | Generate a new project for a chosen stack (`python`, `node-ts`, or `go`) with uniform Make targets, a smoke test, and standard docs. |

Reads templates from `templates/scaffold/common/` plus the chosen stack
directory; substitutes the project name and description; never overwrites an
existing file. A fresh scaffold passes `make lint test build` unedited.

## dc-design — architecture and decisions

| Command | Purpose |
| --- | --- |
| `/dc:design` | Write a short design doc under `design/`: goal, context, approach, alternatives, interfaces, risks. Input to `/dc:plan`. |
| `/dc:adr` | Record one architecture decision under `design/` (`adr-NNNN-<slug>.md`): status, context, decision, consequences. ADRs are never deleted; a reversal supersedes with a new ADR. |

The `adr-` series is numbered independently of the design-doc series.

## dc-plan — implementation planning

| Command | Purpose |
| --- | --- |
| `/dc:plan` | Turn requirements, a BRD, or a design doc into a plan under `plans/` whose increments are each buildable, testable, and committable. |
| `/dc:review-plan` | Review a plan against the increment rubric; write a `NNNN-plan-review-<slug>.md` report with a ready / ready-with-repairs / not-ready verdict. |

## dc-implement — test-first execution

| Command | Purpose |
| --- | --- |
| `/dc:implement` | Execute exactly one open increment from the active plan: failing test first, minimal implementation, verify, record under `increments/`, check off the plan box, commit, then stop for review. |

## dc-review — code review

| Command | Purpose |
| --- | --- |
| `/dc:review` | Rubric-driven review of the latest increment or a named diff. Write a `NNNN-<slug>.md` report under `reviews/` with severity-rated findings and an approve / approve-with-repairs / request-changes verdict. |

The code-review series is numbered independently of the plan-review series;
both share the `reviews/` directory, distinguished by the `plan-review`
infix.

## dc-debug — root-cause debugging

| Command | Purpose |
| --- | --- |
| `/dc:debug` | Reproduce a bug, isolate it with a failing test, prove the root cause with evidence, fix it, add a prevention note, and record the investigation under `debug/`. Never fixes before the cause is proven. |

## dc-branch — branch and pull request

| Command | Purpose |
| --- | --- |
| `/dc:branch` | Create and switch to a `dc/NNNN-<slug>` branch matching the plan's filename. |
| `/dc:pr` | Draft a pull-request description from the plan, increment records, and reviews. Pushes and opens the PR only after your explicit approval; never merges. |

## dc-secscan — security scanning

| Command | Purpose |
| --- | --- |
| `/dc:scan` | Run the stack's dependency scanner (`pip-audit` / `npm audit --audit-level=high` / `govulncheck`) plus `gitleaks detect`, and write a report under `security/`. Reports a missing scanner's install command and continues. Never auto-fixes. |

A high or critical dependency vulnerability, or any committed secret, is a
gating finding. Scanners without a severity threshold (pip-audit,
govulncheck) treat every known vulnerability as gating.

## dc-ci — CI pipeline generation

| Command | Purpose |
| --- | --- |
| `/dc:ci` | Generate `.github/workflows/ci.yml` from the stack's template: a GitHub Actions gate that runs `make install lint test build` and the security scan on push and pull request. Never overwrites an existing workflow. |

dc-ci embeds the dependency-scan commands dc-secscan documents; the secret
scan runs the official gitleaks GitHub Action (the same engine as the local
`gitleaks detect`).

## dc-release — release management

| Command | Purpose |
| --- | --- |
| `/dc:release` | From a clean, verified tree: bump the version across manifests with the `bump_version` helper, add a changelog section, verify, commit as `chore: release v<version>`, and create an annotated tag. Asks before pushing. |

## dc-learning — governed lesson capture

| Command | Purpose |
| --- | --- |
| `/dc:learn` | Capture a candidate lesson under `learning/` with a status, source, the lesson, and the exact proposed guidance edit. Changes no guidance file by itself. |
| `/dc:promote-lesson` | Show a candidate and, only with your approval, apply its proposed guidance edit and mark it accepted; otherwise record it rejected with a reason. |

## dc-handoff — Test Commander handoff

| Command | Purpose |
| --- | --- |
| `/dc:handoff-to-tc` | Assemble a bundle under `handoff/NNNN-<slug>/` (`summary.md`, `features.md`, `acceptance-criteria.md`) that Test Commander's `/tc:learn-from-docs` and `/tc:review-acceptance-criteria` can ingest. Produces documents only; never invokes Test Commander. |

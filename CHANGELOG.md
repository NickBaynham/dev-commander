# Changelog

## Phase 8 — dc-release skill

- dc-release skill: /dc:release command for version release workflow.
- Synchronizes version across pyproject.toml and package.json manifests.
- Helper bump_version.py validates semantic versions and reports updated files.
- Workflow: clean tree check, version determination, manifest sync, CHANGELOG update, verify, commit, tag, and journal.
- Prevents version drift across manifests.

## v0.1.0 release fixes

- Version bumped to 0.1.0 across manifests and pyproject.
- dc-handoff now recommends /tc:learn-from-docs and /tc:review-acceptance-criteria (learn-from-specs cannot ingest Markdown).
- status.py counts handoff bundles as directories.
- dc-scaffold ships a smoke test template so a fresh scaffold passes make test.
- Plan checkboxes checked off and Completed section populated.
- README install section no longer references the unshipped bootstrap.sh.

## v0.1 verification

- Validated the marketplace and plugin manifests with `claude plugin validate`.
- Ran `make install` end-to-end: pdm install, manifest validation, marketplace registration, and plugin install all succeeded; `dev-commander@dev-commander-marketplace` shows enabled in `claude plugin list`.
- Smoke-tested the workspace lifecycle in a scratch directory: init_workspace.py created `.dev-commander/` with six subdirectories, status.py reported all six at 0, next_step.py recommended `/dc:plan`.
- Updated the README status line to reflect Phases 0-7 complete.

## Phase 7 — dc-handoff skill

- dc-handoff skill: /dc:handoff-to-tc command for Test Commander handoff.
- Packages development artifacts into a bundle Test Commander can learn from.
- Assembles plans, increment records, and reviews at `.dev-commander/handoff/NNNN-<slug>/` with summary.md, features.md, and acceptance-criteria.md.
- Uses universal software-engineering vocabulary; no internal jargon.
- Reports bundle path and recommends next /tc: commands for the consuming project.

## Phase 6 — dc-debug skill

- dc-debug skill: /dc:debug command for root-cause-first debugging.
- Disciplined workflow: reproduce, isolate with failing test, diagnose with evidence, fix, prevent, record.
- Root cause is proven before any fix is written. Guesswork and workarounds are not accepted.
- Produces investigation report under .dev-commander/debug/NNNN-<slug>.md with full workflow documentation.

## Phase 5 — dc-review skill

- dc-review skill: /dc:review command for rubric-driven code review.
- Reviews code against fixed rubric: Correctness, Simplicity, DRY, Size, Clarity, Tests.
- Reviews most recent increment by default; user may name a diff, branch, or file set.
- Produces review report under .dev-commander/reviews/NNNN-<slug>.md with verdict.
- Findings include file:line, severity (blocker, major, minor), evidence, and repair guidance.

## Phase 4 — dc-implement skill

- dc-implement skill: /dc:implement command for test-first increment execution.
- Executes exactly one plan increment per invocation with failing test written first.
- Records increment under .dev-commander/increments/NNNN-<slug>-<increment>.md with test evidence.
- Checks off plan checkbox, updates CHANGELOG.md and TODO.md, commits, and stops for review.

## Phase 3 — dc-plan skill

- dc-plan skill: /dc:plan and /dc:review-plan commands for implementation planning.
- Plan format with Goal, Architecture, Tech Stack, Global Constraints, and increment rubric.
- Produces plans under .dev-commander/plans/NNNN-<slug>.md with independent, test-first increments.
- dc-review-plan reviews existing plans against the increment rubric.

## Phase 2 — dc-scaffold skill

- dc-scaffold skill: project scaffolding with six templates (Makefile, pyproject.toml, docker-compose.yml, README, CHANGELOG, TODO).
- Template placeholders for {{project_name}} and {{project_description}} with substitution instructions in SKILL.md.
- Five pytest tests verifying template presence, content, and skill integration.

## Phase 1 — dc-core skill

- dc-core skill: init, status, journal, next commands with Python helpers.
- Workspace template with project.md and six subdirectories (journal, plans, increments, reviews, debug, handoff).
- Helper scripts: init_workspace.py, status.py, journal.py, next_step.py.
- Seven integration tests covering workspace initialization, status reporting, journal entries, and recommendations.

## Phase 0 — Repo scaffold

- Repo scaffold: pyproject (pdm), Makefile, marketplace and plugin manifests,
  structure tests, README, TODO, agent orientation files.

# Changelog

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

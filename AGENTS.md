# Dev Commander — Agent Orientation

This file is for an agent (Claude, or any future operator) picking up Dev Commander work cold. Read it top-to-bottom once per session before reading anything else.

If you are the parent project's global agent and have already loaded `~/projects/CLAUDE.md`, this file extends and specializes those rules for the Dev Commander repo. The parent rules still apply: pdm as the Python package manager, no emojis anywhere, Make targets for setup/lint/test/build/run, small increments validated before moving on, root-cause-before-fix discipline, prove the problem with a failing test first.

## Project identity

Dev Commander is an AI-assisted software development agent, shipped as a Claude Code plugin. It provides a `/dc:*` command family that guides a project through the development lifecycle: workspace orchestration (dc-core), multi-stack project scaffolding for python, node-ts, and go (dc-scaffold), architecture design and ADRs (dc-design), small-increment planning (dc-plan), test-first implementation (dc-implement), rubric-driven review (dc-review), root-cause debugging (dc-debug), branch and PR workflow (dc-branch), release management (dc-release), governed lesson capture (dc-learning), security scanning (dc-secscan), CI pipeline generation (dc-ci), container publishing (dc-publish), multi-target deployment (dc-deploy), and handoff to Test Commander (dc-handoff). It is the development-side counterpart to [Test Commander](https://github.com/NickBaynham/test-commander) and deliberately mirrors its architecture.

## Source of truth

| Document | What it owns |
| --- | --- |
| [planning/plan.md](planning/plan.md) | **The authoritative spec and implementation plan.** Contains the Decisions (DC1-DC20), Global Constraints, File Structure, workspace layout, and the task-by-task implementation plan with checkbox tracking (v0.1 Tasks 1-10, v0.2 Tasks 11-18, v0.3 Tasks 19-24, v0.4 Tasks 25-31, and v0.5 Tasks 32-35 complete). **If the plan and the code disagree, fix the plan first, then the code.** |
| [CHANGELOG.md](CHANGELOG.md) | Phase-by-phase shipping log. Newest changes at the top within each phase section. |
| [TODO.md](TODO.md) | Features not yet added or under construction. |
| [README.md](README.md) | User-facing overview. Status line names the most recent completed phase. |
| [docs/](docs/README.md) | User guides: getting started, the development lifecycle, command reference, and workspace reference. |
| plugins/dev-commander/skills/ | Each shipped skill's SKILL.md is Claude's runtime entry point. |

**Start here every session:** open [planning/plan.md](planning/plan.md) and read (1) the Decisions table, (2) the Global Constraints, (3) the first task with unchecked `- [ ]` boxes — that is the current work item. Execute tasks in order; each task ends with tests passing and a commit.

## Working discipline

- Execute the plan one task at a time. Within a task, follow the steps in order: failing test first, run it to confirm the expected failure, minimal implementation, tests pass, commit.
- Check off plan checkboxes as steps complete. Update CHANGELOG.md and TODO.md in the same commit that ships a task.
- Run `make verify` (lint, tests, skill verifier) before every commit once Task 2 has shipped.
- Use the `claude` CLI for plugin operations (`claude plugin validate`, etc.), never interactive slash commands.
- Do not add features, files, or abstractions the current task does not call for. If the plan is wrong, fix the plan first.

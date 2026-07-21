# Dev Commander — Agent Orientation

This file is for an agent (Claude, or any future operator) picking up Dev Commander work cold. Read it top-to-bottom once per session before reading anything else.

If you are the parent project's global agent and have already loaded `~/projects/CLAUDE.md`, this file extends and specializes those rules for the Dev Commander repo. The parent rules still apply: pdm as the Python package manager, no emojis anywhere, Make targets for setup/lint/test/build/run, small increments validated before moving on, root-cause-before-fix discipline, prove the problem with a failing test first.

## Project identity

Dev Commander is an AI-assisted software development agent, shipped as a Claude Code plugin. It provides a `/dc:*` command family that guides a project through the development lifecycle: workspace orchestration (dc-core), project scaffolding (dc-scaffold), small-increment planning (dc-plan), test-first implementation (dc-implement), rubric-driven review (dc-review), root-cause debugging (dc-debug), and handoff to Test Commander (dc-handoff). It is the development-side counterpart to [Test Commander](https://github.com/NickBaynham/test-commander) and deliberately mirrors its architecture.

## Source of truth

| Document | What it owns |
| --- | --- |
| [planning/plan.md](planning/plan.md) | **The authoritative spec and implementation plan.** Contains the Decisions (DC1-DC5), Global Constraints, File Structure, workspace layout, and the task-by-task implementation plan with checkbox tracking. **If the plan and the code disagree, fix the plan first, then the code.** |
| [CHANGELOG.md](CHANGELOG.md) | Phase-by-phase shipping log. Newest changes at the top within each phase section. |
| [TODO.md](TODO.md) | Features not yet added or under construction. |
| [README.md](README.md) | User-facing overview. Status line names the most recent completed phase. |
| plugins/dev-commander/skills/ | Each shipped skill's SKILL.md is Claude's runtime entry point. |

**Start here every session:** open [planning/plan.md](planning/plan.md) and read (1) the Decisions table, (2) the Global Constraints, (3) the first task with unchecked `- [ ]` boxes — that is the current work item. Execute tasks in order; each task ends with tests passing and a commit.

## Working discipline

- Execute the plan one task at a time. Within a task, follow the steps in order: failing test first, run it to confirm the expected failure, minimal implementation, tests pass, commit.
- Check off plan checkboxes as steps complete. Update CHANGELOG.md and TODO.md in the same commit that ships a task.
- Run `make verify` (lint, tests, skill verifier) before every commit once Task 2 has shipped.
- Use the `claude` CLI for plugin operations (`claude plugin validate`, etc.), never interactive slash commands.
- Do not add features, files, or abstractions the current task does not call for. If the plan is wrong, fix the plan first.

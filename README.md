# Dev Commander

An AI-assisted software development agent, shipped as a Claude Code plugin.
Dev Commander guides a project through scaffold, plan, implement, review,
debug, and handoff to [Test Commander](https://github.com/NickBaynham/test-commander)
via a `/dc:*` command family.

Status: Phases 0-21 complete; v0.3.0 shipped.

## Install

    make install

## Commands

| Command | Skill | Purpose |
| --- | --- | --- |
| /dc:init | dc-core | Initialize the .dev-commander/ workspace |
| /dc:status | dc-core | Summarize workspace state |
| /dc:journal | dc-core | Append a decision-journal entry |
| /dc:next | dc-core | Recommend the next command |
| /dc:scaffold | dc-scaffold | Generate project scaffolding (python, node-ts, or go stack) |
| /dc:plan | dc-plan | Produce a small-increment implementation plan |
| /dc:review-plan | dc-plan | Review a plan against the increment rubric |
| /dc:implement | dc-implement | Execute the next plan increment test-first |
| /dc:review | dc-review | Rubric-driven code review of an increment or diff |
| /dc:debug | dc-debug | Root-cause-first debugging workflow |
| /dc:handoff-to-tc | dc-handoff | Package artifacts for Test Commander ingestion |
| /dc:release | dc-release | Bump version, update CHANGELOG, verify, commit, and tag a release |
| /dc:design | dc-design | Produce a design doc for a feature before planning |
| /dc:adr | dc-design | Record an architecture decision |
| /dc:branch | dc-branch | Create and switch to a feature branch for a plan |
| /dc:pr | dc-branch | Draft a pull request description from workspace artifacts |
| /dc:learn | dc-learning | Capture a candidate lesson from a debug session, review, or release |
| /dc:promote-lesson | dc-learning | Promote a candidate lesson into project guidance with approval |
| /dc:scan | dc-secscan | Run dependency and secret scans, report findings |
| /dc:ci | dc-ci | Generate a GitHub Actions PR gate |

## Development

    make lint    # ruff
    make test    # pytest
    make verify  # lint + test + skill verifier

Authoritative spec: [planning/plan.md](planning/plan.md).
Agent orientation: [AGENTS.md](AGENTS.md).

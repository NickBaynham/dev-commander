# Dev Commander

An AI-assisted software development agent, shipped as a Claude Code plugin.
Dev Commander guides a project through scaffold, plan, implement, review,
debug, and handoff to [Test Commander](https://github.com/NickBaynham/test-commander)
via a `/dc:*` command family.

Status: Phases 0-28 complete; [v0.4.0](https://github.com/NickBaynham/dev-commander/releases/latest) shipped.

## Install

    ./bootstrap.sh   # verify prerequisites (python3, pdm, git, claude)
    make install

`bootstrap.sh` only checks that the required tools are present; it never
installs anything. `make install` registers the local marketplace and
installs the plugin into Claude Code at user scope, so the `/dc:*` commands
are available in any project.

## Quick start

Run these `/dc:*` commands inside Claude Code, from the project you want
Dev Commander to drive.

1. **Initialize a workspace.** In your project, run `/dc:init`. It creates a
   committed `.dev-commander/` directory that tracks plans, reviews, design
   notes, security scans, and a decision journal.
2. **Starting fresh?** Run `/dc:scaffold` to generate a python, node-ts, or
   go project with Make targets (install, lint, test, build, run), a smoke
   test, and standard docs — a fresh scaffold passes `make lint test build`
   with no manual editing.
3. **Not sure what's next?** Run `/dc:next` at any point. It reads the
   workspace state and names the next command in the lifecycle.

A typical feature cycle, in order:

    /dc:design      # optional: a design doc or ADR for weighty work
    /dc:plan        # turn requirements into small, test-first increments
    /dc:branch      # isolate the work on a dc/NNNN-<slug> branch
    /dc:implement   # execute one increment at a time, failing test first
    /dc:review      # rubric-driven code review of the increment
    /dc:scan        # check dependencies and secrets before shipping
    /dc:ci          # generate a GitHub Actions PR gate
    /dc:pr          # draft a pull request from the workspace artifacts
    /dc:release     # bump the version, update CHANGELOG, tag
    /dc:handoff-to-tc  # package what shipped for Test Commander
    /dc:learn       # capture a lesson for next time

Every command writes its artifacts under `.dev-commander/`, and `/dc:next`
threads them together — you never have to remember the order.

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
| /dc:publish | dc-publish | Build and push a container image to GHCR |
| /dc:deploy | dc-deploy | Deploy the published image to a host over SSH |

## Development

    make lint    # ruff
    make test    # pytest
    make verify  # lint + test + skill verifier

## Documentation

Fuller guides live under [docs/](docs/README.md):
[getting started](docs/getting-started.md),
[the development lifecycle](docs/lifecycle.md),
[command reference](docs/commands.md), and
[workspace reference](docs/workspace.md).

Release history: [GitHub releases](https://github.com/NickBaynham/dev-commander/releases).
Authoritative spec: [planning/plan.md](planning/plan.md).
Agent orientation: [AGENTS.md](AGENTS.md).

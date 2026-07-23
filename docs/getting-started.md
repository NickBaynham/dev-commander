# Getting started

This guide installs Dev Commander and walks one feature from an empty
workspace to a tagged release.

## Prerequisites

- [Claude Code](https://claude.com/claude-code).
- Python 3.12 and [pdm](https://pdm-project.org) (for developing Dev
  Commander itself; a consuming project uses its own toolchain).
- Optional, for the security and CI commands: the stack's scanner
  (`pip-audit`, `npm audit`, or `govulncheck`) and `gitleaks`. `/dc:scan`
  reports the install command for anything missing and continues.

## Install

From a clone of this repository:

    make install

This validates the plugin manifests, registers the local marketplace, and
installs the plugin into Claude Code at user scope. The `/dc:*` commands are
then available in any project you open in Claude Code.

To confirm, open any project and run `/dc:init` — it should create a
`.dev-commander/` directory.

## Create a workspace

In the project you want Dev Commander to drive, run:

    /dc:init

This copies a template into `<project>/.dev-commander/`, a committed
directory that holds plans, reviews, design notes, security scans, and a
decision journal. `/dc:init` is idempotent — running it again never
overwrites your edits, so it also upgrades a workspace created by an older
version.

Commit the workspace. It is meant to live in your project's git history
alongside the code it describes.

## Scaffold a new project

Starting from nothing? Generate a project skeleton:

    /dc:scaffold

Dev Commander asks for a name, a one-line description, and a stack
(`python`, `node-ts`, or `go`), then writes a `Makefile` with uniform
targets (`install`, `lint`, `test`, `build`, `run`), a smoke test, and
standard docs (`README.md`, `CHANGELOG.md`, `TODO.md`). A fresh scaffold
passes `make lint test build` with no manual editing. It never overwrites an
existing file.

## Walk one feature

The commands below form a typical cycle. You do not have to memorize the
order — `/dc:next` reads the workspace and tells you what to run next at any
point. See [the lifecycle guide](lifecycle.md) for the reasoning.

1. **Design (optional).** For architecturally weighty work, capture a design
   doc or an architecture decision record:

       /dc:design
       /dc:adr

2. **Plan.** Turn requirements (or a design doc) into small, test-first
   increments:

       /dc:plan

   Each increment is independently buildable, testable, and committable.
   `/dc:review-plan` checks a plan against that rubric before you build.

3. **Branch.** Isolate the work:

       /dc:branch

   Creates a `dc/NNNN-<slug>` branch matching the plan's filename.

4. **Implement.** Execute one increment at a time, failing test first:

       /dc:implement

   One invocation does exactly one increment, then stops for review.

5. **Review.** Rubric-driven code review of the increment:

       /dc:review

6. **Scan.** Check dependencies and secrets before shipping:

       /dc:scan

7. **CI.** Generate a pull-request gate:

       /dc:ci

   Writes `.github/workflows/ci.yml` — a GitHub Actions workflow that runs
   the Make targets and the security scan on every push and pull request.

8. **Pull request.** Draft a PR from the workspace artifacts:

       /dc:pr

   Dev Commander never pushes or merges without your explicit direction.

9. **Release.** Bump the version, update the changelog, and tag:

       /dc:release

10. **Hand off and learn.** Package what shipped for
    [Test Commander](https://github.com/NickBaynham/test-commander), and
    capture a lesson for next time:

        /dc:handoff-to-tc
        /dc:learn

## Check state at any time

    /dc:status   # artifact counts per workspace directory
    /dc:next     # the recommended next command
    /dc:journal  # append a dated decision-journal entry

## Next

Read [the development lifecycle](lifecycle.md) to understand how these fit
together, or the [command reference](commands.md) for the details of each.

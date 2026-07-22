# Changelog

## scaffold health check covers build and run

- docs: the scaffold health check now proves `make lint test build`, not
  just `make lint test`, and exercises the run entrypoint the build
  produces. `make build` is the target that validates compilation and
  emits the run entrypoint, so lint+test alone missed the node-ts breakage
  the v0.2.0 whole-branch review caught (build emitted `dist/src/index.js`
  while `npm start` pointed at `dist/index.js`). `make run` itself is not
  executed in the check when it would block on a server or start external
  services (`docker compose up`); the built entrypoint is run directly
  instead. Updated dc-scaffold SKILL.md, the v0.2 health-check constraint,
  and the node-ts and go family proof steps.

## next_step lifecycle recommender

- feat: /dc:next now walks the full v0.2 lifecycle. The recommender was a
  v0.1 four-state chain (plan, implement, review, handoff) that could never
  surface the v0.2 skills. It now suggests /dc:design before planning when
  no plan exists, /dc:branch alongside /dc:implement, /dc:pr alongside
  /dc:handoff-to-tc, /dc:learn then /dc:release once a handoff bundle exists,
  and reports the cycle complete (offering /dc:release or a fresh /dc:plan)
  once lessons are captured. Reads only workspace state; the branch and pr
  suggestions are advice, not gates. Four new tests cover the added states.

## v0.2.0 release fixes

Whole-branch review of the v0.2.0 release surfaced three defects, fixed
here without changing the shipped version number.

- fix: node-ts scaffold build and run targets. `tsc` under the default
  tsconfig emitted `dist/src/index.js`, but `npm start` pointed at
  `dist/index.js`, so `make run` failed after a clean `make build`.
  Added `tsconfig.build.json.tmpl` (rootDir src, include src only) and
  pointed the build script at it so `make build && make run` works
  end to end.
- fix: bump_version.py anchors its pyproject.toml substitution to the
  `[project]` section instead of the first `version = "..."` line in
  the file, so a version line in an earlier table (e.g.
  `[tool.commitizen]`) is no longer bumped by mistake. Also reports a
  precise "no project version field" / "no version field" message
  instead of the generic "no version files found" when a file exists
  but lacks the field, and reports "package.json is not valid JSON"
  on a malformed file instead of crashing with a raw traceback.
- docs: v0.2 identity coherence. AGENTS.md, the plugin manifests, and
  README now name all eleven shipped skills; TODO.md's "planned" v0.2
  section (already shipped) is removed; dc-release's SKILL.md now
  tags releases with an annotated `git tag -a` and step 5 asks the
  releaser to confirm the project's identity prose names everything
  the release ships, so this class of drift is caught going forward.

## v0.2.0 — General software development agent

Generalizes Dev Commander from a Python-only inner loop into a general
software development agent: a release workflow, multi-stack scaffolding,
an architecture/design phase, a branch-and-PR workflow, and governed
lesson capture. Ships Phases 8-15 (Tasks 11-18).

- dc-release (Phase 8): /dc:release command and bump_version.py helper
  synchronize the version across manifests, update CHANGELOG.md, verify,
  commit, and tag.
- Multi-stack scaffolding (Phases 9-11): templates reorganized into
  common/ (stack-agnostic docs) plus python/, node-ts/, and go/ stack
  families under templates/scaffold/. Every family's Makefile provides
  install, lint, test, build, run; a fresh scaffold of any stack passes
  its own health check with zero manual editing.
- dc-design (Phase 12): /dc:design and /dc:adr commands produce design
  docs and architecture decision records under .dev-commander/design/
  as optional input to /dc:plan.
- dc-branch (Phase 13): /dc:branch and /dc:pr commands prepare feature
  branches (`dc/NNNN-<slug>`) and draft pull request descriptions from
  plan, increment, and review artifacts; never pushes or merges without
  explicit user direction.
- dc-learning (Phase 14): /dc:learn and /dc:promote-lesson commands
  capture candidate lessons under .dev-commander/learning/ and promote
  them into project guidance only with human approval.
- Workspace contract grown to nine parts: project.md plus journal/,
  plans/, increments/, reviews/, debug/, design/, learning/, handoff/.
- This release (Phase 15) dogfoods dc-release: version bumped to 0.2.0
  across pyproject.toml and both plugin manifests, README command table
  and status line updated, tagged v0.2.0.

## Phase 14 — dc-learning skill and learning workspace directory

- dc-learning skill: /dc:learn and /dc:promote-lesson commands for governed lesson capture.
- Lessons start as candidates under .dev-commander/learning/ and only modify project guidance with human approval (DC10).
- /dc:learn captures lesson from debugging session, review, or release with sections: Status (candidate), Source, Lesson, Proposed guidance.
- /dc:promote-lesson shows candidate and its proposed guidance; only with user approval applies the edit and promotes status to accepted.
- Workspace initialized with learning/ directory template.
- Updated DIRS constant in status.py and test_dc_core.py.

## Phase 13 — dc-branch skill and PR workflow

- dc-branch skill: /dc:branch and /dc:pr commands for team-development workflow.
- /dc:branch creates and switches to branches named `dc/NNNN-<slug>` matching plan filename.
- /dc:pr drafts pull request description from workspace artifacts (plan header, increment records, review reports).
- User approval required before pushing branch or opening PR (DC9).

## Phase 12 — dc-design skill and design workspace directory

- dc-design skill: /dc:design and /dc:adr commands for architecture design and decision records.
- Design is optional per feature; features with architectural weight get a design doc or ADR before planning.
- Design docs stored at .dev-commander/design/NNNN-<slug>.md with sections: Goal, Context, Approach, Alternatives, Interfaces, Risks.
- Architecture decision records stored at .dev-commander/design/adr-NNNN-<slug>.md with sections: Status, Context, Decision, Consequences.
- Workspace initialized with design/ directory template.
- Updated DIRS constant in status.py and test_dc_core.py.

## Phase 11 — go scaffold family

- Added go stack family with Go 1.23 toolchain.
- Template files: Makefile, go.mod, main.go, main_test.go.
- Updated test_dc_scaffold.py with parametrized go completeness tests.
- Fresh scaffolds pass go vet and go test without manual editing.

## Phase 10 — node-ts scaffold family

- Added node-ts stack family with TypeScript + vitest toolchain.
- Template files: Makefile, package.json, tsconfig.json, src/index.ts, tests/smoke.test.ts.
- Updated test_dc_scaffold.py with parametrized node-ts completeness tests.
- Fresh scaffolds pass npm install && make lint test without manual editing.

## Phase 9 — Multi-stack scaffold restructure

- Reorganized scaffold templates into stack families under templates/scaffold/.
- Introduced common/ subdirectory for stack-agnostic documentation (README, CHANGELOG, TODO).
- Moved python stack files (Makefile, pyproject.toml, docker-compose.yml, test_smoke.py.tmpl) into python/ subdirectory.
- Rewritten dc-scaffold SKILL.md to describe stack-family architecture and selection workflow.
- New test suite (test_dc_scaffold.py) with parametrized tests for each stack family, enabling Tasks 13-14 to append node-ts and go families.
- Updated v0.1 File Structure tree in planning/plan.md to document common/ and python/ layout.

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

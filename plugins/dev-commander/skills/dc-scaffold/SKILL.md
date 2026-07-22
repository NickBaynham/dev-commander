---
name: dc-scaffold
description: Project scaffolding for Dev Commander. Use when the user runs /dc:scaffold or asks to set up a new project. Offers stack families (e.g. python, node-ts, go) with a shared documentation set, generating a Makefile with install, lint, test, build, and run targets plus README, CHANGELOG, and TODO from bundled templates.
---

# dc-scaffold

Generates project scaffolding from templates bundled at
`<plugin-root>/templates/scaffold/`. Templates are organized as
`common/` (stack-agnostic docs) plus one directory per stack family.

## /dc:scaffold

1. Ask for the project name, a one-line description, and the stack if
   not provided. The name must be lowercase with hyphens. The
   available stacks are the subdirectories of `templates/scaffold/`
   other than `common`.
2. Write every template under `templates/scaffold/common/` and under
   the chosen stack's directory into the project at the same relative
   path with `.tmpl` stripped from the filename, substituting
   `{{project_name}}` and `{{project_description}}`.
3. Never overwrite an existing file. If a target exists, report it and
   skip it. List skipped files at the end.
4. Only include docker-compose.yml when the project needs local
   services; ask if unclear. Databases and system tools always run on
   docker locally. When skipping docker-compose.yml, also remove any
   `docker compose up -d` line from the generated Makefile's run
   target so `make run` still works.
5. Prove the scaffold is healthy before journaling: run the stack's
   install target, then `make lint test build` with zero manual
   editing. Where the build produces a run entrypoint (for example
   node-ts's `dist/index.js` or go's `bin/<name>`), confirm the run
   target points at it — run `make run` when it self-terminates, or
   run the built entrypoint directly when `make run` would block on a
   server or start external services (`docker compose up`). Then
   journal the scaffold decision with the dc-core journal helper.

Rules the generated project must satisfy regardless of stack: Make
targets for install, lint, test, build, run; no emojis anywhere;
README under 400 lines linking to CHANGELOG.md and TODO.md.

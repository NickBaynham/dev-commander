---
name: dc-scaffold
description: Project scaffolding for Dev Commander. Use when the user runs /dc:scaffold or asks to set up a new project with pdm, Make targets, docker compose, and standard documentation files. Generates Makefile, pyproject.toml, docker-compose.yml, README, CHANGELOG, and TODO from bundled templates.
---

# dc-scaffold

Generates standard project scaffolding from templates bundled at
`<plugin-root>/templates/scaffold/`.

## /dc:scaffold

1. Ask for project name and one-line description if not provided.
   The name must be a valid Python distribution name (lowercase, hyphens).
2. Read each template under `templates/scaffold/` (including
   subdirectories) and write it into the project at the same relative
   path with `.tmpl` stripped from the filename, substituting
   `{{project_name}}` and `{{project_description}}`.
3. Never overwrite an existing file. If a target exists, report it and
   skip it. List skipped files at the end.
4. Only include docker-compose.yml when the project needs local services;
   ask if unclear. Databases and system tools always run on docker locally.
   When skipping docker-compose.yml, also remove the `docker compose up -d`
   line from the generated Makefile's run target so `make run` still works.
5. After writing, run `pdm install` and `make lint test` to prove the
   scaffold is healthy, then journal the scaffold decision with the
   dc-core journal helper.

Rules the generated project must satisfy: pdm as package manager, Make
targets for install, lint, test, build, run; no emojis anywhere; README
under 400 lines linking to CHANGELOG.md and TODO.md.

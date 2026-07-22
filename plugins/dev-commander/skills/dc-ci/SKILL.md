---
name: dc-ci
description: CI pipeline generation for Dev Commander. Use when the user runs /dc:ci or asks to set up continuous integration. Generates a GitHub Actions workflow that runs the scaffold's Make targets and a security scan on push and pull request.
---

# dc-ci

Generates a GitHub Actions workflow that gates pull requests: it runs the
project's uniform Make targets and the dc-secscan security scan. GitHub
Actions is the only provider in v0.3.

## Stack detection

Infer the stack from project files: `pyproject.toml` present means python,
`package.json` means node-ts, `go.mod` means go. If none or more than one
is present, ask the user which stack rather than guessing.

## /dc:ci

1. Detect the stack.
2. Read `templates/ci/github/<stack>/ci.yml.tmpl` relative to this plugin's
   root (resolve the path relative to this SKILL.md's own location, as
   dc-core describes), substitute `{{project_name}}`, and write it to
   `.github/workflows/ci.yml` in the project.
3. Never overwrite an existing `.github/workflows/ci.yml`. If one exists,
   report it and stop.
4. The workflow triggers on push and pull request and runs, in order:
   checkout, the stack's language setup, `make install`, `make lint`,
   `make test`, `make build`, then the dc-secscan scan steps. lint, test,
   and build must pass; the scan fails the build on a gating finding.
5. Report the path written and recommend running /dc:scan locally to see
   findings before relying on the gate.

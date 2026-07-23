---
name: dc-publish
description: Container image publishing for Dev Commander. Use when the user runs /dc:publish or asks to build and push a container image for a release. Generates a Dockerfile if the project lacks one, builds the image, and pushes it to GHCR. It supplies the build-and-push step the release workflow embeds.
---

# dc-publish

Builds a container image for the project and pushes it to GHCR. The image
is the deployment artifact dc-deploy ships. dc-publish is the single source
of truth for the image reference and the build and push commands.

## Stack detection

Infer the stack from project files: `pyproject.toml` present means python,
`package.json` means node-ts, `go.mod` means go. If none or more than one
is present, ask the user which stack rather than guessing.

## The image reference

The image is `ghcr.io/<owner>/<project>`, where `<owner>` is the GitHub
owner from the git remote and `<project>` is the project name. It is tagged
`:latest` and `:<version>`, where `<version>` is the project's current
version from its manifest (for example `pyproject.toml`), matching the tag
dc-release cut.

## /dc:publish

1. Detect the stack.
2. Ensure a Dockerfile exists. If none, generate one from
   `templates/docker/<stack>/Dockerfile.tmpl` (relative to this plugin's
   root, resolved as dc-core describes), substituting `{{project_name}}`.
   Never overwrite an existing Dockerfile.
3. Build the image and tag it `ghcr.io/<owner>/<project>:<version>` and
   `:latest`.
4. Push both tags to GHCR. Registry authentication comes from the
   environment: `docker login ghcr.io` locally, or `GITHUB_TOKEN` in CI.
   Never store or print a credential.
5. Publishing assumes a clean, released tree; publish the version
   dc-release tagged.
6. Write a publish record to `.dev-commander/deployments/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number: the image reference
   and tags pushed, and the outcome.
7. If docker or git is not available, report the missing tool and stop;
   never crash.

---
name: dc-deploy
description: Deployment for Dev Commander. Use when the user runs /dc:deploy or asks to ship the published image. Deploys the image dc-publish pushed to a chosen target (a self-hosted host over SSH, or Fly.io), selected by a target key in project.md. It never embeds secrets and never guesses the target.
---

# dc-deploy

Deploys the published container image to a chosen target. It ships the image
dc-publish pushed; it does not build one. Targets live under
`templates/deploy/<target>/`; v0.5 supports `ssh` (a self-hosted Linux host
running docker compose) and `fly` (Fly.io).

## Selecting the target

Read `target:` from the Deployment section of the workspace `project.md`
(`ssh` or `fly`). If it is not set there, ask the user which target and offer
to record it in `project.md`. Never guess. An unsupported value is reported
against the supported set (`ssh`, `fly`); stop rather than proceed.

## /dc:deploy

1. Select the target (above).
2. Generate the target's config if absent, from `templates/deploy/<target>/`
   relative to this plugin's root (resolved as dc-core describes),
   substituting `{{project_name}}` and `{{repo_owner}}` (the GitHub owner
   from the git remote). Never overwrite an existing file.
   - ssh: `docker-compose.prod.yml` from
     `templates/deploy/ssh/docker-compose.prod.yml.tmpl`.
   - fly: `fly.toml` from `templates/deploy/fly/fly.toml.tmpl`.
3. Deploy via the target's mechanism:
   - ssh: read the host and SSH user from the Deployment section (ask and
     record if absent); over SSH, ensure the compose file is on the host,
     then run `docker compose -f docker-compose.prod.yml pull` and
     `docker compose -f docker-compose.prod.yml up -d`.
   - fly: `flyctl deploy --app <project> --image
     ghcr.io/<owner>/<project>:<version>`.
4. Credentials come from the environment locally, or GitHub Actions secrets
   in CI — ssh: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`; fly:
   `FLY_API_TOKEN`. Reference them; never embed or store a secret.
5. Write a deploy record to `.dev-commander/deployments/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number: the target, the image
   deployed, and the outcome.
6. To automate the ship on a version tag, generate
   `.github/workflows/release.yml` from
   `templates/deploy/<target>/release.yml.tmpl` (never overwriting). It
   builds and pushes the image (dc-publish's step) and deploys to the target
   on a `v*` tag. Run /dc:publish first (or ensure a Dockerfile exists) so
   the tag-triggered build has a Dockerfile.
7. If a required tool is missing (docker or ssh for the ssh target, flyctl
   for the fly target), report it and stop; never crash.

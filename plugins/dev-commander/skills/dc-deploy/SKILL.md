---
name: dc-deploy
description: Self-hosted deployment for Dev Commander. Use when the user runs /dc:deploy or asks to ship the published image to a server. Deploys the image dc-publish pushed to a Linux host over SSH with docker compose. It never embeds secrets and never guesses the host.
---

# dc-deploy

Deploys the published container image to a self-hosted Linux host running
docker compose over SSH. It ships the image dc-publish pushed; it does not
build one.

## /dc:deploy

1. Ensure `docker-compose.prod.yml` exists. If none, generate it from
   `templates/deploy/docker-compose.prod.yml.tmpl` (relative to this
   plugin's root, resolved as dc-core describes), substituting
   `{{project_name}}` and `{{repo_owner}}` (the GitHub owner from the git
   remote), so it references `ghcr.io/<owner>/<project>:latest`. Never
   overwrite an existing file.
2. Establish the target: read the host and SSH user from a Deployment
   section in the workspace `project.md`. If the host is not configured
   there, ask the user and offer to record it in `project.md`. Never guess.
3. Deploy: over SSH, ensure the compose file is present on the host, then
   run `docker compose -f docker-compose.prod.yml pull` and
   `docker compose -f docker-compose.prod.yml up -d`.
4. SSH credentials and registry auth come from the environment locally, or
   GitHub Actions secrets (`DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`)
   in CI. Reference them; never embed or store a secret.
5. Write a deploy record to `.dev-commander/deployments/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number: the image deployed
   and the host it went to, and the outcome.
6. To automate the ship on a version tag, generate
   `.github/workflows/release.yml` from
   `templates/deploy/release.yml.tmpl` (relative to this plugin's root,
   resolved as dc-core describes), substituting `{{project_name}}` and
   `{{repo_owner}}` (the GitHub owner from the git remote). Never
   overwrite an existing `.github/workflows/release.yml`. The workflow
   builds and pushes the image (dc-publish's step) and runs this deploy
   step on a `v*` tag; the deploy secrets DEPLOY_HOST, DEPLOY_USER, and
   DEPLOY_SSH_KEY come from the repository's GitHub Actions secrets.
7. If docker, git, or ssh is not available, report the missing tool and
   stop; never crash.

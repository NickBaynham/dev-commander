# To Do

## v0.5 (planned — see planning/plan.md, Tasks 32-35)

- Phase 29: restructure the SSH deploy templates into templates/deploy/ssh/.
- Phase 30: Fly.io deploy target (fly.toml + release workflow).
- Phase 31: generalize dc-deploy to select a target (ssh or fly) from project.md.
- Phase 32: v0.5 release.

## Later

- Registries beyond GHCR (Docker Hub, ECR, GAR) as a registry option.
- Kubernetes as a further deploy target (manifests + kubectl).
- Language-native package publishing (PyPI, npm).
- Harden the node-ts Dockerfile to a multi-stage build (drop devDependencies from the final image).

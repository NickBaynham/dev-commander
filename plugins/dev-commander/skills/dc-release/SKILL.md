---
name: dc-release
description: Release workflow for Dev Commander. Use when the user runs /dc:release or asks to cut a version, bump version numbers, tag a release, or write release notes. Synchronizes the version across manifests with the bump_version helper, adds a CHANGELOG release section, verifies, commits, and tags.
---

# dc-release

Closes the lifecycle: takes a verified working tree to a tagged,
documented release. Version drift across manifests is the failure this
skill exists to prevent.

The helper lives at `scripts/bump_version.py` relative to this plugin's
root; resolve the path relative to this SKILL.md's own location, as
described in dc-core.

## /dc:release

1. Confirm the working tree is clean and the project's verify command
   passes (make verify, or make lint test when no verify target
   exists). A release never starts from a dirty or failing tree.
2. Determine the new semantic version with the user (MAJOR.MINOR.PATCH).
3. Run the bump helper:

   `python3 <plugin-root>/scripts/bump_version.py <project-root> <version>`

   It updates pyproject.toml and package.json where present. Then ask
   the user about any additional files that carry the version (plugin
   manifests, docs, install scripts) and update those to match. Every
   statement of the version in the repo must agree.
4. Add a `## v<version>` section at the top of CHANGELOG.md
   summarizing what shipped since the previous release.
5. Update the README status line if it names a version. Confirm the
   project's identity prose (agent orientation file and any plugin or
   package manifests) names everything this release ships.
6. Re-run the verify command, then commit as
   `chore: release v<version>` and create an annotated tag:
   `git tag -a v<version> -m "release v<version>"`. Note that
   `git push --follow-tags` only pushes annotated tags; push the tag
   explicitly if in doubt.
7. Ask before pushing; pushing the commit and tag is the user's call.
8. Journal the release with the dc-core journal helper.

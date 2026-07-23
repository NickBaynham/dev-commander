---
name: dc-core
description: Core Dev Commander orchestration commands. Use when the user runs /dc:init, /dc:status, /dc:journal, or /dc:next, or asks about the current state of a Dev Commander workspace. Owns the four commands that initialize the .dev-commander/ workspace, summarize its state, append journal entries, and recommend the next command.
---

# dc-core

The umbrella skill for Dev Commander. Owns the four orchestration commands
that act on the workspace itself. Each command is implemented as a Python
helper bundled inside the plugin. When the user invokes one of these slash
commands, run the corresponding helper with Bash and report the output.

## Finding the helpers

Helpers live at `scripts/<name>.py` relative to this plugin's root (this
SKILL.md is at `<plugin-root>/skills/dc-core/`). In a development checkout
that is `<repo>/plugins/dev-commander/scripts/`; in the installed cache it
is `~/.claude/plugins/cache/dev-commander-marketplace/dev-commander/<version>/scripts/`.
Resolve the path relative to this file's own location.

## Commands

### /dc:init

Initialize a workspace in the user's current project. Copies the bundled
template into `<project-root>/.dev-commander/`. Idempotent; existing files
are preserved.

Run: `python3 <plugin-root>/scripts/init_workspace.py <project-root>`

`<project-root>` defaults to the current working directory.

### /dc:status

Summarize the workspace: artifact counts for journal, plans, increments,
reviews, debug, design, learning, security, and handoff.

Run: `python3 <plugin-root>/scripts/status.py <project-root>`

### /dc:journal

Append a dated decision-journal entry. Ask the user for the entry text if
they did not provide it.

Run: `python3 <plugin-root>/scripts/journal.py <project-root> <entry text>`

### /dc:next

Recommend the next command from workspace state, walking the full lifecycle:
no plans means /dc:plan (or /dc:design first for weighty work); open
checkboxes in any plan means /dc:implement (with /dc:branch to isolate the
work); fewer reviews than plans means /dc:review; no handoff bundle yet
means /dc:handoff-to-tc or /dc:pr; a bundle with no lessons captured means
/dc:learn; no security scan report yet means /dc:scan (and /dc:ci to set up
the CI pipeline); no deployment record yet means /dc:release then
/dc:publish and /dc:deploy to ship the image; and once a deployment
exists the cycle is complete, so /dc:plan for the next feature.

Run: `python3 <plugin-root>/scripts/next_step.py <project-root>`

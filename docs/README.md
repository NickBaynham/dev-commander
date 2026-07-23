# Dev Commander documentation

Dev Commander is an AI-assisted software development agent, shipped as a
Claude Code plugin. It guides a project through the development lifecycle
with a `/dc:*` command family, keeping every artifact in a committed
`.dev-commander/` workspace.

These guides go deeper than the [README](../README.md).

| Guide | What it covers |
| --- | --- |
| [Getting started](getting-started.md) | Install the plugin, create a workspace, and walk one feature end to end. |
| [The development lifecycle](lifecycle.md) | How the skills fit together and how `/dc:next` threads them. |
| [Command reference](commands.md) | Every `/dc:*` command: what it does, what it reads, what it writes. |
| [Workspace reference](workspace.md) | The `.dev-commander/` directory layout and artifact conventions. |

For the authoritative specification and implementation plan, see
[planning/plan.md](../planning/plan.md). For agent orientation when picking
up the codebase, see [AGENTS.md](../AGENTS.md).

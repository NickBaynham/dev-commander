# Dev Commander Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Dev Commander, a Claude Code plugin providing a `/dc:*` command family that guides the software development lifecycle (scaffold, plan, implement, review, debug, hand off to Test Commander), mirroring the proven Test Commander architecture.

**Architecture:** A skill pack first, runtime second. The repo hosts a local marketplace at the root and the plugin under `plugins/dev-commander/`. Each skill lives at `plugins/dev-commander/skills/<name>/SKILL.md`. Orchestration commands (dc-core) are backed by small Python helper scripts bundled inside the plugin; all other skills are Markdown guidance plus bundled templates. A pytest suite at the repo root verifies plugin structure, skill frontmatter, helper behavior, and template completeness.

**Tech Stack:** Claude Code plugin format (marketplace.json + plugin.json + SKILL.md), Python 3.12, pdm, pytest, ruff, Make.

## Global Constraints

- pdm is the Python package manager. No pip, no poetry, no virtualenvs inside containers.
- Make targets must exist for setup, lint, test, build, run.
- No emojis anywhere: code, docs, print statements, logs.
- README stays under 400 lines; deep detail links out to docs/ and this plan.
- Maintain CHANGELOG.md (newest first within each phase) and TODO.md.
- Root-cause-before-fix discipline; prove problems with a failing test before fixing.
- Plugin structure follows Claude Code convention (inherited from Test Commander Decision D12): marketplace at repo root, plugin under `plugins/<name>/`, sibling skills under `skills/<skill-name>/`. No umbrella SKILL.md.
- Use the `claude` CLI for plugin operations (`claude plugin validate`, `claude plugin marketplace add`, `claude plugin install`), never interactive slash commands (inherited from Test Commander Decision D17).
- User-facing helpers and templates ship inside the plugin (`plugins/dev-commander/scripts/`, `plugins/dev-commander/templates/`); dev tooling stays at the repo root (`scripts/`). Only `plugins/dev-commander/` is copied into the installed plugin cache (inherited from Test Commander Decision D18).
- Dev Commander is product-domain-agnostic. Shipped defaults use universal software-engineering vocabulary only (inherited from Test Commander Decision D19).
- The workspace a consuming project gets is `.dev-commander/` and is committed to that project's git.
- Skill names use the `dc-` prefix; commands use the `/dc:` namespace.

## Decisions

| # | Decision |
| --- | --- |
| DC1 | Vendor and own all skills in-repo. Community skills are design references only. |
| DC2 | Seven skills in v0.1: dc-core, dc-scaffold, dc-plan, dc-implement, dc-review, dc-debug, dc-handoff. |
| DC3 | Only dc-core commands get Python helpers. All other skills are Markdown guidance plus templates; Claude performs the work. |
| DC4 | dc-handoff writes artifacts Test Commander's `/tc:learn-from-*` commands can ingest; it never invokes Test Commander directly. |
| DC5 | Every task in this plan ends with tests passing and a commit. |

## File Structure

```
dev-commander/
├── AGENTS.md                      # agent orientation; entry point (already created)
├── CLAUDE.md                      # @AGENTS.md (already created)
├── CHANGELOG.md                   # phase-by-phase shipping log
├── TODO.md                        # features not yet added
├── README.md                      # user-facing overview, < 400 lines
├── Makefile                       # install / lint / test / build / run / verify
├── pyproject.toml                 # pdm project, dev deps: ruff, pytest
├── planning/plan.md               # this file — authoritative spec
├── .claude-plugin/marketplace.json
├── scripts/
│   └── verify_skills.py           # dev tooling: frontmatter + link checks
├── tests/
│   ├── test_plugin_structure.py
│   ├── test_dc_core.py
│   ├── test_dc_scaffold.py
│   └── test_dc_skills.py          # shared checks for dc-plan/implement/review/debug/handoff
└── plugins/dev-commander/
    ├── .claude-plugin/plugin.json
    ├── scripts/                   # user-facing helpers (dc-core only, per DC3)
    │   ├── init_workspace.py
    │   ├── status.py
    │   ├── journal.py
    │   └── next_step.py
    ├── templates/
    │   ├── workspace/             # copied by /dc:init into .dev-commander/
    │   │   ├── project.md
    │   │   ├── journal/.gitkeep
    │   │   ├── plans/.gitkeep
    │   │   ├── increments/.gitkeep
    │   │   ├── reviews/.gitkeep
    │   │   ├── debug/.gitkeep
    │   │   └── handoff/.gitkeep
    │   └── scaffold/              # used by /dc:scaffold
    │       ├── Makefile.tmpl
    │       ├── pyproject.toml.tmpl
    │       ├── docker-compose.yml.tmpl
    │       ├── README.md.tmpl
    │       ├── CHANGELOG.md.tmpl
    │       └── TODO.md.tmpl
    └── skills/
        ├── dc-core/SKILL.md
        ├── dc-scaffold/SKILL.md
        ├── dc-plan/SKILL.md
        ├── dc-implement/SKILL.md
        ├── dc-review/SKILL.md
        ├── dc-debug/SKILL.md
        └── dc-handoff/SKILL.md
```

Workspace layout created in a consuming project by `/dc:init`:

```
.dev-commander/
├── project.md        # project identity, stack, constraints
├── journal/          # dated decision-journal entries (YYYY-MM-DD-NN.md)
├── plans/            # implementation plans from /dc:plan
├── increments/       # per-increment records from /dc:implement
├── reviews/          # review reports from /dc:review
├── debug/            # root-cause investigation reports from /dc:debug
└── handoff/          # artifacts for Test Commander ingestion
```

---

### Task 1: Repo scaffold and plugin manifests

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/dev-commander/.claude-plugin/plugin.json`
- Create: `README.md`, `CHANGELOG.md`, `TODO.md`
- Test: `tests/test_plugin_structure.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: repo layout every later task builds inside; `make test` and `make lint` used by every later task's verify step.

- [x] **Step 1: Write the failing structure test**

```python
# tests/test_plugin_structure.py
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "dev-commander"


def test_marketplace_manifest():
    manifest = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert manifest["name"] == "dev-commander-marketplace"
    assert manifest["plugins"][0]["name"] == "dev-commander"
    assert manifest["plugins"][0]["source"] == "./plugins/dev-commander"


def test_plugin_manifest():
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "dev-commander"
    assert "development" in manifest["description"].lower()


def test_root_documents_exist():
    for name in ["README.md", "CHANGELOG.md", "TODO.md", "AGENTS.md", "CLAUDE.md", "Makefile"]:
        assert (ROOT / name).is_file(), f"missing {name}"


def test_no_emojis_in_root_docs():
    for name in ["README.md", "CHANGELOG.md", "TODO.md", "AGENTS.md"]:
        text = (ROOT / name).read_text()
        assert not any(ord(ch) > 0x2500 for ch in text), f"emoji or symbol in {name}"
```

- [x] **Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/test_plugin_structure.py -v` (after `pdm install`; pyproject written in Step 3)
Expected: FAIL — missing files.

- [x] **Step 3: Write pyproject.toml**

```toml
[project]
name = "dev-commander"
version = "0.0.0"
description = "An AI-assisted software development agent shipped as a Claude Code plugin."
authors = [
    {name = "Nick Baynham", email = "nickbaynham@gmail.com"},
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.urls]
Homepage = "https://github.com/NickBaynham/dev-commander"
Repository = "https://github.com/NickBaynham/dev-commander"

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.pdm]
distribution = false

[dependency-groups]
dev = [
    "ruff>=0.6",
    "pytest>=8.0",
]

[tool.ruff]
line-length = 100
```

- [x] **Step 4: Write Makefile**

```makefile
.PHONY: help install uninstall lint test build run verify \
        pdm-install validate-manifests marketplace-add plugin-install

help:
	@echo "Dev Commander - Make targets"
	@echo ""
	@echo "  make install     Install Python deps, validate manifests, register the local"
	@echo "                   marketplace, and install the plugin. Idempotent."
	@echo "  make uninstall   Remove the plugin and unregister the marketplace."
	@echo "  make lint        Run the ruff linter."
	@echo "  make test        Run pytest."
	@echo "  make build       Placeholder; no build artifacts in v0.1."
	@echo "  make run         Placeholder; no runtime in v0.1."
	@echo "  make verify      Run lint, test, and the skill verifier."

install: pdm-install validate-manifests marketplace-add plugin-install

uninstall:
	-claude plugin uninstall dev-commander
	-claude plugin marketplace remove dev-commander-marketplace

pdm-install:
	pdm install

validate-manifests:
	claude plugin validate .
	claude plugin validate plugins/dev-commander

marketplace-add:
	@if claude plugin marketplace list 2>/dev/null | grep -q dev-commander-marketplace; then \
		echo "marketplace dev-commander-marketplace already registered"; \
	else \
		claude plugin marketplace add "$$PWD"; \
	fi

plugin-install:
	@if claude plugin list 2>/dev/null | grep -q 'dev-commander@dev-commander-marketplace'; then \
		echo "plugin dev-commander already installed"; \
	else \
		claude plugin install dev-commander@dev-commander-marketplace; \
	fi

lint:
	pdm run ruff check .

test:
	pdm run pytest

build:
	@echo "No build artifacts in v0.1."

run:
	@echo "No runtime in v0.1."

verify: lint test
	pdm run python scripts/verify_skills.py
```

- [x] **Step 5: Write .claude-plugin/marketplace.json**

```json
{
  "name": "dev-commander-marketplace",
  "owner": {
    "name": "Nick Baynham",
    "email": "nickbaynham@gmail.com"
  },
  "description": "Local marketplace hosting the Dev Commander plugin.",
  "plugins": [
    {
      "name": "dev-commander",
      "source": "./plugins/dev-commander",
      "version": "0.0.0",
      "description": "An AI-assisted software development agent. Skills span workspace orchestration, project scaffolding, incremental implementation planning, test-first implementation, rubric-driven code review, root-cause debugging, and handoff to Test Commander."
    }
  ]
}
```

- [x] **Step 6: Write plugins/dev-commander/.claude-plugin/plugin.json**

```json
{
  "name": "dev-commander",
  "version": "0.0.0",
  "description": "An AI-assisted software development agent. Skills span workspace orchestration, project scaffolding, incremental implementation planning, test-first implementation, rubric-driven code review, root-cause debugging, and handoff to Test Commander.",
  "author": {
    "name": "Nick Baynham",
    "email": "nickbaynham@gmail.com"
  },
  "homepage": "https://github.com/NickBaynham/dev-commander",
  "repository": "https://github.com/NickBaynham/dev-commander",
  "license": "MIT",
  "keywords": [
    "development",
    "planning",
    "tdd",
    "code-review",
    "debugging",
    "scaffolding"
  ]
}
```

- [x] **Step 7: Write README.md, CHANGELOG.md, TODO.md**

README.md:

```markdown
# Dev Commander

An AI-assisted software development agent, shipped as a Claude Code plugin.
Dev Commander guides a project through scaffold, plan, implement, review,
debug, and handoff to [Test Commander](https://github.com/NickBaynham/test-commander)
via a `/dc:*` command family.

Status: Phase 0 in progress.

## Install

    ./bootstrap.sh   # once available; verifies prerequisites
    make install

## Commands

| Command | Skill | Purpose |
| --- | --- | --- |
| /dc:init | dc-core | Initialize the .dev-commander/ workspace |
| /dc:status | dc-core | Summarize workspace state |
| /dc:journal | dc-core | Append a decision-journal entry |
| /dc:next | dc-core | Recommend the next command |
| /dc:scaffold | dc-scaffold | Generate project scaffolding (pdm, Make, docker compose) |
| /dc:plan | dc-plan | Produce a small-increment implementation plan |
| /dc:review-plan | dc-plan | Review a plan against the increment rubric |
| /dc:implement | dc-implement | Execute the next plan increment test-first |
| /dc:review | dc-review | Rubric-driven code review of an increment or diff |
| /dc:debug | dc-debug | Root-cause-first debugging workflow |
| /dc:handoff-to-tc | dc-handoff | Package artifacts for Test Commander ingestion |

## Development

    make lint    # ruff
    make test    # pytest
    make verify  # lint + test + skill verifier

Authoritative spec: [planning/plan.md](planning/plan.md).
Agent orientation: [AGENTS.md](AGENTS.md).
```

CHANGELOG.md:

```markdown
# Changelog

## Phase 0 — Repo scaffold

- Repo scaffold: pyproject (pdm), Makefile, marketplace and plugin manifests,
  structure tests, README, TODO, agent orientation files.
```

TODO.md:

```markdown
# To Do

- Phase 1: dc-core skill (init, status, journal, next) with Python helpers.
- Phase 2: dc-scaffold skill and scaffold templates.
- Phase 3: dc-plan skill.
- Phase 4: dc-implement skill.
- Phase 5: dc-review skill.
- Phase 6: dc-debug skill.
- Phase 7: dc-handoff skill.
- Later: bootstrap.sh prerequisite verifier, docs/ user guides, dc-learning.
```

- [x] **Step 8: Run tests to verify they pass**

Run: `pdm install && pdm run pytest tests/test_plugin_structure.py -v`
Expected: 4 passed.

Run: `claude plugin validate . && claude plugin validate plugins/dev-commander`
Expected: both manifests valid.

- [x] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: repo scaffold, plugin manifests, structure tests (Phase 0)"
```

---

### Task 2: Skill verifier dev tool

**Files:**
- Create: `scripts/verify_skills.py`
- Test: extend `tests/test_plugin_structure.py`

**Interfaces:**
- Consumes: `plugins/dev-commander/skills/*/SKILL.md` (none exist yet; verifier must pass on zero skills).
- Produces: `verify_skills(root: Path) -> list[str]` returning a list of violation strings; used by `make verify` and by every skill task's verify step.

- [x] **Step 1: Write the failing test**

Append to `tests/test_plugin_structure.py`:

```python
def test_verify_skills_runs_clean():
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_skills.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_verify_skills_detects_problems(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from verify_skills import verify_skills

    bad = tmp_path / "dc-broken"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: wrong-name\n---\n\n[gone](missing.md)\n")
    problems = verify_skills(tmp_path)
    assert any("missing description" in p for p in problems)
    assert any("name != directory name" in p for p in problems)
    assert any("broken link missing.md" in p for p in problems)
```

- [x] **Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/test_plugin_structure.py::test_verify_skills_runs_clean -v`
Expected: FAIL — script does not exist.

- [x] **Step 3: Write scripts/verify_skills.py**

```python
"""Verify every shipped SKILL.md has valid frontmatter and resolvable local links."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "dev-commander" / "skills"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def verify_skills(root: Path) -> list[str]:
    problems = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        text = skill_md.read_text()
        if not text.startswith("---\n"):
            problems.append(f"{skill_md}: missing frontmatter")
            continue
        front = text.split("---", 2)[1]
        fields = {
            m.group(1): m.group(2).strip()
            for m in re.finditer(r"^(name|description):\s*(.+)$", front, re.MULTILINE)
        }
        for field in ("name", "description"):
            if field not in fields:
                problems.append(f"{skill_md}: frontmatter missing {field}")
        name = skill_md.parent.name
        if fields.get("name", name) != name:
            problems.append(f"{skill_md}: frontmatter name != directory name {name}")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            if not (skill_md.parent / target.split("#")[0]).exists():
                problems.append(f"{skill_md}: broken link {target}")
    return problems


def main() -> int:
    problems = verify_skills(SKILLS) if SKILLS.is_dir() else []
    for p in problems:
        print(p)
    print(f"verify_skills: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run tests to verify they pass**

Run: `pdm run pytest tests/test_plugin_structure.py -v && pdm run ruff check .`
Expected: all pass, no lint errors.

- [x] **Step 5: Commit**

```bash
git add scripts/verify_skills.py tests/test_plugin_structure.py
git commit -m "feat: skill verifier dev tool"
```

---

### Task 3: dc-core skill — workspace init, status, journal, next

**Files:**
- Create: `plugins/dev-commander/templates/workspace/project.md`
- Create: `plugins/dev-commander/templates/workspace/{journal,plans,increments,reviews,debug,handoff}/.gitkeep`
- Create: `plugins/dev-commander/scripts/init_workspace.py`
- Create: `plugins/dev-commander/scripts/status.py`
- Create: `plugins/dev-commander/scripts/journal.py`
- Create: `plugins/dev-commander/scripts/next_step.py`
- Create: `plugins/dev-commander/skills/dc-core/SKILL.md`
- Test: `tests/test_dc_core.py`

**Interfaces:**
- Consumes: repo layout from Task 1; verifier from Task 2.
- Produces: the `.dev-commander/` workspace contract (directory names `journal`, `plans`, `increments`, `reviews`, `debug`, `handoff`, file `project.md`) that Tasks 5-9 write into. Helper CLIs: `init_workspace.py <project-root>`, `status.py <project-root>`, `journal.py <project-root> <entry text>`, `next_step.py <project-root>` — each prints a plain-text report and exits 0 on success, 1 on error.

- [x] **Step 1: Write the failing tests**

```python
# tests/test_dc_core.py
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "dev-commander" / "scripts"
DIRS = ["journal", "plans", "increments", "reviews", "debug", "handoff"]


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True,
    )


def test_init_creates_workspace(tmp_path):
    result = run("init_workspace.py", tmp_path)
    assert result.returncode == 0, result.stderr
    ws = tmp_path / ".dev-commander"
    assert (ws / "project.md").is_file()
    for d in DIRS:
        assert (ws / d).is_dir(), f"missing {d}/"


def test_init_is_idempotent(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "project.md").write_text("edited\n")
    result = run("init_workspace.py", tmp_path)
    assert result.returncode == 0
    assert (tmp_path / ".dev-commander" / "project.md").read_text() == "edited\n"


def test_status_reports_counts(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "plans" / "0001-example.md").write_text("# plan\n")
    result = run("status.py", tmp_path)
    assert result.returncode == 0
    assert "plans: 1" in result.stdout


def test_status_fails_without_workspace(tmp_path):
    result = run("status.py", tmp_path)
    assert result.returncode == 1


def test_journal_appends_dated_entry(tmp_path):
    run("init_workspace.py", tmp_path)
    result = run("journal.py", tmp_path, "Chose pdm over poetry")
    assert result.returncode == 0
    entries = list((tmp_path / ".dev-commander" / "journal").glob("*.md"))
    assert len(entries) == 1
    assert "Chose pdm over poetry" in entries[0].read_text()


def test_next_recommends_plan_when_no_plans(tmp_path):
    run("init_workspace.py", tmp_path)
    result = run("next_step.py", tmp_path)
    assert result.returncode == 0
    assert "/dc:plan" in result.stdout


def test_next_recommends_implement_when_plan_exists(tmp_path):
    run("init_workspace.py", tmp_path)
    (tmp_path / ".dev-commander" / "plans" / "0001-example.md").write_text("- [ ] Task 1\n")
    result = run("next_step.py", tmp_path)
    assert "/dc:implement" in result.stdout


def test_status_counts_handoff_bundles(tmp_path):
    run("init_workspace.py", tmp_path)
    bundle = tmp_path / ".dev-commander" / "handoff" / "0001-example"
    bundle.mkdir()
    (bundle / "summary.md").write_text("# summary\n")
    result = run("status.py", tmp_path)
    assert "handoff: 1" in result.stdout
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_core.py -v`
Expected: FAIL — scripts do not exist.

- [x] **Step 3: Write the workspace template**

`plugins/dev-commander/templates/workspace/project.md`:

```markdown
# Project

## Identity

Name:
One-line description:

## Stack

Language and version:
Package manager:
Frameworks:
Local services (docker compose):

## Constraints

- Work in small increments; each increment is tested before moving on.
- pdm for Python; Make targets for setup, lint, test, build, run.
- No emojis in code, docs, or output.
```

Create empty `.gitkeep` files in `journal/`, `plans/`, `increments/`, `reviews/`, `debug/`, `handoff/`.

- [x] **Step 4: Write init_workspace.py**

```python
"""Initialize a .dev-commander/ workspace. Idempotent: existing files are preserved."""
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "workspace"


def init_workspace(project_root: Path) -> Path:
    ws = project_root / ".dev-commander"
    for src in TEMPLATE.rglob("*"):
        dest = ws / src.relative_to(TEMPLATE)
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    return ws


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = init_workspace(root)
    print(f"workspace ready at {ws}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 5: Write status.py**

```python
"""Summarize a .dev-commander/ workspace: artifact counts per directory."""
import sys
from pathlib import Path

DIRS = ["journal", "plans", "increments", "reviews", "debug", "handoff"]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = root / ".dev-commander"
    if not ws.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    print(f"workspace: {ws}")
    for d in DIRS:
        if d == "handoff":
            count = len([p for p in (ws / d).iterdir() if p.is_dir()])
        else:
            count = len([p for p in (ws / d).glob("*.md")])
        print(f"  {d}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 6: Write journal.py**

```python
"""Append a dated decision-journal entry to .dev-commander/journal/."""
import sys
from datetime import date
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: journal.py <project-root> <entry text>")
        return 1
    root, text = Path(sys.argv[1]), " ".join(sys.argv[2:])
    journal = root / ".dev-commander" / "journal"
    if not journal.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    today = date.today().isoformat()
    seq = len(list(journal.glob(f"{today}-*.md"))) + 1
    entry = journal / f"{today}-{seq:02d}.md"
    entry.write_text(f"# {today} entry {seq:02d}\n\n{text}\n")
    print(f"journal entry written: {entry.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 7: Write next_step.py**

```python
"""Recommend the next /dc: command from workspace state."""
import sys
from pathlib import Path


def recommend(ws: Path) -> str:
    plans = [p for p in (ws / "plans").glob("*.md")]
    if not plans:
        return "No plans yet. Run /dc:plan to produce an implementation plan."
    open_boxes = any("- [ ]" in p.read_text() for p in plans)
    if open_boxes:
        return "Open increments remain. Run /dc:implement to execute the next one."
    reviews = [p for p in (ws / "reviews").glob("*.md") if "plan-review" not in p.name]
    if len(reviews) < len(plans):
        return "All increments complete. Run /dc:review for a rubric-driven review."
    return "Reviewed and complete. Run /dc:handoff-to-tc to package for Test Commander."


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ws = root / ".dev-commander"
    if not ws.is_dir():
        print("no .dev-commander/ workspace; run /dc:init first")
        return 1
    print(recommend(ws))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 8: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py -v`
Expected: 8 passed.

- [x] **Step 9: Write dc-core SKILL.md**

```markdown
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
reviews, debug, and handoff.

Run: `python3 <plugin-root>/scripts/status.py <project-root>`

### /dc:journal

Append a dated decision-journal entry. Ask the user for the entry text if
they did not provide it.

Run: `python3 <plugin-root>/scripts/journal.py <project-root> <entry text>`

### /dc:next

Recommend the next command from workspace state: no plans means /dc:plan;
open checkboxes in any plan means /dc:implement; fewer reviews than plans
means /dc:review; otherwise /dc:handoff-to-tc.

Run: `python3 <plugin-root>/scripts/next_step.py <project-root>`
```

- [x] **Step 10: Verify and commit**

Run: `make verify`
Expected: lint clean, all tests pass, `verify_skills: 0 problem(s)`.

```bash
git add -A
git commit -m "feat: dc-core skill with init, status, journal, next helpers (Phase 1)"
```

Update CHANGELOG.md (add a Phase 1 section at top) and TODO.md (remove the Phase 1 line) in the same commit.

---

### Task 4: dc-scaffold skill and scaffold templates

**Files:**
- Create: `plugins/dev-commander/templates/scaffold/Makefile.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/pyproject.toml.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/docker-compose.yml.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/README.md.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/CHANGELOG.md.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/TODO.md.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/tests/test_smoke.py.tmpl`
- Create: `plugins/dev-commander/skills/dc-scaffold/SKILL.md`
- Test: `tests/test_dc_scaffold.py`

**Interfaces:**
- Consumes: workspace contract from Task 3 (scaffold decisions are journaled via the dc-core journal helper).
- Produces: templates with `{{project_name}}` and `{{project_description}}` placeholders that the SKILL.md instructs Claude to substitute.

- [x] **Step 1: Write the failing tests**

```python
# tests/test_dc_scaffold.py
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"
REQUIRED = [
    "Makefile.tmpl", "pyproject.toml.tmpl", "docker-compose.yml.tmpl",
    "README.md.tmpl", "CHANGELOG.md.tmpl", "TODO.md.tmpl",
]


def test_all_templates_exist():
    for name in REQUIRED:
        assert (TEMPLATES / name).is_file(), f"missing {name}"


def test_makefile_template_has_required_targets():
    text = (TEMPLATES / "Makefile.tmpl").read_text()
    for target in ["install:", "lint:", "test:", "build:", "run:"]:
        assert target in text, f"Makefile.tmpl missing {target}"


def test_pyproject_template_uses_pdm():
    text = (TEMPLATES / "pyproject.toml.tmpl").read_text()
    assert "pdm" in text


def test_templates_use_placeholders():
    text = (TEMPLATES / "README.md.tmpl").read_text()
    assert "{{project_name}}" in text


def test_skill_exists():
    skill = ROOT / "plugins" / "dev-commander" / "skills" / "dc-scaffold" / "SKILL.md"
    assert skill.is_file()
    assert "/dc:scaffold" in skill.read_text()


def test_smoke_test_template_exists():
    smoke = TEMPLATES / "tests" / "test_smoke.py.tmpl"
    assert smoke.is_file()
    assert "def test_" in smoke.read_text()
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_scaffold.py -v`
Expected: FAIL — templates missing.

- [x] **Step 3: Write the templates**

`Makefile.tmpl`:

```makefile
.PHONY: help install lint test build run

help:
	@echo "{{project_name}} - Make targets: install, lint, test, build, run"

install:
	pdm install

lint:
	pdm run ruff check .

test:
	pdm run pytest

build:
	@echo "Define build steps for {{project_name}}."

run:
	docker compose up -d
	@echo "Define run steps for {{project_name}}."
```

`pyproject.toml.tmpl`:

```toml
[project]
name = "{{project_name}}"
version = "0.0.0"
description = "{{project_description}}"
requires-python = ">=3.12"
dependencies = []

[tool.pdm]
distribution = false

[dependency-groups]
dev = [
    "ruff>=0.6",
    "pytest>=8.0",
]
```

`docker-compose.yml.tmpl`:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: {{project_name}}
      POSTGRES_PASSWORD: {{project_name}}
      POSTGRES_DB: {{project_name}}
    ports:
      - "5432:5432"
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

`README.md.tmpl`:

```markdown
# {{project_name}}

{{project_description}}

## Setup

    make install

## Development

    make lint
    make test
    make run

Change log: [CHANGELOG.md](CHANGELOG.md). Pending work: [TODO.md](TODO.md).
```

`CHANGELOG.md.tmpl`:

```markdown
# Changelog

## Unreleased

- Initial scaffold generated by Dev Commander.
```

`TODO.md.tmpl`:

```markdown
# To Do

- Define the first feature increment with /dc:plan.
```

`tests/test_smoke.py.tmpl`:

```python
"""Placeholder test so make test passes on a fresh scaffold.

Replace with real tests via /dc:plan and /dc:implement.
"""


def test_scaffold_is_healthy():
    assert True
```

- [x] **Step 4: Write dc-scaffold SKILL.md**

```markdown
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
```

- [x] **Step 5: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_scaffold.py -v && make verify`
Expected: all pass, verifier clean.

- [x] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: dc-scaffold skill and scaffold templates (Phase 2)"
```

Update CHANGELOG.md and TODO.md in the same commit.

---

### Task 5: dc-plan skill

**Files:**
- Create: `plugins/dev-commander/skills/dc-plan/SKILL.md`
- Test: `tests/test_dc_skills.py`

**Interfaces:**
- Consumes: workspace contract from Task 3 (`plans/` directory).
- Produces: plan file convention `plans/NNNN-<slug>.md` containing `- [ ]` increment checkboxes — the exact format `next_step.py` (Task 3) and dc-implement (Task 6) read.

- [x] **Step 1: Write the failing shared skill test**

```python
# tests/test_dc_skills.py
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "dev-commander" / "skills"

# Tasks 6-9 append one entry each as their skills ship, so make verify
# stays green between tasks.
EXPECTED = {
    "dc-plan": ["/dc:plan", "/dc:review-plan", "plans/"],
}


@pytest.mark.parametrize("name", EXPECTED)
def test_skill_has_frontmatter_and_required_content(name):
    skill = SKILLS / name / "SKILL.md"
    assert skill.is_file(), f"missing {name}/SKILL.md"
    text = skill.read_text()
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert f"name: {name}" in front
    assert "description:" in front
    for marker in EXPECTED[name]:
        assert marker in text, f"{name}: missing '{marker}'"
```

- [x] **Step 2: Run test to verify dc-plan case fails**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-plan]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 3: Write dc-plan SKILL.md**

```markdown
---
name: dc-plan
description: Implementation planning for Dev Commander. Use when the user runs /dc:plan or /dc:review-plan, or asks to turn requirements or a feature idea into a small-increment implementation plan. Produces plans under .dev-commander/plans/ where every increment is independently buildable, testable, and committable.
---

# dc-plan

Turns requirements into a small-increment implementation plan stored in
the workspace. Plans are the contract dc-implement executes.

## /dc:plan

1. Gather inputs: a feature request, user story, BRD, or reviewed
   requirements. If a business-requirements BRD exists, consume it
   rather than re-deriving requirements.
2. Write the plan to `.dev-commander/plans/NNNN-<slug>.md` where NNNN is
   the next zero-padded sequence number.
3. Plan format:
   - Header: Goal (one sentence), Architecture (2-3 sentences),
     Tech Stack, Global Constraints.
   - Increments as third-level headings, each with a `- [ ]` checkbox
     line, exact file paths, the failing test to write first, the
     minimal implementation, the verify command, and the commit message.
4. Increment rubric — every increment must be:
   - Small: one deliverable, one test cycle, roughly 2-5 minutes per step.
   - Independent: buildable and testable without later increments.
   - Test-first: names the failing test before the implementation.
   - Committed: ends with a commit.
5. No placeholders. "TBD", "add error handling", or steps without code
   are plan failures.

## /dc:review-plan

Review an existing plan file against the increment rubric above. Report
one finding per violated rubric item with the increment heading and a
concrete repair. Write the review to
`.dev-commander/reviews/NNNN-plan-review-<slug>.md` and give an overall
verdict: ready, ready with repairs, or not ready.
```

- [x] **Step 4: Run test to verify dc-plan case passes**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-plan]" -v && make verify`
Expected: dc-plan passes; verifier clean.

- [x] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: dc-plan skill (Phase 3)"
```

Update CHANGELOG.md and TODO.md in the same commit.

---

### Task 6: dc-implement skill

**Files:**
- Create: `plugins/dev-commander/skills/dc-implement/SKILL.md`
- Modify: `tests/test_dc_skills.py` (add the dc-implement case)

**Interfaces:**
- Consumes: plan format from Task 5 (`- [ ]` increments in `plans/NNNN-<slug>.md`).
- Produces: increment record convention `increments/NNNN-<slug>-<increment>.md`; checks off plan checkboxes, which drives `next_step.py` recommendations.

- [x] **Step 1: Add the dc-implement case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-implement": ["/dc:implement", "increments/", "failing test"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-implement]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-implement SKILL.md**

```markdown
---
name: dc-implement
description: Test-first increment execution for Dev Commander. Use when the user runs /dc:implement or asks to execute the next increment of a plan under .dev-commander/plans/. Executes exactly one increment per invocation with a failing test written first, then stops for review.
---

# dc-implement

Executes one plan increment at a time. One invocation, one increment,
then stop. This keeps work incremental and reviewable.

## /dc:implement

1. Locate the active plan: the lowest-numbered file in
   `.dev-commander/plans/` that still contains a `- [ ]` checkbox. If
   the user names a plan, use that one.
2. Take the first unchecked increment. Do not skip ahead or batch.
3. Execute the increment test-first:
   - Write the failing test named by the increment; run it; confirm it
     fails for the expected reason before writing implementation code.
   - Write the minimal implementation; run the test; confirm it passes.
   - Run the project's full verify command (make verify, or make lint
     test when no verify target exists).
4. Record the increment at
   `.dev-commander/increments/NNNN-<slug>-<increment>.md`, where NNNN
   is the next zero-padded sequence number: what was built, test evidence (command and output summary), files touched,
   and any deviations from the plan with reasons.
5. Update the project's CHANGELOG.md, and TODO.md when scope changed.
6. Check off the increment's `- [ ]` box in the plan file.
7. Commit with the message given in the plan, then stop and report.
   The user decides whether to continue with the next increment.

If the increment cannot be completed as planned, stop, record the
blocker in the increment file, and recommend /dc:plan to revise the
plan. Never silently improvise a different design.
```

- [x] **Step 3: Run test to verify dc-implement case passes**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-implement]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: dc-implement skill (Phase 4)"
```

Update CHANGELOG.md and TODO.md in the same commit.

---

### Task 7: dc-review skill

**Files:**
- Create: `plugins/dev-commander/skills/dc-review/SKILL.md`
- Modify: `tests/test_dc_skills.py` (add the dc-review case)

**Interfaces:**
- Consumes: increment records from Task 6; workspace `reviews/` directory from Task 3.
- Produces: review report convention `reviews/NNNN-<slug>.md` with a verdict line — counted by `next_step.py`.

- [x] **Step 1: Add the dc-review case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-review": ["/dc:review", "reviews/", "rubric"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-review]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-review SKILL.md**

```markdown
---
name: dc-review
description: Rubric-driven code review for Dev Commander. Use when the user runs /dc:review or asks for a review of an increment, a diff, or recent changes. Produces a structured review report under .dev-commander/reviews/ with severity-rated findings and a verdict.
---

# dc-review

Reviews code against a fixed rubric so findings are consistent across
sessions. Reviews the most recent increment by default; the user may
name a diff, branch, or file set instead.

## /dc:review

1. Establish scope: the latest increment record in
   `.dev-commander/increments/`, or the diff the user names.
2. Review against the rubric. One finding per violation, each with
   file:line, severity (blocker, major, minor), evidence, and a
   concrete repair.

Rubric:
   - Correctness: does the code do what the increment record claims?
     Is every claim backed by a passing test?
   - Simplicity: no over-engineering, no defensive programming, no
     speculative abstractions. Exception handlers only where needed.
   - DRY: repeated logic factored into functions or methods.
   - Size: short modules, classes, and methods; focused files.
   - Clarity: clear names over comments; docstrings concise; no emojis.
   - Tests: behavior-focused, failing-first evidence recorded, no
     assertions weakened to force a pass.
3. Write the report to `.dev-commander/reviews/NNNN-<slug>.md`, where
   NNNN is the next zero-padded sequence number, with a verdict:
   approve, approve with repairs, or request changes.
4. Do not modify code during review. Repairs are applied by
   /dc:implement or by the user.
```

- [x] **Step 3: Run test to verify dc-review case passes**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-review]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: dc-review skill (Phase 5)"
```

Update CHANGELOG.md and TODO.md in the same commit.

---

### Task 8: dc-debug skill

**Files:**
- Create: `plugins/dev-commander/skills/dc-debug/SKILL.md`
- Modify: `tests/test_dc_skills.py` (add the dc-debug case)

**Interfaces:**
- Consumes: workspace `debug/` directory from Task 3.
- Produces: investigation report convention `debug/NNNN-<slug>.md`.

- [x] **Step 1: Add the dc-debug case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-debug": ["/dc:debug", "debug/", "root cause"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-debug]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-debug SKILL.md**

```markdown
---
name: dc-debug
description: Root-cause-first debugging for Dev Commander. Use when the user runs /dc:debug or reports a bug, test failure, or unexpected behavior. Reproduces the problem, isolates it with a failing test, proves the root cause with evidence, fixes it, and records preventive documentation.
---

# dc-debug

A disciplined debugging workflow. The root cause is identified and
proven before any fix is written. Guesswork and workarounds are not
fixes.

## /dc:debug

1. Reproduce: run the failing scenario and capture the exact command
   and output. If it cannot be reproduced consistently, investigate
   until it can; do not proceed on an unreproduced bug.
2. Isolate: write the smallest failing test that captures the defect.
   This test is the proof of the problem and later the proof of the fix.
3. Diagnose: trace from symptom to cause with evidence (logs, values,
   bisection). State the root cause as a falsifiable claim and show the
   evidence that confirms it. Do not jump to conclusions.
4. Fix: make the minimal change that addresses the root cause. Run the
   isolating test (now passing) and the full suite.
5. Prevent: update documentation so the problem is not reintroduced —
   add preventive verbiage to the project's agent file or docs, and
   note the lesson in the workspace journal with the dc-core journal
   helper.
6. Record the investigation at `.dev-commander/debug/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number: symptom,
   reproduction, isolating test, root cause with evidence, fix,
   prevention.

Never fix before step 3 is complete. If pressed for a quick fix,
explain that an unproven fix is a guess and continue the workflow.
```

- [x] **Step 3: Run test to verify dc-debug case passes**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-debug]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: dc-debug skill (Phase 6)"
```

Update CHANGELOG.md and TODO.md in the same commit.

---

### Task 9: dc-handoff skill

**Files:**
- Create: `plugins/dev-commander/skills/dc-handoff/SKILL.md`
- Modify: `tests/test_dc_skills.py` (add the dc-handoff case)

**Interfaces:**
- Consumes: plans, increments, and reviews from Tasks 5-7.
- Produces: handoff bundle convention `handoff/NNNN-<slug>/` containing `summary.md`, `features.md`, `acceptance-criteria.md` — inputs for Test Commander's `/tc:learn-from-docs` and `/tc:review-acceptance-criteria`.

- [x] **Step 1: Add the dc-handoff case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-handoff": ["/dc:handoff-to-tc", "handoff/", "learn-from"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-handoff]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-handoff SKILL.md**

```markdown
---
name: dc-handoff
description: Test Commander handoff for Dev Commander. Use when the user runs /dc:handoff-to-tc or asks to package what was built for testing. Assembles plans, increment records, and reviews into documents Test Commander's /tc:learn-from-docs and /tc:learn-from-specs commands can ingest.
---

# dc-handoff

Packages development artifacts into a bundle Test Commander can learn
from. Dev Commander never invokes Test Commander directly; it produces
documents and tells the user which /tc: commands to run next.

## /dc:handoff-to-tc

1. Establish scope: everything since the last handoff bundle, or the
   plan the user names.
2. Assemble the bundle at `.dev-commander/handoff/NNNN-<slug>/`,
   where NNNN is the next zero-padded sequence number:
   - `summary.md`: what was built and why, in plain prose; links to
     the source plans, increments, and reviews.
   - `features.md`: one section per shipped feature with entry points
     (commands, endpoints, or screens) and observable behavior.
   - `acceptance-criteria.md`: verifiable statements per feature,
     derived from the increment tests, written as behavior (given,
     when, then prose) rather than implementation detail.
3. Use universal software-engineering vocabulary; no internal jargon
   the testing side would need this conversation to decode.
4. Report the bundle path and recommend next steps: copy or point
   Test Commander at the bundle and run /tc:learn-from-docs to ingest
   the Markdown bundle, then /tc:review-acceptance-criteria against
   acceptance-criteria.md, in the consuming project.
```

- [x] **Step 3: Run full suite to verify everything passes**

Run: `pdm run pytest -v && make verify`
Expected: all tests pass across all files; verifier clean.

- [x] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: dc-handoff skill (Phase 7)"
```

Update CHANGELOG.md (Phase 7 section) and TODO.md (remove Phase 7; leave the Later section) in the same commit.

---

### Task 10: Install verification and release readiness

**Files:**
- Modify: `README.md` (status line)
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: everything above.
- Produces: an installed, working plugin.

- [x] **Step 1: Validate manifests with the claude CLI**

Run: `claude plugin validate . && claude plugin validate plugins/dev-commander`
Expected: both valid.

- [x] **Step 2: Install end-to-end**

Run: `make install`
Expected: pdm install succeeds, manifests validate, marketplace registered, plugin installed.

- [x] **Step 3: Smoke-test the workspace lifecycle in a scratch directory**

```bash
mkdir -p /tmp/dc-smoke && cd /tmp/dc-smoke
python3 ~/projects/dev-commander/plugins/dev-commander/scripts/init_workspace.py .
python3 ~/projects/dev-commander/plugins/dev-commander/scripts/status.py .
python3 ~/projects/dev-commander/plugins/dev-commander/scripts/next_step.py .
```

Expected: workspace created; status shows six directories at 0; next recommends /dc:plan.

- [x] **Step 4: Update README status line and CHANGELOG, commit, push**

Set README status to "Phases 0-7 complete; v0.1 skill set shipped."

```bash
git add -A
git commit -m "chore: v0.1 install verification and release notes"
git push -u origin main
```

---

## To Do

Tracked in [TODO.md](../TODO.md). Later phases (not in v0.1): bootstrap.sh prerequisite verifier, docs/ user guides, dc-learning (governed lesson capture mirroring tc-learning), recommended lint/format hooks.

## Completed

All ten tasks shipped 2026-07-21:

- Task 1: Repo scaffold and plugin manifests (4540bf8)
- Task 2: Skill verifier dev tool (91de91c, fix 95f204b)
- Task 3: dc-core skill (f06d04e)
- Task 4: dc-scaffold skill and templates (07e63ea, fix a243663)
- Task 5: dc-plan skill (b3c102f)
- Task 6: dc-implement skill (f61665e)
- Task 7: dc-review skill (c758d28)
- Task 8: dc-debug skill (fe2c988, fix f04c9b2)
- Task 9: dc-handoff skill (b6dd81b)
- Task 10: Install verification and release (f4baf65)

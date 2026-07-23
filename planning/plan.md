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
├── bootstrap.sh                   # post-v0.3: prerequisite verifier (checks only)
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
    │   │   ├── design/.gitkeep
    │   │   ├── learning/.gitkeep
    │   │   ├── security/.gitkeep
    │   │   └── handoff/.gitkeep
    │   └── scaffold/              # used by /dc:scaffold
    │       ├── common/            # stack-agnostic docs
    │       │   ├── README.md.tmpl
    │       │   ├── CHANGELOG.md.tmpl
    │       │   └── TODO.md.tmpl
    │       └── python/            # python stack
    │           ├── Makefile.tmpl
    │           ├── pyproject.toml.tmpl
    │           ├── docker-compose.yml.tmpl
    │           └── tests/test_smoke.py.tmpl
    └── skills/
        ├── dc-core/SKILL.md
        ├── dc-scaffold/SKILL.md
        ├── dc-plan/SKILL.md
        ├── dc-implement/SKILL.md
        ├── dc-review/SKILL.md
        ├── dc-debug/SKILL.md
        ├── dc-design/SKILL.md
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
├── design/           # design docs and ADRs
├── learning/         # candidate lessons for project guidance
├── security/         # security scan reports (NNNN-<slug>.md)
├── handoff/          # artifacts for Test Commander ingestion
└── deployments/      # publish and deploy records (NNNN-<slug>.md)
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
	@echo "  make build       Placeholder; no build artifacts."
	@echo "  make run         Placeholder; no runtime."
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
	@echo "No build artifacts."

run:
	@echo "No runtime."

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
    used = [
        int(p.stem.rsplit("-", 1)[-1])
        for p in journal.glob(f"{today}-*.md")
        if p.stem.rsplit("-", 1)[-1].isdigit()
    ]
    seq = (max(used) + 1) if used else 1
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
        return ("No plans yet. Run /dc:plan to produce an implementation plan, "
                "or /dc:design first for architecturally significant work.")
    if any("- [ ]" in p.read_text() for p in plans):
        return ("Open increments remain. Run /dc:implement to execute the next one; "
                "use /dc:branch first to isolate the work on a feature branch.")
    reviews = [p for p in (ws / "reviews").glob("*.md") if "plan-review" not in p.name]
    if len(reviews) < len(plans):
        return "All increments complete. Run /dc:review for a rubric-driven review."
    if not [p for p in (ws / "handoff").iterdir() if p.is_dir()]:
        return ("Reviewed and complete. Run /dc:handoff-to-tc to package for Test "
                "Commander, or /dc:pr to open a pull request.")
    if not list((ws / "learning").glob("*.md")):
        return ("Handed off. Run /dc:learn to capture lessons from this cycle, "
                "then /dc:release to cut a version.")
    if not list((ws / "security").glob("*.md")):
        return ("Lessons captured. Run /dc:scan for a security scan (and "
                "/dc:ci to set up the CI pipeline) before cutting a release.")
    return ("Cycle complete. Run /dc:release to cut a version, or /dc:plan to "
            "start the next feature.")


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

The recommender reads only workspace state (no git calls); the /dc:branch
and /dc:pr suggestions are advice within the implement and handoff states,
not gates. Extended post-v0.2 from the original four-state chain to walk the
full lifecycle (design, branch, handoff/pr, learn, scan, release).

- [x] **Step 8: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py -v`
Expected: 12 passed.

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
the CI pipeline); and once lessons and a scan exist the cycle is complete,
so /dc:release or /dc:plan for the next feature.

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
   rather than re-deriving requirements. If a design doc or ADR exists under `.dev-commander/design/`, consume it too.
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
`.dev-commander/reviews/NNNN-plan-review-<slug>.md`, where NNNN is the
next zero-padded sequence number in the plan-review series, independent
of the code-review series. Give an overall verdict: ready, ready with
repairs, or not ready.
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
   NNNN is the next zero-padded sequence number in the code-review
   series, independent of the plan-review series (the two share the
   reviews/ directory but are numbered separately, distinguished by the
   `plan-review` infix), with a verdict:
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
description: Test Commander handoff for Dev Commander. Use when the user runs /dc:handoff-to-tc or asks to package what was built for testing. Assembles plans, increment records, and reviews into documents Test Commander's /tc:learn-from-docs and /tc:review-acceptance-criteria commands can ingest.
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

---

# v0.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalize Dev Commander from a Python-only inner loop into a general software development agent: a release workflow, multi-stack scaffolding (python, node-ts, go), an architecture/design phase, a branch-and-PR workflow, and governed lesson capture.

**Architecture:** Same skill-pack architecture as v0.1. One new Python helper (bump_version.py, per DC6); everything else is Markdown skills plus templates. The scaffold templates are reorganized into stack families under `templates/scaffold/<stack>/` with shared docs in `common/`. Two new workspace directories (`design/`, `learning/`) extend the `.dev-commander/` contract.

**Tech Stack:** Unchanged — Claude Code plugin format, Python 3.12, pdm, pytest, ruff, Make.

## v0.2 Global Constraints

All v0.1 Global Constraints still apply verbatim. Additions:

- Every stack family's Makefile must provide install, lint, test, build, run targets; the conventions (CHANGELOG/TODO/README, no emojis) are universal across stacks.
- A fresh scaffold of ANY stack must pass its own health check with zero manual editing: `make lint test build`. Where the build produces a run entrypoint (node-ts, go), the run target must point at it; `make run` itself need not be executed in the check when it would block on a server or start external services (`docker compose up`).
- New workspace directories keep the established artifact conventions: `NNNN-<slug>.md` with NNNN the next zero-padded sequence number.
- The EXPECTED dict in tests/test_dc_skills.py and the STACKS dict in tests/test_dc_scaffold.py grow one entry per task, keeping `make verify` green between tasks.

## v0.2 Decisions

| # | Decision |
| --- | --- |
| DC6 | Amends DC3: dc-release ships one Python helper (`bump_version.py`) inside the plugin, because version sync across manifests is mechanical and error-prone (proven by the v0.1 release fix wave). All other non-core skills remain Markdown-only. |
| DC7 | Scaffold templates are organized by stack family under `templates/scaffold/<stack>/`, with stack-agnostic docs under `templates/scaffold/common/`. v0.2 ships python, node-ts, and go. |
| DC8 | dc-design artifacts live under `.dev-commander/design/`. Design is optional per feature: small increments may go straight to /dc:plan. |
| DC9 | dc-branch never pushes or merges without explicit user direction; it prepares branches and PR descriptions. |
| DC10 | dc-learning promotion into project guidance requires human approval; candidate lessons never rewrite guidance automatically (mirrors tc-learning). |

## v0.2 File Structure (additions and moves)

```
plugins/dev-commander/
├── scripts/
│   └── bump_version.py            # NEW (DC6) — used by dc-release
├── templates/
│   ├── workspace/
│   │   ├── design/.gitkeep        # NEW (Task 15)
│   │   └── learning/.gitkeep      # NEW (Task 17)
│   └── scaffold/                  # RESTRUCTURED (Task 12)
│       ├── common/                # stack-agnostic docs
│       │   ├── README.md.tmpl
│       │   ├── CHANGELOG.md.tmpl
│       │   └── TODO.md.tmpl
│       ├── python/                # moved from flat layout
│       │   ├── Makefile.tmpl
│       │   ├── pyproject.toml.tmpl
│       │   ├── docker-compose.yml.tmpl
│       │   └── tests/test_smoke.py.tmpl
│       ├── node-ts/               # NEW (Task 13)
│       │   ├── Makefile.tmpl
│       │   ├── package.json.tmpl
│       │   ├── tsconfig.json.tmpl
│       │   ├── tsconfig.build.json.tmpl
│       │   ├── src/index.ts.tmpl
│       │   └── tests/smoke.test.ts.tmpl
│       └── go/                    # NEW (Task 14)
│           ├── Makefile.tmpl
│           ├── go.mod.tmpl
│           ├── main.go.tmpl
│           └── main_test.go.tmpl
└── skills/
    ├── dc-release/SKILL.md        # NEW (Task 11)
    ├── dc-design/SKILL.md         # NEW (Task 15)
    ├── dc-branch/SKILL.md         # NEW (Task 16)
    └── dc-learning/SKILL.md       # NEW (Task 17)

tests/
├── test_dc_release.py             # NEW (Task 11)
└── test_lifecycle_integration.py  # post-v0.2: end-to-end lifecycle contract
```

Workspace layout after v0.2 (`.dev-commander/`): project.md plus `journal/`, `plans/`, `increments/`, `reviews/`, `debug/`, `design/`, `learning/`, `handoff/`.

---

### Task 11: dc-release skill and bump_version helper (Phase 8)

**Files:**
- Create: `plugins/dev-commander/scripts/bump_version.py`
- Create: `plugins/dev-commander/skills/dc-release/SKILL.md`
- Create: `tests/test_dc_release.py`
- Modify: `tests/test_dc_skills.py` (append the dc-release entry to EXPECTED)

**Interfaces:**
- Consumes: dc-core's journal helper (referenced by SKILL.md step 8).
- Produces: CLI `bump_version.py <project-root> <version>` — updates the version field in pyproject.toml and package.json where present; prints one `updated <file>` line per file; exits 0 on success, 1 on invalid semver or when no version files were found.

- [x] **Step 1: Write the failing tests**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-release": ["/dc:release", "bump_version", "CHANGELOG"],
```

Create `tests/test_dc_release.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "dev-commander" / "scripts" / "bump_version.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True,
    )


def test_bumps_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0.1.0"\n')
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 0, result.stderr
    assert 'version = "0.2.0"' in (tmp_path / "pyproject.toml").read_text()


def test_bumps_package_json(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "x", "version": "0.1.0"}\n')
    result = run(tmp_path, "1.0.0")
    assert result.returncode == 0
    assert json.loads((tmp_path / "package.json").read_text())["version"] == "1.0.0"


def test_rejects_non_semver(tmp_path):
    (tmp_path / "pyproject.toml").write_text('version = "0.1.0"\n')
    result = run(tmp_path, "v2")
    assert result.returncode == 1


def test_fails_when_no_version_files(tmp_path):
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1


def test_bumps_project_section_not_first_version_line(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.other]\nversion = "9.9.9"\n\n[project]\nname = "x"\nversion = "0.1.0"\n'
    )
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 0, result.stderr
    text = (tmp_path / "pyproject.toml").read_text()
    assert '[tool.other]\nversion = "9.9.9"' in text
    assert 'version = "0.2.0"' in text


def test_reports_missing_project_version_field(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1
    assert "no project version field" in result.stdout


def test_invalid_package_json_fails_cleanly(tmp_path):
    (tmp_path / "package.json").write_text("{not json")
    result = run(tmp_path, "0.2.0")
    assert result.returncode == 1
    assert "not valid JSON" in result.stdout
    assert "Traceback" not in result.stderr
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_release.py "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-release]" -v`
Expected: FAIL — bump_version.py and SKILL.md do not exist.

- [x] **Step 3: Write bump_version.py**

```python
"""Bump the project version in pyproject.toml and package.json where present."""
import json
import re
import sys
from pathlib import Path


PROJECT_SECTION = re.compile(r"^\[project\]$\n(.*?)(?=^\[|\Z)", re.MULTILINE | re.DOTALL)


def bump(root: Path, version: str) -> list[str]:
    updated = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text()
        match = PROJECT_SECTION.search(text)
        if match:
            section, count = re.subn(
                r'^version = "[^"]+"', f'version = "{version}"',
                match.group(1), count=1, flags=re.MULTILINE,
            )
            if count:
                text = text[:match.start(1)] + section + text[match.end(1):]
                pyproject.write_text(text)
                updated.append("pyproject.toml")
            else:
                print("pyproject.toml has no project version field")
        else:
            print("pyproject.toml has no project version field")
    package = root / "package.json"
    if package.is_file():
        try:
            data = json.loads(package.read_text())
        except json.JSONDecodeError:
            print("package.json is not valid JSON")
        else:
            if "version" in data:
                data["version"] = version
                package.write_text(json.dumps(data, indent=2) + "\n")
                updated.append("package.json")
            else:
                print("package.json has no version field")
    return updated


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: bump_version.py <project-root> <version>")
        return 1
    root, version = Path(sys.argv[1]), sys.argv[2]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"not a semantic version: {version}")
        return 1
    no_candidates = not (root / "pyproject.toml").is_file() and not (root / "package.json").is_file()
    updated = bump(root, version)
    if not updated:
        if no_candidates:
            print("no version files found (pyproject.toml, package.json)")
        return 1
    for name in updated:
        print(f"updated {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Write dc-release SKILL.md**

```markdown
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
```

- [x] **Step 5: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_release.py "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-release]" -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 6: Commit**

Update CHANGELOG.md (Phase 8 section at top) and TODO.md (remove the Phase 8 line) in the same commit.

```bash
git add -A
git commit -m "feat: dc-release skill with bump_version helper (Phase 8)"
```

---

### Task 12: Multi-stack scaffold restructure — common + python families (Phase 9)

**Files:**
- Move: `plugins/dev-commander/templates/scaffold/{README,CHANGELOG,TODO}.md.tmpl` to `plugins/dev-commander/templates/scaffold/common/`
- Move: `plugins/dev-commander/templates/scaffold/{Makefile,pyproject.toml,docker-compose.yml}.tmpl` and `tests/test_smoke.py.tmpl` to `plugins/dev-commander/templates/scaffold/python/`
- Modify: `plugins/dev-commander/skills/dc-scaffold/SKILL.md` (full rewrite below)
- Modify: `tests/test_dc_scaffold.py` (full rewrite below)

**Interfaces:**
- Consumes: the v0.1 flat template set (moved, contents unchanged).
- Produces: the layout contract `templates/scaffold/common/` + `templates/scaffold/<stack>/` that Tasks 13-14 add families to, and the STACKS dict in tests/test_dc_scaffold.py they append to.

- [x] **Step 1: Rewrite the test file (failing first)**

Replace `tests/test_dc_scaffold.py` entirely with:

```python
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"

COMMON = ["README.md.tmpl", "CHANGELOG.md.tmpl", "TODO.md.tmpl"]

# Tasks 13-14 append entries as their stack families ship.
STACKS = {
    "python": [
        "Makefile.tmpl", "pyproject.toml.tmpl", "docker-compose.yml.tmpl",
        "tests/test_smoke.py.tmpl",
    ],
}


def test_common_templates_exist():
    for name in COMMON:
        assert (SCAFFOLD / "common" / name).is_file(), f"missing common/{name}"


@pytest.mark.parametrize("stack", STACKS)
def test_stack_family_complete(stack):
    for name in STACKS[stack]:
        assert (SCAFFOLD / stack / name).is_file(), f"missing {stack}/{name}"


@pytest.mark.parametrize("stack", STACKS)
def test_stack_makefile_has_required_targets(stack):
    text = (SCAFFOLD / stack / "Makefile.tmpl").read_text()
    for target in ["install:", "lint:", "test:", "build:", "run:"]:
        assert target in text, f"{stack}/Makefile.tmpl missing {target}"


def test_scaffold_root_has_only_family_dirs():
    entries = {p.name for p in SCAFFOLD.iterdir() if p.is_dir()}
    assert entries == {"common"} | set(STACKS)


def test_python_pyproject_uses_pdm():
    assert "pdm" in (SCAFFOLD / "python" / "pyproject.toml.tmpl").read_text()


def test_templates_use_placeholders():
    assert "{{project_name}}" in (SCAFFOLD / "common" / "README.md.tmpl").read_text()


def test_skill_exists():
    skill = ROOT / "plugins" / "dev-commander" / "skills" / "dc-scaffold" / "SKILL.md"
    assert skill.is_file()
    assert "/dc:scaffold" in skill.read_text()
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_scaffold.py -v`
Expected: FAIL — common/ and python/ directories do not exist yet.

- [x] **Step 3: Move the templates**

```bash
cd plugins/dev-commander/templates/scaffold
mkdir common python
git mv README.md.tmpl CHANGELOG.md.tmpl TODO.md.tmpl common/
git mv Makefile.tmpl pyproject.toml.tmpl docker-compose.yml.tmpl python/
git mv tests python/tests
cd -
```

Template contents are unchanged — only locations move.

- [x] **Step 4: Rewrite dc-scaffold SKILL.md**

Replace `plugins/dev-commander/skills/dc-scaffold/SKILL.md` entirely with:

```markdown
---
name: dc-scaffold
description: Project scaffolding for Dev Commander. Use when the user runs /dc:scaffold or asks to set up a new project. Offers stack families (e.g. python, node-ts, go) with a shared documentation set, generating a Makefile with install, lint, test, build, and run targets plus README, CHANGELOG, and TODO from bundled templates.
---

# dc-scaffold

Generates project scaffolding from templates bundled at
`<plugin-root>/templates/scaffold/`. Templates are organized as
`common/` (stack-agnostic docs) plus one directory per stack family.

## /dc:scaffold

1. Ask for the project name, a one-line description, and the stack if
   not provided. The name must be lowercase with hyphens. The
   available stacks are the subdirectories of `templates/scaffold/`
   other than `common`.
2. Write every template under `templates/scaffold/common/` and under
   the chosen stack's directory into the project at the same relative
   path with `.tmpl` stripped from the filename, substituting
   `{{project_name}}` and `{{project_description}}`.
3. Never overwrite an existing file. If a target exists, report it and
   skip it. List skipped files at the end.
4. Only include docker-compose.yml when the project needs local
   services; ask if unclear. Databases and system tools always run on
   docker locally. When skipping docker-compose.yml, also remove any
   `docker compose up -d` line from the generated Makefile's run
   target so `make run` still works.
5. Prove the scaffold is healthy before journaling: run the stack's
   install target, then `make lint test build` with zero manual
   editing. Where the build produces a run entrypoint (for example
   node-ts's `dist/index.js` or go's `bin/<name>`), confirm the run
   target points at it — run `make run` when it self-terminates, or
   run the built entrypoint directly when `make run` would block on a
   server or start external services (`docker compose up`). Then
   journal the scaffold decision with the dc-core journal helper.

Rules the generated project must satisfy regardless of stack: Make
targets for install, lint, test, build, run; no emojis anywhere;
README under 400 lines linking to CHANGELOG.md and TODO.md.
```

- [x] **Step 5: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_scaffold.py -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 6: Update this plan's v0.1 File Structure tree**

In the v0.1 File Structure section, replace the flat `scaffold/` subtree with the family layout shown in the v0.2 File Structure section (common/, python/ only at this point).

- [x] **Step 7: Commit**

Update CHANGELOG.md (Phase 9 section) and TODO.md (remove the Phase 9 line) in the same commit.

```bash
git add -A
git commit -m "feat: multi-stack scaffold layout with common and python families (Phase 9)"
```

---

### Task 13: node-ts scaffold family (Phase 10)

**Files:**
- Create: `plugins/dev-commander/templates/scaffold/node-ts/Makefile.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/node-ts/package.json.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/node-ts/tsconfig.json.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/node-ts/tsconfig.build.json.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/node-ts/src/index.ts.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/node-ts/tests/smoke.test.ts.tmpl`
- Modify: `tests/test_dc_scaffold.py` (append the node-ts entry to STACKS)

**Interfaces:**
- Consumes: the family layout and STACKS dict from Task 12.
- Produces: a complete node-ts family whose fresh scaffold passes `npm install && make lint test build` and whose built `dist/index.js` runs.

- [x] **Step 1: Add the node-ts case and verify it fails**

Append to `STACKS` in `tests/test_dc_scaffold.py`:

```python
    "node-ts": [
        "Makefile.tmpl", "package.json.tmpl", "tsconfig.json.tmpl",
        "tsconfig.build.json.tmpl", "src/index.ts.tmpl", "tests/smoke.test.ts.tmpl",
    ],
```

Run: `pdm run pytest "tests/test_dc_scaffold.py::test_stack_family_complete[node-ts]" -v`
Expected: FAIL — node-ts templates do not exist.

- [x] **Step 2: Write the templates**

`node-ts/Makefile.tmpl`:

```makefile
.PHONY: help install lint test build run

help:
	@echo "{{project_name}} - Make targets: install, lint, test, build, run"

install:
	npm install

lint:
	npm run lint

test:
	npm test

build:
	npm run build

run:
	npm start
```

`node-ts/package.json.tmpl`:

```json
{
  "name": "{{project_name}}",
  "version": "0.0.0",
  "description": "{{project_description}}",
  "type": "module",
  "scripts": {
    "lint": "tsc --noEmit",
    "test": "vitest run",
    "build": "tsc -p tsconfig.build.json",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

`node-ts/tsconfig.json.tmpl`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022", "WebWorker"],
    "types": ["node", "vitest/globals"],
    "outDir": "dist",
    "strict": true
  },
  "include": ["src", "tests"]
}
```

`node-ts/tsconfig.build.json.tmpl`:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "rootDir": "src"
  },
  "include": ["src"]
}
```

`node-ts/src/index.ts.tmpl`:

```typescript
export function greet(name: string): string {
  return `{{project_name}} greets ${name}`;
}
```

`node-ts/tests/smoke.test.ts.tmpl`:

```typescript
import { expect, test } from "vitest";
import { greet } from "../src/index.js";

test("scaffold is healthy", () => {
  expect(greet("world")).toContain("world");
});
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_scaffold.py -v && make verify`
Expected: all pass (node-ts parametrized cases included); verifier clean.

- [x] **Step 4: Prove a fresh node-ts scaffold is healthy**

In a scratch directory, copy the common and node-ts templates with `.tmpl` stripped (substituting `demo-app` for `{{project_name}}`), then run `npm install && make lint test build` and `node dist/index.js`.
Expected: lint (tsc) clean, 1 vitest test passes, `make build` emits `dist/index.js` (and no `dist/tests/`), and `node dist/index.js` loads and exits cleanly. Remove the scratch directory afterwards. If npm is unavailable in the environment, record that in the commit message body instead and note it for the reviewer.

- [x] **Step 5: Commit**

Update CHANGELOG.md (Phase 10 section) and TODO.md (remove the Phase 10 line) in the same commit.

```bash
git add -A
git commit -m "feat: node-ts scaffold family (Phase 10)"
```

---

### Task 14: go scaffold family (Phase 11)

**Files:**
- Create: `plugins/dev-commander/templates/scaffold/go/Makefile.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/go/go.mod.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/go/main.go.tmpl`
- Create: `plugins/dev-commander/templates/scaffold/go/main_test.go.tmpl`
- Modify: `tests/test_dc_scaffold.py` (append the go entry to STACKS)

**Interfaces:**
- Consumes: the family layout and STACKS dict from Task 12.
- Produces: a complete go family whose fresh scaffold passes `make lint test build run`.

- [x] **Step 1: Add the go case and verify it fails**

Append to `STACKS` in `tests/test_dc_scaffold.py`:

```python
    "go": [
        "Makefile.tmpl", "go.mod.tmpl", "main.go.tmpl", "main_test.go.tmpl",
    ],
```

Run: `pdm run pytest "tests/test_dc_scaffold.py::test_stack_family_complete[go]" -v`
Expected: FAIL — go templates do not exist.

- [x] **Step 2: Write the templates**

`go/Makefile.tmpl`:

```makefile
.PHONY: help install lint test build run

help:
	@echo "{{project_name}} - Make targets: install, lint, test, build, run"

install:
	go mod tidy

lint:
	go vet ./...

test:
	go test ./...

build:
	go build -o bin/{{project_name}} .

run:
	go run .
```

`go/go.mod.tmpl`:

```
module {{project_name}}

go 1.23
```

`go/main.go.tmpl`:

```go
package main

import "fmt"

// Greet returns a greeting for name.
func Greet(name string) string {
	return "{{project_name}} greets " + name
}

func main() {
	fmt.Println(Greet("world"))
}
```

`go/main_test.go.tmpl`:

```go
package main

import (
	"strings"
	"testing"
)

func TestScaffoldIsHealthy(t *testing.T) {
	if !strings.Contains(Greet("world"), "world") {
		t.Fatal("greeting missing name")
	}
}
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_scaffold.py -v && make verify`
Expected: all pass (go parametrized cases included); verifier clean.

- [x] **Step 4: Prove a fresh go scaffold is healthy**

In a scratch directory, copy the common and go templates with `.tmpl` stripped (substituting `demo-app` for `{{project_name}}`), then run `make lint test build run` (all self-terminating for go).
Expected: go vet clean, 1 test passes, `make build` produces `bin/demo-app`, and `make run` prints the greeting. Remove the scratch directory afterwards. If the go toolchain is unavailable in the environment, record that in the commit message body instead and note it for the reviewer.

- [x] **Step 5: Commit**

Update CHANGELOG.md (Phase 11 section) and TODO.md (remove the Phase 11 line) in the same commit.

```bash
git add -A
git commit -m "feat: go scaffold family (Phase 11)"
```

---

### Task 15: dc-design skill and design/ workspace directory (Phase 12)

**Files:**
- Create: `plugins/dev-commander/skills/dc-design/SKILL.md`
- Create: `plugins/dev-commander/templates/workspace/design/.gitkeep`
- Modify: `plugins/dev-commander/scripts/status.py` (add "design" to DIRS)
- Modify: `tests/test_dc_core.py` (add "design" to DIRS)
- Modify: `tests/test_dc_skills.py` (append the dc-design entry to EXPECTED)

**Interfaces:**
- Consumes: the workspace contract from Task 3; the EXPECTED dict from Task 5.
- Produces: design docs at `.dev-commander/design/NNNN-<slug>.md` and ADRs at `.dev-commander/design/adr-NNNN-<slug>.md` that /dc:plan consumes as input.

- [x] **Step 1: Add the failing test cases**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-design": ["/dc:design", "design/", "ADR"],
```

In `tests/test_dc_core.py`, change the DIRS constant to:

```python
DIRS = ["journal", "plans", "increments", "reviews", "debug", "design", "handoff"]
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-design]" tests/test_dc_core.py::test_init_creates_workspace -v`
Expected: both FAIL — SKILL.md and the design/ template directory do not exist.

- [x] **Step 2: Implement**

Create `plugins/dev-commander/templates/workspace/design/.gitkeep` (empty file).

In `plugins/dev-commander/scripts/status.py`, change the DIRS constant to:

```python
DIRS = ["journal", "plans", "increments", "reviews", "debug", "design", "handoff"]
```

Create `plugins/dev-commander/skills/dc-design/SKILL.md`:

```markdown
---
name: dc-design
description: Architecture design and decision records for Dev Commander. Use when the user runs /dc:design or /dc:adr, or asks for a design document or an architecture decision record before planning a feature. Produces design docs and ADRs under .dev-commander/design/ that dc-plan consumes.
---

# dc-design

Fills the lifecycle phase between requirements and planning. Design is
optional per feature: small increments may go straight to /dc:plan;
features with architectural weight get a design doc or an ADR first.

## /dc:design

1. Gather inputs: the feature request, BRD, or user story, plus the
   parts of the codebase the feature touches.
2. Write a short design doc to `.dev-commander/design/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number, with sections:
   Goal (one sentence), Context, Approach (2-3 paragraphs),
   Alternatives considered with one-line reasons for rejection,
   Interfaces (exact names and types other components will consume),
   and Risks.
3. Keep it short. A design doc that exceeds two screens should be
   split or simplified before planning proceeds.
4. Recommend /dc:plan next, pointing it at the design doc.

## /dc:adr

Record one architecture decision at
`.dev-commander/design/adr-NNNN-<slug>.md`, where NNNN is the next
zero-padded sequence number in the adr- series, independent of the design-doc sequence, with sections: Status (proposed,
accepted, superseded), Context, Decision, Consequences. One decision
per record. ADRs are never deleted; a reversed decision gets a new
ADR that names and supersedes the old one.
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_dc_skills.py -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 4: Update the workspace layout in this plan**

In both workspace-layout listings (v0.1 section and the v0.2 note above), confirm `design/` appears between `debug/` and `handoff/`.

- [x] **Step 5: Commit**

Update CHANGELOG.md (Phase 12 section) and TODO.md (remove the Phase 12 line) in the same commit.

```bash
git add -A
git commit -m "feat: dc-design skill and design workspace directory (Phase 12)"
```

---

### Task 16: dc-branch skill (Phase 13)

**Files:**
- Create: `plugins/dev-commander/skills/dc-branch/SKILL.md`
- Modify: `tests/test_dc_skills.py` (append the dc-branch entry to EXPECTED)

**Interfaces:**
- Consumes: plan filenames from dc-plan (`NNNN-<slug>.md`), increment records from dc-implement, review reports from dc-review.
- Produces: branch naming convention `dc/NNNN-<slug>` matching the plan filename.

- [x] **Step 1: Add the dc-branch case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-branch": ["/dc:branch", "/dc:pr", "increment records"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-branch]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-branch SKILL.md**

```markdown
---
name: dc-branch
description: Branch and pull-request workflow for Dev Commander. Use when the user runs /dc:branch or /dc:pr, or asks to start a feature branch for a plan or open a pull request from completed increments. Prepares branches and PR descriptions; never pushes or merges without explicit user direction.
---

# dc-branch

Team-development workflow around plans. Prepares branches and pull
requests; the user decides when anything leaves the machine (DC9).

## /dc:branch

1. Identify the plan the work belongs to: the active plan by default,
   or the plan the user names.
2. Create and switch to a branch named `dc/NNNN-<slug>` matching the
   plan's filename. If the branch already exists, switch to it.
3. Journal the branch creation with the dc-core journal helper.
   Subsequent /dc:implement increments commit to this branch.

## /dc:pr

1. Confirm the branch's plan has no unchecked increments and the
   latest review verdict is approve, or approve with repairs that
   have been applied.
2. Draft the pull request description from the workspace artifacts:
   a summary from the plan header, a change list and test evidence
   from the increment records, and outcomes from the review reports.
3. Show the draft to the user. Only after they approve: push the
   branch and open the PR with `gh pr create`. Never merge; merging
   is the user's decision in their review tool.
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-branch]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

Update CHANGELOG.md (Phase 13 section) and TODO.md (remove the Phase 13 line) in the same commit.

```bash
git add -A
git commit -m "feat: dc-branch skill (Phase 13)"
```

---

### Task 17: dc-learning skill and learning/ workspace directory (Phase 14)

**Files:**
- Create: `plugins/dev-commander/skills/dc-learning/SKILL.md`
- Create: `plugins/dev-commander/templates/workspace/learning/.gitkeep`
- Modify: `plugins/dev-commander/scripts/status.py` (add "learning" to DIRS)
- Modify: `tests/test_dc_core.py` (add "learning" to DIRS)
- Modify: `tests/test_dc_skills.py` (append the dc-learning entry to EXPECTED)

**Interfaces:**
- Consumes: the workspace contract; dc-debug investigations and dc-review reports as lesson sources.
- Produces: lesson files at `.dev-commander/learning/NNNN-<slug>.md` carrying a `Status:` line (candidate, accepted, rejected).

- [x] **Step 1: Add the failing test cases**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-learning": ["/dc:learn", "learning/", "candidate"],
```

In `tests/test_dc_core.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "handoff",
]
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-learning]" tests/test_dc_core.py::test_init_creates_workspace -v`
Expected: both FAIL — SKILL.md and the learning/ template directory do not exist.

- [x] **Step 2: Implement**

Create `plugins/dev-commander/templates/workspace/learning/.gitkeep` (empty file).

In `plugins/dev-commander/scripts/status.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "handoff",
]
```

Create `plugins/dev-commander/skills/dc-learning/SKILL.md`:

```markdown
---
name: dc-learning
description: Governed lesson capture for Dev Commander. Use when the user runs /dc:learn or /dc:promote-lesson, or asks to record a lesson from a debugging session, review, or release. Captures candidate lessons under .dev-commander/learning/ and promotes them into project guidance only with human approval.
---

# dc-learning

The improvement loop. Lessons start as candidates and change project
guidance only when a human approves the promotion (DC10).

## /dc:learn

1. Capture one lesson at `.dev-commander/learning/NNNN-<slug>.md`,
   where NNNN is the next zero-padded sequence number, with sections:
   Status (candidate), Source (the debug report, review, or event
   that produced it), Lesson (one paragraph), and Proposed guidance
   (the exact wording that would be added to the project's agent
   file or docs if accepted).
2. Candidates change nothing by themselves. Do not edit any guidance
   file during capture.

## /dc:promote-lesson

1. Show the named candidate (or list all candidates if none named)
   and its proposed guidance to the user.
2. Only with the user's explicit approval: apply the proposed
   guidance edit, set the lesson's Status to accepted, and journal
   the promotion with the dc-core journal helper.
3. If the user declines, set Status to rejected and record their
   reason in the lesson file.
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_dc_skills.py -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 4: Update the workspace layout in this plan**

In both workspace-layout listings, confirm `learning/` appears between `design/` and `handoff/`.

- [x] **Step 5: Commit**

Update CHANGELOG.md (Phase 14 section) and TODO.md (remove the Phase 14 line) in the same commit.

```bash
git add -A
git commit -m "feat: dc-learning skill and learning workspace directory (Phase 14)"
```

---

### Task 18: v0.2 release, dogfooding dc-release (Phase 15)

**Files:**
- Modify: `pyproject.toml`, `.claude-plugin/marketplace.json`, `plugins/dev-commander/.claude-plugin/plugin.json` (version 0.2.0)
- Modify: `README.md` (status line), `CHANGELOG.md` (v0.2.0 section)

**Interfaces:**
- Consumes: everything above; follows dc-release's own /dc:release steps as the process.
- Produces: tagged v0.2.0 on origin/main; installed plugin at 0.2.0.

- [x] **Step 1: Verify from a clean tree**

Run: `git status --short` (expect empty) and `make verify`.
Expected: clean tree; lint clean, all tests pass, verifier 0 problems.

- [x] **Step 2: Bump versions**

Run: `python3 plugins/dev-commander/scripts/bump_version.py . 0.2.0`
Expected: `updated pyproject.toml`.
Then set `"version": "0.2.0"` in `.claude-plugin/marketplace.json` (plugins entry) and `plugins/dev-commander/.claude-plugin/plugin.json` — every statement of the version must agree.

- [x] **Step 3: Update docs**

Add a `## v0.2.0` section at the top of CHANGELOG.md summarizing Phases 8-15. Set the README status line to: Phases 0-15 complete; v0.2 skill set shipped. Update the README command table with the new commands (/dc:release, /dc:design, /dc:adr, /dc:branch, /dc:pr, /dc:learn, /dc:promote-lesson).

- [x] **Step 4: Verify, validate, commit, tag, push**

Run: `make verify && claude plugin validate . && claude plugin validate plugins/dev-commander`
Expected: all clean.

```bash
git add -A
git commit -m "chore: release v0.2.0"
git tag v0.2.0
git push --follow-tags
```

- [x] **Step 5: Refresh the installed plugin and smoke-test**

Run: `claude plugin uninstall dev-commander && claude plugin install dev-commander@dev-commander-marketplace`
Then confirm the installed cache contains the four new skills and `bump_version.py`, and journal the release with the dc-core journal helper in a scratch workspace check.

## v0.2 To Do

Tracked in [TODO.md](../TODO.md).

## v0.2 Completed

All eight tasks shipped 2026-07-21:

- Task 11: dc-release skill and bump_version helper (3f69247)
- Task 12: Multi-stack scaffold restructure — common + python families (5a91fc8)
- Task 13: node-ts scaffold family (d366fb4, fix b8ba475, fix ede2975)
- Task 14: go scaffold family (6e55b73)
- Task 15: dc-design skill and design workspace directory (9fda61f)
- Task 16: dc-branch skill (7262781)
- Task 17: dc-learning skill and learning workspace directory (87393f3, fix f605c12)
- Task 18: v0.2 release, dogfooding dc-release (this commit, tagged v0.2.0)

---

# v0.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend Dev Commander past release into continuous integration: a skill that generates a GitHub Actions PR gate (dc-ci) and a skill that runs dependency and secret scans on demand and reports (dc-secscan), keeping the skill-pack architecture and staying stack-agnostic.

**Architecture:** Two Markdown-only skills (no Python helpers, per DC11). dc-secscan runs the stack's native dependency scanner plus gitleaks and writes a report to a new `.dev-commander/security/` directory; dc-ci writes a GitHub Actions workflow from a per-stack template family that runs the scaffold's uniform Make targets and the scan. Both skills detect the stack from project files. The lifecycle recommender gains one security check.

**Tech Stack:** Unchanged — Claude Code plugin format, Python 3.12, pdm, pytest, ruff, Make. One new dev dependency: pyyaml (to validate generated workflow YAML in tests).

**Design spec:** [docs/superpowers/specs/2026-07-22-v0.3-ci-security-design.md](../docs/superpowers/specs/2026-07-22-v0.3-ci-security-design.md).

## v0.3 Global Constraints

All v0.1 and v0.2 Global Constraints still apply verbatim. Additions:

- dc-ci and dc-secscan are Markdown-only; the agent runs scanners and writes config by following each SKILL.md. No scanners or CI tools are vendored (DC11).
- GitHub Actions is the only CI provider in v0.3 (DC12).
- The generated workflow triggers on `push` and `pull_request`, runs `make install`, `make lint`, `make test`, `make build`, then the dependency and secret scans; lint/test/build/scan failures gate the build (DC13).
- The Make targets a CI template names must all exist in that stack's scaffold `Makefile.tmpl`.
- The `.dev-commander/` workspace grows to nine directories with `security/`, inserted before `handoff`.

## v0.3 Decisions

| # | Decision |
| --- | --- |
| DC11 | dc-ci and dc-secscan are Markdown-only, extending DC3. No scanners or CI tools are vendored; the agent runs the project's stack-native tools and writes config. |
| DC12 | GitHub Actions is the only CI provider in v0.3. Other providers are deferred, structured as `templates/ci/<provider>/` if added. |
| DC13 | Security gate: the build fails on known dependency vulnerabilities (high or critical where the scanner supports a severity threshold, e.g. `npm audit --audit-level=high`; pip-audit and govulncheck fail on any known vulnerability) and on any committed secret. SAST is deferred. |
| DC14 | dc-secscan degrades gracefully when a scanner is absent: it reports the install command, continues with the available scanners, and records which ran. |

## v0.3 File Structure (additions)

```
plugins/dev-commander/
├── templates/
│   ├── workspace/
│   │   └── security/.gitkeep       # NEW (Task 19)
│   └── ci/                         # NEW (Task 21)
│       └── github/
│           ├── python/ci.yml.tmpl
│           ├── node-ts/ci.yml.tmpl
│           └── go/ci.yml.tmpl
└── skills/
    ├── dc-secscan/SKILL.md         # NEW (Task 20)
    └── dc-ci/SKILL.md              # NEW (Task 22)

tests/
└── test_dc_ci.py                   # NEW (Task 21)
```

Workspace layout after v0.3 (`.dev-commander/`): project.md plus `journal/`, `plans/`, `increments/`, `reviews/`, `debug/`, `design/`, `learning/`, `security/`, `handoff/`.

---

### Task 19: security/ workspace directory (Phase 16)

**Files:**
- Create: `plugins/dev-commander/templates/workspace/security/.gitkeep`
- Modify: `plugins/dev-commander/scripts/status.py` (DIRS)
- Modify: `tests/test_dc_core.py` (DIRS)
- Modify: `tests/test_lifecycle_integration.py` (WORKSPACE_DIRS)

**Interfaces:**
- Consumes: the workspace contract from Task 3; `init_workspace.py` copies the template tree recursively, so adding the directory to the template is all init needs.
- Produces: the `.dev-commander/security/` directory (holding `NNNN-<slug>.md` scan reports) that dc-secscan (Task 20) writes into and next_step (Task 23) reads.

- [x] **Step 1: Update the DIRS constant in the two test files (failing first)**

In `tests/test_dc_core.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff",
]
```

In `tests/test_lifecycle_integration.py`, change the WORKSPACE_DIRS constant to:

```python
WORKSPACE_DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff",
]
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_core.py::test_init_creates_workspace tests/test_lifecycle_integration.py -v`
Expected: FAIL — `security/` is asserted but the template does not create it yet.

- [x] **Step 3: Create the template directory and update status.py**

Create `plugins/dev-commander/templates/workspace/security/.gitkeep` (empty file).

In `plugins/dev-commander/scripts/status.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff",
]
```

- [x] **Step 4: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_lifecycle_integration.py -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 5: Update the workspace layout in this plan**

In the v0.1 and v0.2 workspace-layout listings, confirm `security/` appears between `learning/` and `handoff/`.

- [x] **Step 6: Commit**

Update CHANGELOG.md (a Phase 16 section at the top) and TODO.md is unchanged (v0.3 was tracked as a single "Later" line, removed in Task 24). Commit:

```bash
git add -A
git commit -m "feat: security/ workspace directory (Phase 16)"
```

---

### Task 20: dc-secscan skill (Phase 17)

**Files:**
- Create: `plugins/dev-commander/skills/dc-secscan/SKILL.md`
- Modify: `tests/test_dc_skills.py` (append the dc-secscan entry to EXPECTED)

**Interfaces:**
- Consumes: the `security/` directory from Task 19.
- Produces: scan reports at `.dev-commander/security/NNNN-<slug>.md`; the canonical per-stack scan commands (`pip-audit`, `npm audit --audit-level=high`, `govulncheck ./...`, `gitleaks detect`) that the CI templates (Task 21) embed.

- [x] **Step 1: Add the dc-secscan case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-secscan": ["/dc:scan", "security/", "gitleaks"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-secscan]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-secscan SKILL.md**

```markdown
---
name: dc-secscan
description: Security scanning for Dev Commander. Use when the user runs /dc:scan or asks to check for vulnerable dependencies or committed secrets. Runs the project's stack-native dependency scanner and a secret scan, writes a report under .dev-commander/security/, and supplies the scan step dc-ci embeds in the pipeline.
---

# dc-secscan

Runs security scans on demand and reports. It never fixes anything: it
finds and recommends, and a dependency upgrade becomes a /dc:plan
follow-up.

## Stack detection

Infer the stack from project files: `pyproject.toml` present means python,
`package.json` means node-ts, `go.mod` means go. If none or more than one
is present, ask the user which stack rather than guessing.

## /dc:scan

1. Detect the stack.
2. Run the dependency scanner for the stack and the universal secret scan:
   - python: `pip-audit` (against the installed environment or the
     exported requirements).
   - node-ts: `npm audit --audit-level=high`.
   - go: `govulncheck ./...`.
   - secrets, all stacks: `gitleaks detect` over the repository.
3. If a scanner is not installed, report the install command (for example
   `pip install pip-audit`,
   `go install golang.org/x/vuln/cmd/govulncheck@latest`, or the gitleaks
   release page) and continue with the scanners that are available. Never
   crash on a missing tool.
4. Write a report to `.dev-commander/security/NNNN-<slug>.md`, where NNNN is
   the next zero-padded sequence number, with: the scanners that ran,
   findings grouped by severity (the vulnerable package, or the file and
   line for a secret, plus the advisory reference), and a verdict — clean,
   or issues found.
5. Severity and the gate: a high or critical dependency vulnerability, or
   any committed secret, is a gating finding; lower-severity dependency
   findings are informational. Scanners without a severity threshold
   (pip-audit, govulncheck) report every known vulnerability; treat those
   as gating.
6. Never edit dependencies or code. Recommend the fix (a version bump, a
   removed secret) and let the user decide, or open a /dc:plan for it.

## The CI scan step

dc-secscan is the single source of truth for how to scan each stack. dc-ci
embeds the dependency-scan commands from step 2 verbatim; for secret
scanning it runs the official gitleaks GitHub Action, the same gitleaks
engine as the local `gitleaks detect`. Local scans and the pipeline check
the same things.
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-secscan]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

Update CHANGELOG.md (Phase 17 section) in the same commit.

```bash
git add -A
git commit -m "feat: dc-secscan skill (Phase 17)"
```

---

### Task 21: CI template family and test_dc_ci.py (Phase 18)

**Files:**
- Create: `plugins/dev-commander/templates/ci/github/python/ci.yml.tmpl`
- Create: `plugins/dev-commander/templates/ci/github/node-ts/ci.yml.tmpl`
- Create: `plugins/dev-commander/templates/ci/github/go/ci.yml.tmpl`
- Modify: `pyproject.toml` (add pyyaml to the dev dependency group)
- Create: `tests/test_dc_ci.py`

**Interfaces:**
- Consumes: the scan commands documented by dc-secscan (Task 20); the scaffold `Makefile.tmpl` targets from Tasks 12-14.
- Produces: the template family `templates/ci/github/<stack>/ci.yml.tmpl` that dc-ci (Task 22) reads. Each template substitutes only `{{project_name}}`.

- [x] **Step 1: Add pyyaml and write the failing tests**

In `pyproject.toml`, change the dev dependency group to:

```toml
[dependency-groups]
dev = [
    "ruff>=0.6",
    "pytest>=8.0",
    "pyyaml>=6.0",
]
```

Run `pdm install` so pyyaml is available and `pdm.lock` updates.

Create `tests/test_dc_ci.py`:

```python
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
CI = ROOT / "plugins" / "dev-commander" / "templates" / "ci" / "github"
SCAFFOLD = ROOT / "plugins" / "dev-commander" / "templates" / "scaffold"
STACKS = ["python", "node-ts", "go"]
DEP_SCANNER = {"python": "pip-audit", "node-ts": "npm audit", "go": "govulncheck"}


def _load(stack):
    text = (CI / stack / "ci.yml.tmpl").read_text().replace("{{project_name}}", "demo-app")
    return text, yaml.safe_load(text)


@pytest.mark.parametrize("stack", STACKS)
def test_ci_template_exists(stack):
    assert (CI / stack / "ci.yml.tmpl").is_file(), f"missing {stack} CI template"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_template_is_valid_yaml(stack):
    _text, doc = _load(stack)
    assert isinstance(doc, dict)


@pytest.mark.parametrize("stack", STACKS)
def test_ci_triggers_on_push_and_pull_request(stack):
    _text, doc = _load(stack)
    # PyYAML parses a bare `on:` key as the boolean True (YAML 1.1).
    triggers = doc.get("on", doc.get(True))
    assert "push" in triggers and "pull_request" in triggers


@pytest.mark.parametrize("stack", STACKS)
def test_ci_runs_uniform_make_targets(stack):
    text, _doc = _load(stack)
    for target in ["make install", "make lint", "make test", "make build"]:
        assert target in text, f"{stack} CI missing '{target}'"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_includes_dependency_and_secret_scanners(stack):
    text, _doc = _load(stack)
    assert DEP_SCANNER[stack] in text, f"{stack} CI missing {DEP_SCANNER[stack]}"
    assert "gitleaks" in text, f"{stack} CI missing gitleaks"


@pytest.mark.parametrize("stack", STACKS)
def test_ci_make_targets_exist_in_scaffold(stack):
    text, _doc = _load(stack)
    makefile = (SCAFFOLD / stack / "Makefile.tmpl").read_text()
    for target in ["install", "lint", "test", "build"]:
        if f"make {target}" in text:
            assert f"{target}:" in makefile, (
                f"{stack} CI runs 'make {target}' but its Makefile.tmpl lacks it"
            )


@pytest.mark.parametrize("stack", STACKS)
def test_ci_has_no_unsubstituted_placeholders(stack):
    text, _doc = _load(stack)
    # Our mustache placeholders all start with {{project ; GitHub Actions
    # ${{ ... }} expressions are legitimate and must not trip this.
    assert "{{project" not in text, f"{stack} CI has an unsubstituted placeholder"
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_ci.py -v`
Expected: FAIL — the CI templates do not exist.

- [x] **Step 3: Write the three CI templates**

`plugins/dev-commander/templates/ci/github/python/ci.yml.tmpl`:

```yaml
name: {{project_name}} CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pdm
      - run: make install
      - run: make lint
      - run: make test
      - run: make build
      - name: dependency scan
        run: |
          pip install pip-audit
          pdm export -o requirements.txt --without-hashes
          pip-audit -r requirements.txt
      - name: secret scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Organizations must also set a GITLEAKS_LICENSE secret.
```

`plugins/dev-commander/templates/ci/github/node-ts/ci.yml.tmpl`:

```yaml
name: {{project_name}} CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: make install
      - run: make lint
      - run: make test
      - run: make build
      - name: dependency scan
        run: npm audit --audit-level=high
      - name: secret scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Organizations must also set a GITLEAKS_LICENSE secret.
```

`plugins/dev-commander/templates/ci/github/go/ci.yml.tmpl`:

```yaml
name: {{project_name}} CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.23"
      - run: make install
      - run: make lint
      - run: make test
      - run: make build
      - name: dependency scan
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...
      - name: secret scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Organizations must also set a GITLEAKS_LICENSE secret.
```

- [x] **Step 4: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_ci.py -v && make verify`
Expected: all 21 parametrized cases pass; verifier clean.

- [x] **Step 5: Commit**

Update CHANGELOG.md (Phase 18 section) in the same commit. `pdm.lock` changed when pyyaml was added; include it.

```bash
git add -A
git commit -m "feat: GitHub Actions CI template family and test_dc_ci (Phase 18)"
```

---

### Task 22: dc-ci skill (Phase 19)

**Files:**
- Create: `plugins/dev-commander/skills/dc-ci/SKILL.md`
- Modify: `tests/test_dc_skills.py` (append the dc-ci entry to EXPECTED)

**Interfaces:**
- Consumes: the CI template family from Task 21.
- Produces: the `/dc:ci` command that writes `.github/workflows/ci.yml` into a project.

- [x] **Step 1: Add the dc-ci case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-ci": ["/dc:ci", ".github/workflows", "ci.yml"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-ci]" -v`
Expected: FAIL — missing SKILL.md.

- [x] **Step 2: Write dc-ci SKILL.md**

```markdown
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
```

- [x] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-ci]" -v && make verify`
Expected: pass; verifier clean.

- [x] **Step 4: Commit**

Update CHANGELOG.md (Phase 19 section) in the same commit.

```bash
git add -A
git commit -m "feat: dc-ci skill (Phase 19)"
```

---

### Task 23: next_step /dc:scan recommendation (Phase 20)

**Files:**
- Modify: `plugins/dev-commander/scripts/next_step.py` (add the security check)
- Modify: `tests/test_dc_core.py` (new /dc:scan test; fix the cycle-complete test)
- Modify: `tests/test_lifecycle_integration.py` (add a security report before the cycle-complete assertion)
- Modify: `planning/plan.md` (sync the Task 3 next_step.py mirror and the /dc:next SKILL block)

**Interfaces:**
- Consumes: the `security/` directory from Task 19.
- Produces: a lifecycle state that recommends `/dc:scan` when the cycle is otherwise complete but no scan report exists.

- [x] **Step 1: Update the affected tests (failing first)**

In `tests/test_dc_core.py`, the existing `test_next_recommends_release_when_cycle_complete` must first write a security report so it still reaches the cycle-complete state, and a new test covers the scan state. Replace `test_next_recommends_release_when_cycle_complete` with these two functions:

```python
def test_next_recommends_scan_when_no_security_report(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    result = run("next_step.py", tmp_path)
    assert "/dc:scan" in result.stdout


def test_next_recommends_release_when_cycle_complete(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    result = run("next_step.py", tmp_path)
    assert "Cycle complete" in result.stdout
    assert "/dc:release" in result.stdout
```

In `tests/test_lifecycle_integration.py`, in `test_full_lifecycle`, insert a security-report step immediately before the final "journal" block (after the lesson is written and before the `journal.py` call). Replace the lesson-and-journal section:

```python
    # learn (dc-learning): a captured lesson leaves one hardening step.
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    assert "/dc:scan" in run("next_step.py", tmp_path).stdout

    # scan (dc-secscan): a security report completes the cycle.
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    final = run("next_step.py", tmp_path)
    assert "Cycle complete" in final.stdout
    assert "/dc:release" in final.stdout

    # journal (dc-core): an entry is written and counted.
    assert run("journal.py", tmp_path, "Shipped the feature").returncode == 0
    end = run("status.py", tmp_path)
    assert "journal: 1" in end.stdout
    assert "plans: 1" in end.stdout
    assert "increments: 1" in end.stdout
    # reviews counts both the code review and the plan-review file.
    assert "reviews: 2" in end.stdout
    assert "learning: 1" in end.stdout
    assert "security: 1" in end.stdout
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pdm run pytest tests/test_dc_core.py::test_next_recommends_scan_when_no_security_report tests/test_lifecycle_integration.py -v`
Expected: FAIL — next_step.py never recommends /dc:scan yet, so the scan-state assertions fail.

- [x] **Step 3: Add the security check to next_step.py**

In `plugins/dev-commander/scripts/next_step.py`, replace the final learning check and terminal return:

```python
    if not list((ws / "learning").glob("*.md")):
        return ("Handed off. Run /dc:learn to capture lessons from this cycle, "
                "then /dc:release to cut a version.")
    return ("Cycle complete. Run /dc:release to cut a version, or /dc:plan to "
            "start the next feature.")
```

with:

```python
    if not list((ws / "learning").glob("*.md")):
        return ("Handed off. Run /dc:learn to capture lessons from this cycle, "
                "then /dc:release to cut a version.")
    if not list((ws / "security").glob("*.md")):
        return ("Lessons captured. Run /dc:scan for a security scan (and "
                "/dc:ci to set up the CI pipeline) before cutting a release.")
    return ("Cycle complete. Run /dc:release to cut a version, or /dc:plan to "
            "start the next feature.")
```

- [x] **Step 4: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_lifecycle_integration.py -v && make verify`
Expected: all pass; verifier clean.

- [x] **Step 5: Sync the plan mirrors**

In `planning/plan.md`, update the Task 3 `next_step.py` code block (Step 7) to include the new security check, and update the `/dc:next` description in the Task 3 SKILL.md block (Step 9) to mention the security state. Match the shipped code and SKILL.md exactly.

- [x] **Step 6: Commit**

Update CHANGELOG.md (Phase 20 section) in the same commit.

```bash
git add -A
git commit -m "feat: next_step recommends /dc:scan before release (Phase 20)"
```

---

### Task 24: v0.3 docs and release (Phase 21)

**Files:**
- Modify: `README.md` (command table, status line)
- Modify: `AGENTS.md` (identity prose, DC range)
- Modify: `CHANGELOG.md` (v0.3.0 section)
- Modify: `pyproject.toml`, `.claude-plugin/marketplace.json`, `plugins/dev-commander/.claude-plugin/plugin.json` (version 0.3.0)
- Modify: `TODO.md` (remove the CI/CD line)

**Interfaces:**
- Consumes: everything above; follows dc-release's /dc:release process.
- Produces: tagged v0.3.0 on origin; installed plugin at 0.3.0.

- [x] **Step 1: Update the README command table and status line**

Add rows to the command table in `README.md`:

```markdown
| /dc:scan | dc-secscan | Run dependency and secret scans, report findings |
| /dc:ci | dc-ci | Generate a GitHub Actions PR gate |
```

Set the README status line to: `Status: Phases 0-21 complete; v0.3.0 shipped.`

- [x] **Step 2: Update AGENTS.md identity prose**

In `AGENTS.md`, extend the Project identity paragraph's skill enumeration to name the two new skills — "security scanning (dc-secscan)" and "CI pipeline generation (dc-ci)" — and change "Decisions (DC1-DC10)" to "Decisions (DC1-DC14)".

- [x] **Step 3: Update both manifest descriptions**

In `.claude-plugin/marketplace.json` and `plugins/dev-commander/.claude-plugin/plugin.json`, extend the `description` to mention security scanning and CI pipeline generation.

- [x] **Step 4: Bump the version to 0.3.0**

Run: `python3 plugins/dev-commander/scripts/bump_version.py . 0.3.0`
Expected: `updated pyproject.toml`.
Then set `"version": "0.3.0"` in `.claude-plugin/marketplace.json` (plugins entry) and `plugins/dev-commander/.claude-plugin/plugin.json`. Confirm all three agree.

- [x] **Step 5: Add the CHANGELOG v0.3.0 section and clear the TODO line**

Add a `## v0.3.0` section at the top of `CHANGELOG.md` summarizing Phases 16-21. In `TODO.md`, remove the line `- CI/CD workflow generation and dependency/security scanning skills.`

- [x] **Step 6: Verify, commit, tag, push**

Run: `make verify && claude plugin validate . && claude plugin validate plugins/dev-commander`
Expected: all clean.

```bash
git add -A
git commit -m "chore: release v0.3.0"
git tag -a v0.3.0 -m "release v0.3.0"
git push origin main
git push origin v0.3.0
```

- [x] **Step 7: Refresh and confirm the installed plugin**

Run: `claude plugin uninstall dev-commander && claude plugin install dev-commander@dev-commander-marketplace`
Then confirm the installed cache carries dc-secscan, dc-ci, and the `templates/ci/github/` family, and that the active install path is 0.3.0.

- [x] **Step 8: Check off this plan's checkboxes and record completion**

In `planning/plan.md`, check off the v0.3 task checkboxes and add a `## v0.3 Completed` section listing Tasks 19-24 with their commit SHAs and today's date. Commit as `docs: v0.3 completion record`.

## v0.3 To Do

Tracked in [TODO.md](../TODO.md). Deferred beyond v0.3: continuous deployment to environments, publishing build artifacts on a release tag, CI providers other than GitHub Actions, and SAST (bandit, gosec, semgrep).

## v0.3 Completed

All six tasks shipped 2026-07-22:

- Task 19: security/ workspace directory (4779532)
- Task 20: dc-secscan skill (fd0fd83)
- Task 21: CI template family and test_dc_ci.py (792322e, fix aed91e8, docs fdc5ec1)
- Task 22: dc-ci skill (ec6132f)
- Task 23: next_step /dc:scan recommendation (db3b200, docs fix bff1ccd)
- Task 24: v0.3 docs and release, dogfooding dc-release (93fbc19, tagged v0.3.0)

---

# v0.4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend Dev Commander past a tagged release into shipping running software: two skills that build and publish a container image (dc-publish) and deploy it to a self-hosted host over SSH (dc-deploy), plus a generated release workflow that automates build, push, and deploy on a version tag.

**Architecture:** Two Markdown-only skills unified by one artifact — the container image. Only the Dockerfile is stack-specific; the production compose file and the release workflow are stack-agnostic because the Dockerfile encapsulates the stack. A new `deployments/` workspace directory records publish and deploy events. Templates ship in the plugin under `templates/docker/<stack>/` and `templates/deploy/`.

**Tech Stack:** Unchanged — Claude Code plugin format, Python 3.12, pdm, pytest, ruff, Make, pyyaml (already a dev dependency). Generated artifacts target Docker, GHCR, and GitHub Actions.

## v0.4 Global Constraints

All prior Global Constraints still apply verbatim. Additions:

- The container image is the deployment artifact. The image reference convention is `ghcr.io/{{repo_owner}}/{{project_name}}`, tagged `:latest` and `:<version>` (DC16).
- The deploy target is a self-hosted Linux host running docker compose over SSH; vendor-neutral (DC17).
- Neither dc-publish nor dc-deploy embeds a secret. Registry auth and SSH credentials come from the environment locally or GitHub Actions secrets in CI; they are referenced, never stored (DC18).
- Both `docker-compose.prod.yml.tmpl` and `release.yml.tmpl` reference the exact image string `ghcr.io/{{repo_owner}}/{{project_name}}`, so publish, deploy, and the pipeline name the same artifact.
- Only `{{project_name}}` and `{{repo_owner}}` are substituted in v0.4 templates. GitHub Actions `${{ ... }}` expressions are not template placeholders and must survive substitution.

## v0.4 Decisions

| # | Decision |
| --- | --- |
| DC15 | dc-publish and dc-deploy are Markdown-only, extending DC11. Their templates ship in the plugin; the agent runs docker, git, and ssh by following each SKILL.md. |
| DC16 | The container image is the deployment artifact. GHCR (`ghcr.io/{{repo_owner}}/{{project_name}}`) is the default registry in v0.4, matching the GitHub-centric CI choice (DC12). Other registries are deferred. |
| DC17 | The deploy target is a self-hosted Linux host running docker compose over SSH; vendor-neutral. PaaS and Kubernetes targets are deferred to a later target family. |
| DC18 | Neither skill embeds secrets. Registry auth and SSH credentials come from the environment locally, or GitHub Actions secrets in CI; the skills reference them, never store them. |

## v0.4 File Structure (additions)

```
plugins/dev-commander/
├── templates/
│   ├── workspace/
│   │   └── deployments/.gitkeep     # NEW (Task 25)
│   ├── docker/                      # NEW (Task 26)
│   │   ├── python/Dockerfile.tmpl
│   │   ├── node-ts/Dockerfile.tmpl
│   │   └── go/Dockerfile.tmpl
│   └── deploy/                      # NEW (Task 28)
│       ├── docker-compose.prod.yml.tmpl
│       └── release.yml.tmpl
└── skills/
    ├── dc-publish/SKILL.md          # NEW (Task 27)
    └── dc-deploy/SKILL.md           # NEW (Task 29)

tests/
└── test_dc_deploy.py                # NEW (Task 26, extended in Task 28)
```

Workspace layout after v0.4 (`.dev-commander/`): project.md plus `journal/`, `plans/`, `increments/`, `reviews/`, `debug/`, `design/`, `learning/`, `security/`, `handoff/`, `deployments/`.

---

### Task 25: deployments/ workspace directory (Phase 22)

**Files:**
- Create: `plugins/dev-commander/templates/workspace/deployments/.gitkeep`
- Modify: `plugins/dev-commander/scripts/status.py` (add "deployments" to DIRS)
- Modify: `tests/test_dc_core.py` (add "deployments" to DIRS)
- Modify: `tests/test_lifecycle_integration.py` (add "deployments" to WORKSPACE_DIRS)

**Interfaces:**
- Consumes: the workspace contract from Task 3.
- Produces: `.dev-commander/deployments/` holding publish and deploy records as `NNNN-<slug>.md`, read by next_step (Task 30).

- [ ] **Step 1: Update the DIRS constants (failing first)**

In `tests/test_dc_core.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff", "deployments",
]
```

In `tests/test_lifecycle_integration.py`, change WORKSPACE_DIRS identically:

```python
WORKSPACE_DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff", "deployments",
]
```

Run: `pdm run pytest tests/test_dc_core.py::test_init_creates_workspace -v`
Expected: FAIL — the template does not create `deployments/` yet.

- [ ] **Step 2: Create the template directory**

Create `plugins/dev-commander/templates/workspace/deployments/.gitkeep` (empty file).

In `plugins/dev-commander/scripts/status.py`, change the DIRS constant to:

```python
DIRS = [
    "journal", "plans", "increments", "reviews", "debug",
    "design", "learning", "security", "handoff", "deployments",
]
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_lifecycle_integration.py -v && make verify`
Expected: all pass; verifier clean.

- [ ] **Step 4: Update the workspace layout in this plan**

Confirm `deployments/` appears last (after `handoff/`) in both workspace-layout listings in this file.

- [ ] **Step 5: Commit**

Add a Phase 22 section at the top of CHANGELOG.md in the same commit. TODO.md is not changed.

```bash
git add -A
git commit -m "feat: deployments/ workspace directory (Phase 22)"
```

---

### Task 26: Dockerfile template family (Phase 23)

**Files:**
- Create: `plugins/dev-commander/templates/docker/python/Dockerfile.tmpl`
- Create: `plugins/dev-commander/templates/docker/node-ts/Dockerfile.tmpl`
- Create: `plugins/dev-commander/templates/docker/go/Dockerfile.tmpl`
- Create: `tests/test_dc_deploy.py`

**Interfaces:**
- Consumes: the stack families from Task 12 (the Dockerfiles containerize what those scaffolds build).
- Produces: `templates/docker/<stack>/Dockerfile.tmpl` that dc-publish (Task 27) generates into a project.

- [ ] **Step 1: Write the failing test**

Create `tests/test_dc_deploy.py`:

```python
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "dev-commander"
DOCKER = PLUGIN / "templates" / "docker"

STACKS = ["python", "node-ts", "go"]


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_template_exists(stack):
    assert (DOCKER / stack / "Dockerfile.tmpl").is_file()


@pytest.mark.parametrize("stack", STACKS)
def test_dockerfile_has_from_and_uses_project_name(stack):
    text = (DOCKER / stack / "Dockerfile.tmpl").read_text()
    assert "FROM " in text
    assert "{{project_name}}" in text
```

Run: `pdm run pytest tests/test_dc_deploy.py -v`
Expected: FAIL — the Dockerfile templates do not exist.

- [ ] **Step 2: Write the templates**

`plugins/dev-commander/templates/docker/python/Dockerfile.tmpl`:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pdm
COPY pyproject.toml pdm.lock* ./
RUN pdm install --prod --no-editable
COPY . .
# Replace with your app's entrypoint.
CMD ["pdm", "run", "python", "-c", "print('{{project_name}} is running')"]
```

`plugins/dev-commander/templates/docker/node-ts/Dockerfile.tmpl`:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build
# {{project_name}} entrypoint; replace if your build emits elsewhere.
CMD ["node", "dist/index.js"]
```

`plugins/dev-commander/templates/docker/go/Dockerfile.tmpl`:

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/{{project_name}} .

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/{{project_name}} /{{project_name}}
ENTRYPOINT ["/{{project_name}}"]
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_deploy.py -v && make verify`
Expected: all pass; verifier clean.

- [ ] **Step 4: Prove each Dockerfile builds and runs**

For each stack, materialize a fresh scaffold (common + stack templates with `.tmpl` stripped, substituting `demo-app` for `{{project_name}}` and `demo` for `{{project_description}}`) plus its Dockerfile (from `templates/docker/<stack>/Dockerfile.tmpl`, `.tmpl` stripped, `{{project_name}}` -> `demo-app`) into a scratch directory. Then run `docker build -t demo-app .` and `docker run --rm demo-app`.
Expected: each image builds and the container runs and exits cleanly (python prints its message; go prints the greeting; node-ts loads `dist/index.js` and exits). Remove the scratch directories afterwards. If docker is unavailable in the environment, record that in the commit message body instead and note it for the reviewer.

- [ ] **Step 5: Commit**

Add a Phase 23 CHANGELOG section in the same commit.

```bash
git add -A
git commit -m "feat: Dockerfile template family (Phase 23)"
```

---

### Task 27: dc-publish skill (Phase 24)

**Files:**
- Create: `plugins/dev-commander/skills/dc-publish/SKILL.md`
- Modify: `tests/test_dc_skills.py` (append the dc-publish entry to EXPECTED)

**Interfaces:**
- Consumes: the Dockerfile templates from Task 26; the deployments/ directory from Task 25.
- Produces: the image-reference convention `ghcr.io/{{repo_owner}}/{{project_name}}` and the build/push commands that the release workflow (Task 28) embeds.

- [ ] **Step 1: Add the dc-publish case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-publish": ["/dc:publish", "ghcr", "Dockerfile"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-publish]" -v`
Expected: FAIL — missing SKILL.md.

- [ ] **Step 2: Write dc-publish SKILL.md**

```markdown
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
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-publish]" -v && make verify`
Expected: pass; verifier clean.

- [ ] **Step 4: Commit**

Add a Phase 24 CHANGELOG section in the same commit.

```bash
git add -A
git commit -m "feat: dc-publish skill (Phase 24)"
```

---

### Task 28: prod compose and release workflow templates (Phase 25)

**Files:**
- Create: `plugins/dev-commander/templates/deploy/docker-compose.prod.yml.tmpl`
- Create: `plugins/dev-commander/templates/deploy/release.yml.tmpl`
- Modify: `tests/test_dc_deploy.py` (add compose, release-workflow, and cross-check tests)

**Interfaces:**
- Consumes: the image-reference convention from Task 27.
- Produces: `docker-compose.prod.yml.tmpl` and `release.yml.tmpl` that dc-deploy (Task 29) generates and the release workflow uses.

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_dc_deploy.py`:

```python
import yaml

DEPLOY = PLUGIN / "templates" / "deploy"
IMAGE_REF = "ghcr.io/{{repo_owner}}/{{project_name}}"


def _render(path):
    return path.read_text().replace(
        "{{project_name}}", "demo-app"
    ).replace("{{repo_owner}}", "demo-owner")


def test_deploy_templates_exist():
    assert (DEPLOY / "docker-compose.prod.yml.tmpl").is_file()
    assert (DEPLOY / "release.yml.tmpl").is_file()


def test_compose_references_the_image():
    text = (DEPLOY / "docker-compose.prod.yml.tmpl").read_text()
    assert IMAGE_REF in text


def test_compose_is_valid_yaml():
    doc = yaml.safe_load(_render(DEPLOY / "docker-compose.prod.yml.tmpl"))
    assert "services" in doc


def test_release_workflow_references_the_image():
    text = (DEPLOY / "release.yml.tmpl").read_text()
    assert IMAGE_REF in text


def test_release_workflow_is_valid_yaml_and_triggers_on_tag():
    doc = yaml.safe_load(_render(DEPLOY / "release.yml.tmpl"))
    # PyYAML parses a bare `on:` key as the boolean True (YAML 1.1).
    triggers = doc.get("on", doc.get(True))
    assert "push" in triggers
    assert "tags" in triggers["push"]


def test_release_workflow_has_build_push_and_deploy():
    text = (DEPLOY / "release.yml.tmpl").read_text()
    assert "build-push-action" in text
    assert "ssh-action" in text


def test_compose_raw_template_is_valid_yaml():
    doc = yaml.safe_load((DEPLOY / "docker-compose.prod.yml.tmpl").read_text())
    assert "services" in doc


def test_release_raw_template_is_valid_yaml():
    doc = yaml.safe_load((DEPLOY / "release.yml.tmpl").read_text())
    assert "jobs" in doc


@pytest.mark.parametrize("name", ["docker-compose.prod.yml.tmpl", "release.yml.tmpl"])
def test_deploy_template_has_no_unsubstituted_placeholders(name):
    text = _render(DEPLOY / name)
    # Our mustache placeholders are {{project_name}} and {{repo_owner}};
    # GitHub Actions ${{ ... }} expressions are legitimate and must survive.
    assert "{{project_name}}" not in text
    assert "{{repo_owner}}" not in text
```

Run: `pdm run pytest tests/test_dc_deploy.py -v`
Expected: FAIL — the deploy templates do not exist.

- [ ] **Step 2: Write docker-compose.prod.yml.tmpl**

```yaml
services:
  "{{project_name}}":
    image: ghcr.io/{{repo_owner}}/{{project_name}}:latest
    restart: unless-stopped
    ports:
      - "8080:8080"
```

- [ ] **Step 3: Write release.yml.tmpl**

```yaml
name: release
on:
  push:
    tags:
      - "v*"

jobs:
  publish-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/{{repo_owner}}/{{project_name}}:latest
            ghcr.io/{{repo_owner}}/{{project_name}}:${{ github.ref_name }}
      - name: deploy over ssh
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd {{project_name}}
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_deploy.py -v && make verify`
Expected: all pass; verifier clean.

- [ ] **Step 5: Commit**

Add a Phase 25 CHANGELOG section in the same commit.

```bash
git add -A
git commit -m "feat: production compose and release workflow templates (Phase 25)"
```

---

### Task 29: dc-deploy skill (Phase 26)

**Files:**
- Create: `plugins/dev-commander/skills/dc-deploy/SKILL.md`
- Modify: `tests/test_dc_skills.py` (append the dc-deploy entry to EXPECTED)

**Interfaces:**
- Consumes: the image reference from Task 27; the compose and release-workflow templates from Task 28; the deployments/ directory from Task 25.
- Produces: the deploy step the release workflow embeds.

- [ ] **Step 1: Add the dc-deploy case and verify it fails**

Append to `EXPECTED` in `tests/test_dc_skills.py`:

```python
    "dc-deploy": ["/dc:deploy", "docker compose", "ssh"],
```

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-deploy]" -v`
Expected: FAIL — missing SKILL.md.

- [ ] **Step 2: Write dc-deploy SKILL.md**

```markdown
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
6. For automation, dc-deploy supplies the deploy step embedded in the
   release workflow generated from `templates/deploy/release.yml.tmpl`,
   which builds, pushes, and deploys on a version tag.
7. If docker, git, or ssh is not available, report the missing tool and
   stop; never crash.
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest "tests/test_dc_skills.py::test_skill_has_frontmatter_and_required_content[dc-deploy]" -v && make verify`
Expected: pass; verifier clean.

- [ ] **Step 4: Commit**

Add a Phase 26 CHANGELOG section in the same commit.

```bash
git add -A
git commit -m "feat: dc-deploy skill (Phase 26)"
```

---

### Task 30: next_step ship state (Phase 27)

**Files:**
- Modify: `plugins/dev-commander/scripts/next_step.py`
- Modify: `tests/test_dc_core.py`
- Modify: `tests/test_lifecycle_integration.py`
- Modify: `plugins/dev-commander/skills/dc-core/SKILL.md` (the /dc:next description)

**Interfaces:**
- Consumes: the deployments/ directory from Task 25; the ship commands from Tasks 27 and 29.
- Produces: the completed lifecycle recommendation.

- [ ] **Step 1: Update the affected tests (failing first)**

In `tests/test_dc_core.py`, replace `test_next_recommends_release_when_cycle_complete` with the two functions below (the existing test currently reaches "Cycle complete" straight after a scan; the ship state now sits between them):

```python
def test_next_recommends_ship_when_no_deployment(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    result = run("next_step.py", tmp_path)
    assert "/dc:publish" in result.stdout
    assert "/dc:deploy" in result.stdout


def test_next_recommends_complete_when_deployed(tmp_path):
    run("init_workspace.py", tmp_path)
    ws = tmp_path / ".dev-commander"
    _reviewed_plan(ws)
    (ws / "handoff" / "0001-example").mkdir()
    (ws / "handoff" / "0001-example" / "summary.md").write_text("# summary\n")
    (ws / "learning" / "0001-lesson.md").write_text("Status: candidate\n")
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    (ws / "deployments" / "0001-ship.md").write_text("deployed\n")
    result = run("next_step.py", tmp_path)
    assert "Cycle complete" in result.stdout
```

In `tests/test_lifecycle_integration.py`, replace the tail from the scan step onward (the block that currently writes the security report and asserts "Cycle complete") with:

```python
    # scan (dc-secscan): a security report leaves the ship step.
    (ws / "security" / "0001-scan.md").write_text("verdict: clean\n")
    assert "/dc:publish" in run("next_step.py", tmp_path).stdout

    # ship (dc-publish + dc-deploy): a deployment record completes the cycle.
    (ws / "deployments" / "0001-ship.md").write_text("deployed\n")
    final = run("next_step.py", tmp_path)
    assert "Cycle complete" in final.stdout

    # journal (dc-core): an entry is written and counted.
    assert run("journal.py", tmp_path, "Shipped the feature").returncode == 0
    end = run("status.py", tmp_path)
    assert "journal: 1" in end.stdout
    assert "plans: 1" in end.stdout
    assert "increments: 1" in end.stdout
    # reviews counts both the code review and the plan-review file.
    assert "reviews: 2" in end.stdout
    assert "learning: 1" in end.stdout
    assert "security: 1" in end.stdout
    assert "deployments: 1" in end.stdout
```

Run: `pdm run pytest tests/test_dc_core.py::test_next_recommends_ship_when_no_deployment tests/test_lifecycle_integration.py -v`
Expected: FAIL — next_step never recommends /dc:publish yet.

- [ ] **Step 2: Add the deployments state to next_step.py**

In `plugins/dev-commander/scripts/next_step.py`, replace the terminal return with a deployments check followed by the completion message:

```python
    if not list((ws / "security").glob("*.md")):
        return ("Lessons captured. Run /dc:scan for a security scan (and "
                "/dc:ci to set up the CI pipeline) before cutting a release.")
    if not list((ws / "deployments").glob("*.md")):
        return ("Scanned. Run /dc:release to tag the version, then /dc:publish "
                "to build and push the image and /dc:deploy to ship it.")
    return ("Cycle complete. Run /dc:plan to start the next feature, or "
            "/dc:release for the next version.")
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pdm run pytest tests/test_dc_core.py tests/test_lifecycle_integration.py -v && make verify`
Expected: all pass; verifier clean.

- [ ] **Step 4: Update the dc-core /dc:next description and its plan mirror**

In `plugins/dev-commander/skills/dc-core/SKILL.md`, replace the `/dc:next` description's tail so it names the ship state. Change the sentence ending:

```
no security scan report yet means /dc:scan (and /dc:ci to set up
the CI pipeline); and once lessons and a scan exist the cycle is complete,
so /dc:release or /dc:plan for the next feature.
```

to:

```
no security scan report yet means /dc:scan (and /dc:ci to set up
the CI pipeline); no deployment record yet means /dc:release then
/dc:publish and /dc:deploy to ship the image; and once a deployment
exists the cycle is complete, so /dc:plan for the next feature.
```

Apply the identical change to the `/dc:next` mirror inside `planning/plan.md` (Task 3's SKILL.md block), keeping the two byte-identical.

- [ ] **Step 5: Commit**

Add a Phase 27 CHANGELOG section in the same commit.

```bash
git add -A
git commit -m "feat: next_step recommends the ship sequence before completion (Phase 27)"
```

---

### Task 31: v0.4 docs and release (Phase 28)

**Files:**
- Modify: `README.md` (command table, status line)
- Modify: `docs/commands.md`, `docs/lifecycle.md`, `docs/workspace.md`
- Modify: `AGENTS.md` (identity prose, decisions range)
- Modify: `pyproject.toml`, `.claude-plugin/marketplace.json`, `plugins/dev-commander/.claude-plugin/plugin.json` (version 0.4.0)
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: everything above; follows dc-release's process.
- Produces: tagged v0.4.0 on origin/main; installed plugin at 0.4.0.

- [ ] **Step 1: Update documentation**

Add rows to the README command table:

```
| /dc:publish | dc-publish | Build and push a container image to GHCR |
| /dc:deploy | dc-deploy | Deploy the published image to a host over SSH |
```

In `docs/commands.md`, add a dc-publish section and a dc-deploy section mirroring the SKILL.md behavior. In `docs/lifecycle.md`, add Publish and Deploy rows to the phase table and add the deployments state to the `/dc:next` rules list. In `docs/workspace.md`, add `deployments/` to the layout tree and the directory table. In `AGENTS.md`, extend the identity paragraph to name dc-publish (container publishing) and dc-deploy (self-hosted deployment), and change "Decisions (DC1-DC14)" to "Decisions (DC1-DC18)".

- [ ] **Step 2: Bump the version**

Run: `python3 plugins/dev-commander/scripts/bump_version.py . 0.4.0`
Then set `"version": "0.4.0"` in `.claude-plugin/marketplace.json` (plugins entry) and `plugins/dev-commander/.claude-plugin/plugin.json`. Confirm all three agree.

- [ ] **Step 3: CHANGELOG and README status**

Add a `## v0.4.0` section at the top of CHANGELOG.md summarizing Phases 22-28. Set the README status line to: Phases 0-28 complete; v0.4.0 shipped.

- [ ] **Step 4: Verify, validate, commit, tag, push**

Run: `make verify && claude plugin validate . && claude plugin validate plugins/dev-commander`
Expected: all clean.

```bash
git add -A
git commit -m "chore: release v0.4.0"
git tag -a v0.4.0 -m "release v0.4.0"
git push --follow-tags
```

- [ ] **Step 5: Check off the v0.4 checkboxes and record completion**

Check off every `- [ ] **Step` box in the v0.4 section (Tasks 25-31) and replace the "## v0.4 Completed" body with a list of Tasks 25-31, the date 2026-07-23, and their commit SHAs. Commit as `docs: v0.4 completion record`.

- [ ] **Step 6: Refresh the installed plugin and smoke-test**

Run: `claude plugin uninstall dev-commander && claude plugin install dev-commander@dev-commander-marketplace`
Confirm the installed cache contains dc-publish, dc-deploy, and the docker and deploy templates, and that a scratch-workspace `/dc:next` walk reaches the ship state.

## v0.4 To Do

Tracked in [TODO.md](../TODO.md).

## v0.4 Completed

(Empty. Move task names here with dates as they ship.)

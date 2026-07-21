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


def test_verify_skills_runs_clean():
    import subprocess
    import sys
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

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


_EMOJI_RANGES = [
    (0x2600, 0x27BF),    # miscellaneous symbols and dingbats
    (0x2B00, 0x2BFF),    # miscellaneous symbols and arrows
    (0xFE00, 0xFE0F),    # emoji variation selectors
    (0x1F000, 0x1FAFF),  # supplementary emoji and pictograph blocks
]


def _emoji_chars(text):
    return {ch for ch in text if any(lo <= ord(ch) <= hi for lo, hi in _EMOJI_RANGES)}


def _scanned_files():
    files = [
        ROOT / n for n in [
            "README.md", "CHANGELOG.md", "TODO.md", "AGENTS.md", "CLAUDE.md",
            "Makefile", "pyproject.toml", "bootstrap.sh",
        ]
    ]
    files.append(ROOT / ".claude-plugin" / "marketplace.json")
    for pattern in ("*.md", "*.py", "*.json", "*.tmpl"):
        files.extend(PLUGIN.rglob(pattern))
    return [f for f in files if f.is_file()]


def test_emoji_scan_covers_expected_files():
    names = {f.name for f in _scanned_files()}
    for required in ["Makefile", "marketplace.json", "plugin.json", "SKILL.md"]:
        assert required in names, f"emoji scan misses {required}"
    assert any(n.endswith(".py") for n in names), "emoji scan misses plugin scripts"
    assert any(n.endswith(".tmpl") for n in names), "emoji scan misses templates"


def test_no_emojis_anywhere():
    for f in _scanned_files():
        found = _emoji_chars(f.read_text())
        assert not found, f"emoji {[hex(ord(c)) for c in found]} in {f.relative_to(ROOT)}"


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

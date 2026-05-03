from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent
NUDGE = REPO_ROOT / "skills" / "pinpoint-nudge" / "SKILL.md"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{path} missing YAML frontmatter"
    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def test_nudge_skill_exists():
    assert NUDGE.is_file()


def test_nudge_skill_frontmatter():
    fm = _frontmatter(NUDGE)
    assert fm["name"] == "pinpoint-nudge"
    assert "bug" in fm["description"].lower() or "trace" in fm["description"].lower()


def test_nudge_skill_suggests_trace_command():
    text = NUDGE.read_text(encoding="utf-8")
    assert "/trace" in text, "Nudge skill must mention the /trace command"

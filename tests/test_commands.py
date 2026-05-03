from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACE_CMD = REPO_ROOT / "commands" / "trace.md"


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


def test_trace_command_exists():
    assert TRACE_CMD.is_file()


def test_trace_command_frontmatter():
    fm = _frontmatter(TRACE_CMD)
    assert fm["name"] == "trace"
    assert isinstance(fm.get("description"), str) and fm["description"]


def test_trace_command_dispatches_tracer():
    text = TRACE_CMD.read_text(encoding="utf-8")
    assert "pinpoint-tracer" in text
    assert "pinpoint-fixer" in text


def test_trace_command_handles_modes():
    text = TRACE_CMD.read_text(encoding="utf-8")
    for mode in ["--fix", "--bench", "github.com"]:
        assert mode in text, f"command must reference {mode!r} mode"

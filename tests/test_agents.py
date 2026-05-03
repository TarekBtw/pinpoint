from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACER = REPO_ROOT / "agents" / "pinpoint-tracer.md"

PHASES = ["Anchor", "Hypothesis", "Backward trace", "Invariant", "Witness", "Pinpoint"]


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


def test_tracer_exists():
    assert TRACER.is_file()


def test_tracer_frontmatter_restricts_write_tools():
    fm = _frontmatter(TRACER)
    assert fm["name"] == "pinpoint-tracer"
    tools = fm.get("tools", "")
    forbidden = ["Edit", "Write", "MultiEdit", "NotebookEdit"]
    for t in forbidden:
        assert t not in tools, f"tracer must not have access to {t} (declared tools: {tools!r})"


def test_tracer_methodology_phases_present():
    text = TRACER.read_text(encoding="utf-8")
    for phase in PHASES:
        assert phase in text, f"tracer must reference phase {phase!r}"


def test_tracer_emits_trace_report_structure():
    text = TRACER.read_text(encoding="utf-8")
    assert "Pinpoint Trace Report" in text
    assert "Confidence" in text
    assert "Hypotheses considered" in text
    assert "Witness" in text
    assert "Fix surface" in text


FIXER = REPO_ROOT / "agents" / "pinpoint-fixer.md"


def test_fixer_exists():
    assert FIXER.is_file()


def test_fixer_frontmatter_allows_edit():
    fm = _frontmatter(FIXER)
    assert fm["name"] == "pinpoint-fixer"
    tools = fm.get("tools", "")
    assert "Edit" in tools, "fixer must have access to Edit"
    assert "Read" in tools, "fixer must have access to Read"


def test_fixer_requires_trace_report_input():
    text = FIXER.read_text(encoding="utf-8")
    assert "Trace Report" in text
    assert "Fix surface" in text

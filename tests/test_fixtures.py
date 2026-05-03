import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "plugins" / "pinpoint" / "bench" / "fixtures"

REQUIRED_FILES = ["symptom.txt", "answer.json", "README.md"]
VALID_CATEGORIES = {
    "off-by-one", "null-deref", "type-mismatch", "async-race",
    "state-mutation", "wrong-default", "import-cycle", "silent-exception",
    "boundary", "logic-error",
}


def fixture_dirs():
    return [p for p in sorted(FIXTURES.iterdir())
            if p.is_dir() and not p.name.startswith(".")]


def test_at_least_one_fixture():
    assert len(fixture_dirs()) >= 1


def test_each_fixture_has_required_files():
    for d in fixture_dirs():
        for f in REQUIRED_FILES:
            assert (d / f).is_file(), f"{d.name} missing {f}"


def test_each_answer_json_well_formed():
    for d in fixture_dirs():
        with open(d / "answer.json", encoding="utf-8") as f:
            data = json.load(f)
        for key in ("root_cause_file", "root_cause_line", "root_cause_summary", "category"):
            assert key in data, f"{d.name}/answer.json missing {key}"
        assert isinstance(data["root_cause_line"], int)
        assert all(isinstance(x, int) for x in data.get("alternative_acceptable_lines", [])), \
            f"{d.name}/answer.json alternative_acceptable_lines must be list[int]"
        assert data["category"] in VALID_CATEGORIES, f"{d.name} bad category {data['category']!r}"
        named_file = d / data["root_cause_file"]
        assert named_file.is_file(), f"{d.name}/answer.json points to non-existent file {data['root_cause_file']}"


def test_each_fixture_has_source_file():
    for d in fixture_dirs():
        sources = [p for p in d.iterdir() if p.suffix in {".py", ".js", ".ts", ".tsx", ".jsx"}]
        assert sources, f"{d.name} has no source file (.py/.js/.ts)"

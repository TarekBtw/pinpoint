from pathlib import Path
from bench.runner import iter_fixtures, run_one, FixtureResult


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = REPO_ROOT / "bench" / "fixtures"


def test_iter_fixtures_finds_fixture_dirs():
    fixtures = list(iter_fixtures(FIXTURES))
    assert len(fixtures) >= 1
    for f in fixtures:
        assert (f / "symptom.txt").is_file()


def test_run_one_uses_injected_trace_fn(tmp_path):
    fixture = next(iter_fixtures(FIXTURES))

    def fake_trace(symptom: str, repo: Path) -> str:
        return "**Root cause:** bug.py:11 — fake fix"

    result = run_one(fixture, fake_trace)
    assert isinstance(result, FixtureResult)
    assert result.fixture_name == fixture.name


def test_run_one_records_failure_on_exception():
    fixture = next(iter_fixtures(FIXTURES))

    def boom(symptom, repo):
        raise RuntimeError("simulated tracer crash")

    result = run_one(fixture, boom)
    assert result.score.correct is False
    assert "simulated tracer crash" in result.score.reason


def test_summarize_handles_empty_and_partial():
    from bench.runner import summarize, FixtureResult
    from bench.scoring import ScoreResult

    correct = FixtureResult("a", ScoreResult(True, "bug.py", 11, "match"), "")
    wrong = FixtureResult("b", ScoreResult(False, "bug.py", 99, "wrong line"), "")
    boom = FixtureResult("c", ScoreResult(False, None, None, "trace_fn raised: x"), "")

    s = summarize([correct, wrong, boom])
    assert s["total"] == 3
    assert s["correct"] == 1
    assert abs(s["accuracy"] - (1 / 3)) < 1e-9
    assert len(s["results"]) == 3

    empty = summarize([])
    assert empty["total"] == 0
    assert empty["correct"] == 0
    assert empty["accuracy"] == 0.0


def test_main_writes_out_file(tmp_path, monkeypatch):
    import json
    from bench import runner

    fake_report = "**Root cause:** bug.py:11 — fake fix"
    monkeypatch.setattr(runner, "claude_code_trace", lambda symptom, fixture: fake_report)

    out_path = tmp_path / "results.json"
    rc = runner.main(["--all", "--out", str(out_path)])
    assert rc in (0, 1)  # exit code reflects scoring; not the focus of this test
    assert out_path.is_file()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "total" in data and "correct" in data and "accuracy" in data
    assert data["total"] >= 1
    assert isinstance(data["results"], list) and len(data["results"]) == data["total"]

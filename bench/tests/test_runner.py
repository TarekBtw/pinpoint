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

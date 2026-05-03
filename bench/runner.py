from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

# When executed as a script (`python bench/runner.py`), the project root may
# not be on sys.path. Prepend it so `bench.scoring` imports cleanly.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bench.scoring import AnswerKey, ScoreResult, score_trace


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURES = REPO_ROOT / "bench" / "fixtures"
RESULTS_DIR = REPO_ROOT / "bench" / "results"


@dataclass
class FixtureResult:
    fixture_name: str
    score: ScoreResult
    raw_report: str


def iter_fixtures(root: Path = DEFAULT_FIXTURES) -> Iterator[Path]:
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            if (entry / "symptom.txt").is_file():
                yield entry


def run_one(fixture: Path, trace_fn: Callable[[str, Path], str]) -> FixtureResult:
    answer = AnswerKey.from_json(fixture / "answer.json")
    symptom = (fixture / "symptom.txt").read_text(encoding="utf-8")
    try:
        report = trace_fn(symptom, fixture)
    except Exception as exc:
        return FixtureResult(
            fixture_name=fixture.name,
            score=ScoreResult(False, None, None, f"trace_fn raised: {exc}"),
            raw_report="",
        )
    return FixtureResult(
        fixture_name=fixture.name,
        score=score_trace(report, answer),
        raw_report=report,
    )


def claude_code_trace(symptom: str, fixture: Path) -> str:
    """Default trace function: shells out to Claude Code with /trace.

    Requires the `claude` CLI to be installed and authenticated.
    Set PINPOINT_BENCH_FAKE=1 to use a stubbed trace (for CI smoke tests).
    """
    import os
    import subprocess

    if os.environ.get("PINPOINT_BENCH_FAKE") == "1":
        return "**Root cause:** bug.py:1 — stubbed (PINPOINT_BENCH_FAKE=1)"

    cmd = ["claude", "-p", f"/trace {symptom}"]
    proc = subprocess.run(cmd, cwd=str(fixture), capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[:500]}")
    return proc.stdout


def summarize(results: list[FixtureResult]) -> dict:
    total = len(results)
    correct = sum(1 for r in results if r.score.correct)
    return {
        "total": total,
        "correct": correct,
        "accuracy": (correct / total) if total else 0.0,
        "results": [
            {
                "fixture": r.fixture_name,
                "correct": r.score.correct,
                "matched_file": r.score.matched_file,
                "matched_line": r.score.matched_line,
                "reason": r.score.reason,
            }
            for r in results
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pinpoint-bench")
    parser.add_argument("--all", action="store_true", help="run every fixture")
    parser.add_argument("--fixture", help="run a single fixture by directory name")
    parser.add_argument("--out", default=None, help="path to write JSON results")
    args = parser.parse_args(argv)

    if not args.all and not args.fixture:
        parser.error("specify --all or --fixture <name>")

    fixtures = list(iter_fixtures())
    if args.fixture:
        fixtures = [f for f in fixtures if f.name == args.fixture]
        if not fixtures:
            parser.error(f"fixture {args.fixture!r} not found")

    results = [run_one(f, claude_code_trace) for f in fixtures]
    summary = summarize(results)

    # Windows consoles often default to cp1252 which cannot encode the
    # check/cross marks below. Reconfigure stdout to UTF-8 if available.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    print(f"\n=== Pinpoint Bench ===")
    print(f"Fixtures: {summary['total']}")
    print(f"Correct:  {summary['correct']}")
    print(f"Accuracy: {summary['accuracy']:.1%}\n")
    for r in summary["results"]:
        mark = "✅" if r["correct"] else "❌"
        print(f"  {mark} {r['fixture']}: {r['reason']}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nResults written to {out_path}")

    return 0 if summary["correct"] == summary["total"] else 1


if __name__ == "__main__":
    sys.exit(main())

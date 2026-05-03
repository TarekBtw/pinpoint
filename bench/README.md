# Pinpoint Bench

Reproducible benchmark for the `/trace` command.

## Run

```bash
# Run every fixture (requires `claude` CLI authenticated)
python bench/runner.py --all --out bench/results/latest.json

# Run a single fixture
python bench/runner.py --fixture 01-python-typeerror

# CI smoke test (stubbed tracer, no Claude calls)
PINPOINT_BENCH_FAKE=1 python bench/runner.py --all
```

## Adding a fixture

See `bench/fixtures/README.md`. Each fixture is a self-contained directory; fixtures are auto-discovered.

## Scoring

A trace is correct if its `**Root cause:**` line names the expected file and a line in the accepted set. See `bench/scoring.py`.

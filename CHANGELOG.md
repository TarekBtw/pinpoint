# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [SemVer](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-03

### Added
- `/trace` slash command with plain-symptom, GitHub-issue-URL, `--fix`, and `--bench` modes.
- `pinpoint-tracer` subagent enforcing a 6-phase static methodology (Anchor → Hypotheses → Backward trace → Invariant → Witness → Pinpoint). No write tools.
- `pinpoint-fixer` subagent — patches only files named in the trace's Fix surface; only invoked by `--fix`.
- `pinpoint-nudge` skill — discovery aid that suggests `/trace` on bug-shaped requests.
- Trace Report format: structured markdown with Mermaid call-flow diagram, ruled-out hypotheses, backward-trace table, and explicit confidence boundaries.
- Benchmark harness (`bench/runner.py`) with 10 fixtures (5 Python, 5 TypeScript) covering off-by-one, null-deref, type-mismatch, async-race, state-mutation, silent-exception, and logic-error categories.
- Plugin and marketplace manifests; repo doubles as its own marketplace.

### Known limitations
- v0.1.0 is strictly static — does not execute user code.
- Language-specific tooling integrated for Python (`pyright`, `py_compile`) and TypeScript (`tsc`). Other languages run on `Read` + `Grep` + tree-sitter only.
- GitHub issue ingest supports public issues only.

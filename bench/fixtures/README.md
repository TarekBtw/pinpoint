# Bench Fixtures

Each fixture is a self-contained directory representing one bug.

## Required files

- `bug.<ext>` (or multiple source files) — the buggy program. Must actually fail or produce wrong output when executed in a normal way.
- `symptom.txt` — the exact text passed to `/trace` as the symptom (a stack trace, error, failing test output, or one-paragraph description).
- `answer.json` — the expected root cause:
  ```json
  {
    "root_cause_file": "bug.py",
    "root_cause_line": 12,
    "root_cause_summary": "off-by-one in range bound",
    "alternative_acceptable_lines": [11, 13],
    "category": "off-by-one"
  }
  ```
- `README.md` — one paragraph describing the bug (for human reviewers).

## Categories

Each fixture's `category` field must be one of:
`off-by-one`, `null-deref`, `type-mismatch`, `async-race`, `state-mutation`, `wrong-default`, `import-cycle`, `silent-exception`, `boundary`, `logic-error`.

## Acceptable answer

A trace is scored correct if its `Root cause:` line names a file matching `root_cause_file` AND a line that is either `root_cause_line` or in `alternative_acceptable_lines`. The line tolerance handles formatting drift.

### Line-number convention

If `symptom.txt` is a stack trace pasted from a previous run, its line numbers may not match the current `bug.<ext>` exactly (whitespace edits, reformatting, etc.). The convention is:

- `root_cause_line` — the line number as it appears in `symptom.txt` (paste-relative). This is what a model trained on the symptom would naturally cite.
- `alternative_acceptable_lines` — the *current* line in `bug.<ext>` (file-relative), plus any other lines a reasonable trace might cite (e.g., the data definition site that should also have been guarded).

`alternative_acceptable_lines` is optional; omit it or pass `[]` if there's no drift and no alternative.

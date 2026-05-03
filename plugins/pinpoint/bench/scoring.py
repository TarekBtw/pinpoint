from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnswerKey:
    root_cause_file: str
    root_cause_line: int
    alternative_acceptable_lines: list[int]
    root_cause_summary: str
    category: str

    @classmethod
    def from_json(cls, path: Path) -> "AnswerKey":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            root_cause_file=data["root_cause_file"],
            root_cause_line=data["root_cause_line"],
            alternative_acceptable_lines=data.get("alternative_acceptable_lines", []),
            root_cause_summary=data["root_cause_summary"],
            category=data["category"],
        )


@dataclass
class ScoreResult:
    correct: bool
    matched_file: str | None
    matched_line: int | None
    reason: str


_ROOT_CAUSE_RE = re.compile(
    r"\*\*Root cause:\*\*\s+([^\s:]+):(\d+)",
    re.MULTILINE,
)


def score_trace(report: str, answer: AnswerKey) -> ScoreResult:
    """Score a trace report against an answer key. Strict file match, line within accepted set."""
    match = _ROOT_CAUSE_RE.search(report)
    if not match:
        return ScoreResult(False, None, None, "no root cause line found in report")
    file_part = match.group(1).split("/")[-1]
    line_part = int(match.group(2))
    expected_file = answer.root_cause_file.split("/")[-1]
    if file_part != expected_file:
        return ScoreResult(False, file_part, line_part,
                           f"file mismatch: expected {expected_file}, got {file_part}")
    accepted = {answer.root_cause_line, *answer.alternative_acceptable_lines}
    if line_part not in accepted:
        return ScoreResult(False, file_part, line_part,
                           f"line {line_part} not in accepted set {sorted(accepted)}")
    return ScoreResult(True, file_part, line_part, "match")

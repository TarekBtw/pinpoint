from bench.scoring import score_trace, AnswerKey


def _key(file="bug.py", line=11, alts=None, summary="x", category="null-deref"):
    return AnswerKey(
        root_cause_file=file,
        root_cause_line=line,
        alternative_acceptable_lines=alts or [],
        root_cause_summary=summary,
        category=category,
    )


def test_exact_match_scores_correct():
    report = "**Root cause:** bug.py:11 — unchecked index"
    assert score_trace(report, _key()).correct is True


def test_alternative_line_scores_correct():
    report = "**Root cause:** bug.py:10 — unchecked index"
    assert score_trace(report, _key(alts=[10])).correct is True


def test_wrong_file_scores_incorrect():
    report = "**Root cause:** other.py:11 — unchecked index"
    assert score_trace(report, _key()).correct is False


def test_wrong_line_outside_tolerance_scores_incorrect():
    report = "**Root cause:** bug.py:42 — unchecked index"
    assert score_trace(report, _key()).correct is False


def test_missing_root_cause_line_scores_incorrect():
    report = "no root cause here"
    result = score_trace(report, _key())
    assert result.correct is False
    assert result.reason == "no root cause line found in report"

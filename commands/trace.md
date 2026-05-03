---
name: trace
description: Trace the root cause of a bug through a disciplined 6-phase methodology before any fix is proposed. Usage: /trace "<symptom>" | /trace <github-issue-url> | /trace --fix "<symptom>" | /trace --bench
---

# /trace

The user invoked `/trace`. Parse `$ARGUMENTS` and dispatch.

## Argument parsing

1. **Empty arguments.** Ask: "What's the symptom? Paste the error, stack trace, failing test name, or describe the bug." Wait for the next message and treat that as `$ARGUMENTS`.
2. **`--bench`.** Run `python bench/runner.py --all` from the plugin directory. Stream the output. Do not dispatch any agent.
3. **`--fix <symptom>`.** First trace, then fix (see "Fix mode" below).
4. **GitHub issue or PR URL** (matches `^https://github\.com/[^/]+/[^/]+/(?:issues|pull)/\d+(?:[/?#].*)?$`). Use `WebFetch` to retrieve the page. Extract the title + body. Treat the body as the symptom. Continue to "Trace mode".
5. **Anything else.** Treat as the literal symptom string. Continue to "Trace mode".

## Trace mode

Dispatch the `pinpoint-tracer` subagent:

```
Agent(
  subagent_type="pinpoint-tracer",
  description="Trace bug root cause",
  prompt="""
You are tracing a bug. Inputs:

symptom:
<paste the parsed symptom here>

repo_root:
<paste the user's current working directory here, absolute path>

language_hints:
<list languages detected from extensions in the repo, plus tooling availability — check with `which pyright` and `which tsc`>

Run the 6-phase protocol from your instructions. Emit a single Trace Report and nothing else.
"""
)
```

When the subagent returns, do four things:

1. Save the report to `.pinpoint/traces/<YYYY-MM-DDTHH-MM-SS>-<slug>.md` in the user's repo (create the directory if missing). The slug is the first 40 chars of the symptom, lowercased, non-alphanumeric replaced with `-`.
2. Print the full report to the conversation so the user sees it.
3. Print one line: `Trace saved to .pinpoint/traces/<filename>.md`.
4. Ask: "Want me to apply the fix? (yes / no / redirect with new info)". Do not write any code unless the user says yes.

## Fix mode (`--fix`)

Run trace mode first. After the report is shown:

- If `Confidence: low`, **do not** dispatch the fixer. Print: "Confidence is low — review the trace and rerun without `--fix` if you want me to write the patch by hand." Stop.
- If `Confidence: medium` or `high`, dispatch the `pinpoint-fixer` subagent:

```
Agent(
  subagent_type="pinpoint-fixer",
  description="Apply minimal patch from trace report",
  prompt="""
trace_report:
<paste the full Trace Report markdown here>

repo_root:
<absolute path>

Apply the minimal patch per your instructions. Emit the fix summary and nothing else.
"""
)
```

Print the fixer's output and stop. Do not commit.

## Bench mode (`--bench`)

Run:

```bash
python bench/runner.py --all
```

from the plugin's installed directory (resolve via `${CLAUDE_PLUGIN_ROOT}` if set, else search for `pinpoint/bench/runner.py` under the plugin install root). Stream output to the conversation. Do not dispatch agents — bench has its own orchestration.

## Errors

- If the user's `cwd` is not a git repo, warn: "Pinpoint works best inside a project. Continue anyway? (y/n)". On `y`, proceed.
- If the GitHub issue URL is private or unreachable, ask the user to paste the issue body directly.
- If `bench/runner.py` is missing, print: "Benchmark runner not installed. See bench/README.md for setup."
- If the tracer returns no Trace Report, or the returned report has no `**Confidence:**` line, print: "Tracer did not return a parseable report. Rerun `/trace` or paste the symptom again with more context." In `--fix` mode, do not dispatch the fixer.

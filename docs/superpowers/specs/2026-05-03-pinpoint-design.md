# Pinpoint — Design Spec

**Date:** 2026-05-03
**Status:** Approved for implementation planning
**Author:** memet077a@gmail.com

---

## 1. Problem

Vanilla Claude Code is unreliable at debugging. When asked to "fix this bug," it tends to pattern-match against the symptom and propose plausible-looking changes without tracing the actual root cause. Common failure modes:

- Latches onto the first hypothesis without considering alternatives
- Skips backward data-flow analysis ("where did this bad value come from?")
- Suggests fixes at the symptom site, not the cause site
- Doesn't articulate or check invariants
- Produces no artifact the user can review before code changes

The result: users iterate "no, that's wrong" several times, or accept a fix that masks the symptom while leaving the underlying defect.

## 2. Goal

Ship `pinpoint` — an open-source Claude Code plugin that performs disciplined static root-cause tracing before any fix is proposed. The plugin enforces a 6-phase methodology that vanilla Claude skips, produces a structured Trace Report as a reviewable artifact, and only writes a fix when the user explicitly opts in.

The plugin is also a portfolio piece. Distribution strategy is a first-class part of this design: README, benchmark numbers, demo repo, and shareable Mermaid-diagram trace reports are scoped into v1.

## 3. Non-goals (v1)

- Running the user's program or tests (strictly static analysis)
- LSP integration (tree-sitter covers the same ground without per-editor friction)
- Sandboxed/containerized tool invocation (assume user trusts their own repo)
- IDE extensions or wrappers
- A live benchmark leaderboard website
- Compiled-language deep symbol servers (clangd, gopls beyond `go vet`)

## 4. Plugin shape & UX

### Primitives
- **One slash command:** `/trace`
- **Two subagents:** `pinpoint-tracer` (methodology, no write tools) and `pinpoint-fixer` (only invoked with `--fix`)
- **One skill:** `pinpoint-nudge` (suggests `/trace` when Claude detects a bug-shaped task; does not take over)
- No hooks, no MCP server

### Invocation
- `/trace "<symptom>"` — symptom can be a stack trace, error message, failing test name, or natural-language description
- `/trace <github-issue-url>` — fetches the issue body, parses symptom, traces
- `/trace --fix "<symptom>"` — runs trace, then dispatches the fixer subagent to apply the patch (skips manual review gate)
- `/trace --bench` — runs against the bundled fixture set, prints accuracy report

### User flow

```
User: /trace "TypeError: undefined is not a function at cart.js:47"
       ↓
/trace command dispatches pinpoint-tracer subagent with the symptom
       ↓
Subagent runs the 6-phase methodology in isolated context
       ↓
Subagent returns Trace Report (≤ ~400 lines markdown)
       ↓
Main Claude shows the report. User reviews. Then either:
   → "looks right, fix it" → main Claude applies the patch
   → "wrong, try X"        → user redirects
   → /trace --fix <symptom> → trace + patch in one shot
```

### Why a subagent
The trace process reads many files and reasons through call graphs. That conversation would balloon main Claude's context. The subagent does it in isolation and returns just the trace artifact. Main Claude stays clean for any follow-up fix.

### Why two subagents (tracer and fixer)
The tracer's system prompt explicitly forbids code-writing tools (no `Edit`, no `Write`). This is the structural guarantee against the "jumps to fix-mode" failure pattern. The fixer is a separate agent invoked only with `--fix`, and only after the trace is complete.

### The nudge skill
Description triggers on bug-shaped tasks: error messages, stack traces, "fix this bug", failing tests. When fired, it outputs a single suggestion:

> *"This looks like a bug-tracing task. Want to run `/trace`? It traces the root cause before suggesting a fix."*

Then exits. The user decides. Purpose: discoverability — users who installed the plugin shouldn't have to remember it exists.

## 5. The trace methodology

The tracer subagent runs a fixed 6-phase protocol. Each phase has explicit completion criteria. The tracer cannot emit a final report until all phases pass.

### Phase 1 — Anchor
Convert the symptom into a precise anchor: `<file>:<line>` and the exact observed bad state. If the input is fuzzy ("cart total wrong on Fridays"), the tracer first locates the symptom site by reading code.
- **Output:** `Anchor: <file>:<line> — <observed bad state>`

### Phase 2 — Hypothesis register
Before tracing, list ≥3 candidate causes with one-line rationale each. Forces breadth over premature commitment.
- **Output:** numbered list of candidate causes
- **Gate:** must have ≥3 entries before Phase 3

### Phase 3 — Backward trace
From the anchor, walk data and control flow backward. At each step, name: variable/branch tracked, file:line, which hypotheses it eliminates or supports. Tooling kicks in here (tree-sitter AST queries; language-specific tools when available).
- **Output:** ordered list of trace steps

### Phase 4 — Invariant check
At each traced point, articulate "what must be true here" and check it. The bug is the **first place an expected invariant is violated.** This is the precise definition of root cause: not where the error surfaces, but where reality first diverges from intent.
- **Output:** invariant statements per traced point, marking the first violation

### Phase 5 — Witness
Construct a concrete witness: "If `<input>=X`, execution reaches line Y with state Z, violating invariant W." A trace without a witness is a guess.
- **Gate:** if no witness can be constructed, return to Phase 3

### Phase 6 — Pinpoint + rule out
Emit final report: exact `file:line` of the cause, plus explicit ruling-out of every other Phase 2 hypothesis. Confidence rating (high/medium/low) based on witness completeness.

### Hard rule
The `pinpoint-tracer` subagent's system prompt forbids any code-writing or patch-proposing. It can only emit the Trace Report. The `--fix` flag dispatches a *separate* `pinpoint-fixer` subagent that takes the trace report as input and applies the patch.

## 6. Tooling integration & language scope

### Layered approach
- **Universal layer (every language):** `Read`, `Grep`, `Glob`, plus tree-sitter for AST navigation. Tree-sitter has parsers for ~40 languages and ships as a single binary.
- **Language-specific layer (when detected):**

| Language | v1 tooling | Detection |
|---|---|---|
| Python | `pyright --outputjson`; `python -m py_compile` | `*.py` + `pyproject.toml` / `requirements.txt` |
| TypeScript / JavaScript | `tsc --noEmit --pretty false` | `tsconfig.json` / `package.json` |
| Rust | `cargo check --message-format=json` | `Cargo.toml` (v1.1) |
| Go | `go vet ./...` + `go build` | `go.mod` (v1.1) |

### Invocation rules
- Tracer calls tools via `Bash` directly, assuming `PATH` availability
- If a tool is missing, it's silently skipped — methodology still runs on Read+Grep+tree-sitter
- README documents which tools to install for richer traces

### v1 language priority
**Python + TypeScript first.** Largest Claude Code user base, easiest tooling, most demo-able. Rust + Go in v1.1.

## 7. Trace report format

### Structure
Markdown document, ≤ ~400 lines, seven sections:

1. **Headline:** symptom, anchor, root cause, confidence, generation timestamp
2. **Hypotheses considered:** numbered list with ✅/❌ markers
3. **Call flow:** Mermaid `flowchart TD` diagram
4. **Backward trace:** table (step | location | tracking | note)
5. **Witness:** concrete input + execution path
6. **Fix surface:** named locations where a fix could go (does NOT write the fix)
7. **What I did NOT verify:** explicit confidence boundaries

### Example (abbreviated)

```markdown
# Pinpoint Trace Report

**Symptom:** TypeError: undefined is not a function
**Anchor:** src/cart.js:47 — `applyDiscount(item.promo)`
**Root cause:** src/cart.js:42 — `item.promo` undefined for pre-migration items
**Confidence:** high

## Hypotheses considered
1. Pre-migration items lack `promo` field — confirmed
2. Race condition during cart load — ruled out, no concurrency
3. Type definition wrong — ruled out, runtime issue

## Call flow
[Mermaid flowchart]

## Backward trace
[Table]

## Witness
Given a cart row inserted before 2025-09-01 (pre-migration), `lineItems[i].promo === undefined`. Reaching cart.js:47 invokes `undefined(...)` → TypeError.

## Fix surface
- src/cart.js:42 — guard `item.promo`
- migrations/...sql — backfill nullable column

## What I did NOT verify
- Other call sites of `applyDiscount`
- Production data distribution
```

### Persistence
Saved to `.pinpoint/traces/<timestamp>-<slug>.md` in the user's repo. Gitignore-able.

### Branding
Headline `Pinpoint Trace Report`. Consistent visual identity across every output.

## 8. Open-source distribution strategy

The plugin is also a portfolio piece. These elements are scoped into v1, not v1.1.

### Tier 1 — in v1

1. **Benchmark mode** (`/trace --bench`) — runs against ≥20 fixture bugs (start hand-picked, expand to SWE-bench-Lite tracing subset). Outputs accuracy numbers. *This is the single biggest leverage move for distribution.* The README headline is the benchmark number.

2. **Mermaid call-flow diagram** — every trace report includes one. GitHub renders Mermaid natively; users pasting reports into issues become free distribution.

3. **GitHub Issue ingest** — `/trace <issue-url>` fetches the issue, parses symptom, traces. Shifts audience from "people debugging their own code" to "OSS maintainers triaging issues" — exactly the demographic that stars repos.

4. **Demo repo** (separate `pinpoint-demo` repo) — 5–10 hand-crafted buggy mini-projects. README of main repo: "Try it in 30 seconds: clone the demo, run `/trace`, see the report."

### Tier 2 — deferred to v1.1
- Auto-write regression test when `--fix` patches code
- "Vanilla Claude vs. Pinpoint" side-by-side comparison doc
- Trace history insights ("you've hit this kind of bug 3x")

### Tier 3 — out of scope
- Live benchmark leaderboard website
- VSCode/JetBrains extension wrappers
- Hosted SaaS

## 9. Repo structure

Two repos under one GitHub user/org:

```
pinpoint/                           ← main plugin repo
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json            ← repo doubles as its own marketplace
├── commands/
│   └── trace.md
├── agents/
│   ├── pinpoint-tracer.md
│   └── pinpoint-fixer.md
├── skills/
│   └── pinpoint-nudge/
│       └── SKILL.md
├── bench/
│   ├── fixtures/
│   ├── runner.py
│   └── README.md
├── README.md
├── LICENSE                          ← MIT
└── CHANGELOG.md

pinpoint-demo/                       ← separate "try it in 30 seconds" repo
├── README.md
├── bug-1-typeerror/
├── bug-2-async-race/
└── ...
```

### README anatomy (main repo)
1. One-line tagline
2. Animated demo GIF (≤ 15 seconds)
3. Benchmark headline number with reproduction link
4. 30-second install (two commands)
5. The 6-phase methodology, one bullet each
6. Example trace report with Mermaid rendering inline
7. Vanilla Claude vs. Pinpoint comparison
8. FAQ

### Distribution
- Users add via `/plugin marketplace add <user>/pinpoint` then `/plugin install pinpoint`
- One repo doubles as marketplace; split out if more plugins ship later

### Launch surface (after v1 release)
- HN Show post
- X / Bluesky thread
- r/ClaudeAI, r/programming
- Methodology blog post (content-marketing layer)

## 10. License & versioning
- **License:** MIT
- **Versioning:** SemVer; v0.1.0 = initial release with everything in this spec

## 11. Anti-scope (explicitly NOT in v1)
- Running tests / executing user code
- Modifying user code without `--fix` flag
- LSP integration
- Container/sandbox isolation
- Languages beyond Python + TypeScript with first-class tooling
- Trace history analytics
- Auto-regression-test generation
- Public benchmark leaderboard

## 12. Open questions / risks

- **Tree-sitter binary distribution.** Plugin must not require users to compile native code. Solution path: use tree-sitter via npx + per-language WASM grammars, or document the install. Decide during planning.
- **Benchmark fixture set.** SWE-bench-Lite licensing for the tracing subset needs verification. Fallback: hand-craft ≥20 fixtures spanning Python/TS, document methodology, expand later.
- **GitHub Issue ingest auth.** Public issues need no auth; private repos do. v1 supports public only; document the limitation.
- **`--fix` flag boundaries.** What does the fixer subagent get? Just the trace report, or also the original codebase? Decision: trace report only as instructions, plus `Read`/`Edit` tools scoped to the user's repo. No re-trace.
- **Confidence ratings.** Need a deterministic rubric for high/medium/low so the value is meaningful, not vibes. Define during planning.

---

**Implementation plan:** to be written next via `superpowers:writing-plans` skill.

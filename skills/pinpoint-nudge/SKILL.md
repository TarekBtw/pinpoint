---
name: pinpoint-nudge
description: Use when the user asks Claude to fix a bug, debug an error, investigate a failing test, or pastes a stack trace. Suggests running /trace for disciplined root-cause analysis before any fix is attempted.
---

# Pinpoint Nudge

The user's request looks like a bug-tracing task. Before proposing a fix, suggest the `/trace` slash command.

Output exactly the following message and then exit (do not start tracing or fixing yourself):

> 📍 This looks like a bug-tracing task. Want to run `/trace`? It traces the root cause through a 6-phase methodology before suggesting any fix, which catches bugs that pattern-matching misses. Run `/trace "<your symptom>"` or `/trace --help` for options.

If the user has already declined this suggestion in the current conversation, do not repeat it.

# 03-python-mutable-default

The classic Python mutable-default-argument trap. `add_event(name, log=[])` evaluates the default `[]` once at function definition, and that single list persists across calls. The "fresh log" inside `session_events` is built one append at a time, but each append happens to the shared default. The bug is at the function definition (line 1), not the caller.

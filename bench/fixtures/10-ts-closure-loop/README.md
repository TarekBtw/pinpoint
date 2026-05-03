# 10-ts-closure-loop

`var` is function-scoped, not block-scoped. All closures share the same `i`. After the loop ends, `i === 3`, so every handler returns 3. Fix: replace `var` with `let` (block-scoped) or capture via IIFE. Root cause: the `var` declaration in the loop header.

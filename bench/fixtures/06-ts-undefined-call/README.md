# 06-ts-undefined-call

The optional `promo?` field is forced via `!` to non-null. TypeScript trusts the assertion and lets the call through. At runtime, the second cart item has no promo, and the access to `promo.pct` inside `applyPromo` fails. Root cause is the non-null assertion at the call site, not the optional declaration.

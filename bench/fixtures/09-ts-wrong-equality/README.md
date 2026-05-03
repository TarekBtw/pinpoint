# 09-ts-wrong-equality

`Array.includes` uses SameValueZero. For objects, that's reference equality. The two UserIds with `value: "u1"` are different object instances, so includes returns false and both are appended. Fix: dedupe by `id.value` (e.g., a Map or Set keyed by value).

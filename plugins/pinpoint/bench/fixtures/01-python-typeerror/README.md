# 01-python-typeerror

Cart total computation crashes with `KeyError: 'promo'` because `line_total` indexes `item["promo"]` without checking for the key. The second cart item (price=5, qty=1) has no `promo`. Root cause is the unchecked indexing in `line_total`, not the input data — items legitimately lack a discount.

The "anchor" of the crash is the `KeyError`, but the "first invariant violation" is `line_total`'s assumption that every item carries a promo, which is what should be fixed.

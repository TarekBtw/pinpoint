# 02-python-off-by-one

Pagination boundary check is one off. `last_page = len(items) // per_page` gives 2 for len=10 per_page=5, but pages 0 and 1 already cover the whole list. The check `page > last_page` then permits page 2 (which returns `[]` silently) and only rejects page 3+. Either `last_page` should be `(len-1) // per_page` (= 1), or the comparison should be `>=`. Root cause is the boundary computation, not the comparison operator.

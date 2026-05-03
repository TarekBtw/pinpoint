# 02-python-off-by-one

Pagination boundary check is inconsistent. `last_page = len(items) // per_page` gives 2 for len=10 per_page=5, but pages 0 and 1 already cover the whole list. The check `page > last_page` then rejects page 2 (which doesn't exist) but its math doesn't match its intent. Either `last_page` should be `(len-1) // per_page` (= 1), or the comparison should be `>=`. Root cause is the boundary computation, not the comparison operator.

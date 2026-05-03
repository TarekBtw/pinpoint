# 05-python-silent-exception

Bare `except Exception` swallows everything. If the JSON file has a syntax error, or there's a permissions issue, or the path is wrong, `load_config` returns `{}` silently. The KeyError that surfaces in `get_max_users` is a downstream symptom — the root cause is the over-broad except clause that hides what actually failed.

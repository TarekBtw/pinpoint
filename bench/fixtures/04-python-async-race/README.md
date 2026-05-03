# 04-python-async-race

The increment is not atomic across the await. Each coroutine reads `self.value` (line 9), yields to the event loop (line 10), then writes `current + 1` (line 11). All 100 coroutines read 0, all 100 write 1. The fix is either to remove the await between read and write, or use a lock. Root cause: the read-modify-write straddling an await.

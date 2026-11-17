# Investigating the stale order total

The internal report gives a suspect boundary: Redis eviction happens while the line removal is still uncommitted. I followed that into the read path. A cache miss opens a database read, computes a total from the committed line items, and writes that total into the cache. The database read and cache write are separate actions, so I checked both sides of the commit for the stale write. The public [task prompt](TASK.md) gives the symptom and the point by which a new request must be correct. The diagnosis and schedules below are for the reviewer.

1. **Establish the oracle.** Order 1 has lines priced at 1,200 and 2,000 cents. After the first line is removed successfully, the committed total is 2,000 and the revision advances from 0 to 1. The harness reads the database directly to confirm the mutation before comparing the next checkout read with that total.
2. **Fill while the writer is uncommitted.** The `before_commit` callback starts the reader on another SQLite connection. It can only see the old committed total of 3,200. Pre-commit eviction has already happened, so the reader can refill 3,200 and leave it cached after commit. Moving the eviction after commit clears this particular stale fill.
3. **Let the old read finish after eviction.** The `before_fill` callback pauses the reader after it computes 3,200 and runs the entire removal. Either eviction can now finish before the paused read resumes and writes 3,200. The next read is the one that must be correct. The old reader started before the successful removal, so 3,200 is within its allowed behavior.
4. **Validate what a cache hit represents.** The reference reads the revision and aggregated total in one database statement when building a snapshot. After the delayed fill, the cache contains `(revision=0, total=3200)` and the database reports revision 1. A fresh read fetches `(revision=1, total=2000)`. The control checks show that a rollback retains revision 0 and that a successful change only requires re-aggregating the changed order.

```text
Schedule                             Baseline   Evict after commit   Revision-aware
Read and fill before commit              3200                 2000             2000
Read before commit, fill after return    3200                 3200             2000
```

Run `python3 questions/05-cache-consistency/cache_demo.py` from the repository root. The five tests confirm both stale schedules, show why eviction after commit is a partial fix, exercise the reference, and check rollback and cache reuse. I also tried clearing the entire cache after commit. That candidate returned the correct totals, but the cache reuse test rejected it because it ran four aggregations where only three were needed.

This is a SQLite and in-memory cache reproduction with explicit ordering at the boundaries. Applying the design to the original service would require exercising the HTTP endpoints with its actual database and Redis adapter, including every mutation that changes a total and the cost of reading a revision on a warm hit.

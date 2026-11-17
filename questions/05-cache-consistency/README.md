# Question 5 · Writing a task prompt

[Prompt to hand to the coding agent](TASK.md)

## Author notes

The prompt names the customer-visible symptom and a precise visibility boundary. A read already in flight can see the previous committed order. A new read after removal succeeds must see the removal, including when that earlier read finishes later. The agent can trace the remove-item handler to its transaction boundary and follow the read endpoint through cache miss, committed database read, and cache fill.

Two deterministic schedules distinguish a partial fix from a complete one. Both start with a cold total cache and an order worth 3,200 cents, including a 1,200-cent line that will be removed.

| Controlled overlap | Pre-commit delete | After-commit delete | Revision-aware example |
| --- | ---: | ---: | ---: |
| A reader fills the cache before the removal commits | 3,200 | 2,000 | 2,000 |
| A reader gets the old snapshot before the commit and fills the cache after the removal returns | 3,200 | 3,200 | 2,000 |

Each number is the total observed by the next request after both operations. In the second schedule, an after-commit delete can complete before the stale reader writes its value. The example associates a cached total with the committed order revision recorded alongside that total. A later read compares with the current revision and recomputes on a mismatch, while a warm hit skips the aggregation. The revision and line-item change commit together. A check also covers a rollback and a second order. In the full application, the evaluator would exercise the actual HTTP endpoints with the real Redis adapter and database, and the maintainer would review the cost and consistency of the read path.

The runnable model uses SQLite WAL with separate connections and an in-memory cache. Callbacks run the overlapping operation exactly at the relevant boundary, so the reproduction needs no sleeps or scheduling luck.

```sh
python3 questions/05-cache-consistency/cache_demo.py
```

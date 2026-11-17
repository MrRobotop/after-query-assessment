# Question 5 · Writing a task prompt

[Prompt to hand to the coding agent](TASK.md)

[Investigation and verification record](INVESTIGATION.md)

## Author notes

The prompt defines when the total must be correct. A read that starts after removal succeeds must reflect the committed change, including when an earlier read finishes later. The agent has to trace both the remove handler's transaction and the total endpoint's cache refill to explain the symptom.

The demo forces two cache-refill schedules against separate SQLite connections. It also checks that a rollback preserves the old total and that removing a line keeps other orders' cached totals reusable.

```sh
python3 questions/05-cache-consistency/cache_demo.py
```

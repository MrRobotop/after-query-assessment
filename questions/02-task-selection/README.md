# Question 2 · Sourcing and scoping a task

## (a) Best candidate

I’d pick (2) because an incorrect merchant balance could originate in concurrent checkout writes, Redis balance publication, or reconciliation. A controlled replay can be graded against committed ledger activity at the service’s supported visibility boundary. Most of the other tickets prescribe a change, and the CI-only flake first needs its runner conditions reproduced reliably.

## (b) Two weaker candidates

- **(1) Blank usernames.** The request already identifies the entry point, invalid input, and expected outcome, so a focused validation change and request-level test cover it.
- **(6) Shared webhook context.** As described, the target type and eight packages are already specified, so much of the apparent scope is wiring call sites and checking them with the compiler and existing tests.

## (c) Three things to inspect or run

1. **Checkout writes and commits.** Trace debit or credit requests through the ledger writes, any materialized balance update, and retry handling. Replay two distinct valid checkouts for one merchant on independent connections with a controlled overlap, then compare the committed ledger deltas and persisted balance to find lost or duplicated activity.
2. **Redis reads and fills.** Trace the merchant-facing balance endpoint through cache reads, invalidation or publication, and the database fallback. Compare a cache-hit read with a cold-cache fill that overlaps a checkout commit, recording the response, Redis value, and committed balance at the same documented visibility boundary.
3. **Nightly reconciliation.** Inspect the job’s ledger cutoff or snapshot and the conditions under which it writes a balance. Replay the job around the same checkout commits with controlled ordering, compare its output and the stored result against the correct ledger snapshot, and rerun it to check replay behavior.

## (d) Plausible wrong fix

Reduce the Redis TTL. That can shorten the lifetime of a stale entry, while an overlapping read can still publish an old value and an incorrect persisted balance will survive cache refreshes.

[Candidate comparison and a worked replay plan](INVESTIGATION.md)

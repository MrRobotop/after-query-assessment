# Question 2 · Sourcing and scoping a task

## (a) Best candidate

I’d pick (2), the incorrect merchant balance, because locating the first divergence requires tracing concurrent checkout writes, Redis balance publication, and reconciliation. A captured interleaving would give the verifier a concrete oracle in committed ledger activity, while the prescribed changes need less diagnosis and the CI-only flake first needs a repeatable reproduction.

## (b) Two weaker candidates

- **(1) Blank usernames.** The request already identifies the entry point, invalid input, and expected outcome, so a focused validation change and request-level test cover it.
- **(6) Shared webhook context.** As described, the target type and eight packages are already specified, so much of the apparent scope is wiring call sites and checking them with the compiler and existing tests.

## (c) Three things to inspect or run

1. **Checkout writes and commits.** Trace debit or credit requests through the ledger writes, any materialized balance update, and retry handling. Replay two distinct valid checkouts for one merchant on independent connections with a controlled overlap, then compare the committed ledger deltas and persisted balance to find lost or duplicated activity.
2. **Redis reads and fills.** Trace the merchant-facing balance endpoint through cache reads, invalidation or publication, and the database fallback. Compare a cache-hit read with a cold-cache fill that overlaps a checkout commit, recording the response, Redis value, and committed balance at the same documented visibility boundary.
3. **Nightly reconciliation.** Inspect the job’s ledger cutoff or snapshot and the conditions under which it writes a balance. Replay the job around the same checkout commits with controlled ordering, compare its output and the stored result against the correct ledger snapshot, and rerun it to check replay behavior.

## (d) Plausible wrong fix

Reduce the Redis TTL. That makes a stale value expire sooner, but a concurrent read can still publish it again, and a lost ledger-derived balance update would survive any number of cache refreshes.

## Evidence I would require before packaging

Capture one representative merchant timeline using sanitized request and job logs. Translate it into a local fixture with a known opening balance, distinct operation IDs, and explicit coordination at transaction or cache boundaries. Establish the supported read-visibility contract from the service before choosing assertion points. The primary check would compare the merchant-facing result with the opening balance plus the signed deltas of committed ledger operations that are visible at that point. First confirm that the baseline reproduces the discrepancy consistently. Then keep ordinary single-checkout and repeated-reconciliation cases in the existing regression suite to preserve behavior around the fix.

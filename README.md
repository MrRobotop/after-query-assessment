# AfterQuery assessment

Six answers on selecting, writing, and verifying long-horizon coding tasks. The checkout and inventory examples are small, runnable models of the assessment scenarios.

| Question | Answer and supporting work | Investigation |
| --- | --- | --- |
| 1. Programming best practices | [Median ranking and characterization tests](questions/01-median/) | [Input probes and API assumptions](questions/01-median/INVESTIGATION.md) |
| 2. Sourcing and scoping | [Concurrent merchant balance investigation](questions/02-task-selection/) | [Candidate comparison and proposed ledger replay](questions/02-task-selection/INVESTIGATION.md) |
| 3. Constructing a task | [Mixed-cart tax prompt and verification design](questions/03-tax-task/) | [Tax calculations and regression controls](questions/03-tax-task/INVESTIGATION.md) |
| 4. Reward hacking | [Inventory shortcut and deterministic lost-update demonstration](questions/04-reward-hacking/) | [Read and write sequence](questions/04-reward-hacking/INVESTIGATION.md) |
| 5. Writing a prompt | [Stale order totals prompt and cache race reproduction](questions/05-cache-consistency/) | [Two cache races and the database oracle](questions/05-cache-consistency/INVESTIGATION.md) |
| 6. Packaging a verifier | [Coupon task, executable verifier, reference patch, and known-bad patch](questions/06-coupon-verifier/) | [Price derivations and grading results](questions/06-coupon-verifier/INVESTIGATION.md) |

[Private repository I would bring to the role](PRIVATE-REPOSITORY.md)

## Run the checks

From the repository root with Python 3.11 or newer and Git installed:

```sh
python3 check.py
```

The command runs the median tests, the tax, inventory, and cache demonstrations, and the coupon verifier. The coupon demo succeeds when the baseline fails the regression checks, the reference passes every check, and the hardcoded patch passes the disclosed fixture but fails the broader checks. To grade an individual patch, see the [coupon verifier instructions](questions/06-coupon-verifier/#run-the-demonstration).

The coupon verifier also checks 1–4% and 96–99% rates deterministically. The [coupon investigation](questions/06-coupon-verifier/INVESTIGATION.md) records which partial fixes those cases reject.

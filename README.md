# AfterQuery assessment

Six answers on selecting, writing, and verifying long-horizon coding tasks. The checkout and inventory examples are small, runnable models of the assessment scenarios.

| Question | Answer and supporting work |
| --- | --- |
| 1. Programming best practices | [Median ranking and characterization tests](questions/01-median/) |
| 2. Sourcing and scoping | [Concurrent merchant balance investigation](questions/02-task-selection/) |
| 3. Constructing a task | [Mixed-cart tax prompt and verification design](questions/03-tax-task/) |
| 4. Reward hacking | [Inventory shortcut and deterministic lost-update demonstration](questions/04-reward-hacking/) |
| 5. Writing a prompt | [Stale order totals prompt and cache race reproduction](questions/05-cache-consistency/) |
| 6. Packaging a verifier | [Coupon task, executable verifier, reference patch, and known-bad patch](questions/06-coupon-verifier/) |

[Private repository I would bring to the role](PRIVATE-REPOSITORY.md)

## Run the checks

From the repository root with Python 3.11 or newer and Git installed:

```sh
python3 check.py
```

The command runs the median tests, the inventory and cache demonstrations, and the coupon verifier. The coupon demo succeeds when the baseline fails the regression checks, the reference passes every check, and the hardcoded patch passes the disclosed fixture but fails the broader checks. To grade an individual patch, see the [coupon verifier instructions](questions/06-coupon-verifier/#run-the-demonstration).

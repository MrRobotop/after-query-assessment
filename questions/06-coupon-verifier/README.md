# Question 6 · Packaging a checkout verifier

The screenshot describes a checkout service without supplying its source, so I built a small executable fixture for the pricing contract. [`agent/`](agent/) contains the candidate workspace and prompt. The rest of this directory is the reviewer package.

## (a) Fail-to-pass

One $100.00 item has a $20.00 line discount and a 10% coupon, which takes another $8.00 off the adjusted subtotal. The checkout assertion expects $72.00 and the baseline returns $70.00 because it takes the coupon from $100.00. [Fail-to-pass test](verify.py)

The other fail-to-pass cases cover a mixed cart with quantities, a coupon amount exactly halfway between two cents, and varied baskets computed with an independent `Decimal` oracle. The [reference patch](reference.patch) changes the coupon base and reuses the existing rounding function.

## (b) Pass-to-pass

- **Coupon only.** A 15% coupon on two $9.95 items should still yield $16.91, catching a skipped coupon when no line discount exists or a change in half-up rounding.
- **Line discount only.** Two $25.00 items at $5.00 off per unit plus a $7.50 item should still yield $47.50, catching a dropped discount or one applied once per line instead of once per unit.

## (c) Weak verifier test

1. The test calls a helper directly on a coupon-only cart, so it can pass while the checkout entry point still computes stacked discounts incorrectly.
2. A helper name in a comment and a log file left by an earlier run can satisfy the two artifact assertions, and the fixed sleep leaves the log disconnected from the current checkout call.

## (d) Weak debounce rubric

1. “Handles the use case correctly” lacks a binary behavioral check such as calling the wrapper repeatedly within the delay and observing a single callback with the last call’s arguments after the final quiet period.
2. Requiring `setTimeout` grades scheduler choice even though a different scheduler can produce identical call timing.

## (e) Mergeability rubric

- The response applies the percent coupon to the post-line-discount subtotal in the pricing path used by `checkout_summary`.
- The response preserves the existing half-up rounding of the coupon amount to a whole cent.
- The response preserves the public `checkout_summary` return schema.

## (f) Known-bad submission

The [known-bad patch](known-bad.patch) special-cases the $100.00 fixture and returns $72.00 for it. The mixed-cart fail-to-pass test catches it by requiring $13.16 for a different cart and coupon, where the shortcut still returns $12.73.

## Run the demonstration

From the repository root with Python 3 and Git installed, run the baseline, reference, and known-bad variants:

```sh
python3 questions/06-coupon-verifier/verify.py --demo
```

| Candidate | Fail-to-pass checks | Pass-to-pass checks |
| --- | --- | --- |
| Buggy baseline | All four fail | Both pass |
| Reference patch | All four pass | Both pass |
| Hardcoded fixture | The single-line check passes and the other three fail | Both pass |

Demo mode exits zero when these outcomes match. To grade a candidate, call the runner with its checkout module and a recorded seed:

```sh
python3 questions/06-coupon-verifier/verify.py --candidate /path/to/checkout.py --seed 403
```

For a scored run, give the agent the contents of `agent/` and run the reviewer package from a grader-controlled checkout with a grader-selected seed. The local worker calls the public checkout entry point in a separate process with the caller's permissions. In a scored environment, run the worker and candidate in a network-disabled sandbox and keep the verifier and expected results outside the sandbox.

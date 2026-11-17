# Question 3 · Constructing a long-horizon task

## (a) Task and investigation

> Support has flagged small sales-tax discrepancies on carts that mix taxable and exempt items in certain regions. Reproduce the discrepancy with the captured checkout fixture and fix the tax and order total according to the repository's regional policies. Add a checkout regression test and preserve the existing totals for unaffected regions and carts.

The same one-cent discrepancy could arise in region resolution, line-item classification, or rounding, so finding the cause requires tracing a failing replay through checkout and comparing it with the policy fixtures.

## (b) Five design concerns

- **Investigation depth.** The failing replay follows regional policy and item taxability across the checkout boundary into the tax calculation.
- **Deterministic reproduction.** The replay pins the catalog, region policy and cart, then exercises the normal checkout entry point with integer-cent inputs.
- **Behavioral verification.** The verifier compares the customer-visible tax and total with independently calculated amounts.
- **Mergeability.** A maintainer checks the patch against the existing regional policy contract and runs checkout regressions for unaffected carts.
- **Reward-hack resistance.** An evaluator-owned suite varies region policy, prices, item taxability and line order around rounding boundaries.

## Reproduce the example

The runnable model uses fictional policies to test a mixed-cart rounding failure and its controls. [Investigation and expected results](INVESTIGATION.md)

```sh
python3 -B questions/03-tax-task/tax_demo.py
```

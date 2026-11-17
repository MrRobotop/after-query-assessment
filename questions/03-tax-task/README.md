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

## Author notes

I would supply a scrubbed failing cart, the pinned regional policies, the catalog records that establish each item's taxability, and the checkout replay command. I would first run the replay on the starting revision and confirm that its result differs from a hand-calculated total. The agent needs that evidence and the repository's policy contract to tell a real regression from a regional difference.

For example, two fictional regions can share a 10% rate and use different rounding scopes. Region A rounds half up per line. Region B rounds half up once on the taxable subtotal. With two taxable five-cent lines and one exempt seven-cent line, the taxable lines each contribute half a cent before rounding. Region A collects 1 + 1 = 2 cents. Region B rounds 10% of 10 cents to 1 cent. A mixed-cart regression that falls back to subtotal rounding would produce 1 cent of tax in Region A.

| Fixture | Subtotal (¢) | Expected tax (¢) | Expected total (¢) |
| --- | ---: | ---: | ---: |
| Region A, two taxable lines and one exempt line | 17 | 2 | 19 |
| Region B, same mixed cart | 17 | 1 | 18 |
| Region A, only the two taxable lines | 10 | 2 | 12 |
| Region A, same prices with every line exempt | 17 | 0 | 17 |
| Region A, original mixed cart with the exempt line priced at 31 cents | 41 | 2 | 43 |

Keeping the rate fixed isolates rounding scope. Varying the exempt price catches a calculation that taxes the full subtotal. The evaluator would also reorder lines and add independently calculated variants using other prices and rates, including regions that legitimately use subtotal rounding. The replay matrix and the existing checkout suite would run from a trusted checkout of the verifier.

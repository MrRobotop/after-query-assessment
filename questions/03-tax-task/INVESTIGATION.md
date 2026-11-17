# Mixed-cart tax investigation

The assessment describes a symptom. The runnable example constructs one plausible cause using fictional policies and catalog items. An actual task checkout would need a scrubbed failing cart, pinned regional policy records, catalog tax codes, and a replay command that fails on the starting revision.

## Isolate the variable

1. Replay the same ordered cart for two regions sharing a rate. Capture the resolved policy key and rounding scope, so a bad region mapping is distinguishable from a later calculation error.
2. Compare the catalog taxability flags and line prices used by checkout. The taxable basis should be 10 cents for both regions. Reprice the exempt line and confirm that only the cart subtotal changes.
3. Compare the taxable basis and rounding scope seen at the calculation boundary. Region A should round each taxable line half up, and Region B should round half up once on the taxable subtotal. For the base cart, both start with two taxable five-cent lines and one exempt seven-cent line. A 10% rate gives half a cent per taxable line. Region A rounds each half cent to one cent, for two cents of tax. Region B applies 10% to the 10-cent taxable subtotal, for one cent of tax.

In the modeled fault, a mixed cart reaches checkout with the correct rate and taxability but is mistakenly routed to subtotal rounding. This predicts a one-cent shortfall in Region A and a correct result in Region B. It also predicts correct results when the cart is entirely taxable or exempt.

## Compare behavior against a fixed oracle

Amounts are in cents. The verifier stores the expected tax and total as literal fixture values calculated by hand. It compares both values at the checkout boundary.

| Replay | Subtotal | Expected tax / total | Faulty tax / total |
| --- | ---: | ---: | ---: |
| Region A mixed cart | 17 | 2 / 19 | 1 / 18 |
| Region B mixed cart | 17 | 1 / 18 | 1 / 18 |
| Region A taxable lines only | 10 | 2 / 12 | 2 / 12 |
| Region A all lines exempt | 17 | 0 / 17 | 0 / 17 |
| Region A exempt line repriced from 7¢ to 31¢ | 41 | 2 / 43 | 1 / 42 |
| Region A original mixed cart reordered | 17 | 2 / 19 | 1 / 18 |
| Region A one taxable line repriced from 5¢ to 15¢ | 27 | 3 / 30 | 2 / 29 |

The Region B control catches applying per-line rounding everywhere. The exempt-price change checks that exempt lines stay out of the taxable basis, and the order permutation tests that the position of the exempt line does not affect the outcome. The taxable-price change rules out returning a flat two-cent tax for Region A mixed carts. In an evaluation, I would run these controls, additional unpublished fixtures drawn from the same policy contract, and the existing checkout suite from an evaluator-owned checkout.

```sh
python3 -B questions/03-tax-task/tax_demo.py
```

The two checks cover both the policy-correct model and the deliberately faulty one over all seven fixtures. Four fixtures expose the fault and three serve as unaffected controls. [Executable model and checks](tax_demo.py)

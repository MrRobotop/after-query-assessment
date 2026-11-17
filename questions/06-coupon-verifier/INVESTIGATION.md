# Stacked coupon investigation

I followed the fixture’s displayed total from `checkout_summary` to `compute_cart_total`. It extends prices and per-unit discounts by quantity, then calculates the reduced subtotal. The coupon helper receives the gross subtotal in the baseline, so it discounts money the customer no longer owes. The reference patch passes the reduced subtotal to the same rounding helper. [Baseline](agent/checkout.py) · [Reference patch](reference.patch)

## Expected totals

1. **Stacked discounts.** A $100.00 line becomes $80.00 after its line discount. The 10% coupon takes $8.00 off that amount, giving $72.00. The baseline takes $10.00 off and returns $70.00.
2. **Mixed cart.** Two $7.51 items with $1.25 off each and one full-price $3.33 item give $15.85. The 17% coupon rounds from $2.6945 to $2.69, giving $13.16. The baseline uses the $18.35 gross subtotal and returns $12.73. Rounding the coupon separately for each line would give $13.15, so this case also checks where rounding happens.
3. **Half-cent boundary.** A $0.35 item with $0.10 off leaves $0.25. A 10% coupon gives 2.5 cents, which rounds up to 3 cents under the fixture’s existing policy. The total is 22 cents.
4. **Coupon-only control.** Two $9.95 items give $19.90. A 15% coupon gives $2.985, which rounds up to $2.99, leaving $16.91.
5. **Line-discount-only control.** Two $25.00 items with $5.00 off each plus a $7.50 item give $47.50. A patch that subtracts $5.00 only once would return $52.50.

The verifier calls `checkout_summary` because that is where the fixture exposes its displayed total. The suggested helper call in the question supplies only one discount. Its other assertions can be satisfied by a helper name in a comment and a leftover file. For the debounce rubric, advancing a fake clock from the final call’s deadline minus one tick to the deadline would let a reviewer check when the callback runs, how often it runs, and which arguments it receives. That behavior gives the reviewer a concrete result independent of scheduler choice. The coupon review criteria similarly name the pricing rule, rounding policy, and interface a maintainer can check independently. [Answer](README.md) · [Verifier](verify.py)

## A shortcut the first verifier missed

I tried using `adjusted_subtotal or gross_subtotal` as the coupon base. This passed all six original checks at seeds `20261117`, `403`, and `8128`, even though zero is a valid adjusted subtotal. Two $4.99 items fully covered by per-unit discounts leave $0.00 eligible. The fallback uses the $9.98 gross amount, rounds its 15% coupon to $1.50, and returns −$1.50. I added that basket as a fixed case so rejection does not depend on the seed. [Zero-subtotal test](verify.py)

## Re-run evidence

I copied the baseline into temporary candidate directories, applied the two supplied patches to separate copies, and called `verify.py --candidate` on each at seeds `20261117`, `403`, and `8128`. I graded the zero-fallback variant the same way. Each seed gave the following results, with both pass-to-pass checks green for every candidate.

| Candidate | Checks passed | Exit status |
| --- | ---: | ---: |
| Baseline | 2 of 7 | 1 |
| Reference patch | 7 of 7 | 0 |
| Hardcoded single-line result | 3 of 7 | 1 |
| Zero-subtotal fallback | 6 of 7 | 1 |

The hardcoded patch passes the first example and still returns $12.73 on the mixed cart. The fallback’s sole failure is the fully discounted cart. The local results cover the supplied pricing fixture and these sampled candidates. [Run the verifier](README.md#run-the-demonstration)

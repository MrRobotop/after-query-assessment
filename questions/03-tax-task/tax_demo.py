"""Replay a fictional checkout with and without a mixed-cart routing fault."""

import unittest
from dataclasses import dataclass


@dataclass(frozen=True)
class RegionalPolicy:
    rate_bps: int
    round_per_line: bool


POLICIES = {
    "A": RegionalPolicy(rate_bps=1000, round_per_line=True),
    "B": RegionalPolicy(rate_bps=1000, round_per_line=False),
}
CATALOG_TAXABLE = {"taxable": True, "exempt": False}
Cart = tuple[tuple[str, int], ...]
CheckoutTotals = tuple[int, int]


def round_tax_cents(amount_cents: int, rate_bps: int) -> int:
    # Half-up rounding for the nonnegative amounts in these fixtures.
    return (amount_cents * rate_bps + 5000) // 10000


def checkout_total(
    region: str, cart: Cart, *, mixed_cart_fallback: bool = False
) -> CheckoutTotals:
    policy = POLICIES[region]
    taxable_amounts = [amount for sku, amount in cart if CATALOG_TAXABLE[sku]]
    round_per_line = policy.round_per_line
    if mixed_cart_fallback and 0 < len(taxable_amounts) < len(cart):
        # Model a routing defect that loses the rounding scope on mixed carts.
        round_per_line = False

    bases = taxable_amounts if round_per_line else [sum(taxable_amounts)]
    tax = sum(round_tax_cents(amount, policy.rate_bps) for amount in bases)
    return tax, sum(amount for _, amount in cart) + tax


@dataclass(frozen=True)
class Replay:
    label: str
    region: str
    cart: Cart
    expected: CheckoutTotals
    faulty: CheckoutTotals


TAXABLE_LINES = (("taxable", 5), ("taxable", 5))
MIXED_CART = (*TAXABLE_LINES, ("exempt", 7))

# The tax and order total pairs come from the worked calculation, independent
# of the implementation's rounding arithmetic.
REPLAYS = (
    Replay("mixed cart", "A", MIXED_CART, expected=(2, 19), faulty=(1, 18)),
    Replay("subtotal policy", "B", MIXED_CART, expected=(1, 18), faulty=(1, 18)),
    Replay("taxable only", "A", TAXABLE_LINES, expected=(2, 12), faulty=(2, 12)),
    Replay(
        "exempt only", "A", (("exempt", 5), ("exempt", 5), ("exempt", 7)),
        expected=(0, 17), faulty=(0, 17),
    ),
    Replay(
        "exempt price increased", "A", (*TAXABLE_LINES, ("exempt", 31)),
        expected=(2, 43), faulty=(1, 42),
    ),
    Replay(
        "mixed cart reordered", "A", MIXED_CART[::-1],
        expected=(2, 19), faulty=(1, 18),
    ),
    Replay(
        "taxable price increased", "A", (("taxable", 15), *MIXED_CART[1:]),
        expected=(3, 30), faulty=(2, 29),
    ),
)


class TaxReplayDemo(unittest.TestCase):
    def test_policy_correct_checkout_matches_oracle(self):
        for replay in REPLAYS:
            with self.subTest(replay=replay.label):
                actual = checkout_total(replay.region, replay.cart)
                self.assertEqual(actual, replay.expected)

    def test_fallback_reproduces_the_wrong_totals(self):
        for replay in REPLAYS:
            with self.subTest(replay=replay.label):
                actual = checkout_total(
                    replay.region, replay.cart, mixed_cart_fallback=True
                )
                self.assertEqual(actual, replay.faulty)


if __name__ == "__main__":
    unittest.main(verbosity=2)

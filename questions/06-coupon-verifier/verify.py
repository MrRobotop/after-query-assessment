"""Grade a checkout candidate and demonstrate the expected verifier outcomes."""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


QUESTION_DIR = Path(__file__).resolve().parent
BASELINE = QUESTION_DIR / "agent" / "checkout.py"
FAIL_TO_PASS = (
    "test_stacked_single_line",
    "test_stacked_single_line_with_multiple_units",
    "test_stacked_mixed_cart",
    "test_coupon_rounding_at_half_cent",
    "test_coupon_on_fully_discounted_cart",
    "test_stacked_coupons_near_rate_limits",
    "test_varied_stacked_carts",
)
PASS_TO_PASS = ("test_coupon_only", "test_line_discount_only")


def cart_line(unit_price, unit_discount=0, quantity=1):
    return {
        "unit_price_cents": unit_price,
        "unit_discount_cents": unit_discount,
        "quantity": quantity,
    }


class CheckoutTests(unittest.TestCase):
    def __init__(self, method_name, candidate, seed, working_directory):
        super().__init__(method_name)
        self.candidate = candidate
        self.seed = seed
        self.working_directory = working_directory

    def assert_checkout_total(self, lines, coupon_percent, expected_cents):
        request = {"lines": lines, "coupon_percent": coupon_percent}
        worker = QUESTION_DIR / "checkout_worker.py"
        completed = subprocess.run(
            [sys.executable, "-I", "-B", str(worker), str(self.candidate)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            cwd=self.working_directory,
            env={},
            timeout=5,
        )
        if completed.returncode:
            raise RuntimeError(f"Checkout process exited with {completed.returncode}\n{completed.stderr}")
        summary = json.loads(completed.stdout)
        self.assertIs(type(summary["total_cents"]), int)
        self.assertEqual(summary, {"total_cents": expected_cents}, msg=f"checkout input {request!r}")

    def test_stacked_single_line(self):
        # A $100 unit is reduced to $80 before the $8 coupon.
        self.assert_checkout_total([cart_line(10_000, 2_000)], 10, 7_200)

    def test_stacked_single_line_with_multiple_units(self):
        # Three $10 units with $2 off each leave $24 eligible for a $2.40 coupon.
        self.assert_checkout_total([cart_line(1_000, 200, quantity=3)], 10, 2_160)

    def test_stacked_mixed_cart(self):
        # Two discounted units and a full-price item leave $15.85 eligible.
        # The 17% coupon rounds to $2.69 on the entire adjusted subtotal.
        lines = [cart_line(751, 125, quantity=2), cart_line(333)]
        self.assert_checkout_total(lines, 17, 1_316)

    def test_coupon_rounding_at_half_cent(self):
        # The adjusted 25 cents earns a 2.5-cent coupon, rounded up to 3 cents.
        self.assert_checkout_total([cart_line(35, 10)], 10, 22)

    def test_coupon_on_fully_discounted_cart(self):
        # Fully discounted items leave a valid zero subtotal and no further coupon amount.
        self.assert_checkout_total([cart_line(499, 499, quantity=2)], 15, 0)

    def test_stacked_coupons_near_rate_limits(self):
        # The $12.50 line discount leaves $87.50 eligible for each coupon.
        # Check every valid rate outside the seeded 5–95% range and the fixed 0% and 100% cases.
        lines = [cart_line(10_000, 1_250)]
        expected_totals = (
            (1, 8_662),
            (2, 8_575),
            (3, 8_487),
            (4, 8_400),
            (96, 350),
            (97, 262),
            (98, 175),
            (99, 87),
        )
        for percent, expected_cents in expected_totals:
            self.assert_checkout_total(lines, percent, expected_cents)

    def test_varied_stacked_carts(self):
        rng = random.Random(self.seed)
        for scenario in range(12):
            price = rng.randint(200, 7_000)
            lines = [cart_line(price, rng.randint(100, price), rng.randint(1, 5))]
            extra_lines = 0 if scenario % 4 == 1 else rng.randint(1, 4)
            for _ in range(extra_lines):
                price = rng.randint(1, 5_000)
                discount = 0 if scenario % 3 == 0 else rng.randint(0, price)
                lines.append(cart_line(price, discount, rng.randint(1, 3)))
            rng.shuffle(lines)
            percent = 100 if scenario == 0 else rng.randint(5, 95)
            # The verifier sums extended net prices and uses independent decimal rounding.
            net = sum(
                (line["unit_price_cents"] - line["unit_discount_cents"]) * line["quantity"]
                for line in lines
            )
            coupon = (Decimal(net) * percent / 100).quantize(Decimal(1), rounding=ROUND_HALF_UP)
            self.assert_checkout_total(lines, percent, net - int(coupon))

    def test_coupon_only(self):
        self.assert_checkout_total([cart_line(995, quantity=2)], 15, 1_691)

    def test_line_discount_only(self):
        self.assert_checkout_total([cart_line(2_500, 500, quantity=2), cart_line(750)], 0, 4_750)


def run_suite(candidate, methods, seed):
    with tempfile.TemporaryDirectory(prefix="checkout-verifier-") as working_directory:
        suite = unittest.TestSuite(
            CheckoutTests(method, candidate, seed, working_directory) for method in methods
        )
        return unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)


def run_demo(seed):
    expected_failures = {
        "baseline": set(FAIL_TO_PASS),
        "reference": set(),
        "known-bad": set(FAIL_TO_PASS) - {"test_stacked_single_line"},
    }
    all_expected = True
    with tempfile.TemporaryDirectory(prefix="checkout-demo-") as temp_dir:
        for variant, expected in expected_failures.items():
            print(f"\n{variant}", flush=True)
            variant_dir = Path(temp_dir) / variant
            variant_dir.mkdir()
            candidate = variant_dir / "checkout.py"
            shutil.copy2(BASELINE, candidate)
            if variant != "baseline":
                subprocess.run(
                    ["git", "apply", str(QUESTION_DIR / f"{variant}.patch")],
                    cwd=variant_dir,
                    check=True,
                )
            result = run_suite(candidate, FAIL_TO_PASS + PASS_TO_PASS, seed)
            failures = {test.id().rsplit(".", 1)[-1] for test, _ in result.failures}
            matches = not result.errors and failures == expected
            print(f"{variant} outcome {'matches' if matches else 'differs from'} expectations.")
            all_expected &= matches
    return int(not all_expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subject = parser.add_mutually_exclusive_group(required=True)
    subject.add_argument("--candidate", type=Path, help="Path to a checkout.py to grade")
    subject.add_argument("--demo", action="store_true", help="Run the baseline, reference, and known-bad matrix")
    parser.add_argument("--suite", choices=("all", "fail-to-pass", "pass-to-pass"), default="all")
    parser.add_argument("--seed", type=int, default=20261117, help="Seed for the varied-cart cases")
    args = parser.parse_args()
    if args.demo:
        return run_demo(args.seed)

    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error(f"Candidate file not found at {candidate}")
    methods = {
        "all": FAIL_TO_PASS + PASS_TO_PASS,
        "fail-to-pass": FAIL_TO_PASS,
        "pass-to-pass": PASS_TO_PASS,
    }[args.suite]
    return int(not run_suite(candidate, methods, args.seed).wasSuccessful())


if __name__ == "__main__":
    sys.exit(main())

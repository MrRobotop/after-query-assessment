"""A checkout pricing fixture with integer cents and whole-percent coupons.

Each line has a unit price, a per-unit discount, and a positive quantity.
Prices and discounts are nonnegative and a discount can cover the whole unit.
Coupon percentages range from 0 to 100. Coupons round half up to a cent.
"""


def _percent_discount_cents(subtotal_cents, coupon_percent):
    # Adding half the divisor rounds a nonnegative percentage half up.
    return (subtotal_cents * coupon_percent + 50) // 100


def compute_cart_total(lines, coupon_percent):
    gross_subtotal = sum(line["unit_price_cents"] * line["quantity"] for line in lines)
    line_discounts = sum(line["unit_discount_cents"] * line["quantity"] for line in lines)
    adjusted_subtotal = gross_subtotal - line_discounts
    coupon_discount = _percent_discount_cents(gross_subtotal, coupon_percent)
    return adjusted_subtotal - coupon_discount


def checkout_summary(lines, coupon_percent=0):
    """Return the total displayed at checkout."""
    return {"total_cents": compute_cart_total(lines, coupon_percent)}

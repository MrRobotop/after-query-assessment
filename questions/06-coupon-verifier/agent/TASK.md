# Stacked discounts show the wrong checkout total

Checkout applies a percent-off coupon incorrectly when the cart already has a line-item discount. On a cart with both, the total shown at checkout doesn't match what we'd expect from applying the coupon on the already-reduced price. Fix checkout so stacked discounts compute the right total.

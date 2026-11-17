# Fix stale order totals after removing an item

Under concurrent traffic, `GET /orders/{id}/total` can still include a removed line item after the removal request succeeds. Reproduce the issue and fix it so a total request that starts after a successful removal reflects the committed order, even when another total request overlaps the removal. Keep the endpoint contract, continue to reuse cached totals on warm reads, and add a regression test that reliably exercises the overlap.

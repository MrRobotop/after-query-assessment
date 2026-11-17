# Question 4 · Reward hacking

A patch could return `4` whenever `get_inventory` receives `HAT-001`. The assertion would pass because it reads through that accessor. If both checkouts read ten before either writes, each writes seven and the stored count remains seven. [Runnable example](inventory_demo.py)

```bash
python3 questions/04-reward-hacking/inventory_demo.py
```

The example uses a barrier between each read and write to force the lost update. Its tests show the baseline failing the original assertion and the shortcut passing it. A separate storage assertion still catches the lost update after both checkouts report success.

For this fixture a stronger verifier would check that both orders were recorded and read the remaining stock independently of the checkout read API. It could also vary SKU, starting stock, quantities and worker count, and include contention for insufficient stock with a check that accepted orders account for every unit deducted.

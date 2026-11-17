# Question 4 · Reward hacking

A patch could return `4` whenever `get_inventory` receives `HAT-001`. The assertion would pass because it reads through that accessor. If both checkouts read ten before either writes, each writes seven and the stored count remains seven. [Runnable example](inventory_demo.py)

```bash
python3 questions/04-reward-hacking/inventory_demo.py
```

The example reproduces the original failure and checks whether the shortcut repairs the stored count. [Worker trace and verifier findings](INVESTIGATION.md)

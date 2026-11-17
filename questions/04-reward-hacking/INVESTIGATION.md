# Inventory verifier investigation

The original test exercises one SKU with a single starting quantity and checks only what one read accessor returns. That gives the shortcut everything it needs to choose a response. I modeled the write path as a read of the SKU count followed by a write of the reduced count, and left that path identical under the shortcut.

## Reproduce the lost update

| Step | First checkout | Second checkout | Stored stock |
| --- | --- | --- | ---: |
| Seed `HAT-001` | Ready | Ready | 10 |
| Each worker reads | Reads 10, reaches barrier | Reads 10, reaches barrier | 10 |
| Both workers can write | Writes 10 − 3 | Writes 10 − 3 | 7 |
| Both calls finish | Reports success | Reports success | 7 |

The barrier releases the two workers after both have read ten. Either worker may write first. They both write the same seven, so the final count is deterministic. Two accepted checkouts of three units imply ten minus six, or four units remaining.

## Check the observable results

| Implementation | Both checkouts report success | Accessor result | Backing count | Original assertion |
| --- | --- | ---: | ---: | --- |
| Baseline write path and accessor | Yes | 7 | 7 | Fails |
| Same write path with the shortcut | Yes | 4 | 7 | Passes |

The independent check derives expected stock from accepted quantities and reads the backing store directly. It rejects seven in the shortcut case. A separate one-order control buys two units and observes eight in storage, with the shortcut still reporting four.

```sh
python3 -B questions/04-reward-hacking/inventory_demo.py
```

The three tests corroborate the baseline failure, the shortcut's false pass, and the sequential control. The backing store here is an in-memory dictionary and the demo reproduces a specific lost-update schedule. In a real service, I would reconcile persisted order quantities with an independent database read, vary SKUs and quantities, and exercise workers in separate processes when the application supports that deployment. The barrier in this demo makes the vulnerable read and write visible. An evaluator that accepts any correct synchronization scheme can coordinate worker starts outside the candidate's critical section.

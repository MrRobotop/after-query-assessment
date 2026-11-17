import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


SKU = "HAT-001"


class Inventory:
    def __init__(self):
        self.stock = {SKU: 10}

    def get_inventory(self, sku):
        return self.stock[sku]

    def checkout(self, sku, quantity, after_read):
        available = self.stock[sku]
        if quantity > available:
            return False

        # Force the two workers to act on the same snapshot for this repro.
        after_read()
        self.stock[sku] = available - quantity
        return True


class InventoryWithShortcut(Inventory):
    def get_inventory(self, sku):
        # The published check queries this SKU and expects this answer.
        if sku == SKU:
            return 4
        return super().get_inventory(sku)


def concurrent_checkouts(inventory):
    both_reads_complete = Barrier(2, timeout=5)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(inventory.checkout, SKU, 3, both_reads_complete.wait)
        second = workers.submit(inventory.checkout, SKU, 3, both_reads_complete.wait)
        return first.result(), second.result()


def original_check(inventory):
    return inventory.get_inventory(SKU) == 4


class InventoryVerifierDemo(unittest.TestCase):
    def test_original_check_fails_on_baseline(self):
        inventory = Inventory()
        concurrent_checkouts(inventory)
        self.assertFalse(original_check(inventory))
        self.assertEqual(inventory.get_inventory(SKU), 7)

    def test_shortcut_can_fool_original_check(self):
        inventory = InventoryWithShortcut()
        accepted = concurrent_checkouts(inventory)

        self.assertTrue(original_check(inventory))

        # An independent observer of storage sees a mismatch with the orders.
        self.assertEqual(accepted, (True, True))
        expected_stock = 10 - sum(accepted) * 3
        self.assertEqual(inventory.stock[SKU], 7)
        self.assertNotEqual(inventory.stock[SKU], expected_stock)


if __name__ == "__main__":
    unittest.main(verbosity=2)

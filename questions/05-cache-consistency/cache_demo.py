"""Exercise order-total cache races with separate SQLite WAL connections."""

import sqlite3
import unittest
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass(frozen=True)
class Snapshot:
    revision: int
    total_cents: int


class OrderStore:
    def __init__(self, path):
        self.path = path
        self.before_commit = lambda: None
        self.snapshot_reads = 0
        with closing(self.connect()) as connection:
            connection.executescript("""
                PRAGMA journal_mode = WAL;
                CREATE TABLE orders (id INTEGER PRIMARY KEY, revision INTEGER);
                CREATE TABLE lines (id INTEGER PRIMARY KEY, order_id INTEGER, cents INTEGER);
                INSERT INTO orders VALUES (1, 0), (2, 0);
                INSERT INTO lines VALUES (11, 1, 1200), (12, 1, 2000), (21, 2, 900);
            """)

    def connect(self):
        return sqlite3.connect(self.path)

    def revision(self, order_id):
        with closing(self.connect()) as connection:
            revision, = connection.execute(
                "SELECT revision FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            return revision

    def snapshot(self, order_id):
        self.snapshot_reads += 1
        # One statement binds the revision and total to the same committed view.
        with closing(self.connect()) as connection:
            row = connection.execute(
                """
                SELECT orders.revision, COALESCE(SUM(lines.cents), 0)
                FROM orders LEFT JOIN lines ON lines.order_id = orders.id
                WHERE orders.id = ? GROUP BY orders.id
                """,
                (order_id,),
            ).fetchone()
            return Snapshot(*row)

    @contextmanager
    def removing_line(self, order_id, line_id):
        with closing(self.connect()) as connection, connection:
            result = connection.execute(
                "DELETE FROM lines WHERE order_id = ? AND id = ?", (order_id, line_id)
            )
            if result.rowcount != 1:
                raise LookupError(line_id)
            connection.execute(
                "UPDATE orders SET revision = revision + 1 WHERE id = ?", (order_id,)
            )
            yield
            self.before_commit()


class TotalCache(dict):
    def __init__(self):
        super().__init__()
        self.before_fill = lambda: None

    def fill(self, order_id, snapshot):
        self.before_fill()
        self[order_id] = snapshot


class Checkout:
    def __init__(self, store, cache):
        self.store = store
        self.cache = cache

    def get_total(self, order_id):
        snapshot = self.cache.get(order_id)
        if snapshot is None:
            snapshot = self.store.snapshot(order_id)
            self.cache.fill(order_id, snapshot)
        return snapshot.total_cents

    def remove_line(self, order_id, line_id):
        with self.store.removing_line(order_id, line_id):
            self.cache.pop(order_id, None)


class DeleteAfterCommit(Checkout):
    def remove_line(self, order_id, line_id):
        with self.store.removing_line(order_id, line_id):
            pass
        self.cache.pop(order_id, None)


class RevisionAwareCheckout(DeleteAfterCommit):
    def get_total(self, order_id):
        snapshot = self.cache.get(order_id)
        if snapshot is None or snapshot.revision != self.store.revision(order_id):
            snapshot = self.store.snapshot(order_id)
            self.cache.fill(order_id, snapshot)
        return snapshot.total_cents


class CacheReproduction(unittest.TestCase):
    def services(self, implementation):
        directory = self.enterContext(TemporaryDirectory())
        store = OrderStore(Path(directory) / "orders.sqlite")
        cache = TotalCache()
        return implementation(store, cache), implementation(store, cache)

    def fill_before_commit(self, implementation):
        writer, reader = self.services(implementation)
        writer.store.before_commit = lambda: self.assertEqual(reader.get_total(1), 3200)
        writer.remove_line(1, 11)
        self.assertEqual(writer.store.snapshot(1).total_cents, 2000)
        return reader.get_total(1)

    def fill_after_commit(self, implementation):
        writer, reader = self.services(implementation)
        reader.cache.before_fill = lambda: writer.remove_line(1, 11)
        self.assertEqual(reader.get_total(1), 3200)
        reader.cache.before_fill = lambda: None
        self.assertEqual(writer.store.snapshot(1).total_cents, 2000)
        return reader.get_total(1)

    def test_pre_commit_delete_leaks_stale_cache_fills(self):
        self.assertEqual(self.fill_before_commit(Checkout), 3200)
        self.assertEqual(self.fill_after_commit(Checkout), 3200)

    def test_post_commit_delete_can_still_lose_to_a_late_fill(self):
        self.assertEqual(self.fill_before_commit(DeleteAfterCommit), 2000)
        self.assertEqual(self.fill_after_commit(DeleteAfterCommit), 3200)

    def test_revision_aware_checkout_survives_both_interleavings(self):
        self.assertEqual(self.fill_before_commit(RevisionAwareCheckout), 2000)
        self.assertEqual(self.fill_after_commit(RevisionAwareCheckout), 2000)

    def test_warm_hits_rollback_and_order_isolation(self):
        writer, reader = self.services(RevisionAwareCheckout)
        self.assertEqual(reader.get_total(1), 3200)
        self.assertEqual(reader.get_total(2), 900)
        self.assertEqual(writer.store.snapshot_reads, 2)

        def fail_commit():
            raise RuntimeError("injected rollback")

        writer.store.before_commit = fail_commit
        with self.assertRaisesRegex(RuntimeError, "injected rollback"):
            writer.remove_line(1, 11)
        self.assertEqual(reader.get_total(1), 3200)
        self.assertEqual(reader.get_total(2), 900)
        self.assertEqual(writer.store.snapshot_reads, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

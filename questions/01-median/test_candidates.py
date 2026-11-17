"""Characterization tests for the supplied implementations, including defects."""

from decimal import Decimal
from unittest import TestCase

from candidates import median_a, median_b, median_c


class MedianCandidatesTest(TestCase):
    def test_a_floors_a_fractional_median_and_mutates_the_input(self):
        # An unsorted pair with an odd sum exposes both behaviors in one call.
        nums = [3, 0]
        self.assertEqual(median_a(nums), 1)
        self.assertEqual(nums, [0, 3])

    def test_b_and_c_preserve_input_and_fraction(self):
        for median in (median_b, median_c):
            with self.subTest(candidate=median.__name__):
                nums = [3, 0]
                self.assertEqual(median(nums), 1.5)
                self.assertEqual(nums, [3, 0])

    def test_empty_sequence(self):
        self.assertIsNone(median_c([]))
        for median in (median_a, median_b):
            with self.subTest(candidate=median.__name__):
                with self.assertRaises(IndexError):
                    median([])

    def test_decimal_requires_a_compatible_divisor(self):
        nums = [Decimal("0.20"), Decimal("0.30")]
        self.assertEqual(median_c(nums), Decimal("0.25"))
        with self.assertRaises(TypeError):
            median_b(nums)

    def test_empty_iterable_exposes_the_limit_of_cs_guard(self):
        # An empty generator is truthy before sorted() consumes it.
        with self.assertRaises(IndexError):
            median_c(value for value in ())

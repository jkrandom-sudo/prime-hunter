"""Tests for Prime Hunter core."""
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import prime_hunter as core


class TestPrime(unittest.TestCase):
    def test_config_default(self):
        self.assertEqual(core.config("bad"), core.config("normal"))

    def test_small_non_primes(self):
        for n in (-1, 0, 1):
            self.assertFalse(core.is_prime(n))

    def test_primes(self):
        for n in (2, 3, 5, 97, 149):
            self.assertTrue(core.is_prime(n))

    def test_composites(self):
        for n in (4, 9, 21, 100, 221):
            self.assertFalse(core.is_prime(n))

    def test_factor_hint_prime(self):
        self.assertIsNone(core.factor_hint(17))

    def test_factor_hint_composite(self):
        self.assertEqual(core.factor_hint(21), 3)
        self.assertEqual(core.factor_hint(1), 1)

    def test_make_number_range(self):
        for difficulty in ("easy", "normal", "hard"):
            n = core.make_number(difficulty, random.Random(0))
            self.assertGreaterEqual(n, 1)
            self.assertLessEqual(n, core.config(difficulty)["max_num"])


class TestAnswers(unittest.TestCase):
    def test_normalize_prime(self):
        self.assertTrue(core.normalize_answer("p"))
        self.assertTrue(core.normalize_answer("质数"))

    def test_normalize_composite(self):
        self.assertFalse(core.normalize_answer("c"))
        self.assertFalse(core.normalize_answer("合数"))

    def test_normalize_invalid(self):
        self.assertIsNone(core.normalize_answer("x"))

    def test_answer_correct(self):
        self.assertTrue(core.answer_correct(7, "p"))
        self.assertTrue(core.answer_correct(8, "c"))
        self.assertFalse(core.answer_correct(7, "c"))


class TestScoring(unittest.TestCase):
    def test_points_easy(self):
        self.assertEqual(core.points_for("easy", 1), 10)
        self.assertEqual(core.points_for("easy", 3), 20)

    def test_points_hint(self):
        self.assertEqual(core.points_for("easy", 2, True), 7)

    def test_points_unknown(self):
        self.assertEqual(core.points_for("bad", 1), 15)

    def test_final_rating_win(self):
        self.assertEqual(core.final_rating(8, 10), "win")

    def test_final_rating_draw(self):
        self.assertEqual(core.final_rating(5, 10), "draw")

    def test_final_rating_loss(self):
        self.assertEqual(core.final_rating(4, 10), "loss")

    def test_final_rating_zero(self):
        self.assertEqual(core.final_rating(0, 0), "loss")


if __name__ == "__main__":
    unittest.main()

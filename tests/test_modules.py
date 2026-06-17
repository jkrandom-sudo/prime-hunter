"""Tests for support modules."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import i18n
import score as score_mod
import settings as settings_mod
from sound import Sound


class TestI18n(unittest.TestCase):
    def test_keys_match(self):
        self.assertEqual(set(i18n.STRINGS["zh"].keys()), set(i18n.STRINGS["en"].keys()))

    def test_t_basic(self):
        self.assertEqual(i18n.t("en", "title"), "Prime Hunter")

    def test_t_kwargs(self):
        self.assertIn("7", i18n.t("en", "correct", points=7))

    def test_t_missing_lang(self):
        self.assertEqual(i18n.t("xx", "title"), "Prime Hunter")

    def test_t_missing_key(self):
        self.assertEqual(i18n.t("en", "missing"), "missing")

    def test_format_failure(self):
        self.assertIsInstance(i18n.t("en", "correct"), str)


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = Path(self.tmp) / "s.json"

    def test_defaults(self):
        s = settings_mod.load(self.path)
        self.assertEqual(s["lang"], "zh")
        self.assertTrue(s["sound"])
        self.assertEqual(s["volume"], 1)
        self.assertEqual(s["difficulty"], "normal")

    def test_round_trip(self):
        s = {"lang": "en", "sound": False, "volume": 3, "difficulty": "hard"}
        settings_mod.save(s, self.path)
        self.assertEqual(settings_mod.load(self.path), s)

    def test_invalid_values_reset(self):
        settings_mod.save({"lang": "fr", "sound": "yes", "volume": 9, "difficulty": "bad"}, self.path)
        s = settings_mod.load(self.path)
        self.assertEqual(s["lang"], "zh")
        self.assertTrue(s["sound"])
        self.assertEqual(s["volume"], 1)
        self.assertEqual(s["difficulty"], "normal")

    def test_cycle_lang(self):
        s = {"lang": "zh"}
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "en")

    def test_toggle_sound(self):
        s = {"sound": True}
        settings_mod.toggle_sound(s)
        self.assertFalse(s["sound"])

    def test_cycle_volume(self):
        s = {"volume": 1}
        for expected in (2, 3, 0, 1):
            settings_mod.cycle_volume(s)
            self.assertEqual(s["volume"], expected)

    def test_cycle_difficulty(self):
        s = {"difficulty": "easy"}
        for expected in ("normal", "hard", "easy"):
            settings_mod.cycle_difficulty(s)
            self.assertEqual(s["difficulty"], expected)


class TestScore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = Path(self.tmp) / "scores.json"

    def test_empty(self):
        self.assertEqual(score_mod.load(self.path), [])

    def test_add(self):
        score_mod.add("Alice", 10, "easy", self.path)
        self.assertEqual(score_mod.load(self.path)[0]["name"], "Alice")

    def test_sorted_limited(self):
        for i in range(15):
            score_mod.add(f"P{i}", i, "normal", self.path)
        scores = score_mod.load(self.path)
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0]["score"], 14)


class TestSound(unittest.TestCase):
    def _make(self, **kw):
        self.buf = []

        class Out:
            def write(_self, s): self.buf.append(s)
            def flush(_self): pass

        kw.setdefault("output", Out())
        kw.setdefault("enabled", True)
        kw.setdefault("volume", 1)
        return Sound(**kw)

    def test_correct(self):
        self._make().correct()
        self.assertEqual(self.buf, ["\a"])

    def test_incorrect(self):
        self._make().incorrect()
        self.assertEqual(self.buf, ["\a\a"])

    def test_win(self):
        self._make().win()
        self.assertEqual(self.buf, ["\a\a\a"])

    def test_disabled(self):
        self._make(enabled=False).correct()
        self.assertEqual(self.buf, [])

    def test_volume_multiplies(self):
        self._make(volume=3).correct()
        self.assertEqual(self.buf, ["\a\a\a"])


if __name__ == "__main__":
    unittest.main()

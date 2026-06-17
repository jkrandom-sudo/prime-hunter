"""Tests for game flow."""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import game
import score as score_mod
import settings as settings_mod


class StackedInput:
    def __init__(self, lines):
        self.lines = list(lines)
        self.idx = 0

    def __call__(self, prompt=""):
        if self.idx >= len(self.lines):
            raise EOFError()
        value = self.lines[self.idx]
        self.idx += 1
        return value


def _stub(**overrides):
    s = {"lang": "en", "sound": False, "volume": 0, "difficulty": "easy"}
    s.update(overrides)
    return s


class TestMenus(unittest.TestCase):
    def test_help(self):
        out = io.StringIO()
        game.show_help(_stub(), StackedInput([""]), out)
        self.assertIn("Help", out.getvalue())

    def test_scores_empty(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(score_mod, "DEFAULT_PATH", Path(tmp) / "scores.json"):
                game.show_scores(_stub(), StackedInput([""]), out)
        self.assertIn("No scores", out.getvalue())

    def test_scores_entry(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(score_mod, "DEFAULT_PATH", Path(tmp) / "scores.json"):
                score_mod.add("Alice", 20, "easy")
                game.show_scores(_stub(), StackedInput([""]), out)
        self.assertIn("Alice", out.getvalue())

    def test_settings_back(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH", Path(tmp) / "s.json"):
                game.settings_menu(_stub(), StackedInput(["b"]), out)

    def test_settings_cycle_lang(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH", Path(tmp) / "s.json"):
                s = _stub(lang="zh")
                game.settings_menu(s, StackedInput(["1", "b"]), out)
        self.assertEqual(s["lang"], "en")

    def test_settings_unknown(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(settings_mod, "DEFAULT_PATH", Path(tmp) / "s.json"):
                game.settings_menu(_stub(), StackedInput(["x", "b"]), out)
        self.assertIn("Unknown", out.getvalue())


class TestPlayRound(unittest.TestCase):
    def test_quit_returns_none(self):
        out = io.StringIO()
        with mock.patch.object(game.core, "make_number", return_value=7):
            result = game.play_round(_stub(), mock.MagicMock(), StackedInput(["q"]), out)
        self.assertIsNone(result)

    def test_eof_raises(self):
        out = io.StringIO()
        with mock.patch.object(game.core, "make_number", return_value=7):
            with self.assertRaises(game.QuitGame):
                game.play_round(_stub(), mock.MagicMock(), StackedInput([]), out)

    def test_all_correct_win(self):
        out = io.StringIO()
        sound = mock.MagicMock()
        nums = [2, 4, 5, 6, 7, 8, 11, 12]
        with mock.patch.object(game.core, "make_number", side_effect=nums):
            result = game.play_round(_stub(), sound,
                                     StackedInput(["p", "c", "p", "c", "p", "c", "p", "c"]), out)
        self.assertEqual(result["result"], "win")
        self.assertEqual(result["correct"], 8)
        self.assertEqual(result["score"], 220)
        sound.win.assert_called_once()

    def test_all_wrong_loss(self):
        out = io.StringIO()
        sound = mock.MagicMock()
        with mock.patch.object(game.core, "make_number", return_value=7):
            result = game.play_round(_stub(), sound, StackedInput(["c"] * 8), out)
        self.assertEqual(result["result"], "loss")
        self.assertEqual(result["correct"], 0)
        sound.lose.assert_called_once()

    def test_hint_halves_points(self):
        out = io.StringIO()
        with mock.patch.object(game.core, "make_number", return_value=9):
            result = game.play_round(_stub(), mock.MagicMock(), StackedInput(["hint", "c"] + ["p"] * 7), out)
        self.assertEqual(result["score"], 5)
        self.assertIn("divisible", out.getvalue())

    def test_invalid_answer_retries(self):
        out = io.StringIO()
        with mock.patch.object(game.core, "make_number", return_value=7):
            result = game.play_round(_stub(), mock.MagicMock(), StackedInput(["x", "p"] + ["c"] * 7), out)
        self.assertEqual(result["correct"], 1)
        self.assertIn("Invalid", out.getvalue())


class TestMainMenu(unittest.TestCase):
    def _ctx(self, tmp):
        return (mock.patch.object(settings_mod, "DEFAULT_PATH", Path(tmp) / "s.json"),
                mock.patch.object(score_mod, "DEFAULT_PATH", Path(tmp) / "scores.json"))

    def test_quit(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["q"]), out)
        self.assertIn("Bye", out.getvalue())

    def test_help(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["h", "", "q"]), out)
        self.assertIn("Help", out.getvalue())

    def test_play_save_score(self):
        fake = {"result": "win", "score": 20, "correct": 1,
                "rounds": 1, "best_streak": 1, "difficulty": "easy"}
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_round", return_value=fake):
                    game.main_menu(StackedInput(["p", "Bob", "q"]), out)
                scores = score_mod.load()
        self.assertEqual(scores[0]["name"], "Bob")

    def test_play_no_name(self):
        fake = {"result": "win", "score": 20, "correct": 1,
                "rounds": 1, "best_streak": 1, "difficulty": "easy"}
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_round", return_value=fake):
                    game.main_menu(StackedInput(["p", "", "q"]), out)
                self.assertEqual(score_mod.load(), [])

    def test_play_quit_propagates(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                with mock.patch.object(game, "play_round", side_effect=game.QuitGame()):
                    game.main_menu(StackedInput(["p"]), out)
        self.assertIn("Bye", out.getvalue())

    def test_unknown(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput(["x", "q"]), out)
        self.assertIn("Unknown", out.getvalue())

    def test_eof(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            p1, p2 = self._ctx(tmp)
            with p1, p2:
                settings_mod.save(_stub())
                game.main_menu(StackedInput([]), out)
        self.assertIn("Bye", out.getvalue())


if __name__ == "__main__":
    unittest.main()

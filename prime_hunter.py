"""Core logic for Prime Hunter."""
import random

DIFFICULTY_CONFIG = {
    "easy": {"rounds": 8, "max_num": 50, "base": 10},
    "normal": {"rounds": 10, "max_num": 150, "base": 15},
    "hard": {"rounds": 12, "max_num": 300, "base": 25},
}


def config(difficulty):
    return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["normal"])


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def factor_hint(n):
    if is_prime(n):
        return None
    if n < 2:
        return 1
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return d
    return n


def make_number(difficulty, rng=None):
    rng = rng or random
    return rng.randint(1, config(difficulty)["max_num"])


def normalize_answer(text):
    text = text.strip().lower()
    if text in ("p", "prime", "yes", "y", "质数", "是"):
        return True
    if text in ("c", "composite", "no", "n", "合数", "否"):
        return False
    return None


def answer_correct(n, text):
    answer = normalize_answer(text)
    return answer is not None and answer == is_prime(n)


def points_for(difficulty, streak, used_hint=False):
    base = config(difficulty)["base"]
    points = base + max(0, streak - 1) * 5
    if used_hint:
        points //= 2
    return max(1, points)


def final_rating(correct, rounds):
    if rounds <= 0:
        return "loss"
    ratio = correct / rounds
    if ratio >= 0.75:
        return "win"
    if ratio >= 0.5:
        return "draw"
    return "loss"

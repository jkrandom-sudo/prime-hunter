"""Score persistence."""
import json
from pathlib import Path

DEFAULT_PATH = Path.home() / ".prime_hunter_scores.json"
MAX_SCORES = 10


def load(path=None):
    if path is None:
        path = DEFAULT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []


def save(scores, path=None):
    if path is None:
        path = DEFAULT_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores[:MAX_SCORES], f, ensure_ascii=False, indent=2)


def add(name, score, difficulty, path=None):
    scores = load(path)
    scores.append({"name": name, "score": score, "difficulty": difficulty})
    scores.sort(key=lambda item: item.get("score", 0), reverse=True)
    save(scores, path)

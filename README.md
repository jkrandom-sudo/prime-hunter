# 质数猎人 / Prime Hunter

一个使用 Python 标准库实现的控制台质数判断小游戏。玩家需要判断给出的数字是否为质数，可使用因子提示，但提示会降低得分。支持中英双语、难度设置、音效、音量、排行榜和自动化测试。

A pure Python standard-library console prime-number game. Decide whether each number is prime or composite. You can request a factor hint, but hints reduce the points for that round. Includes bilingual zh/en UI, difficulty settings, terminal sound, volume control, score history, and automated tests.

## 功能 / Features

- 纯 Python 标准库，无第三方依赖 / Pure Python stdlib, no third-party dependencies
- 判断质数或合数 / Classify numbers as prime or composite
- `hint` 提供因子提示，或提示没有小因子 / `hint` gives a factor clue or says no small factor was found
- 连对加分 / Streak bonus scoring
- 中英双语界面，可在设置中切换 / Bilingual zh/en UI with language toggle
- 三档难度：easy / normal / hard / Three difficulty levels
- JSON 持久化设置和排行榜 / JSON-persistent settings and top scores
- 终端铃声音效，音量 0-3 / Terminal bell sound with volume 0-3
- 自动化测试覆盖核心逻辑、菜单、设置、音效和分数 / Automated tests for core logic, menus, settings, sound, and scores

## 快速开始 / Quick start

```bash
cd ~/games/prime-hunter
python3 game.py
```

## 操作 / Controls

主菜单 / Main menu:

| 输入 / Input | 作用 / Action |
|---|---|
| `p` | 开始游戏 / play |
| `h` | 查看帮助 / help |
| `s` | 设置语言、音效、音量、难度 / settings |
| `c` | 查看排行榜 / scores |
| `q` | 退出 / quit |

游戏中 / During a round:

| 输入 / Input | 作用 / Action |
|---|---|
| `p` / `prime` / `质数` | 判断为质数 / answer prime |
| `c` / `composite` / `合数` | 判断为合数 / answer composite |
| `hint` | 查看提示，本题得分减半 / show hint and halve points |
| `q` | 退出本轮 / quit round |

## 难度与计分 / Difficulty and scoring

| 难度 / Difficulty | 轮数 / Rounds | 最大数字 / Max number | 基础分 / Base |
|---|---:|---:|---:|
| easy | 8 | 50 | 10 |
| normal | 10 | 150 | 15 |
| hard | 12 | 300 | 25 |

正确得分 / Correct answer points:

```text
base + (streak - 1) * 5
```

如果使用提示，本题得分减半。
If a hint is used, points for that round are halved.

比赛评级 / Result rating:

- 正确率 >= 75%：胜利 / win
- 正确率 >= 50%：平局 / draw
- 否则：失败 / loss

## 测试 / Tests

```bash
cd ~/games/prime-hunter
python3 -m py_compile game.py prime_hunter.py i18n.py settings.py score.py sound.py
python3 tests/run_tests.py
```

当前测试数量 / Current test count: 58.

## 文件结构 / Project layout

```text
prime-hunter/
├── game.py          # 主菜单与交互流程 / menus and gameplay
├── prime_hunter.py  # 核心质数与计分逻辑 / core prime and scoring logic
├── i18n.py          # 中英文本 / bilingual strings
├── settings.py      # 设置保存 / settings persistence
├── score.py         # 排行榜 / scoreboard
├── sound.py         # 终端音效 / terminal sound
└── tests/
    ├── test_core.py
    ├── test_game.py
    ├── test_modules.py
    └── run_tests.py
```

# Tutorial 1 — Agents, hands on

A worked walkthrough of the AIMA vacuum-world agents tutorial.

## What's here

| File | What it is |
|---|---|
| `Tutorial_1_Agents_Hands_On_solved.ipynb` | The original notebook with all four exercises solved, executed end to end (outputs are real, not transcribed) |
| `vacuum-world-walkthrough.html` | A standalone study guide: every line of code explained, every output shown, full exercise write-ups |
| `Vacuum-World-Line-by-Line.pdf` | The same guide as a 52-page PDF |

## Rebuilding the guide

The HTML is generated from the executed notebook, so the code shown can never drift
from the code that ran:

```bash
pip install nbformat nbclient ipykernel
python3 render.py          # reads the .ipynb, writes vacuum-world-walkthrough.html
```

| Module | Role |
|---|---|
| `hl.py` | Minimal Python syntax highlighter with line numbering |
| `shell.py` | The stylesheet (light/dark tokens + print styles) |
| `build.py` | Page assembly and helpers; pulls source and outputs from the notebook |
| `content_a/b/c.py` | The prose and the per-line annotations |

## The four exercises, in one line each

1. **Stochastic dirt** — beliefs that never expire go stale; the fix is an expiry date, not less memory.
2. **Partial observability** — memoryless agents break silently; internal state buys back the observability the sensors lost.
3. **A row of four** — a fixed direction rule oscillates at the wall, because direction of travel is state.
4. **Time pressure** — a deadline term makes the agent give up on its own, with no "if late, stop" branch anywhere.

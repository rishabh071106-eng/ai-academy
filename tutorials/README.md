# AI Academy — worked tutorials

Solved notebooks and generated study guides for the hands-on tutorial series.

## Tutorial 1 — Agents (vacuum world)

| File | What it is |
|---|---|
| `Tutorial_1_Agents_Hands_On_solved.ipynb` | The notebook with all four exercises solved, executed end to end |
| `vacuum-world-walkthrough.html` | Study guide: every line explained, every output shown |
| `Vacuum-World-Line-by-Line.pdf` | The same guide, 52 pages |

Written for readers new to Python: a "Python you need" primer, then a Python box on
172 of its 176 line annotations explaining the syntax on that specific line.

**What the exercises turned up.** The goal-based agent has no goal test (so it never
stops); the utility agent never travels, and only scored well because it started on the
dirty square; the model-based agent trusts stale beliefs; and the reflex agent
oscillates at walls once there are more than two squares.

## Tutorial 2 — Transformer architecture (attention from scratch)

| File | What it is |
|---|---|
| `Tutorial_2_Transformer_Architecture_SOLVED.ipynb` | All twelve exercises solved, executed end to end |
| `attention-worked-out.html` | Study guide: the mathematics derived, every line explained |
| `Attention-Worked-Out.pdf` | The same guide, 80 pages |

Covers the full derivation — why the dot product, why `1/sqrt(d_k)` (the variance
argument), the softmax Jacobian and why saturation kills gradients, the positional
encoding rotation identity, layer-norm scale invariance, and why residuals are what
make depth trainable.

**What the exercises turned up.**

1. The custom-sentence skeleton says `Q, K, V = X, X, X`, silently reusing the previous
   sentence's matrix. It must be `X_demo`.
2. Final Exercise 1's suggested method cannot demonstrate its own point: zero-padding
   leaves `Q @ K.T` unchanged, so scaling gets *flatter*, not peakier. Shown as written
   (Part A), then properly with random vectors (Part B), where the gradient scale falls
   ~44x from `d_k=8` to `d_k=1024`.
3. Final Exercise 3's premise is wrong in an instructive way: `num_heads=8` with
   `d_model=8` does not break — it runs fine and degrades silently to rank-1 attention.
   Verified by measuring the score matrix rank.
4. Stacking `encoder_block` twice adds positional encoding twice. No error, no shape
   mismatch, just wrong numbers.

## Rebuilding the guides

Both HTML files are generated from their executed notebooks, so the code shown can never
drift from the code that produced the outputs.

```bash
pip install nbformat nbclient ipykernel numpy matplotlib
python3 render.py     # Tutorial 1 -> vacuum-world-walkthrough.html
python3 render2.py    # Tutorial 2 -> attention-worked-out.html
```

| Module | Role |
|---|---|
| `hl.py` | Python syntax highlighter with line numbering (shared) |
| `shell.py` / `shell2.py` | Stylesheets — light/dark tokens plus print styles |
| `build.py` / `build2.py` | Page assembly; pulls source, outputs and figures from the notebooks |
| `content_*.py` / `content2_*.py` | Prose and per-line annotations |
| `pynotes.py` / `pynotes2.py` | Per-line Python-syntax explanations |
| `mathsvg.py` | LaTeX → inline SVG math (see below) |
| `checkmath.py` | Renders every formula in the content modules and reports failures |

### How the math is rendered

The Artifact CSP blocks external scripts, so MathJax and KaTeX are unavailable.
Instead `mathsvg.py` renders each formula with matplotlib's mathtext at
`svg.fonttype='path'`, which emits glyphs as `<path>` elements with no explicit fill.
Since SVG's `fill` is inherited, `fill: currentColor` on the root makes every formula
follow the surrounding text colour — so it stays readable in both themes for free.
Baselines are aligned using mathtext's reported descent.

matplotlib's mathtext does not support `\begin{bmatrix}`, `\underbrace` or `\big`.
Matrices are built as a small CSS grid component instead; run `checkmath.py` after
editing formulas to catch unsupported commands before they reach the page.

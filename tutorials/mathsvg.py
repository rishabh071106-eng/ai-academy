"""Render LaTeX math to inline SVG that inherits the page's text colour.

The Artifact CSP blocks external scripts, so MathJax/KaTeX are not an option.
matplotlib's mathtext renders the formula; svg.fonttype='path' turns every glyph
into a <path> with no explicit fill; and because SVG's `fill` is inherited,
`fill: currentColor` on the root <svg> makes the formula follow the surrounding
text colour and stay legible in both themes.

Baselines: mathtext reports (width, height, descent) in points, so the figure is
sized exactly to the ink box and the SVG is given a negative vertical-align of
descent/fontsize em -- which puts the formula's baseline on the text baseline.
"""
import io, re, functools
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath

plt.rcParams["svg.fonttype"] = "path"
plt.rcParams["mathtext.fontset"] = "cm"

_T2P = TextToPath()
_PAD = 1.0     # points of breathing room so glyphs are never clipped


@functools.lru_cache(maxsize=512)
def _svg(tex, fontsize):
    s = "$%s$" % tex
    prop = FontProperties(size=fontsize)
    w, h, d = _T2P.get_text_width_height_descent(s, prop, ismath=True)
    W, H = w + 2 * _PAD, h + 2 * _PAD
    fig = plt.figure(figsize=(W / 72.0, H / 72.0))
    # place the text with its baseline (d + pad) up from the bottom of the figure
    fig.text(_PAD / W, (d + _PAD) / H, s, fontsize=fontsize, ha="left", va="baseline")
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", transparent=True)
    plt.close(fig)

    svg = buf.getvalue().decode("utf-8")
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    svg = re.sub(r'\swidth="[^"]*pt"', "", svg, count=1)
    svg = re.sub(r'\sheight="[^"]*pt"', "", svg, count=1)
    return svg, W, H, d + _PAD


def imath(tex, fontsize=15.5):
    """Inline math, baseline-aligned with the surrounding text."""
    svg, w, h, desc = _svg(tex, fontsize)
    style = ("height:%.3fem;width:%.3fem;vertical-align:%.3fem"
             % (h / fontsize, w / fontsize, -desc / fontsize))
    return svg.replace("<svg ", '<svg class="mi" style="%s" ' % style, 1)


def dmath(tex, fontsize=19, label=None):
    """A centred display equation, optionally tagged."""
    svg, w, h, _ = _svg(tex, fontsize)
    svg = svg.replace("<svg ", '<svg class="md" style="height:%.3fem;width:%.3fem" '
                      % (h / fontsize, w / fontsize), 1)
    tag = '<span class="eqtag">%s</span>' % label if label else ""
    return '<div class="eqwrap"><div class="eq">%s</div>%s</div>' % (svg, tag)

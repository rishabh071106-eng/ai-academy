import nbformat, html
from hl import code_block, out_block, esc
from shell2 import CSS2
from mathsvg import imath, dmath
from pynotes2 import PYNOTES2

NB = nbformat.read('Tutorial_2_Transformer_Architecture_SOLVED.ipynb', as_version=4)

M = imath
E = dmath


def src(i):
    return ''.join(NB.cells[i].source).rstrip('\n')


def out(i):
    return ''.join(o.get('text', '') for o in NB.cells[i].get('outputs', [])
                   if o.output_type == 'stream')


def img(i, n=0):
    """The n-th PNG figure produced by cell i, as a data URI."""
    pics = [o['data']['image/png'] for o in NB.cells[i].get('outputs', [])
            if 'image/png' in o.get('data', {})]
    return 'data:image/png;base64,' + pics[n].replace('\n', '')


def figure(i, caption, n=0):
    return ('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>'
            % (img(i, n), esc(caption.replace('<strong>', '').replace('</strong>', '')), caption))


def code(i, cap=None):
    head = '<p class="codecap">%s</p>' % cap if cap else ''
    return head + code_block(src(i))


def ann(rows, sec=None):
    notes = PYNOTES2.get(sec, {}) if sec else {}
    parts = []
    for r in rows:
        extra = r[2] if len(r) > 2 else notes.get(r[0])
        block = ('<div class="pynote"><span class="pytag">Python</span>%s</div>' % extra) if extra else ''
        parts.append('<div class="ann-row"><div class="lref">%s</div>'
                     '<div class="atxt">%s%s</div></div>' % (r[0], r[1], block))
    return '<div class="ann">%s</div>' % "".join(parts)


def outp(i, label="Output", head=None, tail=None):
    t = out(i)
    if head:
        t = "\n".join(t.split("\n")[:head])
    if tail:
        t = "\n".join(t.split("\n")[-tail:])
    return out_block(t, label)


def raw_out(text, label="Output"):
    return out_block(text, label)


def mat(rows):
    """A bracketed matrix; each cell is any HTML (typically inline math)."""
    cols = max(len(r) for r in rows)
    cells = "".join('<span>%s</span>' % c for r in rows for c in r)
    return ('<span class="mtx"><span class="mtx-grid" '
            'style="grid-template-columns:repeat(%d,auto)">%s</span></span>' % (cols, cells))


def eqline(parts, label=None):
    """Lay out a display equation from mixed pieces (math SVG, matrices, operators)."""
    body = "".join(p if p.startswith("<") else '<span class="eqop">%s</span>' % p
                   for p in parts)
    tag = '<span class="eqtag">%s</span>' % label if label else ""
    return '<div class="eqwrap"><div class="eq"><span class="eqline">%s</span></div>%s</div>' % (body, tag)


def note(tag, body):
    return '<div class="note"><span class="tag">%s</span>%s</div>' % (tag, body)


def warn(tag, body):
    return '<div class="warn"><span class="tag">%s</span>%s</div>' % (tag, body)


def concept(tag, body):
    return '<div class="concept"><span class="tag">%s</span>%s</div>' % (tag, body)


def table(headers, rows, aligns=None):
    aligns = aligns or [''] * len(headers)
    th = "".join('<th>%s</th>' % h for h in headers)
    trs = "".join('<tr>%s</tr>' % "".join(
        '<td%s>%s</td>' % (' class="num"' if aligns[i] == 'n' else '', c)
        for i, c in enumerate(r)) for r in rows)
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (th, trs))


def page(sections):
    rail = "".join('<li><a href="#%s"><span class="rn">%s</span><span>%s</span></a></li>'
                   % (s['id'], s['num'], s['rail']) for s in sections)
    body = "".join('<section id="%s"><h2><span class="snum">%s</span><span>%s</span></h2>%s</section>'
                   % (s['id'], s['num'], s['title'], s['body']) for s in sections)
    return TEMPLATE % (CSS2, rail, body)


TEMPLATE = """<title>Attention, Worked Out</title>
%s
<div class="layout">
<nav class="rail" aria-label="Contents">
  <p class="rail-title">Contents</p>
  <ol>%s</ol>
</nav>
<main>
<header class="masthead">
  <p class="eyebrow"><span>Tutorial 2</span><span class="dot"></span>
     <span>Transformer architecture</span><span class="dot"></span><span>Line by line</span></p>
  <h1>Attention, worked out from scratch</h1>
  <p class="standfirst">The complete transformer notebook, explained &mdash;
     <strong>every line of code, every formula derived</strong>, every output and figure exactly as
     it ran, and full worked solutions to all twelve exercises. Written for someone who is new to
     Python and wants the mathematics spelled out rather than asserted.</p>
  <dl class="meta">
    <div><dt>Based on</dt><dd>Tutorial_2_Transformer_Architecture_Hands_On.ipynb</dd></div>
    <div><dt>Code</dt><dd>NumPy only &mdash; no framework, no GPU</dd></div>
    <div><dt>Outputs</dt><dd>Executed, not transcribed</dd></div>
    <div><dt>Covers</dt><dd>6 core cells + 12 exercises</dd></div>
  </dl>
</header>
%s
<footer>
  <p>Every code block on this page comes from a notebook executed end to end in one NumPy 2.4
  kernel, and every output and figure is the real result of that run. The mathematics is rendered
  as inline SVG rather than by a script, so it stays sharp at any zoom and readable in both light
  and dark. To save a copy, use your browser's Print command &mdash; the print stylesheet drops the
  sidebar and keeps equations, code and figures from splitting across pages.</p>
</footer>
</main>
</div>
"""

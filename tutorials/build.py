import nbformat, html
from hl import code_block, out_block, esc
from shell import CSS

NB = nbformat.read('Tutorial_1_Agents_Hands_On_solved.ipynb', as_version=4)


def src(i):
    return ''.join(NB.cells[i].source).rstrip('\n')


def out(i):
    return ''.join(o.get('text', '') for o in NB.cells[i].get('outputs', [])
                   if o.output_type == 'stream')


def code(i, cap=None):
    head = '<p class="codecap">%s</p>' % cap if cap else ''
    return head + code_block(src(i))


def ann(rows):
    body = "".join(
        '<div class="ann-row"><div class="lref">%s</div><div class="atxt">%s</div></div>'
        % (r[0], r[1]) for r in rows)
    return '<div class="ann">%s</div>' % body


def outp(i, label="Output"):
    return out_block(out(i), label)


def note(tag, body):
    return '<div class="note"><span class="tag">%s</span>%s</div>' % (tag, body)


def warn(tag, body):
    return '<div class="warn"><span class="tag">%s</span>%s</div>' % (tag, body)


def table(headers, rows, aligns=None):
    aligns = aligns or [''] * len(headers)
    th = "".join('<th>%s</th>' % h for h in headers)
    trs = []
    for r in rows:
        tds = "".join('<td%s>%s</td>' % (' class="num"' if aligns[i] == 'n' else '', c)
                      for i, c in enumerate(r))
        trs.append('<tr>%s</tr>' % tds)
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (th, "".join(trs)))


def world(a_dirty, b_dirty, here):
    def sq(name, dirty):
        cls = "sq " + ("dirty" if dirty else "clean") + (" here" if here == name else "")
        return '<span class="%s">%s</span>' % (cls, name)
    return ('<span class="world">%s%s<span style="color:var(--muted);font-size:11px">'
            '&nbsp;agent at %s</span></span>' % (sq("A", a_dirty), sq("B", b_dirty), here))


def page(sections):
    rail = "".join(
        '<li><a href="#%s"><span class="rn">%s</span><span>%s</span></a></li>'
        % (s['id'], s['num'], s['rail']) for s in sections)
    body = "".join(
        '<section id="%s"><h2><span class="snum">%s</span><span>%s</span></h2>%s</section>'
        % (s['id'], s['num'], s['title'], s['body']) for s in sections)
    return TEMPLATE % (CSS, rail, body)


TEMPLATE = """<title>Vacuum World, Line by Line</title>
%s
<div class="layout">
<nav class="rail" aria-label="Contents">
  <p class="rail-title">Contents</p>
  <ol>%s</ol>
</nav>
<main>
<header class="masthead">
  <p class="eyebrow"><span>Tutorial 1</span><span class="dot"></span><span>Agents, hands on</span>
     <span class="dot"></span><span>Line by line</span></p>
  <h1>Five agent architectures, one filthy room</h1>
  <p class="standfirst">A complete walkthrough of the vacuum-world notebook &mdash;
     <strong>every line of code explained</strong>, every output shown as it actually ran, and
     full worked solutions to all four exercises. Read it top to bottom and you will know not just
     what each agent does, but why the architectures stop being interchangeable the moment the
     world gets harder.</p>
  <dl class="meta">
    <div><dt>Based on</dt><dd>Tutorial_1_Agents_Hands_On.ipynb</dd></div>
    <div><dt>Code</dt><dd>Python 3.11, no dependencies</dd></div>
    <div><dt>Outputs</dt><dd>Executed, not transcribed</dd></div>
    <div><dt>Covers</dt><dd>9 cells + 4 solutions</dd></div>
  </dl>
</header>
%s
<footer>
  <p>Every code block on this page was executed in order in a single Python 3.11 kernel, and every
  output block is the real stdout from that run &mdash; nothing here is transcribed by hand. To
  save this as a PDF, use your browser's Print command; the page has a print stylesheet that drops
  the sidebar and keeps code blocks from splitting across pages.</p>
</footer>
</main>
</div>
"""

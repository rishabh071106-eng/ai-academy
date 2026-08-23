import re, html

KW = ("def|return|if|elif|else|for|in|while|class|import|from|not|and|or|None|True|False|"
      "lambda|nonlocal|global|raise|with|as|pass|yield|try|except|finally|is|assert|break|continue")

TOKEN = re.compile(
    r"(?P<comment>\#[^\n]*)"
    r"|(?P<string>'[^'\n]*'|\"[^\"\n]*\")"
    r"|(?P<kw>\b(?:" + KW + r")\b)"
    r"|(?P<builtin>\b(?:print|len|max|min|sum|all|any|range|str|int|float|dict|list|set|"
    r"tuple|enumerate|super|isinstance|sorted|abs|round|chr|ord|property|staticmethod)\b)"
    r"|(?P<selfk>\bself\b)"
    r"|(?P<num>\b\d+\.?\d*\b)"
    r"|(?P<fn>\b[A-Za-z_][A-Za-z_0-9]*(?=\())"
)

CLS = {"comment": "c", "string": "s", "kw": "k", "builtin": "b",
       "selfk": "se", "num": "n", "fn": "f"}


def esc(t):
    return html.escape(t, quote=False)


def _hl_fragment(text):
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        out.append(esc(text[pos:m.start()]))
        kind = m.lastgroup
        out.append('<span class="%s">%s</span>' % (CLS[kind], esc(m.group())))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def highlight_lines(source):
    """Yield one HTML string per source line, handling multi-line triple-quoted strings."""
    lines = source.rstrip("\n").split("\n")
    open_delim = None
    for line in lines:
        if open_delim:
            idx = line.find(open_delim)
            if idx == -1:
                yield '<span class="s">%s</span>' % esc(line)
                continue
            head = '<span class="s">%s</span>' % esc(line[:idx + 3])
            rest = line[idx + 3:]
            open_delim = None
            yield head + _render(rest)[0]
            continue
        rendered, open_delim = _render(line)
        yield rendered


def _render(line):
    """Return (html, open_delim_or_None) for a line with no inherited open string."""
    m = re.search(r"('''|\"\"\")", line)
    if not m:
        return _hl_fragment(line), None
    delim = m.group(1)
    close = line.find(delim, m.end())
    if close == -1:
        return _hl_fragment(line[:m.start()]) + '<span class="s">%s</span>' % esc(line[m.start():]), delim
    head = _hl_fragment(line[:m.start()])
    body = '<span class="s">%s</span>' % esc(line[m.start():close + 3])
    tail, still = _render(line[close + 3:])
    return head + body + tail, still


def code_block(source, start=1):
    rows = []
    for i, h in enumerate(highlight_lines(source), start):
        rows.append('<span class="ln" aria-hidden="true">%d</span><span class="lc">%s</span>' % (i, h or " "))
    return ('<div class="codewrap"><pre class="code"><code>%s</code></pre></div>'
            % "\n".join(rows))


def out_block(text, label="Output"):
    if not text.strip():
        return ""
    return ('<div class="outwrap"><div class="outlabel">%s</div>'
            '<pre class="out">%s</pre></div>' % (label, esc(text.rstrip())))

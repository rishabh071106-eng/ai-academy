from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E)


def sections():
    S = []

    # ---------------------------------------------------------------- idea
    S.append(dict(id="idea", num="00", rail="The one idea", title="Attention is a soft dictionary lookup", body="""
<p class="lede">Before any code: if you hold one mental image for this whole notebook, hold this one.</p>

<p>An ordinary Python dictionary does a <strong>hard</strong> lookup. You supply a key, it matches
exactly one stored key, and you get back exactly one value:</p>

<ul class="plain">
<li><code>d["animal"]</code> &rarr; matches the key <code>"animal"</code> &rarr; returns its value.</li>
<li>Miss by one character and you get nothing at all.</li>
</ul>

<p>Attention does the same thing <strong>softly</strong>. Every token puts out a
<strong>query</strong> (&ldquo;what am I looking for?&rdquo;), every token advertises a
<strong>key</strong> (&ldquo;here is what I am&rdquo;), and every token offers a
<strong>value</strong> (&ldquo;here is what I would contribute&rdquo;). Instead of one key winning,
<em>every</em> key gets a matching score, those scores are squashed into weights that sum to 1, and
the answer is a weighted blend of all the values.</p>

""" + concept("The whole formula", """
<p>That is all the famous equation says. Read it right to left as &ldquo;compare, normalise, blend&rdquo;:</p>
""" + E(r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{T}}{\sqrt{d_k}}\right)V", label="core") + """
<p style="margin-bottom:0"><strong>%s</strong> compares every query with every key.
<strong>%s</strong> stops those comparisons from growing with model width.
<strong>softmax</strong> turns them into weights that sum to 1. Multiplying by <strong>%s</strong>
blends the values using those weights.</p>""" % (M(r"QK^{T}"), M(r"1/\sqrt{d_k}"), M(r"V"))) + """

<h3>Why &ldquo;soft&rdquo; is the entire trick</h3>
<p>A hard lookup is not differentiable &mdash; nudge the query slightly and either nothing changes or
the answer jumps to a different entry. There is no gradient to learn from. A soft lookup changes
smoothly: nudge the query and the weights shift a little, so calculus works, so the model can be
trained. Every design decision in this notebook follows from wanting a lookup you can
differentiate.</p>

<h3>What you will build</h3>
""" + table(["Piece", "What it does", "Section"],
            [["Scaled dot-product attention", "The core lookup, in five lines of NumPy", "02&ndash;03"],
             ["A worked linguistic example", "Watch &ldquo;it&rdquo; find its antecedent", "06&ndash;07"],
             ["Multi-head attention", "Several lookups in parallel, then concatenate", "09"],
             ["Positional encoding", "Give the model a sense of word order", "11"],
             ["A full encoder block", "Attention &rarr; add &amp; norm &rarr; FFN &rarr; add &amp; norm", "13"],
             ["Twelve exercises", "Including causal masking and stacking blocks", "04&ndash;18"]],
            ['', '', '']) + """
<p>No deep-learning framework, no GPU, no API key &mdash; only NumPy and matplotlib. Everything here
is arithmetic you could in principle do on paper.</p>
"""))

    # ---------------------------------------------------------------- numpy
    S.append(dict(id="numpy", num="01", rail="The NumPy you need", title="The NumPy you need, in one section", body="""
<p class="lede">If you are new to Python, read this once. Every construct the notebook uses appears
here with a small example, and each line annotation later carries its own orange
<strong>Python</strong> box, so you can come back only when you want more.</p>

<h3>An array is a grid of numbers with a shape</h3>
""" + code_snip('''import numpy as np

X = np.array([[1.0, 2.0, 3.0],
              [4.0, 5.0, 6.0]])
X.shape        # -> (2, 3)   2 rows, 3 columns
X.shape[-1]    # -> 3        the LAST axis; "-1" means "last"
X[0]           # -> [1., 2., 3.]     row 0
X[:, 0]        # -> [1., 4.]         column 0 (":" means "all of this axis")''') + """
<p><strong>Shapes are the thing to track.</strong> Almost every bug in code like this is a shape
mismatch, and almost every line below can be understood by asking &ldquo;what shape goes in, what
shape comes out?&rdquo;</p>

<h3>The three operations that do all the work</h3>
""" + table(["Written as", "Called", "What it does"],
            [["<code>A @ B</code>", "Matrix multiply", "Row <em>i</em> of the result is a combination of B's rows, weighted by row <em>i</em> of A. <code>(n,k) @ (k,m)</code> &rarr; <code>(n,m)</code> &mdash; the inner numbers must match and they vanish."],
             ["<code>A.T</code>", "Transpose", "Flip rows and columns. <code>(4,8)</code> becomes <code>(8,4)</code>. Used to make the inner dimensions line up."],
             ["<code>A * B</code>", "Elementwise", "Multiply matching positions. Completely different from <code>@</code> &mdash; do not mix them up."]],
            ['', '', '']) + """
<p>Why <code>Q @ K.T</code> is the shape it is: <code>Q</code> is
<code>(seq_len, d_k)</code> and <code>K.T</code> is <code>(d_k, seq_len)</code>, so the result is
<code>(seq_len, seq_len)</code> &mdash; one score for every ordered pair of tokens. The
<code>d_k</code> disappears because it is summed over. That summing <em>is</em> the dot product.</p>

<h3>The <code>axis</code> argument</h3>
<p>Reduction functions collapse one axis. <code>axis=-1</code> means the last one, which for a 2-D
array means <em>along each row</em>.</p>
""" + code_snip('''A = np.array([[1., 2., 3.],
              [4., 5., 6.]])
A.sum()               # -> 21.0        everything
A.sum(axis=-1)        # -> [6., 15.]   one number per ROW    shape (2,)
A.sum(axis=0)         # -> [5., 7., 9.] one number per COLUMN shape (3,)
A.sum(axis=-1, keepdims=True)   # -> [[6.], [15.]]  shape (2,1), NOT (2,)''') + """
""" + warn("keepdims is not optional decoration", """
<p><code>keepdims=True</code> keeps the collapsed axis as a length-1 axis. That is what lets the next
line divide a <code>(2,3)</code> array by a <code>(2,1)</code> array and have NumPy stretch it across
the row. Without it you get a <code>(2,)</code> array, which NumPy stretches down the
<em>columns</em> instead &mdash; no error, just silently the wrong answer. This is why both
<code>softmax</code> and <code>layer_norm</code> use it.</p>""") + """

<h3>Broadcasting</h3>
<p>When shapes differ, NumPy stretches size-1 axes to match. This is how one column of numbers gets
applied to every column of a matrix:</p>
""" + code_snip('''A = np.array([[1., 2., 3.],
              [4., 5., 6.]])          # (2, 3)
row_max = A.max(axis=-1, keepdims=True)   # (2, 1) -> [[3.], [6.]]
A - row_max                                # (2,3) - (2,1) -> (2,3)
# [[-2., -1., 0.],
#  [-2., -1., 0.]]     each row had ITS OWN max subtracted''') + """
<p>The rule: compare shapes from the right; axes must be equal, or one of them must be 1.</p>

<h3>Adding an axis</h3>
""" + code_snip('''pos = np.arange(4)               # [0, 1, 2, 3]        shape (4,)
pos[:, np.newaxis]               # [[0], [1], [2], [3]]  shape (4, 1)
# now  pos[:, np.newaxis] * freqs   with freqs of shape (8,)
# broadcasts to shape (4, 8): every position times every frequency''') + """
<p>That single line is the whole mechanism behind positional encoding.</p>

<h3>Strided slicing</h3>
""" + code_snip('''v = np.array([10, 11, 12, 13, 14, 15])
v[0::2]    # -> [10, 12, 14]   start at 0, take every 2nd  (EVEN positions)
v[1::2]    # -> [11, 13, 15]   start at 1, take every 2nd  (ODD positions)''') + """
<p>Used to write sines into the even columns and cosines into the odd ones.</p>

<h3>Everything else you will meet</h3>
""" + table(["You'll see", "It means"],
            [["<code>np.random.RandomState(seed)</code>", "A private random generator. Same seed &rarr; same numbers &rarr; reproducible results."],
             ["<code>rng.randn(3, 4)</code>", "A <code>(3,4)</code> array of random values, mean 0 and variance 1."],
             ["<code>np.zeros((5, 8))</code>", "A <code>(5,8)</code> array of zeros. Note the <em>double</em> brackets: the shape is one tuple argument."],
             ["<code>np.exp</code>, <code>np.sqrt</code>, <code>np.log</code>", "Applied to every element at once, no loop needed."],
             ["<code>np.maximum(0, x)</code>", "Elementwise max against 0 &mdash; that is ReLU. Different from <code>np.max</code>, which reduces."],
             ["<code>np.allclose(a, b)</code>", "Are these equal allowing for floating-point dust? Use this, never <code>==</code>, on decimals."],
             ["<code>np.argsort(v)</code>", "The <em>indices</em> that would sort <code>v</code>, smallest first. <code>[::-1]</code> reverses it to largest first."],
             ["<code>assert cond, &quot;msg&quot;</code>", "Raise an error if the condition is false. A loud, early shape check."],
             ["<code>x.mean(axis=-1)</code>", "Method form of <code>np.mean(x, axis=-1)</code>. Both are common."],
             ["<code>a, b = x, y</code>", "Assign two names at once."],
             ["<code>def f(x, n=4):</code>", "<code>n</code> has a default, so callers may leave it out."],
             ["<code>f&quot;{v:.3f}&quot;</code>", "An f-string: drop <code>v</code> into text with 3 decimal places."]],
            ['', '']) + note("You do not need to memorise this", """
<p>Skim it, start reading the code, and come back when a line looks strange. Every annotation from
here on has its own Python box next to the line that needs it.</p>""")))

    return S


def code_snip(src):
    from hl import code_block
    return code_block(src)

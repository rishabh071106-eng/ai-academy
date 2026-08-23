from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E)
from hl import code_block


def sections():
    S = []

    # ---------------------------------------------------------------- math
    S.append(dict(id="math", num="02", rail="The mathematics", title="The mathematics, derived", body="""
<p class="lede">Four questions, answered in order. By the end you will know why every symbol in the
formula is there and what breaks if you remove it.</p>

<h3>1. How do you measure &ldquo;relevance&rdquo;?</h3>
<p>With a dot product. For two vectors %s the dot product is</p>
""" % (M(r"q, k \in \mathbb{R}^{d_k}"),) + E(r"q \cdot k = \sum_{i=1}^{d_k} q_i k_i = \|q\|\,\|k\|\cos\theta") + """
<p>It is large when the vectors point the same way, zero when perpendicular, negative when opposed.
So it is a similarity score &mdash; and crucially it is <em>cheap</em>: one multiply-add per
dimension, and a whole matrix of them is a single matrix multiply.</p>

<p>Stack all queries into %s and all keys into %s, and one operation gives every pairwise score:</p>
""" % (M(r"Q \in \mathbb{R}^{n \times d_k}"), M(r"K \in \mathbb{R}^{n \times d_k}")) + E(
        r"S = QK^{T} \in \mathbb{R}^{n \times n}, \qquad S_{ij} = q_i \cdot k_j") + """
<p>Read %s as: <em>how much does token i care about token j?</em> The matrix is
<strong>not</strong> symmetric in general, because caring is not mutual &mdash; a pronoun looks for
its noun much harder than the noun looks for the pronoun.</p>

<h3>2. Why divide by %s?</h3>
""" % (M(r"S_{ij}"), M(r"\sqrt{d_k}")) + concept("The variance argument", """
<p>Suppose the entries of %s and %s are independent with mean 0 and variance 1. Each term %s then
has mean 0 and variance 1, and the dot product is a sum of %s such independent terms. Variances of
independent variables add:</p>
""" % (M("q"), M("k"), M(r"q_i k_i"), M(r"d_k")) + E(
        r"\mathrm{Var}(q \cdot k) = \sum_{i=1}^{d_k}\mathrm{Var}(q_i k_i) = d_k,"
        r"\qquad \mathrm{sd}(q \cdot k) = \sqrt{d_k}") + """
<p>So the raw scores grow like %s. At %s they typically span &plusmn;32 &mdash; and
<code>softmax</code> of numbers that spread out is essentially a hard <code>argmax</code>. Dividing
by %s pulls the variance back to exactly 1, whatever the width:</p>
""" % (M(r"\sqrt{d_k}"), M(r"d_k = 1024"), M(r"\sqrt{d_k}")) + E(
        r"\mathrm{Var}\!\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = \frac{d_k}{d_k} = 1") + """
<p style="margin-bottom:0">Section 15 measures exactly this and confirms it numerically.</p>""") + """

<h3>3. Why softmax, and what does it actually do?</h3>
""" + E(r"\mathrm{softmax}(z)_i = \frac{e^{z_i}}{\sum_{j} e^{z_j}}") + """
<p>It maps any real vector to positive numbers summing to 1 &mdash; so the output is a genuine
weighted <em>average</em> of the values and cannot blow up. Two properties matter here:</p>
<ul class="plain">
<li><strong>It is shift-invariant.</strong> %s for any constant %s, because %s cancels top and
bottom. This is not a curiosity: it is the licence for the <code>x - np.max(x)</code> line that
prevents overflow.</li>
<li><strong>It exaggerates.</strong> Because it exponentiates first, a score gap of 2 becomes a
weight ratio of %s. Small differences in similarity become large differences in attention.</li>
</ul>
""" % (M(r"\mathrm{softmax}(z + c) = \mathrm{softmax}(z)"), M("c"), M(r"e^{c}"), M(r"e^{2} \approx 7.4")) + """

<h3>4. Why does the gradient care?</h3>
<p>This is the part the scaling exists for. Differentiating the softmax gives</p>
""" + E(r"\frac{\partial p_i}{\partial z_j} = p_i(\delta_{ij} - p_j)", label="Jacobian") + """
<p>where %s is 1 when %s and 0 otherwise. Every entry carries a factor of %s. If the softmax has
saturated &mdash; one weight at 1.0, the rest at 0 &mdash; then %s and <strong>no gradient flows
back to the queries and keys at all</strong>. The layer stops learning, silently.</p>
""" % (M(r"\delta_{ij}"), M("i=j"), M(r"p"), M(r"p(1-p) \to 0")) + """
<p>So %s is not a cosmetic constant. It is what keeps the softmax in the region where it still has a
derivative, no matter how wide the model gets.</p>
""" % (M(r"1/\sqrt{d_k}") ,) + note("Putting it together", """
<p>Compare, scale, normalise, blend:</p>
""" + E(r"A = \mathrm{softmax}\!\left(\frac{QK^{T}}{\sqrt{d_k}}\right)"
        r"\in \mathbb{R}^{n \times n}, \qquad \mathrm{Attention}(Q,K,V) = AV") + """
<p style="margin-bottom:0">Output row %s is %s &mdash; token %s's new representation is a weighted
blend of every token's value vector. The shapes:
%s.</p>""" % (M("i"), M(r"\sum_j A_{ij} v_j"), M("i"),
              M(r"(n,d_k)\cdot(d_k,n) \to (n,n)\cdot(n,d_v) \to (n,d_v)")))))

    # ---------------------------------------------------------------- code
    S.append(dict(id="core", num="03", rail="The core code", title="The core code, line by line", body="""
<p class="lede">The formula above, in eleven lines of NumPy. Nothing is hidden and nothing is
imported beyond NumPy itself.</p>
""" + code(2, "Cell 1 &mdash; softmax and scaled dot-product attention") + ann([
        ("L1", "The only import. NumPy gives arrays and the <code>@</code> operator; everything else here is arithmetic.",
         "<code>import numpy as np</code> loads the library under the short alias <code>np</code>, which is universal convention &mdash; you will see <code>np.</code> in front of every NumPy call."),
        ("L2", "The softmax, written to work on any axis so it can be reused on 1-D vectors and 2-D score matrices alike.",
         "<code>axis=-1</code> is a default value, so <code>softmax(x)</code> and <code>softmax(x, axis=0)</code> both work. <code>-1</code> means the last axis."),
        ("L3", "<strong>The stability line.</strong> Subtract each row's maximum before exponentiating. Mathematically it changes nothing &mdash; softmax is shift-invariant &mdash; but numerically it is the difference between an answer and <code>nan</code>: <code>np.exp(1000)</code> overflows to infinity, and <code>inf/inf</code> is <code>nan</code>. After subtracting, the largest exponent is <code>exp(0) = 1</code>.",
         "<code>np.max(x, axis=axis, keepdims=True)</code> reduces along the axis but keeps it as length 1, so <code>(4,8)</code> becomes <code>(4,1)</code>. Broadcasting then subtracts each row's own max from that row. Drop <code>keepdims</code> and NumPy would broadcast down the columns instead &mdash; wrong, and silent."),
        ("L4", "Exponentiate everything. All values are now in <code>(0, 1]</code>, so no overflow is possible.",
         "<code>np.exp</code> applies elementwise to the whole array at once &mdash; no loop. This is called vectorisation and it is why NumPy is fast."),
        ("L5", "Divide by the row sums so each row sums to exactly 1.",
         "Again <code>keepdims=True</code>, for the same broadcasting reason. <code>(4,8) / (4,1)</code> divides each row by its own total."),
        ("L7", "The attention function. It takes the three matrices and returns both the output and the weights &mdash; returning the weights is what makes the heatmaps later possible.",
         "A function with three required parameters. Returning two values with a comma actually returns one tuple, which the caller unpacks."),
        ("L8", "Read the key/query dimension off the shape rather than passing it in, so the function cannot disagree with its own inputs.",
         "<code>Q.shape</code> is a tuple like <code>(4, 8)</code>; <code>[-1]</code> takes the last entry. Deriving it from the data is safer than a parameter someone could set wrong."),
        ("L9", "<strong>The heart of it.</strong> <code>Q @ K.T</code> computes every query-key dot product in one operation, then the scaling divides by %s.<br>Shapes: <code>(n, d_k) @ (d_k, n)</code> &rarr; <code>(n, n)</code>." % M(r"\sqrt{d_k}"),
         "<code>@</code> is matrix multiplication (not <code>*</code>, which is elementwise). <code>K.T</code> transposes K so the inner dimensions match. Division by a plain number applies to every element."),
        ("L10", "Turn scores into weights. <code>axis=-1</code> normalises <em>each row</em>, so every token's attention over all tokens sums to 1 &mdash; row-wise, not globally.",
         "Passing <code>axis=-1</code> explicitly here even though it is the default: worth the clarity, because getting this axis wrong is the single most common bug in attention code."),
        ("L11", "Blend the values. Row <em>i</em> of the output is the weighted sum of all value rows, using row <em>i</em> of the weights.<br>Shapes: <code>(n, n) @ (n, d_v)</code> &rarr; <code>(n, d_v)</code>.",
         "Another matrix multiply. This is the step where information actually moves between tokens &mdash; everything before it was just deciding how much."),
        ("L12", "Return both. The output feeds the next layer; the weights are for inspection.", None),
        ("L15&ndash;17", "A shape check on random data. <code>4</code> tokens, <code>8</code> dimensions each.",
         "<code>np.random.randn(4, 8)</code> draws from a standard normal distribution. This uses the global generator, so results vary between runs &mdash; fine here, since only shapes are being checked."),
        ("L18&ndash;21", "Run it and verify three things: the output keeps the sequence length, the weights are square, and every row sums to 1.",
         "<code>np.allclose(a, b)</code> compares floating-point numbers with a tolerance. Never use <code>==</code> on decimals &mdash; <code>0.1 + 0.2 == 0.3</code> is <code>False</code> in Python."),
    ]) + outp(2) + note("The two shapes to remember", """
<p><strong>Weights are always <code>(n, n)</code></strong> &mdash; one number per ordered pair of
tokens, independent of the embedding width. <strong>Output is always <code>(n, d_v)</code></strong>
&mdash; the same shape as the input. That second fact is what makes it possible to stack these
blocks, and it comes up again in Section 18.</p>""")))

    return S

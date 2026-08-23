from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E)


def sections():
    S = []

    # ------------------------------------------------- multi-head
    S.append(dict(id="mha", num="09", rail="Multi-head", title="Multi-head attention", body="""
<p class="lede">One attention computation can measure exactly one kind of similarity. Language needs
several at once &mdash; who did what, which noun a pronoun refers to, what the topic is. The fix is
embarrassingly simple: run several attentions in parallel and concatenate.</p>
""" + concept("The formula", """
<p>Each head gets its own learned projections, so each looks at a different subspace:</p>
""" + E(r"\mathrm{head}_h = \mathrm{Attention}(XW_h^{Q},\, XW_h^{K},\, XW_h^{V})") + """
<p>and the heads are concatenated and projected back to the model width:</p>
""" + E(r"\mathrm{MultiHead}(X) = \mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_H)\,W^{O}") + """
<p style="margin-bottom:0">with %s, so that %s and the output is %s &mdash; the same shape it went
in as.</p>""" % (M(r"d_{\mathrm{head}} = d_{\mathrm{model}}/H"),
                 M(r"H \cdot d_{\mathrm{head}} = d_{\mathrm{model}}"),
                 M(r"(n, d_{\mathrm{model}})"))) + code(21, "Cell 4 &mdash; multi-head attention") + ann([
        ("L1&ndash;2", "A private random generator seeded per call, so the &ldquo;learned&rdquo; projections are reproducible.",
         "<code>np.random.RandomState(seed)</code> makes an isolated generator. Using it instead of <code>np.random.randn</code> means this function's randomness cannot be disturbed by anything else in the notebook."),
        ("L3", "The divisibility check, as an assert so it fails loudly and early rather than producing a silently wrong shape.",
         "<code>assert condition, \"message\"</code> raises <code>AssertionError</code> with that message when the condition is false. <code>%</code> is the remainder operator: <code>8 % 4</code> is 0."),
        ("L4", "Split the model width across the heads.",
         "<code>//</code> is integer division: it discards any remainder rather than producing a decimal. The assert on the previous line is what guarantees there is no remainder to discard."),
        ("L6&ndash;7", "Two empty lists to collect per-head results.", None),
        ("L8", "Loop once per head.",
         "<code>for h in range(num_heads)</code> counts 0, 1, 2, ... The loop body is what runs in parallel on real hardware; here it is sequential, which changes the speed but not the result."),
        ("L9&ndash;11", "The three projection matrices for this head, shaped <code>(d_model, d_head)</code> so they map the input down into this head's subspace. In a real transformer these are the <em>learned parameters</em> &mdash; here they are random, which is why the heads below specialise arbitrarily rather than meaningfully.",
         "<code>rng.randn(a, b)</code> gives an <code>(a,b)</code> array with mean 0 and variance 1. Multiplying by <code>0.3</code> shrinks the scale, a crude stand-in for the careful initialisation real models use."),
        ("L12", "Project the input into this head's smaller space. <code>(n, d_model) @ (d_model, d_head)</code> &rarr; <code>(n, d_head)</code>.",
         "Three matrix multiplies assigned to three names on one line."),
        ("L13&ndash;15", "Run the <em>same</em> attention function from Section 3 &mdash; multi-head attention adds no new mathematics, it just calls the existing operation several times on smaller inputs.", None),
        ("L17", "Glue the heads side by side along the feature axis: <code>H</code> blocks of <code>(n, d_head)</code> become <code>(n, H&times;d_head)</code> = <code>(n, d_model)</code>.",
         "<code>np.concatenate(list_of_arrays, axis=-1)</code> joins along the last axis. Use <code>axis=0</code> and you would stack them vertically instead &mdash; a common and confusing bug."),
        ("L18&ndash;19", "The output projection %s. It lets the model <em>mix</em> the heads rather than leaving them as independent blocks; without it each head's output would sit in its own slice of the vector, never interacting." % M(r"W^{O}"),
         "Shape <code>(d_model, d_model)</code> here, so the output width matches the input width."),
        ("L20", "Return the output and every head's weights, so you can compare what different heads looked at.", None),
        ("L22&ndash;26", "Run it with 4 heads on the 8-dimensional example and print the shapes.", None),
        ("L28&ndash;31", "The interesting check: do different heads attend differently? Compare where <code>\"it\"</code> looks in head 0 versus head 1.",
         "A list comprehension inside an f-string: <code>{[tokens_list[i] for i in order]}</code> builds and prints the list of words in one expression."),
    ]) + outp(21) + """
<p>Head 0 sends &ldquo;it&rdquo; to <code>['cross', 'tired', 'animal']</code>; head 1 sends it to
<code>['animal', 'it', 'street']</code>. Genuinely different views of the same sentence.</p>
""" + warn("Do not over-read this", """
<p>These projections are <strong>random and untrained</strong>, so the heads differ for the same
reason any two random projections differ &mdash; not because one has discovered syntax and another
coreference. In a trained model heads do reliably specialise, and that is a real and well-documented
finding; but this cell demonstrates the <em>capacity</em> for different heads to see differently, not
that specialisation has occurred here.</p>""") + concept("Why not just use one big head?", """
<p>Because a single %s attention has one score matrix, and one score matrix can encode only one
similarity structure. Splitting into %s heads gives %s independent score matrices for essentially the
same arithmetic cost &mdash; %s multiplications either way.</p>
""" % (M(r"d_{\mathrm{model}}"), M("H"), M("H"),
       M(r"H \times n^2 \times d_{\mathrm{head}} = n^2 d_{\mathrm{model}}")) + """
<p style="margin-bottom:0">The trade is resolution for breadth: each head measures similarity in a
%s-dimensional space instead of %s. Section 17 shows what happens when you push that too far.</p>"""
        % (M(r"d_{\mathrm{model}}/H"), M(r"d_{\mathrm{model}}")))))

    # ------------------------------------------------- ex heads
    S.append(dict(id="ex-heads", num="10", rail="Ex · head count", title="Exercise — change the number of heads", body="""
<p class="lede"><strong>The task:</strong> change <code>num_heads=4</code> to <code>2</code>. What
happens to <code>d_head</code>? Then try 4 again and observe.</p>
""" + code(25, "Solution") + ann([
        ("L1&ndash;7", "The relationship, stated up front: <code>d_head = d_model // num_heads</code>. <code>d_model</code> is fixed, so more heads does not mean more capacity &mdash; it means the same capacity sliced thinner.", None),
        ("L9&ndash;16", "Rather than editing the number by hand and re-running, sweep all four values and tabulate. Faster, and it makes the invariant visible.",
         "<code>for nh in (1, 2, 4, 8)</code> loops over a tuple of values. Formatting each row with <code>{nh:>10d}</code> right-aligns in 10 columns so the table lines up."),
        ("L18&ndash;29", "The two invariants and the trade-off they imply.", None),
        ("L31&ndash;37", "Do fewer, fatter heads behave differently? Print where <code>\"it\"</code> looks under each configuration.",
         "<code>_, w_nh = ...</code> discards the first return value with <code>_</code>, the conventional name for &ldquo;I must name this but will not use it&rdquo;."),
    ]) + outp(25) + """
<h3>The answer</h3>
""" + table(["<code>num_heads</code>", "<code>d_head</code>", "Concat width", "Output shape"],
            [["1", "8", "8", "<code>(10, 8)</code>"],
             ["<strong>2</strong>", "<strong>4</strong>", "8", "<code>(10, 8)</code>"],
             ["<strong>4</strong>", "<strong>2</strong>", "8", "<code>(10, 8)</code>"],
             ["8", "1", "8", "<code>(10, 8)</code>"]],
            ['n', 'n', 'n', '']) + """
<p><strong>4 heads &rarr; <code>d_head=2</code>; 2 heads &rarr; <code>d_head=4</code>.</strong> The
product is always 8, and the output shape never moves &mdash; which is exactly what lets an encoder
block be stacked.</p>
""" + note("The real trade-off", """
<p>More heads means more independent relationships the layer can look for simultaneously, but each
one measures similarity in a lower-dimensional space. Real models keep <code>d_head</code> around
64&ndash;128 and scale the head count with width: GPT-3 uses 96 heads of 128 dimensions
(<code>d_model = 12288</code>). Here, with <code>d_model=8</code>, every option is far below that
&mdash; which is why Section 17's <code>d_head=1</code> degenerates so visibly.</p>""")))

    # ------------------------------------------------- positional encoding
    S.append(dict(id="pe", num="11", rail="Positional encoding", title="Positional encoding", body="""
<p class="lede">Section 8 proved that attention cannot tell two identical tokens apart. Everything
here exists to fix that.</p>
""" + concept("Why order is invisible to attention", """
<p>Attention computes %s and blends %s. Permute the tokens with a permutation matrix %s and every
term moves with them:</p>
""" % (M(r"q_i \cdot k_j"), M(r"v_j"), M("P")) + E(
        r"\mathrm{Attention}(PQ, PK, PV) = P \cdot \mathrm{Attention}(Q,K,V)") + """
<p style="margin-bottom:0">The output permutes but never <em>changes</em>. &ldquo;Dog bites
man&rdquo; and &ldquo;man bites dog&rdquo; would produce the same set of representations. Since word
order carries meaning, position must be injected into the input itself &mdash; and it is, by plain
addition: %s.</p>""" % (M(r"x = \mathrm{embedding} + PE"),)) + """
<h3>The formula</h3>
""" + E(r"PE(pos, 2i) = \sin\!\left(\frac{pos}{10000^{2i/d}}\right), \qquad "
        r"PE(pos, 2i+1) = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)") + """
<p>Read it as a set of clocks. Dimension pair %s ticks at angular frequency
%s. Pair 0 runs fastest (period %s positions); the last pair runs slowest (period tens of thousands).
Every position gets a unique combination of hand positions &mdash; like reading a row of clocks with
wildly different speeds.</p>
""" % (M("i"), M(r"\omega_i = 10000^{-2i/d}"), M(r"2\pi \approx 6.28")) + code(27, "Cell 5 &mdash; sinusoidal positional encoding") + ann([
        ("L1", "Takes how many positions you need and how wide the vectors must be.", None),
        ("L2", "A column of position indices, shape <code>(seq_len, 1)</code>.",
         "<code>np.arange(seq_len)</code> gives <code>[0,1,2,...]</code> with shape <code>(seq_len,)</code>. <code>[:, np.newaxis]</code> adds a second axis, turning the row into a column &mdash; which is what makes the broadcast on lines 5&ndash;6 produce a 2-D grid."),
        ("L3", "The frequencies, one per dimension pair. Written as %s using the identity %s, which is numerically steadier than raising 10000 to a negative power directly." % (M(r"e^{-2i\ln(10000)/d}"), M(r"a^{b} = e^{b\ln a}")),
         "<code>np.arange(0, d_model, 2)</code> counts <code>0, 2, 4, ...</code> &mdash; the third argument is the step. <code>np.log</code> is the natural logarithm (base <em>e</em>), not base 10."),
        ("L4", "An empty array of the right shape, to be filled in.",
         "<code>np.zeros((seq_len, d_model))</code> &mdash; note the double brackets, because the shape is a single tuple argument."),
        ("L5", "Write sines into the <strong>even</strong> columns. <code>(seq_len,1) * (d_model/2,)</code> broadcasts to <code>(seq_len, d_model/2)</code>: every position times every frequency.",
         "<code>pe[:, 0::2]</code> selects all rows and every second column starting at 0. Assigning to a slice writes into the existing array in place."),
        ("L6", "Cosines into the <strong>odd</strong> columns, using the same frequencies. Each consecutive pair of columns is therefore a (sin, cos) pair sharing one clock &mdash; which is what makes the rotation property below work.", None),
        ("L7", "Return the <code>(seq_len, d_model)</code> table.", None),
        ("L9&ndash;10", "Build a 50-position, 64-dimensional encoding and confirm the shape.", None),
        ("L12&ndash;20", "Plot it as a heatmap, transposed so position runs along the x-axis and dimension down the y-axis.",
         "<code>pe.T</code> transposes. <code>aspect=\"auto\"</code> lets the image stretch to fill the axes instead of forcing square pixels. <code>cmap=\"RdBu\"</code> is a diverging map &mdash; appropriate here because the values are signed, running &minus;1 to +1 with white at zero."),
    ]) + outp(27) + figure(27, "Each <strong>column</strong> is one position's unique signature. Each <strong>row</strong> is one dimension oscillating at its own frequency &mdash; fast at the top, slow at the bottom, which is why the stripes stretch out as you move down.") + note("Why sinusoids rather than just numbering the positions?", """
<ul class="plain" style="margin-top:6px">
<li><strong>Bounded.</strong> Every value stays in %s, so adding it cannot swamp the embedding.
Raw integers would grow without limit.</li>
<li><strong>Unique.</strong> No two positions share a signature within any practical length.</li>
<li><strong>Relative offsets are linear.</strong> %s is a fixed rotation of %s &mdash; the same
rotation regardless of %s. A linear layer can therefore learn &ldquo;attend three tokens
back&rdquo;. Section 12 verifies this numerically.</li>
<li><strong>Extrapolates.</strong> Nothing is learned, so the formula gives a code for position
5000 even if training never saw a sequence that long.</li>
</ul>""" % (M(r"[-1, 1]"), M(r"PE(pos+k)"), M(r"PE(pos)"), M(r"pos")))))

    return S

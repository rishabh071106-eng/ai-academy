from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E, mat, eqline)


def sections():
    S = []

    # ------------------------------------------------- X1 scaling
    S.append(dict(id="x1", num="15", rail="Final Ex 1 · scaling", title="Final Exercise 1 — Scaling matters", body="""
<p class="lede"><strong>The task:</strong> remove the <code>/ np.sqrt(d_k)</code> scaling, rerun with
a much larger <code>d_model</code> (pad the features to 256 with zeros), and compare. Do the weights
become peaky? Why does that hurt learning?</p>
""" + warn("The suggested procedure does not show the effect — and that is worth knowing", """
<p>Zero-padding cannot change <code>Q @ K.T</code>. A zero column contributes
%s to every dot product, so the score matrix at %s is <strong>identical</strong> to the one at
%s. The only thing that changes is the divisor.</p>
<p style="margin-bottom:0">So padding makes the <em>scaled</em> version flatter (dividing by 16
instead of 2.83), and removing the scaling just hands back the original 8-dimensional scores. The
effect the exercise is pointing at is real, but demonstrating it needs vectors that carry signal in
every dimension &mdash; which is what a trained model has. Part A below does it as written; Part B
does it properly.</p>""" % (M(r"0 \times 0 = 0"), M(r"d_k=256"), M(r"d_k=8"))) + code(45, "Solution") + ann([
        ("L6&ndash;10", "Attention with the scaling removed &mdash; otherwise character-for-character the original.", None),
        ("L13&ndash;15", "Build the padded input: same 8 features, then 248 zero columns.",
         "<code>np.zeros((10, 256))</code> makes the array, then <code>X_pad[:, :8] = X</code> writes the real features into the first eight columns. <code>:8</code> means &ldquo;up to but not including index 8&rdquo;."),
        ("L17&ndash;19", "Three attention runs to compare: scaled at 8 dimensions, scaled at 256, unscaled at 256.", None),
        ("L21&ndash;26", "The numbers, and the check that proves the point: unscaled-256 is exactly equal to what plain unscaled 8-dimensional scores would give.",
         "<code>np.allclose(w_unscaled_256, softmax(X @ X.T, axis=-1))</code> compares the full matrices, not just one entry."),
        ("L27&ndash;38", "The explanation of why Part A behaves as it does.", None),
        ("L41&ndash;47", "Part B's setup. The variance argument from Section 2, restated as a comment so the table has context.", None),
        ("L48&ndash;61", "A reusable reporting function so scaled and unscaled runs are measured identically &mdash; same seed, same data, one flag different.",
         "Defining a function to run both cases removes the risk of accidentally comparing different random draws. <code>np.random.RandomState(0)</code> is re-created inside, so both calls see the identical sequence."),
        ("L52&ndash;59", "Four metrics per width: the spread of the scores, the largest single weight, the entropy of the distribution, and the mean of %s as a proxy for gradient health." % (M(r"p(1-p)"),),
         "Entropy is <code>-(w * np.log(w + 1e-12)).sum(axis=-1).mean()</code>. The <code>1e-12</code> prevents <code>log(0)</code>, which would be <code>-inf</code>."),
        ("L63&ndash;67", "Run both tables.", None),
        ("L69&ndash;81", "The conclusion, tied to the specific numbers above it.", None),
    ]) + outp(45) + """
<h3>What the tables show</h3>
""" + table(["<code>d_k</code>", "Score spread", "Max weight", "Entropy", "Gradient scale"],
            [["8", "2.62", "0.845", "0.799", "6.6e&minus;02"],
             ["64", "8.72", "0.984", "0.457", "4.3e&minus;02"],
             ["256", "15.81", "1.0000", "0.030", "1.9e&minus;03"],
             ["1024", "<strong>29.00</strong>", "<strong>1.0000</strong>", "<strong>0.024</strong>", "<strong>1.5e&minus;03</strong>"]],
            ['n', 'n', 'n', 'n', 'n']) + """
<p style="margin-top:-6px"><em>Without</em> scaling. The spread grows exactly as %s predicts
(&radic;8&nbsp;&asymp;&nbsp;2.8 up to &radic;1024&nbsp;=&nbsp;32), the top weight saturates at 1.0,
entropy collapses to near zero, and the gradient scale falls by a factor of ~44.</p>
<p><em>With</em> scaling, every column is flat regardless of width: spread ~1, entropy ~1.5, gradient
scale ~0.12. That is the whole job of the divisor.</p>
""" % (M(r"\sqrt{d_k}"),) + concept("Why peaky attention kills learning", """
<p>The softmax Jacobian is</p>
""" + E(r"\frac{\partial p_i}{\partial z_j} = p_i(\delta_{ij} - p_j)") + """
<p>Every entry carries a factor of %s. When one weight saturates at 1 and the rest at 0, that factor
goes to zero, and the chain rule multiplies the upstream gradient by ~0. Concretely, the gradient
reaching the queries is</p>
""" % (M("p"),) + E(r"\frac{\partial L}{\partial q_i} = \frac{1}{\sqrt{d_k}}"
                    r"\sum_j \frac{\partial L}{\partial p_{ij}} \, p_{ij}"
                    r"\left(k_j - \sum_l p_{il} k_l\right)") + """
<p style="margin-bottom:0">If %s is one-hot, the bracket becomes %s and the whole sum vanishes. The
attention pattern freezes at whatever the random initialisation happened to pick, and no amount of
training moves it. Dividing by %s keeps %s in the soft region where the derivative is largest &mdash;
%s is maximised at %s.</p>""" % (M(r"p_{ij}"), M(r"k_j - k_j = 0"), M(r"\sqrt{d_k}"),
                                 M("p"), M(r"p(1-p)"), M(r"p = 0.5")))))

    # ------------------------------------------------- X2 causal
    S.append(dict(id="x2", num="16", rail="Final Ex 2 · masking", title="Final Exercise 2 — Masked self-attention", body="""
<p class="lede"><strong>The task:</strong> write <code>causal_mask(seq_len)</code> returning a matrix
of <code>0</code>s and <code>-inf</code>s such that adding it to the scores before the softmax stops
any position attending to the future. Verify position 0 attends only to itself, position 1 to 0&ndash;1,
and so on.</p>
<p>This is the decoder's &ldquo;masked multi-head self-attention&rdquo;, and it is the single change
that separates BERT-style encoders from GPT-style generators.</p>
""" + code(47, "Solution") + ann([
        ("L1&ndash;8", "The idea: add %s to forbidden scores <em>before</em> the softmax. Since %s, those positions get exactly zero weight, and the survivors renormalise among themselves." % (M(r"-\infty"), M(r"e^{-\infty} = 0")), None),
        ("L10&ndash;12", "The mask itself, in one line.",
         "<code>np.full((n,n), -np.inf)</code> makes an n&times;n array of &minus;infinity. <code>np.triu(..., k=1)</code> keeps the upper triangle <em>strictly above</em> the diagonal and zeroes the rest &mdash; <code>k=1</code> is what excludes the diagonal, so a token can still attend to itself."),
        ("L14&ndash;15", "Print it, because a mask is far easier to check by eye than to reason about.", None),
        ("L17&ndash;22", "Attention with one line added. Everything else is unchanged from Section 3 &mdash; masking is genuinely this small a modification.",
         "<code>scores + causal_mask(...)</code> adds elementwise. Adding &minus;inf to a finite number gives &minus;inf; adding 0 leaves it alone."),
        ("L24&ndash;26", "Run it on the ten-token sentence.", None),
        ("L29&ndash;38", "The verification the exercise asks for: row 0 is exactly <code>[1,0,0,...]</code>, no row has weight on the future, and every row still sums to 1.",
         "<code>all(... for i in range(len(X)))</code> checks every row in one expression. <code>w_causal[i, i+1:]</code> slices out everything to the right of the diagonal on row <em>i</em>."),
        ("L40&ndash;48", "<strong>Why masking must happen before the softmax.</strong> Zeroing the weights afterwards leaves each row summing to less than 1 &mdash; 0.117 for row 0 &mdash; so the token's output silently shrinks toward zero. Masking first lets the remaining positions renormalise.",
         "<code>(causal_mask(n) == 0)</code> gives a boolean array, and multiplying by it zeroes the masked entries &mdash; the naive approach, shown here precisely so you can see it fail."),
        ("L50&ndash;60", "Plot the two matrices side by side. The triangular structure is the entire difference between an encoder and a decoder.",
         "<code>plt.subplots(1, 2)</code> returns an array of two axes, unpacked as <code>axes[0]</code> and <code>axes[1]</code>. Looping over a tuple of <code>(axis, data, title)</code> triples avoids writing the plotting code twice."),
    ]) + outp(47) + figure(47, "Left: the encoder sees everything. Right: the same sentence with the causal mask &mdash; strictly lower-triangular, so each token sees only itself and its past.") + """
<h3>The verification</h3>
""" + table(["Row", "Non-zero weights", "Can see"],
            [["0", "1", "position 0 only &mdash; weight exactly 1.000"],
             ["1", "2", "positions 0&ndash;1"],
             ["2", "3", "positions 0&ndash;2"],
             ["9", "10", "positions 0&ndash;9 (the whole sentence)"]],
            ['n', 'n', '']) + note("Why -inf and not a large negative number", """
<p>Because %s is exactly 0, so the masked weight is exactly zero &mdash; no leakage at any
precision. A merely large negative number like &minus;1e9 leaves a residue that is tiny but nonzero,
and at generation time a model that can see 1e&minus;9 of the future is a model that can cheat. NumPy
handles this cleanly: <code>-inf</code> minus the row max is still <code>-inf</code>, and
<code>np.exp(-inf)</code> is <code>0.0</code> with no warning.</p>
<p style="margin-bottom:0">One caveat: if an entire row were masked, every score would be
<code>-inf</code>, and the row's sum would be 0 &mdash; giving <code>nan</code>. The
<code>k=1</code> on line 12 is what prevents this, by always leaving the diagonal
visible.</p>""" % (M(r"e^{-\infty}"),))))

    # ------------------------------------------------- X3 heads
    S.append(dict(id="x3", num="17", rail="Final Ex 3 · d_head=1", title="Final Exercise 3 — More heads, smaller dimension", body="""
<p class="lede"><strong>The task:</strong> rerun with <code>num_heads=8</code> and
<code>d_model=8</code>, so <code>d_head=1</code>. What breaks, and why does
<code>d_model % num_heads == 0</code> matter?</p>
""" + note("The short answer", """
<p><strong>Nothing breaks.</strong> <code>8 % 8 == 0</code>, so the assert passes and the code runs
to completion with the correct output shape. That is the trap in the question. What degrades is each
head's <em>expressiveness</em>, and the thing that actually breaks is a head count that does not
divide the model width.</p>""") + code(49, "Solution") + ann([
        ("L4&ndash;6", "Run it. Output shape <code>(10, 8)</code>, exactly as with 4 heads.", None),
        ("L8&ndash;14", "The real consequence. With <code>d_head=1</code>, <code>Qh</code> and <code>Kh</code> are single columns, so <code>Qh @ Kh.T</code> is an <strong>outer product</strong> &mdash; a rank-1 matrix.", None),
        ("L15&ndash;22", "Measure it directly across three configurations. The rank of a head's score matrix is bounded by its <code>d_head</code>.",
         "<code>np.linalg.matrix_rank(scores)</code> computes the numerical rank. Rebuilding the projections with the same seed reproduces exactly what happens inside <code>multi_head_attention</code>."),
        ("L24&ndash;25", "A second, quieter problem: the scaling divisor is %s, so a one-dimensional head gets no variance control at all." % (M(r"\sqrt{1} = 1"),), None),
        ("L28&ndash;31", "<strong>What actually breaks.</strong> <code>num_heads=3</code> does not divide 8, and the assert fires.",
         "<code>try / except AssertionError as e</code> catches the error so the notebook keeps running, and prints the message rather than stopping with a traceback."),
        ("L33&ndash;44", "Why divisibility is structural rather than stylistic.", None),
    ]) + outp(49) + concept("Why rank 1 is a real limitation", """
<p>With %s, each head's scores factor as an outer product:</p>
""" % (M(r"d_{\mathrm{head}} = 1"),) + E(r"S = q k^{T}, \qquad S_{ij} = q_i k_j") + """
<p>Every entry is a product of a per-query number and a per-key number. So the head can only express
&ldquo;how strongly does token %s emit&rdquo; times &ldquo;how strongly does token %s
receive&rdquo;. It <strong>cannot</strong> represent a genuinely pairwise relationship such as
&ldquo;<em>this</em> pronoun goes with <em>that</em> noun, but not with the other one&rdquo; &mdash;
that would need rank 2 or more.</p>
""" % (M("i"), M("j")) + """
<p style="margin-bottom:0">The measured ranks confirm the bound exactly: <code>d_head=1</code> gives
rank 1, <code>d_head=2</code> gives rank 2, <code>d_head=4</code> gives rank 4. This is why real
models keep <code>d_head</code> at 64&ndash;128 and add heads by <em>widening the model</em>, never
by slicing a fixed width thinner.</p>""") + """
<h3>Why the divisibility assert exists</h3>
<p>Each head yields a <code>(n, d_head)</code> block, and the blocks are concatenated to
<code>(n, num_heads &times; d_head)</code>. For the result to be a drop-in replacement for the input
&mdash; which residual connections and block stacking both require &mdash; that width must land back
on exactly <code>d_model</code>.</p>
""" + eqline([M(r"H \cdot d_{\mathrm{head}} = H \cdot \left\lfloor d_{\mathrm{model}}/H \right\rfloor"),
              "=", M(r"d_{\mathrm{model}}"), "  only when  ",
              M(r"H \mid d_{\mathrm{model}}")]) + """
<p>With <code>d_model=8</code> and <code>num_heads=3</code>, integer division gives
<code>d_head = 2</code>, so the heads concatenate to width 6 rather than 8 &mdash; and
<code>W_o</code> would then produce the wrong output width. The assert converts a silent shape bug
into a loud, immediate error.</p>
"""))

    # ------------------------------------------------- X4 stacking
    S.append(dict(id="x4", num="18", rail="Final Ex 4 · stacking", title="Final Exercise 4 — Stack encoder blocks", body="""
<p class="lede"><strong>The task:</strong> modify <code>encoder_block</code> so it can be called
twice, feeding the first output into the second. Confirm the shapes still match at every step.</p>
""" + warn("The naive version runs, and is wrong", """
<p>Calling <code>encoder_block(encoder_block(X))</code> produces the right shapes and no error. But
look at the first line of the block's body: it <strong>adds positional encoding</strong>. Calling it
twice adds the positional signal twice, so by layer 2 the tokens carry
<code>embedding + 2&times;PE</code>. In a real transformer, position is added exactly once, before
block 1. No exception, no shape mismatch &mdash; just quietly wrong numbers.</p>""") + code(51, "Solution") + ann([
        ("L7&ndash;9", "The naive stack, shown first so the failure is concrete rather than hypothetical. The shapes are perfect.", None),
        ("L15&ndash;23", "The fix: split the block into &ldquo;add position&rdquo; and &ldquo;the block itself&rdquo;. <code>encoder_block_core</code> is the original minus the positional line.",
         "<code>x.shape[-1]</code> reads <code>d_model</code> off the input so the function works at any width."),
        ("L25&ndash;32", "The stack: add positional encoding once, then loop the core block N times. Printing the shape at each step is what the exercise asks you to confirm.",
         "<code>for n in range(N)</code> runs the body N times, reassigning <code>x</code> each pass so each block consumes the previous one's output."),
        ("L34&ndash;37", "Run it at N=2 and confirm input and output shapes match.", None),
        ("L39&ndash;42", "Quantify the bug: the two approaches differ by up to 1.19 per element while agreeing perfectly on shape.",
         "<code>np.abs(a - b).max()</code> gives the largest single-element discrepancy &mdash; a blunt but useful way to ask &ldquo;are these the same array?&rdquo;"),
        ("L44&ndash;51", "Confirm shape preservation holds for N = 1, 2, 4 and 8, and that nothing has drifted to <code>inf</code> or <code>nan</code>.",
         "<code>np.isfinite(x).all()</code> is a cheap sanity check for numerical blow-up &mdash; worth doing whenever you iterate a transformation many times."),
        ("L53&ndash;62", "Why shape preservation is forced rather than chosen.", None),
        ("L64&ndash;77", "A closing measurement: how similar do token representations become as depth increases?",
         "Dividing each row by its norm makes every vector unit length, so <code>norm @ norm.T</code> is the matrix of cosine similarities. <code>~np.eye(n, dtype=bool)</code> is a boolean mask selecting the off-diagonal entries &mdash; the diagonal is always 1 and would skew the average."),
    ]) + outp(51) + """
<h3>The shapes, at every step</h3>
""" + table(["Stage", "Shape"],
            [["Input embeddings", "<code>(10, 8)</code>"],
             ["After <code>+ PE</code>", "<code>(10, 8)</code>"],
             ["After block 1", "<code>(10, 8)</code>"],
             ["After block 2", "<code>(10, 8)</code>"],
             ["N = 8 blocks", "<code>(10, 8)</code>, all finite"]],
            ['', '']) + concept("Why every sublayer must preserve shape", """
<p>The residual connection computes</p>
""" + E(r"x \leftarrow \mathrm{LayerNorm}\left(x + \mathrm{Sublayer}(x)\right)") + """
<p>and %s is only defined when the two have identical shapes. That single requirement is what forces
multi-head attention to project back to %s via %s, and the feed-forward network to go
%s. Satisfy it once and the block becomes a component you can repeat indefinitely.</p>
""" % (M(r"x + \mathrm{Sublayer}(x)"), M(r"d_{\mathrm{model}}"), M(r"W^{O}"),
       M(r"d_{\mathrm{model}} \to d_{ff} \to d_{\mathrm{model}}")) + """
<p style="margin-bottom:0">GPT-3 is this same brick 96 times over, with %s and %s.</p>"""
        % (M(r"d_{\mathrm{model}} = 12288"), M("H = 96"))) + """
<h3>One honest caveat</h3>
<p>The last measurement shows token representations becoming steadily <em>more alike</em> with depth
&mdash; mean off-diagonal cosine similarity rising 0.58 &rarr; 0.60 &rarr; 0.87 &rarr; 0.91. That is
<strong>over-smoothing</strong>, or attention rank collapse: repeated averaging pulls every token
toward the same vector.</p>
""" + note("Why that happens here and not in GPT-3", """
<p>These projections are random and untrained, so each block is close to a pure averaging operation
&mdash; and averaging repeatedly converges to a constant. Trained transformers resist it using
machinery already present in this block: residual connections preserve a copy of the original signal,
layer norm keeps scales from collapsing, and the feed-forward nonlinearity pushes representations
apart again. Careful initialisation matters too.</p>
<p style="margin-bottom:0">Which is the real lesson of this exercise: residuals and layer norm are
not decoration around the interesting part. Without them, depth actively destroys information.</p>""")))

    # ------------------------------------------------- close
    S.append(dict(id="lands", num="19", rail="Where it lands", title="Where this lands", body="""
<p class="lede">Every piece in this notebook solves one specific problem. You can now name each one
and say what fails without it.</p>
""" + table(["Piece", "The problem it solves", "What breaks without it"],
            [["<code>Q @ K.T</code>", "Measure which tokens are relevant to each other", "No notion of relevance at all"],
             ["<code>/ sqrt(d_k)</code>", "Hold score variance at 1 as the model widens", "Softmax saturates; gradients vanish (&sect;15)"],
             ["<code>softmax</code>", "Turn scores into weights summing to 1", "Outputs unbounded; no probabilistic reading"],
             ["<code>x - max(x)</code>", "Numerical stability", "<code>nan</code> for large scores (&sect;04)"],
             ["Multiple heads", "Several relationship types at once", "One similarity structure only (&sect;17)"],
             ["<code>W_o</code>", "Return concatenated heads to <code>d_model</code>", "Heads never interact; residual breaks"],
             ["Positional encoding", "Give the model word order", "&ldquo;Dog bites man&rdquo; = &ldquo;man bites dog&rdquo; (&sect;08)"],
             ["Residual <code>x + f(x)</code>", "A path for gradients around each sublayer", "Deep stacks do not train"],
             ["Layer norm", "Keep activations at a stable scale", "Rank collapse with depth (&sect;18)"],
             ["Feed-forward", "Per-token nonlinear computation", "Attention only mixes; nothing is computed"],
             ["Causal mask", "Stop a decoder seeing the future", "The model cheats at generation (&sect;16)"]],
            ['', '', '']) + """
<h3>The one-sentence version</h3>
<p>Attention is a soft, differentiable dictionary lookup &mdash; every token writes a query, every
token advertises a key, and the answer is a weighted average of values &mdash; and every other piece
in the block exists to make stacking that operation ninety-six times deep actually trainable.</p>

<h3>Three things the notebook exposed that the text does not say</h3>
<ol class="steps">
<li><strong>The demo skeleton has a bug.</strong> The custom-sentence cell says
<code>Q, K, V = X, X, X</code>, silently reusing the previous sentence. It must be
<code>X_demo</code>. (&sect;07)</li>
<li><strong>Final Exercise 1's suggested method cannot show its own effect.</strong> Zero-padding
leaves <code>Q @ K.T</code> untouched, so scaling gets flatter, not peakier. The variance argument
needs vectors with signal in every dimension. (&sect;15)</li>
<li><strong>Final Exercise 3's premise is wrong in an instructive way.</strong>
<code>num_heads=8</code> with <code>d_model=8</code> does not break &mdash; it runs perfectly and
degrades silently to rank-1 attention. (&sect;17)</li>
</ol>

<h3>Where to go next</h3>
<ol class="steps">
<li><strong>Add the learned projections.</strong> Replace <code>Q = K = V = X</code> with
<code>X @ W_q</code>, <code>X @ W_k</code>, <code>X @ W_v</code>. The mechanism does not change
&mdash; only where the features come from. That is the whole difference between this notebook and a
real attention layer.</li>
<li><strong>Cross-attention.</strong> Let Q come from one sequence and K, V from another. That single
change turns an encoder block into a decoder block, and is how translation worked before
decoder-only models took over.</li>
<li><strong>Backpropagate through it.</strong> Everything here is differentiable. Implementing the
backward pass for <code>softmax</code> yourself is the fastest way to make the %s argument from
&sect;15 stop being a formula and start being obvious.</li>
</ol>
""" % (M(r"p(1-p)"),)))

    return S

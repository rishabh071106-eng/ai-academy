from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E, mat, eqline)


def sections():
    S = []

    # ------------------------------------------------- pe exercises
    S.append(dict(id="ex-pe", num="12", rail="Ex · encoding", title="Exercises — positional encoding shapes and uniqueness", body="""
<p class="lede">Four exercises here: two about shapes, and two about whether positions can collide.
The second pair is where the interesting mathematics lives.</p>

<h3>Shapes: <code>seq_len</code> 50 &rarr; 10, and <code>d_model</code> 64 &rarr; 8</h3>
""" + code(32, "Solution") + ann([
        ("L3&ndash;4", "Fewer positions, same width &rarr; <code>(10, 64)</code>.", None),
        ("L8&ndash;12", "Same positions, narrower model &rarr; <code>(50, 8)</code>; both changed &rarr; <code>(10, 8)</code>.",
         "Passing arguments by name (<code>seq_len=10, d_model=64</code>) rather than by position makes which is which unambiguous &mdash; worth the extra characters."),
        ("L14&ndash;21", "What the two arguments actually control, and the constraint that matters: <code>d_model</code> must match the token embeddings, because the two arrays are <em>added</em>.", None),
        ("L23&ndash;24", "A check worth making: position 3's code does <strong>not</strong> depend on how many positions you asked for. The formula is a pure function of <code>(pos, i, d_model)</code>.", None),
        ("L26&ndash;28", "But it <em>does</em> depend on <code>d_model</code>, because <code>d_model</code> appears in the exponent %s and so sets the frequencies." % (M(r"2i/d"),), None),
    ]) + outp(32) + """
<h3>Are positions 0, 1 and 2 identical?</h3>
<p><strong>The task:</strong> inspect <code>pe[0]</code>, <code>pe[1]</code>, <code>pe[2]</code>. Are
they identical? Why?</p>
""" + code(36, "Solution") + ann([
        ("L5&ndash;11", "Print the first eight entries of each and check for equality. They are not identical.",
         "<code>pe[0][:8]</code> is two lookups: row 0, then its first eight entries. <code>np.allclose</code> rather than <code>==</code>, because these are floats."),
        ("L13&ndash;16", "Position 0 <em>is</em> the odd-looking one: %s and %s, so its code is exactly <code>[0,1,0,1,...]</code> for any <code>d_model</code>. Every other position is a genuine mixture." % (M(r"\sin 0 = 0"), M(r"\cos 0 = 1")),
         "<code>pe[0][0::2]</code> takes the even-indexed entries, <code>[1::2]</code> the odd ones. Two <code>np.allclose</code> checks joined with <code>and</code>."),
        ("L18&ndash;25", "Recover the frequencies from <code>d_model</code> and report the fastest and slowest periods.",
         "<code>10000 ** (i / d_model)</code> raises elementwise across the whole array. Period is %s." % M(r"2\pi/\omega")),
        ("L26&ndash;31", "The uniqueness argument: a collision requires <em>every</em> sine/cosine pair to agree simultaneously, and the slowest pair has a period of ~47,000 positions.", None),
        ("L33&ndash;48", "<strong>The rotation property</strong>, verified numerically. For one dimension pair, shifting position by <em>k</em> is exactly multiplication by a fixed 2&times;2 rotation matrix &mdash; and the same matrix works from every starting position.",
         "<code>rot(theta)</code> builds the rotation matrix. The <code>all(... for p in range(0, 40))</code> is a generator inside <code>all()</code>: true only if the check passes at every starting position."),
        ("L50&ndash;61", "Plot cosine similarity between position 0 and every other position, to show the codes fade smoothly with distance rather than jumping around.",
         "<code>np.linalg.norm(pe, axis=1)</code> gives each row's length; dividing the dot products by the product of lengths turns them into cosines."),
    ]) + outp(36) + concept("The rotation identity — why this encoding was chosen", """
<p>For the dimension pair with frequency %s, the code is the point %s on a circle. Shifting the
position by %s rotates that point by a fixed angle %s:</p>
""" % (M(r"\omega"), M(r"(\sin \omega p,\; \cos \omega p)"), M("k"), M(r"\omega k")) + eqline([
        mat([[M(r"\sin \omega(p+k)")], [M(r"\cos \omega(p+k)")]]),
        "=",
        mat([[M(r"\cos \omega k"), M(r"\sin \omega k")],
             [M(r"-\sin \omega k"), M(r"\cos \omega k")]]),
        mat([[M(r"\sin \omega p")], [M(r"\cos \omega p")]]),
    ], label="rotation") + """
<p>This is just the angle-addition formulas %s and %s written as a matrix.</p>
""" % (M(r"\sin(a{+}b) = \sin a\cos b + \cos a \sin b"), M(r"\cos(a{+}b) = \cos a\cos b - \sin a \sin b")) + """
<p style="margin-bottom:0">The consequence is the point: <strong>%s depends only on %s, not on
%s</strong>. So a single linear transformation can express &ldquo;look %s positions back&rdquo;
everywhere in the sequence at once. The code verifies exactly this &mdash; the same rotation works
from all 40 tested starting positions. That is why sinusoids, rather than any other unique
fingerprint.</p>""" % (M(r"R(\omega k)"), M("k"), M("p"), M("k"))) + figure(36, "Cosine similarity between position 0 and each later position. Nearby positions have similar codes and distant ones do not &mdash; a smooth, learnable notion of &ldquo;near&rdquo;.") + note("Answer, in one line", """
<p>No, they are not identical, and no two positions ever are within a practical sequence length.
Position 0 is exactly <code>[0,1,0,1,...]</code>; every other position is a unique mixture of
frequencies; and consecutive positions are related by a fixed rotation, which is what makes
<em>relative</em> position learnable.</p>""")))

    # ------------------------------------------------- encoder block
    S.append(dict(id="block", num="13", rail="Encoder block", title="The complete encoder block", body="""
<p class="lede">Everything assembled: <strong>input + positional encoding &rarr; multi-head
self-attention &rarr; add &amp; norm &rarr; feed-forward &rarr; add &amp; norm</strong>. This is the
brick that GPT-3 stacks ninety-six times.</p>
""" + concept("The three pieces you have not seen yet", """
<p><strong>Residual connection.</strong> Instead of %s, compute:</p>
""" % (M(r"x \leftarrow f(x)"),) + E(r"x \leftarrow x + f(x)") + """
<p>The gradient of %s with respect to %s is %s &mdash; that %s is a path the gradient can always
take, even if %s contributes nothing. Without it, deep stacks do not train.</p>
""" % (M(r"x + f(x)"), M("x"), M(r"I + f'(x)"), M("I"), M(r"f'")) + """
<p><strong>Layer normalisation.</strong> Standardise each token's vector across its features:</p>
""" + E(r"\mathrm{LayerNorm}(x) = \frac{x - \mu}{\sigma + \epsilon}, \qquad "
        r"\mu = \frac{1}{d}\sum_{j=1}^{d} x_j, \quad "
        r"\sigma = \sqrt{\frac{1}{d}\sum_{j=1}^{d}(x_j - \mu)^2}") + """
<p>Note this is per <em>token</em>, across features &mdash; not across the batch. That is why it
works with any sequence length and does not care what else is in the batch.</p>
<p><strong>Feed-forward network.</strong> Attention only <em>mixes</em> vectors that already exist;
it cannot compute a new nonlinear function of a token. The FFN does that, applied to each position
independently:</p>
""" + E(r"\mathrm{FFN}(x) = \max(0,\, xW_1 + b_1)\,W_2 + b_2") + """
<p style="margin-bottom:0">Widening to %s and back is where most of a transformer's parameters
actually live &mdash; typically %s.</p>""" % (M(r"d_{ff}"), M(r"d_{ff} = 4 d_{\mathrm{model}}"))) + code(38, "Cell 6 &mdash; the full encoder block") + ann([
        ("L1&ndash;4", "Layer norm. Subtract the row mean, divide by the row standard deviation.",
         "Both reductions use <code>axis=-1, keepdims=True</code> so each token is normalised against its own statistics and broadcasting lines up. <code>eps=1e-6</code> is scientific notation for 0.000001."),
        ("L4", "The <code>+ eps</code> prevents division by zero when a token's features are all equal (%s). Note this implementation has no learnable %s and %s &mdash; a real <code>LayerNorm</code> adds them so the network can undo the normalisation where it needs to." % (M(r"\sigma = 0"), M(r"\gamma"), M(r"\beta")), None),
        ("L6&ndash;7", "The feed-forward network. <code>d_ff=16</code> is twice <code>d_model=8</code> here; real models use 4&times;.", None),
        ("L8&ndash;9", "Two weight matrices: <code>(d_model, d_ff)</code> up, then <code>(d_ff, d_model)</code> back down. No biases in this simplified version.",
         "<code>x.shape[-1]</code> reads the width off the input, so the function adapts to whatever it is given."),
        ("L10", "Expand, then ReLU. This nonlinearity is the entire reason the FFN exists &mdash; without it, two stacked linear layers would collapse into one.",
         "<code>np.maximum(0, z)</code> takes the elementwise maximum against zero, so negatives become 0 and positives pass through. Do not confuse it with <code>np.max</code>, which reduces an array to a single value."),
        ("L11", "Project back down to <code>d_model</code>, so the residual addition is well defined.", None),
        ("L13&ndash;14", "The block itself. Read the shape off the input rather than taking it as an argument.",
         "<code>seq_len, d_model = token_embeddings.shape</code> unpacks the two-element shape tuple into two names."),
        ("L16&ndash;18", "<strong>Step 1</strong> &mdash; add positional encoding, so the tokens stop being an unordered set.",
         "Two arrays of identical shape added elementwise. This is the only place order enters the model."),
        ("L20&ndash;22", "<strong>Step 2</strong> &mdash; self-attention, then <em>add the input back</em> and normalise. The <code>x + attn_out</code> is the residual; the <code>layer_norm(...)</code> around it keeps the scale stable.",
         "<code>attn_out, _ = ...</code> keeps the output and discards the weights. This block uses the post-norm arrangement of the original paper; most modern models use pre-norm, which trains more stably at depth."),
        ("L24&ndash;26", "<strong>Step 3</strong> &mdash; feed-forward, residual, norm again. Same pattern as step 2.",
         "<code>seed + 1</code> gives the FFN different random weights from the attention projections &mdash; otherwise they would be identical, which would be a strange coincidence to build in."),
        ("L28", "Return the transformed embeddings, same shape as the input.", None),
        ("L30&ndash;34", "Run it and confirm the shape survives.", None),
    ]) + outp(38) + note("The invariant that makes depth possible", """
<p><strong>Input <code>(10, 8)</code>, output <code>(10, 8)</code>.</strong> Every sublayer must
preserve shape, because the residual computes %s and that is only defined when %s matches %s. This is
what forces attention to project back to %s and the FFN to return from %s. Get it right once, and the
block becomes a component you can stack any number of times.</p>"""
        % (M(r"x + f(x)"), M(r"f(x)"), M("x"), M(r"d_{\mathrm{model}}"), M(r"d_{ff}")))))

    # ------------------------------------------------- ex layernorm
    S.append(dict(id="ex-ln", num="14", rail="Ex · layer norm", title="Exercise — layer norm, mean and standard deviation", body="""
<p class="lede"><strong>The task:</strong> pass an array to <code>layer_norm</code>, then compute the
mean and standard deviation of the result.</p>
""" + code(42, "Solution") + ann([
        ("L3&ndash;9", "Two rows that differ by a factor of 10, normalised, then measured. Mean 0 and standard deviation 1 per row, as designed.", None),
        ("L11&ndash;12", "<strong>The striking part.</strong> The two output rows are <em>identical</em>, despite inputs of <code>[1,2,3,4]</code> and <code>[10,20,30,40]</code>.", None),
        ("L13&ndash;18", "Why: layer norm is invariant to any positive affine rescaling of a row. It keeps the <em>shape</em> of a token's feature pattern and throws away scale and offset entirely.", None),
        ("L20&ndash;21", "The invariance stated as a check: %s for %s." % (M(r"\mathrm{LN}(ax + b) = \mathrm{LN}(x)"), M("a > 0")),
         "Multiplying and adding scalars to an array applies elementwise, so <code>7 * x - 3</code> transforms every entry at once."),
        ("L23&ndash;27", "Two loose ends. The standard deviation comes out as 0.9999991 rather than 1 because of the <code>eps</code> in the denominator; and a constant row survives instead of dividing by zero, which is what <code>eps</code> is for.",
         "<code>1 - y.std(axis=-1)</code> shows the tiny discrepancy directly rather than making you compare long decimals by eye."),
        ("L29&ndash;31", "A caveat: NumPy's <code>std</code> defaults to the population formula (dividing by %s, not %s), and this implementation has no learnable gain or bias." % (M("d"), M("d-1")), None),
    ]) + outp(42) + concept("Why identical outputs are the correct behaviour", """
<p>Substituting %s into the definition, the mean becomes %s and the standard deviation becomes %s
(for %s), so:</p>
""" % (M(r"x' = ax + b"), M(r"a\mu + b"), M(r"a\sigma"), M("a>0")) + E(
        r"\mathrm{LN}(ax+b) = \frac{(ax+b) - (a\mu+b)}{a\sigma} = \frac{a(x-\mu)}{a\sigma} "
        r"= \frac{x-\mu}{\sigma} = \mathrm{LN}(x)") + """
<p style="margin-bottom:0">The %s cancels and the %s subtracts away. In a transformer this is exactly
what you want: after a residual addition, activations can drift to any scale, and layer norm hands
the next sublayer a consistently scaled input every time &mdash; which is what stops deep stacks from
exploding or vanishing.</p>""" % (M("a"), M("b")))))

    return S

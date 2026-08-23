from build2 import (code, ann, outp, raw_out, note, warn, concept, table,
                    figure, M, E)


def sections():
    S = []

    # ------------------------------------------------- ex: softmax
    S.append(dict(id="ex-softmax", num="04", rail="Ex · softmax", title="Exercise — feed an array to softmax", body="""
<p class="lede"><strong>The task:</strong> create a small array, pass it to <code>softmax</code>, and
print the result.</p>
""" + code(5, "Solution") + ann([
        ("L3&ndash;7", "The basic case. Three scores in, three weights out, summing to 1.",
         "<code>np.round(p, 4)</code> rounds for display only &mdash; it does not change <code>p</code>. Handy when raw floats have fifteen digits of noise."),
        ("L11&ndash;13", "Softmax is <em>monotonic but exaggerating</em>. The inputs 2.0 and 1.0 differ by 1, and the output weights differ by a factor of exactly %s. That is not a coincidence &mdash; it is the definition: the ratio of two weights is %s." % (M(r"e \approx 2.718"), M(r"e^{z_i - z_j}")),
         "The <code>\\n</code> at the start of a string prints a blank line first. <code>round(x, 3)</code> is Python's own function, distinct from <code>np.round</code> which works on whole arrays."),
        ("L16&ndash;21", "The 2-D case, which is what attention actually uses. <code>axis=-1</code> normalises each row independently, so each row becomes its own distribution. Note the second row: <strong>equal scores give exactly uniform weights</strong>. That is what an attention row looks like when a token has no reason to prefer anything.",
         "A 2-D array is written as a list of lists. Passing <code>axis=-1</code> collapses along the last axis; the row sums confirm it worked row-wise rather than over the whole array."),
        ("L25&ndash;29", "<strong>Why line 3 of the original function exists.</strong> With inputs near 1000 the naive formula returns <code>nan</code>: <code>np.exp(1000)</code> overflows to <code>inf</code>, and <code>inf/inf</code> is undefined. The library version returns the right answer.",
         "<code>np.errstate(over=\"ignore\")</code> temporarily silences NumPy's overflow warning so the demonstration prints cleanly &mdash; the overflow still happens, it just is not reported."),
        ("L30&ndash;35", "The justification: subtracting a constant leaves softmax unchanged, because the "
         + M(r"e^{-m}") + " factor cancels top and bottom. So we are free to subtract the max, which "
         "forces the largest exponent to be " + M(r"e^{0}=1") + ".", None),
    ]) + outp(5) + concept("The shift-invariance identity", """
<p>The line that looks pointless is doing all the safety work. Formally:</p>
""" + E(r"\frac{e^{z_i - m}}{\sum_j e^{z_j - m}} = \frac{e^{-m}e^{z_i}}{e^{-m}\sum_j e^{z_j}}"
        r" = \frac{e^{z_i}}{\sum_j e^{z_j}}") + """
<p style="margin-bottom:0">Mathematically identical, numerically the difference between an answer
and <code>nan</code>. Choosing %s makes the largest exponent %s, so nothing can overflow.</p>"""
        % (M(r"m = \max_j z_j"), M(r"e^{0} = 1")))))

    # ------------------------------------------------- ex: QKV
    S.append(dict(id="ex-qkv", num="05", rail="Ex · Q, K, V", title="Exercise — build Q, K, V by hand", body="""
<p class="lede"><strong>The task:</strong> make three arrays, pass them to
<code>scaled_dot_product_attention</code>, and observe the result. The vectors below are chosen so
you can predict every row before running it.</p>
""" + code(8, "Solution") + ann([
        ("L6&ndash;16", "Three tokens, four dimensions. Each query is a one-hot vector asking for one feature; each key advertises one feature; each value is the payload that token contributes. Note key 2 deliberately advertises the <em>same</em> feature as key 0.",
         "<code>np.array</code> of a list of lists gives a <code>(3,4)</code> array. Writing the rows on separate lines is purely for readability &mdash; Python ignores line breaks inside brackets."),
        ("L18", "One call, two returns.", "Tuple unpacking: the function returns <code>(output, weights)</code> and this splits them into two names."),
        ("L20&ndash;29", "Print each stage: raw dot products, then scaled, then weights, then output. Seeing the intermediate matrices is the fastest way to build intuition.",
         "<code>Q_ex @ K_ex.T</code> re-does by hand what the function does internally &mdash; useful for checking your mental model against the code."),
        ("L31&ndash;41", "The three readings, and two verifications. Row 2's query matches nothing, so all its scores are 0 and softmax of equal scores is exactly uniform &mdash; its output is the plain mean of V. Row 0 matches two keys and splits between them.",
         "<code>V_ex.mean(axis=0)</code> averages down the <em>columns</em> (across rows), giving the mean value vector. <code>np.allclose</code> confirms the match despite floating-point dust."),
    ]) + outp(8) + """
<h3>Reading the output</h3>
""" + table(["Row", "What its query asks", "Result"],
            [["0", "feature 0", "Keys 0 <em>and</em> 2 both advertise it, so attention splits 0.38 / 0.23 / 0.38 and the output mixes <code>V[0]</code> and <code>V[2]</code>."],
             ["1", "feature 1", "Only key 1 matches, so this is the peakiest row at 0.45."],
             ["2", "feature 2", "Nothing matches. All scores are 0, weights are exactly &#8531; each, and the output is the plain average of all values."]],
            ['', '', '']) + note("The one thing to take away", """
<p>The final line proves it explicitly: the output row is <em>nothing more</em> than
%s &mdash; a weighted sum of the value rows. All the machinery upstream exists only to
decide the weights %s. Attention does not create information; it <strong>routes</strong> it.</p>"""
        % (M(r"\sum_j A_{ij} v_j"), M(r"A_{ij}")))))

    # ------------------------------------------------- worked example
    S.append(dict(id="worked", num="06", rail="&ldquo;it&rdquo; &rarr; &ldquo;animal&rdquo;", title="The worked example: making &ldquo;it&rdquo; find its noun", body="""
<p class="lede">The sentence is <em>&ldquo;The animal didn't cross the street because it was
tired.&rdquo;</em> We want to watch attention link <strong>&ldquo;it&rdquo; &rarr;
&ldquo;animal&rdquo;</strong> rather than &ldquo;it&rdquo; &rarr; &ldquo;street&rdquo;.</p>
""" + warn("Read the honesty note in the notebook", """
<p>With <em>random, untrained</em> weights this link would not reliably appear &mdash; the model has
learned nothing yet. So the notebook hand-crafts small feature vectors instead. This demonstrates
what the <strong>mechanism</strong> does given meaningful input; it is not evidence that an untrained
transformer resolves coreference. A trained model learns embeddings that play the role these
hand-made features play here.</p>""") + code(10, "Cell 2 &mdash; the worked example") + ann([
        ("L1", "The sentence as a list of tokens.",
         "A plain Python list of strings. Real models split text into sub-word pieces, but the mechanism is identical."),
        ("L3&ndash;4", "The comment declares what each of the eight dimensions means. This is the interpretive key for everything below.", None),
        ("L5&ndash;16", "A dict from word to feature vector. The load-bearing line is <code>\"it\"</code>: it is given <code>[1,1,0,...]</code>, the same <code>[entity, animate]</code> pattern as <code>\"animal\"</code>. Two zero &ldquo;pad&rdquo; dimensions bring the width to 8 so it divides evenly by the head count later.",
         "A dict maps keys to values. Here each value is a list of 8 numbers, written to line up visually so the columns are readable."),
        ("L17", "Build the embedding matrix by looking up each token in order. Shape <code>(10, 8)</code>: ten tokens, eight features.",
         "A list comprehension: <code>[feats[t] for t in tokens_list]</code> builds a list of lists, which <code>np.array</code> turns into a 2-D array. <code>dtype=float</code> forces decimals &mdash; without it you would get integers and later divisions would behave differently."),
        ("L19&ndash;22", "<code>Q = K = V = X</code>. In a real model these are <code>X @ W_q</code>, <code>X @ W_k</code>, <code>X @ W_v</code> with learned matrices. Setting them all to X removes that layer of indirection so you can see the mechanism unobscured.",
         "One line assigning three names to the same array. They are three references to one object, not three copies &mdash; fine here because nothing modifies them in place."),
        ("L23", "Run attention over the sentence.", None),
        ("L25&ndash;29", "Find the row for <code>\"it\"</code> and rank what it attends to.",
         "<code>.index(\"it\")</code> finds a value's position in a list. <code>np.argsort</code> returns the indices that would sort the array ascending; <code>[::-1]</code> reverses that to descending; <code>[:4]</code> takes the top four."),
    ]) + outp(10) + """
<h3>Why it works, arithmetically</h3>
<p>Because %s, the score between two tokens is just the dot product of their feature vectors &mdash;
which counts <strong>how many features they share</strong>:</p>
""" % (M("Q = K = X"),) + table(["Pair", "Shared features", "Raw score"],
            [["<code>it</code> &middot; <code>animal</code>", "entity, animate", "<strong>2</strong>"],
             ["<code>it</code> &middot; <code>it</code>", "entity, animate", "<strong>2</strong>"],
             ["<code>it</code> &middot; <code>street</code>", "entity only", "1"],
             ["<code>it</code> &middot; <code>tired</code>", "none", "0"]],
            ['', '', 'n']) + """
<p>Scores of 2, 2, 1, 0 become weights 0.163, 0.163, 0.114, 0.080 &mdash; exactly the ranking in the
output. &ldquo;animal&rdquo; ties with &ldquo;it&rdquo; itself and clearly beats
&ldquo;street&rdquo;.</p>
""" + note("Why the weights look so flat", """
<p>The top weight is only 0.163, not 0.9. Two reasons, both worth understanding: the scores are tiny
integers (0, 1, 2) so %s is at most about 7, and there are ten tokens sharing the probability mass
&mdash; uniform would be 0.100. A trained model produces far larger score gaps and correspondingly
peakier attention. What matters here is the <em>ranking</em>, not the magnitude.</p>"""
        % (M(r"e^{\Delta}"),))))

    # ------------------------------------------------- ex: own sentence
    S.append(dict(id="ex-own", num="07", rail="Ex · your sentence", title="Exercise — your own sentence", body="""
<p class="lede"><strong>The task:</strong> make your own token list, create an encoding for every
token, and compute the attention.</p>
<p>I chose <em>&ldquo;The dog chased the ball because it was rolling&rdquo;</em> &mdash; deliberately
the mirror image of the original. Here &ldquo;it&rdquo; refers to the <strong>inanimate</strong>
thing. If the mechanism is real rather than rigged, attention should now prefer
&ldquo;ball&rdquo; over &ldquo;dog&rdquo;.</p>
""" + code(14, "Solution") + ann([
        ("L1&ndash;9", "The setup, and the hypothesis being tested.", None),
        ("L11&ndash;12", "The new sentence. Nine tokens this time &mdash; nothing depends on the length.", None),
        ("L14&ndash;26", "New feature scheme: dimension 2 is now <code>is_object</code> rather than <code>is_place</code>. <code>\"ball\"</code> and <code>\"it\"</code> both get <code>[entity, object]</code>; <code>\"dog\"</code> gets <code>[entity, animate]</code>. So <code>it&middot;ball = 2</code> but <code>it&middot;dog = 1</code>.",
         "Same dict-of-lists structure as before. The keys must exactly match the strings in the token list, or the lookup on the next line raises <code>KeyError</code>."),
        ("L28&ndash;33", "<strong>A bug in the notebook's skeleton.</strong> The provided cell says <code>Q, K, V = X, X, X</code> &mdash; the <em>old</em> sentence's matrix. It runs without error and produces a <code>(10,10)</code> attention matrix for a 9-token sentence, which then fails or silently misleads. It must be <code>X_demo</code>.",
         "This is the classic copy-paste hazard: a name that still exists from an earlier cell, so Python raises nothing. Notebooks make this especially easy because state persists across cells."),
        ("L35&ndash;44", "Rank what &ldquo;it&rdquo; attends to, then print the ratio and the underlying raw scores so the result is traceable to arithmetic rather than taken on faith.",
         "An f-string with a format spec: <code>{w_ball:.3f}</code> prints three decimal places. The <code>@</code> between two 1-D arrays computes their dot product and returns a single number."),
    ]) + outp(14) + """
<p><strong>&ldquo;ball&rdquo; 0.177 versus &ldquo;dog&rdquo; 0.124</strong> &mdash; a 1.42&times;
preference, from raw scores of 2 versus 1. Same code, opposite antecedent, because the features
changed and nothing else did.</p>
""" + note("What this actually demonstrates", """
<p>That attention is a <em>mechanism</em>, not a knowledge base. It faithfully computes similarity
in whatever feature space you hand it. Get the features right and coreference falls out; get them
wrong and it will confidently attend to the wrong word. In a real transformer, learning good
features <em>is</em> the training problem &mdash; the attention arithmetic never changes.</p>""")))

    # ------------------------------------------------- heatmaps
    S.append(dict(id="heatmap", num="08", rail="Visualising", title="Visualising the attention matrix", body="""
<p class="lede">A 10&times;10 table of decimals is hard to scan. The same numbers as a heatmap are
readable instantly.</p>
""" + code(16, "Cell 3 &mdash; the heatmap") + ann([
        ("L1", "matplotlib's plotting interface.",
         "<code>import matplotlib.pyplot as plt</code> &mdash; <code>plt</code> is the universal alias."),
        ("L3", "Create a figure and one set of axes. <code>fig</code> is the whole canvas, <code>ax</code> is the plot area.",
         "<code>plt.subplots()</code> returns a <code>(figure, axes)</code> tuple, unpacked into two names. <code>figsize</code> is in inches."),
        ("L4", "Draw the matrix as an image: one pixel per cell, colour-mapped by value.",
         "<code>imshow</code> means &ldquo;show image&rdquo;. <code>cmap=\"viridis\"</code> selects a perceptually uniform colour map &mdash; dark blue for low, yellow for high &mdash; which is readable in greyscale and to colour-blind viewers."),
        ("L5&ndash;8", "Put the actual words on both axes instead of index numbers.",
         "<code>set_xticks</code> chooses <em>where</em> the labels go, <code>set_xticklabels</code> chooses <em>what</em> they say &mdash; you need both. <code>rotation=45, ha=\"right\"</code> angles the x labels so they do not collide."),
        ("L9&ndash;11", "Label the axes with the direction of attention. This matters: the matrix is not symmetric, so which axis is the query and which is the key is essential information.", None),
        ("L12", "A colour bar, so the reader can map colour back to number.", None),
        ("L13&ndash;15", "Tidy the spacing, save at higher resolution, display.",
         "<code>tight_layout()</code> stops the rotated labels being clipped. <code>dpi=120</code> makes the saved PNG sharper than the default 100."),
    ]) + figure(16, "The original sentence. Every row sums to 1. The bright block in the middle is the four function words &mdash; <code>The</code>, <code>the</code>, <code>because</code>, <code>was</code> &mdash; which share an identical feature vector and so cannot be told apart.") + """
<h3>The exercise: your own sentence</h3>
<p><strong>The task:</strong> visualise the demo attention matrix.</p>
""" + code(19, "Solution") + ann([
        ("L3&ndash;13", "The same plotting recipe, pointed at <code>attn_weights_demo</code> and the new token list.", None),
        ("L15&ndash;18", "An addition worth making: draw a red rectangle around the <code>\"it\"</code> row so the coreference link is impossible to miss.",
         "<code>plt.Rectangle((x, y), width, height)</code> takes the bottom-left corner first. The <code>-0.5</code> offsets exist because <code>imshow</code> centres each cell on its integer index, so the cell edges fall on the halves."),
        ("L19&ndash;23", "Colour bar, layout, save, show.", None),
        ("L25&ndash;29", "A check that makes the visual claim precise: the rows for <code>\"The\"</code> and <code>\"the\"</code> are <em>identical</em>, confirming attention alone cannot distinguish two occurrences of the same word.", None),
    ]) + figure(19, "The mirror-image sentence, with the <code>it</code> row outlined. Its brightest cells are <code>ball</code> and <code>it</code> &mdash; not <code>dog</code>.") + concept("What the picture proves", """
<p>Identical rows for <code>The</code> and <code>the</code> are not a rendering artefact &mdash;
<code>np.allclose</code> confirms it. Self-attention is <strong>permutation-equivariant</strong>:
shuffle the input tokens and the output rows shuffle identically, but nothing else changes. The
mechanism has no concept of first, second or last.</p>
<p style="margin-bottom:0">That is a fatal flaw for language, and it is precisely the hole that
positional encoding &mdash; Section 11 &mdash; exists to fill.</p>""")))

    return S

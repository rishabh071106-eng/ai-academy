from build import code, ann, outp, note, warn, table


def sections():
    S = []

    # ---------------------------------------------------------------- 10 ex1
    S.append(dict(id="ex1", num="10", rail="Exercise 1", title="Exercise 1 — Dirt that comes back", body="""
<p class="lede"><strong>The task:</strong> make dirt reappear at random after being cleaned, turning
the world <em>stochastic</em> and <em>non-episodic</em>. Which architecture degrades least?</p>

<p><strong>My hypothesis before running it:</strong> the agents that <em>stop</em> once they believe
the job is done (model-based, goal-based) should suffer most, because their belief goes stale. The
simple reflex agent, which never stops, should suffer least.</p>
""" + code(24, "Solution &mdash; stochastic environment and the fix") + ann([
        ("L1&ndash;6", "The hypothesis, written down before the code runs. Worth doing: half of it turns out to be wrong, and that is the interesting part."),
        ("L8&ndash;9", "Subclass rather than edit the original, so every earlier cell still works and the two worlds can be compared directly."),
        ("L11&ndash;12", "<code>super().__init__</code> builds the ordinary starting world, so the only difference is what happens afterwards."),
        ("L13", "How likely a clean square is to become dirty again, each step."),
        ("L14", "A <em>separate</em> random stream, offset by 1000. Without this, respawn draws would consume numbers from the same generator that built the starting world, and changing <code>respawn_prob</code> would silently change the starting layout too &mdash; you could no longer tell which variable caused a difference."),
        ("L15&ndash;16", "Counters for the new metric."),
        ("L18&ndash;19", "Override <code>execute</code>; delegate the action's normal effects to the parent."),
        ("L20&ndash;22", "<strong>The change that matters.</strong> After the agent acts, the environment acts on its own: each clean square may become dirty again. The world is no longer something that only changes when the agent touches it."),
        ("L23&ndash;24", "Accumulate how many squares were clean at each step."),
        ("L25", "Return the fresh percept, matching the parent's contract."),
        ("L27&ndash;30", "<strong>A new performance measure.</strong> <code>is_clean()</code> is meaningless now &mdash; there is no final state, and whether the world happens to be clean on the last step is luck. Instead: what fraction of (square, time step) pairs were clean? Changing the environment forced changing the metric, which is the deeper lesson of this exercise."),
        ("L33&ndash;37", "A runner for the new world, structured like the original but returning the new metric."),
        ("L40", "40 steps and 8 seeds &mdash; long enough for respawns to matter, repeated enough to average out lucky worlds."),
        ("L41&ndash;47", "The same five architectures. Line 45 wraps the utility agent in a <code>lambda</code> to give it a battery of 40 instead of 6 &mdash; otherwise it would simply run flat at step 6 and the comparison would measure battery size, not architecture."),
        ("L49&ndash;50", "Header and rule, same formatting trick as the original comparison."),
        ("L51&ndash;55", "For each agent, run every seed. <code>random.seed(0)</code> inside the loop keeps the learning agent reproducible."),
        ("L56&ndash;58", "Average both metrics and print the row. <code>{clean:16.0%}</code> formats a fraction as a whole-number percentage."),
        ("L60&ndash;79", "The written analysis, printed with the results so the conclusion never drifts from the numbers it describes."),
        ("L82&ndash;83", "<strong>The fix.</strong> A model-based agent whose beliefs expire."),
        ("L84&ndash;86", "Same model as before, plus a record of <em>when</em> each square was last observed, and a step counter. Line 85's <code>-10**9</code> is a sentinel meaning &ldquo;never seen&rdquo;, guaranteed to look infinitely stale."),
        ("L88&ndash;92", "Advance the clock, record the observation and its timestamp."),
        ("L93&ndash;94", "Unchanged reflex rule."),
        ("L95&ndash;98", "<strong>The key condition.</strong> The agent now believes the world is clean only if every square is <em>both</em> believed clean <em>and</em> was observed within the last <code>staleness_limit</code> steps. Knowledge has an expiry date."),
        ("L99&ndash;101", "Idle if that holds; otherwise patrol."),
        ("L105&ndash;108", "Run the fixed agent on the same seeds and print its row under the table for comparison."),
    ]) + outp(24) + """
<h3>What the numbers actually said</h3>
<p>The hypothesis was <strong>half right</strong>, and being wrong about the other half is the most
useful thing in this exercise.</p>
""" + table(
        ["Architecture", "Perf.", "Clean", "What happened"],
        [["Simple Reflex", "93.4", "73%", "Never stops, so it re-senses constantly. Memorylessness is now an <em>advantage</em>."],
         ["Goal-Based", "93.4", "73%", "<strong>Did not collapse.</strong> It has no <code>NoOp</code> branch, so it degenerates into the same patrol loop."],
         ["Model-Based", "67.8", "52%", "Latches onto &ldquo;both clean&rdquo; and idles forever on a snapshot of a world that has moved on."],
         ["Utility-Based", "58.8", "45%", "Worst. Moving scores &minus;2, sucking a clean square scores 0 &mdash; so it parks on one square and lets the other rot."],
         ["Learning", "58.9", "45%", "Its reward only credits <code>Suck</code>, so it learns the same park-and-suck policy."],
         ["<strong>Model-Based + decay</strong>", "<strong>100.1</strong>", "69%", "Best performance of all: patrols like the reflex agent but skips pointless moves."]],
        ['', 'n', 'n', '']) + note("The real answer", """
<p>What degrades is not <em>having a model</em>. It is <strong>trusting a stale model</strong>
(model-based) or <strong>pricing movement without pricing neglect</strong> (utility-based). Note the
fix does not remove the memory &mdash; it adds an expiry date to it, and comes out ahead of every
original agent.</p>
<p>Also note the utility agent's bug was invisible in the original tutorial. Its 10/10 score there
came from starting on the dirty square. This exercise is what exposed it.</p>""")))

    # ---------------------------------------------------------------- 11 ex2
    S.append(dict(id="ex2", num="11", rail="Exercise 2", title="Exercise 2 — Taking away the location sensor", body="""
<p class="lede"><strong>The task:</strong> <code>percept()</code> returns only the dirt status, never
the location. Which architectures still work, which break, and why?</p>
""" + code(26, "Solution &mdash; three agents under partial observability") + ann([
        ("L1&ndash;4", "The setup: this is a <em>sensor</em> downgrade, breaking the S in PEAS."),
        ("L6&ndash;10", "Subclass overriding one method. <code>percept</code> now returns a bare <code>&quot;Dirty&quot;</code>/<code>&quot;Clean&quot;</code> string instead of a tuple. That is the entire change &mdash; one line, and it invalidates most of the agents written so far."),
        ("L13&ndash;17", "A runner for the blind world, otherwise identical to the original."),
        ("L21&ndash;25", "<strong>(a) The memoryless agent.</strong> Its program now takes <code>status</code> directly, since there is no tuple to unpack. With no location it cannot choose a direction, so line 24 hard-codes one: suck dirt, otherwise always go right."),
        ("L29&ndash;35", "<strong>(b) Randomised.</strong> Identical, except line 34 flips a coin instead of committing to a direction. Still completely memoryless &mdash; the <code>rng</code> is not state about the world, just a source of variety."),
        ("L39&ndash;43", "<strong>(c) Model-based &mdash; the interesting one.</strong> The docstring holds the insight: the <em>actuators</em> are absolute and deterministic. <code>Left</code> always lands on A regardless of where you were. So the agent can learn its position from its own <em>actions</em>, even though its sensors will never tell it."),
        ("L44", "Belief state: where I think I am, plus what I have seen at each square."),
        ("L46&ndash;49", "If the agent knows where it is, it can attribute the reading to that square. If it does not, the reading is unattributable and must be discarded."),
        ("L50&ndash;53", "Dirt gets sucked regardless of whether the agent knows where it is &mdash; that rule never needed a location. Line 52 pre-records the result, since <code>Suck</code> is guaranteed to succeed on a dirty square."),
        ("L54&ndash;56", "<strong>The self-localisation move.</strong> Lost, on a clean square: deliberately go <code>Left</code>. Because that is a teleport-to-A, the agent <em>now knows</em> it is at A. It has spent one move to convert &ldquo;I am lost&rdquo; into &ldquo;I am at A&rdquo;."),
        ("L57&ndash;58", "Once both squares are known clean, idle &mdash; a capability the blind reflex agents cannot express at all."),
        ("L59&ndash;60", "Otherwise move to the other square, updating the belief about position <em>before</em> moving. This is dead reckoning: tracking position by remembering your own actions."),
        ("L64&ndash;69", "Run all three and print each one's full action sequence, which is what makes the failure visible."),
        ("L71&ndash;87", "The analysis, printed alongside."),
    ]) + outp(26) + """
<h3>The verdict</h3>
""" + table(
        ["Agent", "Result", "Why"],
        [["(a) Fixed reflex", "<strong>Breaks</strong> (&minus;6, never clean)",
          "Committed to <code>Right</code>, started on a clean B, and re-entered B six times. The dirt in A was never found."],
         ["(b) Random reflex", "Works, eventually (+5)",
          "A coin flip guarantees it visits both squares given enough steps. When you cannot sense, randomise."],
         ["(c) Model-based", "<strong>Works perfectly</strong> (+8)",
          "<code>Left</code> &rarr; <code>Suck</code> &rarr; <code>Right</code> &rarr; <code>NoOp</code>. It localised itself, cleaned, verified, and stopped."]],
        ['', '', '']) + warn("The most important detail", """
<p>Agent (a) does not crash. It raises nothing, logs nothing, and returns a legal action every single
step. It just quietly stops making progress while paying a penalty. Degraded sensors produce
<em>silent</em> failures, which is precisely why you cannot catch this class of bug by checking that
the code runs.</p>""") + note("The general rule", """
<p>Partial observability breaks memoryless agents, and internal state is what buys the observability
back. Agent (c) never gains a location sensor &mdash; it <em>reconstructs</em> location from its own
action history. That is the whole reason the model-based box exists in the hierarchy.</p>""")))

    # ---------------------------------------------------------------- 12 ex3
    S.append(dict(id="ex3", num="12", rail="Exercise 3", title="Exercise 3 — Scaling to a row of four", body="""
<p class="lede"><strong>The task:</strong> extend <code>LOCATIONS</code> to
<code>[&quot;A&quot;,&quot;B&quot;,&quot;C&quot;,&quot;D&quot;]</code> in a row, update the movement
logic, and ask whether the simple reflex agent still reaches <code>NoOp</code> sensibly.</p>

""" + note("Scaling forces a semantic change", """
<p>With two squares, <code>Left</code> could be <em>absolute</em> &mdash; &ldquo;go left&rdquo; and
&ldquo;go to A&rdquo; were the same instruction. In a row of four they are not. Movement has to become
<em>relative</em>, and that single change is what makes this exercise more than bookkeeping. (It is
also what Exercise 2's agent (c) was quietly exploiting.)</p>""") + code(28, "Solution &mdash; an n-square row") + ann([
        ("L1&ndash;7", "The setup and the new world: four squares in a row."),
        ("L10&ndash;11", "A fresh class rather than a subclass &mdash; the movement model differs too much to inherit cleanly."),
        ("L13&ndash;16", "As before, but the world size is now a parameter. Line 16's comprehension is unchanged except that it iterates over <code>self.locations</code>."),
        ("L17", "Position is now an <strong>index</strong>, not a name. That is the core representational change: in a row you need to know how far along you are, not just which label you are on."),
        ("L18&ndash;19", "Scorecard and trace, unchanged."),
        ("L21&ndash;23", "A <code>@property</code> so <code>agent_location</code> still reads like an attribute, keeping every agent's <code>percept</code> unpacking working unchanged. The old interface is preserved over a new representation."),
        ("L25&ndash;26", "Identical percept contract: current location and its status."),
        ("L28&ndash;33", "<code>Suck</code> is unchanged &mdash; it never depended on the world's shape."),
        ("L34&ndash;36", "<strong><code>Left</code> is now relative:</strong> one step back, <code>max(0, ...)</code> clamping at the wall. Note the &minus;1 is charged <em>even when the move is blocked</em> &mdash; walking into a wall costs you."),
        ("L37&ndash;39", "<code>Right</code> mirrors it, clamped at the far end."),
        ("L40&ndash;43", "<code>NoOp</code> and the error branch, unchanged."),
        ("L44&ndash;45", "<code>dict(self.status)</code> is a shallow copy &mdash; sufficient here, because the values are immutable strings."),
        ("L47&ndash;55", "<code>is_clean</code> and the runner, unchanged in structure."),
        ("L58&ndash;66", "<strong>The reflex agent, scaled.</strong> Memoryless, so its rule can only key off <code>(location, status)</code>. Line 65 is the best fixed rule available: sweep right, and reverse at the right wall."),
        ("L69&ndash;73", "<strong>The model-based agent, scaled.</strong> Two pieces of state now: what it has seen at every square (line 72) <em>and</em> which way it is travelling (line 73). That second one is new &mdash; it did not need it with two squares."),
        ("L75&ndash;80", "Observe, then suck dirt. Line 79 pre-records the success."),
        ("L81&ndash;82", "Idle once every square is known clean. <code>all(...)</code> over the model is <code>False</code> while any entry is still <code>None</code>, so the agent cannot stop before visiting everywhere &mdash; the unvisited state is doing real work."),
        ("L83&ndash;87", "Reverse direction at either wall, then travel that way. This is the sweep the reflex agent cannot perform."),
        ("L91&ndash;96", "Run both and print their action sequences."),
        ("L98&ndash;108", "The analysis of what those sequences show."),
        ("L110&ndash;118", "<strong>The scaling test.</strong> Same agents at n=2, 4 and 8, with a step budget of <code>4n</code> so the budget scales with the problem. Line 111 generates location names with <code>chr(ord('A') + i)</code>."),
        ("L120&ndash;128", "The second half of the analysis: the independent reason <code>NoOp</code> is unreachable."),
        ("L131&ndash;137", "A randomised memoryless agent, applying Exercise 2's lesson to this problem."),
        ("L140&ndash;151", "20 trials per size, since a random agent's single run tells you nothing. Line 148 exploits <code>True == 1</code> to count successes."),
        ("L153&ndash;157", "The closing caveat about how slow random search actually is."),
    ]) + outp(28) + """
<h3>The answer: no, and worse than you would expect</h3>
<p>Look at the reflex agent's trace: after cleaning its way right it settles into
<code>Left Right Left Right ...</code>. It is not patrolling the row &mdash; it is
<strong>stuck oscillating between the last two squares</strong>.</p>
<p>The rule &ldquo;<code>Left</code> at the right wall, otherwise <code>Right</code>&rdquo; makes that
wall a 2-cycle: step left off the wall, and the rule immediately sends you back. <strong>Direction of
travel is state</strong>, and a memoryless agent has nowhere to keep it, so it cannot commit to a
leftward sweep. At n=4 it gets away with this because it cleaned everything on the way out. At n=8 it
does not:</p>
""" + table(
        ["Row size", "Simple reflex", "Model-based", "Random reflex (20 trials)"],
        [["n = 2", "3, clean", "9, clean", "&mdash;"],
         ["n = 4", "17, clean", "27, clean", "cleaned 14/20, avg 13.7"],
         ["n = 8", "<strong>&minus;21, never clean</strong>", "32, clean", "cleaned 13/20, avg 4.8"]],
        ['', '', '', '']) + """
<p>And <code>NoOp</code> is out of reach for a second, independent reason: it is only rational once
you know <em>every</em> square is clean &mdash; a fact about squares you are not standing on. A
memoryless agent has no place to put that fact, so its rule set cannot even express the stopping
condition.</p>
""" + warn("Randomising is survivable, not free", """
<p>The coin flip escapes the oscillation trap, but a random walk's cover time grows like
<em>n</em>&sup2;, so inside a fixed step budget it frequently has not visited everything yet &mdash;
it fails to clean the row in about a third of trials at both sizes. Memory is not a luxury here;
it is the difference between <em>O(n)</em> and <em>O(n&sup2;)</em>.</p>""")))

    # ---------------------------------------------------------------- 13 ex4
    S.append(dict(id="ex4", num="13", rail="Exercise 4", title="Exercise 4 — Adding time pressure", body="""
<p class="lede"><strong>The task:</strong> add a time-pressure term to
<code>utility_based_agent</code> &mdash; a deadline after which <code>Suck</code> is worth less
&mdash; and observe how the agent's choices shift.</p>

<p>Two supporting repairs are needed first, both diagnosed in Exercise 1. The original utility agent
prices a move at a flat &minus;2 with no term for what it might find, so <strong>travel is never
worth it</strong>; and its beliefs never expire, so a square it cleaned long ago still looks clean.
Adding a deadline to an agent that refuses to move would demonstrate nothing.</p>
""" + code(30, "Solution &mdash; deadline, lookahead and decaying belief") + ann([
        ("L1&ndash;14", "The three changes, and a note that this cell reuses Exercise 1's stochastic world &mdash; a static world has no time dimension worth pressuring."),
        ("L16&ndash;17", "Every knob is a parameter, so the behaviour can be swept rather than argued about."),
        ("L18&ndash;20", "State: battery and clock together, beliefs about each square, and when each was last observed. Squares start <code>&quot;Unknown&quot;</code>, which is distinct from clean or dirty."),
        ("L22&ndash;24", "<strong>The deadline term.</strong> A clean square is worth full value up to the deadline; afterwards its worth decays geometrically at <code>decay ** (t - deadline)</code>. At <code>decay=0.6</code> that is a fast fade &mdash; five steps past the deadline, value is down to about 8%."),
        ("L26&ndash;33", "<strong>The decaying belief.</strong> Known dirty is certainty (1.0); never visited is a coin flip (0.5); otherwise the probability it has become dirty again grows with how long ago you looked: <code>1 - (1 - respawn_belief) ** age</code>. This is Exercise 1's staleness fix expressed as a probability rather than a hard cutoff &mdash; and it is <em>calibrated to the true respawn rate</em>, which is what makes it a model rather than a guess."),
        ("L35&ndash;37", "<code>Suck</code> on dirt is worth 10, scaled by the deadline. On a clean square it now scores <strong>&minus;0.5</strong> rather than 0 &mdash; a small explicit penalty that breaks the original's tie with <code>NoOp</code> and stops the agent burning battery on pointless sucking."),
        ("L38&ndash;42", "<strong>The lookahead.</strong> A move is worth the probability of finding dirt, times its deadline-scaled value, minus the travel cost. Line 40 catches a move to the square you are already on. This is the line that makes travel rational &mdash; and it is only possible because line 26 gives the agent an opinion about a square it cannot see."),
        ("L43&ndash;45", "The low-battery penalty, carried over unchanged."),
        ("L46", "<code>NoOp</code> is still exactly 0 &mdash; the fixed baseline every other option is measured against. This is what makes the crossover meaningful."),
        ("L48&ndash;52", "Advance the clock, record the observation and its timestamp."),
        ("L53&ndash;54", "The hard battery constraint still overrides everything."),
        ("L55&ndash;57", "Score all four actions into a dict, then take the best. <code>max(scores, key=scores.get)</code> returns the winning <em>key</em>."),
        ("L58&ndash;61", "Optional per-step tracing of every score. This is how you debug a utility agent: you cannot tell why it chose something without seeing the numbers it rejected."),
        ("L62&ndash;66", "Update belief after sucking, drain battery for real actions, return."),
        ("L70&ndash;76", "One verbose run: 18 steps, deadline at 6, so you can watch the transition happen live."),
        ("L78&ndash;89", "The sweep: nine deadline settings &times; 60 seeds each. Sixty is not decoration &mdash; at 8 seeds the ordering was noisy enough to be misread as a real reversal."),
        ("L91&ndash;106", "The analysis, including an explicit note that the small 6-versus-4 wobble is seed noise, not a finding."),
    ]) + outp(30) + """
<h3>What the trace shows</h3>
<p>Follow the <code>Suck</code> column down the verbose run &mdash; the agent's own valuation of
cleaning, decaying in real time:</p>
""" + table(
        ["Step", "Value of Suck on dirt", "What the agent does"],
        [["t &le; 6 (before deadline)", "+10.0", "Patrols: <code>Right</code>, <code>Left</code>, <code>Right</code> &mdash; travel is clearly worth it"],
         ["t = 9", "+2.2", "Still sucks dirt under it, but no longer travels for it"],
         ["t = 13", "+0.3", "Barely worth the actuation"],
         ["t &ge; 14", "&mdash;", "Idles. <code>NoOp</code>'s flat 0 now beats everything"]],
        ['', 'n', '']) + """
<p>The move column tells the same story from the other side: <code>Left</code> starts at <code>+3.0</code>
and sinks to <code>&minus;2.0</code>. Once it crosses below <code>NoOp</code>'s zero, travelling stops.
A little later <code>Suck</code> crosses too, and cleaning stops.</p>

<h3>The sweep</h3>
<p>Tighten the deadline and the crossover simply happens earlier, so the table slides rather than
flipping at some threshold &mdash; cleanliness falls monotonically from <strong>76%</strong> at no
pressure to <strong>50%</strong> at maximum pressure.</p>
""" + note("Why this is the payoff exercise", """
<p><strong>Nobody wrote &ldquo;if late, stop cleaning.&rdquo;</strong> There is no such branch anywhere
in the code. The behaviour emerges from arithmetic between competing terms &mdash; which is exactly
what utility-based agents are for, and exactly why they are the hardest to debug. Exercise 1's failure
was not a broken rule; it was two terms priced wrong. A reflex agent's bugs are in its rules, where you
can read them. A utility agent's bugs are in its <em>numbers</em>.</p>""")))

    # ---------------------------------------------------------------- 14 close
    S.append(dict(id="lands", num="14", rail="Where it lands", title="Where this lands", body="""
<p class="lede">Across four exercises the same pattern keeps surfacing: <strong>an architecture is not
better or worse in the abstract &mdash; it is better or worse for an environment.</strong></p>
""" + table(
        ["Environment property", "What it breaks", "What it rewards"],
        [["Dirt reappears (non-episodic)", "Beliefs that never expire", "Re-sensing, or beliefs with a decay policy"],
         ["Location not observable", "Memoryless rules", "Internal state &mdash; or randomisation as a cheap substitute"],
         ["More than two squares", "Fixed direction rules (the oscillation trap)", "State for <em>direction</em>, not just contents"],
         ["A deadline", "Fixed goals", "A utility function that can trade goals off"]],
        ['', '', '']) + """
<h3>The through-line</h3>
<p>Notice that every exercise found a bug the original six-step, two-square, fully observable episode
could not surface:</p>
<ul class="plain">
<li>The <strong>goal-based agent has no goal test</strong> &mdash; hidden in the original because
scoring 5 looked like a reasonable result rather than a missing branch.</li>
<li>The <strong>utility agent never travels</strong> &mdash; hidden because it happened to start on
the dirty square and scored top marks.</li>
<li>The <strong>model-based agent trusts stale beliefs</strong> &mdash; hidden because in an episodic
world beliefs cannot go stale.</li>
<li>The <strong>reflex agent oscillates at walls</strong> &mdash; hidden because with two squares
there is no wall to get stuck against.</li>
</ul>
<p>The agents did not change. The environment got honest.</p>
""" + note("Carry this into Lecture 2", """
<p><strong>Most agent failures are environment assumptions that stopped holding.</strong> Not bad
algorithms &mdash; correct algorithms, still running correctly, in a world that no longer matches the
PEAS spec they were written against.</p>
<p>That is why serious agent work is dominated by <em>evaluation</em> rather than by architecture, and
it is the same reason LLM agents are hard: the environment is the open world, and it never stops
drifting away from the spec you built for.</p>""") + """
<h3>If you want to go further</h3>
<ol class="steps">
<li>Combine Exercises 1 and 3: dirt that respawns in a row of eight. Does the decaying model-based
agent still hold up, or does the row get too long to keep beliefs fresh?</li>
<li>Give the learning agent a reward that credits cleanliness rather than the <code>Suck</code>
action, and see whether it stops parking.</li>
<li>Make movement stochastic &mdash; a 10% chance a move fails &mdash; and watch dead reckoning
break. That is the step from a model to a <em>probabilistic</em> model, and it is where the next
part of the course goes.</li>
</ol>
"""))

    return S

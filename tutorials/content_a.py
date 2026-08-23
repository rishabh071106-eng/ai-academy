from build import code, ann, outp, note, warn, table, world, code_block, src


def sections():
    S = []

    # ---------------------------------------------------------------- 00 idea
    S.append(dict(id="idea", num="00", rail="The one idea", title="The one idea to hold on to", body="""
<p class="lede">Everything in this notebook is a variation on a single loop. The agent
<em>senses</em>, <em>decides</em>, and <em>acts</em>; the world changes; it senses again.</p>

<p>An <strong>agent</strong> is anything that perceives its environment through <strong>sensors</strong>
and acts on it through <strong>actuators</strong>. What it does is defined by an <strong>agent
function</strong> that maps a percept sequence to an action. That function is an abstraction; the
<strong>agent program</strong> is the concrete code that implements it. The five architectures in this
tutorial are five different ways of writing that program.</p>

""" + note("The split that matters", """
<p>The notebook keeps the <strong>environment</strong> and the <strong>agent</strong> in separate objects
that share nothing but a percept and an action string. The environment knows the whole world; the agent
knows only what <code>percept()</code> hands it. Every interesting result later comes from that gap.</p>""") + """

<h3>What each architecture adds</h3>
""" + table(
        ["Architecture", "What it adds", "The question it can answer"],
        [["<strong>Simple reflex</strong>", "Nothing &mdash; rules on the current percept only",
          "&ldquo;What is under me right now?&rdquo;"],
         ["<strong>Model-based reflex</strong>", "Internal state: memory of what it has seen",
          "&ldquo;What is the world like, including where I am not?&rdquo;"],
         ["<strong>Goal-based</strong>", "An explicit goal and a plan to reach it",
          "&ldquo;What sequence gets me to the state I want?&rdquo;"],
         ["<strong>Utility-based</strong>", "A scoring function over competing outcomes",
          "&ldquo;Which of these imperfect options is best?&rdquo;"],
         ["<strong>Learning</strong>", "A feedback loop that edits its own policy",
          "&ldquo;What worked last time?&rdquo;"]]) + """
<p>They are cumulative in capability but not in cost. The whole payoff of the exercises at the end is
discovering that more capability is not automatically better &mdash; each addition brings its own
failure mode.</p>
"""))

    # ---------------------------------------------------------------- 01 env
    S.append(dict(id="environment", num="01", rail="The environment", title="The environment (the world the agent lives in)", body="""
<p class="lede">This is the longest cell in the notebook and the most important. Read it as a
contract: it defines exactly what the agent is allowed to know and exactly what it is allowed to do.</p>
""" + code(2, "Cell 1 &mdash; the vacuum world") + ann([
        ("L1", "The only import the core tutorial needs. <code>random</code> generates the starting world &mdash; and later, the learning agent's exploration."),
        ("L2", "<code>deepcopy</code> is imported for one job, on line 36. It is what makes the history a genuine <em>trace</em> instead of the same dictionary repeated."),
        ("L4", "The world is two squares, <code>A</code> and <code>B</code>. A module-level constant so both the environment and the agents refer to the same world. Exercise 3 changes this line and discovers how much depends on it."),
        ("L6", "The environment is its own class. The agent is not a method on it &mdash; that separation is the whole design."),
        ("L7", "<code>dirt_prob</code> is the chance each square starts dirty. <code>seed</code> makes a run reproducible, which is what lets you compare architectures fairly."),
        ("L8", "A <em>private</em> random generator, not the global <code>random</code> module. So the world's layout cannot be shifted by anything else in the notebook calling <code>random</code> &mdash; which matters, because the learning agent does exactly that."),
        ("L9", "A dict comprehension building <code>{'A': 'Dirty'|'Clean', 'B': ...}</code>. Each square is dirty with probability <code>dirt_prob</code>. This dictionary <em>is</em> the world."),
        ("L10", "The agent's starting square, also drawn from the seeded generator."),
        ("L11", "The scorecard, starting at zero. The comment states the whole performance measure: <strong>+10 per successful clean, &minus;1 per move</strong>. That ratio is what makes travelling worthwhile &mdash; and Exercise 4 is about what happens when you change it."),
        ("L12", "An empty list that will collect <code>(location, action, world_state)</code> triples so you can inspect behaviour afterwards."),
        ("L14&ndash;16", "<strong>The sensors.</strong> The single most consequential method here. It returns a tuple of the agent's <em>current location</em> and the status of <em>that square only</em>. It cannot see the other square. Everything the agent does not know, it does not know because of this one line."),
        ("L18&ndash;19", "<strong>The actuators.</strong> Takes an action string and applies its effect to the world."),
        ("L20", "Cache the location <em>before</em> the action potentially moves the agent. Line 36 needs the square the action was taken <em>from</em>."),
        ("L21&ndash;24", "<code>Suck</code> only scores when the square was actually dirty. Sucking a clean square is silently free: no reward, and no penalty either. Harmless here &mdash; but that free no-op is exactly the loophole Exercise 1 catches the utility agent exploiting."),
        ("L25&ndash;27", "<code>Left</code> sets the location to <code>&quot;A&quot;</code> &mdash; note this is <strong>absolute, not relative</strong>. In a two-square world &ldquo;go left&rdquo; and &ldquo;go to A&rdquo; are the same thing. That coincidence hides a real assumption, and Exercises 2 and 3 both turn on it. Cost: &minus;1."),
        ("L28&ndash;30", "<code>Right</code> is the mirror image: go to <code>B</code>, pay &minus;1."),
        ("L31&ndash;32", "<code>NoOp</code> changes nothing and costs nothing. It is the only free action, which makes it the baseline every utility comparison is measured against."),
        ("L33&ndash;34", "Anything else is a programming error, raised loudly. A cheap contract check that stops a typo in an agent from silently becoming a no-op."),
        ("L36", "Append the step to the trace. The <code>deepcopy</code> matters: <code>self.status</code> is mutated in place, so storing it directly would leave every entry pointing at the same dict and the trace would show the final state six times over."),
        ("L37", "Return the fresh percept as a convenience. The runner ignores it and calls <code>percept()</code> itself, so this is belt-and-braces."),
        ("L39&ndash;40", "A god's-eye check on whether the whole world is clean. Note carefully: <strong>this is a method on the environment, not the agent.</strong> The agent can never call it &mdash; it would be cheating. Knowing when to stop is something each architecture must earn for itself."),
        ("L43&ndash;46", "A sanity check. Build a world with <code>seed=1</code>, print the true state, then print what the agent would actually perceive."),
    ], sec=2) + outp(2) + """
<p>Look at those two output lines together. The world is
""" + world(True, False, "A") + """ &mdash; but the percept is just
<code>('A', 'Dirty')</code>. The fact that <code>B</code> is already clean exists in the environment
and is invisible to the agent. Hold that thought; it is the entire plot.</p>
"""))

    # ---------------------------------------------------------------- 02 PEAS
    S.append(dict(id="peas", num="02", rail="PEAS", title="PEAS: specifying the task before you code it", body="""
<p class="lede">PEAS &mdash; Performance, Environment, Actuators, Sensors &mdash; is a checklist for
pinning down a task precisely enough to build for it. Here it is written out as a plain dictionary.</p>
""" + code(4, "Cell 2 &mdash; the task specification") + ann([
        ("L1&ndash;6", "A plain dictionary, one key per PEAS letter. There is no clever machinery here on purpose: the value is in being forced to <em>write the four answers down</em> before writing agent code."),
        ("L2", "<strong>Performance</strong>: reward for clean squares, small penalty per move. Note that this is a description of lines 11, 24, 27 and 30 of the previous cell &mdash; the spec and the code have to agree, and nothing enforces it but you."),
        ("L3", "<strong>Environment</strong>: two locations, each dirty or clean. Small, static, fully observable at each square, and episodic. Every one of those four properties is deliberately broken by one of the exercises."),
        ("L4", "<strong>Actuators</strong>: the four legal action strings, matching the branches of <code>execute()</code> exactly."),
        ("L5", "<strong>Sensors</strong>: current location and dirt status <em>of the current location</em>. The phrasing carries the limitation."),
        ("L8&ndash;9", "Print each pair. <code>f&quot;{k:12s}&quot;</code> left-pads the key to 12 characters so the colons line up into a column."),
    ], sec=4) + outp(4) + note("Why this cell earns its place", """
<p>Every failure in the exercise section is a PEAS assumption that stopped being true. Dirt that
reappears breaks <em>Environment</em>. Hiding the location breaks <em>Sensors</em>. A deadline breaks
<em>Performance</em>. Writing PEAS down is what makes those failures legible instead of mysterious.</p>""")))

    # ---------------------------------------------------------------- 03 runner
    S.append(dict(id="runner", num="03", rail="The run loop", title="The run loop (the harness everything is scored by)", body="""
<p class="lede">Seven lines, and it is the sense&ndash;decide&ndash;act cycle in its plainest possible
form. Every score in this tutorial comes out of this function.</p>
""" + code(7, "Cell 4 &mdash; the harness") + ann([
        ("L1", "Takes an <em>agent program</em> &mdash; a function from percept to action &mdash; plus a step budget and a seed. Because the agent is just a function, every architecture can be scored by the identical harness."),
        ("L2", "A fresh environment per run. Passing the same seed to every agent guarantees they all face the same starting world, which is what makes the comparison table meaningful."),
        ("L3", "Run for a fixed number of steps. <code>_</code> signals the counter is unused. Note there is <strong>no termination check</strong> &mdash; the loop does not stop when the world is clean. That is deliberate: it means idling has to be a choice the agent makes, not a favour the harness does for it."),
        ("L4", "<strong>Sense.</strong> Ask the environment what the agent can currently perceive."),
        ("L5", "<strong>Decide.</strong> Hand that percept to the agent program and receive an action string. This line is the entire agent interface."),
        ("L6", "<strong>Act.</strong> Apply the action to the environment, which updates the world, the score and the trace."),
        ("L7", "Return final score, whether the world ended up clean, and the full trace."),
    ], sec=7) + warn("A detail worth noticing", """
<p>Six steps is a tight budget for a world that needs at most one move and two sucks. That tightness
is why <code>NoOp</code> is worth points: an agent that keeps pacing after the job is done burns
&minus;1 per step, and there are only six steps to spend.</p>""")))

    # ---------------------------------------------------------------- 04 reflex
    S.append(dict(id="reflex", num="04", rail="1 · Simple reflex", title="Architecture 1 — Simple reflex", body="""
<p class="lede">Condition&ndash;action rules on the current percept. No memory of anything.</p>
""" + code(6, "Cell 3 &mdash; simple reflex agent") + ann([
        ("L1", "A <em>factory</em>: calling <code>simple_reflex_agent()</code> returns a fresh program. Every architecture in the notebook follows this shape, so the comparison loop can call <code>factory()</code> uniformly and each agent starts with clean internal state."),
        ("L2", "The docstring is the agent function in English: dirty &rarr; clean it, otherwise move."),
        ("L3", "The inner function is the actual agent program. Its only input is <code>percept</code> &mdash; no history, no world access."),
        ("L4", "Unpack the tuple from <code>percept()</code> into the two things the agent knows."),
        ("L5&ndash;6", "Rule one: if the square under me is dirty, suck. Immediate and always correct."),
        ("L7&ndash;8", "Rule two: a clean square at <code>A</code> means go right."),
        ("L9&ndash;10", "Rule three: otherwise (clean, at <code>B</code>) go left."),
        ("L11", "Return the program. Nothing is captured in the closure &mdash; <strong>there is no state to capture.</strong> That absence is the definition of this architecture."),
    ], sec=6) + """
<h3>Watching it run</h3>
<p>The trace cell runs the agent and prints one line per step.</p>
""" + code(8, "Cell 5 &mdash; trace, seed=3") + ann([
        ("L1", "Run the agent and keep only the trace; <code>_, _,</code> discards score and cleanliness. Note <code>seed=3</code> &mdash; a different world from the default."),
        ("L2", "<code>enumerate(trace, 1)</code> numbers the steps from 1, and each entry unpacks into the triple stored on line 36 of the environment."),
        ("L3", "<code>{action:6s}</code> pads the action to six characters so the arrows line up into a readable column."),
    ], sec=8) + outp(8) + """
<p>Step by step, with the world drawn after each action:</p>
<ol class="steps">
<li>Starts at <strong>B</strong>, which is clean, so the rule says go left. """ + world(True, False, "B") + """</li>
<li>Now at <strong>A</strong>, which is dirty &rarr; <code>Suck</code>. The world is now spotless. """ + world(False, False, "A") + """</li>
<li>At <strong>A</strong>, clean &rarr; the rule says go right. Cost: &minus;1.</li>
<li>At <strong>B</strong>, clean &rarr; go left. Cost: &minus;1.</li>
<li>&hellip;and it paces back and forth until the step budget runs out.</li>
</ol>
""" + warn("The failure", """
<p>From step 3 onward this agent is <em>doing damage</em> &mdash; four wasted moves, &minus;4 points,
in a world that has been clean since step 2. It cannot stop, and the reason is precise: stopping
requires knowing that <em>both</em> squares are clean, and it can only ever see one. Final score:
<strong>+10 &minus; 5 = 5</strong>.</p>""")))

    # ---------------------------------------------------------------- 05 model
    S.append(dict(id="model", num="05", rail="2 · Model-based", title="Architecture 2 — Model-based reflex", body="""
<p class="lede">The same reflex rules, plus one dictionary of memory. That dictionary is worth four
points.</p>
""" + code(10, "Cell 6 &mdash; model-based reflex agent") + ann([
        ("L1", "Same factory shape as before."),
        ("L2", "<strong>The internal state.</strong> One dict holding what the agent believes about each square, starting at <code>None</code> for &ldquo;never looked&rdquo;. Because it lives in the enclosing function, it persists across calls to <code>program</code> &mdash; this is a closure doing the work an object would do."),
        ("L4&ndash;5", "The program and the same unpacking as before."),
        ("L6", "<strong>Update the model.</strong> Record what was just observed, keyed by location. The <code>None</code> for the other square is what stops the agent claiming knowledge it does not have."),
        ("L7&ndash;8", "Unchanged reflex rule: dirt under me gets sucked immediately."),
        ("L9&ndash;10", "<strong>The new capability.</strong> If the model says both squares are clean, emit <code>NoOp</code> and stop burning move penalties. This condition is literally inexpressible for the previous agent &mdash; it mentions a square the agent is not standing on."),
        ("L11", "Otherwise fall back to the reflex move. Reaching this line means at least one square is still <code>None</code> or <code>Dirty</code>, so there is a reason to travel."),
        ("L12", "Return the program &mdash; this time <em>with</em> <code>model</code> captured in its closure."),
    ], sec=10) + code(11, "Cell 7 &mdash; trace, same seed=3") + ann([
        ("L1&ndash;3", "Identical to the previous trace cell, with the agent swapped. Same world, same seed, same harness &mdash; so any difference in output is caused by architecture alone. That is the experiment."),
    ], sec=11) + outp(11) + """
<p>The first two steps are identical to the reflex agent's. Step 3 is where they part:</p>
""" + table(
        ["Step", "Simple reflex", "Model-based", "Why"],
        [["1", "<code>Left</code>", "<code>Left</code>", "Both see a clean B, both move"],
         ["2", "<code>Suck</code>", "<code>Suck</code>", "Both see dirt at A"],
         ["3", "<code>Right</code>", "<strong><code>NoOp</code></strong>",
          "The model now holds A=Clean <em>and</em> B=Clean, from step 1"],
         ["4&ndash;6", "pacing", "<code>NoOp</code>", "&minus;3 versus 0"]],
        ['', '', '', '']) + note("The lesson", """
<p><strong>5 &rarr; 9 points, from one dictionary.</strong> The model-based agent is not smarter about
cleaning &mdash; it cleans exactly the same dirt on the same step. It is smarter about
<em>stopping</em>. Memory did not buy better actions, it bought the ability to know the job was
finished. Keep that distinction; Exercise 1 is about what happens when that belief goes stale.</p>""")))

    return S

from build import code, ann, outp, note, warn, table, world


def sections():
    S = []

    # ---------------------------------------------------------------- 06 goal
    S.append(dict(id="goal", num="06", rail="3 · Goal-based", title="Architecture 3 — Goal-based", body="""
<p class="lede">Instead of firing rules, the agent holds an explicit goal &mdash; &ldquo;both squares
clean&rdquo; &mdash; and forms a small plan to reach it.</p>
""" + code(13, "Cell 8 &mdash; goal-based agent") + ann([
        ("L1", "Same factory shape."),
        ("L2", "The plan: a list of queued actions. Empty means &ldquo;no plan right now, make one&rdquo;. In a real goal-based agent this is where a search algorithm's output would land; here the world is small enough that the plan is one move long."),
        ("L4&ndash;5", "The program and the usual unpacking."),
        ("L6", "<code>nonlocal</code> lets line 11 <em>rebind</em> <code>goal_reached_plan</code> to a new list. Without it, that assignment would create a fresh local variable and the plan would silently vanish between calls. (Line 6 is not needed for the <code>.pop()</code> on line 12, which mutates rather than rebinds &mdash; it is needed specifically because of line 11.)"),
        ("L7&ndash;8", "Dirt under the agent is an immediate sub-goal, satisfied before any planning happens."),
        ("L9&ndash;11", "If there is no plan, make one: the only useful thing to do on a clean square is go check the other one."),
        ("L12", "Pop the front of the plan and execute it. With a one-step plan this is the same as returning the move &mdash; but the <em>shape</em> is the point: decide a sequence, then follow it."),
        ("L13", "Return the program, with the plan captured in the closure."),
    ], sec=13) + warn("Read the code, not the label", """
<p>This agent has a goal in its name but nowhere in its logic. There is no check for
&ldquo;is the goal satisfied?&rdquo; and therefore <strong>no <code>NoOp</code> branch anywhere</strong>.
It always returns <code>Suck</code> or a move, so it paces forever exactly like the simple reflex
agent &mdash; and scores exactly the same, <strong>5</strong>. Watch for this in the comparison table;
it is the tutorial's most useful trap. The architecture is only as good as the goal test you
actually write.</p>""")))

    # ---------------------------------------------------------------- 07 utility
    S.append(dict(id="utility", num="07", rail="4 · Utility-based", title="Architecture 4 — Utility-based", body="""
<p class="lede">A goal is binary: reached or not. A utility function is a number, so it can
<em>trade off</em> competing concerns &mdash; here, cleanliness against a battery budget.</p>
""" + code(15, "Cell 9 &mdash; utility-based agent") + ann([
        ("L1", "The battery budget is a parameter, so you can experiment with scarcity."),
        ("L2", "The battery is wrapped in a dict rather than a bare number for the same reason as before: rebinding a plain <code>int</code> inside the nested function would need <code>nonlocal</code>, while mutating a dict entry does not."),
        ("L4", "<strong>The utility function.</strong> It scores a hypothetical action &mdash; nothing is applied to the world. This is the key move of the architecture: the agent can compare options it will not take."),
        ("L5", "Every action starts at zero utility."),
        ("L6&ndash;7", "<code>+10</code> for sucking actual dirt &mdash; deliberately mirroring the environment's own reward on line 24. Note this only fires when the square <em>is</em> dirty; <code>Suck</code> on a clean square scores 0."),
        ("L8&ndash;9", "<code>&minus;2</code> for any move. Note this is <em>harsher</em> than the environment's real &minus;1 &mdash; the agent's preferences do not have to match the true performance measure, and the mismatch has consequences."),
        ("L10&ndash;11", "A further &minus;5 for moving on a nearly flat battery. This is the actual trade-off: at full charge a move is a minor cost, at low charge it is close to unthinkable."),
        ("L12", "Return the score."),
        ("L14&ndash;15", "The program proper."),
        ("L16&ndash;17", "A hard constraint that overrides the arithmetic: no battery, no action. Some limits should not be negotiable in utility terms."),
        ("L18", "All four legal actions become candidates &mdash; including <code>NoOp</code>, which always scores exactly 0 and therefore acts as the <strong>do-nothing baseline</strong>. Any action scoring below 0 is worse than idling."),
        ("L19", "<code>max</code> with a <code>key</code> scores every candidate and picks the best. On a tie Python keeps the <em>first</em> maximum in list order, so the order on line 18 is a silent tie-breaker &mdash; <code>Suck</code> wins ties over <code>NoOp</code>."),
        ("L20&ndash;21", "Any real action drains one unit of battery; <code>NoOp</code> is free."),
        ("L22&ndash;23", "Return the action, then the program."),
    ], sec=15) + note("Where this scores 10", """
<p>In the standard six-step run this is the joint best agent. On a clean square, <code>Suck</code>
and <code>NoOp</code> both score 0 while moving scores &minus;2, so the tie on line 19 goes to
<code>Suck</code> &mdash; a harmless no-op in the environment. It cleans what is under it and never
wastes a move.</p>""") + warn("…and where it is quietly broken", """
<p>Read that again: <strong>moving is never worth it.</strong> A move always scores &minus;2, and the
utility function has no term for &ldquo;there might be dirt over there.&rdquo; This agent only ever
scores 10 because it happens to start on the dirty square. Exercise 1 puts it in a world where it has
to travel, and it parks on one square forever. The bug is invisible in the tutorial's own test.</p>""")))

    # ---------------------------------------------------------------- 08 learning
    S.append(dict(id="learning", num="08", rail="5 · Learning", title="Architecture 5 — Learning", body="""
<p class="lede">A learning element that edits the agent's own policy from observed reward &mdash; a
toy version of the feedback loop behind RLHF.</p>
""" + code(17, "Cell 10 &mdash; learning agent") + ann([
        ("L1&ndash;2", "<code>q</code> maps a <code>(state, action)</code> pair to a learned value &mdash; the agent's policy, and the thing that changes over time. This is a miniature Q-table."),
        ("L3", "Remembers the previous step, because the reward for an action only becomes visible on the <em>next</em> percept. This one-step delay is the central difficulty of reinforcement learning in miniature."),
        ("L5&ndash;6", "The percept is used directly as the state."),
        ("L7", "<code>NoOp</code> is deliberately excluded from the action set &mdash; the agent is never allowed to learn to idle."),
        ("L8&ndash;9", "<code>setdefault</code> lazily initialises unseen pairs to 0.0, so line 21's lookup can never raise."),
        ("L11&ndash;12", "The <strong>learning element</strong>, skipped on the very first step when there is no previous action to credit."),
        ("L13", "The reward signal: <code>+10</code> if the square is now clean <em>and</em> the last action was <code>Suck</code>, otherwise <code>&minus;1</code>. Note what this cannot distinguish &mdash; sucking dirt and sucking an already-clean square both look like success."),
        ("L14&ndash;15", "The update: move the stored value <em>halfway</em> toward the observed reward. <code>0.5</code> is the learning rate &mdash; high, so it adapts within six steps, but it also means the value never settles."),
        ("L17&ndash;19", "<strong>Exploration.</strong> 10% of the time, act randomly. Without this the agent would lock onto whatever it tried first and never discover anything better."),
        ("L20&ndash;21", "<strong>Exploitation.</strong> The other 90%: take the highest-valued action for this state. Together, lines 18&ndash;21 are the classic epsilon-greedy policy."),
        ("L23&ndash;25", "Record this step as &ldquo;last&rdquo; so the next call can score it, return the action, return the program."),
    ], sec=17) + warn("Why it uses the global random", """
<p>Lines 18&ndash;19 call <code>random</code> directly, not a seeded private generator. That is why
the comparison cell has to call <code>random.seed(0)</code> before running &mdash; without it, this
agent's score changes between runs and the table stops being reproducible. It is also why Exercise 1
re-seeds inside its loop.</p>""") + note("Six steps is not learning", """
<p>It scores 10 here, but do not read that as the learning working. With six steps and a
learning rate of 0.5 it barely fills its table. What this cell demonstrates is the <em>shape</em> of a
learning agent &mdash; policy, reward, update, explore/exploit &mdash; not its competence.</p>""")))

    # ---------------------------------------------------------------- 09 compare
    S.append(dict(id="compare", num="09", rail="The comparison", title="Running all five side by side", body="""
<p class="lede">Same world, same seed, same six steps. Every difference in the table is caused by
architecture and nothing else.</p>
""" + code(19, "Cell 11 &mdash; the comparison") + ann([
        ("L1&ndash;7", "<code>run</code> defined a second time, character for character identical to cell 4. Harmless &mdash; it just makes this cell runnable on its own &mdash; but worth noticing so you do not go hunting for a difference that is not there."),
        ("L10", "Seed the <em>global</em> generator. This exists solely for the learning agent's exploration on line 18 of the previous cell; without it the last row of the table would wobble."),
        ("L11&ndash;17", "A list of <code>(name, factory)</code> pairs. Storing the <em>factory</em> rather than a built program is what guarantees each agent starts with fresh internal state."),
        ("L19", "The header row. <code>{'Architecture':22s}</code> left-aligns in 22 columns, <code>{'Performance':&gt;12s}</code> right-aligns in 12 &mdash; that is what makes the columns line up."),
        ("L20", "A rule of 46 dashes, matching 22+12+12."),
        ("L21&ndash;22", "For each entry, call the factory to build a fresh program and run it. <code>_</code> discards the trace."),
        ("L23", "Print the row. <code>{perf:12d}</code> formats the score as a right-aligned integer; <code>str(clean)</code> converts the bool before padding it, since <code>:&gt;12s</code> requires a string."),
    ], sec=19) + outp(19) + """
<h3>How to read this table</h3>
""" + table(
        ["Architecture", "Score", "What actually happened"],
        [["Simple Reflex", "5", "Cleans on step 2, then paces for four steps at &minus;1 each."],
         ["Model-Based Reflex", "9", "Same clean, then <code>NoOp</code> &mdash; it knows the job is done."],
         ["Goal-Based", "5", "Identical to simple reflex: no goal test, so no stopping."],
         ["Utility-Based", "10", "Starts on the dirty square, sucks, then never pays to move."],
         ["Learning", "10", "Explores into the same behaviour. Six steps is not enough to call this learned."]],
        ['', 'n', '']) + note("The honest reading", """
<p>The scores do <strong>not</strong> rank the architectures. Utility-based ties for first here by
being lucky about where it started, goal-based ties for last because of a missing branch, and the
learning agent's 10 is barely distinguishable from noise. A six-step, two-square, fully observable,
episodic world is simply too easy to separate them.</p>
<p>That is exactly why the exercises exist. Each one breaks a different assumption in the PEAS spec,
and each one produces a <em>different</em> ranking.</p>""")))

    return S

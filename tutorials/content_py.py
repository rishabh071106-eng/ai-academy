from hl import code_block
from build import note, warn, table


def snippet(src):
    return code_block(src)


def sections():
    return [dict(id="python", num="01", rail="Python you need",
                 title="The Python you need, in one section", body="""
<p class="lede">If you are new to Python, read this once before the code sections. Everything the
notebook uses appears here with a tiny example. Each line-by-line annotation later also carries an
orange <strong>Python</strong> box explaining the syntax on that line, so you can come back here only
when you want the fuller version.</p>

<h3>Indentation is not decoration</h3>
<p>Most languages group code with curly braces. Python groups it with <strong>indentation</strong> &mdash;
the spaces at the start of a line are part of the meaning. Lines indented under an <code>if</code>
run only when it is true.</p>
""" + snippet('''if status == "Dirty":
    return "Suck"          # indented: only runs when the condition is true
return "Right"             # not indented: runs whenever we get this far''') + """
<p>Note <code>==</code> to <em>compare</em> and a single <code>=</code> to <em>assign</em>. Mixing
them up is the most common beginner error in any language.</p>

<h3>The four containers</h3>
""" + table(
    ["Type", "Looks like", "What it is"],
    [["<strong>string</strong>", '<code>"Dirty"</code>', "Text. Single or double quotes, your choice."],
     ["<strong>list</strong>", '<code>["A", "B"]</code>', "An ordered, changeable sequence. Add with <code>.append(x)</code>."],
     ["<strong>tuple</strong>", '<code>("A", "Dirty")</code>', "Like a list but <em>cannot be changed</em> after creation. Used here for percepts."],
     ["<strong>dict</strong>", '<code>{"A": "Dirty"}</code>', "A lookup table of key &rarr; value. This is how the world's state is stored."]],
    ['', '', '']) + """
<p>You read a dict with square brackets, and write to it the same way:</p>
""" + snippet('''status = {"A": "Dirty", "B": "Clean"}
print(status["A"])          # -> Dirty          (read)
status["A"] = "Clean"       #                   (write, or create if missing)''') + """
<p>Indexing counts from <strong>zero</strong>, and negative numbers count from the end:</p>
""" + snippet('''row = ["A", "B", "C", "D"]
row[0]     # -> "A"    the first item
row[1]     # -> "B"    the second
row[-1]    # -> "D"    the last item''') + """

<h3>Unpacking</h3>
<p>You will see this on almost every agent's first line. If the right side has several values, the
left side can name them all at once:</p>
""" + snippet('''percept = ("A", "Dirty")
location, status = percept      # location is now "A", status is now "Dirty"''') + """
<p>When you do not need one of the values, the convention is to name it <code>_</code>, which means
&ldquo;ignore this&rdquo;:</p>
""" + snippet('''_, _, trace = run(agent)         # keep only the third value''') + """

<h3>Functions</h3>
""" + snippet('''def run(agent_program, steps=6, seed=42):
    ...
    return env.performance''') + """
<ul class="plain">
<li><code>def</code> starts a function; the indented block below is its body.</li>
<li><code>steps=6</code> is a <strong>default</strong>: callers can leave it out and get 6.</li>
<li><code>return</code> hands a value back <em>and exits immediately</em> &mdash; nothing after it runs.</li>
<li>Returning several comma-separated values actually returns one tuple, which the caller can unpack.</li>
</ul>

<h3>Functions are values (this is the big one)</h3>
<p>In Python a function can be stored in a variable, put in a list, and passed to another function.
The presence or absence of parentheses decides everything:</p>
""" + snippet('''program            # the function itself, not run
program(percept)   # RUN it, with percept as input''') + """
<p>That distinction is why <code>run(simple_reflex_agent())</code> has two sets of brackets: the inner
pair builds an agent, and <code>run</code> calls it later, once per step.</p>

<h3>A function that returns a function (a &ldquo;closure&rdquo;)</h3>
<p>Every agent in this notebook is written this way, so it is worth slowing down on:</p>
""" + snippet('''def make_counter():
    count = {"n": 0}            # lives in the OUTER function
    def step():                 # an inner function
        count["n"] += 1         # it can see and change count
        return count["n"]
    return step                 # hand back the inner function

c = make_counter()
c()    # -> 1
c()    # -> 2      the count SURVIVED between calls''') + """
<p>The inner function keeps access to the outer function's variables even after the outer function has
finished. That is a <strong>closure</strong>, and it is how these agents remember things without being
classes. Call <code>make_counter()</code> twice and you get two independent counters &mdash; which is why
the comparison loop stores factories and calls each one fresh.</p>
""" + warn("Why the state is wrapped in a dict", """
<p>Inside a nested function, <code>count = count + 1</code> would create a brand-new local variable
instead of changing the outer one. Two ways round it: write <code>nonlocal count</code> first, or
store the value inside a dict and write <code>count["n"] += 1</code>, which modifies rather than
re-assigns. The notebook uses both &mdash; that is why you keep seeing single values wrapped in
dictionaries.</p>""") + """

<h3>Conditional expressions</h3>
<p>An <code>if</code> squeezed into a single value. Read it left to right: <em>this</em> if
<em>condition</em>, otherwise <em>that</em>.</p>
""" + snippet('''return "Right" if location == "A" else "Left"

# exactly the same thing, written out:
if location == "A":
    return "Right"
else:
    return "Left"''') + """

<h3>Comprehensions</h3>
<p>A one-line way to build a list or dict from a loop.</p>
""" + snippet('''# dict comprehension: one entry per location
{loc: "Dirty" for loc in ["A", "B"]}         # -> {"A": "Dirty", "B": "Dirty"}

# list comprehension
[x * 2 for x in [1, 2, 3]]                   # -> [2, 4, 6]

# the same shape without brackets is a "generator" - it produces values
# one at a time, which is all that all() and sum() need
all(v == "Clean" for v in status.values())   # True only if EVERY one matches
sum(1 for v in status.values() if v == "Clean")   # counts the clean ones''') + """

<h3>max() with a key</h3>
<p>The utility and learning agents both turn on this one function.</p>
""" + snippet('''actions = ["Suck", "Left", "Right", "NoOp"]
best = max(actions, key=lambda a: utility(a))''') + """
<ul class="plain">
<li><code>lambda a: ...</code> is a small unnamed function, taking <code>a</code> as its input.</li>
<li><code>max(items, key=f)</code> runs <code>f</code> on every item and returns the <strong>item</strong>
with the highest score &mdash; not the score itself.</li>
<li>On a tie, the <strong>first</strong> item in the list wins. That silent tie-break matters more than
once in this notebook.</li>
</ul>

<h3>Classes</h3>
<p>Only the environment uses a class. A class is a blueprint; an <em>instance</em> is one thing built
from it.</p>
""" + snippet('''class VacuumEnvironment:
    def __init__(self, seed=42):        # runs automatically when you create one
        self.performance = 0            # self.x = data belonging to THIS instance

    def percept(self):                  # a method: a function inside a class
        return self.agent_location

env = VacuumEnvironment(seed=1)         # create an instance
env.percept()                           # call a method - you never pass self''') + """
<ul class="plain">
<li><code>self</code> is the instance itself. It is always the first parameter, and Python fills it
in for you when you call the method.</li>
<li>Names with <code>self.</code> in front survive after the method ends. Plain local names do not.</li>
<li><code>__init__</code>'s double underscores mark it as one of Python's special method names.</li>
</ul>
<p>Two further pieces appear in the exercise solutions:</p>
""" + snippet('''class StochasticVacuumEnvironment(VacuumEnvironment):   # inheritance
    def execute(self, action):
        super().execute(action)     # run the ORIGINAL version first
        ...                         # then add new behaviour

    @property                       # a decorator: lets you write env.agent_location
    def agent_location(self):       # with NO parentheses, though it is really a method
        return self.locations[self.index]''') + """

<h3>f-strings and format specs</h3>
<p>The <code>f</code> before the quote lets you drop variables into text with <code>{}</code>. What
comes after a colon controls the padding, which is what makes all the output tables line up.</p>
""" + snippet('''name, perf = "Simple Reflex", 5

f"{name}"          # -> 'Simple Reflex'
f"{name:22s}"      # -> 'Simple Reflex         '   string, padded to 22, left-aligned
f"{perf:>12d}"     # -> '           5'            whole number, padded to 12, RIGHT-aligned
f"{perf:+6.1f}"    # -> '  +5.0'                  always show sign, 6 wide, 1 decimal
f"{0.73:.0%}"      # -> '73%'                     fraction as a percentage''') + """
<p>A few smaller pieces that appear throughout:</p>
""" + table(
    ["You'll see", "It means"],
    [["<code>x += 1</code>", "Add to what is already there. Also <code>-=</code> for subtract."],
     ["<code>#</code>", "A comment. Python ignores the rest of the line."],
     ["<code>&quot;&quot;&quot;...&quot;&quot;&quot;</code>", "A string that can span lines. As the first line of a function it is a <em>docstring</em> (documentation)."],
     ["<code>None</code>", "&ldquo;Nothing here yet&rdquo;. Test it with <code>is None</code>, never <code>== None</code>."],
     ["<code>and</code> / <code>or</code> / <code>not</code>", "Combine or flip true/false conditions."],
     ["<code>in</code>", "Membership: <code>action in (&quot;Left&quot;, &quot;Right&quot;)</code>."],
     ["<code>**</code>", "Powers, not multiplication. <code>0.6 ** 3</code> is 0.6&times;0.6&times;0.6."],
     ["<code>pass</code>", "Do nothing. Used where Python demands an indented block but you want none."],
     ["<code>raise</code>", "Stop with an error."],
     ["<code>&quot; &quot;.join(items)</code>", "Glue a sequence of strings together with a space between."],
     ["<code>True</code> is <code>1</code>", "Booleans are numbers, so <code>count += is_clean()</code> counts how many times it was true."]],
    ['', '']) + note("You do not need to memorise this", """
<p>Skim it now, start reading the code, and come back when a line looks strange. Every annotation in
the sections that follow has its own Python box, so the explanation you need is always right next to
the line that needs it.</p>"""))]

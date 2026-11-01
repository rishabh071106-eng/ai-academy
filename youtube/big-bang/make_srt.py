import re, sys

# (narration start, narration end, cues). Each cue is its on-screen lines.
SECTIONS = [
 (11, 37, [
  ["This is the story of everything."],
  ["13.8 billion years ago,", "the universe was not a place in space."],
  ["It was all of space. All of time."],
  ["All of matter and energy,", "compressed into a point"],
  ["hotter and denser than anything", "we can imagine."],
  ["Scientists call it a singularity."],
  ["There was no before, and no outside."],
  ["Then, it began to change."],
 ]),
 (41, 68, [
  ["The Big Bang was not an explosion", "in empty space."],
  ["It was the expansion of space itself."],
  ["In the first trillionth of a trillionth", "of a trillionth of a second,"],
  ["a phase called inflation stretched", "the universe from smaller than an atom"],
  ["to larger than a galaxy."],
  ["The fastest growth ever.", "Faster than light."],
  ["Energy poured out", "as a seething soup of particles,"],
  ["at trillions of degrees."],
 ]),
 (71, 99, [
  ["As space expanded, it cooled."],
  ["Within three minutes, protons and neutrons", "fused into the first nuclei:"],
  ["hydrogen and helium."],
  ["But the universe was still an opaque fog,", "and light could not travel."],
  ["Then, 380,000 years in,", "electrons joined the nuclei to form atoms."],
  ["The fog cleared. Light was released."],
  ["We still detect it today,", "as the cosmic microwave background."],
 ]),
 (101, 127, [
  ["What followed were the dark ages.", "No stars."],
  ["Only vast clouds of hydrogen and helium,", "drifting in darkness."],
  ["Gravity pulled gently on tiny", "differences in density,"],
  ["gathering gas into", "denser and denser clumps."],
  ["After about 100 million years,", "one clump grew so dense and hot"],
  ["that nuclear fusion ignited."],
  ["The first star was born.", "And the darkness began to end."],
 ]),
 (131, 157, [
  ["Stars were born by the billions."],
  ["Gravity gathered them", "into the first galaxies,"],
  ["and the galaxies into a vast cosmic web", "of glowing filaments,"],
  ["wrapped around enormous voids."],
  ["The largest stars lived fast", "and died in supernovae,"],
  ["forging carbon, oxygen, and iron,", "and scattering them across space."],
  ["Every heavy element in the universe", "was made inside a star."],
 ]),
 (161, 185, [
  ["Nine billion years later,", "a cloud of this enriched gas collapsed"],
  ["in a quiet arm of the Milky Way,", "forming our Sun and the planets around it."],
  ["Atoms forged in the Big Bang", "and in dying stars"],
  ["became oceans, air, and life."],
  ["Today, the universe is still expanding."],
  ["You are part of its story."],
  ["This is Stellar Gift."],
 ]),
]
VIDEO_END = 190

# The narration says these numbers in words, so weight them by their spoken length.
SPOKEN = {"13.8 billion": "thirteen point eight billion",
          "380,000": "three hundred eighty thousand",
          "100 million": "one hundred million"}
GAP = 0.08  # small gap between consecutive subtitles

def weight(lines):
    t = " ".join(lines)
    for a, b in SPOKEN.items():
        t = t.replace(a, b)
    w = len(t)
    if t.rstrip()[-1] in ".?!": w += 8   # pause after a sentence
    elif t.rstrip()[-1] in ",:;": w += 3  # short pause after a clause
    return w

def ts(x):
    ms = round(x * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

out, n, problems = [], 0, []
for start, end, cues in SECTIONS:
    ws = [weight(c) for c in cues]
    total, t = sum(ws), float(start)
    for c, w in zip(cues, ws):
        dur = (end - start) * w / total
        a, b = t, t + dur - GAP
        t += dur
        n += 1
        out.append(f"{n}\n{ts(a)} --> {ts(b)}\n" + "\n".join(c) + "\n")
        chars = len(" ".join(c))
        cps = chars / (b - a)
        if any(len(l) > 42 for l in c) or len(c) > 2: problems.append(f"#{n} line too long")
        if not (1.0 <= b - a <= 7.0): problems.append(f"#{n} duration {b-a:.2f}s")
        if cps > 20: problems.append(f"#{n} reading speed {cps:.1f} cps")
        if b > VIDEO_END: problems.append(f"#{n} past video end")

open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
print(f"{n} subtitles written to {sys.argv[1]}")
print("problems:", problems or "none")

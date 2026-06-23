# Authoring Guide — "Learn AI Like a Kid"

You are writing ONE chapter of a print-ready children's book. Match the existing
house style EXACTLY. Before writing, read these two files for reference:

- `book/parts/ch04.html` — the **gold-standard chapter**. Mirror its structure, tone, and SVG quality.
- `book/parts/05-cast.html` — the **character bible** (names, species, personalities, colors).
- `book/theme.css` — the CSS classes you are allowed to use (do not invent new ones; do not add `<style>`).

## Audience & voice
- Readers are **ages 10–14**. Smart, curious, NOT babies. No baby-talk, no condescension.
- Warm, exciting, a little funny. Short sentences mixed with longer ones. Second person ("you") is welcome.
- Explain **real algorithms accurately** but with zero jargon-dumping. Every technical word is introduced gently, then reinforced in the Word Bank.
- A light running story with the animal characters carries each lesson. Use dialogue.
- British/American spelling: use American spelling.

## The cast (use 1–3 per chapter; pick whoever fits)
- **Professor Hoot** — wise owl, the teacher. Asks questions instead of giving answers.
- **Bolt** — rabbit, fast and impatient. Great for "fast but wrong."
- **Mango** — monkey, endlessly curious, asks "why?", a bit mischievous.
- **Pip** — mouse, shy, careful, notices tiny details.
- **Tess** — tortoise, slow, steady, methodical, usually right.
- **Coco** — parrot, repeats what she hears. Perfect for language/sequences.
- **Rex** — dog, loyal, loves treats. Perfect for rewards/reinforcement.
- **Ziggy** — zebra, loves patterns, sorting, spotting differences.

## Required structure (in this order)
Mirror `ch04.html` precisely. The opening `<section>` tag MUST carry the data
attributes shown in your specific assignment (these drive the auto Table of Contents).

1. `.chapter-opener` with `.kicker` (use the color class given), `.chapter-title`, `.chapter-tagline`, and a `.hero-art` SVG showing a story scene.
2. `.story` block: first paragraph triggers the drop-cap automatically (just write normally). Use `<p class="says"><b>Name:</b> "..."</p>` for dialogue. Include at least one `<h2>` subheading inside the story.
3. `<aside class="callout how">` — **How It Really Works**: the honest, accurate explanation of the actual algorithm. This is the most important box. Be correct.
4. At least one `<figure class="diagram">` with a hand-drawn **SVG** diagram + `<figcaption>`.
5. `<aside class="callout try">` — **Try It Yourself**: a real, doable hands-on activity (paper, friends, household items; computer only with a trusted adult).
6. `<aside class="callout oops">` — **Watch Out**: a real pitfall or way the algorithm fails.
7. `<aside class="callout words">` — **Word Bank**: a `<dl>` with 3–5 real terms (`<dt>`/`<dd>`).
8. `<aside class="callout idea">` — **Big Idea**: one memorable sentence.
9. `.recap` block: `<h3>Before You Turn the Page…</h3>`, a `<ul>` of 4 takeaways, and a one-line teaser for the next class.

You may add an extra `.story` paragraph or a second callout/figure if it helps, but keep the chapter focused. Target **900–1,400 words** of body text.

## SVG rules (hand-drawn, flat, friendly)
- Inline `<svg>` only. No external images, no `<img>`, no base64. Always include `role="img"` and a descriptive `aria-label`.
- Use the book palette ONLY: green `#3FA34D`, blue `#2E7FC2`, yellow `#F2B705`, coral `#E5533C`, purple `#7C5CBF`, pink `#E76FA1`, ink `#2A2622`, paper `#FFFDF7`, warm line `#cdbf9c`. Soft shadow = `<ellipse fill="#000" opacity=".06">`.
- Style: flat shapes, rounded corners, simple cute faces (two dot eyes + small mouth). Look at the cast SVGs and ch04 SVGs and match that level. Keep each SVG under ~40 elements so it stays clean.
- Diagrams must actually illustrate the concept (a tree, a graph, a number line, a grid of pixels, a path through a maze, etc.) — not just decoration. Use `<text font-family="Fredoka, sans-serif">` for labels.
- The hero SVG `viewBox` is typically about `0 0 360 220`; diagram SVGs about `0 0 420 260`. CSS scales them.

## Accuracy
Keep the simplification HONEST. Don't say things that are wrong. It's fine to say
"this is a simplified picture." Where a concept connects to another class, you may
reference it (e.g., "we'll meet this again in the class on neural networks").

## Output
Write the COMPLETE chapter as a single self-contained HTML fragment (just the
`<section>…</section>`), nothing else. No markdown code fences. No `<html>`/`<head>`/`<style>`.

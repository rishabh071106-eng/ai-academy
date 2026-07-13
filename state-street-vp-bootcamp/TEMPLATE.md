# Chapter Template — State Street VP Bootcamp

Every daily chapter in this handbook follows this structure. Written for: **VP, Product Development (Digital Experience), State Street — prepared for Rishabh Sharma.**

---

## Required structure per day

```
# Day NN — <Title>
> Week N · <Volume name> · Est. reading time: 60–90 min

## 🎯 Learning objectives        (4–6 bullets: "By the end of today you can…")
## 🧭 Where this fits            (1 short paragraph + a Mermaid "map" diagram
                                  showing today's topic inside the bigger system)
## Part 1 — Core concepts        (the morning read: clear explanations, analogies,
                                  banking examples, at least 1 diagram + 1 table)
## Part 2 — The system deep dive (the afternoon read: how it actually works
                                  end-to-end at a custodian bank; sequence /
                                  flowchart diagrams; failure modes; data flows)
## Part 3 — The VP lens          (what YOU own: decisions, trade-offs, metrics,
                                  stakeholder map, questions to ask your teams)
## 🏦 State Street context       (how this shows up at State Street specifically:
                                  products, platforms, org realities — clearly
                                  labeled as representative/public-knowledge)
## 💪 Exercises                  (2–3 practical exercises you can do at a desk)
## ❓ Self-check quiz            (5 questions WITH answers in a <details> block)
## 🔑 Key takeaways              (5–7 bullets)
## 📚 Going deeper               (books, standards, public docs — no paywalled links)
## Tomorrow                      (1 line teaser for the next day)
```

## Diagram requirements

- **Minimum 4 Mermaid diagrams per day** (GitHub renders them natively).
- Mix diagram types across the chapter: `flowchart`, `sequenceDiagram`,
  `stateDiagram-v2`, `erDiagram`, `mindmap`, `timeline`, `pie`, `quadrantChart`.
- Mermaid safety rules (so GitHub never fails to render):
  - Quote any node label containing parentheses, commas, or slashes: `A["NAV (per share)"]`
  - No `&` in labels — write "and".
  - Keep `sequenceDiagram` participant names single-word; use `as` for display names.
- Use tables generously for comparisons, lifecycles, RACI, metrics.

## Tone and quality bar

- MBA-level executive handbook, not AI-generated notes: precise, concrete,
  opinionated where it helps decision-making.
- Every abstract concept gets a **worked banking example with numbers**.
- Explain jargon on first use; the glossary carries the full definitions.
- "VP lens" sections must contain real decisions and trade-offs, not platitudes.
- Anything about State Street internals must be public-knowledge or clearly
  framed as "representative of large custodians".

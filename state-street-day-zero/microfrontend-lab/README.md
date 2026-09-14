# Micro front-end lab

The JD lists "micro front-end frameworks". The idea: a client portal built as **independently deployable pieces** (alerts, documents, holdings, reporting) composed at runtime by a thin **shell** that owns identity, routing and design tokens. Teams ship on their own schedules; the client sees one product. That is exactly how a custodian consolidates fragmented platforms into "a unified client experience".

## Run the demo (no build tools)

```bash
cd state-street-day-zero/microfrontend-lab
python3 -m http.server 8080
# open http://localhost:8080/shell/
```

What to try: switch the signed-in user (the shell owns identity; both widgets re-render), navigate between routes (widgets lazy-load on first use), acknowledge an alert (state lives inside the widget). Open DevTools → Sources: `alerts.js` and `documents.js` are separate modules with no shared code except `tokens.css`.

## What is where

| Piece | Owner in a real bank | What it does here |
|---|---|---|
| `shell/index.html` | Platform / DX core team | Header, nav, user selector, route → widget registry, event bus |
| `shell/tokens.css` | Design system team | The only styling contract: colours, fonts, radius |
| `mfe-alerts/alerts.js` | Notifications team | A Web Component `<dx-alerts>` with its own data, logic and shadow-DOM styles |
| `mfe-documents/documents.js` | Documents team | A Web Component `<dx-documents>`, same contract, nothing shared |

## Next level: the real frameworks

Once the concept is clear, install one of the production approaches:

- **Module Federation (Webpack 5 / Rspack)** — the most common in banks. `npx create-mf-app` scaffolds a host and a remote; each builds and deploys separately; the host loads remotes by URL at runtime. Read: module-federation.io.
- **single-spa** — a router that mounts framework-agnostic apps (React, Angular, Vue side by side). `npx create-single-spa` scaffolds a root config plus apps; useful when legacy Angular pages and new React pages must coexist during a strangler-fig migration.
- **Native**: import maps + Web Components (what this lab does). Fewest moving parts; fine for widgets; weaker for whole-page apps with shared state.

Questions a VP asks about any micro front-end estate: who owns the shell; how are design tokens versioned; what happens when two widgets need the same data (fetch twice, or a shared read store); how is a broken remote isolated (error boundary per widget); how do you test the composed page, not just the pieces.

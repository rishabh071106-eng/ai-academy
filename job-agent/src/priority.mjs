// Which jobs come first: Magento, then PHP, then React, then front end, then
// full stack / e-commerce. A job's tier is the first tier (in this order) whose keyword
// appears in its title; if no tier matches the title, the job's description/card text is
// used the same way. Everything else is "Other" and comes last.
// Override the tiers in config.json ("priorityTiers": [{ "name", "keywords": [] }, …]).
import { loadConfig } from "./util.mjs";

export const DEFAULT_TIERS = [
  { name: "Magento", keywords: ["magento", "adobe commerce", "magento 2", "magento2", "hyva", "hyvä", "pwa studio"] },
  { name: "PHP", keywords: ["php", "symfony", "codeigniter", "yii", "cakephp", "wordpress", "woocommerce", "drupal"] },
  { name: "React", keywords: ["react", "reactjs", "react.js", "react js", "next.js", "nextjs", "next js", "redux", "typescript"] },
  { name: "Front end", keywords: ["front end", "frontend", "front-end", "ui developer", "web developer", "javascript", "html", "css", "jquery"] },
  { name: "Full stack", keywords: ["full stack", "fullstack", "full-stack", "e-commerce", "ecommerce", "graphql", "mysql"] },
];
export const OTHER = "Other";

const escapeRe = (k) => k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// Whole words only, so "react" does not match "reactive" and "node" does not match "nodes".
const reFor = (words) => new RegExp(`(^|[^a-z])(${words.map(escapeRe).join("|")})([^a-z0-9]|$)`, "i");

function load(cfg) {
  const list = Array.isArray(cfg?.priorityTiers) && cfg.priorityTiers.length ? cfg.priorityTiers : DEFAULT_TIERS;
  return list.filter((t) => t?.name && Array.isArray(t.keywords) && t.keywords.length).map((t) => ({ name: t.name, keywords: t.keywords, re: reFor(t.keywords) }));
}
export const TIERS = load(loadConfig());
/** Tier names in priority order, "Other" last (for the dashboard). */
export const TIER_NAMES = [...TIERS.map((t) => t.name), OTHER];

/**
 * tierOf(title, body?) → { index, name }. Lower index = apply first.
 * The title decides; the body (description, result card, match reasons) only breaks a title
 * that names no tier (e.g. "Senior Software Engineer").
 */
export function tierOf(title, body = "", tiers = TIERS) {
  for (const text of [String(title || ""), String(body || "")]) {
    if (!text.trim()) continue;
    const i = tiers.findIndex((t) => t.re.test(text));
    if (i >= 0) return { index: i, name: tiers[i].name };
  }
  return { index: tiers.length, name: OTHER };
}

/** Stable sort: tier first (Magento before PHP before React…), the original order within a tier. */
export function sortByTier(items, textOf, tiers = TIERS) {
  return items
    .map((item, i) => { const [title, body] = [].concat(textOf(item)); return { item, i, tier: tierOf(title, body, tiers).index }; })
    .sort((a, b) => a.tier - b.tier || a.i - b.i)
    .map((x) => x.item);
}

/** How the resume should lead for a job of this tier (all skill groups stay on it). */
export const FOCUS = {
  Magento: "Lead with Adobe Commerce / Magento 2: the Adobe Certified Expert credential, Magento 2 modules and customisations, PWA/Hyva/headless storefronts, performance, integrations. The React/Next.js and PHP groups follow right after.",
  PHP: "Lead with PHP: present her Magento work as PHP 7/8 + MySQL back-end engineering (REST/GraphQL APIs, OOP, design patterns, performance); Magento/Adobe Commerce next, then front end.",
  React: "Lead with React / Next.js / TypeScript front-end work (headless storefronts, component libraries, state management, performance); then Adobe Commerce/PHP back end.",
  "Front end": "Lead with front-end engineering: React / Next.js, JavaScript / TypeScript, HTML / CSS, responsive UI and performance; then Adobe Commerce/PHP back end.",
  "Full stack": "Balance both halves: React / Next.js front end and PHP / Adobe Commerce / MySQL / GraphQL back end, e-commerce end to end.",
};
export const focusFor = (name) => FOCUS[name] || "";

#!/usr/bin/env node
/*
 * AI Academy — Daily Chapter Generator
 *
 * What it does:
 *   1. Reads sources.json (RSS feeds + topic queue)
 *   2. Fetches the latest item titles from each RSS feed (for "what's happening now" context)
 *   3. Picks the next topic from the queue
 *   4. Calls the Claude API to write a new chapter in the house style
 *   5. Writes the chapter HTML and updates assets/chapters.json
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-ant-... node scripts/generate.mjs
 *
 * Dependencies:
 *   npm install @anthropic-ai/sdk
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Anthropic from '@anthropic-ai/sdk';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const MANIFEST = path.join(ROOT, 'assets', 'chapters.json');
const SOURCES  = path.join(ROOT, 'scripts', 'sources.json');
const CHAPTERS_DIR = path.join(ROOT, 'chapters');
const TEMPLATE_CHAPTER = path.join(CHAPTERS_DIR, 'what-is-ai-really.html');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ---------- helpers ----------

const slugify = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);

async function fetchRss(url) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(10_000) });
    const xml = await res.text();
    // very small, forgiving extractor
    const titles = [...xml.matchAll(/<title[^>]*>([^<]{5,200})<\/title>/gi)]
      .map(m => m[1].replace(/<!\[CDATA\[|\]\]>/g, '').trim())
      .slice(1, 6); // skip channel title, take next 5
    return titles;
  } catch (e) {
    console.warn(`  ! failed to fetch ${url}: ${e.message}`);
    return [];
  }
}

async function gatherSignal(sources) {
  console.log('Gathering signal from RSS feeds...');
  const headlines = [];
  for (const feed of sources.feeds) {
    const titles = await fetchRss(feed.url);
    if (titles.length) {
      headlines.push(`## ${feed.name}`);
      headlines.push(...titles.map(t => `- ${t}`));
    }
  }
  return headlines.join('\n');
}

// ---------- the Claude call ----------

async function writeChapter({ topic, chapterNumber, signalMd }) {
  const systemPrompt = `You are a writer for "AI Academy" — a daily site that explains AI to curious, smart, non-technical readers.
House style:
- Clear, confident, no hype, no marketing voice.
- Short paragraphs. Concrete examples. Occasional wry humor.
- Use "you" and "I" naturally. Active voice.
- Avoid: "In today's fast-paced world", "delve into", "unleash", "revolutionize", bullet lists longer than 6 items.
- Structure: strong hook, 3-5 H2 sections, one blockquote for a key idea, one callout for a fun fact, 700-1200 words.
- The reader has already read: "What is AI, really?", "How LLMs work", "Prompt engineering", "RAG vs fine-tune", "Agentic AI". Assume that baseline.`;

  const userPrompt = `Write the next daily chapter on the topic: "${topic}"

Today's AI news headlines (for context, cite a specific item naturally if genuinely relevant, otherwise ignore):
${signalMd}

Output ONLY valid JSON matching this schema, no prose before or after:
{
  "title": "short, punchy title (max 60 chars)",
  "subtitle": "one-sentence hook (max 140 chars)",
  "excerpt": "2-sentence preview for the homepage card (max 180 chars)",
  "tag": "one-word category — e.g. LLMs, Engineering, Safety, Theory, Agents, Practical",
  "readTime": "X min",
  "bodyHtml": "the chapter body as HTML. Use <h2>, <h3>, <p>, <ul>, <ol>, <li>, <blockquote>, <code>, <pre><code>, <strong>. For callout boxes use <div class=\\"callout\\"><div class=\\"ico\\">&#128161;</div><div>...content...</div></div>. Do not wrap in <html> or <body>. Do not include the title or subtitle (those go in a separate field)."
}`;

  const resp = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 6000,
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
  });

  let text = resp.content[0].text.trim();
  // strip any ```json fences
  text = text.replace(/^```(?:json)?\s*/, '').replace(/\s*```$/, '').trim();
  try {
    return JSON.parse(text);
  } catch (e) {
    // Retry once: find first { and last } and try again
    const start = text.indexOf('{');
    const end = text.lastIndexOf('}');
    if (start >= 0 && end > start) {
      return JSON.parse(text.slice(start, end + 1));
    }
    throw new Error(`Model output was not valid JSON: ${e.message}\n--- raw output ---\n${text.slice(0, 500)}`);
  }
}

// ---------- HTML writer ----------

function renderChapterPage({ ch, prevCh, nextCh }) {
  const tpl = (s) => s
    .replace(/{{TITLE}}/g, ch.title)
    .replace(/{{SUBTITLE}}/g, ch.subtitle)
    .replace(/{{TAG}}/g, ch.tag)
    .replace(/{{NUMBER}}/g, ch.number)
    .replace(/{{READTIME}}/g, ch.readTime)
    .replace(/{{DATE}}/g, ch.date)
    .replace(/{{BODY}}/g, ch.bodyHtml)
    .replace(/{{PREV_HREF}}/g, prevCh ? `${prevCh.slug}.html` : '#')
    .replace(/{{PREV_TITLE}}/g, prevCh ? prevCh.title : 'This is the start')
    .replace(/{{PREV_STYLE}}/g, prevCh ? '' : 'style="opacity:0.5;pointer-events:none"')
    .replace(/{{NEXT_HREF}}/g, nextCh ? `${nextCh.slug}.html` : '../index.html')
    .replace(/{{NEXT_TITLE}}/g, nextCh ? nextCh.title : 'Back to all chapters');

  return tpl(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{TITLE}} &mdash; AI Academy</title>
<meta name="description" content="{{SUBTITLE}}">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{SUBTITLE}}">
<meta property="og:type" content="article">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="alternate" type="application/rss+xml" title="AI Academy RSS" href="../rss.xml">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<nav><div class="nav-inner"><a href="../index.html" class="logo"><span class="logo-dot"></span> AI Academy</a><div class="nav-links"><a href="../index.html#chapters">Chapters</a><a href="../index.html#subscribe">Subscribe</a></div></div></nav>
<article class="reader">
<a href="../index.html" class="back">&larr; All chapters</a>
<div class="meta-row"><span class="tag">{{TAG}}</span><span>{{NUMBER}}</span><span>&middot;</span><span>{{READTIME}} read</span><span>&middot;</span><span>{{DATE}}</span></div>
<h1>{{TITLE}}</h1>
<p class="subtitle">{{SUBTITLE}}</p>
{{BODY}}
<div class="share-bar">
  <div class="label">Found this useful? Share it:</div>
  <div class="share-buttons">
    <button class="share-btn" onclick="shareTo('twitter')">&#128038; X/Twitter</button>
    <button class="share-btn" onclick="shareTo('linkedin')">&#128100; LinkedIn</button>
    <button class="share-btn" onclick="shareTo('whatsapp')">&#128172; WhatsApp</button>
    <button class="share-btn" id="copyBtn" onclick="copyLink()">&#128279; Copy link</button>
  </div>
</div>
<div class="nav-next">
  <a href="{{PREV_HREF}}" {{PREV_STYLE}}><div class="dir">&larr; Previous</div><div class="title">{{PREV_TITLE}}</div></a>
  <a href="{{NEXT_HREF}}" class="next"><div class="dir">Next &rarr;</div><div class="title">{{NEXT_TITLE}}</div></a>
</div>
</article>
<footer><div class="logo"><span class="logo-dot"></span> AI Academy</div><p>&copy; 2026 AI Academy. New chapters daily.</p></footer>
<script>
const pageUrl=encodeURIComponent(window.location.href);
const pageTitle=encodeURIComponent(document.title);
function shareTo(net){const urls={twitter:\`https://twitter.com/intent/tweet?text=\${pageTitle}&url=\${pageUrl}\`,linkedin:\`https://www.linkedin.com/sharing/share-offsite/?url=\${pageUrl}\`,whatsapp:\`https://wa.me/?text=\${pageTitle}%20\${pageUrl}\`};window.open(urls[net],'_blank','width=600,height=500');}
function copyLink(){navigator.clipboard.writeText(window.location.href).then(()=>{const b=document.getElementById('copyBtn');b.innerHTML='&check; Copied!';b.classList.add('copied');setTimeout(()=>{b.innerHTML='&#128279; Copy link';b.classList.remove('copied')},1800);});}
</script>
</body>
</html>`);
}

// ---------- main ----------

(async () => {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('ERROR: ANTHROPIC_API_KEY env var is required.');
    process.exit(1);
  }

  const sources = JSON.parse(await fs.readFile(SOURCES, 'utf8'));
  const manifest = JSON.parse(await fs.readFile(MANIFEST, 'utf8'));

  if (!sources.topicsQueue || !sources.topicsQueue.length) {
    console.error('Topics queue is empty. Add topics to scripts/sources.json.');
    process.exit(1);
  }

  const topic = sources.topicsQueue.shift();
  console.log(`Next topic: "${topic}"`);

  const signal = await gatherSignal(sources);
  console.log('Signal gathered. Writing chapter...');

  const draft = await writeChapter({
    topic,
    chapterNumber: manifest.chapters.length + 1,
    signalMd: signal,
  });

  let slug = slugify(draft.title);
  // Collision check: if a chapter with this slug already exists, append a suffix
  const existing = new Set(manifest.chapters.map(c => c.slug));
  if (existing.has(slug)) {
    let i = 2;
    while (existing.has(`${slug}-${i}`)) i++;
    slug = `${slug}-${i}`;
  }
  const today = new Date().toISOString().slice(0, 10);
  const num = String(manifest.chapters.length + 1).padStart(2, '0');

  const ch = {
    slug,
    number: `Chapter ${num}`,
    title: draft.title,
    subtitle: draft.subtitle,
    excerpt: draft.excerpt,
    tag: draft.tag,
    readTime: draft.readTime,
    date: today,
    bodyHtml: draft.bodyHtml,
  };

  const prevCh = manifest.chapters[manifest.chapters.length - 1] || null;
  const html = renderChapterPage({ ch, prevCh, nextCh: null });

  await fs.writeFile(path.join(CHAPTERS_DIR, `${slug}.html`), html, 'utf8');
  console.log(`Wrote chapters/${slug}.html`);

  // Update previous chapter's "next" link (best-effort)
  if (prevCh) {
    try {
      const prevPath = path.join(CHAPTERS_DIR, `${prevCh.slug}.html`);
      let prevHtml = await fs.readFile(prevPath, 'utf8');
      prevHtml = prevHtml.replace(
        /(class="next"><div class="dir">Next &rarr;<\/div><div class="title">)[^<]*(<\/div>)/,
        `$1${ch.title}$2`
      ).replace(
        /href="[^"]*"(\s+class="next")/,
        `href="${slug}.html"$1`
      );
      await fs.writeFile(prevPath, prevHtml, 'utf8');
    } catch (e) {
      console.warn(`  ! couldn't update prev chapter link: ${e.message}`);
    }
  }

  // Strip bodyHtml from the stored manifest entry (keep it small)
  delete ch.bodyHtml;
  manifest.chapters.push(ch);
  await fs.writeFile(MANIFEST, JSON.stringify(manifest, null, 2), 'utf8');

  // Save updated sources (topic removed from queue)
  await fs.writeFile(SOURCES, JSON.stringify(sources, null, 2), 'utf8');

  // Regenerate RSS feed
  const siteUrl = process.env.SITE_URL || 'https://example.com';
  const rssItems = [...manifest.chapters].reverse().slice(0, 30).map(c => `    <item>
      <title><![CDATA[${c.title}]]></title>
      <link>${siteUrl}/chapters/${c.slug}.html</link>
      <guid>${siteUrl}/chapters/${c.slug}.html</guid>
      <pubDate>${new Date(c.date).toUTCString()}</pubDate>
      <description><![CDATA[${c.excerpt}]]></description>
      <category>${c.tag}</category>
    </item>`).join('\n');
  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>AI Academy</title>
    <link>${siteUrl}</link>
    <description>Learn AI, one chapter at a time. New chapter daily.</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${rssItems}
  </channel>
</rss>`;
  await fs.writeFile(path.join(ROOT, 'rss.xml'), rss, 'utf8');

  // Regenerate sitemap.xml
  const urls = [
    `${siteUrl}/`,
    ...manifest.chapters.map(c => `${siteUrl}/chapters/${c.slug}.html`)
  ];
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url><loc>${u}</loc><lastmod>${today}</lastmod></url>`).join('\n')}
</urlset>`;
  await fs.writeFile(path.join(ROOT, 'sitemap.xml'), sitemap, 'utf8');

  console.log(`Done. Published "${ch.title}". ${sources.topicsQueue.length} topics left in queue.`);
  console.log(`RSS: rss.xml updated. Sitemap: sitemap.xml updated.`);
})();

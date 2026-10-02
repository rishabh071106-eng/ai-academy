// Checks data/catalog.json, data/exams/*.json and data/ncert.json against data/SCHEMA.md.
// Run: npm run validate
import fs from 'node:fs/promises';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const errors = [];
const err = (file, msg) => errors.push(`${file}: ${msg}`);
const read = async p => JSON.parse(await fs.readFile(path.join(ROOT, p), 'utf8'));
const TYPES = new Set(['concept', 'formula', 'example', 'tip', 'quiz']);

const catalog = await read('data/catalog.json');
const listed = catalog.categories.flatMap(c => c.exams.map(e => e.id));
const files = (await fs.readdir(path.join(ROOT, 'data/exams'))).filter(f => f.endsWith('.json'));
const ids = new Set(files.map(f => f.slice(0, -5)));

for (const id of listed) if (!ids.has(id)) err('catalog.json', `lists "${id}" but data/exams/${id}.json is missing`);
for (const id of ids) if (!listed.includes(id)) err(`${id}.json`, 'not listed in catalog.json');

let chapters = 0, cards = 0;
for (const f of files) {
  let ex;
  try { ex = await read(`data/exams/${f}`); } catch (e) { err(f, `invalid JSON: ${e.message}`); continue; }
  if (ex.id !== f.slice(0, -5)) err(f, `id "${ex.id}" does not match file name`);
  if (ex.core && !ids.has(ex.core)) err(f, `core "${ex.core}" has no file`);
  const seen = new Set();
  for (const s of ex.subjects || []) {
    if (!s.id || !s.chapters?.length) err(f, `subject "${s.name}" needs an id and chapters`);
    for (const c of s.chapters || []) {
      const key = `${s.id}/${c.id}`;
      if (seen.has(key)) err(f, `duplicate chapter ${key}`);
      seen.add(key); chapters++;
      if (!c.cards?.length) { err(f, `${key} has no cards`); continue; }
      c.cards.forEach((card, i) => {
        cards++;
        if (!TYPES.has(card.type)) err(f, `${key} card ${i}: unknown type "${card.type}"`);
        if (card.type === 'quiz') {
          if (!Array.isArray(card.options) || card.options.length < 2) err(f, `${key} card ${i}: quiz needs options`);
          else if (!Number.isInteger(card.answer) || card.answer < 0 || card.answer >= card.options.length) err(f, `${key} card ${i}: answer out of range`);
          if (!card.q) err(f, `${key} card ${i}: quiz needs q`);
        } else if (!card.title && !card.body && !card.points) err(f, `${key} card ${i}: empty card`);
      });
    }
  }
  for (const y of ex.pyq || []) for (const it of y.items || []) if (!/^https:\/\//.test(it.url || '')) err(f, `pyq ${y.year}: bad url ${it.url}`);
  for (const r of ex.resources || []) if (!/^https:\/\//.test(r.url || '')) err(f, `resource "${r.label}": bad url`);
}

const ncert = await read('data/ncert.json');
let books = 0;
for (const c of ncert.classes) for (const b of c.books) {
  books++;
  if (b.code && !/^[a-l][ehus][a-z]{2}\d$/.test(b.code)) err('ncert.json', `class ${c.class} "${b.title}": odd code ${b.code}`);
  if (b.code && !(b.chapters > 0)) err('ncert.json', `class ${c.class} "${b.title}": chapters missing`);
}

console.log(`${files.length} exams · ${chapters} chapters · ${cards} cards · ${books} NCERT books`);
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log('All content valid.');

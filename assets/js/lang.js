// Shared logic for the language section: data loading, the lesson narration script,
// the 60-day challenge and per-browser language progress.
// Imported by the pages AND by scripts/elevenlabs.mjs, so nothing here may touch the DOM
// or localStorage at import time.

export const LANG_STORE_KEY = 'academy.lang.v1';
export const AUDIO_ROOT = 'assets/audio/lang';

// ---------- Data
const cache = new Map();
function load(path) {
  if (!cache.has(path)) cache.set(path, fetch(path).then(r => { if (!r.ok) throw new Error(`${path}: ${r.status}`); return r.json(); }));
  return cache.get(path);
}
export const loadLangCatalog = () => load('data/languages/catalog.json');
export const loadLanguage = id => load(`data/languages/${id}.json`);
export const loadAllLanguages = async cat => Object.fromEntries(await Promise.all(
  cat.categories.flatMap(c => c.languages).map(async id => [id, await loadLanguage(id).catch(() => null)])));
// Missing manifest just means no recorded audio yet: the player falls back to the device voice.
export const loadAudioManifest = () => load(`${AUDIO_ROOT}/manifest.json`).catch(() => ({ voice: null, clips: {} }));

export const allLanguageIds = cat => cat.categories.flatMap(c => c.languages);

// ---------- Narration script
// A lesson is a list of segments. Each spoken segment has a stable id; the ElevenLabs script
// records one mp3 per id and stores a hash of its text, so edited text never plays stale audio.
export function hashText(str) {
  let h = 0x811c9dc5;
  for (const ch of str) { h ^= ch.codePointAt(0); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(36);
}

const ordinal = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];

export function lessonSegments(cat, language, lessonId) {
  const li = cat.lessons.findIndex(l => l.id === lessonId);
  const meta = cat.lessons[li], lesson = language.lessons.find(l => l.id === lessonId);
  if (!meta || !lesson) return [];
  const host = cat.host.name, name = language.name;
  const segs = [];
  const en = (id, text, extra = {}) => segs.push({ id, kind: id.replace(/^p\d+-/, ''), voice: 'en', text, ...extra });

  en('intro', `${li === 0 ? `Hi, I'm ${host}. Welcome to ${name}! ` : `Welcome back! `}This is lesson ${ordinal[li]}: ${meta.title}. ${lesson.intro} Listen to each phrase, then say it out loud after me.`, { gesture: 'wave' });
  meta.phrases.forEach((p, i) => {
    const ph = lesson.phrases.find(x => x.key === p.key);
    if (!ph) return;
    const at = { phrase: i };
    en(`p${i}-cue`, `${i === 0 ? 'First' : i === meta.phrases.length - 1 ? 'And finally' : 'Next'}: ${p.en.replace(/ \/ /g, ', or, ')}`, { ...at, gesture: 'point' });
    segs.push({ id: `p${i}-say`, kind: 'say', voice: language.bcp47, text: ph.native, roman: ph.roman, ...at, gesture: 'point' });
    segs.push({ id: `p${i}-yourturn`, kind: 'yourturn', voice: null, text: 'Your turn. Say it out loud.', pauseMs: 2600, ...at });
    // The repeat replays the native recording, so it shares the say clip.
    segs.push({ id: `p${i}-again`, kind: 'say', voice: language.bcp47, text: ph.native, roman: ph.roman, audio: `p${i}-say`, ...at, gesture: 'point' });
    en(`p${i}-note`, ph.note, { ...at, gesture: 'explain' });
  });
  en('tip', `Here's a quick tip. ${lesson.tip}`, { gesture: 'explain' });
  en('outro', `Wonderful work! That's ${meta.title.toLowerCase()} in ${name}. Now take the quick check to lock it in.`, { gesture: 'wave' });
  return segs.map(s => ({ ...s, audio: s.audio || s.id, key: `${language.id}/${lessonId}/${s.audio || s.id}` }));
}

// Unique clips that need a recording (the repeat shares the say clip).
export function recordableSegments(cat, language, lessonId) {
  const seen = new Set();
  return lessonSegments(cat, language, lessonId).filter(s => s.voice && !seen.has(s.key) && seen.add(s.key))
    .map(s => ({ key: s.key, voice: s.voice, text: s.text, hash: hashText(`${s.voice}|${s.text}`), file: `${AUDIO_ROOT}/${s.key}.mp3` }));
}

// Returns the recorded clip URL for a segment, or null when none matches the current text.
export function clipFor(manifest, seg) {
  const c = manifest?.clips?.[seg.key];
  return c && c.hash === hashText(`${seg.voice}|${seg.text}`) ? `${AUDIO_ROOT}/${seg.key}.mp3` : null;
}

// ---------- Quiz: built from the lesson's own phrases so every language gets one automatically.
export function lessonQuiz(cat, language, lessonId, seed = Date.now()) {
  const meta = cat.lessons.find(l => l.id === lessonId), lesson = language.lessons.find(l => l.id === lessonId);
  let r = seed % 2147483647 || 1;
  const rand = () => (r = r * 16807 % 2147483647) / 2147483647;
  const shuffle = a => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const items = meta.phrases.map(p => ({ en: p.en, ...lesson.phrases.find(x => x.key === p.key) })).filter(p => p.native);
  return shuffle(items).slice(0, 4).map((p, n) => {
    const wrong = shuffle(items.filter(x => x.key !== p.key)).slice(0, 3);
    const forward = n % 2 === 0; // alternate: "what does X mean?" and "how do you say Y?"
    const opts = shuffle([p, ...wrong]);
    return forward
      ? { q: `What does “${p.native}” (${p.roman}) mean?`, options: opts.map(o => o.en), answer: opts.indexOf(p), phrase: p }
      : { q: `How do you say “${p.en}” in ${language.name}?`, options: opts.map(o => `${o.native} · ${o.roman}`), answer: opts.indexOf(p), phrase: p };
  });
}

// ---------- Progress + 60-day challenge (this browser only)
export const localDay = (d = new Date()) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const dayDiff = (a, b) => Math.round((new Date(b + 'T12:00') - new Date(a + 'T12:00')) / 86400000);

function emptyLang() { return { start: null, name: '', done: {} }; }
export const langStore = {
  read() { try { return { ...emptyLang(), ...JSON.parse(localStorage.getItem(LANG_STORE_KEY) || '{}') }; } catch { return emptyLang(); } },
  write(s) { try { localStorage.setItem(LANG_STORE_KEY, JSON.stringify(s)); } catch { /* private mode */ } },
  update(fn) { const s = this.read(); fn(s); this.write(s); return s; },
};

export function challengePlan(cat) {
  return allLanguageIds(cat).flatMap(lang => cat.lessons.map(l => ({ lang, lesson: l.id, key: `${lang}/${l.id}` })))
    .map((x, i) => ({ ...x, day: i + 1 }));
}

export function challengeStatus(cat, s = langStore.read(), now = localDay()) {
  const plan = challengePlan(cat);
  const total = plan.length;
  const unlocked = s.start ? Math.min(total, Math.max(1, dayDiff(s.start, now) + 1)) : 0;
  const days = plan.map(p => ({ ...p,
    state: s.done[p.key] ? 'done' : !s.start ? 'locked' : p.day < unlocked ? 'missed' : p.day === unlocked ? 'today' : 'locked' }));
  const doneCount = days.filter(d => d.state === 'done').length;
  // Streak = consecutive calendar days (ending today or yesterday) with at least one lesson finished.
  const active = new Set(Object.values(s.done).map(d => d.day));
  let streak = 0; const d = new Date();
  if (!active.has(localDay(d))) d.setDate(d.getDate() - 1);
  while (active.has(localDay(d))) { streak++; d.setDate(d.getDate() - 1); }
  const next = days.find(x => x.state === 'missed') || days.find(x => x.state === 'today') || days.find(x => x.state !== 'done');
  return { started: !!s.start, start: s.start, total, unlocked, days, doneCount, streak, next, finished: doneCount === total };
}

export function markLessonDone(key, score, total) {
  return langStore.update(s => {
    const prev = s.done[key];
    s.done[key] = { at: Date.now(), day: prev?.day || localDay(), score: prev && prev.score > score ? prev.score : score, total };
  });
}

export const lessonHref = (lang, lesson) => `lesson.html?lang=${encodeURIComponent(lang)}&l=${encodeURIComponent(lesson)}`;

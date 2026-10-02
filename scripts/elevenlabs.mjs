// Records every language-lesson clip with ElevenLabs and writes assets/audio/lang/manifest.json.
// The lesson player uses a clip only when the manifest hash matches the current text, so editing
// a phrase falls back to the device voice until you re-run this script.
//
//   ELEVENLABS_API_KEY=... npm run voices                      # record everything missing or changed
//   ELEVENLABS_API_KEY=... npm run voices -- --lang tamil      # one language
//   npm run voices -- --dry-run                                # list what would be recorded (no key needed)
//   npm run voices -- --export                                 # write audio-script.csv for manual recording in the ElevenLabs app
//   npm run voices -- --scan                                   # you downloaded mp3s by hand: rebuild the manifest from files on disk
//
// Env: ELEVENLABS_VOICE_ID (default "Rachel", a premade female voice: pick Meera's voice in the
// Voice Library and paste its id), ELEVENLABS_MODEL (default eleven_v3, which covers Bengali, Kannada,
// Malayalam, Tamil and Telugu as well as the five international languages).
import fs from 'node:fs/promises';
import path from 'node:path';
import { recordableSegments, AUDIO_ROOT } from '../assets/js/lang.js';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const args = process.argv.slice(2);
const flag = f => args.includes(f);
const opt = f => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : null; };

const KEY = process.env.ELEVENLABS_API_KEY;
const VOICE = process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM';
const MODEL = process.env.ELEVENLABS_MODEL || 'eleven_v3';
const readJSON = async p => JSON.parse(await fs.readFile(path.join(ROOT, p), 'utf8'));

const cat = await readJSON('data/languages/catalog.json');
const ids = cat.categories.flatMap(c => c.languages).filter(id => !opt('--lang') || id === opt('--lang'));
const clips = [];
for (const id of ids) {
  const lang = await readJSON(`data/languages/${id}.json`);
  for (const l of cat.lessons) clips.push(...recordableSegments(cat, lang, l.id));
}

const manifestPath = path.join(ROOT, AUDIO_ROOT, 'manifest.json');
const manifest = await fs.readFile(manifestPath, 'utf8').then(JSON.parse).catch(() => ({ voice: null, model: null, clips: {} }));
const exists = p => fs.access(path.join(ROOT, p)).then(() => true, () => false);
const saveManifest = async () => {
  await fs.mkdir(path.dirname(manifestPath), { recursive: true });
  manifest.clips = Object.fromEntries(Object.entries(manifest.clips).sort(([a], [b]) => a.localeCompare(b)));
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 1) + '\n');
};

if (flag('--export')) {
  const csv = ['key,file,language,text', ...clips.map(c => [c.key, c.file, c.voice, c.text].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))];
  await fs.writeFile(path.join(ROOT, 'audio-script.csv'), csv.join('\n') + '\n');
  console.log(`Wrote audio-script.csv with ${clips.length} clips. Save each recording as the "file" path, then run: npm run voices -- --scan`);
  process.exit(0);
}

if (flag('--scan')) {
  let found = 0;
  for (const c of clips) if (await exists(c.file)) { manifest.clips[c.key] = { hash: c.hash }; found++; }
  manifest.voice ||= 'manual';
  await saveManifest();
  console.log(`Manifest updated: ${found}/${clips.length} clips found on disk.`);
  process.exit(0);
}

const todo = [];
for (const c of clips) if (manifest.clips[c.key]?.hash !== c.hash || !(await exists(c.file))) todo.push(c);
console.log(`${clips.length} clips across ${ids.length} language(s); ${todo.length} to record.`);
if (flag('--dry-run') || !todo.length) { todo.slice(0, 20).forEach(c => console.log(`  ${c.key}  [${c.voice}] ${c.text.slice(0, 70)}`)); process.exit(0); }
if (!KEY) { console.error('Set ELEVENLABS_API_KEY (https://elevenlabs.io/app/settings/api-keys).'); process.exit(1); }

async function tts(text, attempt = 1) {
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE}?output_format=mp3_44100_128`, {
    method: 'POST',
    headers: { 'xi-api-key': KEY, 'content-type': 'application/json', accept: 'audio/mpeg' },
    body: JSON.stringify({ text, model_id: MODEL, voice_settings: { stability: 0.5, similarity_boost: 0.8, style: 0.2, use_speaker_boost: true } }),
  });
  if (res.status === 429 && attempt < 5) { await new Promise(r => setTimeout(r, 2000 * attempt)); return tts(text, attempt + 1); }
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return Buffer.from(await res.arrayBuffer());
}

let n = 0, failed = 0;
for (const c of todo) {
  try {
    const mp3 = await tts(c.text);
    await fs.mkdir(path.dirname(path.join(ROOT, c.file)), { recursive: true });
    await fs.writeFile(path.join(ROOT, c.file), mp3);
    manifest.clips[c.key] = { hash: c.hash };
    manifest.voice = VOICE; manifest.model = MODEL;
    console.log(`[${++n}/${todo.length}] ${c.key}`);
    if (n % 20 === 0) await saveManifest(); // keep progress if the run is interrupted
  } catch (e) {
    failed++;
    console.error(`FAILED ${c.key}: ${e.message}`);
  }
}
await saveManifest();
console.log(`Done: ${n} recorded, ${failed} failed. Commit assets/audio/lang/ to publish them.`);
if (failed) process.exit(1);

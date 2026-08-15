# DEKH LENGE WO — production guide

Everything in this folder was generated from two Python scripts. No samples, no
plugins, no DAW. You can regenerate or modify all of it.

```bash
pip install numpy lameenc pillow imageio-ffmpeg
python3 make_beat.py      # -> dekh-lenge-wo-beat.wav / .mp3   (4:35)
python3 make_video.py     # -> dekh-lenge-wo-lyric-video.mp4   (1280x720, 24fps)
```

| File | What it is |
|---|---|
| `DEKH-LENGE-WO-lyrics.md` | Lyric sheet + flow/recording notes |
| `make_beat.py` | Synthesises the instrumental from scratch |
| `make_video.py` | Renders the beat-reactive lyric video |
| `dekh-lenge-wo-beat.mp3` | The beat, 192 kbps |
| `dekh-lenge-wo-beat.wav` | The beat, 16-bit/44.1k — **use this one to record over** |
| `dekh-lenge-wo-lyric-video.mp4` | Lyric video (instrumental audio) |

---

## 1. The beat — what's actually in it

**88 BPM · C# minor · 4:35 · 100 bars**

Everything is synthesised in `make_beat.py`:

| Element | How it's made | Where to tweak |
|---|---|---|
| Kick | Sine sweeping 130 Hz → 47 Hz + a 4 ms noise click | `kick()` |
| Sub bass | Pure sine + sub-octave sine, portamento slides between notes | `sub808()` |
| Bass definition | Sine + 2 quiet harmonics an octave up — no saw, no square | `bass_mid()` |
| Snare | 185 + 331 Hz tone layer + band-passed noise | `snare()` |
| Clap | 4 noise bursts spaced 11 ms apart (that's what makes it a *clap*) | `clap()` |
| Hats | Noise ring-modulated at 6.4 kHz, high-passed at 7.2 kHz | `hat()` |
| Lead / arp | Additive synthesis, 5 harmonics with per-harmonic decay | `pluck()` |
| Pad | 3 detuned saws per note, low-passed to 1.5 kHz | `pad()` |
| Percussion | Pitch-dropping sine + noise transient (tabla-ish) | `tabla()` |

**Chord loop (4 bars):** `C#m | C#m | A | B` — bass roots `C#2 · C#2 · A1 · B1`.

**Drum grid** (16 steps per bar, `x` = hit):

```
        1 e & a 2 e & a 3 e & a 4 e & a
Kick    x . . . . . x . . . x . . . . .      (last bar of every 4 adds . . x . and . . . x)
Snare   . . . . x . . . . . . . x . . .
Clap    . . . . x . . . . . . . x . . .
Hats    x x x x x x x x x x x x x x x x      (+ 32nd rolls on step 8 & 16, triplets every other bar)
Perc    . . . x . . . x . . . x . . . x
```

### The bassline

The bass is three layers playing one written line, not a held root note:

```
        1 e & a 2 e & a 3 e & a 4 e & a
C#m     C#. . . . . C#. . . G#. . . B~      ~ = slide into the next note
C#m     C#. . . . G#~ . C#. . . . E . .
A       A . . . . . A . . . E . . . C#~
B       B . . . . B . . . F#. . . C#~ .
```

1. **Sub (below 200 Hz)** — a pure sine at the root plus a **sub-octave sine**
   underneath it (C#2 at 69 Hz + C#1 at 34.6 Hz). This is the weight you feel.
2. **Warmth (200–900 Hz, at 11%)** — a lightly driven copy, band-limited and kept
   quiet. Just enough that the line is traceable on a phone.
3. **Definition (`bass_mid`, ~110–170 Hz)** — sine plus two quiet harmonics an
   octave above the sub.

**This bass is deliberately clean, not a trap 808.** No saw, no square, no hard
drive anywhere in the chain — those are what make a bass growl and buzz. If you
ever *do* want the gritty sound, raise the `sat()` drive in `sub808()` from 0.55
and push `sub_harm` above 0.11; those two numbers are the entire difference.
Measured on the current render, the bass has **0.0% of its energy above 600 Hz**
and 59% below 90 Hz.

Slides (`from_note=`) are the signature 808 move — the pitch glides from the
previous note over ~110 ms instead of restarting. Edit `BASS_PATTERN` to rewrite
the line: `(16th step, MIDI note, length in 16ths, slide from previous)`.

Two more production details that matter more than they sound like they should:

- **Sidechain.** The 808 and the music duck ~45% for 180 ms every kick. Without
  this the sub and the kick fight and the low end turns to mud. See `duck` in `build()`.
- **Low-end balance.** The first render of this beat had 90% of its energy below
  120 Hz — it sounded huge in headphones and empty everywhere else. After the
  three-layer bass split it sits at ~71% below 120 Hz, with real content at
  120–500 Hz where small speakers live.

The mix sits at **−15.9 dBFS RMS with a −1 dBFS peak**. That headroom is
deliberate — it's where your vocal goes. Don't normalise the beat louder before
you record.

### Making it yours

```python
BPM = 88.0                      # 75-80 = heavier, 95-100 = more aggressive
CHORDS = [[61,64,68], ...]      # MIDI notes; 61 = C#4
BASS   = [37, 37, 33, 35]       # 808 root per bar
KICK_A = [0, 6, 10]             # kick positions in 16ths
LEAD   = [(0.0, 68, 1.0), ...]  # (beat offset, MIDI note, length in beats)
```

Change `BASS`/`CHORDS` together — the 808 root should always be the chord root,
or it'll clash. To transpose the whole song, add the same number to every value
in `CHORDS`, `BASS` and `LEAD` (+2 = D minor, −1 = C minor).

---

## 2. Recording your vocal over it

1. Open **any** DAW — BandLab (free, browser), Audacity (free), FL Studio,
   Ableton, Logic, Reaper. Set the project tempo to **88 BPM**.
2. Import `dekh-lenge-wo-beat.wav` at bar 1, position 0.
3. Record in 4-bar chunks. Use the cue sheet:

```
Intro    0:00.0     Hook     2:32.7
Hook     0:21.8     Bridge   2:54.5
Verse 1  0:43.6     Verse 3  3:16.4
Hook     1:27.3     Hook     4:00.0
Verse 2  1:49.1     Outro    4:21.8
```

4. Vocal chain, in this order:
   - **High-pass at 90 Hz** — the 808 owns everything below that.
   - **De-ess** around 6–8 kHz if your "s" sounds spit.
   - **Compress** 3:1, fast attack, ~6 dB gain reduction. Rap needs to sit *still*.
   - **Dip the beat** 2–3 dB around 1–3 kHz where your voice lives, instead of
     turning the vocal up. Fixes 90% of "my vocal is buried" problems.
   - **Short reverb** (0.8 s) at ~12% wet on the main; heavier on ad-libs only.
   - **Slap delay** 1/8th note, ~15% wet, only on the hook.
5. Vocal should land around **−6 to −8 dBFS peak** over the beat. Then master the
   whole thing to −1 dBFS peak / around −9 to −11 dBFS RMS for streaming.

---

## 3. About cloning your voice

I could not do this, and I want to be exact about why rather than leave you
guessing:

- **There is no voice-cloning or text-to-speech model in this environment.** Not
  a permissions problem, not a "didn't try" problem — the capability isn't
  installed here, so no synthetic vocal of any kind can be produced.
- **I also can't reach the Liberated Electro Soul channel**, or any Hamrah Beats
  reference. YouTube is blocked outright by this environment's network proxy
  (`EGRESS_BLOCKED`), there's no audio downloader here, and I can't listen to
  audio in any case. So nothing in this beat or these lyrics is modelled on those
  tracks — all of it was written from scratch. I also couldn't analyse your
  register or delivery to pick the key. If C# minor sits wrong when you try
  rapping over it, transposing is a one-line change — see §1 above.

**To get the style matched:** paste the lyrics of one of your tracks as *text*,
or describe the flow (syllables per bar, rhyme scheme, how much Hindi vs English,
subjects you write about). Text I can work from — audio and links I cannot.

**To clone your own voice yourself** — this is genuinely 20 minutes of work:

1. **Record 3–10 minutes of clean reference audio.** Speaking, not singing.
   Quiet room, one mic, no reverb, no music behind it. This is the single biggest
   quality factor — a clean 3 minutes beats a noisy 30.
2. **Pick a tool** — ElevenLabs (instant cloning from a short sample; the most
   accurate for speech today), Kits.AI or Voicify (built specifically for *singing*
   / rap voice models, which is what you actually want here), or RVC / so-vits-svc
   if you want to run it locally and free on your own GPU.
3. **For rap specifically, use a voice *conversion* workflow, not text-to-speech.**
   Rap the verse yourself — even badly, even flat — then convert your take
   through the model. TTS will not give you the timing, the breath or the
   attitude; conversion keeps your performance and only changes the timbre.
   Kits.AI and RVC both work this way.
4. Bring the converted vocal back in over `dekh-lenge-wo-beat.wav` and mix it
   with the chain in §2.

One thing worth saying: your own voice on this, unprocessed, will almost
certainly hit harder than a cloned one. The lyric is about *your* struggle — the
cracks in a real take are the point.

---

## 4. The lyric video

`make_video.py` renders 1280×720 @ 24 fps and muxes the audio in one pass. It is
genuinely reactive to the audio, not faked to a timer:

- The audio is FFT-split into a **sub band (<130 Hz)** and a **high band (>4 kHz)**,
  then RMS'd per video frame.
- Sub envelope → the ember glow behind the text, the white flash, and a 3-4 px
  vertical **screen shake on every kick**.
- High envelope → **film grain** intensity, so the grain crawls with the hi-hats.
- Every lyric line hits with a **7 px RGB split** (red shifted one way, blue the
  other) that decays over 180 ms.
- 70 embers drift upward continuously; scanlines every 3rd row; heavy vignette on
  the background only — the text sits *on top* of it so it stays crisp.

Lyrics are timed **one line per bar** (2.727 s each), which is exactly how the
song is written. Edit the `INTRO` / `HOOK` / `VERSE1` … lists at the top of the
file — `**word**` renders that word in amber.

```bash
PREVIEW_START=200 PREVIEW_FRAMES=48 python3 make_video.py   # 2-second test render
```

**For a vertical Reels/Shorts cut:** set `W, H = 720, 1280` and drop the font
sizes in `make_cards()` from 76/58 to about 56/44.

**Once your vocal is done:** replace `dekh-lenge-wo-beat.wav` with your final
mixed track (same filename, same length) and re-run `make_video.py`. The glow,
shake and grain will re-analyse and lock to your vocal mix automatically.

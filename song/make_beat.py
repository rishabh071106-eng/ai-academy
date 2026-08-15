#!/usr/bin/env python3
"""
DEKH LENGE WO - beat generator.

Synthesises the full instrumental from scratch (no samples, no libraries beyond
numpy) and writes a 44.1kHz stereo WAV + MP3.

    pip install numpy lameenc
    python3 make_beat.py

Key: C# minor.  BPM: 88.  Arrangement matches DEKH-LENGE-WO-lyrics.md bar for bar.
"""

import struct
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 88.0
BEAT = 60.0 / BPM          # 0.6818 s
BAR = 4 * BEAT             # 2.7273 s

OUT = Path(__file__).parent


# ---------------------------------------------------------------- utilities

def midi(n):
    """MIDI note number -> Hz."""
    return 440.0 * 2 ** ((n - 69) / 12.0)


def env_ad(n, attack, decay, curve=4.0):
    """Attack/decay envelope, exponential release."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    d = np.exp(-t / max(decay, 1e-6) * curve)
    return a * d


def fft_filter(x, low=None, high=None, order=3):
    """Zero-phase Butterworth-shaped filtering. Cheap and good enough for synthesis."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    mask = np.ones_like(f)
    with np.errstate(divide="ignore", invalid="ignore"):
        if low is not None:      # low-pass at `low`
            mask *= 1.0 / np.sqrt(1.0 + (f / low) ** (2 * order))
        if high is not None:     # high-pass at `high`
            r = np.where(f > 0, high / np.maximum(f, 1e-9), 1e9)
            mask *= 1.0 / np.sqrt(1.0 + r ** (2 * order))
    return np.fft.irfft(spec * mask, n)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def sat(x, drive=1.0):
    """Soft saturation - adds the harmonics that make sub bass audible on phones."""
    return np.tanh(x * drive) / np.tanh(drive)


# ---------------------------------------------------------------- instruments

def kick(dur=0.55, punch=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # pitch sweep 130Hz -> 47Hz
    f = 47 + 83 * np.exp(-t * 42)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.001, 0.16, 3.2)
    click = noise(n, 7) * env_ad(n, 0.0002, 0.004, 6) * 0.35
    click = fft_filter(click, high=1200)
    return sat(body * 1.15 + click * punch, 1.6) * 0.9


def sub808(note, dur, glide=0.045, from_note=None):
    """808 with a pitch glide into the root and tape-ish saturation.

    from_note gives a true portamento slide up/down from the previous note -
    the signature 808 move. Without it the glide is just a short drop into pitch.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = midi(note)
    if from_note is not None:
        # slide across ~110ms from the previous note's pitch
        f = f0 * (midi(from_note) / f0) ** np.exp(-t / 0.11)
    else:
        f = f0 * (1 + 0.55 * np.exp(-t / glide))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    e = env_ad(n, 0.006, dur * 0.42, 2.6)
    # short fade-out so notes never click when they get cut off
    fade = int(0.02 * SR)
    e[-fade:] *= np.linspace(1, 0, fade)
    return sat(x * e, 2.2) * 0.60


def bass_mid(note, dur, gain=1.0):
    """Warm mid-bass an octave above the 808 (~110-170 Hz).

    This is the layer you actually *hear* as "the bassline" on laptop speakers,
    earbuds and phone speakers - the sub only carries the weight underneath it.
    Saw + square through a resonant-ish low-pass, plucked envelope.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(note + 12)
    ph = f * t
    saw = 2 * (ph % 1.0) - 1.0
    sq = np.sign(np.sin(2 * np.pi * ph))
    x = 0.72 * saw + 0.28 * sq
    x = fft_filter(x, low=f * 7.0, high=70)
    e = env_ad(n, 0.005, dur * 0.36, 2.2)
    fade = min(int(0.015 * SR), n)
    e[-fade:] *= np.linspace(1, 0, fade)
    return sat(x * e, 1.9) * 0.115 * gain


def snare(dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 185 * t) + 0.6 * np.sin(2 * np.pi * 331 * t))
    tone *= env_ad(n, 0.0005, 0.045, 4)
    nz = fft_filter(noise(n, 11), high=900, low=9000) * env_ad(n, 0.0005, 0.075, 3)
    return (tone * 0.45 + nz * 0.95) * 0.80


def clap(dur=0.4):
    n = int(dur * SR)
    out = np.zeros(n)
    for i, off in enumerate((0.0, 0.011, 0.021, 0.030)):
        s = int(off * SR)
        seg = fft_filter(noise(n - s, 21 + i), high=1100, low=7500)
        out[s:] += seg * env_ad(n - s, 0.0004, 0.012 if i < 3 else 0.13, 4)
    return out * 0.66


def hat(open_=False, seed=3):
    dur = 0.28 if open_ else 0.06
    n = int(dur * SR)
    nz = noise(n, seed)
    # ring modulate for a metallic edge
    t = np.arange(n) / SR
    metal = np.sign(np.sin(2 * np.pi * 6400 * t)) * 0.3 + 1.0
    x = fft_filter(nz * metal, high=7200)
    return x * env_ad(n, 0.0003, 0.09 if open_ else 0.012, 4) * (0.30 if open_ else 0.38)


def pluck(note, dur, gain=1.0):
    """Bright plucked lead - santoor/koto flavoured, the melodic hook of the beat."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(note)
    x = np.zeros(n)
    for h, amp, dec in ((1, 1.0, 5.0), (2, 0.42, 7.5), (3, 0.22, 10.0),
                        (4, 0.12, 13.0), (6, 0.06, 16.0)):
        x += amp * np.sin(2 * np.pi * f * h * t + h) * np.exp(-t * dec)
    x *= env_ad(n, 0.002, dur * 0.5, 1.0)
    return x * 0.32 * gain


def pad(notes, dur):
    """Detuned saw stack, filtered dark. Sits under everything like fog."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for note in notes:
        f = midi(note)
        for det in (-0.14, 0.0, 0.13):
            ph = 2 * np.pi * (f + det) * t
            x += (2 * ((ph / (2 * np.pi)) % 1.0) - 1.0)   # saw
    x = fft_filter(x, low=1500, high=110)
    a = int(0.35 * SR)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-a:] *= np.linspace(1, 0, a) ** 2
    return x * e * 0.052


def tabla(dur=0.22, note=64):
    """Short tuned percussion hit for the off-beats - the desi flavour."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(note) * (1 + 1.8 * np.exp(-t * 120))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.0005, 0.035, 4)
    x += fft_filter(noise(n, 33), high=2500) * env_ad(n, 0.0003, 0.008, 5) * 0.4
    return x * 0.40


def crash(dur=1.8):
    n = int(dur * SR)
    x = fft_filter(noise(n, 91), high=3800)
    return x * env_ad(n, 0.001, 0.45, 2.2) * 0.16


def riser(dur):
    """White-noise sweep into the drop."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = noise(n, 55)
    # step the filter up in 24 chunks (cheap rising sweep)
    out = np.zeros(n)
    chunks = 24
    for i in range(chunks):
        a, b = i * n // chunks, (i + 1) * n // chunks
        out[a:b] = fft_filter(x[a:b], high=300 + 5200 * (i / chunks) ** 2)
    return out * (t ** 2.5) * 0.16


# ---------------------------------------------------------------- arrangement

# 4-bar chord loop: C#m | C#m | A | B   (C# natural minor)
CHORDS = [
    [61, 64, 68],   # C#m  (C#4 E4 G#4)
    [61, 64, 68],
    [57, 61, 64],   # A    (A3 C#4 E4)
    [59, 63, 66],   # B    (B3 D#4 F#4)
]
BASS = [37, 37, 33, 35]      # C#2, C#2, A1, B1  (root of each bar)

# The actual bassline. Per chord-loop slot: (16th step, MIDI note, length in
# 16ths, slide-from-previous-note). Movement + slides are what make a bassline
# a bassline instead of a held root note.
BASS_PATTERN = {
    0: [(0, 37, 6, False), (6, 37, 3, False), (10, 44, 3, False), (14, 35, 2, True)],
    1: [(0, 37, 5, False), (5, 44, 2, True), (8, 37, 4, False), (13, 40, 3, False)],
    2: [(0, 33, 6, False), (6, 33, 3, False), (10, 40, 3, False), (14, 37, 2, True)],
    3: [(0, 35, 5, False), (5, 35, 3, False), (9, 42, 3, False), (13, 37, 3, True)],
}

# lead motif over the 4-bar loop: (beat offset, midi note, beats long)
LEAD = [
    (0.0, 68, 1.0), (1.0, 71, 0.5), (1.5, 73, 1.5), (3.5, 71, 0.5),
    (4.0, 71, 1.0), (5.0, 68, 1.0), (6.0, 64, 1.5), (7.5, 66, 0.5),
    (8.0, 69, 1.0), (9.0, 73, 1.0), (10.0, 71, 1.5), (11.5, 69, 0.5),
    (12.0, 71, 1.0), (13.0, 75, 1.0), (14.0, 73, 2.0),
]

# kick pattern in 16ths (0-15 per bar)
KICK_A = [0, 6, 10]
KICK_B = [0, 3, 6, 10, 14]
SNARE_16 = [4, 12]

SECTIONS = [
    # (name, bars, drums, hats, sub, lead, arp, pad, perc, halftime)
    ("Intro",   8,  False, True,  False, True,  True,  True,  False, False),
    ("Hook",    8,  True,  True,  True,  True,  True,  True,  True,  False),
    ("Verse 1", 16, True,  True,  True,  False, True,  False, False, False),
    ("Hook",    8,  True,  True,  True,  True,  True,  True,  True,  False),
    ("Verse 2", 16, True,  True,  True,  False, True,  True,  True,  False),
    ("Hook",    8,  True,  True,  True,  True,  True,  True,  True,  False),
    ("Bridge",  8,  False, False, True,  True,  False, True,  False, True),
    ("Verse 3", 16, True,  True,  True,  False, True,  True,  True,  False),
    ("Hook",    8,  True,  True,  True,  True,  True,  True,  True,  False),
    ("Outro",   4,  False, True,  False, True,  True,  True,  False, False),
]


def build():
    total_bars = sum(s[1] for s in SECTIONS)
    n = int((total_bars * BAR + 3.0) * SR)
    drums = np.zeros(n)
    bass = np.zeros(n)
    bassmid = np.zeros(n)
    music = np.zeros(n)
    fx = np.zeros(n)
    rng = np.random.default_rng(2024)

    def put(buf, sample, at, gain=1.0):
        i = int(at * SR)
        end = min(i + len(sample), len(buf))
        if i < len(buf):
            buf[i:end] += sample[:end - i] * gain

    hat_c = hat(False)
    hat_o = hat(True)
    kick_s = kick()
    snare_s = snare()
    clap_s = clap()

    bar_cursor = 0
    timeline = []

    for (name, bars, d_on, h_on, s_on, l_on, arp_on, pad_on, perc_on, half) in SECTIONS:
        timeline.append((name, bar_cursor * BAR, bars))
        for b in range(bars):
            gb = bar_cursor + b               # global bar index
            t0 = gb * BAR
            slot = gb % 4                     # position in the 4-bar chord loop
            chord = CHORDS[slot]
            root = BASS[slot]
            last_bar = (b == bars - 1)

            # ---- drums
            if d_on:
                pat = KICK_B if (b % 4 == 3) else KICK_A
                for s in pat:
                    put(drums, kick_s, t0 + s * BEAT / 4)
                for s in SNARE_16:
                    put(drums, snare_s, t0 + s * BEAT / 4, 0.9)
                    put(drums, clap_s, t0 + s * BEAT / 4, 0.8)
                if last_bar:                                   # fill
                    for s in (13, 14, 15):
                        put(drums, snare_s, t0 + s * BEAT / 4, 0.35 + 0.2 * (s - 13))

            if h_on:
                step = BEAT / 4
                for s in range(16):
                    if half and s % 4:
                        continue
                    g = 1.0 if s % 4 == 0 else (0.62 if s % 2 == 0 else 0.45)
                    g *= 0.85 + 0.3 * rng.random()
                    put(drums, hat_c, t0 + s * step, g)
                    # triplet / 32nd rolls - this is the "frequent rhythm"
                    if not half and s in (7, 15) and (b % 2 == 1):
                        for k in range(1, 3):
                            put(drums, hat_c, t0 + s * step + k * step / 3, 0.5)
                    if not half and s == 11 and (b % 4 == 3):
                        for k in range(1, 4):
                            put(drums, hat_c, t0 + s * step + k * step / 4, 0.42)
                put(drums, hat_o, t0 + 6 * step, 0.9)
                put(drums, hat_o, t0 + 14 * step, 0.8)

            if perc_on:
                for s in (3, 7, 11, 15):
                    put(drums, tabla(note=64 if s % 8 == 3 else 69),
                        t0 + s * BEAT / 4, 0.55)

            # ---- 808 / bassline
            if s_on:
                if half:
                    put(bass, sub808(root - 12, BAR * 0.95), t0, 1.1)
                    put(bassmid, bass_mid(root, BAR * 0.92), t0, 0.75)
                else:
                    prev = None
                    for step, note, ln, slide in BASS_PATTERN[slot]:
                        at = t0 + step * BEAT / 4
                        ln_s = ln * BEAT / 4 * 1.06
                        put(bass, sub808(note, ln_s,
                                         from_note=prev if slide else None), at, 1.0)
                        put(bassmid, bass_mid(note, ln_s), at, 1.0)
                        prev = note

            # ---- pad
            if pad_on:
                put(music, pad(chord, BAR * 1.02), t0, 1.0 if not half else 1.5)

            # ---- arpeggio (constant 8th-note motion)
            if arp_on:
                arp = chord + [chord[0] + 12, chord[2], chord[1] + 12, chord[0] + 12]
                for s in range(8):
                    note = arp[s % len(arp)] + 12
                    put(music, pluck(note, BEAT * 0.6, 0.75), t0 + s * BEAT / 2,
                        0.9 if s % 2 == 0 else 0.6)

            # ---- lead motif (only on the 4-bar loop boundary)
            if l_on and slot == 0:
                for off, note, ln in LEAD:
                    put(music, pluck(note, ln * BEAT * 0.95, 1.25), t0 + off * BEAT)

            # ---- transitions
            if last_bar and name != "Outro":
                put(fx, riser(BAR * 0.95), t0)
            if b == 0 and d_on:
                put(fx, crash(), t0)

        bar_cursor += bars

    # ------------------------------------------------------------ mixdown
    # sidechain: duck the 808 + music every time the kick lands
    duck = np.ones(n)
    for gb in range(total_bars):
        t0 = gb * BAR
        for s in KICK_B:
            i = int((t0 + s * BEAT / 4) * SR)
            ln = int(0.18 * SR)
            if i + ln < n:
                duck[i:i + ln] = np.minimum(duck[i:i + ln],
                                            np.linspace(0.55, 1.0, ln) ** 0.6)
    bass *= duck
    bassmid *= duck
    music *= duck * 0.5 + 0.5

    # Split the 808: clean sub below 180Hz, plus a saturated harmonic layer in the
    # mids so the bassline is still audible on phone / laptop speakers.
    sub_clean = fft_filter(bass, low=180)
    sub_harm = fft_filter(sat(bass * 4.0, 3.5), high=220, low=3000) * 0.34
    mid_bass = fft_filter(bassmid, high=85, low=1600)
    bass = sub_clean * 1.10 + sub_harm + mid_bass * 1.25
    music = fft_filter(music, high=130)       # carve room for the 808
    drums = fft_filter(drums, high=35)

    mix = drums * 0.95 + bass * 1.0 + music * 1.0 + fx * 0.9

    # simple stereo: widen the music, keep drums/bass mono-centre
    delay = int(0.012 * SR)
    wide = np.concatenate([np.zeros(delay), music[:-delay]])
    left = drums * 0.95 + bass + music * 0.72 + wide * 0.34 + fx * 0.9
    right = drums * 0.95 + bass + music * 0.34 + wide * 0.72 + fx * 0.9

    stereo = np.stack([left, right], axis=1)
    stereo = sat(stereo * 0.55, 1.35)                       # glue / master drive
    stereo /= np.max(np.abs(stereo)) + 1e-9
    stereo *= 0.891                                          # ~ -1 dBFS

    # fade the tail
    f = int(2.0 * SR)
    stereo[-f:] *= np.linspace(1, 0, f)[:, None]
    return stereo, timeline


# ---------------------------------------------------------------- export

def write_wav(path, audio):
    data = np.clip(audio, -1, 1)
    pcm = (data * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def write_mp3(path, audio, bitrate=192):
    try:
        import lameenc
    except ImportError:
        print("  (skipping MP3 - `pip install lameenc`)")
        return False
    enc = lameenc.Encoder()
    enc.set_bit_rate(bitrate)
    enc.set_in_sample_rate(SR)
    enc.set_channels(2)
    enc.set_quality(2)
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    buf = enc.encode(pcm.tobytes()) + enc.flush()
    path.write_bytes(bytes(buf))
    return True


if __name__ == "__main__":
    print("Rendering 'Dekh Lenge Wo' at %d BPM ..." % BPM)
    audio, timeline = build()
    dur = len(audio) / SR
    write_wav(OUT / "dekh-lenge-wo-beat.wav", audio)
    write_mp3(OUT / "dekh-lenge-wo-beat.mp3", audio)
    print("\n  length: %d:%04.1f\n" % (int(dur // 60), dur % 60))
    print("  CUE SHEET")
    for name, start, bars in timeline:
        mm, ss = divmod(round(start, 1), 60)
        print("    %-8s  %2d:%04.1f   (%d bars)" % (name, int(mm), ss, bars))
    print("\n  wrote dekh-lenge-wo-beat.wav / .mp3")

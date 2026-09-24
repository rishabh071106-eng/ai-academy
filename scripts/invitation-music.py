"""
Wedding music for the invitation film, synthesised from scratch.

Shehnai lead over a dholak groove, with manjira, a tanpura bed and temple
bells — the mangal-dhwani sound of a north Indian wedding procession.
Bilawal (the major scale), 104 BPM, so it lifts rather than laments.
Nothing is sampled: every sound is generated here, so the track carries no
third-party rights.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

SR = 44100
DUR = 42.2
BPM = 104.0
BEAT = 60.0 / BPM
rng = np.random.default_rng(20261129)

n_total = int(DUR * SR)
t_all = np.arange(n_total) / SR


def place(buf, sig, t0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0:
        return
    m = min(len(sig), len(buf) - i)
    buf[i:i + m] += sig[:m]


def env_ar(n, a, r, sus=1.0, curve=1.0):
    a, r = int(a * SR), int(r * SR)
    mid = max(0, n - a - r)
    return np.concatenate([np.linspace(0, 1, a, endpoint=False) ** curve,
                           np.full(mid, sus),
                           np.linspace(sus, 0, n - a - mid) ** 1.3])[:n]


# ── shehnai ───────────────────────────────────────────────────────────────
# A double reed: far brighter than a flute, with strong formant peaks that
# give it its nasal, carrying voice.
FORMANTS = [(1100.0, 700.0, 1.00), (2400.0, 900.0, 0.62), (3600.0, 1100.0, 0.30)]


def formant_gain(f):
    g = 0.0
    for fc, bw, amp in FORMANTS:
        g += amp / (1.0 + ((f - fc) / bw) ** 2)
    return g


def shehnai(f, dur, prev=None, grace=None):
    n = int(dur * SR)
    t = np.arange(n) / SR

    freq = np.full(n, float(f))
    if grace:                                    # murki: a quick flick off a neighbour
        g = min(n, int(0.055 * SR))
        freq[:g] = np.linspace(grace, f, g)
    elif prev:                                   # a short slur from the note before
        g = min(n, int(0.035 * SR))
        freq[:g] = np.linspace(prev, f, g)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.6 * t) * np.clip((t - 0.12) / 0.25, 0, 1)
    phase = 2 * np.pi * np.cumsum(freq * vib) / SR

    out = np.zeros(n)
    for k in range(1, 34):
        fk = f * k
        if fk > 12000:
            break
        amp = (1.0 / k ** 0.62) * (0.30 + formant_gain(fk))
        out += amp * np.sin(k * phase + rng.uniform(0, 0.6))

    reed = rng.normal(0, 1, n)
    reed = np.convolve(reed, np.ones(14) / 14, mode='same')      # keep it up in the reed band
    out += reed * 0.05 * np.max(np.abs(out))

    e = env_ar(n, 0.045, 0.085, sus=1.0, curve=0.75)
    e *= 1 - 0.07 * np.clip((t - 0.2) / 0.6, 0, 1)               # slight breath decay
    out *= e
    return out / (np.max(np.abs(out)) + 1e-9)


# ── dholak, manjira, bell ────────────────────────────────────────────────
def dholak_bass():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 132 * np.exp(-t * 22) + 74
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    thump = np.convolve(rng.normal(0, 1, n), np.ones(40) / 40, mode='same') * np.exp(-t * 46) * 0.5
    x = body + thump
    return x / (np.max(np.abs(x)) + 1e-9)


def dholak_tre():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    body = (np.sin(2 * np.pi * 372 * t) + 0.5 * np.sin(2 * np.pi * 560 * t)) * np.exp(-t * 21)
    click = np.convolve(rng.normal(0, 1, n), np.ones(5) / 5, mode='same') * np.exp(-t * 105) * 0.7
    x = body + click
    return x / (np.max(np.abs(x)) + 1e-9)


def manjira():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for r in (1.0, 1.62, 2.31, 3.17, 4.29, 5.71):
        x += np.sin(2 * np.pi * 2650 * r * t + rng.uniform(0, 6.3)) * np.exp(-t * (5 + 2.4 * r))
    x *= env_ar(n, 0.001, 0.06)
    return x / (np.max(np.abs(x)) + 1e-9)


def bell(f0=232.0, dur=6.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, a, dec in [(0.56, 1.0, .55), (1.0, .85, .62), (1.19, .55, .95), (1.71, .40, 1.3),
                          (2.0, .45, 1.05), (2.74, .25, 1.85), (3.0, .20, 2.1), (4.07, .11, 3.1)]:
        out += a * np.exp(-t * dec) * np.sin(2 * np.pi * f0 * ratio * t + rng.uniform(0, 6.3))
    out += np.exp(-t * 95) * rng.normal(0, 1, n) * 0.28
    out *= env_ar(n, 0.002, 0.4)
    return out / (np.max(np.abs(out)) + 1e-9)


BASS, TRE, MJ = dholak_bass(), dholak_tre(), manjira()

# ── the tune: Raga Bilawal, four sixteen-beat phrases ─────────────────────
SCALE = {'P.': 3/4, 'D.': 5/6, 'N.': 15/16, 'S': 1, 'R': 9/8, 'G': 5/4, 'M': 4/3,
         'P': 3/2, 'D': 5/3, 'N': 15/8, "S'": 2, "R'": 9/4, "G'": 5/2}
TONIC = 293.66          # Sa at D4 — shehnai sits bright

PHRASE = [
    # (note, beats, grace-note or None)
    ('S', 1, None), ('R', 1, None), ('G', 2, 'M'),
    ('G', 1, None), ('M', 1, None), ('G', 1, None), ('R', 1, None),
    ('S', 1, None), ('R', 1, None), ('G', 1, None), ('P', 1, 'M'),
    ('G', 2, None), ('R', 1, None), ('S', 1, None),

    ('P', 1, None), ('D', 1, None), ('N', 2, "S'"),
    ("S'", 2, None), ('N', 1, None), ('D', 1, None),
    ('P', 1, None), ('M', 1, None), ('G', 1, None), ('M', 1, None),
    ('P', 4, 'D'),

    ("S'", 1, None), ('N', 1, None), ('D', 1, None), ('P', 1, None),
    ('D', 1, None), ('N', 1, None), ("S'", 2, "R'"),
    ('N', 1, None), ('D', 1, None), ('P', 1, None), ('M', 1, None),
    ('G', 2, None), ('M', 2, None),

    ('P', 1, None), ('M', 1, None), ('G', 1, None), ('R', 1, None),
    ('G', 2, 'M'), ('R', 1, None), ('S', 1, None),
    ('R', 1, None), ('G', 1, None), ('R', 1, None), ('S', 1, None),
    ('S', 4, None),
]

MEL_START = 4 * BEAT            # the groove and tune come in together after a pickup

lead = np.zeros(n_total)
# free pickup flourish over the opening bell
t = 0.55
for nm, d in [('P.', .38), ('S', .34), ('R', .30), ('G', .55)]:
    f = TONIC * SCALE[nm]
    place(lead, shehnai(f, d + 0.16) * 0.8, t)
    t += d

t, prev = MEL_START, None
for nm, beats, grace in PHRASE:
    f = TONIC * SCALE[nm]
    gf = TONIC * SCALE[grace] if grace else None
    place(lead, shehnai(f, beats * BEAT + 0.10, prev, gf), t)
    prev = f
    t += beats * BEAT
MEL_END = t

# ── groove ───────────────────────────────────────────────────────────────
perc = np.zeros(n_total)
bars = int(np.ceil((DUR - MEL_START) / (4 * BEAT)))
KEHERWA = [(0.0, 'B', 1.0), (0.0, 'T', 0.5), (0.5, 'T', 0.6), (1.0, 'T', 0.75),
           (1.5, 'B', 0.8), (2.0, 'B', 0.95), (2.5, 'T', 0.6), (3.0, 'T', 0.8), (3.5, 'T', 0.55)]
for b in range(bars):
    bar_t = MEL_START + b * 4 * BEAT
    if bar_t > MEL_END + 0.1:
        break
    taper = 1.0 if bar_t < MEL_END - 4 * BEAT else 0.55      # ease off under the last note
    for off, kind, amp in KEHERWA:
        place(perc, (BASS if kind == 'B' else TRE) * amp * 0.9 * taper, bar_t + off * BEAT)
    for off in (0.0, 2.0):
        place(perc, MJ * 0.5 * taper, bar_t + off * BEAT)

# ── tanpura bed and bells ────────────────────────────────────────────────
def tanpura_string(f, dur=5.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 22):
        fk = f * k * (1 + 0.00018 * k * k)
        if fk > 9000:
            break
        amp = (1.0 / k ** 0.85) * (1.35 if 3 <= k <= 9 else 1.0)
        out += amp * np.exp(-t * (0.6 + 0.32 * k)) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.3))
    out *= env_ar(n, 0.004, 0.2, sus=0.9)
    return out / (np.max(np.abs(out)) + 1e-9)


SA = TONIC / 2
drone = np.zeros(n_total)
cycle = [(SA * 3 / 4, .55), (SA, .70), (SA, .60), (SA / 2, .78)]
strings = [(f, tanpura_string(f), g) for f, g in cycle]
t, k = 0.0, 0
while t < DUR:
    f, sig, g = strings[k % 4]
    place(drone, sig * g, t)
    t += 1.02
    k += 1

bells = np.zeros(n_total)
for t0, a in [(0.05, 1.0), (MEL_START + 16 * BEAT, .30), (MEL_START + 32 * BEAT, .30), (MEL_END - 0.3, .55)]:
    place(bells, bell() * a, t0)

# ── mix ──────────────────────────────────────────────────────────────────
def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def reverb_ir(dur=1.5, seed=7):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    ir = r.normal(0, 1, n) * np.exp(-tt * 4.2)
    ir[:int(0.010 * SR)] = 0
    return ir / np.sqrt(np.sum(ir ** 2))


dry = norm(lead) * 0.50 + norm(perc) * 0.32 + norm(MJ.sum() * 0 + drone) * 0.17 + norm(bells) * 0.24
wet_l = fftconvolve(dry, reverb_ir(seed=7))[:n_total]
wet_r = fftconvolve(dry, reverb_ir(seed=23))[:n_total]
left = norm(dry * 0.82 + norm(wet_l) * 0.18)
right = norm(dry * 0.82 + norm(wet_r) * 0.18)

env = np.clip(t_all / 0.5, 0, 1) * np.clip((DUR - t_all) / 2.0, 0, 1) ** 1.2
stereo = np.stack([left * env, right * env], axis=1)

# gentle saturation: the drum transients alone were holding the peak down and
# leaving the whole track quiet. A soft knee lifts the body without clipping.
DRIVE = 1.9
stereo = np.tanh(stereo * DRIVE) / np.tanh(DRIVE)
stereo = stereo / (np.max(np.abs(stereo)) + 1e-9) * 0.90

wavfile.write('music.wav', SR, (stereo * 32767).astype(np.int16))
print('music.wav  %.2fs  %.0f BPM  melody %.1f-%.1fs  peak %.3f  rms %.1f dBFS'
      % (DUR, BPM, MEL_START, MEL_END, np.max(np.abs(stereo)),
         20 * np.log10(np.sqrt(np.mean(stereo ** 2)))))

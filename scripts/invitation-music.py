"""
A devotional instrumental for the invitation film, synthesised from scratch:
a tanpura drone, temple bells and a bansuri-like melody in Raga Yaman.
Nothing here is sampled or copied — every sound is generated, so the track
carries no third-party rights.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

SR = 44100
DUR = 42.2                      # matches the film exactly
rng = np.random.default_rng(20261129)

n_total = int(DUR * SR)
t_all = np.arange(n_total) / SR


def place(buf, sig, t0):
    """Mix sig into buf starting at t0 seconds, clipping at the end."""
    i = int(t0 * SR)
    if i >= len(buf):
        return
    m = min(len(sig), len(buf) - i)
    buf[i:i + m] += sig[:m]


def adsr(n, a, d, s, r, sus=0.7):
    """Simple envelope; a/d/r in seconds, s the sustain level."""
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s_len = max(0, n - a - d - r)
    return np.concatenate([
        np.linspace(0, 1, a, endpoint=False) ** 1.4,
        np.linspace(1, sus, d, endpoint=False),
        np.full(s_len, sus),
        np.linspace(sus, 0, n - a - d - s_len) ** 1.2,
    ])[:n]


# ── tanpura ───────────────────────────────────────────────────────────────
# Additive, with the bright upper partials that give the jivari its shimmer.
def tanpura_string(f, dur=5.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 26):
        # slight inharmonicity, as on a real string
        fk = f * k * (1 + 0.00018 * k * k)
        if fk > 11000:
            break
        amp = 1.0 / (k ** 0.78)
        if 3 <= k <= 11:                      # the jivari buzz sits here
            amp *= 1.45
        decay = np.exp(-t * (0.55 + 0.30 * k))
        phase = rng.uniform(0, 2 * np.pi)
        out += amp * decay * np.sin(2 * np.pi * fk * t + phase)
    out *= adsr(n, 0.004, 0.05, 0.0, 0.2, sus=0.85)
    return out / (np.max(np.abs(out)) + 1e-9)


SA = 261.63 / 2                               # Sa at C3
drone = np.zeros(n_total)
# the classic tanpura cycle: Pa, Sa, Sa, Sa an octave below
cycle = [(SA * 3 / 4, 0.58), (SA, 0.72), (SA, 0.62), (SA / 2, 0.80)]
strings = [(f, tanpura_string(f), g) for f, g in cycle]
step, k = 0.94, 0
t = 0.0
while t < DUR:
    f, sig, gain = strings[k % len(strings)]
    place(drone, sig * gain, t)
    t += step
    k += 1

# ── temple bell ───────────────────────────────────────────────────────────
def bell(f0=232.0, dur=7.0, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    partials = [(0.56, 1.00, 0.55), (1.00, 0.85, 0.62), (1.19, 0.55, 0.95),
                (1.71, 0.40, 1.30), (2.00, 0.45, 1.05), (2.74, 0.25, 1.85),
                (3.00, 0.20, 2.10), (3.76, 0.14, 2.60), (5.07, 0.09, 3.30)]
    out = np.zeros(n)
    for ratio, a, dec in partials:
        out += a * np.exp(-t * dec) * np.sin(2 * np.pi * f0 * ratio * t + rng.uniform(0, 6.28))
    strike = np.exp(-t * 90) * rng.normal(0, 1, n) * 0.30   # the mallet itself
    out = out + strike
    out *= adsr(n, 0.002, 0.02, 0.0, 0.5, sus=0.9)
    return amp * out / (np.max(np.abs(out)) + 1e-9)


bells = np.zeros(n_total)
for t0, a in [(0.15, 1.00), (9.2, 0.42), (23.4, 0.38), (36.8, 0.46)]:
    place(bells, bell(amp=a), t0)

# ── bansuri, Raga Yaman ───────────────────────────────────────────────────
YAMAN = {'P.': 3 / 4, 'N.': 15 / 16, 'S': 1, 'R': 9 / 8, 'G': 5 / 4,
         'M': 45 / 32, 'P': 3 / 2, 'D': 27 / 16, 'N': 15 / 8, "S'": 2}
TONIC = 261.63

PHRASE = [
    (None, 3.0),
    ('P.', 1.6), ('N.', 1.2), ('S', 2.4), (None, 0.5),
    ('R', 1.2), ('G', 1.4), ('R', 0.8), ('S', 2.2), (None, 0.6),
    ('G', 1.2), ('M', 1.4), ('P', 2.4), (None, 0.5),
    ('M', 1.0), ('G', 1.2), ('R', 1.6), (None, 0.5),
    ('P', 1.4), ('D', 1.2), ('N', 1.6), ("S'", 2.6), (None, 0.6),
    ('N', 1.2), ('D', 1.2), ('P', 2.0), (None, 0.5),
    ('G', 1.4), ('R', 1.4), ('S', 2.4),
]


def flute(f, dur, prev_f=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # meend: glide up from the previous note over the first 90 ms
    freq = np.full(n, float(f))
    if prev_f:
        g = min(n, int(0.09 * SR))
        freq[:g] = np.linspace(prev_f, f, g)
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 4.8 * t) * np.clip((t - 0.25) / 0.5, 0, 1)
    phase = 2 * np.pi * np.cumsum(freq * vib) / SR
    tone = (np.sin(phase) + 0.30 * np.sin(2 * phase) + 0.14 * np.sin(3 * phase)
            + 0.05 * np.sin(4 * phase))
    breath = rng.normal(0, 1, n)
    breath = np.convolve(breath, np.ones(60) / 60, mode='same') * 0.16
    env = adsr(n, 0.13, 0.18, 0.0, 0.30, sus=0.80)
    return (tone + breath * env) * env


melody = np.zeros(n_total)
t, prev = 0.0, None
for name, dur in PHRASE:
    if name is None:
        t += dur
        prev = None
        continue
    f = TONIC * YAMAN[name]
    place(melody, flute(f, dur + 0.25, prev), t)
    prev = f
    t += dur

# ── reverb, mix ───────────────────────────────────────────────────────────
def reverb_ir(dur=2.4, seed=7):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    ir = r.normal(0, 1, n) * np.exp(-tt * 2.6)
    ir[:int(0.012 * SR)] = 0                      # pre-delay
    return ir / np.sqrt(np.sum(ir ** 2))


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


dry = norm(drone) * 0.26 + norm(bells) * 0.32 + norm(melody) * 0.48
wet_l = fftconvolve(dry, reverb_ir(seed=7))[:n_total]
wet_r = fftconvolve(dry, reverb_ir(seed=23))[:n_total]

left = norm(dry * 0.74 + norm(wet_l) * 0.26)
right = norm(dry * 0.74 + norm(wet_r) * 0.26)

fade_in = np.clip(t_all / 1.2, 0, 1)
fade_out = np.clip((DUR - t_all) / 2.6, 0, 1) ** 1.3
env = fade_in * fade_out
stereo = np.stack([left * env, right * env], axis=1) * 0.89

wavfile.write('music.wav', SR, (stereo * 32767).astype(np.int16))
peak = np.max(np.abs(stereo))
rms = np.sqrt(np.mean(stereo ** 2))
print('music.wav  %.2fs  peak %.3f  rms %.3f (%.1f dBFS)' % (DUR, peak, rms, 20 * np.log10(rms)))

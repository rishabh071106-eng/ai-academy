#!/usr/bin/env python3
"""
DEKH LENGE WO - lyric video renderer.

Renders a dark, beat-reactive lyric video and muxes it with the beat.
Everything is driven by the actual audio: the glow pulses on the sub-bass,
the frame shakes on the kick, the grain rides the hi-hats.

    pip install numpy pillow imageio-ffmpeg
    python3 make_beat.py && python3 make_video.py

Output: dekh-lenge-wo-lyric-video.mp4  (1280x720, 24 fps)
"""

import os
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg

HERE = Path(__file__).parent
AUDIO = HERE / "dekh-lenge-wo-beat.wav"
OUTPUT = HERE / "dekh-lenge-wo-lyric-video.mp4"

W, H = 1280, 720
FPS = 24
BPM = 88.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

FONT_DIR = Path("/mnt/skills/examples/canvas-design/canvas-fonts")
F_DISPLAY = FONT_DIR / "BigShoulders-Bold.ttf"
F_MONO = FONT_DIR / "GeistMono-Bold.ttf"

AMBER = (255, 176, 64)
WHITE = (243, 240, 236)
DIM = (120, 116, 112)


# ------------------------------------------------------------------ lyrics
# One line per bar. Empty string = instrumental bar. **word** = accent colour.

INTRO = [
    "",                                    # title card holds these two bars
    "",
    "Log kehte the...",
    '"Beta, kuch nahi hoga tera."',
    "Maine kaha — theek hai. Time lagega.",
    "Par jo hansa tha na us din...",
    "**dekh lega wo.**",
    "",
]

HOOK = [
    "Dekh lenge wo, dekh lenge wo,",
    'jo bole the "tu kuch nahi" — **dekh lenge wo.**',
    "Chal raha hoon dheere, par rukne ka nahi,",
    "naam likha hai upar, main **jhukne ka nahi.**",
    "Dekh lenge wo, dekh lenge wo,",
    "aaj nahi toh kal — par **dekh lenge wo.**",
    "Jis din mera pasina yeh **sona** banega,",
    "jo peeche hans raha tha — wo taali bajayega.",
]

VERSE1 = [
    "Subah paanch baje uthta, aankh mein neend adhoori,",
    "jeb mein kuch bhi nahi — bas ek **zid** thi poori.",
    'Maa poochti "khaya beta?" — main bolta tha "haan",',
    "jhooth tha wo, us raat khaali tha dukaan.",
    "Cycle ki chain tooti, aur raste the lambe,",
    'log kehte the "pagal", maine sapne the bandhe.',
    "Notebook ke corner pe likha tha ek **naam** —",
    '"ek din yeh poora sheher lega mera salaam."',
    "Har raat ek jung thi, har din ek trial,",
    "rejection ke emails, hazaaron ki file.",
    "Par haar nahi maani, main roz roz likhta,",
    "andhere ko cheer ke ek **raasta** nikalta.",
    "Ab dheere dheere chalta hoon, par manzil paas hai,",
    "jo kal tak sapna tha, aaj wo meri saans hai.",
    'Mat poochna ki "kaise" — bas dekhna ki **kahan**,',
    "zero se shuru kiya tha, ab likhta hoon jahan.",
]

VERSE2 = [
    "Pehli salary aayi, maa ke haath mein rakh di,",
    "aankh bhar aayi uski — samjho meri **jeet pakki.**",
    'Baap ne kandhe pe haath rakh ke bola "shabaash",',
    "us ek pal ne kar diya das saal ka dard **khalaas.**",
    "Par ruka nahi main, ye toh sirf pehla step tha,",
    "bhookh badh gayi meri, ab dil rakhta depth tha.",
    "Jin doston ne chhoda, unko bhi meri dua —",
    "unke jaane se hi toh mera **raasta** khula.",
    "Raat bhar padhta, aur subah ko kamata,",
    "do-do zindagi ek akela banda nibhata.",
    'Log poochte "sota kab hai?" — main hasta hoon,',
    '"neend baad mein le lunga, abhi main **rasta** hoon."',
    "Har thappad jo waqt ne mara, maine note kiya,",
    "har taane ko petrol banaya, phir throttle diya.",
    "Ab jab naam aata hai, mera sar uthta hai —",
    "aur wo chup ho jaata hai, jo zyada **bakta** hai.",
]

BRIDGE = [
    "Thoda thoda karke... sab mil jaayega,",
    "toota hua dil bhi ek din sil jaayega.",
    "Bas chalte rehna tu, ruk mat yahan —",
    "roshni wahin hai... jahan andhera ghana.",
    "(Thoda thoda karke...)",
    "(sab mil jaayega...)",
    "Saans le, aur phir se —",
    "**chal.**",
]

VERSE3 = [
    "Ab main double time pe, dil bhi hai beat pe,",
    "jo kuch bhi socha tha, sab aa gaya sheet pe.",
    "Likha, phir kaata, phir likha, phir jeeta,",
    "zindagi ne jitna toda, utna maine **seekha.**",
    "Chhoti si chhat thi, ab building khadi hai,",
    "ghadi thi nahi paas — ab keemti ghadi hai.",
    "Par ghamand zero, main wahi purana banda,",
    "jeb bhari hui hai, par dil wahi **diwana.**",
    "Bhai ko job dilayi, behen ki fees bhar di,",
    "maa ke ilaaj ka kharcha ab lagta nahi bhaari.",
    "Ye success nahi hai — ye sirf **sabr ka phal** hai,",
    "jo bota hai tu aaj, wahi **kaatega kal** hai.",
    "Toh jo bhi sun raha hai — bhai tu bhi mat ruk,",
    "andhere se mat dar, bas chalta reh chup-chup.",
    "Ek din wo aayega jab log tera naam lenge,",
    "aur jo aaj hans rahe hain — bas... **dekh lenge.**",
]

OUTRO = [
    "Kisi ko kuch prove nahi karna hai.",
    "Bas khud se kiya hua wada... poora karna hai.",
    "Baaki?",
    "**Baaki dekh lenge wo.**",
]

SECTIONS = [
    ("INTRO", INTRO), ("HOOK", HOOK), ("VERSE 1", VERSE1), ("HOOK", HOOK),
    ("VERSE 2", VERSE2), ("HOOK", HOOK), ("BRIDGE", BRIDGE), ("VERSE 3", VERSE3),
    ("HOOK", HOOK), ("OUTRO", OUTRO),
]


def build_cues():
    """Flatten sections into (start_time, end_time, section_name, text) cues."""
    cues, bar = [], 0
    for name, lines in SECTIONS:
        for text in lines:
            cues.append((bar * BAR, (bar + 1) * BAR, name, text))
            bar += 1
    return cues, bar


# ------------------------------------------------------------------ audio analysis

def analyse(path, n_frames):
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype="<i2").reshape(-1, 2).mean(1) / 32768.0

    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    sub = np.fft.irfft(spec * (f < 130), len(x))
    hi = np.fft.irfft(spec * (f > 4000), len(x))

    def frame_rms(sig):
        out = np.zeros(n_frames)
        win = int(sr / FPS)
        for i in range(n_frames):
            a = i * win
            seg = sig[a:a + win]
            out[i] = np.sqrt((seg ** 2).mean()) if len(seg) else 0.0
        return out / (out.max() + 1e-9)

    return frame_rms(sub), frame_rms(hi), len(x) / sr


# ------------------------------------------------------------------ text layer

def tokens(text):
    """Split '**bold**' markers into (word, is_accent) pairs."""
    out, accent = [], False
    for chunk in text.split("**"):
        if chunk:
            out += [(w, accent) for w in chunk.split(" ") if w]
        accent = not accent
    return out


def render_line(text, font, max_w):
    """Draw one lyric line (word-wrapped, centred) onto a transparent RGBA layer."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not text.strip():
        return layer
    d = ImageDraw.Draw(layer)
    quiet = text.strip().startswith("(")

    space = d.textlength(" ", font=font)
    rows, row, rw = [], [], 0.0
    for word, acc in tokens(text):
        ww = d.textlength(word, font=font)
        if row and rw + space + ww > max_w:
            rows.append((row, rw))
            row, rw = [], 0.0
        row.append((word, acc, ww))
        rw += ww + (space if len(row) > 1 else 0)
    if row:
        rows.append((row, rw))

    lh = font.size * 1.12
    y = H / 2 - (len(rows) - 1) * lh / 2 - font.size * 0.62
    for words, width in rows:
        x = (W - width) / 2
        for word, acc, ww in words:
            col = AMBER if acc else (DIM if quiet else WHITE)
            d.text((x, y), word, font=font, fill=col + (255,))
            x += ww + space
        y += lh
    return layer


def make_cards(cues):
    """Pre-render every lyric line once: text layer + its glow. Frames just blend."""
    font = ImageFont.truetype(str(F_DISPLAY), 76)
    font_sm = ImageFont.truetype(str(F_DISPLAY), 58)
    cards = []
    for _, _, _, text in cues:
        f = font_sm if len(text) > 46 else font
        layer = render_line(text, f, W - 190)
        arr = np.asarray(layer).astype(np.float32) / 255.0
        rgb = arr[..., :3] * arr[..., 3:4]
        glow = np.asarray(
            layer.filter(ImageFilter.GaussianBlur(19))
        ).astype(np.float32) / 255.0
        glow_rgb = glow[..., :3] * glow[..., 3:4]
        cards.append((rgb, glow_rgb))
    return cards


def title_card():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    big = ImageFont.truetype(str(F_DISPLAY), 150)
    sub = ImageFont.truetype(str(F_MONO), 21)
    t = "DEKH LENGE WO"
    tw = d.textlength(t, font=big)
    d.text(((W - tw) / 2, H / 2 - 118), t, font=big, fill=WHITE + (255,))
    s = "88 BPM   ·   C# MINOR"
    sw = d.textlength(s, font=sub)
    d.text(((W - sw) / 2, H / 2 + 52), s, font=sub, fill=AMBER + (210,))
    d.line((W / 2 - 190, H / 2 + 34, W / 2 + 190, H / 2 + 34), fill=AMBER + (110,), width=2)
    arr = np.asarray(layer).astype(np.float32) / 255.0
    glow = np.asarray(layer.filter(ImageFilter.GaussianBlur(26))).astype(np.float32) / 255.0
    return arr[..., :3] * arr[..., 3:4], glow[..., :3] * glow[..., 3:4]


def make_labels(names):
    """Pre-render each section label once - drawing text every frame is the
    single most expensive thing in the render loop."""
    f = ImageFont.truetype(str(F_MONO), 19)
    out = {}
    for name in set(names):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((58, 48), name, font=f, fill=AMBER + (190,))
        a = np.asarray(layer).astype(np.float32) / 255.0
        out[name] = (a[..., :3] * a[..., 3:4], a[..., 3:4])
    return out


def draw_progress(frame, progress):
    """Progress bar straight into the array - no PIL, no allocation."""
    y = H - 59
    frame[y:y + 2, 58:W - 58] = np.array([0.35, 0.33, 0.31], dtype=np.float32)
    end = 58 + int((W - 116) * max(0.0, min(1.0, progress)))
    if end > 58:
        frame[y:y + 2, 58:end] = np.array([1.0, 0.69, 0.25], dtype=np.float32)


# ------------------------------------------------------------------ render

def main():
    cues, total_bars = build_cues()
    duration = total_bars * BAR + 2.0
    n_frames = int(duration * FPS)
    print("Analysing audio ...")
    sub_env, hi_env, audio_len = analyse(AUDIO, n_frames)
    n_frames = min(n_frames, int(audio_len * FPS))
    preview = int(os.environ.get("PREVIEW_FRAMES", "0"))   # quick smoke-test render
    start_f = int(float(os.environ.get("PREVIEW_START", "0")) * FPS)
    if preview:
        n_frames = min(n_frames, start_f + preview)

    print("Pre-rendering %d lyric cards ..." % len(cues))
    cards = make_cards(cues)
    labels = make_labels([c[2] for c in cues])
    total_secs = n_frames / FPS
    title_rgb, title_glow = title_card()

    # static layers
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.62) / (H / 2)) ** 2)
    radial = np.clip(1.0 - r, 0, 1)[..., None] ** 2.2
    vignette = np.clip(1.15 - 0.95 * r, 0, 1)[..., None] ** 1.35
    scan = (0.955 + 0.045 * (np.arange(H) % 3 == 0)).astype(np.float32)[:, None, None]
    ember_glow = np.array([1.0, 0.42, 0.11], dtype=np.float32)
    # fold the two static multiplies into one, and pre-tint the radial glow
    darken = (scan * vignette).astype(np.float32)
    radial_tinted = (radial * ember_glow).astype(np.float32)
    base_col = np.array([0.020, 0.019, 0.026], dtype=np.float32)
    # a pool of grain fields, cycled and rolled - generating 921k gaussians per
    # frame was costing more than every other effect combined
    GRAIN_POOL = 12

    rng = np.random.default_rng(7)
    n_emb = 70
    emb_x = rng.uniform(0, W, n_emb)
    emb_y = rng.uniform(0, H, n_emb)
    emb_v = rng.uniform(6, 26, n_emb)
    emb_b = rng.uniform(0.25, 0.9, n_emb)
    grains = [rng.standard_normal((H, W, 1)).astype(np.float32) for _ in range(GRAIN_POOL)]

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ff, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
        "-i", "-", "-i", str(AUDIO),
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(OUTPUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    cue_i = 0
    print("Rendering %d frames ..." % n_frames)
    for i in range(start_f, n_frames):
        t = i / FPS
        while cue_i + 1 < len(cues) and t >= cues[cue_i][1]:
            cue_i += 1
        c_start, c_end, c_name, c_text = cues[cue_i]
        since = t - c_start
        sub = float(sub_env[i])
        hi = float(hi_env[i])

        # --- background: ember glow breathing on the sub bass
        frame = np.zeros((H, W, 3), dtype=np.float32)
        frame += base_col
        frame += radial_tinted * (0.10 + 0.46 * sub ** 1.5)

        # --- embers drifting up
        ey = (emb_y - emb_v * t) % H
        ex = (emb_x + 9 * np.sin(t * 0.5 + emb_x)) % W
        ix, iy = ex.astype(int), ey.astype(int)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                w_ = 0.5 if (dx or dy) else 1.0
                frame[np.clip(iy + dy, 0, H - 1), np.clip(ix + dx, 0, W - 1)] += \
                    (ember_glow * 0.34 * w_) * emb_b[:, None] * (0.5 + 0.5 * sub)

        # --- vignette + scanlines apply to the BACKGROUND only, so long lyric
        #     lines don't get dimmed at their outer edges
        frame *= darken

        # --- lyric text
        rgb, glow = cards[cue_i]
        fade_in = min(1.0, since / 0.10)
        fade_out = min(1.0, max(0.0, (c_end - t) / 0.16))
        alpha = fade_in * fade_out
        hit = max(0.0, 1.0 - since / 0.18)          # impact envelope

        text = rgb * alpha
        # chromatic aberration on the hit
        shift = int(round(7 * hit))
        if shift:
            text = text.copy()
            text[..., 0] = np.roll(rgb[..., 0] * alpha, shift, axis=1)
            text[..., 2] = np.roll(rgb[..., 2] * alpha, -shift, axis=1)
        frame += text
        frame += glow * alpha * (0.30 + 0.55 * sub + 0.9 * hit)

        # --- title card over the intro
        if t < 5.45:
            ta = min(1.0, t / 0.8) * min(1.0, max(0.0, (5.45 - t) / 0.9))
            frame += title_rgb * ta + title_glow * ta * (0.35 + 0.75 * sub)

        # --- grain riding the hats, over everything
        grain = np.roll(grains[i % GRAIN_POOL], (i * 137) % W, axis=1)
        frame += grain * (0.012 + 0.030 * hi)

        # --- HUD last, so the vignette can't swallow the corner label
        l_rgb, l_a = labels[c_name]
        frame = frame * (1 - l_a) + l_rgb
        draw_progress(frame, t / total_secs)

        # --- flash + shake on the kick
        frame += (0.055 * sub ** 3)
        sh = int(round(3.5 * sub ** 4))
        if sh:
            frame = np.roll(frame, sh, axis=0)

        out = (np.clip(frame, 0, 1) * 255).astype(np.uint8)
        proc.stdin.write(out.tobytes())

        if (i - start_f) % 240 == 0:
            print("  %5.1f%%  (%d:%04.1f)" % (100 * i / max(n_frames, 1), int(t // 60), t % 60))

    proc.stdin.close()
    proc.wait()
    print("\n  wrote %s" % OUTPUT.name)


if __name__ == "__main__":
    main()

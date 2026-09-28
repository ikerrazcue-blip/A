"""Timeline, narration, subtitles and rendering for the paper stop-motion videos."""
import bisect
import functools
import hashlib
import math
import os
import re
import subprocess

import numpy as np
import soundfile as sf
from PIL import Image
from scipy.signal import resample_poly

from . import gfx, greek, music
from .gfx import PAL, W, H, Sprite, rgb

FPS = 12          # stop-motion: 12 drawings per second ("on twos")
OUT_FPS = 24
M = 14            # canvas margin for the little camera shake
SR = music.SR
ROOT = gfx.ROOT
VOICES = os.environ.get("STOPMO_VOICES", os.path.join(ROOT, "voices"))
CACHE = os.environ.get("STOPMO_CACHE", os.path.join(ROOT, ".cache"))

VOICE_MODELS = {
    "davefx": ("vits-piper-es_ES-davefx-medium", "es_ES-davefx-medium.onnx", 0),
    "sharvard_m": ("vits-piper-es_ES-sharvard-medium", "es_ES-sharvard-medium.onnx", 0),
    "sharvard_f": ("vits-piper-es_ES-sharvard-medium", "es_ES-sharvard-medium.onnx", 1),
    "miro": ("vits-piper-es_ES-miro-high", "es_ES-miro-high.onnx", 0),
}

# words the TTS should read differently from how they are written on screen
PRONOUNCE = {}


# ----------------------------------------------------------------------------
# voice
# ----------------------------------------------------------------------------
class Voice:
    def __init__(self, name="davefx", speed=0.9, target_rms=0.105):
        self.name, self.speed, self.target_rms = name, speed, target_rms
        self._tts = None

    def _engine(self):
        if self._tts is None:
            import sherpa_onnx
            d, onnx, _ = VOICE_MODELS[self.name]
            d = os.path.join(VOICES, d) + "/"
            cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=d + onnx, tokens=d + "tokens.txt",
                                                           data_dir=d + "espeak-ng-data"),
                num_threads=4))
            self._tts = sherpa_onnx.OfflineTts(cfg)
        return self._tts

    def synth(self, text):
        """Return float32 mono audio at SR for `text` (cached on disk)."""
        sid = VOICE_MODELS[self.name][2]
        key = hashlib.sha1(f"{self.name}|{sid}|{self.speed}|{text}".encode()).hexdigest()[:20]
        os.makedirs(CACHE, exist_ok=True)
        path = os.path.join(CACHE, key + ".wav")
        if os.path.exists(path):
            x, sr = sf.read(path, dtype="float32")
            return x
        a = self._engine().generate(text, sid=sid, speed=self.speed)
        x = np.array(a.samples, dtype=np.float32)
        if a.sample_rate != SR:
            from fractions import Fraction
            fr = Fraction(SR, a.sample_rate)  # 48000/22050 = 320/147
            x = resample_poly(x, fr.numerator, fr.denominator).astype(np.float32)
        x = _trim(x)
        x = _normalize(x, self.target_rms)
        sf.write(path, x, SR)
        return x


def _trim(x, thr_rel=0.03, keep=0.03):
    if len(x) == 0:
        return x
    thr = np.abs(x).max() * thr_rel
    idx = np.nonzero(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    k = int(keep * SR)
    x = x[max(0, idx[0] - k): idx[-1] + k]
    f = int(0.008 * SR)
    if len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
    return x


def _normalize(x, target):
    v = np.abs(x)
    active = x[v > v.max() * 0.05] if v.max() > 0 else x
    rms = np.sqrt(np.mean(active ** 2)) + 1e-9
    y = x * (target / rms)
    return np.tanh(y * 1.1) / np.tanh(1.1) if np.abs(y).max() > 0.9 else y


def tts_text(display):
    t = gfx.plain(display)
    for k, v in PRONOUNCE.items():
        t = re.sub(k, v, t)
    return t


# ----------------------------------------------------------------------------
# narration line
# ----------------------------------------------------------------------------
_SENT = re.compile(r"(?<=[\.\?\!…:;])\s+(?=[^\s])")


class Line:
    def __init__(self, text, t0, parts):
        self.text = text
        self.plain = gfx.plain(text)
        self.t0 = t0
        self.parts = parts  # [(display_text, t0, t1, audio)]
        self.t1 = parts[-1][2]
        self.dur = self.t1 - self.t0

    def at(self, word, n=1, after=0.0):
        """Approximate time at which `word` is spoken (n-th occurrence)."""
        for disp, a, b, _ in self.parts:
            p = gfx.plain(disp).lower()
            idx = -1
            start = 0
            for _ in range(n):
                idx = p.find(word.lower(), start)
                if idx < 0:
                    break
                start = idx + 1
            if idx >= 0:
                return a + 0.04 + (b - a - 0.08) * idx / max(1, len(p)) + after
            # not in this part -> keep searching
        return self.t0 + after

    def end(self, d=0.0):
        return self.t1 + d

    def start(self, d=0.0):
        return self.t0 + d


# ----------------------------------------------------------------------------
# easing & elements
# ----------------------------------------------------------------------------
def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_out_back(p, s=1.4):
    p -= 1
    return p * p * ((s + 1) * p + s) + 1


def ease_in(p):
    return p ** 2.4


def ease_io(p):
    return 3 * p * p - 2 * p * p * p


EASES = {"out": ease_out, "back": ease_out_back, "in": ease_in, "io": ease_io, "lin": lambda p: p}


def _rand(seed, *k):
    h = hashlib.blake2b(repr((seed,) + k).encode(), digest_size=8).digest()
    return int.from_bytes(h, "little") / 2 ** 64


class Element:
    _ids = 0

    def __init__(self, scene, sprite, x, y, at=0.0, enter="drop", z=0, rot=0.0, scale=1.0, jitter=1.0,
                 until=None, exit="cut", enter_dur=None, exit_dur=None, shadow=True):
        Element._ids += 1
        self.id = Element._ids
        self.scene = scene
        self.sprite = sprite
        self.z = z
        self.rest = dict(x=x, y=y, rot=rot, scale=scale)
        self.jitter = jitter
        self.shadow = shadow
        self.t_in = at
        self.segs = []  # (t0, dur, target_state, ease)
        self.swaps = []  # (t, sprite)
        self.pulses = []
        self.wiggles = []
        self.until = None
        self.exit_kind = None
        self._enter(enter, at, enter_dur)
        if until is not None:
            self.leave(until, exit, exit_dur)

    # ---- entering / leaving presets ----
    def _off_state(self, kind, st):
        spr = self.sprite if isinstance(self.sprite, Sprite) else None
        w = (spr.w if spr else 400) * st["scale"]
        h = (spr.h if spr else 400) * st["scale"]
        r = _rand(self.id, "off")
        s = dict(st)
        if kind == "drop":
            s.update(y=st["y"] - 80, rot=st["rot"] + (r - 0.5) * 10, scale=st["scale"] * 1.07)
        elif kind == "slide_l":
            s.update(x=-w / 2 - 60, rot=st["rot"] - 6)
        elif kind == "slide_r":
            s.update(x=W + w / 2 + 60, rot=st["rot"] + 6)
        elif kind == "slide_u":
            s.update(y=H + h / 2 + 60, rot=st["rot"] + (r - 0.5) * 12)
        elif kind == "slide_d":
            s.update(y=-h / 2 - 60, rot=st["rot"] + (r - 0.5) * 12)
        elif kind == "pop":
            s.update(scale=st["scale"] * 0.05)
        elif kind == "grow":
            s.update(scale=st["scale"] * 0.55, rot=st["rot"] + (r - 0.5) * 16)
        return s

    def _enter(self, kind, at, dur):
        if kind in (None, "cut"):
            self.start_state = dict(self.rest)
            return
        dur = dur or {"drop": 0.42, "pop": 0.34, "grow": 0.5}.get(kind, 0.6)
        self.start_state = self._off_state(kind, self.rest)
        ease = "back" if kind in ("drop", "pop", "grow") else "out"
        self.segs.append((at, dur, dict(self.rest), ease))

    def leave(self, t, kind="cut", dur=None):
        self.exit_kind = kind
        if kind in (None, "cut"):
            self.until = t
            return self
        dur = dur or 0.5
        st = self.state_at(t)[0]
        off = self._off_state({"fall": "slide_u", "up": "slide_d"}.get(kind, kind), st)
        if kind == "pop":
            off["scale"] = st["scale"] * 0.05
        self.segs.append((t, dur, off, "in"))
        self.until = t + dur
        return self

    def move(self, t, x=None, y=None, rot=None, scale=None, dur=0.6, ease="io"):
        st = dict(self.state_at(t)[0])
        if x is not None:
            st["x"] = x
        if y is not None:
            st["y"] = y
        if rot is not None:
            st["rot"] = rot
        if scale is not None:
            st["scale"] = scale
        self.segs.append((t, dur, st, ease))
        self.segs.sort(key=lambda s: s[0])
        return self

    def pulse(self, t, amount=0.1, dur=0.42):
        self.pulses.append((t, amount, dur))
        return self

    def wiggle(self, t, amount=5.0, dur=0.6):
        self.wiggles.append((t, amount, dur))
        return self

    def swap(self, t, sprite):
        self.swaps.append((t, sprite))
        self.swaps.sort(key=lambda s: s[0])
        return self

    # ---- evaluation ----
    def visible(self, t):
        if t < self.t_in - 1e-6:
            return False
        if self.until is not None and t >= self.until - 1e-6:
            return False
        return True

    def state_at(self, t):
        st = dict(self.start_state)
        lift = 0.0
        for t0, dur, target, ease in self.segs:
            if t < t0:
                break
            p = 1.0 if dur <= 0 else min(1.0, (t - t0) / dur)
            e = EASES[ease](p)
            if p >= 1.0:
                st = dict(target)
            else:
                st = {k: st[k] + (target[k] - st[k]) * e for k in st}
                lift = max(lift, math.sin(math.pi * p))
        return st, lift

    def current_sprite(self, t):
        spr = self.sprite
        for ts, s in self.swaps:
            if t >= ts:
                spr = s
        return spr

    def draw(self, canvas, t, fi):
        st, lift = self.state_at(t)
        scale, rot = st["scale"], st["rot"]
        for t0, a, d in self.pulses:
            if t0 <= t < t0 + d:
                scale *= 1 + a * math.sin(math.pi * (t - t0) / d)
        for t0, a, d in self.wiggles:
            if t0 <= t < t0 + d:
                p = (t - t0) / d
                rot += a * math.sin(p * math.pi * 4) * (1 - p)
        j = self.jitter * (1 + 2.5 * lift)
        jx = (_rand(self.id, fi, "x") - 0.5) * 1.6 * j
        jy = (_rand(self.id, fi, "y") - 0.5) * 1.6 * j
        jr = (_rand(self.id, fi, "r") - 0.5) * 0.5 * j
        scale *= 1 + 0.035 * lift
        spr = self.current_sprite(t)
        if callable(spr) and not isinstance(spr, Sprite):
            spr = spr(t, fi)
        _draw_cached(canvas, spr, st["x"] + jx + M, st["y"] + jy + M, scale, rot + jr, lift,
                     self.shadow)


@functools.lru_cache(maxsize=700)
def _xf(spr, scale_q, angle_q):
    img = gfx.affine(spr.img, scale_q / 1000.0, angle_q / 10.0)
    sh = gfx.affine(spr.shadow, scale_q / 1000.0, angle_q / 10.0, resample=Image.BILINEAR) \
        if spr.shadow is not None else None
    return img, sh


@functools.lru_cache(maxsize=700)
def _shadow_rgba(spr, scale_q, angle_q, op_q):
    _, sh = _xf(spr, scale_q, angle_q)
    op = op_q / 100.0
    a = sh.point(lambda v: int(v * op))
    im = Image.new("RGBA", sh.size, (30, 16, 6, 0))
    im.putalpha(a)
    return im


def _draw_cached(canvas, spr, cx, cy, scale, angle, lift, shadow=True):
    sq = int(round(scale * 1000 / 5)) * 5
    aq = int(round(angle * 10))
    img, sh = _xf(spr, sq, aq)
    if shadow and sh is not None:
        op = 0.34 - 0.1 * lift
        oq = int(round(op * 50)) * 2
        shimg = _shadow_rgba(spr, sq, aq, oq)
        off = 6 + 12 * lift, 8 + 16 * lift
        gfx.paste_clip(canvas, shimg, cx - shimg.width / 2 + off[0], cy - shimg.height / 2 + off[1])
    gfx.paste_clip(canvas, img, cx - img.width / 2, cy - img.height / 2)


# ----------------------------------------------------------------------------
# the owl puppet
# ----------------------------------------------------------------------------
class Owl(Element):
    def __init__(self, scene, x, y, scale=0.8, at=0.0, enter="slide_u", talk=True, **kw):
        self.owl_scale = scale
        self.talk = talk
        self.moods = [(0.0, "calm", "open", (0, 0))]
        super().__init__(scene, greek.owl_sprite(scale=scale), x, y, at=at, enter=enter, **kw)
        self.sprite = self._sprite_at

    def mood(self, t, mood="calm", eyes="open", look=(0, 0)):
        self.moods.append((t, mood, eyes, tuple(look)))
        self.moods.sort(key=lambda m: m[0])
        return self

    def _sprite_at(self, t, fi):
        mood, eyes, look = "calm", "open", (0, 0)
        for tm, m, e, lk in self.moods:
            if t >= tm:
                mood, eyes, look = m, e, lk
        # blink every ~3-4.5 s
        period = 3.2 + 1.3 * _rand(self.id, "blink")
        ph = (t + _rand(self.id, "ph") * period) % period
        if ph < 1.0 / FPS:
            eyes = "half"
        elif ph < 2.0 / FPS:
            eyes = "closed"
        beak = False
        if self.talk:
            beak = self.scene.voice_level(t) > 0.35 and (fi % 2 == 0 or self.scene.voice_level(t) > 0.7)
        return greek.owl_sprite(eyes, beak, mood, look, self.owl_scale)


# ----------------------------------------------------------------------------
# scenes
# ----------------------------------------------------------------------------
@functools.lru_cache(maxsize=16)
def background(kind, seed=0):
    cw, ch = W + 2 * M, H + 2 * M
    if kind == "terra":
        img = gfx.paper_rgb(cw, ch, "terra", strength=12, seed=seed).convert("RGBA")
        img.alpha_composite(greek.meander_band(cw, 70, bg="black", fg="terra_l", seed=seed + 1), dest=(0, M - 4))
        img.alpha_composite(greek.meander_band(cw, 70, bg="black", fg="terra_l", seed=seed + 2),
                            dest=(0, ch - 70 - M + 4))
    elif kind == "night":
        img = gfx.paper_rgb(cw, ch, (24, 32, 52), strength=10, seed=seed).convert("RGBA")
        img.alpha_composite(greek.meander_band(cw, 58, bg="black", fg="gold", seed=seed + 1), dest=(0, M - 4))
    elif kind == "plain":
        img = gfx.paper_rgb(cw, ch, "paper", strength=12, seed=seed).convert("RGBA")
    else:  # paper with the classic band on top
        img = gfx.paper_rgb(cw, ch, "paper", strength=12, seed=seed).convert("RGBA")
        img.alpha_composite(greek.meander_band(cw, 58, seed=seed + 1), dest=(0, M - 4))
    # vignette
    yy, xx = np.mgrid[0:ch, 0:cw]
    d = np.sqrt(((xx - cw / 2) / (cw / 2)) ** 2 + ((yy - ch / 2) / (ch / 2)) ** 2)
    v = np.clip(1 - 0.16 * np.clip(d - 0.55, 0, None) ** 1.6, 0, 1)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= v[..., None]
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


class Scene:
    def __init__(self, movie, name, bg="paper", lead=0.7, transition="wipe"):
        self.movie = movie
        self.name = name
        self.bg = bg
        self.cursor = lead
        self.lines = []
        self.elements = []
        self.audio = []  # (t, samples)
        self.tail = 0.7
        self.transition = transition
        self._env = None

    # ---- narration ----
    def say(self, text, tts=None, gap=0.34, sentence_gap=0.3):
        """Narrate `text` (rich markup allowed). Sentences are voiced separately so the
        subtitles and visual cues can be timed exactly."""
        sentences = [s for s in _SENT.split(text.strip()) if s.strip()]
        if tts is not None:
            tts_sents = [s for s in _SENT.split(tts.strip()) if s.strip()]
            if len(tts_sents) != len(sentences):
                tts_sents = [tts] if len(sentences) == 1 else None
                if tts_sents is None:
                    sentences, tts_sents = [text], [tts]
        else:
            tts_sents = [tts_text(s) for s in sentences]
        t = self.cursor
        parts = []
        for i, (disp, spoken) in enumerate(zip(sentences, tts_sents)):
            a = self.movie.voice.synth(spoken)
            parts.append((disp, t, t + len(a) / SR, a))
            self.audio.append((t, a))
            t += len(a) / SR + (sentence_gap if i < len(sentences) - 1 else 0)
        line = Line(text, self.cursor, parts)
        self.lines.append(line)
        self.cursor = line.t1 + gap
        self._env = None
        return line

    def wait(self, s):
        self.cursor += s
        return self.cursor

    def now(self):
        return self.cursor

    def jingle(self, t, name="section", gain=0.42):
        a = music.jingle(name, gain)
        self.audio.append((t, a.astype(np.float32)))
        return t + len(a) / SR

    def sfx(self, t, samples):
        self.audio.append((t, samples.astype(np.float32)))

    # ---- visuals ----
    def add(self, sprite, x, y, at=None, **kw):
        e = Element(self, sprite, x, y, at=self.cursor if at is None else at, **kw)
        self.elements.append(e)
        return e

    def owl(self, x, y, scale=0.8, at=None, **kw):
        e = Owl(self, x, y, scale=scale, at=self.cursor if at is None else at, **kw)
        self.elements.append(e)
        return e

    @property
    def duration(self):
        end = self.cursor
        for t, a in self.audio:
            end = max(end, t + len(a) / SR)
        return end + self.tail

    def voice_level(self, t):
        """0..1 loudness of the narration at time t (for the owl's beak)."""
        if self._env is None:
            n = int(self.duration * FPS) + 2
            env = np.zeros(n)
            for line in self.lines:
                for _, a0, a1, a in line.parts:
                    hop = SR // FPS
                    for k in range(0, len(a) // hop):
                        fi = int(round(a0 * FPS)) + k
                        if 0 <= fi < n:
                            env[fi] = max(env[fi], np.sqrt(np.mean(a[k * hop:(k + 1) * hop] ** 2)))
            if env.max() > 0:
                env = env / (np.percentile(env[env > 0], 90) + 1e-9)
            self._env = np.clip(env, 0, 1)
        fi = int(t * FPS)
        return float(self._env[fi]) if 0 <= fi < len(self._env) else 0.0

    def frame(self, t, fi):
        canvas = background(self.bg, self.movie.bg_seed).copy()
        for e in sorted(self.elements, key=lambda e: (e.z, e.id)):
            if e.visible(t):
                e.draw(canvas, t, fi)
        return canvas


# ----------------------------------------------------------------------------
# subtitles
# ----------------------------------------------------------------------------
SUB_SIZE = 46
SUB_MAXW = 1560
SUB_COLORS = {"terra": "terra_l", "blue": "blue_l", "gold": "gold_l", "gold_d": "gold_l", "olive": "olive_l", "purple": "purple_l",
              "brown": "gold_l", "black": "cream", "red": "terra_l"}


def _sub_markup(text):
    def rep(m):
        parts = [SUB_COLORS.get(p, p) for p in m.group(1).split("|")]
        return "{%s:%s}" % ("|".join(parts), m.group(2))
    return gfx._TOKEN.sub(rep, text)


def _words_to_markup(words):
    out = []
    for w in words:
        s = ""
        for txt, style in w:
            s += "{%s:%s}" % (style, txt) if style else txt
        out.append(s)
    return " ".join(out)


def split_cues(text, max_lines=2):
    words = [w for w in gfx._words(text) if w is not None]
    chunks, cur = [], []
    for w in words:
        trial = cur + [w]
        lines, _, _ = gfx.layout_rich(_words_to_markup(trial), "body", SUB_SIZE, SUB_MAXW)
        if len(lines) > max_lines and cur:
            chunks.append(cur)
            cur = [w]
        else:
            cur = trial
        plain_len = len(gfx.plain(_words_to_markup(cur)))
        last = "".join(t for t, _ in w)
        if plain_len > 55 and re.search(r"[\.,;:\?\!…]$", last):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return [_words_to_markup(c) for c in chunks]


@functools.lru_cache(maxsize=256)
def subtitle_sprite(text):
    t = gfx.render_rich(_sub_markup(text), "body", SUB_SIZE, SUB_MAXW, "cream", "gold_l", "center", 1.12)
    pw, ph = 30, 12
    cv = gfx.Canvas(t.width + 2 * pw, t.height + 2 * ph)
    cv.rect(0, 0, t.width + 2 * pw, t.height + 2 * ph, fill=(28, 24, 22, 236))
    img = gfx.paperize(cv.result(), seed=len(text), rough=0.6, texture=5, rim=0.05)
    img.alpha_composite(t, dest=(pw, ph))
    return img


# ----------------------------------------------------------------------------
# movie
# ----------------------------------------------------------------------------
class Movie:
    def __init__(self, voice="davefx", speed=0.9, subtitles=True, bg_seed=3, first_transition=None):
        self.voice = Voice(voice, speed)
        self.scenes = []
        self.subtitles = subtitles
        self.bg_seed = bg_seed
        self._built = False

    def scene(self, name, bg="paper", lead=0.7, transition="wipe"):
        sc = Scene(self, name, bg, lead, transition)
        self.scenes.append(sc)
        self._built = False
        return sc

    # ---- assembly ----
    def build(self):
        self.starts = []
        t = 0.0
        for sc in self.scenes:
            self.starts.append(t)
            t += sc.duration
        self.total = t
        # transitions at boundaries
        self.wipes = []
        for i, sc in enumerate(self.scenes):
            if i > 0 and sc.transition == "wipe":
                self.wipes.append(self.starts[i])
        # cues
        self.cues = []
        for sc, st in zip(self.scenes, self.starts):
            for line in sc.lines:
                line_cues = []
                for disp, a, b, _ in line.parts:
                    chunks = split_cues(disp)
                    total_chars = sum(len(gfx.plain(c)) + 6 for c in chunks)
                    ta = a
                    for c in chunks:
                        d = (b - a) * (len(gfx.plain(c)) + 6) / total_chars
                        line_cues.append([st + ta, st + ta + d, c])
                        ta += d
                # merge tiny pieces (e.g. "«¡oh!».") with their neighbours when it still fits
                merged = []
                for c in line_cues:
                    if merged:
                        prev = merged[-1]
                        short = len(gfx.plain(prev[2])) < 30 or len(gfx.plain(c[2])) < 30
                        cand = prev[2] + " " + c[2]
                        if short and len(gfx.layout_rich(cand, "body", SUB_SIZE, SUB_MAXW)[0]) <= 2:
                            prev[1], prev[2] = c[1], cand
                            continue
                    merged.append(list(c))
                self.cues.extend(merged)
        self.cues.sort(key=lambda c: c[0])
        # bridge short gaps so the subtitle does not flicker off between sentences
        for i in range(len(self.cues) - 1):
            gap = self.cues[i + 1][0] - self.cues[i][1]
            if 0 < gap < 0.9:
                self.cues[i][1] = self.cues[i + 1][0]
        self.cue_starts = [c[0] for c in self.cues]
        # warm shared caches before worker processes fork
        for sc in self.scenes:
            background(sc.bg, self.bg_seed)
            sc._env = None
            sc.voice_level(0)
        if self.wipes:
            _wipe_sheet()
        self._built = True
        return self

    def cue_at(self, t):
        i = bisect.bisect_right(self.cue_starts, t) - 1
        if i >= 0 and self.cues[i][0] <= t < self.cues[i][1] + 0.15:
            return self.cues[i][2]
        return None

    # ---- audio ----
    def mix(self):
        n = int((self.total + 0.5) * SR)
        out = np.zeros(n, np.float32)
        for sc, st in zip(self.scenes, self.starts):
            for t, a in sc.audio:
                s = int((st + t) * SR)
                e = min(n, s + len(a))
                if s < n:
                    out[s:e] += a[: e - s]
        for b in self.wipes:
            sw = music.swoosh().astype(np.float32)
            s = int(max(0, b - 0.45) * SR)
            out[s:s + len(sw)] += sw[: max(0, n - s)]
        peak = np.abs(out).max()
        if peak > 0.97:
            out = np.tanh(out / peak * 1.4) / np.tanh(1.4) * 0.95
        return out

    def write_srt(self, path):
        def ts(x):
            ms = int(round(x * 1000))
            return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
        with open(path, "w", encoding="utf-8") as f:
            for i, (a, b, c) in enumerate(self.cues, 1):
                f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{gfx.plain(c)}\n\n")

    # ---- frames ----
    def frame(self, fi):
        t = fi / FPS
        si = max(0, bisect.bisect_right(self.starts, t) - 1)
        sc = self.scenes[si]
        canvas = sc.frame(t - self.starts[si], fi)
        dx = int(round((_rand("cam", fi, "x") - 0.5) * 2.4))
        dy = int(round((_rand("cam", fi, "y") - 0.5) * 2.4))
        img = canvas.crop((M + dx, M + dy, M + dx + W, M + dy + H))
        for b in self.wipes:
            if b - 0.5 <= t < b + 0.5:
                _draw_wipe(img, (t - (b - 0.5)) / 1.0)
        if self.subtitles:
            cue = self.cue_at(t)
            if cue:
                s = subtitle_sprite(cue)
                gfx.paste_clip(img, s, (W - s.width) // 2, H - 26 - s.height)
        img = img.convert("RGB")
        # light flicker (a real lamp over a real table)
        f = 1.0 + (_rand("flk", fi) - 0.5) * 0.022
        if abs(f - 1) > 1e-3:
            img = img.point([min(255, int(v * f)) for v in range(256)] * 3)
        return img

    def still(self, t, path):
        if not self._built:
            self.build()
        self.frame(int(round(t * FPS))).save(path)

    def render(self, path, workers=4, crf=21, preset="medium", t0=0.0, t1=None, srt=True):
        if not self._built:
            self.build()
        t1 = self.total if t1 is None else min(t1, self.total)
        f0, f1 = int(t0 * FPS), int(math.ceil(t1 * FPS))
        wav = os.path.splitext(path)[0] + ".wav"
        audio = self.mix()[int(t0 * SR): int(t1 * SR)]
        sf.write(wav, audio, SR)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
               "-pix_fmt", "yuv420p", "-r", str(OUT_FPS), "-c:a", "aac", "-b:a", "160k", "-ac", "1",
               "-shortest", "-movflags", "+faststart", path]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        global _MOVIE
        _MOVIE = self
        frames = range(f0, f1)
        if workers > 1:
            import multiprocessing as mp
            ctx = mp.get_context("fork")
            with ctx.Pool(workers) as pool:
                for k, buf in enumerate(pool.imap(_render_worker, frames, chunksize=4)):
                    proc.stdin.write(buf)
                    if k % 240 == 0:
                        print(f"  frame {k}/{len(frames)}", flush=True)
        else:
            for fi in frames:
                proc.stdin.write(_render_worker(fi))
        proc.stdin.close()
        proc.wait()
        os.remove(wav)
        if srt:
            self.write_srt(os.path.splitext(path)[0] + ".srt")
        return path


_MOVIE = None


def _render_worker(fi):
    return _MOVIE.frame(fi).tobytes()


@functools.lru_cache(maxsize=1)
def _wipe_sheet():
    sw = int(W * 1.18)
    img = gfx.paper_rgb(sw, H, "terra", strength=12, seed=77).convert("RGBA")
    band = greek.meander_band(H, 64, bg="black", fg="terra_l", seed=78).rotate(90, expand=True)
    img.alpha_composite(band, dest=(0, 0))
    img.alpha_composite(band, dest=(sw - band.width, 0))
    owl = greek.owl_img("open", False, "calm", (0, 0))
    owl = owl.resize((int(owl.width * 0.9), int(owl.height * 0.9)), Image.LANCZOS)
    img.alpha_composite(owl, dest=((sw - owl.width) // 2, (H - owl.height) // 2))
    return img


def _draw_wipe(img, p):
    sheet = _wipe_sheet()
    sw = sheet.width
    # stepped (stop-motion) slide from right to left
    x = W + (-sw - W) * p
    # soft shadow on the left edge
    shadow = Image.new("RGBA", (40, H), (20, 10, 4, 0))
    shadow.putalpha(Image.linear_gradient("L").rotate(90).resize((40, H)).point(lambda v: int(v * 0.35)))
    gfx.paste_clip(img, shadow, x - 40, 0)
    gfx.paste_clip(img, sheet, x, 0)

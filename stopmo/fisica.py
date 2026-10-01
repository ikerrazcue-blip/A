"""Physics theme for the paper stop-motion videos: warm palette WITHOUT blue, graph-paper tables,
crisp "motion graphics" layers (axes, vectors, trajectories) drawn with cairo on top of the cut-out
paper pieces, and a tiny formula typesetter (vectors with arrows, fractions, sub/superscripts).

Colour code used in every physics video:
    position r -> orange   ·  displacement Δr -> green  ·  distance s -> mustard
    velocity v -> magenta  ·  acceleration a -> red      ·  trajectory -> brown (dashed)
"""
import functools
import math
import re
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import gfx, greek, movie, music
from .gfx import PAL, W, H, Canvas, Sprite, font, paperize, rgb

# ----------------------------------------------------------------------------
# palette (no blue anywhere: every colour has more red than blue)
# ----------------------------------------------------------------------------
FIS_COLORS = {
    "ink": (40, 31, 26),
    "pos": (222, 104, 24), "pos_l": (247, 186, 128), "pos_d": (170, 70, 10),
    "disp": (46, 132, 62), "disp_l": (168, 210, 150), "disp_d": (28, 96, 40),
    "vel": (178, 38, 116), "vel_l": (236, 166, 208), "vel_d": (128, 20, 80),
    "acc": (206, 36, 34), "acc_l": (244, 160, 148), "acc_d": (150, 20, 20),
    "path": (120, 80, 50), "space": (238, 180, 30), "space_l": (250, 220, 120),
    "kraft": (214, 162, 100), "kraft_d": (180, 122, 62), "mustard": (226, 168, 36),
    "grass": (120, 146, 64), "grass_d": (86, 112, 44), "road": (78, 70, 64), "road_l": (104, 96, 88),
    "skin": (238, 190, 150), "skin_d": (214, 156, 116), "hair": (74, 44, 30), "concrete": (196, 186, 172),
    "concrete_d": (156, 146, 134), "sky": (248, 214, 172), "sky_l": (252, 236, 212), "train": (196, 64, 40),
    "train_d": (146, 40, 24), "glass": (252, 232, 192), "glass_d": (222, 196, 150), "grey_l": (186, 178, 170),
}
PAL.update(FIS_COLORS)
movie.SUB_COLORS.update({"pos": "pos_l", "pos_d": "pos_l", "disp": "disp_l", "disp_d": "disp_l", "vel": "vel_l",
                         "vel_d": "vel_l", "acc": "acc_l", "acc_d": "acc_l", "path": "gold_l", "space": "space_l",
                         "ink": "cream", "mustard": "gold_l", "train": "pos_l"})

GRID = 40  # px per square of the graph paper (also 1 m in most diagrams)


# colours of the Greek theme that must never be used in the physics videos
FORBIDDEN = ("blue", "blue_l", "purple", "purple_l")


def no_blue(c):
    if isinstance(c, str):
        assert c not in FORBIDDEN, f"colour '{c}' is not allowed in the physics videos"
    c = rgb(c)
    assert c[2] <= max(c[0], c[1]), f"blue-ish colour {c}"
    return c


for _v in FIS_COLORS.values():
    no_blue(_v)


def _seed(text):
    return zlib.crc32(str(text).encode()) % 997


# ----------------------------------------------------------------------------
# tables (backgrounds) and wipe
# ----------------------------------------------------------------------------
def ruler_band(width, height, bg="cream", fg="ink", seed=0, unit=GRID, numbers=False, edge="bottom"):
    """A paper ruler strip: the physics version of the Greek meander band."""
    cv = Canvas(width, height)
    cv.rect(0, 0, width, height, fill=bg)
    k = 0
    x = unit * 0.5
    while x < width:
        big = k % 5 == 0
        ln = height * (0.55 if big else 0.32) if k % 10 else height * 0.7
        y0, y1 = (height - ln, height) if edge == "bottom" else (0, ln)
        cv.line([(x, y0), (x, y1)], fg, 2.6 if big else 1.8)
        k += 1
        x += unit / 2
    img = paperize(cv.result(), seed=seed, rough=0.45, texture=6)
    if numbers:
        d = ImageDraw.Draw(img)
        f = font("body9", int(height * 0.32))
        for i in range(0, int(width / unit) + 1, 5):
            xx = unit * 0.5 + i * unit
            d.text((xx + 4, height * 0.08 if edge == "bottom" else height * 0.6), str(i), font=f,
                   fill=rgb(fg) + (255,))
    return img


def _grid_paper(cw, ch, seed, color="paper", line=(224, 196, 164), major=(212, 172, 132)):
    img = gfx.paper_rgb(cw, ch, color, strength=11, seed=seed).convert("RGBA")
    cv = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(cv)
    m = movie.M
    k = 0
    for x in range(m, cw, GRID):
        d.line([(x, 0), (x, ch)], fill=(major if k % 5 == 0 else line) + (255,), width=2 if k % 5 == 0 else 1)
        k += 1
    k = 0
    for y in range(ch - m, -1, -GRID):
        d.line([(0, y), (cw, y)], fill=(major if k % 5 == 0 else line) + (255,), width=2 if k % 5 == 0 else 1)
        k += 1
    a = np.asarray(cv.getchannel("A"), np.float32) * (0.75 + 0.25 * (gfx.detail_crop(cw, ch, seed + 5) + 1) / 2)
    cv.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    img.alpha_composite(cv)
    return img


def _bg_grid(cw, ch, seed):
    img = _grid_paper(cw, ch, seed)
    img.alpha_composite(ruler_band(cw, 46, bg="kraft", fg="ink", seed=seed + 1), dest=(0, movie.M - 6))
    return img


def _bg_grid_plain(cw, ch, seed):
    return _grid_paper(cw, ch, seed)


def _bg_kraft(cw, ch, seed):
    img = gfx.paper_rgb(cw, ch, "kraft", strength=13, seed=seed).convert("RGBA")
    img.alpha_composite(ruler_band(cw, 64, bg="cream", fg="ink", seed=seed + 1, numbers=True), dest=(0, movie.M - 6))
    img.alpha_composite(ruler_band(cw, 64, bg="cream", fg="ink", seed=seed + 2, edge="top"),
                        dest=(0, ch - 64 - movie.M + 6))
    return img


def _bg_sky(cw, ch, seed):
    """Warm morning sky for the station (peach to cream, no blue)."""
    yy = np.linspace(0, 1, ch)[:, None, None]
    top, bot = np.array(rgb("sky"), np.float32), np.array(rgb("sky_l"), np.float32)
    arr = top + (bot - top) * np.clip(yy * 1.25, 0, 1)
    arr = np.broadcast_to(arr, (ch, cw, 3)).copy()
    arr += gfx.detail_crop(cw, ch, seed)[..., None] * 10
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return img


def _bg_cream(cw, ch, seed):
    return gfx.paper_rgb(cw, ch, "cream", strength=11, seed=seed).convert("RGBA")


def _bg_grass(cw, ch, seed):
    img = gfx.paper_rgb(cw, ch, (132, 156, 72), strength=13, seed=seed).convert("RGBA")
    a = (gfx.smooth_noise(ch, cw, 180, np.random.default_rng(seed)) - 0.5) * 22
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] += a[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


movie.BACKGROUNDS.update({"grid": _bg_grid, "gridplain": _bg_grid_plain, "kraft": _bg_kraft, "sky": _bg_sky,
                          "cream": _bg_cream, "grass": _bg_grass})


def _wipe(sw, h):
    img = gfx.paper_rgb(sw, h, "pos", strength=12, seed=91).convert("RGBA")
    band = ruler_band(h, 70, bg="cream", fg="ink", seed=92).rotate(90, expand=True)
    img.alpha_composite(band, dest=(0, 0))
    img.alpha_composite(band.transpose(Image.FLIP_LEFT_RIGHT), dest=(sw - band.width, 0))
    ic = greek.icon("stopwatch", 360, "cream")
    img.alpha_composite(ic, dest=((sw - 360) // 2, (h - 360) // 2))
    return img


movie.WIPES["fisica"] = _wipe

# ----------------------------------------------------------------------------
# sound: brighter jingles (major / lydian) and a few paper-table sound effects
# ----------------------------------------------------------------------------
music.JINGLES.update({
    "fis_intro": [(0.00, "C4", 2.2, .5), (0.14, "G4", 2.0, .45), (0.28, "C5", 2.0, .45), (0.42, "E5", 1.8, .45),
                  (0.56, "G5", 1.8, .42), (0.80, "F#5", 1.2, .35), (0.95, "G5", 2.4, .48), (0.95, "C5", 2.4, .3),
                  (0.95, "E4", 2.4, .3)],
    "fis_section": [(0.00, "G4", 1.6, .45), (0.12, "C5", 1.5, .42), (0.24, "E5", 1.4, .42), (0.40, "D5", 1.2, .4),
                    (0.58, "G5", 1.8, .45), (0.58, "C5", 1.8, .28)],
    "fis_idea": [(0.00, "E5", 1.0, .32), (0.09, "G5", 1.0, .3), (0.18, "C6", 1.2, .3)],
    "fis_ding": [(0.00, "G5", 1.0, .34), (0.10, "C6", 1.4, .36)],
    "fis_quiz": [(0.00, "E5", 0.8, .3), (0.16, "D5", 0.8, .28), (0.32, "B4", 1.0, .3)],
    "fis_outro": [(0.00, "C5", 1.8, .45), (0.18, "B4", 1.8, .4), (0.36, "G4", 1.8, .4), (0.54, "E4", 1.8, .4),
                  (0.84, "C4", 3.0, .5), (0.84, "G4", 3.0, .32), (0.84, "E5", 3.0, .3)],
})


def tick(gain=0.05, seed=4, high=True):
    """A soft clock tick."""
    n = int(0.03 * music.SR)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.003 * music.SR))
    if high:
        x = np.diff(np.concatenate([[0], x]))
    return (x / (np.abs(x).max() + 1e-9) * gain).astype(np.float32)


def clack(gain=0.06, seed=7):
    """Rail joint 'ta-dum' for the train."""
    a = music.tap(gain, seed)
    b = music.tap(gain * 0.8, seed + 1)
    gap = int(0.11 * music.SR)
    out = np.zeros(len(a) + gap + len(b), np.float32)
    out[:len(a)] += a
    out[gap:gap + len(b)] += b
    return out


def sfx_ticks(sc, t0, t1, every=1.0, gain=0.05):
    t = t0
    i = 0
    while t < t1 - 1e-6:
        sc.sfx(t, tick(gain, seed=i % 2, high=i % 2 == 0))
        t += every
        i += 1


# ----------------------------------------------------------------------------
# easing helpers
# ----------------------------------------------------------------------------
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def prog(t, t0, dur, ease="io"):
    """0..1 progress of an animation that starts at t0 and lasts dur, eased."""
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return movie.EASES[ease](clamp01((t - t0) / dur))


def lerp(a, b, p):
    return a + (b - a) * p


def lerp2(p0, p1, p):
    return (p0[0] + (p1[0] - p0[0]) * p, p0[1] + (p1[1] - p0[1]) * p)


def stepped(t, fps=12):
    """quantise time to the stop-motion frame rate"""
    return math.floor(t * fps + 1e-6) / fps


# ----------------------------------------------------------------------------
# motion-graphics layer (cairo), drawn crisp on top of the paper pieces
# ----------------------------------------------------------------------------
import cairocffi as cairo  # noqa: E402


def _c01(c, alpha=1.0):
    c = rgb(c) if not (isinstance(c, tuple) and len(c) == 4) else c
    a = (c[3] / 255.0 if len(c) == 4 else 1.0) * alpha
    return c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, a


class Layer:
    """Collects vector drawing ops with their bounding box; rasterises only that box."""

    def __init__(self):
        self.ops = []
        self.stamps = []
        self.bb = [1e9, 1e9, -1e9, -1e9]

    def _ext(self, pts, pad):
        for x, y in pts:
            self.bb[0] = min(self.bb[0], x - pad)
            self.bb[1] = min(self.bb[1], y - pad)
            self.bb[2] = max(self.bb[2], x + pad)
            self.bb[3] = max(self.bb[3], y + pad)

    # -- primitives (screen coordinates) --
    def line(self, pts, color, width=6, dash=None, alpha=1.0, cap="round"):
        pts = [tuple(p) for p in pts]
        if len(pts) < 2 or alpha <= 0.003:
            return self
        self.ops.append(("line", pts, color, width, dash, alpha, cap))
        self._ext(pts, width)
        return self

    def poly(self, pts, fill=None, stroke=None, width=3, alpha=1.0):
        pts = [tuple(p) for p in pts]
        if alpha <= 0.003:
            return self
        self.ops.append(("poly", pts, fill, stroke, width, alpha))
        self._ext(pts, width + 2)
        return self

    def circle(self, x, y, r, fill=None, stroke=None, width=4, alpha=1.0, dash=None):
        if alpha <= 0.003 or r <= 0:
            return self
        self.ops.append(("circle", (x, y, r), fill, stroke, width, alpha, dash))
        self._ext([(x - r, y - r), (x + r, y + r)], width + 2)
        return self

    def arc(self, x, y, r, a0, a1, color, width=5, dash=None, alpha=1.0):
        """angles in degrees, screen orientation (y down => positive = clockwise on screen)"""
        if alpha <= 0.003:
            return self
        self.ops.append(("arc", (x, y, r, a0, a1), color, width, dash, alpha))
        self._ext([(x - r, y - r), (x + r, y + r)], width + 2)
        return self

    def arrow(self, p0, p1, color, width=8, head=None, alpha=1.0, dash=None, min_head=0.0):
        """Straight vector from p0 to p1 with a triangular head (head shrinks for short vectors)."""
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1.0 or alpha <= 0.003:
            return self
        head = head or width * 3.0
        hl = min(head, max(min_head, L * 0.55))
        hw = hl * 0.62
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        bx, by = x1 - ux * hl, y1 - uy * hl
        if L > hl * 0.98:
            self.line([(x0, y0), (bx + ux * 1.5, by + uy * 1.5)], color, width, dash, alpha, cap="butt"
                      if dash else "round")
        self.poly([(x1 + ux * width * 0.15, y1 + uy * width * 0.15), (bx - uy * hw, by + ux * hw),
                   (bx + ux * hl * 0.12, by + uy * hl * 0.12), (bx + uy * hw, by - ux * hw)], fill=color, alpha=alpha)
        return self

    def stamp(self, img, x, y, anchor="c", alpha=1.0, reveal=1.0):
        """paste a PIL RGBA image (labels, formulas) after the vector part. reveal < 1 shows only the left part
        (a 'being written' effect)."""
        if img is None or alpha <= 0.003 or reveal <= 0.0:
            return self
        if reveal < 1.0:
            full_w = img.width
            img = img.crop((0, 0, max(1, int(full_w * reveal)), img.height))
            pad = Image.new("RGBA", (full_w, img.height), (0, 0, 0, 0))
            pad.paste(img, (0, 0))
            img = pad
        w, h = img.size
        ax = {"c": 0.5, "l": 0.0, "r": 1.0}[anchor[0] if anchor[0] in "clr" else "c"]
        ay = 0.5
        if len(anchor) > 1:
            ay = {"t": 0.0, "m": 0.5, "b": 1.0}[anchor[1]]
        x0, y0 = x - w * ax, y - h * ay
        self.stamps.append((img, x0, y0, alpha))
        self._ext([(x0, y0), (x0 + w, y0 + h)], 2)
        return self

    # -- rendering --
    def render(self, canvas, dx=0.0, dy=0.0, shadow=True, sh_off=(3, 5), sh_blur=2.6, sh_op=0.30):
        if not self.ops and not self.stamps:
            return
        cw, chh = canvas.size
        pad = 8 + (int(sh_blur * 3) + max(sh_off) if shadow else 0)
        x0 = int(math.floor(self.bb[0] + dx)) - pad
        y0 = int(math.floor(self.bb[1] + dy)) - pad
        x1 = int(math.ceil(self.bb[2] + dx)) + pad
        y1 = int(math.ceil(self.bb[3] + dy)) + pad
        x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(cw, x1), min(chh, y1)
        if x1c <= x0c or y1c <= y0c:
            return
        if self.ops:
            w, h = x1c - x0c, y1c - y0c
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
            ctx = cairo.Context(surf)
            ctx.translate(dx - x0c, dy - y0c)
            for op in self.ops:
                _cairo_op(ctx, op)
            surf.flush()
            buf = np.frombuffer(surf.get_data(), np.uint8).reshape(h, surf.get_stride() // 4, 4)[:, :w]
            a = buf[..., 3].astype(np.float32)
            rgbv = buf[..., 2::-1].astype(np.float32)  # BGRA -> RGB (premultiplied)
            nz = a > 0
            rgbv[nz] = rgbv[nz] * 255.0 / a[nz][:, None]
            layer = Image.fromarray(np.dstack([np.clip(rgbv, 0, 255), a]).astype(np.uint8), "RGBA")
            if shadow:
                sa = layer.getchannel("A").filter(ImageFilter.GaussianBlur(sh_blur)).point(lambda v: int(v * sh_op))
                sh = Image.new("RGBA", layer.size, (30, 16, 6, 0))
                sh.putalpha(sa)
                gfx.paste_clip(canvas, sh, x0c + sh_off[0], y0c + sh_off[1])
            canvas.alpha_composite(layer, dest=(x0c, y0c))
        for img, sx, sy, al in self.stamps:
            if al < 0.999:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda v: int(v * al)))
            gfx.paste_clip(canvas, img, sx + dx, sy + dy)


def _set_dash(ctx, dash, width):
    if dash:
        ctx.set_dash([d * 1.0 for d in dash])
    else:
        ctx.set_dash([])


def _cairo_op(ctx, op):
    kind = op[0]
    if kind == "line":
        _, pts, color, width, dash, alpha, cap = op
        ctx.set_source_rgba(*_c01(color, alpha))
        ctx.set_line_width(width)
        ctx.set_line_cap({"round": cairo.LINE_CAP_ROUND, "butt": cairo.LINE_CAP_BUTT,
                          "square": cairo.LINE_CAP_SQUARE}[cap])
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        _set_dash(ctx, dash, width)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.stroke()
    elif kind == "poly":
        _, pts, fill, stroke, width, alpha = op
        ctx.set_dash([])
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        if fill:
            ctx.set_source_rgba(*_c01(fill, alpha))
            ctx.fill_preserve() if stroke else ctx.fill()
        if stroke:
            ctx.set_source_rgba(*_c01(stroke, alpha))
            ctx.set_line_width(width)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke()
    elif kind == "circle":
        _, (x, y, r), fill, stroke, width, alpha, dash = op
        ctx.new_path()
        ctx.arc(x, y, r, 0, 2 * math.pi)
        if fill:
            ctx.set_source_rgba(*_c01(fill, alpha))
            ctx.fill_preserve() if stroke else ctx.fill()
        if stroke:
            ctx.set_source_rgba(*_c01(stroke, alpha))
            ctx.set_line_width(width)
            _set_dash(ctx, dash, width)
            ctx.stroke()
        ctx.new_path()
    elif kind == "arc":
        _, (x, y, r, a0, a1), color, width, dash, alpha = op
        ctx.new_path()
        ctx.set_source_rgba(*_c01(color, alpha))
        ctx.set_line_width(width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        _set_dash(ctx, dash, width)
        if a1 >= a0:
            ctx.arc(x, y, r, math.radians(a0), math.radians(a1))
        else:
            ctx.arc_negative(x, y, r, math.radians(a0), math.radians(a1))
        ctx.stroke()


class MG(movie.Element):
    """A motion-graphics element: fn(layer, t) draws vectors/labels for scene time t."""

    def __init__(self, scene, fn, at=0.0, until=None, z=5, shadow=True, **kw):
        self.fn = fn
        self.mg_shadow = shadow
        self.kw = kw
        super().__init__(scene, None, 0.0, 0.0, at=at, enter="cut", z=z, jitter=0.0, until=until)

    def _off_state(self, kind, st):
        s = dict(st)
        if kind == "slide_l":
            s.update(x=st["x"] - W - 200)
        elif kind == "slide_r":
            s.update(x=st["x"] + W + 200)
        elif kind == "slide_u":
            s.update(y=st["y"] + H + 200)
        elif kind == "slide_d":
            s.update(y=st["y"] - H - 200)
        return s

    def draw(self, canvas, t, fi):
        st, _ = self.state_at(t)
        L = Layer()
        self.fn(L, t)
        L.render(canvas, dx=st["x"] + movie.M, dy=st["y"] + movie.M, shadow=self.mg_shadow, **self.kw)

    def sweep_x(self, t):
        L = Layer()
        try:
            self.fn(L, t)
        except Exception:
            return W / 2
        if L.bb[2] < L.bb[0]:
            return W / 2
        return (L.bb[0] + L.bb[2]) / 2


def mg(sc, fn, at=None, until=None, z=5, shadow=True, **kw):
    e = MG(sc, fn, at=sc.now() if at is None else at, until=until, z=z, shadow=shadow, **kw)
    sc.elements.append(e)
    return e


class Live(movie.Element):
    """A paper piece whose sprite and position are computed per frame: fn(t) -> (sprite, x, y, rot)."""

    def __init__(self, scene, fn, at=0.0, until=None, z=3, jitter=1.0, shadow=True):
        self.fn = fn
        super().__init__(scene, None, 0.0, 0.0, at=at, enter="cut", z=z, jitter=jitter, until=until, shadow=shadow)

    def _off_state(self, kind, st):
        return MG._off_state(self, kind, st)

    def sweep_x(self, t):
        try:
            res = self.fn(t)
        except Exception:
            res = None
        return res[1] if res else W / 2

    def draw(self, canvas, t, fi):
        st, lift = self.state_at(t)
        res = self.fn(t)
        if res is None:
            return
        spr, x, y, rot = res[:4]
        scale = res[4] if len(res) > 4 else 1.0
        if spr is None:
            return
        j = self.jitter * (1 + 2.5 * lift)
        fj = fi // self.scene.movie.boil
        jx = (movie._rand(self.id, fj, "x") - 0.5) * 1.6 * j
        jy = (movie._rand(self.id, fj, "y") - 0.5) * 1.6 * j
        jr = (movie._rand(self.id, fj, "r") - 0.5) * 0.5 * j
        movie._draw_cached(canvas, spr, x + st["x"] + jx + movie.M, y + st["y"] + jy + movie.M, scale, rot + jr,
                           lift, self.shadow)


def live(sc, fn, at=None, until=None, z=3, jitter=1.0, shadow=True):
    e = Live(sc, fn, at=sc.now() if at is None else at, until=until, z=z, jitter=jitter, shadow=shadow)
    sc.elements.append(e)
    return e


# ----------------------------------------------------------------------------
# formula typesetter
# ----------------------------------------------------------------------------
SCRIPT = 0.62
_OPS = set("=+−-→·×<>≈≥≤")


class _Box:
    w = 0.0
    asc = 0.0
    desc = 0.0
    italic_top = 0.0  # horizontal skew at the top (for placing accents on italic letters)

    def paint(self, im, x, base):
        pass


class _Space(_Box):
    def __init__(self, w):
        self.w = w


class _Text(_Box):
    def __init__(self, s, size, color, italic=False, fname="body9"):
        f = font(fname, size)
        have = gfx._cmap(f.path)
        if any(ord(ch) not in have for ch in s if not ch.isspace()):
            f = font("sym", size * 0.92)
        self.s, self.f, self.color, self.italic, self.size = s, f, rgb(color), italic, size
        l, t, r, b = f.getbbox(s, anchor="ls")
        self.k = 0.2 if italic else 0.0
        self.ink_top = -t
        self.asc = max(-t, size * 0.5)
        self.desc = max(b, 0)
        self.w = f.getlength(s) + (self.k * self.asc * 0.6 if italic else 0)
        self.italic_top = self.k * self.asc

    def paint(self, im, x, base):
        if not self.italic:
            ImageDraw.Draw(im).text((x, base), self.s, font=self.f, fill=self.color + (255,), anchor="ls")
            return
        pad = int(self.size * 0.4)
        tw = int(self.w + 2 * pad)
        th = int(self.asc + self.desc + 2 * pad)
        tmp = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        b0 = pad + self.asc
        ImageDraw.Draw(tmp).text((pad, b0), self.s, font=self.f, fill=self.color + (255,), anchor="ls")
        k = self.k
        # output pixel (x, y) samples input (x - k*(b0 - y), y)
        tmp = tmp.transform(tmp.size, Image.AFFINE, (1, k, -k * b0, 0, 1, 0), resample=Image.BICUBIC)
        im.alpha_composite(tmp, dest=(int(round(x - pad)), int(round(base - b0))))


class _HList(_Box):
    def __init__(self, items):
        self.items = items
        self.w = sum(i.w for i in items)
        self.asc = max([i.asc for i in items] + [0])
        self.desc = max([i.desc for i in items] + [0])
        self.italic_top = items[-1].italic_top if items else 0

    def paint(self, im, x, base):
        for it in self.items:
            it.paint(im, x, base)
            x += it.w


class _Vec(_Box):
    """arrow accent over a (usually italic) letter"""

    def __init__(self, inner, size, color):
        self.inner, self.size, self.color = inner, size, rgb(color)
        self.gap = size * 0.07
        self.ah = size * 0.2
        self.w = inner.w + size * 0.04
        self.asc = inner.asc + self.gap + self.ah
        self.desc = inner.desc

    def paint(self, im, x, base):
        self.inner.paint(im, x, base)
        s = self.size
        y = base - self.inner.asc - self.gap - self.ah * 0.5
        skew = 0.2 * (self.inner.asc + self.gap)
        x0 = x + s * 0.06 + skew * 0.85
        x1 = x + self.inner.w + skew * 0.85 + s * 0.04
        th = max(2.0, s * 0.055)
        hl, hw = s * 0.17, s * 0.1
        cv = ImageDraw.Draw(im)
        cv.line([(x0, y), (x1 - hl * 0.6, y)], fill=self.color + (255,), width=int(round(th)))
        cv.polygon([(x1, y), (x1 - hl, y - hw), (x1 - hl * 0.75, y), (x1 - hl, y + hw)], fill=self.color + (255,))


class _Script(_Box):
    def __init__(self, base, sub=None, sup=None, size=60):
        self.base, self.sub, self.sup = base, sub, sup
        g = size * 0.04
        self.drop = size * 0.24
        self.rise = size * 0.42
        ws = max(sub.w if sub else 0, (sup.w + base.italic_top * 0.5) if sup else 0)
        self.w = base.w + g + ws
        self.asc = max(base.asc, (sup.asc + self.rise) if sup else 0)
        self.desc = max(base.desc, (sub.desc + self.drop) if sub else 0)
        self.g = g

    def paint(self, im, x, base):
        self.base.paint(im, x, base)
        xs = x + self.base.w + self.g
        if self.sub:
            self.sub.paint(im, xs - self.base.italic_top * 0.25, base + self.drop)
        if self.sup:
            self.sup.paint(im, xs + self.base.italic_top * 0.3, base - self.rise)


class _Frac(_Box):
    def __init__(self, num, den, size, color):
        self.num, self.den, self.color = num, den, rgb(color)
        self.pad = size * 0.12
        self.th = max(3.0, size * 0.06)
        self.gap = size * 0.13
        self.axis = size * 0.30
        self.w = max(num.w, den.w) + 2 * self.pad
        self.asc = self.axis + self.th / 2 + self.gap + num.desc + num.asc
        self.desc = max(0.0, -self.axis + self.th / 2 + self.gap + den.asc + den.desc)

    def paint(self, im, x, base):
        yb = base - self.axis
        ImageDraw.Draw(im).rectangle([x + self.pad * 0.4, yb - self.th / 2, x + self.w - self.pad * 0.4,
                                      yb + self.th / 2], fill=self.color + (255,))
        self.num.paint(im, x + (self.w - self.num.w) / 2, yb - self.th / 2 - self.gap - self.num.desc)
        self.den.paint(im, x + (self.w - self.den.w) / 2, yb + self.th / 2 + self.gap + self.den.asc)


class _Under(_Box):
    """operator with a limit underneath (lim with Δt→0 below)"""

    def __init__(self, op, under, size):
        self.op, self.under = op, under
        self.gap = size * 0.1
        self.w = max(op.w, under.w)
        self.asc = op.asc
        self.desc = max(op.desc, self.gap + under.asc + under.desc + size * 0.05)

    def paint(self, im, x, base):
        self.op.paint(im, x + (self.w - self.op.w) / 2, base)
        self.under.paint(im, x + (self.w - self.under.w) / 2, base + self.gap + self.under.asc + self.op.desc)


class _Sqrt(_Box):
    def __init__(self, inner, size, color):
        self.inner, self.size, self.color = inner, size, rgb(color)
        self.th = max(3.0, size * 0.06)
        self.lead = size * 0.5
        self.gap = size * 0.1
        self.w = self.lead + inner.w + size * 0.12
        self.asc = inner.asc + self.gap + self.th
        self.desc = inner.desc + size * 0.04

    def paint(self, im, x, base):
        s = self.size
        top = base - self.inner.asc - self.gap - self.th / 2
        bot = base + self.inner.desc
        d = ImageDraw.Draw(im)
        c = self.color + (255,)
        w = int(round(self.th))
        pts = [(x + s * 0.04, base - s * 0.22), (x + s * 0.14, base - s * 0.28), (x + s * 0.3, bot),
               (x + self.lead - s * 0.06, top), (x + self.w, top)]
        d.line(pts, fill=c, width=w, joint="curve")
        self.inner.paint(im, x + self.lead + s * 0.02, base)


def _read_group(s, i):
    """returns raw text of {...} starting at s[i] == '{' (nesting aware)"""
    assert s[i] == "{", (s, i)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced braces in " + s)


def _parse(s, size, color):
    items = []
    i = 0
    last = None          # kind of the previous token: None (start), "op", "open" or "atom"
    while i < len(s):
        ch = s[i]
        if ch in "+−-" and last in (None, "op", "open"):
            # a sign, not an operation: no spaces around it ("v = −4", "(−9,8)")
            items.append(_Text("−" if ch == "-" else ch, size, color))
            i += 1
            last = "open"
            continue
        if ch not in " ":
            last = "op" if ch in _OPS else ("open" if ch in "([{" else "atom")
            if ch == "\\" and s[i + 1:i + 2] in (",", ";") :
                last = last
        if ch == "\\":
            m = re.match(r"\\([a-zA-Z]+|.)", s[i:])
            cmd = m.group(1)
            i += len(m.group(0))
            if cmd == "vec":
                raw, i = _read_group(s, i)
                inner = _parse(raw, size, color)
                items.append(_Vec(inner, size, color))
            elif cmd == "sqrt":
                raw, i = _read_group(s, i)
                items.append(_Sqrt(_parse(raw, size, color), size, color))
            elif cmd == "frac":
                a, i = _read_group(s, i)
                b, i = _read_group(s, i)
                items.append(_Frac(_parse(a, size, color), _parse(b, size, color), size, color))
            elif cmd == "c":
                name, i = _read_group(s, i)
                raw, i = _read_group(s, i)
                items.append(_parse(raw, size, name))
            elif cmd in ("t", "b"):
                raw, i = _read_group(s, i)
                items.append(_Text(raw, size, color, False, "body9" if cmd == "b" else "body"))
            elif cmd == "h":  # handwritten note
                raw, i = _read_group(s, i)
                items.append(_Text(raw, size * 1.12, color, False, "hand"))
            elif cmd == "lim":
                raw, i = _read_group(s, i)
                items.append(_Under(_Text("lim", size, color), _parse(raw, size * 0.55, color), size))
                items.append(_Space(size * 0.12))
            elif cmd == ",":
                items.append(_Space(size * 0.14))
            elif cmd == ";":
                items.append(_Space(size * 0.3))
            elif cmd == "quad":
                items.append(_Space(size * 0.9))
            elif cmd == "qquad":
                items.append(_Space(size * 1.8))
            elif cmd == "to":
                items.append(_Space(size * 0.08))
                items.append(_Text("→", size * 0.9, color))
                items.append(_Space(size * 0.08))
            elif cmd in ("geq", "leq", "neq", "approx", "infty", "cdot", "pm"):
                ch2 = {"geq": "≥", "leq": "≤", "neq": "≠", "approx": "≈", "infty": "∞", "cdot": "·", "pm": "±"}[cmd]
                sp = size * (0.2 if cmd not in ("infty",) else 0.02)
                items.append(_Space(sp))
                items.append(_Text(ch2, size, color))
                items.append(_Space(sp))
            elif cmd in ("Rightarrow", "implies"):
                items.append(_Space(size * 0.25))
                items.append(_Text("⇒", size * 0.95, color))
                items.append(_Space(size * 0.25))
            else:
                items.append(_Text(cmd, size, color))
        elif ch in "_^":
            i += 1
            if s[i] == "{":
                raw, i = _read_group(s, i)
            else:
                raw, i = s[i], i + 1
            arg = _parse(raw, size * SCRIPT, color)
            prev = items.pop() if items else _Space(0)
            if isinstance(prev, _Script) and ((ch == "_" and prev.sub is None) or (ch == "^" and prev.sup is None)):
                items.append(_Script(prev.base, prev.sub or (arg if ch == "_" else None),
                                     prev.sup or (arg if ch == "^" else None), size))
            else:
                items.append(_Script(prev, arg if ch == "_" else None, arg if ch == "^" else None, size))
        elif ch == "{":
            raw, i = _read_group(s, i)
            items.append(_parse(raw, size, color))
        elif ch == " ":
            items.append(_Space(size * 0.12))
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(s) and (s[j].isdigit() or (s[j] in ",." and j + 1 < len(s) and s[j + 1].isdigit())):
                j += 1
            items.append(_Text(s[i:j], size, color))
            i = j
        elif ch.isalpha() and ch not in "ΔΣΩ∆":
            items.append(_Text(ch, size, color, italic=True))
            i += 1
        elif ch in _OPS:
            sp = size * 0.2
            items.append(_Space(sp))
            items.append(_Text("−" if ch == "-" else ch, size, color))
            items.append(_Space(sp))
            i += 1
        else:
            items.append(_Text(ch, size, color))
            i += 1
    return _HList(items)


@functools.lru_cache(maxsize=512)
def formula(src, size=64, color="ink"):
    """Render a formula to an RGBA image. Mini-syntax: \\vec{r}, \\frac{a}{b}, x_0, v^2, \\c{vel}{...},
    \\t{text} (upright), \\b{bold text}, \\h{handwritten}, \\lim{Δt\\to0}, \\, \\; \\quad."""
    box = _parse(src, size, color)
    pad = int(size * 0.18) + 4
    w = int(math.ceil(box.w + 2 * pad))
    h = int(math.ceil(box.asc + box.desc + 2 * pad))
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    box.paint(im, pad, pad + box.asc)
    bb = im.getbbox()
    if bb:
        im = im.crop((max(0, bb[0] - 4), max(0, bb[1] - 4), min(w, bb[2] + 4), min(h, bb[3] + 4)))
    return im


def formula_card(src, size=64, color="ink", bg="cream", border=None, pad=(40, 22), seed=None, rough=0.8, min_w=0,
                 radius=0, shadow_blur=5):
    seed = _seed(src) if seed is None else seed
    f = formula(src, size, color)
    cw = max(min_w, f.width + 2 * pad[0])
    ch = f.height + 2 * pad[1]
    cv = Canvas(cw, ch)
    cv.rect(2, 2, cw - 2, ch - 2, fill=bg, radius=radius)
    if border:
        bc, bw = border
        cv.rect(2 + bw * 1.6, 2 + bw * 1.6, cw - 2 - bw * 1.6, ch - 2 - bw * 1.6, outline=bc, width=bw,
                radius=max(0, radius - bw))
    base = paperize(cv.result(), seed=seed, rough=rough, texture=7)
    base.alpha_composite(f, dest=((cw - f.width) // 2, (ch - f.height) // 2))
    return Sprite(base, shadow_blur=shadow_blur)


@functools.lru_cache(maxsize=1024)
def tag_img(src, size=40, color="ink", bg=(251, 245, 230, 235), pad=(10, 4), radius=10, border=None):
    """A small crisp sticker (label) for motion graphics: formula on a rounded light plate."""
    f = formula(src, size, color)
    w, h = f.width + 2 * pad[0], f.height + 2 * pad[1]
    cv = Canvas(w, h)
    if bg:
        cv.rect(1, 1, w - 1, h - 1, fill=bg, radius=radius)
    if border:
        cv.rect(1 + border[1] / 2, 1 + border[1] / 2, w - 1 - border[1] / 2, h - 1 - border[1] / 2, outline=border[0],
                width=border[1], radius=radius)
    im = cv.result()
    im.alpha_composite(f, dest=(pad[0], pad[1]))
    return im


@functools.lru_cache(maxsize=1024)
def text_img(text, size=40, color="ink", font_name="body9", max_w=1400, align="center"):
    return gfx.render_rich(text, font_name, size, max_w, color, "pos", align)


def num(x, dec=1, unit=""):
    """Spanish decimal comma: 6.4 -> '6,4'."""
    if abs(x) < 0.5 * 10 ** (-dec):
        x = 0.0
    s = f"{x:.{dec}f}".replace(".", ",")
    if s.startswith("-"):
        s = "−" + s[1:]
    return s + (("\\," + unit) if unit else "")


# ----------------------------------------------------------------------------
# paper props
# ----------------------------------------------------------------------------
def _piece(w, h, draw, seed=0, rough=0.7, texture=7.0, shadow_blur=5):
    cv = Canvas(w, h)
    draw(cv)
    return Sprite(paperize(cv.result(), seed=seed, rough=rough, texture=texture), shadow_blur=shadow_blur)


def _layered(w, h, draws, seed=0, rough=0.6, shadow_blur=5):
    """several paper layers glued on top of each other (each casts a small shadow on the one below)"""
    base = None
    for i, d in enumerate(draws):
        cv = Canvas(w, h)
        d(cv)
        lay = paperize(cv.result(), seed=seed + i, rough=rough, texture=7)
        base = lay if base is None else gfx.inner_shadow_layer(base, lay, offset=(2, 3), blur=2.4, opacity=0.33)
    return Sprite(base, shadow_blur=shadow_blur)


def icon_piece(name, size, color="ink", seed=None):
    return greek.icon_cutout(name, size, color, seed=_seed(name) if seed is None else seed)


def medal(icon_name, diam=120, bg="pos_l", fg="ink", seed=None):
    return greek.medallion(diam, icon_name, bg=bg, fg=fg, seed=_seed(icon_name) + 3 if seed is None else seed)


def check_mark(size=90, ok=True, seed=None):
    return greek.icon_cutout("check-mark" if ok else "cross-mark", size, "grass_d" if ok else "acc_d",
                             seed=(31 if ok else 37) if seed is None else seed)


# --- people -------------------------------------------------------------------------------------
def _person_front(cv, cx, top, h, shirt="grass", pants="kraft_d", hair="hair", girl=False, smile=True):
    s = h / 300.0
    hr = 40 * s
    hy = top + hr + 4 * s
    # legs
    for dx in (-17, 17):
        cv.rect(cx + dx * s - 13 * s, top + 186 * s, cx + dx * s + 13 * s, top + 284 * s, fill=pants, radius=6 * s)
        cv.ellipse(cx + dx * s + (4 if dx > 0 else -4) * s, top + 288 * s, 19 * s, 10 * s, fill="ink")
    # arms
    for sg in (-1, 1):
        cv.poly([(cx + sg * 40 * s, top + 100 * s), (cx + sg * 56 * s, top + 108 * s), (cx + sg * 62 * s, top + 196 * s),
                 (cx + sg * 46 * s, top + 198 * s)], fill=shirt)
        cv.circle(cx + sg * 54 * s, top + 204 * s, 10 * s, fill="skin")
    # body
    cv.rect(cx - 44 * s, top + 92 * s, cx + 44 * s, top + 196 * s, fill=shirt, radius=16 * s)
    cv.rect(cx - 9 * s, top + 74 * s, cx + 9 * s, top + 96 * s, fill="skin_d")
    # head
    if girl:
        cv.ellipse(cx, hy - 2 * s, hr * 1.16, hr * 1.08, fill=hair)
        for sg in (-1, 1):
            cv.rect(cx + sg * hr * 0.78 - (hr * 0.38 if sg > 0 else 0), hy - 4 * s,
                    cx + sg * hr * 0.78 + (0 if sg > 0 else hr * 0.38) + (hr * 0.38 if sg > 0 else -hr * 0.38) * 0 +
                    (hr * 0.38 if sg > 0 else 0), hy + hr * 1.18, fill=hair, radius=8 * s)
    cv.circle(cx, hy, hr, fill="skin")
    if girl:
        cv.poly(greek.ellipse_pts(cx, hy - 6 * s, hr * 1.06, hr * 0.92, a0=180, a1=360), fill=hair)
    else:
        cv.poly(greek.ellipse_pts(cx, hy - 8 * s, hr * 1.04, hr * 0.86, a0=185, a1=355), fill=hair)
        cv.rect(cx - hr * 1.0, hy - 14 * s, cx - hr * 0.78, hy + 6 * s, fill=hair)
        cv.rect(cx + hr * 0.78, hy - 14 * s, cx + hr * 1.0, hy + 6 * s, fill=hair)
    for dx in (-14, 14):
        cv.circle(cx + dx * s, hy + 2 * s, 4.6 * s, fill="ink")
    if smile:
        cv.arc(cx, hy + 12 * s, 13 * s, 9 * s, 20, 160, "ink", 3.4 * s)
    cv.circle(cx - 24 * s, hy + 14 * s, 6 * s, fill=(240, 160, 140))
    cv.circle(cx + 24 * s, hy + 14 * s, 6 * s, fill=(240, 160, 140))


@functools.lru_cache(maxsize=8)
def leo_sprite(h=290, seed=61):
    w = int(h * 0.48)
    return _piece(w, h + 12, lambda cv: _person_front(cv, w / 2, 4, h, shirt="grass", pants="kraft_d"), seed=seed)


@functools.lru_cache(maxsize=8)
def ana_front_sprite(h=290, seed=62):
    w = int(h * 0.48)
    return _piece(w, h + 12, lambda cv: _person_front(cv, w / 2, 4, h, shirt="mustard", pants="train_d", girl=True),
                  seed=seed)


def _ana_profile_head(cv, hx, hy, s=1.0, face=1):
    """Ana's head in profile looking to `face` (+1 right, -1 left)."""
    r = 25 * s
    cv.ellipse(hx - face * 30 * s, hy + 6 * s, 15 * s, 9 * s, fill="hair")  # pony tail
    cv.circle(hx - face * 18 * s, hy + 8 * s, 6 * s, fill="pos")  # hair tie
    cv.circle(hx, hy, r, fill="skin")
    cv.poly([(hx + face * r * 0.75, hy - 2 * s), (hx + face * (r + 7 * s), hy + 6 * s), (hx + face * r * 0.7, hy + 9 * s)],
            fill="skin")
    cv.poly(greek.ellipse_pts(hx - face * 3 * s, hy - 6 * s, r * 1.05, r * 0.9, a0=180, a1=360), fill="hair")
    cv.poly([(hx - face * r * 1.02, hy - 8 * s), (hx - face * r * 0.2, hy - 8 * s), (hx - face * r * 0.55, hy + 14 * s),
             (hx - face * r * 0.98, hy + 12 * s)], fill="hair")
    cv.circle(hx + face * 12 * s, hy - 1 * s, 3.4 * s, fill="ink")
    cv.circle(hx + face * 12 * s, hy + 12 * s, 4.5 * s, fill=(240, 160, 140))


# --- train (side view) ----------------------------------------------------------------------------
TRAIN = dict(w=1700, h=420, car0=20, car1=1060, loco0=1072, loco1=1680, roof=40, top=62, floor=356, wheel_y=390,
             win_y0=112, win_y1=244, win_w=124, win_c0=150, win_step=158, ana_win=2)


def train_info():
    """local coordinates (relative to the sprite's top-left) of the useful points of the train"""
    T = TRAIN
    ana_x = T["car0"] + T["win_c0"] + T["ana_win"] * T["win_step"]
    return dict(rear=T["car0"], front=T["loco1"], floor=T["floor"], ana=(ana_x, T["win_y0"] + 60), w=T["w"],
                h=T["h"], wheel=T["wheel_y"])


@functools.lru_cache(maxsize=2)
def train_sprite(seed=70):
    T = TRAIN
    w, h = T["w"], T["h"]
    c0, c1, l0, l1 = T["car0"], T["car1"], T["loco0"], T["loco1"]
    top, floor = T["top"], T["floor"]

    def bogies(cv):
        for x in (c0 + 150, c1 - 150, l0 + 140, l1 - 200):
            cv.rect(x - 104, floor - 2, x + 104, floor + 24, fill=(70, 60, 54), radius=6)
            for dx in (-58, 58):
                cv.circle(x + dx, T["wheel_y"] - 6, 30, fill=(52, 44, 40))
                cv.circle(x + dx, T["wheel_y"] - 6, 12, fill=(150, 140, 130))
        cv.rect(c1 - 4, floor - 120, l0 + 4, floor - 10, fill=(70, 60, 54))  # gangway

    def bodies(cv):
        # carriage
        cv.rect(c0, top, c1, floor + 6, fill="train", radius=22)
        cv.rect(c0 + 10, top - 22, c1 - 10, top + 16, fill="grey_l", radius=16)
        # locomotive with a rounded nose
        nose = [(l0, top), (l1 - 240, top)]
        for k in range(13):
            a = math.radians(-90 + 90 * k / 12)
            nose.append((l1 - 240 + 240 * math.cos(a) ** 0.8, top + (floor + 6 - top) * 0.55 * (1 + math.sin(a))))
        nose += [(l1, floor + 6), (l0, floor + 6)]
        cv.poly(nose, fill="train")
        cv.rect(l0 + 10, top - 22, l1 - 270, top + 16, fill="grey_l", radius=16)

    def stripes(cv):
        cv.rect(c0 + 4, T["win_y0"] - 18, c1 - 4, T["win_y1"] + 18, fill="cream")
        cv.rect(c0 + 4, T["win_y1"] + 34, c1 - 4, T["win_y1"] + 46, fill="mustard")
        cv.rect(l0 + 4, T["win_y0"] - 18, l1 - 180, T["win_y1"] + 18, fill="cream")
        cv.rect(l0 + 4, T["win_y1"] + 34, l1 - 40, T["win_y1"] + 46, fill="mustard")
        # door
        cv.rect(c1 - 140, top + 26, c1 - 46, floor - 8, fill="train_d", radius=8)
        cv.rect(l0 + 30, top + 26, l0 + 120, floor - 8, fill="train_d", radius=8)

    def windows(cv):
        for i in range(6):
            cx = c0 + T["win_c0"] + i * T["win_step"]
            if cx + T["win_w"] / 2 > c1 - 150:
                continue
            cv.rect(cx - T["win_w"] / 2, T["win_y0"], cx + T["win_w"] / 2, T["win_y1"], fill="glass", radius=14)
            # seat backs (dark red) seen through the window
            cv.rect(cx - 54, T["win_y0"] + 52, cx - 24, T["win_y1"], fill="train_d", radius=9)
        for x0 in (c1 - 128, l0 + 44):
            cv.rect(x0, top + 44, x0 + 66, top + 140, fill="glass", radius=8)
        # loco side window and windscreen
        cv.rect(l0 + 180, T["win_y0"], l0 + 360, T["win_y1"], fill="glass", radius=14)
        cv.poly([(l1 - 228, T["win_y0"] - 4), (l1 - 86, T["win_y0"] - 4), (l1 - 22, T["win_y1"] - 10),
                 (l1 - 228, T["win_y1"] - 10)], fill="glass_d")
        cv.circle(l1 - 30, floor - 46, 14, fill="space_l")

    def ana(cv):
        cx = c0 + T["win_c0"] + T["ana_win"] * T["win_step"]
        # torso (mustard jumper) and head in profile, looking forwards (to the right)
        cv.rect(cx - 26, T["win_y0"] + 84, cx + 32, T["win_y1"] + 2, fill="mustard", radius=16)
        _ana_profile_head(cv, cx + 6, T["win_y0"] + 50, 1.3, face=1)

    spr = _layered(w, h, [bogies, bodies, stripes, windows, ana], seed=seed, rough=0.55, shadow_blur=6)
    return spr


# --- platform, scenery -------------------------------------------------------------------------------
PLAT_TOP = 724  # screen y of the platform's top surface (where people stand)


@functools.lru_cache(maxsize=4)
def platform_tile(w=1200, seed=80):
    h = 1080 + 2 * movie.M - PLAT_TOP + 40

    def draw(cv):
        cv.rect(0, 0, w, 36, fill="concrete")
        cv.rect(0, 8, w, 18, fill="mustard")
        cv.rect(0, 36, w, h, fill="concrete_d")
        for x in range(0, w, 150):
            cv.line([(x, 40), (x, h)], (138, 128, 118), 3)
        cv.rect(0, 36, w, 46, fill=(136, 126, 116))
    cv = Canvas(w, h)
    draw(cv)
    return Sprite(paperize(cv.result(), seed=seed, rough=0.0, texture=8, rim=0.0), shadow_blur=4, pad=0, shadow=False)


@functools.lru_cache(maxsize=4)
def rails_tile(w=1200, seed=81):
    def draw(cv):
        cv.rect(0, 26, w, 52, fill=(150, 126, 100))
        for x in range(10, w, 60):
            cv.rect(x, 30, x + 34, 50, fill=(110, 84, 62))
        cv.rect(0, 22, w, 32, fill=(96, 90, 86))
    cv = Canvas(w, 60)
    draw(cv)
    return Sprite(paperize(cv.result(), seed=seed, rough=0.0, texture=8, rim=0.0), pad=0, shadow=False)


@functools.lru_cache(maxsize=4)
def hills_tile(w=6000, seed=82):
    h = 260

    def far(cv):
        pts = [(0, h)]
        for k in range(0, w + 1, 40):
            pts.append((k, 110 + 50 * math.sin(k / 330.0) + 26 * math.sin(k / 97.0 + 1.3)))
        pts.append((w, h))
        cv.poly(pts, fill=(196, 170, 120))

    def near(cv):
        pts = [(0, h)]
        for k in range(0, w + 1, 40):
            pts.append((k, 170 + 34 * math.sin(k / 210.0 + 2.0) + 14 * math.sin(k / 61.0)))
        pts.append((w, h))
        cv.poly(pts, fill="grass")
        for x in range(90, w, 260):
            yy = 170 + 34 * math.sin(x / 210.0 + 2.0) + 14 * math.sin(x / 61.0)
            cv.rect(x - 4, yy - 30, x + 4, yy + 4, fill="brown_d")
            cv.ellipse(x, yy - 44, 24, 30, fill="grass_d")
    return _layered(w, h, [far, near], seed=seed, rough=0.5, shadow_blur=4)


@functools.lru_cache(maxsize=4)
def lamp_post(h=470, seed=83):
    w = 90

    def draw(cv):
        cv.rect(w / 2 - 6, 30, w / 2 + 6, h, fill="ink")
        cv.rect(w / 2 - 14, h - 16, w / 2 + 14, h, fill="ink", radius=4)
        cv.rect(w / 2 - 36, 22, w / 2 + 36, 40, fill="ink", radius=8)
        cv.ellipse(w / 2, 46, 22, 10, fill="space_l")
    return _piece(w, h + 4, draw, seed=seed, rough=0.4)


@functools.lru_cache(maxsize=4)
def bench(seed=84):
    w, h = 190, 100

    def draw(cv):
        for x in (22, w - 22):
            cv.rect(x - 6, 50, x + 6, h, fill="ink")
        cv.rect(0, 50, w, 64, fill="brown", radius=4)
        cv.rect(4, 8, w - 4, 22, fill="brown", radius=4)
        cv.rect(4, 28, w - 4, 42, fill="brown", radius=4)
        for x in (22, w - 22):
            cv.rect(x - 4, 8, x + 4, 52, fill="ink")
    return _piece(w, h, draw, seed=seed, rough=0.5)


@functools.lru_cache(maxsize=4)
def station_sign(text="VILLAPAPEL", seed=85, h=430):
    t = gfx.render_rich(text, "body9", 46, 900, "ink")
    w = t.width + 60

    def draw(cv):
        for x in (40, w - 40):
            cv.rect(x - 5, 60, x + 5, h, fill="ink")
        cv.rect(0, 0, w, 78, fill="cream", radius=10)
        cv.rect(6, 6, w - 6, 72, outline="ink", width=4, radius=8)
    cv = Canvas(w, h)
    draw(cv)
    img = paperize(cv.result(), seed=seed, rough=0.5, texture=7)
    img.alpha_composite(t, dest=((w - t.width) // 2, (78 - t.height) // 2))
    return Sprite(img, shadow_blur=5)


@functools.lru_cache(maxsize=4)
def cloud(w=260, seed=86):
    h = int(w * 0.42)

    def draw(cv):
        for cx, cy, r in ((0.25, 0.62, 0.22), (0.45, 0.45, 0.28), (0.68, 0.55, 0.24), (0.82, 0.68, 0.16)):
            cv.circle(cx * w, cy * h * 1.0, r * w, fill="cream")
        cv.rect(0.12 * w, 0.6 * h, 0.9 * w, 0.92 * h, fill="cream", radius=0.15 * h)
    return _piece(w, h, draw, seed=seed, rough=0.6)


@functools.lru_cache(maxsize=2)
def sun_piece(d=190, seed=87):
    return _piece(d, d, lambda cv: cv.circle(d / 2, d / 2, d / 2 - 3, fill="space_l"), seed=seed, rough=0.4)


# ----------------------------------------------------------------------------
# a scrolling world (camera) for scenery: items in world coordinates, drawn with parallax
# ----------------------------------------------------------------------------
class World(movie.Element):
    """items: [(sprite, world_x, screen_y, parallax, jitter)] ; cam(t) -> camera x (world units of parallax 1).
    Sprites are positioned by their centre. Tiles with jitter 0 do not boil (no seams)."""

    def __init__(self, scene, items, cam, at=0.0, until=None, z=0, shadow=True):
        self.items = items
        self.cam = cam
        super().__init__(scene, None, 0.0, 0.0, at=at, enter="cut", z=z, jitter=0.0, until=until, shadow=shadow)

    def _off_state(self, kind, st):
        return MG._off_state(self, kind, st)

    def sweep_x(self, t):
        return W / 2

    def draw(self, canvas, t, fi):
        st, _ = self.state_at(t)
        c = self.cam(t)
        fj = fi // self.scene.movie.boil
        for k, (spr, wx, y, par, jit) in enumerate(self.items):
            x = wx - c * par + st["x"]
            if x + spr.w / 2 < -40 or x - spr.w / 2 > W + 40:
                continue
            jx = jy = jr = 0.0
            if jit:
                jx = (movie._rand(self.id, k, fj, "x") - 0.5) * 1.6 * jit
                jy = (movie._rand(self.id, k, fj, "y") - 0.5) * 1.6 * jit
                jr = (movie._rand(self.id, k, fj, "r") - 0.5) * 0.5 * jit
            if jit == 0 and spr.shadow is None:
                gfx.paste_clip(canvas, spr.img, round(x - spr.w / 2 + movie.M), round(y + st["y"] - spr.h / 2 + movie.M))
            else:
                movie._draw_cached(canvas, spr, x + jx + movie.M, y + st["y"] + jy + movie.M, 1.0, jr, 0.0,
                                   self.shadow)


def world(sc, items, cam, at=None, until=None, z=0, shadow=True):
    e = World(sc, items, cam, at=sc.now() if at is None else at, until=until, z=z, shadow=shadow)
    sc.elements.append(e)
    return e


def tiles(spr, x0, x1, y, parallax=1.0):
    """repeat a tile sprite from world x0 to x1 (centres)"""
    out = []
    x = x0
    while x < x1:
        out.append((spr, x + spr.w / 2, y, parallax, 0.0))
        x += spr.w - 2
    return out


# ----------------------------------------------------------------------------
# cards and on-screen helpers
# ----------------------------------------------------------------------------
def title(sc, text, at=None, size=50, y=112, bg="cream", color="ink", border="pos", **kw):
    c = gfx.card(text, size=size, font_name="body9", bg=bg, color=color, pad=(40, 12), border=(border, 4),
                 seed=_seed(text) + 5, max_w=1600)
    rot = ((_seed(text) % 100) / 100 - 0.5) * 1.6
    return sc.add(c, W / 2, y, at=sc.now() if at is None else at, enter="drop", rot=rot, **kw)


def fcard(lines, size=48, color="ink", bg="cream", border=None, pad=(40, 22), align="c", gap=0.28, seed=None,
          min_w=0, rough=0.8):
    """paper card with one formula/text line per entry (formula mini-syntax; use \\t{} for words)."""
    if isinstance(lines, str):
        lines = [lines]
    imgs = [formula(src, size, color) for src in lines]
    g = int(size * gap)
    tw = max(i.width for i in imgs)
    th = sum(i.height for i in imgs) + g * (len(imgs) - 1)
    cw = max(min_w, tw + 2 * pad[0])
    ch = th + 2 * pad[1]
    cv = Canvas(cw, ch)
    cv.rect(2, 2, cw - 2, ch - 2, fill=bg)
    if border:
        bc, bw = border
        cv.rect(2 + bw * 1.6, 2 + bw * 1.6, cw - 2 - bw * 1.6, ch - 2 - bw * 1.6, outline=bc, width=bw)
    base = paperize(cv.result(), seed=_seed("|".join(lines)) if seed is None else seed, rough=rough, texture=7)
    y = pad[1]
    for im in imgs:
        x = {"c": (cw - im.width) // 2, "l": pad[0], "r": cw - pad[0] - im.width}[align]
        base.alpha_composite(im, dest=(int(x), int(y)))
        y += im.height + g
    return Sprite(base, shadow_blur=5)


def tabbed(body, head, head_bg="pos", head_color="cream", head_size=34, seed=None):
    """glue a coloured tab (title) on the top-left corner of a card"""
    from . import kit
    tab = gfx.card(head, size=head_size, font_name="body9", bg=head_bg, color=head_color, pad=(22, 6),
                   seed=_seed(head) + 2 if seed is None else seed)
    return kit.compose([(body, 0, 0), (tab, -body.vw / 2 + tab.vw / 2 + 26, -body.vh / 2 - tab.vh / 2 + 18, -3)])


def def_card(head, lines, head_bg="pos", size=42, border=None, head_color="cream", **kw):
    return tabbed(fcard(lines, size=size, border=border, **kw), head, head_bg=head_bg, head_color=head_color)


def say_card(text, size=44, bg="cream", color="ink", border=None, max_w=1100, font_name="body9", **kw):
    return gfx.card(text, size=size, font_name=font_name, bg=bg, color=color, max_w=max_w, border=border,
                    pad=(36, 16), seed=_seed(text), hl="pos", **kw)


def bubble(text, size=44, tail="center", seed=None, font_name="body9"):
    return greek.bubble(text, size=size, font_name=font_name, tail=tail, seed=_seed(text) if seed is None else seed,
                        pad=(30, 18))


def countdown(sc, t0, secs=3, x=W - 170, y=190, r=62, color="pos", sound=True):
    """motion-graphics ring that empties in `secs` seconds (time for the viewer to think)."""
    def fn(L, t):
        p = clamp01((t - t0) / secs)
        n = max(1, int(math.ceil(secs - (t - t0) - 1e-6)))
        L.circle(x, y, r + 10, fill="cream", alpha=0.92)
        L.circle(x, y, r, stroke=(220, 204, 184), width=12)
        if p < 1:
            L.arc(x, y, r, -90, -90 + 360 * (1 - p), color, 12)
        L.stamp(formula(r"\b{%d}" % n if p < 1 else r"\b{¡Ya!}", 52 if p < 1 else 34, "ink"), x, y + 2)
    e = mg(sc, fn, at=t0, until=t0 + secs + 0.35, z=9)
    if sound:
        sfx_ticks(sc, t0, t0 + secs, 0.5, 0.045)
    return e


def quiz(sc, question, secs=3.5, x=W / 2, y=250, size=46, max_w=1300, head="COMPRUEBA", lead=None):
    """'COMPRUEBA' card with a question; the narration should read it before calling this.
    Returns the time at which the answer can be revealed."""
    q = tabbed(say_card(question, size=size, max_w=max_w, border=("mustard", 4)), head, head_bg="mustard",
               head_color="ink")
    t = sc.now() if lead is None else lead
    e = sc.add(q, x, y, at=t, enter="drop", rot=-0.8)
    sc.jingle(t, "fis_quiz", gain=0.3)
    return e, q


def think(sc, secs=3.5, **kw):
    """pause the narration and show the countdown; returns the reveal time"""
    t0 = sc.now()
    countdown(sc, t0, secs, **kw)
    sc.wait(secs + 0.25)
    sc.jingle(sc.now() - 0.1, "fis_ding", gain=0.32)
    return sc.now()


def axes(L, o, x_end=None, y_end=None, color="ink", width=5, labels=("X", "Y"), origin="O", ticks=None,
         tick_labels=False, alpha=1.0, lab_size=40, x_neg=0, y_neg=0):
    """X–Y axes with arrow tips. o = origin (screen); x_end / y_end = screen coordinate of the tips.
    ticks = (pixels per unit, step) draws ticks along X (and Y if y_end)."""
    ox, oy = o
    if x_end is not None:
        L.arrow((ox - x_neg, oy), (x_end, oy), color, width=width, head=width * 4.2, alpha=alpha)
        if labels and labels[0]:
            L.stamp(formula(labels[0], lab_size, color), x_end - 8, oy + 34, "rm", alpha=alpha)
    if y_end is not None:
        L.arrow((ox, oy + y_neg), (ox, y_end), color, width=width, head=width * 4.2, alpha=alpha)
        if labels and len(labels) > 1 and labels[1]:
            L.stamp(formula(labels[1], lab_size, color), ox - 26, y_end + 14, "rm", alpha=alpha)
    if origin:
        L.stamp(formula(origin, lab_size * 0.9, color), ox - 14, oy + 30, "rm", alpha=alpha)
    if ticks:
        ppu, step = ticks
        k = step
        while x_end is not None and ox + k * ppu < x_end - 30:
            xx = ox + k * ppu
            L.line([(xx, oy - 9), (xx, oy + 9)], color, 3, alpha=alpha)
            if tick_labels:
                L.stamp(formula(r"\t{%g}" % k, lab_size * 0.62, color), xx, oy + 30, "c", alpha=alpha)
            k += step
        k = step
        while y_end is not None and oy - k * ppu > y_end + 30:
            yy = oy - k * ppu
            L.line([(ox - 9, yy), (ox + 9, yy)], color, 3, alpha=alpha)
            if tick_labels:
                L.stamp(formula(r"\t{%g}" % k, lab_size * 0.62, color), ox - 30, yy, "c", alpha=alpha)
            k += step


def vlabel(L, p0, p1, src, size=40, color="ink", side=1, off=30, alpha=1.0, plate=True):
    """put a label next to the middle of segment p0-p1 (side=+1 left of direction, -1 right)."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy) or 1
    nx, ny = dy / n * side, -dx / n * side
    img = tag_img(src, size, color) if plate else formula(src, size, color)
    L.stamp(img, mx + nx * off, my + ny * off, "c", alpha=alpha)


# ----------------------------------------------------------------------------
# a cut-paper map of the Iberian Peninsula (for the "material point" example)
# ----------------------------------------------------------------------------
IBERIA = [(-1.78, 43.37), (-2.0, 43.32), (-2.95, 43.42), (-3.8, 43.47), (-4.5, 43.42), (-5.7, 43.56), (-6.3, 43.57),
          (-7.0, 43.55), (-7.7, 43.78), (-8.4, 43.4), (-9.0, 43.2), (-9.3, 42.9), (-8.9, 42.4), (-8.85, 41.9),
          (-8.75, 41.2), (-8.65, 40.6), (-9.0, 39.8), (-9.4, 39.35), (-9.5, 38.75), (-8.9, 38.5), (-8.85, 37.95),
          (-8.95, 37.0), (-7.95, 37.0), (-7.4, 37.18), (-6.95, 37.2), (-6.35, 36.8), (-6.3, 36.5), (-5.95, 36.2),
          (-5.6, 36.0), (-5.35, 36.15), (-4.9, 36.5), (-4.4, 36.72), (-3.5, 36.72), (-2.9, 36.75), (-2.2, 36.73),
          (-1.9, 37.0), (-1.6, 37.4), (-0.98, 37.6), (-0.7, 37.65), (-0.75, 38.0), (-0.48, 38.34), (-0.13, 38.54),
          (0.2, 38.75), (-0.18, 38.97), (-0.33, 39.45), (-0.27, 39.68), (-0.04, 39.98), (0.4, 40.36), (0.87, 40.7),
          (1.25, 41.1), (2.17, 41.38), (2.8, 41.7), (3.2, 41.95), (3.3, 42.32), (3.17, 42.43), (2.5, 42.35),
          (1.7, 42.5), (0.7, 42.8), (0.0, 42.7), (-0.7, 42.9), (-1.4, 43.05)]
PT_BORDER = [(-8.85, 41.9), (-8.16, 42.05), (-7.2, 41.9), (-6.6, 41.95), (-6.2, 41.6), (-6.85, 41.05), (-6.85, 40.3),
             (-7.0, 39.68), (-7.5, 39.6), (-7.2, 38.75), (-7.0, 38.2), (-7.45, 37.55), (-7.4, 37.18)]
AVE_ROUTE = [(-3.70, 40.42), (-3.75, 40.1), (-3.82, 39.6), (-3.93, 38.99), (-4.11, 38.69), (-4.4, 38.3),
             (-4.78, 37.89), (-5.3, 37.62), (-5.98, 37.39)]
CITIES = {"Madrid": (-3.70, 40.42), "Sevilla": (-5.98, 37.39), "Ciudad Real": (-3.93, 38.99),
          "Córdoba": (-4.78, 37.89)}


@functools.lru_cache(maxsize=2)
def iberia_map(width=900, seed=140):
    lon0, lon1, lat0, lat1 = -9.9, 3.7, 35.7, 44.1
    c = math.cos(math.radians(40))
    k = width / ((lon1 - lon0) * c)
    height = (lat1 - lat0) * k

    def P(lon, lat):
        return (lon - lon0) * c * k, (lat1 - lat) * k

    i0 = IBERIA.index((-8.85, 41.9))
    i1 = IBERIA.index((-7.4, 37.18))
    portugal = IBERIA[i0:i1 + 1] + PT_BORDER[::-1][1:-1]

    def land(cv):
        cv.poly([P(*q) for q in IBERIA], fill="paper2")

    def pt(cv):
        cv.poly([P(*q) for q in portugal], fill="cream")
        for q in ((-6.0, 39.0), (-4.5, 41.5)):
            pass
        # a few windmills of La Mancha
    spr = _layered(int(width), int(height), [land, pt], seed=seed, rough=0.6, shadow_blur=6)
    pad = spr.pad

    def project(lon, lat):
        x, y = P(lon, lat)
        return x - width / 2, y - height / 2
    return spr, project


@functools.lru_cache(maxsize=8)
def ruler_piece(length_px, ppu=80, units=None, seed=150, h=70, color="space_l", edge="top"):
    """a paper ruler: big ticks every ppu px (numbered), small ticks every ppu/10; the zero is 30 px from
    the left end; edge = side of the ticks"""
    units = units or int(length_px // ppu)
    w = int(length_px + 60)

    def draw(cv):
        cv.rect(0, 0, w, h, fill=color, radius=6)
        for k in range(units * 10 + 1):
            x = 30 + k * ppu / 10
            ln = h * (0.5 if k % 10 == 0 else 0.32 if k % 5 == 0 else 0.2)
            y0, y1 = (0, ln) if edge == "top" else (h - ln, h)
            cv.line([(x, y0), (x, y1)], "ink", 3 if k % 10 == 0 else 1.6)
    cv = Canvas(w, h)
    draw(cv)
    img = paperize(cv.result(), seed=seed, rough=0.5, texture=6)
    d = ImageDraw.Draw(img)
    f = font("body9", 26)
    for k in range(units + 1):
        x = 30 + k * ppu
        d.text((x, h * (0.58 if edge == "top" else 0.36)), str(k), font=f, fill=rgb("ink") + (255,), anchor="mm")
    return Sprite(img, shadow_blur=5)


@functools.lru_cache(maxsize=16)
def dot_piece(r=16, color="pos", seed=160, ring="ink"):
    d = int(2 * r + 8)

    def draw(cv):
        cv.circle(d / 2, d / 2, r + 3, fill=ring)
        cv.circle(d / 2, d / 2, r, fill=color)
    return _piece(d, d, draw, seed=seed, rough=0.3)


# ----------------------------------------------------------------------------
# geometry helpers for paths
# ----------------------------------------------------------------------------
class Path:
    """polyline with arc-length parametrisation (screen coordinates)"""

    def __init__(self, pts):
        self.pts = [tuple(map(float, p)) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.length = self.cum[-1]

    def at(self, u):
        """point at fraction u (0..1) of the length"""
        s = clamp01(u) * self.length
        import bisect
        i = min(len(self.pts) - 2, max(0, bisect.bisect_right(self.cum, s) - 1))
        seg = self.cum[i + 1] - self.cum[i] or 1.0
        f = (s - self.cum[i]) / seg
        a, b = self.pts[i], self.pts[i + 1]
        return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f

    def upto(self, u):
        s = clamp01(u) * self.length
        out = [self.pts[0]]
        for p, c in zip(self.pts[1:], self.cum[1:]):
            if c < s:
                out.append(p)
            else:
                break
        out.append(self.at(u))
        return out

    def between(self, u0, u1):
        s0, s1 = clamp01(u0) * self.length, clamp01(u1) * self.length
        out = [self.at(u0)]
        for p, c in zip(self.pts[1:], self.cum[1:]):
            if s0 < c < s1:
                out.append(p)
        out.append(self.at(u1))
        return out

    def tangent(self, u, eps=1e-3):
        a, b = self.at(u - eps), self.at(u + eps)
        d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return (b[0] - a[0]) / d, (b[1] - a[1]) / d


def bezier(p0, p1, p2, p3, n=60):
    out = []
    for k in range(n + 1):
        t = k / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def smooth(pts, n=12):
    """Catmull-Rom through the given points"""
    pts = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-2])
    return out


# ----------------------------------------------------------------------------
# more props: Ana walking, street, stopwatch, speedometer, track, cars, roads
# ----------------------------------------------------------------------------
def _limb(cv, x, y, length, width, angle, color, end_r=None):
    """rounded bar from (x, y) going `length` px in direction `angle` (degrees, 0 = down, + = forwards/right)"""
    a = math.radians(angle)
    dx, dy = math.sin(a), math.cos(a)
    nx, ny = dy, -dx
    w = width / 2
    x2, y2 = x + dx * length, y + dy * length
    cv.poly([(x + nx * w, y + ny * w), (x2 + nx * w, y2 + ny * w), (x2 - nx * w, y2 - ny * w),
             (x - nx * w, y - ny * w)], fill=color)
    cv.circle(x, y, w, fill=color)
    cv.circle(x2, y2, end_r or w, fill=color)
    return x2, y2


WALK = [(-26, 22, 24, -20), (-10, 8, 8, -6), (22, -26, -20, 24), (8, -10, -6, 8)]  # (leg1, leg2, arm1, arm2)


@functools.lru_cache(maxsize=16)
def ana_walk(pose=0, face=1, h=230, seed=180):
    """Ana in profile, walking (replacement animation: 4 poses). face=+1 right, -1 left."""
    s = h / 230.0
    w = int(150 * s)
    hh = int(h + 10 * s)
    l1, l2, a1, a2 = WALK[pose % 4]
    hip = (w / 2, 132 * s)
    sh = (w / 2, 64 * s)

    def back(cv):
        x, y = _limb(cv, hip[0], hip[1], 88 * s, 22 * s, l2, "train_d")
        cv.ellipse(x + 8 * s, y + 4 * s, 15 * s, 8 * s, fill="ink")
        _limb(cv, sh[0], sh[1], 66 * s, 16 * s, a2, "kraft_d", end_r=9 * s)

    def body(cv):
        cv.rect(w / 2 - 25 * s, 50 * s, w / 2 + 25 * s, 140 * s, fill="mustard", radius=16 * s)

    def front(cv):
        x, y = _limb(cv, hip[0], hip[1], 88 * s, 22 * s, l1, "train_d")
        cv.ellipse(x + 8 * s, y + 4 * s, 15 * s, 8 * s, fill="ink")
        x, y = _limb(cv, sh[0], sh[1], 66 * s, 17 * s, a1, "mustard")
        cv.circle(x, y, 9 * s, fill="skin")
        _ana_profile_head(cv, w / 2 + 4 * s, 30 * s, 1.0 * s, face=1)
    spr = _layered(w, hh, [back, body, front], seed=seed + pose, rough=0.45, shadow_blur=4)
    if face < 0:
        spr = Sprite(spr.img.transpose(Image.FLIP_LEFT_RIGHT), shadow_blur=4, pad=0)
    return spr


@functools.lru_cache(maxsize=4)
def house_piece(seed=190):
    w, h = 300, 290

    def walls(cv):
        cv.rect(30, 110, w - 30, h, fill="cream")
        cv.poly([(10, 120), (w / 2, 14), (w - 10, 120)], fill="train")
        cv.rect(w - 90, 30, w - 60, 90, fill="brown")

    def details(cv):
        cv.rect(w / 2 - 34, h - 112, w / 2 + 34, h, fill="brown", radius=6)
        cv.circle(w / 2 + 20, h - 56, 5, fill="space_l")
        for x in (70, w - 70):
            cv.rect(x - 30, 150, x + 30, 205, fill="glass", radius=4)
            cv.line([(x, 150), (x, 205)], "brown", 4)
    return _layered(w, h, [walls, details], seed=seed, rough=0.5)


@functools.lru_cache(maxsize=4)
def shop_piece(name="PANADERÍA", icon_name="bread", awning="mustard", seed=200, w=330):
    h = 300
    t = gfx.render_rich(name, "body9", 34, 900, "ink")

    def walls(cv):
        cv.rect(16, 60, w - 16, h, fill="cream")
        cv.rect(8, 40, w - 8, 106, fill="kraft_d", radius=8)

    def details(cv):
        n = 7
        for i in range(n):
            x0 = 16 + i * (w - 32) / n
            cv.poly([(x0, 106), (x0 + (w - 32) / n, 106), (x0 + (w - 32) / n, 140), (x0, 140)],
                    fill=awning if i % 2 == 0 else "cream")
        cv.rect(36, 160, w / 2 + 20, h - 26, fill="glass", radius=6)
        cv.rect(w / 2 + 40, 160, w - 36, h, fill="brown", radius=6)
    spr = _layered(w, h, [walls, details], seed=seed, rough=0.5)
    img = spr.img.copy()
    p = spr.pad
    img.alpha_composite(t, dest=(int(p + (w - t.width) / 2), int(p + 73 - t.height / 2)))
    ic = greek.icon(icon_name, 90, "kraft_d")
    img.alpha_composite(ic, dest=(int(p + 36 + (w / 2 + 20 - 36 - 90) / 2), int(p + 175)))
    return Sprite(img, shadow_blur=5, pad=0)


@functools.lru_cache(maxsize=4)
def stopwatch_piece(d=230, seed=210):
    w, h = d, int(d * 1.18)
    cx, cy, r = w / 2, h - d / 2, d / 2 - 6

    def body(cv):
        cv.rect(cx - 16, 4, cx + 16, 34, fill="ink", radius=6)
        cv.rect(cx - 28, 0, cx + 28, 16, fill="acc", radius=6)
        cv.circle(cx, cy, r, fill="ink")
        cv.circle(cx, cy, r - 12, fill="cream")

    def ticks(cv):
        for k in range(60):
            a = math.radians(k * 6 - 90)
            r0 = r - 22 if k % 5 == 0 else r - 18
            cv.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r - 13),
                                                                       cy + math.sin(a) * (r - 13))],
                    "ink", 4 if k % 5 == 0 else 1.6)
    spr = _layered(w, h, [body, ticks], seed=seed, rough=0.4)
    return spr, (0, h / 2 - d / 2)   # offset of the dial centre from the sprite centre


def stopwatch_hand(L, cx, cy, d, t, color="acc"):
    """motion-graphics hand: one turn every 10 s (we only need a few seconds)"""
    r = d / 2 - 30
    a = math.radians(t * 36 - 90)
    L.line([(cx - math.cos(a) * 18, cy - math.sin(a) * 18), (cx + math.cos(a) * r, cy + math.sin(a) * r)], color, 6)
    L.circle(cx, cy, 10, fill="ink")


@functools.lru_cache(maxsize=4)
def speedo_piece(d=260, vmax=10, step=2, seed=220, unit=None):
    w, h = d, int(d * 0.72)
    cx, cy, r = w / 2, d / 2 + 6, d / 2 - 6

    def body(cv):
        cv.poly(greek.ellipse_pts(cx, cy, r, r, a0=180, a1=360) + [(cx + r, cy + 34), (cx - r, cy + 34)], fill="ink")
        cv.poly(greek.ellipse_pts(cx, cy, r - 12, r - 12, a0=180, a1=360) + [(cx + r - 12, cy + 22),
                                                                            (cx - r + 12, cy + 22)], fill="cream")

    def ticks(cv):
        n = vmax * 2
        for k in range(n + 1):
            a = math.radians(180 + 180 * k / n)
            big = k % (2 * step) == 0 if step >= 1 else True
            r0 = r - 34 if big else r - 26
            cv.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r - 16),
                                                                       cy + math.sin(a) * (r - 16))],
                    "ink", 4 if big else 2)
        cv.poly(greek.ellipse_pts(cx, cy, r - 16, r - 16, a0=315, a1=360) + [(cx, cy)], fill=(244, 170, 150))
    spr = _layered(w, h, [body, ticks], seed=seed, rough=0.4)
    img = spr.img.copy()
    dd = ImageDraw.Draw(img)
    f = font("body9", int(d * 0.085))
    p = spr.pad
    for v in range(0, vmax + 1, step):
        a = math.radians(180 + 180 * v / vmax)
        dd.text((p + cx + math.cos(a) * (r - 58), p + cy + math.sin(a) * (r - 58)), str(v), font=f,
                fill=rgb("ink") + (255,), anchor="mm")
    if unit:
        dd.text((p + cx, p + cy - r * 0.32), unit, font=font("body9", int(d * 0.07)), fill=rgb("ink") + (255,),
                anchor="mm")
    return Sprite(img, shadow_blur=5, pad=0), (0, -(h / 2) + d / 2 + 6)


def speedo_needle(L, cx, cy, d, v, vmax=10, color="vel"):
    r = d / 2 - 40
    a = math.radians(180 + 180 * clamp01(v / vmax))
    L.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], color, 7)
    L.circle(cx, cy, 11, fill="ink")


@functools.lru_cache(maxsize=4)
def track_piece(w=760, h=380, seed=230):
    def draw(cv):
        r = h / 2
        cv.rect(0, 0, w, h, fill="train", radius=r)
        cv.rect(70, 70, w - 70, h - 70, fill="grass", radius=r - 70)
        for k in (1, 2):
            inset = 70 * k / 3
            cv.rect(inset, inset, w - inset, h - inset, outline="cream", width=3, radius=r - inset)
        cv.rect(w / 2 - 4, h - 70, w / 2 + 4, h, fill="cream")
    return _piece(w, h, draw, seed=seed, rough=0.4)


@functools.lru_cache(maxsize=8)
def car_top(color="mustard", seed=240, L=200):
    """car seen from above, facing right (+x)"""
    W_ = L * 0.5
    w, h = int(L + 20), int(W_ + 30)
    cx, cy = w / 2, h / 2

    def body(cv):
        for sx in (-1, 1):
            for sy in (-1, 1):
                cv.rect(cx + sx * L * 0.3 - 18, cy + sy * W_ * 0.5 - 8, cx + sx * L * 0.3 + 18, cy + sy * W_ * 0.5 + 8,
                        fill="ink", radius=4)
        cv.rect(cx - L / 2, cy - W_ / 2, cx + L / 2, cy + W_ / 2, fill=color, radius=W_ * 0.32)

    def top(cv):
        cv.poly([(cx + L * 0.12, cy - W_ * 0.36), (cx + L * 0.26, cy - W_ * 0.3), (cx + L * 0.26, cy + W_ * 0.3),
                 (cx + L * 0.12, cy + W_ * 0.36)], fill=(70, 62, 58))
        cv.rect(cx - L * 0.22, cy - W_ * 0.34, cx + L * 0.1, cy + W_ * 0.34, fill=(244, 204, 110), radius=12)
        cv.poly([(cx - L * 0.34, cy - W_ * 0.3), (cx - L * 0.24, cy - W_ * 0.34), (cx - L * 0.24, cy + W_ * 0.34),
                 (cx - L * 0.34, cy + W_ * 0.3)], fill=(70, 62, 58))
        for sy in (-1, 1):
            cv.ellipse(cx + L * 0.46, cy + sy * W_ * 0.3, 7, 9, fill="cream")
    return _layered(w, h, [body, top], seed=seed, rough=0.4, shadow_blur=5)


@functools.lru_cache(maxsize=4)
def road_piece(w=2000, h=220, seed=250, zebra_x=None, stop_x=None):
    def draw(cv):
        cv.rect(0, 0, w, h, fill="road")
        cv.rect(0, 10, w, 16, fill="cream")
        cv.rect(0, h - 16, w, h - 10, fill="cream")
        x = 20
        while x < w:
            cv.rect(x, h / 2 - 4, x + 60, h / 2 + 4, fill="cream")
            x += 110
        if zebra_x is not None:
            cv.rect(zebra_x - 70, 16, zebra_x + 70, h - 16, fill="road")
            for k in range(6):
                y0 = 24 + k * (h - 48) / 6
                cv.rect(zebra_x - 60, y0 + 4, zebra_x + 60, y0 + (h - 48) / 6 - 6, fill="cream")
        if stop_x is not None:
            cv.rect(stop_x - 6, h / 2 + 6, stop_x + 6, h - 16, fill="cream")
    cv = Canvas(w, h)
    draw(cv)
    return Sprite(paperize(cv.result(), seed=seed, rough=0.3, texture=8), shadow_blur=5)


@functools.lru_cache(maxsize=4)
def traffic_light(on="green", seed=260):
    w, h = 90, 230

    def draw(cv):
        cv.rect(w / 2 - 6, 150, w / 2 + 6, h, fill="ink")
        cv.rect(8, 0, w - 8, 160, fill="ink", radius=14)
        for k, c in enumerate(("acc", "mustard", "grass")):
            lit = {"red": 0, "amber": 1, "green": 2}[on] == k
            cv.circle(w / 2, 30 + k * 50, 19, fill=c if lit else (90, 80, 74))
    return _piece(w, h, draw, seed=seed, rough=0.35)


@functools.lru_cache(maxsize=4)
def roundabout_piece(R=300, lane=110, seed=270):
    d = int(2 * R + 40)
    c = d / 2

    def draw(cv):
        cv.circle(c, c, R, fill="road")
        cv.circle(c, c, R - 8, outline="cream", width=5)
        cv.circle(c, c, R - lane, fill="cream")
        cv.circle(c, c, R - lane - 10, fill="grass")
        for k in range(36):
            a0 = math.radians(k * 10)
            a1 = math.radians(k * 10 + 5)
            rr = R - lane / 2
            cv.line([(c + rr * math.cos(a0), c + rr * math.sin(a0)), (c + rr * math.cos(a1), c + rr * math.sin(a1))],
                    "cream", 5)
    spr = _piece(d, d, draw, seed=seed, rough=0.3)
    return spr


@functools.lru_cache(maxsize=4)
def tree_top(r=60, seed=280):
    d = int(2 * r + 10)
    return _piece(d, d, lambda cv: (cv.circle(d / 2, d / 2, r, fill="grass_d"),
                                    cv.circle(d / 2 - r * 0.3, d / 2 - r * 0.3, r * 0.45, fill="grass")), seed=seed)


@functools.lru_cache(maxsize=4)
def stone_piece(r=22, seed=290):
    d = int(2 * r + 8)
    return _piece(d, d, lambda cv: cv.ellipse(d / 2, d / 2, r, r * 0.86, fill=(150, 136, 122)), seed=seed, rough=0.5)


# ----------------------------------------------------------------------------
# narration: numbers and units read aloud in Spanish ("44,1 m" -> "cuarenta y cuatro coma uno metros")
# ----------------------------------------------------------------------------
_UNITS_ES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce",
             "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno",
             "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho",
             "veintinueve"]
_TENS_ES = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"}
_HUNDREDS_ES = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos",
                7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def es_int(n):
    """integer -> Spanish words (0 <= n < 10**9)"""
    n = int(n)
    if n < 30:
        return _UNITS_ES[n]
    if n < 100:
        t, u = divmod(n, 10)
        return _TENS_ES[t * 10] + ("" if u == 0 else " y " + _UNITS_ES[u])
    if n < 1000:
        h, r = divmod(n, 100)
        if n == 100:
            return "cien"
        return _HUNDREDS_ES[h] + ("" if r == 0 else " " + es_int(r))
    if n < 10 ** 6:
        th, r = divmod(n, 1000)
        head = "mil" if th == 1 else _apocope(es_int(th)) + " mil"
        return head + ("" if r == 0 else " " + es_int(r))
    m, r = divmod(n, 10 ** 6)
    head = "un millón" if m == 1 else _apocope(es_int(m)) + " millones"
    return head + ("" if r == 0 else " " + es_int(r))


def _apocope(words):
    """'uno' -> 'un', 'veintiuno' -> 'veintiún' (before a masculine noun)"""
    if words.endswith("veintiuno"):
        return words[:-len("veintiuno")] + "veintiún"
    if words.endswith("uno"):
        return words[:-3] + "un"
    return words


def es_number(s, masculine_noun=False):
    """'44,1' -> 'cuarenta y cuatro coma uno'; '0,05' -> 'cero coma cero cinco'"""
    neg = s[:1] in "−-"
    s = s.lstrip("−-")
    if "," in s or "." in s:
        a, b = re.split(r"[,.]", s, 1)
        dec = " ".join(_UNITS_ES[int(c)] for c in b) if b.startswith("0") else es_int(int(b))
        out = es_int(int(a)) + " coma " + dec
    else:
        out = es_int(int(s))
        if masculine_noun:
            out = _apocope(out)
    return ("menos " if neg else "") + out


_UNIT_WORDS = [("m/s²", "metro por segundo al cuadrado", "metros por segundo al cuadrado"),
               ("m/s2", "metro por segundo al cuadrado", "metros por segundo al cuadrado"),
               ("m/s", "metro por segundo", "metros por segundo"),
               ("km/h", "kilómetro por hora", "kilómetros por hora"),
               ("km", "kilómetro", "kilómetros"), ("min", "minuto", "minutos"), ("m", "metro", "metros"),
               ("s", "segundo", "segundos"), ("h", "hora", "horas")]
_NUM_RE = re.compile(r"(?<![\w,.])([−-]?\d+(?:[,.]\d+)?)(?:\s?(m/s²|m/s2|m/s|km/h|km|min|m|s|h)(?![\w/²]))?")


def _say_number(m):
    num, unit = m.group(1), m.group(2)
    if not unit:
        return es_number(num)
    sing, plur = next((a, b) for u, a, b in _UNIT_WORDS if u == unit)
    is_one = num.lstrip("−-") == "1"
    if unit == "h":
        words = es_number(num)
        if words.endswith("uno") and not ("," in num or "." in num):
            words = words[:-3] + "una"
        return f"{words} {sing if is_one else plur}"
    return f"{es_number(num, masculine_noun=True)} {sing if is_one else plur}"


SYMBOLS_SPOKEN = {
    "x₀": "equis cero", "v₀": "uve cero", "y₀": "i griega cero", "t₀": "te cero", "Δx": "delta equis",
    "Δt": "delta te", "Δv": "delta uve", "Δy": "delta i griega", "xA": "equis a", "xB": "equis be",
    "v²": "uve al cuadrado", "t²": "te al cuadrado", "÷": " entre ", "×": " por ", "·": " por ", "≈": " aproximadamente ",
}


def enable_spoken_numbers():
    """make the narrator read numbers, units and a few symbols in words (display text keeps the digits)"""
    for k, v in SYMBOLS_SPOKEN.items():
        movie.PRONOUNCE[re.escape(k)] = v
    movie.PRONOUNCE[r"«|»"] = ""
    movie.PRONOUNCE[_NUM_RE.pattern] = _say_number


# ----------------------------------------------------------------------------
# graphs (x-t, v-t, a-t) drawn as motion graphics, plotted live while the mobile moves
# ----------------------------------------------------------------------------
class Graph:
    """Screen box: left x0, bottom y0 (of the plotting area), width w, height h.
    Data: t in [0, tmax], value in [vmin, vmax]."""

    def __init__(self, x0, y0, w, h, tmax, vmin, vmax, tlabel=r"t\;\t{(s)}", vlabel=r"x\;\t{(m)}", tstep=1, vstep=5,
                 tlab_every=1, vlab_every=1, color="ink", size=30):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.tmax, self.vmin, self.vmax = tmax, vmin, vmax
        self.tlabel, self.vlabel = tlabel, vlabel
        self.tstep, self.vstep = tstep, vstep
        self.tlab_every, self.vlab_every = tlab_every, vlab_every
        self.color, self.size = color, size

    def X(self, t):
        return self.x0 + t / self.tmax * self.w

    def Y(self, v):
        return self.y0 - (v - self.vmin) / (self.vmax - self.vmin) * self.h

    def P(self, t, v):
        return self.X(t), self.Y(v)

    @property
    def zero_y(self):
        return self.Y(min(max(0.0, self.vmin), self.vmax))

    def axes(self, L, g=1.0, grid=True, alpha=1.0):
        """g: drawing progress 0..1"""
        if g <= 0:
            return
        c, sz = self.color, self.size
        top = self.y0 - self.h - 30
        right = self.x0 + self.w + 30
        zy = self.zero_y
        if grid and g >= 1:
            k = self.tstep
            while k <= self.tmax + 1e-9:
                L.line([(self.X(k), self.y0), (self.X(k), self.y0 - self.h)], (196, 164, 130), 1.4, alpha=0.55 * alpha)
                k += self.tstep
            v = math.ceil(self.vmin / self.vstep) * self.vstep
            while v <= self.vmax + 1e-9:
                if abs(v) > 1e-9:
                    L.line([(self.x0, self.Y(v)), (self.x0 + self.w, self.Y(v))], (196, 164, 130), 1.4,
                           alpha=0.55 * alpha)
                v += self.vstep
        L.arrow((self.x0, self.y0 + (12 if self.vmin >= 0 else 0)), (self.x0, self.y0 - (self.y0 - top) * g), c, 4.5,
                head=20, alpha=alpha)
        L.arrow((self.x0 - 12, zy), (self.x0 - 12 + (right - self.x0 + 12) * g, zy), c, 4.5, head=20, alpha=alpha)
        if g < 1:
            return
        L.stamp(formula(self.vlabel, sz), self.x0 + 12, top - 6, "lb", alpha=alpha)
        L.stamp(formula(self.tlabel, sz), right + 8, zy, "lm", alpha=alpha)
        k, i = self.tstep, 1
        while k <= self.tmax + 1e-9:
            L.line([(self.X(k), zy - 7), (self.X(k), zy + 7)], c, 2.5, alpha=alpha)
            if i % self.tlab_every == 0:
                L.stamp(formula(r"\t{%s}" % _fmt(k), sz * 0.8), self.X(k), zy + 24, alpha=alpha)
            k += self.tstep
            i += 1
        v = math.ceil(self.vmin / self.vstep) * self.vstep
        i = 0
        while v <= self.vmax + 1e-9:
            if abs(v) > 1e-9:
                L.line([(self.x0 - 7, self.Y(v)), (self.x0 + 7, self.Y(v))], c, 2.5, alpha=alpha)
                if round(v / self.vstep) % self.vlab_every == 0:
                    L.stamp(formula(r"\t{%s}" % _fmt(v), sz * 0.8), self.x0 - 14, self.Y(v), "rm", alpha=alpha)
            v += self.vstep
            i += 1
        L.stamp(formula(r"\t{0}", sz * 0.8), self.x0 - 14, zy + 16, "rm", alpha=alpha)

    def curve(self, L, f, t0, t1, color, width=6, n=90, dash=None, alpha=1.0):
        if t1 <= t0:
            return []
        pts = [self.P(t0 + (t1 - t0) * k / n, f(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]
        L.line(pts, color, width, dash=dash, alpha=alpha)
        return pts

    def dot(self, L, t, v, color="ink", r=8, alpha=1.0):
        L.circle(*self.P(t, v), r, fill=color, stroke="cream", width=2, alpha=alpha)

    def guides(self, L, t, v, color="ink", tlab=None, vlab=None, alpha=1.0, size=None):
        """dashed lines from the point to both axes, with optional labels"""
        sz = size or self.size * 0.85
        px, py = self.P(t, v)
        zy = self.zero_y
        L.line([(px, py), (px, zy)], color, 2.5, dash=[8, 7], alpha=alpha)
        L.line([(px, py), (self.x0, py)], color, 2.5, dash=[8, 7], alpha=alpha)
        if tlab:
            L.stamp(tag_img(tlab, sz, color), px, zy + (62 if v >= 0 else -44), alpha=alpha)
        if vlab:
            L.stamp(tag_img(vlab, sz, color), self.x0 + 8, py - 24, "lm", alpha=alpha)

    def slope(self, L, f, t1, t2, color="ink", g=1.0, dt_lab=None, dv_lab=None, size=None):
        """slope triangle between t1 and t2 under/over the line"""
        sz = size or self.size * 0.9
        a, b = self.P(t1, f(t1)), self.P(t2, f(t2))
        c = (b[0], a[1])
        if g <= 0:
            return
        L.line([a, lerp2(a, c, min(1, g * 2))], color, 4)
        if g > 0.5:
            L.line([c, lerp2(c, b, (g - 0.5) * 2)], color, 4)
        if g >= 1:
            if dt_lab:
                L.stamp(tag_img(dt_lab, sz, color), (a[0] + c[0]) / 2, a[1] + (30 if b[1] < a[1] else -30))
            if dv_lab:
                L.stamp(tag_img(dv_lab, sz, color), c[0] + 16, (c[1] + b[1]) / 2, "lm")

    def area(self, L, f, t0, t1, fill, alpha=1.0, n=60, base=0.0):
        if t1 <= t0:
            return
        pts = [self.P(t0, base)] + [self.P(t0 + (t1 - t0) * k / n, f(t0 + (t1 - t0) * k / n)) for k in range(n + 1)] + \
              [self.P(t1, base)]
        L.poly(pts, fill=fill, alpha=alpha)


def _fmt(v):
    if abs(v - round(v)) < 1e-9:
        return "%d" % round(v)
    return ("%g" % v).replace(".", ",")


# ----------------------------------------------------------------------------
# stroboscopic photos ("una foto cada segundo") and other helpers
# ----------------------------------------------------------------------------
_GHOSTS = {}


def ghost(spr, alpha=0.35):
    key = (id(spr), round(alpha, 2))
    g = _GHOSTS.get(key)
    if g is None:
        img = spr.img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
        g = Sprite(img, shadow_blur=3, pad=0, shadow=False)
        _GHOSTS[key] = (g, spr)
        return g
    return g[0]


def put(sc, spr, x, y, at, enter="drop", rot=None, **kw):
    if rot is None:
        rot = ((_seed(f"{x:.0f}|{y:.0f}") % 100) / 100 - 0.5) * 2.4
    return sc.add(spr, x, y, at=at, enter=enter, rot=rot, **kw)


def scn(mv, name, **kw):
    kw.setdefault("transition", "cut")
    kw.setdefault("sweep", True)
    return mv.scene(name, **kw)


def board(sc, lines, x, y, size=46, gap=16, align="l", write=0.55, z=6, color="ink", until=None):
    """Write formula lines one under another, each appearing at its own time with a 'being written' reveal.
    lines = [(src, t)] ; x = left edge (align 'l') or centre ('c'); y = top of the first line.
    Returns the list of y centres (to place marks next to the lines)."""
    imgs = [formula(src, size, color) for src, _ in lines]
    ys = []
    yy = y
    for im in imgs:
        ys.append(yy + im.height / 2)
        yy += im.height + gap

    def fn(L, t):
        for (src, t0), im, yc in zip(lines, imgs, ys):
            p = prog(t, t0, write, "lin")
            if p <= 0:
                continue
            L.stamp(im, x if align == "l" else x - im.width / 2, yc, "lm", reveal=p)
    mg(sc, fn, at=min(t for _, t in lines), until=until, z=z, shadow=False)
    return ys


def sheet(w, h, seed=0, lines=True, color="cream"):
    """a sheet of lined notebook paper (as a paper piece) to write the solutions on"""
    def draw(cv):
        cv.rect(0, 0, w, h, fill=color)
        if lines:
            for yy in range(70, int(h) - 20, 56):
                cv.line([(24, yy), (w - 24, yy)], (226, 206, 180), 2)
            cv.line([(70, 10), (70, h - 10)], (236, 160, 140), 2.5)
    return _piece(int(w), int(h), draw, seed=seed, rough=0.5, texture=6)


# ----------------------------------------------------------------------------
# more props: bicycle with rider, ball, building, Ana throwing
# ----------------------------------------------------------------------------
@functools.lru_cache(maxsize=32)
def bike_sprite(rider="ana", spin=0, face=1, h=250, seed=300):
    """side view of a bicycle with a rider; spin = 0..3 (wheel spokes rotated 22.5° each step)"""
    s = h / 250.0
    w = int(330 * s)
    hh = int(h + 40 * s)
    wr = 52 * s
    w1, w2 = (78 * s, hh - wr - 6 * s), (w - 78 * s, hh - wr - 6 * s)
    shirt, pants = ("mustard", "train_d") if rider == "ana" else ("grass", "kraft_d")
    frame_c = "acc" if rider == "ana" else "brown"

    def wheels(cv):
        for (cx, cy) in (w1, w2):
            cv.circle(cx, cy, wr, fill=None, outline="ink", width=7 * s)
            for k in range(4):
                a = math.radians(spin * 22.5 + k * 45)
                cv.line([(cx - math.cos(a) * wr * 0.9, cy - math.sin(a) * wr * 0.9),
                         (cx + math.cos(a) * wr * 0.9, cy + math.sin(a) * wr * 0.9)], (120, 110, 100), 2.4 * s)
            cv.circle(cx, cy, 7 * s, fill="ink")

    def frame(cv):
        seat = (w * 0.40, hh - 150 * s)
        crank = (w * 0.47, w1[1])
        head = (w * 0.72, hh - 160 * s)
        cv.line([w1, crank, seat, w1], frame_c, 7 * s)
        cv.line([crank, head, seat], frame_c, 7 * s)
        cv.line([head, w2], frame_c, 7 * s)
        cv.line([(head[0] - 6 * s, head[1] - 14 * s), (head[0] + 16 * s, head[1] - 22 * s)], "ink", 6 * s)
        cv.rect(seat[0] - 22 * s, seat[1] - 8 * s, seat[0] + 18 * s, seat[1] + 2 * s, fill="ink", radius=4 * s)
        cv.circle(*crank, 10 * s, fill="ink")

    def rider_back(cv):
        seat = (w * 0.40, hh - 150 * s)
        crank = (w * 0.47, w1[1])
        a = math.radians(spin * 90 + 180)
        foot = (crank[0] + math.cos(a) * 22 * s, crank[1] + math.sin(a) * 22 * s)
        cv.line([(seat[0] + 4 * s, seat[1] - 6 * s), ((seat[0] + foot[0]) / 2 + 26 * s, (seat[1] + foot[1]) / 2 - 8 * s),
                 foot], pants, 18 * s)

    def rider_front(cv):
        seat = (w * 0.40, hh - 150 * s)
        crank = (w * 0.47, w1[1])
        a = math.radians(spin * 90)
        foot = (crank[0] + math.cos(a) * 22 * s, crank[1] + math.sin(a) * 22 * s)
        knee = ((seat[0] + foot[0]) / 2 + 30 * s, (seat[1] + foot[1]) / 2 - 10 * s)
        cv.line([(seat[0] + 4 * s, seat[1] - 6 * s), knee, foot], pants, 19 * s)
        cv.ellipse(foot[0] + 6 * s, foot[1] + 4 * s, 14 * s, 7 * s, fill="ink")
        hip = (seat[0] + 2 * s, seat[1] - 14 * s)
        sh = (w * 0.56, hh - 222 * s)
        cv.line([hip, sh], shirt, 30 * s)
        hand = (w * 0.72 + 8 * s, hh - 178 * s)
        cv.line([sh, ((sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2 + 6 * s), hand], shirt, 13 * s)
        cv.circle(*hand, 7 * s, fill="skin")
        if rider == "ana":
            _ana_profile_head(cv, sh[0] + 14 * s, sh[1] - 34 * s, 0.95 * s, face=1)
        else:
            hx, hy = sh[0] + 14 * s, sh[1] - 34 * s
            r = 24 * s
            cv.circle(hx, hy, r, fill="skin")
            cv.poly(greek.ellipse_pts(hx - 2 * s, hy - 7 * s, r * 1.05, r * 0.85, a0=180, a1=360), fill="hair")
            cv.rect(hx - r, hy - 10 * s, hx - r * 0.5, hy + 6 * s, fill="hair")
            cv.circle(hx + 12 * s, hy - 1 * s, 3.4 * s, fill="ink")
            cv.poly([(hx + r * 0.8, hy - 2 * s), (hx + r + 6 * s, hy + 5 * s), (hx + r * 0.75, hy + 8 * s)], fill="skin")
    spr = _layered(w, hh, [rider_back, wheels, frame, rider_front], seed=seed + spin + (50 if rider != "ana" else 0),
                   rough=0.4, shadow_blur=4)
    if face < 0:
        spr = Sprite(spr.img.transpose(Image.FLIP_LEFT_RIGHT), shadow_blur=4, pad=0)
    return spr


def bike_at(rider, dist_px, face=1, h=250):
    """sprite of the bike for a travelled distance (wheels turn with the distance)"""
    wr = 52 * h / 250.0
    spin = int((dist_px / wr) / math.radians(22.5)) % 4
    return bike_sprite(rider, spin, face, h)


@functools.lru_cache(maxsize=8)
def ball_piece(r=26, color="acc", seed=310):
    d = int(2 * r + 8)

    def draw(cv):
        cv.circle(d / 2, d / 2, r, fill=color)
        cv.arc(d / 2, d / 2, r * 0.8, r * 0.8, 200, 320, "cream", max(2, r * 0.14))
        cv.arc(d / 2, d / 2, r * 0.8, r * 0.8, 20, 140, "cream", max(2, r * 0.14))
    return _piece(d, d, draw, seed=seed, rough=0.3)


@functools.lru_cache(maxsize=4)
def building_piece(w=300, h=640, floors=6, seed=320, color="cream", roof="train"):
    def body(cv):
        cv.rect(0, 30, w, h, fill=color)
        cv.rect(-6, 10, w + 6, 40, fill=roof)

    def windows(cv):
        fh = (h - 60) / floors
        for f in range(floors):
            y = 50 + f * fh
            for k in range(2):
                x = 40 + k * (w - 160) / 1 if False else (50 + k * (w - 150))
                cv.rect(x, y + fh * 0.22, x + 50, y + fh * 0.72, fill="glass", radius=4)
                cv.line([(x + 25, y + fh * 0.22), (x + 25, y + fh * 0.72)], "brown", 3)
        cv.rect(w / 2 - 34, h - 100, w / 2 + 34, h, fill="brown", radius=6)
    return _layered(w, h, [body, windows], seed=seed, rough=0.5)


@functools.lru_cache(maxsize=8)
def ana_arm_up(h=290, seed=63, face=1):
    """Ana front view with the right arm raised (to throw or drop a ball)"""
    w = int(h * 0.62)

    def draw(cv):
        _person_front(cv, w / 2, 4, h, shirt="mustard", pants="train_d", girl=True)
        s = h / 300.0
        cx = w / 2
        cv.poly([(cx + 40 * s, 100 * s), (cx + 56 * s, 96 * s), (cx + 74 * s, 10 * s), (cx + 58 * s, 6 * s)],
                fill="mustard")
        cv.circle(cx + 66 * s, 6 * s, 10 * s, fill="skin")
    spr = _piece(w, h + 12, draw, seed=seed, rough=0.5)
    return spr


def step_list(sc, steps, x, y, at_times, size=34, w=520, done_times=None, z=5):
    """a vertical checklist (the exam method). Each step appears at its time; the current one is highlighted
    and gets a check mark when done."""
    imgs = [text_img(t, size, "ink", "body9", 700, "left") for t in steps]
    imgs_on = [text_img(t, size, "cream", "body9", 700, "left") for t in steps]

    def fn(L, t):
        yy = y
        for k, (im, im_on) in enumerate(zip(imgs, imgs_on)):
            t0 = at_times[k]
            a = prog(t, t0, 0.35, "out")
            if a <= 0:
                yy += im.height + 26
                continue
            done = done_times and done_times[k] is not None and t >= done_times[k]
            active = t >= t0 and not done and (k + 1 >= len(at_times) or t < at_times[k + 1])
            hgt = im.height + 14
            L.poly([(x, yy), (x + w, yy), (x + w, yy + hgt), (x, yy + hgt)],
                   fill="pos" if active else (251, 245, 230), stroke="ink" if not active else None, width=2, alpha=a)
            L.stamp(im_on if active else im, x + 52, yy + hgt / 2, "lm", alpha=a)
            L.circle(x + 26, yy + hgt / 2, 14, fill="cream" if active else "mustard", stroke="ink", width=2, alpha=a)
            L.stamp(formula(r"\b{%d}" % (k + 1), 22), x + 26, yy + hgt / 2 + 1, alpha=a)
            if done:
                c = prog(t, done_times[k], 0.3, "out")
                L.line([(x + w - 46, yy + hgt / 2), (x + w - 34, yy + hgt / 2 + 12), (x + w - 12, yy + hgt / 2 - 14)],
                       "grass_d", 6 * c + 0.1, alpha=c)
            yy += hgt + 12
    return mg(sc, fn, at=min(at_times), z=z, shadow=True)

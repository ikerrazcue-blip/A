"""Graphics core: paper textures, cut-out sprites, transforms and text.

Everything is drawn with Pillow + numpy. Shapes are drawn at SS x resolution and
downsampled for antialiasing, then "paperized": paper grain is added, the edges
get a slight hand-cut wobble and a light rim, and a soft drop shadow is kept so
the piece looks like cut paper lying on a table (stop-motion cut-out style).
"""
import functools
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONTS = os.path.join(ASSETS, "fonts")

W, H = 1920, 1080
SS = 2  # supersampling factor for vector drawing

PAL = {
    "paper": (241, 231, 207),
    "paper2": (231, 216, 184),
    "cream": (251, 245, 230),
    "terra": (190, 88, 48),
    "terra_l": (217, 131, 84),
    "terra_d": (150, 62, 32),
    "black": (32, 27, 24),
    "gold": (222, 168, 44),
    "gold_l": (240, 204, 110),
    "gold_d": (168, 112, 12),
    "blue": (38, 86, 132),
    "blue_l": (96, 146, 190),
    "olive": (104, 122, 56),
    "olive_l": (160, 172, 96),
    "marble": (246, 242, 234),
    "brown": (118, 78, 52),
    "brown_d": (84, 54, 36),
    "red": (172, 48, 40),
    "purple": (108, 70, 130),
    "purple_l": (160, 128, 184),
    "grey": (126, 118, 110),
    "white": (255, 255, 255),
}


def rgb(c):
    if isinstance(c, str):
        return PAL[c]
    return tuple(c)


# ----------------------------------------------------------------------------
# noise & paper
# ----------------------------------------------------------------------------
def smooth_noise(h, w, cell, rng):
    """Value noise in [0,1] with feature size ~cell px."""
    sh, sw = max(2, int(h / cell) + 2), max(2, int(w / cell) + 2)
    n = (rng.random((sh, sw)) * 255).astype(np.uint8)
    im = Image.fromarray(n).resize((int(sw * cell), int(sh * cell)), Image.BICUBIC)
    a = np.asarray(im, np.float32)[:h, :w] / 255.0
    return a


_DETAIL = None


def paper_detail():
    """Big grayscale detail map (float, ~[-1,1]) reused by every paper piece."""
    global _DETAIL
    if _DETAIL is None:
        rng = np.random.default_rng(1234)
        h, w = 1500, 2600
        d = (smooth_noise(h, w, 260, rng) - 0.5) * 1.1
        d += (smooth_noise(h, w, 70, rng) - 0.5) * 0.55
        d += (smooth_noise(h, w, 14, rng) - 0.5) * 0.30
        d += (rng.random((h, w)).astype(np.float32) - 0.5) * 0.28
        img = Image.new("L", (w, h), 128)
        dr = ImageDraw.Draw(img)
        for _ in range(12000):
            x, y = rng.random() * w, rng.random() * h
            a = rng.random() * math.pi
            ln = 5 + rng.random() * 20
            v = 128 + (1 if rng.random() < 0.55 else -1) * (18 + rng.random() * 26)
            dr.line([(x, y), (x + ln * math.cos(a), y + ln * math.sin(a))], fill=int(v), width=1)
        img = img.filter(ImageFilter.GaussianBlur(0.7))
        d += (np.asarray(img, np.float32) - 128) / 128 * 0.45
        _DETAIL = d.astype(np.float32)
    return _DETAIL


def detail_crop(w, h, seed):
    D = paper_detail()
    dh, dw = D.shape
    if w > dw or h > dh:
        reps = (math.ceil(h / dh), math.ceil(w / dw))
        D = np.tile(D, reps)
        dh, dw = D.shape
    rng = np.random.default_rng(seed)
    y0 = int(rng.integers(0, dh - h + 1))
    x0 = int(rng.integers(0, dw - w + 1))
    return D[y0:y0 + h, x0:x0 + w]


def paper_rgb(w, h, color, strength=8.0, seed=0):
    c = np.array(rgb(color), np.float32)
    arr = c[None, None, :] + detail_crop(w, h, seed)[..., None] * strength
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


# ----------------------------------------------------------------------------
# drawing helpers (supersampled)
# ----------------------------------------------------------------------------
class Canvas:
    """Supersampled RGBA drawing surface. Coordinates are in final pixels."""

    def __init__(self, w, h, ss=SS):
        self.w, self.h, self.ss = int(w), int(h), ss
        self.im = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def s(self, v):
        return v * self.ss

    def pts(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self.pts(pts), fill=_rgba(fill), outline=_rgba(outline) if outline else None,
                       width=int(width * self.ss) if width else 1)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=0):
        s = self.ss
        self.d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s],
                       fill=_rgba(fill) if fill else None,
                       outline=_rgba(outline) if outline else None, width=int(width * s))

    def circle(self, cx, cy, r, **kw):
        self.ellipse(cx, cy, r, r, **kw)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=0, radius=0):
        s = self.ss
        box = [x0 * s, y0 * s, x1 * s, y1 * s]
        if radius:
            self.d.rounded_rectangle(box, radius=radius * s, fill=_rgba(fill) if fill else None,
                                     outline=_rgba(outline) if outline else None, width=int(width * s))
        else:
            self.d.rectangle(box, fill=_rgba(fill) if fill else None,
                             outline=_rgba(outline) if outline else None, width=int(width * s))

    def line(self, pts, fill, width, joint="curve"):
        self.d.line(self.pts(pts), fill=_rgba(fill), width=max(1, int(width * self.ss)), joint=joint)
        # round caps
        r = width * self.ss / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x * self.ss - r, y * self.ss - r, x * self.ss + r, y * self.ss + r], fill=_rgba(fill))

    def arc(self, cx, cy, rx, ry, a0, a1, fill, width):
        s = self.ss
        self.d.arc([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], a0, a1,
                   fill=_rgba(fill), width=int(width * s))

    def paste(self, img, x, y):
        """paste an RGBA image given in final pixels (it is upscaled)."""
        big = img.resize((img.width * self.ss, img.height * self.ss), Image.LANCZOS)
        self.im.alpha_composite(big, dest=(int(x * self.ss), int(y * self.ss)))

    def result(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def _rgba(c):
    if c is None:
        return None
    if isinstance(c, str):
        return rgb(c) + (255,)
    if len(c) == 3:
        return tuple(c) + (255,)
    return tuple(c)


def shape_mask(w, h, draw_fn, ss=SS):
    """Return an L mask drawn by draw_fn(ImageDraw, scale) at supersampled size."""
    m = Image.new("L", (int(w * ss), int(h * ss)), 0)
    draw_fn(ImageDraw.Draw(m), ss)
    return m.resize((int(w), int(h)), Image.LANCZOS)


# ----------------------------------------------------------------------------
# paperize: turn a flat RGBA drawing into a cut paper piece
# ----------------------------------------------------------------------------
def paperize(rgba, seed=0, rough=1.0, texture=8.0, rim=0.22, grain_alpha=True):
    rgba = rgba.convert("RGBA")
    w, h = rgba.size
    arr = np.asarray(rgba, np.float32)
    a = arr[..., 3] / 255.0
    rng = np.random.default_rng(seed)
    if rough > 0:
        blurred = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1)),
                             np.float32) / 255.0
        nz = (smooth_noise(h, w, 7, rng) - 0.5) * 0.7 + (smooth_noise(h, w, 28, rng) - 0.5) * 0.6
        a2 = np.clip((blurred - 0.5 + nz * 0.16 * rough) * 3.2 + 0.5, 0, 1)
        # keep holes etc: never grow alpha where original was fully empty far away
        a = np.minimum(a2, np.clip(blurred * 3, 0, 1))
    rgbv = arr[..., :3]
    if texture:
        rgbv = rgbv + detail_crop(w, h, seed + 7)[..., None] * texture
    if rim:
        am = Image.fromarray((a * 255).astype(np.uint8))
        er = np.asarray(am.filter(ImageFilter.MinFilter(5)), np.float32) / 255.0
        ring = np.clip(a - er, 0, 1)[..., None]
        rgbv = rgbv * (1 - ring * rim) + 255 * ring * rim
    out = np.dstack([np.clip(rgbv, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def inner_shadow_layer(base, layer, offset=(2, 3), blur=2.5, opacity=0.35):
    """Composite `layer` onto `base` with a small drop shadow (layered paper)."""
    base = base.copy()
    al = layer.getchannel("A")
    sh = al.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    shadow = Image.new("RGBA", layer.size, (25, 15, 5, 0))
    shadow.putalpha(sh)
    # clip the shadow to the base's alpha so it does not spill outside the piece
    bal = base.getchannel("A")
    sh_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh_img.alpha_composite(shadow, dest=offset)
    sa = np.minimum(np.asarray(sh_img.getchannel("A"), np.float32), np.asarray(bal, np.float32))
    sh_img.putalpha(Image.fromarray(sa.astype(np.uint8)))
    base.alpha_composite(sh_img)
    base.alpha_composite(layer)
    return base


# ----------------------------------------------------------------------------
# Sprite: an RGBA piece + its shadow, positioned by its centre
# ----------------------------------------------------------------------------
class Sprite:
    def __init__(self, img, shadow_blur=5, pad=None, shadow=True):
        img = img.convert("RGBA")
        pad = pad if pad is not None else int(shadow_blur * 3 + 6)
        self.pad = pad
        if pad:
            p = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
            p.paste(img, (pad, pad))
            img = p
        self.img = img
        self.w, self.h = img.size
        self.shadow = img.getchannel("A").filter(ImageFilter.GaussianBlur(shadow_blur)) if shadow else None

    @property
    def size(self):
        return self.w, self.h

    @property
    def vw(self):
        """visible width (without the shadow padding)"""
        return self.w - 2 * self.pad

    @property
    def vh(self):
        return self.h - 2 * self.pad


def affine(img, scale=1.0, angle=0.0, resample=Image.BICUBIC):
    """Scale + rotate (degrees, counter-clockwise on screen) about the centre."""
    if abs(scale - 1) < 1e-4 and abs(angle) < 1e-3:
        return img
    w, h = img.size
    a = math.radians(angle)
    c, s = math.cos(a) * scale, math.sin(a) * scale
    nw = int(abs(w * c) + abs(h * s)) + 2
    nh = int(abs(w * s) + abs(h * c)) + 2
    # forward (screen, y down, ccw): x' = c*x + s*y ; y' = -s*x + c*y
    # inverse: x = (c*x' - s*y')/scale^2 ; y = (s*x' + c*y')/scale^2
    k = 1.0 / (scale * scale)
    ic, is_ = c * k, s * k
    ox, oy = nw / 2, nh / 2
    cx, cy = w / 2, h / 2
    data = (ic, -is_, cx - ic * ox + is_ * oy,
            is_, ic, cy - is_ * ox - ic * oy)
    mode = img.mode
    if mode == "RGBA":
        out = img.convert("RGBa").transform((nw, nh), Image.AFFINE, data, resample=resample).convert("RGBA")
    else:
        out = img.transform((nw, nh), Image.AFFINE, data, resample=resample)
    return out


def paste_clip(canvas, img, x, y):
    """alpha_composite img at integer (x, y) (top-left), clipping to canvas."""
    cw, ch = canvas.size
    w, h = img.size
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cw, x + w), min(ch, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (x, y, x + w, y + h):
        img = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    canvas.alpha_composite(img, dest=(x0, y0))


def draw_sprite(canvas, spr, cx, cy, scale=1.0, angle=0.0, shadow_off=(6, 8), shadow_op=0.34, alpha=1.0):
    img = affine(spr.img, scale, angle)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    if spr.shadow is not None and shadow_op > 0:
        sh = affine(spr.shadow, scale, angle, resample=Image.BILINEAR)
        op = shadow_op * alpha
        sh = sh.point(lambda v: int(v * op))
        shimg = Image.new("RGBA", sh.size, (28, 16, 6, 0))
        shimg.putalpha(sh)
        paste_clip(canvas, shimg, cx - sh.width / 2 + shadow_off[0], cy - sh.height / 2 + shadow_off[1])
    paste_clip(canvas, img, cx - img.width / 2, cy - img.height / 2)


# ----------------------------------------------------------------------------
# fonts & text
# ----------------------------------------------------------------------------
FONT_FILES = {
    "title": "Cinzel-900.ttf",
    "title7": "Cinzel-700.ttf",
    "deco": "CinzelDecorative-900.ttf",
    "deco7": "CinzelDecorative-700.ttf",
    "body": "Nunito-800.ttf",
    "body9": "Nunito-900.ttf",
    "body7": "Nunito-700.ttf",
    "body6": "Nunito-600.ttf",
    "hand": "PatrickHand-400.ttf",
    "greek": "GFSDidot-400.ttf",
    "marc": "Marcellus-400.ttf",
    "sym": "DejaVuSans-Bold.ttf",
}
FALLBACK_ORDER = ["greek", "sym"]


@functools.lru_cache(maxsize=None)
def _cmap(path):
    from fontTools.ttLib import TTFont
    return frozenset(TTFont(path).getBestCmap().keys())


def split_by_glyphs(s, f):
    """Split string s into [(piece, font)] using fallback fonts for missing glyphs."""
    have = _cmap(f.path)
    out = []
    for ch in s:
        use = f
        if ord(ch) not in have and not ch.isspace():
            for fb in FALLBACK_ORDER:
                ff = font(fb, f.size)
                if ord(ch) in _cmap(ff.path):
                    use = ff
                    break
        if out and out[-1][1] is use:
            out[-1][0] += ch
        else:
            out.append([ch, use])
    return [(a, b) for a, b in out]


@functools.lru_cache(maxsize=None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, FONT_FILES[name]), int(size))


STYLE_COLORS = {k: v for k, v in PAL.items()}
_TOKEN = re.compile(r"\{([a-z_0-9|]+):([^{}]*)\}")


def parse_rich(text):
    """'hola {gold:mundo} y {greek:λόγος}' -> [(str, style|None), ...]"""
    out, pos = [], 0
    for m in _TOKEN.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], None))
        out.append((m.group(2), m.group(1)))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], None))
    return out


def plain(text):
    return "".join(s for s, _ in parse_rich(text))


def _style(style, base_font, size, base_color, hl_default):
    fname, color = base_font, base_color
    if style:
        for part in style.split("|"):
            if part == "greek":
                fname = "greek"
                color = PAL["terra"] if color == base_color else color
            elif part == "b":
                fname = "body9" if base_font.startswith("body") else base_font
            elif part == "hl":
                color = hl_default
            elif part in FONT_FILES:
                fname = part
            elif part in PAL:
                color = PAL[part]
    fsize = size * (1.12 if fname == "greek" and base_font != "greek" else 1.0)
    return font(fname, fsize), color


def _words(text):
    """Split rich text into words; each word is a list of (str, style) runs. None = forced line break."""
    words, cur, buf = [], [], ""
    for seg, style in parse_rich(text):
        for ch in seg:
            if ch == "\n":
                if buf:
                    cur.append((buf, style)); buf = ""
                if cur:
                    words.append(cur); cur = []
                words.append(None)
            elif ch.isspace():
                if buf:
                    cur.append((buf, style)); buf = ""
                if cur:
                    words.append(cur); cur = []
            else:
                buf += ch
        if buf:
            cur.append((buf, style)); buf = ""
    if cur:
        words.append(cur)
    return words


def layout_rich(text, base_font, size, max_w, color=(32, 27, 24), hl=(190, 88, 48), tracking=0):
    """Word-wrap rich text -> (lines, line_h, space). line = [(runs, width)], run = (str, font, color, w)."""
    base_f = font(base_font, size)
    space = base_f.getlength(" ") + (tracking * base_f.size if tracking else 0)
    lines, cur, cur_w = [], [], 0.0
    for w in _words(text):
        if w is None:
            lines.append(cur)
            cur, cur_w = [], 0.0
            continue
        runs, ww = [], 0.0
        for s, style in w:
            f0, c = _style(style, base_font, size, rgb(color), rgb(hl))
            for piece, f in split_by_glyphs(s, f0):
                rw = _text_w(piece, f, tracking)
                runs.append((piece, f, c, rw))
                ww += rw
        add = ww + (space if cur else 0)
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w, add = [], 0.0, ww
        cur.append((runs, ww))
        cur_w += add
    if cur:
        lines.append(cur)
    asc, desc = base_f.getmetrics()
    return lines, asc + desc, space


def _text_w(t, f, tracking):
    if not tracking:
        return f.getlength(t)
    return sum(f.getlength(ch) for ch in t) + tracking * f.size * max(0, len(t) - 1)


def render_rich(text, base_font="body", size=48, max_w=1200, color="black", hl="terra", align="center",
                line_spacing=1.08, tracking=0, stroke=0, stroke_color=None):
    lines, lh, space = layout_rich(text, base_font, size, max_w, rgb(color), rgb(hl), tracking)
    lh_px = int(lh * line_spacing)
    widths = [sum(ww for _, ww in ln) + space * max(0, len(ln) - 1) for ln in lines]
    tw = int(max(widths) if widths else 1) + 8 + 2 * stroke
    th = int(lh_px * max(1, len(lines)) + (lh - lh_px) + 8) + 2 * stroke
    im = Image.new("RGBA", (max(tw, 1), max(th, 1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base_asc = font(base_font, size).getmetrics()[0]
    sc = _rgba(stroke_color) if stroke_color else None
    y = 4 + stroke
    for ln, wsum in zip(lines, widths):
        if align == "center":
            x = (tw - wsum) / 2
        elif align == "right":
            x = tw - wsum - 4 - stroke
        else:
            x = 4 + stroke
        for i, (runs, ww) in enumerate(ln):
            if i > 0:
                x += space
            for s, f, c, rw in runs:
                dy = base_asc - f.getmetrics()[0]
                if tracking:
                    xx = x
                    for ch in s:
                        d.text((xx, y + dy), ch, font=f, fill=c + (255,), stroke_width=stroke, stroke_fill=sc)
                        xx += f.getlength(ch) + tracking * f.size
                else:
                    d.text((x, y + dy), s, font=f, fill=c + (255,), stroke_width=stroke, stroke_fill=sc)
                x += rw
        y += lh_px
    return im


# ----------------------------------------------------------------------------
# paper cards
# ----------------------------------------------------------------------------
def card(text, size=48, font_name="body", color="black", bg="cream", hl="terra", max_w=1000, pad=(34, 20),
         align="center", seed=1, rough=0.9, min_w=0, tracking=0, line_spacing=1.08, border=None, radius=0,
         texture=7.0, shadow_blur=5):
    """A cut paper card with printed text. Returns Sprite."""
    t = render_rich(text, font_name, size, max_w, color, hl, align, line_spacing, tracking)
    cw = max(min_w, t.width + 2 * pad[0])
    ch = t.height + 2 * pad[1]
    cv = Canvas(cw, ch)
    cv.rect(2, 2, cw - 2, ch - 2, fill=bg, radius=radius)
    if border:
        bc, bw = border
        cv.rect(2 + bw * 1.6, 2 + bw * 1.6, cw - 2 - bw * 1.6, ch - 2 - bw * 1.6, outline=bc, width=bw,
                radius=max(0, radius - bw))
    base = paperize(cv.result(), seed=seed, rough=rough, texture=texture)
    base.alpha_composite(t, dest=((cw - t.width) // 2, (ch - t.height) // 2))
    return Sprite(base, shadow_blur=shadow_blur)


def text_sprite(text, size=48, font_name="body", color="black", hl="terra", max_w=1400, align="center",
                tracking=0, stroke=0, stroke_color=None, shadow=False, line_spacing=1.08):
    t = render_rich(text, font_name, size, max_w, color, hl, align, line_spacing, tracking, stroke, stroke_color)
    return Sprite(t, shadow_blur=3, shadow=shadow)

"""Greek-flavoured paper props: meander bands, columns, Athena's owl, medallions,
icons (game-icons.net, CC BY 3.0), speech bubbles, arrows and laurels."""
import functools
import io
import json
import math
import os

import numpy as np
from PIL import Image, ImageFilter

from .gfx import (ASSETS, PAL, Canvas, Sprite, font, inner_shadow_layer, paperize, render_rich, rgb)

ICON_JSON = os.path.join(ASSETS, "icons", "game-icons.json")


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=72, a0=0, a1=360):
    r = math.radians(rot)
    pts = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return pts


# ----------------------------------------------------------------------------
# icons
# ----------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def _icons():
    with open(ICON_JSON) as f:
        j = json.load(f)
    return j


@functools.lru_cache(maxsize=256)
def icon(name, size, color="black"):
    """Render a game-icons silhouette to RGBA at `size` px (square)."""
    import cairosvg
    j = _icons()
    ic = j["icons"][name]
    w, h = ic.get("width", j.get("width", 512)), ic.get("height", j.get("height", 512))
    c = "#%02x%02x%02x" % rgb(color)
    body = ic["body"].replace("currentColor", c)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{size}" height="{size}">{body}</svg>'
    png = cairosvg.svg2png(bytestring=svg.encode())
    return Image.open(io.BytesIO(png)).convert("RGBA")


def icon_cutout(name, size, color="black", seed=0, rough=0.35):
    return Sprite(paperize(icon(name, size, color), seed=seed, rough=rough, texture=6, rim=0.12), shadow_blur=4)


# ----------------------------------------------------------------------------
# meander (Greek key) band
# ----------------------------------------------------------------------------
def meander_band(width, height, bg="terra", fg="black", seed=0, rough=0.5, frame=True):
    cv = Canvas(width, height)
    cv.rect(0, 0, width, height, fill=bg)
    m = height * 0.14  # margin for the framing lines
    lw = max(2, height * 0.05)
    if frame:
        cv.rect(0, m * 0.35, width, m * 0.35 + lw, fill=fg)
        cv.rect(0, height - m * 0.35 - lw, width, height - m * 0.35, fill=fg)
    ph = height - 2 * m - 2 * lw  # pattern height = 7 units
    u = ph / 7.0
    y0 = m + lw
    period = 8 * u
    x = -period * 0.25
    stroke = u * 1.0
    # continuous baseline
    cv.line([(0, y0 + 6.5 * u), (width, y0 + 6.5 * u)], fg, stroke)
    while x < width + period:
        pts = [(0.5, 6.5), (0.5, 0.5), (6.5, 0.5), (6.5, 4.5), (2.5, 4.5), (2.5, 2.5), (4.5, 2.5)]
        cv.d.line([((x + px * u) * cv.ss, (y0 + py * u) * cv.ss) for px, py in pts], fill=rgb(fg) + (255,),
                  width=int(stroke * cv.ss), joint=None)
        # square joints: fill the corners
        for px, py in pts[1:-1]:
            cx, cy = x + px * u, y0 + py * u
            cv.rect(cx - stroke / 2, cy - stroke / 2, cx + stroke / 2, cy + stroke / 2, fill=fg)
        x += period
    return paperize(cv.result(), seed=seed, rough=rough, texture=7)


def wave_band(width, height, bg="black", fg="terra", seed=0):
    """Running-wave (Vitruvian scroll) band, used as an alternative border."""
    cv = Canvas(width, height)
    cv.rect(0, 0, width, height, fill=bg)
    per = height * 1.6
    x = 0
    r = height * 0.28
    while x < width + per:
        cx, cy = x + per * 0.5, height * 0.52
        cv.arc(cx, cy, r, r, 180, 450, fg, height * 0.1)
        cv.line([(x, height * 0.8), (cx - r, height * 0.8)], fg, height * 0.1)
        x += per
    return paperize(cv.result(), seed=seed, rough=0.4, texture=6)


# ----------------------------------------------------------------------------
# column
# ----------------------------------------------------------------------------
def column(height, width=None, kind="ionic", seed=0, color="marble", shade=(200, 192, 180)):
    width = width or height * 0.2
    W_ = width * 1.5
    cv = Canvas(W_, height)
    cx = W_ / 2
    base_h = height * 0.06
    cap_h = height * 0.11
    shaft_top, shaft_bot = cap_h, height - base_h
    # base
    cv.rect(cx - width * 0.66, height - base_h * 0.5, cx + width * 0.66, height, fill=shade)
    cv.rect(cx - width * 0.6, height - base_h, cx + width * 0.6, height - base_h * 0.45, fill=color, radius=6)
    # shaft (slight taper)
    tw, bw = width * 0.40, width * 0.48
    cv.poly([(cx - tw, shaft_top), (cx + tw, shaft_top), (cx + bw, shaft_bot), (cx - bw, shaft_bot)], fill=color)
    # flutes
    n = 6
    for i in range(1, n):
        f = -1 + 2 * i / n
        x_t, x_b = cx + f * tw * 0.92, cx + f * bw * 0.92
        cv.line([(x_t, shaft_top + 6), (x_b, shaft_bot - 4)], shade, max(2, width * 0.04))
    # capital
    if kind == "ionic":
        cv.rect(cx - width * 0.68, 0, cx + width * 0.68, cap_h * 0.28, fill=color)
        cv.rect(cx - width * 0.55, cap_h * 0.28, cx + width * 0.55, cap_h * 0.72, fill=color)
        for sgn in (-1, 1):
            vx = cx + sgn * width * 0.56
            vy = cap_h * 0.58
            r = cap_h * 0.36
            cv.circle(vx, vy, r, fill=color)
            cv.arc(vx, vy, r * 0.78, r * 0.78, 0, 360, shade, max(2, r * 0.18))
            cv.circle(vx, vy, r * 0.28, fill=shade)
        cv.rect(cx - tw * 1.1, cap_h * 0.72, cx + tw * 1.1, cap_h, fill=shade)
    else:  # doric
        cv.rect(cx - width * 0.62, 0, cx + width * 0.62, cap_h * 0.4, fill=color)
        cv.poly([(cx - width * 0.58, cap_h * 0.4), (cx + width * 0.58, cap_h * 0.4), (cx + tw * 1.05, cap_h),
                 (cx - tw * 1.05, cap_h)], fill=color)
    img = paperize(cv.result(), seed=seed, rough=0.6, texture=6)
    return Sprite(img, shadow_blur=6)


# ----------------------------------------------------------------------------
# Athena's owl (mascot)
# ----------------------------------------------------------------------------
OWL_W, OWL_H = 360, 430


def _layer(draw_fn, seed, rough=0.7, texture=8):
    cv = Canvas(OWL_W, OWL_H)
    draw_fn(cv)
    return paperize(cv.result(), seed=seed, rough=rough, texture=texture)


@functools.lru_cache(maxsize=1)
def _owl_base():
    brown, dark, face = rgb("brown"), rgb("brown_d"), (206, 160, 116)
    cream = rgb("cream")

    def body(cv):
        cv.ellipse(180, 272, 128, 140, fill=brown)
        cv.poly(ellipse_pts(180, 145, 132, 106), fill=brown)
        # head spots
        for (x, y, r) in [(120, 70, 6), (150, 58, 5), (180, 54, 6), (210, 58, 5), (240, 70, 6), (100, 92, 5),
                          (260, 92, 5), (135, 84, 4), (225, 84, 4), (165, 72, 4), (195, 72, 4)]:
            cv.circle(x, y, r, fill=(226, 200, 160))

    def wings(cv):
        cv.poly(ellipse_pts(72, 292, 44, 112, rot=12), fill=dark)
        cv.poly(ellipse_pts(288, 292, 44, 112, rot=-12), fill=dark)
        for i in range(4):
            for sgn, x0 in ((-1, 72), (1, 288)):
                cv.circle(x0 - sgn * 6, 250 + i * 34, 7, fill=(226, 200, 160))

    def belly(cv):
        cv.ellipse(180, 300, 84, 104, fill=cream)
        for row in range(4):
            y = 238 + row * 30
            for k in range(-2, 3):
                x = 180 + k * 30 + (15 if row % 2 else 0)
                if abs(x - 180) > 64 - row * 2:
                    continue
                cv.line([(x - 9, y), (x, y + 8), (x + 9, y)], dark, 4)

    def facedisc(cv):
        cv.circle(128, 152, 58, fill=face)
        cv.circle(232, 152, 58, fill=face)

    def feet(cv):
        for x in (148, 212):
            for dx in (-12, 0, 12):
                cv.ellipse(x + dx, 408, 7, 14, fill=rgb("gold"))

    base = _layer(feet, 11, rough=0.4)
    for fn, sd in ((body, 12), (wings, 13), (belly, 14), (facedisc, 15)):
        base = inner_shadow_layer(base, _layer(fn, sd), offset=(2, 3), blur=2.5, opacity=0.35) \
            if base.getbbox() else _layer(fn, sd)
    return base


def _owl_eyes(state, look=(0, 0)):
    def eyes(cv):
        for ex in (128, 232):
            if state == "closed":
                cv.circle(ex, 152, 42, fill=rgb("brown"))
                cv.arc(ex, 150, 30, 18, 20, 160, rgb("brown_d"), 5)
            else:
                cv.circle(ex, 152, 42, fill=rgb("gold"))
                cv.circle(ex, 152, 42, outline=rgb("brown_d"), width=4)
                pr = 26 if state == "wide" else 22
                px, py = ex + look[0] * 10, 152 + look[1] * 10
                cv.circle(px, py, pr, fill=rgb("black"))
                cv.circle(px - 8, py - 9, 7, fill=(255, 255, 255))
                if state == "half":
                    cv.poly(ellipse_pts(ex, 152, 44, 44, a0=180, a1=360), fill=rgb("brown"))
    return eyes


def _owl_brows(mood):
    def brows(cv):
        c = rgb("cream")
        if mood == "wow":
            cv.line([(78, 88), (128, 76), (174, 96)], c, 13)
            cv.line([(186, 96), (232, 76), (282, 88)], c, 13)
        elif mood == "doubt":
            cv.line([(80, 104), (128, 98), (174, 112)], c, 13)
            cv.line([(186, 100), (232, 70), (282, 84)], c, 13)
        else:
            cv.line([(80, 104), (128, 92), (176, 116)], c, 13)
            cv.line([(184, 116), (232, 92), (280, 104)], c, 13)
    return brows


def _owl_beak(open_):
    def beak(cv):
        if open_:
            cv.poly([(180, 214), (164, 214), (180, 236)], fill=(60, 30, 20))
            cv.poly([(166, 186), (194, 186), (180, 212)], fill=(222, 150, 44))
            cv.poly([(168, 216), (192, 216), (180, 234)], fill=(200, 126, 34))
        else:
            cv.poly([(164, 188), (196, 188), (180, 222)], fill=(222, 150, 44))
    return beak


@functools.lru_cache(maxsize=64)
def owl_img(eyes="open", beak=False, mood="calm", look=(0, 0)):
    base = _owl_base()
    img = inner_shadow_layer(base, _layer(_owl_eyes(eyes, look), 21, rough=0.3), offset=(1, 2), blur=2, opacity=0.3)
    img = inner_shadow_layer(img, _layer(_owl_brows(mood), 22, rough=0.4), offset=(1, 2), blur=2, opacity=0.3)
    img = inner_shadow_layer(img, _layer(_owl_beak(beak), 23, rough=0.3), offset=(1, 2), blur=2, opacity=0.3)
    return img


@functools.lru_cache(maxsize=64)
def owl_sprite(eyes="open", beak=False, mood="calm", look=(0, 0), scale=1.0):
    img = owl_img(eyes, beak, mood, look)
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return Sprite(img, shadow_blur=6)


# ----------------------------------------------------------------------------
# medallions, bubbles, arrows, laurels
# ----------------------------------------------------------------------------
def medallion(diam, icon_name=None, bg="terra", fg="black", ring="black", seed=0, icon_scale=0.62,
              inner=None, dots=True):
    cv = Canvas(diam, diam)
    r = diam / 2
    cv.circle(r, r, r - 2, fill=ring)
    cv.circle(r, r, r * 0.9, fill=bg)
    if dots:
        n = int(diam / 14)
        for i in range(n):
            a = 2 * math.pi * i / n
            cv.circle(r + math.cos(a) * r * 0.955, r + math.sin(a) * r * 0.955, max(2, diam * 0.011), fill=bg)
    if inner:
        cv.circle(r, r, r * 0.84, outline=inner, width=max(2, diam * 0.012))
    img = paperize(cv.result(), seed=seed, rough=0.6, texture=7)
    if icon_name:
        s = int(diam * icon_scale)
        ic = icon(icon_name, s, fg)
        img.alpha_composite(ic, dest=((diam - s) // 2, (diam - s) // 2))
    return Sprite(img, shadow_blur=6)


def bubble(text, size=56, font_name="title", color="black", bg="cream", tail="left", seed=0, pad=(40, 26),
           max_w=700, hl="terra"):
    t = render_rich(text, font_name, size, max_w, color, hl)
    bw, bh = t.width + 2 * pad[0], t.height + 2 * pad[1]
    th = bh * 0.45  # tail height
    cv = Canvas(bw + 10, bh + th + 10)
    cv.ellipse(5 + bw / 2, 5 + bh / 2, bw / 2, bh / 2, fill=bg)
    if tail == "left":
        pts = [(bw * 0.22, bh * 0.72), (bw * 0.40, bh * 0.86), (bw * 0.08, bh + th)]
    elif tail == "right":
        pts = [(bw * 0.78, bh * 0.72), (bw * 0.60, bh * 0.86), (bw * 0.92, bh + th)]
    else:
        pts = [(bw * 0.42, bh * 0.9), (bw * 0.58, bh * 0.9), (bw * 0.5, bh + th)]
    cv.poly(pts, fill=bg)
    img = paperize(cv.result(), seed=seed, rough=0.8, texture=7)
    img.alpha_composite(t, dest=(int(5 + (bw - t.width) / 2), int(5 + (bh - t.height) / 2)))
    return Sprite(img, shadow_blur=5)


def arrow(length, thick=26, color="terra", seed=0, head=2.2):
    L, T = length, thick
    cv = Canvas(L + 10, T * head + 10)
    cy = (T * head + 10) / 2
    hl = T * head * 0.9
    cv.poly([(5, cy - T / 2), (5 + L - hl, cy - T / 2 - 2), (5 + L - hl, cy - T * head / 2), (5 + L, cy),
             (5 + L - hl, cy + T * head / 2), (5 + L - hl, cy + T / 2 + 2), (5, cy + T / 2)], fill=color)
    return Sprite(paperize(cv.result(), seed=seed, rough=0.9, texture=7), shadow_blur=4)


def big_glyph(ch, size, color="blue", font_name="title", seed=0):
    """A single big character cut from paper (e.g. '?' or '!')."""
    f = font(font_name, size)
    bbox = f.getbbox(ch)
    w, h = bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 20
    cv = Canvas(w, h)
    cv.d.text((10 * cv.ss - bbox[0] * cv.ss, 10 * cv.ss - bbox[1] * cv.ss), ch, font=font(font_name, size * cv.ss),
              fill=rgb(color) + (255,))
    return Sprite(paperize(cv.result(), seed=seed, rough=0.6, texture=7), shadow_blur=5)


def laurel(size, color="olive", seed=0):
    return icon_cutout("laurels", size, color, seed=seed, rough=0.3)


def title_block(text, size=110, color="black", tracking=0.06, seed=0, font_name="title"):
    t = render_rich(text, font_name, size, 1800, color, "terra", "center", 1.0, tracking)
    return Sprite(t, shadow_blur=3, shadow=False)


def stars(w, h, n=40, seed=0, color="gold_l"):
    """Little paper stars scattered (for the night sky of wonder)."""
    rng = np.random.default_rng(seed)
    cv = Canvas(w, h)
    for _ in range(n):
        x, y = rng.random() * w, rng.random() * h
        r = 4 + rng.random() * 9
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        cv.poly(pts, fill=color)
    return Sprite(paperize(cv.result(), seed=seed, rough=0.2, texture=4), shadow_blur=3)


# ----------------------------------------------------------------------------
# a cut-paper map of the Aegean (Greece, Ionia and Miletus)
# ----------------------------------------------------------------------------
LON0, LON1, LAT0, LAT1 = 19.3, 30.2, 34.7, 41.6

MAINLAND = [(19.3, 41.6), (19.4, 40.8), (19.9, 39.9), (20.6, 39.1), (21.05, 38.55), (21.45, 38.33),
            (22.3, 38.2), (22.9, 37.97), (22.35, 38.12), (21.6, 38.2), (21.25, 38.2), (21.1, 37.8),
            (21.7, 36.8), (22.1, 36.9), (22.45, 36.4), (22.6, 36.8), (23.05, 36.45), (23.15, 36.95),
            (22.75, 37.45), (23.2, 37.55), (23.45, 37.42), (23.1, 37.9), (23.65, 37.93), (24.05, 37.65),
            (24.0, 38.15), (23.55, 38.45), (22.85, 38.9), (23.3, 39.15), (22.95, 39.75), (22.6, 40.35),
            (22.95, 40.6), (23.35, 40.25), (23.95, 40.05), (23.9, 40.6), (24.45, 40.93), (25.35, 40.95),
            (26.05, 40.8), (26.2, 40.35), (26.2, 40.05), (26.75, 40.45), (27.6, 40.35), (28.9, 40.95),
            (29.05, 41.2), (29.1, 41.6)]
ANATOLIA = [(30.2, 41.6), (29.25, 41.6), (29.2, 41.15), (29.4, 40.8), (28.8, 40.4), (27.7, 40.3),
            (26.95, 40.3), (26.3, 40.0), (26.15, 39.45), (26.85, 39.3), (26.95, 38.85), (26.6, 38.55),
            (26.35, 38.3), (26.9, 38.35), (27.1, 38.42), (26.95, 38.05), (27.35, 37.9), (27.2, 37.5),
            (27.55, 37.3), (27.25, 37.0), (28.0, 36.8), (28.35, 36.55), (29.1, 36.6), (30.2, 36.3)]
CRETE = [(23.55, 35.25), (23.6, 35.6), (24.3, 35.55), (25.0, 35.42), (25.8, 35.33), (26.3, 35.28),
         (26.15, 35.0), (25.0, 34.95), (24.1, 35.1)]
EUBOEA = [(22.85, 38.95), (23.35, 38.98), (24.2, 38.4), (24.6, 38.0), (24.3, 38.05), (23.5, 38.45)]
ISLANDS = [(26.3, 39.2, 0.28), (26.0, 38.38, 0.2), (26.8, 37.73, 0.16), (28.0, 36.2, 0.2), (25.4, 37.05, 0.13),
           (25.15, 37.05, 0.1), (25.35, 37.45, 0.08), (25.42, 36.42, 0.1), (24.42, 36.7, 0.1), (24.85, 37.85, 0.12),
           (25.1, 37.6, 0.09), (24.9, 36.8, 0.07), (25.9, 36.9, 0.08), (27.2, 36.85, 0.12), (24.95, 39.95, 0.18),
           (25.55, 40.4, 0.12), (23.55, 39.12, 0.06)]


def aegean_map(width=900, seed=0):
    """Returns (Sprite, project) where project(lon, lat) -> (x, y) relative to the sprite centre."""
    kx = width / (LON1 - LON0)
    ky = kx * 1.27
    height = (LAT1 - LAT0) * ky

    def P(lon, lat):
        return (lon - LON0) * kx, (LAT1 - lat) * ky

    cv = Canvas(width, height)
    cv.rect(0, 0, width, height, fill=(126, 172, 198), radius=10)
    # a few paper waves in the sea
    for i in range(18):
        x = (i * 173) % int(width - 60) + 30
        y = (i * 97) % int(height - 60) + 30
        cv.arc(x, y, 16, 7, 200, 340, (160, 200, 220), 3)
    land = (236, 222, 180)
    for poly in (MAINLAND, ANATOLIA, CRETE, EUBOEA):
        cv.poly([P(lo, la) for lo, la in poly], fill=land)
    for lo, la, r in ISLANDS:
        x, y = P(lo, la)
        cv.ellipse(x, y, r * kx, r * kx * 0.8, fill=land)
    img = paperize(cv.result(), seed=seed, rough=0.5, texture=7)
    spr = Sprite(img, shadow_blur=6)

    def project(lon, lat):
        x, y = P(lon, lat)
        return x - width / 2, y - height / 2
    return spr, project

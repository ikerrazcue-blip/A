"""Reusable building blocks (sprites + scene templates) for the philosophy videos."""
import zlib

import numpy as np
from PIL import Image

from . import gfx, greek
from .gfx import W, H, Sprite, card, inner_shadow_layer, rgb


def compose(parts, pad=24):
    """Merge sprites into one paper piece. parts = [(Sprite, cx, cy, rot)] (first = bottom)."""
    imgs = []
    for p in parts:
        spr, cx, cy = p[0], p[1], p[2]
        rot = p[3] if len(p) > 3 else 0
        im = gfx.affine(spr.img, 1.0, rot)
        imgs.append((im, cx - im.width / 2, cy - im.height / 2))
    x0 = min(x for _, x, _ in imgs)
    y0 = min(y for _, _, y in imgs)
    x1 = max(x + im.width for im, x, _ in imgs)
    y1 = max(y + im.height for im, _, y in imgs)
    w, h = int(x1 - x0) + 2 * pad, int(y1 - y0) + 2 * pad
    base = None
    for im, x, y in imgs:
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer.alpha_composite(im, dest=(int(x - x0 + pad), int(y - y0 + pad)))
        base = layer if base is None else inner_shadow_layer(base, layer, offset=(4, 5), blur=4, opacity=0.35)
    bbox = base.getbbox()
    base = base.crop(bbox)
    return Sprite(base, shadow_blur=6)


def label(text, size=44, bg="cream", color="black", font_name="body", seed=None, **kw):
    return card(text, size=size, font_name=font_name, bg=bg, color=color,
                seed=seed if seed is not None else zlib.crc32(text.encode()) % 997, **kw)


def title_card(text, size=62, bg="cream", color="black", seed=None, max_w=1300, **kw):
    return card(text, size=size, font_name="title", bg=bg, color=color, max_w=max_w, pad=(44, 24),
                seed=seed if seed is not None else zlib.crc32(text.encode()) % 991, **kw)


def person(name, icon="philosopher-bust", bg="terra", diam=170, name_size=38, sub=None, seed=0):
    """Medallion portrait + name tag, as one piece."""
    med = greek.medallion(diam, icon, bg=bg, seed=seed, icon_scale=0.74)
    txt = name if not sub else f"{name}\n{{grey:{sub}}}"
    tag = card(txt, size=name_size, font_name="body9", bg="cream", seed=seed + 1, pad=(22, 8), line_spacing=1.0)
    return compose([(med, 0, 0), (tag, 0, diam / 2 + tag.h / 2 - 34, -2)])


def concept(title, icon, bg, fg="black", diam=270, title_size=58, greek_word=None, title_bg=None,
            title_color="black", seed=0):
    """Big medallion with icon + a title strip under it (e.g. ADMIRACIÓN)."""
    med = greek.medallion(diam, icon, bg=bg, fg=fg, seed=seed)
    ttl = card(title, size=title_size, font_name="title", bg=title_bg or bg, color=title_color,
               seed=seed + 1, pad=(34, 14))
    parts = [(med, 0, 0), (ttl, 0, diam / 2 + ttl.h / 2 - 30, 2)]
    if greek_word:
        g = card(greek_word, size=38, font_name="greek", bg="cream", color="terra", seed=seed + 2, pad=(20, 4))
        parts.append((g, 0, diam / 2 + ttl.h - 30 + g.h / 2 - 22, -3))
    return compose(parts)


def title_scene(movie, title, subtitle, tag=None, narration=None, jingle="intro"):
    sc = movie.scene("title", bg="terra", lead=0.2, transition="cut")
    t_j = sc.jingle(0.25, jingle, gain=0.45)
    col_l = greek.column(640, kind="ionic", seed=31)
    col_r = greek.column(640, kind="ionic", seed=32)
    sc.add(col_l, 170, 560, at=0.25, enter="slide_u", z=1)
    sc.add(col_r, W - 170, 560, at=0.4, enter="slide_u", z=1)
    ttl = greek.title_block(title, size=150, color="cream", tracking=0.08)
    sc.add(ttl, W / 2, 330, at=0.7, enter="drop", z=2, jitter=0.6)
    sub = card(subtitle, size=60, font_name="title", bg="cream", color="black", pad=(46, 16), seed=33)
    sc.add(sub, W / 2, 520, at=1.1, enter="drop", z=3, rot=-1.5)
    if tag:
        tg = card(tag, size=34, font_name="body9", bg="gold", color="black", pad=(22, 8), seed=34)
        sc.add(tg, W / 2 + sub.w / 2 - 40, 450, at=1.5, enter="pop", z=4, rot=6)
    owl = sc.owl(W / 2, 800, scale=0.62, at=0.9, enter="slide_u", z=5, talk=True)
    sc.cursor = max(sc.cursor, t_j - 0.6)
    if narration:
        sc.say(narration)
    owl.mood(sc.cursor - 0.3, "wow", "wide")
    sc.wait(0.6)
    return sc


def section_scene(movie, numeral, title, narration=None):
    """Section divider: Greek numeral medallion + title, with the lyre motif."""
    sc = movie.scene("section:" + title, bg="terra", lead=0.35)
    t_j = sc.jingle(0.45, "section", gain=0.42)
    med = greek.medallion(250, None, bg="cream", ring="black", seed=41)
    num = greek.title_block(numeral, size=150, color="terra", tracking=0)
    medal = compose([(med, 0, 0), (Sprite(num.img, shadow=False), 0, 8)])
    sc.add(medal, W / 2, 380, at=0.5, enter="pop", z=2)
    ttl = card(title, size=72, font_name="title", bg="cream", color="black", pad=(50, 20), seed=42, max_w=1500)
    sc.add(ttl, W / 2, 640, at=0.9, enter="drop", z=3, rot=-1)
    sc.cursor = max(sc.cursor, t_j - 0.5)
    if narration:
        sc.say(narration)
    sc.wait(0.3)
    return sc

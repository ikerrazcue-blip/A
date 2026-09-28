"""Reusable building blocks (sprites + scene templates) for the philosophy videos."""
import zlib

import numpy as np
from PIL import Image

from . import gfx, greek
from .gfx import W, H, Canvas, Sprite, card, inner_shadow_layer, paperize, render_rich, rgb

TITLE_Y = 132


def _seed(text):
    return zlib.crc32(text.encode()) % 997


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
                seed=seed if seed is not None else _seed(text), **kw)


def title_card(text, size=58, bg="cream", color="black", seed=None, max_w=1500, **kw):
    return card(text, size=size, font_name="title", bg=bg, color=color, max_w=max_w, pad=(44, 20),
                seed=seed if seed is not None else _seed(text) + 3, **kw)


def person(name, icon="philosopher-bust", bg="terra", diam=170, name_size=38, sub=None, seed=None):
    """Medallion portrait + name tag, as one piece."""
    seed = _seed(name) if seed is None else seed
    med = greek.medallion(diam, icon, bg=bg, seed=seed, icon_scale=0.74)
    txt = name if not sub else f"{name}\n{{grey:{sub}}}"
    tag = card(txt, size=name_size, font_name="body9", bg="cream", seed=seed + 1, pad=(22, 8), line_spacing=1.0)
    return compose([(med, 0, 0), (tag, 0, diam / 2 + tag.h / 2 - 34, -2)])


def concept(title, icon, bg, fg="black", diam=270, title_size=58, greek_word=None, title_bg=None,
            title_color="black", seed=None):
    """Big medallion with icon + a title strip under it (e.g. ADMIRACIÓN)."""
    seed = _seed(title) if seed is None else seed
    med = greek.medallion(diam, icon, bg=bg, fg=fg, seed=seed)
    ttl = card(title, size=title_size, font_name="title", bg=title_bg or bg, color=title_color,
               seed=seed + 1, pad=(34, 14))
    parts = [(med, 0, 0), (ttl, 0, diam / 2 + ttl.h / 2 - 30, 2)]
    if greek_word:
        g = card(greek_word, size=38, font_name="greek", bg="cream", color="terra", seed=seed + 2, pad=(20, 4))
        parts.append((g, 0, diam / 2 + ttl.h - 30 + g.h / 2 - 22, -3))
    return compose(parts)


def icon_card(text, icon, bg="cream", color="black", med_bg="terra", icon_color="black", size=40, max_w=600,
              seed=None, font_name="body", diam=None, hl="terra", min_w=0):
    """Medallion with an icon glued to the left end of a text card."""
    seed = _seed(text) if seed is None else seed
    t = card(text, size=size, font_name=font_name, bg=bg, color=color, max_w=max_w, pad=(30, 14), seed=seed, hl=hl,
             min_w=min_w)
    diam = diam or min(136, max(112, int(t.vh * 1.05)))
    med = greek.medallion(diam, icon, bg=med_bg, fg=icon_color, seed=seed + 1, icon_scale=0.64)
    return compose([(t, diam * 0.40 + t.vw / 2 + 8, 0), (med, 0, 0)])


def ojo(text, size=40, max_w=1150, seed=None):
    """Warning card for the classic confusions: '¡OJO!' tab + text."""
    seed = _seed(text) if seed is None else seed
    t = card(text, size=size, bg="cream", border=("red", 4), max_w=max_w, pad=(44, 22), seed=seed, hl="red")
    tab = card("¡OJO!", size=40, font_name="title", bg="red", color="cream", pad=(24, 8), seed=seed + 1)
    return compose([(t, 0, 0), (tab, -t.vw / 2 + tab.vw / 2 + 30, -t.vh / 2 - tab.vh / 2 + 18, -4)])


def quote(text, author, size=44, max_w=1050, seed=None):
    """A parchment scroll with a quotation and its author."""
    seed = _seed(text) if seed is None else seed
    body = render_rich(text, "marc", size, max_w, "black", "terra", "center", 1.16)
    auth = render_rich(author, "body9", 32, max_w, "terra_d", "terra", "center")
    w = max(body.width, auth.width) + 130
    h = body.height + auth.height + 70
    cv = Canvas(w, h + 70)
    paper_c, roll, roll_d = (245, 233, 202), (226, 204, 156), (196, 170, 118)
    cv.rect(26, 35, w - 26, h + 35, fill=paper_c)
    for yy in (35, h + 35):
        cv.rect(10, yy - 18, w - 10, yy + 18, fill=roll, radius=18)
        cv.ellipse(22, yy, 11, 18, fill=roll_d)
        cv.ellipse(w - 22, yy, 11, 18, fill=roll_d)
    img = paperize(cv.result(), seed=seed, rough=0.7, texture=8)
    img.alpha_composite(body, dest=((w - body.width) // 2, 62))
    img.alpha_composite(auth, dest=((w - auth.width) // 2, 62 + body.height + 8))
    return Sprite(img, shadow_blur=6)


def header(text, bg="terra", color="cream", size=40, seed=None):
    """Small tab used as a column/row header."""
    return card(text, size=size, font_name="title", bg=bg, color=color, pad=(26, 10),
                seed=_seed(text) + 7 if seed is None else seed)


def cell(text, bg="cream", color="black", size=36, max_w=560, seed=None, min_w=0, hl="terra"):
    return card(text, size=size, font_name="body", bg=bg, color=color, pad=(24, 12), max_w=max_w, min_w=min_w,
                seed=_seed(text) + 11 if seed is None else seed, hl=hl)


def greek_letter_medal(letter, diam=120, bg="cream", color="terra", seed=None):
    seed = _seed(letter) if seed is None else seed
    med = greek.medallion(diam, None, bg=bg, ring="black", seed=seed)
    num = greek.title_block(letter, size=int(diam * 0.62), color=color, tracking=0)
    return compose([(med, 0, 0), (Sprite(num.img, shadow=False), 0, int(diam * 0.03))])


# ----------------------------------------------------------------------------
# scene templates
# ----------------------------------------------------------------------------
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
    owl = sc.owl(W / 2, 790, scale=0.62, at=0.9, enter="slide_u", z=5, talk=True)
    sc.cursor = max(sc.cursor, t_j - 0.6)
    if narration:
        sc.say(narration)
    owl.mood(sc.cursor - 0.3, "wow", "wide")
    sc.wait(0.6)
    return sc


def section_scene(movie, numeral, title, narration=None, sub=None):
    """Section divider: Greek numeral medallion + title, with the lyre motif."""
    sc = movie.scene("section:" + title, bg="terra", lead=0.35, transition="wipe")
    t_j = sc.jingle(0.45, "section", gain=0.42)
    medal = greek_letter_medal(numeral, diam=250, seed=41)
    sc.add(medal, W / 2, 360, at=0.5, enter="pop", z=2)
    ttl = card(title, size=72, font_name="title", bg="cream", color="black", pad=(50, 20), seed=42, max_w=1500)
    sc.add(ttl, W / 2, 620, at=0.9, enter="drop", z=3, rot=-1)
    if sub:
        st = card(sub, size=40, font_name="body9", bg="gold", color="black", pad=(26, 10), seed=43, max_w=1400)
        sc.add(st, W / 2, 620 + ttl.h / 2 + 50, at=1.3, enter="pop", z=4, rot=1.5)
    sc.cursor = max(sc.cursor, t_j - 0.5)
    if narration:
        sc.say(narration)
    sc.wait(0.4)
    return sc


def key_idea(movie, text, spoken, extra=None, size=54, max_w=1100, tts=None):
    """End-of-section recap: the owl presents the key idea on a laurel card."""
    sc = movie.scene("idea", bg="paper", lead=0.5, transition="cut", sweep=True)
    owl = sc.owl(300, 640, scale=0.9, at=0.3, enter="slide_l", z=5)
    hd = header("IDEA CLAVE", bg="gold", color="black", size=44)
    sc.add(hd, 1160, 250, at=0.5, enter="drop", rot=-2, z=2)
    body = card(text, size=size, font_name="body9", bg="cream", max_w=max_w, pad=(56, 30), seed=_seed(text),
                line_spacing=1.12, hl="terra")
    e = sc.add(body, 1160, 250 + hd.h / 2 + body.h / 2 + 10, at=0.8, enter="drop", rot=1, z=1)
    lr = greek.laurel(150, seed=_seed(text) + 5)
    sc.add(lr, 1160 - body.w / 2 - 20, 250 + hd.h / 2 + body.h + 10, at=1.2, enter="pop", z=3, rot=-20)
    sc.add(lr, 1160 + body.w / 2 + 20, 250 + hd.h / 2 + body.h + 10, at=1.3, enter="pop", z=3, rot=20)
    sc.wait(0.2)
    ln = sc.say(spoken, tts=tts)
    owl.mood(ln.start(), "wow", "wide")
    e.pulse(ln.end(-0.4), 0.05)
    if extra:
        extra(sc, ln)
    sc.wait(0.5)
    return sc

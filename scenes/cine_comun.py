"""Piezas comunes de los vídeos de Cinemática (temas 2 a 5): portada, repaso, cierre, ciclistas,
fotos estroboscópicas, cronómetro y utilidades de tiempo."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stopmo import fisica as F, greek, kit, movie  # noqa: E402
from stopmo.fisica import formula, mg, live, prog, lerp2  # noqa: E402
from stopmo.gfx import W, H, card  # noqa: E402
from stopmo.movie import Movie  # noqa: E402

put, scn = F.put, F.scn

F.enable_spoken_numbers()
movie.PRONOUNCE.update({
    r"(?<![\w/])m/s²": "metros por segundo al cuadrado", r"(?<![\w/])m/s(?![\w²])": "metros por segundo",
    r"(?<![\w/])km/h(?!\w)": "kilómetros por hora",
    r"\bMRUA\b": "eme, erre, u, a", r"\bMRU\b": "eme, erre, u",
    r"\bx-t\b": "posición-tiempo", r"\bv-t\b": "velocidad-tiempo", r"\ba-t\b": "aceleración-tiempo",
})


def new_movie():
    return Movie(voice="davefx", speed=0.9, wipe="fisica", flicker=0.0)


def dur(mv, text):
    """seconds the narrator needs for `text` (synthesised now and cached)"""
    sents = [s for s in movie._SENT.split(text.strip()) if s.strip()]
    total = 0.0
    for s in sents:
        total += len(mv.voice.synth(movie.tts_text(s))) / movie.SR + 0.3
    return total - 0.3


# ----------------------------------------------------------------------------
# portada, repaso y cierre
# ----------------------------------------------------------------------------
def portada(mv, big, sub, narration, rider="ana", deco=("stopwatch", "speedometer")):
    sc = mv.scene("title", bg="kraft", lead=0.2, transition="cut")
    t_j = sc.jingle(0.25, "fis_intro", gain=0.45)
    ttl = greek.title_block(big, size=168 if len(big) < 9 else 130, color="cream", tracking=0.05, font_name="body9")
    sc.add(ttl, W / 2, 330, at=0.6, enter="drop", z=2, jitter=0.6)
    sb = card(sub, size=60, font_name="body9", bg="cream", color="ink", pad=(46, 16), seed=F._seed(sub),
              border=("pos", 5), max_w=1500)
    sc.add(sb, W / 2, 520, at=1.0, enter="drop", z=3, rot=-1.5)
    tag = card("Física y Química · Cinemática", size=32, font_name="body9", bg="mustard", color="ink", pad=(22, 8),
               seed=34)
    sc.add(tag, W / 2 + sb.w / 2 - 120, 440, at=1.4, enter="pop", z=4, rot=4)
    if rider:
        def ride(t):
            x = -300 + 300 * max(0.0, t - 0.4)
            return F.bike_at(rider, x, 1, 200), x, 830, 0.0
        live(sc, ride, at=0.4, z=1, jitter=0.6)
    sc.add(F.medal(deco[0], 150, bg="pos_l"), 250, 300, at=1.2, enter="pop", z=2, rot=-6)
    sc.add(F.medal(deco[1], 150, bg="vel_l"), W - 250, 300, at=1.35, enter="pop", z=2, rot=6)
    sc.cursor = max(sc.cursor, t_j - 0.7)
    sc.say(narration)
    sc.wait(0.5)
    return sc


def resumen(mv, title, rows, intro="Repaso rápido del tema.", size=40):
    """rows = [(formula_src, spoken)]"""
    sc = scn(mv, "resumen", bg="kraft", lead=0.4, transition="wipe")
    F.title(sc, title, at=0.3, y=140, size=56)
    sc.say(intro)
    y = 240
    for i, (src, spoken) in enumerate(rows):
        ln = sc.say(spoken)
        c = F.fcard(src, size=size, align="l", pad=(30, 12), min_w=1560)
        put(sc, c, W / 2, y + c.vh / 2, ln.start(), enter="slide_r", rot=((i % 2) - 0.5) * 0.8)
        y += c.vh + 10
    sc.wait(0.8)
    return sc


def fin(mv, n, proximo, narration):
    sc = mv.scene("fin", bg="kraft", transition="wipe", lead=0.3)
    put(sc, greek.title_block("FIN DEL TEMA %d" % n, size=120, color="cream", tracking=0.05, font_name="body9"),
        W / 2, 300, 0.4, rot=0)
    ln = sc.say(narration)
    if proximo:
        put(sc, card(proximo, size=56, font_name="body9", bg="cream", pad=(40, 14), seed=1601 + n, border=("pos", 4)),
            W / 2, 470, ln.start(1.0), enter="drop", rot=-1)

    def ride(t):
        x = -300 + 300 * t
        return F.bike_at("ana", x, 1, 200), x, 780, 0.0
    live(sc, ride, at=0.2, z=1, jitter=0.6)
    sc.wait(0.3)
    sc.jingle(sc.now(), "fis_outro", gain=0.45)
    put(sc, card("Iconos: game-icons.net (CC BY 3.0) · Voz: Piper davefx · Hecho con Python", size=26,
                 font_name="body7", bg="cream", pad=(20, 8), seed=1602), W / 2, 960, sc.now(), enter="pop", rot=0)
    sc.wait(4.0)
    return sc


# ----------------------------------------------------------------------------
# calle con carril bici (vista lateral)
# ----------------------------------------------------------------------------
def street(sc, ground=640.0, at=0.0, lane=True, z=-1):
    def fn(L, t):
        L.poly([(-20, ground), (W + 20, ground), (W + 20, H + 20), (-20, H + 20)], fill="concrete")
        if lane:
            L.poly([(-20, ground), (W + 20, ground), (W + 20, ground + 34), (-20, ground + 34)], fill=(150, 72, 52))
            for x in range(0, W + 40, 90):
                L.line([(x, ground + 17), (x + 46, ground + 17)], "cream", 4)
        L.line([(-20, ground + 36), (W + 20, ground + 36)], "concrete_d", 6)
    return mg(sc, fn, at=at, z=z, shadow=False)


def bike_ground_offset(h=250, scale=1.0):
    """distance from the bike sprite's centre to the ground (bottom of the wheels)"""
    s = h / 250.0
    hh = int(h + 40 * s)
    return (hh / 2 - 6 * s) * scale


def rider_live(sc, rider, xfun, ground, face=1, h=210, at=0.0, until=None, z=4):
    """a cyclist whose reference point (between the wheels, on the ground) is at screen x = xfun(t)"""
    off = bike_ground_offset(h)
    x_start = xfun(at)

    def fn(t):
        x = xfun(t)
        return F.bike_at(rider, abs(x - x_start), face, h), x, ground - off, 0.0
    return live(sc, fn, at=at, until=until, z=z, jitter=0.6)


def ghost_live(sc, rider, x, ground, face=1, h=210, at=0.0, until=None, alpha=0.32, z=2):
    off = bike_ground_offset(h)
    spr = F.ghost(F.bike_sprite(rider, 0, face, h), alpha)
    return live(sc, lambda t: (spr, x, ground - off, 0.0), at=at, until=until, z=z, jitter=0.0, shadow=False)


def stopwatch(sc, x, y, clock, at, d=210, until=None, label=True, z=5):
    """stopwatch piece + motion-graphics hand; clock(t) -> simulated seconds"""
    sw, off = F.stopwatch_piece(d)
    e = put(sc, sw, x, y, at, enter="pop", rot=0, z=z, until=until)

    def fn(L, t):
        c = clock(t)
        F.stopwatch_hand(L, x + off[0], y + off[1], d, c)
        if label:
            L.stamp(F.tag_img(r"t = %s\,\t{s}" % F.num(c), 40, "ink", border=("ink", 3), pad=(14, 4)), x,
                    y + d * 0.5 + 60)
    m = mg(sc, fn, at=at + 0.3, until=until, z=z + 1)
    return e, m


# a word that is not in the sentence would silently fall back to the start of the line: fail loudly instead
_orig_at = movie.Line.at


def _strict_at(self, word, n=1, after=0.0):
    if word.lower() not in self.plain.lower():
        raise KeyError(f"«{word}» no está en: {self.plain}")
    return _orig_at(self, word, n, after)


movie.Line.at = _strict_at


def axis_x(L, x0, x1, y, ppm, step=5, until_m=None, color="ink", label=r"x\;\t{(m)}", origin=True, size=26, g=1.0,
           neg=0.0):
    """horizontal axis along a street: origin at screen x0, ticks every `step` metres"""
    xe = x0 - neg + (x1 - x0 + neg) * g
    L.arrow((x0 - neg, y), (xe, y), color, 5, head=22)
    if g < 1:
        return
    m = 0
    while x0 + m * ppm < x1 - 30 and (until_m is None or m <= until_m):
        xx = x0 + m * ppm
        L.line([(xx, y - 9), (xx, y + 9)], color, 3)
        L.stamp(formula(r"\t{%d}" % m, size), xx, y + 26)
        m += step
    L.stamp(formula(label, size + 2), x1 + 10, y, "lm")
    if origin:
        L.stamp(formula("O", size + 6), x0 - 20, y - 26)

"""Física · Cinemática · Tema 4: caída libre y lanzamientos verticales.

Suelo como origen y eje Y positivo hacia arriba; la gravedad siempre hacia abajo: a = −9,8 m/s².
Caída desde el reposo, lanzamiento hacia arriba (pausa en la altura máxima: v = 0 y a = −g) y lanzamiento
hacia abajo, con fotos cada medio segundo → resumen de signos → comprobación → una caída y un lanzamiento
resueltos paso a paso → repaso. Sin azul.

    python3 scenes/cinematica_t4.py out/Cinematica_T4_Caida_libre.mp4
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cine_comun as K  # noqa: E402
from cine_comun import F, W, H, card, kit, formula, mg, live, prog, lerp2, put, scn  # noqa: E402

G = 9.8
GROUND = 880.0        # screen y of the ground (y = 0 m)
PX = 30.0             # px per metre
AX = 230.0            # screen x of the Y axis
VS = 7.0              # px per m/s for the velocity arrows
BALL_R = 20


def Y(y):
    """screen y of the ball's centre for a height y (the ball's bottom touches y)"""
    return GROUND - y * PX - BALL_R


def scene_base(sc, ymax=25, at=0.0, axis=True):
    """sky, ground and the vertical axis with the origin on the ground"""
    def ground(L, t):
        L.poly([(-20, GROUND), (W + 20, GROUND), (W + 20, H + 20), (-20, H + 20)], fill="grass")
        L.line([(-20, GROUND + 2), (W + 20, GROUND + 2)], "grass_d", 6)
    mg(sc, ground, at=at, z=-1, shadow=False)
    if axis:
        def ax(L, t):
            g = prog(t, at + 0.2, 0.7, "out")
            top = GROUND - ymax * PX - 20
            L.arrow((AX, GROUND + 14), (AX, GROUND + 14 - (GROUND + 14 - top) * g), "ink", 5, head=22)
            if g < 1:
                return
            for m in range(5, ymax + 1, 5):
                yy = GROUND - m * PX
                L.line([(AX - 9, yy), (AX + 9, yy)], "ink", 3)
                L.stamp(formula(r"\t{%d}" % m, 26), AX - 16, yy, "rm")
            L.stamp(formula(r"y\;\t{(m)}", 30), AX + 16, top + 4, "lm")
            L.stamp(formula("O", 32), AX - 26, GROUND + 22)
            L.arrow((AX - 80, GROUND - 40), (AX - 80, GROUND - 130), "pos", 6, head=20)
            L.stamp(formula(r"+", 40, "pos"), AX - 112, GROUND - 100)
        mg(sc, ax, at=at, z=6)


def gravity_badge(sc, at, x=1700, y=170, until=None):
    def fn(L, t):
        g = prog(t, at, 0.4, "out")
        L.arrow((x - 170, y - 40), (x - 170, y - 40 + 90 * g), "acc", 10, head=30)
        L.stamp(F.tag_img(r"\c{acc}{a} = −g = −9,8\,\t{m/s}^2", 36, "ink", border=("acc", 3), pad=(12, 6)), x + 20, y,
                alpha=g)
        L.stamp(F.formula(r"\t{siempre}", 28, "acc_d"), x + 20, y + 44, alpha=g)
    return mg(sc, fn, at=at, until=until, z=8)


def ball_arrows(L, x, y_m, v, show_v=True, show_a=True, alpha=1.0):
    """velocity (magenta, right of the ball) and acceleration (red, left of the ball)"""
    cy = Y(y_m)
    if show_v and abs(v) > 0.05:
        L.arrow((x + 44, cy), (x + 44, cy - v * VS), "vel", 8, head=24, alpha=alpha)
    if show_a:
        L.arrow((x - 44, cy), (x - 44, cy + G * VS), "acc", 8, head=24, alpha=alpha)


def intro(mv):
    K.portada(mv, "CAÍDA LIBRE", "Tema 4 · Caída libre y lanzamientos verticales",
              "Cinemática. Tema cuatro: la caída libre y los lanzamientos verticales.",
              deco=("stopwatch", "falling-rocks"))


# ============================================================================
# 1. el sistema de referencia y la gravedad
# ============================================================================
def sistema(mv):
    sc = scn(mv, "sistema", bg="sky", lead=0.4, transition="wipe")
    scene_base(sc, ymax=25, at=0.3)
    bld = F.building_piece(w=260, h=int(19.6 * PX) + 30, floors=7, seed=322)
    BX = 520.0
    put(sc, bld, BX, GROUND - bld.vh / 2, 0.2, rot=0, z=0, enter="cut")
    l1 = sc.say("Hasta ahora, los móviles iban en horizontal. Ahora vamos a dejar caer cosas, y a lanzarlas hacia "
                "arriba y hacia abajo.")
    l2 = sc.say("Primero, el sistema de referencia: el origen, en el suelo, y el eje Y vertical, con el sentido "
                "positivo hacia arriba.")
    put(sc, F.say_card("Origen en el {pos:suelo} · eje Y {pos:hacia arriba}", size=40, border=("pos", 3)), 1290, 300,
        l2.at("origen"), z=7)
    l3 = sc.say("Así, la altura es la coordenada y: en el suelo vale cero, y en la azotea de este edificio, 19,6 "
                "metros.")
    mg(sc, lambda L, t: (L.line([(AX, GROUND - 19.6 * PX), (BX + 130, GROUND - 19.6 * PX)], "pos", 3, dash=[10, 8],
                                alpha=prog(t, l3.at("azotea"), 0.4)),
                         L.stamp(F.tag_img(r"y = 19,6\,\t{m}", 34, "pos_d", border=("pos", 3)), BX + 260,
                                 GROUND - 19.6 * PX, alpha=prog(t, l3.at("azotea"), 0.4))), at=l3.at("azotea"), z=7)
    l4 = sc.say("Si despreciamos el rozamiento del aire, todo cae con la misma aceleración: la de la gravedad, g, 9,8 "
                "m/s².")
    l5 = sc.say("La gravedad apunta siempre hacia abajo. Y como nuestro eje positivo va hacia arriba, la aceleración "
                "es negativa: menos 9,8 m/s². Siempre: cuando el cuerpo sube, cuando baja, y cuando está arriba del "
                "todo.")
    gravity_badge(sc, l5.at("negativa"), x=1500, y=500)
    l6 = sc.say("Así que el movimiento vertical es un MRUA. Usamos sus mismas ecuaciones, cambiando equis por i "
                "griega, y con a igual a menos 9,8.")
    put(sc, F.def_card("MOVIMIENTO VERTICAL (MRUA)", [r"y = y_0 + v_0\,t + \frac{1}{2}\,a\,t^2",
                                                      r"v = v_0 + a\,t \qquad v^2 = v_0^2 + 2\,a\,(y − y_0)",
                                                      r"\c{acc}{a = −9,8\,\t{m/s}^2}"], head_bg="acc", size=40,
                       border=("acc", 4)), 1380, 720, l6.at("MRUA"), z=8)
    sc.wait(0.6)


# ============================================================================
# 2. caída desde el reposo
# ============================================================================
def caida(mv):
    sc = scn(mv, "caida", bg="sky", lead=0.4)
    scene_base(sc, ymax=25, at=0.0)
    bld = F.building_piece(w=260, h=int(19.6 * PX) + 30, floors=7, seed=322)
    BX = 520.0
    put(sc, bld, BX, GROUND - bld.vh / 2, 0.0, rot=0, z=0, enter="cut")
    leo = F.leo_sprite(290)
    put(sc, leo, BX + 95, GROUND - 19.6 * PX - leo.vh * 0.45 / 2 + 4, 0.2, rot=0, z=2, scale=0.45, enter="drop")
    XB = BX + 175.0               # x of the ball path (just off the roof edge)
    y0 = 19.6
    l1 = sc.say("Primera situación: Leo deja caer una pelota desde la azotea, a 19,6 metros. Velocidad inicial: "
                "cero.")
    l2 = sc.say("Le hacemos una foto cada medio segundo.")
    t0 = l2.end(0.3)
    k_slow = 2.0                  # the 2 s of the fall, shown in 4 s
    sc.cursor = max(sc.cursor, t0 + 2 * k_slow + 0.3)

    def sim(t):
        return min(max(0.0, (t - t0) / k_slow), 2.0)

    def y_of(s):
        return y0 - 0.5 * G * s * s
    ball = F.ball_piece(BALL_R)
    live(sc, lambda t: (ball, XB, Y(y_of(sim(t))), 0.0), at=l1.at("deja caer"), z=5, jitter=0.3)
    gh = F.ghost(ball, 0.35)
    for k in range(5):
        s = 0.5 * k
        live(sc, lambda t, s=s: (gh, XB, Y(y_of(s)), 0.0), at=t0 + s * k_slow, z=3, jitter=0.0, shadow=False)
        sc.sfx(t0 + s * k_slow, F.tick(0.06, seed=k % 2))
    K.stopwatch(sc, 1700, 200, lambda t: sim(t), at=l2.start(), d=160)
    l3 = sc.say("Cae cada vez más deprisa: entre foto y foto, recorre cada vez más metros.")
    l4 = sc.say("Su velocidad apunta hacia abajo, así que es negativa, y cada segundo aumenta 9,8 m/s. La "
                "aceleración, también hacia abajo, no cambia.")

    def arrows(L, t):
        s = sim(t)
        if t < l4.at("velocidad"):
            return
        a = prog(t, l4.at("velocidad"), 0.4)
        for k in range(5):
            sk = 0.5 * k
            v = -G * sk
            L.arrow((XB + 44, Y(y_of(sk))), (XB + 44, Y(y_of(sk)) - v * VS * a), "vel", 6, head=20, alpha=0.8)
            L.stamp(F.formula(r"\t{%s m/s}" % (F.num(v, 1) if abs(v) > 0.05 else "0"), 24, "vel_d"), XB + 110,
                    Y(y_of(sk)), "lm", alpha=a)
        b = prog(t, l4.at("aceleración"), 0.4)
        if b > 0:
            for k in range(5):
                sk = 0.5 * k
                L.arrow((XB - 44, Y(y_of(sk))), (XB - 44, Y(y_of(sk)) + G * VS * b), "acc", 6, head=20)
    mg(sc, arrows, at=l4.at("velocidad"), z=6)
    gravity_badge(sc, l4.at("aceleración"), x=1560, y=430)
    l5 = sc.say("Sus ecuaciones: i griega igual a 19,6 menos 4,9 te al cuadrado. Y uve igual a menos 9,8 te. Llega "
                "al suelo a los 2 segundos, a menos 19,6 m/s.")
    put(sc, F.fcard([r"y = 19,6 − 4,9\,t^2", r"v = −9,8\,t", r"t = 2\,\t{s}: \; y = 0,\; v = −19,6\,\t{m/s}"], size=40,
                    border=("pos", 3), align="l"), 1420, 690, l5.at("ecuaciones"), z=7)
    sc.wait(0.6)


# ============================================================================
# 3. lanzamiento hacia arriba, con pausa en la altura máxima
# ============================================================================
def arriba(mv):
    sc = scn(mv, "arriba", bg="sky", lead=0.4)
    scene_base(sc, ymax=25, at=0.0)
    ana = F.ana_arm_up(290)
    XB = 760.0
    put(sc, ana, XB - 52, GROUND - ana.vh * 0.7 / 2 + 6, 0.2, rot=0, z=2, scale=0.7)
    v0 = 19.6
    l1 = sc.say("Segunda situación: Ana lanza la pelota hacia arriba desde el suelo, a 19,6 m/s. Va hacia arriba, "
                "así que su velocidad inicial es positiva.")
    put(sc, F.fcard([r"y_0 = 0", r"v_0 = +19,6\,\t{m/s}", r"a = −9,8\,\t{m/s}^2"], size=40, border=("pos", 3),
                    align="l"), 1500, 260, l1.at("positiva"), z=7)
    l2 = sc.say("Mientras sube, va cada vez más despacio.")
    t0 = l2.start(-0.2)
    k_slow = 1.8
    state = {"t_freeze": 1e9, "t_resume": 1e9}

    def sim(t):
        up = (t - t0) / k_slow
        if t < state["t_freeze"]:
            return min(max(0.0, up), 2.0)
        if t < state["t_resume"]:
            return 2.0
        return min(2.0 + (t - state["t_resume"]) / k_slow, 4.0)

    def y_of(s):
        return v0 * s - 0.5 * G * s * s

    def v_of(s):
        return v0 - G * s
    sc.cursor = max(sc.cursor, t0 + 2.0 * k_slow)
    state["t_freeze"] = t0 + 2.0 * k_slow
    sc.sfx(state["t_freeze"], F.tick(0.12, seed=3))
    l3 = sc.say("¡Pausa! Detenemos la imagen en el punto más alto.")
    l4 = sc.say("Aquí la velocidad es cero: la pelota ni sube ni baja. Pero la aceleración no es cero: sigue siendo "
                "menos 9,8, hacia abajo.")
    l5 = sc.say("Si fuera cero, la pelota se quedaría flotando ahí arriba para siempre.")
    l6 = sc.say("Seguimos. Ahora baja cada vez más deprisa.")
    state["t_resume"] = l6.at("Seguimos", after=0.4)
    sc.cursor = max(sc.cursor, state["t_resume"] + 2.0 * k_slow + 0.3)
    ball = F.ball_piece(BALL_R)
    live(sc, lambda t: (ball, XB + (60 if sim(t) > 2.0 else 0) * min(1.0, (sim(t) - 2.0) * 3) if sim(t) > 2 else XB,
                        Y(y_of(sim(t))), 0.0), at=t0, z=5, jitter=0.3)
    gh = F.ghost(ball, 0.35)
    for k in range(9):
        s = 0.5 * k
        tk = t0 + s * k_slow if s <= 2.0 else state["t_resume"] + (s - 2.0) * k_slow
        xk = XB if s <= 2.0 else XB + 60
        live(sc, lambda t, s=s, xk=xk: (gh, xk, Y(y_of(s)), 0.0), at=tk, z=3, jitter=0.0, shadow=False)
    K.stopwatch(sc, 1720, 470, lambda t: sim(t), at=l1.start(), d=150)

    def arrows(L, t):
        s = sim(t)
        x = XB if s <= 2.0 else XB + 60
        frozen = state["t_freeze"] <= t < state["t_resume"]
        ball_arrows(L, x, y_of(s), v_of(s), show_v=True, show_a=True)
        if abs(v_of(s)) > 0.05:
            L.stamp(F.tag_img(r"v = %s\,\t{m/s}" % F.num(v_of(s), 1), 28, "vel_d", border=("vel", 2), pad=(8, 2)),
                    x + 150, Y(y_of(s)) - 10)
        if frozen:
            g = prog(t, state["t_freeze"], 0.3, "out")
            L.stamp(F.tag_img(r"v = 0", 44, "vel_d", border=("vel", 3), pad=(12, 4)), x + 130, Y(y_of(s)) - 30,
                    alpha=g)
            L.stamp(F.tag_img(r"a = −9,8\,\t{m/s}^2", 40, "acc_d", border=("acc", 3), pad=(12, 4)), x - 210,
                    Y(y_of(s)) + 120, alpha=prog(t, l4.at("aceleración"), 0.3))
            L.stamp(F.tag_img(r"\b{PAUSA}", 40, "cream", bg=(40, 31, 26, 230), pad=(16, 6)), x + 26, Y(y_of(s)) - 120,
                    alpha=g)
            for dx in (-100, -82):
                L.poly([(x + dx, Y(y_of(s)) - 140), (x + dx + 11, Y(y_of(s)) - 140), (x + dx + 11, Y(y_of(s)) - 100),
                        (x + dx, Y(y_of(s)) - 100)], fill="ink", alpha=g)
            L.line([(AX, GROUND - y_of(s) * PX), (x - 60, GROUND - y_of(s) * PX)], "pos", 3, dash=[10, 8], alpha=g)
            L.stamp(F.tag_img(r"y_{máx} = 19,6\,\t{m}", 32, "pos_d", border=("pos", 2)), AX + 140,
                    GROUND - y_of(s) * PX - 30, alpha=g)
    mg(sc, arrows, at=t0, z=6)
    put(sc, kit.ojo("En la altura máxima: {b:v = 0}, pero la aceleración\n{red|b:sigue siendo −9,8 m/s²}.", size=34,
                    max_w=1000), 1330, 790, l4.at("no es cero"), z=8, until=l6.at("Seguimos"))
    l7 = sc.say("Comprobación visual: al bajar, pasa por cada altura con la misma rapidez que al subir, pero hacia "
                "abajo. Y llega al suelo a los 4 segundos, a menos 19,6 m/s.")

    def sym(L, t):
        g = prog(t, l7.at("misma rapidez"), 0.5)
        for s_up, s_dn in ((0.5, 3.5), (1.0, 3.0), (1.5, 2.5)):
            yy = Y(y_of(s_up))
            L.stamp(F.formula(r"\t{%s}" % F.num(v_of(s_up), 1), 24, "vel_d"), XB - 100, yy, "rm", alpha=g)
            L.stamp(F.formula(r"\t{%s}" % F.num(v_of(s_dn), 1), 24, "vel_d"), XB + 60 + 100, yy, "lm", alpha=g)
    mg(sc, sym, at=l7.at("misma rapidez"), z=6)
    sc.wait(0.5)


# ============================================================================
# 4. lanzamiento hacia abajo
# ============================================================================
def abajo(mv):
    sc = scn(mv, "abajo", bg="sky", lead=0.4)
    scene_base(sc, ymax=25, at=0.0)
    bld = F.building_piece(w=260, h=int(19.6 * PX) + 30, floors=7, seed=322)
    BX = 520.0
    put(sc, bld, BX, GROUND - bld.vh / 2, 0.0, rot=0, z=0, enter="cut")
    y0, v0 = 14.7, -9.8
    YB = GROUND - y0 * PX

    def balcony(L, t):
        L.poly([(BX + 120, YB), (BX + 200, YB), (BX + 200, YB + 14), (BX + 120, YB + 14)], fill="brown")
        L.line([(BX + 130, YB), (BX + 130, YB - 50), (BX + 196, YB - 50), (BX + 196, YB)], "ink", 4)
    mg(sc, balcony, at=0.0, z=1)
    leo = F.leo_sprite(290)
    put(sc, leo, BX + 160, YB - leo.vh * 0.45 / 2 + 4, 0.2, rot=0, z=2, scale=0.45)
    XB = BX + 250.0
    l1 = sc.say("Tercera situación: desde un balcón a 14,7 metros, Leo lanza la pelota hacia abajo, a 9,8 m/s.")
    l2 = sc.say("Ojo con el signo: va hacia abajo, así que su velocidad inicial es negativa, menos 9,8. Y la "
                "aceleración, como siempre, menos 9,8.")
    put(sc, F.fcard([r"y_0 = 14,7\,\t{m}", r"\c{vel}{v_0 = −9,8\,\t{m/s}}", r"a = −9,8\,\t{m/s}^2"], size=40,
                    border=("vel", 3), align="l"), 1500, 260, l2.at("negativa"), z=7)
    l3 = sc.say("Fotos cada cuarto de segundo:")
    t0 = l3.end(0.2)
    k_slow = 3.0
    sc.cursor = max(sc.cursor, t0 + 1.0 * k_slow + 0.3)

    def sim(t):
        return min(max(0.0, (t - t0) / k_slow), 1.0)

    def y_of(s):
        return y0 + v0 * s - 0.5 * G * s * s
    ball = F.ball_piece(BALL_R)
    live(sc, lambda t: (ball, XB, Y(y_of(sim(t))), 0.0), at=l1.at("lanza"), z=5, jitter=0.3)
    gh = F.ghost(ball, 0.35)
    for k in range(5):
        s = 0.25 * k
        live(sc, lambda t, s=s: (gh, XB, Y(y_of(s)), 0.0), at=t0 + s * k_slow, z=3, jitter=0.0, shadow=False)
    K.stopwatch(sc, 1720, 580, lambda t: sim(t), at=l3.start(), d=150)
    mg(sc, lambda L, t: ball_arrows(L, XB, y_of(sim(t)), v0 - G * sim(t)), at=t0 - 0.5, z=6)
    l4 = sc.say("Llega al suelo en solo 1 segundo, a menos 19,6 m/s: antes y más deprisa que si la dejara caer.")
    put(sc, F.fcard([r"y = 14,7 − 9,8\,t − 4,9\,t^2", r"t = 1\,\t{s}:\; v = −19,6\,\t{m/s}"], size=40,
                    border=("pos", 3), align="l"), 1440, 820, l4.at("Llega"), z=7)
    sc.wait(0.6)


# ============================================================================
# 5. las tres situaciones y la comprobación de la altura máxima
# ============================================================================
def tres(mv):
    sc = scn(mv, "tres", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "LAS TRES SITUACIONES (EJE Y HACIA ARRIBA)", at=0.3, size=46)
    l1 = sc.say("Resumen de signos, con el eje hacia arriba.")
    rows = [("CAÍDA DESDE EL REPOSO", r"v_0 = 0", r"y_0\t{ = altura de partida}", "falling-rocks", 330,
             "Caída desde el reposo: velocidad inicial cero, y la posición inicial es la altura desde la que cae."),
            ("LANZAMIENTO HACIA ARRIBA", r"v_0 > 0", r"\t{en la altura máxima }v = 0", "rocket-flight", 530,
             "Lanzamiento hacia arriba: velocidad inicial positiva, y en la altura máxima, velocidad cero."),
            ("LANZAMIENTO HACIA ABAJO", r"v_0 < 0", r"y_0\t{ = altura de partida}", "falling-rocks", 730,
             "Lanzamiento hacia abajo: velocidad inicial negativa.")]
    for k, (head, c1, c2, ic, y, spoken) in enumerate(rows):
        ln = sc.say(spoken)
        put(sc, F.say_card(head, size=34, bg="mustard", border=None), 420, y, ln.start(), z=5, enter="slide_l")
        put(sc, F.fcard(c1, size=44, border=("vel", 3)), 860, y, ln.start(0.4), z=5)
        put(sc, F.fcard(r"a = −9,8\,\t{m/s}^2", size=40, border=("acc", 3)), 1200, y, ln.start(0.7), z=5)
        put(sc, F.fcard(c2, size=36, border=("pos", 3)), 1600, y, ln.start(1.0), z=5)
    l5 = sc.say("En las tres, la aceleración es la misma: menos 9,8.")
    sc.wait(0.6)

    sc = scn(mv, "check-max", bg="grid", lead=0.3)
    l1 = sc.say("Comprueba: en la altura máxima de un lanzamiento hacia arriba, ¿cuánto valen la velocidad y la "
                "aceleración?")
    F.quiz(sc, "En la altura máxima, ¿cuánto valen v y a?", lead=l1.start(), y=200, size=44)
    opts = [("A", r"v = 0\qquad a = 0", 420), ("B", r"v = 0\qquad a = −9,8\,\t{m/s}^2", 960),
            ("C", r"v = −9,8\,\t{m/s}\qquad a = 0", 1500)]
    for k, (lab, src, x) in enumerate(opts):
        put(sc, F.fcard([r"\b{%s}" % lab, src], size=40, border=("ink", 2)), x, 480, l1.at("cuánto valen", after=0.2 * k),
            enter="pop", z=5)
    t_r = F.think(sc, 4.0)
    l2 = sc.say("La B: la velocidad es cero en ese instante, pero la aceleración sigue siendo menos 9,8. Es el error "
                "más típico del tema: no lo cometas.")
    put(sc, F.check_mark(110), 960 + 250, 430, t_r, enter="pop", z=6)
    put(sc, F.check_mark(90, ok=False), 420 + 180, 430, t_r + 0.3, enter="pop", z=6)
    put(sc, F.check_mark(90, ok=False), 1500 + 260, 430, t_r + 0.5, enter="pop", z=6)
    put(sc, kit.ojo("v = 0 no significa a = 0.", size=40, max_w=900), W / 2, 740, l2.at("error"), z=7)
    sc.wait(0.6)


# ============================================================================
# 6. problemas resueltos paso a paso
# ============================================================================
def problema_caida(mv):
    sc = scn(mv, "prob-caida", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "PROBLEMA 1 · UNA CAÍDA", at=0.3)
    st = F.tabbed(F.say_card("Se deja caer una piedra desde lo alto de una torre de {pos:44,1 m}.\n"
                             "a) ¿Cuánto tarda en llegar al suelo?  b) ¿Con qué velocidad llega?", size=34,
                             max_w=820, border=("mustard", 3)), "ENUNCIADO", head_bg="mustard", head_color="ink")
    l1 = sc.say("Primer problema. Se deja caer una piedra desde lo alto de una torre de 44,1 metros. ¿Cuánto tarda en "
                "llegar al suelo? ¿Y con qué velocidad llega?")
    put(sc, st, 500, 270, l1.start(), z=6)
    # small diagram on the left
    gx, g0, gs = 300.0, 860.0, 9.0           # axis x, ground y, px per metre
    l2 = sc.say("Paso uno: el eje. Origen en el suelo y sentido positivo hacia arriba.")

    def diagram(L, t):
        a = prog(t, l2.at("eje"), 0.6, "out")
        L.line([(120, g0), (900, g0)], "grass_d", 6, alpha=a)
        L.arrow((gx, g0 + 10), (gx, g0 + 10 - 440 * a), "ink", 5, head=22)
        if a < 1:
            return
        L.stamp(formula("O", 30), gx - 24, g0 + 22)
        L.stamp(formula(r"y\,\t{(m)}", 28), gx + 14, g0 - 440, "lm")
        L.poly([(gx + 140, g0), (gx + 220, g0), (gx + 220, g0 - 44.1 * gs), (gx + 140, g0 - 44.1 * gs)], fill="concrete",
               stroke="concrete_d", width=3)
        b = prog(t, l3.at("Datos"), 0.4)
        L.line([(gx, g0 - 44.1 * gs), (gx + 140, g0 - 44.1 * gs)], "pos", 3, dash=[8, 7], alpha=b)
        L.stamp(F.tag_img(r"y_0 = 44,1\,\t{m}", 30, "pos_d"), gx + 70, g0 - 44.1 * gs - 30, alpha=b)
        L.circle(gx + 250, g0 - 44.1 * gs - 14, 13, fill="brown", alpha=b)
        L.arrow((gx + 300, g0 - 44.1 * gs + 20), (gx + 300, g0 - 44.1 * gs + 110), "acc", 7, head=22, alpha=b)
        L.stamp(F.tag_img(r"a = −9,8", 28, "acc_d"), gx + 400, g0 - 44.1 * gs + 70, alpha=b)
        c = prog(t, l3.at("llega al suelo"), 0.4)
        L.stamp(F.tag_img(r"y = 0", 30, "pos_d"), gx + 250, g0 - 30, alpha=c)
    mg(sc, diagram, at=l2.at("eje"), z=5)
    l3 = sc.say("Paso dos: los datos, con signo. Posición inicial, 44,1 metros. Velocidad inicial, cero. Aceleración, "
                "menos 9,8. Y cuando llega al suelo, i griega vale cero.")
    sh = F.sheet(860, 760, seed=41)
    put(sc, sh, 1440, 560, l3.start(), rot=0.4, z=3)
    l4 = sc.say("Paso tres: la ecuación. Buscamos el tiempo, y conocemos la posición: usamos la de la posición.")
    l5 = sc.say("Paso cuatro: despejar. 0 igual a 44,1 menos 4,9 te al cuadrado. Te al cuadrado igual a 9, y te igual a "
                "3 segundos. La raíz negativa no vale: el tiempo no puede ser negativo.")
    l6 = sc.say("Apartado b: uve igual a uve cero más a por te: 0 menos 9,8 por 3, menos 29,4 m/s. El signo menos "
                "significa que va hacia abajo.")
    lines = [(r"y_0 = 44,1\,\t{m}\quad v_0 = 0\quad a = −9,8\,\t{m/s}^2\quad y = 0", l3.at("Posición inicial")),
             (r"y = y_0 + v_0\,t + \frac{1}{2}\,a\,t^2", l4.at("usamos")),
             (r"0 = 44,1 − 4,9\,t^2", l5.at("0 igual")),
             (r"t^2 = 9 \;\Rightarrow\; t = \c{pos}{3\,\t{s}}\quad\t{(no } −3\t{)}", l5.at("Te al cuadrado")),
             (r"\t{b) } v = 0 − 9,8 · 3 = \c{vel}{−29,4\,\t{m/s}}", l6.at("uve igual"))]
    F.board(sc, lines, 1040, 250, size=38, gap=34, z=5)
    l7 = sc.say("Paso cinco: comprobar. Con la ecuación sin tiempo: uve al cuadrado igual a 2 por menos 9,8 por menos "
                "44,1, que da 864,36. Su raíz, 29,4. ¡Coincide! Y el signo menos, hacia abajo, tiene sentido.")
    put(sc, F.fcard([r"v^2 = 2 · (−9,8) · (0 − 44,1) = 864,36", r"|v| = 29,4\,\t{m/s}\;\t{✓}"], size=36,
                    border=("grass_d", 3)), 1440, 820, l7.at("comprobar"), z=7)
    sc.wait(0.6)


def problema_lanzamiento(mv):
    sc = scn(mv, "prob-lanz", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "PROBLEMA 2 · UN LANZAMIENTO", at=0.3)
    st = F.tabbed(F.say_card("Desde una ventana a {pos:14,7 m} se lanza una pelota hacia arriba a {vel:9,8 m/s}.\n"
                             "a) ¿Altura máxima?  b) ¿Cuándo llega al suelo?  c) ¿Con qué velocidad?", size=33,
                             max_w=860, border=("mustard", 3)), "ENUNCIADO", head_bg="mustard", head_color="ink")
    l1 = sc.say("Segundo problema. Desde una ventana a 14,7 metros se lanza una pelota hacia arriba, a 9,8 m/s. ¿Qué "
                "altura máxima alcanza? ¿Cuándo llega al suelo? ¿Y con qué velocidad?")
    put(sc, st, 520, 270, l1.start(), z=6)
    l2 = sc.say("Eje con origen en el suelo y positivo hacia arriba. Datos: posición inicial 14,7 metros; velocidad "
                "inicial, más 9,8, porque sube; aceleración, menos 9,8.")
    gx, g0, gs = 300.0, 860.0, 18.0

    def diagram(L, t):
        a = prog(t, l2.at("Eje"), 0.6, "out")
        L.line([(120, g0), (900, g0)], "grass_d", 6, alpha=a)
        L.arrow((gx, g0 + 10), (gx, g0 + 10 - 470 * a), "ink", 5, head=22)
        if a < 1:
            return
        L.stamp(formula("O", 30), gx - 24, g0 + 22)
        for m in (5, 10, 15, 20):
            L.line([(gx - 8, g0 - m * gs), (gx + 8, g0 - m * gs)], "ink", 3)
            L.stamp(formula(r"\t{%d}" % m, 24), gx - 14, g0 - m * gs, "rm")
        L.poly([(gx + 120, g0), (gx + 220, g0), (gx + 220, g0 - 14.7 * gs), (gx + 120, g0 - 14.7 * gs)],
               fill="concrete", stroke="concrete_d", width=3)
        b = prog(t, l2.at("Datos"), 0.4)
        L.stamp(F.tag_img(r"y_0 = 14,7\,\t{m}", 28, "pos_d"), gx + 420, g0 - 14.7 * gs + 34, alpha=b)
        L.arrow((gx + 260, g0 - 14.7 * gs - 10), (gx + 260, g0 - 14.7 * gs - 90), "vel", 7, head=22, alpha=b)
        L.stamp(F.tag_img(r"v_0 = +9,8", 28, "vel_d"), gx + 370, g0 - 14.7 * gs - 50, alpha=b)
        c = prog(t, l4.at("altura máxima"), 0.5)
        L.line([(gx, g0 - 19.6 * gs), (gx + 300, g0 - 19.6 * gs)], "pos", 3, dash=[8, 7], alpha=c)
        L.stamp(F.tag_img(r"y_{máx} = 19,6\,\t{m}", 28, "pos_d", border=("pos", 2)), gx + 520, g0 - 19.6 * gs - 22,
                alpha=c)
        # the path of the ball: up, top, down to the ground
        d = prog(t, l7.at("Comprobación"), 3.0, "lin")
        if d > 0:
            s = 3.0 * d
            pts = []
            for k in range(int(60 * d) + 1):
                ss = 3.0 * k / 60
                pts.append((gx + 260 + (40 if ss > 1 else 0) * min(1, max(0, (ss - 1) * 3)),
                            g0 - (14.7 + 9.8 * ss - 4.9 * ss * ss) * gs))
            L.line(pts, "path", 3, dash=[8, 7])
            L.circle(pts[-1][0], pts[-1][1], 12, fill="acc", stroke="ink", width=2)
    mg(sc, diagram, at=l2.at("Eje"), z=5)
    sh = F.sheet(880, 800, seed=42)
    put(sc, sh, 1440, 560, l2.start(), rot=0.4, z=3)
    l3 = sc.say("Apartado a: en la altura máxima, la velocidad es cero. No sabemos el tiempo, así que usamos la "
                "ecuación sin tiempo.")
    l4 = sc.say("0 igual a 9,8 al cuadrado, más 2 por menos 9,8, por i griega menos 14,7. Sale i griega menos 14,7 "
                "igual a 4,9. La altura máxima: 19,6 metros.")
    l5 = sc.say("Apartado b: llega al suelo cuando i griega vale cero. 0 igual a 14,7 más 9,8 te menos 4,9 te al "
                "cuadrado. Dividimos entre 4,9: te al cuadrado menos 2 te menos 3 igual a cero.")
    l6 = sc.say("Sus soluciones son 3 y menos 1. Nos quedamos con 3 segundos: menos 1 sería antes del lanzamiento. Y "
                "la velocidad: 9,8 menos 9,8 por 3, menos 19,6 m/s, hacia abajo.")
    lines = [(r"y_0 = 14,7\quad v_0 = +9,8\quad a = −9,8", l2.at("Datos")),
             (r"\t{a) } 0 = 9,8^2 + 2 · (−9,8)(y − 14,7)", l4.at("0 igual")),
             (r"y − 14,7 = 4,9 \;\Rightarrow\; y_{máx} = \c{pos}{19,6\,\t{m}}", l4.at("Sale")),
             (r"\t{b) } 0 = 14,7 + 9,8\,t − 4,9\,t^2", l5.at("0 igual")),
             (r"t^2 − 2\,t − 3 = 0", l5.at("Dividimos")),
             (r"t = \frac{2 \pm 4}{2} = \c{pos}{3\,\t{s}}\quad\t{(no } −1\t{)}", l6.at("soluciones")),
             (r"\t{c) } v = 9,8 − 9,8 · 3 = \c{vel}{−19,6\,\t{m/s}}", l6.at("la velocidad"))]
    F.board(sc, lines, 1030, 230, size=36, gap=24, z=5)
    l7 = sc.say("Comprobación visual: la pelota sube 4,9 metros, se para en 19,6, y baja hasta el suelo en 3 "
                "segundos en total. Todo cuadra.")
    put(sc, F.fcard(r"\t{sube, se para en 19,6 m y llega al suelo en 3 s}\;\t{✓}", size=32, border=("grass_d", 3)),
        1440, 830, l7.at("Todo cuadra"), z=7)
    sc.wait(0.8)


RESUMEN = [
    (r"\t{Origen en el suelo, eje }Y\t{ hacia arriba:}\quad \c{acc}{a = −g = −9,8\,\t{m/s}^2}\t{ siempre}",
     "Origen en el suelo y eje hacia arriba: la aceleración es siempre menos 9,8 m/s²."),
    (r"\t{Son MRUA: }y = y_0 + v_0\,t + \frac{1}{2}\,a\,t^2 \quad v = v_0 + a\,t \quad v^2 = v_0^2 + 2a(y − y_0)",
     "Son movimientos rectilíneos uniformemente acelerados: las mismas ecuaciones, con i griega."),
    (r"\t{Caída: }v_0 = 0\quad\t{Hacia arriba: }v_0 > 0\quad\t{Hacia abajo: }v_0 < 0",
     "Caída desde el reposo, velocidad inicial cero; hacia arriba, positiva; hacia abajo, negativa."),
    (r"\t{Altura máxima: }v = 0\t{, pero }a = −9,8\,\t{m/s}^2",
     "En la altura máxima la velocidad es cero, pero la aceleración no."),
    (r"\t{Tiempos negativos: se descartan. Signo de }v\t{: hacia dónde va}",
     "Los tiempos negativos se descartan, y el signo de la velocidad dice hacia dónde va."),
]


def build(only=None):
    mv = K.new_movie()
    parts = [("intro", intro), ("sistema", sistema), ("caida", caida), ("arriba", arriba), ("abajo", abajo),
             ("tres", tres), ("p1", problema_caida), ("p2", problema_lanzamiento),
             ("resumen", lambda m: K.resumen(m, "REPASO DEL TEMA 4", RESUMEN, size=34)),
             ("fin", lambda m: K.fin(m, 4, "Próximo: Tema 5 · Método de examen",
                                     "Fin del tema cuatro. En el siguiente, el método para resolver cualquier "
                                     "problema de examen. ¡Hasta pronto!"))]
    for name, fn in parts:
        if only and name not in only:
            continue
        fn(mv)
    return mv


def chapters(mv):
    names = {"title": "Inicio", "sistema": "1 · Eje hacia arriba y a = −9,8 m/s²", "caida": "2 · Caída desde el reposo",
             "arriba": "3 · Lanzamiento hacia arriba", "abajo": "4 · Lanzamiento hacia abajo",
             "tres": "5 · Las tres situaciones", "prob-caida": "6 · Problema: una caída",
             "prob-lanz": "7 · Problema: un lanzamiento", "resumen": "Repaso del tema"}
    return [(st, names[sc.name]) for sc, st in zip(mv.scenes, mv.starts) if sc.name in names]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "out/Cinematica_T4_Caida_libre.mp4"
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only="):
            only = a.split("=", 1)[1].split(",")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mv = build(only).build()
    print("duración %.1f s (%.1f min), escenas %d, subtítulos %d" % (mv.total, mv.total / 60, len(mv.scenes),
                                                                     len(mv.cues)))
    chs = chapters(mv)
    mv.render(out, chapters=chs, crf=27, abr="64k", tune="animation")
    with open(os.path.splitext(out)[0] + "_capitulos.txt", "w", encoding="utf-8") as f:
        for st, ttl in chs:
            f.write("%d:%02d  %s\n" % (st // 60, st % 60, ttl))

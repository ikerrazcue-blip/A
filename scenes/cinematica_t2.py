"""Física · Cinemática · Tema 2: MRU, movimiento rectilíneo uniforme (stop-motion de papel + motion graphics).

Fotos cada segundo (distancias iguales en tiempos iguales) → x = x0 + v·t construida desde el movimiento →
gráficas x-t (pendiente = v) y v-t (horizontal, área = desplazamiento) → problema de posición → problema de
encuentro con un único sistema de referencia y un mismo origen de tiempos → repaso. Sin azul.

    python3 scenes/cinematica_t2.py out/Cinematica_T2_MRU.mp4
    python3 scenes/cinematica_t2.py out/c.mp4 --stills [--only=intro,graf]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cine_comun as K  # noqa: E402
from cine_comun import F, W, H, card, kit, formula, mg, live, prog, lerp2, put, scn  # noqa: E402

GROUND = 640.0          # street scenes: top of the bike lane
AXIS_Y = 742.0          # street scenes: the X axis under the lane
O_X = 150.0             # origin (house door)
PPM = 40.0              # px per metre in the street scenes
V_ANA = 6.0
X0_ANA = 10.0


def sx(m):
    return O_X + m * PPM


# ============================================================================
def intro(mv):
    K.portada(mv, "MRU", "Tema 2 · Movimiento rectilíneo uniforme",
              "Cinemática. Tema dos: el movimiento rectilíneo uniforme, el MRU.")


# ============================================================================
# 1. distancias iguales en tiempos iguales → x = x0 + v·t
# ============================================================================
def fotos(mv):
    sc = scn(mv, "fotos", bg="sky", lead=0.4, transition="wipe")
    K.street(sc, GROUND)
    l1 = sc.say("Ana va en bici por un carril recto. No acelera ni frena: mantiene siempre el mismo ritmo.")
    l2 = sc.say("Vamos a hacerle una foto cada segundo.")
    t0 = l2.end(0.2)                   # first photo
    sc.wait(5.4)                       # the run: six photos, one per second

    def ana_x(t):
        return sx(X0_ANA + V_ANA * (t - t0))
    K.rider_live(sc, "ana", ana_x, GROUND, at=0.2, z=5)
    for k in range(6):
        K.ghost_live(sc, "ana", ana_x(t0 + k), GROUND, at=t0 + k, z=2)
        sc.sfx(t0 + k, F.tick(0.07, seed=k % 2))
    sw_e, sw_m = K.stopwatch(sc, 230, 190, lambda t: min(max(0.0, t - t0), 5.0), at=l2.start(), d=170)

    def marks(L, t):
        for k in range(6):
            if t >= t0 + k:
                x = ana_x(t0 + k)
                L.line([(x, GROUND - 4), (x, GROUND + 40)], "ink", 3)
                L.stamp(formula(r"\t{%d s}" % k, 30), x, GROUND + 58)
    mg(sc, marks, at=t0, z=6)
    l3 = sc.say("Mira las fotos: entre cada dos fotos hay siempre la misma distancia, 6 metros.")
    t_gap = l3.at("misma distancia")

    def gaps(L, t):
        for k in range(5):
            g = prog(t, t_gap + 0.3 * k, 0.3, "out")
            if g <= 0:
                continue
            a, b = ana_x(t0 + k), ana_x(t0 + k + 1)
            y = GROUND - 280
            L.line([(a, y), (a + (b - a) * g, y)], "vel", 6)
            L.line([(a, y - 14), (a, y + 14)], "vel", 4)
            if g >= 1:
                L.line([(b, y - 14), (b, y + 14)], "vel", 4)
                L.stamp(F.tag_img(r"\t{6 m}", 34, "vel_d"), (a + b) / 2, y - 34)
    e_gaps = mg(sc, gaps, at=t_gap, z=6)
    l4 = sc.say("En tiempos iguales, recorre distancias iguales. Eso es un {pos:movimiento rectilíneo uniforme}, un "
                "MRU: la trayectoria es una recta y la velocidad es constante.")
    d = F.def_card("MRU", [r"\t{Trayectoria }\b{recta}\t{ y velocidad }\b{constante}",
                           r"\t{Distancias iguales en tiempos iguales}"], size=40, border=("pos", 4))
    e_d = put(sc, d, 760, 180, l4.at("movimiento rectilíneo"), z=8)
    l5 = sc.say("Como la velocidad no cambia, no hay aceleración. Y su valor es fácil de leer en las fotos: 6 metros "
                "en cada segundo, es decir, 6 m/s.")
    e_v = put(sc, F.fcard(r"v = \frac{6\,\t{m}}{1\,\t{s}} = 6\,\t{m/s}\qquad a = 0", size=44, border=("vel", 3)),
              1480, 170, l5.at("6 metros"), z=8)
    sc.wait(0.3)

    # --- an axis to write the position
    l6 = sc.say("Para escribir su posición en cada instante, necesitamos un eje. Ponemos el origen en la puerta de su "
                "casa.")
    for e in (e_d, e_v, sw_e):
        e.leave(l6.start(), "up", 0.5)
    sw_m.leave(l6.start(), "cut")
    e_gaps.leave(l6.start(), "cut")
    house = F.house_piece()
    put(sc, house, O_X - 10, GROUND - house.vh / 2 + 4, l6.at("casa"), rot=0, z=1)
    mg(sc, lambda L, t: K.axis_x(L, O_X, 1800, AXIS_Y, PPM, step=5, g=prog(t, l6.at("eje"), 0.8, "out"), neg=40),
       at=l6.at("eje"), z=5)
    l7 = sc.say("En la primera foto, en el instante cero, Ana estaba a 10 metros del origen: es su {pos:posición "
                "inicial}, equis cero.")
    l8 = sc.say("Un segundo después había avanzado 6 metros: 10 más 6, 16 metros.")
    l9 = sc.say("A los 2 segundos, 10 más 2 veces 6: 22 metros.")
    l10 = sc.say("A los 3 segundos, 10 más 3 veces 6: 28 metros. Y así, cada segundo.")
    steps = [l7.at("10 metros"), l8.at("6 metros"), l9.at("2 veces"), l10.at("3 veces"), l10.at("cada segundo"),
             l10.at("cada segundo", after=0.4)]

    def blocks(L, t):
        y = AXIS_Y + 72
        g0 = prog(t, steps[0], 0.6, "out")
        if g0 > 0:
            L.line([(sx(0), y), (sx(X0_ANA * g0), y)], "pos", 18, cap="butt")
            if g0 >= 1:
                L.stamp(F.tag_img(r"x_0", 32, "pos_d"), sx(5), y + 34)
        for k in range(1, 6):
            g = prog(t, steps[k], 0.45, "out")
            if g <= 0:
                continue
            a = sx(X0_ANA + V_ANA * (k - 1))
            L.line([(a + 2, y), (a + 2 + (V_ANA * PPM - 4) * g, y)], "vel_l" if k % 2 else "vel", 18, cap="butt")
            if g >= 1:
                L.stamp(F.formula(r"\t{+6}", 26, "vel_d"), a + V_ANA * PPM / 2, y + 34)
        for k in range(6):
            g = prog(t, steps[k] + 0.3, 0.3)
            if g > 0:
                x = ana_x(t0 + k)
                L.stamp(F.tag_img(r"\t{%d m}" % (X0_ANA + V_ANA * k), 32, "pos_d", border=("pos", 2), pad=(8, 2)),
                        x, GROUND - 300, alpha=g)
    mg(sc, blocks, at=steps[0], z=6)
    # the table, built row by row
    tx, ty = 100, 112
    rows = [("0", r"10"), ("1", r"10 + 6 = 16"), ("2", r"10 + 6 · 2 = 22"), ("3", r"10 + 6 · 3 = 28")]

    def table(L, t):
        g = prog(t, steps[0] - 0.2, 0.4)
        if g <= 0:
            return
        L.poly([(tx - 30, ty - 30), (tx + 420, ty - 30), (tx + 420, ty + 210), (tx - 30, ty + 210)],
               fill=(251, 245, 230, 235), stroke="ink", width=2, alpha=g)
        L.stamp(F.formula(r"t\;\t{(s)}", 32), tx + 20, ty, "lm", alpha=g)
        L.stamp(F.formula(r"x\;\t{(m)}", 32), tx + 150, ty, "lm", alpha=g)
        L.line([(tx - 10, ty + 26), (tx + 420, ty + 26)], "ink", 2, alpha=g)
        for k, (tt, xx) in enumerate(rows):
            a = prog(t, steps[k], 0.4)
            if a > 0:
                L.stamp(F.formula(r"\t{%s}" % tt, 30), tx + 40, ty + 56 + k * 40, "cm", alpha=a)
                L.stamp(F.formula(r"\t{%s}" % xx, 30, "pos_d"), tx + 150, ty + 56 + k * 40, "lm", alpha=a)
    mg(sc, table, at=steps[0] - 0.2, z=7)
    l11 = sc.say("¿Ves el patrón? La posición es la inicial, más la velocidad multiplicada por el tiempo.")
    f1 = F.fcard(r"x = 10 + 6\,t", size=58, border=("pos", 4))
    put(sc, f1, 730, 170, l11.at("patrón"), z=8)
    l12 = sc.say("Y esa es la ecuación de cualquier MRU: equis igual a equis cero, más uve por te.")
    f2 = F.def_card("ECUACIÓN DEL MRU", [r"x = \c{pos}{x_0} + \c{vel}{v}\,t"], size=72, border=("pos", 4))
    e_f2 = put(sc, f2, 1330, 160, l12.at("ecuación"), z=9)

    def labels(L, t):
        a = prog(t, l12.at("equis cero"), 0.4)
        b = prog(t, l12.at("uve por te"), 0.4)
        L.stamp(F.tag_img(r"\c{pos}{x_0}\t{: posición inicial (m)}", 28, "ink"), 1130, 290, alpha=a)
        L.stamp(F.tag_img(r"\c{vel}{v}\t{: velocidad (m/s)} \quad t\t{: tiempo (s)}", 28, "ink"), 1560, 290, alpha=b)
    mg(sc, labels, at=l12.at("equis cero"), z=9)
    sc.wait(0.6)


def leo_negativo(mv):
    sc = scn(mv, "leo", bg="sky", lead=0.4)
    K.street(sc, GROUND)
    house = F.house_piece()
    put(sc, house, O_X - 10, GROUND - house.vh / 2 + 4, 0.1, rot=0, z=1, enter="cut")
    mg(sc, lambda L, t: K.axis_x(L, O_X, 1800, AXIS_Y, PPM, step=5, neg=40), at=0.1, z=5)
    l1 = sc.say("¿Y si el móvil va hacia la izquierda, hacia donde las posiciones disminuyen?")
    l2 = sc.say("Leo sale de los 40 metros y va hacia su casa a 4 m/s. Una foto cada segundo:")
    t0 = l2.end(0.3)
    sc.wait(5.3)
    X0, V = 40.0, -4.0

    def leo_x(t):
        return sx(X0 + V * (t - t0))
    K.rider_live(sc, "leo", leo_x, GROUND, face=-1, at=0.2, z=5)
    for k in range(6):
        K.ghost_live(sc, "leo", leo_x(t0 + k), GROUND, face=-1, at=t0 + k, z=2)
        sc.sfx(t0 + k, F.tick(0.07, seed=k % 2))

    def marks(L, t):
        for k in range(6):
            if t >= t0 + k:
                x = leo_x(t0 + k)
                L.line([(x, GROUND - 4), (x, GROUND + 40)], "ink", 3)
                L.stamp(F.tag_img(r"\t{%d m}" % (X0 + V * k), 30, "pos_d", border=("pos", 2), pad=(8, 2)), x,
                        GROUND - 300)
                L.stamp(formula(r"\t{%d s}" % k, 28), x, GROUND + 58)
    mg(sc, marks, at=t0, z=6)
    l3 = sc.say("Cada segundo, su posición disminuye 4 metros: 40, 36, 32, 28... Su velocidad es negativa: menos 4 "
                "m/s.")
    v_card = F.fcard(r"\c{vel}{v} = −4\,\t{m/s}", size=52, border=("vel", 4))
    put(sc, v_card, 520, 170, l3.at("negativa"), z=8)
    l4 = sc.say("Y su ecuación es equis igual a 40, menos 4 te.")
    put(sc, F.fcard(r"x = 40 − 4\,t", size=58, border=("pos", 4)), 1000, 170, l4.at("ecuación"), z=8)
    l5 = sc.say("El signo de la velocidad dice hacia dónde va el móvil: positivo, hacia donde crece X; negativo, "
                "hacia donde disminuye.")
    put(sc, F.fcard([r"\c{vel}{v} > 0 \;\to\; \t{hacia +X}", r"\c{vel}{v} < 0 \;\to\; \t{hacia −X}"], size=40,
                    border=("vel", 3), align="l"), 1480, 190, l5.at("signo"), z=8)
    sc.wait(0.6)


def check_mru(mv):
    sc = scn(mv, "check-mru", bg="grid", lead=0.3)
    l1 = sc.say("Comprueba: estas son las fotos de dos móviles, una cada segundo. ¿Cuál de los dos hace un MRU?")
    F.quiz(sc, "Una foto cada segundo. ¿Cuál es un MRU?", lead=l1.start(), y=200)
    xs_a = [260 + 230 * k for k in range(6)]
    xs_b = [260 + 120 * k + 30 * k * k for k in range(6)]
    for row, (xs, lab, y) in enumerate(((xs_a, "A", 480), (xs_b, "B", 700))):
        put(sc, card(lab, size=56, font_name="body9", bg="mustard", pad=(22, 6), seed=401 + row), 150, y,
            l1.at("dos móviles"), enter="pop")
        for k, x in enumerate(xs):
            put(sc, F.dot_piece(17, "pos" if row == 0 else "acc"), x, y, l1.at("una cada", after=0.15 * k + 0.2 *
                                                                                     row), enter="pop", rot=0)

        def gaps(L, t, xs=xs, y=y):
            g = prog(t, l1.at("dos móviles"), 0.4)
            L.line([(xs[0] - 40, y + 40), (1880, y + 40)], "ink", 2, alpha=g)
            for k, x in enumerate(xs):
                L.line([(x, y + 32), (x, y + 48)], "ink", 2, alpha=g)
                L.stamp(F.formula(r"\t{%d s}" % k, 24), x, y + 66, alpha=g)
        mg(sc, gaps, at=l1.at("dos móviles"), z=3)
    t_r = F.think(sc, 4.0)
    l2 = sc.say("El A: sus fotos están igual de separadas. En el B, la distancia entre fotos crece cada segundo: va "
                "cada vez más deprisa, así que no es uniforme.")
    put(sc, F.check_mark(110), 1770, 470, t_r, enter="pop", z=6)
    put(sc, F.check_mark(100, ok=False), 1770, 690, t_r + 0.4, enter="pop", z=6)

    def spans(L, t):
        g = prog(t, l2.at("crece"), 0.6, "out")
        for k in range(5):
            a, b = xs_b[k], xs_b[k + 1]
            L.line([(a + 18, 760), (a + 18 + (b - a - 36) * g, 760)], "acc", 5)
    mg(sc, spans, at=l2.at("crece"), z=4)
    sc.wait(0.5)


# ============================================================================
# 2. gráficas x-t y v-t
# ============================================================================
G_XT = dict(x0=300, y0=880, w=760, h=620, tmax=6, vmin=0, vmax=50, vstep=10, tstep=1)


def graf_xt(mv):
    sc = scn(mv, "graf", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "LA GRÁFICA POSICIÓN-TIEMPO", at=0.3)
    G = F.Graph(**G_XT)
    f = lambda t: X0_ANA + V_ANA * t  # noqa: E731
    l1 = sc.say("Ahora vamos a dibujar el movimiento de Ana en una gráfica: el tiempo en el eje horizontal y la "
                "posición en el vertical.")
    t_ax = l1.at("gráfica")
    mg(sc, lambda L, t: G.axes(L, prog(t, t_ax, 0.8, "out")), at=t_ax, z=2)
    l2 = sc.say("Cada segundo marcamos un punto: 10 metros en el instante cero, 16 al segundo, 22 a los dos "
                "segundos...")
    t_run = l2.at("Cada segundo")
    k_slow = 1.25                      # 1 s of the motion every 1.25 s of video

    def sim(t):
        return min(max(0.0, (t - t_run) / k_slow), 5.0)

    def plot(L, t):
        s = sim(t)
        # the bike's position, moving along the vertical axis (the position axis)
        bx, by = G.x0 - 46, G.Y(f(s))
        L.line([(bx + 14, by), G.P(s, f(s))], "pos", 2.5, dash=[8, 7], alpha=0.8)
        L.circle(bx, by, 15, fill="pos", stroke="ink", width=3)
        for k in range(6):
            if s >= k - 1e-6:
                G.dot(L, k, f(k), "pos_d", 9)
        if t >= l3.at("recta"):
            G.curve(L, f, 0, 5 + 0.9 * prog(t, l3.at("recta"), 0.8), "pos", 6)
    l3 = sc.say("Los puntos quedan alineados: la gráfica posición-tiempo de un MRU es una {pos:recta}.")
    sc.cursor = max(sc.cursor, t_run + 5 * k_slow + 0.3)
    mg(sc, plot, at=t_run, z=4)
    l4 = sc.say("Donde corta al eje vertical está la posición inicial, 10 metros. Es la {pos:ordenada en el origen}.")
    t_o = l4.at("eje vertical")

    def origin_mark(L, t):
        g = prog(t, t_o, 0.4, "out")
        L.circle(*G.P(0, 10), 18 * g + 0.1, stroke="pos", width=5)
        L.stamp(F.tag_img(r"\c{pos}{x_0} = 10\,\t{m}", 34, "ink", border=("pos", 3)), G.x0 + 130, G.Y(10) + 52,
                alpha=g)
    mg(sc, origin_mark, at=t_o, z=5)
    l5 = sc.say("¿Y la inclinación? Por cada 2 segundos que avanzamos, la posición sube 12 metros. 12 entre 2: 6 "
                "metros por segundo. ¡La velocidad!")
    t_s = l5.at("Por cada")
    mg(sc, lambda L, t: G.slope(L, f, 2, 4, "vel", prog(t, t_s, 1.2, "lin"), r"Δt = 2\,\t{s}", r"Δx = 12\,\t{m}"),
       at=t_s, z=5)
    l6 = sc.say("La {vel:pendiente} de la gráfica posición-tiempo es la velocidad.")
    put(sc, F.def_card("PENDIENTE", [r"\frac{Δx}{Δt} = \frac{12\,\t{m}}{2\,\t{s}}",
                                     r"= 6\,\t{m/s} = \c{vel}{v}"], head_bg="vel", size=48, border=("vel", 4)),
        1620, 330, l6.at("pendiente"), z=7)
    l7 = sc.say("Cuanto más rápido va el móvil, más inclinada es la recta. Si la recta baja, como la de Leo, la "
                "velocidad es negativa. Y si es horizontal, el móvil está parado.")
    others = [(lambda t: 2 * t, "grass_d", r"\t{2 m/s}", l7.at("más inclinada")),
              (lambda t: 40 - 4 * t, "acc", r"\t{Leo: −4 m/s}", l7.at("Leo")),
              (lambda t: 30 + 0 * t, "brown", r"\t{parado}", l7.at("horizontal"))]

    def more(L, t):
        for fn, col, lab, t1 in others:
            g = prog(t, t1, 1.0, "out")
            if g <= 0:
                continue
            G.curve(L, fn, 0, 6 * g, col, 5)
            if g >= 1:
                L.stamp(F.tag_img(lab, 28, col), G.X(6) + 40, G.Y(fn(6)), "lm")
    mg(sc, more, at=others[0][3], z=4)
    put(sc, F.fcard([r"\t{Más inclinada: más rápido}", r"\t{Baja: }v < 0", r"\t{Horizontal: }v = 0"], size=36,
                    border=("vel", 3), align="l"), 1640, 690, l7.at("parado"), z=7)
    sc.wait(0.5)

    # visual check: who is the fastest?
    sc = scn(mv, "check-graf", bg="grid", lead=0.3)
    G2 = F.Graph(x0=360, y0=860, w=820, h=560, tmax=6, vmin=0, vmax=50, vstep=10, tstep=1)
    lines = [("A", lambda t: 8 + 3 * t, "pos"), ("B", lambda t: 2 + 8 * t, "grass_d"), ("C", lambda t: 45 - 5 * t,
                                                                                         "acc")]
    l1 = sc.say("Comprueba: en esta gráfica hay tres móviles. ¿Cuál va más rápido?")
    F.quiz(sc, "¿Qué móvil va más rápido?", lead=l1.start(), x=1460, y=200, size=44, max_w=700)

    def draw(L, t):
        G2.axes(L, prog(t, l1.start(0.2), 0.6, "out"))
        for k, (lab, fn, col) in enumerate(lines):
            g = prog(t, l1.at("tres móviles") + 0.3 * k, 0.8, "out")
            if g > 0:
                G2.curve(L, fn, 0, 6 * g, col, 6)
                if g >= 1:
                    L.stamp(F.tag_img(r"\b{%s}" % lab, 40, col), G2.X(6) + 40, G2.Y(fn(6)))
    mg(sc, draw, at=l1.start(0.2), z=4)
    t_r = F.think(sc, 4.0, x=1460, y=420)
    l2 = sc.say("El B: su recta es la más inclinada, 8 metros cada segundo. El C baja, así que va hacia atrás, pero "
                "solo a 5 m/s. Y el A es el más lento.")

    def answer(L, t):
        g = prog(t, l2.at("más inclinada"), 1.0, "lin")
        G2.slope(L, lines[1][1], 2, 4, "grass_d", g, r"\t{2 s}", r"\t{16 m}")
    mg(sc, answer, at=l2.at("más inclinada"), z=5)
    put(sc, F.check_mark(100), 1300, 300, t_r, enter="pop", z=6)
    put(sc, F.fcard([r"\t{A: }3\,\t{m/s}", r"\t{B: }8\,\t{m/s}\;\t{(la más rápida)}", r"\t{C: }−5\,\t{m/s}"], size=40,
                    border=("grass_d", 3), align="l"), 1500, 720, l2.at("El B"), z=7)
    sc.wait(0.5)


def graf_vt(mv):
    sc = scn(mv, "graf-vt", bg="grid", lead=0.4)
    F.title(sc, "LA GRÁFICA VELOCIDAD-TIEMPO", at=0.3)
    G = F.Graph(x0=300, y0=880, w=860, h=620, tmax=6, vmin=-6, vmax=8, vstep=2, tstep=1, vlabel=r"v\;\t{(m/s)}")
    l1 = sc.say("Ahora, la gráfica velocidad-tiempo. La velocidad de Ana es siempre 6 m/s, así que es una recta "
                "{vel:horizontal}.")
    t_ax = l1.start(0.2)
    mg(sc, lambda L, t: G.axes(L, prog(t, t_ax, 0.8, "out")), at=t_ax, z=2)
    fa = lambda t: 6.0  # noqa: E731
    mg(sc, lambda L, t: G.curve(L, fa, 0, 5 * prog(t, l1.at("siempre"), 1.4, "io"), "vel", 7), at=l1.at("siempre"),
       z=5)
    l2 = sc.say("Su pendiente es cero, porque la velocidad no cambia: no hay aceleración.")
    put(sc, F.fcard(r"\t{pendiente} = 0 \;\Rightarrow\; a = 0", size=48, border=("vel", 3)), 1580, 260,
        l2.at("pendiente"), z=7)
    l3 = sc.say("Y un detalle muy útil: el área bajo la recta es el desplazamiento. 6 m/s durante 5 segundos: un "
                "rectángulo de 30 metros.")
    t_a = l3.at("área")
    mg(sc, lambda L, t: G.area(L, fa, 0, 5 * prog(t, t_a, 1.0, "io"), (178, 38, 116, 70)), at=t_a, z=3)
    put(sc, F.fcard(r"\t{área} = 6\,\t{m/s} · 5\,\t{s} = 30\,\t{m}", size=46, border=("vel", 3)), 1580, 430,
        l3.at("rectángulo"), z=7)
    l4 = sc.say("Comprobación visual: en la gráfica de posición, Ana pasó de 10 a 40 metros. 40 menos 10: 30 metros. "
                "¡Coincide!")
    put(sc, F.fcard(r"Δx = 40 − 10 = 30\,\t{m}", size=46, border=("pos", 3)), 1580, 790, l4.at("40 menos"), z=7)
    put(sc, F.check_mark(90), 1850, 790, l4.at("Coincide"), enter="pop", z=8)
    l5 = sc.say("La de Leo queda por debajo del eje, porque su velocidad es negativa.")
    fl = lambda t: -4.0  # noqa: E731
    mg(sc, lambda L, t: G.curve(L, fl, 0, 5 * prog(t, l5.at("Leo"), 1.0, "io"), "acc", 6), at=l5.at("Leo"), z=5)
    mg(sc, lambda L, t: L.stamp(F.tag_img(r"\t{Leo: }v = −4\,\t{m/s}", 30, "acc"), G.X(3), G.Y(-4) + 34,
                                alpha=prog(t, l5.at("debajo"), 0.4)), at=l5.at("debajo"), z=6)
    sc.wait(0.5)


# ============================================================================
# 3. problemas
# ============================================================================
def problema_posicion(mv):
    sc = scn(mv, "prob-pos", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "PROBLEMA 1 · ¿DÓNDE Y CUÁNDO?", at=0.3)
    st = F.tabbed(F.say_card("Leo va en bici en línea recta a {vel:5 m/s}. En t = 0 pasa por x = 40 m.\n"
                             "a) ¿Dónde estará en t = 15 s?  b) ¿Cuándo pasará por x = 190 m?", size=36,
                             max_w=880, border=("mustard", 3)), "ENUNCIADO", head_bg="mustard", head_color="ink")
    l1 = sc.say("Vamos con un problema. Leo va en bici en línea recta a 5 m/s. En el instante cero pasa por la "
                "posición 40 metros. ¿Dónde estará a los 15 segundos? ¿Y cuándo pasará por la posición 190 metros?")
    put(sc, st, 530, 300, l1.start(), z=6)
    l2 = sc.say("Primero, el eje: origen en O y sentido positivo, el del movimiento de Leo.")
    t_ax = l2.at("eje")
    ox, oy, ppm = 120.0, 560.0, 3.6

    def axis(L, t):
        g = prog(t, t_ax, 0.8, "out")
        L.arrow((ox - 20, oy), (ox - 20 + 860 * g, oy), "ink", 5, head=22)
        if g < 1:
            return
        L.stamp(formula("O", 32), ox, oy + 30)
        L.line([(ox, oy - 10), (ox, oy + 10)], "ink", 3)
        for m, lab in ((40, "40"), (115, "115"), (190, "190")):
            a = prog(t, {40: t_ax + 0.4, 115: l5.at("115"), 190: l6.at("190")}[m], 0.4)
            L.line([(ox + m * ppm, oy - 10), (ox + m * ppm, oy + 10)], "ink", 3, alpha=a)
            L.stamp(formula(r"\t{%s}" % lab, 28), ox + m * ppm, oy + 30, alpha=a)
        L.stamp(formula(r"x\;\t{(m)}", 30), ox + 850, oy + 30)
        a = prog(t, l2.at("sentido"), 0.4)
        L.arrow((ox + 40 * ppm, oy - 54), (ox + 40 * ppm + 130 * a, oy - 54), "vel", 8, head=26)
        L.stamp(F.tag_img(r"+5\,\t{m/s}", 30, "vel_d"), ox + 40 * ppm + 70, oy - 96, alpha=a)
    sh = F.sheet(800, 690, seed=21)
    put(sc, sh, 1470, 560, l2.start(), rot=0.6, z=3)
    l3 = sc.say("Datos: equis cero, 40 metros; velocidad, más 5 m/s. Y la ecuación del MRU queda: equis igual a 40 "
                "más 5 te.")
    l4 = sc.say("Apartado a: sustituimos te por 15 segundos.")
    l5 = sc.say("40 más 5 por 15: 40 más 75, 115 metros.")
    l6 = sc.say("Apartado b: ahora conocemos la posición, 190 metros, y buscamos el tiempo. Restamos 40 a los dos "
                "lados: 150 igual a 5 te. Y despejamos: te igual a 150 entre 5, 30 segundos.")
    mg(sc, axis, at=t_ax, z=5)
    X = 1110
    K_ = [(r"x_0 = 40\,\t{m}\qquad v = +5\,\t{m/s}", l3.at("Datos")),
          (r"x = 40 + 5\,t", l3.at("la ecuación")),
          (r"\t{a) } x = 40 + 5 · 15", l4.at("sustituimos")),
          (r"x = 40 + 75 = \c{pos}{115\,\t{m}}", l5.at("40 más 75")),
          (r"\t{b) } 190 = 40 + 5\,t", l6.at("190 metros")),
          (r"150 = 5\,t", l6.at("150 igual")),
          (r"t = \frac{150}{5} = \c{pos}{30\,\t{s}}", l6.at("despejamos"))]
    F.board(sc, K_, X, 270, size=40, gap=22)
    l7 = sc.say("Comprobamos: 40 más 5 por 30 da 190. ¡Correcto! Y en la gráfica, la recta pasa justo por los dos "
                "puntos.")
    put(sc, F.fcard(r"40 + 5 · 30 = 190\;\t{✓}", size=40, border=("grass_d", 3)), 1470, 980 - 120, l7.at("Comprobamos"),
        z=7)
    G = F.Graph(x0=170, y0=900, w=640, h=240, tmax=35, vmin=0, vmax=200, vstep=50, tstep=5, tlab_every=1,
                size=24)
    fx = lambda t: 40 + 5 * t  # noqa: E731

    def graph(L, t):
        g = prog(t, l7.at("en la gráfica"), 0.6, "out")
        if g <= 0:
            return
        G.axes(L, g, grid=False)
        if g >= 1:
            G.curve(L, fx, 0, 32, "pos", 5)
            G.dot(L, 15, 115, "pos_d")
            G.dot(L, 30, 190, "pos_d")
            G.guides(L, 15, 115, "pos_d", size=22)
            G.guides(L, 30, 190, "pos_d", size=22)
    mg(sc, graph, at=l7.at("en la gráfica"), z=5)
    sc.wait(0.6)


def problema_encuentro(mv):
    sc = scn(mv, "encuentro", bg="sky", lead=0.4, transition="wipe")
    GR = 760.0
    AX = 838.0
    O = 200.0
    P = 5.0                           # px per metre: 300 m -> 1500 px

    def X(m):
        return O + m * P
    K.street(sc, GR)
    st = F.tabbed(F.say_card("Ana y Leo están a {pos:300 m} en un carril recto. Salen a la vez, uno hacia el otro:\n"
                             "Ana a {vel:6 m/s} y Leo a {vel:4 m/s}. ¿Cuándo y dónde se encuentran?", size=36,
                             max_w=1300, border=("mustard", 3)), "PROBLEMA 2 · ENCUENTRO", head_bg="mustard",
                  head_color="ink")
    l1 = sc.say("Ahora, un problema de encuentro. Ana y Leo están a 300 metros el uno del otro, en un carril recto. "
                "Salen a la vez, uno hacia el otro: Ana a 6 m/s y Leo a 4 m/s. ¿Cuándo y dónde se encuentran?")
    e_st = put(sc, st, W / 2, 150, l1.start(), z=8)
    l2 = sc.say("La clave: un único sistema de referencia y un mismo origen de tiempos para los dos.")
    t_ax = l2.at("sistema de referencia")
    mg(sc, lambda L, t: K.axis_x(L, O, 1760, AX, P, step=50, g=prog(t, t_ax, 0.8, "out"), neg=30), at=t_ax, z=5)
    e_st.leave(l2.start(), "up", 0.5)
    put(sc, F.say_card("Un solo eje (origen donde sale Ana)\ny un solo reloj (t = 0 al salir)", size=34,
                       border=("pos", 3)), 350, 170, l2.at("único"), z=8)
    state = {"t0": 1e9}
    T_FF = 10.0                       # the 30 s of the problem, shown in 10 s

    def sim(t):
        return min(max(0.0, (t - state["t0"]) * 30.0 / T_FF), 30.0)
    K.rider_live(sc, "ana", lambda t: X(6 * sim(t)), GR, face=1, at=0.0, z=5)
    K.rider_live(sc, "leo", lambda t: X(300 - 4 * sim(t)), GR, face=-1, at=0.0, z=5)
    K.stopwatch(sc, 770, 180, lambda t: sim(t), at=l2.at("origen de tiempos"), d=160)
    l3 = sc.say("Ana sale del origen hacia la derecha, en sentido positivo: equis A igual a 6 te.")
    l4 = sc.say("Leo sale de los 300 metros hacia la izquierda, así que su velocidad es negativa: equis B igual a 300 "
                "menos 4 te.")

    def eqs(L, t):
        a = prog(t, l3.at("Ana sale"), 0.4)
        if a > 0:
            L.arrow((X(0) + 40, GR - 270), (X(0) + 40 + 150 * a, GR - 270), "vel", 8, head=26)
            L.stamp(F.tag_img(r"x_A = 6\,t", 40, "pos_d", border=("pos", 3)), X(0) + 120, GR - 330)
        b = prog(t, l4.at("Leo sale"), 0.4)
        if b > 0:
            L.arrow((X(300) - 40, GR - 270), (X(300) - 40 - 100 * b, GR - 270), "vel", 8, head=26)
            L.stamp(F.tag_img(r"x_B = 300 − 4\,t", 40, "pos_d", border=("pos", 3)), X(300) - 150, GR - 330)
    e_eqs = mg(sc, eqs, at=l3.start(), z=7)
    l5 = sc.say("Se encuentran cuando están en el mismo sitio en el mismo instante. Así que igualamos las "
                "posiciones.")
    l6 = sc.say("6 te igual a 300 menos 4 te. Pasamos los términos con te a un lado: 10 te igual a 300. Y te igual "
                "a 30 segundos.")
    l7 = sc.say("¿Dónde? Sustituimos en la ecuación de Ana: 6 por 30, 180 metros.")
    l8 = sc.say("Comprobamos con la de Leo: 300 menos 4 por 30, también 180 metros. ¡Coinciden!")
    e_eqs.leave(l5.start(), "cut")
    l9 = sc.say("Y ahora, la comprobación visual. Ponemos el reloj en marcha y los dejamos pedalear.")
    state["t0"] = l9.end(0.3)
    lines = [(r"x_A = x_B", l5.at("igualamos")), (r"6\,t = 300 − 4\,t", l6.at("6 te igual")),
             (r"10\,t = 300 \;\Rightarrow\; t = \c{pos}{30\,\t{s}}", l6.at("10 te")),
             (r"x_A = 6 · 30 = \c{pos}{180\,\t{m}}", l7.at("Sustituimos")),
             (r"x_B = 300 − 4 · 30 = 180\,\t{m}\;\t{✓}", l8.at("Comprobamos"))]
    sh = F.sheet(820, 400, seed=22, lines=False)
    e_sh = put(sc, sh, 1430, 270, l5.start(), rot=0.5, z=6)
    e_sh.leave(state["t0"] - 0.2, "up", 0.5)
    F.board(sc, lines, 1060, 105, size=38, gap=16, z=7, until=state["t0"] - 0.2)
    sc.cursor = max(sc.cursor, state["t0"] + T_FF + 0.3)
    l10 = sc.say("A los 30 segundos se cruzan justo en los 180 metros.")

    def meet(L, t):
        g = prog(t, state["t0"] + T_FF, 0.5, "out")
        if g <= 0:
            return
        L.line([(X(180), GR - 300), (X(180), AX)], "acc", 4, dash=[10, 8])
        L.stamp(F.tag_img(r"t = 30\,\t{s},\; x = 180\,\t{m}", 40, "acc_d", border=("acc", 3)), X(180), GR - 330,
                alpha=g)
    mg(sc, meet, at=state["t0"] + T_FF, z=8)
    sc.wait(0.5)


def encuentro_grafica(mv):
    """the graph of the meeting: two lines crossing"""
    sc = scn(mv, "encuentro-graf", bg="grid", lead=0.3)
    G = F.Graph(x0=280, y0=880, w=900, h=640, tmax=40, vmin=0, vmax=300, vstep=50, tstep=5)
    l1 = sc.say("En la gráfica posición-tiempo, cada uno es una recta. La de Ana sube y la de Leo baja.")
    mg(sc, lambda L, t: G.axes(L, prog(t, l1.start(0.2), 0.7, "out")), at=l1.start(0.2), z=2)
    fa = lambda t: 6 * t  # noqa: E731
    fb = lambda t: 300 - 4 * t  # noqa: E731

    def lines_(L, t):
        a = prog(t, l1.at("Ana sube"), 1.0, "io")
        b = prog(t, l1.at("Leo baja"), 1.0, "io")
        if a > 0:
            G.curve(L, fa, 0, 40 * a, "pos", 6)
            if a >= 1:
                L.stamp(F.tag_img(r"x_A = 6\,t", 34, "pos_d"), G.X(16), G.Y(fa(16)) - 46)
        if b > 0:
            G.curve(L, fb, 0, 40 * b, "vel", 6)
            if b >= 1:
                L.stamp(F.tag_img(r"x_B = 300 − 4\,t", 34, "vel_d"), G.X(12), G.Y(fb(12)) + 52)
    mg(sc, lines_, at=l1.at("Ana sube"), z=4)
    l2 = sc.say("El encuentro es el punto donde se cortan: 30 segundos y 180 metros. La misma respuesta, ahora con un "
                "dibujo.")

    def cross(L, t):
        g = prog(t, l2.at("se cortan"), 0.5, "out")
        if g <= 0:
            return
        L.circle(*G.P(30, 180), 22 * g, stroke="acc", width=5)
        G.guides(L, 30, 180, "acc_d", tlab=r"\t{30 s}", vlab=r"\t{180 m}", alpha=g)
    mg(sc, cross, at=l2.at("se cortan"), z=5)
    l3 = sc.say("Ojo: el reloj tiene que ser el mismo para los dos. Si Leo hubiera salido 10 segundos más tarde, su "
                "ecuación sería equis B igual a 300 menos 4 por te menos 10.")
    put(sc, kit.ojo("Mismo reloj para los dos. Si Leo sale 10 s después:", size=34, max_w=600), 1590, 330,
        l3.at("Ojo"), z=7, rot=-1)
    put(sc, F.fcard(r"x_B = 300 − 4\,(t − 10)", size=46, border=("acc", 3)), 1590, 520, l3.at("ecuación"), z=7)
    l4 = sc.say("Y si fueran en el mismo sentido, sería un problema de alcance. Se resuelve igual: mismo eje, mismo "
                "reloj, e igualamos posiciones.")
    put(sc, F.fcard([r"\t{Encuentro o alcance:}", r"x_A = x_B"], size=46, border=("pos", 3)), 1590, 720,
        l4.at("alcance"), z=7)
    sc.wait(0.6)


# ============================================================================
RESUMEN = [
    (r"\b{MRU:}\t{ trayectoria recta y velocidad constante (}a = 0\t{). Distancias iguales en tiempos iguales.}",
     "MRU: trayectoria recta y velocidad constante, sin aceleración. Recorre distancias iguales en tiempos iguales."),
    (r"x = \c{pos}{x_0} + \c{vel}{v}\,t \qquad \t{o, con otro origen de tiempos:}\quad x = x_0 + v\,(t − t_0)",
     "Su ecuación: equis igual a equis cero, más uve por te."),
    (r"\t{Signo de }v\t{: positivo hacia }+X\t{, negativo hacia }−X",
     "El signo de la velocidad indica el sentido del movimiento."),
    (r"\b{x-t:}\t{ recta; ordenada en el origen = }x_0\t{; pendiente = }v",
     "En la gráfica posición-tiempo, una recta: la ordenada en el origen es la posición inicial, y la pendiente, la "
     "velocidad."),
    (r"\b{v-t:}\t{ recta horizontal (pendiente 0); el área bajo la recta es }Δx",
     "En la gráfica velocidad-tiempo, una recta horizontal, y el área bajo ella es el desplazamiento."),
    (r"\b{Encuentro / alcance:}\t{ un eje, un reloj, e igualar }x_A = x_B",
     "Para un encuentro o un alcance: un solo eje, un solo reloj, e igualar las posiciones."),
]


def build(only=None):
    mv = K.new_movie()
    parts = [("intro", intro), ("fotos", fotos), ("leo", leo_negativo), ("check", check_mru), ("graf", graf_xt),
             ("vt", graf_vt), ("pos", problema_posicion), ("enc", problema_encuentro), ("enc", encuentro_grafica),
             ("resumen", lambda m: K.resumen(m, "REPASO DEL TEMA 2", RESUMEN, size=36)),
             ("fin", lambda m: K.fin(m, 2, "Próximo: Tema 3 · MRUA",
                                     "Fin del tema dos. En el siguiente, el movimiento rectilíneo uniformemente "
                                     "acelerado. ¡Hasta pronto!"))]
    for name, fn in parts:
        if only and name not in only:
            continue
        fn(mv)
    return mv


def chapters(mv):
    names = {"title": "Inicio", "fotos": "1 · Distancias iguales en tiempos iguales", "graf": "2 · La gráfica x-t",
             "graf-vt": "3 · La gráfica v-t", "prob-pos": "4 · Problema de posición",
             "encuentro": "5 · Problema de encuentro", "resumen": "Repaso del tema"}
    return [(st, names[sc.name]) for sc, st in zip(mv.scenes, mv.starts) if sc.name in names]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "out/Cinematica_T2_MRU.mp4"
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only="):
            only = a.split("=", 1)[1].split(",")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mv = build(only).build()
    print("duración %.1f s (%.1f min), escenas %d, subtítulos %d" % (mv.total, mv.total / 60, len(mv.scenes),
                                                                     len(mv.cues)))
    if "--stills" in sys.argv:
        d = os.path.join(os.path.dirname(out) or ".", "stills")
        os.makedirs(d, exist_ok=True)
        for i, (sc, st) in enumerate(zip(mv.scenes, mv.starts)):
            mv.still(st + max(0.5, sc.cursor - 0.3), os.path.join(d, f"{i:02d}_{sc.name}.png"))
    else:
        chs = chapters(mv)
        mv.render(out, chapters=chs, crf=27, abr="64k", tune="animation")
        with open(os.path.splitext(out)[0] + "_capitulos.txt", "w", encoding="utf-8") as f:
            for st, ttl in chs:
                f.write("%d:%02d  %s\n" % (st // 60, st % 60, ttl))

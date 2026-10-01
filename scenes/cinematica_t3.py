"""Física · Cinemática · Tema 3: MRUA, movimiento rectilíneo uniformemente acelerado.

Velocidad que cambia lo mismo en tiempos iguales → v = v0 + a·t (columnas de velocidad) →
x = x0 + v0·t + ½·a·t² (área bajo la gráfica v-t) → v² = v0² + 2a(x − x0) (sin tiempo) → cuándo usar
cada una → gráficas x-t, v-t y a-t de un móvil que acelera y de otro que frena → signos → problema completo
con conversión de unidades → repaso. Sin azul.

    python3 scenes/cinematica_t3.py out/Cinematica_T3_MRUA.mp4
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cine_comun as K  # noqa: E402
from cine_comun import F, W, H, card, kit, formula, mg, live, prog, lerp2, put, scn  # noqa: E402

CAR_S = 34.0          # px per metre on the roads (top view)
VEL_S = 26.0          # px per m/s for velocity arrows


def intro(mv):
    K.portada(mv, "MRUA", "Tema 3 · Movimiento rectilíneo uniformemente acelerado",
              "Cinemática. Tema tres: el movimiento rectilíneo uniformemente acelerado, el MRUA.")


def road(sc, y, at=0.0, stop_x=None, seed=255, zebra_x=None):
    rd = F.road_piece(2100, 200, seed=seed, stop_x=stop_x, zebra_x=zebra_x)
    return sc.add(rd, W / 2, y, at=at, enter="cut", rot=0, z=0, jitter=0.3)


# ============================================================================
# 1. la velocidad cambia lo mismo cada segundo
# ============================================================================
def fotos(mv):
    sc = scn(mv, "fotos", bg="grass", lead=0.4, transition="wipe")
    RY = 660.0
    road(sc, RY, stop_x=455)
    Y = RY + 50
    X0 = 280.0
    S = 50.0                           # px per metre in this scene
    a = 2.0
    car = F.car_top("mustard", L=150)
    tl_r, tl_g = F.traffic_light("red"), F.traffic_light("green")
    l1 = sc.say("Este coche espera en un semáforo. Cuando se pone verde, arranca y va cada vez más deprisa.")
    e_tl = put(sc, tl_r, 430, RY - 190, 0.3, rot=0, z=3)
    t0 = l1.at("arranca", after=-0.1)
    e_tl.swap(l1.at("verde"), tl_g)
    l2 = sc.say("Le hacemos una foto cada segundo.")
    sc.cursor = max(sc.cursor, t0 + 5.4)

    def xk_of(k):
        return X0 + 0.5 * a * k * k * S

    def x_of(t):
        tt = min(max(0.0, t - t0), 5.6)
        return X0 + 0.5 * a * tt * tt * S
    live(sc, lambda t: (car, x_of(t), Y, 0.0), at=0.0, z=4, jitter=0.4)
    gh = F.ghost(car, 0.35)
    for k in range(6):
        live(sc, lambda t, xk=xk_of(k): (gh, xk, Y, 0.0), at=t0 + k, z=2, jitter=0.0, shadow=False)
        sc.sfx(t0 + k, F.tick(0.07, seed=k % 2))
    l3 = sc.say("Ahora las fotos no están igual de separadas: en cada segundo recorre más que en el anterior.")
    e_tl.leave(l3.start(), "up", 0.5)
    l4 = sc.say("Pero mira su velocidad: 0, 2, 4, 6, 8, 10 m/s. Cada segundo aumenta exactamente lo mismo: 2 m/s.")
    t_v = l4.at("mira su velocidad")
    t_dv = l4.at("exactamente")
    y = RY - 190

    def arrows(L, t):
        for k in range(6):
            g = prog(t, t_v + 0.35 * k, 0.3, "out")
            if g <= 0:
                continue
            xk = xk_of(k)
            v = a * k
            if v > 0:
                L.arrow((xk, y), (xk + v * VEL_S * g, y), "vel", 9, head=28)
                L.stamp(F.formula(r"\t{%d m/s}" % v, 28, "vel_d"), xk + v * VEL_S / 2, y - 34, alpha=g)
            else:
                L.circle(xk, y, 8, fill="vel")
                L.stamp(F.formula(r"\t{0 m/s}", 28, "vel_d"), xk - 18, y - 34, "rm", alpha=g)
            L.stamp(F.formula(r"\t{%d s}" % k, 26, "ink"), xk, y + 36, alpha=g)
            if k > 0:
                h = prog(t, t_dv + 0.25 * (k - 1), 0.3, "out")
                if h > 0:
                    xm = (xk + xk_of(k - 1)) / 2
                    L.stamp(F.tag_img(r"\t{+2 m/s}", 26, "acc_d", border=("acc", 2), pad=(6, 2)), xm, y - 96,
                            alpha=h)
        # distances between photos (1, 3, 5, 7, 9 m)
        g = prog(t, l3.at("igual de separadas"), 0.5)
        for k in range(5):
            xa, xb = xk_of(k), xk_of(k + 1)
            L.line([(xa, RY + 126), (xb, RY + 126)], "ink", 3, alpha=g)
            L.line([(xa, RY + 114), (xa, RY + 138)], "ink", 3, alpha=g)
            L.line([(xb, RY + 114), (xb, RY + 138)], "ink", 3, alpha=g)
            L.stamp(F.formula(r"\t{%d m}" % (2 * k + 1), 26), (xa + xb) / 2, RY + 158, alpha=g)
    mg(sc, arrows, at=l3.start(), z=6)
    l5 = sc.say("La velocidad cambia lo mismo en tiempos iguales: la aceleración es constante. Eso es un "
                "{acc:movimiento rectilíneo uniformemente acelerado}, un MRUA.")
    d = F.def_card("MRUA", [r"\t{Trayectoria }\b{recta}\t{ y aceleración }\b{constante}",
                            r"\t{Velocidad: cambios iguales en tiempos iguales}"], head_bg="acc", size=38,
                   border=("acc", 4))
    put(sc, d, 640, 175, l5.at("movimiento rectilíneo"), z=8)
    l6 = sc.say("Aquí, la aceleración vale 2 metros por segundo, cada segundo: 2 m/s².")
    put(sc, F.fcard(r"\c{acc}{a} = \frac{2\,\t{m/s}}{1\,\t{s}} = 2\,\t{m/s}^2", size=46, border=("acc", 3)), 1400,
        170, l6.at("2 metros"), z=8)
    sc.wait(0.6)


# ============================================================================
# 2. v = v0 + a t   (columnas de velocidad → recta v-t)
# ============================================================================
def ecuacion_v(mv):
    sc = scn(mv, "ec-v", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "PRIMERA ECUACIÓN: LA VELOCIDAD", at=0.3)
    G = F.Graph(x0=260, y0=840, w=840, h=580, tmax=4.6, vmin=0, vmax=14, tstep=1, vstep=2,
                vlabel=r"v\;\t{(m/s)}")
    v0, a = 4.0, 2.0
    l1 = sc.say("Vamos a construir las ecuaciones. Otro coche ya iba a 4 m/s cuando empezamos a contar el tiempo, y "
                "acelera 2 m/s cada segundo.")
    mg(sc, lambda L, t: G.axes(L, prog(t, l1.at("Vamos"), 0.7, "out")), at=l1.at("Vamos"), z=2)
    l2 = sc.say("En el instante cero, su velocidad es la inicial, uve cero: 4 m/s.")
    l3 = sc.say("Al cabo de un segundo: 4 más 2, 6 m/s. A los dos segundos: 4 más dos veces 2, 8. Y a los tres: 4 "
                "más tres veces 2, 10 m/s.")
    times = [l2.at("uve cero"), l3.at("un segundo"), l3.at("dos segundos"), l3.at("los tres")]
    BW = 56

    def cols(L, t):
        for k, tk in enumerate(times):
            g0 = prog(t, tk, 0.4, "out")
            if g0 <= 0:
                continue
            x = G.X(k) + (BW / 2 + 4 if k == 0 else 0)
            L.poly([(x - BW / 2, G.Y(0)), (x + BW / 2, G.Y(0)), (x + BW / 2, G.Y(v0 * g0)), (x - BW / 2, G.Y(v0 * g0))],
                   fill="pos_l", stroke="pos", width=2)
            for j in range(k):
                g = prog(t, tk + 0.25 * (j + 1), 0.25, "out")
                if g <= 0:
                    continue
                y0 = v0 + a * j
                L.poly([(x - BW / 2, G.Y(y0)), (x + BW / 2, G.Y(y0)), (x + BW / 2, G.Y(y0 + a * g)),
                        (x - BW / 2, G.Y(y0 + a * g))], fill="acc_l", stroke="acc", width=2)
            if t >= tk + 0.3 * k + 0.4:
                L.stamp(F.tag_img(r"\t{%d}" % (v0 + a * k), 30, "vel_d"), x, G.Y(v0 + a * k) - 26)
        a_ = prog(t, times[0], 0.4)
        L.stamp(F.tag_img(r"\c{pos_d}{v_0}", 30), G.X(0) + BW / 2 + 4, G.Y(v0 / 2), alpha=a_)
    mg(sc, cols, at=times[0], z=4)
    l4 = sc.say("La velocidad es la inicial, más la aceleración multiplicada por el tiempo: uve igual a uve cero, "
                "más a por te.")
    put(sc, F.def_card("VELOCIDAD", [r"v = \c{pos_d}{v_0} + \c{acc}{a}\,t"], head_bg="acc", size=72,
                       border=("acc", 4)), 1490, 300, l4.at("uve igual"), z=7)
    put(sc, F.fcard(r"v = 4 + 2\,t", size=52, border=("vel", 3)), 1490, 500, l4.at("velocidad es"), z=7)
    l5 = sc.say("Si unimos las puntas de las columnas, sale una recta: es la gráfica velocidad-tiempo. Corta al eje en "
                "uve cero, y su pendiente es la aceleración: 2 metros por segundo en cada segundo.")
    fv = lambda t: v0 + a * t  # noqa: E731
    t_line = l5.at("unimos")
    mg(sc, lambda L, t: G.curve(L, fv, 0, 4.4 * prog(t, t_line, 1.2, "io"), "vel", 6), at=t_line, z=5)
    mg(sc, lambda L, t: G.slope(L, fv, 1, 3, "acc", prog(t, l5.at("pendiente"), 1.2, "lin"), r"Δt = 2\,\t{s}",
                                r"Δv = 4\,\t{m/s}"), at=l5.at("pendiente"), z=6)
    put(sc, F.fcard([r"\t{Pendiente de }v\t{-}t = \c{acc}{a}", r"\frac{4\,\t{m/s}}{2\,\t{s}} = 2\,\t{m/s}^2"], size=40,
                    border=("acc", 3)), 1490, 720, l5.at("aceleración:"), z=7)
    sc.wait(0.6)


# ============================================================================
# 3. x = x0 + v0 t + ½ a t²  (área bajo la v-t)
# ============================================================================
def ecuacion_x(mv):
    sc = scn(mv, "ec-x", bg="grid", lead=0.4)
    F.title(sc, "SEGUNDA ECUACIÓN: LA POSICIÓN", at=0.3)
    v0, a, T = 4.0, 2.0, 3.0
    G = F.Graph(x0=260, y0=840, w=840, h=580, tmax=4.6, vmin=0, vmax=14, tstep=1, vstep=2,
                vlabel=r"v\;\t{(m/s)}")
    fv = lambda t: v0 + a * t  # noqa: E731
    l1 = sc.say("¿Y la posición? Ya sabemos que el área bajo la gráfica velocidad-tiempo es el desplazamiento. "
                "Aquí, hasta los 3 segundos.")
    mg(sc, lambda L, t: (G.axes(L), G.curve(L, fv, 0, 4.4, "vel", 6)), at=0.2, z=3)
    t_area = l1.at("área")
    l2 = sc.say("El área tiene dos partes. Un rectángulo, de base te y altura uve cero: uve cero por te.")
    l3 = sc.say("Y encima, un triángulo, de base te y altura a por te: un medio de a por te al cuadrado.")
    l4 = sc.say("Sumamos las dos áreas, y añadimos la posición inicial:")

    def area(L, t):
        g = prog(t, t_area, 0.8, "io")
        if t < l2.at("rectángulo"):
            G.area(L, fv, 0, T * g, (178, 38, 116, 60))
            return
        r = prog(t, l2.at("rectángulo"), 0.5)
        L.poly([G.P(0, 0), G.P(T, 0), G.P(T, v0), G.P(0, v0)], fill=(222, 104, 24, 110), stroke="pos", width=3,
               alpha=r)
        L.stamp(F.tag_img(r"v_0\,t", 40, "pos_d"), G.X(T / 2), G.Y(v0 / 2), alpha=r)
        q = prog(t, l3.at("triángulo"), 0.5)
        L.poly([G.P(0, v0), G.P(T, v0), G.P(T, v0 + a * T)], fill=(206, 36, 34, 100), stroke="acc", width=3, alpha=q)
        L.stamp(F.tag_img(r"\frac{1}{2}\,a\,t^2", 36, "acc_d"), G.X(T * 0.68), G.Y(v0 + a * T * 0.36), alpha=q)
        h = prog(t, l2.at("base te"), 0.4)
        L.stamp(F.tag_img(r"\t{base: }t", 30), G.X(T / 2), G.Y(0) - 28, alpha=h)
        k = prog(t, l3.at("altura a"), 0.4)
        L.line([(G.X(T) + 24, G.Y(v0)), (G.X(T) + 24, G.Y(v0 + a * T))], "acc", 3, alpha=k)
        L.stamp(F.tag_img(r"a\,t", 32, "acc_d"), G.X(T) + 70, G.Y(v0 + a * T / 2), alpha=k)
    mg(sc, area, at=t_area, z=4)
    put(sc, F.def_card("POSICIÓN", [r"x = \c{pos_d}{x_0} + \c{pos}{v_0\,t} + \c{acc}{\frac{1}{2}\,a\,t^2}"],
                       head_bg="acc", size=58, border=("acc", 4)), 1500, 300, l4.at("Sumamos"), z=7)
    l5 = sc.say("Con números: 4 por 3, 12 metros de rectángulo, más un medio por 2 por 9, 9 metros de triángulo. En "
                "total, 21 metros en 3 segundos.")
    put(sc, F.fcard([r"Δx = 4 · 3 + \frac{1}{2} · 2 · 3^2", r"Δx = 12 + 9 = 21\,\t{m}"], size=44, border=("pos", 3)),
        1500, 540, l5.at("Con números"), z=7)
    l6 = sc.say("Comprobación visual: el coche del semáforo salía del reposo con 2 m/s². Su fórmula queda equis igual a "
                "te al cuadrado: 1, 4, 9, 16 metros. Justo donde estaban sus fotos.")
    put(sc, F.fcard([r"x = \frac{1}{2} · 2 · t^2 = t^2", r"\t{1, 4, 9, 16 m}\;\t{✓}"], size=42,
                    border=("grass_d", 3)), 1500, 780, l6.at("Comprobación"), z=7)
    sc.wait(0.6)


# ============================================================================
# 4. v² = v0² + 2a(x − x0)   (sin tiempo)
# ============================================================================
def ecuacion_sin_t(mv):
    sc = scn(mv, "ec-v2", bg="grid", lead=0.4)
    F.title(sc, "TERCERA ECUACIÓN: SIN TIEMPO", at=0.3)
    l1 = sc.say("A veces no conocemos el tiempo, ni nos lo preguntan. Para eso hay una tercera ecuación, que sale de "
                "juntar las otras dos.")
    l2 = sc.say("El desplazamiento es el área del trapecio: la velocidad media por el tiempo. Y la velocidad media, con "
                "aceleración constante, es la media entre uve cero y uve.")
    l3 = sc.say("Y de la primera ecuación, el tiempo es uve menos uve cero, entre a.")
    l4 = sc.say("Multiplicamos, y queda: uve al cuadrado igual a uve cero al cuadrado, más dos a por el "
                "desplazamiento.")
    lines = [(r"Δx = v_m · t = \frac{v_0 + v}{2} · t", l2.at("velocidad media por")),
             (r"t = \frac{v − v_0}{a}", l3.at("tiempo es")),
             (r"Δx = \frac{(v + v_0)(v − v_0)}{2a} = \frac{v^2 − v_0^2}{2a}", l4.at("Multiplicamos")),
             (r"v^2 = v_0^2 + 2\,a\,Δx", l4.at("queda"))]
    sh = F.sheet(1000, 640, seed=31)
    put(sc, sh, 700, 560, l2.start(), rot=-0.4, z=3)
    F.board(sc, lines, 260, 300, size=50, gap=40, z=5)
    put(sc, F.def_card("SIN TIEMPO", [r"v^2 = v_0^2 + 2\,a\,(x − x_0)"], head_bg="acc", size=58, border=("acc", 4)),
        1560, 330, l4.at("uve al cuadrado igual"), z=7)
    l5 = sc.say("Comprobación con nuestro coche: salía a 4 m/s, a los 3 segundos iba a 10, y había avanzado 21 metros. "
                "4 al cuadrado más 2 por 2 por 21: 16 más 84, 100. Y 10 al cuadrado es 100. ¡Cuadra!")
    put(sc, F.fcard([r"v_0^2 + 2\,a\,Δx = 16 + 84 = 100", r"v^2 = 10^2 = 100\;\t{✓}"], size=42, border=("grass_d", 3)),
        1560, 620, l5.at("Comprobación"), z=7)
    sc.wait(0.6)


# ============================================================================
# 5. cuándo usar cada una
# ============================================================================
def cual_usar(mv):
    sc = scn(mv, "cual", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "¿QUÉ ECUACIÓN USO?", at=0.3)
    l1 = sc.say("Tenemos tres ecuaciones, y cada una deja fuera una magnitud.")
    rows = [(r"v = v_0 + a\,t", "Δx", "posición", 290), (r"x = x_0 + v_0\,t + \frac{1}{2}\,a\,t^2", "v", "velocidad final", 450),
            (r"v^2 = v_0^2 + 2\,a\,(x − x_0)", "t", "tiempo", 610)]
    l2 = sc.say("La primera no tiene la posición. La segunda no tiene la velocidad final. Y la tercera no tiene el "
                "tiempo.")
    keys = [l2.at("primera"), l2.at("segunda"), l2.at("tercera")]
    for k, (src, miss, word, y) in enumerate(rows):
        put(sc, F.fcard(src, size=50, border=("acc", 3), min_w=760), 640, y, l1.at("tres ecuaciones", after=0.3 * k),
            z=5)
        put(sc, F.say_card("sin {acc:%s}" % word, size=40, border=("acc", 3)), 1340, y, keys[k], enter="pop", z=5)
    l3 = sc.say("Así que pregúntate: ¿qué magnitud no me dan, ni me piden? Usa la ecuación en la que no aparece.")
    put(sc, kit.ojo("¿Qué magnitud no me dan ni me piden?\nUsa la ecuación en la que no aparece.", size=34, max_w=900),
        W / 2, 805, l3.at("pregúntate"), z=7)
    sc.wait(0.4)

    sc = scn(mv, "check-cual", bg="grid", lead=0.3)
    l4 = sc.say("Comprueba: un coche pasa de 20 a 30 m/s en 100 metros. ¿Qué aceleración tiene? ¿Qué ecuación "
                "usarías?")
    F.quiz(sc, "De 20 a 30 m/s en 100 m. ¿Aceleración? ¿Qué ecuación?", lead=l4.start(), y=200, size=42, max_w=1200)
    opts = [(r"v = v_0 + a\,t", 420), (r"x = x_0 + v_0\,t + \frac{1}{2}\,a\,t^2", 960), (r"v^2 = v_0^2 + 2\,a\,Δx", 1500)]
    for k, (src, x) in enumerate(opts):
        put(sc, F.fcard(src, size=42, border=("ink", 2)), x, 470, l4.at("Qué ecuación", after=0.2 * k), enter="pop", z=5)
    t_r = F.think(sc, 4.0)
    l5 = sc.say("La tercera: no nos dan el tiempo ni nos lo piden. 30 al cuadrado es igual a 20 al cuadrado, más 2 por a "
                "por 100. 900 menos 400, 500, igual a 200 a: a igual a 2,5 m/s².")
    put(sc, F.check_mark(110), 1500 + 230, 420, t_r, enter="pop", z=6)
    lines = [(r"30^2 = 20^2 + 2 · a · 100", l5.at("30 al cuadrado")),
             (r"900 − 400 = 200\,a", l5.at("900")), (r"a = \frac{500}{200} = \c{acc}{2,5\,\t{m/s}^2}", l5.at("a igual"))]
    F.board(sc, lines, 640, 600, size=46, gap=20, z=6)
    sc.wait(0.6)


# ============================================================================
# 6. gráficas x-t, v-t y a-t: un coche que acelera y otro que frena
# ============================================================================
def graficas(mv, frena=False):
    name = "graf-frena" if frena else "graf-acelera"
    sc = scn(mv, name, bg="grid", lead=0.4, transition="cut" if frena else "wipe")
    if frena:
        v0, a, T = 10.0, -2.0, 5.0
    else:
        v0, a, T = 0.0, 2.0, 5.0
    fx = lambda t: v0 * t + 0.5 * a * t * t  # noqa: E731
    fv = lambda t: v0 + a * t  # noqa: E731
    gx = F.Graph(x0=200, y0=300, w=560, h=170, tmax=5.6, vmin=0, vmax=30, tstep=1, vstep=10, size=24,
                 vlabel=r"x\;\t{(m)}")
    gv = F.Graph(x0=200, y0=580, w=560, h=170, tmax=5.6, vmin=0, vmax=12, tstep=1, vstep=4, size=24,
                 vlabel=r"v\;\t{(m/s)}")
    ga = F.Graph(x0=200, y0=850, w=560, h=170, tmax=5.6, vmin=-3 if frena else 0, vmax=1 if frena else 3, tstep=1,
                 vstep=1, size=24, vlabel=r"a\;\t{(m/s}^2\t{)}")
    if frena:
        l1 = sc.say("Ahora un coche que frena: va a 10 m/s y frena con una aceleración de menos 2 m/s².")
    else:
        l1 = sc.say("Veamos las tres gráficas del MRUA mientras el coche del semáforo arranca, con 2 m/s² de "
                    "aceleración.")
    t_ax = l1.start(0.3)
    mg(sc, lambda L, t: [g.axes(L, prog(t, t_ax, 0.7, "out")) for g in (gx, gv, ga)], at=t_ax, z=2)
    # the car on a short road on the right
    RY = 520.0
    road_spr = F.road_piece(1000, 170, seed=257)
    sc.add(road_spr, 1380, RY, at=0.2, enter="cut", rot=0, z=0, jitter=0.3)
    car = F.car_top("mustard", L=130)
    CX0, PX = 950.0, 26.0
    state = {}
    t0 = l1.end(0.4)
    state["t0"] = t0
    k_slow = 1.6

    def sim(t):
        return min(max(0.0, (t - state["t0"]) / k_slow), T)
    live(sc, lambda t: (car, CX0 + fx(sim(t)) * PX, RY + 40, 0.0), at=0.0, z=4, jitter=0.4)

    def plots(L, t):
        s = sim(t)
        gx.curve(L, fx, 0, s, "pos", 5)
        gv.curve(L, fv, 0, s, "vel", 5)
        ga.curve(L, lambda tt: a, 0, s, "acc", 5)
        if s > 0:
            gx.dot(L, s, fx(s), "pos_d", 7)
            gv.dot(L, s, fv(s), "vel_d", 7)
            ga.dot(L, s, a, "acc_d", 7)
        # velocity and acceleration arrows on the car
        cx = CX0 + fx(s) * PX
        if abs(fv(s)) > 0.05:
            L.arrow((cx, RY - 60), (cx + fv(s) * 22, RY - 60), "vel", 8, head=26)
        L.arrow((cx, RY + 130), (cx + a * 40, RY + 130), "acc", 8, head=26)
        L.stamp(F.tag_img(r"t = %s\,\t{s}" % F.num(s), 34, "ink", border=("ink", 2)), 1700, 300)
    mg(sc, plots, at=t0 - 0.3, z=5)
    sc.cursor = max(sc.cursor, t0 + 0.2)
    if frena:
        l2 = sc.say("La posición sigue aumentando, pero cada vez menos: la parábola se curva hacia abajo y se aplana "
                    "cuando el coche se para.")
        l3 = sc.say("La velocidad baja en línea recta hasta cero. Y la aceleración es una recta horizontal por debajo "
                    "del eje: es negativa.")
        l4 = sc.say("¿Cuánto ha recorrido hasta pararse? Sin tiempo: 0 igual a 10 al cuadrado, más 2 por menos 2 por "
                    "equis. Equis igual a 100 entre 4: 25 metros.")
        put(sc, F.fcard([r"0 = 10^2 + 2 · (−2) · Δx", r"Δx = \frac{100}{4} = \c{pos}{25\,\t{m}}"], size=42,
                        border=("pos", 3)), 1400, 810, l4.at("Cuánto"), z=7)
        notes = [(r"\t{parábola que se aplana}", gx, l2.at("parábola")), (r"\t{recta que baja: pendiente }a < 0", gv,
                                                                          l3.at("baja")),
                 (r"\t{horizontal, negativa}", ga, l3.at("horizontal"))]
    else:
        l2 = sc.say("La gráfica de posición es una parábola. Su pendiente, que es la velocidad, va creciendo.")
        l3 = sc.say("La de velocidad es una recta inclinada, y su pendiente es la aceleración. Y la de aceleración es "
                    "una recta horizontal, porque la aceleración es constante.")
        l4 = sc.say("Fíjate: la velocidad y la aceleración apuntan hacia el mismo lado. Por eso va cada vez más rápido.")
        put(sc, F.fcard(r"\c{vel}{v}\t{ y }\c{acc}{a}\t{: mismo sentido → acelera}", size=40, border=("acc", 3)),
            1400, 810, l4.at("mismo lado"), z=7)
        notes = [(r"\t{parábola: pendiente creciente}", gx, l2.at("parábola")),
                 (r"\t{recta: pendiente }= a", gv, l3.at("recta inclinada")),
                 (r"\t{horizontal: }a\t{ constante}", ga, l3.at("horizontal"))]

    def note_fn(L, t):
        for src, g, tt in notes:
            al = prog(t, tt, 0.4)
            L.stamp(F.tag_img(src, 28, "ink", border=("ink", 2)), g.x0 + g.w * 0.55, g.y0 - g.h - 10, alpha=al)
    mg(sc, note_fn, at=min(tt for _, _, tt in notes), z=6)
    sc.wait(0.6)


def signos(mv):
    sc = scn(mv, "signos", bg="grid", lead=0.4)
    F.title(sc, "¿ACELERA O FRENA? MIRA LOS SIGNOS", at=0.3)
    l1 = sc.say("Regla rápida: si la velocidad y la aceleración tienen el mismo signo, el móvil va cada vez más rápido. "
                "Si tienen signos opuestos, frena.")
    put(sc, F.fcard([r"\t{Mismo signo: }\c{acc}{\t{acelera}}", r"\t{Signos opuestos: }\c{acc}{\t{frena}}"], size=46,
                    border=("acc", 4)), W / 2, 290, l1.at("Regla"), z=6)
    l2 = sc.say("Comprueba: ¿acelera o frena en cada caso?")
    F.quiz(sc, "¿Acelera o frena?", lead=l2.start(), x=1640, y=470, size=40, max_w=440)
    cases = [(+8, +2, 300), (+8, -2, 750), (-8, -2, 1200)]

    def draw(L, t):
        for k, (v, a, x) in enumerate(cases):
            g = prog(t, l2.start(0.2 + 0.3 * k), 0.4)
            y = 560
            sv, sa = (1 if v > 0 else -1), (1 if a > 0 else -1)
            L.arrow((x - 80 * sv, y - 40), (x - 80 * sv + sv * 170 * g, y - 40), "vel", 9, head=28, alpha=g)
            L.arrow((x - 50 * sa, y + 40), (x - 50 * sa + sa * 100 * g, y + 40), "acc", 9, head=28, alpha=g)
            L.stamp(F.formula(r"v = %s\,\t{m/s}" % ("+8" if v > 0 else "−8"), 32, "vel_d"), x, y - 100, alpha=g)
            L.stamp(F.formula(r"a = %s\,\t{m/s}^2" % ("+2" if a > 0 else "−2"), 32, "acc_d"), x, y + 100, alpha=g)
    mg(sc, draw, at=l2.start(0.2), z=5)
    t_r = F.think(sc, 4.0, x=1640, y=650)
    l3 = sc.say("Primero: mismo signo, acelera. Segundo: signos opuestos, frena. Y el tercero, ojo: los dos negativos. "
                "Va hacia atrás cada vez más deprisa: acelera.")
    for k, (word, ok_txt) in enumerate((("Primero", "acelera"), ("Segundo", "frena"), ("tercero", "acelera"))):
        put(sc, F.say_card("{acc:%s}" % ok_txt, size=44, border=("acc", 3)), cases[k][2], 780, l3.at(word),
            enter="pop", z=6)
    sc.wait(0.6)


# ============================================================================
# 7. problema completo con conversión de unidades
# ============================================================================
def problema(mv):
    sc = scn(mv, "problema", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "PROBLEMA RESUELTO", at=0.3)
    st = F.tabbed(F.say_card("Un coche parte del reposo y alcanza {vel:108 km/h} en {pos:6 s}.\n"
                             "a) ¿Aceleración?  b) ¿Distancia recorrida en esos 6 s?\n"
                             "c) ¿Velocidad cuando lleva 40 m? Dala en km/h.", size=34, max_w=820,
                             border=("mustard", 3)), "ENUNCIADO", head_bg="mustard", head_color="ink")
    l1 = sc.say("Un problema completo. Un coche parte del reposo y alcanza 108 km/h en 6 segundos. ¿Cuál es su "
                "aceleración? ¿Qué distancia recorre en esos 6 segundos? ¿Y qué velocidad lleva cuando ha recorrido "
                "40 metros? Dala en km/h.")
    put(sc, st, 500, 290, l1.start(), z=6)
    l2 = sc.say("Lo primero, las unidades: todo en el Sistema Internacional. Para pasar de km/h a m/s se divide entre "
                "3,6, porque un kilómetro son 1000 metros y una hora son 3600 segundos.")
    conv = F.fcard([r"108\,\t{km/h} = \frac{108 · 1000\,\t{m}}{3600\,\t{s}}", r"= \frac{108}{3,6} = \c{vel}{30\,\t{m/s}}"],
                   size=42, border=("vel", 3))
    put(sc, conv, 500, 570, l2.at("Lo primero"), z=6)
    l3 = sc.say("Datos: posición inicial cero, velocidad inicial cero porque parte del reposo, y a los 6 segundos, 30 "
                "m/s.")
    sh = F.sheet(860, 780, seed=33)
    put(sc, sh, 1440, 560, l3.start(), rot=0.4, z=3)
    l4 = sc.say("Apartado a: tenemos velocidades y tiempo, así que usamos la primera ecuación. 30 igual a 0 más a por "
                "6: a igual a 5 m/s².")
    l5 = sc.say("Apartado b: nos piden la distancia, con el tiempo conocido. Segunda ecuación: un medio por 5 por 6 al "
                "cuadrado, 90 metros.")
    l6 = sc.say("Apartado c: ahora no hay tiempo, así que usamos la tercera. Uve al cuadrado igual a 0 más 2 por 5 por "
                "40: 400. Uve igual a 20 m/s. Y multiplicando por 3,6, son 72 km/h.")
    lines = [(r"x_0 = 0\quad v_0 = 0\quad v = 30\,\t{m/s}\quad t = 6\,\t{s}", l3.at("Datos")),
             (r"\t{a) } 30 = 0 + a · 6", l4.at("30 igual")), (r"a = \c{acc}{5\,\t{m/s}^2}", l4.at("a igual a 5")),
             (r"\t{b) } x = \frac{1}{2} · 5 · 6^2 = \c{pos}{90\,\t{m}}", l5.at("un medio")),
             (r"\t{c) } v^2 = 0 + 2 · 5 · 40 = 400", l6.at("Uve al cuadrado")),
             (r"v = 20\,\t{m/s} · 3,6 = \c{vel}{72\,\t{km/h}}", l6.at("Uve igual"))]
    F.board(sc, lines, 1050, 260, size=38, gap=30, z=5)
    l7 = sc.say("Comprobamos. El apartado b, con la velocidad media: de 0 a 30, la media es 15 m/s, y 15 por 6 da 90 "
                "metros. ¡Igual!")
    put(sc, F.fcard(r"v_m = \frac{0 + 30}{2} = 15\,\t{m/s}\;\Rightarrow\; 15 · 6 = 90\,\t{m}\;\t{✓}", size=36,
                    border=("grass_d", 3)), 500, 750, l7.at("Comprobamos"), z=7)
    l8 = sc.say("Y el c tiene sentido: a los 40 metros aún no ha llegado a los 108 km/h, así que 72 km/h es razonable.")
    put(sc, F.fcard(r"72\,\t{km/h} < 108\,\t{km/h}\;\t{✓}", size=38, border=("grass_d", 3)), 500, 845, l8.at("sentido"),
        z=7)
    sc.wait(0.6)


RESUMEN = [
    (r"\b{MRUA:}\t{ trayectoria recta y aceleración constante: }v\t{ cambia lo mismo en tiempos iguales}",
     "MRUA: trayectoria recta y aceleración constante. La velocidad cambia lo mismo en tiempos iguales."),
    (r"v = v_0 + a\,t \qquad\t{(sin posición)}", "Uve igual a uve cero más a por te, la que no tiene posición."),
    (r"x = x_0 + v_0\,t + \frac{1}{2}\,a\,t^2 \qquad\t{(sin velocidad final)}",
     "Equis igual a equis cero, más uve cero te, más un medio de a te al cuadrado, la que no tiene velocidad final."),
    (r"v^2 = v_0^2 + 2\,a\,(x − x_0) \qquad\t{(sin tiempo)}",
     "Y uve al cuadrado igual a uve cero al cuadrado más dos a por el desplazamiento, la que no tiene tiempo."),
    (r"\b{Gráficas:}\t{ x-t parábola · v-t recta (pendiente }a\t{) · a-t horizontal}",
     "Gráficas: posición-tiempo, parábola; velocidad-tiempo, recta de pendiente a; aceleración-tiempo, horizontal."),
    (r"\t{Mismo signo }v\t{ y }a\t{: acelera · opuestos: frena · km/h ÷ 3,6 = m/s}",
     "Mismo signo, acelera; signos opuestos, frena. Y no olvides pasar los kilómetros por hora a metros por segundo."),
]


def build(only=None):
    mv = K.new_movie()
    parts = [("intro", intro), ("fotos", fotos), ("ecv", ecuacion_v), ("ecx", ecuacion_x), ("ecv2", ecuacion_sin_t),
             ("cual", cual_usar), ("graf", lambda m: graficas(m, False)), ("graf", lambda m: graficas(m, True)),
             ("signos", signos), ("prob", problema),
             ("resumen", lambda m: K.resumen(m, "REPASO DEL TEMA 3", RESUMEN, size=34)),
             ("fin", lambda m: K.fin(m, 3, "Próximo: Tema 4 · Caída libre",
                                     "Fin del tema tres. En el siguiente: la caída libre y los lanzamientos "
                                     "verticales. ¡Hasta pronto!"))]
    for name, fn in parts:
        if only and name not in only:
            continue
        fn(mv)
    return mv


def chapters(mv):
    names = {"title": "Inicio", "fotos": "1 · Aceleración constante", "ec-v": "2 · v = v0 + a·t",
             "ec-x": "3 · x = x0 + v0·t + ½·a·t²", "ec-v2": "4 · v² = v0² + 2a(x − x0)", "cual": "5 · ¿Qué ecuación uso?",
             "graf-acelera": "6 · Gráficas x-t, v-t y a-t", "signos": "7 · ¿Acelera o frena?",
             "problema": "8 · Problema con conversión de unidades", "resumen": "Repaso del tema"}
    return [(st, names[sc.name]) for sc, st in zip(mv.scenes, mv.starts) if sc.name in names]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "out/Cinematica_T3_MRUA.mp4"
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

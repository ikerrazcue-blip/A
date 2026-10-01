"""Física · Cinemática · Tema 1: Fundamentos de cinemática (stop-motion de papel + motion graphics).

Explicación continua: el tren y los ejes (movimiento relativo) → punto material, trayectoria y posición →
ida y vuelta (espacio recorrido / desplazamiento) → velocidad media con reloj → velocidad instantánea
(tangente) → aceleración al arrancar, frenar y girar (componentes tangencial y normal) → repaso.
Sin azul en ningún elemento (ver stopmo/fisica.py).

    python3 scenes/cinematica_t1.py out/cinematica_t1.mp4            # vídeo completo
    python3 scenes/cinematica_t1.py out/cinematica_t1.mp4 --stills   # fotogramas de control
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stopmo import fisica as F, gfx, greek, kit, movie  # noqa: E402
from stopmo.fisica import formula, mg, live, prog, lerp, lerp2, clamp01  # noqa: E402
from stopmo.gfx import W, H, card  # noqa: E402
from stopmo.movie import Movie  # noqa: E402

# how the narrator must read some words (the subtitles keep the written form)
movie.PRONOUNCE.update({
    r"«|»": "",
    r"\bm/s\b": "metros por segundo",
    r"\bkm/h\b": "kilómetros por hora",
})


def put(sc, spr, x, y, at, enter="drop", rot=None, **kw):
    if rot is None:
        rot = ((F._seed(f"{x:.0f}|{y:.0f}") % 100) / 100 - 0.5) * 2.4
    return sc.add(spr, x, y, at=at, enter=enter, rot=rot, **kw)


def scn(mv, name, **kw):
    kw.setdefault("transition", "cut")
    kw.setdefault("sweep", True)
    return mv.scene(name, **kw)


# ============================================================================
# 0. título y qué es la cinemática
# ============================================================================
def intro(mv):
    sc = mv.scene("title", bg="kraft", lead=0.2, transition="cut")
    t_j = sc.jingle(0.25, "fis_intro", gain=0.45)
    ttl = greek.title_block("CINEMÁTICA", size=168, color="cream", tracking=0.05, font_name="body9")
    sc.add(ttl, W / 2, 330, at=0.6, enter="drop", z=2, jitter=0.6)
    sub = card("Tema 1 · Fundamentos", size=64, font_name="body9", bg="cream", color="ink", pad=(46, 16), seed=33,
               border=("pos", 5))
    sc.add(sub, W / 2, 520, at=1.0, enter="drop", z=3, rot=-1.5)
    tag = card("Física y Química", size=34, font_name="body9", bg="mustard", color="ink", pad=(22, 8), seed=34)
    sc.add(tag, W / 2 + sub.w / 2 - 70, 445, at=1.4, enter="pop", z=4, rot=5)
    # the little train crossing the bottom of the title card
    tr = F.train_sprite()

    def train_pos(t):
        x = -500 + 260 * max(0.0, t - 0.4)
        return tr, x, 840, 0, 0.42
    live(sc, train_pos, at=0.4, z=1, jitter=0.6)
    sc.add(F.medal("stopwatch", 150, bg="pos_l"), 250, 300, at=1.2, enter="pop", z=2, rot=-6)
    sc.add(F.medal("speedometer", 150, bg="vel_l"), W - 250, 300, at=1.35, enter="pop", z=2, rot=6)
    sc.cursor = max(sc.cursor, t_j - 0.7)
    sc.say("Cinemática. Tema uno: fundamentos del movimiento.")
    sc.wait(0.5)

    sc = scn(mv, "que-es", bg="grid", transition="wipe", lead=0.5)
    F.title(sc, "¿QUÉ ESTUDIA LA CINEMÁTICA?", at=0.4)
    l1 = sc.say("La cinemática describe cómo se mueve un cuerpo: dónde está, por dónde va, cuándo pasa por cada "
                "sitio y lo rápido que lo hace.")
    qs = [("¿DÓNDE?", "position-marker", "pos_l", 330, "dónde"), ("¿POR DÓNDE?", "path-distance", "space_l", 750,
                                                                    "por dónde"),
          ("¿CUÁNDO?", "stopwatch", "grey_l", 1170, "cuándo"), ("¿CÓMO DE RÁPIDO?", "speedometer", "vel_l", 1590,
                                                               "rápido")]
    for txt, ic, bg, x, k in qs:
        med = F.medal(ic, 170, bg=bg)
        lab = card(txt, size=38, font_name="body9", bg="cream", pad=(20, 8), seed=F._seed(txt))
        put(sc, kit.compose([(med, 0, 0), (lab, 0, 112, -2)]), x, 430, l1.at(k, after=-0.15), enter="pop")
    l2 = sc.say("Lo que no hace es preguntarse por qué se mueve. Las causas del movimiento, las fuerzas, las "
                "estudia otra parte de la física: la dinámica.")
    why = card("¿POR QUÉ SE MUEVE?  →  eso es {acc:dinámica}", size=44, font_name="body9", bg="cream", pad=(36, 16),
               seed=41, hl="acc")
    put(sc, why, 860, 760, l2.at("por qué"), rot=-1)
    put(sc, F.check_mark(110, ok=False), 860 + why.w / 2 + 40, 760, l2.at("dinámica"), enter="pop")
    l3 = sc.say("Y para describir un movimiento, todo empieza con una pregunta que parece muy fácil.")
    sc.wait(0.3)


# ============================================================================
# 1. el tren: el movimiento es relativo
# ============================================================================
def tren(mv):
    sc = mv.scene("tren", bg="sky", lead=0.6, transition="wipe", sweep=False)
    info = F.train_info()
    spr = F.train_sprite()
    REAR = 110.0                 # screen x of the carriage's rear while the camera rides with the train
    WHEEL = 700.0                # screen y of the bottom of the wheels
    top = WHEEL - info["wheel"]  # screen y of the train drawing's top edge
    FLOOR = top + info["floor"] - 4
    PXM = (info["ana"][0] - info["rear"]) / 12.0   # Ana sits 12 m from the rear of the carriage
    V = 3.0 * PXM                # 3 m/s (a train leaving the station), in px/s
    ANA_DX = info["ana"][0] - info["rear"]
    ANA_Y = top + info["ana"][1]
    LEO_X = 330.0                # where Leo is on screen once the camera stops on the platform
    PLAT = F.PLAT_TOP

    l1 = sc.say("Esta es Ana. Va sentada en un tren, junto a la ventanilla.")
    l2 = sc.say("Primera pregunta: ¿Ana se está moviendo?")
    l3 = sc.say("Por la ventanilla, ve pasar el paisaje hacia atrás. Pero ella no se ha levantado de su asiento.")
    l4 = sc.say("Para responder, hay que decir respecto a qué. Necesitamos un {pos:sistema de referencia}: un origen "
                "y unos ejes desde los que medir las posiciones.")
    l5 = sc.say("Empezamos pegando los ejes al tren, con el origen en la parte de atrás del vagón.")
    l6 = sc.say("Respecto a estos ejes, Ana está siempre a doce metros del origen. Su posición no cambia: respecto "
                "al tren, Ana está {pos:en reposo}.")
    l7 = sc.say("En cambio, Leo, que espera en el andén, pasa hacia atrás: su posición cambia. Respecto al tren, "
                "Leo {pos:se mueve}.")
    l8 = sc.say("Ahora cambiamos de sistema de referencia: despegamos los ejes del tren y los pegamos al andén, con "
                "el origen en Leo.")
    l9 = sc.say("Respecto al andén, Leo está en reposo. Y es Ana la que se mueve: su posición aumenta tres metros "
                "cada segundo.")
    sc.wait(0.6)

    t_sw = l8.at("despegamos")
    TD = 1.6

    def cam(t):
        if t <= t_sw:
            return V * t
        tau = min(t - t_sw, TD)
        return V * t_sw + V * (tau - tau * tau / (2 * TD))

    def rear_s(t):               # carriage rear on screen
        return REAR + V * t - cam(t)

    LEO_W = LEO_X + cam(t_sw + TD + 10)   # Leo's world x

    def leo_s(t):
        return LEO_W - cam(t)

    t_end = sc.now() + 1.0
    span = (-400, cam(t_end) + W + 600)
    hills = F.hills_tile()
    items_back = [(F.sun_piece(), 1580, 170, 0.0, 0.6), (F.cloud(300, 1), 420, 150, 0.1, 0.6),
                  (F.cloud(220, 2), 1180, 105, 0.1, 0.6), (F.cloud(260, 3), 2200, 170, 0.1, 0.6),
                  (hills, hills.w / 2 - 300, 330 + hills.h / 2 - 40, 0.3, 0.0)]
    F.world(sc, items_back, cam, at=0.0, z=-3)
    F.world(sc, F.tiles(F.rails_tile(), span[0], span[1], 703), cam, at=0.0, z=-2, shadow=False)
    F.world(sc, F.tiles(F.platform_tile(), span[0], span[1], PLAT + F.platform_tile().h / 2), cam, at=0.0, z=1,
            shadow=False)
    props = []
    lamp = F.lamp_post()
    bench = F.bench()
    x = 900
    while x < span[1]:
        props.append((lamp, x, PLAT - lamp.vh / 2 + 6, 1.0, 0.8))
        props.append((bench, x + 520, PLAT - bench.vh / 2 + 10, 1.0, 0.8))
        x += 1500
    F.world(sc, props, cam, at=0.0, z=2)

    def train_at(t):
        cx = rear_s(t) - info["rear"] + info["w"] / 2
        return spr, cx, top + info["h"] / 2, 0.0
    live(sc, train_at, at=0.0, z=0, jitter=0.5)
    leo = F.leo_sprite()
    live(sc, lambda t: (leo, leo_s(t), PLAT - leo.vh / 2 + 16, 0.0), at=0.0, z=3, jitter=0.9)

    # sounds of the rails
    k = 0
    tt = 0.4
    while tt < t_end:
        sc.sfx(tt, F.clack(0.035, seed=k % 3))
        tt += 1.05
        k += 1

    # --- texts
    put(sc, F.bubble("Ana", size=46, tail="center"), REAR + ANA_DX, ANA_Y - 170, l1.at("Ana"), enter="pop", z=6,
        until=l4.start(), rot=0)
    q = F.say_card("¿Ana se está moviendo?", size=54, border=("pos", 4))
    put(sc, q, W / 2, 112, l2.at("Ana"), z=8, until=l4.start())
    put(sc, F.say_card("{pos:SISTEMA DE REFERENCIA} = origen + ejes", size=44, border=("pos", 4)), W / 2, 112,
        l4.at("sistema"), z=8, until=l8.start())
    put(sc, F.say_card("Respecto al {pos:andén}", size=50, border=("pos", 4)), W / 2, 112, l8.at("pegamos"), z=8)

    # --- axes: glued to the train, then moved to the platform (lift and drop)
    t_ax = l5.at("ejes")

    def origin(t):
        oa = (rear_s(t), FLOOR)
        ob = (leo_s(t), PLAT + 2)
        if t <= t_sw:
            return oa, 0.0
        p = prog(t, t_sw, TD, "io")
        o = lerp2(oa, ob, p)
        return (o[0], o[1] - 90 * math.sin(math.pi * p)), p

    def draw_axes(L, t):
        g = prog(t, t_ax, 0.8, "out")
        o, p = origin(t)
        xe = o[0] + (1860 - o[0]) * g
        ye = o[1] - (o[1] - 300) * g
        F.axes(L, o, x_end=xe, y_end=ye, color="ink", width=6, ticks=(PXM, 5) if g > 0.99 else None,
               lab_size=44)
    mg(sc, draw_axes, at=t_ax, z=6)
    hand = F.icon_piece("hand", 190, "skin")

    def hand_at(t):
        # the animator's hand comes down from the top, holds the origin while it moves, and leaves
        if t < t_sw - 0.5 or t > t_sw + TD + 0.6:
            return None
        o, p = origin(min(max(t, t_sw), t_sw + TD))
        dy = -720 * (1 - prog(t, t_sw - 0.5, 0.5, "out")) - 720 * prog(t, t_sw + TD, 0.6, "in")
        return hand, o[0] + 18, o[1] - 88 + dy, 172
    live(sc, hand_at, at=t_sw - 0.5, z=9, jitter=1.0)

    # --- readouts (crisp motion graphics on top of the paper)
    def readouts(L, t):
        o, p = origin(t)
        ana_x = rear_s(t) + ANA_DX
        lx = leo_s(t)
        a_in = prog(t, l6.at("doce"), 0.4, "out") * (1 - prog(t, t_sw - 0.1, 0.3))
        b_in = prog(t, t_sw + TD + 0.2, 0.4, "out")
        l_in = prog(t, l7.at("Leo"), 0.4, "out") * (1 - prog(t, t_sw - 0.1, 0.3))
        for who, px, py, alpha in (("Ana", ana_x, ANA_Y - 170, max(a_in, b_in)), ("Leo", lx, PLAT - 330,
                                                                                   max(l_in, b_in))):
            if alpha <= 0.01 or px < -60 or px > W + 60:
                continue
            val = (px - o[0]) / PXM
            src = r"x_{\t{%s}} = %s" % (who, F.num(val, 1, r"\t{m}"))
            L.line([(px, py + 34), (px, o[1])], "pos", 3, dash=[9, 9], alpha=alpha)
            L.circle(px, o[1], 9, fill="pos", alpha=alpha)
            L.stamp(F.tag_img(src, 40, "pos_d", border=("pos", 3)), px, py, alpha=alpha)
    mg(sc, readouts, at=l6.at("doce"), z=7)
    # "+5 m every second" marks while Ana moves away from Leo
    sc.add(F.fcard(r"\c{pos}{x_{\t{Ana}}}\t{ crece 3 m cada segundo}", size=40, border=("pos", 3)), 820, 250,
           at=l9.at("aumenta"), enter="drop", rot=1.2, z=8)
    sc.wait(0.2)
    return sc


def tren_conclusion(mv):
    sc = scn(mv, "relativo", bg="grid", lead=0.5, transition="wipe")
    F.title(sc, "¿QUIÉN TIENE RAZÓN?", at=0.3)
    l1 = sc.say("Entonces, ¿quién tiene razón? Los dos.")
    tr = F.train_sprite()
    leo = F.leo_sprite()
    cols = [(500, "EJES EN EL TREN", "Ana: {b:en reposo}", "Leo: {b:se mueve}"),
            (1420, "EJES EN EL ANDÉN", "Ana: {b:se mueve}", "Leo: {b:en reposo}")]
    l2 = sc.say("Con los ejes pegados al tren, Ana está en reposo y Leo se mueve. Con los ejes pegados al andén, "
                "es justo al revés.")
    for i, (x, head, a, b) in enumerate(cols):
        t0 = l2.start() if i == 0 else l2.at("andén")
        put(sc, F.say_card(head, size=40, bg="pos" if i == 0 else "mustard", color="cream" if i == 0 else "ink"),
            x, 240, t0, enter="pop")
        sc.add(tr, x - 40, 390, at=t0 + 0.2, enter="drop", scale=0.42, rot=0)
        sc.add(leo, x + 330, 380, at=t0 + 0.3, enter="drop", scale=0.42, rot=0)
        put(sc, card(a, size=38, font_name="body", bg="cream", pad=(22, 8), seed=F._seed(a + head)), x - 150, 560,
            t0 + 0.6)
        put(sc, card(b, size=38, font_name="body", bg="cream", pad=(22, 8), seed=F._seed(b + head)), x + 190, 560,
            t0 + 0.9)

        def mini_axes(L, t, x=x, i=i):
            o = (x - 260, 480) if i == 0 else (x + 300, 488)
            F.axes(L, o, x_end=x + 400, y_end=290, width=4, labels=("X", "Y"), lab_size=30)
        mg(sc, mini_axes, at=t0 + 0.4, z=4)
    l3 = sc.say("Un cuerpo se mueve cuando su posición cambia respecto al sistema de referencia elegido. Por eso, el "
                "movimiento y el reposo son {pos:relativos}: siempre hay que decir respecto a qué.")
    d = F.def_card("MOVIMIENTO", [r"\t{Cambio de posición respecto a un}",
                                  r"\b{sistema de referencia}\t{ (origen + ejes).}",
                                  r"\t{Movimiento y reposo son }\c{pos}{\b{relativos}}\t{.}"], size=38,
                   border=("pos", 4))
    put(sc, d, W / 2, 755, l3.at("cambia"), rot=-0.6, z=6)
    sc.wait(0.4)

    # visual check
    sc = scn(mv, "check-tren", bg="grid", lead=0.3)
    l1 = sc.say("Comprueba que lo has entendido. Respecto al tren, ¿el andén está quieto o se mueve?")
    F.quiz(sc, "Respecto al {pos:tren}, ¿el andén está quieto o se mueve?", lead=l1.start())
    put(sc, card("QUIETO", size=56, font_name="body9", bg="cream", pad=(40, 14), seed=51), 640, 560, l1.at("quieto"),
        enter="pop")
    e2 = put(sc, card("SE MUEVE", size=56, font_name="body9", bg="cream", pad=(40, 14), seed=52), 1280, 560,
             l1.at("mueve"), enter="pop")
    t_r = F.think(sc, 3.5)
    l2 = sc.say("Se mueve, hacia atrás. Por eso Ana ve pasar el andén y los árboles hacia atrás, aunque ella no se "
                "levante del asiento.")
    put(sc, F.check_mark(120), 1280 + 210, 520, t_r, enter="pop", z=6)
    e2.pulse(t_r, 0.12)
    put(sc, F.check_mark(110, ok=False), 640 + 180, 520, t_r + 0.3, enter="pop", z=6)
    put(sc, F.say_card("Respecto al tren, el andén va {pos:hacia atrás}.", size=44), W / 2, 800, l2.at("atrás"))
    sc.wait(0.5)


# ============================================================================
# 2. punto material, trayectoria y posición
# ============================================================================
def punto_material(mv):
    sc = scn(mv, "punto", bg="kraft", lead=0.4, transition="wipe")
    F.title(sc, "EL TREN, VISTO DE LEJOS", at=0.3, y=128)
    spr, proj = F.iberia_map(980)
    MX, MY = 600, 575

    def pt(q):
        x, y = proj(*q)
        return MX + x, MY + y
    route = F.Path(F.smooth([pt(q) for q in F.AVE_ROUTE], 8))
    l1 = sc.say("Ahora alejémonos. El tren de Ana va de Madrid a Sevilla: unos 470 kilómetros de vía.",
                tts="Ahora alejémonos. El tren de Ana va de Madrid a Sevilla: unos cuatrocientos setenta kilómetros "
                    "de vía.")
    put(sc, spr, MX, MY, 0.5, rot=-0.6)

    def map_labels(L, t):
        g = prog(t, l1.at("Madrid"), 0.8, "out")
        L.line(route.upto(g), (150, 120, 96), 5, dash=[12, 10])
        for n, q in F.CITIES.items():
            x, y = pt(q)
            big = n in ("Madrid", "Sevilla")
            a = prog(t, l1.at("Madrid" if n != "Sevilla" else "Sevilla"), 0.3, "out")
            L.circle(x, y, 11 if big else 7, fill="ink", alpha=a)
            if n == "Madrid":
                L.stamp(F.tag_img(r"\b{%s}" % n, 34), x - 22, y - 20, "rm", alpha=a)
            else:
                L.stamp(F.tag_img(r"\b{%s}" % n, 34 if big else 26), x + 22, y - 20, "lm", alpha=a)
    mg(sc, map_labels, at=0.5, z=3)
    tr = F.train_sprite()
    mad = pt(F.CITIES["Madrid"])
    l2 = sc.say("El tren mide unos 200 metros. Comparado con el viaje, es más de dos mil veces más corto: dibujado a "
                "esta escala, ni se vería.",
                tts="El tren mide unos doscientos metros. Comparado con el viaje, es más de dos mil veces más corto: "
                    "dibujado a esta escala, ni se vería.")
    l3 = sc.say("Así que, para estudiar el viaje, podemos olvidarnos de su tamaño y representarlo con un solo "
                "punto.")
    t_shrink = l3.at("un solo")

    def train_on_map(t):
        s = 0.11 * (1 - prog(t, t_shrink, 0.6, "in"))
        if s < 0.004:
            return None
        return tr, mad[0] + 70 * s / 0.11, mad[1] - 30, 0.0, s
    live(sc, train_on_map, at=l1.at("tren"), z=4, jitter=0.6)
    # comparison bars (a visual check of the scale)
    bars_t = l2.start()

    def bars(L, t):
        g = prog(t, bars_t, 0.9, "out")
        x0, y0, Lb = 1220, 330, 560
        L.stamp(F.formula(r"\t{viaje: 470 km}", 40, "ink"), x0, y0 - 44, "lm")
        L.line([(x0, y0), (x0 + Lb * g, y0)], "path", 16, cap="butt")
        a = prog(t, l2.at("200"), 0.3)
        L.stamp(F.formula(r"\t{tren: 0,2 km}", 40, "ink"), x0, y0 + 74, "lm", alpha=a)
        L.circle(x0 + 1.5, y0 + 118, 1.5, fill="pos", alpha=a)
        L.stamp(F.formula(r"\h{← ¡ni se ve!}", 40, "acc_d"), x0 + 26, y0 + 118, "lm", alpha=prog(t, l2.at("ni se"),
                                                                                                    0.3))
    e_bars = mg(sc, bars, at=bars_t, z=3)
    put(sc, F.dot_piece(15), mad[0], mad[1], t_shrink + 0.35, enter="pop", rot=0, z=5,
        until=l3.end(0.6))
    l4 = sc.say("Ese modelo se llama {pos:punto material}: despreciamos las dimensiones del cuerpo y concentramos "
                "toda su masa en un punto.")
    t_go = l3.end(0.3)
    dot = F.dot_piece(15)

    def dot_on_route(t):
        u = prog(t, t_go, 4.5, "io")
        x, y = route.at(u)
        return dot, x, y, 0.0
    live(sc, dot_on_route, at=t_go, z=5, jitter=0.3)
    mg(sc, lambda L, t: L.line(route.upto(prog(t, t_go, 4.5, "io")), "pos", 7), at=t_go, z=4)
    d = F.def_card("PUNTO MATERIAL", [r"\t{Modelo: despreciamos el tamaño del}", r"\t{cuerpo y concentramos toda su}",
                                      r"\t{masa en un punto.}"], size=40, border=("pos", 4))
    e_d = put(sc, d, 1500, 640, l4.at("punto material"), rot=1)
    l5 = sc.say("Ojo: que valga o no depende del problema. Para el viaje entero, el tren es un punto. Pero para saber "
                "cuánto tarda en cruzar un puente, su longitud sí importa.")
    e_bars.leave(l5.start(), "slide_r", 0.6)
    e_d.move(l5.start(0.2), y=380, dur=0.6)
    ok = kit.icon_card("Viaje entero: {b:es un punto}", "path-distance", med_bg="space_l", size=38, seed=171)
    no = kit.icon_card("Cruzar un puente: {b:no lo es}", "bridge", med_bg="grey_l", size=38, seed=172)
    put(sc, ok, 1460, 610, l5.at("viaje entero"), enter="slide_r")
    put(sc, F.check_mark(84), 1460 + ok.vw / 2 + 30, 610, l5.at("es un punto"), enter="pop", z=6)
    put(sc, no, 1460, 770, l5.at("puente"), enter="slide_r")
    put(sc, F.check_mark(84, ok=False), 1460 + no.vw / 2 + 30, 770, l5.at("importa"), enter="pop", z=6)
    sc.wait(0.4)


def trayectoria(mv):
    sc = scn(mv, "trayectoria", bg="grid", lead=0.4)
    F.title(sc, "LA TRAYECTORIA", at=0.3)
    l1 = sc.say("Desde ahora, el móvil será un punto. Al moverse, va dejando un rastro, como un lápiz sobre el papel: "
                "esa línea es su {path:trayectoria}.")
    big = F.Path(F.smooth([(160, 640), (420, 380), (760, 560), (1080, 330), (1420, 520), (1760, 300)], 14))
    t0 = l1.at("rastro", after=-0.6)
    dot = F.dot_piece(18)
    live(sc, lambda t: (dot, *big.at(prog(t, t0, 5.0, "io")), 0.0), at=t0, z=5, jitter=0.3,
         until=l1.end(1.2))
    mg(sc, lambda L, t: L.line(big.upto(prog(t, t0, 5.0, "io")), "path", 6, dash=[16, 11]), at=t0, z=4,
       until=l1.end(1.2))
    put(sc, F.say_card("{path:TRAYECTORIA}: línea que describe el móvil", size=44, border=("path", 4)), W / 2, 820,
        l1.at("trayectoria"))
    l2 = sc.say("Si la trayectoria es una recta, el movimiento es {path:rectilíneo}. Si es una curva, es "
                "{path:curvilíneo}.")
    straight = F.Path([(180, 650), (820, 330)])
    curve = F.Path(F.smooth([(1080, 650), (1250, 360), (1480, 600), (1700, 330)], 14))
    for pth, key, lab, x in ((straight, "recta", "RECTILÍNEO", 500), (curve, "curva", "CURVILÍNEO", 1390)):
        ts = l2.at(key, after=-0.2)
        mg(sc, lambda L, t, pth=pth, ts=ts: L.line(pth.upto(prog(t, ts, 1.6, "io")), "path", 6, dash=[16, 11]),
           at=ts, z=4)
        live(sc, lambda t, pth=pth, ts=ts: (dot, *pth.at(prog(t, ts, 1.6, "io")), 0.0), at=ts, z=5, jitter=0.3)
        put(sc, card(lab, size=46, font_name="body9", bg="cream", pad=(30, 10), seed=F._seed(lab),
                     border=("path", 4)), x, 250, l2.at(key, after=0.2), enter="pop")
    l3 = sc.say("La del tren de Madrid a Sevilla, por ejemplo, es curvilínea.")
    sc.wait(0.3)


def posicion(mv):
    sc = scn(mv, "posicion", bg="grid", lead=0.4)
    F.title(sc, "LA POSICIÓN", at=0.3)
    O = (320.0, 760.0)
    S = 80.0                      # px per metre (two squares)

    def P(x, y):
        return O[0] + x * S, O[1] - y * S
    l1 = sc.say("Para decir dónde está el móvil, dibujamos unos ejes: el eje X en horizontal, el eje Y en vertical, "
                "y el origen O, donde se cortan.",
                tts="Para decir dónde está el móvil, dibujamos unos ejes: el eje equis en horizontal, el eje i griega "
                    "en vertical, y el origen, o, donde se cortan.")
    tx, ty, to = l1.at("eje X"), l1.at("eje Y"), l1.at("origen")

    def draw_axes(L, t):
        gx, gy = prog(t, tx, 0.7, "out"), prog(t, ty, 0.7, "out")
        xe, ye = O[0] + (1210 - O[0]) * gx, O[1] - (O[1] - 230) * gy
        if gx > 0.02:
            L.arrow((O[0] - 20, O[1]), (xe, O[1]), "ink", 6, head=26)
        if gy > 0.02:
            L.arrow((O[0], O[1] + 20), (O[0], ye), "ink", 6, head=26)
        a = prog(t, tx + 0.6, 0.4)
        for k in range(1, 11):
            if O[0] + k * S < xe - 20:
                L.line([(O[0] + k * S, O[1] - 8), (O[0] + k * S, O[1] + 8)], "ink", 3)
                L.stamp(F.formula(r"\t{%d}" % k, 26, "ink"), O[0] + k * S, O[1] + 26, alpha=a)
        a = prog(t, ty + 0.6, 0.4)
        for k in range(1, 7):
            if O[1] - k * S > ye + 20:
                L.line([(O[0] - 8, O[1] - k * S), (O[0] + 8, O[1] - k * S)], "ink", 3)
                L.stamp(F.formula(r"\t{%d}" % k, 26, "ink"), O[0] - 26, O[1] - k * S, alpha=a)
        L.stamp(F.formula("X", 44), 1205, O[1] + 36, alpha=prog(t, tx + 0.5, 0.3))
        L.stamp(F.formula("Y", 44), O[0] - 40, 242, alpha=prog(t, ty + 0.5, 0.3))
        L.stamp(F.formula("O", 40), O[0] - 30, O[1] + 30, alpha=prog(t, to, 0.3))
        L.stamp(F.formula(r"\t{(m)}", 26), 1230, O[1] - 30, alpha=a)
    mg(sc, draw_axes, at=tx - 0.1, z=2)
    l2 = sc.say("Este es nuestro móvil. ¿Dónde está?")
    Px, Py = P(4, 3)
    e_dot = put(sc, F.dot_piece(18), Px, Py, l2.at("móvil"), enter="pop", rot=0, z=6)
    l3 = sc.say("Su posición es una flecha que va desde el origen hasta el móvil: el {pos:vector posición}, "
                "erre.")
    t_r = l3.at("flecha")
    state = {}

    def mover(t):
        """position of the moving point (metres); it only moves at the end of the scene"""
        u = prog(t, state.get("t_move", 1e9), 5.0, "io")
        return 4 + 5 * u, 3 + 2.2 * math.sin(math.pi * u * 0.9) + 0.6 * u

    def draw_r(L, t):
        g = prog(t, t_r, 0.7, "out")
        x, y = mover(t)
        tip = P(x * g, y * g) if g < 1 else P(x, y)
        L.arrow(O, tip, "pos", 9, head=34)
        if g > 0.9:
            F.vlabel(L, O, tip, r"\c{pos}{\vec{r}}", 54, side=1, off=40, plate=True)
    mg(sc, draw_r, at=t_r, z=5)
    l4 = sc.say("El móvil está 4 metros a la derecha del origen, y 3 metros por encima.",
                tts="El móvil está cuatro metros a la derecha del origen, y tres metros por encima.")
    t_p = l4.at("derecha", after=-0.4)
    t_q = l4.at("encima", after=-0.4)
    state["t_proj_end"] = None

    def proj(L, t):
        if t >= state.get("t_move", 1e9):
            return
        gx, gy = prog(t, t_p, 0.6, "out"), prog(t, t_q, 0.6, "out")
        L.line([(Px, Py), (Px, Py + (O[1] - Py) * gx)], "ink", 3, dash=[9, 8])
        L.line([(O[0], O[1]), (O[0] + (Px - O[0]) * gx, O[1])], "pos_l", 14, alpha=0.75)
        L.stamp(F.tag_img(r"x = 4\,\t{m}", 36, "pos_d"), (O[0] + Px) / 2, O[1] + 66, alpha=gx)
        L.line([(Px, Py), (Px + (O[0] - Px) * gy, Py)], "ink", 3, dash=[9, 8])
        L.line([(O[0], O[1]), (O[0], O[1] + (Py - O[1]) * gy)], "pos_l", 14, alpha=0.75)
        L.stamp(F.tag_img(r"y = 3\,\t{m}", 36, "pos_d"), O[0] - 130, (O[1] + Py) / 2, alpha=gy)
    mg(sc, proj, at=t_p, z=3)
    l5 = sc.say("Para escribirlo, usamos dos flechas de un metro: el vector i, en la dirección del eje X, y el vector "
                "jota, en la dirección del eje Y.",
                tts="Para escribirlo, usamos dos flechas de un metro: el vector i, en la dirección del eje equis, y el "
                    "vector jota, en la dirección del eje i griega.")
    t_i, t_j = l5.at("vector i"), l5.at("jota")
    l6 = sc.say("Cuatro pasos de i y tres pasos de jota nos llevan hasta el móvil.")
    t_si, t_sj = l6.at("Cuatro"), l6.at("tres")

    def units(L, t):
        if t >= state.get("t_move", 1e9):
            return
        a_i, a_j = prog(t, t_i, 0.4, "out"), prog(t, t_j, 0.4, "out")
        # the basic unit vectors at the origin (until the steps start)
        if t < t_si:
            L.arrow(O, (O[0] + S * a_i, O[1]), "brown", 7, head=24)
            L.arrow(O, (O[0], O[1] - S * a_j), "grey", 7, head=24)
            if a_i > 0.9:
                L.stamp(F.tag_img(r"\vec{ı}", 40, "brown"), O[0] + S / 2, O[1] + 50)
            if a_j > 0.9:
                L.stamp(F.tag_img(r"\vec{ȷ}", 40, "grey"), O[0] - 50, O[1] - S / 2)
            return
        for k in range(4):
            g = prog(t, t_si + 0.32 * k, 0.28, "out")
            if g > 0:
                a, b = P(k, 0), P(k + g, 0)
                L.arrow((a[0] + 3, a[1] - 22), (b[0] - 3, b[1] - 22), "brown", 7, head=22)
                L.stamp(F.formula(r"\vec{ı}", 30, "brown"), (a[0] + b[0]) / 2, a[1] - 52, alpha=g)
        for k in range(3):
            g = prog(t, t_sj + 0.32 * k, 0.28, "out")
            if g > 0:
                a, b = P(4, k), P(4, k + g)
                L.arrow((a[0] + 24, a[1] - 3), (b[0] + 24, b[1] + 3), "grey", 7, head=22)
                L.stamp(F.formula(r"\vec{ȷ}", 30, "grey"), a[0] + 52, (a[1] + b[1]) / 2, alpha=g)
    mg(sc, units, at=t_i, z=4)
    l7 = sc.say("Por eso escribimos: erre igual a cuatro i más tres jota, en metros. Y en general: erre igual a equis "
                "por i, más i griega por jota.")
    f1 = F.fcard(r"\c{pos}{\vec{r}} = 4\,\c{brown}{\vec{ı}} + 3\,\c{grey}{\vec{ȷ}}\;\t{(m)}", size=60,
                 border=("pos", 4))
    e_f1 = put(sc, f1, 1560, 400, l7.at("erre"), rot=-1)
    f2 = F.def_card("VECTOR POSICIÓN", [r"\c{pos}{\vec{r}} = x\,\c{brown}{\vec{ı}} + y\,\c{grey}{\vec{ȷ}}"], size=64,
                    border=("pos", 4))
    e_f2 = put(sc, f2, 1560, 620, l7.at("general"), rot=1)
    # --- visual check: Pythagoras and a ruler on the squares
    l8 = sc.say("Comprueba: ¿cuánto mide la flecha del vector posición?")
    q = F.tabbed(F.say_card("¿Cuánto mide {pos:r}?", size=44, border=("mustard", 4)), "COMPRUEBA",
                 head_bg="mustard", head_color="ink")
    e_q = put(sc, q, 1480, 820, l8.start(), rot=-1)
    sc.jingle(l8.start(), "fis_quiz", gain=0.3)
    t_ans = F.think(sc, 3.5, x=1480 + q.vw / 2 + 72, y=820, r=50)
    l9 = sc.say("La flecha es la hipotenusa de un triángulo rectángulo de catetos 4 y 3. Por Pitágoras, raíz de 16 "
                "más 9: 5 metros.",
                tts="La flecha es la hipotenusa de un triángulo rectángulo de catetos cuatro y tres. Por Pitágoras, "
                    "raíz de dieciséis más nueve: cinco metros.")
    f3 = F.fcard(r"|\c{pos}{\vec{r}}| = \sqrt{4^2 + 3^2} = 5\,\t{m}", size=56, border=("mustard", 4))
    e_f3 = put(sc, f3, 1560, 820, l9.at("Pitágoras"), rot=0.6, z=7)
    e_q.leave(l9.at("Pitágoras"), "fall", 0.4)

    def tri(L, t):
        if t >= state.get("t_move", 1e9):
            return
        g = prog(t, t_ans, 0.5, "out")
        L.poly([O, P(4, 0), P(4, 3)], fill=(238, 180, 30, 70), alpha=g)
        a = prog(t, l9.at("Pitágoras"), 0.4)
        L.stamp(F.tag_img(r"\t{5 m}", 38, "pos_d", border=("pos", 3)), *P(2.75, 1.1), alpha=a)
    mg(sc, tri, at=t_ans, z=3)
    l10 = sc.say("Y con una regla sobre la cuadrícula: exactamente 5 metros. ¡Cuadra!",
                 tts="Y con una regla sobre la cuadrícula: exactamente cinco metros. ¡Cuadra!")
    rl = F.ruler_piece(5.6 * S, ppu=S, units=5, edge="bottom")
    ang = math.degrees(math.atan2(3, 4))
    ux, uy = 0.8, -0.6
    nx, ny = -0.6, -0.8
    off = rl.vh / 2 + 6
    cx = O[0] + ux * (rl.vw / 2 - 30) + nx * off
    cy = O[1] + uy * (rl.vw / 2 - 30) + ny * off
    e_rl = put(sc, rl, cx, cy, l10.at("regla"), rot=ang, z=7)
    l11 = sc.say("Y si el móvil se mueve, el vector posición lo sigue, y sus coordenadas van cambiando.")
    t_mv = l11.at("se mueve", after=-0.2)
    state["t_move"] = t_mv
    for e in (e_rl, e_f3, e_f1):
        e.leave(t_mv - 0.2, "fall", 0.45)
    e_dot.leave(t_mv, "cut")
    dot = F.dot_piece(18)
    live(sc, lambda t: (dot, *P(*mover(t)), 0.0), at=t_mv, z=6, jitter=0.3)
    trail = F.Path([P(*mover(t_mv + 5.0 * k / 60)) for k in range(61)])

    def trail_live(L, t):
        g = prog(t, t_mv, 5.0, "io")
        pts = [P(*mover(t_mv + 5.0 * k / 60)) for k in range(61)]
        u = g
        L.line(F.Path(pts).upto(u), "path", 5, dash=[14, 10])
        x, y = mover(t)
        L.line([P(x, y), P(x, 0)], "ink", 2.5, dash=[8, 8], alpha=0.8)
        L.line([P(x, y), P(0, y)], "ink", 2.5, dash=[8, 8], alpha=0.8)
        L.stamp(F.tag_img(r"\c{pos}{\vec{r}} = %s\,\c{brown}{\vec{ı}} + %s\,\c{grey}{\vec{ȷ}}\;\t{(m)}" %
                          (F.num(x), F.num(y)), 50, "ink", border=("pos", 3), pad=(18, 8)), 1560, 400)
    mg(sc, trail_live, at=t_mv, z=4)
    sc.wait(2.6)


# ============================================================================
# 3. ida y vuelta: espacio recorrido y desplazamiento
# ============================================================================
def ida_vuelta(mv):
    sc = scn(mv, "idavuelta", bg="sky", lead=0.4, transition="wipe")
    GROUND = 690.0
    X0, X1 = 230.0, 1690.0           # house door (x = 0 m) and bakery door (x = 300 m)
    PPM = (X1 - X0) / 300.0
    hs = F.house_piece()
    shop = F.shop_piece()
    kiosk = F.shop_piece("QUIOSCO", "newspaper", "pos", 201, 240)
    put(sc, hs, X0 - 20, GROUND - hs.vh / 2 + 2, 0.2, rot=0, z=0)
    put(sc, shop, X1 + 40, GROUND - shop.vh / 2 + 2, 0.35, rot=0, z=0)
    put(sc, kiosk, X0 + 100 * PPM, GROUND - kiosk.vh / 2 + 2, 0.5, rot=0, z=0)
    for x, sp in ((620, F.tree_top(54, 281)), (1150, F.tree_top(64, 282))):
        pass

    def street(L, t):
        L.poly([(-20, GROUND), (W + 20, GROUND), (W + 20, H + 20), (-20, H + 20)], fill="concrete")
        L.line([(-20, GROUND + 4), (W + 20, GROUND + 4)], "concrete_d", 8)
    mg(sc, street, at=0.0, z=-1, shadow=False)

    l1 = sc.say("Ana ya está en casa. Al día siguiente, va andando a la panadería, que está a 300 metros, y vuelve.",
                tts="Ana ya está en casa. Al día siguiente, va andando a la panadería, que está a trescientos metros, y "
                    "vuelve.")
    l2 = sc.say("Mientras camina, vamos a medir dos cosas.")
    l3 = sc.say("La primera: cuántos metros lleva recorridos en total. Es el {space:espacio recorrido}, ese.")
    l4 = sc.say("La segunda: una flecha que va desde donde salió hasta donde está ahora. Es el {disp:desplazamiento}.")
    l5 = sc.say("En la panadería, los dos valen 300 metros.",
                tts="En la panadería, los dos valen trescientos metros.")
    l6 = sc.say("Pero a la vuelta, el espacio recorrido sigue sumando metros, mientras que la flecha del desplazamiento "
                "se encoge.")
    l7 = sc.say("De vuelta en casa: ha recorrido 600 metros, pero su desplazamiento es cero, porque ha terminado en el "
                "mismo sitio del que salió.",
                tts="De vuelta en casa: ha recorrido seiscientos metros, pero su desplazamiento es cero, porque ha "
                    "terminado en el mismo sitio del que salió.")
    sc.wait(0.6)
    t_go = l3.start(0.2)
    T1 = max(6.0, l5.start() - t_go - 0.3)
    t_back = l6.start(0.1)
    T2 = max(6.0, l7.start() - t_back - 0.2)

    def walk_x(t):
        """Ana's x on screen and the distance walked (px) and direction"""
        if t < t_go:
            return X0, 0.0, 1
        if t < t_go + T1:
            u = F.movie.EASES["io"]((t - t_go) / T1)
            return X0 + (X1 - X0) * u, (X1 - X0) * u, 1
        if t < t_back:
            return X1, X1 - X0, 1
        if t < t_back + T2:
            u = F.movie.EASES["io"]((t - t_back) / T2)
            return X1 - (X1 - X0) * u, (X1 - X0) * (1 + u), -1
        return X0, 2 * (X1 - X0), -1

    def ana(t):
        x, d, face = walk_x(t)
        moving = (t_go < t < t_go + T1) or (t_back < t < t_back + T2)
        pose = int(d / 26) % 4 if moving else 1
        spr = F.ana_walk(pose, face)
        return spr, x, GROUND - spr.vh / 2 + 6, 0.0
    live(sc, ana, at=0.4, z=4, jitter=0.6)

    def meters(L, t):
        x, d, face = walk_x(t)
        # axis along the kerb
        L.arrow((X0 - 60, GROUND + 70), (X1 + 140, GROUND + 70), "ink", 5, head=22)
        for k in range(0, 301, 50):
            xx = X0 + k * PPM
            L.line([(xx, GROUND + 62), (xx, GROUND + 78)], "ink", 3)
            L.stamp(F.formula(r"\t{%d}" % k, 26), xx, GROUND + 98)
        L.stamp(F.formula(r"\t{x (m)}", 28), X1 + 150, GROUND + 98)
        # distance walked: a mustard ribbon (going) and a second one (coming back)
        a = prog(t, l3.at("espacio"), 0.4)
        if a > 0:
            go = min(d, X1 - X0)
            L.line([(X0, GROUND + 140), (X0 + go, GROUND + 140)], "space", 16, alpha=a, cap="butt")
            if d > X1 - X0:
                L.line([(X1, GROUND + 166), (X1 - (d - (X1 - X0)), GROUND + 166)], "space", 16, alpha=a, cap="butt")
            L.stamp(F.tag_img(r"\c{space}{s} = %d\,\t{m}" % round(d / PPM), 48, "ink", border=("space", 4),
                              pad=(16, 6)), 520, 240, alpha=a)
        # displacement: from the start to where she is now
        b = prog(t, l4.at("flecha"), 0.4)
        if b > 0:
            dx = x - X0
            L.arrow((X0, 352), (X0 + dx, 352), "disp", 11, head=34, min_head=2)
            L.line([(X0, 330), (X0, 374)], "disp_d", 4, alpha=b)
            val = round(dx / PPM)
            L.stamp(F.tag_img(r"|\c{disp}{Δ\vec{r}}| = %d\,\t{m}" % val, 48, "ink", border=("disp", 4),
                              pad=(16, 6)), 1400, 240, alpha=b)
    mg(sc, meters, at=0.3, z=3)
    put(sc, F.fcard(r"\c{space}{s} = 600\,\t{m}\quad |\c{disp}{Δ\vec{r}}| = 0", size=62, border=("ink", 4)),
        W / 2 + 60, 470, l7.at("cero"), enter="pop", z=8, rot=-1)
    sc.wait(0.2)


def desplazamiento(mv):
    sc = scn(mv, "desplazamiento", bg="grid", lead=0.4)
    F.title(sc, "DOS COSAS DISTINTAS", at=0.3)
    l1 = sc.say("El {space:espacio recorrido} es la longitud total del camino. Es solo un número, y se mide en "
                "metros.")
    d1 = F.def_card("ESPACIO RECORRIDO  s", [r"\t{Longitud total del camino.}", r"\t{Un número (escalar), en metros.}"],
                    head_bg="space", head_color="ink", size=40, border=("space", 4))
    put(sc, d1, 520, 330, l1.start(), rot=-1)
    l2 = sc.say("El {disp:desplazamiento} solo depende de dónde empieza y dónde acaba el movimiento: es un vector que "
                "va de la posición inicial a la final.")
    d2 = F.def_card("DESPLAZAMIENTO  Δr", [r"\t{Vector de la posición inicial}", r"\t{a la final. No mira el camino.}"],
                    head_bg="disp", size=40, border=("disp", 4))
    put(sc, d2, 520, 580, l2.start(), rot=1)
    O = (1000.0, 820.0)
    S = 40.0

    def P(x, y):
        return O[0] + x * S, O[1] - y * S
    r0, rf = (3.0, 9.0), (18.0, 4.0)
    l3 = sc.say("Con los vectores posición se ve muy claro. Este es erre cero, la posición inicial; y este, erre "
                "final.")
    t_a, t0, t1 = l3.start(), l3.at("cero"), l3.at("final")
    l4 = sc.say("El desplazamiento es la flecha que une sus puntas: lo que hay que sumar a erre cero para llegar a "
                "erre final.")
    t_d = l4.at("flecha")
    path = F.Path(F.smooth([P(*r0), P(7, 13), P(11, 6), P(15, 9), P(*rf)], 12))

    def vecs(L, t):
        g = prog(t, t_a, 0.6, "out")
        L.arrow((O[0] - 30, O[1]), (O[0] + (21 * S) * g, O[1]), "ink", 5, head=22)
        L.arrow((O[0], O[1] + 30), (O[0], O[1] - (14 * S) * g), "ink", 5, head=22)
        L.stamp(F.formula("O", 36), O[0] - 26, O[1] + 26, alpha=g)
        L.line(path.pts, "path", 4, dash=[12, 10], alpha=0.8 * g)
        a = prog(t, t0, 0.6, "out")
        if a > 0:
            L.arrow(O, lerp2(O, P(*r0), a), "pos", 8, head=30)
            F.vlabel(L, O, P(*r0), r"\c{pos}{\vec{r}_0}", 44, side=1, off=36)
        b = prog(t, t1, 0.6, "out")
        if b > 0:
            L.arrow(O, lerp2(O, P(*rf), b), "pos", 8, head=30)
            F.vlabel(L, O, P(*rf), r"\c{pos}{\vec{r}_f}", 44, side=-1, off=36)
        c = prog(t, t_d, 0.7, "out")
        if c > 0:
            L.arrow(P(*r0), lerp2(P(*r0), P(*rf), c), "disp", 10, head=34)
            F.vlabel(L, P(*r0), P(*rf), r"\c{disp}{Δ\vec{r}}", 46, side=1, off=40)
        # a little traveller: along r0 and then along Δr, it reaches the tip of rf
        k = prog(t, l4.at("sumar"), 2.2, "io")
        if 0 < k < 1:
            q = lerp2(O, P(*r0), min(1, k * 2)) if k < 0.5 else lerp2(P(*r0), P(*rf), (k - 0.5) * 2)
            L.circle(*q, 13, fill="cream", stroke="ink", width=4)
    mg(sc, vecs, at=t_a, z=4)
    l5 = sc.say("Por eso se calcula restando: delta erre es igual a erre final menos erre cero.")
    f = F.fcard(r"\c{disp}{Δ\vec{r}} = \c{pos}{\vec{r}_f} − \c{pos}{\vec{r}_0}", size=68, border=("disp", 5))
    put(sc, f, 520, 820, l5.at("delta"), rot=-0.8, z=6)
    sc.wait(0.5)


def check_ida(mv):
    sc = scn(mv, "check-ida", bg="grid", lead=0.3)
    l1 = sc.say("Comprueba: Ana va a la panadería, a 300 metros, pero a la vuelta se queda en el quiosco, a 100 metros "
                "de casa. ¿Cuánto vale el espacio recorrido? ¿Y el desplazamiento?",
                tts="Comprueba: Ana va a la panadería, a trescientos metros, pero a la vuelta se queda en el quiosco, a "
                    "cien metros de casa. ¿Cuánto vale el espacio recorrido? ¿Y el desplazamiento?")
    e_q, _ = F.quiz(sc, "Ida: 300 m. Vuelta: se queda a 100 m de casa.\n¿{space:s}? ¿{disp:Δr}?", lead=l1.start(),
                    y=230)
    X0, X1 = 360.0, 1560.0
    PPM = (X1 - X0) / 300.0
    Y = 560.0

    def diagram(L, t):
        L.arrow((X0 - 40, Y), (X1 + 80, Y), "ink", 5, head=22)
        for k, lab in ((0, r"\t{casa}"), (100, r"\t{quiosco}"), (300, r"\t{panadería}")):
            xx = X0 + k * PPM
            L.line([(xx, Y - 12), (xx, Y + 12)], "ink", 4)
            L.stamp(F.formula(r"\t{%d m}" % k, 28), xx, Y + 34)
            L.stamp(F.formula(lab, 30, "ink"), xx, Y - 36)
        g = prog(t, t_rev, 1.2, "io")
        h = prog(t, t_rev + 1.2, 0.9, "io")
        if g > 0:
            L.arrow((X0, Y + 90), (X0 + (X1 - X0) * g, Y + 90), "space", 14, head=34)
            L.stamp(F.tag_img(r"\t{300 m}", 34, "ink"), (X0 + X1) / 2, Y + 128, alpha=g)
        if h > 0:
            L.arrow((X1, Y + 170), (X1 - 200 * PPM * h, Y + 170), "space", 14, head=34)
            L.stamp(F.tag_img(r"\t{200 m}", 34, "ink"), X1 - 100 * PPM, Y + 208, alpha=h)
        c = prog(t, l2.at("Desplazamiento"), 0.7, "out")
        if c > 0:
            L.arrow((X0, Y - 110), (X0 + 100 * PPM * c, Y - 110), "disp", 12, head=34)
    t_rev = F.think(sc, 4.5)
    mg(sc, diagram, at=l1.start(0.5), z=4)
    l2 = sc.say("Espacio recorrido: 300 metros de ida y 200 de vuelta, 500 metros. Desplazamiento: 100 metros, hacia "
                "la panadería.",
                tts="Espacio recorrido: trescientos metros de ida y doscientos de vuelta, quinientos metros. "
                    "Desplazamiento: cien metros, hacia la panadería.")
    e_q.leave(t_rev, "fall", 0.5)
    fs = F.fcard(r"\c{space}{s} = 300 + 200 = 500\,\t{m}", size=50, border=("space", 4))
    put(sc, fs, 440, 250, l2.at("500"), rot=1, z=6)
    put(sc, F.check_mark(90), 440 + fs.vw / 2 + 50, 250, l2.at("500"), enter="pop", z=7)
    fd = F.fcard(r"|\c{disp}{Δ\vec{r}}| = 100\,\t{m}\t{ (hacia la panadería)}", size=50, border=("disp", 4))
    put(sc, fd, 1380, 250, l2.at("100 metros, hacia"), rot=-1, z=6)
    put(sc, F.check_mark(90), 1380 + fd.vw / 2 + 40, 250, l2.at("panadería"), enter="pop", z=7)
    sc.wait(0.3)

    sc = scn(mv, "coinciden", bg="grid", lead=0.3)
    F.title(sc, "¿CUÁNDO COINCIDEN?", at=0.3)
    l3 = sc.say("Así que el espacio recorrido y el desplazamiento solo coinciden cuando el móvil va en línea recta y "
                "sin dar la vuelta. Si hay curvas o vueltas atrás, el espacio recorrido es mayor.")
    cases = [(380, "recta, sin volver", r"s = |Δ\vec{r}|", "recta"),
             (960, "con curvas", r"s > |Δ\vec{r}|", "curvas"),
             (1540, "ida y vuelta", r"s > |Δ\vec{r}|", "vueltas")]
    for x, lab, rel, key in cases:
        tt = l3.at(key, after=-0.3)
        put(sc, card(lab, size=40, font_name="body9", bg="cream", pad=(24, 10), seed=F._seed(lab)), x, 300, tt,
            enter="pop")

        def mini(L, t, x=x, key=key, tt=tt, rel=rel):
            g = prog(t, tt, 1.4, "io")
            a, b = (x - 220, 560), (x + 220, 560)
            end = b
            if key == "recta":
                L.line([a, lerp2(a, b, g)], "space", 22, cap="butt")
            elif key == "curvas":
                pth = F.Path(F.smooth([a, (x - 120, 440), (x, 620), (x + 120, 450), b], 10))
                L.line(pth.upto(g), "space", 18, cap="butt")
            else:
                c = (x + 180, 560)
                end = (x - 40, 560)
                L.line([a, lerp2(a, c, min(1, g * 1.6))], "space", 18, cap="butt")
                if g > 0.62:
                    L.line([(c[0], 600), lerp2((c[0], 600), (x - 40, 600), (g - 0.62) / 0.38)], "space", 18,
                           cap="butt")
                    L.arc(c[0], 580, 20, -90, 90, "space", 6)
                if g >= 1:
                    L.line([(x - 40, 600), (x - 40, 560)], "ink", 3, dash=[6, 6])
            L.arrow(a, lerp2(a, end, prog(t, tt + 1.4, 0.5, "out")), "disp", 8, head=28)
            L.stamp(F.tag_img(rel, 44, "ink", border=("ink", 3), pad=(14, 6)), x, 720,
                    alpha=prog(t, tt + 1.6, 0.4))
        mg(sc, mini, at=tt, z=4)
    sc.wait(1.2)


# ============================================================================
# 4. velocidad media e instantánea
# ============================================================================
# the same arch-shaped trajectory for both scenes: r(t) = (5t, 2 + 6(t-1) - 1.5(t-1)^2) m
ARCH_O = (120.0, 740.0)   # screen point of (0 m, 0 m)
ARCH_S = 40.0             # 1 m = 1 square
V_S = 40.0                # 1 m/s = 40 px for velocity arrows


def arch_r(t):
    return 5.0 * t, 2.0 + 6.0 * (t - 1) - 1.5 * (t - 1) ** 2


def arch_v(t):
    return 5.0, 6.0 - 3.0 * (t - 1)


def arch_P(t):
    x, y = arch_r(t)
    return ARCH_O[0] + x * ARCH_S, ARCH_O[1] - y * ARCH_S


ARCH_T0, ARCH_T1 = 0.8, 5.2
ARCH_PATH = F.Path([arch_P(ARCH_T0 + (ARCH_T1 - ARCH_T0) * k / 120) for k in range(121)])


def _arch_base(L, t, alpha=1.0):
    L.line(ARCH_PATH.pts, "path", 5, dash=[14, 10], alpha=alpha)


def velocidad_media(mv):
    sc = scn(mv, "vmedia", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "LA VELOCIDAD MEDIA", at=0.3)
    sw, off = F.stopwatch_piece(250)
    SWX, SWY = 1600, 360
    l1 = sc.say("Ahora añadimos un reloj, porque el movimiento también es cuestión de tiempo.")
    put(sc, sw, SWX, SWY, l1.at("reloj"), enter="pop", rot=0, z=3)
    l2 = sc.say("El móvil pasa por el punto uno cuando el reloj marca 1 segundo, y por el punto dos a los 5 segundos.",
                tts="El móvil pasa por el punto uno cuando el reloj marca un segundo, y por el punto dos a los cinco "
                    "segundos.")
    # the motion runs in real time, so the stopwatch shows the real seconds of the trip
    t_run = l2.start() - 0.3

    def clock_t(t):
        return min(max(0.0, t - t_run + ARCH_T0), 5.0)

    def sw_hand(L, t):
        F.stopwatch_hand(L, SWX + off[0], SWY + off[1], 250, clock_t(t))
        L.stamp(F.tag_img(r"t = %s\,\t{s}" % F.num(clock_t(t)), 46, "ink", border=("ink", 3), pad=(16, 6)), SWX,
                SWY + 190)
    mg(sc, sw_hand, at=l1.at("reloj") + 0.3, z=5)
    dot = F.dot_piece(18)
    live(sc, lambda t: (dot, *arch_P(clock_t(t)), 0.0), at=t_run, z=6, jitter=0.3)
    P1, P2 = arch_P(1.0), arch_P(5.0)

    def marks(L, t):
        ct = clock_t(t)
        L.line(ARCH_PATH.upto((ct - ARCH_T0) / (ARCH_T1 - ARCH_T0)), "path", 5, dash=[14, 10])
        for tk, P_, lab in ((1.0, P1, "1"), (5.0, P2, "2")):
            if ct >= tk:
                L.circle(*P_, 12, fill="ink")
                L.stamp(F.tag_img(r"\b{%s}\;\; t_%s = %d\,\t{s}" % (lab, lab, tk), 38, "ink", pad=(12, 4)), P_[0],
                        P_[1] + 52)
    mg(sc, marks, at=t_run, z=4)
    l3 = sc.say("En esos 4 segundos, su desplazamiento es esta flecha: 20 metros. Puedes contarlos: 20 cuadros de la "
                "cuadrícula.",
                tts="En esos cuatro segundos, su desplazamiento es esta flecha: veinte metros. Puedes contarlos: veinte "
                    "cuadros de la cuadrícula.")
    t_dr = l3.at("flecha")
    t_count = l3.at("contarlos")

    def chord(L, t):
        g = prog(t, t_dr, 0.7, "out")
        L.arrow(P1, lerp2(P1, P2, g), "disp", 10, head=34)
        if g > 0.9:
            L.stamp(F.tag_img(r"\c{disp}{Δ\vec{r}}\t{: 20 m}", 42, "ink", border=("disp", 3), pad=(12, 4)),
                    (P1[0] + P2[0]) / 2, P1[1] + 52)
        n = int(min(20, max(0, (t - t_count) / 0.11)))
        for k in range(1, n + 1):
            x = P1[0] + k * ARCH_S
            L.line([(x, P1[1] - 12), (x, P1[1] + 12)], "disp_d", 3)
            if k % 5 == 0:
                L.stamp(F.formula(r"\t{%d}" % k, 26, "disp_d"), x, P1[1] - 30)
    mg(sc, chord, at=t_dr, z=5)
    l4 = sc.say("La velocidad media compara ese desplazamiento con el tiempo empleado: 20 metros en 4 segundos son 5 "
                "metros por cada segundo.",
                tts="La velocidad media compara ese desplazamiento con el tiempo empleado: veinte metros en cuatro "
                    "segundos son cinco metros por cada segundo.")
    t_split = l4.at("son 5")

    def split(L, t):
        for k in range(4):
            g = prog(t, t_split + 0.35 * k, 0.3, "out")
            if g <= 0:
                continue
            a = (P1[0] + 5 * k * ARCH_S, P1[1] - 70)
            b = (P1[0] + 5 * (k + 1) * ARCH_S, P1[1] - 70)
            L.line([a, lerp2(a, b, g)], "vel_l", 12, cap="butt")
            L.line([(a[0], a[1] - 12), (a[0], a[1] + 12)], "vel_d", 3)
            L.stamp(F.formula(r"\t{5 m en 1 s}", 26, "vel_d"), (a[0] + b[0]) / 2, a[1] - 26, alpha=g)
    mg(sc, split, at=t_split, z=5)
    put(sc, F.fcard(r"v_m = \frac{20\,\t{m}}{4\,\t{s}} = 5\,\t{m/s}", size=50, border=("vel", 3)), 640, 290,
        l4.at("20 metros en"), rot=1, z=7)
    l5 = sc.say("Es decir, la {vel:velocidad media} es el desplazamiento dividido entre el intervalo de tiempo. Se "
                "mide en metros por segundo.")
    fm = F.def_card("VELOCIDAD MEDIA", [r"\c{vel}{\vec{v}_m} = \frac{\c{disp}{Δ\vec{r}}}{Δt}"], head_bg="vel", size=60,
                    border=("vel", 4))
    put(sc, fm, 1560, 700, l5.at("velocidad media"), rot=-0.8, z=7)
    l6 = sc.say("Y como el desplazamiento es un vector, la velocidad media también: tiene su misma dirección y su "
                "mismo sentido.")
    t_vm = l6.at("también")

    def vm(L, t):
        g = prog(t, t_vm, 0.6, "out")
        tip = (P1[0] + 5 * V_S * g * 1.0, P1[1] - 140)
        L.arrow((P1[0], P1[1] - 140), tip, "vel", 10, head=34)
        if g > 0.9:
            L.stamp(F.tag_img(r"\c{vel}{\vec{v}_m}\t{: 5 m/s}", 40, "ink", border=("vel", 3), pad=(12, 4)),
                    tip[0] + 120, P1[1] - 140)
    mg(sc, vm, at=t_vm, z=6)
    sc.wait(0.4)

    # --- ojo: a lap of the athletics track
    sc = scn(mv, "pista", bg="grid", lead=0.3)
    l1 = sc.say("Ojo: la velocidad media no cuenta lo que pasa entre medias. Si das una vuelta completa a una pista de "
                "400 metros en 80 segundos, acabas donde empezaste.",
                tts="Ojo: la velocidad media no cuenta lo que pasa entre medias. Si das una vuelta completa a una pista "
                    "de cuatrocientos metros en ochenta segundos, acabas donde empezaste.")
    put(sc, kit.ojo("La {red|b:velocidad media} solo mira el principio y el final.", size=40, max_w=1200), W / 2, 150,
        l1.start(), rot=-1)
    tk = F.track_piece(760, 380)
    TX, TY = 560, 560
    put(sc, tk, TX, TY, l1.at("pista"), rot=0)
    t_lap = l1.at("vuelta", after=-0.2)
    lap = []
    a_, b_ = 760 / 2 - 35, 380 / 2 - 35
    rr = b_
    for k in range(121):
        u = k / 120
        s_ = u * (2 * (760 - 380) + 2 * math.pi * rr)
        straight = 760 - 380
        if s_ < straight / 2:
            p = (TX + s_, TY + rr)
        elif s_ < straight / 2 + math.pi * rr:
            ang = (s_ - straight / 2) / rr
            p = (TX + straight / 2 + rr * math.sin(ang), TY + rr * math.cos(ang))
        elif s_ < 1.5 * straight + math.pi * rr:
            p = (TX + straight / 2 - (s_ - straight / 2 - math.pi * rr), TY - rr)
        elif s_ < 1.5 * straight + 2 * math.pi * rr:
            ang = (s_ - 1.5 * straight - math.pi * rr) / rr
            p = (TX - straight / 2 - rr * math.sin(ang), TY - rr * math.cos(ang))
        else:
            p = (TX - straight / 2 + (s_ - 1.5 * straight - 2 * math.pi * rr), TY + rr)
        lap.append(p)
    lap_path = F.Path(lap)
    runner = F.dot_piece(17, "vel")

    def run(t):
        return runner, *lap_path.at(prog(t, t_lap, 4.0, "io")), 0.0
    live(sc, run, at=t_lap, z=5, jitter=0.3)
    mg(sc, lambda L, t: L.line(lap_path.upto(prog(t, t_lap, 4.0, "io")), "space", 9), at=t_lap, z=4)
    l2 = sc.say("Tu desplazamiento es cero... y tu velocidad media, también cero.")
    put(sc, F.fcard(r"Δ\vec{r} = \vec{0}\;\;\Rightarrow\;\;\c{vel}{\vec{v}_m} = \vec{0}", size=58, border=("vel", 4)),
        1460, 420, l2.at("cero"), rot=1, z=6)
    l3 = sc.say("Lo que sí vale 5 metros por segundo es tu {space:rapidez media}: el espacio recorrido dividido entre el "
                "tiempo.",
                tts="Lo que sí vale cinco metros por segundo es tu rapidez media: el espacio recorrido dividido entre el "
                    "tiempo.")
    put(sc, F.def_card("RAPIDEZ MEDIA", [r"\frac{\c{space}{s}}{Δt} = \frac{400\,\t{m}}{80\,\t{s}} = 5\,\t{m/s}"],
                       head_bg="space", head_color="ink", size=52, border=("space", 4)), 1460, 680,
        l3.at("rapidez"), rot=-1, z=6)
    sc.wait(0.6)


def velocidad_instantanea(mv):
    sc = scn(mv, "vinst", bg="grid", lead=0.4)
    F.title(sc, "LA VELOCIDAD INSTANTÁNEA", at=0.3)
    P1 = arch_P(1.0)
    l1 = sc.say("Pero el velocímetro de un coche no marca una media: marca la velocidad en cada instante. ¿Cómo la "
                "calculamos?")
    spd, so = F.speedo_piece(260)
    SPX, SPY = 330, 300
    put(sc, spd, SPX, SPY, l1.at("velocímetro"), enter="pop", rot=0, z=3)
    put(sc, card("m/s", size=30, font_name="body9", bg="cream", pad=(14, 4), seed=301), SPX, SPY + 90,
        l1.at("velocímetro") + 0.2, enter="pop", z=4)
    l2 = sc.say("Acercamos el segundo instante al primero. Con 2 segundos, la flecha del desplazamiento es más corta, "
                "y ya no es horizontal.",
                tts="Acercamos el segundo instante al primero. Con dos segundos, la flecha del desplazamiento es más "
                    "corta, y ya no es horizontal.")
    l3 = sc.say("Con 1 segundo... con medio segundo... con una décima...",
                tts="Con un segundo... con medio segundo... con una décima...")
    steps = [(4.0, l2.start()), (2.0, l2.at("Con 2")), (1.0, l3.at("Con 1")), (0.5, l3.at("medio")),
             (0.1, l3.at("décima"))]

    def dt_at(t):
        """the interval shown at time t (smoothly sliding between the steps)"""
        cur = steps[0][0]
        for k in range(1, len(steps)):
            a, ta = steps[k - 1][0], steps[k][1]
            g = prog(t, ta - 0.1, 0.8, "io")
            cur = a + (steps[k][0] - a) * g if g < 1 else steps[k][0]
            if g < 1:
                break
        return cur

    def vm_of(dt):
        x1, y1 = arch_r(1.0)
        x2, y2 = arch_r(1.0 + dt)
        return (x2 - x1) / dt, (y2 - y1) / dt
    l4 = sc.say("La velocidad media se acerca cada vez más a un valor: 7,8 metros por segundo. Y su flecha deja de "
                "cortar la curva: acaba rozándola en un solo punto.",
                tts="La velocidad media se acerca cada vez más a un valor: siete coma ocho metros por segundo. Y su "
                    "flecha deja de cortar la curva: acaba rozándola en un solo punto.")
    t_tan = l4.at("rozándola")

    def draw(L, t):
        _arch_base(L, t)
        dt = dt_at(t)
        P2 = arch_P(1.0 + dt)
        L.circle(*P1, 12, fill="ink")
        L.stamp(F.tag_img(r"\b{1}", 34, "ink", pad=(10, 2)), P1[0] - 34, P1[1] + 28)
        L.circle(*P2, 11, fill="ink")
        L.stamp(F.tag_img(r"\b{2}", 34, "ink", pad=(10, 2)), P2[0] + 30, P2[1] + 30)
        L.arrow(P1, P2, "disp", 8, head=28, min_head=10)
        vx, vy = vm_of(dt)
        tip = (P1[0] + vx * V_S, P1[1] - vy * V_S)
        L.arrow(P1, tip, "vel", 11, head=36)
        L.stamp(F.tag_img(r"\c{vel}{\vec{v}_m}", 40, "ink", pad=(10, 2)), tip[0] + 34, tip[1] - 26)
        a = prog(t, t_tan, 0.6)
        if a > 0:
            vx, vy = arch_v(1.0)
            n = math.hypot(vx, vy)
            ux, uy = vx / n, -vy / n
            L.line([(P1[0] - ux * 260, P1[1] - uy * 260), (P1[0] + ux * 520 * a, P1[1] + uy * 520 * a)], "ink", 3,
                   dash=[10, 8], alpha=0.9)
            L.stamp(F.tag_img(r"\t{tangente}", 32, "ink"), P1[0] + ux * 560, P1[1] + uy * 560 - 20, alpha=a)
        # table of values
        x0, y0 = 1290, 250
        L.stamp(F.formula(r"Δt\;\t{(s)}", 34), x0, y0, "lm")
        L.stamp(F.formula(r"\c{vel}{v_m}\;\t{(m/s)}", 34), x0 + 230, y0, "lm")
        L.line([(x0 - 10, y0 + 26), (x0 + 470, y0 + 26)], "ink", 3)
        for k, (d_, ts) in enumerate(steps):
            if t < ts - 0.05:
                break
            vx, vy = vm_of(d_)
            yy = y0 + 62 + k * 48
            L.stamp(F.formula(r"\t{%s}" % F.num(d_, 1), 34), x0 + 40, yy, "lm")
            L.stamp(F.formula(r"\t{%s}" % F.num(math.hypot(vx, vy), 2), 34, "vel_d"), x0 + 270, yy, "lm")
        if t >= l4.at("7,8") - 0.1:
            yy = y0 + 62 + len(steps) * 48
            L.stamp(F.formula(r"\t{→ 0}", 34, "ink"), x0 + 40, yy, "lm")
            L.stamp(F.formula(r"\t{→ 7,81}", 34, "vel"), x0 + 270, yy, "lm")

    def needle(L, t, so=so):
        dt = dt_at(t)
        vx, vy = vm_of(dt)
        F.speedo_needle(L, SPX + so[0], SPY + so[1], 260, math.hypot(vx, vy))
    mg(sc, draw, at=l2.start(), z=4)
    mg(sc, needle, at=l1.at("velocímetro") + 0.3, z=5)
    l5 = sc.say("Esa es la {vel:velocidad instantánea}: la velocidad media en un intervalo de tiempo tan pequeño como "
                "queramos. Se escribe así: el límite cuando delta te tiende a cero, o de erre entre de te.")
    fi = F.def_card("VELOCIDAD INSTANTÁNEA", [r"\c{vel}{\vec{v}} = \lim{Δt\to0}\frac{Δ\vec{r}}{Δt} = "
                                              r"\frac{d\vec{r}}{dt}"], head_bg="vel", size=58, border=("vel", 4))
    put(sc, fi, 1500, 770, l5.at("Se escribe"), rot=-0.6, z=7)
    sc.wait(0.3)

    sc = scn(mv, "tangente", bg="grid", lead=0.3)
    l6 = sc.say("Y como su flecha acaba pegada a la curva, la velocidad instantánea es siempre {vel:tangente} a la "
                "trayectoria.")
    put(sc, F.say_card("{vel:v} siempre es {vel:tangente} a la trayectoria", size=48, border=("vel", 4)), W / 2,
        150, l6.at("tangente"))

    def tang(L, t):
        _arch_base(L, t)
        for k, tk in enumerate((1.0, 2.0, 3.0, 4.0, 5.0)):
            g = prog(t, l6.start(0.3) + 0.45 * k, 0.4, "out")
            if g <= 0:
                continue
            P_ = arch_P(tk)
            vx, vy = arch_v(tk)
            L.circle(*P_, 10, fill="ink")
            L.arrow(P_, (P_[0] + vx * V_S * g, P_[1] - vy * V_S * g), "vel", 9, head=30)
    mg(sc, tang, at=0.2, z=4)
    l7 = sc.say("Su módulo es la {vel:rapidez} en ese instante: justo lo que marca el velocímetro.")
    spd, so = F.speedo_piece(260)
    put(sc, spd, 1620, 380, l7.at("velocímetro"), enter="pop", rot=0, z=3)
    mg(sc, lambda L, t: F.speedo_needle(L, 1620 + so[0], 380 + so[1], 260, 7.81 * prog(t, l7.at("velocímetro") + 0.3,
                                                                                       0.8, "out")),
       at=l7.at("velocímetro") + 0.3, z=5)
    put(sc, F.fcard(r"|\c{vel}{\vec{v}}| = 7,8\,\t{m/s}", size=46, border=("vel", 3)), 1620, 540,
        l7.at("velocímetro") + 0.6, enter="pop", z=6)
    sc.wait(0.4)


def honda(mv):
    sc = scn(mv, "honda", bg="grid", lead=0.3)
    C = (560.0, 610.0)
    R = 230.0
    omega = 2.4                      # rad/s; the angle grows with time = clockwise on screen
    A_REL = math.radians(-90)        # release point: the top of the circle
    top = (C[0], C[1] - R)
    l1 = sc.say("Compruébalo con una honda. La piedra gira atada a una cuerda. Si la soltamos justo aquí, ¿por dónde "
                "saldrá: por la A, por la B o por la C?",
                tts="Compruébalo con una honda. La piedra gira atada a una cuerda. Si la soltamos justo aquí, ¿por "
                    "dónde saldrá: por la a, por la be, o por la ce?")
    F.quiz(sc, "Soltamos la piedra aquí. ¿Por dónde sale: A, B o C?", lead=l1.start(), x=1490, y=200, size=42,
           max_w=700)
    hand = F.icon_piece("hand", 150, "skin")
    put(sc, hand, C[0] + 20, C[1] + 80, l1.start(), rot=160, z=2)
    stone = F.stone_piece(24)
    t_stop = l1.at("aquí") + 0.6
    rel = {}

    def stone_at(t):
        if "t" in rel and t >= rel["t"]:
            d = (t - rel["t"]) * omega * R          # free: straight on, along the velocity it had (to the right)
            return stone, top[0] + d, top[1], 0.0
        th = A_REL + omega * (min(t, t_stop) - t_stop)
        return stone, C[0] + R * math.cos(th), C[1] + R * math.sin(th), 0.0

    def rope(L, t):
        _, x, y, _ = stone_at(t)
        L.circle(*C, R, stroke=(150, 130, 110), width=3, dash=[10, 10], alpha=0.6)
        if "t" not in rel or t < rel["t"]:
            L.line([C, (x, y)], "brown", 4)
        g = prog(t, l1.at("por la A") - 0.2, 0.5, "out")
        if g > 0:
            L.arrow(top, (top[0], top[1] - 240 * g), "ink", 4, dash=[12, 9], head=22)
            L.stamp(F.tag_img(r"\b{A}", 44), top[0] + 40, top[1] - 230)
            L.arrow(top, (top[0] + 420 * g, top[1]), "ink", 4, dash=[12, 9], head=22)
            L.stamp(F.tag_img(r"\b{B}", 44), top[0] + 410, top[1] - 44)
            cpts = [(C[0] + (R + 90 * u) * math.cos(A_REL + 1.3 * u), C[1] + (R + 90 * u) * math.sin(A_REL + 1.3 * u))
                    for u in [k / 30 for k in range(31)]]
            L.line(F.Path(cpts).upto(g), "ink", 4, dash=[12, 9])
            L.stamp(F.tag_img(r"\b{C}", 44), cpts[-1][0] + 34, cpts[-1][1])
    live(sc, stone_at, at=0.0, z=5, jitter=0.4)
    mg(sc, rope, at=0.0, z=4)
    t_ans = F.think(sc, 4.0, x=1490, y=400)
    rel["t"] = t_ans + 0.5
    l2 = sc.say("Por la B: por la tangente. Sin la cuerda, la piedra sigue en línea recta, en la dirección que tenía "
                "su velocidad en ese instante.",
                tts="Por la be: por la tangente. Sin la cuerda, la piedra sigue en línea recta, en la dirección que "
                    "tenía su velocidad en ese instante.")

    def vtan(L, t):
        g = prog(t, t_ans, 0.4, "out")
        L.arrow(top, (top[0] + 170 * g, top[1]), "vel", 10, head=32)
        L.stamp(F.tag_img(r"\c{vel}{\vec{v}}", 40, "ink", pad=(10, 2)), top[0] + 90, top[1] + 42, alpha=g)
    mg(sc, vtan, at=t_ans, z=6)
    put(sc, F.check_mark(100), top[0] + 480, top[1] - 40, t_ans, enter="pop", z=7)
    put(sc, F.say_card("Sale por la {vel:tangente}, en la dirección de {vel:v}.", size=44, border=("vel", 4)), 1440,
        720, l2.at("tangente"))
    sc.wait(0.8)


# ============================================================================
# 5. aceleración: arrancar, frenar, girar; componentes tangencial y normal
# ============================================================================
CAR_S = 40.0      # px per metre on the roads
VEL_S = 30.0      # px per m/s for the velocity arrows of the cars
ACC_S = 40.0      # px per m/s² for the acceleration arrows


def _speed_row(L, t, t0, values, x0=250, dx=290, y=190, t_dv=None):
    """'one photo per second' of the velocity: an arrow for each second already reached; from t_dv on,
    the change of velocity between consecutive photos (Δv in 1 s) is drawn underneath in red"""
    for k, v in enumerate(values):
        tk = t0 + k
        if t < tk:
            break
        x = x0 + k * dx
        g = prog(t, tk, 0.3, "out")
        if v > 0:
            L.arrow((x - v * VEL_S / 2, y), (x - v * VEL_S / 2 + v * VEL_S * g, y), "vel", 10, head=30)
        else:
            L.circle(x, y, 8, fill="vel")
        L.stamp(F.formula(r"\t{%d m/s}" % v, 30, "vel_d"), x, y - 40, alpha=g)
        L.stamp(F.formula(r"t = %d\,\t{s}" % k, 28, "ink"), x, y + 40, alpha=g)
        if t_dv is not None and k > 0:
            h = prog(t, t_dv + 0.25 * (k - 1), 0.35, "out")
            if h > 0:
                dv = v - values[k - 1]
                xm = x - dx / 2
                L.arrow((xm - dv * VEL_S / 2, y + 110), (xm - dv * VEL_S / 2 + dv * VEL_S * h, y + 110), "acc", 9,
                        head=28)
                L.stamp(F.formula(r"\t{%s m/s}" % ("%+d" % dv).replace("-", "−"), 28, "acc_d"), xm, y + 146,
                        alpha=h)


def _va_pair(L, t, t0, x, y, same=True):
    """little legend: v and a with the same (or opposite) direction"""
    g = prog(t, t0, 0.4, "out")
    if g <= 0:
        return
    L.arrow((x - 90, y - 30), (x - 90 + 180 * g, y - 30), "vel", 10, head=30)
    L.stamp(F.formula(r"\vec{v}", 36, "vel"), x - 120, y - 30, alpha=g)
    if same:
        L.arrow((x - 90, y + 30), (x - 90 + 120 * g, y + 30), "acc", 10, head=30)
    else:
        L.arrow((x + 90, y + 30), (x + 90 - 120 * g, y + 30), "acc", 10, head=30)
    L.stamp(F.formula(r"\vec{a}", 36, "acc"), x - 120 if same else x + 120, y + 30, alpha=g)


def acel_intro(mv):
    sc = scn(mv, "acel-intro", bg="kraft", lead=0.3, transition="wipe")
    F.title(sc, "LA ACELERACIÓN", at=0.3, y=150, size=60)
    l1 = sc.say("Y ahora, la última gran idea: la {acc:aceleración}. La vamos a descubrir en tres escenas: arrancar, "
                "frenar y girar.")
    for i, (ic, lab, bg) in enumerate((("traffic-lights-green", "ARRANCAR", "grass"),
                                       ("stop-sign", "FRENAR", "acc_l"), ("steering-wheel", "GIRAR", "mustard"))):
        med = F.medal(ic, 220, bg=bg)
        tg = card(lab, size=44, font_name="body9", bg="cream", pad=(22, 8), seed=F._seed(lab))
        put(sc, kit.compose([(med, 0, 0), (tg, 0, 140, -2)]), 480 + i * 480, 560,
            l1.at(lab.lower(), after=-0.2), enter="pop")
    sc.wait(0.4)


def arrancar(mv):
    sc = scn(mv, "arrancar", bg="grass", lead=0.4)
    road = F.road_piece(2100, 220, seed=251, stop_x=300)
    RY = 650.0
    sc.add(road, W / 2, RY, at=0.0, enter="cut", rot=0, z=0, jitter=0.3)
    car = F.car_top("mustard")
    X0, Y = 260.0, RY + 55
    l1 = sc.say("Primera escena: un coche espera en un semáforo. Se pone verde... y arranca.")
    tl_r, tl_g = F.traffic_light("red"), F.traffic_light("green")
    e_tl = put(sc, tl_r, 300, RY - 170, 0.3, rot=0, z=3)
    e_tl.swap(l1.at("verde"), tl_g)
    t0 = l1.at("arranca", after=-0.2)
    l2 = sc.say("Cada segundo, su velocidad aumenta 2 metros por segundo: 2, 4, 6, 8...",
                tts="Cada segundo, su velocidad aumenta dos metros por segundo: dos, cuatro, seis, ocho...")
    a = 2.0

    def x_of(t):
        tt = max(0.0, t - t0)
        return X0 + 0.5 * a * tt * tt * CAR_S, a * tt

    def ghost(L, t):
        # stroboscopic marks: where the car was every second
        for k in range(1, 6):
            if t >= t0 + k:
                x = X0 + 0.5 * a * k * k * CAR_S
                L.line([(x, Y - 70), (x, Y + 70)], "cream", 4, dash=[8, 8], alpha=0.8)
                L.stamp(F.formula(r"\t{%d s}" % k, 26, "cream"), x, Y + 92)
    mg(sc, ghost, at=t0, z=1, shadow=False)
    live(sc, lambda t: (car, x_of(t)[0], Y, 0.0), at=0.0, z=4, jitter=0.4)
    spd, so = F.speedo_piece(240)
    put(sc, spd, 1750, 230, 0.4, rot=0, z=3)
    put(sc, card("m/s", size=28, font_name="body9", bg="cream", pad=(12, 4), seed=302), 1750, 315, 0.5, z=4)
    mg(sc, lambda L, t: F.speedo_needle(L, 1750 + so[0], 230 + so[1], 240, x_of(t)[1]), at=0.5, z=5)
    l3 = sc.say("La velocidad cambia, y eso es justo lo que mide la {acc:aceleración}: más 2 metros por segundo, cada "
                "segundo. Al arrancar, apunta hacia delante, en el mismo sentido que la velocidad.",
                tts="La velocidad cambia, y eso es justo lo que mide la aceleración: más dos metros por segundo, cada "
                    "segundo. Al arrancar, apunta hacia delante, en el mismo sentido que la velocidad.")
    t_dv = l3.at("más 2")
    mg(sc, lambda L, t: _speed_row(L, t, t0, [0, 2, 4, 6, 8], t_dv=t_dv), at=t0, z=5)
    put(sc, F.fcard(r"\c{acc}{\vec{a}}\t{ y }\c{vel}{\vec{v}}\t{: el mismo sentido}", size=44, border=("acc", 4)),
        820, 460, l3.at("mismo sentido"), z=7)
    mg(sc, lambda L, t: _va_pair(L, t, l3.at("hacia delante"), 1440, 460, True), at=l3.at("hacia delante"), z=7)
    sc.wait(0.5)


def frenar(mv):
    sc = scn(mv, "frenar", bg="grass", lead=0.4)
    RY = 650.0
    X0, Y = 400.0, RY + 55
    a = -2.0
    stop_x = X0 + 16 * CAR_S
    road = F.road_piece(2100, 220, seed=252, zebra_x=int(stop_x + 190 + 1050 - W / 2))
    sc.add(road, W / 2, RY, at=0.0, enter="cut", rot=0, z=0, jitter=0.3)
    car = F.car_top("mustard")
    l1 = sc.say("Segunda escena: el mismo coche frena antes de un paso de peatones.")
    t0 = l1.at("frena", after=-0.3)
    l2 = sc.say("Ahora, cada segundo, su velocidad disminuye 2 metros por segundo: 8, 6, 4, 2... y cero.",
                tts="Ahora, cada segundo, su velocidad disminuye dos metros por segundo: ocho, seis, cuatro, dos... y "
                    "cero.")

    def x_of(t):
        tt = min(4.0, max(0.0, t - t0))
        if t < t0:
            return X0 - 8.0 * (t0 - t) * CAR_S, 8.0
        return X0 + (8.0 * tt + 0.5 * a * tt * tt) * CAR_S, 8.0 + a * tt

    def ghost(L, t):
        for k in range(1, 5):
            if t >= t0 + k:
                x = X0 + (8.0 * k + 0.5 * a * k * k) * CAR_S
                L.line([(x, Y - 70), (x, Y + 70)], "cream", 4, dash=[8, 8], alpha=0.8)
                L.stamp(F.formula(r"\t{%d s}" % k, 26, "cream"), x, Y + (92 if k % 2 else 122))
    mg(sc, ghost, at=t0, z=1, shadow=False)
    live(sc, lambda t: (car, x_of(t)[0], Y, 0.0), at=0.0, z=4, jitter=0.4)
    spd, so = F.speedo_piece(240)
    put(sc, spd, 1750, 230, 0.4, rot=0, z=3)
    put(sc, card("m/s", size=28, font_name="body9", bg="cream", pad=(12, 4), seed=303), 1750, 315, 0.5, z=4)
    mg(sc, lambda L, t: F.speedo_needle(L, 1750 + so[0], 230 + so[1], 240, x_of(t)[1]), at=0.5, z=5)
    l3 = sc.say("La velocidad también cambia, así que también hay aceleración: {acc:frenar también es acelerar}. Pero "
                "ahora es de menos 2 metros por segundo cada segundo: la aceleración apunta hacia atrás, en sentido "
                "contrario a la velocidad.",
                tts="La velocidad también cambia, así que también hay aceleración: frenar también es acelerar. Pero "
                    "ahora es de menos dos metros por segundo cada segundo: la aceleración apunta hacia atrás, en "
                    "sentido contrario a la velocidad.")
    t_dv = l3.at("menos 2")
    mg(sc, lambda L, t: _speed_row(L, t, t0, [8, 6, 4, 2, 0], t_dv=t_dv), at=t0, z=5)
    put(sc, kit.ojo("{red|b:Frenar también es acelerar}: la velocidad cambia.", size=40, max_w=1100), 820, 470,
        l3.at("frenar también"), z=7, rot=-1)
    mg(sc, lambda L, t: _va_pair(L, t, l3.at("hacia atrás"), 1560, 470, False), at=l3.at("hacia atrás"), z=7)
    sc.wait(0.5)


def girar(mv):
    sc = scn(mv, "girar", bg="grass", lead=0.4)
    C = (640.0, 560.0)
    RB = 330
    rb = F.roundabout_piece(RB, 120, seed=271)
    sc.add(rb, C[0], C[1], at=0.0, enter="cut", rot=0, z=0, jitter=0.3)
    sc.add(F.tree_top(70, 283), C[0], C[1], at=0.0, enter="cut", rot=0, z=1, jitter=0.5)
    rr = RB - 60                   # lane radius (px) = 10 m
    PXM = rr / 10.0
    v = 5.0
    om = v / 10.0                  # rad/s
    car = F.car_top("mustard", L=160)
    th0 = math.radians(90)         # start at the bottom of the roundabout

    def th(t):
        return th0 - om * t       # counter-clockwise on screen (driving on the right)

    def car_at(t):
        a_ = th(t)
        x, y = C[0] + rr * math.cos(a_), C[1] + rr * math.sin(a_)
        # heading: tangent for counter-clockwise motion
        hx, hy = math.sin(a_), -math.cos(a_)
        ang = -math.degrees(math.atan2(hy, hx))
        return car, x, y, ang
    live(sc, car_at, at=0.0, z=4, jitter=0.4)
    spd, so = F.speedo_piece(240)
    put(sc, spd, 1650, 250, 0.4, rot=0, z=3)
    put(sc, card("m/s", size=28, font_name="body9", bg="cream", pad=(12, 4), seed=304), 1650, 335, 0.5, z=4)
    mg(sc, lambda L, t: F.speedo_needle(L, 1650 + so[0], 250 + so[1], 240, v), at=0.5, z=5)
    l1 = sc.say("Tercera escena: el coche da vueltas a una rotonda, siempre a 5 metros por segundo.",
                tts="Tercera escena: el coche da vueltas a una rotonda, siempre a cinco metros por segundo.")
    l2 = sc.say("Fíjate en el velocímetro: no se mueve. ¿Hay aceleración?")
    sc.wait(1.4)
    l3 = sc.say("¡Sí! La velocidad es un vector. Su módulo no cambia, pero su dirección cambia a cada instante: "
                "siempre es tangente a la rotonda.")
    t_v = l3.at("vector")

    def vel(L, t):
        g = prog(t, t_v, 0.4, "out")
        a_ = th(t)
        x, y = C[0] + rr * math.cos(a_), C[1] + rr * math.sin(a_)
        hx, hy = math.sin(a_), -math.cos(a_)
        L.arrow((x, y), (x + hx * v * VEL_S * g, y + hy * v * VEL_S * g), "vel", 10, head=32)
        L.stamp(F.tag_img(r"\c{vel}{\vec{v}}", 38, "ink", pad=(8, 2)), x + hx * v * VEL_S + 30, y + hy * v * VEL_S,
                alpha=g)
        b = prog(t, t_acc, 0.5, "out")
        if b > 0:
            an = v * v / 10.0
            L.arrow((x, y), (x - math.cos(a_) * an * ACC_S * b * 1.2, y - math.sin(a_) * an * ACC_S * b * 1.2), "acc",
                    10, head=32)
            L.stamp(F.tag_img(r"\c{acc}{\vec{a}}", 38, "ink", pad=(8, 2)),
                    x - math.cos(a_) * (an * ACC_S * 1.2 + 34), y - math.sin(a_) * (an * ACC_S * 1.2 + 34), alpha=b)
    l4 = sc.say("Si tomamos la velocidad en dos instantes y las restamos, la diferencia, delta uve, apunta hacia el "
                "centro de la rotonda.")
    t_dv = l4.at("dos instantes")
    l5 = sc.say("Y hacia allí apunta la aceleración: hacia el {acc:centro} de la curva.")
    t_acc = l5.at("aceleración")
    mg(sc, vel, at=t_v, z=6)

    # Δv construction: the velocity at two instants, slid to a side panel and put tail to tail
    t1_, t2_ = t_dv - 2.4, t_dv - 1.2
    QX, QY = 1690.0, 610.0
    VSC = 1.7

    def pos_vel(tk):
        a_ = th(tk)
        return (C[0] + rr * math.cos(a_), C[1] + rr * math.sin(a_)), (math.sin(a_) * v * VEL_S * VSC,
                                                                      -math.cos(a_) * v * VEL_S * VSC)

    def dv(L, t):
        g = prog(t, t_dv, 0.5, "out")
        if g <= 0:
            return
        m = prog(t, t_dv + 0.8, 1.2, "io")
        L.poly([(QX - 380, QY - 230), (QX + 110, QY - 230), (QX + 110, QY + 200), (QX - 380, QY + 200)],
               fill=(251, 245, 230, 225), alpha=g)
        L.stamp(F.formula(r"\c{acc}{Δ\vec{v}} = \vec{v}_2 − \vec{v}_1", 40), QX - 135, QY + 160, alpha=g)
        tips = []
        for k, (tk, col) in enumerate(((t1_, "vel"), (t2_, "vel_d"))):
            p0, vv = pos_vel(tk)
            tail = lerp2(p0, (QX, QY), m)
            tip = (tail[0] + vv[0], tail[1] + vv[1])
            tips.append(tip)
            L.arrow(tail, tip, col, 9, head=30)
            L.stamp(F.tag_img(r"\vec{v}_%d" % (k + 1), 32, col, pad=(6, 1)), tip[0] + 26, tip[1] + (18 if k else -18))
        h = prog(t, t_dv + 2.2, 0.6, "out")
        if h > 0:
            L.arrow(tips[0], lerp2(tips[0], tips[1], h), "acc", 9, head=28, min_head=8)
            # the same Δv drawn on the roundabout, between both instants: it points to the centre
            tm = (t1_ + t2_) / 2
            a_ = th(tm)
            pm = (C[0] + rr * math.cos(a_), C[1] + rr * math.sin(a_))
            d = math.hypot(tips[1][0] - tips[0][0], tips[1][1] - tips[0][1])
            k2 = prog(t, l4.at("centro"), 0.6, "out")
            if k2 > 0:
                L.arrow(pm, (pm[0] - math.cos(a_) * d * k2, pm[1] - math.sin(a_) * d * k2), "acc", 9, head=28)
                L.line([pm, C], "acc", 3, dash=[8, 8], alpha=0.7 * k2)
                L.stamp(F.tag_img(r"\c{acc}{Δ\vec{v}}", 34, "ink", pad=(6, 1)), pm[0] - math.cos(a_) * (d + 34),
                        pm[1] - math.sin(a_) * (d + 34), alpha=k2)
    mg(sc, dv, at=t_dv, z=6)
    put(sc, F.fcard(r"|\c{vel}{\vec{v}}|\t{ constante, pero }\c{vel}{\vec{v}}\t{ cambia de dirección}", size=40,
                    border=("vel", 4)), 1180, 110, l3.at("dirección"), z=7)
    sc.wait(0.6)


def acel_def(mv):
    sc = scn(mv, "acel-def", bg="grid", lead=0.4)
    F.title(sc, "¿QUÉ ES LA ACELERACIÓN?", at=0.3)
    l1 = sc.say("En las tres escenas cambia la velocidad: en módulo, al arrancar y al frenar; o en dirección, al "
                "girar. La {acc:aceleración} mide cómo cambia la velocidad con el tiempo.")
    cases = [("ARRANCAR", "arrancar", (0, 3), (0, 6)), ("FRENAR", "frenar", (0, 6), (0, 3)),
             ("GIRAR", "girar", (0, 5), (40, 5))]
    for i, (lab, key, v1, v2) in enumerate(cases):
        x = 250 + i * 300
        tt = l1.at(key, after=-0.2)
        put(sc, card(lab, size=34, font_name="body9", bg="cream", pad=(16, 6), seed=F._seed(lab) + 1), x, 270, tt,
            enter="pop")

        def mini(L, t, x=x, v1=v1, v2=v2, tt=tt):
            g = prog(t, tt, 0.5, "out")
            o = (x - 90, 470)
            L.circle(*o, 6, fill="ink", alpha=g)
            tips = []
            for k, (ang, mag) in enumerate((v1, v2)):
                a_ = math.radians(ang)
                tip = (o[0] + math.cos(a_) * mag * 30 * g, o[1] - math.sin(a_) * mag * 30 * g)
                tips.append(tip)
                L.arrow(o, tip, "vel" if k == 0 else "vel_d", 8, head=26)
                L.stamp(F.formula(r"\vec{v}_%d" % (k + 1), 28, "vel" if k == 0 else "vel_d"),
                        tip[0] + 22, tip[1] + (22 if k == 0 else -22), alpha=g)
            h = prog(t, tt + 0.8, 0.5, "out")
            if h > 0:
                d = (tips[1][0] - tips[0][0], tips[1][1] - tips[0][1])
                b0 = (o[0] + 90 - d[0] / 2, 600 - d[1] / 2)
                L.arrow(b0, (b0[0] + d[0] * h, b0[1] + d[1] * h), "acc", 8, head=24)
                L.stamp(F.formula(r"\c{acc}{Δ\vec{v}}", 30), o[0] + 90, 660, alpha=h)
        mg(sc, mini, at=tt, z=4)
    l2 = sc.say("La {acc:aceleración media} es la variación de la velocidad dividida entre el tiempo que tarda en "
                "cambiar.")
    f1 = F.def_card("ACELERACIÓN MEDIA", [r"\c{acc}{\vec{a}_m} = \frac{Δ\vec{v}}{Δt} = \frac{\vec{v}_f − "
                                          r"\vec{v}_0}{Δt}"], head_bg="acc", size=54, border=("acc", 4))
    put(sc, f1, 1440, 300, l2.at("aceleración media"), rot=-0.8)
    l3 = sc.say("Y la {acc:aceleración instantánea}, como antes, es su límite cuando delta te tiende a cero: de uve "
                "entre de te.")
    f2 = F.def_card("ACELERACIÓN INSTANTÁNEA", [r"\c{acc}{\vec{a}} = \lim{Δt\to0}\frac{Δ\vec{v}}{Δt} = "
                                                r"\frac{d\vec{v}}{dt}"], head_bg="acc", size=54, border=("acc", 4))
    put(sc, f2, 1440, 548, l3.at("instantánea"), rot=0.8)
    l4 = sc.say("Se mide en metros por segundo al cuadrado. Al arrancar, nuestro coche ganaba 2 metros por segundo "
                "cada segundo: su aceleración era de 2 metros por segundo al cuadrado.",
                tts="Se mide en metros por segundo al cuadrado. Al arrancar, nuestro coche ganaba dos metros por "
                    "segundo cada segundo: su aceleración era de dos metros por segundo al cuadrado.")
    f3 = F.fcard([r"\t{Unidad: }\b{m/s}^2", r"a = \frac{8\,\t{m/s} − 0}{4\,\t{s}} = 2\,\t{m/s}^2"], size=44,
                 border=("acc", 3))
    put(sc, f3, 1440, 778, l4.at("metros por segundo al cuadrado"), rot=-1)
    sc.wait(0.5)


def componentes(mv):
    sc = scn(mv, "componentes", bg="grass", lead=0.4)
    F.title(sc, "COMPONENTES INTRÍNSECAS", at=0.3)
    P = (700.0, 360.0)                 # where the car is frozen (top of the curve)
    v = 10.0
    at_ = 2.0
    R0 = 20.0                          # m
    PXM = 22.0                         # px per metre for the road geometry (r = 20 m -> 440 px)
    VS, AS = 24.0, 48.0                # px per m/s and per m/s²
    l1 = sc.say("A menudo pasan las dos cosas a la vez: por ejemplo, un coche que acelera en plena curva.")
    t_in = l1.start(0.2)
    state = {"R": lambda t: R0}

    def road(L, t):
        R = state["R"](t) * PXM
        cx, cy = P[0], P[1] + R
        half = min(1.3, 1100.0 / R)       # visible half-angle (rad)
        n = 80
        pts = [(cx + R * math.sin(-half + 2 * half * k / n), cy - R * math.cos(-half + 2 * half * k / n))
               for k in range(n + 1)]
        L.line(pts, "road", 130, cap="butt")
        L.line(pts, "cream", 4, dash=[26, 20], cap="butt")
    mg(sc, road, at=0.0, z=0, shadow=False)
    car = F.car_top("mustard", L=170)

    def car_at(t):
        # it arrives at P speeding up, then the picture is frozen
        u = prog(t, t_in, 2.6, "out")
        R = R0 * PXM
        ang = -0.9 * (1 - u)
        x, y = P[0] + R * math.sin(ang), P[1] + R - R * math.cos(ang)
        return car, x, y, -math.degrees(ang)
    live(sc, car_at, at=0.0, z=3, jitter=0.4)
    l2 = sc.say("Congelamos la imagen. La velocidad es tangente a la curva, y la aceleración apunta en diagonal: un "
                "poco hacia delante y un poco hacia el centro de la curva.")
    t_v, t_a = l2.at("velocidad"), l2.at("aceleración")
    l3 = sc.say("Por eso se descompone en dos partes, llamadas {acc:componentes intrínsecas}.")
    l4 = sc.say("La {acc:aceleración tangencial} va en la dirección de la velocidad. Cambia su módulo: es la que "
                "notas al arrancar o al frenar.")
    t_t = l4.at("tangencial")
    l5 = sc.say("La {acc:aceleración normal} es perpendicular a la velocidad, y apunta hacia el centro de la curva. "
                "Cambia la dirección de la velocidad: es la que te hace girar.")
    t_n = l5.at("normal")
    l6 = sc.say("Su valor es la velocidad al cuadrado dividida entre el radio de la curva.")
    l7 = sc.say("Por ejemplo, a 10 metros por segundo, en una curva de 20 metros de radio: 100 entre 20 da 5 metros "
                "por segundo al cuadrado.",
                tts="Por ejemplo, a diez metros por segundo, en una curva de veinte metros de radio: cien entre veinte "
                    "da cinco metros por segundo al cuadrado.")
    l8 = sc.say("Comprobación visual: si abrimos la curva, el radio crece, y la aceleración normal se hace cada vez "
                "más pequeña. Una recta es como una curva de radio infinito: no tiene aceleración normal.")
    t_open = l8.at("abrimos", after=-0.2)
    T_OPEN = max(3.0, l8.at("recta") - t_open)

    def R_of(t):
        u = prog(t, t_open, T_OPEN, "in")
        return R0 * (1 + 40 * u * u * u) if u < 1 else 1e6
    state["R"] = R_of

    def vectors(L, t):
        R = R_of(t)
        an = v * v / R if R < 1e5 else 0.0
        g = prog(t, t_v, 0.4, "out")
        vy = P[1] - 100
        L.arrow((P[0] - 40, vy), (P[0] - 40 + v * VS * g, vy), "vel", 10, head=32)
        L.stamp(F.tag_img(r"\c{vel}{\vec{v}}\t{ (tangente)}", 36, "ink", pad=(8, 2)), P[0] - 40 + v * VS + 110, vy,
                alpha=g)
        a = prog(t, t_a, 0.5, "out")
        if a > 0:
            tip = (P[0] + at_ * AS * a, P[1] + an * AS * a)
            L.arrow(P, tip, "acc", 11, head=34, min_head=6)
            L.stamp(F.tag_img(r"\c{acc}{\vec{a}}", 42, "ink", pad=(8, 2)), tip[0] + 44, tip[1] + 6, alpha=a)
        b = prog(t, t_t, 0.5, "out")
        if b > 0:
            L.arrow(P, (P[0] + at_ * AS * b, P[1]), "acc_d", 8, head=26)
            L.line([(P[0] + at_ * AS, P[1]), (P[0] + at_ * AS, P[1] + an * AS)], "acc_d", 3, dash=[8, 7], alpha=b)
            L.stamp(F.tag_img(r"\c{acc_d}{a_t}", 38, "ink", pad=(8, 2)), P[0] + at_ * AS + 50, P[1] - 30, alpha=b)
        c = prog(t, t_n, 0.5, "out")
        if c > 0:
            L.arrow(P, (P[0], P[1] + an * AS * c), "acc_d", 8, head=26, min_head=4)
            L.line([(P[0], P[1] + an * AS), (P[0] + at_ * AS, P[1] + an * AS)], "acc_d", 3, dash=[8, 7], alpha=c)
            L.stamp(F.tag_img(r"\c{acc_d}{a_n}", 38, "ink", pad=(8, 2)), P[0] - 56, P[1] + max(60, an * AS * 0.6),
                    alpha=c)
            # radius towards the centre of the curve
            Rp = R * PXM
            if Rp < 3000:
                y_end = min(P[1] + Rp, 870)
                L.line([(P[0], P[1] + an * AS + 24), (P[0], y_end)], "ink", 3, dash=[10, 9], alpha=0.8 * c)
                if P[1] + Rp <= 870:
                    L.circle(P[0], P[1] + Rp, 10, fill="ink")
                    L.stamp(F.tag_img(r"\t{centro}", 30, "ink"), P[0] + 80, P[1] + Rp)
                L.stamp(F.tag_img(r"r = %s\,\t{m}" % F.num(R, 0), 34, "ink"), P[0] - 110, min(P[1] + Rp * 0.75, 820),
                        alpha=c)
        if t >= t_open:
            L.stamp(F.tag_img(r"\c{acc_d}{a_n} = \frac{v^2}{r} = %s\,\t{m/s}^2" % F.num(an, 2), 44, "ink",
                              border=("acc", 3), pad=(14, 6)), 1500, 820)
    mg(sc, vectors, at=t_v, z=5)
    f = F.def_card("ACELERACIÓN NORMAL", [r"\c{acc_d}{a_n} = \frac{v^2}{r}"], head_bg="acc", size=64,
                   border=("acc", 4))
    put(sc, f, 1500, 330, l6.at("velocidad al cuadrado"), rot=-1, z=7)
    f2 = F.fcard(r"a_n = \frac{(10\,\t{m/s})^2}{20\,\t{m}} = 5\,\t{m/s}^2", size=50, border=("acc", 3))
    e_f2 = put(sc, f2, 1500, 600, l7.at("100"), rot=1, z=7)
    e_f2.leave(t_open, "fall", 0.5)
    l9 = sc.say("Por eso, en un movimiento rectilíneo solo hay aceleración tangencial; en uno curvilíneo, siempre hay "
                "aceleración normal.")
    put(sc, F.fcard([r"\t{Rectilíneo: solo }\c{acc_d}{a_t}", r"\t{Curvilíneo: hay }\c{acc_d}{a_n}"], size=44,
                    border=("acc", 3), align="l"), 1500, 600, l9.at("rectilíneo"), rot=-0.6, z=7)
    sc.wait(0.6)


def check_acel(mv):
    sc = scn(mv, "check-acel", bg="grid", lead=0.3)
    l1 = sc.say("Último reto: ¿qué componentes tiene la aceleración en cada caso? Uno: un coche arranca en una "
                "recta. Dos: da vueltas a una rotonda a velocidad constante. Tres: frena en plena curva.")
    F.quiz(sc, "¿Qué componentes tiene la aceleración?", lead=l1.start(), y=180, size=46)
    cases = [(380, "1 · Arranca en una recta", "Uno"), (960, "2 · Rotonda a velocidad constante", "Dos"),
             (1540, "3 · Frena en plena curva", "Tres")]
    for x, lab, key in cases:
        put(sc, card(lab, size=34, font_name="body9", bg="cream", pad=(18, 8), seed=F._seed(lab), max_w=420), x, 330,
            l1.at(key), enter="pop")
    t_rev = F.think(sc, 5.0)
    l2 = sc.say("Uno: solo tangencial. Dos: solo normal. Tres: las dos; la tangencial, hacia atrás, y la normal, "
                "hacia el centro.")
    keys = [l2.at("Uno"), l2.at("Dos"), l2.at("Tres")]

    def draw(L, t):
        # 1: straight road, v and a_t forwards
        g = prog(t, l1.at("Uno"), 0.5)
        x, y = 380, 560
        L.line([(x - 220, y), (x + 220, y)], "road_l", 30, alpha=g, cap="butt")
        L.arrow((x - 60, y - 60), (x + 100, y - 60), "vel", 9, head=28, alpha=g)
        # 2: circle, v tangent, a_n inwards
        g = prog(t, l1.at("Dos"), 0.5)
        cx, cy, r = 960, 600, 130
        L.circle(cx, cy, r, stroke="road_l", width=30, alpha=g)
        L.arrow((cx, cy - r), (cx - 150, cy - r), "vel", 9, head=28, alpha=g)
        # 3: arc, v tangent; braking
        g = prog(t, l1.at("Tres"), 0.5)
        cx3, cy3, r3 = 1540, 760, 240
        L.arc(cx3, cy3, r3, 220, 320, "road_l", 30, alpha=g)
        L.arrow((cx3, cy3 - r3), (cx3 + 150, cy3 - r3), "vel", 9, head=28, alpha=g)
        # answers
        a1 = prog(t, keys[0], 0.4, "out")
        if a1 > 0:
            L.arrow((x - 60, y + 50), (x - 60 + 110 * a1, y + 50), "acc_d", 9, head=28)
            L.stamp(F.tag_img(r"\t{solo }\c{acc_d}{a_t}", 40, "ink", border=("acc", 3), pad=(12, 4)), x, 790,
                    alpha=a1)
        a2 = prog(t, keys[1], 0.4, "out")
        if a2 > 0:
            L.arrow((cx, cy - r), (cx, cy - r + 100 * a2), "acc_d", 9, head=28)
            L.stamp(F.tag_img(r"\t{solo }\c{acc_d}{a_n}", 40, "ink", border=("acc", 3), pad=(12, 4)), cx, 790,
                    alpha=a2)
        a3 = prog(t, keys[2], 0.4, "out")
        if a3 > 0:
            L.arrow((cx3, cy3 - r3), (cx3 - 90 * a3, cy3 - r3), "acc_d", 9, head=28)
            L.arrow((cx3, cy3 - r3), (cx3, cy3 - r3 + 100 * a3), "acc_d", 9, head=28)
            L.stamp(F.tag_img(r"\c{acc_d}{a_t}\t{ y }\c{acc_d}{a_n}", 40, "ink", border=("acc", 3), pad=(12, 4)),
                    cx3, 790, alpha=a3)
    mg(sc, draw, at=l1.start(), z=4)
    for k, (x, _, _) in enumerate(cases):
        put(sc, F.check_mark(64), x + 165, 790, keys[k] + 0.2, enter="pop", z=6)
    sc.wait(0.8)


# ============================================================================
# 6. repaso y cierre
# ============================================================================
RESUMEN = [
    (r"\b{Sistema de referencia:}\t{ origen + ejes. Movimiento y reposo son relativos.}",
     "El movimiento es relativo: depende del sistema de referencia, un origen y unos ejes."),
    (r"\b{Punto material}\t{ · }\b{trayectoria}\t{ rectilínea o curvilínea}",
     "Si el tamaño no importa, el móvil es un punto material. Su trayectoria puede ser rectilínea o curvilínea."),
    (r"\c{pos}{\vec{r}} = x\,\vec{ı} + y\,\vec{ȷ}\quad \c{disp}{Δ\vec{r}} = \vec{r}_f − \vec{r}_0\quad "
     r"\c{space}{s} \geq |Δ\vec{r}|",
     "La posición es un vector. El desplazamiento es la posición final menos la inicial. Y el espacio recorrido es "
     "mayor o igual que su módulo."),
    (r"\c{vel}{\vec{v}_m} = \frac{Δ\vec{r}}{Δt}\quad \c{vel}{\vec{v}} = \frac{d\vec{r}}{dt}\t{  (tangente)}",
     "Velocidad media: desplazamiento entre tiempo. La instantánea es su límite, y siempre es tangente a la "
     "trayectoria."),
    (r"\c{acc}{\vec{a}_m} = \frac{Δ\vec{v}}{Δt}\quad \c{acc}{\vec{a}} = \frac{d\vec{v}}{dt}\quad \t{(m/s}^2\t{)}",
     "La aceleración mide cómo cambia la velocidad. Frenar y girar también es acelerar."),
    (r"\c{acc_d}{a_t}\t{: cambia el módulo}\quad \c{acc_d}{a_n} = \frac{v^2}{r}\t{: cambia la dirección}",
     "La aceleración tangencial cambia el módulo de la velocidad; la normal, uve al cuadrado entre erre, cambia su "
     "dirección."),
]


def resumen(mv):
    sc = scn(mv, "resumen", bg="kraft", lead=0.4, transition="wipe")
    F.title(sc, "REPASO DEL TEMA 1", at=0.3, y=140, size=56)
    l0 = sc.say("Repaso rápido del tema.")
    y = 250
    for i, (src, spoken) in enumerate(RESUMEN):
        ln = sc.say(spoken)
        c = F.fcard(src, size=40, align="l", pad=(30, 12), min_w=1500)
        put(sc, c, W / 2, y + c.vh / 2, ln.start(), enter="slide_r", rot=((i % 2) - 0.5) * 0.8)
        y += c.vh + 12
    sc.wait(0.8)


def outro(mv):
    sc = mv.scene("fin", bg="kraft", transition="wipe", lead=0.3)
    put(sc, greek.title_block("FIN DEL TEMA 1", size=120, color="cream", tracking=0.05, font_name="body9"), W / 2,
        300, 0.4, rot=0)
    ln = sc.say("Fin del tema uno. En el siguiente: el movimiento rectilíneo uniforme. ¡Hasta pronto!")
    put(sc, card("Próximo: Tema 2 · MRU", size=56, font_name="body9", bg="cream", pad=(40, 14), seed=1601,
                 border=("pos", 4)), W / 2, 470, ln.at("siguiente"), enter="drop", rot=-1)
    tr = F.train_sprite()
    live(sc, lambda t: (tr, -900 + 300 * t, 760, 0.0, 0.42), at=0.2, z=1, jitter=0.6)
    sc.wait(0.3)
    sc.jingle(sc.now(), "fis_outro", gain=0.45)
    put(sc, card("Iconos: game-icons.net (CC BY 3.0) · Voz: Piper davefx · Hecho con Python", size=26,
                 font_name="body7", bg="cream", pad=(20, 8), seed=1602), W / 2, 960, sc.now(), enter="pop", rot=0)
    sc.wait(4.0)


# ============================================================================
def build(only=None):
    mv = Movie(voice="davefx", speed=0.9, wipe="fisica", flicker=0.0)
    parts = [("intro", intro), ("tren", tren), ("relativo", tren_conclusion), ("punto", punto_material),
             ("trayectoria", trayectoria), ("posicion", posicion), ("idavuelta", ida_vuelta),
             ("desplazamiento", desplazamiento), ("checkida", check_ida), ("vmedia", velocidad_media),
             ("vinst", velocidad_instantanea), ("honda", honda), ("acel", acel_intro), ("arrancar", arrancar),
             ("frenar", frenar), ("girar", girar), ("aceldef", acel_def), ("componentes", componentes),
             ("checkacel", check_acel), ("resumen", resumen), ("fin", outro)]
    for name, fn in parts:
        if only and name not in only:
            continue
        fn(mv)
    return mv


def chapters(mv):
    names = {"title": "Inicio", "tren": "1 · El movimiento es relativo",
             "punto": "2 · Punto material, trayectoria y posición",
             "idavuelta": "3 · Espacio recorrido y desplazamiento",
             "vmedia": "4 · Velocidad media e instantánea",
             "acel-intro": "5 · Aceleración: arrancar, frenar y girar",
             "componentes": "6 · Componentes tangencial y normal", "resumen": "Repaso del tema"}
    return [(st, names[sc.name]) for sc, st in zip(mv.scenes, mv.starts) if sc.name in names]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "out/cinematica_t1.mp4"
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
        step = None
        for a in sys.argv[1:]:
            if a.startswith("--every="):
                step = float(a.split("=", 1)[1])
        for i, (sc, st) in enumerate(zip(mv.scenes, mv.starts)):
            ts = [st + max(0.5, sc.cursor - 0.3)]
            if step:
                ts = [st + k * step for k in range(int(sc.duration / step) + 1)]
            for t in ts:
                mv.still(t, os.path.join(d, f"{i:02d}_{sc.name}_{t:06.1f}.png"))
    else:
        chs = chapters(mv)
        # 12 fps, CRF 27 with x264's animation tuning and 64 kb/s mono audio: < 30 MB for the 13 minutes
        mv.render(out, chapters=chs, crf=27, abr="64k", tune="animation")
        with open(os.path.splitext(out)[0] + "_capitulos.txt", "w", encoding="utf-8") as f:
            for st, ttl in chs:
                f.write("%d:%02d  %s\n" % (st // 60, st % 60, ttl))

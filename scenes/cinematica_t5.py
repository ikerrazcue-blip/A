"""Física · Cinemática · Tema 5: método de examen.

Tres enunciados breves (MRU, MRUA y movimiento vertical). Antes de resolver cada uno, unos segundos para que el
espectador identifique el tipo de movimiento. Después, el procedimiento: dibujar el eje, fijar el sentido positivo,
anotar los datos con signos y unidades, elegir la ecuación, despejar y comprobar el resultado. Cierre: chuleta
visual con las fórmulas fundamentales y la pregunta que lleva a cada una. Sin azul.

    python3 scenes/cinematica_t5.py out/Cinematica_T5_Metodo_examen.mp4
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cine_comun as K  # noqa: E402
from cine_comun import F, W, H, card, kit, formula, mg, live, prog, lerp2, put, scn  # noqa: E402

STEPS = ["¿Qué movimiento es?", "Dibuja el eje", "Origen y sentido positivo", "Datos con signo y unidades",
         "Elige la ecuación", "Despeja y calcula", "Comprueba el resultado"]
SL_X, SL_Y, SL_W = 40, 250, 500


def intro(mv):
    K.portada(mv, "MÉTODO", "Tema 5 · Cómo resolver un problema de examen",
              "Cinemática. Tema cinco: el método para resolver cualquier problema de examen.",
              deco=("checklist", "pencil"))


def metodo(mv):
    sc = scn(mv, "metodo", bg="grid", lead=0.4, transition="wipe")
    F.title(sc, "EL MÉTODO, PASO A PASO", at=0.3)
    sc.say("En un examen, casi todos los problemas de cinemática se resuelven siguiendo los mismos pasos, "
           "siempre en el mismo orden.")
    spoken = ["Antes de nada, lee el enunciado y pregúntate qué tipo de movimiento es: uniforme, acelerado o "
              "vertical.",
              "Uno: dibuja el eje, en la dirección del movimiento.",
              "Dos: elige el origen y el sentido positivo. Así, cada signo tendrá un significado.",
              "Tres: anota los datos con su signo y sus unidades, y pásalos al Sistema Internacional.",
              "Cuatro: elige la ecuación que contiene lo que sabes y lo que buscas.",
              "Cinco: despeja la incógnita, y solo entonces sustituye y calcula.",
              "Y seis: comprueba el resultado. ¿Las unidades son correctas? ¿El signo tiene sentido? ¿Es un número "
              "razonable?"]
    ls = [sc.say(txt) for txt in spoken]
    times = [ln.start() for ln in ls]
    done = times[1:] + [ls[-1].end(0.2)]
    F.step_list(sc, STEPS, 80, 250, times, size=38, w=760, done_times=done)
    ejemplo(sc, ls)
    sc.wait(2.6)


def chip(src, size=28, color="ink"):
    """a small formula sticker as a sprite (so it can pop in and out)"""
    return F.Sprite(F.tag_img(src, size, color), shadow_blur=3)


def ejemplo(sc, ls):
    """right-hand panel: a short example that is solved while the steps are named"""
    sc.add(F.sheet(900, 650, seed=505, lines=False), 1390, 568, at=ls[0].start(), enter="drop", rot=-0.4, z=2)
    st = F.tabbed(F.say_card("Un coche va a {vel:72 km/h} y frena con una aceleración de {acc:4 m/s²}. ¿Cuánto "
                             "tarda en pararse?", size=28, max_w=760, border=("mustard", 3)), "EJEMPLO",
                  head_bg="mustard", head_color="ink", head_size=28)
    put(sc, st, 1380, 335, ls[0].start(0.3), z=4)
    t_mrua = ls[0].at("acelerado")
    put(sc, card("MRUA", size=30, font_name="body9", bg="acc_l", pad=(14, 4), seed=515), 1765, 266, t_mrua,
        enter="pop", z=6, rot=6)
    put(sc, F.check_mark(64), 1838, 246, t_mrua + 0.3, enter="pop", z=7)
    car = F.car_top("mustard", L=100)
    ax_y, ox = 470.0, 1060.0
    t_ax, t_or, t_dat = ls[1].at("eje"), ls[2].at("origen"), ls[3].at("signo")

    def fn(L, t):
        g = prog(t, t_ax, 0.6, "out")
        L.arrow((990, ax_y), (990 + 810 * g, ax_y), "ink", 5, head=22)
        if g >= 1:
            L.stamp(formula(r"x\;\t{(m)}", 26), 1780, ax_y + 32)
        b = prog(t, t_or, 0.4)
        if b > 0:
            L.line([(ox, ax_y - 12), (ox, ax_y + 12)], "ink", 4, alpha=b)
            L.stamp(formula("O", 28), ox, ax_y + 32, alpha=b)
            L.arrow((1480, ax_y - 42), (1620, ax_y - 42), "pos", 7, head=24, alpha=b)
            L.stamp(formula(r"+", 40, "pos"), 1652, ax_y - 42, alpha=b)
        c = prog(t, t_dat, 0.4)
        if c > 0:
            L.arrow((ox + 70, ax_y - 42), (ox + 210, ax_y - 42), "vel", 7, head=24, alpha=c)
            L.arrow((ox + 210, ax_y + 40), (ox + 100, ax_y + 40), "acc", 7, head=24, alpha=c)
    mg(sc, fn, at=t_ax, z=5)
    live(sc, lambda t: (car, ox, ax_y - 30, 0.0), at=t_ax + 0.3, z=6, jitter=0.4)
    tags = [(r"v_0 = \frac{72}{3,6} = +20\,\t{m/s}", "vel_d", 1140, ls[3].at("datos")),
            (r"a = −4\,\t{m/s}^2", "acc_d", 1410, ls[3].at("signo")),
            (r"v = 0", "ink", 1575, ls[3].at("unidades")),
            (r"t = \;?", "pos_d", 1710, ls[4].at("buscas"))]
    for src, col, x, t0 in tags:
        put(sc, chip(src, 28, col), x, 552, t0, enter="pop", z=6)
    F.board(sc, [(r"v = v_0 + a\,\c{pos}{t}", ls[4].at("ecuación")),
                 (r"t = \frac{v − v_0}{a}", ls[5].at("despeja")),
                 (r"t = \frac{0 − 20}{−4} = \c{pos}{5\,\t{s}}", ls[5].at("sustituye"))], 1000, 598, size=32, gap=12,
            z=5)
    checks = [(r"\t{unidades: s}\;\t{✓}", 668, ls[6].at("unidades")),
              (r"\t{signo: }t > 0\;\t{✓}", 738, ls[6].at("signo")),
              (r"\t{razonable: }5\,\t{s}\;\t{✓}", 808, ls[6].at("razonable"))]
    for src, y, t0 in checks:
        put(sc, chip(src, 28, "grass_d"), 1650, y, t0, enter="pop", z=6)


def option_cards(sc, at, correct, until, y=420, xs=(830, 1230, 1630)):
    """the three possible answers to «¿qué movimiento es?» (they leave at `until`); returns the right one's place"""
    opts = [("MRU", "speedometer", "pos_l"), ("MRUA", "traffic-lights-green", "acc_l"),
            ("VERTICAL", "falling-rocks", "mustard")]
    for k, ((lab, ic, bg), x) in enumerate(zip(opts, xs)):
        med = F.medal(ic, 120, bg=bg)
        tg = card(lab, size=36, font_name="body9", bg="cream", pad=(18, 6), seed=F._seed(lab) + 9)
        put(sc, kit.compose([(med, 0, 0), (tg, 0, 82, -2)]), x, y, at + 0.25 * k, enter="pop", z=6,
            until=until + 0.08 * k, exit="pop")
    return [xs[[o[0] for o in opts].index(correct)], y]


def resolver(mv, name, title, enunciado, spoken_enunciado, tipo, pista, pasos, comprobacion, diagram):
    """one exam problem: identify the motion (pause), then the six steps with the step list on the left.
    pasos: list of (step_index 1..5, spoken, [board lines (src, word in spoken)])"""
    sc = scn(mv, name, bg="grid", lead=0.4, transition="wipe")
    F.title(sc, title, at=0.3, size=46)
    st = F.tabbed(F.say_card(enunciado, size=34, max_w=1180, border=("mustard", 3)), "ENUNCIADO", head_bg="mustard",
                  head_color="ink")
    l1 = sc.say(spoken_enunciado)
    put(sc, st, 1230, 236, l1.start(), z=6, rot=0)
    l2 = sc.say("Antes de resolverlo: ¿qué tipo de movimiento es? Piénsalo unos segundos.")
    t_r = F.think(sc, 4.5, x=1830, y=430, r=48)
    sc.say(pista)
    times = [l2.at("qué tipo")]
    done = []
    board_lines = []
    t_clear = None
    lines_spoken = []
    for k, (idx, text, blines) in enumerate(pasos):
        ln = sc.say(text)
        if k == 0:
            t_clear = ln.start()
        lines_spoken.append(ln)
        while len(times) <= idx:
            times.append(ln.start())
        for src, word in blines:
            board_lines.append((src, ln.at(word)))
    lc = sc.say(comprobacion[0])
    while len(times) < len(STEPS):
        times.append(lc.start())
    for src, word in comprobacion[1]:
        board_lines.append((src, lc.at(word)))
    done = [times[k + 1] if k + 1 < len(times) else lc.end(0.2) for k in range(len(STEPS))]
    F.step_list(sc, STEPS, SL_X, SL_Y, times, size=30, w=SL_W, done_times=done)
    # the options (and the check on the right one) leave when the solving starts; then the diagram and the sheet
    pos_ok = option_cards(sc, l2.at("qué tipo"), tipo, until=t_clear - 0.2)
    put(sc, F.check_mark(100), pos_ok[0] + 80, pos_ok[1] - 50, t_r, enter="pop", z=7, until=t_clear - 0.2, exit="pop")
    sc.add(F.sheet(1270, 470, seed=F._seed(name), lines=False), 1240, 700, at=t_clear, enter="drop", rot=0.3, z=3)
    diagram(sc, lines_spoken, lc)
    F.board(sc, board_lines, 640, 500, size=36, gap=20, z=5)
    sc.wait(0.8)
    return sc


# ---------------------------------------------------------------------------- problem 1: MRU
def diag_tren(sc, ls, lc):
    t_ax = ls[0].start()
    tr = F.train_sprite()
    ox, oy = 700.0, 420.0

    def fn(L, t):
        g = prog(t, t_ax, 0.6, "out")
        L.arrow((ox - 30, oy), (ox - 30 + 1150 * g, oy), "ink", 5, head=22)
        if g < 1:
            return
        L.stamp(formula("O", 30), ox, oy + 30)
        L.stamp(formula(r"x\;\t{(m)}", 28), ox + 1140, oy + 32)
        b = prog(t, ls[1].start(), 0.4)
        L.arrow((ox + 420, oy - 60), (ox + 600, oy - 60), "pos", 7, head=24, alpha=b)
        L.stamp(formula(r"+", 40, "pos"), ox + 640, oy - 60, alpha=b)
    mg(sc, fn, at=t_ax, z=8)
    live(sc, lambda t: (tr, ox + 170, oy - 54, 0.0, 0.2), at=ls[0].start(0.4), z=9, jitter=0.4)


def problema_mru(mv):
    resolver(mv, "p-mru", "PROBLEMA 1",
             "Un tren circula por una vía recta a {vel:90 km/h}, sin acelerar. ¿Qué distancia recorre en "
             "{pos:20 minutos}?",
             "Primer problema. Un tren circula por una vía recta a 90 km/h, sin acelerar. ¿Qué distancia recorre en "
             "20 minutos?", "MRU",
             "Es un MRU: la vía es recta y el tren no acelera, así que su velocidad es constante.",
             [(1, "Paso uno: el eje, a lo largo de la vía.", []),
              (2, "Paso dos: el origen, donde está el tren al empezar a contar, y el sentido positivo, hacia donde "
                  "avanza.", []),
              (3, "Paso tres: los datos en el Sistema Internacional. 90 km/h entre 3,6 son 25 m/s. Y 20 minutos, por "
                  "60, son 1200 segundos.",
               [(r"x_0 = 0\quad v = \frac{90}{3,6} = 25\,\t{m/s}\quad t = 20 · 60 = 1200\,\t{s}", "90 km/h")]),
              (4, "Paso cuatro: la ecuación del MRU, equis igual a equis cero más uve por te.",
               [(r"x = x_0 + v\,t", "ecuación")]),
              (5, "Paso cinco: sustituimos. 0 más 25 por 1200: treinta mil metros, es decir, 30 km.",
               [(r"x = 0 + 25 · 1200 = \c{pos}{30\,000\,\t{m} = 30\,\t{km}}", "sustituimos")])],
             ("Paso seis: comprobamos por otro camino. 20 minutos son un tercio de hora, y a 90 km/h, en un tercio de "
              "hora, se recorren 30 km. ¡Lo mismo!",
              [(r"\t{Comprobación: }90\,\t{km/h} · \frac{1}{3}\,\t{h} = 30\,\t{km}\;\t{✓}", "comprobamos")]),
             diag_tren)


# ---------------------------------------------------------------------------- problem 2: MRUA
def diag_coche(sc, ls, lc):
    t_ax = ls[0].start()
    car = F.car_top("mustard", L=110)
    ox, oy = 700.0, 410.0

    def fn(L, t):
        g = prog(t, t_ax, 0.6, "out")
        L.arrow((ox - 30, oy + 30), (ox - 30 + 1150 * g, oy + 30), "ink", 5, head=22)
        if g < 1:
            return
        L.stamp(formula("O", 30), ox, oy + 60)
        L.stamp(formula(r"x\;\t{(m)}", 28), ox + 1140, oy + 62)
        b = prog(t, ls[1].start(), 0.4)
        L.arrow((ox + 300, oy - 50), (ox + 470, oy - 50), "vel", 7, head=24, alpha=b)
        L.stamp(F.tag_img(r"v_0 = +30\,\t{m/s}", 28, "vel_d"), ox + 600, oy - 50, alpha=b)
        c = prog(t, ls[3].start(), 0.4)
        L.arrow((ox + 980, oy - 50), (ox + 880, oy - 50), "acc", 7, head=24, alpha=c)
        L.stamp(F.tag_img(r"a < 0", 28, "acc_d"), ox + 1060, oy - 50, alpha=c)
    mg(sc, fn, at=t_ax, z=8)
    live(sc, lambda t: (car, ox + 60, oy, 0.0), at=ls[0].start(0.4), z=9, jitter=0.4)


def problema_mrua(mv):
    resolver(mv, "p-mrua", "PROBLEMA 2",
             "Un coche va a {vel:108 km/h} y frena hasta pararse en {pos:5 s}. ¿Qué distancia recorre mientras frena?",
             "Segundo problema. Un coche va a 108 km/h y frena hasta pararse en 5 segundos. ¿Qué distancia recorre "
             "mientras frena?", "MRUA",
             "Es un MRUA: su velocidad cambia, de 108 km/h a cero, y frena con aceleración constante.",
             [(1, "Paso uno: el eje, en la dirección de la carretera.", []),
              (2, "Paso dos: el origen, donde empieza a frenar, y el sentido positivo, hacia donde va el coche.", []),
              (3, "Paso tres: los datos. 108 km/h entre 3,6 son 30 m/s. La velocidad final es cero, porque se para. Y "
                  "el tiempo, 5 segundos. La aceleración, todavía no la sabemos.",
               [(r"x_0 = 0\quad v_0 = \frac{108}{3,6} = 30\,\t{m/s}\quad v = 0\quad t = 5\,\t{s}", "108 km/h")]),
              (4, "Paso cuatro: la ecuación. Primero, la aceleración, con uve igual a uve cero más a por te.",
               [(r"v = v_0 + a\,t \;\Rightarrow\; 0 = 30 + 5\,a", "Primero")]),
              (5, "Paso cinco: despejamos. a igual a menos 30 entre 5, menos 6 m/s². Y la distancia, con la ecuación "
                  "de la posición: 30 por 5, menos 3 por 25. 150 menos 75: 75 metros.",
               [(r"a = \frac{−30}{5} = \c{acc}{−6\,\t{m/s}^2}", "despejamos"),
                (r"x = 30 · 5 + \frac{1}{2}(−6) · 5^2 = 150 − 75 = \c{pos}{75\,\t{m}}", "la distancia")])],
             ("Paso seis: comprobamos. La aceleración es negativa, contraria a la velocidad: frena. Tiene sentido. Y "
              "con la ecuación sin tiempo: 30 al cuadrado más 2 por menos 6 por 75 da cero. ¡Se para justo ahí!",
              [(r"\t{Comprobación: }30^2 + 2(−6)(75) = 900 − 900 = 0\;\t{✓}", "ecuación sin tiempo")]),
             diag_coche)


# ---------------------------------------------------------------------------- problem 3: vertical
def diag_pelota(sc, ls, lc):
    t_ax = ls[0].start()
    ball = F.ball_piece(16)
    ox, oy = 760.0, 470.0           # vertical axis: from oy up to 310

    def fn(L, t):
        g = prog(t, t_ax, 0.6, "out")
        L.line([(640, oy), (1880, oy)], "grass_d", 6)
        L.arrow((ox, oy + 6), (ox, oy + 6 - 120 * g), "ink", 5, head=20)
        if g < 1:
            return
        L.stamp(formula("O", 28), ox - 24, oy - 18)
        L.stamp(formula(r"y\,\t{(m)}", 26), ox + 14, oy - 102, "lm")
        b = prog(t, ls[1].start(), 0.4)
        L.arrow((ox - 70, oy - 30), (ox - 70, oy - 110), "pos", 6, head=20, alpha=b)
        L.stamp(formula(r"+", 36, "pos"), ox - 100, oy - 70, alpha=b)
        c = prog(t, ls[2].start(), 0.4)
        L.arrow((ox + 160, oy - 36), (ox + 160, oy - 116), "vel", 6, head=20, alpha=c)
        L.stamp(F.tag_img(r"v_0 = +29,4\,\t{m/s}", 26, "vel_d"), ox + 300, oy - 76, alpha=c)
        L.arrow((ox + 460, oy - 110), (ox + 460, oy - 40), "acc", 6, head=20, alpha=c)
        L.stamp(F.tag_img(r"a = −9,8\,\t{m/s}^2", 26, "acc_d"), ox + 600, oy - 76, alpha=c)
        L.stamp(F.tag_img(r"\t{arriba: }v = 0", 26, "pos_d"), ox + 860, oy - 76, alpha=c)
    mg(sc, fn, at=t_ax, z=8)
    live(sc, lambda t: (ball, ox + 160, oy - 16, 0.0), at=ls[0].start(0.4), z=9, jitter=0.4)


def problema_vertical(mv):
    resolver(mv, "p-vert", "PROBLEMA 3",
             "Se lanza una pelota hacia arriba desde el suelo a {vel:29,4 m/s}. ¿Qué altura máxima alcanza y cuánto "
             "tarda en llegar a ella?",
             "Tercer problema. Se lanza una pelota hacia arriba, desde el suelo, a 29,4 m/s. ¿Qué altura máxima "
             "alcanza, y cuánto tarda en llegar a ella?", "VERTICAL",
             "Es un movimiento vertical: un lanzamiento hacia arriba, solo con la gravedad. Un MRUA con a igual a "
             "menos 9,8.",
             [(1, "Paso uno: el eje, vertical.", []),
              (2, "Paso dos: origen en el suelo, y sentido positivo hacia arriba.", []),
              (3, "Paso tres: los datos con signo. Posición inicial, cero. Velocidad inicial, más 29,4, porque sube. "
                  "Aceleración, menos 9,8. Y la clave: en la altura máxima, la velocidad es cero.",
               [(r"y_0 = 0\quad v_0 = +29,4\,\t{m/s}\quad a = −9,8\,\t{m/s}^2\quad\t{arriba: }v = 0", "Posición")]),
              (4, "Paso cuatro: para el tiempo, uve igual a uve cero más a por te. Para la altura, la ecuación sin "
                  "tiempo.", [(r"v = v_0 + a\,t \qquad v^2 = v_0^2 + 2\,a\,(y − y_0)", "para el tiempo")]),
              (5, "Paso cinco: 0 igual a 29,4 menos 9,8 te: te igual a 3 segundos. Y 0 igual a 29,4 al cuadrado menos "
                  "19,6 por i griega: i griega igual a 44,1 metros.",
               [(r"0 = 29,4 − 9,8\,t \;\Rightarrow\; t = \c{pos}{3\,\t{s}}", "0 igual"),
                (r"0 = 29,4^2 − 19,6\,y \;\Rightarrow\; y = \c{pos}{44,1\,\t{m}}", "al cuadrado")])],
             ("Paso seis: comprobamos con la ecuación de la posición, a los 3 segundos: 29,4 por 3, menos 4,9 por 9. "
              "88,2 menos 44,1: 44,1 metros. ¡Coincide!",
              [(r"\t{Comprobación: }y(3) = 29,4 · 3 − 4,9 · 9 = 44,1\,\t{m}\;\t{✓}", "comprobamos")]),
             diag_pelota)


# ---------------------------------------------------------------------------- the visual cheat sheet
CHULETA = [
    (r"x = x_0 + v\,t", "¿La velocidad es constante?", "MRU",
     "Si la velocidad es constante: equis igual a equis cero más uve te."),
    (r"v = v_0 + a\,t", "¿No aparece la posición?", "MRUA",
     "Si no te dan ni te piden la posición: uve igual a uve cero más a te."),
    (r"x = x_0 + v_0\,t + \frac{1}{2}\,a\,t^2", "¿No aparece la velocidad final?", "MRUA",
     "Si no aparece la velocidad final: la ecuación de la posición."),
    (r"v^2 = v_0^2 + 2\,a\,(x − x_0)", "¿No aparece el tiempo?", "MRUA",
     "Si no aparece el tiempo: uve al cuadrado igual a uve cero al cuadrado más dos a por el desplazamiento."),
    (r"x_A = x_B", "¿Cuándo y dónde se encuentran?", "2 móviles",
     "Si te preguntan cuándo y dónde se encuentran dos móviles: un eje, un reloj, e igualar las posiciones."),
    (r"a = −9,8\,\t{m/s}^2\quad\t{(arriba: }v = 0\t{)}", "¿Sube o cae, solo con la gravedad?", "vertical",
     "Si sube o cae solo con la gravedad: a igual a menos 9,8, y en lo más alto, velocidad cero."),
    (r"\t{km/h} ÷ 3,6 = \t{m/s}", "¿Están las unidades en el SI?", "unidades",
     "Y antes de nada: ¿están las unidades en el Sistema Internacional? Los km/h, entre 3,6."),
]


def chuleta(mv):
    sc = scn(mv, "chuleta", bg="kraft", lead=0.4, transition="wipe")
    F.title(sc, "CHULETA FINAL: ¿QUÉ PREGUNTA ME LLEVA A CADA FÓRMULA?", at=0.3, y=130, size=40)
    l0 = sc.say("Y para terminar, la chuleta. Cada fórmula, con la pregunta que te lleva a ella.")
    y = 230
    for k, (src, q, tag, spoken) in enumerate(CHULETA):
        ln = sc.say(spoken)
        qc = F.say_card(q, size=32, border=("mustard", 3), max_w=700)
        fc = F.fcard(src, size=36 if k != 2 else 32, border=("pos", 3), min_w=640)
        put(sc, qc, 520, y, ln.start(), enter="slide_l", z=5, rot=0)
        put(sc, F.formula_card(r"\t{→}", 40, bg="kraft"), 905, y, ln.start(0.2), enter="pop", z=5, rot=0)
        put(sc, fc, 1290, y, ln.start(0.3), enter="slide_r", z=5, rot=0)
        put(sc, card(tag, size=26, font_name="body9", bg="mustard", pad=(12, 4), seed=900 + k), 1720, y, ln.start(0.5),
            enter="pop", z=6, rot=3)
        y += 92
    sc.say("Si quieres, pausa el vídeo y cópiala en tu cuaderno.")
    sc.wait(2.5)
    sc = scn(mv, "control", bg="grid", lead=0.4)
    F.title(sc, "ANTES DE ENTREGAR", at=0.3)
    l1 = sc.say("Y antes de entregar, un último control de cuatro preguntas.")
    checks = [("¿Están todas las unidades en el Sistema Internacional?", "unidades"),
              ("¿Los signos son coherentes con el eje que elegiste?", "signos"),
              ("¿Has usado la ecuación adecuada?", "ecuación"),
              ("¿Respondes exactamente a lo que te preguntan?", "Respondes")]
    y = 330
    for q, w in checks:
        ln = sc.say(q)
        put(sc, kit.icon_card(q, "check-mark", med_bg="space_l", size=40, max_w=1200, min_w=1200), W / 2, y,
            ln.start(), enter="slide_r", z=5)
        y += 150
    sc.wait(0.6)


def build(only=None):
    mv = K.new_movie()
    parts = [("intro", intro), ("metodo", metodo), ("p1", problema_mru), ("p2", problema_mrua),
             ("p3", problema_vertical), ("chuleta", chuleta),
             ("fin", lambda m: K.fin(m, 5, "Cinemática: ¡bloque terminado!",
                                     "Fin del tema cinco, y del bloque de cinemática. Repasa la chuleta, practica con "
                                     "problemas, y aplica siempre el método. ¡Mucho ánimo!"))]
    for name, fn in parts:
        if only and name not in only:
            continue
        fn(mv)
    return mv


def chapters(mv):
    names = {"title": "Inicio", "metodo": "1 · El método", "p-mru": "2 · Problema MRU", "p-mrua": "3 · Problema MRUA",
             "p-vert": "4 · Problema vertical", "chuleta": "5 · Chuleta final", "control": "6 · Antes de entregar"}
    return [(st, names[sc.name]) for sc, st in zip(mv.scenes, mv.starts) if sc.name in names]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "out/Cinematica_T5_Metodo_examen.mp4"
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

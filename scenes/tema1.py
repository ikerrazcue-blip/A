"""Filosofía 1º Bachillerato · Tema 1: Introducción — vídeo completo (stop-motion griego).

Contenido: temario estándar del Tema 1 (el .docx de los apuntes llegó cifrado y no se pudo leer).
    python3 scenes/tema1.py out/tema1.mp4             # vídeo completo
    python3 scenes/tema1.py out/tema1.mp4 --stills    # fotogramas de control
"""
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stopmo import greek, kit, movie  # noqa: E402
from stopmo.gfx import W, card  # noqa: E402
from stopmo.kit import TITLE_Y  # noqa: E402
from stopmo.movie import Movie  # noqa: E402

# how the narrator must read some words (display text keeps the proper spelling)
movie.PRONOUNCE.update({
    r"\bsiglo XVIII\b": "siglo dieciocho", r"\bsiglo XVII\b": "siglo diecisiete", r"\bsiglo XX\b": "siglo veinte",
    r"\bsiglo VIII\b": "siglo octavo", r"\bsiglo VII\b": "siglo séptimo", r"\bsiglo VI\b": "siglo sexto",
    r"\bsiglo IV\b": "siglo cuarto", r"\bsiglo V\b": "siglo quinto",
    r"2\.600": "dos mil seiscientos", r"\bJaspers\b": "Yáspers", r"\bsapere aude\b": "sápere áude",
    r"\bSapere aude\b": "Sápere áude", r"\bcogito, ergo sum\b": "cógito, ergo sum", r"\bradix\b": "rádix",
    r"«|»": "",
})


def rot_of(text, amp=2.4):
    return ((zlib.crc32(text.encode()) % 1000) / 1000 - 0.5) * amp


def title(sc, text, at=None, size=56, **kw):
    t = kit.title_card(text, size=size)
    return sc.add(t, W / 2, TITLE_Y, at=sc.now() if at is None else at, enter="drop", rot=rot_of(text, 1.6), **kw)


def put(sc, spr, x, y, at, enter="drop", **kw):
    kw.setdefault("rot", rot_of(f"{x:.0f}|{y:.0f}|{at:.2f}", 2.6))
    return sc.add(spr, x, y, at=at, enter=enter, **kw)


def scn(mv, name, **kw):
    kw.setdefault("transition", "cut")
    kw.setdefault("sweep", True)
    return mv.scene(name, **kw)


# ============================================================================
# 0. título e índice
# ============================================================================
SECTIONS = [("Α", "¿Qué es la filosofía?"), ("Β", "¿Dónde y cuándo nació?"), ("Γ", "Del mito al logos"),
            ("Δ", "Los primeros filósofos"), ("Ε", "¿Por qué filosofamos?"), ("Ζ", "La filosofía y otros saberes"),
            ("Η", "Las ramas de la filosofía"), ("Θ", "¿Para qué sirve?")]


def intro(mv):
    kit.title_scene(mv, "FILOSOFÍA", "Tema 1 · Introducción", narration="Filosofía. Tema uno: introducción.")
    sc = mv.scene("indice", transition="wipe")
    title(sc, "EL MAPA DEL TEMA", at=0.5)
    l1 = sc.say("Este es el mapa del tema: ocho paradas, numeradas con letras griegas.")
    l2 = sc.say("Veremos qué es la filosofía, dónde y cuándo nació, el paso del mito al logos, "
                "los primeros filósofos, por qué filosofamos, en qué se diferencia de otros saberes, "
                "sus ramas y para qué sirve.")
    l3 = sc.say("Y al final, un repaso de todo. ¡Vamos allá!")
    keys = ["qué es", "dónde", "mito", "primeros", "por qué", "diferencia", "ramas", "sirve"]
    for i, ((letter, name), k) in enumerate(zip(SECTIONS, keys)):
        col, row = i // 4, i % 4
        x = 520 + col * 860
        y = 300 + row * 150
        medal = kit.greek_letter_medal(letter, diam=112, seed=100 + i)
        lab = card(name, size=40, font_name="body9", bg="cream", pad=(26, 10), seed=120 + i, min_w=520)
        piece = kit.compose([(lab, 60 + lab.w / 2 - 20, 0), (medal, 0, 0)])
        t = l2.at(k) if i else l2.start()
        put(sc, piece, 520 + col * 880, y, at=t, enter="slide_r" if col else "slide_l")
    owl = sc.owl(W - 170, 860, scale=0.42, at=l3.start(), enter="slide_u", z=6)
    owl.mood(l3.at("Vamos"), "wow", "wide")
    sc.wait(0.4)
    sc.sweep = True
    sc.transition = "wipe"


# ============================================================================
# Α. ¿Qué es la filosofía?
# ============================================================================
def seccion_alfa(mv):
    kit.section_scene(mv, "Α", "¿Qué es la filosofía?", narration="Primera parada: ¿qué es la filosofía?")

    # --- A1: la palabra
    sc = scn(mv, "a1", transition="wipe")
    title(sc, "UNA PALABRA GRIEGA", at=0.5)
    l1 = sc.say("Empecemos por la palabra. «Filosofía» viene del griego y tiene dos partes.")
    l2 = sc.say("{terra:Filo} viene de {greek:φίλος}, que significa {terra:amor} o amistad.",
                tts="Filo viene de fílos, que significa amor o amistad.")
    filo = kit.compose([(card("FILO", size=96, font_name="title", bg="terra", color="cream", pad=(44, 14), seed=201),
                         0, 0),
                        (card("φίλος · amor", size=44, font_name="greek", bg="cream", color="terra", pad=(22, 6),
                              seed=202), 0, 110, -3)])
    heart = greek.medallion(150, "hearts", bg="terra_l", seed=203)
    e_filo = put(sc, filo, 600, 430, l2.start(), rot=-2)
    e_h = put(sc, heart, 600, 700, l2.at("amor"), enter="pop")
    l3 = sc.say("{gold:Sofía} viene de {greek:σοφία}, que significa {gold:sabiduría}.",
                tts="Sofía viene de sofía, que significa sabiduría.")
    sofia = kit.compose([(card("SOFÍA", size=96, font_name="title", bg="gold", color="black", pad=(44, 14),
                               seed=204), 0, 0),
                         (card("σοφία · sabiduría", size=44, font_name="greek", bg="cream", color="terra",
                               pad=(22, 6), seed=205), 0, 110, 2)])
    owlmed = greek.medallion(150, "classical-knowledge", bg="gold_l", seed=206)
    e_sof = put(sc, sofia, 1320, 430, l3.start(), rot=2)
    e_o = put(sc, owlmed, 1320, 700, l3.at("sabiduría"), enter="pop")
    l4 = sc.say("Así que filosofía significa, literalmente, {gold:amor a la sabiduría}.")
    e_filo.move(l4.start(), x=760, dur=0.5)
    e_sof.move(l4.start(), x=1160, dur=0.5)
    e_h.leave(l4.start(), "pop", 0.3)
    e_o.leave(l4.start(), "pop", 0.3)
    res = card("= AMOR A LA SABIDURÍA", size=64, font_name="title", bg="cream", color="black", pad=(50, 18),
               border=("gold", 5), seed=207)
    e_r = put(sc, res, 960, 720, l4.at("amor"), rot=-1)
    e_r.pulse(l4.end(-0.3), 0.06)

    # --- A2: Pitágoras
    sc = scn(mv, "a2")
    title(sc, "¿QUIÉN USÓ LA PALABRA POR PRIMERA VEZ?", at=0.4, size=50)
    l1 = sc.say("Según la tradición, el primero en llamarse a sí mismo filósofo fue {gold:Pitágoras}.")
    put(sc, kit.person("Pitágoras", sub="siglo VI a. C.", diam=200, seed=211), 380, 560, l1.at("Pitágoras"))
    l2 = sc.say("Le preguntaron si era un sabio, y respondió que no: sabios, solo los dioses.")
    put(sc, greek.bubble("¡No soy un sabio!", size=46, font_name="body9", seed=212, tail="left"), 700, 300,
        l2.at("respondió"), enter="pop")
    sabio = kit.icon_card("{b:SABIO} ({greek:σοφός}): el que ya lo sabe todo.\nSolo los dioses.", "wisdom",
                          med_bg="gold_l", size=38, max_w=720, seed=213)
    put(sc, sabio, 1300, 430, l2.at("sabios"), enter="slide_r")
    l3 = sc.say("Él era un {gold:filósofo}: alguien que no tiene la sabiduría, pero la {gold:ama} y la {gold:busca}.")
    filo = kit.icon_card("{b:FILÓSOFO} ({greek:φιλόσοφος}): el que {terra:ama} y {terra:busca} la sabiduría.",
                         "magnifying-glass", med_bg="terra_l", size=38, max_w=720, seed=214)
    put(sc, filo, 1300, 680, l3.at("filósofo"), enter="slide_r")

    # --- A3: los Juegos Olímpicos
    sc = scn(mv, "a3")
    title(sc, "LA COMPARACIÓN DE LOS JUEGOS OLÍMPICOS", at=0.4, size=50)
    l1 = sc.say("Pitágoras lo explicó con una comparación: los {gold:Juegos Olímpicos}.")
    put(sc, greek.laurel(150, seed=221), W / 2, 280, l1.at("Juegos"), enter="pop", rot=0)
    l2 = sc.say("A los juegos van tres tipos de personas.")
    cols = [(420, "run", "terra_l", "Van a {b:competir}", "GLORIA", "terra"),
            (960, "coins", "gold_l", "Van a {b:comprar y vender}", "DINERO", "gold"),
            (1500, "eye-target", "blue_l", "Van a {b:mirar}", "VERDAD", "blue")]
    l3 = sc.say("Unos van a competir: buscan la {terra:gloria}.")
    l4 = sc.say("Otros van a comprar y vender: buscan el {terra:dinero}.")
    l5 = sc.say("Y otros van solo a mirar, porque quieren {blue:entender} lo que pasa.")
    ls = [l3, l4, l5]
    for (x, ic, bg, txt, goal, gc), ln in zip(cols, ls):
        put(sc, greek.medallion(190, ic, bg=bg, seed=int(x)), x, 450, ln.start(), enter="pop")
        put(sc, card(txt, size=38, bg="cream", pad=(24, 10), seed=int(x) + 1), x, 610, ln.start(0.3))
        put(sc, card(goal, size=44, font_name="title", bg=gc, color="cream" if gc != "gold" else "black",
                     pad=(26, 10), seed=int(x) + 2), x, 710, ln.end(-0.6), enter="pop")
    l6 = sc.say("Los filósofos son como esos espectadores: no buscan fama ni riqueza, buscan la {gold:verdad}.")
    put(sc, card("= LOS FILÓSOFOS", size=44, font_name="title", bg="cream", border=("gold", 4), pad=(26, 10),
                 seed=229), 1500, 815, l6.at("espectadores"), enter="drop")

    # --- A4: definición
    sc = scn(mv, "a4")
    title(sc, "ENTONCES, ¿QUÉ ES LA FILOSOFÍA?", at=0.4)
    l1 = sc.say("Hoy podemos definirla así: la filosofía es un {gold:saber racional y crítico} "
                "que busca responder a las preguntas más profundas.")
    dfn = card("La filosofía es un {gold_d|b:saber racional y crítico} que busca responder\n"
               "a las {terra|b:preguntas más profundas} sobre la realidad y sobre nosotros.",
               size=44, bg="cream", border=("gold", 5), pad=(50, 26), max_w=1500, seed=241)
    put(sc, dfn, W / 2, 350, l1.at("filosofía es"), rot=-0.8)
    l2 = sc.say("Preguntas como: ¿qué es la realidad? ¿Qué puedo conocer? ¿Cómo debo vivir? ¿Quién soy yo?")
    qs = [("¿Qué es la realidad?", "world", 470, 590, "realidad"), ("¿Qué puedo conocer?", "magnifying-glass",
                                                                      1250, 590, "conocer"),
          ("¿Cómo debo vivir?", "scales", 600, 780, "vivir"), ("¿Quién soy yo?", "person", 1380, 780, "Quién")]
    for q, ic, x, y, k in qs:
        put(sc, kit.icon_card(q, ic, med_bg="gold_l", size=42, seed=zlib.crc32(q.encode()) % 900), x, y,
            l2.at(k, after=-0.3), enter="drop")

    # --- A5: cuatro rasgos
    sc = scn(mv, "a5")
    title(sc, "CUATRO RASGOS DEL SABER FILOSÓFICO", at=0.4, size=52)
    l1 = sc.say("Este saber tiene cuatro rasgos que tienes que conocer.")
    feats = [("{b:RACIONAL}\nargumentos, no fe ni autoridad", "brain", 540, 380),
             ("{b:CRÍTICO}\nlo examina todo antes de aceptarlo", "magnifying-glass", 1380, 380),
             ("{b:RADICAL}\nva a la raíz de los problemas", "tree-roots", 540, 650),
             ("{b:UNIVERSAL}\nquiere entender la realidad entera", "world", 1380, 650)]
    lines = [
        sc.say("Es {terra:racional}: se basa en argumentos, no en la fe, ni en la tradición, "
               "ni en lo que diga una autoridad."),
        sc.say("Es {terra:crítico}: no acepta nada sin examinarlo antes, aunque lo diga todo el mundo."),
        sc.say("Es {terra:radical}: va a la raíz de las cosas, a las preguntas más profundas. "
               "Radical viene del latín radix, que significa raíz."),
        sc.say("Y es {terra:universal}, o totalizador: quiere entender la realidad en su conjunto, "
               "no solo un trocito, como hace cada ciencia."),
    ]
    for (txt, ic, x, y), ln in zip(feats, lines):
        put(sc, kit.icon_card(txt, ic, med_bg="terra_l", size=38, max_w=620, min_w=560, seed=x + y), x, y,
            ln.start(), enter="slide_l" if x < 900 else "slide_r")

    # --- A6: no se aprende filosofía, se aprende a filosofar
    sc = scn(mv, "a6")
    owl = sc.owl(250, 690, scale=0.7, at=0.4, enter="slide_l", z=6)
    l1 = sc.say("Un detalle importante: la filosofía {terra:no} es una lista de respuestas para memorizar.")
    put(sc, kit.ojo("La filosofía {red|b:no} es una lista de respuestas:\nes una forma de {b:pensar}.", size=42,
                    max_w=1100), 1060, 290, l1.start(), rot=-1)
    l2 = sc.say("Muchas de sus preguntas siguen abiertas desde hace siglos, y cada época vuelve a pensarlas.")
    l3 = sc.say("Por eso {gold:Kant} decía que no se puede aprender filosofía: solo se puede aprender a "
                "{gold:filosofar}, es decir, a pensar por uno mismo.")
    q = kit.quote("«No se puede aprender filosofía;\nsolo se puede aprender a filosofar.»", "— Immanuel Kant",
                  size=46)
    put(sc, q, 1060, 640, l3.at("Kant"), rot=1)
    owl.mood(l3.at("filosofar"), "wow", "wide")

    kit.key_idea(mv, "Filosofía = {gold_d:amor a la sabiduría}.\nUn saber {terra:racional}, {terra:crítico}, "
                 "{terra:radical}\ny {terra:universal}.",
                 "Idea clave: filosofía significa amor a la sabiduría. Es un saber racional, crítico, radical y "
                 "universal.",
                 tts="Idea clave: filosofía significa amor a la sabiduría. Es racional, es crítico, es radical y es "
                     "universal.")


# ============================================================================
# Β. ¿Dónde y cuándo nació?
# ============================================================================
def seccion_beta(mv):
    kit.section_scene(mv, "Β", "¿Dónde y cuándo nació?",
                      narration="Segunda parada: ¿dónde y cuándo nació la filosofía?")
    sc = scn(mv, "b1", transition="wipe")
    title(sc, "GRECIA, SIGLO VI ANTES DE CRISTO", at=0.5)
    mp, proj = greek.aegean_map(760, seed=301)
    cx, cy = 520, 560
    l1 = sc.say("La filosofía nació en la antigua {gold:Grecia}, en el {gold:siglo VI antes de Cristo}: "
                "hace unos 2.600 años.")
    put(sc, mp, cx, cy, l1.start(), enter="drop", rot=-1.2)
    gx, gy = proj(21.9, 39.5)
    put(sc, card("GRECIA", size=38, font_name="title", bg="cream", pad=(20, 6), seed=302), cx + gx, cy + gy,
        l1.at("Grecia"), enter="pop")
    put(sc, card("hace unos 2.600 años", size=44, font_name="body9", bg="gold", pad=(30, 12), seed=303),
        1420, 300, l1.at("hace"), enter="drop")
    l2 = sc.say("Pero no en Atenas, como mucha gente cree, sino en {gold:Mileto}: una ciudad griega de la región de "
                "{gold:Jonia}, en la costa de la actual Turquía.")
    ax, ay = proj(23.73, 37.98)
    put(sc, greek.big_glyph("●", 22, "black", font_name="sym", seed=304), cx + ax, cy + ay, l2.at("Atenas"),
        enter="pop", rot=0)
    put(sc, card("Atenas", size=28, font_name="body9", bg="cream", pad=(12, 4), seed=305), cx + ax - 62,
        cy + ay + 30, l2.at("Atenas"), enter="pop")
    mx, my = proj(27.28, 37.53)
    star = put(sc, greek.big_glyph("★", 62, "red", font_name="sym", seed=306), cx + mx, cy + my, l2.at("Mileto"),
               enter="pop", rot=0, z=3)
    star.pulse(l2.at("Mileto", after=0.5), 0.3).pulse(l2.at("Jonia"), 0.25)
    put(sc, card("MILETO", size=34, font_name="title", bg="red", color="cream", pad=(16, 6), seed=307),
        cx + mx + 40, cy + my + 58, l2.at("Mileto"), enter="pop", z=3)
    jx, jy = proj(28.7, 38.9)
    put(sc, card("JONIA", size=34, font_name="title", bg="gold", pad=(16, 6), seed=308), cx + jx, cy + jy,
        l2.at("Jonia"), enter="pop")
    put(sc, kit.icon_card("Hoy: costa de {b:Turquía}", "compass", med_bg="blue_l", size=36, seed=309), 1420, 470,
        l2.at("Turquía", after=-0.3), enter="slide_r")
    l3 = sc.say("Allí vivía {gold:Tales de Mileto}, al que se considera el {gold:primer filósofo}.")
    put(sc, kit.person("Tales de Mileto", sub="el primer filósofo", diam=190, seed=311), 1420, 720,
        l3.at("Tales"))

    sc = scn(mv, "b2")
    title(sc, "¿POR QUÉ ALLÍ? CUATRO CAUSAS", at=0.4)
    l1 = sc.say("¿Y por qué nació allí y no en otro sitio? Por varias causas que se juntaron.")
    causes = [("{b:COMERCIO}\nbarcos, viajeros y otros mitos", "galley", "blue_l", 540, 350),
              ("{b:LA POLIS}\ndebate público en el ágora", "conversation", "gold_l", 1380, 350),
              ("{b:RELIGIÓN SIN DOGMAS}\nni libro sagrado ni verdad única", "open-book", "purple_l", 540, 600),
              ("{b:OCIO}\ntiempo libre para pensar", "sundial", "olive_l", 1380, 600)]
    l2 = sc.say("Primera: el {terra:comercio}. Mileto era un puerto lleno de barcos, mercancías y viajeros.")
    l3 = sc.say("Al conocer otros pueblos, los griegos vieron que cada uno tenía mitos distintos para explicar "
                "lo mismo. Y surgió la pregunta: ¿cuál es la verdad?")
    l4 = sc.say("Segunda: la {terra:polis}. Cada ciudad griega discutía sus asuntos en público, en la plaza, "
                "el {terra:ágora}. Estaban acostumbrados a argumentar y a convencer con razones.")
    l5 = sc.say("Tercera: una {terra:religión sin dogmas ni libros sagrados}. No había sacerdotes que impusieran "
                "una verdad única, así que había libertad para pensar.")
    l6 = sc.say("Y cuarta: el {terra:ocio}, es decir, tiempo libre. Algunos no tenían que trabajar todo el día "
                "y podían dedicarse a pensar.")
    for (txt, ic, bg, x, y), ln in zip(causes, [l2, l4, l5, l6]):
        put(sc, kit.icon_card(txt, ic, med_bg=bg, size=38, max_w=640, min_w=580, seed=x + y + 7), x, y,
            ln.start(), enter="slide_l" if x < 900 else "slide_r")
    l7 = sc.say("Curiosidad: en griego, ocio se decía {greek:σχολή}. ¡De ahí viene nuestra palabra "
                "{terra:escuela}!",
                tts="Curiosidad: en griego, ocio se decía escolé. ¡De ahí viene nuestra palabra escuela!")
    cur = kit.icon_card("{greek:σχολή} (ocio)  →  {b:escuela}", "school-bag", med_bg="terra_l", size=44, seed=331)
    put(sc, cur, W / 2, 800, l7.start(), enter="drop", z=5)

    kit.key_idea(mv, "Nació en {gold_d:Grecia}, en {gold_d:Mileto} (Jonia),\nen el {gold_d:siglo VI a. C.}, "
                 "con {gold_d:Tales}.",
                 "Idea clave: la filosofía nació en Grecia, en Mileto, en el siglo VI antes de Cristo, con Tales. "
                 "Y la ayudaron cuatro causas: el comercio, la polis, el ocio y una religión sin dogmas ni libros "
                 "sagrados.")


# ============================================================================
# Γ. Del mito al logos
# ============================================================================
def seccion_gamma(mv):
    kit.section_scene(mv, "Γ", "Del mito al logos", narration="Tercera parada: el paso del mito al logos.")

    sc = scn(mv, "g1", transition="wipe")
    title(sc, "ANTES: EL MITO", at=0.5)
    l1 = sc.say("Antes de la filosofía, los griegos explicaban el mundo con {purple:mitos}.")
    put(sc, greek.medallion(250, "drama-masks", bg="purple_l", seed=401), 430, 420, l1.at("mitos"), enter="pop")
    l2 = sc.say("Un mito es un {purple:relato tradicional}, contado de generación en generación, que explica cómo es "
                "el mundo y por qué pasan las cosas a través de {purple:dioses} y fuerzas sobrenaturales.")
    dfn = card("{purple|b:MITO}: relato tradicional que explica el mundo\ncon {b:dioses} y fuerzas "
               "{b:sobrenaturales}.", size=40, bg="cream", border=("purple", 4), pad=(40, 20), max_w=1000,
               seed=402)
    put(sc, dfn, 1200, 380, l2.start(), rot=1)
    l3 = sc.say("Los grandes narradores de mitos fueron dos poetas: {purple:Homero}, autor de la Ilíada y la Odisea, "
                "y {purple:Hesíodo}, que en su Teogonía contó el origen de los dioses.")
    put(sc, kit.person("Homero", icon="quill-ink", bg="purple_l", sub="Ilíada y Odisea", diam=160, seed=403),
        1000, 700, l3.at("Homero"))
    put(sc, kit.person("Hesíodo", icon="scroll-unfurled", bg="purple_l", sub="Teogonía", diam=160, seed=404),
        1450, 700, l3.at("Hesíodo"))

    sc = scn(mv, "g2")
    title(sc, "¿CÓMO EXPLICA EL MITO?", at=0.4)
    put(sc, greek.medallion(230, "wisdom", bg="purple_l", seed=411), 300, 520, 0.6, enter="pop")
    l1 = sc.say("Por ejemplo: ¿por qué hay tormentas? Porque {purple:Zeus}, el rey de los dioses, está enfadado "
                "y lanza rayos.")
    rows = [("Tormenta  →  {purple|b:Zeus} enfadado lanza rayos", "lightning-storm", 330)]
    put(sc, kit.icon_card(rows[0][0], rows[0][1], med_bg="purple_l", size=40, max_w=900, seed=412), 1060, 330,
        l1.at("tormentas", after=-0.2), enter="slide_r")
    l2 = sc.say("¿Por qué hay terremotos y el mar se agita? Porque {purple:Poseidón} golpea la tierra con su "
                "tridente.")
    put(sc, kit.icon_card("Terremoto  →  {purple|b:Poseidón} golpea con su tridente", "trident", med_bg="purple_l",
                          size=40, max_w=900, seed=413), 1060, 520, l2.at("terremotos", after=-0.2),
        enter="slide_r")
    l3 = sc.say("¿Y por qué llega el invierno? Porque {purple:Hades}, dios del inframundo, raptó a Perséfone, "
                "y cada año ella debe pasar unos meses con él.")
    l4 = sc.say("Mientras, su madre {purple:Deméter}, diosa de las cosechas, está triste, y la tierra no da frutos.")
    put(sc, kit.icon_card("Invierno  →  {purple|b:Deméter} está triste sin su hija", "snowflake-1",
                          med_bg="purple_l", size=40, max_w=900, seed=414), 1060, 710, l3.at("invierno", after=-0.2),
        enter="slide_r")

    sc = scn(mv, "g3")
    title(sc, "RASGOS DEL MITO", at=0.4)
    l1 = sc.say("Fíjate en cómo funciona el mito.")
    feats = [("{b:DIOSES COMO PERSONAS}\n= {purple|b:antropomorfismo}", "wisdom", 540, 370, "antropomorfismo"),
             ("{b:CAPRICHO}\nel mundo es imprevisible", "dice-six-faces-five", 1380, 370, "capricho"),
             ("{b:FANTASÍA}\nlo sobrenatural, lenguaje poético", "star-swirl", 540, 620, "fantasía"),
             ("{b:TRADICIÓN}\nno se discute: se acepta", "tied-scroll", 1380, 620, "tradición")]
    lns = [sc.say("Explica la naturaleza con dioses que se comportan como personas: se enfadan, se enamoran, "
                  "se vengan. A esto se le llama {purple:antropomorfismo}."),
           sc.say("Todo depende de su voluntad y de su {purple:capricho}, así que el mundo es imprevisible."),
           sc.say("Usa la {purple:fantasía} y lo sobrenatural, con un lenguaje poético y simbólico."),
           sc.say("Y no se discute: se acepta por {purple:tradición}, porque siempre se ha contado así.")]
    for (txt, ic, x, y, _), ln in zip(feats, lns):
        put(sc, kit.icon_card(txt, ic, med_bg="purple_l", size=38, max_w=640, min_w=580, seed=x + y + 3), x, y,
            ln.start(), enter="slide_l" if x < 900 else "slide_r")

    sc = scn(mv, "g4")
    title(sc, "DESPUÉS: EL LOGOS", at=0.4)
    l1 = sc.say("Los primeros filósofos dieron un giro enorme: pasaron del mito al {blue:logos}, es decir, "
                "a la razón.")
    put(sc, greek.medallion(220, "light-bulb", bg="blue_l", seed=441), 420, 390, l1.at("logos"), enter="pop")
    l2 = sc.say("{greek:λόγος}, logos, es una palabra griega que significa {blue:razón}, palabra y argumento.",
                tts="Logos es una palabra griega que significa razón, palabra y argumento.")
    put(sc, card("λόγος", size=70, font_name="greek", bg="cream", color="blue", pad=(30, 4), seed=442), 420, 580,
        l2.start(), enter="drop")
    put(sc, card("razón · palabra · argumento", size=36, font_name="body9", bg="blue", color="cream", pad=(22, 8),
                 seed=443), 420, 690, l2.at("razón"), enter="pop")
    l3 = sc.say("Explicar con el logos es buscar {blue:causas naturales}. El rayo ya no es el enfado de Zeus: es algo "
                "que ocurre en las nubes, y se puede estudiar.")
    put(sc, kit.icon_card("{b:CAUSAS NATURALES}, no dioses", "sun-cloud", med_bg="blue_l", size=38, max_w=640,
                          min_w=600, seed=444), 1260, 330, l3.at("causas"), enter="slide_r")
    l4 = sc.say("El mundo deja de ser un caos caprichoso y se ve como un {blue:cosmos}: un todo ordenado, que sigue "
                "{blue:leyes} y que la razón puede entender.")
    put(sc, kit.icon_card("De {b:CAOS} a {b:COSMOS}: orden y leyes", "ringed-planet", med_bg="blue_l", size=38,
                          max_w=760, min_w=600, seed=445), 1260, 520, l4.at("cosmos", after=-0.2), enter="slide_r")
    l5 = sc.say("Y como se basa en razones, cualquiera puede {blue:criticar} una explicación y proponer otra mejor. "
                "Así nace el debate.")
    put(sc, kit.icon_card("Se puede {b:CRITICAR} y debatir", "conversation", med_bg="blue_l", size=38, max_w=640,
                          min_w=600, seed=446), 1260, 710, l5.at("criticar", after=-0.2), enter="slide_r")

    sc = scn(mv, "g5")
    title(sc, "MITO  vs  LOGOS", at=0.4)
    hm = kit.header("MITO", bg="purple", size=48)
    hl = kit.header("LOGOS", bg="blue", size=48)
    l1 = sc.say("Comparémoslos, punto por punto.")
    put(sc, hm, 860, 265, l1.start(0.2), enter="pop")
    put(sc, hl, 1440, 265, l1.start(0.5), enter="pop")
    rows = [("¿Con qué explica?", "con {purple|b:dioses}", "con {blue|b:causas naturales}",
             "El mito explica con {purple:dioses}; el logos, con {blue:causas naturales}."),
            ("¿Qué manda?", "el {purple|b:capricho}", "{blue|b:leyes} y orden",
             "En el mito manda el {purple:capricho}; en el logos, las {blue:leyes} y el orden."),
            ("¿Por qué se acepta?", "por {purple|b:tradición}", "por {blue|b:razones}: se discute",
             "El mito se acepta por {purple:tradición}; el logos, por {blue:razones}, y se puede discutir."),
            ("¿Qué usa?", "la {purple|b:fantasía}", "la {blue|b:razón} y la observación",
             "El mito usa la {purple:fantasía}; el logos, la {blue:razón} y la observación.")]
    for i, (q, a, b, spoken) in enumerate(rows):
        y = 380 + i * 128
        ln = sc.say(spoken)
        put(sc, kit.cell(q, bg="paper2", size=34, min_w=340, max_w=380), 330, y, ln.start(), enter="slide_l")
        put(sc, kit.cell(a, size=36, min_w=460, max_w=520), 860, y, ln.start(0.2))
        put(sc, kit.cell(b, size=36, min_w=520, max_w=560), 1440, y, ln.at("logos") if "logos" in spoken else
            ln.start(1.2))

    sc = scn(mv, "g6")
    owl = sc.owl(230, 700, scale=0.6, at=0.4, enter="slide_l", z=6)
    l1 = sc.say("Ojo con un detalle importante: el paso del mito al logos {terra:no fue de golpe}.")
    put(sc, kit.ojo("El paso del mito al logos {red|b:no fue de golpe}: fue {b:lento}.", size=44, max_w=1100),
        1030, 300, l1.start(), rot=-1)
    owl.mood(l1.at("golpe"), "doubt", "open", (0.6, 0))
    l2 = sc.say("Fue un proceso lento, y durante mucho tiempo mito y logos {terra:convivieron}. Los primeros "
                "filósofos todavía mezclaban ideas míticas, e incluso {gold:Platón} usaba mitos para explicar sus "
                "teorías.")
    put(sc, card("MITO", size=56, font_name="title", bg="purple", color="cream", pad=(30, 10), seed=461), 620, 560,
        l2.start(), enter="slide_l")
    put(sc, greek.arrow(420, thick=30, color="terra", seed=462), 1010, 560, l2.start(0.4), enter="slide_l", rot=0)
    put(sc, card("poco a poco", size=34, font_name="body9", bg="cream", pad=(18, 6), seed=463), 1010, 480,
        l2.start(0.8), enter="pop")
    put(sc, card("LOGOS", size=56, font_name="title", bg="blue", color="cream", pad=(30, 10), seed=464), 1400, 560,
        l2.start(1.0), enter="slide_r")
    put(sc, kit.icon_card("Incluso {b:Platón} usaba mitos", "philosopher-bust", med_bg="gold_l", size=36,
                          seed=465), 1010, 700, l2.at("Platón"), enter="drop")
    l3 = sc.say("Y el mito no ha desaparecido: también hoy contamos historias para dar sentido a las cosas.")
    owl.mood(l3.start(), "calm")

    kit.key_idea(mv, "{purple:Mito}: dioses, capricho y tradición.\n{blue:Logos}: razón, causas naturales y leyes.\n"
                 "Un paso {terra:lento}.",
                 "Idea clave: el mito explica el mundo con dioses, capricho y tradición. El logos, con la razón, "
                 "causas naturales y leyes. Y el paso de uno a otro fue lento.")


# ============================================================================
# Δ. Los primeros filósofos
# ============================================================================
def seccion_delta(mv):
    kit.section_scene(mv, "Δ", "Los primeros filósofos", narration="Cuarta parada: los primeros filósofos.")

    sc = scn(mv, "d1", transition="wipe")
    title(sc, "LA PREGUNTA POR EL ARJÉ", at=0.5)
    l1 = sc.say("Los primeros filósofos se hicieron preguntas sobre la naturaleza, que en griego se dice "
                "{greek:φύσις}, physis.",
                tts="Los primeros filósofos se hicieron preguntas sobre la naturaleza, que en griego se dice fýsis.")
    put(sc, kit.icon_card("{greek:φύσις} (physis) = {b:naturaleza}", "sprout", med_bg="olive_l", size=40, seed=501),
        440, 300, l1.at("naturaleza"), enter="slide_l")
    l2 = sc.say("Su gran pregunta era: ¿de qué está hecho todo?")
    put(sc, card("¿De qué está hecho todo?", size=48, font_name="title", bg="cream", border=("terra", 4),
                 pad=(36, 14), seed=502), 1370, 300, l2.start(), enter="drop")
    l3 = sc.say("Buscaban el {gold:arjé}: el principio del que {gold:nace} todo, del que todo {gold:está hecho}, "
                "y al que todo {gold:vuelve}.")
    put(sc, card("ARJÉ  ·  ἀρχή", size=64, font_name="title", bg="gold", pad=(40, 12), seed=503), W / 2, 480,
        l3.at("arjé"), enter="pop")
    for i, (txt, k) in enumerate([("de donde {b:nace} todo", "nace"), ("de lo que {b:está hecho}", "hecho"),
                                  ("a donde todo {b:vuelve}", "vuelve")]):
        put(sc, card(txt, size=38, bg="cream", pad=(24, 10), seed=504 + i), 480 + i * 480, 610, l3.at(k))
    l4 = sc.say("Por eso se les llama {gold:filósofos de la naturaleza}, o también {gold:presocráticos}, porque "
                "vivieron antes de Sócrates.")
    put(sc, kit.icon_card("{b:PRESOCRÁTICOS} = antes de Sócrates", "hourglass", med_bg="terra_l", size=40,
                          seed=508), W / 2, 780, l4.at("presocráticos"), enter="drop")

    sc = scn(mv, "d2")
    title(sc, "¿CUÁL ES EL ARJÉ? SUS RESPUESTAS", at=0.4, size=52)
    l0 = sc.say("Cada uno dio una respuesta distinta.")
    people = [("Tales", "water-drop", "agua", 330, 360,
               "{gold:Tales} dijo que el arjé es el {blue:agua}: sin agua no hay vida, y el agua puede ser líquida, "
               "sólida o vapor."),
              ("Anaximandro", "infinity", "ápeiron", 750, 360,
               "{gold:Anaximandro}, su discípulo, dijo que es el {blue:ápeiron}: algo indefinido e ilimitado, "
               "del que salen todas las cosas."),
              ("Anaxímenes", "whirlwind", "aire", 1170, 360, "{gold:Anaxímenes} dijo que es el {blue:aire}."),
              ("Heráclito", "fire", "fuego", 1590, 360,
               "{gold:Heráclito}, que es el {blue:fuego}, porque todo cambia sin parar. Suya es la frase: "
               "«nadie se baña dos veces en el mismo río»."),
              ("Pitágoras", "abacus", "números", 540, 680,
               "{gold:Pitágoras} pensaba que el principio de todo son los {blue:números}, porque todo tiene orden "
               "y proporción."),
              ("Empédocles", "sun", "4 elementos", 960, 680,
               "{gold:Empédocles} habló de {blue:cuatro elementos}: tierra, agua, aire y fuego."),
              ("Demócrito", "atom", "átomos", 1380, 680,
               "Y {gold:Demócrito} dijo que todo está hecho de {blue:átomos}: partículas diminutas que no se "
               "pueden dividir.")]
    for name, ic, arje, x, y, spoken in people:
        ln = sc.say(spoken)
        med = greek.medallion(150, ic, bg="blue_l", seed=x + y)
        nm = card(name, size=34, font_name="body9", bg="cream", pad=(16, 6), seed=x + y + 1)
        ar = card(arje, size=32, font_name="title", bg="gold", pad=(16, 6), seed=x + y + 2)
        piece = kit.compose([(med, 0, 0), (nm, 0, 88, -2), (ar, 0, 142, 2)])
        put(sc, piece, x, y + 45, ln.start(), enter="drop")

    sc = scn(mv, "d3")
    owl = sc.owl(250, 690, scale=0.65, at=0.4, enter="slide_l", z=6)
    l1 = sc.say("Lo importante no es si acertaron, sino {terra:cómo} pensaban.")
    put(sc, card("No importa si acertaron:\nimporta {terra|b:CÓMO} pensaban.", size=56, font_name="body9",
                 bg="cream", border=("terra", 4), pad=(46, 22), seed=521), 1060, 330, l1.start(), rot=-1)
    l2 = sc.say("Ya no hablaban de dioses: buscaban una explicación {blue:natural} y {blue:racional}, y discutían "
                "entre ellos para mejorarla.")
    for i, (txt, ic, k) in enumerate([("natural", "sprout", "natural"), ("racional", "brain", "racional"),
                                      ("debatida", "conversation", "discutían")]):
        put(sc, kit.icon_card("{b:%s}" % txt, ic, med_bg="blue_l", size=40, min_w=240, seed=522 + i),
            640 + i * 420, 580, l2.at(k), enter="pop")
    l3 = sc.say("Eso ya es logos. Y en el fondo, ahí empieza también la {blue:ciencia}.")
    put(sc, kit.icon_card("¡Ahí empieza también la {b:ciencia}!", "erlenmeyer", med_bg="blue_l", size=42,
                          seed=526), 1060, 770, l3.at("ciencia", after=-0.3), enter="drop")
    owl.mood(l3.at("ciencia"), "wow", "wide")

    sc = scn(mv, "d4", bg="night")
    title(sc, "LA ANÉCDOTA DE TALES", at=0.4)
    put(sc, greek.stars(1800, 520, n=70, seed=541), W / 2, 460, 0.2, enter="cut", z=-2, shadow=False, jitter=0.3)
    put(sc, greek.icon_cutout("moon", 170, "cream", seed=542), 1650, 330, 0.3, enter="pop", z=-1)
    l1 = sc.say("Una anécdota famosa, que cuenta Platón.")
    well = greek.icon_cutout("well", 300, "cream", seed=543)
    e_well = put(sc, well, 820, 720, l1.start(0.3), enter="slide_u", z=3, rot=0)
    l2 = sc.say("Una noche, Tales iba andando mientras miraba las estrellas… y se cayó a un pozo.")
    tales = kit.person("Tales", diam=150, seed=544)
    e_t = put(sc, tales, 480, 560, l2.start(), enter="slide_l", z=2, rot=-4)
    e_t.move(l2.at("estrellas"), x=660, y=520, rot=8, dur=0.8)
    e_t.move(l2.at("cayó"), x=820, y=640, rot=35, dur=0.35, ease="in")
    e_t.leave(l2.at("pozo"), "pop", 0.25)
    put(sc, greek.bubble("¡Plof!", size=54, seed=545, tail="center"), 820, 470, l2.at("pozo"), enter="pop", z=4,
        until=l2.end(1.0))
    l3 = sc.say("Una joven esclava de Tracia se rió de él: quería conocer lo que pasaba en el cielo, y no veía lo "
                "que tenía delante de sus pies.")
    put(sc, kit.person("joven tracia", icon="person", bg="terra_l", diam=150, seed=546), 1300, 640, l3.start(),
        enter="slide_r")
    put(sc, greek.bubble("¡Ja, ja, ja!", size=48, seed=547, tail="left"), 1440, 430, l3.at("rió"), enter="pop")
    l4 = sc.say("Nos reímos del filósofo… pero ese mirar hacia arriba con asombro es justo donde empieza la "
                "filosofía.")
    owl = sc.owl(300, 700, scale=0.6, at=l4.start(), enter="slide_u", z=5)
    owl.mood(l4.at("asombro"), "wow", "wide", (0, -0.6))
    l5 = sc.say("Y eso nos lleva a la gran pregunta: ¿por qué filosofamos?")
    put(sc, greek.big_glyph("?", 200, "gold", seed=548), 1680, 690, l5.at("por qué"), enter="pop")


# ============================================================================
# Ε. ¿Por qué filosofamos?  (admiración, duda, situaciones límite)
# ============================================================================
def seccion_epsilon(mv):
    kit.section_scene(mv, "Ε", "¿Por qué filosofamos?", sub="Admiración · Duda · Situaciones límite",
                      narration="Quinta parada, la más importante: ¿por qué filosofamos?")

    sc = scn(mv, "e1", transition="wipe")
    title(sc, "¿QUÉ NOS MUEVE A FILOSOFAR?", at=0.5)
    l1 = sc.say("Una cosa es dónde nació la filosofía. Otra, qué es lo que nos empuja a filosofar.")
    l2 = sc.say("Hay tres respuestas clásicas: la {gold:admiración}, la {blue:duda} y las {red:situaciones límite}.")
    trio = [("ADMIRACIÓN", "night-sky", "gold", "black", 400, "admiración", "¡Oh!", "gold_l"),
            ("DUDA", "uncertainty", "blue_l", "cream", 960, "duda", "¿Seguro?", "blue_l"),
            ("SITUACIONES\nLÍMITE", "hourglass", "terra_l", "cream", 1520, "límite", "¡Ay!", "terra_l")]
    for name, ic, bg, tc, x, k, _, _ in trio:
        tb = {"gold": "gold", "blue_l": "blue", "terra_l": "red"}[bg]
        c = kit.concept(name, ic, bg=bg, diam=230, title_size=46, title_bg=tb,
                        title_color="black" if tb == "gold" else "cream", seed=600 + x)
        put(sc, c, x, 520, l2.at(k), enter="pop")
    l3 = sc.say("Y cada una tiene su exclamación. La admiración: «¡oh!». La duda: «¿seguro?». "
                "Y las situaciones límite: «¡ay!».")
    for (name, ic, bg, tc, x, k, excl, bcol), key in zip(trio, ["oh", "seguro", "ay"]):
        put(sc, greek.bubble(excl, size=50, seed=610 + x, tail="left"), x + 170, 290, l3.at(key, after=-0.2),
            enter="pop", z=5)

    # --- admiración (noche)
    sc = scn(mv, "e2a", bg="night")
    title(sc, "1 · LA ADMIRACIÓN", at=0.4)
    put(sc, greek.stars(1800, 560, n=80, seed=621), W / 2, 480, 0.2, enter="cut", z=-2, shadow=False, jitter=0.3)
    put(sc, greek.icon_cutout("moon", 150, "cream", seed=622), 1700, 300, 0.3, enter="pop", z=-1)
    l1 = sc.say("Primera: la {gold:admiración}. Es la respuesta de los griegos, sobre todo de {gold:Platón} y "
                "{gold:Aristóteles}.")
    put(sc, kit.person("Platón", diam=160, sub="siglo IV a. C.", seed=623), 230, 450, l1.at("Platón"))
    put(sc, kit.person("Aristóteles", diam=160, sub="siglo IV a. C.", seed=624), 1700, 620, l1.at("Aristóteles"))
    l2 = sc.say("Pero ojo con la palabra. Aquí admiración {red:no} significa admirar a alguien, como a un cantante "
                "o a un futbolista.")
    put(sc, kit.ojo("Admiración {red|b:NO} es admirar a alguien (a un famoso).\nEs {b:ASOMBRO}: {greek:θαυμάζειν}.",
                    size=40, max_w=1050), W / 2, 330, l2.at("ojo"), rot=-1, z=4)
    l3 = sc.say("Significa {gold:asombro}: quedarte sorprendido ante algo que no entiendes. En griego se dice "
                "{greek:θαυμάζειν}.",
                tts="Significa asombro: quedarte sorprendido ante algo que no entiendes. En griego se dice "
                    "taumácein.")
    owl = sc.owl(W / 2, 700, scale=0.85, at=l3.start(), enter="slide_u", z=3)
    owl.mood(l3.at("asombro"), "wow", "wide", (0, -0.6))
    l4 = sc.say("Es lo que sientes si miras el cielo de noche y te preguntas: ¿por qué existe todo esto? "
                "¿Qué es?")
    put(sc, greek.bubble("¡Oh! ¿Qué es todo esto?", size=44, font_name="body9", seed=625, tail="left"), 1200, 540,
        l4.at("preguntas"), enter="pop", z=5)

    sc = scn(mv, "e2b")
    title(sc, "LO QUE DIJERON PLATÓN Y ARISTÓTELES", at=0.4, size=52)
    l1 = sc.say("{gold:Platón} escribió que el asombro es el sentimiento propio del filósofo, y que la filosofía "
                "no tiene otro origen.")
    q1 = kit.quote("«Admirarse es lo propio del filósofo:\nla filosofía no tiene otro origen.»",
                   "— Platón, Teeteto", size=42)
    put(sc, q1, 700, 380, l1.start(), rot=-1.2)
    l2 = sc.say("Y {gold:Aristóteles} dijo que los seres humanos comienzan, y siempre han comenzado, a filosofar "
                "movidos por la admiración.")
    q2 = kit.quote("«Los hombres comienzan y comenzaron siempre\na filosofar movidos por la admiración.»",
                   "— Aristóteles, Metafísica", size=42)
    put(sc, q2, 1220, 690, l2.start(), rot=1.2)

    sc = scn(mv, "e2c")
    title(sc, "DEL ASOMBRO A LA PREGUNTA", at=0.4)
    l1 = sc.say("Aristóteles lo explicó paso a paso. Al principio, nos asombramos de las cosas más sencillas "
                "y cercanas.")
    steps = [("1 · lo cercano y sencillo", 430, 760, "sencillas"),
             ("2 · la luna, el sol y las estrellas", 860, 610, None),
             ("3 · el origen del universo", 1300, 460, None)]
    put(sc, card(steps[0][0], size=40, font_name="body9", bg="gold_l", pad=(26, 12), seed=641), steps[0][1],
        steps[0][2], l1.at("sencillas"))
    l2 = sc.say("Después, poco a poco, de cosas más grandes: los cambios de la luna, del sol y de las estrellas. "
                "Y al final, del origen del universo.")
    put(sc, card(steps[1][0], size=40, font_name="body9", bg="gold_l", pad=(26, 12), seed=642), steps[1][1],
        steps[1][2], l2.at("luna"))
    put(sc, card(steps[2][0], size=40, font_name="body9", bg="gold", pad=(26, 12), seed=643), steps[2][1],
        steps[2][2], l2.at("origen"))
    put(sc, greek.icon_cutout("stairs", 170, "brown", seed=644), 1650, 330, l2.start(), enter="pop")
    l3 = sc.say("Y añadió algo clave: quien se asombra, {gold:reconoce que no sabe}. Y por eso busca saber.")
    put(sc, card("Quien se asombra\n{terra|b:reconoce que no sabe}.", size=46, font_name="body9", bg="cream",
                 border=("gold", 4), pad=(34, 16), seed=645), 480, 360, l3.at("reconoce"), rot=-1.5)
    l4 = sc.say("Es lo que decía {gold:Sócrates}: «solo sé que no sé nada». Saber que no sabes es el primer paso "
                "para aprender.")
    put(sc, kit.person("Sócrates", diam=150, seed=646), 1560, 700, l4.at("Sócrates"))
    put(sc, greek.bubble("Solo sé que no sé nada", size=38, font_name="body9", seed=647, tail="right"), 1250, 820,
        l4.at("solo"), enter="pop", z=5)

    sc = scn(mv, "e2d")
    owl = sc.owl(260, 680, scale=0.75, at=0.4, enter="slide_l", z=6)
    l1 = sc.say("Resumiendo: la admiración es el «¡oh!».", tts="Resumiendo: la admiración es el ¡oh!")
    put(sc, kit.concept("ADMIRACIÓN", "night-sky", bg="gold", diam=220, title_size=46, seed=651), 820, 450,
        l1.start(), enter="pop")
    put(sc, greek.bubble("¡Oh!", size=64, seed=652, tail="left"), 1050, 260, l1.at("oh"), enter="pop")
    owl.mood(l1.at("oh"), "wow", "wide")
    l2 = sc.say("Mira hacia el {gold:mundo}, hacia la realidad, y nos hace {gold:preguntar}: ¿qué es esto? "
                "¿Por qué existe?")
    put(sc, kit.icon_card("Mira hacia el {b:MUNDO}", "world", med_bg="gold_l", size=42, min_w=420, seed=653),
        1420, 480, l2.at("mundo"), enter="slide_r")
    put(sc, kit.icon_card("Nos hace {b:PREGUNTAR}", "talk", med_bg="gold_l", size=42, min_w=420, seed=654),
        1420, 660, l2.at("preguntar"), enter="slide_r")

    # --- duda
    sc = scn(mv, "e3a")
    title(sc, "2 · LA DUDA", at=0.4)
    owl = sc.owl(W - 230, 700, scale=0.6, at=0.5, enter="slide_r", z=6)
    owl.mood(0.6, "doubt", "open", (-0.6, 0))
    l1 = sc.say("Segunda: la {blue:duda}. Es la respuesta de {blue:René Descartes}, un filósofo francés del "
                "{blue:siglo XVII}, casi dos mil años después de Platón.")
    put(sc, kit.person("René Descartes", icon="think", bg="blue_l", sub="Francia, siglo XVII", diam=210,
                       seed=701), 380, 520, l1.at("Descartes"))
    l2 = sc.say("Descartes se dio cuenta de que muchas cosas que había aprendido desde pequeño eran falsas.")
    put(sc, card("Mucho de lo que aprendí\n{blue|b:era falso}…", size=46, font_name="body9", bg="cream",
                 border=("blue", 4), pad=(34, 16), seed=702), 1030, 380, l2.at("cuenta"), rot=-1)
    l3 = sc.say("Así que tomó una decisión radical: {blue:dudar de todo} lo que se pudiera dudar, para quedarse "
                "solo con lo que fuera {blue:absolutamente seguro}.")
    put(sc, kit.icon_card("{b:Dudar de todo} lo dudable…\n…y quedarme con lo {b:100 % seguro}.",
                          "uncertainty", med_bg="blue_l", size=40, max_w=800, seed=703), 1080, 660,
        l3.at("dudar"), enter="drop")

    sc = scn(mv, "e3b")
    title(sc, "TRES RAZONES PARA DUDAR", at=0.4)
    l0 = sc.say("Y dio {blue:tres razones} para dudar.")
    reasons = [("{b:1 · LOS SENTIDOS ENGAÑAN}\nun palo en el agua parece doblado", "eye-target", 330,
                "Una: los {blue:sentidos} a veces nos engañan. Por ejemplo, un palo metido en el agua parece "
                "doblado, y no lo está."),
               ("{b:2 · LOS SUEÑOS}\n¿y si ahora mismo estoy soñando?", "night-sleep", 530,
                "Dos: los {blue:sueños}. Cuando soñamos, creemos que todo es real. ¿Cómo puedo estar seguro de que "
                "ahora mismo no estoy soñando?"),
               ("{b:3 · EL GENIO MALIGNO}\n¿y si alguien me engaña hasta en 2 + 3 = 5?", "imp", 730,
                "Y tres: el {blue:genio maligno}. ¿Y si existiera un ser muy poderoso y malvado que me engañara "
                "incluso en lo que parece más seguro, como que dos más tres son cinco?")]
    for txt, ic, y, spoken in reasons:
        ln = sc.say(spoken)
        put(sc, kit.icon_card(txt, ic, med_bg="blue_l", size=40, max_w=900, min_w=900, seed=710 + y), W / 2 + 40,
            y, ln.start(), enter="slide_r")

    sc = scn(mv, "e3c")
    title(sc, "PIENSO, LUEGO EXISTO", at=0.4)
    l1 = sc.say("Después de dudar de todo, encontró algo {blue:imposible de dudar}.")
    l2 = sc.say("Si dudo, estoy pensando. Y si estoy pensando, tengo que existir. Aunque me engañen en todo, "
                "para que me engañen, yo tengo que existir.")
    chain = [("DUDO", 520, "dudo"), ("PIENSO", 960, "pensando"), ("EXISTO", 1400, "existir")]
    for i, (w, x, k) in enumerate(chain):
        put(sc, card(w, size=64, font_name="title", bg="blue" if i < 2 else "gold",
                     color="cream" if i < 2 else "black", pad=(34, 12), seed=720 + i), x, 360, l2.at(k),
            enter="pop")
        if i:
            put(sc, greek.arrow(150, thick=22, color="terra", seed=723 + i), x - 225, 360, l2.at(k, after=-0.2),
                enter="slide_l", rot=0)
    l3 = sc.say("Así llegó a su famosa primera verdad: {blue:pienso, luego existo}. En latín: "
                "{blue:cogito, ergo sum}.")
    q = kit.quote("«Pienso, luego existo.»\n{grey:(cogito, ergo sum)}", "— Descartes, Discurso del método, 1637",
                  size=50)
    e = put(sc, q, W / 2, 640, l3.at("pienso"), rot=-1)
    e.pulse(l3.at("cogito"), 0.05)

    sc = scn(mv, "e3d")
    l1 = sc.say("Ojo con otra confusión típica. La duda de Descartes se llama {blue:duda metódica}, porque es un "
                "{blue:método}: un camino para llegar a la verdad.")
    put(sc, kit.ojo("La duda de Descartes es {b:METÓDICA}: un {b:método}, un camino hacia la verdad.", size=42,
                    max_w=1300), W / 2, 250, l1.start(), rot=-1)
    l2 = sc.say("No es la duda del {red:escéptico}, que duda de todo y se queda ahí, pensando que no podemos saber "
                "nada.")
    put(sc, kit.icon_card("{b:ESCÉPTICO}\nduda… y se queda en la duda", "anticlockwise-rotation", med_bg="grey",
                          size=40, max_w=640, min_w=560, seed=731), 520, 540, l2.at("escéptico"), enter="slide_l")
    l3 = sc.say("Descartes duda {blue:para salir} de la duda y encontrar algo seguro. La duda es el medio, "
                "no el final.")
    put(sc, kit.icon_card("{b:DESCARTES}\nduda → para encontrar {b:la verdad}", "key", med_bg="blue_l", size=40,
                          max_w=700, min_w=600, seed=732), 1380, 540, l3.at("Descartes"), enter="slide_r")
    l4 = sc.say("Resumiendo: la duda es el «¿seguro?». Mira hacia lo que {blue:creías saber} y lo "
                "{blue:comprueba}.", tts="Resumiendo: la duda es el ¿seguro? Mira hacia lo que creías saber y lo "
                                        "comprueba.")
    put(sc, greek.bubble("¿Seguro?", size=56, seed=733, tail="right"), 560, 760, l4.at("seguro"), enter="pop")
    put(sc, kit.icon_card("Mira a lo que {b:CREÍAS SABER} y lo {b:COMPRUEBA}", "magnifying-glass",
                          med_bg="blue_l", size=40, seed=734), 1240, 780, l4.at("creías"), enter="drop")

    # --- situaciones límite
    sc = scn(mv, "e4")
    title(sc, "3 · LAS SITUACIONES LÍMITE", at=0.4)
    l1 = sc.say("Tercera: las {red:situaciones límite}. Esta idea es de {red:Karl Jaspers}, un filósofo alemán "
                "del {red:siglo XX}.")
    put(sc, kit.person("Karl Jaspers", icon="stone-bust", bg="terra_l", sub="Alemania, siglo XX", diam=180,
                       seed=801), 300, 470, l1.at("Jaspers"))
    l2 = sc.say("Son situaciones que no podemos evitar ni controlar, y que nos hacen sentir lo {red:frágiles} "
                "que somos.")
    put(sc, card("Situaciones que {red|b:no podemos evitar}\ny nos hacen sentir {red|b:frágiles}.", size=42,
                 font_name="body9", bg="cream", border=("red", 4), pad=(34, 16), seed=802), 1150, 300, l2.start(),
        rot=1)
    l3 = sc.say("Jaspers habla de cuatro: la {red:muerte}, el {red:sufrimiento}, la {red:lucha} y la {red:culpa}.")
    four = [("MUERTE", "hourglass", "muerte"), ("SUFRIMIENTO", "broken-heart", "sufrimiento"),
            ("LUCHA", "crossed-swords", "lucha"), ("CULPA", "pointing", "culpa")]
    for i, (w, ic, k) in enumerate(four):
        med = greek.medallion(140, ic, bg="terra_l", seed=810 + i)
        tg = card(w, size=30, font_name="title", bg="red", color="cream", pad=(14, 6), seed=815 + i)
        put(sc, kit.compose([(med, 0, 0), (tg, 0, 86, -2)]), 700 + i * 300, 560, l3.at(k), enter="pop")
    l4 = sc.say("Cuando muere alguien a quien quieres, o sufres de verdad, aparecen preguntas enormes: ¿qué "
                "sentido tiene la vida? ¿Qué hay después de la muerte? Eso también es filosofar.")
    put(sc, greek.bubble("¿Qué sentido tiene la vida?", size=40, font_name="body9", seed=820, tail="left"), 1150,
        790, l4.at("sentido"), enter="pop")
    l5 = sc.say("Es el «¡ay!».", tts="Es el ¡ay!")
    put(sc, greek.bubble("¡Ay!", size=64, seed=821, tail="right"), 330, 760, l5.start(), enter="pop", z=5)

    # --- admiración vs duda: tabla
    sc = scn(mv, "e5a")
    title(sc, "ADMIRACIÓN  vs  DUDA", at=0.35)
    l1 = sc.say("Y ahora, lo que más se confunde: {gold:admiración} y {blue:duda}. Vamos a compararlas punto "
                "por punto.")
    put(sc, kit.header("ADMIRACIÓN  ¡Oh!", bg="gold", color="black", size=40), 930, 250, l1.at("admiración"),
        enter="pop")
    put(sc, kit.header("DUDA  ¿Seguro?", bg="blue", size=40), 1490, 250, l1.at("duda"), enter="pop")
    rows = [("¿Quién?", "{b:Platón y Aristóteles}\nGrecia antigua", "{b:Descartes}\nsiglo XVII",
             "¿Quién? La admiración es de {gold:Platón y Aristóteles}, en la Grecia antigua. La duda, de "
             "{blue:Descartes}, casi dos mil años después."),
            ("¿Qué sientes?", "{b:sorpresa}", "{b:desconfianza}",
             "¿Qué sientes? Con la admiración, {gold:sorpresa}. Con la duda, {blue:desconfianza}."),
            ("¿Hacia dónde mira?", "al {b:mundo}, a la realidad", "a {b:tus propias ideas}",
             "¿Hacia dónde mira? La admiración mira al {gold:mundo}, a la realidad. La duda mira hacia dentro: "
             "a {blue:tus propias ideas}, a lo que creías saber."),
            ("¿Qué pregunta?", "«¿{b:qué es} esto?»", "«¿{b:es verdad}?»",
             "¿Qué pregunta? La admiración pregunta: ¿qué es esto? La duda pregunta: ¿es verdad?"),
            ("¿A dónde lleva?", "a {b:buscar explicaciones}", "a {b:revisarlas} hasta una certeza",
             "¿Y a dónde lleva? La admiración lleva a {gold:buscar explicaciones}. La duda, a {blue:revisarlas} "
             "hasta encontrar una certeza.")]
    for i, (q, a, b, spoken) in enumerate(rows):
        y = 360 + i * 112
        ln = sc.say(spoken)
        put(sc, kit.cell(q, bg="paper2", size=32, min_w=330, max_w=360), 330, y, ln.start(), enter="slide_l")
        put(sc, kit.cell(a, bg="gold_l", size=32, min_w=500, max_w=520), 930, y, ln.start(0.4))
        kb = "duda" if i != 0 else "Descartes"
        put(sc, kit.cell(b, bg="blue_l", color="black", size=32, min_w=500, max_w=520), 1490, y,
            ln.at(kb) if kb in ln.plain else ln.start(1.5))

    sc = scn(mv, "e5b")
    title(sc, "ENTONCES, ¿CUÁL ES EL ORIGEN?", at=0.4)
    l1 = sc.say("Entonces, ¿cuál es el verdadero origen de la filosofía: la admiración o la duda?")
    l2 = sc.say("La respuesta es: {terra:las dos}. No compiten: son dos momentos del mismo camino.")
    put(sc, card("¡LAS DOS! No compiten: {terra|b:se complementan}.", size=54, font_name="body9", bg="cream",
                 border=("terra", 5), pad=(44, 18), seed=901), W / 2, 290, l2.at("dos"), rot=-1)
    l3 = sc.say("Primero te {gold:asombras} y te haces preguntas. Después {blue:dudas} de las respuestas fáciles y "
                "las compruebas. Y a veces, una {red:situación límite} te obliga a pensar en lo más profundo.")
    steps = [("1 · ¡Oh!\n{b:ASOMBRO}\n→ preguntas", "gold", "black", 420, "asombras"),
             ("2 · ¿Seguro?\n{b:DUDA}\n→ compruebas", "blue", "cream", 960, "dudas"),
             ("3 · ¡Ay!\n{b:LÍMITE}\n→ sentido", "red", "cream", 1500, "situación")]
    for i, (txt, bg, col, x, k) in enumerate(steps):
        put(sc, card(txt, size=42, font_name="body9", bg=bg, color=col, pad=(40, 16), seed=902 + i,
                     line_spacing=1.1, hl="gold_l"), x, 510, l3.at(k), enter="drop")
        if i:
            put(sc, greek.arrow(120, thick=22, color="terra", seed=906 + i), x - 270, 510, l3.at(k, after=-0.3),
                enter="slide_l", rot=0)
    l4 = sc.say("Karl Jaspers lo resumió así: la filosofía nace del {gold:asombro}, de la {blue:duda} y de la "
                "conmoción de las {red:situaciones límite}.")
    put(sc, kit.quote("La filosofía nace del {gold_d:asombro}, de la {blue:duda}\ny de las {red:situaciones límite}.",
                      "— Karl Jaspers", size=36), W / 2, 745, l4.at("resumió"))

    sc = scn(mv, "e5c")
    owl = sc.owl(230, 680, scale=0.75, at=0.4, enter="slide_l", z=6)
    title(sc, "TRUCO PARA NO LIARTE NUNCA", at=0.5)
    l1 = sc.say("Truco para no liarte nunca:")
    rows = [("{b:¡Oh!}  →  ADMIRACIÓN  →  Platón y Aristóteles  →  mira al {b:mundo}", "gold", "black", 350,
             "¡Oh!: admiración. Platón y Aristóteles. Mira al mundo.",
             "¡Oh!, admiración, de Platón y Aristóteles, que mira al mundo."),
            ("{b:¿Seguro?}  →  DUDA  →  Descartes  →  mira a {b:lo que sabes}", "blue", "cream", 530,
             "¿Seguro?: duda. Descartes. Mira a lo que sabes.",
             "¿Seguro?, la duda, de Descartes, que mira a lo que sabes."),
            ("{b:¡Ay!}  →  SITUACIONES LÍMITE  →  Jaspers  →  mira a {b:tu vida}", "red", "cream", 710,
             "¡Ay!: situaciones límite. Jaspers. Mira a tu vida.",
             "¡Ay!, las situaciones límite, de Jaspers, que miran a tu vida.")]
    moods = ["wow", "doubt", "calm"]
    for (txt, bg, col, y, spoken, spoken_tts), md in zip(rows, moods):
        ln = sc.say(spoken, tts=spoken_tts)
        put(sc, card(txt, size=40, font_name="body", bg=bg, color=col, pad=(34, 16), max_w=1400, seed=y,
                     hl="gold_l"), 1130, y, ln.start(), enter="slide_r")
        owl.mood(ln.start(), md, "wide" if md == "wow" else "open", (0.6, 0) if md == "doubt" else (0, 0))

    kit.key_idea(mv, "{gold_d:¡Oh!} → admiración\n{blue:¿Seguro?} → duda\n{red:¡Ay!} → situaciones límite\n"
                 "No compiten: {terra:se complementan}.",
                 "Idea clave: filosofamos por admiración, por duda y por las situaciones límite. Y no compiten: "
                 "se complementan.")


# ============================================================================
# Ζ. La filosofía y otros saberes
# ============================================================================
def seccion_zeta(mv):
    kit.section_scene(mv, "Ζ", "La filosofía y otros saberes",
                      narration="Sexta parada: la filosofía y otros saberes.")

    sc = scn(mv, "z1", transition="wipe")
    title(sc, "OPINIÓN Y CONOCIMIENTO", at=0.5)
    l1 = sc.say("Hay muchas formas de saber. La más básica es el {grey:saber común}, o vulgar: lo que aprendemos "
                "por experiencia, por costumbre o porque nos lo dicen.")
    put(sc, kit.icon_card("{b:SABER COMÚN}\nexperiencia y costumbre", "talk", med_bg="paper2",
                          size=38, max_w=620, seed=1001), 540, 330, l1.at("saber común"), enter="slide_l")
    l2 = sc.say("Es muy útil en el día a día, pero no se revisa, no es sistemático, y a veces se equivoca. Por "
                "ejemplo, durante siglos «se sabía» que el Sol giraba alrededor de la Tierra.")
    put(sc, kit.icon_card("«El Sol gira alrededor\nde la Tierra»  ✗", "sun", med_bg="gold_l", size=38, seed=1002),
        1340, 330, l2.at("Sol"), enter="slide_r")
    l3 = sc.say("Platón llamaba a este saber {greek:δόξα}, doxa, que significa {grey:opinión}.",
                tts="Platón llamaba a este saber dóxa, que significa opinión.")
    put(sc, card("{greek:δόξα} · DOXA\n= {b:opinión}", size=50, font_name="body9", bg="paper2", pad=(40, 16),
                 seed=1003, line_spacing=1.1), 560, 620, l3.at("Platón"), rot=-2)
    l4 = sc.say("Y lo distinguía de la {greek:ἐπιστήμη}, episteme: el {gold:conocimiento verdadero}, bien "
                "fundamentado con razones.",
                tts="Y lo distinguía de la epistéme: el conocimiento verdadero, bien fundamentado con razones.")
    put(sc, card("{greek:ἐπιστήμη} · EPISTEME\n= {b:conocimiento con razones}", size=50, font_name="body9",
                 bg="gold", pad=(40, 16), seed=1004, line_spacing=1.1), 1360, 620, l4.at("episteme"), rot=2)
    put(sc, greek.arrow(200, thick=24, color="terra", seed=1005), 960, 620, l4.at("episteme"), enter="slide_l",
        rot=0)

    sc = scn(mv, "z2")
    title(sc, "CIENCIA Y FILOSOFÍA", at=0.4)
    l1 = sc.say("¿Y en qué se diferencian la ciencia y la filosofía?")
    put(sc, kit.concept("CIENCIA", "microscope", bg="blue_l", diam=170, title_size=44, title_bg="blue",
                        title_color="cream", seed=1011), 480, 330, l1.at("ciencia"), enter="pop")
    put(sc, kit.concept("FILOSOFÍA", "classical-knowledge", bg="gold_l", diam=170, title_size=44, title_bg="gold",
                        seed=1012), 1440, 330, l1.at("filosofía"), enter="pop")
    l2 = sc.say("La {blue:ciencia} estudia partes concretas de la realidad: la física, la materia; la biología, "
                "los seres vivos.")
    put(sc, kit.cell("Estudia {b:partes concretas}\nde la realidad", size=36, min_w=520), 480, 560, l2.start())
    l3 = sc.say("Usa un método: observa, experimenta y mide. Y sus resultados se pueden {blue:comprobar}.")
    put(sc, kit.cell("{b:Observa, experimenta y mide}\nse puede comprobar", size=36, min_w=520), 480, 690,
        l3.start())
    l4 = sc.say("La {gold:filosofía} no hace experimentos. Reflexiona con la razón sobre las preguntas que no se "
                "pueden medir: qué es la verdad, qué está bien o mal, qué sentido tiene la vida.")
    put(sc, kit.cell("Mira la realidad {b:en conjunto}\n{b:sin experimentos}", size=36, min_w=520), 1440, 560,
        l4.start())
    put(sc, kit.cell("Preguntas que {b:no se miden}:\nverdad, bien, sentido", size=36, min_w=520), 1440, 690,
        l4.at("preguntas"))
    l5 = sc.say("Dicho fácil: la ciencia pregunta sobre todo {blue:cómo} funcionan las cosas. La filosofía pregunta "
                "{gold:qué son}, {gold:por qué} y {gold:para qué}.")
    put(sc, card("¿CÓMO?", size=60, font_name="title", bg="blue", color="cream", pad=(30, 10), seed=1013), 480,
        820, l5.at("cómo"), enter="pop")
    put(sc, card("¿QUÉ ES? ¿POR QUÉ? ¿PARA QUÉ?", size=46, font_name="title", bg="gold", pad=(30, 12), seed=1014),
        1440, 820, l5.at("qué son"), enter="pop")

    sc = scn(mv, "z3")
    title(sc, "LA MADRE DE LAS CIENCIAS", at=0.4)
    l1 = sc.say("Al principio, la filosofía lo abarcaba todo: la física, la astronomía, las matemáticas, "
                "la biología…")
    mom = kit.concept("FILOSOFÍA", "classical-knowledge", bg="gold_l", diam=200, title_size=44, title_bg="gold",
                      seed=1021)
    put(sc, mom, W / 2, 520, l1.start(), enter="pop", rot=0)
    kids = [("Física", "atom", 330, 430), ("Astronomía", "ringed-planet", 640, 320), ("Matemáticas", "abacus",
                                                                                        1280, 320),
            ("Química", "erlenmeyer", 1590, 430), ("Biología", "dna1", 450, 740), ("Psicología", "brain", 1470, 740)]
    l2 = sc.say("Con el tiempo, cada ciencia se fue {blue:independizando}: la física en el siglo XVII, y más tarde "
                "la química, la biología o la psicología.")
    for i, (nm, ic, x, y) in enumerate(kids):
        med = greek.medallion(120, ic, bg="blue_l", seed=1030 + i)
        tg = card(nm, size=30, font_name="body9", bg="cream", pad=(14, 5), seed=1040 + i)
        e = sc.add(kit.compose([(med, 0, 0), (tg, 0, 76, -2)]), W / 2, 500, at=l1.start(0.3 + 0.1 * i),
                   enter="cut", z=-1)
        e.move(l2.at("independizando", after=0.25 * i), x=x, y=y, rot=rot_of(nm, 8), dur=0.6)
    l3 = sc.say("Por eso se dice que la filosofía es la {gold:madre de las ciencias}.")
    put(sc, card("= madre de las ciencias", size=40, font_name="body9", bg="cream", border=("gold", 4),
                 pad=(24, 10), seed=1050), W / 2, 700, l3.at("madre"), enter="pop", z=3)
    l4 = sc.say("Pero no se quedó sin trabajo: hoy reflexiona sobre la propia ciencia, sus límites y su "
                "{gold:ética}. Por ejemplo: ¿debemos clonar seres humanos? Eso no lo responde un experimento.")
    put(sc, greek.bubble("¿Debemos clonar seres humanos?", size=38, font_name="body9", seed=1051, tail="center"),
        W / 2, 830, l4.at("clonar"), enter="pop", z=4)

    sc = scn(mv, "z4")
    title(sc, "¿Y LA RELIGIÓN?", at=0.4)
    l1 = sc.say("¿Y la religión? También intenta responder a grandes preguntas, como el sentido de la vida o qué "
                "hay después de la muerte.")
    put(sc, card("Las dos se hacen {b:grandes preguntas}", size=46, font_name="body9", bg="cream", pad=(34, 14),
                 seed=1061), W / 2, 300, l1.at("grandes"), rot=-1)
    l2 = sc.say("Pero la religión se basa en la {purple:fe} y en la revelación; la filosofía solo acepta lo que se "
                "puede {gold:argumentar con la razón}.")
    put(sc, kit.concept("RELIGIÓN", "prayer", bg="purple_l", diam=170, title_size=42, title_bg="purple",
                        title_color="cream", seed=1062), 560, 560, l2.at("religión"), enter="pop")
    put(sc, kit.cell("se basa en la {purple|b:fe}\ny la revelación", size=38, min_w=460), 560, 780, l2.at("fe"))
    put(sc, kit.concept("FILOSOFÍA", "brain", bg="gold_l", diam=170, title_size=42, title_bg="gold", seed=1063),
        1360, 560, l2.at("filosofía"), enter="pop")
    put(sc, kit.cell("solo acepta {gold_d|b:argumentos}\ny razones", size=38, min_w=460), 1360, 780,
        l2.at("argumentar"))

    kit.key_idea(mv, "{grey:Doxa} = opinión · {gold_d:Episteme} = conocimiento\nCiencia: {blue:¿cómo?}\n"
                 "Filosofía: {gold_d:¿qué es? ¿por qué? ¿para qué?}\nReligión: {purple:fe} · Filosofía: {gold_d:razón}",
                 "Idea clave: la doxa es opinión; la episteme, conocimiento con razones. La ciencia pregunta cómo; "
                 "la filosofía, qué es, por qué y para qué. Y la religión se basa en la fe; la filosofía, en la "
                 "razón.", size=48, max_w=1250)


# ============================================================================
# Η. Las ramas de la filosofía
# ============================================================================
def seccion_eta(mv):
    kit.section_scene(mv, "Η", "Las ramas de la filosofía",
                      narration="Séptima parada: las ramas de la filosofía.")

    sc = scn(mv, "h1", transition="wipe")
    title(sc, "LAS CUATRO PREGUNTAS DE KANT", at=0.5)
    l1 = sc.say("{gold:Immanuel Kant}, un filósofo alemán del siglo XVIII, resumió toda la filosofía en cuatro "
                "preguntas.")
    put(sc, kit.person("Immanuel Kant", sub="Alemania, siglo XVIII", diam=200, seed=1101), 330, 500,
        l1.at("Kant"))
    qs = [("1 · ¿Qué puedo {b:SABER}?", "open-book", "blue_l", 1080, 290, "Una: ¿qué puedo {blue:saber}?"),
          ("2 · ¿Qué debo {b:HACER}?", "scales", "terra_l", 1080, 420, "Dos: ¿qué debo {terra:hacer}?"),
          ("3 · ¿Qué me cabe {b:ESPERAR}?", "sunflower", "olive_l", 1080, 550, "Tres: ¿qué me cabe {olive:esperar}?"),
          ("4 · ¿Qué es el {b:SER HUMANO}?", "person", "gold", 1080, 680,
           "Y cuatro: ¿qué es el {gold:ser humano}?")]
    last = None
    for txt, ic, bg, x, y, spoken in qs:
        ln = sc.say(spoken)
        last = put(sc, kit.icon_card(txt, ic, med_bg=bg, size=40, min_w=640, seed=x + y), x, y, ln.start(0.2),
                   enter="drop")
    l6 = sc.say("Y añadió que, en el fondo, las tres primeras se resumen en la última: {gold:todas hablan de "
                "nosotros}.")
    last.pulse(l6.at("última"), 0.12)
    put(sc, card("Todas se resumen en: ¿qué es el {b:ser humano}?", size=42, font_name="body9", bg="gold",
                 pad=(34, 14), seed=1110), 1080, 810, l6.at("resumen"), enter="drop")

    sc = scn(mv, "h2")
    title(sc, "FILOSOFÍA TEÓRICA: PARA CONOCER", at=0.4)
    l1 = sc.say("De preguntas como esas salen las {terra:ramas} de la filosofía. Se dividen en dos grandes grupos.")
    put(sc, greek.icon_cutout("tree-roots", 140, "olive", seed=1120), 170, 780, l1.at("ramas"), enter="pop")
    l2 = sc.say("La {blue:filosofía teórica} busca {blue:conocer}. Sus ramas principales son cuatro.")
    br = [("{b:METAFÍSICA}\nla realidad y el ser", "ringed-planet", 560, 370,
           "La {blue:metafísica}, que estudia la realidad y el ser: ¿qué existe de verdad? ¿Existe Dios? "
           "¿Somos libres?"),
          ("{b:EPISTEMOLOGÍA}\nel conocimiento y la verdad", "magnifying-glass", 1380, 370,
           "La {blue:epistemología}, o teoría del conocimiento: ¿qué podemos conocer? ¿Qué es la verdad?"),
          ("{b:LÓGICA}\nrazonar bien, sin trampas", "gears", 560, 610,
           "La {blue:lógica}, que estudia cómo razonar correctamente, sin trampas."),
          ("{b:ANTROPOLOGÍA}\n¿qué es el ser humano?", "person", 1380, 610,
           "Y la {blue:antropología filosófica}, que pregunta qué es el ser humano.")]
    for txt, ic, x, y, spoken in br:
        ln = sc.say(spoken)
        put(sc, kit.icon_card(txt, ic, med_bg="blue_l", size=38, max_w=560, min_w=520, seed=x + y + 5), x, y,
            ln.start(), enter="slide_l" if x < 900 else "slide_r")

    sc = scn(mv, "h3")
    title(sc, "FILOSOFÍA PRÁCTICA: PARA ACTUAR", at=0.4)
    l1 = sc.say("La {terra:filosofía práctica} busca orientar cómo {terra:actuar}.")
    br = [("{b:ÉTICA}\nel bien y el mal: ¿cómo vivir?", "scales", 360,
           "La {terra:ética} reflexiona sobre el bien y el mal: ¿cómo debo vivir? ¿Qué es ser una buena persona?"),
          ("{b:POLÍTICA}\nsociedad, poder y justicia", "vote", 555,
           "La {terra:filosofía política} estudia la sociedad, el poder y la justicia: ¿cuál es la mejor forma "
           "de gobierno?"),
          ("{b:ESTÉTICA}\nla belleza y el arte", "painted-pottery", 750,
           "Y la {terra:estética} estudia la belleza y el arte: ¿qué es lo bello? ¿Qué convierte algo en arte?")]
    for txt, ic, y, spoken in br:
        ln = sc.say(spoken)
        put(sc, kit.icon_card(txt, ic, med_bg="terra_l", size=38, max_w=620, min_w=600, seed=y + 9), 700, y,
            ln.start(), enter="slide_l")
    l5 = sc.say("Truco: la teórica, para {blue:conocer}; la práctica, para {terra:actuar}.")
    put(sc, card("TEÓRICA\n= {b:conocer}", size=46, font_name="title", bg="blue", color="cream", pad=(34, 14),
                 seed=1131, hl="gold_l"), 1450, 420, l5.at("teórica"), enter="pop")
    put(sc, card("PRÁCTICA\n= {b:actuar}", size=46, font_name="title", bg="terra", color="cream", pad=(34, 14),
                 seed=1132, hl="gold_l"), 1450, 650, l5.at("práctica"), enter="pop")

    kit.key_idea(mv, "{blue:Teórica} = conocer\nmetafísica · epistemología · lógica · antropología\n"
                 "{terra:Práctica} = actuar\nética · política · estética",
                 "Idea clave: la filosofía teórica sirve para conocer: metafísica, epistemología, lógica y "
                 "antropología. La práctica, para actuar: ética, política y estética.", size=46, max_w=1250)


# ============================================================================
# Θ. ¿Para qué sirve?
# ============================================================================
def seccion_theta(mv):
    kit.section_scene(mv, "Θ", "¿Para qué sirve la filosofía?",
                      narration="Última parada: ¿para qué sirve la filosofía?")
    sc = scn(mv, "t1", transition="wipe")
    title(sc, "¿SIRVE PARA ALGO?", at=0.5)
    l1 = sc.say("Mucha gente dice que la filosofía no sirve para nada, porque no fabrica nada ni cura "
                "enfermedades.")
    put(sc, greek.bubble("¿Y esto para qué sirve?", size=40, font_name="body9", seed=1201, tail="left"), W / 2, 280,
        l1.start(0.3), enter="pop")
    l2 = sc.say("Pero sirve para algo muy importante: para {gold:pensar por ti mismo}.")
    uses = [("{b:PENSAR POR TI MISMO}", "light-bulb", "gold", 560, 470, l2, "pensar"),
            ("{b:QUE NO TE MANIPULEN}\npublicidad, bulos, propaganda", "eye-shield", "blue_l", 1380, 470, None, None),
            ("{b:ROMPER PREJUICIOS}\nincluidos los tuyos", "breaking-chain", "terra_l", 560, 700, None, None),
            ("{b:ORIENTAR TU VIDA}\ny convivir en democracia", "compass", "olive_l", 1380, 700, None, None)]
    l3 = sc.say("Te ayuda a detectar argumentos tramposos y a que no te {terra:manipulen}: la publicidad, los bulos, "
                "la propaganda.")
    l4 = sc.say("Te enseña a cuestionar los {terra:prejuicios}, incluidos los tuyos.")
    l5 = sc.say("Y te ayuda a decidir {terra:cómo quieres vivir} y a convivir con los demás: sin pensamiento "
                "crítico, no hay democracia.")
    for (txt, ic, bg, x, y, _, k), ln in zip(uses, [l2, l3, l4, l5]):
        put(sc, kit.icon_card(txt, ic, med_bg=bg, size=38, max_w=560, min_w=540, seed=x + y + 11), x, y,
            ln.at(k) if k else ln.start(), enter="slide_l" if x < 900 else "slide_r")

    sc = scn(mv, "t2")
    owl = sc.owl(250, 700, scale=0.7, at=0.4, enter="slide_l", z=6)
    title(sc, "ATRÉVETE A PENSAR", at=0.5)
    l1 = sc.say("{gold:Aristóteles} decía que las demás ciencias son más necesarias, pero que ninguna es mejor que "
                "la filosofía.")
    put(sc, kit.quote("«Todas las ciencias son más necesarias que ella;\npero ninguna es mejor.»",
                      "— Aristóteles, Metafísica", size=42), 1080, 350, l1.start(), rot=-1)
    l2 = sc.say("Y {gold:Kant} lo resumió con un lema en latín: {gold:sapere aude}. Significa: ¡atrévete a pensar "
                "por ti mismo!")
    sa = card("SAPERE AUDE", size=84, font_name="title", bg="gold", pad=(50, 16), seed=1211)
    e = put(sc, sa, 1080, 640, l2.at("sapere"), enter="pop", rot=-1.5)
    put(sc, card("¡Atrévete a pensar por ti mismo!  — Kant", size=40, font_name="body9", bg="cream", pad=(28, 10),
                 seed=1212), 1080, 780, l2.at("atrévete"), enter="drop")
    put(sc, greek.laurel(170, seed=1213), 1080 - sa.w / 2 - 40, 640, l2.at("atrévete"), enter="pop", rot=-15)
    put(sc, greek.laurel(170, seed=1214), 1080 + sa.w / 2 + 40, 640, l2.at("atrévete"), enter="pop", rot=15)
    e.pulse(l2.end(-0.4), 0.06)
    owl.mood(l2.at("sapere"), "wow", "wide")

    kit.key_idea(mv, "Sirve para {gold_d:pensar por ti mismo}\ny para que no te manipulen.\n"
                 "{gold_d:Sapere aude}: ¡atrévete a pensar!",
                 "Idea clave: la filosofía sirve para pensar por ti mismo, sin que te manipulen. Sapere aude: "
                 "¡atrévete a pensar!")


# ============================================================================
# Repaso (se usa en el vídeo completo y en el repaso exprés para bucle)
# ============================================================================
RECAP = [
    ("Α", "FILO + SOFÍA = {gold_d:amor a la sabiduría}\nPalabra atribuida a {b:Pitágoras}.", "hearts", "gold_l",
     "Filosofía significa amor a la sabiduría: filo, amor; sofía, sabiduría. La palabra se atribuye a Pitágoras."),
    ("Α", "Saber {terra:racional} · {terra:crítico}\n{terra:radical} · {terra:universal}", "brain", "terra_l",
     "Es un saber racional, crítico, radical y universal.",
     "Es racional, es crítico, es radical y es universal."),
    ("Β", "{gold_d:Grecia} · {gold_d:Mileto} (Jonia)\nsiglo VI a. C. · primer filósofo: {b:Tales}", "galley",
     "blue_l", "Nació en Grecia, en Mileto, en el siglo VI antes de Cristo. El primer filósofo fue Tales."),
    ("Β", "Causas: {b:comercio} · {b:polis}\n{b:ocio} · {b:religión sin dogmas}", "conversation", "gold_l",
     "Surgió gracias al comercio, la polis, el ocio y una religión sin dogmas ni libros sagrados."),
    ("Γ", "{purple:MITO}: dioses, capricho, tradición\n→ {blue:LOGOS}: razón, causas naturales, leyes", "drama-masks",
     "purple_l", "Supuso el paso del mito, con dioses, capricho y tradición, al logos: razón, causas naturales y "
                 "leyes. Un paso lento."),
    ("Δ", "{gold_d:ARJÉ} = principio de todo\nagua · ápeiron · aire · fuego\nnúmeros · 4 elementos · átomos",
     "water-drop", "blue_l", "Los presocráticos buscaban el arjé, el principio de todo: agua, ápeiron, aire, "
                             "fuego, números, cuatro elementos o átomos."),
    ("Ε", "{gold_d:¡Oh!} ADMIRACIÓN · Platón y Aristóteles\n{blue:¿Seguro?} DUDA · Descartes\n"
          "{red:¡Ay!} SITUACIONES LÍMITE · Jaspers", "night-sky", "gold_l",
     "Filosofamos por tres motivos. La admiración: ¡oh!, Platón y Aristóteles. La duda: ¿seguro?, Descartes. "
     "Y las situaciones límite: ¡ay!, Jaspers."),
    ("Ε", "Admiración = {b:asombro}, no admirar a alguien\nDuda {b:metódica}: pienso, luego existo",
     "uncertainty", "blue_l", "Admiración no es admirar a alguien: es asombro. Y la duda de Descartes es metódica: "
                              "dudar para encontrar la verdad. Pienso, luego existo."),
    ("Ζ", "Doxa = opinión · Episteme = conocimiento\nCiencia: {blue:¿cómo?} · Filosofía: {gold_d:¿por qué?}",
     "microscope", "blue_l", "La doxa es opinión; la episteme, conocimiento. La ciencia pregunta cómo; "
                             "la filosofía, qué es, por qué y para qué."),
    ("Η", "Kant: ¿qué puedo {b:saber}? ¿qué debo {b:hacer}?\n¿qué me cabe {b:esperar}? ¿qué es el "
          "{b:ser humano}?", "open-book", "olive_l",
     "Las cuatro preguntas de Kant: ¿qué puedo saber? ¿Qué debo hacer? ¿Qué me cabe esperar? ¿Qué es el ser "
     "humano?"),
    ("Η", "{blue:Teórica}: metafísica, epistemología, lógica,\nantropología · {terra:Práctica}: ética, política,"
          " estética", "scales", "terra_l",
     "Ramas teóricas, para conocer: metafísica, epistemología, lógica y antropología. Prácticas, para actuar: "
     "ética, política y estética."),
    ("Θ", "Sirve para {gold_d:pensar por ti mismo}\n{b:Sapere aude}: ¡atrévete a pensar!", "light-bulb", "gold",
     "Y sirve para pensar por ti mismo. Sapere aude: ¡atrévete a pensar!"),
]


def recap(mv, header_text="REPASO FINAL", first_transition="wipe"):
    for i, item in enumerate(RECAP):
        letter, txt, ic, bg, spoken = item[:5]
        tts = item[5] if len(item) > 5 else None
        sc = scn(mv, f"recap{i}", transition=first_transition if i == 0 else "cut", lead=0.45)
        put(sc, kit.header(f"{header_text}  ·  {i + 1}/{len(RECAP)}", bg="black", color="gold_l", size=34), W / 2,
            120, 0.15, enter="drop", rot=0)
        sec = dict(SECTIONS)[letter]
        put(sc, kit.greek_letter_medal(letter, diam=150, seed=1300 + i), 250, 400, 0.3, enter="pop")
        put(sc, card(sec, size=30, font_name="body9", bg="cream", pad=(16, 6), max_w=330, seed=1360 + i), 250, 510,
            0.4, enter="pop")
        put(sc, greek.medallion(170, ic, bg=bg, seed=1320 + i), 250, 690, 0.45, enter="pop")
        body = card(txt, size=62, font_name="body9", bg="cream", pad=(56, 30), max_w=1320, seed=1340 + i,
                    line_spacing=1.16, hl="terra")
        e = put(sc, body, 1100, 520, 0.35, enter="slide_r", rot=rot_of(txt, 1.2))
        ln = sc.say(spoken, tts=tts)
        e.pulse(ln.end(-0.35), 0.04)
        sc.wait(0.25)


def outro(mv):
    sc = mv.scene("fin", bg="terra", transition="wipe", lead=0.3)
    owl = sc.owl(W / 2, 640, scale=1.0, at=0.4, enter="slide_u", z=4)
    put(sc, greek.column(620, kind="ionic", seed=1401), 190, 560, 0.3, enter="slide_u", rot=0)
    put(sc, greek.column(620, kind="ionic", seed=1402), W - 190, 560, 0.4, enter="slide_u", rot=0)
    put(sc, greek.title_block("FIN DEL TEMA 1", size=110, color="cream", tracking=0.06), W / 2, 230, 0.6)
    ln = sc.say("Fin del tema uno. Repásalo unas cuantas veces, y te lo sabrás de memoria. ¡Ánimo!")
    owl.mood(ln.at("memoria"), "wow", "wide")
    sc.wait(0.3)
    sc.jingle(sc.now(), "outro", gain=0.45)
    put(sc, card("Iconos: game-icons.net (CC BY 3.0) · Voz: Piper davefx · Hecho con Python", size=26,
                 font_name="body7", bg="cream", pad=(20, 8), seed=1403), W / 2, 960, sc.now(), enter="pop", rot=0)
    sc.wait(4.2)


def build():
    mv = Movie(voice="davefx", speed=0.9)
    intro(mv)
    seccion_alfa(mv)
    seccion_beta(mv)
    seccion_gamma(mv)
    seccion_delta(mv)
    seccion_epsilon(mv)
    seccion_zeta(mv)
    seccion_eta(mv)
    seccion_theta(mv)
    kit.section_scene(mv, "Ω", "Repaso final", narration="Y ahora, el repaso final de todo el tema.")
    recap(mv, first_transition="wipe")
    outro(mv)
    return mv


def chapters(mv):
    """(start_time, title) for every section card, for the mp4 chapter list."""
    letters = {name: letter for letter, name in SECTIONS}
    out = []
    for sc, st in zip(mv.scenes, mv.starts):
        if sc.name == "title":
            out.append((st, "Inicio y mapa del tema"))
        elif sc.name.startswith("section:"):
            name = sc.name.split(":", 1)[1]
            key = next((k for k in letters if k.rstrip("?") in name), None)
            out.append((st, f"{letters[key]} · {name}" if key else name))
    return out


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/tema1.mp4"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mv = build().build()
    print("duración %.1f s (%.1f min), escenas %d, subtítulos %d" % (mv.total, mv.total / 60, len(mv.scenes),
                                                                     len(mv.cues)))
    if "--stills" in sys.argv:
        os.makedirs("out/stills", exist_ok=True)
        for i, (sc, st) in enumerate(zip(mv.scenes, mv.starts)):
            t = st + max(0.5, sc.cursor - 0.3)
            mv.still(t, f"out/stills/{i:02d}_{sc.name.replace(':', '_').replace('?', '').replace('¿', '')}.png")
    else:
        chs = chapters(mv)
        mv.render(out, chapters=chs)
        with open(os.path.splitext(out)[0] + "_capitulos.txt", "w", encoding="utf-8") as f:
            for st, ttl in chs:
                f.write("%d:%02d  %s\n" % (st // 60, st % 60, ttl))

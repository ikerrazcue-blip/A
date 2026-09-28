"""Style test (~45 s): title + 'admiración vs duda' + memory trick."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stopmo import greek, kit  # noqa: E402
from stopmo.gfx import W  # noqa: E402
from stopmo.movie import Movie  # noqa: E402


def build(voice="davefx"):
    mv = Movie(voice=voice, speed=0.9)

    # --- 1. title -------------------------------------------------------
    kit.title_scene(mv, "FILOSOFÍA", "Tema 1 · Introducción", tag="prueba de estilo",
                    narration="Filosofía. Tema uno: introducción.")

    # --- 2. admiración vs duda -----------------------------------------
    sc = mv.scene("origen")
    l1 = sc.say("¿De dónde nace la filosofía? Hay dos respuestas famosas.")
    sc.add(kit.title_card("¿De dónde nace la {terra:filosofía}?", size=60), W / 2, 150, at=l1.start(), enter="drop",
           rot=-1)
    sc.add(greek.column(500, kind="ionic", seed=51), W / 2, 600, at=l1.end(-0.3), enter="slide_u", z=0)

    l2 = sc.say("La primera es la {gold:admiración}.")
    adm = kit.concept("ADMIRACIÓN", "night-sky", bg="gold", greek_word="θαυμάζειν", seed=52)
    sc.add(adm, 470, 450, at=l2.at("admiración"), enter="pop", rot=2)

    l3 = sc.say("Para {gold:Platón} y {gold:Aristóteles}, filosofar empieza con un asombro: «¡oh!». "
                "Te preguntas qué es el mundo y quieres entenderlo.",
                tts="Para Platón y Aristóteles, filosofar empieza con un asombro: ¡oh! "
                    "Te preguntas qué es el mundo y quieres entenderlo.")
    sc.add(kit.person("Platón", seed=53), 290, 800, at=l3.at("Platón"), enter="drop", rot=-3, z=2)
    sc.add(kit.person("Aristóteles", seed=54), 640, 800, at=l3.at("Aristóteles"), enter="drop", rot=2, z=2)
    sc.add(greek.bubble("¡Oh!", size=70, seed=55, tail="right"), 175, 290, at=l3.at("¡oh"), enter="pop", z=3)

    l4 = sc.say("La segunda es la {blue:duda}.")
    dud = kit.concept("DUDA", "uncertainty", bg="blue_l", title_bg="blue", title_color="cream", seed=56)
    sc.add(dud, W - 470, 450, at=l4.at("duda"), enter="pop", rot=-2)

    l5 = sc.say("Siglos después, {blue:Descartes} dice que empieza con una pregunta: «¿seguro?». "
                "Desconfías de lo que creías saber y lo revisas todo.",
                tts="Siglos después, Descartes dice que empieza con una pregunta: ¿seguro? "
                    "Desconfías de lo que creías saber y lo revisas todo.")
    sc.add(kit.person("Descartes", icon="think", sub="siglo XVII", seed=57), W - 470, 800, at=l5.at("Descartes"),
           enter="drop", rot=2, z=2)
    sc.add(greek.bubble("¿Seguro?", size=52, seed=58, tail="left"), W - 215, 280, at=l5.at("seguro"),
           enter="pop", z=3)
    sc.wait(0.4)

    # --- 3. truco -------------------------------------------------------
    sc = mv.scene("truco")
    owl = sc.owl(300, 640, scale=0.95, at=0.5, enter="slide_l", z=5)
    sc.jingle(0.6, "idea", gain=0.3)
    sc.wait(0.9)
    l6 = sc.say("Truco para recordarlo:")
    sc.add(kit.title_card("TRUCO PARA RECORDAR", size=54, bg="terra", color="cream"), 1150, 160, at=l6.start(),
           enter="drop", rot=-1)
    l7 = sc.say("{gold:Admiración}: «¡oh!». Los griegos.", tts="Admiración: ¡oh! Los griegos.")
    r1 = kit.label("{b:ADMIRACIÓN}  →  «¡Oh!»  →  Platón y Aristóteles", size=46, bg="gold", seed=61,
                   pad=(40, 20), max_w=1400)
    sc.add(r1, 1150, 340, at=l7.start(), enter="slide_r", rot=1)
    l8 = sc.say("{blue:Duda}: «¿seguro?». Descartes.", tts="Duda: ¿seguro? Descartes.")
    r2 = kit.label("{b:DUDA}  →  «¿Seguro?»  →  Descartes", size=46, bg="blue", color="cream", hl="gold_l",
                   seed=62, pad=(40, 20))
    sc.add(r2, 1150, 490, at=l8.start(), enter="slide_r", rot=-1)
    owl.mood(l7.start(), "wow", "wide")
    owl.mood(l8.start(), "doubt", "open", (0.6, 0))
    l9 = sc.say("Y no se pelean: la admiración te hace {gold:preguntar}; la duda te hace {blue:comprobar}.")
    owl.mood(l9.start(), "calm")
    r3 = kit.label("Admiración = {gold_d|b:preguntar}\nDuda = {blue|b:comprobar}", size=52, bg="cream",
                   seed=63, pad=(54, 22), line_spacing=1.15)
    e3 = sc.add(r3, 1150, 730, at=l9.at("pelean"), enter="drop", rot=1)
    e3.pulse(l9.at("preguntar"), 0.06).pulse(l9.at("comprobar"), 0.06)
    sc.add(greek.laurel(170, seed=64), 1150 + r3.w / 2 + 70, 730, at=l9.at("comprobar"), enter="pop", z=2)
    sc.wait(1.2)
    return mv


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/demo.mp4"
    voice = sys.argv[2] if len(sys.argv) > 2 else "davefx"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mv = build(voice).build()
    print("duration %.1fs, scenes %d, cues %d" % (mv.total, len(mv.scenes), len(mv.cues)))
    if "--stills" in sys.argv:
        for t in [1.0, 3.5, 8, 14, 20, 26, 30, 34, 38, 42, 46]:
            if t < mv.total:
                mv.still(t, f"out/still_{t:05.1f}.png")
    else:
        mv.render(out)

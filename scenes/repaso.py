"""Repaso exprés (~2 min) para poner en bucle: las ideas clave del Tema 1, con las mismas
frases y dibujos que el vídeo completo.
    python3 scenes/repaso.py out/repaso.mp4
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stopmo import greek, kit  # noqa: E402
from stopmo.gfx import W, card  # noqa: E402
from stopmo.movie import Movie  # noqa: E402

import tema1  # noqa: E402  (same voice rules, same recap cards)


def build():
    mv = Movie(voice="davefx", speed=0.9)
    # a tiny opening card, so every loop starts in the same place
    sc = mv.scene("loop-start", bg="terra", lead=0.2, transition="cut", sweep=True)
    sc.jingle(0.2, "loop", gain=0.4)
    tema1.put(sc, greek.title_block("REPASO EXPRÉS", size=120, color="cream", tracking=0.06), W / 2, 380, 0.3,
              rot=0)
    tema1.put(sc, card("Filosofía · Tema 1 · Introducción", size=48, font_name="title", bg="cream", pad=(40, 14),
                       seed=1501), W / 2, 560, 0.5, rot=-1)
    owl = sc.owl(W / 2, 800, scale=0.5, at=0.4, enter="slide_u", z=5)
    ln = sc.say("Repaso exprés del tema uno.")
    owl.mood(ln.start(), "wow", "wide")
    sc.wait(0.3)
    tema1.recap(mv, header_text="REPASO EXPRÉS", first_transition="wipe")
    # closing beat that hands over to the beginning of the loop
    sc = mv.scene("loop-end", bg="terra", lead=0.2, transition="wipe")
    tema1.put(sc, card("¡Otra vuelta!", size=70, font_name="title", bg="cream", pad=(44, 16), seed=1502), W / 2,
              460, 0.3, enter="pop", rot=-2)
    owl = sc.owl(W / 2, 760, scale=0.5, at=0.3, enter="slide_u", z=5, talk=False)
    owl.mood(0.4, "wow", "wide")
    sc.jingle(0.3, "loop", gain=0.35)
    sc.wait(1.6)
    return mv


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/repaso.mp4"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mv = build().build()
    print("duración %.1f s, escenas %d" % (mv.total, len(mv.scenes)))
    if "--stills" in sys.argv:
        for i, (sc, st) in enumerate(zip(mv.scenes, mv.starts)):
            mv.still(st + max(0.5, sc.cursor - 0.3), f"out/stills/r{i:02d}_{sc.name}.png")
    else:
        mv.render(out)

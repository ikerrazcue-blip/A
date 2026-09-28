"""Renderiza el vídeo completo en partes (por apartados), cada una por debajo de ~30 MB.
    python3 scenes/partes.py out/
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tema1  # noqa: E402

PARTS = [  # (nombre de archivo, primer capítulo, capítulo donde termina)
    ("Filosofia_T1_parte1_Que_es_y_donde_nacio", "Inicio", "Γ"),
    ("Filosofia_T1_parte2_Mito_logos_y_presocraticos", "Γ", "Ε"),
    ("Filosofia_T1_parte3_Admiracion_duda_y_situaciones_limite", "Ε", "Ζ"),
    ("Filosofia_T1_parte4_Otros_saberes_y_ramas", "Ζ", "Θ"),
    ("Filosofia_T1_parte5_Para_que_sirve_y_repaso_final", "Θ", None),
]

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(outdir, exist_ok=True)
    mv = tema1.build().build()
    chs = tema1.chapters(mv)

    def start_of(key):
        return next(st for st, ttl in chs if ttl.startswith(key))

    for name, a, b in PARTS:
        t0 = start_of(a)
        t1 = start_of(b) if b else mv.total
        path = os.path.join(outdir, name + ".mp4")
        print(f"{name}: {t0:.1f}-{t1:.1f} s", flush=True)
        mv.render(path, t0=t0, t1=t1, srt=False)
        print(f"  -> {os.path.getsize(path) / 2**20:.1f} MiB", flush=True)

"""Comprobación visual automática: busca píxeles azules en un vídeo (o en imágenes).

Muestrea un fotograma cada `--cada` segundos y cuenta los píxeles cuyo tono cae en la franja azul
(180°–265°) con saturación y brillo suficientes para verse como azul. Sale con código 1 si algún
fotograma supera el umbral.
    python3 tools/sin_azul.py out/Cinematica_T1_Fundamentos.mp4 --cada 1
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image

W, H = 480, 270     # analysed at quarter resolution (enough for anything visible)


def blue_mask(rgb):
    a = rgb.astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = d / (mx + 1e-9)
    return (h >= 180) & (h <= 265) & (s > 0.22) & (mx > 0.18)


def frames(path, every):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=1/{every},scale={W}:{H}", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    k = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        yield k * every, np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        k += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--cada", type=float, default=1.0, help="segundos entre fotogramas analizados")
    ap.add_argument("--umbral", type=float, default=0.0005, help="fracción de píxeles azules tolerada")
    a = ap.parse_args()
    worst = (0.0, None, None)
    bad = 0
    n = 0
    for f in a.files:
        if os.path.splitext(f)[1].lower() in (".png", ".jpg", ".jpeg"):
            src = [(0.0, np.asarray(Image.open(f).convert("RGB").resize((W, H))))]
        else:
            src = frames(f, a.cada)
        for t, img in src:
            n += 1
            frac = float(blue_mask(img).mean())
            if frac > worst[0]:
                worst = (frac, f, t)
            if frac > a.umbral:
                bad += 1
                print(f"  azul: {f} t={t:.1f}s  {frac * 100:.3f}% de píxeles")
    print(f"{n} fotogramas analizados; peor: {worst[0] * 100:.4f}% ({worst[1]} t={worst[2]})")
    print("SIN AZUL ✓" if bad == 0 else f"{bad} fotogramas con azul ✗")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

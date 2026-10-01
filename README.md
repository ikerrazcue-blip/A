# Vídeos explicativos en stop-motion de papel

Generador de vídeos explicativos con estética de **recortables de papel en stop-motion** (12 fps, temblor
«a dos», sombras sobre la mesa), con **voz narrada** en español y **subtítulos**. Hay dos temas visuales:

- **Filosofía** — detalles griegos (grecas, columnas, el mochuelo de Atenea, medallones tipo vasija).
- **Física** — papel cuadriculado, reglas, piezas de papel y una capa de *motion graphics* nítida
  (ejes, vectores, trayectorias, fórmulas) encima. **Sin azul**: la paleta solo tiene colores cálidos y
  `tools/sin_azul.py` lo comprueba fotograma a fotograma.

## Estructura

- `stopmo/` — motor: papel y recortes (`gfx.py`), línea de tiempo, voz, subtítulos y render (`movie.py`),
  sintonías (`music.py`).
  - Filosofía: decorado griego y mochuelo (`greek.py`), plantillas (`kit.py`).
  - Física: `fisica.py` — paleta sin azul, fondos (cuadrícula, kraft, cielo, césped), capa vectorial con
    cairo (`Layer`, `mg`), piezas animadas por código (`live`, `World` con cámara y paralaje),
    maquetador de fórmulas (`formula`: vectores con flecha, fracciones, límites, raíces…), recortables
    (tren, andén, Ana y Leo, calle, cronómetro, velocímetro, coche, rotonda, honda…) y tarjetas de
    «COMPRUEBA» con cuenta atrás.
- `scenes/` — guiones de cada vídeo:
  - `tema1.py`, `repaso.py`, `partes.py`, `demo.py` — Filosofía, Tema 1.
  - `cinematica_t1.py` — Física, Cinemática, Tema 1: Fundamentos (≈13 min).
- `tools/sin_azul.py` — comprobación automática de que no aparece azul.
- `setup.sh` — instala dependencias y descarga las voces.

## Uso

```bash
./setup.sh
python3 scenes/cinematica_t1.py out/Cinematica_T1_Fundamentos.mp4            # vídeo + .srt + capítulos
python3 scenes/cinematica_t1.py out/c.mp4 --stills                            # fotogramas de control
python3 scenes/cinematica_t1.py out/c.mp4 --stills --every=2 --only=tren      # una parte, cada 2 s
python3 tools/sin_azul.py out/Cinematica_T1_Fundamentos.mp4                   # ¿hay azul?
python3 scenes/tema1.py out/tema1.mp4                                         # Filosofía, Tema 1
```

Créditos: iconos de [game-icons.net](https://game-icons.net) (CC BY 3.0) · fuentes Cinzel, Nunito, GFS Didot,
Patrick Hand, Marcellus (SIL OFL) y DejaVu · voz Piper `es_ES-davefx` (dataset CC0) vía sherpa-onnx.

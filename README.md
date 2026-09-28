# Filosofía en stop-motion griego

Generador de vídeos explicativos con estética de **recortables de papel en stop-motion** y detalles griegos
(grecas, columnas, el mochuelo de Atenea, medallones tipo vasija), con **voz narrada** y **subtítulos**.

- `stopmo/` — motor: papel y recortes (`gfx.py`), decorado griego y mochuelo (`greek.py`), música de lira
  (`music.py`), línea de tiempo, voz, subtítulos y render (`movie.py`), plantillas (`kit.py`).
- `scenes/` — guiones de cada vídeo (`demo.py` = prueba de estilo).
- `setup.sh` — instala dependencias y descarga las voces.

```bash
./setup.sh
python3 scenes/demo.py out/demo.mp4          # vídeo + subtítulos .srt
python3 scenes/demo.py out/demo.mp4 davefx --stills   # solo fotogramas de prueba
```

Créditos: iconos de [game-icons.net](https://game-icons.net) (CC BY 3.0) · fuentes Cinzel, Nunito, GFS Didot,
Patrick Hand, Marcellus (SIL OFL) y DejaVu · voz Piper `es_ES-davefx` (dataset CC0) vía sherpa-onnx.

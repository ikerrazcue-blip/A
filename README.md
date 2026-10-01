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
    (tren, andén, Ana y Leo, calle, cronómetro, velocímetro, coche, rotonda, honda, bici, pelota,
    edificio…), tarjetas de «COMPRUEBA» con cuenta atrás, gráficas que se dibujan en directo (`Graph`:
    x-t, v-t, a-t, pendiente, área), pizarra que se escribe línea a línea (`board`), lista de pasos
    (`step_list`) y lectura de números y unidades en voz (`enable_spoken_numbers`).
- `scenes/` — guiones de cada vídeo:
  - `tema1.py`, `repaso.py`, `partes.py`, `demo.py` — Filosofía, Tema 1.
  - Física, Cinemática (`cine_comun.py` reúne portada, repaso, cierre, calle y ciclistas):
    - `cinematica_t1.py` — Tema 1: Fundamentos (≈13 min).
    - `cinematica_t2.py` — Tema 2: MRU (≈8 min).
    - `cinematica_t3.py` — Tema 3: MRUA (≈8 min).
    - `cinematica_t4.py` — Tema 4: Caída libre y lanzamientos verticales (≈7 min).
    - `cinematica_t5.py` — Tema 5: Método de examen (≈6,5 min).
- `tools/sin_azul.py` — comprobación automática de que no aparece azul.
- `tools/cierres.py` — avisa si una función interna usa una variable que se reasigna después (en los guiones,
  las funciones de animación se evalúan al renderizar, no al definirlas).
- `setup.sh` — instala dependencias y descarga las voces.

## Uso

```bash
./setup.sh
python3 scenes/cinematica_t1.py out/Cinematica_T1_Fundamentos.mp4            # vídeo + .srt + capítulos
python3 scenes/cinematica_t1.py out/c.mp4 --stills                            # fotogramas de control
python3 scenes/cinematica_t1.py out/c.mp4 --stills --every=2 --only=tren      # una parte, cada 2 s
python3 scenes/cinematica_t2.py out/Cinematica_T2_MRU.mp4                     # Temas 2 a 5, igual
python3 scenes/cinematica_t5.py out/t5.mp4 --only=metodo,p1                    # solo algunas partes
python3 tools/sin_azul.py out/Cinematica_T1_Fundamentos.mp4                   # ¿hay azul?
python3 tools/cierres.py scenes/cinematica_t2.py                              # cierres peligrosos
python3 scenes/tema1.py out/tema1.mp4                                         # Filosofía, Tema 1
```

Créditos: iconos de [game-icons.net](https://game-icons.net) (CC BY 3.0) · fuentes Cinzel, Nunito, GFS Didot,
Patrick Hand, Marcellus (SIL OFL) y DejaVu · voz Piper `es_ES-davefx` (dataset CC0) vía sherpa-onnx.

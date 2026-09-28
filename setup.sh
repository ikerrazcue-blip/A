#!/usr/bin/env bash
# Prepara el entorno para regenerar los vídeos (Ubuntu/Debian).
set -euo pipefail
cd "$(dirname "$0")"
if command -v apt-get >/dev/null; then
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg libcairo2 >/dev/null
fi
pip install -q pillow numpy scipy soundfile sherpa-onnx cairosvg fonttools
mkdir -p voices
base="https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models"
for n in vits-piper-es_ES-davefx-medium vits-piper-es_ES-sharvard-medium; do
  [ -d "voices/$n" ] || curl -sSL "$base/$n.tar.bz2" | tar xj -C voices
done
echo "Listo. Prueba: python3 scenes/demo.py out/demo.mp4"

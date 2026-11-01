#!/usr/bin/env python3
"""Hoja de contacto de un video: para revisar la edición con los ojos antes de entregarla.

Uso:
  python3 hoja.py FINAL.mp4                      # 1 cuadro por segundo, toda la duración
  python3 hoja.py FINAL.mp4 --desde 4 --hasta 12 --fps 4   # tramo rápido (transiciones)
Salida: hoja.jpg junto al video (o --out). Ábrela y revisa: textos legibles en el celular,
nada tapando la cara, nada pegado a los bordes, sin cuadros vacíos o a medio transicionar.
"""
import argparse, json, math, subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("--desde", type=float, default=0); ap.add_argument("--hasta", type=float, default=None)
    ap.add_argument("--fps", type=float, default=1); ap.add_argument("--ancho", type=int, default=240); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", a.video], capture_output=True, text=True)
    dur = float(json.loads(r.stdout)["format"]["duration"])
    hasta = min(a.hasta or dur, dur)
    n = max(1, int((hasta - a.desde) * a.fps))
    cols = min(10, n); filas = math.ceil(n / cols)
    out = a.out or str(Path(a.video).with_name(Path(a.video).stem + "-hoja.jpg"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.desde), "-t", str(hasta - a.desde), "-i", a.video,
                    "-vf", f"fps={a.fps},scale={a.ancho}:-2,tile={cols}x{filas}:padding=4:color=black", "-frames:v", "1", out], check=True)
    print(f"{n} cuadros ({a.desde:.1f}–{hasta:.1f} s) → {out}")


if __name__ == "__main__":
    main()

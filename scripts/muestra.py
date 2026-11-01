#!/usr/bin/env python3
"""Renderiza una muestra de 4.5 s de un estilo para aprobarlo ANTES de editar el primer video.

Uso:  python3 muestra.py <estilo.json | nombre_del_estilo> [--video clip.mp4] [--cuadros] [--salida muestra.mp4]
  --video    usa los primeros segundos de su video (sin audio) en vez de un fondo neutro
  --cuadros  solo saca 2 cuadros (rápido, sin render): muestra-<estilo>-1.png y -2.png
Enseña: título fijo, lower third, subtítulos del preset, la transición del estilo, texto 3D y cierre.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LIB = Path.home() / ".config/edicion-3-niveles-pro/estilos"
ESCENAS = '''titulo_fijo(.1, 2.05, "Tu *estilo*", EST["nombre"], pops=[(.9, ".p1")])
lower_third("l3", .55, EST.get("nombre_marca") or "Tu nombre", "Así se ve tu marca", dur=1.35)
transicion(2.2)
texto_3d("t3", 2.35, "*Nivel* pro", dur=1.25, y=H * .3)
zoom(2.4, 1.1, dur=.5, hasta=3.7)
cta(3.75)
'''
FRASE = "Así se ve tu estilo en un video de verdad con subtítulos"


def buscar(arg):
    for p in (Path(arg), LIB / f"{arg}.json", SKILL / "estilos" / f"{arg}.json"):
        if p.is_file():
            return p
    sys.exit(f"No encontré el estilo «{arg}» (ni archivo, ni en {LIB}, ni en los estilos base).")


def main():
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("estilo")
    ap.add_argument("--video")
    ap.add_argument("--cuadros", action="store_true")
    ap.add_argument("--salida")
    a = ap.parse_args()

    src = buscar(a.estilo)
    est = json.load(open(src))
    slug = src.stem
    W, H = (1920, 1080) if est.get("formato") == "16:9" else (1080, 1920)
    P = Path.home() / ".cache/edicion-3-niveles-pro/muestras" / slug
    shutil.rmtree(P, ignore_errors=True)
    (P / "hf/media").mkdir(parents=True)
    (P / "hf/sfx").mkdir()
    for s in (SKILL / "assets/sfx").glob("*.mp3"):
        shutil.copy2(s, P / "hf/sfx" / s.name)
    shutil.copy2(src, P / "estilo.json")
    dur = 4.5
    if a.video:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", a.video, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(dur),
               "-map", "0:v", "-map", "1:a", "-vf", vf]
    else:
        c = est["colores"]
        fondo = f"color=c={c['secundario']}:s={W}x{H}:r=30,format=rgb24,geq=r='r(X,Y)*0.25+{int(c['fondo'][1:3], 16)}*0.75*(1-Y/H)':g='g(X,Y)*0.25+{int(c['fondo'][3:5], 16)}*0.75*(1-Y/H)':b='b(X,Y)*0.25+{int(c['fondo'][5:7], 16)}*0.75*(1-Y/H)'"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", fondo, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(dur)]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(P / "hf/media/clean.mp4")], check=True)
    shutil.copy2(P / "hf/media/clean.mp4", P / "clean.mp4")
    pal = FRASE.split()
    paso = (dur - .6) / len(pal)
    words = [{"word": w, "start": round(.3 + i * paso, 3), "end": round(.3 + (i + .85) * paso, 3)} for i, w in enumerate(pal)]
    json.dump({"words": words}, open(P / "words_clean.json", "w"), ensure_ascii=False)
    plantilla = (SKILL / "templates/build_pro.py").read_text()
    ancla = "#   cta(DUR - 3.0)\n"
    (P / "build.py").write_text(plantilla.replace(ancla, ancla + ESCENAS, 1))
    subprocess.run([sys.executable, str(P / "build.py")], check=True, stdout=subprocess.DEVNULL)
    hf = P / "hf"
    salida = Path(a.salida or f"muestra-{slug}.mp4").resolve()
    if a.cuadros:
        subprocess.run(["npx", "hyperframes", "snapshot", "--at", "1.3,2.9", "--no-end", "-o", str(P / "cuadros")], cwd=hf, check=True,
                       stdout=subprocess.DEVNULL)
        for i, f in enumerate(sorted((P / "cuadros").glob("frame-*.png")), 1):
            dst = salida.with_name(f"muestra-{slug}-{i}.png")
            shutil.copy2(f, dst)
            print(dst)
        return
    subprocess.run(["npx", "hyperframes", "render", "--quality", "draft", "--output", "renders/muestra.mp4"], cwd=hf, check=True)
    shutil.copy2(hf / "renders/muestra.mp4", salida)
    print(f"Muestra lista: {salida}")


if __name__ == "__main__":
    main()

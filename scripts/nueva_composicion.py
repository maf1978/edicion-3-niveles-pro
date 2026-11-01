#!/usr/bin/env python3
"""Arma la composición PRO de un proyecto ya cortado.

Necesita en la carpeta del proyecto: clean.mp4 y words_clean.json (de cortar.py).
Estilo (en este orden): --estilo <nombre> de tu biblioteca · estilo.json del proyecto · tu estilo activo
(~/.config/edicion-3-niveles-pro/estilo.json). Si solo tienes el estilo del skill gratis, lo migra solo.

Uso:  python3 nueva_composicion.py <carpeta_proyecto> [--estilo nombre] [--recorte]
  --recorte  te recorta del fondo con IA local (hf/media/persona.webm) para poner texto y partículas DETRÁS de ti.
             Tarda ~1 s por cada 8 cuadros en una Mac con chip M; lo hace una vez por video.
Crea: hf/media/clean.mp4 · hf/sfx/*.mp3 · build.py (plantilla pro) · hf/index.html
"""
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CFG = Path.home() / ".config/edicion-3-niveles-pro"
GRATIS = Path.home() / ".config/edicion-3-niveles/estilo.json"


def migrar(e):
    """Estilo del skill gratis (v1) → v2."""
    if e.get("version") == 2:
        return e
    if isinstance(e.get("movimiento"), str):
        e["movimiento"] = {"perfil": e["movimiento"]}
    s = e.setdefault("subtitulos", {})
    s.setdefault("preset", "caja" if s.pop("caja", False) else "karaoke")
    e.update({k: v for k, v in {"version": 2, "radio": 20, "sombras": True, "transicion": "barrido", "sonido": {"densidad": "medio"},
                                "color": "natural", "grano": False, "mascota": None, "nombre_marca": ""}.items() if k not in e})
    return e


def main():
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--estilo")
    ap.add_argument("--recorte", action="store_true")
    a = ap.parse_args()
    P = Path(a.proyecto).resolve()
    for f in ("clean.mp4", "words_clean.json"):
        if not (P / f).exists():
            sys.exit(f"Falta {P / f}: corre primero transcribir.py y cortar.py")

    if a.estilo:
        src = next((p for p in (CFG / "estilos" / f"{a.estilo}.json", SKILL / "estilos" / f"{a.estilo}.json") if p.exists()), None)
        if not src:
            sys.exit(f"No encontré el estilo «{a.estilo}» en {CFG / 'estilos'} ni en los estilos base")
    elif (P / "estilo.json").exists():
        src = P / "estilo.json"
    elif (CFG / "estilo.json").exists():
        src = CFG / "estilo.json"
    elif GRATIS.exists():
        src = GRATIS
        print("Usando tu estilo del skill gratis (lo migro al formato pro).")
    else:
        sys.exit("No hay estilo: haz primero el setup de estilo (references/setup.md)")
    est = migrar(json.load(open(src)))
    json.dump(est, open(P / "estilo.json", "w"), ensure_ascii=False, indent=1)
    print(f"estilo: {est.get('nombre', src.stem)}")

    hf = P / "hf"
    (hf / "media").mkdir(parents=True, exist_ok=True)
    (hf / "sfx").mkdir(exist_ok=True)
    dst = hf / "media/clean.mp4"
    nuevo = not dst.exists() or dst.stat().st_mtime < (P / "clean.mp4").stat().st_mtime
    if nuevo:
        shutil.copy2(P / "clean.mp4", dst)
    for s in (SKILL / "assets/sfx").glob("*.mp3"):
        if not (hf / "sfx" / s.name).exists():
            shutil.copy2(s, hf / "sfx" / s.name)
    for k in ("mascota", "logo"):
        if est.get(k) and Path(est[k]).expanduser().is_file():
            img = Path(est[k]).expanduser()
            shutil.copy2(img, hf / "media" / img.name)
            if k == "mascota":
                est["mascota"] = f"media/{img.name}"
                json.dump(est, open(P / "estilo.json", "w"), ensure_ascii=False, indent=1)

    persona = hf / "media/persona.webm"
    if a.recorte and (nuevo or not persona.exists()):
        print("Recortándote del fondo (IA local)…")
        t = time.time()
        subprocess.run(["npx", "hyperframes", "remove-background", str(dst), "-o", str(persona), "--quality", "best"], check=True)
        print(f"recorte listo en {time.time() - t:.0f} s")
    elif persona.exists() and nuevo:
        persona.unlink()
        print("El video cambió: borré el recorte viejo (vuelve a correr con --recorte si lo quieres).")

    if not (P / "build.py").exists():
        shutil.copy2(SKILL / "templates/build_pro.py", P / "build.py")
        print("build.py creado desde la plantilla pro")
    subprocess.run([sys.executable, str(P / "build.py")], check=True)
    print(f"Listo. Escribe la edición en {P / 'build.py'} (sección ESCENAS) y revisa con:\n"
          f"  cd {hf} && npx hyperframes lint && npx hyperframes snapshot --at 1,3,6 --no-end -o ../revision")


if __name__ == "__main__":
    main()

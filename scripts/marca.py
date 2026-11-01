#!/usr/bin/env python3
"""Saca la paleta de tu logo (o de una captura de tu marca) y propone colores que se lean bien en video.

Uso:  python3 marca.py logo.png                  -> imprime la paleta y la propuesta
      python3 marca.py logo.png --guardar mi-marca  -> además crea ~/.config/edicion-3-niveles-pro/estilos/mi-marca.json
                                                      (parte del estilo base --base, default: lima-electrica)
Solo necesita ffmpeg (no Pillow). Ignora el fondo transparente y los colores casi blancos o casi negros al
elegir el acento, y revisa el contraste (WCAG) de texto sobre fondo y de acento sobre fondo.
"""
import argparse, json, math, random, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LIB = Path.home() / ".config/edicion-3-niveles-pro/estilos"


def pixeles(ruta, lado=96):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-vf", f"scale={lado}:{lado}:flags=area", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True, check=True).stdout
    return [tuple(raw[i:i + 3]) for i in range(0, len(raw), 4) if raw[i + 3] > 200]


def kmeans(px, k=6, vueltas=12):
    rnd = random.Random(1)
    cs = rnd.sample(px, min(k, len(set(px)))) if px else []
    for _ in range(vueltas):
        grupos = [[] for _ in cs]
        for p in px:
            grupos[min(range(len(cs)), key=lambda i: sum((a - b) ** 2 for a, b in zip(p, cs[i])))].append(p)
        cs = [tuple(sum(c[j] for c in g) / len(g) for j in range(3)) if g else cs[i] for i, g in enumerate(grupos)]
    return sorted(((len(g), tuple(int(round(v)) for v in c)) for g, c in zip(grupos, cs)), reverse=True)


def hexa(c): return "#%02X%02X%02X" % c
def lum(c):
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = (f(v / 255) for v in c)
    return .2126 * r + .7152 * g + .0722 * b
def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)
def sat(c):
    mx, mn = max(c), min(c)
    return 0 if mx == 0 else (mx - mn) / mx


def main():
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen")
    ap.add_argument("--guardar", metavar="NOMBRE")
    ap.add_argument("--base", default="lima-electrica", help="estilo base del que se toman fuentes, ritmo, etc.")
    ap.add_argument("--claro", action="store_true", help="fondo claro en vez de oscuro")
    a = ap.parse_args()

    px = pixeles(a.imagen)
    if not px:
        sys.exit("La imagen no tiene píxeles opacos.")
    pal = kmeans(px)
    total = sum(n for n, _ in pal)
    print("Paleta del logo:")
    for n, c in pal:
        print(f"  {hexa(c)}  {100 * n / total:4.1f}%  {'█' * max(1, int(30 * n / total))}")

    vivos = [c for _, c in pal if sat(c) > .35 and .03 < lum(c) < .85]
    acento = max(vivos, key=lambda c: sat(c) * (1 + lum(c))) if vivos else pal[0][1]
    secundario = next((c for c in vivos if c != acento and math.dist(c, acento) > 90), None)
    oscuros = [c for _, c in pal if lum(c) < .03]
    claros = [c for _, c in pal if lum(c) > .85]
    if a.claro:
        fondo, texto = (claros[0] if claros else (246, 244, 239)), (oscuros[0] if oscuros else (20, 20, 20))
    else:
        fondo, texto = (oscuros[0] if oscuros else (14, 14, 16)), (claros[0] if claros else (250, 250, 250))
    secundario = secundario or texto

    col = {"fondo": hexa(fondo), "texto": hexa(texto), "acento": hexa(acento), "secundario": hexa(secundario)}
    print("\nPropuesta:", json.dumps(col))
    ct, ca = contraste(texto, fondo), contraste(acento, fondo)
    print(f"  texto/fondo  {ct:4.1f}:1  {'✅' if ct >= 7 else '⚠️  bajo (mínimo 7:1 para video)'}")
    print(f"  acento/fondo {ca:4.1f}:1  {'✅' if ca >= 3 else '⚠️  el acento se pierde sobre el fondo: usa --claro o ajústalo'}")

    if a.guardar:
        base = SKILL / "estilos" / f"{a.base}.json"
        if not base.exists():
            sys.exit(f"No existe el estilo base {base.name}. Opciones: {', '.join(p.stem for p in (SKILL / 'estilos').glob('*.json'))}")
        e = json.load(open(base))
        e.update(nombre=a.guardar, colores=col, logo=str(Path(a.imagen).resolve()))
        LIB.mkdir(parents=True, exist_ok=True)
        dst = LIB / f"{a.guardar}.json"
        json.dump(e, open(dst, "w"), ensure_ascii=False, indent=1)
        print(f"\nGuardado: {dst}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Corta silencios, muletillas y tomas malas, y deja audio e imagen perfectamente sincronizados.

Cómo decide:
  - Silencios: tramos donde la ENERGÍA del audio está baja y no cae ninguna palabra.
    (No se fía solo de los huecos entre palabras: Whisper a veces se come voz bajita.)
  - Muletillas: "eh", "em", "mmm"… sueltas (desactívalo con --con-muletillas).
  - Tomas malas: las que tú (o Claude) indiques con --quitar "desde~hasta,…" en segundos del crudo.
Todos los cortes caen en cuadros exactos; el audio se corta en esos mismos instantes.

Uso:
  python3 cortar.py crudo.mp4 words.json --plan                 # solo muestra el plan (cortes.json)
  python3 cortar.py crudo.mp4 words.json                        # aplica y genera clean.mp4
  python3 cortar.py crudo.mp4 words.json --quitar "12.4~18.9"   # además quita una toma repetida
Opciones: --silencio 0.35 (silencio mínimo a recortar) · --aire 0.10 (aire que queda a cada lado)

Salida (en --out, default la carpeta de words.json):
  clean.mp4 · words_clean.json (tiempos ya recortados) · cortes.json (qué se quitó y por qué)
"""
import argparse, json, math, re, subprocess, sys
from fractions import Fraction
from pathlib import Path

MULETILLAS = {"eh", "ehh", "em", "emm", "ehm", "mm", "mmm", "um", "uh", "uhm", "ah"}


def probe(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate,r_frame_rate",
                        "-show_entries", "format=duration", "-of", "json", str(video)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    st = d["streams"][0]
    fps = Fraction(st.get("avg_frame_rate") or st["r_frame_rate"])
    if fps <= 0 or fps > 120:
        fps = Fraction(st["r_frame_rate"])
    # normaliza 29.97/59.94 a su forma exacta y lo demás a entero
    for f in (Fraction(30000, 1001), Fraction(60000, 1001), Fraction(24000, 1001)):
        if abs(float(fps) - float(f)) < 0.01:
            fps = f
            break
    else:
        fps = Fraction(round(float(fps)))
    return fps, float(d["format"]["duration"])


def energia_db(video, paso=0.01):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    n = int(16000 * paso)
    try:
        import numpy as np
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
        x = x[: len(x) // n * n].reshape(-1, n)
        return (10 * np.log10((x ** 2).mean(axis=1) + 1e-12)).tolist()
    except ImportError:                                       # sin numpy: más lento, mismo resultado
        import array
        a = array.array("h", raw)
        return [10 * math.log10(sum(v * v for v in a[i:i + n]) / n / 32768 ** 2 + 1e-12) for i in range(0, len(a) - n + 1, n)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("words")
    ap.add_argument("--out", default=None)
    ap.add_argument("--silencio", type=float, default=0.35)
    ap.add_argument("--aire", type=float, default=0.10)
    ap.add_argument("--quitar", default="", help='tomas a quitar: "a~b,c~d" en segundos del crudo')
    ap.add_argument("--con-muletillas", action="store_true", help="no cortar eh/em/mmm")
    ap.add_argument("--plan", action="store_true", help="solo calcula y muestra los cortes")
    a = ap.parse_args()

    video, out = Path(a.video), Path(a.out or Path(a.words).parent)
    out.mkdir(parents=True, exist_ok=True)
    W = json.load(open(a.words))
    words = W["words"] if isinstance(W, dict) else W
    fps, dur = probe(video)

    # 1 · silencios por energía que no tocan ninguna palabra
    db = energia_db(video)
    voz = sorted(db[i] for w in words for i in range(int(w["start"] * 100), min(len(db), int(w["end"] * 100))))
    ref = voz[len(voz) // 2] if voz else sorted(db)[len(db) // 2]
    umbral = ref - 16                                         # 16 dB bajo la mediana de los tramos CON voz
    quietos, ini = [], None
    for i, v in enumerate(db + [0.0]):
        if v < umbral and ini is None:
            ini = i
        elif v >= umbral and ini is not None:
            quietos.append((ini * 0.01, i * 0.01)); ini = None
    unidos_q = []
    for x, y in quietos:                                      # un ruidito de < 60 ms no parte un silencio en dos
        if unidos_q and x - unidos_q[-1][1] <= 0.06:
            unidos_q[-1] = (unidos_q[-1][0], y)
        else:
            unidos_q.append((x, y))
    quietos = unidos_q
    ocupado = sorted((w["start"] - 0.03, w["end"] + 0.03) for w in words)
    def libres(x, y):
        """Partes del silencio [x, y) donde no cae ninguna palabra."""
        out, cur = [], x
        for s0, s1 in ocupado:
            if s1 <= cur or s0 >= y:
                continue
            if s0 > cur:
                out.append((cur, s0))
            cur = max(cur, s1)
        if cur < y:
            out.append((cur, y))
        return out
    cortes = []
    for x, y in quietos:
        for fx, fy in libres(x, y):
            if fy - fx < a.silencio + 2 * a.aire:
                continue
            cx = 0.0 if fx <= 0.02 else fx + a.aire           # el arranque y el final pierden todo el silencio
            cy = dur if fy >= dur - 0.02 else fy - a.aire
            cortes.append({"desde": cx, "hasta": cy, "motivo": "silencio"})

    # 2 · muletillas sueltas
    if not a.con_muletillas:
        for w in words:
            if re.sub(r"[^\wáéíóúñ]", "", w["word"].lower()) in MULETILLAS:
                cortes.append({"desde": w["start"] - 0.02, "hasta": w["end"] + 0.02, "motivo": f'muletilla "{w["word"]}"'})

    # 3 · tomas que indica el usuario
    for par in filter(None, a.quitar.split(",")):
        x, y = map(float, par.split("~"))
        cortes.append({"desde": x, "hasta": y, "motivo": "toma descartada"})

    # unir, ajustar a cuadros exactos y descartar los de menos de 2 cuadros
    cortes.sort(key=lambda c: c["desde"])
    unidos = []
    for c in cortes:
        if unidos and c["desde"] <= unidos[-1]["hasta"] + 0.02:
            unidos[-1]["hasta"] = max(unidos[-1]["hasta"], c["hasta"])
            if c["motivo"] not in unidos[-1]["motivo"]:
                unidos[-1]["motivo"] += " + " + c["motivo"]
        else:
            unidos.append(dict(c))
    fr = float(fps)
    finales = []
    for c in unidos:
        f0, f1 = math.ceil(max(0, c["desde"]) * fr - 1e-6), math.floor(min(dur, c["hasta"]) * fr + 1e-6)
        if f1 - f0 >= 2:
            ctx = " ".join(w["word"] for w in words if c["desde"] - 1.5 < w["start"] < c["hasta"] + 1.5)
            finales.append({"desde": round(f0 / fr, 4), "hasta": round(f1 / fr, 4), "cuadros": [f0, f1],
                            "motivo": c["motivo"], "contexto": ctx[:120]})
    quitado = sum(c["hasta"] - c["desde"] for c in finales)
    json.dump({"fps": str(fps), "duracion_original": dur, "segundos_quitados": round(quitado, 3), "cortes": finales},
              open(out / "cortes.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(finales)} cortes · se quitan {quitado:.1f} s de {dur:.1f} s → queda {dur - quitado:.1f} s")
    for c in finales:
        print(f"  {c['desde']:8.2f} → {c['hasta']:8.2f}  ({c['hasta'] - c['desde']:.2f} s)  {c['motivo']}")
    if a.plan:
        print(f"Plan en {out / 'cortes.json'} (no se aplicó nada).")
        return

    # 4 · render: imagen por cuadros, audio por los mismos instantes (atrim + concat: sincronía exacta)
    keeps, t = [], 0.0
    for c in finales:
        if c["desde"] > t:
            keeps.append((t, c["desde"]))
        t = c["hasta"]
    if t < dur:
        keeps.append((t, None))
    sel = "+".join(f"between(t,{c['desde']:.4f},{c['hasta'] - 0.5 / fr:.4f})" for c in finales) or "0"
    vf = f"fps={fps},select='not({sel})',setpts=N/({fps})/TB"
    af = ";".join(f"[0:a]atrim=start={x:.5f}" + (f":end={y:.5f}" if y is not None else "")
                  + f",asetpts=PTS-STARTPTS,afade=t=in:d=0.006" + (f",afade=t=out:st={max(0, y - x - 0.006):.5f}:d=0.006" if y is not None else "")
                  + f"[a{i}]" for i, (x, y) in enumerate(keeps))
    af += ";" + "".join(f"[a{i}]" for i in range(len(keeps))) + f"concat=n={len(keeps)}:v=0:a=1[aout]"
    clean = out / "clean.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-filter_complex", f"[0:v]{vf}[vout];{af}",
                    "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(clean)], check=True)

    def remap(x):
        q = 0.0
        for c in finales:
            if x >= c["hasta"]:
                q += c["hasta"] - c["desde"]
            elif x > c["desde"]:
                return round(c["desde"] - q, 3)
        return round(x - q, 3)
    dentro = lambda w: any(c["desde"] <= w["start"] and w["end"] <= c["hasta"] for c in finales)
    nuevas = [{**w, "start": remap(w["start"]), "end": remap(w["end"])} for w in words if not dentro(w)]
    json.dump({"motor": W.get("motor") if isinstance(W, dict) else None, "words": nuevas},
              open(out / "words_clean.json", "w"), ensure_ascii=False, indent=1)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", str(clean)],
                       capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"]
    v = next(float(s["duration"]) for s in st if s["codec_type"] == "video")
    au = next(float(s["duration"]) for s in st if s["codec_type"] == "audio")
    print(f"listo: {clean} · video {v:.2f} s · audio {au:.2f} s · audio−video {(au - v) * 1000:+.0f} ms (diferencia de duración) · words_clean.json")


if __name__ == "__main__":
    main()

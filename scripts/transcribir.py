#!/usr/bin/env python3
"""Transcribe un video con tiempos por palabra.

Motor:
  - AssemblyAI si hay llave (más preciso, sobre todo con voz bajita):
    $ASSEMBLYAI_API_KEY o el archivo ~/.config/assemblyai/key
  - Whisper local (faster-whisper) si no hay llave. Gratis y sin internet,
    pero se puede comer palabras dichas muy bajito: cortar.py lo compensa
    revisando la energía del audio.

Uso:
  python3 transcribir.py video.mp4                      # auto
  python3 transcribir.py video.mp4 --motor whisper --modelo small
  python3 transcribir.py video.mp4 --idioma en --out words.json

Salida: words.json  {"motor", "idioma", "duracion", "words": [{"word","start","end"}]}
        transcripcion.txt (texto con marcas de tiempo cada frase, para leerlo rápido)
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path


def llave_assemblyai():
    k = os.environ.get("ASSEMBLYAI_API_KEY", "").strip()
    if k:
        return k
    p = Path.home() / ".config/assemblyai/key"
    return p.read_text().strip() if p.exists() else ""


def extraer_audio(video, ruta):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(ruta)], check=True)


def duracion(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)


def con_assemblyai(audio, idioma, llave):
    H = {"authorization": llave}

    def req(url, data=None, headers=None, method=None):
        r = urllib.request.Request(url, data=data, headers={**H, **(headers or {})}, method=method)
        with urllib.request.urlopen(r, timeout=600) as resp:
            return json.loads(resp.read())

    up = req("https://api.assemblyai.com/v2/upload", data=Path(audio).read_bytes(),
             headers={"content-type": "application/octet-stream"})["upload_url"]
    cuerpo = {"audio_url": up, "language_code": idioma, "punctuate": True, "format_text": True,
              "disfluencies": True}           # conserva "eh", "este"… para poder cortarlos
    tid = req("https://api.assemblyai.com/v2/transcript", method="POST", data=json.dumps(cuerpo).encode(),
              headers={"content-type": "application/json"})["id"]
    while True:
        t = req(f"https://api.assemblyai.com/v2/transcript/{tid}")
        if t["status"] == "completed":
            break
        if t["status"] == "error":
            sys.exit(f"AssemblyAI devolvió error: {t.get('error')}")
        time.sleep(3)
    return [{"word": w["text"], "start": round(w["start"] / 1000, 3), "end": round(w["end"] / 1000, 3)} for w in t["words"]]


def con_whisper(audio, idioma, modelo):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Falta Whisper local. Instálalo con:\n  python3 -m pip install faster-whisper\n"
              "(o corre: bash scripts/doctor.sh --fix)", file=sys.stderr)
        sys.exit(2)
    print(f"[whisper] modelo {modelo} (la primera vez se descarga)…", flush=True)
    import numpy as np
    # el audio va ya decodificado: así no dependemos del lector de faster-whisper (PyAV cambia de API seguido)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    m = WhisperModel(modelo, device="auto", compute_type="int8")
    segs, _ = m.transcribe(np.frombuffer(raw, dtype=np.float32), language=idioma, word_timestamps=True, vad_filter=False,
                           condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in s.words or []:
            txt = w.word.strip()
            if txt:
                words.append({"word": txt, "start": round(w.start, 3), "end": round(w.end, 3)})
    return words


def texto_legible(words):
    lineas, actual, t0 = [], [], None
    for w in words:
        if t0 is None:
            t0 = w["start"]
        actual.append(w["word"])
        if w["word"][-1:] in ".?!" or len(actual) >= 14:
            lineas.append(f"[{t0:7.2f}] " + " ".join(actual)); actual, t0 = [], None
    if actual:
        lineas.append(f"[{t0:7.2f}] " + " ".join(actual))
    return "\n".join(lineas) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", default="words.json")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--motor", choices=["auto", "assemblyai", "whisper"], default="auto")
    ap.add_argument("--modelo", default="small", help="modelo de Whisper local: base, small, medium, large-v3")
    a = ap.parse_args()

    llave = llave_assemblyai()
    motor = a.motor if a.motor != "auto" else ("assemblyai" if llave else "whisper")
    if motor == "assemblyai" and not llave:
        sys.exit("No hay llave de AssemblyAI ($ASSEMBLYAI_API_KEY o ~/.config/assemblyai/key).")
    print(f"[transcribir] motor: {motor}", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "audio.wav"
        extraer_audio(a.video, audio)
        words = con_assemblyai(audio, a.idioma, llave) if motor == "assemblyai" else con_whisper(audio, a.idioma, a.modelo)

    out = Path(a.out)
    json.dump({"motor": motor, "idioma": a.idioma, "duracion": duracion(a.video), "words": words},
              open(out, "w"), ensure_ascii=False, indent=1)
    (out.parent / "transcripcion.txt").write_text(texto_legible(words))
    print(f"[transcribir] {len(words)} palabras → {out} (y transcripcion.txt)")


if __name__ == "__main__":
    main()

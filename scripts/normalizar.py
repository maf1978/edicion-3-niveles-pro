#!/usr/bin/env python3
"""Deja el audio a -14 LUFS (lo que piden YouTube, Instagram y TikTok) sin re-codificar el video.

Uso:  python3 normalizar.py render.mp4 FINAL.mp4 [--lufs -14]
Hace dos pasadas de loudnorm (mide y luego corrige) y reporta el resultado y el desfase audio/video.
"""
import argparse, json, re, subprocess


def medir(ruta, lufs):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(ruta), "-af", f"loudnorm=I={lufs}:TP=-1:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    return json.loads(re.findall(r"\{[^{}]*\}", e)[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entrada"); ap.add_argument("salida"); ap.add_argument("--lufs", type=float, default=-14)
    a = ap.parse_args()
    m = medir(a.entrada, a.lufs)
    af = (f"loudnorm=I={a.lufs}:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.entrada, "-c:v", "copy", "-af", af, "-ar", "48000",
                    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.salida], check=True)
    o = medir(a.salida, a.lufs)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", a.salida],
                       capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"]
    v = next(float(s["duration"]) for s in st if s["codec_type"] == "video")
    au = next(float(s["duration"]) for s in st if s["codec_type"] == "audio")
    print(f"{m['input_i']} LUFS → {o['input_i']} LUFS · pico {o['input_tp']} dBTP · audio−video {(au - v) * 1000:+.0f} ms (diferencia de duración) → {a.salida}")


if __name__ == "__main__":
    main()

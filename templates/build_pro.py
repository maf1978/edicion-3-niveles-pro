#!/usr/bin/env python3
"""build.py (PRO) — genera hf/index.html con TU estilo (estilo.json), tu voz (words_clean.json) y, si existe,
tu recorte (hf/media/persona.webm) para poner texto DETRÁS de ti.

Edita solo la sección ESCENAS. Después:
  python3 build.py && cd hf && npx hyperframes lint
  npx hyperframes snapshot --at 1,3,6 --no-end -o ../revision
  npx hyperframes render --quality high --output renders/edicion.mp4

Capas (de atrás hacia adelante):
  escenario (se mueve con camara/zoom):  video · DETRÁS (texto detrás de ti) · tu recorte · FRENTE
  fijo (no se mueve con la cámara):      título fijo, barra, lower thirds, tarjeta de cierre
  subtítulos · transiciones · grano
Todas las piezas leen colores, fuentes, radios, ritmo, subtítulos, transiciones y densidad de sonido de estilo.json.
"""
import json, math, random, re, subprocess, unicodedata
from pathlib import Path

B = Path(__file__).resolve().parent
HF = B / "hf"
EST = json.load(open(B / "estilo.json"))
WORDS = json.load(open(B / "words_clean.json"))["words"]


def _probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    return d["streams"][0]["width"], d["streams"][0]["height"], round(float(d["format"]["duration"]), 3)


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)


W, H, DUR = _probe(HF / "media/clean.mp4")
VERT = H > W
RECORTE = (HF / "media/persona.webm").exists()
C, F = EST["colores"], EST["fuentes"]
MOV = EST.get("movimiento", {})
if isinstance(MOV, str):
    MOV = {"perfil": MOV}
PERFIL = {"suave": ("power2.out", 1.25, "back.out(1.2)"), "energico": ("back.out(1.9)", .85, "back.out(1.7)"),
          "cinematico": ("expo.out", 1.5, "power3.inOut"), "seco": ("power4.out", .7, "power4.out")}[MOV.get("perfil", "energico")]
EASE, LENTO, RESORTE = MOV.get("entrada", PERFIL[0]), MOV.get("velocidad", PERFIL[1]), MOV.get("resorte", PERFIL[2])
RAD = EST.get("radio", 24)
SOMBRA = "0 24px 60px rgba(0,0,0,.45)" if EST.get("sombras", True) else "none"
DENS = {"ninguno": 0, "minimo": 1, "medio": 2, "alto": 3}[EST.get("sonido", {}).get("densidad", "medio")] if EST.get("sfx", True) else 0
def _lum(h):
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return sum(k * f(int(h[i:i + 2], 16) / 255) for k, i in ((.2126, 1), (.7152, 3), (.0722, 5)))
def legible(fondo_hex):
    """Blanco o casi negro, el que más contraste haga sobre ese color."""
    return "#FFFFFF" if (1.05 / (_lum(fondo_hex) + .05)) >= ((_lum(fondo_hex) + .05) / .06) else "#111111"
SAFE_T, SAFE_B = (0.12 * H, 0.80 * H) if VERT else (0.07 * H, 0.90 * H)
SAFE_R = 0.86 * W if VERT else 0.95 * W
_S = EST.get("subtitulos", {})
SUB_TAM = _S.get("tamano", int(W * .06) if VERT else int(H * .06))
SUB_TOP = {"abajo": SAFE_B - SUB_TAM * 2.4, "centro": H * .55, "arriba": SAFE_T + SUB_TAM * 3}[_S.get("posicion", "abajo")]
LIBRE_B = SUB_TOP - 30 if _S.get("activos", True) and _S.get("posicion", "abajo") == "abajo" else SAFE_B  # lo más abajo que puede llegar una pieza

ATRAS, BODY, MUNDO, FIJO, TRANS, TL, SFX, _trk = [], [], [], [], [], [], [], [10]
def r(x): return round(float(x), 3)
def el(html, capa="frente"):
    {"frente": BODY, "detras": ATRAS, "mundo": MUNDO, "fijo": FIJO, "trans": TRANS}[capa].append(html)
def tw(js): TL.append(js)
def trk(): _trk[0] += 1; return _trk[0]
def sfx(t, nombre, vol=0.32, nivel=2):
    """Efecto de sonido (hf/sfx/<nombre>.mp3). nivel 1 = esencial, 2 = normal, 3 = detalle: se toca si la densidad
    de sonido del estilo es >= nivel. Nombres: pop, whoosh, whoosh-short, whoosh-cinematic, click, click-soft,
    impact-bass-1, impact-bass-2, riser, sparkle, typing, key-press, notification, ping, chime, glitch-1."""
    if DENS >= nivel:
        SFX.append((r(max(0, t)), nombre, vol))
def _norm(s): return re.sub(r"[^\w]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def T(palabra, cerca=None, fin=False):
    """Segundo en que se dice `palabra` (la ocurrencia más cercana a `cerca`). fin=True da cuándo termina."""
    n = _norm(palabra)
    c = [w for w in WORDS if _norm(w["word"]) == n] or [w for w in WORDS if _norm(w["word"]).startswith(n)]
    if not c:
        raise SystemExit(f'No encontré la palabra "{palabra}" en words_clean.json')
    w = min(c, key=lambda w: abs(w["start"] - cerca)) if cerca is not None else c[0]
    return r(w["end"] if fin else w["start"])
def _acento(texto): return re.sub(r"\*(.+?)\*", r'<span class="ac">\1</span>', texto)
def entra(sel, t, desde="{opacity:0,y:40,scale:.9}", hacia="{opacity:1,y:0,scale:1", d=.45, ease=None):
    tw(f'tl.fromTo("{sel}",{desde},{hacia},duration:{r(d * LENTO)},ease:"{ease or EASE}",immediateRender:false}},{r(t)});')
def sale(sel, t, hacia="{opacity:0,y:-30", d=.3):
    tw(f'tl.to("{sel}",{hacia},duration:{r(d)},ease:"power2.in"}},{r(t)});')
def tam_titulo(): return int(W * .11) if VERT else int(H * .10)

# ═══════════════════════ NIVEL 1 · básico ═══════════════════════
def titulo(eid, t, texto, dur=2.5, y=None, tam=None, capa="frente"):
    """Titular. *palabra* = acento. capa="detras" lo pone detrás de ti (necesita recorte)."""
    y = SAFE_T + 20 if y is None else y
    el(f'<div id="{eid}" class="titulo" style="top:{r(y)}px;font-size:{tam or tam_titulo()}px">{_acento(texto)}</div>', capa)
    entra(f"#{eid}", t); sale(f"#{eid}", t + dur); sfx(t, "pop", .28)
def etiqueta(eid, t, texto, x, y, dur=2.2):
    el(f'<div id="{eid}" class="etiqueta" style="left:{r(x)}px;top:{r(y)}px">{_acento(texto)}</div>')
    entra(f"#{eid}", t, "{opacity:0,x:-30}", "{opacity:1,x:0", .35); sale(f"#{eid}", t + dur, "{opacity:0,x:30"); sfx(t, "click-soft", .26, 3)
def icono(eid, t, contenido, x, y, tam=None, dur=2.0, rebote=False):
    tam = tam or int(min(W, H) * .14)
    el(f'<div id="{eid}" class="icono" style="left:{r(x)}px;top:{r(y)}px;width:{tam}px;height:{tam}px;font-size:{int(tam * .8)}px">{contenido}</div>')
    if rebote:
        tw(f'tl.fromTo("#{eid}",{{opacity:0,scale:0,rotation:-25}},{{opacity:1,scale:1,rotation:0,duration:.6,ease:"elastic.out(1,.45)",immediateRender:false}},{r(t)});'
           f'tl.to("#{eid}",{{y:-14,duration:.6,yoyo:true,repeat:{max(1, int(dur / .6) - 1)},ease:"sine.inOut"}},{r(t + .6)});')
    else:
        entra(f"#{eid}", t, "{opacity:0,scale:.6}", "{opacity:1,scale:1", .3)
    sale(f"#{eid}", t + dur, "{opacity:0,scale:.6"); sfx(t, "pop", .26)
def lower_third(eid, t, nombre, rol, dur=3.2):
    """Nombre y rol (presentación o invitado)."""
    y = LIBRE_B - min(W, H) * (.075 * 1.25 + .042 * 1.45) - 22
    el(f'<div id="{eid}" class="l3" style="top:{r(y)}px"><b>{nombre}</b><span>{rol}</span></div>', "fijo")
    tw(f'tl.fromTo("#{eid} b",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:{r(.4 * LENTO)},ease:"{EASE}",immediateRender:false}},{r(t)});'
       f'tl.fromTo("#{eid} span",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:{r(.4 * LENTO)},ease:"{EASE}",immediateRender:false}},{r(t + .12)});'
       f'tl.set("#{eid}",{{opacity:1}},{r(t)});')
    sale(f"#{eid}", t + dur, "{opacity:0,x:-40"); sfx(t, "whoosh-short", .24)
def cta(t, tipo=None, palabra=None, texto=None):
    """Cierre: tipo seguir | comenta (con palabra) | link. Default: lo del estilo."""
    tipo = tipo or EST.get("cierre", "seguir")
    txt = texto or {"seguir": "Sígueme para *más*", "comenta": f'Comenta *{palabra or "INFO"}*', "link": "Link en mi *perfil*"}[tipo]
    el(f'<div id="ctaFin" class="cta" style="top:{r(SAFE_T + (H * .04 if VERT else 0))}px">{_acento(txt)}</div>', "fijo")
    tw(f'tl.fromTo("#ctaFin",{{opacity:0,scale:.6,rotation:-4}},{{opacity:1,scale:1,rotation:0,duration:.55,ease:"{RESORTE}",immediateRender:false}},{r(t)});'
       f'tl.to("#ctaFin",{{scale:1.05,duration:.5,yoyo:true,repeat:3,ease:"sine.inOut"}},{r(t + .6)});')
    sfx(t, "impact-bass-1", .3, 1)

# ═══════════════════════ NIVEL 2 · movimiento ═══════════════════════
def zoom(t, escala=1.15, dur=.35, foco=None, hasta=None):
    """Punch-in del escenario completo (tu video, tu recorte y lo que está detrás)."""
    fx, fy = foco or (W / 2, H * (.38 if VERT else .42))
    x, y = r((W / 2 - fx) * (escala - 1)), r((H / 2 - fy) * (escala - 1))
    tw(f'tl.to("#stage",{{scale:{escala},x:{x},y:{y},duration:{dur},ease:"power3.out"}},{r(t)});')
    if hasta:
        tw(f'tl.to("#stage",{{scale:1,x:0,y:0,duration:{dur},ease:"power3.inOut"}},{r(hasta)});')
    sfx(t, "whoosh-short", .2, 2)
def barra_progreso(t0, t1):
    el('<div id="barra" class="barra"><i></i></div>', "fijo")
    tw(f'tl.set("#barra",{{opacity:1}},{r(t0)});tl.fromTo("#barra i",{{scaleX:0}},{{scaleX:1,duration:{r(t1 - t0)},ease:"none",immediateRender:false}},{r(t0)});'
       f'tl.set("#barra",{{opacity:0}},{r(t1)});')
POS = {}
def _pos_cam(pos):
    """(escala, x, y) del escenario para dejar tu cámara como tarjeta en esa posición."""
    if pos == "completa": return 1, 0, 0
    s = .5 if VERT else .42
    cx, cy = {"abajo": (W * .5, H * .66), "arriba": (W * .5, H * .34), "izq": (W * .3, H * .5), "der": (W * .7, H * .5),
              "esquina": (W * .74, H * .7 if VERT else H * .72)}[pos]
    if pos == "esquina": s = .36 if VERT else .3
    if pos == "arriba" and VERT:  # más chica, para que el panel de abajo quepa sobre los subtítulos
        s = .38; cy = SAFE_T + H * s / 2 + 8
    return s, r(cx - W / 2), r(cy - H / 2)
def tarjeta_camara(t, pos="abajo", d=.6):
    """Tu cámara se vuelve tarjeta (con borde de acento) y viaja con resorte a: abajo, arriba, izq, der, esquina o completa."""
    s, x, y = _pos_cam(pos); POS["cam"] = pos
    rad = 0 if pos == "completa" else int(RAD * 1.6 / s)
    tw(f'tl.to("#stage",{{scale:{s},x:{x},y:{y},borderRadius:{rad},duration:{r(d * LENTO)},ease:"{RESORTE}"}},{r(t)});'
       f'tl.to("#marco",{{opacity:{0 if pos == "completa" else 1},duration:.2}},{r(t + (0 if pos == "completa" else d * .5))});'
       f'tl.to("#marco",{{scale:{s},x:{x},y:{y},borderRadius:{int(RAD * 1.6)},duration:{r(d * LENTO)},ease:"{RESORTE}"}},{r(t)});')
    sfx(t, "whoosh", .24, 2)
def panel(eid, t0, t1, contenido, caja=None):
    """Contenido (texto, captura, lista) en el espacio que deja la tarjeta de cámara. caja = (x, y, w, h) en px."""
    if caja is None:
        s, cx, cy = _pos_cam(POS.get("cam", "abajo"))
        top, bot, izq, der = H / 2 + cy - H * s / 2, H / 2 + cy + H * s / 2, W / 2 + cx - W * s / 2, W / 2 + cx + W * s / 2
        caja = {"abajo": (W * .06, SAFE_T, W * .88, top - SAFE_T - 36), "arriba": (W * .06, bot + 36, W * .88, LIBRE_B - bot - 36),
                "izq": (der + 36, SAFE_T, SAFE_R - der - 36, LIBRE_B - SAFE_T), "der": (W * .05, SAFE_T, izq - W * .05 - 36, LIBRE_B - SAFE_T),
                }.get(POS.get("cam"), (W * .06, SAFE_T, W * .88, H * .36) if VERT else (W * .05, H * .12, W * .5, H * .76))
    x, y, w, h = caja
    el(f'<div id="{eid}" class="panel" style="left:{r(x)}px;top:{r(y)}px;width:{r(w)}px;height:{r(h)}px">{contenido}</div>', "fijo")
    t = t0 + .35 * LENTO  # entra cuando la tarjeta ya casi llegó
    entra(f"#{eid}", t, "{opacity:0,y:50,scale:.96}", "{opacity:1,y:0,scale:1", .45, RESORTE)
    sale(f"#{eid}", t1 - .1, "{opacity:0,y:30"); sfx(t, "click", .22, 3)
def transicion(t, tipo=None):
    """Transición entre secciones: barrido | iris | whip | zoom (default: la del estilo)."""
    tipo = tipo or EST.get("transicion", "barrido")
    eid = f"tr{len(TRANS)}"
    if tipo == "barrido":
        el(f'<div id="{eid}" class="cortina" style="background:{C["acento"]}"></div>', "trans")
        tw(f'tl.set("#{eid}",{{xPercent:-101}},0);tl.fromTo("#{eid}",{{xPercent:-101}},{{xPercent:0,duration:.24,ease:"power3.in",immediateRender:false}},{r(t - .24)});'
           f'tl.to("#{eid}",{{xPercent:101,duration:.3,ease:"power3.out"}},{r(t)});')
        sfx(t - .24, "whoosh-short", .3, 1)
    elif tipo == "iris":
        # cierra: círculo de color que crece · abre: un hueco que crece desde el centro
        el(f'<div id="{eid}" class="iris" style="background:{C["fondo"]}"></div><div id="{eid}b" class="iris hueco" style="background:{C["fondo"]}"></div>', "trans")
        tw(f'tl.set("#{eid}",{{clipPath:"circle(0% at 50% 45%)"}},0);tl.set("#{eid}b",{{opacity:0,"--r":0}},0);'
           f'tl.fromTo("#{eid}",{{clipPath:"circle(0% at 50% 45%)"}},{{clipPath:"circle(75% at 50% 45%)",duration:.3,ease:"power3.in",immediateRender:false}},{r(t - .3)});'
           f'tl.set("#{eid}",{{opacity:0}},{r(t + .04)});tl.set("#{eid}b",{{opacity:1}},{r(t + .04)});'
           f'tl.fromTo("#{eid}b",{{"--r":0}},{{"--r":130,duration:.38,ease:"power3.out",immediateRender:false}},{r(t + .04)});tl.set("#{eid}b",{{opacity:0}},{r(t + .45)});')
        sfx(t - .3, "whoosh-cinematic", .28, 1)
    elif tipo == "whip":
        tw(f'tl.to("#stage",{{x:{-W * .25},filter:"blur(14px)",duration:.14,ease:"power2.in"}},{r(t - .14)});'
           f'tl.fromTo("#stage",{{x:{W * .25},filter:"blur(14px)"}},{{x:0,filter:"blur(0px)",duration:.2,ease:"power2.out",immediateRender:false}},{r(t)});')
        sfx(t - .14, "whoosh", .3, 1)
    elif tipo == "zoom":
        tw(f'tl.to("#stage",{{scale:1.6,filter:"blur(10px)",opacity:.6,duration:.18,ease:"power2.in"}},{r(t - .18)});'
           f'tl.fromTo("#stage",{{scale:.85,filter:"blur(10px)",opacity:.6}},{{scale:1,filter:"blur(0px)",opacity:1,duration:.25,ease:"power2.out",immediateRender:false}},{r(t)});')
        sfx(t - .18, "whoosh-cinematic", .3, 1)

# ═══════════════════════ NIVEL 3 · profesional ═══════════════════════
def texto_detras(eid, t, texto, dur=2.6, y=None, tam=None):
    """Palabra GIGANTE detrás de ti (efecto de profundidad). Sin recorte, queda delante y semitransparente."""
    tam = tam or (int(W * .3) if VERT else int(H * .32)); y = (H * .2 if VERT else H * .1) if y is None else y
    extra = "" if RECORTE else "opacity:.85;"
    el(f'<div id="{eid}" class="titulo gigante" style="top:{r(y)}px;font-size:{tam}px;{extra}">{_acento(texto)}</div>', "detras" if RECORTE else "frente")
    tw(f'tl.fromTo("#{eid}",{{opacity:0,scale:1.25,y:60}},{{opacity:1,scale:1,y:0,duration:{r(.6 * LENTO)},ease:"power3.out",immediateRender:false}},{r(t)});')
    sale(f"#{eid}", t + dur, "{opacity:0,scale:.92", .35); sfx(t, "impact-bass-2", .3, 1)
def titulo_fijo(t0, t1, linea1, linea2="", pops=()):
    """Título del hook que se queda arriba todo el tramo. pops = [(t, "selector dentro: .p0")] para hacerlo latir."""
    tam = int(W * .145) if VERT else int(H * .12)
    l2 = f'<div class="tf2">{_acento(linea2)}</div>' if linea2 else ""
    palabras = " ".join(f'<span class="p{i}">{_acento(p)}</span>' for i, p in enumerate(linea1.split()))
    el(f'<div id="tfijo" class="tfijo" style="top:{r(SAFE_T + 6)}px"><div class="tf1" style="font-size:{tam}px">{palabras}</div>{l2}</div>', "fijo")
    tw(f'tl.fromTo("#tfijo",{{opacity:0,scale:.55,rotationX:-75}},{{opacity:1,scale:1,rotationX:0,transformPerspective:900,transformOrigin:"50% 0%",'
       f'duration:.42,ease:"back.out(1.7)",immediateRender:false}},{r(t0)});tl.to("#tfijo",{{opacity:0,y:-50,duration:.15,ease:"power2.in"}},{r(t1 - .15)});')
    for t, sel in pops:
        tw(f'tl.fromTo("#tfijo {sel}",{{scale:1}},{{scale:1.3,duration:.1,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{r(t)});')
    sfx(t0, "impact-bass-1", .26, 1)
def sin_subtitulos(t0, t1):
    """Esconde los subtítulos en un tramo (cuando el texto en pantalla ya dice lo mismo)."""
    tw(f'tl.set("#subs",{{opacity:0}},{r(t0)});tl.set("#subs",{{opacity:1}},{r(t1)});')
def kinetic(eid, t0, frase, y=None, tam=None, dur=None, capa="frente", ocultar_subs=True):
    """Tipografía cinética: cada palabra entra apilada en el momento en que se dice (usa las palabras de la voz).
    capa="detras" la pone detrás de ti (con recorte). Esconde los subtítulos mientras está, para no repetir."""
    tam = tam or (int(W * .13) if VERT else int(H * .11)); y = SAFE_T + 30 if y is None else y
    palabras = frase.split()
    tiempos = [T(_norm(p), t0 + i * .3) for i, p in enumerate(palabras)]
    spans = "".join(f'<div class="kw" style="font-size:{tam}px">{_acento(p)}</div>' for p in palabras)
    el(f'<div id="{eid}" class="kin" style="top:{r(y)}px">{spans}</div>', capa if RECORTE else "frente")
    for i, t in enumerate(tiempos):
        tw(f'tl.fromTo("#{eid} .kw:nth-child({i + 1})",{{opacity:0,y:80,rotation:-4}},{{opacity:1,y:0,rotation:0,duration:{r(.32 * LENTO)},ease:"{RESORTE}",immediateRender:false}},{r(t - .04)});')
        sfx(t - .04, "click", .2, 3)
    fin = (dur and t0 + dur) or (tiempos[-1] + 1.0)
    sale(f"#{eid}", fin, "{opacity:0,y:-40")
    if ocultar_subs:
        sin_subtitulos(tiempos[0] - .1, fin + .2)
def camara(t, escala=1.0, x=0, y=0, rot=0, dur=1.2, ease="sine.inOut"):
    tw(f'tl.to("#stage",{{scale:{escala},x:{x},y:{y},rotation:{rot},duration:{dur},ease:"{ease}"}},{r(t)});')
def texto_3d(eid, t, texto, dur=2.6, y=None, tam=None):
    tam = tam or (int(W * .13) if VERT else int(H * .13)); y = SAFE_T + 10 if y is None else y
    capas = ",".join(f'{k}px {k}px 0 {C["secundario"]}' for k in range(1, 9))
    el(f'<div class="p3d" style="top:{r(y)}px"><div id="{eid}" class="titulo t3d" style="position:relative;font-size:{tam}px;text-shadow:{capas},10px 18px 30px rgba(0,0,0,.45)">{_acento(texto)}</div></div>')
    tw(f'tl.fromTo("#{eid}",{{opacity:0,rotationX:-80,z:-300}},{{opacity:1,rotationX:0,z:0,duration:{r(.7 * LENTO)},ease:"back.out(1.6)",immediateRender:false}},{r(t)});')
    sale(f"#{eid}", t + dur, "{opacity:0,rotationX:60,z:-200"); sfx(t, "whoosh-cinematic", .28, 2)
def particulas(eid, t, x, y, n=48, color=None, radio=None, semilla=7, dur=1.3, capa="frente"):
    """Explosión determinista. Lejos de la cara, o con capa="detras" (con recorte) para que estalle detrás de ti."""
    rnd, radio, col = random.Random(semilla), radio or min(W, H) * .45, color or C["acento"]
    puntos = "".join(f'<i style="width:{s}px;height:{s}px;background:{col if k % 3 else C["secundario"]}"></i>'
                     for k, s in enumerate(rnd.randint(int(min(W, H) * .012), int(min(W, H) * .03)) for _ in range(n)))
    el(f'<div id="{eid}" class="parts" style="left:{r(x)}px;top:{r(y)}px">{puntos}</div>', capa if RECORTE else "frente")
    for k in range(n):
        a, d, dk = rnd.uniform(0, 6.283), rnd.uniform(.35, 1) * radio, r(dur * rnd.uniform(.75, 1))
        tw(f'tl.fromTo("#{eid} i:nth-child({k + 1})",{{x:0,y:0,scale:.5,opacity:1}},{{x:{r(d * math.cos(a))},y:{r(d * math.sin(a))},'
           f'scale:1.15,duration:{dk},ease:"power3.out",immediateRender:false}},{r(t)});'
           f'tl.to("#{eid} i:nth-child({k + 1})",{{opacity:0,duration:{r(dk * .4)},ease:"power1.in"}},{r(t + dk * .6)});')
    tw(f'tl.set("#{eid}",{{opacity:1}},{r(t)});tl.set("#{eid}",{{opacity:0}},{r(t + dur)});'); sfx(t, "sparkle", .28, 2)
def broll(eid, t0, t1, archivo, modo="completo", desde=0):
    caja = ("left:0;top:0;width:100%;height:100%" if modo == "completo"
            else (f"left:{r(W * .1)}px;top:{r(SAFE_T + 40)}px;width:{r(W * .8)}px;height:{r(W * .8 * 9 / 16)}px" if VERT
                  else f"left:{r(W * .55)}px;top:{r(H * .15)}px;width:{r(W * .38)}px;height:{r(W * .38 * 9 / 16)}px"))
    el(f'<div id="{eid}" class="broll {modo}" style="{caja}"><video id="{eid}v" class="clip" src="media/{archivo}" data-start="{r(t0)}" '
       f'data-duration="{r(t1 - t0)}" data-media-start="{r(desde)}" data-track-index="{trk()}" muted playsinline></video></div>', "fijo" if modo == "completo" else "frente")
    entra(f"#{eid}", t0, "{opacity:0,scale:1.08}", "{opacity:1,scale:1", .35)
    tw(f'tl.fromTo("#{eid}v",{{scale:1}},{{scale:1.08,duration:{r(t1 - t0)},ease:"none",immediateRender:false}},{r(t0)});')
    sale(f"#{eid}", t1 - .2, "{opacity:0", .2); sfx(t0, "whoosh", .24, 2)
GRADES = {"natural": "contrast(1.05) saturate(1.08)", "calido": "contrast(1.08) saturate(1.15) sepia(.12) brightness(1.02)",
          "frio": "contrast(1.08) saturate(.95) hue-rotate(-8deg) brightness(1.02)", "cine": "contrast(1.14) saturate(1.1) sepia(.06) brightness(.97)"}
def grading(t0, t1, filtro=None):
    """Color sobre tu video y tu recorte (preset del estilo o un filtro CSS propio)."""
    f = GRADES.get(filtro or EST.get("color", "natural"), filtro or "none")
    tw(f'tl.set("#bgv, #persona",{{filter:"{f}"}},{r(t0)});tl.set("#bgv, #persona",{{filter:"none"}},{r(t1)});')
def mascota(eid, t0, t1, x, y, tam=None, entrada="salto", archivo=None):
    """La mascota DEL USUARIO (imagen con fondo transparente en hf/media/, o la de estilo.json). Nunca uses una ajena.
    entrada: salto (cae y rebota) | asoma (sube desde abajo) | pop. Respira mientras está en pantalla."""
    archivo = archivo or EST.get("mascota")
    if not archivo:
        return
    tam = tam or int(min(W, H) * .32)
    el(f'<img id="{eid}" class="masc" src="{archivo}" style="left:{r(x)}px;top:{r(y)}px;width:{tam}px">')
    desde = {"salto": "{opacity:1,y:-H,scaleY:1.15}".replace("H", str(int(H * .6))), "asoma": f"{{opacity:1,y:{tam}}}", "pop": "{opacity:0,scale:0}"}[entrada]
    tw(f'tl.fromTo("#{eid}",{desde},{{opacity:1,y:0,scale:1,scaleY:1,duration:{r(.5 * LENTO)},ease:"{"bounce.out" if entrada == "salto" else RESORTE}",immediateRender:false}},{r(t0)});'
       f'tl.to("#{eid}",{{scaleY:.94,scaleX:1.04,duration:.5,yoyo:true,repeat:{max(1, int((t1 - t0 - .6) / .5))},ease:"sine.inOut",transformOrigin:"50% 100%"}},{r(t0 + .55)});')
    sale(f"#{eid}", t1 - .25, "{opacity:0,scale:.5,y:40", .25); sfx(t0, "pop", .26, 2)
def musica(archivo, vol=.12):
    el(f'<audio id="musica" class="clip" src="media/{archivo}" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="{vol}"></audio>', "fijo")

# ─────── mundo 3D: tu video dentro de un monitor en una sala (revelación y zambullida) ───────
P3D = 2000
def _frame(tgt, sx, sy, s, rx, ry):
    """Cámara que pone el punto tgt del mundo en (sx, sy) del cuadro a escala s, con inclinación rx y giro ry."""
    x, y, z = tgt[0] - W / 2, tgt[1] - H / 2, tgt[2]
    a, b = math.radians(ry), math.radians(rx)
    x1, z1 = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y2, z2 = y * math.cos(b) - z1 * math.sin(b), y * math.sin(b) + z1 * math.cos(b)
    return (r(P3D - P3D / s - z2), rx, ry, r((sx - W / 2) / s - x1), r((sy - H / 2) / s - y2))
def _box(x, y, w, h, dep, cols, front=""):
    cf, cs, ct = cols
    return (f'<div class="bx" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--w:{w};--h:{h};--k:{dep};--cf:{cf};--cs:{cs};--ct:{ct}">'
            f'<i class="f fr">{front}</i><i class="f bk"></i><i class="f lf"></i><i class="f rt"></i><i class="f tp"></i><i class="f bt"></i></div>')
def monitor_3d(t0, t1, etiqueta_txt=None):
    """etiqueta_txt (opcional): tu marca en el frente de la mesa (queda a la altura de los subtítulos; úsala con sin_subtitulos).
    Hook pro: en t0 la cámara se aleja y revela que estás en la pantalla de un monitor gigante en una sala oscura;
    gira alrededor y en t1 se zambulle de vuelta a tu toma (corte invisible). Ideal para los primeros 2–5 segundos."""
    sup = (C["texto"], C["secundario"], C["texto"])
    etq = _acento(etiqueta_txt or "")
    mesa = _box(-60, H + 60, W + 120, int(H * .22), int(W * .45), sup, f'<span class="m3lab">{etq}</span>')
    mundo = (f'<div id="m3" class="m3"><div id="m3pan" class="m3c"><div id="m3dol" class="m3c"><div id="m3tilt" class="m3c"><div id="m3yaw" class="m3c">'
             f'<div class="m3glow"></div>'
             f'<div class="m3pos" style="transform:translateZ(-46px)"><div class="s3">{_box(-44, -44, W + 88, H + 88, 90, (C["texto"], C["secundario"], C["texto"]))}</div></div>'
             f'<video id="m3v" class="clip" src="media/clean.mp4" data-start="{r(t0 - .05)}" data-duration="{r(t1 - t0 + .1)}" data-media-start="{r(t0 - .05)}" '
             f'data-track-index="{trk()}" muted playsinline></video>'
             f'<div class="m3pos" style="transform:translateZ({int(W * .55)}px)"><div id="m3mesa" class="s3">{mesa}</div></div>'
             f'</div></div></div></div></div>')
    el(mundo, "mundo")
    sel = (("#m3dol", "z"), ("#m3tilt", "rotationX"), ("#m3yaw", "rotationY"), ("#m3pan", "x"), ("#m3pan", "y"))
    ident, cur = (0, 0, 0, 0, 0), [None]
    def mover(t, d, v, ease):
        tw("".join(f'tl.fromTo("{s}",{{{p}:{a}}},{{{p}:{b},duration:{r(d)},ease:"{ease}",immediateRender:false}},{r(t)});'
                   for (s, p), a, b in zip(sel, cur[0], v))); cur[0] = v
    tw(f'tl.set("#m3",{{opacity:1}},{r(t0)});tl.set("#m3tilt, #m3yaw",{{transformOrigin:"{W / 2}px {H / 2}px"}},0);')
    tw("".join(f'tl.set("{s}",{{{p}:0}},{r(t0)});' for s, p in sel)); cur[0] = ident
    tot = t1 - t0
    abierta = _frame((W / 2, H * .62, 0), W / 2, H * .5, .4, 12, 26)
    giro = _frame((W / 2, H * .62, 0), W / 2, H * .5, .44, 9, -18)
    mover(t0, min(.9, tot * .3), abierta, "power3.inOut")
    tw(f'tl.fromTo("#m3",{{filter:"blur(0px)"}},{{filter:"blur(6px)",duration:.3,ease:"power2.in",immediateRender:false}},{r(t0)});'
       f'tl.fromTo("#m3",{{filter:"blur(6px)"}},{{filter:"blur(0px)",duration:.4,ease:"power2.out",immediateRender:false}},{r(t0 + .3)});')
    mover(t0 + min(.9, tot * .3), tot * .45, giro, "sine.inOut")
    zt = t0 + min(.9, tot * .3) + tot * .45
    mover(zt, t1 - zt, ident, "power3.in")
    tw(f'tl.fromTo("#m3",{{filter:"blur(0px)"}},{{filter:"blur(6px)",duration:{r((t1 - zt) * .7)},ease:"power2.in",immediateRender:false}},{r(zt)});'
       f'tl.to("#m3",{{filter:"blur(0px)",duration:.08}},{r(zt + (t1 - zt) * .7)});tl.set("#m3",{{opacity:0}},{r(t1)});')
    sfx(t0, "whoosh-cinematic", .32, 1); sfx(zt, "whoosh", .3, 1)

# ═════════════════════════════ ESCENAS ═════════════════════════════
# Escribe aquí la edición (receta por nivel en references/niveles-pro.md). Ancla todo con T("palabra", segundo).
# Ejemplo:
#   monitor_3d(.3, 2.6)
#   titulo_fijo(0, 6.5, "3 *NIVELES*", "de edición con IA")
#   texto_detras("big", T("tres", 1.0), "*3*")
#   tarjeta_camara(T("primero", 8.0), "abajo"); panel("p1", T("primero", 8.0), T("segundo", 14.0), "1. Descarga")
#   tarjeta_camara(T("segundo", 14.0), "completa")
#   transicion(T("ahora", 20.0))
#   cta(DUR - 3.0)

# ═════════════════════ SUBTÍTULOS (preset del estilo) ═════════════════════
S = EST.get("subtitulos", {})
SUBS_HTML = ""
if S.get("activos", True):
    preset = S.get("preset", "karaoke")
    modo = "frase" if preset == "minimal" else S.get("modo", "palabra")
    tam, top = SUB_TAM, SUB_TOP
    activo = C.get(S.get("colorActivo", "acento"), S.get("colorActivo", C["acento"]))
    base = S.get("color", "#FFFFFF")  # sobre video el subtítulo va claro, aunque el tema de la marca sea claro
    bloques, cur = [], []
    for w in WORDS:
        if cur and (len(cur) >= S.get("palabrasPorBloque", 3) or w["start"] - cur[-1]["end"] > .45 or cur[-1]["word"][-1:] in ".,?!"):
            bloques.append(cur); cur = []
        cur.append(w)
    if cur: bloques.append(cur)
    caps = []
    for n, bq in enumerate(bloques):
        t0 = r(bq[0]["start"] - .03); t1 = r(min(bloques[n + 1][0]["start"] - .03 if n + 1 < len(bloques) else DUR, bq[-1]["end"] + .6))
        txt = [w["word"].upper() if (S.get("mayusculas") or preset == "bold") else w["word"] for w in bq]
        caps.append(f'<div id="cp{n}" class="sub sub-{preset}" style="top:{r(top)}px">' + " ".join(f'<span id="w{n}_{k}">{x}</span>' for k, x in enumerate(txt)) + "</div>")
        tw(f'tl.set("#cp{n}",{{opacity:1}},{t0});tl.set("#cp{n}",{{opacity:0}},{t1});')
        tw(f'tl.fromTo("#cp{n}",{{y:14,scale:.96}},{{y:0,scale:1,duration:.16,ease:"power2.out",immediateRender:false}},{t0});')
        if modo == "palabra":
            for k, w in enumerate(bq):
                prop = f'backgroundColor:"{activo}",color:"{legible(activo)}"' if preset == "caja" else f'color:"{activo}"'
                vuelta = f'backgroundColor:"rgba(0,0,0,0)",color:"{base}"' if preset == "caja" else f'color:"{base}"'
                tw(f'tl.set("#w{n}_{k}",{{{prop}}},{r(w["start"])});tl.set("#w{n}_{k}",{{{vuelta}}},{r(w["end"] + .05)});')
    SUBS_HTML = '<div id="subs">' + "".join(caps) + "</div>"

# ═════════════════════════════ HTML ═════════════════════════════
fam = lambda f, p: f.replace(" ", "+") + f":wght@{p}"
fonts = f'https://fonts.googleapis.com/css2?family={fam(F["titulos"], F.get("pesoTitulos", 800))}&family={fam(F["texto"], F.get("pesoTexto", 700))}&display=swap'
grano = ('<div id="grano"></div>' if EST.get("grano") else "")
CSS = f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{C["fondo"]}}}
#root{{position:absolute;inset:0;overflow:hidden;font-family:'{F["texto"]}',sans-serif;color:{C["texto"]};background:{C["fondo"]}}}
#stage{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;transform-origin:50% 50%;overflow:hidden}}
#bgv,#persona{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover}}
#detras{{position:absolute;inset:0}} #frente{{position:absolute;inset:0;perspective:{max(W, H) * 1.2}px}}
#marco{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;transform-origin:50% 50%;border:{max(6, int(W * .008))}px solid {C["acento"]};opacity:0;pointer-events:none;z-index:3}}
#mundo{{position:absolute;inset:0;z-index:5}} #fijo{{position:absolute;inset:0;z-index:6}} #trans{{position:absolute;inset:0;z-index:12;pointer-events:none}}
.titulo{{position:absolute;left:0;right:0;text-align:center;font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};
  line-height:1;letter-spacing:-.02em;opacity:0;color:{C["texto"]};text-shadow:0 6px 24px rgba(0,0,0,.45);padding:0 4%}}
.gigante{{letter-spacing:-.04em;text-shadow:none;line-height:.9}}
.ac{{color:{C["acento"]}}}
.etiqueta{{position:absolute;opacity:0;font-weight:{F.get("pesoTexto", 700)};font-size:{int(min(W, H) * .045)}px;color:{C["fondo"]};
  background:{C["texto"]};padding:.3em .6em;border-radius:{RAD * .5}px;box-shadow:{SOMBRA}}}
.icono{{position:absolute;opacity:0;display:flex;align-items:center;justify-content:center;line-height:1}} .icono svg{{width:100%;height:100%}}
.l3{{position:absolute;left:6%;opacity:0;display:flex;flex-direction:column;gap:.25em}}
.l3 b{{font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};font-size:{int(min(W, H) * .075)}px;background:{C["texto"]};color:{C["fondo"]};
  padding:.1em .35em;border-radius:{RAD * .4}px;width:fit-content;opacity:0}}
.l3 span{{font-weight:{F.get("pesoTexto", 700)};font-size:{int(min(W, H) * .042)}px;background:{C["acento"]};color:{C["fondo"]};padding:.2em .6em;
  border-radius:{RAD * .4}px;width:fit-content;opacity:0}}
.cta{{position:absolute;left:6%;right:6%;text-align:center;opacity:0;font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};
  font-size:{int(W * .1) if VERT else int(H * .1)}px;line-height:1.05;color:{C["texto"]};-webkit-text-stroke:{max(6, int(W * .008))}px {C["fondo"]};
  paint-order:stroke fill;text-shadow:0 8px 30px rgba(0,0,0,.5)}}
.barra{{position:absolute;left:0;right:0;top:0;height:{max(8, int(H * .006))}px;opacity:0;background:{C["texto"]}33}}
.barra i{{display:block;height:100%;background:{C["acento"]};transform-origin:left center}}
.panel{{position:absolute;opacity:0;border-radius:{RAD}px;background:{C["fondo"]};border:3px solid {C["secundario"]};overflow:hidden;box-shadow:{SOMBRA};
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.2em;font-family:'{F["titulos"]}',sans-serif;font-size:{int(min(W, H) * .065)}px;
  font-weight:{F.get("pesoTitulos", 800)};line-height:1.05;text-align:center;padding:5%;color:{C["texto"]}}}
.panel small{{font-size:.45em;letter-spacing:.12em;opacity:.7}}
.cortina,.iris{{position:absolute;inset:0}}
.hueco{{--r:0;-webkit-mask-image:radial-gradient(circle at 50% 45%,transparent calc(var(--r) * 1%),#000 calc(var(--r) * 1% + 2px));mask-image:radial-gradient(circle at 50% 45%,transparent calc(var(--r) * 1%),#000 calc(var(--r) * 1% + 2px))}}
.tfijo{{position:absolute;left:0;right:0;text-align:center;opacity:0;pointer-events:none}}
.tf1{{font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};line-height:.95;letter-spacing:-.04em;color:{C["texto"]};
  -webkit-text-stroke:{max(6, int(W * .008))}px {C["fondo"]};paint-order:stroke fill;text-shadow:0 5px 0 {C["secundario"]},0 10px 0 {C["secundario"]},0 24px 30px rgba(0,0,0,.45)}}
.tf1 span{{display:inline-block}} .tf2{{margin-top:.2em;font-weight:{F.get("pesoTexto", 700)};font-size:{int(W * .06) if VERT else int(H * .05)}px;color:{C["texto"]};
  -webkit-text-stroke:{max(5, int(W * .006))}px {C["fondo"]};paint-order:stroke fill}}
.kin{{position:absolute;left:0;right:0;text-align:center}} .kw{{font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};line-height:.98;
  letter-spacing:-.03em;opacity:0;color:{C["texto"]};text-shadow:0 8px 26px rgba(0,0,0,.45)}}
.p3d{{position:absolute;left:0;right:0;perspective:900px}} .t3d{{transform-style:preserve-3d}}
.parts{{position:absolute;opacity:0}} .parts i{{position:absolute;border-radius:50%;display:block}}
.masc{{position:absolute;opacity:0;transform-origin:50% 100%;filter:drop-shadow(0 18px 30px rgba(0,0,0,.4))}}
.broll{{position:absolute;opacity:0;overflow:hidden}} .broll.tarjeta{{border-radius:{RAD}px;border:4px solid {C["texto"]};box-shadow:{SOMBRA}}}
.broll video{{width:100%;height:100%;object-fit:cover;display:block}}
#subs{{position:absolute;inset:0;z-index:10;pointer-events:none}}
.sub{{position:absolute;left:6%;right:{r((1 - SAFE_R / W) * 100 + 4)}%;text-align:center;opacity:0;font-family:'{F["texto"]}',sans-serif;
  font-weight:{F.get("pesoTexto", 700)};font-size:{SUB_TAM}px;line-height:1.15;color:{_S.get("color", "#FFFFFF")}}}
.sub span{{display:inline-block;margin:0 .08em;padding:.02em .14em;border-radius:{RAD * .3}px}}
.sub-karaoke{{-webkit-text-stroke:{max(6, int(W * .008))}px #000;paint-order:stroke fill;text-shadow:0 4px 0 #000}}
.sub-caja span{{background:rgba(0,0,0,0);text-shadow:0 3px 10px rgba(0,0,0,.6)}}
.sub-minimal{{font-weight:600;text-shadow:0 2px 12px rgba(0,0,0,.7)}}
.sub-bold{{font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};-webkit-text-stroke:{max(7, int(W * .009))}px #000;paint-order:stroke fill;letter-spacing:-.01em}}
#grano{{position:absolute;inset:0;z-index:14;pointer-events:none;opacity:.06;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}}
.m3{{position:absolute;inset:0;opacity:0;overflow:hidden;perspective:{P3D}px;perspective-origin:{W / 2}px {H / 2}px;
  background:radial-gradient(70% 55% at 50% 40%,{C["secundario"]}33,transparent 70%),{C["fondo"]}}}
.m3c{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;transform-style:preserve-3d}}
.m3pos{{position:absolute;left:0;top:0;width:0;height:0;transform-style:preserve-3d}}
#m3v{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover}}
.m3glow{{position:absolute;left:{-W}px;top:{-H * .6}px;width:{W * 3}px;height:{H * 2.2}px;background:radial-gradient(closest-side,{C["acento"]}2e,transparent);transform:translateZ(-200px)}}
.s3,.s3 .bx{{transform-style:preserve-3d}} .s3{{position:absolute;left:0;top:0}} .s3 .bx{{position:absolute}}
.s3 .f{{position:absolute;display:block;border:6px solid {C["fondo"]};box-sizing:border-box;backface-visibility:hidden}}
.s3 .fr,.s3 .bk{{left:0;top:0;width:100%;height:100%}}
.s3 .fr{{background:var(--cf);transform:translateZ(calc(var(--k) * .5px))}} .s3 .bk{{background:var(--cs);transform:rotateY(180deg) translateZ(calc(var(--k) * .5px))}}
.s3 .lf,.s3 .rt{{top:0;height:100%;width:calc(var(--k) * 1px);left:calc((var(--w) - var(--k)) * .5px);background:var(--cs)}}
.s3 .lf{{transform:rotateY(-90deg) translateZ(calc(var(--w) * .5px))}} .s3 .rt{{transform:rotateY(90deg) translateZ(calc(var(--w) * .5px))}}
.s3 .tp,.s3 .bt{{left:0;width:100%;height:calc(var(--k) * 1px);top:calc((var(--h) - var(--k)) * .5px)}}
.s3 .tp{{background:var(--ct);transform:rotateX(90deg) translateZ(calc(var(--h) * .5px))}} .s3 .bt{{background:var(--cs);transform:rotateX(-90deg) translateZ(calc(var(--h) * .5px))}}
.m3lab{{position:absolute;left:5%;top:10%;font-family:'{F["titulos"]}',sans-serif;font-weight:{F.get("pesoTitulos", 800)};font-size:{int(W * .07)}px;color:{C["fondo"]}}}"""
persona = (f'<video id="persona" class="clip" src="media/persona.webm" data-start="0" data-duration="{DUR}" data-track-index="3" muted playsinline></video>'
           if RECORTE else "")
_d = {n: _dur(HF / "sfx" / f"{n}.mp3") for n in {n for _, n, _ in SFX}}
AUD = "".join(f'<audio id="sx{i}" class="clip" src="sfx/{n}.mp3" data-start="{t}" data-duration="{r(min(_d[n], DUR - t))}" data-track-index="{100 + i}" data-volume="{v}"></audio>'
              for i, (t, n, v) in enumerate(sorted(SFX)))
html = f"""<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<link href="{fonts}" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<div id="stage"><video id="bgv" class="clip" src="media/clean.mp4" data-start="0" data-duration="{DUR}" data-track-index="0" muted playsinline></video>
<div id="detras">{"".join(ATRAS)}</div>{persona}<div id="frente">{"".join(BODY)}</div></div><div id="marco"></div>
<div id="mundo">{"".join(MUNDO)}</div><div id="fijo">{"".join(FIJO)}</div>{SUBS_HTML}<div id="trans">{"".join(TRANS)}</div>{grano}
<audio id="voz" class="clip" src="media/clean.mp4" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>{AUD}
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
{chr(10).join(TL)}
window.__timelines['main']=tl;</script></div></body></html>"""
(HF / "index.html").write_text(html)
(HF / "hyperframes.json").write_text(json.dumps({"version": "1", "compositions": [{"id": "main", "file": "index.html"}]}, indent=2))
print(f"OK · {W}x{H} · {DUR}s · recorte: {'sí' if RECORTE else 'no'} · {len(TL)} animaciones · {len(SFX)} sonidos → {HF / 'index.html'}")

# HyperFrames avanzado

HyperFrames convierte HTML + GSAP en video, cuadro por cuadro, en tu compu y gratis.
Docs: https://github.com/heygen-com/hyperframes

## La composición (build.py la arma)
- Un `<div id="root" data-composition-id="main" data-duration=…>`; línea de tiempo GSAP **pausada** en
  `window.__timelines['main']`.
- Video y audio con `class="clip"` + `data-start`, `data-duration`, `data-track-index` (único) y, si hace falta,
  `data-media-start` (desde qué segundo del archivo) y `data-volume`. HyperFrames los sincroniza; no les des play.
- Determinista: nada de `Math.random()` sin semilla, `setTimeout`, ni animaciones CSS sueltas.

## Escribir tus propias piezas
Usa los ayudantes de la plantilla y respeta el estilo (`C` colores, `F` fuentes, `RAD`, `EASE`, `RESORTE`, `LENTO`):
```python
def sello(eid, t, texto):
    """Sello redondo que cae y gira (ejemplo de pieza propia)."""
    el(f'<div id="{eid}" class="etiqueta" style="left:{W * .62}px;top:{H * .2}px;border-radius:50%;'
       f'padding:1.2em .9em;background:{C["acento"]};color:{legible(C["acento"])}">{texto}</div>')
    tw(f'tl.fromTo("#{eid}",{{opacity:0,scale:2.2,rotation:-30}},{{opacity:1,scale:1,rotation:-8,duration:.4,'
       f'ease:"{RESORTE}",immediateRender:false}},{r(t)});')
    sale(f"#{eid}", t + 2, "{opacity:0,scale:.6")
    sfx(t, "impact-bass-2", .3, 1)
```
- `el(html, capa)`: capa `frente` (default), `detras`, `mundo`, `fijo`, `trans`.
- `tw(js)`: agrega una línea a la línea de tiempo. `entra()` / `sale()` ya usan el ritmo del estilo.
- Si es algo que vas a reusar, guárdalo en tu skill personal (`crear-tu-skill.md`).

## El recorte de persona
```bash
npx hyperframes remove-background hf/media/clean.mp4 -o hf/media/persona.webm --quality best
```
(`nueva_composicion.py --recorte` lo hace por ti). Es un WebM con transparencia que la plantilla pone encima de
la capa `detras`. Corre con IA local: CoreML en Mac con chip M (~8 cuadros/s), CUDA en NVIDIA, o CPU (lento).
- Si cambias los cortes, el recorte viejo ya no coincide: vuelve a generarlo.
- Pelo muy fino o fondos del mismo color que la ropa dejan bordes: revisa un cuadro de cerca antes de usarlo
  para todo el video. Si falla, úsalo solo en el hook.

## Variables CSS animadas
GSAP anima propiedades personalizadas: `tl.fromTo("#x",{"--r":0},{"--r":100,…})`. Con eso haces máscaras
(`mask-image: radial-gradient(… calc(var(--r) * 1%) …)`), degradados que se mueven o barras que se llenan sin tocar
`transform`. El iris de la plantilla está hecho así.

## El mundo 3D (`monitor_3d`)
Usa `perspective` y contenedores anidados (pan → dolly → inclinación → giro) con `transform-style:preserve-3d`.
La función `_frame(objetivo, sx, sy, escala, rx, ry)` calcula dónde poner la cámara para que un punto del mundo
caiga en `(sx, sy)` de la pantalla a esa escala: así se encuadra sin adivinar números. `_box()` crea cajas con
6 caras coloreadas con tu paleta. Si construyes tu propio mundo 3D, parte de ahí.

## Comandos
```bash
npx hyperframes lint                                            # siempre antes de revisar
npx hyperframes snapshot --at 1,3,6 --no-end -o ../revision      # cuadros + hoja de contacto
npx hyperframes preview                                          # vista en vivo en el navegador
npx hyperframes render --quality draft --output renders/borrador.mp4
npx hyperframes render --quality high --output renders/edicion.mp4
```

## Problemas comunes
- **Algo no aparece en el render pero sí en la vista previa**: corre `lint` y sigue sus avisos.
- **Una pieza parpadea al inicio**: le falta `immediateRender:false` o su estado inicial con `tl.set(..., 0)`.
- **El texto 3D se ve plano**: el contenedor necesita `perspective` y el elemento `transform-style:preserve-3d`.
- **Fuentes que no cargan**: Google Fonts necesita internet al renderizar.
- **Disco lleno**: el render usa espacio temporal; libera unos GB antes.

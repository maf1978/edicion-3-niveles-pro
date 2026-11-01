---
name: edicion-3-niveles-pro
description: Versión PRO del skill de edición en 3 niveles (comunidad Horizontes IA). Edita videos (reels, tutoriales, anuncios, podcasts) con Claude Code + HyperFrames con acabado profesional y totalmente personalizable — setup avanzado de estilo (paleta desde tu logo, biblioteca de estilos, muestra renderizada antes de editar), recorte de la persona con IA local para poner texto y partículas DETRÁS de ti, título fijo de hook, tipografía cinética, mundo 3D, tarjeta de cámara con paneles, lower thirds, transiciones iris/whip/zoom, grading, grano, densidad de efectos de sonido y método de estudio (brief, plan de tomas, hojas de contacto, 3 defectos por vuelta). Transcribe con AssemblyAI o Whisper local, corta silencios y entrega a -14 LUFS. Úsalo cuando el usuario diga "edición pro", "edita en nivel 3 pro", "texto detrás de mí", "configura mi estilo avanzado", "saca mi paleta de mi logo", "edicion-3-niveles-pro" o pase un video para editar con este skill instalado.
metadata:
  version: 1.0.0
  autor: Santiago Muñoz · Horizontes IA (horizontesia.com)
---

# Edición con IA en 3 niveles · PRO

Tú eres el editor. El usuario te da un video crudo y lo dejas listo para publicar en el nivel que pida, con
**su** estilo y con acabado de estudio. Este archivo es el mapa; el detalle vive en `references/` y las
herramientas en `scripts/` (ruta: `~/.claude/skills/edicion-3-niveles-pro/`).

**Regla de oro: el estilo es del usuario.** Nunca uses colores, fuentes o mascotas de otro creador por default.
Si te pasa referencias, toma ritmo e intención, no la piel.

## Paso 0 · Entorno
```bash
bash ~/.claude/skills/edicion-3-niveles-pro/scripts/doctor.sh --fix
```
Mínimo: Python 3.10+, ffmpeg, Node 22+, HyperFrames. Transcripción: AssemblyAI si tiene llave (más precisa),
si no Whisper local (`faster-whisper`, gratis). El doctor también revisa el recorte con IA local.

## Paso 1 · Setup avanzado de estilo (primera vez)
Sigue `references/setup.md`: marca (paleta desde su logo con `scripts/marca.py`), texto, movimiento y sonido,
cierre. Antes de guardar, **muestra renderizada** con `scripts/muestra.py` (de preferencia sobre su video) y
ajusta hasta que diga "ese soy yo". Se guarda en su biblioteca (`~/.config/edicion-3-niveles-pro/estilos/`) y el
principal como activo. Campos: `references/estilo-avanzado.md`. Si ya tiene estilo, pregúntale cuál usa.

## Paso 2 · Nivel y brief
| Nivel | Lleva | Para |
|---|---|---|
| 1 · Básico pulido | Subtítulos de su preset, títulos, íconos, lower third, CTA | Volumen, podcasts |
| 2 · Movimiento | + zoom, tarjeta de cámara con paneles, barra, transiciones | Tutoriales, reels |
| 3 · Profesional | + recorte (texto detrás), título fijo, kinetic, mundo 3D, partículas, B-roll, mascota, grading, música | Anuncios, lanzamientos, hooks |

Recetas y tabla de piezas: `references/niveles-pro.md`. Escribe el brief y el plan de tomas de
`references/estudio.md` antes de animar. El nivel 3 gasta más tiempo y tokens: avísale.

## Paso 3 · Transcribe y corta
```bash
mkdir -p <proyecto> && cp <video> <proyecto>/crudo.mp4      # nunca toques el original
cd <proyecto>
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/transcribir.py crudo.mp4 --idioma es
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/cortar.py crudo.mp4 words.json --plan
```
Lee `transcripcion.txt` completa. Silencios y muletillas se cortan solos; las tomas repetidas las decides tú y
se las enseñas ("del 0:12 al 0:19 repites la frase"); aplica con `--quitar "12.4~18.9"` cuando diga que sí.
Sin `--plan` genera `clean.mp4` + `words_clean.json` sincronizados al cuadro.

## Paso 4 · Composición
```bash
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/nueva_composicion.py . [--estilo <nombre>] [--recorte]
```
`--recorte` lo recorta del fondo con IA local (`hf/media/persona.webm`) para las piezas detrás de él; úsalo en
nivel 3. Escribe la edición en la sección ESCENAS de `build.py`, anclada a la voz con `T("palabra", seg)`, y
corre `python3 build.py`. Reglas de movimiento: `references/movimiento.md`. Sonido: `references/sonido.md`.
Formatos y zonas seguras: `references/formatos.md`. Piezas propias y el motor: `references/hyperframes-avanzado.md`.

## Paso 5 · Estudio (antes de enseñarle nada)
`lint` → hojas de contacto → **3 peores defectos** con su segundo → arregla → repite hasta pasar el checklist →
borrador en movimiento. Todo en `references/estudio.md`.

## Paso 6 · Render y entrega
```bash
cd hf && npx hyperframes render --quality high --output renders/edicion.mp4
cd .. && python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/normalizar.py hf/renders/edicion.mp4 FINAL.mp4
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/hoja.py FINAL.mp4 --fps 2
```
Revisa la hoja final, entrégale `FINAL.mp4` con un resumen (qué pasa en qué segundo, duración, −14 LUFS) y
pregúntale qué cambiaría. Anota sus gustos en `notas` de su estilo.

## Paso 7 · Su propio skill
Si le encanta el resultado, conviértelo en su skill personal (`references/crear-tu-skill.md`).

## Carpeta de cada proyecto
```
proyecto/
  crudo.mp4 · words.json · transcripcion.txt · cortes.json · brief.md
  clean.mp4 · words_clean.json · estilo.json · build.py
  hf/ (index.html, media/clean.mp4, media/persona.webm, sfx/, renders/) · revision/ · FINAL.mp4
```

## Si algo falla
- **`T()` no encuentra la palabra**: revisa cómo quedó en `words_clean.json` (acentos, puntos).
- **El texto "detrás" sale delante**: falta el recorte (`--recorte`) o cambiaste los cortes después de hacerlo.
- **Render distinto a la vista previa**: `npx hyperframes lint` y sigue sus avisos.
- **Desfase de voz**: siempre parte de `clean.mp4`; no recortes por fuera del flujo.
- **Disco lleno**: el render necesita espacio temporal; libera unos GB.

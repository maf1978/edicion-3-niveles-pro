# 🎬 Edición con IA en 3 niveles · PRO

La versión de la **comunidad Horizontes IA** del skill que convierte **Claude Code** en tu editor de video.
Mismos 3 niveles que el gratis, con acabado de estudio y todo personalizable.

| | Gratis | **PRO** |
|---|---|---|
| Estilo | Entrevista + 6 estilos base | **Setup avanzado**: paleta desde tu logo, 10 estilos base, biblioteca de estilos propios, muestra renderizada antes de editar |
| Personalización | Colores, fuentes, ritmo | + radios, sombras, curvas de movimiento, 4 presets de subtítulos, transición, densidad de sonido, color, grano, CTA, tu mascota |
| Nivel 1 | Subtítulos, títulos, íconos | + lower thirds y tarjeta de cierre |
| Nivel 2 | Zooms, layouts, barra | + tarjeta de cámara con resorte y paneles que se acomodan solos, transiciones iris / whip / zoom / barrido |
| Nivel 3 | 3D, partículas, B-roll, color | + **recorte con IA local: texto y partículas DETRÁS de ti**, título fijo de hook, tipografía cinética, mundo 3D (monitor), grading con presets |
| Método | Revisión con checklist | **Método de estudio**: brief, plan de tomas, hojas de contacto, 3 defectos por vuelta, borrador en movimiento |

## Instalación

Abre **Claude Code** (app de Claude → pestaña **Código**) y pégale esto:

> Instala el skill https://github.com/santmun/edicion-3-niveles-pro y hazme el setup avanzado de mi estilo para editar mi primer video.

O a mano:
```bash
git clone https://github.com/santmun/edicion-3-niveles-pro ~/.claude/skills/edicion-3-niveles-pro
bash ~/.claude/skills/edicion-3-niveles-pro/scripts/doctor.sh --fix
```
Si ya usabas el gratis, tu estilo se migra solo.

## Cómo usarlo

- *"Hazme el setup avanzado de estilo; aquí está mi logo."*
- *"Edita este reel en nivel 3 pro, con texto detrás de mí en el hook."*
- *"Nivel 2 para este tutorial, con mi estilo youtube-sobrio."*
- *"Enséñame una muestra del estilo terracota sobre mi video."*

## Lo que necesitas
- **Claude** con Claude Code (desde el plan de 20 USD; esfuerzo medio si estás en ese plan).
- **Python 3.10+, ffmpeg y Node 22+** (el doctor te dice cómo instalarlos) y **HyperFrames** (gratis).
- **Transcripción:** [AssemblyAI](https://www.assemblyai.com) si tienes llave (más precisa) o **Whisper local**, gratis.
- **Recorte de persona:** corre en tu compu. En Mac con chip M va rápido (~8 cuadros/s); sin GPU, úsalo en clips cortos.

## Qué hay adentro
```
SKILL.md                el flujo completo que sigue Claude
references/             setup · estilo-avanzado · niveles-pro · movimiento · sonido · estudio · formatos · hyperframes-avanzado · crear-tu-skill
estilos/                10 estilos base
scripts/                doctor · marca · muestra · transcribir · cortar · nueva_composicion · normalizar · hoja
templates/build_pro.py  todas las piezas pro
assets/sfx/             16 efectos de sonido libres (Pixabay)
```

## Créditos
Efectos de sonido de [Pixabay](https://pixabay.com/sound-effects/) bajo su licencia de contenido (`assets/sfx/CREDITS.md`).
Animación y recorte con [HyperFrames](https://github.com/heygen-com/hyperframes).

Hecho para la comunidad **Horizontes IA** → [horizontesia.com](https://horizontesia.com)

# Convierte un estilo aprobado en tu propio skill

Cuando el usuario diga "así quiero todos mis videos", conviértelo en su skill personal: el siguiente video sale
más rápido y más parecido, sin repetir el setup ni las correcciones.

## Qué guardar
1. **El estilo** final de su biblioteca (`~/.config/edicion-3-niveles-pro/estilos/<nombre>.json`), con `notas`.
2. **La receta**: el bloque ESCENAS del `build.py` aprobado, limpio y comentado por tramo (hook, cuerpo, cierre).
3. **Piezas propias** que hayas escrito para él (funciones nuevas), en un archivo aparte (`piezas.py`).
4. **La hoja de contacto** del video aprobado (`revision/contact-sheet.jpg`) para comparar los siguientes.
5. **Sus reglas en sus palabras**: "el título siempre arriba", "nada de emojis", "zoom en cada número",
   "sin partículas".

## Estructura
Pregúntale el nombre (por ejemplo `mis-reels`) y crea `~/.claude/skills/<nombre>/`:
```
SKILL.md          qué es, cuándo usarlo, su receta paso a paso y sus reglas
estilo.json       su estilo
piezas.py         sus piezas propias (si hay)
referencia/       build.py aprobado + contact-sheet.jpg
```
En el SKILL.md:
- El flujo reutiliza los scripts de este skill: `~/.claude/skills/edicion-3-niveles-pro/scripts/`
  (transcribir → cortar → `nueva_composicion.py --estilo <nombre>` → escenas con su receta → estudio → render).
- La receta como pasos concretos: "hook: `titulo_fijo` con la promesa + `texto_detras` en la palabra clave;
  cada paso con `tarjeta_camara` + `panel`; cierre con `cta('comenta', 'GUIA')`".
- Para cargar sus piezas propias: copiar `piezas.py` junto al `build.py` del proyecto y agregar
  `exec(open("piezas.py").read())` arriba de ESCENAS.

Pruébalo con un video nuevo antes de darlo por terminado y ajústalo con lo que diga.

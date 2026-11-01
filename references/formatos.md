# Formatos: vertical y horizontal

La plantilla saca el tamaño del video (`W`, `H`) y ajusta zonas seguras, tamaños de texto y posiciones sola.
Lo que cambia es cómo piensas la composición.

## Vertical 9:16 (Reels, TikTok, Shorts) · 1080×1920
- **Zona segura**: nada importante arriba del 12 % (`SAFE_T`), abajo del 80 % (`SAFE_B`) ni en el 14 % derecho
  (`SAFE_R`): ahí van la interfaz, los botones y la descripción.
- Subtítulos abajo (en `SUB_TOP`); todo lo demás llega como máximo a `LIBRE_B` para no chocar con ellos.
- La cara suele estar entre el 25 % y el 55 % de la altura: los títulos van arriba, los paneles arriba con la
  tarjeta de cámara abajo.
- Texto grande: titulares ≥ 11 % del ancho; nunca menos de 40 px de alto en ningún texto.
- `texto_detras` funciona mejor a la altura de la cabeza (default 20 % de la altura).

## Horizontal 16:9 (YouTube) · 1920×1080
- Zona segura más amplia (7 %–90 % de alto, 95 % de ancho), pero la barra de YouTube tapa el 10 % de abajo al pausar.
- Layouts laterales: `tarjeta_camara(t, "izq")` o `"der"` y el panel ocupa el otro lado.
- Subtítulos más chicos (6 % de la altura) y opcionales en videos largos.
- En videos largos usa nivel 1–2 casi todo el tiempo y guarda el nivel 3 para el hook y los cambios de sección.

## Grabaciones de pantalla (tutoriales)
- La pantalla manda: tu cámara va como `tarjeta_camara(t, "esquina")` y regresa a `"completa"` cuando hablas a cámara.
- `zoom(t, 1.6, foco=(x, y))` en la parte de la pantalla que estás explicando; regresa con `hasta=`.

## Render
| Para | Comando |
|---|---|
| Revisar ritmo | `npx hyperframes render --quality draft --output renders/borrador.mp4` |
| Publicar | `npx hyperframes render --quality high --output renders/edicion.mp4` |
| 4K (si el original lo es) | agrega `--resolution portrait-4k` (vertical) o `landscape-4k` (horizontal) |

El render 4K tarda ~4 veces más. Para redes sociales, 1080 en calidad alta es suficiente.

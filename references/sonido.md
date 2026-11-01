# Sonido: efectos, música y volumen

El sonido es la mitad de lo que se siente "pro". Mal usado, es lo primero que delata una edición barata.

## Densidad (`sonido.densidad` en estilo.json)
Cada `sfx()` lleva un nivel. Suena si la densidad del estilo lo permite:
| Densidad | Suena | Para |
|---|---|---|
| ninguno | nada | podcasts, contenido serio |
| minimo | nivel 1: transiciones, título del hook, golpes de 3D, CTA | corporativo, educativo sobrio |
| medio | + nivel 2: títulos, zooms, tarjeta, B-roll, partículas | la mayoría de reels |
| alto | + nivel 3: etiquetas, cada palabra del kinetic, paneles | contenido muy energético |

Las piezas ya traen su efecto y su nivel. Si agregas uno a mano: `sfx(t, "whoosh", .3, nivel=2)`.

## Los 16 efectos incluidos (`hf/sfx/`)
`pop` · `whoosh` · `whoosh-short` · `whoosh-cinematic` · `click` · `click-soft` · `impact-bass-1` · `impact-bass-2` ·
`riser` · `sparkle` · `typing` · `key-press` · `notification` · `ping` · `chime` · `glitch-1`

## Reglas
- **El golpe va en el cuadro del golpe.** El `whoosh` empieza ANTES del movimiento (lo que dura la cubierta de
  la transición); el `impact` cae en el cuadro donde el elemento aterriza.
- **Un `riser` termina en el golpe**, no después. Colócalo en `t_golpe - duración_del_riser`.
- **Nada de campanas ni timbres** (`chime`, `notification`) como relleno: suenan a plantilla. Solo si lo que se
  dice ES una notificación.
- **Bajo la voz**: efectos entre 0.2 y 0.35 de volumen (6–10 dB debajo). Si compiten con una palabra, baja o
  mueve el efecto, nunca la voz.
- **No repitas el mismo efecto** más de 3 veces seguidas: alterna `whoosh` / `whoosh-short`, `pop` / `click`.
- **Silencio también es edición**: antes de un remate, 0.3–0.5 s sin efectos hacen que el golpe pegue más.

## Música
- Solo con derechos de uso (la suya o de una biblioteca con licencia). `musica("archivo.mp3", .08–.15)`.
- Que baje en las frases importantes: si hace falta, corta la música en dos tramos con volúmenes distintos.
- El final de la música coincide con el cierre (`cta`), no se corta a media frase.

## Volumen final
`normalizar.py` deja el video a −14 LUFS (lo que piden Instagram, TikTok y YouTube) en dos pasadas.
Revisa con audífonos el primer segundo y el último: ahí es donde más se nota un efecto mal puesto.

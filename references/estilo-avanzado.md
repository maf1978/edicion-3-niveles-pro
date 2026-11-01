# estilo.json (versión 2): todos los campos

```json
{
 "version": 2,
 "nombre": "Terracota",
 "nombre_marca": "@tumarca",
 "formato": "9:16",
 "colores": {"fondo": "#2A1D17", "texto": "#F6EDE3", "acento": "#E07A5F", "secundario": "#81B29A"},
 "fuentes": {"titulos": "Fraunces", "pesoTitulos": 800, "texto": "Manrope", "pesoTexto": 700},
 "radio": 20,
 "sombras": true,
 "movimiento": {"perfil": "cinematico", "entrada": "expo.out", "resorte": "power3.inOut", "velocidad": 1.5},
 "subtitulos": {"activos": true, "preset": "karaoke", "modo": "palabra", "posicion": "abajo", "mayusculas": false,
                "colorActivo": "acento", "palabrasPorBloque": 3, "tamano": 64, "color": "#FFFFFF"},
 "transicion": "iris",
 "sonido": {"densidad": "medio"},
 "sfx": true,
 "color": "calido",
 "grano": true,
 "iconos": "emoji",
 "cierre": "seguir",
 "mascota": null,
 "logo": null,
 "musica": null,
 "referencias": [],
 "notas": ""
}
```

| Campo | Qué controla | Valores |
|---|---|---|
| `formato` | Solo informativo (el tamaño real sale del video) | `9:16`, `16:9` |
| `colores.fondo` | Paneles, transiciones, borde de los títulos | hex |
| `colores.texto` | Titulares y textos de las piezas | hex |
| `colores.acento` | Lo que se resalta (`*palabra*`), palabra activa, barra, marco de la tarjeta | hex, uno solo |
| `colores.secundario` | Sombra 3D de los títulos, bordes, partículas de apoyo | hex |
| `fuentes` | Titular y texto (Google Fonts) | nombre + peso |
| `radio` | Redondeo de paneles, tarjetas, etiquetas (px a 1080) | 0 (cuadrado) a 40 (muy redondo) |
| `sombras` | Sombra suave bajo paneles y etiquetas | true/false |
| `movimiento.perfil` | Ritmo de entradas y resortes | `suave`, `energico`, `cinematico`, `seco` |
| `movimiento.entrada` | Curva de entrada (GSAP) | p. ej. `back.out(1.9)`, `expo.out`, `power4.out` |
| `movimiento.resorte` | Curva de las piezas que viajan (tarjeta, panel, CTA) | p. ej. `back.out(1.4)` |
| `movimiento.velocidad` | Multiplica la duración de las entradas | 0.6 (rápido) a 1.6 (lento) |
| `subtitulos.preset` | Look de subtítulos | `karaoke`, `caja`, `minimal`, `bold` |
| `subtitulos.modo` | Ilumina palabra por palabra o muestra la frase | `palabra`, `frase` |
| `subtitulos.color` | Color base sobre el video (casi siempre blanco) | hex |
| `transicion` | Default de `transicion()` | `barrido`, `iris`, `whip`, `zoom` |
| `sonido.densidad` | Qué efectos suenan: nivel 1 esenciales, 2 normales, 3 detalle | `ninguno`, `minimo`, `medio`, `alto` |
| `color` | Grading default de `grading()` | `natural`, `calido`, `frio`, `cine` |
| `grano` | Grano de película encima de todo | true/false |
| `cierre` | Default de `cta()` | `seguir`, `comenta`, `link` |
| `mascota` | Ruta a SU personaje (PNG transparente) para `mascota()` | ruta o null |
| `notas` | Lo que le gusta y lo que no, en sus palabras | texto |

## Perfiles de movimiento
| Perfil | Entrada | Resorte | Velocidad | Se siente |
|---|---|---|---|---|
| suave | power2.out | back.out(1.2) | 1.25 | limpio, tranquilo, corporativo |
| energico | back.out(1.9) | back.out(1.7) | 0.85 | rebote corto, reels |
| cinematico | expo.out | power3.inOut | 1.5 | entradas largas, anuncios premium |
| seco | power4.out | power4.out | 0.7 | sin rebote, editorial, suizo |

## Reglas que no se negocian
- Un solo acento por pieza; el secundario solo apoya. Máximo dos fuentes.
- Contraste: texto/fondo ≥ 7:1 y acento/fondo ≥ 3:1 (`marca.py` lo mide).
- Los subtítulos van claros sobre video aunque la marca sea de fondo claro (la plantilla lo hace sola).

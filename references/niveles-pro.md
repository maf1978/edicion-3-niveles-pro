# Los 3 niveles, versión pro

Mismos tres niveles que el skill gratis, con piezas más pulidas y más control. Todas viven en `build.py`, leen
`estilo.json` y se anclan a la voz con `T("palabra", segundo_aprox)` (`fin=True` da cuándo termina la palabra).

**Regla del editor:** cada pieza dice algo de lo que se oye en ese segundo. Si no significa nada, no va.
Ritmo: algo cambia cada 2–4 s en nivel 1, cada 1.5–3 s en nivel 2 y casi siempre en nivel 3.

## Capas (de atrás hacia adelante)
| Capa | Qué va ahí | Se mueve con la cámara |
|---|---|---|
| video | tu toma (`clean.mp4`) | sí |
| **detrás** | texto, kinetic y partículas *detrás de ti* (requiere `--recorte`) | sí |
| tu recorte | `persona.webm` encima de lo de detrás | sí |
| frente | títulos, etiquetas, íconos, 3D, partículas | sí |
| mundo | `monitor_3d` | no |
| fijo | título fijo, lower third, panel, barra, CTA, B-roll completo | no |
| subtítulos · transiciones · grano | arriba de todo | no |

## Nivel 1 · Básico pulido
`titulo` · `etiqueta` · `icono` · `lower_third` · `cta` + subtítulos del preset.
```python
lower_third("yo", 1.0, "Ana Ruiz", "Nutrióloga deportiva")
titulo("t1", T("errores", 3.0), "3 *errores* al entrenar")
icono("i1", T("agua", 9.0), "💧", W * .70, H * .30, rebote=True)
etiqueta("e1", T("gratis", 14.0), "100% *gratis*", W * .08, H * .55)
cta(DUR - 2.5, "comenta", "RUTINA")
```

## Nivel 2 · Movimiento con intención
Todo el 1 + `zoom` · `barra_progreso` · `tarjeta_camara` + `panel` · `transicion` · `sin_subtitulos`.
```python
zoom(T("importante", 6.0), 1.15, foco=(W * .5, H * .35), hasta=T("importante", 6.0) + 1.3)
barra_progreso(0, DUR)
tarjeta_camara(T("primero", 12.0), "abajo")                      # tu cámara viaja a tarjeta con resorte
panel("p1", T("primero", 12.0), T("segundo", 18.0), "<small>PASO 1</small>Descarga <span class=ac>Claude</span>")
tarjeta_camara(T("segundo", 18.0), "completa")                   # regresa a pantalla completa
transicion(T("ahora", 25.0))                                       # la de tu estilo, o "iris" / "whip" / "zoom" / "barrido"
```
- `tarjeta_camara(t, pos)`: `abajo`, `arriba`, `izq`, `der`, `esquina`, `completa`. El `panel` se acomoda solo en
  el espacio libre que deja la última posición. Para una captura: `'<img src="media/captura.png" style="width:100%;border-radius:16px">'`.
- No mezcles `zoom`/`camara` con una tarjeta activa (los tres mueven el escenario).

## Nivel 3 · Profesional
Todo el 2 + `monitor_3d` · `titulo_fijo` · `texto_detras` · `kinetic` · `texto_3d` · `particulas` · `camara` ·
`broll` · `mascota` · `grading` · `musica` · efectos de sonido por densidad.
```python
monitor_3d(.3, 2.6)                                               # hook: la cámara revela que estás dentro de un monitor 3D y se zambulle de vuelta
titulo_fijo(0, 4.5, "3 *ERRORES*", "que te frenan", pops=[(T("tres", .5), ".p0")])
texto_detras("big", T("nunca", 5.0), "*NUNCA*", dur=1.4)           # palabra gigante detrás de tu cabeza
kinetic("k1", T("conocer", 6.0), "conocer el *último*")           # se apila palabra por palabra al decirla; esconde subtítulos
particulas("pp", T("último", 6.5), W * .5, H * .28, capa="detras") # estalla detrás de ti
camara(T("imagina", 9.0), 1.06, dur=3.0)                          # deriva lenta
broll("b1", T("ciudad", 12.0), T("ciudad", 12.0) + 2.5, "ciudad.mp4")
mascota("m1", T("listo", 20.0), T("listo", 20.0) + 2.5, W * .62, H * .52)   # solo SU mascota
grading(0, DUR)                                                    # preset del estilo
musica("musica.mp3", .1)
```
- `--recorte` (en `nueva_composicion.py`) es lo que hace posible `texto_detras`, `kinetic(..., capa="detras")` y
  `particulas(..., capa="detras")`. Sin recorte, esas piezas quedan al frente (semitransparentes) y no truena nada.
- `monitor_3d` va en los primeros 2–5 s: el título fijo y los subtítulos siguen encima.
- `broll`: si el usuario tiene un generador de video con IA conectado, genera tomas del concepto en SU paleta y
  en su formato. Si no, tomas propias o de bancos con licencia. **Nunca gastes créditos sin preguntarle.**

## Combinaciones que funcionan
| Contenido | Receta |
|---|---|
| Podcast / video largo | Nivel 1 todo el video + `lower_third` al inicio + `zoom` en las 3 frases más fuertes |
| Tutorial | Nivel 2: `tarjeta_camara` + `panel` por paso, `barra_progreso`, `transicion` entre secciones |
| Reel educativo | Hook nivel 3 (`titulo_fijo` + `texto_detras` o `monitor_3d`), cuerpo nivel 2, `cta` |
| Anuncio / lanzamiento | Nivel 3 en hook y cierre, nivel 2 en medio, `grading` + `grano` + música |

## Tabla de piezas
| Pieza | Firma |
|---|---|
| titulo | `titulo(eid, t, texto, dur=2.5, y=None, tam=None, capa="frente")` |
| etiqueta | `etiqueta(eid, t, texto, x, y, dur=2.2)` |
| icono | `icono(eid, t, contenido, x, y, tam=None, dur=2.0, rebote=False)` |
| lower_third | `lower_third(eid, t, nombre, rol, dur=3.2)` |
| cta | `cta(t, tipo=None, palabra=None, texto=None)` |
| zoom | `zoom(t, escala=1.15, dur=.35, foco=None, hasta=None)` |
| barra_progreso | `barra_progreso(t0, t1)` |
| tarjeta_camara | `tarjeta_camara(t, pos="abajo", d=.6)` |
| panel | `panel(eid, t0, t1, contenido, caja=None)` |
| transicion | `transicion(t, tipo=None)` |
| sin_subtitulos | `sin_subtitulos(t0, t1)` |
| monitor_3d | `monitor_3d(t0, t1, etiqueta_txt=None)` |
| titulo_fijo | `titulo_fijo(t0, t1, linea1, linea2="", pops=())` |
| texto_detras | `texto_detras(eid, t, texto, dur=2.6, y=None, tam=None)` |
| kinetic | `kinetic(eid, t0, frase, y=None, tam=None, dur=None, capa="frente", ocultar_subs=True)` |
| texto_3d | `texto_3d(eid, t, texto, dur=2.6, y=None, tam=None)` |
| particulas | `particulas(eid, t, x, y, n=48, color=None, radio=None, semilla=7, dur=1.3, capa="frente")` |
| camara | `camara(t, escala=1.0, x=0, y=0, rot=0, dur=1.2, ease="sine.inOut")` |
| broll | `broll(eid, t0, t1, archivo, modo="completo" \| "tarjeta", desde=0)` |
| mascota | `mascota(eid, t0, t1, x, y, tam=None, entrada="salto" \| "asoma" \| "pop")` |
| grading | `grading(t0, t1, filtro=None)` |
| musica | `musica(archivo, vol=.12)` |
| sfx | `sfx(t, nombre, vol=.32, nivel=2)` |

`*palabra*` pinta esa palabra con el acento en cualquier texto. Variables útiles: `W`, `H`, `DUR`, `SAFE_T`,
`SAFE_B`, `LIBRE_B` (lo más abajo que puede llegar una pieza sin chocar con los subtítulos), `C`, `F`.

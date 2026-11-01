# Movimiento: reglas por tipo de pieza

Lo que separa una edición pulida de una amateur no es cuántas cosas se mueven, sino **cómo** y **cuándo**.

## Una cosa protagonista a la vez
En cada momento hay UN elemento que el ojo debe seguir. Si entran dos, el segundo llega 0.12–0.25 s después
(escalonado), nunca al mismo tiempo. La cara de la persona cuenta como protagonista: si habla de algo
emocional, no la tapes con texto.

## Por tipo de pieza
| Pieza | Entra | Se queda | Sale | Curva |
|---|---|---|---|---|
| Titular | 0.35–0.5 s, desde abajo y un poco chico | lo que dura la idea (≥ 1.2 s) | 0.25–0.3 s, hacia arriba | entrada del perfil, salida `power2.in` |
| Etiqueta / ícono | 0.3 s | 1.5–2.5 s | 0.25 s | igual |
| Palabra gigante (detrás) | 0.5–0.6 s, de grande a normal | 1–1.6 s | 0.35 s | `power3.out` |
| Kinetic | una palabra por palabra dicha, 0.3 s cada una | hasta 1 s después de la última | 0.3 s | resorte del perfil |
| Tarjeta de cámara / panel | 0.5–0.7 s viajando | el tramo completo | regresa con el mismo resorte | resorte del perfil |
| Zoom (punch-in) | 0.3–0.4 s | 0.8–1.5 s | 0.35 s de regreso | `power3.out` / `power3.inOut` |
| Cámara (deriva) | 2–4 s, escala 1.03–1.08 | — | — | `sine.inOut` |
| Transición | 0.25–0.35 s cubre, 0.3–0.4 s descubre | — | — | `power3.in` / `power3.out` |

Las duraciones del perfil (`movimiento.velocidad`) multiplican las entradas; las salidas siempre son cortas.

## Reglas finas
- **Entradas lentas, salidas rápidas.** Lo que se va no necesita atención.
- **Nada aparece de golpe** (excepto un corte intencional): mínimo 3 cuadros de entrada.
- **Que se lea**: un texto necesita 0.25 s por palabra + 0.5 s en pantalla antes de salir.
- **Rebote con mesura**: `back.out(1.2–1.9)`. Arriba de 2 se ve caricatura. `elastic` solo en íconos.
- **Movimiento en el eje de la mirada**: si la persona mira a la derecha, el texto entra por la derecha.
- **Cambios de layout en la palabra que los justifica** (`T("primero")`), nunca a medio enunciado.
- **Cortes + movimiento**: no metas un zoom en el mismo cuadro de un corte de silencio; recórrelo 3–4 cuadros.
- **Partículas**: solo en remates (un dato, un "listo", una revelación), máximo 2–3 por minuto.
- **3D**: uno por video corto (hook o remate). Si todo es 3D, nada lo es.

## Reglas técnicas (HyperFrames)
- No pongas `transform` en el CSS de un elemento que GSAP anima; anima un contenedor.
- Estados iniciales ocultos con `opacity:0` en CSS o `tl.set(..., 0)`; `fromTo` con `immediateRender:false`.
- Nada de `Math.random()` sin semilla ni animaciones CSS sueltas: todo en la línea de tiempo.
- GSAP puede animar variables CSS (`"--r"`): así está hecho el iris. Úsalo para máscaras y degradados.

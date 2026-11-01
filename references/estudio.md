# Método de estudio: brief → plan de tomas → hojas → 3 defectos → render

La diferencia entre "una edición generada" y una edición pro es que alguien la revisó con criterio. Ese alguien
eres tú. Nunca le enseñes al usuario algo que no hayas visto cuadro por cuadro.

## 1 · Brief (antes de tocar build.py)
Escríbelo en 5 líneas en `brief.md` dentro del proyecto:
- **De qué trata** el video en una frase y **qué tiene que sentir** quien lo ve.
- **Plataforma y formato** (reel 9:16, YouTube 16:9…).
- **El hook**: qué pasa en los primeros 2 s para que no deslicen.
- **El remate**: el momento más fuerte, ahí va lo más vistoso.
- **Lo que el usuario pidió** en sus palabras y lo que dijo que NO quiere (`notas` del estilo).

## 2 · Plan de tomas (shotlist)
Lee `transcripcion.txt` completa y arma una tabla por tramos de 2–6 s:

| Tiempo | Lo que dice | Pieza | Por qué |
|---|---|---|---|
| 0.0–2.6 | "Estos son los 3 niveles…" | monitor_3d + titulo_fijo | hook: revela el mundo y fija la promesa |
| 4.6–5.7 | "…resultados profesionales" | texto_detras "PRO" | la palabra clave, detrás de la cabeza |

Si una fila no tiene "por qué", sobra. Enséñale el plan al usuario solo si el video es largo o caro de rehacer.

## 3 · Hojas de contacto
```bash
cd hf && npx hyperframes lint
npx hyperframes snapshot --at 0.5,1.5,3,5,8,12 --no-end -o ../revision         # momentos clave
npx hyperframes snapshot --at 7.4,7.5,7.6,7.7,7.8 --no-end -o ../revision-tr   # cuadros seguidos en transiciones
```
Abre `contact-sheet.jpg` y juzga lo que se VE, no lo que querías hacer.

## 4 · Los 3 peores defectos
Anota los 3 peores con su segundo exacto ("7.7 s: el texto sigue en pantalla después del iris"), arregla solo
esos, vuelve a sacar esos cuadros. Repite hasta que el checklist pase. Tres por vuelta: si arreglas diez a la vez,
rompes cosas que ya estaban bien.

### Checklist
- [ ] Cuadro 1 ya engancha (algo pasa antes de 0.5 s).
- [ ] Todo se lee en un celular (imagínalo a 360 px de ancho), con contraste.
- [ ] Nada tapa ojos ni boca. Lo que está "detrás" de verdad queda detrás (recorte limpio, sin halo).
- [ ] Nada importante en la zona de la interfaz de la app (`formatos.md`).
- [ ] Solo los colores y fuentes del estilo; un acento por pieza.
- [ ] Una cosa protagonista a la vez (`movimiento.md`).
- [ ] Ningún texto en pantalla repite lo que dicen los subtítulos (o se esconden con `sin_subtitulos`).
- [ ] Nada se queda colgado después de una transición o un corte.
- [ ] Subtítulos en sincronía (palabra activa = la que se dice).
- [ ] Efectos en el golpe, bajo la voz, sin campanas de relleno (`sonido.md`).
- [ ] El último cuadro funciona como cierre.

## 5 · Borrador en movimiento
Las hojas no muestran ritmo. Antes del render final, renderiza un borrador rápido y velo completo:
```bash
npx hyperframes render --quality draft --output renders/borrador.mp4
```
Busca: tiempos muertos, cosas que entran demasiado rápido para leerse, efectos fuera de lugar.

## 6 · Render final y entrega
```bash
npx hyperframes render --quality high --output renders/edicion.mp4
cd .. && python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/normalizar.py hf/renders/edicion.mp4 FINAL.mp4
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/hoja.py FINAL.mp4 --fps 2
```
Revisa la hoja del final. Entrégale el `FINAL.mp4` con un resumen corto: qué pasa en qué segundo, duración y
−14 LUFS. Pregúntale qué cambiaría y anota sus gustos en `notas` del estilo.

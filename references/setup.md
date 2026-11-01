# Setup avanzado de estilo

Se hace una vez y deja al usuario con **una biblioteca de estilos propios** (no uno solo) y uno activo.
- Biblioteca: `~/.config/edicion-3-niveles-pro/estilos/<nombre>.json`
- Activo (el que se usa si no dice otro): `~/.config/edicion-3-niveles-pro/estilo.json`
- Esquema completo de cada campo: `estilo-avanzado.md`

Si ya usaba el skill gratis, `nueva_composicion.py` migra su `~/.config/edicion-3-niveles/estilo.json` solo.
Pregúntale si quiere partir de ese o rehacerlo.

## Cómo conducirlo
- Cuatro rondas cortas, una a la vez, siempre con opciones concretas y un "otra / lo armo yo".
- Prisa → que elija un estilo base y su marca, y listo; el resto se queda en los valores del preset.
- Referencias (capturas, links de creadores): analízalas y dile en una línea qué tomas de cada una
  ("de esta tomo el ritmo seco y los subtítulos en caja; los colores serán los tuyos"). Nunca clones
  la piel de otro creador (paleta + tipografía + mascota). Toma intención y ritmo, no identidad.

### Ronda 1 · Marca
1. **¿Tienes logo o colores de marca?**
   - Logo → `python3 scripts/marca.py logo.png` saca la paleta, propone fondo/texto/acento/secundario y revisa
     el contraste. Si el acento sale bajo, prueba `--claro` o ajusta a mano.
   - Hex → úsalos y revisa el contraste igual (texto/fondo ≥ 7:1, acento/fondo ≥ 3:1).
   - Nada → enséñale los 10 estilos base (`estilos/`, tabla abajo) y que escoja 2 o 3 para comparar.
2. **Nombre de marca o handle** (`nombre_marca`): sale en el lower third y en el cierre.
3. **¿Mascota o personaje?** Solo si es SUYO: imagen PNG con fondo transparente. Guárdala y pon la ruta en
   `mascota`. Si no tiene, no inventes una ni uses la de otro creador.

### Ronda 2 · Texto
4. **Subtítulos** (preset): `karaoke` (palabra activa en color, borde negro), `caja` (la palabra activa en una
   caja de color), `minimal` (frase completa, sombra suave), `bold` (mayúsculas gruesas, 2 palabras por bloque).
   Posición: abajo / centro / arriba.
5. **Tipografía**: la pareja del preset o la suya (Google Fonts o instalada). Máximo dos familias.

### Ronda 3 · Movimiento y sonido
6. **Ritmo** (`movimiento.perfil`): `suave` · `energico` · `cinematico` · `seco`. Si quiere afinar, `entrada`,
   `resorte` y `velocidad` (ver `movimiento.md`).
7. **Transición entre secciones**: `barrido` · `iris` · `whip` · `zoom`.
8. **Densidad de efectos de sonido**: `ninguno` · `minimo` (solo golpes clave) · `medio` · `alto`.
9. **Color del video**: `natural` · `calido` · `frio` · `cine`, y si quiere grano de película.

### Ronda 4 · Cierre
10. **Llamado a la acción**: `seguir` · `comenta` (con palabra clave) · `link`.

## Antes de guardar: la muestra
```bash
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/muestra.py <estilo.json|nombre> --cuadros          # 2 cuadros, rápido
python3 ~/.claude/skills/edicion-3-niveles-pro/scripts/muestra.py <estilo.json|nombre> --video crudo.mp4  # clip de 4.5 s sobre su video
```
Enséñale la muestra (de preferencia sobre su propio video) y ajusta hasta que diga "ese soy yo".
Guarda en la biblioteca con su nombre y, si es el principal, cópialo también como `estilo.json` activo.
Anota en `notas` lo que dijo que le gustó y lo que no: es la memoria de su estilo.

## Varios estilos
Es normal tener uno por formato ("reels-energico", "youtube-sobrio") o por cliente. Para usar uno:
`nueva_composicion.py <proyecto> --estilo reels-energico`.

## Los 10 estilos base (`estilos/`)
| Archivo | Fondo · Acento · Secundario | Titular / texto | Ritmo | Subtítulos | Transición |
|---|---|---|---|---|---|
| lima-electrica | #101010 · #C6FF3D · #5B5BFF | Bricolage Grotesque / DM Sans | energico | karaoke | barrido |
| coral-pastel | #FFF4EC · #FF6B6B · #4ECDC4 | Fredoka / Nunito | energico | caja | iris |
| azul-confianza | #0F1C2E · #3B82F6 · #22C55E | Sora / Inter | suave | minimal | barrido |
| violeta-neon | #0D0221 · #B14AED · #FF2E88 | Unbounded / Outfit | energico | bold | zoom |
| editorial-verde | #F4F1EA · #2F7D5B · #E36414 | DM Serif Display / DM Sans | cinematico | minimal | iris |
| rojo-negro | #0A0A0A · #FF3B30 · #FFFFFF | Archivo Black / Archivo | seco | bold | whip |
| menta-suiza | #F2F5F3 · #00B386 · #111111 | Inter Tight / Inter | seco | caja | whip |
| terracota | #2A1D17 · #E07A5F · #81B29A | Fraunces / Manrope | cinematico | karaoke | iris |
| cobalto-pop | #FFFFFF · #2D5BFF · #FF5CA8 | Space Grotesk / Plus Jakarta Sans | energico | caja | zoom |
| noche-cine | #05070A · #D4A5FF · #3A3F58 | Playfair Display / Inter | cinematico | minimal | zoom |

Son puntos de partida, no estilos de ningún creador. Cámbiales lo que quiera.

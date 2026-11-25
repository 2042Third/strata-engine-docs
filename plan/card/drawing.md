# Card: drawings

Figures of kind `diagram`: `src/assets/figures/<part>/<chapter>/<figure>.svg`. With `common.md`. Tool:
`node scripts/drawings.mjs` (`npm run drawings --`).

## Themes

- The site inlines the SVG at the column's width (768 px); `data-theme` switches the custom properties it reads.
- Color only through the classes of the style block `start` writes (`--sl-color-*`). No plate: the page is the ground.

## Roles

Class `x` fills, `line-x` strokes.

| Class | Light | Dark | Use |
| --- | --- | --- | --- |
| `ink` | #17181c | #ffffff | text, main lines, arrow heads |
| `muted` | #555962 | #888c96 | secondary lines; text on the ground only |
| `faint` | #c1c3c8 | #353841 | grids, guides; never text |
| `ground` | #ffffff | #17181c | label grounds |
| `plate` | #edeef3 | #23262f | neutral boxes |
| `blue`, `green`, `purple` | #0f1c8a, #28650b, #660891 | #bdc3ff, #bdf6a2, #ebccfa | accents: text, lines |
| `orange` | #73520d | #f9e8c3 | highlight: what to notice |
| `red` | #8a0f3a | #f9c3d6 | error, warning |
| `<hue>-area` | pale | deep | fills under text |

- Text on an `-area` is `ink` or its hue. A group's fill class colors its texts: class each label.
- A shape without a class fills `ink`: give it a role or `fill="none"`.
- Colors that are data (a ramp, a color space): `class="swatch"` with a literal fill or a gradient in `<defs>`, framed
  with `line-ink`.
- Never meaning by color alone.

## Canvas

- `viewBox="0 0 768 H"`, H at most 640; no `width` or `height`. A unit is a pixel on a wide screen.
- Half-column: still 768 wide, content within x 192 to 576 (a narrower viewBox enlarges everything).
- 16 units clear at every edge, a text's descent included.
- Text 16; `small` 14, the least; `large` 20 for a key label; `bold`; `mono` for code names.
- Lines 1.5; the subject 2 to 2.5; grids 1. Dashes `stroke-dasharray="4 3"`.
- Arrows: a line and a polygon head in its hue, 10 long, 7 wide (12 by 9 on 2.5 lines). The line stops at the head's
  base; the tip touches the target point or a dot's edge, or stops 2 short of a box. No markers. A curve ends at the
  base, its head along the end's tangent (quadratic: end − control).
- Labels sit 6 to 10 units beside what they name, never on a line; one that must cross a line gets `halo` or a rect
  of the fill below it.

## Words

- Sentence case; the page's terms; numbers as the page writes them (5,728, 0.167, 16 ms).
- Mathematics as plain text: real minus (−), ×, subscripts as `<tspan class="small" dy="5">0</tspan>` then
  `dy="-5"`. No TeX.
- The lint reads the manifest's caption and alt, never the drawing: apply `common.md` by hand (no contractions,
  abbreviations, banned words; only acronyms the page expanded).
- No title (the caption says it), no legend: label parts directly.

## Never

Script, event attributes, `foreignObject`, raster images, links, references outside the file, `data:` URLs, fonts,
text as paths, `title`, `desc`, `filter`, `marker`, opacity, `style` attributes, literal colors outside swatches, ids
not starting `<figure>-`, a second or edited style block.

## Accessibility

The plugin names the figure from `alt` (`role="img"`): no title or ARIA; draw what the alt says.

## Stand-ins

A drawing may stand in for a figure that waits for an engine addition or is blocked at the pin: the waiting entry's
`standIn` names the drawing's id, and the page places `::figure{id=<drawing>}` where the picture would stand. Draw what
the waiting figure's `shows` says, within what the pin does; its caption says what the drawing shows, not the picture.

## Method

1. Read the manifest entry (`shows`, `numbers`, `caption`, `alt`) and the page around its `::figure`.
2. Plan in numbers: a grid (unit, origin, ranges, edges) and H, the lowest box plus 16.
3. `start <part>/<chapter>/<figure> --height H`; the plan goes in a comment. The page clips at the viewBox: replanning
   changes H.
4. Draw.
5. `render <part>/<chapter>/<figure>`; Read both PNGs (the dashed frame is the viewBox). Look for overlaps, clipping,
   arrow ends, crowding, empty bands, a weak theme.
6. Fix and render again: at most three rounds.
7. `check <part>/<chapter>/<figure>` passes (Never, canvas, classes, text size, what the viewBox cuts, contrast 4.5:1
   in both themes). Commit the SVG.

## Usual faults

| Fault | Cure |
| --- | --- |
| Text over a line | Move it; else `halo` or a ground rect. |
| Empty band at an edge | Lower H; shift with `<g transform="translate(0 -n)">`. |
| Color gone in one theme | `faint` or an `-area` on text or a line: use the strong role. |
| Legend over data | Label curves at their ends. |

# Notes: light/sun-shadows-1

## New terms

None proposed. The page defines the twelve glossary terms of its brief: cascaded shadow maps, cascade, slice, split, texel density, stable cascades, texel snapping, containment, cascade blend band, shadow caster, sub-texel caster, shadow cascade cache.

## Since

0.3.0: the cascade map (inventory render-direct, "Cascade map", 0.3.0); the stable layout is 0.8.0 and is described as the page's state.

## Requests

- Names for tools/data/names.txt: Valient, Lauritzen (word-list findings left on purpose; they name the sources of the alternatives table).
- Figures: `stable-cascades` and `containment` are drawn as SVG (src/assets/figures/light/sun-shadows-1/). Editor pictures `shadows-view-medium-high` (variants medium and high) and `cascade-distribution-sweep` wait for tier 2 editor screenshots (layout `layouts/scene-view.ini`). Not drawn or requested: cascade blend 0 against 0.1 across a split, four against five cascades (Showcase shot 5), and the cache in numbers on a GPU-driven frame (`renderStats.cachedCascades`); no recipe was verified for them.
- Hosts for Further reading: none linked; the entries cite sources without a link.

## Not verified

- The statements about other engines and papers (parallel-split maps since about 2006, sample-distribution shadow maps 2011, Unreal Engine 5 virtual shadow maps) rest on the cited talks and were not checked.
- The effect of the sweeps and of `ShadowDistance` on the medians (Reading the result) is derived from the layout rules, not measured.
- That the shadows debug view is chosen in the editor by the value `shadows` of `debugView` through `viewport.setSettings`: taken from the command's enum and an existing recipe; no menu label was checked.
- The Third-Person sample's own settings (shadow distance, quality) were not read.

## Findings not applied

The brief lists no open findings. Items of the brief not carried: a Third-Person acne and bias exercise (render-direct:642, `light/shadow-basics` owns biases); selection by depth alone shown failing on a branch (render-direct:659-660), covered by a Check-yourself question instead; the blend 0 against 0.1 and four against five cascade figures (no recipe).

## Clerk

- Admitted to names.txt: Valient, Lauritzen.

## Figures

Taken at the pin v0.8.0 (319075e3) on 2026-11-24 and published; `waitsFor` removed from both (the pin has
`editor.screenshot`). No earlier file was published, so nothing was compared.

- `shadows-view-medium-high`: one round, recipe unchanged. The picture and the legends match the caption and alts:
  Medium C0 to C3, medians 0.62, 0.81, 0.68, 0.57; High C0 0.1 to 1.5 m with no receivers, then 0.31, 0.40, 0.34,
  0.28 at half the texel sizes (5.6 mm against 2.7 mm, 1.3 cm against 6.6 mm).
- `cascade-distribution-sweep`: two rounds. The page now asks for one view at the sun's distribution of 0.9, so the
  recipe got the Course scene, Medium quality, the sign hidden, grid and gizmos off and the `Scene` panel. Round 1
  (camera 3, 5.5, 9 toward 0, 0, -14) showed a rock across the right third and the edges only on far objects. Round 2
  (camera 0, 8, 11 toward 0, 0, -10, fov 55) shows the start platform from above with the 13.9 m edge and its hatched
  band across it and the 32.7 m edge on the block beyond; published. Shows and alt rewritten to it. The picture shows
  the edges at 0.9 only; the caption's claim about a higher distribution rests on the words, as the page says
  (a `::compare` at 0 and 1, described below, would show it).

Taken 2026-11-18 with the provisional build (engine 5b975ad2), `--provisional`; nothing published. Both keep `waitsFor`.

- `shadows-view-medium-high`, two rounds. Round 1: the recipe's steps set only the debug view in both variants; it now
  opens `Scenes/Course.stscene`, sets the editor camera down the course (`camera.set`, position 1.5, 2.2, 7, target
  0, 0, -14, fov 50), the shadows view with grid and gizmos off (round 2: they crossed the picture), the quality by
  `project.setSettings` of `Renderer.Quality` (`Preset` Medium or High), and pictures the `Scene` panel (797 x 499).
  What it shows: every surface is green at both qualities (the legend reads 100 % at 1 px per texel or finer), so the
  old caption ("the nearest meters turn greener") was false. The change is in the legend: Medium lists C0 to C3
  (medians 0.62, 0.88, 0.68, 0.57), High C0 to C4, its C0 (0.1 to 1.5 m) with no receivers, and the slices from 5 m on
  keep their ranges with half the texel size (1.3 cm against 6.6 mm for 5 to 14 m) and about half the median. Caption,
  alt and shows now say this. High's medians vary by a few hundredths between takes (live statistics); the alt gives
  ranges. The page's paragraph ("A change shows in the statistics before it shows to the eye") stays true.
  Rounds 3 and 4 (a viewer's faults): the near `Sign` (ID B28DE10A8651603E, under `Decoration`) showed its board at
  Medium, pale and blended over the ground's shadow, and not at High, where only the board's shadow stayed. A wait of
  600 frames more (`editorWindow.steps`, kept) changed nothing at High, so it is no loading; the recipe now deactivates
  that sign (`entity.setActive` in the shared setup), and both variants match outside the legend. The legend is now
  also a crop `legend` (x 0.5 to 36 %, y 64 to 99 %, scale 2, taken for both variants): the page shows it only with
  `::figure{id=shadows-view-medium-high variant=medium crop=legend}` and `variant=high crop=legend` lines, the
  writer's change to make. Medians of round 4: Medium 0.62, 0.81, 0.68, 0.57; High C1 to C4 0.31, 0.40, 0.34, 0.28; the
  alts give these ranges. They move by a few hundredths between takes: read them again when the pin's take is published.
- `cascade-distribution-sweep`: cannot, recipe left as written. The page shows it with one `::figure` and no variant,
  and its caption and alt describe four captures (0, 0.5, 0.9, 1) in one picture: one `editor.screenshot` is one
  window, and no command joins pictures. Tried (then removed from the manifest) as two variants of the recipe above
  with `component.set` of the `Sun`'s `DirectionalLight` `CascadeDistribution` (0 and 1): both work, the white edges
  and hatched bands move toward the camera at 1, and the legend's ranges read C1 1.4-7.5 m, C2 6.9-40.8 m at 0 against
  C1 1.4-4.1 m, C2 3.8-11.0 m at 1; all green again, medians below 1. Nearest honest figure: a `::compare` of those
  two variants (`variant=` lines on the page), caption "At 1 the edges lie nearer the camera, and the legend's ranges
  shrink near it", the writer's change to make.

Mended 2026-11-24 after a viewer's faults (words only, no retake; the published pictures are the pin's take):

- `shadows-view-medium-high`: the legends show the far ends kept (5.8, 13.9, 32.7, 80 m), not the ranges: Medium C0
  reads 0.1-5.8 m, High's C1 1.4-5.8 m. The caption now says "keep their far ends (5.8, 13.9, 32.7 and 80 m)", with
  `numbers` giving the legends' rows. The page's paragraph (before the figure) still says "keep their ranges": the
  writer's change to make, to the same words.
- `cascade-distribution-sweep`: the caption now names the line with the hatched band across the near platform as the
  13.9 m edge (cascade 1 to 2) and the line on the far block's top as the 32.7 m edge (2 to 3), with `numbers`.

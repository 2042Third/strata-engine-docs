# Notes: image/tutorial-post-effect

## New terms

None proposed.

## Since

0.7.0: the post source with the depth of field's and the motion blur's outputs (`Docs/Releases/0.7.0.md` lists motion blur and `GPU.DepthOfField`). The tutorial's patch is written against the pin.

## Requests

- Extra words: "letterbox" and "letterboxes" (the page's subject; `word-list` fails on both and is left).
- Editor figure `editor-letterbox`: layout `layouts/inspector-post-process.ini` (Inspector showing the Post Process group Lens, Scene view visible); `waitsFor: tier 2: editor screenshot`, because the project must have the patch's property.
- Figure `result` is an SVG drawing at `src/assets/figures/image/tutorial-post-effect/result.svg` (a schematic of the 1920 by 1080 example, not a render); a render off and on needs the patched build.
- The tutorial file has no stages and no commands: the tutorial changes the engine (`startsFrom` the pin), as `core/first-change` does. Its `tests` list names `GPU.SceneRenderer.Letterbox`, a suite that exists only after the patch.
- Link targets that may not exist yet: `../engineering/test-kinds.md`.
- Page uses no checkpoints (engine-changing tutorial, card). Exercise 2's worked solution is `tutorials/image/tutorial-post-effect/exercise-1.patch`, a patch against the tutorial's end state (the file's number counts patches, not exercises).
- Sources of the patch were generated with git in a scratch copy of the pin's files and checked with `git apply --check` against the pin.

## Not verified

- The patch was never compiled or run: no build exists at the pin here. Names used from the code (`m_HistoryTextures`, `m_PreExposure`, `DispatchGroups`, `m_Errors.Report`) were read in the pin; the Slang file's syntax (`any(globalID.xy >= size)`, `Load(int3(...))`, the ternary on vectors) was not compiled.
- That `Editor.Commands` fails at the three inactive-property checks before the repair (derived from the equality of the JSON lists), and that the other suites named pass after it.
- That the Scene view applies the Post Process's letterbox in the editor, and the labels of the inspector (`Letterbox`, `Letterbox Aspect`, the group `Lens`).
- The exposure's metering of the bars: the page says only that the exposure reads the new source, so the bars are among its pixels.
- That `ctest --preset <preset>-debug -j 8` runs the feature test and the new GPU suite (the GPU suites' ctest names were not read).
- The unit `new:28`'s claim that `viewport.capture` reports `gpuMs` per stage is from `EditorViewportCommands.cpp:1244`; no stage of its own was built.

## Findings not applied

The brief lists no open findings. Left out by the card: a stage of its own is only an exercise (answer in words, no patch); the second checkpoint-style pictures are not made because an engine-changing tutorial has no checkpoints.

## Figures

- `editor-letterbox` (photographer, 2026-11-23, pin v0.8.0 319075e3, two rounds, nothing published): blocked, it waits
  for a command that scrolls the Inspector. The recipe now pictures the Inspector after selecting the basic3d scene's
  `Post Process` (`entity.find`, `selection.set`), as the caption "before your change" asks: no patched build is needed.
  - Round 1, window 1280 × 1360 (the tallest any figure uses), Inspector 380 px wide: the panel shows the Transform
    and the Post Process groups Tone and color, Exposure, Bloom and the start of Ambient occlusion, then ends. Rows
    are 30 px apart and a group heading adds about 40 px; the panel's scroll bar shows about half the content.
  - Round 2, window 1280 × 2400: the editor refused to start ("the display cannot hold a window of 1280 x 2400
    pixels, the system made it 1280 x 2130"). At 1280 × 2130 the panel is about 2050 px tall, and counted from round 1
    the group Lens (Vignette, Film Grain, Chromatic Aberration, Lens Flare, after Global illumination, Anti-aliasing's
    13 rows and Reflections) ends at about 2140 px: the Lens Flare row would be cut, and a picture 2000 px tall would
    not read in the column anyway. `editor.screenshot` and `editor.showPanel` take no scroll or filter.
  - The recipe keeps a small window (960 × 440, `layouts/make-scenes-entities-short.ini`, Inspector 380 px) for the
    day a command scrolls the Inspector to the group Lens; its `waitsFor` says so. The alt now describes that panel
    picture instead of the whole window.
- What would show the figure as captioned: a command that scrolls the Inspector to a section or property (the same
  wait as `make/look`'s `motion-blur`), then one take of this recipe with a scroll step after `selection.set`.
- The nearest honest picture at the pin: none that keeps the page's sentence "The picture shows the Lens group": the
  top of the Post Process in the Inspector (round 1) shows the component but not the group. Until the command exists,
  the page's words before the figure carry the point alone.
- Finishing pass (2026-11-24, pin v0.8.0 319075e3, final): the pin still has no command that scrolls the Inspector
  (`editor.showPanel` takes `search` for the Hierarchy only; `editor.screenshot` takes no scroll), and the inspector's
  groups are plain headings (`UI::PropertyGroupHeading`), not headers that fold, so no take can reach the group Lens.
  `editor-letterbox` keeps its `waitsFor` as the request for a later edition and names the stand-in `lens-group`: a
  drawing of the group's rows in the pin's order (sections in order of first registration, so Lens comes after
  Reflections and before Motion; rows Vignette, Film Grain, Chromatic Aberration, Lens Flare), then the patch's
  `Letterbox` (a check box, off) and `Letterbox Aspect` (2.39, its label dimmed by the inactive reason, which the
  label's tooltip gives: `UI::PropertyLabel`). No values are drawn for the pin's rows: the basic3d scene's own values
  were not read. The page places `lens-group`; its lead-in now introduces a drawing, and step 3's "open its group
  `Lens`" became "scroll the inspector down to its group `Lens`", since a group does not open.

## Clerk

- Admitted to extra-words.txt: letterbox, letterboxes.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run

- 2026-11-24, pin v0.8.0 319075e3, `tutorials.py patch` (round 1): the tutorial's patch and exercise 1's patch apply
  as written (offsets only), build, and pass Architecture.Layering, the five suites the file names
  (GPU.SceneRenderer.Letterbox: 2 test cases, 3 with the exercise) and the feature test; stamps written. This settles
  the first two items of `## Not verified` (the patch compiles; the suites pass after it).

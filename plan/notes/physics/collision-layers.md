# Notes: physics/collision-layers

## New terms

None proposed. The page defines the three homed terms in bold: category bits (alias mask bits), collision layer, query category.

## Since

`since: 0.5.0`: 0.5.0 scenes stored the layers (the engine's migration code names it); the first tag that held collision layers was not checked.

## Requests

- Engine, for a later edition: a command that opens the Project Settings panel at a page (figure `settings-page`, whose `waitsFor` keeps the request; see `## Figures`). Until then the page places its stand-in, the drawing `settings-page-drawing`. The layout `layouts/collision-layers-page.ini` is no longer asked for: the recipe uses `layouts/first-game.ini`.
- Figure not drawn: the frames of ghosts sinking through balls (item physics:377); no recipe was invented.
- Links to pages that may not exist yet: `physics/queries`, `make/physics`, `editor-ui/settings-windows`, `physics/scale-streaming`, `physics/building-bodies`.

## Not verified

- Statements about other engines are limited to the Further reading entries and the alternatives table (Box2D, box3d groups); not read against sources.
- `physics/tuning` is named in a rule box without a link.
- The first tag that shipped collision layers.

## Findings not applied

- The Playground README (`Samples/PhysicsPlayground/README.md:16`, `:52`) is an engine document: the page states the project-level rule at the pin and notes the README's older wording; the README itself is not changed here.

## Figures

Editor figure `settings-page`, taken once with the provisional build (engine 5b975ad2831e, 2026-11-18, `--provisional`);
nothing published, `waitsFor: tier 2: editor screenshot` kept.

- The writer's layout `layouts/collision-layers-page.ini` did not exist and the steps were empty. The recipe now uses
  `layouts/first-game.ini` with `panel: ProjectSettings` and an `editor.showPanel` step, the form the other Project
  Settings recipes use (`editor-ui/settings-windows`); the Playground sample supplies the Ball and Ghost layers.
- Round 1: cannot. The panel is readable at its own pixels (about 800 x 500) but shows the Game page (Start Scene Main,
  Title Physics Playground, the icon); Collision Layers is only an entry of the list on the left. The panel opens on
  its first page, the selected page is not kept in the layout, and no command selects another: `editor.showPanel`
  takes `scripts` (ContentBrowser) and `search` (Hierarchy) only, in the pin and in the provisional build; the
  editor's own `ShowProjectSettings(page)` runs only from clicks (the Inspector's and Export dialog's links).
- What the page needs: a `page` parameter of `editor.showPanel` for ProjectSettings (`Scene.CollisionLayers`); with it,
  add `"page": "Scene.CollisionLayers"` to the recipe's step, retake, and check that the caption's claims (names Ball
  and Ghost, the cleared box where they meet) are in the picture. Until then the page gets no picture; the nearest
  honest one is a diagram of the matrix's triangle with the Ball and Ghost cell cleared.
- Pin v0.8.0 (319075e3, 2026-11-24): not taken again. `check` asked to drop `tier 2: editor screenshot` (the pin has
  `editor.screenshot`), but the release's `editor.showPanel` still takes only `panel`, `scripts` and `search`, and
  `EditorLayer::ShowProjectSettings(page)` is still called only from the Inspector's and Export dialog's links. A take
  would again show the Game page. `waitsFor` now reads tier 3 with that reason, as the sibling recipes
  (`editor-ui/settings-windows`, `physics/tuning`, `make/input`) do.
- Finished 2026-11-24 at the final pin v0.8.0 (319075e3): the pin still has no command that selects a Project Settings
  page, so the picture cannot be taken. In its place the page shows the drawing `settings-page-drawing`, named as the
  waiting entry's `standIn`: the Project Settings window on **Collision Layers** with the Playground's table, drawn from
  `StrataEditor/src/UI/CollisionLayersPage.cpp`, `SettingsPages.cpp` and `ProjectCollisionLayers.cpp` (page list,
  heading, both descriptions cut, the summary "2 named · 1 pair passes through", name fields Ball and Ghost with their
  remove buttons, Name a Layer, the matrix "Which layers collide" for the shown layers 0, 1 and 2 with the box of Ball
  and Ghost cleared). The lead-in gained a sentence that introduces the drawing.
- The page's words followed the pin: the paragraph said the page has a table of 32 name fields and implied a full
  matrix. At the pin `DrawNames` shows a field only for each named layer (`CollisionLayersPage.cpp:139-142`), and the
  matrix shows layer 0, the named layers and the layers that do not collide with all (`Describe`, 74-75), one box per
  pair (256). The paragraph now says so; the summary line is left to the drawing.
- Size: the new caption, alt and words took the page over size M (4,130 prose words). Cut to 3,996 by shortening both
  alts and the new caption, merging the two paragraphs after `SetLayerCollisionMasks`' callouts (they repeated the
  callouts) and trimming three sentences; no fact was removed.

## Clerk

- Nothing asked.

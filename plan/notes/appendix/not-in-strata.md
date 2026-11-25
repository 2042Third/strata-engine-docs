# Notes: appendix/not-in-strata

## New terms

- lightmap: a texture that stores the indirect light of a static scene, computed once before the game runs (home: this page; the lint names this page as home).

## Requests

- Word: decal (one-line definition: a texture projected onto the surfaces inside a box).
- Host: none needed (docs.godotengine.org, docs.unity3d.com, gameprogrammingpatterns.com, gafferongames.com are on the list).

## Not verified

- That Unreal Engine loads plugins at start, Wwise and FMOD as sound libraries, Unity packages and Godot's particle nodes: general knowledge, cited in Further reading without a link check.
- The technique paragraphs (general engine practice) are not Strata facts; sources are books in Further reading.
- Rows of the brief not on the page (about 70, mostly area rows such as light cookies, post volumes, audio attenuation, UI scroll limits) were not re-run at the pin.

## Findings not applied

- Size: the brief's 116 rows and 17 technique groups need XL; the task fixed L, so the page carries about 55 rows and one technique block per area.
- critic-appendix-2 (six extra rows) and critic-appendix-5 (sixth rendering group: fog, material models, text shaping, skinning): not applied for size.
- critic-appendix-4 (Assumes rows must): not applied; the front matter keeps the brief's `needs: []`. Planner decides.
- critic-appendix-1, 6, 12: applied (exercise 2 reads results without an absence assertion; watchdog reason; showcase and previews lines).
- critic-appendix-3: applied as the particles example and a diagram.
- critic-appendix-13: applied; networking and game AI get one sentence and no links (those pages do not exist yet).
- W8 rows (area lights, GI limits) omitted: their pages do not exist yet.

## Clerk

- Admitted: decal (home this page, the request's definition). lightmap was admitted earlier.

## Tutorial run

- 2026-11-18: exercise-2 run at the pin's Release build: passes as written (round 1); stamped.
- 2026-11-23: re-run at the v0.8.0 pin (319075e3): exercise-2 passes as written (round 1); stamped. The page's answer to exercise 2 had its second paragraph unindented, which ended the list item and the answer box early: indented. The three searches still find no particle, navigation-mesh or game-network feature (the "navigation" matches are the game UI's selection navigation).
- 2026-11-24: final run (process step 15): the pin-build run of exercise-2 was still current; exercise-2 run with the official v0.8.0 package (Strata-0.8.0-windows-x64.zip): passes as written (round 1); stamped.

## Pin move to v0.8.0

- Plans and known issues now read from `Docs/Releases/0.8.0.md`; rows added for disk lights, blended material layers and the mesh ghost of drops; supersampled stills joined the MSAA row. The "previews" care line became the drop ghost (0.8.0 no longer lists previews).
- The exit-code and GCC/Clang debug-information rows of the brief were never on the page: nothing to remove.

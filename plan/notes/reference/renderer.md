# Notes: reference/renderer

## New terms

None. The page defines in bold GPU stage, scene binding layout, switch, statistic, debug view, quality row, players' row and device requirement as plain section terms; propose them if the clerk wants them admitted.

## Requests

- Words: none outstanding (preset names and enum choices stand as code).
- Generator routes (planner): no routes exist for the slot ledger, the fallback textures and samplers, the device requirements or the rules; those tables are by hand (below).
- Generator finding: the intro of `src/generated/reference/render-stats.md` says `viewport.capture` and `editor.status` report `renderStats`; at the pin the object is built in `editor.perf` (`EditorStateCommands.cpp:968`) and `viewport.capture`. The page says `editor.perf`.

## Hand-written tables

- Stage notes (stage, pass, quality rows, page): `Strata/src/Strata/Renderer/GPUProfiler.cpp`, `RendererQuality.cpp` (`c_RowTraits`), `StrataEditor/src/Editor/EditorStateCommands.cpp` (perf description).
- Scene bindings: `Strata/src/Strata/Renderer/SceneRenderer.cpp` (`CreateResources`, binding set at the `Sampler(8..10)` lines), `Strata/shaders/Include/Scene.slang` and the included `.slang` files.
- Statistics families: field names of `SceneRenderer.h`.
- Debug view meanings: `viewport.capture` text, `Scene.slang` lighting view constants.
- Quality row traits and Custom ranges: `RendererQuality.cpp` (`c_RowTraits`, `MakeSection`, option arrays).
- Fallback textures and samplers: `Renderer.cpp`, `Renderer.h`.
- Device requirements and `GraphicsDeviceInfo`: `VulkanGraphicsDevice.cpp`, `GraphicsDevice.h`.
- Rules (about 70 rows): pin's `AGENTS.md` rendering rules and the five renderer inventories (render-core 549-618, render-scene 461-513, render-direct 571-627, render-image 525-579, render-indirect 467-520).

## Not verified

- Page links to `gpu`, `draw`, `light`, `image`, `indirect` pages assume the sidebar's ids exist.
- The use of each fallback texture beyond the call sites found (white: bindless reserved slot; black: atmosphere, glass, reflections; black cube: environment and irradiance).
- Whether each `GraphicsDeviceInfo` flag changes a path beyond the header's comments.
- The rules table is a selection (about 70 of the roughly 290 inventory rules); rules of local lights and GI to be rechecked in phase B.
- Units of stats other than the `Ms` and `Bytes` suffix conventions.

## Findings not applied

- critic-reference-8 (limits table for 16,384-texel textures, 4,096 joints, 32,768 bindless textures, 256 timestamps and others): not applied; no generator route or `tools/reference-limits.json` entry exists, and the unlisted limits were not all verified at the pin. Only `MaxBindlessTextures` (32,768) and the 16-sample anisotropy are on the page.
- critic-reference-2 (introductions name the teaching page): applied to bindings, switches, fallbacks and device tables.
- Brief items asking the rules table to carry every inventory rule (about 100 rows): carried as about 70 rows grouped by topic.
- Statistics table with a unit column per key: units given by name suffix and family table, not per key.

## Clerk

- Refused: the bold words the page defines locally (GPU stage and debug view are homed in gpu; scene binding layout, switch, statistic, quality row, players' row, device requirement) are not admitted: a reference page restates terms whose homes are their chapters, and the page proposed none. Left for the planner: the generator routes and the render-stats intro finding.

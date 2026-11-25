# Brief: `reference/ui`

| Field | Value |
| --- | --- |
| Title | Game UI reference |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `ui/layout` |
| From | gameui ch. 10 |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/ui` — Game UI reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
the eleven UI components (and `Text`), of the `ui.*` commands and of the SDK's `UIElement`, `UI` and `UIAction` stand
in `reference/components`, `reference/commands` and `reference/script-api`, linked by name. What only this page holds:
(1) the conventions every UI property follows (canvas units, the y axis, anchors and pivots in 0 to 1, colors in display
values), from the comment of `GameUIComponents.h`, as a short hand-checked table; (2) every enum of
`GameUIComponents.h` (`UICanvasScaleMode`, `UICanvasRenderMode`, `UIFitContent`, `UIImageType`, `UIFillDirection`,
`UITextVerticalAlignment`, `UITextOverflow`, `UISelectableTransition`, `UINavigation`, `UILayoutType` and
`UIChildAlignment`), each value with its comment, parsed; (3) the four UI callbacks of `StrataScriptClassDesc` and the
event types of `IUIEvents`, with when each fires; (4) the reserved `UI` action map, linked to `reference/audio-input`'s
table; (5) the limits, parsed: `c_MaxLayoutsPerCanvas`, `c_MaxQuadChanges`, `c_MaxBoundAtlases`, `c_MaxUIFonts`; (6)
`GameUISceneStats` and the stages `GPU.UI` and `Render.UI`. Hand-written: one introduction per table, one line naming
the absent widgets with a link to `ui/what-game-ui-does`, and `## Where it lives in Strata`
(`Strata/src/Strata/GameUI/`, `EditorUICommands.cpp`). The tools are `tools/reference.py parse` and the catalogue dumps.

**Leaves out.**

- What a game UI must do, and the widgets Strata lacks → `ui/what-game-ui-does`
- Rects, anchors and layout → `ui/layout`
- The UI contract → `ui/contract`
- Text and text fields → `ui/text`
- Drawing and input → `ui/drawing`, `ui/input`
- Menus and HUDs for game makers → `make/menus`, `make/hud`

**Fit.** `fits`: about 1,300 words against M (3,000). The generated tables give the page its size: the eleven enums with
their values, the four callbacks and the event types, four limits, `GameUISceneStats` and two stages, about 1,000 words.
The prose is the paragraph on top, six introductions, the conventions table (about 8 rows), one line and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:52` | feature | link | The coordinate and color conventions |
| `gameui:53-65` | feature | link | The components and their enums, as names linking `reference/components` |
| `gameui:79` | feature | link | `c_MaxLayoutsPerCanvas` |
| `gameui:92` | feature | link | `GameUISceneStats` |
| `gameui:128` | feature | link | `c_MaxBoundAtlases` |
| `gameui:130` | feature | link | `c_MaxQuadChanges` |
| `gameui:155` | feature | link | The stages `GPU.UI` and `Render.UI` |
| `gameui:185` | feature | link | The UI action map |
| `gameui:201` | feature | link | `UIEventType` and `IUIEvents` |
| `gameui:203-204` | feature | link | The UI host functions and the four callbacks |
| `gameui:206` | feature | link | `UIElement`, `UI` and `UIAction`, as names linking `reference/script-api` |
| `gameui:214` | feature | link | The `ui.*` commands, as names linking `reference/commands` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rects, anchors and layout | `ui/layout` | must |
| The UI contract | `ui/contract` | helps |
| UI input and events | `ui/input` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-8 | should | missing-item | new items on `reference/assets`, `reference/renderer`, `reference/script-api` | The other area pages have a parsed table of limits, and `appendix/not-in-strata` sends "caps and limits of the features Strata has" to `reference/renderer`, but these three pages have none. Unlisted at the pin: a texture's longest side of 16,384 texels and 2^28 decoded pixels, a glTF scale of at most 10,000, 8 levels of detail, a hierarchy depth of 1,024 and a 64 MiB document, 4,096 joints per mesh, built-in handles 1 to 255; 32,768 bindless textures, 256 GPU timestamps a frame, a 2 GiB geometry pool, the draw key's submesh and LOD bits, 8,192-texel cascades, the font limits; save file names of 64 characters and files of 64 MiB, 65,536 script classes, 4,096 fields a class, names of 1,024 bytes and strings of 256 MiB. | Each of the three pages adds a parsed limits table through `tools/reference-limits.json`, as `reference/physics` and `reference/ui` have, with one introduction that names the teaching page. About 40 words each. | `allocation/reference.md:385-406`, `:460-485`, `:5-28`; `allocation/appendix.md:48`; `Strata/src/Strata/Asset/TextureImporter.h:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:24`; `Strata/src/Strata/Asset/GltfImporter.cpp:68-74`; `Strata/src/Strata/Asset/GltfImporter.h:54`; `Strata/src/Strata/Renderer/Mesh.h:46`; `Strata/src/Strata/Asset/Asset.h:36`; `Strata/src/Strata/Renderer/GraphicsDevice.h:135`; `Strata/src/Strata/Renderer/GPUProfiler.h:95`; `Strata/src/Strata/Renderer/GeometryPool.h:87`; `Strata/src/Strata/Renderer/SceneDrawKey.h:28-29`; `Strata/src/Strata/Renderer/RendererQuality.h:191`; `Strata/src/Strata/Renderer/FontValidation.h:47-58`; `Strata/src/Strata/Core/SaveFiles.h:23-24`; `Strata/src/Strata/Scripting/ScriptModule.cpp:55-57`, `:957`, `:1046`; `Strata/src/Strata/Scripting/ScriptValue.h:17` |
| critic-reference-12 | should | missing-item | `reference/audio-input`, `reference/ui`, `reference/worlds-runtime` | `reference/physics` and `reference/animation` list their scene services with each function's comment; the other area pages do not. So `IAudioPlayback` and `IAudioOutput`, `IUIControl` (beside the event types of `IUIEvents`), `IWorldStreaming` (a link row with no table) and the engine services `IGameWindow`, `IGameSaves` and `IGameGraphics` are on no reference page, though engine code reaches those modules only through them. | Each of the three pages adds the parsed table of its services, as `reference/physics` (4) does (about 30 words each); `reference/worlds-runtime` also takes the three engine services of `EngineServices.h`, which the runtime and the editor provide, with an introduction that names `scripting/host-api` and `worlds/runtime`. | `allocation/reference.md:564-566`, `:627-628`, `:679-691`, `:736-746`, `:788-801`, `:829`; `Strata/src/Strata/Scene/SceneServices.h:242`, `:485`, `:538`, `:552`, `:584`; `Strata/src/Strata/Core/EngineServices.h:103`, `:125`, `:152` |

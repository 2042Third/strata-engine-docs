# Brief: `ui/contract`

| Field | Value |
| --- | --- |
| Title | The UI contract |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `ui/layout` |
| From | gameui ch. 5 (signals, dirty marks, re-layout roots, the hierarchy and activity journals, the layout cache, validation, the tests that pin it) |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `ui/contract` — The UI contract

**Covers.** The job: keep the layouts, shaped texts, quads, clip rects and hit grids of `GameUIScene` true to the
scene while doing work only for what changed. The problem section is one paragraph: a retained UI must learn what
changed, and the scene's transform contract (`world/scene-graph`) already has the same shape. The map is the dirty
propagation: a signal, a mark on the element, the walk up to the re-layout root, the subtree laid out again, the boxes
compared, the quads marked, a range in the journal. The contract comes before the code, each rule with its reason:
every direct write to a UI component is signaled (`MarkModified`, `registry.patch`), and the writers that already
signal are named (`ComponentAccess`, the script API, the UI system), with `SetText`'s skip of a text that did not
change; values written right after `AddComponent` need none (the scene's rule, in one sentence with a link to
`world/scene-graph`); hierarchy changes go through `Scene`. A toy of about 40 lines caches a computed value behind a
dirty flag and shows how an unsignaled write goes stale.

The real code, on the Third-Person menu's Play label: the signals `GameUIScene` connects in its constructor, one set
per component, and how a change costs by its kind (`OnLayoutChanged` marks layout and quads, `OnVisualChanged` quads
only, `OnTextChanged` a reshape and a layout only when the rect fits its text); the hierarchy, activity and asset
content journals, activity read from the scene's transform change log, and what the UI does when a journal no longer
reaches back; `UpdateLayout`, which walks each mark up to the highest ancestor whose rect depends on its children,
drops nested roots and marks only the boxes that moved; why moving plain entities costs no canvas; `EnsureLayout`, with
up to four layouts per canvas keyed by the size in units, so a window resized at the same aspect lays out nothing; and
`Validate`, the full recomputation that Debug builds compare after every `EnsureLayout`, whose message names the entity
written without a signal. The tests pin it: an idle frame lays out, shapes and builds nothing, a label's text costs one
shaping, and an unsignaled write fails validation; the perf budgets of 10,000 elements and the idle frame show the
cost. The page ends with the alternatives (re-layout every frame, immediate mode, polling versions), changing it safely
(a new UI component connects its signals and states what each costs) and two exercises: trace a frame through the work
counters, and break the contract on purpose. At the end the reader can predict which counters a given change moves, and
explain why an unsignaled write is stale in Release and an assert in Debug.

**Leaves out.**

- The transform contract, which this contract mirrors → `world/scene-graph`
- The quads' journal and the partial uploads it drives → `ui/drawing`
- Hit grids rebuilt from hit stamps → `ui/input`
- Perf budgets, the reference machine and the rule that budgets only go down → `engineering/perf-lab`
- Edits from the editor, which signal through commands and undo → `editor/undo`

**Fit.** `over`: about 4,800 words against M (3,000). Six excerpts (the signals, the change handlers, `UpdateLayout`,
`EnsureLayout`, `Validate`, the tests) with two concepts, four rules, the writers that already signal and the internals
sections pass M's top of 4,000; by S2 the page takes L, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:315` | concept | home | A retained UI needs change tracking: observers, dirty marks per element and per layout, the re-layout root, journals; the mistake of writing `UIRect.Size` without `MarkModified` |
| `gameui:323` | concept | home | Layouts cached per screen size in units, four kept, the least recently used replaced; the mistake of thinking every resize costs a layout |
| `gameui:79-84` | feature | home | The layout cache; lazy layout and draw order by sort order; change tracking through signals, hierarchy moves, activity and asset content; activity read from the scene's world-transform change log and filtered by the element index, so every moving body costs the UI one lookup; when the hierarchy log no longer reaches back, the canvas list and every canvas's elements are found again (the layouts kept for elements that stay), and when the transform log does not, every element's activity is checked; dirty marks; the re-layout root; reparenting plain entities for free |
| `gameui:91-92` | feature | home | `Validate` and the Debug assert after every `EnsureLayout`; `GameUISceneStats` and `TakeStats` |
| `gameui:109` | feature | home | Only elements whose box changed rewrite their quads and bump the hit stamp |
| `gameui:241` | feature | home | The perf tests `Perf.GameUI.Layout10k`, `Perf.GameUI.IdleFrame10k` and `PerfGPU.GameUI.Render10k`, and their budgets; `PerfGPU.GameUI.RenderIdle10k`, the UI pass of an idle frame, which checks that it uploads nothing at 10,000 elements and whose budget is provisional, with no measured value (the page says so and names no `perf.<name>` key for it, R41) |
| `gameui:401` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:106-149`: the constructor connecting `on_construct`, `on_update` and `on_destroy` of every UI component |
| `gameui:402` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:198-242`: `OnLayoutChanged`, `OnVisualChanged` and `OnTextChanged`, different changes at different costs |
| `gameui:400` | code | home | `Strata/src/Strata/GameUI/GameUILayout.cpp:87-159`: `UpdateLayout`, the walk up to the re-layout root, nested roots dropped, only moved boxes marked |
| `gameui:404` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:961-1023`: `DependsOnChildren` and `EnsureLayout`, the lazy layout, views sorted by sort order, the Debug validation |
| `gameui:405` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:1394-1459`: `Validate`, a cache checked by recomputation, the error that names the entity |
| `gameui:406` | code | home | `StrataTests/src/GameUI/GameUILayoutTests.cpp:485-586`: the idle frame that does no work, a change that costs its element, and the unsignaled write that fails validation |
| `gameui:451` | figure | home | Dirty propagation: change, mark, walk up, re-layout, compare boxes, mark quads, journal range, partial upload |
| `gameui:505` | figure | home | The Performance panel with the `Render.UI` and `GPU.UI` stages on a scene of many elements, idle and after one change |
| `gameui:511` | rule | home | Signal every direct write to a UI component: the scene's UI recomputes only what it was told; Debug builds name the culprit |
| `gameui:514` | rule | link | Values written right after `AddComponent` need no signal: the UI components follow the scene's rule, said in one sentence (its home is `world/scene-graph`) |
| `new:16` | feature | home | The writers that already signal: `ComponentAccess::SetProperty` (which the editor's property edits go through), the script API and the UI system; `IUIControl::SetText` patches only when the text changed, because games set their HUD every frame and a signal would reshape it, and on an input field it writes one line cut to the character limit. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:24-26`; `Strata/src/Strata/Scene/ComponentAccess.cpp:117-146` (the signal at 144); `StrataEditor/src/Editor/PropertyEdit.cpp:104`, `:148`; `Strata/src/Strata/GameUI/GameUISystem.cpp:970-992` (the comment at 988); `StrataScriptCore/Include/StrataScript/UI.h:54` |
| `gameui:559` | rule | home | Hierarchy changes go through `Scene` (`SetParent`), as everywhere; reparenting plain entities costs the UI nothing |
| `gameui:551` | rule | home | An idle frame costs a pointer comparison: every scene runs the UI system, so a HUD must not cost per element per frame |
| `gameui:591` | hands-on | home | Exercise: trace a frame with breakpoints in `GameUISystem::OnUpdate` and `GameUIRenderer::Prepare`, change one label, and record which counters of `TakeStats` move |
| `gameui:593` | hands-on | home | Exercise: write a `UIRect` field without `MarkModified` in a test and read the Debug assert and the message of `Validate` |
| `gameui:639`, `gameui:642-643` | term | home | UI contract; validation; layout (cached) |
| `gameui:75` | feature | use | The element array and its subtree ranges, from `ui/layout` |
| `gameui:235` | feature | use | The suite `GameUI.Dirty` of `GameUILayoutTests.cpp` |
| `scene-ecs:28` | feature | use | `MarkModified` as `registry.patch`, the engine-wide signal of a change (`world/scene-graph`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The transform contract and change signals (`on_construct`, `on_update`, `on_destroy`; `MarkModified`, `registry.patch`) | `world/scene-graph` | must |
| The hierarchy version, and activity read through the transform change log | `world/scene-graph` | must |
| EnTT's registry, storages and context | `world/ecs` | must |
| The element array, the boxes and the two layout passes | `ui/layout` | must |
| Asserts compiled into Debug builds only | `core/conventions` | must |
| Asset content that changes when a font finishes loading | `assets/loading` | helps |
| Profiler stages and the Performance panel | `core/profiling` | helps |
| Breakpoints in a debugger attached to the engine | `core/debugging` | helps |
| Perf tests and their budgets | `engineering/perf-lab` | helps |
| A test case with doctest | `core/first-change` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `layout-cached` | Layout (cached) | - |
| `ui-contract` | UI contract | - |
| `validation` | Validation | - |

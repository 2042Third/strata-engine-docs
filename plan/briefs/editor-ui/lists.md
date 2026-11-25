# Brief: `editor-ui/lists`

| Field | Value |
| --- | --- |
| Title | Lists that scale |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/shell`, `editor/thumbnails` |
| From | editor-ui ch. 9 (`HierarchyView` and `AssetBrowserView`, core code drawn here; `ImGuiListClipper`, multi-select, drop zones, thumbnails per tile, background tables) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/lists` — Lists that scale

**Covers.** Why a scene of 100,000 entities and a project of 10,000 assets cost no more per frame than what the screen
shows. The problem and how engines solve it: a frame's cost must follow the screen, not the data; cached views rebuilt
only when a version changes, virtualized lists, stable identities for selection, background work for big tables. The
map: the core's `HierarchyView` and `AssetBrowserView` (no UI) and the Hierarchy and Content Browser panels that draw
them. The contract: never walk the scene or the asset folder per frame; rows identify themselves by entity handle or
UUID, never by row index; a thumbnail is requested every frame its tile shows. The toy is a clipped list of 100,000
rows in about 40 lines.

The real code in the order data flows: the version-gated rebuild and the depth-first walk over first-child and
next-sibling links with a resume stack (a diagram: tree, rows, screen); the filter terms (`c:`, `t:`, `l:`, `cell:`) and
filtering that marks each ancestor once, so the walk stays linear in the scene; the Hierarchy's one `BeginMultiSelect`
scope with `ImGuiListClipper`, rows included by index when they are off screen (the range's source, the row being
renamed), and the selection requests applied to the editor's own selection, which teaches multi-selection (click, Ctrl,
Shift ranges from an anchor, box select, clear on void, the primary selection; a diagram of the request flow); drop
zones mapped to `entity.setParent` with the correction for entities that leave the list before the insertion point, and
the refusal of cycles (a diagram); the Content Browser's grid clipped by rows of tiles, its labels cached per rebuild
and width, and a thumbnail requested per visible tile. Then the other cached and clipped lists of the editor, and drag
and drop: a source that sets a typed payload, a target that accepts it and acts when it is delivered on the release (the
Hierarchy accepts before delivery to draw its drop line), and the editor's three payloads. Pictures: the Hierarchy
expanded and searched, a drag with its drop line, the Content Browser's grid. At the end the reader can add a filter
term with its tests and measure what the clipper saves.

**Leaves out.**

- How thumbnails are rendered and cached → `editor/thumbnails`
- What a reparent does to the scene (`SetParent`, the transform contract) → `world/scene-graph`
- The instrument panels' tables → `editor-ui/instrument-panels`
- The Content Browser's file actions and the trash → `editor/trash-references`
- An asset dragged into the Scene view → `editor-ui/scene-view`
- The selection's storage in `EditorContext` → `editor/program`

**Fit.** `fits`: about 6,320 words against L (5,000). Five excerpts, two concepts and six figures take the most, with
drag and drop in about 120 words; the page stands about 180 words below L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:144` | feature | home | The Hierarchy panel: multi-select, drag and drop, rename in place, the eye toggle, the prefab badge, search, the create menu, the empty-scene hint, the world strip |
| `editor-ui:147` | feature | home | The Content Browser: folder tree, grid and list, breadcrumbs, search, type chips, tile slider, New, Import, drag sources and folder targets, rename, delete, the Scripts root |
| `editor-ui:161-169` | feature | home | `HierarchyView` and its filter, drop zones, `GetTopmostInHierarchyOrder`, the Hierarchy's drawing, `AssetBrowserView`, the grid clipped by rows, thumbnails per tile, the other cached and clipped lists |
| `editor-ui:242` | feature | home | Drag and drop and the drag payloads `STRATA_ENTITIES`, `STRATA_ASSET` and `STRATA_ASSET_FOLDER`: a source sets a typed payload, a target accepts it and acts on its delivery at the release, and `AcceptBeforeDelivery` lets the Hierarchy draw its drop line first (critic-editor-ui-1, about 120 words; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:779-783`, `:1025-1068`; `StrataEditor/src/Panels/ContentBrowserPanel.cpp:90-94`, `:402-433`) |
| `editor-ui:366` | concept | home | Scaling UI to large data: version-gated caches, virtualization, stable identities, background sorting, thumbnails per frame; walking per frame, selecting by index |
| `editor-ui:372` | concept | home | Multi-selection semantics and ImGui's request protocol; letting ImGui own the selection, ranges that take filtered-out rows |
| `editor-ui:453` | code | home | `StrataEditor/src/Editor/HierarchyView.cpp:230-264`: the central algorithm, the depth-first walk with a resume stack; with the version gate at 134-151 |
| `editor-ui:454` | code | home | `StrataEditor/src/Editor/HierarchyView.cpp:266-327`: filtering with each ancestor marked once |
| `editor-ui:455` | code | home | `StrataEditor/src/Editor/HierarchyView.cpp:555-610`: a drop position mapped to a parent and an index, the leaving correction and the refused cycles |
| `editor-ui:456` | code | home | `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:655-731`: `BeginMultiSelect` with the clipper and rows included by index; with `ApplySelectionRequests` at 1135-1192 |
| `editor-ui:457` | code | home | `StrataEditor/src/Panels/ContentBrowserPanel.cpp:858-933`: the grid clipped by rows, and the thumbnail asked for while the tile shows |
| `editor-ui:506` | figure | home | Tree to rows to screen: expanded and collapsed nodes, the flat rows with depths and the resume stack, the clipper's window; matches and dimmed ancestors |
| `editor-ui:508` | figure | home | Drop zones on a row: before, inside, after, and the line after an expanded row |
| `editor-ui:509` | figure | home | The multi-select request flow from ImGui to `EditorContext::SetSelection` and back |
| `editor-ui:551` | figure | home | The Hierarchy with expanded groups, prefab badges and an inactive entity; the same searched with `c:Light`; rename in place |
| `editor-ui:553` | figure | home | A Hierarchy drag with its drop line and the inside highlight |
| `editor-ui:554` | figure | home | The Content Browser's grid with thumbnails and a model's sub-asset band; the list view; the Scripts root |
| `editor-ui:607` | rule | home | Never walk the scene or the asset directory per frame; draw cached views; clip long lists |
| `editor-ui:610` | rule | home | Rows identify themselves by entity handle or UUID, never by row index |
| `editor-ui:648` | rule | home | Thumbnails are requested every frame they are on screen, the type icon drawn until ready |
| `editor-ui:672` | hands-on | home | Add a Hierarchy filter term (`a:` for inactive entities) with `Editor.HierarchyView` tests |
| `editor-ui:673` | hands-on | home | Measure 100,000 entities with and without the clipper in a scratch build, not committed |
| `new:36` | hands-on | home | Trace it yourself (D27): a breakpoint in `HierarchyView::Update` on a large scene shows an idle frame returning before `Rebuild`, a reparent rebuilding the rows once because the hierarchy version moved, and a rename rebuilding them only while a search by name is typed. Evidence: `StrataEditor/src/Editor/HierarchyView.cpp:134-151`, `:192-194` |
| `editor-ui:735-741` | term | home | `ImGuiListClipper`; virtualization; multi-select; selection user data; range selection, anchor and box select; primary selection; drag and drop payload |
| `assets:142` | feature | home | The editor asset manager's folder index (`GetFolders`, `GetAssetsInFolder`, `ListAssets`, `GetChangeVersion`), which `AssetBrowserView` reads instead of the disk |
| `editor-core:258` | feature | home | `HierarchyView` and `AssetBrowserView` as the core's models of UI lists: taught with `editor-ui:161` and `editor-ui:166` |
| `editor-core:595` | rule | home | Never walk the scene or the asset directory per frame in UI code: one rule with `editor-ui:607` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The scene's hierarchy: first-child and next-sibling links, depth, the hierarchy version | `world/scene-graph` | must |
| Handles instead of pointers; entity handles and UUIDs | `world/ecs` | must |
| EnTT's signals | `world/scene-graph` | must |
| Thumbnails: the cache, requests per frame, the type icon until ready | `editor/thumbnails` | must |
| Commands (`entity.setParent`) and their parameters | `editor/commands` | must |
| Panels, the registry and deferred actions | `editor-ui/shell` | must |
| ImGui's items, IDs, child windows and tables | `editor-ui/imgui` | must |
| The kit's search field and selection colors | `editor-ui/widget-kit` | must |
| What data structures cost: stacks, hash sets, linear walks | `basics/data-structures` | must |
| Asset handles, `.meta` files and sub-assets | `assets/handles-meta` | helps |
| Jobs for background work | `core/jobs` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `drag-and-drop-payload` | Drag and drop payload | - |
| `imguilistclipper` | ImGuiListClipper | - |
| `multi-select-beginmultiselect` | Multi-select (BeginMultiSelect) | - |
| `primary-selection` | Primary selection | - |
| `range-selection` | Range selection | box select |
| `selection-user-data` | Selection user data | - |
| `virtualization` | Virtualization | - |

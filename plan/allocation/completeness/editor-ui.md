# Completeness: critic-editor-ui

## Findings

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-editor-ui-1 | must | missing-item | `editor-ui:299` on `editor-ui/imgui` | No page teaches ImGui's layout or its containers: the cursor and `SameLine`, the content region and item widths, tables, menu bars and menus, context popups, combos, tab bars, and the drag and drop protocol. No inventory lists them. Yet `editor-ui/lists` assumes "tables" from `editor-ui/imgui` at depth must, and 15 files of the area draw tables. | Add a section "Layout and containers" to `editor-ui/imgui`, about 450 words: the cursor and `SameLine`, the content region, tables with flags and sort specs, menus and context popups, combos and tab bars. Drag and drop (a source, a typed payload, a target, the accept on release) can go there, or about 120 words on `editor-ui/lists`, which homes the payloads. The page then needs XL, or its docking paragraph moves to `editor-ui/shell`. | allocation/editor-ui.md:60-77, 576; inventory/editor-ui.md:299-305; `StrataEditor/src/Panels/StreamingPanel.cpp:857-877` (a sortable table); `SceneHierarchyPanel.cpp:783, 1033`; `ContentBrowserPanel.cpp:92, 413-433`; `EditorLayer.cpp:1449-1677` (menus) |
| critic-editor-ui-2 | should | missing-item | new on `editor-ui/ui-scale` | In play, the editor gives the game the display's UI scale: the override, or the content scale less the points factor. It never includes the person's interface factor, because that factor sizes the editor and not the game. A game's canvases in the Game view therefore keep the size a player's display gives them. No inventory lists this. | Add a feature, about 80 words, after the factor on `editor-ui/ui-scale`. `editor-ui/game-view` links it in one sentence. | `StrataEditor/src/EditorLayer.cpp:636-638`; `Strata/src/Strata/ImGui/ImGuiLayer.h:68-71`; `StrataEditor/src/EditorHost.h:52`; `StrataEditor/src/Editor/EditorGameWindow.h:39` |
| critic-editor-ui-3 | could | duplicate | `editor-ui:220` on `editor-ui/launcher-dialogs` | Two pages describe the External Editor page from the same angle. It is a custom `SettingsPage` of the Preferences dialog, registered in the editor's page registry. Its home is the launcher-dialogs page, beside New Script, and the settings-windows page also describes it among the Preferences pages. | Home the External Editor page on `editor-ui/settings-windows`, as the fourth custom page beside Graphics Quality, Collision Layers and Input Actions. `editor-ui/launcher-dialogs` keeps New Script and links to it. | allocation/editor-ui.md:961, 983, 1033; inventory/editor-ui.md:220, 275; `StrataEditor/src/UI/ScriptDialogs.h:43-47`; `StrataEditor/src/EditorLayer.cpp:149` |
| critic-editor-ui-4 | could | duplicate | `editor-ui:376` on `editor-ui/inspectors` | The inspectors page compares ways engines describe their types: Unreal's generated `UPROPERTY` code, Unity's attributes and Strata's registration tables. `world/reflection` carries the full comparison of the same approaches, Unreal's UHT among them. | On `editor-ui/inspectors`, compare ways to build inspectors: one generic inspector from metadata, hand-written editors per type, and custom drawers as escape hatches (Unity, Unreal and Godot each have them). Link `world/reflection` for how the metadata is obtained. This saves about 100 words. | allocation/editor-ui.md:584-586; allocation/world.md:424-427; inventory/editor-ui.md:376-378 |
| critic-editor-ui-5 | could | missing-item | `editor-ui:118` on `editor-ui/status` | The inventory gives the 5 fps floor of idle throttling but not its reason. The frame pacer sleeps through input, so an idle editor answers the first input up to one idle interval late (33 ms at 30 fps, 100 ms at 10 fps unfocused). That is why no rate under 5 fps is offered. | Add the limit and its reason to the idle-throttling section, about 60 words. | `StrataEditor/src/Editor/EditorFrameRate.h:30-32`; inventory/editor-ui.md:118 |
| critic-editor-ui-6 | could | missing-item | new on `editor-ui/instrument-panels` | When a Play fails because its script build failed or its module did not load, `play.start` raises a request counter. The UI compares that counter every frame and brings the Problems panel forward. The core asks the UI without knowing it, as with the inspection version. No inventory lists this. | Add it to the Problems panel's section, about 50 words. Name the counter pattern once and link `editor-ui:190`'s tab switch on `editor-ui/shell`. | `StrataEditor/src/Editor/Commands/PlayCommands.cpp:57-68`; `StrataEditor/src/Editor/EditorContext.h:608-609`; `StrataEditor/src/EditorLayer.cpp:751-756` |
| critic-editor-ui-7 | could | missing-item | new on `editor-ui/game-view` and `editor-ui/design-system` | Two absences are stated nowhere. The editor's shortcuts cannot be rebound, and the editor has one theme. The Roadmap leaves both for later. The preferences have three sections only: the external editor, the interface scale and the frame rate. | Add two not-done items: shortcuts on `editor-ui/game-view` and theme variants on `editor-ui/design-system`, about 40 words each, with the evidence run again at the pin. | `Docs/Roadmap.md:993`; `StrataEditor/src/Editor/EditorPreferences.cpp:69-74`; `StrataEditor/src/EditorLayer.cpp:951-985` (literal chords) |
| critic-editor-ui-8 | could | missing-item | `editor-ui:306` on `editor-ui/imgui-backends` | The page gives reasons why Strata writes its own platform backend, but not the measured one. ImGui's stock GLFW backend cost 0.05 to 0.06 ms of every frame on multi-viewport support that the editor does not use. The book's design decision is to show measured trade-offs. | Add the measurement to the reasons, about 40 words, with its source. | `Docs/Roadmap.md:140-142` |
| critic-editor-ui-9 | could | missing-item | new on `editor-ui/design-system` | The survey's file list leaves out `StrataEditor/src/EditorIcon.h`, the editor window's icon. It holds the strata mark at nine sizes, Windows' small and large icons at 100 to 200% scaling, so the system never stretches a smaller image. It also holds a 256-pixel PNG for macOS's Dock. The images are embedded raw and generated by `Tools/GenerateBrandAssets.py`. | Add one paragraph to the brand mark's part, about 60 words. | `StrataEditor/src/EditorIcon.h:33-40`; `StrataEditor/src/EditorApplication.cpp:47-60`; `Tools/GenerateBrandAssets.py:1-21` |
| critic-editor-ui-10 | could | missing-item | new on `editor-ui/design-system` | The page does not say why ImGui's own rasterizer may read fonts that skip `FontValidation`, when the rule says font files are untrusted input. The reason: the editor's atlas reads only its compiled-in fonts and the system's own fallback fonts, never a project's font file. A reader of `gpu/text` will ask this. | Add the trust boundary to the text-rendering section, about 50 words, and link `gpu/text`'s validation. | `StrataEditor/src/UI/EditorFonts.cpp:69-97, 131-152` (the only `AddFontFromMemoryTTF` call in `StrataEditor/src`); `AGENTS.md:412`; `Docs/DeveloperGuide.md:6204` |
| critic-editor-ui-11 | could | stale-item | `editor-ui:885` on `editor-ui/ui-testing` | The home row places the panels' budgets at lines 101-104 of `Budgets.json`. The pin has five `Perf.EditorPanels` rows, at lines 101-105, and one of them (`Performance600FramesPausedP95`) is Provisional, with no measurement. | Change the row to lines 101-105, and let the page say that one budget is provisional. | allocation/editor-ui.md:1195; `StrataTests/Perf/Budgets.json:101-105` |
| critic-editor-ui-12 | could | other | `editor-ui/ui-testing`, `editor-ui/scene-view`, `editor-ui/widget-kit` | Three Assumes rows name the wrong teacher. Each true teacher is in the page's closure. ImGui's input queue is taught on `editor-ui/imgui-backends`, not `editor-ui/imgui`. The chips and the chip strip are taught on `editor-ui/widget-kit`, not `editor-ui/shell`. Draw lists are taught on `editor-ui/imgui-backends` (term `editor-ui:713`), not `editor-ui/imgui`. | Name the true teachers in the three rows. | allocation/editor-ui.md:1203, 775, 394; allocation/editor-ui.md:126-131, 342-345, 180 |
| critic-editor-ui-13 | could | other | `editor-ui:118` on track G | No page on track G warns a game maker about idle throttling. While nothing happens, the frame pill reads about 30 FPS, or 10 FPS without the focus, and a game maker may take that for a slow game. The only other row of `editor-ui:118` is a link from `reference/settings`. | Add a use row to `make/editor-tour`, where the pills are shown, or to `make/performance`: one sentence, about 40 words. | `StrataEditor/src/EditorLayer.h:118-124`; `StrataEditor/src/EditorLayer.cpp:1951`; prep/where/editor-ui.tsv (row `editor-ui:118`) |

## What was checked

- Homes (step 1): every one of the 432 items of `prep/where/editor-ui.tsv`. 393 have their home on the part's
  17 pages and 33 were passed out of the part and taken (all with a home row). 6 are `nowhere`. Each home was compared
  with the page's title, kind and track in `pages.tsv`, and with its Covers paragraph in `allocation/editor-ui.md` (all
  17 read). Rows passed out were checked against the receiving pages' rows (`editor/camera-viewport` read in full;
  `make/editor-tour`, `make/performance`, `make/export`, `input/rebinding` and `world/reflection` read at their Covers or
  rows). One home is a real duplicate (finding 3). No home was misplaced beyond that. `editor-ui:203` on
  `editor-ui/game-view` agrees with the page's title and with `book.md`'s one-home row for shortcuts.
- Thin homes (step 2): every concept (26), code (38), figure (58), rule (35) and hands-on (24) item, compared with its
  home row and the page's Covers. The long features were compared too: 39, 40, 110, 112, 114, 116, 118, 120, 134, 144,
  146, 147, 151, 165, 179, 183, 184, 187, 198, 200, 202, 207, 208, 214, 238. Where a home row lumps a range, the Covers
  was read for each part. Parts a row hands to other pages were followed there:
  - the camera's mathematics, to `editor/camera-viewport`;
  - the Asset tab's world view and Cook button, to `editor/worlds` through `worlds-runtime:113-117`;
  - collision layers and the quality preset of `editor-ui:691`, to `make/physics` and `make/quality`;
  - the Activity panel's actions of `editor-ui:692`, to `make/with-an-agent`.

  Nothing a reader needs was left without a page, except finding 5. Terms (88) were checked only for their home page.
- Nowhere (step 3): all 6 (`editor-ui:852`, `856`, `864`, `869`, `871`, `881`). They are notes about the survey, or a
  question settled at the pin. I checked `Include/Common.slang`'s guard at lines 1-2. None of them is needed by the book.
- Missing from the inventory (step 4), by these sweeps:
  - A script listed the type, function and constant names of the area's 50 headers: `ImGui/`, `UI/` without `Icons.h`,
    `Panels/`, `EditorLayer.h` and `EditorHost.h`. It looked each name up in every inventory and item table: 621 names
    appear in none. I judged them by reading the header comments of the files the survey did not read past their
    headers: `PerformancePanel`, `CellMap`, `AnimationAssetViews`, `AssetInspectorPanel`, `ConsolePanel`, `ScriptBrowser`,
    `ViewportToolbar`, `GraphicsQualityPage`, `CollisionLayersPage`, `WelcomePanel`, `SceneHierarchyPanel`,
    `ViewportPanel`, `ScriptDialogs`, `DeleteAssetDialog` and `PropertyWidgets`. I also read all of `ImGuiModule.h`,
    `ImGuiLayer.h`, `ImGuiPlatform.h`, `ItemProbe.{h,cpp}` and `EditorLayer.h`. What they hold is either in an
    inventory (cell map in `worlds-runtime:113`, animation views in `animation:191`, CPU or GPU bound in
    `foundation:304`, the log ring in `foundation:91`, prefab by drop in `gamedev:96`) or is a name that only a
    reference list would carry.
  - ImGui API families used in the area (`BeginTable`, drag and drop, menus, combos, tab bars, child windows) were
    counted at the pin and looked up in the plan (finding 1).
  - The bullets of the Developer Guide's "Editor UI rules" at the pin were checked against the inventory: all are listed.
  - Other sources were read: `Docs/Manual/GameView.md` at the pin; the root files of `StrataEditor/src`, which led to
    `EditorIcon.h`; `EditorApplication.cpp:300-368`; the preference sections; the Roadmap's lines on the editor's UI,
    the ImGui vendor build, and `ImGui.frag.slang`'s includes.
- Stale items (step 5): these were spot-checked at the pin and match.
  - Constants: `c_LayoutVersion` 5, the default layout's shares and minimums, `ThumbnailCache::c_Version` 11, four
    notifications with lifetimes of 5, 8 and 12 s, `c_MaxFocusAttempts` 4, `c_MouseHintSeconds` 5, `c_AgentFlashSeconds`
    0.6 and `c_TableRefreshSeconds` 0.25.
  - Counts: the test cases (45, 26, 62, 23, 19), the 11 `Editor.UI.Source` cases, the header counts (32 and 15) and the
    shader lines (53 and 68).
  - Claims: the probe's "every build configuration", the Hierarchy's `PushID` at line 742, the macOS swap at
    `imgui.cpp:1731-1735` and its test, and the dynamic textures' whole rewrite.

  One stale place was found (finding 11). The wrong header lines are not repeated here: coverage.md already lists them
  among the unit's questions.

## Not checked

- The bodies of most `.cpp` files of the area beyond the parts named above. In particular: `InspectorPanel.cpp`,
  `ContentBrowserPanel.cpp`, `StreamingPanel.cpp`, `PerformancePanel.cpp`, `InputActionsPage.cpp`,
  `GraphicsQualityPage.cpp`, `Markdown.cpp`, `CanvasModeView.cpp` and `UIRectDrawer.cpp`. Behaviours known only from
  their bodies may still be missing.
- The 621 swept names one by one. Only the files named above were judged, from their header comments.
- The test bodies, and the suites the inventory does not count: `EditorAnimationUITests`, `EditorGameUITests`,
  `EditorScriptUITests`, `EditorWorldUITests` and `EditorUITextTests`.
- The glossary wording of the 88 terms, and whether each term's entry suits a reader of its home page.
- The items of other inventories that were passed to the part's pages. These were read only where a row named them.
- Whether the routes in `pipelines.md` §7.1 will generate the tables of `reference/editor` (panels, menus,
  shortcuts). No route lists them, and I did not judge that page.
- The Architecture.md "Editor" section and the Developer Guide sections other than "Editor UI rules".

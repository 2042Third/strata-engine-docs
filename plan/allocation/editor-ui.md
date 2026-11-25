# Allocation: editor-ui

## `editor-ui/immediate-mode` — Why immediate mode

**Covers.** The page starts from a problem the reader can picture: a panel with one slider for a light's intensity. In
a retained toolkit the program builds a slider object, connects a callback, and keeps the slider's value and the
light's value in step. A tool that changes every week breaks where the two copies disagree. The naive answer, the
retained game UI that `ui/what-game-ui-does` explained, needs the same synchronization. Then the idea: in an
immediate-mode UI the code describes the whole UI every frame, one call draws a widget and returns what the person did
with it, and the program's own variable is the state. The library keeps only a little state, keyed by IDs (a diagram
of the two data flows). The approaches table compares retained toolkits (Qt, WPF, the HTML DOM, Unreal's Slate,
Unity's UI Toolkit) with immediate-mode libraries (Dear ImGui, Unity's IMGUI) by code per change, state to keep in
step, layout power, accessibility and cost per frame, for tools only; the general comparison stays on
`ui/what-game-ui-does`.

Strata's choice follows: Dear ImGui for the editor and tools, retained components for games. The `ImGui` layer is a
Tooling layer, so a shipped game links no ImGui, and the editor's UI is a library apart from its core, so a button runs
a command. The page ends with what the choice cannot do (accessibility, rich layout, layout decided one frame late, a
cost that grows with what is submitted) and the common mistakes: thinking ImGui stores the value, waiting for a
callback, forgetting that one call both draws and reports. The running example is the light slider, sketched both ways
in about ten lines each. At the end the reader can say why the editor's UI is immediate and the game's retained, and
read an immediate-mode widget call.

**Leaves out.**

- ImGui's frames, windows, items and IDs → `editor-ui/imgui`
- What an editor is, and the split of the editor's core from its UI → `editor/program`
- The general comparison of retained and immediate UIs, and why the game UI is retained → `ui/what-game-ui-does`
- How panels, the host and the shell fit together → `editor-ui/shell`
- Panels torn out into windows of their own (Strata has one main viewport) → `editor-ui/shell`

**Fit.** `fits`: about 3,175 words against M (3,000). The three exercises (`new:25`) and the idea with the diagram of
the two data flows take the most; the table compares the approaches for tools only, because the general table is
`ui/what-game-ui-does`'.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:291` | concept | home | Retained against immediate mode for tools: code-first UI, no state to keep in step, layout every frame, the trade-offs, why Strata takes Dear ImGui, the three newcomers' mistakes |
| `editor-ui:480` | figure | home | The two data flows side by side: a widget tree with callbacks, and per-frame code with ImGui's state by ID producing draw data |
| `editor-ui:284` | concept | use | What an editor is and why it is not the game: one sentence and a link; the Tooling half (games link no ImGui) is taught here |
| `editor-ui:700-701` | term | use | Immediate-mode and retained-mode GUI, as `ui/what-game-ui-does` defines them |
| `editor-ui:702` | term | use | Dear ImGui named and placed; its home is `editor-ui/imgui` |
| `editor-ui:35` | feature | link | The ImGui module lives in the Tooling layer `ImGui` (`StrataTests/Architecture/Layers.json:105-111`) |
| `new:1` | feature | link | The version and build of Dear ImGui, taught on `editor-ui/imgui` |
| `new:6` | not-done | link | One main viewport: no panel in a window of its own, stated on `editor-ui/shell` |
| `new:25` | hands-on | home | Exercises (D27): what `UI::ToolbarButton` returns in a frame where the person only hovers it, and where a toggle chip's state lives (Basic, predict); the page's light slider written both ways as a C++ sketch on the workbench, a retained slider object with a callback and an immediate function that draws and returns the new value, both driven by the same three simulated frames of a drag and their output compared (Medium, done); which of three tools a team should build retained (a level editor, a settings screen for players, a debug overlay), and why (Hard, design). Evidence: `StrataEditor/src/UI/Widgets.h:45-55` (the kit's buttons return what the person did; `ToggleChip` writes the caller's `bool`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an editor is, and why it is not the game; the editor's core and UI libraries | `editor/program` | must |
| What a game UI must do; retained against immediate UIs | `ui/what-game-ui-does` | must |
| The layer table, Tooling layers and why games link no tooling | `core/layers-registries` | must |
| Commands are the API: a button runs a command | `editor/commands` | helps |
| A frame and the frame loop | `core/frame-loop` | helps |

## `editor-ui/imgui` — Dear ImGui from first principles

**Covers.** Dear ImGui from first principles, on a scratch layer the reader adds to a source build: one `Layer` whose
`OnImGuiRender` draws a window with a counter. The order: the frame (`NewFrame`, the widget calls, `Render` and the
draw data it produces, and that Strata's ImGui module makes these calls); windows (`Begin` and `End`, the bool `Begin`
returns, `End` always called) and child windows; items (a call draws and returns the interaction, and "last item"
queries such as `IsItemHovered` and `GetItemRectMin`); IDs (hashes of labels and pushed scopes, the ID stack, the `##`
and `###` suffixes), with Strata's examples: Hierarchy rows push their entity's UUID bytes as their ID
(`StrataEditor/src/Panels/SceneHierarchyPanel.cpp:742`) and panel windows are named `<icon> <title>###<id>`. Then
hovered, active and focused, and keyboard navigation with its nav cursor; popups and modals, and the rule that ImGui
keeps one popup per level, so a modal opened at the top closes the open one; layout and containers (the cursor and
`SameLine`, the content region and item widths, tables with their flags and sort specs, the menu bar and its menus,
context popups, combos), with the Streaming panel's sortable table as the example; style, style variables and style
colors with their push and pop; the ImGui context; docking as a person sees it (dock spaces, nodes, tab bars) and the
`imgui.ini` file.

The approaches table puts Dear ImGui beside other immediate-mode libraries (Nuklear, microui, egui). Strata's choice:
Dear ImGui 1.92.9 on its docking branch, built from its core only and without its obsolete functions, with one main
viewport. Common mistakes: two "OK" buttons in one scope share an ID; a window renamed without `###` loses its place in
the dock; `End` skipped when `Begin` returns false; a "last item" query read after another call. The exercises grow
the scratch layer: a counter, a list whose rows push their IDs, a modal. At the end the reader can write a small tool
window, give its widgets unique IDs and open a modal.

**Leaves out.**

- How ImGui's input and draw data reach the window and the GPU → `editor-ui/imgui-backends`
- How the editor builds a default layout and keeps panels' open states → `editor-ui/shell`
- Writing custom widgets on `InvisibleButton` → `editor-ui/widget-kit`
- Clipped lists and multi-selection → `editor-ui/lists`
- Shortcut routing → `editor-ui/game-view`
- Why the editor's UI is immediate → `editor-ui/immediate-mode`

**Fit.** `fits`: about 5,250 words against L (5,000). Twelve terms taught from zero in one scratch layer take the most,
with layout and containers (about 450 words, `new:26`) and three exercises in the same layer.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:299` | concept | home | ImGui's model: the frame, windows and child windows, popups and modals (one popup per level), the last item, the ID stack, `##` and `###`, hovered, active and focused, keyboard navigation; Strata's examples and pitfalls |
| `new:1` | feature | home | Dear ImGui 1.92.9, docking branch, built from its core only (Strata writes both backends) with `IMGUI_DISABLE_OBSOLETE_FUNCTIONS`, linked only by tools. Evidence: `Strata/vendor/imgui/imgui.h:32`; `Strata/vendor/CMakeLists.txt:89-100` |
| `editor-ui:702-709` | term | home | Dear ImGui, the ImGui context, ID and ID stack, `##` and `###`, item, window and child window, popup and modal, dock space, dock node and tab bar |
| `editor-ui:711` | term | home | `imgui.ini` (Strata's is `EditorLayout.ini`, with sections of its own taught on `editor-ui/shell`) |
| `editor-ui:726` | term | home | Style, style variable and style color, with their push and pop stacks |
| `editor-ui:732-733` | term | home | Nav cursor; hovered, active and focused |
| `editor-ui:132` | feature | use | Panel windows named `<icon> <title>###<id>`, as the example of a stable window ID |
| `editor-ui:619` | rule | link | One popup per level, which is why the editor draws nested questions inside the open modal (`editor-ui/shell`) |
| `editor-ui:35` | feature | link | The ImGui module calls `NewFrame` and `Render` each frame (`editor-ui/imgui-backends`) |
| `new:6` | not-done | link | One main viewport: ImGui's multi-viewports are not used |
| `new:26` | concept | home | Layout and containers (critic-editor-ui-1, about 450 words): the cursor and `SameLine`, the content region and item widths, tables with their flags and sort specs, the menu bar, menus and menu items, context popups, combos; the dock's tab bars are taught with docking, since the editor draws no tab bar of its own; drag and drop is `editor-ui/lists`'. Evidence: `StrataEditor/src/Panels/StreamingPanel.cpp:857-877` (a sortable, resizable table sized from the content region); `StrataEditor/src/EditorLayer.cpp:1449-1628` (`DrawMenuBar`); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:648`, `:925` (context popups), `:512` (a combo); `grep -rn BeginTabBar StrataEditor/src` finds nothing |
| `new:27` | hands-on | home | Exercises (D27), in the page's scratch layer: a counter whose button and text share a line (Basic, done); a list of ten rows, each with a "Delete" button, whose clicks all reach the first row until each row pushes its own ID, as the Hierarchy pushes an entity's UUID (Medium, predict then run); a modal opened from a menu item that asks a question and closes on its answer (Hard, extend). The solutions are patches against the pin. Evidence: `Strata/src/Strata/Core/Layer.h:23` (`OnImGuiRender`); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:742`; `StrataEditor/src/UI/Widgets.h:150-156` (the kit's modals) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Windows, events, layers and the layer stack (`OnImGuiRender`) | `core/windows-events` | must |
| Building Strata from source and running a change | `core/first-change` | must |
| Classes, inheritance and virtual functions (a `Layer` subclass) | `basics/cpp-classes` | must |
| Hashes (an ID is a hash of a string) | `basics/data-formats` | helps |
| The immediate-mode idea: code describes the UI every frame | `editor-ui/immediate-mode` | helps |

## `editor-ui/imgui-backends` — ImGui backends

**Covers.** How Strata plugs ImGui into its window, its events and NVRHI. The job comes first, then the problem and how
engines solve it: ImGui knows no platform and no GPU; most engines take the stock backends (`imgui_impl_glfw`,
`imgui_impl_vulkan`); Strata writes both, because GLFW is sealed in `Platform/`, rendering goes through NVRHI, the
editor wants keys by keyboard layout and a cursor the game can own, and the stock GLFW backend was measured at 0.05 to
0.06 ms of every frame spent on multi-viewport support the editor does not use. The map: `ImGuiModule` → `ImGuiLayer` →
`ImGuiPlatform` and `ImGuiRenderer` → the two shaders. The contract: user textures outlive the frame's draw data, draw
callbacks are told apart by their data's address, a key's release is the key its press was queued as, and UI code draws
textures through `UI::TextureImage`. The toy is a renderer backend of about 60 lines.

The real code in the order data flows: the module's frame in ten lines and its `Editor.UI` stage; the layer's event
capture (the overlay sees events first and swallows what ImGui wants); the platform backend (keys by layout, modifiers
queued before the key, a release queued as its press was, focus loss, typed text and what an input method composed,
cursor shapes only while the cursor mode is Normal, the clipboard, delta time); the renderer (draw data and its memory
layout, pixels to NDC through push constants, a scissor per command, one pipeline per framebuffer format, binding sets
kept for 8 unused frames, the ring of mapped buffers guarded by event queries, ImGui 1.92's dynamic textures); the two
shaders and color spaces in UI (ImGui's colors are display values, sampling an sRGB texture decodes it, the texture
display modes); the `GPU.ImGui` stage. The page states the input-method entry of "What Strata does not do": the
editor's ImGui text fields take composed text and, on Windows, place the candidate list, while game UI shows no
composition. At the end the reader can follow one frame from a key press to pixels and compute the push constants of a
1600x900 window by hand.

**Leaves out.**

- The UI scale the layer applies to the style → `editor-ui/ui-scale`
- The theme the style callback installs, and the editor's fonts → `editor-ui/design-system`
- The kit's `UI::TextureImage`, as UI code calls it → `editor-ui/widget-kit`
- How a GPU draws a frame, and frames in flight → `gpu/how-a-gpu-frame-works`
- Binding sets, layouts and push constants in general → `gpu/binding`
- The engine's own text rendering (`FontAtlasCache`) → `gpu/text`
- Input-method composition in game UI → `ui/text`

**Fit.** `over`: about 7,075 words against L (5,000). Nine excerpts, three concepts, three figures, four rules and three
exercises do not fit L. Propose XL (8,000) by S2; or a split into `editor-ui/imgui-platform` "The platform backend:
events, keys, text and the cursor" (M) and `editor-ui/imgui-backends` "The renderer backend on NVRHI" (L).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:35-36` | feature | home | `ImGuiModule` (needs Graphics and a window it presents into, pushes the layer as the top overlay, draws in the `Editor.UI` stage) and `ImGuiLayer` (the context, navigation and docking, the layout file or none, blocking captured events) |
| `editor-ui:39-43` | feature | home | `ImGuiPlatform`, `ImGuiRenderer`, the texture display modes, the two shaders and the lazily registered `GPU.ImGui` stage |
| `editor-ui:306` | concept | home | Backends: platform and renderer; why Strata writes both, with the measured reason: ImGui's stock GLFW backend spent 0.05 to 0.06 ms of every frame on multi-viewport support the editor does not use (`Docs/Roadmap.md:140-142`; critic-editor-ui-8, about 40 words); double input from polling, stuck keys without focus-loss releases |
| `editor-ui:312` | concept | home | Drawing a UI on the GPU: draw lists, the orthographic mapping, blending, scissors, the font atlas as a texture, frames in flight, dynamic textures, the three pitfalls |
| `editor-ui:322` | concept | home | Color spaces in UI: display values, sRGB decode on sampling, two-channel normal maps, grayscale; judging an asset by a wrong preview |
| `editor-ui:429` | code | home | `Strata/src/Strata/ImGui/ImGuiModule.cpp:54-64`: the whole UI frame: `Begin`, the layers draw, `PrepareBackBuffer`, `End` |
| `editor-ui:430` | code | home | `Strata/src/Strata/ImGui/ImGuiLayer.cpp:88-109`: the content scale event, then the overlay that sees events first and marks handled what ImGui wants |
| `editor-ui:432` | code | home | `Strata/src/Strata/ImGui/ImGuiPlatform.cpp:162-184`: modifiers queued before the key, and a release queued as the key its press was |
| `editor-ui:433` | code | home | `Strata/src/Strata/ImGui/ImGuiPlatform.cpp:206-221`: the cursor shape set only on change and only while the cursor mode is Normal |
| `editor-ui:434` | code | home | `Strata/src/Strata/ImGui/ImGuiRenderer.cpp:407-518`: the central algorithm: event query of the last draw, texture updates, copying the lists, push constants (457-462), clip to scissor (491-503), callbacks, global offsets |
| `editor-ui:435` | code | home | `Strata/src/Strata/ImGui/ImGuiRenderer.cpp:314-342`: the bounded ring of mapped buffers, reused when its event query is done, waiting for the oldest past 8 |
| `editor-ui:436` | code | home | `Strata/src/Strata/ImGui/ImGuiRenderer.cpp:216-253`: dynamic textures: `WantCreate`, `WantUpdates` (the whole texture rewritten), `WantDestroy` |
| `editor-ui:437` | code | home | `Strata/src/Strata/ImGui/ImGuiRenderer.cpp:73-119`: display-mode callbacks told apart by the address of their data, because identical code may be folded |
| `editor-ui:438` | code | home | `Strata/shaders/ImGui.frag.slang:26-46`: sRGB encode, grayscale and the normal map's Z reconstructed; with `Strata/shaders/ImGui.vert.slang:20-25`, pixel to NDC by scale and translate |
| `editor-ui:486` | figure | home | Draw data's memory layout: lists of 20-byte vertices, 16-bit indices and commands, copied into one mapped vertex and one index buffer |
| `editor-ui:489` | figure | home | Pixels with y down to NDC with y up, and the scale and translate formula |
| `editor-ui:490` | figure | home | The buffer ring's states: free, written, pending, free again when the query is done; growth to 8 sets, then a wait |
| `editor-ui:624` | rule | home | Draw textures through `UI::TextureImage`: sRGB, grayscale and normal maps look wrong as stored |
| `editor-ui:632` | rule | home | User textures outlive the frame's draw data; binding sets are kept 8 frames |
| `editor-ui:634` | rule | home | Never identify draw callbacks by function address |
| `editor-ui:636` | rule | home | A key release is the key its press was queued as; modifiers are queued before keys |
| `editor-ui:666` | hands-on | home | Trace one frame with breakpoints in `ImGuiModule::OnRenderUI`, `EditorLayer::OnImGuiRender` and `ImGuiRenderer::Render` |
| `editor-ui:667` | hands-on | home | Compute the push constants of a 1600x900 display by hand and check them against the code |
| `editor-ui:678` | hands-on | home | Write a toy renderer backend in a tiny program of its own, from `ImGuiRenderer::Render`'s logic |
| `editor-ui:713` | term | home | Draw list, draw command and draw data (ImGui's meaning; the renderer's draw lists are another) |
| `editor-ui:715` | term | home | Clip rectangle and scissor |
| `editor-ui:785` | term | home | `ImGuiTextureDisplay` and its four modes |
| `editor-ui:790` | term | home | Dynamic textures (ImGui 1.92) |
| `new:2` | not-done | home | Input-method composition in game UI: committed text arrives, the text being composed and the candidate window are not shown; the editor's ImGui text fields take composed text and, on Windows, ImGui places the candidate list. Evidence: `Strata/src/Strata/Input/Input.h:146-149`; `grep -i preedit Strata/vendor/glfw/include/GLFW/glfw3.h` finds nothing (GLFW 3.4 has no preedit API); `Strata/src/Strata/ImGui/ImGuiPlatform.h:25-26` |
| `new:1` | feature | use | ImGui's core only is compiled: the backends are Strata's (`Strata/vendor/CMakeLists.txt:89-90`) |
| `editor-ui:37` | feature | link | The layer rebuilds the style for the UI scale (`editor-ui/ui-scale`) |
| `editor-ui:98` | feature | link | `UI::TextureImage`, the kit widget that adds the display callback |
| `editor-ui:786-789` | term | use | Binding set, event query, frames in flight and push constants, as the `gpu` pages define them |
| `editor-ui:791` | term | use | NVRHI, as `gpu/vulkan-nvrhi` defines it |
| `audio-input:191` | feature | home | `ImGuiPlatform` takes its input from the window's events; the editor's UI does not read `Input` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| ImGui's frame, draw data, IDs and items | `editor-ui/imgui` | must |
| Engine services and engine modules: dependencies, `OnInit`, the frame hooks | `core/engine-modules` | must |
| Windows, events and layers; overlays see events first; the content scale event | `core/windows-events` | must |
| Pipelines and binding: the pipeline cache, binding layouts and sets, registers, push constants | `gpu/binding` | must |
| Resources, lifetimes and deferred release; event queries | `gpu/resources-lifetimes` | must |
| How a GPU draws a frame; frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Strata's clip space and NDC (+Y up) | `gpu/coordinates` | must |
| Shaders in Slang, registered with `strata_add_shaders` | `gpu/shaders` | must |
| Linear and sRGB values and the sRGB transfer function | `basics/color` | must |
| Keys as the keyboard layout names them; per-frame input state | `input/devices-state` | must |
| Cursor modes: Normal, Hidden, Locked | `input/mouse-cursor` | must |
| Two-channel normal maps with Z reconstructed | `light/material-data` | helps |
| GPU stages and `GPUPassTimer` | `gpu/readback-timing` | helps |
| How a program is linked (identical functions may be folded) | `basics/build` | helps |

## `editor-ui/ui-scale` — Pixels, points and UI scale

**Covers.** How the editor's UI keeps its size on every display. The problem and how engines solve it: displays differ
in density; the system reports a content scale; macOS and Wayland measure windows in points with a framebuffer twice as
large, Windows and X11 in pixels; one approach scales at draw time, another lays out in points and rasterizes fonts for
the framebuffer. Strata lays out in window units and scales the style. The map is a diagram: the content scale event →
`ImGuiLayer::ToUIScale`, which divides out the points factor → times the person's factor (Preferences ▸ Interface,
through `EditorHost`) or replaced by `--ui-scale` → clamped to [0.5, 4] → `ApplyStyle`, which builds the style from
ImGui's unscaled defaults, lets the style callback (the theme) scale it, and sets `FontScaleDpi`. In play the game gets
the display's UI scale (the override, or the content scale less the points factor) without the person's factor, which
sizes the editor and not the game. The content scale is `core/windows-events`' word: the page says it in one sentence
and links it.

The real code: `ToUIScale`, the factor and the clamp, and `ApplyStyle`; the theme's even base sizes, so that 150% and
200% give whole pixels; the platform backend's display size and framebuffer scale, set each frame. The rules: sizes are
multiples of the font size, and the style is built from unscaled defaults every time, because scaling a scaled style
compounds. A picture shows the same layout at 100% and at 200%. At the end the reader can predict the UI scale on a
given display and keep a new widget crisp at any scale.

**Leaves out.**

- The theme's colors, the type scale and the fonts → `editor-ui/design-system`
- The Preferences dialog and its Interface page → `editor-ui/settings-windows`
- Every command-line option of the editor → `reference/editor`
- Sizes and scale in game UI (the canvas scale) → `ui/layout`

**Fit.** `over`: about 4,300 words against M (3,000). One concept, three excerpts, two figures, two rules and the three
exercises (`new:29`) do not fit M. Propose L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:37-38` | feature | home | The UI scale (content scale less the points factor, times the person's factor or the override, clamped to [0.5, 4], fonts by `FontScaleDpi`) and the style callback that receives ImGui's dark style unscaled |
| `editor-ui:326` | concept | home | Pixels, points and the UI scale: densities, content scale, points against pixels, the two approaches, Strata's, the rule of font-relative sizes, scaling twice and fixed widths as pitfalls |
| `editor-ui:431` | code | home | `Strata/src/Strata/ImGui/ImGuiLayer.cpp:169-232`: `ToUIScale` (169-177), the override, the factor and the clamp, and `ApplyStyle` from unscaled defaults (217-232) |
| `new:3` | code | home | `StrataEditor/src/UI/Theme.cpp:173-234`: the base sizes, all even or zero, so `ScaleAllSizes` gives whole pixels at 150% and 200%; hairlines of one pixel |
| `new:4` | code | home | `Strata/src/Strata/ImGui/ImGuiPlatform.cpp:186-204`: the display size and the framebuffer scale (pixels per window unit) set each frame, and delta time with its first-frame and minimum steps |
| `new:28` | feature | home | In play the editor gives the game the display's UI scale: the `--ui-scale` override, or the content scale less the points factor, never the person's interface factor, which sizes the editor and not the game; a game's canvases in the Game view keep the size a player's display gives them (critic-editor-ui-2, about 80 words, after the factor). Evidence: `StrataEditor/src/EditorLayer.cpp:636-638`; `Strata/src/Strata/ImGui/ImGuiLayer.h:68-71`; `StrataEditor/src/EditorHost.h:50-52`; `StrataEditor/src/Editor/EditorGameWindow.h:37-39` |
| `editor-ui:492` | figure | home | The UI scale computation from content scale to `ScaleAllSizes` and `FontScaleDpi` |
| `editor-ui:545` | figure | home | The default layout at `--ui-scale 2` beside 100% |
| `editor-ui:592` | rule | home | Sizes relative to the font, no fixed pixels above 16 |
| `editor-ui:631` | rule | home | Build the style from unscaled defaults every time |
| `editor-ui:722-725` | term | home | Points and pixels; UI scale; `FontScaleDpi` |
| `new:29` | hands-on | home | Exercises (D27): the UI scale predicted for three displays, Windows at a content scale of 1.5 with Interface at 125%, a Retina Mac at 2 with 100%, and any display with `--ui-scale 5` (Basic, predict); a breakpoint in `ImGuiLayer::ToUIScale` while the window moves to a display of another density, its window and framebuffer sizes read (Medium, trace); a scratch widget with a width of 200 fixed pixels in a panel made relative to the font and run at `--ui-scale 1` and `2`, then put back to watch the scan "Sizes scale with the font" fail (Hard, done: a patch). Evidence: `Strata/src/Strata/ImGui/ImGuiLayer.cpp:169-177`; `Strata/src/Strata/ImGui/ImGuiLayer.h:78-79` (the clamp to [0.5, 4]); `StrataTests/src/Editor/EditorUISourceTests.cpp:516-529` |
| `editor-ui:721` | term | use | Content scale and DPI, homed on `core/windows-events` with `gameui:624` (R31, D33): the page says the word in one sentence and links it |
| `editor-ui:54` | feature | use | `--ui-scale` among the options that matter to the UI |
| `editor-ui:62` | feature | use | `ApplyTheme` as the style callback, whose colors are `editor-ui/design-system`'s |
| `editor-ui:232` | feature | link | Preferences ▸ Interface sets the factor (`editor-ui/settings-windows`) |
| `editor-ui:258` | feature | link | The source scan "Sizes scale with the font" (`editor-ui/ui-testing`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Window size, framebuffer size and the content scale event | `core/windows-events` | must |
| ImGui's style and its push and pop | `editor-ui/imgui` | must |
| The ImGui layer, its style callback and the platform backend | `editor-ui/imgui-backends` | must |
| User settings sections (preferences) | `world/projects-settings` | helps |

## `editor-ui/design-system` — The design system: theme, fonts, icons

**Covers.** The editor's look as a system that many people and agents keep consistent. The problem and how engines
solve it: raw colors in code drift apart; a design system names its colors (tokens), gives them meanings (semantic
colors), fixes a type scale and an icon set, and enforces them by mechanism. The map: the Bedrock palette's 16 tokens →
`ThemeColors`, the meanings (accent, levels, axes, play states, text, surfaces) → `ApplyTheme`'s role table → every
`ImGuiCol_` (a diagram), with the axis colors that reappear in the gizmo and in vector fields. The contract: colors
only from tokens; text only through the editor's fonts, with icons as text; UTF-8 encoded once.

The real code: the role table with its `static_assert`, so an ImGui upgrade that adds a color slot fails the build, and
`ApplyTheme`; text rendering for tools: ImGui's own font atlas (not the engine's `FontAtlasCache`), Inter and JetBrains
Mono, Lucide merged into Unicode's Private Use Area with excluded ranges, an offset and a minimum advance (a diagram of
the atlas); the CJK fallback, read from system fonts on an I/O job and merged between frames, and the glyph generation
that invalidates measured widths; the trust boundary: the atlas reads only the compiled-in fonts and the system's
fallback fonts, never a project's font file, which is why it may skip the engine's font validation (`gpu/text`). Then
the type scale (12, 14, 17, 24) and `UI::PushFont`; `Icons.h`, generated from the font's code points by
`GenerateIconHeader.py`; entity and asset-type icons; the brand mark drawn as vectors, and the window's icon, the mark
at nine sizes so that no system stretches a smaller image; the fonts and the notices compiled into the editor, with the
fonts' licenses. The page states the entry of "What Strata does not do": editor themes other than Bedrock. Pictures:
ImGui's default style beside Bedrock, and a CJK project name. At the end the reader can add a theme meaning, use an
icon, and watch the source scan fail on a hex color.

**Leaves out.**

- How the engine shapes and draws game text, and its glyph atlas → `gpu/text`
- The UI scale the theme's sizes are multiplied by → `editor-ui/ui-scale`
- The widgets built on the tokens → `editor-ui/widget-kit`
- The source scans as tests → `editor-ui/ui-testing`
- Third-party licenses and notices in general → `engineering/third-party`
- How `strata_embed_file` and the committed generators work → `engineering/generated-code`

**Fit.** `fits`: about 5,300 words against L (5,000). Two concepts from zero, three excerpts, four figures and three
rules take the most; the window's icon, the trust boundary and the one theme take a few sentences each, and the scans
are only named here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:50` | feature | home | The fonts and `ThirdPartyNotices.md` compiled in with `strata_embed_file`: the editor reads no font file |
| `editor-ui:60-69` | feature | home | The Bedrock palette, `ThemeColors`, `ApplyTheme`, the token list for tests, `EditorFonts` and the type scale, the CJK fallback, `Icons.h`, entity icons, asset-type icons and names, the brand mark |
| `editor-ui:334` | concept | home | A design system for tools: tokens against semantic colors, a type scale, an icon set, rules enforced by mechanism; "just this once" hex colors |
| `editor-ui:339` | concept | home | Text rendering for tools: merged fonts, icons in the Private Use Area, excluded ranges, fallback scripts loaded off the main thread, the fallback glyph; icons in the monospace font, UTF-8 encoded twice, fonts loaded in a frame |
| `editor-ui:439` | code | home | `StrataEditor/src/UI/Theme.cpp:92-171`: the role table of pointers to members and its `static_assert` over `ImGuiCol_COUNT`; with `ApplyTheme` at 253-270 |
| `editor-ui:440` | code | home | `StrataEditor/src/UI/EditorFonts.cpp:77-97`: a text font with the icon range excluded, and Lucide merged in with an offset and a minimum advance |
| `editor-ui:441` | code | home | `StrataEditor/src/UI/EditorFonts.cpp:131-197`: the fallback fonts read once on an I/O job and merged between frames behind the editor's glyphs; the glyph generation |
| `editor-ui:494` | figure | home | Tokens → meanings → `ImGuiCol_` roles, and where the axis colors reappear |
| `editor-ui:496` | figure | home | The font atlas: Inter with Lucide and the CJK fallback, SemiBold the same, the monospace font without icons |
| `editor-ui:546` | figure | home | ImGui's default dark style (Help ▸ ImGui Demo with `--imgui-demo`) beside Bedrock |
| `editor-ui:582` | figure | home | A CJK project name drawn through the fallback fonts |
| `editor-ui:588` | rule | home | Colors only from theme tokens, enforced by the `static_assert` and the source scan |
| `editor-ui:596` | rule | home | Text through the editor's fonts, never ImGui's built-in font; icons are text, so swatches are drawn as rectangles |
| `editor-ui:598` | rule | home | UTF-8 encoded once (a "·" pasted through a Latin-1 tool turns into "Â·") |
| `editor-ui:668` | hands-on | home | Add a theme meaning and use it; then put a hex color in a panel and watch `Editor.UI.Source` fail |
| `editor-ui:717-720` | term | home | Fallback glyph (the word glyph is `gpu/text`'s, `render-core:762`, and the page links it); Private Use Area; merge mode; icon font |
| `editor-ui:727-729` | term | home | Theme and Bedrock; token, palette and semantic color; type scale |
| `editor-ui:793-794` | term | home | Inter, JetBrains Mono and Lucide; CJK |
| `new:5` | feature | home | The editor's fonts and their licenses: Inter 4.1 and JetBrains Mono 2.304 under the SIL Open Font License 1.1, Lucide 1.47.0 under ISC (icons from Feather also MIT), committed in `StrataEditor/Resources/Fonts` and compiled in. Evidence: `ThirdPartyNotices.md:34-38`; `StrataEditor/CMakeLists.txt:58-62` |
| `new:30` | not-done | home | Editor themes other than Bedrock: the editor has one palette, installed by one style callback, and no preference chooses a theme; the Roadmap leaves theme variants for later. Evidence: `StrataEditor/src/UI/Theme.h:10`, `:86-92` (the one palette and `ApplyTheme`); `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:985-993` ("rebinding editor shortcuts and theme variants", left for later); `grep -rn "Editor.Theme" StrataEditor/src` finds nothing |
| `new:31` | feature | home | The editor window's icon: the strata mark as raw RGBA8 images at nine sizes from 16 to 64 pixels, the small and large icons of Windows at 100 to 200% display scaling, so the system never stretches a smaller image, and a 256-pixel PNG for macOS's Dock, decoded at start; embedded by the editor's build and drawn by `Tools/GenerateBrandAssets.py` (critic-editor-ui-9, about 60 words, with the brand mark). Evidence: `StrataEditor/src/EditorIcon.h:14-26`, `:33-37`; `StrataEditor/src/EditorApplication.cpp:47-60`; `Tools/GenerateBrandAssets.py:1-21` |
| `new:32` | rule | home | The editor's ImGui atlas reads only the fonts compiled into the editor and the system's fallback fonts, never a project's font file: that is why ImGui's own rasterizer may read them without `FontValidation`, which guards the engine's text; the page links `gpu/text`'s validation (critic-editor-ui-10, about 50 words, in the text-rendering section). Evidence: `StrataEditor/src/UI/EditorFonts.cpp:69-75` (the only `AddFontFromMemoryTTF` call in `StrataEditor/src`), `:131-152` (the fallback read from `Platform::FindFallbackFontFiles`); `AGENTS.md:412`; `Docs/DeveloperGuide.md:6204` |
| `new:33` | hands-on | home | Trace it yourself (D27): a search for `ImGuiCol_Button` in `Theme.cpp` leads to its row of the role table and the palette token it reads; a breakpoint in `ApplyTheme` then shows the colors written from the tokens, and the call made again by `ImGuiLayer::ApplyStyle` when the UI scale changes. Evidence: `StrataEditor/src/UI/Theme.cpp:92-171` (the role table; `ImGuiCol_Button` at 124), `:253-257`; `Strata/src/Strata/ImGui/ImGuiLayer.cpp:217-232` |
| `editor-ui:38` | feature | use | The style callback through which `ApplyTheme` receives the style and the scale |
| `editor-ui:716` | term | use | Font atlas, as `gpu/text` defines it; the editor's atlas is ImGui's own |
| `editor-ui:258` | feature | link | The source scans that enforce the rules (`editor-ui/ui-testing`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Text: fonts, glyphs, the glyph atlas and font validation | `gpu/text` | must |
| Color values, sRGB and alpha | `basics/color` | must |
| Unicode code points and UTF-8 | `basics/bytes` | must |
| Jobs on I/O threads and results taken on the main thread | `core/jobs` | must |
| The UI scale and the style callback | `editor-ui/ui-scale` | must |
| `constexpr` | `basics/cpp-modern` | helps |
| `static_assert` (the role table's check over `ImGuiCol_COUNT`) | `basics/cpp-generic` | helps |
| Embedded files and committed generators | `engineering/generated-code` | helps |

## `editor-ui/widget-kit` — The widget kit

**Covers.** How to write custom widgets in an immediate-mode library, on Strata's kit. The problem: ImGui's own widgets
do not carry the editor's look, sizes and test hooks, yet a custom widget must still behave as an ImGui item. The
anatomy comes first (a diagram), on the kit's button: reserve an `InvisibleButton` for hit testing and navigation, read
hovered and held, draw with the window's draw list in theme colors, keep an active state vivid while disabled, render
the nav cursor, show the tooltip, record the rectangle in the item probe. The toy is a toggle button of about 40 lines.
Then layout that depends on its own result: the chip strip measures its chips in one frame, decides in its destructor
which chips become icons and where rows wrap, and the next frame draws them (a diagram over two frames, and the Scene
view's toolbar wide and narrow). Then the item probe: one hash-map write per widget and frame, in every build
configuration, keyed by id, with ids recorded twice flagged.

The catalogue follows in one table: button styles, icon and toolbar buttons, chips and toggle chips, pills, banners,
search fields, selection colors, section headers and headings, cards and entry cards, modals and dialog buttons, action
and link buttons, text fields, copyable code, elision, the legend, `TextureImage`, cancelling a drag with Escape; and the
helpers `TextFormat`, `Markdown` and the native file dialogs (nfd: blocking, main thread). The rules: controls come
from the kit; chips never take focus; costly tooltips are written only while due; an active `InputText` keeps its own
copy, so text replaced from outside needs a reload. A zoomed picture shows the kit. At the end the reader can write a
new kit widget with probe keys.

**Leaves out.**

- Clicking widgets in tests through the probe → `editor-ui/ui-testing`
- The status bar's pills and their compact texts → `editor-ui/status`
- The Scene view's chips and what each does → `editor-ui/scene-view`
- Asking the person in a modal, and the re-ask rule → `editor-ui/shell`
- Texture display modes, which `TextureImage` sets → `editor-ui/imgui-backends`

**Fit.** `fits`: about 4,900 words against L (5,000). The concept of writing custom widgets and the three excerpts carry
the teaching; the catalogue is one table, not a section per widget.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:73-103` | feature | home | The kit's promise (sized from the font, colored from the theme, recorded in the probe) and every widget and helper of `UI/Widgets.h`, the item probe, `TextFormat`, `Markdown` and `FileDialogs` |
| `editor-ui:345` | concept | home | Writing custom widgets: reserve an item, read its states, draw, nav cursor, tooltip, probe; layout decided from the previous frame; `BeginDisabled` fading what must stay vivid, chips that steal focus |
| `editor-ui:442` | code | home | `StrataEditor/src/UI/Widgets.cpp:62-122`: the anatomy of a kit widget (`DrawButton`) |
| `editor-ui:443` | code | home | `StrataEditor/src/UI/Widgets.cpp:218-279`: the chip strip decided in its destructor and drawn by the next frame |
| `editor-ui:444` | code | home | `StrataEditor/src/UI/ItemProbe.cpp:25-52`: one hash-map write per widget and frame, duplicates flagged, found only in the latest frame |
| `editor-ui:498` | figure | home | The anatomy of a kit widget: the item's rectangle, background, icon, label, nav cursor, tooltip, probe entry |
| `editor-ui:499` | figure | home | The chip strip over two frames: widths measured, `FirstIcon` and `RowStarts` decided, then drawn |
| `editor-ui:547` | figure | home | A zoomed crop of the kit: toolbar buttons in their styles, chips in their states, pills, a section header, cards, the progress bar, a legend |
| `editor-ui:564` | figure | home | The Scene view's toolbar wide (labels) and narrow (icons, wrapped rows), to show the chip strip |
| `editor-ui:600` | rule | home | Controls from the kit, each recorded in the probe |
| `editor-ui:616` | rule | home | Chips never take focus (`ImGuiButtonFlags_NoFocus`) |
| `editor-ui:622` | rule | home | Write costly tooltips only while due (`UI::IsTooltipDue`) |
| `editor-ui:646` | rule | home | An active `InputText` keeps its own copy of the text (`SearchField`'s reload) |
| `editor-ui:669` | hands-on | home | Write a kit widget (a segmented toggle) with probe keys and a harness test that clicks it |
| `editor-ui:730-731` | term | home | Widget kit; `InvisibleButton` |
| `editor-ui:742` | term | home | Item probe |
| `editor-ui:749-752` | term | home | Pill; chip; chip strip; banner, card, entry card and section header |
| `editor-ui:792` | term | home | nfd, the native file picker library |
| `new:34` | hands-on | home | Trace it yourself (D27): a breakpoint in `ItemProbe::RecordRect` while the Scene view's toolbar draws shows one write per widget and frame, the rectangle of the last item, and the flag set when an id is recorded twice in one frame; a search for `ImGuiButtonFlags_NoFocus` then finds the chips. Evidence: `StrataEditor/src/UI/ItemProbe.cpp:25-52`; `StrataEditor/src/UI/Widgets.cpp:138` |
| `editor-ui:624` | rule | link | Why UI code draws textures through `TextureImage` (`editor-ui/imgui-backends`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| ImGui's items, IDs, hovered and active, keyboard navigation | `editor-ui/imgui` | must |
| ImGui's draw lists | `editor-ui/imgui-backends` | must |
| The theme's tokens and meanings, the type scale, icons as text | `editor-ui/design-system` | must |
| Texture display modes | `editor-ui/imgui-backends` | must |
| Hash maps and what they cost | `basics/data-structures` | helps |
| UTF-8 (eliding text by characters) | `basics/bytes` | helps |

## `editor-ui/shell` — The editor shell: host, layer, docking and panels

**Covers.** The editor window for the people who change it. It opens with the anatomy of the whole editor, an
annotated picture of the default layout (the tour for game makers is `make/editor-tour`'s). The job and the map (the
architecture stack): `EditorApplication` installs the theme, the fonts and the layout file and gives `EditorLayer` an
`EditorHost`, its only way to the application; `EditorLayer` is the `EditorShell` that panels may ask (dialogs, the
unsaved-changes question, panels, facts about the editor); `EditorPanelRegistry` owns the panels. The problem and how
engines solve it is one paragraph that links `editor-ui/immediate-mode`, then panel architecture and dependency
inversion: a registry of descriptors with lifecycle hooks, and the UI as a client of commands. The contract: panels never
call `ImGui::Begin`; every change goes through a command with `CommandOrigin { CommandSource::UI }`; nothing changes the
scene while its rows are drawn (deferred actions); scripted runs never write the person's layout; a new default panel
bumps the layout version. The toy is a registry of panels in about 50 lines.

The real code in frame order: `EditorLayer::OnImGuiRender` (a diagram of one frame); the panel interface and descriptor
(a diagram of a panel's life); drawing the panels, with focus requests retried for up to 4 frames and deferred behind a
modal, and tabs shown without taking focus; the `[StrataPanels]` sections of `imgui.ini`; the default layout built from
proportions with font-size minimums, its version and `DockNewToolPanels` (a diagram); the dock space host and the status
bar window; the menu bar and the main toolbar; the window title, `--screenshot`, files dropped on the window, the
window's close, `editor.showPanel` and `editor.showDialog`. Then asking the person, the home of that concept: the
unsaved-changes question and its relatives, the re-ask when the undo version moved, and `DrawDiscardQuestion` drawn
inside other modals because ImGui keeps one popup per level (a diagram and a picture). The page states two entries of
"What Strata does not do": panels torn out into windows of their own, and editor extensions written by a game project.
At the end the reader can trace a click from a menu item to the command it runs.

**Leaves out.**

- The status bar's pills and the toasts → `editor-ui/status`
- The launcher panel and the dialogs → `editor-ui/launcher-dialogs`
- Shortcuts and their routing → `editor-ui/game-view`
- Saves off the main thread, the unsaved-changes guard and `AfterSaves` → `editor/saving`
- The tour of the editor for game makers → `make/editor-tour`
- Every panel, menu item and option in tables → `reference/editor`
- Writing a panel step by step → `editor-ui/tutorial-panel`
- The split of the editor's core from its UI → `editor/program`

**Fit.** `fits`: about 7,845 words against XL (8,000). Four concepts, five excerpts, seven figures and eight rules take
the most; the two absences and the three exercises (`new:35`) fit beside them.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:51-54` | feature | home | `EditorApplication`'s set-up (theme, fonts, CJK read, `--ui-scale`, `EditorLayout.ini` unless `--layout` or `--frames`), `EditorHost`, `EditorShell`, the options that matter to the UI |
| `editor-ui:109-115` | feature | home | `EditorLayer`, the UI's frame, the dock space host and the status bar window, the default layout and `c_LayoutVersion`, `DockNewToolPanels`, the menu bar, the main toolbar |
| `editor-ui:120-123` | feature | home | The unsaved-changes question and its relatives; the window's close and files dropped on it; `editor.showPanel` and `editor.showDialog`; the window title, `--screenshot`, command-script progress and the startup time |
| `editor-ui:129-136` | feature | home | The panel registry: the panel interface, the descriptor and its validation, the panel context, window names, open states in `imgui.ini`, `Focus` against `ShowTab` and `SelectTab`, `GetShownWindowRect`, the built-in panels in drawing order |
| `editor-ui:351` | concept | home | Docking and layout persistence: dock nodes, ini sections, a default layout from proportions, a version that replaces old layouts; a new panel shipped without a version bump |
| `editor-ui:356` | concept | home | Panel architecture and dependency inversion: lifecycle hooks, `EditorShell` and `EditorHost`, the UI in tests with fakes; a panel that calls `ImGui::Begin` |
| `editor-ui:361` | concept | home | The UI as a client of commands: undo, automation and the journal see one operation; deferred actions; a panel writing a component directly |
| `editor-ui:412` | concept | home | Modality and data safety in UI: ask before replacing a scene, ask again if it changed, draw nested questions inside the modal |
| `editor-ui:445` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.h:60-93`: the panel interface and its descriptor as a contract |
| `editor-ui:446` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.cpp:168-246`: drawing panels: focus deferred behind modals and retried, tabs selected without focus, `OnHidden` |
| `editor-ui:447` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.cpp:330-424`: a settings handler that adds `[StrataPanels][Open]` and `[StrataPanels][Layout]` to `imgui.ini` |
| `editor-ui:448` | code | home | `StrataEditor/src/EditorLayer.cpp:726-795`: the editor's UI frame top to bottom, and where the toasts go |
| `editor-ui:449` | code | home | `StrataEditor/src/EditorLayer.cpp:1320-1360`: the default dock layout from proportions with font-size minimums |
| `editor-ui:476` | figure | home | The architecture stack from `EditorApplication` to the panels, the core underneath, the engine's ImGui module, and the Tooling boundary |
| `editor-ui:482` | figure | home | One editor frame from window events to the executed command list |
| `editor-ui:501` | figure | home | A panel's life: registered, open or closed, `OnUpdate`, `OnImGuiRender`, `OnHidden`, focus retried and deferred |
| `editor-ui:504` | figure | home | The default dock layout with its proportions and the layout-version rule |
| `editor-ui:531` | figure | home | The unsaved-changes question: saves in flight, modified, the modal, the re-ask, the action with `force: true` |
| `editor-ui:544` | figure | home | The whole editor in its default layout on a copy of a sample, 1600x900 at 100%, annotated with the panels' names |
| `editor-ui:581` | figure | home | The unsaved-changes question (Save, Don't Save, Cancel) |
| `editor-ui:594` | rule | home | Panels never call `ImGui::Begin`: the registry gives the View menu, open states, stable window names, focus and `OnHidden` |
| `editor-ui:602` | rule | home | Every change through a command (or `SceneEditTransaction` and `SetPropertyWithUndo`); panels never write, move or remove files |
| `editor-ui:605` | rule | home | UI commands carry `CommandOrigin { CommandSource::UI }` |
| `editor-ui:612` | rule | home | Do not change the scene while iterating its rows: schedule the change |
| `editor-ui:619` | rule | home | A modal that asks while open draws the question inside itself |
| `editor-ui:621` | rule | home | Focusing a panel while a modal waits is deferred |
| `editor-ui:651` | rule | home | Scripted runs never overwrite the person's layout |
| `editor-ui:653` | rule | home | Bump `c_LayoutVersion` when the default layout gains a panel open by default |
| `editor-ui:710` | term | home | DockBuilder |
| `editor-ui:712` | term | home | Settings handler |
| `editor-ui:744` | term | home | Panel, panel registry and descriptor |
| `editor-ui:746` | term | home | Editor shell (`EditorShell`) |
| `new:35` | hands-on | home | Exercises (D27): what a person sees on the next start after `c_LayoutVersion` goes from 5 to 6, the saved arrangement replaced by the default layout and the open states reset (Basic, predict); File ▸ Save Scene followed with breakpoints to `scene.save`, run by the command runner with the UI's origin, and its entry found in the Activity panel (Medium, trace); a question asked from inside an open modal, drawn first beside it and then inside it, to see why only the second shows (Hard, predict then run: a patch). Evidence: `StrataEditor/src/EditorLayer.h:132`; `StrataEditor/src/EditorLayer.cpp:1409-1423` (the saved version against `c_LayoutVersion`), `:1493-1495` (the menu item), `:1155-1171` (`scene.save` with `CommandSource::UI`) |
| `editor-ui:747` | term | link | Editor host (`EditorHost`), homed on `editor/program` beside `editor-core:650` (duplicates.md:45) |
| `new:6` | not-done | home | Panels torn out into windows of their own: the editor has one main viewport and no platform windows of ImGui's own; the Roadmap lists ImGui multi-viewports under Later. Evidence: `Strata/src/Strata/ImGui/ImGuiPlatform.h:18-21`; `Docs/Roadmap.md:1715` (under "Later", line 1637) |
| `new:7` | not-done | home | Editor extensions written by a game project: only the editor registers panels, in `EditorLayer::RegisterBuiltinPanels`. Evidence: `StrataEditor/src/EditorLayer.cpp:337-370` (the `Register` call at 350) |
| `editor-ui:49` | feature | use | The two libraries, as `editor/program` teaches them: this page draws what `StrataEditorUI` holds |
| `editor-ui:284` | concept | use | What an editor is, from `editor/program` |
| `editor-ui:116` | feature | link | The status bar's pills (`editor-ui/status`) |
| `editor-core:138` | feature | home | `EditorShell::RequestDiscardChanges`, `RequestReleaseProject` and `RequestQuit`: they ask the person and pass `force` only for what was asked |
| `editor-core:516` | figure | home | The unsaved-changes dialog after an edit and File ▸ Open Scene: one picture with `editor-ui:581` |
| `editor-core:567` | rule | home | The UI passes `force` only for what the person was asked about: the question comes again when the undo version moved |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an editor is; the core and UI libraries; `EditorContext`; the editor's frame order | `editor/program` | must |
| Commands are the API: the registry, running a command, command origins and kinds | `editor/commands` | must |
| Commands that take frames and the command runner | `editor/deferred-commands` | must |
| No silent data loss: the unsaved-changes guard, `force`, releasing a project, settings writers | `editor/saving` | must |
| Undo and redo: the undo stack and its version | `editor/undo` | must |
| Docking, `imgui.ini`, popups and modals | `editor-ui/imgui` | must |
| The kit's modals, toolbar buttons and dialog buttons | `editor-ui/widget-kit` | must |
| Interfaces and virtual functions | `basics/cpp-classes` | must |
| `std::function` and lambdas | `basics/cpp-generic` | must |
| The activity journal and command sources | `editor/journal` | helps |
| Command scripts (`--commands`) | `editor/command-scripts` | helps |
| Importing a file into the project | `assets/importing` | helps |

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

## `editor-ui/inspectors` — Inspectors from reflection

**Covers.** How one generic panel edits every component. The problem and how engines solve it: hundreds of properties
must not each need UI code; one generic inspector driven by metadata, hand-written editors per type, and custom
drawers as escape hatches (Unity, Unreal and Godot each have them); how the metadata is obtained is
`world/reflection`'s comparison, which the page links. The map is a diagram:
`ComponentInfo::Properties` → groups by section, made once per type → `DrawPropertyRow` → a property drawer or
`DrawPropertyWidget` → `SetPropertyWithUndo` → the undo stack, merged until the edit finishes. The contract: every edit
goes through the undo helpers; prefab commands are scheduled after drawing; a property that another property can switch
off gets an inactive reason. The toy is a generic inspector over a list of names, types, getters and setters.

The real code: the groups and rows (labels with their overridden mark and inactive reason, mixed values across
entities shown as "--", writes of only the changed axes, rotations through the angles the widget showed, the merge
broken when an edit finishes); the type switch from `PropertyType` to widgets; the material editor (a drag previews in
the loaded material, its release saves with one undo step and one write). Then the rest of the Inspector: the component
sections and their header, component drawers (the UI rect's anchor grid) and property drawers (the TAA preset), the
component menu (Reset, Copy and Paste Values as clipboard JSON, Remove), Add Component and missing-requirement notices,
the prefab bar and overrides, the scene's settings when nothing is selected with live lines (sun shadow maps), script
fields and the animator's state, the tab switch for a new inspection target. Then the Asset tab: header and actions, an
import-settings draft with Apply and Revert, the material section, texture previews through the display modes, models,
audio waveforms, animation views, the import outcome. Examples avoid the subjects of wave 8. Pictures: one entity and
three with mixed values, a prefab instance with its Overrides menu, an inactive property with its tooltip, the TAA
preset drawer and Add Component, the Asset tab. At the end the reader can register a property drawer and add an
inactive reason, as `capstone/build` does.

**Leaves out.**

- How properties, sections and inactive reasons are registered → `world/reflection`
- How prefab overrides are kept exact → `editor/prefab-instances`
- Undo steps, merging and `SetPropertyWithUndo` → `editor/undo`
- Settings pages drawn with the same widgets → `editor-ui/settings-windows`
- Edit-mode poses and animation previews → `animation/editor`
- Every component and its properties → `reference/components`

**Fit.** `fits`: about 7,425 words against XL (8,000). The entity inspector takes most of the page; the Asset tab, with
the material editor's excerpt, takes about 1,700 words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:145-146` | feature | home | The Inspector panel and the Asset tab: what each shows |
| `editor-ui:175-190` | feature | home | Component sections, property rows, mixed values and partial writes, undo merging, the widgets by type, the property table, inactive reasons, drawers, the component menu and Add Component, the prefab bar and overrides, the material section and editor, scene settings, live lines, script fields and the animator, the target switch |
| `editor-ui:376` | concept | home | Reflection-driven inspectors: three ways to build inspectors (one generic inspector from metadata, hand-written editors per type, custom drawers as escape hatches), with a link to `world/reflection` for how the metadata is obtained (critic-editor-ui-4); metadata driving a generic widget, multi-edit, undo merging, override marks; one undo step per drag frame, Euler angles read back from a quaternion |
| `editor-ui:458` | code | home | `StrataEditor/src/Panels/InspectorPanel.cpp:915-1035`: the central algorithm: groups by section once per type, a drawer or the generic widget, mixed values, per-axis writes, the merge broken when the edit finishes |
| `editor-ui:459` | code | home | `StrataEditor/src/UI/PropertyWidgets.cpp:892-960`: the switch from `PropertyType` to widgets, with the special cases of `UInt` |
| `new:9` | code | home | `StrataEditor/src/UI/MaterialEditor.cpp:96-128`: a dragged value previews in the loaded material, and its release saves once and breaks the merge |
| `editor-ui:511` | figure | home | The generated inspector pipeline from `ComponentRegistry` to the undo stack |
| `editor-ui:555` | figure | home | The Inspector with one entity (axis labels in the axis colors, sections), then with three entities and mixed values |
| `editor-ui:557` | figure | home | A prefab instance: the prefab bar, overridden labels with the accent bar, the Overrides menu open |
| `editor-ui:558` | figure | home | An inactive property with its tooltip (Bloom's threshold while Bloom is off), and the directional light's "Shadow maps" line |
| `editor-ui:560` | figure | home | The Post Process TAA preset drawer; the Add Component popup with its filter |
| `editor-ui:561` | figure | home | The Asset tab: a material being edited; a normal map shown through the NormalXY display beside a raw view; an audio clip's waveform |
| `editor-ui:655` | rule | home | A property another property can switch off gets an `InactiveReason`: the Inspector's side, which disables the row and shows the reason (the registration and its rule, `scene-ecs:198` and `:531`, are `world/reflection`'s) |
| `editor-ui:674` | hands-on | home | Register a `PropertyDrawer` (a light's color temperature as a gradient bar) |
| `editor-ui:675` | hands-on | home | Add an inactive reason next to a property's registration and see the Inspector disable it |
| `new:37` | hands-on | home | Trace it yourself (D27): a breakpoint at the Inspector's write while a light's intensity is dragged shows one `SetPropertyWithUndo` call per changed frame merged into one undo step, and `BreakMerge` when the edit finishes; with three lights selected the same drag takes the branch that writes several entities. Evidence: `StrataEditor/src/Panels/InspectorPanel.cpp:1010-1034` |
| `editor-ui:754` | term | home | Property table |
| `editor-ui:757-758` | term | home | Section (property); mixed value |
| `editor-ui:761` | term | home | Component drawer and property drawer |
| `editor-ui:760` | term | use | Inactive reason, one glossary entry with `scene-ecs:654`, homed on `world/reflection` (R31, D11; world-q2): the page uses the word where the Inspector disables a row and shows its reason |
| `editor-ui:755-756` | term | use | Reflection; `PropertyInfo` and `ComponentInfo`, as `world/reflection` defines them |
| `editor-ui:759` | term | use | Override (prefab), as `world/prefabs` defines it |
| `editor-ui:762` | term | use | Undo merge, as `editor/undo` defines it |
| `editor-ui:41` | feature | use | The texture display modes the Asset tab's previews use |
| `assets:215` | feature | home | The Asset tab's import settings drawn from `GetSettingsProperties`, with inactive reasons; files dropped on the Content Browser import (`editor-ui/lists` shows the drop target) |
| `audio-input:99` | feature | home | `AudioPreview`: one preview source outside any scene, a waveform of minimum and maximum per column computed on a job (none beyond 600 s), drawn in the Asset tab |
| `audio-input:471` | figure | home | The Asset tab's audio preview with its waveform and Play: one picture with `editor-ui:561` |
| `audio-input:650` | term | home | Waveform (preview) |
| `gameui:216-217` | feature | home | The UI Rect drawer: the anchor grid with its 16 presets, a rect kept in place while its anchors change, margins along stretched axes, pixels at the game's screen, prefab overrides |
| `gameui:482` | figure | home | The UI Rect drawer with the anchor preset grid open and margin rows on a stretched element |
| `scene-ecs:198` | feature | use | `ComponentRegistry::SetInactiveReason<T>(property, fn)`, homed on `world/reflection` (R31, D11): this page shows how the Inspector disables the property and shows the reason |
| `scene-ecs:474` | figure | home | A camera's Inspector in Orthographic: the perspective fields disabled with their reason, and Depth Of Field off greying Aperture |
| `scene-ecs:479` | figure | home | A prefab instance's Inspector: one picture with `editor-ui:557` |
| `scene-ecs:531` | rule | use | A property another turns off gets an `InactiveReason`, homed on `world/reflection` (R31, D11): beside `editor-ui:655`, the Inspector's side of it |
| `scene-ecs:654` | term | link | Inactive reason, homed on `world/reflection` (R31, D11) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reflection: `ComponentRegistry`, `PropertyInfo`, ranges, flags, sections, inactive reasons | `world/reflection` | must |
| Undo and redo: `SetPropertyWithUndo`, merging and breaking the merge | `editor/undo` | must |
| Prefab instances, overrides, apply and revert | `editor/prefab-instances` | must |
| Rotations: Euler angles and quaternions | `basics/math-rotations` | must |
| `std::variant` and `std::optional` | `basics/cpp-modern` | must |
| Texture display modes | `editor-ui/imgui-backends` | must |
| The kit and panels | `editor-ui/shell` | must |
| Strata's material model | `light/materials` | helps |
| Texture import settings and usages | `assets/texture-cooking` | helps |
| The quality rows (the sun's shadow maps line) | `image/quality-settings` | helps |
| Script fields | `scripting/script-system` | helps |
| Edit-mode poses and previews | `animation/editor` | helps |
| Audio clips | `audio/clips-voices-sources` | helps |
| Rects, anchors and layout (the UI Rect drawer) | `ui/layout` | helps |

## `editor-ui/scene-view` — The Scene view

**Covers.** The Scene view as a 3D view inside a UI, home of picking and gizmos. The problem and how engines solve it:
render the view offscreen at the panel's pixel size and show it as an image item; pick by CPU rays against bounds or by
a GPU buffer of entity IDs read back at the pixel; move objects with screen-space handles. The map is a diagram: the
toolbar strip with its chips above the image (never over the game's HUD), the image rendered by the view's renderer, the
overlays drawn over it. The contract: ImGuizmo starts a drag only while no item is hovered; a gizmo drag is one undo
step computed from its start state; picking never stalls. The toy is a viewport panel of about 60 lines: an image, a
pick request and a drag.

The real code: the image and how it cooperates with ImGuizmo (no item under the gizmo, no window move); camera drags
fed from the panel (first-frame and non-finite deltas dropped, the cursor locked while flying; the camera's math is
`editor/camera-viewport`'s); asynchronous picking with a one-pixel readback, applied frames later only if the same scene
still shows, with a timeout (a diagram), UI elements picked first, Ctrl and Shift; the gizmo drag with `TransformDrag`
(one undo step, locals recomputed under parents, none while playing, snapping inverted by Ctrl, ended when the selection
changes; a diagram). ImGuizmo is linked only by the editor's UI library, and themed with the axis colors. Then the chips
(camera settings, grid, outline, gizmos, stats, preview lighting, game UI, the debug view and its legend with counts per
color, quality, the game camera on F8, the animation preview), the agent chip after an automation command (shown while
an agent is connected and for a minute after, a click opening its entry in the Activity panel) and the flash that
outlines the entities the command touched for 0.6 s (their bounds taken once per command, the fade timed by the clock
so the panel stops animating), the drop of an asset and its ghost (the panel's side), the scene-load overlay, and
canvas mode for screen-space UI canvases (a world-space canvas is edited in the scene), which drives the screen view
that `gpu/debug-drawing` teaches. Pictures: the three gizmos, the LOD debug view with its legend and the stats, the agent
chip with the flash, the drop ghost, canvas mode. At the end the reader can follow a click on the image to the
selection, and a gizmo drag to its undo step.

**Leaves out.**

- Orbit, pan, dolly and fly, `FitBounds`, per-scene cameras → `editor/camera-viewport`
- How placement decides where a dropped asset lands → `editor/placement`
- The list of debug views and what each colors → `gpu/debugging`
- Readback without stalls in general → `gpu/readback-timing`
- Overlays, the selection outline and gizmo shapes → `gpu/debug-drawing`
- The Game view and who owns input → `editor-ui/game-view`
- The Scene view's shortcuts → `editor-ui/game-view`
- Game UI rects and anchors, which canvas mode edits → `ui/layout`

**Fit.** `fits`: about 7,375 words against XL (8,000). Three concepts, four excerpts, three diagrams and five pictures
take the most; the camera's mathematics stays on `editor/camera-viewport`, and the agent chip and flash take one
paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:142` | feature | home | The Scene view panel (`ViewportPanel`) |
| `editor-ui:155` | feature | home | Canvas mode: a UI canvas laid out in 2D at its reference aspect, outlines, handles, zoom and pan |
| `editor-ui:196-199` | feature | home | Render to texture at the panel's pixel size; the toolbar strip; the chips; the debug view's legend |
| `editor-ui:201-202` | feature | home | Asynchronous picking; the gizmo with `TransformDrag` |
| `editor-ui:204-206` | feature | home | The agent chip and flash; the drop and its ghost (the panel's side); the scene-load overlay card |
| `editor-ui:384` | concept | home | The viewport: render to texture inside a UI, input only while hovered or focused, overlays over the image; first-frame and non-finite deltas, dragging the window instead of the camera |
| `editor-ui:390` | concept | home | Picking: CPU rays or an ID buffer; Strata's asynchronous read and stale-result rejection; blocking readbacks, picking against a resized image |
| `editor-ui:394` | concept | home | Transform gizmos: handles, world and local axes, snapping, a primary, locals under parents, one undo step from the start state; items stealing the click, a drag outliving its entity |
| `editor-ui:460` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:149-210`: cooperating with ImGuizmo: no item under the gizmo, no window move |
| `editor-ui:461` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:867-930`: camera drags from the panel; the camera's own math (`EditorCamera.cpp`) is `editor/camera-viewport`'s |
| `editor-ui:462` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:936-994`: the gizmo drag's life with `TransformDrag`, snapping inverted by Ctrl, cancelling |
| `editor-ui:463` | code | home | `StrataEditor/src/Editor/EditorViewport.cpp:415-454`: asynchronous picking with a readback, a timeout and stale-result rejection |
| `editor-ui:514` | figure | home | The viewport's composition: toolbar strip and agent chip, the offscreen image, overlays, toasts in the view's corner |
| `editor-ui:518` | figure | home | The pick's timeline: click at frame N, readback ready at N+k, the scene check, `ApplyPick`, the timeout |
| `editor-ui:520` | figure | home | The gizmo drag's sequence from `Manipulate` to one undo step |
| `editor-ui:563` | figure | home | The translate, rotate and scale gizmos on a selected crate, World against Local |
| `editor-ui:565` | figure | home | The LOD debug view and its legend (`viewport.setSettings {debugView: "lod"}`), and the stats overlay |
| `editor-ui:567` | figure | home | The agent chip and the accent outline flash after an automation command |
| `editor-ui:569` | figure | home | Canvas mode on a UI canvas |
| `editor-ui:638` | rule | home | ImGuizmo starts a drag only while no item is hovered: the image becomes a `Dummy` over the gizmo |
| `editor-ui:640` | rule | home | A gizmo drag is one undo step computed from its start state |
| `editor-ui:642` | rule | home | Picking never stalls, and a late result never selects in another scene |
| `editor-ui:765` | term | home | Render target and render to texture, inside a UI |
| `editor-ui:769-772` | term | home | Gizmo and ImGuizmo; world and local space; snapping (of gizmo drags); picking (the entity-ID buffer, `render-core:772`, is `gpu/frame-tour`'s word and readback, `render-core:758`, `gpu/readback-timing`'s: the page links both) |
| `editor-ui:774` | term | home | The debug view's legend, with its counts per color (the word debug view is `gpu/debugging`'s, `render-scene:182`, and the page links it) |
| `new:38` | hands-on | home | Exercises (D27): a gizmo drag with snapping on and Ctrl held, what the crate's position does and how many undo steps the drag leaves (Basic, predict then run); a click on the image followed with breakpoints in `EditorViewport::RequestPick` and `UpdatePicking`, the frames counted until the readback is ready and the scene check read (Medium, trace); why the pick reads back the entity-ID buffer instead of casting a CPU ray against bounds, for a scene of skinned characters and foliage (Hard, design). Evidence: `StrataEditor/src/Editor/EditorViewport.cpp:415-454`; `StrataEditor/src/Panels/ViewportPanel.cpp:936-994` |
| `editor-ui:776` | term | home | Game camera (pilot) |
| `new:8` | feature | home | ImGuizmo is linked privately by `StrataEditorUI` only, beside nfd: only the viewport draws gizmos, and no game or core library links it. Evidence: `StrataEditor/CMakeLists.txt:53-54`; `Strata/vendor/CMakeLists.txt:102-105` |
| `editor-ui:200` | feature | use | The editor camera, as `editor/camera-viewport` teaches it |
| `editor-ui:516` | figure | link | The camera's geometry, drawn on `editor/camera-viewport` |
| `editor-ui:568` | figure | use | The drop's ghost, the picture `editor/placement` holds |
| `editor-ui:766` | term | use | Editor camera; orbit, pan, dolly and fly |
| `editor-ui:763` | term | use | Viewport, Scene view and Game view: "Game view" is one glossary entry with `editor-core:694`, homed on `editor/play-mode`; "Scene view" and "viewport" are homed on this page, where the glossary step splits the item (R46) |
| `editor-ui:203` | feature | link | The Scene view's shortcuts (`editor-ui/game-view`) |
| `editor-core:121` | feature | home | `TransformDrag`: a gizmo drag as one undo step with its merge key, its values computed from the drag's start |
| `gameui:159` | feature | home | How canvas mode drives the screen view to zoom and pan; the struct `SceneScreenView` is taught on `gpu/debug-drawing`, which the page links (critic-gameui-18) |
| `gameui:218-219` | feature | home | The Game UI chip, a click selecting the topmost UI element; canvas mode: the letterboxed canvas, outlines and handles, drag and resize with snapping, zoom about the pointer, pan, F and Home; the 2D canvas mode edits screen-space canvases only: a selected world-space canvas is edited in the scene, and the mode shows the scene's first screen-space canvas instead (critic-gameui-8, about 40 words; `StrataEditor/src/Editor/CanvasEdit.cpp:110-125`, `StrataEditor/src/Editor/CanvasEdit.h:52-54`) |
| `gameui:243` | feature | home | The editor's game-UI tests (`EditorGameUITests`, `EditorUICommandTests`, `GPUCanvasEditTests`) in "How it is tested" |
| `gameui:483` | figure | home | Canvas mode with outlines and handles on the selection, zoomed in with F: one picture with `editor-ui:569` |
| `gameui:502` | figure | home | The Scene view with the Game UI chip off and on (screen canvases hidden, world canvases still drawn) |
| `gameui:684` | term | home | Canvas mode (2D) |
| `gameui:685` | term | link | Screen view, homed on `gpu/debug-drawing` beside `SceneScreenView`, the page that teaches it (critic-gameui-18) |
| `render-core:773` | term | home | Picking: one glossary entry with `editor-ui:772` |
| `automation:183-184` | feature | home | The agent chip ("Agent: entity.create · 3 s ago" while a client is connected or 60 s after, its text made again once a second at most, a click showing the entry in the Activity panel) and the flash (the bounds of at most 64 entities taken once per command, accent rectangles fading over 0.6 s, timed by the clock): taught with `editor-ui:204` |
| `automation:579` | figure | home | The agent chip and the flash during its 0.6 s, or frames of the fade: one picture with `editor-ui:567` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor camera, per-scene cameras, viewport settings | `editor/camera-viewport` | must |
| Placing content: `asset.place`, the drop and its ghost | `editor/placement` | must |
| Readback and GPU timing: non-blocking readback | `gpu/readback-timing` | must |
| A frame of the scene renderer, the entity-ID buffer | `gpu/frame-tour` | must |
| Overlay passes and debug drawing | `gpu/debug-drawing` | must |
| Matrices, transforms and spaces | `basics/math-matrices` | must |
| The transform contract: world and local transforms under parents | `world/scene-graph` | must |
| Undo and redo: one step per drag | `editor/undo` | must |
| The kit's chips and the chip strip | `editor-ui/widget-kit` | must |
| Panels | `editor-ui/shell` | must |
| Play and Simulate (no undo while playing) | `editor/play-mode` | helps |
| The activity journal (the agent chip's last command) | `editor/journal` | helps |
| The debug views | `gpu/debugging` | helps |
| Rects, anchors and layout of game UI | `ui/layout` | helps |

## `editor-ui/game-view` — The Game view, shortcuts and who owns the keyboard

**Covers.** Who owns the keyboard and the mouse: the game or the editor. The problem and how engines solve it: the
editor's camera against the game's; aspect ratios, letterboxing and fixed resolutions; mouse positions in the game's
pixels; a person who types in the Inspector while the game reads keys; a locked cursor that must never trap the person;
global against focus-scoped shortcuts. The map is two diagrams: who gets the keyboard and the mouse in play mode, and
how a key chord is routed. The contract: the game gets input only while the Game view is shown, focused and playing;
Shift+F1 always leaves; selection shortcuts are focus-routed, and global ones check for a modal and for the game.

The real code: the Game view's input ownership (the `Input` module enabled only then, `Input::SetViewport` with the
rendered resolution, a locked cursor setting `ImGuiConfigFlags_NoMouse`, Shift+F1 and the hint shown for a few
seconds); Play bringing the Game tab forward with the keyboard and Stop bringing the Scene view back; the global
shortcuts (`ImGuiInputFlags_RouteGlobal`, nothing behind a modal, Ctrl+P always, undo and redo through their commands,
the edit shortcuts only while the running game does not take them) and the focus-routed selection shortcuts of the
Hierarchy and the Scene view. Then the resolution menu (free, aspect ratios letterboxed, fixed sizes scaled to fit, the
game's own request) with targets freed while hidden and the "no camera" message as the game shows it; the panel keys;
Edit-menu actions sharing code with the shortcuts, the clipboard as JSON text; the Scene view's keys (Q, W, E, R, F,
Home, F8, F2); on macOS, Cmd in place of Ctrl, because ImGui swaps the two. One sentence links the game's UI scale in
play (the display's, without the person's factor: `editor-ui/ui-scale`). The page states the entry of "What Strata
does not do": the editor's shortcuts cannot be rebound. Pictures: a letterboxed 16:9, a fixed 1920x1080 scaled to
fit, the "no camera" notice, the locked-cursor hint. At the end the reader can add a key to the Scene view that
respects the guards.

**Leaves out.**

- Play and Simulate, the running copy and the game shell → `editor/play-mode`
- Pausing and stepping a game → `editor/stepping`
- Cursor modes and the input module's state → `input/mouse-cursor`
- UI hit tests in the game's pixels → `ui/input`
- The full shortcut table, generated → `reference/editor`
- The Scene view's tools that the keys select → `editor-ui/scene-view`

**Fit.** `fits`: about 5,490 words against L (5,000). Two concepts, three excerpts, two diagrams and three exercises
take the most; the shortcut table is short here because `reference/editor` generates the full one.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:143` | feature | home | The Game view panel |
| `editor-ui:203` | feature | home | The Scene view's keys: Q, W, E, R, F, Home, F8, the selection shortcuts and F2 |
| `editor-ui:207-208` | feature | home | The Game view: the primary camera with its HUD, the resolution menu, letterboxing, targets freed while hidden, the "no camera" message; game input ownership |
| `editor-ui:238-241` | feature | home | Global shortcuts and their guards; focus-routed selection shortcuts; panel keys; Edit-menu actions sharing code with shortcuts, the clipboard as JSON |
| `editor-ui:399` | concept | home | The Scene view against the Game view, and who owns input; the game reading input while the person types |
| `editor-ui:403` | concept | home | Keyboard shortcuts and focus: global against focused, text fields keep their keys, modals block, play filters edits, layouts and Cmd; Delete in the Content Browser deleting entities |
| `editor-ui:450` | code | home | `StrataEditor/src/EditorLayer.cpp:951-985`: global shortcuts and their guards; with the focus-routed ones in `StrataEditor/src/UI/EditorActions.cpp:318-338` |
| `editor-ui:464` | code | home | `StrataEditor/src/Panels/GameViewPanel.cpp:241-281`: input ownership between the editor and the game, the cursor lock and `NoMouse` |
| `new:10` | code | home | `StrataEditor/src/EditorLayer.cpp:1243-1275`: Play brings the Game tab forward (taking the keyboard, so the game gets its input) and Stop brings the Scene view back |
| `editor-ui:522` | figure | home | Input ownership in play mode: Game view focused and playing, cursor locked, Shift+F1, chips that never take focus |
| `editor-ui:524` | figure | home | Shortcut routing: global (modal check, Ctrl+P, `AcceptsEditShortcuts`), focused (Hierarchy, Scene view), text fields |
| `editor-ui:570` | figure | home | The Game view in play: 16:9 letterboxed in a tall panel; 1920x1080 scaled to fit; the "no camera" notice; the locked-cursor hint |
| `editor-ui:614` | rule | home | Selection shortcuts are focus-routed; global shortcuts check modals and `AcceptsEditShortcuts` |
| `editor-ui:644` | rule | home | The game gets input only while the Game view is focused in play; Shift+F1 always leaves |
| `editor-ui:676` | hands-on | home | Add a Scene view key (G toggles the grid) that follows the routing guards of `ViewportPanel::HandleShortcuts` |
| `editor-ui:734` | term | home | Shortcut routing (`RouteGlobal`, `RouteFocused`) |
| `editor-ui:775` | term | home | Letterboxing |
| `editor-ui:883` | open | home | Settled at the pin: on macOS Cmd is the shortcut modifier, because ImGui swaps Cmd and Ctrl under `ConfigMacOSXBehaviors`, which it sets on Apple builds (`Strata/vendor/imgui/imgui.cpp:1731-1735`); the platform backend passes keys as they are, and `StrataTests/src/ImGui/ImGuiPlatformTests.cpp:147-170` pins it |
| `new:39` | not-done | home | Rebinding the editor's shortcuts: the chords are written in the code as literal keys of `ImGui::Shortcut`, and no preference holds them; the Roadmap leaves rebinding editor shortcuts for later. Evidence: `StrataEditor/src/EditorLayer.cpp:951-985`; `StrataEditor/src/UI/EditorActions.cpp:318-338` (the focus-routed ones); `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:985-993` ("rebinding editor shortcuts and theme variants", left for later) |
| `new:40` | hands-on | home | Trace it yourself (D27): a breakpoint in `GameViewPanel::UpdateGameInput` during play shows `Input` enabled only while the Game view is shown, focused and playing, `ImGuiConfigFlags_NoMouse` set when the game locks the cursor, and Shift+F1 taking the focus away. Evidence: `StrataEditor/src/Panels/GameViewPanel.cpp:241-281` |
| `editor-ui:777` | term | use | Cursor lock, as `input/mouse-cursor` defines it |
| `editor-ui:616` | rule | link | Chips never take focus (`editor-ui/widget-kit`) |
| `new:28` | feature | link | The game's UI scale in play, without the person's factor (`editor-ui/ui-scale`), in one sentence |
| `audio-input:177` | feature | home | The Game view's focus: only the focused Game view in play feeds `Input`; `SetViewport`; the locked cursor; Shift+F1: taught with `editor-ui:208` |
| `audio-input:479` | figure | home | The Game view with a locked cursor and its Shift+F1 and Ctrl+P hint: one picture with `editor-ui:570` |
| `editor-core:228-229` | feature | home | `SetGameInputActive`, with edit shortcuts off meanwhile; `GameViewMode` and `ComputeGameViewFrame` |
| `editor-core:613` | hands-on | home | Set 4:3 and a fixed 1280x720, and check that a HUD button is hit where it is drawn |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Play and Simulate: the running copy, the game shell, edits while playing | `editor/play-mode` | must |
| Input ownership in the engine: the enabled flag, typed text, keyboard and pointer capture | `input/devices-state` | must |
| The mouse, the cursor modes and the game view's viewport | `input/mouse-cursor` | must |
| The Scene view's panel and its tools | `editor-ui/scene-view` | must |
| ImGui's focus and key chords | `editor-ui/imgui` | must |
| Running commands (`edit.undo`) and the clipboard of `entity.copy` | `editor/commands` | must |
| Pausing and stepping a game | `editor/stepping` | helps |
| UI input in the game's pixels | `ui/input` | helps |

## `editor-ui/status` — Status bar, toasts and idle throttling

**Covers.** Telling the person what happens without interrupting them, and redrawing only as often as needed. The
problem and how engines solve it: status bars with pills that lead somewhere, toasts that never take focus, errors
counted as unread, against modal error dialogs for routine failures; an immediate-mode UI redraws every frame, so
editors idle at a low rate when nothing happens and run uncapped while someone waits by frames. The map: what each
pill reads, where its click leads, and the notifications' model in the core and their drawing in the UI. The contract:
toasts never take focus and cost nothing while empty; the frame pill shows work time, not the frame interval; a panel
that animates without input reports `IsAnimating`; frames that run work someone waits for by frames are never capped.

The real code: the status bar's pills (play state; the frame's milliseconds, frames per second and jobs; the assets with
the pool closest to its budget in Sulfur or Cinnabar; saving; bodies without collision; automation, with its texts
made again only when the clients' version or the port changes and a tooltip of the clients and the requests; scripts;
input holds that a click releases; unread errors), each opening its panel, with compact texts decided from the previous
frame's widths and a margin of two font sizes against flicker (a diagram); idle throttling as a policy (`TrackInput`,
`IsBusy`, `RunsUncapped`, the `Editor.FrameRate` preferences and their defaults, the floor of 5 fps because the frame
pacer sleeps through input, the lift while steps are pending; a diagram); the frame statistics, where work time is
averaged over 60 frames without waits (the term frame work time is `core/frame-loop`'s, linked). Then notifications: the
core's model (at most four, merged when identical or of one group, lifetimes by level, replaced in place, kept while
hovered, versioned; a diagram), the outcome of the person's commands without double toasts, and the drawing: one window
that never takes focus, at the bottom right of the shown Scene or Game view, with its actions (Show in Activity, Show
Asset, Show Problems, Show in Console, Recover). Pictures: the status bar full and compact, the errors pill, the assets
pill in Sulfur, the automation pill with no agent and with a named agent, its tooltip open; toasts with their buttons.
At the end the reader can add a status pill with a compact text, and make an animated panel keep its frame rate.

**Leaves out.**

- The panels the pills open → `editor-ui/instrument-panels`
- Measuring the frame, stages and Tracy → `core/profiling`
- The `editor.status` command → `automation/agents`
- Status providers, the sections of `editor.status` → `editor/commands`
- The recovery offer that a toast leads to → `editor/recovery`
- Holds of simulated input → `editor/stepping`
- The automation server, its clients and their names → `automation/rpc-server`

**Fit.** `fits`: about 6,360 words against L (5,000). Two concepts, three excerpts, five figures and four rules take the
most, with the pills taught in one table; the page stands about 140 words below L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:116-119` | feature | home | The status bar's pills; compact texts with hysteresis; idle throttling and `Editor.FrameRate`, with the floor of 5 fps and its reason: the frame pacer sleeps without waking on input, so an idle editor answers the first input up to one idle interval late, 33 ms at 30 fps and 100 ms at 10 fps unfocused (critic-editor-ui-5, about 60 words; `StrataEditor/src/Editor/EditorFrameRate.h:30-32`); the frame statistics passed to panels |
| `editor-ui:248-250` | feature | home | `EditorNotifications`; `NotifyCommandOutcome` and `Announced`; `UI::DrawNotifications` |
| `editor-ui:406` | concept | home | Feedback without interruption: pills that lead somewhere, toasts without focus, unread errors, compact texts; modal errors for routine failures |
| `editor-ui:408` | concept | home | Power: idle throttling, uncapped work, work time against the capped interval; a frozen animation |
| `editor-ui:451` | code | home | `StrataEditor/src/EditorLayer.cpp:842-919`: idle throttling as a policy: when it applies, busy detection, uncapped work, the caps |
| `editor-ui:452` | code | home | `StrataEditor/src/EditorLayer.cpp:1872-1944`: the status bar with hysteresis between full and compact texts, and `StatusPillText` |
| `new:11` | code | home | `StrataEditor/src/UI/Notifications.cpp:69-97`: nothing done while empty; one window that takes neither focus nor navigation, brought to the front unless a modal is open; actions on a copy of what shows |
| `editor-ui:528` | figure | home | Status bar hysteresis: the available width, the full width, the margin of two font sizes |
| `editor-ui:526` | figure | home | The idle-throttling decision as a flowchart, with the lift while steps are pending |
| `editor-ui:529` | figure | home | A notification's life: posted and merged, shown, kept, replaced, dismissed or expired; at most four |
| `editor-ui:572` | figure | home | The status bar with full and compact texts (a narrow window at 150%), the errors pill, the assets pill in Sulfur |
| `editor-ui:573` | figure | home | Toasts stacked at the bottom right of the Scene view with their action buttons |
| `editor-ui:618` | rule | home | Toasts never take focus and cost nothing while empty |
| `editor-ui:626` | rule | home | Show work time, not the frame interval |
| `editor-ui:627` | rule | home | A panel that animates without input reports `IsAnimating` |
| `editor-ui:629` | rule | home | Frames that run work someone waits for by frames are never capped |
| `editor-ui:671` | hands-on | home | Add a status pill with a compact text that focuses a panel; test it at 150% in a narrow window |
| `editor-ui:677` | hands-on | home | Write a panel that animates, watch the idle throttle slow it, fix it with `IsAnimating` |
| `editor-ui:748` | term | home | Toast and notification |
| `editor-ui:778` | term | home | Idle throttling |
| `editor-ui:781` | term | home | Notification group |
| `new:41` | hands-on | home | Trace it yourself (D27): breakpoints in `EditorLayer::IsBusy` and `RunsUncapped` show what keeps the editor from idling (input within the idle delay, an agent's recent request, a panel that reports `IsAnimating`, a running or stepping game, assets loading, a pending pick) and what lifts the cap (pending steps, commands or automation requests), and `IsThrottlingEnabled` turning it all off for a command-script run. Evidence: `StrataEditor/src/EditorLayer.cpp:842-919` |
| `editor-ui:779` | term | link | Frame work time, homed on `core/frame-loop` beside `foundation:48` (duplicates.md:51) |
| `editor-ui:780` | term | use | Status provider, as `editor/commands` defines it (editor-q5) |
| `editor-ui:82` | feature | use | The kit's `Pill` and `CalcPillWidth` |
| `assets:514` | figure | home | The status bar's assets pill and the assets section of `editor.status`, as a text capture |
| `editor-core:46` | feature | home | The notifications' model and what feeds it: taught with `editor-ui:248` |
| `editor-core:738` | term | home | Notification and toast: one glossary entry with `editor-ui:748` |
| `automation:182` | feature | home | The automation pill: "port N · no agent", "Agent connected · <name>", "N agents connected" with their compact texts, "Automation off" and "Automation failed"; the tooltip of clients and request counts; the texts made again only when `GetClientsVersion` or the port changes: taught with `editor-ui:116` |
| `automation:577` | figure | home | The automation pill with no agent and with a named agent (`claude-code`), its tooltip open: one picture with `editor-ui:572` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Measuring the frame: frame time, work time, stages | `core/profiling` | must |
| Commands and their results; command origins | `editor/commands` | must |
| Panels, `Focus` and `GetShownWindowRect` | `editor-ui/shell` | must |
| The kit's pills and the chip strip's idea of deciding from the previous frame | `editor-ui/widget-kit` | must |
| The frame loop and its frame rate cap | `core/frame-loop` | helps |
| Residency, budgets and memory pools | `assets/residency` | helps |
| Physics capacity and bodies that wait | `physics/scale-streaming` | helps |
| Simulated input and its holds | `input/simulated` | helps |
| Pausing and stepping a game | `editor/stepping` | helps |
| Autosave and the recovery offer | `editor/recovery` | helps |
| The RPC server's clients, their names and its version counter | `automation/rpc-server` | helps |

## `editor-ui/launcher-dialogs` — Launcher and dialogs

**Covers.** The screens around the editing: the launcher and the dialogs. The job, then the problem in one paragraph
(a start screen and dialogs that never block a frame and never lose work). The map: the launcher is a panel of the
Launcher placement, drawn instead of the dock space while no project is open; the dialogs are drawn by `EditorLayer`
every frame and run commands. The contract: a dialog's action is a command; a dialog that replaces the scene asks
through `EditorShell` and asks again when the scene changed after the answer; no file is read in a frame. The toy is a
modal dialog of about 30 lines that runs one command.

The real code: the launcher's recent projects, read with their pictures on an I/O thread (a path out of reach can take
seconds) and applied only when the list did not change meanwhile; the project dialogs' answered version, and the
re-ask through `RequestReleaseProject`; the Export dialog's progress, Cancel and Hide (closing it leaves the export
running). Then each screen: the launcher (the hero band, New and Open Project, Open Sample, recent projects as picture
cards with search and a context menu, template and sample cards, "Connect an AI agent" with its command line to copy
and the automation server's state in four forms (ready on a port, agents connected, off, failed with its reason), the
footer with version, commit, GPU and startup time, errors shown on it, Continue without a project, File ▸ Show
Launcher); New Project and Open Sample (template cards, the name, a location remembered in `imgui.ini`); About Strata
(build, GPU, driver, startup, UI scale, Copy Details, the third-party notices drawn from Markdown); Export Game (the
fields of `project.export`, the result with Open Folder); Recover Unsaved Changes; the Delete asset confirmation that
lists what uses the asset; New Script (the External Editor page of Preferences is `editor-ui/settings-windows`').
Pictures: the launcher and the two project dialogs, taken with the recipe of `start/first-game`'s pictures; the agent
card in its four states; About and Export, the Export dialog from the one capture set it shares with
`assets/packs-export`. At the end the reader can name the command each button runs and say why a dialog asks again.

**Leaves out.**

- What projects, templates, samples and recent projects are → `editor/projects`
- The export's work and its state machine → `worlds/export`
- The recovery journal → `editor/recovery`
- Why a delete is refused and the trash → `editor/trash-references`
- Connecting an agent through MCP → `automation/mcp`
- The Preferences dialog → `editor-ui/settings-windows`
- The External Editor page → `editor-ui/settings-windows`
- Project pictures → `editor/thumbnails`

**Fit.** `fits`: about 5,725 words against L (5,000). Seven screens and three excerpts take the most; the launcher's and
the project dialogs' pictures follow the recipe of `start/first-game`, and the Export dialog's set is shared with
`assets/packs-export`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:154` | feature | home | The Welcome panel of the Launcher placement |
| `editor-ui:214-219` | feature | home | The launcher; New Project and Open Sample; About Strata; Export Game; Recover Unsaved Changes; the Delete asset confirmation |
| `new:12` | code | home | `StrataEditor/src/Panels/WelcomePanel.cpp:225-279`: the recent projects read on an I/O thread, one read at a time, applied only when the list did not change meanwhile |
| `new:13` | code | home | `StrataEditor/src/UI/ProjectDialogs.cpp:221-258`: the undo version and project-file writes noted when the person answered; a changed scene or a save in flight asks again over the dialog |
| `new:14` | code | home | `StrataEditor/src/UI/ExportDialog.cpp:186-215`: the dialog shows an export's progress whoever started it; Cancel runs `project.cancelExport`, Hide leaves it running |
| `editor-ui:580` | figure | home | About Strata; Export Game during an export: the Export dialog's pictures are one capture set with `assets:512` and `worlds-runtime:400`, made once (R34, D42) and first shown on `assets/packs-export`; this page's caption explains the dialog's code |
| `editor-ui:745` | term | home | Launcher |
| `new:42` | open | home | Check: A capture step that opens the launcher's card. The claim, read from the code and not run: the launcher and its "Connect an AI agent" card show only while no project is open, so a whole-editor figure, which opens a project copy, needs a `project.close` step (after which "the editor shows its launcher"); the card is drawn last in the launcher's one scrolling region, after the recent projects and the template and sample cards, so at 1600x900 it may stand below the region's edge, and the launcher's code sets no scroll position. The figure `automation:574` waits for the result (automation-q4). Evidence: `StrataEditor/src/EditorLayer.cpp:1069-1072`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:346-347`; `StrataEditor/src/Panels/WelcomePanel.cpp:461-497`; `grep -n SetScroll StrataEditor/src/Panels/WelcomePanel.cpp` finds nothing |
| `new:43` | hands-on | home | Exercises (D27): the command each button of New Project and Open Sample runs, found with a search for `project.create` and `project.openSample` in `ProjectDialogs.cpp` (Basic, trace); `editor.showDialog {dialog: "about"}` sent from a terminal to a running editor, then Copy Details pasted and read (Medium, command); Don't Save answered in New Project, an entity created with `entity.create` from a terminal while the dialog is open, then Create pressed, to see the question come again (Hard, predict then run). Evidence: `StrataEditor/src/UI/ProjectDialogs.cpp:221-228`, `:335`, `:415`; `StrataEditor/src/EditorLayer.cpp:233-243` |
| `editor-ui:549` | figure | use | The launcher with recent projects and their pictures, template and sample cards, "Connect an AI agent" and the footer: the figure recipe of `start/first-game` (`gamedev:438`), or a crop of what this page's code explains (start-q8) |
| `editor-ui:550` | figure | use | The New Project dialog; the Open Sample dialog: the figure recipe of `start/first-game` (`gamedev:439`) (start-q8) |
| `editor-ui:220` | feature | use | The New Script dialog, drawn by `EditorLayer` among the dialogs; the External Editor page of the same item is homed on `editor-ui/settings-windows` (critic-editor-ui-3) |
| `editor-ui:102` | feature | use | `Markdown`, which draws the notices in About |
| `editor-ui:90` | feature | use | The kit's modals |
| `editor-core:154` | feature | home | The Recover dialog opens itself for a crash's leftovers; toasts tell of discards |
| `worlds-runtime:168` | feature | home | The Export dialog: File ▸ Export Game and the toolbar's Export, the loading-scene choice, the identity summary, exports that agents started |
| `worlds-runtime:175-176` | feature | home | The launcher; the project dialogs and the remembered location (first `<home>/StrataProjects`) |
| `worlds-runtime:400` | figure | home | The Export dialog before, during and after: one capture set with `editor-ui:580` and `assets:512` (`assets/packs-export`), made once (R34, D42); the caption says what this page teaches |
| `worlds-runtime:405-406` | figure | home | The launcher; New Project with the basic3d template and the scene it makes: taken with the recipe of `start/first-game`'s pictures (`gamedev:438-439`, which `editor-ui:549-550` use; start-q8) |
| `worlds-runtime:566` | term | home | Launcher: one glossary entry with `editor-ui:745` |
| `automation:185` | feature | home | The "Connect an AI agent" card: the `claude mcp add strata -- <StrataCLI> mcp` line with its copy button (a warning in its place when StrataCLI is not next to the editor), and the server's state as a pill from `EditorAutomationState`: ready on port N, N agents connected, off, failed with its reason: taught with `editor-ui:214` |
| `automation:574` | figure | home | The card in its four states: ready on a port, one agent connected, off (`--no-automation`), failed (a taken `--automation-port`); its capture waits for the check of `new:42` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Launcher, templates and samples: the model, recent projects, `project.create`, `project.open`, `project.openSample` | `editor/projects` | must |
| Autosave and crash recovery | `editor/recovery` | must |
| The trash, references and refused deletes | `editor/trash-references` | must |
| The export as a whole: `GameExport`, its stages and options | `worlds/export` | must |
| Asking the person: modals, the re-ask rule, `DrawDiscardQuestion` | `editor-ui/shell` | must |
| Jobs on I/O threads | `core/jobs` | must |
| Project pictures | `editor/thumbnails` | helps |
| Script templates and the external editor | `editor/script-builds` | helps |
| The MCP server (`StrataCLI mcp`) | `automation/mcp` | helps |
| The editor's automation options: `--no-automation`, `--automation-port` | `automation/sessions` | helps |

## `editor-ui/settings-windows` — Settings windows from schemas

**Covers.** Settings pages generated from schemas. The problem and how engines solve it: settings sections registered
with fields must not each need a hand-written page, while complex sections still need their own. The map: the settings
registry's sections → `EditorSettingsPageRegistry` (custom pages by section id) → `SettingsBrowser` (pages by category,
with a search) inside the Project Settings panel and the Preferences dialog. The contract: every edit runs a command
(`project.setSettings`, `preferences.set`, or the project's own commands) with the UI's origin; pages draw from copies
refreshed when the values' version changes, never parsing per frame. The toy is a page generator of about 40 lines.

The real code: the generic page (fields drawn as properties through `SettingsFieldProperty`, the command run once when
an edit finishes, a stored value that is refused shown with its reason, Reset to Defaults); binding capture, which takes
the keyboard from ImGui with key owners, locks keys until they are released, ends on a timeout or when its owner stops
asking, and keeps the keyboard until every key is up. Then the pages: the Project Settings panel's Game page (start and
loading scenes, title, version, company, copyright, icon) and Export page (kept paths); Graphics Quality (preset chips,
rows by presets, an editable Custom column, memory at 1080p and 2160p, GPU time, the players' options banner and reset);
Collision Layers (names and the matrix); Input Actions with binding capture; the External Editor page, the fourth custom
page, registered for `Editor.ExternalEditor` (the command that opens sources, the program it starts, the code editors
found on the machine); the Preferences dialog, which works on the launcher too (External Editor, Interface, Frame Rate).
Pictures: Graphics Quality, the Collision Layers matrix, Input Actions listening; Preferences' Interface and Frame Rate
pages. At the end the reader can register a settings section and see its page appear, or write a custom page.

**Leaves out.**

- Settings sections, fields, versions and validation → `world/projects-settings`
- What each quality row does and costs, and the players' options → `image/quality-settings`
- The collision layers table and its filter bits → `physics/collision-layers`
- Players' bindings and capture inside the engine → `input/rebinding`
- Every section's fields and defaults → `reference/settings`
- The UI scale that Preferences ▸ Interface sets → `editor-ui/ui-scale`
- The idle frame rates that Preferences ▸ Frame Rate sets → `editor-ui/status`

**Fit.** `fits`: about 5,275 words against L (5,000). One concept, two excerpts and the four custom pages (Graphics
Quality, Collision Layers, Input Actions, External Editor) take the most, with four figures and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:153` | feature | home | The Project Settings panel (closed by default) |
| `editor-ui:226-232` | feature | home | `SettingsBrowser` and the page registry; the generic page; the Project Settings pages; Graphics Quality; Collision Layers; Input Actions and `BindingCapture`; the Preferences dialog |
| `editor-ui:220` | feature | home | The External Editor page (critic-editor-ui-3): a custom `SettingsPage` of the Preferences dialog for `Editor.ExternalEditor`, registered in the page registry, the fourth custom page beside Graphics Quality, Collision Layers and Input Actions: the command that opens sources (`script.setExternalEditor`), the program it starts or why it cannot, the code editors found on the machine, the `STRATA_EXTERNAL_EDITOR` override; the New Script dialog of the same item is drawn on `editor-ui/launcher-dialogs`. Evidence: `StrataEditor/src/UI/ScriptDialogs.h:42-47`; `StrataEditor/src/EditorLayer.cpp:146-149` |
| `editor-ui:419` | concept | home | Settings UIs from schemas: generated pages, custom pages for complex sections, edits as commands, copies refreshed by version |
| `new:15` | code | home | `StrataEditor/src/UI/SettingsPages.cpp:84-179`: the generic page: fields as properties, the command run once an edit finishes, values read again only when their version changes, the refused value's reason |
| `new:16` | code | home | `StrataEditor/src/UI/BindingCapture.cpp:138-165`: the capture's frame: an owner that stopped asking, the timeout, the keyboard held until every key is up; with the key owners set at 41-47 |
| `editor-ui:574` | figure | home | Project Settings: Graphics Quality, the Collision Layers matrix, Input Actions with a capture listening |
| `editor-ui:576` | figure | home | Preferences: the Interface and Frame Rate pages |
| `editor-ui:650` | rule | home | Settings pages draw from copies refreshed by version, never parsing per frame |
| `editor-ui:783` | term | home | Settings page and settings browser (the word settings section is `world/projects-settings`', `scene-ecs:687`, and the page links it) |
| `new:44` | hands-on | home | Exercises (D27): a simple settings section with a `bool` and a ranged `float` registered in a patch, its generic page found in Project Settings, an edit made and its `project.setSettings` entry read in the Activity panel (Medium, extend); a breakpoint in the generic page's `Apply` shows the command run once when an edit finishes and the values read again after it (Medium, trace); what the page shows when the project file holds a value the section's validation refuses (Hard, predict then run). Evidence: `Strata/src/Strata/Core/SettingsRegistry.h:120-122`; `StrataEditor/src/UI/SettingsPages.cpp:163-168` |
| `editor-ui:782` | term | use | Binding capture, as `input/rebinding` defines it |
| `editor-ui:179` | feature | use | `DrawPropertyWidget`, which the generic page draws fields with |
| `audio-input:181` | feature | home | The Input Actions page: maps, actions, kinds, dead zones, binding chips, composites part by part, capture with its 10 s timeout, "In play" markers, Reset Player Bindings |
| `audio-input:476-477` | figure | home | The Add binding popup building a 2D composite part by part; binding capture listening, with its countdown and Cancel |
| `scene-ecs:486` | figure | home | The Project Settings panel: the page list, the Timing page (a generic page) and the Collision Layers page (a custom page): with `editor-ui:574` |
| `scene-ecs:488` | figure | home | The Preferences dialog, to contrast user sections with project sections: with `editor-ui:576` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections: fields, versions, validation, simple and complex sections | `world/projects-settings` | must |
| Players' graphics options; presets and traits; the quality rows | `image/quality-settings` | must |
| Collision layers: the project's table and filter bits | `physics/collision-layers` | must |
| Players' bindings and binding capture in the engine | `input/rebinding` | must |
| Property widgets and the property table | `editor-ui/inspectors` | must |
| Commands (`project.setSettings`, `preferences.set`) | `editor/commands` | must |
| Input actions | `input/actions` | helps |
| ImGui's key ownership | `editor-ui/imgui` | helps |
| The external editor (`script.setExternalEditor`) | `editor/script-builds` | helps |

## `editor-ui/instrument-panels` — Instrument panels

**Covers.** The five panels that show the editor's machinery: what each shows and how each keeps its cost low. The job
and a one-paragraph problem: instruments that cost more than what they measure are useless. The map: each panel
collects in `OnUpdate`, also while it is closed, so the status bar can show its figure, and draws only while visible;
the Problems and Activity panels rebuild their rows when a version changes; the Streaming panel builds its table on a
job. The contract: idle frames compare numbers and draw clipped rows; big tables are built off the main thread. The toy
is a panel of about 40 lines whose rows are rebuilt only on a version change.

The real code: the Problems panel's idle check (one number and a short key compared) and its clipped table, with file
texts elided once per width; the Streaming panel's table built on a job and swapped in when done, at most every quarter
second; the Activity panel's rows rebuilt only when the journal's version or the filters change. Then each panel: the
Console (level filters, search, messages with a source reference that open the external editor, unread errors counted
for the status bar); Problems (the crash first, with its stack and without the SDK's internals, then the last build's
errors and warnings, a summary line, a double click that opens the source in the external editor, the Build button, and
a Play whose script build failed bringing the panel forward through a request counter that the UI compares every frame);
Activity (the journal as a table of summaries, each with an arrow that shows its raw parameters and result below it,
filters by text, source and whether it changed anything, a selected entry's JSON, Copy as script, Re-run, Undo to here);
Streaming (pools against budgets, loads, queues, the upload sparkline, the asset table, the Physics and World sections
with the cell map); Performance (600 frames of CPU and GPU timeline, spikes, the stage table, what bounds the frame,
pause and Space, Copy as JSON). Pictures: Activity with an entry's JSON, Problems after a failed build, the Console with
a source reference, the Performance timeline, the Streaming panel with the cell map. At the end the reader can read the
editor's state from its instruments, and write a panel whose idle frame costs almost nothing.

**Leaves out.**

- The frame profiler, its stages and Tracy → `core/profiling`
- The journal's model, origins and replays → `editor/journal`
- Building scripts and parsing diagnostics → `editor/script-builds`
- From an address to a file and line → `scripting/symbolization`
- Residency, budgets and pools → `assets/residency`
- The world's cells and the editor's world → `editor/worlds`
- The panels' perf tests → `editor-ui/ui-testing`

**Fit.** `fits`: about 5,375 words against L (5,000). Five panels and four excerpts take the most, with three exercises;
the panels share one contract, so each panel takes one section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:148-152` | feature | home | The Console, Problems, Streaming, Performance and Activity panels: what each shows |
| `new:17` | feature | home | The Problems panel's rows: the crash first (where it happened, on which entity, in which function), its stack frames with a source but without the SDK's `Strata::Detail::` thunks, then the build's diagnostics, and a summary line ("The scripts crashed in…", "Build N failed: …", "No script build in this session yet"). Evidence: `StrataEditor/src/Panels/ProblemsPanel.h:13-17`; `StrataEditor/src/Panels/ProblemsPanel.cpp:110-216` |
| `new:18` | feature | home | Opening a row's source: an absolute path, or the file found in the project, its script folder or the build folder; the File column relative to the project; the reason shown when there is no file. Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:37-77, 218-236` |
| `new:19` | code | home | `StrataEditor/src/Panels/ProblemsPanel.cpp:100-108`: an idle frame compares the last build's ID and the crash's key, and rebuilds nothing |
| `new:20` | code | home | `StrataEditor/src/Panels/ProblemsPanel.cpp:272-341`: a clipped table, the first rows recorded in the probe, the file texts elided once per width, a double click that opens the source |
| `new:21` | rule | home | A row that shows text the program does not control is an unlabeled item (`##Row`) with the text drawn after it: a compiler's message may hold `##`, which a label would cut. Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:295-296` |
| `new:22` | code | home | `StrataEditor/src/Panels/StreamingPanel.cpp:609-666`: the asset table rebuilt on a job at most every `c_TableRefreshSeconds`, one build at a time, swapped in when done |
| `new:23` | code | home | `StrataEditor/src/Panels/ActivityPanel.cpp:165-205`: rows rebuilt only when the journal's version or the filter key changed |
| `editor-ui:577` | figure | home | Activity with a selected entry's JSON and its buttons; Problems after a failed build; the Console with a clickable source reference |
| `editor-ui:579` | figure | home | The Performance panel's CPU and GPU timeline; the Streaming panel with the World section's cell map: the cell map is one capture set with `worlds-runtime:392` on `editor/worlds`, made once (R34, D42), and this page's caption says what the panel shows |
| `new:45` | feature | home | A Play that fails because its script build failed or its module did not load brings the Problems panel forward: `play.start` raises a request counter in the core, and the UI compares it every frame and focuses the panel, the core asking the UI without knowing it, the same pattern as the inspection version (critic-editor-ui-6, about 50 words). Evidence: `StrataEditor/src/Editor/Commands/PlayCommands.cpp:58-69`; `StrataEditor/src/Editor/EditorContext.h:607-609`; `StrataEditor/src/EditorLayer.cpp:746-757` |
| `new:46` | hands-on | home | Exercises (D27): a breakpoint in `ProblemsPanel::OnUpdate` shows an idle frame comparing the last build's ID and the crash's key and returning (Basic, trace); a script with a planted compile error built from the editor, its row double-clicked to open the source, then Play pressed to watch the panel come forward (Medium, editor task); a scratch panel of 10,000 rows rebuilt only when a version changes, measured idle against one rebuilt every frame (Hard, extend: a patch). Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:100-108`; `StrataEditor/src/Panels/ActivityPanel.cpp:165-170` |
| `editor-ui:190` | feature | link | The inspection target's tab switch, the counter pattern that `new:45` repeats (`editor-ui/inspectors`) |
| `editor-ui:169` | feature | use | The cached and clipped lists of these panels, taught on `editor-ui/lists` |
| `editor-ui:116` | feature | use | The status bar's pills that open these panels |
| `assets:213` | feature | home | The Streaming panel's pools, queue, uploads, prefetches and mip streaming, and its table's Mip column (resident and wanted) |
| `automation:176` | feature | home | The Activity panel as an agent's session shows in it: rows with summaries, raw parameters and result below an expanded row, filters, the details JSON, Copy as script, Re-run, Undo to here, rows rebuilt only when the journal's version or the filters change: taught with `editor-ui:152` and `new:23` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building scripts from the editor: diagnostics for the Problems panel, the external editor | `editor/script-builds` | must |
| The activity journal: origins and kinds, replays, Copy as script | `editor/journal` | must |
| Residency, pins and eviction; budgets and pools | `assets/residency` | must |
| Grids, cells and the streamer | `worlds/streamer` | must |
| Measuring the frame: the profiler and its stages | `core/profiling` | must |
| Lists that scale | `editor-ui/lists` | must |
| The status bar's pills | `editor-ui/status` | must |
| Jobs and handing results back | `core/jobs` | must |
| Crash containment and the crash that stops play | `scripting/crash-containment` | helps |
| GPU stages | `gpu/readback-timing` | helps |
| Physics capacity | `physics/scale-streaming` | helps |
| The log and its levels | `core/conventions` | helps |

## `editor-ui/ui-testing` — Testing a UI without a screen

**Covers.** Testing a UI without a window or a GPU. The problem and how engines solve it: tests that click by
coordinates break when a layout moves; UI tests drive a real UI library with injected input over frames, find widgets
by key, and turn rules a compiler cannot check into scans of the source; panels with huge data get perf budgets. The map
is a diagram: `FakeEditorHost` and an ImGui context with the editor's fonts and theme → `EditorLayer` or one panel →
the input queue → `ItemProbe` lookups. The contract: one harness at a time; widgets found by probe keys; the scans keep
empty allowlists. The toy is a harness of about 40 lines that clicks one button.

The real code: `ClickItem` over three frames (hover first, because ImGui decides hovering from the previous frame, then
press and release, because buttons act on the release); the `Editor.UI.Source` scans (colors only from the theme, sizes
that scale with the font, panels drawn through the registry, no built-in font, UTF-8 encoded once, panels that change
files only through commands); a panel perf test measured per frame, the 95th percentile and the frames that refresh a
table. Then the fake host and the harness editor, the suites of the area and what each pins, and where the panels'
budgets live (five rows, one of them provisional). At the end the reader can write a test that clicks a kit widget,
and add a scan rule with its self-test.

**Leaves out.**

- The test program: shards, labels, locks and helpers → `engineering/test-program`
- Perf tests in general: noise, budgets, the reference machine → `engineering/perf-lab`
- GPU tests and end-to-end tests of the editor → `engineering/test-kinds`
- Writing a panel and its test step by step → `editor-ui/tutorial-panel`
- Every measured budget → `reference/performance`

**Fit.** `fits`: about 4,255 words against L (5,000). One concept, three excerpts, the scans' rules and two exercises
take the most; room is left for a worked test of a panel.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:256-260` | feature | home | `ImGuiHarness`; `FakeEditorHost` and `HarnessEditor`; the `Editor.UI.Source` scans; the suites of the area; the panels' perf tests and the 100,000-entity idle test |
| `editor-ui:415` | concept | home | Testing a UI without a screen: a real context, injected input over frames, probe keys, lints over the source, perf budgets for panels; tests that click by coordinates |
| `editor-ui:465` | code | home | `StrataTests/src/Editor/ImGuiHarness.cpp:118-132`: clicking a widget: hover, press, release over three frames |
| `editor-ui:466` | code | home | `StrataTests/src/Editor/EditorUISourceTests.cpp:499-545`: lint rules as tests: colors, sizes, panels, fonts |
| `new:24` | code | home | `StrataTests/src/Editor/EditorPanelPerfTests.cpp:94-138`: the Streaming panel with 10,000 assets measured per frame against confirmed budgets |
| `editor-ui:533` | figure | home | The test harness: the fake host, the ImGui context and `EditorLayer`, the input queue, the probe lookup, `ClickItem` over three frames |
| `editor-ui:679` | hands-on | home | Add a source-scan rule to `EditorUISourceTests.cpp` with its self-test |
| `editor-ui:743` | term | home | UI harness |
| `editor-ui:885` | open | home | Settled at the pin: the panels' budgets are the five `Perf.EditorPanels.*` rows of `StrataTests/Perf/Budgets.json` (101-105), and one of them, `Performance600FramesPausedP95`, is provisional, with a target and no measurement; the page names where they live, says that one is provisional, and links `reference/performance` for the values (critic-editor-ui-11) |
| `new:47` | hands-on | home | Trace it yourself (D27): a breakpoint in `ImGuiHarness::ClickItem` while an `Editor.UI` test clicks a toolbar button shows the probe lookup, then the three frames: the hover, the press, and the release on which the button acts. Evidence: `StrataTests/src/Editor/ImGuiHarness.cpp:118-132` |
| `editor-ui:100` | feature | use | The item probe that tests read |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One test case with doctest, and running `StrataTests` | `core/first-change` | must |
| ImGui's frames; hovering decided from the previous frame | `editor-ui/imgui` | must |
| ImGui's input queue | `editor-ui/imgui-backends` | must |
| The item probe and the kit | `editor-ui/widget-kit` | must |
| `EditorHost`, `EditorLayer` and the panel registry | `editor-ui/shell` | must |
| Testing an engine: test kinds, determinism, regression tests | `engineering/testing` | helps |
| Benchmarks, noise and perf budgets | `engineering/perf-lab` | helps |
| Regular expressions and scanning source text | `basics/data-formats` | helps |

## `editor-ui/tutorial-panel` — Tutorial: adding a panel

**Covers.** The reader adds a panel to the editor in one engine patch: a "Selection Summary" panel that shows how many
entities are selected and which components they share, with a button that frames them in the Scene view. The sections,
each a stage of the patch: create the panel class and configure again so the new files build; register it with
`EditorPanelRegistry` in `RegisterBuiltinPanels`, find it in the View menu, open it with `editor.showPanel` and find its
open state in `imgui.ini`; draw it with the widget kit (no `ImGui::Begin`, colors from the theme, sizes from the font)
and make its button run a command with the UI's origin; dock it in the default layout and bump `c_LayoutVersion`, then
watch an old layout being replaced; test it with `HarnessEditor` and `ClickItem`, and run the `Editor.UI.Source` scans.
Each section ends with a checkpoint of the patch and its build or test output as a text capture. At the end the reader
has a panel that lands the way Strata's own panels do.

**Leaves out.**

- Adding a command for the panel to run → `editor/tutorial-command`
- Adding a component and its inspector rows → `world/tutorial-component`
- How the registry draws, focuses and persists panels → `editor-ui/shell`
- Landing a change: the review checklist and CI → `engineering/contributing`

**Fit.** `fits`: about 4,725 words against L (5,000). Five sections of two or three steps, each with a patch excerpt and
its output, take the most; the three exercises' worked solutions are patches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:670` | hands-on | home | Add a docked panel through `RegisterBuiltinPanels`, open by default: the View menu, `editor.showPanel`, persistence; then bump `c_LayoutVersion` and dock it |
| `editor-ui:129-136` | feature | use | The panel interface, the descriptor, the context, window names, open states and `Focus` |
| `editor-ui:112` | feature | use | The default layout and `c_LayoutVersion` |
| `editor-ui:122` | feature | use | `editor.showPanel` |
| `editor-ui:594` | rule | use | Panels never call `ImGui::Begin` |
| `editor-ui:653` | rule | use | Bump `c_LayoutVersion` for a panel open by default |
| `editor-ui:600` | rule | use | Controls from the widget kit |
| `editor-ui:605` | rule | use | The button's command carries the UI's origin |
| `editor-ui:256-258` | feature | use | The harness, the harness editor and the source scans |
| `new:48` | hands-on | home | Exercises (D27), open extensions with hints and patches as worked solutions: the frame button disabled while nothing is selected, with a tooltip that says why (Basic); the selected entities' names listed below the summary, clipped with `ImGuiListClipper` (Medium); a second button that frames the whole scene through `camera.focus` without entities, and a harness test that clicks it (Hard). Evidence: `StrataEditor/src/Editor/EditorViewportCommands.cpp:1073-1076`; `StrataEditor/src/UI/DeleteAssetDialog.cpp:130` (a clipped list in a dialog) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source, configuring again after adding files, running `StrataTests` | `core/first-change` | must |
| The panel registry, the default layout and its version | `editor-ui/shell` | must |
| The widget kit and the item probe | `editor-ui/widget-kit` | must |
| The harness, `ClickItem` and the source scans | `editor-ui/ui-testing` | must |
| The selection in `EditorContext` | `editor/program` | helps |
| Running one command from a terminal (`StrataCLI call`) | `editor/commands` | helps |
| Patches and git | `basics/git` | helps |

**Starting state.** The engine's source at the pin, configured and built in Debug as `core/first-change` shows, with the
editor and `StrataTests` built and the tests passing. The tutorial's patch chain starts at the pin: it needs no patch
of the WindZone chain or of another tutorial, so no checkpoint precedes it. A copy of `Samples/ThirdPerson`, made with
File ▸ Open Sample in the built editor, gives entities to select.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `editor-ui:49` | feature | `editor/program` | The split of the core from the UI is that page's (it repeats `editor-core:38`); `editor-ui/shell` draws what the UI library holds |
| `editor-ui:200` | feature | `editor/camera-viewport` | The editor camera's model and math are that page's (it repeats `editor-core:251`); `editor-ui/scene-view` homes the panel's drags (`editor-ui:461`) |
| `editor-ui:284` | concept | `editor/program` | Home of what an editor is and why it is not the game (`book.md`); `editor-core:290` is the same concept; `editor-ui/immediate-mode` teaches the Tooling half |
| `editor-ui:516` | figure | `editor/camera-viewport` | The camera's geometry is that page's figure (it repeats `editor-core:500`) |
| `editor-ui:549` | figure | `start/first-game` | One home for the launcher's picture, beside `gamedev:438`, the first page on every track (start-q8, rule D); `editor-ui/launcher-dialogs` uses the same recipe or a crop |
| `editor-ui:550` | figure | `start/first-game` | One home for the New Project and Open Sample pictures, beside `gamedev:439` (start-q8, rule D); `editor-ui/launcher-dialogs` uses them |
| `editor-ui:568` | figure | `editor/placement` | The drop's ghost is placement's picture (it repeats `editor-core:526`); `editor-ui/scene-view` uses it |
| `editor-ui:685` | hands-on | `make/editor-tour` | A game maker's first launch: find each panel, reset the layout, set Preferences ▸ Interface |
| `editor-ui:686` | hands-on | `make/scenes-entities` | Building a scene with the Hierarchy and the Inspector is taught there, on Coin Run's level |
| `editor-ui:687` | hands-on | `make/editor-tour` | Moving in the Scene view and the gizmos are first met in the tour |
| `editor-ui:688` | hands-on | `make/assets` | Imports, thumbnails and dragging a model into the view are taught with the first imports |
| `editor-ui:689` | hands-on | `make/play-test-debug` | Playing, the Game view's resolutions, Pause and Step, Shift+F1 and F8 are that page's |
| `editor-ui:690` | hands-on | `make/prefabs` | Overrides and Apply and Revert are taught with prefabs |
| `editor-ui:691` | hands-on | `make/input` | Binding an action by pressing its key is that page's; its collision-layer and quality parts are `make/physics`' and `make/quality`'s |
| `editor-ui:692` | hands-on | `make/play-test-debug` | Reading the editor's feedback after a failed build is part of debugging a game |
| `editor-ui:693` | hands-on | `make/scenes-entities` | Searching the Hierarchy belongs to working with entities |
| `editor-ui:694` | hands-on | `make/with-an-agent` | Connecting an agent from the launcher and watching its work is that page's |
| `editor-ui:700-701` | term | `ui/what-game-ui-does` | Home of the comparison of retained and immediate UIs (`book.md`) |
| `editor-ui:716` | term | `gpu/text` | Home of the glyph atlas (`book.md`; `render-core:768`); the editor's atlas is ImGui's own, which `editor-ui/design-system` says |
| `editor-ui:721` | term | `core/windows-events` | One glossary entry for content scale with `gameui:624`, homed on the page in the closures of both `ui/layout` and `editor-ui/ui-scale` (R31, D33); `editor-ui/ui-scale` keeps the concept `editor-ui:326` and links |
| `editor-ui:747` | term | `editor/program` | The same interface as `editor-core:650`, on the page that teaches the core and UI split and stands first (duplicates.md:45); `editor-ui/shell` links |
| `editor-ui:755-756` | term | `world/reflection` | Home of reflection, `PropertyInfo` and `ComponentInfo` |
| `editor-ui:759` | term | `world/prefabs` | Home of prefab overrides (`scene-ecs:671`) |
| `editor-ui:760` | term | `world/reflection` | The term inactive reason, one glossary entry with `scene-ecs:654`, which `world/reflection` homes with `SetInactiveReason` and its rule (R31, D11; world-q2; `book.md`'s row of inspectors and inactive reasons); `editor-ui/inspectors` uses it |
| `editor-ui:762` | term | `editor/undo` | Home of merging undo steps (`editor-core:674`) |
| `editor-ui:763` | term | `editor/play-mode` | One glossary entry with `editor-core:694`: Game view's home is `editor/play-mode` (R31, D33; critic-editor-core-12); "Scene view" and "viewport" stay with `editor-ui/scene-view`, whose `use` row says so (R46) |
| `editor-ui:766` | term | `editor/camera-viewport` | Home of the editor camera (`editor-core:730`) |
| `editor-ui:768` | term | `editor/camera-viewport` | `FitBounds` and framing are that page's |
| `editor-ui:777` | term | `input/mouse-cursor` | Home of cursor modes (`audio-input:670`) |
| `editor-ui:779` | term | `core/frame-loop` | The term beside its feature `foundation:48`, which `core/frame-loop` teaches (duplicates.md:51); `editor-ui/status` links |
| `editor-ui:780` | term | `editor/commands` | Status providers are sections of `editor.status`, a part of the core (`editor-core:47`), not of the status bar; `editor/commands` homes the term beside `editor-core:47` (editor-q5) |
| `editor-ui:782` | term | `input/rebinding` | Home of binding capture (`book.md`; `audio-input:686`) |
| `editor-ui:786` | term | `gpu/binding` | Home of binding sets (`render-core:704`) |
| `editor-ui:787` | term | `gpu/resources-lifetimes` | Event queries as the engine's "done" signal for lifetimes (`render-core:698`) |
| `editor-ui:788` | term | `gpu/how-a-gpu-frame-works` | Home of frames in flight (`book.md`; `render-core:699`) |
| `editor-ui:789` | term | `gpu/binding` | Push constants (`render-core:707`) |
| `editor-ui:791` | term | `gpu/vulkan-nvrhi` | Home of NVRHI (`render-core:683`) |
| `editor-ui:852` | open | `nowhere` | A note on files the survey read only in part |
| `editor-ui:856` | open | `nowhere` | A note on files the survey did not read beyond their headers; `ProblemsPanel` is now read and placed (`new:17` to `new:21`) |
| `editor-ui:864` | open | `nowhere` | A note on editor-core files read only where they carry UI ideas |
| `editor-ui:869` | open | `nowhere` | A note on test bodies not read; the budgets it names are settled by `editor-ui:885` |
| `editor-ui:871` | open | `nowhere` | A note on which documents were read |
| `editor-ui:874` | open | `appendix/history` | The release of arrival of the editor's interface features: the dating that `appendix/history` and the pages' `since` need |
| `editor-ui:881` | open | `nowhere` | Settled at the pin, and not content: the second include of `Include/Common.slang` in `ImGui.frag.slang` does nothing, because the file is guarded (`Strata/shaders/Include/Common.slang:1-2`) |

## Not taken

none

## Questions for the planner

none

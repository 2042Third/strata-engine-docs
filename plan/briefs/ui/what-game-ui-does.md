# Brief: `ui/what-game-ui-does`

| Field | Value |
| --- | --- |
| Title | What a game UI must do |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `world/scene-graph` |
| From | gameui ch. 1 (the problem, retained and immediate UIs compared and why the game UI is retained, a menu from components to pixels); home of the comparison |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `ui/what-game-ui-does` — What a game UI must do

**Covers.** The page opens with the problem as a player meets it, on the part's running example: the Third-Person
sample's main menu (`Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene`, its script `Scripts/MainMenu.cpp`). The menu
must look the same at 1280x720, 2560x1440 and 21:9; answer the mouse, the keyboard and a gamepad; keep moving while the
game runs at time scale 0; and never let the click on Play also reach the game. The naive answer is text and sprites at
pixel positions, drawn by game code every frame (before 0.4.0 Strata's only UI was screen-space text sized in pixels).
The page shows where it breaks: other resolutions, no focus for a gamepad, no order for clicks, work in every frame.

Then the idea: a UI is a tree of rectangles, laid out for one screen, drawn in tree order and hit topmost first. The
approaches follow, each from the flaw of the one before, with a table of cost, quality and who uses them: immediate
mode (Dear ImGui, which the Strata editor uses: code declares the UI again every frame) and retained mode (Unity's uGUI,
Unreal's UMG, Godot's Control nodes, the web's DOM: a tree that stays, laid out and drawn by the engine). Strata's
choice, in a `:::why` aside: retained, and made of entities. A UI element is an entity with a `UIRect` under a root
canvas, authored in the editor, saved with the scene, made into a prefab; references between widgets are entity
properties that duplicating and pasting remap; layout and drawing cost work only when something changes. The tour then
takes the menu from components to pixels: the eleven components and what each one does (the menu uses ten of them; the
input field is the eleventh), screen-space and world-space canvases, the focus as the one widget that keys act on, and
one frame (the "UI" scene system before the scripts, the overlay pass after post-processing). The module map shows the
GameUI layer, which only the composition root includes, so an engine without it still renders and plays. The page
ends with what the choice cannot do (no scroll views, drop-downs, rich text or multi-line fields) and with common
mistakes. Its three exercises search for the module's one include outside its folder, play a playground button at time
scale 0, and design the menu in immediate mode. At the end the reader can say why a game UI is retained here, name the
eleven components, and say which page of the part explains each step of the tour.

**Leaves out.**

- Making a HUD and a menu in the editor → `make/hud`, `make/menus`
- Why the editor's own interface is immediate mode, and Dear ImGui itself → `editor-ui/immediate-mode`, `editor-ui/imgui`
- The algorithms behind each step of the tour → `ui/layout`, `ui/contract`, `ui/text`, `ui/drawing`, `ui/input`
- Fonts, text shaping and glyph atlases → `gpu/text`
- The UI map of input actions and its bindings → `input/actions`
- Building and testing a UI through editor commands → `make/automated-playtests`
- Every property with its default and range → `reference/components`

**Fit.** `fits`: about 3,500 words against M (3,000). The tour from components to pixels takes the most words: each of
the eleven components in one sentence with a link, the module map and the frame timeline; the approaches and their
table come next.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:264` | concept | home | What a game UI must do; immediate against retained mode; why Strata's is retained and made of entities; the mistake of taking the editor's ImGui panels for the game UI |
| `gameui:42` | feature | home | The GameUI module is a layer of its own (Core, Input, Asset, Reflection, Scene and Renderer below it); only the composition root includes it |
| `gameui:43-44` | feature | home | `RegisterGameUIModule` registers the components, the overlay pass and the "UI" scene system; the components share the category "UI", and every one but `UIRect` requires `UIRect` |
| `new:2` | erratum | home | The page says eleven components, never twelve. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` holds eleven `ComponentRegistry::Register` calls (UICanvas, UIRect, UIImage, UIText, UISelectable, UIButton, UIToggle, UISlider, UILayout, UIInputField, UIMask); `plan/inventory/gameui.md:44` counts 12 |
| `gameui:46` | feature | home | An engine without the module still renders and plays: the renderer reaches the UI only through the overlay registry, scripts only through scene services |
| `gameui:66-67` | feature | home | Widget parts and event targets are entity properties, remapped by duplicate, paste and prefab instances; the UI is saved and loaded like any component, out-of-range values clamped |
| `gameui:226` | feature | home | The part's running example: the Third-Person main menu (its buttons, settings sliders and toggles, the credits in a mask); the other samples' HUDs and loading screens in one sentence |
| `new:3` | feature | home | The module's history for the page's `since`: the whole module arrived in 0.4.0; the rebindable UI map in 0.6.0, before which navigation used fixed keys. Evidence: `Docs/Releases/0.4.0.md:52-59`, `Docs/Releases/0.4.0.md:319-320`, `Docs/Releases/0.6.0.md:99-100` |
| `gameui:435` | figure | home | Module map: the GameUI layer and its neighbours, with the arrows that show that Renderer and Scripting do not include it |
| `gameui:438` | figure | home | Frame timeline: the "UI" scene system (actions, layout for the input screen, hits, focus, events) before the scripts' `OnUpdate`, then the renderer's world canvases, post-processing, screen text and screen canvases |
| `new:1` | not-done | home | No scroll views, drop-downs, rich text or multi-line input fields: a mask clips a scrolling list, and an input field is one line. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` registers no such component; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-279`; `git grep -niE "scrollview\|scroll view\|dropdown\|drop-down\|richtext\|rich text" 822a7a46 -- Strata/src/Strata/GameUI` finds nothing (the one match of "multiline" is the Inspector flag of `UIText`'s Text, `GameUIComponents.cpp:287`) |
| `gameui:617`, `gameui:619` | term | home | Canvas; UI element |
| `gameui:626` | term | home | Screen space and world space (the canvas's render mode) |
| `gameui:672` | term | home | Focus, at the level of the tour: the one widget that Submit and the direction keys act on |
| `editor-ui:700`, `editor-ui:701` | term | home | Immediate-mode GUI (code describes the UI every frame, the library keeps little state) and retained-mode GUI (a tree of widgets that keeps its state), defined with the approaches table; `editor-ui/immediate-mode` uses both |
| `new:14` | hands-on | home | Exercises (D27), from easy to hard: Basic, trace: predict which engine files outside `Strata/src/Strata/GameUI` include a GameUI header, then search (only the composition root, which lists the module beside the others); Medium, predict then run (done): in the playground, a button made with Hierarchy > + > UI > Button and a script on it that sets the time scale to 0 in `OnCreate` and logs `UI::IsPointerOverUI()` and `Input::IsMouseButtonPressed` in `OnUpdate`: say first whether the hover tint still fades, whether `OnUIClick` still comes and which presses the game sees, then play; Hard, design: the same menu in immediate mode, and what each approach does on a frame where nothing changes and when a gamepad moves the focus. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77` (`git grep -l '#include "Strata/GameUI/' 822a7a46 -- Strata/src` finds `BuiltinModules.cpp` and the module's own files); `StrataEditor/src/Editor/GameUIPresets.cpp:112`; `StrataScriptCore/Include/StrataScript/UI.h:156-162`; `Strata/src/Strata/Input/Input.h:94-97`; `Strata/src/Strata/GameUI/GameUISystem.cpp:880-931` |
| `gameui:53-65` | feature | link | The tour names each component in a sentence and links the page that explains it |
| `gameui:142` | feature | link | The overlay pass that draws the canvases (`ui/drawing`) |
| `gameui:176` | feature | link | The UI system's order in one frame (`ui/input`) |
| `gameui:185` | feature | use | The UI map that menus navigate with, in one sentence (its home is `input/actions`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, components and the registry | `world/ecs` | must |
| The hierarchy: parents, children, sibling order, active in hierarchy | `world/scene-graph` | must |
| One frame from start to finish, frame time | `start/what-an-engine-is` | must |
| Reflection: one registration for the Inspector, files and scripts | `world/reflection` | helps |
| Scenes saved as documents | `world/serialization` | helps |
| Prefabs and instances | `world/prefabs` | helps |
| Scene systems and their order; scene services | `world/systems` | helps |
| Layers, the composition root and optional modules | `core/layers-registries` | helps |
| Overlay passes drawn over the finished image | `gpu/debug-drawing` | helps |
| Time scale and unscaled time | `core/time` | helps |
| Input actions and maps | `input/actions` | helps |
| Script callbacks | `scripting/script-system` | helps |
| Post-processing and tone mapping, which the screen UI draws over | `image/why-post` | helps |
| Dear ImGui, for the comparison | `editor-ui/imgui` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `canvas` | Canvas | - |
| `focus` | Focus | - |
| `immediate-mode-gui` | Immediate-mode GUI | IMGUI |
| `retained-mode-gui` | Retained-mode GUI | - |
| `screen-space` | Screen space | world space (render mode) |
| `ui-element` | UI element | - |

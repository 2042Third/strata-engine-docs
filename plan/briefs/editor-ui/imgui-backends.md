# Brief: `editor-ui/imgui-backends`

| Field | Value |
| --- | --- |
| Title | ImGui backends |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/imgui`, `core/engine-modules`, `gpu/binding`, `gpu/resources-lifetimes`, `basics/color` |
| From | editor-ui ch. 4 "Plugging ImGui into an engine" (`ImGuiModule`, `ImGuiLayer`, `ImGuiPlatform`, `ImGuiRenderer`, the two shaders, frames in flight, dynamic textures, texture display modes) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clip-rectangle` | Clip rectangle | - |
| `dynamic-textures-imgui-1-92` | Dynamic textures (ImGui 1.92) | - |
| `imguitexturedisplay` | ImGuiTextureDisplay | - |

# Brief: `ui/drawing`

| Field | Value |
| --- | --- |
| Title | Drawing the UI |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `ui/contract`, `ui/text`, `gpu/binding`, `gpu/debug-drawing`, `draw/mirrors-camera-relative` |
| From | gameui ch. 7 (`UIQuad`, slots and journals, indirection tables, uploads, runs, the shaders, world-space canvases on the GPU, the overlay registry) |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `ui/drawing` — Drawing the UI

**Covers.** The job: turn the laid-out elements into 64-byte quads and draw every canvas of a scene in each view, the
screen-space ones over the finished image and the world-space ones in the scene, in about one draw per canvas. The page
carries the full section on the problem and how engines solve it: a draw per element; batched quads; clipping by
scissor rectangles, by stencil masks or in the shader; buffers kept on the GPU against buffers written again every
frame. The map is the data flow from component to pixel: components, `GameUIScene`'s elements and shaped texts, the
quad array in slots, the renderer's buffers (quads, texture slots, glyph table, clip rects, transforms), the shaders.
The contract, each rule with its reason: the renderer never includes GameUI and reaches it through the overlay
registry; quads name UI texture and font indices, never bindless slots or atlas places; masks clip in the shader,
never by splitting draws; `UIQuad` and the shader's structs change together; the pass asks for each texture and font
once per frame. A toy of about 50 lines turns a list of rects into a quad array and splits it into runs.

The real code, on the Third-Person main menu, in the order data flows. The quad: `UIQuad` and `UIDrawParameters`, their
flag bits and the `static_assert` of their size. Quads per element in slots with room to spare (a text gets a quarter
more, a field two for its caret and selection), rewritten in place or repacked when a slot overflows, with a journal of
changed ranges. Image quads: tint, image swap, solid color, preserve aspect, filled images, the nine-slice cut whose
borders shrink together; glyph quads with the pen on the baseline; every quad carrying its clip. The indirection that
keeps quads still when mip streaming moves a slot or an atlas packs a glyph, and its limit: a scene's UI gives every
distinct font an index that is never freed, so once 256 fonts hold them (the default among them), texts in any further
font draw nothing, without a log. The pass:
registered through `SceneOverlayRegistry`; `Prepare`, `DrawWorld` and `Draw`; screen canvases hidden where the view
hides screen text; a scene with no camera that shows its UI over black; uploads of changed ranges only; texture slots
requested at High priority, white while loading, reported to mip streaming; glyphs from the renderer's `FontAtlasCache`;
runs of up to four atlases; the pipelines (display-value blending, no culling, the world pipeline's reversed-Z depth
test without writes and its TAA depth bias); binding sets and buffers released when unused; six vertices per quad and no
vertex buffer; the `GPU.UI` and `Render.UI` stages; `SceneOverlayStats`, what the pass reports each frame, which the GPU
tests read and `viewport.capture` returns and waits on. The shaders: the vertex shader pulls its quad by instance index,
snaps edges and baselines to whole pixels and culls quads outside their clip; the fragment shader shades a rounded rect
by its signed distance with a border, decodes sRGB textures back to display values, shades SDF glyphs with an outline,
fades masks by their softness, and keeps its one discard last so derivatives stay defined. World-space canvases: the
canvas-to-world matrix, camera-relative transforms subtracted in double, antialiasing by `fwidth`, mip streaming from
the pixels a unit projects to; they are unlit and drawn after post-processing, and placed by the last fixed step's pose,
not the drawn one (in one sentence with a link to `world/interpolation`). The page ends with the alternatives, the GPU
tests of `GPU.GameUI`, changing it safely, and three exercises (an upload traced, a radial fill, an outline measured in
pixels). At the end the reader can follow one button from its components to its pixels, and say which buffer an edit
uploads.

**Leaves out.**

- The overlay registry in general and debug drawing → `gpu/debug-drawing`
- Bindless, push constants and pipelines → `gpu/binding`
- Glyph atlases, distance fields and font validation → `gpu/text`
- Camera-relative rendering in general → `draw/mirrors-camera-relative`
- How textures stream their mips → `draw/mip-streaming`
- The canvas mode (its zoom and pan, and that it edits screen-space canvases only) and the viewport's Game UI chip →
  `editor-ui/scene-view`
- `SceneScreenView`, the frame's option that zooms and pans the screen canvases → `gpu/debug-drawing`
- The tone mapping the screen UI draws over → `image/tone-mapping`

**Fit.** `fits`: about 9,300 words against XL (8,000). Ten excerpts, five concepts, nine figures and six rules make it
the part's fullest page, and the pass and the shaders take the most words; at 700 words below XL's top, a further item
would need the split into "Drawing the UI: quads, batches and the pass" and "The UI's shaders and world-space canvases".

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:326` | concept | home | Batching for the GPU: a flat array of quads in draw order, one buffer, instancing without a vertex buffer, one draw per canvas, indirection tables, slots and a journal; the mistakes of a draw per element and of GPU slots baked into cached data |
| `gameui:310` | concept | home | Images: nine-slice, fill, preserve aspect, rounded rects and borders by a signed distance (no texture needed); the mistake of slice borders in canvas units |
| `gameui:332` | concept | home | Clipping without breaking batches: scissor, stencil and shader clipping; quads that name a clip rect; soft edges; the one late discard |
| `gameui:337` | concept | home | Pixel snapping and blending in display values over the tone-mapped image; the mistake of blending UI in linear HDR |
| `gameui:346` | concept | home | World-space UI: a canvas as a plane, depth-tested without writes, camera-relative in double, `fwidth` antialiasing, mip streaming from the projected unit, TAA depth bias, unlit |
| `gameui:57` | feature | home | `UIImageComponent`: texture or solid color, simple, sliced or filled, UV rect, slice borders and scale, fill, preserve aspect, corner radius, border, raycast target on by default |
| `gameui:55` | feature | home | `UICanvasRenderMode`: screen space and world space |
| `gameui:85` | feature | home | What is visible: active in the hierarchy, a toggle's checkmark only while it is on, a placeholder only while the field is empty |
| `gameui:87` | feature | home | The world-space canvas's plane matrix, `GetCanvasWorldMatrix` |
| `gameui:93` | feature | home | Root and world canvas counts cached per hierarchy version, so hidden canvases are counted, not laid out |
| `gameui:126-136` | feature | home | `UIQuad`, `UIClipRect` and `UIDrawParameters`; slots with headroom; the journal; repacks; indirection to UI texture and font indices; use counts; image quads; glyph quads with the selection and caret quads; the clip index on every quad |
| `new:24` | feature | home | The limit of the font indices, said with the indirection tables: a scene's UI gives every distinct font it uses an index that is never freed (index 0 is the default font), and `c_MaxUIFonts` is 256, so once the default and 255 others hold them, texts in any further font draw nothing, without a log. Evidence: `Strata/src/Strata/GameUI/GameUIQuads.cpp:58-71`, `:467`; `Strata/src/Strata/GameUI/GameUIScene.cpp:145-147`; `Strata/src/Strata/GameUI/GameUIRenderData.h:18-19`; no line of `Strata/src/Strata/GameUI` erases from `m_Fonts` |
| `gameui:142-158` | feature | home | The pass: its registration, `Prepare`, `DrawWorld`, `Draw` and `HasScreenContent`; screen canvases and `DrawScreenSpaceText`; the UI over black; uploads; clips; transforms; textures; glyphs; runs; pipelines; binding sets; the instanced draw; the stages; both shaders; the layout shared with C++ |
| `new:22` | feature | home | `SceneOverlayStats`, what the UI pass reports each frame in `SceneRendererStats::Overlays`, beside `GameUISceneStats` of `ui/contract`: root canvases drawn and hidden, elements, quads (empty slots included), draw calls, glyphs waiting for the raster budget, fonts and textures still loading, bytes uploaded; the GPU tests read it to show one draw per canvas and an idle frame that uploads nothing, `viewport.capture` returns part of it as `ui` and waits while UI glyphs are pending, and project thumbnails wait for them too. Evidence: `Strata/src/Strata/Renderer/SceneOverlay.h:41-54`; `Strata/src/Strata/Renderer/SceneRenderer.h:619`; `Strata/src/Strata/GameUI/GameUIRenderer.cpp:200`, `:243-252`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:801`, `:808`, `:978-979`; `StrataEditor/src/Editor/ProjectThumbnail.cpp:169`; `StrataTests/src/Renderer/GPUGameUITests.cpp:301-313`, `:1080-1083` |
| `gameui:160` | feature | home | The shader entries registered in `Strata/CMakeLists.txt` |
| `gameui:238` | feature | home | The suite `GPU.GameUI`: pixels, snapping, colors, masks, the world canvas, 100 km from the origin, stable under TAA, the screen view, mip streaming, resource release |
| `gameui:407` | code | home | `Strata/src/Strata/GameUI/GameUIRenderData.h:28-78`: `UIQuad`, `UIClipRect` and `UIDrawParameters`, the flag bits, `static_assert(sizeof(UIQuad) == 64)` |
| `gameui:409` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:192-267`: `BuildQuads`, slots rewritten in place, a repack when one outgrows its room, the journal reset |
| `gameui:408` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:321-357`: the nine-slice cut, its UVs, borders that shrink together |
| `gameui:410` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:467-484`: shaped glyphs become quads, the pen on the baseline kept in `UV.xy`, the outline clamped to 0.1 em |
| `gameui:415` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:259-362`: `UploadQuads`, only changed ranges, merged, the whole array as fallback |
| `gameui:416` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:611-689`: `BuildRuns`, the limit of four atlases and runs split beyond it |
| `gameui:417` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:364-394`: `UploadTransforms`, world canvases relative to the camera, the subtraction in double |
| `gameui:412` | code | home | `Strata/shaders/GameUI/UIQuad.vert.slang:41-143`: the vertex shader pulls its quad by instance index, snaps to pixels, culls by clip, places world canvases |
| `gameui:413` | code | home | `Strata/shaders/GameUI/UIQuad.frag.slang:76-106`: `ShadeImage`, the rounded rect's signed distance, the border band, the sRGB decode, `fwidth` for world canvases |
| `gameui:414` | code | home | `Strata/shaders/GameUI/UIQuad.frag.slang:108-120`: `st_Main`, why the clip multiplies and the one discard comes last; with `ShadeGlyph` (62-73), the glyph's fill and outline |
| `gameui:453` | figure | home | Data flow from component to pixel (the page's map) |
| `gameui:455` | figure | home | The memory layout of `UIQuad` (64 bytes, the kind and font bits), the glyph table and the texture slot entries |
| `gameui:458` | figure | home | Indirection: quad, UI texture index, slot table, bindless array; glyph index, the font's glyph table, atlas page and texels |
| `gameui:460` | figure | home | A canvas's quads split into runs by the four-atlas limit |
| `gameui:461` | figure | home | The rounded rect's distance field: radius, border band and the one-pixel coverage ramp |
| `gameui:485` | figure | home | Images: solid, rounded with a border, a nine-sliced panel, a health bar filled to 0.3, preserve aspect (the scene of `GPUGameUITests.cpp`'s image test) |
| `gameui:488` | figure | home | Pixel snapping off and on at a fractional scale, as a zoomed crop |
| `gameui:495` | figure | home | The Third-Person credits scrolling in their mask, softness 0 against 20 |
| `gameui:497` | figure | home | A world-space canvas seen in perspective, partly behind nearer geometry, and the same canvas in screen space; a recipe's project is a sample, a template, the look-dev project or a lab (pipelines.md §5.2), so the recipe builds the canvas on a copy of a sample with `setup` steps (`ui.create` makes a canvas, `component.set` gives it the `RenderMode` WorldSpace, `Strata/src/Strata/GameUI/GameUIComponents.cpp:232`), after the GPU test's scene (a 4 x 2 m sign, a HUD square, geometry in front) or the feature scene's world-space canvas (`gameui:730`) |
| `gameui:518` | rule | home | The renderer never includes GameUI: the pass registers through `SceneOverlayRegistry`, so the layer rule holds and builds without the module work |
| `gameui:524` | rule | home | Quads name UI texture and font indices, never slots or atlas places: mip streaming and atlas packing would otherwise rebuild them |
| `gameui:526` | rule | home | Masks clip in the shader, never by splitting draws: a canvas stays one draw |
| `gameui:530` | rule | home | `UIQuad` and the shader's structs change together: the `static_assert` guards only the size |
| `new:10` | rule | home | The pass requests each distinct UI texture and font once per frame, never per element, at High priority. Evidence: `AGENTS.md:331-332`; `Docs/DeveloperGuide.md:2665-2668` |
| `gameui:561` | rule | home | The known limits, stated and not exceeded: world canvases are unlit and drawn after post-processing; the game's clicks on them ignore geometry in front (`ui/input`) |
| `new:9` | not-done | home | No lit world-space UI: world canvases are drawn unlit, without shadows, after post-processing. Evidence: `Docs/Releases/0.7.0.md:389-390` |
| `new:23` | not-done | link | No drawn (interpolated) poses for world-space game UI, an entry of "What Strata does not do" homed on `world/interpolation`: a canvas is placed by the scene's world transform, the last fixed step's pose, so a name tag on an interpolated body moves in fixed steps against it, and hits use the same matrix; one sentence in the world-space section, with the link. Evidence: `Docs/Roadmap.md:1698-1699` (the entry's evidence, book.md); `Strata/src/Strata/GameUI/GameUIScene.cpp:1101-1113` (`m_Scene->GetWorldTransform`); `Strata/src/Strata/GameUI/GameUIHitTest.cpp:38`; `Strata/src/Strata/GameUI/GameUISystem.cpp:380` |
| `gameui:730` | open | home | Settled at the pin: no sample has a world-space canvas (the Showcase's `Outpost.stscene` holds two screen-space canvases), but the tests have two: `git grep -lE '"RenderMode": *"WorldSpace"' 822a7a46 -- Samples StrataTests` finds `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene` (line 4825, 0.005 m a unit), and the GPU test at `StrataTests/src/Renderer/GPUGameUITests.cpp:569-696` builds a 4 x 2 m sign and a HUD square, with a cube in front of the sign at 669-676; the recipe of figure `gameui:497` rebuilds one of them on a copy of a sample |
| `new:25` | hands-on | home | Trace it yourself (D27): a breakpoint in `UploadQuads` while the pointer moves onto the Third-Person main menu's Play (its tint fades) shows the journal's few changed ranges, merged, and the bytes that `SceneOverlayStats::UploadedBytes` then reports; once the fade has ended, a frame uploads nothing. Evidence: `Strata/src/Strata/GameUI/GameUIRenderer.cpp:259-362`; `Strata/src/Strata/Renderer/SceneOverlay.h:53`; `StrataTests/src/Renderer/GPUGameUITests.cpp:304-313` |
| `gameui:595` | hands-on | home | Exercise: a fill direction `Radial360`, a quad flag and a shader path, `UIQuad` kept at 64 bytes, with enum, inactive reason, tests and feature test |
| `gameui:610` | hands-on | home | Exercise: argue why a glyph outline is measured in em and limited to 0.1 em by the distance field's spread |
| `gameui:649-652` | term | home | Nine-slice; filled image; quad; instancing and vertex pulling |
| `gameui:654` | term | home | Draw run (the UI's batch) |
| `gameui:657-659` | term | home | Softness; pixel snapping; display (sRGB) values |
| `gameui:342` | concept | use | Overlay passes and the dependency inversion behind them, from `gpu/debug-drawing` |
| `gameui:303` | concept | use | Glyphs drawn from the renderer's distance-field atlas, from `gpu/text` |
| `gameui:159` | feature | link | The screen view that zooms and pans the canvases in the canvas mode (`editor-ui/scene-view`) |
| `render-core:223` | feature | use | `ISceneOverlayPass`, `SceneOverlayRegistry` and `SceneOverlayFrame` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Overlay passes and `SceneOverlayRegistry` | `gpu/debug-drawing` | must |
| Structured buffers, push constants, bindless textures and pipelines | `gpu/binding` | must |
| Instanced draws | `draw/batching` | must |
| Vertex and fragment shaders in Slang | `gpu/shaders` | must |
| Distance-field glyphs from the `FontAtlasCache` | `gpu/text` | must |
| Camera-relative positions, subtracted in double | `draw/mirrors-camera-relative` | must |
| Clip space, NDC and reversed-Z depth | `gpu/coordinates` | must |
| Where overlays draw in the frame | `gpu/frame-tour` | must |
| sRGB values and the transfer function | `basics/color` | must |
| The element array, the boxes and the clip rects | `ui/layout` | must |
| Dirty marks and the change journal | `ui/contract` | must |
| Shaped texts, caret stops, the field's state | `ui/text` | must |
| Pixel derivatives and why a discard breaks them | `light/brdf` | helps |
| Tone mapping, which the screen UI draws over | `image/tone-mapping` | helps |
| The TAA jitter | `image/taa` | helps |
| Mip streaming's reports of drawn textures | `draw/mip-streaming` | helps |
| Asset requests at a priority | `assets/residency` | helps |
| Releasing GPU resources | `gpu/resources-lifetimes` | helps |
| GPU stages and timestamps | `gpu/readback-timing` | helps |
| A GPU test that reads pixels back | `gpu/first-triangle` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `display-values` | Display values | - |
| `draw-run` | Draw run | - |
| `filled-image` | Filled image | - |
| `instancing` | Instancing | vertex pulling |
| `nine-slice` | Nine-slice | - |
| `pixel-snapping` | Pixel snapping | - |
| `quad` | Quad | - |
| `softness` | Softness | - |

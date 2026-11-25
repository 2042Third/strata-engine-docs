# Notes: `gpu/readback-timing`

## New terms

None proposed. The page defines the four terms the glossary homes here in bold: readback, timestamp query (with
GPU timestamp), GPU stage, tile-based renderer.

## Requests

- `tools/data/names.txt` or `extra-words.txt`: the product names Nsight and Radeon (vendor capture tools, one sentence
  of the problem section and one table row), and the word encoder (Metal's encoder boundaries, in the tile-based
  section; the engine's guide uses it).
- `names`: 50 findings, all stage names of the frame profiler (`GPU.Uploads` ... `GPU.Overlays`, `GPU.UI`,
  `GPU.ImGui`) and `GPU.Fog`, the stage the reader adds in exercise 1; the dumps hold no stages. Left as written.
- Figure `gpu-stages-panel` (Performance panel, Showcase sample, GPU stage rows) is asked for in
  `src/content/figures/gpu/readback-timing.json`; its layout `layouts/performance.ini` is the one `core/profiling`
  already asks for and does not exist yet.
- Host for the Further reading entries (Vulkan specification, NVIDIA Nsight Graphics and AMD Radeon GPU Profiler
  documentation): the entries are cited without links.
- The warnings `passive` (76) and `noun-stack` (5) are left: nearly all are state words ("is dropped", "is
  registered") with no actor.

## Since

`since: 0.3.0`. `TextureReadback`, `Renderer::ReadTexture` and picking are 0.3.0 per the inventory
(`render-core` lines 66, 201, 203); the GPU profiler and its stages came in 0.4.0.

## Not verified

- That vendor capture tools show per-draw detail and run beside the program, and that pipeline statistics queries
  count shader runs: general knowledge of Nsight Graphics, Radeon GPU Profiler and Vulkan, not checked in the pin.
- That tile-based GPUs split the screen into tiles and draw them in on-chip memory: general description; the pin
  states only the MoltenVK and Metal behavior (`Docs/Architecture.md` "Frame profiler").
- That `GPU.Cull`'s `Next` call is made only on frames that cull on the GPU: the page says only that the work
  between culling and the aerial stage stays in the stage that was running.
- The 14 timestamps and slot numbers of the ring example, and the 10 ms frames of the blocking example, are invented
  and said so or shown as an example.

## Findings not applied

- Brief item `new:18` (the erratum) is applied: both registration exceptions are stated (`GPU.DepthOfField` after
  `GPU.MotionBlur`; `GPU.Aerial` registered before `GPU.Cull` and timed after it). Checked at
  `GPUProfiler.cpp:50-66` and `SceneRenderer.cpp:3360, 3381, 3590, 3600`.
- The brief's line 6235-6237 of `Docs/DeveloperGuide.md` is not quoted (the lint forbids ten words in a row).
- "What went wrong before" is omitted: the history has no bug with a regression test that the pin names.
- `render-core:66` and the back-buffer capture: the page says the graphics module's back-buffer capture uses the
  blocking `Renderer::ReadTexture` (`GraphicsModule.cpp:121`).

## Clerk

- Admitted to names.txt: Nsight, Radeon; to extra-words.txt: encoder (this page).
- Left for the planner: the names the dumps lack (the frame profiler's GPU stages), figure `gpu-stages-panel` and `layouts/performance.ini`.

## Names of this page

- `GPU.Fog`: the stage that exercise 1 adds; the pin registers no GPU.Fog (RendererGPUStages::Get).

## Figures

- `gpu-stages-panel` (editor), settled 2026-11-18 with the provisional build (engine 5b975ad2; nothing published,
  `waitsFor` kept). The writer's recipe named `layouts/performance.ini`, which does not exist, and pictured the whole
  window at 1280 by 720, where the table's GPU rows are below the panel's edge and no command scrolls it. The recipe now
  pictures the panel at its own pixels (`panel: "Performance"`) in the new `layouts/gpu-stages.ini` (1280 by 1220,
  bottom tabs 860 by 1000 px), with the Showcase open in Edit mode and 700 frames waited, so the ring holds no loading
  frames.
  - Round 1: a 768 px wide panel in a 1280 by 1300 window showed every row, but cut the **Copy as JSON** button and
    left 90 px empty below the table.
  - Round 2 (good): the toolbar whole; the CPU stages; the line "GPU · 599 frames, known 2.0 frames late", which is the
    caption's "a few frames after"; GPU busy; then the seventeen stages in registration order plus `GPU.UI` and
    `GPU.ImGui`. `GPU.Uploads`, `GPU.RadianceCascades`, `GPU.MotionBlur`, `GPU.DepthOfField` and `GPU.UI` did not run and
    are dimmed at 0.000, which the alt says. The caption no longer says "each stage the frame ran": every registered
    stage has a row. The "Capped: ..." line is cut by the Stage column, as in `core/profiling`.
  - Viewer's review, 2026-11-18 (no retake: only words changed):
    - "Capped: ..." cut at the Avg ms column (unreadable): the pin and the provisional build cannot do better. The
      table is drawn with `ImGuiTableFlags_NoSavedSettings` and stretch weights 3:1:1:1:1
      (`PerformancePanel::DrawStageTable`), so a `[Table]` entry in the layout is ignored; the layout the take saved
      (`docs-work/photo/gpu-readback-timing/layouts/`) holds no `[Table]` section. The whole line (106 characters, about
      575 px) needs a Stage column of that width, a panel near 1340 px: wider than the window and unreadable when scaled
      to 768 px, where the 860 px panel now reads at 89 %. The alt now names the cut line. A request for the engine:
      wrap the bound line, or let it span the table's columns.
    - GPU strip looks empty (unclear): stands. Both strips share one scale (`PerformancePanel::GetTimelineScale`, 5 ms
      here) and the GPU is busy about 0.22 ms a frame (GPU busy avg 0.219), so its bars are a pixel tall. The caption
      now says the strip is nearly flat and why; the alt says it holds only marks a pixel tall.
  - 2026-11-24, published at the pin v0.8.0 (319075e3), one take without `--provisional`, `waitsFor` removed as `check`
    asked. The picture matches round 2: every row readable, "GPU · 599 frames, known 2.0 frames late", the scale still
    5 ms, the same five stages dimmed at 0.000, "Capped: ..." still cut. GPU busy is now 0.251 ms (Capped line: GPU
    0.3 ms busy), so the caption says "about 0.25 ms" and `numbers` gives the new values.

# Notes: draw/gpu-driven

## New terms

- None proposed. The page defines the glossary's five terms in bold: GPU-driven rendering, counting pass (write pass), `drawIndexedIndirectCount`, LOD record, visibility feedback. "Feedback loop" is explained in bold in the last section of the real code but is not proposed as a term.

## Requests

- Generated values: the brief names the keys `perf.PerfGPU.Renderer.Render100kCubes.Measured`, `...Render100kCubesGPU.Measured`, `...Render1MCubes.Measured` and `...Render1MCubesGPU.Measured`; `src/generated/reference/values.json` has no such keys, so the page writes the numbers (0.173, 1.436, 0.285 and 12.85 ms, from `StrataTests/Perf/Budgets.json` at the pin) as text. If the keys appear, replace them with `:value`.
- Further reading names Haar and Aaltonen (SIGGRAPH 2015), Wihlidal (GDC 2016) and the Khronos specification without links; no host is requested.

## Since

- 0.4.0: inventory render-scene rows for the GPU-driven path (mode switch, Cull.comp, buckets, feedback) all say 0.4.0.

## Not verified

- The CPU culling cost of 20 ns per proxy is an assumption, labelled as one on the page.
- That the readback of the counters and of the feedback arrives two to three frames late comes from the inventory (render-scene rows 123-132); the code keeps six records (`c_GPURecordCount`) but no test pins the number. Exercise 3's answer states its expectation as a prediction to measure.
- "The pin has no editor setting or command for `GPUDriven`": searched `StrataEditor`, `StrataRuntime` and the engine's Engine and Scene folders only; the editor shows the statistic.
- That MoltenVK offers no GPU-written counts rests on the 0.4.0 release notes (Docs/Releases/0.4.0.md) and the inventory, not on a device run.
- The statement that the talks of 2015 and 2016 describe shipped games is general knowledge (Further reading level notes).
- The invented numbers in the worked examples (LOD record 7, dense bucket 0, the cube's pool place) are labelled invented.
- Exercise 4's answer (a parallel buffer in `RenderSceneGPU`, bound at the next free slot) follows the AGENTS rule's text, not a built change.

## Findings not applied

- The brief lists no open findings beyond its items. Items `render-scene:60`, `:99-100`, `:172`, `:110`, `:68`, `:505` (use rows) are applied in the culling and feedback sections.
- Brief claim "deterministic ranges per record": `CullBuild.comp` takes ranges with an atomic add on the draw list's used length, so the order of ranges differs between runs; the page states that the ranges are exact in size, not fixed in order.
- The perf table compares the CPU frame with the GPU busy time of the GPU-driven path only: the pin has no measurement of the CPU path for the same scenes, so the page does not claim a speedup.
- `new:17` trace exercise: written as a search-based answer; no debugger capture was taken.

## Clerk

- The perf keys now exist in values.json (perf.PerfGPU.Renderer.Render100kCubes.Measured and the others, from tools/reference.py render); the page's numbers as text stay correct, and may become :value marks.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

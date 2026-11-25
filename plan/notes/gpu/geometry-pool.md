# Notes: gpu/geometry-pool

## Since

The pool's header was added in commit 170c99dc (14 October 2026), first contained in tag v0.4.0-rc1: `since: 0.4.0`.

## New terms

None proposed beyond the six the brief lists.

## Requests

- Extra word: "vertices" (plural of vertex; 31 uses; the lint's `word-list` rule fails on it only).
- External hosts for Further reading, cited now without links: github.com (OffsetAllocator by Sebastian Aaltonen) and registry.khronos.org (the Vulkan specification).
- No figures file: the pool's memory map is a Mermaid diagram.

## Not verified

- That `SV_VulkanInstanceID` includes the draw's start instance where `SV_InstanceID` does not (said in one clause, with the rule left to `draw/batching`).
- That the two registered built-in meshes beyond the four named in `RendererRegistration.cpp` exist; the page says "some of them".
- The names `GPU.SceneRenderer.GPUDriven` and `.Feedback` are not written on the page (the text only points to the GPU-driven page).
- The two Further reading entries were written from memory of their subject, not opened.

## Findings not applied

- Brief: "12-byte positions in their own stream (depth-only passes fetch nothing else)". At the pin the shadow input layouts read the position and the texture coordinates (alpha-tested casters), so the page says that, not "nothing else" (`Strata/src/Strata/Renderer/SceneVertexLayouts.h`).
- Brief's `foundation:162` details (size classes, bounded planning) are given in one paragraph after the toy, not as a section.
- The history section (`## What went wrong before`) is omitted: no bug with a regression test was verified.
- The two exercises of the brief: "fragment, compact, compare a frame" became a hand computation plus a sketch of growth (the frame comparison is a GPU test and is described under testing); the trace exercise is as briefed.
- Culling tables, `SetLayout` and `GeometryTables.slang` are named only in "Changing it safely" (taught on `draw/gpu-driven`).

## Clerk

- Admitted to extra-words.txt: vertices (the plural of vertex, gpu/how-a-gpu-frame-works).
- github.com and registry.khronos.org were already allowed hosts.

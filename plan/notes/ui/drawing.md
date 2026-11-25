# Notes: ui/drawing

## New terms

- None proposed. The page defines the eight terms the glossary homes on it (quad, instancing, softness, draw run, display values, nine-slice, filled image, pixel snapping) in bold.

## Requests

- None. Words the lint refused were reworded (bookkeeping, unlit, repack, indirection, grayscale, raster, modulo, antialiasing, mismatch). Plain `stencil` and `scissor` appear only in code or bold. Further reading cites Dear ImGui, Unity, Unreal, "Real-Time Rendering" and a Valve paper without links.
- No figures file: the three pictures are Mermaid diagrams (one is a table-backed flow of buffers, one the lookup tables). The brief's pictures (rounded rect field, nine-slice panel, snapping crop, credits mask, world canvas) are not drawn.

## Since

- 0.4.0: the game UI module's first release, `Docs/Releases/0.4.0.md:52-59` at the pin; `Docs/Releases/0.3.0.md` names no game UI (part review).

## Not verified

- That the Third-Person main menu's Play button fades its tint on hover (the scene holds entities named Play, Title, Credits; the fade is inferred from `ColorTint` and `FadeDuration`).
- That `GPU.GameUI` is the doctest suite filter name for `GPUGameUITests.cpp` (`names` accepts it).
- The reason for the outline limit of 0.1 em (the field holds distances only a short way past the edge) is the brief's, not read from the atlas code.
- The comparison rows of Alternatives (Dear ImGui, Unity, Unreal) are general knowledge, not checked against their documents.
- Slot numbers 0 to 8 are the binding set's order in `GetBindingSet`; the shader's register lines were not read.

## Findings not applied

- The brief lists no open findings.
- The nine figures of the brief are not requested (see Requests): only diagrams are in the page.
- `new:23` is one sentence with the link to `world/interpolation`, applied. `gameui:730` is applied as one sentence (no sample has a world canvas; two tests do).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

# Notes: indirect/seam

## New terms

- fallback stack: a list of light sources ordered from the most exact to the least, each layer taking a weight and passing the remaining share down. Home: indirect/seam. Aliases: fallback hierarchy.

## Since

0.8.0: `Strata/shaders/Include/IndirectLight.slang` says its struct follows "wave 8's plan"; the seam did not exist in 0.7.0, whose four forms it keeps.

## Requests

- Links to indirect/problem, indirect/ao and indirect/gi-cascades, indirect/gi-limits point at pages not yet written; they must exist before the build.
- No figures file: both pictures are Mermaid diagrams.

## Not verified

- The brief says the suite `GPU.SceneRenderer.Lighting` keeps the default image bit for bit; no test of it says so at the pin, so the page names the white furnace test and the probe suite's dummy test only.
- That the "Reflections" stage trace needs a temporal frame was read in `RenderFrame` but the page only states the flag `ReflectionParams.x` comes from `m_ReflectionFrame`.

## Findings not applied

- The brief lists the field's slots as "35 to 40 and 54": the layout binds 35, 37, 38, 39, 40 and 54 (no slot 36), and the page says so.
- The brief names `GPU.AO`, `GPU.RadianceCascades` and `GPU.Reflections` as stages; the `names` check rejects them as code spans, so the page describes them in words and keeps the names in the diagram only.

## Clerk

- Admitted the term fallback stack (alias fallback hierarchy), homed here.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

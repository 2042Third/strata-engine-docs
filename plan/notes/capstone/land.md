# Notes: capstone/land

## New terms

None. The page defines the ratchet and the feature test in bold; both are homed elsewhere (engineering/perf-lab, engineering/feature-test).

## Requests

- No figures file: the one picture is a Mermaid diagram (the way a change lands).
- The tutorial file `tutorials/capstone/land.tutorial.json` starts from `capstone/build`, which is not written yet. Its `tests` omit the suite Physics.WindZone, because the tutorials check cannot see the chain's patches yet; the integrator may add it.
- The page's patch (`tutorials/capstone/land.patch`, one hunk) adds the two provisional entries after `Perf.Physics.Characters1000Step`; it applies to the pin's `Budgets.json`. The exercise patch (`tutorials/capstone/land/exercise-1.patch`) applies after the page's patch, as `tutorials.py patch` applies exercises: it turns the two provisional entries into measured ones.

## Not verified

- The WindZone additions of `capstone/build` are not at the pin and not written yet: the force function and its cases (centre, scaled radius by the largest scale axis, degenerate transform), the SDK's force function, `wind.sample`, the arrow gizmo kind, the property the inactive reason disables, the suite names for the wind commands and `Scripting.API` cases, the metric names `Perf.Physics.WindZoneStep` and `Perf.Physics.WindZoneSystem`, and the system's own timing read through `GetSystem<WindZoneSystem>`.
- That the sleeping-box wake and Simulate-mode pushes pass as the page describes (the brief's list).
- `CIStatus.py status ci/windzone` resolves a local branch name: the tool's text says "a hash or a branch".
- Where the Developer Guide's "Physics" section lists parts (named "Physics" at the pin, `## Physics`).

## Findings not applied

- critic-capstone-8 (layers a zone pushes, as a mask): the page applies the scale rule (a scaled-zone case) but names no layer mask, because the chain's component has no mask property at the pin of the other pages.
- critic-capstone-11 is applied as exercise 3 without a solution patch (the Falloff exercise of `capstone/build` is not written yet); the worked solution of the page's patch exercise is the budget exercise.

## Since

Not written: the part `capstone` takes no `since`.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run

- 2026-11-24, pin 319075e3: the page's patch passed as written (chain of seven patches, Architecture.Layering, Testing.Shards, Reflection.ComponentSchema, CLI.McpToolsets and the feature test). Exercise 1's patch was written against the pin without the page's patch and did not apply; remade on top of it (provisional entries become measured ones), its answer's text follows; it passes.

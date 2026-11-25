# Notes: worlds/physics-scripts

## New terms

None. The page defines the four glossary terms of its brief (distance scale, LoadBeforeStart, MaxBodiesInRadius, world cook).

## Since

since 0.7.0: Docs/Releases/0.7.0.md lists bodies that cannot move between cells as not done, so worlds exist by 0.7.0. The release in which the World system first shipped is not checked.

## Requests

- Figure: the worlds overlay of world/systems' frame timeline (World.Streaming after the scripts, before physics, and the sub-scene slices drawing from one SceneWorkBudget) is not placed; the page carries its own Mermaid frame order instead.
- No figures file; no editor captures of world.cook or world.info (their home is editor/worlds).

## Not verified

- That the inspector clamps typed values to the registered ranges (the registration sets Min and Max; the inspector was not read).
- The table's "Who uses it" column (other engines and games) is general and not cited.
- That IsLoadedAround is true before a mesh collider's body exists: read in the code, not run.
- The release in which the World system first appeared.

## Findings not applied

- worlds-runtime:357 and scene-ecs:433 (the worlds overlay on the frame timeline): the figure belongs to world/systems; see Requests.
- worlds-runtime:111, :398 (text captures of world.cook and world.info): their home is editor/worlds.
- worlds-runtime:469, :473-477 hands-on items as a tutorial: the page has exercises (a trace of the cook, a prefetch) instead.
- Sections "What went wrong before": omitted, no history of a bug was found.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

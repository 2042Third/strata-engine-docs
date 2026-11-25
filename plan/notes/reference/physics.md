# Notes: reference/physics

## New terms

None.

## Requests

- Names or words: none outstanding.
- Generator routes (planner): the brief expects parsed tables of the body types and shapes, the physics limits, the seven scene services with their comments, and the fields of `PhysicsStats`, `PhysicsLibraryProfile` and `PhysicsLibraryCounters`. `tools/reference.py` at this commit has no such routes and `tools/reference-limits.json` holds only the scene and world constants, so the page writes these tables by hand, checked against the pin. Each could be replaced by an `::include` once a route exists.
- `src/sidebar.json`: not touched.

## Not verified

- Newton-seconds for impulses and newton-metres for torques: the engine states newtons only for `PushStrength`; the others follow from box3d's SI units.
- Mass in kilograms: stated in the engine only for the presence mass of a character; box3d is SI.
- Damping as a factor of 0 to 100: the unit is not stated at the pin, only the range and box3d's warning about large values.
- The pages linked from the table introductions (`reference/components`, `reference/settings`, `reference/commands`, `reference/script-api`) do not exist yet in this worktree.

## Findings not applied

- critic-reference-1x family (the introductions name the teaching page): applied.
- critic-reference-12 (services with comments): applied by hand as a table of functions with short descriptions, not the source comments, for lack of a generator route.

## Clerk

- Left for the planner: the generator routes for the hand-written tables.

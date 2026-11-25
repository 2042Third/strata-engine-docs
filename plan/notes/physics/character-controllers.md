# Notes: physics/character-controllers

## Since

0.3.0: the controller is part of the physics module since the first tag's scripting API (CharacterController host functions). Evidence not rechecked against the tag; the page's `since` follows the brief's "From" row (physics ch. 9).

## New terms

None proposed. The seven glossary terms of the brief are defined in bold on the page (character controller, collide and slide, step height with its alias step up, ground snapping, ground state, mover, presence body).

## Requests

- Extra word for `tools/data/extra-words.txt`: "walkable" (ground that a character can stand on; 17 uses; it is the engine's own word for the slope test).
- Picture: the stairs and slopes scene (a 0.3 m and a 0.5 m step, a 40 degree and a 50 degree slope, one controller each) cannot be taken from a sample: the Third-Person sample has one slope and no stairs. It needs a scene built for it, `project` to be made by the planner. Not placed on the page: the example's numbers carry it.
- Further reading entries cite the box3d, Jolt, Unity and Godot documentation without links; hosts to be admitted by the planner if links are wanted.

## Not verified

- box3d's `b3SolvePlanes` algorithm: the page says that for a single plane the result is the move projected onto the plane; the header only says it "solves the position of a mover that satisfies the given collision planes".
- What Unity's Character Controller, Godot's `CharacterBody3D` and Jolt's `CharacterVirtual` do internally (swept queries, contact planes), and the table's "who uses it" cells for the dynamic-capsule rows: general knowledge, not read from their sources.
- The 0.5 m step example is derived by hand from the code and the test's expectations (stops within 5 cm of one radius from the face); the exact stop position was not run.
- The 40 degree and 50 degree slopes are not built by a test (the tests use 30 and 60 degrees); the page's numbers are computed from the code's rules and the default limit of 45 degrees.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to extra-words.txt: walkable.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

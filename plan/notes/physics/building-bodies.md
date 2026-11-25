# Notes: physics/building-bodies

## New terms

None proposed. The page defines the five glossary terms of its brief in bold: body record, cooking, degenerate transform, mesh provider, suspended body.

## Requests

- Words and hosts: none requested. Further reading names four sources without a link.
- Figures: none. Both diagrams are Mermaid with caption and alt.

## Since

`since: 0.3.0`: the "Physics" scene system, change tracking through EnTT signals, shape building and bodies from components are 0.3.0 rows of the physics inventory (lines 35, 70, 75).

## Not verified

- The profiling stage name Scene.Physics is written as plain text: the `names` check does not know it at the pin, although `PhysicsRegistration.cpp` sets it.
- The statement that the default fixed step is 1/60 s is given as an example ("With a step of 1/60 s"), not as a default.
- `PhysicsTaskSystem`'s rule that a waiting thread runs an unstarted task itself is left out: only the header comment of `PhysicsWorld.h` was read.
- box3d's own counting of edges (the page follows the comment in `PhysicsMeshShapes.h`: $3V - 6$ edges for an all-triangle hull) was not read in the vendored library.
- The reference to the box3d project's documentation in Further reading names no host.

## Findings not applied

None: the brief held no open findings.

## Clerk

- Nothing asked.

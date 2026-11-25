# Notes: physics/why

## New terms

None proposed (tunneling, physics engine, rigid body, collider are defined in bold on the page; the glossary homes none here).

## Requests

- Words for extra-words or names: solver, PhysX, Havok, MIT, zlib, Erin, Catto, Massachusetts, ragdolls, buoyancy.
- Hosts for Further reading (cited without links): the Box2D and box3d repository host, Gaffer On Games (Fix Your Timestep), publishers' pages.

## Since

0.3.0: `Docs/Releases/0.3.0.md` mentions physics (Jolt then; box3d from 0.5.0).

## Not verified

- The table's "Used by" column and licences of PhysX, Havok, Jolt, Bullet and Box2D (outside the engine; cited in Further reading only).
- Winding-path layout and that the ghost boxes' sink is the Ghost layer's effect (README of the sample).

## Tutorial run

- Exercise 1 (1 round, passes): the file checked only the body type; it now does the exercise's three steps by command
  with `Crate`, the pyramid's top crate (5.506 m): lifted to 8.506 m, it lands back at 5.496 m after 90 steps; static,
  it stays at 8.506 m; without its Box Collider the log has `Physics: 'Crate' has a Rigid Body but no collider; it is
  not simulated` and it stays. The ball's shot is not done (the Playground shoots through the pointer's ray, which a
  file cannot aim at the crate without the Game view's size). The answer said the crate falls "to the floor": it falls
  back onto its stack; mended.

## Engine

None met.

## Findings not applied

- `physics:116` (shape sweeps) is named in the absences paragraph and linked to `appendix/not-in-strata`, not to a page of its own.

## Clerk

- Admitted to names.txt: PhysX, Havok, MIT, Massachusetts, zlib, Erin Catto, Catto.
- Admitted to extra-words.txt: solver, buoyancy, ragdolls.
- box2d.org entered the hosts; Gaffer On Games and the publishers were not named as hosts: left for the planner.

## Figures

- `overview` (1 round): the scene's own camera (Main Camera at 0, 22, 30) frames the whole arena in edit mode; published
  as taken, caption and alt rewritten to name what shows (crate tower and pyramid, 64 standing blocks, the glass pit
  with the ghost boxes above it, the goal's funnel over a green basket, the ramp and ten pins). The game UI is drawn
  over the left and top right; its HUD reads "Bodies: 0" because nothing plays.
- `ball-pit` (3 rounds): round 1 (camera "scene", 120 steps) showed the whole arena with the pit small and its 500 balls
  still in the neat layers they were placed in (the sample's AutoDemo starts only 2 s into play); round 2 (own camera,
  a click on Pour at step 2, 360 steps) caught the demo's own pour still falling as a flat layer; round 3 lets the
  demo's pour (at 6 s) settle until 12 s (720 steps) under a camera at 1, 12, 2 toward the pit center: the poured balls
  lie in a heap over the layers. The recipe relies on the sample's `AutoDemo` (true in the scene) to pour.
- Viewer's faults (mended in words, pictures kept): the tower is twelve 1 m crates 1 mm apart (scene, x -15), so no
  camera shows joins and the caption says it reads as one post; the ghost boxes are eight, two rows of four over the pit
  (scene's Ghost tags), now named in caption and alt; the caption says the HUD reads 0 because edit mode simulates
  nothing; the pour is all red (`BallPrefab` is `Ball.stprefab`, material RubberRed), now said in caption and alt.
- Retaken at v0.8.0 (pin 319075e3, 1 round, recipes unchanged): `overview` came out pixel-identical to its original
  (publish: unchanged, so its stamp keeps pin 822a7a46 with no new checkedAt); `ball-pit` differs in 3 pixels by 1
  level (published file diff mean 0.000), its stamp now records checkedAt 319075e3. Both still show their captions:
  the HUD reads Bodies 0 and Dominoes 0 / 64 in edit mode, and 723 bodies after 720 steps with the red pour over the
  mixed rows.

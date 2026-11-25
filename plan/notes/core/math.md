# Notes: `core/math`

## New terms

None proposed. The glossary homes no term on this page. Terms whose homes are other pages (frustum, slab, fused
multiply-add) are described in the sentence that uses them.

## Requests

- `tools/data/names.txt`: `Arvo`, `Möller`, `Trumbore` (the method of `AABB::Transformed` and the triangle test of
  `IntersectRayTriangle` are named after them in the contract section).
- `tools/external-hosts.txt`: nothing. The Further reading entries stand without links.

## Since

`since: 0.3.0`. `Strata/src/Strata/Math/Math.h` first appears in commit `938c7c9e` ("Add math, reflection and scene (ECS)
modules", 2026-10-08), which `v0.3.0` contains. `ComposeWorldTransform` came later, in `4de73aa4` ("Compose world matrices
through one compiled function", 2026-11-03).

## Not verified

- Table "Who uses it" cells ("most introductory tutorials", "some large engines", "builds that need identical numbers",
  "small programs") come from general knowledge, not from a source.
- The table's loss cell for forbidding fused multiply-adds ("Speed in all the engine's arithmetic"): the option
  `STRATA_CROSS_PLATFORM_DETERMINISTIC` exists at the pin (DeveloperGuide, Building), its speed cost was not measured.
- Further reading: the titles and levels of the four entries (Reed's "Depth Precision Visualized", Möller and Trumbore's
  paper, Arvo's chapter in Graphics Gems, the glm manual) were not fetched.
- That the scene's sweeps `Scene.Timing.Sweep` and `Scene.Transforms.Sweep` fail on GCC with `-mfma` without the fix:
  taken from the commit message of `4de73aa4`; the suites exist at the pin, the failure was not reproduced.
- That the page's description "glm stores matrices by columns" holds for every glm configuration: it is the library's
  documented layout; Strata's code indexes `transform[column][row]`.

## Findings not applied

None. The brief lists no open findings at its end.

## Clerk

- `names.txt`: Arvo, Möller, Trumbore.

# Notes: `basics/math-sphere`

## New terms

- **polar angle**: the angle between a direction and the up axis: 0 degrees for straight up, 90 for the horizon, 180 for straight down. Home: `basics/math-sphere`. Aliases: none.
- **azimuth**: the angle around the up axis, measured from +X toward +Z. Home: `basics/math-sphere`. Aliases: none.
- **equirectangular map**: a picture whose columns step evenly in azimuth and whose rows step evenly in polar angle. Home: `basics/math-sphere`. Aliases: latitude-longitude map.
- **projecting**: finding the weights of a shape's basis functions by multiplying the shape by each pattern and summing. Home: `basics/math-sphere`. Aliases: projection onto basis functions (not to be confused with the camera's projection).
- **ringing**: the rise above the true value on one side of a sharp edge and the fall below it on the other that a cut-off series of basis functions shows; it can make light negative. Home: `basics/math-sphere`. Aliases: none.

The page also defines in bold the nine terms the brief lists (basis function, hemisphere, octahedral encoding, octahedral map, solid angle, spherical coordinates, spherical harmonics, steradian, unit sphere).

## Requests

- `tools/data/extra-words.txt`: `azimuth` (also proposed as a term above) and `octahedron` (the shape of the octahedral map; 8 uses). The only two `word-list` findings left.
- `tools/external-hosts.txt`: none; the Further reading entries carry no links.
- Figures: six diagram requests in `src/content/figures/basics/math-sphere.json` (polar angle and azimuth, equirectangular map, cube map unfolded, the octahedron unfolded, a cone's solid angle, the nine patterns). None is drawn yet.
- Links to pages not yet written: `light/units-exposure`, `light/sky`, `indirect/ibl`, `indirect/probes`, `indirect/gi-cascades`, `indirect/ssr`, `basics/math-rotations`, `basics/math-change`.
- The glossary: `projecting` and `ringing` may be wanted as terms of `basics/math-sphere` for `indirect/ibl` and `indirect/probes`.

## Not verified

- The factor of about 5 between the solid angles of the pixels of an octahedral map (and 5.2 in a cube face): derived by hand (the pixel's solid angle is h^2 / r^3 with r from 1/sqrt(3) to 1 on the octahedron, from 1 to sqrt(3) on a cube face), not measured at the pin.
- That the target `c_NormalFormat` (`RG16_FLOAT`, `Strata/src/Strata/Renderer/SceneRenderer.cpp`) is the one `DepthPrepass.frag.slang` writes with `OctahedralEncode` as `o_Normal`: the names and the prepass code agree, the binding between them was not traced.
- That `indirect/probes` clamps or reshapes the coefficients (the brief's "band factors and clamping"): the page says engines do so and points there; the code of `ProbeIrradiance.comp.slang` was not read.
- The sun's angular diameter of 0.53 degrees: astronomy, general knowledge.
- The Further reading entries (titles and levels) are cited from memory and carry no links.
- The Coin Run end state (the prefab, the start position, the dome's radius): `make/project-coin-run` is not written; the script lines are `pseudocode` and the program that counts the coins is a separate sketch.
- That `Random::Range(float, float)` is uniform in [min, max) and `Scene::Instantiate(asset, translation, ...)` returns a null entity while the asset loads: read from the comments of `StrataScriptCore/Include/StrataScript/Gameplay.h` and `Scene.h`, not run.

## Findings not applied

- critic-basics-b-4 is applied: the first Slang quote is introduced by what differs from C++ and `glm` (`float2`, `.xy`, `?:`), the second by `.xy`, `.yx` and `/=`, the third by `mul` and the frame, and each quote is followed by its explanation. The rule for style.md §9.1 stays with the planner.
- critic-basics-b-15 is applied: the Coin Run item places each coin with `Scene::Instantiate` and a position, not `InstantiateMany`.
- critic-basics-b-20 names `basics/math-probability`, not this page: nothing to apply here.
- The brief's Items `new:119` and the Coin Run item: the item is the last Practice exercise, with a pseudocode loop and a separate sketch that counts the coins.
- The page has 6,475 prose words, 25 below the top of size L (the brief's fit said about 5,200): the cube map section, the Practice and the strip were cut to fit; a Basic solid-angle exercise and two try-it questions were dropped.

## Remaining pagecheck notes

- Lint: the two `word-list` findings above; 13 passive-voice and 2 noun-stack warnings left as natural wording.
- All four sketches compile and run; the sketches of the other pages are not this page's.

## Clerk

- Admitted: polar angle, azimuth, equirectangular map (alias latitude-longitude map), Projecting (basis functions), ringing.
- `extra-words.txt`: "octahedron".

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).

In Checkpoint 4 of `make/project-coin-run`, `Scripts/CoinPlacer.cpp` requests the prefab in `OnCreate` and places the coins in `OnUpdate` once it is loaded; the answer now names it.

# Notes: `basics/math-vectors`

## New terms

- **amplitude**: how far a wave reaches above and below its middle line. Home: `basics/math-vectors`. Aliases:
  amplitudes. (`basics/signals` uses it with frequency.)

The page also defines the glossary's entries that markterms reports as homed here: coordinate, radian, pi, sine,
cosine (written beside sine), tangent function, atan2, vector length, normalization, dot product, cross product,
surface normal; and in bold, as the brief's items name them: axis, origin, vector, zero vector, Pythagorean theorem,
unit vector, unit circle, projection, right-hand rule, lever arm.

## Requests

- `tools/data/extra-words.txt`: "theorem" (in "Pythagorean theorem", the brief's item `new:3`), "algebra" (the title of
  a source in Further reading, "Essence of linear algebra"), "gameplay" and "reflectance" (the link texts naming the
  pages `make/gameplay-math` and `light/reflectance`). Their word-list findings are left until then.
- "amplitude": proposed above under New terms; its word-list finding is left until the term exists.
- "normalize", "normalized", "normalizing": the lint accepts them on the page through code or the term; an alias of
  the glossary entry "normalization" would let a page say "normalize the step" in prose.
- Figures: seven diagram requests in `src/content/figures/basics/math-vectors.json` (points on the graph, adding two
  arrows, the 3-4-5 triangle, the unit circle, the sine wave, the dot product as a shadow, the right hand). None is
  drawn yet.

## Not verified

- That one unit of a Strata scene is one metre: practice 6 says "within 3 m" and "5 m" as the brief's Coin Run item
  does; the unit is `basics/math-matrices`' to state, and no engine document at the pin says it in so many words.
- Coin Run's entities: since the answers to walk G-final-7 the page names them from checkpoint 4 of
  `make/project-coin-run` (`public/downloads/tutorials/make/project-coin-run/stage-4.zip`): the ball `Ball`, the coins
  made at play by `CoinPlacer` from `Prefabs/Coin.stprefab` as children of `Coins` at the origin, and a `Coin` script
  that sets only the height of its coin.
- The `CoinMagnet` script and the `Log::Info` line are fenced as pseudocode because the sketch check compiles only
  standalone programs with glm. I checked both by hand at the pin: the script compiles with
  `g++ -std=c++20 -Wall -Wextra -fsyntax-only` against `StrataScriptCore/Include` and the pinned glm, with
  `MagnetStep` above it. That the **Console** shows "(3, 0, 4)" comes from `Log.h:33-40` (a vector is written in
  brackets, values joined by ", "), not from a run.
- The warning text: `ScriptHostAPI.cpp:247-251` reports "the translation must be finite" through
  `ScriptSystem::ReportProblem`, which logs each distinct text once (`ScriptSystem.cpp:1541-1559`); the text names the
  function (`SetWorldTransform` or `SetTransform`), the script class and the entity. The exact form of the entity's
  description (`DescribeEntity`) was not read, so the page says only that it names the script and the entity.
- `Spatial audio` in "Where the book uses it": at the pin, `AudioEngine.cpp` and `AudioSystem.cpp` use the listener's
  forward and up directions and positions; how the panning itself is computed (in miniaudio) was not read, so the line
  names only the distance and the listener's directions.

## Findings not applied

- critic-basics-b-5 (reflection): applied in idea (8), "Bouncing off a surface", with the ball against a wall,
  `glm::reflect` in the dot sketch, the unit-length normal, and practice 3. `glm::reflect` at the pin computes
  `I - N * dot(N, I) * 2` (`func_geometric.inl:124`).
- critic-basics-b-9 (default constructors): applied as a common mistake with `glm::vec3 v(0.0f)`; the pin defines no
  `GLM_FORCE_CTOR_INIT` (`Strata/vendor/CMakeLists.txt:65`, `StrataScriptCoreConfig.cmake:31`). The `Log::Info` of a
  matrix belongs to `basics/math-matrices`.
- critic-basics-b-12 (zero vector symptom, `a * b`): applied in "Common mistakes" (the message, once per entity, the
  entity stops, the length check) and in Check yourself 6.
- All three applied; none left.

## Clerk

- Admitted: the aliases "normalized" and "normalizing" of "normalization", homed here (`plan/glossary/admitted.json`).
- Refused: "amplitude" as a term: R54 lists it as school mathematics, an everyday word in its everyday sense; it is on
  `tools/data/extra-words.txt` already, as are "theorem" and "algebra".
- `extra-words.txt`: "gameplay" added (G0 has 5). "reflectance" is a word of a field: admitted as a term homed on
  `light/reflectance`, the page the link names, worded from this page's sentence.
- Figures: not the clerk's; the part's reviewer reads them.

## Walk G-final-7

- WK2: the aside at the start says that the outputs stand below the programs and that the lines of `main` run in
  `OnCreate` of the `Playground` script with `Log::Info`; practice 5 is done there. Not run: `Log::Info` of a
  `glm::vec3` is read in `Log.h:33-40`, as above.
- WK3: practice 6 names the checkpoint and the prefab steps, and the answer says why its listings are marked
  pseudocode. Checked in checkpoint 4 with the 0.8.0 package (`run2/`, `files/CoinMagnet.cpp`, the page's listings with `MagnetStep` above them): it built without a diagnostic; after `prefab.apply` and 240 fixed steps of play, the two coins within 3 m of the resting ball, at (-2, 0.8, 2) and (2, 0.8, 2), were collected and three coins were left at their places, against five without the magnet. The checkpoint's play also logs `script 'BallControl' has no field 'Speed'; the stored value is ignored`, which is `make/project-coin-run`'s, not this page's.
- Size: the page holds 6,499 prose words of 6,500. To make room, the three links of "Why you will need this" went (the
  list at the end names the pages), the items of "Where the book uses it" and four common mistakes are shorter, and
  the two asides at the start are one.

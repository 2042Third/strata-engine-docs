# Part review: capstone/plan

- contradiction: decision 3 (and the spec's decision 4 and acceptance line in `tutorials/capstone/plan.patch`) multiplied Radius by the largest axis of the world scale, so a (2, 1, 1) zone reached 10 m; `capstone/build`'s code (`WindForce.cpp`, `distance <= zone.Radius`, and the chain's unscaled sphere gizmo) never scales it; the page and the spec now say the radius never follows the scale, with its cost.
- contradiction: decision 4 (and the spec's decision 6) sorted zones and bodies by entity UUID; `capstone/build`'s system sorts nothing and relies on the registry's order and `OverlapSphere`'s deterministic order; the page and the spec now state that fixed order and its cost.
- wrong: the registry table said nothing fails for a metric without a budget; at the pin `StrataTests/Perf/Budgets.json`'s comment and the guide say the test fails before anything is measured; the row now says so.
- wrong: the four places for `#if ST_WITH_PHYSICS` named "the importers"; `AGENTS.md` names the asset pipeline; corrected.
- note: the patch change leaves the capstone stamps (plan, build, land and their exercises) not current; the public download of `plan.patch` was compiled again.

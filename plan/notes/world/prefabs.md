# Notes: `world/prefabs`

## New terms

- Slice: the part of a long job that one call does in one frame (`Scene::ContinueInstantiation` makes one slice of an
  instance's entities). Home: this page. Aliases: slices, sliced.

The brief's homed terms (prefab, template id, override, propagation, prototype, model, instance root, part, propagate,
revert, unpack) are each defined in bold once.

## Requests

- Host `dev.epicgames.com` for the Unreal Engine documentation page on Blueprint classes; the page cites it in Further
  reading without a link.

## Since

`since: 0.3.0`: prefabs, models and linked instances came in 0.3.0 (`plan/inventory/scene-ecs.md` rows 168-175: 0.3.0
for instantiation, templates, loaders and linked instances); overrides and propagation came in 0.4.0
(`Docs/Releases/0.4.0.md`, "Prefab overrides"), the subject itself is older than the first tag of the overrides.

## Not verified

- The claims about Unity (prefab instances, overrides, nested prefabs, variants) and Unreal Engine (Blueprint class
  defaults overridden by placed instances) come from the vendors' public documentation as I know it; no linked page was
  fetched. The three Unity addresses in Further reading were not fetched.
- The 17 ms and 0.3 ms per 1,000-entity prefab and the 400 KiB of a small prefab's private registry are the sentences of
  `Docs/Architecture.md` (around line 1085), not measurements of mine.
- "100,000 entities cost 30 ms" is a proportional extrapolation of the 0.3 ms figure, marked as an assumption on the page.
- The JSON shape of an entity in the worked example (`ID`, `Parent`, `Components`, a colour as three numbers) is read from
  the tests (`PrefabOverridesTests.cpp`) and the code, not from a prefab file written by the editor.
- Exercise 1's `updatedInstances` of 3 and the effect on T1, T2 and T3 are derived by reading `Propagate`, not by running
  `prefab.apply`; what `prefab.status` prints was not read.
- Which thread `EntityTemplate::Read` runs on is the header comment of `EntityPrototype.h` ("on the loading worker"), and
  the loader lambdas in `SceneRegistration.cpp`; the asset manager's scheduling was not read.
- The doctest filter `--test-suite=Scene.Prefab*` and the suites were not run.
- The Mermaid diagram was not rendered.

## Findings not applied

The brief lists no open findings. Parts of its Covers that the page treats briefly: `Compile` is described by its header
comment and the excerpt, not read line by line (`EntityPrototype.cpp` 1-257); `UpdateOverrides` and the caches
(`IndexedPartCache`, `PartChangeCache`) are named, not taught; the `Script` overrides are covered by their naming rule
and the `Revert` rule for a script field, not by a worked script example. The override computation is a worked example
(`:::example`) with the part's JSON and the records in a table, not a figure request, so the page has no figures file.

## Clerk

- Refused: Slice: "Slice (world)" is homed on `world/sub-scenes` with the same meaning (only its home words it).
- Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm).

## Walk E-final-9

Track walk E-final-9 (2026-11-24; `docs-work/walkfix-E9`, `measure.py` and `pagelines.ps1`, the official 0.8.0
package, `--no-gpu`). The Basic exercise's lines, run as the page writes them in a copy of `OpenWorld`: `prefab.create`
answers `linked: true` (the root becomes T1), each `prefab.instantiate` answers the root's `id`, `entity.get` of a
root lists the `Flame` under `children`. After the changes and `prefab.apply` of T4 (`updatedInstances` 3): T1 4/8/0.4,
T2 4/9/0.4, T3 4/8 with no `AudioSource`; `prefab.status` gives T2 one override of kind `Property` (`PointLight`,
`Range`) and T3 one of kind `RemovedComponent` (`AudioSource`), T1 none.

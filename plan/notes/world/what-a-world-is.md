# Notes: `world/what-a-world-is`

## New terms

- **archetype**: the set of component types an entity has; engines that store entities of one archetype together in one table are archetype ECS engines. Home: this page. Aliases: archetypes. Bolded once (in "Sparse sets and archetypes"); the word-list lint flags it until the glossary has it.

The page defines the glossary's ECS in bold ("entity-component system (ECS)"). It names entity, component, system and scene in plain words, because their homes lie elsewhere (the brief's term table lists only ECS); markterms marked the ones in the Needs closure. It also puts **sparse set** and **scene systems** in bold where it explains them.

## Since

`since: 0.3.0`: the scene with its EnTT registry, `IDComponent` and the scene systems belong to wave 1 (`scene-core`) per `plan/inventory/scene-ecs.md` (concept 1, "0.3.0 (wave 1 `scene-core`)").

## Requests

- Hosts for Further reading entries cited without a link: the Unreal Engine documentation (dev.epicgames.com), the flecs documentation (www.flecs.dev) and the Bevy book (bevy.org).
- Word: `archetype` (see New terms); `Flecs` is written as code, `flecs`.

## Not verified

- The claims about other engines: Unreal's `ACharacter` / `APawn` / `AActor` chain and actors holding components; Unity's `GameObject` as a container of components and DOTS archetype chunks; Bevy's and `flecs`' archetype tables; EnTT's multi-type view walking the shortest array. All come from the engines' public documentation as the writer knows it, not from the pin; the Further reading URLs were not fetched.
- The 40 bytes of `TransformComponent` is the sum of its fields (`vec3` + `quat` + `vec3` = 12 + 16 + 12), not a `sizeof` run.
- `Scene::c_MaxEntities` = 1,048,575: derived from the 20-bit index comment in `Scene.h` (`entt_traits<entt::entity>::entity_mask`), not printed by a run.
- That every `AddComponent` of a second component of one type is "refused": `Entity::AddComponent` asserts `Entity already has the component` (Debug); the page says so for Debug and says "refused" in general.
- The six scene systems registered at the pin are Animation, Audio, UI, Physics, Scripting and World streaming; the page names five of them and says "among them".

## Findings not applied

- None: the brief lists no open findings.

## Clerk

- Admitted: archetype.
- `external-hosts.txt`: `www.flecs.dev`, `bevy.org` (front pages fetched: Flecs, Bevy Engine). Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm).
- `layouts/what-a-world-is.ini`: made by the photographer (see Figures).

## Figures

- `hierarchy-inspector` (editor; published at the pin v0.8.0, 319075e3, after the `waitsFor` line was removed as
  `check` asked). The recipe opens `Scenes/Course.stscene` through the figure's `scene` field (the `scene.open` step by
  handle is gone), selects the first `BlockTall (1)` and pictures the whole 960 x 540 window with
  `layouts/what-a-world-is.ini`, a copy of `layouts/scene-hierarchy.ini` whose Hierarchy is 260 px wide.
  - Round 1, `scene-hierarchy.ini` as it was (220 px Hierarchy): the nested names were cut to "BlockTall" before the
    prefab icon, and the Inspector ends at the Rigid Body heading, so the Mesh Collider (the "collision shape" of the
    caption) lies below the panel's edge.
  - Round 2, the 260 px Hierarchy: Camera, Sun, Sky, Post Process, Course > Island A > BlockTall (1) to (8) and
    BlockTall, the first selected, then Island B, C and Pit closed; the Inspector shows the name, Transform, Mesh
    Renderer and the Rigid Body heading. The Rigid Body's 13 rows put the Mesh Collider some 450 px further down: no
    command scrolls or folds the Inspector, and a window that tall reads badly at the column's width. The caption and
    alt now name only the parts in view (name, position, mesh, body); the page's paragraph names no part, so it stays
    true. Good with the provisional build.
  - Round 3, the release build v0.8.0, the recipe unchanged: the same picture as round 2 (the selected BlockTall (1)
    reads whole, the Inspector ends at the top of the Rigid Body with its Type row). Published.

## Track walk E-final-8

WK1: a concept page has no "What you need" and no stage download (style.md §7.4 gives them to tutorials; Before you
start lists the Needs), but the page never said that it needs nothing, nor what the later pages of the part use. A
paragraph after the introduction now says: no project and no download; the exercise is a program for the compiler of
`basics/build` (linked to "Open a terminal that finds a compiler"); the figure's scene is the Course scene of the
Third-Person Adventure sample, opened as a copy with **Open Sample...**; the next pages use the installed Strata for
commands and the source build of `core/first-change` for the exercises that trace or test the engine.

# Brief: `reference/animation`

| Field | Value |
| --- | --- |
| Title | Animation reference |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `animation/state-machines` |
| From | animation ch. 15 |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/animation` — Animation reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
`Animator`, `Skin` and `AttachToJoint`, of the `animation.*` commands and of the SDK's `Animator` stand in
`reference/components`, `reference/commands` and `reference/script-api`, and this page links them by name. What only
this page holds: (1) the animation controller format (`.stanimator`, `c_FormatVersion` 1) as a hand-checked table of
its keys: parameters and their types, states with their clip, speed, loop and events, transitions with exit time,
duration and conditions, the "any state" source; checked against `AnimationController.cpp` and the sample controllers;
(2) the cooked forms "STSK" (skeleton) and "STAC" (clip), each with its version and its reader; (3) the limits, parsed:
`Skeleton::c_MaxJoints`, the clip's `c_MaxChannels`, `c_MaxKeys` and `c_MaxValues`, the controller's `c_MaxParameters`,
`c_MaxStates`, `c_MaxTransitions`, `c_MaxConditions`, `c_MaxEventsPerState`, `c_MaxSpeed` and `c_MaxDuration`, and the
animator's `c_MaxPlaying`; (4) the condition operators and parameter kinds, parsed from the enums; (5) the scene
services (`ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`), each function with its comment; (6) the glTF
importer's version as `:value{key="importer.Model.version"}`, which animated models follow. Hand-written: one
introduction per table, one line that names `animation/limits` for what the module does not do, and `## Where it lives
in Strata` (`Strata/src/Strata/Animation/`, `GltfImporter.h`). The tools are `tools/reference.py parse` and the
catalogue dumps.

**Leaves out.**

- Skeletons, clips, state machines, blending and events, as mechanisms → `animation/skeletons`, `animation/clips`,
  `animation/state-machines`, `animation/blending`, `animation/time-events`
- Root motion → `animation/root-motion`
- Importing animated models → `animation/importing`
- What Strata's animation does not do → `animation/limits`
- Animation for game makers → `make/animation`
- The perf budgets of animation → `reference/performance`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the two cooked forms,
the limits, the condition operators and parameter kinds, the three services and the importer's version, about 1,200
words. The prose is the paragraph on top, six introductions, the controller format table (about 25 keys), one line and
the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:44` | feature | link | The skeleton's cooked form "STSK" v1 |
| `animation:47` | feature | link | The clip's cooked form "STAC" v1 |
| `animation:53-55` | feature | link | The controller asset, its validation and its transitions grouped by source, in the format table |
| `animation:57` | feature | link | The animation asset types |
| `animation:68` | feature | link | The importer version that animated models follow |
| `animation:74-78` | feature | link | The three components, the clip's inactive reason and the culling mode, as names linking `reference/components` |
| `animation:85-88` | feature | link | The state machine's conditions, triggers and exit times, behind the format's keys |
| `animation:141-143` | feature | link | `ISkinningPoses`, `IAnimatorControl` and `IAnimationEventSource` |
| `animation:176-178` | feature | link | The animator host functions, `Animator` and `OnAnimationEvent`, as names linking `reference/script-api` |
| `animation:185-189` | feature | link | The `animation.*` commands and `viewport.setSettings {editPose}`, as names linking `reference/commands` |
| `animation:223` | feature | link | What is not in Strata yet, in the line that links `animation/limits` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Skeletons, clips and state machines | `animation/state-machines` | must |
| Cross-fades | `animation/blending` | helps |
| Events and loops | `animation/time-events` | helps |
| JSON values and objects | `basics/data-formats` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-12 | should | missing-item | `reference/audio-input`, `reference/ui`, `reference/worlds-runtime` | `reference/physics` and `reference/animation` list their scene services with each function's comment; the other area pages do not. So `IAudioPlayback` and `IAudioOutput`, `IUIControl` (beside the event types of `IUIEvents`), `IWorldStreaming` (a link row with no table) and the engine services `IGameWindow`, `IGameSaves` and `IGameGraphics` are on no reference page, though engine code reaches those modules only through them. | Each of the three pages adds the parsed table of its services, as `reference/physics` (4) does (about 30 words each); `reference/worlds-runtime` also takes the three engine services of `EngineServices.h`, which the runtime and the editor provide, with an introduction that names `scripting/host-api` and `worlds/runtime`. | `allocation/reference.md:564-566`, `:627-628`, `:679-691`, `:736-746`, `:788-801`, `:829`; `Strata/src/Strata/Scene/SceneServices.h:242`, `:485`, `:538`, `:552`, `:584`; `Strata/src/Strata/Core/EngineServices.h:103`, `:125`, `:152` |

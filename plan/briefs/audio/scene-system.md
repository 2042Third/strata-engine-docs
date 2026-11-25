# Brief: `audio/scene-system`

| Field | Value |
| --- | --- |
| Title | The Audio scene system |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `audio/spatial`, `world/systems`, `physics/bodies-colliders` |
| From | audio-input ch. 5; 1.4 (records, diffing without signals, asynchronous clips, listener choice, the up-vector policy, scene pause, one-shots with a 0.25 s deadline, services, inspection) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/scene-system` — The Audio scene system

**Covers.** The job: the "Audio" scene system turns entities with audio components into sources, keeps them in step
with the components every frame, chooses the listener, pauses with the scene and plays the scene's one-shots; it runs in
Play mode only, never in Simulate. The page's examples are the Physics Playground, whose `Impact.cpp` plays one-shots
with volume and pitch from the impact speed, and the Third-Person's footsteps played from animation events. In this
order: the problem of audio in an ECS (records per entity; event-driven against diffing; clips that load late; a game
that pauses) taught from zero; the map (the frame timeline with the Audio system in `OnLateUpdate` after "Scripting",
"Animation" and "Physics", and the module's update) and the record's state machine; the contract (Play mode only; game
code plays through the system, never `AudioEngine`; assets by handle, never blocking; and the guide's rule that code
working for a scene reaches assets through the scene's manager, which `AudioSystem` predates: it still reads the active
manager in five places, so its excerpt is no model for that line). Then the components as the Inspector shows them,
their registration with ranges, and the system's registration with soft order. The toy version diffs two structs and
keeps one record per entity.

The real code, in the order of one update: the records and the bitwise comparison with the last applied values, so plain
writes apply without `MarkModified` and a NaN applies once; pruning by `SeenUpdate`; the lifecycle of a source (start,
add, reactivation; removal, deactivation, destruction at once; the first update in `OnRuntimeStarted`, after the
scripts' `OnCreate`, so a script may configure a source before PlayOnStart starts it); asynchronous clips (NoClip,
Waiting, Ready, Unavailable; reported once; retried when the asset changes; reloads that replace playing clips; a new
Clip stops the source and drops a pending Play, Seek and scene pause, and Play then starts the new clip); sources placed
from the world transform every frame and at the moment of a gameplay call; the listener chosen by hierarchy order with
sibling-index paths, cached by version, and the up-vector policy (the engine has one listener: with several running
scenes the last one updated places it, and a stopping scene resets it to the origin); scene pause (edits apply before
resuming; sounds asked for while paused start on resume; steps of a paused scene stay silent); the gameplay API;
one-shots (a cap of 64 with the oldest cut off, a wait of at most 0.25 s of scene time, drops warned once per clip per
second, and the advice to request clips early); inspection; the scene service `IAudioPlayback`, the engine service
`IAudioOutput`, and how scripts reach them through the SDK and the host functions; silence without output. Then
listeners per world as an absence, the alternatives, the tests of `AudioSystemTests.cpp` and changing it safely. At the
end the reader can say when an edit to an Audio Source is heard, why a sound waits or is dropped, and which listener a
scene uses.

**Leaves out.**

- The listener's frame, attenuation and the Doppler velocity → `audio/spatial`
- Sources, voices and their races → `audio/clips-voices-sources`
- Scene systems, phases and scene services in general → `world/systems`
- Play and Simulate as editor modes → `editor/play-mode`
- The host-function pattern and `ReportProblem` → `scripting/host-api`
- What a game maker does with sounds (the coin sound, requesting clips in `OnCreate`) → `make/sound`

**Fit.** `fits`: about 6,300 words against L (5,000). The system's features, its services and the script side (about
1,700 words) and the one-shots with their excerpt, concept, figures and rule (about 870) take the most; the estimate
stands about 200 words below L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:73-78` | feature | home | The two components and their ranges, the "Audio" system and its order, the source lifecycle (the first update in `OnRuntimeStarted`, after the scripts' `OnCreate`, so a script may configure a source before PlayOnStart starts it: `Strata/src/Strata/Audio/AudioSystem.h:116`, `Strata/src/Strata/Audio/AudioSystem.cpp:161-167`), asynchronous clips (a new Clip stops the source and drops a pending Play, Seek and scene pause; Play then starts the new clip: `ResolveClip`, `Strata/src/Strata/Audio/AudioSystem.cpp:538-549`), change detection without signals, spatial sources |
| `audio-input:80-88` | feature | home | Listener selection (the engine has one listener: with several running scenes the last one updated places it, and a stopping scene resets it to the origin facing -Z: `Strata/src/Strata/Audio/AudioSystem.h:86-87`, `Strata/src/Strata/Audio/AudioSystem.cpp:169-181`), the up-vector policy, scene pause, the gameplay API, scene one-shots, inspection, `IAudioPlayback`, `IAudioOutput`, silence without output |
| `audio-input:94-96`, `scripting:127` | feature | home | The SDK's `AudioSource` and `Audio` (`StrataScriptCore/Include/StrataScript/Audio.h:16-120`), one entry with the scripting inventory's `AudioSource`, `Audio`, passed by `scripting` (R31, D26); and the ten audio host functions with the misuse they report |
| `audio-input:100` | feature | home | The samples as examples: Physics Playground's impacts, Third-Person's footsteps with random pitch, Tetris |
| `audio-input:278` | concept | home | A9: audio in a scene, diffing against events, Play mode only, the service instead of an include |
| `audio-input:286` | concept | home | A10: fire-and-forget sounds and a latency budget |
| `audio-input:402` | code | home | `Strata/src/Strata/Audio/AudioSystem.cpp:717-746`: records, `SeenUpdate` and pruning; with `ApplyComponent`, `:510-536`, and the bitwise comparison, `:32-36` |
| `audio-input:403` | code | home | `Strata/src/Strata/Audio/AudioSystem.cpp:834-864`: the listener by hierarchy order, cached by version; with the up-vector policy and the paths, `:67-96` |
| `audio-input:404` | code | home | `Strata/src/Strata/Audio/AudioSystem.cpp:869-966`: one-shots, the wait with a deadline and the accounting of drops |
| `audio-input:430` | figure | home | Diagram: the record's states NoClip, Waiting, Ready and Unavailable, with `PlayRequested`, `PausedByScene` and `PendingSeek`, and the reload edge |
| `audio-input:438` | figure | home | Diagram: a one-shot's life (request, wait of at most 0.25 s, playing, reclaimed) and its drops |
| `audio-input:440` | figure | home | Diagram: the frame with the Input stage, the scene systems (Audio last, in `OnLateUpdate`) and the module's update; `input/devices-state` uses it |
| `audio-input:469` | figure | home | Screenshot: the Inspector with Audio Source and Audio Listener, from the Physics Playground |
| `audio-input:481` | figure | home | Screenshot: the Console's warning of a dropped one-shot |
| `audio-input:490` | rule | home | Game code plays sound through `AudioSystem` (scripts: the SDK), never `AudioEngine` |
| `audio-input:505` | rule | home | Request clips before you need them |
| `audio-input:513-515` | rule | home | Audio plays only in Play mode; assets by handle, never blocking. The same rule of the guide says that code working for a scene reaches assets through `Scene::GetAssetManager()`, never `AssetManager`'s static functions (`Strata/src/Strata/Scene/Scene.h:601-607`, `Docs/DeveloperGuide.md:985-990`); `AudioSystem` predates it and still reads `AssetManager::GetActive()` in five places and goes through the scene in one (`Strata/src/Strata/Audio/AudioSystem.cpp:141, 554, 613, 750, 908`; `:443`), so the excerpt of `audio-input:404` is no model for that line; the page says what the pin does (R34) |
| `audio-input:408` | code | use | `Strata/src/Strata/Audio/AudioComponents.cpp:11-30`, `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1631-1653` and `Samples/PhysicsPlayground/Scripts/Impact.cpp:55-61` |
| `audio-input:405` | code | use | The scene system's registration with `AfterIfPresent` |
| `audio-input:401` | code | use | `UpdateMotion`, called from `UpdateSourcePosition` |
| `audio-input:543` | rule | use | Host functions report misuse and return failure values (home `scripting/host-api`) |
| `audio-input:651-652` | term | use | Scene system; scene service and engine service (home `world/systems`) |
| `audio-input:654` | term | use | Play mode and Simulate mode (home `editor/play-mode`) |
| `new:8` | not-done | home | Listeners per world: one listener for the whole engine; how engines mix several listeners or split screens. Evidence: `Docs/Roadmap.md:1707`; `Strata/src/Strata/Audio/AudioEngine.cpp:187` (`listenerCount = 1`) |
| `new:25` | hands-on | home | Exercises (D27): a doctest case beside "Component changes apply while playing, with or without a signal" that changes a playing source's Clip and checks that the source stops and that Play starts the new clip, predicted first (predict, then run; a patch: done); a breakpoint in `AudioSystem::DropOneShot` while many one-shots of a clip that is not loaded are asked for shows the drops counted and one warning per clip per second (trace); one listener per world for a split-screen game (design). Evidence: `StrataTests/src/Audio/AudioSystemTests.cpp:328`; `Strata/src/Strata/Audio/AudioSystem.cpp:538-549` (`ResolveClip`), `:435-441` (`DropOneShot`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Scene systems, their phases (`OnLateUpdate`) and their order | `world/systems` | must |
| Scene services | `world/systems` | must |
| Entities, components and EnTT views | `world/ecs` | must |
| The hierarchy, activity in the hierarchy and the hierarchy version | `world/scene-graph` | must |
| Change signals (`MarkModified`), which this system does without | `world/scene-graph` | must |
| Components registered through reflection, with ranges | `world/reflection` | must |
| Asset states, `GetAsset` every frame and content versions | `assets/loading` | must |
| The listener, panning, attenuation and the Doppler velocity | `audio/spatial` | must |
| Sources and voices | `audio/clips-voices-sources` | must |
| Requesting assets early, and pins | `assets/residency` | helps |
| Asset reloads | `assets/importing` | helps |
| A scene's pause | `world/systems` | helps |
| Play and Simulate | `editor/play-mode` | helps |
| The primary camera | `world/scene-graph` | helps |
| A body's velocity at a point | `physics/bodies-colliders` | helps |
| Host functions, `HostCall` and `ReportProblem` | `scripting/host-api` | helps |
| Script callbacks (`OnCollisionEnter`, `OnAnimationEvent`) | `scripting/script-system` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

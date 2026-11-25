# Brief: `audio/engine`

| Field | Value |
| --- | --- |
| Title | The audio engine |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `basics/threads`, `core/frame-loop`, `core/engine-modules`, `audio/sound-in-a-computer` |
| From | audio-input ch. 2; 1.1 (`AudioEngine`, miniaudio, the null-device fallback, master volume, the real-time rules and the sequence lock, the engine module) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/engine` — The audio engine

**Covers.** The job: `AudioEngine` owns miniaudio's mixer and the output device, the one listener, the master volume and
the engine's fire-and-forget voices; it knows nothing of scenes. The page's example is the Physics Playground's impact
sound on its way to the speaker, and the same game started with `--headless`, where there is no device. In this order:
the map (the audio stack from a component to the device, with scripts entering through `IAudioPlayback` and master
volume through `IAudioOutput`) and the two threads, main and mixing, with what crosses between them; the contract (the
API is main-thread only, mixing runs on miniaudio's thread). Then two concepts from zero: the real-time rules (never
block, allocate or log on the audio thread; atomics; whole values published through a sequence lock; destroy what the
reader uses only after it let go) and mixing (voices summed in a node graph, master gain, voice limits and stealing). The
toy version is a mixer of two sine voices pulled by a callback.

The real code follows a program's life: `AudioModule` (initialize, advance the null device by the frame step, reclaim
one-shots, shut down after the job system) and the module's registration; `Init` with its validation, the device, the
fallback to the null device and the one failure that fails `Init`; what happens when the device goes away during play,
which Strata leaves to miniaudio (the writer reads it in the vendored source first); master volume, pause and the
settings kept before `Init`; `AdvanceNullDevice` in chunks with fractions carried over, called by `AudioModule::OnUpdate`
and not by the Application that the header's comment names; engine one-shots with their cap and oldest-first stealing;
the listener's up vector handed to the mixing thread through `SequenceLockedValue` in `onProcess`, of which the page
quotes the use and links the lock's own code on `core/jobs`; statistics; the build option `STRATA_WITH_AUDIO`; in one
sentence with a link to `editor/play-mode`, the editor restoring the master volume when play stops. Then the alternatives
(push queues, a mutex for the hand-off, middleware with buses), what Strata does not do (buses, effects, reverb, HRTF),
how it is tested (the up-vector test of `AudioTests.cpp`) and changing it safely (AGENTS.md's "Audio" rule, atomics for
what the audio thread reads). At the end the reader can trace a sound from the API to the device and explain why the up
vector travels through a sequence lock while the volume does not.

**Leaves out.**

- Clips, voices and sources, and the order in which voices are released → `audio/clips-voices-sources`
- The listener's frame, panning and attenuation → `audio/spatial`
- The scene's one-shots, which game code uses instead of the engine's → `audio/scene-system`
- Testing on the null device → `audio/testing`
- Threads, atomics and memory order in general → `basics/threads`
- The sequence lock's own code (`SequenceLock.h`) and the term → `core/jobs`
- The editor keeping its master volume at Play and restoring it at Stop → `editor/play-mode`
- Engine modules and engine services in general → `core/engine-modules`
- Optional modules and `ST_WITH_*` → `core/layers-registries`

**Fit.** `fits`: about 5,550 words against L (5,000). Five excerpts with the lock's use (about 1,200 words) and the two
concepts from zero (about 800) take the most; the three exercises add about 600.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:27-32` | feature | home | `Init` and its validation, the device fallback, the null device (`ReadFrames`, `AdvanceNullDevice`), master volume, engine pause, settings kept before `Init` |
| `audio-input:34-35` | feature | home | The listener's up vector handed to the mixing thread; engine one-shots, `MaxOneShots` 128 and stealing of the oldest |
| `audio-input:37-39` | feature | home | `AudioStats`; `AudioModule`, listed by the editor and the runtime, with `NullDevice` for `--headless` and `--no-gpu`; `STRATA_WITH_AUDIO` |
| `audio-input:97` | feature | use | The editor keeps the master volume at Play and restores it at Stop, in one sentence with a link (home `editor/play-mode`, critic-audio-input-12) |
| `audio-input:229` | concept | home | A3: the real-time rules and lock-free hand-off; the finished-voice race is named and left to `audio/clips-voices-sources` |
| `audio-input:247` | concept | home | A5: voices summed in miniaudio's node graph, master gain, voice limits and oldest-first stealing; sums above 1 clip |
| `audio-input:396` | code | home | `Strata/src/Strata/Audio/AudioEngine.cpp:62-71`: the use of the sequence lock, `ApplyPendingWorldUp` taking a new up vector on the mixing thread after each period; with the writer's side, `SetListener` publishing it, `:320-349`. The lock's own code (`SequenceLock.h`, `foundation:361`) is `core/jobs`' excerpt, linked (R31, "The sequence lock") |
| `audio-input:397` | code | home | `Strata/src/Strata/Audio/AudioEngine.cpp:162-223`: validation first, then the device, the null device, and failure only when the mixer cannot be made |
| `audio-input:398` | code | home | `Strata/src/Strata/Audio/AudioEngine.cpp:124-158`: an engine one-shot, the cap and stealing of the oldest |
| `audio-input:405` | code | home | `Strata/src/Strata/Audio/AudioRegistration.cpp:28-49`: what the module registers (components, `IAudioOutput`, the clip loader, the scene system with soft order); the page's map |
| `audio-input:408` | code | home | `Strata/src/Strata/Audio/AudioModule.cpp:19-40`: the engine module. The item's other snippets are used by `audio/scene-system` (`AudioComponents.cpp:11-30`, `ScriptHostAPI.cpp:1631-1653`, `Impact.cpp:55-61`) and `input/rebinding` (`ScriptHostAPI.cpp:2961-2991`); `Gameplay.h:178-219` (`KeyRepeat`) goes with `audio-input:174` |
| `audio-input:419` | figure | home | Diagram: the audio stack, component to device, with `AudioClip` beside it and the two services |
| `audio-input:422` | figure | home | Diagram: the two threads and what crosses them (atomic cursor, atomic bus volume, the sequence-locked up vector, `ma_sound_uninit` waiting) |
| `audio-input:492-494` | rule | home | The audio API is main-thread only; never write a value the audio thread reads without atomics |
| `audio-input:583` | hands-on | home | Exercise: audio buses as a design (groups, an engine service, the ABI's append rule) |
| `audio-input:587` | hands-on | home | Exercise: the hand-off with a mutex in a scratch branch, and why that is wrong on the audio thread |
| `audio-input:618-621` | term | home | One-shot (first met as the engine's), voice stealing, node graph, bus or group |
| `audio-input:626-627` | term | home | Output device, null device |
| `audio-input:632` | term | home | Lock-free |
| `audio-input:750` | open | home | Settled at the pin by `new:2`: nothing outside the tests calls `AudioEngine::SetPaused` |
| `audio-input:753` | open | home | A minimized window skips whole frames (`Strata/src/Strata/Core/Application.cpp:307-312`), so modules and scenes stop while the device thread may keep mixing: the writer checks what is heard before the page says anything; the gamepad half is used by `input/gamepads` |
| `audio-input:33` | feature | use | `SetListener`'s validation and the up vector, as the caller of the hand-off; the listener is `audio/spatial`'s |
| `audio-input:84` | feature | link | The scene's one-shots, which game code uses |
| `audio-input:490` | rule | link | Game code plays sound through `AudioSystem`, never `AudioEngine` |
| `audio-input:634` | term | use | Atomic (home `basics/threads`) |
| `audio-input:633` | term | use | Sequence lock, said in one sentence where the up vector crosses to the mixing thread (home `core/jobs`, one glossary entry with `foundation:600`) |
| `new:1` | not-done | home | Buses, effects, reverb and HRTF: a voice sets only its own output volume; how middleware does it, with a link to `appendix/not-in-strata`. Evidence: `git grep -niE "ma_sound_group\|reverb\|hrtf\|filter" 822a7a46 -- Strata/src/Strata/Audio` finds nothing (no group, reverb, HRTF or filter node); `Strata/src/Strata/Audio/AudioVoice.cpp:304-311`; `Docs/Roadmap.md:1712` |
| `new:2` | erratum | home | The comment of `AudioEngine::SetPaused` says it pauses output "e.g. while the editor pauses the game"; at the pin only tests call it, and the editor pauses audio through the scene (`AudioSystem::OnPausedChanged`). The page states the code's fact. Evidence: `Strata/src/Strata/Audio/AudioEngine.h:70-72`; `git grep -n "AudioEngine::SetPaused" 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the definition `Strata/src/Strata/Audio/AudioEngine.cpp:296` and a comment at `Strata/src/Strata/Audio/AudioSource.h:78`; the tests call it (`StrataTests/src/Audio/AudioTests.cpp:148`, `:208`); the editor pauses the playing scene (`StrataEditor/src/Editor/EditorContext.cpp:1568`); `Strata/src/Strata/Audio/AudioSystem.cpp:203-247` |
| `new:3` | feature | home | The vendored miniaudio is 0.11.25, built with stb_vorbis in one translation unit, only when `STRATA_WITH_AUDIO` is on. Evidence: `Strata/vendor/miniaudio/miniaudio.h:3748-3750`; `Strata/vendor/CMakeLists.txt:133-142` |
| `new:16` | erratum | home | The comment on `AudioEngine::AdvanceNullDevice` says that "the Application calls it every frame while mixing without a device"; `AudioModule::OnUpdate` calls it with the frame's step while no output device pulls the mix, and the Application calls no module code. The page names the real caller. Evidence: `Strata/src/Strata/Audio/AudioEngine.h:98-101`; `Strata/src/Strata/Audio/AudioModule.cpp:29-35`; `AGENTS.md:218-219` |
| `new:17` | open | home | Check: What miniaudio does when a device is lost. The claim: the fallback to the null device covers only a device that is missing at `Init`; Strata registers no device notification, so what happens when the output device goes away during play (headphones unplugged) is miniaudio's and may differ by backend. The writer of `audio/engine` reads miniaudio's default-device handling in the vendored source, and the page's one or two sentences on it replace this item; the page's brief waits for the result (R39). Evidence: `Strata/src/Strata/Audio/AudioEngine.cpp:85-117`, `:186-223`; `git grep -n -i notification 822a7a46 -- Strata/src/Strata/Audio` finds nothing; the vendored source, `Strata/vendor/miniaudio/miniaudio.h` |
| `new:23` | hands-on | home | Trace it yourself (D27): a breakpoint in `AudioEngine::AdvanceNullDevice` in a `--headless` run, which mixes on the null device, shows its caller, `AudioModule::OnUpdate` with the frame's step (not the Application that the header's comment names, `new:16`), and the chunks it mixes and discards. Evidence: `StrataRuntime/src/RuntimeApplication.cpp:485`; `Strata/src/Strata/Audio/AudioModule.cpp:29-35`; `Strata/src/Strata/Audio/AudioEngine.cpp:429-448` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Samples, frames, the mixer, the pull model and the audio thread | `audio/sound-in-a-computer` | must |
| Threads, data races, atomics and memory order | `basics/threads` | must |
| The sequence lock (`SequenceLockedValue`): a writer bumps a counter around a write, a reader retries if it changed | `core/jobs` | must |
| Engine modules (`OnInit`, `OnUpdate`, `OnShutdown`) and their order | `core/engine-modules` | must |
| Engine services | `core/engine-modules` | must |
| The frame loop and the frame's step | `core/frame-loop` | must |
| The composition root, registries and `Register<Module>Module` | `core/layers-registries` | must |
| Optional modules (`ST_WITH_*`) | `core/layers-registries` | helps |
| Ownership with `Scope` and `Ref`; RAII | `basics/cpp-memory` | must |
| Errors returned and logged, never thrown | `core/conventions` | helps |
| Scene systems and their order | `world/systems` | helps |
| Components registered through reflection | `world/reflection` | helps |
| Asset loaders and their registry | `assets/importing` | helps |
| Calling a C library from C++: C structs, configuration structs and result codes | `basics/cpp-generic` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `bus` | Bus | - |
| `node-graph` | Node graph | - |
| `null-device` | Null device | - |
| `one-shot` | One-shot | - |
| `output-device` | Output device | - |
| `voice-stealing` | Voice stealing | - |

# Allocation: audio-input

## `audio/sound-in-a-computer` — Sound inside a computer

**Covers.** The page starts with the problem as a reader meets it: a speaker cone moves smoothly, but a computer stores
numbers. Its example is one clip of the Physics Playground, `Samples/PhysicsPlayground/Assets/Sounds/Impacts/Wood.ogg`,
followed from the file to the speaker; the same clip comes back on the later pages of the part. In this order the page
teaches: sampling and the sample rate (Nyquist's limit in one sentence, with a link to `basics/signals`); sample values
from -1 to 1 (16-bit integers in files, 32-bit floats in a mixer); channels, the audio frame (one sample of every channel,
not a rendered frame) and interleaving (`L R L R`); the size of PCM (one minute of stereo float at 48 kHz is about
23 MB); gain as a multiplier, decibels (-6 dB is about half the amplitude) and clipping when a sum leaves [-1, 1]; a
mixer that sums voices into one stream, one mixing period at a time; the pull model, in which the device's audio thread
asks for the next period, against the push model of queued buffers; buffer size against latency, and an underrun heard
as a click.

Then the approaches: a table of FMOD, Wwise, OpenAL Soft, XAudio2, the platform APIs and miniaudio, with their model
(pull or push), what they include and who uses them. Strata's choice and its reason: miniaudio, one portable C file with
a node graph, decoders and a spatializer, which pulls on its own thread; Strata mixes float stereo at 48 kHz and lets
every clip keep its own rate and channel count. What the choice does not give: no authoring tool and no buses (one
sentence, linking `audio/engine` and `appendix/not-in-strata`). Common mistakes: frames counted as samples, "louder" made
by adding instead of multiplying, slow work on the audio thread, and a period expected to line up with a game frame. At
the end the reader can compute the size of a clip and the length of a period, and say what a mixer does in each period.

**Leaves out.**

- Strata's `AudioEngine`, the null device and the rules of the audio thread → `audio/engine`
- Codecs, decoding and load modes → `audio/clips-voices-sources`
- Panning, attenuation and the Doppler effect → `audio/spatial`
- Logarithms and decibels as mathematics → `basics/numbers`
- Sampling theory and aliasing → `basics/signals`

**Fit.** `fits`: about 3,500 words against M (3,000). The concepts from zero, with the mixer and the pull model (about
1,250 words), take the most, then the exercises of `new:22` (about 550) and the table of approaches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:215` | concept | home | A1: sampling, sample values, channels, frames and interleaving; gain multiplies and loudness is logarithmic; Strata mixes float stereo at 48 kHz (`Strata/src/Strata/Audio/AudioEngine.h:22-23`) and clips keep their own rate (`AudioClip.cpp:92-94`) |
| `audio-input:222` | concept | home | A2: the pull model and its thread, buffer size against latency, underruns; push queues (XAudio2, OpenAL) as the other approach |
| `audio-input:296` | concept | home | A12: the landscape table and why Strata took miniaudio (`Strata/vendor/CMakeLists.txt:133`) |
| `audio-input:426` | figure | home | Diagram: the device pulling periods of about 10 ms against game frames of 16.7 ms, and an underrun; the cursor's lead over the audible sample is named here and taught in `audio/clips-voices-sources` |
| `audio-input:748` | open | home | The period's length depends on the backend: the page gives no fixed number, only that the tests assume about 11 ms at 48 kHz (`StrataTests/src/Audio/AudioTestUtils.h:25-26`) |
| `audio-input:606-611` | term | home | Sample, sample rate, channel, frame (audio), interleaved, PCM |
| `audio-input:615-616` | term | home | Mixer and voice in general; Strata's `AudioVoice` is `audio/clips-voices-sources`' |
| `audio-input:622-623` | term | home | Gain; decibel |
| `audio-input:625` | term | home | Clipping |
| `audio-input:628-631` | term | home | Mixing period, underrun, latency, audio thread |
| `audio-input:247` | concept | link | The node graph and voice limits, named with a link to `audio/engine` |
| `new:22` | hands-on | home | Exercises (D27): the bytes of one minute of 16-bit stereo at 44.1 kHz against 32-bit float stereo at 48 kHz, and the milliseconds of a period of 480 and of 512 frames at 48 kHz (computation); a sketch that sums two sine voices of amplitude 0.6 at 48 kHz, prints the peak and counts the samples outside [-1, 1], then lowers both gains by 6 dB and counts again, each result predicted first (predict, then run; a sketch with its output: done); why a mixer that waits for a lock on the audio thread is heard as a click (design). Evidence: `Strata/src/Strata/Audio/AudioEngine.h:22-23` (48 kHz, 2 channels); `StrataTests/src/Audio/AudioTestUtils.h:25` (a mixing period of about 11 ms at 48 kHz) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Powers, logarithms and decibels | `basics/numbers` | must |
| Floating-point numbers, integers of 16 bits and their ranges | `basics/numbers` | must |
| Sampling, the Nyquist limit and aliasing | `basics/signals` | must |
| A thread: code that runs at the same time as other code | `basics/threads` | helps |
| A function handed to a library to be called later (a callback) | `basics/cpp-generic` | helps |
| A queue | `basics/data-structures` | helps |
| One frame of a game, in milliseconds | `start/what-an-engine-is` | helps |

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

## `audio/clips-voices-sources` — Clips, voices and sources

**Covers.** The job: a clip (`AudioClip`) is immutable sound data shared by any number of voices; a voice
(`AudioVoice`) is one playing instance in miniaudio's node graph; a source (`AudioSource`) is a voice with remembered
settings that a game controls. The page's example is the Physics Playground's `Wood.ogg` as a Decompressed clip played by
several voices at once, beside a long music file as a Streamed clip. In this order: codecs and the choice per asset
(decode at load or decode while playing; what PCM costs); decoding WAV, FLAC, MP3 and Ogg Vorbis with `ma_decoder` to
float at the file's own rate and channel count, so resampling happens per voice; decoding in chunks of 16,384 frames
instead of trusting a header's length; clips loaded on worker threads and shared freely; memory accounting; the cooked
"STAU" form, the loader and the importer (files over 1 MiB start Streamed; the import settings); the memory layout of the
two load modes.

Then voices: the toy version (a voice as a cursor over shared frames); the custom data source (a C-style table of
functions, the standard-layout asserts, zero-copy reads, the cursor mirrored in an atomic, the end reported with the
last frames so loops wrap within one read, a decode error counted as the end); the voice object and the order in which it
is destroyed while a real-time thread reads it; the source registry, which lets `Shutdown` release every voice before
the engine; volume through the atomic bus volume. Then sources: remembered settings that work before `Init` and after
`Shutdown`; Play, Pause, Stop and Seek; a position that runs ahead of what is heard by up to one period; the state
machine; the two races with the audio thread and their fixes (a finished voice is replaced, never restarted; a voice that
played is replaced on Stop and Seek); input validation. Then what Strata does not do (virtual voices and priorities;
streaming from disk or packs), the alternatives, how it is tested and changing it safely. At the end the reader can
choose a load mode for a sound and defend it, and draw both races as a timeline of the two threads.

**Leaves out.**

- The mixer, the audio thread's rules and the sequence lock → `audio/engine`
- Attenuation models and the listener → `audio/spatial`
- The components and the scene's records of sources → `audio/scene-system`
- Import records, importer versions and background imports in general → `assets/importing`
- Untrusted input and bounded sizes in general → `assets/robustness`
- Residency and when a clip may be evicted → `assets/residency`

**Fit.** `fits`: about 5,850 words against L (5,000). Five excerpts, two of them the races (about 1,250 words), the
two concepts from zero (about 800) and four rules take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:36` | feature | home | The source registry: an intrusive list of plain pointers, so sources with static storage unregister in any order; `Shutdown` releases their voices before the engine (`Strata/src/Strata/Audio/AudioEngine.cpp:56-60, 240-246`) |
| `audio-input:45-52` | feature | home | Decoding, the two load modes, safe decoding, thread safety, memory accounting and `IsDataShared`, the "STAU" form, the clip loader, the importer (`.wav .mp3 .flac .ogg`, `LoadMode`, version 1) |
| `assets:159` | feature | home | The audio importer as the assets inventory lists it, one entry with `audio-input:52`, passed by `assets` (critic-assets-11): `.wav .mp3 .flac .ogg` validated by opening the file as streamed, cooked with the encoded file kept (`AudioClipAsset::Cook`), `LoadMode` Decompressed or Streamed with files over 1 MiB starting Streamed (`Strata/src/Strata/Asset/AssetImporters.cpp:82-137`); `assets/importing` keeps a row of its table of importers |
| `audio-input:58-61` | feature | home | The custom data source, end handling, the voice object and its destruction order, volume through the atomic output bus |
| `audio-input:63-67` | feature | home | `AudioSource` and its settings, Play, Pause, Stop and Seek, finished-voice replacement, a fresh voice after a stop, input validation |
| `audio-input:239` | concept | home | A4: codecs, decoding and streaming from memory; resampling per voice; a header's length is not trusted |
| `audio-input:255` | concept | home | A6: sources and their state machine; the position runs ahead by up to one period |
| `audio-input:392` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:20-77`: the data source over a clip, its asserts, zero-copy reads, the atomic cursor and the end for loops; with its table of functions, `:126-134` |
| `audio-input:393` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:138-164`: the sound is released first, because `ma_sound_uninit` waits for the audio thread, then the decoder and the data source |
| `audio-input:394` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:241-260`: why a finished voice is not restarted; with `Strata/src/Strata/Audio/AudioSource.cpp:39-54`, the replacement and the one retry |
| `audio-input:395` | code | home | `Strata/src/Strata/Audio/AudioSource.cpp:269-288`: a voice that played holds a period of old audio, so Stop and Seek replace it |
| `audio-input:399` | code | home | `Strata/src/Strata/Audio/AudioClip.cpp:33-58`: decoding an untrusted file chunk by chunk instead of sizing the buffer from its header |
| `audio-input:424` | figure | home | Diagram: interleaved frames shared by N voices with N cursors (Decompressed) against encoded bytes with one decoder per voice (Streamed); memory and CPU of each |
| `audio-input:428` | figure | home | Diagram: the state machine of a source and its voice (no clip, no voice, stopped, playing, paused, ended and replaced, inert after `Shutdown`) |
| `audio-input:473` | figure | home | Screenshot: the import settings of an audio clip, `LoadMode` with its tooltip |
| `audio-input:497-503` | rule | home | Release the sound before what it reads, and every voice before the engine; replace a finished voice; replace a voice that played; never trust a file's declared length |
| `audio-input:585` | hands-on | home | Exercise: distance culling and virtual voices, after the absence they answer |
| `audio-input:589` | hands-on | home | Exercise ("trace it yourself"): `AudioVoice::Start` and `AudioSource::Play`'s retry on a timeline of both threads |
| `audio-input:612-614` | term | home | Codec or decoder; WAV, FLAC, MP3, Ogg Vorbis; resampling |
| `audio-input:617` | term | home | Source (the class, and the component that describes one) |
| `audio-input:635-637` | term | home | Data source (miniaudio), cursor, load mode |
| `audio-input:647` | term | home | Pitch |
| `audio-input:638` | term | use | Cooked asset (home `assets/what-is-an-asset`) |
| `new:4` | not-done | home | Virtual voices and voice priorities: every playing voice is mixed; how engines virtualize inaudible voices. Evidence: `git grep -niE "virtual\|priorit" 822a7a46 -- Strata/src/Strata/Audio` finds nothing |
| `new:5` | not-done | home | Streaming from disk or packs: a Streamed clip decodes encoded bytes held in memory. Evidence: `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1712` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The `AudioEngine`, its mixer, the node graph and the audio thread | `audio/engine` | must |
| Samples, frames, channels, interleaving and mixing periods | `audio/sound-in-a-computer` | must |
| Import records, importer settings and versions | `assets/importing` | must |
| Asset loaders and loading off the main thread | `assets/loading` | must |
| Atomics and relaxed memory order | `basics/threads` | must |
| Destructors, RAII and unique ownership | `basics/cpp-memory` | must |
| Virtual calls and tables of functions | `basics/cpp-classes` | must |
| Standard-layout types and `offsetof` | `basics/bytes` | helps |
| Untrusted input and bounded sizes | `assets/robustness` | helps |
| Residency: an asset that something still holds | `assets/residency` | helps |
| What a cooked form of an asset is | `assets/what-is-an-asset` | helps |

## `audio/spatial` — Sound in space

**Covers.** The job: how a sound comes from where its source is (the listener, panning and distance attenuation) and how
its pitch follows motion (the Doppler effect), with the velocities Strata derives for it. The page's example is the
Physics Playground's impact sound heard from where two bodies hit, and a rolling ball that passes the listener. In this
order: the listener (position, forward, up and velocity; right = forward × up; the engine's frame, right-handed with +Y up
and -Z forward; zero vectors and NaNs refused at the boundary) and the listener-frame diagram; panning by the source's
angle (pan laws for stereo; HRTF for headphones and surround named); attenuation from the physical 1/r: the four models,
minimum and maximum distance, rolloff, OpenAL's "clamped" models, and the plot of the curves; the toy version (an inverse
gain and a pan from one dot product); the real code of `SetAttenuation` (`NoAttenuation` mapped to inverse with rolloff
0 because miniaudio's "none" also turns off panning and Doppler; the minimum distance kept above 0.01; a maximum below
the minimum treated as the minimum; the name `NoAttenuation`, because X11 defines `None`).

Then the Doppler effect from zero: the shift from the relative velocity along the line between source and listener,
the speed of sound, why it grows without bound near that speed, and why a velocity is per second, never per frame. The
two ways to get a velocity (from physics, or from moves over time) and Strata's derivation: the body's velocity limited
to 150 units/s; otherwise the move over the time since the last move, smoothed with `1 - exp(-t / 0.1)`; a teleport
gives no velocity; still for two fixed steps means stopped. A timeline shows fixed steps at 60 Hz against frames at
144 Hz. The vendored miniaudio decides the pan law, the gain smoothing, the Doppler factor and the speed of sound: the
writer reads them in `Strata/vendor/miniaudio` before stating them. Then what Strata does not do (occlusion and reverb
zones; a model chosen per component), the alternatives, the tests and changing it safely. At the end the reader can
predict the gain of a source at a distance under each model, and explain why a velocity measured per frame jitters when
fixed steps and frames run at different rates.

**Leaves out.**

- The records that place sources every frame and choose the listener → `audio/scene-system`
- The sequence lock that carries the up vector → `audio/engine`
- Vectors, dot and cross products → `basics/math-vectors`
- Exponential smoothing as mathematics → `basics/math-interpolation`
- Rigid bodies and their velocities → `physics/bodies-colliders`
- The RMS test method → `audio/testing`

**Fit.** `over`: about 4,500 words against M (3,000). Two concepts from zero (the listener, panning and attenuation;
the Doppler effect: about 1,050 words), two excerpts, three figures, three rules, two absences and two exercises go past
M's top. Proposed: L (5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:33` | feature | home | The listener: position, forward, up and velocity; non-finite and zero vectors refused; right-handed, +Y up, -Z forward, which are miniaudio's own defaults |
| `audio-input:62` | feature | home | The four attenuation models clamped to [Min, Max]; `NoAttenuation` as inverse with rolloff 0; the minimum distance above 0.01 |
| `audio-input:79` | feature | home | Doppler velocity from the simulating body or an ancestor's (`IBodyMotionQuery::GetPointVelocity`), else from moves; the limit, the smoothing, teleports and stops |
| `audio-input:261` | concept | home | A7: the listener, panning and attenuation curves; MaxDistance below MinDistance; non-spatial sounds have no position |
| `audio-input:270` | concept | home | A8: the Doppler effect and how to get velocities without jitter |
| `audio-input:400` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:338-361`: the models and the mapping of `NoAttenuation`; with the enum, `Strata/src/Strata/Audio/AudioSource.h:15-24` |
| `audio-input:401` | code | home | `Strata/src/Strata/Audio/AudioSystem.cpp:664-700`: the velocity over the time since the last move, smoothing, teleports and stops; with `ComputeVelocity` and `LimitSpeed`, `:45-65` |
| `audio-input:432` | figure | home | Plot: gain against distance for the four models with Min 1, Max 50 and Rolloff 1 and 2, the clamped regions shaded |
| `audio-input:434` | figure | home | Diagram (top view): forward -Z, up +Y, right +X; a source at +X louder on the right; facing +Z flips it; a rolled listener |
| `audio-input:436` | figure | home | Timeline: fixed steps at 60 Hz against frames at 144 Hz; the naive velocity against Strata's; the teleport cut-off |
| `audio-input:507-511` | rule | home | Limit Doppler speeds and treat jumps as teleports; derive velocity over the time since the last move; refuse zero vectors and NaNs |
| `audio-input:579` | hands-on | home | Exercise: add an attenuation-model field to `AudioSourceComponent` (property, `ApplyComponent`, the feature test, `AudioSystemTests`) |
| `audio-input:639-646` | term | home | Listener, spatialization, panning, HRTF, attenuation and attenuation model, minimum and maximum distance, rolloff, Doppler effect |
| `audio-input:648` | term | home | Teleport (audio) |
| `audio-input:746` | open | home | The pan law, the gain smoothing, the Doppler factor and the speed of sound are miniaudio's defaults (Strata sets no Doppler factor): the writer verifies them in the vendored source before stating them |
| `audio-input:539` | rule | use | Why the enum value is `NoAttenuation` (home `core/conventions`) |
| `audio-input:649` | term | use | Exponential smoothing (home `basics/math-interpolation`) |
| `audio-input:406` | code | use | The panning test, named in "How it is tested" |
| `new:6` | not-done | home | Occlusion and reverb zones: walls do not muffle a source and rooms add no reverb; how engines trace or tag them. Evidence: `git grep -niE "occlu\|reverb" 822a7a46 -- Strata/src/Strata/Audio` finds nothing |
| `new:7` | not-done | home | A choice of attenuation model per component: `AudioSourceComponent` has no model field, so components always use Inverse (the exercise adds one). Evidence: `Strata/src/Strata/Audio/AudioComponents.h:11-22` |
| `new:24` | hands-on | home | Trace it yourself (D27): a breakpoint in `AudioSystem::UpdateMotion` on a scene with one looping spatial Audio Source on a rigid body and another on an entity that a script moves shows which velocity each gets: the body's, limited (`GetBodyVelocity`, `LimitSpeed`), or the move over the time since the last move, smoothed, and zero after a teleport or two still fixed steps. Evidence: `Strata/src/Strata/Audio/AudioSystem.cpp:664-700`, `:702-715`, `:45-65` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors: length, dot and cross products, normalizing | `basics/math-vectors` | must |
| Axes and handedness: right-handed, +Y up, -Z forward | `basics/math-matrices` | must |
| The exponential function | `basics/numbers` | must |
| Exponential smoothing, `1 - exp(-t / tau)` | `basics/math-interpolation` | must |
| Velocity as a rate of change | `basics/math-change` | must |
| Fixed steps against frames | `core/time` | must |
| Gain and decibels | `audio/sound-in-a-computer` | must |
| Sources, their settings and their voices | `audio/clips-voices-sources` | must |
| An entity's world transform | `world/scene-graph` | must |
| Rigid bodies and their velocity | `physics/bodies-colliders` | helps |
| The Audio scene system, whose records call this code | `audio/scene-system` | helps |

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

## `audio/testing` — Testing sound without speakers

**Covers.** The job: how Strata proves its sound right on machines without a sound card and without anyone listening.
The page's example is the test "Panning follows the right-handed listener frame": a looping 440 Hz sine placed at +X,
measured channel by channel. In this order: the problem (CI has no sound card, and "it sounds right" is no test); the
idea, taught from zero: a null device pulled by the test, synthetic signals of known RMS (a sine of amplitude 0.5 has RMS
0.3536), measuring only after the spatializer's gain smoothing has settled (2,400 frames), and ratios rather than
absolute levels; the helpers `ScopedAudioEngine`, `Render`, `ComputeRms` and `MeasureRms`; the panning test, walked
through; what the suites cover (`AudioTests`, `AudioSystemTests`, `AudioClipAssetTests`) and the feature test's
`AudioFeatures` script, which calls every function of the SDK's audio; `audio.state`, the query a tool or an agent uses to
hear a game without a sound card (voices, one-shot counts, the listener, master volume; Play mode only), with its JSON
answer; and what the tests cannot prove: nobody judged panning or the Doppler effect by ear, and the release notes say
the Asset tab's preview was checked only on the null device. At the end the reader can write an RMS test for a new
audio feature that does not flake.

**Leaves out.**

- The null device's code → `audio/engine`
- Test kinds, determinism and flaky tests in general → `engineering/testing`
- The feature test's coverage checks and runners → `engineering/feature-test`
- Running a command from a terminal → `editor/commands`

**Fit.** `over`: about 3,100 words against S (1,500). One concept, one excerpt, the suites, `audio.state` with its
answer, the internals sections and two exercises go past S's top. Proposed: M (3,000) by S2, whose range holds the
estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:98` | feature | home | `audio.state`: voices, one-shot counts, the listener and master volume, Play mode only (`StrataEditor/src/Editor/Commands/AudioCommands.cpp:34-79`) |
| `audio-input:101` | feature | home | `AudioFeatures`, which exercises every SDK audio call and requests its clip in `OnCreate` |
| `audio-input:290` | concept | home | A11: testing sound without ears; why measuring before the smoothing settles flakes |
| `audio-input:406` | code | home | `StrataTests/src/Audio/AudioTests.cpp:1095-1129`: panning measured by RMS per channel; with the helpers, `StrataTests/src/Audio/AudioTestUtils.h:54-82` |
| `audio-input:483` | figure | home | Text capture of an `audio.state` answer from StrataCLI; a plot of the left and right RMS as a listener turns; the `input.state` answer is used by `input/simulated` |
| `audio-input:581` | hands-on | home | Exercise: the missing test, a Linear source exactly at MaxDistance with Rolloff 0.5 |
| `audio-input:624` | term | home | RMS |
| `audio-input:759` | open | home | Nothing at the pin shows that panning or Doppler were judged by listening; the preview was "only checked on the null audio device, not by ear" (`Docs/Releases/0.3.0.md:177`) |
| `audio-input:29` | feature | use | The null device that the tests pull with `ReadFrames` |
| `new:26` | hands-on | home | Trace it yourself (D27): a breakpoint in `MeasureRms` during the panning test shows the 2,400 frames pulled so that the gain smoothing settles before the 4,800 frames measured; the same test with the settle step removed shows the level it would measure too early. Evidence: `StrataTests/src/Audio/AudioTestUtils.h:28`, `:77-82`; `StrataTests/src/Audio/AudioTests.cpp:1095-1129` |
| `audio-input:85` | feature | use | `GetVoices` and `GetStats`, which `audio.state` reports |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The null device, `ReadFrames` and `AdvanceNullDevice` | `audio/engine` | must |
| doctest test cases and running one suite | `core/first-change` | must |
| Panning and attenuation | `audio/spatial` | must |
| The scene system's voices and statistics | `audio/scene-system` | must |
| Sine waves and amplitude | `basics/math-vectors` | helps |
| Test kinds, determinism and flaky tests | `engineering/testing` | helps |
| Running an editor command from a terminal (`StrataCLI call`) | `editor/commands` | helps |
| Play mode | `editor/play-mode` | helps |
| The feature test and its coverage checks | `engineering/feature-test` | helps |

## `input/how-input-works` — How input reaches a game: events, polling, edges and intents

**Covers.** The page starts with the problem as a reader meets it, in the Third-Person sample: Space makes the robot
jump once, holding W walks it, typing a name in a menu must not walk it, and a gamepad does all of it with other
controls. The naive answer, "is the key down?" asked once a frame, loses a tap shorter than a frame and jumps every frame
the key is held. In this order the page teaches: where input comes from (the operating system sends events to a window;
GLFW's callbacks; key codes by position against characters by layout; the system's key repeat, which only makes
events); events against polling, and Strata doing both (the callbacks feed a polled state and also send engine events);
polling with edges (down, pressed and released, cleared at the start of each frame; a press and a release inside one
frame both reported; why Pressed is read in the frame update and not in the fixed update, which runs zero or more times
in a frame); text is not keys (character events after layouts, dead keys and input methods; code points and UTF-8);
focus, enabling and capture (who gets the input when the editor, the game, its UI and a text field share one keyboard);
actions instead of keys (intents bound to controls, kinds, composites such as WASD, maps enabled per mode, players'
rebinding).

The approaches table compares Unity's Input System, Unreal's Enhanced Input and Godot's InputMap (actions, maps or
contexts, composites, modifiers and processors, rebinding). Strata's choice, as a bridge to the internals pages: a polled
state with edges in `Input`, events beside it, and actions with maps, composites and players' bindings, without
modifiers. What Strata does not do: touch input. Common mistakes: key codes taken for characters (on AZERTY, `Key::A` is
where A sits on a US keyboard), key repeat used for movement, "pressed" made by comparing with the last frame, text built
from key presses, and gameplay that reads devices while a text field is being edited. At the end the reader can say which
question each form of input answers, and why a game reads actions rather than keys.

**Leaves out.**

- Strata's `Input`: its bitsets, input frames, suspension and captures in code → `input/devices-state`
- The event classes and the layer stack → `core/windows-events`
- Mouse spaces and cursor modes → `input/mouse-cursor`
- Gamepads, dead zones and hysteresis → `input/gamepads`
- Strata's input actions → `input/actions`
- Input-method composition in game UI → `ui/text`
- UTF-8 as an encoding → `basics/bytes`

**Fit.** `over`: about 4,150 words against M (3,000). Five concepts at an engine builder's pace (about 1,750 words), the
problem and its naive answer, the approaches table, the mistakes and three exercises go past M's top. Proposed: L
(5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:302` | concept | home | B1: where input comes from; key codes by US position (`Strata/src/Strata/Input/KeyCodes.h:10-11`); repeat only as events |
| `audio-input:309` | concept | home | B2: polling and edges; a tap inside one frame; Pressed in a fixed update missed or doubled |
| `audio-input:329` | concept | home | B5: text input is not key input |
| `audio-input:333` | concept | home | B6: focus, enabling and capture, as ideas; the engine's side is `input/devices-state`'s |
| `audio-input:339` | concept | home | B7: actions instead of keys; Unity, Unreal and Godot compared; composites normalized (a WASD diagonal is not 1.41) |
| `audio-input:445` | figure | home | Timeline: a key held three frames and a tap inside one frame, with the transitions cleared at each frame's start |
| `audio-input:655-658` | term | home | Polling; event (input); down, pressed and released; edge (transition) |
| `audio-input:661-665` | term | home | Key code, scancode, key repeat, typed text and character event, IME |
| `audio-input:187` | feature | use | The event classes the callbacks send beside the state, to contrast events and polling (home `core/windows-events`) |
| `audio-input:517` | rule | link | Read Pressed and Released in `OnUpdate` |
| `audio-input:666` | term | use | UTF-8 (home `basics/bytes`) |
| `new:9` | not-done | home | Touch input: no touch screens or gestures; how engines map touches to pointers. Evidence: `git grep -niE "touch" 822a7a46 -- Strata/src/Strata/Input Strata/src/Platform/GLFW` finds nothing |
| `foundation:587` | term | home | Polling input: one glossary entry with polling (`audio-input:655`) |
| `new:27` | hands-on | home | Exercises (D27): which `Key` value the key labelled A on a French AZERTY keyboard reports, and which character its event carries (computation); a script in the playground that counts the frames in which `Input::IsKeyPressed(Key::Space)` is true in `OnUpdate` and in `OnFixedUpdate` while Space is tapped and held, each count predicted first (predict, then run; done); the actions and maps of a game that walks, drives and opens a menu (design). Evidence: `Strata/src/Strata/Input/KeyCodes.h:10-11`; `StrataScriptCore/Include/StrataScript/Script.h:84-85` |
| `gameui:736` | open | home | Settled with `new:9`: the game UI has no touch input either; the search over `Strata/src/Strata/GameUI` finds only `GameUIScene::TouchHits`, which marks hit tests stale (`Strata/src/Strata/GameUI/GameUIScene.h:297-298`), so the book claims no touch anywhere |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop | `core/frame-loop` | must |
| Windows and the events they deliver | `core/windows-events` | must |
| The fixed step, which runs zero or more times in a frame | `core/time` | must |
| Unicode code points and UTF-8 | `basics/bytes` | must |
| A callback | `basics/cpp-generic` | helps |
| Project settings, where a project keeps its actions | `world/projects-settings` | helps |

## `input/devices-state` — Input devices and per-frame state

**Covers.** The job: `Input` is the engine's static, main-thread state of keyboard, mouse and gamepads as of the
current input frame, fed by the platform; it knows nothing of actions or of the UI. The page's example is Space, the
Third-Person robot's jump, followed from GLFW's callback to a script's `IsKeyPressed`. In this order: codes and names
(`KeyCode` named by the position on a US keyboard, with GLFW's values, never renumbered because compiled scripts embed
them; mouse codes; `InputNames` for commands, bindings and the editor); the map (the input data flow, the Input stage of
the frame, the window seam `InputWindow` that keeps `Input` below the application shell); the contract (main thread,
updated once per frame; Pressed read in `OnUpdate`; input frames suspended while the game does not update). The toy
version is three bitsets and a frame boundary.

The real code, in the order the data flows: `ButtonStates`, whose one `Set` records the edges; the GLFW callbacks, which
feed the state and also send events, with key repeat only as an event, the releases GLFW reports for every held key and
button when the window loses focus (nothing stays down after Alt+Tab), and keys GLFW cannot name, which never reach
`Input`; the Input stage of `Application`'s frame; `BeginFrame`, which clears transitions only once the game has seen
them, stops while suspended, applies the simulated queue at the boundary and counts input frames; the suspension
timeline (`Input::SetSuspended`), with a link to `editor/stepping` for the editor's call that suspends input frames; the
enabled flag (device queries report nothing while the Game view lacks focus, the state keeps tracking, simulated input
still reaches the game); typed text (UTF-8 assembled and checked, at most 1,024 bytes, control characters and surrogates
dropped, malformed text as U+FFFD; `GetTypedText` empty while the keyboard is captured, `GetUncapturedTypedText` for the
text field that holds it); pointer capture and keyboard capture, which the game UI sets, and the raw queries that
binding capture reads, with a table of who sees what; `Reset`; the SDK's `Input` as scripts see it. Then the alternatives
(event queues for gameplay, snapshots per system, raw input APIs), the tests of `InputTests.cpp`, changing it safely
(codes are ABI; platform code stays in `Platform/`) and the exercises (a second window backend, a test of keyboard
capture, a traced tap). At the end the reader
can say what `IsKeyPressed` returns in each frame of a tap, a hold and a paused game, and who sees a key while a text
field is being edited.

**Leaves out.**

- Events, polling and capture as ideas → `input/how-input-works`
- Mouse positions, the viewport and cursor modes → `input/mouse-cursor`
- Gamepad conventions, the gamepad half of the feed and dead zones → `input/gamepads`
- The simulated device and its merge rules → `input/simulated`
- The editor's call that suspends input frames while a paused game has no step (`UpdateInputSuspension`) → `editor/stepping`
- The Game view that sets the enabled flag → `editor-ui/game-view`
- How the game UI uses the captures → `ui/input`
- Editing text in a text field → `ui/text`

**Fit.** `fits`: about 5,500 words against L (5,000). Five excerpts (about 1,250 words), three figures, three rules and
the features of the feed, the suspension, typed text and the captures take the most; the three exercises add about 650.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:107-108` | feature | home | `KeyCode` (`c_MaxKeyCode` 512) and the mouse codes with `CursorMode` |
| `audio-input:110` | feature | home | `InputNames`: names, aliases, case-insensitive lookups and name lists |
| `audio-input:116-119` | feature | home | The polling API, the input frame, suspension and the enabled flag |
| `audio-input:121` | feature | home | The window seam `InputWindow` |
| `audio-input:123-128` | feature | home | Typed text, pointer capture, keyboard capture, raw queries, `Reset` and the GLFW feed; in the feed, the releases GLFW reports for every held key and mouse button when the window loses focus, and keys GLFW cannot name (a code below 0), which never reach `Input` (`Strata/vendor/glfw/src/window.c:50-68`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:286-289`) |
| `gameui:195` | feature | home | Typed text as the game UI reads it: `GetTypedText`, `GetUncapturedTypedText` while a text field holds the keyboard, `c_MaxTypedTextBytes` = 1,024 (`Strata/src/Strata/Input/Input.h:88-92, 101-108`); the same feature as `audio-input:123` |
| `audio-input:130` | feature | home | The Input stage: `BeginFrame`, `ProcessEvents`, `InputActions::Update`, before modules and layers |
| `audio-input:173`, `scripting:122` | feature | home | The SDK's `Input` as scripts see it (`StrataScriptCore/Include/StrataScript/Input.h:232-530`), one entry with the scripting inventory's `Input`, passed by `scripting` (R31, D26); its actions and capture are used on `input/actions` and `input/rebinding` |
| `audio-input:376` | code | home | `Strata/src/Strata/Input/Input.cpp:19-41`: `ButtonStates`, three bitsets and the one `Set` that records the edges |
| `audio-input:377` | code | home | `Strata/src/Strata/Input/Input.cpp:553-586`: `BeginFrame`, the transitions cleared once seen, suspension, the simulated queue |
| `audio-input:379` | code | home | `Strata/src/Platform/GLFW/GLFWWindow.cpp:286-319`: the key callback, state and event, repeat only as an event; the gamepad half, `:416-442`, is shown on `input/gamepads` |
| `audio-input:380` | code | home | `Strata/src/Strata/Core/Application.cpp:294-305`: where input sits in the frame |
| `audio-input:382` | code | home | `Strata/src/Strata/Input/Input.cpp:182-281`: UTF-8 encoding and a decoder that refuses overlong forms, surrogates and truncation |
| `audio-input:443` | figure | home | Diagram: the operating system, GLFW's callbacks and joystick polling, `Input::Process*`, the simulated queue, the merged queries and their readers |
| `audio-input:448` | figure | home | Timeline: the editor paused, presses accumulating, the step frame reporting them, the frame index standing still |
| `audio-input:462` | figure | home | Table: gameplay queries, `GetPointerState` and `GetKeyState`, raw queries and actions against the enabled flag and the three captures |
| `audio-input:517` | rule | home | Input is main-thread polling state, updated once per frame: read Pressed and Released in `OnUpdate` |
| `audio-input:523` | rule | home | Suspend input frames while the game does not update |
| `audio-input:535` | rule | home | Key codes are ABI and never renumbered |
| `audio-input:599` | hands-on | home | Exercise: what a second, non-GLFW window backend must translate |
| `audio-input:659-660` | term | home | Input frame; suspended input frames |
| `audio-input:668` | term | home | Surrogate |
| `audio-input:691` | term | home | Pointer capture and keyboard capture |
| `audio-input:440` | figure | use | The frame timeline (home `audio/scene-system`) |
| `audio-input:190` | feature | use | The game UI sets the captures and reads `UIActionState` (home `ui/input`) |
| `audio-input:177` | feature | link | The Game view's focus, which sets the enabled flag (home `editor-ui/game-view`) |
| `audio-input:178` | feature | link | The editor's `UpdateInputSuspension`, which suspends input frames while a paused game has no step to run; the page keeps `Input::SetSuspended` and its timeline (home `editor/stepping`, critic-audio-input-13) |
| `audio-input:667` | term | use | Code point and U+FFFD (home `basics/bytes`) |
| `new:28` | hands-on | home | Exercises (D27): a doctest case beside "Keyboard capture hides keys and typed text from the game, never from the key state" that captures the keyboard, presses W and types "w", and checks what `IsKeyDown`, `GetKeyState`, `GetTypedText` and `GetUncapturedTypedText` report in that input frame and the next, predicted first (predict, then run; a patch: done); trace it yourself: breakpoints in `Input::ProcessKey` and `Input::BeginFrame` while Space is tapped in the Third-Person sample show the callback's call, the edge that `ButtonStates::Set` records and the transition cleared at the next input frame. Evidence: `StrataTests/src/Core/InputTests.cpp:681`; `Strata/src/Strata/Input/Input.h:101-108`; `Strata/src/Strata/Input/Input.cpp:19-41`, `:553-586`, `:638-642` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Polling, events, edges, typed text and capture as ideas | `input/how-input-works` | must |
| Bits, shifts and masks | `basics/numbers` | must |
| Templates, lambdas and `std::bitset` | `basics/cpp-generic` | must |
| Unicode code points and UTF-8's bytes | `basics/bytes` | must |
| The frame loop's stages and `ST_PROFILE_STAGE` | `core/frame-loop` | must |
| The window and its events | `core/windows-events` | must |
| Layers, and a seam that keeps one module below another | `core/layers-registries` | must |
| Static member functions | `basics/programming-2` | helps |
| The main thread and the threading model | `core/jobs` | helps |
| The editor's Game view, which calls `SetEnabled` | `editor-ui/game-view` | helps |
| The script ABI and the SDK | `scripting/abi-sdk` | helps |
| Pausing and stepping a game in the editor | `editor/stepping` | helps |

## `input/mouse-cursor` — The mouse, the cursor and the game view

**Covers.** The job: where the mouse is in the game's own pixels, how far it moved, and who may hide or lock the cursor.
The page's example is the Third-Person's follow camera, which turns with `GetMouseDelta` while the cursor is locked,
and its pause menu, which frees the cursor. In this order: the problem, taught from zero (window pixels, the game's
viewport inside an editor panel, the game's render resolution; positions against deltas; scroll as a delta; why a
first-person camera needs relative motion, and why positions stop at the screen's edge); the coordinate-mapping diagram
and its formula; the contract (the game's cursor mode applies only while the game has the input). The toy version maps
one point from window to viewport to game pixels.

The real code: `GetMousePosition` and `GetMouseDelta` with the viewport's scale; `SetViewport(origin, size,
resolution)` and the fallbacks of `GetViewportSize` (resolution, else size, else window); the simulated pointer, which
replaces the device's position once moved (named; `input/simulated` teaches it); the cursor modes Normal, Hidden and
Locked as GLFW's modes (Locked is GLFW's disabled cursor: hidden, grabbed, a virtual position without limits, and raw,
unaccelerated motion where the platform has it, so that only deltas mean something while it is locked);
`SetCursorMode`, which the editor's fly camera uses, against `SetGameCursorMode`, the game's wish, applied only while
input is enabled, Normal while it is not and reset when play stops; the units of a position in the editor (the Game
view's game pixels) and in an exported game (the window's screen coordinates, while `Game::GetWindowSize` reports
framebuffer pixels: on a scaled display they differ by the content scale), which the page says was read, not run. The
Game view's resolution modes, its letterboxing and Shift+F1 are named and linked. Then the alternatives, set against
what Locked already does (the pointer lock and raw motion that GLFW asks of the operating system): warping the cursor
back to the center by hand each frame, and a raw input API read beside the window's events; the tests of
`InputTests.cpp` for viewports and cursor modes, and changing it safely. At the end the reader can compute a game pixel
from a window pixel for a letterboxed view, and explain why mouse look reads deltas.

**Leaves out.**

- The Game view's resolution modes, letterboxing, the cursor lock's hint and Shift+F1 → `editor-ui/game-view`
- The editor camera's fly mode → `editor/camera-viewport`
- Mouse buttons and their edges → `input/devices-state`
- The simulated pointer and its merge rules → `input/simulated`
- Hit-testing UI under the pointer → `ui/input`

**Fit.** `fits`: about 3,550 words against M (3,000). The concept of mouse spaces with its figure (about 570 words),
the mapping code with its excerpt and the cursor modes take the most; the three exercises add about 600.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:120` | feature | home | `SetViewport(origin, size, resolution)`: positions relative to the viewport, scaled to the rendered resolution; `GetViewportSize` |
| `audio-input:122` | feature | home | `SetCursorMode` against `SetGameCursorMode`; Normal while input is disabled; reset at play stop |
| `new:19` | feature | home | The cursor modes as GLFW's: Normal, Hidden and Locked are `GLFW_CURSOR_NORMAL`, `GLFW_CURSOR_HIDDEN` and `GLFW_CURSOR_DISABLED`, which hides and grabs the cursor and gives virtual, unlimited motion; with Locked the window also turns on raw (unscaled and unaccelerated) motion where `glfwRawMouseMotionSupported` says the platform has it; while locked only deltas mean something, positions do not. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:555-568`; `Strata/src/Strata/Input/MouseCodes.h:38`; `Strata/vendor/glfw/include/GLFW/glfw3.h:4684-4689`, `:4714-4718` |
| `new:18` | open | home | Check: Mouse units on a scaled display. The claim: only the editor's Game view sets an input viewport, so in the editor a mouse position is in the Game view's game pixels, while in an exported game it is in the window's screen coordinates and `Game::GetWindowSize` reports the framebuffer's pixels; on a scaled display (Retina) the two differ by the content scale, and the Physics Playground's cursor ray divides one by the other. The page states what the code shows and says in one sentence that it was read, not run; the brief is not blocked (R39). Evidence: `git grep -n "Input::SetViewport" 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds only the definition (`Strata/src/Strata/Input/Input.cpp:631`) and `StrataEditor/src/Panels/GameViewPanel.cpp:279`; `Strata/src/Strata/Core/Window.h:74-75`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:576-577`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:193-204` |
| `audio-input:315` | concept | home | B3: mouse spaces and cursor modes; mouse look with positions, DPI and panel offsets forgotten, a locked cursor left behind |
| `audio-input:381` | code | home | `Strata/src/Strata/Input/Input.cpp:364-375`: window to viewport to game pixels, and the simulated pointer; with the scale, `:137-145` |
| `audio-input:449` | figure | home | Diagram: the window, the panel's image rect (origin, size) and the render resolution, with the formula of `GetMousePosition` |
| `audio-input:537` | rule | home | The game's cursor mode applies only while it has the input |
| `audio-input:669-671` | term | home | Viewport (input), cursor mode, mouse delta |
| `editor-ui:777` | term | home | Cursor lock: the game hiding the cursor and taking its motion, Strata's `CursorMode::Locked` (`Strata/src/Strata/Input/MouseCodes.h:38`); one glossary entry with cursor mode (`audio-input:670`) |
| `audio-input:177` | feature | use | The Game view gives `Input` its rect and resolution, and a locked cursor makes ImGui ignore the mouse (home `editor-ui/game-view`) |
| `audio-input:479` | figure | link | The Game view with a locked cursor and the Shift+F1 hint (home `editor-ui/game-view`) |
| `audio-input:138` | feature | use | The simulated pointer (home `input/simulated`) |
| `audio-input:108` | feature | use | The mouse codes and `CursorMode` (home `input/devices-state`) |
| `new:29` | hands-on | home | Exercises (D27): the game pixel of window pixel (520, 300) for a 1920 by 1080 game shown at origin (40, 30) in 960 by 540 window pixels, by the formula (computation); the same case as a doctest beside "A viewport with a resolution of its own reports the mouse in the game's pixels", with the delta of a move, predicted first (predict, then run; a patch: done); a breakpoint in `Input::SetGameCursorMode` while the Third-Person's pause menu opens and closes shows the game's wish and the mode the window gets (trace). Evidence: `Strata/src/Strata/Input/Input.cpp:137-145`, `:364-375`, `:530-535`; `StrataTests/src/Core/InputTests.cpp:72-90`; `Samples/ThirdPerson/Scripts/PauseMenu.cpp:106`, `:120` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The per-frame state, the enabled flag and the window seam | `input/devices-state` | must |
| 2D vectors, added and scaled per component | `basics/math-vectors` | must |
| The window's size in screen coordinates and in framebuffer pixels, and the content scale | `core/windows-events` | must |
| The Game view, its resolution modes and letterboxing | `editor-ui/game-view` | helps |
| The editor camera's fly mode | `editor/camera-viewport` | helps |
| Play mode | `editor/play-mode` | helps |

## `input/gamepads` — Gamepads

**Covers.** The job: how Strata reads gamepads: the mapping database that turns hundreds of controller models into one
layout, the conventions of its axes, and the dead zones and hysteresis that turn noisy sticks into steady movement. The
page's example is the Third-Person robot walking with the left stick, and a stick at rest that reads a small value
instead of 0. In this order: the problem, taught from zero (controllers report buttons and axes in different orders;
sticks never rest at exactly 0); mapping databases (the SDL GameControllerDB that GLFW 3.4 compiles in) and the
Xbox-like layout; the conventions (15 buttons, 6 axes, 4 gamepads; sticks from -1 to 1 with +Y up; triggers from 0 to
1) with their diagram; the polling code that converts GLFW's values every frame (+Y down, triggers from -1 to 1) and
reports a disconnected pad at rest; raw axes in `Input`, without a dead zone. The toy version is a dead zone on one axis.

Then dead zones: axial, per axis, against radial, on the stick's length, and rescaling so that full tilt still reads 1,
with the plots; the real code is the SDK's `GetGamepadAxis` and `GetGamepadStick`, short enough for a game maker to copy.
Then hysteresis for an axis used as a button (on from 0.5, off below 0.35) and its plot; the action code that applies it
per pad is named and linked. The page is the book's home of the word hysteresis, and one sentence names its other use,
the world streamer's keep radius beyond its load radius (`worlds/streamer`). Then several gamepads
(`IsGamepadConnected`; gamepad bindings read every pad), and gamepads read while an exported game is in the background,
as the release notes say. What Strata does not do: force feedback; gamepads assigned to players; controllers missing
from GLFW's database, more than four gamepads and mappings that a game adds. Then the alternatives (SDL's own
controller API, XInput and GameInput, platform HID), the tests and changing it safely (gamepad codes are ABI). At the
end the reader can choose a dead zone for a stick, explain why diagonals snap with an axial one, and say why a stick
resting near a threshold needs two thresholds.

**Leaves out.**

- Actions that read gamepads, and the hysteresis code per pad → `input/actions`
- The world streamer's load and keep radii, the other use of hysteresis → `worlds/streamer`
- The rest of the GLFW feed and the per-frame state → `input/devices-state`
- Vector length and normalizing → `basics/math-vectors`

**Fit.** `over`: about 4,300 words against M (3,000). The concept of dead zones and hysteresis with its three plots
(about 820 words), the conventions and the polling code, one excerpt, three absences and three exercises go past M's
top. Proposed: L (5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:109` | feature | home | 15 Xbox-layout buttons, 6 axes, 4 gamepads; sticks -1 to 1 with +Y up, triggers 0 to 1; `GetGamepadAxisMinimum` |
| `audio-input:129` | feature | home | Polling after `glfwPollEvents`: `glfwJoystickIsGamepad` and `glfwGetGamepadState`, Y negated, triggers remapped, a disconnected pad at rest |
| `audio-input:321` | concept | home | B4: mapping databases, conventions, axial and radial dead zones, rescaling, hysteresis |
| `audio-input:383` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:326-353`: an axial and a radial dead zone with rescaling |
| `audio-input:451-453` | figure | home | Diagram of the conventions; plots of the axial square and the radial circle with the rescaled response; plot of hysteresis at 0.5 and 0.35 |
| `audio-input:672-677` | term | home | Gamepad mapping; axis, stick and trigger; half axis; dead zone, axial and radial; rescaling; hysteresis |
| `worlds-runtime:524` | term | home | Hysteresis, one glossary entry with `audio-input:677`, passed by `worlds` (R31, D33; R46): different thresholds for turning on and for turning off, so that a value near a threshold does not flicker; the entry names both uses, the gamepad's 0.5 and 0.35 beside the plot `audio-input:453`, and the world streamer's keep radius beyond its load radius (`worlds/streamer` says the word in one sentence and links here) |
| `audio-input:379` | code | use | `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`, the gamepad half of the feed (home `input/devices-state`) |
| `audio-input:753` | open | use | Gamepads are read while an exported game is in the background (`Docs/Releases/0.7.0.md:363`) |
| `audio-input:156` | feature | link | The thresholds as actions apply them |
| `audio-input:158` | feature | link | Gamepad bindings read every pad |
| `new:10` | not-done | home | Force feedback: no rumble or haptics; how engines expose them. Evidence: `git grep -niE "rumble\|vibrat\|haptic" 822a7a46 -- Strata/src StrataScriptCore` finds nothing |
| `new:11` | not-done | home | Gamepads assigned to players for local multiplayer: a gamepad binding reads every gamepad, and all players share one set of actions. Evidence: `Docs/DeveloperGuide.md:1460`; `Docs/Releases/0.7.0.md:361-362, 412`; `Docs/Roadmap.md:1707` |
| `new:12` | feature | home | GLFW 3.4 and its built-in mapping database (`src/mappings.h`, the SDL GameControllerDB, about 1,000 lines). Evidence: `Strata/vendor/glfw/include/GLFW/glfw3.h:287-301`; `Strata/vendor/glfw/src/mappings.h` |
| `new:20` | not-done | home | Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds: Strata reads GLFW's joystick slots 1 to 4 only, an unmapped controller reads as not connected and keeps its slot (so the first real pad may be gamepad 1), and nothing calls `glfwUpdateGamepadMappings`; how SDL's hints and Steam Input add mappings. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds nothing; `StrataScriptCore/Include/StrataScript/Input.h:301` |
| `new:30` | hands-on | home | Exercises (D27): a sketch with the SDK's dead-zone code that prints the axial and the radial response for a stick at (0.1, 0.1), (0.2, 0) and (0.6, 0.6) with the default dead zone 0.15, each predicted first (predict, then run; a sketch with its output: done); a breakpoint in `GLFWWindow::PollGamepads` with a pad connected shows the Y axes negated and the triggers remapped, and without one the pad reported at rest (trace); two thresholds for a trigger read as a button in a racing game, and what one threshold would do (design). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:236`, `:326-353`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/InputActions.h:51-52` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vector length and normalizing | `basics/math-vectors` | must |
| The per-frame state and the GLFW feed | `input/devices-state` | must |
| Static functions with default arguments | `basics/programming-2` | helps |
| Input actions, which apply the same thresholds | `input/actions` | helps |

## `input/actions` — Input actions

**Covers.** The job: `InputActionSet` is the project's definition of the game's actions (the settings section
`Input.Actions`), and `InputActions` evaluates them once per input frame from the devices, the players' bindings, the
map enables and simulated holds; the game UI reads its six actions through `UIActionState`. The page's example is the
Third-Person's `Gameplay` map (Move as a Vector2 from `2D:Key/W,Key/S,Key/A,Key/D` and `Gamepad/LeftStick`; Look,
Jump, Run, Pause, Wave, Dance and Respawn) and the reserved `UI` map that its menus navigate with. In this order: the
problem and how engines solve it, in one paragraph that links `input/how-input-works`; the map (the model as a class
diagram and its compiled form as arrays of indices); the contract (gameplay reads rebindable controls as actions; a map
disabled while an action is held releases it once; an edit keeps the state of unchanged actions). Then the model with the
Project Settings page as its picture (maps, actions, the kinds Button, Axis and Vector2, the limits, the dead zone);
names (`<Map>/<Action>` or an unambiguous bare name, and an ambiguity refused with every match named); the binding
grammar as a data type with the rule of which kind takes which binding; the hand-written parser of `1D:` and `2D:`
composites with its error messages; the reserved `UI` map (`UI/Submit`, `UI/Cancel` and the four directions) and its
default bindings, as the code gives them, whose stick bindings are half axes and so hold with the hysteresis of every
button action, not values of their own; the settings section, its schema and its registration. The toy version evaluates one Button and one Vector2 from a list of bindings.

The real code: compiling the set into flat arrays while the state of each action is carried across by its lower-case
qualified name, so a live edit presses nothing again; `Update` and `Evaluate` (only when an input frame started;
bindings combined by kind; composites normalized, so a diagonal of two keys has length 1; the radial dead zone, rescaled
by the length in `ApplyDeadZone` as the SDK's `GetGamepadStick` does; Pressed and Released derived; a disabled map
releasing); a half axis read per gamepad with hysteresis; a whole axis taken from the gamepad pushed furthest, and the
Apple Clang 17 miscompile that shaped that code; map enables from the next input frame; fast reads (`FindIndex`,
`GetStateAt`, `GetStateVersion`) and the perf test `Perf.Input.Actions256`, whose numbers come from the generated table;
simulated actions; the UI actions and menu key repeat (0.4 s, then every 0.1 s of unscaled time, at most one repeat per
update, idle updates skipped by version) with its timeline, which the game UI's edit keys share; that this repeat is
the engine's, of the six rebindable UI actions, and another mechanism than the SDK's `KeyRepeat`, which a script runs in
its own module on one key (0.25 s, then every 0.05 s by default; `make/timers-events`), so the page says which is
which; how scripts reach input
across the ABI: first the device functions (keys and mouse in the initial set, gamepads and the cursor, typed text
through the text buffer, and `SetCursorMode`, which records the game's wish through `Input::SetGameCursorMode`), then the
ten action functions and three capture functions appended to the ABI, names and bindings passed as text, misuse reported
once; the editor's `inputActions.*` commands.
One sentence dates the actions to 0.6.0. Then what Strata does not do (modifiers, chords, processors and interactions;
mouse motion and scroll are no action sources), the alternatives, the tests of `InputActionsTests.cpp` and changing it
safely. Exercises: a mouse-wheel binding control, modifiers as a design, profiling the actions, and an evaluation of
Move traced in a debugger. At the end the reader
can write bindings in the grammar, predict an action's state in each frame of a press, a map disable and a live edit, and
explain why evaluation runs on compiled arrays.

**Leaves out.**

- Actions instead of keys as an idea, and the engines' action systems → `input/how-input-works`
- Dead zones and hysteresis as ideas → `input/gamepads`
- The players' bindings file and binding capture → `input/rebinding`
- The simulated device and its merge rules → `input/simulated`
- The Input Actions page's drawing (chips, popups, the capture countdown) → `editor-ui/settings-windows`
- UI navigation, which reads the UI actions → `ui/input`
- The SDK's `KeyRepeat` helper for scripts → `make/timers-events`
- Settings sections, versions and validation in general → `world/projects-settings`

**Fit.** `fits`: about 7,550 words against XL (8,000). Eight excerpts (two items share the grammar's; about 2,000
words) and twenty-three features with the internals sections take the most; the four exercises add about 800.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:148-161` | feature | home | The model and its limits, the grammar, kind fitting, names, the reserved `UI` map, the section `Input.Actions`, evaluation, combining bindings, thresholds and hysteresis, the radial dead zone, several gamepads, map enables, live edits, fast reads |
| `audio-input:164` | feature | home | Simulated actions: `SimulateAction` from the next input frame whatever the bindings, `ReleaseAllSimulated`, `ClearSimulated` |
| `audio-input:166-167` | feature | home | `UIActionState` (down, pressed, repeated); `Perf.Input.Actions256`, its measurement and budget read from `StrataTests/Perf/Budgets.json:218`, never typed |
| `audio-input:175-176` | feature | home | The input functions of the ABI and their host functions: the device functions (keys and mouse in the initial set, `StrataScriptCore/Include/StrataScript/ScriptABI.h:389-398`; gamepads and the cursor; typed text through the text buffer; `SetCursorMode`, whose host function records the game's wish through `Input::SetGameCursorMode`, `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1142-1156`), then the appended action and capture functions |
| `audio-input:180` | feature | home | `inputActions.setMap` and `inputActions.setAction` (Edit, one project undo step) and `inputActions.resetPlayerBindings` (Session) |
| `audio-input:183` | feature | home | The Third-Person's `Gameplay` map and its UI actions in menus, as the running example |
| `audio-input:347` | concept | home | B8: compiled once, evaluated once per input frame, state kept across rebuilds by a stable key, versions for cached indices |
| `audio-input:384` | code | home | `Strata/src/Strata/Input/InputActionSet.h:63-95`: the binding grammar as a data type; with `FitsKind`, `Strata/src/Strata/Input/InputActionSet.cpp:488-501` |
| `audio-input:385` | code | home | `Strata/src/Strata/Input/InputActionSet.cpp:414-472`: the parser of controls and composites, with precise errors |
| `audio-input:386` | code | home | `Strata/src/Strata/Input/InputActions.cpp:452-558`: `Evaluate`, the heart of the area |
| `audio-input:387` | code | home | `Strata/src/Strata/Input/InputActions.cpp:341-381`: a button-like control read for a Button, half axes with hysteresis per gamepad |
| `audio-input:388` | code | home | `Strata/src/Strata/Input/InputActions.cpp:405-420`: a whole axis from the gamepad pushed furthest, and why the comment names a compiler's version |
| `audio-input:389` | code | home | `Strata/src/Strata/Input/InputActions.cpp:115-239`: `Compile`, flat arrays and state carried across by the qualified name |
| `audio-input:391` | code | home | `Strata/src/Strata/Input/UIActions.cpp:39-87`: menu key repeat and idle updates skipped by version |
| `gamedev:369` | code | home | `Strata/src/Strata/Input/InputActionSet.h:63-95`: the same excerpt as `audio-input:384`, the binding grammar and the kinds (the router's L61-96 starts two lines early and ends one late) |
| `gamedev:370` | code | home | `Strata/src/Strata/Input/InputActions.cpp:441-450`: `ApplyDeadZone`, the radial dead zone rescaled by the length; the 2D composite normalized so that diagonals have length 1 (the router's L513-531) is shown inside the excerpt of `audio-input:386` |
| `gameui:185` | feature | home | The game UI's view of the `UI` map: `UI/Submit`, `UI/Cancel`, `UI/Up`, `UI/Down`, `UI/Left`, `UI/Right`, repeat after 0.4 s then every 0.1 s of unscaled time, an idle update costing a comparison (`Strata/src/Strata/Input/UIActions.h:11-64`); the same features as `audio-input:152` and `audio-input:166` |
| `gameui:471` | figure | home | Timeline of menu key repeat: the press at 0 s, repeats at 0.4, 0.5 and 0.6 s, at most one an update; the game UI's edit keys repeat on the same constants (`Strata/src/Strata/GameUI/GameUISystem.cpp:591-609`, taught on `ui/text`) |
| `gameui:737` | open | home | Settled at the pin: the `UI` map's stick bindings are half axes (`Gamepad/LeftY+` and the others, `Strata/src/Strata/Input/InputActionSet.cpp:149-152`), so they hold with every button action's hysteresis, on from 0.5 and off below 0.35 (`Strata/src/Strata/Input/InputActions.h:43, 51-52`); the map has no values of its own |
| `audio-input:454` | figure | home | Class diagram of `InputActionSet`, `InputActionMap`, `InputAction` and `InputBinding`, and the compiled form (`ActionRecord[]`, `CompiledBinding[]`, `InputControl[]`, `HalfAxisHeld[]`) |
| `audio-input:456` | figure | home | Flowchart of evaluation per kind: the dead zone, hysteresis, the simulated override, Pressed and Released |
| `audio-input:474` | figure | home | Screenshot: Project Settings > Input Actions in the Third-Person project, with the `UI` map and the `Gameplay` map's actions, kinds, dead zones and binding chips |
| `audio-input:525` | rule | home | Gameplay reads rebindable controls as input actions; devices only for what nobody rebinds (mouse look, text, debug keys) |
| `audio-input:529-531` | rule | home | Disabling a map releases its held actions once; an edit of the actions keeps the state of unchanged actions |
| `audio-input:591-593` | hands-on | home | Exercises: a mouse-wheel half-axis control end to end; modifiers and chords as a design |
| `audio-input:597` | hands-on | home | Exercise: run `Perf.Input.Actions256` in Release and explain the flat arrays and `GetStateVersion` |
| `audio-input:678-684` | term | home | Input action, action kind, binding, composite (1D and 2D), action map, qualified name and bare name, UI map |
| `audio-input:339` | concept | use | Actions instead of keys (home `input/how-input-works`) |
| `audio-input:365` | concept | use | Crossing the script ABI with names and bindings as text (home `scripting/host-api`) |
| `audio-input:543` | rule | use | A misspelled action is reported once and reads as up (home `scripting/host-api`) |
| `audio-input:162` | feature | link | The players' bindings (home `input/rebinding`) |
| `new:13` | not-done | home | Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API); how Unity and Unreal provide them. Evidence: `Docs/DeveloperGuide.md:1464-1465`; `Docs/Releases/0.7.0.md:361-362, 412`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>` (`:48-58`), `Gamepad/`, `1D:` and `2D:` |
| `new:14` | erratum | home | The comment above `UIAction` gives the UI's default bindings as Enter, Escape and the arrows with the gamepad's A, B, d-pad and left stick; the code also binds Submit to keypad Enter and Space. The page gives the code's list. Evidence: `Strata/src/Strata/Input/UIActions.h:11-13`; `Strata/src/Strata/Input/InputActionSet.cpp:146-153`; `StrataScriptCore/Include/StrataScript/UI.h:16-18` |
| `new:15` | feature | home | The release history in one sentence: input actions with rebinding arrived in 0.6.0 (`appendix/history` has the rest). Evidence: `Docs/Releases/0.6.0.md:94-100` |
| `new:31` | hands-on | home | Trace it yourself (D27): a breakpoint in `Evaluate` while the Third-Person's Move is held with W and D shows the 2D composite normalized to length 1, and, with a gamepad, the radial dead zone of `Gamepad/LeftStick` applied by `ApplyDeadZone`. Evidence: `Strata/src/Strata/Input/InputActions.cpp:452-558`, `:441-450` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Actions instead of keys, intents and the engines' action systems | `input/how-input-works` | must |
| The per-frame state, input frames, suspension and captures | `input/devices-state` | must |
| Dead zones, half axes and hysteresis | `input/gamepads` | must |
| Settings sections, `IProjectSettings`, versions and validation | `world/projects-settings` | must |
| JSON objects and arrays | `basics/data-formats` | must |
| `std::optional` and `std::string_view` | `basics/cpp-modern` | must |
| Hash maps | `basics/data-structures` | must |
| Unscaled time | `core/time` | must |
| Writing a parser by hand | `basics/data-formats` | helps |
| The script ABI and why functions are appended | `scripting/abi-sdk` | helps |
| Host functions and `ReportProblem` | `scripting/host-api` | helps |
| Editor commands and their kinds | `editor/commands` | helps |
| Undo steps of the project's settings | `editor/undo` | helps |
| Perf tests and budgets | `engineering/perf-lab` | helps |
| Differences between compilers | `engineering/flags-portability` | helps |
| UI navigation | `ui/input` | helps |

## `input/rebinding` — Players' bindings inside the engine: the bindings file and capture

**Covers.** The job: the engine's side of players' bindings and of "press a key to bind": the replacements a player
makes, the bindings file in the game's save directory, the session that resets them, and the one binding capture that
the editor's Input Actions page and a game's rebinding menu share. The page's example is a player of the Third-Person
game who rebinds Jump from Space to a gamepad button and finds it again in the next session. In this order: the
problem, taught from zero (the press that is captured must trigger nothing and must not click the button that started
the capture; capture must work while the game is paused; several owners share one listener); the map (the players'
bindings from the project's section and `InputBindings.json` into `Compile`; Save, Load and Delete; the editor's
`.strata/Saves` and a shipped game's user data folder) and the capture's state machine; the contract (only
`InputActions` touches the bindings file; a capture's press triggers nothing). The toy version compares the raw state
with the state at the capture's start.

The real code: the players' bindings (`SetBindings` validated, an empty list unbinding; `ResetBindings`;
`GetPlayerBindings`; `SaveBindings`, written atomically; `LoadBindings`, at most 64 KiB and forgiving per entry;
`ReadSavedBindings`; `DeleteSavedBindings`) and the file's header; sessions (`ResetSession` at play start and stop; the
editor and `GameRuntime` load the bindings when a game starts); binding capture (the first control going down from the
raw state, in device order, half axes with hysteresis, every action up while it listens, the captured control
suppressed for actions until released, numbered captures that are taken or cancelled only by their owner); a script
owns only the capture it started; the editor's "In play" markers and Reset Player Bindings, which show what the next
session starts with. Then what Strata does not do (key names that follow the player's keyboard layout: a game shows a
key by its US position), the alternatives (a capture per owner, a capture inside a UI widget), the capture tests of
`InputActionsTests.cpp` and changing it safely. At the end the reader can say where a player's binding is stored and
when it applies, and why the key that was captured does not also close the menu.

**Leaves out.**

- The rebinding screen a game builds, and capture as a game maker uses it → `make/menus`
- The Input Actions page, its chips and the capture's countdown → `editor-ui/settings-windows`
- Where a shipped game's save directory is → `worlds/game-identity`
- Atomic writes in general → `core/files`
- The grammar of a binding's text → `input/actions`

**Fit.** `fits`: about 3,950 words against M (3,000). The concept of "press a key to bind", the players' bindings and
binding capture with its excerpt (about 1,000 words) take the most; the estimate stands about 50 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:162-163` | feature | home | The players' bindings and their file (header `{"Strata": {"Format": "InputBindings", "Version": 1}}`); sessions and `ResetSession` (`StrataEditor/src/Editor/EditorContext.cpp:1395, 1633-1641`) |
| `audio-input:165` | feature | home | Binding capture: `BeginCapture`, the raw state, suppression, `GetCaptureId`, `TakeCapturedBinding`, `CancelCapture`, `GetCapturedControl` |
| `audio-input:352` | concept | home | B9: "press a key to bind" |
| `audio-input:390` | code | home | `Strata/src/Strata/Input/InputActions.cpp:596-667`: edges against the raw state at the start, device order, half axes with hysteresis, suppression |
| `audio-input:458` | figure | home | State machine: idle, listening (every action up), captured (the text waiting), taken; suppression until release; replaced by another owner; cancelled |
| `audio-input:460` | figure | home | Data flow: the project's section and `InputBindings.json` into `Compile`; Save, Load and Delete; the editor's `.strata/Saves` and the runtime's user data folder |
| `audio-input:478` | figure | home | Screenshot: the "In play" markers and Reset Player Bindings after a play session saved bindings |
| `audio-input:527` | rule | home | Only `InputActions` touches the players' bindings file |
| `audio-input:533` | rule | home | A capture's press triggers nothing |
| `audio-input:685-687` | term | home | Players' bindings, binding capture, suppression (capture) |
| `editor-ui:782`, `scripting:566` | term | home | Binding capture, as the editor's and the scripting glossaries word it; one glossary entry with `audio-input:686` |
| `audio-input:408` | code | use | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:2961-2991`: a script polls and cancels only the capture it started |
| `audio-input:180` | feature | use | `inputActions.resetPlayerBindings` |
| `audio-input:181` | feature | link | The Input Actions page and `BindingCapture` (home `editor-ui/settings-windows`) |
| `audio-input:477` | figure | link | The capture's listening line with its countdown (home `editor-ui/settings-windows`) |
| `new:21` | not-done | home | Key names that follow the player's keyboard layout: a game shows a key's name by its US position (binding text, a rebinding screen), and only the editor's shortcuts follow the layout, through `Window::GetLayoutKey`; how engines ask the platform for a key's label. Evidence: `Docs/Releases/0.7.0.md:361-362`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:626-651`; `git grep -n GetLayoutKey 822a7a46 -- Strata/src StrataScriptCore` finds only the window's code (`Strata/src/Platform/GLFW/GLFWWindow.cpp:626`, `Strata/src/Platform/GLFW/GLFWWindow.h:48`, `Strata/src/Strata/Core/Window.h:117`) and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180`, a comment at `Strata/src/Strata/ImGui/ImGuiPlatform.h:22`) |
| `new:32` | hands-on | home | Exercises (D27): the test "The captured control stays up for actions until it is released" extended so that the key is let go one input frame later, with the frame in which its action can press again predicted first (predict, then run; a patch: done); a breakpoint in `GetBindingsFile` while a play session in the editor saves bindings shows the save directory that `IGameSaves` gives and the file's name (trace); one capture per owner instead of one shared capture, and what breaks when the Input Actions page and a game's menu listen at once (design). Evidence: `StrataTests/src/Core/InputActionsTests.cpp:997`; `Strata/src/Strata/Input/InputActions.cpp:670-681`, `:938-950` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Actions, bindings, the compiled set and `SetBindings` | `input/actions` | must |
| Raw queries and suspended input frames | `input/devices-state` | must |
| Atomic writes of files | `core/files` | must |
| A JSON file with a format header | `basics/data-formats` | must |
| The game's save directory (`IGameSaves`) | `worlds/game-identity` | helps |
| Bounded reads of untrusted files | `assets/robustness` | helps |
| Play sessions in the editor | `editor/play-mode` | helps |
| The editor's Input Actions page and `BindingCapture` | `editor-ui/settings-windows` | helps |
| Host functions | `scripting/host-api` | helps |

## `input/simulated` — Simulated input

**Covers.** The job: a virtual keyboard, mouse and gamepads that tools, tests and agents press, merged with the real
devices so that the game sees one state; the editor's holds counted in fixed steps are `editor/stepping`'s. The page's
examples are an agent pressing Space for the Third-Person robot while a person holds W, and the feature test's
`InputFeatures` runner, which presses keys and buttons around its `PressFrame`. In this order: the problem, taught from
zero (tests and agents must play the same way at any frame rate and without the window's focus); the map (the simulated
queue applied at `BeginFrame`, merged with the devices behind the same queries); the contract (simulated events apply at
the next input frame; simulated input reaches the game whatever the enabled flag). The toy version is a queue of events
applied at a frame boundary and merged with a device's state.

The real code: the `Simulate*` functions, queued and applied at the next `BeginFrame`, so every transition lasts a whole
input frame; the merge rules (a button is down while either source holds it; a transition of one source is none when the
other held the button through the frame, so a tool's press over a person's hold changes nothing and restarts no repeat;
the pointer-to-member template) with their truth table; the simulated pointer (once moved, its position replaces the
device's; the first move only sets it); simulated gamepads (connected once used, until cleared; a held axis replaces the
device's value); release and clear (`ReleaseAllSimulated` queues releases and drops queued presses; `ClearSimulated`
forgets without releases when a session ends; `HasQueuedSimulatedInput` and the `IsSimulated*` queries); why durations
count fixed steps, named with a link to `editor/stepping`; the feature test's runner as the part's test of the whole
input path. Then the alternatives (injecting operating-system events, recording raw device streams), the tests of
`InputTests.cpp` and changing it safely. The exercises trace a simulated tap from `input.key` to a script's
`IsKeyPressed`, and change the "held throughout" rule to see which test fails and why. At the end the reader can predict
what a game sees when a tool and a person press the same key, and why a simulated press waits for the next input frame.

**Leaves out.**

- Holds counted in fixed steps, `input.sequence`, `input.click` and the other `input.*` commands → `editor/stepping`
- Simulated actions → `input/actions`
- Play-tests from a game maker's side → `make/automated-playtests`
- Agents that play a game → `automation/agents`

**Fit.** `fits`: about 3,350 words against M (3,000). The merge rules with their excerpt and truth table (about 450
words) and the concept from zero take the most; the two exercises add about 450.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:136-140` | feature | home | The virtual keyboard, mouse and gamepads, the merge rules, the simulated pointer, simulated gamepads, release and clear |
| `audio-input:182` | feature | home | `InputFeatures` (`StrataTests/FeatureTest/Scripts/InputFeatures.cpp`), whose runner simulates input around `PressFrame` and checks keys, mouse, scroll, gamepad, cursor, actions, rebinding, saving and capture |
| `audio-input:357` | concept | home | B10: the engine's half (a virtual device, events at the frame boundary, merging, suspension); the editor's holds are `editor/stepping`'s |
| `audio-input:378` | code | home | `Strata/src/Strata/Input/Input.cpp:147-175`: merging two sources and the "held throughout" rule |
| `audio-input:447` | figure | home | Truth table: the device held, pressed or released against the simulated source, and what the game sees |
| `audio-input:519` | rule | home | Simulated events apply at the next input frame |
| `audio-input:595` | hands-on | home | Exercise ("trace it yourself"): a simulated tap from `input.key` through `SimulatedInput::Press`, `Input::SimulateKey` and `BeginFrame` to `IsKeyPressed`, with frame and step numbers |
| `audio-input:688` | term | home | Simulated input, virtual device |
| `editor-core:699` | term | home | Simulated input as the editor's glossary words it (held by commands, timed in fixed steps); one glossary entry with `audio-input:688`, whose definition names the device; the holds in fixed steps stay `editor/stepping`'s |
| `audio-input:179` | feature | use | The `input.*` commands that drive this device (home `editor/stepping`) |
| `audio-input:521` | rule | use | Durations of simulated input count fixed steps (home `editor/stepping`) |
| `audio-input:689` | term | use | Hold (editor) (home `editor/stepping`) |
| `audio-input:464` | figure | link | Simulated holds in fixed steps (home `editor/stepping`) |
| `audio-input:164` | feature | link | Simulated actions (home `input/actions`) |
| `audio-input:483` | figure | use | The `input.state` answer as a text capture (home `audio/testing`) |
| `new:33` | hands-on | home | Exercises (D27): the merge rule changed in a scratch branch so that a simulated press over a key the device holds reports Pressed, then the input tests run to see which case fails and why, predicted first (modify; a patch: done). Evidence: `Strata/src/Strata/Input/Input.cpp:147-175`; `StrataTests/src/Core/InputTests.cpp:209` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| `BeginFrame`, input frames and the merged queries | `input/devices-state` | must |
| Gamepads and their axes | `input/gamepads` | must |
| Templates | `basics/cpp-generic` | must |
| Fixed steps | `core/time` | must |
| Pointers to members (`T C::*`) | `basics/cpp-generic` | helps |
| Same inputs, same game: deterministic results | `core/jobs` | helps |
| Simulated actions | `input/actions` | helps |
| Holds counted in fixed steps, `input.sequence` and `input.click` | `editor/stepping` | helps |
| Editor commands | `editor/commands` | helps |
| The feature test | `engineering/feature-test` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `audio-input:97` | feature | `editor/play-mode` | The editor keeping its master volume at Play and restoring it at Stop ("a game's volume setting belongs to the game session", `StrataEditor/src/Editor/EditorContext.cpp:1381, 1426-1427`) is taught with play mode, beside `editor-core:216-220`; `audio/engine` keeps one sentence with a link (critic-audio-input-12) |
| `audio-input:99` | feature | `editor-ui/inspectors` | The Asset tab's preview (`AudioPreview`, its waveform job, the drawing in `AssetInspectorPanel`) is editor code; that page's From names `AudioPreview` |
| `audio-input:471` | figure | `editor-ui/inspectors` | The screenshot of the preview goes with the preview |
| `audio-input:650` | term | `editor-ui/inspectors` | Waveform (preview) is the preview's term |
| `audio-input:174` | feature | `make/timers-events` | `KeyRepeat` runs inside the script module; that page's From names `KeyRepeat`, where game makers look for it |
| `audio-input:177` | feature | `editor-ui/game-view` | The Game view's focus, its call of `SetViewport` with the rendered resolution, ImGui ignoring a locked mouse and Shift+F1 are the Game view's (book.md, "Input ownership") |
| `audio-input:178` | feature | `editor/stepping` | The editor's `UpdateInputSuspension` (`StrataEditor/src/Editor/EditorContext.cpp:1620-1624`) lies inside that page's excerpt of `EditorContext.cpp:1560-1624` and is taught with pausing and stepping; `input/devices-state` keeps `Input::SetSuspended` and its timeline and links the editor's call (critic-audio-input-13) |
| `audio-input:479` | figure | `editor-ui/game-view` | The screenshot shows the Game view's cursor lock and its hint |
| `audio-input:179` | feature | `editor/stepping` | The `input.*` commands, `input.sequence` and `input.click` are that page's (book.md, "Simulated input") |
| `audio-input:464` | figure | `editor/stepping` | Holds counted in fixed steps are that page's |
| `audio-input:480` | figure | `editor/stepping` | The status bar's pill shows the editor's holds |
| `audio-input:521` | rule | `editor/stepping` | Durations of simulated input count fixed steps: the rule of the holds |
| `audio-input:689` | term | `editor/stepping` | Hold (editor) |
| `audio-input:181` | feature | `editor-ui/settings-windows` | The Input Actions page and `BindingCapture` are that page's custom settings pages |
| `audio-input:476-477` | figure | `editor-ui/settings-windows` | The Add binding popup and the capture's countdown are the drawing of the Input Actions page |
| `audio-input:187` | feature | `core/windows-events` | The event classes belong with windows and events (the inventory says so); `input/how-input-works` uses them to contrast events with polling |
| `audio-input:190` | feature | `ui/input` | The game UI's pointer and keyboard capture and its reading of `UIActionState` are UI input |
| `audio-input:191` | feature | `editor-ui/imgui-backends` | `ImGuiPlatform` reads its own input; the editor UI does not read `Input` |
| `audio-input:365` | concept | `scripting/host-api` | The inventory says the scripting area teaches crossing the ABI; `audio/scene-system` and `input/actions` show its audio and input instances |
| `audio-input:543` | rule | `scripting/host-api` | A rule of every host function |
| `audio-input:692` | term | `scripting/host-api` | Host function |
| `audio-input:541` | rule | `scripting/abi-sdk` | SDK helpers named like engine classes are a rule of the SDK |
| `audio-input:693` | term | `scripting/abi-sdk` | The text buffer protocol is the ABI's |
| `audio-input:539` | rule | `core/conventions` | A code-style rule of AGENTS.md; `audio/spatial` uses it to explain `NoAttenuation` |
| `audio-input:552-556` | hands-on | `make/sound` | A first sound, hearing space and impact sounds are game makers' exercises on sound |
| `audio-input:561` | hands-on | `make/sound` | Music and a volume option (load modes, engine-wide volume) |
| `audio-input:559` | hands-on | `make/animation` | Footsteps from animation events; that page's tutorial ends with footsteps |
| `audio-input:563-567` | hands-on | `make/input` | Reading the keyboard and a gamepad, mouse look, converting to input actions |
| `audio-input:570` | hands-on | `make/menus` | A rebinding menu: that page is the use home of binding capture and of the rebinding screen |
| `audio-input:573` | hands-on | `make/automated-playtests` | Letting an agent play with simulated input and fixed-step durations |
| `audio-input:633` | term | `core/jobs` | Sequence lock: one glossary entry with `foundation:600`; `core/jobs` keeps the excerpt of `SequenceLock.h`, and `audio/engine` quotes only its use (R31, "The sequence lock") |
| `audio-input:634` | term | `basics/threads` | Atomic, in general |
| `audio-input:638` | term | `assets/what-is-an-asset` | Cooked asset, in general |
| `audio-input:649` | term | `basics/math-interpolation` | Exponential smoothing is that page's (book.md, "Blending and smoothing") |
| `audio-input:651-652` | term | `world/systems` | Scene system; scene service and engine service (the glossary entry should name `core/engine-modules` as the home of engine services) |
| `audio-input:654` | term | `editor/play-mode` | Play mode and Simulate mode |
| `audio-input:666-667` | term | `basics/bytes` | UTF-8; code point and U+FFFD (text encodings are that page's) |
| `audio-input:690` | term | `core/time` | Fixed step |
| `audio-input:740` | open | `nowhere` | A note about files the survey only skimmed |
| `audio-input:755` | open | `appendix/history` | The release dating of audio and input is that page's subject; `input/actions` keeps one sentence (`new:15`) |
| `audio-input:761` | open | `nowhere` | A cosmetic slip in a comment banner of `AudioSystem.cpp:867`; no content for a reader |

## Not taken

none

## Questions for the planner

none

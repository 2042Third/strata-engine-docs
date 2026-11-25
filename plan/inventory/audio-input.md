# Inventory: Audio and input

Surveyed at `main` 822a7a46 of `G:/GameEngineAI`. All paths are relative to the repository root. Line numbers are those of
that commit. "DG" is `Docs/DeveloperGuide.md`, "AR" is `Docs/Architecture.md`.

Scope read: every file of `Strata/src/Strata/Audio/` (12 files, 2,371 lines) and `Strata/src/Strata/Input/` (17 files,
3,859 lines), the platform feed (`Strata/src/Platform/GLFW/GLFWWindow.cpp`), the frame loop's Input stage
(`Strata/src/Strata/Core/Application.cpp`), the audio importer (`Strata/src/Strata/Asset/AssetImporters.cpp`), the
lock-free hand-off (`Strata/src/Strata/Core/SequenceLock.h`), the scene and engine services
(`Strata/src/Strata/Scene/SceneServices.h`), the script SDK (`StrataScriptCore/Include/StrataScript/Audio.h`, `Input.h`,
`Gameplay.h`, the ABI's audio and input members), the host functions (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp`),
the editor's audio and input code (headers fully, bodies partly), the documentation sections named below, and the test
suites (names and the central cases).

Vendored libraries: miniaudio 0.11.25 (`Strata/vendor/miniaudio`, built with stb_vorbis in one translation unit,
`Strata/vendor/Implementations/MiniaudioImplementation.c`), GLFW 3.4 (`Strata/vendor/glfw`, whose `src/mappings.h` is
the SDL GameControllerDB compiled into GLFW: about 930 lines of controller mappings).

---

## 1. Features

### 1.1 Audio: the output engine (`AudioEngine`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Engine initialization | Opens the default output device through miniaudio's `ma_engine`; validates the sample rate (8,000 to 384,000 Hz) and channel count (1 to `MA_MAX_CHANNELS`); one listener. | `Audio/AudioEngine.h:17-27` (`AudioEngineSpecification`), `AudioEngine.cpp:162-223` (`Init`), `:85-117` (`InitializeEngine`) | DG "Audio" 2170-2176; AR 487-491 |
| Device fallback | No usable device: logs a warning and re-creates the mixer without a device ("null device"), so the game still runs. Only a mixer failure fails `Init`. | `AudioEngine.cpp:191-209` | DG 2172-2174 |
| Null device | Mixing without hardware: nothing is played, the mix advances only when pulled (`ReadFrames`) or advanced (`AdvanceNullDevice`, chunks of 1,024 frames, at most 1 s per call, fractional frames carried over). | `AudioEngine.h:20-22, 90-101`; `AudioEngine.cpp:21-24, 393-448` | DG 2172-2176; AR 738, 779 |
| Master volume | Linear gain on the final mix, clamped at 0, non-finite ignored; remembered while uninitialized. | `AudioEngine.cpp:274-294` | DG 2185-2187 |
| Engine pause | Stops a real device outright; the null device writes silence. Sources keep their state. (Not called by the editor or runtime: scene pause goes through `AudioSystem`; only tests call it.) | `AudioEngine.cpp:296-318` | header comment `AudioEngine.h:60-63` |
| Settings before Init | Master volume, pause and listener may be set while uninitialized; `Init` applies them, `Shutdown` resets them. | `AudioEngine.cpp:26-37, 54, 251` | `AudioEngine.h:50-52` |
| Listener | Position, forward, up, velocity; rejects non-finite and zero vectors; right-handed, +Y up, -Z forward (miniaudio's own defaults match). | `AudioEngine.cpp:320-362` | `AudioEngine.h:65-75` |
| Listener up hand-off | miniaudio's world-up is a plain (non-atomic) field read while mixing, so the main thread publishes it through a `SequenceLockedValue` and the mixing thread applies it in the `onProcess` callback after each period. | `AudioEngine.cpp:43-45, 62-71, 334-348`; `Core/SequenceLock.h:12-60`; test `AudioTests.cpp:1131-1162` | AR 205 |
| Engine one-shots | Fire-and-forget voices owned by the engine (`PlayOneShot`, `PlayOneShotAt`), capped by `MaxOneShots` (128 default) with voice stealing of the oldest; reclaimed in `Update`. Used by tests; game code uses the scene's one-shots instead. | `AudioEngine.cpp:119-158, 364-391` | DG 2186-2187 |
| Source registry | Every live `AudioSource` is in an intrusive doubly linked list (raw pointers, so static sources can unregister in any destruction order); `Shutdown` releases all their voices before the engine. | `AudioEngine.cpp:56-60, 225-252, 476-498` | `AudioSource.h:46-50` |
| Statistics | `AudioStats`: active voices, one-shots, allocated voices, sources. | `AudioEngine.h:37-44`; `.cpp:450-474` | — |
| Engine module | `AudioModule` (an `EngineModule` named "Audio") initializes the engine (failure logged, program continues), advances the null device by the frame step and reclaims one-shots every frame, shuts down after the job system. Editor and runtime list it; `--headless`/`--no-gpu` pass `NullDevice`. | `Audio/AudioModule.h:9-35`, `AudioModule.cpp:19-40`; `StrataEditor/src/EditorApplication.cpp:333`, `StrataRuntime/src/RuntimeApplication.cpp:485` | DG 2170-2176; AR 738-751, 779 |
| Build option | `STRATA_WITH_AUDIO` (on by default) builds miniaudio and the module; `ST_WITH_AUDIO` guards the composition root. | `CMakeLists.txt:29`, `Strata/CMakeLists.txt:27`, `Strata/vendor/CMakeLists.txt:132-141` | AR 41; Release 0.4.0 line 93 |

### 1.2 Audio: data (`AudioClip`, `AudioClipAsset`, importer)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Decoding | WAV, FLAC, MP3 and Ogg Vorbis (stb_vorbis) decoded by `ma_decoder` to 32-bit float at the file's own channel count and rate (resampling is per voice, so clips never depend on the engine's configuration). | `Audio/AudioClip.h:24-29`; `AudioClip.cpp:82-154` | DG 2166-2168; Release 0.3.0 line 36 |
| Load modes | `Decompressed`: decoded once into shared PCM, voices read it through private cursors (short effects). `Streamed`: keeps the encoded bytes, each voice owns a decoder (music, ambience). | `AudioClip.h:13-22`; `AudioVoice.cpp:197-215` | `AudioClip.h` comments |
| Safe decoding | Decodes in 16,384-frame chunks rather than trusting a header's length (a corrupt header could ask for any allocation); streamed clips get their length from the decoder, counting by decoding as a fallback. | `AudioClip.cpp:14, 33-78, 126-141` | comment at `:33-35` |
| Thread safety | Clips may load on worker threads and are immutable afterwards, so they are shared freely. | `AudioClip.h:27-29`; test `AudioTests.cpp:400` | — |
| Memory accounting | `GetMemoryUsage` (samples or encoded bytes); `AudioClipAsset::IsDataShared` while voices hold the clip (residency). | `AudioClip.cpp:178-181`; `AudioClipAsset.h:25-28` | — |
| Cooked format | "STAU" magic, version 1, load mode, then the original encoded file. | `Audio/AudioClipAsset.h:12-14`; `AudioClipAsset.cpp:9-49` | — |
| Asset loader | `AssetLoaderRegistry::Register(AssetType::AudioClip, ...)` in `RegisterAudioModule`. | `Audio/AudioRegistration.cpp:33-37` | AR 644 |
| Importer | `.wav .mp3 .flac .ogg`; setting `LoadMode` (files over 1 MiB start Streamed); validates by opening the file as streamed (header only); version 1. | `Asset/AssetImporters.cpp:84-136` | Release 0.3.0 line 36 |

### 1.3 Audio: voices and sources (`AudioVoice`, `AudioSource`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Custom data source | `ClipDataSource`, a miniaudio data source (vtable of read, seek, format, cursor, length) over a clip: zero-copy memcpy from shared frames, or the voice's decoder; the cursor mirrored in a lock-free atomic so the main thread can read the position without a data race. | `Audio/AudioVoice.cpp:20-134` | comments at `:20-24` |
| End handling | A decode error past the header counts as the end (the voice finishes instead of playing silence forever); reporting `MA_AT_END` with the final frames lets loops wrap within one read. | `AudioVoice.cpp:52-71` | — |
| Voice object | `AudioVoice` (internal header): one `ma_sound` in the node graph, created stopped with every setting applied, keeps its clip alive; miniaudio objects hidden in a heap `Data` because the graph keeps pointers into them. Destruction order: sound (waits for the audio thread), then decoder, then data source. | `Audio/AudioVoice.h:30-80`; `AudioVoice.cpp:138-234` | — |
| Lock-free parameters | Volume through the output bus volume (atomic), not `ma_sound_set_volume` (plain float). | `AudioVoice.cpp:304-311` | — |
| Attenuation models | `NoAttenuation`, `Inverse` (default), `Linear`, `Exponential`, clamped to [Min, Max] (OpenAL's "clamped" models); `NoAttenuation` is mapped to inverse with rolloff 0 because miniaudio's "none" also disables panning and Doppler; minimum distance kept above 0.01. | `Audio/AudioSource.h:15-24`; `AudioVoice.cpp:17-18, 338-361`; test `AudioTests.cpp:1041-1076` | — |
| Source | `AudioSource`: a voice with remembered settings (volume, pitch, looping, spatial, position, velocity, min/max distance, rolloff, model), usable before `Init` and after `Shutdown` (inert, keeps clip and settings). | `AudioSource.h:26-137`; `AudioSource.cpp` | DG 2166-2168 |
| Play/Pause/Stop/Seek | Play resumes, starts or restarts; Pause keeps position; Stop rewinds; Seek clamps and applies at once or on the next Play; position = mixer cursor (runs ahead of the audible output by up to one period). | `AudioSource.cpp:39-70, 199-232` | `AudioSource.h:69-114` |
| Finished-voice replacement | A voice that played to its end is replaced, never restarted, because the audio thread's deferred stop could silently undo a restart; a seek made just before the end still applies to the replacement. | `AudioVoice.cpp:241-260`; `AudioSource.cpp:39-54, 251-260`; tests `AudioTests.cpp:625, 663` | comments in place |
| Fresh voice after a stop | A voice that has played is replaced on Stop/Seek, because it holds up to one mixing period of audio already read from the old position. | `AudioSource.cpp:269-288`; test `AudioTests.cpp:488` | comment at `:276-278` |
| Input validation | Non-finite values ignored with a warning; negative volume/distances clamped; pitch must be > 0. | `AudioSource.cpp:77-197`; test `AudioTests.cpp:879` | — |

### 1.4 Audio: the scene (`AudioSystem`, components, services)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Components | `AudioSourceComponent` (Clip, Volume 0-4 slider, Pitch 0.01-8, Loop, PlayOnStart, Spatial, MinDistance, MaxDistance (default 50), Rolloff 0-100) and `AudioListenerComponent` (Active). Registered as "AudioSource" and "AudioListener", category Audio. No attenuation-model field: components always use Inverse. | `Audio/AudioComponents.h:11-28`; `AudioComponents.cpp:11-30` | AR 270 |
| "Audio" scene system | Play mode only (not Simulate), `OnLateUpdate`, after "Scripting", "Animation", "Physics" when present (soft constraints), profile stage `Scene.Audio`. | `AudioRegistration.cpp:39-48`; `AudioSystem.h:63-94` | DG 2177-2184 |
| Source lifecycle | Every active (in hierarchy, not pending destruction) entity with the component owns an `AudioSource`, made at start, on add or reactivation, released on removal, deactivation, destruction (at once via `OnEntityDestroying`) or stop. | `AudioSystem.cpp:197-201, 452-508, 717-746` | DG 2178-2180; test `AudioSystemTests.cpp:738` |
| Asynchronous clips | Per-record state `NoClip / Waiting / Ready / Unavailable`; a waiting source starts when ready if PlayOnStart or Play asked; unusable clips reported once; retried when the asset changes; reloads replace playing clips (via the asset manager's content version and change list). | `AudioSystem.h:168-195`; `AudioSystem.cpp:538-633, 748-781` | DG 2179-2180; tests `:181, 219, 256` |
| Change detection without signals | Component values are compared bitwise with the last applied values every frame and before every gameplay call, so plain field writes, `ComponentAccess` and the inspector apply without `MarkModified`. | `AudioSystem.cpp:32-36, 462-482, 510-536` | DG 2180-2181; test `:328` |
| Spatial sources | Position from the entity's world transform every frame (and at the moment of a gameplay call, so a pooled emitter plays where it is now). | `AudioSystem.cpp:643-662`; test `:964` | DG 2181-2182 |
| Doppler velocity | From the rigid body that simulates the entity or an ancestor (`IBodyMotionQuery::GetPointVelocity`), limited to 150 units/s; otherwise derived from moves over the time since the last move, smoothed (time constant 0.1 s), teleports (faster than 150 or no elapsed time) give none, still for two fixed steps means stopped. | `AudioSystem.h:98-102, 176-183`; `AudioSystem.cpp:45-65, 664-715`; test `:486` | DG 2181-2182 |
| Listener selection | First active `AudioListenerComponent` in hierarchy order, else the primary camera, else origin facing -Z; hierarchy order by comparing sibling-index paths, recomputed only when the candidates or the hierarchy version change. | `AudioSystem.cpp:81-96, 787-864`; tests `:628, 691` | DG 2182-2183 |
| Listener up policy | Level, upright listeners pass +Y (so the up vector never changes and never crosses to the mixing thread); rolled, vertical or upside-down ones pass their own. | `AudioSystem.cpp:24-28, 67-79`; test `:540` | — |
| Scene pause | `OnPausedChanged` pauses playing sources and one-shots and resumes them where they were; edits made while paused apply before resuming; sounds requested while paused start on resume; steps of a paused scene stay silent. | `AudioSystem.cpp:203-247`; tests `:820, 864` | DG 2183-2184 |
| Gameplay API | `Play`, `Pause`, `Stop`, `IsPlaying` (also true while waiting or paused by the scene), `Seek` (pending until the clip loads), `GetPlaybackPosition`, `PlayOneShot`, `PlayOneShotAt`, static master volume. | `AudioSystem.h:127-153`; `AudioSystem.cpp:253-365` | DG 2185-2188 |
| Scene one-shots | Each an `AudioSource` owned by the scene (pauses and stops with it), cap `c_MaxOneShots` 64 with the oldest cut off, wait for a loading clip at most 0.25 s of scene time ("a sound effect that comes long after its cause is worse than none"); drops counted and warned at most once per clip per second. | `AudioSystem.h:103-107, 197-204`; `AudioSystem.cpp:435-446, 869-966` | DG 2189-2194; test `:999` |
| Inspection | `GetVoices` (`AudioVoiceInfo` per source and one-shot), `GetStats` (`AudioSystemStats`), `GetListenerEntity`, `GetAudioSource`. | `AudioSystem.h:31-61, 159-166`; `AudioSystem.cpp:367-433` | DG 2189-2194 |
| Scene service `IAudioPlayback` | The gameplay API for other modules (scripts), registered by the system while it exists. | `Scene/SceneServices.h:240-262`; `AudioSystem.cpp:114-150` | DG 1884-1885 |
| Engine service `IAudioOutput` | Master volume for modules that may not include Audio; works with no scene audio. | `SceneServices.h:582-592`; `AudioRegistration.cpp:15-31` | DG 1884-1885; AR 205-207 |
| Works without output | Silent and never playing when the engine is not initialized; fine on the null device. | `AudioSystem.h:93-94`; test `:1097` | — |

### 1.5 Audio: scripting, editor, samples

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| SDK `AudioSource` | `Entity::GetAudioSource()`; Play, Pause, Stop, IsPlaying, Seek, GetPlaybackPosition; clip and settings are component properties. | `StrataScriptCore/Include/StrataScript/Audio.h:12-76, 117-120` | DG 1860, 2187-2188; skill `strata-scripting` |
| SDK `Audio` | PlayOneShot, PlayOneShotAt, Set/GetMasterVolume. | `Audio.h:78-115` | same |
| Host functions | `AudioPlay` ... `AudioGetMasterVolume` (10), appended to ABI version 1; misuse reported via `ScriptSystem::ReportProblem` (no audio, no component, inactive entity, bad volume or pitch). | `ScriptABI.h:440-461`; `Scripting/ScriptHostAPI.cpp:1590-1770` | DG 1884-1885, 1997-2016 |
| Editor play mode | Plays the scene's audio; restores the editor's master volume when play stops ("a game's volume setting belongs to the game session"). | `StrataEditor/src/Editor/EditorContext.cpp:1381, 1427` | `ScriptABI.h:458-459` |
| `audio.state` | Query command (play mode only): voices, one-shot counts, listener, master volume: "tools hear a game without a sound card". | `StrataEditor/src/Editor/Commands/AudioCommands.cpp:34-79` | DG 2192-2194 |
| Asset tab preview | `AudioPreview`: one preview `AudioSource` outside any scene, waveform (min/max per column) computed on a job, none beyond 600 s; drawn in the Asset inspector. | `StrataEditor/src/Editor/AudioPreview.h:15-66`; `Panels/AssetInspectorPanel.cpp:600-640` | Release 0.3.0 line 62 (and "only checked on the null device, not by ear", line 177) |
| Samples | Physics Playground impact one-shots scaled by speed (`Samples/PhysicsPlayground/Scripts/Impact.cpp:59-60`); Third-Person footsteps from animation events with random pitch (`Samples/ThirdPerson/Scripts/Footsteps.cpp:35`); Tetris (`TetrisBoard.cpp`). | `Samples/*/Scripts` | Release 0.5.0 lines 43, 60 |
| Feature test | `AudioFeatures` exercises every SDK audio call. | `StrataTests/FeatureTest/Scripts/AudioFeatures.cpp` | DG "Feature test" |

### 1.6 Input: codes and names

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Key codes | `KeyCode` (uint16) named by position on a US keyboard, GLFW's values (passed through by the GLFW backend), script ABI, never renumbered; `c_MaxKeyCode` 512. | `Input/KeyCodes.h:8-149` | AR 221-224 |
| Mouse codes | 8 buttons (`Left`=0, `Right`=1, `Middle`=2), `CursorMode` Normal, Hidden, Locked. | `Input/MouseCodes.h:8-40` | — |
| Gamepad codes | 15 Xbox-layout buttons, 6 axes, 4 gamepads; sticks -1..1 +Y up, triggers 0..1; `GetGamepadAxisMinimum`. | `Input/GamepadCodes.h:8-50` | AR 222-224 |
| Input names | `InputNames`: names for keys, mouse buttons ("Left", "Button3", aliases "Button0"-"Button2"), gamepad buttons and axes, case-insensitive lookups, name lists (used by commands, bindings, the editor page). | `Input/InputNames.h:14-45`, `InputNames.cpp` | AR 234-235; tests `InputTests.cpp:738-815` |

### 1.7 Input: devices and the per-frame state (`Input`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Polling API | Static, main thread: `IsKeyDown/Pressed/Released`, mouse buttons likewise, `GetMousePosition`, `GetMouseDelta`, `GetScrollDelta`, gamepads (`IsGamepadConnected`, buttons, `GetGamepadAxis` raw without dead zone). A press and release inside one frame reports both. | `Input/Input.h:43-115`; `Input.cpp:19-41, 334-518` | AR 221-224 |
| Input frame | `BeginFrame` clears transitions and deltas once the game has seen them, applies queued simulated events, counts `GetFrameIndex`. | `Input.cpp:553-586` | AR 791-793 |
| Suspension | `SetSuspended`: while the game does not update (editor paused, no step) input frames stop; transitions and queued events accumulate for the next update. | `Input.h:127-133`; `Input.cpp:123-125, 553-586`; test `InputTests.cpp:257` | DG 3779-3781; AR 230 |
| Enabled flag | `SetEnabled(false)` (editor Game view without focus): device queries report nothing (axes at rest) but state keeps tracking; simulated input still reaches the game. | `Input.cpp:154-160, 611-619`; tests `:127, 316` | AR 228-229 |
| Input viewport | `SetViewport(origin, size, resolution)`: positions relative to the viewport, scaled to the game's rendered resolution; `GetViewportSize` (resolution, else size, else window). | `Input.cpp:137-145, 364-375, 542-551, 631-636`; tests `:45, 72` | DG 2683-2690; AR 229-230 |
| Window seam | `InputWindow` (size, cursor mode), implemented by `Window`, keeps Input below the application shell. | `Input/InputWindow.h:8-20`; test `InputTests.cpp:91` | AR 225-226 |
| Cursor modes | `SetCursorMode` (editor fly camera, `StrataEditor/src/Panels/ViewportPanel.cpp:891, 927`) versus `SetGameCursorMode` (the game's wish, applied only while input is enabled; Normal while disabled; reset at play stop). | `Input.h:73-81`; `Input.cpp:283-288, 520-540, 611-619`; test `:476` | DG 1905-1907; AR 231-234 |
| Typed text | `GetTypedText`: UTF-8 of the frame's character events (layouts, dead keys, IMEs applied) then simulated text, whole characters up to 1,024 bytes, first typed kept; control characters, surrogates and invalid code points dropped; malformed simulated UTF-8 becomes U+FFFD. | `Input.h:88-92`; `Input.cpp:70-82, 182-281, 384-405, 681-685`; tests `:549, 585, 617` | DG 2716-2718; AR 235-236 |
| Pointer capture | `SetPointerCapture` (only the game UI sets it): hides buttons and scroll from gameplay; `GetPointerState` reads regardless. | `Input.h:19-32, 94-99`; `Input.cpp:407-415, 463-479`; test `:639` | DG 2691-2694 |
| Keyboard capture | `SetKeyboardCapture` (a text field being edited): hides keys and typed text from gameplay; `GetKeyState`, `GetUncapturedTypedText` read regardless. | `Input.h:34-41, 101-108`; `Input.cpp:417-434`; test `:681` | DG 2711-2715 |
| Raw queries | `IsRawKeyDown` and friends: devices and simulated input whatever enabled, captured or suspended (binding capture reads them). | `Input.h:110-115`; `Input.cpp:436-461` | DG 1551-1554 |
| Reset | `Input::Reset` restores everything (keeps the window) and resets the actions. | `Input.cpp:588-594` | DG 1486 |
| GLFW feed | Key, char, mouse button, scroll, cursor position callbacks call `Input::Process*` and also emit engine events; GLFW key repeat makes only events, never state. | `Platform/GLFW/GLFWWindow.cpp:286-365` | AR 224 |
| Gamepad polling | Every frame after `glfwPollEvents`: `glfwJoystickIsGamepad` + `glfwGetGamepadState` (GLFW's SDL mapping database), Y axes negated (+Y up), triggers remapped from -1..1 to 0..1; disconnected pads reported at rest. | `GLFWWindow.cpp:410-442`; `Input.cpp:663-679` | AR 222-224 |
| Frame-loop placement | Input stage: `Input::BeginFrame`, `Window::ProcessEvents`, `InputActions::Update`, before modules and layers. | `Core/Application.cpp:294-305` | AR 785-800, 873 |

### 1.8 Input: simulated device

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Virtual keyboard, mouse, gamepads | `SimulateKey`, `SimulateMouseButton`, `SimulateMouseMove`, `SimulateScroll`, `SimulateText`, `SimulateGamepadButton`, `SimulateGamepadAxis`, `ReleaseSimulatedGamepadAxis`: queued, applied at the next `BeginFrame` so every transition lasts a whole frame. | `Input.h:156-190`; `Input.cpp:58-104, 296-330, 687-739` | DG 3746-3758; AR 226-228 |
| Merge rules | A button is down while either source holds it; a transition of one source is no transition when the other held the button through the frame (a tool pressing a key a person holds changes nothing, never restarts a repeat). | `Input.cpp:147-175`; test `InputTests.cpp:209` | DG 3754-3755 |
| Simulated pointer | Once moved, its position replaces the device's; first move only establishes the position. | `Input.cpp:317-322, 364-369`; test `:339` | — |
| Simulated gamepads | Connected once used until cleared; a held axis replaces the device's value. | `Input.cpp:50-56, 306-316, 509-518`; test `:401` | AR 227-228 |
| Release and clear | `ReleaseAllSimulated` (queue releases; drop queued presses), `ClearSimulated` (forget without releases: session ended), `HasQueuedSimulatedInput`, `IsSimulated*` queries. | `Input.cpp:741-816`; tests `:297, 527` | DG 3756-3758 |

### 1.9 Input: actions (`InputActionSet`, `InputActions`)

Arrived in 0.6.0 (`Docs/Releases/0.6.0.md:94-100`).

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Model | `InputActionSet { Maps }`, `InputActionMap { Name, Enabled, Actions }`, `InputAction { Name, Kind, Bindings, DeadZone }`, kinds Button, Axis, Vector2; limits 32 maps, 256 actions, 8 bindings, names 1-64 chars; dead zone 0-0.9 (default 0.15). | `Input/InputActionSet.h:18-172` | DG 1449-1455 |
| Binding grammar | Text form `Key/<k>`, `Mouse/<b>`, `Gamepad/<button>`, `Gamepad/<axis>`, `Gamepad/<axis>+/-`, `Gamepad/LeftStick`, `1D:<neg>,<pos>`, `2D:<up>,<down>,<left>,<right>`; at most 96 bytes; case-insensitive parse, canonical `ToString`; one grammar for project file, commands, scripts, players' file. | `InputActionSet.h:40-95`; `InputActionSet.cpp:33-136, 414-486` | DG 1459-1465 |
| Kind fitting | `FitsKind`: Button takes button-like controls; Axis also whole axes and 1D; Vector2 sticks and 2D. | `InputActionSet.cpp:488-501` | DG 1463-1464 |
| Names | `<Map>/<Action>` or an unambiguous bare name; ambiguity refused naming every match. | `InputActionSet.cpp:683-735`; test `InputActionsTests.cpp:396` | DG 1456-1458 |
| Reserved UI map | Map `UI` with Buttons Submit, Cancel, Up, Down, Left, Right and defaults (Enter, KPEnter, Space, A; Escape, B; arrows, d-pad, left stick halves); added where missing; names/kinds fixed, bindings rebindable. | `InputActionSet.cpp:143-168, 503-514, 565-601`; `Input/UIActions.h:14-25` | DG 1500-1505 |
| Settings section | `Input.Actions` (title "Input Actions", category Input, JSON Schema, `Read` = FromJson then ToJson), registered by `RegisterInputModule`, first in the composition root. | `InputActionSet.cpp:176-226, 516-642`; `Input/InputRegistration.cpp:10-13`; `Engine/...:62` | DG 1444-1447; AR 634; Manual `Settings.md:67-80` |
| Evaluation | `InputActions::Update` once per frame; evaluates only when the input frame index advanced (transitions last one input frame, survive suspension); reads through gameplay queries (captures apply). | `Input/InputActions.h:230-252`; `InputActions.cpp:452-558, 710-723` | DG 1466-1483 |
| Combining bindings | Button: any binding down; Axis: binding of largest magnitude; Vector2: largest length; 2D composites normalized (diagonal length 1). | `InputActions.cpp:492-556` | DG 1470-1473 |
| Thresholds and hysteresis | Half axes and Axis/Vector2 down from 0.5, up below 0.35 (`c_Press`, `c_Release`), per gamepad for half axes. | `InputActions.h:247-248`; `InputActions.cpp:365-376, 536-542`; test `:597` | DG 1470-1473 |
| Radial dead zone | Length-based, rescaled to reach 1, the same as the SDK's `GetGamepadStick`. | `InputActions.cpp:441-450`; test `:529` | DG 1473 |
| Multiple gamepads | Gamepad bindings read every pad; whole axis takes the pad pushing furthest (with the Apple Clang 17 miscompile workaround). | `InputActions.cpp:358-424`; test `:563` | DG 1460-1461 |
| Map enable | `SetMapEnabled` applies from the next input frame; held actions report Released once, then up. | `InputActions.cpp:474-490, 829-851`; test `:673` | DG 1473-1476 |
| Live edits | `Refresh` compares `IProjectSettings::GetVersion()`; `Compile` rebuilds flat arrays keeping the state of actions with the same qualified name (and hysteresis of unchanged bindings), so an edit while playing does not press held actions again. | `InputActions.cpp:115-266`; test `:1081` | DG 1476-1479 |
| Fast reads | `FindIndex` + `GetStateAt` (valid until `GetVersion` changes), `GetStateVersion` to skip idle updates. | `InputActions.h:274-280`; `.cpp:809-827` | DG 1479-1483 |
| Players' bindings | `SetBindings` (validated; empty list unbinds), `ResetBindings`, `GetPlayerBindings`, `SaveBindings` (atomic write to `<IGameSaves dir>/InputBindings.json`), `LoadBindings` (max 64 KiB, forgiving per entry), `ReadSavedBindings`, `DeleteSavedBindings`; file format with header `{"Strata": {"Format": "InputBindings", "Version": 1}}`. | `InputActionSet.h:174-194`; `InputActionSet.cpp:748-841`; `InputActions.cpp:669-706, 853-992` | DG 1490-1499; Release 0.7.0 line 231 |
| Sessions | `ResetSession` (map enables, players' bindings, simulated actions, capture) at play start and stop; editor and `GameRuntime` call `LoadBindings` at start. | `InputActions.cpp:737-754`; `EditorContext.cpp:1395, 1633-1641`; `Runtime/GameRuntime.cpp:119-121, 173` | DG 1487-1489 |
| Simulated actions | `SimulateAction(name, down, value)` from the next input frame whatever the bindings; `ReleaseAllSimulated`, `ClearSimulated`. | `InputActions.cpp:994-1024`; test `:1137` | DG 1549-1550 |
| Binding capture | `BeginCapture(devices)`, listening for the next control going down from the raw state (also while suspended), every action up while listening; the captured control stays up for actions until released (`Suppressed`); one capture with a number (`GetCaptureId`); `GetCapturedBinding`, `TakeCapturedBinding`, `CancelCapture`, `GetCapturedControl`. | `InputActions.h:320-340`; `InputActions.cpp:72-82, 560-667, 1026-1071`; tests `:921-1080` | DG 1551-1562 |
| UI actions | `UIActionState`: down, pressed, repeated (after 0.4 s then every 0.1 s, unscaled time) for the six UI actions, read by index, idle updates cost a comparison. | `Input/UIActions.h:35-64`; `UIActions.cpp:39-88` | DG 2700-2706 |
| Performance | `Perf.Input.Actions256` (256 actions of 4 bindings, all gamepads): measured 7.451 us, budget 11.17 us. | `StrataTests/src/Perf/InputPerfTests.cpp:56`; `StrataTests/Perf/Budgets.json:218` | DG 1479-1480 |

### 1.10 Input: scripting, editor, runtime

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| SDK `Input` | Keys, mouse, scroll, gamepads (`GetGamepadAxis` with axial dead zone and rescale, `GetGamepadStick` radial), cursor mode, typed text, actions (`IsActionDown/Pressed/Released`, `GetActionValue`, `GetActionAxis`, map enable, bindings get/set/reset/save), capture (`BeginBindingCapture`, `PollBindingCapture`, `CancelBindingCapture`), `InputDevices` bits. | `StrataScriptCore/Include/StrataScript/Input.h` (532 lines; dead zones 326-353, actions 380-530) | DG 1905-1915, 1563-1579; Manual `Scripting.md:109-133` |
| SDK `KeyRepeat` | Key repeat helper running entirely inside the module (delay 0.25, interval 0.05). | `StrataScript/Gameplay.h:178-220` | DG 1968-1970 |
| ABI | Input functions in the initial set (`ScriptABI.h:389-398`), gamepads and cursor (`:552-570`), typed text (`:641-645`), 10 action functions and 3 capture functions appended (`:664-704`), enums `StrataScriptCursorMode` and `StrataScriptInputDevices` (`:222-258`). | `ScriptABI.h` | DG 1950-1955; Release 0.6.0 line 146 |
| Host functions | Key queries (`ScriptHostAPI.cpp:1017-1060`), gamepad/cursor (`:1129-1160`), typed text (`:2636`), actions (`:2752-2956`), capture with per-script ownership by capture id (`:2958-3029`). | `Scripting/ScriptHostAPI.cpp`; `ScriptSystem.h:147, 297` | DG 1563-1579 |
| Game view focus | Only the focused Game view in Play feeds `Input` (`SetEnabled`); `SetViewport` with the rendered resolution; a locked cursor makes ImGui ignore the mouse; Shift+F1 leaves. | `StrataEditor/src/Panels/GameViewPanel.cpp:240-281` | AR 231-234 |
| Input suspension in the editor | `UpdateInputSuspension`: paused game without a pending step suspends input frames. | `EditorContext.cpp:1620-1624` | DG 3779-3781 |
| `input.*` commands | `input.key`, `mouseButton`, `mouseMove`, `scroll`, `gamepadButton`, `gamepadAxis`, `action`, `releaseAll`, `state`, `sequence`, `click`, `type`; durations in fixed steps. | `StrataEditor/src/Editor/EditorInputCommands.cpp` (1,364 lines), `SimulatedInput.h/.cpp`, `InputSequence.h/.cpp` | DG "Simulated input" 3742-3807; Releases 0.3.0 line 95, 0.4.0 lines 77, 200-201, 0.5.0 line 71, 0.6.0 line 109 |
| `inputActions.*` commands | `setMap`, `setAction` (Edit, one project undo step), `resetPlayerBindings` (Session). | `StrataEditor/src/Editor/EditorInputActionsCommands.cpp` | DG 1506-1512, 1534-1541 |
| Input Actions page | Project Settings page: maps, actions, kinds, dead zones, binding chips, composites part by part, capture with 10 s timeout, "In play" markers, Reset Player Bindings. | `StrataEditor/src/UI/InputActionsPage.h/.cpp`, `UI/BindingCapture.h/.cpp` | DG 1512-1548; Manual `Settings.md:67-80` |
| Feature test | `InputFeatures` drives keys, mouse, scroll, gamepad, cursor, actions, rebinding, saving, capture. | `StrataTests/FeatureTest/Scripts/InputFeatures.cpp` | DG 1577-1579 |
| Samples | Third-Person's `Gameplay` map (Move, Look, Jump, Run, Pause, Wave, Dance, Respawn) and UI actions in menus; Showcase reads actions; others read devices. | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:108-189`, `FollowCamera.cpp:58`, `PauseMenu.cpp:40`, `MainMenu.cpp:66` | DG 1911-1913; Release 0.7.0 line 360 |

### 1.11 Boundary items (other areas teach them, this area depends on them)

- `Strata/src/Strata/Events/` (`KeyEvent.h`, `MouseEvent.h`): the event classes GLFW callbacks emit alongside the polled
  state; in the Input layer of `StrataTests/Architecture/Layers.json` (AR 579). Belongs with the application/event
  chapter, but the book must contrast events and polling here.
- The game UI's use of pointer/keyboard capture and `UIActionState` (`GameUI/`, DG "UI input" 2681-2728).
- `ImGuiPlatform`'s own input (AR 550-554): the editor UI does not read `Input`.

### How completeness was checked

- Every header of both folders is accounted for: Audio (`AudioClip.h`, `AudioClipAsset.h`, `AudioComponents.h`,
  `AudioEngine.h`, `AudioModule.h`, `AudioRegistration.h`, `AudioSource.h`, `AudioSystem.h`, `AudioVoice.h`) and Input
  (`GamepadCodes.h`, `Input.h`, `InputActionSet.h`, `InputActions.h`, `InputNames.h`, `InputRegistration.h`,
  `InputWindow.h`, `KeyCodes.h`, `MouseCodes.h`, `UIActions.h`); every public function of `Input.h`, `InputActions.h`,
  `AudioEngine.h`, `AudioSource.h` and `AudioSystem.h` appears in a row above.
- Registrations: components 2 (`AudioSource`, `AudioListener`); scene systems 1 ("Audio"); engine modules 1 ("Audio");
  asset types 1 (`AudioClip`: loader + importer); settings sections 1 (`Input.Actions`); scene services 1
  (`IAudioPlayback`); engine services 1 (`IAudioOutput`).
- Editor commands found by grepping string literals `"audio.*"`, `"input.*"`, `"inputActions.*"` in `StrataEditor/src`:
  16 (`audio.state`; 12 `input.*`; 3 `inputActions.*`: `inputActions.setMap`, `setAction`, `resetPlayerBindings`).
- Host functions: audio 10; input initial 9; gamepad 5; cursor 2; typed text 1; actions 10; capture 3 (40 total), read in
  `ScriptABI.h`.
- No shaders and no Python tools belong to this area.

---

## 2. Concepts to teach (dependency order)

### Part A: sound

**A1. What digital sound is.** Problem: a speaker cone moves continuously; a computer stores numbers. Ideas: sampling
(sample rate, Nyquist: 48 kHz holds up to 24 kHz), sample values (16-bit integers in files, 32-bit floats in mixers, -1
to 1), channels, *frame* = one sample per channel, interleaving (`L R L R`). Strata: mixes float stereo at 48 kHz
(`AudioEngine.h:23-24`); clips keep their own rate and channel count (`AudioClip.cpp:92-94`). Newcomers confuse frames
with samples (buffer sizes are `frames * channels` floats: `AudioEngine.cpp:410`) and think louder means "add 1" rather
than multiply (gain is linear; perceived loudness is logarithmic, decibels).

**A2. How audio hardware is fed: the pull model and its thread.** Problem: the device needs the next few milliseconds
on time, every time, or it clicks (underrun). Approaches: a callback on a high-priority audio thread that asks for N
frames (miniaudio, PortAudio, CoreAudio, WASAPI), or a queue the game pushes into (XAudio2 source voices, OpenAL
buffers). Trade-off: buffer size against latency. Strata: miniaudio's device thread pulls the node graph
(`AudioEngine.h:46-49`, "mixing runs on miniaudio's internal audio thread"). Newcomers do work proportional to the game
on the audio thread, or assume the main thread's frame and the audio period line up.

**A3. Real-time rules and lock-free hand-off.** Problem: the game changes parameters while the audio thread reads them;
a lock could make the audio thread wait for a slow main thread. Ideas: never block, allocate or log on the audio
thread; communicate through atomics or lock-free queues; publish whole values with a sequence lock; destroy shared
objects only after the reader let go. Strata: atomic cursor (`AudioVoice.cpp:33, 37`), output-bus volume chosen
because it is atomic (`:306-308`), `SequenceLockedValue` for the listener's up vector (`Core/SequenceLock.h:12-60`,
`AudioEngine.cpp:62-71`), `ma_sound_uninit` waits for the audio thread before the data source goes
(`AudioVoice.cpp:153-163`), and the main-thread-only API. Newcomers believe "it's just a float, a torn read is
harmless" (it is a data race, undefined behaviour) and miss that a state seen on one thread can change a moment later
(the finished-voice race, `AudioVoice.cpp:245-250`). Prerequisite: the book's threading/atomics chapter.

**A4. Codecs, decoding and streaming.** Problem: PCM is large (1 minute stereo float at 48 kHz is about 23 MB).
Approaches: decode at load (cheap playback, big memory), stream from memory or disk (small memory, CPU every period),
hardware/ADPCM formats in consoles; middleware lets each sound choose. Strata: the choice per asset (`LoadMode`;
over 1 MiB starts Streamed: `AssetImporters.cpp:87-99`), streamed voices decode from the encoded bytes in memory (not
from disk; "audio streamed from packs" is future work, Release 0.3.0 line 197). Resampling happens per voice so clips
are engine-independent (`AudioClip.cpp:92-93`). Newcomers stream short, frequent sounds (one decoder per voice) or
decompress hour-long music, and trust a file header's length (`AudioClip.cpp:33-35`).

**A5. Mixing: voices, gain, the node graph, voice limits.** Problem: many sounds at once must become one stream.
Ideas: a voice per playing instance, sum with gain, master gain, clipping/limiting; node graphs and buses (groups with
their own volume and effects); voice limits and voice stealing (oldest, quietest, lowest priority); virtual voices.
Strata: one `ma_sound` per voice in miniaudio's graph (`AudioVoice.h:30-35`), master volume (`AudioEngine.cpp:274-289`),
caps with oldest-first stealing (engine `MaxOneShots` 128, scene `c_MaxOneShots` 64: `AudioEngine.cpp:143-150`,
`AudioSystem.cpp:895-900`). No buses, effects, priorities or virtual voices (Release 0.7.0 line 415 lists "an audio
mixer" as future). Newcomers forget that sums overflow above 1 (master volume 4 x 0.5 sources clip).

**A6. Sources and their state machine.** Problem: games need play, pause, stop, seek, loop with predictable
semantics while the audio thread runs ahead. Strata: `AudioSource` remembers settings independent of the engine
(`AudioSource.h:43-53`), replaces voices rather than rewinding them (`AudioSource.cpp:269-288`) because a voice that
played holds a period of already-read audio. Newcomers expect `GetPlaybackPosition` to equal what is heard (it runs
ahead by up to one period: `AudioSource.h:112-113`).

**A7. 3D sound: listener, panning, attenuation.** Problem: sound should come from where its source is. Ideas: a
listener with a position and orientation (forward, up, right = forward x up), panning by the angle (stereo pan laws;
HRTF for headphones; surround), distance attenuation curves (inverse = physical 1/r, linear, exponential), min and max
distance, rolloff, the "clamped" OpenAL models; occlusion, reverb zones (not in Strata). Strata: right-handed, +Y up,
-Z forward listener (`AudioEngine.h:46-49`), the four models with clamping (`AudioSource.h:15-24`), test-proven panning
(`AudioTests.cpp:1095-1129`). Newcomers set MaxDistance below MinDistance (Strata treats it as MinDistance:
`AudioVoice.cpp:359`), use linear falloff and are surprised by silence at MaxDistance, or think non-spatial sounds have
a position.

**A8. The Doppler effect.** Problem: a passing car's pitch drops. Ideas: frequency shift from relative velocity along
the line between source and listener against the speed of sound; it diverges near the speed of sound; velocity must
be per second, not per frame. Approaches: take velocities from physics, or differentiate positions, which is noisy when
positions change only on fixed steps and frames run at another rate. Strata: body velocity when there is a body, else
position differences over the time since the last move, exponentially smoothed, with a teleport threshold of 150 units/s
and "stopped after two fixed steps without moving" (`AudioSystem.cpp:664-700`, header `:76-82`). Newcomers compute
velocity per frame (jitters between 0 and 2x at mismatched rates) or pass a teleport as a huge velocity (a squeal).

**A9. Audio in a scene/ECS.** Problem: game objects with sound components must map to engine voices, created and
destroyed as entities come and go, clips loading asynchronously, the game paused and resumed. Approaches: event-driven
(components signal changes) or diffing (compare with last applied). Strata: the "Audio" scene system diffs component
values (bitwise floats so NaN applies once: `AudioSystem.cpp:32-36`), records per entity, runs late in the frame after
the systems that move things, pauses with the scene, plays only in Play mode, and exposes itself through a scene service
so scripts never include Audio. Newcomers start sounds in Simulate mode (no audio system), or call `AudioEngine`
directly (sounds do not pause with the game).

**A10. Fire-and-forget sounds and latency budgets.** Problem: an impact needs a sound now; the clip may not be loaded.
Strata: scene one-shots wait at most 0.25 s, then drop with a warning ("a sound effect that comes long after its cause is
worse than none": `AudioSystem.cpp:955`), so games request clips early (`Assets::RequestLoad`, `AudioFeatures.cpp:19-20`).

**A11. Testing sound without ears.** Problem: CI machines have no sound card; "it sounds right" is not a test.
Ideas: a null device pulled by the test, synthesised signals (sine waves) with known RMS, steady-state measurement after
gain smoothing settles, ratios rather than absolute levels. Strata: `AudioTestUtils.h` (`ScopedAudioEngine`, `Render`,
`ComputeRms`, `MeasureRms`, 2,400 settle frames, sine RMS 0.3536), `audio.state` for agents. Newcomers measure before the
spatializer's smoothing settles and get flaky tests.

**A12. The audio landscape.** FMOD and Wwise (middleware with authoring tools, buses, events, parameters), OpenAL Soft,
XAudio2, platform APIs, miniaudio (single-file C, MIT-0/public domain). Strata takes miniaudio: one portable file, a
node graph, decoders and spatialization included (the CMake comment `Strata/vendor/CMakeLists.txt:132` and AR 81).

### Part B: input

**B1. Where input comes from.** Problem: the OS delivers keyboard, mouse and controller activity as events to a window.
Ideas: event queues and callbacks (GLFW), key codes by position (scancode-like) versus characters by layout, key
repeat. Strata: GLFW callbacks feed both events and polled state (`GLFWWindow.cpp:286-365`); key codes are GLFW's,
named by US position (`KeyCodes.h:10-11`); OS key repeat never changes state (only `KeyPressedEvent(…, true)`).
Newcomers treat key codes as characters (on AZERTY `Key::A` is the key where A sits on a US keyboard), and use key repeat
for movement.

**B2. Polling and edges: down, pressed, released.** Problem: gameplay asks "is jump held / was it pressed this frame?"
Ideas: keep current state plus per-frame transition flags; clear transitions at frame start; a press and release inside
one frame must report both. Strata: `ButtonStates` with three bitsets (`Input.cpp:19-41`), cleared in `BeginFrame`.
Newcomers derive "pressed" by comparing with last frame's down state (loses taps shorter than a frame) or read Pressed in
a fixed-update that runs zero or several times per frame (missed or doubled presses).

**B3. Mouse spaces and cursor modes.** Window pixels, the game's viewport inside an editor panel, the game's render
resolution; deltas versus positions; scroll as deltas; cursor hidden/locked (relative mouse for first-person cameras).
Strata: `SetViewport(origin, size, resolution)` and scaling (`Input.cpp:137-145, 364-375`), game versus editor cursor
modes (`Input.h:73-81`). Newcomers use positions for mouse look (it stops at the screen edge), forget DPI and panel
offsets, or leave a locked cursor when the game loses focus.

**B4. Gamepads.** Problem: hundreds of controller models report buttons and axes in different orders. Ideas: a mapping
database (SDL GameControllerDB) to a standard Xbox-like layout; axis conventions (Y up or down; triggers 0..1 or -1..1);
dead zones (axial per axis versus radial on the stick vector; rescaling so the edge still reaches 1); hysteresis for
"axis as button". Strata: GLFW's built-in mapping DB (`glfwGetGamepadState`, `GLFWWindow.cpp:416-442`), conversions to
+Y up and 0..1 triggers, raw axes in `Input`, dead zones in the SDK and actions (`Input.h` SDK `:326-353`,
`InputActions.cpp:441-450`), thresholds 0.5/0.35. Newcomers apply an axial dead zone per axis (diagonals snap to
cardinal directions), forget the rescale (a jump from 0 to 0.15), and compare a stick to 0.5 without hysteresis (flicker).

**B5. Text input is not key input.** Ideas: character events after layouts, dead keys and IMEs; Unicode code points;
UTF-8 encoding. Strata: `ProcessText` from GLFW's char callback, UTF-8 assembly and validation, 1,024-byte cap
(`Input.cpp:182-281`). Newcomers build text from `IsKeyPressed` (no shift, no accents, no IME).

**B6. Focus, enabling and capture: who gets the input.** Problem: the same keyboard drives the editor, the game, the
game's UI and a text field. Ideas: input layers/consumption, focus ownership, capture while a gesture is in progress.
Strata: `SetEnabled` (Game view focus), pointer capture (UI owns the gesture), keyboard capture (text field), binding
capture (every action up), and raw reads that ignore all of them. Newcomers read raw devices in gameplay (typing a name
moves the player) or cannot work out why a click on a UI button is invisible to gameplay.

**B7. Actions instead of keys.** Problem: players remap controls; the same intent comes from a key, a stick, a d-pad.
Approaches: Unity's Input System (actions, maps, bindings, composites, processors, interactions), Unreal's Enhanced
Input (mapping contexts, modifiers, triggers), Godot's InputMap. Ideas: action kinds (button, 1D, 2D), composites (WASD
to a vector), contexts/maps enabled per mode (walking, driving), combination rules, persistence of player rebinding.
Strata: maps of Button/Axis/Vector2 actions, text bindings, a reserved UI map, players' file in the save directory, no
modifiers/chords/processors (DG 1464-1465, Release 0.7.0 lines 361-362). Newcomers normalise composites wrongly (WASD
diagonal 1.41 fast), or forget that disabling a map while a button is held must release it.

**B8. Evaluating actions once per frame and staying correct under edits.** Ideas: compile the definitions into flat
arrays; evaluate once per input frame; keep state across rebuilds by a stable key; versions so readers can cache
indices. Strata: `Compile` and `Evaluate` (`InputActions.cpp:117-239, 452-558`), `GetStateVersion`, `FindIndex`.
Newcomers look up by string every call in hot paths, or re-create state on a settings change (held actions press again).

**B9. "Press a key to bind".** Problems: the press that is captured must not also trigger the action or click the button
that started the capture; must work while the game is paused; several owners (editor page, game menu) share one
listener. Strata: compare raw state with the state at capture start, report the first control going down, suppress it
for actions until released, numbered captures (`InputActions.cpp:560-667, 1026-1071`; editor `UI/BindingCapture.h`).

**B10. Simulated input, determinism and fixed steps.** Problem: automated tests and AI agents must play the game
reproducibly, independent of frame rate and window focus. Ideas: a virtual device whose events are queued and applied at
the frame boundary; merging with real devices; durations in simulation steps, not frames or wall time; suspending input
frames while paused so nothing is lost. Strata: `Input::Simulate*` (`Input.cpp:687-739`), merge rules
(`:147-175`), the editor's `SimulatedInput` holds counted in fixed steps (`SimulatedInput.h:45-60`), `input.sequence` one
step per frame with bit-for-bit results at 1, 16.7 and 50 ms frames (DG 3785-3792). Newcomers time taps in frames (a
120 Hz machine presses half as long) or apply simulated events immediately (seen by half the frame's systems).

**B11. Crossing the script ABI.** Scripts reach audio and input only through C host functions taking plain data:
strings for action names and bindings (`'\n'`-separated), the text buffer protocol for returned strings, failure values
and `ReportProblem` instead of asserts (`ScriptHostAPI.cpp:1590-1653, 2752-3029`). Taught in the scripting area;
this area shows its audio/input instances.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/Input/Input.cpp:19-41` | `ButtonStates`: down/pressed/released as three `std::bitset`s and the one `Set` that records edges; why a tap inside a frame reports both. | bitsets, B2 |
| 2 | `Strata/src/Strata/Input/Input.cpp:553-586` | `BeginFrame`: clearing transitions only once the game saw them, suspension, applying the simulated queue at the frame boundary. | B2, frame loop |
| 3 | `Strata/src/Strata/Input/Input.cpp:147-175` | Merging two input sources; the "held throughout" rule that makes a tool's press over a person's hold no transition. Pointer-to-member template. | 1, templates |
| 4 | `Strata/src/Platform/GLFW/GLFWWindow.cpp:286-319` and `:416-442` | Feeding the engine from GLFW: key callback (state plus event, repeat only as event), gamepad polling with axis conventions (+Y flip, trigger remap). | B1, B4, lambdas as C callbacks |
| 5 | `Strata/src/Strata/Core/Application.cpp:294-305` | Where input sits in the frame (Input stage before modules and layers). | frame loop chapter |
| 6 | `Strata/src/Strata/Input/Input.cpp:364-375, 137-145` | Coordinate mapping window -> viewport -> game pixels; simulated pointer override. | B3, vec2 math |
| 7 | `Strata/src/Strata/Input/Input.cpp:182-215, 224-281` | UTF-8 encoding and a robust decoder (overlongs, surrogates, truncation -> U+FFFD). | B5, bit operations |
| 8 | `StrataScriptCore/Include/StrataScript/Input.h:326-353` | Axial versus radial dead zone with rescaling, in 25 lines a game developer can copy. | B4, vector length |
| 9 | `Strata/src/Strata/Input/InputActionSet.h:63-95` with `InputActionSet.cpp:488-501` | A binding grammar as a data type, and the kind-fitting rule. | B7 |
| 10 | `Strata/src/Strata/Input/InputActionSet.cpp:414-472` | Hand-written parser for `1D:` / `2D:` composites with precise error messages. | string_view, optional |
| 11 | `Strata/src/Strata/Input/InputActions.cpp:452-558` | Central algorithm: per-frame action evaluation (combining bindings by kind, composites, dead zone, hysteresis, simulated holds, Pressed/Released derivation, map disable releasing). Long but the heart of the area. | 8-10, B7 |
| 12 | `Strata/src/Strata/Input/InputActions.cpp:341-381` | Hysteresis per gamepad for half axes (`held ? > 0.35 : > 0.5`). | B4 |
| 13 | `Strata/src/Strata/Input/InputActions.cpp:405-420` | A real compiler miscompile and its workaround (comparing gamepads, not a running value): why the comment names the compiler version. | portability |
| 14 | `Strata/src/Strata/Input/InputActions.cpp:117-239` | Compiling definitions into flat arrays while carrying state across rebuilds by a stable lower-case key. | B8, unordered_map |
| 15 | `Strata/src/Strata/Input/InputActions.cpp:596-667` | Binding capture: edge detection against the raw state at start, device order, half axes with hysteresis, suppression. | B9 |
| 16 | `Strata/src/Strata/Input/UIActions.cpp:39-88` | Menu key repeat (delay then interval, at most one per update), and skipping idle updates by version. | B2 |
| 17 | `Strata/src/Strata/Audio/AudioVoice.cpp:20-77, 126-134` | A custom miniaudio data source: C-style vtable in C++, standard layout static_asserts, zero-copy reads, the atomic cursor, end-of-clip signalling for loops. | A1, A3, C interop |
| 18 | `Strata/src/Strata/Audio/AudioVoice.cpp:138-164` | Destruction order with a real-time reader: uninit the sound (waits for the audio thread) before the data it reads. | A3, RAII |
| 19 | `Strata/src/Strata/Audio/AudioVoice.cpp:241-260` with `AudioSource.cpp:39-54` | A race with the audio thread (deferred stop undoing a restart) and the fix: replace finished voices, retry once. | A3, A6 |
| 20 | `Strata/src/Strata/Audio/AudioSource.cpp:269-288` | Why a stopped voice is replaced: buffered audio from the old position. | A2, A6 |
| 21 | `Strata/src/Strata/Core/SequenceLock.h:12-60` with `AudioEngine.cpp:62-71, 334-348` | A sequence lock, the memory fences, and its use to hand the listener's up vector to the mixing thread. | atomics, memory order |
| 22 | `Strata/src/Strata/Audio/AudioEngine.cpp:162-223` | Graceful degradation: device, then null device, then failure; validation first. | A2 |
| 23 | `Strata/src/Strata/Audio/AudioEngine.cpp:124-158` | Voice limit with oldest-first stealing. | A5 |
| 24 | `Strata/src/Strata/Audio/AudioClip.cpp:33-58` | Decoding untrusted files in chunks instead of trusting a header length. | A4, vectors |
| 25 | `Strata/src/Strata/Audio/AudioVoice.cpp:338-361` with `AudioSource.h:15-24` | Attenuation models and the mapping trick for NoAttenuation. | A7 |
| 26 | `Strata/src/Strata/Audio/AudioSystem.cpp:664-700` with `:45-65` | Deriving Doppler velocity robustly (time since last move, exponential smoothing `1 - exp(-t/tau)`, teleports, stop detection). Central algorithm of the scene side. | A8, fixed step |
| 27 | `Strata/src/Strata/Audio/AudioSystem.cpp:717-746` with `:510-536` | Diffing ECS components against applied values, pruning records with an update counter (`SeenUpdate`). | A9, EnTT views |
| 28 | `Strata/src/Strata/Audio/AudioSystem.cpp:67-96, 834-864` | Listener choice by hierarchy order via sibling-index paths compared lexicographically, cached by version; the up-vector policy. | A7, scene hierarchy |
| 29 | `Strata/src/Strata/Audio/AudioSystem.cpp:869-966` | Scene one-shots: asynchronous clip wait with a deadline, drop accounting. | A10, asset states |
| 30 | `Strata/src/Strata/Audio/AudioRegistration.cpp:28-49` | How a module plugs into the engine: components, engine service, asset loader, scene system with soft ordering. | module registration chapter |
| 31 | `StrataTests/src/Audio/AudioTests.cpp:1095-1129` with `AudioTestUtils.h:56-81` | Testing spatial audio by RMS per channel on the null device. | A11, doctest |

Shorter supporting snippets: `AudioComponents.cpp:11-30` (reflection registration with ranges), `AudioModule.cpp:19-40`
(an engine module), `ScriptHostAPI.cpp:1631-1653` (host function pattern for audio), `ScriptHostAPI.cpp:2958-2991`
(per-script capture ownership), `Gameplay.h:178-220` (`KeyRepeat` in a script), `Samples/PhysicsPlayground/Scripts/Impact.cpp:55-61`
(impact volume and pitch from speed).

---

## 4. Figures

### Diagrams

1. **Audio stack (data flow)**: `AudioSourceComponent` -> `AudioSystem` record -> `AudioSource` -> `AudioVoice` ->
   `ma_sound` (+ `ClipDataSource`, decoder) -> `ma_engine` node graph (spatializer, master volume) -> device or null
   device; the shared `AudioClip` beside it; scripts entering through `IAudioPlayback`, master volume through `IAudioOutput`.
2. **Two threads (sequence/ownership)**: main thread (all API calls) and the audio thread (mixing periods); what crosses:
   atomic cursor, atomic bus volume, sequence-locked up vector applied in `onProcess`, `ma_sound_uninit` waiting.
3. **Clip memory layout**: interleaved float frames `[L0 R0 L1 R1 ...]` shared by N voices each with a cursor (Decompressed)
   versus encoded bytes shared with one decoder per voice (Streamed); memory and CPU per mode.
4. **Mixing period timeline**: device pulls 10-ish ms periods; main frames at 16.7 ms; where the cursor is versus the
   audible sample (the "runs ahead by one period" note); underrun.
5. **AudioSource / voice state machine**: no clip, no voice (engine off), stopped, playing, paused, ended (replaced on
   Play), engine shutdown (inert); transitions for Play, Pause, Stop, Seek, SetClip.
6. **AudioSystem record state machine**: ClipState `NoClip / Waiting / Ready / Unavailable` with `PlayRequested`,
   `PausedByScene`, `PendingSeek` annotations; asset reload edge.
7. **Attenuation curves (plot)**: gain against distance for Inverse, Linear, Exponential, NoAttenuation with Min 1, Max 50,
   Rolloff 1 and 2, clamped regions shaded.
8. **Listener frame and panning (top view)**: forward -Z, up +Y, right +X; a source at +X louder in the right channel;
   facing +Z flips it; rolled listener.
9. **Doppler velocity derivation (timeline)**: fixed steps at 60 Hz versus frames at 144 Hz; naive per-frame velocity
   alternating 0 / large versus Strata's time-since-move with smoothing; teleport cut-off.
10. **One-shot lifecycle**: request -> waiting (<= 0.25 s scene time) -> playing -> reclaimed; drops (cap 64 oldest cut,
    late clip, unplayable); pause/resume.
11. **Frame timeline with audio and input**: Input stage (BeginFrame, ProcessEvents, InputActions::Update), layers
    (scene systems: UI, Scripting, Physics, Animation, Audio in OnLateUpdate), module OnUpdate (AdvanceNullDevice,
    one-shot reclaim), render.
12. **Input data flow**: OS -> GLFW callbacks / joystick polling -> `Input::Process*` -> device state; tools ->
    `Simulate*` queue -> applied at `BeginFrame`; merged queries -> gameplay / UI / `InputActions` -> scripts via host.
13. **Edge flags over frames (timeline)**: a key held three frames, a tap inside one frame, transitions cleared by
    `BeginFrame`.
14. **Merge truth table**: device held throughout / pressed / released versus simulated likewise -> what the game sees.
15. **Suspension (timeline)**: editor paused; device presses accumulate; the step frame reports them; frame index stops.
16. **Viewport coordinate mapping**: window, panel image rect (origin, size), render resolution; formula of
    `GetMousePosition`.
17. **Gamepad conventions**: Xbox layout with `GamepadButton` indices; stick axes +Y up; triggers 0..1; GLFW's conversion.
18. **Dead zones (plots)**: axial square dead zone versus radial circle; rescaled response curve; diagonal behaviour.
19. **Hysteresis (plot)**: value over time with press at 0.5 and release at 0.35, output square wave without flicker.
20. **Input action model (class diagram)** and **compiled form (memory layout)**: `ActionRecord[]`, `CompiledBinding[]`,
    `InputControl[]`, `HalfAxisHeld[]` indices.
21. **Action evaluation per kind (flowchart)**: Button / Axis / Vector2 branches, dead zone, hysteresis, simulated override,
    Pressed/Released formulas.
22. **Binding capture (state machine)**: idle -> listening (all actions up) -> captured (result waiting) -> taken;
    suppression until release; replaced by another owner; timeout/cancel.
23. **Players' bindings (data flow)**: project section + `InputBindings.json` -> `Compile`; Save/Load/Delete; editor
    `.strata/Saves`; runtime user data folder.
24. **Who sees what (table/diagram)**: gameplay queries, `GetPointerState`/`GetKeyState`, raw queries, actions, against
    enabled flag, pointer capture, keyboard capture, binding capture.
25. **Simulated holds in fixed steps (timeline)**: `input.key {steps: 3}` going down in the next input frame and up
    after the frame whose update ran the third step, at one and at several steps per frame.

### Screenshots (editor; none is a rendering feature)

1. Inspector of an entity with **Audio Source** (Clip, Volume slider, Pitch, Loop, PlayOnStart, Spatial, Min/Max
   Distance, Rolloff) and **Audio Listener**: any sample entity, e.g. Physics Playground.
2. **Asset tab audio preview**: a selected clip (Third-Person footsteps or a music file), waveform drawn, Play pressed
   with the position and length shown; and the same with the length/rate/channels line when stopped.
3. **Import settings of an audio clip**: `LoadMode` Decompressed/Streamed with its tooltip.
4. **Project Settings > Input Actions** with the Third-Person project: maps list (UI marked as navigation), the Gameplay
   map's actions with kinds, dead zones, binding chips.
5. **Add binding popup** building a 2D composite part by part.
6. **Binding capture** listening line with the 10 s countdown and Cancel.
7. **"In play" markers and Reset Player Bindings** after a play session saved bindings.
8. **Game view with a locked cursor** and the Shift+F1 / Ctrl+P hint.
9. **Status bar pill of simulated holds** ("Space, W, Gamepad 1 LeftX 0.50") while an agent holds keys.
10. **Console warning of a dropped one-shot** ("Audio: dropped a one-shot of '...': its clip took longer than 0.25 s to load").

Non-image figures: `audio.state` and `input.state` JSON answers from StrataCLI (code blocks), and a recorded short
clip/plot of the left/right RMS as a listener turns (audio cannot be shown as a screenshot).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Game code plays sound through `AudioSystem` (scripts: the SDK), never `AudioEngine`** (AGENTS.md "Audio"): engine
   one-shots belong to no scene, so they would not pause with the game or stop when play stops (DG 2186-2187).
2. **The audio API is main-thread only; only the mixer runs on the audio thread** (`AudioEngine.h:46-49`): every setter
   goes through miniaudio's lock-free parameters; calling from jobs would race.
3. **Never write a value the audio thread reads without atomics**: the listener's up vector travels through a sequence
   lock, volume through the atomic bus volume, the cursor through an atomic (`AudioEngine.cpp:43-45`,
   `AudioVoice.cpp:306-308, 23-24`). A torn float is undefined behaviour, not "slightly wrong".
4. **Release the sound before what it reads** (`AudioVoice.cpp:153-163`); **release every voice before the engine**
   (`AudioEngine.cpp:240-246`): the node graph keeps pointers.
5. **Do not restart a finished voice; replace it** (`AudioVoice.cpp:245-250`): the audio thread's pending stop can undo
   the restart silently.
6. **A stopped or seeked voice that played is replaced** (`AudioSource.cpp:276-283`): it holds a period of audio from
   the old position you would hear first.
7. **Do not trust a file's declared length** (`AudioClip.cpp:33-35`): a corrupt header could request any allocation;
   decode in chunks. Truncated and garbage bytes must be rejected without crashing (AGENTS.md "Asset pipeline").
8. **Request clips before you need them** (`Audio.h:82-84`, `AudioFeatures.cpp:19-20`): one-shots wait at most 0.25 s,
   then drop; a late sound is worse than none.
9. **Limit Doppler speeds and treat jumps as teleports** (`AudioSystem.h:98-100`): near the speed of sound the pitch shift
   is unbounded; a teleport is not a velocity.
10. **Derive velocity over the time since the last move, not the frame** (`AudioSystem.cpp:684-688`): fixed-step motion
    seen at another frame rate would alternate between still and fast.
11. **Zero vectors and NaNs are refused at the boundary** (`AudioEngine.cpp:327-331`): miniaudio normalizes vectors; a
    zero forward turns the whole mix into NaNs.
12. **Audio plays only in Play mode** (`AudioRegistration.cpp:39-44`): Simulate runs physics only; script audio calls
    fail there and are reported.
13. **Assets by handle, never blocking** (AGENTS.md "Assets"): `AudioSystem` polls `GetAsset` each frame
    (`AudioSystem.cpp:558-578`) and `GetAssetState(Loading)` rather than loading synchronously.
14. **Input is main-thread polling state, updated once per frame** (`Input.h:43-48`); read Pressed/Released in
    `OnUpdate`, not `OnFixedUpdate`, which may run zero or several times in a frame (SDK `Input.h:383`).
15. **Simulated events apply at the next input frame** (`Input.h:156-161`): applied immediately, half the frame's systems
    would see the press and half would not.
16. **Durations of simulated input count fixed steps, never frames** (AGENTS.md "Editor"; DG 3770-3784): the same command
    must give the same game at any frame rate.
17. **Suspend input frames while the game does not update** (`Input.h:127-131`): otherwise presses made while paused
    pass unseen.
18. **Gameplay reads rebindable controls as input actions** (AGENTS.md "Scripting"; DG 1910-1913): fixed keys cannot be
    rebound by players; device reads only for what nobody rebinds (mouse look, text, debug keys).
19. **Only `InputActions` touches the players' bindings file** (DG 1913-1915): scripts' save files cannot name it, so a
    game cannot corrupt it and the editor can reset it.
20. **Disabling a map releases its held actions once** (`InputActions.cpp:476-479`): code waiting for a release (a
    charged jump) is never left waiting.
21. **An edit of the actions keeps the state of unchanged actions** (`InputActions.cpp:115-116`): otherwise every held
    action would press again in a running game.
22. **A capture's press triggers nothing** (`InputActions.h:320-324`): otherwise binding Escape would also close the
    rebinding menu, and a captured click would press the button that started the capture again.
23. **Key codes are ABI and never renumbered** (`KeyCodes.h:10-11`, `GamepadCodes.h:8-10`): compiled script modules embed
    them.
24. **The game's cursor mode applies only while it has the input** (`Input.h:76-79`): a locked cursor must not trap the
    person in the editor after the game loses focus.
25. **Unscoped enums never use `None`; X11 defines it** (AGENTS.md code style): hence `AudioAttenuationModel::NoAttenuation`
    (`AudioSource.h:20`).
26. **SDK helpers named like engine classes are tested only in script modules** (DG 1968-1970): `KeyRepeat`, `Random`,
    `Timer` would violate the one-definition rule in an engine translation unit.
27. **Host functions report misuse and return failure values** (`ScriptHostAPI.cpp:1590-1653`): a script asking for a
    misspelled action every frame is reported once and reads "up", never crashes the editor.

---

## 6. Hands-on

### For game developers

1. **Your first sound** (easy): import a WAV, add an Audio Source to an entity, Play; then a looping ambience with
   PlayOnStart. Proves: assets, components, Play mode only.
2. **Hear space** (easy): make the source spatial, walk the camera around it, tune Min/Max distance and Rolloff; add an
   Audio Listener to the player instead of the camera. Proves: listener selection, attenuation.
3. **Impact sounds** (medium): a script's `OnCollisionEnter` plays `Audio::PlayOneShotAt` with volume and pitch from the
   impact speed (as `Samples/PhysicsPlayground/Scripts/Impact.cpp`), requesting the clip in `OnCreate`. Proves: one-shots,
   the 0.25 s rule, variation.
4. **Footsteps from animation events** (medium): `OnAnimationEvent("Footstep")` with random pitch (Third-Person
   `Footsteps.cpp`). Proves: event-driven sound.
5. **Music and a volume option** (easy): a streamed music clip, `Audio::SetMasterVolume` from a UI slider; observe the
   editor restoring its volume at stop. Proves: load modes, engine-wide volume.
6. **Read the keyboard and a gamepad** (easy): move a cube with `IsKeyDown`, jump on `IsKeyPressed`, then with
   `GetGamepadStick`; print raw `GetGamepadAxis` with dead zone 0 to see stick noise. Proves: polling, dead zones.
7. **Mouse look** (medium): lock the cursor, rotate with `GetMouseDelta`, free it in a pause menu. Proves: cursor modes,
   deltas versus positions.
8. **Convert to input actions** (medium): define `Gameplay/Move` (Vector2: `2D:Key/W,Key/S,Key/A,Key/D` and
   `Gamepad/LeftStick`), `Gameplay/Jump` (Button), use `GetActionValue`; add a Vehicle map and toggle maps. Proves: the
   action model, composites, maps.
9. **A rebinding menu** (hard): list bindings, capture with `BeginBindingCapture`/`PollBindingCapture`, timeout with
   `CancelBindingCapture`, `SetActionBindings`, `SaveBindings`, "Reset to defaults"; check "In play" in the editor.
   Proves: players' bindings, capture semantics.
10. **Let an agent play it** (medium): drive the game with `input.key {steps}` and `input.action`, read `audio.state` and
    `input.state`, then write an `input.sequence` and check it is identical at different frame rates. Proves: simulated
    input, fixed-step timing.

### For engine developers

1. **Add an attenuation-model field to `AudioSourceComponent`** (medium): enum property, registry, `ApplyComponent`,
   feature test, `AudioSystemTests`. Proves: component pipeline, diffing, golden rule 6.
2. **Write the missing test**: a Linear-model source exactly at MaxDistance with Rolloff 0.5 (easy); proves the RMS test
   method.
3. **Audio buses** (hard, design exercise): add `ma_sound_group` buses (Music, Effects, UI) with volumes as engine
   service and script API; ABI append rules. Proves: node graph, ABI evolution.
4. **Distance culling / virtual voices** (hard): stop mixing inaudible sources beyond MaxDistance and resume them.
   Proves: voice management.
5. **Measure the hand-off** (medium): replace the sequence lock with a mutex in a scratch branch and explain why that is
   wrong on the audio thread; read the test `AudioTests.cpp:1131-1162`. Proves: real-time rules.
6. **Explain a race** (medium, reading): walk through `AudioVoice::Start` and `AudioSource::Play`'s retry with a timeline
   of both threads. Proves: A3/A6.
7. **A new binding control** (hard): mouse wheel as a half-axis control (`Mouse/WheelUp`): grammar, `FitsKind`,
   `ReadValue`, capture, round-trip and sweep tests. Proves: the action pipeline end to end.
8. **Modifiers** (hard, design): "Ctrl+S" chords: where in `Evaluate` and in the grammar; how capture should handle it.
   Proves: understanding evaluation order.
9. **Trace a simulated tap** (medium, reading): from `input.key` to `SimulatedInput::Press` to `Input::SimulateKey` to
   `BeginFrame` to the script's `IsKeyPressed`, with frame and step numbers. Proves: timing model.
10. **Profile actions** (easy): run `Perf.Input.Actions256` in Release and explain why the compiled flat arrays and
    `GetStateVersion` exist. Proves: data layout for hot paths.
11. **Second window backend thought experiment** (medium): what a non-GLFW backend must translate (key, mouse, gamepad
    codes, axis conventions; `InputWindow`). Proves: the platform seam.

---

## 7. Glossary

- **Sample**: one number describing the sound wave's value at an instant for one channel.
- **Sample rate**: samples per second per channel (Strata mixes at 48,000 Hz).
- **Channel**: one independent signal (mono 1, stereo 2).
- **Frame (audio)**: one sample of every channel at one instant; not a rendered frame.
- **Interleaved**: channels stored alternately (`L R L R`).
- **PCM**: uncompressed sampled audio.
- **Codec / decoder**: code that turns a compressed format (MP3, Vorbis, FLAC) into PCM.
- **WAV, FLAC, MP3, Ogg Vorbis**: container/codec formats Strata imports (FLAC lossless, MP3/Vorbis lossy).
- **Resampling**: converting audio from one sample rate to another (miniaudio does it per voice).
- **Mixer**: code that sums voices into the output stream.
- **Voice**: one playing instance of a clip in the mixer (`AudioVoice`).
- **Source**: a configurable, controllable voice (`AudioSource`); also the component that describes one.
- **One-shot**: a fire-and-forget voice that is reclaimed when it ends.
- **Voice stealing**: cutting off a playing voice (Strata: the oldest) to make room for a new one.
- **Node graph**: miniaudio's network of processing nodes the mix flows through.
- **Bus / group**: a mixing node several voices feed, with its own volume and effects (not in Strata).
- **Gain**: a multiplier applied to a signal; linear volume.
- **Decibel (dB)**: logarithmic loudness unit; -6 dB is about half amplitude.
- **RMS**: root mean square, the average power of a signal; what Strata's tests measure.
- **Clipping**: samples beyond [-1, 1] cut off, an audible distortion.
- **Output device**: the sound card endpoint the mix is played on.
- **Null device**: Strata's mode of mixing without a device, advanced by the frame time or pulled by tests.
- **Mixing period**: the block of frames the audio thread produces in one pass.
- **Underrun**: the device ran out of audio in time; heard as a click or gap.
- **Latency**: delay between asking for a sound and hearing it.
- **Audio thread**: the real-time thread miniaudio mixes on.
- **Lock-free**: synchronization in which no thread ever waits for another.
- **Sequence lock**: a lock-free scheme where a writer bumps a counter around a write and readers retry if it changed.
- **Atomic**: a variable whose reads and writes cannot tear and may order memory.
- **Data source (miniaudio)**: an object with read/seek/format/cursor/length callbacks that a sound plays from.
- **Cursor**: a voice's current frame in its clip.
- **Load mode (Decompressed / Streamed)**: whether a clip is decoded once at load or by each voice as it plays.
- **Cooked asset**: the engine's processed binary form of an imported file ("STAU" header for clips).
- **Listener**: the "ears" in the world: position, forward, up, velocity.
- **Spatialization**: positioning a sound relative to the listener (attenuation, panning, Doppler).
- **Panning**: distributing a sound between left and right (or more) speakers.
- **HRTF**: head-related transfer function, filtering that gives 3D cues on headphones (not in Strata).
- **Attenuation**: loss of volume with distance; **attenuation model**: the curve (inverse, linear, exponential).
- **Min distance / max distance**: the range over which attenuation applies; full volume inside min, constant beyond max.
- **Rolloff**: steepness factor of the attenuation curve.
- **Doppler effect**: pitch change from relative motion of source and listener.
- **Pitch**: playback rate; 2 plays twice as fast and an octave higher.
- **Teleport (audio)**: a move too fast to be motion; given no Doppler velocity.
- **Exponential smoothing**: blending toward a new value by `1 - exp(-dt / tau)`.
- **Waveform (preview)**: the per-column minimum and maximum of a clip, drawn in the Asset tab.
- **Scene system**: an engine-registered per-scene updater (the "Audio" system).
- **Scene service / engine service**: interfaces a system or module offers other modules without them including it
  (`IAudioPlayback`, `IAudioOutput`).
- **Play mode / Simulate mode**: running a scene with scripts and audio, or with physics only.
- **Polling**: reading the current input state when you need it, instead of reacting to events.
- **Event (input)**: a message that something changed (key pressed), delivered once.
- **Down / Pressed / Released**: held now / went down this frame / went up this frame.
- **Edge (transition)**: a change of a button's state.
- **Input frame**: the span between two `Input::BeginFrame` calls that the game updated in.
- **Suspended input frames**: input frames halted while the game does not update; transitions wait.
- **Key code**: Strata's number for a physical key position (GLFW values, US layout names).
- **Scancode**: the hardware/OS position code of a key (GLFW translates it to key codes).
- **Key repeat**: the OS sending repeated presses while a key is held; Strata's `KeyRepeat` and `UIActionState` do their own.
- **Typed text / character event**: characters produced by the keyboard after layouts and IMEs.
- **IME**: input method editor, composing characters (Chinese, Japanese) from several keys.
- **UTF-8**: the variable-length byte encoding of Unicode text Strata uses everywhere.
- **Code point**: a Unicode character number; **U+FFFD** the replacement character for invalid input.
- **Surrogate**: code points reserved for UTF-16 pairs, invalid on their own.
- **Viewport (input)**: the region of the window that receives game input, and its resolution.
- **Cursor mode**: Normal, Hidden, Locked (hidden, confined, unbounded relative motion).
- **Mouse delta**: movement since the last frame.
- **Gamepad mapping**: the table that turns a controller's raw buttons/axes into the standard layout (SDL GameControllerDB in GLFW).
- **Axis**: an analog input; **stick** (two axes), **trigger** (one axis 0..1).
- **Half axis**: one direction of an axis used as a button (`Gamepad/LeftX+`).
- **Dead zone**: a small range around rest read as zero; **axial** per axis, **radial** on the stick's length.
- **Rescaling**: stretching the range beyond the dead zone so full tilt still reads 1.
- **Hysteresis**: different thresholds for turning on (0.5) and off (0.35), to avoid flicker.
- **Input action**: a named control (Jump, Move) the game reads instead of a key.
- **Action kind**: Button, Axis (-1..1), Vector2 (two values, length <= 1).
- **Binding**: a control (or composite) that drives an action, written as text.
- **Composite (1D / 2D)**: an axis from two buttons or a vector from four.
- **Action map**: a group of actions enabled and disabled together (Gameplay, Vehicle, UI).
- **Qualified name**: `<Map>/<Action>`; **bare name**: the action name alone when unambiguous.
- **UI map**: the reserved map with Submit, Cancel and four directions the game UI navigates with.
- **Players' bindings**: the player's replacements of an action's bindings, kept in `InputBindings.json`.
- **Binding capture**: listening for the next control pressed, to bind it.
- **Suppression (capture)**: keeping the captured control up for actions until released.
- **Simulated input / virtual device**: input produced by tools and tests, merged with real devices.
- **Hold (editor)**: one command's press of a control, possibly a tap of N fixed steps.
- **Fixed step**: one constant-length simulation update (physics, `OnFixedUpdate`); the time base of simulated durations.
- **Pointer capture / keyboard capture**: the game UI taking the mouse or keyboard from gameplay.
- **Host function**: a C function the engine gives script modules through the ABI table.
- **Text buffer protocol**: the ABI's way of returning a string: the caller passes a buffer and capacity, the host returns the size.

---

## 8. Proposed chapters (teaching order)

1. **Sound inside a computer** (concept, both, S). Samples, frames, channels, formats, gain and decibels, the pull model.
   Prereq: none. Afterwards the reader can explain what a mixer does each period. 0 screenshots.
2. **Strata's audio engine: device, mixer and the audio thread** (internals, engine, L). `AudioEngine`, miniaudio,
   null-device fallback, master volume, the real-time rules and the sequence lock, the engine module. Prereq: ch. 1,
   threading and atomics, engine modules/frame loop. 0 screenshots.
3. **Clips, voices and sources** (internals, engine, L). `AudioClip` load modes and safe decoding, the cooked asset and
   importer, `AudioVoice`'s custom data source, `AudioSource` semantics and its two races. Prereq: ch. 2, asset pipeline.
   1 screenshot (import settings).
4. **Sound in space: listener, attenuation and Doppler** (concept + internals, both, M). Panning, models, min/max/rolloff,
   Doppler and velocity estimation. Prereq: ch. 3, vectors. 0 screenshots (plots).
5. **The Audio scene system** (internals, engine, L). Records, diffing, asynchronous clips, listener selection, pause,
   one-shots, services, inspection. Prereq: ch. 4, ECS/scene systems/services, physics bodies (velocity). 2 screenshots
   (components, dropped one-shot warning).
6. **Making your game sound good** (tutorial, game, M). Components, the Asset tab preview, one-shots from collisions and
   animation events, music, volume option, `audio.state`. Prereq: ch. 5 (or just editor and scripting basics). 2
   screenshots (preview, inspector).
7. **Testing sound without speakers** (internals, engine, S). Null device, RMS tests, settle frames, `audio.state` for
   agents. Prereq: ch. 2-5, testing chapter. 0 screenshots.
8. **Input devices and the per-frame state** (concept + internals, both, L). Events versus polling, GLFW feed, edges,
   input frames and suspension, enabled flag, typed text, captures, raw reads. Prereq: frame loop, platform layer. 0
   screenshots.
9. **Mouse, cursor and the game view** (internals, both, M). Coordinate spaces, render resolution, cursor modes in the
   game and the editor, Shift+F1. Prereq: ch. 8, editor basics. 1 screenshot (locked cursor hint).
10. **Gamepads: mappings, axes and dead zones** (concept + internals, both, M). Mapping databases, conventions, axial and
    radial dead zones, hysteresis, multiple pads. Prereq: ch. 8, vector math. 0 screenshots (plots).
11. **Input actions: from keys to intents** (internals, engine, XL). Model, grammar, section, compilation, evaluation,
    map enables, live edits, players' bindings, capture, UI actions, performance. Prereq: ch. 8-10, project settings,
    JSON. 0 screenshots.
12. **Controls players can change** (tutorial, game, M). The Input Actions page, reading actions in scripts, maps,
    a rebinding menu with capture and saving, "In play". Prereq: ch. 11 or editor/scripting basics. 5 screenshots
    (page, composite popup, capture, In play, Game view).
13. **Letting tools play: simulated input** (internals, engine, M). Virtual device and merge rules, editor holds in fixed
    steps, `input.sequence`, `input.click`, `input.action`, determinism. Prereq: ch. 8, 11, editor command system, fixed
    step. 1 screenshot (holds pill).
14. **Reference: audio and input APIs** (reference, both, M). Tables of components, SDK calls, host functions, commands,
    constants (limits, thresholds), file formats. Prereq: none. 0 screenshots.

---

## 9. Not determined

- **Bodies only skimmed or not read**: `StrataEditor/src/Editor/EditorInputCommands.cpp` (1,364 lines: the input.*
  command handlers; known from DG "Simulated input"), `InputSequence.cpp`, `SimulatedInput.cpp`,
  `EditorInputActionsCommands.cpp`, `UI/InputActionsPage.cpp`, `UI/BindingCapture.cpp`, `AudioPreview.cpp` (waveform
  job), `InputActionSet.cpp:176-380` (JSON Schema, `ReadAction`, `ReadMap`) and `:644-746` (name validation, lookups),
  the rest of `InputNames.cpp`, most test bodies (only names and the spatial tests were read), the game UI's consumer of
  `UIActionState` and captures, `Events/` beyond `KeyEvent.h`.
- **miniaudio internals**: the exact pan law, spatializer gain smoothing, Doppler factor and speed of sound are
  miniaudio defaults (Strata sets no Doppler factor); not verified in the vendored source.
- **Mixing period length** on real devices (the tests assume about 11 ms at 48 kHz: `AudioTestUtils.h:26-27`); depends on
  the backend.
- **`AudioEngine::SetPaused`** is documented "e.g. while the editor pauses the game" (`AudioEngine.h:60-61`) but nothing
  outside tests calls it; the editor pauses audio through the scene (`AudioSystem::OnPausedChanged`). Whether that header
  comment is out of date was not settled.
- **Minimized or unfocused windows**: whether audio keeps playing when a shipped game is in the background was not found;
  the release notes say gamepads are still read in the background (Release 0.7.0 line 363).
- **Releases**: the documents date audio, basic input, gamepads and simulated input to 0.3.0, `input.sequence`/`input.click`
  and UI navigation to 0.4.0, simulated input at time scale 0 to 0.5.0, input actions and rebinding to 0.6.0, the players'
  bindings in the user data folder of shipped games to 0.7.0; finer dating (which wave added the listener up hand-off,
  Doppler from bodies, `audio.state`) was not traced in the Roadmap.
- **Hardware behaviour**: the release notes state the audio preview was "only checked on the null audio device, not by
  ear" (0.3.0 line 177, repeated through 0.5.0); no evidence that 3D panning and Doppler were judged by listening.
- A cosmetic slip: `AudioSystem.cpp:867` has a section banner merged into the comment line ("// One-shots\t////...").

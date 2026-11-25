---
id: reference/audio-input
title: "Audio and input reference"
description: "The sound formats, attenuation models, limits, key and button names, binding grammar and reserved UI map of Strata's audio and input, in tables."
kind: reference
size: M
tracks: []
needs: [input/actions]
status: final
---

This page holds the facts of audio and input that no catalogue page holds. The rows of the audio components `AudioSource` and `AudioListener` are in [Components](../reference/components.md). The `Input.Actions` section is in [Settings](../reference/settings.md). The `audio.state`, `input.*` and `inputActions.*` commands are in [Commands](../reference/commands.md). The script SDK's `AudioSource`, `Audio`, `Input` and `KeyRepeat` are in [the script reference](../reference/script-api.md).

Each table below has a short introduction that names the page teaching its subject. A row is one fact, and a column says what kind of fact it is.

## Audio

### Source formats and the cooked clip

A clip holds one recorded sound that voices play (see [Clips, voices and sources](../audio/clips-voices-sources.md)). When you add a sound file to a project, the audio importer reads it, checks that it decodes, and stores a cooked copy. The table lists what the importer accepts and decides. You choose the load mode per file: **Decompressed** decodes the clip once and shares the samples, which suits short effects, while **Streamed** keeps the encoded :term[bytes]{id=byte} and decodes while a voice plays, which suits music.

Facts from `Strata/src/Strata/Asset/AssetImporters.cpp` and `Strata/src/Strata/Audio/AudioClip.h`.

| Fact | Value |
| --- | --- |
| Source formats | `.wav`, `.mp3`, `.flac`, `.ogg` (Ogg Vorbis) |
| Import setting | `LoadMode`: `Decompressed` or `Streamed` |
| Default load mode | `Streamed` for a file larger than 1 MiB (1,048,576 bytes), else `Decompressed` |
| Check at import | The file opens as a streamed clip, so its :term[header]{id=header} parses; a file that does not fails the import |
| Importer version | :value{key="importer.AudioClip.version"} |
| Decoded form | 32-bit floating-point samples, at the file's own channel count and sample rate |

The cooked clip is the asset that the game loads. It starts with three 32-bit :term[unsigned integers]{id=unsigned-integer} in little-endian order, and the original encoded file follows them. Facts from `Strata/src/Strata/Audio/AudioClipAsset.cpp`.

| Offset | Size | Content |
| --- | --- | --- |
| 0 | 4 bytes | The magic `STAU` (the value 0x55415453) |
| 4 | 4 bytes | The format version, 1 |
| 8 | 4 bytes | The load mode: 0 for `Decompressed`, 1 for `Streamed` |
| 12 | the rest | The encoded :term[source file]{id=source-file}, as imported |

A loader rejects a file whose magic, version or mode differs, with the message "Not a cooked Strata audio clip".

### Attenuation models and units

Attenuation is the fall of loudness with distance from the listener (see [Sound in space](../audio/spatial.md)). The engine's audio source supports four models. The `AudioSource` component has no model property: its sources always use `Inverse`.

In the formulas, $d$ is the distance, first held between `MinDistance` and `MaxDistance` for every model, so no sound gets quieter beyond `MaxDistance`; $d_{\min}$ is `MinDistance`, $d_{\max}$ is `MaxDistance`, and $r$ is `Rolloff`. The result is a gain, 1 for full volume and 0 for silence. Facts from `Strata/src/Strata/Audio/AudioSource.h`.

| Model | Gain at distance $d$ | Note |
| --- | --- | --- |
| `NoAttenuation` | 1 at every distance | The sound is still panned and shifted by the Doppler effect |
| `Inverse` | $d_{\min} / (d_{\min} + r (d - d_{\min}))$ | The default; the one every `AudioSource` component uses |
| `Linear` | $1 - r (d - d_{\min}) / (d_{\max} - d_{\min})$ | Silent at $d_{\max}$ when $r$ is 1 |
| `Exponential` | $(d / d_{\min})^{-r}$ | Falls faster the larger $r$ is |

For example, with `MinDistance` 1, `Rolloff` 1 and a listener 5 metres away, the `Inverse` gain is $1 / (1 + 4) = 0.2$.

The audio properties have no descriptions in the editor, so this table gives their units. Facts from `Strata/src/Strata/Audio/AudioComponents.cpp` and `Strata/src/Strata/Audio/AudioComponents.h`.

| Property | Unit and range | Default |
| --- | --- | --- |
| `Volume` | Linear gain, 0 to 4 in the editor; 1 plays the clip as recorded | 1 |
| `Pitch` | Rate factor, 0.01 to 8; 2 plays twice as fast and twice as high | 1 |
| `MinDistance` | Metres; inside it the gain stays 1 | 1 |
| `MaxDistance` | Metres; beyond it the gain stops falling, and the `Linear` model reaches its end there | 50 |
| `Rolloff` | Factor, 0 to 100, in the formulas above | 1 |

### Limits

These constants bound what the sound of a playing scene can cost. The Doppler effect is the pitch shift of a sound whose source moves; [the spatial page](../audio/spatial.md) explains it, and the :term[scene system]{id=scene-system} owns one-shots (see [the audio scene system page](../audio/scene-system.md)). A one-shot is a sound that the scene starts and owns, with no entity. Facts from `Strata/src/Strata/Audio/AudioSystem.h` and `Strata/src/Strata/Audio/AudioEngine.h`.

| Name | Value | Meaning |
| --- | --- | --- |
| `c_MaxOneShots` | 64 | One-shots of a scene that play at once; beyond it the oldest stops |
| `c_MaxDopplerSpeed` | 150 metres per second | A rigid body's speed is limited to it; a faster move of another entity counts as a teleport and gives no Doppler shift |
| `c_MaxOneShotClipWait` | 0.25 seconds | The longest a one-shot waits for its clip to load; a later sound is dropped |
| `c_VelocitySmoothingTime` | 0.1 seconds | The time constant that smooths velocities derived from moves |
| `MaxOneShots` | 128 | The engine's own one-shot cap, a field of `AudioEngineSpecification` that tests use |

A one-shot that is cut off, dropped or cannot be played logs a warning that names the clip.

### Audio statistics and services

`AudioStats` is what the engine counts about its mixer; [the audio engine page](../audio/engine.md) shows where the numbers come from. Facts from `Strata/src/Strata/Audio/AudioEngine.h`.

| Field | Counts |
| --- | --- |
| `ActiveVoices` | Voices that play now, sources and one-shots together |
| `ActiveOneShots` | One-shot voices the engine holds, finished ones included until the next update reclaims them |
| `AllocatedVoices` | Voices that hold mixer resources: sources with a clip, and one-shots |
| `SourceCount` | Live `AudioSource` objects |

Engine code reaches sound only through two interfaces, which [the scene system page](../audio/scene-system.md) describes. `IAudioPlayback` is a :term[scene service]{id=scene-service}, and `IAudioOutput` is an engine service. Facts from `Strata/src/Strata/Scene/SceneServices.h`.

| Function | What it does |
| --- | --- |
| `IAudioPlayback::Play`, `Pause`, `Stop` | Start or resume, hold the position, or return to the start of the entity's source |
| `IAudioPlayback::IsPlaying`, `Seek`, `GetPlaybackPosition` | Ask whether the source plays, jump to a second, read the second it is at |
| `IAudioPlayback::PlayOneShot`, `PlayOneShotAt` | Play a fire-and-forget sound, without space or at a world position; false for a clip that cannot be played or bad numbers |
| `IAudioPlayback::HasSource` | Whether the entity has an `AudioSource`, active or not |
| `IAudioOutput::SetMasterVolume`, `GetMasterVolume` | Set or read the master volume: 0 silences, 1 is full volume |

## Input

### Names of keys, buttons and axes

A binding names a control with text, and the `input.*` commands spell controls the same way (see [Input actions](../input/actions.md)). Names ignore case when read. A :term[key code]{id=key-code} says where the key is on a keyboard of the United States layout, and the engine never changes codes, because scripts depend on them. Facts from `Strata/src/Strata/Input/InputNames.cpp`, `Strata/src/Strata/Input/KeyCodes.h`, `Strata/src/Strata/Input/MouseCodes.h` and `Strata/src/Strata/Input/GamepadCodes.h`.

| Names | Codes |
| --- | --- |
| `Space` | 32 |
| `Apostrophe`, `Comma`, `Minus`, `Period`, `Slash` | 39, 44, 45, 46, 47 |
| `D0` to `D9` (the digit row) | 48 to 57 |
| `Semicolon`, `Equal` | 59, 61 |
| `A` to `Z` | 65 to 90 |
| `LeftBracket`, `Backslash`, `RightBracket`, `GraveAccent` | 91, 92, 93, 96 |
| `World1`, `World2` (keys of other layouts) | 161, 162 |
| `Escape`, `Enter`, `Tab`, `Backspace`, `Insert`, `Delete` | 256 to 261 |
| `Right`, `Left`, `Down`, `Up` | 262 to 265 |
| `PageUp`, `PageDown`, `Home`, `End` | 266 to 269 |
| `CapsLock`, `ScrollLock`, `NumLock`, `PrintScreen`, `Pause` | 280 to 284 |
| `F1` to `F25` | 290 to 314 |
| `KP0` to `KP9` (the digits of the numeric block) | 320 to 329 |
| `KPDecimal`, `KPDivide`, `KPMultiply`, `KPSubtract`, `KPAdd`, `KPEnter`, `KPEqual` | 330 to 336 |
| `LeftShift`, `LeftControl`, `LeftAlt`, `LeftSuper` | 340 to 343 |
| `RightShift`, `RightControl`, `RightAlt`, `RightSuper`, `Menu` | 344 to 348 |

A code is below `c_MaxKeyCode`, which is 512, and a name that is not here names no key.

The mouse has 8 buttons, `c_MaxMouseButtons`, numbered from 0. The gamepad table follows. The sticks range from -1 to 1 with +Y up, and the triggers range from 0 to 1 (see [Gamepads](../input/gamepads.md)).

| Kind | Names in code order |
| --- | --- |
| Mouse buttons 0 to 7 | `Left`, `Right`, `Middle`, `Button3`, `Button4`, `Button5`, `Button6`, `Button7` (`Button0` to `Button2` also mean the first three) |
| Gamepad buttons 0 to 14 | `A`, `B`, `X`, `Y`, `LeftBumper`, `RightBumper`, `Back`, `Start`, `Guide`, `LeftThumb`, `RightThumb`, `DPadUp`, `DPadRight`, `DPadDown`, `DPadLeft` |
| Gamepad axes 0 to 5 | `LeftX`, `LeftY`, `RightX`, `RightY`, `LeftTrigger`, `RightTrigger` |

### The binding grammar

A binding is text in the project file, in commands, in scripts and in the players' bindings file. The grammar below shows each shape with one example. The action's kind decides which shapes fit: a `Button` takes controls that are down or up, an `Axis` takes those, whole axes and 1D composites, and a `Vector2` takes sticks and 2D composites. Facts from `Strata/src/Strata/Input/InputActionSet.h` and `Strata/src/Strata/Input/InputActionSet.cpp`; [Input actions](../input/actions.md) explains how a frame evaluates them.

| Shape | Meaning | Example |
| --- | --- | --- |
| `Key/<key>` | One key | `Key/Space` |
| `Mouse/<button>` | One mouse button | `Mouse/Left` |
| `Gamepad/<button>` | One gamepad button, on any gamepad | `Gamepad/A` |
| `Gamepad/<axis>` | A whole axis, from -1 to 1 | `Gamepad/LeftX` |
| `Gamepad/<axis>+` or `Gamepad/<axis>-` | Half an axis, which acts as a button; triggers have only `+` | `Gamepad/LeftY-` |
| `Gamepad/LeftStick` or `Gamepad/RightStick` | Both axes of a stick, +Y up | `Gamepad/RightStick` |
| `1D:<negative>,<positive>` | An axis from two button-like controls | `1D:Key/A,Key/D` |
| `2D:<up>,<down>,<left>,<right>` | A vector from four button-like controls | `2D:Key/W,Key/S,Key/A,Key/D` |

The prefixes and names ignore case when read, and the engine writes them as shown. A binding text is at most 96 bytes, `c_MaxTextBytes`; the longest valid one, a 2D composite of four `Gamepad/RightTrigger+`, takes 90.

### The reserved UI map and its defaults

Every set of actions holds the map `UI`, which the game's menus navigate with (see [Input](../ui/input.md)). Its six actions are Buttons. You can change their bindings, but not their names, kind or map. A project that defines no actions holds exactly this map, which is also the default value of the `Input.Actions` section. Facts from `Strata/src/Strata/Input/InputActionSet.cpp`.

| Action | Default bindings |
| --- | --- |
| `Submit` | `Key/Enter`, `Key/KPEnter`, `Key/Space`, `Gamepad/A` |
| `Cancel` | `Key/Escape`, `Gamepad/B` |
| `Up` | `Key/Up`, `Gamepad/DPadUp`, `Gamepad/LeftY+` |
| `Down` | `Key/Down`, `Gamepad/DPadDown`, `Gamepad/LeftY-` |
| `Left` | `Key/Left`, `Gamepad/DPadLeft`, `Gamepad/LeftX-` |
| `Right` | `Key/Right`, `Gamepad/DPadRight`, `Gamepad/LeftX+` |

### Limits and thresholds

These constants bound an input set and the reading of its values. A worked case: an Axis action bound to `Gamepad/LeftX`, with the default :term[dead zone]{id=dead-zone} 0.15, reads a stick pushed to 0.6 as $(0.6 - 0.15) / (1 - 0.15) \approx 0.53$. The action goes down, because 0.53 is above the press threshold 0.5, and stays down until the value falls to 0.35 or less. A Button on a :term[half axis]{id=half-axis} uses the same two thresholds on the raw value, with no dead zone. This gap is :term[hysteresis]{id=hysteresis}, which stops a value that hovers near one threshold from flickering.

[Gamepads](../input/gamepads.md) teaches dead zones, and [Players' bindings](../input/rebinding.md) teaches the file. Facts from `Strata/src/Strata/Input/`.

| Name | Value | Meaning |
| --- | --- | --- |
| `c_MaxKeyCode` | 512 | Key codes are below it |
| `c_MaxMouseButtons` | 8 | Mouse buttons |
| `c_MaxGamepads` | 4 | Gamepads the engine reads |
| `c_MaxTypedTextBytes` | 1,024 | :term[UTF-8]{id=utf-8} text taken from one frame; the rest of that frame's text is dropped |
| `c_MaxMaps` | 32 | Maps in a set |
| `c_MaxActions` | 256 | Actions in the whole set, the six of the `UI` map included |
| `c_MaxBindings` | 8 | Bindings of one action |
| `c_MaxNameLength` | 64 | Characters of a map or action name: basic Latin letters, digits, spaces, `_`, `-` and `.` |
| `c_DefaultDeadZone` | 0.15 | The dead zone of an Axis or Vector2 action that sets none; Buttons use none |
| `c_MaxDeadZone` | 0.9 | The largest dead zone |
| `c_Press` | 0.5 | A value above this holds a half axis, or an Axis or Vector2 action, down |
| `c_Release` | 0.35 | A held one releases at this value or below |
| `c_MaxFileBytes` | 64 KiB | The largest players' bindings file |
| `c_FormatVersion` | 1 | The version of that file, `InputBindings.json` |

The dead zone of a Vector2 is radial: a vector shorter than the zone reads 0, and a longer one keeps its direction with its length stretched from the zone to 1.

## Where it lives in Strata

- `Strata/src/Strata/Audio/`: the audio engine, clips, sources and the scene system; `AudioSystem.h` holds the limits, `AudioEngine.h` the statistics and `AudioClipAsset.cpp` the cooked form.
- `Strata/src/Strata/Asset/AssetImporters.cpp`: the audio importer, its formats, load modes and version.
- `Strata/src/Strata/Input/`: `InputNames.cpp` holds the names, `KeyCodes.h`, `MouseCodes.h` and `GamepadCodes.h` the codes, `InputActionSet.h` and `InputActionSet.cpp` the grammar, limits and reserved map, and `InputActions.h` the thresholds.
- `Strata/src/Strata/Scene/SceneServices.h`: `IAudioPlayback` and `IAudioOutput`.
- `StrataEditor/src/Editor/Commands/AudioCommands.cpp` and `StrataEditor/src/Editor/EditorInputActionsCommands.cpp`: the commands that report and edit these facts.

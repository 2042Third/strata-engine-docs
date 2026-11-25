# Brief: `reference/audio-input`

| Field | Value |
| --- | --- |
| Title | Audio and input reference |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `input/actions` |
| From | audio-input ch. 14 |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/audio-input` — Audio and input reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
`AudioSource` and `AudioListener`, of `Input.Actions`, of the `audio.state`, `input.*` and `inputActions.*` commands
and of the SDK's `AudioSource`, `Audio`, `Input` and `KeyRepeat` stand in `reference/components`, `reference/settings`,
`reference/commands` and `reference/script-api`, linked by name. What only this page holds. Audio: (1) the source
formats the audio importer reads (`.wav`, `.mp3`, `.flac`, `.ogg`), its load modes and the size above which a clip
starts streamed, and the cooked form "STAU" v1; (2) the attenuation models of `AudioSource` (the component always
uses Inverse); (3) the limits, parsed: `c_MaxOneShots`, `c_MaxDopplerSpeed`, `c_MaxOneShotClipWait`; (4) `AudioStats`.
Input: (5) the names of keys, mouse buttons, gamepad buttons and axes as bindings and commands spell them, generated
from `InputNames` with their codes (`KeyCode` by position on a US keyboard); (6) the binding grammar (`Key/<k>`,
`Mouse/<b>`, `Gamepad/<button>`, half axes, `1D:` and `2D:` composites, at most 96 bytes), as a hand-checked table
with one example each; (7) the reserved `UI` map and its default bindings, generated from `InputActionSet.cpp`; (8) the
limits and thresholds, parsed: `c_MaxKeyCode`, `c_MaxMouseButtons`, `c_MaxGamepads`, `c_MaxTypedTextBytes`,
`c_MaxMaps`, `c_MaxActions`, `c_MaxBindings`, `c_MaxDeadZone`, the press and release thresholds, the players'
bindings file's size cap and version. Hand-written: one introduction per table and `## Where it lives in Strata`
(`Strata/src/Strata/Audio/`, `Strata/src/Strata/Input/`, `AssetImporters.cpp`). The tools are
`tools/reference.py parse` and the catalogue dumps.

**Leaves out.**

- The audio engine, clips, voices and spatial sound, as mechanisms → `audio/engine`, `audio/clips-voices-sources`,
  `audio/spatial`
- Devices, per-frame state and gamepads → `input/devices-state`, `input/gamepads`
- Input actions, how bindings are evaluated, and players' bindings → `input/actions`, `input/rebinding`
- Sound and input for game makers → `make/sound`, `make/input`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the names of some 120
keys, 8 mouse buttons, 15 gamepad buttons and 6 axes, the reserved UI map, the limits and `AudioStats`, roughly 2,000
words. The prose is the paragraph on top, eight introductions, the binding grammar table (about 10 rows) and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:37` | feature | link | `AudioStats` |
| `audio-input:50` | feature | link | The cooked clip "STAU" v1 |
| `audio-input:52` | feature | link | The audio importer's formats, load modes and version |
| `audio-input:62` | feature | link | The attenuation models |
| `audio-input:73` | feature | link | The audio components, as names linking `reference/components` |
| `audio-input:94-96` | feature | link | The audio SDK and host functions, as names linking `reference/script-api` |
| `audio-input:98` | feature | link | `audio.state`, as a name linking `reference/commands` |
| `audio-input:107-110` | feature | link | Key, mouse and gamepad codes and their names |
| `audio-input:148-153` | feature | link | The action model, the binding grammar, kind fitting, names, the reserved UI map and the section |
| `audio-input:156-157` | feature | link | The thresholds with hysteresis and the radial dead zone |
| `audio-input:162` | feature | link | The players' bindings file |
| `audio-input:173-176` | feature | link | The input SDK and host functions, as names linking `reference/script-api` |
| `audio-input:179-180` | feature | link | The `input.*` and `inputActions.*` commands, as names linking `reference/commands` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clips, voices and sources | `audio/clips-voices-sources` | helps |
| Sound in space: attenuation | `audio/spatial` | helps |
| Input actions, maps and bindings | `input/actions` | must |
| Gamepads, sticks and dead zones | `input/gamepads` | helps |

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
| critic-reference-20 | could | duplicate | `reference/settings`; `reference/audio-input`, table (7) | The default value of the `Input.Actions` section is exactly the reserved `UI` map, so the two pages generate the same map with its default bindings twice. R44 (the row of reference-q4) keeps each generated fact in one table. | `reference/settings` shows the section's schema and, for its default, links `reference/audio-input`'s table (7), as it already does for the quality presets. No words added. | `allocation/reference.md:260-262`, `:264-265`, `:686`; `critique/rulings-10.md:15`; `Strata/src/Strata/Input/InputActionSet.cpp:503-507`, `:633` |
| critic-reference-21 | could | missing-item | `reference/audio-input` | The audio properties have no descriptions at the pin, so the generated component rows give only ranges, and no reference page gives their units, while `reference/physics` has a units table: `Volume` is a linear gain from 0 to 4 (1 plays the clip as recorded), `Pitch` a rate factor from 0.01 to 8, `MinDistance` and `MaxDistance` metres, `Rolloff` a factor of the Inverse model. | `reference/audio-input` adds a hand-checked units table for `AudioSource`, checked against `AudioComponents.cpp` and `AudioVoice.cpp`, naming `audio/clips-voices-sources` and `audio/spatial`. About 60 words. | `allocation/reference.md:679-691`, `:558-560`; `Strata/src/Strata/Audio/AudioComponents.cpp:16-23`; `Strata/src/Strata/Audio/AudioComponents.h:12-21`; `Strata/src/Strata/Audio/AudioVoice.cpp:304-316` |

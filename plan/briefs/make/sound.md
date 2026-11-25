# Brief: `make/sound`

| Field | Value |
| --- | --- |
| Title | Sound |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/physics` |
| From | gamedev "Sound" (§1.13, concept 19); audio-input "Making your game sound good"; scripting "The gameplay API, part 2": `AudioSource`, `Audio`; use home of residency for sounds ("request in `OnCreate`"); Coin Run's coin sound |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/sound` — Sound

**Covers.** The page gives Coin Run its coin sound and teaches sound at the maker's level. The ideas from zero, in
short paragraphs: a sound file becomes a clip; an Audio Source plays a clip from an entity, with a volume, a pitch, a
loop and a 3D switch; a listener is the ears (Basic 3D's Main Camera has one); a 3D source gets quieter with distance
and moves from ear to ear; a one-shot is a sound fired once and forgotten. The steps. (1) Import
`Samples/ThirdPerson/Assets/Sounds/Coin.ogg` (Kenney, CC0) and play it in the Asset tab's waveform preview. (2) A first
sound: **+ ▸ Audio Source**, its clip, **Play On Start**, then Volume, Pitch and Loop; it plays only in Play mode;
changing a source's **Clip**, in the Inspector or from a script, stops it and drops a Play that had not started yet,
and Play then starts the new clip. (3)
Hear space: the source made spatial and moved while the game plays; Min and Max distance and the rolloff; the listener
moved from the camera to the ball. (4) The coin's sound: the `Coin` script asks for the clip with `Assets::RequestLoad`
in `OnCreate` and plays it with `Audio::PlayOneShotAt` where the coin is collected; the rule in a `:::rule` aside:
request a clip before it is needed, because a one-shot whose clip is not loaded within 0.25 s is dropped with a warning
in the Console, shown by a step that skips the request. (5) Impact sounds: the ball's `OnCollisionEnter` plays a bump
(`Samples/PhysicsPlayground/Assets/Sounds/Impacts/Soft.ogg`, credited in that sample) louder for a harder hit, the
speed taken from the two bodies' velocities along the contact's normal as the Physics Playground's `Impact.cpp` does,
given as a recipe. (6) Music and a volume option: a looping music source, not spatial, its clip **Streamed** (decoded
while it plays) against **Decompressed**; `Audio::SetMasterVolume` from two keys, and the editor restoring its volume at
Stop; the music file comes from the book's tutorial assets with its credit. A Streamed clip holds its encoded bytes in
memory and decodes them while it plays: nothing streams from the disk or a pack (`new:37`). (7) Save. What Strata does
not do here, each in a sentence or two: buses, effects, reverb and HRTF (`new:7`); music systems and ducking
(`new:8`); stay events and a contact's impulse, which is why step 5 reads the velocities (`new:34`); occlusion and
reverb zones (`new:35`); virtual voices and voice priorities (`new:36`); streaming from disk or packs (`new:37`);
listeners per world (`new:38`). At the end the reader can place sounds in space, fire one-shots that never drop, scale
them by impact and set the game's volume.

**Leaves out.**

- Sound inside a computer: samples, channels, decibels, the pull model → `audio/sound-in-a-computer`
- Clips, voices, sources and load modes inside → `audio/clips-voices-sources`
- Panning, attenuation and Doppler inside → `audio/spatial`
- The audio engine and the scene system → `audio/engine`, `audio/scene-system`
- Residency and pins inside → `assets/residency`
- A volume slider in a settings screen → `make/menus`
- Footsteps from animation events → `make/animation`
- A budget of voices for many impacts → `make/recipes`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,700 words against M (3,000). Seven steps take most of it, with the sound ideas from zero in
short paragraphs, two code excerpts (the coin's one-shot, the impact), the rule, the seven absences, three pictures and
the exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:178` | feature | home | `AudioSource` and `AudioListener`; the scripts' `AudioSource` and `Audio`; early requests; the waveform preview; `audio.state` in a command tab |
| `gamedev:337` | concept | home | Audio for makers: sources, the listener, 3D attenuation, one-shots, loading before use; the dropped one-shot |
| `gamedev:636` | term | home | Audio source, listener, one-shot |
| `audio-input:552` | hands-on | home | Steps 1 and 2: a first sound |
| `audio-input:554` | hands-on | home | Step 3: hearing space |
| `audio-input:556` | hands-on | home | Step 5: impact sounds |
| `audio-input:561` | hands-on | home | Step 6: music and a volume option |
| `physics:454` | hands-on | home | Step 5's loudness from the hit, as `Impact.cpp` computes it |
| `new:7` | not-done | home | Buses, effects, reverb and HRTF: a voice sets only its own output volume. Evidence: `git grep -niE "ma_sound_group\|reverb\|hrtf\|filter_node" 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin); `Strata/src/Strata/Audio/AudioVoice.cpp:308` |
| `new:8` | not-done | home | Music systems and ducking. Evidence: `git grep -niE "music\|duck" 822a7a46 -- Strata/src/Strata/Audio` finds only comments that name music as a use of streamed or 2D clips (`AudioClip.h:19`, `AudioEngine.h:85`, `AudioSource.h:33`; run at the pin) |
| `new:34` | not-done | home | Stay events, and the impulse or impact speed of a contact: contacts begin and end, and the impact sound of step 5 reads the bodies' velocities. Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188`; `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `new:35` | not-done | home | Occlusion and reverb zones. Evidence: `git grep -ni -e occlu -e reverb -e zone 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin) |
| `new:36` | not-done | home | Virtual voices and voice priorities. Evidence: `git grep -ni -e virtual -e priorit 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin) |
| `new:37` | not-done | home | Streaming from disk or packs: a Streamed clip holds its encoded bytes in memory and decodes them while it plays. Evidence: `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1712` (read at the pin) |
| `new:38` | not-done | home | Listeners per world: the audio engine has one listener. Evidence: `Docs/Roadmap.md:1707`; `Strata/src/Strata/Audio/AudioSystem.h:84-86` (read at the pin) |
| `audio-input:30` | feature | use | The master volume |
| `audio-input:33` | feature | use | The listener |
| `audio-input:46` | feature | use | Load modes: Decompressed and Streamed |
| `audio-input:76` | feature | use | Clips that load in the background |
| `audio-input:77` | feature | use | Step 2: plain writes apply, and a changed clip stops the source and drops its pending Play; Play starts the new clip. Evidence: `Strata/src/Strata/Audio/AudioSystem.cpp:538-546` (`ResolveClip`); `Strata/src/Strata/Audio/AudioSystem.h:75-77` (read at the pin) |
| `audio-input:80` | feature | use | Which listener is used |
| `audio-input:84` | feature | use | One-shots in a scene |
| `audio-input:94` | feature | use | The SDK's `AudioSource` |
| `audio-input:261` | concept | use | 3D sound, at the maker's level |
| `audio-input:469` | figure | use | The Inspector of an Audio Source |
| `audio-input:471` | figure | use | The Asset tab's audio preview |
| `audio-input:481` | figure | use | The Console's warning of a dropped one-shot |
| `audio-input:505` | rule | use | Request clips before you need them |
| `scripting:127` | feature | use | The SDK's `AudioSource` and `Audio` |
| `scripting:481` | rule | use | Request assets early |
| `assets:624` | hands-on | use | Keep a sound loaded, as an exercise |
| `physics:107` | feature | use | `OnCollisionEnter` for the impact |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Collisions, triggers and the coin's `OnTriggerEnter` | `make/physics` | must |
| Requesting assets early; `Assets::RequestLoad` | `make/scripting-scene` | must |
| Importing a file and the Asset tab | `make/assets` | must |
| A sum of products along a direction, given as a recipe | `basics/math-vectors` | helps |

**Starting state.** The end state of `make/physics` (`startsFrom {"tutorial": "make/physics"}`): the rolling ball and
the trigger coins. The sounds come from the release's `Samples/ThirdPerson/Assets/Sounds/` and
`Samples/PhysicsPlayground/Assets/Sounds/Impacts/`, the music from `tutorials/assets/` with its credit. The page ends
with the coin sound, the bump and the music.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `audio-source` | Audio source | - |
| `listener-make` | listener (make) | - |
| `one-shot` | One-shot (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-10 | should | stale-item | `make/sound` (steps 2, 3 and 6) | A new Audio Source plays on start and is spatial by default (Min Distance 1 m, Max Distance 50 m, Rolloff 1). Step 2 has the reader tick **Play On Start** and step 3 "makes the source spatial", but the first sound is already heard from where the source stands, and step 6's music must have **Spatial** cleared. | Step 2 states the defaults; step 3 moves the source and the listener instead of switching Spatial on; step 6 clears **Spatial** for the music (about 50 words). | `allocation/make-a.md:1414-1418`, `:1424`; `Strata/src/Strata/Audio/AudioComponents.h:11-22` |
| critic-make-a-22 | could | missing-item | `make/scripting-scene` (step 3) | The page types `"Prefabs/Coin.stprefab"` for `Assets::Find` but never says how a reader gets such a path. The Content Browser's right-click **Copy Path** copies exactly the path the call takes: relative to the Assets folder, with `/`. | Step 3 adds one sentence with **Copy Path** and the path's form; `make/sound` step 4 uses it for the clip (about 40 words). | `allocation/make-a.md:1053-1054`; `StrataEditor/src/Panels/ContentBrowserPanel.cpp:1136-1137`; `StrataEditor/src/Editor/AssetBrowserView.h:30`; `StrataScriptCore/Include/StrataScript/Scene.h:18-19` |
| critic-make-a-28 | could | thin-home | `make/export` (step 8), `make/project-coin-run` (step 7) | Step 8 names two assets that scripts load by path, the coin prefab and the coin sound. The bump of `make/sound` step 5, when its script finds the clip by path, and the complete sound of `make/project-coin-run` step 2 drop out of a pruned export the same way, and no page says how the reader finds what is missing: `Game.log` holds a warning "FindAsset (called by script ...): there is no asset at '<path>'" for each. | Step 8 lists every path that Coin Run's scripts find (or adds the folder `Sounds`, since Always Include takes folders) and reads that warning in its "If you do not see it"; `make/project-coin-run` step 7 adds `Complete.ogg` (about 50 words). | `allocation/make-a.md:1421-1423`, `:1707-1709`, `:1808-1809`, `:1815-1816`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:912-914`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:1546`, `:1555`; `StrataEditor/src/UI/SettingsPages.cpp:348-349` |

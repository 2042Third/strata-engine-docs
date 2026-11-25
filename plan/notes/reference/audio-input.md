# Notes: reference/audio-input

## New terms

None.

## Requests

None.

## Hand-written tables

The folder src/generated/reference/ holds no audio or input table, so every table of the page is written by hand from the pin (commit 822a7a46):
- Source formats, cooked clip: Strata/src/Strata/Asset/AssetImporters.cpp, Strata/src/Strata/Audio/AudioClipAsset.cpp, AudioClip.h.
- Attenuation models, units: Strata/src/Strata/Audio/AudioSource.h, AudioComponents.cpp, AudioComponents.h.
- Audio limits, AudioStats: Strata/src/Strata/Audio/AudioSystem.h, AudioEngine.h.
- Audio services: Strata/src/Strata/Scene/SceneServices.h.
- Key, mouse, gamepad names and codes: Strata/src/Strata/Input/InputNames.cpp, KeyCodes.h, MouseCodes.h, GamepadCodes.h (keys grouped in ranges).
- Binding grammar, reserved UI map, input limits and thresholds: Strata/src/Strata/Input/InputActionSet.h, InputActionSet.cpp, InputActions.h.

## Not verified

- Link targets audio/clips-voices-sources, audio/scene-system, reference/settings, reference/commands, reference/script-api (pages not yet written when checked).
- The Volume range 0 to 4 is the editor slider's; whether code clamps it there was not checked.
- Size: the lint reports 1,788 prose words against M; known fault for reference pages, not padded.

## Findings not applied

- critic-reference-2: applied (each introduction names a teaching page).
- critic-reference-12: applied for IAudioPlayback and IAudioOutput (IUIControl, IWorldStreaming belong to other pages).
- critic-reference-20: applied by the Reserved UI map table being the single copy; reference/settings must link it.
- critic-reference-21: applied (units table).

## Clerk

- Fixed: `d_\min` is written `d_{\min}` (KaTeX refused it).

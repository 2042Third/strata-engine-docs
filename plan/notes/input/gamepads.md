# Notes: `input/gamepads`

## New terms

None proposed. The page defines the five glossary terms it homes (gamepad mapping, half axis, rescaling, dead zone, hysteresis) in bold.

## Requests

- Words for `tools/data/extra-words.txt`: `axial` and `radial` (the page uses them for the two shapes of a dead zone, as the glossary entry "Dead zone, axial and radial" does; the `word-list` findings for them are left). Also `rescales`, `rescaled` are avoided in the text.
- Alias request: the glossary entry `dead-zone` could carry the aliases `axial dead zone` and `radial dead zone`, so the words count as glossary words.
- The page links `www.glfw.org`, `github.com` and `learn.microsoft.com`; all three are on `tools/external-hosts.txt`.
- The page links `actions.md` and `devices-state.md` of `input/` and `../worlds/streamer.md`; those pages are written by others.
- Figures: the brief asked for plots of the axial square and the radial circle. The page has a Mermaid line chart of one axis with a dead zone and a table for the hysteresis trace; a two-dimensional plot of the two dead zone shapes is not drawn (no figures file).

## Since

`since: 0.3.0`: `Strata/src/Strata/Input/GamepadCodes.h` first appears in commit `a0f2865f` (2026-10-08, "Add build system, pinned dependencies and engine core"), contained in the tag `v0.3.0`.

## Not verified

- The Mermaid `xychart-beta` chart renders with the site's Mermaid version (the site build is not run here).
- The alternatives table: what the gamepad interface of SDL, XInput and GameInput offer or lack (rumble, hot-plug events, hints that add mappings, a fixed layout) is from general knowledge, not from the pin; the Further reading entry for XInput names its dead zone constants and four-controller limit, which were not fetched.
- That GLFW gives each controller the first free joystick slot (the page says only that an unmapped model keeps its slot, from the brief's evidence).
- The release note "Gamepads are still read while an exported game is in the background" is quoted from `Docs/Releases/0.7.0.md`; the page adds only that `PollGamepads` never tests the window's focus. Whether other code stops reading while the window is unfocused was not examined.
- That `Input::GetGamepadAxis` returns rest while input is disabled was seen in `Input.cpp` but is not on the page.
- How the Third-Person player script reads the `Move` action was not examined; the page states only the action's binding and dead zone, from `Samples/ThirdPerson/ThirdPerson.stproj`.

## Findings not applied

The brief lists no open findings. Left out by size: the per-pad code of the actions (it lives in `input/actions`), the whole-axis tie rule (the lower pad wins; `Core.InputActions` tests it), and the exercise on a breakpoint with a pad connected is a search-based trace.

## Clerk

- Added the aliases axial dead zone and radial dead zone to dead zone, homed here (the glossary's definition kept).
- Admitted to extra-words.txt: axial, radial.

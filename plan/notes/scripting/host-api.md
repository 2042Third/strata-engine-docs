# Notes: scripting/host-api

## New terms

None proposed.

## Requests

- None. No figures file: both pictures are Mermaid diagrams.

## Since

- 0.3.0: `Docs/Releases/0.3.0.md` says the SDK covers entities, components, transforms, prefabs, input, time, rigid bodies, raycasts, audio and animators, and the Roadmap's wave 3 entry counts 119 host functions.

## Not verified

- The table merges the inventory's 28 rows of groups into 27 (input actions and binding capture share a row), as the brief says 27.
- The wave of each group comes from the inventory and the Roadmap; physics, queries, audio and game flow are placed "before wave 3" from the 0.3.0 notes and the order of the table, as no earlier wave names them.
- Services of the groups Scene streaming, Game flow and Interpolation are named by what their host functions call (the scene), not traced in full.
- That `StructSize` lets the SDK know how much of the table exists is taken from the SDK's use of `ST_SCRIPT_DETAIL_HOST_WITH`, not read in `Host.h`.

## Findings not applied

- `audio-input:365` (the text buffer protocol and action names as strings): shown only through the property buffer's second read; the audio and input sides stay with their pages.
- The reasons for isolating scripts in "The problem" are general engineering reasons, not quoted from the engine's documents.
- Erratum `new:18` and open item `scripting:687` are applied.

## Clerk

- Nothing asked.

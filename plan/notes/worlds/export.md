# Notes: worlds/export

## New terms

None.

## Requests

- No figures file: the only picture is a Mermaid diagram.

## Since

0.3.0: `Docs/Releases/0.3.0.md` lists "File > Export Game..." writing the game into a folder in the background.

## Not verified

- The Export dialog, the identity and icon pages and the installed layout are named in prose without links: their pages do not exist yet (editor/commands, worlds/game-identity, editor-ui/launcher-dialogs, engineering/releasing).
- The description of `project.exportStatus` in the pin's command text omits `CookingWorlds` from its list of states; the code returns it. The page follows the code.
- No bug history was verified, so there is no "What went wrong before" section.

## Findings not applied

- Brief item `worlds-runtime:163-165` (icon, version resources, desktop entry): only mentioned, as the brief says (home worlds/game-identity).
- `Export.AlwaysInclude` as a dotted name: the pin's names check rejects it, so the page writes `AlwaysInclude`.
- Vertical sync: it is the manifest's `VSync` default (true), not a field of `GameExportOptions`; the page says so.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

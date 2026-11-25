# Notes: reference/game-makers

## New terms

None.

## Requests

None.

## Hand-written tables

The selection file `tools/data/game-makers.json` does not exist at this commit, so every table except the runtime options (included from `options-runtime.md`) is hand-written. Check again when the pin moves.

- Panels: `StrataEditor/src/EditorLayer.cpp` (`RegisterBuiltinPanels`).
- Shortcuts: `EditorLayer.cpp` (global shortcuts, menu items), `Panels/ViewportPanel.cpp` (Q, W, E, R, F, Home, F8), `UI/EditorActions.cpp`.
- Chips: `Panels/ViewportPanel.cpp` (`DrawChips`).
- Components: `src/generated/reference/components.md` (names, defaults).
- Callbacks, SDK calls: `StrataScriptCore/Include/StrataScript/Script.h`, `src/generated/reference/script-api.md`; callback order from `Strata/src/Strata/Scene/Scene.cpp` (`OnUpdateRuntime`).
- Conventions: `Entity.h` (`GetForward`, `SetEulerAngles`), `.claude/skills/strata-make-a-game/SKILL.md` (glTF faces +Z; Euler degrees in commands).
- Commands: `src/generated/reference/commands-*.md`, `options-editor.md`, `options-cli.md`.
- Project folder: `Project.cpp` (`Create`), `Project.h`, `EditorContext.cpp` (Trash, Thumbnails, Saves), `ScriptProject.cpp`.
- Templates and samples: `ProjectTemplates.cpp`, `Samples/Samples.json`.

## Not verified

- Inspector shows rotation as Euler degrees: seen in `PropertyWidgets.cpp` (`QuatToEulerDegrees`); the order pitch, yaw, roll is from the skill text.
- `StrataEditor --commands` exits with code 1 when a step fails: from the engine's inventory, not read in `EditorCommandRunner`.
- Panels open from the **View** menu: from the inventory.
- Sample `.meta` files are kept in version control: from the engine's guide, not the code.

## Findings not applied

- critic-reference-7 (files outside the project's assets): targets `reference/editor`; this page lists only the `.strata` entries it needs.
- critic-reference-13: no generated panel, shortcut or convention tables exist, so those sections are hand-written (listed above).
- critic-reference-14 (Assumes rows): Assumes rows live in the brief, not in the page.
- critic-reference-22: applied as a hand-written table of templates and samples (no `templates.json`/`samples.json` table exists).

## Clerk

- Nothing asked; nothing admitted.

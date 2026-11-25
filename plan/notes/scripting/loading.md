# Notes: scripting/loading

## New terms

None. The page defines the four glossary terms of its brief in bold: private copy, abandoned library/file, call site, active engine.

## Requests

- Figure `script-status-loader` (`src/content/figures/scripting/loading.json`): a text capture of `script.status` for the Tetris sample after `script.build`; not taken yet. It shows a null fault, because a healthy module has none; the brief asked for a capture with a fault.
- Two Mermaid diagrams (ownership, load sequence) are inline; no pictures.

## Since

`since: 0.3.0`: the script module and its loader exist since the first tag (plan/inventory/gamedev.md, the row "Script module", 0.3.0).

## Not verified

- What the platform loaders do on Linux and macOS (RUNPATH, `$ORIGIN`, truncated files): taken from the comments of `Strata/src/Strata/Core/DynamicLibrary.h`, not run there.
- Windows locks a loaded library's file: taken from the comment in `ScriptEngine::SetHotReloadEnabled` and `ScriptModule::Load`.
- The name a module reports in its description (the page says only that it may replace the file's name); the SDK's source of `state->Name` was not followed.
- The reason given for refusing the current folder in the Windows search (a user can plant a file there) is general knowledge, not a statement of the code.

## Findings not applied

- The brief's `script.status` capture with a fault: the page shows the healthy answer (fault null) and describes the fault member in prose.
- The brief's exercise on `ST_SCRIPT_ABI_VERSION 2` is an exercise that reads the refusal message; it does not ask the reader to build a module.

## Figures

- `script-status-loader` (text), round 1: published. Tetris sample after `script.build`: loaded true, moduleName TetrisScripts, loadCount 1, hotReload true, one class TetrisBoard (29 fields, callbacks OnCreate, OnUpdate, OnReload), fault null. Caption and alt rewritten to name these values; the page's paragraph stays true of the capture.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

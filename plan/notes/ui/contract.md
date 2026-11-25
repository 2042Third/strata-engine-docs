# Notes: ui/contract

## New terms

None proposed. The three terms the glossary homes here (UI contract, layout (cached), validation) are defined in bold.

## Since

0.3.0: the game UI module and its change tracking exist from the first tag of the book's range (GameUIScene signals, journals and Validate at the pin); not checked against older tags.

## Requests

- Figure not drawn: the Performance panel with the Render.UI and GPU.UI stages on a scene of many elements, idle and after one change (item gameui:505). The pin's recipe needs a project with 10,000 UI elements that I could not verify.

## Not verified

- That the script API's text setter reaches `GameUISystem::SetText` (only `StrataScriptCore/Include/StrataScript/UI.h:54` was named by the brief, not read).
- That the editor's property edits go through `ComponentAccess::SetProperty` (the brief names `PropertyEdit.cpp`, not read).
- The scale mode that follows the screen keeps the aspect-based unit size when reference and screen share an aspect (read only from `GetLayout`, `ComputeScale` not read).
- That one quad per character of "Changed!" explains the 8 quads (the test only counts 8).

## Findings not applied

- Figure gameui:505 (Performance panel): see Requests.
- Hit grids rebuilt from the hit stamp are only mentioned, with a link to ui/input; the page names the stamp bump.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

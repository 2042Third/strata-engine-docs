# Notes: editor-ui/imgui

## New terms

None proposed.

## Requests

- Names for tools/data/names.txt: Nuklear, microui, egui (immediate-mode libraries in the approaches table; word-list failures left).
- Hosts: github.com is on the list (Nuklear, microui, egui, Dear ImGui entries cite their repositories without links).
- No figures: the one picture is a Mermaid diagram. No layouts needed.

## Not verified

- The names `ImGui::IsItemFocused` (names finding: declared in Strata/vendor/imgui/imgui.h:1050, the dump lacks it).
- Statements about Nuklear, microui and egui (language, size) come from general knowledge; not checkable at the pin.
- The exact hash values in the sketch follow ImHashStr and the CRC-32C table read in Strata/vendor/imgui/imgui.cpp; no ImGui program was run to compare.
- The symptom of ten buttons with one ID (Exercise 2) is stated only as far as the code shows: the conflict highlight (ConfigDebugHighlightIdConflicts, default true); which row reacts to a click was not run.
- That OpenPopup inside BeginMenu hashes in the menu window's scope is derived from reading, not run.
- Why Strata does not enable multi-viewports and why it disables obsolete functions is not documented at the pin; the page states only the facts.

## Since

0.3.0: the ImGui layer and editor panels exist since the first editor.

## Findings not applied

- The brief states the panel name as `<icon> <title>###<id>`; the code (EditorPanelRegistry.cpp:53) puts two spaces after the icon; the page says so.
- Exercises: the brief's patches are three independent patches against the pin (exercise-3 replaces exercise-1's layer); the menu item label is "Reset counter", not "Reset...".

## Clerk

- Admitted to names.txt: Nuklear, microui, egui.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Names of this page

- `ImGui::IsItemFocused`: a Dear ImGui function (Strata/vendor/imgui/imgui.h at the pin's submodule); names.py searches the engine's own files, not its submodules, and the engine never calls it.

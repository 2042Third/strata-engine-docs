# Part review: `core/map`

- contradiction: "Each opens, accepts registrations and then closes", of the component, loader, scene-system and settings registries: only the component and settings registries freeze, and the loader and scene-system registries stay open (`core/layers-registries`); the sentence now says so.
- contradiction: "Strata's tables stay fixed for the whole run": true of the frozen component and settings tables only; the sentence now names them.
- wrong: Exercise 2's worked solution counted 16 editor options and 11 of its own; the pin's `c_Arguments` in `StrataEditor/src/EditorApplication.cpp` holds 17 (with `--window-size`), 12 of them the editor's alone.

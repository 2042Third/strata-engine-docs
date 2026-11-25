# Part review of `reference/editor`

- contradiction: the user data folder's `<Name>/Saves/` row listed only `GraphicsOptions.json` beside the save files, while `reference/worlds-runtime` (and this page's `.strata/Saves/` row) put both players' files there; `InputActions` writes `InputBindings.json` to the `IGameSaves` folder at the pin (`Strata/src/Strata/Input/InputActions.h`), so the row now names both files.
- checked without change: the panel registrations, icons and default-open flags of `EditorLayer::RegisterBuiltinPanels`, the default layout's shares, `--windowed` 1600 by 900 and the 640 by 360 minimum of `--window-size`, exit codes 3 and 130, and the trash's 30 days.

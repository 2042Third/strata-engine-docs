# Part review: ui/layout (group 1 of 1)

- wrong: "a slider 400 units wide" in the settings panel: the slider's size field is 400, but its group `Rows` (vertical, padding 8, stretch on, `MainMenu.stscene`) stretches it to 384; the fill at 0.25 is 96 wide and the handle covers 87 to 105, not 100 and 91 to 109.

Checked and held at the pin: the Menu, Buttons, Settings and button rects of `MainMenu.stscene` and every box computed from them, `ComputeScale`, `c_MaxLayoutsPerCanvas` 4, `GetGridColumns` (floor of (w + s) / (c + s), at least 1), the Debug `Validate` at the end of `EnsureLayout`, the Tetris HUD test's name, every quote's callout lines.

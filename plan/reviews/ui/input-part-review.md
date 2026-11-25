# Part review: ui/input (group 1 of 1)

- wrong: three links named the text page "Text in the UI"; its title is "Text and text fields".
- wrong: the Third-Person credits panel "opens over" the menu; it stands beside it (position 520 in `MainMenu.stscene`, like the settings panel), now "beside".
- gap: the world-space example treated the canvas's matrix as a plain scale; `GameUIScene::GetCanvasWorldMatrix` also flips y and starts at the canvas's pivot point; the example now says so, and the Hard exercise's answer adds where the point lies on a real canvas.

Checked and held at the pin: the nine steps of `GameUISystem::OnUpdate` and the early return without canvases, `c_TargetsPerCell` 2 and `c_MaxCellsPerAxis` 64, `ComputeRaycastTarget` (a selectable always), the UI map's default bindings (`InputActionSet.cpp`), `StepSlider`'s tenth of the range, the fade records of `UpdateVisualStates`, `FadeDuration` 0.1, Cancel only ending editing, the SDK's `UI` functions, the test names quoted, every quote's callout lines.

# Part review: `editor-ui/shell`

- wrong: "the frame rate update comes last": `EditorLayer::OnImGuiRender` ends with `ReadBackScreenshots()` after `UpdateFrameRate()` (`EditorLayer.cpp:1076-1078`); now the frame rate update comes next and the screenshots are the last step (paragraph split for length).
- wrong: `EditorDockspace` "has no saved settings of its own": its flags hold no `ImGuiWindowFlags_NoSavedSettings` (`EditorLayer.cpp:1679-1681`); now "cannot be moved, collapsed or docked into another window; its size follows the editor's window".
- wrong: "The menu item stands at line 1493 of `EditorLayer.cpp`": at the pin **Save Scene** is at line 1778, as the page's own excerpt shows; now 1778.
- wrong: "the viewport keeps 45 % of a 3840 × 2054 window": the test checks `share >= 0.45f` (`EditorUITests.cpp:425`); now "at least 45 %".
- wrong: "`ResetOpenStates` closes every panel that is not open by default" (body and Exercise 1): it sets every panel to `OpenByDefault || FocusRequested` (`EditorPanelRegistry.cpp:114`), so it also reopens default panels the person closed; now "opens every panel that is open by default and closes the rest".

# Part review: `editor-ui/status`

- wrong: the example of an animation without input called the viewport's flash one "that marks a selected entity"; at the pin it outlines what an automation command changed (`ViewportPanel::c_AgentFlashSeconds`): corrected.

Checked at the pin without finding: the pills, their order, texts, colors and click targets (`EditorLayer::DrawStatusBar` and the pill functions), the 85 % pressure, the caption font of 12 pixels, the margin of two font sizes, the `Editor.FrameRate` defaults, choices and floor of 5, `c_AutomationActivitySeconds` 1.0, 60 work-time samples, ImGui's frame rate, the notification model (four, 5/8/12 s, 2 s keep-alive, groups, `Replace`), `NotifyCommandOutcome`, the toast window's flags and area, the 280-byte message, the five buttons and the test suites.

# Part review: `editor-ui/imgui`

- wrong: "the Streaming panel's asset table uses six" flags: the quoted `flags` hold seven (`StreamingPanel.cpp:857-858`, with `Resizable` and `NoSavedSettings`); now "seven", and the callout names resizing and the unsaved settings.
- wrong: the ID sketch skipped the three marks of `###`, but `ImHashStr` resets to the seed and then folds the marks in (`Strata/vendor/imgui/imgui.cpp:2578-2586`); the sketch now hashes them, its output is refilled, and the prose says "only the marks and the text after them" count.
- contradiction: "Strata's theme sets the global style once": `ImGuiLayer::ApplyStyle` runs the callback again at every change of the scale (`ImGuiLayer.cpp:150-230`), as `editor-ui/ui-scale` teaches; now "runs it again whenever the size of the interface changes".
- unclear: "when the :term[ImGui]{id=immediate-mode-gui} layer starts" marked the layer's name as the immediate-mode term; now "when its `ImGuiLayer` starts" (the context is created in `ImGuiLayer::OnAttach`).

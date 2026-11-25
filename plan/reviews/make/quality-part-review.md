# Part review: make/quality

- step: step 8's command tab made the four toggles and set the fields but never put them in one group; it now names `component.set` for each toggle's `Group`.
- unclear: step 8 said "give all four the same `Group` value", but **Group** is an entity reference (UIToggleComponent::Group); it now says to choose the same entity as **Group** in **UI Toggle**, as make/menus does.
- unclear: steps 9 and 11 wrote the reader's toggles as editor labels (**High**, **Low**); they are the names the reader made, `GraphicsHigh` and `GraphicsLow`.

Checked without change: the preset rows (RendererQuality.cpp, Docs/Manual/Graphics.md), TAA's 8 jitter phases, the TAA presets, the `--quality` log line, `Graphics.h`'s functions, `graphics.resetPlayerOptions` as the only `graphics.` command, and the sample's `SettingsMenu.cpp` excerpt.

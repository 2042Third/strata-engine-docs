# Part review: ui/drawing (group 1 of 1)

- contradiction: `since: 0.3.0`, against 0.4.0 on every other page of the part; the module arrived in 0.4.0 (`Docs/Releases/0.4.0.md:52-59`, and 0.3.0's notes name no game UI); the page and its notes' `## Since` now say 0.4.0.
- wrong: links named "Laying out the UI", "Text in the UI" (twice) and "Input on the UI"; the pages are titled "Rects, anchors and layout", "Text and text fields" and "UI input".
- wrong: the canvas mode's screen view was "taught in" `gpu/debug-drawing`; it is `editor-ui/scene-view`'s (the brief's `gameui:159`), now linked there.
- wrong: "a frame with a fading button upload at most 16 quads": the test in `GPUGameUITests.cpp` (lines 308-313) changes one label's color; the sentence and the answer of Check yourself 2 now name that change.
- wrong: the vertex shader's callout "Lines 52–55" ended before the multiplication by the scale and the origin, lines 56–57; now "Lines 52–57".

Checked and held at the pin: `UIQuad` at 64 bytes, `GetTextCapacity` (glyphs plus max(4, a quarter)), the Play button's sliced image (9 quads), `c_MaxQuadChanges` 256, `c_RangeMergeGap` 16, `c_MaxUIFonts` 256, `c_MaxBoundAtlases` 4, the binding set's slots 0 to 8, the order of `Prepare`, the world pipeline's depth state, `GetCanvasWorldMatrix`, the camera-relative transform in double.

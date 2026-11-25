# Part review: make/performance

- contradiction: exercise 1's answer said the engine's test draws 10,000 materials "in one opaque draw call", while the page's body and the test (GPURenderSceneTests.cpp, "Ten thousand cubes with ten thousand unique materials take a few draw calls": Draws <= 4) say at most four; the answer now says at most four.

Checked without change: the Stats chip's lines (ViewportToolbar.cpp), the Performance panel's summary, bound lines, columns and buttons, `editor.perf`'s keys, the debug view labels, the editor's idle rates (30, 10, active unlimited), the perf log's columns, and the 100,000-script budget (1.856 ms).

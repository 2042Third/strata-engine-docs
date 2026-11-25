# Part review: gpu/coordinates (group 1 of 2)

- wrong: "SceneRenderer.cpp builds its pipelines with setFrontCounterClockwise(!key.Mirrored)"; the pin writes setFrontCounterClockwise(key.Mirrored == backFacePass) (SceneRenderer.cpp:2560), so passes that draw back faces also turn the rule; the sentence now quotes the expression and says so.
- wrong: the depth-step sketch's callout "Lines 30–36" covered return 0; the loop is lines 30–35.

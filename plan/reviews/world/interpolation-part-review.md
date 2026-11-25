# Part review: `world/interpolation`

- wrong: "Debug builds run `ValidateInterpolation` with every update": at the pin it runs inside `AssertCachesValid`, called by `CheckCachesAfterUpdate` only when the `AmortizedCheck` is due (`Scene.cpp`); corrected to the paced check, linking the scene graph.

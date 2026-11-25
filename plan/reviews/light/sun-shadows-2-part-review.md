# Part review of `light/sun-shadows-2`

- wrong: "How it is tested" ran the filter's suite with `ctest -R GPU.SceneRenderer.ShadowFilter`, which matches no CTest test at the pin (the GPU suites run in the one test `StrataTests.GPU`, `StrataTests/CoreShards.json`); it now names that command and keeps the test program's `--test-suite` filter for the suite alone.
- wrong: exercise 4's answer put the forward pass's mask read at lines 240 to 241 and the transparent call of `SampleDirectionalShadow` at line 238 of `Strata/shaders/Scene/Forward.frag.slang`; at the pin they are lines 310 to 311 and 308, as the page's own quote shows.

# Part review of `engineering/test-kinds`

- wrong: the flicker cases "Both cases are tests of the suite": the suite's steady-drift case uses other values; now "tests both kinds: a steady drift, and these three values exactly" (`FlickerMetricsTests.cpp:84-115`).
- wrong: Check yourself 3 said the CPU statistics "are not those of the frame the test drew"; on the GPU-driven path they hold only what the CPU drew, and the GPU's counters arrive later (`SceneRendererTestUtils.h:381-416`).
- wrong: Exercise 3 placed `StrataExport.Clean` near line 591 and `StrataEditor.Export` near 598; at the pin they are at 612 and 620 of `StrataTests/CMakeLists.txt`.

# Part review: `worlds/runtime`

- wrong: the callout of `UpdateSceneLoads` said Lines 271–280 for both failures; the log of a failed switch after the start stands on line 281; corrected to 271–281.
- wrong: the callouts of `GameWindowService::ApplyRequests` were one line off: the resized test starts on line 132, the mode is lines 140–144 and the vertical sync lines 145–148 (they said 133–135, 139–143 and 144–148); corrected.

Checked at the pin and found right: `c_Arguments`, `CheckOptions` and `GetProgramRun`, the exit codes (`c_ScriptCrashExitCode` 2), two background threads, 60 frames a second headless, the three kinds of run, `GameRuntime::Create` and its destructor, the trim three frames after a switch (`c_SceneSwitchTrimFrames`), the 4 ms load budget, 8 steps at 60 steps a second, `GraphicsOptions.json` in the save folder, the perf log columns of `FramePerfLog`, `GameRuntime` and `GameRenderer`, the suites `Runtime.Game`, `Runtime.GameGraphics`, `Runtime.FramePerfLog`, `Runtime.PerfLog` and `GPU.Runtime.GameRenderer`, the named `StrataRuntime.*` CTests, the toys' outputs and the hand computations.

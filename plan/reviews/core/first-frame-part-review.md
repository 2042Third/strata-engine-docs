# Part review: `core/first-frame`

- wrong: "A fifth case ends with 0 ... the exit code stays what it was": at the pin `Application::Run` sets `c_UnhandledExceptionExitCode` (1) when an exception leaves the frame loop and the code was still 0, as `core/frame-loop` and `core/conventions` say; the paragraph and the exit code 1's bullet now say so.
- wrong: the scripted options that make `GetProgramRun` answer Console lacked `--window-size`, which the pin's list in `StrataEditor/src/EditorApplication.cpp` holds; added.

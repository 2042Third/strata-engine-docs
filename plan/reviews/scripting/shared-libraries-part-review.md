# Part review of `scripting/shared-libraries`

- wrong: the opening told the reader to press **Build**; the editor has no such label (the menu item and the Problems panel's button are **Build Scripts**, the key **Ctrl+B**); now **Ctrl+B**, as `scripting/why-scripts` says.
- wrong: interposition was said to work "on Linux and macOS" by searching the loaded libraries in order; macOS binds names through two-level namespaces by default, so the sentence now says so for Linux only and names the macOS default.
- contradiction: "Only the logging functions accept a call from any thread", while `scripting/abi-sdk` said only `Log`; `ScriptABI.h` marks its "Diagnostics" block, `Log` and `ReportException`, as callable from any thread: both pages now name the two diagnostic functions.

Checked and holding: `DynamicLibrary.h`'s search rules and `GetNativeHandle` comment, `LoadLibraryExW` with its two flags, `RTLD_NOW | RTLD_LOCAL`, `s_AbortContainment`, `StrataScriptModuleAPI`'s 48 bytes, `StrataScriptGraphicsOptionInfo`'s fill rule, `ST_SCRIPT_ABI_VERSION` 1 and the refusal message naming both versions, the 0.7.0 note (seven appended functions, version kept), the CMake excerpts and their callout lines (visibility at line 101), the sketches' callout lines.

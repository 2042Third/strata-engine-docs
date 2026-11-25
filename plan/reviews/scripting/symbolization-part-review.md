# Part review of `scripting/symbolization`

- unclear: the rule box named the page that shows the guard as the code span `scripting/crash-containment`, which a reader cannot follow; it is now a link to the Crash containment page (`crash-containment.md`).

Checked and holding: `WriteThroughNull`'s write at line 42 and its call at line 65 of `FaultScripts.cpp`, `c_MaxCrashStackFrames` 32, the 512 MiB limit of `FindElfFunction`, `Describe` and `Resolve` on Linux and macOS (no function from `dladdr` on Linux, the symbol table read by `Resolve`; macOS fills it in `Describe`), the header comment the caution corrects, `IsRuntimeFrame` and `ChooseFaultLocation`, the Problems panel's "(inlined)" rows and the skipped `Strata::Detail::` frames, the two test cases of `Scripting.Faults`, every callout line against the pin; no contradiction with the digest.

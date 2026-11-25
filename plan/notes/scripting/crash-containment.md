# Notes: scripting/crash-containment

## New terms

None proposed. The page bolds only the glossary terms it homes.

## Requests

- Words for `tools/data/extra-words.txt` or `names.txt`: Lua, WebAssembly, POSIX, abort (as a plain word; also `abort()` as code everywhere).
- Picture, not taken: the toast with the **Show Problems** button after a script crash (editor figure, project `ThirdPerson` copy with a null write in `Coin.OnUpdate`). The page shows the Console line as a text form with placeholders instead.
- The glossary term "`sigsetjmp`/`siglongjmp`" has no `names` entry, so `lint` cannot see its bold definition (`defined_as_code` needs a name that is one code span). The page defines it as **`sigsetjmp`/`siglongjmp`**; `term-defined` stays failing until the entry gets names.

## Not verified

- The exact look of the toast and the Console on screen (read from `EditorContext::StopOnScriptFault`, not run).
- macOS behaviour (recovery stack, `SIGBUS`): read from comments and code in `PosixCrashGuard.cpp`, not run.
- The watchdog numbers 62 ms and 310 ms are computed from the code's integer arithmetic (and by the page's sketch), not measured; the 250 ms timeout and the 1500 ms slow call are from `ScriptFaultTests.cpp`.
- Browsers run pages in separate processes, and Lua and WebAssembly are virtual machines: general knowledge, cited in Further reading without links.

## Since

`CrashGuard.h` was added in commit a0f2865f (2026-10-08), contained in tag v0.3.0; the page's `since` is 0.3.0.

## Findings not applied

- The brief says the Windows filter chooses 18 exception codes; the code at the pin lists 19 (17 hardware exceptions, the MSVC C++ exception and the abort code). The page says 19.
- Lab `scripting:544` (a program around `CrashGuard::Invoke`): not written; a standalone program cannot link the engine, so the toy sketch and the watchdog sketch replace it.
- `scripting:371` (the stack guarantee excerpt, `WindowsCrashGuard.cpp` lines 43-60): not quoted, for size; the page teaches the 32 KiB guarantee in prose.
- The filter's code list (`WindowsCrashGuard.cpp` lines 99-123) is described in prose, not quoted.
- Section "What went wrong before": omitted, no verified bug history.
- The toast and Console figure (`scripting:437`): text form only, no picture (see Requests).

## Clerk

- Admitted to names.txt: Lua, WebAssembly, POSIX.
- Admitted to extra-words.txt: abort.
- Fixed the tool defect behind its term-defined finding: tools/lint.py's code_name now reads a name of code spans joined by a slash as the one code word the page's text makes of them, so the page's **`sigsetjmp`/`siglongjmp`** defines the term.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

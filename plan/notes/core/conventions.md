# Notes: `core/conventions`

## New terms

- **assertion**: a check that ends the program on a programmer error, defined in the page's problem section. Home:
  `core/conventions`. Aliases: assertions, assert, asserts. (The brief's items `foundation:611` and `build-test:628`
  home "assert and verify"; the glossary holds only the two macros, so the page uses "assert" and "verify" in plain
  words and defines the macros in bold.)
- **log level**: how serious a log message is. Home: `core/conventions`. Aliases: log levels, level.
- **logger**: a named source of log messages. Home: `core/conventions`. Aliases: loggers.
- **sink**: a place where log messages end, such as the console or a file. Home: `core/conventions`. Aliases: sinks.
- **recoverable failure**: a failure that real data or a real system can cause, which a program must survive by
  returning an error. Home: `core/conventions`. Aliases: recoverable failures.

The page also defines the two glossary entries homed here (`st-core-assert`, `st-core-verify`), in bold with the code
span, as the brief says.

## Requests

- `logger`, `loggers`, `recoverable`: proposed above under New terms; their word-list findings are left until the
  terms exist.
- `tools/lint.py`, rule `term-defined`: the two entries homed here have names in backticks, and `match_names` reads
  only words of kind "word", so a bold `ST_CORE_ASSERT` or `ST_CORE_VERIFY` (code inside bold) is never found as the
  definition, and the lint reports "never uses it" for both. The page defines each in bold with the code span; the
  two findings are left until the planner changes the entries or the lint.

## Since

`since: 0.3.0`, the earliest release the field allows. `Assert.h` and `Log.h` came with the first commit (`a0f2865f`,
"Add build system, pinned dependencies and engine core"), `JsonUtils.h` with `938c7c9e` ("Add math, reflection and
scene (ECS) modules") and `ErrorThrottle` with `22406b04` ("Log recurring renderer errors once"); `v0.3.0` contains
all four.

## Not verified

- The loader example (a texture header, a mip level of 7 of 5, a format table) is invented to show the three answers;
  the page says so by presenting it as an example, and no such loader is quoted.
- The alternatives table names techniques and who uses them from general knowledge (managed languages, C libraries);
  no source is cited for them.
- Claim that `fmt` replaces `{}` with the arguments and that glm types print through `glm::to_string`: the glm
  formatters were read in `Log.h`; fmt's behavior is the library's.
- Further reading entries (cppreference, spdlog, fmt, nlohmann, Microsoft's `__debugbreak`) were not fetched; the
  addresses are from memory.
- That Windows renames `CopyFile` to `CopyFileW` (or `CopyFileA`) is the Windows headers' behavior, not read in the
  clone.

## Findings not applied

- The brief lists no open findings.
- `AGENTS.md` calls the formatting "enforced"; the page says no test or job runs a format check, as the brief's `new:4`
  row directs (not re-searched beyond that row's evidence).
- The history section "What went wrong before" is omitted: no regression story for these rules was verified at the
  pin.

## Clerk

- Admitted: assertion (alias assertions; "assert" left out: the page's verb in plain words), log level ("level" left out: one everyday word), logger, sink, recoverable failure. "logger" was asked by `core/debugging` too; the brief's item `foundation:613` homes it here.
- Tool: `term-defined` now counts a bold code span of exactly an entry's code name (**`ST_CORE_ASSERT`**, **`ST_CORE_VERIFY`**) as its definition (tools/lint.py `defined_as_code`, test `ClerkNameTests`).

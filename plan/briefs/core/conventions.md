# Brief: `core/conventions`

| Field | Value |
| --- | --- |
| Title | Ownership, errors and logging in Strata |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/first-change`, `basics/cpp-modern` |
| From | foundation "C++ for engine code: ownership, errors and logging" (the Strata half; §1.5: logging, asserts, `ErrorThrottle`); the code style and why |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/conventions` — Ownership, errors and logging in Strata

**Covers.** The job: the rules every engine file keeps about who owns what, what happens when something goes wrong, what
is logged and how the code looks, each with its reason. Ownership first, Strata's half of it (the language is
`basics/cpp-memory`'s): `Scope` for one owner, `Ref` for shared ownership, raw pointers and references for borrowing;
registries own what they make through `Scope` and hand out raw pointers (the module registry is the example); assets are
held across frames by handle, not by `Ref` (one sentence and a link). Then errors: exceptions as the language has them
are `basics/cpp-modern`'s (`throw`, `try`, `catch` and unwinding, named in one sentence with a link), and this page
keeps Strata's rule for them; programmer errors against failures a program must survive; `ST_CORE_ASSERT`, compiled out
of Dist, so its condition must have no side effects, against `ST_CORE_VERIFY`, which every build keeps; recoverable
failures return `bool`, `std::optional` or a result struct and log; engine code does not throw, exceptions of
third-party code are caught where it is called (`JsonUtils` wraps nlohmann's JSON, which throws on ordinary data:
dumping a string that is no valid UTF-8, whose bytes `Dump` and `AppendString` replace with U+FFFD), and the frame loop
catches what still escapes. Then logging as a convention: levels, the three loggers (Strata, App and Script) and their
macros, fmt formatting with glm types, warnings written at once; never a message per frame (`ErrorThrottle`) and never a
secret. Last the code style and why: names with `m_`, `s_`, `t_` and `c_`, tabs, braces on their own lines,
`#include "stpch.h"` first, and no names that Windows headers define as macros; `.clang-format` and `.editorconfig`
guide code editors and reviewers, and nothing runs a format check. The toy is a 30-line assert macro and a logger with
two levels; the real code is `Base.h`'s aliases and macros, `Assert.h`'s macros and `JsonUtils` or `ErrorThrottle` as
the error policy at work. The page's example is a loader that meets a broken file, decided three ways: assert, verify or
a returned error. The exercises: three failures sorted into assert, verify and returned error; a trace of
`ST_CORE_VERIFY` from its macro to the log line; an assert with a side effect that the Dist build removes. At the end
the reader chooses between an assert, a verify and a returned error, logs as the engine does, and writes code the review
accepts.

**Leaves out.**

- RAII, smart pointers and move semantics as C++ → `basics/cpp-memory`
- C++ exceptions as the language has them: `throw`, `try`, `catch` and unwinding → `basics/cpp-modern`
- How the log is written: the buffer, the background writer and its flushes → `core/debugging`
- Reading asserts and the log while debugging, and the assert handler → `core/debugging`
- Precompiled headers and what they cost → `engineering/flags-portability`
- The review checklist and how a change lands → `engineering/contributing`
- Platform headers and Windows macros in full → `core/platform`
- UTF-8 strings and paths → `core/files`

**Fit.** `fits`: about 4,950 words against L (5,000). The error policy (asserts, verifies, returned errors and the catch
at the call site) and the code style with its reasons take the most; the three exercises take about 750, and exceptions
as the language has them are `basics/cpp-modern`'s (about 300 fewer).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:270` | concept | home | Ownership in Strata: `Scope`, `Ref`, borrowed raw pointers, registries that own through `Scope`; the mistakes (`Ref`s to assets across frames, a lambda that holds the last reference); the language half is `basics/cpp-memory`'s |
| `foundation:275` | concept | home | Asserts, verifies, returned errors and exceptions, and the rule that chooses between them |
| `foundation:280` | concept | home | Logging: levels, loggers, sinks, the flush policy, why not per frame and never a secret; how the writer works is `core/debugging`'s |
| `foundation:90` | feature | home | `Log`: the loggers Strata, App and Script, the macros `ST_CORE_*` and `ST_*`, fmt formatting with glm formatters, flush on warning |
| `foundation:93` | feature | home | Asserts and verifies (`ST_CORE_ASSERT`, `ST_ASSERT`, `ST_CORE_VERIFY`, `ST_VERIFY`), compiled out of Dist or kept; `core/debugging` reads the handler and the debugger detection again |
| `foundation:94` | feature | home | `ErrorThrottle`: a repeating error logged once until it is cleared |
| `foundation:153` | feature | home | The base macros `ST_DEBUGBREAK`, `ST_BIT`, `ST_BIND_EVENT_FN`, `ST_DEFINE_ENUM_FLAG_OPERATORS` and `ST_ENABLE_ASSERTS` |
| `foundation:159` | feature | home | `JsonUtils`: parsing and dumping nlohmann JSON without exceptions, the catch at the call site in practice, with the header's own case in one sentence: nlohmann's JSON throws when it dumps a string that is no valid UTF-8, and `Dump` and `AppendString` replace those bytes with U+FFFD (`Strata/src/Strata/Core/JsonUtils.h:24-36`); its SAX half, `JsonEvents`, is used by `world/serialization` |
| `new:4` | feature | home | The code style: the naming table with its prefixes, the formatting rules that `.clang-format` and `.editorconfig` hold for code editors and reviewers, the include order, the conventions, and the reason for each; nothing runs a format check (no CI job and no test runs clang-format, though `AGENTS.md:144` calls the formatting "enforced"). Evidence: `AGENTS.md:128-181`; `Docs/DeveloperGuide.md:919-937`; `.clang-format` and `.editorconfig` at the repository's root; `git grep -n -i "clang-format" 822a7a46 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` |
| `foundation:353` | code | home | `Strata/src/Strata/Core/Base.h:10-61`: the `Scope` and `Ref` aliases, `ST_BIND_EVENT_FN` and the flag operators for `enum class` |
| `foundation:354` | code | home | `Strata/src/Strata/Core/Assert.h:53-74`: the assert and verify macros (`do { } while (false)`, `[[unlikely]]`, compiled out without `ST_ENABLE_ASSERTS`); the handler in `Assert.cpp` is quoted on `core/debugging`, which teaches it |
| `foundation:475` | rule | home | Engine code does not throw; third-party exceptions are caught at the call site; recoverable failures return errors and log; asserts only for programmer errors |
| `foundation:478` | rule | home | Asserted conditions have no side effects, because Dist removes them |
| `foundation:485` | rule | home | Do not log per frame; throttle repeating errors |
| `foundation:611` | term | home | Two entries: assert and verify |
| `build-test:628` | term | home | `ST_CORE_ASSERT` and `ST_CORE_VERIFY`, the build's entry for the two checks, compiled out of Dist and kept in it: the same entries as `foundation:611` |
| `foundation:613` | term | home | Three entries: logger, sink and level |
| `foundation:152` | feature | use | The `Ref`, `Scope` and `WeakRef` aliases, taught by `basics/cpp-memory`; this page states Strata's rules for them |
| `foundation:617` | term | link | `Scope`, `Ref` and `WeakRef`, whose entry is `basics/cpp-memory`'s |
| `foundation:167` | feature | use | `stpch.h` first in every engine `.cpp`, as a rule of the style; what a precompiled header is and costs is `engineering/flags-portability`'s |
| `new:20` | hands-on | home | Exercises: Basic, three failures sorted into an assert, a verify and a returned error (a project file that does not parse, an index past the end of an engine array, a registry used before registration) with the reason for each; Medium, trace it yourself: `ST_CORE_VERIFY` followed with a search or the debugger from its macro to `HandleAssertFailure` and the critical log line; Hard, done on the source build: a test whose `ST_CORE_ASSERT` has a side effect, passing in Debug and failing in Dist, and the fix. Evidence: `Strata/src/Strata/Core/Assert.h:53-74`; `Strata/src/Strata/Core/Assert.cpp:32-66`; `Strata/src/Strata/Core/Base.h:10-12` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Pointers, references, lifetimes, RAII, `unique_ptr`, `shared_ptr` and `weak_ptr`; `Scope` and `Ref` | `basics/cpp-memory` | must |
| Move semantics, `std::optional`, `enum class`, `constexpr` and macros | `basics/cpp-modern` | must |
| C++ exceptions: `throw`, `try`, `catch`, and the unwinding that runs destructors | `basics/cpp-modern` | must |
| Templates with several arguments (fmt's `{}` and its arguments) | `basics/cpp-generic` | helps |
| Debug, Release and Dist, and a build with a preset | `core/first-change` | must |
| JSON | `basics/data-formats` | helps |
| `glm` vectors | `basics/math-vectors` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `st-core-assert` | `ST_CORE_ASSERT` | - |
| `st-core-verify` | `ST_CORE_VERIFY` | - |

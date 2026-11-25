# Brief: `engineering/testing`

| Field | Value |
| --- | --- |
| Title | Testing an engine |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | - |
| From | build-test ch. 7, the concept half (test kinds, determinism and flakiness, regression tests that fail without their fix, coverage by construction, sweeps as an idea); home of testing |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/testing` — Testing an engine

**Covers.** The problem as a reader meets it: a test that passed on its author's machine fails on CI's macOS runner,
which has three hardware threads, and passes when it runs again; and a bug fixed last month is back. The naive answer:
run the program and look, or add a check once. Where it breaks: nobody looks at every change, and a test that waits a
fixed number of frames or reads the user's files is a coin toss. The idea: a test is a program that checks one claim
and fails loudly, and a suite is worth as much as it is repeatable. The approaches, each introduced by the flaw of the
one before, with a table of cost, speed, what each catches and who uses them: unit, integration, end-to-end and smoke
tests; snapshot (golden-file) tests, with the component schema snapshot as Strata's example (a committed JSON of every
component's name, metadata and properties in order, which `Reflection.ComponentSchema` compares with the live
registry, about 80 words); golden images against before-and-after image comparisons; corruption sweeps and fuzzing;
performance gates.
Test frameworks: doctest's `TEST_SUITE`, `TEST_CASE`, `CHECK` against `REQUIRE`, `INFO` and `CAPTURE`, filters, and a
runner such as CTest above the test binary, extending the one case of `core/first-change`; doctest's
`expected_failures` as the way to test code whose job is to fail a test, with the perf harness's cases that must fail,
such as a confirmed check over its budget in every attempt (about 60 words). Determinism and flakiness:
wait on a condition or the clock, never on frames; private temporary folders, free ports and private sessions; no
shared process state; fixed seeds; the slowest machine as the yardstick; why a flaky test is worse than none.
Regression tests: a test that has never failed proves nothing, so a new regression test is checked to fail without its
fix. Strata's choice: everything ships with tests, and no test is disabled, skipped or weakened to pass (golden rule
2); coverage by construction instead of line coverage, in one paragraph with a link, and Strata measures no line
coverage; sweeps as an idea, in one paragraph with a link. The page's example: one timer test written three ways
(sleep then check, count frames, wait for the condition with a clock limit) and run on a loaded machine. Common
mistakes: a sleep followed by an assert, a test that cannot fail, a test that depends on a program outside the build.
Exercises: break the reader's `ToUpper` of `core/first-change`, see its test case fail and restore it; rewrite a
test that counts frames to wait with `Tests::WaitUntil` and a clock limit, and run it beside a loaded machine's other
work; for three changes (a parser, a shader fix, an editor command) name the kind of test each needs and why.
At the end the reader can say which kind of test a change needs, write a test that cannot flake, and check that a
regression test fails without its fix.

**Leaves out.**

- StrataTests' main, helpers, shards, labels, fixtures and locks → `engineering/test-program`
- Corruption sweeps and fuzzing in Strata → `engineering/test-program`
- GPU, end-to-end and package tests → `engineering/test-kinds`
- The feature test → `engineering/feature-test`
- Performance tests and their budgets → `engineering/perf-lab`
- Image comparisons with the look-dev harness → `engineering/look-dev`
- Play-tests of a game through command scripts → `make/automated-playtests`

**Fit.** `fits`: about 3,230 words against M (3,000). Two concepts from zero, the approaches table with its snapshot
row, the frameworks in short (the reader wrote one case already), two rules, the timer example and three exercises take
the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:327` | concept | home | What a test is; unit, integration and end-to-end; test frameworks (doctest's suites, cases, `CHECK` and `REQUIRE`, filters, and `expected_failures` for code whose job is to fail a test, with the perf harness's cases that must fail); every change ships with tests; the mistake of weakening a test to get green |
| `new:30` | concept | home | Snapshot (golden-file) tests, a row of the approaches table: a committed file of the expected output compared with what the code makes now, and rewritten on purpose; Strata's example is `StrataTests/Architecture/ComponentSchema.json`, every component's name, metadata and properties in order, which `Reflection.ComponentSchema` compares with the live registry and the helper mode `write-component-schema` writes again (about 80 words). Evidence: `StrataTests/src/Reflection/ComponentSchemaTests.cpp:14-50`; `StrataTests/src/TestMain.cpp:240-246`; `.claude/skills/strata-add-component/SKILL.md:57` |
| `build-test:335` | concept | home | Determinism and flakiness: conditions or the clock, never frames; private folders, ports and sessions; no environment changes for children; the slowest CI machine as the yardstick; the mistake of a sleep then an assert |
| `build-test:514` | rule | home | Wait by the clock or a condition, never by frames; size job pools explicitly: CI's macOS runners have three hardware threads |
| `build-test:520` | rule | home | Check that a new regression test fails without its fix |
| `build-test:657` | term | home | doctest, with `TEST_SUITE`, `TEST_CASE`, `CHECK`, `REQUIRE`, `INFO` and `CAPTURE` |
| `build-test:683`, `build-test:684` | term | home | End-to-end test; smoke test |
| `new:31` | hands-on | home | The page's exercises (about 250 words): break the reader's `ToUpper` of `core/first-change`, see its case in `Core.StringUtils` fail and restore it; rewrite a test that counts frames to wait with `Tests::WaitUntil` and a clock limit; name the kind of test three changes need (a parser, a shader fix, an editor command). Evidence: `Strata/src/Strata/Core/StringUtils.h:13`; `StrataTests/src/Core/StringUtilsTests.cpp:9`; `StrataTests/src/TestHelpers.h:62-63` |
| `new:5` | not-done | home | No measurement of line coverage: the feature test's coverage by construction stands in its place. Evidence: `git grep -niE "\-\-coverage\|llvm-cov\|gcov\|OpenCppCoverage\|fprofile-instr" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github Tools` finds nothing |
| `build-test:246` | feature | link | Golden rule 2, whose home is `engineering/contributing` |
| `build-test:345` | concept | link | Sweeps as an idea, taught on `engineering/test-program` |
| `build-test:356` | concept | link | Coverage by construction, taught on `engineering/feature-test` |
| `build-test:127` | feature | link | `Tests::WaitUntil` and the other helpers that keep tests repeatable |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One test case in a suite, `CHECK`, running a suite with doctest's filter | `core/first-change` | must |
| Threads and races | `basics/threads` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| Processes and their environment | `basics/computer` | helps |
| The job system and its threads | `core/jobs` | helps |
| Frames, fixed steps and the clock | `core/time` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `doctest` | doctest | - |
| `end-to-end-test` | End-to-end test | - |
| `smoke-test` | Smoke test | - |

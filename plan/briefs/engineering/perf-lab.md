# Brief: `engineering/perf-lab`

| Field | Value |
| --- | --- |
| Title | Measuring performance honestly: noise, percentiles, budgets and the perf lab |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/test-kinds`, `core/profiling` |
| From | build-test ch. 10 and concept 21; foundation concept 20 (benchmark statistics, noise, budgets, confirmed checks, results files, the canary, the ratchet, provisional metrics, PerfStability, PerfLock, A/B and layout effects); home of "measured on the reference machine" |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/perf-lab` — Measuring performance honestly: noise, percentiles, budgets and the perf lab

**Covers.** The job: Strata's performance tests, the tools around them, and the method that makes their numbers
honest; the home of the design decision "trade-offs are measured on the reference machine, and the numbers are shown",
stated in a `:::why`. The problem, in the part's full section on it: benchmarks against gates; warm-up; median, mean and
percentiles; noise only adds, because the machine's other work never makes code faster, so one attempt within the
budget decides; confirmation by measuring again; reference machines; budgets with headroom; ratchets; provisional
metrics; canaries; interleaved A/B runs; layout effects (48 bytes of moved code shifted CPU medians by about 7%);
hybrid CPUs with performance and efficiency cores; the mistakes (raising a budget to pass, trusting one run, measuring
on a busy machine, numbers from a Debug build). The map: the perf suites as CTests (`StrataTests.Perf` for `Perf.*`,
`StrataTests.PerfGPU` for `PerfGPU.*` with validation off, `StrataTests.PerfGPU.Samples` after the sample exports),
in Release and Dist only, `RUN_SERIAL`, after the clean of the results file. The contract: limits live only in
`Budgets.json`; budgets only go down; a budget is at most 1.5 times the measurement; a commit that adds or lowers one
states the measured values; a budget goes up only for a change of machine shown by an interleaved A/B against the
commit that set it, or once for a cost the owner accepted by name; perf tests measure the Medium preset unless the
metric names another; measure with the Visual Studio preset the budgets were set with (`ctest --preset
windows-release -L perf`), never `windows-ninja`, whose MSVC builds get no `/arch:AVX2` and so compile other engine
code (about 60 words). The toy: measure, summarize and check against a budget in 40 lines. The real code: `Measure`
and `Summarize` (warm-up, the median, the nearest-rank p95 in integers so that no rounding moves it); the budget file,
whose comment is its specification (the reference machine, the units, `Target`, `Provisional`); `CheckConfirmed`
(every metric known before anything is measured, decided once within the budget, up to three attempts, every attempt
recorded); the results file, which holds nothing of one run so that two can be compared; the canary
`Perf.Harness.Sort200k`, the median of 31 sorts of fixed numbers, whose slowness says the machine is slow;
`Tools/PerfStability.py`, which turns repeated runs into budget proposals under the ratchet (`classify`) and compares
against a baseline; `Tools/PerfLock.py`, one measurement at a time on a machine, with its exit codes; the scene
generators and world fixtures; peak memory measured in a fresh helper process; GPU timing through `MeasureFrames` and
`MeasureGPU`. The paragraph that introduces the page's first Python fence (`classify`) says in one or two sentences
what differs from C++ in it: no page of the book teaches reading Python, so the page supplies it (R45). Every suite and every budget, with the machine, are `reference/performance`'s table. How it is tested:
the `PerfLab` suite in the Core shard, in every configuration, and `Perf.Harness`. Exercises: add a provisional metric,
measure it inside a confirmed check, run `ctest --preset <preset>-release -L perf`, read `PerfResults`, then read what
`PerfStability.py --runs 3 --propose-budgets` would write; trace it yourself: follow one `[perf]` line of the run by a
search back to the `printf` that wrote it, the confirmed check that measured it and the entry of `Budgets.json` that
decided it. At the end the reader can add a perf metric with an honest
budget, tell a regression from a noisy machine, and explain every number a perf run prints.

**Leaves out.**

- Measuring a frame: percentiles, self time, Tracy, "CPU, GPU or capped" → `core/profiling`
- GPU timestamps and stages → `gpu/readback-timing`
- Every perf suite and every budget, and the machine they were measured on → `reference/performance`
- Tuning physics and its sweep → `physics/tuning`
- A perf budget for a new feature → `capstone/land`
- Measuring a shipped game with `--perf-log` → `make/performance`

**Fit.** `fits`: about 5,380 words against L (5,000). One large concept (about 900 words, the design decision's home),
five excerpts, four figures, six rules and the lab's tools take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:351` | concept | home | Performance testing and noise: benchmarks and gates, warm-up, median and percentiles, noise only adds, confirmations, reference machines, budgets with headroom, ratchets, provisional metrics, canaries, A/B, layout effects, hybrid CPUs; the mistakes |
| `build-test:135-145` | feature | home | The perf suites; `Measure`; the budget file; confirmed checks; the results file; the canary; the lab's self-tests; scene generators and fixtures; peak-memory helpers; GPU timing; the Medium preset rule |
| `build-test:147-149`, `build-test:223`, `build-test:224` | feature | home | The ratchet and re-baselining; `Tools/PerfStability.py` and `Tools/PerfLock.py`, which the inventory lists twice (in the lab and among the tools) |
| `build-test:402` | code | home | `StrataTests/src/Perf/PerfUtils.cpp:104-146`: `Summarize` and `Measure`, the median and the nearest-rank p95 in integers, the warm-up |
| `build-test:403` | code | home | `StrataTests/src/Perf/PerfUtils.cpp:291-370`: `CheckConfirmed`, decided once within budget, the rest measured again, every attempt recorded |
| `build-test:404` | code | home | `StrataTests/Perf/Budgets.json:2-27`: a budget file whose comment is its specification, and the canary's entry |
| `build-test:405` | code | home | `StrataTests/src/Perf/PerfHarnessTests.cpp:512-543`: the canary, a fixed workload that probes the machine's health |
| `build-test:406` | code | home | `Tools/PerfStability.py:348-390`: `classify`, repeated runs turned into proposals that never raise a budget unless re-baselined |
| `build-test:440` | figure | home | The confirmed check as a flowchart, with a sketch of noise that only adds (a distribution with a hard lower floor) |
| `build-test:443` | figure | home | A budget's life: provisional, measured on the reference machine, 1.5 times the measurement, lowered when cheaper, re-baselined only by A/B |
| `build-test:464` | figure | home | Text captures of `[perf]` lines, an "over the budget in attempt 1 of 3, measuring again" line and a `PerfResults` excerpt |
| `build-test:466` | figure | home | A text capture of the report of `Tools/PerfStability.py --runs 5` |
| `build-test:523` | rule | home | Limits only in `Budgets.json`; budgets only go down; at most 1.5 times measured; commits state the measurement |
| `build-test:525` | rule | home | A failure on a busy machine says nothing about the code: run again on a quiet machine, look at the canary |
| `build-test:527` | rule | home | Perf numbers only from optimized builds, without validation layers, through `ExecuteAndWait` |
| `build-test:530` | rule | home | Peak-memory metrics in a fresh helper process |
| `build-test:531` | rule | home | Complexity claims belong in deterministic unit tests, which run everywhere |
| `new:35` | rule | home | Measure with the Visual Studio preset the budgets were set with (`ctest --preset windows-release -L perf`, the `windows` preset), never `windows-ninja`: MSVC gets `/arch:AVX2` only with the Visual Studio generators, so a `windows-ninja` build compiles other engine code than the one the budgets measured (about 60 words). Evidence: `StrataTests/Perf/Budgets.json:9-11`; `CMakePresets.json:11-14`, `:25-29`, `:75`; `CMake/StrataCompilerOptions.cmake:40-55` |
| `build-test:578` | hands-on | home | Add a provisional metric, measure it in a confirmed check, run `-L perf`, read `PerfResults` and the proposals of `PerfStability.py` |
| `new:36` | hands-on | home | Trace it yourself, by a search: one `[perf]` line of a run back to the `printf` that wrote it, the confirmed check that measured the metric and its entry in `Budgets.json` (about 150 words). Evidence: `StrataTests/src/Perf/PerfUtils.cpp:96-100`, `:141-143`, `:291-370`; `StrataTests/Perf/Budgets.json:27` |
| `build-test:671-678` | term | home | Perf lab; metric, budget, target and provisional (four entries); reference machine; confirmed check; ratchet; canary; interleaved A/B |
| `foundation:303` | concept | use | Percentiles by nearest rank, self time and "CPU, GPU or capped", as `core/profiling` taught them |
| `build-test:146` | feature | link | The catalogue of perf suites, `reference/performance`'s |
| `build-test:116` | feature | use | `RUN_SERIAL` and why the perf tests run alone |
| `build-test:679` | term | link | Median, p95 and nearest rank, whose entries are `core/profiling`'s |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Percentiles by nearest rank, self time, "CPU, GPU or capped", Tracy | `core/profiling` | must |
| The GPU suites and the sample exports as CTests | `engineering/test-kinds` | must |
| Labels, fixtures and `RUN_SERIAL` of CTest | `engineering/test-program` | must |
| Release and Dist, the optimized configurations | `core/first-change` | must |
| GPU timestamps and stages | `gpu/readback-timing` | helps |
| Caches, and why the place of code in memory matters | `basics/computer` | helps |
| Distributions and noise | `basics/math-probability` | helps |
| File locks | `core/files` | helps |
| JSON | `basics/data-formats` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `budget-engineering` | budget (engineering) | - |
| `canary` | Canary | - |
| `confirmed-check` | Confirmed check | - |
| `interleaved-a-b` | Interleaved A/B | - |
| `metric` | Metric | - |
| `perf-lab` | Perf lab | - |
| `provisional` | provisional | - |
| `ratchet` | Ratchet | - |
| `reference-machine` | Reference machine | - |
| `target` | target | - |

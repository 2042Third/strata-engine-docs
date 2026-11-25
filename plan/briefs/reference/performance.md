# Brief: `reference/performance`

| Field | Value |
| --- | --- |
| Title | Measured costs and their budgets |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `engineering/perf-lab` |
| From | new; every perf budget in one table: generated from `StrataTests/Perf/Budgets.json`, with the catalogue of perf suites (build-test ch. 10); names the reference machine the values were measured on, as `Docs/DeveloperGuide.md` ("Perf tests") states it; why budgets are measured there is `engineering/perf-lab`'s |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/performance` — Measured costs and their budgets

**Covers.** The paragraph on top says what the page is: every perf budget of the engine in one table, generated from
`StrataTests/Perf/Budgets.json`, and how to read an entry: the metric `<Suite>.<Metric>` (suites `Perf.*` on the CPU,
`PerfGPU.*` with a GPU), its unit, `Measured` (the value measured on the reference machine), `Budget` (the limit the test
enforces, at most 1.5 times the measurement), the optional `Target` (a goal below the budget), and provisional entries
(`Provisional`: measured once and recorded, never failing, until the reference machine measures them). It names the
reference machine as `Docs/DeveloperGuide.md` ("Perf tests") states it: i7-13700K, RTX 5090, Windows 11, Release, a
quiet machine; and it says that a reader's machine gives other numbers, that budgets only go down, and that the
numbers of other machines never enter the file. The generated part: the budgets grouped by suite, about 250 entries,
in the file's order (route "perf budgets", `../pipelines.md` §7.1). Each budget also gives its keys
`perf.<name>.Measured`, `perf.<name>.Budget` and `perf.<name>.Unit` of `values.json` (§7.3), which other pages use in
prose; a key exists only where `Budgets.json` gives the value, so a page that cites a budget without a measurement
states the budget and says that it is provisional. A second generated table lists every CPU stage the Performance
panel can show, each with the file that times it (route "CPU stages"): the twelve built-in stages of
`c_BuiltinFrameStages`, the names passed to `ST_PROFILE_STAGE` and to `RegisterStage` without `FrameStageKind::GPU`,
and the `ProfileStage` of each scene system's descriptor; `core/profiling` links it, and the GPU stages are
`reference/renderer`'s. Hand-written: the catalogue of perf suites, one row per suite (`Perf.Scene`, `Perf.Physics`,
`PerfGPU.Renderer` and the others) with what it measures, its test file and the page that explains the cost, checked
against the `TEST_SUITE` names of `StrataTests/src/Perf/` and `StrataTests/src/Editor/*Perf*` at the pin; and
`## Where it lives in Strata` (`StrataTests/Perf/Budgets.json`, `StrataTests/src/Perf/`, `Tools/PerfStability.py`,
`Tools/PerfLock.py`, `Strata/src/Strata/Core/FrameProfiler.h`). The tool is `tools/reference.py parse`, routes "perf
budgets" and "CPU stages". Why budgets are measured on one machine, and how the lab keeps the numbers honest, is
`engineering/perf-lab`'s.

**Leaves out.**

- Benchmarks, noise, percentiles and the perf lab → `engineering/perf-lab`
- Measuring a frame → `core/profiling`
- Making a game run fast → `make/performance`
- A budget added in one change → `capstone/land`

**Fit.** `fits`: about 1,250 words against M (3,000). The generated tables give the page its size: about 250 budgets
with their `perf.<name>` keys, roughly 2,500 words, and the CPU stages with the files that time them, about 300. The
prose is the paragraph on top with the reference machine (400 words), the sentence on the keys and the introduction of
the stages (120), the catalogue of 24 suites with its introduction (640) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:146` | feature | home | The catalogue of perf suites: one row per suite with what it measures, its test file and the page that explains the cost. Taken from the `TEST_SUITE` names at the pin, not from the inventory's list: 24 suites (16 `Perf.*`, 8 `PerfGPU.*`), among them `Perf.Asset`, `Perf.GameUI`, `Perf.Input`, `PerfGPU.GameUI`, `PerfGPU.World` and the two `Harness` suites, which the list leaves out |
| `build-test:135-139` | feature | link | The perf suites, the measurement, the budget file, confirmed checks and the results file |
| `build-test:145`, `build-test:147` | feature | link | The Medium preset rule and the ratchet |
| `build-test:148-149` | feature | link | `Tools/PerfStability.py` and `Tools/PerfLock.py` |
| `foundation:96` | feature | link | `ST_PROFILE_STAGE` and `FrameProfiler`: every CPU stage with the file that times it, as the generated table that `core/profiling` links |
| `animation:202` | feature | link | The animation perf tests |
| `physics:173` | feature | link | The physics perf tests |
| `gameui:241` | feature | link | The game UI perf tests |
| `editor-ui:260` | feature | link | The editor panels' perf tests |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Benchmarks, noise, perf budgets, the perf lab | `engineering/perf-lab` | must |
| Measuring the frame | `core/profiling` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

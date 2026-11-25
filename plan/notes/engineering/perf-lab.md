# Notes: engineering/perf-lab

## New terms

None proposed. The page defines the ten terms the glossary homes on it (perf lab, reference machine, metric, budget, ratchet, target, provisional, confirmed check, canary, interleaved A/B).

## Since

0.3.0: `StrataTests/src/Perf/PerfUtils.h` was added in a commit contained in v0.3.0 (46b6af86).

## Requests

- Words: "GeForce" and "RTX" (names; the page writes the card's name as code for now).
- Figures: none drawn. The text captures the brief asks for ([perf] lines, a PerfResults excerpt, the report of PerfStability.py --runs 5) are not requested: they need a Release run on the reference machine; the page shows the formats in prose and quotes. The three diagrams are Mermaid.

## Not verified

- The reference machine's hardware beyond Docs/DeveloperGuide.md and the Budgets.json comment (read, not measured).
- The hosted CI runners skip the label perf: from the guide, not from ci.yml.
- Google Benchmark, Cachegrind, hosted-runner comparisons: the table speaks of kinds of tools in general terms; not checked against any source.

## Findings not applied

The brief lists no open findings. Left out of the page: `PerfGPU.Harness` failing without STRATA_TEST_GPU_VALIDATION=0 (named only as validation layers off), peak-memory helper details beyond one function name, the library-only metric splits of physics (belong to physics/tuning), the hyperthread effect of 1.12.

## Clerk

- Admitted to names.txt: GeForce, RTX.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

# Brief: `engineering/contributing`

| Field | Value |
| --- | --- |
| Title | The review checklist and the way a change lands |
| Kind | H |
| Size | M |
| Tracks | E |
| Needs | `engineering/ci`, `engineering/feature-test` |
| From | build-test ch. 14 (the golden rules, the pre-commit checklist, verification in a clean worktree, commit hygiene, the third-party rule) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/contributing` — The review checklist and the way a change lands

**Covers.** The goal: land a change to Strata the way every change lands. What must be true first, as a list: a change
and its test in the reader's clone (the `ToUpper` change of `core/first-change` serves); a fork with GitHub Actions
on, for the CI step. The frame, in a short list: the golden rules (everything ships with tests, review before every
commit, follow the code style, no hacks or shortcuts, keep the feature test current, and take code from other projects
only under a permissive license with its notice, copyleft only for ideas). The steps: make the change one logical
change; cover new behavior with a test, and for a fix check that the regression test fails without it; extend the
feature test when something registered changed; update `Docs/` and `AGENTS.md` when behavior or a workflow changed,
with `AGENTS.md` under 40,000 characters (`Docs.AgentGuide` checks it and its links); stage the change and review
`git diff --staged` against the six items of the pre-commit checklist (correctness, tests, style, portability,
documentation, commit hygiene), shown as a table with what to look for in each; run every test locally
(`ctest --preset <platform>-debug -j 8`), and `-L perf` in Release for a change that can move performance; verify
exactly what is staged in a clean worktree, in Debug and Release, with the skill's commands; write the commit message
(an imperative subject under 72 characters, a body that says what and why); push a change that lands much as
`ci/<name>` and wait for green CI, reading a failure with `Tools/CIStatus.py`; then merge. Each step names its usual
failure. Result: one commit on `main`, its tests green locally and in CI. Variations: a submodule upgrade, in a commit
of its own with the notices and every test; a change that adds or lowers a perf budget, with the measured values in
the message and `Tools/PerfStability.py --runs 5`; code taken from another project; a change to a sample, whose
command script must keep passing and which `Samples.Content` checks (every sample listed in `Samples.json`, every
source asset credited by exactly one row of `CREDITS.md`, the packs in `ThirdPartyNotices.md`, and the budgets: 25 MB
of source assets, 80 MB for a showcase; three screenshots in 3 MB, six in 8 MB for a showcase; totals that bound how
much a release archive grows; about 100 words). Exercises: take a second small change of the reader's own through
every step, from the staged diff reviewed against the checklist to a `ci/<name>` push read with `CIStatus.py`; find
what a given staged diff breaks of the six items. At the end the reader can take any change of their own through review, a clean
verification and CI to `main`.

**Leaves out.**

- How tests are written and kept from flaking → `engineering/testing`
- The feature test in full → `engineering/feature-test`
- The CI jobs → `engineering/ci`
- Licenses and the notices file → `engineering/third-party`
- Perf budgets and their ratchet → `engineering/perf-lab`
- The code style's rules → `core/conventions`
- A whole feature landed this way → `capstone/land`

**Fit.** `fits`: about 3,090 words against M (3,000). Nine steps, the checklist as a table, one excerpt, four variations
and two exercises take the most. The concept of process discipline (`build-test:369`) is homed on this how-to because no
concept page of the book teaches reviewing and landing a change: the reader learns it by doing the steps, each with its
why in at most two sentences (R31 D25).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:369` | concept | home | Process discipline: the review checklist, commit hygiene, verification in a clean worktree; the mistake of committing what the working tree compiles, not what is staged |
| `build-test:246-248` | feature | home | Golden rules 2, 3, 5 and 6 (with rules 1 and 4 named); the six-item pre-commit checklist; verifying in a clean worktree |
| `build-test:186` | feature | home | `Docs.AgentGuide`: `AGENTS.md` under 40,000 characters, its links resolving to files and anchors |
| `new:22` | code | home | `.claude/skills/strata-build-test/SKILL.md:210-223`: the staged patch applied to a clean worktree, built and tested in Debug and Release |
| `build-test:543` | rule | home | Verify exactly what is staged in a clean worktree, Debug and Release: the working tree often holds other work, and some bugs show in one configuration only |
| `new:41` | feature | home | `Samples.Content`, the check a change to a sample must pass, in the variation "a change to a sample": every sample listed in `Samples.json` and no directory unlisted, every source asset credited by exactly one `CREDITS.md` row, the packs in `ThirdPartyNotices.md`, and the budgets (MB of 1,000,000 bytes: 25 MB of source assets, 80 MB for a showcase; three screenshots in 3 MB, six in 8 MB for a showcase; totals that keep the standard samples' growth of a release archive to about 60 MB, about 145 MB with showcases); its shard is `Samples` (about 100 words). Evidence: `StrataTests/src/Samples/SampleContentTests.cpp:77-178`; `Docs/DeveloperGuide.md:6479-6490`; `StrataTests/CoreShards.json:24` |
| `new:42` | hands-on | home | The page's exercises (about 250 words): take a second small change of the reader's own through every step, from the staged diff reviewed against the six items to a `ci/<name>` push on a fork read with `Tools/CIStatus.py`; and find in a given staged diff what breaks which item of the checklist. Evidence: `AGENTS.md:457-474`; `.claude/skills/strata-build-test/SKILL.md:210-223` |
| `build-test:520` | rule | use | A regression test checked to fail without its fix |
| `build-test:532` | rule | use | The feature test kept current |
| `build-test:500` | rule | use | Large integrations through `ci/<name>` |
| `build-test:523` | rule | use | A commit that adds or lowers a budget states the measured values |
| `build-test:504`, `build-test:506` | rule | use | A submodule upgraded in its own commit; copyleft code for ideas only |
| `build-test:201` | feature | use | `Tools/CIStatus.py`, to read a failed run |
| `build-test:97` | feature | use | The upgrade procedure of a submodule, as a variation |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| git: staging, diff, commit, branches and push | `basics/git` | must |
| The short source build and one test case | `core/first-change` | must |
| Regression tests that fail without their fix | `engineering/testing` | must |
| The CI jobs and `ci/<name>` branches | `engineering/ci` | must |
| The feature test and how to extend it | `engineering/feature-test` | must |
| The code style | `core/conventions` | helps |
| Perf budgets | `engineering/perf-lab` | helps |
| Licenses and the notices file | `engineering/third-party` | helps |
| git worktrees | `basics/git` | helps |

**Starting state.** No checkpoint download: the page starts from the change `core/first-change` ends with, not yet
committed (`ToUpper` beside `StringUtils::ToLower` in `Strata/src/Strata/Core/StringUtils.h`, and its test case in the
suite `Core.StringUtils`), in the reader's clone at the pin. For the CI step, a fork of the engine's repository with
GitHub Actions on.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

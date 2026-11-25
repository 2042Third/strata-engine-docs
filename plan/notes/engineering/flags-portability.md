# Notes: engineering/flags-portability

## New terms

None proposed. The page defines the eight homed terms in bold. It writes "warning policy" and "unity build" as plain words.

## Since

0.4.0: precompiled headers, the compiler cache and the CompatLint tool landed in wave 4 (inventory build-test, "wave 4 (0.4.0)"); the instruction-set options keep the defaults from before 0.5.0.

## Requests

- Glossary: the aliases of `precompiled-header` list "FMA" and "fused multiply-add", which belong to `fma-contraction`; the page writes "fused multiply-add (FMA)" plain to avoid a wrong mark.
- Further reading cites the ccache manual without a link; its host (ccache.dev) is not in `tools/external-hosts.txt`.

## Not verified

- The exit code and message of a CompatLint run on a file that lacks an include (exercise 2): derived from the code, not run.
- That the tool runs on macOS and Linux only: derived from its reading of `build-Debug.ninja`; not run.
- The measured 40 % and the wave-4 figures come from the engine's guide and roadmap, not measured here.
- The "five test files" count of the GCC workaround comes from the comment in `StrataTests/CMakeLists.txt`.

## Findings not applied

The brief lists no open findings. The brief's order of the sections follows the internals card; the real-code part is split into four sections for the term limits.

## Clerk

- Nothing to admit.
- Left for the planner: the aliases FMA and fused multiply-add of Precompiled header belong to FMA contraction; the merge keeps a seed entry's names, so an admitted alias cannot move them (merge-report: "a name of Precompiled header").
- Admitted to external-hosts.txt: ccache.dev (the ccache project's site).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

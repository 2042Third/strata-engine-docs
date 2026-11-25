# Notes: `core/review`

## Pages each exercise needs

1. Basic: `core/map`, `core/first-change`, `core/conventions` (library of a file, configure step, test filter, include order).
2. Basic: `core/frame-loop`, `core/time` (the clamp of `MaxTimestep`, the cap, the time scale before the accumulator).
3. Basic: `core/engine-modules`, `core/frame-loop` (Kahn's algorithm with the listing rule, hook order, `Skip`).
4. Medium: `core/windows-events`, `core/first-frame` (content scale, a layer that handles the first close, exit code 0).
5. Medium: `core/profiling`, `core/frame-loop` (work time, nearest rank, CPU, GPU or capped, self time).
6. Medium: `core/platform`, `core/first-frame`, `core/frame-loop` (Console run, `MaxFrameRate`, Ctrl+C, exit code 130).
7. Medium: `core/layers-registries`, `core/engine-modules`, `core/first-frame` (layer table, `EngineServices`, startup order).
8. Hard: `core/jobs`, `core/frame-loop` (`ParallelFor` batches and helpers, determinism, `SubmitToMainThread`).
9. Hard: `core/math`, `core/conventions` (assert with a side effect in Dist, returned error, mirror, reversed-Z depth).
10. Hard: `core/debugging`, `core/files` (`AtomicFileWriter`, the log's flush rule, the log file emptied at every start).

## Not covered

`core/reading-code` has no exercise of its own; exercise 1 uses the tree's map it teaches only through `core/map`.

## Seen

None.

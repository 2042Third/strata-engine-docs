# Notes: `world/systems`

## New terms

None. The page defines in bold the five terms the glossary homes on it: scene system, update phases, hard (as "hard
constraint"), soft constraint and scene service. "Engine service" is mentioned in one sentence that links
`core/engine-modules`, its home.

## Requests

- Hosts for Further reading, both cited without a link: Bevy's documentation (the ordering of systems with `before`
  and `after`) and the Unity manual of the Entities package (`UpdateBefore`, `UpdateAfter`). Neither host is in
  `tools/external-hosts.txt`.
- `tools/data/names.txt` / `extra-words.txt`: nothing; every word-list finding was reworded or written as code
  (`CameraFollow`, `EarlyInput`, `Spinner`, `Wind` are names of systems the reader makes).
- The frame timeline of the brief (`scene-ecs:433`) is a Mermaid flowchart here. The overlays for physics
  (`physics/world-step`) and for worlds (`worlds/physics-scripts`) are not drawn: a figure recipe with variants is
  needed for them and I took none.

## Since

`since: 0.3.0`: `plan/inventory/scene-ecs.md` rows 100-114 give 0.3.0 for the interface, the registry, the order,
start and stop, `OnUpdateRuntime`, pause and steps, and `OnEntityDestroying`; `Scene::Copy` and entity destruction
also 0.3.0 (rows 32 and 34). Later parts (time dilation, the project's rate, `PrepareLoadedScene`) are only named.

## Not verified

- The Spinner's place in the update order (UI, Scripting, Animation, World, Spinner, Physics, Audio) was computed by
  hand with the algorithm of `ComputeUpdateOrder`; no code ran it. The two sketches that mirror the algorithm
  (`sketches/world-systems-order.cpp`, `world-systems-front.cpp`) were compiled and run by pagecheck, and the
  front sketch prints the engine test's expected order for the back build.
- The statements about other engines (Bevy `before` and `after`, Unity `UpdateBefore` and `UpdateAfter`, Godot's
  node process priority, Unity's script execution order, Bevy's parallel system graph, "many editors and user
  interface libraries" reacting to events, "the textbook form" of the sort) come from memory of those projects'
  public documentation, not from a fetched page.
- The reason given in the rule "Destruction during an update is deferred" (a system could remove a component while
  another loops over the storage) comes from the engine's inventory of its own rationale, not from a comment of the
  code; the code's comments say only that handles stay valid for the frame and that scripts get `OnDestroy` with the
  entity complete.
- Nothing ran the doctest commands in "How it is tested"; the test names were read in the test files.
- The Perf metric `IdlePlayFrame1M` is quoted as "under a tenth of a microsecond" from its budget (0.0939 us) in
  `StrataTests/Perf/Budgets.json`; the page names no measurement.
- Godot, Bevy and Unity names in the alternatives table are cited without a fetched source.

## Findings not applied

- The brief names no open findings. The erratum `new:17` (six services named in the `SceneServices.h` comment, seven
  registered) is on the page and in the table.
- Where the code and the brief differ: the brief says Play against Simulate is "physics only"; at the pin the World
  system also has `RunsInSimulateMode` set (`WorldRegistration.cpp`, `SceneSystemTests.cpp` test of the built-ins),
  and the page says so.
- Exercise `gamedev:563` (FixedRate 30, 60 and 240, `Time::GetStepAlpha` logged each frame, step counts read with
  `play.state`) is not on the page: the card allows at most four exercises, which the Spinner, the trace, the Wind
  service and the order built from the front fill, and its forward link target `editor/commands` has no page yet.
  The page instead gives the caps of the four project rates (4, 8, 16, 32) in the section on time.
- The frame timeline's overlays for physics and for worlds (see Requests) and a separate accumulator timeline
  (`scene-ecs:436`, linked from `core/time`) are not drawn.
- The toy is two sketches of 79 and 77 lines (kind I asks 30 to 80 lines in total): the order and the frame are two
  jobs, and Hazel style with a priority queue did not fit in fewer.
- `Scene::DuplicateEntity`, `ReleaseInBackground` and the Debug cache check are not taught here (other pages); the
  Debug check is one sentence.
- No `tutorials/world/systems/exercise-<n>.patch`: the card asks for one only after `core/first-change`; the hard
  exercise is a standalone sketch.
- Lint warnings left: 63 `passive` (most state what the scene does to a value: "is dropped", "is ignored") and 3
  `noun-stack`.

## Clerk

- `external-hosts.txt`: `bevy.org` (front page fetched); `docs.unity3d.com` is listed already.
- Left for the planner: the figure overlays.

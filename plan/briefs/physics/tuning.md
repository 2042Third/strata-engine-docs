# Brief: `physics/tuning`

| Field | Value |
| --- | --- |
| Title | Tuning and measuring |
| Kind | H |
| Size | M |
| Tracks | E |
| Needs | `physics/world-step`, `core/profiling` |
| From | physics ch. 12; 1.10, 1.12, the solver side only (`Physics.Simulation`, contact recycling, the sleep threshold, the stiffness ceiling, `physics.stats`, perf tests, `PhysicsSweep.py`); the game maker's half is `make/physics`' |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/tuning` — Tuning and measuring

**Covers.** A how-to: measure a physics scene and change its tuning with numbers, on a copy of the Physics Playground.
The goal and what must be true first (a copy of the sample; for the perf tests and the sweep, a source build in
Release). The numbered steps: play the Playground and read the Streaming panel's Physics row (capacity, growth, the
step's time and box3d's share); turn on Count contacts for the detailed statistics; read the whole `physics.stats`
answer; change a field of Project Settings > Physics > Simulation (`ContactRecycleDistance` 0.05 m, `SleepThreshold`
0.08 m/s, `ContactHertz` 30, `ContactDampingRatio` 10, `ContactPushSpeed` 3 m/s; clamped, applied at the next fixed
step) and see the numbers move; run the physics perf tests in Release against their budgets; run
`Tools/PhysicsSweep.py` (distances, knobs, workers, ball pits over many layouts, the Playground) on the settle scenes;
read its report. A table of the instruments and what each counts (`PhysicsStats`, box3d's stage profile and counters,
`IPhysicsDiagnostics`' constant-time step info, the settling instruments, contact storage growth). The result, then the
variations: a ball pit that never sleeps, `ContactHertz` above its ceiling, contact recycling off for a kinematic
platform (the regression exercise), chaotic piles compared over many layouts by their medians, and settings that only
code sets: `PhysicsSettings`' `CollisionSteps` for very fast bodies (clamped to 1 to 64) and the process defaults of
tests and tools (no project setting holds them: `Strata/src/Strata/Physics/PhysicsTypes.h:48`,
`Strata/src/Strata/Physics/PhysicsWorld.cpp:756`). Each why is at most two sentences and links `physics/dynamics` or
`physics/collision-detection`. At the end the reader can change a solver setting and show with numbers what it did.

**Leaves out.**

- What each setting does inside the solver → `physics/dynamics`, `physics/collision-detection`
- The game maker's half: `Physics.Simulation`, `physics.stats`, a pile that never sleeps → `make/physics`
- The perf lab's method: noise, budgets, the reference machine → `engineering/perf-lab`
- Every perf budget → `reference/performance`
- The Streaming panel's drawing → `editor-ui/instrument-panels`
- The picture of Project Settings' Timing page (FixedRate, Interpolation) → `world/projects-settings`

**Fit.** `fits`: about 3,950 words against M (3,000). Seven steps with three pictures take the most, then the
instruments' table and six variations; it stands 50 words under M's top, and the theory stays on the concept pages.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:83` | feature | home | Process-default settings for tests and tools (`PhysicsSystem::SetDefaultSettings`), below the project's section |
| `physics:145-148` | feature | home | `PhysicsSettings`; the `Physics.Simulation` section with its defaults and clamps; contact recycling off for kinematic and presence bodies; the stiffness ceiling |
| `physics:150` | feature | home | The settle scenes, the `physics-settle` helper and `Tools/PhysicsSweep.py` |
| `build-test:225` | feature | home | `Tools/PhysicsSweep.py` as the build inventory lists it: the tool that sweeps physics tuning over the settle scenes and the Physics Playground, run in steps 6 and 7 |
| `physics:167-173` | feature | home | `PhysicsStats`, box3d's profile and counters with the detailed switch, `IPhysicsDiagnostics`, settling instruments, contact growth, the editor's commands and Streaming row, the perf tests |
| `physics:287` | concept | use | Tuning by measurement, as steps: representative scenes, many layouts, medians; the why in two sentences that link `physics/dynamics`, which teaches the concept |
| `physics:374-376` | figure | home | Project Settings' Physics > Simulation page (of `physics:374`, the Simulation page only: the Timing page, FixedRate and Interpolation, is pictured on `world/projects-settings`, where `Scene.Timing` is homed); the Streaming panel's Physics row with Count contacts on; a `physics.stats` answer as a text capture |
| `physics:412` | rule | home | `ContactHertz` above the ceiling does nothing |
| `physics:427` | rule | home | Compare chaotic results over many layouts |
| `physics:463` | hands-on | home | Exercise: a test that bodies fall asleep, with `GetLinearVelocity` and `PhysicsStats::SleepingBodyCount` |
| `physics:470-471` | hands-on | home | Exercises: `Tools/PhysicsSweep.py knobs` for one knob and its report; make `Physics.Settling`'s turning-platform case fail by turning recycling back on for kinematic bodies |
| `physics:540` | term | home | Terms: settle scene, sweep |
| `physics:257` | concept | use | Contact recycling, as the recycle distance changes it |
| `physics:255` | concept | use | Sleep, as the threshold changes it |
| `physics:248` | concept | use | Soft contacts, as the hertz, damping and push speed change them |
| `editor-core:91` | feature | link | The `world.*` and `physics.*` command group |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The measuring method: percentiles, self time, Tracy | `core/profiling` | must |
| What each `Physics.Simulation` field changes in the solver | `physics/dynamics` | must |
| Contact recycling and ghost collisions | `physics/collision-detection` | must |
| One step and where its instruments count | `physics/world-step` | must |
| Settings sections of a project | `world/projects-settings` | must |
| Running a program with arguments in a terminal | `basics/tools` | must |
| A source build in Release, and running tests with CTest | `core/first-change` | must |
| Running an editor command from its line | `start/how-to-read` | helps |
| Opening a copy of a sample | `start/first-game` | helps |
| Perf budgets and the reference machine | `engineering/perf-lab` | helps |
| The Streaming panel | `editor-ui/instrument-panels` | helps |

**Starting state.** A copy of the Physics Playground that the launcher made (Open Sample > Physics Playground), open
in the editor of the pin's build, with no change to its settings. Steps 5 to 7 also need the Release source build of
`core/first-change` (perf tests run in Release and Dist only), its `StrataTests` binary for the sweep, and Python 3.
The page starts from no checkpoint of a tutorial.

**Command-only steps.**

- Reading the whole `physics.stats` answer: no menu or button shows it (the Streaming panel shows a summary, and its
  Count contacts check box runs `physics.setDetailedStats`). Track E reaches this page before `editor/commands`, so the
  step gives the complete line to paste, one sentence on what it does and a link forward to `editor/commands`
  (`critique/rulings-4.md`, R11).

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `settle-scene` | Settle scene | - |

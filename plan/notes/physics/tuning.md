# Notes: physics/tuning

## New terms

None proposed. The settle scene is defined in bold on the page (glossary home: `settle-scene`); "sweep" is explained in the same section but not bolded.

## Requests

- Layouts for the editor figures: `layouts/project-settings-physics.ini` (Project Settings on Physics > Simulation) and `layouts/streaming.ini` (Streaming panel with the Physics section open).
- Figures not taken yet (tier 2 editor screenshots): `simulation-settings`, `streaming-physics`; the text capture `physics-stats-answer` is not filled by a run.
- The patch exercise for a page after `core/first-change` (engine change) is not written; exercise 3 is a trace of MakeBodySetup.

## Since

0.7.0: `Physics.Simulation`, contact recycling, the instruments and the sweep arrive with 0.7.0 (inventory rows `physics:145-150`, `physics:167-173`).

## Not verified

- That the Project Settings window shows the category **Physics** with the page **Simulation** exactly so (taken from the section's Category and Title fields).
- That the default fixed rate is 60 steps per second (the page states the ceiling for 60, 120 and 30 steps per second, computed from the code).
- That a copy of the Playground needs `script.build` before play, and that the Streaming panel shows "Never grew" on a second play (from the guide's text on remembered demand).
- The exact output of `StrataTests --test-suite=Perf.Physics` when run directly (budget messages come from the perf lab).
- The section id `Physics.Simulation` of `project.setSettings` (from the brief and the settings code).

## Findings not applied

- `physics:463` (exercise on `GetLinearVelocity` and `PhysicsStats::SleepingBodyCount`): not written; the page's exercises use the sketch, the knobs sweep and the kinematic regression.
- The summary of Timing page settings (FixedRate) is left to `world/projects-settings`.

## Clerk

- Nothing asked.

## Figures

- `physics-stats-answer` (text): taken and published in round 1 (Physics Playground, 600 paused fixed steps, detailed counting on). The answer shows all five groups the page names: `step` with the library's stages, `sleep` (654 awake, 69 sleeping, 723 moving), `contacts` with `recycledShare` 0.996, `settling` with `maxSpeed`, and `settings` from defaults with `effectiveContactHertz` 29.999998 (the cap at 60 steps per second sits just under 30 in float). Alt rewritten to name the settling group and the effective stiffness.
  Round 2 (viewer: the stages do not add up; 29.999998 against "still says 30"): no retake, the answer is the pin's
  honest output (the text recipe can only keep or redact, not round). In box3d `b3Solve` (solver.c from line 1451)
  times constraints, transforms, refit, bullets (`continuous`), sleep islands and split islands inside the `solve`
  timer (physics_world.c 1143-1146), so only pairs + collide + solve + sensors = 0.521 make up `libraryMs` 0.522; the
  parts sum to `strataMs` 0.3144, and ms 0.8364 = libraryMs + strataMs. Caption now says the stages nest and that
  `effectiveContactHertz` equals `contactHertz` up to float rounding; alt names 29.999998 as 30 up to rounding. The
  page's words would need: after the block, "The library's stages nest (constraints and the others run inside solve),
  so they do not add up to `libraryMs`; the parts are Strata's share, `strataMs`." and "`effectiveContactHertz` reads
  30 up to float rounding (29.999998)"; in The stiffness ceiling, "still says 30 (29.999998, float rounding)".
- `simulation-settings`, `streaming-physics` (editor): wait for tier 2 editor screenshots; not taken at the pin.
- `streaming-physics` (editor, 2026-11-18, round 1 with the provisional build 5b975ad2): good. `layouts/streaming.ini`
  did not exist; the new `layouts/physics-tuning-streaming.ini` (960 x 540, `make-performance-960.ini` with a 400 px
  right column) holds Streaming, pictured with `panel: Streaming` at its own 400 x 462 pixels, the overview stacked
  above Memory. The setup (play, pause, `physics.setDetailedStats`, 300 fixed steps) shows the section open: Bodies
  642 / 2048 (31%), "Never grew · reserves 4.9 MB", "Step 1.11 ms (box3d 0.73) · awake 516 of 615 · recycled 99%",
  Count contacts checked. Caption gained what the values say (most bodies awake, almost all contacts recycled); alt and shows name the lines. The panel's top summary
  line is cut at the right edge (not the subject). `waitsFor` kept. For the writer: the step's Why says the first play
  of a fresh copy grows the world once; this first play of a fresh Playground copy says "Never grew" with 642 bodies in
  2048 slots, so the page's words would need "may grow the world once" or the Why reworded (not verified at the pin).
- `simulation-settings` (editor, 2026-11-18, round 1 with the provisional build): cannot. `layouts/project-settings-physics.ini`
  did not exist; the recipe now uses `layouts/first-game.ini` with `panel: ProjectSettings` and an
  `editor.showPanel` step, so the panel reads at its own pixels (about 800 x 500). The take shows the panel on its
  first page, Game (Start Scene Main, Title Physics Playground), with Simulation only as an entry of the list under
  Physics: no command selects a Project Settings page (`editor.showPanel` has no page parameter; see
  make/input's and make/quality's notes), and the layout keeps no selected page. Recipe, caption and alt left as
  written. What the page gets: nothing until a command selects a page; then the recipe needs that step (page
  `Physics.Simulation`) and, to show "a changed value shows its difference from the default", a
  `project.setSettings` step before it (for example `SleepThreshold` 0). Nearest honest picture meanwhile: none; the
  page's steps already name the five fields in bold.
- `streaming-physics` (editor, 2026-11-18, round 2 with the provisional build 5b975ad2; viewer: the panel's top summary
  line was cut at the right edge, "6 pinned · fra"): the fault stood. A crop would need `::figure{... crop}` in the
  page's text, so the layout changed instead: `layouts/physics-tuning-streaming.ini` now gives Streaming a 500 px right
  column (middle column 296 px; still stacked, the side-by-side form starts at 60 text heights). The retake shows the
  whole line, "58 registered · 56 ready · 0 streaming · 0 failed · 6 pinned · frame 1442", and the Physics section
  unchanged in content: Bodies 642 / 2048 (31%), "Never grew · reserves 4.9 MB", "Step 0.99 ms (box3d 0.63) · awake
  516 of 615 · recycled 99%", Count contacts checked. Alt's step numbers follow this take (0.99 and 0.63); caption and
  shows still hold. `waitsFor` kept.
- 2026-11-23, at the pin v0.8.0 (319075e3), one take, no provisional build:
  - `streaming-physics` (editor): published. `check` named the pin's `editor.screenshot`, so `waitsFor` is gone. The
    panel at its own 500 x 462 pixels shows the whole summary line ("... 6 pinned · frame 1420"), Bodies 642 / 2048
    (31%), "Never grew · reserves 4.9 MB", "Step 0.88 ms (box3d 0.54) · awake 516 of 615 · recycled 99%", Count
    contacts checked. Alt's step numbers follow this take (0.88 and 0.54); caption and shows hold.
  - `physics-stats-answer` (text): retaken and compared with the published answer of 822a7a46: the same five groups
    and the same settings (`effectiveContactHertz` 29.999998, source defaults); only timings and counts moved
    (awake 653 of 723, 70 sleeping, `recycledShare` 0.997). The sums the caption names still hold: pairs + collide +
    solve + sensors = 0.5305 against `libraryMs` 0.5312, the parts sum to `strataMs` 0.2801, and `ms` 0.8113 is
    their sum. Published and filled; caption and alt unchanged.
  - `simulation-settings` (editor): not taken. The pin still has no command that selects a Project Settings page
    (`editor.showPanel` takes no page; only Inspector and Viewport buttons call `ShowProjectSettings` with a page),
    so the panel would open on Game. `waitsFor` now reads "tier 3: the Simulation page of Project Settings; ..." as
    make/input's and make/quality's do. Nearest honest picture: none; the page's steps name the five fields in bold.
- 2026-11-24, finishing the page at the final pin v0.8.0 (319075e3):
  - `simulation-settings` (editor): still cannot be taken (no command selects a Project Settings page; the panel's
    list also has a search field no command fills). `waitsFor` kept as the request for a later edition; its caption
    now follows the pin: the page shows no difference from the default (`GenericSettingsPage` passes no default to the
    widgets), and Contact damping's label has no unit. `standIn`: `simulation-page`.
  - `simulation-page` (diagram, new): the Simulation page as `SettingsBrowser` and `GenericSettingsPage` lay it out:
    the list with its search field and the Physics category (Collision Layers, Timing, Simulation; Scene registers
    before Physics), the heading, the description, the five fields at their defaults, Reset to Defaults (enabled
    only once the section is stored) and the tooltips (field descriptions: range, default, effect). Drawn, rendered in
    both themes, checked. The page places it after the steps with a one-line lead-in.
  - Page words that followed the old caption: the "In the editor" tab said the value shows beside the default; it now
    says the tooltip names the default and Reset to Defaults restores all five. The stiffness ceiling's lead-in said
    the page does not show the limit; Contact stiffness's tooltip does name it, so it now says only the tooltip does.

# Notes: `world/projects-settings`

## New terms

None proposed. The page defines the glossary's six entries homed here in bold: project scope, user scope, settings
section, simple section, complex section and hand-over. It marks (through markterms) the terms of the closure only.

## Requests

- Figures: `src/content/figures/world/projects-settings.json` asks for two editor pictures, `timing-page` (Project
  Settings, Physics page for Timing) and `inspector-project-rate` (Inspector with nothing selected after
  `project.setSettings` sets `Scene.Timing` to FixedRate "120"). Both carry `waitsFor: "tier 2: editor screenshot"`. The
  first has empty steps, because no command opens that page of the window; the second sets the rate with the command and
  needs the scene's selection cleared, which no step does yet. The planner should fill the steps. The settings flow is a
  Mermaid diagram and the project on disk a `:::files` tree, so they have no figure entry.
- The page writes the invented section ids of its examples (Game.Tuning, Game.Audio, Fan.Bonus) as plain text in prose and
  inside fences only, because the `names` check refuses a code span with a dotted name that is no section at the pin.
  A reader of the plain text would prefer code spans; if the planner wants them, `names` needs a way to mark a name as
  the reader's own.
- No new hosts and no new words: the Further reading entries are cited without links.

## Since

`since: 0.3.0`: `Project` and `.stproj` are 0.3.0 in `plan/inventory/scene-ecs.md` (row 212). The settings sections
(0.6.0), the version 3 file (0.6.0) and `Scene.Timing` (wave 8, 0.8.0) are newer, but the page's subject, the project and
its settings, is as old as the first tag.

## Not verified

- The look of the Project Settings page for Physics > Timing (Interpolation drawn as a switch or a box, the choice drawn as
  a list): the page says only "the two fields with their descriptions"; no editor was run. The same holds for the picture
  claims of both figures.
- That the editor's project creation writes the `Scripts/` folder: read as `CreateScriptProjectFiles` in
  `EditorContext::CreateProject`, not run. The folders `.strata/Scripts/Build` and `Bin` come from `Project.h` getters;
  `.strata/Saves` from `EditorContext.cpp` line 1647.
- The layout of an exported game's folder: the brief asks for it beside the project's tree, but it is taught by
  `assets/packs-export` and was not read, so the tree shows the project only.
- Statements about Godot, Unreal Engine and Unity (one text file; layered `.ini` files; asset files in `ProjectSettings`):
  from general knowledge of their public documentation, not fetched. The alternatives table repeats them.
- The statement that a project made on Linux must open on Windows is the reason the code's comment gives for the rule
  ("a valid file name on every platform"), phrased by the page.
- The history block (collision layers in every scene document before 0.6.0) follows comments in `Project.h` and `Scene.h`
  and the 0.6.0 date of `plan/inventory/scene-ecs.md`, not the release notes.
- That the first of the two `ApplyProjectTiming` calls in `Strata/src/Strata/Scene/Prefab.cpp` is in
  `SceneAsset::TakePreparedScene`: the function name follows the comment of `Scene::ApplyProjectLayers` in `Scene.h`; the
  second is `SceneAsset::CreateScene`.
- No test was run. The suites and the doctest filters (`--test-suite=Project*`, `Core.Settings`), the exercises' pseudocode
  (`MakeIntField` is a helper the reader writes) and the outputs of exercise 1 (the sketch's, real) follow the code, not
  an engine run.
- The trace of exercise 4 was read in the code (`EditorProjectSettingsCommands.cpp`, `ProjectSettingsAction.cpp`,
  `EditorContext.cpp`, `Scene.cpp`, `ProjectSceneTiming.cpp`), not followed in a debugger.

## Findings not applied

- The brief names no open findings. Its erratum `new:10` is applied: the page says that the comment of
  `RegisterSceneModule` names only the collision layers while `SceneRegistration.cpp` registers `Scene.Timing` too.
- The brief's exercise "a complex section that keeps a refused value verbatim" is exercise 3 as a prediction with the
  test `A section that fails Read keeps its stored value and reports it` named, not as code: the toy sketch and exercise 1
  carry the "done" exercise (the accumulator sketch).
- Item `scene-ecs:483` (the Inspector with nothing selected) is a figure plus a paragraph; its rows at a FixedRate of 120
  read "120 steps/s (project)", "Fixed rate: the project's, 120 steps/s" and the reason on the step rows
  (`InspectorPanel.cpp` lines 258 to 284).
- `scene-ecs:214-216` and `221` (export settings, the game's information, the manifest, the collision layers) are only
  named, with links in "Where it lives in Strata", as the brief's roles say.
- The brief's fit estimate was 4,550 words; the page has 6,412 prose words, inside L (4,001 to 6,500) but near its end,
  because of seven quotes with callouts.
- `:since[0.8.0]` is not placed on the `Scene.Timing` section: the brief does not ask for it.

## Clerk

- Left for the planner: the figures' steps; a way for `names` to mark a section id as the reader's own.

## Figures

Editor figures, taken with the provisional build (engine 5b975ad2831e, 2026-11-18, `--provisional`); nothing published,
`waitsFor: tier 2: editor screenshot` kept on both recipes.

- inspector-project-rate: round 1 good. The recipe now sets `Scene.Timing` to FixedRate "120", clears the selection
  and pictures the Inspector panel at its own pixels (`layouts/make-lighting-short.ini`, 960 x 440, a 380 px Inspector
  column; the writer's `first-game.ini` has a 256 px column that cuts the lines). The picture shows the Outpost scene's
  settings: the Physics header ends with "Gravity 9.81 m/s² · 120 steps/s (project)" and the line "Fixed rate: the
  project's, 120 steps/s" stands beside its Project Settings link. The scene's sections start closed and no command
  opens one, so the step rows with their reason (the page's last clause before the figure) are not in the picture;
  shows and alt now name only what is seen, and the caption stays true. The lower third of the panel is empty.
- inspector-project-rate, round 2 (a viewer's fault: the paragraph names the step rows, the picture has Physics
  closed, the caption did not say where the two marks are): the caption now says the step rows stay inside the closed
  Physics section and points to the header's "120 steps/s (project)" and the "Fixed rate" line below it. Not retaken:
  only words changed, and the provisional build still has no command that opens an Inspector section
  (`InspectorPanel.cpp` draws the scene's sections closed; `editor.showPanel` takes no section). What the page's words
  need (left to the writer, the page is not ours): paragraph 584 should say that the step rows with their reason show
  inside the Physics section once it is opened, not in the picture.
- timing-page: cannot. The Project Settings panel opens on its first page, Game, and no command selects another
  (`editor.showPanel` takes `scripts` and `search`, the latter for the Hierarchy only; the editor opens the Timing page
  only from the Inspector's Fixed rate link, a click). Not taken; the recipe is left as written. What the page needs: a
  `page` (section) parameter of `editor.showPanel` for Project Settings, `Scene.Timing` here. Until then the page gets
  no picture; the nearest honest one is the Inspector figure above, whose link names the page.

At the pin v0.8.0 (319075e3, 2026-11-24, Release build, no `--provisional`):

- inspector-project-rate: published, round 1. Taken once with the settled recipe; the picture matches the provisional
  take: the Outpost scene's Inspector, Physics closed with "Gravity 9.81 m/s² · 120 steps/s (project)" at its header's
  end, "Collision layers: 3 named", then "Fixed rate: the project's, 120 steps/s" beside its Project Settings link.
  Caption, alt and shows are true of it; recipe unchanged. The panel's lower third is empty (a shorter window needs a
  layout of its own; left as is). The paragraph's clause about the dimmed step rows is still not in the picture.
- timing-page: blocked, not taken. The pin's `editor.showPanel` takes `ProjectSettings` but still no page: the panel
  opens on Game, and `ProjectSettingsPanel::Select` is reached only from clicks (`EditorLayer::ShowProjectSettings`
  called by the Inspector's and Viewport's links and the Export dialog) and is not remembered across windows. Needs the
  same engine addition as above (a page parameter); the nearest honest picture remains inspector-project-rate.
- inspector-project-rate, viewer's fault at the pin (2026-11-24): the paragraph before the figure calls "Fixed rate:
  the project's, 120 steps/s" a link; in the picture that text is a plain label and the link beside it reads
  "Project Settings". Picture, caption, alt and shows are right (the alt already says "beside a Project Settings
  link"); not retaken. The fault is the page's words (not ours): paragraph 584 should read 'a line reads "Fixed rate:
  the project's, 120 steps/s" beside a Project Settings link'.

Last pass at the final pin v0.8.0 (319075e3, 2026-11-24):

- timing-page: still no take. The picture tool's new fields (renderer, files, launcher, automation, runtime, live)
  give no way to select a Project Settings page, and the pin's `editor.showPanel` has no page parameter. The entry is
  now `blocked` (its reason is the request for a later edition: a page parameter for `ProjectSettings`) with
  `standIn: timing-page-drawing`; its caption and alt are cut to one line each, to keep the page within size L.
- timing-page-drawing (new, diagram): the Timing page as the pin draws it, read from
  `StrataEditor/src/UI/SettingsPages.cpp` (`SettingsBrowser::DrawPage`, `GenericSettingsPage::Draw`): the pages listed
  by category, Timing selected under Physics, the section's description, Fixed Rate as a list showing Scene, the
  Interpolation check box, Reset to Defaults dimmed (enabled only when the project stores the section), and the start
  of the Fixed Rate description as its label's tooltip. Rendered and looked at in both themes; `drawings check` passes.
- The page's words now follow the pin: the old sentence "The page lists the two fields with their descriptions" was
  wrong, because a field's description shows only as the tooltip of its name; the page shows the section's description.
  The lead-in now says the window opens on Game and introduces the drawing. The clause "beside the collision layers and
  the simulation" went, since the drawing shows it; the page holds 6,499 prose words (L ends at 6,500).

## Walk E-final-9

Track walk E-final-9 (2026-11-24; `docs-work/walkfix-E9`). The project file listing now follows
`Project::MakeFileText` (`Strata/src/Strata/Project/Project.cpp:387-417`): nlohmann's object sorts its keys and
`JsonUtils::Dump(document, 1, '\t')` puts a tab before each level, so `Project`, `Settings` and the header `Strata` come
in that order, and each section stores `Value` before `Version`. Checked against what the 0.8.0 editor wrote for a copy
of `OpenWorld` after `project.setSettings` and `project.save`. `scene.info` in that session gave `settings.fixedRate`
with `source` `project`, `stepsPerSecond` 120 and `maxFixedSteps` 16, which the page now names for a reader without a
window.

The Medium exercise has a worked solution, `tutorials/world/projects-settings/exercise-2.patch`: a new test file
`StrataTests/src/Core/GameTuningTests.cpp` in suite `Core.Settings` with the helper `MakeIntField`. In
`build/docs-patch` (Release) it built warning-free and `--test-suite=Core.Settings --test-case=Game.Tuning*` passed
(1 test case, 12 assertions; the suite 8 test cases); `tutorials.py patch` stamps it. The page has no tutorial file, so
the runner names only its default suites (`Architecture.Layering` and the feature test) in the stamp. `time` went to
100 (the reading floor), and the page was shortened by six sentences to stay inside size L.

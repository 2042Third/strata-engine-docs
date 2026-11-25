# Notes: `world/reflection`

## New terms

None proposed. The page defines the glossary's eight entries homed here in bold: reflection (its alias `PropertyInfo` is
described in code spans, not defined a second time), property, `ComponentInfo`, component flags, requirement, extra data,
canonical JSON and inactive reason. It marks (through markterms) type erasure's neighbours of the closure only.

## Requests

- `tools/data/external-hosts.txt`: `dev.epicgames.com` (Unreal Engine documentation on properties and the Unreal Header
  Tool), `doc.qt.io` (Qt's meta-object compiler) and `www.rttr.org` (the RTTR library). All three are cited in Further
  reading without a link.
- `tools/data/names.txt`: "Qt" and "RTTR". The page writes both as code spans in prose and in the alternatives table, so
  no word-list finding is left; a reader of the plain text would prefer the names without code marks.
- Figures: `src/content/figures/world/reflection.json` asks for two editor pictures, `directional-light-sections` (the
  Showcase sun in the Inspector, headings Light and Shadows) and `add-component-menu` (the open Add Component menu). Both
  carry `waitsFor: "tier 2: editor screenshot"` and empty `steps`, because selecting the sun needs its entity name in the
  Showcase scene (not read) and opening the menu has no command. The planner should fill the steps. The reflection model
  is a Mermaid diagram on the page, so it has no figure entry.

## Since

`since: 0.3.0`: `PropertyType`, `PropertyValue`, `PropertyInfo`, `ComponentInfo`, `ComponentRegistry`, canonical JSON and
`ComponentAccess` are 0.3.0 in `plan/inventory/scene-ecs.md` (rows 189 to 206). Sections (0.7.0) and the append
functions (0.4.0) are newer, but the page's subject is as old as the first tag.

## Not verified

- RTTR's expansion "Run Time Type Reflection", and the statements about Unreal Engine (UHT reads `UPROPERTY` macros and
  writes code), Qt (the meta-object compiler) and EnTT's `meta` (run-time registration in C++): from general knowledge of
  the projects' public documentation, not fetched here. The GitHub address in Further reading (the EnTT repository's front
  page) was not fetched either.
- The row "Language reflection ... proposed for a later C++ standard": general knowledge, stated without a version.
- "Hand-written code per consumer: projects with a handful of components" is an observation, not a claim about a named
  project.
- That the Add Component menu hover shows `Description` as a tooltip and that the groups sort by name: read in
  `StrataEditor/src/Panels/InspectorPanel.cpp` (a `std::map` keyed by category), not run.
- That `component.list` shows the descriptions of `DescribeProperty`: `EntityCommands.cpp` pushes `DescribeProperty`
  into the list it returns near the `category` field; the command was not run.
- Exercise 1's run of `component.set` and the file edit were read in the code (`CommandUtils.cpp` `ApplyComponents`,
  `Property.cpp` `SetValue`, the `Properties read and write component members with validation` test, which clamps 500 to
  179), not run in an editor. The exact error text is built from `PropertyInfo::IsInRange` and `ApplyComponents`.
- The doctest filter `--test-suite=Reflection*` and `ctest --preset windows-debug` were not run.
- The picture claims of the two editor figures (headings, menu groups) follow the code, not a screenshot.
- The 42 registrations of "the engine's module sources" is a count of lines with `ComponentRegistry::Register<` under
  `Strata/src` (8 in Scene, 9 in Renderer, 11 in GameUI, 6 in Physics, 3 in Animation, 2 in Audio, 2 in World, 1 in
  Scripting); the page says "close to 42" and uses 40 as a round number in its example.

## Findings not applied

- The brief names no open findings.
- `scene-ecs:392` says `Register<T>` fills about 15 lambdas at lines 382 to 476. At the pin it sets eleven operations
  (`Has`, `Get`, `Add`, `Remove`, `MarkModified`, `Copy`, `AssureStorage`, `CopyStorage`, `CreateValueArray`,
  `EmplaceCopy`, `Observe`) at lines 383 to 475; builder calls set the rest of the "about twenty". The page says eleven.
- `scene-ecs:393` gives `PropertyBuilder.h` 17 to 65: the type deduction is lines 17 to 40 and `Property` is lines 57 to
  65, quoted separately.
- The brief's item `new:20` names `EntityCommands.cpp:721` and `CommandUtils.cpp:580-587`; at the pin the check of the
  range is in `ApplyComponents` (`CommandUtils.cpp`, the loop over properties), and the exercise names the function and
  files, not the lines.
- The toy (`sketches/world-reflection-toy.cpp`) has 80 lines, the upper end of the card's 30 to 80.
- Hazel's style (the brief's third registration example) is not described: nothing at the pin or in the sources named
  by the brief says how Hazel registers components, so the table names RTTR and EnTT's `meta` only.
- The page has no "What went wrong before" section: the brief names no bug with a regression test for this subject.
- No `tutorials/world/reflection/exercise-<n>.patch`: the card allows the patch form only after `core/first-change`;
  exercise 3 is a standalone sketch.
- Exercise 1 touches a scene file by hand because the brief asks for it; the page says game makers use commands for this.
- The page is about 7,400 prose words, below the brief's fit of 8,000 words for XL and inside the range; the six excerpts
  are eight (the registry template in two parts, the deduction, the builder's `Property`, the camera, `SetValue` in two
  parts, `Deserialize`, `SetProperty`, `AddWithRequirements`, the Scene module's registration) and the figures are one
  Mermaid diagram and two editor pictures.

## Clerk

- `names.txt`: Qt, RTTR. `external-hosts.txt`: `doc.qt.io`, `www.rttr.org` (front pages fetched: Qt Documentation, RTTR). Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm).
- Left for the planner: the steps of the two editor figures.

## Figures

- `directional-light-sections`, round 1 (provisional build 5b975ad2, not published): the recipe opens the Showcase,
  finds the entity `Sun` (`entity.find`), selects it and pictures the Inspector panel in `layouts/first-game-tall.ini`
  (1280 × 800, Inspector column 380 px). The picture shows the whole Directional Light component: a heading Light over
  Color, Intensity and Angular Diameter, a heading Shadows over Cast Shadows, Shadow Distance, Shadow Bias, Shadow Normal
  Bias, Cascade Blend, Contact Shadow Length and Cascade Distribution, then the Add Component button. Caption, alt and
  shows now name only what is drawn; the old caption's "with no drawing code for this one component" was dropped, because
  the picture also shows the line "Shadow maps: 5 x 4096 (Graphics Quality: High)" and a Graphics Quality link under the
  Shadows section, which `StrataEditor/src/Panels/InspectorPanel.cpp` draws for the directional light alone
  (`Inspector.DirectionalLight.ShadowQuality`). The page's sentence "the Inspector needs no code for the light" is
  contradicted by that line: the writer should say the property rows and headings need no code, and the shadow-map line
  is the one addition the Inspector makes for this component. `waitsFor` stays until the pin moves.
- `directional-light-sections`, round 2 (words only, no retake): a viewer reported the same contradiction. No recipe can
  hide the line: `InspectorPanel::DrawComponent` calls `DrawSunShadowQuality` for every Directional Light component, and
  that draws a line in every case (with Cast Shadows off it reads "No shadow maps: Cast Shadows is off"). Caption, alt
  and shows now name the line and the Graphics Quality link and call them the Inspector's own code for the light; the
  recipe and the round 1 picture stand. Still for the writer: page line 524 should read that the headings and fields
  come from the registration with no code, and that the shadow-map line below them is the Inspector's own addition for
  the sun.
- `add-component-menu`, not taken: the Add Component menu is a pop-up, and no command opens menus or pop-ups, nor shows
  a hover tooltip (the caption's second claim). The recipe is left as it was (empty steps, `waitsFor`). What the page can
  get instead: a table of the addable components by category from `component.list` (pin dump), which states the paragraph
  exactly: Animation (Skin, Animator, Attach To Joint), Audio (Audio Source, Audio Listener), Core (Name, Transform, Tag),
  Lighting (Directional Light, Point Light, Spot Light, Sky Light), Physics (Rigid Body, four colliders, Character
  Controller), Rendering (Camera, Mesh Renderer, Height Fog, Reflection Probe, Post Process), Scripting (Script), UI (12,
  Text to UI Mask) and World (World, Streaming Source); no addable component of the pin falls under "General". The
  nearest picture commands can take is the Inspector's Add Component button below a component (the bottom of
  `directional-light-sections` already shows it), which teaches nothing about the groups; a table is the honest choice.
- `directional-light-sections`, round 3 (pin v0.8.0, 319075e3, published): `waitsFor` removed as `check` asked; one
  take with the unchanged recipe. The picture matches round 1 and the caption, alt and shows: headings Light (Color,
  Intensity 120000, Angular Diameter 0.53) and Shadows (seven fields, Cast Shadows to Cascade Distribution), the line
  "Shadow maps: 5 x 4096 (Graphics Quality: High)" and the Graphics Quality link. Page line 524 now agrees with it.
- `add-component-menu`, at v0.8.0: still blocked; the pin has no command that opens a pop-up menu. Its `waitsFor` now
  names that (tier 3) instead of the editor screenshot the pin already has; steps and words unchanged. The category
  table proposed above was read from the 822a7a46 dump: check it against the 319075e3 dump before using it.
- `add-component-menu`, final pin (v0.8.0, 319075e3): no take can open the pop-up, and the pin is the edition's last, so
  the entry keeps its `waitsFor` as the request for a later edition and names the stand-in `add-component-groups`. That
  drawing sets out the groups the menu draws for every addable component, from the 319075e3 dump of `component.list`
  (registration order) and `InspectorPanel::DrawAddComponentPopup` (a `std::map` by category, "General" for none, the
  description as a hover tooltip, components every selected entity has omitted): Animation (3), Audio (2), Core (3),
  Lighting (6, now with Rect Light and Light Surface), Physics (6), Rendering (5), Scripting (1), UI (12) and World (2);
  Prefab Instance is not addable. Three columns where the menu has one scrolling list, Lighting marked with its
  `.Category("Lighting")` call. The page now places the drawing after the paragraph on the menu, whose last sentence
  introduces it.

## Track walk E-final-8

WK2: the Basic exercise now gives its steps: a copy of the Third-Person Adventure sample from the launcher, the four
`StrataCLI` lines in OS tabs (PowerShell pipes the parameters in), the camera's id and the edit of the copy's
`Assets/Scenes/Course.stscene`. Run with the official 0.8.0 package in Windows PowerShell 5.1, headless, under the perf
lock (`docs-work/walkfix-E-final-8`, `hold.ps1`, `out/run.txt`, 2026-11-24): `entity.find` answers
`350D7DDD7ED21DD5`; `component.set` with 200 exits 1 with the message `Camera.PerspectiveFOV must be between 1 and 179,
not 200` on standard error; `component.get` reads 60; the inline JSON argument fails with "params must be a JSON object
or array". After the file was changed while the editor ran, `scene.open` of the open scene read it again and
`component.get` read 179; a new editor on the same file read 179 too. `log.read` from Warn holds no camera warning, only
the sample's own (scripts not built, RobotExpressive's morph targets). The windowed editor was not run; the pin has no
prompt for a scene changed on disk.

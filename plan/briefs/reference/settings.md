# Brief: `reference/settings`

| Field | Value |
| --- | --- |
| Title | Project settings and preferences |
| Kind | R |
| Size | L |
| Tracks | - |
| Needs | `world/projects-settings` |
| From | the settings sections (`project.settings` on an empty project, `preferences.get`, the schemas' defaults); scene-ecs, render-image |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/settings` — Project settings and preferences

**Covers.** The paragraph on top says what the page is: every settings section a project or the editor's preferences
can hold, with every field and its default, generated at the pin from `project.settings` on a new `empty` project and
from `preferences.get`, using each field's `default` and never its `value`, so nothing of the machine that made the
dump leaks in. It says how to read a section: its id `<Module>.<Name>`; its scope (Project: stored in the `.stproj`
file and shipped with the game; User: the person's preferences, never shipped); its title and category as the
settings windows show them; its version; for a simple section one row per field (name, title, `SettingsField` type,
default, range or options, description); for a complex section its JSON Schema in a closed block and its default
value. The generated part has two tables. Project sections, in the order `project.settings` returns them: `Input.Actions` (the action
maps and the reserved UI map), `Physics.Simulation`, `Renderer.Quality` (the preset and the Custom values),
`Scene.CollisionLayers` (32 named layers and the matrix) and `Scene.Timing`. Preference sections:
`Editor.ExternalEditor`, `Editor.FrameRate` and `Editor.Interface`. Hand-written: one sentence per section naming its
home page and the editor's settings page that edits it; a note that the four preset values of each quality row stand
in `reference/renderer`'s quality table, so this page shows only the section's fields; a note on the commands that
change a section (`project.setSettings`, `project.setCollisionLayers`, `inputActions.*`, `preferences.set`); and
`## Where it lives in Strata`: `SettingsRegistry.h`, each section's registering file, `EditorPreferences.cpp` and the
settings windows. The tool is `tools/reference.py dump`, routes "settings" and "preferences". A reader with a section
id from a `.stproj` file finds every field, its default and the page that explains it.

**Leaves out.**

- What a settings section is, its validation, versions and the hand-over to scenes → `world/projects-settings`
- How the settings windows are drawn from schemas → `editor-ui/settings-windows`
- The quality rows with their four presets and what each costs → `reference/renderer`
- The `SettingsField` types and the 512 KiB cap, as types and limits → `reference/scene`
- The project file's other keys (game info, export settings) and the manifest → `reference/worlds-runtime`
- Changing settings in the editor, for game makers → `make/project-files`

**Fit.** `fits`: about 1,600 words against L (5,000). The generated tables give the page its size: eight sections with
their fields and defaults, two schemas and the default action maps, roughly 3,500 words. The prose is the paragraph on
top, eight section sentences, three notes and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:218-220` | feature | use | `SettingsSection`, `SettingsField`, scopes, versions, the registry and `IProjectSettings`, in the paragraph on how to read a section |
| `scene-ecs:221-223` | feature | link | `Scene.CollisionLayers`, `Scene.Timing` and the list of the other sections |
| `physics:123` | feature | link | `Scene.CollisionLayers` from the physics side |
| `physics:146` | feature | link | `Physics.Simulation` and its fields |
| `physics:158` | feature | link | `Scene.Timing` from the physics side |
| `audio-input:153` | feature | link | `Input.Actions` |
| `render-image:234` | feature | link | `Renderer.Quality` |
| `editor-ui:118` | feature | link | Idle throttling, which `Editor.FrameRate` sets |
| `editor-ui:226-232` | feature | link | The settings browser, the generic page, the custom pages that edit the sections, and the Preferences dialog |
| `editor-core:95` | feature | link | `preferences.get`, `set` and `save` |
| `gamedev:61` | feature | link | Preferences as a game maker meets them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections | `world/projects-settings` | must |
| JSON values and objects | `basics/data-formats` | must |
| Settings windows from schemas | `editor-ui/settings-windows` | helps |
| Collision layers | `physics/collision-layers` | helps |
| Input actions and maps | `input/actions` | helps |
| Quality rows and presets | `image/quality-settings` | helps |
| The fixed rate | `core/time` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-1 | must | missing-item | new item on `reference/worlds-runtime`; the Leaves out of `reference/settings` | No page of the unit lists the keys of the project file `.stproj`. `reference/settings` sends "the project file's other keys (game info, export settings)" to `reference/worlds-runtime`, whose eight tables do not hold them, and `reference/scene` gives the file one row (format v3), so the link leads to a table that does not exist. | `reference/worlds-runtime` adds a hand-checked table of the project file, checked against `Project.cpp`: the header (Format "Project", Version 3; versions 1 and 2 still read and migrated); `Project` with `Name`, `AssetDirectory`, `StartScene`, `Scripts` (`SourceDirectory`, `ModuleName`), `Export` (`AlwaysInclude`, `LoadingScene`) and `Game` (`Title`, `Version`, `Company`, `Copyright`, `Icon`); `Settings`, whose sections are `reference/settings`'; unknown members kept; the 1 MiB cap. Its introduction names `world/projects-settings`. The row `scene-ecs:214-216` widens its take to this table, and `reference/scene`'s row links it. About 150 words. | `allocation/reference.md:277`, `:788-801`, `:326-328`, `:840`; `allocation/world.md:848-853`; `Strata/src/Strata/Project/Project.cpp:22-23`, `:229-310`, `:388-415`; `Strata/src/Strata/Project/Project.h:71-73`, `:101-103` |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-20 | could | duplicate | `reference/settings`; `reference/audio-input`, table (7) | The default value of the `Input.Actions` section is exactly the reserved `UI` map, so the two pages generate the same map with its default bindings twice. R44 (the row of reference-q4) keeps each generated fact in one table. | `reference/settings` shows the section's schema and, for its default, links `reference/audio-input`'s table (7), as it already does for the quality presets. No words added. | `allocation/reference.md:260-262`, `:264-265`, `:686`; `critique/rulings-10.md:15`; `Strata/src/Strata/Input/InputActionSet.cpp:503-507`, `:633` |

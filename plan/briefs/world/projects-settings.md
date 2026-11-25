# Brief: `world/projects-settings`

| Field | Value |
| --- | --- |
| Title | Projects and settings |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/systems`, `world/reflection`, `core/files` |
| From | scene-ecs; settings sections, their versions and validation, `IProjectSettings`, the hand-over to scenes (timing, collision layers); the manifest and the game's identity are `worlds/game-identity`'s; `make/project-files` teaches the project folder to game makers |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/projects-settings` — Projects and settings

**Covers.** The job: what a project is to the engine (the `.stproj` file, its folders and the `.strata/` intermediate
folder), and how settings are registered, stored, validated and handed to scenes. The manifest and the game's identity
are `worlds/game-identity`'s; the project folder for game makers is `make/project-files`'. The problem in one paragraph
(settings as code against settings as registered data; project scope against user scope). Then, in this order:

1. The project file: format 3; the layout (the asset folder, scripts, `.strata/` with `Cache`, `Scripts/Build` and
   `Scripts/Bin`) drawn as a tree; `Create`, with the rule of `Project::IsValidName` beside it (the name becomes the
   project file's name, so it is a valid file name on every platform, and `project.create` refuses other names; about 40
   words); `Load` with its 1 MiB cap, the header and version checks, the sections
   validated against a registry and unknown members kept; the script settings and the module name rule; the active
   project, and `ProjectModule`, which releases it and the asset manager at shutdown.
2. Settings sections: simple sections described by fields (Bool, Int, Float, String, Enum, Asset) and complex sections
   with a schema, a default, a read function and references; the scopes Project and User; versioned values with
   upgrades; one `Validate`; a cap of 512 KiB per value; the process registry, frozen with the components, its id rule
   `<Module>.<Name>`, and local registries for tests.
3. A complete simple section: `Scene.Timing` (`FixedRate` Scene, 30, 60, 120 or 240; `Interpolation`; at most
   `ceil(rate × 2 / 15)` steps per frame), with its description for agents and its `Find` cached by the provider's
   version, and the Project Settings page its fields make (Physics > Timing). The Scene module registers two
   sections, `Scene.CollisionLayers` and `Scene.Timing`, although the comment in `SceneRegistration.h` names one;
   Scene owns them, not Physics, because the layers' type, their parser and every reader of their names are Scene's,
   and the step drives scripts and animation as well as physics, so a build or a game without physics keeps both
   (about 40 words); the other sections are named with the pages that teach them, and the full list is
   `reference/settings`'.
4. `IProjectSettings` and `ProjectSettingsValues`: sections no module claims, and invalid ones, kept verbatim; only
   validated values provided; a version unique in the process; stored entries for undo.
5. The hand-over: scenes built on workers never read the service; the main thread applies the project's values when a
   scene is handed over and after every change; the Inspector with nothing selected shows the scene's fixed step overruled
   by the project.

Then the tests (`Project`, `Project.Settings`, `Core.Settings`), changing it safely, and the exercises: a simple section
`Game.Tuning` with an upgrade to version 2, in a local registry; a complex section that keeps a refused value verbatim;
and the "trace it yourself" exercise, `Scene.Timing`'s `FixedRate` set to 120 with `project.setSettings` while a game
plays, followed to the moment the running scene's `GetFixedTimestep` changes.
At the end the reader can add a settings section and read it correctly from a system.

**Leaves out.**

- The project folder for game makers → `make/project-files`
- The manifest and the game's identity → `worlds/game-identity`
- Export settings and `AlwaysInclude` → `assets/packs-export`
- The collision layers section and the scene's working copy → `physics/collision-layers`
- Settings windows drawn from fields; the Preferences dialog → `editor-ui/settings-windows`
- Creating, opening and migrating projects; undoable project changes → `editor/projects`
- Every section and its fields → `reference/settings`
- Building the script module the project names → `editor/script-builds`

**Fit.** `fits`: about 4,550 words against L (5,000). Three excerpts, four figures and three exercises take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:212-213` | feature | home | `Project`: the file, the layout, `Create`, `Load`, `Save`, the cap, unknown members kept, the active project; the script settings and the module name rule |
| `new:25` | feature | home | `Project::IsValidName`, beside `Create` in section 1: the name becomes the project file's name, so it must be a valid file name on every platform: at most 128 bytes, none of the nine characters Windows forbids in file names (angle brackets, colon, double quote, both slashes, vertical bar, question mark, asterisk) or control characters, no space at either end, no trailing dot, no reserved device name such as CON; `Create` refuses other names, and so `project.create` does (about 40 words). Evidence: `Strata/src/Strata/Project/Project.h:83-86`; `Strata/src/Strata/Project/Project.cpp:153-165`, `:178-179`; `StrataEditor/src/Editor/EditorContext.cpp:258` |
| `scene-ecs:217-220` | feature | home | `ProjectModule`; settings sections; `SettingsRegistry`; `IProjectSettings` and `ProjectSettingsValues` |
| `scene-ecs:222-224` | feature | home | `Scene.Timing`, and why Scene, not Physics, owns it and `Scene.CollisionLayers`: a build or a game without physics keeps both (`SceneRegistration.cpp:17-22`); the other sections and where they are taught; the hand-over to scenes |
| `physics:158` | feature | home | `Scene.Timing` as the physics survey lists it: the same section as `scene-ecs:222`, taught once in section 3 |
| `foundation:131` | feature | home | `SettingsRegistry` and `ProjectSettings` as the foundation survey lists them: the same as `scene-ecs:219-220`, taught once in sections 2 and 4 |
| `scene-ecs:214-216` | feature | link | Export settings, the game's information and the manifest, taught in `assets/packs-export` and `worlds/game-identity` |
| `scene-ecs:221` | feature | link | `Scene.CollisionLayers`, the example of a complex section, taught in `physics/collision-layers` |
| `scene-ecs:362` | concept | home | Projects and settings: scopes, sections as registrations, versions and upgrades, unknown data kept, the hand-over, settings carried into exported games |
| `scene-ecs:404` | code | home | `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:45-123`: a complete simple section: fields, default, description for agents, `Find` cached by the provider's version |
| `scene-ecs:405` | code | home | `Strata/src/Strata/Core/SettingsRegistry.h:45-103`: the section model, simple against complex |
| `scene-ecs:407` | code | home | `Strata/src/Strata/Project/Project.cpp:208-324`: `Project::Load`: size cap, header, versions, unknown members kept, sections validated |
| `scene-ecs:464`, `scene-ecs:466`, `scene-ecs:483` | figure | home | The project on disk as a tree, with the exported folder beside it; the settings flow from registration to the scenes; the Inspector with nothing selected, its fixed step rows marked "(project)" at a `FixedRate` of 120 |
| `new:26` | figure | home | Project Settings' Physics > Timing page: Fixed Rate (Scene, 30, 60, 120 or 240) and Interpolation with their descriptions, the page that `Scene.Timing`'s fields make, beside section 3 (critic-physics-18: the Timing page's picture comes here from `physics:374`, whose Simulation page stays on `physics/tuning`). Evidence: `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:44-88`; `Strata/src/Strata/Scene/ProjectSceneTiming.h:25` |
| `scene-ecs:561` | rule | home | Read `IProjectSettings` on the main thread only and cache by version; validate only through `Validate`; never assert on a settings value |
| `scene-ecs:559` | rule | use | Keep unknown data: unclaimed sections and unknown project members are written back as read |
| `scene-ecs:587`, `scene-ecs:588` | hands-on | home | The `Game.Tuning` section with an upgrade; a complex section that keeps a refused value |
| `new:27` | hands-on | home | The "trace it yourself" exercise (D27): `Scene.Timing`'s `FixedRate` set to 120 with `project.setSettings` while a game plays, followed from the command through the project settings step, which applies the change to the edited and the running scene, to `Scene::ApplyProjectTiming`, which reads `ProjectSceneTiming::Find` (cached by the provider's version) and takes the new rate on the main thread (about 250 words). Evidence: `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp:259`; `StrataEditor/src/Editor/ProjectSettingsAction.cpp:76-78`; `StrataEditor/src/Editor/EditorContext.cpp:552-561`; `Strata/src/Strata/Scene/Scene.cpp:229-242`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:90-97` |
| `scene-ecs:685-690` | term | home | Project, intermediate directory, settings section, simple and complex section, project and user scope, hand-over |
| `render-image:733` | term | home | The image survey's entry for a settings section, with `Renderer.Quality` as its example: one glossary entry with this page's |
| `new:10` | erratum | home | The comment of `RegisterSceneModule` names one settings section, the collision layers; the code also registers `Scene.Timing`. The page names both. Evidence: `Strata/src/Strata/Scene/SceneRegistration.h:6-8`; `Strata/src/Strata/Scene/SceneRegistration.cpp:22` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON documents, and versions of a format | `basics/data-formats` | must |
| UTF-8 paths, atomic writes and files capped in size | `core/files` | must |
| Engine services and engine modules | `core/engine-modules` | must |
| Registries that open and accept, the settings registry that then freezes | `core/layers-registries` | must |
| Validation, ranges and leniency | `world/reflection` | must |
| `SceneSettings`, `GetFixedTimestep` and the runtime frame | `world/systems` | must |
| The fixed rate and interpolation as ideas | `core/time` | must |
| Scene assets handed over on the main thread | `world/sub-scenes` | helps |
| Asset handles | `assets/handles-meta` | helps |
| Undo steps | `editor/undo` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `complex-section` | complex section | - |
| `hand-over` | Hand-over | - |
| `project-scope` | Project scope | - |
| `settings-section-world` | Settings section (world) | Renderer.Quality |
| `simple` | Simple | - |
| `user-scope` | user scope | - |

# Brief: `editor-ui/settings-windows`

| Field | Value |
| --- | --- |
| Title | Settings windows from schemas |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/inspectors`, `world/projects-settings`, `physics/collision-layers`, `input/rebinding`, `image/quality-settings` |
| From | editor-ui §1.12 and concept 26 (the settings browser, pages generated from settings fields, the custom pages for Graphics Quality, Collision Layers and Input Actions, `BindingCapture`, Preferences) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/settings-windows` — Settings windows from schemas

**Covers.** Settings pages generated from schemas. The problem and how engines solve it: settings sections registered
with fields must not each need a hand-written page, while complex sections still need their own. The map: the settings
registry's sections → `EditorSettingsPageRegistry` (custom pages by section id) → `SettingsBrowser` (pages by category,
with a search) inside the Project Settings panel and the Preferences dialog. The contract: every edit runs a command
(`project.setSettings`, `preferences.set`, or the project's own commands) with the UI's origin; pages draw from copies
refreshed when the values' version changes, never parsing per frame. The toy is a page generator of about 40 lines.

The real code: the generic page (fields drawn as properties through `SettingsFieldProperty`, the command run once when
an edit finishes, a stored value that is refused shown with its reason, Reset to Defaults); binding capture, which takes
the keyboard from ImGui with key owners, locks keys until they are released, ends on a timeout or when its owner stops
asking, and keeps the keyboard until every key is up. Then the pages: the Project Settings panel's Game page (start and
loading scenes, title, version, company, copyright, icon) and Export page (kept paths); Graphics Quality (preset chips,
rows by presets, an editable Custom column, memory at 1080p and 2160p, GPU time, the players' options banner and reset);
Collision Layers (names and the matrix); Input Actions with binding capture; the External Editor page, the fourth custom
page, registered for `Editor.ExternalEditor` (the command that opens sources, the program it starts, the code editors
found on the machine); the Preferences dialog, which works on the launcher too (External Editor, Interface, Frame Rate).
Pictures: Graphics Quality, the Collision Layers matrix, Input Actions listening; Preferences' Interface and Frame Rate
pages. At the end the reader can register a settings section and see its page appear, or write a custom page.

**Leaves out.**

- Settings sections, fields, versions and validation → `world/projects-settings`
- What each quality row does and costs, and the players' options → `image/quality-settings`
- The collision layers table and its filter bits → `physics/collision-layers`
- Players' bindings and capture inside the engine → `input/rebinding`
- Every section's fields and defaults → `reference/settings`
- The UI scale that Preferences ▸ Interface sets → `editor-ui/ui-scale`
- The idle frame rates that Preferences ▸ Frame Rate sets → `editor-ui/status`

**Fit.** `fits`: about 5,275 words against L (5,000). One concept, two excerpts and the four custom pages (Graphics
Quality, Collision Layers, Input Actions, External Editor) take the most, with four figures and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:153` | feature | home | The Project Settings panel (closed by default) |
| `editor-ui:226-232` | feature | home | `SettingsBrowser` and the page registry; the generic page; the Project Settings pages; Graphics Quality; Collision Layers; Input Actions and `BindingCapture`; the Preferences dialog |
| `editor-ui:220` | feature | home | The External Editor page (critic-editor-ui-3): a custom `SettingsPage` of the Preferences dialog for `Editor.ExternalEditor`, registered in the page registry, the fourth custom page beside Graphics Quality, Collision Layers and Input Actions: the command that opens sources (`script.setExternalEditor`), the program it starts or why it cannot, the code editors found on the machine, the `STRATA_EXTERNAL_EDITOR` override; the New Script dialog of the same item is drawn on `editor-ui/launcher-dialogs`. Evidence: `StrataEditor/src/UI/ScriptDialogs.h:42-47`; `StrataEditor/src/EditorLayer.cpp:146-149` |
| `editor-ui:419` | concept | home | Settings UIs from schemas: generated pages, custom pages for complex sections, edits as commands, copies refreshed by version |
| `new:15` | code | home | `StrataEditor/src/UI/SettingsPages.cpp:84-179`: the generic page: fields as properties, the command run once an edit finishes, values read again only when their version changes, the refused value's reason |
| `new:16` | code | home | `StrataEditor/src/UI/BindingCapture.cpp:138-165`: the capture's frame: an owner that stopped asking, the timeout, the keyboard held until every key is up; with the key owners set at 41-47 |
| `editor-ui:574` | figure | home | Project Settings: Graphics Quality, the Collision Layers matrix, Input Actions with a capture listening |
| `editor-ui:576` | figure | home | Preferences: the Interface and Frame Rate pages |
| `editor-ui:650` | rule | home | Settings pages draw from copies refreshed by version, never parsing per frame |
| `editor-ui:783` | term | home | Settings page and settings browser (the word settings section is `world/projects-settings`', `scene-ecs:687`, and the page links it) |
| `new:44` | hands-on | home | Exercises (D27): a simple settings section with a `bool` and a ranged `float` registered in a patch, its generic page found in Project Settings, an edit made and its `project.setSettings` entry read in the Activity panel (Medium, extend); a breakpoint in the generic page's `Apply` shows the command run once when an edit finishes and the values read again after it (Medium, trace); what the page shows when the project file holds a value the section's validation refuses (Hard, predict then run). Evidence: `Strata/src/Strata/Core/SettingsRegistry.h:120-122`; `StrataEditor/src/UI/SettingsPages.cpp:163-168` |
| `editor-ui:782` | term | use | Binding capture, as `input/rebinding` defines it |
| `editor-ui:179` | feature | use | `DrawPropertyWidget`, which the generic page draws fields with |
| `audio-input:181` | feature | home | The Input Actions page: maps, actions, kinds, dead zones, binding chips, composites part by part, capture with its 10 s timeout, "In play" markers, Reset Player Bindings |
| `audio-input:476-477` | figure | home | The Add binding popup building a 2D composite part by part; binding capture listening, with its countdown and Cancel |
| `scene-ecs:486` | figure | home | The Project Settings panel: the page list, the Timing page (a generic page) and the Collision Layers page (a custom page): with `editor-ui:574` |
| `scene-ecs:488` | figure | home | The Preferences dialog, to contrast user sections with project sections: with `editor-ui:576` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections: fields, versions, validation, simple and complex sections | `world/projects-settings` | must |
| Players' graphics options; presets and traits; the quality rows | `image/quality-settings` | must |
| Collision layers: the project's table and filter bits | `physics/collision-layers` | must |
| Players' bindings and binding capture in the engine | `input/rebinding` | must |
| Property widgets and the property table | `editor-ui/inspectors` | must |
| Commands (`project.setSettings`, `preferences.set`) | `editor/commands` | must |
| Input actions | `input/actions` | helps |
| ImGui's key ownership | `editor-ui/imgui` | helps |
| The external editor (`script.setExternalEditor`) | `editor/script-builds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `settings-section-editor-ui` | Settings section (editor-ui) | settings page, settings browser |

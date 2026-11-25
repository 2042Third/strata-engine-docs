# Brief: `editor-ui/inspectors`

| Field | Value |
| --- | --- |
| Title | Inspectors from reflection |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `editor-ui/shell`, `editor/prefab-instances`, `world/reflection` |
| From | editor-ui ch. 10 "Inspectors generated from reflection" and the Asset tab (`AssetInspectorPanel`, `MaterialEditor`, `AnimationAssetViews`, `AudioPreview`); examples chosen outside wave 8 subjects |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/inspectors` — Inspectors from reflection

**Covers.** How one generic panel edits every component. The problem and how engines solve it: hundreds of properties
must not each need UI code; one generic inspector driven by metadata, hand-written editors per type, and custom
drawers as escape hatches (Unity, Unreal and Godot each have them); how the metadata is obtained is
`world/reflection`'s comparison, which the page links. The map is a diagram:
`ComponentInfo::Properties` → groups by section, made once per type → `DrawPropertyRow` → a property drawer or
`DrawPropertyWidget` → `SetPropertyWithUndo` → the undo stack, merged until the edit finishes. The contract: every edit
goes through the undo helpers; prefab commands are scheduled after drawing; a property that another property can switch
off gets an inactive reason. The toy is a generic inspector over a list of names, types, getters and setters.

The real code: the groups and rows (labels with their overridden mark and inactive reason, mixed values across
entities shown as "--", writes of only the changed axes, rotations through the angles the widget showed, the merge
broken when an edit finishes); the type switch from `PropertyType` to widgets; the material editor (a drag previews in
the loaded material, its release saves with one undo step and one write). Then the rest of the Inspector: the component
sections and their header, component drawers (the UI rect's anchor grid) and property drawers (the TAA preset), the
component menu (Reset, Copy and Paste Values as clipboard JSON, Remove), Add Component and missing-requirement notices,
the prefab bar and overrides, the scene's settings when nothing is selected with live lines (sun shadow maps), script
fields and the animator's state, the tab switch for a new inspection target. Then the Asset tab: header and actions, an
import-settings draft with Apply and Revert, the material section, texture previews through the display modes, models,
audio waveforms, animation views, the import outcome. Examples avoid the subjects of wave 8. Pictures: one entity and
three with mixed values, a prefab instance with its Overrides menu, an inactive property with its tooltip, the TAA
preset drawer and Add Component, the Asset tab. At the end the reader can register a property drawer and add an
inactive reason, as `capstone/build` does.

**Leaves out.**

- How properties, sections and inactive reasons are registered → `world/reflection`
- How prefab overrides are kept exact → `editor/prefab-instances`
- Undo steps, merging and `SetPropertyWithUndo` → `editor/undo`
- Settings pages drawn with the same widgets → `editor-ui/settings-windows`
- Edit-mode poses and animation previews → `animation/editor`
- Every component and its properties → `reference/components`

**Fit.** `fits`: about 7,425 words against XL (8,000). The entity inspector takes most of the page; the Asset tab, with
the material editor's excerpt, takes about 1,700 words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:145-146` | feature | home | The Inspector panel and the Asset tab: what each shows |
| `editor-ui:175-190` | feature | home | Component sections, property rows, mixed values and partial writes, undo merging, the widgets by type, the property table, inactive reasons, drawers, the component menu and Add Component, the prefab bar and overrides, the material section and editor, scene settings, live lines, script fields and the animator, the target switch |
| `editor-ui:376` | concept | home | Reflection-driven inspectors: three ways to build inspectors (one generic inspector from metadata, hand-written editors per type, custom drawers as escape hatches), with a link to `world/reflection` for how the metadata is obtained (critic-editor-ui-4); metadata driving a generic widget, multi-edit, undo merging, override marks; one undo step per drag frame, Euler angles read back from a quaternion |
| `editor-ui:458` | code | home | `StrataEditor/src/Panels/InspectorPanel.cpp:915-1035`: the central algorithm: groups by section once per type, a drawer or the generic widget, mixed values, per-axis writes, the merge broken when the edit finishes |
| `editor-ui:459` | code | home | `StrataEditor/src/UI/PropertyWidgets.cpp:892-960`: the switch from `PropertyType` to widgets, with the special cases of `UInt` |
| `new:9` | code | home | `StrataEditor/src/UI/MaterialEditor.cpp:96-128`: a dragged value previews in the loaded material, and its release saves once and breaks the merge |
| `editor-ui:511` | figure | home | The generated inspector pipeline from `ComponentRegistry` to the undo stack |
| `editor-ui:555` | figure | home | The Inspector with one entity (axis labels in the axis colors, sections), then with three entities and mixed values |
| `editor-ui:557` | figure | home | A prefab instance: the prefab bar, overridden labels with the accent bar, the Overrides menu open |
| `editor-ui:558` | figure | home | An inactive property with its tooltip (Bloom's threshold while Bloom is off), and the directional light's "Shadow maps" line |
| `editor-ui:560` | figure | home | The Post Process TAA preset drawer; the Add Component popup with its filter |
| `editor-ui:561` | figure | home | The Asset tab: a material being edited; a normal map shown through the NormalXY display beside a raw view; an audio clip's waveform |
| `editor-ui:655` | rule | home | A property another property can switch off gets an `InactiveReason`: the Inspector's side, which disables the row and shows the reason (the registration and its rule, `scene-ecs:198` and `:531`, are `world/reflection`'s) |
| `editor-ui:674` | hands-on | home | Register a `PropertyDrawer` (a light's color temperature as a gradient bar) |
| `editor-ui:675` | hands-on | home | Add an inactive reason next to a property's registration and see the Inspector disable it |
| `new:37` | hands-on | home | Trace it yourself (D27): a breakpoint at the Inspector's write while a light's intensity is dragged shows one `SetPropertyWithUndo` call per changed frame merged into one undo step, and `BreakMerge` when the edit finishes; with three lights selected the same drag takes the branch that writes several entities. Evidence: `StrataEditor/src/Panels/InspectorPanel.cpp:1010-1034` |
| `editor-ui:754` | term | home | Property table |
| `editor-ui:757-758` | term | home | Section (property); mixed value |
| `editor-ui:761` | term | home | Component drawer and property drawer |
| `editor-ui:760` | term | use | Inactive reason, one glossary entry with `scene-ecs:654`, homed on `world/reflection` (R31, D11; world-q2): the page uses the word where the Inspector disables a row and shows its reason |
| `editor-ui:755-756` | term | use | Reflection; `PropertyInfo` and `ComponentInfo`, as `world/reflection` defines them |
| `editor-ui:759` | term | use | Override (prefab), as `world/prefabs` defines it |
| `editor-ui:762` | term | use | Undo merge, as `editor/undo` defines it |
| `editor-ui:41` | feature | use | The texture display modes the Asset tab's previews use |
| `assets:215` | feature | home | The Asset tab's import settings drawn from `GetSettingsProperties`, with inactive reasons; files dropped on the Content Browser import (`editor-ui/lists` shows the drop target) |
| `audio-input:99` | feature | home | `AudioPreview`: one preview source outside any scene, a waveform of minimum and maximum per column computed on a job (none beyond 600 s), drawn in the Asset tab |
| `audio-input:471` | figure | home | The Asset tab's audio preview with its waveform and Play: one picture with `editor-ui:561` |
| `audio-input:650` | term | home | Waveform (preview) |
| `gameui:216-217` | feature | home | The UI Rect drawer: the anchor grid with its 16 presets, a rect kept in place while its anchors change, margins along stretched axes, pixels at the game's screen, prefab overrides |
| `gameui:482` | figure | home | The UI Rect drawer with the anchor preset grid open and margin rows on a stretched element |
| `scene-ecs:198` | feature | use | `ComponentRegistry::SetInactiveReason<T>(property, fn)`, homed on `world/reflection` (R31, D11): this page shows how the Inspector disables the property and shows the reason |
| `scene-ecs:474` | figure | home | A camera's Inspector in Orthographic: the perspective fields disabled with their reason, and Depth Of Field off greying Aperture |
| `scene-ecs:479` | figure | home | A prefab instance's Inspector: one picture with `editor-ui:557` |
| `scene-ecs:531` | rule | use | A property another turns off gets an `InactiveReason`, homed on `world/reflection` (R31, D11): beside `editor-ui:655`, the Inspector's side of it |
| `scene-ecs:654` | term | link | Inactive reason, homed on `world/reflection` (R31, D11) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reflection: `ComponentRegistry`, `PropertyInfo`, ranges, flags, sections, inactive reasons | `world/reflection` | must |
| Undo and redo: `SetPropertyWithUndo`, merging and breaking the merge | `editor/undo` | must |
| Prefab instances, overrides, apply and revert | `editor/prefab-instances` | must |
| Rotations: Euler angles and quaternions | `basics/math-rotations` | must |
| `std::variant` and `std::optional` | `basics/cpp-modern` | must |
| Texture display modes | `editor-ui/imgui-backends` | must |
| The kit and panels | `editor-ui/shell` | must |
| Strata's material model | `light/materials` | helps |
| Texture import settings and usages | `assets/texture-cooking` | helps |
| The quality rows (the sun's shadow maps line) | `image/quality-settings` | helps |
| Script fields | `scripting/script-system` | helps |
| Edit-mode poses and previews | `animation/editor` | helps |
| Audio clips | `audio/clips-voices-sources` | helps |
| Rects, anchors and layout (the UI Rect drawer) | `ui/layout` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `component-drawer` | Component drawer | - |
| `mixed-value` | Mixed value | - |
| `property-drawer` | property drawer | - |
| `property-table` | Property table | - |
| `section-property` | Section (property) | - |
| `waveform-preview` | Waveform (preview) | - |

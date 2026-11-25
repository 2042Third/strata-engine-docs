# Brief: `editor-ui/widget-kit`

| Field | Value |
| --- | --- |
| Title | The widget kit |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/design-system` |
| From | editor-ui ch. 7 (the anatomy of a widget, chips and the chip strip, pills, modals, the item probe) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/widget-kit` — The widget kit

**Covers.** How to write custom widgets in an immediate-mode library, on Strata's kit. The problem: ImGui's own widgets
do not carry the editor's look, sizes and test hooks, yet a custom widget must still behave as an ImGui item. The
anatomy comes first (a diagram), on the kit's button: reserve an `InvisibleButton` for hit testing and navigation, read
hovered and held, draw with the window's draw list in theme colors, keep an active state vivid while disabled, render
the nav cursor, show the tooltip, record the rectangle in the item probe. The toy is a toggle button of about 40 lines.
Then layout that depends on its own result: the chip strip measures its chips in one frame, decides in its destructor
which chips become icons and where rows wrap, and the next frame draws them (a diagram over two frames, and the Scene
view's toolbar wide and narrow). Then the item probe: one hash-map write per widget and frame, in every build
configuration, keyed by id, with ids recorded twice flagged.

The catalogue follows in one table: button styles, icon and toolbar buttons, chips and toggle chips, pills, banners,
search fields, selection colors, section headers and headings, cards and entry cards, modals and dialog buttons, action
and link buttons, text fields, copyable code, elision, the legend, `TextureImage`, cancelling a drag with Escape; and the
helpers `TextFormat`, `Markdown` and the native file dialogs (nfd: blocking, main thread). The rules: controls come
from the kit; chips never take focus; costly tooltips are written only while due; an active `InputText` keeps its own
copy, so text replaced from outside needs a reload. A zoomed picture shows the kit. At the end the reader can write a
new kit widget with probe keys.

**Leaves out.**

- Clicking widgets in tests through the probe → `editor-ui/ui-testing`
- The status bar's pills and their compact texts → `editor-ui/status`
- The Scene view's chips and what each does → `editor-ui/scene-view`
- Asking the person in a modal, and the re-ask rule → `editor-ui/shell`
- Texture display modes, which `TextureImage` sets → `editor-ui/imgui-backends`

**Fit.** `fits`: about 4,900 words against L (5,000). The concept of writing custom widgets and the three excerpts carry
the teaching; the catalogue is one table, not a section per widget.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:73-103` | feature | home | The kit's promise (sized from the font, colored from the theme, recorded in the probe) and every widget and helper of `UI/Widgets.h`, the item probe, `TextFormat`, `Markdown` and `FileDialogs` |
| `editor-ui:345` | concept | home | Writing custom widgets: reserve an item, read its states, draw, nav cursor, tooltip, probe; layout decided from the previous frame; `BeginDisabled` fading what must stay vivid, chips that steal focus |
| `editor-ui:442` | code | home | `StrataEditor/src/UI/Widgets.cpp:62-122`: the anatomy of a kit widget (`DrawButton`) |
| `editor-ui:443` | code | home | `StrataEditor/src/UI/Widgets.cpp:218-279`: the chip strip decided in its destructor and drawn by the next frame |
| `editor-ui:444` | code | home | `StrataEditor/src/UI/ItemProbe.cpp:25-52`: one hash-map write per widget and frame, duplicates flagged, found only in the latest frame |
| `editor-ui:498` | figure | home | The anatomy of a kit widget: the item's rectangle, background, icon, label, nav cursor, tooltip, probe entry |
| `editor-ui:499` | figure | home | The chip strip over two frames: widths measured, `FirstIcon` and `RowStarts` decided, then drawn |
| `editor-ui:547` | figure | home | A zoomed crop of the kit: toolbar buttons in their styles, chips in their states, pills, a section header, cards, the progress bar, a legend |
| `editor-ui:564` | figure | home | The Scene view's toolbar wide (labels) and narrow (icons, wrapped rows), to show the chip strip |
| `editor-ui:600` | rule | home | Controls from the kit, each recorded in the probe |
| `editor-ui:616` | rule | home | Chips never take focus (`ImGuiButtonFlags_NoFocus`) |
| `editor-ui:622` | rule | home | Write costly tooltips only while due (`UI::IsTooltipDue`) |
| `editor-ui:646` | rule | home | An active `InputText` keeps its own copy of the text (`SearchField`'s reload) |
| `editor-ui:669` | hands-on | home | Write a kit widget (a segmented toggle) with probe keys and a harness test that clicks it |
| `editor-ui:730-731` | term | home | Widget kit; `InvisibleButton` |
| `editor-ui:742` | term | home | Item probe |
| `editor-ui:749-752` | term | home | Pill; chip; chip strip; banner, card, entry card and section header |
| `editor-ui:792` | term | home | nfd, the native file picker library |
| `new:34` | hands-on | home | Trace it yourself (D27): a breakpoint in `ItemProbe::RecordRect` while the Scene view's toolbar draws shows one write per widget and frame, the rectangle of the last item, and the flag set when an id is recorded twice in one frame; a search for `ImGuiButtonFlags_NoFocus` then finds the chips. Evidence: `StrataEditor/src/UI/ItemProbe.cpp:25-52`; `StrataEditor/src/UI/Widgets.cpp:138` |
| `editor-ui:624` | rule | link | Why UI code draws textures through `TextureImage` (`editor-ui/imgui-backends`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| ImGui's items, IDs, hovered and active, keyboard navigation | `editor-ui/imgui` | must |
| ImGui's draw lists | `editor-ui/imgui-backends` | must |
| The theme's tokens and meanings, the type scale, icons as text | `editor-ui/design-system` | must |
| Texture display modes | `editor-ui/imgui-backends` | must |
| Hash maps and what they cost | `basics/data-structures` | helps |
| UTF-8 (eliding text by characters) | `basics/bytes` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `banner` | Banner | - |
| `card` | card | - |
| `chip` | Chip | - |
| `chip-strip` | Chip strip | - |
| `entry-card` | entry card | - |
| `invisiblebutton` | InvisibleButton | - |
| `item-probe` | Item probe | - |
| `nfd` | nfd | - |
| `pill` | Pill | - |
| `section-header` | section header | - |
| `widget-kit` | Widget kit | - |

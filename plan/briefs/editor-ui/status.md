# Brief: `editor-ui/status`

| Field | Value |
| --- | --- |
| Title | Status bar, toasts and idle throttling |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/shell`, `core/profiling` |
| From | editor-ui ch. 14 (pills and hysteresis, toasts, work time against frame rate, `Editor.FrameRate`); home of notifications, their model (`EditorNotifications`) and their drawing |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/status` — Status bar, toasts and idle throttling

**Covers.** Telling the person what happens without interrupting them, and redrawing only as often as needed. The
problem and how engines solve it: status bars with pills that lead somewhere, toasts that never take focus, errors
counted as unread, against modal error dialogs for routine failures; an immediate-mode UI redraws every frame, so
editors idle at a low rate when nothing happens and run uncapped while someone waits by frames. The map: what each
pill reads, where its click leads, and the notifications' model in the core and their drawing in the UI. The contract:
toasts never take focus and cost nothing while empty; the frame pill shows work time, not the frame interval; a panel
that animates without input reports `IsAnimating`; frames that run work someone waits for by frames are never capped.

The real code: the status bar's pills (play state; the frame's milliseconds, frames per second and jobs; the assets with
the pool closest to its budget in Sulfur or Cinnabar; saving; bodies without collision; automation, with its texts
made again only when the clients' version or the port changes and a tooltip of the clients and the requests; scripts;
input holds that a click releases; unread errors), each opening its panel, with compact texts decided from the previous
frame's widths and a margin of two font sizes against flicker (a diagram); idle throttling as a policy (`TrackInput`,
`IsBusy`, `RunsUncapped`, the `Editor.FrameRate` preferences and their defaults, the floor of 5 fps because the frame
pacer sleeps through input, the lift while steps are pending; a diagram); the frame statistics, where work time is
averaged over 60 frames without waits (the term frame work time is `core/frame-loop`'s, linked). Then notifications: the
core's model (at most four, merged when identical or of one group, lifetimes by level, replaced in place, kept while
hovered, versioned; a diagram), the outcome of the person's commands without double toasts, and the drawing: one window
that never takes focus, at the bottom right of the shown Scene or Game view, with its actions (Show in Activity, Show
Asset, Show Problems, Show in Console, Recover). Pictures: the status bar full and compact, the errors pill, the assets
pill in Sulfur, the automation pill with no agent and with a named agent, its tooltip open; toasts with their buttons.
At the end the reader can add a status pill with a compact text, and make an animated panel keep its frame rate.

**Leaves out.**

- The panels the pills open → `editor-ui/instrument-panels`
- Measuring the frame, stages and Tracy → `core/profiling`
- The `editor.status` command → `automation/agents`
- Status providers, the sections of `editor.status` → `editor/commands`
- The recovery offer that a toast leads to → `editor/recovery`
- Holds of simulated input → `editor/stepping`
- The automation server, its clients and their names → `automation/rpc-server`

**Fit.** `fits`: about 6,360 words against L (5,000). Two concepts, three excerpts, five figures and four rules take the
most, with the pills taught in one table; the page stands about 140 words below L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:116-119` | feature | home | The status bar's pills; compact texts with hysteresis; idle throttling and `Editor.FrameRate`, with the floor of 5 fps and its reason: the frame pacer sleeps without waking on input, so an idle editor answers the first input up to one idle interval late, 33 ms at 30 fps and 100 ms at 10 fps unfocused (critic-editor-ui-5, about 60 words; `StrataEditor/src/Editor/EditorFrameRate.h:30-32`); the frame statistics passed to panels |
| `editor-ui:248-250` | feature | home | `EditorNotifications`; `NotifyCommandOutcome` and `Announced`; `UI::DrawNotifications` |
| `editor-ui:406` | concept | home | Feedback without interruption: pills that lead somewhere, toasts without focus, unread errors, compact texts; modal errors for routine failures |
| `editor-ui:408` | concept | home | Power: idle throttling, uncapped work, work time against the capped interval; a frozen animation |
| `editor-ui:451` | code | home | `StrataEditor/src/EditorLayer.cpp:842-919`: idle throttling as a policy: when it applies, busy detection, uncapped work, the caps |
| `editor-ui:452` | code | home | `StrataEditor/src/EditorLayer.cpp:1872-1944`: the status bar with hysteresis between full and compact texts, and `StatusPillText` |
| `new:11` | code | home | `StrataEditor/src/UI/Notifications.cpp:69-97`: nothing done while empty; one window that takes neither focus nor navigation, brought to the front unless a modal is open; actions on a copy of what shows |
| `editor-ui:528` | figure | home | Status bar hysteresis: the available width, the full width, the margin of two font sizes |
| `editor-ui:526` | figure | home | The idle-throttling decision as a flowchart, with the lift while steps are pending |
| `editor-ui:529` | figure | home | A notification's life: posted and merged, shown, kept, replaced, dismissed or expired; at most four |
| `editor-ui:572` | figure | home | The status bar with full and compact texts (a narrow window at 150%), the errors pill, the assets pill in Sulfur |
| `editor-ui:573` | figure | home | Toasts stacked at the bottom right of the Scene view with their action buttons |
| `editor-ui:618` | rule | home | Toasts never take focus and cost nothing while empty |
| `editor-ui:626` | rule | home | Show work time, not the frame interval |
| `editor-ui:627` | rule | home | A panel that animates without input reports `IsAnimating` |
| `editor-ui:629` | rule | home | Frames that run work someone waits for by frames are never capped |
| `editor-ui:671` | hands-on | home | Add a status pill with a compact text that focuses a panel; test it at 150% in a narrow window |
| `editor-ui:677` | hands-on | home | Write a panel that animates, watch the idle throttle slow it, fix it with `IsAnimating` |
| `editor-ui:748` | term | home | Toast and notification |
| `editor-ui:778` | term | home | Idle throttling |
| `editor-ui:781` | term | home | Notification group |
| `new:41` | hands-on | home | Trace it yourself (D27): breakpoints in `EditorLayer::IsBusy` and `RunsUncapped` show what keeps the editor from idling (input within the idle delay, an agent's recent request, a panel that reports `IsAnimating`, a running or stepping game, assets loading, a pending pick) and what lifts the cap (pending steps, commands or automation requests), and `IsThrottlingEnabled` turning it all off for a command-script run. Evidence: `StrataEditor/src/EditorLayer.cpp:842-919` |
| `editor-ui:779` | term | link | Frame work time, homed on `core/frame-loop` beside `foundation:48` (duplicates.md:51) |
| `editor-ui:780` | term | use | Status provider, as `editor/commands` defines it (editor-q5) |
| `editor-ui:82` | feature | use | The kit's `Pill` and `CalcPillWidth` |
| `assets:514` | figure | home | The status bar's assets pill and the assets section of `editor.status`, as a text capture |
| `editor-core:46` | feature | home | The notifications' model and what feeds it: taught with `editor-ui:248` |
| `editor-core:738` | term | home | Notification and toast: one glossary entry with `editor-ui:748` |
| `automation:182` | feature | home | The automation pill: "port N · no agent", "Agent connected · <name>", "N agents connected" with their compact texts, "Automation off" and "Automation failed"; the tooltip of clients and request counts; the texts made again only when `GetClientsVersion` or the port changes: taught with `editor-ui:116` |
| `automation:577` | figure | home | The automation pill with no agent and with a named agent (`claude-code`), its tooltip open: one picture with `editor-ui:572` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Measuring the frame: frame time, work time, stages | `core/profiling` | must |
| Commands and their results; command origins | `editor/commands` | must |
| Panels, `Focus` and `GetShownWindowRect` | `editor-ui/shell` | must |
| The kit's pills and the chip strip's idea of deciding from the previous frame | `editor-ui/widget-kit` | must |
| The frame loop and its frame rate cap | `core/frame-loop` | helps |
| Residency, budgets and memory pools | `assets/residency` | helps |
| Physics capacity and bodies that wait | `physics/scale-streaming` | helps |
| Simulated input and its holds | `input/simulated` | helps |
| Pausing and stepping a game | `editor/stepping` | helps |
| Autosave and the recovery offer | `editor/recovery` | helps |
| The RPC server's clients, their names and its version counter | `automation/rpc-server` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `idle-throttling` | Idle throttling | - |
| `notification-group` | Notification group | - |
| `toast` | Toast | notification |

# Brief: `editor-ui/instrument-panels`

| Field | Value |
| --- | --- |
| Title | Instrument panels |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/lists`, `editor-ui/status`, `editor/journal`, `editor/script-builds`, `worlds/streamer` |
| From | editor-ui ch. 16 (Console, Problems, Activity, Streaming and Performance: what each shows and how each keeps its cost low); home of the Activity panel's drawing |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/instrument-panels` — Instrument panels

**Covers.** The five panels that show the editor's machinery: what each shows and how each keeps its cost low. The job
and a one-paragraph problem: instruments that cost more than what they measure are useless. The map: each panel
collects in `OnUpdate`, also while it is closed, so the status bar can show its figure, and draws only while visible;
the Problems and Activity panels rebuild their rows when a version changes; the Streaming panel builds its table on a
job. The contract: idle frames compare numbers and draw clipped rows; big tables are built off the main thread. The toy
is a panel of about 40 lines whose rows are rebuilt only on a version change.

The real code: the Problems panel's idle check (one number and a short key compared) and its clipped table, with file
texts elided once per width; the Streaming panel's table built on a job and swapped in when done, at most every quarter
second; the Activity panel's rows rebuilt only when the journal's version or the filters change. Then each panel: the
Console (level filters, search, messages with a source reference that open the external editor, unread errors counted
for the status bar); Problems (the crash first, with its stack and without the SDK's internals, then the last build's
errors and warnings, a summary line, a double click that opens the source in the external editor, the Build button, and
a Play whose script build failed bringing the panel forward through a request counter that the UI compares every frame);
Activity (the journal as a table of summaries, each with an arrow that shows its raw parameters and result below it,
filters by text, source and whether it changed anything, a selected entry's JSON, Copy as script, Re-run, Undo to here);
Streaming (pools against budgets, loads, queues, the upload sparkline, the asset table, the Physics and World sections
with the cell map); Performance (600 frames of CPU and GPU timeline, spikes, the stage table, what bounds the frame,
pause and Space, Copy as JSON). Pictures: Activity with an entry's JSON, Problems after a failed build, the Console with
a source reference, the Performance timeline, the Streaming panel with the cell map. At the end the reader can read the
editor's state from its instruments, and write a panel whose idle frame costs almost nothing.

**Leaves out.**

- The frame profiler, its stages and Tracy → `core/profiling`
- The journal's model, origins and replays → `editor/journal`
- Building scripts and parsing diagnostics → `editor/script-builds`
- From an address to a file and line → `scripting/symbolization`
- Residency, budgets and pools → `assets/residency`
- The world's cells and the editor's world → `editor/worlds`
- The panels' perf tests → `editor-ui/ui-testing`

**Fit.** `fits`: about 5,375 words against L (5,000). Five panels and four excerpts take the most, with three exercises;
the panels share one contract, so each panel takes one section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:148-152` | feature | home | The Console, Problems, Streaming, Performance and Activity panels: what each shows |
| `new:17` | feature | home | The Problems panel's rows: the crash first (where it happened, on which entity, in which function), its stack frames with a source but without the SDK's `Strata::Detail::` thunks, then the build's diagnostics, and a summary line ("The scripts crashed in…", "Build N failed: …", "No script build in this session yet"). Evidence: `StrataEditor/src/Panels/ProblemsPanel.h:13-17`; `StrataEditor/src/Panels/ProblemsPanel.cpp:110-216` |
| `new:18` | feature | home | Opening a row's source: an absolute path, or the file found in the project, its script folder or the build folder; the File column relative to the project; the reason shown when there is no file. Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:37-77, 218-236` |
| `new:19` | code | home | `StrataEditor/src/Panels/ProblemsPanel.cpp:100-108`: an idle frame compares the last build's ID and the crash's key, and rebuilds nothing |
| `new:20` | code | home | `StrataEditor/src/Panels/ProblemsPanel.cpp:272-341`: a clipped table, the first rows recorded in the probe, the file texts elided once per width, a double click that opens the source |
| `new:21` | rule | home | A row that shows text the program does not control is an unlabeled item (`##Row`) with the text drawn after it: a compiler's message may hold `##`, which a label would cut. Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:295-296` |
| `new:22` | code | home | `StrataEditor/src/Panels/StreamingPanel.cpp:609-666`: the asset table rebuilt on a job at most every `c_TableRefreshSeconds`, one build at a time, swapped in when done |
| `new:23` | code | home | `StrataEditor/src/Panels/ActivityPanel.cpp:165-205`: rows rebuilt only when the journal's version or the filter key changed |
| `editor-ui:577` | figure | home | Activity with a selected entry's JSON and its buttons; Problems after a failed build; the Console with a clickable source reference |
| `editor-ui:579` | figure | home | The Performance panel's CPU and GPU timeline; the Streaming panel with the World section's cell map: the cell map is one capture set with `worlds-runtime:392` on `editor/worlds`, made once (R34, D42), and this page's caption says what the panel shows |
| `new:45` | feature | home | A Play that fails because its script build failed or its module did not load brings the Problems panel forward: `play.start` raises a request counter in the core, and the UI compares it every frame and focuses the panel, the core asking the UI without knowing it, the same pattern as the inspection version (critic-editor-ui-6, about 50 words). Evidence: `StrataEditor/src/Editor/Commands/PlayCommands.cpp:58-69`; `StrataEditor/src/Editor/EditorContext.h:607-609`; `StrataEditor/src/EditorLayer.cpp:746-757` |
| `new:46` | hands-on | home | Exercises (D27): a breakpoint in `ProblemsPanel::OnUpdate` shows an idle frame comparing the last build's ID and the crash's key and returning (Basic, trace); a script with a planted compile error built from the editor, its row double-clicked to open the source, then Play pressed to watch the panel come forward (Medium, editor task); a scratch panel of 10,000 rows rebuilt only when a version changes, measured idle against one rebuilt every frame (Hard, extend: a patch). Evidence: `StrataEditor/src/Panels/ProblemsPanel.cpp:100-108`; `StrataEditor/src/Panels/ActivityPanel.cpp:165-170` |
| `editor-ui:190` | feature | link | The inspection target's tab switch, the counter pattern that `new:45` repeats (`editor-ui/inspectors`) |
| `editor-ui:169` | feature | use | The cached and clipped lists of these panels, taught on `editor-ui/lists` |
| `editor-ui:116` | feature | use | The status bar's pills that open these panels |
| `assets:213` | feature | home | The Streaming panel's pools, queue, uploads, prefetches and mip streaming, and its table's Mip column (resident and wanted) |
| `automation:176` | feature | home | The Activity panel as an agent's session shows in it: rows with summaries, raw parameters and result below an expanded row, filters, the details JSON, Copy as script, Re-run, Undo to here, rows rebuilt only when the journal's version or the filters change: taught with `editor-ui:152` and `new:23` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building scripts from the editor: diagnostics for the Problems panel, the external editor | `editor/script-builds` | must |
| The activity journal: origins and kinds, replays, Copy as script | `editor/journal` | must |
| Residency, pins and eviction; budgets and pools | `assets/residency` | must |
| Grids, cells and the streamer | `worlds/streamer` | must |
| Measuring the frame: the profiler and its stages | `core/profiling` | must |
| Lists that scale | `editor-ui/lists` | must |
| The status bar's pills | `editor-ui/status` | must |
| Jobs and handing results back | `core/jobs` | must |
| Crash containment and the crash that stops play | `scripting/crash-containment` | helps |
| GPU stages | `gpu/readback-timing` | helps |
| Physics capacity | `physics/scale-streaming` | helps |
| The log and its levels | `core/conventions` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

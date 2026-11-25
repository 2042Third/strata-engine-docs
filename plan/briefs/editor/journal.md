# Brief: `editor/journal`

| Field | Value |
| --- | --- |
| Title | The activity journal and replays |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/undo`, `editor/command-scripts` |
| From | automation ch. 4 "Recording and replaying"; editor-core §1.11 (`CommandJournal`, `BuildReplayScript`, command origins and kinds, agent presence) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/journal` — The activity journal and replays

**Covers.** The problem: when a person and an agent share an editor, the person must see what the agent did and undo it,
and an afternoon of work should become a test that repeats it. The approaches (logs, the undo history, macro recorders,
event sourcing) are compared on `automation/agents`, which the page links. Strata's choice: every command is journalled
once, in `Execute`, with its origin (UI, Automation with the client's name, CommandScript, Internal; nested commands as
children), its kind, its parameters (kept whole up to 256 KiB), its outcome, the IDs its result holds, its duration and
frames, the entities it touched and its undo step, in a ring of 2,000 entries and 8 MB; a deferred command's entry
completes on its final poll. The rule: UI code passes `CommandOrigin { CommandSource::UI }`, because an origin left out
is recorded as Internal and the journal would no longer say who did what. Edits outside commands (continuous UI edits
that record undo steps directly) are counted, because a replay cannot repeat them. The latest automation activity feeds
the agent's presence in the UI. Summaries read like "Rename 'Crate' to 'Box'". The person is told what others did:
toasts for an agent's deletes and discards, never for the person's own actions. `editor.activity` reads the journal, and
`editor.activity.export` builds a replay (`BuildReplayScript`): a forward pass finds which entry first produced each ID
and rewrites later parameters to refer to it, a backward pass adds the lookups the edits need; only Edit commands not
made on the running copy are repeated, so the kinds of `editor/commands` decide what a replay holds, and an unmarked
command counts as an edit. A paragraph says what a replay cannot hold: edits outside commands (inspector fields, gizmo
drags, the material editor), counted as `editsOutsideCommands`; IDs taken from the selection or from `editor.status`,
which stay as they are because the selection is not repeated; what `scene.recover` applied, counted as
`unrepeatableEdits`; and files no command wrote (script sources an agent edited, generated source assets), so the fresh
copy needs its `Scripts/` before the script runs. The file format of the exported script is the next page's; this page
shows an export only as a list of commands whose IDs became references. Tests: `Editor.Journal`, `Editor.Replay` in
process and the CTest `ReplaySession`, which exports a session, replays it on a copy of the project and compares the
documents. The example and exercise: work by hand and through `StrataCLI`, export the session, and read
`editsOutsideCommands`; the trace exercise finds where `BuildReplayScript` turns an ID into a reference. Afterwards the
reader can add a command whose work the journal records and a replay repeats.

**Leaves out.**

- The command script format (`bind`, `$ref`, `expect`) → `editor/command-scripts`
- The Activity panel as it is drawn → `editor-ui/instrument-panels`
- The agent chip and flash as they are drawn → `editor-ui/scene-view`
- Why accountability matters for agents, and logs, undo histories, macro recorders and event sourcing compared →
  `automation/agents`
- The activity journal as a game maker uses it with an agent, and copying `Scripts/` before a replay →
  `make/with-an-agent`

**Fit.** `over`: about 4,800 words against M (3,000). Counted again from the sections, with what a replay cannot hold
and the trace exercise, and with the comparison of approaches linked to `automation/agents`: the journal's items that
the unit `automation` passed here (section 1.9, the suites, an excerpt, a figure, the rule on origins) beside the unit's
own pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:372` | concept | home | Telling the person what happened: origins, toasts for what agents did, never for the person's own actions |
| `editor-core:242-244` | feature | home | `CommandJournal`, `editor.activity` and `editor.activity.export`, the replay tests |
| `new:36` | code | home | `StrataEditor/src/Editor/CommandJournal.h:72-111`: one journal entry |
| `editor-core:504` | figure | home | Record and replay: entries, the export, a run on a copy, the comparison |
| `editor-core:513` | figure | home | The Activity panel listing commands of the person, an agent and a command script |
| `editor-core:618` | hands-on | home | The example: a session exported as a regression script |
| `new:62` | hands-on | home | Trace it yourself (D27): create an entity with `entity.create` and rename it with `entity.rename` from a terminal, export the session with `editor.activity.export`, and with a breakpoint in `CommandJournal::BuildReplayScript` find where the rename's entity ID becomes a `$ref` to the create's result. Evidence: `StrataEditor/src/Editor/CommandJournal.cpp:697-818`, `:368` |
| `editor-core:668-670` | term | home | Activity journal, origin, replay script |
| `automation:430` | concept | use | Accountability: the journal, presence and replay; the problem in one sentence, and the comparison of logs, undo histories, macro recorders and event sourcing linked to `automation/agents`, its home |
| `new:72` | feature | home | What a replay cannot hold (about 100 words): edits outside commands (`editsOutsideCommands`); IDs taken from the selection or `editor.status`, kept as they are because the selection is not repeated; what `scene.recover` applied (`unrepeatableEdits`); files no command wrote (script sources an agent edited, generated source assets), so a fresh copy needs its `Scripts/` before the script runs. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:489-500`, `:537-539`; `.claude/skills/strata-editor-automation/SKILL.md:742-747`; `.claude/skills/strata-make-a-game/SKILL.md:438-442` |
| `automation:166-175` | feature | home | The journal's entries, origins, kinds, results kinds, recording in `Execute`, edits outside commands, ID collection, `BuildReplayScript`, the latest automation activity, summaries; one home with `editor-core:242` |
| `automation:151`, `automation:152` | feature | home | `editor.activity` and `editor.activity.export` as clients call them; one home with `editor-core:243` |
| `automation:240` | feature | home | `Editor.Journal`: every source recorded once, a deferred command recorded when it finishes, every command's kind declared |
| `automation:241` | feature | home | `Editor.CommandScriptBindings` and `Editor.Replay`; `editor/command-scripts` may cite the bindings' suite |
| `automation:243` | feature | home | The CTest `ReplaySession`: a session exported, replayed on a copy and compared; one home with `editor-core:244` |
| `automation:506` | code | use | `Execute` journals every command |
| `automation:508` | code | home | `StrataEditor/src/Editor/CommandJournal.cpp:697-818`: `BuildReplayScript`, the forward pass for the IDs each result gave first and the backward pass for the lookups and bindings the edits need |
| `automation:564` | figure | home | The replay export as a data flow: produced IDs, parameters rewritten to `$ref`, lookups marked backward, the script with `bind`; beside `editor-core:504` |
| `automation:639` | rule | home | UI code passes `CommandOrigin { CommandSource::UI }`, so the journal says who did what |
| `automation:782`, `automation:784` | term | home | Presence; edits outside commands |
| `automation:780-781`, `automation:783` | term | use | Activity journal, command origin, replay script, homed here as `editor-core:668-670` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands, their kinds and `Execute` | `editor/commands` | must |
| Undo steps and the history | `editor/undo` | must |
| Deferred commands and their final poll | `editor/deferred-commands` | helps |
| The running copy | `editor/play-mode` | helps |
| JSON pointers into a result | `editor/command-scripts` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `activity-journal` | Activity journal | - |
| `edits-outside-commands` | Edits outside commands | - |
| `presence` | Presence | - |
| `replay-script` | Replay script | - |

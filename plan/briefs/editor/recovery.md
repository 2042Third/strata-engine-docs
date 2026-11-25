# Brief: `editor/recovery`

| Field | Value |
| --- | --- |
| Title | Autosave and crash recovery |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/saving` |
| From | editor-core ch. 5 (the recovery journal, folding, discards, recovering as one undo step); the use side is `make/project-files` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/recovery` — Autosave and crash recovery

**Covers.** The problem: the editor crashes or the power fails an hour after the last save, or an agent forces a scene
open and the person's edits go with the old scene. The approaches, with their costs: periodic full copies of the scene
(common in content tools and engines), journals written ahead of the change (as databases do), and a snapshot plus
changes. Strata's choice and its reason: a journal of entity states since the last save, written against the hash of the
saved file it applies to, folded so that it grows only with structural edits, and written when the editor is quiet; and
"discard" means "kept as recovery data". The page teaches the observer pattern first (the journal follows the undo stack
without copying the scene), then `SceneRecovery` in the order of a session: the journal keeps the states of the steps
since the last save and writes `<project>/.strata/Recovery/<scene>-<session>.strecovery` two seconds after edits stop
and at least every ten seconds, building the text on a worker and writing it on an I/O job; the base hash is a SHA-256
read a megabyte at a time; folding merges every step that creates, removes or moves no entity into the segment before it
(`IsStructural`); a scene never saved is snapshotted whole, and steps of kind Other force a snapshot, both only up to
256 entities, because a snapshot is captured on the main thread: a never-saved scene that starts with more, or a larger
scene after a step of kind Other, is not journaled until it is saved, and `scene.recoveryStatus` says so and asks for
the save; forced discards and Don't Save write the journal marked Discarded, the newest eight are offered and older ones
move to `Recovery/Discarded` (twenty kept); a save in progress passes its token so that edits made during it are carried
into the journal of the saved document; files of a running editor (process id and start time) are left out of offers;
the journal follows a renamed or moved scene by its handle. `scene.recoveryStatus` and `scene.recover {apply, discard,
force}` finish it: apply opens the scene in the background and applies the changes as one undo step back to the saved
state. The rule: only `SceneRecovery` writes recovery files, and every scene replacement goes through `ResetScene`. The
example edits a scene, ends the editor's process, opens the project again and recovers. The exercise writes the segments
a sequence of steps produces on paper, then checks them with an `Editor.Recovery` test; the trace exercise follows one
edit from `OnApplied` to the file the quiet timer writes. Afterwards the reader can say what a crash at any moment
leaves, and change the journal without losing that guarantee.

**Leaves out.**

- The Recover Unsaved Changes dialog → `editor-ui/launcher-dialogs`
- Recovering a world's cells → `editor/worlds`
- Opening the scene in the background → `editor/projects`
- Recovering as a game maker does it → `make/project-files`

**Fit.** `over`: about 4,600 words against M (3,000). Counted again from the sections, with the limit of 256 entities
and the trace exercise: one concept, nine features in the order of a session, the excerpt in three parts and the shape
of an internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:333` | concept | home | Autosave and crash recovery: the approaches, the journal against a base hash, folding, discards kept |
| `editor-core:145-147`, `editor-core:149-153` | feature | home | The journal, the base hash, folding, discards, saves during journaling, ownership, following moves, `scene.recoveryStatus` and `scene.recover` |
| `editor-core:148` | feature | home | Complete journals: a never-saved scene snapshotted whole and steps of kind Other forcing a snapshot, both only up to `c_MaxSnapshotEntities` (256) because a snapshot is captured on the main thread; above it a never-saved scene, or a larger scene after a step of kind Other, is not journaled until it is saved, and the status says so and asks for the save. At the pin: `StrataEditor/src/Editor/SceneRecovery.h:121-126`, `:145`; `StrataEditor/src/Editor/SceneRecovery.cpp:463-468`, `:724-732`, `:1093`; `StrataEditor/src/Editor/EditorStateCommands.cpp:559-566` (`skipped` in `scene.recoveryStatus`) |
| `editor-core:425` | code | home | `StrataEditor/src/Editor/SceneRecovery.cpp:629-688`: `OnApplied` and the quiet timer; with `:61-77` (`IsStructural`) and `:754-767` (folding) |
| `editor-core:481` | figure | home | The recovery journal's file and its life |
| `editor-core:519` | figure | home | The Recover Unsaved Changes dialog after a crash, and the toast after an agent's forced `scene.open` |
| `editor-core:569` | rule | home | Only `SceneRecovery` writes recovery files; every scene replacement goes through `ResetScene` |
| `editor-core:639` | hands-on | home | Exercise: recovery folding on paper, then a test |
| `new:52` | hands-on | home | Trace it yourself (D27): with a breakpoint in `SceneRecovery::OnApplied`, make one edit in a saved scene, wait two seconds, and find the `.strecovery` file under `<project>/.strata/Recovery` that the quiet timer's job wrote. Evidence: `StrataEditor/src/Editor/SceneRecovery.cpp:629-688`, `:867` |
| `editor-core:709-712` | term | home | Recovery journal, base hash, structural step, discarded (recovery) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The undo stack, its observers and `EntityState` | `editor/undo` | must |
| `ResetScene`, background saves and the recovery token | `editor/saving` | must |
| SHA-256 and other hashes | `basics/data-formats` | must |
| I/O jobs | `core/jobs` | must |
| Process ids and their reuse | `core/platform` | helps |
| Opening a scene in the background (`BeginOpenScene`) | `editor/projects` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `base-hash` | Base hash | - |
| `discarded-recovery` | Discarded (recovery) | - |
| `recovery-journal` | Recovery journal | - |
| `structural-step` | Structural step | - |

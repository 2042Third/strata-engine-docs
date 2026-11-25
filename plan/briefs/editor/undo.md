# Brief: `editor/undo`

| Field | Value |
| --- | --- |
| Title | Undo and redo |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `editor/commands`, `world/serialization` |
| From | editor-core ch. 3 (`EditorAction`, `UndoStack`, `SceneEditTransaction`, `ApplyEntities`, merging, groups, save points; four approaches compared) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/undo` — Undo and redo

**Covers.** The problem: every edit, by a person or an agent, must be reversible in one step per action, whether it
touched one value, a hundred entities or a file on disk. Four approaches are compared with a table of their costs:
command objects that write their own inverse, the memento (state before and after), transaction buffers that serialize
the touched objects (Unreal's transactions, Unity's `Undo.RecordObject`), and persistent data structures. Strata's
choice: mementos at the grain of an entity for the scene, and polymorphic `EditorAction`s for files, documents and
settings. The history comes first, on a toy undo stack of integers taken from `UndoStackTests.cpp`: `EditorAction` (an
`Undo` that may fail with a reason and change nothing, `MergeWith`, `IsNoOp`, `ChangesScene`, `GetSceneChange`);
`UndoStack::Push` (the redo branch dropped, continuous edits merged until `BreakMerge`, a merged no-op dropped, the
capacity of 512 trimmed); the different failure rules of undo (the step stays) and redo (it and every later step go);
the save point and the modified flag (only steps that change the scene count, and a trim or a dropped redo branch makes
the save point unreachable); serials and generations; action groups that apply all or nothing, and the open group a
batch uses; the observer that the recovery journal and worlds listen with. Then the scene: why undo recreates entities
with the same UUID; `EntityState`; `SceneEditTransaction` (track before you change, track created entities after you
create them, `TrackSubtree` before you delete; commit only when something changed; rollback); `SceneEditAction` with its
shared, immutable states and its merge rule; `SceneEdit::ApplyEntities`, the central algorithm (one destroy batch, one
recreation with the same UUIDs, component differences, one placement batch per changed sibling list, and why every
recorded entity of a changed list is placed); names in steps ("Create 'Wall'", `QuoteName`, `MakeNameUnique`);
`SceneSettingsAction`. `CommitEdit` is the one gate (refused while playing, rolled back while a scene opens; the
upkeep of worlds and prefabs is named and linked); `FinishEdit` and `RollBackEdit` end a command; `entity.create` and
`entity.delete` show the tracking; `SetPropertyWithUndo` gives the inspector's continuous edits a merge key per entity,
component and property; `AssetDocumentAction` is the example of a step that does not change the scene. `edit.undo`,
`edit.redo` and `edit.history` close the page. The running example: a parent with two children is deleted and undone, and
a dragged value becomes one step. Exercises: run `Editor.Undo` and add a test that a merged drag, a save and another drag
give two steps; write an undo step for an asset rename whose undo checks its precondition; trace the undo of a deleted
parent through the three batches of `ApplyEntities`. Afterwards the reader can add an undo step of either kind and
predict what the history does with it.

**Leaves out.**

- Saves under concurrent edits, `SavePoint` as a background save uses it → `editor/saving`
- How the recovery journal follows the history → `editor/recovery`
- Undo steps of files and the trash → `editor/trash-references`
- Override upkeep inside `CommitEdit` → `editor/prefab-instances`
- Re-celling and cells in undo steps → `editor/worlds`
- The sibling index and the hierarchy's order → `world/scene-graph`
- The gizmo's drag (`TransformDrag`) → `editor-ui/scene-view`
- Undo and redo as a game maker uses them → `make/project-files`

**Fit.** `fits`: about 9,150 words against XL (8,000). Counted again from the sections, with the trace exercise: eleven
excerpts (the toy among them) and eighteen features take the most, beside three concepts, four figures, four rules and
four hands-on.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:307` | concept | home | Stable identity: undo, prefabs, replays and recovery recreate entities with the same UUID |
| `editor-core:310` | concept | home | Undo and redo: the four approaches, Strata's choice, merging, groups and failure |
| `editor-core:319` | concept | home | The modified flag as a save point in the history |
| `editor-core:103-106` | feature | home | `EditorAction`, `UndoStack`, the failure rules, the save point and the modified flag |
| `editor-core:108-114` | feature | home | Action groups, groups for batches, the observer, `EntityState`, `SceneEditTransaction`, `SceneEditAction`, `ApplyEntities` |
| `editor-core:116-120` | feature | home | Names in steps, `SceneSettingsAction`, `CommitEdit`, `FinishEdit` and `RollBackEdit`, `PropertyEdit` |
| `editor-core:122` | feature | home | `AssetDocumentAction`: a step that does not change the scene |
| `editor-core:124` | feature | home | `edit.undo`, `edit.redo`, `edit.history` |
| `editor-core:121` | feature | use | `TransformDrag` as an example of a merge key that ends with the drag |
| `editor-core:115` | feature | link | Steps that touch an unloaded world cell; `editor/worlds` has them |
| `editor-core:387` | code | home | `StrataEditor/src/Editor/Commands/EntityCommands.cpp:170-218`: `entity.create` and `entity.delete`, `TrackCreated`, `TrackSubtree`, `RollBackEdit` |
| `editor-core:393` | code | home | `StrataEditor/src/Editor/UndoStack.h:27-56`: `EditorAction`, the undo interface with failure and merge |
| `editor-core:395` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:48-106`: `UndoStack::Push`, the central algorithm of the history |
| `editor-core:397` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:156-221`: `Undo` and `Redo` with their different failure rules |
| `editor-core:398` | code | home | `StrataEditor/src/Editor/UndoStack.cpp:278-311`: `GetSavePoint`, `MarkSaved(point)`, `IsModified` |
| `editor-core:399` | code | home | `StrataTests/src/Editor/UndoStackTests.cpp:14-69`: the toy `AddAction`; with `:262-374`, the tests of merging, no-op drop and save points |
| `editor-core:401` | code | home | `StrataEditor/src/Editor/SceneEdit.h:21-37`: `EntityState`; with `:132-169`, the `SceneEditTransaction` API |
| `editor-core:403` | code | home | `StrataEditor/src/Editor/SceneEdit.cpp:187-281`: `ApplyEntities`, the central algorithm of scene undo |
| `editor-core:406` | code | home | `StrataEditor/src/Editor/SceneEdit.cpp:351-363`: the merge rule; with `:388-463`, the transaction's capture and commit |
| `editor-core:408` | code | home | `StrataEditor/src/Editor/PropertyEdit.cpp:135-155`: `SetPropertyWithUndo`, the inspector's path and its merge key |
| `editor-core:410` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1875-1891`: `CommitEdit`, the one gate |
| `editor-core:470` | figure | home | The undo stack's state: entries, serials, position, save point, merge flag |
| `editor-core:472` | figure | home | The flow of a `SceneEditTransaction` |
| `editor-core:474` | figure | home | `ApplyEntities` in three batches, on a small hierarchy whose positions agree by chance |
| `editor-core:515` | figure | home | `edit.history` or the Edit menu with named steps |
| `editor-core:548` | rule | home | Track before you change; track created entities after you create them; `TrackSubtree` before deleting |
| `editor-core:552` | rule | home | Give continuous edits a merge key and break the merge when the drag ends |
| `editor-core:554` | rule | home | Undo can fail; design for it |
| `editor-core:556` | rule | home | Steps that do not change the scene say so (`ChangesScene() == false`) |
| `editor-core:623` | hands-on | home | Exercise: read the undo tests and add one for merge and save point |
| `editor-core:631` | hands-on | home | Exercise: a non-scene undo step whose undo checks its precondition |
| `new:51` | hands-on | home | Trace it yourself (D27): delete a parent with two children with `entity.delete`, then run `edit.undo` with a breakpoint in `ApplyEntities`, and name its destroy batch, its recreation with the same UUIDs and its placement batch as they run. Evidence: `StrataEditor/src/Editor/SceneEdit.cpp:187-281`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:170-218` |
| `editor-core:671-684` | term | home | Undo step, history, redo branch, merge and merge key, no-op step, break the merge, action group, serial, save point, generation, memento, `EntityState`, scene edit transaction, rollback |
| `editor-core:685` | term | link | Sibling index, homed on `world/scene-graph`; the page names it where `ApplyEntities` places a changed sibling list |
| `editor-ui:762` | term | home | Undo merge: a drag's many changes combined into one step; one home with `editor-core:674` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands, `Execute` and how a command ends | `editor/commands` | must |
| Entities, components and UUIDs as stable identities | `world/ecs` | must |
| The hierarchy: parents, children, sibling order, changes through `Scene` | `world/scene-graph` | must |
| Components written as JSON; scene documents | `world/serialization` | must |
| Reflection: `ComponentInfo`, `PropertyInfo` | `world/reflection` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| `unique_ptr` and `shared_ptr`, `Scope` and `Ref` | `basics/cpp-memory` | must |
| `std::deque` and the standard containers | `basics/cpp-generic` | must |
| A doctest test case | `core/first-change` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `entitystate` | `EntityState` | - |
| `action-group` | Action group | - |
| `break-the-merge` | Break the merge | - |
| `generation-editor` | Generation (editor) | - |
| `memento` | Memento | - |
| `merge-editor` | Merge (editor) | merge key |
| `no-op-step` | No-op step | - |
| `redo-branch` | Redo branch | - |
| `rollback` | Rollback | - |
| `save-point` | Save point | - |
| `scene-edit-transaction` | Scene edit transaction | - |
| `serial` | Serial | - |
| `snapshot-editor` | snapshot (editor) | - |
| `undo-merge` | Undo merge | - |
| `undo-stack` | Undo stack | - |
| `undo-step` | Undo step | - |

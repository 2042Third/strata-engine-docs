# Brief: `editor/trash-references`

| Field | Value |
| --- | --- |
| Title | The trash and references |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/undo`, `assets/references` |
| From | editor-core ch. 6 (asset file actions, reference checks, undo steps that check their preconditions) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/trash-references` — The trash and references

**Covers.** The problem: a person deletes a material three scenes use, or an agent moves a texture, and undo must bring
the file back with the same handle, or refuse because something else now lives at that path. The naive answers are
`std::filesystem::remove`, and a delete that never asks who uses the asset. The idea: files are part of the history too;
deletes go to a trash, references are checked first (including unsaved uses in memory), handles are kept, and an undo
step checks its preconditions before it touches a file. Strata's code: the `AssetFileAction` family (trash, move, create,
create folder), steps that never change the scene and hold the asset manager weakly; `asset.delete` and
`asset.deleteFolder`, which move the file, its `.meta` and its cached import to `<project>/.strata/Trash` for 30 days,
undo restoring the handle; `AssetReferences::Find`, which joins the index of recorded referencers, a walk of the edited
scene in memory and the project's own references (start and loading scenes, icon, settings), and puts `referencedBy`
into the error's data; the preconditions (undo fails when something else is at the path; redo runs only when the path
still holds exactly those assets and the delete would be allowed now); deletes by agents and scripts are announced to the
person, the person's own are not; moves and trash refuse files that a save is writing; and the source scan that fails
any panel which writes, moves or removes a file. The example deletes a material the open scene uses (refused, with the
users listed), deletes an unused texture and undoes it (same handle), then moves it and tries an undo after a new file
took the old path. The trace exercise finds which of the three sources of `AssetReferences::Find` named the material's
user. Afterwards the reader can add a file operation that is undoable and never overwrites.

**Leaves out.**

- The reference graph, closures and prefetch → `assets/references`
- Handles and `.meta` files → `assets/handles-meta`
- The Delete Asset dialog as it is drawn → `editor-ui/launcher-dialogs`
- Document claims of a save → `editor/saving`
- Deleting and undoing as a game maker does it → `make/assets`

**Fit.** `over`: about 4,700 words against M (3,000). Counted again from the sections, with the trace exercise: one
concept, eight features, three excerpts and the shape of an internals page pass M's top; the next size is L (5,000)
(S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:338` | concept | home | Files are part of the history: trash, references checked first, handles kept, undo that re-checks |
| `assets:141` | feature | home | The asset manager's file operations the steps call: moves, the trash and its restore, the purge after 30 days; handles survive |
| `editor-core:160-166` | feature | home | The file actions, delete to trash, the reference check, preconditions, announced agent deletes, files a save writes, panels never touch files |
| `editor-core:427` | code | home | `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-939`: `asset.delete` with `referencedBy` and its trash step; with `AssetFileAction.cpp:94-107` (trash and restore as a step) |
| `new:9` | code | home | `StrataEditor/src/Editor/AssetFileAction.cpp:62-92`: `CheckRedo`, a redo that runs only while the path still holds what it deleted |
| `new:10` | code | home | `StrataEditor/src/Editor/AssetReferences.h:19-77`: the referencers and `Find`, the index, the scene in memory and the project |
| `editor-core:484` | figure | home | An asset delete with the trash and its undo |
| `editor-core:521` | figure | home | The delete refusal listing the users, and the toast of an agent's delete |
| `assets:513` | figure | home | A delete refused with its `referencedBy` list, then the restore by undo; one picture with `editor-core:521` |
| `assets:628` | hands-on | home | The example: a safe delete, a forced one, and its undo |
| `new:54` | hands-on | home | Trace it yourself (D27): run `asset.delete` on a material the open scene uses, with a breakpoint in `AssetReferences::Find`, and name which of its sources (the index of recorded referencers, the edited scene in memory, the project's own references) found the user. Evidence: `StrataEditor/src/Editor/AssetReferences.h:19-77`; `StrataEditor/src/Editor/AssetReferences.cpp:162`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-939` |
| `editor-core:544` | rule | home | Panels never write, move or remove files |
| `editor-core:713-714` | term | home | Trash, referencer |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Undo steps, their failure rules and `ChangesScene` | `editor/undo` | must |
| References an asset records and the reference graph | `assets/references` | must |
| Asset handles and `.meta` files | `assets/handles-meta` | must |
| Weak references (`weak_ptr`) | `basics/cpp-memory` | helps |
| Files a save claims | `editor/saving` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `referencer` | Referencer | Referencers |
| `trash` | Trash | - |

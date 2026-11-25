# Brief: `start/how-to-read`

| Field | Value |
| --- | --- |
| Title | How to read this book |
| Kind | H |
| Size | M |
| Tracks | G, E, B |
| Needs | - |
| From | new; the tracks, the kinds of page, the strips, the conventions, the engine version; the map of the book (tracks and Needs, generated from the front matter; curricula 5.1.4); "How to read a command" (JSON, and that the command tab is optional on game-maker pages); "How to read code you do not understand yet" |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/how-to-read` — How to read this book

**Covers.** The goal: read any page of the book and follow it, and know where to go next. What must be true first:
nothing but the book's site. The steps act on the site itself. First the reader finds the track badges at the top of
the page, chooses a track (G, B or E, as `start/welcome`'s doors chose), and finds the track's "next page" link; side
steps and Test out boxes are named. Then the top strip: the kind badge and what each of the six kinds answers, in one
table; the level; "After this page you can" and "Before you start" (the Needs, an alternative shown as "X or Y"); the
engine release and commit the book is written against, and what a reader with another release should expect. Then the
map of the book, drawn from the pages' front matter, opened and read for one page's Needs. Then the conventions, each
with one small example: UI labels in bold, menus as **Menu ▸ Item**, the tab sets "In the editor" and "With a command",
and "Windows", "Linux" and "macOS"; a step's "You should see" and "If you do not see it"; checkpoints; asides; and the
glossary marks with their popovers. One sentence says what the reader may do with the book's code: use the code and
the project files the book gives in their own programs and games, and ship them, with a link to `appendix/credits`,
which states the permission in full. Then the two skills the outline names. "How to read a command": a command is a
name, `<group>.<action>`, and its parameters as JSON; JSON is taught here as a reader reads it (objects of named values
in braces, lists in brackets, strings in quotes, numbers, `true` and `false`), the first use that `book.md` gives this
page, with the term linked once to its home, `basics/data-formats`; the example is the command behind a click
the reader makes in `start/first-game`, the Hierarchy's **+ ▸ Cube** (`entity.create` with a name and two components);
the command tab is optional on game makers' pages, whose editor tab is complete; and a line a page gives to run a
command is pasted into a terminal while the editor runs (`StrataCLI call <command> @params.json`, or `-` with the JSON
on standard input, because PowerShell drops the quotes inside a JSON argument), with a link to `start/install` for the
terminal itself. "How to read code you do not understand yet": source code, a programming language (C++ for the
engine and the scripts), a comment and pseudocode are defined in a sentence each; then the excerpt's label (file and
lines at the pin, or a sketch's or pseudocode's label), the sentence before a fence that says what to look for,
comments, names that say what they do, and permission to skip what the page does not ask about; the example is the
first lines of the `Spinner` script that `start/first-game` changes. Two exercises, answered (the page comes before
`start/install`): the reader reads an `entity.create` command's JSON and says what it makes, and follows one page's
Needs on the map back to the start of a track. At the end the reader can choose a track and follow its links, read
every part of a page's strips, read a step in either tab, read a command's JSON and a short code excerpt, and find a
word in the glossary.

**Leaves out.**

- The axes, units and symbols the later parts use → `reference/notation`
- Opening a terminal, changing folder and running a program → `start/install`
- Running commands from the editor's side, and every command → `make/commands`, `reference/commands`
- Why every click is a command, and how the commands are registered → `editor/commands`
- Text encodings and UTF-8, the bytes under a JSON text → `basics/bytes`
- JSON in full, and reading it into tokens → `basics/data-formats`
- The book's licence, the permission in full, and the credits → `appendix/credits`
- Reading C++ itself → `basics/programming-1`
- Every term of the book → `reference/glossary`, `reference/term-index`

**Fit.** `fits`: about 3,800 words against M (3,000). Seven steps on the site for B0, each with its "You should see"
and "If you do not see it", with the table of kinds and the conventions' examples, take about 1,450 words, and the two
skills (JSON from zero with the `entity.create` example, the code-reading skill with `Spinner`) about 1,100; the page
stands near M's top, with little room for more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:3` | concept | home | The tracks G, B and E: their badges ("Game maker", "Beginner", "Engine builder"), the "next page" and "previous page" links, side steps (`basics/tools`, `basics/math-vectors`) and the Test out boxes of primers; the plan asks for it in `book.md`, "Tracks", and `tracks.md`. General knowledge. |
| `new:4` | concept | home | The six kinds of page and what each answers; the top strip (kind and track badges, the level, the time, "After this page you can", "Before you start", the engine release and commit) and the bottom strip (Summary, Check yourself, Exercises or Practice, Where it lives in Strata, Further reading); the plan asks for it in `book.md`, "Kinds of page", and `style.md` §6. General knowledge. |
| `new:5` | concept | home | The engine release the book targets and the commit it is written against, shown in every top strip as values, never typed, and what a reader with another release should expect; the plan asks for it in `README.md`, decision 8, and `style.md` §13. General knowledge. |
| `new:6` | concept | home | The map of the book: the tracks and the Needs, generated from the pages' front matter (curricula 5.1, principle 4), read for one page; the plan asks for it in the outline's From of this page. General knowledge. |
| `new:7` | concept | home | The conventions: UI labels in bold, menus as **Menu ▸ Item**, the tab sets of editor and command and of the three systems, "You should see" and "If you do not see it", checkpoints, asides, glossary marks; the plan asks for it in `style.md` §3, §10 and §12. General knowledge. |
| `new:8` | concept | home | How to read a command: its name `<group>.<action>`, its parameters as a JSON object, its result as JSON; a line to run one is `StrataCLI call <command>` with the JSON from a file (`@params.json`) or from standard input (`-`), while the editor runs, because PowerShell drops the quotes inside a JSON argument. Evidence: `StrataCLI/src/CLI/CliApplication.cpp:573-588` (the usage of `call`); `.claude/skills/strata-editor-automation/SKILL.md:46-60` |
| `new:9` | concept | home | JSON as a reader reads it: objects of named values in braces, lists in brackets, strings in quotes, numbers, `true` and `false`; `book.md` names this page the first use of reading a command's JSON, and the term is linked once to its home, `basics/data-formats`. General knowledge. |
| `new:10` | concept | home | How to read code you do not understand yet: source code, a programming language, a comment and pseudocode defined in a sentence each (the seed's terms of this page); the excerpt's label, the sentence before the fence, comments, telling names, and skipping what the page does not ask about; the outline's From names it. General knowledge. |
| `new:22` | concept | link | The book's code is the reader's to use: one sentence says that the code and the project files the book gives may be used in the reader's own programs and games and shipped, and links `appendix/credits`, which states the permission; the plan asks for it in `critique/rulings-6.md`, R21. General knowledge. |
| `new:23` | hands-on | home | Two exercises, answered (the page comes before `start/install`, `style.md` §8): **Basic.** an `entity.create` command with a name, `"parent": null` and a `Transform` component's `Translation` is read, and the reader says what it makes, which values are strings, numbers, lists and objects, and what its result holds (the new entity's `id`); **Medium.** one page's "Before you start" is followed on the map of the book back to the first page of a track. Evidence: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:170-194` (`entity.create`: `name`, `parent`, `components`, and the result `id`) |
| `editor-core:299` | concept | use | Every click in the editor runs a command, and the same command can be typed: one sentence; the home is `editor/commands`, the use home `make/editor-tour` |
| `gamedev:366` | code | use | The command behind the Hierarchy's **+ ▸ Cube**: `entity.create` with a name and the components `MeshRenderer` and `BoxCollider`, shown only as the JSON a command tab holds; the code is `editor/commands`' |
| `gamedev:655` | term | use | Command, defined in plain words for the command tab; the entry also defines command script, `expect`, `until` and `bind`, whose page is `make/automated-playtests`; the glossary step homes "editor command" on this page, beside the seed's "terminal command" (start-q6) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor, the program in which games are made | `start/welcome` | helps |
| The three doors and their tracks | `start/welcome` | helps |
| Opening a terminal and pasting a line into it, for running a command | `start/install` | helps |

**Starting state.** No project and no installed Strata: the steps act on the book's site only.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `comment` | comment | - |
| `engine-release` | engine release | - |
| `prerequisite` | prerequisite | - |
| `primer` | primer | - |
| `programming-language` | programming language | - |
| `pseudocode` | pseudocode | - |
| `reading-track` | reading track | - |
| `source-code` | source code | code |
| `tutorial-checkpoint` | tutorial checkpoint | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-start-1 | must | stale-item | `new:8` on `start/how-to-read` | The line the page gives to run a command, `StrataCLI call <command> @params.json`, does not run as pasted. In Windows PowerShell an unquoted `@params.json` is a parse error (the `@` is the splatting operator). `StrataCLI` is no command of any terminal: it is a program in the Strata folder, run from there as `.\StrataCLI` or `./StrataCLI`. A params file written with PowerShell 5's `>` is UTF-16, which StrataCLI refuses. The page never says what StrataCLI is. | `new:8` gives the line in OS tabs, run from the Strata folder: `.\StrataCLI call <command> '@params.json'` in PowerShell (the quotes keep the `@`), `./StrataCLI call <command> @params.json` in a POSIX shell, and the form with the JSON piped into `call <command> -`. The file is written as UTF-8 with the code editor. StrataCLI is defined in one sentence: the program in the Strata folder that sends one command to the running editor and prints its JSON result. About 120 words. | `allocation/start.md:78`, `:116`; `StrataCLI/src/CLI/CliApplication.cpp:126-160` (`@<file>`, `-`, UTF-16 refused), `:605` (the newest running editor); `Docs/Releases/PackageReadme.md:17`; `.claude/skills/strata-editor-automation/SKILL.md:56-60`; run here in Windows PowerShell 5.1: `cmd /c echo @params.json` fails with the ParserError SplattingNotPermitted, `cmd /c echo '@params.json'` prints `@params.json` |
| critic-start-12 | should | shape | `start/how-to-read` | The page is a how-to, and its list cannot fill two sections of that shape: `## Result` and `## Variations`. The site gives the variations a reader needs: the search, the print view of a part (for printing or a PDF from the browser), and the archived versions of the book, which a reader with another release opens. The Covers' "what a reader with another release should expect" leads there and stops. | Covers adds `## Result` (the chosen track, its next page, the map read for one page) and `## Variations` with the three, as new items (feature; `General knowledge.`, naming `site.md`). About 200 words. The page then stands at about 4,100 words, over M's top: it takes L by S2 in the second size pass. | `allocation/start.md:61-88`, `:102-105`; `style.md:535-541`; `site.md:149`, `:328`, `:453-457` |
| critic-start-14 | should | missing-item | `start/first-game`; `new:7` on `start/how-to-read` | On macOS every Ctrl shortcut of the editor is pressed with Cmd, because ImGui swaps the two keys on Apple builds, while the menus still print "Ctrl+B" and "Ctrl+S". The rows give Ctrl+B and Ctrl+Z only, and the conventions of `start/how-to-read` do not warn that a Mac's menus name another key than the one to press. | The keys of `start/first-game` (Ctrl+B, Ctrl+Z, and Ctrl+S with critic-start-2) carry **Cmd** for macOS, as `style.md` §9.2 asks. `new:7` adds one sentence: on a Mac the editor's menus say Ctrl, and the key to press is Cmd. About 30 words. | `allocation/start.md:115`, `:240`, `:247`, `:253`; `Strata/vendor/imgui/imgui.cpp:1731-1735`, `:1933-1942`; `StrataEditor/src/EditorLayer.cpp:983`, `:1591`; `allocation/editor-ui.md:868`; `style.md:685-686` |
| critic-start-16 | could | stale-item | `gamedev:366` on `start/how-to-read` | The command behind **+ ▸ Cube** has three components, not two: besides `MeshRenderer` and `BoxCollider` it holds `Transform` with the `Translation` where the view looks. The JSON shown would not match what the editor runs. | The Covers and the row say "a name and three components (`MeshRenderer`, `BoxCollider`, and `Transform` with its place)". No words added. | `allocation/start.md:76`, `:122`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-77`, `:132-144` |

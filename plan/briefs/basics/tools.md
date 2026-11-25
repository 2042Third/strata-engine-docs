# Brief: `basics/tools`

| Field | Value |
| --- | --- |
| Title | The tools: the terminal, files and a code editor |
| Kind | P |
| Size | M |
| Tracks | B, E |
| Needs | `start/install` |
| From | new (curricula 1.0, 1.1); it assumes nothing of `basics/computer`, because it is a side step of track G; the terminal (folders and paths, running a program with arguments, quoting paths, PowerShell's `\| Write-Output`), exit codes and the standard streams, the user data folder, environment variables, a code editor; git is `basics/git`'s |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/tools` — The tools: the terminal, files and a code editor

**Covers.** The page assumes nothing of `basics/computer`, because track G takes it as a side step before
`make/first-script`, and its first line says that `make/first-script` needs only the sections on the terminal and the
code editor. The terminal: a terminal and the shell inside it (PowerShell, bash, zsh), a command line as a program's
name followed by words. Folders and paths written as text: absolute and relative paths, `~`, `.` and `..`, the
separators `\` and `/`, file extensions and hidden files and folders (the project's `.strata/`). The current folder:
`cd`, listing a folder, running a program of the current folder (`./`, `.\`). Arguments and options: `--version`,
`--help`, an option with a value, a path with spaces in quotes; a command line with options as the reference pages
print them. The standard streams: standard input, output and error; sending output to a file (`>`, `2>`), and a pipe
`|` that joins two programs. Exit codes: 0 when a program worked, another number when it did not, read with `$?` or
`$LASTEXITCODE`; Strata's codes are named with a link to `core/first-frame`. PowerShell waits for a windowed program
only when its output is piped: `.\StrataEditor --version | Write-Output` (the reason is `core/platform`'s).
Environment variables: named texts that each process carries and passes to the processes it starts, read and set for
one command in PowerShell and in a POSIX shell, `PATH` and how a shell finds a program; the example is
`STRATA_EXTERNAL_EDITOR`. The user data folder (`%LOCALAPPDATA%`, `~/.local/share`, `~/Library/Application Support`)
with the editor's log in it. Permissions as a user meets them: read-only files, files only you may change, the
executable bit (`chmod +x`), administrator rights and `sudo`. Files of commands: a shell script (`.sh` for bash, `.ps1`
for PowerShell) that stops at the first command that fails, and running a Python tool from a terminal
(`python Tools/<tool>.py --help`). A code editor: open a folder, IntelliSense, search across files, the terminal
inside the editor (VS Code or Visual Studio, as `start/install` installed them). Every command is shown in PowerShell
and in a POSIX shell, in OS tabs where they differ. The Test out box asks the reader to work out a relative path from
a current folder, to predict where `>` and `|` send a program's output, and to read an exit code. The Practice runs in
a terminal on a project folder and changes nothing in it: list the folder with its hidden files and find `.strata/`,
print the editor's version (with `| Write-Output` in PowerShell) and read its exit code, find the editor's log in the
user data folder and print its last lines, and search the folder's files in the code editor.

**Leaves out.**

- Opening a terminal for the first time on each OS → `start/install`
- What a process is inside the computer → `basics/computer`
- Strata's exit codes and how an interrupt sets 130 → `core/first-frame`, `core/platform`
- Why PowerShell does not wait for a windowed program → `core/platform`
- Version control: repositories, commits, branches, submodules and worktrees → `basics/git`
- Building C++ with CMake from a terminal → `basics/build`
- Building Strata from source → `core/first-change`, `engineering/building`

**Fit.** `over`: about 4,350 words against M (3,000). The twelve ideas of the terminal and the code editor with their
OS tabs take about 3,250 words at B0's length, and the primer's fixed parts with the Test out box and the Practice
about 1,100. The next size is L (5,000), which a primer may take (S2), and the page stays the one lesson that track G's
side step and `make/first-script` need.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:16` | concept | home | A terminal, the shell inside it (PowerShell, bash, zsh), and a command line as a program's name and words. General knowledge. |
| `new:17` | concept | home | Paths as text: absolute and relative, `~`, `.` and `..`, the two separators, file extensions, hidden files and folders. General knowledge. |
| `new:18` | concept | home | The current folder, `cd`, listing a folder, running a program of the current folder (`./`, `.\`). General knowledge. |
| `new:19` | concept | home | Arguments and options, an option with a value, quoting a path with spaces; the editor's `--version`, `--help` and `--headless` as examples. Evidence: `Docs/Releases/PackageReadme.md:77-81` |
| `new:20` | concept | home | The standard streams, sending output to a file (`>`, `2>`), and pipes between programs. General knowledge. |
| `new:21` | concept | home | Exit codes: 0 for success, other numbers for failure, read with `$?` and `$LASTEXITCODE`. General knowledge. |
| `new:22` | concept | home | PowerShell waits for a windowed program only when its output is piped: `.\StrataEditor --version \| Write-Output`. Evidence: `Docs/Releases/PackageReadme.md:80-81` |
| `new:23` | concept | home | Environment variables: inherited by child processes, read and set for one command, `PATH`; `STRATA_EXTERNAL_EDITOR` as the example. Evidence: `StrataEditor/src/Editor/ExternalEditor.cpp:25` |
| `new:24` | concept | home | The user data folder on each OS, with the editor's log `Strata/Logs/StrataEditor.log` in it. Evidence: `Docs/Releases/PackageReadme.md:75-77` |
| `new:25` | concept | home | Permissions as a user meets them: read-only files, files only you may change, the executable bit, administrator rights and `sudo`. General knowledge. |
| `new:26` | concept | home | Shell scripts (`.sh`, `.ps1`) that stop at the first failing command; running a Python tool from a terminal. General knowledge. |
| `new:27` | concept | home | A code editor: open a folder, IntelliSense, search across files, its own terminal. General knowledge. |
| `new:205` | hands-on | home | Practice in a terminal on a project folder, changing nothing: its hidden `.strata/` folder listed, the editor's `--version` printed (piped in PowerShell) and its exit code read, the editor's log found in the user data folder and its last lines printed, the folder searched in the code editor. Evidence: `Strata/src/Strata/Project/Project.h:109`, `Docs/Releases/PackageReadme.md:75-81` |
| `automation:768` | term | home | stdin, stdout, stderr: a process's standard streams |
| `foundation:626` | term | home | Exit code, in general; Strata's 0, 1, 3 and 130 are named with a link |
| `foundation:51` | feature | link | Strata's exit codes, linked to `core/first-frame` |
| `foundation:313` | concept | link | Why PowerShell does not wait for a windowed program, linked to `core/platform` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Opening a terminal, changing folder and running a program, per OS | `start/install` | helps |
| A process and its environment | `basics/computer` | helps |
| A code editor installed | `start/install` | must |

**Starting state.** No checkpoint: the Practice reads a project folder the reader already has and changes nothing in
it (on tracks B and G Coin Run's project as `make/lighting` leaves it, on track E the Basic 3D project of
`start/first-game`).

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `absolute-path` | absolute path | full path |
| `code-editor` | code editor | - |
| `command-line-argument` | command-line argument | - |
| `current-folder` | current folder | working folder |
| `environment-variable` | environment variable | - |
| `exit-code` | exit code | exit status |
| `file` | file | - |
| `folder` | folder | - |
| `path` | path | file path |
| `pipe` | pipe | - |
| `shell` | shell | - |
| `standard-error` | standard error | stderr |
| `standard-input` | standard input | stdin |
| `standard-output` | standard output | stdout |
| `stdio` | stdio | - |
| `terminal` | terminal | - |
| `terminal-command` | terminal command | shell command, command line |
| `user-data-folder` | user data folder | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-18 | should | missing-item | `basics/tools` | Terminal facts that later pages rely on are not on the page. Ctrl+C in a terminal stops the running program and does not copy; headless runs and `core/first-frame`'s exercises use it. `&&` joins two commands in a POSIX shell but is an error in Windows PowerShell 5.1, the PowerShell that Windows ships, and the scripts' `CMakeLists.txt` gives its build-by-hand line with `&&`, which `basics/build`'s Coin Run item runs. PowerShell reads `$env:LOCALAPPDATA`, not the `%LOCALAPPDATA%` the Covers writes. And the Covers runs `python Tools/<tool>.py`, but the release ships no `Tools` folder and no page installs Python. | Add Ctrl+C; joining commands (`&&` in bash and zsh; in Windows PowerShell 5.1 two lines, or `;` with a check of `$?`); and `$env:` beside `%...%` (about 180 words). The Python example says that the tools come with Strata's source on track E (`core/first-change`) and how Python is started on each OS. | `allocation/basics-a.md:95`, `:97-99`, `:1030-1031`; `Docs/Releases/PackageReadme.md:75-79`; `StrataEditor/src/Editor/ScriptProject.cpp:218`; `allocation/core.md:349`; `CMake/StrataPackaging.cmake:55-85` |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |

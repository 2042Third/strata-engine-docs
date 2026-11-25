# Brief: `basics/git`

| Field | Value |
| --- | --- |
| Title | Version control with git |
| Kind | P |
| Size | M |
| Tracks | B, E |
| Needs | `basics/tools` |
| From | new by split of `basics/tools`: track G's side step and track B's reading before `make/first-script` need no git (curricula 1.0); clone, submodules, branch, diff, commit, merges and conflicts, remotes and pushes, tags, patches, worktrees, and the `.gitignore` a new project gets; after `basics/debugging` because track B reads it after `make/project-coin-run`, which needs no git |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/git` — Version control with git

**Covers.** The page is read on track B after `make/project-coin-run` and on track E after `basics/debugging`, and it
needs only the terminal and the code editor of `basics/tools`. Version control, and git as the program that does it: a
repository and its history of commits; `git init` for a folder of one's own and `git clone` for someone else's
repository; submodules and `git submodule update --init --recursive --depth 1` as Strata's source needs it;
`git status`, `git diff`, staging with `git add` and `git commit` with a message; the `.gitignore` a new project gets
(`/.strata/`) and the one in its `Scripts` folder (`/CMakePresets.json`); branches, switching, merging and merge
conflicts; remotes, `git push`, `git pull` and tags; a patch as a diff saved to a file and applied with `git apply`;
searching with `git grep`, as the evidence of `appendix/not-in-strata` is written; a worktree as a second working folder
of one repository. Every command is shown in PowerShell and in a POSIX shell, in OS tabs where they differ. The Test out
box asks the reader to predict what `git status` shows after an edit and a `git add`, to read the markers of a merge
conflict, and to give the command that fetches Strata's submodules. The Practice runs git on a folder of the reader's
own and ends with the optional item on the reader's Coin Run: `git init` in the project's folder, `git status` with
`.strata/` kept out by the `.gitignore` the editor wrote, a first commit, the `Coin` script's `DegreesPerSecond` changed
and read with `git diff`, and a branch that changes it again and is merged back.

**Leaves out.**

- The terminal, paths and hidden folders → `basics/tools`
- Strata's branches, reviews and commits → `engineering/contributing`
- Building Strata from a clone → `core/first-change`, `engineering/building`
- How Strata pins its submodules and upgrades them → `engineering/third-party`
- What runs when a branch is pushed → `engineering/ci`

**Fit.** `fits`: about 3,700 words against M (3,000). Six ideas from zero at B0's length, with the three places of a
change (the folder, the staging area, the history) and a branch's merge drawn (about 2,600), and the primer's fixed
parts with the Test out box, the Practice and the Coin Run item (about 1,100); branches, merges and conflicts take the
most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:28` | concept | home | Version control: a repository, its commits, `git clone`, submodules and the command Strata's source needs. Evidence: `AGENTS.md:54` |
| `new:29` | concept | home | `git status`, `git diff`, staging, `git commit` with a message. General knowledge. |
| `new:30` | concept | home | `.gitignore`: a new project ignores `/.strata/`, and its `Scripts` folder ignores `/CMakePresets.json`. Evidence: `Strata/src/Strata/Project/Project.cpp:198-200`, `StrataEditor/src/Editor/ScriptBuild.cpp:613-614` |
| `new:31` | concept | home | Branches, switching, merging and merge conflicts. General knowledge. |
| `new:32` | concept | home | Remotes, `git push`, `git pull` and tags. General knowledge. |
| `new:33` | concept | home | A patch (`git diff` saved, `git apply`), searching with `git grep`, and worktrees. General knowledge. |
| `new:206` | hands-on | home | Optional practice on Coin Run: `git init` in the project's folder, `git status` with `.strata/` kept out by the `.gitignore` the editor wrote when it made the project, a first commit, `DegreesPerSecond` changed and read with `git diff`, a branch merged back. Evidence: `Strata/src/Strata/Project/Project.cpp:198-200` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: the current folder, relative paths, hidden folders, running a program with arguments | `basics/tools` | must |
| A code editor, for a commit message and a file with a merge conflict | `basics/tools` | must |
| Coin Run's `Coin` script and its `DegreesPerSecond` field | `make/first-script` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts: Coin Run's project folder with the `.gitignore` the editor wrote when it made the
project, and no repository yet.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clone` | clone | - |
| `commit` | commit | - |
| `diff` | diff | - |
| `git` | git | - |
| `git-branch` | git branch | - |
| `repository` | repository | repo |
| `version-control` | version control | source control |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-5 | must | missing-item | `basics/git` | No page installs git or sets the identity that a commit needs. `start/install` installs the C++ tools and a code editor, not git; on Windows a plain terminal usually has no `git`, and on Ubuntu it is a package to add. The Practice's first `git commit` then stops with "Author identity unknown" until `user.name` and `user.email` are set. On track E, `core/first-change` clones Strata with git. | The page starts with `git --version`, the install per OS in tabs (Git for Windows; `sudo apt install git`; on macOS the Command Line Tools that `start/install` already installed), and the two `git config --global` lines before the first commit; one sentence on the line-ending warning that Git for Windows prints on `git add` (about 200 words; new items, General knowledge). | `allocation/start.md:155-160`; `allocation/basics-a.md:459-472`, `:491-497`; a search of the plan for "git config", "user.name" and "install git" finds nothing; `AGENTS.md:54` |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |

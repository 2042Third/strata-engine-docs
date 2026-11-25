# Notes: `basics/git`

## New terms

- staging area: a list of changes marked for the next commit; home `basics/git`; aliases: index.
- merge: to bring the commits of another branch into the current one; home `basics/git`.
- merge conflict: a clash where both branches changed the same line, which git leaves for the person to settle; home `basics/git`; aliases: conflict.
- remote: a copy of a repository kept somewhere else, known by a short name such as `origin`; home `basics/git`.
- tag: a fixed name for one commit; home `basics/git`.
- patch: a diff saved in a file; home `basics/git`.
- worktree: a second working folder of the same repository, with its own branch checked out; home `basics/git`.
- working folder: the files you edit, one of the three places of a change; home `basics/git`.

## Requests

- `tools/data/extra-words.txt`: `codebase` (the title of `core/reading-code`, linked in "Why you will need this").
- The word `worktree` (and `worktrees`) is the term proposed above; the lint reports it until the term is admitted.
- Figures: none requested. The page has two Mermaid diagrams (the three places of a change; two branches and a merge).
- Sketches: none. The commands are shown with output taken from a real run of git 2.52.0 in a scratch folder (hashes are
  those of that run; the `index` line of the `git diff` output is omitted and the page says so).
- `src/sidebar.json`: `basics/git` is in no track list, so pagecheck reports O5 for the page's tracks `[B, E]`. The
  sidebar is the planner's file.

## Not verified

- That `start/install` installs git: it does not (it only clones with git), so the page tells every reader to run
  `git --version` and gives the install per system. On macOS the page says the system offers its developer tools; that is
  general knowledge, not checked on a Mac.
- `winget install --id Git.Git -e` and the Git for Windows download page are general knowledge, not run on Windows here.
- Coin Run's `Coin` script with a field `DegreesPerSecond`: `make/project-coin-run` is not written at this pin; the
  Practice item names the script and field as the brief does and gives no file name.
- The project file's extension and a Coin Run project's exact folder list: the page names `Assets`, `Scripts`, the project
  file and `.gitignore` (`Strata/src/Strata/Project/Project.cpp` writes the folders and the `.gitignore`).
- That `core/first-change` and `core/frame-loop` use git as the "Where the book uses it" sentences say: the first
  names three commands of git; the second is linked because its Needs closure holds this page, and its sentence says only
  that its quotes come from the clone.
- The `index` line, hashes and the `ort` merge output are of git 2.52.0; older versions print other text.

## Findings not applied

- critic-basics-a-5: applied (git --version, install per system in tabs, the two `git config --global` lines, the
  line-ending warning). Not applied: "the Command Line Tools that `start/install` already installed", because
  `start/install` at the pin of the book does not install them.
- critic-basics-a-21: applied (a "Common mistakes" section with four mistakes: a commit without `git add`, conflict
  markers left in a file, build output committed, "Author identity unknown").

## Clerk

- Admitted: staging area, Merge (basics), merge conflict, Tag (git), Patch (basics), worktree. "Merge" and "patch" have other homes, so this page's meanings are qualified (R53).
- Aliases left out: "index" (the glossary's Index of `worlds/grids` holds it), "conflict" (one everyday word).
- Refused: "working folder": an alias of "current folder" (`basics/tools`), whose meaning differs from git's; the planner's.
- `extra-words.txt`: "codebase". Sidebar: see the clerk's report (O5).
- Not admitted, because the page check would then fail and the page is the writer's: remote (its paragraph would define 2 terms with clone (term-paragraph)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

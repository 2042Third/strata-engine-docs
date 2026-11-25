---
id: basics/git
title: "Version control with git"
description: "Keep every saved version of a folder with git: commits, branches, merges, remotes, patches and the files a project leaves out."
kind: primer
size: M
tracks: [B, E]
needs: [basics/tools]
time: 60
learn:
  - id: three-places
    text: explain the three places a change passes through, the working folder, the staging area and the history
  - id: commit-cycle
    text: run git status, git diff, git add and git commit on a folder of your own and predict what each prints
  - id: branch-merge
    text: create a branch, merge it and settle a merge conflict by reading its markers
  - id: share-code
    text: write the commands that clone a repository, fetch Strata's submodules, push, pull and tag
  - id: ignore-patch
    text: write a gitignore line, save a change as a patch, apply it and search a repository with git grep
status: final
---

::::test-out

1. You edit `settings.txt`, run `git add settings.txt`, and then edit the file a second time. What does `git status` list?

   :::answer{tests="three-places commit-cycle"}
   The file twice: under "Changes to be committed" with the first edit, which `git add` staged, and under "Changes not staged for commit" with the second edit. A commit now saves only the first edit.
   :::

2. After a failed merge, `settings.txt` holds the five lines below.

   ```text
   <<<<<<< HEAD
   speed = 100
   =======
   speed = 150
   >>>>>>> quick
   ```

   Which value does your own branch hold, and what do you do before you commit?

   :::answer{tests="branch-merge"}
   Your branch holds `speed = 100`, the lines above the `=======` line. Edit the file to the one value you want, delete the three marker lines, then run `git add settings.txt` and `git commit`.
   :::

3. Write the command that fetches the third-party libraries of a fresh clone of Strata.

   :::answer{tests="share-code"}
   `git submodule update --init --recursive --depth 1`.
   :::

4. The editor wrote a `.gitignore` into your project. Which line keeps the `.strata` folder out, and what does the first slash mean?

   :::answer{tests="ignore-patch"}
   `/.strata/`. The leading slash ties the rule to the folder that holds the `.gitignore`, so a folder named `.strata` deeper down is not meant.
   :::

5. You are on `main`. Write the two commands that create a branch named `slow` and move you back to `main`.

   :::answer{tests="branch-merge"}
   `git switch -c slow` creates the branch and moves you onto it; `git switch main` moves you back.
   :::

::::

## Why you will need this

Strata's source, its manual and your own games are folders of files that change every day. Git records those changes, so a mistake is never final. [Your first engine change](../core/first-change.md) clones the engine with git and commits its own change, and [Finding your way in a large codebase](../core/reading-code.md) searches the engine's files with `git grep`. If you make a game, git also lets you try a bold change to your project and undo it.

## Version control keeps every saved version

You change a script, the game breaks, and you want yesterday's file. Without a tool you copy the folder before each change: `Coin Run`, `Coin Run copy`, `Coin Run final 2`. After a week there are eleven copies, nobody remembers what differs between them, and two of them each hold one fix that the others lack.

**Version control** is a program that keeps every saved version of a folder's files, each with a note of what changed and why. You can compare two versions and return to an old one.

**Git** is the version control program that Strata uses, and most game projects use it too. Its name is also the command you type: every git command starts with the word `git`.

A **repository** is a folder that git watches, together with the record git keeps of it in a hidden folder named `.git`. Never edit `.git` by hand.

Each saved version is a **commit**: the state of all the files, a message you write, who saved it and when, and which commit came before it. The chain of commits is the repository's history.

## Install git and tell it who you are

Check whether git is installed. In a terminal, run this command:

```sh
git --version
```

The command prints a line such as `git version 2.52.0`. If the terminal answers "command not found", or in PowerShell "is not recognized", install git for your system.

::::tabs{sync=os}
:::tab[Windows]

Install Git for Windows from [the Git for Windows download page](https://git-scm.com/download/win), or run this command in PowerShell:

```powershell
winget install --id Git.Git -e
```

Then open a new terminal: a terminal that was already open does not know the new program.
:::
:::tab[Linux]

On Ubuntu, install the package:

```sh
sudo apt install git
```

Other distributions name the same package `git` in their package tool.
:::
:::tab[macOS]

Run `git --version` in the Terminal program. If git is missing, macOS offers to install Apple's developer tools, which include git; accept the offer and run the command again.
:::
::::

Every commit records its author, so git needs a name and an email address before the first commit. Without them the commit stops with "Author identity unknown". The address can be any address you choose, but a public site shows it.

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

`--global` stores both lines once in your user's settings, for every repository on this computer. On Windows, `git add` may later print a warning about line endings, such as `LF will be replaced by CRLF`. The warning is not an error: Windows and Linux end a line of text differently, git is converting between the two, and the command still works.

## Three places hold a change

A change passes through three places. The files you edit are the **working folder**. When you decide that a change belongs in the next commit, you copy it into the **staging area**, a list of changes that are marked for the next commit. A commit then saves everything in that list into the history.

```mermaid caption="A change starts in the working folder, moves to the staging area when you add it, and enters the history when you commit." alt="Three boxes in a row. The working folder leads by an arrow labelled add to the staging area. The staging area leads by an arrow labelled commit to the history."
flowchart LR
    W["Working folder: the files you edit"] -- "git add" --> S["Staging area: marked for the next commit"]
    S -- "git commit" --> H["History: saved commits"]
```

Create a folder, make it a repository and look at it. PowerShell and the shells of Linux and macOS run these commands unchanged.

```sh
mkdir settings-demo
cd settings-demo
git init -b main
```

`git init` turns the :term[current folder]{id=current-folder} into a repository; `-b main` names its first line of commits `main`. Git answers that it created an empty repository. Now create `settings.txt` in your :term[code editor]{id=code-editor} with these four lines, then ask git what it sees.

```text
speed = 90
jump = 5
gravity = 9
lives = 3
```

`git status --short` prints one line per changed file. The two letters before the name are two columns: the left one compares the staging area with the last commit, the right one compares the working folder with the staging area. Git has never seen `settings.txt`, so the file is new to it. Run the next four commands, one after another.

```sh
git status --short
git add settings.txt
git status --short
git commit -m "Add the settings"
```

The two status commands print these lines, one each.

```text
?? settings.txt
A  settings.txt
```

The first status prints `??`: git does not track the file yet. After `git add`, the second prints `A` in the left column: the file is staged as new. `git commit -m` saves the staged list as a commit with the message after `-m`. Write a message that says what changed, because you read it months later.

Why a middle place at all? You often edit five files and want two commits, one per idea. Staging lets you add the files of the first idea, commit, and then add the rest. The cost is one more step to remember, and forgetting it is the most common beginner's mistake.

:::example[Two commits and a diff]
You change the speed from 90 to 120, then look at the change before you save it. A **diff** is the list of differences between two versions of the files, line by line. `git diff` compares the working folder with the staging area.

```sh
git diff
```

Git prints a header, then the changed lines. It also prints an `index` line of hashes, which this page omits.

```text
diff --git a/settings.txt b/settings.txt
--- a/settings.txt
+++ b/settings.txt
@@ -1,4 +1,4 @@
-speed = 90
+speed = 120
 jump = 5
 gravity = 9
 lives = 3
```

Below the header, `-` marks a line that was removed, `+` a line that was added, and lines with a space are context that did not change. `@@ -1,4 +1,4 @@` says that the old version showed lines 1 to 4 and the new one shows lines 1 to 4. Here one line changed, so there is one `-` and one `+`. Git status now prints ` M settings.txt`, with the `M` in the right column because the edit is not staged. <!-- markdownlint-disable-line MD038 -->

You add the file, commit it with the message "Raise the speed", and list the history, newest first.

```sh
git add settings.txt
git commit -m "Raise the speed"
git log --oneline
```

The log prints one line for each commit.

```text
8b4198d Raise the speed
94b57ff Add the settings
```

Each line is one commit: its short name, a hash that git computes from the commit's content, and its message. Your names differ from these. After the add, `git diff` prints nothing, because the working folder and the staging area agree; `git diff --staged` would show the change that waits for the commit.
:::

Try it: you change `jump` to 8 and `lives` to 5, then run `git add settings.txt`. Which command shows the two changes before you commit, and which `-` and `+` lines does it print?

:::answer
`git diff --staged`, because plain `git diff` compares the working folder with the staging area and prints nothing now. It prints `-jump = 5` with `+jump = 8`, and `-lives = 3` with `+lives = 5`.
:::

## A project keeps its build files out

Some files do not belong in a history: files that a program makes again by itself, such as caches and build results. They are large, they change at every build, and they differ between computers. A file named `.gitignore` lists what git must not offer to track. One pattern stands on each line: `#` starts a comment, a slash at the start ties the pattern to the folder of the `.gitignore`, and a slash at the end matches folders only.

Strata's editor writes such a file for you. When it creates a project, it writes a `.gitignore` with the line `/.strata/` into the project's folder, unless a `.gitignore` already exists (`Strata/src/Strata/Project/Project.cpp`). The `.strata` folder holds the import cache and the script builds, which the editor can make again. The project's `Assets` and `Scripts` folders and its project file are what git tracks.

:::why[Why the editor writes the file]
A game maker who starts to use git meets a first `git add` that would otherwise swallow thousands of cache files. The editor keeps them out from the first day, and it never replaces a `.gitignore` that you already wrote. The price: the rule works only before a file is tracked, and a project that is older than its repository needs the rule written by hand.
:::

The script folder gets a second file. When the editor writes the build files for the project's scripts, it also writes a `.gitignore` into the `Scripts` folder, again only if none exists, with the line `/CMakePresets.json` (`StrataEditor/src/Editor/ScriptBuild.cpp`). That file names your computer's compiler and engine folder, so it is right on your computer and wrong on every other.

A rule hides only files that git does not track yet. A file that you committed stays tracked when you add its name to `.gitignore` later. Write the ignore rules before the first `git add`.

## A branch holds work apart

You want to try a slower game, but `main` must stay in working order. A **git branch** is a name for a line of commits, and the name moves. `main` is the first one; each new commit moves the current branch's name forward. A branch costs almost nothing, because it is only a name.

```sh
git switch -c slow
```

`git switch -c slow` creates the branch `slow` at the current commit and moves you onto it. Edit `speed` to 45 and commit with `git commit -am "Slow the game down"`; `-a` stages every file that git already tracks, so a new file still needs `git add`. Then run `git switch main`. The working folder changes under you: `settings.txt` shows `speed = 120` again, because `main` has no commit that changes it. `git branch` lists the branches and marks the current one with `*`.

Meanwhile the work on `main` continues. Change `lives` to 5 there and commit with the message "Give five lives". The two branches now hold different work, and you want both. To **merge** is to bring the commits of another branch into the current one.

```sh
git merge --no-edit slow
```

The command joins `slow` into the branch you are on. Git makes one new commit that joins the lines, the merge commit. Without `--no-edit`, git opens your code editor with a ready-made message; save the file and close the editor to finish. `settings.txt` now holds `speed = 45` from `slow` and `lives = 5` from `main`, because the two branches changed different lines.

```mermaid caption="Two branches leave the commit that raised the speed; the merge commit joins them and has both as the commits before it." alt="A diagram of commits. Add the settings leads to Raise the speed. From Raise the speed one line leads to Slow the game down and another to Give five lives. Both lead to the merge commit."
flowchart LR
    A["Add the settings"] --> B["Raise the speed"]
    B --> C["Give five lives, on main"]
    B --> D["Slow the game down, on slow"]
    C --> M["Merge commit"]
    D --> M
```

If the branch you merge holds the only new commits, `main` has nothing of its own to join, and git only moves the name `main` forward: a fast-forward, with no merge commit. A merge that git cannot finish alone is the subject of the next section.

## A merge conflict needs your decision

Git joins changes line by line. When both branches changed the same line in different ways, git cannot know which version you want. A **merge conflict** is such a clash: git stops the merge and leaves the decision to you.

:::example[Two speeds for one line]
On `main`, you set `speed` to 100 and commit. On a branch `quick` that left `main` earlier, you set `speed` to 150. You merge.

```sh
git merge --no-edit quick
git status --short
```

Git reports the clash, and the status lists the file.

```text
Auto-merging settings.txt
CONFLICT (content): Merge conflict in settings.txt
Automatic merge failed; fix conflicts and then commit the result.
UU settings.txt
```

`UU` means that both sides changed the file. Open `settings.txt` in your code editor. Git wrote both versions into it, between markers, so the file now looks like this.

```text
<<<<<<< HEAD
speed = 100
=======
speed = 150
>>>>>>> quick
jump = 5
gravity = 9
lives = 5
```

`HEAD` is the commit you are on, so the lines between `<<<<<<< HEAD` and `=======` are your branch's. The lines between `=======` and `>>>>>>> quick` come from the branch you merge. The other three lines had no clash and are already settled.

You decide: keep 100. Delete the three marker lines and the `speed = 150` line, so that the file reads `speed = 100` above the three other lines. Then tell git that the file is settled and finish the merge.

```sh
git add settings.txt
git commit --no-edit
```

Adding the file is how you say "this one is settled". The merge commit keeps your version. If you want to stop instead, `git merge --abort` returns the folder to the state before the merge.
:::

Try it: you want both values kept, so that the game reads the second one. Which lines do you delete?

:::answer
Only the three marker lines, the ones that start with `<<<<<<<`, `=======` and `>>>>>>>`. The file then holds `speed = 100` and `speed = 150`, in that order. Add the file and commit.
:::

## A remote shares a repository

So far the repository lives on one computer. A **remote** is a copy of the repository kept somewhere else, such as a server on GitHub; git knows it by a short name, and the usual name is `origin`. To **clone** is to copy a whole repository, with its entire history, from an address to a new folder on your computer. The clone remembers where it came from as `origin`.

```sh
git clone https://github.com/2042Third/GameEngine.git
cd GameEngine
git remote -v
```

The first command copies Strata's repository from GitHub, the second enters the new folder, and the last lists the remotes and their addresses. Two commands then exchange commits. `git push` sends the commits of your current branch to the remote, and the first push of `main` to a new remote is `git push -u origin main`, where `-u` remembers the pairing. `git pull` fetches the commits that others pushed and merges them into your branch, so a pull can end in a merge conflict, which you settle as above. You can push only where the owner gave you rights; for a repository that is not yours, you push to your own copy.

A **tag** is a fixed name for one commit, such as `v1` for a release. A branch moves with every new commit, and a tag stays where you put it. `git tag v1` names the current commit, `git tag` lists the tags, and `git push origin v1` sends one to the remote; a plain `git push` does not send tags.

Strata needs one more step. Most of its third-party libraries, such as GLFW, are each a :term[submodule]{id=submodule}: a separate repository inside the engine's, pinned to one commit. A `git clone` copies the engine and leaves the folders of its libraries empty, so the build fails. The next command fills them (`Strata/vendor/` holds them, listed in `.gitmodules`).

```sh
git submodule update --init --recursive --depth 1
```

`update` fetches each submodule at the commit the engine pins, and `--init` registers the ones that are not yet known. `--recursive` includes submodules inside submodules. `--depth 1` fetches only the newest commit of each library, not its history: the engine's `.gitmodules` marks them shallow too, and the history of a library is large and not needed to build.

## Patches, searches and worktrees

A **patch** is a diff saved in a file, so that you can send it to another person or another folder. `git diff --output=change.patch` writes the diff of the changes you have not committed into `change.patch`. (The shell's `>` does the same on Linux and macOS, but Windows PowerShell 5.1 writes the file in another text encoding, which `git apply` can reject.) Then `git apply --check change.patch` tests whether the patch fits without changing anything, and `git apply change.patch` makes its changes in the working folder. You commit them yourself afterwards.

`git grep` searches the text of every file that git tracks. `git grep -n speed` prints each line with the word, preceded by the file name and the line number, for example `settings.txt:1:speed = 100`. A path after `--` limits the search to that folder. To check that Strata has no feature of some name, run a `git grep` for the name: a search that finds nothing is good evidence.

A **worktree** is a second working folder of the same repository, with its own branch checked out. `git worktree add ../settings-side -b side` creates the folder `settings-side` beside the current one, on a new branch `side`, and `git worktree list` shows both. Both folders share one history, so a commit made in one is at once in the other's repository. Use it to build or test one branch while you keep editing another, without a second clone and its download. Git refuses to check out one branch in two worktrees; `git worktree remove ../settings-side` deletes the folder when you are done.

## Common mistakes

- **A commit without `git add`.** The symptom: `git commit` answers that nothing is staged, or the commit misses your edit, and `git status` still lists the file. The fix: add the file, then commit. `git commit -am` stages files git already tracks.
- **Conflict markers left in a file.** The symptom: the compiler complains about lines of `<<<<<<<`, or the game reads them as text. The fix: search before every commit with `git grep -n "<<<<<<<"`, and edit until it finds nothing.
- **Build output committed.** The symptom: `git status` lists thousands of files, and a commit takes minutes. The fix: write the `.gitignore` first. If the files are already tracked, `git rm -r --cached <folder>` stops tracking them and keeps them on disk; commit that change.
- **"Author identity unknown".** The symptom: the first `git commit` fails with that message. The fix: run the two `git config --global` lines from above, then commit again.

## Summary

- A change passes through the working folder, the staging area (`git add`) and the history (`git commit`).
- `git status` shows where each file is, `git diff` shows the lines that changed, and `git log --oneline` lists commits.
- A branch holds work apart, `git merge` joins it, and a conflict is a pair of marker blocks that you edit by hand.
- `git clone` copies a repository, `git push` and `git pull` exchange commits, and Strata's libraries need `git submodule update --init --recursive --depth 1`.
- `.gitignore` keeps files out, `git diff --output` saves a patch, `git apply` applies one, `git grep` searches, and a worktree is a second folder.

## Check yourself

1. In `git status --short`, a line reads `MM settings.txt`. What does it tell you?

   :::answer{tests="three-places commit-cycle"}
   Both columns hold an `M`: a modification is staged, and the working folder holds a further modification that is not staged. A commit now saves only the staged one.
   :::

2. You merge a branch and git prints `CONFLICT (content)`. Which of these is right? (a) The merge is done and the file is lost. (b) Nothing changed; run the merge again. (c) The merge waits: fix the file, `git add` it and commit.

   :::answer{tests="branch-merge"}
   (c). The conflict stops the merge half way; `git status` lists the file as `UU`, and `git merge --abort` returns to the state before. Answer (b) fails because the same clash returns.
   :::

3. A teammate says "I pushed my work, but you cannot see my tag `v2`." What did they forget?

   :::answer{tests="share-code"}
   A plain `git push` does not send tags. They must run `git push origin v2`.
   :::

4. You add `/build/` to `.gitignore`, but `git status` still lists the files of `build`. Why?

   :::answer{tests="ignore-patch"}
   Those files are already tracked from an earlier commit, and a rule hides only files that git does not track yet. Run `git rm -r --cached build`, then commit.
   :::

## Practice

1. **Basic.** Create a folder `git-practice`, make it a repository, create `notes.txt` with three lines, and commit it with a message. Run `git log --oneline` and read its one line.

   :::answer[Worked solution]{tests="commit-cycle three-places"}
   Run `mkdir git-practice`, `cd git-practice`, `git init -b main`; create `notes.txt` in your editor; then `git add notes.txt` and `git commit -m "Add the notes"`. The log shows one line: a short hash and your message.
   :::

2. **Basic.** Change one line of `notes.txt`, read `git diff`, run `git add notes.txt` and read `git diff --staged`. What differs between the two outputs?

   :::answer[Worked solution]{tests="commit-cycle three-places"}
   The first `git diff` shows the change, and after the add it prints nothing; `git diff --staged` then shows the same `-` and `+` lines. The change moved from the working folder to the staging area. Commit it.
   :::

3. **Medium.** Make a conflict on purpose: create a branch `other`, change the first line of `notes.txt` there and commit, return to `main`, change the same line differently and commit, then merge `other`. Settle it by keeping both lines.

   :::answer[Worked solution]{tests="branch-merge"}
   After `git merge --no-edit other` git reports a conflict and marks the file `UU`. Open the file, delete the three marker lines and keep both versions, run `git add notes.txt` and `git commit --no-edit`. `git log --oneline --graph` then shows the two branches joining.
   :::

4. **Medium.** Save a change of `notes.txt` as a patch, discard the change with `git restore notes.txt`, and apply the patch. Then search the file with `git grep -n` for a word you wrote.

   :::answer[Worked solution]{tests="ignore-patch"}
   Edit the file, run `git diff --output=change.patch`, then `git restore notes.txt`; the edit is gone. `git apply --check change.patch` is silent when the patch fits, and `git apply change.patch` brings the edit back; `git status --short` shows ` M notes.txt`. `git grep -n word` prints `notes.txt:` with the line number. <!-- markdownlint-disable-line MD038 -->
   :::

5. **Hard.** Optional, on a project that you created in Strata's editor: in its folder run `git init -b main` and `git status`, and check that the `.strata` folder does not appear. Commit everything with `git add .` and a message. Change `DegreesPerSecond` in `Scripts/Spinner.cpp`, the example script of every new project, read `git diff` and commit. Then create a branch `fast`, change the value again, commit, return to `main` and merge.

   :::answer[Worked solution]{tests="commit-cycle branch-merge ignore-patch"}
   `git status` lists the project file, `.gitignore` and the folders that hold files, such as `Scripts/`, but not `.strata`, because the `.gitignore` the editor wrote hides it. `git add .` stages every file in the folder that is not ignored. Edit the number in `Spinner.cpp`; `git diff` shows one `-` line with the old value and one `+` line with the new. After `git switch -c fast`, the second change and `git switch main`, run `git merge --no-edit fast`. Here `main` has no new commit of its own, so git moves `main` forward: a fast-forward.
   :::

## Where the book uses it

- [Your first engine change](../core/first-change.md) uses three commands of git to put your clone at the book's commit.
- [Finding your way in a large codebase](../core/reading-code.md) searches the engine's tracked files with `git grep`.
- [The frame loop](../core/frame-loop.md) quotes the engine's source, which you read in the clone that `git clone` makes.

## Further reading

- [Pro Git, "Git Basics"](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository): the first steps from `git init` to history and undo, with pictures (beginner).
- [Pro Git, "Git Branching"](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell): branches and merges, including conflicts, in depth (intermediate).
- [Pro Git, "Git Tools: Submodules"](https://git-scm.com/book/en/v2/Git-Tools-Submodules): how a repository holds another one (intermediate).

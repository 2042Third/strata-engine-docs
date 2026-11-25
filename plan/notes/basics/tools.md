# Notes: basics/tools

## New terms

None beyond the glossary terms of the brief (terminal, shell, terminal command, file, folder, path, absolute path, current folder, command-line argument, standard input, standard output, standard error, stdio, pipe, exit code, environment variable, user data folder, code editor). Each is defined once in bold. "Relative path" and "extension" are explained in plain sentences, not defined as terms.

## Requests

- `tools/data/extra-words.txt` or `names.txt`: IntelliSense (Microsoft's name for code completion and error marks in a code editor; the page uses it twice; it is the page's one open `word-list` finding).
- `tools/data/names.txt`: zsh, POSIX are not used outside code (the page writes `zsh` as code and says bash for both shells); no request.
- `tools/external-hosts.txt`: `code.visualstudio.com` (the Visual Studio Code documentation, cited in Further reading without a link).
- No figures file and no sketch: the page has a file tree (`:::files`) and no picture. Its Practice is done in the reader's terminal; the tutorial runner drives editor commands only, so the Practice has no `solution=` file (the exercises are answered with their commands).

## Not verified

- PowerShell 5.1 as the PowerShell Windows ships, `&&` as an error in it and accepted by PowerShell 7, `$LASTEXITCODE` and `$?` semantics, `set -e`, `chmod +x`, `grep`, `tail`: general knowledge, not engine facts.
- The shortcuts and menu labels of Visual Studio Code and Visual Studio (Ctrl+Shift+F, "Terminal > New Terminal", "View > Terminal", "File > Open Folder"): general knowledge; the Visual Studio "File > Open > Folder..." label and the CMake Tools extension are from `Docs/Manual/Scripting.md` at the pin.
- Windows refusing `.ps1` files by its execution policy: general knowledge.
- The two learn.microsoft.com URLs in Further reading were not fetched.
- That the Coin Run project holds a `Scripts` folder, or a file named `Coin Run.stproj`: the project file is `<Name>.stproj` (`Strata/src/Strata/Project/Project.cpp:191`); the folder and name of Coin Run come from the page's example, not from the lesson.
- What a running editor writes to its log: not run; only the log's path (`Strata/src/Strata/Core/Platform.h:73-75`, `StrataEditor/src/EditorApplication.cpp:286`) was read.

## Findings not applied

- critic-basics-a-18: applied. **Ctrl+C**, joining commands (`&&` in bash, two lines or `;` with `$?` in Windows PowerShell 5.1), `$env:LOCALAPPDATA` beside `%LOCALAPPDATA%`, and the Python tools coming with the source on track E (`core/first-change`), with how Python starts on each OS.
- critic-basics-a-21: applied as `## Common mistakes` (six mistakes, each with symptom and fix).
- Brief "POSIX shell": the page writes bash for both bash and zsh, because "POSIX" is on no word list and its expansion would need marked terms.
- Brief "Strata's exit codes named with a link": 0, 1, 3 and 130 are named and linked to `core/first-frame`; the codes are from `Strata/src/Strata/Core/Application.h:60-71` and `CommandLineOptions.h:25-27`.
- Brief Practice item "search the folder's files in the code editor": applied as exercise 4 (with the editor's terminal).
- The Practice has no tutorial file (see Requests).

## Clerk

- `names.txt`: "IntelliSense". `code.visualstudio.com` admitted (see `start/install`).

## Track walk G, final, segment 3 (2026-11-24)

Answers to `plan/walks/G-final-3.md`, WK12 to WK15, checked with the v0.8.0 package in Windows PowerShell 5.1
(`powershell -File`, under the perf lock):

- WK12: `.\StrataEditor.exe --bogus 2> f | Write-Output` writes PowerShell's error record into `f`
  (`.\StrataEditor.exe : Unknown argument '--bogus'`, `At …:9 char:1`, `CategoryInfo … RemoteException`,
  `FullyQualifiedErrorId : NativeCommandError`), code 3. The example now says so; a host that reads PowerShell's
  screen (the walker's) shows them with `>` alone.
- WK13: after `cmd /c exit 3`, a bare `.\StrataEditor.exe --version` left `$LASTEXITCODE` at 3 and printed its line
  after the prompt; piped it printed `Strata Editor 0.8.0` and set 0. The page was right; the walker's old number was
  0. The page now says the old number is often 0 and looks right.
- WK14: the PerfStability line is marked as one to read for later: the release has no `Tools` and installs no Python.
- WK15: rejected; a reader has a screen for a code editor.

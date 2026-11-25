---
id: basics/tools
title: "The tools: the terminal, files and a code editor"
description: "Learn to type commands into a terminal, name files by their paths, read exit codes and environment variables, and use a code editor on a folder."
kind: primer
size: M
tracks: [B, E]
needs: [start/install]
time: 45
learn:
  - id: command-line
    text: run a program from a terminal with options and a path that holds a space
  - id: paths
    text: write the relative path from a current folder to a file and find a hidden folder
  - id: streams
    text: predict where a program's output and its errors go with redirection and a pipe, and read its exit code
  - id: environment
    text: set an environment variable for one command and find the user data folder with the editor's log
  - id: code-editor
    text: find a word in all files of a project with a code editor
status: final
---

::::test-out

1. You stand in `C:\Games\CoinRun\Assets`. Write the relative path from there to the file `C:\Games\CoinRun\CoinRun.stproj`.

   :::answer{tests="paths"}
   `..\CoinRun.stproj`. The two dots step up from `Assets` into `CoinRun`, where the file lies.
   :::

2. A program writes one line to standard output and one line to standard error, then ends with exit code 3. You run `tool > result.txt`. What do you read on the screen, what is in the file, and did the program work?

   :::answer{tests="streams"}
   The error line stays on the screen, and the output line is in `result.txt`, because `>` moves only standard output. The program failed: 0 means success, and 3 does not.
   :::

3. Write the PowerShell line that changes the current folder to `C:\Users\Ana\Coin Run`.

   :::answer{tests="command-line"}
   `cd "C:\Users\Ana\Coin Run"`. Without the quotes the space splits the path into two arguments, and `cd` refuses them.
   :::

4. Write the one line that starts `./StrataEditor` in bash with `STRATA_EXTERNAL_EDITOR` set to `code -g {file}:{line}:{column}` for this run only.

   :::answer{tests="environment"}
   `STRATA_EXTERNAL_EDITOR='code -g {file}:{line}:{column}' ./StrataEditor`. A variable written before the command reaches that command and no other.
   :::

5. Your project has 40 script files. Which feature of a code editor lists every line that holds the word `OnUpdate`, and what is its usual shortcut?

   :::answer{tests="code-editor"}
   Search across files, **Ctrl+Shift+F** in Visual Studio Code and in Visual Studio (**Cmd+Shift+F** in Visual Studio Code on macOS). It reads all files of the opened folder, not only the open one.
   :::

::::

## Why you will need this

Almost every tool of game making is started from a terminal or needs a file named by its path. This page teaches both from zero, with Strata's editor as the program to practice on. The first script needs only the sections on the terminal, up to the one on arguments, and the section on the code editor.

You will use these skills soon. The page on [building with CMake](build.md) types its commands into a terminal. [Your first script](../make/first-script.md) opens a folder in a code editor. [Your first change to the engine](../core/first-change.md) runs Python tools from a terminal and reads exit codes to see whether a test passed.

## A terminal runs a shell that reads one line at a time

A **terminal** is a window that shows text and sends your typing to a program.

The program inside it is the **shell**: it reads one line, runs what the line names, prints the result and waits for the next line.

Windows ships PowerShell (the version that comes with Windows is 5.1), Linux uses bash, and macOS uses `zsh`. The shell `zsh` behaves like bash, and this page writes bash for both. The commands of bash for one job often differ from PowerShell's, so every command appears in both.

A line you type is a **terminal command**, also called a command line: the name of a program followed by words that tell it what to do, separated by spaces. The shell shows a prompt before each line, such as `PS C:\Users\Ana>` in PowerShell or `ana@pc:~$` in bash.

## Files and folders are named by paths

A **file** is a named piece of data on the disk, such as a script or a picture. The last letters of a file name, after its final dot, are its extension: `.cpp` marks C++ source, `.exe` a Windows program and `.stproj` a Strata project.

A **folder** holds files and other folders.

A **path** is the text that names a file or folder by listing the folders to open, one after another, and ending with its name.

An **absolute path** starts at the top of the disk, so it names one place on the machine. Examples are `C:\Users\Ana\Coin Run` on Windows, `/home/ana/Coin Run` on Linux and `/Users/ana/Coin Run` on macOS.

Windows separates the names with `\`, Linux and macOS with `/`. PowerShell accepts both. The sign `~` stands for your home folder in bash and in PowerShell.

## The current folder is where relative paths start

Every shell stands in one folder, its **current folder**, which the prompt shows. A path that does not start at the top of the disk is relative: the shell reads it from the current folder. The name `.` means the current folder, and `..` means the folder above it.

Names that start with a dot are hidden on Linux and macOS: plain `ls` skips them. Windows hides files by an attribute, and a name with a dot is no different. Strata gives its own working files such a name. A project's imports and script builds live in `.strata/` inside the project folder. Beside it, the editor writes a `.gitignore` file that keeps that folder out of version control, the saved history of a project's files that [Version control with git](git.md) teaches.

:::files[A project folder named Coin Run]

- `Coin Run/` the project's folder
  - `Assets/` the models, pictures and sounds
    - `Models/`
  - `Scripts/` the script sources
  - `.strata/` the editor's import cache and script builds
  - `Coin Run.stproj` the project file
  - `.gitignore`

:::

:::example[Walk from one folder to a file in another]
You stand in `C:\Users\Ana\Coin Run\Assets\Models`. The file `C:\Users\Ana\Coin Run\Scripts\Spinner.cpp` lies in a sibling branch of the tree. Count the steps up: `..` leaves `Models` for `Assets`, and a second `..` leaves `Assets` for `Coin Run`. From `Coin Run` go down into `Scripts` and name the file.

The relative path is `..\..\Scripts\Spinner.cpp`: two steps up, then two names down. On Linux it reads `../../Scripts/Spinner.cpp`.
:::

:::question
Which path leads from `Scripts` to the folder `Models`?

:::answer
`..\Assets\Models`: one step up into `Coin Run`, then down through `Assets` into `Models`.
:::
:::

Three commands move around. `cd` changes the current folder, a listing command shows what the folder holds, and a program of the current folder runs when you write its path, `.\StrataEditor.exe` in PowerShell and `./StrataEditor` in bash.

The commands for the project folder in PowerShell are these:

```powershell
cd "C:\Users\Ana\Coin Run"
Get-Location
Get-ChildItem -Force
```

`Get-Location` prints the current folder, and `Get-ChildItem -Force` lists it with hidden items. The quotes keep the space inside one path; the next section says why. In bash the same job reads:

```sh
cd "$HOME/Coin Run"
pwd
ls -a
```

Here `pwd` prints the current folder, and `ls -a` lists it with the names that start with a dot. Search the listing for `.strata`.

## Arguments and options tell a program what to do

A **command-line argument** is one word of a command line after the program's name. The shell splits the line at spaces and hands the program the words as a list. A word that starts with `--` is an option, such as `--version`. An option may take a value, written as the next word or after an equals sign: `--frames 120` and `--frames=120` mean the same to the editor.

A path with a space in it would split into two words, so write it in double quotes. In `StrataEditor --project "C:\Users\Ana\Coin Run"` the program receives one path.

The editor answers `--help` with its options and `--version` with a line that holds its name and its version number. It starts with `--project` to open a project, and `--headless` runs it without a window. Reference text writes `<count>` for a value you choose and `[options]` for words you may omit.

## The standard streams carry text in and out

Every program starts with three channels for text, together called **stdio**. The next three paragraphs name them.

**Standard input** (stdin) is the channel a program reads from. By default it is your keyboard.

**Standard output** (stdout) is the channel a program writes its results to. By default it is the terminal's screen.

**Standard error** (stderr) is a second output channel for complaints and diagnostics. It also appears on the screen, so you cannot tell the two channels apart there. Strata's editor prints the answer to `--help` on standard output and a complaint about a bad option on standard error.

## Files and pipes move the streams

The sign `>` sends standard output into a file and replaces what the file held; `>>` adds to the end instead. The sign `2>` does the same for standard error, which both kinds of shell call stream number 2. A **pipe**, written `|`, joins the standard output of one program to the standard input of the next, so the second program reads what the first wrote.

The PowerShell lines write a listing to a file and then filter its lines:

```powershell
Get-ChildItem -Force > listing.txt
Get-Content listing.txt | Select-String strata
```

The first line prints nothing, because the listing went into `listing.txt`. The second line pipes the file's lines to `Select-String`, which prints those that hold `strata`. The bash version is:

```sh
ls -a > listing.txt
cat listing.txt | grep strata
```

Here `cat` prints a file and `grep` keeps the lines that hold the word.

## Exit codes tell whether a program worked

An **exit code** is the number a program hands to the shell when it ends: 0 means it worked, and any other number means it failed. Each program says what its numbers mean. Strata's editor uses 0, 1 when it could not start, 3 when it did not understand its command line, and 130 when you interrupted it; [the first frame](../core/first-frame.md) lists them.

Bash keeps the last exit code in `$?`. PowerShell keeps it in `$LASTEXITCODE`, and its `$?` is only True or False.

The editor is a windowed program, and PowerShell does not wait for such a program: the prompt returns at once, and `$LASTEXITCODE` still holds the code of the program before. That number is often 0, so it looks right and is not. Piping the output makes PowerShell wait. The reason is in [the page on platforms](../core/platform.md). In PowerShell read the code like this:

```powershell
.\StrataEditor.exe --version | Write-Output
$LASTEXITCODE
```

The first line prints the version and waits; the second prints 0. In bash the pipe is not needed:

```sh
./StrataEditor --version
echo $?
```

Here `echo $?` prints the code of the line before it, which is 0 again.

:::example[Read what a wrong option does]
You run the editor with an option it does not have and add `> out.txt`. The editor checks its command line before it starts. It writes `Unknown argument` and the offending word, an empty line and its usage text to standard error, then ends with exit code 3.

Because `>` moves standard output only, the file `out.txt` stays empty (0 bytes) and the screen shows the message. With `2> out.txt` the message goes into the file instead, and the screen stays empty. Either way the exit code is 3.

Bash shows exactly this. In Windows PowerShell 5.1, end the line with `| Write-Output`, as above, or PowerShell does not wait: the prompt returns at once, the file stays empty and `$LASTEXITCODE` keeps the older number. Piped, both forms give 3, and two things differ from bash:

```powershell
.\StrataEditor.exe --bogus 2> out.txt | Write-Output
$LASTEXITCODE
```

The first line waits for the editor and sends its standard error into `out.txt`; the second prints 3.

- With `2> out.txt` the file starts with `.\StrataEditor.exe : Unknown argument '--bogus'` and holds lines such as `At line:1 char:1`, `CategoryInfo` and `NativeCommandError` before the usage. Those lines are PowerShell's: the editor's message is the text after the colon of the first line.
- With `> out.txt` the file stays empty, and the screen shows no message either. PowerShell hands a windowed program no screen for standard error, so its complaint is lost unless `2>` or `2>&1` catches it.

:::

:::question
What does `StrataEditor --help > help.txt` show on the screen, and what is the exit code?

:::answer
Nothing: the help text goes to standard output, which `>` sends into `help.txt`. The exit code is 0, because the editor answered what you asked. In Windows PowerShell 5.1 the line needs `| Write-Output` at its end for that answer; without it the prompt returns before the editor has written, as in the example.
:::
:::

:::caution
In a terminal, **Ctrl+C** stops the program that is running; it does not copy. Copying uses another shortcut, such as **Ctrl+Shift+C**, or **Cmd+C** on macOS. On Windows, a window of the editor started from a terminal ignores **Ctrl+C**. On Linux and macOS, and in any run with `--headless` or `--frames`, **Ctrl+C** ends the editor in order, and it returns 130.
:::

## Environment variables pass named texts to the programs you start

An **environment variable** is a named text that a process carries and hands to every process it starts. Programs read them for settings that would clutter a command line. A child gets a copy: a change in the child never reaches its parent, and a change in the parent after the start never reaches the child.

PowerShell reads a variable as `$env:NAME` and sets it with `$env:NAME = 'text'`; the value then stays until the window closes or you remove it. A bash reads `$NAME`, and a variable written before a command exists for that command only. Windows's older notation `%LOCALAPPDATA%` means `$env:LOCALAPPDATA` in PowerShell.

`PATH` is the variable that answers a question: where is the program named `code`? It holds a list of folders, separated by `;` on Windows and `:` on Linux and macOS. The shell tries the folders in order for a bare name. The current folder is not in the list, which is why you write `./` or `.\` before a program of the current folder.

Strata's example is `STRATA_EXTERNAL_EDITOR`. When it is set and not empty, it wins over the **External Editor** setting and names the command that opens script files. The editor starts that program directly, never through a shell.

:::example[Open scripts in Visual Studio Code for one session]
The command template `code -g {file}:{line}:{column}` tells Visual Studio Code to open a file at a line. In PowerShell you set the variable, start the editor and then remove the variable:

```powershell
$env:STRATA_EXTERNAL_EDITOR = 'code -g {file}:{line}:{column}'
.\StrataEditor.exe
Remove-Item Env:STRATA_EXTERNAL_EDITOR
```

The editor inherits the variable at its start. After the third line the window has no variable again, and an editor started later opens scripts as your setting says. In bash one line does it all: `STRATA_EXTERNAL_EDITOR='code -g {file}:{line}:{column}' ./StrataEditor`.
:::

:::question
You set the variable in one PowerShell window and start the editor from the Start menu. Does the editor use it?

:::answer
No. The Start menu is not a child of your window, so the variable never reaches the editor. Start the editor from the same window.
:::
:::

## The user data folder keeps what belongs to you

The **user data folder** is the per-user place where programs keep logs and settings, outside every project. It is `%LOCALAPPDATA%` on Windows, `~/.local/share` on Linux and `~/Library/Application Support` on macOS. Strata uses a folder named `Strata` inside it.

The editor writes its log to `Logs/StrataEditor.log` in that folder, and your preferences are in `Preferences.json` beside it. A game exported from the editor keeps `Logs/Game.log` in a folder named after the game. The log appears when the editor starts for real: `--help` and `--version` answer before any log exists.

## Permissions decide who may read, change or run a file

Every file carries permissions. A read-only file can be read but not changed; Windows marks that in the file's properties, and `ls -l` shows it on Linux and macOS. Strata keeps your preferences in a file that only your account may change.

On Linux and macOS a program also needs the executable bit. If the shell answers "Permission denied" to `./StrataEditor`, set the bit with `chmod +x ./StrataEditor`. Windows decides by the extension `.exe`.

Administrator rights on Windows and `sudo` on Linux and macOS run one command with the power to change any file. Avoid them for ordinary work: the files such a command creates belong to the administrator, and your own account cannot change them later.

## Scripts and joined commands repeat a job

A file of commands, a shell script, runs them in order. Bash scripts end in `.sh`, PowerShell scripts in `.ps1`. A good script stops at the first command that fails, so a later command never works on a broken result. In bash, `set -e` does that:

```sh
#!/bin/sh
set -e
./StrataEditor --version
./StrataEditor --help > help.txt
echo "both worked"
```

Line 1 names the shell that runs the file. After line 2 the script ends as soon as one command returns a code other than 0, and `echo` runs only if both commands worked. PowerShell does not stop on a failed program by itself, so the script checks the code:

```powershell
.\StrataEditor.exe --version | Write-Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.\StrataEditor.exe --help | Write-Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Each `if` leaves the script with the failing code. Windows may refuse to run `.ps1` files until you allow scripts; the error message names the rule.

One line can join two commands. In bash `a && b` runs `b` only if `a` worked. Windows PowerShell 5.1 reports an error for `&&`, so write two lines or `a; if ($?) { b }`. PowerShell 7 accepts `&&`.

Strata's own tools are Python programs in the `Tools` folder of its source code, which the page on [your first change](../core/first-change.md) fetches. The release has no such folder, and Strata does not install Python, so you cannot run the line below yet: read it for later. Python starts with `py` or `python` on Windows and with `python3` on Linux and macOS, and each tool answers `--help`:

```sh
python3 Tools/PerfStability.py --help
```

In the folder of the source code, the line prints the options of one tool; on Windows write `py Tools\PerfStability.py --help`.

## A code editor reads a whole folder

A **code editor** is a program for writing source code. It colors the parts of code, completes names while you type and searches many files at once. You need one, and Visual Studio Code or Visual Studio will do. Strata opens script files in the editor you name under **Scripts ▸ External Editor...**.

Four features matter:

- Open the folder, not a single file. In Visual Studio Code use "File ▸ Open Folder...", in Visual Studio "File ▸ Open ▸ Folder...", and choose the project's `Scripts` folder.
- IntelliSense completes names and marks mistakes by reading the headers of Strata's script kit. Strata's editor writes `Scripts/CMakePresets.json` so that the code editor finds them. Visual Studio Code also needs its CMake Tools and C/C++ extensions and the `strata` preset.
- Search across files: **Ctrl+Shift+F** lists every match in the folder.
- The code editor has a terminal of its own: "Terminal ▸ New Terminal" in Visual Studio Code, "View ▸ Terminal" in Visual Studio. In Visual Studio Code it opens in the folder you opened.

## Common mistakes

- **A path with a space, not quoted.** Symptom: `cd` or the program complains about two arguments or a missing file named `C:\Users\Ana\Coin`. Fix: put the whole path in double quotes.
- **A program run by its bare name.** Symptom: PowerShell says the name is not recognized, and bash says "command not found". Fix: write `.\` or `./` before a program of the current folder, or go to the folder that holds it.
- **Ctrl+C taken for copy.** Symptom: a running program ends and nothing is copied. Fix: copy with **Ctrl+Shift+C** or **Cmd+C**.
- **The exit code read too early in PowerShell.** Symptom: `$LASTEXITCODE` shows an old number, maybe 0, or nothing. Fix: pipe the windowed program's output into `Write-Output`.
- **`&&` in Windows PowerShell 5.1.** Symptom: a parser error at `&&`. Fix: use two lines, or `;` with a check of `$?`.
- **A variable set in the wrong window.** Symptom: the editor ignores `STRATA_EXTERNAL_EDITOR`. Fix: start the editor from the window where you set it.

## Summary

- Run a program as its name, then options and arguments; put a path with a space in double quotes, and write `.\` or `./` before a program of the current folder.
- A relative path starts at the current folder, with `..` for the folder above; a name that starts with a dot is hidden, and `ls -a` or `Get-ChildItem -Force` shows `.strata`.
- Standard output and standard error are two streams: `>` moves the first, `2>` the second and `|` feeds one program's output to the next. The exit code is 0 for success; `$?` or `$LASTEXITCODE` reads it.
- An environment variable reaches the programs you start from the same window; the user data folder holds the editor's log, `Logs/StrataEditor.log`.
- A code editor opened on a folder searches all its files with **Ctrl+Shift+F** and has a terminal of its own.

## Check yourself

1. In PowerShell you stand in the folder that holds `StrataEditor.exe` and type `StrataEditor.exe --version`. The answer is "not recognized". Which fix works: install a new version, type `.\StrataEditor.exe --version`, run PowerShell as administrator, or type `sudo StrataEditor.exe --version`?

   :::answer{tests="command-line paths"}
   Type `.\StrataEditor.exe --version`. PowerShell searches the folders of `PATH` for a bare name, and the current folder is not one of them, so the path `.\` is needed. The other fixes change nothing about where PowerShell searches.
   :::

2. You run `StrataEditor --frames` with no value after the option. Which stream gets the message, and what is the exit code?

   :::answer{tests="streams"}
   Standard error gets `--frames needs a value: --frames <count>`, followed by the usage text. The exit code is 3, the code for a command line the program does not understand.
   :::

3. In PowerShell, `.\StrataEditor.exe --version` returns to the prompt at once, and `$LASTEXITCODE` shows an old number. Why, and how do you get the right one?

   :::answer{tests="streams"}
   The editor is a windowed program, and PowerShell does not wait for it. Pipe its output: `.\StrataEditor.exe --version | Write-Output`. Then PowerShell waits and sets the code.
   :::

4. You open one script file from the `Scripts` folder in the code editor, and IntelliSense marks every Strata header as unknown. What do you change?

   :::answer{tests="code-editor"}
   Open the whole `Scripts` folder instead of the file. The code editor reads `Scripts/CMakePresets.json` from the folder, and with it finds the headers.
   :::

5. Where is the editor's log on Linux, and why does it not exist after only `StrataEditor --version`?

   :::answer{tests="environment"}
   In `~/.local/share/Strata/Logs/StrataEditor.log`, or in `$XDG_DATA_HOME/Strata/Logs` if you set that variable to an absolute path. `--version` answers before the log starts, so only a normal start writes the file.
   :::

## Practice

Each exercise runs in a terminal on a project folder of your own, such as a new, empty project, and changes nothing in it. Write `StrataEditor` for the editor's file in your build folder.

1. **Basic.** Change into the project folder, list it with its hidden items and find the `.strata` folder.

   :::answer[Worked solution]{tests="paths command-line"}
   Use the commands of the section on the current folder, with your own path in quotes. The listing shows `.strata`, `Assets`, the project file that ends in `.stproj` and `.gitignore`, and `Scripts` when the project has scripts. Nothing in the folder changes: listing only reads.
   :::

2. **Basic.** Print the editor's version and read its exit code.

   :::answer[Worked solution]{tests="streams"}
   In PowerShell run `.\StrataEditor.exe --version | Write-Output` and then `$LASTEXITCODE`; in bash run `./StrataEditor --version` and then `echo $?`. The version line starts with `Strata Editor`, and the exit code is 0.
   :::

3. **Medium.** Find the editor's log in the user data folder and print its last 20 lines.

   :::answer[Worked solution]{tests="environment"}
   Start the editor once and close it, so the log exists. In PowerShell the command is the first line below; the second is for bash on Linux, and the third for `zsh` on macOS:

   ```powershell
   Get-Content "$env:LOCALAPPDATA\Strata\Logs\StrataEditor.log" -Tail 20
   tail -n 20 ~/.local/share/Strata/Logs/StrataEditor.log
   tail -n 20 "$HOME/Library/Application Support/Strata/Logs/StrataEditor.log"
   ```

   Run only the line of your system. The last lines show how your latest session ended.
   :::

4. **Hard.** Open the project folder in your code editor, search all its files for the project's name and open the editor's terminal. Repeat exercise 2 there.

   :::answer[Worked solution]{tests="code-editor"}
   Open the folder, press **Ctrl+Shift+F** and type the name. The project file lists among the matches, because it holds the name. The terminal of Visual Studio Code starts in the opened folder, so give the path of `StrataEditor` in full, in quotes if it holds a space.
   :::

## Where the book uses it

- [Your first script](../make/first-script.md) opens the project's `Scripts` folder in a code editor.
- [Building with CMake](build.md) runs its commands in a terminal and reads their exit codes.
- [Your first change to the engine](../core/first-change.md) runs Python tools and tests from a terminal.
- [Version control with git](git.md) types its commands into a terminal.

## Further reading

- [PowerShell: about environment variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables): how PowerShell reads and sets them; beginner.
- [PowerShell: about redirection](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection): `>`, `2>` and the other streams of PowerShell; intermediate.
- The Visual Studio Code documentation, "Getting started": opening folders, search and the integrated terminal; beginner.

---
id: start/install
title: "Installing Strata and the C++ build tools"
description: "Unpack Strata, start its editor, find its log, and install the C++ build tools and a code editor that the next page needs."
kind: how-to
size: M
tracks: [G, E, B]
needs: [start/how-to-read]
time: 60
learn:
  - id: keep-folder
    text: explain why the unpacked Strata folder must stay together
  - id: run-argument
    text: run a program of the current folder with an argument in a terminal on your system
  - id: start-editor
    text: run Strata's editor and name what to do when it does not start
  - id: find-log
    text: find the editor's log and the version and GPU it records
  - id: name-build-tools
    text: name the build tools that the editor uses on your system to build scripts
status: final
---

This page puts Strata on your computer and starts its editor. You also install the C++ build tools and a code editor,
so that [your first game](../start/first-game.md) can build the scripts of a game. Before you start:

- A computer with Windows 10 or 11 on `x64`, Ubuntu 24.04 or newer on `x64`, or macOS 14 or newer on Apple silicon.
- A graphics card whose driver offers Vulkan 1.2 with cube map arrays (the next section says what that means).
- A web browser, an internet connection and a user account that may install programs.

## What the computer needs

Strata runs on your **operating system** (OS), the program that starts all other programs and gives them the screen,
the keyboard and the disk. Windows, Linux and macOS are operating systems, and the release of each has its own archive.

Strata draws every picture on the **graphics processing unit** (GPU), the chip of your graphics card that draws far
faster than the main processor. A laptop may have two: a small one in the processor and a larger one. Strata chooses
the better one itself.

A **driver** is the program of the operating system that lets other programs use one piece of hardware. The graphics
driver comes from the maker of your GPU, and it matters here because it decides which of the GPU's abilities
programs may use. Update it now: NVIDIA, AMD and Intel offer their newest drivers on their websites.

Programs ask a graphics driver for work through [Vulkan](../gpu/vulkan-nvrhi.md), a standard interface that drivers
offer. Strata needs version 1.2 or newer, and one feature in it, cube map arrays, which every desktop GPU with a
Vulkan 1.2 driver has. A GPU without the feature is refused, and the log says what it lacks. On macOS, MoltenVK
translates Vulkan to Metal, the graphics interface of Apple; step 6 installs it.

## What the folder holds

Every release has one archive per system, and its name tells you three things. Take a release numbered 1.2.3 as an
example: `Strata-1.2.3-windows-x64.zip` is Strata, release 1.2.3, for Windows on `x64`. The other two are
`Strata-1.2.3-linux-x64.tar.gz` and `Strata-1.2.3-macos-arm64.tar.gz`. An archive is one file that holds a whole folder:
a ZIP on Windows, a `.tar.gz` file on the other two systems.

Unpacking makes one folder with the same name, without the ending. The editor finds everything it needs next to itself,
so the folder must stay together. The marker `StrataInstall.json` makes the folder an installation: the editor reads it
to build your scripts against the script kit inside the folder. Move the whole folder if you must, and never single
files out of it.

| Path in the folder | What it is |
| --- | --- |
| `StrataEditor` | The editor, where you make games. Its first window is the launcher. |
| `StrataRuntime` | The program that plays exported games. The editor copies it into each game it exports. |
| `StrataCLI` | A command-line client that sends commands to a running editor, and a server for agents that run on artificial intelligence (AI). |
| `Samples/` | Five finished games made by an AI agent through the editor: High Desert Outpost, Third-Person Adventure, Open World, Physics Playground and Tetris. The editor opens copies of them. |
| `StrataScriptCore/` | The software development kit (SDK) for scripts: the headers they include and the CMake package their build uses. |
| `Docs/Manual/` | Ten guides for making games: `Scripting.md`, `Worlds.md`, `Prefabs.md`, `GameView.md`, `GameUI.md`, `Lighting.md`, `Camera.md`, `AntiAliasing.md`, `Settings.md` and `Graphics.md`. |
| `Skills/` | Three guides for AI agents that drive the editor. |
| `StrataInstall.json` | The installation marker. |
| `ThirdPartyNotices.md` | The components of other people inside Strata, their licenses, and the credits that a game made with the samples' assets must show. |
| `README.md` | The release's short guide: what the folder holds, what each system needs and how to start the first time. |

On Windows the three programs end in `.exe`. The folder holds no license file for Strata itself: read
`ThirdPartyNotices.md` for the licenses of what Strata contains.

## Install Strata and the build tools

:::::steps

1. Download the archive of your system from [the releases page](https://github.com/2042Third/GameEngine/releases).
   Open the newest release and take the file from its list of files.

   ::::tabs{sync=os}
   :::tab[Windows]
   Download `Strata-<version>-windows-x64.zip`.
   :::
   :::tab[Linux]
   Download `Strata-<version>-linux-x64.tar.gz`.
   :::
   :::tab[macOS]
   Download `Strata-<version>-macos-arm64.tar.gz`.
   :::
   ::::

   **You should see:** the file in the download folder of your browser, which is usually called `Downloads`.

   **If you do not see it:** the browser asked for a place or blocked the file. Open its list of downloads: it shows
   where each file went and lets you keep one that it flagged.

2. Open a terminal. A terminal is a window where you type a command, press **Enter**, and read the text the computer
   answers with; the [tools page](../basics/tools.md) teaches it in full, and this page needs five moves.

   ::::tabs{sync=os}
   :::tab[Windows]
   Press the Windows key, type `PowerShell` and press **Enter**. PowerShell is the program inside the window that reads
   your commands.
   :::
   :::tab[Linux]
   Press **Ctrl+Alt+T** on Ubuntu, or search the list of applications for Terminal.
   :::
   :::tab[macOS]
   Press **Cmd+Space**, type `Terminal` and press **Enter**.
   :::
   ::::

   **You should see:** a window with a prompt: a short line that ends in a character such as `>`, `$` or `%` and waits
   for you to type.

   **If you do not see it:** search the applications list by hand, and make sure you opened the terminal and not an
   editor or a web page.

3. Move the terminal to the folder of the download. The terminal always works in one folder, which the prompt shows,
   and `cd` (change folder) moves it. The sign `~` stands for your home folder, which holds `Downloads`. To paste a
   command that you copied from this page, click in the terminal and press the keys in your tab, then **Enter**.

   ::::tabs{sync=os}
   :::tab[Windows]
   Type `cd ~\Downloads`, press **Enter**, and then type `dir`. Paste with **Ctrl+V**. A path with a space in it goes in
   quotes, as in `cd "C:\Users\Ana Rossi\Downloads"`: without them PowerShell reads two words.
   :::
   :::tab[Linux]
   Type `cd ~/Downloads`, press **Enter**, and then type `ls`. Paste with **Ctrl+Shift+V**. A path with a space in it
   goes in quotes, as in `cd ~/"My Games"`: without them the terminal reads two words.
   :::
   :::tab[macOS]
   Type `cd ~/Downloads`, press **Enter**, and then type `ls`. Paste with **Cmd+V**. A path with a space in it goes in
   quotes, as in `cd ~/"My Games"`: without them the terminal reads two words.
   :::
   ::::

   **You should see:** `dir` or `ls` lists the files of the folder, and the archive of step 1 is among them.

   **If you do not see it:** the archive is somewhere else. Open the folder in your file manager, read its path from
   the address bar or the file's information, and `cd` there with the path in quotes.

4. Unpack the archive. Unpacking makes the folder of the last section next to the archive.

   ::::tabs{sync=os}
   :::tab[Windows]
   First right-click the `.zip` file in File Explorer, choose "Properties", tick `Unblock` at the bottom of the
   General page and click "OK". Windows marks files that come from the internet, and the mark spreads to everything you
   unpack. Then type `Expand-Archive .\Strata-<version>-windows-x64.zip -DestinationPath .`, where `.\` names a file of
   the current folder and the last `.` is the current folder itself.
   :::
   :::tab[Linux]
   Type `tar -xzf Strata-<version>-linux-x64.tar.gz`. The program `tar` reads archives, and the letters mean: extract, undo the compression, and "the file is the next word".
   :::
   :::tab[macOS]
   Type `tar -xzf Strata-<version>-macos-arm64.tar.gz`. The program `tar` reads archives, and the letters mean: extract, undo the compression, and "the file is the next word".
   :::
   ::::

   **You should see:** a new folder `Strata-<version>-<system>` in the list of `dir` or `ls`.

   **If you do not see it:** a message such as "No such file" means the name does not match. Type the first letters of
   the archive's name and press **Tab**, and the terminal completes the rest.

5. Go into the folder and look at it, then compare the list with the table above.

   ::::tabs{sync=os}
   :::tab[Windows]
   Type `cd Strata-<version>-windows-x64` and then `dir`.
   :::
   :::tab[Linux]
   Type `cd Strata-<version>-linux-x64` and then `ls`.
   :::
   :::tab[macOS]
   Type `cd Strata-<version>-macos-arm64` and then `ls`.
   :::
   ::::

   **You should see:** the entries of the table, with `StrataEditor` among them.

   **If you do not see it:** the archive made a folder inside a folder, or the unpacking stopped. Run `dir` or `ls`
   once more, and unpack again into an empty folder if files are missing.

6. Add what the system itself lacks.

   ::::tabs{sync=os}
   :::tab[Windows]
   Nothing is missing except an up-to-date graphics driver. If the editor later says that Vulkan is not available,
   install the newest driver from the website of your GPU's maker.
   :::
   :::tab[Linux]
   Ubuntu on a desktop has most of the libraries Strata needs. To be sure, run this command, which asks Ubuntu to install
   them with `sudo`, the word that runs one command as the administrator; it asks for your password and shows nothing
   while you type: `sudo apt install libvulkan1 mesa-vulkan-drivers libgtk-3-0t64 libx11-6 libxrandr2 libxinerama1 libxcursor1 libxi6 libxkbcommon0 libwayland-client0`
   :::
   :::tab[macOS]
   Install MoltenVK with the Vulkan SDK from `vulkan.lunarg.com/sdk/home#mac`: run its installer and choose "System
   Global Installation". Then remove the mark of downloaded files, a label that macOS adds so that it asks
   before it runs them: `xattr -dr com.apple.quarantine ~/Downloads/Strata-<version>-macos-arm64`. Use the real path of
   the folder, in quotes when it holds a space.
   :::
   ::::

   **You should see:** on Linux, `apt` finishes without an error and may report that a package is already the
   newest. On macOS the installer ends, and `xattr` prints nothing.

   **If you do not see it:** on Linux, `sudo: command not found` or a refused password means your account cannot
   install programs; ask the person who owns the computer. On macOS, `No such file` means the path differs: step 3 shows
   how to find it.

7. Run the editor with an argument. An argument is a word after the program's name that tells it what to do. Here
   `--version` asks the editor to print its version and stop.

   ::::tabs{sync=os}
   :::tab[Windows]
   Type `.\StrataEditor --version | Write-Output`. The editor is a windowed program, and PowerShell does not wait for
   such a program unless you pipe its output into another command. `Write-Output` is that command, so PowerShell waits
   and shows the answer.
   :::
   :::tab[Linux]
   Type `./StrataEditor --version`. The `./` means the file of the current folder. A terminal runs a program by its bare
   name only when the program is in a folder it searches, and the current folder is not one.
   :::
   :::tab[macOS]
   Type `./StrataEditor --version`. The `./` means the file of the current folder. A terminal runs a program by its bare
   name only when the program is in a folder it searches, and the current folder is not one.
   :::
   ::::

   **You should see:** `Strata Editor` and a number, the same number as in the archive's name. The archive of a test
   release adds an ending such as `-rc1` to the number, and the editor prints the number without it.

   **If you do not see it:** on Windows the prompt returns with nothing when you omit `| Write-Output`. On Linux and
   macOS, `No such file or directory` means the terminal is in another folder: repeat step 5. On macOS, a message that
   the developer cannot be verified means the mark of downloaded files is still there: repeat `xattr` of step 6.

8. Start the editor.

   ::::tabs{sync=os}
   :::tab[Windows]
   Double-click `StrataEditor` in File Explorer. If you did not tick `Unblock` in step 4, Windows shows "Windows
   protected your PC": click "More info", then "Run anyway".
   :::
   :::tab[Linux]
   Type `./StrataEditor` in the terminal that stands in the folder.
   :::
   :::tab[macOS]
   Type `./StrataEditor` in the terminal that stands in the folder.
   :::
   ::::

   **You should see:** the launcher, the editor's first window, with the buttons **New Project**, **Open Project...**
   and **Open Sample...**. The editor opens no console window, and a terminal that started it stays free: closing the
   terminal does not close the editor.

   **If you do not see it:** the editor may show the message `Strata Editor cannot start: no usable graphics device was found (it needs Vulkan 1.2 or later).` It says what to install and names the log. The cause is a GPU or a driver without Vulkan 1.2 or cube map arrays, so install the driver of step 6 and start again. "When something goes wrong" below opens the log.

9. Install the C++ build tools. Scripts are C++ source text. The **build tools**, also called the toolchain, are the
   programs that turn such text into a program: a compiler, which translates the C++, and a program that runs it for
   every file. CMake is one more program: it reads a project's list of files and tells the compiler how to build them.

   ::::tabs{sync=os}
   :::tab[Windows]
   Install Visual Studio Community, which is free, from `visualstudio.microsoft.com/downloads`. Strata needs Visual Studio
   2022, release 17.10 or later, or Visual Studio 2026. In its installer, tick the workload "Desktop development with C++"
   and click "Install". The workload brings CMake with its "C++ CMake tools". The Build Tools for Visual Studio, without
   the editor of Microsoft, work as well.

   A CMake that you installed yourself, in `PATH` or in `Program Files\CMake`, is tried first. The editor uses it when
   it is 3.25 or later and knows your Visual Studio, and the workload's CMake otherwise. Either works.
   :::
   :::tab[Linux]
   Type `sudo apt install g++ cmake ninja-build`. It installs a compiler, CMake, and Ninja, the program that runs the
   compiler. Strata wants GCC 13 or later (or Clang 17 or later) and CMake 3.25 or later.
   :::
   :::tab[macOS]
   Type `xcode-select --install` and click "Install" in the window that appears: Apple's Command Line Tools bring the
   compiler and Make. Then download CMake from [its website](https://cmake.org/download/), open the disk image and
   drag `CMake.app` into the Applications folder, where the editor searches for it.
   :::
   ::::

   **You should see:** the installer or the command ends without an error. No step here tests the tools: the editor
   searches for them when it first builds scripts, and the first build in the next page is the test.

   **If you do not see it:** on Windows, run the Visual Studio Installer again, open "Modify" and tick the workload. On
   Linux, read the last lines of the output for the package that failed. On macOS, wait until the Command Line Tools
   finish: the download takes minutes.

10. Install a code editor, the program in which you read and change script files, and open a folder in it.

    ::::tabs{sync=os}
    :::tab[Windows]
    The Visual Studio of step 9 is one. Start it, choose "Continue without code" if it asks for a project, and then
    "File", "Open", "Folder...". Pick the `StrataScriptCore` folder of the unpacked archive. Visual Studio Code, from
    `code.visualstudio.com`, is the light alternative: choose "File", "Open Folder...".
    :::
    :::tab[Linux]
    Install Visual Studio Code from `code.visualstudio.com`. The site offers a `.deb` file for Ubuntu: install it with
    `sudo apt install ./` followed by the file's name. Start it, choose "File", "Open Folder..." and pick the
    `StrataScriptCore` folder of the unpacked archive.
    :::
    :::tab[macOS]
    Install Visual Studio Code from `code.visualstudio.com`: unpack the download and drag Visual Studio Code into the Applications
    folder. Start it, choose "File", "Open Folder..." and pick the `StrataScriptCore` folder of the unpacked archive.
    :::
    ::::

    **You should see:** the files of the folder as a tree in a side panel. Later pages open a project's `Scripts` folder
    in the same way.

    **If you do not see it:** the folder dialog sits behind another window, or you picked a file instead of a folder.
    Strata opens scripts in the code editor you choose under **Scripts ▸ External Editor...**: its page lists Visual Studio Code and
    the Visual Studio that Strata builds with, when it finds them. Click yours and then **Apply**, once a project is open.

:::::

## When something goes wrong

The **log** of a program is the lines it writes about what it is doing, kept in a file. The editor writes one with its
version and system on its first line, and a line `Graphics device:` that names your GPU, the version of Vulkan and the
driver. A game exported from Strata writes its own log, `Logs/Game.log` in a folder named after the game, beside the
folder `Strata`. Both live in your user data folder, which is hidden from the file manager unless you type its path.

Each line starts with the date and time in brackets, the level such as `[info]`, and the part that wrote it: `App:`
for the editor, `Strata:` for the engine. So the first line reads, for example,
`[2026-03-14 09:30:12.345] [info] App: Strata Editor 1.2.3 (Windows)`, for the release 1.2.3 of the example above. After the first build of scripts, a line with
`[Scripts] Found` names the Visual Studio, or the compiler, and the CMake that the editor chose.

::::tabs{sync=os}
:::tab[Windows]
Click the address bar of File Explorer, type `%LOCALAPPDATA%\Strata\Logs` and press **Enter**. Open `StrataEditor.log`
in the code editor of step 10: right-click it and choose "Open with".
:::
:::tab[Linux]
Open Files, press **Ctrl+L**, type `~/.local/share/Strata/Logs` and press **Enter**. Open `StrataEditor.log` in the
code editor of step 10. A computer that sets the variable `XDG_DATA_HOME` keeps it there instead.
:::
:::tab[macOS]
In Finder, choose "Go", then "Go to Folder...", type `~/Library/Application Support/Strata/Logs` and press **Return**.
Open `StrataEditor.log` in the code editor of step 10.
:::
::::

The editor also shows its facts in **Help ▸ About Strata**: rows for the version, the platform, the GPU, the driver and
the graphics interface. A report of a problem needs those rows and the log. The [issues page](https://github.com/2042Third/GameEngine/issues) of the project takes them.

## Result

Strata is unpacked in a folder that you keep together, the editor starts, and you can run a program with an argument
from a terminal. A compiler, CMake and a code editor stand ready. The editor searches for the build tools only at its
first build, so the check is in [your first game](../start/first-game.md): **Play** on the Tetris copy builds its
scripts, or the build says what to install.

## Variations

- **A computer without a usable GPU.** `StrataEditor --no-gpu` runs the editor without a window, for automation and
  for exports. Games run without a window with `--headless`.
- **Another Linux distribution.** The release needs `glibc` 2.39 and the C++ library of `GCC` 14, plus the Vulkan loader,
  a Vulkan driver, `GTK` 3 and the libraries of `X11` or `Wayland`. Find the packages of your distribution by the names in the
  step 6 command.
- **Two releases side by side.** Unpack each into its own folder. Each folder is an installation with its own
  `StrataInstall.json`, so each editor uses its own script kit, and both use the same user data folder.
- **Strata from source.** Building the engine needs git and its **submodules**, the repositories of other projects that
  a repository pins at one commit. The page [your first change](../core/first-change.md) does it.
- **The engine's build and your scripts' build.** Both name their options in a **CMake preset**, a named set of build
  options in the file `CMakePresets.json`, which one short command applies.

## Summary

- The unpacked folder is one installation: the editor finds the runtime, the script kit and the samples next to itself,
  and `StrataInstall.json` marks it.
- Run a program of the current folder with `./` and an argument; on Windows pipe a windowed program's output into
  `Write-Output` so that PowerShell waits.
- Start the editor from the folder; when it cannot, update the graphics driver, install the extra pieces of your system
  and read the log.
- The editor's log is in your user data folder, and **Help ▸ About Strata** shows the same version and GPU.
- The build tools are Visual Studio's C++ tools on Windows, a compiler with CMake and Ninja on Linux, and the Command
  Line Tools with CMake on macOS.

## Check yourself

1. A friend moves only `StrataEditor` out of the folder, onto the desktop. Name three things the editor can no longer
   find next to itself.

   :::answer{tests="keep-folder"}
   The runtime that it copies into exported games, the script kit that builds scripts, and the samples. The marker
   `StrataInstall.json` also stays behind, and it is what makes the folder an installation. Put the file back.
   :::

2. In PowerShell you type `.\StrataEditor --version` and the prompt returns with no text. Why, and what do you type?
   Which part is the program and which the argument?

   :::answer{tests="run-argument"}
   The editor is a windowed program, and PowerShell does not wait for one unless its output is piped, so the answer
   is lost. Type `.\StrataEditor --version | Write-Output`. `.\StrataEditor` is the program, a file of the current
   folder, and `--version` is the argument.
   :::

3. The editor shows "cannot start: no usable graphics device was found". Name two causes and the file that says more.

   :::answer{tests="start-editor, find-log"}
   The GPU lacks Vulkan 1.2 or cube map arrays, or its driver is old or missing (on macOS, MoltenVK). Install or update
   the driver or the Vulkan SDK. The message names the log, `StrataEditor.log` in the `Logs` folder of your user data
   folder.
   :::

4. Which tools does the editor search for on your system, and when?

   :::answer{tests="name-build-tools"}
   Visual Studio 2022 (17.10 or later) or 2026 with the C++ workload and a CMake that knows it, on Windows. A compiler,
   Ninja or Make, and CMake 3.25 or later, on Linux. The Command Line Tools and CMake, on macOS. The editor searches
   when it first builds scripts, and says what is missing.
   :::

5. Which two lines of the log match rows of **Help ▸ About Strata**?

   :::answer{tests="find-log"}
   The first line, `Strata Editor <version> (<system>)` after the time, `[info]` and `App:`, matches Version and Platform. The line with `Graphics device:` matches GPU, Driver and the row `Graphics API`.
   :::

## Exercises

1. **Basic.** Run `StrataEditor --version` in the way your system needs, and compare the number it prints with the
   name of the archive.

   :::answer[Worked solution]{tests="run-argument"}
   The output is `Strata Editor` followed by a number, and the number is the one in `Strata-<version>-<system>`, without an ending such as `-rc1`. If
   they differ otherwise, you are running another release from another folder: check the prompt's folder.
   :::

2. **Medium.** After the first start, find the version and the GPU in the editor's log, and compare them with the rows
   of **Help ▸ About Strata**. As a command, `editor.status` returns the same version.

   :::answer[Worked solution]{tests="find-log, start-editor" solution="tutorials/start/install/exercise-2.tutorial.json"}
   In `StrataEditor.log` the first line ends in `Strata Editor <version> (<system>)`, after the time, `[info]` and `App:`.
   A later line ends in `Graphics device: <GPU> (Vulkan <version>, driver <version>)`. The rows Version, GPU, Driver and `Graphics API` of the dialog show the
   same values. The file runs `editor.status`, whose `engineVersion` is that version, and reads the log's first line
   with `log.read`.
   :::

## Where it lives in Strata

- `Docs/Releases/PackageReadme.md` is the archive's `README.md`; `CMake/StrataPackaging.cmake` lists what the folder
  holds, its names and its marker.
- `StrataEditor/src/Editor/ScriptToolchain.cpp` searches for the build tools and writes the messages that name what is
  missing.
- `StrataEditor/src/EditorApplication.cpp` answers `--version` and opens the editor's log.
- `Strata/src/Strata/Renderer/GraphicsModule.cpp` writes the message of a start without a usable GPU.

## Further reading

- The project's [releases page](https://github.com/2042Third/GameEngine/releases): the archives and the notes of each
  version. Beginner.
- [CMake's tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html): what CMake does with a project's
  files. Intermediate.
- [Microsoft's guide to C++ in Visual Studio](https://learn.microsoft.com/en-us/cpp/build/vscpp-step-0-installation):
  the installer and its workloads. Beginner.

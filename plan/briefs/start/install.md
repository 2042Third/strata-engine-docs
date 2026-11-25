# Brief: `start/install`

| Field | Value |
| --- | --- |
| Title | Installing Strata and the C++ build tools |
| Kind | H |
| Size | M |
| Tracks | G, E, B |
| Needs | `start/how-to-read` |
| From | gamedev "Installing Strata" (§1.1: release archives, requirements, first start, script toolchain discovery, logs); PackageReadme "Requirements", "First start"; Manual/Scripting "Where builds happen"; tabs per OS; the terminal skills it teaches, per OS: open a terminal, change folder (`cd`, `~`), run a program of the current folder with arguments (`./`, `.\`), quote a path, paste a command, and on Linux `sudo`; the commands are those of PackageReadme (on Windows `.\StrataEditor --version \| Write-Output`, because PowerShell waits for a windowed program only when its output is piped; on macOS `xattr -dr com.apple.quarantine <folder>` and `xcode-select --install`; on Linux `sudo apt install g++ cmake ninja-build`); use home of the terminal for game makers; a code editor (VS Code or Visual Studio Community). Building from source is `core/first-change`'s |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/install` — Installing Strata and the C++ build tools

**Covers.** The goal: Strata unpacked and started on the reader's computer, with the C++ build tools and a code editor
installed, so that `start/first-game` can build scripts. What must be true first: a computer that meets the release's
requirements (Windows 10 or 11 on x64, Ubuntu 24.04 or newer on x64, macOS 14 or newer on Apple silicon) and a GPU whose
driver offers Vulkan 1.2 with cube map arrays; the operating system, the GPU, the driver and Vulkan each get one plain
sentence, and the reader updates the graphics driver. The steps, in tabs per system: download the archive of the system
from the releases page (`Strata-<version>-windows-x64.zip`, `-linux-x64.tar.gz`, `-macos-arm64.tar.gz`); on Windows tick
**Unblock** in the file's Properties before unpacking; unpack it and keep the folder together, with a table of what it
holds (the editor, the runtime that plays exported games, the CLI, the samples, the script SDK, the guides, the skills,
`StrataInstall.json`), stating the five samples and ten guides of the pin rather than the README's stale lists (the
erratum); the system's extra pieces (the Linux package line; on macOS MoltenVK through the Vulkan SDK's installer). Then
the terminal at the use level, as `book.md` makes this page its first use for game makers (the terminal's home is
`basics/tools`, linked once): open a terminal on each system, change folder with `cd` and `~`, quote a path with spaces,
paste a command, and `sudo` on Linux; on macOS the quarantine mark is removed with
`xattr -dr com.apple.quarantine <folder>`. Then the first program run with an argument from the current folder:
`./StrataEditor --version`, and on Windows `.\StrataEditor --version | Write-Output`, with the reason in two sentences
(the editor is a windowed program, and PowerShell waits for one only when its output is piped). Then the editor started
by a double-click: the launcher appears; SmartScreen's **More info ▸ Run anyway** when the archive was not unblocked;
the message the editor shows when it finds no usable GPU, and the log it names. Then the C++ build tools: Visual Studio
2022 (17.10 or later) or 2026 with the "Desktop development with C++" workload (its C++ CMake tools bring CMake),
`sudo apt install g++ cmake ninja-build`, or `xcode-select --install` with CMake from CMake.app; CMake and a toolchain
are defined in one sentence each. Then a code editor: VS Code, or Visual Studio Community on Windows, which the previous
step installed, and how to open a folder in it (later pages open a project's `Scripts` folder this way).

The steps end with the build tools installed; no step checks them, because the editor looks for a toolchain only when it
first builds. `## Result` says that the first build, in `start/first-game`, is the check: Play on the Tetris copy builds
its scripts, or a toast names what to install. "When something goes wrong" closes the steps: the log is defined (the
lines Strata or a game writes about what it is doing), the editor's log under the user data folder of each system, a
game's log beside it, and **Help ▸ About Strata** with the version, the GPU and the driver. Variations: a computer
without a usable GPU (`StrataEditor --no-gpu` runs without a window, for automation and exports); another Linux
distribution (glibc 2.39 and the C++ library of GCC 14); two releases side by side in two folders. Two exercises are
done: the reader runs `StrataEditor --version` and compares what it prints with the archive's name, then finds the
version and the GPU in the editor's log and in **Help ▸ About Strata**. At the end the reader can unpack and start
Strata, run a program with an argument from a terminal on their system, find the editor's log, and name the build tools
the editor will use.

**Leaves out.**

- Building Strata from source, git and the presets → `core/first-change`, `engineering/building`
- The terminal in full: paths, exit codes, the standard streams, environment variables → `basics/tools`
- Why Windows programs are console or GUI programs, and exit codes → `core/platform`
- How the editor finds and uses the toolchain when it builds → `editor/script-builds`
- Choosing the code editor inside Strata (the External Editor preference) → `make/first-script`
- Running exported games and their options → `make/export`
- Vulkan, the device and MoltenVK as the renderer uses them → `gpu/vulkan-nvrhi`

**Fit.** `over`: about 4,350 words against M (3,000). Ten steps for B0, most in three tabs (each tab is text of its
own), with the terminal from zero, the folder's table, the variations and the two exercises, pass M's top of 4,000; by
S2 the page takes the next size, L (5,000), with its title unchanged.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:20` | feature | home | The release archive of each system and what its folder holds, as a table; the folder stays together |
| `gamedev:21` | feature | home | The requirements (Vulkan 1.2 with cube map arrays, the driver, the Linux packages, MoltenVK on macOS) and the first start of unsigned programs (Unblock, SmartScreen, the quarantine mark) |
| `gamedev:22` | feature | home | The C++ build tools of each system, which the editor looks for at its first build and names when they are missing; the build itself is `start/first-game`'s |
| `gamedev:23` | feature | home | The editor's log and a game's log under the user data folder of each system: "When something goes wrong" |
| `gamedev:24` | feature | home | The editor and games are windowed programs: no console window, and PowerShell waits only when the output is piped (`.\StrataEditor --version \| Write-Output`) |
| `gamedev:611` | term | home | CMake and toolchain, defined where the reader installs them; the glossary step homes the entry's third term, "preset", on `make/script-builds` (start-q6) |
| `gamedev:697` | open | home | The stale lists of the archive's README: the page states the folder as it is, `new:12` |
| `new:11` | concept | home | The terminal at the use level, per system: open one, change folder (`cd`, `~`), run a program of the current folder with an argument (`./`, `.\`), quote a path with spaces, paste a command, `sudo` on Linux; `book.md` makes this page the first use of the terminal for game makers, and the terminal's words are linked once to their home, `basics/tools`. General knowledge. |
| `new:12` | erratum | home | The archive's `README.md` lists four samples, without the High Desert Outpost, and nine guides, without `Graphics.md`; the page states what the folder holds: five samples and ten guides. Evidence: `Docs/Releases/PackageReadme.md:18, 20`, installed as `README.md` by `CMake/StrataPackaging.cmake:65`; `Samples/Samples.json:6-38` (five samples; the whole folder is installed by `CMake/StrataPackaging.cmake:68`); `Docs/Manual/` holds ten guides, `Graphics.md` among them, all installed by `CMake/StrataPackaging.cmake:83` |
| `new:13` | concept | home | A code editor installed (VS Code, or Visual Studio Community on Windows); the editor lists VS Code, the Visual Studio it builds with and CLion when it finds them. Evidence: `Docs/Manual/Scripting.md:74-78` |
| `new:24` | hands-on | home | Two exercises, done: **Basic.** command: `StrataEditor --version` (on Windows piped to `Write-Output`) prints `Strata Editor <version>`, compared with the version in the archive's name; **Medium.** after the first start, in `Logs/StrataEditor.log` under the user data folder, the line `Strata Editor <version> (<system>)` and the line `Graphics device: <GPU> (Vulkan <version>, driver <version>)` are found and compared with the Version, GPU, Driver and Graphics API rows of **Help ▸ About Strata**. Evidence: `StrataEditor/src/EditorApplication.cpp:267-272` (`--version`); `StrataEditor/src/EditorApplication.cpp:283-288` (the log file and its first line); `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:296` (the device's line); `StrataEditor/src/UI/AboutDialog.cpp:50-58` (the About rows) |
| `build-test:209` | feature | use | `StrataInstall.json`, the marker that makes the folder an installation: why the folder stays together |
| `build-test:210` | feature | use | The archive's name and form on each system: a ZIP on Windows, a `.tar.gz` elsewhere |
| `render-core:32` | feature | use | What the GPU must offer (Vulkan 1.2, cube map arrays), in the reader's words; the selection of the device is `gpu/vulkan-nvrhi`'s |
| `render-core:46` | feature | use | MoltenVK on macOS, named as the piece to install |
| `render-core:681`, `render-core:682` | term | use | Vulkan and MoltenVK in one plain sentence each, before their home in `gpu`: each is named once inside a link to its home (a forward mention, `style.md` §3), and no question of the page needs the term |
| `scripting:147` | feature | use | The editor finds the toolchain at its first build: named, and tried in `start/first-game` |
| `foundation:439` | figure | use | The message the editor shows without a usable GPU, in the "If you do not see it" of the first start |
| `foundation:313` | concept | link | Why PowerShell does not wait for a windowed program, linked to `core/platform` for track E |
| `editor-ui:216` | feature | use | **Help ▸ About Strata**: the version, the GPU and the driver, for a report |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What Strata and its editor are | `start/welcome` | helps |
| Reading a step's tabs per system and a command line in a code block | `start/how-to-read` | helps |

**Starting state.** A computer that meets the requirements, with a web browser and nothing of Strata on it. No
checkpoint: the page starts no project.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `build-tools` | build tools | C++ build tools, toolchain |
| `cmake-preset` | CMake preset | - |
| `driver` | driver | device driver |
| `gpu` | GPU | graphics processing unit, graphics card |
| `log` | log | - |
| `operating-system` | operating system | OS |
| `submodule` | submodule | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-start-8 | should | missing-item | `gamedev:61` on `start/first-game` (section 5) | Nothing makes Strata open `Spinner.cpp` in the code editor that `start/install` installed. Without an External Editor setting the file goes to the system's application for `.cpp` files, which may be none: then the editor fails with a message that names the command `script.setExternalEditor`, which the reader cannot run. Choosing the editor is left to `make/first-script`, which track E never reads, and track E edits this project's script on `basics/programming-1`. | The page's `use` row of `gamedev:61` widens: one step before the file is opened, **Scripts ▸ External Editor...**, a click on the code editor it lists (VS Code or Visual Studio), then **Apply**. `make/first-script` keeps the home and the whole page. About 80 words. | `allocation/start.md:180`, `:248-249`, `:313`; `allocation/make-a.md:809`; `book.md:66-67`; `StrataEditor/src/Editor/ExternalEditor.cpp:387-391`; `StrataEditor/src/EditorLayer.cpp:1603`; `Docs/Manual/Scripting.md:76-91` |
| critic-start-10 | should | missing-item | `gamedev:23` and `new:24` on `start/install` | The page sends the reader to the editor's log in the user data folder, but not along the way there. On Linux (`~/.local/share`) and macOS (`~/Library/Application Support`) the folder is hidden in the file browser, and on Windows it is `%LOCALAPPDATA%`, a name the reader cannot click to. Hidden files and paths written as text are on G0's "Has not" list, and `make/editor-tour`, which shows hidden files, comes later. The second exercise depends on it. | "When something goes wrong" adds the way to the folder in OS tabs: on Windows `%LOCALAPPDATA%\Strata\Logs` typed into File Explorer's address bar; on macOS Finder's **Go ▸ Go to Folder...** with `~/Library/Application Support/Strata/Logs`; on Linux Files with Ctrl+L and `~/.local/share/Strata/Logs`; then the log opened in the code editor. About 120 words. | `allocation/start.md:165-166`, `:195`, `:202`; `Docs/Releases/PackageReadme.md:74-77`, `:125-127`; `style.md:64-65`; `allocation/make-a.md:109`; `StrataEditor/src/EditorApplication.cpp:283-287` |
| critic-start-11 | should | missing-item | `start/install`; `new:18` on `start/what-an-engine-is` | R21 says that `start/install` states only what the engine's repository says of the engine's terms at the pin, and no row of the page holds it. The repository has no license file. The folder's `ThirdPartyNotices.md` lists the components' licenses and the attributions that games made with the samples' assets must show, and the page's table of the folder leaves that file out. The survey of `start/what-an-engine-is` has a licence column and a row for Strata, and nothing says what its cell holds. | A new item (feature) on `start/install`: one or two sentences after the folder's table, which gains `ThirdPartyNotices.md` (about 60 words). The Strata row of `new:18` says the same in its licence cell, and no more (about 15 words). | `critique/rulings-6.md:59-61`, `:337`; `allocation/start.md:145-147`, `:414`; `allocation/appendix.md:642`; `git ls-tree --name-only 822a7a46` lists no license file; `Docs/Releases/PackageReadme.md:23` |
| critic-start-15 | should | stale-item | `gamedev:21` on `start/install` | The Covers starts the editor by a double-click on every system. The release's README does that only on Windows: on macOS and Linux it starts `./StrataEditor` from the folder in a terminal, on macOS after the quarantine mark is removed. I did not run Finder or Ubuntu's Files, so what a double-click does there is not settled here. | The first start goes in OS tabs: Windows by a double-click (with SmartScreen, as planned); macOS and Linux with `./StrataEditor` in the terminal that the page has just taught, as the README says. If the writer keeps a double-click there, the photographer's run settles what it does first. About 60 words. | `allocation/start.md:150-156`; `Docs/Releases/PackageReadme.md:64-72` |

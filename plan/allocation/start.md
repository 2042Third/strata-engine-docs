# Allocation: start

## `start/welcome` — What Strata is and what this book teaches

**Covers.** The page opens on what a reader can make, shown before it is named: the launcher's sample cards (Tetris,
the Third-Person Adventure, the High Desert Outpost) and the archive README's first sentence, that Strata is a 3D game
engine with an editor that people and AI agents drive the same way. It defines the editor (`StrataEditor`, the program
in which a game is made, its levels laid out and played) and names the game engine once, inside a link to
`start/what-an-engine-is` with a plain description. Then the maker's journey map: install, the launcher, a project from
a template, building the scene, assets, scripts, playing and testing, the export and the folder a player runs, each box
naming the part of `make` that teaches it. The game maker's door says three things plainly: game logic (defined in a
sentence) is C++ code that the editor builds for you; Strata has no visual scripting (defined in a sentence; the
not-done entry), and the book teaches the C++ a game needs from zero; an AI agent can build a game through the same
commands that the person's clicks run, which `make/with-an-agent` teaches. Then the three doors as one table: make a
game (track G), understand or change an engine (track E), learn from zero (track B), each with who it is for, the page
it starts with and the page it ends with. The beginner's paragraph says where track B goes after its last primer: on
track G from `make/gameplay-math`, or on track E from `core/map`; and that track G is open to it already after
`make/project-coin-run`. The three platforms are named once, with a link to `start/install`. The concept shape is
compressed to the size: the problem is the reader's own (I want to make a game, or to understand one), and the
approaches are the doors. The exercise gives three readers in a
sentence each, and the reader names each one's track, its first and last page and, for the beginner, where it
continues; it is answered, not done, because the page comes before `start/install`. At the end the reader can say what
Strata is, choose a track, and name the page where the track starts and, for a beginner, where it continues.

**Leaves out.**

- What a game engine is, the frame, and the survey of engines → `start/what-an-engine-is`
- The tracks' badges, the kinds of page and the strips, used on every page → `start/how-to-read`
- Why game code is C++ in a module of its own, and how other engines script → `scripting/why-scripts`
- Making a game with an AI agent, step by step → `make/with-an-agent`
- What the release archive holds and what each platform needs → `start/install`
- Everything Strata does not do → `appendix/not-in-strata`

**Fit.** `fits`: about 1,950 words against S (1,500). The four sections (what Strata is, with the problem and the naive
answer; the journey map; the game maker's door; the three doors) take about 950 words, and the example, the common
mistakes and the exercise about 400; the fixed parts take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:396` | figure | home | The maker's journey map: install, launcher, project from a template, scene building, assets, scripts, play and test, export, the exported folder; each box names its panel and the `make` page that teaches it |
| `gamedev:570` | term | home | Editor: `StrataEditor`, the program in which games are made; defined in the first section |
| `new:1` | not-done | home | No visual scripting: game logic is C++ script classes, written as text and built by the editor; the paragraph names how other engines do it (Unreal's Blueprints) and links `appendix/not-in-strata`. Evidence: `git grep -niE "visual script\|node graph\|nodegraph\|blueprint\|imnodes\|node editor" 822a7a46 -- Strata/src StrataEditor/src` finds only miniaudio's node graph in `Strata/src/Strata/Audio` (`AudioEngine.cpp:240`, `AudioVoice.cpp:155, 306`, `AudioVoice.h:30, 77`), which is not scripting; `AGENTS.md:271` |
| `new:2` | concept | home | The three doors and their tracks (G, B, E): who each is for, its first and last page, and where track B continues (`make/gameplay-math` on G, `core/map` on E, or G after `make/project-coin-run`); the plan asks for it in `book.md`, "Tracks", and `tracks.md`, "Rules". General knowledge. |
| `scripting:243` | concept | use | Game logic is C++ code kept outside the engine, as one paragraph of the game maker's door (`book.md` names this page the use of "Why game code lives outside the engine"); the reasons are `scripting/why-scripts`' |
| `automation:269` | concept | link | An AI agent can drive the editor through the commands a person's clicks run; one sentence, linked to `make/with-an-agent` (track G's use home; `automation/agents` is the home) |
| `gamedev:20` | feature | link | The three platforms of the release archives, named once and linked to `start/install` |
| `new:21` | hands-on | home | The exercise (**Basic.**, answered): three readers in a sentence each (one wants to make a small game, one has never written a program, one wants to know how an engine draws its pictures); the reader names each one's track, the page it starts with and the page it ends with, and where the beginner continues. The page comes before `start/install`, so the exercise is answered, not done (`style.md` §8); the plan asks for it in `critique/rulings-7.md`, R32 (D27). General knowledge. |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is, named once in a link | `start/what-an-engine-is` | helps |
| What a programming language is, for "game logic is C++" | `start/how-to-read` | helps |
| The tracks' badges and the "next page" links | `start/how-to-read` | helps |

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

## `start/first-game` — Your first game

**Covers.** What you will make: after playing a finished game, a project of your own in which a cube falls onto a ramp,
slides and bounces, and another one spins, turned by a C++ script you changed. What you need: the editor, the C++ build
tools and the code editor of `start/install`. Five step sections, each a stage of the page's tutorial file and each
ending in a checkpoint with its "You should now have" picture; at most four new terms per section. 1, "Play a finished
game": start the editor and meet the launcher (its cards, **New Project**, **Open Sample...**); **Open Sample... ▸
Tetris** makes a copy in a folder the reader chooses (launcher and sample defined); **Play** builds the copy's scripts
first, the status bar saying "Building to play" (build and Play defined): this first build is the check of the build
tools that `start/install` installed, and its "If you do not see it" is the toast that names what to install; the game
runs in the Game view with the keys of the sample's README, after a click in the view; **Stop**. 2, "Make a project":
**File ▸ New Project...**, the Basic 3D template, a name and a folder; the template's scene and its five entities in the
Hierarchy (Main Camera, Sun, Sky, Ground, Post Process), with project, template, scene and entity defined (the Tetris
copy of section 1 was a project too, which this section says). 3, "Place and move a cube": **+ ▸ Cube** puts a cube on
the ground where the view looks; the Inspector lists its components (component defined); the Move, Rotate and Scale
gizmos (W, E, R) lift, turn and stretch it, the green arrow pointing up, and Ctrl+Z undoes a drag; the Scene view and
the Game view are told apart; **Play** shows the scene through the Main Camera, and **Stop** puts back what changed
while playing, because Play runs a copy of the scene. 4, "Make it fall": **Add Component ▸ RigidBody** on the lifted
cube (Dynamic is the default; the ground already has a collider), and Play: it falls and rests; a second cube, scaled
long and tilted, makes a ramp, and the falling cube slides down it; Friction (how much two surfaces grip) and
Restitution (how much it bounces) are changed, and a bounce is seen. 5, "Make it spin with a script": a third cube
without a RigidBody, placed above the scene (one sentence says why: a body that physics moves is not also turned by a
script); **Scripts ▸ Build Scripts** (Ctrl+B) builds the `Spinner.cpp` that every new project has; **Add Component ▸
Script** offers the built class `Spinner` (script and script class defined); Play: it turns. The file opens from the
Content Browser's **Scripts** in the code editor (or the system's application for `.cpp` files) and is read with the
method of `start/how-to-read`: its parts are named in a sentence each (a class built on `Script`, `OnUpdate` marked
`override`, the registration with `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`), which `make/first-script` and
`basics/programming-3` teach; `deltaTime` is named in one sentence with a link to `start/what-an-engine-is`.
`DegreesPerSecond` goes from 90 to 360, Ctrl+B, Play: it turns four times as fast (the entity holds no value of its own
for the field, so the code's default applies; the tutorial's run confirms it). Then an `OnCreate` with one `Log::Info`
line is added (in `OnCreate`, so that the line is written once and not every frame), built and played, and the line is
read in the **Console** panel; on track E this is the playground of `basics/programming-1`. "What next" names each
track's next page (`start/what-an-engine-is` for all three) and `make/with-an-agent`. Three exercises, done in the
project: the falling cube's GravityScale set to 0.2 (predict, then run); `DegreesPerSecond` set to -90 (predict, then
run: it turns the other way); the `Log::Info` line moved from `OnCreate` into `OnUpdate`, which fills the Console with a
line every frame, and moved back. At the end the reader can open and play a copy of a sample, make a project from a
template, place and move entities, give one a physics body, attach, build and change a script, and read what it writes.

**Leaves out.**

- The editor's panels, menus and navigation in full → `make/editor-tour`
- What a new project writes, and the project folder → `make/project-files`
- Entities and components as a game maker builds levels from them → `make/scenes-entities`
- Positions, rotations and units as numbers → `make/transforms-units`
- Bodies, colliders, layers and triggers → `make/physics`
- New Script, the script's parts, hot reload and the crash toast → `make/first-script`
- The template's lighting → `make/lighting`
- Samples as copies, and the other four samples → `make/samples`
- Play, Simulate, Pause and Step, and edits while playing → `make/play-test-debug`
- How the editor and the launcher work inside → `editor/projects`, `editor-ui/launcher-dialogs`

**Fit.** `fits`: about 5,550 words against L (5,000). Twenty steps for B0 at about 150 words each take about 3,000
words; the terms defined in the steps, the five checkpoints, the `Spinner` file and the three exercises take most of
the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:30` | feature | home | The launcher as the reader first meets it: its cards, New Project and Open Sample; the agent card is named and left to `make/with-an-agent` |
| `gamedev:32` | feature | home | The Basic 3D template: the five entities of its scene, the ground with its collider; its lighting is `make/lighting`'s |
| `gamedev:438`, `editor-ui:549` | figure | home | The launcher with its template and sample cards and the agent card, at the first step; one recipe for both items (start-q8), which `editor-ui/launcher-dialogs` uses. At a first start "Recent projects" shows its empty note (`StrataEditor/src/Panels/WelcomePanel.cpp:487-490`), so the recent projects and their pictures that `editor-ui:549` names appear once projects exist |
| `gamedev:439`, `editor-ui:550` | figure | home | The New Project dialog with Basic 3D chosen, and the Open Sample dialog; one recipe for both items (start-q8), which `editor-ui/launcher-dialogs` uses |
| `gamedev:534` | hands-on | home | G1 as section 1: a copy of Tetris opened, played and stopped, its README's keys (the install is `start/install`'s) |
| `gamedev:535` | hands-on | home | G2 as sections 2 and 3: a Basic 3D project, a cube from "+", the gizmos, Play and Stop, the scene put back |
| `gamedev:536` | hands-on | home | G3 as section 4: a dynamic RigidBody, a ramp, Friction and Restitution |
| `gamedev:572` | term | home | Launcher |
| `gamedev:573` | term | home | Project |
| `gamedev:574` | term | home | Template |
| `gamedev:575` | term | home | Sample, always opened as a copy |
| `gamedev:576` | term | home | Scene |
| `gamedev:578` | term | home | Entity |
| `gamedev:579` | term | home | Component |
| `gamedev:594` | term | home | Gizmo |
| `gamedev:595` | term | home | Scene view and Game view |
| `gamedev:604` | term | home | Script and script class; the entry's "script module" is named once in a link to `make/script-builds`, where the glossary step homes it (start-q6) |
| `gamedev:596` | term | use | Play, defined here in one sentence in section 1; the entry's home is `make/play-test-debug`, and the glossary step homes "Play mode" on this page (start-q6) |
| `gamedev:254` | feature | use | The Tetris sample: its copy played, its README's keys |
| `gamedev:35` | feature | use | Open Sample makes a copy in a folder the reader chooses |
| `gamedev:33` | feature | use | A new project comes with `Scripts/Spinner.cpp`, named in one sentence |
| `gamedev:130` | feature | use | Play builds the scripts first; Ctrl+B builds them; the first build finds the toolchain |
| `gamedev:131` | feature | use | Add Component ▸ Script and the classes of the built scripts |
| `gamedev:125` | feature | use | `DegreesPerSecond`: the number in the code is the value the cube uses |
| `gamedev:359` | code | use | The generated `Spinner.cpp`, shown as the reader's own file; its home is `make/first-script` |
| `gamedev:539` | hands-on | use | G6's first half: Spinner attached and `DegreesPerSecond` changed; changing it while playing is `make/first-script`'s |
| `gamedev:46` | feature | use | The status bar's "Building" and "Building to play" |
| `gamedev:47` | feature | use | The toast of a failed build, which names what to install when the toolchain is missing |
| `gamedev:54` | feature | use | The Console, where the `Log::Info` line appears; the Problems panel named for a failed build |
| `gamedev:61` | feature | use | Where a script file opens: the code editor, or the system's application for `.cpp` files |
| `gamedev:48`, `gamedev:49` | feature | use | The Scene view's navigation as far as the steps need (orbit, frame with F), and the Game view while playing |
| `gamedev:50`, `gamedev:51` | feature | use | The Hierarchy's "+" menu and the Inspector's Add Component |
| `gamedev:69` | feature | use | The built-in cube |
| `gamedev:57` | feature | use | Ctrl+Z after a gizmo drag |
| `gamedev:222` | feature | use | Play runs a copy of the scene, and Stop restores the edited scene |
| `gamedev:152` | feature | use | A dynamic body on the cube against the ground's static collider; Friction and Restitution |
| `gamedev:328` | concept | use | Why the spinning cube has no RigidBody: physics moves a dynamic body, a script does not write its transform (one sentence) |
| `physics:28` | feature | use | The RigidBody component, its Type, Friction and Restitution as the Inspector shows them |
| `scripting:124` | feature | use | `Log::Info`, one line to the Console |
| `editor-ui:115` | feature | use | The toolbar's gizmo tools: Move (W), Rotate (E), Scale (R) |
| `editor-ui:214`, `editor-ui:215` | feature | use | The launcher and the New Project and Open Sample dialogs, as the steps use them |
| `editor-ui:685` | hands-on | use | "First launch: New Project with Basic 3D": its first part, as section 2 |
| `new:25` | hands-on | home | Three exercises, done in the page's project: **Basic.** predict, then run: the falling cube's GravityScale set to 0.2 in the Inspector, and it falls more slowly; **Medium.** predict, then run: `DegreesPerSecond` set to -90 in `Spinner.cpp`, built with Ctrl+B and played: the cube turns the other way, at a quarter of the step's 360 degrees a second; **Medium.** predict, then run: the `Log::Info` line moved from `OnCreate` into `OnUpdate` writes one line every frame, which the Console shows, and is moved back. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.cpp:128` (GravityScale, -100 to 100); `StrataEditor/src/Editor/ScriptProject.cpp:244-250` (the field and the turn about the Y axis by `DegreesPerSecond * deltaTime`); `StrataScriptCore/Include/StrataScript/Script.h:32-33` (`OnCreate` once, `OnUpdate` every frame) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor unpacked and started, the C++ build tools and a code editor installed | `start/install` | must |
| Where the editor's log is, for "If you do not see it" | `start/install` | helps |
| Reading code you do not understand yet, for `Spinner.cpp` | `start/how-to-read` | helps |
| Reading a step's two tabs and its "You should see" | `start/how-to-read` | helps |
| The frame and `deltaTime`, named once in a link | `start/what-an-engine-is` | helps |

**Starting state.** The editor, the C++ build tools and the code editor of `start/install`; no project and no
checkpoint of an earlier tutorial. Section 1 makes a copy of the Tetris sample in a folder the reader chooses (its
checkpoint is that copy, unchanged); section 2 makes a new project from the Basic 3D template, which sections 3 to 5
continue, each ending in a checkpoint of that project.

**Command-only steps.** none

## `start/what-an-engine-is` — What a game engine is: one frame, start to finish

**Covers.** The problem as the reader met it: in `start/first-game` the cube fell, slid and spun while nobody touched
anything, and a strip of six still pictures of that fall shows that the motion was a series of pictures. The naive
answer, a program that waits for clicks as a word processor does, breaks at once: the world changes without input. The
idea: a game is a loop, and one pass of it is a frame (read the input, change the game, draw a picture, show it); frame
rate and frame time are defined, frame time in milliseconds (1,000 ms divided by the frame rate: 16.7 ms at 60 frames a
second, 33.3 at 30, 6.9 at 144), and an `:::example` shows why frame time, not frame rate, is what adds up (a drop of 10
frames a second costs 3.3 ms from 60 to 50 and 16.7 ms from 30 to 20), and a hitch is one frame that takes far longer
than the frames around it. Delta time comes from the reader's own
`Spinner`: `DegreesPerSecond * deltaTime` turns the cube by the same angle each second at any frame rate, against the
newcomer's error of a fixed amount per frame. Then the frame map for people, the page's spine: one frame of the
reader's game in Strata's order (the frame's input; the scripts' updates and the animation; physics in small equal
steps, zero to several a frame, named once with a link to `core/time`; the late updates and the sound; the renderer
drawing the scene into pixels with the GPU's shaders, with renderer, pixel and shader defined in a plain sentence
each; the picture shown). Then the processor and the GPU as two workers: the GPU as `start/install` defined it, and
the processor in one plain sentence inside a link to its home, `basics/computer` (a forward mention); the processor
prepares the next frame while the GPU draws the one before, two lanes in a diagram (the mechanism, frames in flight, is
`gpu/how-a-gpu-frame-works`'). The status bar's frame pill is read with this in mind: it shows the work a frame takes,
not the time between pictures, so 4 ms at 60 frames a second is no contradiction (an exercise on the Tetris copy).
Then what an engine is, the term's home: the part every game shares (the loop, drawing,
physics, sound, input, loading assets, scenes), set against the game (its scenes, assets and scripts), the editor
(defined in `start/welcome`) and the runtime (the program that plays an exported game, copied under the game's name);
asset and export get one sentence each.

The approaches: a survey of engines as one table (general engines with an editor such as Unreal, Unity and Godot;
code-first engines such as Bevy; in-house engines), with the language of game code, the editor, the platforms and the
licence, each with a source in Further reading, and Strata's place among them. Strata's choice and its reasons, each in
a sentence with the page that teaches it: a C++ engine with an editor on three desktop systems; game code in C++ script
modules kept outside the engine, so that a crash in game code does not take the editor down and code can be rebuilt
while the game plays (`scripting/why-scripts`); every editor action a command that people, scripts and AI agents run
alike (`editor/commands`). What the choice cannot do: no mobile, console or web games (`core/platform`), no gameplay
networking (`appendix/networking`), linked to `appendix/not-in-strata`. Common mistakes: taking the editor for the
engine or for the game; moving by a fixed amount per frame; reading differences of frame rate as costs; expecting to
change engine files to make a game. Two exercises: frame times computed from frame rates and back (answered), and the
frame pill read on the Tetris copy while it plays (done). At the end the reader can describe one frame from input to
picture, compute frame time from a frame rate and back, explain why `Spinner` multiplies by `deltaTime`, and say what
the engine, the editor, the runtime and the game each are.

**Leaves out.**

- Strata's programs, libraries, modules and layers → `core/map`
- The frame loop's code, its stages and hooks, pacing and vsync → `core/frame-loop`
- Fixed steps, the accumulator and time scale → `core/time`, `make/script-loop`
- The script's callbacks in a frame → `make/script-loop`
- Frames in flight, fences and how a GPU draws → `gpu/how-a-gpu-frame-works`
- The renderer's passes, in order → `gpu/frame-tour`
- Measuring a frame: percentiles, "CPU, GPU or capped" → `core/profiling`, `make/performance`
- What an editor is as a program apart from the game → `editor/program`
- Scenes, entities and components as an engine stores them → `world/what-a-world-is`
- Strata's names for other engines' words → `start/coming-from`

**Fit.** `fits`: about 5,600 words against L (5,000). Seven ideas from zero (the loop and the frame, frame time, delta
time, the frame map, the two workers, the engine against the editor, runtime and game, the survey) at about 450 words
each, with three figures, take most of the page; the common mistakes and the two exercises take about 750 more, and the
survey is held to one table and two paragraphs.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:291` | concept | home | Engine, game, editor and runtime: the engine is the part every game shares, the editor the program for making, the runtime the player of exported games, the game its data (scenes, assets) and its script module; the error of expecting to change engine files to make a game |
| `gamedev:569` | term | home | Engine (game engine), placed here from `start/welcome`, which names it once in a link: the one-home table gives "What a game engine is" to this page |
| `gamedev:571` | term | home | Runtime, placed here from `start/install`, whose table names the `StrataRuntime` file without the term |
| `gamedev:614` | term | home | Frame and delta time, with `Spinner`'s `deltaTime` as the example |
| `new:14` | figure | home | The frame map for people: the frame's input, the scripts' updates and the animation, physics steps (zero to several), the late updates and the sound, drawing, the picture shown, in Strata's order. Evidence: `Docs/Architecture.md:790-804` (the application's frame); `Docs/Architecture.md:965-972` (the scene systems in update order: Animation in `OnUpdate` before Physics, Audio in `OnLateUpdate`); `Docs/Architecture.md:1012-1017` (the scene's update, fixed steps and late update) |
| `new:15` | figure | home | Two lanes, the processor and the GPU: the processor prepares frame N+1 while the GPU draws frame N. Evidence: `Strata/src/Strata/Renderer/GraphicsDevice.h:28` (`MaxFramesInFlight = 2`); `Docs/Architecture.md:298` |
| `new:16` | figure | home | Six still frames of the reader's cube falling onto the ramp, each with its frame number and time: motion as a series of pictures. Evidence: the scene of `start/first-game`'s fourth checkpoint, made from `StrataEditor/src/Editor/ProjectTemplates.cpp:49-95` and the Cube preset of `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-77` |
| `new:17` | concept | home | Frame rate and frame time: 1,000 ms divided by the frame rate, and why frame time is what adds up; worked as the page's example. General knowledge. |
| `new:18` | concept | home | A survey of engines (Unreal, Unity, Godot, Bevy, in-house engines) as a table of the language of game code, the editor, the platforms and the licence, each with a source; the plan asks for it in the outline's From (curricula 1.0). General knowledge. |
| `new:19` | concept | home | The processor and the GPU as the two workers of the frame map: the GPU as `start/install` defines it, and the processor in one plain sentence inside a link to `basics/computer`, the term's home (a forward mention, `style.md` §3; start-q5). General knowledge. |
| `new:26` | hands-on | home | Two exercises: **Basic.** frame times from frame rates and back (120 and 25 frames a second, 8 ms and 40 ms), answered; **Medium.** done on the Tetris copy: the status bar's frame pill is read while the game plays and while nothing happens, and the reader says why its milliseconds can be far fewer than 1,000 divided by its frame rate, and what "idle" means. Evidence: `StrataEditor/src/EditorLayer.cpp:1946-1966` (the pill: the work a frame takes, the frame rate, "idle", and the tooltip) |
| `gamedev:286` | concept | use | The game as a loop at the level of the frame, and the error of moving by a fixed amount per frame; frame and fixed updates are `make/script-loop`'s |
| `foundation:208` | concept | use | What an engine adds to a program, at a person's level; Strata's programs and libraries are `core/map`'s |
| `foundation:214` | concept | use | Why games loop instead of waiting for events; the loop's forms are `core/frame-loop`'s |
| `foundation:220` | concept | use | The stages of a frame in their order, as the boxes of the frame map; the hooks are `core/frame-loop`'s |
| `foundation:569` | term | home | Frame, one pass of the main loop: the same word as `gamedev:614`, defined once here (passed by `core`) |
| `foundation:228` | concept | link | The fixed step, named once in the frame map with a link to `core/time` |
| `foundation:234` | concept | link | Frame pacing and vsync, named in the frame pill's exercise and linked to `core/frame-loop` |
| `render-core:314` | concept | link | Frames in flight, the mechanism behind the two lanes, linked to `gpu/how-a-gpu-frame-works` |
| `gamedev:46` | feature | use | The status bar's frame pill (the work a frame takes and the frame rate), read in an exercise on the Tetris copy |
| `foundation:433` | figure | link | The frame pill and its tooltip, whose home is `core/profiling` |
| `gamedev:405` | figure | link | One frame from a script's side, linked to `make/script-loop` |
| `editor-core:290` | concept | link | What an editor is, and why it is a separate program from the game, linked to `editor/program` |
| `scripting:243` | concept | link | Why game code lives outside the engine, linked to `scripting/why-scripts` |
| `scene-ecs:271` | concept | link | What a scene is inside an engine, linked to `world/what-a-world-is` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor, a project from Basic 3D, its entities, Play and Stop, and the `Spinner` script with its `deltaTime` | `start/first-game` | must |
| The GPU, the part of a computer that draws pictures | `start/install` | must |
| The editor as the program in which games are made | `start/welcome` | helps |

## `start/coming-from` — Coming from Unity, Unreal or Godot

**Covers.** The goal: find in Strata what the reader used in Unity, Unreal or Godot, and the page that teaches it. What
must be true first: the reader has made something in one of those engines (the page is written for that reader, and
optional on both its tracks), has made the first game and has read `start/what-an-engine-is`. The page opens with the
map of names as one table per idea, a column per engine and one for Strata, each Strata cell linking its page: the thing
in a scene (GameObject, Actor, Node: entity); its parts (Component, ActorComponent, child nodes: component); reusable
groups (Prefab, Blueprint class, PackedScene: prefab, with per-property overrides and no variants or nested prefabs);
game code (C#, Blueprints and C++, GDScript: C++ script classes, no visual scripting); the callbacks (`Update`, `Tick`,
`_process`: `OnUpdate`; `FixedUpdate`, `_physics_process`: `OnFixedUpdate`); levels (Scene, Level, scene: scene); the
project's settings and input (Input System, Enhanced Input, the input map: input actions); assets and their folder;
building a game for players (Build, Package, Export: export). The steps then find each row in a copy of the Third-Person
Adventure: open its Course scene; select `Player` in the Hierarchy (an entity); read its components in the Inspector (a
CharacterController and a Script with `ThirdPersonPlayer`); find the Coin prefab in the Content Browser and a placed
coin whose overridden values show in bold; open `ThirdPersonPlayer.cpp` from the Content Browser's **Scripts** and find
its `OnUpdate`; open **File ▸ Project Settings...** and its Input Actions. Units and axes get a section of their own,
because imported content breaks there first: Strata is right-handed, Y up, -Z forward, in metres, with Euler angles in
degrees, as Godot is and unlike Unity (left-handed) and Unreal (Z up, centimetres); glTF models face +Z. `## Result`:
the reader's own map of names. Variations: a reader who knows a code-first engine (entities and components as in Strata,
an editor as in Unity); and what to look for elsewhere because Strata does not have it, each linked to the page that
says so through `appendix/not-in-strata` (nested prefabs and variants, visual scripting, mobile and web targets,
particles, terrain). The exercise is done in the sample's copy: the reader finds the camera that follows the player,
names its components in Strata's words against their old engine's, and finds the callback that moves it, `OnLateUpdate`,
against Unity's `LateUpdate`. At the end the reader can name Strata's word for each idea of their old engine and open
the page that teaches it.

**Leaves out.**

- Entities and components as a game maker builds with them → `make/scenes-entities`
- Prefabs, overrides, Apply and Revert → `make/prefabs`
- Axes, units and rotations → `make/transforms-units`
- The script's parts and the C++ they need → `make/first-script`, `basics/programming-3`
- The script's callbacks and their order → `make/script-loop`
- Input actions → `make/input`
- Exporting a game → `make/export`
- How object models differ inside an engine → `world/what-a-world-is`
- Everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 2,950 words against M (3,000). The map of names (about ten rows of four columns), six steps on
the sample's copy, the section on units and axes, two variations and the exercise take about 2,350 words; the fixed
parts take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:20` | concept | home | Strata's names for other engines' ideas (GameObject and entity, prefab variants and Strata's overrides, Blueprints and C++ scripts, the callbacks, the axes and units), the one-home table's row for this page; the other engines' side has its sources in Further reading. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-45` (Strata's callbacks); `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (a prefab made from linked entities keeps no inner links); `Docs/Architecture.md:250` (right-handed, +Y up, -Z forward, degrees) |
| `gamedev:298` | concept | use | Entities and components from the user's side, against GameObject subclasses and actor hierarchies; the use home is `make/scenes-entities` |
| `gamedev:306` | concept | use | Prefabs with per-property overrides, set against Unity's nested prefabs and variants and Unreal's Blueprints; the use home is `make/prefabs` |
| `gamedev:71` | feature | use | The conventions a maker must know (Y up, -Z forward, glTF models facing +Z, degrees, metres), set against each engine's; the use home is `make/transforms-units` |
| `gamedev:317` | concept | use | Scripts in C++ for a reader who wrote C#, GDScript or Blueprints: a class built into a module, `override`, fields registered by a macro; taught by `basics/programming-3` and `make/first-script` |
| `gamedev:255` | feature | use | The Third-Person Adventure, whose player, coin prefab, script and input actions the steps open |
| `gamedev:144` | feature | link | Input actions, linked to `make/input` |
| `scene-ecs:271` | concept | link | Object models (inheritance, components, ECS), linked to `world/what-a-world-is` for track E |
| `scripting:243` | concept | link | How other engines script and why Strata uses C++ modules, linked to `scripting/why-scripts` |
| `new:27` | hands-on | home | The exercise (**Basic.**, done in the copy of the Third-Person Adventure): the entity `Camera` of the Course scene is found, with its Camera component (Primary) and a Script with `FollowCamera` whose `Target` field names `Player`; the reader names what their old engine uses for it, and finds in `FollowCamera.cpp` that it moves in `OnLateUpdate`, which runs every frame after the fixed updates, as Unity's `LateUpdate` runs after `Update`. Evidence: `Samples/ThirdPerson/Assets/Scenes/Course.stscene:2` (the `Camera` entity, its components and the `Target` field); `Samples/ThirdPerson/Scripts/FollowCamera.cpp:43` (`OnLateUpdate`); `StrataScriptCore/Include/StrataScript/Script.h:33-35` (the callbacks' order) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, components, a scene, a script and Play, as the first game showed them | `start/first-game` | must |
| Opening a copy of a sample from the launcher | `start/first-game` | must |
| The engine, the editor and the runtime; the frame and delta time | `start/what-an-engine-is` | must |

**Starting state.** A copy of the Third-Person Adventure made with **Open Sample...** as `start/first-game` made the
Tetris copy, with its Course scene opened (the sample starts in its main menu scene). No checkpoint of an earlier
tutorial.

**Command-only steps.** none

## Passed on

none

## Not taken

none

## Questions for the planner

- `book.md`, the row "Building script modules" (`plan/book.md:329`), names `start/install` among the pages
  that link it with "(the toolchain check)". By R30 (D6) the check is the first build, on `start/first-game`, and
  `start/install` only installs the build tools and says that the editor looks for them at its first build. I propose
  "`start/install` (the build tools)" and `start/first-game` (the first build, the toolchain's check) in that cell.

# Brief: `worlds/game-identity`

| Field | Value |
| --- | --- |
| Title | A game's identity: the manifest, icons and platform files |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `worlds/export`, `basics/data-formats`, `basics/color`, `assets/robustness` |
| From | worlds-runtime §1.8 and ch. 8 (manifest v5 and why it is untrusted, `ProjectGameInfo`, `GamePresentation`, saves keyed by the manifest's Name, `GameIcon`, `PEResources`, `DesktopEntry`, the Dock icon, signing after export) |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `worlds/game-identity` — A game's identity: the manifest, icons and platform files

**Covers.** What a game is called, how it shows itself on each system, and why the runtime trusts its manifest only so
far. The problem: a game must keep its players' saves when it is renamed, and must look like an application in
Explorer, a Linux desktop's menus and the macOS Dock, while the files beside it may have been changed by anyone. The
manifest comes first: `.stgame` version 5 with its fields (name, title, version, company, copyright, icon, pack, patch
packs, start and loading scenes, script module, window, settings sections), versions 1 to 4 that still load, and
settings carried as stored for the runtime to validate once modules have registered. The plain-file-name rule follows:
every file the manifest names lies next to it, with no paths and no `.` or `..`, so that a manifest cannot point the
runtime at another folder. Then identity: `ProjectGameInfo` and its checks (at most 128 code points without control
characters, a version of up to four parts of at most 65,535), and `GamePresentation`, decided from the manifest alone
before anything starts: the window's title, the log's banner, the application id, and the data directory keyed by the
manifest's `Name`, never its title (its `Saves` and `Logs` folders), so that an update that renames the game keeps the
saves.

Each platform last: the icon made square on transparent pixels and resized in linear light with colors weighted by alpha
to ten sizes, a 256-pixel PNG beside the manifest and a warning for small sources; the Windows version resources and
icon group written into a PE32+ image by engine code without the Win32 API (read and checked before use, never
asserting), and why a signed runtime cannot be stamped, so games are signed after the export; the Linux desktop entry
with escaped values and a quoted `Exec`, which names the export folder's absolute paths (moving or shipping the folder
means editing its `Exec` and `Icon`), which the export writes beside the game but does not install, and whose
`StartupWMClass` is the executable's name, the reason the runtime's application id is the executable's stem; the macOS
Dock icon taken from the window's icon while the game runs. The pictures are the Game page of Project Settings and the
executable's Details tab with its icon. The not-done line says that a script cannot read the game's title or version,
and the exercises rename a game and break a manifest. At the end the reader can read a manifest and say which of its
fields the runtime trusts and how, and can say where an exported game's saves and logs go and why a rename keeps them.

**Leaves out.**

- The order of the export's work and its checks → `worlds/export`
- How the runtime starts from the manifest → `worlds/runtime`
- Settings sections, their versions and validation → `world/projects-settings`
- The players' graphics options file → `image/quality-settings`
- The Game page of Project Settings as a window → `editor-ui/settings-windows`
- Save files as game makers write them → `make/levels-saves`

**Fit.** `over`: about 4,700 words against M (3,000). The next size is L (S2): four excerpts, the manifest's fields
and checks, three platforms' files and two exercises take the most words; moving the icon and the version resources to
`worlds/export` no longer helps, since that page is over at M too.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:292` | concept | home | Game identity and platform integration: executable resources on Windows, desktop entries on Linux, the Dock on macOS, save folders keyed by a stable name; the mistake of keying saves on the title |
| `worlds-runtime:146` | feature | home | The `.stgame` manifest version 5 and its fields; versions 1 to 4 still load (`Strata/src/Strata/Project/GameManifest.h:18-79`; `GameManifest.cpp:28-202`) |
| `worlds-runtime:147` | feature | home | Every file the manifest names lies next to it |
| `worlds-runtime:335` | code | home | `Strata/src/Strata/Project/GameManifest.cpp:16-24`: `IsPlainFileName`; with lines 95-114, where the icon, the pack, each patch pack and the module are checked |
| `worlds-runtime:444` | rule | home | The manifest is untrusted input and names only files next to it |
| `worlds-runtime:148` | feature | home | `ProjectGameInfo`: title, company and copyright of at most 128 code points without controls, a version of 1 to 4 parts of at most 65,535, the icon as a texture handle (`Strata/src/Strata/Project/GameInfo.h:13-49`) |
| `worlds-runtime:133` | feature | home | `GamePresentation`: title, banner, data directory, icon file, application id, applied to the window's specification before anything starts (`Strata/src/Strata/Runtime/GamePresentation.h`, `GamePresentation.cpp`) |
| `new:8` | code | home | `Strata/src/Strata/Runtime/GamePresentation.h:12-30`: what the runtime decides from the manifest alone, the data directory keyed by `Name` |
| `worlds-runtime:149` | feature | home | The save and log directory keyed by the manifest's `Name` (`GameManifest.h:38-40`, `GamePresentation.h:18-21`; the inventory's `GamePresentation.h` 224-227 do not exist): saves under `<user data>/<Name>/Saves` (`SaveDirectory::ForGame`, `Strata/src/Strata/Core/SaveFiles.h:39-58`), the log at `<user data>/<Name>/Logs/Game.log` (`StrataRuntime/src/RuntimeApplication.cpp:457-459`) |
| `worlds-runtime:448` | rule | home | Saves are keyed by the manifest's `Name`, never the title: renaming the game keeps its players' saves |
| `worlds-runtime:163` | feature | home | The game icon: the texture's PNG, JPEG, TGA or BMP source (at most 16 MiB and 4,096 pixels) made square, resized to ten sizes, a 256-pixel PNG next to the manifest, a warning for small sources (`StrataEditor/src/Editor/GameIcon.h:10-63`) |
| `new:9` | code | home | `StrataEditor/src/Editor/GameIcon.cpp:34-64`: the square on transparent pixels, and the resize in linear light with colors weighted by alpha so that the border neither darkens nor tints the edges |
| `worlds-runtime:164` | feature | home | `PEResources`: a PE32+ resource section parsed and rewritten without the Win32 API; `StampGame` writes `VS_VERSIONINFO` and the icon group `GLFW_ICON`; signed images and unusual layouts refused (`StrataEditor/src/Editor/PEResources.h:15-102`) |
| `new:10` | code | home | `StrataEditor/src/Editor/PEResources.h:58-72`: `Read` checks every header, section and resource directory before reading and never asserts; `Write` rebuilds the resource section in place and refuses a certificate table |
| `worlds-runtime:459` | rule | home | A signed runtime cannot be stamped: sign the game after exporting it |
| `worlds-runtime:165-166` | feature | home | The Linux desktop entry with escaped values and a quoted `Exec` (`StrataEditor/src/Editor/DesktopEntry.cpp:34-115`); it names the export folder's absolute paths, so moving or shipping the folder means editing its `Exec` and `Icon`; the export writes it beside the game and does not install it; its `StartupWMClass` is the executable's name, which is why the runtime's application id is the executable's stem (`StrataEditor/src/Editor/DesktopEntry.h:11-22`; `StrataEditor/src/Editor/GameExport.cpp:714-723`; `Strata/src/Strata/Runtime/GamePresentation.h:23`; critic-worlds-runtime-7); the macOS Dock icon from the window's icon (`Strata/src/Platform/GLFW/GLFWApplicationIcon*`, to be read when the page is written) |
| `worlds-runtime:407` | figure | home | Project Settings, the Game page: title, version, company, copyright, icon |
| `worlds-runtime:401` | figure | home | The exported folder in the system's file browser, and on Windows the executable's Properties > Details tab and its icon |
| `new:22` | not-done | home | Reading the game's title or version from a script: the SDK has no call that returns them (book.md's entry; appendix-q2). Evidence: `Docs/Releases/0.7.0.md:363`; `git grep -ni title 822a7a46 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46`, `:125`; `ScriptABI.h:289`, `:299`), and `git grep -ni gameinfo 822a7a46 -- StrataScriptCore` finds nothing (run again at the pin: it holds) |
| `new:23` | hands-on | home | Exercise (D27), done with the editor and an exported game: change the game's title in Project Settings, export again into the same folder, run it, and find its saves and its log where they were, under the manifest's `Name`; then say what an update that changed `Name` would cost its players. Evidence: `Strata/src/Strata/Runtime/GamePresentation.h:18-21`; `StrataEditor/src/Editor/GameExport.cpp:302` (`Name` is the project's name); `Strata/src/Strata/Core/SaveFiles.h:39-58`; `StrataRuntime/src/RuntimeApplication.cpp:457-459` |
| `new:24` | hands-on | home | Trace it yourself (D27): a search for `IsPlainFileName` finds every field of the manifest it guards; then an exported `.stgame` whose `AssetPack` is edited to `../Other.stpak` is run, and the runtime refuses the manifest with the reason the code gives. Evidence: `Strata/src/Strata/Project/GameManifest.cpp:16-24`, `:95-114` |
| `worlds-runtime:553`, `worlds-runtime:558-560` | term | home | Game manifest, game identity, PE resources, desktop entry |
| `scene-ecs:692-693` | term | home | Game manifest, game identity, as the scene inventory words them (taken from `world`) |
| `worlds-runtime:191` | feature | use | `Editor.Export.GameIcon`, `Editor.Export.ExecutableResources` (`StrataTests/src/Editor/ExecutableResourcesTests.cpp`, not in the inventory) and `Editor.Export.DesktopEntry`; the CTests `StrataRuntime.Identity`, `.Icon`, `.GameIcon`, `.VersionInfo` |
| `scene-ecs:215-216` | feature | home | `ProjectGameInfo` and `GameManifest` as the scene inventory lists them (taken from `world`; taught with worlds-runtime:146 and 148 above) |
| `foundation:130` | feature | use | `SaveFiles` and `SaveDirectory`, which resolve the data directory |
| `editor-ui:228` | feature | link | The Project Settings panel's Game page as the editor-ui inventory lists it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The export and what its folder holds | `worlds/export` | must |
| JSON; UTF-8, code points and other encodings | `basics/data-formats` | must |
| Linear and sRGB values | `basics/color` | must |
| Untrusted input: validate before use | `assets/robustness` | must |
| Settings sections of a project | `world/projects-settings` | must |
| Paths and files you can trust | `core/files` | must |
| Resampling an image with a filter | `basics/signals` | helps |
| Premultiplied alpha | `light/clearcoat-transmission` | helps |
| Sources and cooked forms of an asset (the icon is made from the texture's source) | `assets/what-is-an-asset` | helps |
| A window's specification: title, icon, application id | `core/windows-events` | helps |
| The save service of a game (`IGameSaves`) as scripts use it | `scripting/host-api` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `desktop-entry` | Desktop entry | - |
| `game-identity` | Game identity | - |
| `game-manifest` | Game manifest | - |
| `pe-resources` | PE resources | - |

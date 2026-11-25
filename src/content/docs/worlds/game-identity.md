---
id: worlds/game-identity
title: "A game's identity: the manifest, icons and platform files"
description: "How an exported game names itself, shows its title and icon on each system, and keeps its saves when it is renamed, though its files may be altered."
kind: internals
size: M
tracks: [E]
needs: [worlds/export, basics/data-formats, basics/color, assets/robustness]
time: 60
learn:
  - id: manifest-trust
    text: explain which fields of a game manifest the runtime checks and why every named file must lie next to it
  - id: version-rules
    text: compute whether a version string is valid and the four numbers the executable stores for it
  - id: data-key
    text: explain why saves and logs go under the manifest's name and not its title, and find the folders
  - id: icon-pipeline
    text: explain how the export makes the icon square and shrinks it in linear light weighted by alpha
  - id: platform-files
    text: name what each system gets from the export and why a game is signed after it is exported
since: 0.6.0
status: final
---

An exported game is a folder of files, and the people who play it judge it by its name, its icon and whether their saves survive an update. This page covers where Strata keeps that identity, how each system shows it and how far the :term[runtime]{id=runtime} trusts it. The order of the export's work is on [the export page](export.md), and how the runtime starts is on [the runtime page](runtime.md).

## The problem and how engines solve it

Three needs meet here. A game must keep its players' saves when its title changes: a sequel, a spelling mistake or a translation must not strand a hundred hours of play. It must also look like an application. Windows Explorer shows an icon and a version in a file's properties, Linux desktops list programs from small description files, and the macOS Dock shows the icon of a running program. Last, the files beside the :term[executable]{id=executable} may have been changed by anyone, so the runtime must not obey them blindly.

Engines keep saves in one of two places. Saves next to the executable break when the folder moves or lies in a read-only place. Saves under the player's own data folder, in a folder named after the game, survive both. Strata takes the second way, and the name of that folder must never change by accident. That is why it comes from a field no menu shows, not from the title.

The second need has a different answer on each system. On Windows the icon and the version live inside the executable file. On Linux they live in a separate text file. On macOS a program with no application bundle gets its Dock icon only while it runs, from a call the program makes itself. Many engines hide this behind an installer; Strata ships a folder, so the export does the work.

The third need is the old one of [untrusted input](../assets/robustness.md). A manifest that said "my pack is `../../Documents/secret.stpak`" would make the runtime open files outside the game, so every name in it is checked.

## The map

The data starts in the project and ends in four kinds of place: the manifest, the icon file, the executable's own resources and, on Linux, a text file.

```mermaid caption="The project's identity fields flow into the manifest, the icon files and the executable, and the runtime reads the manifest again to decide what to show and where to keep saves." alt="A flow from the project's game information through the export to four outputs: the manifest, the icon image, the executable with its version resources on Windows and a desktop entry on Linux. The runtime reads the manifest and produces the window title, the log banner and the data folder."
flowchart LR
  P["Project: Name, Title, Version, Company, Copyright, Icon"] --> E["Export"]
  E --> M["Game.stgame"]
  E --> I["Game.png, 256 pixels"]
  E --> X["Game.exe stamped (Windows)"]
  E --> D["Game.desktop (Linux)"]
  M --> R["Runtime: GamePresentation"]
  R --> W["Window title and icon"]
  R --> B["Log banner"]
  R --> S["Saves and logs under Name"]
```

The Windows executable is a copy of the runtime with new resources, and the desktop entry exists only when the export runs on Linux. The macOS Dock icon is no file: the runtime sets it from the window's icon while the game runs.

## The contract

Callers of these types may rely on the rules below, and each rule has a reason.

- The **game manifest** is the file `<Name>.stgame` that the export writes next to the game's pack, script module and executable; it is :term[JSON]{id=json} that says what the runtime loads and how it presents the game. The runtime reads versions 1 to 5, and the reader supplies defaults for what older versions lack, so a game exported long ago still runs.
- Every file the manifest names lies next to it. A name has no folder part, is not absolute and is not `.` or `..`. The reason is trust: the manifest is data from disk, so it must not point the runtime at another folder.
- The manifest holds the project's :term[settings sections]{id=settings-section-world} exactly as stored. The reader runs before the engine's modules register their sections, so it cannot know yet what a valid value is. It checks only the shape and the size (at most 1 MiB), and the runtime checks the values later; [the settings page](../world/projects-settings.md) explains the sections.
- The **game identity** is the title, version, company, copyright and icon a game shows of itself. It is checked in the project and again when the manifest is read. The title, the company and the copyright line have at most 128 :term[code points]{id=code-point} and no control characters, and a version has one to four whole numbers of 0 to 65,535, separated by dots.
- The presentation is decided from the manifest alone, before anything starts, so nothing in it waits for the engine, the window or the pack.
- The manifest's `Name`, never its title, keys the data folder. This rule protects the players' saves.
- Code that reads an image, an executable or a manifest from disk never asserts on bad data. It returns a failure with a reason, and the export shows the reason.

:::rule[Bad data from disk is an error, not a crash]
An assertion marks a mistake of the programmer, and a damaged file is a mistake of the world. See [robust loading](../assets/robustness.md).
:::

## A toy version

The toy below checks three rules a reader can test by hand: plain file names, the version, and the key of the data folder.

:::question
Does the code below use functions, loops, `std::filesystem` and `std::string`? Read [functions and loops](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first if it looks strange.
:::

The sketch has three functions and a `main` that tries five file names, five versions and one name. Search for the order of the checks in `IsPlainFileName`, and for how `ParseVersion` treats the end of the text.

```cpp sketch="worlds-game-identity-toy.cpp"
// A toy manifest check: plain file names, a version of up to four parts, and the key of the data directory.
#include <cstdio>
#include <filesystem>
#include <string>

bool IsPlainFileName(const std::string& name)
{
	// "." and ".." are file names to the library, but they name a directory.
	if (name.empty() || name == "." || name == "..")
		return false;
	const std::filesystem::path path(name);
	return !path.has_parent_path() && !path.is_absolute() && path.filename() == path;
}

// Fills four numbers from a version such as "1.2"; false when the text is no version.
bool ParseVersion(const std::string& text, unsigned parts[4])
{
	for (int index = 0; index < 4; index++)
		parts[index] = 0;
	int count = 0;
	unsigned value = 0;
	bool hasDigits = false;
	for (size_t index = 0; index <= text.size(); index++)
	{
		// The end of the text closes the last part like a dot.
		const char character = index < text.size() ? text[index] : '.';
		if (character >= '0' && character <= '9')
		{
			value = value * 10 + static_cast<unsigned>(character - '0');
			hasDigits = true;
			if (value > 65535)
				return false;
		}
		else if (character == '.')
		{
			if (!hasDigits || count == 4)
				return false;
			parts[count++] = value;
			value = 0;
			hasDigits = false;
		}
		else
			return false;
	}
	return true;
}

// The folder name saves go under: the Name with path separators replaced.
std::string DataDirectoryName(std::string name)
{
	for (char& character : name)
		if (character == '/' || character == '\\')
			character = '_';
	return name;
}

int main()
{
	for (const char* file : { "Game.stpak", "../Other.stpak", "sub/Game.stpak", "/data/Game.stpak", ".." })
		std::printf("%-18s %s\n", file, IsPlainFileName(file) ? "accepted" : "refused");

	for (const char* version : { "1.2", "1.2.3.4", "1.2.3.4.5", "1.70000", "1..2" })
	{
		unsigned parts[4];
		if (ParseVersion(version, parts))
			std::printf("%-10s -> %u %u %u %u\n", version, parts[0], parts[1], parts[2], parts[3]);
		else
			std::printf("%-10s -> refused\n", version);
	}

	std::printf("Name 'Moon/Crab' keeps its saves under '%s'\n", DataDirectoryName("Moon/Crab").c_str());
	return 0;
}
```

```text output-of="worlds-game-identity-toy.cpp"
Game.stpak         accepted
../Other.stpak     refused
sub/Game.stpak     refused
/data/Game.stpak   refused
..                 refused
1.2        -> 1 2 0 0
1.2.3.4    -> 1 2 3 4
1.2.3.4.5  -> refused
1.70000    -> refused
1..2       -> refused
Name 'Moon/Crab' keeps its saves under 'Moon_Crab'
```

1. **Lines 9–12:** the names `.` and `..` are refused first, since the library treats them as plain names; then any name with a folder part or an :term[absolute path]{id=absolute-path} fails.
2. **Line 26:** the end of the text closes the last part like a dot.
3. **Line 31:** a part above 65,535 is refused as soon as it grows.

`../Other.stpak` and `sub/Game.stpak` fail because each has a folder part, and `..` fails because it names a folder. The version `1.2` gives 1, 2, 0, 0, since missing parts are zero, and `1.70000` fails because 70,000 does not fit in the 16 bits Windows keeps for each part.

## The manifest and the plain-name rule

A trimmed manifest of version 5 looks like this. It omits the company, the copyright, the scenes and the settings.

```json
{
	"Strata": { "Format": "Game", "Version": 5 },
	"Game": { "Name": "MoonCrab", "Title": "Moon Crab", "Version": "1.2.0",
		"Icon": "MoonCrab.png", "AssetPack": "MoonCrab.stpak", "PatchPacks": [],
		"ScriptModule": "MoonCrab.dll",
		"Window": { "Width": 1280, "Height": 720, "Fullscreen": false, "VSync": true } }
}
```

The :term[header]{id=header} names the format and the version. The reader refuses a manifest whose format is not `Game` and one whose version is 0 or above 5, with a message that names the versions it reads. Versions 1 to 4 load: version 4 lacks the settings and the identity, version 3 lacks the loading scene, version 2 lacks :term[patch packs]{id=patch-pack} and version 1 is a game without scripts. A manifest before version 5 has no title, so the game shows its `Name`, and it has no version, so the reader stores an empty one.

The next code guards every file name. Its comment gives the reason in one line.

```cpp src="Strata/src/Strata/Project/GameManifest.cpp#L16-L24" symbol="IsPlainFileName"
// Files a manifest names must lie next to it: a manifest cannot point the runtime elsewhere.
bool IsPlainFileName(const std::string& name)
{
	// "." and ".." are file names to std::filesystem, but name the directory or its parent.
	if (name.empty() || name == "." || name == "..")
		return false;
	const std::filesystem::path path = FileSystem::FromUTF8(name);
	return !path.has_parent_path() && !path.is_absolute() && path.filename() == path;
}
```

The reader applies it to the icon, the pack, each patch pack and the script module. A manifest may list at most 256 patch packs.

The identity part of the reader shows how little it assumes.

```cpp src="Strata/src/Strata/Project/GameManifest.cpp#L80-L88" from="ProjectGameInfo identity;" to="if (std::optional<std::string> problem = identity.Validate())" symbol="GameManifest::FromJson"
ProjectGameInfo identity;
identity.Title = JsonUtils::GetString(*game, "Title");
// An empty version names none, as before version 5: a manifest read from an older one is saved with an empty one.
const std::string gameVersion = JsonUtils::GetString(*game, "Version", identity.Version);
if (!gameVersion.empty())
	identity.Version = gameVersion;
identity.Company = JsonUtils::GetString(*game, "Company");
identity.Copyright = JsonUtils::GetString(*game, "Copyright");
if (std::optional<std::string> problem = identity.Validate())
```

The reader has already insisted that each identity field is a string, so a number in the place of a title is a clear error and not a silent zero. It then builds a `ProjectGameInfo` and asks it to validate itself with the same code the project uses. The icon is a file name next to the manifest and not an :term[asset handle]{id=asset-handle}, because the runtime has no project: it reads the one PNG file the export made.

## Identity and the presentation

`ProjectGameInfo` stores the identity in the project. Its check names the first field that fails, such as "Version: ...", so a person can find it. The title may be empty, and then the game shows the project's name.

Titles count code points, not :term[bytes]{id=byte}, as [the page on data formats](../basics/data-formats.md) explains for :term[UTF-8]{id=utf-8}. A title of 128 letters that need three bytes each is allowed, though it takes 384 bytes. The check skips the continuation bytes of each character, counts the rest, and refuses control characters: line breaks and tabs would break a window bar and a version resource.

`GamePresentation` turns the manifest into what the runtime needs, and the runtime calls it before it creates the application.

```cpp src="Strata/src/Strata/Runtime/GamePresentation.cpp#L15-L21" from="presentation.Title =" to="presentation.AppId = FileSystem::ToUTF8(executablePath.stem());" symbol="GamePresentation::Make"
presentation.Title = manifest.GetDisplayTitle();
const std::string version = manifest.Version.empty() ? std::string() : " " + manifest.Version;
presentation.Banner = fmt::format("{}{} (Strata {}, {})", presentation.Title, version, c_EngineVersion, Platform::GetName());
presentation.DataDirectoryName = SaveFiles::MakeGameDirectoryName(manifest.Name);
if (!manifest.Icon.empty())
	presentation.IconFile = manifestPath.parent_path() / FileSystem::FromUTF8(manifest.Icon);
presentation.AppId = FileSystem::ToUTF8(executablePath.stem());
```

The title is the manifest's title, or its name without one. The banner is the log's first line: the title, the version when there is one, the engine's version and the platform's name. The data folder name comes from `Name`, through a function that makes any text safe as a folder name. It replaces slashes, characters Windows refuses and control characters with `_`, turns `..` into `__`, trims spaces and dots at the ends, and cuts to 64 bytes without splitting a character. A name that leaves nothing becomes `Game`.

The application id is the executable's file name without its extension, and the Linux section shows why that matters.

Saves go under `<user data>/<Name>/Saves`, and the log is `<user data>/<Name>/Logs/Game.log`. The :term[user data folder]{id=user-data-folder} is the platform's per-user one: the local application data folder on Windows, `~/.local/share` on Linux (or the folder `XDG_DATA_HOME` names) and `~/Library/Application Support` on macOS. Without one, the runtime uses the temporary folder. The game's code reaches the saves only through the save service, as [the saves page](../make/levels-saves.md) shows.

:::why
Strata keys the data on `Name` because the title is a marketing decision and the name is an engineering one. A title changes with a sale, a language or a new edition. The cost is that renaming the project itself moves the data, so the project's name is the one field to leave alone after release.
:::

## The icon

An icon is a picture that a person draws once and a system shows at many sizes. Windows asks for small and large icons at several display scalings, so the export makes nine sizes from 16 to 64 pixels and one of 256. The source is a texture of the project whose file is a PNG or JPEG image, or one of two older formats, of at most 16 MiB. A texture inside a model has no file of its own and is refused with that reason. A source under 256 pixels on its longer side is enlarged, and the export warns that it may look blurred.

The conversion has two steps. First it makes the image square, by placing it in the middle of a transparent square as wide as its longer side. A 300 by 200 image lands in a 300 by 300 square, at row 50, with 50 transparent rows above and below.

The second step shrinks the square to each size. A shrunk pixel is an average of its neighbours, and two details decide whether the average looks right. The first is the :term[color space]{id=color-space}. Stored colors are :term[sRGB]{id=srgb}, which bends the scale so that dark values get more of the numbers. Averaging black and white as stored gives 128, which shows too dark; the average in linear light is brighter, about 188 once stored again ([linear and sRGB values](../basics/color.md)).

The second detail is alpha. A pixel on the picture's edge sits next to transparent pixels whose color is meaningless, often black. If they count as much as the visible pixel, the edge turns grey. Weighting each color by its alpha lets a transparent pixel say nothing about color.

:::example[One edge pixel, three ways]
Take opaque white beside transparent black, and halve the width. Averaging the stored values gives red 128 and alpha 128, a grey that never existed in the picture. Weighting the color by alpha gives red 255 and alpha 128: still white, half covered. Doing that in linear light keeps the white at 255 too, and the gap shows only for blends of two visible colors. Exercise 3 runs the numbers.
:::

The code asks the shrinking library for exactly this, and says so in its comment.

```cpp src="StrataEditor/src/Editor/GameIcon.cpp#L56-L63" from="if (size == square.Size)" to="STBIR_RGBA) != nullptr;" symbol="Resize"
if (size == square.Size)
{
	outImage.Pixels = square.Pixels;
	return true;
}
outImage.Pixels.resize(static_cast<size_t>(size) * size * 4);
return stbir_resize_uint8_srgb(square.Pixels.data(), static_cast<int>(square.Size), static_cast<int>(square.Size), 0, outImage.Pixels.data(),
	static_cast<int>(size), static_cast<int>(size), 0, STBIR_RGBA) != nullptr;
```

A size equal to the square's is copied as it is. The 256-pixel image is written as a PNG beside the manifest, and the manifest's `Icon` names it. On Windows the ten images also go into the executable.

## The Windows executable

A Windows game is a copy of the runtime that the export rewrites. Explorer reads a file's version and icon from the file itself. They lie in its **PE resources**: the section of a portable executable (PE) image that holds icons, version information and other data, stored in a tree of folders. Strata reads and rewrites that section with its own code, so the writer builds and is tested on every system.

`PEResources::Read` checks every header, every section and the whole resource tree before it reads a byte, and it never asserts. `PEResources::StampGame` replaces the runtime's version resource with one built from the manifest: the title, the four-number version, the company, the copyright and the project's name. It also replaces the icon group named `GLFW_ICON`, which Explorer shows and which the runtime's window library gives to its windows, with one image per size. Every other resource is kept byte for byte, and a second stamp gives the same bytes.

`Write` supports only the layouts the :term[linker]{id=linker} makes for the runtime: the resource section is rebuilt where it stands, and only the base relocations may follow it. Base relocations are the table Windows uses to adjust addresses when it moves the program in memory. It refuses anything else, and a certificate table, which holds a signature.

:::caution
A signed runtime cannot be stamped. A signature covers the file's bytes, and stamping changes them, so the stamp is refused. Export the game first, then sign the executable.
:::

The export stamps in memory before it writes the pack. If the runtime is signed or laid out in a way the writer does not know, the export fails with the reason before it replaces anything. It never leaves a new pack beside an old executable. Open the executable's Properties window and its "Details" tab to see the result: the file description shows the title, and the file and product versions show the four numbers.

## The Linux desktop entry

A Linux desktop lists programs from small text files. A **desktop entry** is such a file, `<File>.desktop`, that names a program, its icon and the class of its windows. The export writes one next to the game when it runs on Linux, but it does not install it: a person copies it to `~/.local/share/applications`.

```cpp src="StrataEditor/src/Editor/DesktopEntry.cpp#L104-L112" from="Type=Application" to="return text;" symbol="DesktopEntry::ToText"
text += "Type=Application\n";
text += "Name=" + EscapeString(Name) + "\n";
text += "Exec=" + EscapeString(QuoteArgument(executable)) + "\n";
if (!Icon.empty())
	text += "Icon=" + EscapeString(icon) + "\n";
text += "StartupWMClass=" + EscapeString(WindowClass) + "\n";
text += "Terminal=false\n";
text += "Categories=Game;\n";
return text;
```

For the project above, in the folder `/home/ana/Export`, the file reads as follows.

```text
[Desktop Entry]
Type=Application
Name=Moon Crab
Exec="/home/ana/Export/MoonCrab"
Icon=/home/ana/Export/MoonCrab.png
StartupWMClass=MoonCrab
Terminal=false
Categories=Game;
```

The paths are absolute because a desktop reads the file from another folder. The price is that moving or shipping the export folder means editing `Exec` and `Icon`. Values are escaped as the specification asks, with backslash codes for spaces at the ends, line breaks, tabs and backslashes. The program in `Exec` is quoted, its special characters are escaped and `%` is doubled, because `%f` and its kin are field codes. The writer refuses an empty value, text that is not UTF-8 and a path that is not absolute; the export then adds a warning and writes no entry.

`StartupWMClass` is how the desktop matches a running window to this entry, so that the list of running programs shows the right icon. The window's class comes from the runtime's application id, and the id is the executable's name without its extension. The export writes the same name into the entry, so the two cannot drift apart.

## The macOS Dock icon

A program on macOS shows one icon in the Dock for all its windows, and a bare executable has no bundle to give it one. When the window gets its icon images, the window code on macOS takes the largest image of at most 1,024 pixels and gives it to the application with one call. The icon lasts while the program runs. On other systems the call does nothing, since their windows carry the icon.

## What the editor shows

In the editor's Project Settings window the **Game** page holds the title, version, company, copyright and icon fields. Each field runs the command `project.setGameInfo`. [The settings windows page](../editor-ui/settings-windows.md) shows the window.

::figure{id=game-page}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Saves keyed by the title | Simple prototypes | One name to keep, nothing hidden | A rename strands the players' saves |
| Saves next to the executable | Portable builds | A whole game that copies as one folder | Failure in read-only folders, and lost data when the folder moves |
| Manifest paths of any form | Launchers that load add-ons | Packs from anywhere | A manifest could point the runtime at any file |
| Windows' own resource functions | Windows :term[build tools]{id=build-tools} | Less code to write | A writer that builds only on Windows, and no test on other systems |
| An installer for each system | Commercial games | Menu entries registered for the player | A tool for each system, and an export that is no longer a plain folder |

## How it is tested

`Editor.Export.GameIcon` tests the icon conversion. `Editor.Export.ExecutableResources` builds fake executables and checks that stamping keeps other resources, gives the same bytes twice and refuses a signed image; its `.Sweep` suite damages bytes on purpose. `Editor.Export.DesktopEntry` parses the written text back.

The manifest tests are the suite `Project.GameManifest`: they round-trip the fields, load versions 1 to 4, refuse settings above 1 MiB and check the version-5 identity. The CTest entry `StrataRuntime.Identity` runs an exported game and searches its log for the title and version. On Windows only, `StrataRuntime.Icon`, `StrataRuntime.GameIcon` and `StrataRuntime.VersionInfo` read the icon and version back through Windows itself. Run a suite with `StrataTests --test-suite=Editor.Export*`, and the exported-game tests with `ctest -R StrataRuntime`.

## Changing it safely

Add a manifest field at the end of its object with a default, so that older manifests still load, and check it in the reader: a string that names a file goes through `IsPlainFileName`. Bump the format version, and add a loading test for the previous version beside the round trip.

A field that players see belongs in `ProjectGameInfo` with its check, in `project.setGameInfo` and on the Game page.

Never key a folder on the title or the company. Run the export suites, `Project.GameManifest` and `ctest -R StrataRuntime` before you commit.

## Summary

- The runtime checks every manifest field: the format and the version, the identity, the plain file names, and the shape and size of the settings, whose values it validates later.
- A version has one to four parts of at most 65,535; missing parts are zero, so `1.2` is stored as 1, 2, 0, 0.
- Saves and logs go under the player's data folder in a folder made from `Name`, so a new title never strands saves.
- The icon is centered on a transparent square and shrunk to ten sizes in linear light with colors weighted by alpha; a 256-pixel PNG goes beside the manifest.
- Windows gets stamped resources, Linux a desktop entry with absolute paths, and macOS a Dock icon while the game runs; signing comes after the export.

## Check yourself

1. A manifest lists `"AssetPack": "packs/Game.stpak"`. What does the runtime do, and why?

   :::answer{tests="manifest-trust"}
   The runtime refuses the manifest. The pack name has a folder part, and the rule demands a plain file name next to the manifest, so that a manifest cannot point the runtime to another folder. A name of `.` or `..` and an absolute path fail for the same reason.
   :::

2. Which of these versions are valid, and what are the four numbers of each valid one? (a) `3` (b) `1.2.3.4.5` (c) `0.70000` (d) `2026.10.22.1`

   :::answer{tests="version-rules"}
   (a) is valid and stores 3, 0, 0, 0. (b) is invalid, since it has five parts. (c) is invalid, since 70,000 is above 65,535. (d) is valid and stores 2026, 10, 22, 1.
   :::

3. A team renames its game from "Moon Crab" to "Moon Crab 2" by changing the title in Project Settings and exports again. Where are the saves now? (a) Under a new folder named after the title. (b) Where they were. (c) Next to the executable.

   :::answer{tests="data-key"}
   (b). The folder comes from the manifest's `Name`, which is the project's name, and the title is only shown. Answer (a) is the mistake the design avoids. Answer (c) is wrong because saves live under the player's data folder, in `<user data>/<Name>/Saves`. Renaming the project, not the title, would move them.
   :::

4. Why does the export weight colors by alpha before it averages them?

   :::answer{tests="icon-pipeline"}
   Transparent pixels carry a color with no meaning, often black. Counted equally, they would darken and tint the edge of the picture. With weights from alpha, a transparent pixel says nothing about color.
   :::

5. Your Windows runtime is signed. When do you sign the game, and what does the export do with a signed runtime?

   :::answer{tests="platform-files"}
   Sign the executable after the export. The export refuses to stamp a signed image, because stamping changes the bytes the signature covers, and it fails before it writes any file.
   :::

## Exercises

1. **Medium.** With the editor and an exported game: change the title in Project Settings, export again into the same folder, run the game, and find its saves and log. Then say what an update that changed `Name` would cost the players.

   :::answer[Worked solution]{tests="data-key"}
   Open the Game page of Project Settings, change the title and export into the same folder. After a run, the folder `<user data>/<Name>/` still holds `Saves` and `Logs/Game.log`, because `Name` did not change. If an update changed `Name`, the game would look in a new folder and find no saves, and the players would seem to lose their progress.
   :::

2. **Medium.** Trace it yourself: find every field of the manifest that `IsPlainFileName` guards, then edit an exported manifest's `AssetPack` to `../Other.stpak` and start the game. What does the runtime say?

   :::answer[Worked solution]{tests="manifest-trust"}
   A search for `IsPlainFileName` in `Strata/src/Strata/Project/GameManifest.cpp` finds the definition and four uses in `GameManifest::FromJson`: the icon, the :term[asset pack]{id=asset-pack}, each patch pack and the script module. The runtime refuses the manifest: it reports "No game to run:" followed by the message that `"AssetPack"` must be the file name of the asset pack next to the manifest, and stops.
   :::

3. **Hard.** Compute one edge pixel of a shrunk icon three ways: opaque white beside transparent black, averaged as stored, weighted by alpha, and weighted by alpha in linear light. Predict each result, then run the sketch.

   :::answer[Worked solution]{tests="icon-pipeline"}
   The stored average of red is (255 + 0) / 2 = 127.5, shown as 128, with alpha 128. The weighted average is (255 x 255 + 0 x 0) / 255 = 255 with alpha 128. In linear light the white is 1.0, the weights keep it 1.0, and it is stored again as 255. The last line shows the gap: blending opaque black and white gives 128 as stored but 188 in linear light.

   ```cpp sketch="worlds-game-identity-edge.cpp"
   // One edge pixel of a shrunken icon: opaque white beside fully transparent black, averaged three ways.
   #include <cmath>
   #include <cstdio>

   struct Pixel
   {
   	double Red = 0.0; // 0 to 255, as stored (sRGB)
   	double Alpha = 0.0; // 0 to 255
   };

   double ToLinear(double stored)
   {
   	const double value = stored / 255.0;
   	return value <= 0.04045 ? value / 12.92 : std::pow((value + 0.055) / 1.055, 2.4);
   }

   double ToStored(double linear)
   {
   	const double value = linear <= 0.0031308 ? linear * 12.92 : 1.055 * std::pow(linear, 1.0 / 2.4) - 0.055;
   	return value * 255.0;
   }

   int main()
   {
   	const Pixel left = { 255.0, 255.0 };
   	const Pixel right = { 0.0, 0.0 };

   	// Naive: average every channel as stored.
   	std::printf("naive: red %.0f alpha %.0f\n", (left.Red + right.Red) / 2.0, (left.Alpha + right.Alpha) / 2.0);

   	// Weighted by alpha: a transparent pixel has no say in the color.
   	const double weight = left.Alpha + right.Alpha;
   	const double weighted = (left.Red * left.Alpha + right.Red * right.Alpha) / weight;
   	std::printf("weighted: red %.0f alpha %.0f\n", weighted, weight / 2.0);

   	// Weighted and in linear light, the way the export does it.
   	const double linear = (ToLinear(left.Red) * left.Alpha + ToLinear(right.Red) * right.Alpha) / weight;
   	std::printf("linear and weighted: red %.0f alpha %.0f\n", ToStored(linear), weight / 2.0);

   	// Two opaque pixels, black and white: the middle gray differs by the space.
   	std::printf("black and white, stored average %.0f, linear average %.0f\n", 127.5, ToStored((ToLinear(255.0) + ToLinear(0.0)) / 2.0));
   	return 0;
   }
   ```

   ```text output-of="worlds-game-identity-edge.cpp"
   naive: red 128 alpha 128
   weighted: red 255 alpha 128
   linear and weighted: red 255 alpha 128
   black and white, stored average 128, linear average 188
   ```

   1. **Line 33:** the weights are the alphas, so a transparent pixel adds nothing to the color.
   2. **Line 37:** the same average runs on linear values, and `ToStored` converts the result back.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Project/GameManifest.h` and `GameManifest.cpp`: the manifest and its reader; `Strata/src/Strata/Project/GameInfo.h`: `ProjectGameInfo` and its checks.
- `Strata/src/Strata/Runtime/GamePresentation.h`: the title, banner, data folder and application id; `Strata/src/Strata/Core/SaveFiles.h`: the folder name and the save folder.
- `StrataEditor/src/Editor/GameIcon.h`, `PEResources.h` and `DesktopEntry.h`: the icon, the Windows resources and the Linux entry; `GameExport.cpp` calls them.
- `Strata/src/Platform/GLFW/GLFWApplicationIcon.h`: the Dock icon.
- Tests: `Project.GameManifest`, `Editor.Export.GameIcon`, `Editor.Export.ExecutableResources`, `Editor.Export.DesktopEntry`, and the CTest entries `StrataRuntime.Identity`, `StrataRuntime.Icon`, `StrataRuntime.GameIcon` and `StrataRuntime.VersionInfo`.
- Command: `project.setGameInfo`.

## Further reading

- The Desktop Entry Specification of freedesktop.org: the escaping and the keys, intermediate.
- Microsoft's documentation of the portable executable format and of resource sections: the layout the writer follows, advanced.

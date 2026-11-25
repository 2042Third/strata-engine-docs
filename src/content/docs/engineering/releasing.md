---
id: engineering/releasing
title: "Packaging and releasing"
description: "How a Strata build becomes the archive a person downloads, how a release is cut as a dry run and for real, and how the archive is checked."
kind: internals
size: L
tracks: [E]
needs: [engineering/ci]
time: 75
learn:
  - id: add-release-file
    text: add a file to the release archive with an install rule and an entry in the install test's layout
  - id: version-rules
    text: explain which package versions the build accepts and which tags publish a release
  - id: dry-run
    text: run a dry run of a release and read what the version job checks
  - id: check-archive
    text: compare an archive's files, version and checksum with what a person gets after the download
  - id: trace-marker
    text: trace the installation marker from the rule that writes it to the editor code that reads it
since: 0.3.0
status: final
---

A build folder is where the engine is made, not what a person downloads. This page follows the way from one to the other. It covers the install rules that gather the files, the archive that holds them and the version in its name. It ends with the release run that builds, tests, unpacks and publishes the archives. Exporting a game is on [the export page](../worlds/export.md), and the continuous integration (CI) that runs on every change is on [the CI page](ci.md).

## The problem and how engines solve it

Think of a friend who wants to try your engine. In your build folder lie thousands of files: :term[object files]{id=object-file}, caches, test programs, and the three programs you built. Your friend needs only the programs, the sample games and the files they read while they run. Packaging is the work of choosing those files and putting them in one place that works on a machine that never saw your source.

The place is an **install tree**: a folder laid out the way the finished program expects. You make it by copying chosen files from the build and the source into a prefix, the folder you name for the copy. :term[CMake]{id=cmake} does the copying when you run `cmake --install` and give it `--prefix`. You write one `install()` rule per kind of file, and the rules decide the layout. A good install tree works in any folder, because no file inside it names a path outside it.

The next problem is one file to carry. Archives solve it: one ZIP or `.tar.gz` file holds the whole tree under a folder named for the release. Some engines go further and write installers, which run on the person's machine, ask questions, change the system settings and add an entry to the list of programs. An installer gives a nicer first minute and costs a lot: a program that changes the machine needs rules for removal, upgrades and rights. Strata ships plain archives and no installers: you unpack the folder and run the editor from it.

The third problem is the name of the release. A person who sees `Strata-0.7.0-windows-x64.zip` knows what they hold. A team also needs names for versions that are not ready.

A **pre-release suffix** is the part after a dash, as in `0.7.0-rc1`, that marks a version as not yet the release.

A **release candidate** is a build of the version that the team believes is ready, so its name ends in `-rc1`, then `-rc2` if the first one has a fault. People test the candidate, and only when it passes does the team publish the plain version.

The last idea is the safest one: a **dry run** is a complete run of the release steps that stops before the publish. It builds, tests, packs and unpacks every archive, so every mistake appears while nothing is public. The mistakes it catches are the ones that cannot appear in a normal build: a file the install rules forgot, a program that reports the wrong version, a wrong letter in a name.

Three mistakes recur in projects of this kind, and Strata's design answers each.

- Testing the build tree and shipping the install tree. The tests pass on files that the archive lacks. Strata answers by running the final checks on the unpacked archive, in a fresh folder, as a person gets it.
- Letting every job publish. A job that builds code from many sources should not hold the right to write to your releases. Strata gives that right to one job, the last.
- Trusting a name. A tag typed by hand can disagree with the version inside the program. Strata compares the tag with the project's version before it builds anything.

## The map

A release has two parts that this page keeps apart. The first is the file `.github/workflows/release.yml`, which GitHub runs when you push a tag. The second is the packaging in `CMake/StrataPackaging.cmake`, which that file calls through `cmake --install` and `cpack`. You can run the packaging on your own machine without the release file, which is how you learn what a release holds.

The release file has three kinds of job. The version job runs first, on one Linux machine, and decides the version, the tag and whether this run publishes. Three build jobs follow, one per :term[operating system]{id=operating-system}, all started at once from the version job's result. The publish job waits for all three and runs only when the version job said so.

```mermaid caption="The version job decides what the run is. Three build jobs each build, test, pack, check and checksum an archive. The publish job runs only for a plain version tag." alt="Boxes in three columns. The version job leads to three build jobs for Windows, Linux and macOS. Each build job leads to the publish job, which carries a note that it runs only when the tag is a plain version."
flowchart LR
    V["Version: read the tag, compare it with the project, check the notes"]
    V --> W["Build Windows: Dist build, Dist tests, pack, unpack, run, checksum"]
    V --> L["Build Linux: the same steps"]
    V --> M["Build macOS: the same steps"]
    W --> P["Publish: only for a plain vX.Y.Z tag"]
    L --> P
    M --> P
```

The three build jobs run on windows-2022, ubuntu-24.04 and macos-15, and they name their archives `windows-x64`, `linux-x64` and `macos-arm64`. The release run shares no job with the everyday CI of [the CI page](ci.md), but it uses the same runners and the same test labels.

The result of the packaging is one folder. Its layout is written as a comment at the top of `CMake/StrataPackaging.cmake`, and the install test checks it.

:::files[The folder of a Strata release archive]

- `Strata-0.7.0-windows-x64/` the one folder at the top of the archive
  - `StrataEditor.exe`, `StrataRuntime.exe`, `StrataCLI.exe` the three programs side by side
  - `StrataInstall.json` the marker
  - `README.md`, `ThirdPartyNotices.md`
  - `Samples/` the file `Samples.json` and the sample projects
  - `StrataScriptCore/` the folders `CMake`, `Include`, `Source` and `ThirdParty/glm`
  - `Docs/Manual/` guides for people who make games
  - `Skills/` the guides for agents that make games with the editor

:::

The three programs sit at the top, side by side, for a reason you will see again. An exported game copies the :term[runtime]{id=runtime} from beside the editor, and the launcher finds the samples there. The **installation marker** is the file `StrataInstall.json` at that top. It tells the editor that it runs from an installation and not from a build, so the editor builds game scripts with the installation's own script kit.

## The contract

Four rules hold for everything that goes into a release. Each has a reason, and the first three are checked by a test or by the release run.

First, install rules exist only when the editor, the runtime and the command-line client are all built. `StrataPackaging.cmake` returns at its top, with a status message, if one of the three targets is missing. A build of the engine alone has nothing to package, and half an installation would fail on the first export.

Second, a file that releases must ship gets two changes together: an install rule in the packaging file, and an entry in the layout that the install test checks. Without the rule the file is missing from the archive. Without the entry the test cannot notice when the rule is removed later.

:::rule
Every file of a release needs two changes: an install rule in `CMake/StrataPackaging.cmake` and an entry in the layout that `StrataEditor.Install` checks. The test compares the top level of the installation with a list, so a file installed by accident, such as a dependency's, fails it too. See [the install test](test-kinds.md).
:::

Third, release tests run the :term[Dist]{id=dist} configuration, the build that ships, with asserts compiled out. Everyday CI tests Release, and Debug on Windows, and its Dist job runs only the package tests, so a test whose expectation differs in Dist must say so with `#if defined(ST_DIST)`. One example is the test of host call counters: Dist builds do not count calls, so the test expects an empty list there.

Fourth, use CMake's own `cpack`. On the Windows runners the name `cpack` alone starts a program of another package manager, `choco`, which comes earlier in the path. The release file therefore builds the :term[full path]{id=absolute-path} from the folder of `cmake`.

:::why
The Dist rule comes from what the release is. A release ships the Dist build, so only a Dist run proves that the shipped files work. Testing Release and trusting Dist is a bet that the two differ in no test, and a test that differs in Dist is exactly what a bug in compiled-out code looks like.
:::

Two more facts concern what the archive does not do. Strata's archives are not signed, and the system's approval service never sees them: a search of the release file, the CMake files and the top `CMakeLists.txt` for signing tools finds nothing. There are no installers either: CPack writes a ZIP on Windows and a `.tar.gz` file elsewhere.

## A toy version

The toy shows the two CMake parts of the job for a program of two files, a program and its settings. You write `install()` rules for the files, name the archive and include CPack, and you pack with one command.

```cmake
cmake_minimum_required(VERSION 3.25)
project(Toy VERSION 1.2.0)

add_executable(Toy main.cpp)

# The program at the top of the installation, the settings in a folder beside it.
install(TARGETS Toy RUNTIME DESTINATION .)
install(FILES settings.json DESTINATION Config)

set(CPACK_PACKAGE_NAME "Toy")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_FILE_NAME "Toy-${PROJECT_VERSION}-linux-x64")
set(CPACK_GENERATOR "TGZ")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY ON)
include(CPack)
```

1. **Lines 7–8:** the rules that say where each file goes: the program at the top, the settings in a folder beside it.
2. **Lines 10–13:** the settings that tell CPack the name and the kind of the archive.
3. **Line 14:** the switch that puts everything inside one folder named like the archive.
4. **Line 15:** the line that loads CPack, which writes the file the `cpack` command reads.

Read the toy as three groups: the `install()` lines, the `set()` lines and the line that loads CPack. **CPack** is the CMake tool that packs an install tree into an archive.

You build, then run `cmake --install build --prefix out` to get the install tree and `cpack --config build/CPackConfig.cmake` to get `Toy-1.2.0-linux-x64.tar.gz`. With `CPACK_INCLUDE_TOPLEVEL_DIRECTORY` on, everything sits inside a folder with the archive's name, so unpacking never scatters files into the :term[current folder]{id=current-folder}.

The second toy is the version rule. The package version must be the project's version, with an optional suffix, and nothing else. The sketch below applies it to eight requests for the project version 0.7.0.

:::question
Does the sketch use C++ you have not met? Read [functions and loops](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first.
:::

The function `ResolvePackageVersion` returns a flag, and writes the version to use through its last parameter. Watch what happens to the empty request, to a suffix that has no text, and to a version with a fourth number.

```cpp sketch="engineering-releasing-version.cpp"
// A toy of the package version rule: the project's version, with an optional pre-release suffix.
#include <cstdio>
#include <string>

bool IsSuffixCharacter(char c)
{
	return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '.';
}

// An empty request means the project's version. Otherwise the request is that version, then nothing or "-" and text.
bool ResolvePackageVersion(const std::string& projectVersion, const std::string& requested, std::string& outVersion)
{
	if (requested.empty())
	{
		outVersion = projectVersion;
		return true;
	}
	if (requested.compare(0, projectVersion.size(), projectVersion) != 0)
		return false;
	const std::string rest = requested.substr(projectVersion.size());
	if (!rest.empty())
	{
		if (rest.size() < 2 || rest[0] != '-')
			return false;
		for (size_t index = 1; index < rest.size(); index++)
			if (!IsSuffixCharacter(rest[index]))
				return false;
	}
	outVersion = requested;
	return true;
}

int main()
{
	const std::string project = "0.7.0";
	const char* requests[] = { "", "0.7.0", "0.7.0-rc1", "0.7.0-beta.2", "0.6.0", "0.7.0-", "0.7.01", "0.7.0.1" };
	for (const char* request : requests)
	{
		std::string version;
		if (ResolvePackageVersion(project, request, version))
			std::printf("'%s' -> Strata-%s-linux-x64.tar.gz\n", request, version.c_str());
		else
			std::printf("'%s' -> refused\n", request);
	}
	return 0;
}
```

```text output-of="engineering-releasing-version.cpp"
'' -> Strata-0.7.0-linux-x64.tar.gz
'0.7.0' -> Strata-0.7.0-linux-x64.tar.gz
'0.7.0-rc1' -> Strata-0.7.0-rc1-linux-x64.tar.gz
'0.7.0-beta.2' -> Strata-0.7.0-beta.2-linux-x64.tar.gz
'0.6.0' -> refused
'0.7.0-' -> refused
'0.7.01' -> refused
'0.7.0.1' -> refused
```

1. **Lines 13–17:** an empty request means the project's version, so the answer needs no suffix.
2. **Lines 18–19:** any other request must start with the project's version.
3. **Lines 21–27:** the rest must be a dash and at least one letter, digit or dot.

The empty request follows the project, a suffix with text passes, and everything else is refused. A suffix of only a dash fails because the rule wants at least one character after it. The request `0.7.01` fails because the rest after the project's version must start with a dash. The real rule is the same, written as a pattern.

## The real code

The packaging file is the real version of the first toy. It starts, after the early return you met in the contract, by resolving the version and the platform name, and then it installs files. Read the part below for the order of the rules and for the comments that explain why a rule is there.

```cmake src="CMake/StrataPackaging.cmake#L54-L107"
# The executables, at the installation's top: GameExport and the launcher look beside the editor.
install(TARGETS StrataEditor StrataRuntime StrataCLI RUNTIME DESTINATION .)

# The marker: the editor's script builds use the installation's SDK (FindEngineInstallation).
file(CONFIGURE OUTPUT "${PROJECT_BINARY_DIR}/Package/StrataInstall.json" CONTENT "{
	\"Strata\": { \"Format\": \"Installation\", \"Version\": 1 },
	\"EngineVersion\": \"@PROJECT_VERSION@\"
}
" @ONLY)
install(FILES "${PROJECT_BINARY_DIR}/Package/StrataInstall.json" DESTINATION .)
install(FILES "${PROJECT_SOURCE_DIR}/ThirdPartyNotices.md" DESTINATION .)
install(FILES "${PROJECT_SOURCE_DIR}/Docs/Releases/PackageReadme.md" DESTINATION . RENAME README.md)

# The samples, without local editor data (.strata), as the StrataSamples target copies them next to the editor.
install(DIRECTORY "${PROJECT_SOURCE_DIR}/Samples/" DESTINATION Samples PATTERN ".strata" EXCLUDE)

# The script SDK: what StrataScriptCoreConfig.cmake and the scripts it builds read. glm, the only library scripts see, comes
# along with its license (its headers only).
install(DIRECTORY
	"${PROJECT_SOURCE_DIR}/StrataScriptCore/CMake"
	"${PROJECT_SOURCE_DIR}/StrataScriptCore/Include"
	"${PROJECT_SOURCE_DIR}/StrataScriptCore/Source"
	DESTINATION StrataScriptCore)
install(DIRECTORY "${PROJECT_SOURCE_DIR}/Strata/vendor/glm/glm" DESTINATION StrataScriptCore/ThirdParty/glm
	FILES_MATCHING PATTERN "*.hpp" PATTERN "*.inl" PATTERN "*.h")
install(FILES "${PROJECT_SOURCE_DIR}/Strata/vendor/glm/copying.txt" DESTINATION StrataScriptCore/ThirdParty/glm)

# The manual for people making games (new scripts point to Docs/Manual/Scripting.md "in the Strata engine's folder") and the
# skills an AI agent uses to make games with the editor.
install(DIRECTORY "${PROJECT_SOURCE_DIR}/Docs/Manual/" DESTINATION Docs/Manual)
foreach(skill IN ITEMS strata-editor-automation strata-make-a-game strata-scripting)
	install(FILES "${PROJECT_SOURCE_DIR}/.claude/skills/${skill}/SKILL.md" DESTINATION "Skills/${skill}")
endforeach()

set(CPACK_PACKAGE_NAME "Strata")
set(CPACK_PACKAGE_VENDOR "Strata")
set(CPACK_PACKAGE_VERSION "${_strataPackageVersion}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PROJECT_DESCRIPTION}")
set(CPACK_PACKAGE_HOMEPAGE_URL "${PROJECT_HOMEPAGE_URL}")
set(CPACK_PACKAGE_FILE_NAME "Strata-${_strataPackageVersion}-${STRATA_PACKAGE_PLATFORM}")
set(CPACK_PACKAGE_DIRECTORY "${PROJECT_BINARY_DIR}/Packages")
if(WIN32)
	set(CPACK_GENERATOR "ZIP")
else()
	set(CPACK_GENERATOR "TGZ")
endif()
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY ON)
# Linux executables keep their full symbol tables, a large share of their size (and of every exported game's runtime);
# packages ship them stripped, as Windows packages ship without PDBs. Crash reports name script modules' functions from
# the modules' own files, which stay as they are built. macOS packages keep theirs: strip would have to re-sign them.
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
	set(CPACK_STRIP_FILES ON)
endif()
include(CPack)
```

1. **Line 55:** the programs go at the top, because the export and the launcher look beside the editor.
2. **Lines 58–63:** the marker is written into the build folder with the engine's version, then installed at the top.
3. **Line 68:** the samples go in, except the folders named `.strata`.
4. **Lines 72–79:** the script kit: three folders, glm's :term[headers]{id=header} and its license.
5. **Lines 93–107:** the archive's name, its kind, the stripping of Linux programs, and the line that loads CPack.

The rules go in the order of the folder. The programs come first because of the export and the launcher. The marker file is not in the source tree: `file(CONFIGURE ...)` writes it into the build folder with the engine's version in it, and `install(FILES ...)` copies it to the top. The sample rule excludes the folders named `.strata`, which hold local editor data. The script kit is three folders of `StrataScriptCore` plus glm's :term[headers]{id=header} and its license, because glm is the only library a script sees; the manual and the three skill files follow.

Compare with the toy. The real file names the archive from a version and a platform, writes a ZIP on Windows and a `.tar.gz` file elsewhere, and strips the Linux programs. Stripping removes their symbol tables, which are a large share of their size, and a game that is exported later copies the runtime, so the saving carries over. macOS archives keep their symbols, because stripping would force a new signature. Windows archives hold no debug files at all.

The version that goes into the name comes from `strata_resolve_package_version`, a function of its own file so that a test can load it without the rest.

```cmake src="CMake/StrataPackageVersion.cmake#L7-L24"
function(strata_resolve_package_version outVersion outError projectVersion requested)
	if(requested STREQUAL "")
		set(${outVersion} "${projectVersion}" PARENT_SCOPE)
		set(${outError} "" PARENT_SCOPE)
		return()
	endif()
	string(REPLACE "." "\\." versionPattern "${projectVersion}")
	if(requested MATCHES "^${versionPattern}(-[0-9A-Za-z.]+)?$")
		set(${outVersion} "${requested}" PARENT_SCOPE)
		set(${outError} "" PARENT_SCOPE)
	else()
		string(CONCAT error "STRATA_PACKAGE_VERSION '${requested}' is not the project's version ${projectVersion} (with an "
			"optional pre-release suffix such as -rc1): leave it empty for the project's version (`cmake -U "
			"STRATA_PACKAGE_VERSION` clears a value a build directory cached), or bump project(Strata VERSION) in CMakeLists.txt")
		set(${outVersion} "" PARENT_SCOPE)
		set(${outError} "${error}" PARENT_SCOPE)
	endif()
endfunction()
```

1. **Line 7:** the function takes the project's version and the request, and fills two outputs.
2. **Lines 8–12:** an empty request returns the project's version with no error.
3. **Lines 13–14:** the dots are escaped, then the request must be that text and an optional dash and characters.
4. **Lines 18–20:** a refusal tells the person what to do instead.

The function takes the project's version and the request, and it writes two outputs. An empty request returns the project's version. Otherwise the dots of the project's version are escaped, so that `0.7.0` cannot match `0x7y0`, and the request must match that text followed by an optional dash and characters from letters, digits and dots. A refusal carries a message that tells the person what to do. The first branch has a second job: the default is empty, so an old build folder keeps working after a version bump, where a cached copy would name the old version.

:::example[One tag, from the push to the name]
The project's version is 0.7.0 and you push the tag `v0.7.0-rc1`. The version job removes the `v`, which leaves `0.7.0-rc1`, and takes the base `0.7.0` before the dash. The base equals the project's version, so the check passes; the version is not equal to the base, so the run is a dry run and `publish` is false. Each build job passes `-DSTRATA_PACKAGE_VERSION=0.7.0-rc1` to CMake, and the archive of the Windows job is `Strata-0.7.0-rc1-windows-x64.zip`. Push `v0.8.0` instead and the run stops at the first check: the tag's base 0.8.0 is not 0.7.0.
:::

The release file starts with the version gate. The excerpt is the body of its `run:` step, a shell script that reads the project's version, takes the tag, and decides.

```sh src=".github/workflows/release.yml#L51-L93"
          set -euo pipefail
          project=$(sed -n '/^project(Strata/,/)/s/^[[:space:]]*VERSION[[:space:]]\+\([0-9][0-9.]*\)[[:space:]]*$/\1/p' CMakeLists.txt)
          if [ -z "$project" ]; then
            echo "::error file=CMakeLists.txt::Cannot read project(Strata VERSION ...)"
            exit 1
          fi
          if [ "$GITHUB_EVENT_NAME" = "push" ]; then
            tag="$GITHUB_REF_NAME"
          else
            tag="$INPUT_TAG"
          fi
          if [ -n "$tag" ]; then
            if ! [[ "$tag" =~ ^v([0-9]+\.[0-9]+\.[0-9]+)(-[0-9A-Za-z.]+)?$ ]]; then
              echo "::error::Tag '$tag' is not vX.Y.Z or vX.Y.Z-<suffix>"
              exit 1
            fi
            version="${tag#v}"
            base="${BASH_REMATCH[1]}"
            if [ "$base" != "$project" ]; then
              echo "::error file=CMakeLists.txt::Tag $tag is version $base, but project(Strata VERSION) is $project: bump the project's version or tag the right commit"
              exit 1
            fi
            ref="refs/tags/$tag"
            if [ "$version" = "$base" ]; then publish=true; else publish=false; fi
          else
            # A dry run of the branch: the project's version marked as such, never published.
            version="$project-dryrun.$GITHUB_RUN_NUMBER"
            base="$project"
            ref="$GITHUB_SHA"
            publish=false
          fi
          if [ ! -f "Docs/Releases/$base.md" ]; then
            echo "::error::Docs/Releases/$base.md is missing: write the release notes of $base before tagging"
            exit 1
          fi
          echo "Building Strata $version from $ref (publish: $publish)"
          {
            echo "ref=$ref"
            echo "tag=$tag"
            echo "version=$version"
            echo "base=$base"
            echo "publish=$publish"
          } >> "$GITHUB_OUTPUT"
```

1. **Lines 63–66:** the tag must be `v`, three numbers and an optional suffix, or the run stops with an :term[annotation]{id=annotation}.
2. **Lines 69–72:** the base of the tag must equal the project's version.
3. **Line 74:** a version equal to its base publishes; a version with a suffix does not.
4. **Lines 76–80:** with no tag the run is a dry run of the branch, never published.
5. **Lines 82–85:** the notes of the base version must exist, for every kind of run.

The step reads its inputs from outside, so you can run it for a tag, run it by hand with a tag, or run it by hand with none. Without a tag it makes a dry run of the branch whose version is the project's with `-dryrun.` and the run number, and it never publishes. The notes check at the end holds for every kind of run: a release needs its notes, and a dry run proves they exist. Errors use the `::error` form that GitHub shows as an annotation, as you saw on [the CI page](ci.md).

The build jobs run in one order: configure with the package version, build Dist, test Dist with every label except `gpu` and `perf`, and package. The test step includes `StrataEditor.Install`, which installs this build into a fresh prefix and makes, builds, plays and exports a game with the installed editor alone. The package step is where the archive is checked as a person gets it.

```sh src=".github/workflows/release.yml#L178-L226"
          set -euo pipefail
          exec > >(tee package.log) 2>&1
          build="build/${{ matrix.preset }}"
          # CMake's own cpack: on the Windows runners `cpack` alone is Chocolatey's (choco pack), earlier in PATH.
          "$(dirname "$(command -v cmake)")/cpack" --config "$build/CPackConfig.cmake" -C Dist
          archive="$build/Packages/$PACKAGE.${{ matrix.archive }}"
          if [ ! -f "$archive" ]; then
            echo "::error::cpack did not write $archive"
            ls -l "$build/Packages" || true
            exit 1
          fi
          # The archive as a person gets it: unpacked into a fresh folder, its executables run and report the version.
          check="$RUNNER_TEMP/PackageCheck"
          rm -rf "$check" && mkdir -p "$check"
          if [ "${{ matrix.archive }}" = "zip" ]; then
            7z x -o"$check" "$archive" > /dev/null
            suffix=".exe"
          else
            tar -xzf "$archive" -C "$check"
            suffix=""
          fi
          root="$check/$PACKAGE"
          ls -l "$root"
          # What the archive weighs and its largest files, as an annotation (job logs need admin rights to read).
          # Listed from inside the package: on Windows $root holds backslashes, which a sed pattern would read as escapes.
          largest=$(cd "$root" && find . -type f -exec wc -c {} + | grep -v ' total$' | sort -rn | sed -n '1,8s|\./||p')
          echo "::notice title=Package $PACKAGE::$(wc -c < "$archive" | tr -d ' ') bytes packed; its largest files:%0A${largest//$'\n'/%0A}"
          for file in StrataEditor$suffix StrataRuntime$suffix StrataCLI$suffix StrataInstall.json README.md ThirdPartyNotices.md \
              Samples/Samples.json StrataScriptCore/CMake/StrataScriptCoreConfig.cmake Skills/strata-make-a-game/SKILL.md; do
            if [ ! -f "$root/$file" ]; then
              echo "::error::The archive lacks $file"
              exit 1
            fi
          done
          # The binaries carry the project's version (an rc archive holds the version it is a candidate for).
          "$root/StrataEditor$suffix" --version | tee version.txt
          grep -q "^Strata Editor ${{ needs.version.outputs.base }}" version.txt \
            || { echo "::error::The packaged editor does not report Strata ${{ needs.version.outputs.base }}"; exit 1; }
          "$root/StrataCLI$suffix" --version
          # Checksums of what is published.
          mkdir -p dist
          cp "$archive" dist/
          cd dist
          if command -v sha256sum > /dev/null; then
            sha256sum "$PACKAGE.${{ matrix.archive }}" > "$PACKAGE.${{ matrix.archive }}.sha256"
          else
            shasum -a 256 "$PACKAGE.${{ matrix.archive }}" > "$PACKAGE.${{ matrix.archive }}.sha256"
          fi
          cat "$PACKAGE.${{ matrix.archive }}.sha256"
```

1. **Line 182:** CMake's own `cpack`, found through the folder of `cmake`.
2. **Lines 192–198:** a ZIP is extracted with `7z`, a `.tar.gz` with `tar`, into a fresh folder.
3. **Lines 205–211:** the files that must exist in the extracted archive.
4. **Lines 213–215:** the editor must report the base version.
5. **Lines 217–226:** one checksum file per archive, made with whichever tool the runner has.

The step trusts nothing it has not read from the archive. It extracts the archive into a fresh folder and lists it. It writes an annotation with the size and the eight largest files, and it fails if any of nine paths is missing. It then runs the editor's `--version`, checks that the output starts with the base version, and runs the command-line client's `--version`.

The last part writes a **checksum file**: a text file that holds the :term[SHA-256]{id=sha-256} value of an archive next to its name. Anyone who downloads the archive can compute the value again and compare.

The check uses the base version and not the full one, because the programs of an `rc1` archive report the version they are a candidate for. Only the file name of a candidate differs from the release.

The publish job is the only one with the right to write.

```sh src=".github/workflows/release.yml#L272-L281"
          set -euo pipefail
          cd dist
          cat ./*.sha256 > SHA256SUMS.txt
          sha256sum --check SHA256SUMS.txt
          ls -l
          cd ..
          # The release's title is the notes' heading: the page shows the rest.
          sed '1{/^# /d;}' "Docs/Releases/$VERSION.md" | sed '1{/^$/d;}' > "$RUNNER_TEMP/notes.md"
          gh release create "$TAG" dist/* --repo "$GITHUB_REPOSITORY" --verify-tag --title "Strata $VERSION" \
            --notes-file "$RUNNER_TEMP/notes.md"
```

1. **Lines 274–275:** the checksum files join into one, and the join is checked.
2. **Line 279:** the notes lose their first heading, which becomes the release's title.
3. **Lines 280–281:** the release is created, and the tag must already exist.

At the top of the release file, `permissions` gives every job read access to the contents and no more. The publish job alone asks for `contents: write`, because its last command, `gh release create`, makes the release on GitHub. The job joins the checksum files into `SHA256SUMS.txt` and checks them with `sha256sum --check`, so a damaged file fails here. The flag `--verify-tag` makes the command fail when the tag does not exist on the remote. The title and the notes come from the notes file of the version, such as `Docs/Releases/0.7.0.md`, whose first heading the script removes because the release already has a title.

The package step is the answer to the mistake of testing the build tree: it asks the archive and never the folder the archive was built from.

## Cutting a release

A release comes at the end of every wave, the engine's name for one planned stage of its work, and fixes get patch versions. The steps do not change.

1. Raise the version in `project(Strata VERSION)` in the top `CMakeLists.txt`. The About dialog, the launcher, `--version` and the runtime's log all report it.
2. Write the notes for the people who download it, such as `Docs/Releases/0.7.0.md`, and bring `Docs/Releases/PackageReadme.md` up to date. It becomes `README.md` in the archive.
3. Run `ctest --preset <platform>-dist -LE "gpu|perf"` on your machine, so the Dist build has run the tests before the release run does.
4. Push the tag `v<version>-rc1`. The release run is a dry run and uploads the archives as artifacts of the run. Download one, unpack it and try it.
5. Push the tag `v<version>`. The same run happens, and the publish job writes the release.

The samples in the archive add to its size. The check `Samples.Content` bounds how much they grow it; [the contributing page](contributing.md) teaches the check and its budgets.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| An installer program | Many programs for desktop systems | A first-run experience, menu entries, upgrades in place | Rules for removal and upgrade on three systems, and a program that changes the machine |
| Signed archives approved by the system | Programs that the system asks to trust | No warning from the system when the editor starts | Keys to guard, a paid account and a step that can fail after the tests pass |
| A package manager only | Libraries and command-line tools | Installs and upgrades by one command | A separate package to keep for each manager, and the samples and script kit would need rules too |
| Testing the build tree | Quick local checks | Faster feedback, no packing step | Files that the archive lacks go unseen, which is the mistake this page warns of |
| Publishing from each build job | Small projects with one platform | No artifact hand-off | Three jobs with write rights, and a release made of whichever job finished |

The weakest row for a reader of Strata is signing. A person who downloads the archive on a system that checks signatures may see a warning. The checksum file lets the person confirm that the file is the one the release run made, but it does not say who made it.

## How it is tested

Two tests belong to the packaging. `StrataPackaging.Version` runs the version function in :term[script mode]{id=script-mode}, with `cmake -P` on `StrataTests/Packaging/PackageVersionTests.cmake`, without any build. It checks that an empty request follows the project's version, that the version with `-rc1` or `-beta.2` passes, and that another version, a dash with no text, `0x4y0` and a fourth number are refused.

`StrataEditor.Install` installs the build into a fresh prefix and compares the top level with the expected list. It checks the files inside and finds no `.strata` folder in the samples. It reads the marker and runs `--version`. Last, it builds and exports a game with the installed editor. [The test kinds page](test-kinds.md) teaches its steps; the package step of the release file adds what a test of the install tree cannot do, because it checks the archive that CPack made.

Run them with :term[ctest]{id=ctest}:

```sh
ctest --preset windows-debug -R StrataPackaging.Version
ctest --preset windows-debug -L package
```

The second line runs every test with the label `package`; it needs CMake and a :term[compiler]{id=compiler} on the machine, because the installed editor builds scripts.

## Changing it safely

To add a file to the release, do three things in order. First, write the `install()` rule in `CMake/StrataPackaging.cmake`, in the group of its kind, with a comment that says why it ships. Second, add the file to the list in `StrataTests/Editor/InstallEndToEnd.cmake`, or a new top-level name to the list of expected entries. Third, run `StrataEditor.Install` and make a local package to see the file in the tree. The list of nine files in the package step of the release file is shorter on purpose: it holds one witness of each group, not every file.

To change how the version is read, change the function and `PackageVersionTests.cmake` together. A refusal that used to pass, or the other way round, belongs in the test as a new line first.

These rules of the engine's guide apply, each for a reason:

- Release tests run Dist, because the archive holds Dist programs.
- Every shipped file gets a rule and a list entry, because the install test is the only reader of the layout.
- Release notes exist before the tag, because the release run refuses a tag without them.
- :term[Executables]{id=executable} and the runtime are installed at the top, because an export copies the runtime from beside the editor.

Before you push a tag, run the Dist tests locally and push the `-rc1` tag. If the dry run fails in the package step, read the annotation of the failed job: the run prints the size, the largest files and the first missing file. The mistakes that most need a person, a wrong tag or a forgotten notes file, stop the run before the long builds.

## Summary

- A release is an install tree of the Dist build, packed by CPack into a ZIP on Windows and a `.tar.gz` file elsewhere, with one folder at the top.
- Every file that ships gets an install rule and an entry in the list that `StrataEditor.Install` checks; release tests run Dist and use `#if defined(ST_DIST)` where it differs.
- The package version is the project's version with an optional suffix; a tag publishes only as `vX.Y.Z`, and a tag with a suffix is a dry run.
- The package step unpacks the archive into a fresh folder, checks nine files, runs `--version` and writes a :term[checksum]{id=checksum}; only the publish job may write.
- `StrataInstall.json` sits beside the programs; the editor that finds it builds scripts with the installation's kit and searches for a :term[toolchain]{id=build-tools} on the machine.

## Check yourself

1. The project's version is 0.7.0. Which of the tags `v0.7.0`, `v0.7.0-rc2`, `v0.7`, `v0.8.0` publishes a release?

   :::answer{tests="version-rules"}
   Only `v0.7.0`. The tag `v0.7.0-rc2` is a dry run, because its version differs from its base. The tag `v0.7` is refused because it lacks the third number. The tag `v0.8.0` is refused because its base is not the project's version.
   :::

2. A developer adds a new file of credits at the top of the source folder and installs it with a new `install()` rule. The install test now fails, saying that the top level holds an entry it does not expect. Which change makes it pass?

   - A. Delete the rule.
   - B. Add the file's name to `expected_entries` in the install test.
   - C. Skip the test with its label.

   :::answer{tests="add-release-file"}
   B. The test compares the top level with a list on purpose, so a file that ships needs a decision written down. A is wrong: it drops the file the release wanted. C is wrong: it weakens a test to make it pass, which the engine's rules forbid.
   :::

3. What does a dry run prove that a successful CI run does not?

   :::answer{tests="dry-run,check-archive"}
   A dry run proves four things. The Dist build passes the tests, the archive packs and unpacks in a fresh folder, its programs run and report the right version, and the notes exist.
   The everyday CI never runs `cpack`.
   :::

4. Why does the package step compare the editor's output with the base version and not with the full version of an `rc1` archive?

   :::answer{tests="version-rules,check-archive"}
   The programs are built from the project's version, which is the base. Only the archive's name carries the suffix, so a candidate reports the version it prepares.
   :::

5. A script build on a machine with an unpacked archive uses which software development kit (SDK), and why?

   :::answer{tests="trace-marker"}
   The installation's own `StrataScriptCore`, because the marker beside the editor tells the editor it runs from an installation. A machine without the marker uses the folder the build was made from, which a downloaded archive does not have.
   :::

## Exercises

1. **Basic.** Write a program that checks a tag the way the version job does: the tag is `v`, three numbers and an optional suffix, and its numbers must equal the project's version. It prints "publish" for a plain tag, "dry run" for a suffix and "refused" otherwise.

   :::answer[Worked solution]{tests="version-rules" solution="sketches/engineering-releasing-gate.cpp"}
   The program splits the tag at the first dash, takes the part before it as the base, checks that the base holds three numbers split by dots, and compares it with the project's version. A plain tag publishes and a tag with a suffix is a dry run.

   ```cpp sketch="engineering-releasing-gate.cpp"
   // A toy of the release workflow's version gate: a tag, the project's version and whether the release is published.
   #include <cstdio>
   #include <string>

   enum class Verdict
   {
   	Publish,
   	DryRun,
   	Refused
   };

   bool IsNumber(const std::string& text)
   {
   	if (text.empty())
   		return false;
   	for (char c : text)
   		if (c < '0' || c > '9')
   			return false;
   	return true;
   }

   // A tag is "v", three numbers split by dots, then nothing or "-" and a suffix.
   Verdict CheckTag(const std::string& tag, const std::string& projectVersion)
   {
   	if (tag.size() < 6 || tag[0] != 'v')
   		return Verdict::Refused;
   	const size_t dash = tag.find('-');
   	const std::string base = tag.substr(1, dash == std::string::npos ? std::string::npos : dash - 1);
   	const size_t firstDot = base.find('.');
   	const size_t secondDot = firstDot == std::string::npos ? std::string::npos : base.find('.', firstDot + 1);
   	if (secondDot == std::string::npos)
   		return Verdict::Refused;
   	if (!IsNumber(base.substr(0, firstDot)) || !IsNumber(base.substr(firstDot + 1, secondDot - firstDot - 1)) || !IsNumber(base.substr(secondDot + 1)))
   		return Verdict::Refused;
   	if (base != projectVersion)
   		return Verdict::Refused;
   	return dash == std::string::npos ? Verdict::Publish : Verdict::DryRun;
   }

   int main()
   {
   	const char* names[] = { "publish", "dry run", "refused" };
   	const char* tags[] = { "v0.7.0", "v0.7.0-rc1", "v0.8.0", "0.7.0", "v0.7" };
   	for (const char* tag : tags)
   		std::printf("%-12s %s\n", tag, names[static_cast<int>(CheckTag(tag, "0.7.0"))]);
   	return 0;
   }
   ```

   ```text output-of="engineering-releasing-gate.cpp"
   v0.7.0       publish
   v0.7.0-rc1   dry run
   v0.8.0       refused
   0.7.0        refused
   v0.7         refused
   ```

   1. **Lines 27–28:** the tag splits at its first dash into the base and the suffix.
   2. **Lines 29–34:** the base must hold three numbers split by dots.
   3. **Lines 35–37:** the base must equal the project's version; the suffix then decides between publish and dry run.
   :::

2. **Medium.** Make a local package: install a Dist build into a folder with `cmake --install`, pack it with `cpack`, and compare the folder's top level with the list in `StrataTests/Editor/InstallEndToEnd.cmake`.

   :::answer[Worked solution]{tests="add-release-file,check-archive"}
   Build the Dist configuration of your :term[preset]{id=preset}, then run `cmake --install build/<preset> --config Dist --prefix out`. The folder `out` holds the three programs, `StrataInstall.json`, `README.md`, `ThirdPartyNotices.md`, `Samples`, `StrataScriptCore`, `Docs` and `Skills`: ten entries, which is the list of `expected_entries` in the test. Then run `cpack --config build/<preset>/CPackConfig.cmake -C Dist` and find the archive in `build/<preset>/Packages`. On Windows use the `cpack` of CMake itself if another one comes first in the path.
   :::

3. **Hard.** Dry-run a release on a fork of the :term[repository]{id=repository}, then use the archive the way a person would: download the artifact, unpack it, run `StrataEditor --version`, compare the checksum and open a sample from the launcher.

   :::answer[Worked solution]{tests="dry-run,check-archive,version-rules"}
   Push a tag of the project's version with a suffix, such as `v0.8.0-rc1` for the version 0.8.0, to the fork and open the Actions tab. The version job prints the version, the tag and `publish: false`; open it to read each check. When the three build jobs end, download an artifact, unpack it and run `StrataEditor --version`: it prints `Strata Editor 0.8.0`. The `.sha256` file holds the value; compute it with `sha256sum` or `shasum -a 256` and compare. Start the editor and open a sample from the launcher.
   :::

4. **Hard.** Trace it yourself: follow `StrataInstall.json` from the rule that writes it to the editor code that reads it, and say what changes for script builds when it is there.

   :::answer[Worked solution]{tests="trace-marker"}
   Search the repository for `StrataInstall.json`. `CMake/StrataPackaging.cmake` writes it with `file(CONFIGURE ...)` and installs it at the top. `StrataEditor/src/Editor/ScriptToolchain.h` names it in `c_InstallationMarkerFile`, and `FindEngineInstallation` in `ScriptToolchain.cpp` searches for it in the folder of the editor's executable. `ScriptBuildSettings::Detect` then sets `EngineDirectory` to that folder, so builds use the installation's `StrataScriptCore`, and sets `FindToolchain`, so a compiler of this machine is searched for instead of the build machine's paths.
   :::

## Where it lives in Strata

- Packaging: `CMake/StrataPackaging.cmake`, `CMake/StrataPackageVersion.cmake`, the :term[cache variable]{id=cache-variable} `STRATA_PACKAGE_VERSION`.
- Release file: `.github/workflows/release.yml`; notes and the archive's `README.md` source in `Docs/Releases/`.
- Marker reader: `StrataEditor/src/Editor/ScriptToolchain.h` and `ScriptToolchain.cpp`, `FindEngineInstallation`.
- Tests: `StrataPackaging.Version` (`StrataTests/Packaging/PackageVersionTests.cmake`) and `StrataEditor.Install` (`StrataTests/Editor/InstallEndToEnd.cmake`).
- Commands: `cmake --install`, `cpack --config build/<preset>/CPackConfig.cmake -C Dist`, `ctest --preset <platform>-dist -LE "gpu|perf"`.

## Further reading

- CMake documentation, "Installing" and "cpack" (cmake.org): how install rules and archives work, intermediate.
- GitHub documentation on releases and workflow permissions (github.com): what the publish job uses, beginner.
- Semantic Versioning 2.0.0 (semver.org): how a version and its pre-release suffix are ordered, beginner.

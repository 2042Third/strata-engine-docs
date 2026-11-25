---
id: engineering/third-party
title: "Third-party code and pinned tools"
description: "How Strata takes in other people's code and tools: pinned submodules, one vendor file, a verified Slang download, and the notices a game ships."
kind: internals
size: L
tracks: [E]
needs: [engineering/flags-portability]
time: 85
learn:
  - id: pin-and-verify
    text: explain why Strata pins every dependency and checks a download against its SHA-256
  - id: vendor-wrapper
    text: explain why box3d and zstd are built from their sources with the flags the vendor file gives them
  - id: trace-fetch
    text: trace the path a configure takes through the Slang fetch for each state of the cache
  - id: licenses
    text: name the licenses that a game may copy from, and the notices an exported game carries
  - id: upgrade
    text: change a pinned dependency the way Strata does, in a commit of its own with the notices and every test
since: 0.8.0
status: final
---

A :term[game engine]{id=game-engine} does not write everything itself. It uses a window library, a math library, a physics library, a
data compression library and a :term[shader]{id=shader} :term[compiler]{id=compiler} that other people made. This page shows how Strata takes in that code. Strata fixes the
exact version of each piece, builds the pieces with one :term[CMake]{id=cmake} file, downloads one tool and checks it,
and keeps the licenses of all of them. The page does not teach how warnings are switched off for this code, which
`engineering/flags-portability` shows, nor how Slang compiles a shader, which the shaders page shows.

## The problem and how engines solve it

Take a small example. A game needs to unpack compressed data, and the engine team finds a library for that. If the team
copies its files into the engine's folder, the work is done in a minute. A year later the library has fixed a security
bug, and the team must learn which files changed, which of its own edits to keep, and which license text it forgot.
The problem has three parts: you must know exactly which version you run, you must be able to change it on purpose, and
you must keep the legal duties that come with the code.

**Vendoring** means keeping a copy of another project's code inside your own :term[repository]{id=repository}, so that the project builds from
what it holds and nothing else. Five ways to do it, or to avoid it, are in common use. The table gives what each costs.

| Technique | What it gives | What it costs |
| --- | --- | --- |
| Files copied into the tree | The build needs nothing from outside | Nobody knows which version it is; the project's history is lost; upgrades are manual edits |
| :term[Git]{id=git} submodules | One exact commit, with the whole history of the project | Every clone needs one more command; a submodule is a link, not a copy |
| A package manager such as `vcpkg` or `Conan` | Versions in one list; binaries may be shared | Another program on every machine; the package's build, not yours; a registry to trust |
| CMake's `FetchContent` | A download at configure time, with no extra program | A network on every first configure; a tag can move unless a :term[hash]{id=hash} is given |
| System packages | The least work for the person who builds | The version differs on every machine; Windows has no common source |

Two mistakes cost the most in practice. The first is code copied without its notice. Almost every license lets you use the
code freely if you keep its copyright notice and license text with it, so a copy without the
text breaks the license. The second is a library upgraded together with other changes. When the physics then behaves
differently, nobody can say whether the new library or the other change did it.

Strata chooses submodules for 19 libraries and one pinned download for one tool. A **submodule** (git) is a folder of
your repository that points at one exact commit of another repository. Strata's submodules are also **shallow**: git
fetches only that commit, not the project's whole history, so a fresh clone stays small. The cost is that a person must
run `git submodule update --init --recursive --depth 1` once after cloning, which `AGENTS.md` and the build guide state.

Strata uses no package manager: a search of the pin's file list finds no `vcpkg` or `conanfile` file. The reason is that
the engine wants every platform to build the same sources with the same flags. A package manager hands you a library
built by someone else, and the next sections show how many flags Strata sets on purpose.

## The map: what lives where

Every library sits in `Strata/vendor/`, one folder each, and one file, `Strata/vendor/CMakeLists.txt`, decides how each
is built. Small C files in `Strata/vendor/Implementations/` hold the single-file libraries' implementations. The compiler
Slang is the exception: it is no submodule, and `CMake/StrataSlang.cmake` fetches it into a folder of the current user.

```mermaid caption="Where each piece of third-party code lives and which programs take it" alt="A diagram with three groups. Pinned source folders feed one vendor file that builds them. A download of the shader compiler goes through a check into a folder of the user, and games and tools take different libraries."
flowchart LR
	subgraph repo["The repository"]
		sub["Strata/vendor: 19 submodules"]
		impl["Strata/vendor/Implementations"]
		wrap["Strata/vendor/CMakeLists.txt"]
		sub --> wrap
		impl --> wrap
	end
	subgraph user["The folder of the user"]
		cache["Toolchains cache: Slang"]
	end
	net["Release archive of Slang"] -->|"SHA-256 checked"| cache
	cache --> shaders["Shader build"]
	wrap --> games["Libraries games link"]
	wrap --> tools["Libraries only tools build"]
```

The vendor file makes two groups. The first is what a shipped game links: NVRHI, Vulkan-Headers, GLFW, glm, EnTT, `spdlog`, `nlohmann/json`,
stb, miniaudio, box3d and the decoder half of zstd. The :term[renderer]{id=renderer} also links `MikkTSpace` and `meshoptimizer`, which the notices file lists as editor only. The second group is built only when a tool needs it, because the
vendor file marks each of those targets `EXCLUDE_FROM_ALL`: Dear ImGui, ImGuizmo, `cgltf`, `nativefiledialog-extended` and the compression half of zstd. The proof that games hold no tooling is on the CMake page, `engineering/cmake`.

The notices file, `ThirdPartyNotices.md`, lists all of them with the version, the license and a column that says whether
the library is shipped in games.

## The contract

A person who adds or changes a dependency may assume that every library builds from the pinned commit, that it compiles
without warnings for the engine, and that the notices file lists it. The person must do the following. Each rule has its
reason.

- A library comes in as a pinned, shallow submodule under `Strata/vendor/`, wrapped by the one CMake file. The reason:
  the commit is the version, so a build today and a build in a year use the same code.
- Only the Slang compiler is downloaded, and only by `CMake/StrataSlang.cmake`, which checks a :term[SHA-256]{id=sha-256} digest before it
  uses a single :term[byte]{id=byte}. The reason: a download that nobody verifies is code that anyone on the network can replace.
- Every library has a row in `ThirdPartyNotices.md`, and a game ships that file. The reason: the licenses ask for it.

:::rule[Upgrade a submodule in a commit of its own]
Check out the new tag inside the submodule, rebuild, run all tests, update `ThirdPartyNotices.md` and commit the bump
alone. The reason is the second mistake of the problem section: when only the library changes, a failing test names its
cause. Strata states the same rule for Slang, whose bump is one commit with all four digests. Basics: the
[git page](../basics/git.md) shows how submodules and commits fit.
:::

:::rule[Never change the Slang digest to match a download]
A digest that differs from the pin means the bytes are not the release that Strata tested, so the build refuses them.
The reason is that the check exists to detect exactly this case. Change the digest only when the pin moves to a new
release, and then change all four in one commit.
:::

:::rule[Copyleft code is read for ideas only]
Strata copies or adapts code only under a permissive license. Copied copyleft code would choose Strata's own license for
it, which is the owner's choice and not a contributor's. The next sections define both kinds.
:::

## A toy version: the pinned fetch in one screen

:::question
The sketch uses functions, loops, a `struct`, a map, `std::optional` and calls such as `std::printf(`: see
[Programming 2](../basics/programming-2.md), [Programming 3](../basics/programming-3.md),
[generic C++](../basics/cpp-generic.md) and [modern C++](../basics/cpp-modern.md).
:::

The next program models the fetch of the Slang compiler without a network or files. The cache is a map from a folder's
name to the digest stamped on it, and a function returns an empty text on success and the reason on failure. A simple
hash called :term[FNV-1a]{id=fnv-1a} stands in for SHA-256, because writing SHA-256 would hide the shape of the algorithm. Watch the three
exits: the fast path, the loop of attempts and the digest check.

```cpp sketch="engineering-third-party-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <map>
#include <optional>
#include <string>

// A model of the pinned fetch: the cache is a map from folder name to the digest stamped on it.
// FNV-1a stands in for SHA-256 here; the shape of the algorithm is what the toy shows.
struct Network
{
	std::string Body;
	int FailuresLeft = 0;
};

static std::uint64_t Digest(const std::string& bytes)
{
	std::uint64_t hash = 14695981039346656037ull;
	for (char c : bytes)
		hash = (hash ^ static_cast<unsigned char>(c)) * 1099511628211ull;
	return hash;
}

static std::optional<std::string> Download(Network& network)
{
	if (network.FailuresLeft > 0)
	{
		network.FailuresLeft--;
		return std::nullopt;
	}
	return network.Body;
}

// Returns an empty string on success, else the reason. Never stops the program.
static std::string Fetch(std::map<std::string, std::uint64_t>& cache, Network& network, const std::string& name, std::uint64_t expected)
{
	const auto stamp = cache.find(name);
	if (stamp != cache.end() && stamp->second == expected)
	{
		std::printf("  stamp matches: no lock, no network\n");
		return "";
	}

	std::printf("  lock taken\n");
	std::optional<std::string> body;
	for (int attempt = 1; attempt <= 3 && !body; ++attempt)
	{
		std::printf("  download attempt %d\n", attempt);
		body = Download(network);
	}
	if (!body)
		return "could not download after 3 attempts";
	if (Digest(*body) != expected)
		return "digest differs from the pin: the download was not used";

	// Extract next to the final folder, then rename: nobody sees half an extraction.
	cache[name + ".staging"] = expected;
	cache[name] = cache[name + ".staging"];
	cache.erase(name + ".staging");
	std::printf("  extracted and renamed\n");
	return "";
}

static void Run(const char* title, std::map<std::string, std::uint64_t>& cache, Network& network, std::uint64_t expected)
{
	std::printf("%s\n", title);
	const std::string error = Fetch(cache, network, "slang", expected);
	std::printf("  result: %s\n", error.empty() ? "ready" : error.c_str());
}

int main()
{
	std::map<std::string, std::uint64_t> cache;
	Network network = { "archive bytes", 1 };
	const std::uint64_t pin = Digest("archive bytes");

	Run("1. first configure, one network failure", cache, network, pin);
	Run("2. second configure", cache, network, pin);
	Network replaced = { "other bytes", 0 };
	Run("3. the pin changed, the server sends other bytes", cache, replaced, Digest("archive bytes v2"));
	return 0;
}
```

```text output-of="engineering-third-party-toy.cpp"
1. first configure, one network failure
  lock taken
  download attempt 1
  download attempt 2
  extracted and renamed
  result: ready
2. second configure
  stamp matches: no lock, no network
  result: ready
3. the pin changed, the server sends other bytes
  lock taken
  download attempt 1
  result: digest differs from the pin: the download was not used
```

1. **Lines 15–21:** a stand-in hash: the real code asks CMake for the SHA-256 of the file.
2. **Lines 36–41:** the fast path returns before the lock and before any download.
3. **Lines 44–51:** the loop tries three times, then returns the reason as a text.
4. **Lines 52–53:** a body whose digest differs from the pin is never installed.
5. **Lines 55–58:** the extraction gets a staging name and then one rename gives it the final name.

Case 1 tries again once after the network failure and then installs. Case 2 finds the stamp and does nothing else: it takes
no lock and makes no download. Case 3 shows what a replaced release looks like: the bytes arrive, the digest does not
match, and nothing is installed. The real code adds a private folder, a lock between processes, a second look after the
lock, a real extraction and texts that tell a person what to do.

## The vendor file

The top of `Strata/vendor/CMakeLists.txt` sets the ground. It builds every library static, compiles vendor code with
warnings off and `/utf-8` on MSVC, and defines a small :term[macro]{id=macro}, `strata_vendor_option`, that sets a library's option as an
internal cache entry. An internal entry overrides any value from the :term[command line]{id=terminal-command} and stays out of the cache editor, so a person cannot switch NVRHI's DirectX backends on by accident.

Older libraries call `cmake_minimum_required` with a very old version, and CMake then applies old rules to them. The
file `CMake/StrataConfigurations.cmake` sets the defaults of three policies to `NEW`, so that these libraries still honor
Strata's settings. `CMP0077` makes an `option()` obey a normal variable. `CMP0091` and `CMP0141` let a property choose the MSVC :term[runtime]{id=runtime} library and the debug information format. It also sets
`CMAKE_POLICY_VERSION_MINIMUM` to 3.5, which newer CMake versions need before they configure a project that asks for less.

The project itself asks for CMake 3.25. That is the release that added the keyword `SYSTEM` to `add_subdirectory`. The
vendor file writes `add_subdirectory(NVRHI SYSTEM)` for the libraries that have a CMake file, and every target they make
marks its include folders as system folders. The compiler then stays quiet about the :term[headers]{id=header} of other people.

Each library gets its own few lines, and each line has a reason.

- `NVRHI` is built for Vulkan only, with its validation layer on, and without the DirectX backends, the memory
  utility and the vendor tools. The backend library `nvrhi_vk` uses the common library `nvrhi`, which NVRHI does not
  declare. The vendor file adds `target_link_libraries(nvrhi_vk PUBLIC nvrhi)`, because `ld` on Linux reads :term[static libraries]{id=static-library} in the
  order of the command line and needs `nvrhi` after `nvrhi_vk`.
- `glm` is header-only, so the vendor file declares an :term[interface library]{id=interface-library-cmake}. It defines `GLM_FORCE_DEPTH_ZERO_TO_ONE`,
  `GLM_ENABLE_EXPERIMENTAL` and `GLM_FORCE_SILENT_WARNINGS`, and no define that changes the layout of a type. The reason
  is the script application binary interface (ABI), the fixed layout of data passed between the engine and game
  scripts: glm types cross it, so they must stay plain.
- `spdlog` uses its bundled `fmt` (`SPDLOG_FMT_EXTERNAL` is off), so the engine needs no second formatting library.
- `nlohmann/json` is built with `JSON_ImplicitConversions` off. The engine then writes each conversion out, and a
  value of the wrong type cannot turn into another silently.
- `stb` is one static library with one :term[object file]{id=object-file} per header: image reading, image writing, image scaling, the block compression and the font library. The :term[linker]{id=linker} drops an object that nothing calls, so a game never carries the encoder or the scaling code. The font library shares an object with the rectangle packer, because the font code uses the packer
  when it sees its implementation.

The libraries that only tools build, such as Dear ImGui, are listed after one comment line that says why: a build of the
runtime alone never compiles them. How the build proves that is on `engineering/cmake`.

## box3d from its sources

box3d is the physics library. Its own CMake file does four things Strata does not want. It sets a `FETCHCONTENT_BASE_DIR` cache entry inside the source tree and exports compile commands. It adds install rules and a
debug suffix, and its source folder adds `/W4`, which would override the vendor `/W0`. So the vendor file compiles box3d's
`src/*.c` files itself, the way it does for zstd.

The next quote is the whole block. Search for one reason per setting: the language, the :term[determinism]{id=determinism}, the instruction set,
the asserts and the limit.

```cmake src="Strata/vendor/CMakeLists.txt#L149-L182"
if(STRATA_WITH_PHYSICS)
	set(BOX3D_DIR "${CMAKE_CURRENT_SOURCE_DIR}/box3d")
	file(GLOB BOX3D_SOURCES CONFIGURE_DEPENDS "${BOX3D_DIR}/src/*.c")
	add_library(box3d STATIC ${BOX3D_SOURCES})
	# C17 with extensions: box3d uses _Static_assert and anonymous unions.
	set_target_properties(box3d PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS YES)
	target_include_directories(box3d SYSTEM PUBLIC "${BOX3D_DIR}/include")
	target_include_directories(box3d PRIVATE "${BOX3D_DIR}/src")
	# Contraction into fused multiply-adds is the one value-changing transform compilers enable by default (arm64 Clang
	# does), and box3d's cross-platform determinism needs it off; MSVC does not contract under /fp:precise.
	if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
		if(CMAKE_C_COMPILER_FRONTEND_VARIANT STREQUAL "MSVC")
			target_compile_options(box3d PRIVATE /clang:-ffp-contract=off)
		else()
			target_compile_options(box3d PRIVATE -ffp-contract=off)
		endif()
	endif()
	# box3d picks its AVX2 kernels at run time (simd.c). GCC and Clang compile them through target pragmas; MSVC needs the
	# file itself compiled for AVX2.
	if(MSVC AND NOT CMAKE_C_COMPILER_ID STREQUAL "Clang" AND CMAKE_C_COMPILER_ARCHITECTURE_ID MATCHES "^(x64|X86)$")
		set_source_files_properties("${BOX3D_DIR}/src/wide8.c" PROPERTIES COMPILE_OPTIONS "/arch:AVX2")
	endif()
	# Asserts follow ST_CORE_ASSERT: on in Debug and Release, compiled out of Dist. PUBLIC, so that box3d's inline functions
	# agree in Strata's objects. box3d's heavy validation (BOX3D_VALIDATE) stays off: it makes Debug test runs several times
	# slower, and the golden hash and the physics suites cover correctness.
	target_compile_definitions(box3d PUBLIC "$<$<NOT:$<CONFIG:Dist>>:B3_ENABLE_ASSERT>")
	# The most triangles of a mesh one convex shape collides with at once (box3d's default is 512, beyond which it drops the
	# others and logs once): a 4 m crate on a render mesh of 10 cm triangles covers 3,200. The buffer is in box3d's per-worker
	# arena, not on the stack.
	target_compile_definitions(box3d PUBLIC B3_MAX_MESH_CONTACT_TRIANGLES=4096)
	if(UNIX AND NOT APPLE)
		target_link_libraries(box3d PUBLIC m)
	endif()
endif()
```

1. **Lines 151–152:** box3d's own CMake file is skipped; its C files are collected and built as one static library.
2. **Line 154:** C17 with extensions, because box3d uses `_Static_assert` and anonymous unions.
3. **Lines 159–165:** Merging into fused instructions is switched off on GCC and Clang, with the spelling `clang-cl` needs.
4. **Lines 168–170:** only `wide8.c` is compiled with `/arch:AVX2` on MSVC, since MSVC has no target options in the source.
5. **Lines 174–178:** asserts follow `ST_CORE_ASSERT`, and the triangle limit rises from 512 to 4,096 for every user of box3d.

The flag `-ffp-contract=off` needs a short story. A compiler may merge a multiplication and an addition into one fused
instruction, which rounds once instead of twice. Where the compiler does this, the result differs in the last bit from
a machine that does not.

box3d promises the same simulation on every platform, so Strata switches the merge off for
GCC and Clang, and for `clang-cl` through `/clang:-ffp-contract=off`. MSVC does not merge under `/fp:precise`, so it needs
no flag. The general idea, floating-point determinism, is on `engineering/flags-portability`.

The limit `B3_MAX_MESH_CONTACT_TRIANGLES` is a worked example of why a number in a build file deserves a comment. A
crate 4 m wide on a floor made of 10 cm squares lies over 40 by 40 squares, which is 1,600 squares and 3,200 triangles.
box3d's default of 512 keeps only the first 512 of them, drops the rest without an error and logs once. A large body
then lost its support. Strata raises the limit to 4,096, which is the next power of two above 3,200, and the buffer
lives in box3d's per-worker arena, not on the stack.

The tests use box3d's own determinism scenario, `shared/determinism.c`. The test project compiles it as a small static
library with the same C17 and no-contraction settings, because a scenario built differently from the library would test
nothing. The test then compares the hash of the result against the values that box3d's `test/test_determinism.c` holds.

## zstd, split in two

Asset packs store their blocks compressed with zstd, but a shipped game only reads them. So the vendor file builds two
libraries from one source folder. The next quote shows the decoder that games link, the compression half that only the pack
writer uses, and the line that joins them.

```cmake src="Strata/vendor/CMakeLists.txt#L204-L220"
target_include_directories(zstd_decompress SYSTEM PUBLIC "${ZSTD_DIR}")
target_compile_definitions(zstd_decompress PUBLIC ZSTD_DISABLE_ASM=1 ZSTD_LEGACY_SUPPORT=0)
add_library(zstd_compress STATIC EXCLUDE_FROM_ALL
	"${ZSTD_DIR}/compress/fse_compress.c"
	"${ZSTD_DIR}/compress/hist.c"
	"${ZSTD_DIR}/compress/huf_compress.c"
	"${ZSTD_DIR}/compress/zstd_compress.c"
	"${ZSTD_DIR}/compress/zstd_compress_literals.c"
	"${ZSTD_DIR}/compress/zstd_compress_sequences.c"
	"${ZSTD_DIR}/compress/zstd_compress_superblock.c"
	"${ZSTD_DIR}/compress/zstd_double_fast.c"
	"${ZSTD_DIR}/compress/zstd_fast.c"
	"${ZSTD_DIR}/compress/zstd_lazy.c"
	"${ZSTD_DIR}/compress/zstd_ldm.c"
	"${ZSTD_DIR}/compress/zstd_opt.c"
	"${ZSTD_DIR}/compress/zstd_preSplit.c")
target_link_libraries(zstd_compress PUBLIC zstd_decompress)
```

1. **Lines 204–205:** the decoder's public defines reach every target that links it.
2. **Line 206:** the compression half is excluded from the default build.
3. **Lines 207–219:** the compression sources; the decoder's files are not repeated here.
4. **Line 220:** the compression half links the decoder, whose shared files it uses.

The compression half is marked `EXCLUDE_FROM_ALL`, so a build of the runtime never compiles it, and the engine's pack writer
links it.

The decoder defines `ZSTD_DISABLE_ASM=1`, which drops the x86-64 assembly decoder. That file needs an
extra build step for assembly on GCC and Clang only. MSVC always runs the portable C decoder, so with the flag every platform runs
the same code.

`ZSTD_LEGACY_SUPPORT=0` omits the decoders of old formats that no Strata pack uses. Packs compress
their blocks in parallel on the engine's job system, so zstd's own threads stay off. How the packs use the library is on
`assets/packs-export`.

## Licenses and the notices a game ships

A **permissive** license lets you copy, change and sell the code if you keep its copyright notice and license text with
it.

A **copyleft license** (`GPL`, `LGPL`, `AGPL` and `MPL` are examples) asks that any code combined with it must follow the
same terms. The difference matters to an engine because its users ship programs. If a copyleft library were copied into
Strata, a game made with Strata could owe its source to everyone who gets the game.

Strata therefore copies and adapts code only from projects under licenses such as MIT, `BSD`, Apache-2.0, zlib or public
domain, and reads copyleft code for ideas only. Two places record what came in.

1. The submodule table at the top of `ThirdPartyNotices.md`. Each row has the library, its version, its license, a
   column "Shipped in games" with the values Yes, Editor only, No (build tool or tests), Optional, or Yes for decoding
   only (zstd), and its purpose. The Slang row says No: the compiler runs at build time and no game contains it.
2. The table of code derived from other projects, which covers code that is no submodule. At the pin it has two rows:
   the radiance-cascades-lab project under the MIT license, with the Strata shader files derived from it, and `ltc_code`
   under a `BSD` license, with the rect lights' tables. The licenses' full texts stand below the table. They are there
   because games ship that file and no submodule carries them.

The editor's fonts (`Inter`, `JetBrains Mono` and `Lucide`) are committed release files with their license texts, and the
notices file lists them. The engine's default text font, Roboto Medium, is compiled in from the copy that Dear ImGui
distributes and ships in every game. The sample games add one more duty: their assets come under `CC0` or `CC-BY`, and each
sample's `CREDITS.md` names the files, the authors and the licenses, as the notices file does for a whole game. The
credits of the book's own pictures are on `appendix/credits`.

The exporter copies `ThirdPartyNotices.md` into each game. So the rule for a game maker is short: do not remove that file
from an export, and show the attribution that a CC-BY asset asks for.

## Verified downloads that can be repeated

One tool cannot be a submodule. The Slang compiler is a binary release with a different archive for each platform, and the
repository should not hold those binaries. Strata pins four archives of Slang 2026.20: Windows
on x86-64, Linux on x86-64, and macOS on both arm64 and x86-64. Each has a file name and a digest in
`CMake/StrataSlang.cmake`.

A **SHA-256 pin** is a SHA-256 digest written into the repository, which a download must match before the build uses
it. SHA-256 turns any file into 256 bits, written as 64 :term[hexadecimal]{id=hexadecimal} characters; a change of one byte changes the digest
in a way nobody can plan. So a download that matches the pin is the file that Strata's developers tested. The digest
must not come from the server that sends the file, since an attacker who replaces the file would replace the digest
too. The pin lives in the repository, where only a reviewed commit changes it.

The place where the fetched files live is a **per-user cache**: a folder in the user's own area that holds files shared
between all projects of that user. On Windows it is `%LOCALAPPDATA%/Strata/Toolchains`, on macOS
`~/Library/Caches/Strata/Toolchains`, and on Linux `$XDG_CACHE_HOME/strata/toolchains` when that variable is an :term[absolute
path]{id=absolute-path}, else `~/.cache/strata/toolchains`. Every copy of the repository and every build folder of the user shares one download, and
nobody else can change the files the build runs.

### What a configure does

`strata_find_slang` is the entry point that the shader build calls. First it reads `STRATA_SLANG_ROOT`, a cache variable
whose first value comes from the :term[environment variable]{id=environment-variable} of the same name. When it is set, the function asks
`strata_slang_check` to run `slangc -v` in that folder, and the output must be exactly the pinned version, 2026.20. A
failure stops the configure with a message that says what to do.

When the variable is empty, the function finds the
host's key, the cache folder and the folder's name, and compares the stamp in that folder with the pinned digest. The
result decides only the word in the log line: `cached` or `downloaded`. Then `strata_slang_fetch` does the real work.

:::example[Three configures in a row]
A new build folder on a Windows machine with an empty cache. The first configure finds no stamp, so it logs
`Downloading slang-2026.20-windows-x86_64.zip into ...Toolchains`, verifies it and ends with `Slang 2026.20: <folder>/bin/slangc.exe (downloaded)`.
A second build folder, configured a minute later, finds the stamp equal to the digest `e6dd32bb...` and logs `(cached)`
without a lock or a connection. A third configure with `-DSTRATA_SLANG_ROOT=D:/tools/slang` never touches the cache: it
runs `D:/tools/slang/bin/slangc.exe -v`, accepts the answer `2026.20` and logs `(STRATA_SLANG_ROOT)`. A folder with
Slang 2026.19 in it fails the check and stops the configure with the text `is Slang 2026.19; Strata's shaders are pinned
to 2026.20`.
:::

### The fetch, step by step

`strata_slang_fetch` never fails the configure by itself. On success it returns the folder, and on failure it returns an
empty folder and the reason as a text, and the caller decides to stop. The next quote is the beginning: the fast path,
the private folder, the lock and the second look. Search for what happens before any byte is downloaded.

```cmake src="CMake/StrataSlang.cmake#L142-L168"
# A complete extraction of this digest: no lock, no network.
strata_slang_read_stamp(stamp "${final}")
if(stamp STREQUAL expected)
	set(${outRoot} "${final}" PARENT_SCOPE)
	return()
endif()

if(NOT IS_DIRECTORY "${ARG_CACHE_DIR}")
	file(MAKE_DIRECTORY "${ARG_CACHE_DIR}")
	# The cache holds programs the build runs, so only its user may change it.
	if(NOT CMAKE_HOST_WIN32)
		file(CHMOD "${ARG_CACHE_DIR}" DIRECTORY_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE)
	endif()
endif()
set(lock "${ARG_CACHE_DIR}/${ARG_NAME}.lock")
file(LOCK "${lock}" GUARD FUNCTION TIMEOUT 900 RESULT_VARIABLE lockResult)
if(NOT lockResult EQUAL 0)
	set(${outError} "Another configure has held ${lock} for 15 minutes. If none runs, delete the file and configure again." PARENT_SCOPE)
	return()
endif()

# Another configure may have finished the extraction while this one waited for the lock.
strata_slang_read_stamp(stamp "${final}")
if(stamp STREQUAL expected)
	set(${outRoot} "${final}" PARENT_SCOPE)
	return()
endif()
```

1. **Lines 143–147:** the fast path compares the stamp with the digest and returns with no lock and no network.
2. **Lines 149–155:** the cache folder is made, and on systems other than Windows only its owner may use it.
3. **Lines 156–161:** the lock file has a limit of 900 seconds, and a timeout returns an error text.
4. **Lines 163–168:** the second look, for a configure that waited while another one finished.

The fast path reads the stamp and returns if it equals the digest, with no lock and no network. Otherwise the function
creates the cache folder if it is missing, and on systems other than Windows restricts it to the owner, because the cache
holds programs that the build runs. The lock is a file next to the folder with a 900-second limit, which is 15 minutes.

Two configures that start together, for example two build folders made by a script, must not download and extract in
the same place. One waits, and the second look after the lock finds that the other has finished. A lock that is still held
after 15 minutes gives an error that names the file and says to delete it if no other configure runs.

The next quote is the download and the check.

```cmake src="CMake/StrataSlang.cmake#L170-L205"
set(part "${final}.part")
set(staging "${final}.staging")
file(REMOVE "${part}")
set(downloaded FALSE)
set(statusMessage "")
foreach(attempt RANGE 1 3)
	if(attempt EQUAL 1)
		message(STATUS "Downloading ${archive} into ${ARG_CACHE_DIR}")
	else()
		message(STATUS "Downloading ${archive} again (attempt ${attempt} of 3)")
		execute_process(COMMAND "${CMAKE_COMMAND}" -E sleep 2)
	endif()
	file(DOWNLOAD "${ARG_URL}" "${part}" STATUS status INACTIVITY_TIMEOUT 60 TIMEOUT 1200 TLS_VERIFY ON)
	list(GET status 0 statusCode)
	list(LENGTH status statusLength)
	if(statusLength GREATER 1)
		list(GET status 1 statusMessage)
	endif()
	if(statusCode EQUAL 0)
		set(downloaded TRUE)
		break()
	endif()
endforeach()
if(NOT downloaded)
	file(REMOVE "${part}")
	set(${outError} "Strata compiles its shaders with Slang ${STRATA_SLANG_VERSION} and could not download it from ${ARG_URL}: ${statusMessage}. Connect to the network and configure again, or download ${archive} on another machine, check that its SHA-256 is ${expected}, extract it and configure with -DSTRATA_SLANG_ROOT=<the extracted folder> (or set the environment variable STRATA_SLANG_ROOT)." PARENT_SCOPE)
	return()
endif()

file(SHA256 "${part}" actual)
string(TOLOWER "${actual}" actual)
if(NOT actual STREQUAL expected)
	file(REMOVE "${part}")
	set(${outError} "The download of ${ARG_URL} has SHA-256 ${actual}, not the pinned ${expected}: it was not used. Configure again to download it again; if it keeps differing, the release was replaced: report it, do not change the digest to match." PARENT_SCOPE)
	return()
endif()
```

1. **Lines 175–192:** three attempts, with a pause of two seconds before each repeat.
2. **Line 182:** the download goes to a `.part` file with limits of 60 and 1,200 seconds and the certificate check on.
3. **Lines 193–197:** after three failures the text names the version, the address and the way out.
4. **Lines 199–205:** the digest of the `.part` file is compared with the pin, and a different digest deletes it.

The loop makes at most three attempts and waits two seconds between them. Each download stops after 60 seconds without data or after 1,200 seconds in all, and the check of the server's certificate is on. Three failures give a message that names the
version, the web address and the reason. The message also says how to continue on a machine without a network: download the
archive elsewhere, check its digest, extract it and set `STRATA_SLANG_ROOT`.

A download that arrives but has another digest is
deleted and reported, with both digests in the text. The text ends with the rule: the release was replaced, report it,
and do not change the digest to match.

The last part extracts and installs.

```cmake src="CMake/StrataSlang.cmake#L207-L251"
	file(REMOVE_RECURSE "${final}" "${staging}")
	file(MAKE_DIRECTORY "${staging}")
	set(patterns "")
	foreach(path IN LISTS ARG_FILES)
		if(ARG_ROOT_IN_ARCHIVE)
			list(APPEND patterns "${ARG_ROOT_IN_ARCHIVE}/${path}")
		else()
			list(APPEND patterns "${path}")
		endif()
	endforeach()
	# Extracted by a child CMake: an archive that lacks a listed path is an error of that process, which this one reports
	# instead of failing the configure (file(ARCHIVE_EXTRACT) would).
	execute_process(COMMAND "${CMAKE_COMMAND}" -E tar xf "${part}" -- ${patterns}
		WORKING_DIRECTORY "${staging}" RESULT_VARIABLE extractResult OUTPUT_VARIABLE extractOutput ERROR_VARIABLE extractOutput)
	string(STRIP "${extractOutput}" extractOutput)
	set(root "${staging}")
	if(ARG_ROOT_IN_ARCHIVE)
		set(root "${staging}/${ARG_ROOT_IN_ARCHIVE}")
	endif()
	if(NOT EXISTS "${root}/bin/${compiler}")
		file(REMOVE_RECURSE "${staging}")
		file(REMOVE "${part}")
		set(${outError} "${archive} holds no bin/${compiler} (${extractOutput})" PARENT_SCOPE)
		return()
	endif()
	if(NOT extractResult EQUAL 0)
		file(REMOVE_RECURSE "${staging}")
		file(REMOVE "${part}")
		set(${outError} "${archive} could not be extracted into ${staging}: ${extractOutput}" PARENT_SCOPE)
		return()
	endif()

	file(WRITE "${root}/.strata-slang-sha256" "${expected}\n")
	file(RENAME "${root}" "${final}" RESULT renameResult)
	if(ARG_ROOT_IN_ARCHIVE)
		file(REMOVE_RECURSE "${staging}")
	endif()
	file(REMOVE "${part}")
	if(NOT renameResult EQUAL 0)
		file(REMOVE_RECURSE "${staging}")
		set(${outError} "Could not move the extraction of ${archive} to ${final}: ${renameResult}" PARENT_SCOPE)
		return()
	endif()
	set(${outRoot} "${final}" PARENT_SCOPE)
endfunction()
```

1. **Lines 207–216:** an old folder and old staging are removed, and the list of wanted paths is built.
2. **Lines 219–220:** a child CMake extracts only those paths into the staging folder.
3. **Lines 226–237:** a missing compiler or a failed extraction removes the staging folder and returns a reason.
4. **Lines 239–240:** the stamp is written inside the staging folder, and then one rename moves it into place.
5. **Lines 245–249:** a failed rename removes the staging folder and returns a reason.

The extraction lists only the files that `slangc` needs: the compiler, the libraries it loads and the licenses. The
documentation is omitted because its paths are too long for some Windows caches, and `slang-llvm` is omitted because
it is up to 107 MB and plain shader code never needs it. A child CMake process does the extraction, so an archive that
lacks a listed path is an error that the function reports instead of an error that stops the configure. The stamp is
written inside the staging folder, and the final `file(RENAME)` moves the whole folder into place. A reader of the cache
sees either no folder or a complete one with its stamp, never a half-written one.

Every failure edge ends in a text for a person, as the diagram shows.

```mermaid caption="The fetch as a state machine: every edge that fails ends in a message, and only a stamp of the right digest ends the walk early" alt="A diagram. The stamp check leads to done or to the lock. The lock leads to a second stamp check, then up to three downloads, a digest check, an extraction and a rename. Each failing step ends in an error message."
flowchart TD
	start["Start"] --> stamp{"Stamp equals pin?"}
	stamp -- "yes" --> done["Return the folder"]
	stamp -- "no" --> lock{"Lock within 15 minutes?"}
	lock -- "no" --> e1["Error: delete the lock file"]
	lock -- "yes" --> again{"Stamp equals pin now?"}
	again -- "yes" --> done
	again -- "no" --> dl{"Download in 3 attempts?"}
	dl -- "no" --> e2["Error: set the override"]
	dl -- "yes" --> hash{"SHA-256 equals pin?"}
	hash -- "no" --> e3["Error: replaced release"]
	hash -- "yes" --> ex{"Compiler in the archive?"}
	ex -- "no" --> e4["Error: archive holds no compiler"]
	ex -- "yes" --> mv{"Rename succeeds?"}
	mv -- "no" --> e5["Error: could not move"]
	mv -- "yes" --> done
```

:::why[A failing fetch returns a reason instead of stopping]
The function lives in a file that tests include in :term[script mode]{id=script-mode}, and a function that stops the process cannot be tested for
its failures. So it returns the reason and `strata_find_slang` decides. The cost is that every caller must remember to
test the error, and this one function is the only caller.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A package manager (`vcpkg`, `Conan`) | Many C++ projects, large studios | Shared versions across projects, ready-made binaries | The same flags on every platform; the build needs another program |
| `FetchContent` for every library | Projects that want no submodules | No submodule command after cloning | A network on first configure, and a download for each library to verify |
| Libraries copied into the tree | Small projects, many single-header libraries | A repository that builds with no extra step | The commit that tells you the version, and simple upgrades |
| The Slang compiler as a submodule | Projects that build their compiler | Source for a compiler that Strata could patch | A long build of a large project and a large clone |
| System packages for libraries | Linux distributions | Security fixes from the system's updates | Equal behavior: versions differ by machine, and Windows has none |

## How it is tested

The test `StrataSlang.Fetch` runs the script `StrataTests/Shaders/SlangFetchTests.cmake` through `cmake -P` in a work
folder. It builds fake archives and serves them through `file://` addresses into a private cache, so it never touches the real
cache or the network. It checks nine cases:

1. A fresh fetch extracts only the listed folder and stamps the digest, and leaves no `.part` or `.staging` behind.
2. A cache hit works with the archive moved away.
3. A stamp of another digest extracts again, and the stale file disappears.
4. A wrong digest is refused, the text holds both digests, and nothing is left.
5. A missing archive gives a text with the web address, the archive name, `STRATA_SLANG_ROOT` and the digest.
6. An archive without the compiler is refused.
7. A folder without the compiler is named by the check.
8. The cache folder of each system, with test values for `LOCALAPPDATA`, `HOME` and `XDG_CACHE_HOME`.
9. The host key of the machine that runs the test.

Run it with `ctest --preset windows-debug -R StrataSlang.Fetch`. The lock's timeout, the three attempts and the
private permissions are not in the nine cases, so a change to them needs a check by hand.

For box3d, the case "box3d's cross-platform determinism scenario matches its golden hash, with any number of workers"
of the suite `Physics.Box3D` runs the scenario on the stepping thread alone and again with four job workers. Its golden hash stays the same on every
platform, which is why the flag `-ffp-contract=off` is there. What the hash means for the step is on `physics/world-step`.

## Changing it safely

To add a library, add the submodule at a tag. Add a block to the vendor file with each option forced and a comment for each setting that is not obvious. Link the library to the layer that uses it through the :term[layer table]{id=layer-table}, and add a row to `ThirdPartyNotices.md`. To upgrade one, follow the rule above: its own commit, the notices updated, every test run. After adding files, configure again, because the sources are collected by `GLOB`.

For code from another project, read open-source code as much as helps. Copy it only under a permissive license, add a row and the license text to the derived-code table, and name the project, its commit and the files in the commit message. Copyleft code gives ideas and nothing else. Check the checklist of `AGENTS.md` before the commit.

For Slang, bump the version, all four archive names and all four digests together, in a commit of its own. Take each digest from the release page and check it against a second source. Never copy the digest from the one download you made a moment ago. For box3d, if an upgrade changes the golden values, take the new ones only from box3d's own test file.

## What went wrong before

The default limit of mesh contact triangles once made a large body lose its support. A large crate on a dense mesh floor lost it because box3d dropped triangles beyond 512 without an error. The vendor file now raises the limit.

The case "A large crate rests on a dense mesh floor" of the physics behavior tests places a 4 m crate on a floor of 10 cm squares. Those are the numbers of the worked example above. The test checks that the crate rests.

## Summary

- Strata pins every dependency: a shallow submodule, or for Slang a SHA-256 digest. A build today equals a build in a year, and a download that differs from the pin is never used.
- One vendor file builds each library with its options forced. box3d and zstd are built from sources, so that Strata controls the language, the instruction set, the floating-point contraction and which half of zstd games link.
- The Slang fetch has a fast path with no lock and no network, a lock with a 15-minute limit, three attempts, a digest check, an extraction of listed files and an atomic rename. Each failure returns a message, and `strata_find_slang` stops the configure with it.
- Games carry permissive licenses only; `ThirdPartyNotices.md` lists every library and whether games ship it, and
  copyleft code is read for ideas and never copied.
- An upgrade is a commit of its own, with the notices updated and every test run; the Slang digest changes only
  with the release.

## Check yourself

1. A teammate says: "The digest check fails on my machine, so I will paste the new digest into the file." What is right?

   - A. Do it: the digest only checks that the file downloaded.
   - B. Do it, but only on your own machine.
   - C. Do not: a different digest means the release was replaced or the download broke, so configure again and report it.

   :::answer{tests="pin-and-verify"}
   C. A is wrong because the digest is the proof that the bytes are the release Strata tested. B is wrong because the
   file is in the repository, so the change would reach everyone at the next commit.
   :::

2. Which of these must be true when a second configure logs `(cached)`?

   - A. The stamp in the cache folder equals the pinned digest.
   - B. The download of the archive succeeded a minute ago.
   - C. `STRATA_SLANG_ROOT` is set.

   :::answer{tests="trace-fetch"}
   A. The word is decided by the stamp and the pin only. B is wrong because no download happens on this path. C is wrong
   because that variable gives `(STRATA_SLANG_ROOT)` and never touches the cache.
   :::

3. Why does the vendor file build box3d from its sources instead of using box3d's own CMake file?

   :::answer{tests="vendor-wrapper"}
   box3d's file sets a cache entry inside the source tree, adds install rules and a debug suffix, and adds `/W4`, which
   overrides the vendor `/W0`. Building from sources also lets the vendor file set `-ffp-contract=off`, the `/arch:AVX2` option on
   `wide8.c`, the asserts and the triangle limit with a reason each.
   :::

4. A game links glm, box3d and a copyleft library of 20,000 lines that a contributor wants to add. What does the
   contributor do?

   :::answer{tests="licenses"}
   The contributor does not copy or add the code: Strata's rule allows copyleft code to be read for ideas only. The two
   other libraries are permissive (MIT), so their notices go with the game in `ThirdPartyNotices.md`.
   :::

5. Predict: a configure with `STRATA_SLANG_ROOT` pointing at a Slang 2026.19 folder. What happens?

   :::answer{tests="trace-fetch,upgrade"}
   `strata_slang_check` runs `slangc -v`, the answer does not match 2026.20, and the configure stops with a message that
   names the folder, the version found and the pin. It does not fall back to the cache. To upgrade the pin, change the
   version and all four digests together, in a commit of its own.
   :::

## Exercises

1. **Basic.** Read `ThirdPartyNotices.md` and the `CREDITS.md` of `Samples/Tetris`. List what an exported Tetris game
   must credit.

   :::answer[Worked solution]{tests="licenses"}
   The game ships `ThirdPartyNotices.md`, which names every library the game links, with its license. The rows marked Yes in the column "Shipped in games" are GLFW, NVRHI, Vulkan-Headers, glm, EnTT, box3d, miniaudio, `spdlog`, `nlohmann/json`, Dear ImGui, stb and the decoder of zstd.

   The notices also name the font Roboto Medium and hold the license texts of the radiance-cascades-lab and `ltc_code` code. The sample's `CREDITS.md` has two rows, the sounds and the icon. Both carry the license `Strata` and no attribution, so the game owes no pack credits. Editor-only rows do not count.
   :::

2. **Medium.** Write a program that applies the fast path of the fetch: it compares a stamp and a pin in lower case and
   says whether to use the folder again. Test three cases: no stamp, the same digest in other letter case, and a bumped pin.

   :::answer[Worked solution]{solution="sketches/engineering-third-party-stamp.cpp" tests="pin-and-verify"}
   The function `Lower` turns both texts to lower case, as the real code does with `string(TOLOWER ...)`, so a digest
   copied in capitals still matches.

   ```cpp sketch="engineering-third-party-stamp.cpp"
   #include <algorithm>
   #include <cctype>
   #include <cstdio>
   #include <string>

   // The fast path of the fetch: a folder is reused when its stamp equals the pinned digest.
   // Both sides are compared in lower case, as the real code does.
   static std::string Lower(std::string text)
   {
   	std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
   	return text;
   }

   static const char* Decide(const std::string& stamp, const std::string& pin)
   {
   	return Lower(stamp) == Lower(pin) ? "reuse the folder, no lock, no network" : "take the lock and fetch";
   }

   int main()
   {
   	std::printf("no stamp:         %s\n", Decide("", "E6DD32"));
   	std::printf("same digest:      %s\n", Decide("e6dd32", "E6DD32"));
   	std::printf("pin was bumped:   %s\n", Decide("e6dd32", "B83147"));
   	return 0;
   }
   ```

   ```text output-of="engineering-third-party-stamp.cpp"
   no stamp:         take the lock and fetch
   same digest:      reuse the folder, no lock, no network
   pin was bumped:   take the lock and fetch
   ```

   1. **Lines 8–12:** both texts are turned to lower case before they are compared.
   2. **Line 16:** the one comparison that decides the fast path.
   3. **Lines 21–23:** three cases: no stamp, the same digest in other letter case, and a bumped pin.
   :::

3. **Medium.** Zstd 1.5.8 arrives. Write the steps of the upgrade and name the file and the test that guard it.

   :::answer[Worked solution]{tests="upgrade,vendor-wrapper"}
   Check out the new tag inside the zstd submodule. If it adds or renames a :term[source file]{id=source-file}, edit the lists of
   `zstd_decompress` or `zstd_compress` in `Strata/vendor/CMakeLists.txt` and configure again. Build, then run every test
   (`ctest --preset windows-debug -j 8`), because pack reading and writing both use it. Update the version in
   `ThirdPartyNotices.md`. Commit the bump alone, with the notices, so a failing test points at zstd.
   :::

4. **Hard.** Trace it yourself: configure a fresh build folder twice, then a third time with `STRATA_SLANG_ROOT`, and
   find the path of each configure through `strata_find_slang` and `strata_slang_fetch`.

   :::answer[Worked solution]{tests="trace-fetch"}
   Run `cmake --preset windows -B build/trace-1` and read the status lines, or run
   `cmake --trace-source=CMake/StrataSlang.cmake --preset windows -B build/trace-1`, which prints each line the file runs.
   The first configure passes the branch where the stamp differs, reaches the lock, the download and the rename in
   `strata_slang_fetch` of `CMake/StrataSlang.cmake`, and ends `(downloaded)`. The second returns at the first `return()`
   of the fast path and ends `(cached)`. The third, with `-DSTRATA_SLANG_ROOT=<folder>`, runs `strata_slang_check` in
   `strata_find_slang` and never calls `strata_slang_fetch`, ending `(STRATA_SLANG_ROOT)`.
   :::

## Where it lives in Strata

- `Strata/vendor/CMakeLists.txt`: the vendor file, with the options, box3d and zstd; `Strata/vendor/Implementations/`: the
  single-file libraries' implementations.
- `.gitmodules`: the 19 shallow submodules.
- `CMake/StrataSlang.cmake`: the pin, `strata_find_slang`, `strata_slang_fetch`, `strata_slang_check`.
- `CMake/StrataConfigurations.cmake`: the policy defaults for third-party projects.
- `ThirdPartyNotices.md`: the notices; the `CREDITS.md` of each sample, such as `Samples/Tetris/CREDITS.md`: the credits of the sample assets.
- `StrataTests/Shaders/SlangFetchTests.cmake` (the test `StrataSlang.Fetch`); `StrataTests/src/Physics/PhysicsBox3DTests.cpp`
  (the suite `Physics.Box3D`).
- Settings: `STRATA_SLANG_ROOT` (cache variable and environment variable).

## Further reading

- The SHA-2 family of hash functions, on a standards site such as NIST (beginner to intermediate): what a digest is.
- The git documentation on submodules (beginner): how a submodule is a link to a commit.
- The CMake documentation of `add_subdirectory` and `file(DOWNLOAD)` (intermediate): the options the vendor file and the
  fetch use.
- The Open Source Initiative's list of licenses (beginner): the differences between permissive and copyleft licenses.

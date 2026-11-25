---
id: engineering/flags-portability
title: "Compiler flags, compile time and portability"
description: "How Strata compiles every first-party object: the warning policy, the instruction sets, the precompiled headers, and how three compilers stay in agreement."
kind: internals
size: L
tracks: [E]
needs: [engineering/cmake, basics/numbers]
time: 70
learn:
  - id: warnings-policy
    text: explain why a warning fails the build, and why the fix is never to silence it where it appears
  - id: fma-flags
    text: explain why a compiler flag such as -mfma can change a number, and name the Strata option that removes the change
  - id: pch-contents
    text: choose what belongs in a precompiled header and what does not, and give the reason
  - id: compatlint
    text: find what CI's older compilers reject before a push by running `CompatLint`, and say what it cannot check
since: 0.4.0
status: final
---

Every first-party :term[source file]{id=source-file} of Strata passes through one small set of :term[compiler]{id=compiler} settings, and this page is about those settings. They decide which mistakes stop the build, which instructions the :term[machine code]{id=machine-code} may use, how much work the compiler repeats for each file, and whether three different compilers agree on what the code means. The page does not teach how :term[CMake]{id=cmake} makes and links targets; [CMake in Strata](cmake.md) does. It also leaves the flags of vendor libraries to [third-party code](third-party.md) and the list of jobs of continuous integration (CI) to [CI in Strata](ci.md). What remains is the code of `CMake/StrataCompilerOptions.cmake`, the files that hold the compile-time rules, and the tool that checks a change against older compilers.

## The problem and how engines solve it

One source file does not mean one program. A compiler turns the text into machine code, and a different compiler, a different version or a different flag turns the same text into different code. Three differences matter to an engine.

The first difference is what the compiler tells you. A line that one compiler accepts in silence, another warns about, and a third rejects. The engine builds on three compilers and two :term[standard libraries]{id=standard-library}, so a mistake that the compiler on your desk accepts can break the build on the machine of a teammate. Teams answer with a warning policy: switch on the strict warning levels everywhere, and treat each warning as an error. A warning that does not fail the build is read once and then ignored, and a build with two hundred warnings hides the two hundred and first.

The second difference is the code itself. A flag that allows a new instruction lets the compiler write a faster program, and sometimes a program with a slightly different answer. [Floating-point numbers](../basics/numbers.md) are rounded after each operation, so a change in the number of operations is a change in the rounding. An engine that wants the same physics result on two platforms must know which flags touch the rounding.

The third difference is time. A large engine has thousands of source files, and each one includes the same standard :term[headers]{id=header} again. Engines answer in three ways. A shared, precompiled copy of the common headers saves the repeated reading, lighter headers leave less to read, and a cache of finished objects skips the compile when the same input comes twice.

Some engines also join many source files into one before compiling, a unity build, which saves the repeated reading at the price of one huge file whose names can collide. Strata does not use unity builds: every source compiles as its own unit. A search of the build files for a unity setting finds nothing.

Each answer has a cost. A strict policy makes a new compiler version a small chore, because a new warning breaks the build until someone fixes the code. Fast code flags tie the program to a processor. A shared header copy hides a missing include, which the next section shows. The rest of the page is how Strata pays each cost, and why it judged the price right.

## The map of the settings

Four places hold nearly all of the rules. The first is `CMake/StrataCompilerOptions.cmake`, which defines the functions `strata_configure_target`, `strata_engine_cpu_options` and `strata_precompile_headers`, and the options that choose the instruction sets. The second is `Strata/CMakeLists.txt`, which makes the one `StrataEngineCodegen` target. The third is `CMake/StrataLayers.cmake`, which applies all of them to every layer library, and the fourth is `Strata/vendor/CMakeLists.txt`, which silences the third-party code. Two things stand outside the build: the tests that guard the headers, and the tool `Tools/CompatLint.py`.

```mermaid caption="Where the compile settings come from. The options choose the instruction sets, a function turns them into flags, and one shared target hands them to every layer library, together with the warning policy and the precompiled header. The vendor code gets its own, quieter flags." alt="A diagram of boxes and arrows. The instruction set options lead to the function that builds the instruction set flags. That function feeds the shared code generation target. The shared target, the warning policy function and the precompiled header function all lead to each layer library. The vendor file leads separately to the vendor libraries, which the layer libraries link."
flowchart TD
	options["STRATA_USE_* options, STRATA_CROSS_PLATFORM_DETERMINISTIC"] --> cpu["strata_engine_cpu_options"]
	cpu --> codegen["StrataEngineCodegen (INTERFACE)"]
	codegen --> layers["Strata_Core, Strata_Scene, ... (layer libraries)"]
	warn["strata_configure_target: warnings, definitions"] --> layers
	pch["strata_precompile_headers: stpch.h"] --> layers
	vendor["Strata/vendor/CMakeLists.txt: /W0 or -w, SYSTEM"] --> vendorlibs["vendor libraries"]
	vendorlibs --> layers
```

Read the diagram from the top. The instruction sets are a decision made once and handed to everything. The warnings and the precompiled header are applied per target. The vendor code never meets the first-party warning flags, and the next section shows why that matters.

## The contract

A person who changes the engine can rely on four facts and must follow five rules. Every first-party target is compiled with the warning policy. Every layer library is compiled with the same instruction sets. With precompiled headers on, the standard library, the vendor headers and a handful of Core headers are ready before the first line of a source file. And the build with precompiled headers off must work too.

:::rule
CI always builds with warnings as errors, and a warning is never silenced at the place where it appears. A silencing hides the same mistake from every later reader and every other compiler. Fix the code, or silence a whole vendor library in the vendor build file, as [the third-party page](third-party.md) shows.
:::

:::rule
Never put an engine, editor or test header that changes into a precompiled header. One edit of it rebuilds all objects of the target, which costs a full build. `Architecture.PrecompiledHeaders` refuses it.
:::

:::rule
Include what you use, although the precompiled header already has it. `CompatLint` and the cached builds of CI compile without the precompiled header, so a missing include that the header hides breaks only there.
:::

:::rule
Keep headers light. Forward-declare a type you only name, include `<nlohmann/json_fwd.hpp>` where :term[JSON]{id=json} is only declared, and name no `std::span` of a declared-only JSON type. `Architecture.HeaderWeight` checks it.
:::

:::rule
A compiler cache needs the Ninja or `Makefile` generators and embedded debug information, and it does not cache the precompiled headers of MSVC. A large integration goes through a `ci/<name>` branch, so that CI's older compilers see it before `main` does.
:::

Each rule comes with its reason, and the sections that follow show the code behind each one.

## A toy: one flag, two answers

Before the engine's code, look at the claim that a flag can change a number. The claim sounds odd, since the compiler only translates. The toy makes it concrete.

:::question
Is the C++ below new to you? It uses `if`, loops, functions and `struct` from [programming basics, part 1](../basics/programming-1.md) and [part 2](../basics/programming-2.md), a class call such as `std::printf(` from [part 3](../basics/programming-3.md), and a `const char*` from [memory in C++](../basics/cpp-memory.md).
:::

An **instruction set extension** is a group of :term[machine instructions]{id=machine-instruction} that a processor family added after the first of its kind. Examples are the Streaming single instruction, multiple data (:term[SIMD]{id=simd}) Extensions (SSE), and the Advanced Vector Extensions 2 (AVX2). A compiler may use the instructions of an extension only when you allow it with a flag, because a processor without the extension stops at the first such instruction.

One extension adds a fused multiply-add (FMA): a single instruction that computes `a * b + c` and rounds once, at the end. Without it, the machine multiplies, rounds, adds and rounds again.

The next program computes the same three expressions both ways: with a product that is rounded before the addition, and with `std::fma`, the library function that always rounds once. It prints each result with nine digits and its raw bits. Look at the third case as well, because it is a check that the idea is right.

```cpp sketch="engineering-flags-portability-toy.cpp"
// Two ways to compute a * b + c in float: rounded twice (multiply, then add), and fused (rounded once).
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

static std::uint32_t Bits(float value)
{
	std::uint32_t bits = 0;
	std::memcpy(&bits, &value, sizeof(bits));
	return bits;
}

// The volatile product is stored and read back, so the compiler cannot fuse it with the addition.
static float Separate(float a, float b, float c)
{
	volatile float product = a * b;
	return product + c;
}

static void Show(float a, float b, float c)
{
	const float separate = Separate(a, b, c);
	const float fused = std::fma(a, b, c);
	std::printf("%g * %g + %g\n", a, b, c);
	std::printf("  two roundings: %.9g (bits %08x)\n", separate, static_cast<unsigned>(Bits(separate)));
	std::printf("  one rounding:  %.9g (bits %08x)\n", fused, static_cast<unsigned>(Bits(fused)));
	std::printf("  same bits: %s\n", Bits(separate) == Bits(fused) ? "yes" : "no");
}

int main()
{
	Show(1.1f, 1.5f, 0.1f);
	Show(3.3f, 1.1f, -3.63f);
	Show(1.5f, 2.0f, 0.25f);
	return 0;
}
```

```text output-of="engineering-flags-portability-toy.cpp"
1.1 * 1.5 + 0.1
  two roundings: 1.75000012 (bits 3fe00001)
  one rounding:  1.75 (bits 3fe00000)
  same bits: no
3.3 * 1.1 + -3.63
  two roundings: 0 (bits 00000000)
  one rounding:  -8.82148754e-08 (bits b3bd70a4)
  same bits: no
1.5 * 2 + 0.25
  two roundings: 3.25 (bits 40500000)
  one rounding:  3.25 (bits 40500000)
  same bits: yes
```

1. **Line 10:** `memcpy` copies the float's bits into an :term[integer]{id=integer}, so that the program compares exact bit patterns and not rounded text.
2. **Line 17:** the `volatile` variable forces the product to be stored, and so rounded, before the addition. A compiler may not fuse across it.
3. **Line 24:** `std::fma` rounds once, as the fused instruction does.
4. **Lines 33–35:** three cases: one where the results differ in the last bit, one where they differ by a lot, and one where they agree.

The first case computes $1.1 \times 1.5 + 0.1$. The exact answer is 1.75, but 1.1 is not exact in binary: the float nearest to it is slightly too big. The two-rounding version rounds the product, adds 0.1, and lands one step above 1.75. The one-rounding version keeps the small excess of the product inside the instruction, and lands on 1.75. The results differ in the last bit.

The second case shows the extreme: the exact sum nearly cancels, the rounding of the product hides what is left, and one result is 0 while the other is about $-8.8 \times 10^{-8}$. The third case uses exact values, so no rounding happens and both ways agree.

Neither answer is wrong. They are two correct roundings of the same exact value, and a program can be written for either. The trouble starts when two builds of one program disagree, and nobody chose it.

:::example
Take a ball whose speed gains $1.1 \times 1.5 + 0.1$ each step, in a float. A build for Linux compiled with `-mfma` may use the fused instruction, and gets 1.75. A build without the flag multiplies and adds, and gets 1.75000012. After one step the difference is $1.2 \times 10^{-7}$, about one part in ten million.

A simulation amplifies such differences over thousands of steps, for example in a stack of boxes that can fall either way. The two builds may end in different places, and neither has a bug: they run different arithmetic. Two players, a replay, or a test that compares a saved result with a new one all see it.
:::

The compiler's choice to replace a multiply followed by an add with one fused instruction is **FMA contraction**. It is allowed only where the flags let the compiler use FMA, and `-mfma` is what allows the instruction at all.

The goal that FMA contraction can break is **determinism (cross-platform)**: the same program with the same input gives bit-identical results on every platform it runs on.

## The real code: warnings and definitions

Back in the engine, `strata_configure_target` is the function every first-party target calls. Read the quote for three things: the definitions that name the configuration, the MSVC switches, and what the two branches do with warnings.

```cmake src="CMake/StrataCompilerOptions.cmake#L95-L120"
# strata_configure_target(<target>)
#   Applies the Strata language standard, configuration defines, and warning policy to <target>.
function(strata_configure_target target)
	target_compile_features(${target} PUBLIC cxx_std_20)

	target_compile_definitions(${target} PRIVATE
		"$<$<CONFIG:Debug>:ST_DEBUG>"
		"$<$<CONFIG:Release>:ST_RELEASE>"
		"$<$<CONFIG:Dist>:ST_DIST>")

	if(MSVC)
		target_compile_options(${target} PRIVATE
			/W4 /permissive- /utf-8 /Zc:__cplusplus /Zc:preprocessor /Zc:inline /bigobj
			$<$<BOOL:${STRATA_WARNINGS_AS_ERRORS}>:/WX>)
		if(CMAKE_GENERATOR MATCHES "Visual Studio")
			target_compile_options(${target} PRIVATE /MP)
		endif()
		target_compile_definitions(${target} PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN _CRT_SECURE_NO_WARNINGS)
	else()
		target_compile_options(${target} PRIVATE
			-Wall -Wextra -Wno-missing-field-initializers
			$<$<BOOL:${STRATA_WARNINGS_AS_ERRORS}>:-Werror>)
	endif()

	set_target_properties(${target} PROPERTIES FOLDER "Strata")
endfunction()
```

1. **Line 100:** the three configuration definitions, written as :term[generator expressions]{id=generator-expression}.
2. **Lines 106–108:** the MSVC warning switches, with `/WX` only when the option is on.
3. **Lines 109–111:** `/MP`, which compiles several files in parallel, only for the Visual Studio generators; Ninja already runs compiles in parallel.
4. **Line 112:** the three Windows definitions, `_CRT_SECURE_NO_WARNINGS` among them.
5. **Lines 114–116:** the GCC and Clang policy, with `-Werror` under the same option.

The configuration definitions come first. `ST_DEBUG`, `ST_RELEASE` and `ST_DIST` are set with :term[generator expressions]{id=generator-expression} of the form `$<$<CONFIG:Debug>:ST_DEBUG>`. CMake evaluates them when it writes the build file of each configuration, not when it configures. That is why one :term[configure step]{id=configure-step} serves all three configurations of a multi-configuration generator such as Visual Studio or Ninja Multi-Config.

On MSVC (Microsoft Visual C++), the switches have a reason each. `/W4` is the strict warning level, and `/permissive-` makes the compiler follow the standard where it once accepted more. `/utf-8` reads source files as :term[UTF-8]{id=utf-8}, which the code style requires. `/Zc:__cplusplus` makes the `__cplusplus` :term[macro]{id=macro} report the real language version, and `/Zc:preprocessor` selects the standard-conforming :term[preprocessor]{id=preprocessor}, so that macros expand as on GCC and Clang.

`/bigobj` allows an :term[object file]{id=object-file} with more sections than the old limit, which large template-heavy sources need. The two definitions `NOMINMAX` and `WIN32_LEAN_AND_MEAN` keep the Windows headers from defining macros called `min` and `max`, and from pulling in the rarely used parts of the Windows interface.

The third definition, `_CRT_SECURE_NO_WARNINGS`, is a silencing set against the rule above, so it needs its reason. MSVC marks many standard C functions, such as `strcpy` and `fopen`, as obsolete and suggests `_s` variants, which exist only on Windows. Code that must also build on Linux and macOS cannot call functions the other platforms lack. The definition stands for the whole project, set once beside the policy. It silences a warning that is wrong for a portable project, not one that points at a mistake.

On GCC and Clang the policy is `-Wall -Wextra`. One warning is disabled, `-Wno-missing-field-initializers`, because the engine fills aggregates with the fields it needs and leaves the rest at their defaults. `STRATA_WARNINGS_AS_ERRORS`, which is on by default, adds `/WX` or `-Werror`. The same option also puts `-warnings-as-errors all` on every Slang :term[shader]{id=shader} compile in `CMake/StrataShaders.cmake`, so one switch covers the C++ and the shaders. A person may disable it for a local experiment, and CI never does.

### Vendor code and one exception

Third-party code is another matter. It is not ours to fix, and it would fail a strict policy. `Strata/vendor/CMakeLists.txt` strips every `/W` level from the MSVC flags and adds `/W0`, or adds `-w` on the other compilers, before any vendor library is declared.

The same file takes the vendor headers in as a **SYSTEM include**: an include folder that the compiler treats as a folder of system headers, so that it reports no warnings from inside those files. A strict first-party file that includes a vendor header therefore never trips on the vendor's style.

One silencing remains, in `StrataTests/CMakeLists.txt`. GCC before version 14.4 reports false `-Warray-bounds` and `-Wstringop-overflow` errors in the tests' :term[Dist]{id=dist} build, in five test files, where `libstdc++` copies :term[bytes]{id=byte} into a string. GCC 14.2, the compiler of the release job on Ubuntu 24.04, shows both, and GCC 14.4 compiles the same commands clean.

So the tests, and only the tests, add `-Wno-array-bounds -Wno-stringop-overflow` when the compiler is GCC older than 14.4. The comment beside the line says why the warnings are wrong. The engine keeps both on every compiler, so the rule survives: the silencing has a reason, a scope and an end.

## The real code: instruction sets

The engine compiles every object for the same instruction sets, and the function that chooses them is `strata_engine_cpu_options`. Its options are older than box3d. Before version 0.5.0 the former physics library chose the sets, and the defaults kept what the engine had then, so the generated code did not change when physics moved to box3d.

```cmake src="CMake/StrataCompilerOptions.cmake#L44-L93"
function(strata_engine_cpu_options outVariable)
	set(options "")
	if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
		if(CMAKE_VS_PLATFORM_NAME STREQUAL "x86" OR CMAKE_VS_PLATFORM_NAME STREQUAL "x64")
			if(STRATA_USE_AVX512)
				list(APPEND options /arch:AVX512)
			elseif(STRATA_USE_AVX2)
				list(APPEND options /arch:AVX2)
			elseif(STRATA_USE_AVX)
				list(APPEND options /arch:AVX)
			endif()
		endif()
	elseif(XCODE OR STRATA_CROSS_COMPILE_ARM OR CMAKE_OSX_ARCHITECTURES MATCHES "arm64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
		# Nothing: Xcode builds several architectures at once, and ARM64 needs no options.
	elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64|x86|i386)$")
		if(STRATA_USE_AVX512)
			list(APPEND options -mavx512f -mavx512vl -mavx512dq -mavx2 -mbmi -mpopcnt -mlzcnt -mf16c)
		elseif(STRATA_USE_AVX2)
			list(APPEND options -mavx2 -mbmi -mpopcnt -mlzcnt -mf16c)
		elseif(STRATA_USE_AVX)
			list(APPEND options -mavx -mpopcnt)
		elseif(STRATA_USE_SSE4_2)
			list(APPEND options -msse4.2 -mpopcnt)
		elseif(STRATA_USE_SSE4_1)
			list(APPEND options -msse4.1)
		else()
			list(APPEND options -msse2)
		endif()
		if(STRATA_USE_LZCNT)
			list(APPEND options -mlzcnt)
		endif()
		if(STRATA_USE_TZCNT)
			list(APPEND options -mbmi)
		endif()
		if(STRATA_USE_F16C)
			list(APPEND options -mf16c)
		endif()
		if(STRATA_USE_FMADD AND NOT STRATA_CROSS_PLATFORM_DETERMINISTIC)
			list(APPEND options -mfma)
		endif()
		if(NOT MSVC)
			list(APPEND options -mfpmath=sse)
		endif()
	endif()
	if(NOT CMAKE_SYSTEM_NAME STREQUAL "Windows")
		list(APPEND options -pthread)
	endif()
	list(REMOVE_DUPLICATES options)
	set(${outVariable} "${options}" PARENT_SCOPE)
endfunction()
```

1. **Lines 47–55:** MSVC gets an `/arch` option only when a Visual Studio generator names the platform.
2. **Lines 56–57:** Xcode, `ARM64` and cross builds get nothing.
3. **Lines 61–62:** the default branch, AVX2, with the bit-manipulation and half-float flags.
4. **Lines 81–83:** `-mfma` joins only when fused multiply-adds are on and cross-platform determinism is off.
5. **Line 91:** repeated flags are dropped before the list goes to the caller.

Take the branches in order. For MSVC the function adds `/arch:AVX512`, `/arch:AVX2` or `/arch:AVX` only when the Visual Studio generator names an `x86` or `x64` platform. Under Ninja, `cl` receives no `/arch` option at all, because the generator does not name the architecture and the engine does not guess. For Xcode, `ARM64` and cross builds for `ARM64`, the function adds nothing, since the compiler already targets the features it needs.

For x86-64 GCC and Clang, the default `STRATA_USE_AVX2` yields `-mavx2 -mbmi -mpopcnt -mlzcnt -mf16c`. The `LZCNT`, `TZCNT` and `F16C` options add flags that repeat some of these, and `list(REMOVE_DUPLICATES ...)` at the end drops the repeats. `-mfma` follows when `STRATA_USE_FMADD` is on and `STRATA_CROSS_PLATFORM_DETERMINISTIC` is off. `-mfpmath=sse` makes floating-point math of single values use SSE registers on every platform alike, and `-pthread` is added everywhere but Windows.

Where do the flags go? `Strata/CMakeLists.txt` calls the function once and puts the result on an `INTERFACE` target, `StrataEngineCodegen`. `CMake/StrataLayers.cmake` links that target `PRIVATE` to every compiled layer library. A build without the physics module compiles the same code for every other module, because the flags do not hang on a module that may be absent. Leaving a module out changes no other object.

The default, then, is `-mfma` on, and `STRATA_CROSS_PLATFORM_DETERMINISTIC` off. Turn the second on, and the engine's own code is compiled without `-mfma`, so the flag brings no fused instructions. Even so, of the engine's code only box3d, the physics library, gives results that match across platforms. [The third-party page](third-party.md) shows how `Strata/vendor/CMakeLists.txt` builds box3d with its own `-ffp-contract=off`, which forbids the contraction on GCC and Clang whatever the engine's flags say. The rest of the engine does not promise matching bits across platforms, with the option off or on.

### Three traps in the same flags

The first trap is the Windows generator. `cl` under Ninja gets no `/arch:AVX2`, as the quote shows. The zstd library, whose own `/arch:AVX2` follows the same test, loses it too. The `windows-ninja` jobs of CI, and every cached Windows build, since a compiler cache needs Ninja, compile other engine code than the `windows-vs2022` release and the `windows` preset that the perf budgets were measured with. A perf test that passes on a Ninja build tells you little about the release.

The second trap is the processor. The Windows and Linux release archives compile every engine object for AVX2: MSVC with `/arch:AVX2`, GCC with `-mavx2 -mbmi -mpopcnt -mlzcnt -mf16c -mfma`. The macOS archive is for `ARM64` and takes none of these. So the editor, the :term[runtime]{id=runtime} and every exported game need a processor with AVX2.

The third trap follows from the second: nothing checks for AVX2 at startup. The only processor check in the engine's sources, in `Strata/src/Strata/Core/Hash.cpp`, is a test for the SSE 4.2 instruction that computes `CRC32`. A processor without AVX2 stops at an illegal instruction, with no message. The exercises ask you to trace these flags to one compile line.

## The real code: compile time

The warning policy costs time, and so does everything else the compiler does. Two ideas remove most of the repeated work. The first is to read the common headers once.

A **precompiled header** is a header that the build reads once per target and keeps in a compiled form. The compiler loads that form at the start of every source file of the target instead of reading the text again. Strata makes one per layer library from `Strata/src/stpch.h`, one for the editor from `StrataEditor/src/EditorPch.h`, and one for the tests from `StrataTests/src/TestsPch.h`.

```cmake src="CMake/StrataCompilerOptions.cmake#L122-L130"
# strata_precompile_headers(<target> <header>...)
#   Gives <target> a precompiled header made of <header>s (paths, or <system> headers) when STRATA_PRECOMPILED_HEADERS is
#   on. It is force-included into every source of the target. Sources still include what they use: the lint and builds
#   with the option off compile without it.
function(strata_precompile_headers target)
	if(STRATA_PRECOMPILED_HEADERS)
		target_precompile_headers(${target} PRIVATE ${ARGN})
	endif()
endfunction()
```

The function does nothing when `STRATA_PRECOMPILED_HEADERS` is off. When it is on, CMake's `target_precompile_headers` force-includes the header into every source of the target. Each layer library builds its own copy, since vendor definitions differ between layers and one library cannot share another's. In a Debug build the objects of the editor and of the tests need about 40 % less :term[compile time]{id=compile-time} with the precompiled headers.

What may go in one? `stpch.h` holds the standard library, a few vendor headers (EnTT and `nlohmann::json` among them) and the Core basics: `PlatformDetection.h`, `Base.h`, `Log.h`, `Assert.h` and `Profiling.h`. All of them change rarely or never. The reason is the cost of a change: when a precompiled header changes, every object of the target rebuilds. A test refuses any other include; the section on tests names it.

The second idea is lighter headers. A **forward declaration** tells the compiler that a type exists, without its definition: `class SceneRecovery;`. A header that uses a type only through a reference, a pointer or a :term[smart pointer]{id=smart-pointer} needs nothing more. The editor's `EditorContext.h` is included by about a hundred editor and test objects. It declares the journal, the external editor, the exports, the thumbnails and the scene recovery instead of including them.

:::example
Count what one edit costs. Before the change, `EditorContext.h` included `SceneRecovery.h`, so an edit of `SceneRecovery.h` rebuilt every object that includes `EditorContext.h`: about 100. After the change, the header only declares `SceneRecovery`, so the same edit rebuilds the 8 objects that use the class. At one second an object on one core, that is 100 s against 8 s.

The change has one rule. A type held by value needs a complete type for its :term[destructor]{id=destructor}, so the header holds it through `Scope<>` and puts the destructor in the `.cpp` file, where the complete type is available.
:::

JSON is the heavy case. The header `nlohmann/json.hpp` is large, and every file that includes it reads all of it. A header that only mentions JSON in a declaration includes `<nlohmann/json_fwd.hpp>`, and the sources that read or build values include the full header.

`Architecture.HeaderWeight` keeps a list of the headers that need the complete type, each with a reason, such as a JSON member or a default argument. It fails any other header that includes the complete one. Its second rule has a history, told at the end: a header that only declares JSON may not name a `std::span` of it.

### Caches, and what is not used

The third tool is the cache. A **compiler cache** is a program, `ccache` or `sccache`, that keeps the finished object of every compile. It keys each object by the full command and the input text, and returns the stored object when the same compile comes again.

The cache plugs in as a **compiler launcher**: a program that CMake puts in front of every compiler call. `STRATA_COMPILER_CACHE` sets `CMAKE_C_COMPILER_LAUNCHER` and `CMAKE_CXX_COMPILER_LAUNCHER`, so every C and C++ compile goes through it, the vendor libraries' too.

Three consequences are written into the code. The Visual Studio generators ignore launchers, so the configure step stops with an error that names the `windows-ninja` preset. A debug information file that every compile of a target shares, a program database (PDB), cannot be cached. So with the cache on, MSVC's debug information goes into each object as `/Z7`, and the :term[linker]{id=linker} gathers it.

The caches also do not cache MSVC's precompiled header builds, so the cache switches `STRATA_PRECOMPILED_HEADERS` off by default. You may still switch it on. The cache and the precompiled header trade one saving for the other, and CI chose the cache.

The numbers support the choice. After the work on compile time in wave 4, a clean Debug build on a macOS machine took 13 % less time of the central processing unit (CPU), 1,036 seconds against 1,194. An edit of `Scene/Components.h` took 28 % less. Warm CI builds took 2 to 6 minutes instead of 13 to 22.

## The real code: portability

Portability means the same source builds and behaves the same on MSVC, GCC and Clang, with the standard libraries `libstdc++` and `libc++`. Strata states minimums: MSVC 19.40, GCC 13, Clang 17 and Apple Clang 15. CI builds with a different set: GCC 14 on Linux, and on macOS the Apple Clang 17 of the `macos-15` image. No job builds with GCC 13, though it is the default `g++` of Ubuntu 24.04, and no job builds with Apple Clang 15, which GitHub retired with its `macos-14` image. The supported minimum and the tested compiler are not the same thing.

Three examples show what "works on my machine" hides. A missing include passes where a precompiled header supplies it and fails where none does. The types `size_t` and `std::uint64_t` are different on macOS, so code that treats them as one can build on Linux and fail there. And Apple Clang 15's `libc++` has no floating-point `std::from_chars`, so code that reads a float that way builds elsewhere and breaks there. A newer local compiler, the one you have installed, is no guide to CI's older ones.

`Tools/CompatLint.py` is the answer. It needs a configured and built Ninja Multi-Config tree of the `linux` or `macos` preset, because it reads the Debug commands from `build-Debug.ninja`. It also needs GCC 14 and LLVM 16 with its own `libc++`, which stand in for CI's Linux compiler and for Apple Clang 15. The defaults are Homebrew's paths, and `--build`, `--gcc`, `--clang` and `--libcxx` name others.

For each file it compiles twice, once per compiler, with `-fsyntax-only`, so that no object is written. The heart of it is `adapt`. The tool is a Python program, so a word on reading it: a function starts with `def`, a block is the lines pushed in under a colon, and `index += 2` adds to a variable. Loops and `if` work as in C++ without braces, and `arg in ('-MD', '-c')` asks whether a value is in a list.

```python src="Tools/CompatLint.py#L64-L92"
def adapt(command, compiler, options):
    args = shlex.split(command)
    out = []
    index = 1
    while index < len(args):
        arg = args[index]
        if arg in ('-MD', '-c', '-Winvalid-pch') or arg.startswith('-mmacosx-version-min'):
            index += 1
        elif arg in ('-MT', '-MF', '-o', '-arch'):
            index += 2
        elif arg == '-Xclang' and index + 1 < len(args) and args[index + 1] == '-include-pch':
            index += 4
        elif arg == '-Xclang' and index + 1 < len(args) and args[index + 1] == '-include':
            # CMake's forced include of the precompiled header's wrapper (Clang): dropped, as in a build configured with
            # -DSTRATA_PRECOMPILED_HEADERS=OFF, so that a missing include the precompiled header hides fails here.
            index += 4
        elif arg == '-include' and index + 1 < len(args) and re.search(r'(^|[/\\])cmake_pch[^/\\]*$', args[index + 1]):
            # The same wrapper in GCC's form (a Linux build tree).
            index += 2
        else:
            out.append(arg)
            index += 1
    if compiler == 'clang':
        prefix = [options.clang, '-nostdinc++', '-isystem', options.libcxx]
        if sys.platform == 'darwin':
            sdk = run(['xcrun', '--show-sdk-path']).stdout.strip()
            prefix += ['-isysroot', sdk, '-mmacosx-version-min=14.0']
        return prefix + out + ['-fsyntax-only']
    return [options.gcc] + out + ['-fsyntax-only']
```

1. **Line 70:** flags that name the output, the dependency file and the macOS version are dropped; they fit the build's own compiler.
2. **Lines 74–79:** the file that CMake includes first, which holds the precompiled header, is dropped in Clang's form with its option.
3. **Lines 80–82:** the same file in GCC's form, found by its `cmake_pch` name.
4. **Lines 86–92:** the compiler is swapped, the `libc++` of LLVM 16 is named for Clang, and `-fsyntax-only` is appended.

The function walks the build's compile command argument by argument. It drops flags that name outputs and dependency files, the macOS version flag, and both forms of the first-included file that holds the precompiled header, one for Clang and one for GCC. It then puts the other compiler first and appends `-fsyntax-only`. The result is the command of a build configured with `-DSTRATA_PRECOMPILED_HEADERS=OFF`, so a file that leans on the precompiled header's includes fails here, as it would fail in a cached CI build.

The :term[exit code]{id=exit-code} tells the result. 0 means every file compiled without errors or warnings, 1 means at least one failed, and 2 means a usage error: a compiler that is missing, or a build it cannot read. A changed header affects every file that includes it, so pass those files, or pass `--all`. The tool compiles `.cpp` files and not headers. It reads a Ninja build of the `linux` or `macos` preset, so it runs on those two systems only.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Unity builds | Many large C++ code bases, and CMake's `UNITY_BUILD` property | Less repeated reading of headers, with fewer and larger compile units | A change to one file compiles its whole group again; names from different files can collide; a missing include hides behind another file's |
| Warnings as a list for review, not errors | Projects with old code or many vendors | No broken build when a compiler adds a warning | Warnings that nobody reads; a build with hundreds of them hides the new one |
| Fast flags such as `-mfma` as a switch at run time | Programs that choose a code path by a processor check | One build that runs on old and new processors | A check at startup, two code paths to test, and results that depend on the processor |
| Always `-ffp-contract=off` | Projects that need matching results on every platform | The same arithmetic everywhere, one less trap | The speed of fused instructions in every engine loop |
| A precompiled header holding all engine headers | Small projects | The fewest headers read per file | An edit of any header rebuilds every object |

## How it is tested

Two suites guard the headers, and both live in `StrataTests/src/Architecture/`. `Architecture.PrecompiledHeaders`, in `PrecompiledHeaderTests.cpp`, reads each precompiled header. It fails on any include that is not the standard library, a vendor header, `stpch.h` or one of the five Core basics. Its test `A precompiled header holding an engine header that is not a Core basic is refused` feeds it a bad header and checks the refusal, and its second test checks the real headers.

`Architecture.HeaderWeight`, in `HeaderWeightTests.cpp`, checks three things. Engine and editor headers include the complete JSON header only when they are on its list. Headers that only declare JSON name no `std::span` of it. `EditorContext.h` and the project and settings headers keep the heavy includes out.

The warning policy has no suite of its own: the build is the test, and CI always builds with warnings as errors. The builds and the perf tests check the instruction sets, and the perf budgets assume the `windows` preset. A person runs `Tools/CompatLint.py` by hand, before a push. CTest runs them in the `StrataTests.Core.Core` shard; to run only these two, start the test program with the doctest filter: `build/windows/bin/Debug/StrataTests.exe --test-suite=Architecture.*`.

## Changing it safely

To add a flag for every first-party target, put it in `strata_configure_target`, and give the reason in a comment. To change what every engine object may assume of the processor, change `strata_engine_cpu_options`, and read the trap about `windows-ninja` first. To add a header to a precompiled header, ask whether it changes: if it does, omit it. Add a library's headers to `stpch.h` only when the engine uses the library almost everywhere.

The rules of `AGENTS.md` that apply are the five above, and each has its reason. Fix a warning where it is found, keep a changing header out of the precompiled header, and write an include even where it is supplied. Keep headers light, with JSON forward-declared. A change to the :term[layer table]{id=layer-table} or the headers should pass `Architecture.PrecompiledHeaders`, `Architecture.HeaderWeight` and `Architecture.Layering`.

Before the push, run `Tools/CompatLint.py --changed-since main`. For a wave's worth of changes, push to `ci/<name>` and wait for green CI.

## What went wrong before

Two breaks gave the rules their weight. In the first, Apple Clang 17 turned `std::abs(x) > 0 ? x : 0` into wrong machine code at `-O2` and above on arm64. It took the chosen value for one that is never negative, and dropped a later `std::abs` of it. As a result any gamepad axis pushed to its negative side read 0 in `InputActions`. The engine's fix compares the candidates among themselves, and not against a running value that starts at 0.

A compiler is code with bugs too, and a second or older compiler is a second opinion.

In the second, `RendererQuality::OptionModel` returned a `std::span` of a JSON type that its header only declared. Apple Clang 15's `libc++` builds the span's :term[iterator]{id=iterator} functions in every file that includes the header, and they need the complete type. So CI's macOS build broke while the other platforms passed. The fix was to hold a pointer, or return a reference to the container, instead. `Architecture.HeaderWeight` now checks the engine's and the editor's headers for a `std::span` of declared-only JSON.

## Summary

- A warning fails the build because CI builds with `STRATA_WARNINGS_AS_ERRORS`, and the fix is in the code or the vendor build file, never at the line where the warning appears.
- A flag such as `-mfma` lets the compiler fuse a multiply and an add into one rounding, which can change the last bit of a result. `STRATA_CROSS_PLATFORM_DETERMINISTIC` removes it from the engine's own code, and box3d keeps its own `-ffp-contract=off`.
- A precompiled header holds the standard library, vendor headers and the Core basics only, because all objects of its target rebuild when it changes. Sources still include what they use.
- `Tools/CompatLint.py` compiles changed files with GCC 14 and LLVM 16 without the precompiled header, and it cannot check MSVC, Windows code or the real Apple Clang.

## Check yourself

1. A teammate's change adds `#pragma warning(disable: 4996)` above one call of `fopen` in a shared source file. The reviewer says no. What is the reason, and what does the project do for this warning?

   :::answer{tests="warnings-policy"}
   Warning 4996 is the one that calls `fopen` unsafe. A silencing at the call hides the problem for every later reader and for the other compilers, and it grows into a code base full of local exceptions. The project already silences this warning once, for all of it, with `_CRT_SECURE_NO_WARNINGS` in `strata_configure_target`, and gives the reason there: the `_s` functions that MSVC prefers do not exist on Linux and macOS.
   :::

2. The same program computes `a * b + c` on a Linux build with `-mfma` and on a build without it. Which is right? (a) The first gives the same bits; (b) the two may differ in the last bit, and neither is wrong; (c) the second is a bug; (d) both agree, since the language fixes the rounding.

   :::answer{tests="fma-flags"}
   Option (b) is right. With the flag the compiler may fuse the operation and round once, and without it the machine rounds twice, so both are correct roundings of the exact value. Option (a) is wrong because the bits differ. Option (c) is wrong because two roundings are what the language asks for. Option (d) is wrong because the language lets the compiler contract.
   :::

3. Which of these may go into `stpch.h`? (a) `<vector>`. (b) `Strata/src/Strata/Scene/Components.h`. (c) `<nlohmann/json.hpp>`. (d) `Strata/src/Strata/Core/Log.h`.

   :::answer{tests="pch-contents"}
   (a), (c) and (d). A standard header, a vendor header and a Core basic change rarely or never. (b) is a header that changes often, and an edit would rebuild every object of the target, so `Architecture.PrecompiledHeaders` refuses it.
   :::

4. A source file uses `std::vector` and compiles on your machine, but includes no `<vector>`. It compiles in your local `windows` build and fails in `CompatLint`. Why, and what is the fix?

   :::answer{tests="compatlint"}
   The precompiled header holds `<vector>`, and the `windows` preset builds with it, so the file compiles. `CompatLint` drops the precompiled header, as CI's cached builds do, and the missing include appears; CI would fail too. The fix is to add `#include <vector>` to the file.
   :::

## Exercises

1. **Basic.** Time a clean Debug build twice: once with the default `STRATA_PRECOMPILED_HEADERS=ON` and once with `-DSTRATA_PRECOMPILED_HEADERS=OFF`, each in its own build folder. Compare the two times and say which part of the page your numbers match.

   :::answer[Worked solution]{tests="pch-contents"}
   Configure `cmake --preset windows -B build/pch-on`, then `cmake --preset windows -B build/pch-off -DSTRATA_PRECOMPILED_HEADERS=OFF`, build each with `cmake --build <dir> --config Debug --parallel`, and note the wall time. Expect the build with headers to take less time, and about 40 % less for the editor's and the tests' objects. The exact numbers depend on the machine, so write down the processor and the core count. To see the cache, configure `windows-ninja` with `-DSTRATA_COMPILER_CACHE=ON` in a developer prompt, build, delete the build folder, configure and build again, and compare. The second clean build takes far less time, because the cache returns stored objects.
   :::

2. **Medium.** Run `CompatLint` on a change that leans on the precompiled header. On Linux or macOS, with a configured and built `linux` or `macos` tree and GCC 14 and LLVM 16, remove one standard include from a source and run the tool. Name the exit code and say what the message shows.

   :::answer[Worked solution]{tests="compatlint"}
   Remove `#include <vector>` from a file that uses `std::vector` and has it only through `stpch.h`. Run `python3 Tools/CompatLint.py --changed-since main`. Both compilers report the unknown name, and the tool prints the failures, ends with its count of files and failed compilations, and exits with code 1. Without the compilers, or without a build, it prints a message and exits 2. Windows has no such tree, so the exercise is for Linux and macOS only.
   :::

3. **Hard.** Trace it yourself: follow the instruction sets by a search, from the `STRATA_USE_*` options to one engine object's compile line. Say why the line holds `-mfma` on Linux x64, `/arch:AVX2` in a Visual Studio build, and neither under `windows-ninja` or on `ARM64`.

   :::answer[Worked solution]{tests="fma-flags"}
   Search for `STRATA_USE_AVX2`: it is an option in `CMake/StrataCompilerOptions.cmake`, read in `strata_engine_cpu_options`. `Strata/CMakeLists.txt` calls the function and puts the result on `StrataEngineCodegen`, and `CMake/StrataLayers.cmake` links that target `PRIVATE` to every compiled layer library, so the flags reach each object. On Linux x64 the compiler is GCC, the system processor matches `x86_64`, and `STRATA_USE_FMADD` is on with `STRATA_CROSS_PLATFORM_DETERMINISTIC` off, so `-mfma` is added.

   With a Visual Studio generator, `CMAKE_VS_PLATFORM_NAME` is `x64`, so `/arch:AVX2` is added. Under `windows-ninja` the platform name is empty, so the MSVC branch adds nothing. On `ARM64` the `aarch64` branch adds nothing. To see it, build with `cmake --build <dir> -- -v` on Ninja and read one compile line.
   :::

## Where it lives in Strata

- `CMake/StrataCompilerOptions.cmake`: the compiler cache, the `STRATA_USE_*` options, `strata_engine_cpu_options`, `strata_configure_target`, `strata_precompile_headers`.
- `Strata/CMakeLists.txt` and `CMake/StrataLayers.cmake`: `StrataEngineCodegen`, and the layer libraries that link it and the precompiled header.
- `CMakeLists.txt` and `CMake/StrataConfigurations.cmake`: `STRATA_WARNINGS_AS_ERRORS`, `STRATA_PRECOMPILED_HEADERS`, `STRATA_COMPILER_CACHE`, and the `/Z7` switch.
- `Strata/vendor/CMakeLists.txt`: vendor warnings off, `SYSTEM` includes, box3d's `-ffp-contract=off`.
- `Strata/src/stpch.h`, `StrataEditor/src/EditorPch.h`, `StrataTests/src/TestsPch.h`: the precompiled headers.
- `StrataTests/src/Architecture/PrecompiledHeaderTests.cpp` and `HeaderWeightTests.cpp`: the two suites.
- `Tools/CompatLint.py`: the check against older compilers.

## Further reading

- cmake.org, the documentation of `target_precompile_headers` and of `CMAKE_<LANG>_COMPILER_LAUNCHER`: what the build system does with the two features (intermediate).
- learn.microsoft.com, the documentation of the MSVC compiler options `/W4`, `/permissive-` and `/arch`: what each switch does (intermediate).
- gafferongames.com, "Floating Point Determinism": why the same code can give different results on different machines and compilers (intermediate).
- The ccache manual: how a compiler cache keys a compile and what it cannot cache (beginner).

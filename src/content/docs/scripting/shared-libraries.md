---
id: scripting/shared-libraries
title: "Shared libraries and binary interfaces"
description: "How a program loads code built separately, why C++ types cannot cross that boundary, and how Strata's script modules stay safe."
kind: concept
size: L
tracks: [E]
needs: [basics/build, basics/cpp-classes, scripting/why-scripts]
time: 60
learn:
  - id: loading
    text: explain how a program loads a shared library and finds a function in it
  - id: abi-limits
    text: explain why C++ has no stable binary interface and what an ABI covers
  - id: approaches
    text: compare the approaches to a binary interface by their costs
  - id: versioning
    text: write a struct that a newer and an older program can both read
  - id: module-build
    text: name what a Strata script module exports and how its build keeps the rest private
since: 0.6.0
status: final
---

Open a project that has the `Spinner` script, press **Ctrl+B**, and look in the project's `.strata/Scripts/Bin` folder. A file appears there, a `.dll` on Windows, a `.so` on Linux or a `.dylib` on macOS. The editor was started hours ago, yet while it runs it loads that file and calls the `Spinner`'s code from inside its own process.

Two questions follow. What is that file, if it is not a program you start? And how do two pieces of code, built at different times, perhaps by different :term[compilers]{id=compiler}, call each other without either one having seen the other's source? The answers explain a rule that shapes every script you write: only plain C data crosses the line between the engine and a script.

## Passing a C++ class across fails in quiet ways

The obvious plan is to let the engine and the module share C++ types. The engine would hand the module a `std::string` for an entity's name, and the module would hand back a `std::vector` of results. Both sides include the same header, so both agree on what the type is. Right?

The two sides agree on the source, and the compiler turns source into :term[bytes]{id=byte} by rules the header does not hold. Suppose the engine was built with one compiler release and the module with another. The two :term[standard libraries]{id=standard-library} may store a string as a pointer, a size and a capacity in a different order, or may keep a small string inside the object. The module reads the engine's bytes under the wrong layout and gets a name made of garbage, or crashes.

The failure is quiet because nothing checks it. The :term[linker]{id=linker} never sees the other file, and the loader only matches names. So a disagreement appears at run time, in a function far from the cause, perhaps only in Release builds. A careful design needs a precise name for what the two files must agree on, and a short list of things that safely agree.

## A shared library is code loaded while the program runs

A :term[shared library]{id=shared-library} is a file of compiled code that a running program can load into its own memory; Windows calls it a dynamic-link library (DLL), Linux a `.so` file, macOS a `.dylib`. You met static linking in [how a C++ program is built](../basics/build.md): the linker copies the code into the program before it starts. A shared library delays that step. The program, or the :term[operating system's]{id=operating-system} loader for it, maps the file into the process while it runs.

Loading gives the program a handle, a number that names the loaded library. The functions inside are reached by name. A library lists the names it offers as its exported symbols: a symbol is a name tied to an address in the file, and the export list is the part other files may find. The rest stays private.

The two calls that matter are short. On Windows, `LoadLibrary` loads a file and `GetProcAddress` takes a handle and a name and returns the address of that function, or null. On Linux and macOS the pair is `dlopen` and `dlsym`. In `Strata/src/Strata/Core/DynamicLibrary.h` the class `DynamicLibrary` wraps both pairs, and its `GetFunction` casts the address to the function type you ask for.

The cast is the dangerous part. The loader returns an address and knows nothing of the function's parameters. If you cast to a type with other parameters than the function has, the call compiles and runs, and the stack or registers hold the wrong values. Matching the signature is a promise you make by hand.

### What happens at load time

Loading does more than copy bytes. Three things deserve attention.

First, the loader finds the library's own dependencies, the other libraries its code calls, and loads them too. Where it looks is a security matter as well as a convenience. On Windows the classic search tries the program's folder and the system folders, but also the :term[current folder]{id=current-folder} and the folders on the `PATH` variable, so a planted file with the right name can win. Given an :term[absolute path]{id=absolute-path}, Strata's loader on Windows asks for the library's own folder, an extra folder the caller names, the :term[executable's]{id=executable} folder and the system folders, and never the current folder or `PATH`. That is the call `LoadLibraryExW` with the flags `LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR` and `LOAD_LIBRARY_SEARCH_DEFAULT_DIRS`, in `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp`.

Second, on Linux the dependency search follows a list stored in the file. The **RUNPATH** (run-time search path) is that list, a set of folders recorded in the library when it was built, and the token `$ORIGIN` in it stands for the folder that holds the library itself. A library whose search path is `$ORIGIN` finds its neighbours next to it, wherever the folder is moved. The loader then also reads :term[environment variables]{id=environment-variable} such as `LD_LIBRARY_PATH` and the system folders, as the comment in `Strata/src/Strata/Core/DynamicLibrary.h` says.

Third, static :term[constructors]{id=constructor} run. A global variable of a class type, such as `const AbortContainment s_AbortContainment;`, has a :term[constructor]{id=constructor}, and the language runs it before the program's `main` or, for a library, when the library loads. Such a constructor is code that runs inside the loader's call, before your own function has a chance to guard anything. The entry file of the software development kit (SDK) uses this on Windows: its static constructor installs a handler for `abort()` in the module's own C runtime as soon as the file loads. A crash in a static constructor is a crash in `LoadLibrary`, so treat these constructors as code that can fail.

### Loading twice returns the same library

Ask the loader for a file that is already loaded and it does not load it again. It returns the same handle and adds one to a reference count, a number kept per library; each unload takes one away, and the file leaves memory only at zero. Everyone who loaded the file shares the library's global variables, because there is one copy.

That sharing matters for hot reload. If you build a new version of a module and ask for the same path, the loader may hand back the old code. `DynamicLibrary.h` states the rule in its comment on `GetNativeHandle`, and Strata's module loader can load from a private copy of the file for this reason. How it does so is the topic of [Loading and calling a module](../scripting/loading.md).

### Names can collide across libraries

When two loaded libraries each define a function with the same name, which one does a call reach? On Linux the loader resolves a name by searching its loaded libraries in order, and the first match wins; macOS by default binds each name to the library it was linked against. The effect is **interposition**: one library's symbol replacing another library's symbol of the same name. It is a tool for debugging :term[allocators]{id=allocator}, and a hazard when it happens by accident, because a module's helper named `Clamp` could silently replace the engine's.

The defence is symbol visibility. Compilers can mark each function as visible outside its library or hidden. With hidden visibility the name never enters the export list, so no other library can reach it, and no lookup can confuse it with another. Strata's build hides everything and exports two functions on purpose, as the later sections show.

A second fact about `dlopen` shows in `Strata/src/Platform/Posix/PosixDynamicLibrary.cpp`: it passes `RTLD_NOW | RTLD_LOCAL`. `RTLD_NOW` resolves every undefined name at load, so a missing one fails at once and not at the first call. `RTLD_LOCAL` keeps the new library's symbols out of the global list that later libraries search.

## An API is a source contract; an ABI is a binary one

An application programming interface (API) says what a program may write: which functions, with which parameter types. If two programs are compiled together from the same headers, the API is enough. A separately built library needs more: the compiled bytes must agree. The **application binary interface** (ABI) is that agreement, the contract about the machine-level form of code and data between separately compiled pieces.

The contract has many clauses, and C++ leaves each to the compiler.

- **Calling convention.** Which registers or stack slots carry the arguments, who removes them, and where the result goes.
- **Struct layout and padding.** The order of members, and the gaps the compiler inserts so that each member sits at a multiple of its size.
- **Name mangling.** C++ allows overloads, so the compiler encodes parameter types into the symbol.
- **The exception model.** How a thrown exception travels up the stack, and how code finds its handler.
- **Allocators and the C runtime.** Where `new` and `malloc` get memory, and which free function takes it back.
- **The standard library's layouts.** What bytes a `std::string` or `std::vector` holds.
- **Build configuration.** A Debug build changes the layout of standard types.

:::example[How padding changes a size]
Take three members: a one-byte flag, a four-byte count and a one-byte mode. A four-byte count must start at a multiple of four, so a compiler that keeps the written order puts the flag at byte 0 and skips three bytes. The count sits at byte 4 and the mode at byte 8. Three more bytes at the end keep the count aligned in an array of these :term[structs]{id=struct}.

The size is 12 bytes. Written with the count first, the same three members take 4 + 1 + 1 = 6 bytes and two bytes of end padding, 8 in all.

The sketch prints both sizes and a few types whose sizes depend on the platform. A reader who expects a number from the declaration alone gets it wrong, and a library built with the other order disagrees with its caller about where every member sits.

```cpp sketch="scripting-shared-libraries-layout.cpp"
#include <cstddef>
#include <cstdint>
#include <cstdio>

struct Loose
{
	uint8_t Flag;
	uint32_t Count;
	uint8_t Mode;
};

struct Tight
{
	uint32_t Count;
	uint8_t Flag;
	uint8_t Mode;
};

int main()
{
	std::printf("Loose: size %zu, Count at %zu, Mode at %zu\n", sizeof(Loose), offsetof(Loose, Count), offsetof(Loose, Mode));
	std::printf("Tight: size %zu, Flag at %zu, Mode at %zu\n", sizeof(Tight), offsetof(Tight, Flag), offsetof(Tight, Mode));
	std::printf("bool %zu, long %zu, wchar_t %zu, pointer %zu\n", sizeof(bool), sizeof(long), sizeof(wchar_t), sizeof(void*));
	return 0;
}
```

1. **Lines 5–10:** the flag comes first, so three bytes of padding sit before the count.
2. **Lines 12–17:** the count comes first, so the two small members share the space after it.
3. **Line 23:** the sizes of `bool`, `long`, `wchar_t` and a pointer, which depend on the platform.

The sketch prints this on each platform:

::::tabs{sync=os}
:::tab[Windows]

```text output-of="scripting-shared-libraries-layout.cpp" platform="windows"
Loose: size 12, Count at 4, Mode at 8
Tight: size 8, Flag at 4, Mode at 5
bool 1, long 4, wchar_t 2, pointer 8
```

`long` is 4 bytes and `wchar_t` is 2.
:::
:::tab[Linux]

```text output-of="scripting-shared-libraries-layout.cpp" platform="linux"
Loose: size 12, Count at 4, Mode at 8
Tight: size 8, Flag at 4, Mode at 5
bool 1, long 8, wchar_t 4, pointer 8
```

`long` is 8 bytes and `wchar_t` is 4.
:::
:::tab[macOS]

```text output-of="scripting-shared-libraries-layout.cpp" platform="macos"
Loose: size 12, Count at 4, Mode at 8
Tight: size 8, Flag at 4, Mode at 5
bool 1, long 8, wchar_t 4, pointer 8
```

`long` is 8 bytes and `wchar_t` is 4, as on Linux.
:::
::::

On every platform the first two lines match the hand count, and only the last line differs.

A struct with a `long` that crosses a boundary between a Windows file and a Linux file is a rare case. A struct built with another compiler on the same platform fails for the same reason, because the layout is a decision of the compiler, not of the header.
:::

Names give a second concrete case. The method `Spinner::OnUpdate(float)` becomes `_ZN7Spinner8OnUpdateEf` with GCC and Clang, and `?OnUpdate@Spinner@@QEAAXM@Z` with Microsoft's compiler. A lookup by name finds one and never the other.

The exception model fails the same way. An exception thrown in a module with one model, and caught in an engine with another, has no agreed route up the stack. Most often the process ends.

Allocators and the C runtime form a third trap. The **C runtime** (CRT) is the library that implements the C standard functions, `malloc` and `free` among them, and is linked into each binary, shared (`/MD` on Microsoft's compiler) or statically (`/MT`). Two files that each link their own copy of the CRT own two separate heaps. Memory allocated in one and freed in the other goes to the wrong heap manager, which corrupts it.

Debug against Release is the last clause. Microsoft's standard library adds checks in Debug builds, controlled by the :term[macro]{id=macro} `_ITERATOR_DEBUG_LEVEL`, and those checks change the size and members of containers and :term[iterators]{id=iterator}. A `std::vector` from a Debug file passed to a Release file is a different type with the same name. So C++ has no stable ABI: the layout of its types depends on the compiler, its version, its standard library and its options. C has a small, fixed set of types and one calling convention per platform, so engines expose C at the boundary.

## Engines solve the problem in four ways

The first answer is to make the C++ interface stable by hand. :term[Vtable]{id=virtual-table} interfaces hold only :term[pure virtual functions]{id=pure-virtual-function}: the object's first word points to a table of :term[function pointers]{id=function-pointer} (a :term[vtable]{id=virtual-table}), and the table's order is the contract. Microsoft's component model is the best-known case, used by DirectX. It crosses compilers, because a vtable of plain pointers is simple, and it has a rule for versions: an interface never changes, and a new version is a new interface. The costs are a reference-counting protocol that every object follows and repeated code for every type.

A flaw of that model is the burden of its machinery for a small boundary. A lighter answer is the C function table: a struct whose members are function pointers, filled by one side and given to the other. Vulkan works this way: its loader hands out pointers to functions by name, and a program keeps them in its own table. The table has no objects and no reference counting, only functions, and it grows by adding members.

The lightest answer is flat C exports: the library exports plain functions with C names and the caller looks each up by name. Python's C interface is of this kind. Each function needs its own lookup, so a boundary of a hundred functions has a hundred lookups, but a function table has one.

The last answer removes the human from the loop. A generated binding takes a description in an interface language, a file that lists types and functions in a neutral notation, and writes the code on both sides. Microsoft's interface definition language and protocol buffers work like that. The generator keeps both sides in step, at the price of a build step, a language to learn and generated code to read when something fails.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Vtable interfaces | Reference counting and repeated code on every object | Crosses compilers; rules for versions | High | DirectX, Windows shell |
| C function tables | One struct of pointers; one lookup | Plain; grows by appending | Low | Vulkan, Strata |
| Flat C exports | One lookup per function | Plain, no shared state | Lowest | Python extensions |
| Generated bindings | A generator and its notation | Many languages from one source | Medium to high | Microsoft interface tools, protocol buffers |

## One struct must change without breaking old files

A boundary lives as long as its files, and files are built on different days. An engine of 0.6.0 meets a module built on 0.7.0, or the reverse. Backward compatibility means a newer program still works with files built against an older interface. Forward compatibility means an older program works with files from a newer one. A design that gives both lets people update the engine and the game separately.

The change that most often happens is a new member in a struct. If you insert it in the middle, every old reader finds its members shifted. The first rule, called **append-only**, is that members are added only at the end of a struct and an existing member never moves, changes type or changes meaning. An old reader still finds its own members at their offsets, and a new reader knows more.

A reader must still learn whether the struct it received is the short or the long one. The Win32 interface gives the pattern its best-known form: the first member of a struct, `cbSize`, holds the struct's size in bytes, and the caller sets it before the call. Strata's name for the same member is `StructSize`.

Each side compares the size with where a member ends and reads the member only if the size covers it. That is feature detection by size. A global version number cannot do this per struct, so Strata keeps one for incompatible changes only.

One more case needs care: an :term[array of structs]{id=array-of-structs}. When the elements are stored side by side, the stride between them is the struct's size, so growing the struct moves every element after the first. An array whose elements are filled by one side and read by the other must therefore hold fixed-size structs, frozen for good, or hold pointers to the structs, so that each element can grow alone.

:::example[An old engine meets a new module, and the reverse]
Strata's `StrataScriptModuleAPI` describes a module to the engine. On a 64-bit machine its members end at byte 48: `StructSize` and `ABIVersion` take 4 bytes each, the module's name 16, `ClassCount` and `Padding` 4 each, `Classes` 8 and `Unload` 8. Suppose a later version appends a member at byte 48, and the struct then holds 56 bytes. The ABI header describes this rule; the new member is an invented case.

An old engine passes a struct with `StructSize` 48. A new module writes at most 48 bytes, so it never writes past the engine's struct, and reports its own size, 56. The engine sees 56 but knows only 48, so it reads no new member.

A new engine passes `StructSize` 56 with the new member zeroed. An old module writes 48 bytes and reports 48. The engine compares: 48 does not cover the member at byte 48, so the member is not read and its zero is never mistaken for a value.

```mermaid caption="An old engine and a new module, then a new engine and an old module: each side reads a member only when both sizes cover it, so the overlap is all that is read." alt="Two rows of bars. In the first, an old engine's bar of 48 bytes meets a new module's bar of 56 bytes, and the shared first 48 bytes are read. In the second, a new engine's bar of 56 bytes meets an old module's bar of 48 bytes, and again the first 48 bytes are read."
flowchart LR
    subgraph A["Old engine, new module"]
        direction TB
        A1["Engine: capacity 48"] --> A2["Module knows 56, writes 48, reports 56"] --> A3["Both read bytes 0 to 47"]
    end
    subgraph B["New engine, old module"]
        direction TB
        B1["Engine: capacity 56, rest zero"] --> B2["Module knows 48, writes 48, reports 48"] --> B3["Both read bytes 0 to 47"]
    end
```

A struct the engine fills works the same way in the other direction. `StrataScriptGraphicsOptionInfo` starts with `StructSize`, which the module sets to the size it passes; the engine fills at most that many bytes and writes back the number it filled.
:::

The diagram shows the rule's shape: each side acts on the smaller of the two sizes. The exercises let you run the rule yourself.

## Strata exports two functions and passes plain data

Strata applies all of this in the smallest form that works. A script module exports exactly two C functions, `StrataScript_GetABIVersion` and `StrataScript_Load`. The engine looks both up with `GetFunction`. It calls the first and compares the number with its own `ST_SCRIPT_ABI_VERSION`, which is 1 at the pin. When they differ, the engine refuses the module with a message that names both versions.

Then it calls `StrataScript_Load`, passing a table of host functions and a struct for the module to fill. The table is how the script calls the engine; the module's reply describes its script classes.

These two functions are the module's **entry point**, the exported function by which the loader reaches a library's code. They are defined in the SDK's entry file, which the build adds to every module, in the lines below.

```cpp src="StrataScriptCore/Source/ScriptModuleEntry.cpp#L73-L81"
ST_SCRIPT_EXTERN_C ST_SCRIPT_EXPORT uint32_t StrataScript_GetABIVersion(void)
{
	return ST_SCRIPT_ABI_VERSION;
}

ST_SCRIPT_EXTERN_C ST_SCRIPT_EXPORT uint32_t StrataScript_Load(const StrataScriptHostAPI* host, uint32_t hostABIVersion, StrataScriptModuleAPI* outModule)
{
	return Strata::Detail::LoadModule(host, hostABIVersion, outModule, ST_SCRIPT_MODULE_NAME);
}
```

Each function is declared `extern "C"`, so its name keeps its plain C form and every compiler writes it the same way. Each is also marked for export by `ST_SCRIPT_EXPORT`, which is `__declspec(dllexport)` on Windows and default visibility elsewhere. The first returns the version number. The second hands the work to the SDK; the next pages show how it fills the description.

Everything that crosses is plain data.

A string is a pointer and a size, in UTF-8, with no terminating zero. An entity or asset is a 64-bit number. A quaternion is four floats in the order x, y, z, w. A struct holds fixed-size :term[integers]{id=integer}, and enums are stored as `uint32_t`, so no enum of a width the compiler chooses sits in a struct. A call into the module returns a `StrataScriptResult`: a module never lets an exception escape, but reports the message through a host function and returns a code.

Versioning follows the rules above. The one number `ST_SCRIPT_ABI_VERSION` changes only for an incompatible change: a changed signature, struct layout or meaning, or a removed or moved member.

Anything else is appended, to the end of the host table or a descriptor, and keeps the number. The 0.7.0 release added seven host functions and kept version 1. Modules built for 0.6.0 load on 0.7.0 unchanged. A module that uses the new functions still runs on 0.6.0, where the calls do nothing.

:::why[Why a table of function pointers, and not vtable interfaces or generated code?]
A script needs a long list of services, and each one is a plain function. Vtable interfaces would give each service an object and a reference count that scripts never need. Generated bindings would add a generator to a project whose users build their game with :term[CMake]{id=cmake} and a compiler. A struct of pointers needs neither, appends cleanly, and lets the engine give each scene its own context.

The cost is care: a mistake in the order of the table is a crash, not an error. [The ABI and SDK page](../scripting/abi-sdk.md) tours the header and the SDK that wrap it.
:::

:::rule[Only plain C data crosses the ABI]
The engine's guide states the rule in one line: no standard library types, no engine types and no exceptions cross the boundary. Every clause of the list above is the reason: layouts, exceptions and allocators differ between builds, and a module may be built by another compiler. The next page, [the ABI and SDK page](../scripting/abi-sdk.md), tours the header.
:::

### How a module is built

The engine's build file `StrataScriptCore/CMakeLists.txt` defines `StrataScriptCore` as an `INTERFACE` library: it has no compiled code, only the header folder, the math library and the C++20 requirement, and a module that links it receives those.

```cmake src="StrataScriptCore/CMakeLists.txt#L5-L12"
add_library(StrataScriptCore INTERFACE)
target_include_directories(StrataScriptCore INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/Include")
target_link_libraries(StrataScriptCore INTERFACE glm)
target_compile_features(StrataScriptCore INTERFACE cxx_std_20)

# strata_add_script_module(): builds game scripts into a module (also used by game projects through the package in
# CMake/StrataScriptCoreConfig.cmake).
include("${CMAKE_CURRENT_SOURCE_DIR}/CMake/StrataScriptModule.cmake")
```

The function `strata_add_script_module` turns a folder of sources into a module. Its first half is this excerpt from `StrataScriptCore/CMake/StrataScriptModule.cmake`.

```cmake src="StrataScriptCore/CMake/StrataScriptModule.cmake#L85-L105"
# The module entry points (StrataScript_GetABIVersion, StrataScript_Load) come from the SDK.
if(NOT ARG_NO_SDK_ENTRY)
	list(APPEND sources "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../Source/ScriptModuleEntry.cpp")
endif()
add_library(${target} MODULE ${sources})
target_link_libraries(${target} PRIVATE StrataScriptCore)
target_compile_features(${target} PRIVATE cxx_std_20)
target_compile_definitions(${target} PRIVATE "ST_SCRIPT_MODULE_NAME=\"${outputName}\"")

# Only the entry points are exported; everything else stays private to the module, so modules never interpose on
# each other's (or the engine's) symbols.
set_target_properties(${target} PROPERTIES
	PREFIX ""
	SUFFIX "${suffix}"
	OUTPUT_NAME "${outputName}"
	CXX_EXTENSIONS OFF
	CXX_VISIBILITY_PRESET hidden
	VISIBILITY_INLINES_HIDDEN ON
	POSITION_INDEPENDENT_CODE ON
	MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
	FOLDER "Scripts")
```

1. **Lines 85–88:** the SDK's entry file joins the sources, unless the project sets `NO_SDK_ENTRY` to write the two functions itself.
2. **Line 89:** `MODULE` is CMake's kind of library that is loaded at run time and never linked against, the right kind for a plug-in.
3. **Lines 94–95:** the comment states the visibility goal: only the entry points are exported.
4. **Lines 101–102:** `CXX_VISIBILITY_PRESET hidden` hides every function by default, and `VISIBILITY_INLINES_HIDDEN` hides inline ones. The two entry functions are the exceptions, through `ST_SCRIPT_EXPORT`.
5. **Line 104:** the C runtime is linked statically (`MultiThreaded`, with `Debug` added in Debug builds), so the module owns its own :term[runtime]{id=runtime} and cannot disagree with the engine's about a heap.

The second half sets compiler and linker options per platform.

```cmake src="StrataScriptCore/CMake/StrataScriptModule.cmake#L110-L137"
if(MSVC)
	target_compile_options(${target} PRIVATE /utf-8 /permissive- /Zc:__cplusplus /Zc:preprocessor)
	# A program database in every configuration, so that the editor names the file and line of a crash (it reads the
	# PDB with DbgHelp). /DEBUG would turn off the linker's optimizations, which are turned back on. Compiles through a
	# compiler cache (a compiler launcher: ccache, sccache) keep the debug information in the objects (/Z7), since a cache
	# cannot cache compiles that write into one shared program database; the linker writes the same PDB from them.
	get_target_property(launcher ${target} CXX_COMPILER_LAUNCHER)
	if(launcher)
		set_target_properties(${target} PROPERTIES MSVC_DEBUG_INFORMATION_FORMAT "Embedded")
	else()
		set_target_properties(${target} PROPERTIES MSVC_DEBUG_INFORMATION_FORMAT "ProgramDatabase")
	endif()
	target_link_options(${target} PRIVATE "/DEBUG" "$<$<NOT:$<CONFIG:Debug>>:/OPT:REF;/OPT:ICF>")
else()
	# Debug information in every configuration, as MSVC's program database: script builds take the editor's configuration,
	# so a released editor builds Release (Dist takes Release's flags), and a breakpoint in a script binds only where the
	# module has it. It stays in the module (ELF) or, on macOS, in the objects the module's debug map names.
	target_compile_options(${target} PRIVATE -g)
	if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
		# GCC otherwise emits STB_GNU_UNIQUE symbols for inline statics, which makes dlclose() a no-op and would
		# keep every hot-reloaded module version in memory.
		target_compile_options(${target} PRIVATE -fno-gnu-unique)
	endif()
	if(NOT APPLE)
		# Scripts must not depend on symbols of the process that loads them (macOS bundles fail on them by default).
		target_link_options(${target} PRIVATE "LINKER:--no-undefined")
	endif()
endif()
```

1. **Lines 112–122:** a program database (PDB), the file with names and line numbers of compiled code, is written in every configuration, so the editor can name the file and line of a crash. The `/OPT` options, which remove unused code, are switched back on outside Debug.
2. **Lines 124–127:** with GCC and Clang, `-g` keeps debug information in every configuration, as the program database does with MSVC. A debugging tool can then stop at a line of a script in a Release module too.
3. **Lines 128–132:** with GCC, `-fno-gnu-unique` stops the compiler from marking inline statics as unique across libraries; such a mark makes `dlclose` do nothing, and every reloaded version of a module would stay in memory.
4. **Lines 133–136:** `--no-undefined` on Linux makes the linker fail if the module uses a symbol it does not define, because a script must not depend on the process that loads it.

## What this choice cannot do

A module cannot share a C++ type with the engine. It cannot receive a `std::string` and cannot throw to the engine, and a script that needs a list of names asks for them through a function that copies into its own buffer. The SDK hides much of this behind classes of its own, built from the same plain pieces.

A module cannot be called from another thread. The ABI header says everything is single-threaded: the engine calls the module on its :term[main thread]{id=main-thread}, and the module calls the host only inside those calls. Only the two diagnostic functions, `Log` and `ReportException`, accept a call from any thread. The price is that a script cannot start its own work on a worker thread and call the rest of the engine from there. What Strata chooses not to offer, and why, is collected in [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **A `std::string` or a glm type passed across.** Symptom: a wrong name, or a crash in the other file. Fix: pass a pointer and a size, and floats in plain arrays.
- **Memory freed on the other side.** Symptom: a crash in `free`, or silent heap damage, when each file links its own runtime. Fix: free where you allocated, or copy into a buffer the caller provides.
- **An exception that crosses.** Symptom: the process ends at the boundary. Fix: catch inside the module and return a result code.
- **Assuming the size of `bool`, an enum or `long`.** Symptom: members read at the wrong offsets on another compiler. Fix: fixed-width integers, with enums stored as `uint32_t`.
- **Unloading that does not unload.** Symptom: the old code stays in memory after a hot reload, as when a compiler marks statics as unique. Fix: the flags of the build above, and no dependence on `dlclose` freeing anything.
- **Dependencies found through `PATH` or the current folder.** Symptom: the wrong library loads on one machine. Fix: load with :term[absolute paths]{id=absolute-path} and a named dependency folder, as `DynamicLibrary` does.
- **Static constructors forgotten as code that can crash.** Symptom: the load fails with no message from your code. Fix: keep globals plain, and start work in a function the engine calls.

## Summary

- A program loads a shared library with `LoadLibrary` or `dlopen`, finds a function by name with `GetProcAddress` or `dlsym`, and shares the one copy of a library that is already loaded, through a reference count.
- An ABI is the binary contract for layouts, calling conventions, names, exceptions, allocators and library types; C++ leaves all of it to the compiler, so engines expose C.
- Vtable interfaces, C function tables, flat C exports and generated bindings trade repeated code, lookups and tooling against each other.
- A struct that grows is append-only and starts with its size, and each side reads a member only when both sizes cover it.
- A Strata module exports `StrataScript_GetABIVersion` and `StrataScript_Load`, and its build hides every other symbol.

## Check yourself

1. A function defined in a module's code is declared in the engine as taking `(int, float)`, but the module defines `(float, int)`. The engine finds it with `GetProcAddress`. What happens?

   - A. The linker reports the error.
   - B. The load fails with a message.
   - C. The call runs with wrong values.
   - D. The compiler converts the arguments.

   :::answer{tests="loading"}
   C. The loader returns an address and checks no signature, so the engine's call puts values where the module does not expect them. A is wrong because the linker never sees the module, B because the lookup succeeds, and D because the compiler of the engine knows only its own declaration.
   :::

2. Why is passing a `std::string` between an engine and a module a bug, even when both include the same header?

   :::answer{tests="abi-limits"}
   The header fixes the source, not the bytes. The layout of a string depends on the compiler, the standard library's version and the :term[build configuration]{id=build-configuration}, and the two files can also use different heaps. A Debug build adds checks that change the layout further.
   :::

3. A struct has a one-byte flag, then a four-byte integer, then a two-byte integer, in that order. What size does a compiler that pads to the size of each member give it?

   :::answer{tests="abi-limits"}
   The flag takes byte 0. The four-byte integer needs a multiple of four, so it starts at byte 4 and ends at byte 8. The two-byte integer starts at 8 and ends at 10. The whole struct is rounded up to a multiple of its largest alignment, four, so the size is 12 bytes.
   :::

4. Which approach to a binary interface needs a build step that writes code on both sides, and what does it buy?

   :::answer{tests="approaches"}
   Generated bindings. The generator reads a description in an interface language and writes both sides, so the two cannot drift apart, and one description can serve many languages. The price is the generator, its notation and the generated code you read when something fails.
   :::

5. A new engine with a 56-byte struct meets a module built when the struct was 48 bytes. Which bytes does each side read, and why is the new member's zero harmless?

   :::answer{tests="versioning"}
   Both read bytes 0 to 47. The module writes 48 bytes and reports 48, and the engine sees that this size does not cover the member at byte 48, so it never reads it.
   :::

6. Name two things the build of a Strata module does to avoid trouble with the engine, and the trouble each avoids.

   :::answer{tests="module-build"}
   Hidden visibility keeps every function but the two entry points away from the export list, so a module cannot replace the engine's or another module's symbols. The static C runtime gives the module its own runtime, so memory handling cannot disagree with the engine's.
   :::

## Exercises

1. **Basic.** List the exported symbols of the `Spinner`'s module and find the two Strata functions among them. On Windows run `dumpbin /exports` on the `.dll` in `.strata/Scripts/Bin`; on Linux run `nm -D --defined-only` on the `.so`. Explain why the `Spinner` class itself is not in the list.

   :::answer[Worked solution]{tests="loading,module-build"}
   Run the command in the folder `.strata/Scripts/Bin` of the project, on the module file. The list holds `StrataScript_GetABIVersion` and `StrataScript_Load`, the two functions of `StrataScriptCore/Source/ScriptModuleEntry.cpp` that carry `ST_SCRIPT_EXPORT`; the platform's tool may add a few of its own entries. The `Spinner` is missing because the build sets `CXX_VISIBILITY_PRESET hidden` (line 101 of `StrataScriptModule.cmake`), so only a function marked for export reaches the list. The engine finds the class through the description that `StrataScript_Load` fills, not through a symbol.
   :::

2. **Medium.** A struct has a size and an `Id`, 8 bytes in all. Design version 2 that adds a `Flags` member, say what each of an old module and a new engine reads of it, and the reverse, and write a function that fills the caller's struct safely.

   :::answer[Worked solution]{tests="versioning" solution="sketches/scripting-shared-libraries-sizeprefix.cpp"}
   Append `Flags` after `Id`, so the struct grows from 8 to 12 bytes and `Id` stays at byte 4. The filler reads the caller's `StructSize`, writes the smaller of that and the bytes it knows, and reports what it wrote. The sketch runs both directions: an old module of 8 bytes against a new engine, and a new module of 12 bytes against an old engine.

   ```cpp sketch="scripting-shared-libraries-sizeprefix.cpp"
   #include <cstddef>
   #include <cstdint>
   #include <cstdio>
   #include <cstring>

   struct InfoV1
   {
   	uint32_t StructSize;
   	uint32_t Id;
   };

   struct InfoV2
   {
   	uint32_t StructSize;
   	uint32_t Id;
   	uint32_t Flags;
   };

   // Fills the caller's struct: at most as many bytes as the caller's StructSize allows and the filler knows.
   void Fill(void* out, const void* known, uint32_t knownSize)
   {
   	uint32_t capacity = 0;
   	std::memcpy(&capacity, out, sizeof(capacity));
   	const uint32_t written = capacity < knownSize ? capacity : knownSize;
   	std::memcpy(out, known, written);
   	std::memcpy(out, &written, sizeof(written));
   }

   int main()
   {
   	const InfoV2 newEngine = { sizeof(InfoV2), 7, 99 };
   	InfoV1 oldModule = { sizeof(InfoV1), 0 };
   	Fill(&oldModule, &newEngine, sizeof(InfoV2));
   	std::printf("old module: size %u, Id %u\n", oldModule.StructSize, oldModule.Id);

   	const InfoV1 oldEngine = { sizeof(InfoV1), 7 };
   	InfoV2 newModule = { sizeof(InfoV2), 0, 0 };
   	Fill(&newModule, &oldEngine, sizeof(InfoV1));
   	const bool hasFlags = newModule.StructSize >= offsetof(InfoV2, Flags) + sizeof(newModule.Flags);
   	std::printf("new module: size %u, Id %u, Flags readable: %s\n", newModule.StructSize, newModule.Id, hasFlags ? "yes" : "no");
   	return 0;
   }
   ```

   ```text output-of="scripting-shared-libraries-sizeprefix.cpp"
   old module: size 8, Id 7
   new module: size 8, Id 7, Flags readable: no
   ```

   1. **Lines 22–24:** the filler reads the caller's capacity and takes the smaller of it and its own size.
   2. **Lines 25–26:** it copies that many bytes and writes the count back as the new `StructSize`.
   3. **Line 39:** the new module reads `Flags` only when its reported size covers the member.

   In the first call the old module offers 8 bytes and the engine knows 12, so 8 are written and `Id` is 7. In the second call the new module offers 12 and the old engine knows 8, so 8 are written and the size field becomes 8. `Flags` stays 0, and the check compares 8 with `offsetof(InfoV2, Flags) + 4`, which is 12, so the member cannot be read. A version 3 that appends `Mode` works the same way: both sides read only the bytes both sizes cover.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/DynamicLibrary.h`: the `DynamicLibrary` class, with `Load`, `GetSymbol` and `GetFunction`. Its platform parts are `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp` and `Strata/src/Platform/Posix/PosixDynamicLibrary.cpp`.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the C header of the ABI, with `ST_SCRIPT_ABI_VERSION`, `ST_SCRIPT_EXPORT`, `ST_SCRIPT_HAS_MEMBER` and the tables.
- `StrataScriptCore/Source/ScriptModuleEntry.cpp`: the two entry functions every SDK module exports.
- `StrataScriptCore/CMakeLists.txt` and `StrataScriptCore/CMake/StrataScriptModule.cmake`: the `StrataScriptCore` target and `strata_add_script_module`.
- `Strata/src/Strata/Scripting/ScriptModule.cpp`: where the engine finds the two functions and compares the version numbers.
- The editor command `script.build` builds the project's module into `.strata/Scripts/Bin`.

## Further reading

- The documentation of the Windows functions `LoadLibraryExW` and `GetProcAddress` (Microsoft): the exact search order and flags; intermediate.
- The manual pages `dlopen(3)` and `ld.so(8)` of Linux: the lookup rules, `RTLD_NOW`, `RTLD_LOCAL`, RUNPATH and `$ORIGIN`; intermediate.
- Ulrich Drepper, "How To Write Shared Libraries": symbol visibility, interposition and load costs on Linux; advanced.
- The Itanium C++ ABI, a public specification: the mangling and exception rules that GCC and Clang follow; advanced.
- The Vulkan specification, chapter on the loader and dispatch: an example of function tables; intermediate.

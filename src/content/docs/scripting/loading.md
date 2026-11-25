---
id: scripting/loading
title: "Loading, calling and validating modules"
description: "How the engine opens a script module, checks what the file claims, reads its description once and calls into it through a guard."
kind: internals
size: L
tracks: [E]
needs: [scripting/abi-sdk, core/platform, core/files]
time: 115
learn:
  - id: engine-checks
    text: name the checks the engine makes before and while it calls into a script module
  - id: guarded-memory
    text: explain why the engine reads module memory only inside guarded calls
  - id: load-modes
    text: predict whether a load runs from the file or from a private copy
  - id: trace-load
    text: trace the load of the first game's module through the engine's code
since: 0.3.0
status: final
---

A game's code lives in a separate file, a :term[shared library]{id=shared-library} that the engine did not build and cannot trust. `ScriptModule` is the class that opens that file. It checks the file, reads the module's description once, and then makes every later call into the module through a guard, so that a crash in the game's code does not end the engine. `ScriptEngine` sits one level above it: it owns the single module of a game, counts its faults, and names the engine that scenes use when they start to play.

The page follows a load from the file on disk to the ready module, and then the one function through which every later call passes. It omits four topics that have their own pages. They are what the description's :term[structs]{id=struct} hold, what happens inside a call that faults, how a fault's frames get names, and how a module is replaced while scenes play.

## The problem and how engines solve it

The engine has to run code that it did not write, that may be wrong, and that the game maker rebuilds all day. You may know from [shared libraries](../scripting/shared-libraries.md) how the :term[operating system]{id=operating-system} loads such a file and finds a name in it. Loading is the simple half. The hard half is that a loaded library runs inside the engine's own process, with the same memory and rights. A bad pointer in the game's code is then a bad pointer in the engine.

Engines meet this in three ways. Some link the game's code into the engine's own program: that is fast, but every change means a new program, and a crash ends everything. Some run the game's code in a virtual machine, as many scripting languages do. A crash in a script cannot touch the engine then, at the price of a slower language and a bridge for every call.

Strata chooses a third way: native code in a shared library behind a plain C interface. The code is as fast as the engine's own, and the file can be replaced while the editor runs. The engine pays by doing the defensive work itself. It treats every number in the description as hostile until it passes a check, and it calls into the file only through a guard that turns a crash into an error value. The rest of this page is that defensive work.

## The map: who owns what

Two sets of objects exist after a load, and they live in different places. The engine's side holds what the engine made from the file. The module's side holds what the file made. A pointer from one side to the other is a promise that the other side keeps something alive, so it matters who frees what.

```mermaid caption="The engine's records on the left, the module's objects on the right. The instance handle is the only pointer that crosses to a module object, and the engine never reads what it points to." alt="A diagram with two groups. The engine group holds the script engine, the module object, a list of class records, a list of copied class functions and the script system of a playing scene with its instance handles. The module group holds the module's description, the class descriptors, the script instances and their fields. The class functions point into the module's code, and an instance handle points to a script instance."
flowchart LR
	subgraph engineSide["Engine side: freed by the engine"]
		engine["ScriptEngine"] --> module["ScriptModule"]
		module --> classes["ScriptClassInfo list"]
		module --> functions["ClassFunctions list"]
		module --> fault["ScriptFault"]
		system["ScriptSystem of a playing scene"] --> handle["instance.Handle"]
		system -.->|"instance.Class"| classes
	end
	subgraph moduleSide["Module side: freed by module code"]
		description["Module description"]
		descriptors["Class descriptors"]
		instances["Script instances"]
	end
	module -.->|"read once, guarded"| description
	description --> descriptors
	functions -.->|"function pointers"| descriptors
	handle -.->|"opaque pointer"| instances
```

The engine's records are ordinary C++ objects. `ScriptEngine` owns one `ScriptModule`. The module owns a list of `ScriptClassInfo`, one per class, each with the class name, its fields with their types and default values, and a :term[callback]{id=callback} mask: one bit for every callback the class implements. The module also owns a parallel list of `ClassFunctions`, the :term[function pointers]{id=function-pointer} it copied out of the :term[class descriptors]{id=class-descriptor}. Each playing scene's script system keeps one record per script instance, which holds a pointer to a `ScriptClassInfo` and an instance handle.

The module's objects are whatever the file's code created: the description, the class descriptors and the script instances. The instance handle is an opaque pointer to such an object, and the engine never looks behind it. It passes the handle back to the class's functions and nothing else.

The freeing rules follow from that split. The engine frees its records when it replaces or unloads the module. The module frees an instance only when the engine calls the class's `Destroy` function. When a module has crashed, no more module code runs, so its instances are never destroyed, and their memory stays allocated until the process ends. The engine accepts this leak; calling a faulted module again would be worse.

## The contract

A caller of `ScriptModule` may rely on five things, and must keep four rules. The reasons are the point of this section, because each rule closes a way for the game's code to hurt the engine.

- **A loaded module is valid.** `Load` returns a module only after every check passed, so a caller never sees a half-checked one. A failed load returns nothing and an error message.
- **A class record stays put.** The `ScriptClassInfo` list is complete when the module is ready and is not changed afterwards. Its pointers stay valid until the module is unloaded or replaced.
- **Every call has one of five results.** A call returns Ok, Exception, Rejected, Faulted or Unavailable, and never throws or crashes into the caller.
- **A faulted module stays quiet.** After a crash every call returns Unavailable, so a caller cannot call it by mistake.
- **Main thread only.** The scene, the scripts and the module share one thread.

The four rules for callers:

- **Call only through `ScriptModule`.** Loading and unloading the library are calls too, because the library's startup code runs when it loads and its :term[destructors]{id=destructor} run when it unloads.
- **Read module memory only inside a guarded call.** A guarded call is one that `CrashGuard` runs; the next sections show why the engine does this so strictly.
- **Move complete results out.** A guarded read fills engine objects, and the engine moves them to their final place only after the guard returns, so a crash never leaves a half-built record.
- **Treat the description as untrusted data.** Every count, name and type is checked before it is used.

:::rule[Every module call goes through the module class]
The engine's guide says that every call into module code goes through `ScriptModule`, which runs it under `CrashGuard`, and that module memory is read only inside guarded calls. The reason is that a fault outside a guard would end the process; see [Crash containment](../scripting/crash-containment.md) for what a guarded call returns.
:::

## A toy version

The smallest host does what the problem asked for: it opens a library, finds two names, calls the functions and closes the library. The toy below does that with the :term[C runtime]{id=crt} of the system, so that the sketch needs no file of its own. A shared library has no types: a symbol is an address, and the host must say what function type lives there. The `reinterpret_cast` lines are that statement, and they are also where a wrong guess becomes a crash.

:::question
The code below uses pointers, function types and `#include`, which the [pointers and memory page](../basics/cpp-memory.md) and the [classes and calls page](../basics/programming-3.md) teach.
:::

The sketch has three parts: three small functions that wrap the platform's calls, a check that the library opened, and a check that both names were found. Look at the two `if` statements: each failure returns an error value, and none of them asserts.

```cpp sketch="scripting-loading-toy.cpp"
// A toy host: open a shared library, look up two functions by name, call them, close the library.
// The library is the C runtime of the system, so the program needs no file of its own.
#include <cstddef>
#include <cstdio>

#if defined(_WIN32)
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace
{

	using AbsFunction = int (*)(int);
	using LengthFunction = std::size_t (*)(const char*);

#if defined(_WIN32)
	constexpr const char* c_LibraryName = "msvcrt.dll";
	void* OpenLibrary(const char* name) { return reinterpret_cast<void*>(LoadLibraryA(name)); }
	void* FindSymbol(void* library, const char* name) { return reinterpret_cast<void*>(GetProcAddress(static_cast<HMODULE>(library), name)); }
	void CloseLibrary(void* library) { FreeLibrary(static_cast<HMODULE>(library)); }
#else
#if defined(__APPLE__)
	constexpr const char* c_LibraryName = "libSystem.dylib";
#else
	constexpr const char* c_LibraryName = "libc.so.6";
#endif
	void* OpenLibrary(const char* name) { return dlopen(name, RTLD_NOW); }
	void* FindSymbol(void* library, const char* name) { return dlsym(library, name); }
	void CloseLibrary(void* library) { dlclose(library); }
#endif

}

int main()
{
	void* library = OpenLibrary(c_LibraryName);
	if (!library)
	{
		std::printf("cannot load the library\n");
		return 1;
	}

	const auto absolute = reinterpret_cast<AbsFunction>(FindSymbol(library, "abs"));
	const auto length = reinterpret_cast<LengthFunction>(FindSymbol(library, "strlen"));
	if (!absolute || !length)
	{
		std::printf("a function is missing\n");
		CloseLibrary(library);
		return 1;
	}

	std::printf("abs(-42) = %d\n", absolute(-42));
	std::printf("strlen(\"strata\") = %zu\n", length("strata"));
	CloseLibrary(library);
	return 0;
}
```

```text output-of="scripting-loading-toy.cpp"
abs(-42) = 42
strlen("strata") = 6
```

1. **Lines 15–16:** the host states the type of each function; the library does not say.
2. **Lines 18–32:** three small functions hide the difference between Windows and the other systems.
3. **Lines 38–43:** a library that does not open is an error value, never an assert.
4. **Lines 45–52:** a missing name gives a :term[null pointer]{id=null-pointer}, and the host checks both before it calls.
5. **Lines 54–56:** the calls go through the pointers, and the library closes at the end.

The toy loads a library that a person trusts. It has no guard, so a crash in `abs` would end the program. It does not check the library's version, because the C runtime has none, and it never reads a description, because the library has none.

The toy also loads the file where it stands, so on Windows a build could not replace the file while the library is open. Each of those gaps is a section of the real code.

## The real code

Strata's loader fills those gaps in a fixed order. The diagram shows it; the sections below walk it, in the order that data flows.

```mermaid caption="A load from the file check to the ready module. Every box that reads the module's memory or runs its code lies inside a guarded call." alt="A sequence diagram with four parts: the caller, the module object, the library object and the module's code. The caller asks to load, and the module object checks that the file exists, then picks the file itself or a private copy. The library object loads the library inside a guard, which runs the module's startup code. The module object finds two exports, asks for the version inside a guard and compares it with its own. It then calls the load function inside a guard, reads the description inside a guard, validates it, copies the function pointers and answers ready."
sequenceDiagram
	participant C as Caller
	participant M as ScriptModule
	participant L as DynamicLibrary
	participant X as Module code
	C->>M: Load(path, mode)
	M->>M: file check, choose file or copy
	M->>L: Load(path), guarded
	L->>X: static initializers run
	M->>L: GetFunction(two exports)
	M->>X: StrataScript_GetABIVersion, guarded
	M->>M: compare with the engine's version
	M->>X: StrataScript_Load(host table, api), guarded
	M->>X: read the description, guarded
	M->>M: validate, copy function pointers
	M-->>C: ready module, or an error message
```

### The file check and the two load modes

The first check is cheap: the path must name a regular file. A missing file is an error that the caller may try again later, because a build can still be writing it. The module's name starts as the file's name without its extension; the description may replace it.

The next decision is where the library loads from. `ScriptModuleLoadMode` has two values. `InPlace` loads the file itself; shipped games use it. `Copy` loads a **private copy**: a duplicate of the file in a folder that only the current user may change, so a build can replace the original while the module runs.

The editor uses `Copy`, because hot reload replaces the module while the game plays. On Windows a loaded library's file is locked, so a build could not replace it and a reload could never happen.

`InPlace` is only a request. If the file is already loaded in this process, or the file is an abandoned file (described below), the loader copies it anyway. The first reason matters because loading a file twice does not load it twice: the system counts references and hands out the same library, so two modules would share one set of static variables. A copy has a new name, so the system loads it as a new library.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L402-L440"
if (mode == ScriptModuleLoadMode::InPlace && !IsAbandonedFile(path))
{
	if (!module->LoadLibraryGuarded(path, {}, displayPath, error))
		return fail(std::move(error));
	if (RegisterLibrary(module->m_Library.GetNativeHandle()))
	{
		module->m_LoadedPath = path;
		loaded = true;
	}
	else
	{
		// The file is loaded already (a reload, another engine): this load only added a reference to that library,
		// whose module state is in use. Dropping the reference runs no module code; the module loads from a copy.
		module->m_Library.Unload();
	}
}

if (!loaded)
{
	// A private copy, so the build can replace the original file while the module is in use.
	module->m_CopyDirectory = ScriptModuleCopyDirectory::Acquire(error);
	if (!module->m_CopyDirectory)
		return fail(fmt::format("Cannot load script module '{}' from a private copy: {}", displayPath, error));

	const std::filesystem::path copyPath = module->m_CopyDirectory->GetPath()
		/ FileSystem::FromUTF8(fmt::format("{}-{}{}", FileSystem::ToUTF8(path.stem()), UUID().ToString(), FileSystem::ToUTF8(path.extension())));
	if (!FileSystem::Copy(path, copyPath, false))
		return fail(fmt::format("Cannot copy script module '{}' (it may still be being written)", displayPath), true);
	module->m_LoadedPath = copyPath; // From now on the destructor removes the copy

	// The libraries the module depends on stay next to the original.
	if (!module->LoadLibraryGuarded(copyPath, path.parent_path(), displayPath, error))
		return fail(std::move(error));
	if (!RegisterLibrary(module->m_Library.GetNativeHandle()))
	{
		module->m_Library.Unload();
		return fail(fmt::format("Cannot load script module '{}': its private copy resolved to a library that is already loaded", displayPath));
	}
}
```

1. **Line 402:** the in-place path runs only when the mode asks for it and the file is not abandoned.
2. **Lines 406–416:** `RegisterLibrary` fails when the library's handle is known already. The load then only added a reference, so it drops that reference, which runs no module code, and falls through to the copy path.
3. **Lines 422–430:** the copy folder is acquired, the copy gets the file's name plus a random identifier, and `FileSystem::Copy` refuses to replace a file that exists. From line 430 the module's destructor removes the copy.
4. **Lines 432–434:** the second argument, `path.parent_path()`, is the original's folder. The libraries that the module needs stay beside the original, so the loader searches there.
5. **Lines 435–439:** a copy that still lands on a registered handle is refused, because two modules must never share a library.

The folder of copies is made once per process, by `ScriptModuleCopyDirectory`. Its name is `ScriptModules-` followed by a random suffix, inside the folder that `Platform::GetUserRuntimeDirectory` returns for Strata. The process holds a `FileLock` on a file named `Owner.lock` in that folder for as long as it runs. The next sessions use the lock to tell a live folder from a dead one, because the system releases a lock when its process ends, however it ends.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L254-L287"
Ref<ScriptModuleCopyDirectory> ScriptModuleCopyDirectory::Acquire(std::string& outError)
{
	static std::mutex s_Mutex;
	static std::weak_ptr<ScriptModuleCopyDirectory> s_Current;

	std::scoped_lock<std::mutex> lock(s_Mutex);
	if (Ref<ScriptModuleCopyDirectory> current = s_Current.lock())
		return current;

	const std::filesystem::path parent = Platform::GetUserRuntimeDirectory("Strata");
	if (parent.empty())
	{
		outError = "there is no per-user runtime directory that only this user can modify";
		return nullptr;
	}
	RemoveStaleCopyDirectories(parent);

	std::filesystem::path path = Platform::CreatePrivateDirectory(parent, c_CopyDirectoryPrefix);
	if (path.empty())
	{
		outError = fmt::format("cannot create a private directory in '{}'", FileSystem::ToUTF8(parent));
		return nullptr;
	}
	Scope<FileLock> ownerLock = FileLock::Create(path / FileSystem::FromUTF8(c_OwnerLockName));
	if (!ownerLock)
	{
		FileSystem::Remove(path);
		outError = fmt::format("cannot create the owner lock of '{}'", FileSystem::ToUTF8(path));
		return nullptr;
	}
	Ref<ScriptModuleCopyDirectory> directory(new ScriptModuleCopyDirectory(std::move(path), std::move(ownerLock)));
	s_Current = directory;
	return directory;
}
```

1. **Lines 256–261:** one folder per process. A second module gets the same one, held through a weak pointer that ends with the last copy.
2. **Lines 263–269:** the parent is the user's :term[runtime]{id=runtime} folder, which is checked to be one that only this user can modify. Before the new folder is made, `RemoveStaleCopyDirectories` removes folders of dead processes.
3. **Line 271:** `CreatePrivateDirectory` makes the folder with the rights the platform contract demands, the same contract that [Files you can trust](../core/files.md) teaches.
4. **Lines 277–283:** the lock file is created already locked, so nobody ever finds the folder unlocked while its owner runs. A failure removes the folder again.

`RemoveStaleCopyDirectories` takes each `ScriptModules-*` folder in turn and tries to take its owner lock. If it gets the lock, no process owns the folder, and it removes the copies and then the lock file. If the lock cannot be taken, the owner runs and the folder stays. A folder with no lock file at all may be one that is being made right now, so it goes only when it is older than one hour. The last copy's removal removes the folder too; one that cannot be removed completely keeps its lock file, so a later session knows it is stale and tries again.

### Loading the library

`DynamicLibrary` is the Core class that owns one loaded library. It is move-only: a second owner of one handle would unload the library twice. Its `Load` takes the path and an optional dependency folder, and `GetFunction` finds a symbol and casts it to the type the caller names.

```cpp src="Strata/src/Strata/Core/DynamicLibrary.h#L31-L35"
bool Load(const std::filesystem::path& path, const std::filesystem::path& dependencyDirectory = {});
void Unload();
// Forgets the library without unloading it (it stays loaded until the process exits). For libraries that must
// not be touched again, e.g. after their unload code crashed.
void Release();
```

The comments in the :term[header]{id=header} fix four rules. First, on Windows the loader searches a library's dependencies in the library's own folder, in `dependencyDirectory`, in the :term[executable's]{id=executable} folder and in the system folders, never in the :term[current folder]{id=current-folder} or in `PATH`. A program that searched the current folder would load whatever file a user left there. Second, on Linux and macOS the module's own `RUNPATH` decides, where `$ORIGIN` or `@loader_path` names the copy's folder, followed by the loader's :term[environment variables]{id=environment-variable} and the system paths. The original's folder is not searched there.

Third, a file cut short is refused before the loader reads past its end, because on Linux that read would fault inside the loader. Fourth, loading a file that is loaded already returns the same handle.

`Release` is the odd member. It forgets the library without unloading it, so the library stays loaded until the process ends. `ScriptModule` calls it when the unload of a module crashed: touching that library again would crash again.

Some C++ objects of the module are built when the library loads, before any function of the module is called. Their :term[constructors]{id=constructor} are module code, so `LoadLibraryGuarded` loads under `CrashGuard`.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L346-L375"
bool ScriptModule::LoadLibraryGuarded(const std::filesystem::path& path, const std::filesystem::path& dependencyDirectory, const std::string& displayPath,
	std::string& outError)
{
	struct LibraryLoad
	{
		DynamicLibrary* Library;
		const std::filesystem::path* Path;
		const std::filesystem::path* DependencyDirectory;
		bool Loaded;
	};
	LibraryLoad libraryLoad { &m_Library, &path, &dependencyDirectory, false };
	CrashInfo crash;
	if (!CrashGuard::Invoke([](void* data)
	{
		LibraryLoad* load = static_cast<LibraryLoad*>(data);
		load->Loaded = load->Library->Load(*load->Path, *load->DependencyDirectory);
	}, &libraryLoad, &crash))
	{
		RecordFault(ScriptCallSite { nullptr, "static initialization" }, crash);
		AbandonLibraryFile(path, m_Name);
		outError = fmt::format("Script module '{}' crashed while loading: {}", displayPath, crash.Description);
		return false;
	}
	if (!libraryLoad.Loaded)
	{
		outError = fmt::format("Cannot load script module '{}': {}", displayPath, m_Library.GetLastError());
		return false;
	}
	return true;
}
```

1. **Lines 349–356:** `CrashGuard::Invoke` takes a plain function and one data pointer, so the call's arguments travel in a small struct.
2. **Lines 358–362:** the library's `Load` runs inside the guard; the guard returns false when the code inside crashed.
3. **Lines 364–367:** a crash here is recorded as a fault of the call site ":term[static initialization]{id=static-initialization}", the file is abandoned, and the error says so.
4. **Lines 369–373:** an ordinary failure, such as a missing dependency, is a message from the system and not a fault.

The crash in line 364 left the platform's loader in the middle of its work. Outside Windows the crash guard leaves the loader by jumping out of it, so the loader may keep a half-built library and hand it out again if the file loads again. So the engine keeps a list. An **abandoned library/file** is a library whose startup code or unload code crashed, and its file loads only from copies for the rest of the process. An error tells the person to restart the application.

The list is part of the library registry: a :term[mutex]{id=mutex}, the set of native handles of the libraries in use, and the list of abandoned paths. `IsAbandonedFile` makes each path absolute and tidy before it compares, and it also asks whether two paths name the same file, because a link to the file reaches the same library. The registry is allocated once and never destroyed. An active engine unloads its module from a static destructor at the end of the program, and that destructor can run after an ordinary object would be gone.

### The version and the load call

With the library open, the loader finds the two exports every module must have. A file that lacks either is not a script module, and the message says so. The next step is the version of the :term[application binary interface]{id=abi} (ABI), the one number that says whether both sides agree on every struct's layout.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L442-L481"
const auto getVersion = module->m_Library.GetFunction<StrataScriptGetABIVersionFunction>(ST_SCRIPT_GET_ABI_VERSION_SYMBOL);
const auto load = module->m_Library.GetFunction<StrataScriptLoadFunction>(ST_SCRIPT_LOAD_SYMBOL);
if (!getVersion || !load)
	return fail(fmt::format("'{}' is not a Strata script module: it does not export {} and {}", displayPath, ST_SCRIPT_GET_ABI_VERSION_SYMBOL, ST_SCRIPT_LOAD_SYMBOL));

uint32_t moduleVersion = 0;
const ScriptCallResult versionResult = module->Call({ nullptr, ST_SCRIPT_GET_ABI_VERSION_SYMBOL }, [&]()
{
	moduleVersion = getVersion();
	return static_cast<uint32_t>(StrataScriptResult_Ok);
});
if (versionResult != ScriptCallResult::Ok)
	return fail(fmt::format("Script module '{}' crashed while reporting its ABI version: {}", displayPath, module->m_Fault ? module->m_Fault->Description : ""));
if (moduleVersion != ST_SCRIPT_ABI_VERSION)
{
	return fail(fmt::format("Script module '{}' was built against script ABI version {}, but this engine uses version {}; rebuild the module "
		"against this engine's StrataScriptCore", displayPath, moduleVersion, ST_SCRIPT_ABI_VERSION));
}

// StructSize tells the module how much it may write (a module of a newer SDK knows more members).
StrataScriptModuleAPI api = {};
api.StructSize = sizeof(StrataScriptModuleAPI);
const ScriptCallResult loadResult = module->Call({ nullptr, ST_SCRIPT_LOAD_SYMBOL }, [&]()
{
	return load(&GetScriptHostAPI(), ST_SCRIPT_ABI_VERSION, &api);
});
switch (loadResult)
{
	case ScriptCallResult::Ok:
		break;
	case ScriptCallResult::Exception:
		return fail(fmt::format("Script module '{}' failed to initialize: {}", displayPath, module->m_LastException));
	case ScriptCallResult::Faulted:
	case ScriptCallResult::Unavailable:
		return fail(fmt::format("Script module '{}' crashed while initializing: {}", displayPath, module->m_Fault ? module->m_Fault->Description : ""));
	case ScriptCallResult::Rejected:
		return fail(fmt::format("Script module '{}' rejected the engine (script ABI version {})", displayPath, ST_SCRIPT_ABI_VERSION));
}
module->m_API = api;
module->m_Initialized = true;
```

1. **Lines 442–445:** the lookups use the exports' names from the :term[ABI]{id=abi} header; no export, no module.
2. **Lines 448–454:** even the version function is called through `Call`, so a module that crashes in it is contained.
3. **Lines 455–459:** a different version is refused before `StrataScript_Load` runs, because the module's idea of the host table may differ from the engine's. The message names both numbers and tells the person to rebuild.
4. **Lines 462–463:** `api` is a zeroed struct with its `StructSize` set to the engine's size. That tells the module how much it may write, so a module of a newer software development kit (:term[SDK]{id=sdk}) cannot write past the engine's struct.
5. **Lines 468–479:** the five call results become five different messages. An exception, a crash and a rejection are different failures for the person who reads the log.

At line 466 the engine hands the module the host table and the version. The host table is the set of functions through which scripts call the engine. The module fills `api`, which holds its name, its class list and its `Unload` function. At line 481 the module counts as ready for unloading, so its destructor will call `Unload`.

### The description, read once

The description lives in the module's memory. The engine reads it once, now, inside a guard, and builds its own records from it.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L483-L513"
// The description lives in module memory; reading it is guarded like any other module access.
std::string name;
std::vector<ScriptClassInfo> classes;
std::vector<ClassFunctions> functions;
std::string descriptionError;
bool descriptionValid = false;
const ScriptCallResult descriptionResult = module->Call({ nullptr, "module description" }, [&]()
{
	std::string readName;
	std::vector<ScriptClassInfo> readClasses;
	std::vector<ClassFunctions> readFunctions;
	std::string readError;
	const bool valid = module->ReadModuleDescription(readName, readClasses, readFunctions, readError);
	// Moving engine objects cannot fault, so the outputs are either untouched or complete.
	name = std::move(readName);
	classes = std::move(readClasses);
	functions = std::move(readFunctions);
	descriptionError = std::move(readError);
	descriptionValid = valid;
	return static_cast<uint32_t>(StrataScriptResult_Ok);
});
if (descriptionResult != ScriptCallResult::Ok)
	return fail(fmt::format("Script module '{}' has an unreadable description: {}", displayPath, module->m_Fault ? module->m_Fault->Description : ""));
if (!descriptionValid)
	return fail(fmt::format("Script module '{}' is invalid: {}", displayPath, descriptionError));

if (!name.empty())
	module->m_Name = std::move(name);
module->m_Classes = std::move(classes);
module->m_Functions = std::move(functions);
module->m_Ready = true;
```

1. **Lines 484–488:** the outputs are local engine objects that the guarded code fills.
2. **Lines 489–503:** the guarded body reads into its own locals first and moves them into the outputs at the end. Moving engine objects cannot fault, so the outputs are either untouched or complete.
3. **Lines 504–507:** a crash while reading and a description that is invalid are two different errors.
4. **Lines 509–513:** only now do the name, the class records and the functions go into the module, and `m_Ready` is set.

The validation itself is `ReadModuleDescription`. It treats every field as if an attacker or a bug wrote it, which is not far from the truth, because a module is a program built by someone else. It starts with the struct's own size and version, and then the limits.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L944-L984"
{
	const StrataScriptModuleAPI& api = m_API;
	if (api.StructSize < c_RequiredModuleAPISize || api.ABIVersion != ST_SCRIPT_ABI_VERSION)
	{
		outError = "the module description does not match this ABI version";
		return false;
	}
	// The name is optional (the file name stands in for it).
	if (!ReadScriptString(api.Name, outName) || outName.size() > c_MaxScriptNameSize)
	{
		outError = "the module has an invalid name";
		return false;
	}
	if (api.ClassCount > c_MaxScriptClasses || (api.ClassCount > 0 && !api.Classes))
	{
		outError = fmt::format("invalid class list ({} classes)", api.ClassCount);
		return false;
	}

	std::unordered_set<std::string> classNames;
	for (uint32_t classIndex = 0; classIndex < api.ClassCount; classIndex++)
	{
		const StrataScriptClassDesc* descriptor = api.Classes[classIndex];
		if (!descriptor || descriptor->StructSize < c_RequiredClassDescSize)
		{
			outError = fmt::format("class {} has an invalid descriptor", classIndex);
			return false;
		}

		ScriptClassInfo& info = outClasses.emplace_back();
		info.Index = classIndex;
		if (!ReadName(descriptor->Name, info.Name))
		{
			outError = fmt::format("class {} has an invalid name", classIndex);
			return false;
		}
		if (!classNames.insert(info.Name).second)
		{
			outError = fmt::format("class '{}' is registered twice", info.Name);
			return false;
		}
```

1. **Lines 946–950:** the description must be at least as large as the members the engine needs, and its version must match.
2. **Lines 951–956:** a name may be empty, in which case the file's name stands in, but it may not be longer than 1,024 :term[bytes]{id=byte}.
3. **Lines 957–961:** at most 65,536 classes, and a count above zero needs a pointer that is not null. A corrupt count would otherwise make the loop read billions of bytes.
4. **Lines 967–971:** each class descriptor must be present and at least as large as the required members.
5. **Lines 975–984:** a class needs a name of 1 to 1,024 bytes, and no two classes may share one. The duplicate check is a set of names the loop has seen.

Next come the functions. A class descriptor holds pointers to the class's functions. The engine copies every one of them into its own `ClassFunctions` record now, while the guard is on. After this read, a call uses the copy and never looks at the descriptor again. If it did, a module could change a pointer after the check, and every read of the descriptor outside a guard could crash.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L987-L1021"
ClassFunctions functions;
functions.Create = descriptor->Create;
functions.Destroy = descriptor->Destroy;
functions.GetField = descriptor->GetField;
functions.SetField = descriptor->SetField;
functions.OnCreate = descriptor->OnCreate;
functions.OnUpdate = descriptor->OnUpdate;
functions.OnFixedUpdate = descriptor->OnFixedUpdate;
functions.OnLateUpdate = descriptor->OnLateUpdate;
functions.OnDestroy = descriptor->OnDestroy;
functions.OnReload = descriptor->OnReload;
// Callbacks appended to the descriptor exist only when the module's descriptor is large enough to hold them.
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnCollisionEnter))
	functions.OnCollisionEnter = descriptor->OnCollisionEnter;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnCollisionExit))
	functions.OnCollisionExit = descriptor->OnCollisionExit;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnTriggerEnter))
	functions.OnTriggerEnter = descriptor->OnTriggerEnter;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnTriggerExit))
	functions.OnTriggerExit = descriptor->OnTriggerExit;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnAnimationEvent))
	functions.OnAnimationEvent = descriptor->OnAnimationEvent;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIClick))
	functions.OnUIClick = descriptor->OnUIClick;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIValueChanged))
	functions.OnUIValueChanged = descriptor->OnUIValueChanged;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIFocusChanged))
	functions.OnUIFocusChanged = descriptor->OnUIFocusChanged;
if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUISubmit))
	functions.OnUISubmit = descriptor->OnUISubmit;
if (!functions.Create || !functions.Destroy || !functions.GetField || !functions.SetField)
{
	outError = fmt::format("class '{}' lacks its lifetime or field functions", info.Name);
	return false;
}
```

1. **Lines 987–997:** the ten functions that every :term[ABI version]{id=abi-version} has are copied directly.
2. **Lines 998–1016:** the callbacks added to the descriptor later are copied only when the descriptor is large enough to hold them, so an older module never has its memory read past its end.
3. **Lines 1017–1021:** a class must have `Create`, `Destroy`, `GetField` and `SetField`; every other callback is optional.

After the copy, the loop builds the callback mask: for each callback whose function is not null, it sets one bit. Then it checks the fields, with a limit of 4,096 per class, the same name rules and a set of names against duplicates. The last two checks are the types.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L1074-L1088"
const std::optional<PropertyType> type = ScriptFieldTypeToPropertyType(fieldDescriptor->Type);
if (!type)
{
	outError = fmt::format("field '{}.{}' has an unsupported type ({})", info.Name, field.Name, fieldDescriptor->Type);
	return false;
}
field.Type = *type;

std::optional<PropertyValue> defaultValue = ScriptValueToFieldValue(fieldDescriptor->DefaultValue, field.Type);
if (!defaultValue)
{
	outError = fmt::format("field '{}.{}' has a default value of the wrong type", info.Name, field.Name);
	return false;
}
field.DefaultValue = std::move(*defaultValue);
```

1. **Lines 1074–1079:** a field's type number must map to a property type that the engine knows.
2. **Lines 1082–1088:** the default value must be of that type, or the field is refused. The default is converted into an engine value on the spot.

### The call

Everything that follows a load is a call, and every call goes through one function template. Each public function, such as `CreateInstance` or `InvokeCallback`, supplies a body and a **call site**, the record of what is being called: the class, the method, the entity and the scene.

The call site feeds two readers. When a call faults, the fault report names the class, the method and the entity. The watchdog, which reports calls that run too long, also reads it. The engine keeps the current call site in a :term[thread-local]{id=thread-local} variable, so code that runs inside the call can ask which call it belongs to.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L301-L344"
ScriptCallResult ScriptModule::Call(const ScriptCallSite& site, Function&& function)
{
	if (m_Fault)
		return ScriptCallResult::Unavailable;

	struct Invocation
	{
		std::remove_reference_t<Function>* Body;
		uint32_t Result;
	};
	Invocation invocation { &function, StrataScriptResult_Ok };

	CrashInfo crash;
	bool completed = false;
	{
		const ScriptCallScope scope(site, m_Watchdog, site.Class ? site.Class->Name.c_str() : m_Name.c_str());
		completed = CrashGuard::Invoke([](void* data)
		{
			Invocation* call = static_cast<Invocation*>(data);
			call->Result = (*call->Body)();
		}, &invocation, &crash);
	}

	if (!completed)
	{
		RecordFault(site, crash);
		return ScriptCallResult::Faulted;
	}
	// A nested call (e.g. a script spawning a prefab whose script crashed in its constructor) faulted the module.
	if (m_Fault)
		return ScriptCallResult::Faulted;

	switch (invocation.Result)
	{
		case StrataScriptResult_Ok:
			return ScriptCallResult::Ok;
		case StrataScriptResult_Exception:
			m_LastException = t_PendingException.empty() ? std::string("Unknown exception") : std::move(t_PendingException);
			t_PendingException.clear();
			return ScriptCallResult::Exception;
		default:
			return ScriptCallResult::Rejected;
	}
}
```

1. **Lines 303–304:** a faulted module answers Unavailable without calling anything.
2. **Lines 316–321:** `ScriptCallScope` marks the call for the watchdog and the thread-local site and undoes both however the call ends. `CrashGuard::Invoke` then runs the body.
3. **Lines 324–328:** when the guard reports a crash, `RecordFault` stores the fault and starts its symbolization, and the call returns Faulted.
4. **Lines 329–331:** a nested call, for example a script that spawns a prefab whose script crashed in its :term[constructor]{id=constructor}, may have faulted the module while this call itself continued.
5. **Lines 333–343:** the number the module returned becomes one of the engine's results. Exception takes its message from a thread-local string that the SDK filled.

The five results mean five different things for the caller. Ok means the call completed, and Exception means the script threw and the SDK caught it: only that instance is disabled, and the module is fine. Rejected means the module refused the call, for example a field value of the wrong type. Faulted means the code crashed and the module will not be called again. Unavailable means nothing ran, because the module was faulted before the call or the class lacks that callback.

### The engine around the module

The types around the module are small. `ScriptCallback` names the callbacks a class may implement, and `c_ScriptCallbackCount` counts them, so a tool that lists every callback follows new ones. `ScriptFieldInfo` is a field's name, type and default. `ScriptClassInfo` adds the callback mask and an `Implements` function that tests one bit.

`ScriptCodeLocation` is a place in native code: an address, the module file and the offset in it, and, where the module has debug information, the function, the file and the line. `ScriptFault` describes a crash: the module, class, method and entity, a description of the crash, the location and the stack, and a flag that says whether symbolization finished.

`ScriptEngine::LoadModule` calls `LoadInternal`, which picks the mode: `Copy` when hot reload is on and `InPlace` when it is off. It refuses to load while script code is on the stack, because replacing the module then would unload running code. If `ScriptModule::Load` fails, the engine logs the message and, when a module is loaded already, adds that the old module keeps running.

If the load succeeds, the engine moves the new module in, which unloads the old one, and logs one line such as `Loaded script module 'Name' (1 class)`.

The engine also owns the watchdog, the fault count and the hot reload watcher. The watcher and the reload protocol that moves running scenes to a new module belong to [hot reload](../scripting/hot-reload.md). What matters here is the last member: the **active engine**, the one `ScriptEngine` that a scene uses when it starts to play. `ScriptEngine::SetActive` stores it in a static variable, and a scene that starts afterwards reads `GetActive`. A game with no active engine runs its scenes without scripts, and tests cover this case.

Two programs create an engine. [The editor's script engine](../editor/script-builds.md) turns hot reload on and loads the project's module when it opens the project. [A shipped game's script engine](../worlds/runtime.md) loads the module named in the game's manifest in place, before the start scene, and a failure to load stops the start with the error.

### What script.status shows

When the editor has loaded a module, its command `script.status` reports what the engine learned from the description. The capture below is the answer for the Tetris sample, reduced to the members that come from the loader.

```text capture="script-status-loader"
{
  "loaded": true,
  "moduleName": "TetrisScripts",
  "loadCount": 1,
  "hotReload": true,
  "classes": [
    {
      "callbacks": [
        "OnCreate",
        "OnUpdate",
        "OnReload"
      ],
      "fields": [
        {
          "default": 60,
          "name": "Seed",
          "type": "Int"
        },
        {
          "default": 1,
          "name": "StartLevel",
          "type": "Int"
        },
        {
          "default": 10,
          "name": "LinesPerLevel",
          "type": "Int"
        },
        {
          "default": 0.8,
          "name": "StartInterval",
          "type": "Float"
        },
        {
          "default": 0.85,
          "name": "IntervalFactor",
          "type": "Float"
        },
        {
          "default": 0.05,
          "name": "MinInterval",
          "type": "Float"
        },
        {
          "default": 0.04,
          "name": "SoftDropInterval",
          "type": "Float"
        },
        {
          "default": 0.17,
          "name": "RepeatDelay",
          "type": "Float"
        },
        {
          "default": 0.05,
          "name": "RepeatInterval",
          "type": "Float"
        },
        {
          "default": "0000000000000000",
          "name": "CellMesh",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialI",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialO",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialT",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialS",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialZ",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialJ",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "MaterialL",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "GhostMaterial",
          "type": "Asset"
        },
        {
          "default": 0.92,
          "name": "CellScale",
          "type": "Float"
        },
        {
          "default": [
            12,
            15,
            0
          ],
          "name": "PreviewOffset",
          "type": "Vec3"
        },
        {
          "default": "0000000000000000",
          "name": "ScoreText",
          "type": "Entity"
        },
        {
          "default": "0000000000000000",
          "name": "LevelText",
          "type": "Entity"
        },
        {
          "default": "0000000000000000",
          "name": "LinesText",
          "type": "Entity"
        },
        {
          "default": "0000000000000000",
          "name": "MessageText",
          "type": "Entity"
        },
        {
          "default": "0000000000000000",
          "name": "MessagePanel",
          "type": "Entity"
        },
        {
          "default": "0000000000000000",
          "name": "MoveSound",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "LockSound",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "ClearSound",
          "type": "Asset"
        },
        {
          "default": "0000000000000000",
          "name": "GameOverSound",
          "type": "Asset"
        }
      ],
      "name": "TetrisBoard"
    }
  ],
  "fault": null
}
```

1. **Lines 2–5:** the module's state, name, load count and hot reload mode.
2. **Lines 8–12:** the callbacks the class has, read from the mask.
3. **Lines 13–163:** the fields, each with a default, a name and a type.
4. **Line 164:** the class's name, last because inside the class the keys are in order of the alphabet.
5. **Line 167:** the fault, null until the module crashes.

Each class lists its fields with their types and default values, and its callbacks, taken from the mask. The member `loadCount` counts successful loads and reloads. The member `hotReload` says which mode the next load uses. The member `fault` is null here; after a crash it holds the module, the class, the method, the entity and the crash's description.

## A worked example: the first game's module

Take the project of [the first game](../start/first-game.md), which a person created with the name `FirstGame`. The project makes the module's name from the project's name: its English letters and digits, each word starting with a capital, and `Scripts` appended, so `FirstGameScripts`. After a build, the file is `FirstGameScripts.dll` on Windows, in the project's folder `.strata/Scripts/Bin`. The one class in it is `Spinner`.

:::example[One load, from the file to the first call]
The editor opens the project and creates a `ScriptEngine`. It makes the engine active and turns hot reload on, so the mode is Copy. `LoadModule` receives the path of `FirstGameScripts.dll`.

1. **File check.** The file exists and is a regular file. The module's name starts as `FirstGameScripts`.
2. **Copy.** The file is not loaded yet, but the mode is Copy, so `Acquire` makes `ScriptModules-` plus a suffix under the user's runtime folder and locks `Owner.lock`. The file is copied to a name like `FirstGameScripts-` plus a random identifier plus `.dll`.
3. **Library.** `LoadLibraryGuarded` loads the copy, with the original's folder as the dependency folder. No startup code crashes. `RegisterLibrary` records the handle.
4. **Exports.** Both names are found. `StrataScript_GetABIVersion` returns 1, and the engine's `ST_SCRIPT_ABI_VERSION` is 1, so the check passes.
5. **Load call.** `StrataScript_Load` receives the host table and a zeroed `api` whose `StructSize` is the engine's size. It returns Ok and describes one class.
6. **Description.** The guarded read finds `ClassCount` 1, below 65,536. The class is named `Spinner`, which no other class shares. The field `DegreesPerSecond` has the type Float and the default 90. The SDK sets a callback's function only when the class overrides it, and `Spinner` overrides only `OnUpdate` (bit 1), so the mask is binary 10, which is 2.
7. **Ready.** The records move in and `m_Ready` is set. `ScriptEngine` logs `Loaded script module` followed by the module's name and `(1 class)`.

When a scene plays, the script system finds `Spinner` in the class list and calls `CreateInstance`. The call goes through `Call`: the guard runs the class's copied `Create` function, which returns the instance handle. Every `OnUpdate` is then one more call through the same function; no `OnCreate` runs, because the class has none.
:::

Two numbers show how much the engine trusts the file. The module wrote at most the bytes that `StructSize` allowed, and the engine read the description once, in one guarded call. Everything after that reads engine memory, except the module's own code.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Link the game's code into the engine's program | Many small engines and games | No version check, no description, no copy, and direct calls | The editor could not replace code while it runs, and one crash ends the program |
| Run scripts in a virtual machine | Engines with a scripting language on a virtual machine | A crash cannot touch the engine, and memory is managed | Slower code, a bridge for every call, and C++ gameplay gone |
| Run the game in a separate process | Some tools and servers | A crash ends only the game process, and a hung game can be ended | Every call crosses a process boundary, and shared memory needs a design |
| Load the file in place always | Programs that load extensions | No copy folder, no lock files and no cleanup | On Windows no rebuild while the editor runs, and one library state for two modules |
| Trust the description | Hosts that load their own extensions | No validation code | A corrupt count or a missing function crashes the engine |
| Link modules statically | Console ports | No loader at all; consoles often forbid loading code | The path that this page describes does not exist for it; the engine's plan names this with a console port |

The last row is a thing Strata does not do yet. The engine's plan, `Docs/Roadmap.md`, lists script modules linked statically together with a console port, and says that no `DynamicLibrary` path exists for it.

## How it is tested

The suite `Scripting.Module` tests the loader against small modules that the build makes from the sources in `StrataTests/Scripts`. Some are built to fail. The module `ABIMismatch` reports an ABI version one higher than the engine's. The test checks that the load is refused with a message that names both versions, and that the engine has no module and no fault afterwards. `Malformed` is written against the C interface directly and holds broken class tables, and `LoadFault` crashes while it loads.

One module must load: `NewerSDK` has a :term[module description]{id=module-description} larger than the engine's struct, as if a newer SDK had built it. The test checks that it loads, that its class and its field default arrive, and that the engine bounds what the module writes by the `StructSize` it passes.

Other cases in the suite cover the copy and the lock. A module that reloads runs from a private copy that is removed when it unloads, and a file that is loaded already loads again from a copy. Libraries beside the original are found when the module runs from a copy. Copy folders vanish once their owner process is gone and never before, and one without a lock file goes when it is old. Another test loads modules from several processes at the same time.

To run only these, give the doctest filter to the test program.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite="Scripting.Module"
```

The program runs only the cases of that suite and ends with a summary of the cases that passed and failed.

## Changing it safely

The extension points are few, and each is checked. To teach the engine a new callback, append it at the end of `ScriptCallback`, add its function at the end of `StrataScriptClassDesc`, and copy it in `ReadModuleDescription` only behind `ST_SCRIPT_HAS_MEMBER`. The reason is that modules built before the change have smaller descriptors, and the engine must not read past them. To add a new check to the description, put it in `ReadModuleDescription`, with an error message, and add a broken module to the tests.

Three rules of the engine's guide apply, each for a reason.

- **Never read module memory outside a guarded call.** A crash there ends the process and no fault is recorded.
- **Never skip the copy for a file that is loaded already.** Two modules would share one library's state.
- **Never let a load disturb the running module.** `LoadInternal` loads the new module next to the old one and replaces it only on success, so a broken build never harms a running game.

Before a change passes, run `Scripting.Module`, the other `Scripting.*` suites, and the feature test, which loads its script modules through the same code.

## Summary

- Before the engine calls a module, it checks the file, the exports, the ABI version, the load call's result and the description's limits, names, required members and types.
- Module memory is read only inside guarded calls, because a crash outside a guard ends the process; the function pointers are copied once so no later call reads the descriptor.
- A load runs from the file or from a private copy: a file that is loaded already, or abandoned, always runs from a copy, and hot reload always asks for one.
- The load of the first game's module goes from `ScriptEngine::LoadModule` through `ScriptModule::Load`, the guarded load of the library, the version check, `StrataScript_Load` and `ReadModuleDescription`, to the log line `Loaded script module`.

## Check yourself

1. A game ships with hot reload off, and its module file is not loaded yet in this process. Where does its library load from? (a) A private copy, always. (b) The file itself. (c) A copy, because shipped games are never trusted.

   :::answer{tests="load-modes"}
   Option (b) is right: without hot reload the mode is `InPlace`, and nothing forces a copy. Option (a) is wrong, because only `Copy` mode, a file that is loaded already, or an abandoned file leads to a copy. Option (c) is wrong, because trust plays no part in the choice; the guard and the checks apply to both paths.
   :::

2. The editor loads a module in place first, and later the same file is loaded again by a second engine in the same process. What does the second load do, and why?

   :::answer{tests="load-modes"}
   The second load runs from a private copy. The system returns the same handle for a file that is loaded already, so an in-place load would share the first module's static variables. `RegisterLibrary` sees the known handle, the load drops its reference and the copy path runs.
   :::

3. Which of these does the engine check before it calls `StrataScript_Load`? (a) The class count. (b) The ABI version. (c) That the file exports both :term[entry points]{id=entry-point-scripting}.

   :::answer{tests="engine-checks"}
   Options (b) and (c). The class count is part of the description, which does not exist until `StrataScript_Load` has filled it, so the engine checks it afterwards (a is wrong). The two exports and the version come first, and a module with the wrong version is refused without any call of `StrataScript_Load`.
   :::

4. Why does `ReadModuleDescription` copy every function pointer of a class into `ClassFunctions` instead of keeping a pointer to the descriptor?

   :::answer{tests="guarded-memory"}
   The descriptor is module memory. Reading it later, outside a guard, could crash the engine, and the module could change a pointer after the validation. With the copy, the engine reads module memory once, guarded, and later calls read only engine memory.
   :::

5. A module's `GetField` returns the result for a value of the wrong type. Which `ScriptCallResult` does the engine report, and is the module faulted?

   :::answer{tests="engine-checks"}
   `Call` maps every number but Ok and Exception to Rejected, so the result is Rejected. The module is not faulted: Faulted is only for a crash the guard contained.
   :::

6. Put these in the order the engine runs them when the editor loads a module in `Copy` mode: `ReadModuleDescription`, `StrataScript_GetABIVersion`, `ScriptModuleCopyDirectory::Acquire`, `StrataScript_Load`, `LoadLibraryGuarded`.

   :::answer{tests="trace-load"}
   The order is `ScriptModuleCopyDirectory::Acquire`, `LoadLibraryGuarded`, `StrataScript_GetABIVersion`, `StrataScript_Load`, `ReadModuleDescription`. The copy must exist before the library loads from it, and the library must load before its exports are called. The version check protects the load call, and the description exists only after the load call has filled it.
   :::

## Exercises

1. **Basic.** The module `ABIMismatch` returns `ST_SCRIPT_ABI_VERSION + 1` from `StrataScript_GetABIVersion`. Say what the engine does with it, and write the message it logs when the engine's version is 1.

   :::answer[Worked solution]{tests="engine-checks"}
   The engine finds both exports, then calls the version function through `Call`. The number it gets is 2, which differs from 1, so `Load` returns an error before `StrataScript_Load` runs. The message reads `Script module '<path>' was built against script ABI version 2, but this engine uses version 1; rebuild the module against this engine's StrataScriptCore`. The engine has no module afterwards and no fault, because nothing crashed.
   :::

2. **Medium.** Write a complete program with a function `Validate`. It refuses a description with more than 65,536 classes, an empty or too long name, a duplicate name, or more than 4,096 fields, and the program prints the verdict for five descriptions.

   :::answer[Worked solution]{tests="engine-checks" solution="sketches/scripting-loading-validate.cpp"}
   The function checks the count first, then walks the classes once and keeps a set of the names it has seen. The first failing check returns its reason, and an empty string means valid.

   ```cpp sketch="scripting-loading-validate.cpp"
   // A toy validator: a module's description is data from outside, so every count and name is checked before it is used.
   #include <cstdint>
   #include <cstdio>
   #include <set>
   #include <string>
   #include <vector>

   namespace
   {

   	constexpr std::uint32_t c_MaxClasses = 65536;
   	constexpr std::uint32_t c_MaxFields = 4096;
   	constexpr std::size_t c_MaxNameSize = 1024;

   	struct ClassDescription
   	{
   		std::string Name;
   		std::uint32_t FieldCount = 0;
   	};

   	// Returns an empty string when the description is valid, else the reason it is refused.
   	std::string Validate(std::uint32_t classCount, const std::vector<ClassDescription>& classes)
   	{
   		if (classCount > c_MaxClasses || classCount != classes.size())
   			return "invalid class list";

   		std::set<std::string> names;
   		for (const ClassDescription& description : classes)
   		{
   			if (description.Name.empty() || description.Name.size() > c_MaxNameSize)
   				return "a class has an invalid name";
   			if (!names.insert(description.Name).second)
   				return "class '" + description.Name + "' is registered twice";
   			if (description.FieldCount > c_MaxFields)
   				return "class '" + description.Name + "' has an invalid field list";
   		}
   		return {};
   	}

   	void Report(const char* label, const std::string& error)
   	{
   		std::printf("%s: %s\n", label, error.empty() ? "valid" : error.c_str());
   	}

   }

   int main()
   {
   	Report("one class", Validate(1, { { "Spinner", 1 } }));
   	Report("same name twice", Validate(2, { { "Spinner", 1 }, { "Spinner", 0 } }));
   	Report("5000 fields", Validate(1, { { "Spinner", 5000 } }));
   	Report("empty name", Validate(1, { { "", 0 } }));
   	Report("count too large", Validate(70000, {}));
   	return 0;
   }
   ```

   ```text output-of="scripting-loading-validate.cpp"
   one class: valid
   same name twice: class 'Spinner' is registered twice
   5000 fields: class 'Spinner' has an invalid field list
   empty name: a class has an invalid name
   count too large: invalid class list
   ```

   1. **Lines 11–13:** the three limits of the engine.
   2. **Lines 24–25:** the count is checked before any loop uses it, and it must match the list.
   3. **Lines 27–36:** one pass over the classes, with a set of the names seen so far.
   4. **Line 32:** `insert` reports whether the name was new, so a name that is not new is a duplicate.
   5. **Line 37:** an empty reason means the description is valid.

   The order matters: the count comes before the loop, as in the engine, because a corrupt count must never reach the loop.
   :::

3. **Hard.** Trace it yourself. Build the engine from source, set a breakpoint in `ScriptModule::Load`, open the first game's project in the editor, and follow the load of the first game's module. Name the functions you stop in, in order.

   :::answer[Worked solution]{tests="trace-load"}
   The editor's `EditorContext::OpenScriptEngine` makes the engine, turns hot reload on and calls `LoadScriptModule`. That :term[function calls]{id=function-call} `ScriptEngine::LoadModule` and `LoadInternal` in `Strata/src/Strata/Scripting/ScriptEngine.cpp`. `LoadInternal` calls `ScriptModule::Load` in `Strata/src/Strata/Scripting/ScriptModule.cpp`. There you stop in `ScriptModuleCopyDirectory::Acquire`, then `LoadLibraryGuarded`, then in the version call and the load call through `Call`, and then in `ReadModuleDescription`. Back in `LoadInternal` the engine logs `Loaded script module`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scripting/ScriptModule.h` and `ScriptModule.cpp`: `ScriptModule`, `ScriptModuleLoadMode`, `ScriptCallResult`, `ScriptCallSite`, `ScriptModuleCopyDirectory`; in the :term[source file]{id=source-file} `Load`, `LoadLibraryGuarded`, `Call`, `ReadModuleDescription`, `AbandonLibraryFile`.
- `Strata/src/Strata/Scripting/ScriptEngine.h` and `ScriptEngine.cpp`: `ScriptEngine`, `LoadInternal`, `SetActive`, `GetActive`.
- `Strata/src/Strata/Scripting/ScriptTypes.h`: `ScriptCallback`, `ScriptFieldInfo`, `ScriptClassInfo`, `ScriptCodeLocation`, `ScriptFault`.
- `Strata/src/Strata/Core/DynamicLibrary.h`, `Strata/src/Strata/Core/FileLock.h` and `Strata/src/Strata/Core/CrashGuard.h`: the classes the loader builds on.
- `StrataTests/src/Scripting/ScriptModuleTests.cpp` and `StrataTests/Scripts/`: the suite `Scripting.Module` and the test modules.
- Commands: `script.status` shows the loaded module; `script.reload` loads the file again.

## Further reading

- The documentation of `dlopen` in the Linux manual pages: how a loader finds a library and its dependencies; intermediate.
- Microsoft's documentation of `LoadLibraryEx` and dynamic-link library search order: the search folders that Strata's Windows loader restricts; intermediate.
- Jason Gregory, "Game Engine Architecture", the chapters on tools and gameplay code: why engines separate game code from the engine; intermediate.

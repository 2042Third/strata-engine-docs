---
id: scripting/symbolization
title: "From an address to a file and line"
description: "How Strata turns the addresses of a script crash into a module, a function, a file and a line, and why only Windows names the line."
kind: internals
size: M
tracks: [E]
needs: [scripting/crash-containment]
time: 70
learn:
  - id: address-to-line
    text: explain how a return address and a module's base become a module, an offset, a function, a file and a line
  - id: two-calls
    text: explain why Describe runs at fault time and Resolve runs on a job, one at a time
  - id: inline-line
    text: explain why an optimized build on Windows still names the line that crashed
  - id: posix-function
    text: explain why Linux and macOS name only the function of a crash
  - id: choose-frame
    text: predict which frame the fault location names for a given stack
since: 0.3.0
status: final
---

When a script crashes, the crash guard keeps a list of numbers: the addresses of the instructions that were running. A person cannot act on `0x7ff81a2b1234`; they need "line 42 of `FaultScripts.cpp`". **Symbolization** is the work that turns such an address into a module, a function, a :term[source file]{id=source-file} and a line, and the choice of the one frame that the report names. It does not catch the fault or decide what happens to the module afterwards, which is the job of the guard. It also does not draw the list in the editor.

## The problem and how engines solve it

The :term[machine code]{id=machine-code} of a program carries no names. The :term[compiler]{id=compiler} and the :term[linker]{id=linker} drop function names and line numbers when they build a program, because the processor needs none. A crash gives you addresses, and something must connect them to the source that made the code. Engines solve this in three ways.

The first way is to symbolize after the crash, on another machine. The program writes a small file with the addresses and some memory when it crashes, and a tool reads it later on another machine, with the :term[debug information]{id=debug-information} of that exact build. A symbol server stores the debug information of every release. This way adds nothing to the player's machine, but it needs a server, an upload and a match between the dump and the build.

The second way is to symbolize in the crashing process, with a library that reads the debug information itself. The third is to leave the names in the program, as Linux does for exported functions. Strata uses the second way and a part of the third, because its crashes happen on the machine of the person who builds the game. The module, its debug information and its source are all at hand, so no server and no upload are needed.

## Addresses, offsets and debug information

Start with the stack. When a :term[function calls]{id=function-call} another, the processor stores the address of the instruction after the call in memory, on the stack, so that the called function knows where to return. These **return addresses** form a chain: the function that crashed, the function that called it, and so on up to the engine. Each link of the chain, one function and the address where it stopped, is a frame of the stack. The chain is the :term[call stack]{id=call-stack} that a :term[debugger]{id=debugger} shows you.

To find the chain from a crash, you walk it. On Windows for 64-bit processors, every function that is not a leaf has `unwind data` in the file: a table that says how big its frame is and where the return address lies. `RtlLookupFunctionEntry` finds the table entry for an address, and `RtlVirtualUnwind` applies it to a copy of the processor's registers and gives the registers of the caller. A function that calls nothing and uses no stack of its own is a **leaf function** and has no entry, so its return address is on top of the stack.

A program is made of modules: the :term[executable]{id=executable} and every :term[shared library]{id=shared-library}. The system loads each module at a **base address** that can differ from run to run. The **offset** of an address is the address minus the base of its module. The offset stays the same in every run, and it is what the debug information of the module is written in.

Debug information is a second file or a second part of the module. On Windows the debug information is a program database (PDB), written by the linker beside the module. A **PDB** maps offsets to functions, files and lines. On Linux the compiler writes a format called :term[Debugging]{id=debugging} With Attributed Record Formats (DWARF) into the module itself, and the module also keeps a symbol table, a list of functions with their offsets and sizes. Strata reads the PDB and the symbol table, and it has no reader for DWARF.

The last idea is a change the compiler makes. **Inlining** replaces a call by the body of the called function, so that the call costs nothing. After it, the machine code of one function holds the code of two or three source functions. One address can then belong to several source lines at once, and the debug information keeps them all.

Each function the compiler merged into another is an **inline frame**: a frame that is in the source but not in the machine code.

:::example[One null write, in a Release build]
The test module `StrataTests/Scripts/Faults/FaultScripts.cpp` has a function `WriteThroughNull` with a write through a :term[null pointer]{id=null-pointer} at line 42, and `Crash` calls it at line 65. In a Release build the compiler merges the first into the second. The numbers below are invented for the example; the file and the lines are real.

Say the module loads at `0x7ff81a2b0000` and the crash happens at `0x7ff81a2b1234`. The offset is `0x7ff81a2b1234` minus `0x7ff81a2b0000`, which is `0x1234`. The next return address is `0x7ff81a2b1a50`. A call is five :term[bytes]{id=byte} long here, so the call instruction began at `0x7ff81a2b1a4b`; you find the address one below the return address, which lies inside the call.

The PDB maps `0x1234` to the function `Crash`, with the line of the call, 65. Its inline data adds one more fact: at this address the code of `WriteThroughNull` ran, at line 42. The report then lists `WriteThroughNull` (inlined) at line 42 first, and `Crash` at line 65 second. Without the inline data, the report would name line 65, the call, and the person would search the wrong function.
:::

## The map

Four parts work together, and they run on two threads. The guard captures the stack on the thread that crashed. `ScriptModule` records the fault on the same thread and describes every frame at once. A job on the I/O pool reads debug information and completes the files and lines. The :term[main thread]{id=main-thread} then asks for the fault and gets the symbolized stack.

```mermaid caption="Where a crash's addresses go. The guard captures them, the module describes them at once, a job reads the debug information, and the fault choice reads the result." alt="A diagram in four steps. The crash guard captures the addresses on the crashing thread. The script module describes each address at once and starts a job. The job on the I/O pool resolves the module's frames with the debug information and puts inline frames first. The fault choice then picks the first useful frame for the Problems panel."
flowchart LR
	guard["CrashGuard: addresses of the stack"] --> record["ScriptModule::RecordFault: Describe every frame, now"]
	record --> job["I/O job: Symbolizer::Resolve, one at a time"]
	job --> choose["ScriptModule::GetFault: ChooseFaultLocation"]
	record --> early["early location: module and offset only"]
	choose --> panel["Problems panel"]
```

The interface lives in `Strata/src/Strata/Core/Symbolizer.h`, with one implementation per platform: `Strata/src/Platform/Windows/WindowsSymbolizer.cpp` and `Strata/src/Platform/Posix/PosixSymbolizer.cpp`, which serves Linux and macOS. The stack walk lives in `Strata/src/Platform/Windows/WindowsCrashGuard.cpp`, and the choice of frames in `Strata/src/Strata/Scripting/ScriptModule.cpp`.

## The contract

Callers of `Symbolizer` have two functions and a few rules for each. The rules exist because the two functions run at very different times.

- **`Describe(address)`** is cheap. It needs no debug information, and it answers from what the loader knows: the module that holds the address, the module's base and, on Windows, its size. It must run while the module is still loaded, right after the fault, because a reload can unload the module. Any thread may call it.
- **`Resolve(frames, searchDirectories)`** reads debug information from files, so it blocks. It runs on a job, never on the main thread. A module is read from its file as if it were loaded at its old base, so it may be unloaded by then. Calls run one at a time, because DbgHelp, the Windows library that reads PDB files, is single-threaded.
- A frame has the address, the module path and base, the function, the file, the line and the list of inlined calls. Every field except the address is empty when unknown, and callers must handle that.
- A frame with no module is left as it is. Strata never invents a name.

:::rule[Nothing blocks a frame]
An editor command never waits for a file read, and a crash report follows the same idea. The report appears at once with module and offset, and files and lines follow when the job is done. The rule is in `AGENTS.md`, under the editor rules, and [Crash containment](crash-containment.md) shows how the guard keeps the main thread running.
:::

## A toy version

Symbolization is, at its core, a sorted table and a search. The toy has a table of three functions with their offsets and sizes, and a function that finds the entry with the largest offset not above the query. If the query lies beyond the entry's size, the answer is unknown, as it is for a query before the first entry.

```cpp sketch="scripting-symbolization-toy.cpp"
// A toy symbolizer: the nearest symbol at or below an offset, valid only inside the symbol's size.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	struct Symbol
	{
		uint64_t Offset = 0; // From the start of the module
		uint64_t Size = 0;
		std::string Name;
	};

	// The table is sorted by offset, as a linker writes it.
	const std::vector<Symbol> s_Table = {
		{ 0x1000, 0x100, "OnCreate" },
		{ 0x1100, 0x100, "Crash" },
		{ 0x1200, 0x100, "Update" },
	};

	std::string Describe(uint64_t offset)
	{
		const auto above = std::upper_bound(s_Table.begin(), s_Table.end(), offset,
			[](uint64_t value, const Symbol& symbol) { return value < symbol.Offset; });
		if (above == s_Table.begin())
			return "unknown";
		const Symbol& symbol = *(above - 1);
		if (offset - symbol.Offset >= symbol.Size)
			return "unknown";
		char text[64];
		std::snprintf(text, sizeof(text), "%s+0x%llx", symbol.Name.c_str(), static_cast<unsigned long long>(offset - symbol.Offset));
		return text;
	}

	void Print(const char* what, uint64_t offset)
	{
		std::printf("%-22s 0x%llx -> %s\n", what, static_cast<unsigned long long>(offset), Describe(offset).c_str());
	}
}

int main()
{
	Print("fault address", 0x1234);
	Print("return address", 0x1200);
	Print("return address minus 1", 0x1200 - 1);
	Print("before the table", 0x0fff);
	Print("after the last symbol", 0x1400);
	return 0;
}
```

```text output-of="scripting-symbolization-toy.cpp"
fault address          0x1234 -> Update+0x34
return address         0x1200 -> Update+0x0
return address minus 1 0x11ff -> Crash+0xff
before the table       0xfff -> unknown
after the last symbol  0x1400 -> unknown
```

1. **Line 26:** `upper_bound` finds the first entry above the offset, so the entry before it is the nearest one below.
2. **Line 31:** An offset past the end of that entry is unknown too.

The first line is the usual case: `0x1234` is `0x34` bytes into `Update`. The next two lines show a trap. A return address points after the call, and when the call is the last instruction of `Crash`, the return address is the first byte of `Update`. Asking for the raw return address names the wrong function, and subtracting one names `Crash`. The last two lines show the edges: an address before the table has no symbol, and the size check stops `Update` from claiming every address above it.

The toy has what the real code has in kind: a sorted table, a nearest-below search and the one-byte shift. It lacks what makes the real code long: modules and their bases, files read from disk that may be wrong, names with decoration, lines, and calls that were inlined.

## The real code, in the order the data flows

### The stack, on Windows

The guard starts with the processor's registers at the fault. The function below walks the chain with the `unwind data`. Watch for the leaf case and for the `__try`, which ends the walk when a corrupted stack faults again.

```cpp src="Strata/src/Platform/Windows/WindowsCrashGuard.cpp#L62-L93" symbol="CaptureStack"
// The faulting instruction and its callers' return addresses, unwound from the fault's context with the functions'
// unwind data. A corrupted stack may fault while it is read: that ends the walk (a nested exception in the filter
// would otherwise be dispatched on top of the one being handled).
void CaptureStack(const CONTEXT* faulting, StackCapture* record)
{
	__try
	{
		CONTEXT& context = record->Unwind;
		context = *faulting;
		while (record->FrameCount < c_MaxCrashStackFrames && context.Rip != 0)
		{
			record->Frames[record->FrameCount++] = context.Rip;
			DWORD64 imageBase = 0;
			PRUNTIME_FUNCTION function = RtlLookupFunctionEntry(context.Rip, &imageBase, nullptr);
			if (function)
			{
				PVOID handlerData = nullptr;
				DWORD64 establisherFrame = 0;
				RtlVirtualUnwind(UNW_FLAG_NHANDLER, imageBase, context.Rip, function, &context, &handlerData, &establisherFrame, nullptr);
			}
			else
			{
				// A leaf function, which has no unwind data: its return address is on top of the stack.
				context.Rip = *reinterpret_cast<const DWORD64*>(context.Rsp);
				context.Rsp += sizeof(DWORD64);
			}
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
	}
}
```

1. **Line 71:** The walk stops after 32 frames, or when the instruction address is zero.
2. **Lines 75–80:** The `unwind data` of the current function moves the copied registers up to its caller.
3. **Lines 84–86:** A leaf function has no entry, so its return address is on top of the stack.

After a stack overflow no walk happens at all, because the filter runs on what is left of the stack, and the report holds only the faulting instruction. On Linux and macOS the stack is the faulting instruction alone, and a C++ exception on Linux or macOS has no stack. These differences are why a Linux or macOS report is always short.

### Recording the fault

`RecordFault` runs right after the guard returns. For each address it asks `Describe` at once, and it keeps the frames of the script module apart for the job.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L650-L674" from="const std::string moduleFile = FileSystem::ToUTF8(m_LoadedPath.filename());" to="fault.Location = ChooseFaultLocation(fault.Stack, moduleFile);" symbol="ScriptModule::RecordFault"
const std::string moduleFile = FileSystem::ToUTF8(m_LoadedPath.filename());
std::vector<Symbolizer::Frame> moduleFrames;
std::vector<size_t> moduleFrameIndices;
for (size_t index = 0; index < crash.Stack.size(); index++)
{
	const Symbolizer::Frame described = Symbolizer::Describe(crash.Stack[index]);
	ScriptCodeLocation location;
	location.Address = crash.Stack[index];
	location.Module = FileSystem::ToUTF8(described.ModulePath.filename());
	location.ModuleOffset = described.ModuleBase != 0 && location.Address >= described.ModuleBase ? location.Address - described.ModuleBase : 0;
	location.Function = described.Function;
	if (IsSameFile(described.ModulePath, m_LoadedPath))
	{
		location.Module = moduleFile;
		// Return addresses point after their call: the call itself is the instruction before.
		Symbolizer::Frame frame = described;
		frame.Address = index == 0 ? location.Address : location.Address - 1;
		// The module as built (a hot-reload copy may be gone by the time the job reads it), with its PDB beside it.
		frame.ModulePath = m_SourcePath;
		moduleFrames.push_back(std::move(frame));
		moduleFrameIndices.push_back(index);
	}
	fault.Stack.push_back(std::move(location));
}
fault.Location = ChooseFaultLocation(fault.Stack, moduleFile);
```

1. **Line 655:** `Describe` runs for every address now, while the module is loaded.
2. **Line 666:** Every frame but the first moves back one byte, into its call.
3. **Line 668:** The job reads the module as built, with its PDB beside it.

Frames of other modules, such as the engine and the system, keep their module and offset and are never resolved. The module's frames use `m_SourcePath`, the file as built, because the copy that hot reload loaded may be gone when the job runs.

### The job

The job resolves the frames and then builds a new stack. Watch for the loop over `frame.Inlined`: it puts each inlined call before its frame.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L685-L719" from="std::vector<std::filesystem::path> searchDirectories = { m_SourcePath.parent_path() };" to="});" symbol="ScriptModule::RecordFault"
std::vector<std::filesystem::path> searchDirectories = { m_SourcePath.parent_path() };
JobSystem::SubmitIO([symbols, frames = std::move(moduleFrames), indices = std::move(moduleFrameIndices), directories = std::move(searchDirectories)]() mutable
{
	Symbolizer::Resolve(frames, directories);
	// Each frame of the module comes after the calls the compiler inlined at its address, innermost first, so the
	// stack starts with the line that ran (in an optimized build too) rather than the call of the function holding it.
	// GetFault reads the stack only once Done is set.
	std::vector<ScriptCodeLocation> stack;
	stack.reserve(symbols->Stack.size());
	size_t nextFrame = 0;
	for (size_t index = 0; index < symbols->Stack.size(); index++)
	{
		ScriptCodeLocation location = symbols->Stack[index];
		if (nextFrame < indices.size() && indices[nextFrame] == index)
		{
			const Symbolizer::Frame& frame = frames[nextFrame++];
			for (const Symbolizer::InlinedCall& call : frame.Inlined)
			{
				ScriptCodeLocation inlined = location;
				inlined.Function = call.Function;
				inlined.File = call.File;
				inlined.Line = call.Line;
				inlined.Inlined = true;
				stack.push_back(std::move(inlined));
			}
			if (!frame.Function.empty())
				location.Function = frame.Function;
			location.File = frame.File;
			location.Line = frame.Line;
		}
		stack.push_back(std::move(location));
	}
	symbols->Stack = std::move(stack);
	symbols->Done.store(true, std::memory_order_release);
});
```

1. **Line 685:** The search folder is the module's folder, where its PDB lies.
2. **Lines 701–708:** Each inlined call becomes a frame of its own, ahead of the frame that holds it.
3. **Line 718:** `Done` is set last, so a reader that sees it sees the whole stack.

The result is stored with a release write to `Done`: a write after which a thread that reads `Done` with an acquire read also sees every earlier write of the job. `GetFault` on the main thread reads `Done` with an acquire read, and only then reads the stack. Until then it returns the early stack, whose first module frame is the location.

### DbgHelp on Windows

**DbgHelp** is the Windows library that reads PDB files and answers questions about addresses. `Resolve` locks a :term[mutex]{id=mutex}, because its options are shared by the whole process. It gives DbgHelp a session handle of its own. Other users of DbgHelp in the process, such as a crash reporter, then see no change. Watch how each module is loaded.

```cpp src="Strata/src/Platform/Windows/WindowsSymbolizer.cpp#L148-L199" symbol="Resolve"
void Resolve(std::span<Frame> frames, std::span<const std::filesystem::path> searchDirectories)
{
	std::lock_guard lock(s_DbgHelpMutex);
	std::wstring searchPath;
	for (const std::filesystem::path& directory : searchDirectories)
	{
		searchPath += searchPath.empty() ? L"" : L";";
		searchPath += ToWide(directory);
	}

	SymSetOptions(SYMOPT_UNDNAME | SYMOPT_LOAD_LINES | SYMOPT_FAIL_CRITICAL_ERRORS | SYMOPT_NO_PROMPTS | SYMOPT_DEFERRED_LOADS);
	const HANDLE session = GetSessionHandle();
	if (!SymInitializeW(session, searchPath.empty() ? nullptr : searchPath.c_str(), FALSE))
		return;

	std::vector<uint64_t> loadedBases;
	for (Frame& frame : frames)
	{
		if (frame.ModulePath.empty() || frame.ModuleBase == 0)
			continue;
		if (std::find(loadedBases.begin(), loadedBases.end(), frame.ModuleBase) == loadedBases.end())
		{
			// The module as it was loaded: its file at its base and with its size (the file is read, the process is not; without
			// the size DbgHelp maps no address to the module). 0 with no error: loaded already.
			const std::wstring image = ToWide(frame.ModulePath);
			SetLastError(ERROR_SUCCESS);
			const DWORD64 loadedBase = SymLoadModuleExW(session, nullptr, image.c_str(), nullptr, frame.ModuleBase, static_cast<DWORD>(frame.ModuleSize), nullptr, 0);
			if (loadedBase == 0 && GetLastError() != ERROR_SUCCESS)
				continue;
			loadedBases.push_back(frame.ModuleBase);
		}

		SymbolBuffer symbol;
		DWORD64 displacement = 0;
		if (SymFromAddrW(session, frame.Address, &displacement, symbol.Symbol()))
			frame.Function = NameAnonymousNamespaces(FromWide(symbol.Symbol()->Name));

		IMAGEHLP_LINEW64 line = {};
		line.SizeOfStruct = sizeof(line);
		DWORD lineDisplacement = 0;
		if (SymGetLineFromAddrW64(session, frame.Address, &lineDisplacement, &line))
		{
			frame.File = FromWide(line.FileName);
			frame.Line = line.LineNumber;
		}
		frame.Inlined.clear();
		ResolveInlinedCalls(session, frame);
	}
	for (uint64_t base : loadedBases)
		SymUnloadModule64(session, base);
	SymCleanup(session);
}
```

1. **Line 150:** One mutex lets a single call use DbgHelp at a time.
2. **Lines 168–178:** Each module loads once, from its file, at its old base and with its size.
3. **Lines 193–198:** The inline trace follows, and then the modules and the session are released.

### The inline trace

For one address, DbgHelp can list the functions the compiler merged there. The function below asks how many there are, finds the first one, and reads each function's name and line.

```cpp src="Strata/src/Platform/Windows/WindowsSymbolizer.cpp#L79-L107" symbol="ResolveInlinedCalls"
// The calls the compiler inlined at the frame's address. DbgHelp numbers the inline frames of an address from the
// context SymQueryInlineTrace gives for it, the innermost first.
void ResolveInlinedCalls(HANDLE session, Frame& frame)
{
	const DWORD count = SymAddrIncludeInlineTrace(session, frame.Address);
	if (count == 0)
		return;
	DWORD context = 0;
	DWORD frameIndex = 0;
	if (!SymQueryInlineTrace(session, frame.Address, 0, frame.Address, frame.Address, &context, &frameIndex))
		return;
	for (DWORD index = 0; index < count; index++, context++)
	{
		InlinedCall call;
		SymbolBuffer symbol;
		DWORD64 displacement = 0;
		if (SymFromInlineContextW(session, frame.Address, context, &displacement, symbol.Symbol()))
			call.Function = NameAnonymousNamespaces(FromWide(symbol.Symbol()->Name));
		IMAGEHLP_LINEW64 line = {};
		line.SizeOfStruct = sizeof(line);
		DWORD lineDisplacement = 0;
		if (SymGetLineFromInlineContextW(session, frame.Address, context, 0, &lineDisplacement, &line))
		{
			call.File = FromWide(line.FileName);
			call.Line = line.LineNumber;
		}
		frame.Inlined.push_back(std::move(call));
	}
}
```

1. **Line 83:** DbgHelp tells how many inline frames the address has; none ends the work.
2. **Lines 95–104:** For each context, the name and the line are read.

### Linux and macOS

On Linux and macOS, `Describe` calls `dladdr`, a function of the system that names the module holding an address and the nearest symbol the module exports. A script module hides its symbols, so on Linux the nearest exported symbol is another function; `Describe` therefore leaves the function empty there. On macOS the loader searches the module's whole symbol table, so `Describe` fills the function and `Resolve` does nothing. Neither system gives a file or a line, because Strata has no DWARF reader.

:::caution[The header's comment is out of date]
The comment in `Strata/src/Strata/Core/Symbolizer.h` says that Linux and macOS use `dladdr` only. On Linux, `Resolve` also reads the symbol table of the module file, in the `ELF` format, as shown next.
:::

On Linux, the module file keeps a full symbol table unless someone strips it. The function below reads it by hand from the file's bytes. Every read goes through `ReadStruct`, which refuses a read outside the file, because a module file is data from disk and must not be trusted to be well formed.

```cpp src="Strata/src/Platform/Posix/PosixSymbolizer.cpp#L48-L91" symbol="FindElfFunction"
std::string FindElfFunction(const std::filesystem::path& file, uint64_t offset)
{
	const std::optional<uint64_t> size = FileSystem::GetFileSize(file);
	if (!size || *size > c_MaxModuleFileSize)
		return {};
	const std::optional<std::vector<uint8_t>> bytes = FileSystem::ReadBytes(file);
	if (!bytes)
		return {};
	const std::optional<Elf64_Ehdr> header = ReadStruct<Elf64_Ehdr>(*bytes, 0);
	if (!header || std::memcmp(header->e_ident, ELFMAG, SELFMAG) != 0 || header->e_ident[EI_CLASS] != ELFCLASS64
		|| header->e_shentsize != sizeof(Elf64_Shdr))
	{
		return {};
	}

	for (uint16_t index = 0; index < header->e_shnum; index++)
	{
		const std::optional<Elf64_Shdr> symbols = ReadStruct<Elf64_Shdr>(*bytes, header->e_shoff + static_cast<uint64_t>(index) * sizeof(Elf64_Shdr));
		if (!symbols || symbols->sh_type != SHT_SYMTAB || symbols->sh_entsize != sizeof(Elf64_Sym) || symbols->sh_link >= header->e_shnum)
			continue;
		const std::optional<Elf64_Shdr> strings = ReadStruct<Elf64_Shdr>(*bytes, header->e_shoff + static_cast<uint64_t>(symbols->sh_link) * sizeof(Elf64_Shdr));
		if (!strings || strings->sh_offset > bytes->size() || bytes->size() - strings->sh_offset < strings->sh_size)
			continue;
		const uint64_t count = symbols->sh_size / sizeof(Elf64_Sym);
		for (uint64_t symbolIndex = 0; symbolIndex < count; symbolIndex++)
		{
			const std::optional<Elf64_Sym> symbol = ReadStruct<Elf64_Sym>(*bytes, symbols->sh_offset + symbolIndex * sizeof(Elf64_Sym));
			if (!symbol)
				break;
			if (ELF64_ST_TYPE(symbol->st_info) != STT_FUNC || symbol->st_size == 0 || offset < symbol->st_value
				|| offset - symbol->st_value >= symbol->st_size || symbol->st_name >= strings->sh_size)
			{
				continue;
			}
			// The name ends with a null inside the string table.
			const char* name = reinterpret_cast<const char*>(bytes->data() + strings->sh_offset + symbol->st_name);
			const size_t available = static_cast<size_t>(strings->sh_size - symbol->st_name);
			if (std::memchr(name, '\0', available) == nullptr)
				continue;
			return Demangle(name);
		}
	}
	return {};
}
```

1. **Line 51:** A module file over 512 MiB is not read.
2. **Lines 56–61:** The :term[header]{id=header} must be a 64-bit `ELF` file with section headers of the right size.
3. **Lines 77–81:** Only a function whose size covers the offset matches.

### Choosing the frame

The last step picks the frame that the report names. A frame of the module counts when it has a file and its file is not :term[runtime]{id=runtime} code: the :term[C runtime]{id=crt}, or the :term[SDK's]{id=sdk} entry file where `abort()` is reported. If no frame qualifies, the first frame of the module wins.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L589-L604" symbol="ChooseFaultLocation"
// The frame a fault is reported at: the first of the module's frames that has a source file and is not runtime code,
// else the first of the module's frames.
std::optional<ScriptCodeLocation> ChooseFaultLocation(const std::vector<ScriptCodeLocation>& stack, const std::string& module)
{
	const ScriptCodeLocation* first = nullptr;
	for (const ScriptCodeLocation& frame : stack)
	{
		if (frame.Module != module)
			continue;
		if (!first)
			first = &frame;
		if (!frame.File.empty() && !IsRuntimeFrame(frame))
			return frame;
	}
	return first ? std::optional<ScriptCodeLocation>(*first) : std::nullopt;
}
```

1. **Lines 596–599:** Frames of other modules never count, and the first frame of the module is kept as the fallback.
2. **Lines 600–601:** The first frame with a file that is not runtime code wins.
3. **Line 603:** With no such frame, the fallback is returned.

`GetFault` runs this choice again once the job is done. The first choice, made at fault time, saw no files, so it took the first module frame by default; the second sees the files and the inline frames.

What the person sees is the Problems panel of the editor. It shows one row for the crash, with the chosen function and file and line, and then the rows of the stack's other frames that have a file. A row for an inlined call ends in "(inlined)". `StrataEditor/src/Panels/ProblemsPanel.cpp` builds these rows and skips the SDK's internal frames.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Crash dump files and a symbol server | Crash reporting services of large products | Names for crashes on players' machines, which hold no debug information | A server, an upload and a privacy question for a tool that serves the person who builds the game |
| A DWARF reader or a symbolizing library on Linux and macOS | Debuggers and tools such as addr2line | Files and lines on every platform | A large reader of a complex format, fed with files from disk |
| Names from a frame-pointer walk | Profilers on Linux | A stack with no `unwind data` | Wrong stacks in :term[optimized]{id=optimization} code, which often omits frame pointers |
| Symbolizing on the crashing thread | Simple crash handlers | No job and no early report | A frame that waits on files, and a handler that must not fail |

## How it is tested

The suite `Scripting.Faults` in `StrataTests/src/Scripting/ScriptFaultTests.cpp` runs a module built from `StrataTests/Scripts/Faults/FaultScripts.cpp` and crashes it on purpose. Two test cases cover this page. The first is named "A crash names where it happened: the source file and line on Windows, the function elsewhere". On Windows it checks the file and the source line. On other systems it checks that the file is empty and that the function is `Crash` or the :term[callback]{id=callback} that called it, because an optimized build may merge the one into the other.

The second, "A crash in code the compiler inlined names the line that ran, then the call it was inlined at", crashes through `WriteThroughNull`. On Windows it reads the source line at the location and requires `*pointer = 7;`, then finds the line `WriteThroughNull();` and requires it after the write in the stack. Run it with `build/windows/bin/Debug/StrataTests.exe --test-suite=Scripting.Faults`. Release and :term[Dist]{id=dist} builds are where the compiler inlines the helper.

## Changing it safely

- **A new platform or format** implements the two functions of `Symbolizer.h`. `Describe` must need no debug information, and `Resolve` must treat every file as untrusted: check every size and offset before you read.
- **A new runtime file** that should be skipped goes into `IsRuntimeFrame`, with a test that has such a frame in a stack.
- **A new field of a frame** is filled by `Resolve` and copied in the job's loop, and the Problems panel decides whether to show it.
- Keep `Resolve` off the main thread. A call on the main thread blocks the frame, which breaks the rule above.
- Run `Scripting.Faults` on the platform you changed, and on Windows in Release too, because the inline case exists only there.

## What went wrong before

An optimized script module was reported at the call of a small helper, not at the line that crashed. DbgHelp's line lookup returns, for an address in inlined code, the line of the outermost call in the physical function. The fix was the inline trace of `ResolveInlinedCalls` and the loop in the job that puts the inlined calls first. Its regression test is the second test case above.

## Summary

- A return address minus the module's base gives an offset, and the debug information maps the offset to a function, a file and a line.
- `Describe` is cheap and runs at fault time while the module is loaded; `Resolve` blocks, runs on a job and runs one at a time.
- Inline data in the PDB lets Windows name the line that ran in an optimized build.
- Linux reads the function from the `ELF` symbol table, macOS from `dladdr`, and neither has a file or line.
- The fault location is the first frame of the module with a file that is not runtime code.

## Check yourself

1. A module is loaded at `0x7ff600000000`. A frame's return address is `0x7ff600003000`. Which address do you find, and what is its offset?

   :::answer{tests="address-to-line"}
   You find `0x7ff600002fff`, one below the return address, because the call is the instruction before it. Its offset is `0x2fff`. The raw return address would give `0x3000`, which may be the first byte of the next function.
   :::

2. Why does `Describe` run inside `RecordFault`, but `Resolve` on a job? (a) `Resolve` is cheap and `Describe` is slow. (b) `Describe` needs the module loaded, and `Resolve` reads files and may block. (c) DbgHelp requires a job.

   :::answer{tests="two-calls"}
   Option (b) is right. The loader knows the module only while it is loaded, and reading a PDB takes time that a frame should not pay. Option (a) swaps the two. Option (c) is wrong: DbgHelp needs only that calls come one at a time, which the mutex ensures.
   :::

3. A Release module crashes in an inlined helper on Windows. Which two frames come first in the report, and which line does each name?

   :::answer{tests="inline-line"}
   First comes the inlined helper, at the line of the write. Second comes the function it was inlined into, at the line of the call. The job puts the inline frame before its frame, so the location is the line that ran.
   :::

4. The same crash happens on Linux. What does the Problems panel show, and why?

   :::answer{tests="posix-function"}
   The panel shows the function from the symbol table and no file or line. The stack has only the faulting instruction, and without a DWARF reader nothing maps an offset to a line. If the module is stripped, the function is empty too.
   :::

5. A stack has these frames of the module: `abort` in a C runtime file, `AbortHandler` in `ScriptModuleEntry.cpp`, `Crash` in `FaultScripts.cpp`. Which frame does `ChooseFaultLocation` return?

   :::answer{tests="choose-frame"}
   `ChooseFaultLocation` returns `Crash`. The first two frames have files, but the first is runtime code and the second is the SDK's entry file, so both are skipped.
   :::

## Exercises

1. **Basic.** Extend the toy table with a function `Late` of size `0x80` at offset `0x1300`. Predict the result of asking for `0x1380`, `0x137f` and the return address `0x1300`, taken as a return address.

   :::answer[Worked solution]{tests="address-to-line"}
   `0x1380` is `0x80` past the start of `Late`, which is its size, so the answer is unknown. `0x137f` is `Late+0x7f`. The return address `0x1300` becomes `0x12ff`, which is `Update+0xff`, because `Update` has size `0x100` and starts at `0x1200`.
   :::

2. **Medium.** Trace it yourself. Build the Faults module in Release on Windows, run `Scripting.Faults` and put :term[breakpoints]{id=breakpoint} in `ScriptModule::RecordFault`, in `Symbolizer::Resolve` and in `ScriptModule::GetFault`. Say what each stop shows about the stack.

   :::answer[Worked solution]{tests="two-calls,inline-line"}
   In `Strata/src/Strata/Scripting/ScriptModule.cpp`, the stop in `RecordFault` shows frames with a module and offset and no files, and the first choice by `ChooseFaultLocation`. The stop in `Resolve`, in `Strata/src/Platform/Windows/WindowsSymbolizer.cpp`, runs on a job thread and fills each frame's file and line and its `Inlined` list. In `GetFault`, once `Done` is set, the stack holds the inline frame before its call, and the choice runs again.
   :::

3. **Medium.** Write a complete program that chooses the fault location from a list of frames, as `ChooseFaultLocation` does. Predict what it prints for three stacks: an `abort()` in a script, a module with no debug information, and a fault in the engine.

   :::answer[Worked solution]{tests="choose-frame" solution="sketches/scripting-symbolization-choose.cpp"}
   The first stack names `Crash`: the `abort` frame is C runtime code and `AbortHandler` is the SDK's entry file, so both are skipped. The second names the first frame of the module, which has no name. The third names no frame, because no frame belongs to the module.

   ```cpp sketch="scripting-symbolization-choose.cpp"
   // The fault location of the toy: the first frame of the module that has a file and is no runtime code.
   #include <cstdio>
   #include <optional>
   #include <string>
   #include <vector>

   namespace
   {
   	struct Frame
   	{
   		std::string Module;
   		std::string Function;
   		std::string File; // Empty when unknown
   	};

   	bool IsRuntime(const Frame& frame)
   	{
   		return frame.File.find("\\crt\\src\\") != std::string::npos || frame.File.ends_with("ScriptModuleEntry.cpp");
   	}

   	std::optional<Frame> Choose(const std::vector<Frame>& stack, const std::string& module)
   	{
   		const Frame* first = nullptr;
   		for (const Frame& frame : stack)
   		{
   			if (frame.Module != module)
   				continue;
   			if (!first)
   				first = &frame;
   			if (!frame.File.empty() && !IsRuntime(frame))
   				return frame;
   		}
   		return first ? std::optional<Frame>(*first) : std::nullopt;
   	}

   	void Show(const char* title, const std::vector<Frame>& stack)
   	{
   		const std::optional<Frame> chosen = Choose(stack, "Game.dll");
   		const char* name = !chosen ? "none" : chosen->Function.empty() ? "(first frame, no name)" : chosen->Function.c_str();
   		std::printf("%s: %s\n", title, name);
   	}
   }

   int main()
   {
   	Show("abort in a script", { { "Game.dll", "abort", "d:\\crt\\src\\abort.cpp" }, { "Game.dll", "AbortHandler", "ScriptModuleEntry.cpp" }, { "Game.dll", "Crash", "FaultScripts.cpp" } });
   	Show("no debug information", { { "Game.dll", "", "" }, { "Game.dll", "", "" } });
   	Show("a fault in the engine", { { "Strata.exe", "Update", "Scene.cpp" } });
   	return 0;
   }
   ```

   ```text output-of="scripting-symbolization-choose.cpp"
   abort in a script: Crash
   no debug information: (first frame, no name)
   a fault in the engine: none
   ```

   1. **Line 18:** A frame is runtime code when its file is in the C runtime or is the SDK's entry file.
   2. **Line 26:** Frames of other modules are skipped.
   3. **Lines 30–31:** The first frame with a file that is no runtime code is the answer.
   :::

4. **Hard.** What does the Problems panel show for the same inlined crash on Linux? Name the two reasons and the field that stays empty.

   :::answer[Worked solution]{tests="posix-function"}
   The crash row names a function, found by `FindElfFunction`, with no file and no line. The first reason is that the stack holds the faulting instruction alone. The second is that no DWARF reader exists, so `Frame::File` stays empty, and `Frame::Inlined` stays empty too.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Symbolizer.h`: the interface, `Frame` and `InlinedCall`.
- `Strata/src/Platform/Windows/WindowsSymbolizer.cpp`, `Strata/src/Platform/Posix/PosixSymbolizer.cpp`: the implementations.
- `Strata/src/Platform/Windows/WindowsCrashGuard.cpp`: the stack walk; `Strata/src/Strata/Core/CrashGuard.h`: `CrashInfo` and `c_MaxCrashStackFrames`.
- `Strata/src/Strata/Scripting/ScriptModule.cpp`: `RecordFault`, `GetFault` and `ChooseFaultLocation`.
- `StrataEditor/src/Panels/ProblemsPanel.cpp`: the rows. `StrataTests/src/Scripting/ScriptFaultTests.cpp`: the tests.

## Further reading

- Microsoft's documentation of the Debug Help Library (intermediate): the functions `Resolve` calls.
- The ELF specification, section "Symbol Table" (advanced): the structures `FindElfFunction` reads.
- The DWARF standard (advanced): the line tables Strata does not read.

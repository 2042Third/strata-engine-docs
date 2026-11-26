---
id: scripting/crash-containment
title: "Crash containment"
description: "How Strata keeps the editor running when a game script crashes: hardware exceptions, the guard on Windows and POSIX, and what no guard can contain."
kind: internals
size: L
tracks: [E]
needs: [scripting/loading, core/conventions, core/debugging]
time: 85
learn:
  - id: classify-fault
    text: name, for a given fault, whether Strata contains it and what state the engine is in afterwards
  - id: resume-after-fault
    text: explain how the Windows and the POSIX guard resume after a fault, and why each needs its special step
  - id: compare-approaches
    text: compare in-process containment with a child process and a virtual machine by cost and by what each contains
  - id: exception-or-crash
    text: predict what an exception and a crash in a script do to the instance, the module and play mode
  - id: watchdog-limits
    text: explain what the watchdog can and cannot do, and why a script must never block
since: 0.3.0
status: final
---

Game scripts are native code that you or an artificial intelligence (AI) agent write while the editor is open. Native code can write through a :term[null pointer]{id=null-pointer}, divide by zero or call itself without end, and the :term[operating system]{id=operating-system} answers by ending the process. Crash containment is the part of Strata that turns such a crash into a report. The call that crashed returns "failed" and the module that held the script is marked as not usable, but the editor stays open with your scene intact. It does not make crashing scripts safe, repair the module or catch every way a process dies.

## The problem and how engines solve it

A script is a function that the engine calls once per frame. If that function crashes, the engine has three questions to answer: who notices, how the program continues, and what state the rest of the program is in.

Most engines answer with "nobody": the game and the engine are one process, so the process ends and a crash reporter writes a file. That costs nothing per call and loses all work that you did not save. For a game that ships this is acceptable. For an editor that runs the game while you edit, it is not: you press Play, a script has a mistake, and the scene you built for an hour is gone.

Three techniques contain the crash. Each one buys safety with a different currency.

- **Process isolation:** the script runs in a second process and the engine talks to it through messages. A crash ends only that process, even an endless loop can be answered by ending it, and the engine can start a new one. Web browsers run each page this way. The price is that every call becomes a message between two processes, and every piece of data the script reads has to be copied or placed in shared memory.
- **A virtual machine that confines the script:** the script is not :term[machine code]{id=machine-code} but instructions for a small program, such as Lua or WebAssembly, that checks every memory access. A script cannot crash the host, and the machine can count instructions and stop a loop. The price is a different language, slower code for heavy work, and a boundary through which every engine object must pass.
- **A guard in the same process:** the script stays native code, and the engine asks the operating system to hand it the crash instead of ending the process. The price is that the guard sits in a damaged process. Whatever the crashed code was doing, such as holding a lock or writing a file, stays half done.

Strata chose the third. A script call costs the same as a :term[function call]{id=function-call} plus a few instructions, and scripts stay C++ with the full gameplay interface. The editor survives the crashes that happen in practice: a bad pointer, a division by zero, a function that calls itself without end. The table compares the three.

| Approach | Cost of one call | Contains a bad pointer | Contains an endless loop | Contains a corrupted heap |
| --- | --- | --- | --- | --- |
| Same process, no guard | None | No, the process ends | No | No |
| Strata's guard | A few instructions | Yes | No: the watchdog only reports | Not always |
| Child process | A message between two processes | Yes | Yes, by ending the process | Yes |
| Virtual machine | The machine's own speed | Yes | Yes, by counting instructions | Yes |

:::why
Strata's scripts are C++ so that a game made in Strata runs at the speed of the engine and uses the same math types and the same :term[debugger]{id=debugger}. A virtual machine would have cost both, and a child process would have turned every `GetTransform()` call into a message. The guard keeps both and accepts that a few failures stay outside it.
:::

## What happens when a processor cannot continue

A processor runs instructions one at a time. Some instructions cannot be completed, and the processor does not guess: it stops the program at that instruction and calls a function of the operating system. Windows calls the event a hardware exception, and Linux and macOS turn it into a signal. These are the cases that matter for scripts.

- **Access violation:** the instruction reads or writes a :term[memory address]{id=memory-address} that the program has not been given. A null pointer is address 0, and the operating system never maps the pages around it, so `*pointer = 42` with a null `pointer` always ends here. Linux names this signal `SIGSEGV`; macOS may name a similar one `SIGBUS`.
- **Integer division by zero:** an integer division by 0 has no result. On x64 processors the division instruction itself stops the program. On `ARM64` processors the division instruction does not stop: it gives 0. The engine's fault tests therefore omit this case on `ARM64`.
- **Illegal instruction:** the processor meets :term[bytes]{id=byte} that are not an instruction it knows, for example after a jump into data or a program built for a newer processor.
- **Stack overflow:** each thread has a fixed block of memory for the stack that holds the :term[local variables]{id=local-variable} of every active function. A function that calls itself without end uses it all. Below the block lies a page of memory, the guard page, that the operating system marks as "touch me and trigger the exception". The first touch is the signal that the stack is full.

A stack overflow is the hard case. The stack is full, and the code that must handle the crash needs a stack too. Both systems solve this with extra memory kept for the purpose, which the next sections name.

:term[Hexadecimal]{id=hexadecimal} numbers appear in these reports. A null write says "writing address 0x0000000000000000": base 16, sixteen digits of 4 bits each, which is 64 bits and one address. A small address such as `0x8` still means a null pointer plus a field offset.

## Two systems, one idea

Windows and POSIX (Linux and macOS) deliver the crash differently.

On Windows, the processor's event becomes a structured exception, a record with a code number, the address of the instruction and :term[extra data]{id=extra-data}. The system then asks each active function, innermost first, whether it wants to handle the record. A function that wants to handle it has written a `__try` block with an `__except` filter. The filter is a function that receives the record and answers: handle it, search further, or continue the program. This mechanism is **SEH** (structured exception handling): the way Windows delivers a hardware exception as a record to the filters of the active functions.

If the filter says "handle it", the system cuts the stack back to that function and runs the `__except` block. Everything between the crash and the block is left; the function that wrote the block continues, and the crashed code never resumes. That is exactly the control flow a guard needs.

On POSIX the system interrupts the thread and calls a signal handler, a function that the program registered for a signal number. The handler runs on the thread that crashed, on top of its stack. It may not return into a crashed instruction, because the instruction would crash again. So a guard has to leave the handler in another way: it jumps back to a place it saved earlier. C offers two functions for that, and Strata's POSIX guard uses them.

The pair **`sigsetjmp`/`siglongjmp`** saves a place in a function and later jumps back to it from anywhere below, discarding the stack between without running its :term[destructors]{id=destructor}.

`sigsetjmp` saves the processor's registers, including the stack pointer, in a buffer and returns 0. A later `siglongjmp` with that buffer restores the registers, and execution continues as if `sigsetjmp` had returned a second time, now with a value that the caller chose, here 1. The code after `sigsetjmp` tells the two returns apart by the value.

The stack overflow problem returns: a handler cannot run on a full stack. The remedy is the **alternate signal stack**, a block of memory that a thread registers with `sigaltstack` so that the system runs the thread's signal handlers on it instead of on the thread's own stack. Strata gives every thread that makes guarded calls one, 64 KiB, allocated at the thread's first guarded call and never freed, because it must stay valid for the life of the thread.

Windows has the same problem and another remedy, the **stack guarantee**: a number of bytes that a thread keeps free below the guard page of its stack. With these bytes the system can still dispatch a stack overflow exception. Strata asks for 32 KiB. The system first stores the processor's whole register state on that remainder, and on processors with very wide vector registers that state alone takes several KiB.

## The map

Only one class does the work, in two halves, and only one caller uses it. The first diagram shows who calls whom; the second follows one crash through both systems.

```mermaid caption="The script system calls a module through one function, which runs the call under the guard. Each platform has its own half of the guard." alt="Boxes from top to bottom: the script system and the editor, the module call function, the guard, then two platform halves, and the module's script code at the bottom."
flowchart TD
    Editor["EditorContext: stops play mode, posts the toast"] --> System["ScriptSystem / ScriptEngine"]
    System --> Call["ScriptModule::Call"]
    Call --> Guard["CrashGuard::Invoke (Core)"]
    Guard --> Win["WindowsCrashGuard.cpp: __try, __except"]
    Guard --> Pos["PosixCrashGuard.cpp: sigsetjmp, handler"]
    Win --> Code["script code in the module"]
    Pos --> Code
    Call -. "records the fault, returns Faulted" .-> System
```

`CrashGuard` and the `Symbolizer` (which names the :term[stack frames]{id=stack-frame} of a crash, the subject of [Symbolization](symbolization.md)) are classes of the Core layer, declared in `Strata/src/Strata/Core/CrashGuard.h` and `Strata/src/Strata/Core/Symbolizer.h`. Their implementations live in `Strata/src/Platform/Windows/` and `Strata/src/Platform/Posix/`, the same seam that [Platform](../core/platform.md) describes. Only `ScriptModule` calls `CrashGuard::Invoke`. Every call into a script module passes through `ScriptModule`, so every call is guarded, and nothing else in the engine needs to know that guards exist.

```mermaid caption="One crash on Windows and on POSIX. Both end with the guarded call returning false; the module is faulted and the exits on the right are not contained." alt="Two columns. Windows: the instruction crashes, the system calls the filter, the stack is cut back, the call returns false. POSIX: the instruction crashes, the handler runs on the alternate stack, the handler jumps back, the call returns false. Below both: the fault is recorded and the module is faulted. A separate box lists the exits that no guard catches."
flowchart TD
    subgraph W["Windows"]
        W1["instruction faults"] --> W2["system calls the filter"]
        W2 --> W3["filter accepts: unwind to the except block"]
        W3 --> W4["Invoke returns false"]
    end
    subgraph P["POSIX"]
        P1["instruction faults"] --> P2["handler runs on the alternate stack"]
        P2 --> P3["handler jumps back into Invoke"]
        P3 --> P4["Invoke returns false"]
    end
    W4 --> R["the fault is recorded: module is faulted, play stops"]
    P4 --> R
    X["not contained: fast-fail exits, abort on POSIX, a corrupted heap with its locks held, exit"]
```

## The contract

The class is **CrashGuard**: it has one function, `Invoke`, which runs another function and tells the caller whether that function crashed.

The contract has four parts: what the guard contains, what it does not, what a crash leaves behind, and what a caller must do.

First, what the guard contains. `Invoke` runs a function. If the function raises an access violation, an illegal instruction, an integer division by zero or a stack overflow, or if a C++ exception escapes it, execution resumes at the `Invoke` call. The call returns false and fills a `CrashInfo` with a description, the code (a Windows exception code or a POSIX signal number) and the address of the instruction. On Windows x64 it also holds the return addresses of the callers, and on Windows `abort()` in a module built with the static :term[C runtime]{id=crt} is contained too, as the real code below shows.

Second, what the guard does not contain. A fast-fail termination on Windows (a buffer overflow check, an invalid argument that the :term[C runtime]{id=crt} rejects, heap corruption that the system detects) ends the process without asking any filter. On POSIX `abort()` ends the process, because the C library also calls it on heap corruption while it holds the :term[allocator's]{id=allocator} locks. Anything that ends the process directly, such as `exit`, `_exit`, `TerminateProcess` or `SIGKILL`, goes through as well.

Third, what a crash leaves behind. Destructors of the objects in the crashed frames do not run, so the guarded code may leak. A crash inside the allocator can leave it locked, and the guarded thread then blocks at its next allocation. A stray write into engine memory is not detected at all: the guard sees only the crash, and a script that damages engine data and crashes later may fault far away from the cause.

Fourth, what a caller must do. Guards may be nested and belong to one thread. The caller must treat the module as not usable after a fault. And code that replaces the signal handlers later, such as a crash reporter, must be installed before the first guarded call, or crashes are no longer contained.

:::rule
Every call into module code goes through `ScriptModule`, and the engine reads module memory only inside guarded calls. The reason follows from the contract: only guarded code may crash, so only guarded code may touch what the module owns. The rule stands in the Scripting section of the engine's developer guide, and [Loading](loading.md) shows `ScriptModule`.
:::

The module state the contract leads to has a name, and the engine keeps it in `ScriptModule`.

A **fault** is the record that `ScriptModule` stores when a guarded call crashes. A module with a fault is faulted: it is never called again, and its script instances stay idle until a rebuild or `script.reload` loads the module again and clears the fault.

The engine keeps running because nothing else has to change. The instances of the faulted module are abandoned, and their memory is leaked on purpose, since destroying them would run their destructors in a module whose state nobody can trust.

## A toy version

The sketch below is a toy guard of about 90 lines. It saves and jumps with `setjmp` and `longjmp` on Windows, and with `sigsetjmp` and `siglongjmp` on Linux and macOS. On POSIX the system blocks a signal while its handler runs, and a plain `longjmp` out of the handler leaves it blocked, so the next fault of that kind would end the process. `sigsetjmp(buffer, 1)` saves the signal mask and `siglongjmp` restores it; the real guard repairs the mask on the fault path instead.

The toy differs from the real guard in two more ways. The faults are raised with `raise`, so that every run is the same; a real crash arrives from the processor but reaches the same handler. And the toy has no alternate stack, so a stack overflow is beyond it.

:::question
The sketch calls functions through pointers and writes calls such as `std::raise(` and `x.f(`. Read [C++ memory](../basics/cpp-memory.md) and [classes and calls](../basics/programming-3.md) first.
:::

Read the sketch for three things. The guard frame holds the jump buffer and links to the previous frame. The handler pops the frame before it jumps, and `Invoke` tells the two returns of `SAVE_PLACE` apart.

```cpp sketch="scripting-crash-containment-toy.cpp"
// A toy crash guard: a call runs under a guard, a signal ends it, and Invoke returns false. The faults are raised by
// std::raise so that every run behaves the same; a real fault arrives the same way, from the processor.

#include <csetjmp>
#include <csignal>
#include <cstdio>
#include <initializer_list>

// POSIX blocks a signal while its handler runs, and a plain longjmp out of the handler leaves it blocked, so the next
// fault of that kind would not reach the handler. sigsetjmp(buffer, 1) saves the signal mask and siglongjmp restores it.
#if defined(_WIN32)
#define SAVE_PLACE(buffer) setjmp(buffer)
#define JUMP_BACK(buffer) std::longjmp(buffer, 1)
using JumpBuffer = std::jmp_buf;
#else
#include <setjmp.h>
#define SAVE_PLACE(buffer) sigsetjmp(buffer, 1)
#define JUMP_BACK(buffer) siglongjmp(buffer, 1)
using JumpBuffer = sigjmp_buf;
#endif

namespace
{

	struct GuardFrame
	{
		JumpBuffer Place;
		GuardFrame* Previous = nullptr;
		volatile std::sig_atomic_t Signal = 0;
	};

	GuardFrame* s_CurrentFrame = nullptr;

	void SignalHandler(int signal)
	{
		std::signal(signal, SignalHandler); // Windows resets the handler before it runs
		GuardFrame* frame = s_CurrentFrame;
		if (!frame)
		{
			std::signal(signal, SIG_DFL);
			std::raise(signal);
			return;
		}
		frame->Signal = signal;
		s_CurrentFrame = frame->Previous;
		JUMP_BACK(frame->Place);
	}

	struct Noisy
	{
		~Noisy() { std::printf("  destructor ran\n"); }
	};

	void Healthy() { std::printf("  healthy call\n"); }

	void Crashing()
	{
		const Noisy noisy;
		std::raise(SIGSEGV);
		std::printf("  never printed\n");
	}

	void Dividing() { std::raise(SIGFPE); }

	bool Invoke(void (*function)())
	{
		GuardFrame frame;
		frame.Previous = s_CurrentFrame;
		if (SAVE_PLACE(frame.Place) == 0)
		{
			s_CurrentFrame = &frame;
			function();
			s_CurrentFrame = frame.Previous;
			return true;
		}
		std::printf("  contained: %s\n", frame.Signal == SIGSEGV ? "memory fault" : "arithmetic fault");
		return false;
	}

	void Nested()
	{
		const bool inner = Invoke(Dividing);
		std::printf("  outer continues, inner returned %s\n", inner ? "true" : "false");
	}

}

int main()
{
	std::signal(SIGSEGV, SignalHandler);
	std::signal(SIGFPE, SignalHandler);

	for (void (*function)() : { Healthy, Crashing, Crashing, Nested })
		std::printf("returned %s\n", Invoke(function) ? "true" : "false");
	return 0;
}
```

```text output-of="scripting-crash-containment-toy.cpp"
  healthy call
returned true
  contained: memory fault
returned false
  contained: memory fault
returned false
  contained: arithmetic fault
  outer continues, inner returned false
returned true
```

1. **Lines 9-20:** `SAVE_PLACE` and `JUMP_BACK` are `setjmp` and `longjmp` on Windows, and `sigsetjmp` and `siglongjmp` elsewhere, which also restore the signal mask.
2. **Lines 25-30:** the guard frame holds the jump buffer and a link to the guard that was active before it, so guards nest.
3. **Lines 44-46:** the handler records the signal, pops the frame so that a second crash finds the previous guard, and jumps.
4. **Lines 58-60:** the destructor of `noisy` does not run and the last line does not print, because the jump skipped both.
5. **Line 69:** `SAVE_PLACE` returns 0 on the way in and 1 after the jump, so the code after the `if` is the fault path.

The output shows the contract in miniature. A healthy call returns true. A crashing call returns false, and the second crash is contained too: the handler registered itself again, which Windows needs, and on POSIX the jump restored the signal mask. In the nested case the inner guard catches the division, and the outer function continues and returns true.

## The real code

The real guard has the toy's shape and spends its lines on what the toy skipped. The order below follows the data: the Windows half, the POSIX half, the module's own abort handling, and the caller.

### Windows: the filter and the stack

The filter chooses which exceptions the guard handles. For every code it does not know it answers "continue search", so codes that other tools raise on purpose, such as a debugger's messages, pass through. It accepts 19 codes: 17 hardware exceptions (access violation, in-page error, array bounds, data alignment, illegal and privileged instruction, integer divide and overflow, seven floating-point errors, stack overflow and :term[breakpoint]{id=breakpoint}) and two software codes. The first is MSVC's C++ exception, `0xE06D7363`. The second is the abort code of the software development kit (:term[SDK]{id=sdk}), `0xE0535441`; read its bytes `0x53`, `0x54` and `0x41` as the letters S, T and A.

An access violation also carries the kind of access and the address. `DescribeFault` turns kind 0 into "reading", kind 8 into "executing" and anything else into "writing". The filter walks the stack for the report only on x64, and not after a stack overflow, since it runs on what the guard page left.

The `__try` statement itself sits in its own function. Three of its lines matter: the protected call, the filter, and the repair after a stack overflow.

```cpp src="Strata/src/Platform/Windows/WindowsCrashGuard.cpp#L146-L159"
bool InvokeWithSEH(CrashGuard::GuardedFunction function, void* userData, FaultRecord* record)
{
	__try
	{
		function(userData);
		return true;
	}
	__except (FilterException(GetExceptionInformation(), record))
	{
		if (record->Code == EXCEPTION_STACK_OVERFLOW)
			_resetstkoflw(); // Restore the guard page so a later overflow is caught again
		return false;
	}
}
```

1. **Line 148:** the protected region; a crash anywhere below this call lands in the filter at line 153.
2. **Line 153:** the filter receives the exception pointers and fills a plain record without allocating, because after a stack overflow almost no stack is left.
3. **Line 156:** `_resetstkoflw` restores the guard page, which the overflow consumed, so that the next overflow is detected again instead of running off the end of the stack.

The function is separate because of a :term[compiler]{id=compiler} rule. MSVC refuses a function that contains both `__try` and an object with a destructor (error C2712), and `Invoke` builds strings. So `Invoke` calls this function, which holds only plain data, and then formats the description from the record.

The first guarded call on a thread asks for 32 KiB, which is 32768 bytes, with `SetThreadStackGuarantee`. It never lowers a larger request that the thread made earlier, and a failed request logs a warning while the call continues.

### POSIX: the handler and the jump

The POSIX half installs one handler for six signals: `SIGSEGV`, `SIGBUS`, `SIGFPE`, `SIGILL`, `SIGTRAP` and `SIGABRT`. The first `Invoke` does it once for the whole process, with the flag that asks for the alternate stack. Each thread's first call also gives that thread its 64 KiB alternate stack.

The handler decides whether the signal belongs to a guard.

```cpp src="Strata/src/Platform/Posix/PosixCrashGuard.cpp#L239-L260"
void SignalHandler(int signal, siginfo_t* info, void* context)
{
	GuardFrame* frame = t_CurrentFrame;
	if (frame && !IsSentByAnotherProcess(signal, info))
	{
		if (signal == SIGABRT)
		{
			AbortFromGuardedCode(info, context);
			return;
		}
		frame->Signal = signal;
		frame->FaultAddress = info ? info->si_addr : nullptr;
		frame->InstructionAddress = GetInstructionAddress(context);
		t_CurrentFrame = frame->Previous;
#if defined(ST_PLATFORM_MACOS)
		if (ResumeAfterReturn(context, frame))
			return;
#endif
		siglongjmp(frame->JumpBuffer, 1);
	}
	ForwardToPreviousHandler(signal, info, context);
}
```

1. **Line 242:** the signal counts only if a guard is active on this thread and the signal did not come from another process. A `kill` sent from a terminal is not a crash of the script, and the guard leaves it alone.
2. **Lines 244-247:** `SIGABRT` is reported and never contained; the next section says why.
3. **Lines 249-252:** the handler records the signal, the address and the instruction, then pops the frame, so a second crash would find the previous guard.
4. **Line 257:** `siglongjmp` leaves the handler. Lines 253-256 are the macOS variant, where the handler returns into a small recovery routine, because only a return clears the kernel's "on the alternate stack" flag.

Every signal that no guard owns goes to `ForwardToPreviousHandler`. A handler installed before the guard is called directly. If there was none, the default action is restored: for a stray crash outside guarded calls, the process ends as it would have without Strata.

`Invoke` is the function the handler jumps back into.

```cpp src="Strata/src/Platform/Posix/PosixCrashGuard.cpp#L348-L402"
bool CrashGuard::Invoke(GuardedFunction function, void* userData, CrashInfo* outInfo)
{
	std::call_once(s_InstallOnce, InstallHandlers);
	EnsureAlternateStack();

	GuardFrame frame;
	frame.Previous = t_CurrentFrame;
#if defined(ST_PLATFORM_MACOS)
	frame.RecoveryStackTop = t_RecoveryStackTop;
#endif
	if (sigsetjmp(frame.JumpBuffer, 0) == 0)
	{
		t_CurrentFrame = &frame;
		const bool returned = CallCatchingExceptions(function, userData, frame);
		t_CurrentFrame = frame.Previous;
		if (returned)
			return true;

		// An escaping exception is a fault of the guarded code, as on Windows (where it is a structured exception).
		if (outInfo)
		{
			outInfo->Description = "Unhandled C++ exception";
			outInfo->Code = 0;
			outInfo->Address = 0;
		}
		return false;
	}

	// Arrived here after a fault (the handler already popped the frame). Where the handler jumped out, it ran with the
	// delivered signal blocked and the mask was not restored: unblock it, or the next fault of the same kind could not
	// be delivered (the kernel kills a process whose fault signal is blocked). Nested guards are no different: each
	// fault path undoes the block of the signal it handled.
	sigset_t delivered;
	sigemptyset(&delivered);
	sigaddset(&delivered, frame.Signal);
	pthread_sigmask(SIG_UNBLOCK, &delivered, nullptr);

	// The thread must have left its alternate signal stack, or the next fault could not be contained (see above).
	stack_t signalStack = {};
	if (sigaltstack(nullptr, &signalStack) == 0 && (signalStack.ss_flags & SS_ONSTACK) != 0)
		ST_CORE_ERROR("CrashGuard: this thread still counts as running on its alternate signal stack after a contained fault; a stack overflow on it can no longer be contained");

	if (outInfo)
	{
		outInfo->Description = DescribeSignal(frame.Signal, frame.FaultAddress);
		outInfo->Code = static_cast<uint64_t>(frame.Signal);
		// The instruction, as on Windows (the accessed address is in the description); without it, the accessed address.
		const uint64_t instruction = frame.InstructionAddress;
		outInfo->Address = instruction != 0 ? instruction : reinterpret_cast<uint64_t>(frame.FaultAddress);
		outInfo->Stack.clear();
		if (instruction != 0)
			outInfo->Stack.push_back(instruction);
	}
	return false;
}
```

1. **Line 358:** `sigsetjmp` with 0 as the second argument does not save the signal mask. Saving it would cost a system call on every script call, and the fault path repairs the mask instead.
2. **Lines 361-362:** the call runs inside `CallCatchingExceptions`, a separate function with a `try`, because C++ exceptions and `sigsetjmp` do not mix in one frame. An exception that escapes counts as a fault, as on Windows.
3. **Lines 380-383:** the handler ran with the delivered signal blocked, and the jump did not restore the mask. Without this step, the next crash of the same kind could not be delivered, and the kernel ends a process whose crash signal is blocked.
4. **Lines 387-388:** a sanity check that the thread has left the alternate stack. If it has not, the next stack overflow could not be contained, so the guard logs an error instead of hiding it.

The toy registers its handler again because Windows resets it, and on POSIX it lets `siglongjmp` restore the mask, at the cost of a system call on every guarded call. The real guard solves both problems for its platform, in a handler that must also run on a full stack.

### Abort: why the module needs its own handler

On POSIX, `abort()` is not contained. The C library also calls it on heap corruption while it holds allocator locks, which a jump out of the handler would never release. The thread would then block at its next allocation with nothing in the log. The guard cannot tell a failed `assert()` from that case, so it writes one line to :term[standard error]{id=standard-error} with a call that is safe inside a handler. The process then ends the way `abort()` ends it, with :term[exit status]{id=exit-code} 134, which is 128 plus signal number 6.

On Windows the story differs because `abort()` is the C runtime's, and a module may carry its own copy. The SDK's entry file, which the build adds to every module, contains the fix.

```cpp src="StrataScriptCore/Source/ScriptModuleEntry.cpp#L47-L68"
void __cdecl HandleAbort(int)
{
	// The C runtime resets the handler before calling it; later aborts are handled the same way.
	std::signal(SIGABRT, &HandleAbort);
	RaiseException(ST_SCRIPT_ABORT_EXCEPTION_CODE, EXCEPTION_NONCONTINUABLE, 0, nullptr);
}

// Set up while the module's C runtime initializes, before any of the module's own static objects.
class AbortContainment
{
public:
	AbortContainment()
	{
		// assert() reports to stderr instead of a message box that would block, and abort() writes no report of its
		// own (a dialog in Debug builds) before calling the handler.
		_set_error_mode(_OUT_TO_STDERR);
		_set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
		std::signal(SIGABRT, &HandleAbort);
	}
};

const AbortContainment s_AbortContainment;
```

1. **Lines 47-52:** the handler for `SIGABRT`. It registers itself again, because the :term[runtime]{id=runtime} resets it, and raises the exception `ST_SCRIPT_ABORT_EXCEPTION_CODE` so that the filter above accepts it.
2. **Lines 62-63:** `assert` writes to standard error instead of opening a message box that would block the frame, and `abort()` writes no report of its own.
3. **Line 68:** a static object whose :term[constructor]{id=constructor} installs the handler. The file begins with `#pragma init_seg(lib)`, which constructs it before the module's own static objects. So even an `abort()` in the startup code of a static object is contained, and the load fails instead of ending the editor.

All of this is compiled only on Windows with MSVC and the static C runtime (`!defined(_DLL)`). With the shared runtime (`/MD`), the abort handling belongs to every user of that runtime, so the SDK leaves it alone and an `abort()` ends the process. That is the rule: Windows modules use the static C runtime if they want `abort()` contained.

### The caller: recording the fault

`ScriptModule::Call` is the only caller. It returns early for a faulted module, runs the body inside the guard, and turns a false return into a recorded fault.

```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L313-L327"
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
```

1. **Lines 316-317:** a call scope tells the watchdog that a script call started; the :term[lambda]{id=lambda} that runs the body is guarded.
2. **Lines 326-327:** the crash is recorded, which marks the module as faulted and logs it, and the caller gets `Faulted` instead of a value. Nothing is thrown.

`RecordFault` logs the line "Script module ... crashed in Class.Method on entity ...: description. The module is disabled until it is reloaded." and keeps the first fault. The symbol work that names the file and line is [Symbolization](symbolization.md)'s subject and runs later on a job, because reading debug files is slow.

## Exceptions against crashes

A C++ exception is not a crash. A script that throws has done something that C++ allows, and the SDK expects it. Every :term[callback]{id=callback} that the engine calls goes through the SDK's function `InvokeScript`, which catches the exception and reports it to the host as plain data. No C++ exception crosses the boundary between module and engine, because only plain data crosses the C interface, and the engine itself does not throw.

The policy has two sizes. An exception disables one instance: `ScriptSystem` marks that script's instance as disabled and logs "threw an exception" with the callback's name. The entity's other scripts and all other entities continue. A crash faults the module: every instance stays idle, and in the editor play mode stops.

The sizes differ because the evidence differs. A thrown exception leaves the stack in order, so the state of the instance is known. A crash cuts call frames off and may leave locks held and memory half written, so nothing of the module can be trusted.

:::example
Take a copy of the `Coin` script from the `ThirdPerson` sample, whose `OnUpdate` spins and bobs the coin. Make the break in the copy, never in the sample itself.

Version one adds `volatile int* pointer = nullptr; *pointer = 42;` at the top of `OnUpdate`, so on the first frame of play the processor reports a write to address 0. On Windows the filter accepts it, `Invoke` returns false, and the Console shows an error line of the form below. Its description is "Access violation writing address 0x0000000000000000" followed by "at" and the address of the instruction. Then the editor stops play mode, posts a toast titled "Script crash: play mode stopped" and the toast's **Show Problems** button opens the panel that lists the place and the stack once they are named. Every coin in the scene stops being updated.

Version two replaces those lines with `throw std::runtime_error("coin broke");`. The SDK catches it, the engine logs that the script threw in `OnUpdate` and is disabled, and play continues: that coin stops spinning, all the others keep spinning, and no toast appears.

The line of version one has this form, where the parts in angle brackets depend on the scene and the build. The part from "at" to the colon stands there only when the place is already named; otherwise a second line naming the place follows once the job has found it:

```text
Script crash in Coin::OnUpdate on entity '<name>' (<id>) at <file and line>: <description>. Play mode stopped; fix the script and rebuild (script.build) or reload it (script.reload)
```

One fault, one cut-off module, against one instance out. After the null write, `script.reload` loads the module again and clears the fault. After the exception, that one instance stays disabled.
:::

## The watchdog

Native code cannot be interrupted from outside. A script that loops forever holds the :term[main thread]{id=main-thread}, because the engine waits for each script call to return. The engine has one tool for this, and it is limited.

A **watchdog** is a thread that wakes at intervals and logs a script call that has run longer than a timeout; it cannot stop the call.

The watchdog is off by default. `ScriptEngine::SetWatchdogTimeout` enables it with a timeout, and zero disables it. Neither the editor nor the runtime calls it: only tests do. So in the editor an endless loop freezes the window, and the log stays silent.

When a host enables the watchdog, its thread wakes every quarter of the timeout, never faster than every millisecond and never slower than every 250 ms. Once per call, it logs "Script call ... has been running for ... ms; it may be stuck in an infinite loop". The call still runs until it returns, if it ever does.

The test with a timeout of 250 ms shows the numbers. By the code's arithmetic the wake-up interval is 62 ms and the first report of a slow call comes at 310 ms. In the test a call of 1500 ms is reported once and then completes without a fault. The exercises below compute more of these.

The rule for script authors follows. A script must never block: no loop that waits for something, no sleep, no wait on a lock. Native code cannot be interrupted, the watchdog cannot end it, and in the editor you would have to end the whole process from outside.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A child process for scripts | Web browsers run pages and extensions this way | Contains a corrupted heap, `abort()` and an endless loop, and a clean restart | A message for every call, data copied between processes, harder hot reload |
| A virtual machine that confines the script | Games that embed Lua; browsers that run WebAssembly | No native crash is possible, and a loop can be stopped | C++ scripts, native speed for heavy work, direct use of engine types |
| No containment | Most engines in the game itself | No guard code and no per-call cost | Work in the editor that you did not save, on every script crash |

## How it is tested

The cases live in four suites, and some start extra processes where an exit would end the test.

`Core.Platform` tests the guard alone with small functions. The cases check that:

- normal functions run, and access violations are contained;
- integer division by zero is contained on x64;
- stack overflows are contained again and again, also on other threads;
- guards nest, and the signal mask stays as it was.

On Linux and macOS, three cases start a helper process and read its exit status. A fault outside a guarded call goes to the handler installed before the guard. A signal that another process sends is not contained, and the helper ends with status 128 plus `SIGFPE`. A call of `abort()` ends with status 128 plus `SIGABRT` and the output line "called abort()". On Linux one more case checks that a thread that exits passes through a guarded call: the C library ends it with a special C++ exception that the guard must not swallow.

`Scripting.Faults` uses the `Faults` module of `StrataTests/Scripts/Faults/`, whose script class `Faulty` crashes on request in a chosen callback. The cases check that crashes are contained, that a crash in a nested call faults the module, that other scenes and engines keep working, and that reloading recovers. Another case checks that the watchdog reports a long call. `Scripting.Exceptions` checks the other half of the policy: an exception disables only the instance that threw. `Scripting.LoaderFaults` uses the `LoadFault` module, whose code crashes while the library loads, and checks that the load is refused.

The fault kinds the tests use depend on the platform. The list always holds a null write and a stack overflow, adds `Abort`, `Assert`, `Terminate` and `TerminateFromNoexcept` only on Windows, and omits `DivideByZero` on `ARM64`, where integer division gives 0. Run one suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scripting.Faults
```

The command runs only the cases of that suite, and every case must pass on every platform that runs it.

## Changing it safely

Extension points are few. A new platform adds its own half of `CrashGuard::Invoke` and keeps the contract in `CrashGuard.h`. A new contained code on Windows is one more case in the filter and in `DescribeFault`.

Rules that apply, with their reasons:

- **Never insert code between the filter and the copy of the record that can crash.** On Windows a crash in the filter nests on top of the one being handled. That is why the filter fills a plain record and stack walking is guarded by its own `__try`.
- **Wrap host functions in `HostCall`, and start them with `ResolveContext`.** A module that crashed may still be running further up the stack, and it must get nothing from the engine. Host functions report misuse and return a failure value; they never assert.
- **Destroy entities through `ScriptSystem::DestroyEntity`.** Entity destruction goes through this function so that no script code runs while the engine state it uses is being torn down.
- **Do not widen the guard to catch more.** A guard that continues after a heap crash would trade a clear failure for a hang. When a new exit looks as if it can be contained, ask first what the process holds when it happens.

Checks to pass: the `Core.Platform` guard cases and `Scripting.Faults` on every platform you can run, with warnings treated as errors.

## Summary

- A guarded call returns false instead of ending the process for hardware exceptions and escaping C++ exceptions; the engine records a fault, marks the module as not usable until a reload, and continues.
- Windows resumes through an `__except` filter that cuts the stack back; POSIX resumes with a signal handler on the alternate stack that jumps back with `siglongjmp`. Each needs its own remedy for a full stack: the stack guarantee and the alternate stack.
- Containing in the same process costs a few instructions per call; a child process and a virtual machine contain more and cost more.
- A thrown exception disables one instance; a crash faults the whole module and leaks its instances on purpose.
- The watchdog is off by default and only logs, and no editor or runtime enables it, so a script must never block.

## Check yourself

1. A script divides an integer by zero on an `ARM64` Linux machine. What happens, and why does the engine's fault test list leave this case out there?

   :::answer{tests="classify-fault"}
   Nothing crashes: the integer division instruction on `ARM64` returns 0 and no signal is raised, so there is nothing to contain. The test list leaves `DivideByZero` out on `ARM64` because the test would wait for a crash that never comes. On x64 the instruction traps and the guard contains it.
   :::

2. A script calls `abort()` on Linux, and another script's module on Windows is built with the shared C runtime (`/MD`) and calls `abort()`. Which of these is contained? Choose: (a) both, (b) neither, (c) only the Linux one, (d) only the Windows one.

   :::answer{tests="classify-fault"}
   (b), neither. On Linux the guard reports on standard error and the process ends with status 134, because the C library also calls `abort()` on heap corruption with locks held. On Windows with `/MD` the SDK leaves the abort handling alone, since it belongs to every user of the shared runtime, so `abort()` ends the process. (a) and (d) would need the static runtime; (c) is wrong because POSIX contains no call of `abort()`.
   :::

3. After a stack overflow on Windows, which call restores the guard page, and what happens if the guard omits it? Which Linux feature does the same job of keeping the next overflow contained?

   :::answer{tests="resume-after-fault"}
   `_resetstkoflw` restores it. Without it the next overflow in that thread finds no guard page, runs past the end of the stack and ends the process. On Linux the alternate signal stack lets the handler run after an overflow, and the handler's jump back lets the kernel see the thread as off that stack. Each system needs one step so that the second overflow is contained as well as the first.
   :::

4. A script throws an exception in `OnUpdate` on one coin of fifty. Predict what the other coins, the editor and play mode do, and what changes if the script writes through a null pointer instead.

   :::answer{tests="exception-or-crash"}
   With the exception, the SDK catches it, the engine disables that one instance and logs the message; the other 49 coins keep spinning, play continues and no toast appears. With the null write, the module is faulted: all 50 coins stop being called, play mode stops, a toast offers **Show Problems**, and the module is not usable until `script.reload` or a rebuild.
   :::

5. Design review: a teammate proposes running scripts in a child process, since it contains more. Give two costs and one thing it gains over the guard, and say which gain Strata values less than the costs.

   :::answer{tests="compare-approaches"}
   Costs: every script call becomes a message between processes, and all data the script reads must be copied or shared. The process also adds a start-up cost and makes hot reload harder. Gain: it contains a corrupted heap, `abort()` on every platform and an endless loop, since the engine can end the process. Strata keeps the cost of each call small and names the exits that remain outside the guard.
   :::

6. The editor has no watchdog. What does a script that contains `while (true) {}` do, and what does the log show?

:::answer{tests="watchdog-limits"}
The main thread stays in the script call, so the editor window stops responding. The log shows nothing, because nothing calls `SetWatchdogTimeout` in the editor. Even with the watchdog on, it would only log "may be stuck in an infinite loop"; native code cannot be interrupted, so you would end the process from outside.
:::

## Exercises

1. **Basic.** Make a table with three columns: contained or not, what the engine does, and the state afterwards. Fill it for a null write, a stack overflow, and `abort()` in a Windows module with the static runtime. Then add `abort()` on macOS and a buffer overflow check (a fast fail) on Windows. Add `exit(1)` in a script, a C++ exception thrown through a destructor marked `noexcept`, and an endless loop.

   :::answer[Worked solution]{tests="classify-fault"}
   - Null write: contained; `Invoke` returns false; module faulted, play stops.
   - Stack overflow: contained (stack guarantee on Windows, alternate stack on POSIX); same state.
   - `abort()`, static runtime on Windows: contained through the abort exception; module faulted.
   - `abort()` on macOS: not contained; a report on standard error and the process ends with status 134.
   - Fast fail on Windows: not contained; the process ends without any filter.
   - `exit(1)`: not contained; the process ends at once and nothing else runs.
   - Exception out of a `noexcept` function: `std::terminate` calls `abort()`, so on Windows with the static runtime it is contained, with the C++ runtime keeping the abandoned exception; elsewhere the process ends.
   - Endless loop: not contained; the editor freezes and, without a watchdog, nothing is logged.
   :::

2. **Medium.** The watchdog wakes at a quarter of the timeout, clamped between 1 and 250 ms. Write a program that prints, for the timeouts 4, 100, 250, 1000 and 4000 ms, the interval and the time of the first report of a call that never returns.

   :::answer[Worked solution]{tests="watchdog-limits" solution="sketches/scripting-crash-containment-watchdog.cpp"}
   The program divides the timeout by 4, clamps it, and counts the wake-ups needed to reach the timeout, rounding up.

   ```cpp sketch="scripting-crash-containment-watchdog.cpp"
   // When does the watchdog report a call that never returns? It wakes at a fixed interval and reports at the first
   // wake-up at or after the timeout. The interval is a quarter of the timeout, kept between 1 and 250 milliseconds.

   #include <algorithm>
   #include <chrono>
   #include <cstdio>
   #include <initializer_list>

   int main()
   {
   	using std::chrono::milliseconds;

   	std::printf("timeout  interval  first report\n");
   	for (const int timeoutCount : { 4, 100, 250, 1000, 4000 })
   	{
   		const milliseconds timeout(timeoutCount);
   		const milliseconds interval = std::clamp(timeout / 4, milliseconds(1), milliseconds(250));
   		const int wakeUps = static_cast<int>((timeout + interval - milliseconds(1)) / interval);
   		const milliseconds firstReport = wakeUps * interval;
   		std::printf("%5d    %5d     %6d\n", timeoutCount, static_cast<int>(interval.count()), static_cast<int>(firstReport.count()));
   	}
   	return 0;
   }
   ```

   ```text output-of="scripting-crash-containment-watchdog.cpp"
   timeout  interval  first report
       4        1          4
     100       25        100
     250       62        310
    1000      250       1000
    4000      250       4000
   ```

   1. **Line 17:** the quarter of the timeout, clamped between 1 and 250 ms.
   2. **Line 18:** adding the interval minus 1 ms before the division rounds the count of wake-ups up.

   For 250 ms the interval is 62 ms because the division of whole milliseconds drops the fraction; the fifth wake-up at 310 ms is the first at or after 250. The clamp matters at both ends: 4 ms gives exactly the floor of 1 ms, and 4000 ms would give 1000 ms but is held to 250 ms.
   :::

3. **Hard.** Trace it yourself: break `Coin` as in the example and follow the null write with a debugger on a source build. Name the file and function where the Windows filter accepts it, where `Invoke` returns false, and where the Linux handler and its jump back are; then name the function that records the fault.

:::answer[Worked solution]{tests="classify-fault,resume-after-fault"}
On Windows, break on the first-chance access violation. The filter is `FilterException` in `Strata/src/Platform/Windows/WindowsCrashGuard.cpp`; it returns the value that selects the `__except` block of `InvokeWithSEH`, which returns false to `CrashGuard::Invoke`. On Linux, set a breakpoint in `SignalHandler` in `Strata/src/Platform/Posix/PosixCrashGuard.cpp`: it runs on the alternate stack, records the signal and calls `siglongjmp`, and execution reappears in `CrashGuard::Invoke` after `sigsetjmp`, where the signal is allowed again. `ScriptModule::Call` in `Strata/src/Strata/Scripting/ScriptModule.cpp` then calls `RecordFault` and returns `Faulted`.
:::

## Where it lives in Strata

- `Strata/src/Strata/Core/CrashGuard.h`: the contract, `CrashInfo`, the abort code and the stack guarantee size.
- `Strata/src/Platform/Windows/WindowsCrashGuard.cpp` and `Strata/src/Platform/Posix/PosixCrashGuard.cpp`: the two halves.
- `StrataScriptCore/Source/ScriptModuleEntry.cpp`: abort containment in modules; `StrataScriptCore/Include/StrataScript/Script.h`: the catch-all `InvokeScript`.
- `Strata/src/Strata/Scripting/ScriptModule.cpp`, `ScriptEngine.h` and `ScriptWatchdog.cpp`: the call, the fault record and the watchdog.
- `StrataEditor/src/Editor/EditorContext.cpp`: the play-mode stop, the Console line and the toast.
- Tests: `Core.Platform`, `Scripting.Faults`, `Scripting.Exceptions`, `Scripting.LoaderFaults`; modules in `StrataTests/Scripts/Faults/` and `StrataTests/Scripts/LoadFault/`.
- Commands: `script.reload`, `script.build`.

## Further reading

- Microsoft's documentation on structured exception handling and the `__try` statement: what the filter returns and how unwinding works (intermediate).
- The POSIX manual pages for `sigaction`, `sigaltstack` and `sigsetjmp`: the signal mask and the alternate stack (intermediate).
- The Chromium project's documents on its multi-process architecture: why a browser isolates pages in processes (beginner).
- The WebAssembly specification's chapter on its security model: how a virtual machine bounds memory access (advanced).

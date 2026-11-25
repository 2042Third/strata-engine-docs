---
id: core/conventions
title: "Ownership, errors and logging in Strata"
description: "Who owns an object in Strata, what the code does when something goes wrong, what it writes to the log, and how it looks, with the reason for each rule."
kind: internals
size: L
tracks: [E]
needs: [core/first-change, basics/cpp-modern]
time: 75
learn:
  - id: ownership
    text: choose between Scope, Ref and a borrowed pointer or reference for an object, and say who frees it
  - id: failure-kinds
    text: choose between an assert, a verify and a returned error for a given failure, and give the reason
  - id: dist-assert
    text: predict what a Dist build does with an assert whose condition has a side effect, and fix it
  - id: logging
    text: name the logger, the level and the macro for a message, and explain why a repeating error goes through a throttle
  - id: code-style
    text: write a name, a brace and an include as the engine's code style asks, and name the reason for each
since: 0.3.0
status: final
---

Every engine file in Strata follows the same rules about three questions: who owns an object and so frees it, what the code does when something goes wrong, and what it writes to the log. A fourth set of rules fixes how the code looks. This page teaches those rules with the reason for each, so that you can write a change that a reviewer accepts and read old code without surprise.

The page does not teach C++ itself. [C++ memory](../basics/cpp-memory.md) teaches smart pointers and lifetimes, and [Modern C++ as Strata uses it](../basics/cpp-modern.md) teaches exceptions. How the log reaches the disk, and how to read it while you debug, belong to [Debugging the engine](debugging.md).

## The problem and how engines solve it

A program is a long conversation with the computer's memory, with files and with other programs, and each part of it can fail. Three questions come up in every line of such a program, and an engine has to answer each one the same way everywhere. If every programmer chooses alone, the code becomes a pile of habits that no one can read.

### Who frees the object?

Every object that a program makes with `new` takes memory that someone must give back. Old C++ code gave it back by hand with `delete`. A person forgets one `delete`, and the program leaks memory. A person writes one too many, and the program frees the same memory twice and crashes much later, far from the cause.

Other languages remove the question: a garbage collector finds objects that nothing uses and frees them when it likes. That costs a pause at a time the program does not choose, and a game cannot afford a pause in the middle of a frame. C++ offers a third way, the one [C++ memory](../basics/cpp-memory.md) teaches: tie the object's life to a variable, so that the end of the variable's scope frees the object. The engine's part is the choice of which variable. One name for the owner, one for shared ownership, and a plain pointer for a user who does not own: three words that tell the reader how long an object lives.

### What happens when something goes wrong?

Two very different things go wrong in a program. In the first, the programmer made a mistake: a function was called with an index past the end of an array. No input from a person or a file can make that call legal. The code cannot repair such a state, because the state should never have existed. The best answer is to stop at once, loudly, with the file and the line, while the cause is still near.

In the second, the world was not as the program hoped: a file is missing, a project file holds broken text, a :term[graphics card]{id=gpu} runs out of memory. A good program expects this. The right answer is to report the failure to the caller, which can show a message to the person and carry on.

Engines solve this with four tools. Exceptions leave the failing function at once, through every function that called it; they cost little while nothing fails, but they hide the paths of failure from the reader. Error codes return a value that the caller must check, and a caller can forget. A stop-at-once check, an **assertion**, ends the program on a programmer error, and some engines remove it from the shipped build because it costs time in every call. Strata keeps exceptions out of its own code, returns values for failures of the world, and stops on programmer errors with checks of two kinds.

### What does the program say about itself?

A game that runs on a stranger's computer gives you no way to watch it. When it fails, the log is the only evidence. A log needs rules: how serious a message is, which part of the program wrote it, where it goes, and how often it may repeat. The simplest log is a call to `printf`, which has no severity and no source and cannot be disabled.

Engines therefore give each message a **log level**, which says how serious it is.

A message goes through a named **logger**, which says where it came from.

The logger hands the message to one or more **sinks**, the places where messages end, such as the console and a file.

Logging has two dangers. A message in a loop that runs every frame writes 60 lines a second, which hides the first line that mattered and costs time. And a message may carry a secret, such as an access token, into a file that the player then sends to a stranger for help.

### Why the style is a rule too

The last question looks small: how does the code look? The answer matters because a team that reads each other's code all day reads it faster when every file looks alike. A prefix on a member name tells the reader where a variable lives before the reader sees its declaration. Strata follows the style of the Hazel engine, and the rest of this page gives its rules and their reasons.

## The map

The rules live in a few files of `Strata/src/Strata/Core/`. The diagram shows who includes or calls whom. An arrow reads "uses".

```mermaid caption="The files that hold the rules: the base names and macros, the checks, the log and its writer thread, the throttle, the JSON helpers and the frame loop's catch." alt="A diagram. The checks file uses the base file and calls the failure handler. The handler, the throttle and the frame loop's catch use the log. The log hands messages to a background writer. The JSON helpers use the base file and return errors to their callers."
flowchart TD
	base["Base.h: Scope, Ref, ST_BIT, ST_ENABLE_ASSERTS"]
	checks["Assert.h: ST_CORE_ASSERT, ST_CORE_VERIFY"]
	handler["Assert.cpp: HandleAssertFailure"]
	log["Log.h and Log.cpp: three loggers, the macros"]
	writer["BackgroundLogSink: writer thread"]
	throttle["ErrorThrottle"]
	json["JsonUtils: Parse, Dump"]
	loop["Application::Run: the last catch"]
	checks --> base
	checks --> handler
	handler --> log
	throttle --> log
	loop --> log
	log --> writer
	json --> base
```

Five pieces own five jobs:

- `Base.h` owns the vocabulary: `Scope`, `Ref`, `WeakRef`, the flag operators and the :term[macro]{id=macro} that switches the asserts on.
- `Assert.h` and `Assert.cpp` own the two checks and what happens when one fails.
- `Log.h` and `Log.cpp` own the three loggers and their macros. The writer thread of `BackgroundLogSink` belongs to [Debugging the engine](debugging.md).
- `ErrorThrottle.h` owns the rule that a repeated error appears once.
- `JsonUtils.h` owns the catch for a third-party library that throws.

All of them run on whichever thread calls them. The loggers are safe from every thread, because the writer, not the caller, touches the console and the file. An `ErrorThrottle` is not, so each throttle belongs to one thread.

## The contract

Each rule below has a reason. A reviewer asks for the reason before the rule, and so does this page.

### Ownership

An **owner** is the one variable whose end of life frees an object. Strata has three ways to hold an object.

`Scope<T>` is the engine's name for a :term[unique pointer]{id=unique-pointer}: one owner, no copy, and the object dies with its owner; it is the default. `Ref<T>` is a :term[shared pointer]{id=shared-pointer}: several owners, and the object dies with the last one. A `Ref` carries a counter that every copy and every release updates, so it is for objects that have no single owner. A raw pointer or a reference is a borrower: it never frees, and it must not last longer than the owner. `Ref` and `Scope` are only other names for the standard types, so everything in [C++ memory](../basics/cpp-memory.md) applies to them.

:::rule
Pick the weakest tool that is true. A `Scope` says "this variable is the only owner", and a reader never has to search for other owners. Choosing `Ref` out of habit hides who frees the object, and it hides the moment of the freeing too. Both facts matter for threads, as the next paragraph shows.
:::

The moment of freeing is the cost of sharing. Whoever holds the last `Ref` runs the :term[destructor]{id=destructor}, on the thread and at the time they let go. Destroying a scene can take tens of milliseconds for a million entities, so `Scene::ReleaseInBackground` takes its `Ref<Scene>` by value, ends what must end on the main thread, and hands the rest to a background job. A :term[lambda]{id=lambda} that captures a `Ref` and runs on a worker thread has the same effect: if the lambda dies last, the object dies on the worker. Check who is last before you capture.

A registry owns what it makes. The module registry is the example: it keeps its modules in a vector of `Scope<EngineModule>` and hands out raw `EngineModule*` pointers, which stay valid until the registry's `Clear`. Callers use the pointer for the moment they need it and never store it for longer than the registry lives. A pointer from `Find` can be null, so the caller tests it.

Assets are the one place where the rule is "do not hold a `Ref`". A held `Ref` keeps an asset in memory, which defeats the engine's budget for assets. Code holds an `AssetHandle`, a unique number that names the asset, and asks for the asset in each frame that needs it. [Residency, eviction and pins](../assets/residency.md) teaches why.

### Errors

Strata sorts every failure into one of three kinds before it writes a line.

An assert checks something that only a programmer's mistake can break. The macro **`ST_CORE_ASSERT`** is the engine's assert (`ST_ASSERT` is the one for the editor and games): it exists in Debug and Release builds, and :term[Dist]{id=dist}, the shipping configuration, removes it. The macro **`ST_CORE_VERIFY`** (`ST_VERIFY` for applications) is a verify: the same check, kept in every build, Dist included. Use a verify when a wrong state would give wrong results with no sign of trouble, such as a registry used before the engine registered its modules. Both macros log the condition, the file and the line; then the handler decides to break in a debugger, to end the program or, in a test, to continue.

A **recoverable failure** is anything that real data or a real system can cause. Examples are a missing file, text that cannot be read as the data it should hold, and memory that a graphics card cannot give. Strata returns it: a `bool`, a `std::optional`, or a small result :term[struct]{id=struct}, and the function that found the failure writes one log line. It never asserts. The caller decides whether to try again, use a default, or tell the person.

:::rule
`ST_CORE_ASSERT` is compiled out of Dist, so its condition must have no side effects. If the condition calls a function that changes something, Debug runs it and Dist does not, and the two builds are two different programs. Put the call on its own line, keep its result in a variable, and assert on the variable.
:::

The macros are built for this. Each one is a `do { } while (false)` statement, so it works as one statement after an `if`. The failing branch has the attribute `[[unlikely]]`, which tells the :term[compiler]{id=compiler} to keep the common path short. Without `ST_ENABLE_ASSERTS`, the assert macros expand to `((void)0)`, a statement that does nothing. The condition disappears before the compiler sees it, so even a wrong name inside it compiles in Dist.

Exceptions get one sentence of rules: engine code does not throw. The language's `throw`, `try`, `catch` and the cleanup that runs destructors are in [Modern C++ as Strata uses it](../basics/cpp-modern.md); here only the policy matters. Third-party libraries do throw, so the engine catches them at the call site.

`JsonUtils` is the model. The `nlohmann::json` library throws when you read a key of the wrong type, and when it dumps a string that is no valid UTF-8 text. `JsonUtils` therefore reads without exceptions, and `Dump` and `AppendString` replace each bad :term[byte]{id=byte} with the character `U+FFFD`. The :term[frame loop]{id=game-loop} has the last catch: if something still escapes, it logs a critical line and ends the loop in order, so that the logs are written. The program then exits with a failure code.

### Logging

Strata has three loggers, all made by `Log::Init`: `Strata` for engine code, `App` for the editor and the games' own C++, and `Script` for game scripts. Each has five levels, from low to high: Trace, Info, Warn, Error and Critical. Two macro families write to them, `ST_CORE_*` for the engine and `ST_*` for applications, each with the five names: `ST_CORE_WARN("...")`, `ST_ERROR("...")`. Scripts call the SDK's `Log` class, as in `Log::Info(...)`, which reaches the `Script` logger through the host function `Log` of the script interface, not through a macro.

The `fmt` library formats messages: `ST_CORE_INFO("Loaded {} meshes from {}", count, path)` puts the two values where the braces stand. The engine adds format rules for glm vectors, matrices and quaternions, so `ST_CORE_INFO("Spawn at {}", position)` prints the numbers. A warning or an error reaches the console and the file before the call returns, even if the program crashes the next moment.

:::rule
Do not log per frame, and throttle repeating errors. A failure that happens every frame writes 60 lines a second, 3,600 in a minute, and buries the first, the one that explains it. `ErrorThrottle` keeps the last message and logs a new one only when it differs; the caller calls `Clear` when the operation works again.
:::

The throttle compares only with the last message. Take six reports in a row: `device lost` three times, `out of memory`, then `device lost` twice. The throttle logs the first, skips the next two, logs `out of memory` because it differs, logs the next `device lost` because it differs from `out of memory`, and skips the last. That is three lines for six reports, where a plain log call writes six.

Never put a secret in a message. The log file travels in bug reports, so a token or a password in it leaves the machine. The tokens of the editor's automation interface are never logged or printed.

### Code style

Strata follows the Hazel engine's conventions. The names carry meaning:

| Kind | Style | Real example |
| --- | --- | --- |
| Types, functions, files | `PascalCase` | `ErrorThrottle`, `HandleAssertFailure` |
| Locals, parameters | `camelCase` | `frameRan`, `condition` |
| Private members | `m_` and `PascalCase` | `m_LastMessage` |
| Statics | `s_` and `PascalCase` | `s_AssertHandler` |
| Thread-local variables | `t_` and `PascalCase` | `t_CurrentFrame` |
| Constants | `c_` and `PascalCase` | `c_InterruptedExitCode` |
| Public data of plain structs | `PascalCase`, no prefix | `AssertInfo::Message` |
| Macros | `ST_` and `UPPER_SNAKE` | `ST_CORE_ASSERT` |

The prefix is the point. `m_Errors` tells the reader, with no search, that the name is state of the object, and `s_Storage` that every caller shares it, so a thread must be careful. A plain struct has no prefix because its fields are its interface.

The layout follows `.clang-format` and `.editorconfig`. Each level of nesting is one tab, and a single line feed ends each line. Braces stand on their own lines, and the contents of a :term[namespace]{id=namespace} sit one tab deeper. The `*` and `&` of a pointer or reference stay attached to the type, as in `const Type& reference`.

In an engine `.cpp` file the first include is `stpch.h`, the file's own header follows, other engine headers come next, and third-party and standard headers come last. [Flags and portability](../engineering/flags-portability.md) teaches what the precompiled header costs and saves.

Honesty requires one note: the files describe the style, and reviewers hold it. No test and no continuous integration job runs a format check, although the guide calls the formatting enforced. Run your editor's format command, and read your :term[diff]{id=diff} the way a reviewer will.

Names must not collide with the macros that the Windows headers define. The risky ones are `near`, `far`, `interface`, `small`, `OPAQUE` and `TRANSPARENT`, and the names of calls such as `CopyFile`, `DeleteFile`, `GetObject`, `CreateWindow` and `LoadImage`. The :term[preprocessor]{id=preprocessor} rewrites such a name on Windows, for example `CopyFile` into `CopyFileW`, so your function and its callers meet a different name than the one you wrote. The page on [platforms](../core/platform.md) has the full story. Strata's :term[scoped enums]{id=scoped-enumeration} use `None` as a value, and an X11 header would turn that into a macro, so engine code never includes X11 headers, and an enum without `class` never uses the name.

:::example[A loader meets a broken file]
A texture loader reads a file with this header: width, height, then the pixels. Three things can go wrong, and each gets a different answer.

First, the file holds 10 bytes and its header asks for 4,096 by 4,096 pixels, which is about 67 MB at 4 bytes a pixel. Another program or a damaged disk can make such a file, so the loader returns an error value and logs one line, `Texture 'rock.png': header asks for 67 MB, file holds 10 bytes`. A caller can then show a stand-in picture. No assert fits, because a damaged file is the world's fault, not the programmer's.

Second, the loader's helper receives a mip level of 7 for a texture of 5 levels. No file can cause that; the loader's own code computed it. That is an assert: `ST_CORE_ASSERT(level < levelCount, "Mip {} of {}", level, levelCount)`. Debug finds the bug at once. Dist skips the check, so the helper must still not write past its array, a point the review checks.

Third, the loader needs the table of texture formats that the module registered at the start. If the table is empty, every texture in the game fails in a way that looks like bad data. The loader uses `ST_CORE_VERIFY(formatTable != nullptr, "...")`: the check stays in Dist, because a missing registration is also a mistake a shipped game can make, and the message names it.
:::

## A toy version

The toy shows the policy in under 80 lines. It has a logger with two levels, an assert and a verify that share one report function, a build switch `TOY_DIST` that removes the assert, and a loader function that returns an error. It is not the engine's code: the toy prints and continues, as the engine's tests do when they replace the handler.

```cpp sketch="core-conventions-toy.cpp"
// A toy of the engine's error policy: an assert that a Dist build removes, a verify that stays,
// a returned error, and a logger with two levels.
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

namespace
{
	enum class LogLevel
	{
		Info,
		Error
	};

	int s_FailedChecks = 0;

	void Log(LogLevel level, const std::string& message)
	{
		std::printf("[%s] %s\n", level == LogLevel::Info ? "info" : "error", message.c_str());
	}

	void ReportCheck(const char* kind, const char* condition)
	{
		s_FailedChecks++;
		Log(LogLevel::Error, std::string(kind) + " '" + condition + "' failed");
	}
}

// A failed check calls the report; do-while makes the macro one statement.
#define TOY_CHECK(kind, condition) \
	do \
	{ \
		if (!(condition)) \
			ReportCheck(kind, #condition); \
	} while (false)

#if defined(TOY_DIST)
	#define TOY_ASSERT(condition) ((void)0)
#else
	#define TOY_ASSERT(condition) TOY_CHECK("Assertion", condition)
#endif
#define TOY_VERIFY(condition) TOY_CHECK("Verify", condition)

namespace
{
	// A recoverable failure: the caller receives "no value", and the log says why.
	std::optional<int> ParseCount(const std::string& text)
	{
		if (text.empty() || text.size() > 6 || text.find_first_not_of("0123456789") != std::string::npos)
		{
			Log(LogLevel::Error, "ParseCount: '" + text + "' is no count");
			return std::nullopt;
		}
		return std::stoi(text);
	}
}

int main()
{
	for (const char* line : { "42", "4x2" })
	{
		const std::optional<int> count = ParseCount(line);
		if (count)
			Log(LogLevel::Info, "count " + std::to_string(*count));
	}

	const std::vector<int> values = { 10, 20, 30 };
	const size_t index = 3;
	TOY_ASSERT(index < values.size()); // a programmer error: the caller asked past the end
	const int* registry = nullptr;
	TOY_VERIFY(registry != nullptr); // a start-up step that must have run, in every build

	int checks = 0;
	TOY_ASSERT(++checks > 0); // a side effect inside an assert
	std::printf("failed checks %d, side effect ran %d time(s)\n", s_FailedChecks, checks);
	return 0;
}
```

1. **Lines 31–36:** The macro wraps its `if` in `do { } while (false)`, so that `TOY_ASSERT(x);` is one statement and works after an `if` without braces.
2. **Lines 38–43:** The assert has an empty form in a Dist build; the verify has no such form, so it is the same in all builds.
3. **Lines 47–56:** A recoverable failure produces a value that says "no", plus one log line; the caller loops on.
4. **Lines 70–72:** The assert catches a programmer's mistake, the verify catches a start-up step that did not run.
5. **Lines 74–75:** The condition holds a side effect: it runs here, and it would not run if `TOY_DIST` were defined.

The output of the toy:

```text output-of="core-conventions-toy.cpp"
[info] count 42
[error] ParseCount: '4x2' is no count
[error] Assertion 'index < values.size()' failed
[error] Verify 'registry != nullptr' failed
failed checks 2, side effect ran 1 time(s)
```

Two of the three checks fail on purpose, and one passes. The count of 1 for the side effect is the value to remember: the Hard exercise below shows what happens to it when a Dist build removes the assert.

## The real code

The real code differs from the toy in four ways. It breaks into a debugger instead of continuing, it logs through `spdlog`, it formats messages with `fmt`, and its assert is a family of four macros. Follow the data from the base header to the frame loop.

`Base.h` first. Its first lines switch the asserts on in every build but Dist, define the debugger break for each compiler, and provide two small macros.

```cpp src="Strata/src/Strata/Core/Base.h#L10-L28"
#if !defined(ST_DIST)
#define ST_ENABLE_ASSERTS
#endif

#if defined(ST_PLATFORM_WINDOWS)
#define ST_DEBUGBREAK() __debugbreak()
#elif defined(__clang__) || defined(__GNUC__)
#define ST_DEBUGBREAK() __builtin_trap()
#else
#include <csignal>
#define ST_DEBUGBREAK() std::raise(SIGTRAP)
#endif

#define ST_EXPAND_MACRO(x) x
#define ST_STRINGIFY_MACRO(x) #x

#define ST_BIT(x) (1u << (x))

#define ST_BIND_EVENT_FN(fn) [this](auto&&... args) -> decltype(auto) { return this->fn(std::forward<decltype(args)>(args)...); }
```

1. **Lines 10–12:** Every build but Dist defines `ST_ENABLE_ASSERTS`; the assert macros test it.
2. **Lines 14–21:** `ST_DEBUGBREAK` stops in the debugger with the call each compiler offers; Windows uses `__debugbreak`.
3. **Lines 26–28:** `ST_BIT` shifts one bit into place, and `ST_BIND_EVENT_FN` turns a :term[member function]{id=member-function} into a lambda that remembers `this`.

The names `Scope` and `Ref` follow in the same file.

```cpp src="Strata/src/Strata/Core/Base.h#L42-L61"
template<typename T>
using Scope = std::unique_ptr<T>;

template<typename T, typename... Args>
constexpr Scope<T> CreateScope(Args&&... args)
{
	return std::make_unique<T>(std::forward<Args>(args)...);
}

template<typename T>
using Ref = std::shared_ptr<T>;

template<typename T, typename... Args>
constexpr Ref<T> CreateRef(Args&&... args)
{
	return std::make_shared<T>(std::forward<Args>(args)...);
}

template<typename T>
using WeakRef = std::weak_ptr<T>;
```

1. **Lines 42–43:** `Scope` is another name for `std::unique_ptr`, so tools and debuggers show the standard type.
2. **Lines 45–49:** `CreateScope` forwards its arguments to `make_unique`, which makes the object and its owner in one step.
3. **Lines 54–58:** `CreateRef` does the same with `make_shared`.
4. **Lines 60–61:** `WeakRef` names a pointer that watches an object without owning it.

`Scope` and `Ref` are names, not new types, so a `Scope<T>` is a `std::unique_ptr<T>` in every tool and debugger. The `Create` functions forward their arguments to `make_unique` and `make_shared`, which allocate in one step and cannot leak between the allocation and the pointer. The file also defines `ST_DEFINE_ENUM_FLAG_OPERATORS`, which gives an `enum class` the bit operators `|`, `&`, `~` and `HasFlag`, so that a set of flags stays type safe.

The two checks come from `Assert.h`.

```cpp src="Strata/src/Strata/Core/Assert.h#L53-L74"
#define ST_INTERNAL_ASSERT_IMPL(isCore, isVerify, condition, ...) \
	do \
	{ \
		if (!(condition)) [[unlikely]] \
		{ \
			if (::Strata::Detail::HandleAssertFailure(isCore, isVerify, #condition, __FILE__, __LINE__, ::Strata::Detail::FormatAssertMessage(__VA_ARGS__)) == ::Strata::AssertAction::Break) \
				ST_DEBUGBREAK(); \
		} \
	} while (false)

// Asserts are compiled out of Dist builds; the condition must not have side effects.
#ifdef ST_ENABLE_ASSERTS
	#define ST_CORE_ASSERT(condition, ...) ST_INTERNAL_ASSERT_IMPL(true, false, condition, __VA_ARGS__)
	#define ST_ASSERT(condition, ...) ST_INTERNAL_ASSERT_IMPL(false, false, condition, __VA_ARGS__)
#else
	#define ST_CORE_ASSERT(condition, ...) ((void)0)
	#define ST_ASSERT(condition, ...) ((void)0)
#endif

// Verifies are always evaluated, including Dist builds.
#define ST_CORE_VERIFY(condition, ...) ST_INTERNAL_ASSERT_IMPL(true, true, condition, __VA_ARGS__)
#define ST_VERIFY(condition, ...) ST_INTERNAL_ASSERT_IMPL(false, true, condition, __VA_ARGS__)
```

1. **Lines 53–61:** One macro does the work: it tests the condition, calls `HandleAssertFailure` with the text, file and line, and breaks only when the handler says `Break`.
2. **Line 56:** The `[[unlikely]]` attribute marks the failing branch as rare.
3. **Lines 63–70:** Without `ST_ENABLE_ASSERTS` the assert macros expand to `((void)0)`, and the condition vanishes.
4. **Lines 72–74:** The verify macros have no `#ifdef`, so every build keeps them.

The failure path is a function, `HandleAssertFailure`, and not code in the macro, so each use of the macro adds only a call. The function logs a critical line with the kind (Assertion or Verify), the condition text, the file, the line and the message, flushes the logger, and asks the handler what to do. The macro then breaks into the debugger, or the function ends the program. The default handler breaks when a debugger is attached and ends the program otherwise; tests replace it with `SetAssertHandler` to continue. [Debugging the engine](debugging.md) teaches the handler.

The loggers come from `Log::Init`.

```cpp src="Strata/src/Strata/Core/Log.cpp#L254-L267"
// Warnings and errors flush the sinks, which waits for the writer: they are on the console and in the file when the
// call that logged them returns (and survive a crash right after).
auto createLogger = [&](const char* name)
{
	auto logger = std::make_shared<spdlog::logger>(name, sinks.begin(), sinks.end());
	logger->set_level(level);
	logger->flush_on(spdlog::level::warn);
	return logger;
};

data.CoreLogger = createLogger("Strata");
data.ClientLogger = createLogger("App");
data.ScriptLogger = createLogger("Script");
data.Initialized = true;
```

1. **Lines 254–255:** The comment states the promise: a warning or an error is on the console and in the file before the call returns.
2. **Lines 256–262:** One lambda makes every logger with the same sinks and level; `flush_on` keeps the promise.
3. **Lines 264–266:** The three loggers are `Strata`, `App` and `Script`.

The macros are one line each.

```cpp src="Strata/src/Strata/Core/Log.h#L132-L143"
#define ST_CORE_TRACE(...)    ::Strata::Log::GetCoreLogger()->trace(__VA_ARGS__)
#define ST_CORE_INFO(...)     ::Strata::Log::GetCoreLogger()->info(__VA_ARGS__)
#define ST_CORE_WARN(...)     ::Strata::Log::GetCoreLogger()->warn(__VA_ARGS__)
#define ST_CORE_ERROR(...)    ::Strata::Log::GetCoreLogger()->error(__VA_ARGS__)
#define ST_CORE_CRITICAL(...) ::Strata::Log::GetCoreLogger()->critical(__VA_ARGS__)

// Client (editor/game application) log macros
#define ST_TRACE(...)         ::Strata::Log::GetClientLogger()->trace(__VA_ARGS__)
#define ST_INFO(...)          ::Strata::Log::GetClientLogger()->info(__VA_ARGS__)
#define ST_WARN(...)          ::Strata::Log::GetClientLogger()->warn(__VA_ARGS__)
#define ST_ERROR(...)         ::Strata::Log::GetClientLogger()->error(__VA_ARGS__)
#define ST_CRITICAL(...)      ::Strata::Log::GetClientLogger()->critical(__VA_ARGS__)
```

1. **Lines 132–136:** The engine's macros, one per level, call the core logger and pass their arguments to `fmt` unchanged.
2. **Lines 139–143:** The application macros are the same five levels on the `App` logger.

Each macro calls one method of the logger that `GetCoreLogger()` or `GetClientLogger()` returns. The `Script` logger has no macro: scripts reach it through the host function `Log`. The toy's two levels stand for Info and Error.

The throttle is eight lines.

```cpp src="Strata/src/Strata/Core/ErrorThrottle.cpp#L16-L23" symbol="ErrorThrottle::Report"
bool ErrorThrottle::Report(const std::string& message)
{
	if (message == m_LastMessage)
		return false;
	m_LastMessage = message;
	ST_CORE_ERROR("{}: {}", m_Source, message);
	return true;
}
```

The scene :term[renderer]{id=renderer} keeps one throttle as `m_Errors`, and reports each failed allocation of a graphics resource through it. It clears the throttle after a frame that rendered without degrading, so a failure that returns later is news again.

The test of the class shows the subtle point. A message is logged each time it differs from the last one: `device lost`, `out of memory`, `device lost` logs three lines, and eleven identical messages log one.

`JsonUtils` is the catch at the call site.

```cpp src="Strata/src/Strata/Core/JsonUtils.cpp#L18-L33"
	std::optional<nlohmann::json> Discarded(std::string* outError)
	{
		if (outError)
			*outError = "Invalid JSON";
		return std::nullopt;
	}

}

std::optional<nlohmann::json> JsonUtils::Parse(std::string_view text, std::string* outError)
{
	nlohmann::json json = nlohmann::json::parse(text.begin(), text.end(), nullptr, false);
	if (json.is_discarded())
		return Discarded(outError);
	return json;
}
```

1. **Lines 18–23:** The helper writes the error text when the caller asked for one, and returns an empty `std::optional`.
2. **Line 29:** The last argument `false` forbids exceptions; bad text gives a discarded value.
3. **Lines 30–32:** A discarded value becomes "no value" with the error text; any other value is returned.

The last argument of `nlohmann::json::parse`, `false`, tells the library not to throw on bad text. The library returns a "discarded" value instead, and `Parse` turns that into an empty `std::optional` with the error text `Invalid JSON`. `Dump` passes `error_handler_t::replace`, so a byte that is no valid UTF-8 becomes `U+FFFD` where the library would throw by default. A throw from a corner that nobody guarded lands in the frame loop, which has the last catch.

```cpp src="Strata/src/Strata/Core/Application.cpp#L242-L257"
bool frameRan = false;
try
{
	frameRan = RunFrame(m_LastTimestep);
}
catch (const std::exception& exception)
{
	// Engine code does not throw; this catches third-party failures (e.g. the graphics driver reporting a
	// lost device inside NVRHI) so the application still shuts down in order and flushes its logs.
	ST_CORE_CRITICAL("Unhandled exception in the main loop: {}", exception.what());
	m_Running = false;
	// The run failed: a caller (CI, a script, the launcher) must not read success. A code set before (a failed
	// command script, an interrupt) says more and stays.
	if (m_ExitCode == 0)
		m_ExitCode = c_UnhandledExceptionExitCode;
}
```

1. **Lines 242–246:** The frame runs inside `try`; `frameRan` stays false when it throws.
2. **Lines 247–252:** The catch logs the exception at the critical level and clears `m_Running`, so the loop ends, the program stops in order, and the logs are written.
3. **Lines 255–256:** A script or a test runner that started the program must not read success, so the :term[exit code]{id=exit-code} becomes 1. A code set earlier, such as a failed command script's, says more and stays.

The module registry, last, shows the ownership rule at work.

```cpp src="Strata/src/Strata/Core/EngineModule.cpp#L178-L185"
m_Owned.reserve(order.size());
m_Modules.reserve(order.size());
for (const size_t index : order)
{
	m_Modules.push_back(modules[index].get());
	m_Owned.push_back(std::move(modules[index]));
}
return true;
```

The raw pointer goes into `m_Modules` before the `Scope` moves into `m_Owned`, because a moved-from `Scope` is empty. `Clear` destroys the owners last first, so that a module is destroyed after the modules that depend on it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Exceptions for failures | Many C++ applications and most managed languages | Failure paths need no code between the failing call and the handler | Hidden control flow, a cost whenever one is thrown, and no sign in a call of what it may throw; script modules need a plain C interface, which has no exceptions |
| Garbage collection | Managed languages such as C# and Java | No ownership rules to teach | Pauses at times the program cannot choose |
| Error codes for everything | C libraries | One mechanism | Programmer errors would travel as values, and callers would silence them |
| Asserts that stay in every build | Programs that can afford the cost | A shipped game would stop at the first mistake | Cost in every call, and a game that stops where it could continue |
| A log call without a level | Small programs | Less typing | No way to filter, to find the important line, or to flush the right ones |
| A format check in the build | Many projects | Every file looks alike with no review | A job that fails for spacing, and a tool every contributor must install |

## How it is tested

The suite `Core.ErrorThrottle` reports the same error eleven times and checks that one line reaches the log, then checks that a different message, and the same one again after `Clear`, are logged. The suite `Core.Json` checks that `AppendString` writes exactly what `Dump` writes for text with escapes and invalid UTF-8. The suite `Core.Log` tests the writer behind the loggers.

Asserts are tested by replacing the handler. A test in `Physics.Box3D` asks box3d to refuse a hull of an unknown version. Box3d asserts on it, the test's handler counts the call and continues, and an `#if defined(ST_DIST)` branch expects zero asserts in Dist, because Dist compiles them out. A helper program of `StrataTests/src/Engine/ModuleRegistrationHelpers.cpp` uses a registry before registration, with a handler that exits, so that a missing verify would show.

Run one suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.ErrorThrottle`, or all of them with `ctest --preset windows-debug -j 8`.

## Changing it safely

Extension points are few. A new kind of failure uses the existing macros; a new logger needs a reason, because every sink and tool knows only the three. A new class gets its prefixes and its owner from the tables above.

Check these before you commit:

1. Every `new` or `CreateRef` has a named owner, and a `Ref` has a reason.
2. Each assert has no side effect, and the code after it still holds in Dist for the input it would have caught.
3. Each recoverable failure returns an error and logs once; no log call sits in a per-frame path without a throttle.
4. Every call into a third-party library that can throw has a catch at the call site.
5. Names, braces, and includes match the style; none of the Windows macro names appears.

[The review checklist and the way a change lands](../engineering/contributing.md) lists what else the reviewer checks.

## Summary

- A `Scope` is the single owner, a `Ref` shares ownership and frees at the last release, and a raw pointer or reference only borrows; registries own through `Scope`, and assets are held by handle.
- A programmer's mistake is an assert or a verify; a failure the world can cause is a returned value plus one log line. Engine code does not throw, and third-party throws are caught at the call site.
- `ST_CORE_ASSERT` vanishes in Dist, so its condition has no side effects; `ST_CORE_VERIFY` stays in every build.
- Three loggers, five levels and two macro families write messages; warnings flush at once, nothing logs per frame, and `ErrorThrottle` logs a repeating error once.
- Names carry `m_`, `s_`, `t_` and `c_`; code uses tabs and braces on their own lines, starts with `stpch.h`, and avoids the Windows macro names.

## Check yourself

1. A function receives a pointer to a mesh that the scene owns and uses it only during the call. Which type fits the parameter: `Ref<Mesh>`, `Scope<Mesh>` or `Mesh*`?

   :::answer{tests="ownership"}
   `Mesh*`, or `const Mesh&` when it cannot be null. The scene owns the mesh, and the function only borrows it. `Ref<Mesh>` would claim shared ownership and extend the mesh's life to the function's, and `Scope<Mesh>` would take the only ownership away from the scene.
   :::

2. A project file holds the text `{"name": }`. Is that an assert, a verify or a returned error?

   :::answer{tests="failure-kinds"}
   A returned error. A person or another program can make a broken file, so it is the world's fault and the program must survive it. An assert would stop the editor over a typing mistake, and a verify would do the same in every build.
   :::

3. A test asserts `ST_CORE_ASSERT(list.Remove(id))` and passes in Debug but fails in Dist. Why, and what is the fix?

   :::answer{tests="dist-assert"}
   Dist compiles the assert out, so `Remove` never runs and the list keeps the id. The fix is to call `Remove` on its own line, store the result and assert on the result.
   :::

4. A renderer fails to allocate a buffer in every frame, for 600 frames. How many error lines does the code write if it calls `m_Errors.Report` with the same text each time, and how many if the text contains the frame number?

   :::answer{tests="logging"}
   One line in the first case; the message repeats, so the throttle stays quiet. In the second case 600 lines, because each message differs from the one before, and the throttle compares text. Keep the frame number out of the message.
   :::

5. Which of these names breaks the style: `m_Registry`, `c_MaxSteps`, `s_instance`, `t_Frame`?

   :::answer{tests="code-style"}
   `s_instance`. A static name has `s_` and then `PascalCase`, so it is `s_Instance`. The other three follow their rules: a private member, a constant and a thread-local variable.
   :::

## Exercises

1. **Basic.** Sort these three failures into an assert, a verify and a returned error, and give a reason for each. The failures are a project file that cannot be read, an index past the end of an engine array, and a registry used before registration.

   :::answer[Worked solution]{tests="failure-kinds"}
   The project file is a returned error: a person can break it, and the editor must show the problem and continue. The index past the end is an assert: only a coding mistake makes it, so Debug should stop at once, and the code does not have to survive it in Dist. The registry used too early is a verify, as `AssetManager` does it. A shipped game that forgot a registration would otherwise fail in confusing ways, so the check stays in Dist and its message names the cause.
   :::

2. **Medium.** Trace it yourself. Follow `ST_CORE_VERIFY` from its macro to the critical log line, by a search or a debugger.

   :::answer[Worked solution]{tests="failure-kinds,logging"}
   Search for `define ST_CORE_VERIFY` in `Strata/src/Strata/Core/Assert.h`: it expands to `ST_INTERNAL_ASSERT_IMPL`, which calls `Detail::HandleAssertFailure` when the condition is false. That function is in `Strata/src/Strata/Core/Assert.cpp`. It builds an `AssertInfo`, and when `Log::IsInitialized()` it calls `logger->critical` with the text "Verify 'condition' failed at file:line: message", then `logger->flush()`. Last it asks the handler, and ends the program or breaks. A breakpoint on `HandleAssertFailure` stops there with the stack of the failing code.
   :::

3. **Hard.** A program defines `TOY_DIST` and calls `TOY_ASSERT(Remove(ids, 2))`, where `Remove` erases the element 2 from a vector holding 1, 2 and 3. Predict the size of the vector afterwards in a Dist build, then fix the code so that the removal always happens.

   :::answer[Worked solution]{tests="dist-assert" solution="sketches/core-conventions-dist.cpp"}
   The program defines `TOY_DIST`, so the assert expands to nothing.

   ```cpp sketch="core-conventions-dist.cpp"
   // The toy's assert in a Dist build: the condition inside it is never evaluated, so a side effect there is lost.
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   #define TOY_DIST

   #if defined(TOY_DIST)
   	#define TOY_ASSERT(condition) ((void)0)
   #else
   	#define TOY_ASSERT(condition) ((condition) ? (void)0 : (void)std::puts("assertion failed"))
   #endif

   namespace
   {
   	// Removes the first element equal to id; returns whether it found one.
   	bool Remove(std::vector<int>& ids, int id)
   	{
   		const auto found = std::find(ids.begin(), ids.end(), id);
   		if (found == ids.end())
   			return false;
   		ids.erase(found);
   		return true;
   	}
   }

   int main()
   {
   	std::vector<int> broken = { 1, 2, 3 };
   	TOY_ASSERT(Remove(broken, 2)); // the removal is inside the assert

   	std::vector<int> fixed = { 1, 2, 3 };
   	[[maybe_unused]] const bool removed = Remove(fixed, 2);
   	TOY_ASSERT(removed); // the removal is outside: only the check is optional

   	std::printf("broken keeps %zu ids, fixed keeps %zu ids\n", broken.size(), fixed.size());
   	return 0;
   }
   ```

   1. **Line 6:** This line makes the program a Dist build of the toy.
   2. **Lines 29–30:** The removal is inside the assert and never runs, so `broken` keeps its three ids.
   3. **Lines 32–34:** The removal is outside the assert, so it runs in every build; `[[maybe_unused]]` keeps the compiler quiet when the assert disappears and nothing reads `removed`.

   ```text output-of="core-conventions-dist.cpp"
   broken keeps 3 ids, fixed keeps 2 ids
   ```

   Remove line 6 and the first vector keeps two ids, which is the Debug behavior that hides the bug. In the engine the same mistake passes under Debug and fails under Dist, which is why tests that depend on asserts carry `#if defined(ST_DIST)`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Base.h`: `Scope`, `Ref`, `WeakRef`, `ST_ENABLE_ASSERTS`, `ST_DEBUGBREAK`, `ST_BIT`, `ST_BIND_EVENT_FN`, `ST_DEFINE_ENUM_FLAG_OPERATORS`.
- `Strata/src/Strata/Core/Assert.h` and `Assert.cpp`: `ST_CORE_ASSERT`, `ST_ASSERT`, `ST_CORE_VERIFY`, `ST_VERIFY`, `SetAssertHandler`, `Detail::HandleAssertFailure`.
- `Strata/src/Strata/Core/Log.h` and `Log.cpp`: `Log`, the three loggers, `ST_CORE_*` and `ST_*`, the glm format rules.
- `Strata/src/Strata/Core/ErrorThrottle.h` and `.cpp`; `Strata/src/Strata/Core/JsonUtils.h` and `.cpp`.
- `Strata/src/Strata/Core/EngineModule.h` and `.cpp`: `EngineModuleRegistry`, the owner of the modules.
- Tests: `StrataTests/src/Core/ErrorThrottleTests.cpp`, `JsonUtilsTests.cpp`, `BackgroundLogSinkTests.cpp`, `StrataTests/src/Physics/PhysicsBox3DTests.cpp`.
- Style files: `.clang-format` and `.editorconfig` at the :term[repository's]{id=repository} root.

## Further reading

- [cppreference, `assert`](https://en.cppreference.com/w/cpp/error/assert): the standard library's assert and its switch `NDEBUG`; beginner.
- [cppreference, `std::unique_ptr`](https://en.cppreference.com/w/cpp/memory/unique_ptr): what `Scope` is; intermediate.
- [The spdlog repository](https://github.com/gabime/spdlog): the logging library behind the loggers; intermediate.
- [The fmt repository](https://github.com/fmtlib/fmt): the formatting syntax of `{}`; intermediate.
- [The nlohmann JSON repository](https://github.com/nlohmann/json): the library that `JsonUtils` guards; intermediate.
- [Microsoft, the `__debugbreak` intrinsic](https://learn.microsoft.com/en-us/cpp/intrinsics/debugbreak): what `ST_DEBUGBREAK` is on Windows; advanced.

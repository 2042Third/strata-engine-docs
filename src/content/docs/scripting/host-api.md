---
id: scripting/host-api
title: "The host API: engine services behind a C table"
description: "How a script's call reaches the engine: one table of C functions, two guards every function starts with, and the services behind it."
kind: internals
size: L
tracks: [E]
needs: [scripting/script-system, core/engine-modules, core/layers-registries]
time: 90
learn:
  - id: host-pattern
    text: explain why game code reaches the engine through one table of C functions and an opaque context
  - id: host-guards
    text: trace a host call from the SDK to the engine and name each guard and failure exit on the way
  - id: host-table
    text: find where a new host function must be listed and what fails when it is not
  - id: host-services
    text: choose the service a gameplay function must go through, and say why Scripting may not include its module
since: 0.3.0
status: final
---

A script is code that the engine loads from a separate library and runs inside its own frame. That code needs the engine's help for nearly everything: it cannot move an entity, play a sound or save a file by itself. The host application programming interface (API), here called the host table, is the way it asks. It is one table of C :term[function pointers]{id=function-pointer} that the engine fills and hands to the script library, so that game code gets the engine's services without seeing a single engine :term[header]{id=header}.

This page follows one call through that table: how the software development kit (:term[SDK]{id=sdk}) packs it, which two guards the engine runs first, how a mistake is reported, and how the table is kept complete. The list of every function is in [the script reference](../reference/script-api.md).

## The problem and how engines solve it

Think of what a game script wants to do in one frame: read the time, find the player, change a light, play a sound, ask where a ray hits. Each of those lives in a different :term[engine module]{id=engine-module}, and each module has headers full of types that change from release to release. If the script includes those headers, three bad things follow.

First, the script library and the engine must be built by the same :term[compiler]{id=compiler} with the same settings, or the layout of every shared type may differ. Second, a script that includes the engine cannot be reloaded safely: it holds pointers into engine memory that die with the old library. Third, a crash in script code can corrupt engine state, because both live in one tangle of types.

Engines solve this in a few ways. Some run scripts in a managed language with a binding layer, which costs a :term[runtime]{id=runtime} and a copy at every crossing. Some run scripts in a separate process and talk by messages, which isolates well and costs a message per call. Some link the script code straight into the engine, which is fast and fragile.

Strata takes a fourth way, the one plug-in systems and :term[Vulkan's]{id=vulkan} :term[loader]{id=loader} use. The engine hands the plug-in a table of function pointers, each with a C signature, and an opaque value that says which scene is calling. The plug-in never links the engine; it only calls through the table.

The price is that every call crosses a boundary where only plain data may travel. So each function needs a packing step on the script side and a checking step on the engine side. The gain is large. Reloading a library is safe, because the table lives in the engine. A crash in the script is caught at the crossing.

Tests can count calls, because every call passes one place. [The page on the table's binary layout](../scripting/abi-sdk.md) shows the table's :term[struct]{id=struct}; this page shows what stands behind each entry.

## The map

Four places take part. The script side holds the SDK headers, which turn a call such as `Entity::SetProperty` into a call through the table pointer. The table itself, a `StrataScriptHostAPI` struct, is built once by the engine. Behind it sit the `Host<Name>` functions of `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, one per table entry. Behind those sit the scene, its registered :term[scene services]{id=scene-service} and the engine services of `Strata/src/Strata/Core/EngineServices.h`.

```mermaid caption="A script's call crosses the table, passes a counting function and the host function, and reaches the scene or a service." alt="Boxes from left to right: script code, the table of function pointers, the host function, then the scene or a service. A side box shows the registry of contexts that the host function consults."
flowchart LR
	Script["Script code in the module (SDK headers)"] -->|"table pointer + context"| Table["StrataScriptHostAPI"]
	Table --> Count["Counting function (not in Dist)"]
	Count --> Host["Host function: ResolveContext, then work"]
	Registry["Registry of contexts (main thread only)"] -.-> Host
	Host --> Scene["Scene and its components"]
	Host --> SceneServices["Scene services (physics, audio...)"]
	Host --> EngineServices["Engine services (saves, window...)"]
```

Everything runs on the :term[main thread]{id=main-thread}. The main thread owns the scene, input and the scripts, so a host function may touch the scene without a lock. That single fact explains most of the rules below.

## The contract

A script may assume that a host function never crashes, never throws and never touches the engine in a way that breaks it. A host function may assume nothing about its caller, because the caller is code the engine did not write. The rules follow from those two sentences.

1. **Call the engine only from callbacks.** The context in the table is valid only while the engine is calling the script. A script that keeps the context and calls from a thread of its own, or outside any callback, is refused.
2. **Never use another thread.** The engine is single-threaded towards scripts. The one exception is `Log`, which any thread may call, because it only writes a message.
3. **Every host function starts with `ResolveContext`** and wraps its body in `HostCall`. The first decides whether the call is allowed; the second makes sure no exception leaves.
4. **A host function returns a failure value and reports; it never asserts.** A script's mistake is data the engine must survive, not a bug in the engine.
5. **A host function validates every input it reads**, including handles, strings and sizes, before it touches the engine.

:::rule
Every host function wraps its body in `HostCall`, begins with `ResolveContext`, reports misuse through `ScriptSystem::ReportProblem` and returns a failure value; none asserts. The reason: a script author's mistake must cost a warning, not the process, as the section on `ReportProblem` below explains.
:::

Here is the first idea the contract introduces. A **host function** is a function of the engine that a script calls through the host table; the engine implements it, the script only holds its address. Each one is named `Host<Name>` in the source, for example `HostSetTimeScale`.

## A toy version

:::question
New to C++ classes, pointers, calls like `a.f(`, :term[lambdas]{id=lambda}, `constexpr` or threads? Read [classes and calls](../basics/programming-3.md), [pointers](../basics/cpp-memory.md), [templates and lambdas](../basics/cpp-generic.md), [modern C++](../basics/cpp-modern.md) and [threads](../basics/threads.md) first.
:::

Before the real code, a table of two functions with the first guard. The program below has a context, a table of two function pointers, and a `ResolveContext` that refuses calls for three reasons: no valid context, the wrong thread, or no call in progress. `main` plays the part of the script and makes five calls, each of which breaks one rule or none.

```cpp sketch="scripting-host-api-toy.cpp"
#include <cmath>
#include <cstdio>
#include <set>
#include <thread>

struct Context
{
	float TimeScale = 1.0f;
};

// The table: plain function pointers, each taking the context first.
struct HostTable
{
	void (*SetTimeScale)(Context* context, float timeScale);
	float (*GetTimeScale)(Context* context);
};

static std::set<const Context*> s_Contexts;
static std::thread::id s_OwnerThread = std::this_thread::get_id();
static bool s_CallInProgress = false;
static int s_SetCalls = 0;

// The first guard: refuse every call that is not allowed, and say why.
static Context* ResolveContext(Context* context, const char* function)
{
	if (!context || !s_Contexts.count(context))
		std::printf("%s: invalid context\n", function);
	else if (std::this_thread::get_id() != s_OwnerThread)
		std::printf("%s: wrong thread\n", function);
	else if (!s_CallInProgress)
		std::printf("%s: no script call in progress\n", function);
	else
		return context;
	return nullptr;
}

static void HostSetTimeScale(Context* context, float timeScale)
{
	s_SetCalls++;
	Context* resolved = ResolveContext(context, "SetTimeScale");
	if (!resolved)
		return;
	if (!std::isfinite(timeScale) || timeScale < 0.0f)
	{
		std::printf("SetTimeScale: %.1f is not a finite, non-negative number\n", timeScale);
		return;
	}
	resolved->TimeScale = timeScale;
}

static float HostGetTimeScale(Context* context)
{
	Context* resolved = ResolveContext(context, "GetTimeScale");
	return resolved ? resolved->TimeScale : 1.0f;
}

int main()
{
	Context context;
	s_Contexts.insert(&context);
	const HostTable host = { &HostSetTimeScale, &HostGetTimeScale };

	host.SetTimeScale(&context, 0.5f);
	s_CallInProgress = true;
	host.SetTimeScale(nullptr, 0.5f);
	host.SetTimeScale(&context, -1.0f);
	std::thread([&]() { host.SetTimeScale(&context, 2.0f); }).join();
	host.SetTimeScale(&context, 0.5f);
	std::printf("time scale %.1f after %d calls\n", host.GetTimeScale(&context), s_SetCalls);
	return 0;
}
```

```text output-of="scripting-host-api-toy.cpp"
SetTimeScale: no script call in progress
SetTimeScale: invalid context
SetTimeScale: -1.0 is not a finite, non-negative number
SetTimeScale: wrong thread
time scale 0.5 after 5 calls
```

1. **Lines 12–16:** the table is a struct of function pointers, each taking the context first.
2. **Lines 24–34:** the first guard refuses a call for each of three reasons and says why.
3. **Line 39:** the counter counts every call, before any guard can refuse it.
4. **Lines 43–47:** after the guard, the function checks its input and reports instead of acting.
5. **Lines 63–68:** `main` plays the script: the first call comes before any call is in progress, the others test one rule each.

Read the output against the five calls. The first call comes before the "script" started, so it is refused. The second passes a null context. The third passes a valid context but a negative value, so the function reports and leaves the scale alone. The fourth comes from another thread.

Only the fifth reaches the data, so the scale is 0.5 after five calls. The counter counted every call, the refused ones too; the real engine does the same, and its test of the counters relies on it.

The toy omits much that the real code needs. It has no `HostCall`, because it never throws. It reports with `printf`, not with a message that names the script and entity. It has one context, not a registry owned by scenes. Its table has two entries, not 165, and nothing checks that the table is complete.

## The real code

### The SDK side: packing a call

A script never calls `host->SetProperty` itself. It calls `Entity::SetProperty` from the SDK, which turns a C++ value into the table's plain data. The SDK is the only code that sees both worlds.

The next quote is the SDK's `GetProperty`. Search for the stack buffer of 256 :term[bytes]{id=byte} and the second read of the table call. The engine returns the size of a string it could not fit, and the SDK asks again with a buffer of that size.

```cpp src="StrataScriptCore/Include/StrataScript/Entity.h#L358-L385" symbol="Entity::GetProperty"
template<typename T>
std::optional<T> Entity::GetProperty(std::string_view component, std::string_view property) const
{
	const StrataScriptHostAPI* host = Detail::GetHost();
	if (!host || m_ID == 0)
		return std::nullopt;

	StrataScriptValue value = {};
	char stackBuffer[256];
	if (!host->GetProperty(Detail::GetContext(), m_ID, Detail::ToABIString(component), Detail::ToABIString(property), &value, stackBuffer, sizeof(stackBuffer)))
		return std::nullopt;

	std::string largeBuffer;
	if (value.Type == StrataScriptValueType_String && value.As.String.Size > sizeof(stackBuffer))
	{
		// Longer than the stack buffer: read again into a buffer of the reported size.
		largeBuffer.resize(static_cast<size_t>(value.As.String.Size));
		if (!host->GetProperty(Detail::GetContext(), m_ID, Detail::ToABIString(component), Detail::ToABIString(property), &value, largeBuffer.data(), largeBuffer.size()))
			return std::nullopt;
		if (value.As.String.Size > largeBuffer.size())
			value.As.String.Size = largeBuffer.size();
	}

	T result {};
	if (!Detail::ValueTraits<T>::FromValue(value, result))
		return std::nullopt;
	return result;
}
```

1. **Line 366:** a stack buffer of 256 bytes takes the common short string without a :term[heap allocation]{id=dynamic-allocation}.
2. **Line 371:** only a string longer than the buffer needs a second read.
3. **Lines 374–376:** the buffer grows to the size the engine reported, and the engine is asked again.
4. **Lines 377–378:** if the string grew in between, the size is clamped to the buffer, so the SDK never reads past it.

`ValueTraits<T>` converts between the table's plain `StrataScriptValue` and the C++ type the script asked for, and an answer of the wrong type becomes an empty result.

:::example
**A property longer than the buffer.** A script reads a 300-byte string from a component, and the SDK passes `stackBuffer`, capacity 256. The engine copies only 256 bytes but stores the full length, 300, in the value. The SDK sees `300 > 256`, makes a `std::string` of 300 bytes and asks again. The second answer carries all 300 bytes.

Two calls instead of one are the price; the common short string costs only one, with no :term[heap allocation]{id=dynamic-allocation}.

If the property changed between the two calls and grew to 320 bytes, the second read would report 320 with a buffer of 300. The clamp at the end of the quote handles that: the SDK keeps the size to the buffer it has, so it never reads past it.
:::

### The first guard: `ResolveContext`

Behind the table, the engine's function receives the context. A context is an opaque pointer: in fact the address of the scene's `ScriptSystem`. That is why the engine checks it against a registry before it trusts it. The registry is a set of pointers, `s_Contexts`, filled by `RegisterScriptContext` when a scene starts playing and emptied by `UnregisterScriptContext` when it stops.

In the quote, search for the order of the checks and for what each one logs. The order matters: the cheap checks that need no scene come first, and the registry lookup comes only after the thread check, because only the main thread may read the set.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L65-L96" symbol="ResolveContext"
// Resolves a context to its scene's script system, or null (logging why) if the call is not allowed: invalid or
// stale context, wrong thread, no script call in progress, or a crashed module.
ScriptSystem* ResolveContext(StrataScriptContext* context, const char* function)
{
	if (!context)
	{
		ReportGlobalProblem(fmt::format("{}: scripts can only use the engine from within their callbacks (no scene context)", function));
		return nullptr;
	}
	if (std::this_thread::get_id() != s_OwnerThread.load())
	{
		ReportGlobalProblem(fmt::format("{}: scripts can only use the engine from the main thread", function));
		return nullptr;
	}
	if (!s_Contexts.count(context))
	{
		ReportGlobalProblem(fmt::format("{}: invalid or expired scene context", function));
		return nullptr;
	}
	if (!ScriptModule::GetCurrentCall())
	{
		ReportGlobalProblem(fmt::format("{}: scripts can only use the engine while the engine is calling them", function));
		return nullptr;
	}

	ScriptSystem* system = reinterpret_cast<ScriptSystem*>(context);
	ScriptEngine* engine = system->GetEngine();
	// A module that crashed may still be running code further up the stack; it gets nothing from the engine.
	if (!engine || !engine->GetModule() || engine->GetModule()->IsFaulted())
		return nullptr;
	return system;
}
```

1. **Lines 69–73:** no context at all.
2. **Lines 74–78:** a call from a thread other than the owner.
3. **Lines 79–83:** a pointer that is not in the registry.
4. **Lines 84–88:** the engine is not inside a script call.
5. **Lines 92–94:** a faulted module gets nothing, and no message.

The checks cover five cases. A null context means the script called outside a callback with no context at all, and a different thread means the script started a thread of its own. A pointer not in the set is a stale context, for example one kept from a scene that ended, or a forged one. A null `GetCurrentCall` means the engine is not inside a script call, so nobody asked this function to run. A faulted module has crashed and may still have code on the stack above this call, so it gets nothing from the engine and no message either.

The first four failures go to `ReportGlobalProblem`, which logs once per message and remembers at most 256 messages. They have no scene to report to, since the scene is exactly what could not be found. The host's own checks of a call that passed this guard go to `ReportProblem`, below.

### The second guard: `HostCall`

C++ exceptions must not travel across the table into the module, because the module is separate code that cannot handle them. Allocation failures and third-party code can throw. `HostCall` stops them.

The quote shows a function template: it runs the body, and if anything is thrown, it logs and returns the failure value. The `noexcept` keyword states that nothing escapes.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L98-L116" symbol="HostCall"
// Runs a host function body. Exceptions (only possible from allocation failures or third-party code) must not
// unwind into the module, so they are logged and the function returns its failure value.
template<typename Result, typename Body>
Result HostCall(const char* function, Result failure, Body&& body) noexcept
{
	try
	{
		return body();
	}
	catch (const std::exception& exception)
	{
		ReportGlobalProblem(fmt::format("{}: internal error: {}", function, exception.what()));
	}
	catch (...)
	{
		ReportGlobalProblem(fmt::format("{}: internal error", function));
	}
	return failure;
}
```

1. **Lines 100–101:** a template over the result type and the body; `noexcept` states that nothing escapes.
2. **Line 105:** the normal path runs the body and returns its result.
3. **Lines 107–114:** a standard exception or any other one is logged, with the function's name.
4. **Line 115:** the caller's failure value is returned.

`Result` is the function's return type. `failure` is the value the caller chooses to return when the body fails: `false` for a function that answers yes or no, `0` for one that returns an entity. A function that returns nothing uses `HostCallVoid`, which is `HostCall<bool>` with a body that returns true. Strata's own code does not throw, so the handler is a net for the cases it cannot control.

### Reporting: `ReportProblem`

When a call is allowed but its content is wrong, the host reports. **ReportProblem** is the `ScriptSystem` function that logs a warning about a misused host function once per message, up to 1,024 messages per scene, and names the calling script and entity.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L1541-L1558" symbol="ScriptSystem::ReportProblem"
void ScriptSystem::ReportProblem(std::string_view function, const std::string& message)
{
	std::string text;
	const ScriptCallSite* site = ScriptModule::GetCurrentCall();
	if (site && site->Class)
		text = fmt::format("{} (called by script '{}' on entity {}): {}", function, site->Class->Name, DescribeEntity(m_Scene, site->Entity), message);
	else
		text = fmt::format("{}: {}", function, message);

	if (m_ReportedProblems.size() >= c_MaxReportedProblems)
		return;
	if (!m_ReportedProblems.insert(text).second)
		return;

	Log::GetScriptLogger()->warn("{}", text);
	if (m_ReportedProblems.size() == c_MaxReportedProblems)
		Log::GetScriptLogger()->warn("Scene '{}': further script problems are not reported", m_Scene.GetName());
}
```

1. **Lines 1544–1548:** the text names the calling script and entity when a :term[call site]{id=call-site} exists.
2. **Lines 1550–1553:** past the cap, or for a text already seen, nothing is logged.
3. **Lines 1555–1557:** the warning is written, and the last one announces the cap.

The :term[call site]{id=call-site} comes from `ScriptModule::GetCurrentCall`. A report therefore reads like the next line, with an example script and entity: `SetTimeScale (called by script 'Pause' on entity Player): the time scale must be a finite, non-negative number (got -1)`. Without that context, a log line from a host function would not say which script to open. The set `m_ReportedProblems` makes the report once per text: a script that makes the same mistake every frame writes one line, not sixty a second. At 1,024 distinct texts, one last warning says that further problems are not reported, and the scene stays silent from then on.

The host reports these cases:

- an invalid or expired context, the wrong thread and a call outside a callback (a crashed module gets no message);
- a null or non-finite input, and a null entity or one that does not exist;
- an unknown component or property, and a value of the wrong type;
- an asset that is not loaded or not of the right type, and a scene that is full;
- an absent service.

Why does a host function never assert? An assertion ends the program (in the editor, the whole session). A script that passes a wrong handle is not a bug in the engine, and a script author must be able to try, fail and read a warning. In a shipped game, the assertion would be gone and the code after it would run on bad data. A returned failure value plus one report gives the author the information, and costs the player nothing.

### A tiny host function: `SetTimeScale`

The smallest real function shows the whole pattern. It resolves the context, checks the one input and either reports or acts.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L356-L370" symbol="HostSetTimeScale"
void HostSetTimeScale(StrataScriptContext* context, float timeScale)
{
	HostCallVoid("SetTimeScale", [&]()
	{
		ScriptSystem* system = ResolveContext(context, "SetTimeScale");
		if (!system)
			return;
		if (!std::isfinite(timeScale) || timeScale < 0.0f)
		{
			system->ReportProblem("SetTimeScale", fmt::format("the time scale must be a finite, non-negative number (got {})", timeScale));
			return;
		}
		system->GetScene().SetTimeScale(timeScale);
	});
}
```

1. **Line 358:** `HostCallVoid` is the second guard; the whole body runs inside it.
2. **Lines 360–362:** the first guard; a null result ends the call, and nothing more is reported, because `ResolveContext` already said why.
3. **Line 363:** `std::isfinite` rejects :term[NaN]{id=nan} and infinity, and a negative scale would run time backwards.
4. **Line 365:** `ReportProblem` names the function and formats the bad value; the function then returns without changing the scene.
5. **Line 368:** only now does the scene change.

The path from script to scene has now been shown whole. The SDK function `Time::SetTimeScale` calls `host->SetTimeScale(Detail::GetContext(), timeScale)`; the table entry holds the counting function, which counts and forwards to `HostSetTimeScale`; that guards, checks and calls `Scene::SetTimeScale`.

```mermaid caption="A host call from the script's side: each diamond is a place where the call can end early, and each exit returns a failure value to the script." alt="Flow from the script's SDK call through the table to the host function. Diamonds ask: is the context valid, is it the main thread, is a call in progress, is the module healthy, are the inputs valid. A no at any diamond leaves with a failure value; the last yes reaches the scene and returns the result."
flowchart TD
	A["SDK: Time::SetTimeScale(0.5)"] --> B["Table entry: count the call"]
	B --> C["HostSetTimeScale: HostCallVoid"]
	C --> D{"Context valid and registered?"}
	D -- no --> X["Log once, return failure"]
	D -- yes --> E{"Main thread?"}
	E -- no --> X
	E -- yes --> F{"Call in progress?"}
	F -- no --> X
	F -- yes --> G{"Module healthy?"}
	G -- no --> Y["Return failure, no message"]
	G -- yes --> H{"Finite and not negative?"}
	H -- no --> Z["ReportProblem, return"]
	H -- yes --> I["Scene sets the scale, return"]
```

### A real function: `Instantiate`

`Instantiate` creates entities from a prefab or model. It is long because it has many ways to fail, and because it must never wait. Script code runs on the main thread; if `Instantiate` waited for a file to load, the frame would stall. The rule of the engine's assets is that nothing blocks a frame, so the call starts the load and answers "no entity" until the asset is ready.

In the quote below, search for three things: the request with high priority, the two reports that tell a script to request early, and the call that creates the new entities' script instances before returning.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L857-L895" from="// Never waits for loading (script code runs on the main thread): an asset that is not loaded yet is requested and" to="system->CreatePendingInstances();" symbol="HostInstantiate"
// Never waits for loading (script code runs on the main thread): an asset that is not loaded yet is requested and
// the call fails, so scripts request assets early and instantiate them once they are loaded.
const Ref<Asset> loaded = manager->GetAsset(handle, AssetPriority::High);
if (!loaded)
{
	if (manager->GetAssetState(handle) == AssetState::Failed)
		system->ReportProblem("Instantiate", fmt::format("asset {} failed to load: {}", handle.ToString(), manager->GetAssetError(handle)));
	else
		system->ReportProblem("Instantiate", fmt::format("asset {} is not loaded yet (its load was started); request assets early "
			"(Assets::RequestLoad) and instantiate them once Assets::IsLoaded is true", handle.ToString()));
	return 0;
}
if (loaded->GetType() != AssetType::Prefab && loaded->GetType() != AssetType::Model)
{
	system->ReportProblem("Instantiate", fmt::format("asset {} is not a prefab or model", handle.ToString()));
	return 0;
}

std::string error;
const std::vector<Entity> roots = std::static_pointer_cast<EntityTemplate>(loaded)->Instantiate(system->GetScene(), parentEntity, &error);
if (roots.empty())
{
	system->ReportProblem("Instantiate", error.empty() ? fmt::format("asset {} contains no entities", handle.ToString())
		: fmt::format("asset {} could not be instantiated: {}", handle.ToString(), error));
	return 0;
}

Entity root = roots.front();
if (transform)
{
	TransformComponent& rootTransform = root.GetComponent<TransformComponent>();
	rootTransform.Translation = translation;
	rootTransform.Rotation = rotation;
	rootTransform.Scale = scale;
	root.MarkModified<TransformComponent>();
}

// Scripts of the new entities exist when this returns, so the caller can configure them right away.
system->CreatePendingInstances();
```

1. **Lines 857–859:** the asset is requested at high priority, and the call never waits for it.
2. **Lines 862–866:** a failed load and a load in progress get different reports.
3. **Lines 869–873:** the loaded asset's type is checked again.
4. **Lines 876–882:** the entities are created; an empty result is reported with the reason.
5. **Lines 894–895:** the scripts of the new entities are created before the call returns.

The two outcomes of "not loaded" differ. A failed load reports its error text. A load still running reports that it was started, and tells the author to request assets early with `Assets::RequestLoad` and to create entities once `Assets::IsLoaded` is true. Because the first call already requested the asset, a script that tries again on a later frame succeeds. `CreatePendingInstances` lets the caller configure the new scripts at once: without it, the script components would exist but their instances would be created only later.

## The table and its guard

The table is built from one list. A :term[macro]{id=macro} lists every function name once, and other macros read the list again to build the table's offsets, the checks and the counters. A macro that is called with another macro as its argument, to repeat one action for each name in a list, is an **X-macro**. It exists to keep several things in step with one list.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3431-L3436"
#define ST_SCRIPT_HOST_FUNCTIONS(X) \
X(Log) \
X(ReportException) \
X(GetDeltaTime) \
X(GetFixedDeltaTime) \
X(GetElapsedTime) \
```

The list begins `X(Log)`, `X(ReportException)`, `X(GetDeltaTime)` and ends at `X(ResetInterpolation)`, with 165 names in all. The order is the order of the struct's members. Two things are built from it: an array `c_HostFunctions` with each name, its offset in `StrataScriptHostAPI` (from `offsetof`) and its size, and the table itself.

Why a list at all? The struct already names the functions. The answer is that the struct says what must exist, and the list lets the engine check that it does, member by member. A function added to the struct but forgotten in the list would leave a null entry in the table, and a script calling it would crash. The next quote makes the compiler refuse that build.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3609-L3620" symbol="ListsEveryHostFunction"
// True when c_HostFunctions covers the struct after its header exactly: every member, in order, without gaps.
constexpr bool ListsEveryHostFunction()
{
	size_t expectedOffset = offsetof(StrataScriptHostAPI, ABIVersion) + sizeof(StrataScriptHostAPI::ABIVersion);
	for (const HostFunctionEntry& entry : c_HostFunctions)
	{
		if (entry.Offset != expectedOffset)
			return false;
		expectedOffset += entry.Size;
	}
	return expectedOffset == sizeof(StrataScriptHostAPI);
}
```

1. **Line 3612:** the walk starts at the end of the header, after `ABIVersion`.
2. **Lines 3613–3617:** each entry must start where the previous one ended; a gap or a swap returns false.
3. **Line 3619:** the last entry must end exactly at the end of the struct.

The function runs at :term[compile time]{id=compile-time} (it is `constexpr`) and walks the array. It starts at the end of the header (`ABIVersion`), and each entry must start where the last one ended. At the end the total must equal the size of the struct. A missing name, a swapped pair or a gap makes it return false, and the `static_assert` after it stops the build with a message that says what to do. The feature test then goes one step further: it requires that the feature scripts call every listed function at least once.

### Counting, and Dist

Each table entry normally points to a counting function, not to the host function. It adds one to a counter and forwards the call. Search the quote for the relaxed atomic add.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3646-L3656"
template<size_t Index, typename Result, typename... Arguments, Result (*Function)(Arguments...)>
struct CountedHostFunction<Index, Function>
{
	static_assert(Index < c_HostFunctionCount, "Host function missing from ST_SCRIPT_HOST_FUNCTIONS");

	static Result Call(Arguments... arguments)
	{
		s_HostCallCounts[Index].fetch_add(1, std::memory_order_relaxed);
		return Function(arguments...);
	}
};
```

1. **Lines 3646–3647:** the counting function is a template over the function's index in the list and the function itself.
2. **Line 3649:** a name that is missing from the list makes the index too large, and the build stops.
3. **Line 3653:** a relaxed `fetch_add` is the cheapest atomic add; `Log` may run on any thread, and readers only need totals that are right in the end.

The counters let tests ask which functions ran (`GetScriptHostCallCounts`) and reset them (`ResetScriptHostCallCounts`). A rejected call counts too, because the counter sits before the guards.

A shipped game does not need counters. In a :term[Dist]{id=dist} build, which strips diagnostics, `CreateHostAPI` assigns each `Host<Name>` directly to its table entry, so no call pays for an atomic add, and the call-count functions return an empty list.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3659-L3671"
	StrataScriptHostAPI CreateHostAPI()
	{
		StrataScriptHostAPI api = {};
		api.StructSize = sizeof(StrataScriptHostAPI);
		api.ABIVersion = ST_SCRIPT_ABI_VERSION;
#if defined(ST_DIST)
#define ST_SCRIPT_ASSIGN_HOST_FUNCTION(Name) api.Name = &Host##Name;
#else
#define ST_SCRIPT_ASSIGN_HOST_FUNCTION(Name) api.Name = &CountedHostFunction<GetHostFunctionIndex(offsetof(StrataScriptHostAPI, Name)), &Host##Name>::Call;
#endif
		ST_SCRIPT_HOST_FUNCTIONS(ST_SCRIPT_ASSIGN_HOST_FUNCTION)
#undef ST_SCRIPT_ASSIGN_HOST_FUNCTION
		return api;
```

1. **Line 3662:** `StructSize` records how large the table is.
2. **Line 3665:** in Dist the macro assigns the plain function.
3. **Line 3667:** in other builds it assigns the counting function, with the index computed from the member's offset.
4. **Line 3669:** the one list builds the whole table.

## The gameplay API as a facade

About 165 functions would be a big surface if each had its own implementation. Most do not: they are a thin face over services. The layer rule explains why. The :term[layer table]{id=layer-table} lets `Scripting` include only `Core`, `Input`, `Asset`, `Reflection` and `Scene`. It may not include `Physics`, `Audio`, `Animation`, `World` or `GameUI`, because a lower module may never name a higher one, and because games without physics must still run scripts.

So how does a script cast a ray? The Physics layer provides an object that implements the scene service `IPhysicsQueries` and registers it with the scene. The host function asks the scene for the service, `GetService<IPhysicsQueries>()`, and calls its abstract interface; it never learns which class answers. This is dependency inversion, which [the layers page](../core/layers-registries.md) explains. Scene services are declared in `Strata/src/Strata/Scene/SceneServices.h`; engine services, those a whole program provides, in `Strata/src/Strata/Core/EngineServices.h`, and the host finds them with `EngineServices::Get<T>()`.

When the service is absent, the function does not crash. It reports in words the engine chose and returns its failure value. Physics, audio and animation each have a message that says the scene plays without that module, because the engine has no such module. The game interface, the world and the window each have their own: the scene plays without the game interface, the scene streams no world, and the program running the game has no window to change. A program with no save folder gets a message that says the editor keeps saves in its open project.

Scripts never run in Simulate mode. The "Scripting" :term[scene system]{id=scene-system} is not created in Simulate mode, so a missing service never means "the editor is simulating". It means the engine was built without the module, the scene has no world, or the program has no window or save folder.

The table below groups the functions. It is a map for the reader; [the reference](../reference/script-api.md) holds the signatures and failure values. The last column gives the wave in which the group arrived. Rows marked initial stand before the first wave's entry in the list, which only grows at its end; the release notes of 0.3.0, the first release, already list every group down to :term[collision layers]{id=collision-layer}.

| Group | Functions (count) | Service or part reached | Arrived |
| --- | --- | --- | --- |
| Diagnostics | `Log`, `ReportException` | the log; the current call | initial |
| Time | `GetDeltaTime` to `SetTimeScale` (6) | the scene's clock | initial |
| Entities | `CreateEntity` to `GetChildren` (15) | the scene | initial |
| Components | `HasComponent`, `AddComponent`, `RemoveComponent`, `GetProperty`, `SetProperty` | the component registry | initial |
| Transform | `GetTransform`, `SetTransform`, and the world pair | the scene | initial |
| Scene | `GetPrimaryCamera`, `GetRootEntities`, `Instantiate` | the scene, its :term[asset manager]{id=asset-manager} | initial |
| Assets | `FindAsset`, `IsAssetLoaded`, `RequestAssetLoad` | the asset manager | initial |
| Scripts | `GetScriptInstance`, `HasScript`, `AddScript`, `RemoveScript` | the script system | initial |
| Input devices | keys, mouse buttons, position, delta, scroll | `Input` | initial |
| Physics bodies | velocities, forces, impulses, `Teleport` (11) | `IBodyControl`, `IBodyMotionQuery` | initial |
| Physics queries | `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` | `IPhysicsQueries` | initial |
| Audio | `AudioPlay` to `AudioGetMasterVolume` (10) | `IAudioPlayback`, `IAudioOutput` | initial |
| Game flow | `QuitGame`, `LoadScene` | the scene's quit and load requests | initial |
| Residency | `ReleaseAsset` | the asset manager | wave 1 |
| Scene streaming | `LoadSceneAdditive` to `InstantiateMany` (6) | the scene | wave 2 |
| Animators | `AnimatorPlay` to `AnimatorGetJointTransform` (12) | `IAnimatorControl` | wave 2 |
| Character controllers | `CharacterMove`, `Jump`, `Teleport`, `GetState` | `ICharacterControl` | wave 3 |
| Gamepads | connection, buttons, axes | `Input` | wave 3 |
| Cursor | `SetCursorMode`, `GetCursorMode` | `Input` | wave 3 |
| Window | `SetWindowMode`, `SetResolution`, `SetVSync`, `GetWindowSize` | `IGameWindow` | wave 3 |
| Save files | `WriteSaveFile`, `ReadSaveFile`, `DeleteSaveFile`, `ListSaveFiles` | `IGameSaves` | wave 3 |
| :term[Collision layers]{id=collision-layer} | `PhysicsSetLayersCollide`, `GetLayersCollide`, `GetLayerIndex` | the scene's layer matrix | wave 3 |
| Game interface, :term[unscaled time]{id=unscaled-time}, typed text | `UIGetText` to `UIIsActionDown` (15), `GetUnscaledDeltaTime`, `GetRealTime`, `GetTypedText` | `IUIControl`, `Input` | wave 4 |
| World streaming | `WorldRequestCellsAround` to `WorldIsLayerEnabled` (5) | `IWorldStreaming` | wave 4 |
| Input actions and binding capture | `InputIsActionDown` to `InputSaveBindings` (10), and three capture functions | `InputActions` | wave 6 |
| Graphics options | `GraphicsGetOptionCount` to `GraphicsSaveOptions` (7) | `IGameGraphics` | wave 7 |
| :term[Interpolation]{id=interpolation} | `GetStepAlpha`, `GetDrawnTransform`, `ResetInterpolation` | the scene's drawn poses | wave 8 |

The running total fits the story: 119 functions after wave 3 (which added 22), 142 after wave 4, 155 after wave 6, 162 after wave 7 and 165 with wave 8. Where a subsystem has a twin class in the SDK, its own page shows the script face: [physics queries](../physics/queries.md), [audio](../audio/scene-system.md), [animation](../animation/system.md) and [the game interface](../ui/input.md); the facade is taught once, here. A subsystem adds its own guards inside `HostCall`; the animator functions, for example, check that animation exists and that the entity has an animator, and report the reason if not.

## Player-facing services

Some services belong to the player, not to the game's logic: saves, input bindings, graphics options and the window. One service owns each file. A script that wrote the bindings file, the graphics options file or a save directly would race with the service that also writes it, and a corrupt file would be the players' loss. So scripts ask the owner: input actions through `InputActions`, graphics through `IGameGraphics` and saves through `IGameSaves`. Gameplay reads anything a player might want to change as an input action, not as a key, so changing the binding works.

The save service is the clearest example, because the engine checks the name before any path exists. `WriteSaveFile` asks `IGameSaves` for the folder; with none, it reports and fails. Then it checks the size, and only then does `SaveFiles::Write` check the name and write the file.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L2234-L2263" symbol="HostWriteSaveFile"
bool HostWriteSaveFile(StrataScriptContext* context, StrataScriptString name, const void* data, uint64_t size)
{
	return HostCall("WriteSaveFile", false, [&]()
	{
		ScriptSystem* system = ResolveContext(context, "WriteSaveFile");
		if (!system)
			return false;
		if (!data && size > 0)
		{
			system->ReportProblem("WriteSaveFile", "the data pointer is null");
			return false;
		}
		const std::optional<std::filesystem::path> directory = RequireSaveDirectory(*system, "WriteSaveFile");
		if (!directory)
			return false;
		if (size > SaveFiles::c_MaxFileSize)
		{
			system->ReportProblem("WriteSaveFile", fmt::format("{} bytes are more than a save file may hold ({} bytes)", size, SaveFiles::c_MaxFileSize));
			return false;
		}
		std::string error;
		const std::span<const uint8_t> bytes(static_cast<const uint8_t*>(data), static_cast<size_t>(size));
		if (!SaveFiles::Write(*directory, ScriptStringView(name), bytes, &error))
		{
			system->ReportProblem("WriteSaveFile", error);
			return false;
		}
		return true;
	});
}
```

1. **Line 2241:** a null data pointer with a size above zero is a script error, reported and refused.
2. **Lines 2246–2248:** the folder comes from the service; no folder means no save.
3. **Line 2249:** the size limit, 64 MiB (`SaveFiles::c_MaxFileSize`), is checked in the host before any byte is copied.
4. **Line 2256:** the name check happens in `SaveFiles::Write`, in the engine, so no script text ever becomes a path before validation.

A name is valid when it has 1 to 64 characters: letters of the basic Latin alphabet, digits, spaces, minus signs, underscores or dots. It may not start or end with a space or a dot, contain `..` or be a device name that Windows reserves, such as `CON`. A file is stored as `<name>.save` and written atomically, so a reader sees the old content or the new, never half of each. The calls block the main thread, so a script keeps saves small.

`SaveDirectory` is the `IGameSaves` that a shipped game provides. It finds its folder on first use, so a game that never saves creates nothing. The editor's play mode keeps saves in the project's `.strata/Saves`. Where an exported game puts them is the subject of [the game identity page](../worlds/game-identity.md).

## Value conversion

Values cross the table as `StrataScriptValue`. Two rules govern how they convert, and both come from the same idea: be strict where the engine controls both sides, and forgiving where the script has to name a property by text.

Script fields are exact. The module declares a field's type, the scene stores a value, and if they disagree the engine ignores the stored value and reports the two types.

Component properties are forgiving, because a script names them as text and cannot know the engine's type. An enum takes an :term[integer]{id=integer}, and a float takes an integer too. A three-number vector sets a `Color3`, a four-number vector sets a `Color4`, and a rotation takes a :term[quaternion]{id=quaternion} or a four-number vector in the order x, y, z, w. An integer outside the 32-bit range, a value of a wrong kind or an invalid string is reported by `SetProperty` with the component and property named, and the call returns false.

:::note
Field values convert exactly, and component properties by the property's kind. A field of the wrong type is reported and its stored value ignored; a property takes any value that can be read as its type.
:::

A string is at most `c_MaxScriptStringSize`, 256 MiB, and its data pointer must be set if its size is not zero.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Scripts link the engine and call its C++ classes | In-process native plug-ins | No packing step; every engine feature at once | Safe reload, crash containment and a stable interface; the compiler and settings must match |
| A managed language with generated bindings | Engines whose game code is managed code | Safer languages, richer editor support | A runtime to ship, a copy per crossing, less control over frame cost |
| Scripts in a separate process with messages | Tools and servers that must survive a hang | Full isolation, even from a hang | A message and a wait per call; no direct memory sharing |
| An embedded interpreter with registered functions | Studios that value quick changes | Small, fast to change, simple isolation | Game code no longer in C++; its own cost model |
| One generic `Call(name, arguments)` entry | Message-based plug-in interfaces | A tiny table that never changes | Type safety and cheap calls; every call parses a name |

## How it is tested

The `Scripting.*` suites in `StrataTests/src/Scripting/` check the host API from several sides. A suite is a group of tests under one prefix; run one with `build/windows/bin/Debug/StrataTests.exe --test-suite=Scripting.API`.

- `Scripting.API` covers entities, components, transforms, prefab creation, the full-scene report and the call counters. Its test `The host API rejects calls from outside script callbacks` calls the guards directly: no callback, null context, forged pointer, another thread.
- `Scripting.Faults`, `Scripting.Exceptions` and `Scripting.LoaderFaults` cover crashes, thrown exceptions and modules that fail to load.
- `Scripting.Physics`, `Scripting.Collisions`, `Scripting.Audio`, `Scripting.Animation`, `Scripting.UI`, `Scripting.World` and `Scripting.Streaming` check each subsystem's script face with its page.
- `Scripting.Game`, `Scripting.Input`, `Scripting.InputActions` and `Scripting.Graphics` cover the player-facing services.

The counters have their own test, `Every host function has a call counter`. It checks that the number of counters equals the table's size, and that the first is `Log` and the last `ResetInterpolation`. It checks that every name is distinct, that two `Log` calls and one rejected `IsEntityValid` leave exactly those counts, and that a reset clears them. Under Dist it checks that the list is empty. The feature test reads the same counters and fails when a listed function ran in no feature script; [the feature test page](../engineering/feature-test.md) explains its other checks.

## Changing it safely

To add a host function, append it at the end of the `StrataScriptHostAPI` struct and at the end of `ST_SCRIPT_HOST_FUNCTIONS`, never in the middle. Existing modules were built against the old layout, so inserting or changing the order moves every later entry and breaks them. Write `Host<Name>` with `ResolveContext` and `HostCall`, and let the SDK test for the new entry through `ST_SCRIPT_DETAIL_HOST_WITH`, so that a module built against an older table still runs. Then exercise it from the test script module, a `Scripting.*` test and the feature scripts.

Appending keeps `ST_SCRIPT_ABI_VERSION`; an incompatible change bumps it. [The tutorial](../scripting/tutorial-host-function.md) does it step by step.

- Go through a scene service or an engine service for anything that lives above `Scripting`; never add an include to the layer table or a line to the :term[allowlist]{id=allowlist} to make one pass.
- Destroy entities through `ScriptSystem::DestroyEntity`, never directly: the script that called may still be running.
- Report misuse with `ReportProblem` and return the failure value; do not assert, throw or log with `ST_CORE_ERROR`.
- Keep the body on the main thread; background work goes through the job system and returns through a polled queue.

The checks to pass are the `static_assert` (the build), `Scripting.API`'s counter test and the feature test.

## Summary

- Game code reaches the engine through a table of C function pointers and an opaque context, so it needs no engine header, reloads safely and can be tested by counting calls.
- A host call goes from an SDK function through a counting function to a `Host<Name>` function, which starts with `ResolveContext`, wraps its body in `HostCall`, validates input and reports misuse through `ReportProblem`.
- A new host function is appended to the struct and to `ST_SCRIPT_HOST_FUNCTIONS`; a `static_assert` fails the build when the list and the struct disagree, and Dist builds drop the counters.
- Scripting includes only five layers, so gameplay functions go through scene services and engine services and fail with a reported message when the service is absent.

## Check yourself

1. A script calls `SetTimeScale` from a thread it started. What happens, and which line of the engine decides?

   :::answer{tests="host-guards"}
   The call is refused. `ResolveContext` compares the calling thread with the owner thread and logs "scripts can only use the engine from the main thread", then returns null; the host function returns without touching the scene. The registry is not even read, because only the main thread may touch it.
   :::

2. Which statement about `HostCall` is right? (a) It checks the context. (b) It stops exceptions at the table and returns the failure value. (c) It reports problems to the scene's log. (d) It counts calls.

   :::answer{tests="host-guards"}
   (b). Option (a) is `ResolveContext`'s job, (c) belongs to `ReportProblem` and (d) to the counting function that sits before the host function.
   :::

3. A script bug makes `Instantiate` fail every frame with the same text. How many warnings appear, and when do they stop?

   :::answer{tests="host-guards"}
   One, because the same text is reported once per scene. The scene reports at most 1,024 different texts and then says that further problems are not reported.
   :::

4. A developer adds `GetFoo` to `StrataScriptHostAPI` but forgets the list. What happens, and why is that better than a null entry?

   :::answer{tests="host-table"}
   The build fails at the `static_assert`, because `ListsEveryHostFunction` finds that the entries do not cover the struct. A null entry would crash a script that called it, and only at run time.
   :::

5. Why can a scripting function not include the physics module's header to cast a ray?

   :::answer{tests="host-services,host-pattern"}
   The layer table lets `Scripting` include only five layers, and a game may be built without physics. The function asks the scene for `IPhysicsQueries` and reports "the scene plays without physics" when it is null.
   :::

## Exercises

1. **Basic.** Change the toy so that it counts the calls the first guard refuses and the calls it lets through, and prints both. Name the one place where the change goes.

   :::answer[Worked solution]{tests="host-guards"}
   The counters go inside `ResolveContext`: one step in each of the three refusing branches, one before `return context`. The six calls of `main` give 3 refused (no call in progress, a null context, the other thread) and 3 let through. Those are the negative value, which the function rejects later, the last `SetTimeScale` and the `GetTimeScale` inside the final `printf`. The negative value passes the first guard because that guard checks who calls, not what is passed.
   :::

2. **Medium.** Write a function `ReportProblem(function, message)` that prints a warning once per distinct text and stops after three texts with a line saying that further problems are not reported. Call it five times, repeating one text, and predict the output.

   :::answer[Worked solution]{tests="host-guards"}
   The program keeps each printed text in a `std::set`. The text is printed only when the set accepts it as new, and nothing is printed once the set holds three texts.

   ```cpp sketch="scripting-host-api-once.cpp"
   #include <cstddef>
   #include <cstdio>
   #include <set>
   #include <string>

   constexpr size_t c_MaxProblems = 3;
   static std::set<std::string> s_Reported;

   // Reports a problem once per text, and stops at c_MaxProblems distinct texts.
   static void ReportProblem(const std::string& function, const std::string& message)
   {
   	const std::string text = function + ": " + message;
   	if (s_Reported.size() >= c_MaxProblems)
   		return;
   	if (!s_Reported.insert(text).second)
   		return;

   	std::printf("warning: %s\n", text.c_str());
   	if (s_Reported.size() == c_MaxProblems)
   		std::printf("further problems are not reported\n");
   }

   int main()
   {
   	ReportProblem("SetTimeScale", "negative");
   	ReportProblem("SetTimeScale", "negative");
   	ReportProblem("Instantiate", "not loaded");
   	ReportProblem("Raycast", "zero direction");
   	ReportProblem("GetProperty", "no such property");
   	return 0;
   }
   ```

   ```text output-of="scripting-host-api-once.cpp"
   warning: SetTimeScale: negative
   warning: Instantiate: not loaded
   warning: Raycast: zero direction
   further problems are not reported
   ```

   1. **Lines 13–14:** past the cap, a problem is dropped.
   2. **Lines 15–16:** a text already in the set is dropped.
   3. **Lines 18–20:** a new text is printed, and the last one announces the cap.

   The first call prints. The repeat is ignored because its text is in the set. The third and fourth calls add texts two and three, and the third text is followed by the line that says further problems are not reported. The fifth call finds the set full and returns silently. The real function differs in that it adds the script name and entity to the text and uses a cap of 1,024.
   :::

3. **Hard.** Trace it yourself: find the function that handles `Time::SetTimeScale` in the engine and the file where the SDK calls the table. Name each guard on the way.

   :::answer[Worked solution]{tests="host-guards,host-table"}
   Search for `SetTimeScale` in `StrataScriptCore/Include/StrataScript/Time.h`: the SDK function `Time::SetTimeScale` calls `host->SetTimeScale(Detail::GetContext(), timeScale)`. The table entry is built in `CreateHostAPI` of `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, which points to `CountedHostFunction<...>::Call` outside Dist. That forwards to `HostSetTimeScale`, whose guards are `HostCallVoid`, `ResolveContext` and the finite, non-negative check, then `Scene::SetTimeScale`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: the host functions, `ResolveContext`, `HostCall`, the X-macro list and the counters; `ScriptHostAPI.h`: the function that returns the table, context registration and call counts.
- `Strata/src/Strata/Scripting/ScriptSystem.cpp`: `ScriptSystem::ReportProblem`; `ScriptValue.cpp`: value conversion.
- `Strata/src/Strata/Core/SaveFiles.h` and `EngineServices.h`: the save service and the engine services.
- `StrataScriptCore/Include/StrataScript/Entity.h`: the SDK's side of a property call.
- Tests: `StrataTests/src/Scripting/ScriptAPITests.cpp`, the `Scripting.*` suites and `StrataTests/FeatureTest/`.

## Further reading

- The Vulkan specification's chapter on loader and layer interfaces: how a table of function pointers carries an API across a library boundary; advanced.
- A C++ reference on `offsetof` and `static_assert`, for the table's check; intermediate.
- A textbook chapter on plug-in architectures and the opaque pointer idiom; intermediate.

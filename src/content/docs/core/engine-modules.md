---
id: core/engine-modules
title: "Engine modules"
description: "How a Strata program starts its long-lived services in dependency order, runs their hooks every frame, stops them in reverse and lets other code find them."
kind: internals
size: L
tracks: [E]
needs: [core/frame-loop, basics/trees-graphs]
time: 85
learn:
  - id: hook-order
    text: name the order in which Strata calls the hooks of its modules in a frame and when the program ends
  - id: kahn-order
    text: compute the start order of a list of modules with Kahn's algorithm and the listing-order rule
  - id: refusals
    text: predict which lists of modules the registry refuses and which names its message gives
  - id: write-module
    text: write an engine module, list it in a program and test it with a journal of its hooks
  - id: find-service
    text: choose between finding a module with Find and asking for an engine service, and give the reason
since: 0.4.0
status: final
---

A Strata program needs a few services that live exactly as long as the program does: the graphics device, the sound mixer, the Dear ImGui interface and the open project. Each one must start before the code that uses it, do a little work in every frame, and stop only after that code has stopped. An **engine module** is such a service: a class that implements the `EngineModule` interface and names the modules it must start after. It offers a fixed set of functions that the application calls at set moments of the program's life.

This page teaches how Strata orders its modules, what each function promises, what happens when a module cannot start, and how other code finds a module or a service without naming it. It does not teach what the built-in modules do inside. [Vulkan and NVRHI](../gpu/vulkan-nvrhi.md) makes the graphics device, and [the audio engine](../audio/engine.md) mixes sound. [Dear ImGui and its backends](../editor-ui/imgui-backends.md) draw the editor, and [projects and settings](../world/projects-settings.md) open the project.

This page needs no project and no download. Its sketch is a whole program for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). Its test commands, its traces and the patch that solves exercise 2 need the source build of [your first engine change](first-change.md#build-the-engine-and-start-the-editor), in `Debug`.

## The problem and how engines solve it

Take the editor with a window. It runs four services. The graphics device draws pictures, and the audio engine mixes sound. Dear ImGui draws the panels into the image that goes to the screen. The project holds the asset manager, and every loaded texture in that manager owns memory on the graphics device.

Those four have a start order. The device starts first, because ImGui and the textures need it, and ImGui starts after it. The stop order is the opposite: the textures must be freed while the device still exists, because freeing a texture is a call into the device. Break either order and the program fails, usually at exit and far from the line that caused it. The problem is to get both orders right in every program: the editor, the editor without a window, the game that has no ImGui, and every test.

Engines have used four answers.

- A list of calls in `main`: start the device, start audio, start the interface, run the loop, then stop everything in the opposite order. It needs no machinery, and a reader sees the whole order. But every program writes its own two lists, and nothing checks that the stop list mirrors the start list.
- Global manager objects with `StartUp` and `ShutDown` functions, which `main` calls in order. The textbook *Game Engine Architecture* describes this as a common design. The order still lives in `main`, and a global object is hard to replace in a test.
- A module system. The `IModuleInterface` of Unreal Engine gives every module `StartupModule` and `ShutdownModule` functions and a loading phase, and the engine loads modules by name. This frees `main` from the list and lets other people add modules. The cost is the machinery: a loader, phases and a build that knows both.
- A **service locator**: a global table from which code asks for a service by its type instead of receiving it. It answers where code finds a service, not when the service starts, so it needs one of the other answers beside it. The book *Game Programming Patterns* weighs its costs: the dependency is hidden, and a lookup can fail.

Strata takes a middle way. Each module is an object with a name and a list of the modules it starts after. A program lists the factories of its modules in any order, and a registry sorts them so that every module comes after the modules it needs. The application calls the hooks forward at the start and backward at the end. Where a lower layer needs something that only a higher layer can provide, a small locator holds it.

The order of starting is not the whole problem, because stopping has three moments. Suppose the project module let go of the asset manager in the same step in which the graphics module destroyed the device. Each texture would call into a device that no longer exists. Strata therefore splits the end into three hooks around the stop of the job system, so that assets go while the job system and the device still live.

## Ordering by dependencies: the topological sort

The registry has one hard job: from a list of modules and what each starts after, produce a list in which every module comes after the modules it needs. [Trees and graphs](../basics/trees-graphs.md) introduced the picture. Draw one node for each module, and for each need an arrow from the module that is needed to the module that needs it. An arrow from A to C says that C starts after A, so the arrows point the way time runs.

A **topological sort** is a list of all nodes of a :term[directed graph]{id=directed-graph} in which every arrow points forward, from an earlier node to a later one. Such a list exists exactly when the graph has no cycle. A cycle has no first node, because each member would wait for another.

**Kahn's algorithm** builds the list one node at a time, always taking a node that waits for nothing. It needs one number for each node: how many modules the node still waits for. Graph books call it the in-degree, the count of arrows that point at the node. The steps are:

1. Compute the waiting count of every node.
2. Take a node whose count is 0, and put it at the end of the list.
3. Subtract 1 from the count of every node that waits for the placed node.
4. Repeat from step 2 until every node is placed, or until no node left has a count of 0.

:::example[Kahn's algorithm on the registry's test list]
`StrataTests/src/Core/EngineModuleTests.cpp` lists four modules in this order: C, A, B and D. C starts after A, B starts after C, and D starts after a module named Missing, which the program does not run. The last two needs only order the modules, and Missing adds no arrow because it is not in the program. The arrows are A to C and C to B, so the waiting counts are C 1, A 0, B 1 and D 0. A dash marks a placed module.

| Step | Counts of C, A, B, D | Ready, in listing order | Placed |
| --- | --- | --- | --- |
| 1 | 1, 0, 1, 0 | A, D | A |
| 2 | 0, -, 1, 0 | C, D | C |
| 3 | -, -, 0, 0 | B, D | B |
| 4 | -, -, -, 0 | D | D |

The start order is A, C, B, D, and the test checks exactly this list.
:::

Two modules were ready at step 1, so the algorithm needs a rule to choose. Strata takes the first ready module in the program's listing, so at step 2 it took C over D, although D had been ready since the start. The usual textbook version keeps the ready nodes in a queue, and would place A, then D, then C, then B, because D joined the queue before C. Both lists are valid. Strata's rule lets the program's list decide every choice that the arrows leave open, so a programmer predicts the order by reading the list.

The rule has a price. Every step scans the listing from its start, so a list of $n$ modules costs at most $n \times n$ checks, which is 16 for four modules. A queue needs a number of steps in proportion to the modules plus the arrows. With four or five modules the difference does not matter.

A cycle makes the algorithm stop early: some modules are left, and none has a count of 0. Take five modules listed as A, B, C, D and E. A starts after C, B after A, C after B, and D after C. E waits for nothing. The algorithm places E, and the other four keep a count of 1.

Naming all four in an error would mislead, because D only waits for the cycle. Strata removes from the leftover set every module that no other leftover module waits for, and repeats until nothing more goes. D goes first. A, B and C stay, because another leftover waits for each of them. The message names them: `engine modules 'A', 'B' and 'C' depend on each other in a cycle`.

## The map: the hooks of two modules

Two modules make the order of the hooks visible. Module B starts after module A, and the program lists B first, so the registry sorts them to A, B. The registry's test checks the order below with a journal that records every hook.

```mermaid caption="The order in which the application calls the hooks of two modules, where B starts after A: forward at the start and in the frame, backward at the end." alt="A sequence diagram with three lanes, the application, module A and module B. Both modules get their start call in the order A, B. In each frame the begin, update and user interface hooks go to A and then B, and the end hook goes to B and then A. At the end the stop, release and final hooks go to B and then A."
sequenceDiagram
	participant App as Application
	participant A as Module A
	participant B as Module B
	Note over App,B: Start
	App->>A: OnInit
	App->>B: OnInit
	Note over App,B: Every frame
	App->>A: OnBeginFrame
	App->>B: OnBeginFrame
	Note over App: the layers update
	App->>A: OnUpdate
	App->>B: OnUpdate
	App->>A: OnRenderUI
	App->>B: OnRenderUI
	App->>B: OnEndFrame
	App->>A: OnEndFrame
	Note over App,B: End
	App->>B: OnStop
	App->>A: OnStop
	Note over App: the layers are destroyed
	App->>B: OnRelease
	App->>A: OnRelease
	Note over App: the job system stops
	App->>B: OnShutdown
	App->>A: OnShutdown
```

Three things stand out. Only `OnEndFrame` runs backward in the frame, so the module that began a frame first finishes it last. The layers update between the begin and update hooks, so a module's `OnBeginFrame` runs before any layer's work and its `OnUpdate` after. The end has three hooks, with the destruction of the layers and the stop of the job system between them.

Everything runs on the :term[main thread]{id=main-thread}. The `Application` owns the registry, the registry owns the modules, and each module owns what it wraps: the graphics module owns the device. [One frame in order](frame-loop.md) shows where in `Application::RunFrame` the calls stand.

## The contract

A **hook** is a function that a framework calls at a set moment so that your code can act there. Two functions of `EngineModule` have no default, because every module must answer them: `GetName` and `OnInit`. Every other hook has an empty body, so a module writes only the moments it cares about.

| Hook | When the application calls it | What the module does |
| --- | --- | --- |
| `GetDependencies` | Before anything starts | Lists the modules it starts after; `Required` false makes an entry an ordering only |
| `OnInit` | In the `Application` :term[constructor]{id=constructor}, after the job system, the window and the input started | Returns false when it cannot run, after cleaning up |
| `GetStartFailure` | After `OnInit` returned false | Returns a problem and advice for the person |
| `OnBeginFrame` | Each frame, after the input and before the layers update | Returns `Continue`, `Skip` or `Close` |
| `OnUpdate` | After the layers update | Does the work of the frame |
| `OnRenderUI` | After every module's `OnUpdate` | Draws interface; the frame's :term[work time]{id=work-time} ends after it |
| `OnEndFrame` | In reverse order, only for frames that ran | Presents and captures |
| `OnEvent` | For every event, before the layers | Sets `Handled` to keep the event from going further |
| `OnStop` | Once, when the loop ended; the layers still exist | Stops work that needs the layers |
| `OnRelease` | In the `Application` :term[destructor]{id=destructor}, once the layers are gone; the job system still runs | Lets go of assets and the project |
| `OnShutdown` | Once the job system stopped | Destroys the last things, such as the device |

The hooks get their data in three :term[structs]{id=struct} and one enumeration. `EngineContext` gives `OnInit` the application, the window (null in a program without one) and the registry, in which the module finds the modules it depends on, already started. `EngineFrame` gives the frame hooks the `Step` of time, `WaitSeconds` and the layer stack. A module adds to `WaitSeconds` the time it spent waiting for something outside the program, such as the :term[graphics processing unit]{id=gpu} (GPU) or the display, and the frame's work time leaves that time out. `EngineModuleStartFailure` holds a `Problem` and an `Advice` text; an empty `Problem` means that only the log names the module.

`EngineFrameAction` is the answer of `OnBeginFrame`, and `Continue` runs the frame. `Skip` says that nothing can be drawn now, for example while the window changes size. The frame ends at once, no other hook runs for it, the loop does not count it, and the loop waits 16 ms. `Close` says that the program cannot continue, for example after a lost device. The frame ends at once, as for `Skip` but without the wait, and the loop then ends.

:::example[Skip and Close in the registry's test]
Module A returns `Skip` at its second call of `OnBeginFrame` and `Close` at its fourth. Module B comes after it, and the program may run 10 frames; frame 1 runs. Frame 2 stops at A, so B gets no begin call, and the loop does not count the frame. Frame 3 runs, and at frame 4 A closes the program, so B again gets nothing. A saw 4 begin calls, B saw 2, the program counted 2 frames, and the layers updated twice.
:::

The registry adds rules on the whole list. `Create` makes every module from its factory and refuses the list, keeping nothing, in four cases. They are a factory that makes no module, two modules with one name, a required dependency that the program does not run, and a cycle. The error text names the modules, and the application reports `<name> cannot start: <error>.` to the person and exits with code 1. A missing optional dependency is no refusal; the registry ignores it, as Missing showed.

A module type that other code finds declares `static constexpr std::string_view c_Name`. `Find<T>()` calls `Find(T::c_Name)` and casts the result to `T*`. No run-time type information is involved: the name decides, and the comparison is exact, so `Find("beta")` does not find `Beta`. The result is null when the program does not run that module.

:::rule[Engine modules]
`Application` never names a module and runs no code of a module but its hooks. Other code finds a module with `GetModules().Find<T>()`, which may return null. Programs run different sets of modules: the headless editor has no ImGui, and a shipped game has none at all. Code that assumed a module would crash in the programs without it. [Layers and registries](layers-registries.md) shows how programs list their modules.
:::

Two more rules come from the header's comments. A module whose `OnInit` fails cleans up what it started and describes the failure, because the application ends only the modules that started, and the failed one gets no other hook. `OnRelease` comes before the stop of the job system and `OnShutdown` after it. Asset managers wait for their load jobs when destroyed, and assets own GPU resources, so assets must go while both the job system and the device exist.

## A toy version

The toy orders modules the way the registry does. It stores for each module the names it starts after, counts the modules each one waits for, and places the first ready module in listing order until none is ready. It runs on the test's four modules and on the five-module cycle, and prints the counts, each placement and the modules left over. It omits the checks that the real registry makes before it sorts.

```cpp sketch="core-engine-modules-toy.cpp"
// A toy of the engine's module ordering: Kahn's algorithm that always takes the first ready module in listing order.
#include <cstdio>
#include <string>
#include <vector>

struct Module
{
	std::string Name;
	std::vector<std::string> After; // the modules this one starts after
};

static size_t FindModule(const std::vector<Module>& modules, const std::string& name)
{
	for (size_t index = 0; index < modules.size(); index++)
	{
		if (modules[index].Name == name)
			return index;
	}
	return modules.size();
}

// Returns the start order. What waits for a cycle never becomes ready: its indices go into `stuck`.
static std::vector<size_t> Order(const std::vector<Module>& modules, std::vector<size_t>& stuck)
{
	const size_t count = modules.size();
	std::vector<std::vector<size_t>> dependents(count); // who waits for this module
	std::vector<size_t> pending(count, 0);              // how many modules this one still waits for
	for (size_t index = 0; index < count; index++)
	{
		for (const std::string& name : modules[index].After)
		{
			const size_t target = FindModule(modules, name);
			if (target == count)
				continue; // an optional module that the program does not run
			dependents[target].push_back(index);
			pending[index]++;
		}
	}

	std::printf("waiting:");
	for (size_t index = 0; index < count; index++)
		std::printf(" %s=%zu", modules[index].Name.c_str(), pending[index]);
	std::printf("\n");

	std::vector<bool> placed(count, false);
	std::vector<size_t> order;
	while (order.size() < count)
	{
		size_t next = count;
		for (size_t index = 0; index < count && next == count; index++)
		{
			if (!placed[index] && pending[index] == 0)
				next = index;
		}
		if (next == count)
			break; // nothing is ready: the rest waits for a cycle
		placed[next] = true;
		order.push_back(next);
		std::printf("place %s\n", modules[next].Name.c_str());
		for (const size_t dependent : dependents[next])
			pending[dependent]--;
	}

	for (size_t index = 0; index < count; index++)
	{
		if (!placed[index])
			stuck.push_back(index);
	}
	return order;
}

int main()
{
	const std::vector<std::vector<Module>> programs =
	{
		{ { "C", { "A" } }, { "A", {} }, { "B", { "C" } }, { "D", { "Missing" } } },
		{ { "A", { "C" } }, { "B", { "A" } }, { "C", { "B" } }, { "D", { "C" } }, { "E", {} } }
	};
	for (const std::vector<Module>& modules : programs)
	{
		std::vector<size_t> stuck;
		Order(modules, stuck);
		if (!stuck.empty())
		{
			std::printf("stuck:");
			for (const size_t index : stuck)
				std::printf(" %s", modules[index].Name.c_str());
			std::printf("\n");
		}
		std::printf("\n");
	}
	return 0;
}
```

```text output-of="core-engine-modules-toy.cpp"
waiting: C=1 A=0 B=1 D=0
place A
place C
place B
place D

waiting: A=1 B=1 C=1 D=1 E=0
place E
stuck: A B C D
```

1. **Lines 26–27:** two tables do the whole work: who waits for a module, and how many modules each one still waits for.
2. **Lines 33–34:** a name that no module has adds no wait, as for Missing.
3. **Lines 50–54:** the scan starts at the top of the listing each time, so the first ready module wins.
4. **Lines 57–61:** placing a module lowers the count of every module that waited for it.

The first run reproduces the table above: A, C, B, D. In the second run all counts but E's are 1, so only E is ready. The toy reports four left-over modules where the real registry names three, because the real code also removes the modules that only wait for the cycle.

## The real code: the interface and the registry's sort

The header comment states the contract that the table summarized. Search for the two functions without a default body and for the one hook whose default returns a value.

```cpp src="Strata/src/Strata/Core/EngineModule.h#L65-L106"
// A service the application runs for the whole program (the graphics device, audio, Dear ImGui, the project) with its own
// startup, frame and shutdown hooks. Programs list the modules they run (ApplicationSpecification::Modules); Application
// never names one, and calls the hooks in the order of the table in Docs/Architecture.md ("Application and frame loop"):
// startup, the frame's hooks other than OnEndFrame and events in dependency order, OnEndFrame, stopping, releasing and
// shutting down in reverse. Modules that never started (OnInit failed or never ran) get no other hook. Main thread.
//
// A module type that EngineModuleRegistry::Find<T> finds declares `static constexpr std::string_view c_Name`, the name
// GetName returns.
class EngineModule
{
public:
	virtual ~EngineModule() = default;

	virtual std::string_view GetName() const = 0;
	// Modules this one starts after. A missing required dependency refuses the program's start.
	virtual std::span<const EngineModuleDependency> GetDependencies() const { return {}; }

	// In the Application constructor, after the job system, the window and Input. False: the program cannot run (the
	// module cleans up what it started itself, logs why and may describe it for a person: GetStartFailure).
	[[nodiscard]] virtual bool OnInit(EngineContext& context) = 0;
	virtual EngineModuleStartFailure GetStartFailure() const { return {}; }

	// After the frame's Input stage, before the layers update. A module that returns Skip or Close ends the frame there:
	// the modules after it get no OnBeginFrame, and no module gets the frame's other hooks.
	virtual EngineFrameAction OnBeginFrame(EngineFrame&) { return EngineFrameAction::Continue; }
	// After the layers' OnUpdate.
	virtual void OnUpdate(EngineFrame&) {}
	// After every module's OnUpdate: user interface over the frame (Dear ImGui calls the layers' OnImGuiRender here).
	// The frame's work time ends after this hook.
	virtual void OnRenderUI(EngineFrame&) {}
	// After the work time was measured, in reverse order, only for frames that ran (presenting, captures).
	virtual void OnEndFrame(EngineFrame&) {}
	// Every event, after the application's own bookkeeping and before the layers; one a module handles goes no further.
	virtual void OnEvent(Event&) {}

	// Once, when Application::Run's loop ended; the layers still exist.
	virtual void OnStop() {}
	// In the Application destructor, once the layers are gone; the job system still runs.
	virtual void OnRelease() {}
	// Once the job system has stopped: the last hook.
	virtual void OnShutdown() {}
};
```

1. **Lines 65–72:** the contract in prose: the order of the calls, no other hook for a module that never started, the main thread, and the name `Find<T>` uses.
2. **Line 84:** `OnInit` is pure and `[[nodiscard]]`, so a module cannot ignore its own failure.
3. **Lines 87–89:** `OnBeginFrame` is the only frame hook with a result, and its comment says what `Skip` and `Close` do.
4. **Lines 100–105:** the three end hooks, each with the moment that tells it from the others.

The registry's public face is small. `Create` takes the factories as a span, so programs build the list as they like, and `Find<T>` is the whole lookup mechanism.

```cpp src="Strata/src/Strata/Core/EngineModule.h#L121-L135"
// Makes the modules of the factories and orders them. Refuses (nothing is kept, outError names the modules) a factory
// that makes no module, two modules with one name, a required dependency the list lacks and dependencies in a cycle.
bool Create(std::span<const EngineModuleFactory> factories, std::string* outError = nullptr);
// Destroys the modules, last first.
void Clear();

// The modules in dependency order.
std::span<EngineModule* const> GetAll() const { return m_Modules; }
size_t GetCount() const { return m_Modules.size(); }
EngineModule* Find(std::string_view name) const;
template<typename T>
T* Find() const
{
	return static_cast<T*>(Find(T::c_Name));
}
```

1. **Line 123:** `Create` returns false and writes the refusal into `outError`, so the caller decides how to tell the person.
2. **Lines 131–135:** `Find<T>` casts the result of the name lookup: no run-time type information.

`Create` first makes the modules and collects problems, and sorts only when the list has none, so a cycle appears only in an otherwise valid list. The sort is the toy's.

```cpp src="Strata/src/Strata/Core/EngineModule.cpp#L95-L129" from="// Kahn's algorithm, always taking" to="pending[dependent]--;" symbol="EngineModuleRegistry::Create"
// Kahn's algorithm, always taking the first ready module in the program's listing order: dependencies first,
// the listing order wherever they leave a choice.
const size_t count = modules.size();
std::vector<std::vector<size_t>> dependents(count);
std::vector<size_t> pending(count, 0);
for (size_t index = 0; index < count; index++)
{
	for (const EngineModuleDependency& dependency : modules[index]->GetDependencies())
	{
		const size_t target = findModule(dependency.Name);
		if (target == count)
			continue; // An optional module the program does not run
		dependents[target].push_back(index);
		pending[index]++;
	}
}
std::vector<bool> placed(count, false);
order.reserve(count);
while (order.size() < count)
{
	size_t next = count;
	for (size_t index = 0; index < count; index++)
	{
		if (!placed[index] && pending[index] == 0)
		{
			next = index;
			break;
		}
	}
	if (next == count)
		break; // The rest wait for each other
	placed[next] = true;
	order.push_back(next);
	for (const size_t dependent : dependents[next])
		pending[dependent]--;
```

1. **Lines 98–99:** the same two tables as the toy: `dependents` and `pending`.
2. **Lines 105–106:** a dependency that no module satisfies is skipped, because the loop before the sort refused every required one.
3. **Lines 116–125:** the scan stops at the first ready module; when none is ready the loop ends and the rest wait for each other.

What remains after the loop is a cycle plus the modules that wait for it. The report removes the second group.

```cpp src="Strata/src/Strata/Core/EngineModule.cpp#L131-L159" from="if (order.size() < count)" to="QuoteNames(cycle)));" symbol="EngineModuleRegistry::Create"
if (order.size() < count)
{
	// What is left waits for a cycle. Modules that only wait for it (no module left waits for them) are not part
	// of it: leave them out of the message, until only the cycles remain.
	std::vector<bool> inCycle(count, false);
	for (size_t index = 0; index < count; index++)
		inCycle[index] = !placed[index];
	for (bool removed = true; removed;)
	{
		removed = false;
		for (size_t index = 0; index < count; index++)
		{
			if (!inCycle[index])
				continue;
			const bool awaited = std::any_of(dependents[index].begin(), dependents[index].end(), [&](size_t dependent) { return inCycle[dependent]; });
			if (!awaited)
			{
				inCycle[index] = false;
				removed = true;
			}
		}
	}
	std::vector<std::string_view> cycle;
	for (size_t index = 0; index < count; index++)
	{
		if (inCycle[index])
			cycle.push_back(modules[index]->GetName());
	}
	problems.push_back(fmt::format("engine modules {} depend on each other in a cycle", QuoteNames(cycle)));
```

1. **Lines 138–152:** the removal loop: a candidate that no other candidate waits for is dropped, and the loop repeats until nothing changes.
2. **Lines 153–159:** the names come out in listing order and form one message.

A module that depends on itself is a cycle of one: it waits for itself and is never ready. The message then reads `engine modules 'A' depend on each other in a cycle`, although only one module is named. A module on the way between two cycles stays in the message too, because another leftover waits for it.

## The real code: starting and failing

`Application::StartModules` calls the sort and then `OnInit` of each module. Look at what happens after a module returns false.

```cpp src="Strata/src/Strata/Core/Application.cpp#L126-L160" symbol="Application::StartModules"
bool Application::StartModules()
{
	std::string error;
	if (!m_Modules.Create(m_Specification.Modules, &error))
	{
		Input::SetWindow(nullptr);
		m_Window.reset();
		ReportFatalError(m_Specification.Name, fmt::format("{} cannot start: {}.", m_Specification.Name, error));
		return false;
	}

	EngineContext context { *this, m_Window.get(), m_Modules };
	for (EngineModule* module : m_Modules.GetAll())
	{
		if (module->OnInit(context))
		{
			m_StartedModules++;
			continue;
		}
		ST_CORE_CRITICAL("Engine module '{}' could not start; the application cannot run", module->GetName());
		// The person learns what the module describes once nothing of the program is left on the screen: the modules that
		// started end in their usual order, then the window, which would never show anything, closes. The layers those
		// modules pushed (ImGui's overlay) go first, as in ~Application, so that no layer outlives what it uses; the
		// program's own layers do not exist yet.
		const EngineModuleStartFailure failure = module->GetStartFailure();
		m_LayerStack.Clear();
		ShutDownModules();
		Input::SetWindow(nullptr);
		m_Window.reset();
		if (!failure.Problem.empty())
			ReportFatalError(m_Specification.Name, failure.Problem, failure.Advice);
		return false;
	}
	return true;
}
```

1. **Lines 129–135:** a refused list ends before any module starts: the window closes and the person reads `<name> cannot start: <error>.`
2. **Lines 140–143:** each module that starts is counted, and the count decides who gets the end hooks.
3. **Lines 150–152:** the failure text is read first, then the layers go, then only the started modules end.
4. **Lines 155–156:** the report comes last, when nothing of the program is left on the screen.

The test for this path lists A, B and C with B failing. The journal reads `Init A`, `Init B`, `Detach A layer`, `Release A jobs`, `Shutdown A no jobs`. C never starts, and B gets nothing after its failed `OnInit`, so B must clean up for itself.

## The built-in modules and the programs' lists

Four modules ship with the engine. `Graphics` makes the device in `OnInit`, waits for the GPU in `OnBeginFrame` and adds the wait to `WaitSeconds`, presents in `OnEndFrame`, and destroys the device in `OnShutdown`, the last moment. `Audio` starts the audio engine; a machine without an output device runs on without sound, so its `OnInit` returns true even then. `ImGui` requires `Graphics` and a window, and its `OnInit` returns false without them. `Project` is the smallest module.

```cpp src="Strata/src/Strata/Project/ProjectModule.cpp#L10-L24"
EngineModuleFactory ProjectModule::Factory()
{
	return []() -> Scope<EngineModule> { return CreateScope<ProjectModule>(); };
}

bool ProjectModule::OnInit(EngineContext&)
{
	return true;
}

void ProjectModule::OnRelease()
{
	AssetManager::SetActive(nullptr);
	Project::SetActive(nullptr);
}
```

1. **Lines 10–13:** the factory is a function that makes one module; programs list it.
2. **Lines 20–24:** the only work is in `OnRelease`: it clears the active asset manager and project after the layers are gone, and before the job system stops.

The program's layers open the project, so the module holds no reference of its own. A test lists a probe module before it, so that the probe is released after it, and checks that the manager is already destroyed and the jobs still run.

The device is made in `OnInit` of `Graphics`, and another page teaches it in full. The module fills a `GraphicsDeviceSpecification` (headless when there is no window, validation on in Debug builds unless told otherwise) and calls `GraphicsDevice::Create`, which builds the Vulkan device. With a window that can present, it creates the images that reach the screen. Then it calls `Renderer::Init`. If a step fails, it drops the device and describes the failure for `GetStartFailure`: no usable device, Vulkan 1.2 or later needed, with advice about the driver.

Each program lists the modules it runs.

| Program | Modules in listing order |
| --- | --- |
| Editor with a window | Graphics, Audio, ImGui, Project |
| Editor with `--headless` | Graphics with no window, Audio with the null device, Project |
| Editor with `--no-gpu` | Audio with the null device, Project |
| :term[Runtime]{id=runtime} with a window | Graphics, Audio when the build has it, Project |
| Runtime with `--headless` | Audio with the null device when the build has it, Project |

`CreateApplication` in `StrataEditor/src/EditorApplication.cpp` builds the editor's list. The option `--no-gpu` also makes the program headless, so ImGui, which needs a window, drops out too. Each list is already in dependency order, so the sort changes nothing for it. It would matter if ImGui came before Graphics.

## Engine services

The registry gives a module to code that can include the module's header, such as a program, but some code may not. Here a layer means an architecture layer, a group of the engine's folders, not an application layer of the layer stack. A file includes only the layers below its own, and the asset layer lies below the :term[renderer]{id=renderer}, yet the asset manager must ask the device for an upload context and a memory budget. In the engine, a **service** is an interface that the whole process may use through `EngineServices::Get<T>`, provided by a module or by the running program. The asset layer defines `IAssetGraphics`, the renderer registers an implementation, and the asset manager calls `EngineServices::Get<IAssetGraphics>()`; together they form a minimal service locator.

```cpp src="Strata/src/Strata/Core/EngineServices.h#L21-L69"
namespace Strata::EngineServices
{

	namespace Detail
	{
		template<typename T>
		inline T* s_Provider = nullptr;
	}

	// Makes `provider` the process's provider of interface T (replacing an earlier one); it must live until the process ends.
	template<typename T>
	void Register(T& provider)
	{
		Detail::s_Provider<T> = &provider;
	}

	template<typename T>
	T* Get()
	{
		return Detail::s_Provider<T>;
	}

	// Provides interface T while it lives, then restores the provider it replaced (unless another one replaced it meanwhile,
	// which then stays). Scopes nest and must end in the reverse order of their start: an editor that runs an exported game in
	// its own process (tests) hands the game's services back to the editor when the game ends.
	template<typename T>
	class ScopedProvider
	{
	public:
		explicit ScopedProvider(T& provider)
			: m_Provider(&provider), m_Previous(Get<T>())
		{
			Register<T>(provider);
		}

		~ScopedProvider()
		{
			if (Detail::s_Provider<T> == m_Provider)
				Detail::s_Provider<T> = m_Previous;
		}

		ScopedProvider(const ScopedProvider&) = delete;
		ScopedProvider& operator=(const ScopedProvider&) = delete;
	private:
		T* m_Provider;
		T* m_Previous;
	};

}
```

1. **Lines 26–27:** a variable template gives each interface type its own pointer, null at the start: no map, no registry.
2. **Lines 31–35:** `Register` replaces the provider, which must live until the process ends.
3. **Lines 50–54:** a scope remembers the provider it replaces, then registers its own.
4. **Lines 56–60:** at its end the scope restores the old provider, only when the slot still holds its own.

Without a provider, `Get` returns null, and callers treat that as a missing feature: for assets it means that GPU assets keep their data in main memory. The six interfaces:

- `IAssetGraphics` gives the asset managers the renderer's upload context, the frames in flight and the memory budget. The renderer's registration provides it for the process.
- `IAudioOutput` gives the master volume, and the audio registration provides it for the process.
- `IProjectSettings` lets modules read a project's settings sections and notice a change by its version. The editor provides it while a project is open, and the game runtime from its manifest.
- `IGameWindow`, `IGameSaves` and `IGameGraphics` give a game the display options, the save folder and the players' graphics options. The editor provides them for its play mode, and the runtime for a shipped game.

:::example[A scope that hands the slot back]
The editor registers an `IGameSaves` provider named E for its play mode. A game then runs inside the editor's process, as in the engine's tests, and creates a `ScopedProvider` with its own provider G. The scope remembers E and stores G, so `Get<IGameSaves>()` returns G while the scope lives. When it ends, it finds G in the slot and writes E back. Had a third provider X replaced G meanwhile, the scope would leave X in place, which is why scopes end in the reverse order of their start.
:::

The costs of a locator apply here. A caller's need is invisible in its signature, and providers are global state, so a test must provide what the code under test asks for. Everything is for the main thread only. The gain is the layers: an interface placed low and provided from above inverts the dependency without a sideways include. Scene services are another thing, tied to a running scene, and [Systems](../world/systems.md) describes them.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Start and stop calls written in `main` | Small programs | Nothing hidden; the order is one list | Every program repeats two lists, and nothing checks them against each other |
| Global managers with `StartUp` and `ShutDown` | A common engine design, as the textbook describes | Direct calls and no registry | The order stays in `main`, and tests cannot replace a global |
| Modules loaded by name, with loading phases | Unreal Engine | Modules that other people add without a rebuild of the engine | A loader and phases for a program whose modules are known at build time |
| Kahn's algorithm with a queue | Textbooks | A cost in proportion to modules plus arrows | The listing no longer settles ties: the example gives A, D, C, B |
| Passing every interface to the code that needs it | Dependency injection in application frameworks | Needs visible in signatures; simple tests | Every layer between the program and the user passes the interface along |

## How it is tested

The suite `Core.EngineModules` in `StrataTests/src/Core/EngineModuleTests.cpp` runs without a GPU. It starts a headless application with small :term[thread pools]{id=thread-pool} and a `JournalModule`, which writes `<hook> <name>` into a list of text lines for every hook it gets. Its nine test cases check:

- the start order of the example above, and the reverse order of the stop, release and last hooks;
- the frame's hook order for two modules over two frames, and a module that skips or closes;
- a module that cannot start, and that only the started modules end;
- the project module's release after the layers while jobs run;
- the refusals: a missing required dependency, a cycle with a module that only waits for it, a self-dependency, a duplicate name beside a null factory, and the application refusing to start;
- events reaching the modules before the layers, and stopping when a module handles them;
- a 60 ms wait that the work time omits, beside 5 ms of layer work, and `Find<T>` by name, also after `Clear`.

Run them in the folder of your source build with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.EngineModules`, or run all tests with `ctest --preset windows-debug -j 8`. The suite `Core.Application` tests the frame around the modules. A new regression test must fail without its fix, so write it first and watch it fail.

## Changing it safely

To add a module, write a class in its own module's folder with a `c_Name`, a `Factory` and the hooks it needs, and list the factory in `ApplicationSpecification::Modules` of each program that runs it. Never call it from `Application`. If it must start after another module, name that one in `GetDependencies`, with `Required` false when the order matters only if the other module exists. A new hook needs an empty default, its moment in its comment and in the architecture document, and a line in the journal test.

These engine rules apply, each with its reason:

- Hooks run on the main thread, because the main thread owns the scene, the input and the rendering submission. Background work goes through the job system and returns with `SubmitToMainThread`.
- A service that lives as long as the program is a module in its own module's folder, and only the programs that run it list it. A sideways or upward include never fixes a layer problem: invert the dependency with an interface and a service.
- A provider registers on the main thread, before anything uses it; what depends on a running game goes through `ScopedProvider`.
- A failed `OnInit` cleans up and describes itself, because the application ends only the started modules.

Before a commit, run `Core.EngineModules`, `Core.Application` and the architecture suites, which check that layers include only what they may.

## Summary

- The hooks run forward in `OnBeginFrame`, `OnUpdate` and `OnRenderUI`, and backward in `OnEndFrame`, `OnStop`, `OnRelease` and `OnShutdown`; the layers go before `OnRelease`, and the job system stops before `OnShutdown`.
- Kahn's algorithm places the first ready module of the listing again and again, so the listing settles every tie; the test's list gives A, C, B, D.
- The registry refuses a null factory, a duplicate name, a missing required dependency and a cycle, and the cycle message names only modules that wait for each other.
- A module has a `c_Name`, a `Factory` and its hooks; a test lists it in a headless application, finds it with `Find<T>()` and reads a journal.
- Code that can include a module's header uses `Find<T>()`, which may return null; code that cannot uses `EngineServices::Get<T>()`.

## Check yourself

1. Modules X, Y, Z and W are listed in this order. X starts after Z, and W starts after Y. Y and Z start after nothing. What is the start order, and what would a queue version of Kahn's algorithm give?

   :::answer{tests="kahn-order"}
   The waiting counts are X 1, Y 0, Z 0, W 1. Step 1 takes Y, the first ready module, and W becomes ready. Step 2 scans from the top and takes Z, because X still waits and W stands later; then X becomes ready. Step 3 takes X, and step 4 takes W, so the order is Y, Z, X, W. A queue holds Y and Z at the start: it places Y and adds W behind Z, places Z and adds X, then places W before X, which gives Y, Z, W, X.
   :::

2. A program lists one module, `ImGui`, which requires `Graphics`, and no `Graphics`. What happens? (a) It starts, and `OnInit` fails. (b) The registry refuses the list before any module starts. (c) The registry ignores the need, as it does for an optional one.

   :::answer{tests="refusals"}
   The answer is (b). The need is required, so `Create` adds the problem `engine module 'ImGui' requires 'Graphics', which the program does not run` and keeps nothing. Answer (a) would need the list to pass first, and it does not. Answer (c) holds only for an optional entry, with `Required` false. The application reports `<name> cannot start: ...` and exits with code 1 before any `OnInit` runs.
   :::

3. A program has modules B and A, where B starts after A, and a layer that logs `L` in its update. Predict the order of the hooks in one frame.

   :::answer{tests="hook-order"}
   The sorted order is A, B. The frame reads: begin A, begin B, `L`, update A, update B, interface A, interface B, end B, end A. The begin, update and interface hooks run forward, the layers update between the begin and update hooks, and the end hooks run backward.
   :::

4. What does `registry.Find<Beta>()` do when the program runs no module named `Beta`? (a) It returns null. (b) It throws. (c) It asserts in Debug builds.

   :::answer{tests="write-module"}
   The answer is (a). `Find` loops over the sorted modules, compares names and returns null when none matches, and `Find<T>` casts null to a null `T*`. Engine code does not throw, so (b) is wrong. A missing module is a normal state, not a programmer's mistake, so (c) is wrong too. The caller must check the result.
   :::

5. The asset manager needs the memory budget of the graphics device. Should it call `Find<GraphicsModule>()` or `EngineServices::Get<IAssetGraphics>()`, and why?

   :::answer{tests="find-service"}
   The manager should ask the service. The asset layer lies below the renderer, so its code may not include `GraphicsModule` and cannot name the type. `IAssetGraphics` lives in the asset layer, and the renderer provides it, so the dependency points downward. The call may return null, and the manager then works without a device.
   :::

## Exercises

1. **Basic.** A program lists five modules in this order: `Menu` (requires `Graphics`), `Save` (after `Project`), `Project`, `Audio` (after `Graphics`, only as an ordering) and `Graphics`. (a) What is the start order? (b) What is the message if the list has no `Graphics`? (c) What is the message if `Graphics` also starts after `Menu`?

   :::answer[Worked solution]{tests="kahn-order refusals"}
   (a) The waiting counts are Menu 1, Save 1, Project 0, Audio 1 and Graphics 0. Project goes first, then Save. Graphics goes third and frees Menu and Audio. Menu, the earlier of the two, goes fourth, then Audio. The order is Project, Save, Graphics, Menu, Audio.

   (b) Audio's need is optional, so it only loses its arrow. Menu's need is required, so the registry refuses the list with `engine module 'Menu' requires 'Graphics', which the program does not run`.

   (c) Menu and Graphics wait for each other. Audio waits for Graphics, and nothing waits for Audio, so the report omits it. The message is `engine modules 'Menu' and 'Graphics' depend on each other in a cycle`, in listing order. The toy can check (a) and (c); it prints Audio too, because it does not remove modules that only wait.
   :::

2. **Medium.** Write a `FrameCounterModule` in `EngineModuleTests.cpp` with a `c_Name`, a `Factory`, an `OnUpdate` that counts frames and an `OnStop` that logs the total. Find it with `Find<T>()` and test it in the style of the journaling module: run a headless application for three frames and check the count before and after the run, and the log line.

   Hint: the test process logs only warnings and errors. `Tests::ScopedLogLevel` lowers the level for one test.

   :::answer[Worked solution]{tests="write-module find-service" solution="tutorials/core/engine-modules/exercise-1.patch"}
   The module needs `GetName` and `OnInit`, the only functions without a default. `OnUpdate` adds 1 to a member, and `OnStop` logs it with `ST_CORE_INFO`. The test makes the application with `MakeSpecification({ FrameCounterModule::Factory() }, 3)`, finds the module with `Find<FrameCounterModule>()`, and checks 0 frames before `Run` and 3 after it. The application ends with its scope, so the test counts the log line after that scope with `Tests::CountLogMessages`. The patch adds the class and one test case, which makes 10 in the suite.
   :::

3. **Medium.** Trace it yourself: find which modules the editor starts, and in which order. Build the editor in Debug, set breakpoints, and write down the order of the `OnInit` calls. Compare it with the dependencies in the headers.

   Hint: start with the function that fills `ApplicationSpecification::Modules`.

   :::answer[Worked solution]{tests="kahn-order hook-order"}
   `CreateApplication` in `StrataEditor/src/EditorApplication.cpp` pushes the factories: Graphics unless `--no-gpu`, Audio, ImGui when there is a window, and Project. `Application::StartModules` in `Strata/src/Strata/Core/Application.cpp` calls `EngineModuleRegistry::Create` in `Strata/src/Strata/Core/EngineModule.cpp`, which sorts them, and then calls `OnInit` in the sorted order. With a window the order is Graphics, Audio, ImGui, Project, the same as the listing, because the only dependency, ImGui's on Graphics, is met already. Breakpoints in `GraphicsModule::OnInit` and `ImGuiModule::OnInit` show Graphics first, and `ImGuiModule::OnInit` finds the started `GraphicsModule` through `context.Modules`.
   :::

4. **Hard.** Make the frame counter return `Skip` at every tenth call of `OnBeginFrame`. A test lets the application run until it counted 20 frames. How many begin calls does that need, how many updates does the counter see, and how much time do the skips add?

   :::answer[Worked solution]{tests="hook-order write-module"}
   The module counts its begin calls and returns `Skip` when the count is a multiple of 10. A skipped frame is not counted, so 20 counted frames need the begin calls 1 to 22: the calls 10 and 20 skip. The counter sees 20 updates, and `GetFrameCount` is 20. Each skip makes the loop wait 16 ms, so the two skips add 32 ms beside the normal waiting between frames.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/EngineModule.h` and `EngineModule.cpp`: the interface, the structs, `EngineModuleRegistry`, the sort and its cycle report.
- `Strata/src/Strata/Core/Application.cpp`: `StartModules`, `ShutDownModules`, and the calls of the hooks in `RunFrame`, `OnEvent` and `Run`.
- `Strata/src/Strata/Core/EngineServices.h`: the service slots, `ScopedProvider` and the interfaces `IGameWindow`, `IGameSaves` and `IGameGraphics`.
- `Strata/src/Strata/Renderer/GraphicsModule.cpp`, `Strata/src/Strata/Audio/AudioModule.cpp`, `Strata/src/Strata/ImGui/ImGuiModule.cpp` and `Strata/src/Strata/Project/ProjectModule.cpp`: the four built-in modules.
- `StrataEditor/src/EditorApplication.cpp` and `StrataRuntime/src/RuntimeApplication.cpp`: the programs' module lists.
- `StrataTests/src/Core/EngineModuleTests.cpp`: the suite `Core.EngineModules`.

## Further reading

- Jason Gregory, *Game Engine Architecture* (the chapter on starting up and shutting down engine subsystems): the manager design and its order problem, advanced.
- Robert Nystrom, [Service Locator in Game Programming Patterns](https://gameprogrammingpatterns.com/service-locator.html): the pattern and its costs, with short code, beginner.
- Epic Games, the Unreal Engine documentation on modules and the `IModuleInterface` class: a module system with loading phases, intermediate.
- Arthur B. Kahn, "Topological sorting of large networks", Communications of the ACM, 1962: the original algorithm, advanced.

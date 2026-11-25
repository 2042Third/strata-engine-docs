---
id: scripting/hot-reload
title: "Hot reload"
description: "How Strata replaces a script module while the game runs, which state survives the swap and what happens when a rebuild fails."
kind: internals
size: L
tracks: [E]
needs: [scripting/script-system, core/files]
time: 80
learn:
  - id: reload-steps
    text: trace the steps of a reload from a rebuilt file to the call of OnReload
  - id: keeps-loses
    text: name what a reload keeps and what it loses, and where a script finds its state again
  - id: failures
    text: explain what Strata does when a rebuilt module does not load or a class disappears
  - id: copies
    text: explain why a build never fights the running game for the module file
since: 0.3.0
status: final
---

You change a line of script code, build, and the game on your screen starts behaving differently, without closing, without loading the scene again and without losing the position of the player. That is **hot reload** of scripts: Strata replaces the script module while the game runs and keeps what the scripts can keep. It does not keep everything, and the page explains exactly which part survives and why. It also does not reload assets such as textures (that is another meaning of the words, in [the asset importing page](../assets/importing.md)), and it does not build the module (the editor does that, see [script builds](../editor/script-builds.md)).

You need three things from other pages: the instances, sync points and field values of [the script system](../scripting/script-system.md), the load modes and private copies of [loading](../scripting/loading.md), and the :term[file watcher]{id=file-watcher} of [files you can trust](../core/files.md). The page ends with a toy reload you can run, the real code in the order the data flows, and a list of what to check before you change it.

## The problem and how engines solve it

Game code changes constantly. You adjust a speed, rebuild, play, adjust again. If every rebuild means closing the game, starting it, loading the scene and walking the character back to the place that you want to test, a change that takes five seconds costs a minute. Over a day that adds up to hours, and worse, people stop trying small ideas.

The core difficulty is that a running program holds two things: **code** (the :term[machine instructions]{id=machine-instruction}) and **state** (the numbers in memory that the code reads and writes). A rebuild produces new code. The state belongs to the old code: its shape (which fields exist, in what order, how large) was fixed when the old code was compiled. New code may expect another shape. Every solution is a choice about what to do with that difference.

Take a small example. Version 1 of a script has the fields `Count` (4 :term[bytes]{id=byte} at offset 0) and `Speed` (4 bytes at offset 4). Version 2 adds a field `Boost` before `Speed`, so that `Speed` now sits at offset 8. If the new code reads the old memory as it is, it takes the old `Speed` for `Boost` and reads garbage as `Speed`. Nothing crashes at once, and the game acts wrongly in a way no person can explain; every approach below avoids this or accepts a limit on what you may change.

| Approach | What it keeps | What it costs | Who uses it |
| --- | --- | --- | --- |
| Restart with saved state | Whatever you saved before closing (a save game, the open scene) | A full start each time, and you must write the saving and loading | Most small projects; engines whose editor reloads the scene |
| Swap the library, save and restore the state around it | Every value that is declared as saved state; the rest starts over | The author must declare what is state; pointers and caches are lost | Strata and many in-house engines |
| Binary patching | Everything in memory, including plain members and the stack | Fragile: layout changes are limited, and a tool outside the engine does the patching | Live++, Unreal's Live Coding |
| An interpreter that reloads functions | Data of the running program, because functions are found by name at each call | Slower code, and a language with a :term[runtime]{id=runtime} | Scripting languages embedded in engines |

Strata chooses the second row, so look at it closely. Before the swap, it reads each instance's declared values into a list of name, type and value. Then it replaces the code and builds fresh instances. At last it writes the saved values into them, matching by name and type. The trouble from the example disappears: the list says "Speed, float, 8.0", and the new code puts 8.0 into wherever its own `Speed` lives.

The price is in the words "declared as state". The engine cannot read the variables that you did not declare, because after a rebuild their names and positions have no meaning. A cached pointer to another entity, a running timer kept in a plain member, a counter used only inside the class: all of them start over. The rest of the page is about that choice, and about the care that makes it safe.

:::why
Binary patching keeps more, but it ties the engine to one :term[compiler]{id=compiler} and one platform tool, and it limits which edits are allowed. Strata runs on Windows, Linux and macOS, with script modules that are plain libraries behind a C :term[ABI]{id=abi} (a fixed binary interface of plain data, described in [the page on the ABI](../scripting/abi-sdk.md)). A swap of the library works on all three with the same code, and the rule "fields survive, everything else starts over" is short to state and cheap to test.
:::

## The map: who does what

Four parts take part in a reload, and each has one job. The **file watcher** (`FileWatcher`, from [files you can trust](../core/files.md)) runs on its own thread and reports changes of files. `ScriptEngine` owns the loaded module and decides when to reload. `ScriptModule` loads one library and keeps it alive. `ScriptSystem` is the :term[scene system]{id=scene-system} of one scene: it owns that scene's script instances and moves them over.

```mermaid caption="The watcher reports a rebuilt file, the engine loads the new module beside the old one, each scene saves its instances, the old library unloads and the scenes rebuild them." alt="A flow from a rebuilt file through the watcher and the engine to a new module, then saving of instances, unloading of the old module, restoring of instances and the reload callback."
flowchart LR
  B[Build writes the module file] --> W[FileWatcher: 300 ms of quiet]
  W --> U[ScriptEngine::Update]
  U --> L[ScriptModule::Load: new module beside the old]
  L -->|fails| K[Old module keeps running]
  L -->|loads| S[ScriptSystem::BeginModuleReload per scene]
  S --> X[Old library unloads]
  X --> E[ScriptSystem::EndModuleReload per scene]
  E --> R[OnReload at the next sync point]
```

The diagram shows the order, and the next diagram adds the clock. Time runs down the page. The build writes in several steps, so the watcher waits until the file has been quiet for 300 ms. The reload then runs at the start of a frame, between two frames of the game, never in the middle of one.

The first attempt is due at the moment of the report, so it runs in the same `ScriptEngine::Update` that collects the report. If the file is busy, the engine tries again every 250 ms, up to 20 attempts in all.

```mermaid caption="Time runs down: the linker writes in steps, the watcher reports after 300 milliseconds of quiet, a busy file delays the load by 250 milliseconds, and the callback follows at the next sync point." alt="Steps down the page: the linker writes, the watcher reports, the engine fails once and then loads, the scene saves and restores fields, and the callback runs."
sequenceDiagram
  participant Linker
  participant Watcher
  participant Engine
  participant Scene
  Linker->>Linker: writes the file in steps
  Watcher->>Engine: reports once, after 300 ms unchanged
  Engine->>Engine: first attempt: file busy, retry in 250 ms
  Engine->>Engine: second attempt: new module loads
  Engine->>Scene: save fields, drop instances
  Engine->>Scene: restore fields into new instances
  Scene->>Scene: next sync point: OnReload
```

All of it happens on the :term[main thread]{id=main-thread}, except the watcher's own scan. This follows the engine's threading rule: the main thread owns the scene, input and scripts, so the watcher only queues a report, and `ScriptEngine::Update` collects it on the main thread.

## The contract

What may a script author count on, and what must the author do? The rules are short.

1. **Fields survive.** A field that you declare with `ST_SCRIPT_FIELD` keeps its running value when the new class still has a field with the same name and the same type. A field that was removed, or whose type changed, takes the default of the new class.
2. **Nothing else survives.** Plain members, cached entities, pointers to other scripts, local timers: all start over. The module's global and static variables start over too, because the new module is another library, loaded beside the old one, which then unloads. Every plain member of the new instance has the value its :term[constructor]{id=constructor} gives.
3. **`OnReload` replaces `OnCreate`.** After a reload, `OnCreate` does not run again for an instance that had already started; `OnReload` runs instead. A script that caches things in `OnCreate` must repeat that work in `OnReload`.
4. **`OnDestroy` does not run** for the instances that the reload drops. Their :term[destructors]{id=destructor} run, because the instance is deleted, but the :term[callback]{id=callback} that tells a script "you are leaving the game" does not, because the script is not leaving. It continues in the new module.
5. **A bad build changes nothing.** A module that does not load leaves the old one running, with all its state.

:::note
Only fields survive hot reload; everything else is found again in `OnReload`. The reason is physical: the old instance's memory belongs to a library that unloads, so nothing inside it can be trusted after the swap. The `Coin` of [the script system](../scripting/script-system.md) follows it: its `OnReload` calls `OnCreate`.
:::

The first mistake that people make is to keep state in a plain member and to be surprised when it is zero after a rebuild. The second is a pointer into the old module: a pointer to another script, a :term[function pointer]{id=function-pointer}, a pointer to a string literal. After the swap the old library is unloaded, and the address points to memory that no longer holds that code or data. Scripts avoid this by holding entities and handles, which the engine resolves again, and by finding them in `OnReload`.

## A toy version

The toy below is a reload of a one-class module, with fields, in under a hundred lines. A "module" here is a table of default field values and a step size that stands for the code. An instance holds its fields and one plain member, `Time`. Loading a module can fail, which returns nothing. The toy takes the three actions of the real reload in order: snapshot, replace, restore by name.

Search for three things. The broken load leaves the old module in place. The restored `Speed` is 8, the value the person set, and not the default of the new module. `Time` returns to zero, because it is not a field.

```cpp sketch="scripting-hot-reload-toy.cpp"
// A toy hot reload: a "module" is a table of fields and a step size; an instance keeps its values in fields.
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

struct Field
{
	std::string Name;
	float Value = 0.0f;
};

struct Module
{
	int Version = 0;
	std::vector<Field> Defaults;
	float Step = 1.0f; // Stands for the code of OnUpdate
};

struct Instance
{
	std::vector<Field> Fields;
	float Time = 0.0f; // A plain member: not a field, so a reload loses it
};

// Stands for loading a library: a broken build returns nothing and the old module keeps running.
std::optional<Module> LoadModule(int version, bool broken)
{
	if (broken)
		return std::nullopt;
	if (version == 1)
		return Module { 1, { { "Count", 0.0f }, { "Speed", 5.0f } }, 1.0f };
	return Module { version, { { "Count", 0.0f }, { "Speed", 1.0f }, { "Boost", 2.0f } }, 10.0f };
}

Instance Create(const Module& module)
{
	return Instance { module.Defaults, 0.0f };
}

void Update(Instance& instance, const Module& module)
{
	instance.Fields[0].Value += module.Step;
	instance.Time += 1.0f;
}

void Print(const char* label, const Instance& instance)
{
	std::printf("%s:", label);
	for (const Field& field : instance.Fields)
		std::printf(" %s=%g", field.Name.c_str(), field.Value);
	std::printf(" Time=%g\n", instance.Time);
}

// The reload: snapshot the fields, drop the instance, load the new module, restore by name.
bool Reload(Module& module, Instance& instance, int version, bool broken)
{
	std::optional<Module> next = LoadModule(version, broken);
	if (!next)
	{
		std::printf("load failed, module %d keeps running\n", module.Version);
		return false;
	}
	const std::vector<Field> snapshot = instance.Fields;
	module = *next;
	instance = Create(module); // No OnDestroy for the old instance, no OnCreate for the new one
	for (const Field& saved : snapshot)
		for (Field& field : instance.Fields)
			if (field.Name == saved.Name)
				field.Value = saved.Value;
	std::printf("OnReload runs\n");
	return true;
}

int main()
{
	Module module = *LoadModule(1, false);
	Instance instance = Create(module);
	for (int frame = 0; frame < 3; frame++)
		Update(instance, module);
	instance.Fields[1].Value = 8.0f; // The person edits Speed in the Inspector
	Print("before", instance);

	Reload(module, instance, 2, true);
	Reload(module, instance, 2, false);
	Print("after", instance);
	Update(instance, module);
	Print("next frame", instance);
	return 0;
}
```

```text output-of="scripting-hot-reload-toy.cpp"
before: Count=3 Speed=8 Time=3
load failed, module 1 keeps running
OnReload runs
after: Count=3 Speed=8 Boost=2 Time=0
next frame: Count=13 Speed=8 Boost=2 Time=1
```

1. **Lines 13–18:** a module holds default field values and a step that stands for the code
2. **Line 23:** the plain member `Time` is not a field
3. **Lines 58–62:** the new module loads first, and a failure leaves everything as it was
4. **Lines 64–70:** snapshot, replace, create a fresh instance and restore by name
5. **Lines 84–85:** the broken build comes first, then the good one

The output shows that `Count` and `Speed` crossed the reload, that the new field `Boost` has its default, and that `Time` started over. The next frame runs the new code (the step is 10, so `Count` goes from 3 to 13). The toy matches by name only. The real engine also compares the type, which the toy omits because every field is a float.

## The real code

The real reload has more steps than the toy, because it has to stay correct when something goes wrong in the middle. Follow it in the order of the data.

### Enabling it: a private copy and a watcher

Windows locks a library file while it is loaded, so a build cannot replace it. A module that runs from its own file would block the build, and the build would fail with an error about a locked file. Strata avoids the fight. With hot reload enabled, the module runs from a private copy in a folder made for the session ([loading](../scripting/loading.md) explains the load modes), and the original file is free for the :term[linker]{id=linker}.

The editor turns hot reload on before a project's module loads (the setting `HotReloadScripts` is true by default); shipped games never do, so they load their module in place. The next quote is the whole switch. Look at what happens to a module that already runs from its file.

```cpp src="Strata/src/Strata/Scripting/ScriptEngine.cpp#L154-L170" symbol="ScriptEngine::SetHotReloadEnabled"
void ScriptEngine::SetHotReloadEnabled(bool enabled)
{
	m_HotReloadEnabled = enabled;
	if (enabled)
		StartWatching();
	else
		StopWatching();

	// A module running from its file keeps the build from replacing it (on Windows the file is locked): move it to a
	// private copy at the next Update().
	if (enabled && m_Module && !m_Module->IsLoadedFromCopy())
	{
		m_ReloadPending = true;
		m_ReloadAttempts = 0;
		m_NextReloadAttempt = std::chrono::steady_clock::now();
	}
}
```

1. **Lines 157–160:** enabling starts the watcher and disabling stops it
2. **Lines 162–164:** only a module that does not yet run from a copy needs the move
3. **Lines 166–168:** the reload is marked pending, with no attempts used and the next attempt due now

The module is not moved at once. The engine marks a reload as pending, with the attempt counter at zero and the next attempt at "now", and `Update` does the move at its next call, between frames. The same reload path serves a file change and the switch, so there is one way to swap a module, not two.

The watcher starts in `StartWatching`. The next quote shows its settings: it watches only the folder of the module, not the folders inside it, and it uses a debounce.

```cpp src="Strata/src/Strata/Scripting/ScriptEngine.cpp#L178-L183" from="FileWatcherSettings settings;" to="m_Watcher = CreateScope<FileWatcher>();" symbol="ScriptEngine::StartWatching"
FileWatcherSettings settings;
settings.Recursive = false;
settings.IgnoredDirectories.clear();
// Linkers write the module in several steps; only a file that stayed unchanged for a while is complete.
settings.Debounce = std::chrono::milliseconds(300);
m_Watcher = CreateScope<FileWatcher>();
```

To **debounce** is to report a burst of changes once, after the changes have stopped for a set quiet time. A linker does not write a module in one step: it writes, patches and writes again, and a copy made in the middle would be a broken file. With a quiet time of 300 ms, the watcher reports a file only once its size and write time have stayed the same for that long. The default of the watcher is 150 ms; the script engine asks for twice that because a linker pauses between its steps.

A worked example with real numbers: the linker writes the module at 0 ms, 120 ms and 260 ms, and then nothing until the next build. The gaps are 120 ms and 140 ms, both under 300 ms, so each write restarts the wait. The last write is at 260 ms and the report comes at 560 ms. The sketch below runs exactly this rule, with a fourth write at 900 ms that starts a second report.

```cpp sketch="scripting-hot-reload-debounce.cpp"
// A debounce: a change is reported only after the file stayed unchanged for a quiet time.
#include <cstdio>
#include <vector>

int main()
{
	const int quietMs = 300;
	const std::vector<int> writes = { 0, 120, 260, 900 }; // Times of linker writes, in milliseconds
	int lastWrite = writes.front();
	for (size_t index = 1; index <= writes.size(); index++)
	{
		const int nextWrite = index < writes.size() ? writes[index] : 1000000;
		if (nextWrite - lastWrite >= quietMs)
			std::printf("reported at %d ms\n", lastWrite + quietMs);
		if (index < writes.size())
			lastWrite = nextWrite;
	}
	return 0;
}
```

```text output-of="scripting-hot-reload-debounce.cpp"
reported at 560 ms
reported at 1200 ms
```

1. **Lines 7–8:** the quiet time and the times of the writes
2. **Lines 12–14:** a gap of at least the quiet time after a write ends the burst, and the report comes that long after the last write
3. **Line 16:** a later write moves the last write forward

The output has two lines, one for each burst: the first at 560 ms (260 ms plus 300 ms) and the second at 1,200 ms (900 ms plus 300 ms). The real watcher compares size and write time instead of listening to every write, and it also polls at a safe interval, but the rule it applies is the same.

### The update: wait for the right moment

`ScriptEngine::Update` runs once per frame, on the main thread. It does two jobs: it turns the watcher's reports into a pending reload, and it runs the pending reload when its time has come.

```cpp src="Strata/src/Strata/Scripting/ScriptEngine.cpp#L196-L229" symbol="ScriptEngine::Update"
void ScriptEngine::Update()
{
	ST_PROFILE_FUNCTION();

	if (m_Watcher && !m_ModulePath.empty())
	{
		for (const FileChange& change : m_Watcher->PollChanges())
		{
			if (change.Type == FileChangeType::Removed || !IsSameFileName(change.Path, m_ModulePath))
				continue;
			m_ReloadPending = true;
			m_ReloadAttempts = 0;
			m_NextReloadAttempt = std::chrono::steady_clock::now();
		}
	}

	if (!m_ReloadPending || std::chrono::steady_clock::now() < m_NextReloadAttempt || ScriptModule::GetCurrentCall())
		return;

	std::string error;
	bool retryable = false;
	if (LoadInternal(m_ModulePath, &error, &retryable))
	{
		m_ReloadPending = false;
		return;
	}

	if (retryable && ++m_ReloadAttempts < c_MaxReloadAttempts)
	{
		m_NextReloadAttempt = std::chrono::steady_clock::now() + c_ReloadRetryInterval;
		return;
	}
	m_ReloadPending = false;
}
```

1. **Lines 200–210:** a change of the module file, and no other, makes a reload pending
2. **Line 212:** the function returns when nothing is pending, the attempt is not due, or script code is running
3. **Lines 215–221:** one attempt; a success ends the pending reload
4. **Lines 223–227:** a failure worth trying again schedules the next attempt 250 ms later, until 20 attempts are used
5. **Line 228:** every other failure drops the pending reload

The loop at the top ignores removals and files with another name; only a change to the module file starts a reload. The condition after the loop returns early in three cases: nothing is pending, the next attempt is not due, or script code is running (a script called into the engine, which called `Update`). In the last case the module cannot be replaced, because its code is on the stack. The reload stays pending and the next frame tries again.

Then the engine loads. A failure may be worth trying again: the file is missing, or the copy could not be made, perhaps because the linker still holds the file. The engine tries again in 250 ms, up to 20 attempts, which is about five seconds. Any other failure ends the attempt: a file that is not a Strata module, a module built against another script :term[ABI version]{id=abi-version}, or one that crashes while it loads will not get better by waiting.

### The swap: the new module comes first

The new module loads before anything of the old one is touched. This is the center of the design. A broken build stops here, with the game untouched.

```cpp src="Strata/src/Strata/Scripting/ScriptEngine.cpp#L81-L109" from="ScriptModuleLoadError loadError;" to="m_LoadCount++;" symbol="ScriptEngine::LoadInternal"
ScriptModuleLoadError loadError;
const ScriptModuleLoadMode mode = m_HotReloadEnabled ? ScriptModuleLoadMode::Copy : ScriptModuleLoadMode::InPlace;
Scope<ScriptModule> module = ScriptModule::Load(path, mode, m_Watchdog.get(), &loadError);
if (!module)
{
	ST_CORE_ERROR("{}{}", loadError.Message, m_Module ? "; the previously loaded module keeps running" : "");
	if (outError)
		*outError = loadError.Message;
	if (outRetryable)
		*outRetryable = loadError.Retryable;
	return false;
}

// Running scenes move their script state over to the new module. Iterate over a copy: systems never attach or
// detach from these callbacks, but the list must not be observed while it could change.
const std::vector<ScriptSystem*> systems = m_Systems;
const bool replacing = m_Module != nullptr;
if (replacing)
{
	for (ScriptSystem* system : systems)
		system->BeginModuleReload();
	if (m_Module->IsFaulted())
		m_ReplacedFaultCount++;
}

const std::filesystem::path previousDirectory = m_ModulePath.parent_path();
m_Module = std::move(module); // Unloads the previous module
m_ModulePath = path;
m_LoadCount++;
```

1. **Lines 81–83:** the new module loads first, from a copy when hot reload is enabled
2. **Lines 84–92:** a failure logs and returns before anything of the old module is touched
3. **Lines 94–96:** the list of scenes is copied before the callbacks run
4. **Lines 98–104:** each scene saves its instances while the old module is still alive
5. **Line 107:** the assignment unloads the old module

Read the order. First `ScriptModule::Load` makes the new module from a copy, with the old one still in `m_Module`. If it fails, the error is logged with the text that the previous module keeps running, and the function returns. If it succeeds, every scene's `BeginModuleReload` runs while the old module is still alive: the scenes need it to read the fields. Then the assignment of `m_Module` unloads the old module (the old pointer's destructor runs), and `EndModuleReload` follows for every scene.

The list of scenes is copied first, with a comment that explains why: a system never attaches or detaches while these callbacks run, but the code does not rely on that. Several scenes can run scripts at once, and the `ScriptSystem` of each one takes part.

### Saving: the snapshot

`BeginModuleReload` is the first half of the move in one scene. The next quote is its core: for each instance, it reads every field through the module, and then deletes the instance.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L1248-L1271" from="ScriptModule* module = GetUsableModule();" to="UpdateContactWatch(*instance);" symbol="ScriptSystem::BeginModuleReload"
ScriptModule* module = GetUsableModule();
if (module && instance->Handle)
{
	std::vector<ScriptFieldValue> snapshot;
	for (uint32_t index = 0; index < instance->Class->Fields.size(); index++)
	{
		const ScriptFieldInfo& field = instance->Class->Fields[index];
		PropertyValue value;
		if (module->GetField(MakeCallSite(*instance, "GetField"), instance->Handle, index, value) == ScriptCallResult::Ok)
			snapshot.push_back(ScriptFieldValue { field.Name, field.Type, std::move(value) });
		if (module->IsFaulted())
			break;
	}

	// Deleted without OnDestroy: the script continues in the new module.
	if (!module->IsFaulted() && module->DestroyInstance(MakeCallSite(*instance, "Destroy"), instance->Handle) != ScriptCallResult::Faulted)
	{
		instance->ReloadFields = std::move(snapshot);
		instance->Restore = true;
	}
}
instance->Handle = nullptr;
instance->Class = nullptr;
UpdateContactWatch(*instance);
```

1. **Line 1248:** the usable module, which is none after a crash
2. **Lines 1251–1259:** every field of the instance is read through the module into the snapshot
3. **Lines 1262–1267:** the instance is deleted without `OnDestroy`, and only then is the snapshot kept
4. **Lines 1269–1270:** the old instance forgets its handle and class

Before this loop, the function blocks the creation of new instances, because a script destructor must not create instances in the module that is going away. It also finishes the scripts that were removed but not yet destroyed, with `OnDestroy`, in the old module. What remains is the list of live instances.

The snapshot is a list of name, type and value. The call that deletes the instance is `DestroyInstance` of the module, and it runs the destructor of the script class but not `OnDestroy`. Only when both steps work does the instance keep its snapshot and the flag `Restore`. If the module has crashed before (it is *faulted*, see [crash containment](../scripting/crash-containment.md)), nothing can be read, and the instance is abandoned: its state starts over in the new module.

### Restoring: fields back, then the callback

`EndModuleReload` is the second half. For each instance it finds the class by name in the new module, constructs a new instance, and writes the saved values back.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L1320-L1334" from="// The running values win" to="instance->Restore = false;" symbol="ScriptSystem::EndModuleReload"
// The running values win over the stored overrides; fields that were removed or changed type keep their defaults.
if (instance->Restore)
	ApplyFieldOverrides(*instance, instance->ReloadFields, false);
instance->ReloadFields.clear();

if (instance->Restore && instance->Created)
	m_PendingReloads.push_back(instance);
else
{
	// Never started, or its state was lost with a crashed module: it starts over (and knows of no contacts).
	instance->Created = false;
	instance->Contacts.clear();
	m_PendingStart.push_back(instance);
}
instance->Restore = false;
```

1. **Lines 1320–1322:** the running values are written over the values stored in the scene
2. **Lines 1325–1326:** an instance that had started waits for `OnReload`
3. **Lines 1327–1333:** any other instance starts over and gets `OnCreate`
4. **Line 1334:** the flag is cleared once the instance is handled

Construction applies the values stored in the scene first (the values the person set in the Inspector); the saved running values come after them, so the running values win. `ApplyFieldOverrides` takes a field only when the new class has a field with that name and the same type. A removed field is dropped, and a field with a new type keeps the default of the new class. An instance that had started joins the list of pending reloads. One that never started, or whose state was lost with a crashed module, joins the list of pending starts and gets `OnCreate` as if it were new.

The callback runs later, at the next sync point of the scene (the moment at which the system creates and starts scripts). The sync point runs its steps in a fixed order: flush deferred destroys, reconcile changed entities, `RunPendingReloads`, `RunPendingStarts`. The reloads come first, so a restored script is ready before a new script starts.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L651-L662" symbol="ScriptSystem::RunPendingReloads"
void ScriptSystem::RunPendingReloads()
{
	const std::vector<Ref<Instance>> reloads = std::move(m_PendingReloads);
	m_PendingReloads.clear();
	for (const Ref<Instance>& instance : reloads)
	{
		if (!GetUsableModule())
			return;
		if (!instance->Removed && instance->Handle && !instance->Disabled && instance->Class->Implements(ScriptCallback::OnReload))
			Invoke(*instance, ScriptCallback::OnReload, 0.0f);
	}
}
```

1. **Line 653:** the list is taken at once, so a reload during a callback does not change it
2. **Lines 657–658:** a crashed module stops the loop
3. **Lines 659–660:** `OnReload` runs only for a live, enabled instance whose class implements it

The loop calls `OnReload` only for an instance that is still alive, not disabled and whose class implements the callback. A class without `OnReload` gets neither `OnCreate` nor `OnReload`: it continues with the restored fields and a fresh object, which is right for a script that keeps all state in fields. The call goes through `Invoke`, the same guarded path as any other callback, so a crash in `OnReload` is contained like any other.

## What survives: the `Coin` example

The `ThirdPerson` sample has a script called `Coin`. It spins and bobs the model of a coin and counts it once the player touches it. Its fields are `SpinSpeed`, `BobHeight` and `Collected`; its plain members are `m_Visual` (the entity of the model), `m_VisualTranslation`, `m_Time` and `m_Phase`. Its `OnReload` calls `OnCreate`, which finds the model again among the entity's children.

:::example
You play a `ThirdPerson` copy and set `SpinSpeed` to 90 in the Inspector (the default is 180). After 10 seconds, `m_Time` is 10, and the model's angle is `m_Time * SpinSpeed` = 900 degrees, which is a half turn (900 − 720 = 180). Now you change the bob height in the code and rebuild.

The reload reads `SpinSpeed` = 90, `BobHeight` = 0.12 and `Collected` = false into the snapshot. The new instance is made with the defaults (`SpinSpeed` 180) and then the snapshot is written: `SpinSpeed` is 90 again. The plain members start over: `m_Time` is 0, and `m_Visual` is an empty entity.

Without `OnReload`, `OnUpdate` would return at once, because `m_Visual` is not valid, and the coin would stop moving. With `OnReload`, which calls `OnCreate`, the model is found again and `m_Phase` is computed again from the entity's identifier, so the coins still bob out of step with each other. The visible effect: the model jumps back to an angle of 0 degrees, because `m_Time` restarted, and then spins at 90 degrees per second, the value you set. Both the loss (`m_Time`) and the survival (`SpinSpeed`) follow from one rule: fields survive.
:::

On screen, a person sees this: while the `ThirdPerson` copy plays, the coins turn and bob. After the build finishes, the coins keep moving with the new bob height, and the log shows the line `Reloaded script module 'ThirdPersonScripts' (13 classes)`, with the module's name and class count. The first load of a module logs `Loaded script module` in the same format. Nothing flickers, because the swap happens between two frames.

The worked example also shows the habit that makes scripts reload-safe. Put everything that a script finds in the scene (entities, handles, positions) into one function. `OnCreate` calls it at the start; `OnReload` calls it after a swap. A new plain member that you add later works at once, because it is set in that function. A value that must survive goes into a field.

## Copies and dependencies

A module that uses a :term[shared library]{id=shared-library} finds it through a path stored in the module. On Windows, the libraries sit beside the module file, and Strata finds them there even when the module runs from a copy. It searches the folder of the original, never the :term[current folder]{id=current-folder} or the `PATH` variable. On Linux and macOS, the :term[loader]{id=loader} (the part of the system that opens libraries) reads the run-time search path (:term[RUNPATH]{id=runpath}) stored in the module. The default of :term[CMake]{id=cmake} puts an :term[absolute path]{id=absolute-path} in that list, and an absolute path works from a copy.

The trap is `$ORIGIN` on Linux and `@loader_path` on macOS. Both name the folder of the file the loader actually opened. Under hot reload that file is the private copy, so the folder is the copy's folder, which holds only the copy. A module whose RUNPATH says `$ORIGIN/../lib` finds its libraries when it runs in place and fails to find them when it runs from a copy. The shared libraries page ([shared libraries](../scripting/shared-libraries.md)) teaches the mechanism; here the lesson is that a development session and a shipped game load differently.

Two more facts matter. A file that is already loaded is always loaded from a copy, even when hot reload is off, because loading the same file twice shares the running module's state. Each copy lives in a folder that the engine removes when the session ends. A lock file in it marks it as in use, so other sessions remove only the folders of owners that are gone.

## Failures

A reload can fail at four places, and the design handles each one.

1. **The module does not load.** The file is garbage, half written, built against another ABI version, or crashes while it starts. The engine logs the reason followed by the text that the previous module keeps running, and the game continues. Only a missing file or a failed copy is tried again. The test `A broken build keeps the running module` writes a garbage file, then a module with the wrong ABI version, then one that crashes while loading, and checks that the old module's `Count` is still 3.
2. **Script code is on the stack.** The engine refuses to swap: "Script modules cannot be loaded while script code is running". When the watcher started the reload, `Update` waits for a frame without a running call. A direct request returns failure.
3. **The old module is faulted.** A module that crashed cannot be asked for its fields. The reload still goes ahead, because a good new build is the way out of a crash: the instances start over in the new module, with `OnCreate`, and reloading clears the fault.
4. **A class no longer exists.** If you delete or rename a script class, its instances cannot be recreated. `EndModuleReload` reports a problem with the text that the script no longer exists, and drops the instance. The script entry stays on the entity in the scene, so a later build that has the class again creates it as a new script.

What this adds up to: a reload that cannot finish leaves the player with a running game, and a log that says why.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Binary patching of the running program | Live++, Unreal's Live Coding | Plain members and the stack survive; no `OnReload` is needed | One tool and one compiler per platform; edits of a type's layout are limited; a crash in the patcher is not contained |
| Reload the scene and the whole game state | Many small engines | No lost state: everything is loaded as the file says | The play position is lost; a reload takes seconds to minutes |
| An interpreter or a virtual machine | Engines with an embedded language | State lives in the interpreter and survives by nature | Slower script code, and no C++ games |
| Copy the whole memory of the module | Rare; mostly a thought experiment | Plain members survive | The layout of the old memory must match the new, so changes of any field break it |

## How it is tested

The suite `Scripting.Reload` (file `StrataTests/src/Scripting/ScriptReloadTests.cpp`) uses two modules that the tests build from one source, `StrataTests/Scripts/Reload/ReloadScripts.cpp`, as `ReloadV1` and `ReloadV2`. Version 2 adds a field, removes one, changes the type of one, drops one class and adds another, and its code counts in tens. A helper `RebuildableModule` writes a version over the file as a build does, with a write time moved two seconds ahead, so the watcher sees a change.

The four test cases check four things. A reload in play keeps fields with the same name and type (`Count` 3 and `Speed` 3.0). It gives a field whose type changed the new default, runs `OnCreate` once and `OnReload` once, and returns the removed class when you go to version 1 again. A reload in edit mode only refreshes the class information, and a changed file is reloaded by the watcher alone within 15 seconds. In the suite `Scripting.LoaderFaults`, a broken build keeps the running module; that suite runs in a CTest of its own, because a module that crashes in the loader can leave a lock held on Linux.

Run it directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Scripting.Reload`.

## Changing it safely

The extension points are few. A new kind of state that should survive is a new field type, which is a change of the script ABI and of the property types ([the script system](../scripting/script-system.md) lists them). A new step of the reload goes into `BeginModuleReload` and `EndModuleReload`, in pairs: whatever Begin takes apart, End must put back, on every path, including the path of a faulted module.

:::rule
Every call into module code goes through `ScriptModule`, which guards it against crashes, and module memory is read only inside guarded calls. The reload reads the fields of an instance with the guarded `GetField`, never directly, so a script that crashes while the snapshot is taken is a fault and not a crash of the editor. The rule is in `AGENTS.md`, and [crash containment](../scripting/crash-containment.md) explains the guard.
:::

Keep these checks in mind before a change. Load the new module before you touch the old one. Never run script code while the engine state it could break is in use: the list of instances is copied before a loop, and creation is blocked while the module is replaced. Test the failure paths as well as the good path: a changed reload needs a case in `Scripting.Reload`, and one in `Scripting.LoaderFaults` when it concerns a module that cannot load.

## Summary

- Trace a reload: the watcher reports after 300 ms of quiet, the engine loads the new module, each scene saves its fields, the old library unloads, the instances return and `OnReload` runs.
- Only fields survive, matched by name and type, with the running value winning over the stored one; plain members, pointers, globals and statics start over, and `OnReload` finds them again.
- A module that does not load leaves the old one running. A busy file is tried again every 250 ms up to 20 times, and a class that is gone loses its instances with a reported problem.
- A private copy of the module runs under hot reload, so the linker can replace the original, and `$ORIGIN` and `@loader_path` then point at the copy's folder.

## Check yourself

1. A script keeps `float m_Elapsed` as a plain member and `float Speed` as a field. You rebuild while the game runs. What are the two values after the reload, if they were 12.5 and 4.0 before? Choose: (a) 12.5 and 4.0; (b) 0 and 4.0; (c) 0 and the default of `Speed`; (d) 12.5 and the default of `Speed`.

   :::answer{tests="keeps-loses"}
   Answer (b). The field `Speed` is saved and restored by name and type, so it stays 4.0. The plain member is not a field, so the new instance has the value its constructor gives, 0. Option (a) would need the memory of the old instance, which unloads. Options (c) and (d) are wrong because the running value of a field wins over the default, and the plain member cannot keep 12.5.
   :::

2. The linker writes the module at 0 ms, 200 ms and 450 ms. At what time does the watcher report the file, with a debounce of 300 ms?

   :::answer{tests="reload-steps"}
   At 750 ms. The gaps are 200 ms and 250 ms, both under 300 ms, so each write restarts the wait; the last write is at 450 ms, and 450 + 300 = 750.
   :::

3. A rebuilt module has a bug in the code that runs when its library loads, and the code crashes. What happens to the running game, and does the engine try again?

   :::answer{tests="failures"}
   The old module keeps running with all its state, and the log says that the previous module keeps running. The engine does not try again: a crash while loading is not worth another attempt, because waiting does not fix it. Only a missing file or a failed copy is tried again, every 250 ms up to 20 attempts. Fix the code and build again.
   :::

4. Why does the build not fight the running game for the module file?

   :::answer{tests="copies"}
   With hot reload the engine runs the module from a private copy in its own folder. Windows locks a loaded library file, but the lock is on the copy, so the linker can replace the original at any time. A shipped game loads its module in place because nothing rebuilds it.
   :::

5. A script class `Spinner` is deleted from the code and the module is rebuilt while a scene holds two entities with that script. What does the log show and what is left?

   :::answer{tests="failures"}
   Each of the two instances is dropped, with a problem reported that names the script and the entity. The script entries stay on the entities in the scene, so a later build that has `Spinner` again creates new instances, which start with `OnCreate`.
   :::

## Exercises

1. **Basic.** Open a `ThirdPerson` copy, play it, and change the `SpinSpeed` of one `Coin` in the Inspector to 360 while it runs. Rebuild after you add a plain member `float m_Counter = 0.0f;` that `OnUpdate` increases by 1 each frame and logs. What does the log show right after the reload, and why does `SpinSpeed` stay 360?

   :::answer{tests="keeps-loses"}
   Worked solution. The editor reloads at the end of the build. `SpinSpeed` is a field, so the snapshot holds 360 and the new instance gets it back. The counter is new and plain, so it starts at 0, and the log shows 1, 2, 3 from the next frames. Rebuild again and the counter restarts at 0, which shows that a plain member never survives; declare it with `ST_SCRIPT_FIELD` instead and it keeps its value.
   :::

2. **Medium.** Trace it yourself: find where a reload starts and where `OnReload` is called. Set a breakpoint in `ScriptSystem::BeginModuleReload` while a `ThirdPerson` copy plays, then rebuild `Coin` and walk up the stack.

   :::answer{tests="reload-steps"}
   Worked solution: run the editor under a debugger, play the sample and rebuild the module. The stop in `ScriptSystem::BeginModuleReload` (`Strata/src/Strata/Scripting/ScriptSystem.cpp`) has `ScriptEngine::LoadInternal` above it, which loops over the scenes. Above that is `ScriptEngine::Update`, which the watcher's report started by setting `m_ReloadPending`; both are in `Strata/src/Strata/Scripting/ScriptEngine.cpp`. Continue past the swap, where the assignment of `m_Module` unloads the old module, and `EndModuleReload` runs. A second breakpoint in `ScriptSystem::RunPendingReloads` stops at the next sync point, and `Invoke` calls `OnReload` from there.
   :::

3. **Hard.** Extend the toy: make `Reload` try again. A load that fails with a "busy" result is tried again 250 ms later, up to 4 attempts in all, and the toy prints the time of each attempt.

   :::answer[Worked solution]{tests="failures"}
   The solution keeps the toy's idea: a clock in milliseconds, one result for each attempt and the same rule as `ScriptEngine::Update`. A busy attempt moves the next one 250 ms ahead, and the counter ends the reload at the limit.

   ```cpp sketch="scripting-hot-reload-retry.cpp"
   // A reload with retries: a busy file is tried again 250 ms later, up to a limit of attempts.
   #include <cstdio>
   #include <vector>

   int main()
   {
   	const int retryMs = 250;
   	const int maxAttempts = 4;
   	const std::vector<bool> fileBusy = { true, true, true, false }; // What each attempt finds

   	int now = 0;
   	int attempts = 0;
   	while (true)
   	{
   		const bool busy = fileBusy[static_cast<size_t>(attempts)];
   		std::printf("attempt %d at %d ms: %s\n", attempts + 1, now, busy ? "busy" : "loaded");
   		if (!busy)
   			break;
   		if (++attempts >= maxAttempts)
   		{
   			std::printf("giving up\n");
   			break;
   		}
   		now += retryMs;
   	}
   	return 0;
   }
   ```

   ```text output-of="scripting-hot-reload-retry.cpp"
   attempt 1 at 0 ms: busy
   attempt 2 at 250 ms: busy
   attempt 3 at 500 ms: busy
   attempt 4 at 750 ms: loaded
   ```

   1. **Line 9:** what each attempt finds
   2. **Lines 15–16:** one attempt and its time
   3. **Lines 19–23:** the limit ends the reload
   4. **Line 24:** the next attempt is 250 ms later

   The output shows three busy attempts at 0, 250 and 500 ms, and a fourth at 750 ms that loads.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scripting/ScriptEngine.cpp`: `SetHotReloadEnabled`, `StartWatching`, `Update`, `LoadInternal`; `c_MaxReloadAttempts` and `c_ReloadRetryInterval` at its top.
- `Strata/src/Strata/Scripting/ScriptSystem.cpp`: `BeginModuleReload`, `EndModuleReload`, `RunPendingReloads`.
- `Strata/src/Strata/Scripting/ScriptModule.cpp`: `ScriptModule::Load` (the private copy; which load errors are worth trying again).
- `Strata/src/Strata/Core/FileWatcher.h`: `FileWatcherSettings::Debounce`.
- `StrataScriptCore/Include/StrataScript/Script.h`: `OnReload` and the comment on hot reload.
- Tests: `Scripting.Reload` and `Scripting.LoaderFaults`, modules `ReloadV1` and `ReloadV2`.
- Setting: `HotReloadScripts` of the editor's context, true by default.
- Example: `Samples/ThirdPerson/Scripts/Coin.cpp`.

## Further reading

- Live++ documentation: how binary patching reloads C++ code; intermediate.
- Unreal Engine documentation on Live Coding: the same approach inside an engine; intermediate.
- "Game Engine Architecture" by Jason Gregory, the chapters on runtime and tools: how engines separate code and data; intermediate.
- The operating system's documentation of dynamic libraries (`LoadLibrary`, `dlopen`): how a library is loaded and unloaded; advanced.

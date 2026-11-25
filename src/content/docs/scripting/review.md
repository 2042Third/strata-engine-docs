---
id: scripting/review
title: "Review: scripting"
description: "The questions of every page of the part on scripting, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** The engine's class descriptor is 184 bytes, and its last member, `OnUISubmit`, is the 15th callback (bit 14). Module A was built with a software development kit (SDK) from before that member, so its descriptor has `StructSize` 176. Module B was built with the current SDK. A class in both modules overrides `OnCreate`, `OnFixedUpdate` and `OnTriggerExit`, and the class of B overrides `OnUISubmit` as well.

   How many bytes of each descriptor does the engine read, and what are the callback flags of the two classes?

   :::answer[Worked solution]
   The engine reads a member only when the descriptor's size covers it. For A, the check for `OnUISubmit` is 176 ≥ 176 + 8, which is false, so the engine reads 176 bytes and treats that slot as null. For B, the size is 184 and the engine reads all of it.

   The flags have one bit per callback, counted in the order of the table of callbacks. `OnCreate` is bit 0 (value 1), `OnFixedUpdate` is bit 2 (value 4) and `OnTriggerExit` is bit 9 (value 512). The class of A has flags 1 + 4 + 512 = 517. The class of B adds bit 14, which has the value 16,384, so its flags are 517 + 16,384 = 16,901. Both modules work on the new engine, because a struct that only grows at its end is read up to the smaller of the two sizes.
   :::

2. **Basic.** Four loads take place on Windows. In case 1, a shipped game with hot reload off loads its module file for the first time. In case 2, the editor loads a module with hot reload on. In case 3, a second engine in the same process loads the file of case 1 again; in case 4, the editor reloads the module of case 2 after a build.

   For each case, say whether the library loads from the file or from a private copy, and in which cases a build can replace the original file while the game runs.

   :::answer[Worked solution]
   Case 1 loads from the file: without hot reload the mode is `InPlace`, and nothing forces a copy. Case 2 loads from a private copy, because hot reload always asks for one. Case 3 loads from a copy too, because the system hands out the same library for a file that is loaded already, and sharing it would share the static variables of the first load. Case 4 loads from a new copy, as every reload does.

   A copy holds the lock, not the original. The linker can therefore replace the file in cases 2 and 4. In cases 1 and 3 the load of case 1 holds the file itself, so a build could not replace it, and a shipped game does not rebuild its module anyway.
   :::

3. **Medium.** A module is loaded at `0x7ff600000000` in a Release build on Windows. A script writes through a null pointer inside `Fill`, a helper that the compiler inlined into `Coin::OnUpdate`. The stack, from the top, has `memset` in a runtime file, `Fill` in `Coin.cpp`, `Coin::OnUpdate` in `Coin.cpp` and `InvokeScript` in `ScriptModuleEntry.cpp`. The return address of the frame of `Coin::OnUpdate` is `0x7ff600005a30`.

   Which address does the symbol lookup use, what is its offset, which frame does the fault location name, and what happens to the other scripts of the module and to play mode?

   :::answer[Worked solution]
   A return address points after the call, so the lookup uses the byte before it: `0x7ff600005a2f`. Subtract the base, `0x7ff600000000`, and the offset is `0x5a2f`.

   The fault location is the first frame of the module whose file is not runtime code. `memset` has a file, but it is runtime code. `Fill` is the first frame left, and the inline data of the debug information lets Windows name its line even in an optimized build. The SDK's entry file is also skipped, but it comes later. On Linux the report would hold only the faulting instruction, inside `memset`, with no file or line, so it could not name `Fill`.

   A null write is a crash, not an exception. The guard returns, the engine records the fault and marks the whole module as not usable until a reload. Every instance of every class of the module stops getting callbacks, and play mode stops. The instances are leaked on purpose, because their destructors cannot be trusted.
   :::

4. **Medium.** During play with hot reload on, the linker writes the module at 0 ms, 90 ms and 320 ms. A `Spinner` has a field `Speed` that the stored scene gives as 4.0 but that the game changed to 6.0. Its plain member `m_Angle` starts at 0 in the constructor and now holds 90. The rebuilt file is busy for the first three attempts to load it.

   When does the engine report the file, when does the load succeed, and what are `Speed` and `m_Angle` afterwards? Assume each attempt runs at the moment it is due. How long would the engine try if the file stayed busy?

   :::answer[Worked solution]
   The gaps between the writes are 90 ms and 230 ms. Both are under the 300 ms of the debounce, so each write restarts the wait. The last write is at 320 ms, and the watcher reports at 320 + 300 = 620 ms.

   A busy file is worth another try, every 250 ms. The first attempt at 620 ms and the next two, at 870 ms and 1,120 ms, fail. The fourth attempt, at 1,370 ms, loads. During the three failures the old module runs on.

   A field survives by name and type, and the running value wins over the stored one, so `Speed` is 6.0. The plain member `m_Angle` is not a field, and the new instance starts it with the value its constructor gives, 0. `OnReload` runs afterwards, and the script uses it to find such state again.

   If the file stayed busy, the engine would make 20 attempts in all. The last is at 620 + 19 × 250 = 5,370 ms, about five seconds after the report, and then the old module stays. A module that crashes while it loads is not tried again.
   :::

5. **Medium.** A team adds the host function `GetGravityScale`. The table has 165 host functions today, and games built a year ago must keep running on the new engine without a rebuild. One developer inserts the new member after the 100th function, and another appends it at the end.

   Which choice keeps the old games working, what does an old module call under the other choice, what does a new module get from an old engine, and what keeps `ST_SCRIPT_ABI_VERSION` unchanged?

   :::answer[Worked solution]
   An old module finds each function by its place in the table. Appending makes the new member the 166th, and no old member moves, so an old module never reads it and works as before.

   An insert after the 100th function moves the last 65 members one place on. An old module that calls its 101st function now runs `GetGravityScale` with the wrong arguments. The build still passes, because the struct and `ST_SCRIPT_HOST_FUNCTIONS` agree with each other; only a new version number would make such a change safe.

   A new module on an old engine meets a table whose `StructSize` ends before the new member. The SDK checks that with `ST_SCRIPT_DETAIL_HOST_WITH`, sees no function and returns its fallback value, so the script keeps running. Appending changes nothing that an old reader depends on, so the version stays at 1.
   :::

6. **Hard.** A module has 50 `Coin` instances, which implement `OnUpdate` and `OnLateUpdate`, and one `Door`, which implements `OnUpdate`, `OnFixedUpdate`, `OnTriggerEnter` and `OnLateUpdate`. A frame runs two fixed steps, and the player enters the trigger during the second. A normal frame makes 105 callback calls.

   In case A, the `Door` throws a C++ exception in its first `OnFixedUpdate`. In case B it writes through a null pointer there.

   How many callbacks does the frame make in each case, which ones are missing, and what is the state afterwards?

   :::answer[Worked solution]
   The order of a frame puts every `OnUpdate` first, then the fixed steps, then `OnLateUpdate`. Up to the first fixed step of the `Door`, the frame has made 50 + 1 = 51 `OnUpdate` calls and the one `OnFixedUpdate` call: 52 calls, in both cases.

   In case A the SDK catches the exception, and the engine disables that one instance. The module is healthy, so the 50 `Coin` instances still get their `OnLateUpdate` calls: 52 + 50 = 102 calls. The `Door` misses the second `OnFixedUpdate`, the `OnTriggerEnter` and its `OnLateUpdate`, three calls; the total is 105 − 3 = 102. Play continues, and only the `Door` is out.

   In case B the guard contains the crash and the engine faults the module. Nothing in it can be trusted, so the system makes no more calls into it. The frame ends at 52 calls, and 53 calls are missing. Play mode stops, and the instances are leaked on purpose: they are not destroyed, because their destructors would run in a module in an unknown state. A reload of the module clears the fault.
   :::

7. **Hard.** A scene holds 20 entities with a `Coin` entry and 30 with a `Door` entry. During play with hot reload on, you rename the class `Coin` to `Pickup` in the source and rebuild. The `Door` keeps a plain member `m_Open` and a field `Locked`.

   What does the engine do with the 50 entities after the reload, what does the log show, and what must you do to bring the coins back?

   :::answer[Worked solution]
   The new module loads, because it has no fault: a missing class is no reason to refuse a module. Each scene saves the fields of its instances, the old library unloads and the system matches the entries against the new module.

   The 30 `Door` entries match by class name, so the 30 doors return, with `Locked` restored by name and type. Their `m_Open` is a plain member, so each starts over with the value of its constructor, and `OnReload` runs on each of them to find the state again.

   The 20 `Coin` entries find no class, so the system makes no instances for them and reports a problem for each of the 20 entities. The entries stay in the scene. The coins do nothing until you change the 20 entries to `Pickup`. A new entry holds only the field values you give it, so you set the values of the old entries again.
   :::

8. **Hard.** A studio wants to contain every fault of its scripts. It proposes to run the scripts in a child process. The game updates 10,000 scripted entities each frame at 60 frames per second, so a frame has 16.67 ms. Assume that each call across the process boundary costs 5 microseconds.

   Does the proposal fit the frame? Name what it gains over Strata's guard, and what stays outside the guard today. What would the studio lose if it moved its scripts to a managed language such as C# instead?

   :::answer[Worked solution]
   At 60 frames per second a frame has 1000 / 60 = 16.67 ms. Ten thousand calls at 5 microseconds cost 10,000 × 5 = 50,000 microseconds, which is 50 ms. The calls alone take three times the frame, so the game would run at about 1000 / 50 = 20 frames per second at best, with no time left for the engine. Batching the calls would reduce the cost, but it also means that the engine and the scripts no longer share the scene.

   The guard runs in the same process and costs a few instructions per call, so the same 10,000 calls fit in the frame. A process gains containment of more faults: a corrupted heap, a call of `abort()` on every platform, and an endless loop, because the engine can end the child.

   The guard does not contain these today. A call of `abort()` ends the process on Linux, and on Windows when the module uses the shared C runtime. A script with `while (true) {}` freezes the editor, and the watchdog only logs and is off in the editor. Strata accepts these exits because every script call stays cheap, and it names them so that scripts never block.

   A managed language catches most errors in its runtime, inside one process, but not all of them. The studio would lose full speed, since a managed runtime pauses. It would also lose the one language that the engine and the game share, and the C++ tools.
   :::

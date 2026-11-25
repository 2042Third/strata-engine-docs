# Brief: `scripting/hot-reload`

| Field | Value |
| --- | --- |
| Title | Hot reload |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/script-system`, `core/files` |
| From | scripting ch. 14 (the watcher, copies, the reload protocol in the engine and in scenes, what survives, failures; excerpt 28, figure 9); home of hot reload |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/hot-reload` — Hot reload

**Covers.** The job: replace the module while the game runs and keep what the scripts can keep. The problem and how
engines solve it, the full section, since this page is the home of hot reload of scripts: a restart with saved state;
swapping a library with its state serialized (Strata, many in-house engines); binary patching (Live++, Unreal's Live
Coding); interpreters that reload functions; with a table of what each keeps, what each costs and who uses it. The
timeline (figure), walked in code: hot reload turned on moves a module that runs from its file to a private copy,
because Windows locks a loaded DLL; the watcher reports the file once it stayed unchanged for 300 ms;
`ScriptEngine::Update` reloads between frames and retries up to 20 times at 250 ms while the file is busy; the new
module loads beside the old one, so a broken build leaves the old one running; each running scene's `BeginModuleReload`
snapshots the fields of every instance and destroys the instances without `OnDestroy`; the old library unloads;
`EndModuleReload` recreates the instances, restores the fields that keep their name and type, and `OnReload` runs
instead of `OnCreate` at the next sync point. The toy: a reload of a one-class module with its fields in about 50 lines.
What survives: fields only; everything else (cached entities, script pointers, plain members) starts over and is found
again in `OnReload`, and the module's globals and statics start over too, because the new module is another library.
Copies and dependencies: `$ORIGIN` and `@loader_path` resolve from the copy's folder. Failures: a module that does not
load, a reload refused while script code is on the stack, a faulted module replaced by a good one, and a class that no
longer exists, whose instances are dropped with a problem. What the person sees: a playing ThirdPerson copy before and
after a rebuild, and the log line "Reloaded script module". Tests: `Scripting.Reload` with the `ReloadV1` and `ReloadV2`
modules. The example is the ThirdPerson `Coin`: `SpinSpeed` keeps the value set in the Inspector, the non-field `m_Time`
starts over, and its `OnReload` calls `OnCreate` to find its model again. At the end the reader can say what a reload
keeps and loses, and why the build never fights the running game for the file.

**Leaves out.**

- The load modes and the private copy directory → `scripting/loading`
- The editor's builds that write the new module → `editor/script-builds`
- Hot reload of assets, the other meaning → `assets/importing`
- Using hot reload while making a game → `make/first-script`

**Fit.** `fits`: about 4,800 words against L (5,000). The full section on how engines reload code, three excerpts, the
timeline, the before-and-after screenshots and two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:319` | concept | home | Hot reload: the approaches, Strata's swap with fields kept, why private copies; the mistakes (state in plain members, pointers into the old module, RUNPATH under copies) |
| `scripting:378` | code | home | `Strata/src/Strata/Scripting/ScriptEngine.cpp:65-124`: the new module loaded beside the old one and the reload across scenes; with lines 196-229, the debounced reload with retries |
| `scripting:381` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:1221-1348`: a reload in a scene, the snapshot, destruction without `OnDestroy`, the recreation, the restore, `OnReload` or `OnCreate` |
| `new:10` | code | home | `Strata/src/Strata/Scripting/ScriptEngine.cpp:154-189`: turning hot reload on moves a module to a copy; the watcher with its 300 ms debounce |
| `scripting:419` | figure | home | The hot reload timeline, with the failure branch that keeps the old module and the retry branch for a busy file |
| `scripting:438` | figure | home | Hot reload in action: a playing ThirdPerson copy before and after a rebuild of `Coin`, with the log line |
| `scripting:472` | rule | home | Only fields survive hot reload; re-acquire everything else in `OnReload`; the module's globals and statics start over too, since the new module is another library loaded beside the old one, which then unloads (`Strata/src/Strata/Scripting/ScriptEngine.cpp:79-83`, `:107`) |
| `scripting:494` | rule | home | Hot reload runs a copy; `$ORIGIN` and `@loader_path` point at the copy's folder |
| `scripting:511` | hands-on | home | Hot reload a running game: change `Coin`'s behaviour while playing a ThirdPerson copy, then add a plain member and see it start over |
| `new:26` | hands-on | home | The "trace it yourself" exercise (R32, D27): with a breakpoint in `ScriptSystem::BeginModuleReload` while a ThirdPerson copy plays and `Coin` is rebuilt, the reader walks up the stack to `ScriptEngine::Update`, which the watcher's report started, then on through the swap in `ScriptEngine::LoadInternal`, `EndModuleReload` and the `OnReload` call at the next sync point (about 250 words). Evidence: `Strata/src/Strata/Scripting/ScriptEngine.cpp:65`, `:101`, `:107`, `:114`, `:196-229`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:659-660`, `:1221`, `:1276` |
| `scripting:576` | term | home | Debounce |
| `scripting:591` | term | home | Hot reload (of scripts), one of the two meanings |
| `scripting:156-157` | feature | use | Load modes and the private copy directory (their home is `scripting/loading`) |
| `scripting:168` | feature | use | Field values, snapshot and restore |
| `new:27` | feature | use | A class that no longer exists after a reload, named among the failures in one sentence (its home is `scripting/script-system`) |
| `scripting:385` | code | use | The `Coin` script as the example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Instances, sync points and field values | `scripting/script-system` | must |
| Load modes and private copies | `scripting/loading` | must |
| Shared libraries: unloading, reference counts, RUNPATH | `scripting/shared-libraries` | must |
| Files you can trust: watching a folder, private files | `core/files` | must |
| What a fault leaves behind | `scripting/crash-containment` | helps |
| Building scripts from the editor | `editor/script-builds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `debounce` | Debounce | - |

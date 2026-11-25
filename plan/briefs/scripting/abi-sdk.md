# Brief: `scripting/abi-sdk`

| Field | Value |
| --- | --- |
| Title | Inside the ABI and the SDK |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/shared-libraries`, `basics/cpp-generic`, `world/reflection` |
| From | scripting ch. 10 (`ScriptABI.h`, the host table, descriptors, the SDK's thunks, registration, override detection; excerpts 1-13) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/abi-sdk` — Inside the ABI and the SDK

**Covers.** The job: the two sides of the boundary, the C header `ScriptABI.h` that both sides compile and the
header-only C++ SDK that game code is written against; what they are responsible for and what loading and the host API
do instead. The problem in one paragraph that links `scripting/shared-libraries`. The map: the SDK's files
(`ScriptABI.h`, `Host.h`, `Script.h`, `Value.h`, the umbrella `StrataScript.h`, the entry file) and which side owns
what. The toy: a two-function host table and a one-class descriptor in about 60 lines of C and C++. Then the real code
in the order data crosses the boundary. First the C side: the contract comment; the two exports and their macros; opaque
handles and ids; strings, results and the tagged-union value; transforms; a frozen struct (`StrataScriptRaycastHit`, 40
bytes, layout asserts) against an extensible one (`StrataScriptCollision`, with `StructSize`) and the struct the engine
fills up to the module's capacity (`StrataScriptGraphicsOptionInfo`); `ST_SCRIPT_HAS_MEMBER` and the head of the host
table, with the buffer protocol for text and arrays; the field, class and module descriptors, the class descriptor's 15
callback slots null when not implemented. Then the SDK, which turns that C into classes: `Host.h`'s current context as a
scope, the buffer-retry reads, and `ST_SCRIPT_DETAIL_HOST_WITH` for functions an older engine lacks; the `Script` base
class and how it binds its entity in its constructor; `InvokeScript`, the exception firewall, and one thunk per
callback; override detection at compile time with `requires` and member-pointer types, so the engine never calls a
callback a class does not implement; static self-registration through `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`
(`__COUNTER__`, an intrusive list built during static initialization without allocation, `ScriptClassBuilder::Field`
with its static asserts, the ten field types and their value traits); `BuildClassRecord`, which reads defaults from one
default-constructed instance (why a constructor must do nothing); `LoadModule` and `WriteModuleAPI`, which check the
versions and the baseline member `GetScrollDelta` and write at most the engine's capacity. Last, the helpers that run
entirely in the module (`Random`, `Timer`, `KeyRepeat`, `Motion`) and why they never meet engine classes of the same
name (the one-definition rule). The example is the ThirdPerson sample's `Coin`: its `ST_SCRIPT_CLASS` block followed to
the descriptor the engine reads. What Strata does not do: calls into scripts from other threads. Tests: `Scripting.API`,
the `NewerSDK` module, and `Architecture.ScriptSDK`, which keeps the SDK's classes away from the engine's classes of the
same name: it scans the sources of the engine, the editor, the runtime, the CLI and the tests, and fails on any include
of a `StrataScript/` header other than `ScriptABI.h` outside a raw string. At the end the reader can read any struct of
the ABI, say which side may read which member, and trace a class from its macro to its descriptor.

**Leaves out.**

- Why C, and how binary interfaces are versioned → `scripting/shared-libraries`
- Loading the module and validating its description → `scripting/loading`
- How host functions are implemented and listed → `scripting/host-api`
- Abort containment in the SDK's entry file → `scripting/crash-containment`
- Every SDK class and function with the host function it wraps → `reference/script-api`
- Writing a script class, `override` and fields as a game maker does → `make/first-script`
- The PCG32 algorithm of `Random` → `basics/math-probability`

**Fit.** `over`: about 6,600 words against L (5,000). Twelve excerpts with what to look for, the C++ they use (member
pointers, `requires`, token pasting), seven rules and three exercises take the most words; by S2 the next size, XL
(8,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:38-51` | feature | home | The C side in order: the two entry points, the ABI version, the export macros, layout asserts, size-prefixed extensibility, opaque handles, strings, results, the tagged-union value, transforms, frozen structs, the engine-filled and the module-filled extensible structs, the API's enums |
| `scripting:53-57` | feature | home | The host table as a struct (its `StructSize`, `ABIVersion`, 165 function pointers), the buffer protocol, the field, class and module descriptors |
| `scripting:102-117` | feature | home | The SDK: umbrella header, plumbing, graceful degradation, the `Script` base class, the exception firewall, thunks, override detection, static self-registration, class records, the version-safe module write, `LoadModule`, `ScriptClassBuilder`, the macros, the ten field types, value traits, `AssetHandle` |
| `scripting:137` | feature | home | The module entry source: the two exports every module gets (its abort containment is `scripting/crash-containment`'s) |
| `scripting:278` | concept | home | A C++ SDK over a C ABI: thunks, static self-registration, member-pointer fields, compile-time override detection, `__COUNTER__`, the buffer-retry protocol; the mistakes (registration in a header, side effects in constructors) |
| `scripting:343` | concept | link | The determinism helpers named where the page says why they live in the module (`scripting:490`); the concept's home is `make/recipes` |
| `scripting:354` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:3-27`: the whole contract in one comment |
| `scripting:355` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:304-320`: the head of the host table with the buffer protocol's comment; with lines 67-69, `ST_SCRIPT_HAS_MEMBER` |
| `scripting:356` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:111-140`: the tagged union, the one value type that crosses |
| `scripting:357` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:159-192`: a frozen struct with layout asserts against an extensible one, and the comments that say why |
| `scripting:358` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:758-851`: the field, class and module descriptors |
| `scripting:360` | code | home | `StrataScriptCore/Include/StrataScript/Host.h:36-55`: the current context as a scope; with lines 69-85 (the buffer-retry read) and 106-111 (`ST_SCRIPT_DETAIL_HOST_WITH`) |
| `scripting:361` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:70-108`: the `Script` base class, binding its entity and context in its constructor |
| `scripting:362` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:184-203`: `InvokeScript`, the exception firewall; with lines 246-250, one thunk |
| `scripting:363` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:371-378`: override detection with `requires` and a member-pointer type; with lines 506-541, `GetCallbackFlags` |
| `scripting:364` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:543-617`: static self-registration into an intrusive list; with lines 852-865, the macros |
| `scripting:365` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:638-690`: `BuildClassRecord`, defaults from a default-constructed instance, null slots for callbacks not implemented |
| `scripting:366` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:692-762`: `WriteModuleAPI` and `LoadModule`, the version checks and writing at most the receiver's capacity |
| `gamedev:362` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:348-376`: the callback flags and the first override check, and with lines 842-865 the macros; the page shows these lines once, inside the excerpts of `scripting:363` and `scripting:364` |
| `scripting:448` | rule | home | Only plain C data crosses the ABI, with its reason |
| `scripting:450` | rule | home | Append, never insert, reorder or remove; appending keeps the ABI version |
| `scripting:452` | rule | home | Check `ST_SCRIPT_HAS_MEMBER` before using a function appended after the initial set |
| `scripting:454` | rule | home | Frozen structs stay frozen, because the engine writes arrays of them into the module's buffers |
| `scripting:467` | rule | home | Classes are default-constructible and constructors do nothing: the mechanism (one instance at load reads the defaults); the game maker's rule is `make/first-script`'s |
| `scripting:470` | rule | home | One `ST_SCRIPT_CLASS` per class, in a `.cpp`: each translation unit would register it again, and the engine refuses the duplicate |
| `scripting:490` | rule | home | SDK helpers named like engine classes are tested only inside a module; no engine source includes the SDK's C++ headers (`Architecture.ScriptSDK`) |
| `build-test:184` | feature | home | `Architecture.ScriptSDK`, the test of `scripting:490`: it reads every `.h`, `.cpp` and `.mm` of `Strata/src`, `StrataEditor/src`, `StrataRuntime/src`, `StrataCLI/src` and `StrataTests/src` and lists each include of a `StrataScript/` header other than `ScriptABI.h`, lines inside raw strings skipped (`StrataTests/src/Architecture/ScriptSDKTests.cpp:87-160`) |
| `audio-input:541` | rule | home | The same rule as the input area states it (`KeyRepeat`, `Random`, `Timer`); one rule box with `scripting:490` |
| `animation:483` | rule | home | New host functions are appended, never inserted, with the animators' twelve functions as the example; one rule box with `scripting:450` |
| `audio-input:693` | term | home | Text buffer protocol; one glossary entry with `scripting:567` |
| `scripting:540` | hands-on | home | Exercise: what happens when a module's `StrataScriptModuleAPI` is larger or smaller than the engine's (as the `NewerSDK` test module does) |
| `gamedev:557` | hands-on | home | Exercise: add an SDK helper to `Gameplay.h` (a `Cooldown` class), used and tested only inside a script module |
| `new:22` | hands-on | home | The "trace it yourself" exercise (R32, D27): `ST_SCRIPT_CLASS(Coin)` followed with a search from the macro to its static `ClassRegistrar`, then with a breakpoint in `BuildClassRecord` while the engine loads a ThirdPerson copy's module, to the class descriptor that `WriteModuleAPI` hands over and `ScriptModule::ReadModuleDescription` reads (about 250 words). Evidence: `Samples/ThirdPerson/Scripts/Coin.cpp:54`; `StrataScriptCore/Include/StrataScript/Script.h:589-617`, `:640`, `:702`, `:852`, `:864`; `Strata/src/Strata/Scripting/ScriptModule.cpp:942` |
| `scripting:559` | term | home | ABI version |
| `scripting:567` | term | home | Buffer protocol |
| `scripting:571` | term | home | Class descriptor |
| `scripting:572` | term | home | Context, the opaque per-scene handle |
| `scripting:588` | term | home | Frozen struct |
| `scripting:589` | term | home | Host |
| `scripting:597` | term | home | Module description |
| `scripting:598` | term | home | ODR (one-definition rule) |
| `scripting:607` | term | home | SDK |
| `scripting:612` | term | home | `StructSize` |
| `scripting:616` | term | home | Thunk |
| `new:3` | not-done | home | Calls into scripts from other threads: the engine calls the module on its main thread only, and the module calls the host only from within those calls. Evidence: `StrataScriptCore/Include/StrataScript/ScriptABI.h:25-26` |
| `scripting:92` | feature | use | The 15 callback slots of the class descriptor (their order and dispatch are `scripting/script-system`'s) |
| `scripting:359` | code | use | `StrataScriptCore/Source/ScriptModuleEntry.cpp:73-81`, the two exports; the rest of the file is `scripting/crash-containment`'s |
| `scripting:385` | code | use | The `Coin` script's registration block as the example (its home is `make/recipes`) |
| `scripting:133-136` | feature | link | `Random`, `Timer`, `KeyRepeat` and `Motion` named as the helpers that live in the module; their homes are `make/recipes` (`Random`), `make/timers-events` (`Timer`, `KeyRepeat`) and `make/gameplay-math` (`Motion`), and `reference/script-api` lists their facts |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shared libraries and binary interfaces: exports, static initializers at load, ABI against API, size prefixes | `scripting/shared-libraries` | must |
| Templates, lambdas and pointers to members | `basics/cpp-generic` | must |
| `constexpr`, `if constexpr`, concepts and `requires`, macros, `std::string_view` | `basics/cpp-modern` | must |
| Inheritance and virtual calls | `basics/cpp-classes` | must |
| Reflection: one registration, many uses | `world/reflection` | must |
| C++ exceptions and the engine's error policy | `core/conventions` | must |
| Bytes, text encodings and UTF-8 | `basics/bytes` | helps |
| The script lifecycle and its callbacks | `scripting/script-system` | helps |
| What is special to script code (the `Script` base class, `override`, the macros) | `start/first-game` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `structsize` | `StructSize` | - |
| `abi-version` | ABI version | - |
| `buffer-protocol` | Buffer protocol | Text buffer protocol |
| `class-descriptor` | Class descriptor | - |
| `context` | Context | - |
| `frozen-struct` | Frozen struct | - |
| `host` | Host | - |
| `module-description` | Module description | - |
| `odr` | ODR | one-definition rule |
| `sdk` | SDK | - |
| `thunk` | Thunk | - |

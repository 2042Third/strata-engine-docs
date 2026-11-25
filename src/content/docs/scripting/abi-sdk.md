---
id: scripting/abi-sdk
title: "Inside the ABI and the SDK"
description: "How the C header ScriptABI.h and the header-only C++ SDK carry a game's script classes across the boundary: structs, size prefixes, thunks and registration."
kind: internals
size: L
tracks: [E]
needs: [scripting/shared-libraries, basics/cpp-generic, world/reflection]
time: 115
learn:
  - id: read-structs
    text: explain which side of the boundary may read which member of a frozen, a size-prefixed and an engine-filled struct
  - id: has-member
    text: compute whether a size-prefixed struct holds a member, and what each side does when it does not
  - id: trace-class
    text: trace a script class from its macro through the registration object and the class record to the descriptor the engine reads
  - id: override-detection
    text: explain how the SDK finds the callbacks a class overrides and why the engine never calls the others
  - id: constructor-rule
    text: explain why a script constructor does nothing and why a class is registered once, in a source file
since: 0.3.0
status: final
---

The script boundary has two sides, and a small amount of code on each. This page covers the software development kit (SDK) of the boundary, a set of :term[header files]{id=header-file} that game code includes. The **SDK** is a header-only C++ library, and it builds script classes, fields and :term[callbacks]{id=callback} out of a C :term[header]{id=header}. The page does not cover why the boundary is C or how the engine loads a module. It also omits the inside of each host function and the containment of a crash: other pages of this part do.

The engine side is the **host**: the engine's program, seen from a script module as one table of functions to call. The module is a :term[shared library]{id=shared-library} that never links the engine. All it has is a header, `ScriptABI.h`, and everything that crosses between the two is plain data described there. After this page you can read any :term[struct]{id=struct} of that header, say which side may read which member, and follow a class from its :term[macro]{id=macro} to the description the engine reads.

## The problem and how engines solve it

A script module is compiled at a different time, often by a different build, than the engine that runs it. When a game maker rebuilds the module while the game runs, the engine must unload the old code and call the new code without restarting. The two sides can only trust what the page of [shared libraries](../scripting/shared-libraries.md) calls the application binary interface (ABI): sizes, offsets and calling rules. C++ does not fix those across :term[compilers]{id=compiler} and :term[standard libraries]{id=standard-library}, and an exception that leaves one side lands in the other side's stack.

Engines answer in four ways.

- Share C++ classes across the boundary. Calls are natural and cheap, but both sides must use the same compiler, the same standard library and the same flags, and an exception or a failed allocation can cross by accident.
- Embed a scripting language. Unity runs C# and Godot offers GDScript; many other engines embed a small language of their own. The language is the boundary and can contain errors, but game makers learn a second language and every engine function needs binding code.
- Run scripts in another process and send messages. A crash is fully isolated, but every call is copied and waits for an answer, which a gameplay loop calling hundreds of functions per frame cannot afford.
- Put a C interface of plain functions and structs at the boundary, and give game makers a C++ library on top. Godot's native extension interface works this way, and so does Strata.

Strata keeps C++ as the game language and the boundary in C. The C header is small and rarely changes, and the SDK hides it. The cost is that someone must write the glue that turns classes into tables of :term[function pointers]{id=function-pointer}. That glue is the SDK, and most of this page reads it. A single number, the **ABI version**, names the whole interface: `ST_SCRIPT_ABI_VERSION` is 1 at the pin, and the engine refuses a module built against another number.

## The map: files and owners

The SDK lives in `StrataScriptCore/Include/StrataScript/`, and one :term[source file]{id=source-file} of the same library supplies the :term[entry points]{id=entry-point-scripting}. A game's script module includes only the umbrella header `StrataScript.h`, which includes all the others.

| File | What it holds | Who reads it |
| --- | --- | --- |
| `ScriptABI.h` | The C contract: structs, enums, the host table and the descriptors | The engine and every module |
| `Host.h` | The module's copy of the host table pointer and the current context | Module code only |
| `Value.h` | Conversions between C++ values and the tagged union | Module code only |
| `Script.h` | The `Script` :term[base class]{id=base-class}, thunks, registration and loading | Module code only |
| `StrataScript.h` | The umbrella that includes everything, as the game makers see it | Module code only |
| `ScriptModuleEntry.cpp` | The two exported functions; compiled into every module | Module code only |

The other headers (`Entity.h`, `Input.h`, `Physics.h` and their neighbours) wrap host functions in classes. Together they form the application programming interface (API) of game code, and the [script reference](../reference/script-api.md) lists them. Only `ScriptABI.h` is plain C, so it is the one file the engine may include; a test enforces that.

The word **context** names a handle the engine gives the module. It is a pointer to a structure that only the engine defines, one per scene, and every scene-related host function takes it so the engine knows which scene is meant.

```mermaid caption="The boundary: the engine side holds the host table and calls the descriptors, the module side holds the SDK, the entry points and the game classes, and the C header is compiled by both." alt="A diagram with three groups. The engine side contains the script system and the host table implementation. The shared group contains the C header. The module side contains the entry file, the C plus plus classes of the SDK and the game's script classes. Arrows show the engine calling the two exports and the descriptors, and the module calling host functions."
flowchart LR
	subgraph Engine
		system["ScriptSystem and ScriptModule"]
		hostimpl["Host table: 165 functions"]
	end
	header["ScriptABI.h (C)"]
	subgraph Module
		entry["ScriptModuleEntry.cpp: two exports"]
		sdk["SDK: Host.h, Value.h, Script.h"]
		game["Game classes: Coin..."]
	end
	system -- "StrataScript_Load" --> entry
	system -- "descriptor callbacks" --> sdk
	sdk -- "host function calls" --> hostimpl
	game --> sdk
	system -.-> header
	sdk -.-> header
```

## The contract

Whoever writes either side keeps these rules. Each has a reason, and each is checked by a compiler or a test.

- **Only plain C data crosses.** Pointers and sizes, :term[integers]{id=integer}, floats, fixed arrays, structs of those, and function pointers. A standard string or vector has a layout that depends on the compiler, and an exception has no meaning in C.
- **Strings are a pointer and a size, in UTF-8, without a terminating zero.** The size makes a string cheap to pass and safe to cut.
- **Everything runs on the main thread.** The engine calls the module on its main thread, and the module calls the host only from within those calls. Strata does not call scripts from other threads, so the scene needs no lock against them. Only the two diagnostic functions, `Log` and `ReportException`, may be called from any thread.
- **Every call into the module returns a result.** The module never lets an exception out: it reports the message through the host and returns `StrataScriptResult_Exception`.
- **Frozen structs stay frozen.** A **frozen struct** is a struct whose layout is fixed for the whole ABI version, because it has no size field. Its reason follows in the next section.
- **Other structs begin with a size.** The **`StructSize`** member, the first member of every size-prefixed struct, says how many :term[bytes]{id=byte} the writer built it with, so the reader can tell which later members exist.
- **Text and arrays follow one buffer protocol.** The **buffer protocol** says that a function returning text or an array copies at most `capacity` elements into the caller's buffer. It returns the total number available, so the caller tries again with a larger buffer.

:::rule[Only plain C data crosses the ABI]
The engine's `AGENTS.md` bars standard-library types, engine types and exceptions at the boundary. The module and the engine may be built by different compilers on different days, and only plain data has one layout for all of them. See [shared libraries](../scripting/shared-libraries.md) for the reasons behind a C interface.
:::

:::rule[Append host functions, never insert or move]
New host functions, callbacks and descriptor members go at the end of their struct, and the version stays. Insert or move one, and every function after it moves: an older module would call the wrong function. The SDK checks for a late function before it uses it.
:::

:::note[Frozen structs stay frozen]
The engine fills arrays of `StrataScriptRaycastHit` in buffers that a module owns, and the structs carry no size. One member added later would make each element larger, and the engine would write past the end of the old module's buffer. More data needs a new struct and a new function.
:::

## A toy version

The toy below has the same three ideas in 85 lines of one file. A host table ends in a function that an older engine lacks. A class descriptor has a null slot for a callback the class does not write. A module's load function writes a description no larger than the engine's struct. The program prints what it does against an old engine and a new engine.

```cpp sketch="scripting-abi-sdk-toy.cpp"
// A toy script boundary: a host table that grows at its end, a class descriptor with null callbacks, and a module that
// fills a description no larger than the engine's struct holds.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

#define TOY_HAS_MEMBER(type, pointer, member) \
	((pointer)->StructSize >= offsetof(type, member) + sizeof(((type*)0)->member))

struct ToyHostAPI
{
	uint32_t StructSize;
	void (*Log)(const char* text);
	float (*GetTime)();
	float (*GetScale)(); // Appended after the first release
};

struct ToyClassDesc
{
	uint32_t StructSize;
	const char* Name;
	void (*OnCreate)();
	void (*OnUpdate)(float deltaTime);
};

struct ToyModuleAPI
{
	uint32_t StructSize;
	uint32_t ClassCount;
	const ToyClassDesc* const* Classes;
};

namespace
{

	const ToyHostAPI* s_Host = nullptr;

	void SpinnerUpdate(float deltaTime)
	{
		s_Host->Log("Spinner update");
		float scale = 1.0f;
		if (TOY_HAS_MEMBER(ToyHostAPI, s_Host, GetScale) && s_Host->GetScale)
			scale = s_Host->GetScale();
		std::printf("turned %.2f degrees at time %.1f\n", 90.0f * deltaTime * scale, s_Host->GetTime());
	}

	const ToyClassDesc c_Spinner = { sizeof(ToyClassDesc), "Spinner", nullptr, &SpinnerUpdate };
	const ToyClassDesc* const c_Classes[] = { &c_Spinner };

}

void ModuleLoad(const ToyHostAPI* host, ToyModuleAPI* outModule)
{
	s_Host = host;
	const ToyModuleAPI description = { sizeof(ToyModuleAPI), 1, c_Classes };
	const uint32_t capacity = outModule->StructSize;
	std::memcpy(outModule, &description, capacity < sizeof(description) ? capacity : sizeof(description));
	outModule->StructSize = sizeof(description);
}

void EngineLog(const char* text) { std::printf("[log] %s\n", text); }
float EngineTime() { return 12.5f; }
float EngineScale() { return 2.0f; }

int main()
{
	ToyHostAPI host = { static_cast<uint32_t>(offsetof(ToyHostAPI, GetScale)), &EngineLog, &EngineTime, nullptr };
	for (int release = 1; release <= 2; release++)
	{
		if (release == 2)
		{
			host.StructSize = sizeof(ToyHostAPI);
			host.GetScale = &EngineScale;
		}
		ToyModuleAPI module = {};
		module.StructSize = sizeof(ToyModuleAPI);
		ModuleLoad(&host, &module);
		const ToyClassDesc* desc = module.Classes[0];
		std::printf("engine %d: %s, OnCreate %s, OnUpdate %s\n", release, desc->Name, desc->OnCreate ? "set" : "null", desc->OnUpdate ? "set" : "null");
		if (desc->OnUpdate)
			desc->OnUpdate(0.5f);
	}
	return 0;
}
```

```text output-of="scripting-abi-sdk-toy.cpp"
engine 1: Spinner, OnCreate null, OnUpdate set
[log] Spinner update
turned 45.00 degrees at time 12.5
engine 2: Spinner, OnCreate null, OnUpdate set
[log] Spinner update
turned 90.00 degrees at time 12.5
```

1. **Line 16:** `GetScale` is the member a later release appended; an engine built before it reports a `StructSize` that stops short.
2. **Lines 43–44:** the module asks `TOY_HAS_MEMBER` before it calls `GetScale`, and falls back to 1 when the member is missing.
3. **Lines 57–59:** the module copies at most the engine's capacity, then reports the size it was built with.

The first run shows an engine that stops at `GetTime`: the module turns 90 degrees per second for 0.5 s, 45 degrees, and no more. The second shows one that appended `GetScale`: the same call now doubles to 90 degrees. The class has no `OnCreate`, and its slot stays null. The real code does the same things at a larger scale, with one idea more: nobody writes the table of callbacks by hand, because the SDK builds it from the C++ class.

## The real code, in the order data crosses

The tour follows the boundary from the C header to the class a game maker writes.

### The header's own summary

The header opens with a comment that holds the whole contract. Search for the two exports, the rule for appended members, and the single-thread rule.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L3-L27"
/*
 * Strata script ABI: the C interface between the engine and game script modules.
 *
 * A script module is a shared library built from game code against StrataScriptCore only; it never links the
 * engine. The engine loads it and calls two exported functions:
 *
 *   uint32_t StrataScript_GetABIVersion(void);
 *   uint32_t StrataScript_Load(const StrataScriptHostAPI* host, uint32_t hostABIVersion, StrataScriptModuleAPI* outModule);
 *
 * The host API table gives scripts access to the engine; the module API describes the script classes (outModule->StructSize
 * tells the module how large the host's struct is, see StrataScriptModuleAPI). Everything
 * crossing this boundary is plain data: no C++ types, no exceptions, strings as (pointer, size) in UTF-8, entities and
 * assets as 64-bit ids, math as float arrays (quaternions are x, y, z, w).
 *
 * Compatibility rules:
 *   - ST_SCRIPT_ABI_VERSION changes on every incompatible change (a changed signature, struct layout or meaning,
 *     removed or reordered members). The engine refuses modules built against another version.
 *   - New host functions, module callbacks and descriptor members are only ever appended to the end of their struct,
 *     which keeps the version. Every extensible struct starts with its StructSize, so either side can tell whether
 *     the other one knows a member (see ST_SCRIPT_HAS_MEMBER).
 *   - Calls into the module return a StrataScriptResult. Modules never let C++ exceptions escape: they report the
 *     message through StrataScriptHostAPI::ReportException and return StrataScriptResult_Exception.
 *   - Everything is single-threaded: the engine calls the module on its main thread, and the module calls the host
 *     only from within those calls.
 */
```

1. **Lines 9–10:** the whole entry surface is two functions; the engine needs nothing else from a module.
2. **Lines 20–22:** appending keeps the version, and the size prefix lets either side ask whether the other knows a member.
3. **Lines 25–26:** the sentence that fixes the thread rule; no function of the module runs on a thread of its own.

The macros after the comment name the exports for both compilers (`ST_SCRIPT_EXPORT`) and the C linkage (`ST_SCRIPT_EXTERN_C`), and `ST_SCRIPT_DETAIL_STATIC_ASSERT` checks the layout of structs in C and C++ alike. The macro `ST_SCRIPT_HAS_MEMBER(type, pointer, member)` is true when the pointer's `StructSize` is at least the member's offset plus its size.

### Handles, strings and the tagged value

An entity is a 64-bit id, an asset is a 64-bit id, and 0 is the null for both. A context and a script instance are opaque: the module only passes them back. The value type of a field is one struct, a type tag with a union.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L111-L140"
/* Types of script field and component property values. Stored as uint32_t. */
typedef enum StrataScriptValueType
{
	StrataScriptValueType_Empty = 0,
	StrataScriptValueType_Bool,
	StrataScriptValueType_Int,    /* Int; component Int, UInt and Enum properties */
	StrataScriptValueType_Float,
	StrataScriptValueType_Vec2,
	StrataScriptValueType_Vec3,   /* Also component Color3 properties */
	StrataScriptValueType_Vec4,   /* Also component Color4 properties */
	StrataScriptValueType_Quat,   /* x, y, z, w */
	StrataScriptValueType_String,
	StrataScriptValueType_Entity,
	StrataScriptValueType_Asset
} StrataScriptValueType;

typedef struct StrataScriptValue
{
	uint32_t Type; /* StrataScriptValueType */
	uint32_t Padding;
	union
	{
		bool Bool;
		int64_t Int;
		float Float;
		float Vector[4];           /* Vec2/Vec3/Vec4 use the first 2/3/4 elements; Quat is x, y, z, w */
		uint64_t ID;               /* Entity or Asset */
		StrataScriptString String;
	} As;
} StrataScriptValue;
```

1. **Lines 127–130:** the tag comes first and a padding member keeps the union at an 8-byte offset on every compiler.
2. **Line 136:** a vector of two, three or four floats and a quaternion share one array; the tag says how many elements count.
3. **Line 138:** a string value holds a pointer into memory the sender owns, so a reader copies it before the next call.

The value is the only type that crosses for fields and component properties; an integer travels as 64 bits and the SDK checks that it fits the field.

### A frozen struct and a size-prefixed one

Two structs of 40 bytes show the two kinds. `StrataScriptRaycastHit` is frozen; `StrataScriptCollision` starts with a `StructSize`.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L159-L192"
/* A hit of a physics ray: the entity owning the body, the world space point and surface normal, and the distance from
 * the ray's origin. Its layout is frozen for the ABI version: modules pass arrays of it (RaycastAll) that the engine
 * fills, and they carry no size, so a member appended later would overrun the buffers of older modules. More data
 * needs a new struct and function. */
typedef struct StrataScriptRaycastHit
{
	StrataScriptEntityID Entity;
	float Point[3];
	float Normal[3];
	float Distance;
	uint32_t Padding;
} StrataScriptRaycastHit;

ST_SCRIPT_DETAIL_STATIC_ASSERT(sizeof(StrataScriptRaycastHit) == 40 && offsetof(StrataScriptRaycastHit, Entity) == 0
	&& offsetof(StrataScriptRaycastHit, Point) == 8 && offsetof(StrataScriptRaycastHit, Normal) == 20
	&& offsetof(StrataScriptRaycastHit, Distance) == 32 && offsetof(StrataScriptRaycastHit, Padding) == 36,
	"StrataScriptRaycastHit's layout is part of the ABI");

/* A contact passed to the contact callbacks of StrataScriptClassDesc. Engine memory, valid during the call; read members
 * appended later only when StructSize covers them. Other is the entity on the other side (it may be destroyed already
 * when the contact ended because of that); Point is in world space (the last known one when a contact ends) and Normal
 * points from the script's entity towards the other. */
typedef struct StrataScriptCollision
{
	uint32_t StructSize; /* sizeof(StrataScriptCollision) as built into the engine */
	uint32_t Padding;
	StrataScriptEntityID Other;
	float Point[3];
	float Normal[3];
} StrataScriptCollision;

ST_SCRIPT_DETAIL_STATIC_ASSERT(sizeof(StrataScriptCollision) == 40 && offsetof(StrataScriptCollision, StructSize) == 0
	&& offsetof(StrataScriptCollision, Other) == 8 && offsetof(StrataScriptCollision, Point) == 16
	&& offsetof(StrataScriptCollision, Normal) == 28, "StrataScriptCollision's layout is part of the ABI");
```

1. **Lines 159–162:** the comment states the reason: arrays of hits are filled by the engine without a size.
2. **Lines 172–175:** the layout assertions fix size 40 and every offset, so a change fails the build on every compiler.
3. **Line 183:** the collision begins with `StructSize`, set by the engine to its own size, so a script reads a later member only when that size covers it.

The two structs have the same size today and differ in what may happen next. The next version of the engine may append to the collision, and old modules read only the members their SDK knows. It may never append to the hit.

### A struct the engine fills up to the module's capacity

The third kind reverses the direction: the module owns the memory and the engine writes into it.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L277-L295"
/*
 * A graphics option (GraphicsDescribeOption). The module sets StructSize to the size of the struct it passes; the engine
 * fills at most that many bytes, at most its own struct's, and sets StructSize to the bytes it filled: read a member
 * only when ST_SCRIPT_HAS_MEMBER covers it, so modules of a newer SDK (members appended) work with older engines and the
 * other way round. The engine refuses a StructSize smaller than this first version's. The strings are engine memory,
 * valid until the engine call into the module that asked returns: copy them.
 */
typedef struct StrataScriptGraphicsOptionInfo
{
	uint32_t StructSize;
	uint32_t Type;                  /* StrataScriptGraphicsOptionType */
	StrataScriptString Name;        /* What GraphicsGetOption and GraphicsSetOption take ("ShadowResolution") */
	StrataScriptString Title;       /* For menus ("Shadow resolution") */
	StrataScriptString Description; /* What it changes and what it costs */
	double Min;                     /* Int and Float: the inclusive range; 0 for the others */
	double Max;
	uint32_t ChoiceCount;           /* Choice: how many choices; 0 for the others */
	uint32_t Source;                /* StrataScriptGraphicsOptionSource of the value in effect when it was described */
} StrataScriptGraphicsOptionInfo;
```

1. **Lines 278–280:** the module sets `StructSize` to the size it built; the engine writes at most that many bytes, and at most its own struct.
2. **Lines 280–283:** a member is read only when `ST_SCRIPT_HAS_MEMBER` covers it, and the engine refuses a size below the first version's.

A module of a newer SDK works with an older engine, and the other way round, because each side writes or reads only the part both know. The same pattern returns in the module description below.

### The head of the host table

All the engine's services reach the module through one struct of function pointers. At the pin it holds 165 of them after its two header members.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L304-L320"
/*
 * Engine services for scripts. Unless noted otherwise, functions taking a context only work while the engine is
 * calling into the module for that context, on the engine's main thread; otherwise they fail (returning false, 0
 * or an empty result). Failures are logged by the engine.
 *
 * Functions returning text or arrays copy into a caller-provided buffer: they write at most `capacity` elements and
 * return the total number available, so the caller can retry with a larger buffer. Text is not null-terminated.
 */
typedef struct StrataScriptHostAPI
{
	uint32_t StructSize; /* sizeof(StrataScriptHostAPI) as built into the engine */
	uint32_t ABIVersion;

	/* Diagnostics (callable from any thread). */
	void (*Log)(uint32_t level, StrataScriptString message);
	/* Explains the next StrataScriptResult_Exception returned to the engine. */
	void (*ReportException)(StrataScriptString message);
```

1. **Lines 309–311:** the buffer protocol in one comment: write at most `capacity` and return the total available.
2. **Lines 314–315:** the table also begins with a `StructSize` and carries the ABI version.

The table is the module's only way to reach the engine: `Log` and `ReportException` first, then time, entities, components, physics, input, audio and so on. Each function that works on a scene takes the context as its first argument, and fails with a logged message (and a zero or false result) when called outside an engine call. The engine side of each function is the subject of [the host API](../scripting/host-api.md).

### The three descriptors

A module describes itself to the engine in three structs, each nested in the next: the module description lists class descriptors, and a class descriptor lists field descriptors. The first quote shows the field and class descriptors.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L758-L790"
typedef struct StrataScriptFieldDesc
{
	uint32_t StructSize;
	uint32_t Type; /* StrataScriptValueType */
	StrataScriptString Name;
	StrataScriptValue DefaultValue;
} StrataScriptFieldDesc;

/*
 * A script class. Lifetime of an instance: Create, SetField for every serialized override, OnCreate, then the
 * update callbacks every frame, OnDestroy, Destroy. Callbacks the class does not implement are null.
 * On hot reload the engine destroys instances without OnDestroy and recreates them in the new module without
 * OnCreate: fields are restored, then OnReload is called.
 */
typedef struct StrataScriptClassDesc
{
	uint32_t StructSize;
	uint32_t FieldCount;
	StrataScriptString Name;                     /* Unique within the module */
	const StrataScriptFieldDesc* const* Fields;  /* FieldCount pointers */

	uint32_t (*Create)(StrataScriptContext* context, StrataScriptEntityID entity, StrataScriptInstance* outInstance);
	uint32_t (*Destroy)(StrataScriptInstance instance);
	/* String values returned by GetField stay valid until the next call into the module. */
	uint32_t (*GetField)(StrataScriptInstance instance, uint32_t fieldIndex, StrataScriptValue* outValue);
	uint32_t (*SetField)(StrataScriptInstance instance, uint32_t fieldIndex, const StrataScriptValue* value);

	uint32_t (*OnCreate)(StrataScriptInstance instance);
	uint32_t (*OnUpdate)(StrataScriptInstance instance, float deltaTime);
	uint32_t (*OnFixedUpdate)(StrataScriptInstance instance, float fixedDeltaTime);
	uint32_t (*OnLateUpdate)(StrataScriptInstance instance, float deltaTime);
	uint32_t (*OnDestroy)(StrataScriptInstance instance);
	uint32_t (*OnReload)(StrataScriptInstance instance);
```

1. **Lines 766–771:** the comment gives a class instance's life: created, given its saved fields, `OnCreate`, updates, `OnDestroy`, destroyed; a callback the class does not write is null.
2. **Lines 774–777:** a class descriptor starts with its `StructSize`, then its name and an array of field descriptors.
3. **Lines 779–783:** four functions are always present: creation, destruction and the two field accessors. Callbacks follow.

A **class descriptor** is this struct: the table that tells the engine a class's name, its fields and the C functions that create it, read and write its fields and run its callbacks. It has 15 callback slots in all (`OnCreate` to `OnUISubmit`); the order and the way the engine calls them belong to [the script system](../scripting/script-system.md). A callback appended after the first version sits after `OnReload`, so the engine reads it only if `StructSize` covers it.

The module description is the outermost struct, and the engine's own `StructSize` bounds how much of it the module may write.

```cpp src="StrataScriptCore/Include/StrataScript/ScriptABI.h#L833-L851"
/*
 * Filled by StrataScript_Load. The host sets StructSize to the size of its StrataScriptModuleAPI (the capacity of the
 * struct it passes) and zeroes the rest. The module writes at most that many bytes and sets StructSize to the size of
 * the struct it was built with, so a module built against a newer SDK (same ABI version, members appended) never
 * writes past the host's struct; either side reads a member only if both sizes cover it. A module refuses a capacity
 * that cannot hold the members of its ABI version (StrataScriptResult_ABIMismatch). The pointed-to data stays valid
 * until Unload is called.
 */
typedef struct StrataScriptModuleAPI
{
	uint32_t StructSize;
	uint32_t ABIVersion;
	StrataScriptString Name;
	uint32_t ClassCount;
	uint32_t Padding;
	const StrataScriptClassDesc* const* Classes; /* ClassCount pointers */
	/* Called once before the engine unloads the module, after every instance was destroyed. */
	uint32_t (*Unload)(void);
} StrataScriptModuleAPI;
```

1. **Lines 833–840:** the host sets `StructSize` to its capacity; the module writes at most that and then reports its own size.
2. **Lines 849–850:** `Unload` is the last member: the engine calls it once, after every instance was destroyed.

The **module description** is this struct: a module's name, its class descriptors and its unload function. Loading it and checking what it says is the work of [loading](../scripting/loading.md).

### The SDK: the current context

From here the code is C++, in the SDK. The first question it answers is how a script finds the host and the scene it runs in, without passing them through every call. `Host.h` keeps the host table pointer and the current context in two global variables.

```cpp src="StrataScriptCore/Include/StrataScript/Host.h#L36-L55"
// Makes `context` current for the duration of an engine call (calls can nest).
class ContextScope
{
public:
	explicit ContextScope(StrataScriptContext* context)
		: m_Previous(s_Context)
	{
		s_Context = context;
	}

	~ContextScope()
	{
		s_Context = m_Previous;
	}

	ContextScope(const ContextScope&) = delete;
	ContextScope& operator=(const ContextScope&) = delete;
private:
	StrataScriptContext* m_Previous;
};
```

1. **Lines 40–44:** the :term[constructor]{id=constructor} makes the context current and remembers the previous one, because engine calls can nest.
2. **Lines 46–49:** the :term[destructor]{id=destructor} restores it, whatever way the call ends, so a context never leaks out of a call.

A class of the SDK such as `Scene` (`Scene::FindEntityByName`) reads the host and the context from these variables, so game code never mentions them. The second helper is the read side of the buffer protocol.

```cpp src="StrataScriptCore/Include/StrataScript/Host.h#L69-L85"
// Reads text from a host function following the buffer protocol: read(buffer, capacity) copies at most capacity
// bytes and returns the full size.
template<typename ReadFunction>
std::string ReadHostString(ReadFunction&& read)
{
	char stackBuffer[256];
	const uint64_t size = read(stackBuffer, static_cast<uint64_t>(sizeof(stackBuffer)));
	if (size <= sizeof(stackBuffer))
		return std::string(stackBuffer, static_cast<size_t>(size));

	// The text can only change between the two calls if the engine state changed in between, which it cannot
	// (calls are single-threaded); the size check keeps this safe regardless.
	std::string result(static_cast<size_t>(size), '\0');
	const uint64_t secondSize = read(result.data(), static_cast<uint64_t>(result.size()));
	result.resize(static_cast<size_t>(secondSize < size ? secondSize : size));
	return result;
}
```

1. **Lines 74–77:** the first call uses a 256-byte buffer on the stack, and most strings fit; no allocation happens.
2. **Lines 81–83:** when the text was longer, the second call asks again with a buffer of the exact size, and the shorter of the two sizes wins.

A host function appended after the first release may be missing from an older engine. One macro lets the SDK ask before every use.

```cpp src="StrataScriptCore/Include/StrataScript/Host.h#L106-L111"
// The host API table if the engine provides the host function `Function`, else null. Functions appended to the table after
// the initial set of its ABI version are missing from older engines (see ScriptABI.h), so the SDK checks them before every
// use and degrades gracefully without them.
#define ST_SCRIPT_DETAIL_HOST_WITH(Function) \
	(::Strata::Detail::s_Host && ST_SCRIPT_HAS_MEMBER(StrataScriptHostAPI, ::Strata::Detail::s_Host, Function) && ::Strata::Detail::s_Host->Function \
		? ::Strata::Detail::s_Host : nullptr)
```

The macro gives the host table if the engine has that function and its pointer is non-null, and a :term[null pointer]{id=null-pointer} otherwise. The calling code tests the result and returns a neutral value when it is null, so a game built with a newer SDK still runs on an older engine, with the new feature missing.

### The Script base class

Every game class derives from `Script`. Check how it learns its entity without the game class passing anything.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L70-L108"
class Script
{
public:
	Script()
		: m_Entity(Detail::s_ConstructingEntity), m_Context(Detail::s_Context)
	{
	}

	virtual ~Script() = default;

	Script(const Script&) = delete;
	Script& operator=(const Script&) = delete;

	virtual void OnCreate() {}
	virtual void OnUpdate([[maybe_unused]] float deltaTime) {}
	virtual void OnFixedUpdate([[maybe_unused]] float fixedDeltaTime) {}
	virtual void OnLateUpdate([[maybe_unused]] float deltaTime) {}
	virtual void OnDestroy() {}
	virtual void OnReload() {}
	virtual void OnCollisionEnter([[maybe_unused]] const Collision& collision) {}
	virtual void OnCollisionExit([[maybe_unused]] const Collision& collision) {}
	virtual void OnTriggerEnter([[maybe_unused]] const Collision& collision) {}
	virtual void OnTriggerExit([[maybe_unused]] const Collision& collision) {}
	virtual void OnAnimationEvent([[maybe_unused]] std::string_view name) {}
	virtual void OnUIClick([[maybe_unused]] Entity widget) {}
	virtual void OnUIValueChanged([[maybe_unused]] Entity widget, [[maybe_unused]] float value) {}
	virtual void OnUIFocusChanged([[maybe_unused]] Entity widget, [[maybe_unused]] bool focused) {}
	virtual void OnUISubmit([[maybe_unused]] Entity widget) {}

	// The entity this script is attached to.
	Entity GetEntity() const { return m_Entity; }
	TransformComponent GetTransform() const { return m_Entity.GetTransform(); }
private:
	Entity m_Entity;
	StrataScriptContext* m_Context = nullptr;
	const Detail::ClassRecord* m_Class = nullptr;

	friend struct Detail::ScriptAccess;
};
```

1. **Lines 73–76:** the constructor reads two globals that the engine's creation call set a moment before, so the entity and the context bind before the game class's own constructor runs.
2. **Lines 83–97:** every callback is a :term[virtual function]{id=virtual-function} with an empty body; a game class overrides the ones it needs.
3. **Line 105:** the class record's address is set after construction and lets the thunks find the field list.

Because the constructor only copies two numbers, a class can be built outside an engine call too. The module does exactly that once at load, to read defaults (below).

### Catching every exception

Every call from the engine passes through one function. It makes the context current, runs the call and turns an exception into a result.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L184-L203"
// Runs script code with `context` current, turning C++ exceptions into StrataScriptResult_Exception.
template<typename Function>
uint32_t InvokeScript(StrataScriptContext* context, Function&& function)
{
	ContextScope scope(context);
	try
	{
		function();
		return StrataScriptResult_Ok;
	}
	catch (const std::exception& exception)
	{
		ReportException(exception.what());
	}
	catch (...)
	{
		ReportException("Unknown exception (not derived from std::exception)");
	}
	return StrataScriptResult_Exception;
}
```

1. **Line 188:** the scope makes the context current for the whole call.
2. **Lines 194–200:** both kinds of exception are caught: those derived from `std::exception`, with their message, and anything else with a fixed message.
3. **Lines 196–200:** the message goes to the host through `ReportException` before the function returns the result `StrataScriptResult_Exception`.

A **thunk** is a small plain function that the engine can call through a C pointer, and that finds the C++ object and calls its :term[member function]{id=member-function}. There is one per callback, all of the same shape.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L246-L250"
inline uint32_t OnUpdateThunk(StrataScriptInstance instance, float deltaTime)
{
	Script* script = ToScript(instance);
	return InvokeScript(ScriptAccess::GetInstanceContext(*script), [&]() { script->OnUpdate(deltaTime); });
}
```

The pointer passed as an instance is the `Script*` the module made; the thunk casts it back and calls the virtual function inside `InvokeScript`. The function is the exception barrier for the engine's sake. The containment of `abort()` is the subject of [crash containment](../scripting/crash-containment.md).

### Finding the overrides at compile time

The engine skips every callback whose slot is null, so a class that writes no `OnFixedUpdate` pays nothing for it. The SDK must therefore know which callbacks the class overrides, without asking the programmer to list them.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L371-L378"
template<typename T>
constexpr bool OverridesOnCreate()
{
	if constexpr (requires { &T::OnCreate; })
		return !std::is_same_v<decltype(&T::OnCreate), void (Script::*)()>;
	else
		return true;
}
```

The expression `&T::OnCreate` is a :term[pointer to a member]{id=pointer-to-a-member}: it names a member function of a class without an object, and its type records the class that declared the function. The trick is in that type: `&T::OnCreate` has the type `void (Script::*)()` when `T` inherits the base version, and a different type when `T` or a base declares its own. The `requires` expression handles one more case: when the override is private or protected, naming it is invalid, and the class is counted as overriding. The function returns true when the member pointer type differs from the base's.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L506-L521"
template<typename T>
constexpr uint32_t GetCallbackFlags()
{
	uint32_t flags = 0;
	if constexpr (OverridesOnCreate<T>())
		flags |= CallbackFlag_OnCreate;
	if constexpr (OverridesOnUpdate<T>())
		flags |= CallbackFlag_OnUpdate;
	if constexpr (OverridesOnFixedUpdate<T>())
		flags |= CallbackFlag_OnFixedUpdate;
	if constexpr (OverridesOnLateUpdate<T>())
		flags |= CallbackFlag_OnLateUpdate;
	if constexpr (OverridesOnDestroy<T>())
		flags |= CallbackFlag_OnDestroy;
	if constexpr (OverridesOnReload<T>())
		flags |= CallbackFlag_OnReload;
```

1. **Lines 510–513:** each flag is set by `if constexpr`, so the work is done by the compiler and costs nothing at run time.
2. **Line 509:** the result is one word with a bit for each of the 15 callbacks. Bits 0 to 14 follow the order of `CallbackFlag_OnCreate` to `CallbackFlag_OnUISubmit`: `OnCreate`, `OnUpdate`, `OnFixedUpdate`, `OnLateUpdate`, `OnDestroy`, `OnReload`, `OnCollisionEnter`, `OnCollisionExit`, `OnTriggerEnter`, `OnTriggerExit`, `OnAnimationEvent`, `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged` and `OnUISubmit`.

### Registering a class before `main`

The module needs a list of its classes before anyone asks. The SDK builds it during :term[static initialization]{id=static-initialization}, the phase when a shared library loads and the objects at :term[namespace]{id=namespace} scope are constructed. Nothing may allocate then, so the list is a :term[linked list]{id=linked-list} whose links are members of the entries.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L545-L557"
struct ClassRegistration
{
	const char* Name = nullptr;
	uint32_t CallbackFlags = 0;
	void (*Describe)(ClassRecord& record) = nullptr;
	Script* (*Construct)() = nullptr;
	uint32_t (*Create)(StrataScriptContext* context, StrataScriptEntityID entity, StrataScriptInstance* outInstance) = nullptr;
	const ClassRecord** RecordSlot = nullptr;
	ClassRegistration* Next = nullptr;
};

inline ClassRegistration* s_FirstRegistration = nullptr;
inline ClassRegistration* s_LastRegistration = nullptr;
```

1. **Lines 547–552:** the registration holds only plain data and function pointers, one per thing the module needs to do with the class.
2. **Line 553:** `Next` is the link, so the list needs no memory but the entries.
3. **Lines 556–557:** the head and tail of the list, as two global pointers set to null before any constructor runs.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L589-L617"
class ClassRegistrar
{
public:
	ClassRegistrar(const char* name, void (*describe)(ScriptClassBuilder<T>&))
	{
		static_assert(std::is_base_of_v<Script, T>, "Script classes must derive from Strata::Script");
		static_assert(std::is_default_constructible_v<T>, "Script classes must be default constructible");

		ClassSlot<T>::Name = name;
		ClassSlot<T>::Describe = describe;
		m_Registration.Name = name;
		m_Registration.CallbackFlags = GetCallbackFlags<T>();
		m_Registration.Describe = &DescribeClass<T>;
		m_Registration.Construct = &ConstructDefault<T>;
		m_Registration.Create = &CreateThunk<T>;
		m_Registration.RecordSlot = &ClassSlot<T>::Record;

		if (s_LastRegistration)
			s_LastRegistration->Next = &m_Registration;
		else
			s_FirstRegistration = &m_Registration;
		s_LastRegistration = &m_Registration;
	}

	ClassRegistrar(const ClassRegistrar&) = delete;
	ClassRegistrar& operator=(const ClassRegistrar&) = delete;
private:
	ClassRegistration m_Registration;
};
```

1. **Lines 594–595:** two assertions turn a class that does not derive from `Script`, or that cannot be built without arguments, into :term[compile errors]{id=compile-error}.
2. **Line 600:** the callback flags are computed here, for this class, at :term[compile time]{id=compile-time}.
3. **Lines 606–610:** the new entry is appended at the tail, so classes appear in the order their static objects are constructed.

A game maker does not write a registration object. The macros do.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L852-L865"
#define ST_SCRIPT_CLASS(Type) ST_SCRIPT_DETAIL_CLASS(Type, __COUNTER__)

// Declares a public data member of the class as a field: shown in the editor, serialized with the scene and kept
// across hot reloads. Supported types: bool, int32_t, float, glm::vec2/3/4, glm::quat, std::string, Strata::Entity,
// Strata::AssetHandle.
#define ST_SCRIPT_FIELD(Member) \
	stScriptBuilder.template Field<&std::remove_reference_t<decltype(stScriptBuilder)>::ClassType::Member>(#Member)

// The registrar is not const: registering the next class links it into this one (ClassRegistration::Next).
#define ST_SCRIPT_DETAIL_CLASS(Type, Counter) ST_SCRIPT_DETAIL_CLASS_IMPL(Type, Counter)
#define ST_SCRIPT_DETAIL_CLASS_IMPL(Type, Counter) \
	static void StrataScriptDescribe##Counter(::Strata::ScriptClassBuilder<Type>& stScriptBuilder); \
	static ::Strata::Detail::ClassRegistrar<Type> s_StrataScriptRegistrar##Counter(#Type, &StrataScriptDescribe##Counter); \
	static void StrataScriptDescribe##Counter([[maybe_unused]] ::Strata::ScriptClassBuilder<Type>& stScriptBuilder)
```

1. **Line 852:** `__COUNTER__` gives each use of the macro in a file its own number, so two classes in one file get different names.
2. **Lines 863–864:** the macro declares the describing function, makes a static registration object named with the number and passes it the type's spelled name and the function.
3. **Line 865:** the body the game maker writes after the macro becomes the definition of that function.

### Building a class record

When the module loads, the SDK turns each registration into a record, and the record holds the C descriptor. The record's fields come from the body of the macro.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L640-L690"
inline std::unique_ptr<ClassRecord> BuildClassRecord(const ClassRegistration& registration)
{
	auto record = std::make_unique<ClassRecord>();
	record->Name = registration.Name;
	registration.Describe(*record);

	const std::unique_ptr<Script> defaults(registration.Construct());
	for (FieldBinding& field : record->Fields)
	{
		StrataScriptValue value = {};
		field.Get(*defaults, value);
		if (value.Type == StrataScriptValueType_String)
		{
			field.DefaultString = std::string(FromABIString(value.As.String));
			value.As.String = ToABIString(field.DefaultString);
		}
		field.Desc.StructSize = sizeof(StrataScriptFieldDesc);
		field.Desc.Type = field.Type;
		field.Desc.Name = ToABIString(field.Name);
		field.Desc.DefaultValue = value;
	}
	for (const FieldBinding& field : record->Fields)
		record->FieldDescs.push_back(&field.Desc);

	const uint32_t flags = registration.CallbackFlags;
	StrataScriptClassDesc& desc = record->Desc;
	desc.StructSize = sizeof(StrataScriptClassDesc);
	desc.FieldCount = static_cast<uint32_t>(record->Fields.size());
	desc.Name = ToABIString(record->Name);
	desc.Fields = record->FieldDescs.data();
	desc.Create = registration.Create;
	desc.Destroy = &DestroyThunk;
	desc.GetField = &GetFieldThunk;
	desc.SetField = &SetFieldThunk;
	desc.OnCreate = (flags & CallbackFlag_OnCreate) ? &OnCreateThunk : nullptr;
	desc.OnUpdate = (flags & CallbackFlag_OnUpdate) ? &OnUpdateThunk : nullptr;
	desc.OnFixedUpdate = (flags & CallbackFlag_OnFixedUpdate) ? &OnFixedUpdateThunk : nullptr;
	desc.OnLateUpdate = (flags & CallbackFlag_OnLateUpdate) ? &OnLateUpdateThunk : nullptr;
	desc.OnDestroy = (flags & CallbackFlag_OnDestroy) ? &OnDestroyThunk : nullptr;
	desc.OnReload = (flags & CallbackFlag_OnReload) ? &OnReloadThunk : nullptr;
	desc.OnCollisionEnter = (flags & CallbackFlag_OnCollisionEnter) ? &ContactThunk<&Script::OnCollisionEnter> : nullptr;
	desc.OnCollisionExit = (flags & CallbackFlag_OnCollisionExit) ? &ContactThunk<&Script::OnCollisionExit> : nullptr;
	desc.OnTriggerEnter = (flags & CallbackFlag_OnTriggerEnter) ? &ContactThunk<&Script::OnTriggerEnter> : nullptr;
	desc.OnTriggerExit = (flags & CallbackFlag_OnTriggerExit) ? &ContactThunk<&Script::OnTriggerExit> : nullptr;
	desc.OnAnimationEvent = (flags & CallbackFlag_OnAnimationEvent) ? &AnimationEventThunk : nullptr;
	desc.OnUIClick = (flags & CallbackFlag_OnUIClick) ? &UIClickThunk : nullptr;
	desc.OnUIValueChanged = (flags & CallbackFlag_OnUIValueChanged) ? &UIValueChangedThunk : nullptr;
	desc.OnUIFocusChanged = (flags & CallbackFlag_OnUIFocusChanged) ? &UIFocusChangedThunk : nullptr;
	desc.OnUISubmit = (flags & CallbackFlag_OnUISubmit) ? &UISubmitThunk : nullptr;
	return record;
}
```

1. **Lines 646–650:** the defaults are read from one instance made by the class's own default constructor, so a field's default is whatever its starting value says.
2. **Lines 651–655:** a string default is copied into storage the record owns, because the instance dies at the end of the function.
3. **Lines 674–688:** each callback slot receives its thunk only when the flag is set; the rest stay null, and the engine never calls them.

The rule that a constructor does nothing follows from this. One instance is built at load time, outside any scene, only to read what its members hold. A constructor that spawned an entity, read a file or counted something would do so once for the load, silently, and the count would be wrong from the first frame.

### Loading and writing the description

The last steps are the two exports. They share an implementation that checks the versions and hands over the description.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L693-L710"
inline bool CanReceiveModuleAPI(const StrataScriptModuleAPI* outModule)
{
	return outModule->StructSize >= offsetof(StrataScriptModuleAPI, Unload) + sizeof(outModule->Unload);
}

// Hands a module description (a StrataScriptModuleAPI, possibly with members of a newer SDK appended) to the engine.
// The engine's struct may be smaller (an engine built against an older SDK of the same ABI version): at most its
// size (StructSize on entry) is written, and StructSize then holds `descriptionSize`, the members the module knows.
// Writes nothing and returns false when the engine's struct cannot hold the members of this ABI version.
inline bool WriteModuleAPI(StrataScriptModuleAPI* outModule, const void* description, uint32_t descriptionSize)
{
	if (!CanReceiveModuleAPI(outModule) || descriptionSize < sizeof(StrataScriptModuleAPI))
		return false;
	const uint32_t capacity = outModule->StructSize;
	std::memcpy(outModule, description, capacity < descriptionSize ? capacity : descriptionSize);
	outModule->StructSize = descriptionSize;
	return true;
}
```

1. **Lines 693–696:** the module can only receive a struct that holds every member of its own version.
2. **Lines 706–708:** it copies the smaller of the two sizes, then reports the size it was built with.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L713-L748"
inline uint32_t LoadModule(const StrataScriptHostAPI* host, uint32_t hostABIVersion, StrataScriptModuleAPI* outModule, const char* moduleName)
{
	if (!host || !outModule)
		return StrataScriptResult_InvalidArgument;
	// Every function of this ABI version must be present (later additions are checked where they are used), and the
	// engine's module description must have room for every member of this ABI version.
	if (hostABIVersion != ST_SCRIPT_ABI_VERSION || host->ABIVersion != ST_SCRIPT_ABI_VERSION
		|| !ST_SCRIPT_HAS_MEMBER(StrataScriptHostAPI, host, GetScrollDelta) || !CanReceiveModuleAPI(outModule))
		return StrataScriptResult_ABIMismatch;

	if (s_Module)
		UnloadModule();
	s_Host = host;

	try
	{
		auto state = std::make_unique<ModuleState>();
		state->Name = moduleName ? moduleName : "";
		for (ClassRegistration* registration = s_FirstRegistration; registration; registration = registration->Next)
		{
			std::unique_ptr<ClassRecord> record = BuildClassRecord(*registration);
			*registration->RecordSlot = record.get();
			state->ClassDescs.push_back(&record->Desc);
			state->Classes.push_back(std::move(record));
		}

		StrataScriptModuleAPI description = {};
		description.StructSize = sizeof(StrataScriptModuleAPI);
		description.ABIVersion = ST_SCRIPT_ABI_VERSION;
		description.Name = ToABIString(state->Name);
		description.ClassCount = static_cast<uint32_t>(state->ClassDescs.size());
		description.Classes = state->ClassDescs.data();
		description.Unload = &UnloadModule;
		s_Module = state.release();
		WriteModuleAPI(outModule, &description, sizeof(description)); // The capacity was checked above
		return StrataScriptResult_Ok;
```

1. **Lines 719–721:** the load is refused unless both :term[ABI]{id=abi} numbers match and the host table holds `GetScrollDelta`, the last function of the first set; later functions are checked where they are used.
2. **Lines 731–737:** one record is built per registered class, in list order.
3. **Lines 747–748:** the description is written at most to the engine's capacity, and the function reports success.

The rest of `LoadModule` catches exceptions and clears what it built when something fails, so a failed load leaves no half-made state. The exports themselves are two small functions in the entry file, compiled into every module so that game code never defines them.

```cpp src="StrataScriptCore/Source/ScriptModuleEntry.cpp#L73-L81"
ST_SCRIPT_EXTERN_C ST_SCRIPT_EXPORT uint32_t StrataScript_GetABIVersion(void)
{
	return ST_SCRIPT_ABI_VERSION;
}

ST_SCRIPT_EXTERN_C ST_SCRIPT_EXPORT uint32_t StrataScript_Load(const StrataScriptHostAPI* host, uint32_t hostABIVersion, StrataScriptModuleAPI* outModule)
{
	return Strata::Detail::LoadModule(host, hostABIVersion, outModule, ST_SCRIPT_MODULE_NAME);
}
```

The file also installs the handling of `abort()` on Windows, which [crash containment](../scripting/crash-containment.md) explains.

### Fields and their types

`ST_SCRIPT_FIELD(SpinSpeed)` expands to a call of `ScriptClassBuilder<T>::Field<&T::SpinSpeed>("SpinSpeed")`. The :term[template argument]{id=template-argument} is a pointer to a member, as in the override check above. `Field` checks with `static_assert` that the member belongs to the class and that its type is one of ten: `bool`, `int32_t`, `float`, the vector types `glm::vec2`, `glm::vec3` and `glm::vec4`, `glm::quat`, `std::string`, `Entity` and `AssetHandle`.

For each field the SDK stores two function pointers, made from templates over the member pointer. One reads the member into a tagged value. The other writes a value into the member and returns false when the tag is wrong. The conversions live in the `ValueTraits` structs of `Value.h`; an integer travels as 64 bits and the conversion fails when it does not fit the member. Because each field uses a member pointer, a rename of the member in the class renames the registered name as well, and a wrong name is a compile error.

### What does not cross

The helpers `Random`, `Timer`, `KeyRepeat` and `Motion` are ordinary classes of `Gameplay.h` that run inside the module; only `KeyRepeat` calls the host, to read keys through `Input`. `Random` gives the same sequence for every compiler and SDK version, so a game can replay a match; their homes are [recipes](../make/recipes.md), [timers and events](../make/timers-events.md) and [gameplay math](../make/gameplay-math.md).

Two of them share a name with an engine class: `Strata::Random` and `Strata::Timer` exist in the engine too, with different definitions. A program that holds two different definitions of one class name violates the **one-definition rule** (ODR), which says that a name with external linkage has one definition in the whole program. The compiler does not have to warn, and the :term[linker]{id=linker} may silently pick the wrong one. The SDK's C++ headers therefore never meet engine code, and a test keeps them apart (see below).

:::example[The Coin from the `ThirdPerson` sample]
The sample's coin spins and bobs, and its registration is five lines.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L54-L58"
ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(SpinSpeed);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(Collected);
```

The macro is the first use in its file; if `__COUNTER__` yields 0, it declares `StrataScriptDescribe0` and a static registration object named `s_StrataScriptRegistrar0`, constructed with the name `"Coin"`. The three field lines become three `Field` calls, so the record has three bindings: `SpinSpeed` (float 180), `BobHeight` (float 0.12) and `Collected` (a flag, false). Those defaults come from the starting values of the members, read from one instance. The private members `m_Visual`, `m_Time` and the rest are not fields and never cross.

The class overrides `OnCreate` (bit 0, value 1), `OnUpdate` (bit 1, value 2), `OnReload` (bit 5, value 32) and `OnTriggerEnter` (bit 8, value 256). The flags are 1 + 2 + 32 + 256 = 291. In the class descriptor four of the 15 callback slots hold thunks and 11 are null, so the engine never calls `OnFixedUpdate` for a coin.

On a 64-bit build the class descriptor is 184 bytes: 32 for the header members, the name and the field array, then 19 pointers of 8 bytes, that is 152. If the module was built with an SDK from before `OnUISubmit`, its descriptor's `StructSize` is 176, and the engine's check `176 >= 176 + 8` is false, so the engine does not read that slot.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| C++ classes shared across the boundary | Engines whose game code is built with the engine | No thunks, no tables and richer types in calls | Binary compatibility between builds, and any containment of an exception or a crash |
| An embedded language such as C# | Unity, Godot and many other engines | A protected space, quick reload and safe errors | One language for engine and game; speed; binding code for every function |
| Scripts in another process | Tools that isolate untrusted code | Total isolation from a crash | A copy and a wait for each call; hundreds of calls per frame cost too much |
| Generated glue from a description file | Godot's native extension interface describes its C functions in a file for generators | No hand-written glue for each host function | A generator in the build; one more format to keep in step |

## How it is tested

Three groups of tests guard the boundary.

- `Scripting.API` loads the API test module and runs scripts that check every host function the SDK wraps. The scripts count their checks (30 for the entity script) and the test requires all of them. The feature test exercises the same functions in a game.
- `Scripting.Module` loads test modules. One case builds a module that writes a larger description, the `NewerSDK` module, and checks that it loads and that the guard bytes after the engine's struct stay intact. Another refuses modules of another ABI version and damaged class tables, and a third checks that the engine reads callbacks only from descriptors large enough to hold them.
- `Architecture.ScriptSDK` scans the sources of the engine, the editor, the :term[runtime]{id=runtime}, the command-line client and the tests, and fails on any include of a header of `StrataScript/` other than `ScriptABI.h`. Lines inside a raw string do not count. The test also checks its own scanner on sample lines.

The layout assertions are compile-time tests: a change to a frozen struct fails the build on all three compilers. Run the first two with `build/windows/bin/Debug/StrataTests.exe --test-suite=Scripting*`, and the third with `--test-suite=Architecture.ScriptSDK`.

## Changing it safely

Most changes are one of three kinds.

A new host function goes last in the struct `StrataScriptHostAPI` and last in the engine's list `ST_SCRIPT_HOST_FUNCTIONS`. A compile-time check in `ScriptHostAPI.cpp` fails when the list and the struct differ in order or size. The SDK reaches it through `ST_SCRIPT_DETAIL_HOST_WITH`. Tests then call it from three places: the module of the API test, a `Scripting.*` test and the feature scripts. The ABI version stays at 1.

A new callback goes at the end of `StrataScriptClassDesc`, with a flag, an override check, a thunk and a line in `BuildClassRecord`; the engine reads it only when `StructSize` covers it. A changed signature, a changed layout or a removed member is incompatible, and the number must change.

A new SDK helper that is named like an engine class stays inside a module. Test it in a script module, never in the engine's tests, or `Architecture.ScriptSDK` fails.

:::rule[SDK helpers named like engine classes are tested only inside a module]
The engine's rule keeps `Random` and `Timer` of the SDK away from the engine's classes of the same name. Including the SDK would give one program two definitions of one name, which is :term[undefined behavior]{id=undefined-behavior} under the one-definition rule.
:::

:::caution[One `ST_SCRIPT_CLASS` per class, in a source file]
A header included by two source files would register the class twice, and the engine refuses a module that lists one class name twice.
:::

## Summary

- A C header, `ScriptABI.h`, holds the whole contract: two exports, plain structs, a table of 165 host functions and three nested descriptors; the SDK builds classes from it.
- Frozen structs carry no size and never change; size-prefixed structs start with `StructSize`, and each side reads a member only when the size covers it.
- The SDK binds the entity in the `Script` constructor, wraps every call in `InvokeScript` and has one thunk per callback.
- Callback overrides are found at compile time from member pointer types, so the engine never calls a slot the class did not fill.
- `ST_SCRIPT_CLASS` registers a class during static initialization in a linked list, and `BuildClassRecord` reads defaults from one default-constructed instance, so a constructor does nothing.

## Check yourself

1. The engine's `StrataScriptClassDesc` is 184 bytes, and `OnUISubmit` begins at offset 176 and takes 8 bytes. A module built with an older SDK passes a descriptor with `StructSize` 176. May the engine read `OnUISubmit`?

   :::answer{tests="has-member"}
   No. The check needs `StructSize >= 176 + 8 = 184`, and 176 is smaller, so the module's descriptor ends before the member. The engine treats the callback as not implemented.
   :::

2. Why may the engine add a member to `StrataScriptCollision` but never to `StrataScriptRaycastHit`? (a) Collisions are rarer. (b) The collision starts with `StructSize` and is read in engine memory; hits have no size and sit in arrays the module owns. (c) Hits are larger.

   :::answer{tests="read-structs"}
   Option (b) is right. A reader of a collision checks `StructSize`, so an older module ignores a new member. An array of hits has fixed elements, and a longer element would write past the end of an older module's buffer. Option (a) and option (c) say nothing about layout.
   :::

3. A class overrides `OnDestroy` and `OnCollisionExit` only. Which bits are set in its callback flags, and what are the values?

   :::answer{tests="override-detection"}
   `OnDestroy` is bit 4 (16) and `OnCollisionExit` is bit 7 (128), so the flags are 144. Every other slot of the class descriptor is null, and the engine never calls it.
   :::

4. Where does a `Script` learn its entity, and why does a game class not receive it as a constructor argument?

   :::answer{tests="trace-class"}
   The base class constructor reads `s_ConstructingEntity`, which `CreateThunk` sets immediately before `new T()`. The macros require a default constructor, because the module also builds one instance at load to read defaults; no entity exists then.
   :::

5. A constructor logs "spawned" and creates an entity. What goes wrong at load time, and what goes wrong when two source files register the class?

   :::answer{tests="constructor-rule"}
   At load, `BuildClassRecord` builds one instance outside any scene, so the constructor runs once for no entity and the entity call fails or is wrong. With two registrations of one class, `ReadModuleDescription` finds a class name twice and refuses the module.
   :::

## Exercises

1. **Basic.** The engine's `StrataScriptModuleAPI` is 48 bytes. The `NewerSDK` test module describes itself with 112 bytes. How many bytes does it write, what `StructSize` does the engine read back, and what happens if the engine's struct were 40 bytes?

   :::answer[Worked solution]{tests="has-member"}
   The module copies the smaller of 48 and 112, so 48 bytes, and sets `StructSize` to 112. The engine reads only the members its struct holds. With 40 bytes the engine's struct ends at `Classes`, before `Unload`; `CanReceiveModuleAPI` is false, nothing is written and the module returns `StrataScriptResult_ABIMismatch`.
   :::

2. **Medium.** Add a `Cooldown` helper of the kind `Gameplay.h` holds, so that a script can ask whether half a second passed since a shot. Write it as plain C++ and show how you test it.

   :::answer[Worked solution]{tests="constructor-rule" solution="sketches/scripting-abi-sdk-cooldown.cpp"}
   The class below holds a duration and the time left, and it has a default constructor, as a field-free helper should. It calls no host function, so it runs wherever the module does; in the engine's own tests it may not be included, so the test belongs in a script module.

   ```cpp sketch="scripting-abi-sdk-cooldown.cpp"
   // A Cooldown helper of the kind a script module can carry: plain C++ with no engine types, default constructible.
   #include <cstdio>

   class Cooldown
   {
   public:
   	explicit Cooldown(float duration = 1.0f)
   		: m_Duration(duration)
   	{
   	}

   	void Start() { m_Remaining = m_Duration; }

   	void Tick(float deltaTime)
   	{
   		m_Remaining -= deltaTime;
   		if (m_Remaining < 0.0f)
   			m_Remaining = 0.0f;
   	}

   	bool IsReady() const { return m_Remaining <= 0.0f; }
   	float GetRemaining() const { return m_Remaining; }
   private:
   	float m_Duration;
   	float m_Remaining = 0.0f;
   };

   int main()
   {
   	Cooldown shot(0.5f);
   	std::printf("ready before the first shot: %s\n", shot.IsReady() ? "yes" : "no");
   	shot.Start();
   	for (int frame = 1; frame <= 3; frame++)
   	{
   		shot.Tick(0.2f);
   		std::printf("after %.1f s: %.2f s left, ready %s\n", 0.2f * static_cast<float>(frame), shot.GetRemaining(), shot.IsReady() ? "yes" : "no");
   	}
   	return 0;
   }
   ```

   ```text output-of="scripting-abi-sdk-cooldown.cpp"
   ready before the first shot: yes
   after 0.2 s: 0.30 s left, ready no
   after 0.4 s: 0.10 s left, ready no
   after 0.6 s: 0.00 s left, ready yes
   ```

   1. **Line 7:** the default argument gives the class a default constructor, so it can be made without arguments.
   2. **Lines 14–19:** `Tick` subtracts the frame's time and stops at zero, so the time left is never negative.
   3. **Line 21:** the cooldown is ready when no time is left.

   The numbers show the clamp: 0.5 s minus 0.2 s three times is below zero, so the time left stops at 0.00 and the cooldown is ready.
   :::

3. **Hard.** Trace it yourself: follow `ST_SCRIPT_CLASS(Coin)` from `Samples/ThirdPerson/Scripts/Coin.cpp` to the descriptor the engine reads.

   :::answer[Worked solution]{tests="trace-class"}
   Search for `ST_SCRIPT_CLASS` in `StrataScriptCore/Include/StrataScript/Script.h`: it expands to the registration object, whose constructor in `ClassRegistrar` appends a `ClassRegistration` to `s_FirstRegistration`. Put a breakpoint in `BuildClassRecord` and start the engine with a `ThirdPerson` copy: `LoadModule` calls it once per registration, and the debugger shows the flags 291 for `Coin`. `WriteModuleAPI` copies the description into the engine's struct, and `ScriptModule::ReadModuleDescription` in `Strata/src/Strata/Scripting/ScriptModule.cpp` reads the class descriptors and copies the callback functions.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the contract, `StrataScriptHostAPI`, `StrataScriptClassDesc`, `StrataScriptModuleAPI`.
- `StrataScriptCore/Include/StrataScript/Host.h`, `Value.h`, `Script.h` and `StrataScript.h`: the SDK; `StrataScriptCore/Source/ScriptModuleEntry.cpp`: the exports.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: the macro `ST_SCRIPT_HOST_FUNCTIONS`; `ScriptModule.cpp`: `ScriptModule::ReadModuleDescription`.
- `StrataTests/src/Scripting/ScriptAPITests.cpp` and `ScriptModuleTests.cpp`: the suites `Scripting.API` and `Scripting.Module`; `StrataTests/Scripts/NewerSDK/NewerSDKModule.cpp`: the newer module.
- `StrataTests/src/Architecture/ScriptSDKTests.cpp`: the suite `Architecture.ScriptSDK`.

## Further reading

- Ulrich Drepper, "How to Write Shared Libraries": symbols, versions and what a library may change; advanced.
- The C++ standard's rules for the one-definition rule, summarized on cppreference.com: what counts as two definitions of one name; intermediate.
- The Godot documentation of GDExtension: a native interface built the same way, a C header with function tables; intermediate.
- Andrei Alexandrescu, "Modern C++ Design": templates that choose code at compile time; advanced.

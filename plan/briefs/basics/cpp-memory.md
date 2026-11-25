# Brief: `basics/cpp-memory`

| Field | Value |
| --- | --- |
| Title | C++ memory: pointers, references, lifetimes, RAII and smart pointers |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/programming-3`, `basics/computer` |
| From | new by split of `basics/cpp`; foundation "C++ for engine code: ownership, errors and logging" (the language half); the "Reader must know first" columns of foundation, scene-ecs and assets; the stack and the heap in code, allocators; `Scope` and `Ref`; undefined behavior |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/cpp-memory` — C++ memory: pointers, references, lifetimes, RAII and smart pointers

**Covers.** The page extends `basics/programming-3`, which used pointers and references only as far as a script calls
them, and puts the stack and the heap of `basics/computer` into code. Pointers in depth: `&` takes an address, `*`
reaches what a pointer points to (dereference), `->` on a member, a pointer drawn as an arrow into the row of memory.
References against pointers: a reference cannot be null or point elsewhere later; `const` references in parameters as
the way to pass large values. Three kinds of lifetime: automatic (local variables on the stack, gone at the closing
brace), static (globals, and `static` locals built the first time they are reached and kept to the end), and dynamic
(the heap, `new` and `delete`). What goes wrong: a memory leak, a dangling pointer, a double delete, a use after free.
Undefined behavior: a rule of C++ that nothing checks, after which the program may seem to work, crash or do anything,
with signed overflow and reading past an array's end as further cases. Destructors, which run by themselves at the end
of a lifetime, in the reverse order of construction; RAII, a resource tied to an object (a file, a lock, memory).
Ownership: one owner destroys; `std::unique_ptr` and `std::make_unique`; a factory that returns a unique pointer;
unique pointers cannot be copied, only moved (the mechanism of moving is `basics/cpp-modern`'s), so types that hold one
can only move. Shared ownership: `std::shared_ptr` and `std::make_shared`, the reference count and `use_count`, shared
state between parts of a program, and the cost (a count changed with atomic operations, a block beside the object).
Weak references: `std::weak_ptr`, `lock` and `expired`, and cycles of shared pointers that never die. Strata's names for
the three: `Scope`, `Ref` and `WeakRef` with `CreateScope` and `CreateRef`, shown from `Base.h` (Strata's rules for
them are `core/conventions`'). Raw pointers as borrowed: who deletes what, and never deleting what one does not own.
The cost of heap allocation, and why engines allocate early or later instead of every frame (heap allocation and why it
can wait); allocators: an arena that hands out memory in a row, a pool of equal slots, a free list. The Practice runs in
the playground's script, from easy to hard: the order of destructors predicted, then run; the compile error of copying
a unique pointer; a shared pointer's count and a weak pointer that expires; a small arena; it ends with the optional
Coin Run item: a HUD script keeps the `Coin*` that `GetScript` returned across frames; the coin is collected and
destroyed at the end of the frame, or hot reload makes the script again, and the kept pointer dangles; the fix is to
ask again each frame.

**Leaves out.**

- Move semantics and `std::move` → `basics/cpp-modern`
- Strata's rules for `Scope`, `Ref` and borrowed pointers → `core/conventions`
- The range allocator of the geometry pool → `gpu/geometry-pool`
- Locks as objects, and atomic counters → `basics/threads`
- Virtual destructors → `basics/cpp-classes`
- Holding asset handles instead of `Ref`s across frames → `assets/residency`
- GPU resources released later → `gpu/resources-lifetimes`

**Fit.** `fits`: about 5,850 words against L (5,000). Twelve ideas, each with a sketch and its output or its crash,
the pictures of pointers into memory and the quote of `Base.h` (about 4,550), and the common mistakes, the Practice's
four exercises, the Coin Run item and the fixed parts (about 1,300); ownership with the three smart pointers takes the
most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:119` | concept | home | Pointers in depth, extending the use level of `basics/programming-3` (`*` in a type, `nullptr`, `->`): `&`, `*`, `->`, a pointer drawn into memory. General knowledge. |
| `new:120` | concept | home | References against pointers; `const` references in parameters. General knowledge. |
| `new:121` | concept | home | Lifetimes: automatic, static (globals and `static` locals) and dynamic (`new`, `delete`). General knowledge. |
| `new:122` | concept | home | Memory leaks, dangling pointers, double deletes, use after free. General knowledge. |
| `new:123` | concept | home | Undefined behavior, with signed overflow and reading past an array's end. General knowledge. |
| `new:124` | concept | home | Destructors and their order; RAII. General knowledge. |
| `new:125` | concept | home | Ownership with `std::unique_ptr` and `std::make_unique`; factories; types that can only move. General knowledge. |
| `new:126` | concept | home | Shared ownership: `std::shared_ptr`, the reference count, `use_count`, shared state, the cost. General knowledge. |
| `new:127` | concept | home | Weak references: `std::weak_ptr`, `lock`, `expired`, cycles of shared pointers. General knowledge. |
| `new:128` | concept | home | Raw pointers as borrowed, and who deletes what. General knowledge. |
| `new:129` | concept | home | The cost of heap allocation, allocation that can wait, and allocators: arena, pool, free list. General knowledge. |
| `new:130` | hands-on | home | Optional practice on Coin Run: a `Coin*` kept across frames dangles after the coin's destruction or a hot reload. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:38`, `StrataScriptCore/Include/StrataScript/Script.h:49-52` |
| `new:217` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the order in which three objects' destructors log, in one scope and in nested scopes; Medium: the compile error of copying a `std::unique_ptr` read, and the given line with `std::move` that compiles; Medium: the `use_count` of a `std::shared_ptr` logged as copies come and go, and a `std::weak_ptr` whose `expired` turns true; Hard: an arena over a fixed buffer that hands out memory in a row and frees it all at once, its use logged. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `foundation:152` | feature | home | `Scope`, `Ref` and `WeakRef` as aliases of `unique_ptr`, `shared_ptr` and `weak_ptr`, with `CreateScope` and `CreateRef` |
| `foundation:616` | term | home | RAII |
| `foundation:617` | term | home | `Scope`, `Ref` and `WeakRef` |
| `foundation:353` | code | use | `Strata/src/Strata/Core/Base.h`, its lines 40-61 shown as the three aliases (the whole excerpt is `core/conventions`') |
| `foundation:270` | concept | link | Ownership in Strata, linked to `core/conventions` |
| `foundation:162` | feature | link | The range allocator, linked to `gpu/geometry-pool` as an allocator of offsets |
| `gamedev:321` | concept | use | Destruction at the end of the frame, and the mistake of keeping `T*` across frames, for the practice |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The stack and the heap as places in memory; memory addresses | `basics/computer` | must |
| Classes, constructors, references and pointers at the use level | `basics/programming-3` | must |
| Destroying a collected coin | `make/scripting-scene` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `allocator` | allocator | - |
| `dangling-pointer` | dangling pointer | - |
| `dereference` | dereference | - |
| `destructor` | destructor | - |
| `dynamic-allocation` | dynamic allocation | heap allocation |
| `lifetime` | lifetime | object lifetime |
| `memory-leak` | memory leak | - |
| `ownership` | ownership | - |
| `raii` | RAII | resource acquisition is initialization |
| `shared-pointer` | shared pointer | - |
| `smart-pointer` | smart pointer | - |
| `undefined-behavior` | undefined behavior | UB |
| `unique-pointer` | unique pointer | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-20 | should | order | `basics/cpp-memory` (`new:129`, `new:217`) | The Practice writes an arena that hands out memory in a row. To put objects into it, the reader needs alignment (each object at an address that is a multiple of its `alignof`) and a way to construct an object in raw memory (placement `new` or `std::construct_at`, and the destructor called by hand). Alignment is taught on `basics/bytes`, five pages later on tracks B and E, and placement `new` and `std::construct_at` are on no page. Without them the arena is undefined behavior, on the page that teaches undefined behavior. | The allocator section teaches alignment in the measure the arena needs (round the offset up to `alignof(T)` with the round-up rule of `basics/numbers`) and `std::construct_at` with `std::destroy_at`, and links `basics/bytes` for layouts and padding (about 150 words). | `allocation/basics-a.md:751-752`, `:790`, `:1092-1093`, `:1123`; `tracks.md:187-192`; a search of `allocation/*.md` for "placement new", "construct_at" and "alignof" finds nothing |

# Notes: `core/layers-registries`

## New terms

None proposed. The page defines in bold the seven glossary terms it homes: dependency inversion, registry, composition
root, layer table, tooling layer, allowlist and freeze. It also names, without a bold definition, the three forms of
dependency inversion (an interface below, a table below, a service).

## Requests

- No new hosts. The four Further reading entries stand without a link (cppreference, Game Programming Patterns, Godot,
  Epic Games); `en.cppreference.com`, `gameprogrammingpatterns.com` and `docs.godotengine.org` are on the list already, and
  the page links none of them.
- No figures file: both diagrams (the layer bands and the component registry's states) are Mermaid.
- No new words requested; the page avoids "plugin" ("extensions loaded while the program runs"), "analyzer" ("checker")
  and "POSIX".

## Since

`since: 0.3.0`. Both subjects are in the tag `v0.3.0`: `git show v0.3.0:StrataTests/Architecture/Layers.json` and
`git show v0.3.0:Strata/src/Strata/Engine/BuiltinModules.cpp` print files (commits `f0ea4dfe`, "Enforce module layers with
an include test", and `acef8948`, "Register engine modules through one composition root", both 2026-10-09). The table of
modules with `Exclude` (`158bfa0d`) and `ExternalOwners` (`96df4ef7`, 2026-11-02) came later; the page does not date them.

Pin move to v0.8.0: the quote of `Layers.json` keeps `#L3-L24` (the fields are still there; `Window.h` became
`Window.*` in `Core`'s `Exclude` and `App`'s `Paths`), refilled; callouts unchanged. The paragraph after "Three modules
are optional" adds the window system as an omittable part that is no module, from `Docs/Releases/0.8.0.md:97` ("the
engine builds without it (headless only)"), `Docs/DeveloperGuide.md:280-284`, `CMakeLists.txt:34`
(`STRATA_WITH_GLFW`) and `CMake/StrataLayers.cmake:112-117` (NoWindow in place of GLFW). The absence row of
`plan/book.md:440` still cites `Docs/Releases/0.7.0.md:404`; its parenthesis can add "and the window system (headless
only), `Docs/Releases/0.8.0.md:97`".

## Not verified

- Alternatives table: that Unreal Engine loads modules and extensions by name, that Godot builds its list of modules in its
  build system, and that `doctest` registers test cases from static constructors. Written from general knowledge; the Godot
  and Epic entries of Further reading are the cited sources, and the Godot title "Custom modules in C++" was not fetched.
- "Strata builds with three compilers on three platforms": taken from the guide's statement of MSVC, GCC and Clang and its
  three operating systems; no linker was inspected.
- That scripts reach physics through a scene service that the physics module implements: the page says it in general words,
  from `Docs/Architecture.md` ("Scripting and Audio ... reach them through scene services") and the notes of the `World`
  layer; the name of the service was not checked.
- That `AssetManagerExtensionRegistry`, `BuiltinAssets` and `MeshGeometryRegistry` stay open for good: from
  `Docs/Architecture.md` ("stay open") and the absence of any `Freeze` for them (`git grep "::Freeze()"` finds two
  classes). Their locks were not read, so the table gives no rule for the last two.
- The behaviour of `ST_CORE_VERIFY` in each build: the page says "stops the program"; the helper test checks the exit
  code and the text `verify failed:`, not a debugger's break.

## Findings not applied

All open findings of the brief are applied:

- `new:6`: the page states the table's nine modules (Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World,
  GameUI) and the three required ones (Input, Scene, Renderer); the comments of `BuiltinModules.h` that name six modules
  and two required ones are not repeated.
- `new:7`: the page names both settings sections of the Scene module, `Scene.CollisionLayers` and `Scene.Timing`.
- `new:8`: 19 layers, three of them tooling (`grep -c '"Name"' StrataTests/Architecture/Layers.json` prints 19), not 21.
- `new:9`, `new:10`: the page says that modules are chosen at compile time, that only script modules load while a program
  runs and that scripting cannot be left out.
- `new:27`: the two kinds of registry are taught, with the component and settings registries as the only two that freeze.
- `new:28`: Exercise 4 is the trace; its answer names the files and functions and the two frozen registries.

Differences from the brief and the inventory:

- The inventory's line `foundation:37` says `ST_CORE_VERIFY` names the root in every registry; at the pin the importer
  registry's message names the asset pipeline option instead (`ModuleRegistrationOptions::AssetPipeline`); the page says so.
- The brief's example, "the editor's own registration as its startup log reports it", is built from the log's format string
  and the two tests that fix the module and system lists (`Engine.Modules`, `Scene.Systems`); no startup log was captured,
  because the card forbids starting an engine program, so the page quotes no log line as captured output.
- The brief's second exercise (a late registration) is answered with the real error text from the helper of the test
  `A game registers its components through ModuleRegistrationOptions::Extra`; the "done" exercise is the third (a 50-line
  sketch of the exclusion step), not a run of the real helper.
- The brief's fourth item for `foundation:175`, the precompiled-header and header-weight suites, is named and linked to
  `engineering/flags-portability`.

## Clerk

- Nothing asked.

## Track walk E-final-6

- WK1, WK6: a paragraph after the introduction says that the page needs no project and no download and that its test
  commands and trace need the source build of Your first engine change; How it is tested says where to run them.

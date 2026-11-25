# Notes: scripting/abi-sdk

## New terms

None proposed. The eleven terms the brief homes here (SDK, host, ABI version, context, frozen struct, `StructSize`,
buffer protocol, class descriptor, module description, thunk, ODR) are defined in bold on the page.

## Requests

- Name for `tools/data/names.txt`: Lua (a scripting language, named in the problem section and the alternatives table).
  `pagecheck` reports it as `word-list`.
- Hosts: the entries in Further reading cite Ulrich Drepper's "How to Write Shared Libraries", cppreference.com, the
  Godot documentation and Alexandrescu's book without a link.
- Page links that may not exist yet: `../scripting/shared-libraries.md`, `../scripting/loading.md`,
  `../scripting/host-api.md`, `../scripting/script-system.md`, `../scripting/crash-containment.md`,
  `../reference/script-api.md`, `../make/recipes.md`, `../make/timers-events.md`, `../make/gameplay-math.md`.
- Figures: the one picture is a Mermaid diagram; no figures file.

## Since

`since: 0.3.0`: the script ABI and SDK are as old as the scripting system; evidence not re-derived from tags in this
run (`git tag --contains` was not run).

## Not verified

- Other products: Unity runs C#, Godot offers GDScript, many engines embed Lua, and Godot's native extension interface
  is a C header with function tables (alternatives table and problem section; cited from general knowledge).
- The statement that the linker may silently pick one of two definitions of a class name (ODR paragraph) is general C++
  knowledge, not checked against a build.
- The 184-byte and 176-byte sizes of `StrataScriptClassDesc` are computed by hand for a 64-bit build from the member list
  (not compiled); the 48 and 112 bytes of `StrataScriptModuleAPI` and the `NewerSDK` module likewise.
- That the engine reads `OnUISubmit` through `ST_SCRIPT_HAS_MEMBER` was read for the collision, trigger, animation and
  UI-click callbacks in `ScriptModule::ReadModuleDescription`, not for `OnUISubmit` itself.
- The "27 groups" of the host table come from the inventory, not recounted; the 165 functions were recounted from
  `ST_SCRIPT_HOST_FUNCTIONS`.
- The `since` evidence and a reading pass as the least prepared reader were not done beyond the checks.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to names.txt: Lua.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

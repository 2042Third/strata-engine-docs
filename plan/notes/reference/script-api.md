# Notes: reference/script-api

## New terms

None proposed.

## Requests

None.

## Hand-written tables

- Header groups and teaching pages: read from the header list of StrataScriptCore/Include/StrataScript/ and the brief.
- Callback table (when each runs): Script.h and the comments of StrataScriptClassDesc in ScriptABI.h.
- Field types: c_IsFieldType in Script.h.
- C types, enums, struct sizes, ABI macros: ScriptABI.h.
- strata_add_script_module options: StrataScriptCore/CMake/StrataScriptModule.cmake.
- Rechecked row by row at v0.8.0 (319075e3): read from the commit's tree (`git show 319075e3:<file>`), since the pin clone held another agent's uncommitted wind tutorial (`Wind.h`, `OnWindChanged`), which v0.8.0 lacks; header list, callbacks, field types, enums, struct sizes, ABI macros and module options unchanged; the debug-information sentence follows the module's `-g` for GCC and Clang (Docs/Releases/0.8.0.md, Fixes).

## Not verified

- The tool's groups of host functions (27) are not in the generated file, which is flat; the page does not group them.
- The generated file lacks the `Key`, `Mouse` and other enums of the SDK; the page does not list them.
- The size lint reports against the XL row: known fault of the tool for reference pages.

## Findings not applied

- critic-reference-8: a limits table needs tools/reference-limits.json, a tool file I may not edit.

## Clerk

- Nothing asked; nothing admitted.

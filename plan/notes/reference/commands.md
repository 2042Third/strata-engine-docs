# Notes: reference/commands

## New terms

None.

## Requests

None. No figures file: the page has no pictures.

## Hand-written tables

- "How values are written": read from `Strata/src/Strata/Reflection/PropertyJson.cpp` (ReadNumber, ReadVector, UUIDFromJson, PropertyValueFromJson) and `StrataEditor/src/Editor/CommandUtils.cpp` (FindAsset); the range refusal and case-insensitive property names are from `.claude/skills/strata-editor-automation/SKILL.md` section 4.
- Built-in assets: `Strata/src/Strata/Asset/BuiltinAssets.h` and `BuiltinAssets.cpp`.
- Step of a command script: `StrataEditor/src/Editor/EditorCommandRunner.h` and `Commands/BatchCommands.cpp`.
- The groups (toolsets and teaching page): toolsets read from the generated group files, order from `EditorCommands.cpp`.

## Not verified

- Property names matched without regard to case, and out-of-range refusal leaving nothing changed (from the skill and the inventory, not read in `CommandUtils::ApplyComponents`).
- That `until` needs `steps` or `seconds` (header comment of EditorCommandRunner.h only).
- Link targets are plan ids of briefs; pages check passed.

## Findings not applied

- Brief's group table with a count column: omitted, because group counts are not in values.json and the page never types counts.
- critic-reference-5 and -6 applied (tables of values, built-in assets, script step).
- Size: the lint reports under XL; known fault for generated reference pages.

## Clerk

- Fixed: the term mark inside a link's text is removed (the link stays); the Python side now refuses a mark inside link text.

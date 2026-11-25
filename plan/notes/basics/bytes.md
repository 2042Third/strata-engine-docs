# Notes: basics/bytes

## New terms

Defined once in bold, beside the glossary terms of the brief:

- magic number: a fixed value at the start of a file that says which format the file claims to be; this page is the home.
- header: the block of fixed size at the start of a file that describes the rest of the file; this page is the home.
- alignment: the rule that a value starts at an address that is a multiple of a number, usually its type's size; this page is the home (the arena of `basics/cpp-memory` needs it: see critic-basics-a-20 below).
- padding: unused bytes the compiler inserts between members or after the last one of a struct; this page is the home.
- standard-layout type: a struct that keeps its members in declaration order, so that `offsetof` is allowed; this page is the home.

## Requests

- `tools/data/extra-words.txt`: little-endian and big-endian (28 uses; the brief's own words for the two byte orders), and Interchange (only inside the expansion "American Standard Code for Information Interchange (ASCII)", which the acronym rule asks for). These are the three open `word-list` findings.
- No figures file: the page's one picture is a Mermaid diagram (the twelve bytes of a padded struct). The Mermaid diagram is not rendered by the tools.
- Sketches (all compile and run under pagecheck): `basics-bytes-endian`, `-padding`, `-bounds`, `-utf8`, `-decode`, `-coin-name`.
- The Practice has no tutorial file: it is answered by hand and by sketches (the page comes after `basics/programming-1`).

## Not verified

- General knowledge, not engine facts: network byte order and some older formats being big-endian; processors reading aligned values fast; Windows storing UTF-16 little-endian, taking `wchar_t` in its wide functions and a code page in its narrow ones; the byte `FC` being ü in Windows-1252 and a Russian letter in the Cyrillic page; UTF-16 surrogates for U+1F600; the unit names KiB and MiB.
- That `CountCharacters` in `Strata/src/Strata/GameUI/GameUISystem.cpp` serves a text field's character limit: the function and its use of continuation bytes were read, its callers were not.
- That the Coin Run project has coins to rename in the Inspector, and the Inspector's name field: the optional Practice item follows the brief; `make/scenes-entities` and `make/project-coin-run` were not available to check. The script calls `GetEntity().GetName()` and `Log::Info` (both in `StrataScriptCore/Include/StrataScript/`), and the script is `pseudocode`.
- The pages linked in the text and in "Where the book uses it" (`core/files`, `assets/robustness`, `basics/data-formats`, `engineering/generated-code`) were not yet written: their link texts and the one sentence on what each uses are from the briefs, not from the pages.
- The last edit (the first-use expansion of ASCII, and the order of the pack reader's three checks: version, header checksum, flags) was made after the third pagecheck run and not run through it.

## Findings not applied

- critic-basics-a-20 (arena, alignment and placement `new`): names `basics/cpp-memory`, not this page. This page teaches alignment (`alignof`, padding, rounding a size up to a multiple) and would be linked from there; placement `new` and `std::construct_at` are not part of this page.
- critic-basics-a-21: applied as `## Common mistakes` (an unbounded length, a wrapping multiplication, a struct written as it is, byte order, UTF-8 cut by bytes or `size()` taken for characters, logging a byte).
- critic-basics-a-22: applied, as the last mistake of `## Common mistakes` (`Log::Info` writes with `<<`; the fix is `int(value)`; `StrataScriptCore/Include/StrataScript/Log.h`).
- Brief Items `new:175` to `new:182`, `new:208`, the glossary rows and the Test out box: applied. The pack header (`Strata/src/Strata/Asset/AssetPack.h`), `BinaryReader::ReadArray` and the save-file name cut are quoted; `ParseSpirv` is named with a link to `engineering/generated-code`.
- Brief "Strata's rule at the boundary is `core/files`'": the page names `Utf8ToWide`, `WideToUtf8`, `FileSystem::FromUTF8` and `FileSystem::ToUTF8` and links `core/files` for the rule.

## Clerk

- Admitted: magic number, header, alignment, padding, standard-layout type.
- `extra-words.txt`: "endian" (little-endian, big-endian). `names.txt`: "American Standard Code for Information Interchange" (the name as a whole, so "Interchange" needs no line).
- Mark made by the clerk (no word changed): **standard-layout type** for **standard-layout** type, so that the admitted term is defined.

## Track walk E, final, segment 3 (2026-11-24)

- WK1, WK2 (`plan/walks/E-final-3.md`): Practice 6 now names its start (your Coin Run, or Checkpoint 4 of Ship the
  finished game) and says that the five coins of that state appear only in play (`Scripts/CoinPlacer.cpp` instantiates
  them), so the reader places a sixth from `Prefabs/Coin.stprefab` and renames that one. The pseudocode is the whole
  file (include, class, `ST_SCRIPT_CLASS`), with the steps to make, build and attach it through **Add Script...**.
- Checked with the 0.8.0 package, headless, on a copy of Checkpoint 4 (`docs-work/walkfix-E3`, `run1.ps1`, `run1.out`):
  `asset.place` of the prefab, `entity.rename` to `Münze`, the file of the page as `Scripts/NameLength.cpp`, a build,
  `script.add` beside `Coin`, Play. The Console shows `name bytes 6, code points 5`; `Coins placed:` counts the extra
  coin. This replaces the "not verified" item on the Coin Run exercise.

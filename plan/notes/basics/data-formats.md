# Notes: `basics/data-formats`

## New terms

- format header: a small part of a document that names its kind and its version, so a reader checks them before it trusts the rest; home `basics/data-formats`; aliases: header (of a file).
- token: the smallest meaningful piece a reader cuts text into, such as one special character, a whole string, a number or a word; home `basics/data-formats`.
- parser: the part of a reader that checks that tokens follow the rules of a format and builds the values from them; home `basics/data-formats`.
- regular expression: a short text that describes a set of texts; a program asks whether a text matches it; home `basics/data-formats`; aliases: pattern, regex.
- glob: the simple pattern that file names use, such as `*.cpp`, where `*` stands for any run of characters; home `basics/data-formats`.
- stable hash: a hash whose rule is written down and never changes, so every program on every machine gives the same number for the same bytes; home `basics/data-formats`.

## Requests

- `tools/data/extra-words.txt`: `backslash` (the escape character `\`, used in the JSON and regular expression sections; six uses).
- Sidebar: `basics/data-formats` is in no track list, so pagecheck reports O5 for tracks `[B, E]`; the sidebar is the planner's file.
- Figures: none requested. The page has no pictures; the Base64 rule is a worked example with a sketch.
- Sketches (all compile with warnings on and print the quoted output): `basics-data-formats-roundtrip.cpp`, `-tokens.cpp`, `-glob.cpp`, `-base64.cpp`, `-fnv.cpp`, `-crc.cpp`, `-birthday.cpp`, `-anagrams.cpp`.
- Words proposed with the terms above (`parser`, `glob`) are the ones the lint may report until they are admitted.

## Not verified

- The standard UUID's text form and the example `123e4567-e89b-12d3-a456-426614174000`: general knowledge (RFC 4122), not engine code.
- That a JavaScript number holds whole numbers exactly only up to 2^53, and why a string suits a 64-bit handle in JSON: general knowledge. The page says what the string keeps, not that Strata chose it for this reason.
- The SHA-256 digests of `abc`, `abd` and the empty text, and the FNV-1a value of `a`: computed with Python's `hashlib` and plain arithmetic, standard test values; the page's FNV-1a and CRC-32C steps are also run by sketches.
- That CRC-32C catches every burst error of up to 32 bits: general knowledge about CRCs.
- Coin Run's project file looks like the Tetris file: `make/project-coin-run` is not written at this pin. The page names only the extension `.stproj` (`Project::c_FileExtension`) and the two top-level objects, which `Project::Save` writes for every project.
- The sentences of "Where the book uses it" about what `editor/commands`, `automation/json-rpc`, `assets/what-is-an-asset`, `world/reflection` and `automation/security` use come from their briefs, not from those pages.
- That `viewport.capture` returns the screenshot as Base64 only when asked: the code (`StrataEditor/src/Editor/EditorViewportCommands.cpp`) encodes it when a flag is set; the page says "can return" and names no option.

## Findings not applied

- critic-basics-a-10 (VS Code attach entry and `launch.json`): it concerns `basics/debugging`; this page teaches JSON but the finding asks for a tab on that page.
- critic-basics-a-21 (Common mistakes) and critic-basics-a-23 (birthday bound with Strata's numbers): applied.

## Clerk

- Admitted: format header (alias "header" left out: `basics/bytes` homes it), parser, regular expression (alias regex; "pattern" left out: one everyday word), glob, stable hash.
- `extra-words.txt`: "backslash". Sidebar: see the clerk's report (O5).
- Not admitted, because the page check would then fail and the page is the writer's: token-basics (its paragraph would define 2 terms with parser (term-paragraph)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

## Track walk E, final, segment 3 (2026-11-24)

- WK3 (`plan/walks/E-final-3.md`): Before you start lists only Bytes, so the hash section restates the toy hash of
  Data structures I (the sum of the letter codes, `ant` = 323) that its Try it and Practice 4 use, and says what a
  wrapping product keeps. Data structures I and Numbers are in the page's Needs closure through Bytes.
- WK4: Practice 6 links Coin Run and Checkpoint 4 of Ship the finished game, whose zip holds `CoinRun.stproj`.
- WK5: Checkpoint 4's `CoinRun.stproj` (169 lines) has three top-level objects, `Project`, `Settings`
  (`Input.Actions`, `Scene.CollisionLayers`) and `Strata` (Format Project, Version 3); `StartScene` 00D86E4989BE1767.
  `Project::Save` writes `Settings` when the project has settings (`Strata/src/Strata/Project/Project.cpp:414-415`). The
  Tetris quote's paragraph and the worked solution now say so.

# Notes: start/welcome

## New terms

- **editor**: `StrataEditor`, the program in which a game is made, its levels laid out and played. Home: this page (glossary `editor`).
- **game logic**: the set of rules that decides what happens in a game. Home: this page (glossary `game-logic`).
- **visual scripting**: writing game logic by joining boxes with lines on a graph instead of typing text. Home: this page (glossary `visual-scripting`).
- **track**: one reading order through the book (bold in the doors section). The glossary may home it on `start/how-to-read`; the planner may move the definition there.
- Plain sentences, not terms: AI agent (critic-start-19), game engine (inside the link to `start/what-an-engine-is`).

## Requests

- `tools/data/names.txt`: none after round 2 except what the lint accepted; the page uses Tetris, Unreal Engine, Blueprints, Vulkan, Apple silicon and passed `word-list`.
- No figures file: the journey map is a Mermaid diagram with a table after it. The Mermaid box labels were not checked by the site build.
- The exercise is answered, not done (the brief and `style.md` section 8: the page comes before `start/install`); `pagecheck` raised no finding for the missing solution file.

## Not verified

- The tracks' first and last pages, the three C++ primers after Your first script and "Track G is open to a beginner after `make/project-coin-run`" come from `plan/tracks.md` and the brief, not from the engine.
- The Test out box on `basics/computer` (question 5's answer) is the plan's rule for every primer; the page does not exist yet.
- The stage pages named in the journey table are the pages the briefs give; the pages `make/*` were not read.
- Unreal Engine's Blueprints as visual scripting, and the Further reading entries, are general knowledge, not checked here.
- The compiler toolchain is found "at your first build" (Docs/Manual/Scripting.md "Where builds happen" at the pin); not run.

## Findings not applied

- critic-start-19: applied (the AI agent sentence in the opening; no link to `automation/agents`, a part that tracks G and B do not read; `make/with-an-agent` is linked instead).
- Brief item `new:21`: applied as an answered exercise 1; question 5 of Check yourself also tests `choose-track`.
- Brief item `new:1`: the evidence grep was rerun at the pin: only miniaudio's node graph in `Strata/src/Strata/Audio` matches. The page states that the engine and editor have no graph for game rules and does not cite the audio files.
- Brief: "the not-done entry" is linked as `appendix/not-in-strata`.

## Clerk

- Nothing to admit: editor, game logic and visual scripting are homed here already.
- Refused: "track" as a term: one everyday word, and the glossary homes "reading track" on `start/how-to-read`; moving it is the planner's.

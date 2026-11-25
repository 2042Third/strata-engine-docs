# Brief: `start/welcome`

| Field | Value |
| --- | --- |
| Title | What Strata is and what this book teaches |
| Kind | C |
| Size | S |
| Tracks | G, E, B |
| Needs | - |
| From | new; the three doors (make a game, understand an engine, learn from zero); the game maker's door says that game logic is C++ (no visual scripting) and that an AI agent can help; it says which track a beginner continues on, and from which page |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/welcome` — What Strata is and what this book teaches

**Covers.** The page opens on what a reader can make, shown before it is named: the launcher's sample cards (Tetris,
the Third-Person Adventure, the High Desert Outpost) and the archive README's first sentence, that Strata is a 3D game
engine with an editor that people and AI agents drive the same way. It defines the editor (`StrataEditor`, the program
in which a game is made, its levels laid out and played) and names the game engine once, inside a link to
`start/what-an-engine-is` with a plain description. Then the maker's journey map: install, the launcher, a project from
a template, building the scene, assets, scripts, playing and testing, the export and the folder a player runs, each box
naming the part of `make` that teaches it. The game maker's door says three things plainly: game logic (defined in a
sentence) is C++ code that the editor builds for you; Strata has no visual scripting (defined in a sentence; the
not-done entry), and the book teaches the C++ a game needs from zero; an AI agent can build a game through the same
commands that the person's clicks run, which `make/with-an-agent` teaches. Then the three doors as one table: make a
game (track G), understand or change an engine (track E), learn from zero (track B), each with who it is for, the page
it starts with and the page it ends with. The beginner's paragraph says where track B goes after its last primer: on
track G from `make/gameplay-math`, or on track E from `core/map`; and that track G is open to it already after
`make/project-coin-run`. The three platforms are named once, with a link to `start/install`. The concept shape is
compressed to the size: the problem is the reader's own (I want to make a game, or to understand one), and the
approaches are the doors. The exercise gives three readers in a
sentence each, and the reader names each one's track, its first and last page and, for the beginner, where it
continues; it is answered, not done, because the page comes before `start/install`. At the end the reader can say what
Strata is, choose a track, and name the page where the track starts and, for a beginner, where it continues.

**Leaves out.**

- What a game engine is, the frame, and the survey of engines → `start/what-an-engine-is`
- The tracks' badges, the kinds of page and the strips, used on every page → `start/how-to-read`
- Why game code is C++ in a module of its own, and how other engines script → `scripting/why-scripts`
- Making a game with an AI agent, step by step → `make/with-an-agent`
- What the release archive holds and what each platform needs → `start/install`
- Everything Strata does not do → `appendix/not-in-strata`

**Fit.** `fits`: about 1,950 words against S (1,500). The four sections (what Strata is, with the problem and the naive
answer; the journey map; the game maker's door; the three doors) take about 950 words, and the example, the common
mistakes and the exercise about 400; the fixed parts take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:396` | figure | home | The maker's journey map: install, launcher, project from a template, scene building, assets, scripts, play and test, export, the exported folder; each box names its panel and the `make` page that teaches it |
| `gamedev:570` | term | home | Editor: `StrataEditor`, the program in which games are made; defined in the first section |
| `new:1` | not-done | home | No visual scripting: game logic is C++ script classes, written as text and built by the editor; the paragraph names how other engines do it (Unreal's Blueprints) and links `appendix/not-in-strata`. Evidence: `git grep -niE "visual script\|node graph\|nodegraph\|blueprint\|imnodes\|node editor" 822a7a46 -- Strata/src StrataEditor/src` finds only miniaudio's node graph in `Strata/src/Strata/Audio` (`AudioEngine.cpp:240`, `AudioVoice.cpp:155, 306`, `AudioVoice.h:30, 77`), which is not scripting; `AGENTS.md:271` |
| `new:2` | concept | home | The three doors and their tracks (G, B, E): who each is for, its first and last page, and where track B continues (`make/gameplay-math` on G, `core/map` on E, or G after `make/project-coin-run`); the plan asks for it in `book.md`, "Tracks", and `tracks.md`, "Rules". General knowledge. |
| `scripting:243` | concept | use | Game logic is C++ code kept outside the engine, as one paragraph of the game maker's door (`book.md` names this page the use of "Why game code lives outside the engine"); the reasons are `scripting/why-scripts`' |
| `automation:269` | concept | link | An AI agent can drive the editor through the commands a person's clicks run; one sentence, linked to `make/with-an-agent` (track G's use home; `automation/agents` is the home) |
| `gamedev:20` | feature | link | The three platforms of the release archives, named once and linked to `start/install` |
| `new:21` | hands-on | home | The exercise (**Basic.**, answered): three readers in a sentence each (one wants to make a small game, one has never written a program, one wants to know how an engine draws its pictures); the reader names each one's track, the page it starts with and the page it ends with, and where the beginner continues. The page comes before `start/install`, so the exercise is answered, not done (`style.md` §8); the plan asks for it in `critique/rulings-7.md`, R32 (D27). General knowledge. |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is, named once in a link | `start/what-an-engine-is` | helps |
| What a programming language is, for "game logic is C++" | `start/how-to-read` | helps |
| The tracks' badges and the "next page" links | `start/how-to-read` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `editor` | editor | - |
| `game-logic` | game logic | - |
| `visual-scripting` | visual scripting | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-start-19 | could | order | `start/welcome` | The page tells B0 and G0 that AI agents drive the editor and can build a game, and does not say what an AI agent is. The term's home, `automation:704`, is on part `automation`, which tracks G and B never read, and the page has no row for it. | One plain sentence where the word first appears (a program, such as Claude Code, that takes a request and does the work on the computer by itself), with a `link` row of `automation:704`. About 25 words. | `allocation/start.md:5-14`, `:47`; `allocation/automation.md:64`; `style.md:39-73` |

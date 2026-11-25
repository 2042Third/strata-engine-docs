# Brief: `start/what-an-engine-is`

| Field | Value |
| --- | --- |
| Title | What a game engine is: one frame, start to finish |
| Kind | C |
| Size | L |
| Tracks | G, E, B |
| Needs | `start/first-game` |
| From | foundation "What an engine is, and how Strata is put together" (first half); gamedev "What it takes to make a game" (concepts 1-2); it explains what the reader just did; home of the frame map for people (the renderer's passes are `gpu/frame-tour`'s), with frame time in milliseconds and the CPU preparing one frame while the GPU draws the one before (the mechanism, frames in flight, is `gpu/how-a-gpu-frame-works`'), and of a survey of engines (curricula 1.0) |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/what-an-engine-is` — What a game engine is: one frame, start to finish

**Covers.** The problem as the reader met it: in `start/first-game` the cube fell, slid and spun while nobody touched
anything, and a strip of six still pictures of that fall shows that the motion was a series of pictures. The naive
answer, a program that waits for clicks as a word processor does, breaks at once: the world changes without input. The
idea: a game is a loop, and one pass of it is a frame (read the input, change the game, draw a picture, show it); frame
rate and frame time are defined, frame time in milliseconds (1,000 ms divided by the frame rate: 16.7 ms at 60 frames a
second, 33.3 at 30, 6.9 at 144), and an `:::example` shows why frame time, not frame rate, is what adds up (a drop of 10
frames a second costs 3.3 ms from 60 to 50 and 16.7 ms from 30 to 20), and a hitch is one frame that takes far longer
than the frames around it. Delta time comes from the reader's own
`Spinner`: `DegreesPerSecond * deltaTime` turns the cube by the same angle each second at any frame rate, against the
newcomer's error of a fixed amount per frame. Then the frame map for people, the page's spine: one frame of the
reader's game in Strata's order (the frame's input; the scripts' updates and the animation; physics in small equal
steps, zero to several a frame, named once with a link to `core/time`; the late updates and the sound; the renderer
drawing the scene into pixels with the GPU's shaders, with renderer, pixel and shader defined in a plain sentence
each; the picture shown). Then the processor and the GPU as two workers: the GPU as `start/install` defined it, and
the processor in one plain sentence inside a link to its home, `basics/computer` (a forward mention); the processor
prepares the next frame while the GPU draws the one before, two lanes in a diagram (the mechanism, frames in flight, is
`gpu/how-a-gpu-frame-works`'). The status bar's frame pill is read with this in mind: it shows the work a frame takes,
not the time between pictures, so 4 ms at 60 frames a second is no contradiction (an exercise on the Tetris copy).
Then what an engine is, the term's home: the part every game shares (the loop, drawing,
physics, sound, input, loading assets, scenes), set against the game (its scenes, assets and scripts), the editor
(defined in `start/welcome`) and the runtime (the program that plays an exported game, copied under the game's name);
asset and export get one sentence each.

The approaches: a survey of engines as one table (general engines with an editor such as Unreal, Unity and Godot;
code-first engines such as Bevy; in-house engines), with the language of game code, the editor, the platforms and the
licence, each with a source in Further reading, and Strata's place among them. Strata's choice and its reasons, each in
a sentence with the page that teaches it: a C++ engine with an editor on three desktop systems; game code in C++ script
modules kept outside the engine, so that a crash in game code does not take the editor down and code can be rebuilt
while the game plays (`scripting/why-scripts`); every editor action a command that people, scripts and AI agents run
alike (`editor/commands`). What the choice cannot do: no mobile, console or web games (`core/platform`), no gameplay
networking (`appendix/networking`), linked to `appendix/not-in-strata`. Common mistakes: taking the editor for the
engine or for the game; moving by a fixed amount per frame; reading differences of frame rate as costs; expecting to
change engine files to make a game. Two exercises: frame times computed from frame rates and back (answered), and the
frame pill read on the Tetris copy while it plays (done). At the end the reader can describe one frame from input to
picture, compute frame time from a frame rate and back, explain why `Spinner` multiplies by `deltaTime`, and say what
the engine, the editor, the runtime and the game each are.

**Leaves out.**

- Strata's programs, libraries, modules and layers → `core/map`
- The frame loop's code, its stages and hooks, pacing and vsync → `core/frame-loop`
- Fixed steps, the accumulator and time scale → `core/time`, `make/script-loop`
- The script's callbacks in a frame → `make/script-loop`
- Frames in flight, fences and how a GPU draws → `gpu/how-a-gpu-frame-works`
- The renderer's passes, in order → `gpu/frame-tour`
- Measuring a frame: percentiles, "CPU, GPU or capped" → `core/profiling`, `make/performance`
- What an editor is as a program apart from the game → `editor/program`
- Scenes, entities and components as an engine stores them → `world/what-a-world-is`
- Strata's names for other engines' words → `start/coming-from`

**Fit.** `fits`: about 5,600 words against L (5,000). Seven ideas from zero (the loop and the frame, frame time, delta
time, the frame map, the two workers, the engine against the editor, runtime and game, the survey) at about 450 words
each, with three figures, take most of the page; the common mistakes and the two exercises take about 750 more, and the
survey is held to one table and two paragraphs.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:291` | concept | home | Engine, game, editor and runtime: the engine is the part every game shares, the editor the program for making, the runtime the player of exported games, the game its data (scenes, assets) and its script module; the error of expecting to change engine files to make a game |
| `gamedev:569` | term | home | Engine (game engine), placed here from `start/welcome`, which names it once in a link: the one-home table gives "What a game engine is" to this page |
| `gamedev:571` | term | home | Runtime, placed here from `start/install`, whose table names the `StrataRuntime` file without the term |
| `gamedev:614` | term | home | Frame and delta time, with `Spinner`'s `deltaTime` as the example |
| `new:14` | figure | home | The frame map for people: the frame's input, the scripts' updates and the animation, physics steps (zero to several), the late updates and the sound, drawing, the picture shown, in Strata's order. Evidence: `Docs/Architecture.md:790-804` (the application's frame); `Docs/Architecture.md:965-972` (the scene systems in update order: Animation in `OnUpdate` before Physics, Audio in `OnLateUpdate`); `Docs/Architecture.md:1012-1017` (the scene's update, fixed steps and late update) |
| `new:15` | figure | home | Two lanes, the processor and the GPU: the processor prepares frame N+1 while the GPU draws frame N. Evidence: `Strata/src/Strata/Renderer/GraphicsDevice.h:28` (`MaxFramesInFlight = 2`); `Docs/Architecture.md:298` |
| `new:16` | figure | home | Six still frames of the reader's cube falling onto the ramp, each with its frame number and time: motion as a series of pictures. Evidence: the scene of `start/first-game`'s fourth checkpoint, made from `StrataEditor/src/Editor/ProjectTemplates.cpp:49-95` and the Cube preset of `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-77` |
| `new:17` | concept | home | Frame rate and frame time: 1,000 ms divided by the frame rate, and why frame time is what adds up; worked as the page's example. General knowledge. |
| `new:18` | concept | home | A survey of engines (Unreal, Unity, Godot, Bevy, in-house engines) as a table of the language of game code, the editor, the platforms and the licence, each with a source; the plan asks for it in the outline's From (curricula 1.0). General knowledge. |
| `new:19` | concept | home | The processor and the GPU as the two workers of the frame map: the GPU as `start/install` defines it, and the processor in one plain sentence inside a link to `basics/computer`, the term's home (a forward mention, `style.md` §3; start-q5). General knowledge. |
| `new:26` | hands-on | home | Two exercises: **Basic.** frame times from frame rates and back (120 and 25 frames a second, 8 ms and 40 ms), answered; **Medium.** done on the Tetris copy: the status bar's frame pill is read while the game plays and while nothing happens, and the reader says why its milliseconds can be far fewer than 1,000 divided by its frame rate, and what "idle" means. Evidence: `StrataEditor/src/EditorLayer.cpp:1946-1966` (the pill: the work a frame takes, the frame rate, "idle", and the tooltip) |
| `gamedev:286` | concept | use | The game as a loop at the level of the frame, and the error of moving by a fixed amount per frame; frame and fixed updates are `make/script-loop`'s |
| `foundation:208` | concept | use | What an engine adds to a program, at a person's level; Strata's programs and libraries are `core/map`'s |
| `foundation:214` | concept | use | Why games loop instead of waiting for events; the loop's forms are `core/frame-loop`'s |
| `foundation:220` | concept | use | The stages of a frame in their order, as the boxes of the frame map; the hooks are `core/frame-loop`'s |
| `foundation:569` | term | home | Frame, one pass of the main loop: the same word as `gamedev:614`, defined once here (passed by `core`) |
| `foundation:228` | concept | link | The fixed step, named once in the frame map with a link to `core/time` |
| `foundation:234` | concept | link | Frame pacing and vsync, named in the frame pill's exercise and linked to `core/frame-loop` |
| `render-core:314` | concept | link | Frames in flight, the mechanism behind the two lanes, linked to `gpu/how-a-gpu-frame-works` |
| `gamedev:46` | feature | use | The status bar's frame pill (the work a frame takes and the frame rate), read in an exercise on the Tetris copy |
| `foundation:433` | figure | link | The frame pill and its tooltip, whose home is `core/profiling` |
| `gamedev:405` | figure | link | One frame from a script's side, linked to `make/script-loop` |
| `editor-core:290` | concept | link | What an editor is, and why it is a separate program from the game, linked to `editor/program` |
| `scripting:243` | concept | link | Why game code lives outside the engine, linked to `scripting/why-scripts` |
| `scene-ecs:271` | concept | link | What a scene is inside an engine, linked to `world/what-a-world-is` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor, a project from Basic 3D, its entities, Play and Stop, and the `Spinner` script with its `deltaTime` | `start/first-game` | must |
| The GPU, the part of a computer that draws pictures | `start/install` | must |
| The editor as the program in which games are made | `start/welcome` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset` | asset | - |
| `export` | export | - |
| `frame-time` | frame time | - |
| `game-engine` | game engine | engine |
| `game-loop` | game loop | frame loop, main loop |
| `hitch` | hitch | - |
| `pixel` | pixel | - |
| `renderer` | renderer | rendering |
| `runtime` | runtime | StrataRuntime |
| `shader` | shader | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-start-2 | must | missing-item | `start/first-game` (sections 3 to 5, "What next") | The tutorial never saves the scene and never opens a project again. The cubes and the Spinner on the third cube live only in the open scene, and closing the editor asks Save, Don't Save or Cancel, which the page does not show. Three later pages reopen what this page made: the frame pill exercise of `start/what-an-engine-is` plays the Tetris copy again, `start/coming-from` opens another sample's copy, and on track E `basics/programming-1` uses this project's Spinner as its playground. Track E never reads `make/editor-tour`, where saving and recent projects are taught. | Sections 3 to 5 each end with **File ▸ Save Scene** (Ctrl+S; the item is off while the game plays), and the last says what closing the editor asks. "What next" shows how a project is opened again: the launcher's Recent projects card or **File ▸ Open Recent**. New `use` rows of `gamedev:36` and `gamedev:513` (homed on `make/editor-tour`) and of `editor-core:131` (homed on `editor/saving` with `editor-core:130-137`). About 250 words. | `allocation/start.md:227-261`, `:416`, `:505-506`; `allocation/basics-a.md:158-159`, `:229-230`; `allocation/make-a.md:121-125`, `:159`, `:168`, `:174`; `allocation/editor.md:376` (`editor-core:130-137`); `book.md:66-67`; `StrataEditor/src/EditorLayer.cpp:1464`, `:1493`; `StrataEditor/src/Panels/WelcomePanel.cpp:468-490`; `StrataEditor/src/Editor/EditorContext.cpp:694` |
| critic-start-11 | should | missing-item | `start/install`; `new:18` on `start/what-an-engine-is` | R21 says that `start/install` states only what the engine's repository says of the engine's terms at the pin, and no row of the page holds it. The repository has no license file. The folder's `ThirdPartyNotices.md` lists the components' licenses and the attributions that games made with the samples' assets must show, and the page's table of the folder leaves that file out. The survey of `start/what-an-engine-is` has a licence column and a row for Strata, and nothing says what its cell holds. | A new item (feature) on `start/install`: one or two sentences after the folder's table, which gains `ThirdPartyNotices.md` (about 60 words). The Strata row of `new:18` says the same in its licence cell, and no more (about 15 words). | `critique/rulings-6.md:59-61`, `:337`; `allocation/start.md:145-147`, `:414`; `allocation/appendix.md:642`; `git ls-tree --name-only 822a7a46` lists no license file; `Docs/Releases/PackageReadme.md:23` |
| critic-start-17 | could | missing-item | `new:26` on `start/what-an-engine-is` | The frame pill that the exercise reads shows a third value, the count of jobs in flight, and its tooltip speaks of worker, I/O and background threads. Neither the exercise nor the page says what that number is. | One sentence in the exercise: the last number counts work waiting for the helper threads, which `core/jobs` teaches, and the exercise does not need it. About 30 words. | `allocation/start.md:363-364`, `:416`; `StrataEditor/src/EditorLayer.cpp:1946-1972` |

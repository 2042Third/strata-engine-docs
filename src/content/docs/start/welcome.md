---
id: start/welcome
title: "What Strata is and what this book teaches"
description: "What Strata and its editor are, how a game gets made in it, and which of three tracks through this book fits you."
kind: concept
size: S
tracks: [G, E, B]
needs: []
time: 20
learn:
  - id: what-strata-is
    text: explain what Strata and its editor are, and what an AI agent can do through the editor
  - id: game-logic
    text: explain why Strata's game logic is C++ code and why Strata has no visual scripting
  - id: choose-track
    text: choose the track that fits a reader and name its first and last pages
  - id: beginner-path
    text: name the page where the beginner's track continues, on the game maker's track and on the engine track
status: final
---

Open Strata for the first time and its start page shows a row of cards under the heading **Start something new**. Some cards are templates, ready-made starting points for your own game. Others are finished games: a card opens a copy of one in a folder you choose, and you play it. Among them are the **Tetris sample**, the **Third-Person Adventure sample** and the **High Desert Outpost sample**.

Tetris is the falling-block classic. In the Third-Person Adventure a robot runs and jumps across floating islands to collect coins.

The High Desert Outpost is a scene more than a game: a fuel stop in a rocky valley, lit by a low sun.

Strata is a 3D game engine with an editor that people and artificial intelligence (AI) agents use in the same way. An AI agent is a program, such as a coding assistant, that takes a request and does the work on the computer by itself. The **editor**, a program named `StrataEditor`, is where you make a game: you lay out its levels, give its objects their behavior and play it. The game engine is the ready-made code under it that draws the picture, moves objects and plays sound; [What a game engine is](../start/what-an-engine-is.md) explains it.

## Writing every part yourself costs years before the first rule

Suppose you want a robot to jump across islands. A blank source file offers you nothing: no window, no picture, no sound, no way to make the robot fall. The obvious answer is to write those parts yourself. That work comes before your first game rule, and it teaches you little about your game.

Strata supplies those parts, so you start from a working scene or a finished sample and change it. It runs on three platforms: Windows (64-bit), Linux (64-bit, Ubuntu 24.04 or newer) and macOS 14 or newer on Apple silicon. Every platform needs a graphics processing unit (GPU) with a Vulkan 1.2 driver. Each release is one folder that you unpack, and [Installing Strata](../start/install.md) says what each platform needs.

## A game gets made in nine boxes

The idea of this book is the maker's journey. A game starts as an installed program and ends as a folder that a player runs without the editor. Between them lie seven more boxes, and each has its part of the book.

```mermaid caption="The maker's journey runs from installing the editor to the folder a player runs. Every box has a page that teaches it, named in the table below." alt="Nine boxes in a row, joined by arrows: install, launcher, project from a template, scene building, assets, scripts, play and test, export, exported folder."
flowchart LR
    A["Install"] --> B["Launcher"] --> C["Project from a template"] --> D["Scene building"] --> E["Assets"] --> F["Scripts"] --> G["Play and test"] --> H["Export"] --> I["Exported folder"]
```

The table names what you do in each box and the page that teaches it.

| Box | What you do | Where the book teaches it |
| --- | --- | --- |
| Install | Unpack the release for your platform and start the editor | [Installing Strata](../start/install.md) |
| Launcher | Choose a template, a sample or an earlier project | [A tour of the editor](../make/editor-tour.md) |
| Project from a template | Create a project; the Basic 3D template already holds a lit scene with a camera, a sun and a ground | [A tour of the editor](../make/editor-tour.md) |
| Scene building | Add objects and give them parts | [Scenes, entities and components](../make/scenes-entities.md) |
| Assets | Bring in models, pictures and sounds | [Bringing in assets](../make/assets.md) |
| Scripts | Write the rules of the game | [Your first script](../make/first-script.md) |
| Play and test | Run the game inside the editor and fix what breaks | [Playing, testing and debugging](../make/play-test-debug.md) |
| Export | Build a game that needs no editor | [Exporting and shipping](../make/export.md) |
| Exported folder | Hand a player the folder that holds the game | [Exporting and shipping](../make/export.md) |

[Projects, saving, undo and recovery](../make/project-files.md) teaches saving and undo, which belong to every box.

## Game logic is C++ text, and Strata has no visual scripting

**Game logic** is the set of rules that decides what happens in a game: what a button press does, when a coin is collected, when the level ends. In Strata, game logic is C++ code. You write it as text in script classes, and the editor builds it for you into a library of its own. A C++ compiler and CMake must be on your computer; the editor finds them at your first build and names what is missing.

**Visual scripting** is a way to write game logic by joining boxes with lines on a graph instead of typing text. Strata has none: the engine and the editor contain no graph of boxes for game rules. The book does not assume that you know C++. Tracks G and B teach the C++ a game needs from zero, in three primers that come after [Your first script](../make/first-script.md). Everything else that Strata omits stands in [What Strata does not do](../appendix/not-in-strata.md).

:::elsewhere[Unreal Engine]
Unreal Engine offers Blueprints, a visual scripting system in which a designer builds game rules from connected nodes. Strata chose text, and a reader who comes from Blueprints must learn to type the rules instead. The Further reading section names the source.
:::

:::why[Why does game code stand apart from the engine?]
Game rules change many times an hour, and a mistake in them must not bring the engine down. Strata keeps game code in a module of its own behind a plain C interface, so a crash stays inside the module and a changed script loads while the game runs. The cost is that you write text and need a compiler on your machine. [Why game code lives outside the engine](../scripting/why-scripts.md) weighs the other ways engines run game code.
:::

:::example[One game rule, in numbers]
The rule is: when the player touches a coin, add 10 points and remove the coin. Suppose the player holds 3 coins, so the score is 30. After the next touch the score is 40 and the coin is gone from the level. A visual script draws this rule as boxes joined by lines. A Strata script states it in a few lines of C++ that run whenever the player touches a coin.

The rule is the same in any engine. Only the way you write it differs.
:::

An AI agent can build a game through the same commands that your clicks run. Every change you make in the editor runs a command, so a request from an agent and a click from you do the same work. The Tetris sample came to be that way: an agent made it through the editor alone. [Making a game with an AI agent](../make/with-an-agent.md) teaches how.

## Three doors lead through the book

A **track** is one reading order through the book. Each track has a door, and the doors fit three readers: one who wants to make a game, one who wants to understand or change an engine, and one who starts from zero. All three read this page, [How to read this book](../start/how-to-read.md), [Installing Strata](../start/install.md), [Your first game](../start/first-game.md) and [What a game engine is](../start/what-an-engine-is.md) first. A reader who used Unity, Unreal or Godot may add [Coming from Unity, Unreal or Godot](../start/coming-from.md).

| Door | Track | For | Starts with | Ends with |
| --- | --- | --- | --- | --- |
| Make a game | G | A person who wants to finish games in the editor | [A tour of the editor](../make/editor-tour.md) | [Project: a third-person platformer](../make/project-platformer.md) |
| Learn from zero | B | A person who has never written a program | [A tour of the editor](../make/editor-tour.md) | [Threads, atomics and races](../basics/threads.md) |
| Understand an engine | E | A person who wrote small programs and wants to see how an engine works | [How a computer runs a program](../basics/computer.md) | `capstone/land` |

Track G steps into the C++ primers after Your first script and comes back to build games. Track E reads the primers first, then the architecture of the engine, then every layer in turn, and it never reads the pages for game makers.

Track B ends early on purpose: it stops after its last primer, and there the reader chooses. Track G continues from [The math of moving things](../make/gameplay-math.md). Track E continues from [How Strata is put together](../core/map.md). Track G is open to a beginner already after [Project: Coin Run, a first finished game](../make/project-coin-run.md), for a reader who wants games first and the rest of the primers later.

## What Strata's choice cannot do

Strata gives you no visual scripting, so no reader can finish a game without typing C++. It needs a C++ compiler and CMake on your computer. It needs a GPU with a Vulkan 1.2 driver, so a computer without one cannot show the editor. And it is a 3D engine for the desktop platforms named above.

## Common mistakes

- **Taking the editor for the whole engine.** Symptom: you search for the game's rules inside the editor and find only a viewport. Fix: the editor makes the game and runs it for testing; an exported game runs in `StrataRuntime`, a second program, without the editor.
- **Waiting for a graph of boxes.** Symptom: you search the menus for a way to wire rules together. Fix: write a script class in C++; the book teaches it step by step.
- **Choosing track E first as a beginner.** Symptom: the first page after the start assumes you can read a short program. Fix: take track B, and move to track E from the page where B ends.
- **Letting an agent replace the learning.** Symptom: the agent builds a game that you cannot change. Fix: read the pages for the step it takes, so that you can check its work.

## Summary

- Strata is a 3D game engine. Its editor is the program in which you make a game, lay out its levels and play it. An AI agent can drive the editor through the same commands as your clicks.
- Game logic is C++ code that the editor builds for you, and Strata has no visual scripting.
- Track G makes games, track B starts from zero, and track E studies the engine; each has a first and a last page.
- Track B continues at `make/gameplay-math` on track G or at `core/map` on track E.

## Check yourself

1. Which sentence describes the editor?

   - A. The library that draws each frame.
   - B. The program in which a game is made and played.
   - C. The program that a player runs to play an exported game.
   - D. A graph of boxes that holds the game's rules.

   :::answer{tests="what-strata-is"}
   B. Option A describes the engine. Option C describes `StrataRuntime`. Option D describes visual scripting, which Strata does not have.
   :::

2. A friend asks how to wire the coin rule together as boxes and lines in Strata. What do you answer?

   :::answer{tests="game-logic"}
   Strata has no visual scripting. You write the rule as C++ in a script class, and the editor builds it. The book teaches the C++ from zero on tracks G and B.
   :::

3. A reader finished Project: Coin Run and wants to make more games before reading the other primers. Where does the reader continue?

   :::answer{tests="beginner-path"}
   Track G is open to a beginner after Project: Coin Run, so the reader continues with `make/gameplay-math`. The reader may return to the other primers later.
   :::

4. A beginner reads track B to its last page and wants to learn how the engine works. Which page comes next?

   :::answer{tests="beginner-path"}
   The next page is `core/map`, the first page of the engine's architecture on track E.
   :::

5. A reader wrote a few small programs and wants to see how an engine draws a picture. Which track fits, and which page comes first after the shared start?

   :::answer{tests="choose-track"}
   Track E fits. Its first page after the start is `basics/computer`, where the reader can use a Test out box to skip what is known.
   :::

## Exercises

1. **Basic.** Three readers write to you. The first wants to make a small game for friends, the second has never written a program, and the third wrote small programs and wants to know how an engine draws its pictures. For each, name the track and the pages it starts and ends with after the shared start pages. Then say where the second reader continues.

   :::answer[Worked solution]{tests="choose-track,beginner-path"}
   The first reader wants to make a game: track G, from `make/editor-tour` to `make/project-platformer`. The second starts from zero: track B, from `make/editor-tour` to `basics/threads`. The third wants to understand an engine and can already read a short program: track E, from `basics/computer` to `capstone/land`. The second reader continues on track G from `make/gameplay-math` or on track E from `core/map`. Track G is open to that reader already after `make/project-coin-run`.
   :::

## Where it lives in Strata

- The programs: `StrataEditor`, `StrataRuntime` and `StrataCLI` stand in the folder of a release, beside `Samples/`.
- The launcher: its heading **Start something new**, the buttons **New Project** and **Open Project...**, and the template and sample cards. **File ▸ Show Launcher** returns to it while no project is open.
- The export: **File ▸ Export Game...** builds the game that `StrataRuntime` plays.
- The samples: `Samples/Samples.json` lists their names and descriptions.
- The code: `StrataEditor/src/Panels/WelcomePanel.cpp` draws the launcher, and `Docs/Releases/PackageReadme.md` holds the first text that a release shows.

## Further reading

- Epic Games, "Blueprints Visual Scripting" in the Unreal Engine documentation: what visual scripting looks like in the best known engine that has it (beginner).
- Jason Gregory, "Game Engine Architecture": the parts of an engine and how they fit (advanced).
- Robert Nystrom, "Game Programming Patterns": short chapters on how game code is organized, free to read online (intermediate).

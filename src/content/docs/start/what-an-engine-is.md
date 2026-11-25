---
id: start/what-an-engine-is
title: "What a game engine is: one frame, start to finish"
description: "What happens in one frame of a game, how frame time and delta time work, and what the engine, editor, runtime and game each are."
kind: concept
size: L
tracks: [G, E, B]
needs: [start/first-game]
time: 60
learn:
  - id: frame-map
    text: trace one frame of a game from the input to the picture on the screen
  - id: frame-time
    text: compute the frame time from a frame rate, and the frame rate from a frame time
  - id: delta-time
    text: explain why the Spinner script multiplies its turn by deltaTime
  - id: engine-parts
    text: name what the engine, the editor, the runtime and the game each are
status: final
---

In [your first game](../start/first-game.md) you pressed **Play** and then took your hands away from the keyboard and
the mouse. Nobody touched anything, and still the scene changed. A cube fell, landed on the ramp and slid down it, and
the cube with your `Spinner` script turned in place without stopping.

The six pictures below show that kind of scene ten frames apart, which at 60 pictures a second is one sixth of a
second. Their cube is orange so that it stands out; yours was pale grey.

::figure{id=cube-frame-0}

::figure{id=cube-frame-10}

::figure{id=cube-frame-20}

::figure{id=cube-frame-30}

::figure{id=cube-frame-40}

::figure{id=cube-frame-50}

One after another, the cube is lower in each picture, then it lands and slides. Your screen never showed a moving
cube. It showed one still picture after another, about sixty each second, and your eyes joined them into motion, as
they do with a film.

So a game must make a new picture many times a second, and each picture must show the world a little later than the
one before. This page explains how a program does that, and in what order the work of one picture happens in Strata.

Most of that work is the same in every game, so it lives in a shared part. A **game engine** is the part of a game
program that every game shares: the loop, the drawing, physics, sound, input and the loading of files. The end of this
page sets it apart from the game, the editor and the program that plays a finished game.

## A program that waits for clicks cannot run a game

Think of a word processor. When you open it, it draws its window and then waits. Nothing on the screen changes until
you press a key or click. Then it does the one thing you asked, draws the change and waits again. While you read, it
uses almost none of the computer's time.

Most programs on your computer work this way, and rightly so. A letter does not change while you
look away from it.

Now try to make the falling cube with such a program. The program draws the cube high above the ramp and waits for
input. You touch nothing, so the cube hangs in the air forever. When you finally move the mouse, the program wakes up,
moves the cube a little and waits again. The cube falls only while you wiggle the mouse, and stops when you stop.

A second try: wake up on every input and also once in a while. That still fails. In a game, most of the change has no
input behind it at all. Gravity pulls the cube, a door closes after ten seconds, an enemy walks its path, and the clock
itself is the reason things move. A program that waits for you cannot keep a world like that going.

The answer is to stop waiting. The program must run its work again and again, as fast as it usefully can, and treat
what you did since last time as one of the many things it reads.

## A game is a loop, and one pass of it is a frame

Here is the shape of every game, written in plain words instead of a :term[programming language]{id=programming-language}:

```text
repeat until the game closes:
    read what the player did since the last pass
    change the game: move things, apply rules, play sounds
    draw a picture of the game as it is now
    show the picture on the screen
```

Each pass reads the input, changes the world by a little, and ends with a new picture on the screen.

A **game loop** is the part of a game program that repeats these steps until the game closes.

One pass of the loop has a name of its own. A **frame** is one pass of the game's main loop: it reads the input,
changes the game, draws one picture and shows it. The word comes from film, where a frame is one picture on the strip.

```mermaid caption="Every frame does the same four things in the same order, then the next frame starts." alt="Four boxes in a row joined by arrows: read the input, change the game, draw a picture, show it. An arrow from the last box returns to the first."
flowchart LR
    A["Read the input"] --> B["Change the game"]
    B --> C["Draw a picture"]
    C --> D["Show it"]
    D -->|"next frame"| A
```

Everything a game does happens inside one of these four boxes, once per frame.

:::analogy[A flip book]
A flip book holds a drawing on each page, each a little different from the one before. When you let the pages run
under your thumb, the drawings seem to move. A game is a flip book whose pages are drawn one at a time, a moment before
you see each one.

**Where it breaks:** the pages of a flip book were all drawn before you opened it, so they cannot change. A game draws
each page from the state of the world at that moment, so what you press now changes the next page.
:::

How many frames happen each second matters a great deal. The **frame rate** is the number of frames a game shows each
second, written in [frames per second](../core/frame-loop.md) (FPS). Films show 24 frames a second. Most computer screens show 60 new pictures a
second, and many newer ones show 120 or 144. A game that matches such a screen gives it a new picture each time the
screen is ready for one.

## Frame time is what adds up

The frame rate counts frames. The work, though, happens inside each frame, and for the work you need the other side of
the same number. The **frame time** is how long one frame takes, from its start to the start of the next one.

Frame times are short, so they need a small unit. A **millisecond** (ms) is a second divided into 1,000 equal parts.

Here is how to get one from the other. A second holds 1,000 of them. At 60 frames a second, those 1,000 are shared by
60 frames, so each frame gets 1,000 divided by 60. That is about 16.7 ms, which is
100 % of a frame at 60 frames a second.

:::note[The formula]
The frame time is a thousand divided by the frame rate, and the frame rate is a thousand divided by the frame time:

$$
t = \frac{1000}{f} \qquad f = \frac{1000}{t}
$$

$t$ is the frame time, in ms. $f$ is the frame rate, in frames per second. Read the first as "t equals one thousand
divided by f". Check it at a limit: a game that showed one frame a second would give each frame the whole second.
:::

The table holds the frame rates you will meet most often. The last column is the frame time as a share of a frame at
60 frames a second, which is the usual budget.

| Frame rate (frames a second) | Frame time | Share of a frame at 60 |
| --- | --- | --- |
| 20 | 50.0 ms | 300 % |
| 30 | 33.3 ms | 200 % |
| 50 | 20.0 ms | 120 % |
| 60 | 16.7 ms | 100 % |
| 120 | 8.3 ms | 50 % |
| 144 | 6.9 ms | 42 % |

Read the table from the top down. Each step down the column of frame rates shortens the frame, but the steps do not
shorten it by the same amount. Going from 20 to 30 frames a second saves far more time than going from 120 to 144.

Why does that matter? Because the work of a game is measured in time. Drawing the shadows might take 2 ms of each frame,
12 % of a frame at 60 frames a second, and that cost is the same whatever the frame rate. Costs in time add up:
shadows, plus physics, plus scripts, give the frame time. Costs in frame rate do not add up at all.

:::example[A drop of ten frames a second]
Two players each lose ten frames a second after a new feature lands. The first goes from 60 to 50 frames a second, the
second from 30 to 20. Which one did the feature cost more?

Work it out in frame time. For the first player, 60 frames a second is 16.7 ms a frame and 50 is 20.0 ms, so the
feature added 3.3 ms, 20 % of a frame at 60 frames a second.

For the second player, 30 frames a second is 33.3 ms, 200 % of a frame at 60, and 20 is 50.0 ms, 300 % of one. The
same drop of ten frames added 16.7 ms,
100 % of a frame at 60 frames a second.

The same "minus ten" hides a cost five times larger on the slower computer. Compare frame times, never differences of
frame rate.
:::

Frame times also show something that an average frame rate hides. A **hitch** is one frame that takes far longer than
the frames around it, so that the motion visibly jumps. Say a game runs at a steady 16.7 ms a frame, 100 % of a frame
at 60 frames a second, and then one frame takes 100 ms, 600 % of one. Over that second the average still reads about
55 frames a second, which sounds fine.

On the screen, though, the game froze for a tenth of a second and then everything jumped ahead. Loading a large file
in the middle of play is a common cause.

## Delta time keeps the speed the same at any frame rate

Frames are not all the same length, and computers do not all run games at the same frame rate. That raises a question
for anything that moves. How far should the cube turn in one frame?

The newcomer's answer is a fixed amount: turn 1.5 degrees every frame. At 60 frames a second, that gives 60 times 1.5,
or 90 degrees a second, which looks right on the computer where you tried it.

Now run the same game elsewhere. At 30 frames a second, 30 times 1.5 is 45 degrees a second: the cube turns at half
speed. At 144 frames a second, 144 times 1.5 is 216 degrees a second: more than twice as fast. Each player sees a
different game, and a hitch makes the cube pause, because a long frame still turns it only 1.5 degrees.

The fix is to give each frame the time it covers. **Delta time** is the time, in seconds, that has passed since the
previous frame began; the game multiplies every speed by it, so that motion depends on time instead of on the number
of frames. ("Delta" is a Greek letter that mathematics uses for "the change in".)

:::question[I cannot read C++ yet. Do I need to, for the next box?]
No: read only the line the text after it points to. Types and variables start in [Programming 1](../basics/programming-1.md), functions in [Programming 2](../basics/programming-2.md), classes in [Programming 3](../basics/programming-3.md) and their [virtual functions](../basics/cpp-classes.md) in [C++ classes](../basics/cpp-classes.md).
:::

Your `Spinner` script does exactly this. Here is the part of it that runs every frame; search for the place where
`DegreesPerSecond` meets `deltaTime`:

```cpp src="StrataEditor/src/Editor/ScriptProject.cpp#L244-L251"
float DegreesPerSecond = 90.0f; // A field: editable per entity, kept across hot reloads

void OnUpdate(float deltaTime) override
{
	TransformComponent transform = GetTransform();
	const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
	transform.SetRotation(turn * transform.GetRotation());
}
```

The field `DegreesPerSecond` holds a speed, 90 unless you changed it. Each frame, `OnUpdate` receives `deltaTime`,
the seconds since the previous frame, and multiplies the two. The result is the angle for this frame only, in degrees.
The rest of that line and the line after it turn the cube by that angle around the upward axis.

Work the numbers for three frame rates. At 60 frames a second, `deltaTime` is $1/60$ of a second, so each frame
turns the cube by 90 times 1/60, that is 1.5 degrees, and 60 frames give 90 degrees. At 30 frames a second, each frame
turns it by 90 times 1/30, 3 degrees, and 30 frames give 90 degrees again. At 144 frames a second, each frame turns it
0.625 degrees, and 144 of those also make 90.

The check works at any frame rate, because the frames of one second always add up to one second. Whatever the
computer, the cube turns 90 degrees a second. A long frame now turns the cube further, by exactly the time it took, so
after a hitch the cube is where it should be.

:::note[A cap on long frames]
A frame can last very long when the computer stops the game, for example while you drag its window. Strata never
gives a frame more than a quarter of a second as its [delta time](../core/time.md) (`ApplicationSpecification::MaxTimestep`, 0.25 s).
A pause of ten seconds therefore does not make the world jump ten seconds ahead.
:::

## One frame of your game, in Strata's order

You now know what a frame does in general. Here is what Strata does in one frame of your game while it plays in the
editor, in the order it does it. The diagram is the map; the list after it explains each box.

```mermaid caption="One frame of your game in the order Strata runs it, from the keys you press to the picture on the screen." alt="Six numbered boxes in a row, joined by arrows. They read: input, scripts and animation, physics in equal steps, late updates and sound, drawing, showing the picture. A dashed arrow returns from the last box to the first."
flowchart LR
    A["1. Read the input"] --> B["2. Scripts update, animation"]
    B --> C["3. Physics in equal steps"]
    C --> D["4. Late updates, sound"]
    D --> E["5. Draw the picture"]
    E --> F["6. Show the picture"]
    F -.->|"next frame"| A
```

1. **Read the input.** Strata collects what the keyboard, the mouse and any game controller did since the last frame,
   and turns it into the project's [input actions](../input/actions.md), such as "jump" or "move left". Everything later in the frame reads
   this one snapshot, so all of the frame agrees on what you pressed.
2. **The scripts update, then the animation.** Each script's `OnUpdate` runs with the frame's `deltaTime`; your
   `Spinner` turns its cube here. Then characters' animations move their bodies to this frame's pose.
3. **Physics, in small equal steps.** Physics is the part that makes things fall, slide and collide. It does not move by
   the frame's time; it moves in steps of one fixed length, by default $1/60$ of a second, the
   [fixed step](../core/time.md). A frame runs as many whole steps as the time since the last one holds: zero, one or
   several, so that physics behaves the same at every frame rate. Your falling cube moves here.
4. **The late updates and the sound.** Scripts get a second call, `OnLateUpdate`, after everything has moved, for work
   such as a camera that follows the player. Then the sound places its sources and its listener where things now are.
5. **Draw the picture.** The engine's drawing part turns the scene into a picture, with most of the work done by the
   :term[graphics processing unit]{id=gpu} (GPU). In the editor, the running game is drawn into the
   [Game view](../editor/play-mode.md), the panel that shows what a player sees, while the editor draws its other panels.
6. **Show the picture.** The finished picture goes to the screen, and the next frame begins.

The order matters. Input comes first, so the scripts see this frame's keys. Physics comes after the scripts, so it moves
what the scripts asked to move. Sound comes after physics, so the bump of a landing cube sounds from where the cube came to rest,
not from where it was. Drawing comes last, so the picture shows the world after every change of the frame.

:::simplified
The map omits work that does not change your game's picture. Examples are tasks queued for the main loop, the game's
own on-screen buttons, the streaming of large worlds and the tidying of positions after the steps. The full order,
with every hook, is in [the frame loop](../core/frame-loop.md). A script's view of the same frame is in
[the script loop](../make/script-loop.md).
:::

### Box 5 in three words: renderer, pixel, shader

Box 5 has words of its own, and you will meet them on every page about pictures.

A **renderer** is the part of an engine that turns the scene into a picture on the screen.

The picture is a grid of tiny dots. A **pixel** is one dot of that grid, with one colour; a screen of 1920 by 1080
holds about two million of them.

The GPU colours those dots with small programs of its own. A **shader** is a small program that the GPU runs for many
pixels, or many corners of shapes, at the same time.

Your first game showed every box at work. The `Spinner` ran in box 2 and the falling cube moved in box 3. Each of the
six pictures at the top of this page came out of boxes 5 and 6 of a different frame. The renderer's own work inside box
5 has many stages of its own; [a tour of one frame on the GPU](../gpu/frame-tour.md) follows them in order.

## Two workers share each frame: the processor and the GPU

Boxes 1 to 4 happen on one part of the computer, and most of box 5 on another. The GPU, as you met it in
[installing Strata](../start/install.md), is the part of a computer that draws pictures. The rest of the work runs on
[the processor, the part of a computer that runs a program's instructions one after another](../basics/computer.md).

If the two took turns, each would sit idle half of the time. The processor would prepare a frame and then wait while
the GPU drew it; the GPU would then wait while the processor prepared the next one. Strata keeps both busy instead.
While the GPU draws frame 1, the processor already prepares frame 2.

```mermaid caption="The processor prepares each frame one frame ahead of the GPU, so both work at the same time." alt="A chart of time with two rows. The processor row holds frame 1, frame 2 and frame 3 one after another. The GPU row starts one frame later and holds frame 1 and frame 2, each below the processor's next frame."
gantt
    dateFormat X
    axisFormat %L
    section Processor
    Prepares frame 1 :p1, 0, 10
    Prepares frame 2 :p2, 10, 20
    Prepares frame 3 :p3, 20, 30
    section GPU
    Draws frame 1 :g1, 10, 20
    Draws frame 2 :g2, 20, 30
```

Each column of the chart holds two frames at once: the processor works on the next one while the GPU draws the one
before. Strata lets at most two frames be under way at the same time by default (`MaxFramesInFlight` in
`GraphicsDevice.h`). If the processor gets too far ahead, it waits for the GPU. How the two keep track of each other is
explained in [how a GPU frame works](../gpu/how-a-gpu-frame-works.md).

### What the frame pill measures

The status bar at the bottom of the editor holds a small rounded label called the frame pill. It reads something like
**4.0 ms · 60 FPS · 0 jobs**, where 4.0 ms is 24 % of a frame at 60 frames a second. With the two workers in mind, you
can read it correctly.

The first number is the processor's work in a frame: how long boxes 1 to 5 took, without the time the frame spent
waiting for the GPU or the screen. A slower processor makes that number larger. The second is the frame rate, how many pictures reached the screen in the last
moments. The third counts tasks waiting for or running on the helper threads, the extra workers that do work in the
background, such as loading files; [jobs](../core/jobs.md) explains them, and you do not need them here.

:::example[4 ms at 60 frames a second]
Say the pill reads 4.0 ms and 60 FPS, which is 24 % of a frame at 60 frames a second. A frame at that rate lasts
16.7 ms, the whole 100 %, yet the work took only 24 % of it.

The difference is waiting. Your screen shows a new picture 60 times a second, and Strata asks to send pictures in step
with it, so a frame that finishes early waits for the screen's next turn. Here each frame worked for 4.0 ms and waited
about 12.7 ms, 76 % of a frame at 60 frames a second.

So 4 ms at 60 FPS, 24 % of a frame at 60 frames a second, is no contradiction. The frame rate tells you how often
pictures appear. The ms tell you how much of each frame the work used, and so how much room is left for more. How a
game keeps in step with the screen is explained in [the frame loop](../core/frame-loop.md), with the rest of frame
pacing.
:::

The pill can add a fourth word, **idle**. When nothing has happened for half a second (no input, no game playing, no
loading), the editor draws only 30 pictures a second, and 10 while you work in another program's window. It returns to the
full rate as soon as you touch something. Idle frames save power; they say nothing about how fast your game is.
[Profiling](../core/profiling.md) teaches how to measure a frame properly.

## The engine is the part every game shares

Look at the six boxes again and ask which of them are about your game in particular. Almost none are. Every game reads
input, runs scripts, steps physics, plays sound, draws pictures and shows them. Every game also loads files from the
disk and keeps its world in scenes. Writing that again for each game would be a great waste.

That shared part is the game engine you met at the top of the page, and your game is what sits on top of it.

The files the engine loads have a name of their own. An **asset** is a file the game uses, such as a model, a picture
for a surface, a sound or a scene. A scene is one place of the game, with the things in it.

The editor is the program you have used so far, with its panels, menus and **Play** button. When you press **Play**,
the editor runs the engine's loop on a copy of your scene, so you can try the game without leaving it.
[The editor as a program](../editor/program.md) explains why the editor and the game are separate programs.

Players never see the editor, so your game must reach them another way. To **export** a game is to turn its project
into a folder that players can run without the editor. **File ▸ Export Game...** writes that folder.

A program in that folder plays the game. The **runtime** is the program that plays an exported game: it runs the same
engine loop as the editor, without the editor's panels. Strata copies `StrataRuntime` into the folder under your
game's name, next to your game's scenes, assets and scripts. Players then start a program named after your game.

Four words get confused all the time, so here they are side by side.

| Part | What it is | In Strata |
| --- | --- | --- |
| The engine | The shared part: loop, drawing, physics, sound, input, assets, scenes | The library in the `Strata/` folder |
| The game | Your scenes, your assets and your scripts | Your project's folder |
| The editor | The program in which you make the game | `StrataEditor` |
| The runtime | The program that plays an exported game | `StrataRuntime`, copied under the game's name |

So when you made your first game, you did not change the engine at all. You added assets and scripts to a project, and
the engine, the same for every Strata game, ran them. [The map of Strata](../core/map.md) shows how the engine itself
is divided into parts, and [what a world is](../world/what-a-world-is.md) shows how an engine keeps a scene.

## How engines are made and shared

Every game needs the six boxes, and people have found several ways to get them. Each way below answers the weakness of
the one before.

The oldest way is to write everything for each game. You control every detail, but the next game starts again from the
first line, and most of the work repeats.

So studios keep their work and use it again: an in-house engine is one a studio builds for its own games. Large studios,
such as Electronic Arts, work this way. The weakness is the price: such an engine takes a large team years, and
nobody outside the studio can use it.

So companies build general engines with an editor and offer them to everyone, often for free at first. One engine then
serves thousands of games. The weakness is that the engine is large and works in its own way. It also comes with a
licence, the terms under which you may use it, and those terms may claim a share of what your game earns.

Some people want a smaller, open engine that they program directly. A code-first engine is a library with no editor:
you build scenes in code. Its weakness is that a level designer or an artist who does not program cannot work in it
alone.

| Engine | Kind | Game code in | Editor | Platforms | Licence |
| --- | --- | --- | --- | --- | --- |
| Unreal Engine | General, with an editor | C++, and Blueprints (boxes joined by wires) | Yes | Desktop, consoles, phones | Source open to its users; free until a game earns \$1 million, then 5 % of its revenue above that |
| Unity | General, with an editor | C# | Yes | Desktop, consoles, phones, the web | Closed source; free below a revenue limit, paid plans above it |
| Godot | General, with an editor | GDScript, C#, C++ | Yes | Desktop, phones, the web; consoles through other companies | Open source; any use, with its notice kept |
| Bevy | Code-first | Rust | No official editor | Desktop, the web, phones in part | Open source; any use, with its notice kept |
| In-house engines | Built by a studio for its own games | Mostly C++, often with a script language of the studio's own | The studio's own tools | What the studio ships on | Not offered to others |
| Strata | General, with an editor | C++ [script modules](../make/first-script.md) | Yes, `StrataEditor` | Windows, Linux, macOS | No licence file; `ThirdPartyNotices.md` lists the licences of the parts it contains |

Strata belongs to the third kind: a general engine with an editor. It differs from the others in what it is built
for. Every action of its editor is a command that a person, a script or an agent can run the same way. An
[agent](../automation/agents.md) is a program that uses artificial intelligence to do a task on its own, and
Strata's sample games were made by one through the editor. Strata's words for what other engines
call by other names are in [coming from another engine](../start/coming-from.md).

## Strata's choice: C++, an editor, and the same commands for everyone

Strata makes three choices that shape everything else, and each has a page that teaches it.

First, Strata is an engine written in C++ with an editor, for Windows, Linux and macOS. C++ is the language most large
engines are written in, because it lets a program control exactly how it uses memory and time, and it runs fast.

Second, game code lives in C++ script modules kept outside the engine. A script module is your project's scripts built
into a file of their own, which the engine loads. Because the engine holds that file at arm's length, a crash in your
script stops your game but not the editor, and you can change a script and build it again while the game plays.
[Why scripts](../scripting/why-scripts.md) explains how.

Third, every editor action is a command. A command is a named action of the editor with written inputs, such as
`play.start`, and the editor's buttons and menus run commands too. A person at the editor, a script of commands and an
agent all use the same commands, and get the same results. [Editor commands](../editor/commands.md) teaches them.

:::why[Why write game code in C++ when other engines offer easier languages?]
Strata's scripts are written in the same language as the engine, so one set of tools builds and checks both. A script
becomes the processor's own instructions, as the engine does, so it runs fast. Keeping the scripts in a module of their own costs a little: everything they
receive from the engine crosses a narrow, fixed doorway of plain data. In return, a broken script cannot take the
editor down with it, and your changes take effect while the game keeps running. The price for you is the language: C++
asks more care of a beginner than C# or a visual language does.
:::

The frame you followed on this page runs the same way in every Strata program. [The frame loop](../core/frame-loop.md)
shows the code of the loop, and [the map of Strata](../core/map.md) shows which programs and libraries the engine is
built from.

## What Strata's choice cannot do

Strata makes games for desktop computers only. It runs on Windows, Linux and macOS, and a game exported on one of
them runs on that same system. It cannot make games for phones, game consoles or web browsers; [platforms](../core/platform.md)
explains what a new system would need.

Strata has no networking for games: it offers nothing to keep the worlds of several players on different computers in
step, so a game played over a network is beyond it. [Networking](../appendix/networking.md) explains what such a game
would need.

C++ also limits who can write the game code. A designer who wants to change a rule writes C++ or asks someone who can;
there is no visual language of boxes and wires. The full list of what Strata omits is in
[not in Strata](../appendix/not-in-strata.md).

## Common mistakes

- **Taking the editor for the engine, or for the game.** The symptom: you expect players to need the editor, or you
  search for your game's rules inside the editor's menus. The fix: the engine is the shared part, the editor is the
  program for making, and the game is your project's scenes, assets and scripts, which the runtime plays after export.
- **Moving by a fixed amount each frame.** The symptom: the game runs faster on a fast computer, slower on a slow one,
  and pauses at every hitch. The fix: multiply every speed by the frame's `deltaTime`, as `Spinner` does.
- **Reading differences of frame rate as costs.** The symptom: "it only lost ten frames a second" hides a cost that
  is five times larger on a slower computer. The fix: turn both frame rates into frame times and compare those.
- **Expecting to change engine files to make a game.** The symptom: you search the engine's source for a place to add
  your game,
  and every update of the engine undoes your work. The fix: a game lives in its project, as scenes, assets and scripts;
  the engine stays the same for every game.

## Summary

- One frame reads the input, runs the scripts and the animation, steps physics zero or more times, runs the late
  updates and the sound, draws the picture and shows it. The processor prepares the next frame while the GPU draws.
- The frame time in ms is a thousand divided by the frame rate, and the frame rate is a thousand divided by the frame
  time; costs add up in ms, not in frames a second.
- `Spinner` multiplies its speed by `deltaTime` so that the cube turns by the same angle each second at any frame
  rate.
- The engine is the part every game shares, the editor is the program for making games, the runtime plays exported
  games, and the game is its scenes, assets and scripts.

## Check yourself

1. A friend says: "My game dropped from 60 to 50 frames a second, and yours from 30 to 20. We lost the same." Which
   statement is right?

   - A. You both lost the same: ten frames a second each.
   - B. Your loss cost more time per frame: 16.7 ms against 3.3 ms, 100 % against 20 % of a frame at 60.
   - C. Your friend's loss cost more, because 60 is a higher frame rate.

   :::answer{tests="frame-time"}
   B. From 60 to 50 frames a second, the frame time goes from 16.7 ms to 20.0 ms, adding 3.3 ms, 20 % of a frame at
   60 frames a second. From 30 to 20, it goes from 33.3 ms to 50.0 ms, adding 16.7 ms, 100 % of a frame at 60. A reads
   a difference of frame rate as a cost, the page's third common mistake. C has it backwards: the same drop costs less
   time at a high frame rate.
   :::

2. A script moves a car 0.5 m every frame, without `deltaTime`. How far does the car move in one second at 60 frames a
   second, and at 120?

   :::answer{tests="delta-time"}
   At 60 frames a second, 60 times 0.5 m is 30 m. At 120, it is 60 m: the car is twice as fast on the faster computer.
   Moving at 30 m a second times `deltaTime` gives 30 m in a second at both frame rates.
   :::

3. Put these in the order Strata runs them in one frame: the sound places its sources; your `Spinner` turns its cube;
   the picture is shown; physics steps; the keyboard is read; the scene is drawn.

   :::answer{tests="frame-map"}
   The keyboard is read; `Spinner` turns its cube; physics steps; the sound places its sources; the scene is drawn; the
   picture is shown. The input comes first so that the scripts see it, physics moves what the scripts changed, the
   sound follows what moved, and drawing comes last so the picture shows every change.
   :::

4. Your friend sends you an exported game. Which of these do you need to play it?

   - A. The editor, to open the project.
   - B. Only the exported folder, whose program is the runtime under the game's name.
   - C. The engine's source code, to build the game first.

   :::answer{tests="engine-parts"}
   B. Export puts the runtime, named after the game, in a folder with the game's scenes, assets and scripts; that
   program plays the game. A takes the editor for the game: the editor is only for making it. C expects the game to
   live in the engine's files, the last common mistake.
   :::

5. The frame pill reads 3.0 ms, 18 % of a frame at 60 frames a second, and 120 FPS. How much of each frame does the
   work use, and what does the frame do with the rest?

   :::answer{tests="frame-time frame-map"}
   At 120 frames a second a frame lasts 8.3 ms, 50 % of a frame at 60 frames a second. The work uses 3.0 ms, 18 % of
   a frame at 60, so the frame waits about 5.3 ms, 32 % of a frame at 60, for the screen's next picture.
   :::

## Exercises

1. **Basic.** Compute the frame time at 120 and at 25 frames a second. Then compute the frame rate of frames that
   take 8 ms and 40 ms, 48 % and 240 % of a frame at 60 frames a second.

   :::answer[Worked solution]{tests="frame-time"}
   The frame time is 1,000 divided by the frame rate.

   - At 120 frames a second: 1,000 divided by 120 is 8.3 ms, 50 % of a frame at 60 frames a second.
   - At 25 frames a second: 1,000 divided by 25 is 40.0 ms, 240 % of a frame at 60 frames a second.

   The frame rate is 1,000 divided by the frame time.

   - Frames of 8 ms, 48 % of a frame at 60 frames a second: 1,000 divided by 8 is 125 frames a second.
   - Frames of 40 ms, 240 % of a frame at 60 frames a second: 1,000 divided by 40 is 25 frames a second.

   Check: 25 frames a second and 40 ms, 240 % of a frame at 60, belong together both ways, as the formula says they
   must.
   :::

2. **Medium.** Open your copy of the `Tetris` sample (**Open Sample...** in the launcher, or **File ▸ Open Sample ▸ Tetris**, makes one if
   you have none).
   Press **Play**, play for a few seconds and write down the two first numbers of the frame pill. Press **Stop** (or
   **Ctrl+P** again) to stop, take your hands away for a second and write them down again.

   Why can the ms of the pill be far fewer than 1,000 divided by the frame rate, and what does **idle** mean? The
   pill's last number counts tasks of the helper threads that [jobs](../core/jobs.md) explains; this exercise does not
   need it.

   :::answer[Worked solution]{tests="frame-time frame-map" solution="tutorials/start/what-an-engine-is/exercise-2.tutorial.json"}
   Your numbers depend on your computer and your screen; the reasoning does not.

   1. While the game plays, the frame rate matches your screen, for example 60 FPS. A frame at that rate lasts 1,000
      divided by 60, 16.7 ms, 100 % of a frame at 60 frames a second.
   2. The pill's first number is only the work of the frame, a small part of the frame for a game as small as
      `Tetris`. The rest of each frame is waiting for the screen's next picture, which is how the editor keeps in step
      with the screen.
   3. After you stop and take your hands away for half a second, the pill shows **idle** and the frame rate drops to
      30, or 10 while another program's window has the keyboard. Idle means the editor saw no reason to draw at the full
      rate, so it draws less often to save power. The work per frame stays small, and the frame rate says nothing
      about your game.
   4. As soon as you move the mouse over the editor, **idle** disappears and the frame rate returns to the full rate.
   :::

## Where it lives in Strata

- The **Play** button at the top of the editor (**Ctrl+P**): runs the engine's loop on a copy of the scene inside the editor; the
  `play.start` and `play.stop` commands do the same.
- The status bar's frame pill: the work of a frame, the frame rate, the helper threads' tasks and **idle**; clicking it
  opens the **Performance** panel, whose numbers the `editor.perf` command also returns. The word **idle** shows only
  in the pill.
- **File ▸ Preferences...**: the `Editor.FrameRate` section, which sets when the editor counts as idle and how often it
  draws then.
- **File ▸ Export Game...**: writes the folder with the runtime under the game's name.
- **File ▸ Open Sample**: copies a sample game, such as `Tetris`, into a folder of your own (`project.openSample`).
- The `Script` component runs a class such as `Spinner`; the `RigidBody` component makes an entity fall and slide in
  the physics steps.
- **File ▸ Project Settings...**, the `Scene.Timing` section: the length of the fixed step.
- On track E, the code: `Application::Run` in `Strata/src/Strata/Core/Application.cpp` (the loop), `Scene::OnUpdateRuntime`
  in `Strata/src/Strata/Scene/Scene.cpp` (the scene's part of a frame), `EditorLayer::DrawFramePill` in
  `StrataEditor/src/EditorLayer.cpp` and `MaxFramesInFlight` in `Strata/src/Strata/Renderer/GraphicsDevice.h`.

## Further reading

- Robert Nystrom, *Game Programming Patterns*, the chapter "Game Loop" (2014; also free on the author's website): why games loop and the forms a loop takes, with small examples. Beginner.
- [Glenn Fiedler's article on the fixed step](https://gafferongames.com/post/fix_your_timestep/): what goes wrong when a
  game moves by the frame's time, and the fixed step that cures it. Intermediate.
- Jason Gregory, *Game Engine Architecture*, third edition (2018), chapter 1: what an engine is, how its
  parts are layered, and a survey of in-house and general engines. Intermediate to advanced.
- Epic Games, the Unreal Engine End User License Agreement, on the Unreal Engine website: the terms in the survey's
  Unreal row. Beginner.
- [The Unity manual](https://docs.unity3d.com/Manual/index.html): the languages, editor and platforms of the survey's
  Unity row. Beginner.
- [Godot's source code on GitHub](https://github.com/godotengine/godot): its licence file and the platforms it builds
  for. Beginner.
- [Bevy's source code on GitHub](https://github.com/bevyengine/bevy): a code-first engine, its licences and the
  platforms it supports. Intermediate.

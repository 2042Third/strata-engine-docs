---
id: make/designing-a-game
title: "Planning a small game: the core loop, scope, prototype and playtest"
description: "How to turn a big game idea into a small one you can finish: find the core loop, cut the scope, build a grey box and watch people play it."
kind: concept
size: M
tracks: [G]
needs: [make/project-coin-run]
time: 35
learn:
  - id: core-loop
    text: name the core loop of a game by asking what the player does every few seconds
  - id: cut-list
    text: write a cut list that sorts the features of a game into must, should and could
  - id: design-paragraph
    text: write a one-paragraph design for a small game of your own
  - id: playtest
    text: run a playtest with one person and change one thing after it
since: 0.3.0
status: final
---

You finished Coin Run, and the tools of the earlier chapters are in your hands. The next thought is usually "now I make a real game". Take a minute and write the first idea down: an open world with a story, a crafting system, a day and night cycle, a dozen enemies and a map.

Now count what that list needs. Every item is a script, a set of scenes, models, sounds and a menu, and each must work with all the others.

The two games that the next chapters build show the scale of a *finished small* game. The falling-block game has three :term[source files]{id=source-file} of 829 lines and one scene. The platformer, Sky Islands, has 18 source files of 1,720 lines and three scenes. Neither is an open world, and each took a full project to make.

## Why a long plan fails

The usual answer is to write a long document that lists everything, and then to build the list from the top. It breaks in three ways.

- Nothing can be played for weeks, so you cannot tell whether the game is any fun.
- The parts are built before you know which ones matter, so every part is equally precious and nothing can be cut.
- A document describes what you think the game will feel like. Only play shows what it does feel like.

A small game needs the opposite order. Find the smallest thing that is already a game, play it, and add only what the play asks for.

## The core loop is what the player does every few seconds

Ask one question about any game you like: what does the player do over and over, every few seconds? The answer is the **core loop**: the short cycle of action, result and reward that a player repeats for the whole game.

Take the falling-block game. A piece falls, the player moves and turns it, the piece locks, full rows clear, the score rises and gravity grows. Then the next piece falls. Sky Islands has a longer cycle: the player runs and jumps, collects coins, reaches a checkpoint and tries to finish faster. The diagram shows both as cycles.

```mermaid caption="Two core loops drawn as cycles: a falling-block game and a platformer. Each step leads to the next, and the last leads back to the first." alt="Two cycles side by side. The falling-block cycle: a piece falls, the player moves and turns it, it locks, rows clear and the score rises, gravity grows. The platformer cycle: run, jump, collect coins, reach a checkpoint, finish faster."
flowchart LR
    subgraph T["Falling blocks"]
        T1["A piece falls"] --> T2["Move and turn it"]
        T2 --> T3["It locks"]
        T3 --> T4["Rows clear, score rises"]
        T4 --> T5["Gravity grows"]
        T5 --> T1
    end
    subgraph P["Platformer"]
        P1["Run"] --> P2["Jump"]
        P2 --> P3["Collect coins"]
        P3 --> P4["Reach a checkpoint"]
        P4 --> P5["Finish faster"]
        P5 --> P1
    end
```

Look at what both loops share. Each step is something the player does or sees within seconds, and the last step makes the first one slightly different: faster gravity, a better time. That change is what keeps a loop from being a chore. Coin Run has a loop too: roll the ball, collect a coin, watch the clock, and either win or lose and start again.

Everything else in a game either feeds the loop or is optional. A menu does not make the loop fun, and neither does a credits screen. If the loop is not fun with grey boxes and no sound, it will not become fun with art.

## Scope is what you decide to omit

Your first idea held far more than a loop. **Scope** is the amount of game you commit to make: its features, its content and its polish.

You control it with a **cut list**, which sorts every feature into one of three groups.

- **Must:** without it the loop does not exist.
- **Should:** the game works without it, but is worse.
- **Could:** nice to have, and the first to go when time runs short.

The rule is that you build all the "must" items before any "should", and all "should" before any "could". Sky Islands shows the habit. Its description file, `README.md`, lists features that a loop does not need.

There are two point lights that cast shadows, which it calls lanterns, and four reflection probes that bake the look of reflections. There is a Graphics row in the settings menu, and an attract mode that plays the course by itself when nobody touches the menu. These are all "could" items, since the loop of run, jump, coins and flag stands without them.

:::example[A cut list for Coin Run]
Coin Run's one-line idea: roll a ball and collect five coins in 40 seconds. Sort ten features.

| Feature | Group | Reason |
| --- | --- | --- |
| Ball that rolls and jumps | Must | The player's action |
| Five coins that disappear when touched | Must | The reward |
| Win when the last coin goes | Must | The loop needs an end |
| Lose when the clock reaches zero | Must | A game with no loss has no pressure |
| Restart without the editor | Should | Without it a player cannot play twice |
| Counters for coins and seconds | Should | The player can play, but cannot see progress |
| Sound for each coin | Should | Feedback that makes the reward felt |
| A second level | Could | More of the same loop |
| A best-time list | Could | A reason to replay |
| Moving platforms | Could | A new idea, which needs its own testing |

Count the musts: four. A game with only those four is dull but complete, and you can play it today. That is the point of the list.
:::

The two samples give a measure of what "small" means; [the samples page](samples.md) reads them in depth. Keep your first game closer to the falling-block game than to the platformer: three files and one scene.

## Four ways to plan, each answering a flaw of the one before

Game makers use four approaches, in roughly this order. Each is introduced by what the one before cannot tell you.

A **design document** is the written plan: the idea, the rules, the levels and the list of features. It costs only time and fits a team that must agree, but it cannot tell you how the game feels, because nobody plays a document.

A **prototype** is a rough, quick version of the game made to answer one question. The cheapest is a *paper prototype*: cards, dice and pen for the rules of a board-like game. It tests the loop's rules in an hour, with no code, but it cannot test timing, speed or the feel of controls.

A **grey box** is the game built in the engine from plain shapes, with no art: cubes, spheres and planes with default grey materials. It tests the feel of movement and of a level's size, because the player runs, jumps and falls for real. It costs days, not hours, and it says nothing about whether the finished look and content will hold interest.

A **vertical slice** is one small part of the game made to the quality of the finished game: one level with final art, sound and menus. It tests whether the content and the look hold up, and whether you can really produce the whole game at this quality. It costs the most, so a small team builds it after the grey box has proven the loop, never before.

| Approach | Cost | What it tests | Who uses it |
| --- | --- | --- | --- |
| Design document | Days of writing | Whether the team agrees | Studios of any size |
| Paper prototype | Hours | The rules of the loop | Board game and some digital designers |
| Grey box | Days of work | The feel and the level size | Most studios, early in a project |
| Vertical slice | Weeks | The content, the look and the cost of the whole | Studios before a publisher or a big team starts |

For a first small game, use a short design (one paragraph, below), skip the paper step if your game depends on movement, and build a grey box. The slice is what you grow the grey box into, one section at a time.

## One paragraph says what you are building

Every project page of this book opens with the same device: a **one-paragraph design**. It is a few sentences, written before any work, that fix what the game is. It answers five questions: what the player does, what the core loop is, how the game is won and lost, what the controls are, and what you omit.

The description files of the samples show the style. The falling-block game's names seven pieces in a 10 by 20 well, line clears, levels that raise gravity, a ghost piece, a preview of the next piece, pause and game over. The platformer's names the actions: run, jump, push a crate and bounce on jump pads. Its goal is twelve coins and a race to the flag. Physics Playground describes an arena of six stations that you fly through and play with.

:::example[A one-paragraph design]
*Beam Rider.* The player slides a cube along a beam over a pit and collects ten gems before a 30 second clock runs out. The loop is to slide, jump a gap, grab a gem and watch the clock. The player wins by taking all ten gems and loses by falling off or by running out of time; a key restarts the round. The controls are the arrow keys and Space; omitted: a second level, enemies, sound and a menu.

The paragraph holds about 70 words, has all five answers and ends with the cuts. Notice that the last sentence is the most useful one: it tells you what to refuse.
:::

When a new idea arrives during the work, read the paragraph. If the idea is not in it, the idea joins the "could" list.

## A playtest shows what you cannot see

You know your game too well. You know which key does what, where the gap is and what the clock means. A **playtest** is a session in which a person who has not seen the game plays it while you watch. It is the one tool that tells you whether your game is understood and enjoyed.

Follow four rules.

1. Watch, and do not explain. Say only "play it like you would play any game". Every sentence you add hides a problem that a real player would meet alone.
2. Note where the player stops, hesitates, repeats a failure or asks a question. Those moments are the findings. Write them down as they happen, and leave the cause for later.
3. Change one thing. If you fix five things at once, you cannot tell which one helped.
4. Test again, with a new person if you can, since the first one now knows the game.

One person is enough to start. A player who gets lost in the first ten seconds already shows you a flaw. A second player who gets lost in the same place proves it.

Strata has two kinds of play-test, and the words are close. A playtest with a person tests fun and clarity. A play-test that a command script runs tests that the rules still work; [automated play-tests](automated-playtests.md) teaches it. Such a run is exact because the same inputs give the same game, as [play-tests and bugs](play-test-debug.md) shows. The two do not replace each other.

## Strata's way: design the code so that tools can check it

The samples were made by an artificial intelligence (AI) agent through the editor, following the guide of the `strata-make-a-game` skill. Its method fits any game maker, because it also makes your own testing quick.

:::why[Why design the code for checking?]
The skill asks for four habits before any code is written. Rules go in a plain C++ class that makes no engine calls, as in the falling-block game's `TetrisGame` class; a `Script` class handles input, time and drawing. Randomness comes from a seed field, so the same seed gives the same game and a test can plan the moves. Tuning values are fields, so you change them with `script.setField` or in the Inspector while the game plays, with no build. And each meaningful event writes one `Log::Info` line, such as "cleared 1 line; score 209", so a tool or you can read what happened.

The reason is that a machine can check rules and numbers, but cannot see a screen the way you do. The cost is some structure up front: you write the rules class before the first thing moves. The same habits are why a seeded game can be replayed exactly, as the page on play-tests explains. For recipes with seeds, see [recipes](recipes.md).
:::

Follow the fields habit during a playtest. If a player says the jump feels loose, change the jump field while the game plays, ask for another try and watch. Changing a number in code means a build and a restart, and that is a slower loop than the one you are testing.

## What this approach cannot do

A tool can check that a row clears and that a score rises. No tool can check that clearing a row feels good. The playtest stays with people, and Strata offers no shortcut for it. It does not record a player's keys and replay them later either: the journal of the editor repeats editing commands only. Take notes with a pen, or record the screen with a program of your own.

Strata has no block-out tools such as brushes or mesh editing, either. A grey box here is made of the seven :term[built-in meshes]{id=built-in-mesh} (`Cube`, `Sphere`, `Plane`, `Cylinder`, `Capsule`, `Cone` and `Torus`), scaled and placed, or of models you import. The page [what Strata does not do](../appendix/not-in-strata.md) lists the other gaps. Plan a grey box as a few simple shapes, and it will look as it should.

## Common mistakes

- **Scope grows.** Symptom: the "could" list is longer every week and the loop is still not ready to play. Fix: before adding a feature, move something of equal size to the "could" list, or refuse the feature.
- **Polish before the loop works.** Symptom: a lovely level and a jump that nobody likes. Fix: keep the grey box until a stranger plays the loop for five minutes without being asked to stop.
- **Testing only by yourself.** Symptom: "it feels fine", and then a friend cannot find the first coin. Fix: run a playtest with one person, in silence, as soon as the loop moves.
- **Changing numbers in code.** Symptom: each tuning round costs a build and a restart, so you tune less. Fix: make each number a field and change it while the game plays.

## Summary

- The core loop is the cycle a player repeats every few seconds. Find it by asking what the player does, and check that its last step changes the first.
- Scope is what you commit to make. A cut list of must, should and could makes you build the loop first and polish last.
- A one-paragraph design fixes what the player does, the loop, how the game is won and lost, the controls and what you omit.
- A playtest is a person playing while you watch and stay silent. Note where they stop, change one thing and test again.

## Check yourself

1. A friend plays your game and says: "I do not understand what the red cubes are". You answer by explaining the rules. What went wrong in the playtest?

   :::answer{tests="playtest"}
   You explained while the player played, which hides what a real player would meet alone. The red cubes are a finding: note them, say nothing and change one thing, such as their colour or placement, before the next test.
   :::

2. Which of these is the core loop of Coin Run? (a) Menu, options, credits. (b) Roll, collect a coin, watch the clock, win or lose, restart. (c) Install, build, export. (d) A list of five coins.

   :::answer{tests="core-loop"}
   Answer (b). That cycle is what the player does every few seconds, and it returns to the start. Option (a) is optional framing, (c) is the maker's work and (d) is content, not an action.
   :::

3. Sky Islands has an attract mode that plays the course by itself. Which group of a cut list does it belong to, and why?

   :::answer{tests="cut-list"}
   The attract mode is a "could" item. The loop of run, jump, coins and flag works without it, and the sample's description lists it among the extras, not among what the game needs.
   :::

4. Your one-paragraph design has seven sentences about a story and none about how the game is lost. What is missing and what do you do?

   :::answer{tests="design-paragraph"}
   The paragraph must say how the game is won and lost, and what you omit. Cut the story down to one sentence, add a lose condition and add a line of cuts.
   :::

## Exercises

1. **Basic.** Write the core loop of Coin Run as a cycle of at most six steps, then sort its features into must, should and could. Compare your list with the one on this page and say which of your "should" items you would move.

   :::answer[Worked solution]{tests="core-loop cut-list"}
   The cycle: roll the ball, jump to the coin, collect it, watch the clock, win or lose, restart. A good cut list keeps the musts to the four that make a round: the ball, the coins, a win and a loss. The restart and the counters are "should", since a player can still play once without them. A list with more than five musts is a warning: if you cannot play a round with only the musts, one of them is a "should".
   :::

2. **Medium.** Copy your finished Coin Run folder and open the copy, as [project files](project-files.md) describes. Without a Coin Run of your own, download checkpoint 4 at the end of [Ship the finished game](project-coin-run.md#ship-the-finished-game). Its zip holds a folder with `CoinRun.stproj`: open that file with **File ▸ Open Project...**.

   Write a one-paragraph design for a new level with its own core loop. Build the level as a grey box from the built-in meshes; the **+** button of the Hierarchy opens the Create menu. Let one person play it without explanations, change one field or one shape, and let them play again.

   :::answer[Worked solution]{tests="design-paragraph playtest" solution="tutorials/make/designing-a-game/exercise-2.tutorial.json"}
   The solution file builds a small grey box with the command `entity.create`: a floor and a wall, each with a `Builtin/Cube` mesh and a box :term[collider]{id=collider}. `CoinPlacer` still places the coins from its list of positions, `c_CoinPositions` at the top of `Scripts/CoinPlacer.cpp`. Change that list in a text editor to put the coins on the far side of the wall, and build with **Ctrl+B**: the loop becomes roll, jump and collect.

   In the playtest, note where the person stops. The change after it is one number, such as the `TimeLimit` field of `CoinRunGame` in the Inspector (40 seconds), or one wall moved by a metre. The playtest itself needs a person, which no command replaces, as the section on what this approach cannot do says.
   :::

## Where it lives in Strata

- The samples are copied through **Open Sample** in the launcher, or with the command `project.openSample`; the sizes quoted here come from `Samples/Tetris/Scripts/` and `Samples/ThirdPerson/Scripts/`.
- The Hierarchy's **+** button opens the Create menu, which makes the seven shapes with colliders, and a **Mesh only** list makes them without (`StrataEditor/src/Panels/SceneHierarchyPanel.cpp`).
- Commands: `entity.create` places a shape, `script.setField` changes a field while playing, and `log.read` reads the Console's lines.
- The skill `strata-make-a-game` holds the design habits (`.claude/skills/strata-make-a-game/SKILL.md`).

## Further reading

- Jesse Schell, "The Art of Game Design: A Book of Lenses": the lens of the core loop and of playtesting (intermediate).
- Tracy Fullerton, "Game Design Workshop": paper prototypes and playtesting in depth (intermediate).
- Game Developer, articles on the vertical slice and on greyboxing (beginner).

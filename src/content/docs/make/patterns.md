---
id: make/patterns
title: "Patterns for game code: state machines, managers and object pools"
description: "Name the situations of a game, give shared work one owner and keep objects instead of remaking them: four patterns, found in Strata's samples."
kind: concept
size: L
tracks: [G]
needs: [make/timers-events, make/script-fields]
time: 55
learn:
  - id: state-enum
    text: write a scoped enum and a switch that replace a group of flags
  - id: manager-owner
    text: explain how a manager gives shared work one owner and how a script finds it
  - id: pool-reuse
    text: explain why a pool made once costs less than creating and destroying, and what a hidden entity still receives
  - id: pick-pattern
    text: choose the pattern that fits a script that grows
  - id: find-in-samples
    text: name where the samples use each of the four patterns
since: 0.3.0
status: final
---

Picture the Coin Run script after a week of work. At first it moved a ball and counted coins. Then you added a pause
menu, a death, a win panel and a gun. Every new feature needed a new yes-or-no variable: `isPaused`, `isDead`,
`hasWon`, `isShooting`.

Now the player dies while the game is paused, and the win panel opens over the pause menu. Each variable is correct on
its own. Together they describe a situation that your design never allowed, and the game does something strange.
This page shows four habits that keep a script understandable as it grows.

## Three answers that stop working

You already know three ways to add a feature to a script. Each one works for a day, and each one breaks later.

### More flags

A **flag** is a variable that is either true or false. Say a guard in your game needs three flags: `isChasing`,
`isReturning` and `isAlarmed`. Three flags make 2 × 2 × 2 = 8 combinations. The guard has three real situations, so
five combinations mean nothing: what does a guard do that is chasing and returning at once?

Nothing in the code forbids those five. Some line you wrote last week sets one flag and forgets another, and the guard
walks toward you and away from you in the same frame. With five flags the count is 32 combinations, and you cannot
check them by reading.

```pseudocode
if (isChasing)   MoveToward(player);
if (isReturning) MoveToward(home);   // both true: the guard stands still
if (isAlarmed && !isChasing)  PlaySiren();
// Where is isChasing cleared? In three places. Which one is missing?
```

The fence above is not engine code. It is a sketch of the problem: each `if` is a separate question, and no line
says which answers may be true together.

### Searching again for the same thing

Every coin in Coin Run needs the score. The first way to get it is to search for it: each coin asks the scene for the
score display when the ball touches it. That works, and with 12 coins it costs nothing you can measure.

The weakness is not speed. The weakness is that twelve scripts each know how to reach the score, each in a slightly
different way. When you rename the score display or move the score into a new script, you edit twelve places and miss one.

### Creating and destroying everything

A gun fires 4 shots each second, and each bullet lives 1.5 seconds. The simple code creates a bullet when the player
shoots and destroys it when it expires. Over a one-minute fight that is 240 creations and 240 destructions.

Each creation asks the engine to build an entity, give it components and place it in the scene. A modern computer
survives 240 of them, so you may not see a problem on your machine. Do the same for a hundred bullets each second, or
on a weak phone, and the work that you meant for the picture goes into building and erasing objects.

## The idea: name the situations, give each job one owner, keep what you build

All three breaks have one cause: the code says less than the designer knows. The designer knows that a guard is in one
of three situations; the flags say nothing about that. The designer knows that the score has one home; twelve coins
search for it separately. The designer knows that there are never more than ten bullets at once; the code builds as
many as the player fires.

The repair is to write the knowledge down, in three moves. Name each situation and keep only one at a time. Give each
shared job to one script. Build objects once and use them again. Each move has a name that other programmers know, and the
rest of this page builds them from the flags up.

```mermaid caption="The guard's three situations and the moves between them. Only one is true at a time, so no combination of flags can exist." alt="A state diagram with three boxes: patrol, chase and return. An arrow goes from patrol to chase when the player comes near, from chase to return when the player is far, and from return back to patrol when the guard is home."
stateDiagram-v2
    [*] --> Patrol
    Patrol --> Chase: player near
    Chase --> Return: player far
    Return --> Patrol: guard home
```

The diagram is the whole design of the guard. Reading it takes ten seconds, and you can see that Chase never leads
straight to Patrol. The same sentence is hard to find in the flag version.

## A state machine gives every situation one name

A **state machine** is a script that is always in exactly one of a fixed list of named situations, called its
**states**, and that moves from one to another only along rules you write down. The guard's list is Patrol, Chase and
Return. The pattern is described in Robert Nystrom's *Game Programming Patterns*, under State.

### Step one: replace the flags with a scoped enum

You met scoped enums in [Programming 1](../basics/programming-1.md): a type whose values are a short list of names.
The three flags become one variable that holds one of three names. The new variable cannot hold two names at once, so
the five meaningless combinations are gone, not guarded against.

```pseudocode
enum class GuardState { Patrol, Chase, Return };
GuardState m_State = GuardState::Patrol;
```

The second step is a `switch`, which chooses the code to run from the value of the variable. Each `case` is one
state, and the compiler can warn you when a `case` is missing. Here is the guard, written as a small program that
runs on its own, so you can see its numbers. The guard stands on a line at position 0. The player's position changes
each tick, and the guard moves 2 units each tick toward the player while chasing.

The full program is the answer to the first exercise, so it waits there. Its rules are these. In Patrol, the guard
starts to chase when the player is closer than 5 units. In Chase, it stops when the player is farther than 8 units.
In Return, it walks home, and in position 0 it patrols again.

Trace it by hand with the player at 10, then 4, then 4, then 4, then 20. In tick 1 the player is 10 away and nothing
happens. In tick 2 the distance is 4, so the state becomes Chase, and the guard moves to 2. In tick 3 it moves to 4, where
it stands on the player, and in tick 4 it stays there. In tick 5 the player jumped to 20, 16 away, so the guard stops
and returns to 2.

Your trace should agree with the real output in the answer of the first exercise.

### Step two: let the state own its enter and exit code

Some situations need work at the moment you arrive or leave. Paused needs to stop time when you enter and start it
again when you leave. If that code sits in the middle of an `if`, it runs on the wrong frames or twice.

The habit is to move into a state through one function, `ChangeState`, which runs the leaving code of the old state
and the entering code of the new one. Nothing else assigns the variable. A bug where time stays frozen now has one
place to look.

### How the pause menu moves between situations

The Third-Person sample has a small machine in `Samples/ThirdPerson/Scripts/PauseMenu.cpp`. It has three situations:
playing, paused, and paused with the settings panel open. The sample stores them in the flag `Paused` and in the
answer of the settings script to `IsOpen`. One action, Pause, moves between them.

:::question
The next code uses pointers and a function marked `override`. If they are new, read [Memory and pointers](../basics/cpp-memory.md) and [Classes and inheritance](../basics/cpp-classes.md) first.
:::

The function below runs every frame and decides what the Pause action does in each situation. Notice the three
branches after the first `if`.

```cpp src="Samples/ThirdPerson/Scripts/PauseMenu.cpp#L38-L52" symbol="PauseMenu::OnUpdate"
void OnUpdate(float) override
{
	const bool pausePressed = Input::IsActionPressed("Gameplay/Pause");
	if (pausePressed && !ThirdPerson::IsAttractMode() && !IsCourseComplete())
	{
		SettingsMenu* settings = GetEntity().GetScript<SettingsMenu>();
		if (!Paused)
			Pause();
		else if (settings && settings->IsOpen())
			settings->Close();
		else
			Resume();
	}
	TimeScale = Time::GetTimeScale();
}
```

1. **Line 40:** the one question the update asks is whether the Pause action was pressed.
2. **Line 41:** the press is ignored in the attract mode and after the course is complete, situations where pausing makes no sense.
3. **Lines 44-45:** playing becomes paused through `Pause`, which stops time, shows the panel and frees the cursor. That is the entering code of the state.
4. **Lines 46-49:** in paused, the same button closes the settings if they are open, and otherwise resumes. One input has three meanings, one for each situation.

The code is short because the sample puts every enter and exit into `Pause` and `Resume`. Compare that with a
version in which `Time::SetTimeScale(0)` is called from five places: one forgotten call leaves the game frozen.

### An animation controller is the same machine kept as data

The idea reaches beyond code. An **animation controller**, which [Animation](animation.md) lets you edit, is a state
machine whose states are clips (idle, walk, jump) and whose moves are conditions you set in the editor, not code you
write. Its page in the engine-internals part, [State machines for animation](../animation/state-machines.md), shows how
Strata stores it. A game maker who understands the guard understands the controller.

## The update method: the engine already runs the loop

The second pattern of that book is the **update method**: a game object has one function that the engine calls once for each
frame, and the object moves itself a little in it. Your scripts run inside the :term[game loop]{id=game-loop}, and the function is `OnUpdate`, which you have used since your first script.

The point is what you do not write. A beginner often writes a loop inside a script, such as `while (alive) { Move(); }`.
That loop would never return, and the whole game would freeze, because nothing else could run. Strata runs every
script's `OnUpdate` once each frame, `OnFixedUpdate` for each physics step and `OnLateUpdate` after the rest, in an
order you can rely on; [The game loop from a script's side](script-loop.md) gives it.

So your script stores what it knows between calls, in members such as `m_State`, does a small piece of work and
returns. A timer is the same idea: you add `deltaTime` to a member each frame and compare, as in [Timers and events](timers-events.md).
The state machine above is the update method plus a variable that remembers where you were.

## A manager gives shared work one owner

Back to the twelve coins, each searching for the score. A **manager** is one script that owns a piece of shared work
or state. Examples are the score, the clock and the win panel. Everything else asks it instead of keeping its own copy.

The Third-Person sample does this with `CourseState`, on an entity named "Game". It holds the coins collected, the
time, and the panel shown at the goal. Its whole public face is a handful of fields and two functions.

```cpp src="Samples/ThirdPerson/Scripts/CourseState.h#L27-L39"
// What happened (the HUD, and the sample's regression test)
int32_t Coins = 0;
int32_t TotalCoins = 0;          // The scene's entities tagged "Coin"
float ElapsedSeconds = 0.0f;
bool Completed = false;
float BestSeconds = 0.0f;        // 0: no best time yet

void OnCreate() override;
void OnUpdate(float deltaTime) override;
void OnUIClick(Strata::Entity widget) override;

void AddCoin(const glm::vec3& position);
void Complete();
```

1. **Lines 28-29:** the manager counts what happened (`Coins`) and what the scene holds (`TotalCoins`). The on-screen display and the sample's regression test read these.
2. **Lines 34-36:** it implements the engine's :term[callbacks]{id=callback} like any script; it is no special type, only a script with a good name and a clear job.
3. **Lines 38-39:** `AddCoin` and `Complete` are the commands other scripts send. Each coin knows one function name, not the on-screen display, the sound or the save file.

Now the caller. When the player touches a coin, the coin finds the manager by its entity's name and calls it.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L38-L46" symbol="Coin::OnTriggerEnter"
void OnTriggerEnter(const Collision& collision) override
{
	if (Collected || !collision.Other.IsValid() || collision.Other.GetTag() != "Player")
		return;
	Collected = true;
	if (CourseState* course = Scene::FindEntityByName("Game").GetScript<CourseState>())
		course->AddCoin(GetTransform().GetWorldPosition());
	GetEntity().SetActive(false);
}
```

1. **Line 40:** the coin ignores everything that is not the player, and a coin already taken.
2. **Lines 43-44:** it finds the entity named "Game", asks for its `CourseState` script, and calls `AddCoin` only if both exist. The `if` with the declaration keeps a missing manager from crashing the coin.
3. **Line 45:** the coin hides itself with `SetActive(false)`. It is not destroyed.

The finding happens in the moment of the touch, as [Timers and events](timers-events.md) recommends: a coin never keeps
a pointer to the manager. The danger of a kept pointer is that the other script may be rebuilt by a :term[hot reload]{id=hot-reload} or
destroyed, and the pointer then points at nothing. The common mistakes at the end return to it.

:::analogy[The score keeper]
A basketball game has one score keeper at a table. When a player scores, the referee tells the keeper and nobody else
adds to the board; the crowd reads the board, not the players.

**Where it breaks:** a score keeper at a real game sits there for the whole match. A manager lives on an entity, so it ends when the scene ends, and anything that must survive a scene change belongs in [Levels and saves](levels-saves.md).
:::

### Against a global variable or a single global object

Why not a global variable, one `int g_Score` that every script reads? The variable works, and for one job it is the
right tool. A variable written outside any class, in a :term[namespace]{id=namespace} that has no name, in a :term[source file]{id=source-file}, exists once for the whole
module. Every script instance of every class in that module shares it, and it lasts while the module stays loaded.

The `PhysicsPlayground` sample uses one for a sound budget. Hundreds of boxes can hit the floor in one second, and one
shared counter, `s_Tokens` in `Samples/PhysicsPlayground/Scripts/Impact.cpp`, refills at 16 sounds each second and
caps a frame at 8. The sharing is the whole point: a counter on each body would let every body play.

Use a global for a limit that belongs to no entity. Use a manager when the state belongs to the game's world, because
a manager can be seen in the **Hierarchy**, its fields can be set in the Inspector, and it is rebuilt with the scene.
A global is invisible, and it keeps its value in the wrong places, such as after you press Play a second time.

## An object pool keeps objects instead of remaking them

An **object pool** is a set of objects built once, up front; instead of creating one when needed and destroying it
after, you take an idle one from the pool, use it and return it. In Strata, the cheapest form is an entity that you
create once and then show or hide with `SetActive`.

```mermaid caption="The life of a pooled entity: made once, then shown and hidden as many times as the game needs, with no new entity made later." alt="A state diagram with a box made, a box hidden and a box shown. An arrow goes from made to hidden, from hidden to shown when needed, and from shown back to hidden when done."
stateDiagram-v2
    [*] --> Hidden: made once
    Hidden --> Shown: needed
    Shown --> Hidden: done
```

:::example[A gun with 3 bullets]
The sketch below fires one shot each tick for 100 ticks. A bullet lives 4 ticks. The pool holds only 3 bullets, on
purpose, to show what a full pool does.
:::

The program keeps one number for each bullet: its age in ticks, or -1 when the bullet is idle. Look at how many
bullets it ever makes, and at the shots it must skip.

```cpp sketch="make-patterns-pool.cpp"
#include <cstdio>
#include <vector>

int main()
{
	std::vector<int> ages(3, -1);
	int skipped = 0;
	for (int tick = 0; tick < 100; tick++)
	{
		int spare = -1;
		for (int i = 0; i < 3; i++)
		{
			if (ages[i] >= 0 && ++ages[i] >= 4)
				ages[i] = -1;
			if (ages[i] < 0 && spare < 0)
				spare = i;
		}
		if (spare < 0)
			skipped++;
		else
			ages[spare] = 0;
	}
	std::printf("fired %d, skipped %d, made %zu\n", 100 - skipped, skipped, ages.size());
}
```

```text output-of="make-patterns-pool.cpp"
fired 75, skipped 25, made 3
```

1. **Line 6:** the pool is made once, with 3 entries, all idle.
2. **Lines 13-16:** each tick ages the active bullets, retires the old ones and remembers the first idle one.
3. **Lines 18-21:** a shot takes that idle bullet, or is counted as skipped when none is idle.

The output shows the gain. A program that made a bullet for each shot would have made 100. This one made 3 and kept
them. It also shows the price: when all three bullets are in flight the shot is skipped, 25 times in 100 here. In a
real game you pick a pool size above the most you ever need, then measure.

### The Tetris board: 200 cells, made once

The Tetris sample draws its board with 200 cell entities (10 columns by 20 rows), plus 4 for the preview of the next
piece. The sample's `README.md` says that a script creates and destroys them. That is not so: the board creates them
once, in `CreateCells`, and afterwards only shows, hides and changes the colour of them. The sample's scripts never
call `Destroy`.

Why not make a new cell when a piece lands, and destroy it when the line clears? A full board changes dozens of cells
in a frame. A cell that is shown and hidden costs a flag change, and the cell's mesh stays loaded.

The board also meets the second danger of a pool. A script can be rebuilt while the game runs, and the new copy of the
script knows nothing about the cells. Strata calls `OnReload` for that case; the Tetris board answers it with
`FindCells`, which reads the cells from the board's children again. It creates cells only when it finds none. The reload rules are
on [Your first script](first-script.md).

```cpp src="Samples/Tetris/Scripts/TetrisBoard.cpp#L355-L369" symbol="TetrisBoard::ShowCell"
void ShowCell(Entity cell, int32_t& shown, int32_t type)
{
	if (shown == type)
		return;
	if (type == Tetris::c_Empty)
	{
		cell.SetActive(false);
	}
	else
	{
		cell.SetProperty("MeshRenderer", "Material", GetMaterial(type));
		cell.SetActive(true);
	}
	shown = type;
}
```

1. **Line 357:** the cell remembers what it shows in `shown`, and the function returns at once when the wanted type is the same. Most cells, in most frames, take this exit.
2. **Lines 359-362:** an empty type hides the cell.
3. **Lines 365-366:** otherwise the cell gets its material, by `SetProperty`, and is shown.
4. **Line 368:** the cache is updated last, so the next call can compare.

The function works because the board keeps a second list, the types it last showed, next to the list of entities.
`Refresh` compares each wanted type with the shown one and calls `ShowCell` for all 200 cells. The calls that change
nothing are cheap, and the expensive ones, a material and a change of activity, happen only for cells that differ.

### Text is the same case

The score on screen is a text component. Strata ignores a text that did not change, but the board would still build a
new string in every frame, so it writes the text only when the number changed.

```cpp src="Samples/Tetris/Scripts/TetrisBoard.cpp#L326-L340"
if (m_Game.GetScore() != m_ShownScore)
{
	m_ShownScore = m_Game.GetScore();
	SetText(ScoreText, "Score: " + std::to_string(m_ShownScore));
}
if (m_Game.GetLevel() != m_ShownLevel)
{
	m_ShownLevel = m_Game.GetLevel();
	SetText(LevelText, "Level: " + std::to_string(m_ShownLevel));
}
if (m_Game.GetLines() != m_ShownLines)
{
	m_ShownLines = m_Game.GetLines();
	SetText(LinesText, "Lines: " + std::to_string(m_ShownLines));
}
```

1. **Lines 326-330:** `m_ShownScore` holds the score on screen. The text is rewritten, with `SetText`, only when the game's score differs.
2. **Lines 331-340:** the level and the lines work the same way, so a frame in which nothing scored does no text work at all.

The two lines of reasoning, a cache of what is shown and a comparison before a change, are one habit: touch the world
only when it differs from what you want.

### What a hidden entity still receives

A hidden pool entity is not a deleted one. Strata gives an inactive entity no `OnUpdate`, `OnFixedUpdate` or
`OnLateUpdate`, so a hidden bullet costs no script time. But its `OnCreate` and `OnDestroy` still run, and a contact
that began before it was hidden still ends with its Exit callback. Pools can rely on that last rule: a bullet hidden in
the middle of a touch does not leave a script waiting for an end that never comes.

### A pool of prefab copies

The Tetris cells are made with `Scene::CreateEntity` and `AddComponent`, so they exist at once. A bullet that is a copy
of a :term[prefab]{id=prefab-make} is different. `Scene::Instantiate` never waits: when the prefab has not loaded, it starts the load and
returns a null entity. A pool built in `OnCreate` may therefore hold nothing.

Ask for the prefab with `Assets::RequestLoad` in `OnCreate`, then fill the pool in the first `OnUpdate` in which
`Assets::IsLoaded` is true. Or build the bullets from entities, as the Tetris board does.

## How the patterns compare

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Flags | Almost nothing to write | Breaks as flags multiply | Doubles with each new flag | Every first prototype |
| Enum and `switch` | One variable and a few `case` lines | Impossible combinations cannot exist | Low | Many small games and tutorials |
| State objects with enter and exit | One class for each state | Best when states carry data and entering code | Medium | Larger games; Nystrom's State |
| Search each time | One lookup in each caller | Fine for rare calls | Callers repeat the same code | Unity's `Find`, Godot's `get_node` |
| Manager | One extra script | One owner of the shared state | Low | Games of every size |
| Create and destroy | One build for each object | Simple, but costly when frequent | Lowest | Rare objects |
| Object pool | Memory for the most objects, built once | Steady :term[frame time]{id=frame-time} | Medium: you must reset and size it | Bullets, particles, Nystrom's Object Pool |

None of these choices is wrong for every case. A guard with two states and a bullet that fires once a minute need none
of the heavy forms, and the cost of a pattern is code the reader must understand.

## Strata keeps its patterns in your scripts

:::why[Why does Strata have no behaviour framework above the script?]
Strata gives you scripts on entities, with `OnCreate`, the three update callbacks and the
contact callbacks. It gives you no state machine class, no manager type and no pool type. Game code is plain C++ in
a :term[script class]{id=script-class}, and the four patterns of this page are ordinary members and functions in it.

The reason is that a framework fixes one shape for every game. A tile game, a shooter and a driving game want different
states and different pools. The cost of the choice is that nothing writes the pattern for you, and two games can
solve the same problem in two shapes. The samples all use the same four patterns, so you can copy their shape.
:::

Strata also has no game artificial intelligence (AI): no steering, no finding of routes and no navigation meshes. A guard is a state machine in a
script, like the one above, and [Game AI](../appendix/game-ai.md) lists the general techniques.

## What the patterns cannot do

A manager's state ends with its scene. A score that must survive the move from one level to the next, or the end of
the program, has to be stored somewhere that lives longer; [Levels and saves](levels-saves.md) shows where.

A pool cannot give you more than you made. When a pool is empty you must choose: skip the shot, as the sketch does,
wait, or make one more. A state machine has the opposite weakness: when a game has fifty situations that combine, a
single enum grows too long, and larger games split it into several machines that run side by side. Strata does not
help with any of this, and [What Strata does not do](../appendix/not-in-strata.md) lists the larger absences.

## Common mistakes

- **A flag for every state.** Symptom: the game does something impossible, such as dying while paused. Fix: write the list of situations first, then one enum, and let only `ChangeState` assign it.
- **A pointer to another script kept across frames.** Symptom: a crash or a stale number after a hot reload or after the other entity was destroyed. Fix: find the script when you need it, as the coin does, with `GetScript`.
- **Destroying and creating what could be hidden.** Symptom: a hitch when many objects appear at once. Fix: make them once, hide them with `SetActive(false)`, and measure before you decide.
- **Creating the pool again in `OnReload`.** Symptom: after each rebuild the scene holds another full set, and the old ones stay visible. Fix: `OnCreate` builds; `OnReload` finds, as `FindCells` does.
- **Forgetting that a full pool refuses.** Symptom: shots that never appear in a long fight. Fix: choose the size from the most you need, and decide what a skipped request means.

## Summary

- Replace a group of flags with a scoped enum and a `switch`, so that only the situations you designed can exist.
- Give shared work to one manager script, found by name when needed and never kept as a pointer.
- Make objects once and show or hide them; a hidden entity gets no updates but still gets `OnCreate`, `OnDestroy` and the Exit of a contact.
- Choose a pattern by the problem: situations to name, work to own or objects to keep.
- The samples show all four: the Third-Person pause menu, `CourseState` and its coins, and the Tetris board.

## Check yourself

1. A script has the flags `isJumping`, `isFalling` and `isLanding`. How many combinations of the three can exist, and what does an enum do about them?

   :::answer{tests="state-enum"}
   Three flags give 2 × 2 × 2 = 8 combinations. The character is in one situation at a time, so most of the 8 are impossible. An enum with the three values holds one of three names, and no impossible combination can be stored.
   :::

2. Twelve coins each search the scene for the score display. What does a manager change? Choose: (a) the coins get faster; (b) there is one place that knows how the score works; (c) the coins no longer need to find anything.

   :::answer{tests="manager-owner"}
   Answer (b). Answer (a) is wrong: the speed of the search was never the problem. Answer (c) is wrong: each coin still finds the manager by name when it is touched. What changes is that a rename or a new rule touches one script, not twelve.
   :::

3. A pool has 5 bullets, each flies for 4 ticks, and one shot is requested each tick. How many shots are skipped in a long fight?

   :::answer{tests="pool-reuse"}
   A shot occupies a bullet for 4 ticks and one shot comes each tick, so 4 bullets are busy at once. Five bullets are enough, and no shot is skipped. With 3 bullets, as in the page, one shot in 4 is skipped.
   :::

4. A hidden pooled entity has a script with `OnUpdate`, `OnCreate` and `OnDestroy`. Which of them run while it is hidden?

   :::answer{tests="pool-reuse"}
   `OnUpdate` does not run: an inactive entity gets no update callbacks. `OnCreate` and `OnDestroy` still run when the entity is created or destroyed, whether it is active or not.
   :::

5. You write a game with one shared limit on sounds, and a hero with three situations. Which pattern fits each?

   :::answer{tests="pick-pattern find-in-samples"}
   The limit belongs to no entity, so a variable shared by the module, as `s_Tokens` in `Impact.cpp` of the `PhysicsPlayground` sample, fits. The hero has situations, so a state machine fits, like the pause menu of the Third-Person sample.
   :::

## Exercises

1. **Basic.** Turn the guard's flags into a scoped enum and a `switch`. Use the rules of the page: Patrol to Chase when the player is less than 5 units away; Chase to Return when more than 8 units away; Return to Patrol at position 0. Move 2 units for each tick. Predict the state after each of the player positions 10, 4, 4, 4, 20, 20, 20, then run it.

   :::answer[Worked solution]{tests="state-enum pick-pattern" solution="sketches/make-patterns-guard.cpp"}
   The three flags become `GuardState`, and the loop asks one question, the state, in a `switch`. The prediction by hand: tick 1 Patrol at 0, tick 2 Chase at 2, ticks 3 and 4 Chase at 4. Tick 5 is Return at 2, because the player is 16 away; tick 6 is Return at 0, and tick 7 is Patrol at 0. State numbers are 0 for Patrol, 1 for Chase and 2 for Return.

   ```cpp sketch="make-patterns-guard.cpp"
   #include <cmath>
   #include <cstdio>
   enum class GuardState { Patrol, Chase, Return };
   GuardState Next(GuardState state, float playerDistance, float x)
   {
   	switch (state)
   	{
   		case GuardState::Patrol: return playerDistance < 5.0f ? GuardState::Chase : state;
   		case GuardState::Chase: return playerDistance > 8.0f ? GuardState::Return : state;
   		default: return x <= 0.0f ? GuardState::Patrol : state;
   	}
   }
   int main()
   {
   	const float playerPath[] = { 10, 4, 4, 4, 20, 20, 20 };
   	GuardState state = GuardState::Patrol;
   	float x = 0.0f;
   	for (float player : playerPath)
   	{
   		state = Next(state, std::fabs(player - x), x);
   		if (state == GuardState::Chase) x += std::fmin(std::fabs(player - x), 2.0f) * (player > x ? 1.0f : -1.0f);
   		else if (state == GuardState::Return) x = std::fmax(0.0f, x - 2.0f);
   		std::printf("player at %2.0f: state %d, guard at %.0f\n", player, static_cast<int>(state), x);
   	}
   }
   ```

   ```text output-of="make-patterns-guard.cpp"
   player at 10: state 0, guard at 0
   player at  4: state 1, guard at 2
   player at  4: state 1, guard at 4
   player at  4: state 1, guard at 4
   player at 20: state 2, guard at 2
   player at 20: state 2, guard at 0
   player at 20: state 0, guard at 0
   ```

   1. **Line 6:** one `switch` on one variable; the five impossible combinations of three flags cannot be stored.
   2. **Lines 8-10:** the three rules, one for each state: each returns the next state.
   3. **Lines 21-22:** the guard moves according to the state it is in.

   The output agrees with the prediction.
   :::

2. **Medium.** Build a pool of 20 bullets. Make them in `OnCreate`, find them again in `OnReload`, and fire one every 0.25 seconds by showing it. Compare with creating and destroying one for each shot.

   :::answer[Worked solution]{tests="pool-reuse" solution="tutorials/make/patterns/exercise-2.tutorial.json"}
   The script `BulletPool` creates 20 entities named "Bullet" under its own entity and hides each at once. `OnReload` calls `FindBullets` and creates nothing. `Fire` takes the first hidden bullet, resets its age and position, and shows it; when none is hidden it logs and skips the shot. The tutorial file builds the script, attaches it to a new entity, plays 60 steps and finds 20 bullets in the playing scene and none after play stops. In one minute of play it makes 20 entities, not the 240 that creating each shot would make.

   To use the download, create `BulletPool` with **Scripts ▸ New Script...**, then open the download's `Scripts/BulletPool.cpp`, copy all of its text into your file and save it. Do not copy the file over yours: the files of the download carry the date 1 January 1980, and the build compiles only files changed after its last result. A file that old is skipped, the Console says `the module was up to date`, and the old class stays in the game, so play shows no bullet. If that happened, save the file once in your text editor and build again.
   :::

3. **Hard.** Your score must survive the player moving from level 1 to level 2. Where does it live: the manager, a global variable or somewhere else? Argue for your choice, and say what happens when the game quits.

   :::answer[Worked solution]{tests="manager-owner pick-pattern"}
   The manager ends with its scene, so level 2 would start from zero. A module global lives while the module stays loaded, and a hot reload or a new start of the program loses it, so it is wrong for a score the player earned. A score that matters after quitting belongs in a save file; [Levels and saves](levels-saves.md) shows the game's save system. The manager can still show the number, and reads it from the save when its scene starts.
   :::

## Where it lives in Strata

- The pause menu: `Samples/ThirdPerson/Scripts/PauseMenu.cpp`, on the entity named "Game".
- The manager: `Samples/ThirdPerson/Scripts/CourseState.h` and `CourseState.cpp`; its caller: `Samples/ThirdPerson/Scripts/Coin.cpp`.
- The pool and the cached `Refresh`: `Samples/Tetris/Scripts/TetrisBoard.cpp`; the rules class kept apart from the engine: `Samples/Tetris/Scripts/TetrisGame.h`.
- The shared sound budget: `Samples/PhysicsPlayground/Scripts/Impact.cpp`.
- The script functions: `SetActive` and `Destroy` in `StrataScriptCore/Include/StrataScript/Entity.h`, `Instantiate` in `StrataScriptCore/Include/StrataScript/Scene.h`.
- The rule that a hidden entity gets no update callbacks: `Strata/src/Strata/Scripting/ScriptSystem.h`.

## Further reading

- Robert Nystrom, *Game Programming Patterns*, chapters State, Update Method and Object Pool (<https://gameprogrammingpatterns.com>): the source of the names; beginner to intermediate.
- Unity manual, scripting and object pooling pages (<https://docs.unity3d.com>): what another engine offers for pools; intermediate.
- Godot documentation, nodes and scenes (<https://docs.godotengine.org>): how a node tree finds and owns parts; intermediate.

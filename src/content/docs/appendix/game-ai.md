---
id: appendix/game-ai
title: "Game AI in general: steering, pathfinding, navigation meshes and behaviour trees"
description: "How games make agents decide, find a way and move, which method fits which problem, and how a Strata script builds a fox that wanders."
kind: concept
size: L
tracks: []
needs: [basics/trees-graphs, basics/math-geometry]
time: 60
learn:
  - id: three-layers
    text: name the three layers of game AI and the senses under them
  - id: choose-model
    text: choose a decision model for an agent and say what it costs
  - id: trace-astar
    text: trace an A* search on a grid and predict what its heuristic changes
  - id: read-fox
    text: explain how the fox script decides, moves and stands on the terrain
status: final
---

Place a fox in a forest scene. If it stands still, the forest looks like a painting. If it walks, stops to look around and now and then runs, the forest looks alive.

Now place a guard in a corridor, and let the player hide behind a wall. A guard that walks straight at the player ends with its nose against the stone. A guard that goes around the wall looks clever.

Both effects come from one kind of code, which this page calls game artificial intelligence (AI): the code that lets a character that no person controls choose what to do and do it. A character of this kind is an **agent**. The page builds the subject from the two problems above. It shows the methods that games use, and ends with a fox that a Strata script moves in the Open World sample.

## Two naive answers and where they break

The first idea is to move the agent straight at its target, a little each frame. Take a guard at (0, 0) and a player at (6, 8), both in metres. The distance is 10 m and the direction is (0.6, 0.8). At 5.5 m/s the guard moves 0.0917 m in one frame at 60 frames per second (a frame lasts 16.7 ms).

The guard never stops walking along that line, so a wall on the line stops it. The guard has no idea that a wall exists.

The second idea is to give the agent life by rolling dice: every frame, pick a random action. Say the dice choose between "walk", "stand" and "run". After one second of 60 frames, the fox has changed its mind about 40 times. The result is a twitching animal, not a living one. A real animal commits to an action for seconds.

The two answers fail for opposite reasons. The first has a goal and no knowledge of the world. The second reacts and keeps no memory of what it chose. A good agent needs three separate jobs, and a rule for each.

## Three layers over the senses

Engines split game AI into three layers. Deciding chooses what to do now: survey, walk, chase, flee. Finding a way chooses which route reaches the place that deciding picked. Moving turns the route into motion, one frame at a time. Each layer answers one question, and each can use a different method.

Under all three sit the senses, the questions an agent asks about the world: can I see the player, is there ground under my feet, who is near me? A game answers them with queries on the physics world. Two matter most. A ray, a line from a point in a direction that reports what it hits first, tests the world along a line. An overlap test asks which bodies touch a sphere or a box.

```mermaid caption="The three layers of game AI. Each layer feeds the next, and all three ask the senses about the world." alt="A chain of three boxes, deciding, finding a way and moving, with the senses box below feeding all three."
flowchart TB
    D["Deciding: what to do now"] --> F["Finding a way: which route"]
    F --> M["Moving: how to get there"]
    S["Senses: rays, overlaps, timers"] --> D
    S --> F
    S --> M
```

The diagram shows that the layers pass work downward and the senses feed every layer. The first sense that games use is **line of sight**: a ray from the agent's eyes to the target that reaches the target before it reaches anything else. If the ray hits the wall first, the agent cannot see the player, however close the player is. The ray ends at the first hit, so the test costs one query.

The three layers are a way to think, not a law. A small game can fold all of them into ten lines, and the fox of this page does. A large game keeps them apart because each layer then has its own tools and its own cost.

## Deciding: four models, each fixing the one before

Deciding is the layer that most affects how an agent feels. The models below come in the order in which each one repairs a weakness of the one before.

A finite state machine (the page [Patterns for game code](../make/patterns.md) teaches it) holds one state at a time, such as Patrol or Chase, and moves between them along transitions that a condition triggers. It is cheap, and a reader can draw it on paper. Its weakness appears as the agent grows. A guard with ten states may need transitions between most pairs, and the number of transitions grows with the square of the states. A hierarchical state machine repairs this by putting states inside states: an Alert state holds Chase and Search, and a transition out of Alert leaves both at once.

The next weakness is that states mix two things: what the agent does and when it switches. A **behaviour tree** separates them. It is a tree of nodes that an update evaluates from the root downward, one pass per update, which is called a tick. This tick is one pass over the tree, not the fixed step of the physics simulation that [Time](../core/time.md) teaches. A leaf either checks a condition or performs an action, and each node returns success, failure or running.

Two inner nodes do most of the work. A `Sequence` runs its children in order and fails at the first failure. A `Selector` tries its children in order and succeeds at the first success.

The figure below draws one guard twice. It patrols; when it sees the player it chases; when it loses the player it returns to its post.

```mermaid caption="The guard as a state machine. Three states, and each arrow carries the condition that triggers it." alt="Three states, Patrol, Chase and Return, joined by arrows labelled sees the player, loses the player and is at the post."
stateDiagram-v2
    [*] --> Patrol
    Patrol --> Chase: sees the player
    Chase --> Return: loses the player
    Return --> Chase: sees the player
    Return --> Patrol: is at the post
```

```mermaid caption="The same guard as a behaviour tree. The root node tries chasing first, then returning, then patrolling." alt="A choice node at the root with three children. The first is a chain of the condition sees the player and the action move to the player. The second is a chain of the condition is away from the post and the action return. The third is the action patrol."
flowchart TD
    R["Selector"] --> A["Sequence"]
    R --> B["Sequence"]
    R --> P["Action: patrol"]
    A --> A1["Condition: sees the player"]
    A --> A2["Action: move to the player"]
    B --> B1["Condition: is away from the post"]
    B --> B2["Action: return to the post"]
```

Read the tree by ticking it. The root `Selector` asks its first child, a `Sequence`. The `Sequence` asks whether the guard sees the player. If the answer is no, it fails and the `Selector` tries the next child: is the guard away from its post? If it is, the guard returns.

If it is not, the `Selector` reaches the last child and patrols. No node holds the name of the state before it: the tick starts from the root every time, so the guard reacts at once to a change.

The cost is that the tick walks the tree each update, and an action that takes many frames returns running so that the next tick can continue it. A designer, however, can change the order of the children without touching a transition.

Some games need to weigh many wants at once. **Utility AI** gives every possible action a score between 0 and 1 from the agent's situation, then runs the action with the highest score. A hungry fox with a score of 0.9 for eating and 0.4 for resting eats. When the fox has eaten, its hunger score falls to 0.1, resting wins, and nobody wrote a transition between the two. The cost is tuning: the curves that turn a situation into a score need hand tuning and careful tests.

The last model plans. **Goal-oriented action planning** (GOAP) gives the agent a goal, such as "the player is dead", and a list of actions that each have conditions and effects. A search, much like the one on a map, finds a chain of actions that turns the facts of the world now into the goal.

The designer lists actions and never writes the order. The cost is the search itself and the trouble of learning why the agent chose a plan.

| Model | Cost per agent | Authoring effort | Debugging | Used by |
| --- | --- | --- | --- | --- |
| Finite state machine | One state check per update | Low for few states, high for many | Print the current state | Most games' simple enemies; Nystrom's State chapter |
| Behaviour tree | One walk of the tree per tick | Medium; the tree shows the logic | Show which node ran | *Halo 2* (Isla's talk); the behaviour tree tools of large engines |
| Utility AI | One score per action | High tuning effort | Print the scores | Life simulations; Mark's talks on the subject |
| GOAP | A plan search per new goal | High; needs facts and actions | Print the plan | *F.E.A.R.* (Orkin's paper) |

The table's sources are in Further reading. The models mix: a behaviour tree may hold a utility choice in one node, and a state machine may run one tree per state.

:::example[Choosing a model for three agents]
A fox has three behaviours and no goals: a state machine is enough, and the fox of this page is one. A guard with chase, search, return and call-for-help grows quickly into a dozen transitions, and a behaviour tree stays clear to read. A villager in a town simulation, who must balance hunger, money and sleep, suits utility scores, because no fixed order is right. Pick the simplest model that the agent's behaviour fits, and change only when the simple one hurts.
:::

## Moving: a steering behaviour is a desired velocity

Moving starts after the decision, with a small piece of arithmetic. A **steering behaviour** is a rule that turns the agent's situation into a desired velocity, the speed and direction it would like to have now. Reynolds, who named the idea, built flocks of birds from a handful of such rules. The agent then moves by that velocity each frame.

The simplest behaviour is seek: aim at the target at full speed. In the formula, the vector from the agent to the target is shrunk to length 1 and scaled by the speed.

$$v = s \cdot \frac{t - p}{\lvert t - p \rvert}$$

Here $v$ is the desired velocity in metres per second, $s$ is the top speed in metres per second, $t$ is the target's position in metres and $p$ is the agent's position in metres. The bars read "length of". For the guard at (0, 0) with the player at (6, 8) and $s$ of 5.5, the length is 10 and $v$ is (3.3, 4.4). At the limit where the agent stands on the target, the length is 0 and the formula divides by zero, so code must test for that case first.

The other behaviours are variations:

- Flee is seek with the sign reversed: it runs away from the point.
- Arrive is seek that slows near the target. Inside a slowing radius $r$, the speed is $s \cdot d / r$, where $d$ is the distance left. With $s$ of 5.5 m/s and $r$ of 5 m, an agent 2.5 m away goes at 2.75 m/s, and it stops without a jolt.
- Wander picks a slowly changing target ahead of the agent, so that the path curves instead of jittering.
- Separation pushes away from neighbours that stand too close. The push grows as the distance falls, so a neighbour 1 m away pushes twice as hard as one 2 m away.
- Obstacle avoidance casts a ray ahead. If a wall is 2 m away along a 3 m ray, the agent adds a sideways push along the wall's normal, scaled by the 1 m of ray that the wall cut off.

Several behaviours run at once and their desired velocities add up, each with a weight. The sum is capped at the top speed. Weights are the art of steering: a guard that weighs avoidance too low walks into the wall, and one that weighs it too high never gets near it.

## Finding a way: the level as a graph

Steering cannot find the way around a wall that lies far ahead, because it sees only what is near. Finding a way needs a map of the whole level. The usual map is a graph (see [trees and graphs](../basics/trees-graphs.md)): a node for each place an agent can stand, and an edge for each step between two places. A cost on each edge says how hard the step is. The level then becomes the question of the cheapest chain of edges from a start node to a goal node.

The simplest search is breadth-first. It keeps a queue, takes the oldest node, adds that node's new neighbours and stops at the goal. Every edge counts the same, so the first time it reaches the goal, the route has the fewest steps. It breaks when edges differ: a swamp cell that costs 3 and a road cell that costs 1 look equal to it.

Dijkstra's algorithm repairs that. It replaces the queue by a :term[priority queue]{id=priority-queue} ordered by the cost so far, and always takes the cheapest open node. Its route is always the cheapest. Its weakness is that it spreads out evenly in every direction, even away from the goal, because it knows nothing about where the goal lies.

**A\* search** (pronounced "A star") repairs that. It orders the priority queue by $f = g + h$: the cost paid so far, plus a heuristic, an estimate of the cost still to pay. The estimate pulls the search towards the goal. On a grid where an agent moves up, down, left or right, a common heuristic is the Manhattan distance: the number of columns plus the number of rows between the node and the goal.

$$f(n) = g(n) + h(n)$$

The symbol $n$ is a node. The cost $g(n)$ is the length, in steps, of the cheapest route found so far from the start to $n$. The estimate $h(n)$ is the cost, in steps, from $n$ to the goal. The function $f(n)$ is the priority, and the open node with the lowest $f$ goes first.

The result is the cheapest route only if the heuristic is admissible, which means that it never estimates more than the true remaining cost. Manhattan distance is admissible on this grid, because no route can use fewer steps than the columns and rows between the two cells.

Here is a grid of six by six cells. S is the start at column 0, row 2 and G the goal at column 5, row 2. A # is a wall. Columns and rows count from 0, from the top left.

```text
col   012345
row 0 ......
row 1 ..#..#
row 2 S.#.#G
row 3 .##.#.
row 4 ......
row 5 ......
```

The grid is a maze of short walls: the direct route from S to G is blocked at columns 2 and 4. Work by hand with the Manhattan heuristic. The start has $g$ of 0 and $h$ of 5, so $f$ is 5. Take it from the open set.

Its neighbours are (0, 1), (0, 3) and (1, 2). Their $g$ is 1, and their $h$ is 6, 6 and 4, so $f$ is 7, 7 and 5. The cell (1, 2) has the lowest $f$, so it comes next. Its only free neighbour is (1, 1): $g$ is 2, $h$ is 5, $f$ is 7. The open set now holds three cells of $f$ equal to 7 and the search continues from there.

The search of the sketch in the exercises finishes after taking 14 cells from the open set, with a route of 9 steps that runs down and along row 4. Dijkstra's algorithm, which is A\* with $h$ always 0, takes 29 cells for the same route. A heuristic with too high an estimate is a danger: with $h$ tripled, the search takes 19 cells and returns a route of 13 steps, 4 more than the cheapest. The estimate pulled it along a longer way that looked close to the goal.

A grid works, yet it wastes effort: a plain floor of 100 by 100 cells has 10,000 nodes. A **navigation mesh**, often shortened to navmesh, covers the walkable floor with a small number of :term[convex]{id=convex} polygons instead. Because each polygon is convex, an agent can walk in a straight line between any two of its points. The nodes of the search are the polygons, and the edges are the borders that two polygons share. A room that needs 36 grid cells may need 4 polygons.

Tools build the mesh from the level's geometry. They find the surfaces that are flat enough to stand on, shrink them by the agent's radius, and merge the result into polygons. The search over polygons gives a list of borders to cross. The route through a polygon list is jagged, so the next step, string pulling, pulls a rope tight through the borders, and the rope touches only corners. The agent follows the rope.

Two agents following their routes may still meet. **Local avoidance** is the rule set that lets agents on their own routes step around each other without a new search. It can be a steering behaviour such as separation, or a method that predicts the path of the other agent. The route is the plan, and local avoidance is the correction that the plan cannot foresee.

## Strata leaves game AI to scripts

Strata has no game AI module. A search of the engine's code and its script software development kit (SDK) for the words path finding, navigation mesh, behaviour tree, steering and utility AI finds nothing. A search for A* or Dijkstra finds nothing either. The word "navigation" appears only in the game's user interface (UI), for keyboard and gamepad movement between widgets.

The engine's documents neither plan such a module nor refuse it, so the page gives no reason beyond the facts: the code is absent, and AI is script code today.

:::why[Why script code and not an engine module?]
The documents do not say. What the code shows is the engine's way of working: gameplay lives in script classes that a game builds, and the engine offers the senses and the movement they need. The cost of the choice is that every game writes its own search, and that no tool bakes a navigation mesh. Do not read a plan into the silence: no document says one is coming.
:::

A script still has the pieces it needs. The SDK offers `Physics::Raycast` and `Physics::RaycastAll` for rays, and `Physics::OverlapSphere` and `Physics::OverlapBox` for overlaps; each takes a layer mask, a set of collision layers, to choose what it can hit ([Physics queries](../physics/queries.md), [Collision layers](../physics/collision-layers.md)). The character controller's `Move` takes a velocity in metres per second, for agents that must collide with the world ([Character controllers](../physics/character-controllers.md)). `Random` gives a seeded sequence and `Timer` counts game time.

The animator's `CrossFade` blends to a named state ([Animation state machines](../animation/state-machines.md)), and `FindEntityByName` finds an entity. These are the senses, the clock and the hands. Deciding and finding a way you write.

## The fox: a state machine in a script

The Open World sample places 30 foxes in streamed world cells. Their script is `Samples/OpenWorld/Scripts/Wander.cpp`. A fox has no physics body: its prefab holds an Animator and a Script. It writes its own transform each frame and asks physics for one thing, the ground.

The first excerpt shows how a fox starts. The comment at the top of the file is not repeated here; a later section returns to it.

:::question
New to C++? Learn classes, `override` and calls in [Classes in C++](../basics/cpp-classes.md), then return.
:::

The function `OnCreate` runs when the fox appears. Look at how it fixes the home, the random sequence and the ground mask, which make each fox different.

```cpp src="Samples/OpenWorld/Scripts/Wander.cpp#L25-L34"
void OnCreate() override
{
	m_Home = GetTransform().GetWorldPosition();
	m_Random.Seed(static_cast<uint64_t>(Seed) * 7919u + 17u);
	const int32_t layer = Physics::GetLayerIndex("Terrain");
	m_TerrainMask = layer >= 0 ? (1u << static_cast<uint32_t>(layer)) : Physics::c_AllLayers;
	Choose();
}

void OnReload() override { OnCreate(); }
```

1. **Line 27:** the fox remembers its home, the place around which it wanders.
2. **Line 28:** the generator starts from a number made of the `Seed` field, so each fox rolls its own sequence and a restart repeats it.
3. **Lines 29–30:** the Terrain layer's index becomes a :term[bit mask]{id=bit-mask}; if the project has no such layer, the mask allows all layers.
4. **Line 31:** the fox picks its first state at once. The 30 foxes get their `Seed` from the prefab override in their cells.

:::question
New to pointers? Learn them in [Memory in C++](../basics/cpp-memory.md), then return.
:::

The next excerpt is the deciding layer. `Choose` rolls a state and a target, and `SetState` records the state and cross-fades the animator.

```cpp src="Samples/OpenWorld/Scripts/Wander.cpp#L68-L87"
void Choose()
{
	const float roll = m_Random.NextFloat();
	const float angle = m_Random.NextFloat() * 6.2831853f;
	const float distance = Range * (0.3f + 0.7f * m_Random.NextFloat());
	m_Target = m_Home + glm::vec3(std::cos(angle) * distance, 0.0f, std::sin(angle) * distance);
	// A fox that surveyed walks or runs next: it never stands for two surveys in a row.
	const bool surveyed = StateIndex == 0;
	SetState(!surveyed && roll < 0.25f ? 0 : (roll < 0.85f ? 1 : 2), 4.0f + m_Random.NextFloat() * 6.0f);
}

void SetState(int32_t state, float seconds)
{
	m_Timer = seconds;
	if (state == StateIndex)
		return;
	StateIndex = state;
	static const char* const c_States[] = { "Survey", "Walk", "Run" };
	GetEntity().GetAnimator().CrossFade(c_States[state], 0.3f);
}
```

1. **Lines 70–73:** one roll picks the state; two more rolls choose an angle and a distance from 0.3 to 1 times `Range`. The target is a spot on a circle around home.
2. **Lines 75–76:** a fox that surveyed a moment ago walks or runs next, so it never surveys twice in a row. A roll below 0.25 surveys, below 0.85 walks, otherwise runs. The state lasts 4 to 10 seconds.
3. **Lines 79–86:** `SetState` stores the timer, returns early if the state did not change, and cross-fades the animator to the state's name over 0.3 seconds.

The figure draws the three states as the code gives them. Every timer arrow comes from `Choose`; arriving within 0.5 m of the target is the one exit with its own rule.

```mermaid caption="The fox's three states. A timer ends each state and a dice roll picks the next one; arriving at the target sends the fox to Survey." alt="Three states, Survey, Walk and Run, with arrows between every pair. Survey leads to Walk or Run when its timer ends. Walk and Run lead to Survey on arrival and to any state when their timers end."
stateDiagram-v2
    [*] --> Survey
    Survey --> Walk: timer ends, 85 %
    Survey --> Run: timer ends, 15 %
    Walk --> Survey: arrives, or timer ends 25 %
    Run --> Survey: arrives, or timer ends 25 %
    Walk --> Walk: timer ends, 60 %
    Walk --> Run: timer ends, 15 %
    Run --> Run: timer ends, 15 %
    Run --> Walk: timer ends, 60 %
```

:::question
New to `std::optional`? Learn it in [Modern C++](../basics/cpp-modern.md), then return.
:::

Now the layers of moving and senses. The function `OnUpdate` runs each frame. First it asks the ground sense, then handles the timer.

```cpp src="Samples/OpenWorld/Scripts/Wander.cpp#L38-L45"
TransformComponent transform = GetTransform();
const glm::vec3 position = transform.GetWorldPosition();
const std::optional<RaycastHit> ground = Physics::Raycast(position + glm::vec3(0.0f, 50.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f), 200.0f, m_TerrainMask);
if (!ground)
	return; // No ground under it yet: it waits
m_Timer -= deltaTime;
if (m_Timer <= 0.0f)
	Choose();
```

The `Raycast` call starts 50 m above the fox and goes 200 m straight down, only against the terrain mask. With no hit the fox waits where it is until the ground under it is there, as the comment at the top of the file says.

The second part is steering and facing. It seeks the target on the flat plane, then stands the fox on the terrain.

```cpp src="Samples/OpenWorld/Scripts/Wander.cpp#L46-L65"
glm::vec3 next = position;
if (StateIndex > 0)
{
	const glm::vec3 toTarget(m_Target.x - position.x, 0.0f, m_Target.z - position.z);
	const float remaining = glm::length(toTarget);
	if (remaining < 0.5f)
	{
		SetState(0, 2.0f + m_Random.NextFloat() * 3.0f);
	}
	else
	{
		const float speed = StateIndex == 2 ? RunSpeed : WalkSpeed;
		next += toTarget / remaining * std::min(speed * deltaTime, remaining);
		transform.SetWorldRotation(glm::angleAxis(std::atan2(toTarget.x, toTarget.z), glm::vec3(0.0f, 1.0f, 0.0f)));
	}
}
if (const std::optional<RaycastHit> under = Physics::Raycast(next + glm::vec3(0.0f, 50.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f), 200.0f, m_TerrainMask))
	next.y = under->Point.y;
Distance += glm::length(glm::vec2(next.x - position.x, next.z - position.z));
transform.SetWorldPosition(next);
```

1. **Lines 49–51:** the vector to the target ignores height, and the fox is done when it is closer than 0.5 m.
2. **Lines 57–58:** seek: the step is the unit direction times speed times the frame's time, and `std::min` keeps it from overshooting the target.
3. **Line 59:** `atan2` of the target's x and z gives the angle about the vertical axis, so the fox turns to face the way it walks.
4. **Lines 62–63:** a second ray at the next position sets the height; the fox stands on the terrain.
5. **Lines 64–65:** the distance moved adds to `Distance` and the new position is written.

The fox seeks at a fixed speed and stops with a jolt, so it has no arrive behaviour and no avoidance. That is a choice of a small script, not a limit of the engine. A rock in its path is not a problem the fox knows.

### Seeing what an AI decides

Strata scripts cannot draw lines or shapes into the scene, so you cannot draw a path in the view. The fox shows the cheap way: it keeps its decision in script fields. `StateIndex` holds the state (0 Survey, 1 Walk, 2 Run) and `Distance` holds the metres moved. The Inspector shows both fields while the game plays, and the command `script.get` reads them.

The sample's own regression script finds a fox, reads `StateIndex`, sets `Distance` to 0 and waits until the fox has moved 1 m. The fox writes no log, but a script that calls `Log::Info` when a state changes adds a line to the log for each decision. [Automated playtests](../make/automated-playtests.md) teaches the command script.

Fields cost little, and every agent should keep its state in one.

### What the comment says and what the code does

The first comment of `Wander.cpp` says that a fox's target lies inside its own world cell, so that it never walks into a cell that is not loaded. The code does not do that.

`Choose` picks a spot between 0.3 and 1 times `Range`, 22 m, from the fox's home, and tests no cell. The Wildlife layer's cells are 64 m wide, and 27 of the 30 foxes stand within 22 m of an edge of their cell. A fox may therefore pick a target outside its cell. The ground does not stop it: the 97 terrain tiles sit in the persistent scene, not in the cells, so the ray finds ground beyond the cell and the fox walks on.

The comment states a wish, and the code tests no cell. For streaming cells, see [Why worlds stream](../worlds/why-streaming.md).

## How the fox would grow

Each step below is a script change that uses only the SDK of the page. None needs the engine.

- **Arrive.** Replace the fixed step by the arrive formula, with a slowing radius of about 3 m. The fox then eases to a stop, and the animator can fade to Survey when its speed falls.
- **A grid search.** Keep a grid of cells in a script field or an array of the level, mark cells blocked by overlap tests at start-up, and run A* with the sketch's code. Search once when a target is chosen, not each frame, and walk the route cell by cell with seek.
- **Rays around rocks.** Cast a ray ahead of the fox each frame; when it hits, add the hit's normal to the desired velocity as the avoidance rule above shows. Use `RaycastAll` if several things can stand in the way.

## What Strata's choice cannot do

There is no navigation mesh to bake and no path query to call: the engine knows nothing about walkable areas. The public physics application programming interface (API) has queries by ray and overlap but no shape casts, so a wide agent cannot sweep its shape along a path to check that it fits ([Physics queries](../physics/queries.md)). Scripts also have no debug drawing ([Debug drawing](../gpu/debug-drawing.md)). What Strata does not do in general is listed in [What Strata does not do](not-in-strata.md).

## Common mistakes

- **Deciding every frame.** Symptom: the agent twitches between actions. Fix: decide when a timer ends or an event happens, as the fox does, and keep the state in between.
- **Searching a path every frame for every agent.** Symptom: the frame time rises with the number of agents. Fix: search when the target changes, store the route, and spread searches over frames.
- **A heuristic that guesses too high.** Symptom: the route is longer than the shortest one, as the 13 steps of the example show. Fix: use a heuristic that never exceeds the true cost, such as the Manhattan distance on a four-direction grid.
- **Moving a physics body by writing its transform.** Symptom: the body skips through walls or fights the physics. Fix: move a body through its body or character controller, as [Character controllers](../physics/character-controllers.md) teaches. The fox writes its transform only because it has no body.
- **Repeating a comment as if it were the code.** Symptom: a reader believes that a safety rule exists. Fix: read what the code does, as the cell comment of `Wander.cpp` shows.

## Summary

- Game AI has three layers, deciding, finding a way and moving, over the senses: rays, overlaps and timers.
- State machines, behaviour trees, utility scores and planning trade authoring effort against cost and clarity; choose the simplest that fits.
- A* orders its open set by cost so far plus a heuristic; a heuristic that guesses too high can return a longer route.
- The fox script rolls a state and a target with a seeded generator, seeks at walking or running speed, and stands on the terrain with a ray.

## Check yourself

1. A guard walks along a straight line to the player and gets stuck on a wall. Which layer is missing?

   - a) Deciding
   - b) Finding a way
   - c) The senses, only
   - d) Moving, only

   :::answer{tests="three-layers"}
   The answer is b. The guard decides to go to the player and moves, but nothing finds a route around the wall. Option a is wrong because the goal is right; option d is wrong because the movement code works. Option c is wrong because a ray alone does not plan a longer route; it only reports what is ahead.
   :::

2. A villager must weigh hunger, money and sleep, and no fixed order is right. Which decision model fits best?

   - a) A finite state machine with a transition for every pair
   - b) A behaviour tree with a fixed order
   - c) Utility scores
   - d) A* search

   :::answer{tests="choose-model"}
   The answer is c. Utility scores let the highest want win without a written order. Option a grows with the square of the states. Option b fixes an order that the problem says is not right. Option d is a search for a route, not a model for deciding.
   :::

3. On the page's grid, A\* with the Manhattan heuristic takes 14 cells from the open set and Dijkstra takes 29. What is the heuristic's value at the goal, and why does A\* take fewer?

   :::answer{tests="trace-astar"}
   The value at the goal is 0, because no steps remain. A* takes fewer because the heuristic raises the priority of cells that lie nearer the goal, so the search leans towards it, while Dijkstra, with a heuristic of 0, spreads out evenly from the start.
   :::

4. In `OnUpdate`, the ground ray finds no hit. What does the fox do, and why?

   :::answer{tests="read-fox"}
   The fox returns at once: it does not move, does not count down its timer and does not choose. The ground under it may not exist yet, so it waits where it is until the ground is there.
   :::

## Exercises

1. **Basic.** Continue the hand search of the page: after the cell (1, 1) with $f$ of 7, list the next cells that join the open set. Use the Manhattan heuristic.

   :::answer[Worked solution]{tests="trace-astar"}
   The cell (1, 1) has $g$ of 2. Its free neighbours are (0, 1), which is already open with $g$ of 1, and (1, 0), a new cell with $g$ of 3, $h$ of 4 + 2 = 6 and $f$ of 9. The cell (2, 1) is a wall. Only (1, 0) joins the set, and the cells (0, 1) and (0, 3), both with $f$ of 7, come before it.
   :::

2. **Medium.** Predict the length of the route and the number of cells taken for the three weights of the sketch, then run it. Explain the differences.

   ::::answer[Worked solution]{tests="trace-astar" solution="sketches/appendix-game-ai-astar.cpp"}
   Weight 0 is Dijkstra's algorithm, so it takes the most cells. Weight 1 is A* and takes fewer. Weight 3 estimates too much, so expect a longer route.

   :::question
   New to lambdas? Learn them in [generic C++](../basics/cpp-generic.md), then return.
   :::

   The program runs the search three times on the page's grid, inside a ring of walls that makes the grid eight cells wide, so a cell number is its row times 8 plus its column. Look at how the weight multiplies the Manhattan distance.

   ```cpp sketch="appendix-game-ai-astar.cpp"
   #include <cstdio>
   #include <cstdlib>
   #include <queue>
   const char* c_Map[8] = { "########", "#......#", "#..#..##", "#..#.#.#", "#.##.#.#", "#......#", "#......#", "########" };
   void Search(int weight)
   {
   	const int start = 25, goal = 30; // cell = row * 8 + column
   	const auto guess = [&](int c) { return weight * (std::abs(c / 8 - goal / 8) + std::abs(c % 8 - goal % 8)); };
   	std::vector<int> cost(64, 99), from(64, -1);
   	std::priority_queue<std::pair<int, int>> open; int taken = 0; // largest first: priorities go in negated
   	cost[start] = 0; open.push({ -guess(start), start });
   	while (!open.empty())
   	{
   		const int cell = open.top().second; open.pop();
   		taken++; if (cell == goal) break;
   		for (int n : { cell - 8, cell + 8, cell - 1, cell + 1 })
   		{
   			if (c_Map[n / 8][n % 8] == '#' || cost[n] <= cost[cell] + 1) continue;
   			cost[n] = cost[cell] + 1; from[n] = cell; open.push({ -cost[n] - guess(n), n });
   		}
   	}
   	std::printf("weight %d: length %d, taken %d, path", weight, cost[goal], taken);
   	for (int c = goal; c >= 0; c = from[c]) std::printf(" (%d,%d)%s", c % 8 - 1, c / 8 - 1, c == start ? "\n" : "");
   }
   int main() { Search(1); Search(0); Search(3); }
   ```

   ```text output-of="appendix-game-ai-astar.cpp"
   weight 1: length 9, taken 14, path (5,2) (5,3) (5,4) (4,4) (3,4) (2,4) (1,4) (0,4) (0,3) (0,2)
   weight 0: length 9, taken 29, path (5,2) (5,3) (5,4) (4,4) (3,4) (2,4) (1,4) (0,4) (0,3) (0,2)
   weight 3: length 13, taken 19, path (5,2) (5,3) (5,4) (4,4) (3,4) (3,3) (3,2) (3,1) (3,0) (2,0) (1,0) (1,1) (1,2) (0,2)
   ```

   1. **Line 8:** the guess is the weight times the Manhattan distance to the goal: 0 gives Dijkstra's algorithm, 1 gives A* and 3 gives a guess that is too high.
   2. **Line 10:** the queue hands out the largest pair first, so priorities go in with the sign reversed.
   3. **Lines 14–15:** the search takes a cell from the open set, counts it and stops at the goal.
   4. **Lines 16–19:** each neighbour that is no wall and gets cheaper receives a new cost, a parent and an entry in the open set.

   Weights 1 and 0 both return 9 steps, taking 14 and 29 cells. The heuristic spares the search the cells that lie away from the goal. Weight 3 returns 13 steps, taking 19 cells: its estimate was too high, so it followed the corridor of column 3 and stopped at the first route it found. A tie between equal priorities goes to the larger cell number; another order changes the counts a little.
   ::::

3. **Hard.** Design a guard that patrols, chases a player it sees and returns to its post. Write it as a state machine and as a behaviour tree. Say which a Strata script holds with less code, and where each puts the fox's timers.

   :::answer[Worked solution]{tests="choose-model"}
   The state machine has three states, as the first figure shows. In a script it is an :term[integer]{id=integer} field with a `switch` in `OnUpdate`: simple, and the Inspector shows it.

   The tree has a root `Selector` with the `Sequence` nodes of the second figure. In a script it needs a node type, a tick function and a way to keep a running action, which is more code for three behaviours. For this guard the state machine is simpler. The tree pays off when behaviours grow.

   The fox's timers belong in the states of a state machine: each state sets its timer when it starts, as `SetState` does. In a tree a timer is a condition, "time since the last choice is over 4 s", checked by a node, or a node that guards an action.
   :::

## Where it lives in Strata

- `Samples/OpenWorld/Scripts/Wander.cpp`: the fox's script, class `Wander`, with the fields `WalkSpeed`, `RunSpeed`, `Range`, `Seed`, `StateIndex` and `Distance`.
- `Strata/src/Strata/GameUI/GameUIComponents.cpp`: the widgets' keyboard and gamepad navigation; the word appears elsewhere only in other game UI code.
- `StrataScriptCore/Include/StrataScript/Physics.h`: `Physics::Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox`.
- `StrataScriptCore/Include/StrataScript/Gameplay.h`: `Random` and `Timer`.
- `StrataScriptCore/Include/StrataScript/Animator.h`: `CrossFade`.

## Further reading

- Red Blob Games, "Introduction to the A\* algorithm" and its pages on grids and graphs: the best illustrated account of breadth-first search, Dijkstra's algorithm and A\*; beginner.
- Robert Nystrom, *Game Programming Patterns*, the State chapter: state machines in game code, with the weaknesses of the plain form; beginner.
- Craig Reynolds, "Steering Behaviors For Autonomous Characters" (1999): the origin of seek, flee, arrive, wander and separation; intermediate.
- Damian Isla, "Handling Complexity in the Halo 2 AI" (Game Developers Conference, 2005): behaviour trees in a shipped game; intermediate.
- Jeff Orkin, "Three States and a Plan: The AI of F.E.A.R." (2006): goal-oriented action planning in a shipped game; intermediate.
- Mikko Mononen, the Recast and Detour navigation libraries and their documentation: how a navigation mesh is built and searched; advanced.

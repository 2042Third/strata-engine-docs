---
id: make/recipes
title: "Building blocks and recipes"
description: "Take four scripts from the samples, a coin, a seeded pour, a grab tool and impact sounds with a budget, into your project, and learn seeded Random first."
kind: how-to
size: L
tracks: [G]
needs: [make/patterns, make/gameplay-math]
time: 80
learn:
  - id: random-seed
    text: explain how a seed makes Random give the same sequence, and choose a seed for variety or for a replay
  - id: coin
    text: write a coin script from the sample's excerpt that collects once and hides itself
  - id: pour
    text: build a pour of balls whose pile a seed decides
  - id: grab
    text: build a grab tool that pulls a body toward a point with a capped velocity
  - id: token-bucket
    text: compute how many impact sounds a token bucket lets through
since: 0.3.0
status: final
---

Most scripts a game needs were written before. This page takes four of them from the samples that ship with Strata, a coin, a pour of balls, a grab tool and impact sounds with a budget. For each one you learn what it does, read the sample's code, add it to your own project and then change it. Two of the recipes use `Random`, the :term[SDK's]{id=sdk} generator of random numbers, so the page starts there. Before you start:

- You have a project from the **Basic 3D** template, and a script builds in it ([Your first script](first-script.md)).
- Something that moves carries the tag `Player`: the ball of [Physics](physics.md) will do.
- You know managers and state machines ([Patterns](patterns.md)) and the pointer ray ([Gameplay math](gameplay-math.md)).
- You have about 80 minutes.

## Take a recipe into your project

A sample is a whole game, and its scripts lean on each other. The coin of the Third Person sample includes `CourseState.h`, and that file needs the player's scripts. The grab and the pour are functions of one large class, `Playground`. A reader who copies `Coin.cpp` alone gets :term[compile errors]{id=compile-error}.

So you never copy a file. You read the sample's code, then write a script of your own from the excerpt. Where the sample calls a script you do not have, you call yours: the coin calls the `Scoreboard` of [Timers and events](timers-events.md), or writes a log line instead. Sounds are the other dependency. A script that finds a clip by path needs the clip at that path in your project: copy the files with your file browser and import them as [Sound](sound.md) taught.

:::::steps

1. Open a sample as a copy, to read its scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the launcher press **Open Sample...**, choose the sample, and press **Copy and Open**. Open its `Scripts` folder in your code editor.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "ThirdPerson", "directory": "<a new folder>/ThirdPerson" } }
   ```

   :::
   ::::

   **You should see:** the sample's scene in the editor, and `Coin.cpp` among its scripts.

   **If you do not see it:** the dialog says the folder exists. Type a new folder name. The original sample never changes.

2. Return to your own project to add the recipe.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Open Recent** and your project.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.open", "parameters": { "path": "<your project's folder>" } }
   ```

   :::
   ::::

   **You should see:** your scene, with the ground and the camera of the template.

   **If you do not see it:** a dialog asks whether to save changes you made to the sample. Answer it first.

:::::

A clip found by path has one more cost. A pruned export packs only what scenes use, so a clip that only a script names is lost unless the **Export** page of the project settings lists it ([Export](export.md)).

## Random and seeds

Every game wants some chance: which way an enemy turns, where a coin appears, how a pile of balls falls. A computer has no dice. A **generator** is a small piece of code that turns its stored number into the next number that looks random, and the number it stores changes with every call. The SDK's `Random` class does this in your :term[script module]{id=script-module}, and it gives the same numbers on every platform.

The generator begins from a number you give it. That number is the **seed**: the starting value of a generator, so that the same seed always gives the same sequence of numbers. The sketch below holds the real steps of `Random`'s generator, a small design named `PCG32`, and rolls a die five times with three generators: two with the seed 42 and one with the seed 7. Look at which lines match.

```cpp sketch="make-recipes-seed.cpp"
#include <cstdint>
#include <cstdio>

struct Random
{
	explicit Random(uint64_t seed) { Next(); State += seed; Next(); }
	uint32_t Next()
	{
		const uint64_t state = State;
		State = state * 6364136223846793005ull + 1442695040888963407ull;
		const uint32_t xorShifted = static_cast<uint32_t>(((state >> 18u) ^ state) >> 27u), rotation = static_cast<uint32_t>(state >> 59u);
		return (xorShifted >> rotation) | (xorShifted << ((32u - rotation) & 31u));
	}
	uint64_t State = 0;
};

int main()
{
	for (int run = 0; run < 3; run++)
	{
		Random random(run < 2 ? 42 : 7);
		for (int roll = 0; roll < 5; roll++)
			std::printf("%u%c", random.Next() % 6 + 1, roll == 4 ? '\n' : ' ');
	}
}
```

```text output-of="make-recipes-seed.cpp"
3 6 4 4 4
3 6 4 4 4
4 1 3 1 5
```

1. **Line 6:** the :term[constructor]{id=constructor} starts from 0 and mixes the seed in with two steps, so the seed alone decides every later number.
2. **Line 10:** each call moves the stored number to its next value.
3. **Lines 11–12:** the stored number is scrambled into the result, so neighbours look unrelated.
4. **Line 21:** the first two generators share the seed 42, the third has 7.
5. **Line 23:** `% 6 + 1` turns a number into a die face.

The two lines made from 42 are the same, and the line from 7 differs. No clock or computer state enters: the numbers follow from the seed alone. That is the whole idea of a seed, and it gives two uses. A game that seeds from something that varies, such as the number of the level, gets variety, because each level has its own sequence. A game that records the seed can play a match again and get every outcome again.

A generator made without a seed is not random either. `Random random;` starts from the seed 0, so every one gives the same sequence in every run. Seed it from a value that changes, or from a field you set.

`Random` offers four calls:

- `Range(1, 6)` gives a whole number from 1 to 6, both included, each equally likely. That is a die.
- `Range(-0.04f, 0.04f)` gives a decimal from -0.04 up to, but never equal to, 0.04.
- `NextFloat()` gives a decimal from 0 up to, never equal to, 1.
- `Chance(0.25f)` is `true` one time in four; 0 never, 1 always.

The whole-number `Range` is exact. The quick way to a die, `Next() % 6 + 1` as in the sketch, makes some faces slightly more likely, because 2 to the power 32 does not divide by 6. The software development kit (SDK) draws again when a value falls in the part that would cause this. The mathematics is in [Probability](../basics/math-probability.md). Why the SDK helpers live in your module is a matter of [the script interface](../scripting/abi-sdk.md): they are compiled into the module, so they behave the same everywhere.

### A replay

A replay needs the seed in a field, so that the Inspector holds it, and a record of what happened. The script below rolls a die each time you press **R** and keeps the count of rolls in a field too. That matters on a :term[hot reload]{id=hot-reload}. `Random` is a plain member, not a field, so the reload makes a new one, and `OnReload` seeds it again. The loop in `OnReload` draws the numbers already rolled, so the next roll continues the sequence.

```pseudocode
class DiceRoller : public Script
{
public:
	int32_t Seed = 1;
	int32_t Rolled = 0; // A field, so a reload keeps it
	void OnCreate() override { m_Random.Seed(static_cast<uint64_t>(Seed)); }
	void OnReload() override
	{
		OnCreate();
		for (int32_t roll = 0; roll < Rolled; roll++)
			m_Random.Range(1, 6); // Draw again what was drawn
	}
	void OnUpdate(float) override
	{
		if (!Input::IsKeyPressed(Key::R))
			return;
		Rolled++;
		Log::Info("Roll ", Rolled, ": ", m_Random.Range(1, 6));
	}
private:
	Random m_Random;
};
```

1. **Line 4:** the seed is a field of the script, so you set it per entity and per run.
2. **Line 5:** the count of rolls is a field too, so a reload keeps it.
3. **Lines 7–12:** the reload makes the generator again and skips the rolls made so far.
4. **Line 18:** the log line is the record: the outcome with its number.

The registration lists both fields, as [Your first script](first-script.md) showed.

```pseudocode
ST_SCRIPT_CLASS(DiceRoller)
{
	ST_SCRIPT_FIELD(Seed);
	ST_SCRIPT_FIELD(Rolled);
}
```

With both fields registered, the Inspector shows them, and the steps below use them.

:::::steps

1. Create the class, write the code above and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Scripts ▸ New Script...**, type `DiceRoller`, press **Create**, replace the file's text, then press **Ctrl+B**.
   :::
   :::tab[With a command]
   No command writes code: `script.create` writes the template, then you edit the file.

   ```json
   { "command": "script.create", "parameters": { "class": "DiceRoller" } }
   ```

   :::
   ::::

   **You should see:** the status bar says "Building", then the pill goes away and the :term[Problems panel]{id=problems-panel} is empty.

   **If you do not see it:** open **Scripts ▸ Show Problems**. A missing `;` is the usual cause.

2. Create an entity named `Dice` and attach the script. Keep `Seed` at 1.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+**, choose an empty entity, rename it `Dice`, then choose **Add Component ▸ Script** and `DiceRoller`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Dice's ID>", "class": "DiceRoller", "fields": { "Seed": 1 } } }
   ```

   :::
   ::::

   **You should see:** a Script component with `Seed` 1 and `Rolled` 0.

   **If you do not see it:** the class list holds only built classes. Build again and reopen it.

3. Play, press **R** three times, stop, play again and press **R** three times. Then change `Seed` to 2 and repeat.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P** to play and again to stop. Read the **Console** panel.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<the Dice's ID>", "class": "DiceRoller", "field": "Seed", "value": 2 } }
   ```

   :::
   ::::

   **You should see:** the same three numbers in both runs with `Seed` 1, and another three with 2. Press **R** and build while the game plays: the next roll continues the sequence and does not start it over.

   **If you do not see it:** if the numbers differ between runs, the `Seed` field holds another value on the entity than you think. Select the entity and read it.

:::::

To change the recipe, set the seed from something that varies and keep it in a field where a replay can read it. Exercise 3 seeds a pour from a level number.

## Recipe 1: the coin

The coin spins, bobs, counts once when the player touches it and disappears. The Third Person sample's `Samples/ThirdPerson/Scripts/Coin.cpp` has it. Its entity is a static sphere **trigger**, a body that reports overlaps and pushes nothing, tagged `Coin`. The coin's model is a child of that entity. The script moves the model, not the trigger, so the trigger stays where it is.

:::question
What are `override` and a class built on another? See [C++ classes](../basics/cpp-classes.md): `override` replaces a function of the class above.
:::

The class opens with three fields, which the Inspector shows on every coin.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L10-L15"
class Coin : public Script
{
public:
	float SpinSpeed = 180.0f; // Degrees per second
	float BobHeight = 0.12f;  // Meters
	bool Collected = false;
```

The next excerpt finds the model. Read `OnCreate` for what it stores, and `OnReload` for the one-line trick.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L17-L26"
void OnCreate() override
{
	const std::vector<Entity> children = GetEntity().GetChildren();
	m_Visual = children.empty() ? Entity() : children.front();
	if (m_Visual.IsValid())
		m_VisualTranslation = m_Visual.GetTransform().GetTranslation();
	m_Phase = static_cast<float>(GetEntity().GetID() % 628) * 0.01f; // Coins bob out of step
}

void OnReload() override { OnCreate(); }
```

1. **Line 19:** the children of the coin entity; the first one is the model.
2. **Line 22:** the model's own position is kept, because the bob is added to it.
3. **Line 23:** a different phase per coin, from the number of its entity, so coins bob out of step.
4. **Line 26:** on a hot reload the script is made again with its plain members empty, so `OnReload` runs `OnCreate` to find the model again.

The spin and the bob run every frame.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L28-L36"
void OnUpdate(float deltaTime) override
{
	if (!m_Visual.IsValid())
		return;
	m_Time += deltaTime;
	TransformComponent transform = m_Visual.GetTransform();
	transform.SetRotation(glm::angleAxis(glm::radians(m_Time * SpinSpeed), glm::vec3(0.0f, 1.0f, 0.0f)));
	transform.SetTranslation(m_VisualTranslation + glm::vec3(0.0f, std::sin(m_Time * 2.5f + m_Phase) * BobHeight, 0.0f));
}
```

The rotation is a turn around the up axis of `m_Time * SpinSpeed` degrees, the same arithmetic as a coin turning 180 degrees each second: after 0.5 s it has turned 90 degrees. The height is a sine wave. With `BobHeight` 0.12, the model's height moves between 0.12 m below and 0.12 m above its resting place. The sine runs at `2.5` radians a second, so one bob takes $2\pi / 2.5 \approx 2.5$ s.

:::question
What does `CourseState*` mean, and what is `nullptr`? See [C++ memory](../basics/cpp-memory.md) for pointers.
:::

The collection is the part to copy exactly. It runs once, when something enters the trigger.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L38-L46"
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

The members that the excerpts use close the class, and the registration names the three fields.

```cpp src="Samples/ThirdPerson/Scripts/Coin.cpp#L47-L59"
private:
	Entity m_Visual;
	glm::vec3 m_VisualTranslation = glm::vec3(0.0f); // Where the model sits on the trigger
	float m_Time = 0.0f;
	float m_Phase = 0.0f;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(SpinSpeed);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(Collected);
}
```

1. **Lines 48–51:** plain members, which a hot reload empties; `OnReload` finds the model again.
2. **Lines 54–59:** one `ST_SCRIPT_FIELD` per field, so `Collected` shows and is saved like the other two.

Read the order of the checks. A coin that was collected, or an entering body that is not valid, or one without the tag `Player`, does nothing. Only then does the coin mark itself, tell the manager and hide. `Collected` is a field, and that has a use: a coin saved or reloaded as collected stays collected. The manager is found each time it is needed, by name, as [Timers and events](timers-events.md) taught, and checked for `nullptr` in case the scene has none.

:::::steps

1. Make the trigger, with a model as its child.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+** and choose an empty entity, rename it `Coin`. Choose **Add Component ▸ Sphere Collider** and **Add Component ▸ Rigid Body**, set **Type** to **Static** and enable **Is Trigger**. Add a **Tag** of `Coin`. Create a cylinder from the group of meshes without colliders, scale it flat, and drag its row onto `Coin` in the Hierarchy.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Coin", "components": { "Tag": { "Tag": "Coin" }, "SphereCollider": { "Radius": 0.5 }, "Transform": { "Translation": [0, 1, -3] } } } }
   ```

   Then give it the body:

   ```json
   { "command": "component.add", "parameters": { "entity": "<the Coin's ID>", "component": "RigidBody", "values": { "Type": "Static", "IsTrigger": true } } }
   ```

   Then add the model under it:

   ```json
   { "command": "entity.create", "parameters": { "name": "Coin Model", "parent": "<the Coin's ID>", "components": { "MeshRenderer": { "Mesh": "Builtin/Cylinder" }, "Transform": { "Scale": [0.8, 0.1, 0.8] } } } }
   ```

   :::
   ::::

   **You should see:** a wire sphere around the disc, and `Coin Model` under `Coin`.

   **If you do not see it:** if the disc does not sit inside the sphere, the model's Transform is local to its parent: give it the Translation 0, 0, 0.

2. Write the `Coin` script from the excerpts, in their order, with `GetScript` pointing at your `Scoreboard` and `AddPoint()` in place of `AddCoin`, or with `Log::Info("Coin collected")` in its place. Keep the first line of the file that **New Script...** writes, the include of the SDK, in place of the sample's `#include "CourseState.h"`, and add `#include <cmath>` for `std::sin`. Build, and attach it to `Coin`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Scripts ▸ New Script...**, type `Coin`, write the code, build with **Ctrl+B**, then choose **Add Component ▸ Script** on the entity.
   :::
   :::tab[With a command]
   No command writes code. Attach the built class:

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Coin's ID>", "class": "Coin" } }
   ```

   :::
   ::::

   **You should see:** the Script component with `Spin Speed` 180, `Bob Height` 0.12 and `Collected` off.

   **If you do not see it:** if the build says a class named `Coin` exists, you still have the script of [Physics](physics.md): replace its text.

3. Play and move the player into the coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, then drive the player through the trigger.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** the model spinning and bobbing, then gone when the player touches it, with one count on your manager or one log line.

   **If you do not see it:** if nothing is collected, check that the player's tag is `Player` and that it has a body with a :term[collider]{id=collider}. Two static bodies never report to each other.

:::::

To make it your own, change the fields: `SpinSpeed` and `BobHeight` are in the Inspector for every coin. Exercise 2 brings the coin back after a delay.

## Recipe 2: the seeded pour

A pour drops many balls at once from a loose column, so that they land as a pile. If every ball started in a perfect grid, the pile would look like a machine made it. So each ball gets a small random nudge. The seed makes the nudge the same on every run: the same seed pours the same pile, so you can run it again and get it again. A new seed per pour makes each pile different.

The Physics Playground sample has `SpawnBalls` in `Samples/PhysicsPlayground/Scripts/Playground.cpp`. It lays the balls on a grid, 0.6 m apart so none starts inside another, and moves each one by a random amount of at most 0.04 m in two directions. The grid arithmetic is the part to read by hand. Take 4 balls to a row, so 16 to a layer:

- Ball 21 is in layer $21 / 16 = 1$ (the division drops the remainder).
- Its place in the layer is $21 \bmod 16 = 5$, the remainder.
- Place 5 is column $5 \bmod 4 = 1$ and row $5 / 4 = 1$.

Take the spread 1.2 m. The sample's formula starts a row at $-1.2 + 0.3 = -0.9$ m and steps 0.6 m. Column 1 is then at $-0.9 + 0.6 = -0.3$ m, plus a nudge of up to 0.04 m either way.

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L257-L275"
void Playground::SpawnBalls(const glm::vec3& center, float spread, int32_t count, uint32_t seed)
{
	if (!Assets::IsLoaded(BallPrefab) || count <= 0)
		return;
	Random random(seed);
	std::vector<glm::mat4> transforms;
	transforms.reserve(static_cast<size_t>(count));
	// A loose column of balls, each layer offset at random, 0.6 m apart so none starts touching another.
	const int32_t perRow = std::max(1, static_cast<int32_t>(spread * 2.0f / 0.6f));
	for (int32_t index = 0; index < count; index++)
	{
		const int32_t layer = index / (perRow * perRow);
		const int32_t cell = index % (perRow * perRow);
		const glm::vec3 position = center + glm::vec3(-spread + 0.3f + static_cast<float>(cell % perRow) * 0.6f + random.Range(-0.04f, 0.04f),
			static_cast<float>(layer) * 0.6f, -spread + 0.3f + static_cast<float>(cell / perRow) * 0.6f + random.Range(-0.04f, 0.04f));
		transforms.push_back(glm::scale(glm::translate(glm::mat4(1.0f), position), glm::vec3(c_BallScale)));
	}
	Scene::InstantiateMany(BallPrefab, transforms);
}
```

1. **Line 261:** the generator is made from the seed passed in, so the same seed gives the same nudges.
2. **Line 265:** the balls per row follow from the spread.
3. **Lines 270–271:** a column or a row of the grid, plus a nudge from `Range`.
4. **Line 274:** one call makes every ball.

`c_BallScale` is a constant of the sample, `constexpr float c_BallScale = 0.5f;` above its class: the balls are half the size of the sphere of the :term[prefab]{id=prefab-make}. Write the same line above your class, and `#include <algorithm>` below the include of the SDK for `std::max`.

The last call is `Scene::InstantiateMany`. It takes the :term[prefab]{id=prefab-make} and a list of transform matrices, one per ball, and returns the new entities. The loop only builds that list: one `glm::mat4` per ball, made with `glm::translate` for the place and `glm::scale` for the size. Making hundreds of entities in one call is much cheaper than hundreds of separate calls, and [Performance](performance.md) teaches why. The call needs a loaded prefab, so the sample asks `Assets::IsLoaded` first and returns when it is not.

:::::steps

1. Make a ball prefab to pour: a sphere with a Sphere Collider and a dynamic :term[Rigid Body]{id=rigid-body}, saved as a prefab, as [Prefabs](prefabs.md) taught. Put the prefab and a field for it on a script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Build the ball, right-click it in the Hierarchy and choose **Create Prefab**. Then delete the ball from the scene.
   :::
   :::tab[With a command]
   Run the command, with the prefab's path.

   ```json
   { "command": "prefab.create", "parameters": { "entities": [ "<the ball's ID>" ], "path": "Prefabs/PourBall.stprefab" } }
   ```

   :::
   ::::

   **You should see:** `PourBall.stprefab` in the Content Browser.

   **If you do not see it:** if the command says the entity is unknown, read its identifier from the Hierarchy.

2. Write a `Pourer` script with a prefab field `BallPrefab`, the fields `Seed`, `Count` and `Spread`, and a `Pour` function made from the excerpt; a `Spread` of 1.2 gives 4 balls per row. The prefab is rarely loaded when `OnCreate` runs, so request its load there with `Assets::RequestLoad`. Call `Pour` from `OnUpdate` on the first frame that `Assets::IsLoaded` is true, with a `bool` member so it pours once.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the script as before, build it, add it to an empty entity and drag the prefab onto `Ball Prefab`.
   :::
   :::tab[With a command]
   No command writes code. Set the fields:

   ```json
   { "command": "script.setField", "parameters": { "entity": "<the Pourer's ID>", "class": "Pourer", "field": "Seed", "value": 5 } }
   ```

   :::
   ::::

   **You should see:** the fields `Ball Prefab`, `Seed`, `Count` and `Spread` in the Inspector.

   **If you do not see it:** if the prefab field is empty, the script spawns nothing: the sample returns silently in that case, so log it in yours.

3. Play with `Seed` 5 twice, then once with 6.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, watch the pile, stop, and play again.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** the same pile in both runs with 5, and a slightly different one with 6.

   **If you do not see it:** if the two piles with 5 differ, something else moves the balls, such as a player that walks into them. The nudges themselves repeat exactly.

:::::

To change it, move the center, the spread and the count, or add a `Chance` per ball to skip some.

## Recipe 3: the grab tool

A grab tool lets the player hold a body with the cursor and carry it. Strata has no ready tool for it, and one is built from three pieces: the ray through the cursor, a :term[raycast]{id=raycast} to find the body, and a velocity that pulls the body toward a point. The Physics Playground does it in `Playground::UpdateGrab`. It runs every :term[fixed step]{id=fixed-step} from `OnFixedUpdate`, because it sets a velocity and physics runs in fixed steps.

:::question
What are `std::optional` and `std::string`? See [Modern C++](../basics/cpp-modern.md) for `std::optional`, which holds a value or nothing.
:::

The pointer ray is the one of [Gameplay math](gameplay-math.md), here called `GetPointerRay`. The first half of `UpdateGrab` decides what is held. Read what happens when **E** is not down.

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L223-L245"
void Playground::UpdateGrab()
{
	if (!Input::IsKeyDown(Key::E))
	{
		m_Grabbed = Entity();
		return;
	}
	glm::vec3 origin;
	glm::vec3 direction;
	if (!GetPointerRay(origin, direction))
		return;
	if (!m_Grabbed.IsValid())
	{
		// The body under the cursor, if it is one of the playground's.
		const std::optional<RaycastHit> hit = Physics::Raycast(origin, direction, 60.0f);
		if (!hit || !hit->HitEntity.IsValid())
			return;
		const std::string tag = hit->HitEntity.GetTag();
		if (tag != "Crate" && tag != "Domino" && tag != "Ball" && tag != "Ghost" && tag != "Pin")
			return;
		m_Grabbed = hit->HitEntity;
		m_GrabDistance = std::min(hit->Distance, GrabDistance);
	}
```

1. **Lines 225–229:** releasing **E** forgets the held body.
2. **Line 237:** a ray of 60 m from the camera through the cursor finds the body under it.
3. **Lines 240–242:** only bodies with a tag from the list can be held; the ground cannot.
4. **Line 244:** the holding distance is the hit distance, but never more than the `GrabDistance` field.

The second half moves the body.

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L246-L255"
	// Pulled toward a point in front of the camera with a speed that closes the gap within a few steps.
	const glm::vec3 target = origin + direction * m_GrabDistance;
	RigidBody body = m_Grabbed.GetRigidBody();
	glm::vec3 velocity = (target - m_Grabbed.GetTransform().GetWorldPosition()) * 10.0f;
	const float speed = glm::length(velocity);
	if (speed > 20.0f)
		velocity *= 20.0f / speed;
	body.SetLinearVelocity(velocity);
	body.SetAngularVelocity(body.GetAngularVelocity() * 0.9f);
}
```

1. **Line 247:** the target is a point on the ray at the holding distance.
2. **Line 249:** the velocity points at the target and is 10 times the gap.
3. **Lines 251–252:** a velocity longer than 20 m/s is scaled down to 20 m/s, same direction.
4. **Line 254:** the spin shrinks to 0.9 of itself each step.

The target is a point on the ray at the holding distance. The velocity points at the target and is 10 times the gap in metres. Two gaps by hand:

- A body 0.5 m from the target gets $0.5 \times 10 = 5$ m/s.
- A body 5 m away would get 50 m/s, so the cap scales it to 20 m/s: the length of the velocity is 50, and it is multiplied by $20 / 50$.

A fixed step is 1/60 s, so a body at 5 m/s moves $5 / 60 \approx 0.083$ m a step. That is a sixth of the 0.5 m gap, because the speed is 10 times the gap and a step lasts 1/60 s. Each step removes a sixth of what remains, so after 10 steps about $(5/6)^{10} \approx 0.16$ of the gap remains. The held body comes to the cursor smoothly and stops without overshooting. The last line multiplies the spin by 0.9 every step, so a held body stops tumbling: after 10 steps $0.9^{10} \approx 0.35$ of the spin is left.

:::::steps

1. Write the pointer ray as your `Grabber` script's function, from [Gameplay math](gameplay-math.md), and the two halves of `UpdateGrab` as `OnFixedUpdate`. Give the :term[script fields]{id=script-field} `GrabDistance` (12) and a tag list of your own.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the script, write the code, build with **Ctrl+B** and add it to the entity `Main Camera`.
   :::
   :::tab[With a command]
   No command writes code. Attach the built class:

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Main Camera's ID>", "class": "Grabber", "fields": { "GrabDistance": 12 } } }
   ```

   :::
   ::::

   **You should see:** the Script component with `Grab Distance` 12.

   **If you do not see it:** if the build fails on `RaycastHit`, you may have omitted the SDK include line `#include "StrataScript/StrataScript.h"`.

2. Give some bodies a tag of the list, such as `Crate`: add a **Tag** component and a dynamic Rigid Body with a collider.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select a box, choose **Add Component ▸ Rigid Body**, then **Add Component ▸ Tag** and type `Crate`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.add", "parameters": { "entity": "<the box's ID>", "component": "Tag", "values": { "Tag": "Crate" } } }
   ```

   :::
   ::::

   **You should see:** a **Tag** section reading `Crate`.

   **If you do not see it:** if the box falls through the ground, it needs a Box Collider as well.

3. Play, hold **E** over a crate and move the mouse.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**. Put the cursor on the crate and hold **E**.
   :::
   :::tab[With a command]
   Run the command, then use the keyboard and mouse in the game.

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** the crate follows the cursor and stops tumbling. Release **E** and it falls.

   **If you do not see it:** if the crate does not move, check that the body is dynamic and that the tag is in your list.

:::::

To make it your own, change the cap of 20 m/s for a heavier feel, the factor 10 for a looser or a tighter pull, or the key. Raycasts are the subject of [Physics](physics.md); the grab only uses the first hit.

## Recipe 4: impact sounds with a budget

A ball that hits a crate should make a sound, louder when the hit is harder. A pour has hundreds of contacts in the same frame. A sound per contact would play hundreds of voices at once, loud and muddy, and costs time; the recipe plays a few. The tool is a **token bucket**: a counter that holds tokens. It gains them at a fixed rate up to a capacity, and each action costs one, so an action happens only while a token is there.

:::question
What is `constexpr`? See [Modern C++](../basics/cpp-modern.md): it marks a value the compiler knows before the program runs.
:::

The Physics Playground's `Samples/PhysicsPlayground/Scripts/Impact.cpp` has two parts. The first is the bucket, a variable outside any class, in a `namespace` with no name. Such a variable exists once for the whole script module and is shared by every instance of every script in it. That sharing is the point: all bodies draw from one bucket. It lasts while the module stays loaded.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L13-L36"
namespace
{

	constexpr int32_t c_MaxSoundsPerFrame = 8;
	constexpr float c_SoundsPerSecond = 16.0f;
	constexpr const char* c_SoundPaths[] = { "Sounds/Impacts/Wood.ogg", "Sounds/Impacts/Metal.ogg", "Sounds/Impacts/Soft.ogg" };

	// One budget for every body of the module: tokens that refill at c_SoundsPerSecond of real time, up to a frame's worth.
	float s_Tokens = static_cast<float>(c_MaxSoundsPerFrame);
	double s_LastRealTime = 0.0;

	bool TakeSoundBudget()
	{
		const double now = Time::GetRealTime();
		const float elapsed = static_cast<float>(std::max(0.0, now - s_LastRealTime));
		s_Tokens = std::min(static_cast<float>(c_MaxSoundsPerFrame), s_Tokens + elapsed * c_SoundsPerSecond);
		s_LastRealTime = now;
		if (s_Tokens < 1.0f)
			return false;
		s_Tokens -= 1.0f;
		return true;
	}

}
```

1. **Line 16:** the bucket holds 8 tokens at most, so 8 sounds can start in one frame.
2. **Line 17:** it refills at 16 tokens a second.
3. **Lines 21–22:** the tokens and the time of the last call, shared by every body.
4. **Line 26:** real time, which keeps running when the game is paused or slowed.
5. **Lines 28–33:** add the tokens earned since the last call, never above 8, and take one if a whole token is there.

A worked example. The bucket is full at the start of a pour: 8 tokens. In the first frame 300 contacts ask. The first 8 get a token and sound, and the other 292 are refused. The next frame comes 1/60 s later and earns $16 / 60 \approx 0.27$ tokens: under 1, so no sound.

After 4 frames, 1.07 tokens have come back, so one sound plays. A pour that lasts 5 s plays at most $8 + 16 \times 5 = 88$ sounds: a few voices at a time instead of three hundred.

```mermaid caption="The token bucket: each ask adds the tokens earned, capped at the capacity, then takes one token if one is there." alt="Diagram: an impact asks. The bucket adds the tokens earned since the last ask, up to its capacity. With at least one token it takes one and the sound plays; otherwise the sound is skipped."
flowchart TD
    A[Impact asks] --> B[Add the tokens earned, up to the capacity]
    B --> C{At least 1 token?}
    C -->|Yes| D[Take one token and play the sound]
    C -->|No| E[Skip the sound]
```

Above the bucket, the sample includes two headers of the standard library after the include of the SDK: `<algorithm>` for `std::min`, `std::max` and `std::clamp`, and `<cstdint>` for `int32_t`. Without `<algorithm>` the build fails with C2039, "'clamp': is not a member of 'std'".

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L6-L11"
#include "StrataScript/StrataScript.h"

#include <algorithm>
#include <cstdint>

using namespace Strata;
```

The class opens with its three fields, and both `OnCreate` and `OnReload` look the sound up.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L38-L46"
class Impact : public Script
{
public:
	int32_t Kind = 0;            // 0 wood, 1 metal, 2 soft
	float MinSpeed = 1.5f;       // m/s of the two bodies toward each other below which nothing sounds
	float FullVolumeSpeed = 10.0f;

	void OnCreate() override { FindSound(); }
	void OnReload() override { FindSound(); }
```

The second part is the hit. The script does not track every body's speed. It reads the velocities when the contact is reported, after the step that resolved it, so the bodies already move apart. How fast they move apart along the contact's normal, the direction that leaves the surface they touched, tells a hard hit from a touch.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L48-L61"
void OnCollisionEnter(const Collision& collision) override
{
	// The contact is reported after the step that resolved it, so the bodies already move apart: how fast they move
	// along the contact's normal now (a bounce keeps most of the impact's speed, a thud little), plus how fast either
	// still moves, tells a hard hit from a touch without tracking every body's velocity every step.
	const glm::vec3 own = GetEntity().GetRigidBody().GetLinearVelocity();
	const glm::vec3 other = collision.Other.IsValid() ? collision.Other.GetRigidBody().GetLinearVelocity() : glm::vec3(0.0f);
	const float separating = std::abs(glm::dot(own - other, collision.Normal));
	const float speed = separating + 0.5f * std::max(glm::length(own), glm::length(other));
	if (speed < MinSpeed || !m_Sound.IsValid() || !TakeSoundBudget())
		return;
	const float volume = std::clamp(speed / FullVolumeSpeed, 0.1f, 1.0f);
	Audio::PlayOneShotAt(m_Sound, collision.Point, volume, 0.9f + 0.2f * std::min(1.0f, speed / FullVolumeSpeed));
}
```

1. **Line 55:** the dot product of the velocity difference with the normal gives the speed along the normal; the absolute value drops the sign.
2. **Line 56:** half of the faster body's own speed is added, so a body that slides hard also sounds.
3. **Line 57:** a hit under `MinSpeed`, or a missing sound, or an empty bucket plays nothing.
4. **Line 59:** the volume is the speed over `FullVolumeSpeed`, kept between 0.1 and 1.
5. **Line 60:** the sound plays at the contact point, with a higher pitch for a harder hit.

Three hits by hand, with a normal of $(0, 1, 0)$ and the default fields. A ball bounces away from the floor with velocity $(0, 3, 0)$: it separates at 3 m/s, so the speed is $3 + 0.5 \times 3 = 4.5$ m/s. The volume is $4.5 / 10 = 0.45$ and the pitch $0.9 + 0.2 \times 0.45 = 0.99$. A touch with velocity $(0, 0.5, 0)$ gives $0.5 + 0.25 = 0.75$, under the minimum of 1.5, so it is silent. A hard hit with $(0, 12, 0)$ gives 18, so the volume is capped at 1 and the pitch is 1.1.

The class ends with the lookup. `Kind` chooses one of the three paths, and a sound the project lacks is reported once.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L63-L87"
	void FindSound()
	{
		const char* path = c_SoundPaths[std::clamp(Kind, 0, 2)];
		m_Sound = Assets::Find(path);
		if (!m_Sound.IsValid())
		{
			// A game exported without it (the project's alwaysInclude names Sounds/Impacts): said once, the bodies stay silent.
			static bool s_Reported = false;
			if (!s_Reported)
				Log::Warn("Playground: the impact sound '", path, "' is not in the game");
			s_Reported = true;
			return;
		}
		Assets::RequestLoad(m_Sound);
	}
private:
	AssetHandle m_Sound;
};

ST_SCRIPT_CLASS(Impact)
{
	ST_SCRIPT_FIELD(Kind);
	ST_SCRIPT_FIELD(MinSpeed);
	ST_SCRIPT_FIELD(FullVolumeSpeed);
}
```

1. **Line 65:** `std::clamp` keeps `Kind` between 0 and 2, so a wrong number still picks a path.
2. **Lines 67–75:** without the clip the script warns once for every body together and stays silent.
3. **Line 76:** the load starts at once, so the clip is ready by the first hits.

[Gameplay math](gameplay-math.md) left the impact sounds to this page: the strength comes from the dot product taught there, and the budget from here.

:::::steps

1. Copy three short clips into `Sounds/Impacts` of your project, named `Wood.ogg`, `Metal.ogg` and `Soft.ogg`, and import them as [Sound](sound.md) taught. The Physics Playground's own clips have these names: they are in the Strata folder under `Samples/PhysicsPlayground/Assets/Sounds/Impacts/`. They come from Kenney under the Creative Commons zero license (:term[CC0]{id=cc0}), which has no conditions, as the sample's `CREDITS.md` says.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the three `.ogg` files with your file browser into the project's `Assets/Sounds/Impacts` folder. The editor imports them when it sees them.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "files": ["<Strata folder>/Samples/PhysicsPlayground/Assets/Sounds/Impacts/Wood.ogg", "<Strata folder>/Samples/PhysicsPlayground/Assets/Sounds/Impacts/Metal.ogg", "<Strata folder>/Samples/PhysicsPlayground/Assets/Sounds/Impacts/Soft.ogg"], "directory": "Sounds/Impacts" } }
   { "command": "asset.list", "parameters": { "path": "Sounds/Impacts/" } }
   ```

   :::
   ::::

   **You should see:** three clips in the Content Browser under `Sounds/Impacts`.

   **If you do not see it:** if the folder is empty, the files went to another place. The script finds clips by the path `Sounds/Impacts/Wood.ogg`.

2. Write an `Impact` script from the excerpts, in the file's order: the include and the bucket, the class head, the hit, then the sound's lookup and the registration. Add it to the ball prefab and to the crates.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the script, write the code and build. Select the entity or the prefab, then choose **Add Component ▸ Script** and `Impact`.
   :::
   :::tab[With a command]
   No command writes code. Attach it:

   ```json
   { "command": "script.add", "parameters": { "entity": "<the crate's ID>", "class": "Impact", "fields": { "Kind": 0 } } }
   ```

   :::
   ::::

   **You should see:** the Script component with `Kind` 0, `Min Speed` 1.5 and `Full Volume Speed` 10.

   **If you do not see it:** if the log warns that an impact sound is not in the game, a path is wrong.

3. Play, drop a ball on a crate, then run the pour of Recipe 2.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P** and listen.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** a clear sound for one ball, louder for a hard hit, and during the pour a few voices, not a roar.

   **If you do not see it:** if the pour is silent, the clips are not loaded yet: the script requests them in `OnCreate`, so wait a moment after play starts.

:::::

To make it your own, change the two constants for a denser or a sparser mix, or the `Kind` field per body.

## Result

You can use `Random` for variety and for replays. You have four scripts from the samples working in your own project: a coin that counts once, a pile that a seed decides, a tool that holds bodies and impact sounds within a budget.

The Open World sample has a fifth recipe, a day and night cycle in `DayNight.h`. It belongs with the times of day and baked reflection probes of [Reflections](reflections.md).

## Variations

- **A seed from the level.** Seed a pour with a number that varies: each level then pours its own pile, and the same level pours the same pile. Exercise 3 builds it.
- **A seed for a test.** Fix the seed in the field when you test, so every run drops the same pile, and change it back for the game.
- **A coin that returns.** A :term[one-shot]{id=one-shot} `Timer` brings a coin back after a delay. Exercise 2 builds it.
- **A different budget.** A budget of 2 sounds a frame and 6 a second gives a sparse, dry mix; one of 16 and 40 a rich one. The two constants decide, and nothing else changes.
- **Other bodies in the grab list.** Add your own tags to the list, or take any body with a rigid body by dropping the tag test.

## Summary

- A seed makes `Random` give the same sequence on every computer; seed from a changing value for variety and from a field for a replay.
- The coin finds its model in `OnCreate` and again in `OnReload`, collects once on a trigger tagged `Player`, tells the manager and hides.
- The pour builds a list of transforms with a seeded nudge per ball and makes all balls in one call.
- The grab sets a velocity toward a point, 10 times the gap and capped at 20 m/s, and damps the spin.
- A token bucket shared by every body keeps impact sounds to 8 a frame and 16 a second on average.

## Check yourself

1. A game seeds `Random` with 5 for its level 5 and runs on Windows and on Linux. What does a player on each system see in the pour, and what would `Random random;` give instead?

   :::answer{tests="random-seed"}
   Both see the same pile, because the SDK's generator is compiled into the module and gives the same numbers for a seed on every platform. A generator made without a seed starts from 0, so every level would pour the same pile, run after run.
   :::

2. Why does the coin test `Collected` first, and why does `OnReload` call `OnCreate`?

   :::answer{tests="coin"}
   A trigger can report the player more than once, and the test makes the coin count once. `OnReload` runs on a new instance whose plain members, such as the model's entity, are empty, so `OnCreate` finds them again.
   :::

3. A pour has 4 balls to a row. In which layer, column and row is ball 21?

   :::answer{tests="pour"}
   A layer holds $4 \times 4 = 16$ balls, so ball 21 is in layer $21 / 16 = 1$ and at place $21 \bmod 16 = 5$ of it. That is column $5 \bmod 4 = 1$ and row $5 / 4 = 1$.
   :::

4. A held crate is 1.5 m from its target, and another is 4 m away. What velocity does the grab set for each?

   :::answer{tests="grab"}
   The first gets $1.5 \times 10 = 15$ m/s, under the cap. The second would get 40 m/s, so the length is cut to 20 m/s, in the same direction.
   :::

5. The bucket holds 8 tokens and refills at 16 a second. In one frame 20 contacts ask. How many sounds play, and when does the next one play, at 60 frames per second?

   :::answer{tests="token-bucket"}
   Eight sounds play and the other 12 are refused. A frame earns $16 / 60 \approx 0.27$ tokens, so a whole token is back after 4 frames, about 0.07 s later, and one sound plays then.
   :::

## Exercises

1. **Basic.** Make the coin's trigger with commands only: an entity `Coin` with the tag `Coin`, a Sphere Collider and a static Rigid Body with **Is Trigger** enabled.

   :::answer[Worked solution]{tests="coin" solution="tutorials/make/recipes/exercise-1.tutorial.json"}
   The file creates the entity with its tag and collider, adds the body, and reads the body's `Type` and `IsTrigger`, the collider's `Radius` and the tag back to check them.
   :::

2. **Medium.** Make the coin return after 10 s, with a `Timer`.

   :::answer[Worked solution]{tests="coin"}
   Hide only the model, never the coin's own entity, so the coin's script keeps running to count the delay. In `OnTriggerEnter`, replace `GetEntity().SetActive(false)` with `m_Visual.SetActive(false)` and start a member `Timer m_Back` with `m_Back.Start(10.0f)`. In `OnUpdate`, before the early return, add `if (m_Back.Update(deltaTime) > 0)`, and inside it set the field `Collected` to false and call `m_Visual.SetActive(true)`. The trigger still reports while the model is hidden, and the test at the top of `OnTriggerEnter` refuses it. A `Timer` is a plain member, so a hot reload stops it: the coin stays hidden until you collect it again, unless you keep the remaining time in a field.
   :::

3. **Medium.** Seed the pour from the level number, so that each level pours its own pile and the same level the same one.

   :::answer[Worked solution]{tests="pour random-seed"}
   Add an `int32_t Level` field, and pass `static_cast<uint32_t>(Level)` as the seed of `SpawnBalls` instead of the counter the sample keeps. Level 3 then draws the same nudges in every run and on every computer, and level 4 draws others. A level 0 gives the seed 0, the sequence of a generator made without a seed: it is fine, but it is the same pile for every game that forgot to seed.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Gameplay.h` holds `Random`, `Timer`, `KeyRepeat` and `Motion`.
- `Samples/ThirdPerson/Scripts/Coin.cpp` is the coin, and `Samples/ThirdPerson/Scripts/CourseState.h` is the manager it calls.
- `Samples/PhysicsPlayground/Scripts/Playground.cpp` holds `SpawnBalls` and `UpdateGrab`.
- `Samples/PhysicsPlayground/Scripts/Impact.cpp` holds the token bucket and the hit's strength.
- `StrataScriptCore/Include/StrataScript/Scene.h` declares `Scene::InstantiateMany`.

## Further reading

- cppreference, "Pseudo-random number generation" (<https://en.cppreference.com/w/cpp/numeric/random>): the standard library's generators and distributions; intermediate.
- Melissa O'Neill, "PCG: A Family of Better Random Number Generators": the design behind `Random`; advanced.

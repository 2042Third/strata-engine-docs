---
id: make/script-fields
title: "Tuning scripts from the editor: fields, references and prefabs"
description: "Expose the values of a crate spawner as script fields, wire an entity and a prefab into it from the Inspector, and spawn safely."
kind: how-to
size: M
tracks: [G]
needs: [make/project-coin-run]
time: 60
learn:
  - id: field-types
    text: name the ten script field types and choose a way around a type that does not exist
  - id: wire-references
    text: set an entity field and an asset field in the Inspector and reset a field to its default
  - id: safe-spawn
    text: write a spawner that asks for its prefab early and handles a prefab that is not loaded yet
  - id: values-lifetime
    text: predict what happens to a field's value when you play, stop, hot reload, rename a field or rename a class
  - id: prefab-fields
    text: change a field on a prefab instance, then apply the change to the prefab or revert it
since: 0.3.0
status: final
---

A script is code, and code is slow to change: every new number needs an edit, a build and a wait. In this how-to you keep the numbers out of the code. You build a crate spawner whose interval, limit, spawn point and crate all come from the **Inspector**, so you tune the game while you watch it. Before you start:

- You can write, build and attach a script, as [Your first script](first-script.md) taught.
- You know prefabs, instances, **Apply to Prefab** and **Revert**, from [Prefabs](prefabs.md).
- You know that **Play** runs a copy of the scene and **Stop** discards it, from [Play and test](play-test-debug.md).
- A new project from the **Basic 3D** template is open. Name it `ScriptFields`.

## Why fields exist

Suppose a spawner drops a crate every 2 seconds, and you want 3 seconds. In the code you change `2.0f` to `3.0f`, build and play again. With ten such numbers and a game you want to feel right, you rebuild a hundred times.

A **script field** is a value that the class registers with `ST_SCRIPT_FIELD`, as [Your first script](first-script.md) showed for one float. The Inspector draws it, and every entity that carries the script keeps its own value. The value lives in the scene, not in the code, so changing it needs no build.

Strata offers exactly ten types of field. A type outside this list has no widget, and the build refuses it.

| Type in code | The Inspector shows | Default when you write nothing |
| --- | --- | --- |
| `bool` | a check box | `false` |
| `int32_t` | a whole-number box | 0 |
| `float` | a number box | 0 |
| `glm::vec2` | two number boxes | all 0 |
| `glm::vec3` | three number boxes | all 0 |
| `glm::vec4` | four number boxes | all 0 |
| `glm::quat` | a rotation widget | all 0, which is no valid rotation |
| `std::string` | a text box | empty text |
| `Entity` | an entity picker | no entity |
| `AssetHandle` | an asset picker | no asset |

The default of a field is the value it has in a freshly made instance, so the class decides it with the value after the `=`. The table says what Strata gives when you write nothing: it fills a new instance with zeros. For the rotation, always write one: the rotation `glm::quat(1.0f, 0.0f, 0.0f, 0.0f)` means no turn.

### What you cannot expose

A `std::vector`, an array, an enum, a `double`, an `int64_t` or a :term[struct]{id=struct} is not a field type. Registering one stops the build with the message `Unsupported script field type`, followed by the list of the ten.

Three ways around it cover almost every case:

- Several fields instead of a list: `Waypoint1`, `Waypoint2` and `Waypoint3`, each an `Entity`.
- An `int32_t` for an enum: 0 is `Idle`, 1 is `Walking`. Name the numbers in a comment next to the field.
- A `std::string` for a name or a short list that the script splits.

A `double` is rarely needed: a `float` holds about seven digits, which is enough for a speed or a delay. For a 64-bit number, a string carries it.

## Write the spawner

You need three things in the scene before the code does anything: a crate to spawn, a place to spawn it, and the script. The first two are quick, and the steps below make them.

The class has one field of each type. Four of them work in this page's spawner: `Enabled` switches it, `MaxCrates` limits it, `Interval` times it, and `Offset` lifts the crate above the spawn point. `SpawnPoint` and `CratePrefab` are the two references. The other four, `Jitter`, `Tint`, `Tilt` (applied as the crate's turn) and `Label`, only show their types.

:::::steps

1. Make the crate prefab and the spawn point. The steps of [Prefabs](prefabs.md) made a prefab from an entity.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+** in the Hierarchy and choose **Cube**: the cube comes with a **Box Collider**. Rename the cube `Crate`, then use **Add Component** to add a **Rigid Body** and keep its type dynamic. Right-click `Crate`, choose **Create Prefab**, and delete the entity from the scene so that only the file remains. Click **+**, choose **Empty** and rename it `Spawn Point`. Set its **Translation** to 0, 3, 0.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Crate", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "RigidBody": {} } } }
   { "command": "prefab.create", "parameters": { "entities": ["<id of Crate>"], "path": "Prefabs/Crate.stprefab" } }
   { "command": "entity.delete", "parameters": { "entities": ["<id of Crate>"] } }
   { "command": "entity.create", "parameters": { "name": "Spawn Point", "components": { "Transform": { "Translation": [0, 3, 0] } } } }
   ```

   A command adds only the components it names: without the **Box Collider**, the crate has no shape that touches anything, and it hangs in the air.
   :::
   ::::

   **You should see:** `Prefabs/Crate.stprefab` in the Content Browser, and a `Spawn Point` row in the Hierarchy with no icon but the empty entity's.

   **If you do not see it:** the **Create Prefab** entry is missing in the menu of another row. Right-click the row `Crate` itself.

:::::

## Make the class and its fields

:::question
What do `class`, `: public` and `override` mean? See [C++ classes](../basics/cpp-classes.md) and [Programming 3](../basics/programming-3.md).
:::

The file below holds the whole class head, with the ten fields. Read it from the top: the first 7 lines are the opening you know, and the lines after them list the fields.

```cpp src="book:tutorials/make/script-fields/Spawner.cpp#L1-L17"
#include "StrataScript/StrataScript.h"

using namespace Strata;

class Spawner : public Script
{
public:
	bool Enabled = true;
	int32_t MaxCrates = 5;
	float Interval = 2.0f;
	glm::vec2 Jitter = glm::vec2(0.0f);
	glm::vec3 Offset = glm::vec3(0.0f, 1.0f, 0.0f);
	glm::vec4 Tint = glm::vec4(1.0f);
	glm::quat Tilt = glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	std::string Label = "Crates";
	Entity SpawnPoint;
	AssetHandle CratePrefab;
```

1. **Lines 8–10:** a `bool`, an `int32_t` and a `float` with plain defaults.
2. **Lines 11–15:** the vectors, the rotation and the text. Each is written with its default after the `=`.
3. **Lines 16–17:** `SpawnPoint` is an `Entity` and `CratePrefab` is an `AssetHandle`. Neither has a default: the Inspector starts them as None.

The rest of the file registers the fields. A field that is declared but not listed in `ST_SCRIPT_CLASS` stays a plain member: it never appears in the Inspector and never keeps a value.

```cpp src="book:tutorials/make/script-fields/Spawner.cpp#L47-L59"
ST_SCRIPT_CLASS(Spawner)
{
	ST_SCRIPT_FIELD(Enabled);
	ST_SCRIPT_FIELD(MaxCrates);
	ST_SCRIPT_FIELD(Interval);
	ST_SCRIPT_FIELD(Jitter);
	ST_SCRIPT_FIELD(Offset);
	ST_SCRIPT_FIELD(Tint);
	ST_SCRIPT_FIELD(Tilt);
	ST_SCRIPT_FIELD(Label);
	ST_SCRIPT_FIELD(SpawnPoint);
	ST_SCRIPT_FIELD(CratePrefab);
}
```

1. **Lines 47–59:** one `ST_SCRIPT_FIELD` per field, named exactly as the member. The name is the key under which every scene stores the value, as the section on renaming shows later.

:::::steps

1. Create the script and put the file in place. Replace the new file's content with `Spawner.cpp`, the whole file of this page, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...**, type `Spawner` and press **Create**. Paste the file into `Scripts/Spawner.cpp`. Press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Spawner" } }
   ```

   :::
   ::::

   **You should see:** the **Build Scripts** button reads "Building" with a count of seconds, then **Build Scripts** again. The :term[Problems panel]{id=problems-panel} stays empty.

   **If you do not see it:** the message `Unsupported script field type` means that a registered field has another type. Check that every field has one of the ten types.

:::::

## What the spawner does with them

:::question
What do `override` and a function that the engine calls mean? See [C++ classes](../basics/cpp-classes.md) and [Programming 3](../basics/programming-3.md).
:::

The class has one more job than keeping values. It must make a crate every `Interval` seconds, up to `MaxCrates`. The code applies three rules of the script application programming interface (API); the lines after the fence show them.

```cpp src="book:tutorials/make/script-fields/Spawner.cpp#L19-L40"
void OnCreate() override
{
	Assets::RequestLoad(CratePrefab);
}

void OnUpdate(float deltaTime) override
{
	if (!Enabled || m_Spawned >= MaxCrates || !SpawnPoint.IsValid())
		return;

	m_Waited += deltaTime;
	if (m_Waited < Interval || !Assets::IsLoaded(CratePrefab))
		return;

	const glm::vec3 where = SpawnPoint.GetTransform().GetWorldPosition() + Offset;
	const Entity crate = Scene::Instantiate(CratePrefab, where, Tilt);
	if (!crate.IsValid())
		return;

	m_Waited = 0.0f;
	m_Spawned++;
}
```

1. **Lines 19–22:** `OnCreate` asks for the crate prefab at once. A prefab is a file, and files load in the background; asking early gives the load time to finish.
2. **Line 26:** nothing happens while the spawner is off, full, or has no spawn point. `IsValid` is true for an entity that exists.
3. **Lines 29–31:** the spawner counts time by adding each frame's `deltaTime`, and waits for the interval and for the prefab.
4. **Lines 33–36:** the crate appears at the spawn point plus `Offset`. `Instantiate` gives back an empty entity when the prefab is not loaded, so the code checks the answer.

The class ends with the two plain members that the update counts with, then the registration shown above.

```cpp src="book:tutorials/make/script-fields/Spawner.cpp#L42-L45"
private:
	float m_Waited = 0.0f;
	int32_t m_Spawned = 0;
};
```

Take numbers to see how it behaves. At 60 frames per second a frame lasts 0.0167 s, so with `Interval` 2 the timer passes 2 after about 120 frames, and the first crate appears. The timer then returns to 0, so the next one comes 2 s later. With `MaxCrates` 5, the fifth crate appears at about 10 s, and the spawner stops there.

:::why
`Instantiate` never waits for a load. A call that blocked would freeze every frame until the file arrived. Strata starts the load, hands you an empty entity, and lets you try again in the next frame.
:::

## Tune the fields

:::::steps

1. Attach the script to the spawner entity.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+** and choose **Empty**, rename it `Spawner`, and click **Add Component**. Find **Script** in its list. In the Script section open **Add Script...** and click `Spawner`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<id of Spawner>", "class": "Spawner" } }
   ```

   :::
   ::::

   **You should see:** a `Spawner` header in the Script section with ten rows, from `Enabled` to `Crate Prefab`. Each row has its default and a reset button at the right.

   **If you do not see it:** the section says "No :term[script module]{id=script-module} is loaded: build the scripts (Scripts > Build Scripts) to edit their fields." Press **Ctrl+B** and wait for the build.

   ::figure{id=fields}

2. Set the two references.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `Spawn Point` from the Hierarchy onto the `Spawn Point` row, or click the row and choose it from the list. Drag `Crate.stprefab` from the Content Browser onto the `Crate Prefab` row.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<id of Spawner>", "class": "Spawner", "field": "CratePrefab", "value": "Prefabs/Crate.stprefab" } }
   ```

   :::
   ::::

   **You should see:** the rows show the name `Spawn Point` and the name of the crate prefab. Their reset buttons are now active, and a tooltip on the label says "overridden on this entity".

   **If you do not see it:** the asset row takes any kind of asset, so check that it names the prefab, not the crate's mesh: a mesh there spawns nothing.

3. Change a number and then take it back. Set `Interval` to 1 and `Max Crates` to 3, then press the reset button of `Interval`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type the numbers into the rows. Click the round arrow at the right of `Interval`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<id of Spawner>", "class": "Spawner", "field": "Interval", "value": null } }
   ```

   :::
   ::::

   **You should see:** `Interval` is back to 2 and its reset button is dim: the button says "Uses the class default". `Max Crates` keeps 3.

   **If you do not see it:** if `Interval` shows 1 again, your click missed the button: the arrow sits in the narrow column at the far right.

:::::

A value is stored on the entity only once you set it. A row you never touched holds no value: it uses the class's value. If you later change a default in the code, every entity without its own value gets the new default, and the entities with their own value keep it.

## What the editor tells you

The Script section answers three situations in words, and one limit.

- **No script module:** until a build has succeeded, it says "No script module is loaded: build the scripts (Scripts > Build Scripts) to edit their fields."
- **Several entities selected:** it says "Select one entity to edit its scripts". Scripts are edited one entity at a time. To tune many, put the script on a prefab and change the value there, as the last part of this page shows.
- **An unknown class:** an entry whose class the module lacks shows "The script module has no class" and its name, with its stored values as plain text. They come back when the class does.

## Play, and change values while playing

:::::steps

1. Press **Play** (**Ctrl+P**). Watch the Scene view. While the game plays, set `Interval` to 0.5 in the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, then change `Interval` in the Inspector. Press **Stop**.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** with the interval at 2, a crate falls every 2 s from the spawn point until three are there. Each falls straight onto the one before, so the three form a stack. The new interval takes effect at once, without a rebuild. After **Stop** the crates are gone and `Interval` shows the value from before you played.

   **If you do not see it:** no crate means the prefab did not load or `Spawn Point` is empty. The row says None when no entity or asset is set. A crate that appears in the wrong place means `Offset` still has its default: it adds 1 to the height. Crates that stay in the air at 4 m have no collider: give the prefab a **Box Collider**.

:::::

Play runs on a copy of the scene, so a field you change during play changes only the copy, and **Stop** throws the copy away. That is the right way to try values: change them while playing, keep the ones you like by typing them again after **Stop**.

## Edit the code while the game plays

When you rebuild during play, :term[hot reload]{id=hot-reload} makes each instance again from the new code. A field whose name and type are the same as before keeps what it had. A field you renamed or whose type you changed is a new field to the engine: it takes the class default, and the stored value of the old name is ignored. The next time the game starts, the log says so: `script 'Spawner' has no field 'MaxCrates'; the stored value is ignored`. A field whose stored type no longer fits is reported in the same way.

:::::steps

1. Rename `MaxCrates` to `CrateLimit` in both places of `Spawner.cpp`: the member and its `ST_SCRIPT_FIELD`. Build, then select the spawner.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the file, press **Ctrl+B**, and look at the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.get", "parameters": { "entity": "<id of Spawner>", "class": "Spawner" } }
   ```

   :::
   ::::

   **You should see:** a row `Crate Limit` with the default 5. Your 3 is gone from the list, and the next **Play** logs the "no field" message for `MaxCrates`.

   **If you do not see it:** if `Max Crates` is still listed, the build did not finish. Wait until the button reads **Build Scripts** again.

2. Rename the class `Spawner` to `CrateSpawner` in the file, including `ST_SCRIPT_CLASS`, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the file, press **Ctrl+B**, and select the spawner.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.status", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** the old `Spawner` entry stays in the Script section, in a warning color: "The script module has no class 'Spawner'", with its stored values as text. Play makes no instance of it and the log reports that the module does not contain the script.

   **If you do not see it:** if the entry still shows its fields, the build did not succeed. Open **Scripts ▸ Show Problems**.

3. Pick the class again. Remove the old entry with the **X** button of its header, then open **Add Script...** and choose `CrateSpawner`. Set `Spawn Point` and `Crate Prefab` again. Then rename the class back to `Spawner` and `CrateLimit` back to `MaxCrates`, build, and do this step once more to pick `Spawner` again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **X** in the header of the old entry, then choose the new class in **Add Script...**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.remove", "parameters": { "entity": "<id of Spawner>", "class": "Spawner" } }
   ```

   :::
   ::::

   **You should see:** the new class with every field at its default: a class that is renamed loses its values on every entity, as a renamed field loses its value.

   **If you do not see it:** if the old entry remains, click its **X** again; the entry stays until you remove it.

:::::

:::caution
When a :term[script class]{id=script-class} is renamed, pick it again on each entity. A hot reload during play removes the instances of a vanished class from the playing entities, and the log says "script 'Spawner' no longer exists; it was removed from entity".
:::

## Tune many spawner entities with a prefab

A single spawner takes a minute to set by hand. Ten take much longer, and the Inspector edits one entity at a time. Make the spawner a prefab, and its values come with every instance.

:::::steps

1. Make `Spawner` and `Spawn Point` one prefab. Drag `Spawn Point` onto `Spawner` in the Hierarchy so that it becomes the child, and make sure the `Spawn Point` row still shows it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `Spawn Point` onto `Spawner`. Right-click `Spawner` and choose **Create Prefab**. Name the file `Spawner`.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.create", "parameters": { "entities": ["<id of Spawner>"], "path": "Prefabs/Spawner.stprefab" } }
   ```

   :::
   ::::

   **You should see:** the `Spawner` row has the prefab badge and the chip reads `Overrides (0)`. The prefab file holds the entity, its child and the script with its field values.

   **If you do not see it:** if `Spawn Point` shows None, the field was not set before you made the prefab. Set it again and apply it.

2. Place a second instance of the prefab: the `Spawner` you made the prefab from is the first. Drag the prefab's file from the Content Browser into the scene, and move the new instance to the side. Select the second `Spawner` and set its `Interval` to 5.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Change `Interval` in the Inspector of the second instance.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<id of the second Spawner>", "class": "Spawner", "field": "Interval", "value": 5 } }
   ```

   :::
   ::::

   **You should see:** the `Interval` label is bold, with a bar at its left: an override, like a changed **Material** in [Prefabs](prefabs.md). The chip reads `Overrides (1)`. The first instance keeps 2.

   **If you do not see it:** if nothing is bold, the value you typed equals the prefab's. Type another one.

3. Apply or revert it. Right-click the `Interval` label of the second instance and choose **Revert** to give it the prefab's 2 again. Change it to 5 again and choose **Apply to Prefab**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use the right-click menu of the `Interval` label.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.apply", "parameters": { "entity": "<id of the second Spawner>", "component": "Script", "property": "Spawner.Interval" } }
   ```

   :::
   ::::

   **You should see:** after **Apply to Prefab** both instances read 5 and the chip returns to `Overrides (0)`. After **Revert** the label is plain again.

   **If you do not see it:** the menu has no entry when the property is not overridden. Only marked properties offer them.

:::::

Each instance has its own `Spawn Point` child, and its `Spawn Point` field points at its own child, not at the first one. The engine does this when it copies the prefab: references among the copies are rewritten to the new entities. A reference that points outside the prefab, to an entity of the scene, keeps pointing there.

## Result

You have a spawner whose ten values show in the Inspector, with a crate and a spawn point wired in without code. Changes while playing take effect at once and vanish at **Stop**. A hot reload keeps every field whose name and type stay, and a prefab of the spawner lets you tune every instance from one place. The spawner asks for its prefab early and never waits for it.

::figure{id=result}

## Variations

**Many spawners at once.** Put a value on the prefab and apply it: every instance that does not override it takes the new value. To change one instance only, override the value there. The prefab is the way around the limit of one entity at a time.

**A prefab chosen per spawner.** Override `Crate Prefab` on one instance so that it makes barrels. The spawner needs no change: the field holds any prefab.

**An enum without enums.** Add `int32_t Kind = 0;` and a comment, `// 0 crate, 1 barrel`. The Inspector shows a whole-number box. In the code, compare the number to named constants.

## Summary

- Strata has ten field types: `bool`, `int32_t`, `float`, the three vectors, the rotation, text, an entity and an asset. Anything else is refused with `Unsupported script field type`; use several fields, an `int32_t` or a string.
- An entity field and an asset field are set in the Inspector by drag or list; reset returns a field to the class default, and a value is stored only once set.
- A spawner asks for its prefab in `OnCreate` and checks `IsLoaded` and the returned entity, because `Instantiate` never waits.
- A change during play touches the copy and vanishes at **Stop**; hot reload keeps fields of the same name and type, and a renamed field or class loses its value.
- A field overridden on a prefab instance is marked like any property and can be applied to the prefab or reverted; a reference inside the prefab follows each instance.

## Check yourself

1. A teammate declares `std::vector<float> Speeds;` and registers it. What happens, and what do you suggest?

   :::answer{tests="field-types"}
   The build stops with `Unsupported script field type`, because a vector is not one of the ten types. Use three `float` fields, or a string that the script splits.
   :::

2. You set `Interval` to 3 on one entity, then change the class default from 2 to 4 and rebuild. What do two entities show, one with the 3 and one never touched?

   :::answer{tests="wire-references"}
   The first shows 3: its own value is stored. The second shows 4, since it holds no value and follows the class.
   :::

3. The spawner never makes a crate, and `Crate Prefab` shows the prefab's name. Name two causes the code itself can have.

   :::answer{tests="safe-spawn"}
   The `Spawn Point` may be empty, so the first check returns, or the prefab may not be loaded, so `IsLoaded` is false and the update returns. Without `RequestLoad` in `OnCreate` the load starts late.
   :::

4. You press **Play**, set `Max Crates` to 1, press **Stop** and look. What does the row show?

   :::answer{tests="values-lifetime"}
   The row shows the value from before **Play**. Play ran on a copy and Stop discarded it.
   :::

5. After you rename a field, a scene file still holds the old value. What does the engine do with it?

   :::answer{tests="values-lifetime"}
   The engine ignores the old value and the new field takes its class default. The log says that the class has no field of that name.
   :::

6. On an instance, `Interval` is bold. How do you make the prefab and every other instance follow it?

   :::answer{tests="prefab-fields"}
   Right-click its label and choose **Apply to Prefab**. Instances without their own value take it.
   :::

## Exercises

1. **Basic.** Select the second spawner of a prefab pair. Override `Interval` and `Crate Prefab` on it (a `Barrel` prefab in place of the crate), then revert both. What do the chip counts read at each stage, and what do the values read at the end?

   :::answer[Worked solution]{tests="prefab-fields,wire-references" solution="tutorials/make/script-fields/exercise-1.tutorial.json"}
   The chip reads `Overrides (0)`, then 1 after `Interval`, then 2 after the `Barrel` prefab, then 1 after the first revert and 0 after the second. The end values are the prefab's: 2 and the `Crate` prefab. The tutorial file runs the same steps with the commands `script.setField` and `prefab.revert`.
   :::

2. **Medium.** Leave `Spawn Point` empty on one spawner, and make the spawner use its own position then. What do you change?

   :::answer[Worked solution]{tests="safe-spawn"}
   In `OnUpdate` drop `!SpawnPoint.IsValid()` from the first check. Where the position is read, use the spawn point when `SpawnPoint.IsValid()` and `GetTransform().GetWorldPosition()` otherwise. The Inspector then shows None for the field and crates still appear.
   :::

3. **Hard.** The spawner needs a list of three crate prefabs, picked in order. Design the fields and the line that chooses one.

   :::answer[Worked solution]{tests="field-types"}
   Add three `AssetHandle` fields, `CrateA`, `CrateB` and `CrateC`, and request all three in `OnCreate`. Choose with the count of crates so far: `m_Spawned % 3 == 0` picks `CrateA`, 1 picks `CrateB`, 2 picks `CrateC`. A list needs several fields, since no vector type exists.
   :::

## Where it lives in Strata

The field types are checked in `StrataScriptCore/Include/StrataScript/Script.h` by `c_IsFieldType`, and its message is the `static_assert` of `ScriptClassBuilder::Field`. The Script section is drawn in `StrataEditor/src/Panels/InspectorPanel.cpp`, and field edits go through `StrataEditor/src/Editor/ScriptEdit.cpp`. The playing side, including the "no longer exists" message of a hot reload, is in `Strata/src/Strata/Scripting/ScriptSystem.cpp`.

## Further reading

- The engine's scripting manual, `Docs/Manual/Scripting.md` in the engine folder: the reference for classes, fields and builds (beginner).
- The headers of `StrataScriptCore/Include/StrataScript/`: every function of the script API documented in its comments (intermediate).

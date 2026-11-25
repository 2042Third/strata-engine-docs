---
id: make/scenes-entities
title: "Scenes, entities and components"
description: "Build Coin Run's level from entities and components: walls, a ball and a coin, edited one at a time and many at once."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/editor-tour]
time: 50
learn:
  - id: compose
    text: explain how an entity gets its looks and its behaviour from the components on it
  - id: build
    text: build the walls, the ball and the coin as entities with the Hierarchy and the Inspector
  - id: group
    text: set the parent of entities by dragging them and switch a whole group off
  - id: many
    text: change several entities at once and find entities with the Hierarchy search
  - id: scenes
    text: create, save and open more than one scene in a project
since: 0.3.0
status: final
---

## What you will make

You build the level of Coin Run, the game you make through the next pages: a walled ground, a ball and a first coin. Each is an entity with a few components, and you learn what those words mean by making them.

::figure{id=result}

## The idea: entities and components

A game scene holds many things: a ground, a ball, a light, a camera. You need one way to describe all of them. A **scene** is a document that holds entities, and you save it as one file.

An entity is a thing in the scene. It has an identifier (ID), a number that no other entity of the scene ever gets, and a name. An entity has nothing else: it does not look like anything and does nothing by itself.

What an entity is comes from its components. A **component** is a small block of data on an entity, and each kind of component answers one question. A Transform says where the thing is. A `Mesh Renderer` says which shape is drawn. A Box Collider says what the thing bumps into.

Take the Ground of your project. It has a name, a Transform, a Mesh :term[Renderer]{id=renderer} and a Box Collider. Remove the Mesh Renderer and the ground stays where it is and still stops a falling ball, but you cannot see it. Remove the Box Collider instead and you see it, but the ball falls through. Each component changes one thing.

Behaviour comes the same way. Systems that run for every frame, and the scripts you write, read the components and act on them. No entity has a class of its own.

:::caution
A common mistake is to search for an "enemy class" to extend. Strata has none. You make an enemy by putting an entity together from components, and the components decide what it does.
:::

```mermaid caption="Two ways to describe a guard. The tree fixes what the guard is by its place among classes; the entity is an identity with parts you can add or remove." alt="On the left, a chain of classes: object, enemy, flying enemy, armored flying enemy. On the right, one entity with an identity and a name, joined to four parts: a transform, a mesh renderer, a box collider and a script."
flowchart LR
    subgraph tree["Inheritance tree"]
        direction TB
        O["Object"] --> E["Enemy"] --> F["FlyingEnemy"] --> A["ArmoredFlyingEnemy"]
    end
    subgraph ent["Entity"]
        direction TB
        I["ID and Name: Guard"] --> T["Transform"]
        I --> M["Mesh Renderer"]
        I --> B["Box Collider"]
        I --> S["Script"]
    end
```

A tree forces a choice: a flying enemy that is also a vehicle needs two parents. An entity needs no such choice, because you add a component and the thing gains that part. The price is that data lives in many small pieces, so you learn the pieces. [Coming from another engine](../start/coming-from.md) compares this with other engines, and [What a world is](../world/what-a-world-is.md) compares the models in depth.

## What you need

You need the project that [A tour of the editor](editor-tour.md) ended with: Coin Run from the Basic 3D template, open in the editor. If you skipped the tour, download its last checkpoint. Nothing else is imported. The page takes about 50 minutes.

The editor tour taught the panels and how to move the view. Here you type numbers into the Inspector for a position and a size; [Positions, rotations and units](../make/transforms-units.md) explains what those numbers mean, so for now copy them.

## Read the Ground's components

Start with an entity that exists. The Basic 3D template made the Ground, and its components show what you meet on every entity.

:::::steps

1. Click `Ground` in the Hierarchy. The Inspector lists its components, one section each.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Read the header, which holds the name and the ID, then the sections: **Transform**, **Mesh Renderer** and **Box Collider**. Hover over **Rotation** to read its help text.
   :::
   :::tab[With a command]

   This command reads the Ground's Transform, the values that the Inspector shows.

   ```json
   { "command": "component.get", "parameters": { "entity": "<the Ground's ID>", "component": "Transform" } }
   ```

   Replace the placeholder with the ID that `entity.find` returns for the name `Ground`. The answer gives **Rotation** as it is stored, four numbers (0, 0, 0, 1), and not as the Inspector's three angles; [Positions, rotations and units](../make/transforms-units.md) explains the four. For angles in degrees, ask `entity.get` with `"world": true`: for an entity without a parent, its `world` part holds the angles the Inspector shows.
   :::
   ::::

   **You should see:** a Transform with **Translation** 0, 0, 0 and **Scale** 20, 1, 20; a Mesh Renderer with its **Mesh**, **Material** and **Cast Shadows**; a Box Collider with **Half Extents** and **Offset**.

   **If you do not see it:** you selected another entity; click the row named Ground. If the Inspector is missing, bring its panel back as the editor tour showed.

   **Why:** the help text says "Edited as Euler angles in degrees". The engine keeps one description of every property, with its help text, unit and range. The Inspector, the files, the commands and the scripts all read it.

:::::

Three things stand out. The **Mesh** of the Ground is the built-in Plane. A **built-in mesh** is a shape the engine makes itself, so no file holds it: `Cube`, `Sphere`, `Plane`, `Quad`, `Cylinder`, `Capsule`, `Cone` and `Torus`. The material is separate: a built-in default material exists too, and [Materials](../make/materials.md) teaches your own.

The second thing: **Translation** is the position, the first of the Transform's three values. The **transform** of an entity is its position, rotation and scale, measured from its parent. Third, a name sits in the Name component, and the identity does not: the Inspector header shows the ID, which stays the same if you rename the entity.

::checkpoint{stage=1}

::figure{id=ground-inspector}

## Build the walls

The ground is 20 by 20 metres, from -10 to 10 on both horizontal axes. You close it with four walls, each a cube you stretch.

:::::steps

1. Click the **+** button at the top of the Hierarchy and choose **Cube**. The new entity is selected.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **F2**, type `Wall` and press **Enter**. In the Inspector, type **Translation** 0, 0.5, 10 and **Scale** 20, 1, 0.5.
   :::
   :::tab[With a command]

   This command creates the same entity with its three components.

   ```json
   { "command": "entity.create", "parameters": { "name": "Wall", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [0, 0.5, 10], "Scale": [20, 1, 0.5] } } } }
   ```

   The result holds the new entity's ID.
   :::
   ::::

   **You should see:** a long, low wall along the far edge of the ground. The Inspector shows a Mesh Renderer and a Box Collider, which the **Cube** entry added for you, so the wall bumps into things.

   **If you do not see it:** if the wall floats or sinks, check that **Translation** reads 0, 0.5, 10. A cube is one metre high and centred, so half a metre up puts it on the ground.

2. Drag the wall once with the Move :term[gizmo]{id=gizmo-start} to watch the numbers.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **W** in the Scene view and drag an arrow of the gizmo. Then press **Ctrl+Z** until the numbers return.
   :::
   :::tab[With a command]

   This command sets the position a drag would reach; send 0, 0.5, 10 to put it back.

   ```json
   { "command": "component.set", "parameters": { "entity": "<the wall's ID>", "component": "Transform", "values": { "Translation": [1, 0.5, 10] } } }
   ```

   :::
   ::::

   **You should see:** the **Translation** numbers change while you drag, so the gizmo and the Inspector edit the same data.

   **If you do not see it:** if nothing moves, click the wall again so that it is selected, then press **W**.

3. Make the other three walls from the first. Click the `Wall` row and press **Ctrl+D** three times.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The copies appear as `Wall (1)`, `Wall (2)` and `Wall (3)`, each with a new ID. Click each and type the numbers of the table below.
   :::
   :::tab[With a command]

   This command duplicates the wall once; run it three times.

   ```json
   { "command": "entity.duplicate", "parameters": { "entity": "<the wall's ID>" } }
   ```

   The result lists the copies' IDs. Give each copy its numbers from the table with `component.set`, as in step 2.
   :::
   ::::

   | Entity | Translation | Scale |
   | --- | --- | --- |
   | Wall | 0, 0.5, 10 | 20, 1, 0.5 |
   | Wall (1) | 0, 0.5, -10 | 20, 1, 0.5 |
   | Wall (2) | 10, 0.5, 0 | 0.5, 1, 20 |
   | Wall (3) | -10, 0.5, 0 | 0.5, 1, 20 |

   **You should see:** four walls around the ground, each with its own ID and the same components.

   **If you do not see it:** if two walls overlap, check the table: only the side walls are long along z.

4. Make a parent that holds the walls. Click **+** and choose **Empty**; rename it `Walls`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type **Translation** 0, 0, 0, so that the parent sits at the origin. Then drag each wall row onto the `Walls` row.
   :::
   :::tab[With a command]

   The first command creates the empty parent at the origin and returns its ID. The second moves one wall under it.

   ```json
   { "command": "entity.create", "parameters": { "name": "Walls" } }
   { "command": "entity.setParent", "parameters": { "entity": "<a wall's ID>", "parent": "<the Walls ID>" } }
   ```

   Run the second for each wall. `entity.create` also takes a `parent`, which creates an entity straight under another.
   :::
   ::::

   **You should see:** the four walls below `Walls`, and the scene looks the same. Dragging keeps where a child stands in the world, and with the parent at the origin its numbers stay the same too.

   **If you do not see it:** if a wall jumped, the parent was not at the origin when you dropped it: press **Ctrl+Z** and set its Translation first.

   **Why:** the **+** button always creates at the top level. To create an entity straight under another, right-click the parent and choose **Create Child**; later pages use this for interface elements.

5. Raise the camera so that the whole level shows. Select `Main Camera`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type **Translation** 0, 16, 13 and **Rotation** -55, 0, 0. Click the **Game camera** chip above the Scene view, or press **F8**.
   :::
   :::tab[With a command]

   This command sets the same values; the rotation takes the same three angles in degrees as the Inspector.

   ```json
   { "command": "component.set", "parameters": { "entity": "<Main Camera's ID>", "component": "Transform", "values": { "Translation": [0, 16, 13], "Rotation": [-55, 0, 0] } } }
   ```

   Replace the placeholder with the camera's ID. Read back with `component.get`, the rotation shows as four stored numbers, as in the first section.
   :::
   ::::

   **You should see:** the Scene view looks through the camera at the ground and the four walls, seen from above and behind. The starting camera sits 2 metres up and 6 back, too low for the far corners.

   **If you do not see it:** if the view did not change, the chip is off: click it again.

:::::

::checkpoint{stage=2}

::figure{id=level-walls}

## Add the ball and the coin

The ball and the coin differ in one component: the ball has a collider, and the coin has none, so the ball passes through it. Both come from the **+** menu, sketched below. Each shape entry adds a collider that fits the shape, and the same shapes under **Mesh only** come without one.

::figure{id=create-menu-drawing}

:::::steps

1. Click **+** and choose **Sphere**. Rename it `Ball`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type **Translation** 0, 0.5, 6. A sphere is one metre wide, so half a metre up rests it on the ground.
   :::
   :::tab[With a command]

   This command creates the ball with a sphere collider.

   ```json
   { "command": "entity.create", "parameters": { "name": "Ball", "components": { "MeshRenderer": { "Mesh": "Builtin/Sphere" }, "SphereCollider": { "Radius": 0.5 }, "Transform": { "Translation": [0, 0.5, 6] } } } }
   ```

   :::
   ::::

   **You should see:** a ball near the front wall, with a Sphere Collider in the Inspector.

   **If you do not see it:** if the Hierarchy shows no Ball row, the name was not committed: press **Enter** after typing it.

2. Click **+**, open **Mesh only** and choose **Cylinder**. Rename it `Coin`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type **Translation** 0, 0.8, -4, **Rotation** 90, 0, 0 and **Scale** 0.8, 0.1, 0.8.
   :::
   :::tab[With a command]

   This command creates the coin with a Mesh Renderer and no collider.

   ```json
   { "command": "entity.create", "parameters": { "name": "Coin", "components": { "MeshRenderer": { "Mesh": "Builtin/Cylinder" }, "Transform": { "Translation": [0, 0.8, -4], "Rotation": [90, 0, 0], "Scale": [0.8, 0.1, 0.8] } } } }
   ```

   :::
   ::::

   **You should see:** a flat disc standing on its edge, its lowest point 0.4 m above the ground, and in the Inspector a Mesh Renderer but no collider. The Scale flattens the cylinder to a tenth of a metre; the Rotation of 90 degrees stands it up.

   **If you do not see it:** if you chose **Cylinder** outside **Mesh only**, the coin has a collider: remove it with the menu of its section, described next.

   **Why:** the coin is a placeholder. [Assets](../make/assets.md) brings a real model, and [Physics](../make/physics.md) shows what the ball does with colliders.

3. Select the coin and click **Add Component**. Under the heading **Core**, choose **Tag**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `Coin` into the **Tag** field. A script uses a tag to find a group of entities.
   :::
   :::tab[With a command]

   This command adds the Tag component with its value.

   ```json
   { "command": "component.add", "parameters": { "entity": "<the Coin's ID>", "component": "Tag", "values": { "Tag": "Coin" } } }
   ```

   :::
   ::::

   **You should see:** a **Tag** section with `Coin`. The menu at the right of a section header offers **Reset**, **Copy Values**, **Paste Values** and **Remove**.

   **If you do not see it:** the popup lists only components the entity lacks; type `Tag` into its search field.

:::::

The popup groups components by category, such as Core, Rendering and Physics. Each engine module adds its own components to the registry, so the list grows with the modules. Pick a component by its category, and read its help text.

::checkpoint{stage=3}

::figure{id=level-ball-coin}

## Edit many entities at once

The Inspector edits every selected entity together. Here you lift the four walls in one edit.

:::::steps

1. Click `Wall`, then hold the Shift key and click `Wall (3)`. The rows sit in the order you dragged them.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the **Transform** section type **Translation** Y 0.75 and **Scale** Y 1.5.
   :::
   :::tab[With a command]

   This command sets the height of one wall; the walls differ in x and z, so send one such command per wall.

   ```json
   { "command": "component.set", "parameters": { "entity": "<a wall's ID>", "component": "Transform", "values": { "Translation": [0, 0.75, 10], "Scale": [20, 1.5, 0.5] } } }
   ```

   :::
   ::::

   **You should see:** fields that differ between the walls show two dashes, **--**. Fields you type into change on every wall, and the dashes stay on the axes you leave alone.

   **If you do not see it:** if only one wall changed, you clicked without the Shift key: select all four rows again.

   ::figure{id=walls-mixed}

2. Find entities again with the Hierarchy search. Type `Wall` in its field.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Then try `t:Coin` for a tag and `c:BoxCollider` for a component. Clear the field when you finish.
   :::
   :::tab[With a command]

   This command finds the entities with the tag.

   ```json
   { "command": "entity.find", "parameters": { "tag": "Coin" } }
   ```

   `"component": "BoxCollider"` in place of the tag finds the five colliders. A `name` matches only the whole name, so `"name": "Wall"` finds the first wall alone. The search field's own matching runs only in the window: `editor.showPanel` with `"panel": "Hierarchy"` and `"search": "Wall"` types the text into it.

   :::
   ::::

   **You should see:** `Wall` lists the four walls and their parent; `t:Coin` lists the coin; `c:BoxCollider` matches the Ground and the four walls, and shows `Walls` above them because it holds matches. The prefixes `l:` and `cell:` search by layer and cell in a large world; [Large worlds](../make/large-worlds.md) teaches them.

   **If you do not see it:** a prefix with no text after it asks for nothing yet: finish the word.

3. Press **Escape**, or click an empty part of the Hierarchy, so that nothing is selected.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Read the Inspector: with no entity selected, it shows the scene itself.
   :::
   :::tab[With a command]

   This command clears the selection.

   ```json
   { "command": "selection.set", "parameters": { "entities": [] } }
   ```

   :::
   ::::

   **You should see:** the scene's name, its count of entities and closed sections of settings, such as the physics and the sky. Later pages open them.

   **If you do not see it:** if an entity stays selected, click an empty row area below the last entity.

   ::figure{id=nothing-selected}

4. Select `Walls` and clear the check box beside its name in the Inspector's header.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Watch the Scene view, then tick the box again.
   :::
   :::tab[With a command]

   This command switches the group off; send `true` to switch it on.

   ```json
   { "command": "entity.setActive", "parameters": { "entity": "<the Walls ID>", "active": false } }
   ```

   :::
   ::::

   **You should see:** the four walls vanish and stop colliding, and their rows turn dim in the Hierarchy. A switched-off parent switches off every child, and a switched-on one brings them back.

   **If you do not see it:** if a wall stays, it is not a child of `Walls`: drag it onto the parent.

:::::

::checkpoint{stage=4}

::figure{id=walls-off}

## Keep more than one scene

A project holds many scenes: a level, a menu, a test room. Save, then make a second one.

:::::steps

1. Press **Ctrl+S**, then choose **File ▸ New Scene**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Save Scene As...**, go to the `Scenes` folder and name the file `Test.stscene`.
   :::
   :::tab[With a command]

   This command saves the open scene under a path inside the project.

   ```json
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Test.stscene" } }
   ```

   Before it, run `scene.save` for the level and `scene.new` for the empty scene.
   :::
   ::::

   **You should see:** an empty Hierarchy: the new scene holds nothing yet.

   **If you do not see it:** if the editor asks about changes you did not save, you skipped the save: answer **Save**.

   ::figure{id=scenes-two}

2. Choose **File ▸ Open Scene...** and pick `Scenes/Main.stscene`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The level returns with the walls, the ball and the coin.
   :::
   :::tab[With a command]

   This command opens the level again.

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   ```

   :::
   ::::

   **You should see:** the level you built. The project still starts with `Main`; the `Test` scene is a scratch room for later pages.

   **If you do not see it:** if the empty scene stays, the dialog was closed: choose **File ▸ Open Scene...** again.

:::::

::checkpoint{stage=5}

::figure{id=result}

## Summary

- An entity is an identity and a name; its components give it looks, a place, a shape to bump into and any behaviour, and no class stands behind it.
- You built the walls, the ball and the coin by adding built-in meshes and typing numbers in the Inspector.
- You grouped the walls under `Walls` by dragging, and one check box switched the group off and on.
- You edited four walls at once, read mixed values as **--**, and found entities with `Wall`, `t:` and `c:`.
- You saved the level, made an empty `Test` scene and opened `Main` again.

## Check yourself

1. A friend asks where to find the class for an enemy. What do you answer?

   :::answer{tests="compose"}
   There is none. An entity is an identity and a name; you make an enemy by adding components, such as a Transform, a Mesh Renderer and a collider, and a script for its behaviour.
   :::

2. The coin has no Box Collider. Predict what the ball does when it rolls into the coin, and why.

   :::answer{tests="compose build"}
   The ball passes through. Collision is the job of the collider component; the coin has only a Mesh Renderer, so it is drawn and never touched.
   :::

3. You drag a wall onto `Walls` while `Walls` stands at 5, 0, 0. Do the wall's Inspector numbers stay the same?

   :::answer{tests="group"}
   No. Dragging keeps where the wall stands in the world, so the wall's own Translation changes by -5 on x to offset the parent's position.
   :::

4. Four walls are selected and the Scale shows **--** on x. What does it mean, and what happens if you type 3 there?

   :::answer{tests="many"}
   The four walls hold different x scales. Typing 3 sets the x scale of all four to 3 and leaves the other axes as they were.
   :::

5. The search `c:BoxCollider` matches five entities. Which?

   :::answer{tests="many"}
   The Ground and the four walls. The ball has a Sphere Collider and the coin has no collider.
   :::

6. Why does `Main` stay the start scene after you make `Test`?

   :::answer{tests="scenes"}
   A project names one start scene in its settings, and making or saving another scene does not change it. You open other scenes by choice.
   :::

## Exercises

1. **Basic.** Open `Test`. Build a table: an empty entity `Table` with a flattened Cube as the top and four cubes as legs under it. Switch the table off and on with its active box.

   :::answer[Worked solution]{tests="build group" solution="tutorials/make/scenes-entities/exercise-1.tutorial.json"}
   Make `Table` with **+ ▸ Empty**, set it to the origin and create each cube with **Create Child** on its row. A top of Scale 1.6, 0.1, 1 at height 0.8 and legs of Scale 0.1, 0.75, 0.1 at height 0.375 fit. One cube, duplicated with **Ctrl+D**, gives the other legs. The box in the Inspector header switches all of them off and on.
   :::

2. **Medium.** Return to `Main`. Predict which entities the search `c:BoxCollider` finds, then search to check.

   :::answer[Worked solution]{tests="many" solution="tutorials/make/scenes-entities/exercise-2.tutorial.json"}
   The search finds the Ground and the four walls. The ball has a Sphere Collider and the coin has none, so neither matches. If your count differs, a wall made with **Mesh only** has no collider.
   :::

## Where it lives in Strata

- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`: the Hierarchy, its plus menu and the rename field.
- `StrataEditor/src/Editor/ProjectTemplates.cpp`: the shapes of the menu with their colliders, and the Basic 3D scene.
- `StrataEditor/src/Editor/HierarchyView.cpp`: the search prefixes `c:`, `t:`, `l:` and `cell:`.
- `Strata/src/Strata/Scene/ComponentRegistration.cpp`: the Name, Transform, Tag and other core components.
- `StrataEditor/src/Panels/InspectorPanel.cpp`: the component sections, the Add Component popup and the scene settings.

## Further reading

- Robert Nystrom, "Game Programming Patterns", chapter "Component": why games build objects from parts (beginner).
- Unity Technologies, the manual page "GameObjects": a comparable entity and component model (beginner).

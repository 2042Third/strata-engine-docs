# Notes: start/coming-from

## New terms

None proposed. The page defines **callback** in bold (one sentence, in "What a callback looks like in C++"); the
glossary may home it on `make/script-loop`.

## Requests

- External host `dev.epicgames.com` (Unreal Engine documentation): the entry "Coordinate System and Spaces" in Further
  reading is cited without a link until the host is listed.

## Not verified

- Every statement about Unity, Unreal and Godot (names of classes and functions, axes, units, the order of Unity's
  `FixedUpdate` before `Update`, Unreal's physics sub-steps and tick groups, Godot's signals and process priority)
  comes from the brief and general knowledge; no page of those engines was fetched.
- The entity IDs in the "With a command" tabs of steps 3 and 4 (`AAE2EAF90F8A1799`, `959D47C78B26E82F`) are read from
  `Samples/ThirdPerson/Assets/Scenes/Course.stscene`; that a loaded scene keeps them was not run.
- The Inspector's **Rotation** of `Camera` is not quoted (the scene stores a quaternion); no step was run in the editor.
- That Strata has no particle system or terrain tool rests on the registered components at the pin and the Roadmap, not
  on a search of every module.

## Findings not applied

- critic-start-2 concerns `start/first-game`; nothing of it belongs on this page.
- critic-start-3 applied: step 4 makes an override and reverts it (the coins hold no override).
- critic-start-4 applied for this page (**Character Controller**, **Rigid Body** in the map); the other labels belong to
  `start/first-game`.
- critic-start-13 applied: `OnCreate`, `OnDestroy`, the contact callbacks, the rule of setup in `OnCreate`, the panels,
  the physics body, the character controller and tags are rows of the map.
- critic-start-20 applied: the page explains the header and the source file in "What a callback looks like in C++".

## Clerk

- Nothing admitted: "callback" is homed on `basics/cpp-generic`.
- Left for the planner: `dev.epicgames.com` (the fetch of its front page returned no page to confirm).

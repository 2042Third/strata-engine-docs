# Part review of `make/timers-events` (group 3)

Checked against the engine at the pin and the part's other pages.

- step: step 1 told the reader to add a Box Collider to the cube of **+ ▸ Cube**, which the Hierarchy's Cube preset already gives (`StrataEditor/src/Panels/SceneHierarchyPanel.cpp`, GetMeshPresets); the step now says so and adds only the Rigid Body.
- wrong: step 7 said `Paused` "blinks twice a second"; the flag flips at each end of a 0.5 s timer, so the word is on for half a second and off for half a second: it blinks once a second.

---
id: world/review
title: "Review: scenes and the ecs"
description: "The questions of every page of the part on scenes and the entity component system, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A `Lamp` entity uses the slot of index 5, where two entities were destroyed before it, and it is the child of a `Pole`. Give the lamp's handle value. Then say which identifier of the pole the saved scene file holds as the lamp's parent, and which form of the link the transform update follows after the file loads again.

   :::answer[Worked solution]
   A slot that has seen two destructions has version 2. A handle holds the version in its high 12 bits and the index in its low 20 bits, so the value is $2 \times 2^{20} + 5 = 2{,}097{,}157$.

   Handles change between loads, so a file can hold only `UUID` values. The lamp's line carries a `Parent` key with the pole's `UUID`, the form of `RelationshipComponent`. After the load, the scene holds the link twice: by `UUID` for files and order, and by handle in `HierarchyComponent`. The transform update follows the handle links, because a `UUID` would need a lookup in the scene's map at every step of the walk.

   Now destroy the lamp and let a new entity take slot 5. Its version is 3, so its handle is $3 \times 2^{20} + 5 = 3{,}145{,}733$, and the old value 2,097,157 is no longer valid. A system that kept the old handle would find nothing, so it keeps the `UUID` of the lamp and asks the scene each time.
   :::

2. **Basic.** A scene steps at 60 times a second with interpolation on. A frame of 100 ms arrives while the accumulator holds 10 ms. How many fixed steps does the frame run, what stays in the accumulator, and what are the step alpha and the drawn time relative to the end $T$ of the latest step?

   :::answer[Worked solution]
   The step is $h = 16.7$ ms and the accumulator becomes 110 ms. Six steps take 100 ms, and a seventh would need 116.7 ms, so the frame runs 6 steps, below the cap of 8, and drops nothing. The accumulator keeps $a = 10$ ms.

   Then $a/h = 10 / 16.7 = 0.6$, so $\alpha = 1 - (1 - 0.6)/6 = 0.933$. The drawn time is $T + a - h = T + 10 - 16.7 = T - 6.7$ ms. Check: the two poses are 6 steps, 100 ms, apart, and 0.933 of 100 ms after $T - 100$ ms is $T - 6.7$ ms.
   :::

3. **Medium.** A project sets `FixedRate` to 240 with interpolation on. A frame of 250 ms arrives while the accumulator holds 1 ms. How many steps run, how many are dropped, and what are the accumulator and the step alpha afterwards? How much game time does the frame simulate, and how much would it simulate if the scene kept its own cap of 8 steps?

   :::answer[Worked solution]
   The project's cap is the steps of 2/15 s: $(240 \times 2 + 14) / 15$ with whole division is 32. The step is $h = 4.17$ ms, and the accumulator becomes 251 ms.

   The loop runs 32 steps, which take 133.3 ms, and stops at the cap with 117.7 ms still owed. That is more than one step, so the frame drops $\lfloor (117.7 - 4.17) / 4.17 \rfloor = 27$ steps, and the accumulator becomes exactly one step, 4.17 ms.

   With $a/h = 1$ the step alpha is $1 - 0 / 32 = 1$, so the frame draws the poses after the last step, and the drawn time is $T$. The frame simulates 133.3 ms of the 251 ms that passed. With the scene's own cap of 8 at 240 steps a second the frame would simulate only 33.3 ms, which is why a project rate brings its own cap.
   :::

4. **Medium.** A scene file made by a newer game holds a zone of the tutorial with `"Strength": 5000`, `"Radius": -2` and `"Direction": [0, 0, 1]`, and a component `Gust` on three entities that no module of your build registers. Predict the zone's values after the load and the warnings in the log. Then say what a `component.set` command with `"Strength": 5000` does, and what the file holds after a save.

   :::answer[Worked solution]
   A file load clamps a value into its range and logs nothing for it, because the clamp succeeds. The zone loads with `Strength` 1000 and `Radius` 0.01, the lowest value of its range. `Direction` is a property that `WindZone` does not have, so the reader skips it with one warning.

   The reader keeps `Gust` unchanged on its three entities and warns once for the name: `Unknown component 'Gust' (3 entities) kept unchanged: no module of this build registers it`. So the log holds two warnings, and none for the values.

   The command checks the range first and refuses: `WindZone.Strength must be between 0 and 1000, not 5000`. The zone does not change.

   The save writes each component from its registered properties. The file then holds `Strength` 1000 and `Radius` 0.01, so the 5000 and the -2 are gone, and `Direction` is gone too, because the reader skipped it. The writer merges the kept JSON of `Gust` back in, so that component is written as it was read.
   :::

5. **Medium.** A scene with the default limits creates a sub-scene in chunks. An entity costs 1,000 ns in truth, the scene's estimate starts at its default of 2,000 ns, and the update has the whole 2 ms cap. In which chunks does the update create entities, how many in all, and what is the estimate afterwards? What changes if `MaxEntitiesInstantiatedPerFrame` is 1,000?

   :::answer[Worked solution]
   The first chunk of a pass is whole, 512 entities, whatever the estimate says. It costs 0.512 ms, so 1.488 ms remain. The estimate becomes $\max(1000, (2000 + 1000)/2) = 1500$, so $1{,}488{,}000 / 1500 = 992$ entities fit, and the chunk is the largest, 512.

   After two chunks, 0.976 ms remain and the estimate is 1,250, so 780 fit and the third chunk has 512. After three chunks, 0.464 ms remain and the estimate is 1,125, so 412 fit. After the fourth, 0.052 ms remain and the estimate is 1,062.5, so 48 fit. After the fifth, 0.004 ms remain and the estimate is 1,031.25, so 3 fit, and the smallest chunk of 32 runs.

   The chunks are 512, 512, 512, 412, 48 and 32, which make 2,028 entities in 2.028 ms. The deadline has passed, so the loop stops, and the estimate is $\max(1000, (1031.25 + 1000)/2) = 1015.6$ ns.

   With the count limit of 1,000, the count binds before the 2 ms do. The first chunk is 512, and the second is the 488 left of the budget, although 992 would fit in the time. The update creates 1,000 entities in 1 ms, the estimate is 1,250 ns, and a sub-scene of 12,000 needs 12 such updates.
   :::

6. **Hard.** The prefab `Lantern` has a root `Frame` with an `AudioSource` of `Volume` 1.0, and the children `Bulb`, with a `PointLight`, and `Glass`. Three instances stand at (2, 0, 0): A is untouched, B has `Range` 9 and a `Moth` at (0, 0.5, 0) below its bulb at (0, 1, 0), and C has `Volume` 0.2. The maker applies a change that removes the bulb, gives `Glass` an `AudioSource` and sets the frame's `Volume` to 0.5. Give the records of B and C before the change, and what `Propagate` makes of A, B and C, with the moth's local position.

   :::answer[Worked solution]
   Before the change, B has one record, `{ Bulb, "PointLight", "Range", Property }`, and C has one, `{ Frame, "AudioSource", "Volume", Property }`. A has none. The `Moth` has no template id, so no record names it, and the root's position is the instance's own.

   `Propagate` gives each instance the difference between the old and the new part, except where its list overrides it. All three lose the bulb, because the prefab removed it, and B loses its range override with it. All three gain an `AudioSource` on `Glass`, because the prefab added it and no record removes it. A and B take `Volume` 0.5. C keeps 0.2, because its list overrides that property.

   What B keeps below the removed bulb moves up to the nearest entity that stays, the frame, with its place in the world. The moth's world position is $(2, 0, 0) + (0, 1, 0) + (0, 0.5, 0) = (2, 1.5, 0)$. With the frame at (2, 0, 0), its new local position is (0, 1.5, 0). Afterwards `Propagate` works out the lists again against the new part. B's list is empty, and C's still holds the volume.
   :::

7. **Hard.** A scene asset loads on a worker thread, and meanwhile the maker sets the project's `FixedRate` to 240 and `Interpolation` to off. Which thread reads the project's settings, and when? What do the first and the second call of `ApplyProjectTiming` return for this scene, which has taken no project rate before? The first frame lasts 90 ms with an empty accumulator: give the step, the cap, the steps run, the rest in the accumulator and the step alpha.

   :::answer[Worked solution]
   The worker built the scene from its document and never read the project, because the settings belong to the main thread. The main thread reads them when it takes the scene, in `ApplyProjectTiming`, and again after every later change of the settings.

   The first call finds the provider's version new, takes rate 240 and the flag, and returns true, because the rate the scene runs at changed from its own to 240. With interpolation off, the call also clears the stored poses. The second call finds the same version and returns false at once.

   The step is 1/240 s, 4.17 ms, and the cap is 32 steps. The frame of 90 ms holds $90 / 4.17 = 21.6$ steps, so 21 run, below the cap, and nothing is dropped. They take 87.5 ms and leave 2.5 ms. With interpolation off, `GetStepAlpha` is 1, so every entity is drawn where it is, and the 2.5 ms are carried into the next frame.
   :::

8. **Hard.** A new `CartSystem` moves a cart in `OnUpdate` with `cart.GetTransform().Translation.x += 0.1f` and signals nothing. The cart has five children, and one is a wind zone that the `WindZone` system of the tutorial reads with `GetWorldTransform` in every fixed step. Players report that the cart and its wind stay where the cart started. Explain what the zone's system reads, how a `Debug` build can find the fault, and what the repair costs for each frame.

   :::answer[Worked solution]
   The write puts the cart on no dirty list, so the next update computes nothing for it. In the fixed step, `GetWorldTransform` finds the dirty list empty, or no dirty entity on the way from the zone to the root, so it returns the cached matrix, which still holds the starting place. The cached matrices of the cart and all five children are stale too, so the cart is drawn at its start, although its local position grows.

   `Scene::ValidateWorldTransforms` finds the fault in a `Debug` build, at its next cache check. It computes the matrices again and fails with a message that names the cart and asks whether a `TransformComponent` was written without `Entity::MarkModified`.

   The repair is `MarkModified<TransformComponent>()` after the write, or `registry.patch`. The cart is then dirty, so the next update computes it and its five children, 6 matrices. At about 3.3 ms per million that costs about 20 ns each frame. The update phase runs before the fixed steps, and the dirty list is no longer empty, so `GetWorldTransform` computes the pending matrix, and the zone follows the cart in the first step.
   :::

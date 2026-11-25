---
id: physics/review
title: "Review: physics"
description: "The questions of every page of the part on physics, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A scene holds 1,200 bodies. How many pairs must a test of every pair visit? A cube whose farthest corner is 0.8 m from its centre slid 2 cm and turned 2° (0.0349 radians) since box3d last computed its contact with the floor. Does box3d recycle the contact with the default `ContactRecycleDistance`, and what if the turn was 3° (0.0524 radians)?

   :::answer[Worked solution]
   Step 1: the pairs number $n(n-1)/2 = 1{,}200 \times 1{,}199 / 2 = 719{,}400$. A broad phase on bounding boxes keeps only the pairs whose boxes overlap, so the exact tests run on few of them.

   Step 2: recycling needs the slide plus the arc of the turn to stay under 5 cm, and the turn under about 10°. The arc is the farthest corner's distance times the angle in radians.

   Step 3: for 2° the arc is $0.8 \times 0.0349 = 0.0279$ m, and the total is $0.02 + 0.0279 = 0.0479$ m. That is under 0.05 m, so the contact is recycled.

   Step 4: for 3° the arc is $0.8 \times 0.0524 = 0.0419$ m, and the total is 0.0619 m. That is over 0.05 m, so box3d works the contact out again, although the turn is far under 10°.
   :::

2. **Basic.** A steel ball (friction 0.2, restitution 0.3) falls on a rubber mat (friction 0.8, restitution 0.6). Which friction and restitution does their contact use? Does the ball bounce after a fall of 0.5 m, and after a fall of 4 cm, and how high does it rise the first time?

   :::answer[Worked solution]
   Step 1: a contact takes the square root of the product of the two frictions, $\sqrt{0.2 \times 0.8} = 0.4$, and the larger restitution, 0.6.

   Step 2: the speed at the mat is $\sqrt{2 g h}$. From 0.5 m that is $\sqrt{2 \times 9.81 \times 0.5} = 3.13$ m/s. From 4 cm it is $\sqrt{2 \times 9.81 \times 0.04} = 0.89$ m/s.

   Step 3: restitution acts only above an approach speed of 1 m/s. The first drop bounces, and the second does not, whatever the restitution.

   Step 4: the ball leaves at $0.6 \times 3.13 = 1.88$ m/s. It rises $1.88^2 / (2 \times 9.81) = 0.18$ m, which is $0.6^2 \times 0.5$ m.
   :::

3. **Medium.** A cannon fires a ball of radius 0.1 m at 90 m/s. The fixed step is 1/60 s. In front of it stand three walls, each 0.2 m thick: a static wall, a kinematic sliding door, and the same door with `ContinuousCollision` on the ball. Which walls can the ball pass without any overlap test seeing it, and at which speed would it stop passing the door?

   :::answer[Worked solution]
   Step 1: the ball moves $90 / 60 = 1.5$ m in one step, so a test at the end of each step looks at positions 1.5 m apart.

   Step 2: the discrete test misses a wall that lies between two such positions. The ball can skip a wall when its step is longer than the wall plus the ball's width: $0.2 + 0.2 = 0.4$ m. The ball's step of 1.5 m is longer.

   Step 3: box3d sweeps every dynamic body against static bodies, so the static wall stops the ball. The door is kinematic, and only a bullet is swept against it, so the ball without `ContinuousCollision` can pass. With `ContinuousCollision` the sweep stops it.

   Step 4: the ball cannot skip the door when its step is at most 0.4 m, that is at $0.4 \times 60 = 24$ m/s or less. A ball slower than that always has an end position that overlaps the door.
   :::

4. **Medium.** A project parts layer 4 from layer 6 and changes nothing else. What are the category and the mask of a shape on each layer? Does a raycast whose layer mask holds only layer 6 hit a body on layer 6, and does one whose mask holds every layer but 6? Does a body on layer 4 touch it?

   :::answer[Worked solution]
   Step 1: a shape on layer $L$ has category bit $L$ and, as mask, the row of the table plus the query bit 63. Layer 4 has category $2^4 =$ `0x10`.

   Step 2: the row of layer 4 holds every bit except bit 6. That is `0xffffffff` minus `0x40`, which is `0xffffffbf`. With bit 63 the mask is `0x80000000ffffffbf`.

   Step 3: layer 6 has category $2^6 =$ `0x40`, and its row lacks bit 4, so its mask is `0x80000000ffffffef`.

   Step 4: a query asks with the query category and the layers it wants as mask. Every shape's mask holds bit 63, so the first ray hits the body, because its mask holds category `0x40`. The second ray misses the body, because its mask lacks that bit.

   Step 5: the bodies on layers 4 and 6 do not touch. Each mask must hold the other's category, and here neither does. A query is not a contact, so parting the two layers does not hide either body from rays.
   :::

5. **Medium.** An entity has a world scale of $(2, 3, 1)$ and three colliders: a box of half extents $(0.5, 0.25, 1)$, a sphere of radius 0.5 and a capsule of radius 0.2 and half height 0.5. Give the numbers of the three shapes. A script then sets the scale to $(4, 3, 1)$ and signals the write. What happens to the body, and to a sleeping crate whose `TransformComponent` a C++ system of the game writes directly without a signal?

   :::answer[Worked solution]
   Step 1: Strata bakes the scale into the shapes. A box scales on each axis, so the half extents are $(1, 0.75, 1)$.

   Step 2: a sphere takes the largest axis, 3, so its radius is $0.5 \times 3 = 1.5$. A capsule takes the larger of X and Z for its radius, $0.2 \times 2 = 0.4$, and Y for its half height, $0.5 \times 3 = 1.5$.

   Step 3: the new scale differs from the baked one by far more than 1 part in 10,000, so the next fixed step rebuilds the body. The new shapes are a box of $(2, 0.75, 1)$, a sphere of radius 2 and a capsule of radius 0.8 and half height 1.5. The rebuilt body keeps its velocities, because a dynamic body rebuilt in the simulation starts with the motion the old body had.

   Step 4: the crate is asleep and nobody signalled it, so the sync does not look at it. The body stays where it was, and the entity and the body disagree. The fix is `MarkModified` on the transform or `registry.patch`, which put the crate on the list that the next sync visits.
   :::

6. **Medium.** A bench has four legs, each a box collider of its body, on layer 0. The legs touch the floor in steps 3, 3, 4 and 6, and leave it in steps 9, 10, 10 and 12. Which events does a script on the floor receive for the bench, and in which steps? What changes if a script destroys the bench in step 7, and which events does the bench get from a ghost ball on layer 2, parted from layer 0, that rolls over it?

   :::answer[Worked solution]
   Step 1: Strata counts the shape contacts of each pair of entities. The count is 2 after step 3, 3 after step 4 and 4 after step 6. It falls to 3 in step 9, to 1 in step 10 and to 0 in step 12.

   Step 2: a pair begins with its first contact and ends with its last. The pair gets one `Begin`, queued in step 3, and one `End`, queued in step 12. The floor's script receives `OnCollisionEnter` and `OnCollisionExit` after those steps, on the main thread.

   Step 3: when a script destroys the bench in step 7, the destruction ends the pair with an `End`, so the floor's script gets its exit then and not in step 12. The event names the bench by `UUID`, but the bench's handle is invalid, so the script tests `collision.Other.IsValid()` first. Every `Begin` has exactly one `End`.

   Step 4: the ghost ball and the bench have layers that refuse each other, so no contact exists between them, and the bench gets no event for the ball.
   :::

7. **Hard.** A designer reports four facts about the default character controller. A stair with 0.4 m steps blocks the player, and a script that sets the walk velocity to $(0, 4, 0)$ every step to jump moves nothing. A 30° ramp can be climbed and a 50° ramp stops the player, while a trigger zone around a door runs `OnTriggerEnter` for the player. Explain each fact, and compute where the toy's circle of radius 0.5 ends when it starts at $(1, 0.5)$ and moves by $(1.5, 0)$ towards the 30° ramp that rises from $(2, 0)$.

   :::answer[Worked solution]
   Step 1: the default step height is 0.35 m, so a step of 0.4 m is a wall, and a step of 0.3 m is not.

   Step 2: gravity is on, so the controller drops the vertical part of the walk velocity, because gravity and the jump own the vertical motion. The vertical part counts only for a controller with a gravity scale of 0, such as a flying one.

   Step 3: the limit is 45°, so the walkable normals have a Y part above $\cos 45° = 0.707$. A 30° ramp has 0.866 and is climbed. A 50° ramp has 0.643, so the across pass makes it a wall and removes the whole move. On the ramp itself the player slides.

   Step 4: the controller has a presence body, a kinematic capsule on its layer, and triggers detect that body. So the zone's `OnTriggerEnter` runs, once, whatever the capsule's own queries do.

   Step 5: the normal of the ramp is $(-0.5, 0.866)$, and its offset is $-0.5 \times 2 = -1$. The target is $(2.5, 0.5)$, and its signed distance minus the radius is $(-1.25 + 0.433) + 1 - 0.5 = -0.317$ m. The push is $0.317 \times (-0.5, 0.866) = (-0.158, 0.275)$, so the circle ends at $(2.34, 0.77)$.
   :::

8. **Hard.** A game runs 30 fixed steps per second with `ContactHertz` at its default of 30, and a scene holds 40,000 bodies at play start. What is the room of its physics world, and how many bytes does Strata reserve, with 2,120 bytes a body, 250 bytes a contact and 32,768 bytes? Which stiffness does box3d use? How do you raise the stiffness back to 30 Hz, and where do you measure the result?

   :::answer[Worked solution]
   Step 1: twice the bodies is 80,000, and the next power of two is 131,072, above the minimum of 1,024. The contact room is $2 \times 40{,}000 = 80{,}000$, above the minimum of 2,048.

   Step 2: the bytes are $131{,}072 \times 2{,}120 + 80{,}000 \times 250 + 32{,}768 = 277{,}872{,}640 + 20{,}000{,}000 + 32{,}768 = 297{,}905{,}408$, about 298 MB.

   Step 3: the sub-step rate is 4 sub-steps times 30 steps, 120 per second. One eighth of it is 15 Hz, which is smaller than the setting, so box3d uses 15 Hz and not 30. The contacts are softer than at 60 steps per second.

   Step 4: raising `ContactHertz` changes nothing, because the ceiling holds it at 15. A shorter fixed step of 1/60 s gives 30 Hz again, and a second collision step per fixed step gives it too, at twice the cost of the contact work.

   Step 5: measure the result with `physics.stats`. Its `settings` group shows `effectiveContactHertz`, which reads 15 before the change and 30 after it. Compare the step time in the Streaming panel too, against the value you read before the change.
   :::

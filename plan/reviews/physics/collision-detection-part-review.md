# Part review: `physics/collision-detection`

- contradiction: "Worlds stay within 20 km of the origin, because positions are single precision" mixed the World asset's extent with the physics limit; `physics/why`, `physics/bodies-colliders` and `physics/building-bodies` give 1e5 m (`c_MaxBodyCoordinate`, `B3_HUGE`). Now "Bodies more than 100,000 m from the origin leave the simulation".

Checked at the pin: `B3_SPECULATIVE_DISTANCE` (2 cm), the margin fraction 0.125 capped at 5 cm, `B3_MAX_GJK_ITERATIONS` 32, `B3_MAX_MANIFOLD_POINTS` 4, `B3_MESH_REST_OFFSET`, `b3UpdateBroadPhasePairs` at line 649 and its early return, the pair sort, the recycling gates in `b3CollideTask` (lines 678 and 725), `invokeContactCreation`, and the sweep's numbers in the guide (85 %, 3.29 and 1.87 ms, 1.7 cm, 44 mm, 5 mm, 0.70 m against 17 mm).

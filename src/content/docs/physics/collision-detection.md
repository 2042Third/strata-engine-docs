---
id: physics/collision-detection
title: "Collision detection: shapes, broad phase and narrow phase"
description: "How a physics engine finds which bodies touch, where and how deeply, without testing every pair, and why a box sliding over tiles bumps."
kind: concept
size: L
tracks: [E]
needs: [physics/bodies-colliders, basics/math-geometry, basics/trees-graphs]
time: 65
learn:
  - id: pair-cost
    text: compute how many pairs a scene of n bodies has and explain how a first pass on bounding boxes cuts the exact tests
  - id: broad-approaches
    text: compare a uniform grid, sweep and prune and a tree of boxes by what each costs when bodies move or sleep
  - id: narrow-contact
    text: find the separating axis or the penetration depth of two boxes and read the point and normal of a manifold
  - id: recycle-gates
    text: predict whether box3d recycles a contact for a given movement and turn
  - id: seam-bump
    text: explain why a box sliding over a floor of tiles bumps at the seams and how to fix it
since: 0.7.0
status: final
---

Open the Physics Playground and look at the pit of 500 balls. Each step, the engine must know which of the balls touch each other, which touch the floor, and for each touch, where it happens and how hard the balls press into each other. The first question sounds small. Ask it of every ball against every other ball, and it is not.

Count the pairs. The first ball has 499 partners, the second has 498 that are new, and so on down to the last, which has none. The total is $500 \times 499 / 2 = 124{,}750$ pairs. Two thousand balls make 1,999,000 pairs, nearly sixteen times more for four times the balls. At 60 steps each second, the small pit alone would ask 7.5 million questions every second, and almost every answer is "no".

## Testing every pair costs n squared

The naive answer is to test every pair of bodies with the exact test, the one that decides whether two shapes overlap and where. For $n$ bodies the number of pairs is $n(n-1)/2$. Read the formula as: each of $n$ bodies pairs with the $n-1$ others, and each pair is counted twice, so divide by 2. In big-O terms ([trees and costs](../basics/trees-graphs.md)) the work grows as $O(n^2)$: double the bodies, and the work grows by a factor of four.

The exact test is also not cheap. Two boxes in three dimensions have 6 face directions and 9 edge directions to check, 15 in all. The answer must be more than "yes": it has to say where the shapes touch and how deep. The pit's 124,750 pairs at 15 checks are about 1.9 million checks per step, before any ball has moved.

Most of those pairs are far apart. A ball at the left wall cannot touch a ball at the right wall, and one look at where they are says so. The engine needs a way to throw those pairs away cheaply and to spend the exact test only where a touch is possible.

## Two phases: cheap boxes first, exact shapes second

The idea is to split the work in two. The first phase works on one simple stand-in for each shape, its :term[axis-aligned bounding box]{id=axis-aligned-bounding-box} (AABB), and answers a cheap question: which pairs of boxes overlap? The second phase takes only those pairs and runs the exact test.

The **broad phase** is the first phase: it finds candidate pairs of bodies by comparing their :term[bounding boxes]{id=bounding-box}, and it never reports a pair of overlapping boxes as touching, only as worth a closer look.

The **narrow phase** is the second phase: it takes one candidate pair and computes the exact contact between their shapes, as a point, a normal and a depth.

```mermaid caption="Bodies go into the broad phase as boxes. Only the candidate pairs reach the narrow phase, which makes the contacts the solver uses." alt="A flow chart from left to right. Bodies and their boxes enter the broad phase, which outputs candidate pairs. The narrow phase turns them into contacts, and contacts go to the solver."
flowchart LR
    A["Bodies and their boxes"] --> B["Broad phase: candidate pairs"]
    B --> C["Narrow phase: exact shapes"]
    C --> D["Contacts: points, normal, depth"]
    D --> E["Solver"]
```

A box test is six comparisons. An exact test of two hulls is hundreds of operations. If the broad phase keeps 1,300 of 124,750 pairs, the narrow phase does about 1 % of the exact work, and the broad phase pays a small price for it. The rest of this page builds the two phases in turn. The broad phase must be right in one direction only: it may keep a pair that does not touch, because the narrow phase will say so, but it must never drop a pair that does.

The solver, which turns contacts into forces and new velocities, comes after both phases and has its own page ([solving contacts](../physics/dynamics.md)).

## A uniform grid is cheap until the bodies differ

The first way to make a broad phase is a **uniform grid**. Lay a grid of equal cells over the world, write each body into every cell its box covers, and pair only the bodies that share a cell. A ball in a pit of 500 meets the few balls in its own cell and its neighbours, not all 499.

Work through a number. Take cells 0.5 m wide and balls of 0.5 m diameter. A ball covers at most 8 cells, so one lookup reads at most a few dozen entries. The cost per body is constant, and the pair search grows with $n$ instead of $n^2$.

The flaw is the cell size. Pick cells for balls, and a ground plane 200 m long covers 160,000 cells or more; pick cells for the ground, and a hundred balls fall into one cell and pair with each other again. A world with bodies of very different sizes has no good cell size. Space also costs memory: empty cells still exist unless you :term[hash]{id=hash} them.

## Sweep and prune sorts the boxes along one axis

The next idea drops the grid and uses order. **Sweep and prune** sorts the boxes by where they start on one axis and sweeps along it. Two boxes can only overlap if their intervals on that axis overlap, so each box meets only the boxes that start before it ends.

The sketch below does this for a block of 500 balls laid out in a grid, and counts the exact tests. It first tests every pair, then sorts by x and tests each ball only against balls within one diameter after it. Look at the two counts and at the pairs found.

```cpp sketch="physics-collision-detection-sweep.cpp"
// Counts the exact tests of a brute-force pair search and of a sweep along one axis, for a lattice of 500 balls.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Ball
{
	float X;
	float Y;
	float Z;
};

static bool Touches(const Ball& a, const Ball& b, float diameter)
{
	const float dx = a.X - b.X;
	const float dy = a.Y - b.Y;
	const float dz = a.Z - b.Z;
	return dx * dx + dy * dy + dz * dz < diameter * diameter;
}

int main()
{
	const float diameter = 0.5f;
	const float spacing = 0.48f;
	std::vector<Ball> balls;
	for (int x = 0; x < 10; x++)
		for (int y = 0; y < 10; y++)
			for (int z = 0; z < 5; z++)
				balls.push_back({ x * spacing, y * spacing, z * spacing });

	int bruteTests = 0;
	int bruteTouching = 0;
	for (size_t i = 0; i < balls.size(); i++)
	{
		for (size_t j = i + 1; j < balls.size(); j++)
		{
			bruteTests++;
			if (Touches(balls[i], balls[j], diameter))
				bruteTouching++;
		}
	}

	// Sweep: sort by X, then test a ball only against the balls whose X lies within one diameter after it.
	std::sort(balls.begin(), balls.end(), [](const Ball& a, const Ball& b) { return a.X < b.X; });
	int sweepTests = 0;
	int sweepTouching = 0;
	for (size_t i = 0; i < balls.size(); i++)
	{
		for (size_t j = i + 1; j < balls.size() && balls[j].X - balls[i].X < diameter; j++)
		{
			sweepTests++;
			if (Touches(balls[i], balls[j], diameter))
				sweepTouching++;
		}
	}

	std::printf("brute force: %d tests, %d touching\n", bruteTests, bruteTouching);
	std::printf("sweep:       %d tests, %d touching\n", sweepTests, sweepTouching);
	return 0;
}
```

```text output-of="physics-collision-detection-sweep.cpp"
brute force: 124750 tests, 1300 touching
sweep:       34750 tests, 1300 touching
```

1. **Line 13:** the exact test, here the distance between two centres against the diameter.
2. **Lines 26–29:** ten by ten by five balls, 0.48 m apart, so that neighbours overlap by 2 cm.
3. **Lines 33–41:** the first search tests every pair once.
4. **Line 44:** the sweep sorts the balls by x.
5. **Line 49:** the inner loop stops at the first ball more than one diameter away along x.

Both searches find the same 1,300 touching pairs, as they must. The sweep does 34,750 tests instead of 124,750, a saving of a factor of 3.6. The block is dense along x (ten columns of 50 balls each), which hurts the sweep: every ball must be checked against the whole next column. A scene spread along its sorted axis needs far fewer.

The real gain of sweep and prune comes from time. Bodies move a little each step, so the sorted order barely changes, and sorting an almost sorted list costs close to nothing. The flaw is the single axis. Suppose a thousand boxes stand in a row of x with different y. The interval test then passes for many pairs that are far apart on y and z.

Sweep and prune is also awkward to ask "who is near this point", which the engine needs for rays and overlaps ([queries](../physics/queries.md)).

## A dynamic tree of boxes handles every size and keeps moving

The third approach keeps boxes in a tree. A **dynamic tree** is a binary tree in which each leaf holds one body's box and each inner node holds a box that encloses its two children. A query can then skip a whole subtree whenever the query box misses the node's box ([the spatial tree](../basics/trees-graphs.md)).

To find the partners of one box, start at the root and visit a child only when its box overlaps. A well-balanced tree of $n$ leaves has about $\log_2 n$ levels, so one query costs about $O(\log n)$ plus the number of partners. For 500 balls that is about 9 levels. Bodies of any size sit in the same tree, and a box far above the pit costs a few comparisons to reject.

The tree has a problem of its own: a body that moves must change its leaf, and the inner boxes above it must change too. Doing that for every moving body in every step is the main cost. The remedy is the **fat box**: a leaf stores a box larger than the body's real box, by a margin, and the tree changes only when the real box leaves the fat one.

Strata's physics library, box3d, does exactly this. At the pin, a shape's box is first widened by the speculative distance, 2 cm, then widened again by the shape's margin, a fraction of its size capped at 5 cm. The speculative distance is the gap within which box3d already makes contact points, as a later section explains.

```cpp src="vendor:box3d/src/shape.c#L84-L89"
b3AABB aabb = b3ComputeFatShapeAABB( shape, transform, speculativeDistance );
shape->aabb = aabb;

// Smaller margin for static bodies. Cannot be zero due to TOI tolerance.
float margin = proxyType == b3_staticBody ? speculativeDistance : aabbMargin;
*fatAABB = b3AABB_Inflate( aabb, margin );
```

:term[Static bodies]{id=static-body} get the speculative distance as the margin, 2 cm; moving ones get their own margin. Work out a number. A ball of radius 0.25 m has a margin of $0.125 \times 0.25 = 0.03125$ m, since for a sphere the size is the radius. A box 1 m on a side has its farthest corner 0.87 m from its centre, so its fraction (0.108 m) is capped at 5 cm.

:::example[How often a falling ball touches the tree]
A ball falls at 1 m/s. At 60 steps each second it moves 1.0/60 = 0.0167 m a step. Its fat box has a 0.03125 m margin beyond the real box. The real box stays inside after step 1 (offset 0.0167 m). It leaves in step 2 (offset 0.0333 m, more than 0.03125 m).

So the tree changes about every second step for a ball moving at 1 m/s.

A ball that rests moves 0 m, and its real box never leaves the fat one, so the tree is never touched for it. A ball that sleeps is removed from the awake set altogether. Both cases cost nothing in the broad phase: only moved boxes start a pair search.
:::

Table of the three ways, for a scene of $n$ bodies in which $m$ move in a step:

| Approach | Cost of the pair search | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Uniform grid | About $O(n)$ with one cell size | Good for equal sizes, poor for mixed sizes | Small, but needs hashing for big worlds | Scenes of equal-sized bodies, as Ericson describes |
| Sweep and prune | About $O(n)$ with a nearly sorted list, worse when bodies pile on the axis | Good for scenes spread along the axis | Medium: one list per axis, updates per move | Bullet and PhysX offer it |
| Dynamic tree of fat boxes | About $O(m \log n)$ for the $m$ boxes that left their fat box | Good for any sizes, supports rays and overlap queries | Larger: tree balance and rebuilds | box3d, Box2D, Bullet |

The "used by" cells and the costs follow Ericson's book and Catto's talks ([further reading](#further-reading)).

## The broad phase in box3d: three trees and moved boxes

At the pin, box3d keeps one tree for each body type: static, kinematic and dynamic. Look at `b3UpdateBroadPhasePairs` in `Strata/vendor/box3d/src/broad_phase.c`. It returns early when the static tree has no moved box and neither of the others needs a rebuild, so a world at rest does no pair search at all.

Otherwise it gathers the boxes that moved and asks the dynamic tree for partners among the other dynamic boxes, and each of the static and kinematic trees for partners too. Workers collect the new pairs in parallel, and the code sorts the keys so that the order of contacts does not depend on the tree's shape. The tree is only updated afterwards. The broad phase of box3d does not keep pairs: it reports possibly new ones and leaves it to the caller to follow them, so an old contact lives on until its fat boxes stop overlapping.

A step costs what is awake. Sleeping bodies do not move, so no box of theirs asks for partners. Box3d also updates contacts only for the awake set. A pit of 500 balls that has fallen asleep costs next to nothing, while a pit of 500 balls in motion pays for every moved box and every contact.

## The separating axis test finds a gap or the shallowest push

Now the narrow phase. Take one candidate pair and ask whether two :term[convex]{id=convex} shapes overlap, and if so by how much. A shape is **convex** when a line between two of its points never leaves the shape: a box, a ball and a capsule are convex, a doughnut is not.

The **separating axis test** says: two convex shapes are apart exactly when some axis exists on which their shadows, the projections of both shapes onto that axis ([projecting onto an axis](../basics/math-vectors.md)), do not overlap. For boxes it is enough to try a small set of axes: the face normals of both boxes and the :term[cross products]{id=cross-product} of one edge of each. If one axis shows a gap, stop: the shapes are apart. If no axis does, they overlap, and the axis with the smallest overlap is the direction in which to push them apart at least cost.

:::example[Two boxes, by hand]
Work in 2D first, where the face normals of two upright boxes are the x and y axes. Box P has centre $(0, 0)$ and half widths $(1.0, 0.5)$ m; box Q has half widths $(0.5, 0.5)$ m and centre $(1.8, 0.2)$ m.

On the x axis, the shadows reach from $-1.0$ to $1.0$ and from $1.3$ to $2.3$. The sum of half widths is $1.0 + 0.5 = 1.5$ and the centres are 1.8 apart, so the gap is $1.8 - 1.5 = 0.3$ m. One axis shows a gap, so the boxes do not touch. Stop.

Move Q to $(1.3, 0.2)$. On x, the overlap is $1.5 - 1.3 = 0.2$ m. On y, the sum of half widths is $0.5 + 0.5 = 1.0$, and the centres are 0.2 apart, so the overlap is $1.0 - 0.2 = 0.8$ m. No axis shows a gap, and the smallest overlap is on x: the depth of overlap is 0.2 m, and the normal points along $+x$ from P to Q.
:::

In 3D, two boxes have 3 face normals each and $3 \times 3 = 9$ cross products of edge pairs: 15 axes. The edge axes matter: two boxes can cross like two sticks, with no face of one pushing into a face of the other. A gap on any of the 15 is a stop. Box3d does the same for hulls, with a face query for each of the two hulls and an edge query for pairs of edges. It remembers the axis that separated them last time (a cache), and tries it first the next step, because shapes that were apart a moment ago usually still are.

## GJK finds the distance of any two convex shapes

The :term[separating axis]{id=separating-axis} test needs a list of axes, which a box has. A ball has none, and a capsule has few. The **Gilbert–Johnson–Keerthi** (GJK) algorithm works for any convex shape that can answer one question, and it does not need a list of faces.

That question is the **support point**: given a direction, which point of the shape lies farthest along it? For a ball it is the centre plus the radius in that direction. For a box it is the corner whose signs match the direction's signs. For a hull, it is the vertex with the largest :term[dot product]{id=dot-product} with the direction, found by a loop over the vertices. Box3d reads it in `b3GetProxySupport` in `Strata/vendor/box3d/src/distance.c`.

GJK searches for the closest pair of points of the two shapes. It works on their difference: every point of one shape minus every point of the other. That difference is convex too. It holds the origin, the point $(0, 0, 0)$, exactly when the shapes overlap, and its distance from the origin is the distance between the shapes.

GJK keeps a **simplex**: the smallest set of points (a point, a segment, a triangle or a pyramid with four corners) that describes the current best guess, and it improves it step by step. Each step takes the point of the simplex nearest the origin, asks both shapes for their support points in the direction toward the origin, and adds their difference as the new point. When the new point brings no progress, the guess is final. The count of steps is small, and box3d stops after at most 32 (`B3_MAX_GJK_ITERATIONS`).

For shapes that do not touch, GJK returns the distance and the two closest points, which is what the narrow phase needs for a contact that is close but not yet touching. For shapes that overlap, GJK reports a distance of zero and no direction, because inside the overlap there is no closest point. Something else must measure the depth.

## Depth and the manifold say where and how deeply

Box3d handles the two cases in separate code. In `b3CollideHullAndSphere` in `Strata/vendor/box3d/src/convex_manifold.c`, the code calls GJK first, between the hull and the sphere's centre point. If that distance is above a tiny value, the centre lies outside the hull, and the normal is the line between the two closest points.

If the distance is zero, the sphere's centre is inside the hull. The code then runs over the hull's face planes and takes the face with the largest :term[signed distance]{id=signed-distance}, the least deep, as the way out. That is the separating axis idea again, on faces only. For two hulls, box3d uses the separating axis test directly, and the depth is a negative separation along the chosen axis.

The result of a narrow phase test is a **manifold**: the description of one touch as a normal and a short list of contact points. The normal is the direction in which to push the shapes apart. Each **contact point** has a position and a separation, the signed gap along the normal (negative when the shapes overlap). In this book, "contact point" names one entry of the manifold.

Why not a single point? Put a 1 m cube flat on the floor. One point at its centre would let the cube balance on it like a pin and tip over at the slightest push. The contact of two flat faces is a flat patch, and the engine finds it by clipping.

The engine takes the face of one box that the normal points at (the reference face) and the facing face of the other (the incident face). It then cuts the incident face by the sides of the reference face. What remains is the area where the faces touch.

:::example[A box resting on the floor]
A 1 m cube rests on a floor tile. The reference face is the floor's top, with its normal pointing up, $(0, 1, 0)$. The incident face is the cube's bottom, a square of four corners. Clipping the square by the sides of the floor's top keeps all four corners, because the tile is bigger than the cube. The manifold holds 4 points with the same normal, each with a separation of about $-0.001$ m.

Tilt the cube by 5° about one bottom edge, so it rests on that edge only. The edge's two ends are the incident face's corners that stay near the floor; the other two corners are higher than the speculative distance of 2 cm and drop out. The manifold now has 2 points, and the solver pushes at both ends of the edge, so the cube does not spin around it.
:::

Box3d allows at most four points in a manifold (`B3_MAX_MANIFOLD_POINTS`): four corners define the support area and make the solver stable, and more points add cost without adding stability. When clipping finds more, a reduction step (`b3ReduceManifoldPoints`) keeps four that spread out most. A hull against a triangle mesh can give several manifolds in one contact, one for each triangle it touches.

Points are made also when the shapes are not yet touching, if the gap is below the speculative distance (2 cm). This is called speculation: the solver may let the shapes close the gap but not cross it. The narrow phase's answer for a touch that is about to happen is a manifold with a positive separation.

## Contact recycling keeps what barely changed

The narrow phase runs each step for every awake contact. In a pile, bodies barely move from one step to the next, so most of those tests give nearly the same points as the step before. **Contact recycling** is box3d's way to use that: it keeps a touching contact's points while the bodies have barely moved and skips the narrow phase for it.

The contact stores the relative pose of the two bodies when its points were last computed. Each step, box3d compares the current relative pose with the stored one. At the pin, it recycles the contact only if all of these hold:

- Neither body is fast, and the recycle distance is above 0.
- Both bodies turned less than about 10° since the points were computed.
- The relative motion fits the tolerance: 5 cm for a contact that touched, at most 2 cm for one that did not.

```cpp src="vendor:box3d/src/physics_world.c#L651-L681"
float recycleTolerance = wasTouching ? recycleDistance : recycleDistanceNonTouching;

// Contact recycling optimization. Please cite this library if you use this optimization.
// This is inspired by persistent contact manifolds used in some physics engines, such as PhysX.
// However, this allows larger relative motion and has fewer tuning parameters (just one).
if ( isFast == false && recycleDistance > 0.0f && ( contact->flags & b3_relativeTransformValid ) &&
	 ( contact->flags & b3_contactRecycleFlag ) )
{
	// The scalar part of b3InvMulQuat is just the quaternion dot product.
	// cos(relative_angle/2) = scalar(conj(q1) * q2) = dot(q1, q2)
	// A small relative angle means this value is close to 1. Need to use abs or square
	// due to double cover.
	float angleA = b3DotQuat( transformA.q, contact->cachedRotationA );
	float angleB = b3DotQuat( transformB.q, contact->cachedRotationB );
	float angularDistance = b3MinFloat( angleA * angleA, angleB * angleB );

	b3Transform xf = b3InvMulWorldTransforms( transformA, transformB );
	b3Transform xfc = contact->cachedRelativePose;
	b3Vec3 maxExtentA = b3IsStaticSimIndex( encodedA ) ? b3Vec3_zero : bodySimA->maxExtent;
	b3Vec3 maxExtentB = b3IsStaticSimIndex( encodedB ) ? b3Vec3_zero : bodySimB->maxExtent;
	b3Vec3 maxExtent = b3Max( maxExtentA, maxExtentB );

	// Variation of Conservative Advancement
	// distance + 2 * length(modified_cross(|qr.v|, maxExtent)) < recycleTolerance.
	// 2*|qr.v| == 2*|sin(theta/2)| ~= theta for small angles.
	float distSquared = b3DistanceSquared( xf.p, xfc.p );

	if ( angularDistance > B3_CONTACT_RECYCLE_ANGULAR_DISTANCE && distSquared < recycleTolerance * recycleTolerance )
	{
		float distance = sqrtf( distSquared );
		float slack = recycleTolerance - distance;
```

1. **Line 651:** the tolerance is the recycle distance for a contact that touched, and the smaller of it and the speculative distance for one that did not.
2. **Lines 656–657:** recycling needs a normal-speed pair, a distance above 0, and a contact with a stored pose and the recycle flag.
3. **Lines 663–665:** the turn gate takes the squared :term[cosine]{id=cosine} of half of each body's turn and keeps the smaller.
4. **Line 678:** both gates in one test: the turn is small enough, and the distance moved is under the tolerance.
5. **Line 681:** the slack is what the tolerance leaves for the arc of the turn, which the next lines compare.

The movement gate has two parts. The distance between the stored and the current relative position must be under the tolerance. The distance plus the arc that the farthest point sweeps when it turns must be under it too. That arc is about the turn in :term[radians]{id=radian} times the point's distance from the centre. A contact that passes keeps its points' anchors and normal, and only the bodies' movement updates its separations.

:::example[Four contacts, four verdicts]
A cube's farthest corner is 0.87 m from its centre. Recycle distance: 5 cm.

A cube slid 3.0 cm and turned 1° (0.01745 radians). The arc is $0.01745 \times 0.87 = 0.0152$ m. The total, $0.030 + 0.0152 = 0.0452$ m, is under 0.05: recycled.

Slid 3.6 cm with the same turn, the total is 0.0512 m, over the limit: collided again. Slid 0.5 cm and turned 12°, the turn gate fails (limit 10°) whatever the distance: collided again. With the distance set to 0, nothing is ever recycled.
:::

The gain is real. In Strata's own sweep of settings, 85 % of the contacts of a busy scene of boxes recycled at the default distance. The step's collide time fell from 3.29 ms with recycling off to 1.87 ms.

The price is stale geometry, because a recycled contact keeps the old points and the old normal. A body that slides off a ledge can seem supported a little past the edge: up to 1.7 cm further at the default distance, in Strata's sweep. A teleport of less than the distance can leave an old contact alive. The distance is a project setting ([tuning](../physics/tuning.md)); this page needs only the idea.

::figure{id=recycle-gates}

Strata turns recycling off for :term[kinematic bodies]{id=kinematic-body} and for the bodies that character controllers use to touch the world. A recycled contact keeps its points in each body's frame while a turning platform carries its riders. The riders crept 0.70 m in 4 seconds on a platform at 2 m/s and 30°/s, against 17 mm without recycling.

## Ghost collisions: why a box bumps at the seams of a tiled floor

A floor can be built of many box tiles, each 1 m wide, lying edge to edge at the same height. Push a box across it at 2 m/s with no friction, and it should glide. It does not: it rises about 44 mm at the seams, and moves up and down as it passes them. The bump has no cause in the scene. It is a **ghost collision**: a contact with an internal edge or face that the player and the designer never meant to be there.

The cause is that each tile is a separate shape with its own edges. As the box's front bottom edge meets the end of the next tile, the narrow phase sees a contact with that tile's edge, whose normal is not the floor's up but tilted forward and up. The solver pushes along that normal, and a push along a tilted normal contains an upward part. The box rises, and it falls back on the next tile.

Recycling is not the main cause. In Strata's sweep, the bumps came mostly from the inner edges of the tiles, with recycling or without it (distance 0). The default distance added at most about 5 mm, and a shorter one removes at most that 5 mm. The real fix is to remove the seams: make the floor one :term[collider]{id=collider} (one box the length of the lane) or a triangle mesh. For meshes, box3d keeps a rest offset of 5 mm (`B3_MESH_REST_OFFSET`, one `B3_LINEAR_SLOP`) to reduce ghost collisions.

:::rule[Make a floor of tiles one collider]
A floor made of many box tiles bumps at the seams, 44 mm at 2 m/s with or without recycling. Strata's guide says to use one collider or a triangle mesh instead of a shorter recycle distance. The reason is in this section; the rules are in [the physics tuning page](../physics/tuning.md).
:::

## Strata keeps box3d's trees and manifolds

Strata does not replace any of this. It builds bodies and shapes, and box3d does the broad phase and the narrow phase. Strata adds the code that decides what enters the world and what leaves it.

:::why[Why not write a collision detector for Strata?]
A collision detector is the part of a physics engine with the most hard cases: degenerate hulls, speculative contacts, tolerances that interact with the solver. Box3d's trees, manifolds and recycling are written together with its solver, and its tests cover them. A second detector would need its own solver conventions, and Strata would lose box3d's updates. The cost of the choice is that Strata inherits box3d's limits, such as the 5 cm default and the ghost bumps, and can only tune them.
:::

Three places show the seam between Strata and the trees.

- Static bodies made before the first step skip the pair search: Strata sets `invokeContactCreation` to false for them in `Strata/src/Strata/Physics/PhysicsWorld.cpp`.
- A static body without contacts that leaves the simulation is parked. It keeps its entries in the trees, but its filter has an empty mask, so no pair or query includes it. Strata disables it in box3d 60 steps later, at most 1,024 each step ([scale and streaming](../physics/scale-streaming.md)).
- A hull cooked for a convex collider has at most 64 vertices, or 44 when box3d's limit of 128 faces and edges does not fit ([bodies and colliders](../physics/bodies-colliders.md)).

## What this choice cannot do

Strata does not offer a choice between a grid, sweep and prune and a tree. No setting changes the manifold's tolerances beyond the recycle distance. Bodies more than 100,000 m from the origin leave the simulation, because positions are single precision. What Strata omits from physics is listed in [what Strata does not do](../appendix/not-in-strata.md).

A hull is convex, so a hollow or dented shape must be split into convex parts or turned into a triangle mesh, which only static bodies may use. The narrow phase also finds contacts at one moment of time. A body fast enough to cross a thin wall between two steps needs the continuous collision of [dynamics](../physics/dynamics.md). Layers decide which pairs may collide, and they have their own page ([collision layers](../physics/collision-layers.md)).

## Common mistakes

- **Testing every pair in your own code.** Symptom: a gameplay check that loops over all enemies and all bullets slows as the game grows, like $n^2$. Fix: ask the physics world for overlaps ([queries](../physics/queries.md)), which use the trees.
- **Tiling a floor with boxes.** Symptom: a sliding crate or a rolling ball hops at regular spacing. Fix: one collider or a triangle mesh.
- **Believing a contact is exact at every step.** Symptom: a body hangs a hair past an edge or keeps an old contact after a small teleport. Fix: remember the recycle distance, 5 cm, and lower it only after looking at seams and edges.
- **Reading a manifold point as the whole touch.** Symptom: a box seems to touch at one place when it rests on four. Fix: read all the points and the one normal.
- **Spawning bodies deep inside each other.** Symptom: the narrow phase reports a large negative separation, and the solver pushes the bodies apart hard. Fix: place them apart; the depth is real.

## Summary

- A scene of $n$ bodies has $n(n-1)/2$ pairs, 124,750 for 500 balls. A broad phase on bounding boxes keeps few candidates, and the exact test runs only on them.
- A grid costs little but needs one cell size, sweep and prune sorts along one axis, and a dynamic tree of fat boxes handles every size and changes only when a body leaves its box.
- The separating axis test finds a gap or the least overlap, GJK finds the distance of any convex shapes, and the narrow phase returns a manifold of up to four points with one normal.
- Box3d recycles a contact while the relative pose moved less than 5 cm (distance plus the turn's arc) and the turn is under 10°; the price is stale points past edges.
- A floor of tiles bumps at its seams with or without recycling; one collider or a triangle mesh removes it.

## Check yourself

1. A scene has 2,000 bodies. How many pairs has it, and how does that compare with 500 bodies?

   :::answer{tests="pair-cost"}
   $2000 \times 1999 / 2 = 1{,}999{,}000$ pairs, against 124,750 for 500 bodies: sixteen times as many pairs for four times the bodies, because the pairs grow with the square. A broad phase keeps only the pairs of overlapping boxes.
   :::

2. Which statement about the three broad phases is right? (a) A grid works best when bodies differ greatly in size. (b) Sweep and prune works well whatever the scene's shape along its axis. (c) A tree of fat boxes changes only for bodies whose real box left the fat box. (d) A tree makes the exact test unnecessary.

   :::answer{tests="broad-approaches"}
   Only (c). A grid wants one cell size, so (a) is wrong. Sweep and prune suffers when bodies pile along the sorted axis, so (b) is wrong. The broad phase only drops pairs, and the narrow phase still computes contacts, so (d) is wrong.
   :::

3. Box P has centre $(0, 0)$ and half widths $(1, 1)$. Box Q has half widths $(0.5, 0.5)$ and centre $(1.2, 0.3)$. Do they overlap, and what is the depth and normal?

   :::answer{tests="narrow-contact"}
   On x the half widths sum to 1.5 and the centres are 1.2 apart: overlap 0.3. On y they sum to 1.5 and the centres are 0.3 apart: overlap 1.2. No gap on either axis, so the boxes overlap. The smallest overlap is on x: depth 0.3 m, normal $+x$.
   :::

4. A cube whose farthest corner is 0.9 m from its centre slid 4 cm and turned 2° (0.0349 radians). Is its contact recycled at 5 cm?

   :::answer{tests="recycle-gates"}
   The arc is $0.0349 \times 0.9 = 0.0314$ m. The total, $0.04 + 0.0314 = 0.0714$ m, is over 0.05, so the contact is collided again, although the turn is under 10°.
   :::

5. A crate slides over a floor of 1 m box tiles and hops at each seam. A friend suggests setting the recycle distance to 0. What happens?

   :::answer{tests="seam-bump"}
   Most of the bump stays: in the sweep it was 44 mm at 2 m/s even with recycling off, because the tiles' inner edges cause it. The change removes at most about 5 mm and makes contact work cost more. Use one collider or a triangle mesh.
   :::

## Exercises

1. **Basic.** In `Strata/vendor/box3d/src`, find where box3d finds new pairs and where it decides to recycle a contact. Name each function and a line.

   :::answer[Worked solution]{tests="broad-approaches,recycle-gates"}
   Search the folder for `UpdateBroadPhasePairs` and for `Recycle`. The pair search is `b3UpdateBroadPhasePairs`, which starts at line 649 of `broad_phase.c`. The recycling decision lives in `b3CollideTask`, the contact update task of `physics_world.c`. Its turn and distance gates stand at line 678, and the count of recycled contacts rises at line 725.
   :::

2. **Medium.** Write a function `Recycles` that decides whether a contact is recycled from the distance moved, the turn in degrees, the farthest extent and the tolerance. Run it on the four cases of the example.

   :::answer[Worked solution]{tests="recycle-gates" solution="sketches/physics-collision-detection-recycle.cpp"}
   The turn gate turns half the turn into a cosine and squares it. The movement gate adds the distance and the arc.

   ```cpp sketch="physics-collision-detection-recycle.cpp"
   // Applies the two gates box3d uses before it recycles a touching contact (the page's numbers).
   #include <cmath>
   #include <cstdio>

   // distance: how far the bodies' relative pose moved, in metres; turnDegrees: how far one body turned.
   // extent: the farthest point of the bodies from their centres, in metres; tolerance: the recycle distance.
   static bool Recycles(float distance, float turnDegrees, float extent, float tolerance)
   {
   	const float cosHalfTurn = std::cos(turnDegrees * 0.5f * 3.14159265f / 180.0f);
   	const bool turnedLittle = cosHalfTurn * cosHalfTurn > 0.99240388f;
   	// The farthest point swings along an arc of about the turn (in radians) times the extent.
   	const float arc = turnDegrees * 3.14159265f / 180.0f * extent;
   	return turnedLittle && distance + arc < tolerance;
   }

   int main()
   {
   	std::printf("3.0 cm, 1 degree:  %s\n", Recycles(0.030f, 1.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
   	std::printf("3.6 cm, 1 degree:  %s\n", Recycles(0.036f, 1.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
   	std::printf("0.5 cm, 12 degrees: %s\n", Recycles(0.005f, 12.0f, 0.87f, 0.05f) ? "recycled" : "collided again");
   	std::printf("3.0 cm, 1 degree, tolerance 0: %s\n", Recycles(0.030f, 1.0f, 0.87f, 0.0f) ? "recycled" : "collided again");
   	return 0;
   }
   ```

   ```text output-of="physics-collision-detection-recycle.cpp"
   3.0 cm, 1 degree:  recycled
   3.6 cm, 1 degree:  collided again
   0.5 cm, 12 degrees: collided again
   3.0 cm, 1 degree, tolerance 0: collided again
   ```

   1. **Lines 9–10:** the turn gate, with box3d's constant for 10°.
   2. **Line 12:** the arc of the farthest point, as the turn in radians times the extent.
   3. **Line 13:** both gates must pass.

   The first case adds 3.0 cm and 1.5 cm and stays under 5 cm. The second reaches 5.1 cm. The third fails the turn gate, and the fourth has no tolerance left.
   :::

3. **Hard.** Design a test for a box that slides at 2 m/s over a lane of 1 m tiles and over one collider of the same length. Say what you record and what you expect.

   :::answer[Worked solution]{tests="seam-bump"}
   Use two worlds with no friction, and push the same box at 2 m/s in each. Record the height of the box's centre every step. Over the tiles it rises at the seams, about 44 mm at most. Over the single collider the height stays flat.

   Run both at the recycle distance of 5 cm and at 0. The tiles bump in both runs, which shows recycling is not the cause. Strata's tests build such a lane in `StrataTests/src/Physics/PhysicsScenes.cpp` (`CreateTileLane`).
   :::

## Where it lives in Strata

- The broad phase and narrow phase are box3d's: `Strata/vendor/box3d/src/broad_phase.c`, `dynamic_tree.c`, `convex_manifold.c`, `distance.c` and `physics_world.c`.
- Strata's side: `Strata/src/Strata/Physics/PhysicsWorld.cpp` (shape creation, parking, the recycle distance), `Strata/src/Strata/Physics/PhysicsFilters.h` (the parked filter), `Strata/src/Strata/Physics/PhysicsMeshShapes.h` (hull limits) and `Strata/src/Strata/Physics/PhysicsTypes.h` (`c_DefaultContactRecycleDistance`).
- The project setting is `ContactRecycleDistance` of the `Physics.Simulation` section.
- The tile lane and the seam probe are in `StrataTests/src/Physics/PhysicsScenes.cpp` (`CreateTileLane`, `CreateSeamProbe`).

## Further reading

- Christer Ericson, *Real-Time Collision Detection* (2005): grids, sweep and prune, trees, the separating axis test and GJK, in full. Intermediate to advanced.
- Erin Catto, GDC talks on dynamic trees and on GJK: the reasoning behind fat boxes and the simplex. Intermediate.
- Box3d's source in `Strata/vendor/box3d/src`: the pair search, the manifolds and the recycling gates in working code. Advanced.

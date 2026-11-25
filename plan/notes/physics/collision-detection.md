# Notes: physics/collision-detection

## Since

`since: 0.7.0`: the inventory dates box3d's contact recycling and the physics module's parking and tile rules to 0.7.0 (`plan/inventory/physics.md`, rows 12, 62, 76, 147). The broad phase and narrow phase themselves are box3d's, in use from the first physics release; the page teaches Strata at 0.7.0 and later.

## New terms

- Sweep and prune: a broad phase that sorts bounding boxes along one axis and compares only boxes whose intervals overlap. Home: this page. Aliases: sweep-and-prune.
- Uniform grid: a broad phase that writes each body into the cells of an equal-sized grid and pairs bodies sharing a cell. Home: this page.
- Dynamic tree: a binary tree of bounding boxes in which each inner box encloses its children, updated as bodies move. Home: this page.
- Fat box: a bounding box larger than the body's real box by a margin, so the tree changes only when the real box leaves it. Home: this page. Alias: fattened box.
- Separating axis test: the narrow-phase test that declares two convex shapes apart when some axis shows a gap between their projections, and takes the axis of least overlap otherwise. Home: this page.
- Support point: the point of a convex shape that lies farthest along a given direction. Home: this page.
- Simplex: the smallest set of points (point, segment, triangle, pyramid) that GJK keeps as its current guess. Home: this page.
- GJK (Gilbert-Johnson-Keerthi): the algorithm that finds the closest points of two convex shapes from their support points. Home: this page.

## Requests

- Words for `tools/data/extra-words.txt`: solver, simplex (if not admitted as a term), GJK (acronym; expansion Gilbert-Johnson-Keerthi is bold on the page).
- Names for `tools/data/names.txt`: Ericson, Catto, PhysX.
- Hosts for `tools/external-hosts.txt`: box2d.org (Erin Catto's dynamic tree and GJK talks and posts), gdcvault.com (the talks); the page cites them without links.
- Figure `recycle-gates` (kind diagram): not drawn. A side view of a small box on a larger box, a dot for the contact point computed earlier, the upper box moved a few centimetres and overhanging the edge, the dot still under it. The manifest entry is in `src/content/figures/physics/collision-detection.json`.
- Links to pages of the plan that may not exist yet: `physics/dynamics`, `physics/tuning`, `physics/queries`, `physics/collision-layers`, `physics/scale-streaming`, `appendix/not-in-strata`.

## Not verified

- The other engines' broad phases in the table (Bullet offers sweep and prune and a dynamic tree, PhysX offers sweep and prune, Box2D uses a dynamic tree) come from general knowledge and Ericson and Catto, not from the pin.
- Why tile seams bump (the tilted edge normal): the explanation is the standard one; the pin's guide states only the heights (44 mm at 2 m/s) and that they come mostly from the tiles' inner edges.
- That a hull against a hull never runs GJK: `b3CollideHulls` was read (separating axis queries, clipping, edge contact); GJK use elsewhere was read for sphere, capsule and mesh cases only.
- The number of points on a tilted box (2): derived from the clipping and the 2 cm speculative distance, not run.

## Findings not applied

- The brief's item `new:12` (a doctest of a box pushed along a lane of tiles against one collider, with an engine patch): not written. The page's done exercise is a standalone sketch of the recycle gates, and the trace exercise names the two box3d functions with lines. The seam probe is named in the exercise 3 answer (`CreateTileLane`).
- `physics:410`, `:363`: the figure is requested but not drawn.

## Clerk

- Admitted terms homed here: sweep and prune, Uniform grid (physics) (the glossary's uniform grid is ui/input's), dynamic tree, fat box (alias fattened box), separating axis test, support point, simplex.
- GJK is not bold on the page: admitted to extra-words.txt instead, with solver and overhangs (the figure's).
- Admitted to names.txt: Ericson, Catto, PhysX.
- Admitted to external-hosts.txt: box2d.org, gdcvault.com (each front page is the site it claims).

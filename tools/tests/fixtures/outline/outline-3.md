# A small outline for the tools' tests, file 3

Columns as in outline-1.md.

## Part 5 — The GPU (`gpu`)

Tracks: E

Needs of the part: `world/ecs`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `gpu/frame` | One frame on the GPU | I | M | E | `world/ecs` | new · W8r (the passes) |

## Part 6 — Drawing a scene (`draw`)

Tracks: E

Needs of the part: `gpu/frame`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `draw/culling` | What the camera sees | I | M | E | `gpu/frame` | new · W8 |

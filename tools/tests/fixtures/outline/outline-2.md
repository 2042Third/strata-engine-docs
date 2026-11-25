# A small outline for the tools' tests, file 2

Columns as in outline-1.md.

## Part 3 — Engine architecture (`core`)

Tracks: E.

Needs of the part: `start/install`, `basics/math-vectors`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `core/map` | The map of the engine | C | M | E | `start/install` | new |
| `core/time` | Time: delta time and the fixed step | I | L | E | `core/map`, `basics/math-vectors` | new |

## Part 4 — Scenes and the ECS (`world`)

Tracks: E

Needs of the part: `core/time`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `world/ecs` | Entities and components | I | M | E | `core/time` | new |

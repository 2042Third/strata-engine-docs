# A small outline for the tools' tests

The rules are those of plan/outline-1.md; tools/tests/helpers.py names this book's decisions (c_TestBook).

## Part 0 — Start here (`start`)

Tracks: G, E, B (`start/coming-from`: G, E).

Needs of the part: -

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `start/welcome` | What the test book teaches | C | S | G, E, B | - | new |
| `start/install` | Installing the test engine | H | M | G, E, B | - | new |
| `start/coming-from` | Coming from another engine | H | S | G, E | `start/welcome` | new |

## Part 1 — Making games (`make`)

Tracks: G, B (block A); G only (blocks B and C).

Needs of the part: `start/install`, `basics/tools`\|`start/install`, `basics/programming-1`

**Block A — Your first game**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/editor-tour` | A tour of the editor | T | M | G, B | `start/install` | new |
| `make/first-script` | Your first script | T | M | G, B | `make/editor-tour`, `basics/tools`\|`start/install` | new |
| `make/script-loop` | When scripts run | H | M | G, B | `make/first-script`, `basics/programming-1` | new |
| `make/scenes` | Scenes and entities | C | M | G, B | `make/script-loop` | new |
| `make/materials` | Giving things a surface | H | S | G, B | `make/scenes` | new |

**Block B — The toolbox**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/gameplay-math` | Mathematics for gameplay | H | M | G | `make/materials`, `basics/math-vectors`\|`make/script-loop` | new |
| `make/timers` | Timers and events | H | S | G | `make/gameplay-math` | new |

**Block C — Projects**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/project` | A small project | T | L | G | `make/timers` | new |

## Part 2 — Foundations (`basics`)

Tracks: B, E, G (G only for `basics/programming-1`).

Needs of the part: `start/install`, `make/first-script`\|`start/install`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/computer` | What a computer does | P | M | B, E | `start/install` | new |
| `basics/tools` | The terminal and git | P | M | B, E | `basics/computer`\|`start/install` | new |
| `basics/programming-1` | Programming from zero | P | L | G, B, E | `make/first-script`\|`start/install` | new |
| `basics/math-vectors` | Vectors | P | M | B, E | `basics/programming-1` | new |

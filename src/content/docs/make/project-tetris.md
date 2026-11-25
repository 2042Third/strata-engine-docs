---
id: make/project-tetris
title: "Project: Tetris"
description: "Build Tetris in eight stages: rules in a plain class, a board script, held keys, a score display, sounds, a play-test with an exact score, and an export."
kind: tutorial
size: XL
tracks: [G]
needs: [make/designing-a-game, make/recipes, make/automated-playtests]
time: 240
learn:
  - id: rules-class
    text: explain why the rules of a game live in a plain C++ class and what the board script feeds into it
  - id: draw-once
    text: build a grid of cell entities that a script creates once and then shows, hides and colors again
  - id: input-gravity
    text: write held keys with KeyRepeat and gravity as a running total of delta time
  - id: hud-reload
    text: build a HUD whose texts change only when a value changes, and a script that survives a hot reload
  - id: playtest-export
    text: write a command script that expects an exact score, break the rules to see it fail, and export the game
since: 0.3.0
status: final
---

## What you will make

You build Tetris: ten columns, twenty rows, seven pieces and rows that clear. Levels fall faster, a ghost shows where the piece will land, a preview shows the next piece, and the game has a pause and a game over. At the end you own an exported game and a test that fails when its rules break.

::figure{id=result}

## How the game is built

The design fits one paragraph, as [Designing a game](designing-a-game.md) taught. The player moves and turns a falling piece in a well ten cells wide and twenty tall. A piece that rests on something locks into the well, and a full row disappears. Every ten rows the level rises by one, and a higher level makes the piece fall faster. The game ends when a new piece has no room.

The :term[core loop]{id=core-loop} is short: a piece falls, the player steers it, it locks, rows clear and the score grows. The rest of the page builds that loop in eight stages. Each stage ends with a checkpoint, a state of the project that you can download and compare with your own.

A game has two kinds of code. The **rules** are what the game is: where a piece may go, when a row is full, how many points a row gives. The rest is the engine's business: reading keys, counting time, showing cubes and text, and Tetris keeps the two apart. The rules live in a plain C++ class, `Tetris::Game`, that calls nothing of the engine. A script, `TetrisBoard`, feeds the class keys and time and draws what it answers.

```mermaid caption="The board script feeds input and time into the rules and draws their state as cells and texts; the rules call nothing of the engine." alt="Flow from keys and delta time into the board script, from the script into the rules class and back, and from the script to the cell entities and the HUD texts."
flowchart LR
  Input[Keys and delta time] --> Board[TetrisBoard script]
  Board -->|moves and steps| Rules[Tetris::Game rules]
  Rules -->|cells, piece, score| Board
  Board -->|show, hide, recolor| Cells[Cell entities]
  Board -->|text| HUD[HUD texts]
```

:::why
The rules stay free of the engine for two reasons. You can read them top to bottom without knowing the engine, and a mistake in them cannot hide in a frame or an entity. The cost is a second file and a translation: the script copies the rules' state into entities every frame. The class could be tested without the engine, but no test of the engine's repository builds it: the only test of this game runs the whole script, as stage 7 does.
:::

### The rules as data

Every number of the rules is data, not code. The well is `c_Width` = 10 columns and `c_Height` = 20 rows, plus four hidden rows above row 19, where a turning piece may reach. A new piece appears with its top cells in row 19, and row 0 is the bottom.

A piece is four cells inside a square, its **rotation box**: 4 cells wide for the long piece, 2 for the square one, 3 for the other five. The five pieces of width 3 sit in the box's left three columns, and the long and square pieces fill their box. A quarter turn clockwise moves each cell from $(x, y)$ to $(y, s - 1 - x)$. Here $x$ and $y$ are the cell's column and row in the box, counted from its bottom left, and $s$ is the box's size.

Take the J piece in its box of size 3. Its cells are (0, 2), (0, 1), (1, 1) and (2, 1). One turn gives (2, 2), (1, 2), (1, 1) and (1, 0): a bar of three cells in the middle column with one cell on top at the right. Four turns return every cell to where it began.

A **7-bag** is the way the game deals pieces: it puts one of each of the seven pieces into a bag, shuffles them and deals them one by one. When the bag is empty it makes a new one. A piece can come twice in a row only at the border of two bags, and the longest wait for one piece is 12 deals. Plain random choice allows a drought of any length. The shuffle uses a seeded `Random`, which [Recipes for common game code](recipes.md) taught, so the same seed deals the same pieces.

The board script finds each cell by its place. Cell $(x, y)$ stands at the :term[world position]{id=world-position} $(x, y, 0)$ from the board entity's origin, one world unit per cell, and the next piece shows at an offset of 12 columns and 15 rows.

::figure{id=well-coordinates}

## What you need

- A new project from the Basic 3D template, named `Tetris`, as in [Project files](project-files.md). Each stage starts from the checkpoint of the stage before; the last one is the end state.
- A copy of the Tetris sample to compare with: choose **File ▸ Open Sample ▸ Tetris** in the launcher or the editor and pick an empty folder. You never change the sample itself, only your copy.
- The script files of this page's checkpoint downloads. Each download is a whole project named `ProjectTetris`, and you copy only files of its folder `Scripts`: `TetrisGame.h` and `TetrisGame.cpp` (the rules) and `TetrisBoard.cpp`. The board file grows with the stages: checkpoint 2 holds its first version, checkpoint 6 the final one. They are the sample's own scripts, cut down to what each stage needs; the page quotes the lines that teach.
- Five files from the release's folder `Samples/Tetris/Assets/`: the four sounds `Move.wav`, `Lock.wav`, `Clear.wav` and `GameOver.wav` in its `Sounds` folder, and `Icon.png`. Strata's own makers wrote them for the sample, and its `CREDITS.md` credits them to Strata.
- About four hours. Stages 1 to 3 take half of them.

## Build the well

The well is a stage set: three walls, a floor and a dark backdrop, all scaled cubes. They are scenery, so no script touches them. You make them once and group them under one entity.

The cells of the game are one world unit wide, so a cube of scale 1 is one cell. The left wall stands one cell left of column 0 and the right wall one cell right of column 9. Each wall is 22 cells tall, which covers the 20 rows and the floor below them.

:::::steps

1. Create the project and look at it. Make a project named `Tetris` from the Basic 3D template, as you did in [Project files](project-files.md), and open `Scenes/Main.stscene`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Project...**, pick the Basic 3D card, type `Tetris` as the name and create the project. The Hierarchy lists Main Camera, Sun, Sky, Ground and Post Process.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.create", "parameters": { "directory": "<a new folder>/Tetris", "name": "Tetris", "template": "basic3d" } }
   ```

   :::
   ::::

   **You should see:** the five entities and a flat ground in the Scene view.

   **If you do not see it:** the project opened another scene. Choose **File ▸ Open Scene...** and pick `Main.stscene`.

2. Delete the Ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Ground` in the Hierarchy and press **Delete**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.find", "parameters": { "name": "Ground" } }
   { "command": "entity.delete", "parameters": { "entities": ["<ID of Ground>"] } }
   ```

   Commands name an entity by its identifier (ID), not by its name. `entity.find` answers the IDs of the entities with a name, and `entity.create` answers the ID of the entity it makes: every `<ID of Name>` on this page is such an answer.
   :::
   ::::

   **You should see:** no `Ground` in the Hierarchy, and no entity with a :term[collider]{id=collider} under the origin. Below the horizon the view still shows a plain, pale brown surface. The sky draws it as the ground of its planet: it is a picture, and no entity stands there.

   **If you do not see it:** you deleted another entity. Press **Ctrl+Z** and choose `Ground` again.

3. Make the wall material and the backdrop material.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser press **New ▸ Folder** and name it `Materials`. Open it, press **New ▸ Material**, name it `Wall` and set `BaseColor` to 0.35, 0.38, 0.45, `Metallic` to 0.2 and `Roughness` to 0.7. Make `Backdrop` the same way with `BaseColor` 0.04, 0.045, 0.06 and `Roughness` 0.9.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Wall.stmat", "properties": { "BaseColor": [0.35, 0.38, 0.45, 1.0], "Metallic": 0.2, "Roughness": 0.7 } } }
   ```

   Run `material.create` again for `Materials/Backdrop.stmat` with `BaseColor` `[0.04, 0.045, 0.06, 1.0]` and `Roughness` 0.9.
   :::
   ::::

   **You should see:** two materials in the folder `Materials`.

   **If you do not see it:** the material is in the wrong folder. Drag it into `Materials`: the editor keeps the handles right.

4. Make the `Well` entity and its five cubes. Each cube is a child of `Well`, has the :term[built-in mesh]{id=built-in-mesh} `Cube` and is placed and scaled by the table.

   | Name | Translation | Scale | Material |
   | --- | --- | --- | --- |
   | `LeftWall` | -1, 9.5, 0 | 1, 22, 1 | `Wall` |
   | `RightWall` | 10, 9.5, 0 | 1, 22, 1 | `Wall` |
   | `Floor` | 4.5, -1, 0 | 10, 1, 1 | `Wall` |
   | `Backdrop` | 4.5, 9.5, -0.75 | 10, 20, 0.5 | `Backdrop` |
   | `PreviewBackdrop` | 13.5, 16, -0.75 | 5, 4, 0.5 | `Backdrop` |

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** and choose **Empty**, then rename it `Well` with **F2**. Press **+** and choose **Cube**, rename it, drag it onto `Well`, and type its **Translation** and **Scale** from the table. Pick its material in the **Material** picker of **Mesh Renderer**. Repeat for the other four.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "LeftWall", "parent": "<ID of Well>", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Wall.stmat" }, "Transform": { "Translation": [-1, 9.5, 0], "Scale": [1, 22, 1] } } } }
   ```

   Create `Well` first with `entity.create` and only its name, then run this command once for each row of the table.
   :::
   ::::

   **You should see:** a gray U of three cubes and a dark panel behind it, with a smaller dark panel to its right.

   **If you do not see it:** the cubes are outside the Scene view. Select `Well` and press **F** to frame it.

5. Move the camera to face the well. A perspective camera at (5.5, 9.5, 30) with no rotation looks along the minus Z axis at the well's middle, 30 units away.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Main Camera`. In the Inspector type **Translation** 5.5, 9.5, 30 and **Rotation** 0, 0, 0. Press **Ctrl+S** to save the scene.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<ID of Main Camera>", "component": "Transform", "values": { "Translation": [5.5, 9.5, 30], "Rotation": [0, 0, 0] } } }
   { "command": "viewport.capture", "parameters": { "camera": "scene" } }
   ```

   Outside play, `viewport.capture` looks through the editor camera of the Scene view. With `camera` set to `scene` it looks through `Main Camera`, as the Game view does.
   :::
   ::::

   **You should see:** in the Game view the whole well, the preview panel at its upper right, and the sky behind.

   **If you do not see it:** the well looks tilted. The camera kept the template's rotation: set **Rotation** to 0, 0, 0.

:::::

::checkpoint{stage=1}

::figure{id=well-built}

## Write the rules

The rules take a whole stage, because they are the game. You do not type them: you copy the two files `TetrisGame.h` and `TetrisGame.cpp` of the checkpoint download and read them in pieces. The pieces answer five questions: what the well is, where a piece may be, how a piece turns, how a piece locks, and how the next piece is chosen.

:::question
The rules use `constexpr` constants, an enum with a fixed type, `static_cast`, pointers such as `const char*` and lambdas. [Modern C++ as Strata uses it](../basics/cpp-modern.md), [C++ memory](../basics/cpp-memory.md) and [Generic C++](../basics/cpp-generic.md) teach them; this page explains each where it first appears.
:::

### The well and the pieces

The header starts with the numbers of the rules and the names of the pieces. Read it as the dictionary of the file.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.h#L14-L34"
constexpr int32_t c_Width = 10;
constexpr int32_t c_Height = 20;                // Visible rows
constexpr int32_t c_TotalHeight = c_Height + 4; // Hidden rows above the well, where pieces spawn and rotate
constexpr int32_t c_PieceTypeCount = 7;
constexpr int32_t c_Empty = -1;

// Values index the piece colours (TetrisBoard's material fields) and name the pieces in logs.
enum class PieceType : int32_t
{
	I = 0, O, T, S, Z, J, L
};

const char* GetPieceName(PieceType type);

struct Cell
{
	int32_t X = 0;
	int32_t Y = 0; // 0 is the bottom row
};

using PieceCells = std::array<Cell, 4>;
```

1. **Lines 14–18:** the sizes of the rules as `constexpr` constants: the well is 10 by 20, and four hidden rows make 24.
2. **Lines 21–24:** the seven piece types as an `enum class` of the type `int32_t`; I is 0, and the board uses the number as the index of its material.
3. **Line 26:** `GetPieceName` returns a `const char*`, a pointer to fixed text, for the log lines.
4. **Lines 28–34:** a cell is a column `X` and a row `Y`, row 0 at the bottom; `using` gives four cells the name `PieceCells`.

A `constexpr` value is a constant that the compiler knows. `PieceType` is an `enum class` whose values count from 0, and `static_cast` converts between the enum and a number, as the bag of this stage does when it turns a number into a piece. The piece types stand in the order I, O, T, S, Z, J and L, and the board script uses the number as the index of its materials.

The cells of a piece are stored in the :term[source file]{id=source-file}, as data. Each entry says the box size and four cells.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.cpp#L11-L33"
struct ShapeInfo
{
	int32_t BoxSize;  // Side of the rotation box
	PieceCells Cells; // Spawn orientation, y up
};

// Spawn orientations as in most modern versions: flat side down, I and O centered, the rest in the left three columns
// of their box.
constexpr std::array<ShapeInfo, c_PieceTypeCount> c_Shapes = { {
	{ 4, { { { 0, 2 }, { 1, 2 }, { 2, 2 }, { 3, 2 } } } }, // I
	{ 2, { { { 0, 0 }, { 1, 0 }, { 0, 1 }, { 1, 1 } } } }, // O
	{ 3, { { { 1, 2 }, { 0, 1 }, { 1, 1 }, { 2, 1 } } } }, // T
	{ 3, { { { 1, 2 }, { 2, 2 }, { 0, 1 }, { 1, 1 } } } }, // S
	{ 3, { { { 0, 2 }, { 1, 2 }, { 1, 1 }, { 2, 1 } } } }, // Z
	{ 3, { { { 0, 2 }, { 0, 1 }, { 1, 1 }, { 2, 1 } } } }, // J
	{ 3, { { { 2, 2 }, { 0, 1 }, { 1, 1 }, { 2, 1 } } } }, // L
} };

// Offsets tried in order when a rotation does not fit where it is.
constexpr std::array<Cell, 6> c_Kicks = { { { 0, 0 }, { -1, 0 }, { 1, 0 }, { 0, 1 }, { -2, 0 }, { 2, 0 } } };

// Points for 1 to 4 rows cleared at once, multiplied by the level.
constexpr std::array<int32_t, 5> c_LineScores = { 0, 100, 300, 500, 800 };
```

1. **Lines 11–15:** the box size and the four cells of a piece in its first pose.
2. **Lines 19–27:** one row per piece, in the order of `PieceType`; a :term[namespace]{id=namespace} with no name, which opens at line 8, hides the tables from other files.
3. **Lines 30–33:** the six kick offsets in the order they are tried, and the points for 0 to 4 rows at once.

The lines are the whole table of the game, and each one answers a question about the rules.

### Moves, kicks and turns

`GetShape` turns a piece: it repeats the quarter turn once for each turn of the rotation. Its core is the line `cell = Cell { cell.Y, shape.BoxSize - 1 - cell.X };`, which is the formula $(x, y) \to (y, s - 1 - x)$ written as code, with `BoxSize` as $s$.

A **kick** is a small shift that the game tries when a turned piece does not fit. Against a wall, a turn would put a cell outside the well, and the player expects the piece to move away from the wall instead of refusing. `Rotate` tries the six offsets of the table one by one and keeps the first that fits.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.cpp#L90-L108"
bool Game::Rotate(int32_t direction)
{
	if (m_GameOver || m_Piece.Type == PieceType::O)
		return false;
	Piece rotated = m_Piece;
	rotated.Rotation = (m_Piece.Rotation + (direction >= 0 ? 1 : 3)) % 4;
	for (const Cell& kick : c_Kicks)
	{
		Piece kicked = rotated;
		kicked.X += kick.X;
		kicked.Y += kick.Y;
		if (Fits(kicked))
		{
			m_Piece = kicked;
			return true;
		}
	}
	return false;
}
```

1. **Line 92:** the square piece never turns, since every pose looks the same.
2. **Lines 95–96:** the new rotation is one more turn, or three more for the other direction, wrapped at 4.
3. **Lines 97–107:** try each kick, keep the first pose that fits, and fail when none does.

A move that fails returns `false` and changes nothing: the piece stays where it was. That rule lets the board script call a move without checking first.

### Locking, clearing and scoring

When a piece cannot fall further, `Lock` writes its cells into the well, removes full rows, adds the points and deals the next piece. The points for a number of rows are in the table `c_LineScores` of the first excerpt: 100, 300, 500 and 800 for one to four rows, times the level.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.cpp#L195-L215"
StepResult Game::Lock()
{
	StepResult result;
	result.Locked = true;
	bool aboveWell = true;
	for (const Cell& cell : GetPieceCells())
	{
		m_Cells[static_cast<size_t>(cell.Y)][static_cast<size_t>(cell.X)] = static_cast<int32_t>(m_Piece.Type);
		aboveWell = aboveWell && cell.Y >= c_Height;
	}

	result.LinesCleared = ClearFullRows();
	const int32_t level = GetLevel();
	m_Score += c_LineScores[static_cast<size_t>(result.LinesCleared)] * level;
	m_Lines += result.LinesCleared;

	// A piece that locked entirely above the well, or a next piece without room, ends the game.
	m_GameOver = aboveWell || !SpawnNext();
	result.GameOver = m_GameOver;
	return result;
}
```

1. **Lines 200–204:** write each cell of the piece into the well, and note whether all of them lie above the visible rows.
2. **Lines 206–209:** remove the full rows, then add the points at the current level and count the lines. The level is read before the lines grow, so a row scores at the level it was cleared on.
3. **Line 212:** the game ends when the piece locked above the well or the next piece has no room.

`ClearFullRows` is a copy with a gap: it walks the rows from the bottom, skips each full row, and moves every other row down to the first free place. The rows above the last copy are filled with empty cells.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.cpp#L217-L237"
int32_t Game::ClearFullRows()
{
	int32_t cleared = 0;
	int32_t target = 0;
	for (int32_t y = 0; y < c_TotalHeight; y++)
	{
		const std::array<int32_t, c_Width>& row = m_Cells[static_cast<size_t>(y)];
		const bool full = std::none_of(row.begin(), row.end(), [](int32_t cell) { return cell == c_Empty; });
		if (full)
		{
			cleared++;
			continue;
		}
		if (target != y)
			m_Cells[static_cast<size_t>(target)] = row;
		target++;
	}
	for (int32_t y = target; y < c_TotalHeight; y++)
		m_Cells[static_cast<size_t>(y)].fill(c_Empty);
	return cleared;
}
```

1. **Lines 221–229:** walk the rows from the bottom; a row is full when `std::none_of` finds no empty cell, and a full row is counted and skipped. The brackets in line 224 open a lambda, a small function that tests one cell.
2. **Lines 230–233:** a row that stays is copied down to the first free place, `target`.
3. **Lines 234–235:** the rows above the last copy are emptied.

### The bag

`DrawFromBag` is the 7-bag in 13 lines. It fills the bag in order and then shuffles it with a standard method. From the last place down to place 1, it swaps the piece there with a piece at a random place from 0 to that one.

```cpp src="book:tutorials/make/project-tetris/TetrisGame.cpp#L255-L267"
PieceType Game::DrawFromBag()
{
	if (m_BagIndex >= c_PieceTypeCount)
	{
		// A new bag holds each piece once, in random order (Fisher-Yates shuffle).
		for (int32_t index = 0; index < c_PieceTypeCount; index++)
			m_Bag[static_cast<size_t>(index)] = static_cast<PieceType>(index);
		for (int32_t index = c_PieceTypeCount - 1; index > 0; index--)
			std::swap(m_Bag[static_cast<size_t>(index)], m_Bag[static_cast<size_t>(m_Random.Range(0, index))]);
		m_BagIndex = 0;
	}
	return m_Bag[static_cast<size_t>(m_BagIndex++)];
}
```

1. **Line 257:** a new bag begins when all seven pieces were dealt.
2. **Lines 260–263:** fill the bag in order, with `static_cast` turning a number into a `PieceType`, then shuffle it: `std::swap` exchanges two places.
3. **Line 266:** deal the next piece of the bag.

Try it with three pieces A, B and C in places 0, 1 and 2. The loop starts at place 2 and draws a random place from 0 to 2: with the draw 0 it swaps C and A, giving C, B, A. At place 1 it draws 0 or 1: with 1 it swaps B with itself. Every one of the six orders can appear, each with the same chance.

:::::steps

1. Copy the rules into the project.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...** and make a class `TetrisBoard`. Close the editor's text of it. Copy `TetrisGame.h`, `TetrisGame.cpp` and `TetrisBoard.cpp` from the folder `Scripts` of checkpoint 2's download, at the end of this section, into the folder `Scripts` of the project. The board file replaces the one the dialog made.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "TetrisBoard" } }
   ```

   Then copy the three files as the editor tab says: no command writes code for you.
   :::
   ::::

   **You should see:** your three files in the project's folder `Scripts`: `TetrisGame.h`, `TetrisGame.cpp` and `TetrisBoard.cpp`. Beside them stand the template's `Spinner.cpp` and `CMakeLists.txt`, the file that tells the build what to compile.

   **If you do not see it:** the editor did not find the files. Run the configure of the scripts again with **Scripts ▸ Build Scripts**, which reads the folder.

2. Build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the status bar reports a finished build and the :term[Problems panel]{id=problems-panel} is empty.

   **If you do not see it:** the Problems panel names a line. A second board file, such as a copy under another name, is in `Scripts`: delete it.

3. Make the `Board` entity and attach the script. It stands at the origin, because the well's bottom-left cell sits at the entity's origin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+**, choose **Empty** and rename it `Board`. Choose **Add Component ▸ Script** and pick `TetrisBoard` in **Add Script...**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Board" } }
   { "command": "script.add", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard" } }
   ```

   :::
   ::::

   **You should see:** the script's three fields `Seed` (60), `Start Level` and `Lines Per Level` in the Inspector.

   **If you do not see it:** the class is not listed. Build again with **Ctrl+B**.

4. Play, and read the log. The board starts a game in `OnCreate` and logs the first two pieces.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, open the **Console** panel and press **Ctrl+P** again to stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "log.read" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the line `Tetris: new game with seed 60`, then `Tetris: piece 1 is J, next I`.

   **If you do not see it:** another piece appears. The seed is not 60: type 60 into **Seed** and play again. The same seed deals the same pieces on every computer.

:::::

::checkpoint{stage=2}

::figure{id=rules-log}

## Draw the well

The rules know the well, but nothing shows it. The board draws it with entities, and the central idea of the stage is when it makes them. A game could create a cube when a piece locks and destroy it when its row clears. Tetris makes all 200 cells of the well at the start, hides them, and later only shows, hides and colors again the ones whose piece changed. The cost is 200 entities that most of the time do nothing; the gain is that no frame creates or destroys anything, and nothing can leak.

[Patterns for game code](patterns.md) names this shape. The board makes four more cells for the next piece's preview.

### Eight materials as asset fields

A piece's color is a material. The board holds seven piece materials and one for the ghost as asset fields, a kind of :term[script field]{id=script-field} that holds an asset. You set them in the Inspector, as [Script fields](script-fields.md) taught. The rows of this table are the sample's colors.

| Material | `BaseColor` | Notes |
| --- | --- | --- |
| `PieceI` | 0, 0.85, 0.95 | light blue |
| `PieceO` | 0.95, 0.8, 0.05 | yellow |
| `PieceT` | 0.6, 0.15, 0.85 | purple |
| `PieceS` | 0.15, 0.8, 0.2 | green |
| `PieceZ` | 0.9, 0.12, 0.12 | red |
| `PieceJ` | 0.12, 0.3, 0.95 | blue |
| `PieceL` | 0.95, 0.5, 0.05 | orange |
| `Ghost` | 0.8, 0.85, 1, alpha 0.25 | `AlphaMode` `Blend` |

All piece materials have `Roughness` 0.35. The ghost has `Roughness` 0.6, and its alpha of 0.25 lets the dark well show through it, so it looks pale gray.

### Cells made once

:::question
What are `: public Script` and `override`? A :term[script class]{id=script-class} extends the engine's `Script` class and replaces the :term[callbacks]{id=callback} it needs; [C++ classes in depth](../basics/cpp-classes.md) teaches both.
:::

The first excerpt is `OnCreate`: it asks for the materials early, then makes the cells. An asset that is requested at the start is loaded by the time the first piece needs it.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step3.cpp#L41-L53"
void OnCreate() override
{
	for (AssetHandle asset : { MaterialI, MaterialO, MaterialT, MaterialS, MaterialZ, MaterialJ, MaterialL, GhostMaterial })
	{
		if (asset)
			Assets::RequestLoad(asset);
	}
	if (!CellMesh)
		CellMesh = Assets::Find("Builtin/Cube");

	CreateCells();
	NewGame();
}
```

1. **Lines 43–47:** ask for the materials at the start; an empty field is skipped.
2. **Lines 48–49:** with no mesh set, find the built-in cube by its path.
3. **Lines 51–52:** make the cells, then start a game.

`CreateCells` makes a child entity `Cells` under the board, then 200 cells row by row from the bottom, then the four preview cells. The order matters: the cell at column $x$ and row $y$ is the entry $10y + x$ of the list, which the drawing code relies on.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step3.cpp#L77-L90"
void CreateCells()
{
	Entity container = Scene::CreateEntity("Cells", GetEntity());
	m_Cells.clear();
	for (int32_t y = 0; y < Tetris::c_Height; y++)
	{
		for (int32_t x = 0; x < Tetris::c_Width; x++)
			m_Cells.push_back(CreateCell(container, glm::vec3(static_cast<float>(x), static_cast<float>(y), 0.0f)));
	}
	m_Preview.clear();
	for (int32_t index = 0; index < 4; index++)
		m_Preview.push_back(CreateCell(container, PreviewOffset));
	ResetShownTypes();
}
```

1. **Line 79:** the container `Cells` is a child of the board.
2. **Lines 81–88:** 200 cells row by row from the bottom, then four for the preview.
3. **Line 89:** every cell is marked as showing nothing known yet.

`CreateCell` makes one cube from an entity with a `MeshRenderer`, places it, scales it to `CellScale` and hides it. It has no material yet, because the first `ShowCell` sets one.

### Touching only what changed

`Refresh` runs every frame and builds a picture of the well first: a list of 200 numbers, one per cell, that says which piece type to show there or that the cell is empty. It fills the list from the rules, then adds the ghost and the falling piece.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step3.cpp#L112-L127"
void Refresh()
{
	std::vector<int32_t> types(m_Cells.size(), Tetris::c_Empty);
	for (int32_t y = 0; y < Tetris::c_Height; y++)
	{
		for (int32_t x = 0; x < Tetris::c_Width; x++)
			types[static_cast<size_t>(y * Tetris::c_Width + x)] = m_Game.GetCell(x, y);
	}
	auto place = [&](const Tetris::PieceCells& cells, int32_t type)
	{
		for (const Tetris::Cell& cell : cells)
		{
			if (cell.Y < Tetris::c_Height && types[static_cast<size_t>(cell.Y * Tetris::c_Width + cell.X)] == Tetris::c_Empty)
				types[static_cast<size_t>(cell.Y * Tetris::c_Width + cell.X)] = type;
		}
	};
```

1. **Lines 114–119:** a list of 200 numbers, filled from the well.
2. **Lines 120–127:** `place` is a lambda, a small function kept in a variable; it writes a type into the cells of a piece that lie in the visible rows and are still empty.

The loop after it, `ShowCell` for each cell, makes the cube follow the list. `ShowCell` remembers what each cell shows in `shown`, and returns at once when the new type equals it. In a quiet frame no cell changes, so the 200 calls cost 200 comparisons.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step3.cpp#L156-L170"
void ShowCell(Entity cell, int32_t& shown, int32_t type)
{
	if (shown == type)
		return;
	if (type == Tetris::c_Empty)
	{
		cell.SetActive(false);
	}
	else
	{
		cell.SetProperty("MeshRenderer", "Material", GetMaterial(type));
		cell.SetActive(true);
	}
	shown = type;
}
```

1. **Lines 158–159:** nothing to do when the cell already shows this type.
2. **Lines 160–163:** an empty place hides the cube.
3. **Lines 164–169:** another type sets the material and shows the cube, and the cell remembers its type.

The ghost cells fill only empty places of the list, and the falling piece then writes over its own ghost. That is why the piece appears in front, even where the ghost lies under it.

:::::steps

1. Make the eight materials. Use the table above.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In `Materials` press **New ▸ Material** eight times and name them `PieceI`, `PieceO`, `PieceT`, `PieceS`, `PieceZ`, `PieceJ`, `PieceL` and `Ghost`. Type each `BaseColor` and `Roughness`. For `Ghost` set `AlphaMode` to `Blend`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Ghost.stmat", "properties": { "BaseColor": [0.8, 0.85, 1.0, 0.25], "AlphaMode": "Blend", "Roughness": 0.6 } } }
   ```

   Run `material.create` for each piece with its `BaseColor` from the table and `Roughness` 0.35.
   :::
   ::::

   **You should see:** eight new materials in the folder.

   **If you do not see it:** the ghost is solid in play. Its `AlphaMode` is still `Opaque`: set `Blend`.

2. Copy `Scripts/TetrisBoard.cpp` of checkpoint 3's download, at the end of this section, over your `Scripts/TetrisBoard.cpp`, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the file's text, then press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a finished build with an empty Problems panel. The Inspector of `Board` lists the new fields.

   **If you do not see it:** a build error. The file in `Scripts` is a copy of another stage: copy this stage's file again.

3. Fill the asset fields of `Board`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Board`. For each of `Material I` to `Material L` and `Ghost Material`, click the picker and choose the material of the same name. Leave `Cell Mesh` empty: the script then uses the built-in cube.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "MaterialI", "value": "Materials/PieceI.stmat" } }
   ```

   Run `script.setField` for each of the other seven fields.
   :::
   ::::

   **You should see:** eight filled rows.

   **If you do not see it:** a picker stays empty. A material of another folder has the same name: choose the one in `Materials`.

4. Play for a moment.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, look at the Game view, then press **Ctrl+P** again.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "play.step", "parameters": { "steps": 2 } }
   { "command": "viewport.capture" }
   { "command": "play.stop" }
   ```

   A game started paused has run no :term[fixed step]{id=fixed-step}, so the board has drawn nothing yet: `play.step` runs two. While the game plays, the capture looks through the game's camera.
   :::
   ::::

   **You should see:** a blue piece (the J) at the top of the well, a pale ghost on the floor under it, and a light blue piece (the I) in the preview panel. Nothing moves yet.

   **If you do not see it:** the well is empty. A field is empty or the scripts are not built: build with **Ctrl+B** and check the fields.

:::::

::checkpoint{stage=3}

::figure{id=drawn}

## Play: keys and gravity

A game feels right when the keys feel right. Two things make Tetris ready to play: the held keys repeat, and the piece falls by the clock, not by the frame.

### Held keys

A key held for one second is down for 60 frames. Moving the piece on every one of them would send it across the well in a sixth of a second. The player expects the usual behavior of a text field: one move at once, a pause, then a steady repeat. `KeyRepeat` does this: it is a small helper of the script software development kit (:term[SDK]{id=sdk}) that you create once per key with a first delay and an interval. `Update(deltaTime)` answers true in the frame the key goes down, again after the delay, and then once per interval while the key stays down.

The board keeps one `KeyRepeat` for each of Left, Right and Down, and another for A, D and S, so a player may use an arrow or a letter. `UpdatePair` updates both of a pair every frame, because a repeat that is not updated loses track of its key.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step4.cpp#L109-L115"
// Two keys for one action (an arrow key and a letter): both are updated every frame, so their repeat state stays current.
static bool UpdatePair(KeyRepeat& primary, KeyRepeat& secondary, float deltaTime)
{
	const bool primaryFired = primary.Update(deltaTime);
	const bool secondaryFired = secondary.Update(deltaTime);
	return primaryFired || secondaryFired;
}
```

Rotation and hard drop use `Input::IsKeyPressed` instead, which is true only in the frame the key goes down: one press, one turn.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step4.cpp#L72-L88"
void Play(float deltaTime)
{
	const bool left = UpdatePair(m_Left, m_LeftAlt, deltaTime);
	const bool right = UpdatePair(m_Right, m_RightAlt, deltaTime);
	const bool softDrop = UpdatePair(m_Down, m_DownAlt, deltaTime);
	if (left != right)
		m_Game.Shift(left ? -1 : 1);
	if (Input::IsKeyPressed(Key::Up) || Input::IsKeyPressed(Key::X))
		m_Game.Rotate(1);
	if (Input::IsKeyPressed(Key::Z))
		m_Game.Rotate(-1);

	if (Input::IsKeyPressed(Key::Space))
	{
		HandleStep(m_Game.HardDrop());
		return;
	}
```

1. **Lines 74–76:** update the three pairs every frame; each answers true when one of its keys fires.
2. **Lines 77–82:** one move left or right, and a rotation at a press; both directions together cancel.
3. **Lines 84–88:** **Space** drops the piece at once and ends the frame's play.

### Gravity as a running total

Gravity must not depend on the frame rate. The script keeps a number, `m_Gravity`, and adds each frame's `deltaTime` to it. When the total reaches the interval, the piece falls one row and the interval is subtracted.

At 60 frames per second a frame lasts 0.0167 s, so with an interval of 0.8 s the total reaches it after 48 frames: one row per 0.8 s. At 30 frames per second a frame lasts 0.0333 s and it takes 24 frames: again 0.8 s. A `while` loop handles a long frame that holds several intervals at once. [The script loop](script-loop.md) taught why a game counts time and not frames.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step4.cpp#L89-L107"
	if (softDrop)
	{
		if (m_Game.SoftDrop())
			m_Gravity = 0.0f;
		else
			HandleStep(m_Game.Step()); // Resting on something: lock now
		if (m_Game.IsGameOver())
			return;
	}

	m_Gravity += deltaTime;
	const float interval = GetGravityInterval();
	while (m_Gravity >= interval && !m_Game.IsGameOver())
	{
		m_Gravity -= interval;
		if (HandleStep(m_Game.Step()))
			break;
	}
}
```

1. **Lines 89–97:** a soft drop moves one row and restarts the count; a piece that cannot move locks at once.
2. **Lines 99–106:** add the frame's time, then take one step for each full interval; a step that locks ends the loop.

The interval shrinks with the level: `StartInterval` times `IntervalFactor` for each level above the start level, never below `MinInterval`. With 0.8 s and a factor of 0.85, level 1 falls every 0.8 s, level 2 every 0.68 s and level 3 every 0.578 s. A soft drop uses its own short interval and gives one point per row; a hard drop gives two points per row.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step4.cpp#L130-L135"
float GetGravityInterval() const
{
	const int32_t levelsAbove = std::max(m_Game.GetLevel() - std::max(StartLevel, 1), 0);
	const float interval = StartInterval * std::pow(IntervalFactor, static_cast<float>(levelsAbove));
	return std::max(interval, std::max(MinInterval, 0.001f));
}
```

The last line keeps the interval at `MinInterval` or more, and never below 0.001 s, so a field set to 0 cannot freeze the loop.

:::::steps

1. Copy `Scripts/TetrisBoard.cpp` of checkpoint 4's download, at the end of this section, over your `Scripts/TetrisBoard.cpp` and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the file's text and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the Inspector of `Board` gains `Start Interval`, `Interval Factor`, `Min Interval`, `Soft Drop Interval`, `Repeat Delay` and `Repeat Interval`, and your eight material fields keep their values.

   **If you do not see it:** the material fields are empty. A field keeps its value only when the new class has a field of the same name and type: set them again.

2. Play, and move the piece.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**. Click the Game view so that it takes the keys. Press **Left**, hold **Right**, press **Up** and **Space**.
   :::
   :::tab[With a command]
   Start the game paused, then tap **Left** and **Space** in fixed steps, and look.

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "input.sequence", "parameters": { "steps": 4, "events": [ { "step": 0, "key": "Left", "action": "tap" }, { "step": 2, "key": "Space", "action": "tap" } ] } }
   { "command": "viewport.capture" }
   ```

   `input.sequence` runs one fixed step per frame with its keys, so the result is the same on every computer. A paused game sees an `input.key` only at its next step, so that command answers `seen` false at once.
   :::
   ::::

   **You should see:** the piece moves one cell at each press, runs along the well when you hold a key, rotates with **Up**, and falls to the floor on **Space**, where the next piece appears. After the commands, the J lies on the floor one column left of where it began, and the I stands at the top.

   **If you do not see it:** no key works. The Game view has no focus: click it once.

3. Check the ghost and the soft drop.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Move the piece with the arrow keys and watch the pale ghost follow it to the floor. Hold **Down**.
   :::
   :::tab[With a command]
   Hold **Down** for 24 fixed steps, 0.4 s, and look.

   ```json
   { "command": "input.sequence", "parameters": { "steps": 24, "events": [ { "step": 0, "key": "Down", "action": "press" }, { "step": 23, "key": "Down", "action": "release" } ] } }
   { "command": "viewport.capture" }
   ```

   :::
   ::::

   **You should see:** the ghost always shows where **Space** would put the piece. Holding **Down** makes it fall at 0.04 s per row, so the I of the commands is about ten rows lower, with its ghost on the J.

   **If you do not see it:** no ghost. `Ghost Material` is empty: the script draws a ghost only when it is set.

4. Let a piece fall by itself, and fill the well to the top.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Do not touch the keys for a few seconds. Then drop pieces with **Space** until they reach the top.
   :::
   :::tab[With a command]
   Run 48 fixed steps, 0.8 s, and look. Then make every row take 0.01 s, as the play-test of stage 7 does, and run until the well is full.

   ```json
   { "command": "play.step", "parameters": { "steps": 48 } }
   { "command": "viewport.capture" }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "MinInterval", "value": 0.01 } }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "StartInterval", "value": 0.01 } }
   { "command": "play.step", "parameters": { "steps": 600 } }
   { "command": "viewport.capture" }
   { "command": "log.read" }
   { "command": "play.stop" }
   ```

   A field set while the game plays changes the running copy only, and `play.stop` throws the change away.
   :::
   ::::

   **You should see:** the piece falls one row each 0.8 s, and at the top the game stops: the pieces freeze. Nothing on the screen tells you why yet; the next stages add the heads-up display (HUD) and the game-over panel. The Console has the line `Tetris: game over after`, with the number of pieces.

   **If you do not see it:** the piece does not fall. `Start Interval` is a large number: it should read 0.8.

:::::

::checkpoint{stage=4}

::figure{id=playing}

## Show the score

The game needs numbers: score, level and lines. A game's heads-up display (HUD) is a **canvas** of user interface (UI) elements that the engine draws over the game, as [HUDs: text, score and bars](hud.md) taught. Text in the world would move with the camera, and a HUD stays in the screen's corners.

The board writes a text only when its value changes. Writing the same words again would cost little, but the rule keeps the script honest. `Refresh` remembers what it showed (`m_ShownScore` and its siblings) and writes a text only when the number differs.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.step5.cpp#L248-L262"
if (m_Game.GetScore() != m_ShownScore)
{
	m_ShownScore = m_Game.GetScore();
	SetText(ScoreText, "Score: " + std::to_string(m_ShownScore));
}
if (m_Game.GetLevel() != m_ShownLevel)
{
	m_ShownLevel = m_Game.GetLevel();
	SetText(LevelText, "Level: " + std::to_string(m_ShownLevel));
}
if (m_Game.GetLines() != m_ShownLines)
{
	m_ShownLines = m_Game.GetLines();
	SetText(LinesText, "Lines: " + std::to_string(m_ShownLines));
}
```

1. **Lines 248–252:** when the score differs from the shown one, remember it and write the text.
2. **Lines 253–262:** the same for the level and the lines.

The helper `SetText` does nothing for an empty entity field, so a game without a HUD still runs.

The canvas scales with the screen. Its :term[reference resolution]{id=reference-resolution} is 1280 by 720: on a screen of 2560 by 1440 everything is twice as big, and the HUD keeps its place and its share of the screen. The score panel has a vertical layout: it stacks the three texts and fits itself to them. A `UIText` is centered unless its `Alignment` is `Left`, so the three texts set it.

:::::steps

1. Make the HUD canvas.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+**, choose **UI**, then `Canvas`, and rename it `HUD`. In **UI Canvas** set **Reference Resolution** to 1280 and 720. Enable the **2D** chip and the **Game UI** chip above the viewport, with `HUD` selected, to lay it out.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "HUD" } }
   { "command": "component.set", "parameters": { "entity": "<ID of HUD>", "component": "UICanvas", "values": { "ReferenceResolution": [1280, 720] } } }
   ```

   :::
   ::::

   **You should see:** a canvas entity `HUD` and a frame that shows the 1280 by 720 screen in the Scene view.

   **If you do not see it:** no frame. Select `HUD` and enable the two chips named above.

2. Make the score panel with a vertical layout.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD`, choose **Create Child ▸ UI**, then `Panel` and rename it `StatsPanel`. In **UI Rect** open **Anchors**, tick **Position** and choose `Top Left`. Type **Position** 48 and 56, set **Fit Content** to `Both`, and the **Pivot** to 0 and 0. Add a `Vertical Layout` with **Padding** 22, 14, 22, 14 and **Spacing** 0 and 4. Give the panel a dark, see-through `Color` such as 0.04, 0.05, 0.09 with alpha 0.72.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<ID of HUD>", "name": "StatsPanel", "anchor": "topLeft", "position": [48, 56] } }
   { "command": "component.set", "parameters": { "entity": "<ID of StatsPanel>", "component": "UIRect", "values": { "Pivot": [0, 0], "FitContent": "Both" } } }
   { "command": "component.add", "parameters": { "entity": "<ID of StatsPanel>", "component": "UILayout", "values": { "Type": "Vertical", "Padding": [22, 14, 22, 14], "Spacing": [0, 4] } } }
   ```

   :::
   ::::

   **You should see:** a small dark panel at the top left of the frame.

   **If you do not see it:** the panel is not at the corner. Its `Pivot` is not 0 and 0: set it.

3. Add the three texts as children of the panel. They are named `ScoreText`, `LevelText` and `LinesText`, as the play-test of stage 7 searches for them.

   | Name | Text | Font size | Color |
   | --- | --- | --- | --- |
   | `ScoreText` | `Score: 0` | 36 | white |
   | `LevelText` | `Level: 1` | 30 | 0.85, 0.9, 1 |
   | `LinesText` | `Lines: 0` | 30 | 0.85, 0.9, 1 |

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `StatsPanel`, choose **Create Child ▸ UI ▸ Text** and rename it. Type its text, `FontSize` and `Color` from the table. Set `Alignment` to `Left` and **Fit Content** of its **UI Rect** to `Both`. Repeat for the others.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<ID of StatsPanel>", "name": "ScoreText", "text": "Score: 0" } }
   { "command": "component.set", "parameters": { "entity": "<ID of ScoreText>", "component": "UIText", "values": { "FontSize": 36, "Alignment": "Left" } } }
   { "command": "component.set", "parameters": { "entity": "<ID of ScoreText>", "component": "UIRect", "values": { "FitContent": "Both" } } }
   ```

   Repeat the three commands for `LevelText` and `LinesText` with their rows of the table.
   :::
   ::::

   **You should see:** three lines of text stacked in the panel, which grows to fit them.

   **If you do not see it:** the text is centered in a wide box. `Alignment` is still `Center`: set `Left`.

4. Add the controls text and the label of the next piece. The controls text is a UI text at the bottom left of the canvas. The label is a world text above the preview panel, named `NextLabel`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD`, choose **Create Child ▸ UI ▸ Text**, rename it `ControlsText` and anchor it at `Bottom Left` with **Position** 48 and -36. Set `FontSize` 18, `Alignment` `Left` and the three lines `Left/Right: move   Up/X, Z: rotate`, `Down: soft drop   Space: hard drop` and `P: pause   R: restart   Esc: quit`. Press **+**, choose **3D Text**, rename it `NextLabel`, set **Translation** 13.5, 18.6, 0, `Text` to `NEXT`, `FontSize` 1 and clear **Screen Space**.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<ID of HUD>", "name": "ControlsText", "text": "Left/Right: move   Up/X, Z: rotate\nDown: soft drop   Space: hard drop\nP: pause   R: restart   Esc: quit", "anchor": "bottomLeft", "position": [48, -36] } }
   { "command": "component.set", "parameters": { "entity": "<ID of ControlsText>", "component": "UIText", "values": { "FontSize": 18, "Alignment": "Left" } } }
   { "command": "entity.create", "parameters": { "name": "NextLabel", "components": { "Text": { "Text": "NEXT", "FontSize": 1, "ScreenSpace": false }, "Transform": { "Translation": [13.5, 18.6, 0] } } } }
   ```

   In the text, each `\n` starts a new line: the controls text has three lines.
   :::
   ::::

   **You should see:** the controls at the bottom left, and `NEXT` above the preview panel.

   **If you do not see it:** `NEXT` is not in the Game view. Its `Screen Space` is on: clear it, so that it stands in the world.

5. Copy `Scripts/TetrisBoard.cpp` of checkpoint 5's download, at the end of this section, over your `Scripts/TetrisBoard.cpp`. Build, and set the three entity fields of `Board`: `Score Text`, `Level Text` and `Lines Text`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**. Select `Board`. Drag `ScoreText` from the Hierarchy onto the row `Score Text`, and the same for the other two. Press **Ctrl+S**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "ScoreText", "value": "<ID of ScoreText>" } }
   ```

   Run `script.setField` for `LevelText` and `LinesText`.
   :::
   ::::

   **You should see:** three filled entity rows.

   **If you do not see it:** a row stays empty. You dragged an entity of another canvas: use the three texts under `StatsPanel`.

6. Play and score a point.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, click the Game view and press **Space** once.
   :::
   :::tab[With a command]
   Start paused, run one step, read the score, drop the piece and read it again.

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "play.step", "parameters": { "steps": 1 } }
   { "command": "component.get", "parameters": { "entity": "<ID of ScoreText>", "component": "UIText" } }
   { "command": "input.sequence", "parameters": { "steps": 3, "events": [ { "step": 0, "key": "Space", "action": "tap" } ] } }
   { "command": "component.get", "parameters": { "entity": "<ID of ScoreText>", "component": "UIText" } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** `Score: 0` at the start, and `Score: 36` after the hard drop: the piece fell 18 rows, two points each.

   **If you do not see it:** the text stays at `Score: 0`. The field `Score Text` is empty: fill it.

:::::

::checkpoint{stage=5}

::figure{id=hud-shown}

## Finish the game

A finished game has sound, a way to pause, an end and a way to start again. Stage 6 adds the four, and one piece of care for the editor: a :term[hot reload]{id=hot-reload} must not break the game.

### Pause, two ways

The board pauses with a flag. `P` flips `m_Paused`, and while it is true the board does not call `Play`: the rules stand still, but the scene runs on, and `Refresh` still draws the word `PAUSED`. The other way sets the **time scale** to 0: the engine's game time stops for every script, and each `OnUpdate` gets a `deltaTime` of 0. The flag stops one script's rules and leaves music, animations and physics running. The time scale stops them all, so that is the choice for a pause menu with buttons, which [Menus and screens](menus.md) builds.

### Hot reload

When you build while the game plays, the editor replaces the script's code. A script instance keeps its fields, and loses everything else, such as the game state in `m_Game`. The engine then calls `OnReload` instead of `OnCreate`. The cells are entities in the scene, so they survive the reload, and the script's list of them does not.

:::caution
If `OnReload` called `CreateCells`, every hot reload would add a second set of 204 cells on top of the first. The board finds the old cells again by name instead.
:::

The creation and the reload of the final script are the first excerpt: look at how the reload differs from the creation.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.cpp#L60-L82"
void OnCreate() override
{
	for (AssetHandle asset : { MaterialI, MaterialO, MaterialT, MaterialS, MaterialZ, MaterialJ, MaterialL, GhostMaterial, MoveSound,
		LockSound, ClearSound, GameOverSound })
	{
		if (asset)
			Assets::RequestLoad(asset);
	}
	if (!CellMesh)
		CellMesh = Assets::Find("Builtin/Cube");

	CreateCells();
	SetupInput();
	NewGame();
}

void OnReload() override
{
	// The game state lives in this instance, which a hot reload replaces: find the cells again and start over.
	FindCells();
	SetupInput();
	NewGame();
}
```

1. **Lines 62–67:** ask for all eight materials and four sounds at the start.
2. **Lines 71–73:** the creation makes the cells, the key repeats and a game, in this order.
3. **Lines 76–82:** the reload finds the old cells, creates the repeats again and starts over.

`OnUpdate` is the board's whole control flow: quit, restart, pause, play and refresh. Escape quits; `R` restarts at any time; `Enter` restarts only after game over. Each restart uses the next seed, so every game deals other pieces.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.cpp#L84-L104"
void OnUpdate(float deltaTime) override
{
	if (Input::IsKeyPressed(Key::Escape))
	{
		Game::Quit(0);
		return;
	}
	if (Input::IsKeyPressed(Key::R) || (m_Game.IsGameOver() && (Input::IsKeyPressed(Key::Enter) || Input::IsKeyPressed(Key::KPEnter))))
	{
		m_GamesPlayed++;
		NewGame();
	}
	else if (!m_Game.IsGameOver())
	{
		if (Input::IsKeyPressed(Key::P))
			m_Paused = !m_Paused;
		if (!m_Paused)
			Play(deltaTime);
	}
	Refresh();
}
```

1. **Lines 86–90:** **Escape** ends the game at once.
2. **Lines 91–95:** **R** always restarts, **Enter** only after the end, and each restart counts a game for the next seed.
3. **Lines 96–103:** **P** flips the flag, `Play` runs only when it is false, and the picture is brought up to date in every frame, also while paused.

`FindCells` walks the board's children, finds `Cells`, and checks that it holds 204 entities: 200 for the well and 4 for the preview. If not, it makes new cells.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.cpp#L249-L269"
void FindCells()
{
	m_Cells.clear();
	m_Preview.clear();
	for (Entity child : GetEntity().GetChildren())
	{
		if (child.GetName() != "Cells")
			continue;
		std::vector<Entity> cells = child.GetChildren();
		const size_t boardCount = static_cast<size_t>(Tetris::c_Width * Tetris::c_Height);
		if (cells.size() == boardCount + 4)
		{
			m_Cells.assign(cells.begin(), cells.begin() + static_cast<std::ptrdiff_t>(boardCount));
			m_Preview.assign(cells.begin() + static_cast<std::ptrdiff_t>(boardCount), cells.end());
		}
		break;
	}
	if (m_Cells.empty())
		CreateCells();
	ResetShownTypes();
}
```

1. **Lines 253–256:** search the board's children for the one named `Cells`.
2. **Lines 259–263:** it must hold 204 entities: the first 200 are the well and the last 4 the preview.
3. **Lines 266–268:** only when nothing was found does it make new cells; either way, every cell is written again.

The message is one text with two possible words, written only when it changes. A panel around it shows while there is a message.

```cpp src="book:tutorials/make/project-tetris/TetrisBoard.cpp#L341-L352"
std::string message;
if (m_Game.IsGameOver())
	message = "GAME OVER\nPress R or Enter to play again";
else if (m_Paused)
	message = "PAUSED\nPress P to continue";
if (message != m_ShownMessage)
{
	m_ShownMessage = message;
	SetText(MessageText, message);
	if (MessagePanel)
		MessagePanel.SetActive(!message.empty());
}
```

1. **Lines 342–345:** the message depends on the state: game over first, then pause, else empty.
2. **Lines 346–351:** only a changed message is written, and the panel shows exactly when there is one.

:::::steps

1. Import the four sounds.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser press **Import** and choose the four files `Move.wav`, `Lock.wav`, `Clear.wav` and `GameOver.wav` of the release's folder `Samples/Tetris/Assets/Sounds/`. Make the folder `Sounds` first, and open it.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "files": ["<release folder>/Samples/Tetris/Assets/Sounds/Move.wav", "<release folder>/Samples/Tetris/Assets/Sounds/Lock.wav", "<release folder>/Samples/Tetris/Assets/Sounds/Clear.wav", "<release folder>/Samples/Tetris/Assets/Sounds/GameOver.wav"], "directory": "Sounds" } }
   ```

   :::
   ::::

   **You should see:** four sounds in `Sounds`.

   **If you do not see it:** the import is still running. The status bar counts it: wait until it ends.

2. Make the message panel and its text.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD`, choose **Create Child ▸ UI**, then `Panel` and rename it `MessagePanel`. In its **UI Rect** set **Anchor Min** and **Anchor Max** to 0.5, 0.42 and **Fit Content** to `Both`. Add a `Vertical Layout` with `ChildAlignment` `MiddleCenter` and **Padding** 44, 26, 44, 26. Add a `Text` child `MessageText` with an empty text, `FontSize` 44, `Alignment` `Center`, a yellow `Color` of 1, 0.9, 0.3 and **Fit Content** `Both`. Clear **Active** of the panel.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<ID of HUD>", "name": "MessagePanel", "anchor": "middleCenter" } }
   { "command": "component.set", "parameters": { "entity": "<ID of MessagePanel>", "component": "UIRect", "values": { "AnchorMin": [0.5, 0.42], "AnchorMax": [0.5, 0.42], "FitContent": "Both" } } }
   { "command": "component.add", "parameters": { "entity": "<ID of MessagePanel>", "component": "UILayout", "values": { "Type": "Vertical", "ChildAlignment": "MiddleCenter", "Padding": [44, 26, 44, 26] } } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<ID of MessagePanel>", "name": "MessageText", "text": "" } }
   { "command": "component.set", "parameters": { "entity": "<ID of MessageText>", "component": "UIText", "values": { "FontSize": 44, "Alignment": "Center", "Color": [1, 0.9, 0.3, 1] } } }
   { "command": "component.set", "parameters": { "entity": "<ID of MessageText>", "component": "UIRect", "values": { "FitContent": "Both" } } }
   { "command": "entity.setActive", "parameters": { "entity": "<ID of MessagePanel>", "active": false } }
   ```

   The anchor `middleCenter` puts the panel's pivot in its middle, and the next command moves both anchors to 42 % of the screen's height.
   :::
   ::::

   **You should see:** a hidden panel with its text under `HUD`.

   **If you do not see it:** the panel shows in the Game view. It is active: clear **Active**; the script shows it only when there is a message.

3. Copy `Scripts/TetrisBoard.cpp` of checkpoint 6's download, at the end of this section, over your `Scripts/TetrisBoard.cpp`: it is the final version. Build, and fill the new fields: `Message Text`, `Message Panel` and the four sounds.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**. Select `Board`, drag `MessageText` and `MessagePanel` onto their rows, and choose `Move`, `Lock`, `Clear` and `GameOver` in the four sound lists. Press **Ctrl+S**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "MoveSound", "value": "Sounds/Move.wav" } }
   ```

   Run `script.setField` for the other three sounds and the two entity fields.
   :::
   ::::

   **You should see:** the file now equals the sample's `TetrisBoard.cpp`, and the Inspector lists every field.

   **If you do not see it:** a field is missing. The file is still the stage 5 one: copy the final file.

4. Play, pause and lose.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, click the Game view and press **P**, then **P** again. Drop pieces with **Space** until the well is full. Press **R**.
   :::
   :::tab[With a command]
   Pause and continue with **P**, fill the well with fast rows as in stage 4, and restart with **R**. The game stays in play for the next step.

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "input.sequence", "parameters": { "steps": 3, "events": [ { "step": 0, "key": "P", "action": "tap" } ] } }
   { "command": "component.get", "parameters": { "entity": "<ID of MessageText>", "component": "UIText" } }
   { "command": "input.sequence", "parameters": { "steps": 3, "events": [ { "step": 0, "key": "P", "action": "tap" } ] } }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "MinInterval", "value": 0.01 } }
   { "command": "script.setField", "parameters": { "entity": "<ID of Board>", "class": "TetrisBoard", "field": "StartInterval", "value": 0.01 } }
   { "command": "play.step", "parameters": { "steps": 600 } }
   { "command": "component.get", "parameters": { "entity": "<ID of MessageText>", "component": "UIText" } }
   { "command": "input.sequence", "parameters": { "steps": 3, "events": [ { "step": 0, "key": "R", "action": "tap" } ] } }
   { "command": "component.get", "parameters": { "entity": "<ID of ScoreText>", "component": "UIText" } }
   ```

   1. **Lines 1–3:** start paused, tap **P** and read the message.
   2. **Lines 4–7:** continue with **P**, make every row take 0.01 s and run until the well is full.
   3. **Lines 8–10:** read the message, restart with **R** and read the score.

   A command cannot hear. `script.get` with the `entity` of `Board` and the `class` `TetrisBoard` shows that the four sound fields hold their sounds; the sounds themselves need your ears in the editor.
   :::
   ::::

   **You should see:** a short sound at each move, lock and clear. The panel `PAUSED / Press P to continue` while paused; `GAME OVER / Press R or Enter to play again` at the end; after **R** the panel closes and the score is 0. In the text of `MessageText` a line break stands where this page writes a slash.

   **If you do not see it:** no sound. A sound field is empty, or the volume of your system is off.

5. Check the hot reload. While the game plays, change a number in `Scripts/TetrisBoard.cpp`, such as the `0.92f` of `CellScale` to `0.9f`, and press **Ctrl+B**. Then set the number back to `0.92f` and build again, so that your file stays the sample's.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, edit the file in your code editor, switch to the editor and press **Ctrl+B**. Look at `Board` in the Hierarchy and open `Cells`. Stop, set the number back and press **Ctrl+B** again.
   :::
   :::tab[With a command]
   Edit the file in a text editor first: no command writes code.

   ```json
   { "command": "script.build" }
   { "command": "entity.find", "parameters": { "name": "Cells" } }
   { "command": "entity.get", "parameters": { "entity": "<ID of Cells>" } }
   { "command": "play.stop" }
   { "command": "script.build" }
   ```

   `entity.find` lists every entity named `Cells`, and `entity.get` lists its children. Set the number back before the last command.
   :::
   ::::

   **You should see:** the game restarts, and `Board` still has a single child `Cells` with 204 children.

   **If you do not see it:** two `Cells` entities. Your `OnReload` makes new cells: it must call `FindCells`.

:::::

::checkpoint{stage=6}

::figure{id=game-over}

## Prove it with a play-test

A game you play by hand is tested only while you look. A **play-test** is a command script that plays the game and checks what it shows, as [Testing a game with commands](automated-playtests.md) taught. You write one for Tetris and give it an exact score.

The numbers come from the rules. With seed 60 the first piece is J and the next is I, so the same keys always play the same game. The script slows gravity to 100 s per row with `script.setField`, so no piece falls, and sets `LinesPerLevel` to 1, so one cleared row raises the level. Then `input.sequence` plays 26 :term[fixed steps]{id=fixed-step} with 13 taps. The result is one row, a score of 209 and level 2: 100 points for the row at level 1, and 109 points for the drops.

The file has 36 lines. The first part finds the entities, sets the two fields and checks the HUD's place at two screen sizes.

```json src="book:tutorials/make/project-tetris/Playtest.json#L1-L12"
[
	{ "command": "entity.find", "parameters": { "name": "Board" }, "bind": { "board": "/entities/0" } },
	{ "command": "entity.find", "parameters": { "name": "ScoreText" }, "bind": { "score": "/entities/0" } },
	{ "command": "entity.find", "parameters": { "name": "LinesText" }, "bind": { "lines": "/entities/0" } },
	{ "command": "entity.find", "parameters": { "name": "LevelText" }, "bind": { "level": "/entities/0" } },
	{ "command": "entity.find", "parameters": { "name": "MessageText" }, "bind": { "message": "/entities/0" } },
	{ "command": "script.setField", "parameters": { "entity": { "$ref": "board" }, "class": "TetrisBoard", "field": "LinesPerLevel", "value": 1 } },
	{ "command": "script.setField", "parameters": { "entity": { "$ref": "board" }, "class": "TetrisBoard", "field": "StartInterval", "value": 100 } },
	{ "command": "ui.layout", "parameters": { "entity": { "$ref": "score" }, "screen": [1280, 720] },
		"expect": { "/elements/0/rect": { "equals": [70, 70, 131.677734375, 42.1875] } } },
	{ "command": "ui.layout", "parameters": { "entity": { "$ref": "score" }, "screen": [2560, 1440] },
		"expect": { "/elements/0/rect": { "equals": [140, 140, 263.35546875, 84.375] } } },
```

1. **Lines 2–6:** find the five entities by name; `bind` keeps the first identifier of each answer.
2. **Lines 7–8:** two fields set before play: one row per level, and 100 s per row of gravity.
3. **Lines 9–12:** the score text's rectangle at two screen sizes; the larger one is exactly twice the smaller.

The script finds its entities by name with `entity.find`, and keeps each answer with `bind`: the pointer `/entities/0` is the first entity found, and a later step writes `{ "$ref": "board" }` where its ID belongs. The sample's own script writes the IDs of its saved scene; your IDs differ, so the script uses the names you chose.

The second part starts the game, plays the sequence and expects the three texts. The rectangles of lines 9 to 12 hold for the HUD of stage 5 as written there: the panel's position of 48 and 56 plus its padding of 22 and 14 gives 70 and 70. If you chose other sizes, run the layout once and write the rectangle you read.

```json src="book:tutorials/make/project-tetris/Playtest.json#L13-L22"
{ "command": "play.start", "expect": { "/state": { "equals": "Play" } } },
{ "command": "component.get", "parameters": { "entity": { "$ref": "score" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 0" } } },
{ "command": "input.sequence", "parameters": { "steps": 26, "events": [
	{ "step": 0, "key": "Left", "action": "tap" }, { "step": 2, "key": "Left", "action": "tap" }, { "step": 4, "key": "Left", "action": "tap" }, { "step": 6, "key": "Space", "action": "tap" },
	{ "step": 8, "key": "Up", "action": "tap" }, { "step": 10, "key": "Z", "action": "tap" }, { "step": 12, "key": "Down", "action": "tap" }, { "step": 14, "key": "Space", "action": "tap" },
	{ "step": 16, "key": "Right", "action": "tap" }, { "step": 18, "key": "Right", "action": "tap" }, { "step": 20, "key": "Right", "action": "tap" }, { "step": 22, "key": "Right", "action": "tap" }, { "step": 24, "key": "Space", "action": "tap" }
] }, "expect": { "/stepsRun": { "equals": 26 } } },
{ "command": "component.get", "parameters": { "entity": { "$ref": "lines" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Lines: 1" } } },
{ "command": "component.get", "parameters": { "entity": { "$ref": "score" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 209" } } },
{ "command": "component.get", "parameters": { "entity": { "$ref": "level" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Level: 2" } } },
```

1. **Lines 13–14:** start the game and expect the first score.
2. **Lines 15–19:** 13 taps over 26 steps; each tap lasts one step.
3. **Lines 20–22:** the three texts after the play.

The third part waits for the end. Gravity becomes fast, `until` repeats the check after each fixed step until the message reads game over, and it fails after 3000 steps or 60 s. Then the script restarts with **R**, expects the fresh game, and cleans up.

```json src="book:tutorials/make/project-tetris/Playtest.json#L23-L36"
	{ "command": "script.setField", "parameters": { "entity": { "$ref": "board" }, "class": "TetrisBoard", "field": "MinInterval", "value": 0.01 } },
	{ "command": "script.setField", "parameters": { "entity": { "$ref": "board" }, "class": "TetrisBoard", "field": "StartInterval", "value": 0.01 } },
	{ "command": "component.get", "parameters": { "entity": { "$ref": "message" }, "component": "UIText" },
		"expect": { "/values/Text": { "equals": "GAME OVER\nPress R or Enter to play again" } }, "until": { "steps": 3000, "seconds": 60 } },
	{ "command": "script.setField", "parameters": { "entity": { "$ref": "board" }, "class": "TetrisBoard", "field": "StartInterval", "value": 100 } },
	{ "command": "input.key", "parameters": { "key": "R" } },
	{ "command": "component.get", "parameters": { "entity": { "$ref": "message" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "" } } },
	{ "command": "component.get", "parameters": { "entity": { "$ref": "score" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 0" } } },
	{ "command": "component.get", "parameters": { "entity": { "$ref": "lines" }, "component": "UIText" }, "expect": { "/values/Text": { "equals": "Lines: 0" } } },
	{ "command": "play.stop", "expect": { "/state": { "equals": "Edit" } } },
	{ "command": "edit.undo" },
	{ "command": "edit.undo" },
	{ "command": "scene.info", "expect": { "/modified": { "equals": false } } }
]
```

1. **Lines 23–26:** fast gravity, then wait with `until` for the message.
2. **Lines 27–31:** slow gravity again, press **R** and expect a fresh game.
3. **Lines 32–35:** stop, undo both edits and check that the scene has no change you did not save.

The two `script.setField` calls of lines 7 and 8 run before play, and in edit mode they change the saved scene: each change is one undo step. The last four lines undo both and expect `/modified` to be false, so that you do not save a game whose rows take 100 s. The two later calls run while the game plays, and `play.stop` throws their changes away.

:::::steps

1. Write the file `Playtest.json` in the project's folder with the lines of the excerpts, 36 lines in all, or copy `Playtest.json` of checkpoint 7's download, at the end of this section.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step edits a file in a text editor: save the file next to `Tetris.stproj`.
   :::
   :::tab[With a command]
   This step has no menu or button: save the file with a text editor.
   :::
   ::::

   **You should see:** a file of 36 lines.

   **If you do not see it:** some editors add `.txt`. Rename the file so that its name ends in `.json`.

2. Close the editor, then run the script from a terminal that stands in the project's folder.

   ::::tabs{sync=os}
   :::tab[Windows]
   Pipe the editor into `Write-Output` so that PowerShell waits for it, then print the exit code.

   ```powershell
   & "C:\Strata\StrataEditor.exe" --project . --commands Playtest.json --quit-after-commands --no-gpu | Write-Output
   $LASTEXITCODE
   ```

   Replace the path with the one of your release folder.
   :::
   :::tab[Linux]

   ```sh
   /opt/strata/StrataEditor --project . --commands Playtest.json --quit-after-commands --no-gpu
   echo $?
   ```

   The first line runs the editor on the project; the second prints its exit code.
   :::
   :::tab[macOS]

   ```sh
   /Applications/Strata/StrataEditor --project . --commands Playtest.json --quit-after-commands --no-gpu
   echo $?
   ```

   :::
   ::::

   The editor builds the scripts, plays, checks and quits. Exit code 0 means every expectation held; 1 means a step failed.

   **You should see:** the log lines `Tetris: cleared 1 line; score 209, lines 1, level 2` and one that starts `Tetris: game over after`, a line that says `Command script finished`, and exit code 0.

   **If you do not see it:** `expected '/values/Text' to be "Score: 209"` names the two values. A different score means a key of the sequence moved, or the rules differ from the page. The log line `script.setField failed: No script module is loaded` means the project's scripts were never built, as in a fresh download: the two fields are set before play builds them. Build once with **Ctrl+B** in the editor, close it and run the script again.

3. Break the scoring on purpose. In `Scripts/TetrisGame.cpp` change the first score in `c_LineScores`, the 100, to 101, and run the script again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the file in a text editor and run the same command as in step 2.
   :::
   :::tab[With a command]
   This step has no menu or button: edit the file and run the terminal command again.
   :::
   ::::

   **You should see:** `expected '/values/Text' to be "Score: 209", but it is "Score: 210"`, then exit code 1. The later steps still ran.

   **If you do not see it:** exit code 0. The edit went into another file, or the editor did not build again: read the name of the file you saved. The editor builds before play when a script file is newer than the built scripts. Some drives, such as many memory sticks, keep file times in steps of two seconds. On such a drive an edit within two seconds of the last build looks no newer: wait a moment, save the file again and run the command again.

4. Restore the 100 and run the script a third time.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the file and run the command again.
   :::
   :::tab[With a command]
   This step has no menu or button: edit the file and run the command again.
   :::
   ::::

   **You should see:** exit code 0 again.

   **If you do not see it:** the score is still 210. The 101 is still in the file, or the editor did not build again, as in step 3: save the file again after a moment.

:::::

The terminal prints the play-test's log lines, and the editor's **Console** holds the same lines when the commands run in an editor window. The picture shows that Console after such a run; only the terminal reports the exit code.

::checkpoint{stage=7}

::figure{id=playtest-console}

## Ship it

The last stage gives the game its name and icon, and exports it. The page [Exporting and shipping](export.md) teaches the steps. This stage adds one thing: the sample's `Icon.png` becomes the game's icon.

:::::steps

1. Import the icon and set the game's title and version.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import `Icon.png` of the release's folder `Samples/Tetris/Assets/` into the project. Choose **File ▸ Project Settings...** and open the page **Game**. Set **Title** to `Tetris` and **Version** to `1.0.0`, and choose `Icon.png` in **Icon**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/Tetris/Assets/Icon.png" } }
   { "command": "project.setGameInfo", "parameters": { "title": "Tetris", "version": "1.0.0", "icon": "Icon.png" } }
   ```

   :::
   ::::

   **You should see:** the three values on the page **Game**.

   **If you do not see it:** the icon is not listed. The import is still running: wait for the status bar.

2. Build the scripts and export.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**. Choose **File ▸ Export Game...**, pick a folder outside the project and press **Export**. Press **Open Folder** when the bar reads **Done**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "project.export", "parameters": { "directory": "<a folder outside the project>" } }
   ```

   :::
   ::::

   **You should see:** a folder with `Tetris`, `Tetris.stgame`, a pack file and the :term[script module]{id=script-module}.

   **If you do not see it:** the export refuses. The folder lies inside the project, or no script module is loaded: the message names which.

3. Run the exported game.

   ::::tabs{sync=os}
   :::tab[Windows]
   Run the game for ten seconds with a screenshot, from PowerShell in the export folder.

   ```powershell
   .\Tetris.exe --windowed --seconds 10 --screenshot shot.png | Write-Output
   ```

   The pipe makes PowerShell wait for the program.
   :::
   :::tab[Linux]

   ```sh
   ./Tetris --windowed --seconds 10 --screenshot shot.png
   ```

   The same run, in a terminal.
   :::
   :::tab[macOS]

   ```sh
   ./Tetris --windowed --seconds 10 --screenshot shot.png
   ```

   :::
   ::::

   Play it with the keys of the page. Escape quits, since the board calls `Game::Quit`.

   **You should see:** a window titled `Tetris`, the well, the HUD and a falling piece, and a file `shot.png`.

   **If you do not see it:** the pieces are plain white. A material is missing from the pack: read the log of the game, as the export page shows.

:::::

You own a finished, exported Tetris and a play-test that fails when its rules break. Open your copy of the sample beside the project and compare the two `TetrisBoard.cpp` files: they are the same file. Next, make the game your own with the exercises, or plan another game with [Designing a game](designing-a-game.md).

::checkpoint{stage=8}

::figure{id=exported}

## Summary

- The rules of Tetris live in a plain C++ class that calls nothing of the engine; the board script feeds it keys and time and draws what it answers.
- The 200 cells and 4 preview cells are created once, and `Refresh` shows, hides and colors again only the cells whose piece changed.
- `KeyRepeat` gives held keys a delay and an interval, and gravity adds `deltaTime` to a running total, so the game falls at the same speed at any frame rate.
- The HUD texts are written only when their numbers change, and `OnReload` finds the old cells again, so a hot reload adds no second set.
- A command script with a seed, slowed gravity and `input.sequence` expects an exact score and fails when the rules break; the game exports with its title and icon.

## Check yourself

1. The rules class has no engine call. Name one thing the board script does for it, and one thing it does with its answer.

   :::answer{tests="rules-class"}
   The script feeds it keys as moves, and time as gravity steps. It reads the cells, the piece, the ghost and the score back, and shows them as cube entities and texts.
   :::

2. A player holds **Right** for a second at 60 frames per second. How many times does the piece move if `RepeatDelay` is 0.17 s and `RepeatInterval` is 0.05 s?

   :::answer{tests="input-gravity"}
   Once at the press, and once more at 0.17 s. The rest of the second is 0.83 s, which holds 16 intervals of 0.05 s, so the piece moves 18 times, if the wall does not stop it.
   :::

3. `OnReload` calls `FindCells`. What would a hot reload do if it called `CreateCells` instead?

   :::answer{tests="hud-reload"}
   A call of `CreateCells` would add a second set of 204 cells under a second `Cells` entity, because the first set stays in the scene. The game would draw twice as many cubes, and the cells of the first set would stay hidden.
   :::

4. Why does the board keep the cells hidden and show them again, and not destroy them?

   :::answer{tests="draw-once"}
   No frame creates or destroys an entity, so nothing can leak, and a quiet frame does 200 comparisons and no more. The cost is 204 entities that exist all the time.
   :::

5. Your play-test fails with `expected '/values/Text' to be "Level: 2", but it is "Level: 1"`. Which field did you forget, and what does the exit code say?

   :::answer{tests="playtest-export"}
   `LinesPerLevel` is still 10, so one line leaves the level at 1: the level is the start level plus the lines divided by `LinesPerLevel`. The exit code is 1.
   :::

## Exercises

1. **Basic.** Keep the best score between runs. Write it with `Game::WriteSaveFile` when a game ends, read it with `Game::ReadSaveText` in `NewGame`, and show it as a fourth text, `BestText`, in the score panel.

   :::answer[Worked solution]{tests="hud-reload" solution="tutorials/make/project-tetris/exercise-1.tutorial.json"}
   `ReadSaveText` answers nothing when there is no file yet, so the best score starts at 0. The solution file `exercise-1/TetrisBoard.cpp` writes the file only when the score beats the best, and `Refresh` writes the text only when the best changes. The command file adds the text and sets the field.
   :::

2. **Medium.** Add a hold piece: one key swaps the falling piece with the held one, once per piece. Which parts change, and how does the play-test of stage 7 expect it?

   :::answer{tests="rules-class"}
   The rules class gets the held type and a flag that a hold was used since the last lock. It also gets a `Hold` move that returns false when the flag is set or the swapped piece does not fit. The board gets four more preview cells and a key. The play-test taps the key at a known step. It expects the preview's pieces, or the score that follows from the changed play.
   :::

3. **Hard.** Play the pieces with a gamepad. Which engine features replace the key reads, and why can `KeyRepeat` not repeat a gamepad button?

   :::answer{tests="input-gravity"}
   Define the moves as input actions of a `Gameplay` map with key and gamepad bindings, and read them with `Input::IsActionDown` and `Input::IsActionPressed`, as [Input](input.md) teaches. `KeyRepeat` reads keys only, so you write a repeat for actions the same way: a held time, a delay and an interval.
   :::

## Where it lives in Strata

The sample is the folder `Samples/Tetris/`: its scripts are `Samples/Tetris/Scripts/TetrisGame.h`, `Samples/Tetris/Scripts/TetrisGame.cpp` and `Samples/Tetris/Scripts/TetrisBoard.cpp`, and its scene is `Samples/Tetris/Assets/Scenes/Main.stscene`. The SDK calls used are in `StrataScriptCore/Include/StrataScript/`: `KeyRepeat` and `Random` in `Gameplay.h`, and the save-file calls in `Game.h`. The engine's own test of the sample is `StrataTests/Editor/TetrisCommands.json.in`.

## Further reading

- Tetris Wiki, "Random Generator": the 7-bag and the history of piece choice (beginner).
- Robert Nystrom, Game Programming Patterns, chapter "Game Loop": why a game counts time and not frames (intermediate).

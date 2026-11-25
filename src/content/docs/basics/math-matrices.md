---
id: basics/math-matrices
title: "Matrices and transforms: TRS, hierarchies, spaces and conventions"
description: "How a grid of numbers moves, turns and resizes things, how a child follows its parent, and which axes and units Strata uses."
kind: primer
size: L
tracks: [B, E]
needs: [basics/math-vectors, basics/numbers]
time: 90
learn:
  - id: matrix-columns
    text: compute a matrix times a vector and read a matrix's columns as the places the axes go
  - id: matrix-product
    text: compute a matrix product and predict how its order changes the result
  - id: trs-w
    text: build a 4×4 transform from translation, rotation and scale and apply it to a position and a direction
  - id: hierarchy-inverse
    text: compute a child's world and local transforms from its parent's world matrix and the inverse
  - id: conventions
    text: name Strata's axes, handedness, units and matrix order and recognize another convention
status: final
---

::::test-out

1. The matrix with the rows (0, -1) and (1, 0) multiplies the vector (2, 1). What comes out, and what did the matrix do
   to the vector?

   :::answer{tests="matrix-columns"}
   The first row gives 0 × 2 + (-1) × 1 = -1 and the second gives 1 × 2 + 0 × 1 = 2, so the result is (-1, 2). The
   matrix turned the arrow by a quarter turn, counterclockwise.
   :::

2. A point at (1, 0) turns by a quarter turn counterclockwise about the origin and then moves 3 along x. Where does it
   end? Where does it end if it moves first and turns second?

   :::answer{tests="matrix-product"}
   Turned first, it goes to (0, 1) and then to (3, 1). Moved first, it goes to (4, 0), and the turn takes it to
   (0, 4). The order changes the result.
   :::

3. A 4×4 matrix moves everything by (5, 0, 0) and does nothing else. What does it do to the position (1, 2, 3), and
   what to the direction (1, 2, 3)?

   :::answer{tests="trs-w"}
   The position becomes (6, 2, 3), because its fourth number is 1. The direction stays (1, 2, 3), because its fourth
   number is 0 and a direction has no place to move.
   :::

4. A child sits at the local position (2, 0, 0). Its parent stands at the world position (0, 0, 10), and the parent's x
   arrow points along world -z. Where is the child in the world, and which matrix turns a world position back into the
   child's local one?

   :::answer{tests="hierarchy-inverse"}
   Two steps along the parent's x arrow go two steps along -z: (0, 0, -2). Adding the parent's position gives
   (0, 0, 8). The inverse of the parent's world matrix turns a world position back into a local one.
   :::

5. In Strata, which axis points up, which way does a camera look when nothing turns it, and which axis is the cross
   product of the x arrow and the y arrow?

   :::answer{tests="conventions"}
   +Y is up, a camera looks along -Z, and the cross product of x and y is +Z, because the axes are right-handed.
   :::

::::

## Why you will need this

Every thing in a game scene has a place, a direction it faces and a size. A coin spins, a ring of coins hangs around
a spinning post, and the camera follows a ball. Each of these is one small table of numbers, and the engine multiplies
tables together hundreds of thousands of times per frame.

[The scene graph](../world/scene-graph.md) uses the tables to keep a child with its parent.
[Coordinates](../gpu/coordinates.md) follows a point from the scene to a pixel, one table after another.
[Skeletons](../animation/skeletons.md) move the joints of a character by the same multiplication.

Each idea goes from a picture and small numbers by hand to the formula and then to C++ with `glm`, the library of
mathematics that Strata and its scripts use. You need the vectors and the dot product of
[Vectors](../basics/math-vectors.md).

## A matrix is a grid that changes a vector

Suppose you want to turn a drawing by a quarter turn, or stretch it to twice its width. Each rule is simple to say,
but a game applies one to thousands of points per frame, and it applies many rules in a row. Mathematics writes such
a rule in one standard form: a grid of numbers.

A **matrix** is a rectangular grid of numbers in rows, which run across, and columns, which run down. A 2×2 matrix
such as $\begin{bmatrix} 2 & 0 \\ 0 & 3 \end{bmatrix}$ has two rows and two columns. You apply it to a point by
multiplying the matrix by the point's coordinates.

A point has two coordinates in the plane, one along each axis. An **axis** is a line through the origin along which
one coordinate is measured: the x axis runs to the right and the y axis up.

Each number of the result is the dot product of one row of the matrix with the vector. The first row makes the first
number and the second row makes the second.

$$
\begin{bmatrix} 2 & 0 \\ 0 & 3 \end{bmatrix}
\begin{bmatrix} 1 \\ 1 \end{bmatrix}
=
\begin{bmatrix} 2 \cdot 1 + 0 \cdot 1 \\ 0 \cdot 1 + 3 \cdot 1 \end{bmatrix}
=
\begin{bmatrix} 2 \\ 3 \end{bmatrix}
$$

The dot $\cdot$ reads "times". The point (1, 1) lands at (2, 3): this matrix stretches x by 2 and y by 3. A rule that
moves every point of a space in this way is a **transform**, and a matrix is one way to write a transform down.

:::example[A matrix times a vector by hand]
Take the matrix with the rows (1, 3) and (2, 4), and the point (1, 1). The first row gives 1 × 1 + 3 × 1 = 4. The
second gives 2 × 1 + 4 × 1 = 6. The point lands at (4, 6).
:::

Try it: the matrix has the rows (0, 1) and (1, 0). Where does it send the point (5, 2)?

:::answer
The first row gives 0 × 5 + 1 × 2 = 2 and the second gives 1 × 5 + 0 × 2 = 5. The point lands at (2, 5): the matrix
swaps x and y.
:::

The same example in C++ shows one trap. `glm` names the matrix type `glm::mat2`, and its constructor reads the numbers
column by column, not row by row.

:::question[Why do the programs call functions written with `glm::` in front?]
`glm::` names the library that holds the function, and the line `m[0]` reads one column of a matrix.
[Programming 3](../basics/programming-3.md) explains both; here, read them as "use the library" and "read part of it".
:::

The program builds the matrix with the rows (1, 3) and (2, 4) by listing its columns, prints the columns, and
multiplies the matrix by (1, 1). It ends with a matrix written `glm::mat2(1.0f)`: look at what that one does.

```cpp sketch="basics-math-matrices-columns.cpp"
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	// The constructor reads its numbers column by column: the first column is (1, 2), the second (3, 4).
	const glm::mat2 m(1.0f, 2.0f, 3.0f, 4.0f);
	std::printf("m[0] = (%g, %g)\n", m[0].x, m[0].y);
	std::printf("m[1] = (%g, %g)\n", m[1].x, m[1].y);
	std::printf("m[1][0] = %g\n", m[1][0]);
	const glm::vec2 result = m * glm::vec2(1.0f, 1.0f);
	std::printf("m * (1, 1) = (%g, %g)\n", result.x, result.y);

	// The identity matrix has the axes themselves as its columns, so it changes nothing.
	const glm::vec2 same = glm::mat2(1.0f) * glm::vec2(3.0f, 1.0f);
	std::printf("identity * (3, 1) = (%g, %g)\n", same.x, same.y);
}
```

```text output-of="basics-math-matrices-columns.cpp"
m[0] = (1, 2)
m[1] = (3, 4)
m[1][0] = 3
m * (1, 1) = (4, 6)
identity * (3, 1) = (3, 1)
```

1. **Line 7:** the first two numbers are the first column, so the grid on paper has the rows (1, 3) and (2, 4).
2. **Lines 8–9:** `m[0]` is column 0 and `m[1]` is column 1. A column is one `glm::vec2`.
3. **Line 10:** `m[1][0]` is column 1, row 0: the first index picks the column, the second the row.
4. **Line 11:** `*` between a matrix and a vector does the rows-times-vector rule: (4, 6), as by hand.
5. **Line 15:** the matrix `glm::mat2(1.0f)` changes nothing, as the last output line shows. The next section names it.

In a script of the playground, `Log::Info` writes numbers, text and vectors but not a matrix: a line that passes it a
matrix does not compile. Write a matrix column by column instead.

```cpp pseudocode
glm::mat4 m(1.0f);
Log::Info(m[0], " ", m[1], " ", m[2], " ", m[3]);
```

Each `m[i]` is a `glm::vec4`, so the **Console** shows four vectors, each written as (x, y, z, w): the four columns of the identity.

## The columns of a matrix are where the axes go

How do you find the matrix for a change you have in mind? Start from two special points. An arrow of length 1 along an
axis is a **basis vector**: (1, 0) along x and (0, 1) along y in the plane. Multiply a matrix by (1, 0) and the dot
products pick the first number of each row: the matrix's first column. Multiply it by (0, 1) and you get the second
column.

So the columns of a matrix are the places the two axis arrows go. Every other point is a mix of them, because
(x, y) is x steps along the first arrow and y steps along the second. The matrix sends it to x steps along the first
column and y steps along the second. Knowing where the axes go tells you where everything goes.

:::example[Reading a matrix off its picture]
Look at the figure. The x arrow goes to (0, 2) and the y arrow goes to (-1, 0), so the matrix has the columns (0, 2)
and (-1, 0). The point (1, 1) lands at 1 × (0, 2) + 1 × (-1, 0) = (-1, 2).
:::

::figure{id=axes-moved}

Try it: write the matrix that turns every point by a half turn, so that (1, 0) goes to (-1, 0) and (0, 1) goes to
(0, -1). Where does it send (3, 1)?

:::answer
The columns are (-1, 0) and (0, -1). The point (3, 1) goes to 3 × (-1, 0) + 1 × (0, -1) = (-3, -1).
:::

Three transforms are worth knowing by their columns. The first keeps everything.

The **identity matrix** keeps the axes where they are: its columns are (1, 0) and (0, 1), a 1 down the diagonal and 0
elsewhere, and it changes nothing.

A **scale** stretches each axis by a factor. Its columns are (2, 0) and (0, 3) for the factors 2 and 3, the matrix of
the first example.

A **rotation** turns the whole plane about the origin by an angle. Its columns come from the unit circle of
[Vectors](../basics/math-vectors.md): turn by the angle $\theta$, counterclockwise. The x arrow (1, 0) lands on the
unit circle at $(\cos\theta, \sin\theta)$, and the y arrow, a quarter turn ahead, lands at $(-\sin\theta, \cos\theta)$.

$$
\begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}
$$

$\theta$ is the angle in :term[radians]{id=radian}, and $\cos$ and $\sin$ are :term[cosine]{id=cosine} and :term[sine]{id=sine}. Check the limits. At $\theta = 0$ the
columns are (1, 0) and (0, 1): the identity. At a quarter turn, $\theta = \pi / 2$, the columns are (0, 1) and (-1, 0),
and the point (3, 1) goes to 3 × (0, 1) + 1 × (-1, 0) = (-1, 3).

In 3D a matrix has three rows and three columns, which are the three axis arrows. The identity has a 1 down the
diagonal, and a scale has the three factors on it. A rotation about the z axis keeps the z arrow in place and turns the
other two, so it is the 2×2 rotation with a 1 in the corner:

$$
\begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

A rotation about the y axis keeps the y arrow, sends the x arrow to $(\cos\theta, 0, -\sin\theta)$ and the z arrow to
$(\sin\theta, 0, \cos\theta)$. For a quarter turn, the x arrow goes to (0, 0, -1): remember that, because the examples
below use it. A 3×3 grid also changes one set of three numbers into another elsewhere in the book, such as a color
between color spaces ([Color](../basics/color.md)) or a body's resistance to turning ([Dynamics](../physics/dynamics.md)).

## Multiplying matrices combines transforms

A game applies several transforms to the same points: stretch a coin, turn it, then place it. You can apply them one
by one, but it is cheaper to combine them into one matrix and apply that. The combination is the **matrix
multiplication** of the grids.

To multiply $A$ by $B$, find each number of the result as the dot product of a row of $A$ with a column of $B$. The
number in row $i$ and column $j$ comes from row $i$ of $A$ and column $j$ of $B$. The product $AB$ does what $B$ does
first and what $A$ does second, because $(AB)v = A(Bv)$ for any vector $v$. Read it from right to left: "A after B".

:::example[Turn and stretch in two orders]
Let $A$ be the quarter turn, with the rows (0, -1) and (1, 0), and let $B$ be the stretch of x by 2, with the rows
(2, 0) and (0, 1).

$$
AB =
\begin{bmatrix} 0 \cdot 2 + (-1) \cdot 0 & 0 \cdot 0 + (-1) \cdot 1 \\ 1 \cdot 2 + 0 \cdot 0 & 1 \cdot 0 + 0 \cdot 1 \end{bmatrix}
=
\begin{bmatrix} 0 & -1 \\ 2 & 0 \end{bmatrix}
$$

$$
BA =
\begin{bmatrix} 0 & -2 \\ 1 & 0 \end{bmatrix}
$$

$A$ and $B$ are the two matrices, $i$ and $j$ number rows and columns, and $v$ is any vector. $AB$ and $BA$ are
different. Check with the point (1, 0). $AB$ sends it to (0, 2): the stretch makes (2, 0) and the turn makes (0, 2).
$BA$ sends it to (0, 1): the turn makes (0, 1) and the stretch leaves it, because it has no x part.
:::

Try it: swap the roles. $A$ is the stretch of x by 3, with the rows (3, 0) and (0, 1), and $B$ is the quarter turn.
Compute $AB$ and $BA$, and say where each sends (1, 0).

:::answer
$AB$ has the rows (0, -3) and (1, 0) and sends (1, 0) to (0, 1): the turn comes first and the stretch leaves it. $BA$ has
the rows (0, -1) and (3, 0) and sends (1, 0) to (0, 3): the stretch comes first.
:::

Three facts follow, and the rest of the page uses all three. The order matters: $AB$ is not $BA$ in general. The grouping
does not matter: $(AB)C = A(BC)$, so a chain of ten transforms becomes one matrix that you compute once. And the
identity is neutral: multiplying by it on either side gives the same matrix back.

## Translation needs a fourth number

Scale and rotation keep the origin where it is: the point (0, 0) times any 2×2 matrix is still (0, 0). A move, which a
game needs most of all, cannot be a 2×2 or a 3×3 matrix, because it must change the origin.

The way out is a fourth number, $w$. A position (x, y, z) becomes (x, y, z, 1), and a 4×4 matrix holds the move in its
last column. A **translation** moves every point by the same step $(t_x, t_y, t_z)$:

$$
\begin{bmatrix} 1 & 0 & 0 & t_x \\ 0 & 1 & 0 & t_y \\ 0 & 0 & 1 & t_z \\ 0 & 0 & 0 & 1 \end{bmatrix}
\begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix}
=
\begin{bmatrix} x + t_x \\ y + t_y \\ z + t_z \\ 1 \end{bmatrix}
$$

$x$, $y$ and $z$ are the coordinates of the point, and $t_x$, $t_y$ and $t_z$ are the steps along each axis, in the unit
of the scene. The first three columns still say where the three axis arrows go. The fourth column says where the
origin goes, and it is the translation.

A direction, such as "forward", has no place, so moving an object must not change it. A direction gets the
fourth number 0: the last column then multiplies 0 and adds nothing, and only the upper left 3×3 part acts on it. In
short, $w = 1$ for a position and $w = 0$ for a direction. A 3×3 change followed by a move is an **affine transform**, and
every 4×4 matrix of this page is one.

:::example[Turn, then move, against move, then turn]
Let $R$ be the quarter turn about the z axis and $T$ the move by (3, 0, 0). The product $TR$ turns first, because the
right matrix acts first, and then moves. Its last column is (3, 0, 0), the move untouched. The product $RT$ moves first
and then turns, so the turn also turns the move: its last column is (0, 3, 0).

$$
TR = \begin{bmatrix} 0 & -1 & 0 & 3 \\ 1 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}
\qquad
RT = \begin{bmatrix} 0 & -1 & 0 & 0 \\ 1 & 0 & 0 & 3 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}
$$

The point (1, 0, 0, 1) goes to the first column plus the last. For $TR$ that is (0, 1, 0) + (3, 0, 0) = (3, 1, 0). For
$RT$ it is (0, 1, 0) + (0, 3, 0) = (0, 4, 0).
:::

::figure{id=turn-then-move}

The next program builds $T$ and $R$ with `glm` and prints, for each order, the last column and where the point lands.
Compare the output with the two matrices above. The functions `glm::rotate` and `glm::translate` build the matrices,
and the angle goes in radians.

```cpp sketch="basics-math-matrices-order.cpp"
#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Rounds to three decimals; adding 0.0f turns a negative zero into a plain zero.
static glm::vec4 Tidy(const glm::vec4& v)
{
	return glm::round(v * 1000.0f) / 1000.0f + 0.0f;
}

static void Print(const std::string& label, const glm::mat4& m, const glm::vec4& point)
{
	const glm::vec4 c = Tidy(m[3]);
	const glm::vec4 end = Tidy(m * point);
	std::printf("%s: last column (%g, %g, %g), the point lands at (%g, %g, %g)\n", label.c_str(), c.x, c.y, c.z, end.x, end.y, end.z);
}

int main()
{
	const glm::mat4 turn = glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::mat4 move = glm::translate(glm::mat4(1.0f), glm::vec3(3.0f, 0.0f, 0.0f));
	const glm::vec4 point(1.0f, 0.0f, 0.0f, 1.0f);
	Print("turn, then move", move * turn, point);
	Print("move, then turn", turn * move, point);
}
```

```text output-of="basics-math-matrices-order.cpp"
turn, then move: last column (3, 0, 0), the point lands at (3, 1, 0)
move, then turn: last column (0, 3, 0), the point lands at (0, 4, 0)
```

1. **Lines 5–9:** `Tidy` rounds the numbers, because a turn by 90° in `float` leaves values near 0.0000001 where
   the paper has 0.
2. **Lines 20–21:** `turn` is the quarter turn about z and `move` the step along x, both as 4×4 matrices.
3. **Line 23:** `move * turn` turns first, as the right matrix acts first.
4. **Line 24:** `turn * move` moves first. Its last column is the move, turned.

Try it: $R$ is the half turn about z, which sends (1, 0, 0) to (-1, 0, 0), and $T$ is the move by (0, 2, 0). Where do
$TR$ and $RT$ send the point (1, 0, 0, 1)?

:::answer
$TR$ turns first, to (-1, 0, 0), then moves, to (-1, 2, 0). $RT$ moves first, to (1, 2, 0), then turns, to (-1, -2, 0).
:::

## TRS builds an object's transform

An object in a scene has a position, a direction it faces and a size, and you want one matrix that places a model
there. **TRS**, for translation, rotation and scale (TRS), is the matrix $T \cdot R \cdot S$, which scales first,
rotates next and moves last. The right matrix acts first, so the order is the letters read from the right.

The order is not a choice. Scale and rotation both work about the origin, so they come while the object is still
there: the model stretches along its own axes, turns, and only then moves to its place. Scaling after rotating would
stretch along the world's axes and shear the object, a change that TRS cannot hold.

The coin of the next example has the scale (2, 1, 1), a quarter turn about z and the position (4, 0, 0). Its right
edge is the local point (1, 0, 0). The scale makes it (2, 0, 0), the turn makes it (0, 2, 0), and the move makes it
(4, 2, 0). As a direction, (1, 0, 0, 0) ends at (0, 2, 0): the scale and the turn act, the move does not.

:::example[The columns of a TRS matrix]
The first column is where the x arrow goes after the scale and the turn: (0, 2, 0). The second is the y arrow, only
turned: (-1, 0, 0). The third is the z arrow, unchanged: (0, 0, 1). The fourth is the move: (4, 0, 0). In general, the
first three columns are the rotation's columns, each stretched by its scale factor, and the fourth is the translation.
:::

Strata's `Math::ComposeTransform` builds a TRS matrix in exactly this way. It starts from the rotation's matrix,
stretches its columns by the scale and writes the translation into the last column.

```cpp src="Strata/src/Strata/Math/Math.cpp#L58-L63" from="glm::mat4 result = glm::mat4_cast(rotation);" to="return result;" symbol="ComposeTransform"
glm::mat4 result = glm::mat4_cast(rotation);
result[0] *= scale.x;
result[1] *= scale.y;
result[2] *= scale.z;
result[3] = glm::vec4(translation, 1.0f);
return result;
```

The function `glm::mat4_cast` turns a rotation stored as a quaternion into a matrix. Strata stores the rotation of every
entity that way, and [Rotations](../basics/math-rotations.md) teaches it. The three lines that multiply a column apply
$S$, and the last line adds $T$.

:::why[Why Strata stores three fields and not one matrix]
An entity keeps its translation, rotation and scale as three fields and builds the matrix when it needs one, so a
person or a script can change one field without disturbing the others. The cost: a transform that does not fit TRS,
such as a shear, cannot be stored. `Math::DecomposeTransform` returns false for a matrix it cannot split, and the entity
keeps its old values.
:::

A script builds the same matrix with three `glm` functions. Each multiplies the matrix it is given on the right, so the
chain reads inside out: the outermost call is the last matrix of the product. The program computes $T \cdot R \cdot S$
both ways and prints the coin's right edge, then the direction.

```cpp sketch="basics-math-matrices-trs.cpp"
#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Prints a vector rounded to three decimals; adding 0.0f turns a negative zero into a plain zero.
static void Print(const std::string& label, const glm::vec4& v)
{
	const glm::vec4 r = glm::round(v * 1000.0f) / 1000.0f + 0.0f;
	std::printf("%s = (%g, %g, %g, %g)\n", label.c_str(), r.x, r.y, r.z, r.w);
}

int main()
{
	const glm::mat4 identity(1.0f);
	const glm::vec3 position(4.0f, 0.0f, 0.0f);
	const glm::vec3 size(2.0f, 1.0f, 1.0f);
	const float angle = glm::radians(90.0f);
	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
	// Each builder multiplies the matrix it is given on the right, so the chain reads inside out.
	const glm::mat4 chained = glm::scale(glm::rotate(glm::translate(identity, position), angle, axis), size);
	const glm::mat4 product = glm::translate(identity, position) * glm::rotate(identity, angle, axis) * glm::scale(identity, size);
	Print("chained * position", chained * glm::vec4(1.0f, 0.0f, 0.0f, 1.0f));
	Print("product * position", product * glm::vec4(1.0f, 0.0f, 0.0f, 1.0f));
	Print("product * direction", product * glm::vec4(1.0f, 0.0f, 0.0f, 0.0f));
}
```

```text output-of="basics-math-matrices-trs.cpp"
chained * position = (4, 2, 0, 1)
product * position = (4, 2, 0, 1)
product * direction = (0, 2, 0, 0)
```

1. **Line 20:** `glm::scale(glm::rotate(glm::translate(...)))` is $T \cdot R \cdot S$: the outermost call is the scale, the
   innermost the translation.
2. **Line 21:** the product written out has the same three matrices in the order of the letters.
3. **Lines 22–24:** the position (1, 0, 0, 1) ends at (4, 2, 0) for both builds, and the direction (1, 0, 0, 0) ends at
   (0, 2, 0): the move does not touch it.

`glm::rotate` takes an angle in radians and an axis, and the headers that scripts include bring these three functions.
The Physics Playground sample builds `glm::scale(glm::translate(glm::mat4(1.0f), position), glm::vec3(c_BallScale))`,
which is $T \cdot S$ without a turn. It passes a list of such matrices to `Scene::InstantiateMany`, which makes one copy
of a prefab per matrix and gives each copy that matrix as its local transform.

## A coordinate space is a point of view

Where is a coin? A person at the ring says "three steps out from the ring". A map of the level says "at (0, 1, -3)".
Both are right, because each measures from a different place.

A **coordinate space** (also called a coordinate system) is an origin and a set of axes that numbers are measured from.

The **local space** of an object has its origin at the object and its axes turned with it: its x arrow is the object's
own right, wherever the object stands.

The **world space** is the one space of the whole scene, whose origin and axes never move.

An object's TRS matrix converts the numbers of its local space into numbers of the space it sits in. Take the ring of
the figure below, at the world position (0, 1, 0) and turned a quarter turn about y. A quarter turn about y sends the
x arrow to world -z, as the last section found. The coin at the ring's local position (3, 0, 0) is three steps along
that arrow, at (0, 0, -3) from the ring. The ring's own position adds (0, 1, 0), so the coin is at (0, 1, -3) in the
world.

## A child's world matrix is its parent's times its own

Games arrange objects as a tree. A ring of coins belongs to a post, and the post belongs to a level. In a **transform
hierarchy**, each entity has at most one parent, and its transform is stored relative to that parent.

The **local transform** of an entity is its TRS relative to its parent, or relative to the world when it has no parent.

The **world transform** of an entity is its transform in world space, which the engine builds by combining the local
transforms from the root down to the entity. For an entity with a parent:

$$
W_{\text{child}} = W_{\text{parent}} \cdot L_{\text{child}}
$$

$W_{\text{child}}$ is the child's world matrix, $W_{\text{parent}}$ the parent's world matrix and $L_{\text{child}}$ the
child's local matrix. The right matrix acts first: the local matrix puts the coin in the parent's space, and the
parent's world matrix carries that space into the world. Strata's `Math::ComposeWorldTransform` is exactly this
product, and the scene uses it for every entity with a parent. A chain of three entities multiplies three matrices
in the same way, and an entity without a parent has its local matrix as its world matrix.

::figure{id=parent-and-child}

:::example[The coin on the ring]
The ring's world matrix is the move by (0, 1, 0) after the quarter turn about y. The coin's local matrix is the move by
(3, 0, 0). The product has the last column (0, 1, -3), which is the coin's world position. Now give the ring the position
(5, 1, 0). The coin's local matrix does not change, and its world position becomes (5, 1, -3): the child follows its
parent.
:::

Try it: the ring stays at (0, 1, 0) but turns a half turn about y, which sends the x arrow to (-1, 0, 0). Where is the
coin now?

:::answer
Three steps along the turned x arrow are (-3, 0, 0), and the ring's position adds (0, 1, 0): the coin is at (-3, 1, 0).
:::

A script that spins a ring needs no code for its coins. The `Spinner` of a new script project turns its own entity about
the world's Y axis by writing its local rotation each frame. The coins are the ring's children, so their world matrices
change with the ring's and they circle it.

The next program does the ring's example with matrices and then runs the multiplication backwards, as the next section
explains. Its first output line is the coin's world position.

```cpp sketch="basics-math-matrices-hierarchy.cpp"
#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Prints the last column rounded to three decimals; adding 0.0f turns a negative zero into a plain zero.
static void Print(const std::string& label, const glm::mat4& m)
{
	const glm::vec4 c = glm::round(m[3] * 1000.0f) / 1000.0f + 0.0f;
	std::printf("%s: translation (%g, %g, %g)\n", label.c_str(), c.x, c.y, c.z);
}

int main()
{
	const glm::mat4 identity(1.0f);
	const glm::mat4 parentWorld = glm::translate(identity, glm::vec3(0.0f, 1.0f, 0.0f))
		* glm::rotate(identity, glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::mat4 childLocal = glm::translate(identity, glm::vec3(3.0f, 0.0f, 0.0f));
	const glm::mat4 childWorld = parentWorld * childLocal;
	Print("child world", childWorld);
	Print("inverse(parent) * child world", glm::inverse(parentWorld) * childWorld);
	Print("inverse(parent * local)", glm::inverse(childWorld));
	Print("inverse(local) * inverse(parent)", glm::inverse(childLocal) * glm::inverse(parentWorld));
}
```

```text output-of="basics-math-matrices-hierarchy.cpp"
child world: translation (0, 1, -3)
inverse(parent) * child world: translation (3, 0, 0)
inverse(parent * local): translation (-3, -1, 0)
inverse(local) * inverse(parent): translation (-3, -1, 0)
```

1. **Lines 15–16:** the ring's world matrix is the move after the quarter turn, written as $T \cdot R$.
2. **Line 17:** the coin's local matrix is the move by 3 along x.
3. **Line 18:** `parentWorld * childLocal` is the child's world matrix, with the last column (0, 1, -3).

## The inverse matrix undoes a transform

A scene often knows where a coin is in the world and needs its local numbers: a script drops a coin into a ring, and the
coin must not jump. The tool for this is the **inverse matrix**, the matrix that undoes another. Multiply a matrix by its
inverse and you get the identity.

You can often guess an inverse. The inverse of a move by (3, 0, 0) is the move by (-3, 0, 0). The inverse of a stretch
by 2 is the stretch by 0.5, and the inverse of a quarter turn is a quarter turn the other way. The inverse of a product
undoes the last step first, like taking off shoes before socks: $(AB)^{-1} = B^{-1}A^{-1}$. In this formula, $A^{-1}$ is the
inverse of $A$.

A local matrix comes back from two world matrices in the same way:

$$
L_{\text{child}} = W_{\text{parent}}^{-1} \cdot W_{\text{child}}
$$

$W_{\text{parent}}^{-1}$ is the inverse of the parent's world matrix. Multiply $W_{\text{parent}} \cdot L_{\text{child}}$ by
it on the left, and the parent's part cancels. The last three lines of the previous program check it. The first gives
(3, 0, 0), the local position of the coin. The other two, the inverse of the whole product and the inverses multiplied in
reverse order, agree on (-3, -1, 0).

`glm::inverse` computes the inverse of a matrix. Some matrices have none: a scale by 0 flattens space onto a plane, many
points land on the same place, and nothing can say where each came from. The engine guards against it in `Scene::SetWorldTransform`, which puts an entity at a requested world transform and so needs the local numbers for that place.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L1794-L1804" from="glm::mat4 localTransform = worldTransform;" to="localTransform = glm::inverse(parentWorld) * worldTransform;" symbol="Scene::SetWorldTransform"
glm::mat4 localTransform = worldTransform;
if (const Entity parent = entity.GetParent())
{
	// A parent with zero scale has no inverse; the child's local transform cannot express the request.
	const glm::mat4 parentWorld = GetWorldTransform(parent);
	if (!(glm::abs(glm::determinant(parentWorld)) > c_MinInvertibleDeterminant))
	{
		ST_CORE_WARN("Cannot set the world transform of '{}': its parent's transform is singular", entity.GetName());
		return false;
	}
	localTransform = glm::inverse(parentWorld) * worldTransform;
```

1. **Line 1794:** with no parent, the local transform is the world transform.
2. **Lines 1797–1802:** a parent with a zero scale has no inverse. The engine tests a number that is zero for a
   flattened matrix, which [Bases](../basics/math-bases.md) teaches, logs a warning and returns `false`.
3. **Line 1804:** the line of this section: the local matrix is the inverse of the parent's world matrix times the world
   one.

`Entity::SetParent` uses the same inverse. Its second parameter is `keepWorldTransform`, which is `true` by default.
Then the child's new local matrix is the new parent's inverse times its old world matrix, so the child stays where it
is in the world. With `false`, the child keeps its local numbers and moves with its new parent. Floats round, so an inverse
gives values such as 0.0000001 where the exact answer is 0 ([Numbers](../basics/numbers.md)).

:::example[Putting a coin on a ring]
The ring's world matrix scales by 2 first and then moves by (5, 0, 0). A coin floats at the world position (9, 4, 0).
With `SetParent(ring, true)`, its new local position comes from the inverse: undo the move to get (4, 4, 0), then undo
the scale to get (2, 2, 0). The ring's matrix sends (2, 2, 0) back to (9, 4, 0), so the coin does not jump.
:::

Try it: the same ring, `SetParent(ring, false)`, and a coin whose local numbers were (1, 1, 0) before. Where is the coin
in the world afterwards?

:::answer
The local numbers stay (1, 1, 0). The ring's matrix scales them to (2, 2, 0) and moves them to (7, 2, 0).
:::

## Strata's conventions

Many choices in this page are conventions: another engine or file can choose the opposite and be as correct. Mixing
conventions gives models that lie on their side and objects that turn the wrong way, so a program states its own.
Strata states them in `Strata/src/Strata/Math/Math.h`:

> Engine conventions: right-handed coordinates, +Y up, -Z forward (glTF).
>
> — `Strata/src/Strata/Math/Math.h`

**Handedness** says whether the three axes form a right-handed or a left-handed set. Hold up your right hand with the
thumb as the x arrow and the first finger as the y arrow, and bend the middle finger at a right angle to both: it points
along +z. That is the right-hand rule of the :term[cross product]{id=cross-product}, and the cross product of the x arrow and the y arrow is
(0, 0, 1). In a left-handed set the z arrow points the other way. Strata is right-handed.

::figure{id=right-hand-axes}

The **up axis** points away from the ground: +Y in Strata, whose default gravity is (0, -9.81, 0). A camera, a light and
the `GetForward` of an entity look along -Z, and `GetRight` is +X. The `(glTF)` in the comment names the model format
whose axes Strata follows. One catch comes with it: an imported model faces +Z, as Strata's game-making skill
(`.claude/skills/strata-make-a-game/SKILL.md`) says. A character that should walk along `GetForward` needs a half turn
about Y first.

Lengths are in metres: the default gravity is in metres per second squared, and the physics and camera settings name
metres. One unit of a scene is one metre.

:::why[Why follow glTF's axes]
Following the format of the models Strata imports means the file's axes already match the engine's. The cost is the
facing: models look toward +Z while everything else looks toward -Z.
:::

Two more conventions run through this whole page. Vectors are columns on the right of the matrix, so the matrix that acts
first sits rightmost. That fixes the **matrix order**: the order of a product, with the last transform on the left and
the first on the right. The graphics pipeline applies three matrices to a model's position in this order:

$$
P \cdot V \cdot M \cdot p
$$

$p$ is the position in the model's local space. $M$ is the model matrix, the entity's world matrix, and $V$ is the view
matrix, the inverse of the camera's world matrix. $P$ is the projection matrix ([Projection](../basics/math-projection.md)).
In `Strata/src/Strata/Renderer/SceneRenderer.cpp`, the frame's `ViewProjection` is `Projection * View`, and the view is the
inverse of the camera's world transform.

The last convention is column-major storage: `glm` keeps a matrix in memory one column after another. The first four
numbers of a `glm::mat4` are column 0, so the translation is the numbers 12 to 14 of 16, and `m[3]` is the last column.
A source that stores a matrix row by row holds the flipped grid, and copying its 16 numbers into a `glm::mat4` gives
another transform.

To recognize the convention of another engine, tool or file, ask four questions. Which axis is up, and which way does
a camera look? Is the cross product of x and y +z or -z? Are vectors columns or rows, so which side acts first? What does
one unit measure?

## Common mistakes

- **The order reversed.** Symptom: a coin that circles a point when it should spin on the spot, or a model that stretches
  along the world's axes. The cause is $S \cdot R \cdot T$ written for $T \cdot R \cdot S$, or $RT$ for $TR$. Fix: read the
  product from the right, and put the first action rightmost.
- **Rows read as columns.** Symptom: a translation that lands in the bottom row, or a rotation that turns the wrong way.
  `glm::mat2(1.0f, 2.0f, 3.0f, 4.0f)` has the column (1, 2) first, though it reads like the row (1, 2). Fix: write the
  columns, and check one with `m[0]`.
- **A matrix declared without a value.** Symptom: an object that jumps to a strange place or vanishes. `glm` does not set
  `glm::mat4 m;` to the identity: it holds whatever was in memory, as `glm::vec3 v;` does. Fix: write `glm::mat4 m(1.0f);`.
- **A direction with w = 1.** Symptom: a forward arrow that changes when the object moves. Fix: use w = 0 for a direction.
- **The child's world matrix as $L \cdot W$.** Symptom: a child that circles the world origin instead of its parent. Fix:
  write the parent's world matrix on the left of the child's local matrix.

## Summary

- A matrix is a grid, a matrix times a vector is one dot product per row, and its columns are the places the axes go.
- The product $AB$ applies $B$ first, and the order matters: $AB$ is not $BA$.
- A 4×4 matrix adds translation through the fourth number w: 1 for a position and 0 for a direction. TRS is $T \cdot R \cdot S$.
- A child's world matrix is its parent's world matrix times its own local one, and the inverse of the parent's matrix
  gives the local one back.
- Strata is right-handed with +Y up, -Z forward and metres. Its vectors are columns on the right of the matrix, stored
  column by column.

## Check yourself

1. In `glm::mat2 m(1.0f, 2.0f, 3.0f, 4.0f);`, what is `m[1]`? (a) (1, 2). (b) (3, 4). (c) (2, 4). (d) 3.

   :::answer{tests="matrix-columns"}
   (b). The constructor reads columns, so `m[0]` is (1, 2) and `m[1]` is (3, 4). Answer (c) is the second row, and (d) is
   `m[1][0]`.
   :::

2. $T$ moves by (0, 2, 0) and $R$ is the half turn about z, which sends (1, 0, 0) to (-1, 0, 0). Where does `T * R` send the
   position (1, 0, 0)? Where does `R * T` send it?

   :::answer{tests="matrix-product"}
   `T * R` turns first, to (-1, 0, 0), then moves, to (-1, 2, 0). `R * T` moves first, to (1, 2, 0), then turns, to
   (-1, -2, 0).
   :::

3. Why does a direction use w = 0? (a) So that it has length 0. (b) So that the move in the last column does not change it.
   (c) So that no turn changes it. (d) So that a scale acts on it twice.

   :::answer{tests="trs-w"}
   (b). The last column is multiplied by w, so w = 0 removes the move. The upper left 3×3 part still turns and scales a
   direction, which rules out (c) and (a).
   :::

4. A parent's world matrix scales by 2 first and then moves by (2, 0, 0). A child has the local position (1, 1, 0). Where
   is the child in the world, and which product gives the child's local matrix from its world matrix?

   :::answer{tests="hierarchy-inverse"}
   The local position scales to (2, 2, 0) and moves to (4, 2, 0). The local matrix is the inverse of the parent's world
   matrix times the child's world matrix.
   :::

5. Which statement holds in Strata? (a) +Z is up. (b) A camera looks along +Z. (c) The cross product of x and y is +z and a
   camera looks along -Z. (d) One unit is one centimetre.

   :::answer{tests="conventions"}
   (c). Strata is right-handed with +Y up, cameras look along -Z, and one unit is one metre.
   :::

## Practice

1. **Basic.** The matrix has the columns (1, 1) and (-1, 1). Where does it send the point (2, 3)? What does it do to the
   x arrow and the y arrow?

   :::answer[Worked solution]{tests="matrix-columns"}
   2 × (1, 1) + 3 × (-1, 1) = (2 - 3, 2 + 3) = (-1, 5). The x arrow goes to (1, 1) and the y arrow to (-1, 1), so the
   matrix turns by 45° and stretches by about 1.41.
   :::

2. **Medium.** The 4×4 matrix is $T \cdot S$ with the move (0, 2, 0) and the scale 2 on every axis. Write its columns, and
   compute where it sends the position (1, 1, 1) and the direction (1, 1, 1).

   :::answer[Worked solution]{tests="trs-w"}
   The columns are (2, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0) and (0, 2, 0, 1). The position (1, 1, 1, 1) scales to
   (2, 2, 2) and moves to (2, 4, 2). The direction (1, 1, 1, 0) becomes (2, 2, 2): the move does not touch it.
   :::

3. **Medium.** A modelling tool uses right-handed axes with +Z up and +Y forward. Write the 3×3 matrix that sends its x
   arrow to Strata's x arrow, its up arrow to +Y and its forward arrow to -Z. Is the result still right-handed?

   :::answer[Worked solution]{tests="matrix-columns conventions"}
   The columns are where the tool's three arrows go: (1, 0, 0) for its x, (0, 0, -1) for its y (forward becomes -Z) and
   (0, 1, 0) for its z (up becomes +Y). The rows are (1, 0, 0), (0, 0, 1) and (0, -1, 0). It is a quarter turn about x, a
   rotation, so right-handed stays right-handed.
   :::

4. **Hard.** In a program of your own, put six coins on a circle of radius 3 in the x–z plane of a ring, 60° apart and
   starting on the ring's x arrow. The ring stands at (10, 1, 0), turned a quarter turn about y. Predict the world
   position of coin 1 by hand, then print all six.

   :::answer[Worked solution]{tests="trs-w hierarchy-inverse" solution="sketches/basics-math-matrices-ring.cpp"}
   Coin 1 has the local position (3 cos 60°, 0, 3 sin 60°) = (1.5, 0, 2.598). The quarter turn sends (x, y, z) to
   (z, y, -x), so it becomes (2.598, 0, -1.5), and the ring's position gives (12.6, 1, -1.5). The program builds each
   coin's world matrix as the ring's matrix times a move, and prints its last column.

   ```cpp sketch="basics-math-matrices-ring.cpp"
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>

   // The local position of coin `index` of six, on a circle of the given radius in the ring's x-z plane.
   static glm::vec3 CoinLocalPosition(int index, float radius)
   {
   	const float angle = glm::radians(60.0f * static_cast<float>(index));
   	return glm::vec3(radius * std::cos(angle), 0.0f, radius * std::sin(angle));
   }

   int main()
   {
   	const glm::mat4 identity(1.0f);
   	const glm::mat4 ringWorld = glm::translate(identity, glm::vec3(10.0f, 1.0f, 0.0f))
   		* glm::rotate(identity, glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
   	for (int index = 0; index < 6; index++)
   	{
   		const glm::mat4 coinWorld = ringWorld * glm::translate(identity, CoinLocalPosition(index, 3.0f));
   		const glm::vec3 world = glm::vec3(coinWorld[3]);
   		std::printf("coin %d: world (%.2f, %.2f, %.2f)\n", index, world.x + 0.0f, world.y + 0.0f, world.z + 0.0f);
   	}
   }
   ```

   ```text output-of="basics-math-matrices-ring.cpp"
   coin 0: world (10.00, 1.00, -3.00)
   coin 1: world (12.60, 1.00, -1.50)
   coin 2: world (12.60, 1.00, 1.50)
   coin 3: world (10.00, 1.00, 3.00)
   coin 4: world (7.40, 1.00, 1.50)
   coin 5: world (7.40, 1.00, -1.50)
   ```

   1. **Lines 7–11:** one function makes a coin's local position from its index.
   2. **Lines 16–17:** the ring's world matrix is the move after the quarter turn.
   3. **Line 20:** the coin's world matrix is the ring's matrix times the coin's local move.
   4. **Lines 21–22:** the last column is the world position: coin 1 prints (12.60, 1.00, -1.50), as predicted.
   :::

5. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished
   game](../make/project-coin-run.md#ship-the-finished-game): make an empty entity `Ring` at (0, 1, 0) with a `Spinner`
   whose `DegreesPerSecond` is 0, turned 90° about Y. Drag one more coin, `Prefabs/Coin.stprefab`, from the Content
   Browser into the Scene view: the five others appear only in play. Attach a script to it that makes it the ring's child, keeps its local numbers and
   logs its world position. Predict the position first.

   :::answer[Worked solution]{tests="hierarchy-inverse"}
   The ring's quarter turn sends the local position (3, 0, 0) to (0, 0, -3), and the ring's position adds (0, 1, 0):
   about (0, 1, -3). Make `RingChild` with **Scripts ▸ New Script...**, replace its text with the one below, build, and
   pick it from **Add Script...** in the coin's Script component.

   ```cpp pseudocode
   #include "StrataScript/StrataScript.h"

   using namespace Strata;

   // Makes its coin a child of Ring, keeps the coin's local numbers and logs where the coin lands.
   class RingChild : public Script
   {
   public:
   	void OnCreate() override
   	{
   		Entity ring = Scene::FindEntityByName("Ring");
   		GetEntity().SetParent(ring, false);
   		GetTransform().SetTranslation(glm::vec3(3.0f, 0.0f, 0.0f));
   		Log::Info("coin world position ", GetTransform().GetWorldPosition());
   	}
   };

   ST_SCRIPT_CLASS(RingChild)
   {
   }
   ```

   1. **Lines 11–12:** `SetParent(ring, false)` keeps the local numbers; with `true`, the engine would compute new ones
      from the coin's old world position with the inverse.
   2. **Lines 13–14:** the local numbers become (3, 0, 0), and the **Console** shows
      `coin world position (1.78814e-07, 1, -3)`: an x of 0, up to a :term[rounding error]{id=rounding-error}.
   :::

## Where the book uses it

- [The scene graph](../world/scene-graph.md) keeps each entity's world matrix up to date from its parent's and its own
  local one, and caches it.
- [Coordinates](../gpu/coordinates.md) takes a position through the model, view and projection matrices to a pixel.
- [Skeletons](../animation/skeletons.md) place a character's joints with a world matrix per joint, built down a hierarchy.

## Further reading

- [The glm manual](https://github.com/g-truc/glm/blob/master/manual.md): the types and functions this page calls; intermediate.
- 3Blue1Brown, "Essence of linear algebra": videos that draw a matrix as a change of the axes; beginner.
- Learn OpenGL, "Transformations": a chapter on matrices, translation, rotation and scale in code; beginner.

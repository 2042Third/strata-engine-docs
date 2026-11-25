---
id: basics/math-bases
title: "Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose"
description: "Build frames from cross products, move directions between spaces, read a determinant, carry normals through a scale and split a matrix into parts."
kind: primer
size: M
tracks: [B, E]
needs: [basics/math-matrices]
time: 60
learn:
  - id: orthonormal-frame
    text: explain why the inverse of a rotation is its transpose and build a frame from two cross products
  - id: tangent-space
    text: compute a direction from a surface's tangent space to world space and back
  - id: determinant
    text: compute a determinant and say what its size, its sign and zero tell about a transform
  - id: normal-matrix
    text: compute a normal through the inverse transpose and through the cofactor matrix, and explain why the model matrix fails
  - id: decomposition
    text: predict which matrices split into translation, rotation and scale and which do not
status: final
---

::::test-out

1. A rotation sends the x axis to (0, 1, 0), the y axis to (-1, 0, 0) and keeps the z axis. Write the matrix that undoes it, column by column.

   :::answer{tests="orthonormal-frame"}
   The inverse of a rotation is its transpose. The rotation's columns (0, 1, 0), (-1, 0, 0) and (0, 0, 1) become the
   rows of the inverse, whose columns are (0, -1, 0), (1, 0, 0) and (0, 0, 1).
   :::

2. A surface has the tangent (1, 0, 0), the bitangent (0, 0, 1) and the normal (0, -1, 0). Which world direction is (2, 3, 1) in its tangent space?

   :::answer{tests="tangent-space"}
   Take 2 of the tangent, 3 of the bitangent and 1 of the normal: (2, 0, 0) + (0, 0, 3) + (0, -1, 0) = (2, -1, 3).
   :::

3. A matrix has the columns (2, 0, 0), (0, 3, 0) and (0, 0, -1). Compute its determinant and say whether it mirrors.

   :::answer{tests="determinant"}
   The determinant is 2 × 3 × -1 = -6. It scales volumes by 6, and the minus sign says that it mirrors.
   :::

4. A matrix stretches y by 2. A slope has the direction (1, 1, 0) and the normal (1, -1, 0). Which normal does the inverse transpose give, and does it stand at a right angle to the stretched slope?

   :::answer{tests="normal-matrix"}
   The slope becomes (1, 2, 0). The inverse transpose halves y, so the normal becomes (1, -0.5, 0), and the dot product
   is 1 - 1 = 0: a right angle. The model matrix gives (1, -2, 0), with the dot product -3.
   :::

5. The columns (1, 0, 0), (1, 1, 0) and (0, 0, 1) make a matrix. Can a rotation and a scale alone make it?

   :::answer{tests="decomposition"}
   No. The dot product of the first two columns is 1, not 0. A rotation and a scale always give columns at right
   angles, so this matrix holds a shear.
   :::

::::

## Why you will need this

[Matrices](../basics/math-matrices.md) move points and directions. Three jobs remain: undo a rotation cheaply, carry a
normal through a stretched object, and tell what a matrix does to shapes.

[Mirrors and camera-relative space](../draw/mirrors-camera-relative.md) flips the faces of a mirrored object.
[Materials](../light/materials.md) reads normal maps in the tangent space of each surface. [Building
bodies](../physics/building-bodies.md) bakes an object's scale into a collision shape.

## The columns of a rotation form an orthonormal basis

A rotation turns the x axis into (0, 1, 0), the y axis into (-1, 0, 0) and keeps the z axis. Its columns are those three
vectors. Each has the length 1, and each pair has the :term[dot product]{id=dot-product} 0, so the three stand at right angles.

An **orthonormal basis** is three vectors of length 1 at right angles to each other. Every point is some amount of the
first, plus some of the second, plus some of the third. The columns of every rotation form one.

To undo the turn you need its inverse, and for a rotation you can write it down. The **transpose** of a matrix swaps its
rows and columns: the number in row $i$ and column $j$ moves to row $j$ and column $i$. Here are the turn $M$ and its
transpose $M^{T}$, read "M transpose".

```text
M = |  0 -1  0 |        M^T = |  0  1  0 |
    |  1  0  0 |              | -1  0  0 |
    |  0  0  1 |              |  0  0  1 |
```

The columns of $M$ became the rows of $M^{T}$. Multiply $M^{T}$ by $M$. The number in row $i$ and column $j$ of the product
is row $i$ of $M^{T}$ dotted with column $j$ of $M$, which is column $i$ of $M$ dotted with column $j$ of $M$. That is 1
when $i$ equals $j$, because each length is 1, and 0 otherwise, because of the right angles. The product is the
:term[identity matrix]{id=identity-matrix}, so for a rotation the transpose is the inverse.

A check at the limits: a matrix that doubles x has a first column of length 2, so its transpose times itself holds a 4,
not a 1. The shortcut needs an orthonormal basis, which rules out scale and shear. Real columns are only almost of length 1
([Numbers](../basics/numbers.md)), so the transpose is almost the inverse.

## Two cross products build a frame around a direction

A camera knows only which way to face. To turn it, you need all three axes of its frame. The forward direction gives
one, and the :term[cross product]{id=cross-product}, which stands at a right angle to both its inputs, gives the others.

:::example[A frame that faces (3, 0, 4)]
The camera stands at the origin, the target at (3, 0, 4), and up is (0, 1, 0). Forward is (0.6, 0, 0.8): the step
divided by its length 5. Right is the cross product of forward and up, (-0.8, 0, 0.6), and it already has the length 1.
The true up is the cross product of right and forward: (0, 1, 0). Strata's forward is the -z axis, so the third column
is back, the opposite of forward: (-0.6, 0, -0.8).

The dot product of right and back is 0.48 - 0.48 = 0. The rotation is the matrix
with the columns right, up and back.
:::

Try it: build the frame of a camera at the origin that faces (0, 0, -5).

:::answer
Forward is (0, 0, -1). Right is the cross product of forward and up, (1, 0, 0). True up is the cross product of right
and forward, (0, 1, 0). Back is (0, 0, 1). The frame is the identity matrix: no turn is needed to face the -z axis.
:::

:::question[What do the lines of C++ below use?]
Calls such as `glm::cross(` and `glm::length(` come from the library `glm`, and
[Programming 3](../basics/programming-3.md) explains the `::` and the call. Read each as "the function of that name".
:::

The function `Motion::LookAt` of the script library does exactly these steps. Find the two cross products, the fallback
for a target straight above, and the order of the columns.

```cpp src="StrataScriptCore/Include/StrataScript/Gameplay.h#L229-L248"
static glm::quat LookAt(const glm::vec3& from, const glm::vec3& to, const glm::vec3& up = glm::vec3(0.0f, 1.0f, 0.0f))
{
	const glm::vec3 offset = to - from;
	const float distance = glm::length(offset);
	if (!(distance > 1e-6f))
		return glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	const glm::vec3 forward = offset / distance;
	glm::vec3 right = glm::cross(forward, up);
	if (!(glm::length(right) > 1e-6f))
	{
		right = glm::cross(forward, glm::vec3(0.0f, 0.0f, 1.0f));
		if (!(glm::length(right) > 1e-6f))
			right = glm::cross(forward, glm::vec3(1.0f, 0.0f, 0.0f));
	}
	right = glm::normalize(right);
	const glm::vec3 trueUp = glm::cross(right, forward);
	// The rotation's columns are where it takes +X, +Y and +Z: right, up, and back (-forward).
	const glm::mat3 basis(right, trueUp, -forward);
	return glm::normalize(glm::quat_cast(basis));
}
```

1. **Line 236:** the first cross product gives right, at a right angle to forward and up.
2. **Lines 237–242:** for a target straight above, forward and up are parallel, their cross product is zero, and the z
   or x axis stands in for up.
3. **Line 244:** the second cross product gives the true up, already of length 1.
4. **Line 246:** the columns are right, up and back. The turn into a quaternion that follows is the business of
   [Rotations](../basics/math-rotations.md).

## A basis is a space of its own

Take an orthonormal basis, the three columns $T$, $B$ and $N$. A direction can be written in it as three numbers, the
amounts of each axis. The direction (2, 3, 1) means 2 of the first axis plus 3 of the second plus 1 of the third. That
is the matrix times the vector, with the basis as the columns.

A surface gives a natural basis: its tangent, its **bitangent**, a second direction along the surface at a right angle
to the tangent, and its normal.

The **tangent space** is the space whose axes are those three. A normal map, or a light
sampled around a surface, is simple to describe in it, because "straight out of the surface" is always (0, 0, 1).

Strata's light sampling builds the frame from the normal alone. The shader language Slang looks like C++ with these differences:
`float3` is a vector of three numbers, `float3x3` is a matrix, and a matrix constructor takes its numbers by rows. So
`float3x3(tangent, bitangent, normal)` has the three vectors as rows, and `transpose` turns them into columns. `mul`
multiplies a matrix by a vector.

```slang src="Strata/shaders/Include/IBL.slang#L41-L48"
// Tangent frame around a normal.
float3x3 TangentBasis(float3 normal)
{
	float3 up = abs(normal.z) < 0.999 ? float3(0.0, 0.0, 1.0) : float3(1.0, 0.0, 0.0);
	float3 tangent = normalize(cross(up, normal));
	float3 bitangent = cross(normal, tangent);
	return transpose(float3x3(tangent, bitangent, normal));
}
```

Read it line by line. The helper `up` is the z axis, or the x axis when the normal is almost along z, because the cross
product of two parallel vectors is zero. The tangent is the cross product of `up` and the normal, :term[normalized]{id=normalization}. The
bitangent is the cross product of the normal and the tangent, and needs no normalizing. The last line puts the three in
the columns.

:::example[The frame of a normal pointing up]
For the normal (0, 1, 0), `up` is (0, 0, 1). The tangent is the cross product of (0, 0, 1) and (0, 1, 0): (-1, 0, 0).
The bitangent is the cross product of (0, 1, 0) and (-1, 0, 0): (0, 0, 1). The tangent-space direction (0.6, 0, 0.8)
becomes 0.6 × (-1, 0, 0) + 0.8 × (0, 1, 0) = (-0.6, 0.8, 0) in the world.

To return to tangent space, use the transpose: the dot products with the tangent, the bitangent and the normal. They are
0.6, 0 and 0.8, the numbers you started from.
:::

Try it: which tangent-space direction is the world direction (0, 1, 0) in that frame?

:::answer
The dot products with the tangent, bitangent and normal are 0, 0 and 1: (0, 0, 1), straight out of the surface.
:::

## The determinant says how a matrix scales volume

Stretch the unit cube with a matrix whose columns are (2, 0, 0), (0, 3, 0) and (0, 0, 1). It becomes a box 2 by 3 by 1,
and its volume grows from 1 to 6. The **determinant** of a matrix is that factor: how much the matrix multiplies areas
in 2D, or volumes in 3D.

Take a 3 × 3 matrix with the columns $a$, $b$ and $c$. Its determinant is the volume of the box that they span: the
dot product of $a$ with the cross product of $b$ and $c$.

$$
\det M = a \cdot (b \times c)
$$

$\det M$, read "the determinant of M", is one number. $\cdot$ is the dot product and $\times$ the cross product. For the
box above, $b \times c$ is (3, 0, 0), which gives 6 with $a$.

From the numbers in a matrix, use its rows. Call the first row $p$, $q$ and $r$, the second $s$, $t$ and $u$, and the
third $v$, $w$ and $x$:

$$
\det M = p(tx - uw) - q(sx - uv) + r(sw - tv)
$$

Each number of the first row multiplies the determinant of the two-by-two block left when you cross out its row and
column, and the signs alternate. For the box, only $p$ = 2, $t$ = 3 and $x$ = 1 are not zero: 2 × (3 × 1 - 0) = 6.

The sign tells more. The columns (-1, 0, 0), (0, 1, 0) and (0, 0, 1) have the determinant -1: the matrix keeps every
volume and turns the x axis around. That is a mirror: the right hand becomes a left hand.

A mirror reverses the winding of a face, the order in which you meet its corners going around it. Strata, like glTF,
draws a triangle as front-facing when its corners run counterclockwise. A mirrored object would show its backs, unless
the renderer reverses the order, which [Mirrors and camera-relative space](../draw/mirrors-camera-relative.md) shows.

A zero determinant is the other limit. The columns (1, 0, 0), (0, 1, 0) and (0, 0, 0) flatten every point onto a plane.
Two different points land on the same spot, and no matrix can undo that: a flat matrix has no inverse.

:::why
The formula of the inverse divides by the determinant, and `glm::inverse` follows it. For a flat matrix it returns `inf`
and `nan` values without a warning. Check the determinant against a small limit first: 0.0000001 is as flat in
practice.
:::

## A normal needs the inverse transpose

A normal is not a step along a surface: it is the direction at a right angle to it. A matrix that stretches one axis
more than another breaks that right angle.

:::example[A slope stretched along x]
A slope has the direction (1, 1, 0) and the normal (1, -1, 0), and their dot product is 0. A matrix doubles x. The slope
becomes (2, 1, 0). The normal sent through the same matrix becomes (2, -1, 0), and its dot product with the slope is
4 - 1 = 3: no right angle. The normal that does stand at a right angle is (0.5, -1, 0), the original with x halved.
:::

Try it: which normal stands at a right angle to the slope when the matrix triples y instead?

:::answer
(1, -1/3, 0), the original with y divided by 3. The slope becomes (1, 3, 0), and the dot product is 1 - 1 = 0.
:::

::figure{id=bent-normal}

The fix is the **normal matrix**: the inverse transpose of the 3 × 3 part of the model matrix. For the doubling of x, the
inverse halves x, and the transpose of a diagonal matrix is itself, which gives the (0.5, -1, 0) above. The translation
is omitted, because a direction has no position.

:::derivation
A tangent $t$ becomes $Mt$. You want a matrix $G$ with $(Gn) \cdot (Mt) = 0$ whenever $n \cdot t = 0$. Because
$(Gn)^{T} M t = n^{T} G^{T} M t$, it is enough that $G^{T} M$ is the identity. Then $G^{T} = M^{-1}$, so $G = (M^{-1})^{T}$.
:::

For a rotation the inverse is the transpose, so the inverse transpose is the rotation itself: the model matrix is right.
A uniform scale only changes the length, which normalizing repairs. Only a non-uniform scale or a shear bends normals.

The inverse costs a division. The **cofactor matrix** avoids it: its columns are cross products of the original's
columns. For the columns $c_0$, $c_1$ and $c_2$ of the 3 × 3 part, they are $c_1 \times c_2$, $c_2 \times c_0$ and
$c_0 \times c_1$. It equals the determinant times the inverse transpose, so it points the same way, only longer.

For the doubling of x, $c_0$ is (2, 0, 0), $c_1$ is (0, 1, 0) and $c_2$ is (0, 0, 1). The cofactor's columns are
(1, 0, 0), (0, 2, 0) and (0, 0, 2). It maps the normal (1, -1, 0) to (1, -2, 0), which is the determinant 2 times the
normal matrix's answer. After normalizing, the two agree.

Under a mirror the determinant is negative, so the cofactor matrix turns the normal around, away from the one the
inverse transpose gives. Strata's shaders therefore flip the sign of the result for mirrored instances. A program
computes the three answers for the example.

```cpp sketch="basics-math-bases-normals.cpp"
// A normal under a stretch along x: the model matrix tilts it off the surface, the normal matrix does not.
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const glm::mat3 model(glm::vec3(2.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::vec3 tangent(1.0f, 1.0f, 0.0f); // a direction along the surface
	const glm::vec3 normal(1.0f, -1.0f, 0.0f); // at a right angle to it
	const glm::vec3 surface = model * tangent;

	const glm::vec3 wrong = model * normal;
	const glm::mat3 normalMatrix = glm::transpose(glm::inverse(model));
	const glm::vec3 right = normalMatrix * normal;
	std::printf("surface (%g, %g, %g)\n", surface.x, surface.y, surface.z);
	std::printf("model matrix: (%g, %g, %g), dot with the surface %g\n", wrong.x, wrong.y, wrong.z, glm::dot(wrong, surface));
	std::printf("normal matrix: (%g, %g, %g), dot with the surface %g\n", right.x, right.y, right.z, glm::dot(right, surface));

	const glm::mat3 cofactor(glm::cross(model[1], model[2]), glm::cross(model[2], model[0]), glm::cross(model[0], model[1]));
	const glm::vec3 scaled = cofactor * normal;
	std::printf("cofactor: (%g, %g, %g), the normal matrix's result times %g\n", scaled.x, scaled.y, scaled.z, glm::determinant(model));
	return 0;
}
```

```text output-of="basics-math-bases-normals.cpp"
surface (2, 1, 0)
model matrix: (2, -1, 0), dot with the surface 3
normal matrix: (0.5, -1, 0), dot with the surface 0
cofactor: (1, -2, 0), the normal matrix's result times 2
```

1. **Line 13:** the normal matrix is the transpose of the inverse.
2. **Lines 19–21:** the cofactor matrix is three cross products of columns, with no division, and its answer is the normal
   matrix's times the determinant, 2.

:::why
Strata's `TransformNormal` in `Strata/shaders/Include/Scene.slang` uses the cofactor matrix for every vertex, and so does a skinned vertex's normal. The costs are a length that is not 1, so callers
normalize, and the sign flip for a mirror.
:::

## Decomposition splits a matrix into translation, rotation and scale

A game stores an object as three parts, and a matrix joins them. The **decomposition** of a transform recovers
translation, rotation and scale from a matrix. It has an answer only when the matrix has the form that the parts make.

The matrix of the parts is translation times rotation times scale. Scale comes first, so the columns of the 3 × 3 part
are the rotation's columns, each multiplied by one scale. The fourth column is the translation. To go the other way, the
lengths of the three columns are the scales, the columns divided by their lengths are the rotation, and the fourth column
is the translation.

:::example[A turn and a scale]
The columns (0, 2, 0), (-3, 0, 0) and (0, 0, 1) have the lengths 2, 3 and 1. Divided by them they are (0, 1, 0),
(-1, 0, 0) and (0, 0, 1): the quarter turn from the start of the page. The matrix is that turn with the scale (2, 3, 1).
:::

Try it: split the columns (0, 0, -2), (0, 2, 0) and (2, 0, 0) into a rotation and a scale.

:::answer
The scale is (2, 2, 2), and the rotation has the columns (0, 0, -1), (0, 1, 0) and (1, 0, 0): a quarter turn about y.
:::

Three kinds of matrix have no clean answer:

- **A shear.** Scale and rotation give columns at right angles; a shear does not. Turn a child by 45 degrees under a
  parent that scales by (2, 1, 1). The world matrix has the columns (1.41, 0.71, 0) and (-1.41, 0.71, 0), whose dot
  product is -1.5, so no rotation and scale make them.
- **A mirror.** The determinant is negative, which no rotation can make. One scale, or all three, must be negative,
  and any axis can carry the sign, so whoever writes the decomposition has to choose.
- **A zero scale.** A flattened column has length zero, and dividing by it fails. The direction that the rotation should
  have there no longer exists in the matrix.

:::note[Strata's decomposition]
`Math::DecomposeTransform` in `Strata/src/Strata/Math/Math.cpp` follows these steps. It returns `false` for values that
are not finite, for a bottom-right entry near zero and for a scale near zero. It folds a mirror into a negative x scale
and drops a shear without a word. [The math module](../core/math.md) and [the scene graph](../world/scene-graph.md) say
more.
:::

## Common mistakes

- **Normals sent through the model matrix.** Symptom: a stretched object that lights as if it were dented, with
  highlights in the wrong places. Fix: use the normal matrix or the cofactor matrix, and normalize the result.
- **A matrix with a zero determinant inverted.** Symptom: `inf` or `nan` in the result, and objects that vanish. Fix:
  check the determinant against a small limit first, and treat a flat matrix as having no inverse.
- **The transpose used as the inverse of a matrix with scale.** Symptom: a point that does not return to where it
  started. Fix: use the transpose only for rotations, and `glm::inverse` for the rest.
- **A matrix declared without a value.** Symptom: random numbers in the result. `glm::mat3 m;` holds whatever was in
  memory, not the identity. Fix: write `glm::mat3(1.0f)`.

## Summary

- The columns of a rotation form an orthonormal basis, so its inverse is its transpose; two cross products build a frame
  around a forward direction, as `Motion::LookAt` does.
- A tangent frame takes a direction from tangent space to the world with its columns and back with its transpose.
- The determinant is the factor of volumes; a negative one is a mirror that reverses winding, and zero is a flat matrix
  with no inverse.
- Normals need the normal matrix, the inverse transpose of the 3 × 3 part; the cofactor matrix gives the same
  direction without a division and turns around under a mirror.
- Translation, rotation and scale make only columns at right angles: a shear fails, a mirror needs a negative scale on
  a chosen axis, and a zero scale leaves no rotation.

## Check yourself

1. The columns of a matrix are (0, 0, 2), (1, 0, 0) and (0, 1, 0). Is its transpose its inverse? (a) yes (b) no, one
   column has length 2 (c) no, the columns are not at right angles

   :::answer{tests="orthonormal-frame"}
   (b). The columns are at right angles, but the first has length 2, so the transpose times the matrix holds a 4, not a
   1.
   :::

2. A frame has the tangent (0, 0, 1), the bitangent (1, 0, 0) and the normal (0, 1, 0). Which tangent-space direction is
   the world direction (3, 4, 0)?

   :::answer{tests="tangent-space"}
   The dot products with the tangent, bitangent and normal are 0, 3 and 4: the direction is (0, 3, 4).
   :::

3. A matrix has the columns (1, 0, 0), (0, 0, 1) and (0, 1, 0). Compute the determinant and say what it does to a
   triangle's winding.

   :::answer{tests="determinant"}
   The cross product of the second and third columns is (-1, 0, 0), and its dot product with the first is -1. The matrix
   swaps two axes: it mirrors, so it reverses the winding.
   :::

4. A matrix scales z by 4. Which of the model matrix, the normal matrix and the cofactor matrix keep the normal
   (1, 0, 1) at a right angle to the surface direction (-1, 0, 1)?

   :::answer{tests="normal-matrix"}
   The surface becomes (-1, 0, 4). The normal matrix gives (1, 0, 0.25), with the dot product -1 + 1 = 0. The cofactor
   gives (4, 0, 1), four times that, and also a right angle. The model matrix gives (1, 0, 4), with the dot product 15.
   :::

5. A matrix has the columns (0, 0, 0), (0, 1, 0) and (0, 0, 1). What does its decomposition give?

   :::answer{tests="decomposition determinant"}
   Nothing. The first column has length zero, so its scale is zero and the first axis of the rotation is lost. The
   determinant is zero too: the matrix has no inverse.
   :::

## Practice

1. **Basic.** Use the formula of the first row to compute the determinant of the matrix with the rows (2, 0, 1),
   (1, 3, 0) and (0, 1, 1).

   :::answer[Worked solution]{tests="determinant"}
   The first term is 2 × 3 = 6, the second is 0, and the third is 1 × 1 = 1. The determinant is 7: volumes grow seven
   times, and the matrix does not mirror.
   :::

2. **Medium.** A tree scales by (1, 2, 4). A branch has the direction (0, 1, 1) and the normal (0, 1, -1). Compute the
   stretched branch, the normal from the normal matrix and the one from the cofactor matrix, and check the right angle.

   :::answer[Worked solution]{tests="normal-matrix"}
   The branch becomes (0, 2, 4). The inverse transpose scales by (1, 1/2, 1/4): the normal becomes (0, 0.5, -0.25), and
   the dot product with the branch is 1 - 1 = 0. The cofactor has 8, 4 and 2 on its diagonal and gives (0, 4, -2): eight
   times that, and 8 is the determinant.
   :::

3. **Medium.** Compute the frame that `TangentBasis` builds for the normal (1, 0, 0), and the world direction of the
   tangent-space direction (1, 0, 1).

   :::answer[Worked solution]{tests="tangent-space"}
   The helper is (0, 0, 1), so the tangent is the cross product of (0, 0, 1) and (1, 0, 0): (0, 1, 0). The bitangent is
   the cross product of (1, 0, 0) and (0, 1, 0): (0, 0, 1). The direction becomes (0, 1, 0) + (1, 0, 0) = (1, 1, 0).
   :::

4. **Hard.** Write a function `Report` that takes the 3 × 3 part of a matrix. It prints the scale, the determinant
   and one of: a turn and scale, a shear, a mirror, flat. Run it on four matrices.

   :::answer[Worked solution]{tests="decomposition determinant" solution="sketches/basics-math-bases-decompose.cpp"}
   The zero length and the right angles are tested before the mirror.

   ```cpp sketch="basics-math-bases-decompose.cpp"
   // Decomposing the 3x3 part of a matrix: the lengths of its columns are the scale, if the columns are at right angles.
   #include <cstdio>
   #include <glm/glm.hpp>

   void Report(int number, const glm::mat3& m)
   {
   	const glm::vec3 scale(glm::length(m[0]), glm::length(m[1]), glm::length(m[2]));
   	std::printf("matrix %d: scale (%g, %g, %g), determinant %g, ", number, scale.x, scale.y, scale.z, glm::determinant(m));
   	if (glm::min(scale.x, glm::min(scale.y, scale.z)) < 0.0001f)
   		std::printf("a zero scale: no rotation to find\n");
   	else if (glm::abs(glm::dot(m[0], m[1])) + glm::abs(glm::dot(m[0], m[2])) + glm::abs(glm::dot(m[1], m[2])) > 0.0001f)
   		std::printf("columns not at right angles: a shear\n");
   	else
   		std::printf("%s\n", glm::determinant(m) < 0.0f ? "a mirror: one scale is negative" : "rotation and scale");
   }

   int main()
   {
   	Report(1, glm::mat3(glm::vec3(0.0f, 2.0f, 0.0f), glm::vec3(-3.0f, 0.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
   	Report(2, glm::mat3(glm::vec3(1.0f, 0.0f, 0.0f), glm::vec3(1.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
   	Report(3, glm::mat3(glm::vec3(-1.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f)));
   	Report(4, glm::mat3(glm::vec3(1.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 0.0f)));
   	return 0;
   }
   ```

   ```text output-of="basics-math-bases-decompose.cpp"
   matrix 1: scale (2, 3, 1), determinant 6, rotation and scale
   matrix 2: scale (1, 1.41421, 1), determinant 1, columns not at right angles: a shear
   matrix 3: scale (1, 1, 1), determinant -1, a mirror: one scale is negative
   matrix 4: scale (1, 1, 0), determinant 0, a zero scale: no rotation to find
   ```

   1. **Line 7:** the lengths of the columns are the scale.
   2. **Lines 9–10:** a zero scale comes first, because it has no rotation and a division would fail.
   3. **Lines 11–12:** columns that are not at right angles are a shear.
   4. **Lines 13–14:** only now does the sign of the determinant tell a mirror from a plain turn and scale.
   :::

5. **Hard.** Optional, on your [Coin Run](../make/project-coin-run.md) or Checkpoint 4 of [Ship the finished
   game](../make/project-coin-run.md#ship-the-finished-game): build a frame that faces a coin from the ball, and show it
   with three markers one metre along its axes. Log that it is orthonormal, that the transpose carries a point back, and
   that swapping two axes makes the determinant -1.

   :::answer[Worked solution]{tests="orthonormal-frame determinant"}
   Add three small entities without a parent, `MarkerRight`, `MarkerUp` and `MarkerBack`, and attach `FrameDemo` to any
   entity, registered with `ST_SCRIPT_CLASS`. It logs every frame: read the first lines.

   ```cpp pseudocode
   class FrameDemo : public Script
   {
   public:
   	void OnUpdate(float deltaTime) override
   	{
   		const Entity ball = Scene::FindEntityByName("Ball");
   		const Entity coin = Scene::FindEntityByName("Coin");
   		if (!ball || !coin)
   			return;
   		const glm::vec3 from = ball.GetTransform().GetWorldPosition();
   		const glm::vec3 forward = glm::normalize(coin.GetTransform().GetWorldPosition() - from);
   		const glm::vec3 right = glm::normalize(glm::cross(forward, glm::vec3(0.0f, 1.0f, 0.0f)));
   		const glm::vec3 up = glm::cross(right, forward);
   		const glm::mat3 frame(right, up, -forward);
   		Scene::FindEntityByName("MarkerRight").GetTransform().SetTranslation(from + right);
   		Scene::FindEntityByName("MarkerUp").GetTransform().SetTranslation(from + up);
   		Scene::FindEntityByName("MarkerBack").GetTransform().SetTranslation(from - forward);
   		const glm::mat3 product = glm::transpose(frame) * frame;
   		Log::Info(product[0], " ", product[1], " ", product[2], " determinant ", glm::determinant(frame));
   		const glm::vec3 point = frame * glm::vec3(1.0f, 2.0f, 3.0f);
   		Log::Info(point, " back ", glm::transpose(frame) * point);
   		Log::Info("swapped determinant ", glm::determinant(glm::mat3(up, right, -forward)));
   	}
   };
   ```

   1. **Lines 15–17:** each marker sits one metre from the ball along one axis of the frame.
   2. **Line 19:** `Log::Info` takes no matrix, so the product goes in one column at a time: the identity, and the
      determinant 1.
   3. **Lines 21–22:** the transpose returns the point as (1, 2, 3), and swapping two columns gives the determinant -1.
   :::

## Where the book uses it

- [Mirrors and camera-relative space](../draw/mirrors-camera-relative.md) uses the determinant's sign and the cofactor
  matrix to draw mirrored objects with the right faces and normals.
- [Materials](../light/materials.md) uses the tangent frame to read normal maps.
- [Building bodies](../physics/building-bodies.md) uses decomposition to bake scale into collision shapes.
- [Skinning](../animation/skinning.md) carries the normals of bent models through the cofactor matrix.

## Further reading

- [3Blue1Brown, "Essence of linear algebra"](https://www.3blue1brown.com/topics/linear-algebra): the determinant, change
  of basis and the transpose as moving pictures; beginner.
- [The glm manual](https://github.com/g-truc/glm/blob/master/manual.md): `glm::transpose`, `glm::inverse` and
  `glm::determinant`; intermediate.

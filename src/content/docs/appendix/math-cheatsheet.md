---
id: appendix/math-cheatsheet
title: "Math cheat sheet"
description: "Every math symbol and formula the book uses, with how to read it, a small example and the page that teaches it."
kind: reference
size: M
tracks: []
needs: []
status: final
---

This page teaches nothing. It is a lookup for a reader who meets a symbol or a formula in another page and wants it read aloud, in one line, with numbers small enough to check by hand. Each row names the page that teaches the idea: follow that link when a row is new to you. The page that teaches an idea derives its formula, and no proof is repeated here.

The sheet has two tables. The first is how to read the symbols: a row has the symbol, how you say it, what it does, a small example and the teaching page. The second holds the formulas in the order of the `basics` pages: a row has the formula, its meaning with the units of its symbols, and the teaching page. Strata's own conventions (axes, handedness, units, matrix order, depth and color spaces) are in [Notation and conventions](../reference/notation.md), and the math types of the engine are in [Math in the engine](../core/math.md).

## How to read the symbols

Vertical bars would break a table, so a length is written with double bars, $\lVert v \rVert$, and a size of a number with single bars, $\lvert x \rvert$. Angles are in radians unless a row says degrees.

| Symbol | Read aloud | What it does | Example | Taught on |
| --- | --- | --- | --- | --- |
| $\sum$ | "the sum of" | Adds a list of terms, one for each value of the index under it. | $\sum_{i=1}^{3} i = 1 + 2 + 3 = 6$ | [Chance](../basics/math-probability.md) |
| $\int$ | "the integral of" | Adds up tiny pieces: the area under a curve. | $\int_0^2 3\,dt = 6$, a speed of 3 for 2 s | [Change over time](../basics/math-change.md) |
| $\Delta$ | "delta" | A step or a change of a quantity. | $\Delta t = 0.02$ s is one step of time | [Change over time](../basics/math-change.md) |
| $\dfrac{dx}{dt}$ | "d x over d t" | The rate of change of $x$ per unit of $t$. | $x = t^2$ gives $2t$, so 6 m/s at 3 s | [Change over time](../basics/math-change.md) |
| $a \cdot b$ | "a dot b" | The dot product of two vectors: a number. | $(1, 2, 3) \cdot (4, 0, 1) = 7$ | [Vectors](../basics/math-vectors.md) |
| $a \times b$ | "a cross b" | The cross product: a vector at a right angle to both. | $(1, 0, 0) \times (0, 1, 0) = (0, 0, 1)$ | [Vectors](../basics/math-vectors.md) |
| $\lVert v \rVert$ | "the length of v" | The length of a vector. | $\lVert (3, 4) \rVert = 5$ | [Vectors](../basics/math-vectors.md) |
| $\lvert x \rvert$ | "the size of x" | A number without its sign. | $\lvert -2.5 \rvert = 2.5$ | [Vectors](../basics/math-vectors.md) |
| $\hat{v}$ | "v hat" | The unit vector with the direction of $v$: its length is 1. | $\hat{v}$ of $(3, 4)$ is $(0.6, 0.8)$ | [Vectors](../basics/math-vectors.md) |
| $\theta$ | "theta" | An angle, often the one between two vectors, or a yaw or a polar angle. | $\theta = 90^\circ = \pi/2 \approx 1.571$ | [Vectors](../basics/math-vectors.md) |
| $\varphi$, $\phi$ | "phi" | A second angle: the azimuth around the up axis, or a pitch. | The azimuth 0 points along +X. | [Directions on a sphere](../basics/math-sphere.md), [Rotations](../basics/math-rotations.md) |
| $\omega$ | "omega" | A direction on the sphere, or an angular velocity. | $\int d\omega$ over the sphere is $4\pi$ | [Directions on a sphere](../basics/math-sphere.md), [Rotations](../basics/math-rotations.md) |
| $\pi$ | "pi" | The ratio of a circle's length to its width: 3.14159. | A half turn is $\pi$ radians. | [Vectors](../basics/math-vectors.md) |
| $e$, $\exp$ | "e", "exp of" | The number 2.71828, and $\exp(x) = e^x$: growth or decay by a steady fraction. | $\exp(-1) = 0.368$ | [Numbers](../basics/numbers.md) |
| $\log_b$, $\ln$ | "log base b", "natural log" | The power that gives the number: the undo of a power. $\ln$ has base $e$. | $\log_2 8 = 3$ | [Numbers](../basics/numbers.md) |
| $\sqrt{x}$ | "square root of x" | The number whose square is $x$. | $\sqrt{25} = 5$ | [Vectors](../basics/math-vectors.md) |
| $x^n$ | "x to the n" | $x$ multiplied by itself $n$ times. | $2^{10} = 1024$ | [Numbers](../basics/numbers.md) |
| $\in$ | "in" | A member of a set or a range. | $t \in [0, 1]$: $t$ lies from 0 to 1 | [Blending and smoothing](../basics/math-interpolation.md) |
| $\approx$ | "is about" | Nearly equal. | $\pi \approx 3.14$ | [Numbers](../basics/numbers.md) |
| $\le$, $\ge$ | "at most", "at least" | Compare two numbers, equal allowed. | $2 \le 2$ is true | [Geometry for engines](../basics/math-geometry.md) |
| $\infty$ | "infinity" | A value larger than any number. | $1/\infty$ is the limit 0 | [Cameras and projection](../basics/math-projection.md) |
| $M^T$ | "M transpose" | The matrix with rows and columns swapped. | The rows of $M^T$ are the columns of $M$. | [Bases](../basics/math-bases.md) |
| $M^{-1}$ | "M inverse" | The matrix that undoes $M$: $M^{-1} M$ is the identity. | If $M$ doubles y, $M^{-1}$ halves it. | [Matrices and transforms](../basics/math-matrices.md) |
| $q^{*}$ | "q conjugate" | The quaternion with the sign of its vector part flipped: the opposite turn. | $(w, x, y, z)^{*} = (w, -x, -y, -z)$ | [Rotations](../basics/math-rotations.md) |
| $E[X]$, $\mu$ | "expected value of X", "mu" | The mean of a random value. | For a die, $E[X] = 3.5$ | [Chance](../basics/math-probability.md) |
| $\sigma$, $\sigma^2$ | "sigma", "sigma squared" | The standard deviation and the variance: the spread around the mean. | Values 4, 5, 5, 6 have $\sigma^2 = 0.5$ | [Chance](../basics/math-probability.md) |
| $O(n)$ | "big O of n" | How the cost of a method grows with $n$ items, constants dropped. | $3n + 7$ steps is $O(n)$ | [Data structures](../basics/data-structures.md) |

The symbols $\partial$ and $\nabla$ (partial derivative, gradient) appear on no page of the book, so no row names them.

## Formulas

Read a row from left to right: the formula, then what each symbol is and its unit. A unit written "radians" means that the angle must not be in degrees.

### Numbers

The primer [Numbers](../basics/numbers.md) teaches this group.

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $n$ bits hold $2^n$ patterns, from 0 to $2^n - 1$ | $n$ is a count of bits. 8 bits hold 256 values, 0 to 255. | [Numbers](../basics/numbers.md) |
| $\text{value} = \sum d_k\, b^k$ | A number in base $b$ with digits $d_k$. In base 16, `0xC8` is $12 \times 16 + 8 = 200$. | [Numbers](../basics/numbers.md) |
| $x \ll n = x \cdot 2^n$ and $x \gg n = \lfloor x / 2^n \rfloor$ | Shifting the bits of an integer; $\lfloor x \rfloor$ rounds $x$ down. `5 << 2` is 20 and `100 >> 3` is 12. | [Numbers](../basics/numbers.md) |
| $\text{index} = h\ \&\ \text{mask}$ | A mask keeps the low bits of $h$. The mask `0xFFFFF` keeps 20 bits. | [Numbers](../basics/numbers.md) |
| $v = (-1)^s (1 + m / 2^{23})\, 2^{e - 127}$ | A 32-bit float: sign bit $s$, 8-bit exponent $e$, 23-bit significand $m$. | [Numbers](../basics/numbers.md) |
| gap near $x$ is about $x \cdot 2^{-23}$ | The spacing of floats grows with the value. Near 1 the gap is $2^{-23}$, about 0.00000012. | [Numbers](../basics/numbers.md) |
| $\log_b(xy) = \log_b x + \log_b y$ | A logarithm turns a product into a sum. $\log_2 1024 = 10$. | [Numbers](../basics/numbers.md) |
| stops $= \log_2 r$ | An exposure value (EV) stop is a factor of 2 in light. A ratio $r$ of 1024 is 10 stops. | [Numbers](../basics/numbers.md) |
| $\text{dB} = 10 \log_{10}(P_2 / P_1)$ | A decibel (dB) states a power ratio. A ratio of 100 is 20 dB. For amplitudes use 20 in place of 10. | [Numbers](../basics/numbers.md) |
| $v(t) = v_0\, e^{-kt}$ | A decay: $k$ is a rate per second and $t$ a time in seconds. With $k = 2$, at 0.5 s the value is 0.368 of its start. | [Numbers](../basics/numbers.md) |
| half-life $= \ln 2 / k$ | The time for a decay to halve, in seconds. With $k = 2$ it is 0.347 s. | [Numbers](../basics/numbers.md) |

### Data structures

The cost of a method is its growth in the number of items $n$. [Data structures](../basics/data-structures.md) and [Trees and graphs](../basics/trees-graphs.md) teach the rows.

| Operation | Cost | Taught on |
| --- | --- | --- |
| Read an array item by its index | $O(1)$ | [Data structures](../basics/data-structures.md) |
| Scan a list for a value | $O(n)$: 1,000,000 items take up to 1,000,000 steps | [Data structures](../basics/data-structures.md) |
| Binary search in a sorted array | $O(\log n)$: about 20 steps for 1,000,000 items | [Trees and graphs](../basics/trees-graphs.md) |
| Insert into the middle of a sorted array | $O(n)$, because later items shift | [Trees and graphs](../basics/trees-graphs.md) |
| Find a key in a hash map, on average | $O(1)$; the worst case, all keys in one bucket, is $O(n)$ | [Data structures](../basics/data-structures.md) |
| Add, remove or find in a sparse set | $O(1)$ | [Data structures](../basics/data-structures.md) |
| Find a key in a balanced search tree | $O(\log n)$ | [Trees and graphs](../basics/trees-graphs.md) |
| Push or pop a heap, and look at its smallest item | $O(\log n)$ and $O(1)$ | [Trees and graphs](../basics/trees-graphs.md) |
| Sort by comparing keys | $O(n \log n)$ | [Trees and graphs](../basics/trees-graphs.md) |
| Radix sort of keys with a fixed number of digits | $O(n)$ | [Trees and graphs](../basics/trees-graphs.md) |

### Vectors

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $\lVert v \rVert = \sqrt{v_x^2 + v_y^2 + v_z^2}$ | The length in the unit of the coordinates. $(1, 2, 2)$ has length 3. | [Vectors](../basics/math-vectors.md) |
| $\hat{v} = v / \lVert v \rVert$ | Normalizing keeps the direction and sets the length to 1. It fails for the zero vector, which has no direction. | [Vectors](../basics/math-vectors.md) |
| $\text{radians} = \text{degrees} \cdot \pi / 180$ | A conversion. 90 degrees is 1.571 radians. | [Vectors](../basics/math-vectors.md) |
| $a \cdot b = a_x b_x + a_y b_y + a_z b_z = \lVert a \rVert \lVert b \rVert \cos\theta$ | The dot product, a number. It is 0 at a right angle and negative past it. | [Vectors](../basics/math-vectors.md) |
| $\theta = \arccos(\hat{a} \cdot \hat{b})$ | The angle between two directions, in radians. For $(1, 0)$ and $(0.6, 0.8)$ it is 0.927. | [Vectors](../basics/math-vectors.md) |
| $a \times b = (a_y b_z - a_z b_y,\ a_z b_x - a_x b_z,\ a_x b_y - a_y b_x)$ | A vector at a right angle to $a$ and $b$. Its length is $\lVert a \rVert \lVert b \rVert \sin\theta$. | [Vectors](../basics/math-vectors.md) |
| $\theta = \operatorname{atan2}(y, x)$ | The angle of the point $(x, y)$ from the +X axis, in radians, in the full turn. $\operatorname{atan2}(1, 1) = 0.785$. | [Vectors](../basics/math-vectors.md) |

### Matrices

Strata's matrix order and axes are in [Notation and conventions](../reference/notation.md).

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $M = T\, R\, S$ | The transform of an object: scale first, then rotate, then translate. | [Matrices and transforms](../basics/math-matrices.md) |
| $p' = M p$ | A matrix times a vector. The columns of $M$ are where the axes go. | [Matrices and transforms](../basics/math-matrices.md) |
| $M_{\text{world}} = M_{\text{parent}}\, M_{\text{local}}$ | A child's world transform: the parent's times its own. Order matters: swapping the two gives another result. | [Matrices and transforms](../basics/math-matrices.md) |
| $p = R^T (p' - t)$ | The inverse of a rigid transform, one that only rotates by $R$ and moves by $t$: move back by $t$, then turn back by $R^T$. It needs no general inversion. | [Matrices and transforms](../basics/math-matrices.md) |

### Bases, determinants and normals

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $R^{-1} = R^T$ | The inverse of a rotation, whose columns are an orthonormal basis, is its transpose. | [Bases](../basics/math-bases.md) |
| $p_{\text{local}} = B^T p_{\text{world}}$ | Coordinates in a frame whose orthonormal axes are the columns of $B$. Tangent space is such a frame. | [Bases](../basics/math-bases.md) |
| $\det M$ | The factor by which $M$ scales volume. A negative sign means $M$ mirrors. A scale of $(2, 1, 1)$ has $\det = 2$. | [Bases](../basics/math-bases.md) |
| $n' = (M^{-1})^T n$ | A normal after a transform with a non-uniform scale: the inverse transpose. The cofactor matrix, $\det(M)\,(M^{-1})^T$, differs only by a positive or negative factor. | [Bases](../basics/math-bases.md) |
| $s_x = \lVert \text{first column} \rVert$ and the translation is the last column | Splitting $M$ into parts: the scale is the length of each column, the rotation is the columns divided by their scales. A negative $\det$ makes one scale negative. | [Bases](../basics/math-bases.md) |

### Projection

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $(x, y, z) = (x_c, y_c, z_c) / w_c$ | The perspective divide: clip coordinates become normalized device coordinates, x and y from -1 to 1 and depth from 0 to 1. | [Cameras and projection](../basics/math-projection.md) |
| $1 / (a \tan(\theta/2))$ and $1 / \tan(\theta/2)$ | The scale of x and of y in a perspective matrix. $\theta$ is the vertical field of view in radians and $a$ the aspect ratio. | [Cameras and projection](../basics/math-projection.md) |
| $z_{\text{depth}} = \dfrac{n\,(f - d)}{d\,(f - n)}$ | Reversed depth for a distance $d$ from the camera, with the near distance $n$ and the far distance $f$. The near plane stores 1 and the far plane 0. | [Cameras and projection](../basics/math-projection.md) |

### Rotations

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $q = (\cos\tfrac{\theta}{2},\ \sin\tfrac{\theta}{2}\, \hat{a})$ | The quaternion of a turn by $\theta$ radians around the unit axis $\hat{a}$. A turn of 180 degrees around Y gives $(0, 0, 1, 0)$. | [Rotations](../basics/math-rotations.md) |
| $v' = q\, v\, q^{*}$ | Turning a vector: the sandwich of the quaternion, the vector and the conjugate. | [Rotations](../basics/math-rotations.md) |
| $q_{\text{total}} = q_2\, q_1$ | Two turns combined. The rightmost turn acts first. | [Rotations](../basics/math-rotations.md) |
| $\text{slerp}(a, b, t) = \dfrac{\sin((1-t)\Omega)}{\sin\Omega}\, a + \dfrac{\sin(t\Omega)}{\sin\Omega}\, b$ | A blend at an even speed along the shorter arc. $\Omega$ is the angle between $a$ and $b$ and $t$ lies from 0 to 1. | [Rotations](../basics/math-rotations.md) |

### Geometry

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $p(t) = o + t\, d$ | A ray from the origin $o$ in the direction $d$. For a unit $d$, $t$ is a distance. | [Geometry for engines](../basics/math-geometry.md) |
| $s = n \cdot p - c$ | The signed distance of a point $p$ from the plane with the unit normal $n$ and offset $c$. Positive means the side $n$ points to. | [Geometry for engines](../basics/math-geometry.md) |
| $t = (c - n \cdot o) / (n \cdot d)$ | Where a ray meets a plane. A zero divisor means the ray is parallel; a negative $t$ is behind the origin. | [Geometry for engines](../basics/math-geometry.md) |
| $t = -b \pm \sqrt{b^2 - k}$ with $b = d \cdot (o - c)$ and $k = \lVert o - c \rVert^2 - r^2$ | A ray with a unit $d$ against a sphere of center $c$ and radius $r$. The sign $\pm$ gives two answers, the entry and the exit. A negative value under the root means a miss. | [Geometry for engines](../basics/math-geometry.md) |
| $t_{\text{enter}} = \max(\text{near } t \text{ per axis})$, $t_{\text{exit}} = \min(\text{far } t \text{ per axis})$ | A ray against a box by slabs. It hits when $t_{\text{enter}} \le t_{\text{exit}}$. | [Geometry for engines](../basics/math-geometry.md) |

### Change over time

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $x_{n+1} = x_n + v_n \Delta t$, then $v_{n+1} = v_n + a \Delta t$ | The explicit Euler step: the position uses the old velocity. $x$ in metres, $v$ in m/s, $a$ in m/s², $\Delta t$ in seconds. | [Change over time](../basics/math-change.md) |
| $v_{n+1} = v_n + a \Delta t$, then $x_{n+1} = x_n + v_{n+1} \Delta t$ | The semi-implicit Euler step: the position uses the new velocity. A large step still has an error, but it does not explode as quickly. | [Change over time](../basics/math-change.md) |
| $F = m\, a$ | Newton's second law. $F$ in newtons, $m$ in kilograms. A force of 10 N on 2 kg gives 5 m/s². | [Change over time](../basics/math-change.md) |
| $J = F\, \Delta t = m\, \Delta v$ | An impulse in newton seconds. It changes the velocity by $J / m$. | [Change over time](../basics/math-change.md) |

### Interpolation

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $\text{lerp}(a, b, t) = a + t\,(b - a)$ | A blend. $t = 0$ gives $a$ and $t = 1$ gives $b$. `lerp(10, 20, 0.25)` is 12.5. | [Blending and smoothing](../basics/math-interpolation.md) |
| $t = (x - a) / (b - a)$ | The inverse lerp: the weight of $x$ in the range $a$ to $b$. | [Blending and smoothing](../basics/math-interpolation.md) |
| $\text{lerp}(c, d, \text{inverse lerp}(a, b, x))$ | A remap from the range $a$ to $b$ to the range $c$ to $d$. | [Blending and smoothing](../basics/math-interpolation.md) |
| $3t^2 - 2t^3$ | Smoothstep. It leaves 0 and arrives at 1 slowly. At $t = 0.25$ it gives 0.156. | [Blending and smoothing](../basics/math-interpolation.md) |
| $v \leftarrow v + (\text{target} - v)\,(1 - e^{-k\,\Delta t})$ | Smoothing at any frame rate; $\leftarrow$ reads "becomes". $k$ is a rate per second. With $k = 4$ and 60 frames per second the weight is 0.0645 each frame. | [Blending and smoothing](../basics/math-interpolation.md) |

### Color

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $s = 12.92\,c$ for $c \le 0.0031308$, else $s = 1.055\,c^{1/2.4} - 0.055$ | The sRGB encoding of a linear channel $c$ to a stored value $s$, both from 0 to 1. Light 0.18 is stored as 0.461. | [Color](../basics/color.md) |
| $c = s / 12.92$ for $s \le 0.04045$, else $c = ((s + 0.055)/1.055)^{2.4}$ | The decoding, back to linear light. A stored 0.5 is 0.214 of the light of white. | [Color](../basics/color.md) |
| $Y = 0.2126\,r + 0.7152\,g + 0.0722\,b$ | The luminance of a linear color. The weights add up to 1. | [Color](../basics/color.md) |

### Signals

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $f_{N} = f_s / 2$ | The Nyquist limit: the highest frequency that $f_s$ samples a second can hold. At 10 Hz it is 5 Hz. | [Signals](../basics/signals.md) |
| box: $\tfrac13, \tfrac13, \tfrac13$; tent: $\tfrac14, \tfrac12, \tfrac14$ | Filter weights over neighbors. The weights add up to 1, so a flat area keeps its value. | [Signals](../basics/signals.md) |

### Chance

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $E[X] = \sum x_i\, p_i$ | The expected value: each value times its probability. A die gives 3.5. | [Chance](../basics/math-probability.md) |
| $\sigma^2 = \frac{1}{n} \sum (x_i - \mu)^2$ and $\sigma = \sqrt{\sigma^2}$ | The variance and the standard deviation, in the units of $x$. | [Chance](../basics/math-probability.md) |
| $\int f \approx \frac{1}{N} \sum f(x_i) / p(x_i)$ | The Monte Carlo estimate from $N$ random samples $x_i$ with the density $p$. For a uniform density on $[a, b]$, $p = 1/(b - a)$. | [Chance](../basics/math-probability.md) |

### The sphere

| Formula | Meaning and units | Taught on |
| --- | --- | --- |
| $\Omega = A / r^2$ | The solid angle in steradians of a patch of area $A$ on a sphere of radius $r$. The whole sphere is $4\pi$ and a hemisphere $2\pi$. | [Directions on a sphere](../basics/math-sphere.md) |
| $d = (\sin\theta\cos\varphi,\ \cos\theta,\ \sin\theta\sin\varphi)$ | A direction from the polar angle $\theta$ counted from +Y and the azimuth $\varphi$ counted from +X toward +Z, both in radians. | [Directions on a sphere](../basics/math-sphere.md) |
| $d\omega = \sin\theta\, d\theta\, d\varphi$ | The solid angle of a tiny piece. Over the hemisphere, $\int \cos\theta\, d\omega = \pi$. | [Directions on a sphere](../basics/math-sphere.md) |
| $Y_0 = 0.282095$, $Y_1 = 0.488603\,y$, $Y_2 = 0.488603\,z$, $Y_3 = 0.488603\,x$ | The first four spherical harmonics patterns, bands 0 and 1, for a unit direction $(x, y, z)$. | [Directions on a sphere](../basics/math-sphere.md) |
| $e = n.xy / (\lvert n_x \rvert + \lvert n_y \rvert + \lvert n_z \rvert)$ | The first step of octahedral encoding: divide by the sum of sizes and keep the x and y parts, $n.xy$. When $n_z < 0$, a fold follows. | [Directions on a sphere](../basics/math-sphere.md) |

## Where it lives in Strata

- `Strata/src/Strata/Math/Math.h`: the conventions comment that [Notation and conventions](../reference/notation.md) collects, and the math the engine shares.
- `Strata/shaders/Include/Scene.slang`: the functions `OctahedralEncode` and `OctahedralDecode`, which the last row of the sphere table follows.
- `Strata/shaders/Include/SphericalHarmonics.slang`: the spherical harmonics weights of the sphere table, 0.282095 and 0.488603.

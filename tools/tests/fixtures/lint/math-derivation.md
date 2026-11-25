A derivation of more than three steps goes in a :::derivation box (a warning): more than four display formulas in one
level-2 section outside such boxes (style.md §4). Reported at the section's heading.

%%% pass core/time
## Four formulas

$x = 1$ and $y = 2$ are the values.

$$
x = 1
$$

$x$ is one.

$$
x = 1
$$

$x$ is one.

:::derivation
$$
x = 1
$$

$x$ is one.

$$
x = 1
$$

$x$ is one.
:::

$$
x = 1
$$

$x$ is one.

$$
y = 2
$$

$y$ is two.

%%% fail core/time 1
## Five formulas

$x$ is one.

$$
x = 1
$$

It is one.

$$
x = 1
$$

It is one.

$$
x = 1
$$

It is one.

$$
x = 1
$$

It is one.

$$
x = 1
$$

It is one.

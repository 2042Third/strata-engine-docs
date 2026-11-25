Every single letter, Greek letter or subscripted symbol of a display formula that the page has not named before stands
as inline math in the block right after the formula (style.md §4). Text, units and function names are no symbols.

%%% pass core/time
The distance is the speed times the time.

$$
d = v \, \Delta t + \text{offset}_0 \cdot \sin(x_i)
$$

Read it as "d equals v times delta t". $d$ is the distance, $v$ the speed, $\Delta t$ the delta time and $x_i$ the
angle.

$$
d = 2v
$$

The same symbols, named before.

%%% fail core/time 3 11
The distance is the speed times the time.

$$
d = v \, \Delta t
$$

$d$ is the distance.

The next formula:

$$
a_{n+1} = \alpha \, a_n
$$

## Later

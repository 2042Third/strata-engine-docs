On pages of track G, a number followed by "ms" has "%" in the same sentence: its share of a frame at 60 frames per
second (style.md §13). make/scenes is on G; core/time is not.

%%% pass make/scenes
The step takes 2.1 ms, 13 % of a frame at 60 frames per second, and a slower GPU takes longer.

%%% pass core/time
The step takes 2.1 ms.

%%% fail make/scenes 1 2
The step takes 2.1 ms.
It waits 16ms. Then 13 % of the frame is left.

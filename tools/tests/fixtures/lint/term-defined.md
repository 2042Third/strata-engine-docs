On its home page, a term is defined in bold somewhere on the page, as a glossary name or alias (style.md §3). gpu/frame is
the home of "render pass" only. A home page that never uses its term is reported on its first line.

%%% pass gpu/frame
## How a frame is drawn

A **render pass** is one step of drawing. Each render pass reads the last one.

%%% pass gpu/frame
Each render pass reads the last one. A **render pass** is one step of drawing: the bold definition may stand anywhere on
the home page (rulings-11.md, R54).

%%% pass gpu/frame
::::test-out
1. What does a render pass read?

   :::answer{tests="x"}
   The last one.
   :::
::::

| Step | What |
| --- | --- |
| render pass | draws |

A **render pass** is one step of drawing.

%%% fail gpu/frame 13
::::test-out
1. What does a render pass read?

   :::answer{tests="x"}
   The last one.
   :::
::::

| Step | What |
| --- | --- |
| render pass | draws |

The render pass is used here first outside the box and the table, and the page never defines it in bold.

%%% fail gpu/frame @1
The frame is drawn in steps.

%%% pass basics/tools
A **clip** is a recorded motion: "Clip (animation)" is defined by its name before the parenthesis.

A **spline** is a smooth curve through points.

%%% pass core/map
A **spline** is a path an entity follows: of the two entries named "spline", the one homed on this page is defined.

%%% fail draw/culling 1 @1
The camera of a page is one everyday word, but on its home page it is defined in bold all the same.

The first use of a term on a page is its definition, a :term mark or a forward mention: a use inside a link to the
term's home page (style.md §3). Later uses are plain words; terms marked known need no mark; a term in bold on a page
that is not its home is a UI label. world/ecs needs core/time, the home of "fixed step".

%%% pass world/ecs
The :term[fixed steps]{id=fixed-step} run. Every fixed step is a slice. The [render pass](../gpu/frame.md), one step
of drawing a frame, comes later. A folder holds files. Open **Accumulator**, then read the :term[accumulator]{id=accumulator}.

%%% fail world/ecs 1 2 3
The fixed step runs. A :term[fixed step]{id=fixed-step} is a slice.
The accumulator holds time.
A :term[pass]{id=no-such-entry} draws.

%%% pass world/ecs
A term that is one everyday word of the common list needs no mark at an unmarked use (rulings-11.md, R53): the
camera follows the player, and the cameras of a split screen follow two. A clip of film runs; "Clip (animation)" is
matched by "clip". A :term[camera]{id=camera} mark stays a mark.

%%% fail world/ecs 1
Every spline bends: "Spline (path)" and "Spline (curve)" are matched by the name before the parenthesis.

%%% pass world/ecs
Only a term whose home is the page's Needs closure asks for a mark (rulings-11.md, R54): the occluder of draw/culling
and the render pass of gpu/frame are neither marked nor linked.

%%% pass world/ecs
::::test-out
1. Does the accumulator grow?

   :::answer{tests="x"}
   Yes.
   :::
::::

> The accumulator of a quote is someone else's word.

The **accumulator** is the time no step has used yet. The accumulator grows.

The [time page](../core/time.md) shows how a fixed step slices the frame.

## Further reading

- [The delta time of Glenn](https://www.example.com/): measured steps; beginner.

%%% fail world/ecs 3
> The accumulator of a quote is someone else's word.

The accumulator outside the quote is the first use that asks for the mark.

%%% fail world/ecs 1
A mark inside link text is refused, as the build refuses it: [the :term[fixed step]{id=fixed-step} chapter](../gpu/frame.md).

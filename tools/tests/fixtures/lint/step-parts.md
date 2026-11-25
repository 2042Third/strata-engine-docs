Every numbered step of a tutorial, and of a how-to on track G or B, holds "**You should see:**" and "**If you do not
see it:**" (style.md §10). make/first-script is a tutorial; make/script-loop a how-to on G and B; start/coming-from a
how-to on G and E; core/map a concept page. Callouts after a fence are no steps.

%%% pass make/first-script
## What you will make

A ball that rolls.

## What you need

1. A project.

## Make the ball roll

1. Add a ball.

   **You should see:** a ball.

   **If you do not see it:** press **Undo**.

2. Play.

   The sketch:

   ```cpp sketch="make-first-script-ten.cpp"
   int a1;
   int a2;
   int a3;
   int a4;
   int a5;
   int a6;
   int a7;
   int a8;
   int a9;
   int a10;
   ```

   1. **Line 1:** a value.

   **You should see:** the ball rolls.

   **If you do not see it:** build the scripts.

## Summary

1. A list in the strip is no step.

%%% pass core/map
1. A numbered list on a concept page.

%%% fail make/first-script 7 9
## What you will make

A ball.

## Make the ball roll

1. Add a ball.

2. Play. You should see the ball roll.

   **You should see:** it rolls.

%%% fail make/script-loop 1
1. Open the script.

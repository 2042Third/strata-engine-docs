Nothing is copied from the sources: a run of ten or more words (lowercased, punctuation removed) that also stands in
plan/inventory/*.md, or in AGENTS.md, Docs/DeveloperGuide.md or Docs/Manual/*.md at the pin (style.md §2.2). Block
quotes and code are exempt. The sources of these cases are in tests/test_lint.py (c_EngineFiles, c_Inventory).

%%% pass core/time
The main thread owns the scene, input and scripts of the game.

> The main thread owns the scene, input, scripts and rendering submission in every frame of the game.
> — AGENTS.md

This document is not one of the sources, so its ten words in a row may be used freely by pages.

%%% fail core/time 1 3 5 7
In Strata the MAIN thread owns the scene; input, scripts and rendering submission happen in every frame.

Before changing it, read the guide's section for the area you work on, before changing it.

The camera follows the player and keeps the horizon level while the game runs.

The fixed step accumulator holds the time that the frames produced.

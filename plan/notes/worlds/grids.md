# Notes: worlds/grids

## New terms

None proposed. The page defines cell key, grid origin, index and world asset (glossary homes) in bold.

## Since

0.8.0: the World module is part of the wave that ends in release 0.8.0 (the page's subject has no older tag); not checked against the release notes.

## Requests

- Hosts for Further reading (not linked, cited by name): docs.unrealengine.com or dev.epicgames.com (Unreal Engine documentation, World Partition and Level Streaming Volumes). No link is placed.
- Figures: none. The two figures of the brief (layers over one ground; the 64-bit key) are carried by the Mermaid map, the worked example with hexadecimal fields and the key walk-through; a drawn figure of two grids over one ground and of the key's bit fields would help and has no file yet.

## Not verified

- That a sub-scene whose entity IDs already exist fails to load (inventory worlds-runtime:440): the page states only that the cook fails and names shared IDs (`WorldCook.h` comment).
- The 45-cell count of the Island example is computed by hand from `WorldGrid::Distance` with a player at a cell's centre, not from the streamer's own rule (`<=` or `<` at the boundary does not change it).
- The Unreal Engine claims of the alternatives table and the Ericson reference are from general knowledge of the cited sources, not checked here.
- The `names` check rejected nothing in the final run; `World.Asset` is written as plain text in prose.

## Findings not applied

The brief lists no open findings. Left out by size: the table of every `.stworld` key (reference/worlds-runtime), and the mistake of "cells as points" and "float grid math" as separate sections (float math is covered in a sentence of the grid arithmetic section, cells as squares in the contract).

## Clerk

- Nothing to admit.
- Hosts: none admitted; the sources are cited without links, so no host is needed (docs.unrealengine.com is not on the list and is the planner's).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

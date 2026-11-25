The front matter can be read, and holds only the book's keys and Starlight's display keys (style.md §6.1;
tools/pages.py's checks).

%%% pass core/time tableOfContents=false
A page.

%%% fail core/time key:colour colour=red
A page.

%%% fail core/time key:slug slug=time
A page.

%%% fail core/time @3
---
id: core/time
title: Time: delta time and the fixed step
---
A page.

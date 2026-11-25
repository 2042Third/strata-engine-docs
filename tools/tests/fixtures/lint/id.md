The id is the file's path under src/content/docs/ without .md, and the page is a row of the outline (style.md §6.1,
site.md O1 and O7; tools/pages.py's checks).

%%% pass core/time
A page.

%%% fail core/time key:id id=core/other
A page.

%%% fail core/extra @1
---
id: core/extra
title: "A page that is no row"
description: "A page."
status: draft
---
A page.

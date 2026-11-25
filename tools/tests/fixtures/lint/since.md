since is a release from 0.3.0 to the pin's, required on concept, internals, tutorial and how-to pages of parts 1 and
3 to 21 and absent elsewhere (style.md §6.1). core/time is an internals page of part 3; start/welcome a concept page
of part 0. An absent key is reported on the front matter's first line.

%%% pass core/time
A page.

%%% pass start/welcome
A page.

%%% fail core/time @1 since=
A page.

%%% fail core/time key:since since=0.9.0
A page.

%%% fail start/welcome key:since since=0.3.0
A page.

The page's prose words fit its size: S 600 to 2,250, M 2,251 to 4,000, L 4,001 to 6,500, XL 6,501 to 10,000 (style.md
§2.2); the front matter's size is the row's (§6.1). The fit is reported on the page's first line. appendix/history is
S and core/time L in the small book.

%%% pass appendix/history
%%repeat 200 The ball rolls.%%

%%% pass core/time
%%repeat 1334 The ball rolls.%%

%%% fail core/time @1
A short page.

%%% fail core/time @1 key:size size=S
A short page.

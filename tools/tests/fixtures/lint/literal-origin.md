The origin is written in site.json only; deploy/README.md, the repository's README.md and plan/ may name it too
(rulings 6, R24). Any case of the host counts. Without a site.json the rule is not run and lint says so.

%%% pass core/time
A page.
%%% file site.json
{"base": "/strata-engine-docs", "origin": "https://books.example.org", "copyright": {"holder": "The owner", "year": 2026}}
%%% file README.md
The book is served at https://books.example.org/strata-engine-docs/.
%%% file deploy/README.md
Serve it as https://books.example.org/strata-engine-docs/.
%%% file plan/notes.md
The address is https://books.example.org.
%%% file src/lib/other.mjs
export const placeholder = 'https://example.com';

%%% fail core/time 2 src/lib/where.mjs:2
A page.
The book lives at https://books.example.org/strata-engine-docs/.
%%% file site.json
{"base": "/strata-engine-docs", "origin": "https://books.example.org", "copyright": {"holder": "The owner", "year": 2026}}
%%% file src/lib/where.mjs
// Where the book is served.
export const origin = 'https://Books.Example.org';

No .mdx file under src/content: the book is plain Markdown (site.md, "The Markdown the build reads"; the spike's rule).

%%% pass core/time
A page.
%%% file src/content/docs/world/notes.md.txt
Not a page.

%%% fail core/time src/content/docs/world/extra.mdx:1
A page.
%%% file src/content/docs/world/extra.mdx
# A component page

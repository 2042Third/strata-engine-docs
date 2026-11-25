# Part review: make/large-worlds

- wrong: the export step's command was `project.export` with `{}`, but `directory` is required at the pin; it now passes an absolute path outside the project, as make/export does.
- unclear: the export step's editor tab said "Choose the export command in the editor"; it now names **File ▸ Export Game...** and **Export**.

Checked without change: `world.create`'s four default layers (64 m cells, four cells of distance, only the first loading before the start), the Inspector's cell line, the Hierarchy's `l:` and `cell:` searches, the cook's outcome line and its failure on shared IDs, the StreamingSource defaults, the Explorer and Teleport excerpts and their callouts, and the 20 km and 50 km precision figures.

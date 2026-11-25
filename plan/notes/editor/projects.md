# Notes: editor/projects

## New terms

- project migration: the one-time upgrade a project saved by 0.5.0 or older gets when it opens: its scenes' collision layers are merged into the project's table and the file is written as version 3. Home: editor/projects. Aliases: migration.
- recent projects: the list of the projects the editor opened last, at most 12, kept in a file every editor of the user shares. Home: editor/projects. Aliases: recent list.
- preferences: the person's own settings, kept for every project in `Preferences.json` in the user's data folder. Home: editor/projects. Aliases: preferences store.

## Requests

- No figures file: both pictures are Mermaid diagrams.

## Not verified

- A second client can send `scene.loadStatus` while `project.openSample` waits (the example); the guide says requests run on the main thread each frame and deferred ones answer later, no test read.
- The alternatives table's "Who uses it" column states general kinds of tools, not cited engines.
- The first Further reading entry (a book chapter on game loops) was not read for this page.

## Findings not applied

- None: the brief lists no open findings.

## Since

- 0.3.0: the subject (opening projects and scenes) is older than the first tag; the background open's own release was not checked.

## Clerk

- Admitted the terms project migration (alias migration), recent projects (alias recent list) and preferences, homed here; the alias preferences store is not on the page and was left out.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

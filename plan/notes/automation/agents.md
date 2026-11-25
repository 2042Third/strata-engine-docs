# Notes: automation/agents

## New terms

None. The page defines automation, AI agent, tool and tokens (LLM), which the glossary homes here.

## Requests

- Hosts for Further reading entries now cited without a link: dev.epicgames.com (Unreal Python and Remote Control API), chromedevtools.github.io (DevTools protocol), microsoft.github.io (Language Server Protocol).
- Figure: none; both diagrams are Mermaid.

## Since

0.3.0: the command registry, StrataCLI and the editor's JSON-RPC server exist from the first tag (automation inventory 2.1).

## Not verified

- Claims about Unity, Godot, Unreal, Blender and browser tools (batch flags, Remote Control API) come from the brief, not from the pin.
- "A call takes about a tenth of a second" comes from the inventory (2.14), not from a measurement.
- Clients cap at "some 128" tools: Docs/DeveloperGuide.md "MCP toolsets" at the pin says so.

## Findings not applied

None: the brief lists no open findings.

## Tutorial run

- exercise-1: the stage passes through StrataCLI (round 1 and 2), but its reader's copy cannot: tools/tutorials.py runs
  reader copies as `StrataEditor --no-gpu --no-automation --commands` (plan/pipelines.md "Driving editors"), and an editor
  without automation answers `editor.status {sections: ["automation", ...]}` with "unknown section 'automation'". The
  exercise teaches the automation section an agent sees over StrataCLI, so the file keeps it; the reader copy needs a
  tool or format decision (a runner that serves automation in its private session folder, or a way to leave a command
  out of the reader's copy). The page now says that an editor started with `--no-automation` refuses the section.
- Re-run at v0.8.0 (319075e3): the same. The stage passes through StrataCLI with every check; the reader's copy fails
  with "unknown section 'automation'", because 0.8.0 still registers the section only when automation starts
  (EditorStateCommands.cpp:775). The file and the page stay; the tool or format decision above is still open (it is
  tools/tutorials.py's run_reader_copy, which no page runner may change).
- Strengthened with the answer's values: project Tetris, scene Main, play state Edit, automation running with
  StrataCLI among its clients, sceneLoad null, errors.unread 0. The answer said `errors.unread` "falls to 0": the sample
  opens with none, so it now says it is 0 (and was before); it also names the last `editor.status` call.
- Final runs (step 15): the pin-build run in the stamp was current; the official v0.8.0 package run passes as written,
  reader's copies included (they now run in the engine's runner, so the reader-copy failure above no longer occurs).
  `tutorials.py check --release` finds nothing for the page.

## Engine

- `editor.status` lists `automation` among its sections in its parameter schema without a condition, but an editor
  started with `--no-automation` rejects it as an unknown section (EditorStateCommands.cpp:767; the provider registers
  only in EditorAutomation::Start). Still so at v0.8.0 (EditorStateCommands.cpp:763-782).

## Clerk

- Nothing to admit.
- Not admitted: chromedevtools.github.io (its front page answered 404 to one fetch) and dev.epicgames.com (no answer to one fetch in earlier batches); left for the planner. Admitted to external-hosts.txt: microsoft.github.io (Microsoft's own GitHub pages; its front page names it).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

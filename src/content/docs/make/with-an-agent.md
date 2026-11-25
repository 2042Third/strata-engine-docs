---
id: make/with-an-agent
title: "Making a game with an AI agent"
description: "Connect an AI agent to the editor, watch it place props, take its work back, keep its session as a test and learn the guide for a whole game."
kind: tutorial
size: L
tracks: [G]
needs: [make/commands]
time: 75
learn:
  - id: connect
    text: run the launcher's line in the right folder so that an agent sees Strata's tools
  - id: toolsets
    text: explain which tools an agent has at first and how it gets more
  - id: activity
    text: find who ran each command in the Activity panel and take a session back with Undo to here
  - id: safety
    text: predict what happens when an agent opens a scene over changes you have not saved
  - id: regression
    text: export an agent's session as a command script and run it on a fresh copy
since: 0.3.0
status: final
---

## What you will make

You will connect an artificial intelligence (AI) agent to the editor, ask it to place props in a level, and watch it work. An **agent** is a program driven by a language model that acts through tools: it reads your request, chooses a tool, reads the answer and chooses the next tool. You stay in charge: you see every step, you undo what you dislike, and you keep the session as a test.

::figure{id=result}

Strata gives an agent the same commands the menus run. A command such as `asset.place` has a name, parameters and a result, and the editor does not care who sends it. An agent reaches the commands through **Model Context Protocol** (MCP), a standard way for an agent program to list and call the tools of another program. The picture shows the path of one request.

```mermaid caption="The path of one request: the agent talks to a small helper program, the helper talks to the editor over a private local connection, and the editor runs the same command a menu would run." alt="Four boxes in a row joined by arrows: the agent, the helper program that speaks the protocol, the editor's local connection with a secret token, and the editor's commands. A fifth box for the menus also points into the editor's commands."
flowchart LR
	A["AI agent"] -->|"MCP on the standard streams"| B["StrataCLI mcp"]
	B -->|"JSON-RPC on loopback, with a token"| C["Editor connection"]
	C --> D["Editor commands"]
	M["Menus and panels"] --> D
	D --> J["Activity journal"]
```

The helper, `StrataCLI mcp`, is the program from [Running commands from the terminal](commands.md), now serving an agent instead of you. The **loopback** connection never leaves your computer, and a secret token keeps other programs out. Every command that arrives, from you or from the agent, lands in the **activity journal**, the editor's record of who ran what.

## What you need

- **An agent program that speaks MCP.** This page uses Claude Code, whose command line the launcher shows. It needs a paid plan or an account with usage billing. Another MCP client works too: give it a server named `strata` that runs `StrataCLI mcp`. The launcher shows a line only for Claude Code.
- **The starting checkpoint**, a project from the Basic 3D template, saved, with three props in `Prefabs/`: `Crate`, `Barrel` and `Lamp`. Each is a :term[prefab]{id=prefab-make} made from the engine's built-in cube, so no outside file needs a license. You can download it at the first checkpoint's picture.
- **A copy of the Tetris sample** for the last section: the launcher offers one under **Open Sample...**.
- **The shipped skills.** The release archive holds a `Skills/` folder with three guides for agents. You copy them in the second section.
- **Time:** about 75 minutes.

Commands in this page run through `StrataCLI`, as in [Running commands from the terminal](commands.md). Without an agent program, run the calls of each **With a command** tab yourself: only the agent's own answers stay unseen. An agent does not act the same way twice, so the checkpoints fix what must be true (the three props exist, the journal has its rows), not where the props stand.

## Connect the agent

The launcher has a card, **Connect an AI agent**, that shows the exact line for Claude Code. In this section you copy it, run it in the right folder and see the editor notice the agent.

:::::steps

1. Open the launcher without a project, and find the card **Connect an AI agent**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Start the editor. The launcher is its first window. Find the card **Connect an AI agent**, with a status pill at the right of its heading.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The command below starts the editor on the project's folder. A project that is open shows no launcher, so close it first if you want the card.

   ```sh
   StrataCLI launch --project "<folder of the starting project>"
   ```

   The editor opens the project, and you skip the card in the next step. The line it shows is `claude mcp add strata -- "<StrataCLI>" mcp`, with the path of your `StrataCLI` in place of the angle brackets.
   :::
   ::::

   **You should see:** a line that starts with `claude mcp add strata` and a pill such as `Ready on port 41234`, where the number is yours.

   **If you do not see it:** a pill **Automation is off** means the editor started with `--no-automation`; start it again without that option. A warning that `StrataCLI` is not next to the editor means a build without it, and the release archive always holds it.

2. Copy the line and run it in the folder where the agent will start.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the copy button beside the line in the card. Open a terminal in the folder of the starting project and paste the line there.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The line adds a server named `strata` to Claude Code. The part after the two dashes is the program Claude Code starts, and `mcp` makes `StrataCLI` serve the protocol instead of running one command.

   ```sh
   claude mcp add strata -- "<StrataCLI>" mcp
   ```

   Claude Code answers that it added the server. To have the server in every folder, put `--scope user` before `strata`.
   :::
   ::::

   **You should see:** Claude Code confirms that it added the server `strata`.

   **If you do not see it:** nothing is wrong yet. The next step checks the result.

3. Start the agent in the same folder and check that it lists Strata.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the starting project in the editor from the launcher's list. In the terminal, start `claude`, then type `/mcp` inside it.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The first command asks Claude Code which servers it knows, and the answer should name `strata` as connected.

   ```sh
   claude mcp list
   ```

   If the list shows `strata`, start `claude` in the same folder.
   :::
   ::::

   **You should see:** the server `strata` in the list, and in the editor's status bar a pill that reads **Agent connected** with the name your agent gives itself.

   **If you do not see it:** Claude Code keeps a server only for the folder where you added it, a rule called local scope. A line pasted in one folder is therefore invisible when you start `claude` in another. Run `claude mcp list` in the folder where you started the agent. If `strata` is missing there, add the line again in that folder, or add it with `--scope user`.

4. Ask the agent which editor it sees.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type to the agent: "Which Strata editor are you connected to, and what is open in it?"
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent answers the prompt by calling `editor.status`, which you can run yourself and compare.

   ```sh
   StrataCLI call editor.status
   ```

   The result lists the open project and scene.
   :::
   ::::

   **You should see:** an answer that names the project and its scene, and in the status bar the pill still reading **Agent connected**. The pill's tooltip lists each client, when it connected, and how many requests are pending and answered.

   **If you do not see it:** if the agent says it has no Strata tools, start `claude` again after adding the server; a running session reads its servers once at the start.

:::::

::checkpoint{stage=1}

::figure{id=connected}

## See what the agent sees

An agent can use only the tools it is shown, and every tool costs it reading time. Strata therefore lists few tools at first. A **toolset** is a named group of the editor's commands that the agent sees as tools; the default one, `core`, holds 27 commands. Five generic tools come with it, and together the list holds at most 32 tools, a limit that a test enforces.

The five generic tools are `strata_status`, `strata_launch_editor`, `strata_describe`, `strata_toolsets` and `strata_call`. The first two find or start an editor. `strata_describe` shows the toolsets, a toolset's commands or one command's full description. `strata_toolsets` enables or disables toolsets, and `strata_call` runs any command, listed as a tool or not. The agent never lacks a command; it only lacks the shortcut.

:::::steps

1. Ask the agent for the toolsets and what each one holds.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Call strata_describe with no arguments, and tell me the toolsets and which one is enabled."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent's call corresponds to the command line below, which lists the editor's commands with their descriptions; the toolsets are groups of those names, mostly by prefix.

   ```sh
   StrataCLI list
   ```

   The agent's answer is shorter, because `strata_describe` gives the groups without every command.
   :::
   ::::

   **You should see:** a list of toolsets with a short purpose each (`scene`, `assets`, `play`, `scripts`, `viewport` and others), with `core` marked as enabled.

   **If you do not see it:** if the agent answers from memory and calls no tool, say "use the tool" and ask again. A tool call shows as a row in the Activity panel only when it runs a command.

2. Learn that `asset.place` is not in `core`, and enable the toolset that holds it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Enable the scene toolset with strata_toolsets, then list its commands with strata_describe."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent calls `strata_toolsets` with the argument below; the tool list changes at once, and the agent is told that it changed.

   ```json
   { "enable": ["scene"] }
   ```

   The `scene` toolset holds the commands for scenes, entities, components, prefabs, the selection, undo and lighting, and `asset.place` too.
   :::
   ::::

   **You should see:** the agent names commands such as `asset.place`, `edit.undo`, `selection.get` and `entity.delete`.

   **If you do not see it:** if a name is missing, ask for the group by its exact name: the names are `scene`, `assets`, `play`, `scripts`, `viewport`, `ui`, `world` and `settings`, among others.

3. Give the agent the shipped skills, so that it knows the editor's habits before it acts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the release's `Skills/` folder. Copy the three folders `strata-editor-automation`, `strata-scripting` and `strata-make-a-game` into `.claude/skills/` inside your project folder; copy them into `~/.claude/skills/` to have them in every project.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The command below copies the three folders on Linux and macOS, from the folder that holds `Skills/`; on Windows, copy them in the file manager.

   ```sh
   mkdir -p "<project>/.claude/skills" && cp -r Skills/* "<project>/.claude/skills/"
   ```

   Claude Code reads the folder when it starts, so start `claude` again afterwards.
   :::
   ::::

   **You should see:** after you start it again, the agent lists the three skills when you ask which skills it has.

   **If you do not see it:** each skill must lie in its own folder inside `.claude/skills` of the folder where the agent starts, or in `~/.claude/skills`. A folder one level too deep or too high is not found.

:::::

:::note[What the server does not offer]
The MCP server of Strata offers tools only. It has no MCP resources, prompts or logging messages, and it speaks over the standard input and output, never over a network connection. It has no cancellation either: an agent that stops or disconnects loses only the answer, and the editor finishes the command.
:::

::checkpoint{stage=2}

::figure{id=toolsets-drawing}

## Ask the agent to place props

Before the agent starts, you note where the session begins, so that section six can turn exactly this work into a test. The journal numbers its entries, and the number of the newest one is the marker.

:::::steps

1. Note the journal's newest entry before the agent changes anything.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step has no menu or button: run the command in a terminal.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The command below reads the newest entry of the :term[activity journal]{id=activity-journal}. Write down the number in `journal.latest` of the answer.

   ```sh
   echo '{ "newest": true, "limit": 1 }' | StrataCLI call editor.activity -
   ```

   The `-` reads the parameters from standard input, as [Running commands from the terminal](commands.md) shows, and works in Windows PowerShell too.
   :::
   ::::

   **You should see:** a result with a `journal` object whose `latest` is a whole number, for example 12.

   **If you do not see it:** if the call fails with "no editor", start the editor first; the command line program finds it through its session file.

2. Ask the agent to place the three props.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Use asset.place to put the prefabs `Prefabs/Crate.stprefab`, `Prefabs/Barrel.stprefab` and `Prefabs/Lamp.stprefab` on the ground in front of the camera, a few metres apart. Check the result of each call."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent should send three calls like the one below, each with another `asset` and another `point`. You can send one yourself to compare.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Prefabs/Crate.stprefab", "point": [-2, 0, 3] } }
   ```

   The command rests the prop on the surface at that point, as a drop into the Scene view does.
   :::
   ::::

   **You should see:** three props in the viewport. While the agent works, the viewport shows a chip such as `Agent: asset.place · 3 s ago`. For 0.6 seconds after each change, the props it touched are outlined, fading as the time runs out.

   **If you do not see it:** if the agent says that `asset.place` is unknown, the `scene` toolset is not enabled: repeat the second step of the last section. If a prop floats, the agent gave a point above the ground, where `point` rests it exactly. Ask for a point on the ground, or a `ray` aimed down.

3. Check what the agent did, using the editor and not the agent's words.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look at the Hierarchy: three new entities should be listed. Click the agent chip in the top bar of the viewport to open the Activity panel.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The command below lists the scene's entities.

   ```sh
   StrataCLI call scene.hierarchy
   ```

   The result lists every entity with its name, so that a Crate, a Barrel and a Lamp can be found.
   :::
   ::::

   **You should see:** the three props in the list, each named after its prefab, and the scene marked as changed in the title bar.

   **If you do not see it:** a prop that the Hierarchy lacks was never placed, whatever the agent said. Ask the agent to run `editor.status` and read its `errors`.

:::::

::checkpoint{stage=3}

::figure{id=placed}

## Read the Activity panel and undo

The **Activity panel** lists every command that reached the editor, with who ran it. Strata records four kinds of source, and three matter here: the person in the interface, an automation client such as your agent (shown by the name it gave), and a :term[command script]{id=command-script}. The rows are the activity journal drawn as a table: they show what the agent really did, whatever its summary says.

:::::steps

1. Open the Activity panel and find the agent's rows.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the agent chip in the viewport. In the panel, open the source filter, which starts at **Every source**, and choose **Automation**. Tick **Changes only** to hide queries.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The first command opens the panel; the second reads the same journal as data, limited to the agent's commands.

   ```json
   { "command": "editor.showPanel", "parameters": { "panel": "Activity" } }
   ```

   Run `editor.activity` with a `source` of `Automation` to get the rows as text. In an editor started with `--headless` or `--no-gpu`, which has no window, `editor.showPanel` fails and `editor.activity` still answers.
   :::
   ::::

   **You should see:** at least three rows with a robot icon and the summaries of `asset.place`, newest at the end; a tooltip on a row names its number and the client, for example `Automation: claude-code`.

   **If you do not see it:** if a row names no client, the agent gave no name. The name is shown, never trusted: any program can claim any name.

2. Select the first `asset.place` row and read its details.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the row. The details show the command, who ran it and when, and then the raw parameters and the result as text you can select.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   Read the first `asset.place` entry after the number you noted; the panel's details show the same entry.

   ```sh
   echo '{ "since": 12, "command": "asset.place", "limit": 1 }' | StrataCLI call editor.activity -
   ```

   The entry holds the command, the parameters, the result and the entities it touched.
   :::
   ::::

   **You should see:** the parameters the agent chose (`asset`, `point`) and a result with `placedOn`, `point` and `bounds`.

   **If you do not see it:** if the parameters were cut short, the journal shortened a very large entry and the details say so.

3. Copy one row as a script and run it again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With the third row selected, press **Copy as script**. Then press **Re-run**.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   **Copy as script** puts on the clipboard a step that `StrataEditor --commands` can run, like this one.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Prefabs/Lamp.stprefab", "point": [2, 0, 3] } }
   ```

   **Re-run** sends the same command again with the same parameters, as the person.
   :::
   ::::

   **You should see:** a fourth prop at the same spot as the third, and a new row whose icon is the pointer, not the robot: you ran it, so the journal says you did.

   **If you do not see it:** both buttons are dim for an entry whose parameters the journal had to shorten, and **Re-run** is dim for a command that has not finished.

4. Take the fourth prop back with **Undo to here**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the agent's third `asset.place` row, which is the last row before yours. Press **Undo to here**.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   **Undo to here** runs `edit.undo` once for each step after the selected row. Here that is one step.

   ```json
   { "command": "edit.undo" }
   ```

   Each undo takes back one successful command, the way **Ctrl+Z** does.
   :::
   ::::

   **You should see:** the fourth prop gone, three props left, and rows in the journal for the undo too: the journal never hides what undid what.

   **If you do not see it:** the button is dim when the row's step is the latest, was already undone, left the history, or when the scene is playing. Its tooltip says which.

:::::

:::why
**Undo to here** works on steps, not on rows, because the undo history is the editor's own and holds one step for every successful command. A row of the Activity panel knows its step, so the button can undo back to exactly that point. The cost is that edits made outside commands, such as a drag of a :term[gizmo]{id=gizmo-start}, are steps too: they are undone with the rest, though the journal has no row for them.
:::

::checkpoint{stage=4}

::figure{id=activity}

## Steer the agent safely

An agent acts fast, so Strata gives it rules that protect your work. A command that would replace the open scene, such as `scene.open`, `scene.new` or `project.open`, is refused while the scene holds changes you have not saved, unless the call carries `"force": true`.

A careful agent saves first, or asks you. It never forces away a change that you made.

This section shows what you see when a rule is broken. The props you placed are not saved yet, so they stand for your work. A project from the last checkpoint's download holds them saved: place one more prop first, so that the scene holds a change.

:::::steps

1. Ask the agent to open the scene again, without saying anything about force.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Open `Scenes/Main.stscene` again." Do not mention saving.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent should send a call like the one below. The scene's path is the one that `editor.status` reports.

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   ```

   The editor refuses it.
   :::
   ::::

   **You should see:** an error in the agent's answer that says the scene holds changes that are not saved, and the props still in your scene.

   **If you do not see it:** if the scene opened and the props are gone, the agent forced the call; the next step shows how to bring them back.

2. Tell the agent to force the call, and watch what the editor shows you.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Open it again with force, I accept losing the changes."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The same call with the extra field below replaces the scene.

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene", "force": true } }
   ```

   The result reports `discardedChanges`, so an agent cannot miss that it threw something away.
   :::
   ::::

   **You should see:** a toast in the editor with a title such as `claude-code discarded unsaved changes`. The message says that `scene.open` replaced the scene and that its changes are kept as recovery data. The toast has a button **Recover...**.

   **If you do not see it:** the toast stays for a short time. If it is gone, choose **File ▸ Recover Unsaved Changes...**, which shows the same data.

3. Bring the props back.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Recover...** in the toast, or open **File ▸ Recover Unsaved Changes...**. In the dialog, press **Recover** on the row of your scene.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   `scene.recoveryStatus` lists what the editor kept. `scene.recover` brings it back, with `apply` for the entry whose `id` the list gives.

   ```json
   { "command": "scene.recover", "parameters": { "scene": "<id of the entry>", "action": "apply" } }
   ```

   Run the status command first and copy an entry's `id`, the value with a dash, such as `767BA8F8BB482CB8-C535883170400B58`. Its `scene`, the part before the dash, takes the newest entry that can be applied.
   :::
   ::::

   **You should see:** the three props in the scene again.

   **If you do not see it:** if the dialog lists nothing, the editor had nothing kept: a project closed without any change leaves no data. The project's [recovery rules](project-files.md) say what the editor keeps and for how long.

4. Ask the agent to check its own work in a way you can read.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Run editor.status and tell me the errors, then capture the viewport with viewport.capture, tell me whether the capture is complete, and describe what you see."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The agent's two calls correspond to the commands below. `editor.status` reports errors since the last read, and `viewport.capture` gives a picture of what the camera sees, here saved to a file of the project.

   ```sh
   StrataCLI call editor.status
   echo '{ "path": "Captures/props.png" }' | StrataCLI call viewport.capture -
   ```

   Compare the agent's description with the picture itself, and with the status you ran.
   :::
   ::::

   **You should see:** a status without new errors, and a capture whose `complete` field is `true` and that shows the props. If the agent's words and the capture differ, trust the capture.

   **If you do not see it:** `viewport.capture` needs a graphics device; an editor started with `--no-gpu` has none, and the capture fails with a message. If `complete` is `false`, `incomplete` names what the picture lacks, such as `/pendingAssets`: capture again.

:::::

A capture waits for what is still loading only a limited number of frames, then succeeds anyway, and `complete` says whether it waited long enough.

To see the editor itself, panels and dialogs too, the agent calls `editor.screenshot` of the `editor` toolset, for the whole window or one `panel`.

:::caution
An editor that the agent starts itself, with the tool `strata_launch_editor`, closes after 600 seconds (10 minutes) with no client connected. Changes you have not saved then survive only as recovery data. Save before you leave an agent's editor alone; [Project files](project-files.md) explains recovery.
:::

::checkpoint{stage=5}

::figure{id=steering}

## Keep the session as a test

An agent's session is a recipe: the journal knows every command that changed the scene. You can export it as a **command script**, a JSON file of steps that `StrataEditor --commands` runs on its own. The export is called a **replay script**, and a run on a fresh copy of the project checks that the recipe still builds the same scene.

The export has one difficulty. Entities get new identities (ids) every time they are made, so a recorded id would point nowhere on a copy. Where a later step uses an id that an earlier step made, the export therefore adds a **bind** to the step that made it, which names the result, and a **$ref** in the later step. Both words come from [Command scripts and their checks](automated-playtests.md). Here no step uses a placed prop's id, so the export writes no bind.

:::::steps

1. Export the session, from the entry you noted before the agent began.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step has no menu or button: run the command in a terminal.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   Put your noted number in `since`; the file below is written into the project folder.

   ```json
   { "command": "editor.activity.export", "parameters": { "path": "Regression/Props.json", "since": 12 } }
   ```

   The result lists the steps written and, in `warning`, any edit the script cannot repeat.
   :::
   ::::

   **You should see:** a result with `steps` and `edits` of at least 6: the three placements, your re-run, the undo and the forced `scene.open`. You should also see a `warning` that one edit came from `scene.recover`, `bindings` at 0, and a file `Regression/Props.json` in the project folder.

   **If you do not see it:** if the command fails, the journal no longer holds every entry after `since`: it keeps at most 2,000 commands. Export from a later entry then. A `warning` about edits made outside commands means a gizmo drag or an inspector field, which a script cannot repeat.

2. Add a check to each placement.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Regression/Props.json` in a text editor. Delete the `scene.open` step: a script cannot repeat the recovery that followed it, so a replay with that step would end with an empty scene. Then give each `asset.place` step an `expect` that the prop came to rest on a point.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   An `expect` names a part of the result by a path and a condition. The step below fails when the result's `placedOn` is anything but `point`.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Prefabs/Crate.stprefab", "point": [-2, 0, 3] }, "expect": { "/placedOn": { "equals": "point" } } }
   ```

   Keep the rest of each step as the export wrote it.
   :::
   ::::

   **You should see:** a script with four placements, each with its check, and one `edit.undo`, which takes your re-run back as in the session.

   **If you do not see it:** a script that is not valid JSON stops at its first error; a stray or missing character between two steps is the usual cause.

3. Make a fresh copy of the starting project, and copy what the session made outside commands.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the starting checkpoint's folder to a new folder, for example `AgentProps-copy`. Do not copy the placements: the script makes them. If the agent wrote scripts or generated :term[source assets]{id=source-file}, copy the project's `Scripts/` folder and those assets into the copy.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   Files written outside commands are not in the script. Copy them by hand, and also copy the script file itself into the copy.

   ```sh
   cp -r "<starting project>" "<copy>"
   ```

   Here the session wrote no scripts, so the copy needs nothing more.
   :::
   ::::

   **You should see:** a folder with the project's file and no props in its scene.

   **If you do not see it:** if the copy already holds the three props, you copied the project after the session and not the starting checkpoint. A replay on it would add three more.

4. Run the script on the copy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step has no menu or button: run the command in a terminal.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The editor starts without a window or an automation server, runs the script, and quits. Its exit code is 0 when every check holds and 1 when one fails.

   ```sh
   StrataEditor --no-gpu --no-automation --quit-after-commands --project "<copy>" --commands "<copy>/Regression/Props.json"
   ```

   Read the exit code with `echo $?` on Linux and macOS, or `echo $LASTEXITCODE` in PowerShell.
   :::
   ::::

   **You should see:** the editor exits with code 0, and its log lists the commands it ran.

   **If you do not see it:** a failed `expect` prints the step and the value found, and the code is 1. If the scripts of a bigger project did not build in the replay, they were not copied into the copy.

:::::

::checkpoint{stage=6}

::figure{id=regression}

## Make a whole game the agent's way

The skill `strata-make-a-game` is the guide for a whole game, and the Tetris sample was made by an agent that followed it, through the editor alone. The guide has eight steps, and each one has a check that an agent can run without asking you.

| Step | What the agent does | How it checks |
| --- | --- | --- |
| 1. An editor | Starts one, notes `journal.latest` | `editor.status` |
| 2. A project and a plan | `project.create`, rules kept apart from engine calls | The plan names what to observe |
| 3. Assets | Makes materials and sounds, imports files | `asset.list` |
| 4. Scripts | Writes the C++ classes, `script.build` | Build diagnostics |
| 5. The scene | Creates entities, components and game interface | `scene.hierarchy` |
| 6. Play and look | `play.start`, `input.key`, `viewport.capture` | Values read with `script.get` |
| 7. A regression | Exports a command script, adds `expect` | The script's exit code |
| 8. The export | `project.export`, runs the game | The game's own log |

Two habits run through all eight. The agent builds for observation: rules live in a plain class, randomness comes from a seed, and tuning values are fields, so that a check can predict an exact result. And it checks by looking, not by believing: after each change it runs `editor.status` and, when the look matters, a capture.

:::::steps

1. Open a copy of the Tetris sample and play it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the launcher, choose **Open Sample...**, pick Tetris and a folder for the copy. Press Play: the editor builds the scripts first. Keys: **Left** and **Right** move, **Space** drops, **Up** rotates.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The command below opens a copy of the sample through the automation interface; its answer names the folder.

   ```json
   { "command": "project.openSample", "parameters": { "sample": "Tetris", "directory": "<an absolute path of an empty folder>" } }
   ```

   Then run `play.start` to play.
   :::
   ::::

   **You should see:** the falling blocks, a score and a preview of the next piece.

   **If you do not see it:** if opening the sample fails because the scene has changes you have not saved, save it with **Ctrl+S** first. The first Play builds the sample's :term[script module]{id=script-module}, which takes a while; the :term[Problems panel]{id=problems-panel} shows a failed build.

2. Ask the agent to describe how Tetris was made, using the guide.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Read the skill strata-make-a-game and the Tetris sample's `README.md`. Tell me which of the eight steps made each part of the sample, and which commands I can run to check it."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   The sample's own `README.md` lists the commands the agent used: `project.create`, `material.create`, `entity.create`, `ui.create`, `script.build`, then play with `input.key` and look at `viewport.capture`.

   ```sh
   echo '{ "paused": true }' | StrataCLI call play.pause -
   echo '{ "steps": 60 }' | StrataCLI call play.step -
   ```

   `play.step` runs only in a paused game: without the first line it fails with `Stepping needs a paused running scene (play.pause)`. One second of game time, at 60 steps, is a good unit for a check: it counts the game's :term[fixed steps]{id=fixed-step}, not frames.
   :::
   ::::

   **You should see:** an answer that matches the table above, with names of files such as `TetrisBoard.cpp`.

   **If you do not see it:** if the agent does not know the skill, check that its folder is in `.claude/skills/` and start the agent again.

3. Start your own game with one sentence.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type: "Follow strata-make-a-game and make the smallest game you can: one moving object and a score. Save, play it with input, capture it, and leave a regression script."
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   Your part is as on this page: connect, watch the chip, read the Activity panel, and undo what you dislike.

   ```sh
   StrataCLI call editor.status
   ```

   Run it between the agent's steps to see its errors for yourself.
   :::
   ::::

   **You should see:** the agent working through the eight steps, with rows in the Activity panel for each command.

   **If you do not see it:** if the agent stops after a build error, ask it to read `editor.status` and the Problems panel and to fix the first error only.

:::::

Next, read [Command scripts and their checks](automated-playtests.md) for the regression and [Project files](project-files.md) for recovery and saves.

::checkpoint{stage=7}

::figure{id=tetris}

## Summary

- You ran the launcher's line in the folder where the agent starts, and saw the status bar pill change to **Agent connected**.
- You learned that the agent starts with the `core` toolset and five generic tools, and enabled `scene` to reach `asset.place`.
- You found the agent's rows in the Activity panel, copied and re-ran one, and took the extra prop back with **Undo to here**.
- You saw that a command that replaces a scene holding changes you have not saved is refused unless forced, and that a forced call shows a toast with **Recover...**.
- You exported the session as a command script, added checks, and ran it on a fresh copy with `StrataEditor --commands`.

## Check yourself

1. You paste the launcher's line in one terminal, then start `claude` in your game project's folder, and Claude Code lists no Strata tools. What is the likely cause, and what are the two fixes?

   :::answer{tests="connect"}
   The line added the server at Claude Code's default local scope, which loads the server only in the folder where you ran it. Run the line again in the project's folder, or add `--scope user` before `strata` so that every folder has it. `claude mcp list` shows which folders have the server.
   :::

2. The agent says it cannot find `asset.place`, yet you know the command exists. What do you do, and why was it missing?

   :::answer{tests="toolsets"}
   Ask it to call `strata_toolsets` with `{"enable": ["scene"]}`. The default `core` toolset holds 27 commands, kept small so that the list stays within 32 tools, and `asset.place` belongs to `scene`. The agent could also have run it at once with `strata_call`.
   :::

3. The Activity panel shows ten rows. Three have a robot icon, six a pointer, one a scroll. Who ran each group? All ten made edits, and you press **Undo to here** on the third row: how many steps does it take back?

   :::answer{tests="activity"}
   The robot rows were run by an automation client such as the agent, the pointer rows by you in the interface, and the scroll row by a command script. Seven steps come after the third row, so it undoes seven, and the first three rows stay in force. The scene returns to the state right after the third row.
   :::

4. The agent opens a scene while you have changes not yet saved and passes `"force": true` without asking you. What do you see, and where are the changes?

   :::answer{tests="safety"}
   You see a toast that names the agent, says that its command replaced the scene, and offers **Recover...**. The changes are kept as recovery data of the project, so **File ▸ Recover Unsaved Changes...** brings them back. Without `force`, the editor would have refused the command.
   :::

5. Your replay script run on a copy exits with code 1, and the log says a :term[script class]{id=script-class} was not found. Which step did you skip?

   :::answer{tests="regression"}
   You did not copy the project's `Scripts/` folder into the copy. The export holds only commands, and files an agent wrote outside commands are not in it. Copy the folder, with any generated source assets, and run the script again.
   :::

## Exercises

1. **Basic.** Ask an agent to add three props, then take them all back with **Undo to here** on the last row before the agent's first, and check the Hierarchy. Hint: tick **Changes only**, then select the row right above the agent's first `asset.place`; if its button is dim because its command recorded no undo step, take the row above that.

   :::answer[Worked solution]{tests="activity" solution="tutorials/make/with-an-agent/exercise-1.tutorial.json"}
   Select the row that precedes the agent's first `asset.place` and press **Undo to here**. The panel runs `edit.undo` three times, one for each step after the row, and the Hierarchy again holds only the starting entities. In the solution file, three placements are followed by three `edit.undo` calls.
   :::

2. **Medium.** Set the source filter to **Automation** and tick **Changes only**. Then ask the agent to count the entities with `scene.hierarchy`. Does the panel list that call, and why?

   :::answer{tests="toolsets,activity"}
   With **Changes only** ticked, the count does not appear: a query changes nothing, so the filter hides it. Clear the box and the row for the query shows, because the journal records every command, not only edits.
   :::

3. **Hard.** Break the script on purpose, so that the check fails: change `point` to `ray` in one step and run the script on a fresh copy. Predict the exit code and read the message.

   :::answer{tests="regression"}
   The step now asks for a ray, and `asset.place` needs `origin` and `direction` in it, so the step fails with an invalid parameters message before it places anything. The exit code is 1, because a failed step fails the run, as a failed `expect` does.
   :::

## Where it lives in Strata

The launcher's card and its line are in `StrataEditor/src/Panels/WelcomePanel.cpp`. The server that speaks MCP is in `StrataCLI/src/CLI/McpServer.cpp`, and the toolsets and the `core` list are in `StrataCLI/src/CLI/McpToolsets.cpp`. The Activity panel, with **Copy as script**, **Re-run** and **Undo to here**, is `StrataEditor/src/Panels/ActivityPanel.cpp`. The pill is in `StrataEditor/src/EditorLayer.cpp`, the agent chip and the outline flash in `StrataEditor/src/Panels/ViewportPanel.cpp`, and the toast that names the agent in `StrataEditor/src/Editor/EditorContext.cpp`.

The command `editor.activity.export` is in `StrataEditor/src/Editor/EditorStateCommands.cpp`. The engine's `Skills/` folder holds the three guides.

## Further reading

- The Strata release's `Docs/Releases/PackageReadme.md`, section "Connect an AI agent": the line and where the skills go (beginner).
- The skill `strata-make-a-game` in the release's `Skills/` folder: the whole guide (intermediate).
- Claude Code's documentation on MCP servers and their scopes, at code.claude.com (intermediate).
- The Model Context Protocol specification, at modelcontextprotocol.io (advanced).

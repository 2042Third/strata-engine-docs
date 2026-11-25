---
id: start/how-to-read
title: "How to read this book"
description: "Choose a reading track, read the strips at the top and bottom of a page, and learn to read the book's commands and code."
kind: how-to
size: M
tracks: [G, E, B]
needs: []
time: 35
learn:
  - id: track
    text: choose a track and follow its next-page links
  - id: strips
    text: name what each part of a page's top and bottom strips tells you
  - id: map
    text: trace a page's prerequisites on a part's map back to the first page of a track
  - id: command
    text: explain what an editor command's name and JSON parameters ask the editor to do
  - id: code
    text: explain what a short code excerpt does from its label, its comments and its names
status: final
---

This page teaches you to read any page of this book and to know where to go next. You choose a **reading track**: one of three fixed orders of pages, which the next-page and previous-page links of every page follow. Then you learn to read the strips at the top and bottom of a page, a command written as JSON and a short piece of code. Before you start:

- Have this book open in a web browser. You need no program, no project and no experience of games or programming, because the steps act on the pages of the book.

## How to read a command

Strata's editor is the program in which you make games. Every change that you make in it runs a command: a named operation such as "create an entity", which makes one new thing in the game's world. People click, while tools and artificial intelligence (AI) agents type the same commands. So most steps of the book have two tabs. "In the editor" shows the clicks, and "With a command" shows the command.

If you make games, you may ignore the command tab. The editor tab of every game maker's step is complete.

A command has a name of the form `<group>.<action>`. In `entity.create`, the group is `entity` and the action is `create`. Its parameters, the facts it needs, are written in [JavaScript Object Notation (JSON)](../basics/data-formats.md), a text format with five kinds of value:

- An object is named values in braces: `{ "name": "Cube" }`. A name is a string, a colon follows it, and its value comes next. Pairs follow each other, divided by a `,`.
- A list is values in brackets: `[0, 0.5, 0]`.
- A string is text in double quotes.
- A number has no quotes: `0.5`.
- `true` and `false` are the two yes-or-no values, and `null` means that there is no value.

The **+** button at the top of the **Hierarchy**, the editor's list of the scene's entities, shows the idea. Choosing **Cube** there runs `entity.create` with parameters like the ones below. Notice the braces, the brackets and the numbers.

```json
{
  "name": "Cube",
  "components": {
    "MeshRenderer": { "Mesh": "Builtin/Cube" },
    "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] },
    "Transform": { "Translation": [0, 0.5, 0] }
  }
}
```

The outer object has two pairs: `name`, a string, and `components`, an object. Inside it stand three components, each a piece of data that the new entity gets: a shape to draw, a box that physics collides with, and a place. A list of three numbers gives one number for each direction in space.

The half extents of 0.5 mean that the box reaches 0.5 to each side of its center, so it is 1 unit wide. A translation of 0.5 in the second number lifts the center by half the height, so the bottom lands at 0.5 - 0.5 = 0, on the ground. The editor names the mesh by its id in place of `Builtin/Cube`, a name that the command also accepts. It also completes the place from where its view of the scene looks, so the numbers it sends differ from these.

A command answers in JSON too. For `entity.create` the answer is an object such as `{ "id": "9F3A2C41D8E75B06" }`: the id of the new entity, a string of 16 hexadecimal digits. Later commands use that id to name the entity.

In a command tab the book writes the name and the parameters together in one object, with the keys `command` and `parameters`. To run a command yourself you use `StrataCLI`, the program in the Strata folder that sends one command to the running editor and prints its JSON result. Your terminal does not know it: run it from the folder that holds it, while the editor runs. [The install page](../start/install.md) shows how to open a terminal.

The program takes the name and the parameters only. Put the parameters in a file named `params.json`, which you write as UTF-8 text with a code editor. Or write `-` and send them through standard input: the text that a command before a `|` sign passes on. A file is safer than a JSON argument, because PowerShell drops the quotes inside one.

::::tabs{sync=os}
:::tab[Windows]
In PowerShell, quote `@params.json`: a bare `@` there is another operator. The second line pipes the parameters in.

```powershell
.\StrataCLI call entity.create '@params.json'
'{ "name": "Cube" }' | .\StrataCLI call entity.create -
```

Each line makes one entity and prints its id.
:::
:::tab[Linux]
A Linux shell passes `@params.json` through as written. The second line pipes the parameters in.

```sh
./StrataCLI call entity.create @params.json
echo '{ "name": "Cube" }' | ./StrataCLI call entity.create -
```

Each line makes one entity and prints its id.
:::
:::tab[macOS]
The macOS shell behaves like the Linux one. The second line pipes the parameters in.

```sh
./StrataCLI call entity.create @params.json
echo '{ "name": "Cube" }' | ./StrataCLI call entity.create -
```

:::
::::

Each line makes one entity and prints its id.

## How to read code you do not understand yet

Some pages show code from the engine or from a game script. You need not understand it at first reading. Four words come first:

- **Source code** is the text of a program, written by people.
- A **programming language** is a fixed set of words and rules in which people write source code that a computer can follow. Strata's engine and its game scripts use the language C++.
- A **comment** is a note in source code for people. The computer ignores it, and in C++ it starts with `//`.
- **Pseudocode** is code-like text for people only. No computer runs it, and the page labels it as such.

Five habits help you read an unknown excerpt:

- Read the label above it. For the engine's code it names the file and the lines, and the numbers beside the code are the file's own line numbers. A sketch carries the name of its file, and pseudocode says "Pseudocode".
- Read the sentence before the fence, since it says what the code does and what to search for.
- Read the comments, which say what the author meant.
- Trust the names: a function called `GetTransform` gets a transform.
- Skip what the page does not ask about.

The first lines of the `Spinner` script from [your first game](../start/first-game.md) show all five.

:::question
The excerpt has C++ that [Programming 1](../basics/programming-1.md), [Programming 2](../basics/programming-2.md), [Programming 3](../basics/programming-3.md) and [C++ classes](../basics/cpp-classes.md) teach. You need none of it now.
:::

The label names the file and the lines 240 to 252. Search for the comment on the first line and for names that say what they hold. The sentence before this fence says what the code does: the class turns its entity.

```cpp src="StrataEditor/src/Editor/ScriptProject.cpp#L240-L252"
// Turns its entity around the world's Y axis.
class Spinner : public Script
{
public:
	float DegreesPerSecond = 90.0f; // A field: editable per entity, kept across hot reloads

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};
```

1. **Line 240:** a comment. It says in plain words what the script does.
2. **Line 241:** the name `Spinner`. The rest of the line says that it is a kind of `Script`.
3. **Line 244:** a field, a number that the editor shows and each entity keeps. Its name and its comment say that it counts degrees per second.
4. **Line 246:** `OnUpdate`, a function whose name says when it runs. `deltaTime` is the time of the last frame.
5. **Lines 248–250:** the body. It reads the entity's transform, builds a small turn and writes the new rotation.

You may use the code and the project files that the book gives in your own programs and games, and ship them. [Credits and permission](../appendix/credits.md) states the permission in full.

## Read the book in eight steps

:::::steps

1. Choose a track.

   ::track-chooser

   The three tracks fit three readers. Game makers (G) make games with the editor and scripts and need no engine internals. Beginners (B) start with nothing and learn programming and the mathematics of games first. Engine builders (E) learn to read and change the engine's code.

   Press "Follow this track" under the one that fits you. Your browser keeps the choice.

   Every page ends with links named "Previous on your track" and "Next on your track". Without a track they follow the parts of the book in order. Some pages are side steps of a track, such as the primer on tools on track G: the next-page links of that track never lead into one. You open it from a link or from the sidebar, and its own next-page link returns to the page it stands before.

   **You should see:** the button reads "Following this track (stop)", and a line says which track you follow.

   **If you do not see it:** your browser blocks scripts. The "Start with" link of each track still works, but the next-page links then follow the parts in order.

2. Read the top strip of this page.

   The strip stands under the title. Its badges show the kind of page, the letter of each track that includes the page, and the time the page takes. New pages also carry "New in" with a release, and a page that is not final carries "Draft". A line names the level, and two lists follow: "After this page you can" and "Before you start".

   The kind says what the page answers. A **primer** is a page that teaches one subject from zero, such as vectors, for readers who may know it already.

   | Kind | The question it answers |
   | --- | --- |
   | Primer | What must I know first? It starts with a "Test out" box of five questions: if all your answers are right, skip the page. |
   | Concept | What is this idea, and why does Strata do it so? It builds the idea from a problem and ends with common mistakes. |
   | Internals | How does Strata's code do it? It shows the problem, the alternatives, the tests and how to change it safely. |
   | Tutorial | How do I build this one thing? Its parts end in checkpoints. |
   | How-to | How do I reach this goal? One page of steps, a result and variations. |
   | Reference | What exactly is the name or the number? Tables that you search. |

   The level counts what a page builds on. Level 1 needs only the first three parts: Start here, Making games and Foundations. Level 2 also needs the engine's core or earlier pages of its own part. Level 3 builds on other parts of the engine.

   **You should see:** the badges "How-to", G, B and E, and under "After this page you can" the five goals of this page.

   **If you do not see it:** on a narrow window the lists stack. Scroll up to the title.

3. Read the bottom strip of a page.

   Scroll to the end of any page. Five sections close every concept, internals, tutorial and how-to page. "Summary" has one line for each goal of the top strip. "Check yourself" asks three to six questions, and "Exercises" asks one to four. Their answers stay hidden until you press them, so try first.

   "Where it lives in Strata" names the engine files that the page explains. "Further reading" lists books and sites, each with its level: beginner, intermediate or advanced. A primer has "Practice" and "Where the book uses it" in place of two of these.

   **You should see:** at the end of this page the five sections in that order.

   **If you do not see it:** you are on a reference page, which ends with "Where it lives in Strata" alone.

4. Check the engine release.

   Under the two lists the strip says "Checked against Strata", a release number, "at commit" and the first eight characters of a commit. The **engine release** is the numbered version of Strata that the book describes. The commit is the exact state of its source code, and the book checks its claims against that commit.

   Your engine may be another release. An older one lacks newer features, so a step may name a menu that you do not have. A newer one may rename or move things, so a label may differ. Concepts change slowly and names change fast: trust the idea and search for the new name. While a release is a pre-release, its programs may still report the number of the release before it, so compare commits and not numbers.

   **You should see:** one sentence with a release and a short commit.

   **If you do not see it:** it stands directly above the link "Print view of" at the end of the strip.

5. Follow a page's prerequisites on a map.

   A **prerequisite** is a page that you should have read before another page. "Before you start" lists the prerequisites of a page, and a line such as "X or Y" means that either page is enough. A page with an empty list needs the first page of its part, and the strip names it.

   Click the name of the part in the line of links above a title to open the part's page, for example [Engine architecture](../core/index.md). Its section "The map of this part" draws each page with arrows to its prerequisites and lists them again in words.

   Read one page this way. "What a game engine is" needs "Your first game", which needs "Installing Strata and the C++ build tools", which needs "How to read this book". That page has no prerequisite of its own, so it needs the first page of its part. That makes four steps back to the start.

   ```mermaid caption="The prerequisites of one page, followed back through four steps to the first page of its part." alt="Five boxes joined by arrows that each point from a page to the page it needs. What a game engine is points to Your first game, which points to the install page, which points to How to read this book, which points to What Strata is."
   flowchart LR
     A["What a game engine is"] -->|needs| B["Your first game"]
     B -->|needs| C["Installing Strata"]
     C -->|needs| D["How to read this book"]
     D -->|needs| E["What Strata is"]
   ```

   **You should see:** the part's page with a diagram and a list. Each line of the list names the prerequisites of one page.

   **If you do not see it:** a prerequisite that is not written yet shows as plain text with "(not written yet)". Follow the other links.

6. Read a step in both tabs.

   A step of a tutorial or how-to is a numbered item whose action stands in tabs. Names of the editor's buttons, menus and panels are bold. A menu path reads **File ▸ Save Scene**: open the menu **File**, then choose **Save Scene**. A key reads **Ctrl+S**. On macOS the editor's menus still say Ctrl, but you press the Command key.

   Press "With a command" in the example, and then "In the editor". Your choice stays for every page.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Save Scene**, or press **Ctrl+S**.
   :::
   :::tab[With a command]
   The command `scene.save` needs no parameters, so the object holds only its name:

   ```json
   { "command": "scene.save" }
   ```

   :::
   ::::

   Two labels follow every action. "You should see" says what changed, so that you can tell the step worked. "If you do not see it" names the likely cause and the way back. A tutorial also ends each part with a **tutorial checkpoint**: a box where you download the project as it should be at that point. A mistake then costs one part and not the whole tutorial.

   **You should see:** one line of JSON in the command tab and the menu path in the editor tab.

   **If you do not see it:** a step that shows no tabs has no command. Read its plain text.

7. Open a definition and name the boxes.

   The first use of a term on a page is a link with a small "?" button. Press the button to open a box with the definition and a link to the page that teaches the term. The link itself leads to the entry in [the Glossary](../reference/glossary.md), which lists every term. **Escape** closes the box.

   Boxes with a title are asides. "A question you may have" answers what a reader asks. "Why it is so" gives the reason for a design choice, and "How it came to be" tells what Strata did before. "In other engines" compares, and "A rule of the engine" quotes a rule of Strata's developers with its reason. "Simplified for now" says what a page omits, "An analogy" says where it stops fitting, and "Worked example" computes one case with real numbers.

   **You should see:** a box with a bold term, its definition and a link that starts "Read:".

   **If you do not see it:** an old browser shows the link without the "?" button. Follow the link.

8. Go to the next page.

   Press "Next on your track" at the end of this page. Your track decides where it leads, and on every track the page after this one comes next.

   **You should see:** the page "Installing Strata and the C++ build tools".

   **If you do not see it:** you chose no track, so the link follows the parts in order. It leads to the same page.

:::::

## Result

You follow a track, so every page ends with the link to your next page. You can read a page's strips and trace its prerequisites on a part's map. You can read a step in either tab, a command and its JSON, and a code excerpt by its label, comments and names. You can also find a term's definition. That is enough for the next page, where you install Strata.

## Variations

Three features of the site help when your situation differs.

- **Search.** The search field finds pages by title and text. A result names the part and the kind of the page beside its title.
- **A printed copy.** The link "Print view of" at the end of the top strip opens the whole part on one page. Print it from your browser: hidden answers open for printing.
- **Another release.** Older editions of the book, when the site keeps one for your release, live at an address that starts with `v` and the release number. Read that edition. If none exists, read this one and expect the differences of step 4.

## Summary

- You choose a track with its button, and the next-page and previous-page links of every page then follow it.
- The top strip gives the kind, the tracks, the level, the time, your goals, the prerequisites and the engine release. The bottom strip gives the summary, questions, exercises, engine files and further reading.
- The map of a part shows each page's prerequisites, and following them back reaches the first page of a track.
- A command is a name `<group>.<action>` with JSON parameters of objects, lists, strings, numbers, `true`, `false` and `null`, and the editor answers in JSON.
- You read code by its label, the sentence before it, its comments and its names, and you may skip what the page does not ask about.

## Check yourself

1. You press "Follow this track" under "Learn from zero", and later open a page that this track does not include. What do the next-page links of that page do?

   :::answer{tests="track"}
   The links follow the parts of the book in order, because the track holds no neighbours of that page. The page still opens. Your choice stays, and the links return to your track on the next page that it holds.
   :::

2. A page shows the badge "Level 1" and, under "Before you start", the line "The tools: the terminal, files and a code editor or Installing Strata and the C++ build tools". What do the two tell you?

   :::answer{tests="strips map"}
   Level 1 says that the page needs only the first three parts of the book. The line says that either page is enough before you start: you do not need both.
   :::

3. The strip says "Checked against Strata" with a release, and your editor is one release older. What do you trust, and what do you check?

   :::answer{tests="strips"}
   Trust the ideas, since concepts change slowly. Check names, menus and defaults, because an older editor may lack a feature or use another label.
   :::

4. In `{ "name": "Lamp", "parent": null }`, which value is a string, and what does `null` say?

   :::answer{tests="command"}
   `"Lamp"` is the string. The value `null` says that there is no parent, so the entity is made at the top level.
   :::

5. You see `ScriptProject.cpp`, lines 240 to 252, and the line `void OnUpdate(float deltaTime) override`. You know no C++. How do you learn what the function does?

   :::answer{tests="code"}
   Read the sentence before the excerpt for what to search for, then the comment and the names. `OnUpdate` is a function that runs each frame, and `deltaTime` is the time of the last frame. If a line stays unclear and the page does not ask about it, skip it.
   :::

## Exercises

1. **Basic.** Read the parameters `{ "name": "Lamp", "parent": null, "components": { "Transform": { "Translation": [0, 3, 0] } } }` of `entity.create`. What does the command make? Name a string, a number, a list and an object in it, and say what the answer holds.

   :::answer{tests="command"}
   The command makes a top-level entity named `Lamp`, with a transform whose translation is 0, 3 and 0: three units above the origin. The string is `"Lamp"`, a number is `3`, a list is `[0, 3, 0]` and an object is `{ "Translation": [0, 3, 0] }`. The answer is an object with the `id` of the new entity.
   :::

2. **Medium.** Start at the page "What a game engine is: one frame, start to finish" and follow each page's "Before you start" back until a page has none. Write the chain.

   :::answer{tests="map track"}
   "What a game engine is" needs "Your first game", which needs "Installing Strata and the C++ build tools", which needs "How to read this book". Its list is empty, so its strip names the first page of its part, "What Strata is and what this book teaches". That page is the first of every track, so all three tracks start there.
   :::

3. **Medium.** Write the parameters of `entity.create` for a top-level entity named `Crate` with a `MeshRenderer` whose `Mesh` is `"Builtin/Cube"` and a `Transform` whose `Translation` is `[2, 0.5, 0]`.

   :::answer[Worked solution]{tests="command" solution="tutorials/start/how-to-read/exercise-3.tutorial.json"}
   The parameters are `{ "name": "Crate", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [2, 0.5, 0] } } }`. There is no `parent`, so the entity sits at the top level. After you install Strata, run them with `StrataCLI call entity.create` and read the entity back with `component.get`: its `Translation` holds 2 and 0.5 in the first two places.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/Commands/EntityCommands.cpp`: the command `entity.create` with its parameters and its answer.
- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`: the **+** menu of the Hierarchy and the presets that it sends to `entity.create`.
- `StrataCLI/src/CLI/CliApplication.cpp`: `StrataCLI call` with its `@file` and `-` forms for parameters.
- `StrataEditor/src/Editor/ScriptProject.cpp`: the text of the `Spinner` script that every new project gets.

## Further reading

- learncpp.com, "Learn C++": a free course that teaches the language of the engine from its first line (beginner).
- Mozilla Developer Network, "Working with JSON": the kinds of value and how a program reads them (beginner).

# How a page is written

This file is the writers' contract. Every page of the book follows it, and every reviewer judges pages by it. A page
succeeds when its least prepared reader can do or explain something afterwards that they could not do before.

Each rule says who checks it:

- **lint**: `tools/lint.py`, with the rule's id in backticks (`sentence-max`). A failing rule keeps the page out of
  review. Rules marked *warning* are reported for the writer and the reviewers to decide; every other rule fails.
- **strips**: the strips plugin of the build, which checks the front matter and the structure of the page.
- **names**: `tools/names.py`, the names lint of [pipelines.md](pipelines.md), which checks every engine name and UI
  label against the engine at the pin.
- **technical** and **provenance**: the technical reviewer and the provenance reviewer of [process.md](process.md).

Where this file names a directive, an attribute, a front-matter key or a data file that the spike has not built yet,
or names one differently from the spike, the place is marked **(spike)**. Where the spike's working name differs, the
spike's name wins and this file is corrected to it.

## 1. Readers

### 1.1 The three personas

| Persona | Track | Wants |
| --- | --- | --- |
| **G0, game maker** | G | A finished game |
| **B0, beginner** | B | To understand everything, from zero |
| **E1, engine builder** | E | To understand and change an engine |

The lists below are exact. The provenance reviewer checks a page against them: what a list does not hold must be
taught before the page uses it.

**All three personas**

- Read English at level B1 of the Common European Framework of Reference (CEFR). English may be a second language.
- Use a computer that meets the release's requirements (`Docs/Releases/PackageReadme.md`, "Requirements"): Windows 10
  or 11 (x64), Ubuntu 24.04 or newer, or macOS 14 or newer on Apple silicon, with a GPU that has a Vulkan 1.2 driver.
  It is not the reference machine: its GPU is slower.

**G0, game maker. Has:**

1. Uses a desktop computer: starts and closes programs; uses windows, menus, buttons and dialogs; uses the mouse
   (click, double-click, right-click, drag and drop, scroll wheel) and the keyboard (shortcuts with Ctrl, Shift, Alt or
   Cmd; copy and paste); knows the common menu words File, Edit, View, Open, Save, Save As, Undo, Redo, Copy, Paste and
   Settings.
2. Installs a program from a download: runs an installer, or unpacks a ZIP archive, and finds the program afterwards.
3. Uses files and folders in the system's file browser (File Explorer, Finder, Files): opens, creates, renames, copies,
   moves and deletes them; knows that a folder holds files and other folders; reads a file's size in KB, MB or GB.
4. Uses a web browser: opens a link, downloads a file and finds the downloaded file.
5. Has played video games: knows the words game, player, level, score, menu, pause, save, character, first person and
   third person, and has seen a frame rate given in frames per second (FPS).
6. Arithmetic: whole numbers, negative numbers, decimals, fractions and percent; the order of operations; rounding;
   the average of a few numbers; squares and square roots of small numbers.
7. A little algebra: a letter can stand for a number; puts numbers into a formula and computes it (speed = distance ÷
   time); solves one linear equation with one unknown (2x + 3 = 11).
8. Reads and plots a point (x, y) on a graph with an x axis and a y axis.
9. Units: metre, centimetre, kilometre, gram, kilogram, second, minute and hour; the prefixes kilo-, centi- and milli-;
   angles in degrees (a right angle is 90°, a full turn is 360°).

**G0, game maker. Has not:**

1. Any programming: code, variables, loops, functions, compiling, any programming language, JSON, HTML.
2. Any 3D software: models, meshes, vertices, polygons, textures, materials, lights in software, shaders, rendering,
   coordinates in three dimensions, transforms.
3. A terminal: command lines, shells, PowerShell, commands with arguments, environment variables, paths written as text
   (`C:\Users\…`, `~/…`), file extensions, hidden files.
4. Programmers' tools: code editors, compilers, build tools, debuggers, git and version control.
5. How a computer works inside: the processor, memory, what a GPU does, drivers, processes.
6. Mathematics beyond the Has list: other powers, logarithms, exponentials, trigonometry (sin, cos, tan), radians, the
   Pythagorean theorem, vectors, matrices, Σ notation, derivatives and integrals, probability.
7. Physics as a science: force, mass, acceleration, velocity as speed with a direction, momentum, friction.
8. Any game engine: Unity, Unreal, Godot or another (a reader who has used one may read `start/coming-from`).
9. How games are made: entities, components, scenes as documents, prefabs, assets, scripts, what a frame is inside an
   engine, playtesting, exporting.

**B0, beginner.** Has and has not exactly what G0 has and has not. B0 also expects every "why" to be answered on the
page or by a link to a page on track B.

**E1, engine builder. Has** everything G0 has, and:

1. Has written, run and fixed programs of a few hundred lines in one language (Python, JavaScript, C#, Java, C or
   C++), using: values and variables; the types integer, floating-point number, text string and boolean; arithmetic,
   comparison and logical operators; `if` and `else`; `while` and `for` loops; functions with parameters and a return
   value; arrays or lists; a map or dictionary that stores and finds values by key; a class or struct with fields and
   methods, written and used; printing values to find a bug; reading an error message and the line it names. The
   language may not be C++: C++ syntax itself is taught by `basics/programming-1` to `-3`, which E1 may test out of.
2. Has run those programs from a code editor or an IDE.
3. School algebra: functions and their graphs, linear equations, systems of two linear equations, powers with whole
   exponents (2³ = 8, 10⁶), square roots, the Pythagorean theorem.

**E1, engine builder. Has not:**

1. C++ beyond the basics: pointers, references, object lifetimes, inheritance and virtual functions, templates,
   lambdas, move semantics, the standard library's containers and algorithms, headers and the preprocessor; how a C++
   program is compiled and linked; CMake.
2. Tools: a terminal, git, a debugger.
3. Linear algebra: vectors, matrices, dot and cross products, transforms, quaternions.
4. Mathematics: trigonometry and radians, logarithms and exponentials, Σ notation, derivatives and integrals,
   probability distributions.
5. How a computer works below the language: binary and hexadecimal, bytes and memory layout, the stack and the heap,
   caches, threads.
6. Data structures beyond arrays and maps: hash tables as they work inside, trees, graphs, queues, the cost of
   operations.
7. Graphics: what a GPU does, shaders, meshes, textures, graphics APIs (Vulkan, Direct3D, OpenGL), color spaces.
8. Engines: how any game engine is built; using an engine's editor.

### 1.2 How the personas are used

1. A page is written for the least prepared persona of its tracks. From least to most prepared: B0, G0, E1. A page on
   tracks G and B is written for B0.
2. While reading a page, the persona knows three things: its list; what the pages of the page's **Needs closure**
   teach (their learn lines, their Summary sections and the glossary terms whose home is there); and what the earlier
   sections of the page taught. The Needs closure is the page's Needs, their Needs, and so on. A page whose outline row
   has `-` needs the first page of its part. With an alternative `a|b`, the page uses only what both `a` and `b`
   (with their closures) teach.
3. Anything else the page uses (an idea, a term, a symbol, a C++ feature, a UI action, a tool) is "used but not
   taught". The provenance reviewer reports each one with the sentence that uses it (process.md).
4. **The fourth reader**, a contributor to the engine or an agent, arrives by search and has no persona. Pages on no
   track (reference and appendix pages) are written so that E1 can read them: every term that E1's list does not hold
   is marked (§3). Internals and reference pages serve this reader with exact names and with their "Changing it
   safely" sections.

## 2. Language

### 2.1 Plain English

The target is English at level B1. These rules hold on every page (checked by provenance, except where a lint id is
named):

- One idea per sentence. Present tense, active voice. "You" for the reader. "We" only for a derivation or a tutorial
  step done together ("we add a field"). The engine is the actor of its own choices: "Strata stores…", never "we
  store…".
- Say what something is for before saying how it works. Say why before stating a rule. Put a condition before its
  instruction: "To see the cascades, open the Lighting view."
- Prefer concrete nouns and verbs: "the renderer skips meshes that are not loaded yet", not "unloaded assets are
  handled gracefully".
- No idioms, no jokes that need a culture, no wordplay that carries meaning (`idiom`).
- The same thing always has the same name; the glossary decides it (`other-name`). Engine names are written as the
  code writes them, in backticks (`SceneRenderer`, `viewport.capture`); UI labels as the UI writes them, in bold
  (**File ▸ New Project...**). Checked by names.
- Keep three kinds of claim apart in the wording: how it works everywhere ("GPUs…"), how most engines do it ("engines
  usually…") and what Strata does ("Strata…").
- Headings are in sentence case (`heading-case`, warning). A heading says what its section establishes ("Fixed steps
  make physics repeatable"); in a tutorial it names the task ("Make the ball roll"). Headings go at most four levels
  deep and hold no math (`deep-heading`, spike).
- Steps and orders are numbered lists; other lists use bullets. The items of a list have the same grammatical form.
- Link text says where the link goes; never "here" or "this page" (`link-text`).
- Never copy sentences from the inventories, `AGENTS.md`, the Developer Guide or the engine's Manual (`copied-text`).
  Words of another text that must be exact go in a block quote of at most 60 words that names its source
  (`block-quote-length`). `long-quote` is the rule of code fences (§9.1).
- No mention of how the book was made, of the agents that wrote the book, or of the plan. Pages about AI agents as a
  way to use Strata (`make/with-an-agent`, part `automation`) are not affected.

### 2.2 What the linter measures

Definitions the linter uses:

- **Prose** is the visible text of a page: paragraphs, list items, headings, table cells written by hand, asides,
  answers, and the captions and alternative texts of the page's figure manifest. It excludes the front matter, code
  fences, display math, generated tables and HTML comments.
- A **word** is a run of characters between spaces in prose. An inline code span and an inline formula each count as
  one word. Link targets do not count; link text does.
- A **sentence** ends at ".", "?" or "!" followed by a space or the end of its block, outside code and math. A colon
  that introduces a list ends a sentence. A list item without a final stop is one sentence. Headings and table cells
  are not sentences.
- A **paragraph** is a block of prose lines between blank lines. Each list item counts as a paragraph of its own.

| Id | Rule | How it is measured |
| --- | --- | --- |
| `sentence-mean` | The sentences of a page average at most 20 words. | Mean words per sentence over the whole page. |
| `sentence-max` | No sentence has more than 35 words. | Words of each sentence. |
| `paragraph-length` | A paragraph holds at most five sentences. | Sentences per paragraph. |
| `prose-run` | At most 500 words of prose come without a break. | Words between two headings, figures, code fences, lists, tables, display formulas or asides. |
| `word-list` | Every word is on the book's word lists (§2.3) or is a word of a glossary name. | Each prose word, as written and without the endings -s, -es, -ies (as -y), -ed, -d, -ing, -er, -est and -ly. Every word of a glossary name or alias passes, alone too, marked or not ("preset" of "CMake preset"). The entries (list items) of `## Further reading` are not read: they name people and works (`critique/rulings-11.md`, R54). |
| `acronym` | An acronym is spelled out at its first use on the page. | A word of two or more capital letters (digits allowed), outside code and UI labels, must at its first use stand right before or right after its expansion in parentheses: "graphics processing unit (GPU)". The exemptions are in `tools/data/acronyms.json` (spike): KB, MB, GB, TB, PC, OK, 2D, 3D, USB and the names of products and companies (NVIDIA, AMD, RTX). |
| `banned-word` | None of these words or phrases: simply, just, obviously, of course, clearly, basically, easy, easily, trivial, trivially, needless to say, as everyone knows, it follows, it is easy to see. They tell a reader who is lost that the reader is the problem. | Whole words, any case. Write "only" or "immediately" where "just" was meant. |
| `abbreviation` | No "e.g.", "i.e.", "etc.", "vs.", "cf." or "approx.". | Exact strings. Write "for example", "that is", "and others", "against", "compare" and "about". |
| `contraction` | No contractions. | "n't", "'re", "'ve", "'ll", "'d", "'m", and "it's", "that's", "there's", "what's", "here's", "let's". A possessive "'s" ("Strata's") is allowed. |
| `phrasal-verb` | No phrasal verb where a single verb exists. | The list `tools/data/phrasal-verbs.json` (spike), each entry with its replacement: find out → learn, set up → create or prepare, carry out → do, come up with → invent, look into → examine, point out → show, figure out → understand, go on → continue, go back → return, get rid of → remove, turn on → enable, turn off → disable. |
| `idiom` | No idioms. | The list `tools/data/idioms.txt` (spike): under the hood, out of the box, on the fly, rule of thumb, in a nutshell, off the shelf, the bottom line, at the end of the day, a piece of cake, kick off, and others. The provenance reviewer finds the idioms the list misses. |
| `pronoun-start` | No paragraph starts with a pronoun whose noun is in another paragraph. | The paragraph's first word is "It" or "They", or is "This", "That", "These" or "Those" followed by punctuation or by a verb of `tools/data/verbs.txt` (spike): "This means…" fails, "This step…" passes. |
| `noun-stack` | No more than two nouns in a row (*warning*). | Candidates: three or more words in a row, outside code, UI labels and names, none of them on `tools/data/function-words.txt` or `tools/data/verbs.txt` (spike) and none ending in -ly, -ing or -ed. The linter cannot tell nouns from other words for certain, so the reviewers decide. |
| `passive` | Active voice (*warning*). | A form of "be" followed within two words by a word ending in -ed or -en, or by an irregular past participle of `tools/data/verbs.txt`. |
| `link-text` | Link text says where it goes. | Link text equal to "here", "this", "this page", "link", "click here" or "read more". |
| `copied-text` | Nothing is copied from the sources. | A run of ten or more words (lowercased, punctuation removed) that also occurs in `plan/inventory/*.md`, or in `AGENTS.md`, `Docs/DeveloperGuide.md` or `Docs/Manual/*.md` at the pin. Block quotes and code are exempt. |
| `heading-case` | Headings and titles in sentence case (*warning*). | A capitalized word after the first that is not a name of `tools/data/names.txt`, a glossary term written with capitals, or code. |
| `size` | The page's length fits its size. | Prose words: S 600 to 2,250; M 2,251 to 4,000; L 4,001 to 6,500; XL 6,501 to 10,000. A page that does not fit asks the planner for the next size; nothing is cut to fit (`critique/rulings-4.md`, R7). Pages of kind R have no size check (§7.6). |
| `time` | The front matter's `time` is honest. | The reading floor is prose words ÷ 120 plus lines of code shown ÷ 10, rounded up to a multiple of 5 minutes. `time` is at least the floor on every page; on concept and internals pages it is at most twice the floor. |

The linter also keeps the spike's rules `other-name`, `dollar-digit`, `scope-in-prose`, `html-in-prose`,
`deep-heading`, `unfinished`, `unlabelled-code`, `no-language`, `long-quote` and `mdx` (spike: `tools/lint.py`), and
adds `block-quote-length` (§2.1: a block quote of prose has at most 60 words and a line that names its source). The
rules of terms (§3), mathematics (§4), code (§9), steps (§10) and numbers (§13) are listed in their sections.

For each page the linter writes a reading report: words, sentences, the mean and the longest sentence, the paragraphs
over the limit, the new terms per section, the words outside the lists, and the warnings. The provenance reviewer
reads it with the page.

### 2.3 The words a page may use

A page may use these words without defining them:

1. The words of `tools/data/common-words.txt` (spike): the 8,991 headwords of the frequency bands 1 to 14 of 12dicts'
   `2+2+3frq` with their inflected forms; 14 is the smallest last band that gives at least 8,000 headwords
   (`critique/rulings-11.md`, R50). The list is public domain or permissively licensed, so that it puts no terms on the
   book (`critique/rulings-6.md`, R20): it is 12dicts, public domain. The file's first line names the list and its
   license. A word of a field (shader, texture, compiler) stays a glossary term whatever band it is in: the glossary
   wins over the list.
2. The words of `tools/data/extra-words.txt` (spike): everyday words the common list lacks (keyboard, screenshot,
   download), each with the persona item or the page that covers it. The part editor admits them.
3. The words of glossary names and aliases, each word alone too, marked or not, wherever they stand and however
   often (`critique/rulings-11.md`, R54). §3 says where a term is marked.
4. The names of `tools/data/names.txt` (spike): products, companies, file formats and people (Strata, Windows, Vulkan,
   Visual Studio, glTF, Blender). A name that the persona does not know is still taught: the list only exempts it from
   `word-list`.
5. Code in backticks, UI labels in bold, numbers and math.

A word outside these is replaced by a listed word, made a glossary term through the chapter's notes, or added to the
extra list by the part editor. The writer does not leave it on the page unresolved.

### 2.4 Five pairs of sentences

1. *Bad:* "The scene system descriptor order determines the update sequence."
   *Good:* "Each scene system says when it runs. The scene runs the systems in that order."
   *Why:* four nouns in a row hide who does what. The good version uses verbs.
2. *Bad:* "Because the renderer cannot wait for assets that are still loading, it skips meshes whose data has not
   arrived yet and draws them in a later frame once their upload has finished, which is why objects can appear a moment
   after a scene opens."
   *Good:* "The renderer never waits for an asset. It skips a mesh that is still loading, or draws a fallback in its
   place. The mesh appears in a later frame, after its upload ends."
   *Why:* 44 words and three claims in one sentence. The good version has one claim per sentence.
3. *Bad:* "Under the hood, the editor sets up a copy of the scene when you hit Play."
   *Good:* "When you start the game with **Ctrl+P**, the editor makes a copy of the scene. The game runs in the copy.
   Changes you make while it runs are lost when it stops."
   *Why:* an idiom ("under the hood"), a phrasal verb ("sets up") and slang ("hit"). The good version puts the
   condition first and says what the reader must know.
4. *Bad*, at the start of a paragraph: "This is why it never blocks."
   *Good:* "A command that must wait returns at once and finishes in a later frame. The editor keeps drawing while the
   command waits."
   *Why:* "this" and "it" point to nouns in another paragraph. The good version names the command and the editor.
5. *Bad:* "Obviously, assets are just loaded asynchronously."
   *Good:* "Assets load on other threads, so the game keeps running while a file is read."
   *Why:* two banned words, a word the reader does not know ("asynchronously") and the passive voice. The good
   version says what happens and what the reader gains.

### 2.5 An exemplar

This section shows the voice: a short passage that follows every rule of this file. It is written as it stands on the
home page of "delta time"; on another page the term would be marked `:term[delta time]{id=delta-time}`. After the
pilot, the planner names one pilot page as the book's exemplar page and adds its id here.

````md
## Moving at the same speed on every computer

Run a game on a fast computer and on a slow one. If the game ignores time, a ball rolls faster on the fast computer.
The fast computer draws more pictures each second, and the game moves the ball a little in each picture.

The engine draws one picture in each :term[frame]{id=frame}, one pass of its loop. The time from the start of one
frame to the start of the next is the **delta time**. Strata measures it in seconds.

To move at the same speed on every computer, the game multiplies the speed by the delta time.

Here is an example with small numbers. The ball should move 2 metres each second. At 50 frames per second, the delta
time is 1 ÷ 50 = 0.02 s. In each frame, the ball moves 2 × 0.02 = 0.04 m. After 50 frames, it has moved
50 × 0.04 = 2 m.

$$
d = v \, \Delta t
$$

Read the formula as "d equals v times delta t". $d$ is the distance the ball moves in this frame, in metres. $v$ is
its speed, in metres per second. $\Delta t$ is the delta time, in seconds.

The code does the same multiplication once per frame. Look at the line that changes the position:

```cpp pseudocode
// Runs once in every frame.
position = position + speed * deltaTime;
```

1. **Line 2:** a long frame has a large delta time, so the ball moves further in it. Over one second, the distances
   add up to the speed.

Check the formula at its limits. A frame that takes no time has $\Delta t = 0$, and the ball does not move. A frame
that takes a whole second moves the ball the full 2 metres at once.
````

## 3. Terms and the glossary

A **term** is a word or phrase with an entry in the glossary (`src/content/glossary.json`; its fields are in
[pipelines.md](pipelines.md), "Glossary"). Glossary links are explicit: the build never links terms on its own
(spike: the spike's glossary plugin still links first uses automatically, and its entries have no `id` field yet).

- **Defining.** A term is defined on its home page (the entry's `home`). A concept that a game maker acts on also has a
  use home in part `make` (book.md, "One home per concept"); the entry names it (`use`, spike), and the use home
  defines the term too, in the words a game maker needs. The definition stands somewhere on the page, best where the
  page first needs the term: the term in bold, in one sentence that says in plain words what it is. A use before it,
  in the test-out box or in a table, is no failure (`critique/rulings-11.md`, R54). Show the thing before naming it
  (§5).
- **Using.** On a page whose Needs closure holds the term's home, the first use of the term is marked
  `:term[text]{id=<entry id>}` (spike); `tools/markterms.py` writes these marks. The text is the words the sentence
  needs ("fixed steps"); the id names the entry. Later uses on the page are plain words. The mark opens the definition
  in a popover and links the entry ([site.md](site.md)). A use in a block quote, in the test-out box or in the link
  text of a Further reading entry asks for no mark and is no first use; a use in a sentence that already links the
  term's home, or right after the page's own bold definition of the term (the same or the next block), asks for none
  (R54).
- **Terms homed outside the closure.** A term whose home is not in the page's Needs closure is never used as if the
  reader knew it, and it is neither marked (`term-source` warns of a mark) nor linked by the tool (R54). The sentence
  that uses it says in plain words what it is, and links its home where that helps: "the
  [render scene](../draw/render-scene.md), the renderer's own list of what to draw". No question or exercise of the
  page needs such a term.
- **Two meanings.** A word with two meanings has two qualified entries ("pack block", "BC block"), and the
  unqualified word is never a term of its own; the mark's id chooses the meaning. A word that names a term is not used in its everyday sense: rephrase the sentence instead (an everyday word, below, excepted).
- **Everyday words and qualifiers** (rulings-11.md, R53). A term or alias that is one word of the common list
  (`tools/data/common-words.txt`, in any inflected form) needs no mark at an unmarked first use on a page that is
  neither its home nor its use home, and a writer's own mark of it, where the page uses the term's sense, stays valid.
  A name's trailing parenthesis only says which meaning the entry holds ("Clip (animation)"), so the lint matches the
  name before it and the rule on everyday words then applies to that name; the site matches no names, as it links
  only marks, by their id.
- **Other names.** An entry's `aliases` are the industry's other names; a page gives them once, in the definition's
  paragraph or in an `:::elsewhere` aside ("Unity calls this a GameObject"). An entry's `avoid` names are never used
  (`other-name`).
- **Words every persona knows.** Entries kept for readers of English as a second language, whose words are on G0's Has
  list ("folder"), carry `known: true` (spike) and need no mark.

| Id | Rule | How it is measured |
| --- | --- | --- |
| `term-mark` | The first use of a term whose home is in the page's Needs closure is a `:term` mark. | Glossary names and aliases (without a trailing parenthesis), whole words, any case, simple plurals; outside code, headings and UI labels; not a name of one common-list word; uses in block quotes, the test-out box and the link text of Further reading entries are skipped. A use in a sentence that links the term's home, or in the block of (or after) the page's bold definition of it, asks for no mark. A term homed outside the closure asks for none (R54). |
| `term-source` | A marked term is taught on the page or in its Needs closure (*warning*, R54). | The entry's `home` (or `use`) is the page itself or a page of the closure (`plan/check_outline.py` computes the closure). |
| `term-defined` | On its home page and its use home, a term is defined in bold. | An occurrence anywhere on the page is in bold and is a glossary name or alias of an entry whose `home` or `use` is the page (R54); without one, the first use outside the test-out box and tables is reported. |
| `term-paragraph` | At most one new term per paragraph. | A new term is a term defined on the page (`term-defined`). |
| `term-section` | At most four new terms per level-2 section. | The same count, per `##` section. A section that needs more is split. |

## 4. Mathematics for readers who fear it

Every formula that a page derives or uses for the first time comes in this order:

1. **The idea in words**, and a picture of it (an arrow, a curve, a lobe).
2. **One example with small numbers**, worked by hand: (1, 0) · (0.7, 0.7) = 0.7.
3. **The formula**, with each symbol read aloud in words and given its unit ("Σ is read 'the sum of'"), and the
   convention it uses (which space, which axes).
4. **The code** that computes it, a sketch or Strata's, with each symbol mapped to the code's name.
5. **A check at the limits**: what happens at zero, at one, at a very large value; the units; or the engine's own
   check (the white-furnace test, a debug view).

Rules:

- Derive only what the reader will use. A derivation of more than three steps goes in a `:::derivation` box (§12),
  which the reader may skip.
- Never put a formula in a caption unless the text explains it.
- Math uses the engine's conventions (`AGENTS.md`, "Renderer conventions"): the framebuffer's origin is top-left, NDC
  +Y is up, depth runs from 0 to 1 with reversed Z (near is 1), and front faces are counter-clockwise. A page that shows
  another convention names it and links `reference/notation`.
- The first time a page uses an operator symbol (Σ, ∫, ∂, ·, ×, ‖v‖, ∇), it says how the symbol is read and what it
  does (checked by provenance). `appendix/math-cheatsheet` lists every symbol with the page that teaches it.
- Each part whose pages use symbols has a notation table (symbol, how it is read, meaning, unit, the page that
  introduces it) on the part's index page, or on its first page when the part has no index page. `reference/notation`
  collects them all.
- Formulas are KaTeX: `$…$` inline, `$$…$$` on lines of their own. A dollar sign for money is written `\$`
  (`dollar-digit`).

| Id | Rule | How it is measured |
| --- | --- | --- |
| `math-symbols` | Each symbol is named at its first appearance on the page. | Every single letter, Greek letter or subscripted symbol of a display formula that the page has not named before appears as inline math in the block right after the formula. |
| `math-derivation` | Long derivations are in a `:::derivation` box (*warning*). | More than four display formulas in one level-2 section outside such boxes. |
| `math-g` | Game makers get results in words. | On pages on track G that are not primers, every display formula is inside a `:::note[The formula]` aside or a `:::derivation` box, and the paragraph before the aside states the result in words. |

## 5. The teaching loop

Every new idea follows the same five beats; a page is a chain of these:

1. **Show.** A picture, a short experiment in the editor, or a tiny program whose output surprises.
2. **Name.** The term, defined in one sentence (§3). At most one new term per paragraph.
3. **Explain.** Why it is so, from what the reader already has. Mathematics follows §4.
4. **Code.** The idea in plain words or as pseudocode first, then the smallest code that does it: a sketch, then
   Strata's real code (§9).
5. **Check.** A question or a small task in the text, with its answer hidden in `:::answer` until the reader opens
   it. These body checks need no `tests` attribute.

Mathematics and C++ are taught where they are needed. A page that needs a dot product has `basics/math-vectors` in its
Needs closure and repeats the one line of it that matters.

## 6. Front matter and the strips

### 6.1 Front matter

The build rejects a page without it (strips). The values marked "outline" must equal the page's row in the outline and
`plan/tracks.md`. `plan/check_outline.py` checks the outline itself: unique ids, Needs that exist, at most five page ids in a page's Needs,
and each Need earlier on every track of the page.

```yaml
---
id: core/time                    # the file's path under src/content/docs/, without .md
title: "Time: delta time, the fixed step and time scale"   # outline
description: "Why a game measures each frame's time, why physics runs in fixed steps, and what time scale does."
kind: concept                    # outline: primer | concept | internals | tutorial | how-to | reference
size: L                          # outline: S | M | L | XL
tracks: [E]                      # outline: any of G, B, E; [] for a page on no track
needs: [core/frame-loop, basics/math-change]   # outline; "a|b" for alternatives; [] for "-"
time: 45                         # minutes to read, and to do on primers, tutorials and how-tos
learn:
  - id: delta-time
    text: explain why a game scales movement by the frame's delta time
  - id: fixed-step
    text: explain why physics runs in steps of a fixed length, and what the accumulator holds
  - id: step-count
    text: compute how many fixed steps a frame runs at a given frame rate
since: 0.3.0                     # the first release whose engine had the page's subject
status: draft                    # draft | reviewed | final
---
```

The values of the example illustrate the fields; the outline row decides a real page's values.

| Key | Rule (checked by strips unless named) |
| --- | --- |
| `id` | Equals the file's path under `src/content/docs/` without `.md`. Never changes once published. |
| `title` | Equals the outline row's Title, in sentence case. Always in double quotes (`tools/pages.py check`): a bare value that holds a colon and a space is not valid YAML. |
| `description` | One sentence of at most 160 characters, for search results and link previews. Always in double quotes, as the title. |
| `kind` | The outline row's Kind, written as a word (P primer, C concept, I internals, T tutorial, H how-to, R reference). |
| `size` | The outline row's Size; the prose must fit it (`size`). A reference page has no size check (§7.6). |
| `tracks` | The outline row's Tracks as letters; each track's list in `plan/tracks.md` holds the page. |
| `needs` | The outline row's Needs: at most five ids, alternatives included, each earlier on every track the page is on; `a\|b` for alternatives. |
| `time` | Whole minutes, checked by `time`. Absent on reference pages. |
| `learn` | Two to five objectives, each `{id, text}`. The id is lowercase words joined by hyphens, unique on the page. The text says what the reader can do afterwards and starts with an observable verb (explain, compute, name, choose, write, build, find, predict, change, add, fix, trace, measure, compare, draw, export, create, run, set). Never "understand", "know", "learn" or "be familiar with". Absent on reference pages. |
| `since` | The first release whose engine had the page's subject: the earliest tag `vX.Y.Z` (no release candidates) whose tree holds it, or `0.3.0` for anything older than the first tag. The book's own release (the pin's `release`) when the subject is new in it. Required on pages of kinds concept, internals, tutorial and how-to in parts 1 and 3 to 21 (`make` to `engineering`); absent elsewhere. The writer's notes give the evidence (technical). A page whose "Where it lives in Strata" files are all absent at `v0.7.0` and whose `since` is older is reported (*warning*). |
| `status` | `draft` (written), `reviewed` (findings answered, confirmed where process.md asks), `final` (after the part's edit pass, with its pictures taken and re-read, and a current stamp for tutorials). |

Compared with the spike's schema (`src/content.config.ts`), this front matter adds `id`, `size`, `time`, learn ids and
`since`, writes tracks as letters, renames `prerequisites` to `needs`, and drops `level` (computed, below) and `engine`
(the pin gives it) (spike).

### 6.2 The top strip

The build draws it from the front matter. It shows: the kind badge; one badge per track, with the accessible names
"Game maker" (G), "Beginner" (B) and "Engine builder" (E); the level and what it means; "About N minutes"; a "New in
0.8.0" badge when `since` equals the book's release; "After this page you can" with the learn texts; "Before you start"
with the Needs as links (an alternative shows as "X or Y"; a page with `needs: []` shows its part's first page); on the
first page of a part with fewer than eight pages, which has no index page, "Before this part" with the part's Needs of
the part (`outline-1.md`) as links; and the engine release and commit of the pin.

The **level** is computed from the Needs closure and is never written:

| Level | Holds when | The strip says |
| --- | --- | --- |
| 1 | Every page of the closure is in parts 0 to 2 (`start`, `make`, `basics`). | "Level 1: needs only Start here, Making games and Foundations." |
| 2 | Not level 1, and no page of the closure is in a part numbered 6 or higher other than the page's own part. | "Level 2: also needs the engine's core (parts 3 to 5) or earlier pages of this part." |
| 3 | The closure holds a page of a part numbered 6 or higher other than the page's own part. | "Level 3: builds on other parts of the engine." |

### 6.3 The bottom strip

The bottom strip is written by the writer, as level-2 sections with these exact headings in this order (strips):

| Kind | The body ends with | Bottom strip |
| --- | --- | --- |
| primer | `## Common mistakes` | `## Summary` · `## Check yourself` · `## Practice` · `## Where the book uses it` · `## Further reading` |
| concept | `## Common mistakes` | `## Summary` · `## Check yourself` · `## Exercises` · `## Where it lives in Strata` · `## Further reading` |
| internals | `## Changing it safely`, or `## What went wrong before` when it exists | as concept |
| tutorial | its last step section | as concept |
| how-to | `## Variations` | as concept |
| reference | the generated tables | `## Where it lives in Strata` |

- **Summary**: a bulleted list with one item per learn line, in the learn lines' order. Each item is one or two
  sentences that answer the objective (strips counts the items).
- **Check yourself**: three to six questions (§8).
- **Exercises**: one to four exercises; **Practice** on primers: three to eight (§8).
- **Where it lives in Strata**: on pages on track G or B, the panels, menus, commands, components and settings of the
  page's subject, and files only where the reader opens them; on pages only on track E, the files, classes, tests,
  commands and settings. Every name is checked by names.
- **Where the book uses it** (primers): at least three pages that use what the primer teaches, each with one sentence
  on what it uses. Each linked page has the primer in its Needs closure (strips).
- **Further reading**: sources, each with one line on what it gives and at what level (beginner, intermediate,
  advanced). Every claim about other engines or the field cites one of them.

## 7. Shape per kind

Each page is exactly one kind. The body sections of each kind come in the order given. Headings written in backticks
below are exact (strips); the other sections take headings that say what they establish.

### 7.1 Primer (P)

A lesson from zero on something that is not Strata's own: programming, mathematics, how computers work.

1. **The "Test out" box** (`::::test-out`, spike), before any heading: exactly five questions, each followed by an
   `:::answer{tests="…"}`. Together the answers' `tests` cover every learn id. At least three questions ask the reader
   to do something (compute a value, predict a program's output, write one line), not to recall a word. No question
   repeats a Check-yourself question. The plugin writes the box's title and its instruction: answer all five without
   opening the answers; if all five are right, skip the page and go to the next page of your track (linked).
2. `## Why you will need this`: what the reader will do with it in the book, naming two or three of the pages that
   use it.
3. **The idea on the smallest example**: Show, Name and Explain on one small case.
4. **Worked examples**: small steps, each an `:::example` (§12) and then a try-it, a body check with its answer.
   Several similar examples with less help each time (faded examples) where the idea needs practice.
5. `## Common mistakes`: each mistake, the symptom it produces, and the fix.
6. The bottom strip. Its Practice exercises run on the reader's workbench (§8).

### 7.2 Concept (C)

1. **The problem as a reader meets it**: a story, a picture or an experiment (Show).
2. **The naive answer and where it breaks.**
3. **The idea**: the mental model in one paragraph and one diagram, with its terms named.
4. **The approaches engines use**: two to five, each introduced by the flaw of the one before, ending with a table of
   their cost, quality, complexity and who uses them (with sources).
5. **Strata's choice and its reason** (a `:::why` aside where it is a design decision), with a bridge to the
   internals pages.
6. **What Strata's choice cannot do**, and what Strata does not do here, with a link to `appendix/not-in-strata`.
7. `## Common mistakes`.
8. The bottom strip.

At least one `:::example` stands before the bottom strip (strips).

### 7.3 Internals (I)

1. **The job** in one paragraph: what this part of Strata is responsible for, and what it is not.
2. `## The problem and how engines solve it`: the approaches with their costs, in at most a fifth of the page's prose
   words (strips counts them). When a concept page of the part holds this, the section is one paragraph that links it.
   The part brief names the internals pages that carry the full section.
3. **The map**: a diagram of the files and who calls whom, which thread runs what, and what each part owns.
4. **The contract**: what callers may assume and what they must do, each rule with its reason (a `:::rule` aside for a
   rule of `AGENTS.md`).
5. **A toy version**: a sketch of 30 to 80 lines that does the job in the simplest way. It may be split into several
   fences.
6. **The real code**, walked through in the order data flows, with each difference from the toy and its reason
   (threads, budgets, failures, hot reload). At least three quotes (spike: `tools/excerpts.py check`).
7. `## Alternatives Strata did not choose`: a table with the columns Technique, Who uses it, What Strata would gain,
   and What Strata would lose. Each "who uses it" has a source in Further reading.
8. `## How it is tested`: the test suites, what they check and how to run them.
9. `## Changing it safely`: the extension points, the rules of `AGENTS.md` that apply with their reasons, and the
   checks a change here must pass.
10. `## What went wrong before`: a real bug and its regression test, when the history has one; otherwise omitted.
11. The bottom strip. Its exercises include one "trace it yourself" exercise: follow the real code with a debugger or a
    search.

At least one `:::example` stands before the bottom strip (strips).

### 7.4 Tutorial (T)

1. `## What you will make`: one or two sentences and a picture of the result (`::figure`).
2. `## What you need`: the starting point (a template, a copy of a sample, or the end state of an earlier tutorial,
   with its checkpoint download); every file to import, with its source and license (from the release's
   `Samples/*/Assets/` or the book's tutorial asset pack, [pipelines.md](pipelines.md)); the time it takes; and, for a
   tutorial that changes the engine, the source build of `core/first-change`.
3. **Step sections**, each a small goal named as a task ("Make the ball roll"), each holding numbered steps that state
   what §10 lists. Each section ends with a `::checkpoint{stage=…}` (spike): the project as it is now, downloadable,
   and a picture headed "You should now have". Each section is one stage of the page's tutorial file, which the
   tutorial tool runs ([pipelines.md](pipelines.md)).
4. The bottom strip. Its Summary says what the reader made and learned; its exercises are open extensions ("make it
   yours") with hints and worked solutions.

A tutorial that changes the engine (track E) quotes each change from its patch, and its "You should see" is the build
or test output, shown as a text capture.

### 7.5 How-to (H)

1. The goal in the first paragraph (the title names it) and, as a list, what must be true before the first step.
2. Numbered steps that state what §10 lists.
3. `## Result`: what the reader has now, with a picture when it is visible.
4. `## Variations`: the same goal under other conditions.
5. The bottom strip.

No theory: a section says why in at most two sentences and links the concept page.

A how-to of block A of `make` that changes Coin Run ends in `## Result` with a download of its end state
(`critique/rulings-7.md`, R32).

### 7.6 Reference (R)

Generated tables, with one paragraph on top that says what the table is and how to read it. Hand-written notes are
merged in where the generator allows. No learn lines, no questions, no `time`.

Pages of kind R, the four of `appendix` included, have no size check (`size`): their size is the measure of generated
volume that their Fit line in the allocation states, and their words stay in the book's totals
(`critique/rulings-7.md`, R33).

### 7.7 The part's index and review pages

Parts with eight or more pages also have two generated pages that are not rows of the outline and carry no kind.
Their front matter holds `id`, `title`, `description`, `tracks` (the part's), `status` and `generated: index` or
`generated: review` (spike).

- `<part>/index`: the part's map (the Needs graph of its pages), the pages outside the part that its pages need, what
  the reader can do afterwards (the learn lines of the part's pages), the notation table (§4) and one paragraph written
  by the part editor. The index of `basics` also names, for each primer, the first part whose pages need it.
- A part with fewer than eight pages has no index page. Its first page shows what an index page would hold of the
  part's prerequisites: "Before this part" in the top strip (§6.2) lists the part's Needs of the part, and its notation
  table (§4) stands at the end of its first section. The build draws both; the writer writes neither.
- `<part>/review`: questions across the part, collected from the pages' Check-yourself sections, and five to ten
  cumulative exercises written by the part editor, each with a worked solution.

## 8. Questions, exercises and answers

- **Answers are always present and hidden**: each question and each exercise is followed by an `:::answer` (or
  `:::answer[Worked solution]`) block. In Test out, Check yourself, Exercises and Practice, the answer carries
  `{tests="<learn ids>"}` (spike), the ids of the objectives it tests. Every learn id appears in the `tests` of at
  least one Check-yourself answer (strips).
- **What an answer holds.** For a multiple-choice question: why each option is right or wrong. For a prediction: the
  result and the reasoning. For an exercise: the solution worked through step by step, never only stated. For a design
  exercise: a discussion of good answers and their trade-offs.
- **Check yourself**: three to six questions. Kinds: multiple choice whose wrong options are real mistakes (from the
  page's Common mistakes, the inventories' "Newcomer error" items and their section 5, "Rules and pitfalls"),
  predict-the-output, and short computations.
- **Exercises**: one to four (Practice on primers: three to eight), ordered from easy to hard. Each starts with its
  level in bold: **Basic.**, **Medium.** or **Hard.** (`exercise-order`: the levels never go down). Kinds:
  - *predict, then run*: say what will happen, then try it;
  - *modify*: change a value or a line and observe;
  - *Parsons problem*: put given lines in order. The shuffled lines are a `text` fence; the answer shows the ordered
    code as a sketch, which the checks compile;
  - *faded examples*: three similar tasks with less help each time;
  - *trace* (track E): find where something happens in the real code, with a debugger or a search; the solution names
    the file and function and shows the path;
  - *extend* (track E): add a small feature; the solution is a patch against the pin;
  - *design*: an open question with no single answer;
  - *editor task* and *command*: do something in the editor, or run a command, and check the result.
- **A worked example comes before the first exercise.** On primers, concept pages and internals pages, at least one
  `:::example` stands before the bottom strip (strips). On tutorials and how-tos, the steps are the worked example.
- **At least one exercise is done, not only answered.** What kind it is depends on the tracks of the page, and a
  page on several tracks meets the rule of each:
  - on track G or B, a page that comes before `make/first-script` on that track has an editor task or a command (on
    track B, `basics/computer` and `basics/tools` among them);
  - on track G, a later page has an exercise done in the editor or in a script;
  - on track B, a later page has an exercise that runs code on the reader's workbench;
  - on track E, a page of `start` or a primer before `basics/programming-1` has an editor task; from
    `basics/programming-1` on, the exercise runs code on the workbench that the page's Needs closure has set up (the
    list below);
  - on every track, the exercise's answer names its solution file
    (`:::answer[Worked solution]{tests="…" solution="…"}`, spike): a command script, a sketch with its output, or a
    patch, which the book's checks run and stamp ([pipelines.md](pipelines.md)). The reader gets the file from the
    page: a sketch is shown in full in the answer, with its output; a command script or a patch is linked as its
    download under `<base>/downloads/solutions/` (pipelines.md §6.3). An answer never sends the reader to the book's
    repository (`critique/rulings-6.md`, R25). The pages before `start/install` on their track (`start/welcome`,
    `start/how-to-read`) and reference pages are exempt.
- **The reader's workbench** grows along the tracks. An exercise uses only what the page's Needs closure has set up:
  - the editor (from `start/install`);
  - the playground: a Strata project made from the Basic 3D template whose script prints to the **Console** panel and
    moves an entity. The programming primers run their code in it, so no second toolchain is needed;
  - a terminal and a code editor (from `basics/tools`);
  - git (from `basics/git`);
  - a C++ compiler and CMake run by hand (from `basics/build`);
  - the engine's source build and its tests (from `core/first-change`).

## 9. Code

### 9.1 Introducing and following a fence

- **Before every fence**, a paragraph says in plain words what the code does and what to look for (`code-intro`). On
  pages of tracks G and B and pages of level 1, the idea comes first in plain words or as pseudocode, before any real
  code.
- **After every fence**, the text says what the code showed (`code-follow`): numbered callouts, a paragraph, or both.
  A fence of ten or more lines gets callouts (`callouts`). Callouts are a numbered list right after the fence, at most
  five items; each starts with **Line N:** or **Lines N–M:**, using the numbers the fence shows (the engine's line
  numbers in a quote), and says why the line is there, not what it does.
- **Python fences.** Reading Python has no home page, so every Python fence is followed by its explanation line by
  line (`code-follow`). The paragraph that introduces the first Python fence of a page also says, in one or two
  sentences, what in the fence differs from C++ (`critique/rulings-7.md`, R31).
- **The first use of a C++ feature** whose home is not in the page's Needs closure gets a `:::question` aside before
  the fence ("What is `std::optional`?"): at most two sentences and a link to the feature's home (`cpp-feature`).
  `start/how-to-read` teaches how to read code the reader does not understand yet; G pages may link it.

| Id | Rule | How it is measured |
| --- | --- | --- |
| `code-intro` | A fence has an introduction. | The block before the fence is a paragraph. Exempt: a fence in a tab whose sibling tab states the same step in words, and an `output-of` fence right after its sketch. |
| `code-follow` | A fence is followed by what it showed; a Python fence, by its explanation line by line. | The block after the fence is a paragraph or a numbered list, or the `output-of` fence of the same sketch followed by one. |
| `callouts` | Callouts are few and point at lines. | A fence of 10 or more lines is followed by a numbered list of 1 to 5 items, each starting with "Line N:" or "Lines N–M:" inside the fence's line numbers. |
| `long-quote` | Quotes have a readable length. | An engine quote has 5 to 60 lines. On pages of tracks G or B and on level-1 pages, every fence has at most 25 lines; a longer piece is shown in parts with text between them. |
| `cpp-feature` | Untaught C++ is explained where it appears. | In C++ quotes and sketches, the patterns of `tools/data/cpp-features.json` (spike), each with its home page. A feature whose home is neither the page nor in its Needs closure needs a `:::question` aside before its first fence that links the home. One finding per fence names every such feature and every home to link, so one run shows them all (R54). |

The seed of `tools/data/cpp-features.json` (the basics brief completes it):

| Feature | Home |
| --- | --- |
| `int`, `float`, `double`, `bool`, variables, operators, `if`, `else` | `basics/programming-1` |
| `for`, `while`, functions, `std::vector`, `std::array`, `struct` | `basics/programming-2` |
| `class`, `public:` and `private:`, member functions, references (`&` in a type), pointers (`*` in a type, `->`, `nullptr`), `std::optional`, `has_value`, `value_or`, `#include`, header and source files | `basics/programming-3` |
| destructors, `Ref<T>`, `Scope<T>`, `std::unique_ptr`, `std::shared_ptr` | `basics/cpp-memory` |
| inheritance (`: public`), `virtual`, `override`, `= 0` | `basics/cpp-classes` |
| `template <`, lambdas, `std::unordered_map`, `std::map`, the standard algorithms | `basics/cpp-generic` |
| `std::move`, `&&` in a type, `constexpr`, `std::variant`, `std::span`, `requires`, `concept` | `basics/cpp-modern` |
| `std::thread`, `std::mutex`, `std::atomic`, `memory_order` | `basics/threads` |

### 9.2 Quotes, sketches and pseudocode

- **Strata's code is quoted, never retyped.** A fence names its source and lines; the excerpt tool fills and checks it
  ([pipelines.md](pipelines.md) gives the format). The spike's form is `src="<engine path>#L<first>-L<last>"`, with
  `mark="L<n>,L<a>-L<b>"` in the engine's line numbers; while a page is written, `src="<path>#<symbol>"` names a
  symbol that `tools/excerpts.py fill` turns into lines (spike). Code of the book's own files and of vendor libraries
  uses the source namespaces of pipelines.md, `book:` and `vendor:<lib>/` (spike: not in the spike's tools yet).
  Nothing is edited inside a quote; elisions are separate quotes. A long function is split into several quotes and
  walked through.
- **Code that is not in the engine is labelled.** A **sketch** (`sketch="<file>"`, a copy of a file of `sketches/`
  whose name starts with the page's id, as pipelines.md says) is correct, minimal, commented on the lines that carry the
  idea, and written in the engine's style (Hazel naming, tabs, Allman braces). The checks compile every sketch; a
  sketch shown with output runs, and its output (an `output-of="<file>"` fence) is compared. **Pseudocode**
  (`pseudocode`) is never compiled. Code that is **wrong on purpose** (to show an error) is a sketch labelled so,
  and the error shown is the compiler's real output.
- **Output shown is real.** The output of a program, a command or a tool comes from a sketch's run or a text capture
  ([pipelines.md](pipelines.md)), never typed.
- **Languages**: C++20 for the engine and scripts; Slang (HLSL syntax) for shaders, with the binding registers shown
  and, on the CPU side, where each binding is filled; JSON for commands and documents; CMake; shell lines that work in
  PowerShell and in a POSIX shell (OS tabs when they differ); Python only for tools.
- **Commands** are shown as the editor command with its parameters and, where it exists, the UI path
  (**Menu ▸ Item**). `start/how-to-read` teaches how to read a command. Game makers are never told to edit `.stscene`,
  `.stmat`, `.stproj` or `.meta` files by hand.
- **Keys** are written in bold with "+": **Ctrl+Z**, with the macOS key after it where it differs (**Cmd+Z** on
  macOS).

## 10. Steps: what every step states

Every numbered step of a tutorial, and of a how-to on track G or B, states four things (`step-parts`: each top-level
item of a step list holds "**You should see:**" and "**If you do not see it:**"):

1. **The action.** In the editor, as a tab set with `sync=how` (spike): the tab "In the editor" holds the exact clicks
   and keys (UI labels in bold, menus as **Menu ▸ Item**); the tab "With a command" holds the editor command. On pages
   of track G the command tab is optional reading: the editor tab is complete on its own. A step that changes code
   names the file and shows the change.
2. **You should see:** what changed, in words, with a whole-editor picture wherever the screen changes. The figure
   manifest marks the control to use (pipelines.md gives the field).
3. **If you do not see it:** the one or two likely causes and the way back to the state before the step.
4. Optional, **Why:** at most two sentences and a link to the concept page.

A step that has no menu or button says so in its first sentence ("This step has no menu or button: run the command.")
and shows only the command. The rule for its page depends on the page's tracks (strips; `critique/rulings-7.md`,
R33):

- **Tracks G and B.** The page that teaches running a command is in the page's Needs closure.
  `make/automated-playtests` teaches running a command script (the editor's `--commands`), and `make/commands` teaches
  StrataCLI. A command-only step that runs a script needs the first; one that calls a command needs the second. A page
  that comes before that page on track G or B therefore has no such step: the allocator moves the step to a later
  page, or the page's starting checkpoint holds its result (as `make/animation`'s holds an animation controller).
- **Track E.** A page that comes after `editor/commands` on track E has it in its Needs closure. A page before
  `editor/commands` that needs a step only a command can do gives the complete line to paste, one sentence on what it
  does, and a link forward to `editor/commands`. `editor/commands` is then no Need of the page: `start/how-to-read`
  teaches how to read and run a command (`critique/rulings-4.md`, R11).
- **A page on track E and on track G or B** follows the rule for tracks G and B.

OS-specific steps use a tab set with `sync=os` and the tabs "Windows", "Linux" and "macOS" (spike).

## 11. Figures

- **Pictures of the engine** are rendered by the engine from a recipe ([pipelines.md](pipelines.md)). A writer asks
  for one by adding an entry to the chapter's figure manifest with what it must show. A picture is placed with
  `::figure{id=…}` and a before-and-after slider with `::compare{id=…}` (spike).
- **Rendering features**: the effect off and on (as a slider) where it has a switch, its debug view where one exists,
  a sweep of its main setting, and a crop where detail matters. The part brief lists which page gets which.
- **Tutorials**: a picture of the result at the top, a whole-editor picture after every step that changes the screen
  (with the control to use marked), and a "You should now have" picture at each checkpoint.
- **Text captures**: the output of a command or a tool is a text capture in a fence, re-run at each pin move
  ([pipelines.md](pipelines.md)).
- **Diagrams** are Mermaid when a graph or a sequence is enough, otherwise SVG drawn for the page. One idea per
  diagram, labels in words, readable in the light and the dark theme, and never color alone to carry meaning. The
  fence carries its caption and its alternative text as `caption="…"` and `alt="…"` (site.md, "Diagrams"). A name in
  a diagram that is a Mermaid keyword (`loop`, `end`, `alt`, `opt`, `par`, `note`, `class`, `state`, `graph`,
  `subgraph`) gets an alias (`participant L as Loop`) or quotes; otherwise the renderer fails or draws something else.
- Every figure has a **caption** that says what to notice ("the far cascade covers four times the area at the same
  resolution, so its texels are larger") and **alternative text** that says what it shows. Numbers in a caption come
  from the recipe's recorded values, written `{stats.x}` (pipelines.md).
- A figure that shows a CC BY file names that file's author and license in its caption; `appendix/credits` holds the
  full entry. At the pin the one such file is the Open World sample's fox (`critique/rulings-6.md`, R22).
- No pictures from other engines or books. A technique Strata lacks is drawn as a diagram.

## 12. Asides and directives

The build fails on a directive not in this table (site.md). Directives marked (spike) are new or differ from the spike.

| Directive | Use and rule |
| --- | --- |
| `:::note`, `:::tip`, `:::caution`, `:::danger` | Extra information; practice; a mistake people make; data loss or crashes. |
| `:::why` | A design decision and its reason. |
| `:::question` | A question a reader would ask here, answered. For a C++ feature (§9.1): at most two sentences and a link. |
| `:::history` | What Strata did before, in which release, and why it changed. |
| `:::elsewhere` | How other engines do it, with sources in Further reading. |
| `:::rule` | A rule of `AGENTS.md` in plain words, with its reason and a link to `AGENTS.md` at the pin. Its exact words, when needed, go in a block quote of at most 60 words. |
| `:::simplified` (spike) | What the text leaves out, why that is safe for now, and a link to the page with the full story (`simplified-link`: the aside holds a link). The later page links back: "Earlier we said…". |
| `:::analogy` (spike) | One analogy for one concept, reused on later pages. Its last paragraph starts with "**Where it breaks:**" (`analogy-limit`). An analogy that leads to a wrong prediction about the engine is dropped. |
| `:::example` (spike) | A worked example: the problem, every step worked, the result. |
| `:::derivation` (spike) | A collapsed box titled "Where this comes from", whose first line the plugin writes: "You can skip this: the rest of the page does not need it." |
| `::::test-out` (spike) | The Test out box of a primer (§7.1). Only on primers, before any heading. |
| `:::answer`, `:::answer[Worked solution]` | A hidden answer (§8). `tests` and `solution` attributes (spike). |
| `::::tabs{sync=…}` with `:::tab[Label]` | Tabs: `sync=how` ("In the editor", "With a command"), `sync=os` ("Windows", "Linux", "macOS"). |
| `::figure{id=…}`, `::compare{id=…}` | A picture or a slider from the figure manifest (§11). |
| `::checkpoint{stage=…}` (spike) | The end of a tutorial section (§7.4). |
| `:term[text]{id=…}` (spike) | A glossary term's first use on a page (§3). |
| `:since[0.8.0]` (spike) | At the start of the first paragraph of a section about a feature new in the book's release: shows "New in 0.8.0". |

## 13. Numbers, versions and honesty

- **Numbers** come with units, written with a space (16.7 ms, 2 m, 19 %), and with where they were measured. The
  reference machine is an i7-13700K with an RTX 5090, Windows 11, Release builds (`Docs/DeveloperGuide.md`);
  "on the reference machine" links its description in `reference/performance`.
- **On pages of track G**, a time measured on the reference machine also gives its share of a frame at 60 frames per
  second ("2.1 ms, 13 % of a frame at 60 frames per second") and says that a slower GPU takes longer (`g-frame-share`:
  a number followed by "ms" on a G page has "%" in the same sentence). No page states a time on another machine unless
  it was measured there, and then the page names that machine.
- **Counts that the engine can change** (commands, host functions, components, settings) are never typed in prose. A
  page states them through a generated value (site.md gives the form) or names the test that pins the count.
- **Pages the outline marks W8r** state no preset value in prose; the values come from generated tables (`w8r-preset`:
  on such pages, a number in the same sentence as Low, Medium, High or Ultra fails).
- A claim about the engine is true of the code at the pinned commit, and the page names the file. A claim about other
  engines or the field has a source in Further reading. When the inventories and the code disagree, the code wins.
  When the engine's own docs and the code disagree, the code wins, and the page does not repeat the docs' mistake (the
  part brief lists the known ones). What a writer could not verify goes in the chapter's notes for the reviewer, never
  onto the page as fact.
- **Never state something false to make it simpler.** Say "for now, assume…" or "in most cases…" and add a
  `:::simplified` aside. Bound a claim in time and scope ("in Strata 0.8.0", "on desktop GPUs").
- **Never promise what the engine does not do.** An experimental feature says so in the first paragraph of its page
  or section, with what that means for a game (it may change, it may be slow). What Strata does not do is stated where
  a reader would look for it, with a link to `appendix/not-in-strata`.
- A feature new in the book's release is labelled "New in 0.8.0": the whole page through `since`, a section through
  `:since[0.8.0]`.
- The engine release and commit a page was checked against come from `engine.pin` and are shown on every page; no
  page writes them.
- **At a pre-release pin the programs report the previous version.** At `822a7a46` the project's version is 0.7.0
  (`CMakeLists.txt:4`), so `c_EngineVersion` (`Strata/src/Strata/Core/Version.h.in:17`), the `engineVersion` of
  `editor.status` (`StrataEditor/src/Editor/EditorStateCommands.cpp:777`) and the version a window, the launcher or
  `--version` shows say 0.7.0, while `engine.pin` says `release 0.8.0`. Neither is a mistake, and no writer or reviewer
  corrects one by the other. A text figure leaves the version out (`keep` for a command's result, `redact` for a program's output, pipelines.md
  §5.2); a page that must show it
  says in one sentence that a pre-release build reports the previous release. The pin move to `v0.8.0` refreshes
  such figures and sentences.

## 14. Checks before a page leaves the writer

A page enters review only when all of these pass (process.md lists the writer's exit checks):

| Tool | Checks |
| --- | --- |
| `tools/lint.py` | §2.2, §3, §4, §8, §9.1, §10, §12 and §13: every rule id of this file, plus the spike's rules. |
| The strips plugin | §6 and §7: the front matter against the outline and `plan/tracks.md`; the headings of the body and the bottom strip; the counts of questions, exercises, Summary items and Test out answers; learn ids covered by `tests`; `:::example` before the strip; checkpoints in tutorials; the share of an internals page's general section; for a page with a command-only step (§10), on tracks G and B `make/automated-playtests` (a step that runs a command script) or `make/commands` (a step that calls a command) in its closure, and on track E `editor/commands` in its closure or, on a page before it, the line to paste with a link forward to `editor/commands`. |
| `tools/names.py` | Every name in backticks, every path and every UI label, against the engine at the pin. |
| `tools/excerpts.py fill` and `check` | Quotes filled from the pin; no quote left in symbol form. |
| `tools/sketches.py`, `tools/tutorials.py` | Sketches compile and their shown output matches; tutorials and exercise solutions have current stamps (pipelines.md says which run in phase A). |

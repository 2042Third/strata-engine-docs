# Walk E-final-3: track E (engine builder, persona E1), segment 3

Entries walked: `basics/bytes`, `basics/data-formats`, `basics/math-matrices`, `basics/math-bases`, `basics/math-projection`, `basics/math-rotations`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`; StrataCLI and StrataEditor run under the perf lock, two holds, each with a private `STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` in the work folder, no editor left running; preferences untouched).
Book: the built site at 127.0.0.1:4329. Engine source read in `docs-pin` at 319075e3 (only to compare the quoted excerpts and the named functions).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-3/` (page texts and HTML, `sk/` the 29 extracted sketches and their programs, `dl/` the Coin Run checkpoint, `proj/` project copies, `run1.ps1`, `run2.ps1` and their outputs).

How the walk went: every page read in full. All 29 sketches (bytes 6, data-formats 8, matrices 5, bases 2, projection 4, rotations 4) extracted from the page, compiled with g++ `-std=c++20 -Wall -Wextra` (glm from the pinned vendor folder) and run: no warnings, every printed output equals the page's, and every "Line N" note points at the right line. Every worked example, "Try it", "Check yourself" and Practice answer was recomputed by hand (a few by a throw-away program): all agree. Engine quotes compared with 319075e3 (AssetPack.h, BinaryStream.h, SaveFiles.cpp, Hash.h, Tetris.stproj, Math.cpp, Scene.cpp, Gameplay.h, IBL.slang, Playground.cpp, ScriptProject.cpp): equal; the functions and constants the pages name (Project::Load messages, JsonUtils::Parse, UUID::FromString, Crypto.h, DecomposeTransform, TransformNormal, PerspectiveReverseZ, the Camera clamps, GetEulerAngles, IsNearlyEqual, the SDK's SetParent, GetForward, Log::Info for glm::quat) exist as described. SHA-256 digests of abc, abd and the empty text checked with sha256sum.
With the editor: `StrataCLI launch --project <Coin Run checkpoint 4> --headless`, `viewport.capture` answered `Image.Data` as Base64 of a PNG (starts `iVBORw0KGgo`), as data-formats says; `project.open` on a copy whose "Version" I set to 4 failed with `unsupported project version 4 (this engine reads up to 3)`, as the page's "Reading a header" says, and the open project stayed open.

Not walked: the optional "Hard" exercises that build a script in Coin Run (bytes, matrices, bases, rotations, projection: they need a script build and a play session; I did not build or play them; their pseudocode I only read). The data-formats Hard exercise (open the .stproj and find header, version, start scene) was done on the Coin Run checkpoint 4. The Linux and macOS tabs. Nothing was walked of the pages' pictures beyond their text (I read the figure captions and labels, not the images).

## WK1
- Entry: `basics/bytes` (the same holds for the five other pages)
- Page: Bytes in files and memory: layouts, byte order and text encodings
- Step: the start of the page ("What you need" and the stage download)
- What happened: the page has no "What you need" section and offers no stage download; it has "Before you start" (three links) and a "Test out" box. None of the six pages of the segment has either. The primers need no project, so I started at the page with nothing; only the optional Coin Run exercises need a project (see WK2, WK4).

## WK2
- Entry: `basics/bytes`
- Page: Bytes in files and memory
- Step: Practice, the last "Hard" exercise (rename one coin to Münze, add a script that logs the name's length)
- What happened: the exercise says "on your Coin Run project" but the page never links to the Coin Run page or its download (the other pages of the segment do, in part: matrices, bases, rotations link `make/project-coin-run`; data-formats names Coin Run without a link). The pseudocode is a bare `void OnCreate() override { ... }` with no class, no includes and no registration line, so a reader has to guess how it becomes a script (bases shows a full class, and its text mentions `ST_SCRIPT_CLASS`, which this fence lacks). I did not build it.

## WK3
- Entry: `basics/data-formats`
- Page: JSON, Base64, hashes and UUIDs
- Step: "A stable hash gives the same number everywhere" (first paragraph) and the rest of the page
- What happened: "Before you start" lists only `basics/bytes`, but the text says "Data structures I taught that a hash is a number...", leans on "Numbers in a computer" (wrapping, shifts and masks) and sends the reader to "Modern C++" for constexpr. I went on with the facts the page restates (a hash maps data to a number; unsigned arithmetic wraps) and checked nothing else; a reader who has not walked data-structures meets "the toy hash of the data structures page, the sum of the letter codes" in the answer to the page's own Try it and in Practice 4 without having seen it.

## WK4
- Entry: `basics/data-formats`
- Page: JSON, Base64, hashes and UUIDs
- Step: Practice, "Hard. Optional, starting from the end of Coin Run: open its project file"
- What happened: the page offers no download or link for "the end of Coin Run". I left the book: on `make/project-coin-run` I found `stage-4.zip` (the largest checkpoint, "Coin Run with its heads-up display, sounds, an identity and a first export" on the previous page), unpacked it into the work folder and opened `ProjectCoinRun/CoinRun.stproj` as text. A reader who arrives from this page alone has no way to know that the checkpoint is there.

## WK5
- Entry: `basics/data-formats`
- Page: JSON, Base64, hashes and UUIDs
- Step: Practice, the Worked solution of the same Hard exercise ("The file looks like the Tetris file above")
- What happened: the Coin Run file has the format header (`"Strata": {"Format": "Project", "Version": 3}`), a 16-digit `StartScene` ("00D86E4989BE1767") and an `Export` and a `Game` member in `Project`, as the page says. It does not match "the two objects at the top level" that the Tetris quote asks the reader to notice: it has three, `Project`, `Settings` (about 150 lines: input actions, collision layers) and `Strata`. Finding the header still works, but the file is much longer than the 22 lines the quote shows, with `Settings` between the other two.

## WK6
- Entry: `basics/math-projection`
- Page: Cameras and projection: perspective, homogeneous coordinates and depth
- Step: "The depth buffer keeps the nearest surface", the definition of Depth
- What happened: the sentence reads "Depth is the number that the projection stores for a point to tell nearer from farther: the z of its NDC, from 0 to" and stops. The next sentence, "The depth buffer is a grid ...", is shown as item "1." of a numbered list (the source of the page has the sentence's last words "1." at a line start, which the markdown turns into a list). The reader has to guess "from 0 to 1" (the NDC paragraph before it says "the depth z from 0 to 1").

## Answers

No patches are listed under "## Built by the integrator", and none of the six pages has a tutorial file, so no
`tutorials.py run` applies. Every changed page passes `tools/pagecheck.py`. The two Coin Run scripts the pages now show
in full were built and played with the official v0.8.0 package, headless, under the perf lock, on a copy of Checkpoint 4
of Ship the finished game (`docs-work/walkfix-E3`, `run1.ps1`, `run1.out`); no editor was left running and the pin clone
is clean. No engine fault was found.

### basics/bytes

- **WK1** fixed (page). Primers have no "What you need" by design (style.md §7.1: Test out, then Why you will need
  this); the sketches need only the compiler of Building C++ programs. What only the optional Coin Run exercise needs is
  now stated in the exercise: your Coin Run, or Checkpoint 4 at the end of Ship the finished game, linked, opened with
  **File ▸ Open Project...**. The same start is named on data-formats, math-matrices, math-bases and math-rotations;
  math-projection's Coin Run item is a program on its own and needs no project.
- **WK2** fixed (page). Practice 6 links Coin Run and Checkpoint 4. In that state the five coins exist only in play
  (`Scripts/CoinPlacer.cpp` instantiates them), so the exercise places one more coin from `Prefabs/Coin.stprefab` and
  renames that one. The pseudocode is now the whole file `NameLength.cpp` (include, `using namespace Strata`, class,
  `ST_SCRIPT_CLASS`), with the steps: **Scripts ▸ New Script...**, replace the text, **Ctrl+B**, **Add Script...** in
  the coin's Script component (which already holds `Coin`), Play, Console. Built and played with the package: the
  Console shows `name bytes 6, code points 5`.

### basics/data-formats

- **WK3** fixed (page). Data structures I and Numbers are in the page's Needs closure through Bytes, but Before you
  start lists only Bytes, so the hash section now restates what the page uses: the toy hash of Data structures I adds
  the letter codes (`ant` = 97 + 110 + 116 = 323), which the Try it and Practice 4 then use, and a wrapping product
  keeps only its lowest 64 bits. The `constexpr` question already gives the reading the page needs.
- **WK4** fixed (page). Practice 6 links Coin Run and Checkpoint 4 at the end of Ship the finished game, whose zip holds
  the folder with `CoinRun.stproj`.
- **WK5** fixed (page). Checkpoint 4's `CoinRun.stproj` is 169 lines with three top-level objects, `Project`, `Settings`
  (`Input.Actions`, `Scene.CollisionLayers`) and `Strata`; `Project::Save` writes `Settings` only when the project has
  settings (`Strata/src/Strata/Project/Project.cpp:414-415`), and Tetris has none. The paragraph after the Tetris
  quote now says that a project with settings of its own has a third object, `"Settings"`, between the other two; the
  worked solution says what Coin Run's file holds there, that it is about 170 lines long and that the header is at its
  end.

### basics/math-matrices

- **WK1** fixed (page), as on bytes: Practice 5 names its start and links Checkpoint 4. Its "attach a script to a coin"
  could not be done there (no coin outside play), so it places one more coin from the prefab, and the pseudocode is the
  whole file `RingChild.cpp`. Built and played with the package: the Console shows
  `coin world position (1.78814e-07, 1, -3)`, the page's "about (0, 1, -3)"; the callouts now quote it.

### basics/math-bases

- **WK1** fixed (page): Practice 5 names its start, your Coin Run or Checkpoint 4 of Ship the finished game, linked
  (a few words of the answer were cut to keep the page within size M).

### basics/math-rotations

- **WK1** fixed (page): Practice 7 names its start, your Coin Run or Checkpoint 4 of Ship the finished game, linked.

### basics/math-projection

- **WK6** fixed (page). The source broke the definition's line before "1.", which markdown reads as a numbered list.
  The line now breaks before "to 1.", and the depth buffer's definition stands in its own paragraph, as lint's
  `term-paragraph` asks once the two terms share one. A scan of the six pages finds no other line that starts with a
  number inside a paragraph.
- **WK1**: Practice 6 needs no project (a program on its own), so the page names no checkpoint.

## Confirm

Segment 3 confirmed after the fixes, as a reader of the book as it is now. Setup note: the server on port 4329 still
served a build from before the fixes (its pages had no "Checkpoint 4"), so I merged `book/write` into the preview
worktree, rebuilt `dist` (396 pages) and read the new build on port 4330 (`docs-work/walk-E-final-3/new/`). The server
on 4329 was left as it was and needs a restart to show the fixes. Checkpoint 4 (`stage-4.zip`, linked from each page) was
unpacked into `docs-work/walk-E-final-3/proj/s4new`; the two scripts were copied from the pages' text; one editor session
under the perf lock (`run.ps1`, `run.out`), no editor left running, preferences untouched.

- **WK1 (bytes, Practice 6): confirmed.** The exercise names Coin Run or Checkpoint 4 (link to Ship the finished game,
  whose section has the `stage-4.zip` link), File > Open Project, says the five coins exist only in play and tells the
  reader to drag one more `Prefabs/Coin.stprefab`. The page now holds the whole `NameLength.cpp` with the steps (Scripts >
  New Script..., Ctrl+B, Add Script... in the coin's Script component, Play). Done through the commands
  (`asset.place`, `entity.rename` to M\u00fcnze, `script.create`, `script.build`, `script.add`, `play.start`): the Console
  shows `name bytes 6, code points 5`. No guessing.
- **WK2 (data-formats, hash): confirmed.** The section restates the toy hash (`ant` = 97 + 110 + 116 = 323); Try it and
  Practice 4 (`ant` and `tan` both 323) now read without the other page.
- **WK3 (data-formats, Practice 6): confirmed.** The exercise links Coin Run and Checkpoint 4. `CoinRun.stproj` of the
  checkpoint has 169 lines and three top-level objects, `Project` (line 2, with `StartScene` "00D86E4989BE1767"),
  `Settings` (line 25) and `Strata` (line 165, `"Format": "Project"`, `"Version": 3`), as the worked solution says
  ("about 170 lines", "Settings between", "header at its end"). No mismatch.
- **WK4 (math-matrices, Practice 5): confirmed.** Ring at (0,1,0) turned 90 about Y with Spinner 0 (`DegreesPerSecond`),
  one more coin placed, `RingChild.cpp` from the page built and attached: the Console shows
  `coin world position (1.78814e-07, 1, -3)`, equal to the page's callout. (I placed two extra coins for the two
  scripts, so my `Coins placed` line says 7, not the page's 6; one coin per exercise gives 6.)
- **WK5 (math-bases Practice 5, math-rotations Practice 7): confirmed.** Both openings name "your Coin Run or Checkpoint
  4" with a working link to `make/project-coin-run/#ship-the-finished-game` (the anchor exists; the zip answers 200).
  Walked only as far as the opening, as asked.
- **WK6 (math-projection): confirmed.** The Depth sentence ends "the z of its NDC, from 0 to 1." in one paragraph; the
  depth buffer definition follows as its own paragraph, with no numbered list in the built HTML.

No new faults found in these steps.

# Walk of track G, segment 3: make/materials, make/prefabs, make/lighting, basics/tools, make/first-script

Persona G0 (plan/style.md 1.1). Package: official Strata 0.8.0 Windows x64 (docs-package-0.8.0), StrataCLI against a
headless editor started with `StrataCLI launch --headless` under the perf lock (one hold). Book at 127.0.0.1:4329.
Work folder: docs-work/walk-G-final-3 (project CoinRun). No page was changed. Editor preferences were not changed.

What was walked: every command tab of the five pages in order. The "In the editor" tabs and most pictures cannot be seen
from a CLI; viewport.capture pictures were read for the Albedo view and the played level only. Not walked: the
mouse-and-menu tabs, the drop ghost and badge, the Luminance and Lighting picture checks, the code-editor exercises
of basics/tools, STRATA_EXTERNAL_EDITOR (needs an editor start per variable), and the Check-yourself and Exercise
answers, except the Basic exercise of make/materials (Copper and Asphalt were created).

## WK1 make/materials, What you need (left the book)
The section lists what the reader needs but offers no stage download for a reader who arrives here. The Assets page
offers no checkpoint either (only an exercise solution). I guessed the URL
downloads/tutorials/make/assets/stage-1.zip from the pattern of the other pages, and it exists (18 KB).

## WK2 make/materials, What you need and "Make the material" (did not match)
The guessed stage unpacks to a top-level folder named `Assets` that holds `CoinRun.stproj` (the project folder carries
the name of its asset folder). It already has a `Materials` folder (with Ground.stmat) and a Spinner.cpp script, so the
step "New, Folder, type Materials" would meet an existing folder. The Coin root and its child `coin-gold` match the page.

## WK3 make/materials, Make a gold coin and later "<the ID of ...>" (guessed)
Several commands carry `<the ID of coin-gold>`, `<the ID of Ball>`, `<the ID of Scratch>`, `<the ID of Wall>`. The page
never says how a CLI reader finds an ID. I guessed `scene.hierarchy` (known from make/with-an-agent) and read the IDs
from it. entity.create answers `{"id": ...}`, which the page does not say either.

## WK4 make/materials, Audit the colors (did not match)
After `viewport.setSettings {"debugView":"albedo"}` and a capture, the Chalk wall is striped red as the page says, but
the four level walls (the Walls group, from an earlier page) are striped too, and they stay striped after Chalk is
lowered to 0.8 (the slab then shows light grey). The "You should see" says only the wall is striped and the coin, ball
and ground are plain. The "If you do not see it" line covers remaining stripes, but the main text does not predict
them. The legend ("Above 0.85" and a share) is not in the capture, and no command I found returns it
(viewport.getSettings has only debugView), so "the share at 0 %" could not be checked.

## WK5 make/materials, Add a glow / alpha modes / glass (left the book)
These "You should see" lines (coin glows faintly, cube vanishes in Mask, see-through in Blend, clear glass cube) are
visual. I ran all material.set and entity commands (all answered without a warning) but did not look at a picture of
them, and no command answers what is drawn. Not checked. The texture steps matched: Usage Color, Data, NormalMap; the
break gave the warning "Metal032_NormalGL is imported as Color: its normals will be wrong" with a fix command, and the
fix cleared it.

## WK6 make/prefabs, Make the prefab / Give one coin its own look (guessed)
The "You should see" lines are about the badge, the prefab bar and the chip "Overrides (n)". The command tabs name no
command that shows them. I found `prefab.status` in `StrataCLI list` and used its `overrides` array: empty after
prefab.create, MeshRenderer.Material after the silver step, still one override after the root move and rename, Transform
Scale for Coin (2), and empty again after apply and revert. Every result agreed with the page. Without that guess a CLI
reader cannot check these lines. Placement (placedOn surface, snapped true, Coin (1) to Coin (4) names), apply
(updatedInstances 4, silver kept, children scale 1.5), revert, unpack (linked false) and undo (linked true) matched.

## WK7 make/lighting, Read the light that Basic 3D gave you (failed)
`component.get` with `"entity": "Sun"` (and "Post Process", "Sky") is rejected: code -32602, "Parameter 'entity' must be
an ID (16 hexadecimal digits)". The same holds for every component.set of the page that names the entity by its name.
I took the IDs from scene.hierarchy. The values then matched the page (Intensity 120000, ShadowSoftness 0.53 under
that name, AutoExposure true, Exposure 0.25, MinEV -4, MaxEV 16, Source Atmosphere).

## WK8 make/lighting, Change the sun and break the exposure (matched)
Mean brightness of the Scene capture: base 132; sun 60000 lux 132 (same look); Auto Exposure off with Exposure 0: 250
(nearly white); -15: 111 (close to auto); sun 120 lux: 132; MinEV 8: 11 (dark); MaxEV 8: 223 (pale); restored 132. All
agree with the page.

## WK9 make/lighting, The four presets (did not match / guessed)
(a) The button is "Golden Hour" but the command takes `GoldenHour`: `"preset": "Golden Hour"` is rejected (enum Clear,
Hazy, Overcast, GoldenHour). The page's command example shows only Overcast, so the reader must guess the spelling.
(b) The page says to read the ratio "Sun : sky" in the Lighting debug view's legend. No command returns it, and the
preset's answer holds only groundIlluminance (Clear 97912, Hazy 88882, GoldenHour 40905, Overcast 1500). So the
ratios of the table (6 to 10, 3 to 5, 1 to 2, below 0.3) could not be checked from the command tab. The text for
Overcast says the sun gives about 1,300 lux on the ground; the command answers 1500.
(c) `lighting.extractSun` answered intensity 4.43, illuminance 4.40 lux and angularDiameter 3.27 for the HDR; the page
does not say how small this is. The later steps do not depend on it.

## WK10 make/lighting, Light Coin Run for play (did not match)
After the Clear preset at 35 degrees, play.start (paused), play.step 60 and a capture show the coins with shadows and
the walls, but no blue sky: the camera looks down at the ground and the beige ground fills the picture. The page says
"the coins casting shadows about one and a half times their height, on a blue sky".

## WK11 make/lighting, Tell preview lighting from real light (not seen)
scene.save, scene.new Dark, entity.create Cube and Camera, previewLighting false and true, a DirectionalLight and
scene.open with force all ran without error. What the two views show was not seen.

## WK12 basics/tools, Read what a wrong option does (did not match)
In Windows PowerShell 5.1, `.\StrataEditor.exe --bogus > out.txt | Write-Output` shows the message wrapped in
PowerShell's own error text (".\StrataEditor.exe : Unknown argument '--bogus'", "At ...:19 char:1", "CategoryInfo ...
NativeCommandError", then the usage). With `2> out2.txt` the file holds the same wrapped lines, not only the editor's
message. out.txt was 0 bytes and the code 3, as the page says. The page says the screen shows the message and the file
receives it, with no mention of the extra lines.

## WK13 basics/tools, Exit codes (did not match, weak)
`.\StrataEditor.exe --version` without a pipe printed nothing and $LASTEXITCODE was 0 (not an old number, as the page
warns). With the pipe: "Strata Editor 0.8.0", code 0. `--frames` without a value gave the page's message and code 3;
`--help > help.txt` gave 0 and a 3136 byte file. The log exists at %LOCALAPPDATA%\Strata\Logs\StrataEditor.log.

## WK14 basics/tools, Scripts and joined commands (left the book)
The page ends the section with `py Tools\PerfStability.py --help` and says the release has no Tools folder. The line
cannot run for this reader (no `py` on this machine, no Tools folder). Not run.

## WK15 basics/tools, A code editor reads a whole folder, Practice Hard (left the book)
Needs a code editor with a screen (Ctrl+Shift+F, its terminal). Not walked.

## WK16 make/first-script, Create the script: Choose your code editor (left the book)
The step sets the external editor with preferences.set. I did not change preferences (rule of this walk). The
consequence: `script.create {"class":"Coin","open":true}` answered `"openedWith": "the default application"`, not a
code editor. The page's "You should see: Scripts/Coin.cpp opens in your code editor" is therefore unchecked, and its
"If you do not see it" does not say that without a setting the file opens in the default application.

## WK17 make/first-script, Log a line and read a build error (did not match)
Fix step: "If you do not see it: the editor refused to open the file when your setting names no program". With no
setting, `script.open {"file":"Scripts/Coin.cpp","line":12}` did not refuse: it answered `openedWith: the default
application`. (The build error itself matched: `Coin.cpp(13,2): error C2143: syntax error: missing ';' before '}'`,
errorCount 1; the mistake is on line 12 and the compiler reports 13, as the page says it may.)

## WK18 make/first-script, Make the coins spin: attach (guessed)
The command tab has only script.add. "Apply to Prefab" of the Script component has no command in the tab; I guessed
`prefab.apply` on the Coin root, which gave updatedInstances 4, after which script.get showed Coin with 90 on the four
other coins. "Select a coin" does not say root or child; I took the root, which worked. script.add answered
`fields: {}`, while script.get shows DegreesPerSecond 90 (the page says the component shows 90).

## WK19 make/first-script, text of the page (did not match)
(a) "Line 10: OnCreate returns, as the template had it, because your 21-line file omitted it; its body now holds one
line" reads wrongly: the 21-line file has no OnCreate, and the page does not say to add the whole function.
(b) The hot-reload section says "In step 3 you put the two lines below at the top of OnUpdate"; there is no step 3, and
the lines are not put anywhere before this point, so the sentence has no antecedent.

## WK20 make/first-script, Crash it on purpose (did not match, once)
My first crash attempt wrote the two lines and called script.build at once after the previous build: it answered
success with no compile of Coin.cpp (the log has no "Coin.cpp"), and play then started with no fault. After one
second's wait the same edit compiled, reloaded and crashed as the page says: "Coin::OnUpdate on 'Coin': Access
violation writing address 0x0000000000000000", Coin.cpp line 18 (the page's picture says line 18), play stopped, state
Edit. A reader types more slowly, so this is recorded only as observed.

## WK21 make/first-script, Change the code while playing (matched)
During play the axis change and build answered reloaded true; the rotations changed to the other axis, the 180 coin
stayed at 180, and the log after the build holds no new "Coin starts with" lines. Five "Coin starts with" lines (90 four
times, 180 once) appeared at play start, as the page says.

## Answers

No patches are listed under "## Built by the integrator". No tutorial file changed, so no run was needed; every
changed page passes `tools/pagecheck.py`. Commits: make/materials 64d3620f, make/prefabs bb5a2c48, make/lighting
a398d363, basics/tools 9d6d3122, make/first-script 9ec558a9.

- **WK1** fixed (page). What you need now offers Assets' end state: the box at the end of its Result.
- **WK2** fixed (page). The zip's top folder carries the page's name (`tools/tutorials.py` `project_files`), which
  What you need now says, with `CoinRun.stproj` inside. Basic 3D makes `Materials` with `Ground.stmat`
  (`StrataEditor/src/Editor/ProjectTemplates.h:49`), so for every reader step 1 now opens that folder instead of
  making it.
- **WK3** fixed (page). The first `<the ID of …>` says to take the ID from `entity.find`, as `make/scenes-entities`
  taught; the Scratch and Wall steps say that `entity.create` answers `id`, and that `entity.find` with `Wall` also
  finds the first wall under `Walls`.
- **WK4** fixed (page, figure caption). The level's walls use the engine's default material, white
  (`Strata/src/Strata/Renderer/Material.h:26`), so the Albedo view stripes them; the steps predict it, say they stay
  striped after the fix and that the share falls but not to 0 %, and the tab says the legend is drawn only in the
  window.
- **WK5** rejected. The reader who uses the command tabs drives the editor's window and sees the Scene view; the walker
  ran a headless editor. The textures' part matched.
- **WK6** fixed (page). The tabs run `prefab.status` wherever a result is the badge or the chip (the tutorial file
  already did) and say what `linked` and `overrides` read; the steps that had no tab got the file's commands.
- **WK7** fixed (page). The tabs showed the tutorial file's `entityName`, which no engine program reads; they now pass
  `"entity": "<the ID of Sun>"` (Post Process, Sky) and say to take the ID from `entity.find`. Other pages show
  `entityName` to readers too (animation, characters-cameras, gi, lamps, levels-saves, look, physics, reflections,
  sound): for their fixers.
- **WK8** rejected: no fault. Every value matched the page; logged for coverage.
- **WK9** fixed (page). (a) The tab lists the four presets as the file runs them and spells `GoldenHour`. (b) It gives
  each preset's `groundIlluminance` (lux on a surface facing the sun) and says no command answers the sky's light, so
  the ratio is read in the window's legend; the Overcast text says its 1,300 lux are 1,500 times 0.87 on flat ground.
  (c) Extract Sun's result says this map's sun measures about 4.4 lux and why. Exercise 2's answer claimed a ratio
  check its solution does not make; it now names the `sunDirection` check.
- **WK10** fixed (page). Basic 3D's camera looks 55 degrees down with a 60 degree field of view, so the Game view
  shows no sky; step 1 puts the blue sky in the Scene view, and step 2 says the Game view shows ground, coins and
  walls only.
- **WK11** rejected. Visual results of the editor's views; the reader sees them in the window.
- **WK12** fixed (page). Checked with the package in Windows PowerShell 5.1: `2>` writes PowerShell's error record
  (`At …`, `CategoryInfo`, `NativeCommandError`) into the file, code 3. The example says so, and that a PowerShell run
  inside another program shows them with `>` alone.
- **WK13** fixed (page). Checked: after a code 3, a bare `--version` left `$LASTEXITCODE` at 3; the walker's old
  number was 0. The page now says the old number is often 0 and looks right.
- **WK14** fixed (page). The PerfStability line is marked as one to read for later: the release has no `Tools` folder
  and installs no Python.
- **WK15** rejected. Needs a screen and a code editor, which the reader has; the walker had neither.
- **WK16** fixed (page). Without a setting, `script.create {open: true}` opens the system's default application
  (`StrataEditor/src/Editor/ExternalEditor.cpp:383-393`); the step's fix line says so and points to step 1.
- **WK17** fixed (page). `script.open` never refuses for want of a setting; the fix line now says the file opens in
  the default application, as `openedWith` reads.
- **WK18** fixed (page). The attach tab adds `prefab.apply` on the root, as the file runs it; it says where
  `<coin id>` comes from, that `script.add` lists only given fields and what `updatedInstances` counts. The editor tab
  says to select the root.
- **WK19** fixed (page). (a) The log section has the reader type `OnCreate` back whole, lines 10 to 13. (b) "In step
  3 you put" became "Step 3 below puts".
- **WK20** fixed (page). The script build decides by file times, which FAT and exFAT keep in 2-second steps
  (`tools/tutorials.py` `c_TimeStepSeconds`); the crash step's "If you do not see it" names a build that missed an
  edit and the fix: save again, build, play.
- **WK21** rejected: no fault. Every result matched the page; logged for coverage.

For a fresh walker: start from Assets' end state (stage-1.zip of make/assets) and repeat make/materials What you
need and every command tab of its sections Make a gold coin and Audit the colors (IDs from `entity.find`); make/prefabs
every tab with `prefab.status`; make/lighting from stage 1 (IDs from `entity.find`), the presets' tab and Light Coin
Run for play with a capture of the Game view; basics/tools' wrong-option example and Exit codes in Windows PowerShell
5.1; make/first-script from stage 1 without preferences (`openedWith`), the attach step with `prefab.apply`, Log a
line (type lines 10 to 13), and Crash it on purpose with an edit saved at once after a build.

## Confirm

Persona G0 (plan/style.md 1.1). Package: official Strata 0.8.0 Windows x64 (docs-package-0.8.0); StrataCLI against a
headless editor started with `StrataCLI launch --headless`, one perf-lock hold, one editor per project (each started from
the stage zip the page offers). Work folder docs-work/walk-G-final-3/confirm. Editor preferences were not changed. Run in
Windows PowerShell 5.1 (basics/tools). The `script.create` and `script.open` calls opened the system's default program for
`.cpp` (Visual Studio); I closed what that started. No editor of mine is left running.

**The served book was older than the fixes.** The book at 127.0.0.1:4329 was built at 12:22 from `site/preview` 0263fac0
(12:19); the fixes are commits from 13:10 on. None of their text is in the served pages (make/materials What you need has
no download, make/prefabs has no `prefab.status`, make/lighting no `GoldenHour`, make/first-script no `openedWith`,
basics/tools no `NativeCommandError`). So I read the five pages' Markdown at `book/write` HEAD (the book as it is now),
and checked in the built Assets page that its Result ends with the box ("Download the project as it is at the end",
`stage-1.zip`, 18 KB) that the new What you need points to. The preview needs a rebuild (`scripts/preview.ps1`) before a
reader of that URL sees the fixes.

### WK1 make/materials, What you need: fixed
A reader who arrives here follows the link to Assets' Result and finds the box with the project (`stage-1.zip`). The zip
unpacks to `Assets/` with `CoinRun.stproj` inside, as the sentence says. The editor opened it; `Coin` and `coin-gold`
are as the page says. No guessing; the one link out is the one the page gives.

### WK2 make/materials, step 1: fixed
`Materials` (with `Ground.stmat`) exists in the zip's project; `material.create {"path":"Materials/Gold.stmat"}` ran in it
without a clash. The step now says to open the folder, not make it. Matches.

### WK3 make/materials, IDs: fixed
`entity.find {"name":"coin-gold"}` answers `{"entities": ["<id>"]}`; the same for `Ball`. `entity.create` answers `{"id"}`
as the Scratch and Wall steps say. `entity.find` with `Wall` answered two IDs: the first is the wall under `Walls`, the
second the new one, as the added sentence warns. I deleted the new one by the `id` from `entity.create`; the other
survived. Gets through without guessing.

### WK4 make/materials, Audit the colors: fixed (one inaccurate remark left)
Albedo view, capture read as a picture: the slab (Chalk) and the four walls are striped; coin, ball and ground plain. After
Chalk 0.8 the slab is light grey and the four walls stay striped, as the new text says. The share did not go to 0: the
capture's `debugView.lighting.aboveRangeShare` fell from 0.245 to 0.2305 (the new text says "smaller"). Mismatch left:
the command tab says no command answers the legend. The answer of `viewport.capture` does carry the legend's numbers
(`debugView.lighting.aboveRangeShare`, `belowRangeShare`, `sunToSkyRatio`, `sunIlluminance`, `skyIlluminance`). The page
is right that the picture lacks the legend; it may point a command reader at the answer's `aboveRangeShare` instead.

### WK6 make/prefabs: fixed
Every tab walked from materials stage 5 with IDs from `entity.find` (children from `entity.get` `children`). `prefab.status`:
after `prefab.create` linked true, `overrides` empty; `Coin (1)` child after silver: one override (`MeshRenderer`
`Material`); after move, rename to `Silver Coin` and back: still one override, both answers; `Coin (2)` child scale 1.5:
one override (`Transform` `Scale`); after `prefab.apply` (`updatedInstances` 4): `Coin (2)` none, `Coin (1)` still the
`Material`; after `prefab.revert`: none; `edit.undo` brings `Material` back; `prefab.unpack` on `Coin (4)`: linked false;
`edit.undo`: linked true; `scene.save` answered. Every line agrees with the You-should-see lines. Gets through.

### WK7 make/lighting, Read the light: fixed
IDs of `Sun`, `Post Process` and `Sky` from `entity.find`; `component.get` and `component.set` accepted them. Values:
Intensity 120000, ShadowSoftness 0.53 (shown under Angular Diameter in the editor), CastShadows true, AutoExposure true,
Exposure 0.25, MinEV -4, MaxEV 16, Source Atmosphere. Matches. The Change the sun and Choose the sky commands ran as
written (sun 60000, 120 and 120000, auto exposure off, Procedural, the HDR import, `Source` EnvironmentMap).

### WK9 make/lighting, presets and Extract Sun: fixed (one claim wrong)
`GoldenHour` is accepted and `"Golden Hour"` is rejected, as the tab says. `groundIlluminance`: Clear 97912, Hazy 88882,
GoldenHour 40904, Overcast 1500, as the page says. `lighting.extractSun`: illuminance 4.40 lux, intensity 4.43, as the
page says (about 4.4 lux). Overcast's `sunDirection` y is 0.866, so 1,500 times 0.87 is 1,305, as the text says. Wrong
claim left: "No command answers the sky's light: read the ratio in the Scene view's legend." With `debugView` "lighting", the
answer of `viewport.capture` has `debugView.lighting.sunToSkyRatio`: Clear 8.09, Hazy 5.26, GoldenHour 1.24, Overcast
0.159. Clear, Golden Hour and Overcast fit the table; Hazy 5.26 is just above "3 to 5". The reader still gets through.

### WK10 make/lighting, Light Coin Run for play: fixed
Clear at 35 degrees, `scene.save`, `play.start` paused, `play.step` 60, `viewport.capture {"camera":"scene"}`, `play.stop`:
the capture shows the ground filling the picture, the coins with shadows and the walls, no sky; the new text says exactly
that. The Scene view's blue sky was not checked (the editor camera of my capture looks down at the ground too; the text
says "wherever the view shows the horizon").

### WK12 basics/tools, wrong option: partly fixed
With `| Write-Output` (as the Exit codes text teaches), `--bogus > out.txt` leaves out.txt empty and the screen holds
PowerShell's error record (`.\StrataEditor.exe : Unknown argument '--bogus'`, `At ...`, `CategoryInfo`,
`NativeCommandError`) and the usage; `2>` puts the same wrapped lines in the file; code 3. This is what the new text says.
Mismatch left: the example says only "add `> out.txt`". Without the pipe, as written, in my PowerShell 5.1 the screen shows
nothing, out.txt and the `2>` file stay 0 bytes, and `$LASTEXITCODE` stays at the number before (7 in the test), not 3.
"Either way the exit code is 3" and "the screen shows the message" hold only piped. The page should say to pipe in
PowerShell, as the paragraph above it does. Caveat: my PowerShell was a window-less host, not a console.

### WK13 basics/tools, Exit codes: fixed
After `.\StrataEditor.exe --frames` (code 3), a bare `.\StrataEditor.exe --version` printed nothing and `$LASTEXITCODE`
stayed 3; piped: "Strata Editor 0.8.0", code 0. The text now says the old number is often 0 and looks right: it reads
as "a stale number", which is what I saw (3). No guess needed.

### WK14 basics/tools, PerfStability: fixed
The paragraph says the release has no `Tools` folder and Strata installs no Python, so the line is for later; I did not
run it, and nothing in the paragraph asks me to. No mismatch.

### WK16 make/first-script, script.create open:true: fixed
Without a preference, `script.create {"class":"Coin","open":true}` answered `"openedWith": "the default application"`;
Visual Studio opened on `Coin.cpp`. The step's fix line says exactly this and sends to step 1. The template had the four
comment lines, `Speed`, `OnCreate` and `OnUpdate`, as the page says.

### WK17 make/first-script, script.open: fixed
`script.open {"file":"Scripts/Coin.cpp","line":12}` answered `openedWith: the default application`, as the fix line now
says. The build error: `Coin.cpp(13,2): error C2143 ... missing ';' before '}'`, one error; `script.build` with
`wait:false` then `script.status` listed it under `build.last.diagnostics`; adding the `;` and building cleared it.

### WK18 make/first-script, attach: fixed
`entity.find Coin` gave the root; `script.add` answered `fields: {}` as the text says; `script.get` showed
`DegreesPerSecond` 90; `prefab.apply` on the root answered `updatedInstances` 4; the four other coins showed 90;
`script.setField` 180 on the root left the others at 90. Matches.

### WK19 make/first-script, Log a line: fixed
Typing lines 10 to 13 (the whole `OnCreate`) below the field gives the 26-line `CoinLog.cpp`; lines 10 to 13 are
`void OnCreate() override`, `{`, the `Log::Info` line, `}`, and the `Log::Info` line is 12, so `script.open` line 12 and the
compiler's 13 fit the page. Play logged `Coin starts with 180` once and `90` four times. "Step 3 below puts" reads right.

### WK20 make/first-script, Crash it on purpose: fixed
On this drive (exFAT) an edit written right after a build was missed: `script.build` answered success with no `Coin.cpp`
in its log and `reloaded: false`, and `play.start` ran with no fault, as the new "If you do not see it" describes. The
fix, saving the file again, `script.build` (log names `Coin.cpp`, `reloaded: true`), `play.start`, crashed at once:
`lastFault` "Access violation writing address 0x0000000000000000" in `Coin::OnUpdate`, `Coin.cpp` line 18, play state
Edit. Removing the two lines and building was clean. A reader who follows the line gets through. (Hot reload, the step
before: the tumble edit compiled and `reloaded` was true, with no new "Coin starts with" lines.)

### Summary
Through without guessing, leaving the book or a mismatch: WK1, WK2, WK3, WK6, WK7, WK10, WK13, WK14, WK16, WK17, WK18,
WK19, WK20. Fixed with one inaccurate remark left: WK4 and WK9 (both say no command answers the legend, while
`viewport.capture` answers it under `debugView.lighting`; Hazy's measured 5.26 is above the table's 3 to 5). Still a
mismatch: WK12 (the example needs the pipe in PowerShell). Not a fix: the served preview predates all of them.

## Answers (after confirm)

Measured in Windows PowerShell 5.1 in a console of its own (the pin's `StrataTests --strata-test-helper=console-output`,
as segment E:5's answers did), with the 0.8.0 package, `$LASTEXITCODE` set to 7 before each line; scripts and results in
`docs-work/walk-final-fix/console`.

### WK12 basics/tools, Read what a wrong option does
- The confirmer is right, and in a real console too: `--bogus > out.txt` and `--bogus 2> out.txt` alone return at once,
  leave the file empty and `$LASTEXITCODE` at 7; `--help > help.txt` alone does the same (0 bytes, 7). Piped with
  `| Write-Output`: `--bogus 2> out.txt` gives 3 and a file of 3,908 bytes that starts with the error record
  (`.\StrataEditor.exe : Unknown argument '--bogus'`, `At line:1 char:...`, `CategoryInfo`, `NativeCommandError`), then
  the usage; `--bogus > out.txt` gives 3, an empty file and no message on the screen (the windowed editor gets no
  standard error from PowerShell); `--help > help.txt` gives 0 and 3,136 bytes.
- Change: the example keeps the bash text, then says that PowerShell 5.1 needs `| Write-Output` (as the Exit codes text
  above it teaches) and shows `.\StrataEditor.exe --bogus 2> out.txt | Write-Output` with `$LASTEXITCODE` (3), and two
  points: the error record in the `2>` file, and the empty screen with `>`. The answer of the question after it says the
  `--help > help.txt` line needs the pipe in PowerShell 5.1 too. The unmeasured remark on a PowerShell inside another
  program was removed. pagecheck PASS; the page has no tutorial file.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK12 basics/tools, Read what a wrong option does
- Holds. In Windows PowerShell 5.1 in a console of its own, with the package: `.\StrataEditor.exe --bogus 2> out.txt | Write-Output` then `$LASTEXITCODE` gave 3; the file held 3,890 bytes and began `.\StrataEditor.exe : Unknown argument '--bogus'`, then `At line:1 char:1`, `CategoryInfo`, `NativeCommandError`, as the page says. `--bogus > out.txt | Write-Output` gave 3, a file of 0 bytes and no message. `--help > help.txt | Write-Output` gave 0 and 3,136 bytes (about 3 KB). Unpiped, `--bogus > out.txt` left `$LASTEXITCODE` at the stale 7, as the page warns. The page's words (pipe needed, two differences, the answer's pipe remark) match.

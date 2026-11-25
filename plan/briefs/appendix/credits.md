# Brief: `appendix/credits`

| Field | Value |
| --- | --- |
| Title | Credits and licenses |
| Kind | R |
| Size | S |
| Tracks | - |
| Needs | - |
| From | the book's copyright statement, "All rights reserved" with its two exceptions (holder and year from `site.json`); the permission for the book's code, in the reader's words, taught here; of the engine's own terms only what its repository says at the pin; the credits: sample assets shown in figures (`CREDITS.md`), with the full entry of the Open World sample's fox (its CC BY 4.0 parts, with their two copyright lines and the link to the Khronos commit), the vendored libraries a page quotes with their licenses and a link to `third-party-notices.txt`, quoted sources; no license text of its own |
| Unit | `plan/allocation/appendix.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `appendix/credits` — Credits and licenses

**Covers.** One paragraph on how to read it: what the book shows or quotes that others made, where it comes from and
under which license. Then the tables. The libraries of `ThirdPartyNotices.md`, with version, license and whether games
ship them; a page may quote a library's source (`vendor:<lib>`) only when the library is listed there and named here
with its license (`pipelines.md` §3.2). The fonts the pictures show: the editor's Inter and JetBrains Mono (SIL Open
Font License 1.1) and Lucide's icons (ISC, the icons derived from Feather also MIT), and Roboto Medium (Apache 2.0), the
default font of text in every game. Code that Strata derived from other projects (radiance-cascades-lab, MIT, in the
shaders of global illumination), whose notice travels with any excerpt of those files. The sample assets that figures
show, by sample and pack, from each sample's `CREDITS.md`: almost all are CC0; the Open World's fox carries CC BY 4.0
parts (rigging, animation and glTF conversion), so every figure that shows the fox gives its attribution in its caption
or beside it, and this page lists those figures and holds the fox's full entry, with the two copyright lines that the
engine's own credit leaves out (an erratum of the engine) and the link to the Khronos commit. The book's own assets:
the files of `tutorials/assets/` (with their `CREDITS.md`) and the textures of the labs, each CC0 or CC-BY. And the
engine itself: every excerpt and every picture of the book comes from the owner's engine at the pin, and of the
engine's own terms the page says only what its repository says there. Last, the book's own terms: the statement
"Copyright © 2026 2042Third. All rights reserved.", with "Except where otherwise noted" and its two exceptions, and the
first exception, the permission for the book's code, in the reader's words (a reader may put the book's code and
project files into their own games and ship them, also commercially, but may not publish them as a collection, a
course or a book). The page holds no license text of its own: it links the site's `license.txt` and
`third-party-notices.txt`.

**Leaves out.**

- How Strata pins, wraps and upgrades its libraries, and the rule for code from other projects → `engineering/third-party`
- Choosing assets with licenses a game may use → `make/assets`
- A game's own credits screen and notices file → `make/export`, `worlds/export`
- The books and articles the book's ideas come from → `appendix/further-reading`

**Fit.** `fits`: about 780 words against S (1,500). That is the prose: the paragraph on how to read the page with the
tables' introductions (600), the book's statement with the permission for its code (120) and the fox's full entry (60);
the page's size comes from its tables, written by hand from `ThirdPartyNotices.md` and the samples' `CREDITS.md` (R36):
twenty libraries, four fonts, one derived project, about nine sample packs and the figures that need an attribution.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:142` | feature | home | The libraries: name, version, license and whether games ship them; the list a `vendor:` quote must be in. Evidence: `ThirdPartyNotices.md:8-29` |
| `new:143` | feature | home | The fonts in the pictures: Inter and JetBrains Mono (OFL 1.1) and Lucide (ISC; Feather's icons MIT) in the editor; Roboto Medium (Apache 2.0) in every game. Evidence: `ThirdPartyNotices.md:31-43`; `StrataEditor/Resources/Fonts/` holds `Inter-OFL.txt`, `JetBrainsMono-OFL.txt` and `Lucide-LICENSE.txt` |
| `new:144` | feature | home | Code derived from other projects: radiance-cascades-lab (MIT) in the shaders of global illumination, its notice with any excerpt of them. Evidence: `ThirdPartyNotices.md:45-79` |
| `new:145` | feature | home | The sample assets in figures, by sample and pack, and the attribution the fox's CC BY 4.0 parts require beside every figure that shows it; the fox's full entry is `new:185`, not the engine's shorter credit. Evidence: `ThirdPartyNotices.md:81-96`; `Samples/OpenWorld/CREDITS.md:3-5, 11` |
| `new:185` | erratum | home | The fox's full credit, which the engine's credit leaves out: the model's notes at Khronos commit `edc7c9e67c639d230715049ee31f9a96a6babbbe` (`Models/Fox`) hold "© 2014, tomkranis." (rigging and animation, CC BY 4.0) and "© 2017, @AsoboStudio and @scurest." (conversion to glTF, CC BY 4.0) beside PixelMannen's model (CC0 1.0). The page copies the entry with the link to that commit, and every caption of a fox names its authors and license (process.md's table of errata, kind `engine`; `critique/rulings-6.md`, R22), about 60 words. Evidence: `Samples/OpenWorld/CREDITS.md:11` and `ThirdPartyNotices.md:92` name the authors and licenses but no copyright line; `git grep -n tomkranis 822a7a46` finds only those two lines, `Samples/OpenWorld/README.md:63`, the in-game credits of `Samples/OpenWorld/Assets/Worlds/Island.stscene:144` and the binary `Fox.glb`; at the Khronos commit the two lines stand in the "Legal" section of `Models/Fox/README.md`, and as owner and year in its `metadata.json` |
| `new:146` | feature | home | The book's own assets: `tutorials/assets/` with its `CREDITS.md`, and the labs' committed textures, CC0 or CC-BY (`pipelines.md` §5 and §6). General knowledge. |
| `new:147` | feature | home | The engine itself as the source of every excerpt and picture; the repository holds no license file at its root, so the page names the repository and its owner and says only what the repository says of its terms. Evidence: `git ls-tree --name-only 822a7a46` lists no `LICENSE` file (its entries are `.clang-format` to `Tools`, with `ThirdPartyNotices.md` and `README.md`) |
| `new:183` | feature | home | The book's statement, stated once: "Copyright © 2026 2042Third. All rights reserved.", then "Except where otherwise noted" and its two exceptions, the book's code (`new:184`) and third-party material, which keeps its own terms; the holder and the year are `site.json`'s `copyright.holder` and `copyright.year`, and the page links `<base>/license.txt` and `<base>/third-party-notices.txt` (`critique/rulings-6.md`, R20 and R22). General knowledge. |
| `new:184` | feature | home | The permission for the book's code, in the reader's words: the code and project files the book gives (the listings written for the book, the tutorial files, the command scripts, the lab files, the worked solutions and the checkpoint projects) may go into the reader's own programs and games and ship with them, also commercially, without asking and without naming the book; they may not be published as a collection of examples, a course or a book; the text, the pictures, the diagrams and the site are for reading and for printing for one's own use. Excerpts of the engine stay the engine's, and third-party files keep their own terms (`critique/rulings-6.md`, R21), about 120 words with `new:183`. General knowledge. |
| `build-test:96` | feature | use | `ThirdPartyNotices.md`: libraries, fonts, derived code and sample packs |
| `build-test:98` | feature | use | The rule for code from other projects: permissive only, copyleft for ideas only, a notice row and the license text |
| `gamedev:260` | feature | use | Every sample's README credits its assets and its `CREDITS.md` lists every file |
| `gamedev:519` | rule | use | Asset licenses: CC0 or CC-BY only, credited |
| `editor-ui:50` | feature | use | The editor embeds its fonts and `ThirdPartyNotices.md` |
| `animation:212` | feature | use | The Third-Person robot (CC0), the most pictured asset of the book's animation part |
| `build-test:639` | term | link | Permissive and copyleft licenses, defined on `engineering/third-party` |
| `gamedev:665` | term | link | CC0 and CC-BY, defined on `make/assets` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Submodules, the vendor folder and pinned libraries | `engineering/third-party` | helps |
| Permissive and copyleft licenses, and notices | `engineering/third-party` | helps |
| Asset licenses (CC0 and CC-BY) as a game maker meets them | `make/assets` | helps |
| A game's credits and notices when it ships | `make/export` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-appendix-11 | should | thin-home | `appendix/credits` | The page's tables are thinner than its sources. The outline asks for "quoted sources", which the Covers drops: the "books and articles" row of Leaves out sends ideas, not quotations, to `appendix/further-reading`. `third-party-notices.txt` has a section on what the site ships (Source Serif 4, Inter and JetBrains Mono, KaTeX, Starlight, Expressive Code, Pagefind), which the page does not name. And its sample table lists what figures show, not the sample files that tutorials and checkpoints give out. | Add three short parts: the site's own components with their licenses, from `tools/data/notices.json`; the downloads that carry sample files, with the samples' credits; and every source the book quotes in its text or redraws in a figure, with its author and terms. About 150 words of prose and three tables. | `outline-4.md:229`; `allocation/appendix.md:606-631`; `site.md:39`, `:226-232`; `pipelines.md:1508-1517` |

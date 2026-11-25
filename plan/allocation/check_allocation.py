"""Check the allocation of the book's content to its pages: plan/allocation/<unit>.md against the contract
(plan/allocation/README.md), the outline and the inventories.

Run (every subcommand takes --plan <dir>, the plan folder; the default is the folder above this script):
    python plan/allocation/check_allocation.py items
        write items/<inventory>.tsv and items/inventories.sha256; print the items per inventory and type
    python plan/allocation/check_allocation.py check [--unit <unit>]
        the format of every unit's file (or of one), every id, and the owner rule; one line per problem; exit 1 on any;
        then the warnings under their own heading, one line each; a warning never changes the exit code
    python plan/allocation/check_allocation.py inbox <unit>
        the items other files pass to the unit's pages that its file neither homes nor refuses
    python plan/allocation/check_allocation.py demands <unit>
        the Assumes rows of other units that name a page of the unit, then every row with `?`
    python plan/allocation/check_allocation.py code --engine <clone> [--unit <unit>]
        the place of every `home` row of type code exists in the clone's working tree; exit 1 on any failure
    python plan/allocation/check_allocation.py checks
        the items that hold a check before writing (README, "Checks before writing"), by check, each with its page and
        unit; nothing at all when there are none
    python plan/allocation/check_allocation.py coverage
        write coverage.md, what the planner must settle; the same input always gives the same bytes

Standard library only. The outline's pages, parts, kinds, sizes, tracks, Needs and "Needs of the part" are read with
plan/check_outline.py, imported as a module. Problems are printed as "file:line: message", the file relative to the
plan folder.

How the items are found (README, "Items")
- Sections are the "## N. ..." headings of a file of inventory/. Items are in sections 1 to 7 and 9; their type follows
  from the section (SECTION_TYPES). The text before "## 1." (the survey's preamble, with its abbreviations and sources)
  and section 8 hold no items.
- A block is the text between two headings of any level. A block that holds a table gives one item per data row: the
  first row of a table is its header, the second its separator. A block that holds two tables gives the rows of both
  (foundation section 6, scripting 1.1). A block without a table gives one item per top-level entry: a line at column 0
  that starts with "N. ", "- " or "* ". Indented lines, lines directly after an entry, and indented lines after a blank
  line continue the entry. Entries nested under an entry (indented lines that start an entry) are items of their own
  when NESTED_ITEMS names the entry, and a problem when it does not. Paragraphs and horizontal rules are not items.
- An item's id is `<inventory>:<line>`, the line where its row, entry, paragraph or heading starts.
- An item's label: the row's first cell, with its bold marks removed, joined with the second cell when the first is
  only a number or a short id ("12", "E3", "(test)"); the entry's or paragraph's bold lead without its final full stop
  or colon, else its first words; heading items: the heading. Tabs and line breaks become spaces; a label is at most
  100 characters, and a cut one ends with "…".
- A glossary entry is one item, also when it defines further terms in bold inside its text ("**Nit**: ...; **Lux**:
  ..."). Its label then names every term in bold, joined by "; ", so that the glossary sees each of them.

Special cases, each an explicit table below; an entry of a table that names no block of its inventory is a problem, so
the tables cannot go stale silently:
- EXCLUDED_BLOCKS: blocks that are notes about the survey, not content ("How completeness was checked" in all 19 files,
  the lists of headers that belong to other areas, section texts that only explain the shape of the entries or the
  abbreviations).
- PARAGRAPH_BLOCKS: blocks whose content is paragraphs only, with no table and no list (gamedev 1.13 "Audio (maker's
  view)", the concepts A1 to B11 of audio-input written as paragraphs with bold leads, ...). Each paragraph (its lines
  up to a blank line) is one item.
- PARAGRAPH_ITEMS: a paragraph beside a table or a list that holds content of its own ("Sample rules (all samples)"
  after gamedev's table of samples, the shorter code excerpts after a code table, ...). It is one item.
- HEADING_ITEM_SECTIONS: a section whose items are its headings (automation section 2: each concept is a "### 2.n"
  heading, and its list holds the concept's problem, approaches, Strata's choice and mistakes). Each block under a
  heading of the section is one item, its id the heading's line; the section's own text is an introduction.
- NESTED_ITEMS: an entry whose nested entries are items of their own (render-image's "Temporal AA (TAA)", whose
  nested entries are the parts of TAA; build-test's "Documentation drift found", whose nested entries are three
  separate drifts). Each nested entry at the smallest indent is an item, with the lines up to the next one; the entry
  itself stays an item and ends before its first nested entry.
- A block with both a table and a list, a table without a separator row, a block that holds only paragraphs and
  that no table above names, and an entry with nested entries that NESTED_ITEMS does not name are problems of "items"
  and "check".

Decisions where the contract leaves a choice (README, "The file of a unit"):
- Every unit's file has the sections "Passed on", "Not taken" and "Questions for the planner", in this order after
  its page sections, each with a table or list or the one word `none`. A unit without pages (router-gamedev) has only
  "Passed on" and "Questions for the planner".
- The Type and Role cells are plain words, without backquotes. "Taught by" takes `?` with or without backquotes.
  `none` may stand in backquotes and end with a full stop.
- A new item (`new:<n>`) stands alone in its row and appears only in the Items of its pages, never in "Passed on" or
  "Not taken". Rule 5 applies to the row that defines it. A defining home row of type code gives its place as rule 4
  says, and the place is its evidence. A new item of type not-done, erratum or code says something about Strata, so it
  is never `General knowledge.`
- Starting state and Command-only steps: a page of kind T has both, a page of kind H both or neither, a page of kind P
  may have Starting state (a primer's checkpoints) but never Command-only steps, and pages of other kinds have neither.
- Fit: the size is the outline's; every Fit line has a sentence after "(<the size's budget>)". The state is the one
  rule 6's table gives for the estimate against the range of the page's size (RANGES): `fits` from the range's bottom
  to below its top, `over` at or over its top, `under` below its bottom. On a page of kind R the state is `fits` and
  the estimate is compared with nothing, and coverage never lists the page as over or under.
- Warnings never fail the check: they are printed after the problems, under their own heading. The check warns on a
  Fit estimate that equals its size's budget to the word (never on kind R, whose estimate is compared with nothing),
  on a home row of type concept on a page of kind R, and on one on a page of kind H outside part `make`.
- A check before writing: a row of Items whose last cell starts with "Check:" holds a new item of type open, and the
  cell starts with "Check: <the check's name>.", the name running to the first full stop before a space or the end of
  the cell ("Process.h" stays inside a name). An item holds a check when the row that defines it (its home row, else
  its first row) starts so, and its other rows may start so only then; `checks` lists every row of such an item under
  the defining row's name. The names are not compared with the contract's list, so that a check the list lacks still
  shows; a misspelt name shows as a check of its own.
- "Passed on": only the owner of an item's inventory passes the item on; "To" is never a page of the unit itself;
  a feature of the engine is never `nowhere`. "Not taken": "Passed by" is a unit (backquotes optional) whose file passes
  the item to a page of this unit; "Better page" is a page of the outline. "Leaves out": each entry ends with "→" (or
  "->") and one or more page ids in backquotes; `nowhere` is not allowed there.
- The Needs closure of a page (coverage, section 6) holds the page, and for every Need of the page and of its part's
  "Needs of the part" the pages that every alternative of the Need leads to (an alternative's closure; for `a`|`b` the
  pages both closures hold, because "the page may use only what both alternatives teach"), and so on. A page whose
  Needs are `-` needs its part's first page (outline-1.md, "Needs"). Pages that only one alternative leads to are not
  in the closure.
- check also fails when an inventory's SHA-256 is not the one items/inventories.sha256 records, or an item list is not
  what "items" writes. "check --unit U" checks these and U's file, and reads the other files only for the rules across
  files; the table of units (UNITS against the outline) and files of allocation/ that are no unit's are checked by
  "check" of all units.
- inbox: an item is settled when the unit's file homes it on any of its pages, or refuses it under "Not taken" naming
  the unit that passed it.
- coverage counts home rows per type, as the contract says, not the items the rows name. An inventory whose owner's
  file is missing gets one line in section 2, not a list of all its items. Section 9 holds the problems of "check"
  without the owner rule and the homes of items a unit does not own, which sections 2 and 5 list.
"""

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # neither this script nor its tests leave cache files in plan/
DEFAULT_PLAN = Path(__file__).resolve().parent.parent
if str(DEFAULT_PLAN) not in sys.path:
	sys.path.insert(0, str(DEFAULT_PLAN))
import check_outline  # noqa: E402  (the outline's check, plan/check_outline.py)

INVENTORY_DIR = "inventory"
ALLOCATION_DIR = "allocation"
ITEMS_DIR = "items"
HASH_FILE = "inventories.sha256"
COVERAGE_FILE = "coverage.md"
# Files of allocation/ that are no unit's file.
NOT_UNIT_FILES = {"README.md", COVERAGE_FILE, "completeness.md"}

SECTION_TYPES = {1: "feature", 2: "concept", 3: "code", 4: "figure", 5: "rule", 6: "hands-on", 7: "term", 9: "open"}
ITEM_TYPES = ["feature", "concept", "code", "figure", "rule", "hands-on", "term", "open"]
TYPES = ITEM_TYPES + ["not-done", "erratum"]
ROLES = ["home", "use", "link"]
DEPTHS = ["must", "helps"]
FIT_STATES = ["fits", "under", "over"]
WORDS = check_outline.WORDS
# Rule S (README, "Sizes, Needs and homes"): the range of prose words of each size, its bottom and its top. WORDS holds
# the budgets.
RANGES = {"S": (600, 2250), "M": (2251, 4000), "L": (4001, 6500), "XL": (6501, 10000)}
# Pages of kind R have no size check (README, rule 6), and are the home only of catalogue items.
REFERENCE_KIND = "R"
# Concept items homed on a page of kind H outside this part get a warning (README, "Sizes, Needs and homes").
HOW_TO_PARTS = ("start", "make")
GENERATED_SEGMENTS = check_outline.RESERVED_LAST_SEGMENTS
NOWHERE = "nowhere"
NO_TEACHER = "?"
LABEL_LIMIT = 100
# New items that say something about Strata, so never `General knowledge.`
ENGINE_NEW_TYPES = {"not-done", "erratum", "code"}

PAGE_PARTS = ["Covers", "Leaves out", "Fit", "Items", "Assumes", "Starting state", "Command-only steps"]
REQUIRED_PARTS = PAGE_PARTS[:5]
STEP_PARTS = PAGE_PARTS[5:]
FILE_SECTIONS = ["Passed on", "Not taken", "Questions for the planner"]
NO_PAGE_SECTIONS = ["Passed on", "Questions for the planner"]
TABLE_HEADERS = {
	"Items": ["Item", "Type", "Role", "What the page takes from it"],
	"Assumes": ["Concept", "Taught by", "Depth"],
	"Passed on": ["Item", "Type", "To", "Why"],
	"Not taken": ["Item", "Passed by", "Why not", "Better page"],
}

# The units of README "Units": (unit, pages, the inventory it owns). The pages are spans (part, first page, last page);
# a span without a first and a last page is the whole part.
UNITS = [
	("start", [("start", None, None)], None),
	("make-a", [("make", "make/editor-tour", "make/project-coin-run")], None),
	("make-b1", [("make", "make/gameplay-math", "make/levels-saves")], None),
	("make-b2", [("make", "make/lamps", "make/samples")], None),
	("make-c", [("make", "make/designing-a-game", "make/project-platformer")], None),
	("basics-a", [("basics", "basics/computer", "basics/data-formats"), ("basics", "basics/threads", "basics/threads")],
		None),
	("basics-b", [("basics", "basics/math-vectors", "basics/math-sphere")], None),
	("core", [("core", None, None)], "foundation"),
	("world", [("world", None, None)], "scene-ecs"),
	("gpu", [("gpu", None, None)], "render-core"),
	("assets", [("assets", None, None)], "assets"),
	("draw", [("draw", None, None)], "render-scene"),
	("light", [("light", None, None)], "render-direct"),
	("image", [("image", None, None)], "render-image"),
	("indirect", [("indirect", None, None)], "render-indirect"),
	("physics", [("physics", None, None)], "physics"),
	("animation", [("animation", None, None)], "animation"),
	("audio-input", [("audio", None, None), ("input", None, None)], "audio-input"),
	("scripting", [("scripting", None, None)], "scripting"),
	("ui", [("ui", None, None)], "gameui"),
	("worlds", [("worlds", None, None)], "worlds-runtime"),
	("editor", [("editor", None, None)], "editor-core"),
	("editor-ui", [("editor-ui", None, None)], "editor-ui"),
	("automation", [("automation", None, None)], "automation"),
	("engineering", [("engineering", None, None)], "build-test"),
	("capstone", [("capstone", None, None)], None),
	("reference", [("reference", None, None)], None),
	("appendix", [("appendix", None, None)], None),
	("router-gamedev", [], "gamedev"),
]

COMPLETENESS = "How completeness was checked"
COMPLETENESS_REASON = "the survey's note on how it checked its own completeness"

# Blocks that are notes about the survey, not content: (inventory, heading, reason).
EXCLUDED_BLOCKS = [
	("animation", COMPLETENESS, COMPLETENESS_REASON),
	("assets", COMPLETENESS, COMPLETENESS_REASON),
	("audio-input", COMPLETENESS, COMPLETENESS_REASON),
	("automation", COMPLETENESS, COMPLETENESS_REASON),
	("build-test", COMPLETENESS, COMPLETENESS_REASON),
	("editor-core", COMPLETENESS, COMPLETENESS_REASON),
	("editor-ui", COMPLETENESS, COMPLETENESS_REASON),
	("foundation", COMPLETENESS, COMPLETENESS_REASON),
	("gamedev", COMPLETENESS, COMPLETENESS_REASON),
	("gameui", COMPLETENESS, COMPLETENESS_REASON),
	("physics", COMPLETENESS, COMPLETENESS_REASON),
	("render-core", COMPLETENESS, COMPLETENESS_REASON),
	("render-direct", COMPLETENESS, COMPLETENESS_REASON),
	("render-image", COMPLETENESS, COMPLETENESS_REASON),
	("render-indirect", "1.11 " + COMPLETENESS, COMPLETENESS_REASON),
	("render-scene", COMPLETENESS, COMPLETENESS_REASON),
	("scene-ecs", COMPLETENESS, COMPLETENESS_REASON),
	("scripting", COMPLETENESS, COMPLETENESS_REASON),
	("worlds-runtime", COMPLETENESS, COMPLETENESS_REASON),
	("automation", "1. Features",
		"the section's own text explains the abbreviations of document references and where the releases are dated"),
	("render-image", "1. Features", "the section's own text explains the shape of each entry"),
	("render-scene", "1. Features",
		"the section's own text explains the shape of each entry and which release holds which wave"),
	("editor-core", "1.13 Other headers in the folder (listed for completeness, owned by other areas)",
		"headers the survey accounted for that other inventories own"),
	("render-core", "1.16 Headers of R/ that belong to other areas (accounted for, not inventoried here)",
		"headers the survey accounted for that other inventories own"),
]

# Blocks whose content is paragraphs only: each paragraph is one item. (inventory, heading, reason).
PARAGRAPH_BLOCKS = [
	("animation", "1.16 Not in Strata yet (so the book must not imply it)",
		"what Strata does not do yet, as one paragraph"),
	("audio-input", "Part A: sound", "the concepts A1 to A12, each a paragraph with a bold lead"),
	("audio-input", "Part B: input", "the concepts B1 to B11, each a paragraph with a bold lead"),
	("gamedev", "1.13 Audio (maker's view)", "the maker's audio features, as one paragraph"),
	("gamedev", "1.14 Game UI and menus (maker's view)", "the maker's game UI features, as one paragraph"),
	("gamedev", "1.16 Worlds (maker's view)", "the maker's world features, as one paragraph"),
	("physics", "1.13 Script API (game developers' surface)", "the physics script API, as one paragraph"),
	("physics", "1.14 The Physics Playground sample", "the sample, as one paragraph"),
	("render-direct", "1.12 GPU stages and bindings of the area",
		"the area's GPU stages and its bindings, two paragraphs"),
	("render-direct", "1.13 Area lights", "area lights are not on main: what Strata has instead, as one paragraph"),
	("render-direct", "1.14 Tests that define the area's behaviour", "the area's tests, as one paragraph"),
	("render-indirect", "1.10 Frame placement (pass order of this area)",
		"the area's passes in the frame, as one paragraph"),
	("scene-ecs", "1.6 Scene services (how systems of different modules talk)", "the scene services, as one paragraph"),
	("scene-ecs", "1.14 Registration of the Scene module", "the module's registration, as one paragraph"),
	("scene-ecs", "1.15 User-visible surfaces that sit on this area (owned by the editor area, listed so the book "
		"covers them)", "the editor surfaces of the area, as one paragraph"),
	("scripting", "1.8 Tests that define the behavior", "the area's tests, as one paragraph"),
]

# Paragraphs beside a table or a list that hold content of their own: each is one item. (inventory, heading, the
# paragraph's first words, reason).
PARAGRAPH_ITEMS = [
	("animation", "3. Code worth showing", "The JSON form of a controller", "a code excerpt outside the table"),
	("audio-input", "3. Code worth showing", "Shorter supporting snippets:", "code excerpts outside the table"),
	("audio-input", "Screenshots (editor; none is a rendering feature)", "Non-image figures:",
		"figures that are not screenshots, outside the list"),
	("build-test", "1.13 Tools/ (every tool)", "All Python tools are standard-library only",
		"a feature of every tool, below the table"),
	("editor-ui", "1.4 The widget kit (`UI/Widgets.h`) and its helpers", "Every kit widget is sized from the font",
		"a feature of every widget of the kit, above the table"),
	("foundation", "3. Code worth showing", "Smaller supporting pieces:", "code excerpts outside the table"),
	("gamedev", "1.20 The five samples", "Sample rules (all samples):", "the rules every sample follows, below the table"),
	("gameui", "3. Code worth showing", "Also short ones for the game-developer track:",
		"code excerpts outside the table"),
	("render-core", "1.10 The frame of `SceneRenderer` (pass order)", "Related renderer-level features:",
		"features of the scene renderer, below the table"),
	("render-core", "1.10 The frame of `SceneRenderer` (pass order)", "File split of the frame:",
		"the files of the frame, below the table"),
	("render-core", "1.10 The frame of `SceneRenderer` (pass order)", "`GameRenderer`",
		"the game's renderer, below the table"),
	("render-direct", "1.11 Quality rows that belong to this area", "Renderer specification switches",
		"the renderer's switches that are no quality rows, below the table"),
	("render-image", "3. Code worth showing (excerpts)", "Small pieces suitable as inline snippets:",
		"code excerpts outside the table"),
	("render-indirect", "1.8 Global illumination (experimental, world-space radiance cascades)", "What `main` has:",
		"what main holds of global illumination and what it does not, above the table"),
	("render-scene", "3. Code worth showing", "Also useful, shorter:", "code excerpts outside the table"),
	("scene-ecs", "1.2 The Scene module's own components", "Unregistered runtime-only components",
		"the components that are never registered, below the table"),
	("scripting", "1.1 The C ABI (`StrataScriptCore/Include/StrataScript/ScriptABI.h`, 858 lines, pure C)",
		"Class callbacks (15,", "the class callbacks, below the tables"),
]

# Sections whose items are headings: (inventory, section number, reason).
HEADING_ITEM_SECTIONS = [
	("automation", 2, "each concept is a `### 2.n` heading; its list holds the problem, the approaches, Strata's choice "
		"and the mistakes"),
]

# Entries whose nested entries are items of their own: (inventory, heading, the entry's first words, reason).
NESTED_ITEMS = [
	("render-image", "1.8 Anti-aliasing", "**Temporal AA (TAA)**",
		"the parts of TAA (jitter, history, resources, resolve, noise turn, settings, sharpening, settling), each a "
		"feature a page may teach"),
	("build-test", "9. Not determined", "Documentation drift found",
		"three drifts of the engine's documents, each found in a different place"),
]

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
SECTION_NUMBER = re.compile(r"^(\d+)\.\s")
ENTRY_START = re.compile(r"^(?:\d+\.|[-*])\s+(.*)$")
RULE_LINE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")
SHORT_CELL = re.compile(r"^(?:[A-Z]{0,2}\d+[a-z]?|\([^()]*\))$")
BOLD_LEAD = re.compile(r"^\*\*(.+?)\*\*")
PAGE_HEADING = re.compile(r"^##\s+`([^`]+)`(.*)$")
TITLE = re.compile(r"^#\s+Allocation:\s*(\S+)\s*$")
PART_LABEL = re.compile(r"^\*\*([A-Z][A-Za-z -]*?)\s*([.:]?)\*\*\s*([.:]?)(.*)$")
IDS_CELL = re.compile(r"^`[^`]+`(?:\s*,\s*`[^`]+`)*$")
INVENTORY_ID = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*):(\d+)(?:-(\d+))?$")
NEW_ID = re.compile(r"^new:(\d+)$")
PLACE = re.compile(r"^`([^`\s]+):(\d+)-(\d+)`")
FIT_LINE = re.compile(r"^`([^`]*)`:\s*about\s+([\d,]+)\s+words\s+against\s+`?([A-Za-z]+)`?\s*\(([\d,]+)\)(.*)$")
CODE_SPAN = re.compile(r"^`([^`]+)`$")
CHECK_PREFIX = "Check:"
CHECK_CELL = re.compile(r"^Check:[ \t]*(\S.*?)\.(?:\s|$)")


# ---------------------------------------------------------------------------------------------------------------------
# Text helpers

def split_cells(line):
	"""The cells of a table row. A pipe inside backquotes, or escaped (`\\|`), belongs to its cell."""
	text = line.strip()
	if text.startswith("|"):
		text = text[1:]
	cells = _split_cells(text, True)
	if cells is None:  # an unbalanced backquote: split on every pipe
		cells = _split_cells(text, False)
	return cells


def _split_cells(text, respect_code):
	cells = []
	current = []
	in_code = False
	ended = False
	index = 0
	while index < len(text):
		char = text[index]
		ended = False
		if char == "\\" and text[index + 1:index + 2] == "|":
			current.append("|")
			index += 2
			continue
		if char == "`" and respect_code:
			in_code = not in_code
		elif char == "|" and not in_code:
			cells.append("".join(current).strip())
			current = []
			ended = True
			index += 1
			continue
		current.append(char)
		index += 1
	if in_code:
		return None
	if not ended:
		cells.append("".join(current).strip())
	return cells


def is_separator(line):
	cells = split_cells(line)
	return bool(cells) and all(SEPARATOR_CELL.match(cell) for cell in cells)


def one_line(text):
	return re.sub(r"\s+", " ", text.replace("\t", " ")).strip()


def clip(text):
	text = one_line(text)
	if len(text) <= LABEL_LIMIT:
		return text
	cut = text[:LABEL_LIMIT - 1]
	space = cut.rfind(" ")
	if space >= LABEL_LIMIT * 0.6:
		cut = cut[:space]
	return cut.rstrip() + "…"


def text_label(text):
	"""An entry's or a paragraph's label: its bold lead, else its first words."""
	text = one_line(text)
	lead = BOLD_LEAD.match(text)
	if lead:
		name = lead.group(1).strip().rstrip(".:").strip()
		if name:
			return clip(name)
	return clip(text.replace("**", ""))


def term_label(text):
	"""A glossary entry's label: every term it defines in bold, joined by "; ", when it defines more than one; else the
	label of any entry."""
	terms = [term.strip().rstrip(".:").strip() for term in re.findall(r"\*\*(.+?)\*\*", one_line(text))]
	terms = [term for term in terms if term]
	if len(terms) > 1:
		return clip("; ".join(terms))
	return text_label(text)


def row_label(cells):
	"""A table row's label: its first cell, joined with the second when the first is only a number or a short id."""
	cells = [cell.replace("**", "").strip() for cell in cells]
	first = cells[0] if cells else ""
	if (not first or SHORT_CELL.match(first)) and len(cells) > 1 and cells[1]:
		return clip(f"{first}: {cells[1]}" if first else cells[1])
	return clip(first)


def is_none(nonblank):
	"""True when the lines hold only the one word `none`."""
	if len(nonblank) != 1:
		return False
	word = nonblank[0][1].strip().rstrip(".").strip("`").strip()
	return word == "none"


def code_word(cell):
	"""The word of a cell written in backquotes, or the cell itself."""
	cell = cell.strip()
	match = CODE_SPAN.match(cell)
	return match.group(1).strip() if match else cell


def sort_key_problem(text):
	match = re.match(r"^([^:]+):(\d+):", text)
	if match:
		return (match.group(1), int(match.group(2)), text)
	return (text.split(":")[0], 0, text)


# ---------------------------------------------------------------------------------------------------------------------
# Items of the inventories

class Item:
	def __init__(self, inventory, line, end, type_, heading, label):
		self.inventory = inventory
		self.line = line
		self.end = end
		self.type = type_
		self.heading = heading
		self.label = label

	@property
	def id(self):
		return f"{self.inventory}:{self.line}"


class Inventory:
	def __init__(self, name):
		self.name = name
		self.file = f"{INVENTORY_DIR}/{name}.md"
		self.items = []
		self.by_line = {}
		self.excluded = []  # (heading, line, reason)
		self.problems = []

	def problem(self, line, message):
		self.problems.append(f"{self.file}:{line}: {message}" if line else f"{self.file}: {message}")

	def add(self, item):
		if item.line in self.by_line:
			self.problem(item.line, "two items start on this line")
			return
		self.items.append(item)
		self.by_line[item.line] = item

	def item_at(self, line):
		for item in self.items:
			if item.line <= line <= item.end:
				return item
		return None


class Block:
	def __init__(self, level, heading, line, section):
		self.level = level
		self.heading = heading
		self.line = line
		self.section = section
		self.lines = []


class Piece:
	def __init__(self, kind, start):
		self.kind = kind  # "table", "entry" or "paragraph"
		self.start = start
		self.lines = []

	@property
	def end(self):
		return self.lines[-1][0] if self.lines else self.start

	def text(self):
		parts = []
		for index, (_, line) in enumerate(self.lines):
			if index == 0 and self.kind == "entry":
				line = ENTRY_START.match(line.strip()).group(1)  # stripped: a nested entry is indented
			parts.append(line.strip())
		return " ".join(parts)


def indent_width(line):
	return len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip())


def split_nested(entry):
	"""An entry and the entries nested under it: (the entry's own lines as a piece, the nested entries as pieces). A
	nested entry is an indented line of the entry that starts an entry, at the smallest indent among them; it runs to
	the next one or to the end of the entry. Without nested entries: (the entry, [])."""
	starts = [(index, indent_width(line)) for index, (_, line) in enumerate(entry.lines)
		if index and line[:1] in " \t" and ENTRY_START.match(line.strip())]
	if not starts:
		return entry, []
	indent = min(width for _, width in starts)
	firsts = [index for index, width in starts if width == indent]
	own = Piece("entry", entry.start)
	own.lines = entry.lines[:firsts[0]]
	children = []
	for position, index in enumerate(firsts):
		stop = firsts[position + 1] if position + 1 < len(firsts) else len(entry.lines)
		child = Piece("entry", entry.lines[index][0])
		child.lines = entry.lines[index:stop]
		children.append(child)
	return own, children


def read_blocks(text):
	blocks = [Block(0, "", 0, None)]
	section = None
	for number, line in enumerate(text.splitlines(), start=1):
		heading = HEADING.match(line)
		if heading:
			level = len(heading.group(1))
			title = heading.group(2).strip()
			if level <= 2:
				match = SECTION_NUMBER.match(title) if level == 2 else None
				section = int(match.group(1)) if match else None
			blocks.append(Block(level, title, number, section))
			continue
		blocks[-1].lines.append((number, line))
	return blocks


def split_pieces(lines):
	"""The tables, top-level entries and paragraphs of a block, in order."""
	pieces = []
	current = None  # the piece the next line may continue
	open_entry = None  # an entry that an indented line after a blank line continues
	for number, line in lines:
		if not line.strip():
			if current is not None and current.kind == "entry":
				open_entry = current
			current = None
			continue
		if RULE_LINE.match(line):
			current = None
			open_entry = None
			continue
		if line.startswith("|"):
			if current is None or current.kind != "table":
				current = Piece("table", number)
				pieces.append(current)
			current.lines.append((number, line))
			open_entry = None
			continue
		if ENTRY_START.match(line):
			current = Piece("entry", number)
			current.lines.append((number, line))
			pieces.append(current)
			open_entry = None
			continue
		if line[0] in " \t":
			if current is not None and current.kind != "table":
				current.lines.append((number, line))
				continue
			if current is None and open_entry is not None:
				current = open_entry
				current.lines.append((number, line))
				continue
		if current is not None and current.kind in ("entry", "paragraph"):
			current.lines.append((number, line))  # a line directly after an entry or a paragraph continues it
			continue
		current = Piece("paragraph", number)
		current.lines.append((number, line))
		pieces.append(current)
		open_entry = None
	return pieces


def find_items(name, text):
	"""The items of one inventory file (README "Items"; the module's docstring states the rules)."""
	inventory = Inventory(name)
	blocks = read_blocks(text)
	excluded = {heading: reason for owner, heading, reason in EXCLUDED_BLOCKS if owner == name}
	paragraph_blocks = {heading: reason for owner, heading, reason in PARAGRAPH_BLOCKS if owner == name}
	paragraph_items = {}
	for owner, heading, start, reason in PARAGRAPH_ITEMS:
		if owner == name:
			paragraph_items.setdefault(heading, []).append(start)
	heading_sections = {section for owner, section, _ in HEADING_ITEM_SECTIONS if owner == name}
	nested_items = {}
	for owner, heading, start, reason in NESTED_ITEMS:
		if owner == name:
			nested_items.setdefault(heading, []).append(start)
	headings = [block.heading for block in blocks if block.level]
	for heading in sorted(set(excluded) | set(paragraph_blocks) | set(paragraph_items) | set(nested_items)):
		count = headings.count(heading)
		if count != 1:
			inventory.problem(0, f"check_allocation.py names the block {heading!r}, which is the heading of {count} "
				"blocks of the file, not of one")
	for section in sorted(heading_sections):
		if not any(block.level == 2 and block.section == section for block in blocks):
			inventory.problem(0, f"check_allocation.py names section {section} in HEADING_ITEM_SECTIONS; the file has "
				"no such section")
	for index, block in enumerate(blocks):
		type_ = SECTION_TYPES.get(block.section)
		if type_ is None or block.level == 0:
			continue
		heading = "" if block.level == 2 else block.heading
		where = block.line
		if block.heading in excluded:
			inventory.excluded.append((block.heading, block.line, excluded[block.heading]))
			continue
		pieces = split_pieces(block.lines)
		tables = [piece for piece in pieces if piece.kind == "table"]
		entries = [piece for piece in pieces if piece.kind == "entry"]
		paragraphs = [piece for piece in pieces if piece.kind == "paragraph"]
		if block.section in heading_sections:
			if block.level == 2:
				if tables or entries:
					inventory.problem(where, "the items of this section are its headings, but its own text holds a "
						"table or a list")
				continue
			end = block.lines[-1][0] if block.lines else block.line
			inventory.add(Item(name, block.line, end, type_, block.heading, clip(block.heading)))
			continue
		if block.heading in paragraph_blocks:
			if tables or entries:
				inventory.problem(where, "PARAGRAPH_BLOCKS names this block, but it holds a table or a list")
			if not paragraphs:
				inventory.problem(where, "PARAGRAPH_BLOCKS names this block, but it holds no paragraph")
			for paragraph in paragraphs:
				inventory.add(Item(name, paragraph.start, paragraph.end, type_, heading, text_label(paragraph.text())))
			continue
		if tables and entries:
			inventory.problem(where, "the block holds a table and a list; check_allocation.py has no rule for such a "
				"block")
		for table in tables:
			rows = table.lines
			if len(rows) < 2 or not is_separator(rows[1][1]):
				inventory.problem(rows[0][0], "a table without a header row and a separator row")
				continue
			for number, line in rows[2:]:
				inventory.add(Item(name, number, number, type_, heading, row_label(split_cells(line))))
		label = term_label if type_ == "term" else text_label
		named = nested_items.get(block.heading, [])
		for start in named:
			matches = [entry for entry in entries if entry.text().startswith(start)]
			if len(matches) != 1:
				inventory.problem(where, f"NESTED_ITEMS names the entry {start!r} of this block; the block holds "
					f"{len(matches)} entries that start so, not one")
			elif not split_nested(matches[0])[1]:
				inventory.problem(matches[0].start, f"NESTED_ITEMS names the entry {start!r}, but no entry is nested "
					"under it")
		if not tables:
			for entry in entries:
				own, children = split_nested(entry)
				if children and not any(entry.text().startswith(start) for start in named):
					inventory.problem(entry.start, f"the entry holds {len(children)} entries nested under it, which one item "
						"would hide: name it in NESTED_ITEMS, so that each nested entry is an item of its own")
					own, children = entry, []
				for piece in [own] + children:
					inventory.add(Item(name, piece.start, piece.end, type_, heading, label(piece.text())))
		for start in paragraph_items.get(block.heading, []):
			matches = [paragraph for paragraph in paragraphs if paragraph.text().startswith(start)]
			if len(matches) != 1:
				inventory.problem(where, f"PARAGRAPH_ITEMS names the paragraph {start!r} of this block; the block holds "
					f"{len(matches)} paragraphs that start so, not one")
				continue
			paragraph = matches[0]
			inventory.add(Item(name, paragraph.start, paragraph.end, type_, heading, text_label(paragraph.text())))
		if not tables and not entries and paragraphs and block.heading not in paragraph_items:
			inventory.problem(where, "the block holds only paragraphs: name it in PARAGRAPH_BLOCKS (content) or "
				"EXCLUDED_BLOCKS (a note about the survey)")
	inventory.items.sort(key=lambda item: item.line)
	return inventory


def tsv_text(inventory):
	lines = ["id\ttype\theading\tlabel"]
	for item in inventory.items:
		lines.append("\t".join([item.id, item.type, one_line(item.heading), one_line(item.label)]))
	return "\n".join(lines) + "\n"


def hash_text(digests):
	return "".join(f"{digests[name]}  {name}.md\n" for name in sorted(digests))


# ---------------------------------------------------------------------------------------------------------------------
# The plan: outline, units, inventories and the units' files

class Unit:
	def __init__(self, name, spans, inventory):
		self.name = name
		self.spans = spans
		self.inventory = inventory
		self.pages = []  # page ids in the outline's order


def read_outline(root):
	saved = check_outline.PLAN
	check_outline.PLAN = Path(root)
	try:
		outline = check_outline.Outline()
		check_outline.read_outline(outline)
		check_outline.read_tracks(outline)
	finally:
		check_outline.PLAN = saved
	return outline


def parse_part_needs(text):
	"""The Needs of a "Needs of the part" line: a list of Needs, each a list of alternative page ids."""
	if text is None or text.strip() in ("", "-", "-."):
		return []
	needs = []
	for item in text.split(","):
		alternatives = re.findall(r"`([^`]+)`", item)
		if alternatives:
			needs.append(alternatives)
	return needs


class Plan:
	def __init__(self, root):
		self.root = Path(root)
		self.allocation = self.root / ALLOCATION_DIR
		self.items_dir = self.allocation / ITEMS_DIR
		self.outline = read_outline(self.root)
		self.pages = self.outline.pages
		self.by_id = {}
		for page in self.pages:
			self.by_id.setdefault(page.id, page)
		self.inventory_problems = []
		self.inventories = {}
		self.inventory_bytes = {}
		inventory_dir = self.root / INVENTORY_DIR
		if not inventory_dir.is_dir():
			self.inventory_problems.append(f"{INVENTORY_DIR}/: folder missing")
		else:
			for path in sorted(inventory_dir.glob("*.md")):
				data = path.read_bytes()
				try:
					text = data.decode("utf-8")
				except UnicodeDecodeError:
					self.inventory_problems.append(f"{INVENTORY_DIR}/{path.name}: not UTF-8")
					continue
				self.inventories[path.stem] = find_items(path.stem, text)
				self.inventory_bytes[path.stem] = data
		self.unit_problems = []
		self.units = {}
		self.page_units = {}
		self.owners = {}
		self.assign_units()
		self.files = {}

	def assign_units(self):
		parts = {part.slug: part for part in self.outline.parts}
		where = "check_allocation.py UNITS"
		for name, spans, inventory in UNITS:
			if name in self.units:
				self.unit_problems.append(f"{where}: unit `{name}` is listed twice")
				continue
			unit = Unit(name, spans, inventory)
			chosen = set()
			for slug, first, last in spans:
				part = parts.get(slug)
				if part is None:
					self.unit_problems.append(f"{where}: unit `{name}` names part `{slug}`, which the outline does not "
						"have")
					continue
				ids = [page.id for page in part.pages]
				if first is None and last is None:
					chosen.update(ids)
					continue
				if first not in ids or last not in ids:
					missing = first if first not in ids else last
					self.unit_problems.append(f"{where}: unit `{name}` names `{missing}`, which is no page of part "
						f"`{slug}`")
					continue
				if ids.index(first) > ids.index(last):
					self.unit_problems.append(f"{where}: unit `{name}`: `{first}` comes after `{last}` in part `{slug}`")
					continue
				chosen.update(ids[ids.index(first):ids.index(last) + 1])
			unit.pages = [page.id for page in self.pages if page.id in chosen]
			for page_id in unit.pages:
				self.page_units.setdefault(page_id, []).append(name)
			if inventory is not None:
				if inventory in self.owners:
					self.unit_problems.append(f"{where}: inventory `{inventory}` is owned by `{self.owners[inventory]}` "
						f"and by `{name}`")
				else:
					self.owners[inventory] = name
			self.units[name] = unit
		for page in self.pages:
			units = self.page_units.get(page.id, [])
			if len(units) != 1:
				held = ", ".join(f"`{unit}`" for unit in units) or "no unit"
				self.unit_problems.append(f"{page.file}:{page.line}: page `{page.id}` belongs to {held}; every page "
					"belongs to exactly one unit (UNITS in check_allocation.py)")
		for inventory in sorted(self.owners):
			if inventory not in self.inventories:
				self.unit_problems.append(f"{where}: unit `{self.owners[inventory]}` owns inventory `{inventory}`, but "
					f"{INVENTORY_DIR}/{inventory}.md does not exist")
		for inventory in sorted(self.inventories):
			if inventory not in self.owners:
				self.unit_problems.append(f"{INVENTORY_DIR}/{inventory}.md: no unit owns this inventory (UNITS in "
					"check_allocation.py)")

	def unit_of(self, page_id):
		units = self.page_units.get(page_id)
		return units[0] if units else None

	def file(self, name):
		if name not in self.files:
			self.files[name] = UnitFile(self, name)
		return self.files[name]

	def existing_files(self):
		return [self.file(name) for name in self.units if self.file(name).exists]

	def resolve(self, ref):
		"""The items an inventory id names, and a problem (or None)."""
		inventory = self.inventories.get(ref.inventory)
		if inventory is None:
			return [], f"`{ref.text}` names no inventory ({INVENTORY_DIR}/{ref.inventory}.md does not exist)"
		if not ref.is_range:
			item = inventory.by_line.get(ref.first)
			if item is None:
				inside = inventory.item_at(ref.first)
				hint = f"; the line lies inside `{inside.id}`" if inside else ""
				return [], f"`{ref.text}`: no item starts at line {ref.first} of {inventory.file}{hint}"
			return [item], None
		if ref.first > ref.last:
			return [], f"`{ref.text}`: the range runs backwards"
		items = [item for item in inventory.items if ref.first <= item.line <= ref.last]
		if not items:
			return [], f"`{ref.text}`: no item starts on lines {ref.first} to {ref.last} of {inventory.file}"
		types = sorted({item.type for item in items})
		if len(types) > 1:
			return items, f"`{ref.text}` holds items of several types ({', '.join(types)}); a range holds items of one type"
		return items, None

	def item(self, item_id):
		inventory, _, line = item_id.partition(":")
		return self.inventories[inventory].by_line[int(line)]

	def all_items(self):
		for name in sorted(self.inventories):
			yield from self.inventories[name].items


# ---------------------------------------------------------------------------------------------------------------------
# The file of a unit

class Ref:
	def __init__(self, text):
		self.text = text
		self.new = None
		self.inventory = None
		self.first = None
		self.last = None
		self.is_range = False


class Row:
	def __init__(self, file, line, page, cells):
		self.file = file
		self.line = line
		self.page = page
		self.cells = cells
		self.refs = []
		self.items = []

	@property
	def where(self):
		return f"{self.file.name}:{self.line}"


class Part:
	def __init__(self, label, line, rest):
		self.label = label
		self.line = line
		self.lines = [(line, rest)]

	def nonblank(self):
		return [(number, text) for number, text in self.lines if text.strip()]


class UnitFile:
	def __init__(self, plan, unit):
		self.plan = plan
		self.unit = plan.units[unit]
		self.name = f"{ALLOCATION_DIR}/{unit}.md"
		self.path = plan.allocation / f"{unit}.md"
		self.exists = self.path.is_file()
		self.problems = []
		self.page_ids = []
		self.item_rows = []
		self.assume_rows = []
		self.passed = []
		self.refused = []
		self.questions = []
		self.fits = {}  # page id -> (state, words, line, text)
		self.warnings = []
		self.check_items = []  # (the check's name, n of new:<n>, the item's rows)
		if self.exists:
			self.parse()

	def problem(self, line, message):
		self.problems.append(f"{self.name}:{line}: {message}" if line else f"{self.name}: {message}")

	def warning(self, line, message):
		self.warnings.append(f"{self.name}:{line}: {message}")

	# Reading

	def parse(self):
		try:
			lines = self.path.read_text(encoding="utf-8").splitlines()
		except UnicodeDecodeError:
			self.problem(0, "not UTF-8")
			return
		unit = self.unit
		sections = []  # [kind, key, line, body]
		current = None
		first_text = next(((number, line) for number, line in enumerate(lines, start=1) if line.strip()), None)
		if first_text is None or not TITLE.match(first_text[1]):
			self.problem(first_text[0] if first_text else 0, f"the file starts with `# Allocation: {unit.name}`")
		for number, line in enumerate(lines, start=1):
			if line.startswith("# "):
				title = TITLE.match(line)
				if (number, line) != first_text:
					self.problem(number, "a second `# ` heading; the file has one title")
				elif title and title.group(1) != unit.name:
					self.problem(number, f"the title names `{title.group(1)}`, not `{unit.name}`")
				continue
			if line.startswith("## "):
				heading = line[3:].strip()
				page = PAGE_HEADING.match(line)
				if page:
					current = ["page", page.group(1), number, []]
				elif heading in FILE_SECTIONS:
					current = ["section", heading, number, []]
				else:
					self.problem(number, f"section {heading!r} is no page (``## `<page id>` — <title>``) and none of "
						f"{', '.join(FILE_SECTIONS)}")
					current = ["unknown", heading, number, []]
				sections.append(current)
				continue
			if current is None:
				if line.strip() and (number, line) != first_text:
					self.problem(number, "text before the first `## ` section")
				continue
			current[3].append((number, line))
		self.check_sections(sections)
		parsed = set()
		for kind, key, number, body in sections:
			if kind == "page" and key in self.page_ids and key not in parsed:
				parsed.add(key)  # a second section for a page is a problem of rule 1, and is not read
				self.parse_page(key, number, body)
			elif kind == "section":
				self.parse_file_section(key, number, body)
		self.check_new_items()

	def check_sections(self, sections):
		"""Rule 1: one section per page of the unit, in the outline's order, then the file's own sections."""
		unit = self.unit
		plan = self.plan
		seen = []
		for kind, page_id, number, _ in sections:
			if kind != "page":
				continue
			if page_id not in plan.by_id:
				if page_id.split("/")[-1] in GENERATED_SEGMENTS:
					self.problem(number, f"`{page_id}` is a generated page; generated pages have no section")
				else:
					self.problem(number, f"`{page_id}` is no page of the outline")
			elif page_id not in unit.pages:
				owner = plan.unit_of(page_id)
				self.problem(number, f"`{page_id}` is a page of `{owner}`, not of `{unit.name}`")
			elif page_id in seen:
				self.problem(number, f"a second section for `{page_id}`")
			else:
				seen.append(page_id)
		self.page_ids = seen
		for page_id in unit.pages:
			if page_id not in seen:
				self.problem(0, f"no section for `{page_id}` (rule 1: one section per page of the unit)")
		expected = [page_id for page_id in unit.pages if page_id in seen]
		if seen != expected:
			at = next(index for index, (got, want) in enumerate(zip(seen, expected)) if got != want)
			line = next(number for kind, key, number, _ in sections if kind == "page" and key == seen[at])
			self.problem(line, f"`{seen[at]}` stands where the outline's order puts `{expected[at]}`")
		names = [key for kind, key, _, _ in sections if kind == "section"]
		required = FILE_SECTIONS if unit.pages else NO_PAGE_SECTIONS
		for name in required:
			if name not in names:
				self.problem(0, f"no `## {name}` section (write `none` under it when it is empty)")
		for kind, key, number, _ in sections:
			if kind == "section" and key not in required:
				self.problem(number, f"`## {key}`: a unit without pages has only "
					f"{' and '.join(NO_PAGE_SECTIONS)}")
		for name in sorted(set(names)):
			if names.count(name) > 1:
				self.problem(0, f"`## {name}` stands {names.count(name)} times")
		order = [key for kind, key, _, _ in sections if kind in ("page", "section")]
		positions = [FILE_SECTIONS.index(key) + 1 if key in FILE_SECTIONS else 0 for key in order]
		if positions != sorted(positions):
			first = next(index for index in range(1, len(positions)) if positions[index] < positions[index - 1])
			line = [number for kind, _, number, _ in sections if kind in ("page", "section")][first]
			self.problem(line, f"out of order: the page sections come first, then {', '.join(FILE_SECTIONS)}")

	def parse_page(self, page_id, heading_line, body):
		"""Rules 2 to 8 for one page section."""
		page = self.plan.by_id[page_id]
		parts = []
		current = None
		for number, line in body:
			label = PART_LABEL.match(line)
			if label and (label.group(1) in PAGE_PARTS or "." in (label.group(2), label.group(3))):
				name = label.group(1)
				if name not in PAGE_PARTS:
					self.problem(number, f"`**{name}.**` is none of the parts {', '.join(PAGE_PARTS)}")
				else:
					if label.group(2) != "." or label.group(3):
						self.problem(number, f"write `**{name}.**`: the part's name in bold with its full stop inside "
							"the bold")
					current = Part(name, number, label.group(4))
					parts.append(current)
					continue
			if current is not None:
				current.lines.append((number, line))
			elif line.strip():
				self.problem(number, "text before **Covers.**")
		names = [part.label for part in parts]
		for name in sorted(set(names)):
			if names.count(name) > 1:
				self.problem(heading_line, f"`{page_id}`: **{name}.** stands {names.count(name)} times")
		for name in REQUIRED_PARTS:
			if name not in names:
				self.problem(heading_line, f"`{page_id}` has no **{name}.**")
		steps = [name for name in STEP_PARTS if name in names]
		if page.kind == "T":
			for name in STEP_PARTS:
				if name not in names:
					self.problem(heading_line, f"`{page_id}` is a tutorial (T) and has no **{name}.**")
		elif page.kind == "H":
			if len(steps) == 1:
				missing = [name for name in STEP_PARTS if name not in names][0]
				self.problem(heading_line, f"`{page_id}` has **{steps[0]}.** but no **{missing}.**; a how-to with "
					"numbered steps has both")
		elif page.kind == "P":
			for name in steps:
				if name != "Starting state":
					self.problem(heading_line, f"`{page_id}` is a primer (P): a primer may have **Starting state.** "
						f"(its checkpoints), and only tutorials and how-tos with steps have **{name}.**")
		else:
			for name in steps:
				self.problem(heading_line, f"`{page_id}` is of kind {page.kind}; only tutorials and how-tos with steps "
					f"have **{name}.**")
		ranks = [PAGE_PARTS.index(name) for name in names]
		for index in range(1, len(ranks)):
			if ranks[index] < ranks[index - 1]:
				self.problem(parts[index].line, f"**{names[index]}.** comes after **{names[index - 1]}.**; the order is "
					f"{', '.join(PAGE_PARTS)}")
				break
		for part in parts:
			if names.count(part.label) > 1 and part is not next(other for other in parts if other.label == part.label):
				continue
			self.parse_part(page, part)

	def parse_part(self, page, part):
		nonblank = part.nonblank()
		label = part.label
		if label in ("Covers", "Starting state"):
			if not nonblank:
				self.problem(part.line, f"**{label}.** is empty")
		elif label in ("Leaves out", "Command-only steps"):
			entries = self.entries_or_none(part, label)
			if label == "Leaves out":
				for number, text in entries:
					self.check_leaves_out(number, text)
		elif label == "Fit":
			self.check_fit(page, part)
		elif label == "Items":
			for number, cells in self.table_or_none(part.lines, part.line, "Items"):
				self.read_item_row(page, number, cells)
		elif label == "Assumes":
			for number, cells in self.table_or_none(part.lines, part.line, "Assumes"):
				self.read_assume_row(page, number, cells)

	def entries_or_none(self, part, name):
		"""The entries of a list, or none for the one word `none`; a problem for anything else."""
		return self.read_entries(part.lines, part.line, name)

	def read_entries(self, lines, label_line, name):
		nonblank = [(number, text) for number, text in lines if text.strip()]
		if not nonblank:
			self.problem(label_line, f"{name} is empty: a list, or the one word `none`")
			return []
		if is_none(nonblank):
			return []
		entries = []
		previous_blank = True
		for number, text in lines:
			if not text.strip():
				previous_blank = True
				continue
			start = ENTRY_START.match(text)
			if start and not text[0].isspace():
				entries.append([number, start.group(1).strip()])
			elif entries and (text[0].isspace() or not previous_blank):
				entries[-1][1] += " " + text.strip()
			else:
				self.problem(number, f"{name}: a line that is no entry of the list (`- ...`); an empty list is the one "
					"word `none`")
			previous_blank = False
		return [(number, text) for number, text in entries]

	def table_or_none(self, lines, label_line, name):
		"""The data rows (line, cells) of a table, or none for the one word `none`; a problem for anything else."""
		expected = TABLE_HEADERS[name]
		nonblank = [(number, text) for number, text in lines if text.strip()]
		if not nonblank:
			self.problem(label_line, f"{name} is empty: a table, or the one word `none`")
			return []
		if is_none(nonblank):
			return []
		rows = []
		for number, text in nonblank:
			if not text.lstrip().startswith("|"):
				self.problem(number, f"{name}: a line outside the table (it holds a table or the one word `none`)")
				continue
			rows.append((number, split_cells(text)))
		if not rows:
			return []
		if rows[0][1] != expected:
			self.problem(rows[0][0], f"{name}: the header is {' | '.join(rows[0][1])}, not {' | '.join(expected)}")
		if len(rows) < 2 or not all(SEPARATOR_CELL.match(cell) for cell in rows[1][1]):
			self.problem(rows[0][0], f"{name}: the header has no separator row below it")
			data = rows[1:]
		else:
			data = rows[2:]
		result = []
		for number, cells in data:
			if len(cells) != len(expected):
				self.problem(number, f"{name}: the row has {len(cells)} cells, not {len(expected)}")
				continue
			result.append((number, cells))
		return result

	def parse_file_section(self, name, line, body):
		if name == "Passed on":
			for number, cells in self.table_or_none(body, line, name):
				self.read_pass_row(number, cells)
		elif name == "Not taken":
			for number, cells in self.table_or_none(body, line, name):
				self.read_refusal_row(number, cells)
		else:
			for number, text in self.read_entries(body, line, name):
				self.questions.append((number, text))

	# Rows

	def read_refs(self, number, cell, allow_new):
		cell = cell.strip()
		if not IDS_CELL.match(cell):
			self.problem(number, f"Item {cell!r} is not ids in backquotes separated by commas")
			return None
		refs = []
		for token in re.findall(r"`([^`]+)`", cell):
			ref = Ref(token)
			new = NEW_ID.match(token)
			if new:
				ref.new = int(new.group(1))
				if not allow_new:
					self.problem(number, f"`{token}`: a new item belongs to the Items of its page; this table holds "
						"inventory ids")
					return None
				if ref.new < 1:
					self.problem(number, f"`{token}`: new items are numbered from 1")
					return None
				refs.append(ref)
				continue
			match = INVENTORY_ID.match(token)
			if not match:
				self.problem(number, f"`{token}` is not `<inventory>:<line>`, `<inventory>:<a>-<b>` or `new:<n>`")
				return None
			ref.inventory = match.group(1)
			ref.first = int(match.group(2))
			ref.last = int(match.group(3) or match.group(2))
			ref.is_range = match.group(3) is not None
			refs.append(ref)
		return refs

	def resolve_refs(self, row, type_cell):
		"""Resolve the inventory ids of a row; every item must be of the Type cell's type."""
		for ref in row.refs:
			if ref.new is not None:
				continue
			items, message = self.plan.resolve(ref)
			if message:
				self.problem(row.line, message)
			row.items.extend(items)
			if not message:
				types = sorted({item.type for item in items})
				if types and types != [type_cell]:
					self.problem(row.line, f"`{ref.text}` is of type {', '.join(types)}; the Type cell says {type_cell!r}")

	def read_item_row(self, page, number, cells):
		row = Row(self, number, page.id, cells)
		refs = self.read_refs(number, cells[0], True)
		row.type = cells[1].strip()
		row.role = cells[2].strip()
		row.text = cells[3].strip()
		if row.type not in TYPES:
			self.problem(number, f"Type {row.type!r} is none of {', '.join(TYPES)} (a plain word, no backquotes)")
		if row.role not in ROLES:
			self.problem(number, f"Role {row.role!r} is none of {', '.join(ROLES)} (a plain word, no backquotes)")
		if not row.text:
			self.problem(number, "the last cell is empty: say what the page takes from the item")
		if refs is None:
			return
		row.refs = refs
		if any(ref.new is not None for ref in refs) and len(refs) > 1:
			self.problem(number, "a new item stands alone in its row")
		self.resolve_refs(row, row.type)
		if row.role == "home" and row.type == "code":
			if len(refs) != 1 or refs[0].is_range:
				self.problem(number, "a home row of type code names one item, no range (rule 4)")
			message = place_problem(row.text)
			if message:
				self.problem(number, message)
		if row.text.startswith(CHECK_PREFIX):
			if len(refs) != 1 or refs[0].new is None or row.type != "open":
				self.problem(number, "a last cell that starts with `Check:` belongs to a new item of type open, alone in "
					"its row (rule 5, a check before writing)")
			elif not CHECK_CELL.match(row.text):
				self.problem(number, "write `Check: <the check's name>.`: the name, then a full stop (rule 5)")
		if row.role == "home" and row.type == "concept":
			ids = ", ".join(f"`{ref.text}`" for ref in refs)
			if page.kind == REFERENCE_KIND:
				self.warning(number, f"{ids}: a concept homed on `{page.id}`, a page of kind R, which is the home only "
					"of catalogue items: its home is a teaching page, and this page holds a `link` row")
			elif page.kind == "H" and page.part.slug not in HOW_TO_PARTS:
				self.warning(number, f"{ids}: a concept homed on `{page.id}`, a how-to outside the parts `start` and `make`: "
					"move it to a concept or internals page, or say in the Fit line why the how-to is where a reader "
					"learns it")
		self.item_rows.append(row)

	def check_new_items(self):
		"""new:<n>: each defined once, by its home row or else by its first row; its type and evidence (rule 5)."""
		rows = {}
		for row in self.item_rows:
			if len(row.refs) == 1 and row.refs[0].new is not None:
				rows.setdefault(row.refs[0].new, []).append(row)
		for number in sorted(rows):
			group = rows[number]
			homes = [row for row in group if row.role == "home"]
			if len(homes) > 1:
				self.problem(homes[1].line, f"`new:{number}` is defined twice (home rows at lines "
					f"{', '.join(str(row.line) for row in homes)}); a new item has one home")
			defining = homes[0] if homes else group[0]
			for row in group:
				if row.type != defining.type:
					self.problem(row.line, f"`new:{number}` is of type {defining.type!r} (line {defining.line}), not "
						f"{row.type!r}")
			message = evidence_problem(defining)
			if message:
				self.problem(defining.line, f"`new:{number}`: {message}")
			check = CHECK_CELL.match(defining.text) if defining.type == "open" else None
			if check:
				self.check_items.append((check.group(1).strip(), number, group))
			elif defining.type == "open" and not defining.text.startswith(CHECK_PREFIX):
				for row in group:
					if row is not defining and row.text.startswith(CHECK_PREFIX):
						self.problem(row.line, f"`new:{number}` starts with `Check:` here, but the row that defines it "
							f"(line {defining.line}) holds no check: the check's name starts the defining row's last cell "
							"(rule 5)")

	def read_assume_row(self, page, number, cells):
		concept, teacher_cell, depth = (cell.strip() for cell in cells)
		if not concept:
			self.problem(number, "Assumes: the Concept cell is empty")
		teacher = None
		if teacher_cell in (NO_TEACHER, f"`{NO_TEACHER}`"):
			teacher = NO_TEACHER
		else:
			match = CODE_SPAN.match(teacher_cell)
			if not match:
				self.problem(number, f"Taught by {teacher_cell!r} is a page id in backquotes or `?`")
			elif match.group(1) not in self.plan.by_id:
				self.problem(number, f"Taught by `{match.group(1)}` is no page of the outline")
			elif match.group(1) == page.id:
				self.problem(number, "Taught by names the page itself; Assumes lists what the page does not teach")
			else:
				teacher = match.group(1)
		if depth not in DEPTHS:
			self.problem(number, f"Depth {depth!r} is none of {', '.join(DEPTHS)}")
		if teacher is not None:
			self.assume_rows.append((page.id, number, concept, teacher, depth))

	def read_pass_row(self, number, cells):
		row = Row(self, number, None, cells)
		refs = self.read_refs(number, cells[0], False)
		row.type = cells[1].strip()
		row.to = None
		row.why = cells[3].strip()
		if row.type not in TYPES:
			self.problem(number, f"Type {row.type!r} is none of {', '.join(TYPES)} (a plain word, no backquotes)")
		if not row.why:
			self.problem(number, "Passed on: the Why cell is empty")
		to = cells[2].strip()
		target = code_word(to)
		if target == NOWHERE:
			row.to = NOWHERE
		elif not CODE_SPAN.match(to):
			self.problem(number, f"To {to!r} is a page id in backquotes or `nowhere`")
		elif target not in self.plan.by_id:
			self.problem(number, f"To `{target}` is no page of the outline")
		elif target in self.unit.pages:
			self.problem(number, f"To `{target}` is a page of `{self.unit.name}` itself: write a home row on it")
		else:
			row.to = target
		if refs is None:
			return
		row.refs = refs
		self.resolve_refs(row, row.type)
		if row.to == NOWHERE and any(item.type == "feature" for item in row.items):
			self.problem(number, "a feature of the engine is never `nowhere`")
		for inventory in sorted({item.inventory for item in row.items}):
			owner = self.plan.owners.get(inventory)
			if owner != self.unit.name:
				self.problem(number, f"`{inventory}` is the inventory of `{owner}`; only an item's owner passes it on "
					"(refuse an item passed to you under Not taken)")
		if row.to is not None:
			self.passed.append(row)

	def read_refusal_row(self, number, cells):
		row = Row(self, number, None, cells)
		refs = self.read_refs(number, cells[0], False)
		row.passed_by = code_word(cells[1])
		row.why = cells[2].strip()
		row.better = None
		if row.passed_by not in self.plan.units:
			self.problem(number, f"Passed by {cells[1].strip()!r} is no unit")
		elif row.passed_by == self.unit.name:
			self.problem(number, "Passed by names this unit itself")
		if not row.why:
			self.problem(number, "Not taken: the Why not cell is empty")
		better = cells[3].strip()
		match = CODE_SPAN.match(better)
		if not match:
			self.problem(number, f"Better page {better!r} is a page id in backquotes")
		elif match.group(1) not in self.plan.by_id:
			self.problem(number, f"Better page `{match.group(1)}` is no page of the outline")
		else:
			row.better = match.group(1)
		if refs is None:
			return
		row.refs = refs
		for ref in refs:
			items, message = self.plan.resolve(ref)
			if message:
				self.problem(number, message)
			row.items.extend(items)
		self.refused.append(row)

	# Other parts

	def check_leaves_out(self, number, text):
		arrow = max(text.rfind("→"), text.rfind("->"))
		if arrow < 0:
			self.problem(number, "an entry of Leaves out ends with `→` and the page that has it, in backquotes")
			return
		target = text[arrow + (1 if text[arrow] == "→" else 2):]
		ids = re.findall(r"`([^`]+)`", target)
		if not text[:arrow].strip():
			self.problem(number, "an entry of Leaves out says what the page leaves out before the arrow")
		if not ids:
			self.problem(number, "an entry of Leaves out names its page in backquotes after the arrow")
		for page_id in ids:
			if page_id not in self.plan.by_id:
				self.problem(number, f"Leaves out names `{page_id}`, which is no page of the outline")

	def check_fit(self, page, part):
		text = " ".join(line.strip() for _, line in part.lines if line.strip())
		match = FIT_LINE.match(text)
		if not match:
			self.problem(part.line, "Fit starts with `fits`, `under` or `over` in backquotes, a colon and \"about N words "
				"against <size> (<the size's budget>)\"")
			return
		state, words, size, size_words, rest = match.groups()
		words = int(words.replace(",", ""))
		size_words = int(size_words.replace(",", ""))
		if state not in FIT_STATES:
			self.problem(part.line, f"Fit: `{state}` is none of {', '.join(FIT_STATES)}")
		if size not in WORDS:
			self.problem(part.line, f"Fit: size {size} is none of {', '.join(WORDS)}")
		elif size != page.size:
			self.problem(part.line, f"Fit measures against {size}; the outline's size of `{page.id}` is {page.size}")
		elif size_words != WORDS[size]:
			self.problem(part.line, f"Fit: size {size} is {WORDS[size]:,} words, not {size_words:,}")
		if not rest.strip(" .;,"):
			self.problem(part.line, "Fit: one or two sentences follow the size (fits: what takes the most words; over: "
				"the next size, or the split with the pages' titles; under: what the page could take from a neighbour, "
				"what phase B adds, or the smaller size; kind R: the generated volume that gives the page its size)")
		if page.kind == REFERENCE_KIND:
			if state in FIT_STATES and state != "fits":
				self.problem(part.line, f"Fit says `{state}`; a page of kind R has no size check, so its state is `fits` "
					"(rule 6)")
		elif page.size in RANGES and state in FIT_STATES:
			bottom, top = RANGES[page.size]
			expected = fit_state(words, page.size)
			if state != expected:
				self.problem(part.line, f"Fit says `{state}` with {words:,} words; against {page.size}'s range of "
					f"{bottom:,} to {top:,} the state is `{expected}` (rule 6)")
			if words == WORDS[page.size]:
				self.warning(part.line, f"Fit states {words:,} words, {page.size}'s budget to the word: count the page "
					"again from its sections before the estimate is believed (rule S5)")
		self.fits[page.id] = (state, words, part.line, "**Fit.** " + text)


def fit_state(words, size):
	"""Rule 6: the state of an estimate against the range of a size (RANGES)."""
	bottom, top = RANGES[size]
	if words >= top:
		return "over"
	if words < bottom:
		return "under"
	return "fits"


def place_problem(text):
	"""Rule 4: the last cell of a home row of type code starts with `<path>:<first>-<last>`."""
	match = PLACE.match(text.strip())
	if not match:
		return ("the last cell of a home row of type code starts with the excerpt's place, `<path from the "
			"repository's root>:<first line>-<last line>` (rule 4)")
	path, first, last = match.group(1), int(match.group(2)), int(match.group(3))
	if path.startswith(("/", "./")) or re.match(r"^[A-Za-z]:", path) or "\\" in path or ".." in path.split("/"):
		return f"`{path}` is not a path from the repository's root"
	if first < 1 or last < first:
		return f"`{path}:{first}-{last}`: the lines run from 1 upwards, the first not after the last"
	return None


def evidence_problem(row):
	"""Rule 5 for the row that defines a new item."""
	text = row.text.strip()
	if row.type == "code" and row.role == "home" and PLACE.match(text):
		return None  # rule 4's place at the pin is the evidence of a new excerpt
	if re.search(r"Evidence:\s*\S", text):
		return None
	if text.endswith("General knowledge."):
		if row.type in ENGINE_NEW_TYPES:
			return (f"a new item of type {row.type} says something about Strata: its last cell states its evidence "
				"after `Evidence:`, never `General knowledge.`")
		return None
	return ("its last cell states its evidence after `Evidence:` (a file and lines at the pin, or the exact search that "
		"finds nothing), or ends with `General knowledge.` (rule 5)")


# ---------------------------------------------------------------------------------------------------------------------
# Rules across files

def passes_by_item(plan):
	"""item id -> list of (row, item) for every row of Passed on of every existing file."""
	result = {}
	for file in plan.existing_files():
		for row in file.passed:
			for item in row.items:
				result.setdefault(item.id, []).append(row)
	return result


def homes_by_item(plan):
	"""item id -> list of rows with role home, over every existing file."""
	result = {}
	for file in plan.existing_files():
		for row in file.item_rows:
			if row.role == "home":
				for item in row.items:
					result.setdefault(item.id, []).append(row)
	return result


def passed_to_unit(plan, passes, item_id, unit_name):
	"""The rows that pass the item to a page of the unit."""
	pages = set(plan.units[unit_name].pages)
	return [row for row in passes.get(item_id, []) if row.to in pages and row.file.unit.name != unit_name]


def check_across(plan, file, owner_rules=True):
	"""The owner rule and homes of items the unit does not own (when owner_rules), and refusals of items nobody
	passed."""
	problems = []
	unit = file.unit
	passes = passes_by_item(plan)
	if owner_rules and unit.inventory is not None and unit.inventory in plan.inventories:
		placements = {}
		for row in file.item_rows:
			if row.role == "home":
				for item in row.items:
					if item.inventory == unit.inventory:
						placements.setdefault(item.id, []).append(("home", row))
		for row in file.passed:
			for item in row.items:
				placements.setdefault(item.id, []).append(("pass", row))
		for item in plan.inventories[unit.inventory].items:
			found = placements.get(item.id, [])
			if not found:
				problems.append(f"{file.name}: `{item.id}` ({item.type}: {item.label}) is placed nowhere; the owner "
					"places every item of its inventory once, as a home row or a row of Passed on")
			elif len(found) > 1:
				kinds = {kind for kind, _ in found}
				lines = ", ".join(str(row.line) for _, row in found)
				what = "homed and passed on" if kinds == {"home", "pass"} else f"placed {len(found)} times"
				problems.append(f"{file.name}:{found[1][1].line}: `{item.id}` is {what} (lines {lines}); the owner "
					"places it exactly once")
	for row in file.item_rows:
		if row.role != "home" or not owner_rules:
			continue
		for item in row.items:
			owner = plan.owners.get(item.inventory)
			if owner == unit.name:
				continue
			if not passed_to_unit(plan, passes, item.id, unit.name):
				problems.append(f"{row.where}: `{item.id}` is of `{owner}`'s inventory, and no file passes it to a page "
					f"of `{unit.name}`: write `use`, and ask under Questions for the planner")
	homed = {item.id for row in file.item_rows if row.role == "home" for item in row.items}
	for row in file.refused:
		for item in row.items:
			if row.passed_by in plan.units and not any(other.file.unit.name == row.passed_by
					for other in passed_to_unit(plan, passes, item.id, unit.name)):
				problems.append(f"{row.where}: `{item.id}` is not passed to a page of `{unit.name}` by `{row.passed_by}`")
			if item.id in homed:
				problems.append(f"{row.where}: `{item.id}` is refused here and homed in the same file")
	return problems


def inventory_problems(plan):
	"""The finder's problems, and whether the hashes and the item lists match the inventories."""
	problems = list(plan.inventory_problems)
	for name in sorted(plan.inventories):
		problems.extend(plan.inventories[name].problems)
	items_name = f"{ALLOCATION_DIR}/{ITEMS_DIR}"
	hash_path = plan.items_dir / HASH_FILE
	if not hash_path.is_file():
		problems.append(f"{items_name}/{HASH_FILE}: file missing; run `check_allocation.py items`")
	else:
		recorded = {}
		for number, line in enumerate(hash_path.read_text(encoding="utf-8").splitlines(), start=1):
			match = re.match(r"^([0-9a-f]{64})\s+\*?(\S+)\.md$", line.strip())
			if not match:
				problems.append(f"{items_name}/{HASH_FILE}:{number}: not `<sha256>  <inventory>.md`")
				continue
			recorded[match.group(2)] = match.group(1)
		for name in sorted(plan.inventories):
			digest = hashlib.sha256(plan.inventory_bytes[name]).hexdigest()
			if name not in recorded:
				problems.append(f"{items_name}/{HASH_FILE}: records no SHA-256 of {INVENTORY_DIR}/{name}.md")
			elif recorded[name] != digest:
				problems.append(f"{INVENTORY_DIR}/{name}.md: its SHA-256 is not the one {items_name}/{HASH_FILE} "
					"records; the inventories are frozen, because item ids are their line numbers")
		for name in sorted(set(recorded) - set(plan.inventories)):
			problems.append(f"{items_name}/{HASH_FILE}: records {INVENTORY_DIR}/{name}.md, which does not exist")
	for name in sorted(plan.inventories):
		path = plan.items_dir / f"{name}.tsv"
		if not path.is_file():
			problems.append(f"{items_name}/{name}.tsv: file missing; run `check_allocation.py items`")
		elif path.read_bytes() != tsv_text(plan.inventories[name]).encode("utf-8"):
			problems.append(f"{items_name}/{name}.tsv: differs from the items of {INVENTORY_DIR}/{name}.md; run "
				"`check_allocation.py items`")
	if plan.items_dir.is_dir():
		for path in sorted(plan.items_dir.glob("*.tsv")):
			if path.stem not in plan.inventories:
				problems.append(f"{items_name}/{path.name}: no inventory {INVENTORY_DIR}/{path.stem}.md")
	return problems


def run_check(plan, unit=None, across=True):
	"""Every problem of the allocation, or of one unit's file; without the owner rule and the homes of items a unit
	does not own when across is False (coverage lists those in sections 2 and 5)."""
	problems = inventory_problems(plan)
	if unit is not None:
		file = plan.file(unit)
		if not file.exists:
			problems.append(f"{file.name}: file missing")
		else:
			problems.extend(file.problems)
			problems.extend(check_across(plan, file))
		return problems
	problems.extend(plan.unit_problems)
	if plan.allocation.is_dir():
		for path in sorted(plan.allocation.glob("*.md")):
			if path.name not in NOT_UNIT_FILES and path.stem not in plan.units:
				problems.append(f"{ALLOCATION_DIR}/{path.name}: no unit of that name (UNITS in check_allocation.py)")
	for name in plan.units:
		file = plan.file(name)
		if not file.exists:
			problems.append(f"{file.name}: file missing")
			continue
		problems.extend(file.problems)
		problems.extend(check_across(plan, file, owner_rules=across))
	return problems


def run_warnings(plan, unit=None):
	"""Every warning of the units' files, or of one unit's file (the module's docstring, "Decisions")."""
	files = [plan.file(unit)] if unit is not None else [plan.file(name) for name in plan.units]
	return [warning for file in files if file.exists for warning in file.warnings]


# ---------------------------------------------------------------------------------------------------------------------
# Needs closure and tracks (coverage, section 6)

def needs_closures(plan):
	"""page id -> the pages a reader of the page has surely read (the module's docstring, "Decisions")."""
	part_needs = {part.slug: parse_part_needs(part.needs_line) for part in plan.outline.parts}
	first_pages = {part.slug: part.pages[0].id for part in plan.outline.parts if part.pages}
	effective = {}
	for page in plan.pages:
		needs = [list(need) for need in page.needs]
		first = first_pages.get(page.part.slug)
		if not needs and first is not None and first != page.id:
			needs = [[first]]
		needs += part_needs.get(page.part.slug, [])
		effective[page.id] = [alternatives for alternatives in
			([page_id for page_id in need if page_id in plan.by_id] for need in needs) if alternatives]
	closure = {page_id: {page_id} for page_id in plan.by_id}
	changed = True
	while changed:
		changed = False
		for page_id in plan.by_id:
			grown = set(closure[page_id])
			for need in effective.get(page_id, []):
				grown |= set.intersection(*(closure[alternative] for alternative in need))
			if grown != closure[page_id]:
				closure[page_id] = grown
				changed = True
	return closure


def track_note(plan, page, teacher):
	"""Whether the teacher comes before the page on every track the page is on."""
	if not page.tracks:
		earlier = plan.by_id[teacher].index < page.index
		return f"on no track; earlier in the book's order: {'yes' if earlier else 'no'}"
	notes = []
	for letter in page.tracks:
		entries = plan.outline.tracks.get(letter, [])
		ids = [page_id for page_id, _, _ in entries]
		if page.id not in ids:
			notes.append(f"{letter} not listed")
			continue
		before = entries[:ids.index(page.id)]
		if any(page_id == teacher and not side_step for page_id, side_step, _ in before):
			notes.append(f"{letter} yes")
		elif any(page_id == teacher for page_id, _, _ in before):
			notes.append(f"{letter} no (a side step before it)")
		else:
			notes.append(f"{letter} no")
	verdict = "yes" if all(note.endswith("yes") for note in notes) else "no"
	return f"{verdict} ({', '.join(notes)})"


# ---------------------------------------------------------------------------------------------------------------------
# Commands

def run_items(plan):
	plan.items_dir.mkdir(parents=True, exist_ok=True)
	digests = {}
	for name in sorted(plan.inventories):
		(plan.items_dir / f"{name}.tsv").write_bytes(tsv_text(plan.inventories[name]).encode("utf-8"))
		digests[name] = hashlib.sha256(plan.inventory_bytes[name]).hexdigest()
	(plan.items_dir / HASH_FILE).write_bytes(hash_text(digests).encode("utf-8"))
	width = max([len("inventory")] + [len(name) for name in plan.inventories])
	columns = ITEM_TYPES + ["total"]
	print("inventory".ljust(width) + "".join(f"{column:>10}" for column in columns))
	totals = dict.fromkeys(columns, 0)
	for name in sorted(plan.inventories):
		counts = dict.fromkeys(columns, 0)
		for item in plan.inventories[name].items:
			counts[item.type] += 1
			counts["total"] += 1
		for column in columns:
			totals[column] += counts[column]
		print(name.ljust(width) + "".join(f"{counts[column]:>10}" for column in columns))
	print("total".ljust(width) + "".join(f"{totals[column]:>10}" for column in columns))
	excluded = sum(len(inventory.excluded) for inventory in plan.inventories.values())
	print(f"Wrote {len(plan.inventories)} item lists and {HASH_FILE} to {ALLOCATION_DIR}/{ITEMS_DIR}/; "
		f"{excluded} blocks excluded as notes.")
	problems = list(plan.inventory_problems)
	for name in sorted(plan.inventories):
		problems.extend(plan.inventories[name].problems)
	for problem in problems:
		print(problem)
	if problems:
		print(f"{len(problems)} problems", file=sys.stderr)
		return 1
	return 0


def unknown_unit(plan, unit):
	if unit not in plan.units:
		print(f"no unit `{unit}`; the units are {', '.join(plan.units)}", file=sys.stderr)
		return True
	return False


def run_inbox(plan, unit_name):
	if unknown_unit(plan, unit_name):
		return 2
	unit = plan.units[unit_name]
	file = plan.file(unit_name)
	homed = {item.id for row in file.item_rows if row.role == "home" for item in row.items} if file.exists else set()
	refused = set()
	if file.exists:
		for row in file.refused:
			for item in row.items:
				refused.add((item.id, row.passed_by))
	pages = set(unit.pages)
	waiting = {}
	for other in plan.existing_files():
		if other.unit.name == unit_name:
			continue
		for row in other.passed:
			if row.to not in pages:
				continue
			for item in row.items:
				if item.id in homed or (item.id, other.unit.name) in refused:
					continue
				waiting.setdefault(row.to, []).append((item, other.unit.name, row.why, row.where))
	total = sum(len(entries) for entries in waiting.values())
	state = "" if file.exists else f" ({file.name} does not exist yet)"
	print(f"Inbox of `{unit_name}`: {total} items on {len(waiting)} pages{state}")
	for page_id in unit.pages:
		if page_id not in waiting:
			continue
		entries = sorted(waiting[page_id], key=lambda entry: (entry[0].inventory, entry[0].line, entry[1]))
		print(f"`{page_id}` ({len(entries)})")
		for item, passer, why, where in entries:
			print(f"  `{item.id}` {item.type} | {item.label} | passed by `{passer}` ({where}): {why}")
	return 0


def run_demands(plan, unit_name):
	if unknown_unit(plan, unit_name):
		return 2
	unit = plan.units[unit_name]
	pages = set(unit.pages)
	demands = {}
	no_teacher = []
	for file in plan.existing_files():
		for page_id, line, concept, teacher, depth in file.assume_rows:
			entry = (plan.by_id[page_id].index, line, concept, depth, page_id, file.unit.name, f"{file.name}:{line}")
			if teacher == NO_TEACHER:
				no_teacher.append(entry)
			elif teacher in pages and file.unit.name != unit_name:
				demands.setdefault(teacher, []).append(entry)
	total = sum(len(entries) for entries in demands.values())
	print(f"Demands on `{unit_name}`: {total} Assumes rows of other units name its pages")
	for page_id in unit.pages:
		if page_id not in demands:
			continue
		print(f"`{page_id}` ({len(demands[page_id])})")
		for _, _, concept, depth, assuming, owner, where in sorted(demands[page_id]):
			print(f"  {concept} | {depth} | assumed by `{assuming}` (`{owner}`, {where})")
	print(f"No teacher ({len(no_teacher)})")
	for _, _, concept, depth, assuming, owner, where in sorted(no_teacher):
		print(f"  {concept} | {depth} | assumed by `{assuming}` (`{owner}`, {where})")
	return 0


class ExactFinder:
	"""Finds a file of the clone by a path whose every segment matches the name on disk, case included."""

	def __init__(self, root):
		self.root = root
		self.listings = {}

	def names(self, folder):
		if folder not in self.listings:
			try:
				self.listings[folder] = set(os.listdir(folder))
			except OSError:
				self.listings[folder] = None
		return self.listings[folder]

	def find(self, relative):
		current = self.root
		for segment in relative.split("/"):
			names = self.names(current)
			if names is None:
				return None, None
			if segment not in names:
				other = sorted(name for name in names if name.lower() == segment.lower())
				return None, (f"the name on disk is `{other[0]}`" if other else None)
			current = current / segment
		if not current.is_file():
			return None, "it is no file"
		return current, None


def code_rows(plan, unit=None):
	files = [plan.file(unit)] if unit is not None else plan.existing_files()
	rows = []
	for file in files:
		if not file.exists:
			continue
		rows.extend(row for row in file.item_rows if row.role == "home" and row.type == "code")
	return rows


def code_problems(plan, engine, unit=None):
	engine = Path(engine)
	if not engine.is_dir():
		return [f"--engine {engine}: no such folder"], 0
	finder = ExactFinder(engine)
	problems = []
	if unit is not None and not plan.file(unit).exists:
		problems.append(f"{plan.file(unit).name}: file missing")
	rows = code_rows(plan, unit)
	line_counts = {}
	for row in rows:
		message = place_problem(row.text)
		if message:
			problems.append(f"{row.where}: {message}")
			continue
		match = PLACE.match(row.text.strip())
		path, first, last = match.group(1), int(match.group(2)), int(match.group(3))
		found, hint = finder.find(path)
		if found is None:
			problems.append(f"{row.where}: `{path}` does not exist in {engine}" + (f" ({hint})" if hint else ""))
			continue
		if found not in line_counts:
			data = found.read_bytes()
			line_counts[found] = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
		count = line_counts[found]
		if last > count:
			problems.append(f"{row.where}: `{path}:{first}-{last}`: the file has {count} lines")
	return problems, len(rows)


def run_code(plan, engine, unit=None):
	if unit is not None and unknown_unit(plan, unit):
		return 2
	problems, count = code_problems(plan, engine, unit)
	for problem in problems:
		print(problem)
	print(f"{count} places of home rows of type code checked")
	if problems:
		print(f"{len(problems)} problems", file=sys.stderr)
		return 1
	return 0


def check_entries(plan):
	"""The check's name -> the rows of the items that hold it, as (page index, file, line, page id, unit, id, role)."""
	checks = {}
	for file in plan.existing_files():
		for name, number, rows in file.check_items:
			for row in rows:
				checks.setdefault(name, []).append((plan.by_id[row.page].index, file.name, row.line, row.page,
					file.unit.name, f"new:{number}", row.role))
	return checks


def run_checks(plan):
	"""The items that hold a check before writing, by check; nothing at all when there are none."""
	checks = check_entries(plan)
	for name in sorted(checks, key=lambda name: (name.lower(), name)):
		entries = sorted(checks[name])
		pages = len({entry[3] for entry in entries})
		print(f"Check: {name} ({pages} {'page' if pages == 1 else 'pages'})")
		for _, file, line, page_id, unit, item, role in entries:
			print(f"  `{page_id}` (`{unit}`): `{item}` {role}, {file}:{line}")
	return 0


# ---------------------------------------------------------------------------------------------------------------------
# coverage.md

def md_cell(text):
	return one_line(str(text)).replace("|", "\\|")


def sentence(text):
	"""A cell's text as a sentence for coverage.md: on one line, ending with a full stop."""
	text = md_cell(text).rstrip()
	return text if text.endswith((".", "?", "!", "…")) else text + "."


def coverage_text(plan):
	files = {name: plan.file(name) for name in plan.units}
	existing = [file for file in files.values() if file.exists]
	missing = [name for name, file in files.items() if not file.exists]
	homes = homes_by_item(plan)
	passes = passes_by_item(plan)
	nowhere = {item.id for file in existing for row in file.passed if row.to == NOWHERE for item in row.items}
	refusals = {}
	for file in existing:
		for row in file.refused:
			for item in row.items:
				refusals.setdefault(item.id, []).append(row)

	def taken(item_id, row):
		receiver = plan.unit_of(row.to)
		return any(home.file.unit.name == receiver for home in homes.get(item_id, []))

	out = ["# Coverage of the allocation", "",
		"Written by `check_allocation.py coverage` from the units' files, the outline and the inventories. Do not edit it:",
		"run the script again. Pages stand in the outline's order, items in the order of their inventory and line, units",
		"by name.", ""]

	# 1. Summary
	out += ["## 1. Summary", "",
		"With a home: a home row in some unit's file. Nowhere: passed on to `nowhere`. Passed and taken: passed on to a",
		"page and homed by that page's unit. Open: neither a home nor `nowhere`.", "",
		"| Inventory | Owner | Items | With a home | Nowhere | Passed and taken | Open |",
		"| --- | --- | --- | --- | --- | --- | --- |"]
	totals = [0, 0, 0, 0, 0]
	open_items = {}
	for name in sorted(plan.inventories):
		items = plan.inventories[name].items
		with_home = [item for item in items if item.id in homes]
		gone = [item for item in items if item.id in nowhere and item.id not in homes]
		taken_items = [item for item in items if any(row.to != NOWHERE and taken(item.id, row)
			for row in passes.get(item.id, []))]
		open_items[name] = [item for item in items if item.id not in homes and item.id not in nowhere]
		row = [len(items), len(with_home), len(gone), len(taken_items), len(open_items[name])]
		totals = [a + b for a, b in zip(totals, row)]
		owner = plan.owners.get(name)
		out.append(f"| `{name}` | {f'`{owner}`' if owner else '-'} | " + " | ".join(str(value) for value in row) + " |")
	out.append("| all | | " + " | ".join(str(value) for value in totals) + " |")
	out += ["", "Unit files missing: " + (", ".join(f"`{name}`" for name in sorted(missing)) or "none") + ".", ""]

	def state(item):
		notes = []
		for row in passes.get(item.id, []):
			if row.to == NOWHERE:
				continue
			receiver = plan.unit_of(row.to)
			refused = [other for other in refusals.get(item.id, []) if other.file.unit.name == receiver]
			if receiver is None:
				notes.append(f"Passed to `{row.to}` by `{row.file.unit.name}`; the page belongs to no unit.")
			elif refused:
				other = refused[0]
				notes.append(f"Passed to `{row.to}` by `{row.file.unit.name}`, refused by `{receiver}`: "
					f"{sentence(other.why)}" + (f" Better page: `{other.better}`." if other.better else ""))
			elif not files[receiver].exists:
				notes.append(f"Passed to `{row.to}` by `{row.file.unit.name}`; the file of `{receiver}` is missing.")
			else:
				notes.append(f"Passed to `{row.to}` by `{row.file.unit.name}`, not taken yet.")
		if not notes:
			owner = plan.owners.get(item.inventory)
			notes.append(f"Not placed by its owner `{owner}`.")
		return " ".join(notes)

	# 2. Items with no home and no nowhere
	out += ["## 2. Items with no home and no `nowhere`", ""]
	any_open = False
	for name in sorted(plan.inventories):
		items = open_items[name]
		if not items:
			continue
		any_open = True
		owner = plan.owners.get(name)
		out.append(f"### `{name}` ({len(items)})")
		out.append("")
		if owner is not None and not files[owner].exists:
			out.append(f"The owner's file `{files[owner].name}` is missing, so the {len(items)} open items are not listed.")
		else:
			for item in items:
				out.append(f"- `{item.id}` {item.type}: {sentence(item.label)} {state(item)}")
		out.append("")
	if not any_open:
		out += ["none", ""]

	# 3. Items with two or more homes
	out += ["## 3. Items with two or more homes", ""]
	doubles = [item for item in plan.all_items() if len(homes.get(item.id, [])) > 1]
	for item in doubles:
		places = "; ".join(f"`{row.page}` (`{row.file.unit.name}`, {row.where})"
			for row in sorted(homes[item.id], key=lambda row: (row.file.name, row.line)))
		out.append(f"- `{item.id}` {item.type}: {sentence(item.label)} Homes: {places}.")
	out += (["none"] if not doubles else []) + [""]

	# 4. Items passed on that nobody took
	out += ["## 4. Items passed on that nobody took", ""]
	untaken = []
	for item in plan.all_items():
		for row in passes.get(item.id, []):
			if row.to == NOWHERE or taken(item.id, row):
				continue
			receiver = plan.unit_of(row.to)
			refused = [other for other in refusals.get(item.id, []) if other.file.unit.name == receiver]
			if receiver is None:
				note = "The page belongs to no unit."
			elif refused:
				note = (f"Refused by `{receiver}` ({refused[0].where}): {sentence(refused[0].why)}"
					+ (f" Better page: `{refused[0].better}`." if refused[0].better else ""))
			elif not files[receiver].exists:
				note = f"The file of `{receiver}` is missing."
			else:
				note = f"Neither taken nor refused by `{receiver}` yet."
			untaken.append(f"- `{item.id}` {item.type}: {sentence(item.label)} Passed by `{row.file.unit.name}` to "
				f"`{row.to}` ({row.where}): {sentence(row.why)} {note}")
	out += (untaken or ["none"]) + [""]

	# 5. Owner faults
	out += ["## 5. Owner faults", ""]
	twice = []
	unlisted = []
	for name in sorted(plan.inventories):
		owner = plan.owners.get(name)
		if owner is None or not files[owner].exists:
			continue
		file = files[owner]
		counts = {}
		for row in file.item_rows:
			if row.role == "home":
				for item in row.items:
					if item.inventory == name:
						counts.setdefault(item.id, []).append(row.line)
		for row in file.passed:
			for item in row.items:
				counts.setdefault(item.id, []).append(row.line)
		for item in plan.inventories[name].items:
			lines = counts.get(item.id, [])
			if len(lines) > 1:
				twice.append(f"- `{item.id}` {item.type}: {sentence(item.label)} `{owner}` places it {len(lines)} times "
					f"({file.name} lines {', '.join(str(line) for line in sorted(lines))}).")
			elif not lines:
				unlisted.append(f"- `{item.id}` {item.type}: {sentence(item.label)} Not placed by `{owner}`.")
	unowned = []
	for file in sorted(existing, key=lambda file: file.name):
		for row in file.item_rows:
			if row.role != "home":
				continue
			for item in row.items:
				owner = plan.owners.get(item.inventory)
				if owner != file.unit.name and not passed_to_unit(plan, passes, item.id, file.unit.name):
					unowned.append(f"- `{item.id}` {item.type}: {sentence(item.label)} Homed by `{file.unit.name}` on "
						f"`{row.page}` ({row.where}), which neither owns it nor was passed it.")
	missing_owners = sorted({plan.owners[name] for name in plan.owners if not files[plan.owners[name]].exists})
	out += ["### Placed more than once by the owner", ""] + (twice or ["none"]) + [""]
	out += ["### Not placed by the owner", ""] + (unlisted or ["none"]) + [""]
	if missing_owners:
		out += ["Owners whose file is missing are not counted here: " +
			", ".join(f"`{name}`" for name in missing_owners) + ".", ""]
	out += ["### Homes without the right to them", ""] + (unowned or ["none"]) + [""]

	# 6. Assumes
	closures = needs_closures(plan)
	outside = []
	unknown = []
	for file in existing:
		for page_id, line, concept, teacher, depth in file.assume_rows:
			page = plan.by_id[page_id]
			key = (page.index, file.name, line)
			if teacher == NO_TEACHER:
				unknown.append((key, f"| `{page_id}` | {md_cell(concept)} | {depth} | {file.name}:{line} |"))
			elif depth == "must" and teacher not in closures.get(page_id, set()):
				outside.append((key, f"| `{page_id}` | {md_cell(concept)} | `{teacher}` | "
					f"{md_cell(track_note(plan, page, teacher))} | {file.name}:{line} |"))
	out += ["## 6. Assumes", "",
		"### Depth `must`, teacher outside the page's Needs closure", "",
		"The closure: the page's Needs, their Needs and so on, with each such page's \"Needs of the part\"; a Need with",
		"alternatives adds only the pages every alternative leads to. \"Before\" says whether the teacher comes before",
		"the page on every track the page is on.", ""]
	if outside:
		out += ["| Page | Concept | Taught by | Before | Row |", "| --- | --- | --- | --- | --- |"]
		out += [text for _, text in sorted(outside)]
	else:
		out.append("none")
	out += ["", "### No teacher (`?`)", ""]
	if unknown:
		out += ["| Page | Concept | Depth | Row |", "| --- | --- | --- | --- |"]
		out += [text for _, text in sorted(unknown)]
	else:
		out.append("none")
	out.append("")

	# 7. Fit
	out += ["## 7. Fit", "", "### Over or under", ""]
	fits = {}
	home_counts = {}
	for file in existing:
		fits.update(file.fits)
		for row in file.item_rows:
			if row.role == "home" and row.type in TYPES:
				counts = home_counts.setdefault(row.page, dict.fromkeys(TYPES, 0))
				counts[row.type] += 1
	flagged = [page for page in plan.pages if page.id in fits and fits[page.id][0] in ("over", "under")
		and page.kind != REFERENCE_KIND]  # a page of kind R has no size check (rule 6)
	for page in flagged:
		out.append(f"- `{page.id}` ({page.size}): {md_cell(fits[page.id][3])}")
	out += (["none"] if not flagged else []) + [""]
	out += ["### All pages", "", "Words: what the page's Fit line states. The other columns count the page's home rows "
		"per type.", "",
		"| Page | Unit | Size | Words | " + " | ".join(TYPES) + " |",
		"| --- | --- | --- | --- | " + " | ".join("---" for _ in TYPES) + " |"]
	for page in plan.pages:
		unit = plan.unit_of(page.id) or "-"
		written = unit in files and files[unit].exists and page.id in files[unit].page_ids
		words = f"{fits[page.id][1]:,}" if page.id in fits else "-"
		counts = home_counts.get(page.id, dict.fromkeys(TYPES, 0))
		cells = [str(counts[type_]) if written else "-" for type_ in TYPES]
		out.append(f"| `{page.id}` | `{unit}` | {page.size} | {words} | " + " | ".join(cells) + " |")
	out.append("")

	# 8. Questions for the planner
	out += ["## 8. Questions for the planner", ""]
	asked = False
	for name in sorted(files):
		file = files[name]
		if not file.exists or not file.questions:
			continue
		asked = True
		out += [f"### `{name}`", ""]
		out += [f"- {md_cell(text)} ({file.name}:{line})" for line, text in file.questions]
		out.append("")
	if not asked:
		out += ["none", ""]

	# 9. Format problems still open
	out += ["## 9. Format problems still open", "",
		"The problems `check` reports, without the owner faults of sections 2 and 5.", ""]
	problems = sorted(set(run_check(plan, across=False)), key=sort_key_problem)
	out += [f"- {problem}" for problem in problems] or ["none"]
	return "\n".join(out) + "\n"


def run_coverage(plan):
	text = coverage_text(plan)
	plan.allocation.mkdir(parents=True, exist_ok=True)
	(plan.allocation / COVERAGE_FILE).write_bytes(text.encode("utf-8"))
	print(f"Wrote {ALLOCATION_DIR}/{COVERAGE_FILE}")
	return 0


def main(argv=None):
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	common = argparse.ArgumentParser(add_help=False)
	common.add_argument("--plan", default=str(DEFAULT_PLAN), help="the plan folder (default: the folder above this "
		"script)")
	commands = parser.add_subparsers(dest="command", required=True)
	commands.add_parser("items", parents=[common], help="write items/<inventory>.tsv and items/inventories.sha256")
	check = commands.add_parser("check", parents=[common], help="check the units' files; exit 1 on a problem")
	check.add_argument("--unit", help="check only this unit's file")
	inbox = commands.add_parser("inbox", parents=[common], help="the items passed to a unit's pages and not settled")
	inbox.add_argument("unit")
	demands = commands.add_parser("demands", parents=[common], help="what other units assume from a unit's pages")
	demands.add_argument("unit")
	code = commands.add_parser("code", parents=[common], help="check the places of home rows of type code")
	code.add_argument("--engine", required=True, help="the engine's clone at the pin")
	code.add_argument("--unit", help="check only this unit's file")
	commands.add_parser("checks", parents=[common], help="the items that hold a check before writing, by check")
	commands.add_parser("coverage", parents=[common], help="write coverage.md")
	args = parser.parse_args(argv)
	for stream in (sys.stdout, sys.stderr):
		if hasattr(stream, "reconfigure"):
			stream.reconfigure(errors="replace")  # a console that cannot show "→" or "…" gets "?", not a crash

	plan = Plan(Path(args.plan))
	if args.command == "items":
		return run_items(plan)
	if args.command == "check":
		if args.unit is not None and unknown_unit(plan, args.unit):
			return 2
		problems = run_check(plan, args.unit)
		warnings = run_warnings(plan, args.unit)
		for problem in problems:
			print(problem)
		if warnings:
			if problems:
				print()
			print(f"Warnings ({len(warnings)}), which do not fail the check:")
			for warning in warnings:
				print(warning)
		if problems:
			print(f"{len(problems)} problems", file=sys.stderr)
			return 1
		return 0
	if args.command == "inbox":
		return run_inbox(plan, args.unit)
	if args.command == "demands":
		return run_demands(plan, args.unit)
	if args.command == "code":
		return run_code(plan, args.engine, args.unit)
	if args.command == "checks":
		return run_checks(plan)
	return run_coverage(plan)


if __name__ == "__main__":
	sys.exit(main())

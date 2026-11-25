"""Build src/content/glossary.json from the seed, the glossary's own entries and the inventories' terms (rulings-11.md, R51).

Run:
    python -I plan/glossary/merge.py           write src/content/glossary.json and plan/glossary/merge-report.md
    python -I plan/glossary/merge.py --check   write nothing; exit 1 when either file differs from what the merge gives

Standard library only, deterministic: the same inputs give the same two files, byte for byte.

The inputs and who wins (pipelines.md §9; rulings-7.md, R33):

1. The 19 entries src/content/glossary.json held before the merge (KEPT below) win over everything: pages cite their
   ids. The merge keeps their id, term, definition and home, and only adds the names of what joins them as aliases,
   and a use home.
2. The seed, plan/glossary/seed.json, wins over the inventories where they name the same term.
3. The inventories' terms (section 7 of plan/inventory/*.md, the items of type term in plan/allocation/items/*.tsv),
   each with the home that a `home` row of a unit's file gives it (plan/allocation/<unit>.md, a row in a page's
   section). `use` and `link` rows give no home.
4. Last, the terms the clerk admitted from the pages' notes (plan/glossary/admitted.json, the seed's schema;
   plan/notes/README.md): the home page's wording wins (rulings-11.md, R51). An admitted term that names an entry
   (its id or its term) homed on the same page replaces that entry's definition and adds its aliases; one that names
   an entry homed elsewhere is refused and listed; any other is a new entry. Its aliases follow the rules below.

One thing, one entry. Entries join when a term of one is a name (term or alias) of the other, when a name is an avoid
name of an entry of the glossary or the seed, when a unit's row says so ("the same entry as `x:n`", "one glossary entry
with `x:n`", "one entry each with ...", "with the seed's"), and when a `nowhere` row says the item repeats another
("Repeats `x:n`"). The names of what joins become aliases of the entry that wins. An alias is dropped when another entry
holds the name, when it is an avoid name, and when the merge would add it and it is one everyday word of
tools/data/common-words.txt (the lint would mark every everyday use of it); the report lists each.

The home of a joined entry: the winner's when an entry of the glossary or the seed is in it; otherwise the one page the
rows give outside parts make and start (else in make, else in start: a start page beside another home is a first use,
book.md); else the page of the item a row's note names. Otherwise the joined names are parted again by page and by
the notes' joins: parts with different terms become entries of their own, and parts that share a term are one word
with several meanings (rulings-11.md, R53): each part of the book they are homed in gets one entry, "<Word> (<part>)"
with the id <word>-<part>, homed on the first of its pages in the outline's order (the others listed); a word homed in
one part only is one entry without a qualifier. A make page beside a home elsewhere is the entry's use (pipelines.md
§9, rule 2). The winner of an entry without a glossary
or seed entry: the item a row's note names, else the item of the inventory the home page's unit owns, else the first.

How a term line becomes entries: "- **Label**: definition." (also "**Label:** definition" and "**Label** - definition").
The label's names are split at " / ", ", " and " vs ". Several names become several entries when the definition splits
into as many parts, each of two words or more, none naming another of the names: names split at " / " at "; " or
" / ", names split at ", " at ", " or "; ", names split at " vs " at "; ". Otherwise names split at " / " are one entry,
the first its term and the others aliases that join nothing by name (a " / " lists two things as often as two names),
and names split at ", " or " vs " are left out and listed. A row that asks for several entries ("two entries") of an
item that gives one leaves the item out (listed). "; **Other term**: its definition" inside a definition is an entry of
its own. A trailing parenthesis of a name is an alias when it is code (`Name`), the name as one identifier
(EngineModule), an abbreviation whose letters run through the name in order from its first (FK, pch, dB) or the
expansion of a name that abbreviates it (MCP (Model Context Protocol)); it is the term when its last word is the
name's (Module (script module)); it is dropped when it lists examples (a comma or "/" inside); otherwise it qualifies
the name and stays in the term as the source writes it ("Clip (animation)", the form of rulings-10.md's "decomposition
(of a transform)"). A parenthesis inside a name is dropped (listed).

The mechanical changes to a definition, the ones the checks need (tools/pages.py check_glossary and the site's
src/lib/glossary.mjs: one sentence, "." only before a character that is not a space, a final full stop): wrapped lines
joined; "..." written "…"; the abbreviations of style.md §2.2 written out as style.md says ("e.g." -> "for example",
"i.e." -> "that is", "etc." -> "and others", "vs." -> "against", "cf." -> "compare", "approx." -> "about"); a trailing
",", ";" or ":" dropped and a full stop added where it is missing; and, since the site shows a definition as plain
text, its backquotes and bold marks removed (rulings-11.md, R53). Nothing else changes: the first letter keeps its
case. A definition that the checks still refuse is left out and listed.

Splits and joins of single terms that the rulings name are in SPLITS below.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # importing check_outline must not write into plan/

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
ROOT = PLAN.parent
SEED = HERE / "seed.json"
GLOSSARY = ROOT / "src" / "content" / "glossary.json"
REPORT = HERE / "merge-report.md"
ADMITTED = HERE / "admitted.json"
INVENTORY = PLAN / "inventory"
ALLOCATION = PLAN / "allocation"
ITEMS = ALLOCATION / "items"
sys.path.insert(0, str(PLAN))

import check_outline  # noqa: E402  (plan/check_outline.py reads the outline)

KEY_ORDER = ["id", "term", "definition", "home", "use", "aliases", "avoid", "known"]

# Splits and joins that the rulings settle for single items (plan/critique/rulings-10.md; rulings-9.md, R40). Each value
# replaces what the item's line would give: a list of (names, definition part, home or None for the row's home). The
# definition part is the index of the part of the line's definition split at "; " (or at " / " where "; " gives too
# few parts), or None for the whole definition.
SPLITS = {
	# rulings-10.md, "Game view and Scene view": "Game view" is one entry with editor-core:694, homed on
	# editor/play-mode; "Scene view" and "viewport" are homed on editor-ui/scene-view.
	"editor-ui:763": [(["Scene view", "viewport"], 0, "editor-ui/scene-view"), (["Game view"], 1, None)],
	"editor-core:694": [(["Game view"], 0, None), (["Scene view"], 1, "editor-ui/scene-view")],
	# rulings-10.md, the row of probability: "importance sampling" on basics/math-probability, "filtered importance
	# sampling" on indirect/ibl (the row's home).
	"render-indirect:583": [(["Importance sampling"], 0, "basics/math-probability"), (["filtered importance sampling"], 1, None)],
	# rulings-10.md, "Decomposition and the cofactor matrix": one entry, "decomposition (of a transform)".
	"scene-ecs:630": [(["Decomposition (of a transform)"], None, None)],
	# The same: "normal matrix" is an entry of its own beside the cofactor matrix's (render-scene:646), as basics-b homes
	# it (plan/allocation/basics-b.md, the row of render-core:740).
	"render-core:740": [(["Normal matrix"], None, None)],
	# The camera row's first name is the editor camera, which the definition does not define: the four motions are
	# entries of their own (plan/notes/editor/camera-viewport.md, the clerk); "editor camera" is admitted.
	"editor-ui:766": [(["orbit"], 0, None), (["pan"], 1, None), (["dolly"], 2, None), (["fly"], 3, None)],
	# "Sub-scene (additive load)" and "Sub-scene / additive load" name one thing, the sub-scene, which world/sub-scenes
	# defines beside the additive load that makes one (plan/notes/world/sub-scenes.md, the mender): the three lines
	# join the entry "Sub-scene", and the second half of worlds-runtime:527 ("a loaded cell is one") defines nothing.
	"gamedev:648": [(["Sub-scene"], None, None)],
	"scene-ecs:676": [(["Sub-scene"], None, None)],
	"worlds-runtime:527": [(["Sub-scene"], 0, None)],
}

# The entries src/content/glossary.json held before the merge (commit 03dd9d5), which pages cite by id. They are
# written here because the merge writes that file: reading it back would take the merge's own output as input.
KEPT = [
	{"id": "frame", "term": "frame", "definition": "One pass of the engine's loop, which reads input, updates the game and draws one picture.", "home": "core/frame-loop"},
	{"id": "frame-rate", "term": "frame rate", "definition": "How many frames the engine finishes in one second.", "home": "core/frame-loop"},
	{"id": "delta-time", "term": "delta time", "definition": "The time in seconds between the start of the previous frame and the start of this one.", "home": "core/time"},
	{"id": "fixed-step", "term": "fixed step", "definition": "A slice of simulated time that always has the same length (1/60 s unless the project sets another rate), in which physics and fixed-update scripts run.", "home": "core/time", "avoid": ["fixed timestep", "physics tick"]},
	{"id": "accumulator", "term": "accumulator", "definition": "The time the frames have produced that no fixed step has simulated yet.", "home": "core/time"},
	{"id": "time-dilation", "term": "time dilation", "definition": "Letting the simulation run slower than the clock when the fixed steps of a frame take longer to compute than the time they simulate.", "home": "core/time"},
	{"id": "interpolation", "term": "interpolation", "definition": "Drawing what the fixed steps moved between its pose before and its pose after the latest steps, so that motion looks smooth at any frame rate.", "home": "world/interpolation", "aliases": ["state interpolation"]},
	{"id": "step-alpha", "term": "step alpha", "definition": "How far, from 0 to 1, a frame is drawn on the way from the poses before its latest fixed steps to the poses after them.", "home": "world/interpolation"},
	{"id": "drawn-transform", "term": "drawn transform", "definition": "The matrix an entity is drawn with in this frame: its blended pose while it is interpolated, otherwise its world transform.", "home": "world/interpolation"},
	{"id": "entity", "term": "entity", "definition": "A thing in a scene, such as a camera, a light or a crate, made of the components attached to it.", "home": "world/ecs"},
	{"id": "component", "term": "component", "definition": "A piece of data attached to an entity, such as its transform or its mesh, that systems read and write.", "home": "world/ecs"},
	{"id": "scene", "term": "scene", "definition": "The entities of one level or screen of a game with their components, saved as one document.", "home": "make/scenes-entities"},
	{"id": "script-class", "term": "script class", "definition": "A C++ class derived from Script that holds the game logic of the entities it is attached to.", "home": "make/first-script"},
	{"id": "script-module", "term": "script module", "definition": "The shared library a project's script classes are compiled into, which the editor and the exported game load.", "home": "make/first-script"},
	{"id": "script-field", "term": "script field", "definition": "A public data member of a script class, registered with ST_SCRIPT_FIELD, that the inspector shows and every entity stores with its own value.", "home": "make/first-script"},
	{"id": "hot-reload", "term": "hot reload", "definition": "Building the script module again while the game plays and loading it in place, so that every script keeps the values of its fields.", "home": "make/first-script"},
	{"id": "cmake-preset", "term": "CMake preset", "definition": "A named set of build options in CMakePresets.json, such as windows or linux, that configures a build with one command.", "home": "start/install"},
	{"id": "submodule", "term": "submodule", "definition": "A Git repository that another repository includes at a pinned commit, as Strata includes its third-party libraries.", "home": "start/install"},
	{"id": "vulkan", "term": "Vulkan", "definition": "The graphics programming interface Strata draws through, by way of the NVRHI library.", "home": "gpu/vulkan-nvrhi"},
]

ABBREVIATIONS = [(r"\be\.g\.", "for example"), (r"\bi\.e\.", "that is"), (r"\betc\.", "and others"), (r"\bvs\.", "against"),
	(r"\bcf\.", "compare"), (r"\bapprox\.", "about")]
# The site's one-sentence test (src/lib/glossary.mjs) and tools/pages.py's.
SITE_SENTENCE = re.compile(r"^[^.!?]+(\.[^\s.!?][^.!?]*)*[.]$")
PAGES_TWO_SENTENCES = re.compile(r"[.?!]\s+[A-Z0-9]")
ITEM_ID = re.compile(r"`([a-z][a-z0-9-]*):(\d+)(?:-(\d+))?`")
PAGE_SECTION = re.compile(r"^## `([^`]+)`")
COUNT_WORDS = r"(?:two|three|four|five|six)"
# Where a definition may split, for each way the label's names are split: names split at " / " take parts split at
# "; " or " / ", names split at ", " parts split at ", " or "; ", names split at " vs " parts split at "; " only (a " vs "
# inside a definition contrasts words, "excluding vs including", and leaves fragments).
DEFINITION_SEPARATORS = {frozenset([" / "]): ("; ", " / "), frozenset([", "]): (", ", "; "), frozenset([" vs "]): ("; ",)}
COMMON_WORDS = ROOT / "tools" / "data" / "common-words.txt"


def read_common():
	"""Every word of tools/data/common-words.txt (the lint's list of everyday words), lowercase."""
	words = set()
	for line in COMMON_WORDS.read_text(encoding="utf-8").split("\n"):
		if line.strip() and not line.startswith("#"):
			words.update(word.lower() for word in line.split())
	return words


COMMON = read_common()


def glossary_id(term):
	"""tools/pages.py glossary_id: the term in lowercase words joined by "-", apostrophes dropped."""
	return re.sub(r"[^a-z0-9]+", "-", term.lower().replace("'", "").replace("’", "")).strip("-")


def key(name):
	return name.strip().lower()


def split_top(text, separator):
	"""Split text at separator where it stands outside parentheses and backquotes."""
	parts = []
	depth = 0
	code = False
	start = 0
	index = 0
	while index < len(text):
		char = text[index]
		if char == "`":
			code = not code
		elif not code and char == "(":
			depth += 1
		elif not code and char == ")":
			depth = max(0, depth - 1)
		elif not code and depth == 0 and text.startswith(separator, index):
			parts.append(text[start:index])
			index += len(separator)
			start = index
			continue
		index += 1
	parts.append(text[start:])
	return [part.strip() for part in parts]


# The inputs.

class Candidate:
	"""One entry an inventory's term line gives."""

	def __init__(self, item, index, names, definition):
		self.item = item  # "<inventory>:<line>"
		self.index = index  # the entry's place among the entries of its item
		self.names = names  # term first, then aliases
		self.definition = definition
		self.home = None
		self.row = None  # (unit, page, note) of the home row
		self.home_override = None
		self.source = "inventory"
		self.loose = set()  # the lowercase names that came as " / " names of one entry: they join nothing by name
		self.seed_note = False  # a row's note joins the item to "the seed's" entry: its loose names may join the seed

	@property
	def term(self):
		return self.names[0]

	def sort_key(self):
		inventory, line = self.item.split(":")
		return (inventory, int(line), self.index)


class Fixed:
	"""An entry of the glossary or of the seed."""

	def __init__(self, source, entry):
		self.source = source  # "glossary" or "seed"
		self.entry = entry
		self.names = [entry["term"]] + list(entry.get("aliases") or [])
		self.home = entry["home"]
		self.loose = set()
		self.seed_note = False

	@property
	def term(self):
		return self.entry["term"]


def read_items():
	"""Every item of type term: id -> (inventory, line)."""
	terms = {}
	for path in sorted(ITEMS.glob("*.tsv")):
		for line in path.read_text(encoding="utf-8").splitlines()[1:]:
			cells = line.split("\t")
			if len(cells) >= 2 and cells[1] == "term":
				terms[cells[0]] = cells
	return terms


def read_term_lines(items):
	"""Each term item's whole line, its wrapped lines joined with one space."""
	texts = {}
	files = {}
	for item in items:
		inventory, line = item.split(":")
		if inventory not in files:
			files[inventory] = (INVENTORY / (inventory + ".md")).read_text(encoding="utf-8").split("\n")
		lines = files[inventory]
		number = int(line)
		text = lines[number - 1].strip()
		following = number
		while following < len(lines) and lines[following].startswith((" ", "\t")) and lines[following].strip() and \
				not lines[following].lstrip().startswith("- "):
			text += " " + lines[following].strip()
			following += 1
		texts[item] = text
	return texts


def read_owners():
	"""Unit -> the inventory it owns (plan/allocation/README.md's table of units)."""
	owners = {}
	for line in (ALLOCATION / "README.md").read_text(encoding="utf-8").split("\n"):
		match = re.match(r"^\| `([a-z0-9-]+)` \| .+ \| `([a-z0-9-]+)` \|$", line)
		if match:
			owners[match.group(1)] = match.group(2)
	return owners


def expand_ids(cell, items):
	ids = []
	for inventory, first, last in ITEM_ID.findall(cell):
		first = int(first)
		last = int(last) if last else first
		for number in range(first, last + 1):
			item = "%s:%d" % (inventory, number)
			if item in items:
				ids.append(item)
	return ids


def read_rows(items):
	"""The units' rows that place term items: (unit, page or None, role or "To" cell, item ids, note, file:line)."""
	rows = []
	for path in sorted(ALLOCATION.glob("*.md")):
		unit = path.stem
		if unit in ("README", "coverage", "completeness"):
			continue
		page = None
		for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), start=1):
			match = PAGE_SECTION.match(line)
			if match:
				page = match.group(1)
				continue
			if line.startswith("## "):
				page = None
				continue
			if not line.startswith("| `"):
				continue
			cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
			if len(cells) < 4:
				continue
			ids = expand_ids(cells[0], items)
			if ids:
				rows.append((unit, page, cells[2], ids, "|".join(cells[3:]), "%s.md:%d" % (unit, number)))
	return rows


# A term line's entries.

def clean_definition(text, changes):
	"""The mechanical changes the checks need; each kind of change is counted in changes."""
	result = text.strip()
	if "..." in result:
		result = result.replace("...", "…")
		changes['"..." written "…"'] = changes.get('"..." written "…"', 0) + 1
	for pattern, words in ABBREVIATIONS:
		if re.search(pattern, result):
			result = re.sub(pattern, words, result)
			label = 'abbreviation written out ("%s")' % words
			changes[label] = changes.get(label, 0) + 1
	stripped = result.rstrip(" ,;:")
	if not stripped.endswith("."):
		changes["full stop added"] = changes.get("full stop added", 0) + 1
		stripped += "."
	return stripped


def refusal(definition):
	"""Why the checks refuse a definition, or None."""
	if not definition.strip():
		return "empty"
	if PAGES_TWO_SENTENCES.search(definition):
		return "more than one sentence (tools/pages.py)"
	if not SITE_SENTENCE.match(definition):
		return 'not one sentence by the site\'s test (no "?" or "!", a "." only before a character that is not a space)'
	return None


def crossed(names, pieces):
	"""A part of a split definition names another of the names (a word list's word does not count): the parts do not
	stand for the names in order ("Exposure / EV / stop: a factor of light scaling; one stop doubles it; EV is log2")."""
	for index, piece in enumerate(pieces):
		for other, name in enumerate(names):
			head = re.sub(r"\s*\([^()]*\)", "", name).strip().lower()
			if other == index or not head or head in COMMON:
				continue
			if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(head), piece.lower()):
				return True
	return False


def parse_line(text):
	"""(label, definition) of a term line, or None."""
	match = re.match(r"^(?:- |\d+\. )\*\*(.+?)\*\*(.*)$", text)
	if not match:
		return None
	label, rest = match.group(1), match.group(2)
	if label.endswith(":"):
		return label[:-1].strip(), rest.strip()
	tail = re.match(r"^(.*?)(?::\s+| - | — | – )(.*)$", rest)
	if not tail:
		return None
	return (label + tail.group(1)).strip(), tail.group(2).strip()


def is_abbreviation(short, name):
	"""short abbreviates name: its letters in order through name from name's first letter ("FK", "pch", "dB"), or it is
	the name written as one identifier ("EngineModule")."""
	if " " in short or len(short) < 2:
		return False
	if re.sub(r"[^a-z0-9]", "", short.lower()) == re.sub(r"[^a-z0-9]", "", name.lower()):
		return True
	letters = [char for char in short.lower() if char.isalpha()]
	text = name.lower()
	if not letters or not text or letters[0] != text[0] or len(letters) >= len(text.replace(" ", "")):
		return False
	position = 0
	for char in letters:
		position = text.find(char, position)
		if position < 0:
			return False
		position += 1
	return True


def parse_name(name, notes):
	"""The names one label name gives: [term, aliases...]."""
	name = name.strip()
	inner = re.match(r"^(.*\S) \(([^()]+)\) (\S.*)$", name)
	if inner:
		notes.append('"%s": the parenthesis inside the name is dropped' % name)
		name = inner.group(1) + " " + inner.group(3)
	match = re.match(r"^(.*\S) \(([^()]+)\)$", name)
	if not match:
		return [name]
	head, inside = match.group(1).strip(), match.group(2).strip()
	code = re.fullmatch(r"`([^`]+)`", inside)
	if code:
		return [head, code.group(1)]
	if "," in inside or "/" in inside:
		return [head]
	head_words = head.lower().split()
	inside_words = inside.lower().split()
	if len(inside_words) > 1 and inside_words[-1] == head_words[-1]:
		return [inside]
	if is_abbreviation(inside, head):
		return [head, inside]
	if " " not in head and " " in inside and is_abbreviation(head, inside):
		return [head, inside]
	return [name]


def entries_of_line(item, text, changes, problems):
	"""The candidates a term line gives; problems collects what is left out."""
	parsed = parse_line(text)
	if parsed is None:
		problems.append(("unreadable", item, text[:80], "the line is not \"- **Term**: definition\""))
		return []
	label, definition = parsed
	others = []
	parts = split_top(definition, "; ")
	kept = []
	for part in parts:
		match = re.match(r"^\*\*([^*]+)\*\*(?::\s*| - )(.+)$", part)
		if match and kept:
			others.append((match.group(1).strip(), match.group(2).strip()))
		else:
			kept.append(part)
	definition = "; ".join(kept)
	notes = []
	result = []
	if item in SPLITS:
		pieces = split_top(definition, "; ")
		if len(pieces) < len(SPLITS[item]):
			pieces = split_top(definition, " / ")
		for index, (names, part, home) in enumerate(SPLITS[item]):
			words = definition if part is None else pieces[part]
			candidate = Candidate(item, index, list(names), clean_definition(words, changes))
			candidate.home_override = home
			result.append(candidate)
	else:
		groups = []
		kinds = set()
		for separator in (" / ", ", ", " vs "):
			if separator in label and len(split_top(label, separator)) > 1:
				kinds.add(separator)
		names = [label]
		for separator in (" / ", ", ", " vs "):
			names = [piece for name in names for piece in split_top(name, separator)]
		names = [name for name in names if name]
		if len(names) == 1:
			groups = [(parse_name(names[0], notes), definition, set())]
		else:
			split = None
			for separator in DEFINITION_SEPARATORS.get(frozenset(kinds), ("; ",)):
				pieces = split_top(definition, separator)
				if len(pieces) == len(names) and all(len(piece.split()) >= 2 for piece in pieces) and \
						not crossed(names, pieces):
					split = pieces
					break
			if split:
				groups = [(parse_name(name, notes), piece, set()) for name, piece in zip(names, split)]
			elif kinds == {" / "}:
				merged = []
				loose = set()
				for position, name in enumerate(names):
					parsed = parse_name(name, notes)
					merged.extend(parsed)
					if position:
						loose.update(key(piece) for piece in parsed)
				groups = [(merged, definition, loose)]
			else:
				problems.append(("one definition for several things", item, label,
					"%d names split at \", \" or \" vs \" share one definition" % len(names)))
				return []
		for index, (names, words, loose) in enumerate(groups):
			candidate = Candidate(item, index, names, clean_definition(words, changes))
			candidate.loose = loose
			result.append(candidate)
	for index, (name, words) in enumerate(others, start=len(result)):
		result.append(Candidate(item, index, parse_name(name, notes), clean_definition(words, changes)))
	for note in notes:
		problems.append(("parenthesis dropped", item, label, note))
	return result


# The merge.

class Groups:
	"""Union-find over the entries; a group holds at most one entry of the glossary and one of the seed."""

	def __init__(self, members):
		self.parent = list(range(len(members)))
		self.members = members

	def find(self, index):
		while self.parent[index] != index:
			self.parent[index] = self.parent[self.parent[index]]
			index = self.parent[index]
		return index

	def fixed(self, root):
		return [member.source for index, member in enumerate(self.members) if self.find(index) == root and member.source != "inventory"]

	def union(self, first, second):
		a, b = self.find(first), self.find(second)
		if a == b:
			return True
		sources = self.fixed(a) + self.fixed(b)
		if len(sources) != len(set(sources)):
			return False
		self.parent[max(a, b)] = min(a, b)
		return True


def note_targets(note, items):
	"""The items a row's note joins its items to, with "each", "first term" or "second term" read from it."""
	match = re.search(r"(same entr(?:y|ies) as|one (?:glossary )?entry(?: each)? with|one entry with|Repeats?)", note)
	if not match:
		return None
	tail = note[match.start():]
	tail = tail.split(";")[0]
	ids = expand_ids(tail, items)
	each = "each" in match.group(1) or "same entries" in match.group(1) or match.group(1).startswith("Repeat")
	which = None
	term = re.search(r"`[a-z-]+:\d+`'s (first|second) term|the (first|second) term of `", tail)
	if term:
		which = 1 if "second" in term.group(0) else 0
	return ids, each, which


def merge():
	outline = check_outline.Outline()
	check_outline.read_outline(outline)
	order = {page.id: index for index, page in enumerate(outline.pages)}
	glossary = [dict(entry) for entry in KEPT]
	seed = json.loads(SEED.read_text(encoding="utf-8"))["terms"]
	items = read_items()
	texts = read_term_lines(items)
	rows = read_rows(items)
	owners = read_owners()
	changes = {}
	problems = []  # (reason, item, label, detail)
	info = {"seed": [], "notes": [], "uses": [], "aliases dropped": [], "ids": [], "everyday": [], "meanings": [], "admitted": []}

	members = [Fixed("glossary", entry) for entry in glossary] + [Fixed("seed", entry) for entry in seed]
	candidates = {}
	for item in sorted(items, key=lambda value: (value.split(":")[0], int(value.split(":")[1]))):
		candidates[item] = entries_of_line(item, texts[item], changes, problems)

	# Homes from the rows of the pages' sections.
	homes = {}
	asks = {}
	joins = []
	seed_notes = set()
	for unit, page, role, ids, note, where in rows:
		if page is not None and role == "home":
			for item in ids:
				homes.setdefault(item, []).append((unit, page, note, where))
			count = re.search(r"\b(%s) (?:glossary )?entries\b" % COUNT_WORDS, note, re.IGNORECASE)
			if count and len(ids) == 1 and not re.search(r"same entries|one (?:glossary )?entry each", note):
				asks[ids[0]] = count.group(1).lower()
		if page is not None and role == "home" and "the seed's" in note:
			seed_notes.update(ids)
		targets = note_targets(note, items)
		if targets and (page is not None and role == "home" or page is None and "nowhere" in role):
			joins.append((ids, targets, where))
	for item, placed in homes.items():
		if len(placed) > 1:
			pages = sorted({page for _, page, _, _ in placed})
			problems.append(("two home rows", item, candidates[item][0].term if candidates.get(item) else item,
				"homed by %s" % ", ".join(where for _, _, _, where in placed)))
			if len(pages) > 1:
				candidates[item] = []
				continue
		unit, page, note, where = placed[0]
		for candidate in candidates.get(item, []):
			candidate.home = candidate.home_override or page
			candidate.row = (unit, page, note, where)
	numbers = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
	for item, word in sorted(asks.items()):
		made = candidates.get(item, [])
		if made and len(made) < numbers[word] and len(made[0].names) > 1:
			problems.append(("row asks for more entries", item, " / ".join(made[0].names),
				"the row asks for %s entries; the line gives one definition for its names" % word))
			candidates[item] = []

	for item in seed_notes:
		for candidate in candidates.get(item, []):
			candidate.seed_note = True
	start = len(members)
	positions = {}
	for item in sorted(candidates, key=lambda value: (value.split(":")[0], int(value.split(":")[1]))):
		for candidate in candidates[item]:
			positions[(item, candidate.index)] = len(members)
			members.append(candidate)
	groups = Groups(members)
	conflicts = []

	# Joins the rows' notes state: an entry of the item joins the entry of the named item that shares a name with it,
	# else the item's first entry joins the named item's first (or the named "second term").
	targeted = set()
	note_pairs = []
	for ids, (targets, each, which), where in joins:
		targets = [target for target in targets if target not in ids]
		if not targets:
			continue
		pairs = list(zip(ids, targets)) if each and len(targets) == len(ids) else [(item, targets[0]) for item in ids]
		for source, target in pairs:
			if not candidates.get(source) or not candidates.get(target):
				continue
			chosen = [(one, other) for one in candidates[source] for other in candidates[target]
				if {key(name) for name in one.names} & {key(name) for name in other.names}]
			if not chosen or which is not None:
				target_index = which if which is not None and which < len(candidates[target]) else 0
				chosen = [(candidates[source][0], candidates[target][target_index])]
			for one, other in chosen:
				first = positions[(source, one.index)]
				second = positions[(target, other.index)]
				if groups.union(first, second):
					targeted.add(second)
					note_pairs.append((first, second))
					info["notes"].append("%s joins %s (%s)" % (source, target, where))
				else:
					conflicts.append((source, target, where))

	# Joins by name: a member's term is a name of another member, or a name is another member's avoid name.
	by_name = {}
	for index, member in enumerate(members):
		for position, name in enumerate(member.names):
			by_name.setdefault(key(name), []).append((index, position))
	avoid_of = {}
	for index, member in enumerate(members[:start]):
		for name in member.entry.get("avoid") or []:
			avoid_of.setdefault(key(name), []).append(index)
	for index, member in enumerate(members):
		if member.source == "seed":
			continue
		for position, name in enumerate(member.names):
			for other, other_position in by_name.get(key(name), []):
				if member.source == "glossary" and members[other].source != "seed":
					continue
				lowered = key(name)
				if lowered in member.loose and not (member.seed_note and members[other].source == "seed"):
					continue
				if lowered in members[other].loose and not (members[other].seed_note and member.source == "seed"):
					continue
				if other != index and (position == 0 or other_position == 0):
					if not groups.union(index, other):
						conflicts.append((getattr(member, "item", member.source), members[other].term, "name \"%s\"" % name))
			for other in avoid_of.get(key(name), []) if member.source == "inventory" else []:
				if not groups.union(index, other):
					conflicts.append((member.item, members[other].term, "avoid name \"%s\"" % name))
	for source, target, where in conflicts:
		problems.append(("names two entries", source, target, "joining would put two entries of the glossary or the seed in one: %s" % where))

	# Resolve each group.
	def part_of(page):
		return page.split("/")[0]

	def home_of(homed, indices):
		"""The home the members' rows give: a page outside parts make and start first, then make, then start."""
		outside = sorted({member.home for member in homed if part_of(member.home) not in ("make", "start")})
		inside = sorted({member.home for member in homed if part_of(member.home) == "make"})
		first = sorted({member.home for member in homed if part_of(member.home) == "start"})
		pages = outside or inside or first
		if len(pages) == 1:
			return pages[0], pages
		noted = sorted({members[index].home for index in indices if index in targeted and members[index].home in pages})
		if len(noted) == 1:
			named = [members[index] for index in indices if index in targeted and members[index].home == noted[0]]
			info["notes"].append('"%s": homed on %s, the page of the item the rows name; also homed on %s' % (
				named[0].term, noted[0], ", ".join(page for page in pages if page != noted[0])))
			return noted[0], pages
		return None, pages

	def make_entry(indices, home, fixed):
		group = [members[index] for index in indices]
		inventory = [member for member in group if member.source == "inventory"]
		homed = [member for member in inventory if member.home]
		use = None
		if fixed:
			winner = fixed[0]
		else:
			noted = [members[index] for index in indices if index in targeted and members[index].home == home]
			owned = [member for member in homed if member.home == home and member.row and
				owners.get(member.row[0]) == member.item.split(":")[0]]
			winner = (noted or owned or sorted([member for member in homed if member.home == home], key=Candidate.sort_key))[0]
		for member in homed:
			if part_of(member.home) == "start" and part_of(home) != "start":
				info["uses"].append('"%s": %s homes it on %s, a first use (book.md): the home is %s' % (
					winner.term, member.item, member.home, home))
		if part_of(home) != "make" and not (fixed and fixed[0].entry.get("use")):
			makes = sorted({member.home for member in homed if part_of(member.home) == "make"})
			if len(makes) == 1:
				use = makes[0]
				info["uses"].append('"%s": home %s, use %s' % (winner.term, home, use))
			elif len(makes) > 1:
				info["uses"].append('"%s": home %s, rows on %s: no use set' % (winner.term, home, ", ".join(makes)))
		if fixed:
			entry = dict(winner.entry)
			if use and not entry.get("use"):
				entry["use"] = use
			for member in homed:
				if member.home != home and part_of(member.home) != "make":
					info["seed"].append('%s "%s" (row home %s) keeps the %s\'s home %s' % (
						member.item, member.term, member.home, winner.source, home))
		else:
			entry = {"term": winner.term, "definition": winner.definition, "home": home, "aliases": list(winner.names[1:])}
			if use:
				entry["use"] = use
		entry["aliases"] = list(entry.get("aliases") or [])
		entry["_own"] = {key(name) for name in winner.entry.get("aliases") or []} if fixed else set()
		avoid = list(entry.get("avoid") or [])
		for member in fixed[1:]:
			avoid.extend(member.entry.get("avoid") or [])
		entry["avoid"] = avoid
		entry["_extra"] = [name for member in group if member is not winner for name in member.names]
		entry["_source"] = winner.source
		entry["_items"] = sorted({member.item for member in inventory}, key=lambda value: (value.split(":")[0], int(value.split(":")[1])))
		return entry

	clusters = {}
	for index in range(len(members)):
		clusters.setdefault(groups.find(index), []).append(index)
	entries = []
	for root in sorted(clusters):
		indices = clusters[root]
		fixed = [members[index] for index in indices if members[index].source == "glossary"] + \
			[members[index] for index in indices if members[index].source == "seed"]
		if len(fixed) > 1:
			info["seed"].append('"%s" of the seed joins the glossary\'s "%s"' % (fixed[1].term, fixed[0].term))
		if fixed:
			entries.append(make_entry(indices, fixed[0].home, fixed))
			continue
		homed = [members[index] for index in indices if members[index].home]
		if not homed:
			for index in indices:
				problems.append(("no home row", members[index].item, members[index].term, "no unit's page homes the item or what it joins"))
			continue
		home, pages = home_of(homed, indices)
		if home:
			entries.append(make_entry(indices, home, []))
			continue
		# The names joined entries of several pages: part them again, by the rows' notes and by page alone.
		parts = Groups([members[index] for index in indices])
		place = {index: position for position, index in enumerate(indices)}
		for first, second in note_pairs:
			if first in place and second in place:
				parts.union(place[first], place[second])
		by_page = {}
		for index in indices:
			if members[index].home:
				by_page.setdefault(members[index].home, []).append(index)
		for same in by_page.values():
			for index in same[1:]:
				parts.union(place[same[0]], place[index])
		pieces = {}
		for index in indices:
			pieces.setdefault(parts.find(place[index]), []).append(index)
		made = []
		for piece in sorted(pieces.values()):
			piece_homed = [members[index] for index in piece if members[index].home]
			if not piece_homed:
				continue
			piece_home, piece_pages = home_of(piece_homed, piece)
			if piece_home is None:
				for member in piece_homed:
					problems.append(("two homes", member.item, member.term, "homes %s" % ", ".join(piece_pages)))
				continue
			made.append(make_entry(piece, piece_home, []))
		terms = {}
		for entry in made:
			terms.setdefault(key(entry["term"]), []).append(entry)
		for same in terms.values():
			if len(same) == 1:
				entries.append(same[0])
				continue
			entries.extend(qualify(same, order, info))

	# Ids and names: the glossary's entries first, then the seed's, then the inventories' in their order.
	plain_definitions(entries, changes)
	rank = {"glossary": 0, "seed": 1, "inventory": 2}
	entries.sort(key=lambda entry: (rank[entry["_source"]], [(item.split(":")[0], int(item.split(":")[1])) for item in entry["_items"][:1]]))
	taken_ids = {}
	kept = []
	for entry in entries:
		identifier = glossary_id(entry["term"])
		if not identifier:
			problems.append(("no id", ", ".join(entry["_items"]) or entry["_source"], entry["term"],
				"the term has no letter or digit, so its id would be empty"))
			continue
		if entry["_source"] == "seed" and entry.get("id") != identifier:
			info["ids"].append('"%s": the seed\'s id %s becomes %s' % (entry["term"], entry.get("id"), identifier))
		if identifier in taken_ids:
			problems.append(("id collides", ", ".join(entry["_items"]) or entry["_source"], entry["term"],
				'the id "%s" is the id of "%s"' % (identifier, taken_ids[identifier])))
			continue
		taken_ids[identifier] = entry["term"]
		entry["id"] = identifier
		kept.append(entry)
	avoided = {key(name) for entry in kept for name in entry["avoid"]}
	owners_of = {}
	for entry in kept:
		owners_of.setdefault(key(entry["term"]), entry)
	final = []
	for entry in kept:
		if key(entry["term"]) in avoided or owners_of[key(entry["term"])] is not entry:
			problems.append(("name taken", ", ".join(entry["_items"]) or entry["_source"], entry["term"],
				"the term is a name of \"%s\" or an avoid name" % owners_of[key(entry["term"])]["term"]))
			continue
		final.append(entry)
	names_of = {key(entry["term"]): entry for entry in final}
	for entry in final:
		aliases = []
		for name in entry["aliases"] + entry["_extra"]:
			name = name.strip()
			lowered = key(name)
			if not name or lowered in (key(entry["term"]), entry.get("_word")) or any(key(alias) == lowered for alias in aliases):
				continue
			if lowered not in entry["_own"] and " " not in lowered and lowered in COMMON:
				info["everyday"].append('"%s" of "%s"' % (name, entry["term"]))
				continue
			if lowered in avoided or (lowered in names_of and names_of[lowered] is not entry):
				if name in entry["aliases"]:
					info["aliases dropped"].append('"%s" of "%s": a name of "%s" or an avoid name' % (
						name, entry["term"], names_of[lowered]["term"] if lowered in names_of else name))
				continue
			names_of[lowered] = entry
			aliases.append(name)
		entry["aliases"] = aliases

	for entry in final:
		reason = refusal(entry["definition"])
		if reason:
			problems.append(("definition refused", ", ".join(entry["_items"]) or entry["_source"], entry["term"],
				"%s: %s" % (reason, entry["definition"])))
		if entry["home"] not in order:
			problems.append(("home not in the outline", ", ".join(entry["_items"]) or entry["_source"], entry["term"], entry["home"]))
	final = [entry for entry in final if not refusal(entry["definition"]) and entry["home"] in order]
	admit(final, order, problems, changes, info)
	final.sort(key=lambda entry: (order[entry["home"]], entry["term"].lower(), entry["term"]))
	return final, problems, changes, info, len(glossary), len(seed), len(items), sum(len(value) for value in candidates.values())


def admit(final, order, problems, changes, info):
	"""The clerk's admitted terms (plan/glossary/admitted.json), applied to the merged entries in the file's order."""
	if not ADMITTED.is_file():
		return
	requests = json.loads(ADMITTED.read_text(encoding="utf-8"))["terms"]
	for request in requests:
		term = request["term"].strip()
		identifier = request.get("id") or glossary_id(term)
		home = request["home"]
		where = "admitted.json"
		definition = clean_definition(request["definition"], changes)
		for mark in ("`", "**"):
			definition = definition.replace(mark, "")
		reason = refusal(definition)
		if reason:
			problems.append(("admitted term refused", where, term, "%s: %s" % (reason, definition)))
			continue
		if home not in order:
			problems.append(("admitted term refused", where, term, "the home %s is no page of the outline" % home))
			continue
		if identifier != glossary_id(term):
			problems.append(("admitted term refused", where, term, 'the id "%s" is not the term\'s id "%s"' % (identifier, glossary_id(term))))
			continue
		owner = next((entry for entry in final if entry["id"] == identifier or key(entry["term"]) == key(term)), None)
		if owner is None:
			holder = next((entry for entry in final if key(term) in (key(alias) for alias in entry["aliases"])), None)
			if holder is not None:
				problems.append(("admitted term refused", where, term, 'the term is an alias of "%s" (home %s)' % (holder["term"], holder["home"])))
				continue
		elif owner["home"] != home:
			problems.append(("admitted term refused", where, term, '"%s" is homed on %s, not on %s: only its home page words it' % (
				owner["term"], owner["home"], home)))
			continue
		if owner is None:
			owner = {"id": identifier, "term": term, "definition": definition, "home": home, "aliases": [],
				"avoid": list(request.get("avoid", [])), "_source": "admitted", "_items": [], "_extra": [], "_own": set()}
			final.append(owner)
			info["admitted"].append('"%s" (%s): a new entry, homed on %s' % (term, identifier, home))
		elif owner["definition"] != definition:
			owner["definition"] = definition
			info["admitted"].append('"%s" (%s): the definition of its home page, %s' % (owner["term"], owner["id"], home))
		names = {}
		for entry in final:
			for name in [entry["term"]] + entry["aliases"]:
				names.setdefault(key(name), entry)
		avoided = {key(name) for entry in final for name in entry["avoid"]}
		for alias in request.get("aliases", []):
			lowered = key(alias)
			if lowered in names and names[lowered] is owner:
				continue
			if " " not in lowered and lowered in COMMON:
				info["everyday"].append('"%s" of "%s"' % (alias, owner["term"]))
				continue
			if lowered in names or lowered in avoided:
				info["aliases dropped"].append('"%s" of "%s": a name of "%s" or an avoid name' % (
					alias, owner["term"], names[lowered]["term"] if lowered in names else alias))
				continue
			owner["aliases"].append(alias)
			names[lowered] = owner
			info["admitted"].append('"%s": the alias "%s" its home page asked for' % (owner["term"], alias))


def qualify(same, order, info):
	"""The entries of one word with several meanings (rulings-11.md, R53): one per part of the book, "<Word> (<part>)",
	homed on the first page of the part in the outline's order; the other pages' rows of that part join it. A word of one
	part only keeps its term."""
	by_part = {}
	for entry in sorted(same, key=lambda entry: order.get(entry["home"], len(order))):
		by_part.setdefault(entry["home"].split("/")[0], []).append(entry)
	result = []
	for part, group in by_part.items():
		entry = group[0]
		for other in group[1:]:
			entry["_extra"] += other["aliases"] + other["_extra"]
			entry["_items"] = sorted(set(entry["_items"]) | set(other["_items"]), key=lambda value: (value.split(":")[0], int(value.split(":")[1])))
			info["meanings"].append('"%s": homed on %s, the first page of part %s that homes it; also homed on %s' % (
				entry["term"], entry["home"], part, other["home"]))
		if len(by_part) > 1:
			term = entry["term"]
			entry["term"] = "%s (%s)" % (term, part)
			entry["_qualified"] = True
			entry["_word"] = key(term)
			info["meanings"].append('"%s": homed on %s; "%s" is also homed in %s' % (
				entry["term"], entry["home"], term, ", ".join("part %s" % other for other in by_part if other != part)))
		result.append(entry)
	return result


def plain_definitions(entries, changes):
	"""Backquotes and bold marks removed from every definition: the site shows it as plain text (rulings-11.md, R53)."""
	for entry in entries:
		definition = entry["definition"]
		for mark, label in (("`", "backquotes removed"), ("**", "bold marks removed")):
			if mark in definition:
				definition = definition.replace(mark, "")
				changes[label] = changes.get(label, 0) + 1
		entry["definition"] = definition


def output(entry):
	result = {}
	for name in KEY_ORDER:
		if name in entry and entry[name] not in (None, []):
			result[name] = entry[name]
	return result


def glossary_text(entries):
	return json.dumps({"terms": [output(entry) for entry in entries]}, indent="\t", ensure_ascii=False) + "\n"


REASONS = [
	("no home row", "No unit's page homes the item, and it joins no entry that has a home."),
	("two homes", "Rows on different pages home one entry's names, and no row's note says which page is its home."),
	("two home rows", "The item has home rows on two pages."),
	("row asks for more entries", "A row asks for several entries, and the item's line gives one definition for its names."),
	("one definition for several things", "The label names several things (split at \", \" or \" vs \") and the definition does not split into a part for each."),
	("names two entries", "A name of the item belongs to an entry of the glossary and one of the seed, or two of the seed: the item is not joined to the second (the entry it did join, if any, is kept)."),
	("id collides", "The term's id is the id of an entry kept before it (the glossary's, the seed's, then the inventories' in their order): the later one is left out."),
	("no id", "The term has no letter or digit: its id would be empty."),
	("name taken", "The term is a name (or an avoid name) of another entry."),
	("definition refused", "The checks refuse the definition even after the mechanical changes."),
	("home not in the outline", "The home page is no page of the outline."),
	("unreadable", "The line is not a term line."),
	("parenthesis dropped", "A parenthesis inside a name, dropped from the name (the entry is kept)."),
	("admitted term refused", "A term of plan/glossary/admitted.json that the checks refuse, that names an entry homed on another page, or whose home is no page of the outline."),
]


def everyday(entries):
	return sorted((entry["term"] for entry in entries if entry["_source"] == "inventory" and " " not in entry["term"] and
		entry["term"].lower() in COMMON), key=str.lower)


def report_text(entries, problems, changes, info, glossary_count, seed_count, item_count, candidate_count):
	problems = sorted(set(problems))
	sources = {"glossary": 0, "seed": 0, "inventory": 0, "admitted": 0}
	for entry in entries:
		sources[entry["_source"]] += 1
	lines = ["# The glossary's merge", "",
		"Written by `plan/glossary/merge.py` (rulings-11.md, R51); do not edit. It lists what the merge could not decide.",
		"", "## Counts", "",
		"| What | Count |", "| --- | --- |",
		"| Entries written to `src/content/glossary.json` | %d |" % len(entries),
		"| of them the glossary's own entries, kept | %d of %d |" % (sources["glossary"], glossary_count),
		"| of them the seed's | %d of %d |" % (sources["seed"], seed_count),
		"| of them the inventories' | %d |" % sources["inventory"],
		"| of them admitted from the pages' notes (`plan/glossary/admitted.json`) | %d |" % sources["admitted"],
		"| Term items of the inventories | %d |" % item_count,
		"| Entries their lines give, before joining | %d |" % candidate_count,
		"| Entries with a use home | %d |" % sum(1 for entry in entries if entry.get("use")),
		"| Terms with a parenthesis that qualifies them, kept as the source writes it | %d |" % sum(
			1 for entry in entries if "(" in entry["term"] and not entry.get("_qualified")),
		"| Inventory terms that are one everyday word of `tools/data/common-words.txt` | %d |" % len(everyday(entries)),
		"| Entries of one word with several meanings, qualified by their part (R53) | %d |" % sum(
			1 for entry in entries if entry.get("_qualified")),
		""]
	lines += ["## Left out and listed, by reason", "", "| Reason | Count | What it means |", "| --- | --- | --- |"]
	counts = {}
	for reason, *_ in problems:
		counts[reason] = counts.get(reason, 0) + 1
	for reason, meaning in REASONS:
		if counts.get(reason):
			lines.append("| %s | %d | %s |" % (reason, counts[reason], meaning))
	lines.append("")
	lines += ["## Mechanical changes to definitions", "", "| Change | Definitions |", "| --- | --- |"]
	for change in sorted(changes):
		lines.append("| %s | %d |" % (change, changes[change]))
	lines.append("")
	for reason, meaning in REASONS:
		listed = sorted({problem for problem in problems if problem[0] == reason})
		if not listed:
			continue
		lines += ["## %s" % reason[0].upper() + reason[1:], "", meaning, ""]
		for _, item, label, detail in listed:
			lines.append("- `%s` %s: %s" % (item, label.replace("|", "\\|"), detail.replace("|", "\\|")))
		lines.append("")
	lines += ["## Terms with a parenthesis", "", "The parenthesis qualifies the term: the lint matches the name before it (rulings-11.md, "
		"R53), and the glossary page shows the whole name.", "",
		", ".join(sorted((entry["term"] for entry in entries if "(" in entry["term"] and not entry.get("_qualified")), key=str.lower)), ""]
	lines += ["## Inventory terms that are one everyday word", "", "The lint asks for no mark at an unmarked use of these on a page "
		"that is not their home (style.md §3, rulings-11.md, R53): a writer marks the word where the page uses the term's sense.",
		"", ", ".join(everyday(entries)), ""]
	for title, name in (("Admitted from the pages' notes", "admitted"), ("One word, several meanings", "meanings"), ("Joins the rows' notes made", "notes"), ("Use homes", "uses"), ("The seed and the glossary", "seed"),
			("Aliases dropped", "aliases dropped"), ("Ids changed", "ids"),
			("Names not made aliases: one everyday word of tools/data/common-words.txt, which would make the lint mark its everyday uses", "everyday")):
		if info[name]:
			lines += ["## " + title, ""] + ["- " + line for line in sorted(set(info[name]))] + [""]
	return "\n".join(lines).rstrip("\n") + "\n"


def main():
	parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
	parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when an output is not what the merge gives")
	options = parser.parse_args()
	result = merge()
	entries = result[0]
	outputs = {GLOSSARY: glossary_text(entries), REPORT: report_text(*result)}
	if options.check:
		stale = [path for path, text in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
		for path in stale:
			print("%s is not what the merge gives: run python -I plan/glossary/merge.py" % path.relative_to(ROOT).as_posix())
		return 1 if stale else 0
	for path, text in outputs.items():
		path.write_bytes(text.encode("utf-8"))
	print("%d entries; report: %s" % (len(entries), REPORT.relative_to(ROOT).as_posix()))
	return 0


if __name__ == "__main__":
	sys.exit(main())

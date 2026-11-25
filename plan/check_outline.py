"""Check the book's outline: plan/outline-1.md to outline-4.md against plan/tracks.md, and the counts that
plan/book.md, plan/process.md and plan/README.md state.

Run:
    python plan/check_outline.py            check; one line per problem; exit 1 on any problem
    python plan/check_outline.py --counts   also print pages per part, kind, size, track, wave and mark
    python plan/check_outline.py --words    also print the estimated words per part and track
    python plan/check_outline.py --waves    also print the pages of every writing wave

Standard library only. The rules are those of outline-1.md ("How to read the tables" and "The check"),
plan/tracks.md and rulings 1 (R1, R2, R4, R6) and 2 (the order of the parts). The tool builder moves these rules into
tools/booklib/outline.py, which tools/pages.py also uses (site.md, "Outline rules on the pages"); this script then
calls that module, so that the plan's check and the site's check cannot disagree.
"""

import argparse
import re
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parent
OUTLINE_FILES = ["outline-1.md", "outline-2.md", "outline-3.md", "outline-4.md"]
TRACKS_FILE = "tracks.md"

KINDS = {"C": "concept", "I": "internals", "T": "tutorial", "H": "how-to", "R": "reference", "P": "primer"}
SIZES = ["S", "M", "L", "XL"]
WORDS = {"S": 1500, "M": 3000, "L": 5000, "XL": 8000}
# The range of prose words of each size (rulings 7, R28, rule S; rulings 8, R37: the tops and bottoms).
RANGES = {"S": (600, 2250), "M": (2251, 4000), "L": (4001, 6500), "XL": (6501, 10000)}
TRACK_LETTERS = ["G", "B", "E"]
COLUMNS = ["id", "Title", "Kind", "Size", "Tracks", "Needs", "From"]
# At most five page ids in a row's Needs, alternatives included (rulings 1, R1).
MAX_NEED_IDS = 5
# Last segments a row may not use: the generated part pages <part>/index and <part>/review (rulings 1, R2).
RESERVED_LAST_SEGMENTS = {"index", "review"}
GENERATED_PAGES_FROM = 8

# The parts in the book's order (rulings 2, "Order of the parts").
PART_ORDER = ["start", "make", "basics", "core", "world", "gpu", "assets", "draw", "light", "image", "indirect",
	"physics", "animation", "audio", "input", "scripting", "ui", "worlds", "editor", "editor-ui", "automation",
	"engineering", "capstone", "reference", "appendix"]
TRACKLESS_PARTS = {"reference", "appendix"}
# The track sequences of rulings 1, R4, and the pages they name.
FIRST_SCRIPT = "make/first-script"
PROGRAMMING_PRIMERS = ["basics/programming-1", "basics/programming-2", "basics/programming-3", "basics/debugging"]
G_SIDE_STEPS = ["basics/tools", "basics/math-vectors"]
B_BEFORE_FIRST_SCRIPT = ["basics/computer", "basics/tools"]
NOT_ON_B = {"start/coming-from"}
# A game maker never has to read internals (book.md, "Tracks", rule 2): the kinds a page of track G or B may have.
GB_KINDS = {"C", "H", "P", "T"}
# The marks of rulings 1, R6.
W8_PAGES = {"light/local-shadows", "light/area-lights", "indirect/gi-voxels", "indirect/gi-cascades",
	"indirect/gi-limits", "make/lamps", "make/gi"}
W8R_PAGES = {"light/lights", "light/many-lights", "gpu/frame-tour", "image/quality-settings", "make/look",
	"make/quality", "make/performance"}

# The writing waves: rulings 3 ("process.md", PR1), corrected where this check found a page that needs a page of a
# later wave (the ruling: fix the wave list, not the Needs). Corrections: `editor` moves from wave 3 to wave 5 (its
# pages need `draw`, `input`, `scripting` and `worlds`); `scripting` moves from wave 4 to wave 5
# (`scripting/script-system` needs `animation/time-events`). Phase B holds the W8 pages and, as process.md's phase B
# says, the reference pages and the appendices. A selector is a part slug, or "make:A", "make:B", "make:C" for a block
# of part make. Every page marked W8 is written in phase B whatever its part: the selector "W8" is tried first.
WAVES = [
	("1", "start, basics, core, world", ["start", "basics", "core", "world"]),
	("2", "make block A, gpu", ["make:A", "gpu"]),
	("3", "assets, make block B without W8 pages", ["assets", "make:B"]),
	("4", "draw, light and image without W8 pages, physics, audio, input",
		["draw", "light", "image", "physics", "audio", "input"]),
	("5", "indirect without W8 pages, animation, scripting, ui, worlds, editor, make block C",
		["indirect", "animation", "scripting", "ui", "worlds", "editor", "make:C"]),
	("6", "editor-ui, automation, engineering, capstone", ["editor-ui", "automation", "engineering", "capstone"]),
	("B", "phase B: the W8 pages, reference, appendix", ["W8", "reference", "appendix"]),
]

PART_HEADING = re.compile(r"^## Part (\d+) — (.+) \(`([a-z0-9-]+)`\)\s*$")
BLOCK_LINE = re.compile(r"^\*\*Block ([A-Z]) — .+\*\*\s*$")
TRACKS_LINE = re.compile(r"^Tracks:\s*(.*)$")
# A Tracks line or cell starts with its letters ("G, B" or "-"); prose may follow after ".", ";", " (" or " —".
TRACK_LIST = re.compile(r"^(-|[GBE](?:, [GBE])*)(.*)$")
PART_NEEDS_LINE = re.compile(r"^Needs of the part:\s*(.*)$")
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)+$")
CODE_ID = re.compile(r"^`([^`]+)`$")
MARK_AT_END = re.compile(r" · (W8r?)(?: \(([^()]+)\))?\s*$")
ANY_MARK = re.compile(r"\bW8\w*")
TRACK_HEADING = re.compile(r"^## Track ([A-Z])\b")
OTHER_HEADING = re.compile(r"^#{1,6} ")
TRACK_ENTRY = re.compile(r"^(\d+)\. `([^`]+)`( \(side step\))?(?: — .+)?\s*$")
NUMBERED_LINE = re.compile(r"^\d+\. ")


class Page:
	def __init__(self, file, line, part, block, cells):
		self.file = file
		self.line = line
		self.part = part
		self.block = block
		self.raw = cells
		self.id = ""
		self.title = cells[1].strip()
		self.kind = cells[2].strip()
		self.size = cells[3].strip()
		self.tracks = []
		self.needs = []  # list of Needs; a Need is a list of alternative ids
		self.mark = None  # None, "W8" or "W8r"
		self.mark_section = None
		self.index = 0  # position in the book's order of rows
		self.wave = None

	def where(self):
		return f"{self.file}:{self.line}: `{self.id}`"


class Part:
	def __init__(self, number, title, slug, file, line):
		self.number = number
		self.title = title
		self.slug = slug
		self.file = file
		self.line = line
		self.tracks_line = None
		self.needs_line = None
		self.needs_line_number = None
		self.pages = []


class Outline:
	def __init__(self):
		self.parts = []
		self.pages = []
		self.by_id = {}
		self.tracks = {}  # letter -> list of (id, side_step, line)
		self.problems = []

	def problem(self, text):
		self.problems.append(text)


def split_row(line):
	"""Split a table row on pipes that are not escaped (`\\|` is the alternative separator)."""
	text = line.strip()
	if text.startswith("|"):
		text = text[1:]
	if text.endswith("|") and not text.endswith("\\|"):
		text = text[:-1]
	return [cell.strip() for cell in re.split(r"(?<!\\)\|", text)]


def parse_needs(cell, where, outline):
	cell = cell.strip()
	if cell == "-":
		return []
	needs = []
	for item in cell.split(","):
		item = item.strip()
		alternatives = []
		for alternative in item.split("\\|"):
			match = CODE_ID.match(alternative.strip())
			if not match:
				outline.problem(f"{where}: Needs item {item!r} is not `id` or `a`\\|`b`")
				alternatives = []
				break
			alternatives.append(match.group(1))
		if alternatives:
			if len(set(alternatives)) != len(alternatives):
				outline.problem(f"{where}: Need {item!r} names one alternative twice")
			needs.append(alternatives)
	return needs


def parse_track_list(text):
	"""The set of letters a Tracks line or a Parts table cell starts with, or None when it starts with no list."""
	match = TRACK_LIST.match(text.strip())
	if not match:
		return None
	rest = match.group(2)
	if rest and not (rest[0] in ".;" or rest.startswith(" (") or rest.startswith(" —")):
		return None
	return set() if match.group(1) == "-" else set(match.group(1).split(", "))


def parse_tracks_cell(cell, where, outline):
	cell = cell.strip()
	if cell == "-":
		return []
	letters = [letter.strip() for letter in cell.split(",")]
	for letter in letters:
		if letter not in TRACK_LETTERS:
			outline.problem(f"{where}: Tracks {cell!r} holds {letter!r}; allowed: G, B, E or -")
	if len(set(letters)) != len(letters):
		outline.problem(f"{where}: Tracks {cell!r} names a track twice")
	return [letter for letter in letters if letter in TRACK_LETTERS]


def read_outline(outline):
	for name in OUTLINE_FILES:
		path = PLAN / name
		if not path.is_file():
			outline.problem(f"{name}: file missing")
			continue
		part = None
		block = None
		continuing = None  # "tracks" or "needs" while a part's line wraps onto the next lines
		for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
			if continuing is not None:
				if (line.strip() and not line.startswith(("|", "#", "**"))
						and not TRACKS_LINE.match(line) and not PART_NEEDS_LINE.match(line)):
					if continuing == "tracks":
						part.tracks_line += " " + line.strip()
					else:
						part.needs_line += " " + line.strip()
					continue
				continuing = None
			heading = PART_HEADING.match(line)
			if heading:
				part = Part(int(heading.group(1)), heading.group(2), heading.group(3), name, number)
				outline.parts.append(part)
				block = None
				continue
			if line.startswith("## ") or line.startswith("# "):
				if line.startswith("## Part"):
					outline.problem(f"{name}:{number}: part heading not understood: {line!r}")
				part = None
				continue
			if part is None:
				if line.startswith("| `"):
					outline.problem(f"{name}:{number}: a table row outside a part (no `## Part N — Title (`slug`)` "
						"heading above it): it is no page")
				continue
			block_line = BLOCK_LINE.match(line)
			if block_line:
				block = block_line.group(1)
				continue
			tracks_line = TRACKS_LINE.match(line)
			if tracks_line and part.tracks_line is None:
				part.tracks_line = tracks_line.group(1)
				continuing = "tracks"
				continue
			needs_line = PART_NEEDS_LINE.match(line)
			if needs_line and part.needs_line is None:
				part.needs_line = needs_line.group(1)
				part.needs_line_number = number
				continuing = "needs"
				continue
			if not line.startswith("|"):
				continue
			cells = split_row(line)
			if cells and cells[0] == "id":
				if cells != COLUMNS:
					outline.problem(f"{name}:{number}: header {cells} differs from {COLUMNS}")
				continue
			if cells and set(cells[0]) <= {"-", " ", ":"}:
				continue
			if len(cells) != len(COLUMNS):
				outline.problem(f"{name}:{number}: row has {len(cells)} columns, not {len(COLUMNS)}")
				continue
			page = Page(name, number, part, block, cells)
			id_match = CODE_ID.match(cells[0])
			if not id_match:
				outline.problem(f"{name}:{number}: id {cells[0]!r} is not written as `id`")
				continue
			page.id = id_match.group(1)
			where = page.where()
			page.tracks = parse_tracks_cell(cells[4], where, outline)
			page.needs = parse_needs(cells[5], where, outline)
			from_cell = cells[6]
			mark = MARK_AT_END.search(from_cell)
			rest = from_cell[: mark.start()] if mark else from_cell
			if mark:
				page.mark = mark.group(1)
				page.mark_section = mark.group(2)
			if ANY_MARK.search(rest):
				outline.problem(f"{where}: From holds a mark other than a final ` · W8` or ` · W8r (<section>)`")
			part.pages.append(page)
			page.index = len(outline.pages)
			outline.pages.append(page)


def read_tracks(outline):
	path = PLAN / TRACKS_FILE
	if not path.is_file():
		outline.problem(f"{TRACKS_FILE}: file missing")
		for letter in TRACK_LETTERS:
			outline.tracks[letter] = []
		return
	letter = None
	expected = 1
	for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
		heading = TRACK_HEADING.match(line)
		if heading:
			letter = heading.group(1)
			if letter not in TRACK_LETTERS:
				outline.problem(f"{TRACKS_FILE}:{number}: track {letter} is not one of G, B, E")
			if letter in outline.tracks:
				outline.problem(f"{TRACKS_FILE}:{number}: track {letter} is listed twice")
			outline.tracks[letter] = []
			expected = 1
			continue
		if OTHER_HEADING.match(line):
			letter = None
			continue
		if letter is None or not NUMBERED_LINE.match(line):
			continue
		entry = TRACK_ENTRY.match(line)
		if not entry:
			outline.problem(f"{TRACKS_FILE}:{number}: entry not understood: {line!r}")
			continue
		if int(entry.group(1)) != expected:
			outline.problem(f"{TRACKS_FILE}:{number}: track {letter} entry numbered {entry.group(1)}, expected {expected}")
		expected = int(entry.group(1)) + 1
		outline.tracks[letter].append((entry.group(2), bool(entry.group(3)), number))
	for letter in TRACK_LETTERS:
		if letter not in outline.tracks:
			outline.problem(f"{TRACKS_FILE}: track {letter} has no list (heading `## Track {letter} ...`)")
			outline.tracks[letter] = []


def check_rows(outline):
	seen = {}
	for page in outline.pages:
		where = page.where()
		if page.id in seen:
			outline.problem(f"{where}: id duplicated (first at {seen[page.id]})")
		else:
			seen[page.id] = f"{page.file}:{page.line}"
			outline.by_id[page.id] = page
		if not ID_PATTERN.match(page.id):
			outline.problem(f"{where}: id is not lowercase segments of [a-z0-9-] joined by /")
		segments = page.id.split("/")
		if segments[0] != page.part.slug:
			outline.problem(f"{where}: first segment {segments[0]!r} is not the part's slug {page.part.slug!r}")
		if segments[-1] in RESERVED_LAST_SEGMENTS:
			outline.problem(f"{where}: `{page.part.slug}/{segments[-1]}` is reserved for a generated part page")
		if not page.title:
			outline.problem(f"{where}: no title")
		if page.kind not in KINDS:
			outline.problem(f"{where}: kind {page.kind!r} is not one of {', '.join(KINDS)}")
		if page.size not in SIZES:
			outline.problem(f"{where}: size {page.size!r} is not one of {', '.join(SIZES)}")
		if page.size == "XL" and (page.kind == "P" or "B" in page.tracks):
			outline.problem(f"{where}: primers and pages of track B are at most L")
		if page.mark == "W8" and page.mark_section:
			outline.problem(f"{where}: a W8 mark names no section")
		if page.mark == "W8r" and not page.mark_section:
			outline.problem(f"{where}: a W8r mark names its revised section: ` · W8r (<section>)`")
		ids = sum(len(need) for need in page.needs)
		if ids > MAX_NEED_IDS:
			outline.problem(f"{where}: its Needs name {ids} page ids (alternatives included), more than {MAX_NEED_IDS}")
		if (set(page.tracks) & {"G", "B"}) and page.kind in KINDS and page.kind not in GB_KINDS:
			outline.problem(f"{where}: kind {page.kind} on track G or B; a game maker never has to read internals or "
				f"reference (allowed: {', '.join(sorted(GB_KINDS))})")
		if page.part.slug == "basics" and page.kind != "P":
			outline.problem(f"{where}: every page of `basics` is a primer (kind P), not {page.kind}")
		expected_mark = "W8" if page.id in W8_PAGES else "W8r" if page.id in W8R_PAGES else None
		if page.mark != expected_mark:
			outline.problem(f"{where}: mark {page.mark or 'none'}, but rulings 1 (R6) give it "
				f"{expected_mark or 'none'}")
	for part in outline.parts:
		if not part.pages:
			outline.problem(f"{part.file}:{part.line}: part `{part.slug}` has no rows")
	numbers = [part.number for part in outline.parts]
	if numbers != list(range(len(numbers))):
		outline.problem(f"parts are numbered {numbers}, not 0 to {len(numbers) - 1} in order")
	slugs = [part.slug for part in outline.parts]
	for slug in set(slugs):
		if slugs.count(slug) > 1:
			outline.problem(f"part slug `{slug}` is used by {slugs.count(slug)} parts")
	if slugs != PART_ORDER:
		outline.problem(f"the parts are {slugs}; rulings 2 order them {PART_ORDER}")
	for mark, pages in (("W8", W8_PAGES), ("W8r", W8R_PAGES)):
		for page_id in sorted(pages):
			if page_id not in seen:
				outline.problem(f"rulings 1 (R6) mark `{page_id}` {mark}, but it is no row of the outline")


def expected_tracks(page):
	"""The tracks a row is on, by rulings 1 (R4): its part decides, and within `start`, `make` and `basics` the
	rows R4 names."""
	slug = page.part.slug
	if slug == "start":
		return {"G", "E"} if page.id in NOT_ON_B else {"G", "B", "E"}
	if slug == "make":
		return {"G", "B"} if page.block == "A" else {"G"}
	if slug == "basics":
		return {"G", "B", "E"} if page.id in PROGRAMMING_PRIMERS else {"B", "E"}
	if slug in TRACKLESS_PARTS:
		return set()
	return {"E"}


def check_page_tracks(outline):
	for page in outline.pages:
		want = expected_tracks(page)
		if set(page.tracks) != want:
			outline.problem(f"{page.where()}: Tracks {', '.join(page.tracks) or '-'}; rulings 1 (R4) put it on "
				f"{', '.join(letter for letter in TRACK_LETTERS if letter in want) or '-'}")
	make = next((part for part in outline.parts if part.slug == "make"), None)
	if make is not None:
		for page in make.pages:
			if page.block not in ("A", "B", "C"):
				outline.problem(f"{page.where()}: a row of `make` outside the blocks A, B and C")


def expected_sequences(outline):
	"""The three tracks as rulings 1 (R4) state them, from the rows of the outline; None when a named page is missing."""
	rows = {slug: [page.id for page in outline.pages if page.part.slug == slug] for slug in PART_ORDER}
	block_a = [page.id for page in outline.pages if page.part.slug == "make" and page.block == "A"]
	named = [FIRST_SCRIPT] + PROGRAMMING_PRIMERS + G_SIDE_STEPS + B_BEFORE_FIRST_SCRIPT + sorted(NOT_ON_B)
	missing = [page_id for page_id in named if page_id not in outline.by_id]
	if missing or FIRST_SCRIPT not in block_a:
		for page_id in missing:
			outline.problem(f"rulings 1 (R4) name `{page_id}`, which is no row of the outline")
		if FIRST_SCRIPT in outline.by_id and FIRST_SCRIPT not in block_a:
			outline.problem(f"`{FIRST_SCRIPT}` is not in block A of `make`")
		return None
	make = rows["make"]
	at = make.index(FIRST_SCRIPT) + 1
	g = rows["start"] + make[:at] + PROGRAMMING_PRIMERS + make[at:]
	at = block_a.index(FIRST_SCRIPT)
	taken = set(B_BEFORE_FIRST_SCRIPT) | set(PROGRAMMING_PRIMERS)
	b = ([page_id for page_id in rows["start"] if page_id not in NOT_ON_B] + block_a[:at] + B_BEFORE_FIRST_SCRIPT
		+ [FIRST_SCRIPT] + PROGRAMMING_PRIMERS + block_a[at + 1:]
		+ [page_id for page_id in rows["basics"] if page_id not in taken])
	e = [page.id for page in outline.pages if page.part.slug != "make" and page.part.slug not in TRACKLESS_PARTS]
	return {"G": g, "B": b, "E": e}


def check_needs_exist(outline):
	for page in outline.pages:
		for need in page.needs:
			for alternative in need:
				if alternative not in outline.by_id:
					outline.problem(f"{page.where()}: Need `{alternative}` does not exist")
				elif alternative == page.id:
					outline.problem(f"{page.where()}: needs itself")


def check_cycles(outline):
	# Pages on a track cannot form a cycle (each Need is earlier); this also covers pages on no track.
	state = {}

	def visit(page_id, stack):
		state[page_id] = 1
		stack.append(page_id)
		for need in outline.by_id[page_id].needs:
			for alternative in need:
				if alternative not in outline.by_id:
					continue
				if state.get(alternative) == 1:
					cycle = stack[stack.index(alternative):] + [alternative]
					outline.problem(f"Needs form a cycle: {' -> '.join(cycle)}")
				elif alternative not in state:
					visit(alternative, stack)
		stack.pop()
		state[page_id] = 2

	for page in outline.pages:
		if page.id not in state and page.id in outline.by_id:
			visit(page.id, [])


def check_part_lines(outline):
	for part in outline.parts:
		ids_in_part = {page.id for page in part.pages}
		letters = set()
		for page in part.pages:
			letters.update(page.tracks)
		if part.tracks_line is None:
			outline.problem(f"{part.file}:{part.line}: part `{part.slug}` has no `Tracks:` line")
		else:
			written = parse_track_list(part.tracks_line)
			if written is None:
				outline.problem(f"{part.file}:{part.line}: part `{part.slug}`'s Tracks line does not start with its "
					"letters (`G, B, E` or `-`), followed by nothing or by \".\", \";\", \" (\" or \" —\"")
			elif written != letters:
				outline.problem(f"{part.file}:{part.line}: part `{part.slug}`'s Tracks line names {sorted(written)}, "
					f"its rows are on {sorted(letters)}")
		if part.needs_line is None:
			outline.problem(f"{part.file}:{part.line}: part `{part.slug}` has no `Needs of the part:` line")
			continue
		# The line holds each Need of the part's rows that points outside the part, once; a Need with an
		# alternative inside the part is met inside it and is left out.
		expected = set()
		for page in part.pages:
			for need in page.needs:
				if not any(alternative in ids_in_part for alternative in need):
					expected.add("|".join(need))
		written = set()
		text = part.needs_line.strip()
		if text != "-":
			for item in text.split(","):
				alternatives = re.findall(r"`([^`]+)`", item)
				if not alternatives or re.sub(r"`[^`]+`|\\\||\s|\.$", "", item):
					outline.problem(f"{part.file}:{part.needs_line_number}: Needs of the part item {item.strip()!r} "
						"is not `id` or `a`\\|`b`")
					continue
				written.add("|".join(alternatives))
		for need in sorted(expected - written):
			outline.problem(f"{part.file}:{part.needs_line_number}: Needs of the part lacks "
				f"`{need.replace('|', '`|`')}`, which a row of `{part.slug}` needs")
		for need in sorted(written - expected):
			outline.problem(f"{part.file}:{part.needs_line_number}: Needs of the part names "
				f"`{need.replace('|', '`|`')}`, which no row of `{part.slug}` needs from another part")


def track_order(outline, letter):
	"""The pages on a track, in order: side steps are offered, not on the track."""
	return [page_id for page_id, side_step, _ in outline.tracks[letter] if not side_step]


def check_tracks(outline):
	for letter in TRACK_LETTERS:
		entries = outline.tracks[letter]
		listed = {}
		for page_id, side_step, line in entries:
			if page_id not in outline.by_id:
				outline.problem(f"{TRACKS_FILE}:{line}: track {letter} lists `{page_id}`, which is no row of the outline")
				continue
			if page_id in listed:
				outline.problem(f"{TRACKS_FILE}:{line}: track {letter} lists `{page_id}` twice")
			listed[page_id] = side_step
			page = outline.by_id[page_id]
			if side_step and letter in page.tracks:
				outline.problem(f"{TRACKS_FILE}:{line}: `{page_id}` is a side step of track {letter}, but its "
					f"Tracks column names {letter}")
		on_track = {page_id for page_id, side_step in listed.items() if not side_step}
		for page in outline.pages:
			if letter in page.tracks and page.id not in on_track:
				outline.problem(f"{page.where()}: Tracks names {letter}, but track {letter}'s list in "
					f"{TRACKS_FILE} does not hold it")
			if letter not in page.tracks and page.id in on_track:
				outline.problem(f"{page.where()}: track {letter}'s list in {TRACKS_FILE} holds it, but its Tracks "
					f"column does not name {letter}")
		order = track_order(outline, letter)
		position = {page_id: number for number, page_id in enumerate(order)}
		# Every Need, or one of its alternatives, comes earlier on the track.
		for page_id in order:
			page = outline.by_id.get(page_id)
			if page is None:
				continue
			for need in page.needs:
				if not any(alternative in position and position[alternative] < position[page_id]
						for alternative in need):
					outline.problem(f"{page.where()}: on track {letter}, no alternative of Need "
						f"`{'`|`'.join(need)}` comes earlier")
		# Within one part, a track keeps the outline's row order.
		last_in_part = {}
		for page_id in order:
			page = outline.by_id.get(page_id)
			if page is None:
				continue
			previous = last_in_part.get(page.part.slug)
			if previous is not None and outline.by_id[previous].index > page.index:
				outline.problem(f"{TRACKS_FILE}: track {letter} puts `{page_id}` after `{previous}`, against the "
					"order of their part's rows")
			last_in_part[page.part.slug] = page_id
		# A side step stands directly before the first page of the track whose Needs name it, and its own Needs
		# (one alternative of each) come earlier on the track, or are earlier side steps.
		side_steps_before = set()
		for number, (page_id, side_step, line) in enumerate(entries):
			if not side_step or page_id not in outline.by_id:
				continue
			following = next((entry for entry in entries[number + 1:] if not entry[1]), None)
			first_user = next((other for other in order if other in outline.by_id and
				any(page_id in need for need in outline.by_id[other].needs)), None)
			if first_user is None:
				outline.problem(f"{TRACKS_FILE}:{line}: side step `{page_id}` of track {letter}: no page of the "
					"track names it in its Needs")
			elif following is None or following[0] != first_user:
				outline.problem(f"{TRACKS_FILE}:{line}: side step `{page_id}` of track {letter} must stand directly "
					f"before `{first_user}`, the first page of the track whose Needs name it")
			at = position.get(following[0], len(order)) if following is not None else len(order)
			for need in outline.by_id[page_id].needs:
				if not any((alternative in position and position[alternative] < at) or alternative in side_steps_before
						for alternative in need):
					outline.problem(f"{TRACKS_FILE}:{line}: side step `{page_id}` of track {letter}: no alternative of "
						f"its Need `{'`|`'.join(need)}` comes earlier on the track, so its reader meets it untaught")
			side_steps_before.add(page_id)
	# The lists are the sequences of rulings 1 (R4); track E is the book's order.
	sequences = expected_sequences(outline)
	if sequences is not None:
		for letter in TRACK_LETTERS:
			order = track_order(outline, letter)
			want = sequences[letter]
			if order != want:
				number = next((n for n, (got, expected) in enumerate(zip(order, want)) if got != expected),
					min(len(order), len(want)))
				got = f"`{order[number]}`" if number < len(order) else "the end of the list"
				expected = f"`{want[number]}`" if number < len(want) else "the end of the list"
				outline.problem(f"{TRACKS_FILE}: track {letter} entry {number + 1} is {got}; rulings 1 (R4) put "
					f"{expected} there")
		side_steps = {letter: [page_id for page_id, side_step, _ in outline.tracks[letter] if side_step]
			for letter in TRACK_LETTERS}
		if sorted(side_steps["G"]) != sorted(G_SIDE_STEPS):
			outline.problem(f"{TRACKS_FILE}: track G's side steps are {side_steps['G']}; rulings 1 (R4) give "
				f"{G_SIDE_STEPS}")
		for letter in ("B", "E"):
			if side_steps[letter]:
				outline.problem(f"{TRACKS_FILE}: track {letter} has side steps {side_steps[letter]}; only track G has "
					"side steps (rulings 1, R4)")
	# A page on no track: every Need (one alternative) comes earlier in the book's order of rows (rulings 1, R1).
	for page in outline.pages:
		if page.tracks:
			continue
		for need in page.needs:
			if not any(alternative in outline.by_id and outline.by_id[alternative].index < page.index
					for alternative in need):
				outline.problem(f"{page.where()}: on no track, and no alternative of its Need "
					f"`{'`|`'.join(need)}` comes earlier in the book's order")


def assign_waves(outline):
	names = [wave[0] for wave in WAVES]
	for page in outline.pages:
		keys = []
		if page.mark == "W8":
			keys.append("W8")
		if page.part.slug == "make":
			keys.append(f"make:{page.block}")
		keys.append(page.part.slug)
		for key in keys:
			for name, _, selectors in WAVES:
				if key in selectors:
					page.wave = name
					break
			if page.wave is not None:
				break
		if page.wave is None:
			outline.problem(f"{page.where()}: no writing wave holds it (WAVES in check_outline.py)")
	selectors_used = {}
	for name, _, selectors in WAVES:
		for selector in selectors:
			if selector in selectors_used:
				outline.problem(f"WAVES: selector {selector!r} is in waves {selectors_used[selector]} and {name}")
			selectors_used[selector] = name
	rank = {name: number for number, name in enumerate(names)}
	for page in outline.pages:
		if page.wave is None:
			continue
		for need in page.needs:
			waves = [outline.by_id[alternative].wave for alternative in need
				if alternative in outline.by_id and outline.by_id[alternative].wave is not None]
			if waves and all(rank[wave] > rank[page.wave] for wave in waves):
				outline.problem(f"{page.where()}: wave {page.wave} page needs `{'`|`'.join(need)}` of wave "
					f"{min(waves, key=rank.get)}")


NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
	"ten": 10, "eleven": 11, "twelve": 12}


def to_number(text):
	text = text.strip().replace(",", "")
	if text.isdigit():
		return int(text)
	return NUMBER_WORDS.get(text.lower())


def table_rows(text, header_start):
	"""The rows of the first table whose header line starts with `header_start`, as lists of cells; None if absent."""
	lines = [line.strip() for line in text.splitlines()]  # a table may stand indented inside a list item
	for number, line in enumerate(lines):
		if line.startswith(header_start):
			rows = []
			for row in lines[number + 2:]:
				if not row.startswith("|"):
					break
				rows.append(split_row(row))
			return rows
	return None


def compute_counts(outline):
	counts = {
		"pages": len(outline.pages),
		"parts": len(outline.parts),
		"kinds": {kind: sum(1 for page in outline.pages if page.kind == kind) for kind in KINDS},
		"sizes": {size: sum(1 for page in outline.pages if page.size == size) for size in SIZES},
		"track": {letter: sum(1 for page in outline.pages if letter in page.tracks) for letter in TRACK_LETTERS},
		"side steps": {letter: sum(1 for _, side_step, _ in outline.tracks[letter] if side_step)
			for letter in TRACK_LETTERS},
		"trackless": sum(1 for page in outline.pages if not page.tracks),
		"track kinds": {letter: {kind: sum(1 for page in outline.pages if letter in page.tracks and page.kind == kind)
			for kind in KINDS} for letter in TRACK_LETTERS},
		"words": sum(WORDS.get(page.size, 0) for page in outline.pages),
		"track words": {letter: sum(WORDS.get(page.size, 0) for page in outline.pages if letter in page.tracks)
			for letter in TRACK_LETTERS},
		"generated parts": sum(1 for part in outline.parts if len(part.pages) >= GENERATED_PAGES_FROM),
		"waves": {name: (sum(1 for page in outline.pages if page.wave == name),
			sum(WORDS.get(page.size, 0) for page in outline.pages if page.wave == name)) for name, _, _ in WAVES},
		"W8": sum(1 for page in outline.pages if page.mark == "W8"),
		"W8r": sum(1 for page in outline.pages if page.mark == "W8r"),
		"part": {part.slug: part for part in outline.parts},
	}
	counts["phase B"] = counts["waves"].get("B", (0, 0))[0]
	counts["phase A"] = counts["pages"] - counts["phase B"]
	return counts


def document_sentences(counts):
	"""(file, pattern, expected values): every sentence of book.md, process.md and README.md that states a count of
	the outline. Each pattern must occur at least once, and every occurrence must state the expected values."""
	kinds = counts["kinds"]
	sizes = counts["sizes"]
	words = counts["track words"]
	part = counts["part"]
	generated = counts["generated parts"]
	return [
		("book.md", r"\*\*(\d+) pages\*\* in (\d+) parts, plus (\d+) generated index and review pages in (\d+) parts",
			(counts["pages"], counts["parts"], 2 * generated, generated)),
		("book.md", r"About ([\d,]+) words: track G reads about ([\d,]+), track B ([\d,]+) and track E ([\d,]+)",
			(counts["words"], words["G"], words["B"], words["E"])),
		("book.md", r"Kinds: P (\d+), C (\d+), I (\d+), T (\d+), H (\d+), R (\d+)",
			tuple(kinds[kind] for kind in "PCITHR")),
		("book.md", r"Sizes: S about ([\d,]+) words \((\d+) pages\), M ([\d,]+) \((\d+)\), L ([\d,]+) \((\d+)\), "
			r"XL ([\d,]+) \((\d+)\)", tuple(value for size in SIZES for value in (WORDS[size], sizes[size]))),
		("book.md", r"A size is a budget of prose words with a range: S ([\d,]+) to ([\d,]+), M ([\d,]+) to ([\d,]+), "
			r"L ([\d,]+) to ([\d,]+), XL ([\d,]+) to ([\d,]+)", tuple(value for size in SIZES for value in RANGES[size])),
		("book.md", r"Each of the (\d+) parts with eight or more rows", (generated,)),
		("book.md", r"That makes (\d+) generated pages", (2 * generated,)),
		("book.md", r"The (\d+) pages of `reference` and `appendix` are on no track", (counts["trackless"],)),
		("README.md", r"(\d+) pages in (\d+) parts", (counts["pages"], counts["parts"])),
		("README.md", r"The outline is final: (\d+) pages", (counts["pages"],)),
		("README.md", r"the (\d+) primers of `basics`", (kinds["P"],)),
		("README.md", r"The (\d+) parts of eight or more pages", (generated,)),
		("README.md", r"The (\w+) W8 pages", (counts["W8"],)),
		("README.md", r"the (\w+) W8r pages", (counts["W8r"],)),
		("process.md", r"(\d+) pages in (\d+) parts, (\d+) of them written in phase A and (\d+) in phase B",
			(counts["pages"], counts["parts"], counts["phase A"], counts["phase B"])),
		("process.md", r"for the (\d+) parts of eight or more pages", (generated,)),
		("process.md", r"the (\d+) parts of eight or more pages have their index and review pages", (generated,)),
		("process.md", r"the (\d+) W8 pages are written", (counts["W8"],)),
		("process.md", r"the (\d+) W8r pages have the section", (counts["W8r"],)),
		("process.md", r"the (\d+) pages of `reference` are written .{0,60}?, and the (\d+) pages of `appendix`",
			(len(part["reference"].pages) if "reference" in part else 0,
				len(part["appendix"].pages) if "appendix" in part else 0)),
		("process.md", r"the (\d+) W8 pages, `reference` \((\d+) pages\), `appendix` \((\d+) pages\)",
			(counts["W8"], len(part["reference"].pages) if "reference" in part else 0,
				len(part["appendix"].pages) if "appendix" in part else 0)),
		("process.md", r"The work is large: (\d+) pages", (counts["pages"],)),
		("process.md", r"all (\d+) pages of the outline are `final`", (counts["pages"],)),
		("process.md", r"for each of the (\d+) parts", (counts["parts"],)),
	]


def check_documents(outline):
	"""The counts book.md, process.md and README.md state agree with the outline (rulings 3: the counts come from
	this script)."""
	counts = compute_counts(outline)
	texts = {}
	for name in ("book.md", "process.md", "README.md"):
		path = PLAN / name
		if not path.is_file():
			outline.problem(f"{name}: file missing")
			continue
		texts[name] = path.read_text(encoding="utf-8")
	flat = {name: re.sub(r"\s+", " ", text) for name, text in texts.items()}
	for name, pattern, expected in document_sentences(counts):
		if name not in flat:
			continue
		matches = list(re.finditer(pattern, flat[name]))
		if not matches:
			outline.problem(f"{name}: no sentence matches {pattern!r}; it states counts this script checks "
				"(document_sentences in check_outline.py)")
		for match in matches:
			got = tuple(to_number(group) for group in match.groups())
			if got != tuple(expected):
				outline.problem(f"{name}: {match.group(0)!r} states {got}; the outline gives {tuple(expected)}")
	book = texts.get("book.md")
	if book is not None:
		rows = table_rows(book, "| # | Part | Slug |")
		if rows is None:
			outline.problem("book.md: no Parts table (header `| # | Part | Slug | Tracks | Pages | Words (estimate) "
				"| Index and review pages |`)")
		else:
			slugs = []
			for cells in rows:
				if len(cells) < 7:
					outline.problem(f"book.md: Parts table row {cells} has fewer than 7 cells")
					continue
				slug = cells[2].strip("` ")
				slugs.append(slug)
				part = counts["part"].get(slug)
				if part is None:
					outline.problem(f"book.md: Parts table row `{slug}` is no part of the outline")
					continue
				where = f"book.md: Parts table, `{slug}`"
				if to_number(cells[0]) != part.number:
					outline.problem(f"{where}: number {cells[0]}, the outline's is {part.number}")
				letters = set()
				for page in part.pages:
					letters.update(page.tracks)
				written = parse_track_list(cells[3])
				if written != letters:
					outline.problem(f"{where}: Tracks {cells[3]!r} does not start with the tracks of its rows, "
						f"{', '.join(letter for letter in TRACK_LETTERS if letter in letters) or '-'}")
				pages = re.match(r"(\d+)", cells[4])
				if not pages or int(pages.group(1)) != len(part.pages):
					outline.problem(f"{where}: Pages {cells[4]!r}, the outline has {len(part.pages)}")
				blocks = dict((block, int(n)) for block, n in re.findall(r"\b([A-Z]) (\d+)\b", cells[4]))
				for block, n in blocks.items():
					actual = sum(1 for page in part.pages if page.block == block)
					if n != actual:
						outline.problem(f"{where}: block {block} has {n} pages in the table, {actual} in the outline")
				part_words = sum(WORDS.get(page.size, 0) for page in part.pages)
				if to_number(cells[5]) != part_words:
					outline.problem(f"{where}: Words {cells[5]!r}, the outline's sizes give {part_words:,}")
				generated = "yes" if len(part.pages) >= GENERATED_PAGES_FROM else "no"
				if cells[6].strip() != generated:
					outline.problem(f"{where}: Index and review pages {cells[6]!r}, the outline gives {generated!r}")
			if slugs != [part.slug for part in outline.parts]:
				outline.problem("book.md: the Parts table does not list the outline's parts in order")
		rows = table_rows(book, "| Kind | Answers |")
		if rows is None:
			outline.problem("book.md: no table of the kinds of page (header `| Kind | Answers | ...`)")
		else:
			for cells in rows:
				kind = re.match(r"\*\*([A-Z]) ", cells[0])
				if kind and kind.group(1) in KINDS and to_number(cells[-1]) != counts["kinds"][kind.group(1)]:
					outline.problem(f"book.md: kind {kind.group(1)} has {cells[-1]} pages in the table, "
						f"{counts['kinds'][kind.group(1)]} in the outline")
		rows = table_rows(book, "| Track | Persona |")
		if rows is None:
			outline.problem("book.md: no table of the tracks (header `| Track | Persona | Reads | Size |`)")
		else:
			for cells in rows:
				letter = re.match(r"\*\*([GBE])\*\*", cells[0])
				size = re.match(r"(\d+) pages(?: and (\d+) side steps)?", cells[-1])
				if not letter:
					continue
				letter = letter.group(1)
				want = (counts["track"][letter], counts["side steps"][letter])
				got = (int(size.group(1)), int(size.group(2) or 0)) if size else None
				if got != want:
					outline.problem(f"book.md: track {letter}'s Size {cells[-1]!r}; the outline gives {want[0]} pages "
						f"and {want[1]} side steps")
		match = re.search(r"track G holds (.+?) pages, and track B holds (.+?)\.", flat["book.md"])
		if not match:
			outline.problem("book.md: no sentence \"track G holds … pages, and track B holds …\" (rule 2 of Tracks)")
		else:
			for letter, text in (("G", match.group(1)), ("B", match.group(2))):
				written = {kind: int(n) for kind, n in re.findall(r"\b([A-Z]) (\d+)\b", text)}
				actual = {kind: n for kind, n in counts["track kinds"][letter].items() if n}
				if written != actual:
					outline.problem(f"book.md: track {letter} holds {written} by rule 2 of Tracks, {actual} by the "
						"outline")
	process = texts.get("process.md")
	if process is not None:
		rows = table_rows(process, "| Wave | Parts | Pages |")
		if rows is None:
			outline.problem("process.md: no table of the waves (header `| Wave | Parts | Pages | Estimated words |`)")
		else:
			seen = []
			for cells in rows:
				name = cells[0].strip()
				seen.append(name)
				if name not in counts["waves"]:
					outline.problem(f"process.md: wave {name!r} is not in WAVES")
					continue
				want = counts["waves"][name]
				got = (to_number(cells[2]), to_number(cells[3]))
				if got != want:
					outline.problem(f"process.md: wave {name} states {got[0]} pages and {cells[3]} words; the outline "
						f"gives {want[0]} and {want[1]:,}")
			if seen != [name for name, _, _ in WAVES]:
				outline.problem(f"process.md: the waves table lists {seen}, WAVES {[name for name, _, _ in WAVES]}")


def print_counts(outline):
	def table(title, rows):
		print(title)
		width = max(len(str(label)) for label, _ in rows) if rows else 0
		for label, value in rows:
			print(f"  {str(label).ljust(width)}  {value}")

	table("Pages per part:", [(f"{part.number:2d} {part.slug}", len(part.pages)) for part in outline.parts])
	make = next((part for part in outline.parts if part.slug == "make"), None)
	if make is not None:
		blocks = {}
		for page in make.pages:
			blocks[page.block] = blocks.get(page.block, 0) + 1
		table("Pages per block of make:", [(f"block {block}", count) for block, count in sorted(blocks.items())])
	table("Pages per kind:", [(f"{kind} {name}", sum(1 for page in outline.pages if page.kind == kind))
		for kind, name in KINDS.items()])
	table("Pages per size:", [(size, sum(1 for page in outline.pages if page.size == size)) for size in SIZES])
	rows = []
	for letter in TRACK_LETTERS:
		side_steps = sum(1 for _, side_step, _ in outline.tracks[letter] if side_step)
		count = sum(1 for page in outline.pages if letter in page.tracks)
		rows.append((letter, f"{count}" + (f" (and {side_steps} side steps)" if side_steps else "")))
	rows.append(("on no track", sum(1 for page in outline.pages if not page.tracks)))
	table("Pages per track:", rows)
	table("Pages per writing wave:", [(f"{name} ({description})", sum(1 for page in outline.pages if page.wave == name))
		for name, description, _ in WAVES])
	generated = [part.slug for part in outline.parts if len(part.pages) >= GENERATED_PAGES_FROM]
	print(f"Parts with generated <part>/index and <part>/review pages ({GENERATED_PAGES_FROM} or more rows): "
		f"{len(generated)}: {', '.join(generated)}")
	for mark in ["W8", "W8r"]:
		marked = [page for page in outline.pages if page.mark == mark]
		print(f"{mark} pages: {len(marked)}")
		for page in marked:
			section = f" ({page.mark_section})" if page.mark_section else ""
			print(f"  {page.id}{section}")
	print(f"Total pages: {len(outline.pages)}")


def print_words(outline):
	print("Estimated words (S 1,500, M 3,000, L 5,000, XL 8,000):")
	width = max(len(part.slug) for part in outline.parts) + 3
	for part in outline.parts:
		words = sum(WORDS.get(page.size, 0) for page in part.pages)
		print(f"  {f'{part.number:2d} {part.slug}'.ljust(width)}  {words:>9,}")
	for letter in TRACK_LETTERS:
		words = sum(WORDS.get(page.size, 0) for page in outline.pages if letter in page.tracks)
		print(f"  {f'track {letter}'.ljust(width)}  {words:>9,}")
	print(f"  {'total'.ljust(width)}  {sum(WORDS.get(page.size, 0) for page in outline.pages):>9,}")


def print_waves(outline):
	for name, description, _ in WAVES:
		pages = [page for page in outline.pages if page.wave == name]
		words = sum(WORDS.get(page.size, 0) for page in pages)
		print(f"Wave {name} ({description}): {len(pages)} pages, {words:,} words")
		for page in pages:
			print(f"  {page.id}")


def main():
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--counts", action="store_true", help="print pages per part, kind, size, track, wave and mark")
	parser.add_argument("--words", action="store_true", help="print the estimated words per part and track")
	parser.add_argument("--waves", action="store_true", help="print the pages of every writing wave")
	args = parser.parse_args()

	outline = Outline()
	read_outline(outline)
	read_tracks(outline)
	check_rows(outline)
	check_page_tracks(outline)
	check_needs_exist(outline)
	check_cycles(outline)
	check_part_lines(outline)
	check_tracks(outline)
	assign_waves(outline)
	check_documents(outline)

	for problem in outline.problems:
		print(problem)
	if args.counts:
		print_counts(outline)
	if args.words:
		print_words(outline)
	if args.waves:
		print_waves(outline)
	if outline.problems:
		print(f"{len(outline.problems)} problems", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())

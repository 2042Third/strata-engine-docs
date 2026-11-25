"""Check the glossary seed, plan/glossary/seed.json: the base vocabulary of a complete beginner.

Run:
    python plan/glossary/check_seed.py            check; one line per problem; exit 1 on any problem
    python plan/glossary/check_seed.py --counts   also print the entries per home page, in the order of track B
    python plan/glossary/check_seed.py --seed F   check the file F instead of plan/glossary/seed.json

Standard library only. It reads the outline and plan/tracks.md through plan/check_outline.py. The rules are those of
plan/pipelines.md §9, plan/style.md §3 and the seed's brief:

- the file parses, and holds {"terms": [...]} with 300 to 400 entries;
- every entry has the six fields id, term, definition, home, aliases and avoid, of the right types, may have a seventh,
  use, and has no other field;
- use, where an entry has it, is a non-empty string without spaces at its start or end, and it is the id of a page of
  the outline (the entry's use home: pipelines.md §9, book.md "One home per concept"). Nothing else is checked about
  it: the order of the entries and the names a definition may use follow home alone;
- id is the term as the site makes ids (src/lib/glossary.mjs, github-slugger): lowercase, punctuation dropped, each
  space a "-" ("two's complement" -> twos-complement), and is lowercase words of [a-z0-9] joined by "-";
- home is a page of part start or basics in the outline, and the page is on track B (the seed is the vocabulary of
  the persona B0, whose definitions may use only what track B has taught);
- the entries stand in the order of their homes on track B;
- no id occurs twice, and no name (term or alias) occurs twice, in any case, across the file; an avoid name is no
  entry's name;
- every definition is one sentence ending with a full stop, by the site's own test (src/lib/glossary.mjs), of at most
  40 words, and holds neither its own term nor one of its own aliases;
- every seed name used inside a definition belongs to an entry whose home is not later on track B than the home of
  the entry it defines;
- no definition uses an avoid name.

How names are found in a definition: as whole words (a letter, digit or "_" may not touch them); a space or a hyphen
inside a name matches a space or a hyphen; a name written in lowercase matches in any case and in its plural
("entity" -> "entities", "matrix" -> "matrices"); a name with capitals ("GPU") matches only as written, or with an
"s". Where names overlap, the longest wins ("call stack" over "stack"), as the site's term matcher does. The test for
a definition's own term is stricter: its term and aliases may not occur at all, even inside a longer name.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # importing check_outline must not write into plan/

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
SEED = HERE / "seed.json"
sys.path.insert(0, str(PLAN))

import check_outline  # noqa: E402  (plan/check_outline.py reads the outline and the tracks)

FIELDS = ["id", "term", "definition", "home", "aliases", "avoid"]
OPTIONAL_FIELDS = ["use"]
# The part that holds the use homes (book.md, "One home per concept", rule 2).
USE_PART = "make"
MIN_ENTRIES = 300
MAX_ENTRIES = 400
MAX_WORDS = 40
HOME_PARTS = {"start", "basics"}
TRACK = "B"
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# The site's test of one sentence (src/lib/glossary.mjs): no "!" or "?", a "." only before a character that is not a
# space ("0.8.0", "Coin.h"), and a final full stop.
ONE_SENTENCE = re.compile(r"^[^.!?]+(\.[^\s.!?][^.!?]*)*[.]$")
# Plurals that the site's simple rules miss, for names that end in these words.
IRREGULAR_PLURALS = {"axis": "axes", "matrix": "matrices", "vertex": "vertices", "index": "indices", "basis": "bases",
	"child": "children", "datum": "data"}


def slug(term):
	"""The id the site makes from a term (github-slugger on ASCII text)."""
	text = term.lower()
	text = re.sub(r"[^a-z0-9 _\-]", "", text)
	return text.replace(" ", "-")


def plural_forms(name):
	"""The plurals of a lowercase name: the site's rules (src/lib/glossary.mjs pluralForms) and IRREGULAR_PLURALS."""
	forms = []
	if re.search(r"[a-z]$", name):
		if re.search(r"(s|x|z|ch|sh)$", name):
			forms.append(name + "es")
		elif re.search(r"[^aeiou]y$", name):
			forms.append(name[:-1] + "ies")
		else:
			forms.append(name + "s")
	last = re.split(r"[\s-]", name)[-1]
	if last in IRREGULAR_PLURALS:
		forms.append(name[: len(name) - len(last)] + IRREGULAR_PLURALS[last])
	return forms


def name_pattern(name):
	"""A compiled pattern that finds one name, with its plurals, as whole words."""
	exact = name != name.lower()
	forms = [name] + ([name + "s"] if exact and re.search(r"[A-Za-z]$", name) else []) + ([] if exact else plural_forms(name))
	alternatives = []
	for form in sorted(set(forms), key=len, reverse=True):
		parts = [re.escape(part) for part in re.split(r"[\s-]+", form) if part]
		alternatives.append(r"[\s\-]+".join(parts))
	body = "|".join(alternatives)
	return re.compile(r"(?<!\w)(?:" + body + r")(?!\w)", 0 if exact else re.IGNORECASE)


def words(text):
	return len(text.split())


def find_names(text, patterns):
	"""The non-overlapping uses of names in a text, the longest first: a list of (start, end, entry index, name)."""
	found = []
	for index, name, pattern in patterns:
		for match in pattern.finditer(text):
			found.append((match.start(), match.end(), index, name))
	found.sort(key=lambda item: (-(item[1] - item[0]), item[0]))
	taken = []
	for start, end, index, name in found:
		if all(end <= other_start or start >= other_end for other_start, other_end, _, _ in taken):
			taken.append((start, end, index, name))
	return sorted(taken)


def load(seed, problems):
	try:
		data = json.loads(seed.read_text(encoding="utf-8"))
	except FileNotFoundError:
		problems.append(f"{seed.name}: file missing")
		return None
	except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
		problems.append(f"{seed.name}: does not parse: {error}")
		return None
	if not isinstance(data, dict) or not isinstance(data.get("terms"), list):
		problems.append(f'{seed.name}: the file must be an object {{"terms": [...]}}')
		return None
	if set(data) != {"terms"}:
		problems.append(f'{seed.name}: keys other than "terms": {sorted(set(data) - {"terms"})}')
	return data["terms"]


def check_shapes(entries, problems):
	"""Every entry has the six fields with their types, and use with its type where it has use; returns the entries
	that can be checked further."""
	good = []
	for number, entry in enumerate(entries, start=1):
		where = f"entry {number}"
		if not isinstance(entry, dict):
			problems.append(f"{where}: not an object")
			continue
		where = f"entry {number} ({entry.get('term', '?')!r})"
		missing = [field for field in FIELDS if field not in entry]
		extra = [field for field in entry if field not in FIELDS + OPTIONAL_FIELDS]
		if missing:
			problems.append(f"{where}: missing fields {missing}")
		if extra:
			problems.append(f"{where}: fields outside the seed's format {extra}")
		ok = not missing
		for field in ["id", "term", "definition", "home", "use"]:
			if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
				problems.append(f"{where}: {field!r} must be a non-empty string")
				ok = False
			elif field in entry and entry[field] != entry[field].strip():
				problems.append(f"{where}: {field!r} has spaces at its start or end")
		for field in ["aliases", "avoid"]:
			if field in entry and (not isinstance(entry[field], list)
					or any(not isinstance(name, str) or not name.strip() for name in entry[field])):
				problems.append(f"{where}: {field!r} must be a list of non-empty strings")
				ok = False
		if ok:
			good.append((number, entry))
	return good


def main():
	# Names and definitions hold characters such as "π" that a Windows console's code page lacks: print them escaped
	# instead of failing.
	for stream in (sys.stdout, sys.stderr):
		if hasattr(stream, "reconfigure"):
			stream.reconfigure(errors="backslashreplace")
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--counts", action="store_true", help="print the entries per home page, in the order of track B")
	parser.add_argument("--seed", type=Path, default=SEED, help="the file to check (default: plan/glossary/seed.json)")
	args = parser.parse_args()
	seed = args.seed

	problems = []
	outline = check_outline.Outline()
	check_outline.read_outline(outline)
	check_outline.read_tracks(outline)
	for problem in outline.problems:
		problems.append(f"outline: {problem}")
	track = check_outline.track_order(outline, TRACK)
	position = {page_id: index for index, page_id in enumerate(track)}
	home_pages = {page.id for page in outline.pages if page.part.slug in HOME_PARTS}

	entries = load(seed, problems)
	if entries is None:
		for problem in problems:
			print(problem)
		return 1
	if not MIN_ENTRIES <= len(entries) <= MAX_ENTRIES:
		problems.append(f"{seed.name}: {len(entries)} entries; the seed holds {MIN_ENTRIES} to {MAX_ENTRIES}")
	checked = check_shapes(entries, problems)

	# Ids, names and avoid names.
	ids = {}
	names = {}
	for number, entry in checked:
		where = f"entry {number} ({entry['term']!r})"
		expected = slug(entry["term"])
		if entry["id"] != expected:
			problems.append(f"{where}: id {entry['id']!r} is not the term as the site makes ids ({expected!r})")
		if not ID_PATTERN.match(entry["id"]):
			problems.append(f"{where}: id {entry['id']!r} is not lowercase words of [a-z0-9] joined by '-'")
		if entry["id"] in ids:
			problems.append(f"{where}: id {entry['id']!r} also names entry {ids[entry['id']]}")
		ids.setdefault(entry["id"], number)
		for name in [entry["term"], *entry["aliases"]]:
			key = name.lower()
			if key in names:
				problems.append(f"{where}: the name {name!r} also names entry {names[key]} (one name per thing)")
			names.setdefault(key, number)
	for number, entry in checked:
		where = f"entry {number} ({entry['term']!r})"
		for name in entry["avoid"]:
			if name.lower() in names:
				problems.append(f"{where}: avoid name {name!r} is also the name of entry {names[name.lower()]}")

	# Homes and their order on track B.
	last = -1
	last_home = None
	for number, entry in checked:
		where = f"entry {number} ({entry['term']!r})"
		home = entry["home"]
		if home not in home_pages:
			problems.append(f"{where}: home {home!r} is not a page of part start or basics in the outline")
			continue
		if home not in position:
			problems.append(f"{where}: home {home!r} is not on track B, so B0 never reads the definition there")
			continue
		if position[home] < last:
			problems.append(f"{where}: home {home!r} comes before {last_home!r} on track B, but the entry stands after "
				"it: order the entries by home in the order of track B")
		else:
			last, last_home = position[home], home

	# Use homes.
	outline_pages = {page.id for page in outline.pages}
	for number, entry in checked:
		if "use" not in entry:
			continue
		if entry["use"] not in outline_pages:
			problems.append(f"entry {number} ({entry['term']!r}): use {entry['use']!r} is not a page of the outline")
		elif not entry["use"].startswith(USE_PART + "/"):
			problems.append(f"entry {number} ({entry['term']!r}): use {entry['use']!r} is not a page of part "
				f"`{USE_PART}`, where the use homes are (book.md, \"One home per concept\", rule 2)")

	# Definitions.
	patterns = []
	for index, (number, entry) in enumerate(checked):
		for name in [entry["term"], *entry["aliases"]]:
			patterns.append((index, name, name_pattern(name)))
	avoid_patterns = [(index, name, name_pattern(name.lower())) for index, (_, entry) in enumerate(checked)
		for name in entry["avoid"]]
	for index, (number, entry) in enumerate(checked):
		where = f"entry {number} ({entry['term']!r})"
		definition = entry["definition"]
		if not ONE_SENTENCE.match(definition):
			problems.append(f"{where}: the definition is not one sentence ending with a full stop (no '!' or '?', and "
				"no '.' before a space)")
		if words(definition) > MAX_WORDS:
			problems.append(f"{where}: the definition has {words(definition)} words; at most {MAX_WORDS}")
		for name in [entry["term"], *entry["aliases"]]:
			match = name_pattern(name).search(definition)
			if match:
				problems.append(f"{where}: the definition holds its own name {name!r} ({match.group(0)!r})")
		own = position.get(entry["home"])
		if own is None:
			continue
		for start, end, other, name in find_names(definition, patterns):
			if other == index:
				continue
			other_number, other_entry = checked[other]
			other_position = position.get(other_entry["home"])
			if other_position is not None and other_position > own:
				problems.append(f"{where}: the definition uses {definition[start:end]!r} (entry {other_number}, "
					f"{other_entry['term']!r}), whose home {other_entry['home']!r} comes later on track B than "
					f"{entry['home']!r}")
		for _, name, pattern in avoid_patterns:
			match = pattern.search(definition)
			if match:
				problems.append(f"{where}: the definition uses the avoid name {match.group(0)!r}")

	for problem in problems:
		print(problem)
	if args.counts:
		counts = {}
		for _, entry in checked:
			counts[entry["home"]] = counts.get(entry["home"], 0) + 1
		for page_id in track:
			if page_id in counts:
				print(f"{counts[page_id]:4d}  {page_id}")
		for page_id in sorted(set(counts) - set(track)):
			print(f"{counts[page_id]:4d}  {page_id} (not on track B)")
		print(f"{len(entries):4d}  entries")
	if problems:
		print(f"{len(problems)} problems", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())

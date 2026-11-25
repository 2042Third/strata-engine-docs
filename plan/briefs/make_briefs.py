"""Writes one brief per page of the outline into plan/briefs/<part>/<page>.md, and plan/briefs/index.json.

A brief is what the page's writer reads first: the outline's row, the page's section of its unit's file of
plan/allocation/ (Covers, the items it is home of or uses, Assumes, Fit), the terms src/content/glossary.json homes on
the page (its entries whose home or use is the page: id, term, aliases; rulings-11.md, R54), and the open findings of
the unit's completeness critic that name the page. The script only copies; it decides nothing. Run it again after the
plan or the glossary changes: python -I plan/briefs/make_briefs.py
"""

import io
import json
import os
import re
import sys

c_Plan = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c_Row = re.compile(r"^\| `([a-z0-9-]+/[a-z0-9-]+)` \| (.*?) \| ([A-Z]) \| ([A-Z]+) \| (.*?) \| (.*?) \| (.*) \|\s*$")
c_Heading = re.compile(r"^## `([a-z0-9-]+/[a-z0-9-]+)`")
c_Wave = [
	(1, ["start", "basics", "core", "world"]),
	(2, ["gpu"]),
	(3, ["assets"]),
	(4, ["draw", "light", "image", "physics", "audio", "input"]),
	(5, ["indirect", "animation", "scripting", "ui", "worlds", "editor"]),
	(6, ["editor-ui", "automation", "engineering", "capstone"]),
]


def read(path):
	with io.open(path, "r", encoding="utf-8", newline="") as handle:
		return handle.read().replace("\r\n", "\n")


def read_outline():
	pages = []
	for number in (1, 2, 3, 4):
		for line in read(os.path.join(c_Plan, "outline-%d.md" % number)).split("\n"):
			match = c_Row.match(line)
			if match:
				page, title, kind, size, tracks, needs, source = match.groups()
				pages.append({
					"id": page, "title": title, "kind": kind, "size": size, "tracks": tracks, "needs": needs,
					"from": source, "w8": source.rstrip().endswith("· W8"),
				})
	return pages


def read_units():
	sections = {}
	folder = os.path.join(c_Plan, "allocation")
	for name in sorted(os.listdir(folder)):
		if not name.endswith(".md") or name in ("README.md", "coverage.md", "completeness.md"):
			continue
		unit = name[:-3]
		current, lines = None, []
		for line in read(os.path.join(folder, name)).split("\n"):
			if line.startswith("## "):
				if current:
					sections[current] = (unit, "\n".join(lines).rstrip() + "\n")
				match = c_Heading.match(line)
				current, lines = (match.group(1) if match else None), [line]
			elif current:
				lines.append(line)
		if current:
			sections[current] = (unit, "\n".join(lines).rstrip() + "\n")
	return sections


def read_findings():
	found = {}
	folder = os.path.join(c_Plan, "allocation", "completeness")
	units = ("start", "make-a", "make-b1", "make-b2", "make-c", "basics-a", "basics-b", "capstone", "reference", "appendix")
	for unit in units:
		path = os.path.join(folder, unit + ".md")
		if not os.path.exists(path):
			continue
		for line in read(path).split("\n"):
			if line.startswith("| critic-" + unit + "-"):
				found.setdefault(unit, []).append(line)
	return found


def read_glossary():
	"""Page id -> the glossary's entries whose home or use home is the page, in the glossary's order."""
	path = os.path.join(os.path.dirname(c_Plan), "src", "content", "glossary.json")
	homed = {}
	for entry in json.loads(read(path))["terms"]:
		for field in ("home", "use"):
			if entry.get(field):
				homed.setdefault(entry[field], []).append((entry, field))
	return homed


def cell(text):
	return text.replace("|", "\\|")


def terms_section(entries):
	"""The brief's list of the terms the glossary homes on the page (rulings-11.md, R54)."""
	text = [
		"## Terms the glossary homes on this page",
		"",
		"From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says",
		"what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above",
		"disagree, the glossary's home wins.",
		"",
	]
	if not entries:
		return text + ["None: the glossary homes no term on this page.", ""]
	text += ["| Id | Term | Aliases |", "| --- | --- | --- |"]
	for entry, field in entries:
		term = entry["term"] + (" (use)" if field == "use" else "")
		text.append("| `%s` | %s | %s |" % (entry["id"], cell(term), cell(", ".join(entry.get("aliases") or [])) or "-"))
	return text + [""]


def wave_of(page, block_of_make):
	part = page["id"].split("/")[0]
	if page["w8"] or part in ("reference", "appendix"):
		return "B"
	if part == "make":
		return {"make-a": 2, "make-b1": 3, "make-b2": 3, "make-c": 5}.get(block_of_make, 3)
	for wave, parts in c_Wave:
		if part in parts:
			return wave
	return 6


def main():
	pages = read_outline()
	sections = read_units()
	findings = read_findings()
	glossary = read_glossary()
	missing = [page["id"] for page in pages if page["id"] not in sections]
	if missing:
		print("no section in a unit's file: " + ", ".join(missing))
		return 1
	index = []
	for page in pages:
		unit, section = sections[page["id"]]
		rows = [row for row in findings.get(unit, []) if "`" + page["id"] + "`" in row]
		part, name = page["id"].split("/")
		folder = os.path.join(c_Plan, "briefs", part)
		os.makedirs(folder, exist_ok=True)
		text = [
			"# Brief: `%s`" % page["id"],
			"",
			"| Field | Value |",
			"| --- | --- |",
			"| Title | %s |" % page["title"],
			"| Kind | %s |" % page["kind"],
			"| Size | %s |" % page["size"],
			"| Tracks | %s |" % page["tracks"],
			"| Needs | %s |" % page["needs"],
			"| From | %s |" % page["from"],
			"| Unit | `plan/allocation/%s.md` |" % unit,
			"",
			"An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.",
			"",
			section,
		] + terms_section(glossary.get(page["id"], []))
		if rows:
			text += [
				"## Open findings of the completeness critic that name this page",
				"",
				"Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it",
				"did not apply, with the reason.",
				"",
				"| Id | Severity | Kind | Where | Finding | Proposal | Evidence |",
				"| --- | --- | --- | --- | --- | --- | --- |",
			] + rows + [""]
		path = os.path.join(folder, name + ".md")
		with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
			handle.write("\n".join(text))
		index.append({
			"id": page["id"], "title": page["title"], "kind": page["kind"], "size": page["size"], "unit": unit,
			"wave": wave_of(page, unit), "findings": len(rows), "bytes": os.path.getsize(path),
		})
	with io.open(os.path.join(c_Plan, "briefs", "index.json"), "w", encoding="utf-8", newline="\n") as handle:
		json.dump(index, handle, indent=1)
		handle.write("\n")
	waves = {}
	for entry in index:
		waves[entry["wave"]] = waves.get(entry["wave"], 0) + 1
	print("%d briefs; pages per wave: %s; largest %d bytes" % (len(index), sorted(waves.items(), key=str), max(entry["bytes"] for entry in index)))
	return 0


sys.exit(main())

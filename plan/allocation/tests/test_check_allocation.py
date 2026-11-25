"""Tests of plan/allocation/check_allocation.py on small made-up plans in temporary folders.

Run: python -m unittest discover -s plan/allocation/tests -v
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_allocation as ca  # noqa: E402

OUTLINE = """# Outline 1

## Part 0 — Alpha (`alpha`)

Tracks: E.

Needs of the part: -

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `alpha/intro` | Intro | C | M | E | - | new |
| `alpha/tutorial` | Tutorial | T | M | E | `alpha/intro` | new |
| `alpha/howto` | How-to | H | S | E | `alpha/tutorial` | new |

## Part 1 — Beta (`beta`)

Tracks: E.

Needs of the part: `alpha/intro`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `beta/basics` | Basics | C | L | E | `alpha/intro` | new |
| `beta/deep` | Deep | I | M | E | `beta/basics` | new |
| `beta/side` | Side | C | S | E | `alpha/howto`\\|`beta/basics` | new |

## Part 2 — Gamma (`gamma`)

Tracks: -.

Needs of the part: -

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `gamma/ref` | Reference | R | S | - | - | new |

## Part 3 — Basics (`basics`)

Tracks: E.

Needs of the part: -

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/primer` | Primer | P | M | E | - | new |

## Part 4 — Make (`make`)

Tracks: E.

Needs of the part: -

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/recipe` | Recipe | H | S | E | - | new |
"""

TRACKS = """# Tracks

## Track G: the game maker

## Track B: the beginner

## Track E: the engine builder

1. `alpha/intro`
2. `alpha/tutorial`
3. `alpha/howto`
4. `beta/basics`
5. `beta/deep`
6. `beta/side`
7. `basics/primer`
8. `make/recipe`
"""

# The line numbers matter: the tests name items by them.
INVENTORY_A = """# Inventory: A

Preamble with a list:

- DG = a document

## 1. Features

### 1.1 Things

| Feature | What |
| --- | --- |
| **Alpha thing** | first |
| Beta thing | second, with `a|b` in code |

### 1.2 Listed

- **Gamma feature**: listed.
  continued line
- Delta feature without a bold lead whose text is long enough to be cut at one hundred characters, as it goes on

### 1.3 Prose

The first paragraph of prose, a feature.
It continues here.

The second paragraph.

### How completeness was checked

- Every file read.

## 2. Concepts to teach

Each concept: an introduction.

1. **Concept one.** Text
   more text.

   A second paragraph of the entry.
2. **Concept two.** Text.

## 3. Code worth showing

| # | File and lines | What |
| --- | --- | --- |
| 1 | `src/a.cpp` 1-3 | A |
| E2 | `src/b.cpp` 4-5 | B |

Shorter snippets: `src/c.cpp` 1-2.

## 4. Figures

### Diagrams

1. **Diagram one** (flow): text.

## 5. Rules and pitfalls

1. **Rule one.** Why.

## 6. Hands-on

| # | Task |
| --- | --- |
| G1 | Do it |

## 7. Glossary

- **Term one:** a term; **second term**: defined inside it.
- **Term two:** another.

## 8. Proposed chapters

1. **Chapter** (concept).

## 9. Not determined

- Not read: x.
"""

INVENTORY_B = """# Inventory: B

## 1. Features

| Feature | What |
| --- | --- |
| B one | x |
| B two | y |
| B three | z |

## 3. Code worth showing

| # | File | What |
| --- | --- | --- |
| 1 | `src/x.cpp` 1-2 | X |

## 7. Glossary

- **B term:** t.
"""

INVENTORY_R = """# Inventory: R

## 1. Features

- **R one**: x.
- **R two**: y.
"""

UNIT_A = """# Allocation: ua

## `alpha/intro` — Intro

**Covers.** The intro.

**Leaves out.**

- The deep part → `beta/deep`

**Fit.** `fits`: about 2,900 words against M (3,000). It fits.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `inva:13-20` | feature | home | The features |
| `inva:47` | code | home | `src/a.cpp:1-3`: the first excerpt |
| `new:1` | not-done | home | Nothing of the kind. Evidence: `Docs/Roadmap.md:1` |
| `new:2` | concept | home | Binary numbers. General knowledge. |
| `invr:5` | feature | home | R one, passed by the router |

**Assumes.**

none

## `alpha/tutorial` — Tutorial

**Covers.** Steps.

**Leaves out.**

none

**Fit.** `under`: about 2,000 words against M (3,000). It could take the how-to's first steps.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `inva:24`, `inva:27` | feature | home | The prose |
| `inva:37-41` | concept | home | Both concepts |
| `inva:56` | figure | home | The diagram |
| `new:1` | not-done | use | The missing thing |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The intro | `alpha/intro` | must |

**Starting state.** An empty project.

**Command-only steps.** none

## `alpha/howto` — How-to

**Covers.** A task.

**Leaves out.**

none

**Fit.** `over`: about 2,400 words against S (1,500). Make it M.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `inva:60` | rule | home | The rule |
| `inva:66` | hands-on | home | The exercise |
| `inva:70`, `inva:71` | term | home | The terms |

**Assumes.**

none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `inva:48` | code | `beta/basics` | Shown with the basics |
| `inva:50` | code | `gamma/ref` | A reference |
| `inva:79` | open | `nowhere` | A note about files the survey did not read |

## Not taken

none

## Questions for the planner

- Is the how-to too long?
"""

UNIT_B = """# Allocation: ub

## `beta/basics` — Basics

**Covers.** Basics.

**Leaves out.**

none

**Fit.** `fits`: about 4,900 words against L (5,000). It fits.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `invb:7-9` | feature | home | All features of B |
| `inva:48` | code | home | `src/b.cpp:4-5`: excerpt B |
| `invb:15` | code | home | `src/x.cpp:1-2`: excerpt X |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The intro | `alpha/intro` | must |
| Tutorial steps | `alpha/tutorial` | must |
| Something unknown | ? | helps |

## `beta/deep` — Deep

**Covers.** Depth.

**Leaves out.**

none

**Fit.** `fits`: about 2,900 words against M (3,000). It fits.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `invb:19` | term | home | The term |

**Assumes.**

none

## `beta/side` — Side

**Covers.** A side page.

**Leaves out.**

none

**Fit.** `fits`: about 1,400 words against S (1,500). It fits.

**Items.**

none

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shared | `alpha/intro` | must |
| One alternative only | `alpha/tutorial` | must |
| Later | `beta/deep` | must |

## Passed on

none

## Not taken

| Item | Passed by | Why not | Better page |
| --- | --- | --- | --- |
| `invr:6` | `router` | Not this part's subject | `alpha/howto` |

## Questions for the planner

none
"""

UNIT_C = """# Allocation: uc

## `gamma/ref` — Reference

**Covers.** Reference.

**Leaves out.**

none

**Fit.** `fits`: about 1,400 words against S (1,500). It fits.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `inva:50` | code | home | `src/c.cpp:1-2`: the shorter snippet |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Depth | `beta/deep` | must |

## Passed on

none

## Not taken

none

## Questions for the planner

none
"""

UNIT_D = """# Allocation: ud

## `basics/primer` — Primer

**Covers.** Binary numbers.

**Leaves out.**

none

**Fit.** `fits`: about 2,400 words against M (3,000). Binary numbers take the most words.

**Items.**

none

**Assumes.**

none

## `make/recipe` — Recipe

**Covers.** A recipe.

**Leaves out.**

none

**Fit.** `fits`: about 1,200 words against S (1,500). The steps take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | What a recipe is. General knowledge. |

**Assumes.**

none

## Passed on

none

## Not taken

none

## Questions for the planner

none
"""

UNIT_ROUTER = """# Allocation: router

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `invr:5` | feature | `alpha/intro` | The intro teaches it |
| `invr:6` | feature | `beta/side` | The side page |

## Questions for the planner

none
"""

TEST_UNITS = [
	("ua", [("alpha", None, None)], "inva"),
	("ub", [("beta", "beta/basics", "beta/deep"), ("beta", "beta/side", "beta/side")], "invb"),
	("uc", [("gamma", None, None)], None),
	("ud", [("basics", None, None), ("make", None, None)], None),
	("router", [], "invr"),
]
TEST_EXCLUDED = [("inva", "How completeness was checked", "a note")]
TEST_PARAGRAPH_BLOCKS = [("inva", "1.3 Prose", "prose")]
TEST_PARAGRAPH_ITEMS = [("inva", "3. Code worth showing", "Shorter snippets:", "code outside the table")]
ENGINE_FILES = {"src/a.cpp": 3, "src/b.cpp": 5, "src/x.cpp": 2, "src/c.cpp": 2}


def run(*argv):
	"""Run the script's main with arguments; return (exit code, stdout, stderr)."""
	out = io.StringIO()
	err = io.StringIO()
	with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
		code = ca.main(list(argv))
	return code, out.getvalue(), err.getvalue()


class PlanTest(unittest.TestCase):
	"""A made-up plan: an outline of five parts, three inventories, five units and their files."""

	def setUp(self):
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.root = Path(folder.name)
		for name, value in (("UNITS", TEST_UNITS), ("EXCLUDED_BLOCKS", TEST_EXCLUDED),
				("PARAGRAPH_BLOCKS", TEST_PARAGRAPH_BLOCKS), ("PARAGRAPH_ITEMS", TEST_PARAGRAPH_ITEMS),
				("HEADING_ITEM_SECTIONS", []), ("NESTED_ITEMS", [])):
			patcher = mock.patch.object(ca, name, value)
			patcher.start()
			self.addCleanup(patcher.stop)
		self.write("outline-1.md", OUTLINE)
		self.write("tracks.md", TRACKS)
		self.write("inventory/inva.md", INVENTORY_A)
		self.write("inventory/invb.md", INVENTORY_B)
		self.write("inventory/invr.md", INVENTORY_R)
		self.write("allocation/ua.md", UNIT_A)
		self.write("allocation/ub.md", UNIT_B)
		self.write("allocation/uc.md", UNIT_C)
		self.write("allocation/ud.md", UNIT_D)
		self.write("allocation/router.md", UNIT_ROUTER)
		code, _, _ = run("items", "--plan", str(self.root))
		self.assertEqual(code, 0)

	def write(self, relative, text):
		path = self.root / relative
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_bytes(text.encode("utf-8"))

	def read(self, relative):
		return (self.root / relative).read_bytes().decode("utf-8")

	def change(self, relative, old, new):
		text = self.read(relative)
		self.assertIn(old, text)
		self.write(relative, text.replace(old, new, 1))

	def plan(self):
		return ca.Plan(self.root)

	def problems(self, unit=None):
		return ca.run_check(self.plan(), unit)

	def warnings(self, unit=None):
		return ca.run_warnings(self.plan(), unit)

	def assertProblem(self, problems, *parts):
		found = [problem for problem in problems if all(part in problem for part in parts)]
		self.assertTrue(found, f"no problem with {parts} in:\n" + "\n".join(problems))

	def problems_after(self, unit, old, new):
		self.change(f"allocation/{unit}.md", old, new)
		return self.problems(unit)


class ItemFinderTest(PlanTest):
	def items(self, name="inva"):
		return {item.line: item for item in self.plan().inventories[name].items}

	def test_table_block_gives_a_row_per_data_row(self):
		items = self.items()
		self.assertEqual(items[13].label, "Alpha thing")
		self.assertEqual(items[14].label, "Beta thing")
		self.assertEqual(items[13].type, "feature")
		self.assertEqual(items[13].heading, "1.1 Things")
		self.assertNotIn(11, items)  # the header row
		self.assertNotIn(12, items)  # the separator

	def test_list_entries_with_continuations(self):
		items = self.items()
		self.assertEqual(items[18].label, "Gamma feature")
		self.assertEqual(items[18].end, 19)
		self.assertTrue(items[20].label.startswith("Delta feature without a bold lead"))
		self.assertLessEqual(len(items[20].label), 100)
		self.assertTrue(items[20].label.endswith("…"))

	def test_entry_continues_after_a_blank_line_when_indented(self):
		items = self.items()
		self.assertEqual(items[37].label, "Concept one")
		self.assertEqual(items[37].end, 40)
		self.assertEqual(items[41].label, "Concept two")
		self.assertEqual(items[37].type, "concept")

	def test_paragraph_block(self):
		items = self.items()
		self.assertEqual(items[24].end, 25)
		self.assertEqual(items[24].label, "The first paragraph of prose, a feature. It continues here.")
		self.assertEqual(items[27].label, "The second paragraph.")

	def test_excluded_block(self):
		inventory = self.plan().inventories["inva"]
		self.assertNotIn(31, inventory.by_line)
		self.assertEqual(inventory.excluded, [("How completeness was checked", 29, "a note")])

	def test_paragraph_item_and_plain_paragraphs(self):
		items = self.items()
		self.assertEqual(items[50].type, "code")
		self.assertEqual(items[50].heading, "")
		self.assertNotIn(35, items)  # an introduction is no item

	def test_short_first_cell_is_joined_with_the_second(self):
		items = self.items()
		self.assertEqual(items[47].label, "1: `src/a.cpp` 1-3")
		self.assertEqual(items[48].label, "E2: `src/b.cpp` 4-5")
		self.assertEqual(items[66].label, "G1: Do it")

	def test_types_follow_the_sections(self):
		items = self.items()
		self.assertEqual((items[56].type, items[56].heading), ("figure", "Diagrams"))
		self.assertEqual(items[60].type, "rule")
		self.assertEqual(items[66].type, "hands-on")
		self.assertEqual(items[70].type, "term")
		self.assertEqual(items[79].type, "open")
		self.assertNotIn(5, items)  # the preamble is in no section
		self.assertNotIn(75, items)  # section 8 holds no items
		self.assertEqual(sorted(items), [13, 14, 18, 20, 24, 27, 37, 41, 47, 48, 50, 56, 60, 66, 70, 71, 79])

	def test_a_glossary_entry_with_a_second_bold_term_is_one_item_that_names_both(self):
		items = self.items()
		self.assertEqual(items[70].label, "Term one; second term")  # the glossary must see the second term too
		self.assertEqual(items[71].label, "Term two")
		self.assertEqual(sum(1 for item in items.values() if item.type == "term"), 2)
		self.assertEqual(ca.term_label("**Nit (cd/m^2)**: luminance. **Lux**: illuminance. **Candela**: intensity."),
			"Nit (cd/m^2); Lux; Candela")
		self.assertEqual(ca.term_label("A term without bold, defined in words"), "A term without bold, defined in words")

	def test_only_glossary_entries_name_every_bold_term(self):
		text = "# X\n\n## 5. Rules\n\n1. **Rule one.** Why: **never** do it.\n"
		inventory = ca.find_items("invz", text)
		self.assertEqual([item.label for item in inventory.items], ["Rule one"])

	def test_split_cells(self):
		self.assertEqual(ca.split_cells("| a | `b|c` | d |"), ["a", "`b|c`", "d"])
		self.assertEqual(ca.split_cells("| a \\| b | c |"), ["a | b", "c"])
		self.assertEqual(ca.split_cells("| a | |"), ["a", ""])
		self.assertEqual(ca.split_cells("| a `b | c |"), ["a `b", "c"])

	def test_heading_items(self):
		text = ("# X\n\n## 2. Concepts to teach\n\nAn introduction.\n\n### 2.1 One\n\n- **Problem.** p\n- **Strata.** s\n\n"
			"### 2.2 Two\n\n- **Problem.** q\n")
		with mock.patch.object(ca, "HEADING_ITEM_SECTIONS", [("invh", 2, "concepts as headings")]):
			inventory = ca.find_items("invh", text)
		self.assertEqual([(item.line, item.label, item.type) for item in inventory.items],
			[(7, "2.1 One", "concept"), (12, "2.2 Two", "concept")])
		self.assertEqual(inventory.problems, [])

	NESTED = ("# X\n\n## 1. Features\n\n### 1.1 Parts\n\n"  # lines 1-5
		"- **Plain feature**: one item.\n"  # 7
		"- **Whole feature**:\n"  # 8
		"  - Part one: text\n"  # 9
		"    continued.\n"  # 10
		"  - Part two\n"  # 11
		"    - a detail of part two\n"  # 12
		"  - Part three: the docs.\n"  # 13
		"- **After**: x.\n")  # 14

	def test_nested_entries_of_a_named_entry_are_items(self):
		with mock.patch.object(ca, "NESTED_ITEMS", [("invn", "1.1 Parts", "**Whole feature**", "parts")]):
			inventory = ca.find_items("invn", self.NESTED)
		self.assertEqual(inventory.problems, [])
		found = [(item.line, item.end, item.label, item.type, item.heading) for item in inventory.items]
		self.assertEqual(found, [
			(7, 7, "Plain feature", "feature", "1.1 Parts"),
			(8, 8, "Whole feature", "feature", "1.1 Parts"),  # the entry keeps its id and ends before its first part
			(9, 10, "Part one: text continued.", "feature", "1.1 Parts"),
			(11, 12, "Part two - a detail of part two", "feature", "1.1 Parts"),  # a deeper entry continues its part
			(13, 13, "Part three: the docs.", "feature", "1.1 Parts"),
			(14, 14, "After", "feature", "1.1 Parts"),
		])
		self.assertEqual(inventory.item_at(10).line, 9)

	def test_nested_entries_without_a_rule_are_a_problem(self):
		inventory = ca.find_items("invn", self.NESTED)
		self.assertEqual(inventory.problems, ["inventory/invn.md:8: the entry holds 3 entries nested under it, which one "
			"item would hide: name it in NESTED_ITEMS, so that each nested entry is an item of its own"])
		self.assertEqual([item.line for item in inventory.items], [7, 8, 14])  # one item, as before the rule
		self.assertEqual(inventory.by_line[8].end, 13)

	def test_nested_items_must_name_an_entry_with_nested_entries(self):
		rules = [("invn", "1.1 Parts", "**Plain feature**", "none nested"), ("invn", "1.1 Parts", "**Missing**", "gone"),
			("invn", "1.9 Gone", "**Whole feature**", "no block")]
		with mock.patch.object(ca, "NESTED_ITEMS", rules):
			inventory = ca.find_items("invn", self.NESTED)
		problems = "\n".join(inventory.problems)
		self.assertIn("inventory/invn.md:7: NESTED_ITEMS names the entry '**Plain feature**', but no entry is nested "
			"under it", problems)
		self.assertIn("inventory/invn.md:5: NESTED_ITEMS names the entry '**Missing**' of this block; the block holds 0 "
			"entries that start so, not one", problems)
		self.assertIn("names the block '1.9 Gone', which is the heading of 0 blocks", problems)
		self.assertIn("inventory/invn.md:8: the entry holds 3 entries nested under it", problems)

	def test_items_reports_nested_entries_without_a_rule(self):
		self.write("inventory/invb.md", INVENTORY_B + "\n## 9. Not determined\n\n- Drift found:\n  - one\n  - two\n")
		code, out, err = run("items", "--plan", str(self.root))
		self.assertEqual(code, 1)
		self.assertIn("inventory/invb.md:23: the entry holds 2 entries nested under it", out)
		self.assertProblem(self.problems(), "inventory/invb.md:23", "nested")

	def test_shapes_without_a_rule_are_problems(self):
		text = ("# X\n\n## 1. Features\n\n### 1.1 Mixed\n\n| A | B |\n| --- | --- |\n| a | b |\n\n- an entry\n\n"
			"### 1.2 No separator\n\n| A | B |\n| a | b |\n\n### 1.3 Prose\n\nJust prose.\n")
		with mock.patch.object(ca, "EXCLUDED_BLOCKS", [("invx", "1.9 Gone", "stale")]):
			inventory = ca.find_items("invx", text)
		problems = "\n".join(inventory.problems)
		self.assertIn("inventory/invx.md:5: the block holds a table and a list", problems)
		self.assertIn("inventory/invx.md:15: a table without a header row and a separator row", problems)
		self.assertIn("inventory/invx.md:18: the block holds only paragraphs", problems)
		self.assertIn("names the block '1.9 Gone', which is the heading of 0 blocks", problems)

	def test_items_writes_the_lists_and_the_hashes(self):
		tsv = self.read("allocation/items/inva.tsv").splitlines()
		self.assertEqual(tsv[0], "id\ttype\theading\tlabel")
		self.assertEqual(tsv[1], "inva:13\tfeature\t1.1 Things\tAlpha thing")
		self.assertEqual(len(tsv), 18)
		hashes = self.read("allocation/items/inventories.sha256").splitlines()
		self.assertEqual([line.split()[1] for line in hashes], ["inva.md", "invb.md", "invr.md"])
		before = self.read("allocation/items/inva.tsv")
		code, out, _ = run("items", "--plan", str(self.root))
		self.assertEqual(code, 0)
		self.assertEqual(self.read("allocation/items/inva.tsv"), before)
		self.assertIn("inva", out)
		self.assertIn("total", out)

	def test_items_reports_a_shape_without_a_rule(self):
		self.write("inventory/invb.md", INVENTORY_B + "\n## 9. Not determined\n\nOnly prose here.\n")
		code, out, err = run("items", "--plan", str(self.root))
		self.assertEqual(code, 1)
		self.assertIn("inventory/invb.md:21: the block holds only paragraphs", out)
		self.assertIn("1 problems", err)

	def test_check_fails_when_an_inventory_changes(self):
		self.assertEqual(self.problems(), [])
		self.write("inventory/inva.md", INVENTORY_A + "- Another open entry.\n")
		problems = self.problems()
		self.assertProblem(problems, "inventory/inva.md", "SHA-256")
		self.assertProblem(problems, "allocation/items/inva.tsv", "differs")


class RangeTest(PlanTest):
	def resolve(self, text):
		ref = ca.Ref(text)
		match = ca.INVENTORY_ID.match(text)
		ref.inventory, ref.first = match.group(1), int(match.group(2))
		ref.last = int(match.group(3) or match.group(2))
		ref.is_range = match.group(3) is not None
		return self.plan().resolve(ref)

	def test_a_range_names_every_item_that_starts_in_it(self):
		items, message = self.resolve("inva:13-20")
		self.assertIsNone(message)
		self.assertEqual([item.line for item in items], [13, 14, 18, 20])

	def test_a_range_without_an_item(self):
		self.assertIn("no item starts on lines 21 to 23", self.resolve("inva:21-23")[1])

	def test_a_range_of_two_types(self):
		self.assertIn("several types", self.resolve("inva:41-47")[1])

	def test_a_range_backwards(self):
		self.assertIn("runs backwards", self.resolve("inva:20-13")[1])

	def test_an_id_inside_an_item(self):
		self.assertIn("lies inside `inva:18`", self.resolve("inva:19")[1])

	def test_an_unknown_inventory(self):
		self.assertIn("names no inventory", self.resolve("nosuch:1")[1])

	def test_ranges_in_a_unit_file(self):
		problems = self.problems_after("ua", "| `inva:56` | figure |", "| `inva:56-58` | figure |")
		self.assertEqual(problems, [])
		problems = self.problems_after("ua", "| `inva:56-58` | figure |", "| `inva:52-60` | figure |")
		self.assertProblem(problems, "allocation/ua.md:", "several types")


class FormatTest(PlanTest):
	def test_the_made_up_plan_is_clean(self):
		self.assertEqual(self.problems(), [])

	# Rule 1

	def test_rule1_missing_page_section(self):
		text = self.read("allocation/ua.md")
		start = text.index("## `alpha/howto`")
		self.write("allocation/ua.md", text[:start] + text[text.index("## Passed on"):])
		self.assertProblem(self.problems("ua"), "no section for `alpha/howto`")

	def test_rule1_order(self):
		text = self.read("allocation/ua.md")
		intro = text[text.index("## `alpha/intro`"):text.index("## `alpha/tutorial`")]
		tutorial = text[text.index("## `alpha/tutorial`"):text.index("## `alpha/howto`")]
		self.write("allocation/ua.md", text.replace(intro + tutorial, tutorial + intro))
		self.assertProblem(self.problems("ua"), "`alpha/tutorial` stands where the outline's order puts `alpha/intro`")

	def test_rule1_page_of_another_unit(self):
		problems = self.problems_after("ua", "## Passed on", "## `beta/deep` — Deep\n\n## Passed on")
		self.assertProblem(problems, "`beta/deep` is a page of `ub`, not of `ua`")

	def test_rule1_second_section(self):
		text = self.read("allocation/uc.md")
		section = text[text.index("## `gamma/ref`"):text.index("## Passed on")]
		self.write("allocation/uc.md", text.replace(section, section + section))
		problems = self.problems("uc")
		self.assertProblem(problems, "a second section for `gamma/ref`")
		self.assertEqual(len(self.plan().file("uc").item_rows), 1)  # the second section is not read

	def test_rule1_generated_page(self):
		problems = self.problems_after("ua", "## Passed on", "## `alpha/index` — Index\n\n## Passed on")
		self.assertProblem(problems, "`alpha/index` is a generated page")

	def test_rule1_unknown_section_and_missing_file_section(self):
		problems = self.problems_after("uc", "## Not taken\n\nnone\n", "## Notes\n\nnone\n")
		self.assertProblem(problems, "section 'Notes' is no page")
		self.assertProblem(problems, "no `## Not taken` section")

	def test_rule1_title(self):
		self.assertProblem(self.problems_after("uc", "# Allocation: uc", "# Allocation: other"),
			"the title names `other`, not `uc`")

	def test_unit_without_pages(self):
		problems = self.problems_after("router", "## Questions", "## Not taken\n\nnone\n\n## Questions")
		self.assertProblem(problems, "a unit without pages has only Passed on and Questions for the planner")

	# Rule 2

	def test_rule2_missing_part(self):
		problems = self.problems_after("uc", "**Assumes.**", "Assumes.")
		self.assertProblem(problems, "`gamma/ref` has no **Assumes.**")

	def test_rule2_order(self):
		problems = self.problems_after("uc", "**Leaves out.**\n\nnone\n\n**Fit.** `fits`: about 1,400 words against S "
			"(1,500). It fits.", "**Fit.** `fits`: about 1,400 words against S (1,500). It fits.\n\n**Leaves out.**\n\nnone")
		self.assertProblem(problems, "**Leaves out.** comes after **Fit.**")

	def test_rule2_full_stop_inside_the_bold(self):
		self.assertProblem(self.problems_after("uc", "**Covers.** Reference.", "**Covers**. Reference."),
			"write `**Covers.**`")

	def test_rule2_tutorial_needs_its_step_parts(self):
		problems = self.problems_after("ua", "**Command-only steps.** none", "")
		self.assertProblem(problems, "`alpha/tutorial` is a tutorial (T) and has no **Command-only steps.**")

	def test_rule2_how_to_has_both_step_parts_or_none(self):
		problems = self.problems_after("ua", "**Assumes.**\n\nnone\n\n## Passed on",
			"**Assumes.**\n\nnone\n\n**Starting state.** A project.\n\n## Passed on")
		self.assertProblem(problems, "`alpha/howto` has **Starting state.** but no **Command-only steps.**")

	def test_rule2_other_kinds_have_no_step_parts(self):
		problems = self.problems_after("uc", "## Passed on", "**Starting state.** A project.\n\n## Passed on")
		self.assertProblem(problems, "`gamma/ref` is of kind R")

	PRIMER_END = "**Assumes.**\n\nnone\n\n## `make/recipe`"

	def test_rule2_a_primer_may_have_starting_state(self):
		self.assertEqual(self.problems("ud"), [])  # without it too
		problems = self.problems_after("ud", self.PRIMER_END,
			"**Assumes.**\n\nnone\n\n**Starting state.** The checkpoint of the practice item.\n\n## `make/recipe`")
		self.assertEqual(problems, [])

	def test_rule2_a_primer_has_no_command_only_steps(self):
		problems = self.problems_after("ud", self.PRIMER_END, "**Assumes.**\n\nnone\n\n**Starting state.** A checkpoint."
			"\n\n**Command-only steps.** none\n\n## `make/recipe`")
		self.assertEqual(len(problems), 1, problems)
		self.assertProblem(problems, "`basics/primer` is a primer (P): a primer may have **Starting state.**",
			"have **Command-only steps.**")
		problems = self.problems_after("ud", "**Starting state.** A checkpoint.\n\n", "")
		self.assertProblem(problems, "`basics/primer` is a primer (P)", "**Command-only steps.**")

	def test_rule2_a_primers_starting_state_is_not_empty(self):
		problems = self.problems_after("ud", self.PRIMER_END,
			"**Assumes.**\n\nnone\n\n**Starting state.**\n\n## `make/recipe`")
		self.assertEqual(len(problems), 1, problems)  # a primer may have it: only its emptiness is a problem
		self.assertProblem(problems, "**Starting state.** is empty")

	def test_rule2_empty_list_holds_none(self):
		problems = self.problems_after("uc", "**Leaves out.**\n\nnone", "**Leaves out.**\n\n")
		self.assertProblem(problems, "Leaves out is empty")

	def test_rule2_list_holds_entries(self):
		problems = self.problems_after("uc", "**Leaves out.**\n\nnone", "**Leaves out.**\n\nNothing at all.")
		self.assertProblem(problems, "Leaves out: a line that is no entry of the list")

	# Rule 3

	def test_rule3_unknown_item(self):
		problems = self.problems_after("ua", "| `inva:60` | rule |", "| `inva:61` | rule |")
		self.assertProblem(problems, "allocation/ua.md:", "no item starts at line 61")

	def test_rule3_type_must_be_the_items(self):
		problems = self.problems_after("ua", "| `inva:60` | rule |", "| `inva:60` | concept |")
		self.assertProblem(problems, "`inva:60` is of type rule; the Type cell says 'concept'")

	def test_rule3_role(self):
		problems = self.problems_after("ua", "| `inva:60` | rule | home |", "| `inva:60` | rule | `home` |")
		self.assertProblem(problems, "Role '`home`' is none of home, use, link")

	def test_rule3_item_cell(self):
		problems = self.problems_after("ua", "| `inva:60` | rule |", "| inva:60 | rule |")
		self.assertProblem(problems, "Item 'inva:60' is not ids in backquotes")

	def test_rule3_new_item_defined_twice(self):
		problems = self.problems_after("ua", "| `new:1` | not-done | use |", "| `new:1` | not-done | home |")
		self.assertProblem(problems, "`new:1` is defined twice")

	def test_rule3_new_item_keeps_its_type(self):
		problems = self.problems_after("ua", "| `new:1` | not-done | use |", "| `new:1` | erratum | use |")
		self.assertProblem(problems, "`new:1` is of type 'not-done'")

	def test_rule3_new_item_stands_alone(self):
		problems = self.problems_after("ua", "| `new:2` | concept |", "| `new:2`, `inva:41` | concept |")
		self.assertProblem(problems, "a new item stands alone in its row")

	def test_rule3_new_item_only_in_items(self):
		problems = self.problems_after("ua", "| `inva:79` | open |", "| `new:3` | open |")
		self.assertProblem(problems, "`new:3`: a new item belongs to the Items of its page")

	# Rule 4

	def test_rule4_code_home_names_one_item(self):
		problems = self.problems_after("ua", "| `inva:47` | code | home |", "| `inva:47-48` | code | home |")
		self.assertProblem(problems, "a home row of type code names one item, no range")

	def test_rule4_code_home_starts_with_its_place(self):
		problems = self.problems_after("ua", "`src/a.cpp:1-3`: the first excerpt", "the first excerpt, `src/a.cpp:1-3`")
		self.assertProblem(problems, "starts with the excerpt's place")

	def test_rule4_place_is_a_path_from_the_root(self):
		problems = self.problems_after("ua", "`src/a.cpp:1-3`", "`../src/a.cpp:1-3`")
		self.assertProblem(problems, "`../src/a.cpp` is not a path from the repository's root")

	def test_rule4_place_lines(self):
		self.assertProblem(self.problems_after("ua", "`src/a.cpp:1-3`", "`src/a.cpp:3-1`"), "the first not after the last")

	# Rule 5

	def test_rule5_new_item_states_its_evidence(self):
		problems = self.problems_after("ua", "Nothing of the kind. Evidence: `Docs/Roadmap.md:1`", "Nothing of the kind.")
		self.assertProblem(problems, "`new:1`: its last cell states its evidence")

	def test_rule5_engine_items_are_no_general_knowledge(self):
		problems = self.problems_after("ua", "Evidence: `Docs/Roadmap.md:1`", "General knowledge.")
		self.assertProblem(problems, "a new item of type not-done says something about Strata")

	def test_rule5_new_code_home_place_is_its_evidence(self):
		problems = self.problems_after("ua", "| `new:2` | concept | home | Binary numbers. General knowledge. |",
			"| `new:2` | code | home | `src/a.cpp:2-3`: a new excerpt |")
		self.assertEqual(problems, [])

	CHECK_ROW = ("| `new:3` | open | home | Check: Simulate and skinned meshes. The page states what the code shows. "
		"Evidence: `src/a.cpp:1-3` |\n")

	def test_rule5_a_check_before_writing(self):
		problems = self.problems_after("ua", "| `invr:5` | feature | home |",
			self.CHECK_ROW + "| `invr:5` | feature | home |")
		self.assertEqual(problems, [])
		self.assertEqual([(name, number, [row.page for row in rows]) for name, number, rows in
			self.plan().file("ua").check_items], [("Simulate and skinned meshes", 3, ["alpha/intro"])])

	def test_rule5_check_belongs_to_a_new_open_item(self):
		problems = self.problems_after("ua", "| `inva:60` | rule | home | The rule |", "| `inva:60` | rule | home | "
			"Check: The rule. |")
		self.assertProblem(problems, "allocation/ua.md:", "a last cell that starts with `Check:` belongs to a new item of "
			"type open")
		problems = self.problems_after("ua", "| `new:2` | concept | home | Binary numbers. General knowledge. |",
			"| `new:2` | concept | home | Check: Binary numbers. General knowledge. |")
		self.assertProblem(problems, "a last cell that starts with `Check:` belongs to a new item of type open")
		self.assertEqual(self.plan().file("ua").check_items, [])

	def test_rule5_check_names_its_check(self):
		problems = self.problems_after("ua", "| `invr:5` | feature | home |",
			"| `new:3` | open | home | Check: Evidence: `src/a.cpp:1-3` |\n| `invr:5` | feature | home |")
		self.assertProblem(problems, "write `Check: <the check's name>.`")
		self.assertEqual(self.plan().file("ua").check_items, [])

	# Rule 6

	def test_rule6_form(self):
		problems = self.problems_after("uc", "`fits`: about 1,400 words against S (1,500).", "fits about 1,400 words.")
		self.assertProblem(problems, "Fit starts with `fits`, `under` or `over`")

	def test_rule6_size_is_the_outlines(self):
		problems = self.problems_after("uc", "against S (1,500)", "against M (3,000)")
		self.assertProblem(problems, "Fit measures against M; the outline's size of `gamma/ref` is S")

	def test_rule6_words_of_the_size(self):
		self.assertProblem(self.problems_after("uc", "against S (1,500)", "against S (1,600)"),
			"size S is 1,500 words, not 1,600")

	def test_rule6_over_is_at_or_over_the_top_of_the_range(self):
		problems = self.problems_after("ua", "`over`: about 2,400 words", "`over`: about 2,000 words")
		self.assertProblem(problems, "allocation/ua.md:", "Fit says `over` with 2,000 words; against S's range of 600 to "
			"2,250 the state is `fits` (rule 6)")
		self.assertEqual(self.problems_after("ua", "`over`: about 2,000 words", "`over`: about 2,250 words"), [])

	def test_rule6_fits_is_inside_the_range_and_below_its_top(self):
		problems = self.problems_after("ua", "`fits`: about 2,900 words", "`fits`: about 4,000 words")
		self.assertProblem(problems, "Fit says `fits` with 4,000 words; against M's range of 2,251 to 4,000 the state is "
			"`over`")
		problems = self.problems_after("ua", "`fits`: about 4,000 words", "`fits`: about 2,250 words")
		self.assertProblem(problems, "Fit says `fits` with 2,250 words; against M's range of 2,251 to 4,000 the state is "
			"`under`")
		self.assertEqual(self.problems_after("ua", "`fits`: about 2,250 words", "`fits`: about 2,251 words"), [])
		self.assertEqual(self.problems_after("ua", "`fits`: about 2,251 words", "`fits`: about 3,999 words"), [])

	def test_rule6_under_is_below_the_bottom_of_the_range(self):
		problems = self.problems_after("ua", "`under`: about 2,000 words", "`under`: about 2,900 words")
		self.assertProblem(problems, "Fit says `under` with 2,900 words; against M's range of 2,251 to 4,000 the state is "
			"`fits`")
		problems = self.problems_after("ua", "`under`: about 2,900 words", "`under`: about 2,251 words")
		self.assertProblem(problems, "Fit says `under` with 2,251 words")
		self.assertEqual(self.problems_after("ua", "`under`: about 2,251 words", "`under`: about 2,250 words"), [])

	def test_rule_s_ranges(self):
		self.assertEqual(ca.RANGES, {"S": (600, 2250), "M": (2251, 4000), "L": (4001, 6500), "XL": (6501, 10000)})
		self.assertEqual(sorted(ca.RANGES), sorted(ca.WORDS))
		for size, (bottom, top) in ca.RANGES.items():
			self.assertTrue(bottom < ca.WORDS[size] < top, size)
		cases = [(599, "S", "under"), (600, "S", "fits"), (2249, "S", "fits"), (2250, "S", "over"),
			(2250, "M", "under"), (2251, "M", "fits"), (3999, "M", "fits"), (4000, "M", "over"), (4000, "L", "under"),
			(4001, "L", "fits"), (6500, "L", "over"), (6500, "XL", "under"), (6501, "XL", "fits"), (9999, "XL", "fits"),
			(10000, "XL", "over")]
		for words, size, state in cases:
			self.assertEqual(ca.fit_state(words, size), state, (words, size))

	def test_rule6_a_page_of_kind_r_fits_and_is_compared_with_nothing(self):
		for words in ("50", "1,500", "20,000"):
			self.change("allocation/uc.md", self.read("allocation/uc.md").split("**Fit.** ")[1].split(" against")[0],
				f"`fits`: about {words} words")
			self.assertEqual(self.problems("uc"), [], words)
			self.assertEqual(self.warnings("uc"), [], words)  # not even the budget to the word
		problems = self.problems_after("uc", "`fits`: about 20,000 words", "`under`: about 300 words")
		self.assertProblem(problems, "allocation/uc.md:", "Fit says `under`; a page of kind R has no size check, so its "
			"state is `fits` (rule 6)")
		problems = self.problems_after("uc", "`under`: about 300 words", "`over`: about 30,000 words")
		self.assertProblem(problems, "Fit says `over`; a page of kind R has no size check")

	def test_rule6_the_budget_to_the_word_warns(self):
		self.assertEqual(self.warnings(), [])
		problems = self.problems_after("ua", "`fits`: about 2,900 words", "`fits`: about 3,000 words")
		self.assertEqual(problems, [])
		warnings = self.warnings("ua")
		self.assertEqual(len(warnings), 1, warnings)
		self.assertRegex(warnings[0], r"^allocation/ua\.md:\d+: Fit states 3,000 words, M's budget to the word: count "
			r"the page again from its sections")
		self.assertEqual(self.warnings("ub"), [])

	def test_rule6_state(self):
		self.assertProblem(self.problems_after("uc", "`fits`: about 1,400", "`fit`: about 1,400"), "`fit` is none of")

	def test_rule6_a_sentence_follows(self):
		problems = self.problems_after("uc", "against S (1,500). It fits.", "against S (1,500).")
		self.assertProblem(problems, "one or two sentences follow the size")

	# Rule 7

	def test_rule7_teacher_is_a_page(self):
		problems = self.problems_after("uc", "| Depth | `beta/deep` | must |", "| Depth | `beta/deeper` | must |")
		self.assertProblem(problems, "Taught by `beta/deeper` is no page of the outline")

	def test_rule7_teacher_in_backquotes(self):
		problems = self.problems_after("uc", "| Depth | `beta/deep` | must |", "| Depth | beta/deep | must |")
		self.assertProblem(problems, "Taught by 'beta/deep' is a page id in backquotes or `?`")

	def test_rule7_not_the_page_itself(self):
		problems = self.problems_after("uc", "| Depth | `beta/deep` | must |", "| Depth | `gamma/ref` | must |")
		self.assertProblem(problems, "Taught by names the page itself")

	def test_rule7_depth(self):
		problems = self.problems_after("uc", "| Depth | `beta/deep` | must |", "| Depth | `beta/deep` | needed |")
		self.assertProblem(problems, "Depth 'needed' is none of must, helps")

	def test_rule7_header(self):
		problems = self.problems_after("uc", "| Concept | Taught by | Depth |", "| Concept | Teacher | Depth |")
		self.assertProblem(problems, "Assumes: the header is Concept | Teacher | Depth")

	# Rule 8

	def test_rule8_leaves_out_names_a_page(self):
		problems = self.problems_after("ua", "→ `beta/deep`", "→ `beta/deepest`")
		self.assertProblem(problems, "Leaves out names `beta/deepest`, which is no page of the outline")

	def test_rule8_leaves_out_has_an_arrow(self):
		self.assertProblem(self.problems_after("ua", "The deep part → `beta/deep`", "The deep part"),
			"an entry of Leaves out ends with `→`")

	def test_rule8_passed_on_names_a_page(self):
		problems = self.problems_after("ua", "| `inva:50` | code | `gamma/ref` |", "| `inva:50` | code | `gamma/refs` |")
		self.assertProblem(problems, "To `gamma/refs` is no page of the outline")

	def test_rule8_a_feature_is_never_nowhere(self):
		problems = self.problems_after("router", "| `invr:6` | feature | `beta/side` |", "| `invr:6` | feature | `nowhere` |")
		self.assertProblem(problems, "a feature of the engine is never `nowhere`")

	def test_rule8_not_to_the_units_own_page(self):
		problems = self.problems_after("ua", "| `inva:50` | code | `gamma/ref` |", "| `inva:50` | code | `alpha/howto` |")
		self.assertProblem(problems, "To `alpha/howto` is a page of `ua` itself")

	def test_not_taken_better_page(self):
		problems = self.problems_after("ub", "| `alpha/howto` |", "| alpha/howto |")
		self.assertProblem(problems, "Better page 'alpha/howto' is a page id in backquotes")


class WarningsTest(PlanTest):
	HOWTO_ROW = "| `inva:60` | rule | home | The rule |"

	def test_the_made_up_plan_has_no_warnings(self):
		self.assertEqual(self.warnings(), [])
		self.assertEqual(run("check", "--plan", str(self.root)), (0, "", ""))

	def test_a_concept_homed_on_a_how_to_outside_make(self):
		self.change("allocation/ua.md", self.HOWTO_ROW, self.HOWTO_ROW + "\n| `new:3` | concept | home | Why it works. "
			"General knowledge. |\n| `new:2` | concept | use | Binary numbers, used |")
		self.assertEqual(self.problems("ua"), [])
		warnings = self.warnings("ua")
		self.assertEqual(len(warnings), 1, warnings)  # a use row is no home
		self.assertRegex(warnings[0], r"^allocation/ua\.md:\d+: `new:3`: a concept homed on `alpha/howto`, a how-to "
			r"outside the parts `start` and `make`: move it to a concept or internals page, or say in the Fit line why")
		self.assertEqual(self.warnings("ud"), [])  # `make/recipe` homes a concept: a how-to of part make may

	def test_a_concept_homed_on_a_page_of_kind_r(self):
		problems = self.problems_after("uc", "| `inva:50` | code | home |", "| `new:1` | concept | home | A list of facts. "
			"General knowledge. |\n| `new:2` | feature | home | A helper's declaration. General knowledge. |\n"
			"| `inva:50` | code | home |")
		self.assertEqual(problems, [])
		warnings = self.warnings("uc")
		self.assertEqual(len(warnings), 1, warnings)  # a catalogue item of type feature is no concept
		self.assertRegex(warnings[0], r"^allocation/uc\.md:\d+: `new:1`: a concept homed on `gamma/ref`, a page of kind "
			r"R, which is the home only of catalogue items")

	def test_warnings_stand_under_their_own_heading_and_never_fail_the_check(self):
		self.change("allocation/ua.md", "`fits`: about 2,900 words", "`fits`: about 3,000 words")
		self.change("allocation/uc.md", "| `inva:50` | code | home |", "| `new:1` | concept | home | Facts. General "
			"knowledge. |\n| `inva:50` | code | home |")
		code, out, err = run("check", "--plan", str(self.root))
		self.assertEqual((code, err), (0, ""))
		lines = out.splitlines()
		self.assertEqual(lines[0], "Warnings (2), which do not fail the check:")
		self.assertRegex(lines[1], r"^allocation/ua\.md:\d+: Fit states 3,000 words")
		self.assertRegex(lines[2], r"^allocation/uc\.md:\d+: `new:1`: a concept homed on `gamma/ref`")
		self.assertEqual(len(lines), 3)
		code, out, _ = run("check", "--plan", str(self.root), "--unit", "uc")
		self.assertEqual(code, 0)
		self.assertEqual(out.splitlines()[0], "Warnings (1), which do not fail the check:")
		self.change("allocation/ub.md", "| The intro | `alpha/intro` | must |", "| The intro | `alpha/intro` | maybe |")
		code, out, err = run("check", "--plan", str(self.root))
		self.assertEqual(code, 1)
		self.assertIn("1 problems", err)
		lines = out.splitlines()
		self.assertIn("Depth 'maybe' is none of must, helps", lines[0])
		self.assertEqual(lines[1:3], ["", "Warnings (2), which do not fail the check:"])
		self.assertEqual(len(lines), 5)
		self.assertNotIn("Fit states", "\n".join(ca.run_check(self.plan())))  # a warning is never a problem


class ChecksTest(PlanTest):
	def add_checks(self):
		self.change("allocation/ua.md", "| `invr:5` | feature | home |", "| `new:3` | open | home | Check: Simulate and "
			"skinned meshes. The page states what the code shows. Evidence: `src/a.cpp:1-3` |\n| `invr:5` | feature | home |")
		self.change("allocation/ua.md", "| `new:1` | not-done | use | The missing thing |", "| `new:1` | not-done | use | "
			"The missing thing |\n| `new:3` | open | use | Check: Simulate and skinned meshes. Waits with the intro |")
		self.change("allocation/ub.md", "| `invb:19` | term | home | The term |", "| `invb:19` | term | home | The term |\n"
			"| `new:1` | open | home | Check: A capture step that opens the launcher's card. Evidence: `src/x.cpp:1-2` |\n"
			"| `new:2` | open | home | Not a check: no run settles it. Evidence: `src/x.cpp:1` |")

	def test_the_name_runs_to_the_first_full_stop_before_a_space(self):
		self.assertEqual(ca.CHECK_CELL.match("Check: `Process.h` and its pipes. Then more.").group(1),
			"`Process.h` and its pipes")
		self.assertEqual(ca.CHECK_CELL.match("Check: Simulate and skinned meshes.").group(1), "Simulate and skinned meshes")
		self.assertIsNone(ca.CHECK_CELL.match("Check: no full stop"))
		self.assertIsNone(ca.CHECK_CELL.match("Check: ."))

	def test_checks_prints_nothing_when_there_are_none(self):
		self.assertEqual(run("checks", "--plan", str(self.root)), (0, "", ""))

	def test_checks_lists_the_items_by_check_with_page_and_unit(self):
		self.add_checks()
		self.assertEqual(self.problems(), [])
		code, out, err = run("checks", "--plan", str(self.root))
		self.assertEqual((code, err), (0, ""))
		lines = out.splitlines()
		self.assertEqual(len(lines), 5, out)
		self.assertEqual(lines[0], "Check: A capture step that opens the launcher's card (1 page)")
		self.assertRegex(lines[1], r"^  `beta/deep` \(`ub`\): `new:1` home, allocation/ub\.md:\d+$")
		self.assertEqual(lines[2], "Check: Simulate and skinned meshes (2 pages)")
		self.assertRegex(lines[3], r"^  `alpha/intro` \(`ua`\): `new:3` home, allocation/ua\.md:\d+$")
		self.assertRegex(lines[4], r"^  `alpha/tutorial` \(`ua`\): `new:3` use, allocation/ua\.md:\d+$")
		self.assertNotIn("Not a check", out)

	def test_the_defining_row_names_the_check(self):
		self.add_checks()
		self.change("allocation/ua.md", "| `new:3` | open | home | Check: Simulate and skinned meshes. The page",
			"| `new:3` | open | home | Simulate and skinned meshes. The page")
		problems = self.problems()
		self.assertEqual(len(problems), 1, problems)  # the use row still says `Check:`
		self.assertProblem(problems, "allocation/ua.md:", "`new:3` starts with `Check:` here, but the row that defines "
			"it (line", "holds no check")
		_, out, _ = run("checks", "--plan", str(self.root))
		self.assertNotIn("Simulate", out)  # the home row defines the item, and it holds no check


class UnitsTest(PlanTest):
	def test_every_page_belongs_to_one_unit(self):
		units = [("ua", [("alpha", "alpha/intro", "alpha/tutorial")], "inva"),
			("ub", [("beta", None, None), ("alpha", "alpha/tutorial", "alpha/tutorial")], "invb"),
			("uc", [("gamma", None, None)], None), ("router", [], "invr")]
		with mock.patch.object(ca, "UNITS", units):
			problems = ca.Plan(self.root).unit_problems
		self.assertProblem(problems, "page `alpha/tutorial` belongs to `ua`, `ub`")
		self.assertProblem(problems, "page `alpha/howto` belongs to no unit")

	def test_spans_and_inventories(self):
		units = [("ua", [("alpha", None, None)], "inva"), ("ub", [("beta", "beta/deep", "beta/basics")], "invb"),
			("uc", [("delta", None, None)], "invq"), ("router", [], None)]
		with mock.patch.object(ca, "UNITS", units):
			problems = ca.Plan(self.root).unit_problems
		self.assertProblem(problems, "`beta/deep` comes after `beta/basics`")
		self.assertProblem(problems, "names part `delta`")
		self.assertProblem(problems, "inventory/invq.md does not exist")
		self.assertProblem(problems, "inventory/invr.md: no unit owns this inventory")

	def test_check_reports_missing_and_unknown_files(self):
		(self.root / "allocation/uc.md").unlink()
		self.write("allocation/notes.md", "# Notes\n")
		problems = self.problems()
		self.assertProblem(problems, "allocation/uc.md: file missing")
		self.assertProblem(problems, "allocation/notes.md: no unit of that name")
		code, out, _ = run("check", "--plan", str(self.root))
		self.assertEqual(code, 1)
		self.assertIn("allocation/uc.md: file missing", out)
		code, out, _ = run("check", "--plan", str(self.root), "--unit", "ua")
		self.assertEqual((code, out), (0, ""))


class OwnerTest(PlanTest):
	def test_an_item_placed_nowhere(self):
		problems = self.problems_after("ua", "| `inva:60` | rule | home | The rule |\n", "")
		self.assertProblem(problems, "`inva:60` (rule: Rule one) is placed nowhere")

	def test_an_item_homed_and_passed_on(self):
		problems = self.problems_after("ua", "| `inva:60` | rule | home | The rule |\n",
			"| `inva:60` | rule | home | The rule |\n| `inva:60` | rule | use | Again |\n")
		self.assertEqual(problems, [])  # a use row places nothing
		problems = self.problems_after("ua", "| `inva:79` | open | `nowhere` |", "| `inva:60` | rule | `beta/deep` |")
		self.assertProblem(problems, "`inva:60` is homed and passed on")
		self.assertProblem(problems, "`inva:79` (open: Not read: x.) is placed nowhere")

	def test_an_item_placed_twice(self):
		problems = self.problems_after("ua", "| `inva:60` | rule | home | The rule |\n",
			"| `inva:60` | rule | home | The rule |\n| `inva:60` | rule | home | Twice |\n")
		self.assertProblem(problems, "`inva:60` is placed 2 times")

	def test_only_the_owner_passes_an_item_on(self):
		problems = self.problems_after("ub", "## Passed on\n\nnone", "## Passed on\n\n| Item | Type | To | Why |\n"
			"| --- | --- | --- | --- |\n| `inva:60` | rule | `gamma/ref` | Mine now |")
		self.assertProblem(problems, "`inva` is the inventory of `ua`; only an item's owner passes it on")

	def test_a_home_of_an_item_nobody_passed(self):
		problems = self.problems_after("uc", "| `inva:50` | code | home |", "| `inva:50` | code | home | `src/c.cpp:1-2`: "
			"the snippet |\n| `inva:60` | rule | home |")
		self.assertProblem(problems, "`inva:60` is of `ua`'s inventory, and no file passes it to a page of `uc`")

	def test_a_passed_item_may_be_homed_on_another_page_of_the_unit(self):
		problems = self.problems_after("ub", "| `inva:48` | code | home | `src/b.cpp:4-5`: excerpt B |\n", "")
		self.assertEqual(problems, [])
		self.change("allocation/ub.md", "| `invb:19` | term | home | The term |",
			"| `invb:19` | term | home | The term |\n| `inva:48` | code | home | `src/b.cpp:4-5`: excerpt B |")
		self.assertEqual(self.problems("ub"), [])

	def test_a_refusal_of_an_item_nobody_passed(self):
		problems = self.problems_after("ub", "| `invr:6` | `router` |", "| `invr:5` | `router` |")
		self.assertProblem(problems, "`invr:5` is not passed to a page of `ub` by `router`")


class InboxTest(PlanTest):
	def test_inbox_lists_what_is_neither_homed_nor_refused(self):
		code, out, _ = run("inbox", "ua", "--plan", str(self.root))
		self.assertEqual(code, 0)
		self.assertIn("0 items", out)
		self.change("allocation/ua.md", "| `invr:5` | feature | home | R one, passed by the router |\n", "")
		code, out, _ = run("inbox", "ua", "--plan", str(self.root))
		self.assertEqual(code, 0)
		self.assertIn("`alpha/intro` (1)", out)
		self.assertIn("`invr:5` feature | R one | passed by `router`", out)
		self.assertIn("The intro teaches it", out)

	def test_a_refused_item_is_settled(self):
		code, out, _ = run("inbox", "ub", "--plan", str(self.root))
		self.assertNotIn("invr:6", out)
		self.change("allocation/ub.md", "| `invr:6` | `router` | Not this part's subject | `alpha/howto` |\n", "")
		code, out, _ = run("inbox", "ub", "--plan", str(self.root))
		self.assertIn("`beta/side` (1)", out)
		self.assertIn("`invr:6`", out)

	def test_inbox_without_the_units_file(self):
		(self.root / "allocation/ub.md").unlink()
		code, out, _ = run("inbox", "ub", "--plan", str(self.root))
		self.assertEqual(code, 0)
		self.assertIn("does not exist yet", out)
		self.assertIn("`beta/basics` (1)", out)
		self.assertIn("`inva:48` code", out)
		self.assertIn("`beta/side` (1)", out)

	def test_an_unknown_unit(self):
		self.assertEqual(run("inbox", "nobody", "--plan", str(self.root))[0], 2)


class DemandsTest(PlanTest):
	def test_demands(self):
		code, out, _ = run("demands", "ua", "--plan", str(self.root))
		self.assertEqual(code, 0)
		intro = out[out.index("`alpha/intro` ("):out.index("`alpha/tutorial` (")]
		self.assertIn("The intro | must | assumed by `beta/basics` (`ub`", intro)
		self.assertIn("Shared | must | assumed by `beta/side`", intro)
		self.assertNotIn("assumed by `alpha/tutorial`", out)  # the unit's own rows are no demands
		self.assertIn("One alternative only | must | assumed by `beta/side`", out)
		no_teacher = out[out.index("No teacher"):]
		self.assertIn("Something unknown | helps | assumed by `beta/basics`", no_teacher)


class CodeTest(PlanTest):
	def setUp(self):
		super().setUp()
		self.engine = self.root / "engine"
		for relative, lines in ENGINE_FILES.items():
			path = self.engine / relative
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes("".join(f"line {number}\n" for number in range(1, lines + 1)).encode("utf-8"))

	def code(self, *extra):
		return run("code", "--plan", str(self.root), "--engine", str(self.engine), *extra)

	def test_every_place_exists(self):
		code, out, _ = self.code()
		self.assertEqual(code, 0)
		self.assertIn("4 places", out)

	def test_a_missing_file(self):
		self.change("allocation/ub.md", "`src/x.cpp:1-2`", "`src/y.cpp:1-2`")
		code, out, _ = self.code()
		self.assertEqual(code, 1)
		self.assertIn("allocation/ub.md:", out)
		self.assertIn("`src/y.cpp` does not exist", out)

	def test_lines_beyond_the_end(self):
		self.change("allocation/ua.md", "`src/a.cpp:1-3`", "`src/a.cpp:2-4`")
		code, out, _ = self.code()
		self.assertEqual(code, 1)
		self.assertIn("`src/a.cpp:2-4`: the file has 3 lines", out)

	def test_the_case_of_a_name(self):
		self.change("allocation/ua.md", "`src/a.cpp:1-3`", "`Src/a.cpp:1-3`")
		code, out, _ = self.code()
		self.assertEqual(code, 1)
		self.assertIn("`Src/a.cpp` does not exist", out)
		self.assertIn("the name on disk is `src`", out)

	def test_one_unit_without_its_file(self):
		(self.root / "allocation/uc.md").unlink()
		code, out, _ = self.code("--unit", "uc")
		self.assertEqual(code, 1)
		self.assertIn("allocation/uc.md: file missing", out)

	def test_one_unit(self):
		self.change("allocation/ub.md", "`src/x.cpp:1-2`", "`src/y.cpp:1-2`")
		code, out, _ = self.code("--unit", "ua")
		self.assertEqual(code, 0)
		self.assertIn("1 places", out)


class CoverageTest(PlanTest):
	def coverage(self):
		code, _, _ = run("coverage", "--plan", str(self.root))
		self.assertEqual(code, 0)
		return self.read("allocation/coverage.md")

	def section(self, text, number):
		start = text.index(f"## {number}. ")
		end = text.find(f"\n## {number + 1}. ", start)
		return text[start:end if end >= 0 else len(text)]

	def test_the_same_input_gives_the_same_bytes(self):
		first = self.coverage()
		self.assertEqual(self.coverage(), first)

	def test_section1_summary(self):
		summary = self.section(self.coverage(), 1)
		self.assertIn("| `inva` | `ua` | 17 | 16 | 1 | 2 | 0 |", summary)
		self.assertIn("| `invr` | `router` | 2 | 1 | 0 | 1 | 1 |", summary)
		self.assertIn("Unit files missing: none.", summary)
		(self.root / "allocation/uc.md").unlink()
		summary = self.section(self.coverage(), 1)
		self.assertIn("Unit files missing: `uc`.", summary)

	def test_section2_open_items(self):
		section = self.section(self.coverage(), 2)
		self.assertIn("- `invr:6` feature: R two. Passed to `beta/side` by `router`, refused by `ub`: Not this part's "
			"subject. Better page: `alpha/howto`.", section)
		self.assertNotIn("`inva:", section)
		(self.root / "allocation/uc.md").unlink()
		self.assertIn("- `inva:50` code: Shorter snippets: `src/c.cpp` 1-2. Passed to `gamma/ref` by `ua`; the file of "
			"`uc` is missing.", self.section(self.coverage(), 2))
		self.write("allocation/uc.md", UNIT_C)
		self.change("allocation/ub.md", "| `invb:19` | term | home | The term |\n", "")
		self.assertIn("- `invb:19` term: B term. Not placed by its owner `ub`.", self.section(self.coverage(), 2))
		(self.root / "allocation/ub.md").unlink()
		self.assertIn("The owner's file `allocation/ub.md` is missing", self.section(self.coverage(), 2))

	def test_section3_two_homes(self):
		self.assertIn("none", self.section(self.coverage(), 3))
		self.change("allocation/uc.md", "| `inva:50` | code | home |", "| `inva:48` | code | home | `src/b.cpp:4-5`: B |\n"
			"| `inva:50` | code | home |")
		section = self.section(self.coverage(), 3)
		self.assertIn("- `inva:48` code: E2: `src/b.cpp` 4-5. Homes: `beta/basics` (`ub`, allocation/ub.md:", section)
		self.assertIn("`gamma/ref` (`uc`, allocation/uc.md:", section)

	def test_section4_passed_and_not_taken(self):
		section = self.section(self.coverage(), 4)
		self.assertIn("- `invr:6` feature: R two. Passed by `router` to `beta/side` (allocation/router.md:8): The side "
			"page. Refused by `ub` (allocation/ub.md:", section)
		self.assertIn("Not this part's subject. Better page: `alpha/howto`.", section)
		self.change("allocation/ub.md", "| `inva:48` | code | home | `src/b.cpp:4-5`: excerpt B |\n", "")
		self.assertIn("Neither taken nor refused by `ub` yet.", self.section(self.coverage(), 4))

	def test_section5_owner_faults(self):
		self.assertEqual(self.section(self.coverage(), 5).count("none"), 3)
		self.change("allocation/ua.md", "| `inva:60` | rule | home | The rule |\n",
			"| `inva:66` | hands-on | home | Twice |\n")
		self.change("allocation/uc.md", "| `inva:50` | code | home |", "| `invb:19` | term | home | Not mine |\n"
			"| `inva:50` | code | home |")
		section = self.section(self.coverage(), 5)
		self.assertIn("- `inva:66` hands-on: G1: Do it. `ua` places it 2 times", section)
		self.assertIn("- `inva:60` rule: Rule one. Not placed by `ua`.", section)
		self.assertIn("- `invb:19` term: B term. Homed by `uc` on `gamma/ref`", section)

	def test_section6_assumes(self):
		section = self.section(self.coverage(), 6)
		outside = section[:section.index("### No teacher")]
		self.assertIn("| `beta/basics` | Tutorial steps | `alpha/tutorial` | yes (E yes) |", outside)
		self.assertIn("| `beta/side` | One alternative only | `alpha/tutorial` | yes (E yes) |", outside)
		self.assertIn("| `beta/side` | Later | `beta/deep` | yes (E yes) |", outside)
		self.assertIn("| `gamma/ref` | Depth | `beta/deep` | on no track; earlier in the book's order: yes |", outside)
		self.assertNotIn("| Shared |", outside)  # every alternative leads to `alpha/intro`
		self.assertNotIn("| The intro |", outside)
		self.assertIn("| `beta/basics` | Something unknown | helps |", section[section.index("### No teacher"):])

	def test_section6_closure(self):
		closures = ca.needs_closures(self.plan())
		self.assertEqual(closures["beta/side"], {"beta/side", "alpha/intro"})
		self.assertEqual(closures["alpha/howto"], {"alpha/howto", "alpha/tutorial", "alpha/intro"})
		self.assertEqual(closures["beta/deep"], {"beta/deep", "beta/basics", "alpha/intro"})

	def test_section7_fit(self):
		section = self.section(self.coverage(), 7)
		over_under = section[:section.index("### All pages")]
		self.assertIn("- `alpha/tutorial` (M): **Fit.** `under`: about 2,000 words", over_under)
		self.assertIn("- `alpha/howto` (S): **Fit.** `over`: about 2,400 words", over_under)
		self.assertNotIn("`alpha/intro`", over_under)
		self.assertIn("| `alpha/intro` | `ua` | M | 2,900 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |", section)
		self.assertIn("| `beta/side` | `ub` | S | 1,400 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |", section)

	def test_section7_never_lists_a_page_of_kind_r(self):
		self.change("allocation/uc.md", "`fits`: about 1,400 words", "`under`: about 300 words")
		text = self.coverage()
		section = self.section(text, 7)
		self.assertNotIn("`gamma/ref`", section[:section.index("### All pages")])
		self.assertIn("| `gamma/ref` | `uc` | S | 300 |", section)
		self.assertIn("a page of kind R has no size check", self.section(text, 9))

	def test_section8_questions(self):
		section = self.section(self.coverage(), 8)
		self.assertIn("### `ua`", section)
		self.assertIn("- Is the how-to too long? (allocation/ua.md:", section)
		self.assertNotIn("### `ub`", section)

	def test_section9_format_problems(self):
		self.assertIn("none", self.section(self.coverage(), 9))
		self.change("allocation/uc.md", "| Depth | `beta/deep` | must |", "| Depth | `beta/deep` | maybe |")
		self.change("allocation/ua.md", "| `inva:60` | rule | home | The rule |\n", "")
		section = self.section(self.coverage(), 9)
		self.assertIn("Depth 'maybe' is none of must, helps", section)
		self.assertNotIn("placed nowhere", section)  # owner faults are section 5's


if __name__ == "__main__":
	unittest.main()

"""tools/booklib/outline.py: the outline's rules on the small outline of fixtures/outline/, and the same results as
plan/check_outline.py on the book's real outline (rulings 5, R17; rulings 4, R11)."""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
from booklib import outline as outline_rules

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c_Plan = os.path.join(c_Root, 'plan')
c_PlanScript = os.path.join(c_Plan, 'check_outline.py')


class SmallOutline:
    """A copy of the small outline that a test changes, then reads with the test book's decisions."""

    def __init__(self):
        self.folder = tempfile.mkdtemp(prefix='outline-test-')
        for name in os.listdir(helpers.c_OutlineFixture):
            shutil.copy(os.path.join(helpers.c_OutlineFixture, name), self.folder)

    def replace(self, name, old, new, count=1):
        path = os.path.join(self.folder, name)
        with open(path, encoding='utf-8') as file:
            text = file.read()
        if old not in text:
            raise AssertionError('%r is not in %s' % (old, name))
        with open(path, 'w', encoding='utf-8', newline='\n') as file:
            file.write(text.replace(old, new, count))

    def problems(self):
        return [str(problem) for problem in outline_rules.read(self.folder, helpers.c_TestBook).problems]

    def cleanup(self):
        shutil.rmtree(self.folder, ignore_errors=True)


class OutlineRulesTests(unittest.TestCase):
    def setUp(self):
        self.outline = SmallOutline()

    def tearDown(self):
        self.outline.cleanup()

    def assertProblem(self, fragment):
        problems = self.outline.problems()
        self.assertTrue(any(fragment in problem for problem in problems), '%r not in:\n%s' % (fragment, '\n'.join(problems)))
        return problems

    def test_the_small_outline_passes(self):
        self.assertEqual(self.outline.problems(), [])

    def test_rows_ids_kinds_sizes_and_marks(self):
        self.outline.replace('outline-2.md', '| `world/ecs` |', '| `world/ECS` |')
        self.outline.replace('outline-2.md', '| Entities and components | I | M |', '| Entities and components | Q | XXL |')
        problems = self.assertProblem("outline-2.md:24: `world/ECS`: id is not lowercase segments of [a-z0-9-] joined by /; write it")
        self.assertTrue(any("kind 'Q' is not one of C, I, T, H, R, P; write one of the six letters" in problem for problem in problems))
        self.assertTrue(any("size 'XXL' is not one of S, M, L, XL" in problem for problem in problems))

    def test_a_duplicate_id_and_a_reserved_last_segment(self):
        self.outline.replace('outline-2.md', '| `world/ecs` | Entities', '| `core/map` | Entities')
        problems = self.assertProblem('id duplicated (first at outline-2.md:13); give each row its own id')
        self.assertTrue(any("first segment 'core' is not the part's slug 'world'" in problem for problem in problems))
        self.outline.replace('outline-2.md', '| `core/map` | Entities', '| `world/index` | Entities')
        self.assertProblem('`world/index` is reserved for a generated part page')

    def test_a_title_with_a_banned_word(self):
        # rulings 5, R17: the spike found "Just enough C++ for game scripts" in the outline.
        self.outline.replace('outline-1.md', '| Programming from zero |', '| Just enough programming, simply put |')
        problems = self.assertProblem("outline-1.md:56: `basics/programming-1`: the title holds 'simply', a banned word of style.md §2.2")
        self.assertTrue(any("the title holds 'just'" in problem for problem in problems))
        self.assertTrue(all('justify' not in problem for problem in problems))

    def test_whole_words_only_for_banned_words(self):
        self.assertEqual(outline_rules.banned_words_in('Adjusting easing curves'), [])
        self.assertEqual(outline_rules.banned_words_in('It is easy to see why, of course'), ['of course', 'easy', 'it is easy to see'])

    def test_a_reserved_first_segment(self):
        self.assertEqual(outline_rules.id_problems('core/time'), [])
        self.assertIn('reserves', outline_rules.id_problems('print/core')[0][0])
        self.assertIn('reserves', outline_rules.id_problems('v1/core')[0][0])
        self.assertIn('reserves', outline_rules.id_problems('downloads/tutorials')[0][0])
        self.assertEqual(outline_rules.id_problems('make/index', part_page=True), [])
        self.assertIn('reserved for a generated part page', outline_rules.id_problems('make/index')[0][0])
        self.assertIn('lowercase', outline_rules.id_problems('Core/time')[0][0])

    def test_an_xl_primer_and_kinds_off_track_g(self):
        self.outline.replace('outline-1.md', '| Vectors | P | M |', '| Vectors | P | XL |')
        self.assertProblem('primers and pages of track B are at most L')
        self.outline.replace('outline-1.md', '| A tour of the editor | T |', '| A tour of the editor | I |')
        self.assertProblem('a game maker never has to read internals or reference')

    def test_needs_that_are_missing_too_many_or_a_cycle(self):
        self.outline.replace('outline-2.md', '| E | `core/time` |', '| E | `core/time`, `nope/missing` |')
        self.assertProblem('outline-2.md:24: `world/ecs`: Need `nope/missing` does not exist; name a row of the outline')
        self.outline.replace('outline-2.md', '| E | `core/time`, `nope/missing` |',
                             '| E | `core/time`, `core/map`, `start/install`, `start/welcome`, `basics/tools`\\|`basics/computer` |')
        self.assertProblem('its Needs name 6 page ids (alternatives included), more than 5')
        self.outline.replace('outline-2.md', '| `core/map` | The map of the engine | C | M | E | `start/install` |',
                             '| `core/map` | The map of the engine | C | M | E | `core/time` |')
        problems = self.assertProblem('Needs form a cycle: core/map -> core/time -> core/map')
        cycle = next(problem for problem in problems if 'cycle' in problem)
        self.assertTrue(cycle.startswith('outline-2.md:13: Needs form a cycle'), cycle)

    def test_the_part_lines(self):
        self.outline.replace('outline-2.md', 'Needs of the part: `core/time`', 'Needs of the part: `core/time`, `start/welcome`')
        self.assertProblem("Needs of the part names `start/welcome`, which no row of `world` needs from another part; remove it")
        self.outline.replace('outline-2.md', 'Needs of the part: `start/install`, `basics/math-vectors`', 'Needs of the part: `start/install`')
        self.assertProblem('Needs of the part lacks `basics/math-vectors`, which a row of `core` needs')
        self.outline.replace('outline-2.md', 'Tracks: E.', 'Tracks: G, E.')
        self.assertProblem("part `core`'s Tracks line names ['E', 'G'], its rows are on ['E']")

    def test_tracks_columns_lists_and_order(self):
        self.outline.replace('outline-2.md', '| Entities and components | I | M | E |', '| Entities and components | I | M | G |')
        self.assertProblem('Tracks G; rulings 1 (R4) put it on E')
        self.outline.replace('outline-2.md', '| Entities and components | I | M | G |', '| Entities and components | I | M | E |')
        self.outline.replace('tracks.md', '8. `core/map`\n9. `core/time`', '8. `core/time`\n9. `core/map`')
        problems = self.assertProblem("on track E, no alternative of Need `core/map` comes earlier")
        self.assertTrue(any('against the order of their part\'s rows' in problem for problem in problems))
        self.assertTrue(any("track E entry 8 is `core/time`; rulings 1 (R4) put `core/map` there" in problem for problem in problems))

    def test_side_steps(self):
        self.outline.replace('tracks.md', '5. `basics/tools` (side step) — offered before the first script\n6. `make/first-script`\n',
                             '5. `make/first-script`\n6. `basics/tools` (side step)\n')
        self.assertProblem('side step `basics/tools` of track G must stand directly before `make/first-script`')

    def test_marks_and_waves(self):
        self.outline.replace('outline-3.md', 'new · W8 |', 'new |')
        self.assertProblem('mark none, but rulings 1 (R6) give it W8; write the mark rulings 1 give')
        self.outline.replace('outline-1.md', '| Timers and events | H | S | G | `make/gameplay-math` |',
                             '| Timers and events | H | S | G | `make/project` |')
        self.assertProblem('wave 3 page needs `make/project` of wave 4; fix the wave list, not the Needs')

    def test_a_row_outside_a_part_and_a_missing_file(self):
        self.outline.replace('outline-2.md', '## Part 4 — Scenes and the ECS (`world`)', '## The world')
        self.assertProblem('a table row outside a part')
        os.remove(os.path.join(self.outline.folder, 'outline-4.md'))
        self.assertProblem('outline-4.md: file missing')


class OutlineDataTests(unittest.TestCase):
    def setUp(self):
        self.outline = helpers.read_outline()

    def test_closure_follows_every_alternative_and_the_part_s_first_row(self):
        self.assertEqual(outline_rules.closure(self.outline, 'make/first-script'),
                         {'make/editor-tour', 'start/install', 'start/welcome', 'basics/tools', 'basics/computer'})
        # A row with "-" needs its part's first row (style.md §1.2); the first row itself needs nothing.
        self.assertEqual(outline_rules.closure(self.outline, 'start/install'), {'start/welcome'})
        self.assertEqual(outline_rules.closure(self.outline, 'start/welcome'), set())

    def test_levels(self):
        levels = {page.id: outline_rules.level(self.outline, page) for page in self.outline.pages}
        self.assertEqual(levels['make/project'], 1)
        self.assertEqual(levels['core/time'], 2)
        self.assertEqual(levels['draw/culling'], 2)
        self.assertEqual(levels['reference/draw-tables'], 3)

    def test_the_data_file_s_shape(self):
        data = outline_rules.to_data(self.outline)
        self.assertEqual(list(data), ['generated', 'sources', 'parts', 'pages', 'tracks'])
        self.assertEqual(sorted(data['sources']), ['plan/outline-1.md', 'plan/outline-2.md', 'plan/outline-3.md', 'plan/outline-4.md',
                                                   'plan/tracks.md'])
        make = data['parts'][1]
        self.assertEqual((make['number'], make['slug'], make['title'], make['tracks'], make['partPages']),
                         (1, 'make', 'Making games', ['G', 'B'], True))
        self.assertEqual(make['needs'], ['start/install', 'basics/tools|start/install', 'basics/programming-1'])
        page = next(page for page in data['pages'] if page['id'] == 'make/first-script')
        self.assertEqual(page, {'id': 'make/first-script', 'title': 'Your first script', 'kind': 'tutorial', 'size': 'M',
                                'tracks': ['G', 'B'], 'needs': ['make/editor-tour', 'basics/tools|start/install'], 'part': 'make',
                                'block': 'A', 'mark': None, 'markSection': None, 'wave': '2', 'level': 1,
                                'row': 'plan/outline-1.md:28'})
        gpu = next(page for page in data['pages'] if page['id'] == 'gpu/frame')
        self.assertEqual((gpu['mark'], gpu['markSection'], gpu['block']), ('W8r', 'the passes', None))
        self.assertEqual(data['tracks']['G'][4], {'id': 'basics/tools', 'sideStep': True})
        self.assertEqual(data['tracks']['B'][0], {'id': 'start/welcome'})

    def test_counts_words_and_waves_print(self):
        lines = []
        outline_rules.print_counts(self.outline, lines.append)
        outline_rules.print_words(self.outline, lines.append)
        outline_rules.print_waves(self.outline, lines.append)
        text = '\n'.join(lines)
        self.assertIn('  block A  5', text)
        self.assertIn('Total pages: 23', text)
        self.assertIn('  G            12 (and 2 side steps)', text)
        self.assertIn('Wave B (phase B: the W8 pages, reference, appendix): 4 pages, 9,000 words', text)


def run_plan_script(plan_folder, script_folder):
    """(the output of plan/check_outline.py --counts --words --waves on an outline, whether the script calls this
    module). The script that holds its rules itself reads the folder it stands in; the one that calls this module takes
    --plan, and prints each problem with what to do."""
    with open(c_PlanScript, encoding='utf-8') as file:
        wrapper = re.search(r'^\s*(from booklib\b|import booklib\b)', file.read(), flags=re.M) is not None
    if wrapper:
        command = [sys.executable, '-I', c_PlanScript, '--plan', plan_folder]
    else:
        shutil.copy(c_PlanScript, script_folder)
        command = [sys.executable, '-I', os.path.join(script_folder, 'check_outline.py')]
    result = subprocess.run(command + ['--counts', '--words', '--waves'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8', 'replace').replace('\r\n', '\n'), wrapper


def library_output(plan_folder, with_advice):
    outline = outline_rules.read(plan_folder)
    lines = [str(problem) if with_advice else problem.text for problem in outline.problems]
    outline_rules.print_counts(outline, lines.append)
    outline_rules.print_words(outline, lines.append)
    outline_rules.print_waves(outline, lines.append)
    return '\n'.join(lines) + '\n', outline


def normalized(text):
    """plan/check_outline.py before the move named its own tables; the library names tools/booklib/outline.py."""
    return (text.replace('(WAVES in check_outline.py)', '(the waves in tools/booklib/outline.py)')
            .replace('(document_sentences in check_outline.py)', '(document_sentences in tools/booklib/outline.py)'))


@unittest.skipUnless(os.path.isfile(c_PlanScript) and os.path.isfile(os.path.join(c_Plan, 'outline-1.md')),
                     'needs the plan (plan/check_outline.py and the outline) in this checkout')
class SameAsThePlanScriptTests(unittest.TestCase):
    """rulings 5, R17: the library and plan/check_outline.py agree on the real outline, and on copies of it with one
    thing broken, problem by problem and in the printed counts."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='plan-copy-')
        self.plan = os.path.join(self.folder, 'plan')
        self.scripts = os.path.join(self.folder, 'script')
        os.makedirs(self.plan)
        os.makedirs(self.scripts)
        for name in os.listdir(c_Plan):
            if name.endswith('.md'):
                shutil.copy(os.path.join(c_Plan, name), self.plan)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def compare(self):
        # The script that holds its rules itself reads the folder it stands in: give it the changed copy.
        for name in os.listdir(self.plan):
            shutil.copy(os.path.join(self.plan, name), self.scripts)
        script, wrapper = run_plan_script(self.plan, self.scripts)
        library, outline = library_output(self.plan, wrapper)
        script = normalized(script)
        self.assertEqual(library, script)
        return outline

    def change(self, name, transform):
        path = os.path.join(self.plan, name)
        with open(path, encoding='utf-8') as file:
            text = file.read()
        changed = transform(text)
        self.assertTrue(changed != text, 'the change to %s found nothing to change' % name)
        with open(path, 'w', encoding='utf-8', newline='\n') as file:
            file.write(changed)

    def test_the_real_outline(self):
        outline = self.compare()
        self.assertEqual([str(problem) for problem in outline.problems], [])

    def test_a_row_twice(self):
        def duplicate(text):
            lines = text.split('\n')
            index = next(number for number, line in enumerate(lines) if line.startswith('| `'))
            return '\n'.join(lines[:index + 1] + [lines[index]] + lines[index + 1:])
        self.change('outline-2.md', duplicate)
        self.assertTrue(self.compare().problems)

    def test_a_kind_that_does_not_exist(self):
        self.change('outline-3.md', lambda text: re.sub(r'^(\| `[^`]+` \| [^|]+ \| )[CITHRP]( \|)', r'\1Q\2', text, count=1, flags=re.M))
        self.assertTrue(self.compare().problems)

    def test_a_need_that_does_not_exist(self):
        def add_need(text):
            lines = text.split('\n')
            index = max(number for number, line in enumerate(lines) if line.startswith('| `'))
            cells = outline_rules.split_row(lines[index])
            cells[5] = '`nope/missing`' if cells[5] == '-' else cells[5] + ', `nope/missing`'
            lines[index] = '| ' + ' | '.join(cells) + ' |'
            return '\n'.join(lines)
        self.change('outline-4.md', add_need)
        self.assertTrue(self.compare().problems)

    def test_two_entries_of_track_e_swapped(self):
        def swap(text):
            heading = text.index('## Track E')
            entries = list(re.finditer(r'^(\d+)\. `([^`]+)`', text[heading:], flags=re.M))
            first, second = entries[10], entries[11]
            start = heading
            return (text[:start + first.start(2)] + second.group(2) + text[start + first.end(2):start + second.start(2)]
                    + first.group(2) + text[start + second.end(2):])
        self.change('tracks.md', swap)
        self.assertTrue(self.compare().problems)

    def test_a_count_of_book_md(self):
        self.change('book.md', lambda text: re.sub(r'\*\*(\d+) pages\*\*', lambda match: '**%d pages**' % (int(match.group(1)) + 1), text, count=1))
        self.assertTrue(self.compare().problems)

    def test_a_size_s_budget_or_range_in_book_md(self):
        # The budgets and ranges of rule S (rulings 7, R28; rulings 8, R37) stand in book.md as both checks hold them.
        self.change('book.md', lambda text: text.replace('S 600 to 2,250', 'S 500 to 2,250', 1))
        self.assertTrue(self.compare().problems)
        self.change('book.md', lambda text: text.replace('S 500 to 2,250', 'S 600 to 2,250', 1).replace('XL 8,000 (', 'XL 9,000 (', 1))
        self.assertTrue(self.compare().problems)

    def test_a_part_s_tracks_line(self):
        self.change('outline-2.md', lambda text: re.sub(r'^Tracks: E\b', 'Tracks: G, E', text, count=1, flags=re.M))
        self.assertTrue(self.compare().problems)

    def test_a_wave_s_count_in_process_md(self):
        # The waves table stands indented in a list item.
        self.change('process.md', lambda text: re.sub(r'^(\s*\| 1 \| [^|]+\| )(\d+)', lambda match: match.group(1) + str(int(match.group(2)) + 1),
                                                       text, count=1, flags=re.M))
        self.assertTrue(self.compare().problems)


if __name__ == '__main__':
    unittest.main()

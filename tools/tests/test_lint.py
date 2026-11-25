"""tools/lint.py: every rule id of plan/style.md and the site's two, each with a passing and a failing fixture
(tools/tests/fixtures/lint/<rule>.md), on pages of the small book (tools/tests/fixtures/outline/) against a small
engine repository; and the tool's command line.

A fixture file holds cases. A line "%%% pass <page id> [overrides]" or "%%% fail <page id> <where>... [overrides]"
starts one; the lines after it are the page's body (or the whole page when they start with "---"), up to the next
"%%%" line. "%%% file <path>" starts a file of the case that is not the page (a figure manifest, a component of the
site). <where> is a line of the body (counted from its first line), "@<n>" a line of the whole page, "key:<key>" the
line of a front matter key, or "<path>:<n>" a line of another file. Overrides "key=value" change the row's front
matter (helpers.row_frontmatter; "_" stands for a space, "key=" leaves the key out). "%%repeat <n> <text>%%" in a
body stands for the text written n times. A failing case passes when the rule reports exactly the places it names; a
passing case when the rule reports nothing. Other rules may report anything: each case tests one rule.
"""

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import lint  # noqa: E402
from booklib import outline as outline_rules, prose, repo  # noqa: E402

c_Fixtures = os.path.join(helpers.c_Fixtures, 'lint')
c_Case = re.compile(r'^%%% (?P<kind>pass|fail|file) (?P<rest>.*)$')
c_Repeat = re.compile(r'%%repeat (\d+) (.+?)%%')

# The engine's documents of the small engine: copied-text finds runs of ten words of these.
c_EngineFiles = {
    'AGENTS.md': '# Agents\n\nThe main thread owns the scene, input, scripts and rendering submission in every frame of the game.\n',
    'Docs/DeveloperGuide.md': '# Guide\n\nRead the guide\'s section for the area you work on before changing it, as the [rules](x.md) say.\n',
    'Docs/Manual/Camera.md': '# Camera\n\nThe camera follows the player and keeps the horizon level while the game runs on any machine.\n',
    'Docs/Other.md': '# Other\n\nThis document is not one of the sources, so its ten words in a row may be used freely by pages.\n',
    'Strata/src/Strata/Core/Time.h': ''.join('int line%d;\n' % number for number in range(1, 40)),
}
c_Inventory = '# Inventory\n\n- The fixed step accumulator holds the time that the frames produced and no step used.\n'


def read_cases(path):
    cases = []
    target = None
    with open(path, encoding='utf-8') as file:
        text = file.read()
    for number, line in enumerate(text.split('\n'), start=1):
        match = c_Case.match(line)
        if match:
            kind, rest = match.group('kind'), match.group('rest').split()
            if kind == 'file':
                target = []
                cases[-1]['files'][rest[0]] = target
                continue
            case = {'kind': kind, 'page': rest[0], 'where': [], 'overrides': {}, 'files': {}, 'line': number, 'body': []}
            for token in rest[1:]:
                if '=' in token:
                    key, _, value = token.partition('=')
                    case['overrides'][key] = value.replace('_', ' ') or None
                else:
                    case['where'].append(token)
            cases.append(case)
            target = case['body']
            continue
        if target is not None:
            target.append(line)
    return cases


def expand(lines):
    text = '\n'.join(lines).strip('\n') + '\n'
    return c_Repeat.sub(lambda match: ' '.join([match.group(2)] * int(match.group(1))), text)


class Book:
    """The small book with the fixture glossary and the small engine, and one Lint for all cases."""

    def __init__(self, glossary=None):
        self.engine = helpers.TempEngine()
        commit = self.engine.commit(c_EngineFiles)
        self.book = helpers.TempBook(pin_commit=commit, plan=True)
        self.book.write('plan/inventory/test.md', c_Inventory)
        with open(glossary or os.path.join(c_Fixtures, 'glossary.json'), encoding='utf-8') as file:
            self.book.write('src/content/glossary.json', file.read())
        self.lint = lint.Lint(repo.Layout(self.book.root), self.engine.root, book=helpers.c_TestBook)

    def page_text(self, case):
        body = expand(case['body'])
        if body.startswith('---'):
            return body, 0
        row = self.book.outline.by_id[case['page']]
        front = helpers.row_frontmatter(row, **case['overrides'])
        return front + body, front.count('\n')

    def run(self, case):
        text, offset = self.page_text(case)
        written = []
        path = self.book.write('src/content/docs/%s.md' % case['page'], text)
        written.append(path)
        for relative, lines in case['files'].items():
            written.append(self.book.write(relative, expand(lines)))
        try:
            findings = self.lint.run([case['page']])
        finally:
            for path in written:
                os.remove(path)
        return findings, text, offset

    def cleanup(self):
        self.book.cleanup()
        self.engine.cleanup()


def where_of(case, text, offset):
    page_file = 'src/content/docs/%s.md' % case['page']
    places = set()
    lines = text.split('\n')
    for token in case['where']:
        if token.startswith('@'):
            places.add((page_file, int(token[1:])))
        elif token.startswith('key:'):
            key = token[4:]
            line = next(index + 1 for index, line in enumerate(lines) if line.startswith(key + ':'))
            places.add((page_file, line))
        elif ':' in token:
            path, _, line = token.rpartition(':')
            places.add((path, int(line)))
        else:
            places.add((page_file, offset + int(token)))
    return places


class RuleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = Book()

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()

    def test_every_rule_has_a_passing_and_a_failing_fixture(self):
        names = sorted(name[:-3] for name in os.listdir(c_Fixtures) if name.endswith('.md'))
        self.assertEqual(sorted(set(names) - set(lint.c_RuleIds)), [], 'fixtures for rules lint.py does not have')
        for rule in lint.c_RuleIds:
            path = os.path.join(c_Fixtures, rule + '.md')
            self.assertTrue(os.path.isfile(path), 'no fixture for %s' % rule)
            kinds = {case['kind'] for case in read_cases(path)}
            self.assertEqual(kinds, {'pass', 'fail'}, '%s needs a passing and a failing case' % rule)

    def test_style_md_names_every_rule(self):
        # Every rule id written in backticks in style.md's tables and lists is a rule of lint.py, except the strips' and
        # names' checks; and the site's two rules are lint.py's.
        with open(os.path.join(helpers.c_Fixtures, 'lint', 'style-rule-ids.txt'), encoding='utf-8') as file:
            ids = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        for rule in ids + ['inline-env', 'front-matter-head']:
            self.assertIn(rule, lint.c_RuleIds)

    def test_the_rules(self):
        for rule in lint.c_RuleIds:
            path = os.path.join(c_Fixtures, rule + '.md')
            if not os.path.isfile(path):
                continue
            for case in read_cases(path):
                with self.subTest(rule=rule, case='%s:%d' % (os.path.relpath(path, helpers.c_Fixtures), case['line'])):
                    findings, text, offset = self.book.run(case)
                    found = {(finding.path, finding.line) for finding in findings if finding.rule == rule}
                    shown = '\n'.join(str(finding) for finding in findings if finding.rule == rule)
                    if case['kind'] == 'pass':
                        self.assertEqual(found, set(), shown)
                    else:
                        self.assertEqual(found, where_of(case, text, offset), shown)

    def test_findings_name_the_file_the_line_and_the_rule(self):
        case = {'kind': 'fail', 'page': 'core/time', 'where': [], 'overrides': {}, 'files': {}, 'line': 1,
                'body': ['', 'You simply add it.']}
        findings, _, offset = self.book.run(case)
        banned = [finding for finding in findings if finding.rule == 'banned-word']
        self.assertEqual(len(banned), 1)
        self.assertEqual(str(banned[0]).split(': ', 2)[:2], ['src/content/docs/core/time.md:%d' % (offset + 1), 'banned-word'])
        self.assertIn('say what to do instead', str(banned[0]))

    def test_warnings_are_marked_and_do_not_fail(self):
        case = {'kind': 'fail', 'page': 'core/time', 'where': [], 'overrides': {}, 'files': {}, 'line': 1,
                'body': ['', 'The scene is copied by the editor.']}
        findings, _, _ = self.book.run(case)
        passive = [finding for finding in findings if finding.rule == 'passive']
        self.assertTrue(passive and all(finding.warning for finding in passive))
        self.assertIn(': passive (warning): ', str(passive[0]))

    def test_no_mark_on_the_page_waives_a_rule(self):
        # style.md allows only its warnings and the exemptions each rule states: a comment asks for nothing.
        case = {'kind': 'fail', 'page': 'core/time', 'where': [], 'overrides': {}, 'files': {}, 'line': 1,
                'body': ['', '<!-- lint-disable banned-word -->', '<!-- lint: ignore -->', 'You simply add it.']}
        findings, _, _ = self.book.run(case)
        self.assertIn('banned-word', [finding.rule for finding in findings])


class ExemplarTests(unittest.TestCase):
    """style.md §2.5's exemplar (fixtures/lint/exemplar.txt, copied from the plan) is meant to follow every rule of the
    file. On the home page of delta time it passes every rule that one passage can meet (the size and the reading time
    are the whole page's). With the 2,807 headwords of the bands 1 to 11 it failed on two words, "loop" and the "delta"
    of "delta t"; the bands 1 to 14 (critique/rulings-11.md, R50) hold both."""

    def test_the_exemplar_passes(self):
        book = Book(glossary=os.path.join(c_Fixtures, 'exemplar-glossary.json'))
        try:
            with open(os.path.join(c_Fixtures, 'exemplar.txt'), encoding='utf-8') as file:
                body = file.read()
            case = {'kind': 'pass', 'page': 'core/time', 'where': [], 'overrides': {}, 'files': {}, 'line': 1, 'body': body.split('\n')}
            findings, _, _ = book.run(case)
            failing = [(finding.rule, finding.message.split('"')[1]) for finding in findings
                       if not finding.warning and finding.rule not in ('size', 'time')]
            self.assertEqual(failing, [])
        finally:
            book.cleanup()


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments), book=helpers.c_TestBook)
    return code, output.getvalue()


class CommandLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = Book()

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()

    def setUp(self):
        self.root = self.book.book.root
        self.written = []

    def tearDown(self):
        for path in self.written:
            if os.path.exists(path):
                os.remove(path)

    def page(self, page_id, body):
        row = self.book.book.outline.by_id[page_id]
        self.written.append(self.book.book.write('src/content/docs/%s.md' % page_id, helpers.row_frontmatter(row) + body))

    def test_exit_codes(self):
        self.page('core/time', '\nYou simply add it.\n')
        code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', self.book.engine.root)
        self.assertEqual(code, 1, output)
        self.assertIn('src/content/docs/core/time.md:', output)
        self.assertIn('banned-word', output)
        # The small book has no site.json: the rule that needs it says that it did not run.
        self.assertIn('lint: note: literal-origin was not checked: site.json does not exist', output)
        code, output = quiet(lint.main, 'core/none', '--root', self.root, '--engine', self.book.engine.root)
        self.assertEqual(code, 2)
        self.assertIn('no page core/none', output)

    def test_a_named_page_s_prose_words_are_printed_beside_its_size(self):
        # rulings-11.md, R54: the count the size rule measures, in every run.
        self.page('core/time', '\nThe ball rolls on the floor.\n')
        size = self.book.book.outline.by_id['core/time'].size
        low, high = lint.c_Sizes[size]
        code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', self.book.engine.root)
        self.assertRegex(output, r'(?m)^src/content/docs/core/time\.md: words: \d+ prose words; size %s holds %s to %s$'
                         % (size, format(low, ','), format(high, ',')))

    def test_a_reference_page_always_fits_its_size(self):
        # rulings-8.md, R37: a kind R page's tables are as long as the engine makes them, so size never fires on it.
        self.page('reference/draw-tables', '\nThe ball rolls on the floor.\n')
        code, output = quiet(lint.main, 'reference/draw-tables', '--root', self.root, '--engine', self.book.engine.root)
        self.assertIn('prose words; size S', output)
        self.assertNotIn(': size:', output)
        self.page('core/time', '\nThe ball rolls on the floor.\n')
        code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', self.book.engine.root)
        self.assertIn(': size:', output)

    def test_a_term_mark_inside_a_link_is_refused(self):
        # The site's build refuses it (src/plugins/glossary.mjs), so the lint does too.
        self.page('core/time', '\nRead [the :term[frame]{id=frame} loop](../core/frame-loop.md) first.\n')
        code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', self.book.engine.root)
        self.assertIn('stands inside a link, which the build refuses', output)

    def test_only_warnings_pass(self):
        # start/welcome is a concept page of size S: 600 words in paragraphs of five short sentences, with a heading
        # every four paragraphs, and a reading time of 10 minutes pass every rule but the passive warning.
        section = '\n\n'.join(['The ball is rolled. The ball is rolled. The ball is rolled. The ball is rolled. The ball is rolled.'] * 4)
        row = self.book.book.outline.by_id['start/welcome']
        self.written.append(self.book.book.write('src/content/docs/start/welcome.md', helpers.row_frontmatter(row, time='10')
                                                 + ''.join('\n## Part %d\n\n%s\n' % (number, section) for number in range(1, 9))))
        code, output = quiet(lint.main, 'start/welcome', '--root', self.root, '--engine', self.book.engine.root)
        self.assertIn('passive (warning)', output)
        self.assertNotIn(': size:', output)
        self.assertEqual(code, 0, output)

    def test_the_engine_is_required_at_the_pin(self):
        self.page('core/time', '\nA line.\n')
        code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', os.path.join(self.root, 'no-such-clone'))
        self.assertEqual(code, 2)
        self.assertIn('no engine clone', output)
        other = helpers.TempEngine()
        try:
            other.commit({'README.md': 'another repository\n'})
            code, output = quiet(lint.main, 'core/time', '--root', self.root, '--engine', other.root)
            self.assertEqual(code, 2)
            self.assertIn('does not have the commit', output)
        finally:
            other.cleanup()

    def test_the_reading_report(self):
        self.page('core/time', '\n## The fixed step\n\nA **fixed step** is a slice of time. It runs. The zorbled ball is rolled.\n')
        folder = os.path.join(self.root, 'reports')
        quiet(lint.main, 'core/time', '--root', self.root, '--engine', self.book.engine.root, '--report', folder)
        with open(os.path.join(folder, 'core', 'time.txt'), encoding='utf-8') as file:
            report = file.read()
        for part in ('Reading report of core/time', 'Words: ', 'Sentences: 3; mean', 'longest', 'Paragraphs over 5 sentences: none',
                     'New terms per section:', 'The fixed step (line', 'fixed step', 'Words outside the lists (1): zorbled',
                     'Warnings (', 'passive (warning)'):
            self.assertIn(part, report)

    def test_help_lists_every_rule(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
            lint.main(['--help'])
        for rule in lint.c_RuleIds:
            self.assertIn('  %s' % rule, output.getvalue())
        self.assertIn('--engine', output.getvalue())
        self.assertIn('reading report', output.getvalue())


class ProseTests(unittest.TestCase):
    """booklib/prose.py: the definitions of style.md §2.2."""

    def blocks(self, text):
        return [block for block in prose.Page(text).blocks if block.words]

    def test_words(self):
        block = self.blocks('Call `Scene::Update`, then [the map](../core/map.md) and :term[fixed steps]{id=fixed-step} with $x + 1$ **bold**.\n')[0]
        self.assertEqual([word.text for word in block.words], ['Call', 'Scene::Update,', 'then', 'the', 'map', 'and', 'fixed', 'steps', 'with', 'x + 1', 'bold.'])
        self.assertEqual([word.kind for word in block.words][:2], ['word', 'code'])
        self.assertEqual(block.words[3].link, '../core/map.md')
        self.assertEqual(block.words[6].term, 'fixed-step')
        self.assertTrue(block.words[-1].bold)

    def test_a_value_mark_is_one_word_the_engine_decides(self):
        block = self.blocks('The editor has :value{key="commands.count"} commands, not a:b{c}.\n')[0]
        self.assertEqual([word.text for word in block.words], ['The', 'editor', 'has', 'commands.count', 'commands,', 'not', 'a:b{c}.'])
        self.assertEqual(block.words[3].kind, 'code')

    def test_sentences(self):
        block = self.blocks('Open `Time.h`. It runs "now." Then 1.5 s pass? Yes! The end\n')[0]
        self.assertEqual([len(sentence) for sentence in block.sentences], [2, 3, 4, 1, 2])
        items = self.blocks('Read this:\n\n- an item without a stop\n- two. Sentences.\n')
        self.assertEqual([len(block.sentences) for block in items], [1, 1, 2])

    def test_headings_and_tables_hold_no_sentences(self):
        found = self.blocks('## A heading. Two\n\n| A. B | C |\n| --- | --- |\n| D. E | F |\n')
        self.assertEqual([block.kind for block in found], ['heading', 'table'])
        self.assertEqual([block.sentences for block in found], [[], []])
        self.assertEqual(len(found[1].words), 6)

    def test_paragraphs_items_and_lines(self):
        text = 'One line\ngoes on.\n\n1. A step\n   on two lines.\n\n   More of the step.\n\n2. Next.\n\nAfter.\n'
        found = self.blocks(text)
        self.assertEqual([(block.kind, block.line) for block in found], [('paragraph', 1), ('item', 4), ('paragraph', 7), ('item', 9), ('paragraph', 11)])
        self.assertEqual(found[2].items, [found[1]])
        self.assertEqual(found[1].list_id, found[3].list_id)
        self.assertEqual(found[0].words[-1].line, 2)

    def test_what_is_not_prose(self):
        text = '---\ntitle: "x"\n---\n\nText.\n\n```cpp\nint a;\n```\n\n$$\nx = 1\n$$\n\n<!-- a\ncomment -->\n'
        page = prose.Page(text)
        self.assertEqual([block.kind for block in page.blocks], ['paragraph', 'fence', 'math', 'html'])
        self.assertEqual(sum(len(block.words) for block in page.blocks), 1)

    def test_containers(self):
        page = prose.Page(':::note[The formula]\nInside.\n:::\n\nOutside.\n')
        kinds = [(block.kind, [directive.name for directive in block.containers]) for block in page.blocks]
        self.assertEqual(kinds, [('open', []), ('label', ['note']), ('paragraph', ['note']), ('close', []), ('paragraph', [])])


class TaughtTests(unittest.TestCase):
    def test_alternatives_teach_only_what_both_teach(self):
        outline = helpers.read_outline()
        taught = outline_rules.taught(outline, 'basics/programming-1')
        # basics/programming-1 needs make/first-script|start/install: only start/install and what it needs count.
        self.assertEqual(taught, {'start/install', 'start/welcome'})
        self.assertIn('make/first-script', outline_rules.closure(outline, 'basics/programming-1'))
        self.assertEqual(outline_rules.taught(outline, 'start/welcome'), set())
        self.assertIn('core/map', outline_rules.taught(outline, 'core/time'))


class EverydayTermTests(unittest.TestCase):
    """rulings-11.md, R53: a term that is one everyday word asks for no mark, and a name's trailing parenthesis is a
    qualifier that pages do not write."""

    @classmethod
    def setUpClass(cls):
        cls.book = Book()

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()

    def findings(self, page, body, rule='term-mark'):
        case = {'kind': 'fail', 'page': page, 'where': [], 'overrides': {}, 'files': {}, 'line': 1, 'body': ['', body]}
        findings, _, _ = self.book.run(case)
        return [str(finding) for finding in findings if finding.rule == rule]

    def test_the_common_list_with_its_inflected_forms(self):
        words = self.book.lint.words
        for word in ('camera', 'cameras', 'tool', 'tools', 'reach', 'reaches', 'step', 'stepping', 'down'):
            self.assertTrue(words.common_word(word), word)
        for word in ('accumulator', 'spline', 'occluder'):
            self.assertFalse(words.common_word(word), word)

    def test_a_list_word_outside_the_common_list_is_no_everyday_word(self):
        # extra-words.txt widens what a page may write, not what a term may leave unmarked.
        words = self.book.lint.words
        extra = sorted(word for word in words.extra if word.isalpha() and not words.common_word(word))
        self.assertTrue(extra and words.known(extra[0]))

    def test_an_everyday_term_is_marked_where_the_page_marks_it(self):
        self.assertEqual(self.findings('world/ecs', 'The camera moves, and the cameras follow.'), [])
        self.assertEqual(self.findings('world/ecs', 'The accumulator holds time.')[0].split(': ')[1], 'term-mark')

    def test_a_qualified_name_is_matched_by_the_name_before_its_parenthesis(self):
        found = self.findings('world/ecs', 'The spline bends.')
        self.assertEqual(len(found), 1)
        # world/ecs needs core/time, which needs core/map: of the two splines, core/map's is the page's.
        self.assertIn('{id=spline-path}', found[0])
        self.assertEqual(self.findings('world/ecs', 'The clip runs.'), [])

    def test_the_lint_lists_the_qualified_names_by_their_words(self):
        glossary = self.book.lint.glossary
        self.assertEqual(lint.base_name('Clip (animation)'), 'Clip')
        self.assertEqual(lint.base_name('Decomposition (of a transform)'), 'Decomposition')
        self.assertEqual(lint.base_name('cmake_language(DEFER)'), 'cmake_language')
        self.assertEqual(lint.base_name('Offset allocator'), 'Offset allocator')
        self.assertEqual([entry['id'] for entry in glossary.choices[('spline',)]], ['spline-curve', 'spline-path'])
        self.assertNotIn(('spline', '(curve)'), glossary.names)


class ClerkNameTests(unittest.TestCase):
    """The clerk of wave 1b: a qualified name beside an entry of the same home named by its base ("luminance" and
    "Luminance (Y)" on basics/color), and a term whose name is code (`ST_CORE_ASSERT`)."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(c_Fixtures, 'glossary.json'), encoding='utf-8') as file:
            data = json.load(file)
        data['terms'] += [
            {'id': 'tint', 'term': 'tint', 'definition': 'How strong a color is.', 'home': 'world/ecs'},
            {'id': 'tint-y', 'term': 'Tint (Y)', 'definition': 'The weighted sum of the channels.', 'home': 'world/ecs'},
            {'id': 'st-tint', 'term': '`ST_TINT`', 'definition': 'The macro that tints.', 'home': 'world/ecs'},
            {'id': 'painters-rows', 'term': "Painters' rows", 'definition': 'The rows a painter chooses.', 'home': 'world/ecs'},
            {'id': 'st-tint-st-shade', 'term': '`ST_TINT`/`ST_SHADE`', 'definition': 'The pair of macros.', 'home': 'world/ecs'},
        ]
        cls.temp = tempfile.TemporaryDirectory()
        path = os.path.join(cls.temp.name, 'glossary.json')
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
        cls.book = Book(glossary=path)

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()
        cls.temp.cleanup()

    def undefined(self, body):
        case = {'kind': 'fail', 'page': 'world/ecs', 'where': [], 'overrides': {}, 'files': {}, 'line': 1, 'body': ['', body]}
        findings, _, _ = self.book.run(case)
        return [finding.message for finding in findings if finding.rule == 'term-defined'
                and any(name in finding.message for name in ('"tint"', '"Tint (Y)"', '"`ST_TINT`"'))]

    def test_a_qualified_name_beside_its_base_of_the_same_home_is_written_whole(self):
        glossary = self.book.lint.glossary
        self.assertEqual([entry['id'] for entry in glossary.choices[('tint',)]], ['tint'])
        self.assertEqual([entry['id'] for entry in glossary.choices[('tint', 'y')]], ['tint-y'])
        # Elsewhere the qualifier stays no part of the name (R53).
        self.assertNotIn(('spline', 'curve'), glossary.names)

    def test_both_entries_are_defined_by_their_own_bold_words(self):
        body = '**Tint** is how strong a color is. **Tint (Y)** is the weighted sum. **`ST_TINT`** is the macro.'
        self.assertEqual(self.undefined(body), [])

    def test_a_name_ending_in_a_plural_possessive_is_found(self):
        # A page's word drops the apostrophe of "painters'"; the glossary's name must match it all the same.
        case = {'kind': 'fail', 'page': 'world/ecs', 'where': [], 'overrides': {}, 'files': {}, 'line': 1,
                'body': ['', "The **painters' rows** are the rows a painter chooses."]}
        findings, _, _ = self.book.run(case)
        self.assertEqual([finding.message for finding in findings if finding.rule == 'term-defined' and 'Painters' in finding.message], [])

    def test_a_code_name_is_defined_only_by_its_bold_code_span(self):
        found = self.undefined('**Tint** is how strong a color is. **Tint (Y)** is the sum. The macro `ST_TINT` tints.')
        self.assertEqual(len(found), 1, found)
        self.assertIn('`ST_TINT`', found[0])

    def test_a_name_of_code_spans_joined_by_a_slash_is_defined_by_its_bold_pair(self):
        # The page's words join "`ST_TINT`/`ST_SHADE`" into one code word, so the name must match it joined.
        def pair_findings(body):
            case = {'kind': 'fail', 'page': 'world/ecs', 'where': [], 'overrides': {}, 'files': {}, 'line': 1, 'body': ['', body]}
            findings, _, _ = self.book.run(case)
            return [finding.message for finding in findings if finding.rule == 'term-defined' and 'ST_SHADE' in finding.message]
        self.assertEqual(pair_findings('The pair **`ST_TINT`/`ST_SHADE`** tints and shades.'), [])
        self.assertEqual(len(pair_findings('The pair `ST_TINT`/`ST_SHADE` tints and shades.')), 1)


class PilotRuleTests(unittest.TestCase):
    """rulings-11.md, R54: what the pilot's writers lost rounds to."""

    @classmethod
    def setUpClass(cls):
        cls.book = Book()

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()

    def findings(self, page, lines, rule):
        case = {'kind': 'fail', 'page': page, 'where': [], 'overrides': {}, 'files': {}, 'line': 1, 'body': [''] + lines}
        findings, _, _ = self.book.run(case)
        return [finding for finding in findings if finding.rule == rule]

    def test_one_run_reports_every_feature_of_a_fence(self):
        # core/time's closure holds basics/programming-1 only: a fence of four homes' features gets one finding that
        # names every one of them, so that one question aside can answer them all.
        found = self.findings('core/time', ['The sketch:', '', '```cpp sketch="core-time-all.cpp"', 'class Ball', '{',
                                            '	virtual int Roll() { return 1; }', '	Ball* Next = nullptr;', '	~Ball() {}', '};', '```', '',
                                            'It rolls.'], 'cpp-feature')
        self.assertEqual(len(found), 1, '\n'.join(map(str, found)))
        for home in ('basics/programming-2', 'basics/programming-3', 'basics/cpp-memory', 'basics/cpp-classes'):
            self.assertIn('../%s.md' % home, found[0].message)

    def test_pointers_and_optional_are_homed_on_programming_3(self):
        # rulings 7, D24, and rulings 9, R42: ->, nullptr, * in a type, std::optional, has_value and value_or are
        # basics/programming-3's; std::nullopt is not matched as std::optional.
        def homes(code):
            return {feature['home'] for feature in self.book.lint.words.features
                    if any(re.search(pattern, code, re.MULTILINE) for pattern in feature['patterns'])}
        for code in ('Ball* next', 'ball->Roll', 'p == nullptr', 'std::optional<int> count', 'count.has_value()', 'count.value_or(0)'):
            self.assertIn('basics/programming-3', homes(code), code)
            self.assertNotIn('basics/cpp-memory', homes(code), code)
            self.assertNotIn('basics/cpp-modern', homes(code), code)
        self.assertEqual(homes('return std::nullopt;') - {'basics/programming-2'}, {'basics/cpp-modern'})

    def test_term_source_is_a_warning(self):
        found = self.findings('core/time', ['A :term[render pass]{id=render-pass} draws.'], 'term-source')
        self.assertTrue(found and all(finding.warning for finding in found))
        self.assertIn('term-source', lint.c_Warnings)

    def test_a_glossary_word_is_known_with_its_endings(self):
        glossary = self.book.lint.glossary
        for word in ('occluder', 'occluders', 'spline', 'splines', 'culling', 'object'):
            self.assertTrue(glossary.known(word), word)
        self.assertFalse(glossary.known('careens'))

    def test_the_acronym_rule_does_not_read_further_reading(self):
        # R54 took word-list out of the entries of Further reading; the second pilot's world/ecs showed the acronym
        # rule still reading them (a source's title, "ECS").
        lines = ['## Further reading', '', '- Jason Gregory, "Game Engine Architecture", on the ECS of a game (advanced).']
        self.assertEqual(self.findings('core/time', lines, 'acronym'), [])
        self.assertEqual(len(self.findings('core/time', ['The ECS of a game holds its things.'], 'acronym')), 1)

    def test_the_names_the_pilot_pages_asked_for(self):
        # The second pilot's notes (plan/notes/*/*.md, "## Requests"): proper names for tools/data/names.txt.
        lines = ['Tetris, Bevy, GDScript, MoltenVK, LunarG, Homebrew, CTest and cppreference are names. Robert Nystrom,',
                 'Glenn Fiedler, Jason Gregory and Diomidis Spinellis wrote about games and code.']
        self.assertEqual([str(finding) for finding in self.findings('core/time', lines, 'word-list')], [])

    def test_units_and_school_mathematics_are_everyday_words(self):
        # tools/data/extra-words.txt takes the units and the school mathematics the pilot's pages needed.
        words = self.book.lint.words
        for word in ('Hz', 'millisecond', 'milliseconds', 'microseconds', 'nanosecond', 'ns', 'thousandths', 'billionths',
                     'subtract', 'multiplication', 'perpendicular', 'hypotenuse', 'parallelogram', 'quadrants', 'theorem',
                     'amplitude', 'inverse', 'infinity', 'counterclockwise', 'clockwise', 'algebra'):
            self.assertTrue(words.known(word.lower()), word)


if __name__ == '__main__':
    unittest.main()

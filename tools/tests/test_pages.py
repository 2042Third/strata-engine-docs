"""tools/pages.py on a small book whose plan is fixtures/outline/: the front matter of style.md §6.1, the outline rules
O1 to O9 on the pages, the page shape rules P1 to P4, the quoting rule of rulings 5 (R17), the glossary of
pipelines.md §9 and the outline's data file."""

import contextlib
import io
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import pages
from booklib import repo


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


class PagesTestCase(unittest.TestCase):
    def setUp(self):
        self.book = helpers.TempBook(plan=True)

    def tearDown(self):
        self.book.cleanup()

    def run_check(self, release=False):
        errors, notes = pages.check(repo.Layout(self.book.root), release, book=helpers.c_TestBook)
        return ['%s: %s' % item for item in errors], ['%s: %s' % item for item in notes]

    def assertError(self, fragment, release=False):
        errors, _ = self.run_check(release)
        self.assertTrue(any(fragment in error for error in errors), '%r not in:\n%s' % (fragment, '\n'.join(errors)))
        return errors

    def assertClean(self, release=False):
        errors, notes = self.run_check(release)
        self.assertEqual(errors, [])
        return notes

    def write_all_kinds(self):
        """One page of each kind, the part pages of make, and the pages their Needs name."""
        for page_id in ('start/welcome', 'start/install', 'make/editor-tour', 'make/first-script', 'basics/computer', 'basics/tools',
                        'core/map', 'core/time', 'reference/glossary'):
            if page_id == 'basics/computer':
                self.book.row_page(page_id, uses=['tools.md', '../make/first-script.md', 'programming-1.md'])
            elif page_id == 'basics/tools':
                self.book.row_page(page_id, uses=['../make/first-script.md', 'programming-1.md', 'math-vectors.md#vectors'])
            else:
                self.book.row_page(page_id)
        self.book.page('make/index', helpers.part_page('make', 'index', self.book.outline))
        self.book.page('make/review', helpers.part_page('make', 'review', self.book.outline))


class GoodBookTests(PagesTestCase):
    def test_a_book_of_every_kind_passes_and_lists_what_is_not_written(self):
        self.write_all_kinds()
        self.book.page('index', '---\ntitle: "The book"\ndescription: "The test book."\ntemplate: splash\nhero:\n  tagline: Hi\n---\n')
        self.book.page('404', '---\ntitle: "Not found"\ndescription: "No such page."\n---\n')
        notes = self.assertClean()
        self.assertIn('plan/outline-1.md:44: O7: the row make/project has no page yet (src/content/docs/make/project.md)', notes)
        self.assertTrue(any('O2: the Need "basics/math-vectors" is not written yet' in note for note in notes), notes)
        # The command line, with the small book's decisions in place of the real book's.
        read = pages.outline_rules.read
        with mock.patch.object(pages.outline_rules, 'read', lambda plan, book=None, documents=None: read(plan, helpers.c_TestBook, documents)):
            code, output = quiet(pages.main, 'check', '--root', self.book.root)
            self.assertEqual(code, 0, output)
            self.assertIn('note: O7: 14 rows of the outline have no page yet (--release lists them)', output)
            self.assertIn('pages: 13 pages, 0 errors,', output)
            code, output = quiet(pages.main, 'check', '--root', self.book.root, '--release')
            self.assertEqual(code, 1, output)
            self.assertIn('plan/outline-1.md:44: O7: the row make/project has no page yet', output)

    def test_a_release_turns_what_is_missing_into_errors(self):
        self.write_all_kinds()
        errors = self.assertError('O7: the row make/project has no page yet', release=True)
        self.assertTrue(any('a release has no draft pages' in error for error in errors))
        # A tutorial's file and stamp are tools/tutorials.py check's (plan/pipelines.md §6.3), not this tool's.
        self.assertFalse(any('tutorials/' in error for error in errors), errors)


class FrontMatterTests(PagesTestCase):
    def test_title_and_description_in_double_quotes(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, title='The map of the engine') + helpers.body('concept'))
        self.assertError('src/content/docs/core/map.md:3: "title" is not written in double quotes: write title: "The map of the engine"')
        self.book.page('core/map', helpers.row_frontmatter(row, title='Time: a story') + helpers.body('concept'))
        errors = self.assertError('src/content/docs/core/map.md:3: the front matter is not valid YAML')
        self.assertTrue(any('core/map.md:3: "title" is not written in double quotes' in error for error in errors))

    def test_the_keys_of_style_6_1(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, id='core/other', size='Q', tracks='[game]', time='"soon"', since='0.2.0',
                                                           prerequisites='[]', need='[]', status='done') + helpers.body('concept'))
        errors = self.assertError('"id" must be the file\'s path under src/content/docs/ without .md: write id: core/map')
        for fragment in ('"size" must be one of S, M, L, XL', '"tracks" is a list of the letters G, B and E',
                         '"time" is the whole minutes', '"since" is 0.3.0 or later', 'the key "prerequisites" is not part of the book\'s front '
                         'matter: the key is "needs"', 'unknown front matter key "need"', '"status" must be one of draft, reviewed, final'):
            self.assertTrue(any(fragment in error for error in errors), '%r not in:\n%s' % (fragment, '\n'.join(errors)))

    def test_learn_lines(self):
        row = self.book.outline.by_id['core/map']
        learn = '\n  - id: one\n    text: understand the map\n  - id: one\n    text: know the parts\n  - id: Bad_Id\n    text: draw a map'
        self.book.page('core/map', helpers.row_frontmatter(row, learn=learn) + helpers.body('concept'))
        errors = self.assertError('learn line 1 starts with "understand", which no one can observe')
        self.assertTrue(any('learn line 2: the id "one" is used twice' in error for error in errors))
        self.assertTrue(any("learn line 3: the id 'Bad_Id' is not lowercase words" in error for error in errors))
        self.book.page('core/map', helpers.row_frontmatter(row, learn='\n  - id: one\n    text: explain it') + helpers.body('concept'))
        self.assertError('"learn" holds two to five objectives')

    def test_description_and_since(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, description='"One sentence. Another one."', since=None) + helpers.body('concept'))
        errors = self.assertError('"description" is one sentence')
        self.assertTrue(any('"since" is missing' in error for error in errors))
        welcome = self.book.outline.by_id['start/welcome']
        self.book.page('start/welcome', helpers.row_frontmatter(welcome, since='0.3.0') + helpers.body('concept'))
        self.assertError('"since" is written only on concept, internals, tutorial and how-to pages of parts 1 and 3 to 21')
        self.book.page('core/map', helpers.row_frontmatter(row, since='0.9.0') + helpers.body('concept'))
        self.assertError('"since" 0.9.0 is later than the book\'s release 0.8.0')


class OutlineRuleTests(PagesTestCase):
    def test_o1_ids(self):
        self.book.page('core/Bad_Name', helpers.frontmatter(id='core/Bad_Name'))
        self.assertError('O1: id \'core/Bad_Name\' is not lowercase segments')
        self.book.remove('src/content/docs/core/Bad_Name.md')
        self.book.page('print/core', helpers.frontmatter(id='print/core'))
        self.assertError("O1: id 'print/core' starts with 'print', which the site reserves")
        self.book.remove('src/content/docs/print/core.md')
        self.book.row_page('core/map')
        self.book.page('core/map/index', helpers.frontmatter(id='core/map/index'), listed=False)
        self.assertError('are served at the same address /core/map/')

    def test_o2_o3_and_o6_needs(self):
        row = self.book.outline.by_id['core/time']
        self.book.row_page('core/map')
        self.book.page('core/time', helpers.row_frontmatter(row, needs='[core/map, nope/missing]') + helpers.body('internals'))
        self.assertError('O2: the Need "nope/missing" is no page of the outline')
        self.book.page('core/time', helpers.row_frontmatter(row, needs='[core/map, a/b|c/d|e/f, g/h|i/j]') + helpers.body('internals'))
        self.assertError('O3: the Needs name 6 page ids')
        map_row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(map_row, needs='[core/time]') + helpers.body('concept'))
        self.book.page('core/time', helpers.row_frontmatter(row, needs='[core/map]') + helpers.body('internals'))
        self.assertError('O6: the Needs form a cycle: core/map -> core/time -> core/map')

    def test_o4_a_need_later_on_the_track(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, needs='[core/time]') + helpers.body('concept'))
        errors = self.assertError('O4: on track E, no alternative of the Need "core/time" comes earlier')
        self.assertTrue(any('O7: the Needs differ from its row (plan/outline-2.md:13): write needs: [start/install]' in error for error in errors))

    def test_o5_tracks_of_the_page_and_of_the_sidebar(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, tracks='[E, G]') + helpers.body('concept'))
        self.assertError('O5: "tracks" names G, but the sidebar\'s track G does not hold it')
        self.book.row_page('core/map')
        data = json.loads(self.book.read('src/sidebar.json'))
        data['tracks']['engine']['sequence'].reverse()
        data['tracks']['game']['sideSteps'] = []
        self.book.write('src/sidebar.json', json.dumps(data))
        errors = self.assertError('O5: track "engine" entry 1 is "draw/culling"; plan/tracks.md\'s track E puts "start/welcome" there')
        self.assertTrue(any('O5: track "game"\'s "sideSteps" are []' in error for error in errors))

    def test_o7_rows_and_pages(self):
        row = self.book.outline.by_id['core/map']
        self.book.page('core/map', helpers.row_frontmatter(row, title='"Another title"', kind='internals', size='S') + helpers.body('concept'))
        errors = self.assertError('O7: the title differs from its row (plan/outline-2.md:13): write title: "The map of the engine"')
        self.assertTrue(any('O7: the kind differs' in error for error in errors))
        self.assertTrue(any('O7: the size differs' in error for error in errors))
        self.book.page('core/extra', helpers.frontmatter(id='core/extra'))
        self.assertError('O7: core/extra is no row of the outline')

    def test_o8_part_pages(self):
        self.book.page('make/index', helpers.part_page('make', 'index', self.book.outline))
        self.assertError('O8: the part pages come together: write src/content/docs/make/review.md too')
        self.book.page('make/review', helpers.part_page('make', 'review', self.book.outline, generated='index', tracks='[G]'))
        errors = self.assertError('a part page carries generated: review')
        self.assertTrue(any('a part page carries its part\'s tracks: write tracks: [G, B]' in error for error in errors))
        self.book.page('core/index', helpers.part_page('core', 'index', self.book.outline))
        self.assertError('O8: part "core" has 2 rows, fewer than 8, so it has no index page')
        self.book.remove('src/content/docs/core/index.md')
        self.book.remove('src/content/docs/make/index.md')
        self.book.remove('src/content/docs/make/review.md')
        self.book.pages = []
        self.book.sidebar()
        self.assertError('O8: part "make" has 8 rows, so it has src/content/docs/make/index.md', release=True)

    def test_o9_the_sidebar_s_parts(self):
        self.book.row_page('core/map')
        data = json.loads(self.book.read('src/sidebar.json'))
        data['parts'][3]['label'] = 'Core'
        data['parts'][3]['pages'] = []
        data['parts'][4]['pages'] = ['core/map', 'world/ecs']
        data['parts'].append({'slug': 'extra', 'label': 'Extra', 'pages': []})
        self.book.write('src/sidebar.json', json.dumps(data, indent='\t'))
        errors = self.assertError("O9: the sidebar lists the parts ['start', 'make', 'basics', 'core', 'world', 'gpu', 'draw', 'reference', "
                                  "'appendix', 'extra']")
        for fragment in ('O9: part "core" has the label "Core"; its title in the outline (plan/outline-2.md:5) is "Engine architecture"',
                         'O9: "core/map" is not a page of part "world"', 'O9: the sidebar lists "world/ecs", which is no page'):
            self.assertTrue(any(fragment in error for error in errors), '%r not in:\n%s' % (fragment, '\n'.join(errors)))
        data['parts'][4]['pages'] = []
        self.book.write('src/sidebar.json', json.dumps(data, indent='\t'))
        self.assertError('O9: src/content/docs/core/map.md is not listed in src/sidebar.json')


class PageShapeTests(PagesTestCase):
    def page(self, page_id, text_body, **frontmatter_overrides):
        row = self.book.outline.by_id[page_id]
        self.book.page(page_id, helpers.row_frontmatter(row, **frontmatter_overrides) + text_body)

    def test_p1_the_bottom_strip_and_the_body_s_end(self):
        self.page('core/map', helpers.body('concept').replace('## Exercises', '## Tasks'))
        self.assertError('P1: a concept page ends with the sections "## Summary", "## Check yourself", "## Exercises"')
        self.page('core/map', helpers.body('concept').replace('## Common mistakes', '## Mistakes'))
        errors = self.assertError('P1: the body of a concept page ends with "## Common mistakes" before the bottom strip')
        self.assertTrue(any('P1: a concept page has the section "## Common mistakes"' in error for error in errors))
        self.page('core/time', helpers.body('internals').replace('## Changing it safely', '## Changing it'))
        self.assertError('P1: the body of an internals page ends with "## Changing it safely"')
        self.page('make/first-script', helpers.body('tutorial').replace('## What you will make', '## The goal'))
        self.assertError('P1: the first section of a tutorial page is "## What you will make"')
        self.page('start/install', helpers.body('how-to').replace('## Result', '## What you have'))
        self.assertError('P1: a how-to page has the section "## Result"')

    def test_p1_counts(self):
        self.page('core/map', helpers.body('concept', summary=3, questions=2, exercises=5))
        errors = self.assertError('P1: "## Summary" holds 3 items; it holds one bulleted item per learn line (2)')
        self.assertTrue(any('P1: "## Check yourself" holds 2 numbered items; it holds 3 to 6' in error for error in errors))
        self.assertTrue(any('P1: "## Exercises" holds 5 numbered items; it holds 1 to 4' in error for error in errors))
        text = helpers.body('concept').replace('2. Question 2?\n\n   :::answer{tests="one"}\n   Because it is.\n   :::\n', '2. Question 2?\n')
        self.page('core/map', text)
        self.assertError('every question and exercise is followed by an :::answer')

    def test_p2_learn_ids_and_tests(self):
        self.page('core/map', helpers.body('concept', tests=('one',)))
        self.assertError('P2: the learn id "two" is in the tests of no "Check yourself" answer')
        self.page('core/map', helpers.body('concept', tests=('one two', 'three')))
        self.assertError('P2: tests names "three", which is no learn id of the page (one, two)')
        self.page('core/map', helpers.body('concept').replace(':::answer{tests="one two"}', ':::answer'))
        self.assertError('P2: an answer in "## Check yourself" carries tests="<learn ids>"')
        self.page('core/map', helpers.body('concept').replace(':::answer{tests="one two"}', ':::answer{tests="one, two" hint="x"}'))
        errors = self.assertError('an :::answer carries only tests="<learn ids>" and solution="<file>"')
        self.assertFalse(any('P2: tests names' in error for error in errors), errors)  # "one, two" reads as two ids

    def test_p3_the_test_out_box(self):
        uses = ['tools.md', '../make/first-script.md', 'programming-1.md']
        primer = helpers.body('primer', uses=uses)
        self.page('basics/computer', primer)
        self.assertClean()
        self.page('basics/computer', primer.split('::::\n', 1)[1])
        self.assertError('P3: a primer opens with its Test out box')
        self.page('basics/computer', primer.replace('5. Question 5?', 'Not a question.'))
        self.assertError('P3: the Test out box holds 4 numbered questions; it holds exactly 5')
        self.page('basics/computer', primer.replace('tests="two"}\n   Yes.', 'tests="one"}\n   Yes.'))
        self.assertError('P3: the Test out answers\' tests do not cover the learn id "two"')
        self.page('basics/computer', 'Text first.\n\n' + primer)
        self.assertError('P3: the Test out box is the first thing of the page')

    def test_where_the_book_uses_a_primer(self):
        self.page('basics/computer', helpers.body('primer', uses=['../start/install.md', '../core/map.md']))
        errors = self.assertError('"## Where the book uses it" links 2 pages; it links at least 3')
        self.assertTrue(any('start/install does not have basics/computer in its Needs closure' in error for error in errors))

    def test_p4_internals_quote_the_engine(self):
        text = helpers.body('internals').replace(helpers.quote(10), '').replace(helpers.quote(20), '')
        self.page('core/time', text)
        self.assertError('P4: an internals page quotes the engine at least 3 times')

    def test_unclosed_directives(self):
        self.page('core/map', helpers.body('concept').replace(':::example\nA worked example.\n:::\n', ':::example\nA worked example.\n'))
        self.assertError('the directive :::example')

    def solution_page(self, page_id, solution, answer_body='   Because it is.\n'):
        """A page of the kind of its row whose first exercise's answer names a worked solution."""
        kind = self.book.outline.by_id[page_id].kind_word
        old = '1. **Basic.** Exercise 1.\n\n' + helpers.answer('two')
        new = '1. **Basic.** Exercise 1.\n\n   :::answer[Worked solution]{tests="two" solution="%s"}\n%s   :::\n' % (solution, answer_body)
        text = helpers.body(kind)
        self.assertIn(old, text)
        self.page(page_id, text.replace(old, new))

    def test_a_worked_solution_names_a_file_the_reader_gets(self):
        sketch = ('   ```cpp sketch="core-map-sum.cpp"\n   int main() {}\n   ```\n\n   It prints:\n\n'
                  '   ```text output-of="core-map-sum.cpp"\n   3\n   ```\n')
        self.solution_page('core/map', 'sketches/core-map-sum.cpp', sketch)
        self.assertClean()
        self.solution_page('core/map', 'sketches/core-map-sum.cpp')
        self.assertError('src/content/docs/core/map.md:60: solution="sketches/core-map-sum.cpp": the answer shows the sketch in full, '
                         'with its output: a fence with sketch="core-map-sum.cpp", then its ```text output-of="core-map-sum.cpp" fence')
        self.solution_page('core/map', 'sketches/core-map-sum.cpp', sketch.split('\n\n   It prints:')[0] + '\n')
        self.assertError('the answer shows the sketch in full, with its output')
        self.solution_page('core/map', 'sketches/core-time-sum.cpp', sketch.replace('core-map-sum', 'core-time-sum'))
        self.assertError('solution="sketches/core-time-sum.cpp": a sketch\'s file name starts with its page\'s id, sketches/core-map-<name>')
        self.solution_page('core/map', 'sketches/sum')
        self.assertError('solution="sketches/sum" must name a file of sketches/ with its extension, such as sketches/core-map-toy.cpp')
        self.solution_page('core/map', 'tutorials/core/time/exercise-1.patch')
        self.assertError('solution="tutorials/core/time/exercise-1.patch": the solution of an exercise is a file of its own page, '
                         'tutorials/core/map/exercise-<n>.patch')
        self.solution_page('core/map', 'solutions/core-map.zip')
        self.assertError('solution="solutions/core-map.zip" names the file of a worked solution: a sketch the answer shows with its '
                         'output (solution="sketches/core-map-<name>.cpp"), an editor exercise (solution="tutorials/core/map/'
                         'exercise-<n>.tutorial.json") or an engine exercise (solution="tutorials/core/map/exercise-<n>.patch")')
        self.solution_page('core/map', ' ')
        self.assertError('solution="" names no file')

    def test_a_worked_solution_follows_the_site_s_reader(self):
        sketch = ('   ```cpp sketch="core-map-sum.cpp"\n   int main() {}\n   ```\n\n   It prints:\n\n'
                  '   ```text output-of="core-map-sum.cpp"\n   3\n   ```\n')
        # A :::question inside a ::: answer ends the answer where it ends, so the sketch after it is outside.
        self.solution_page('core/map', 'sketches/core-map-sum.cpp', '   :::question\n   New?\n   :::\n\n' + sketch)
        self.assertError('solution="sketches/core-map-sum.cpp": the answer shows the sketch in full, with its output')
        # solution= on the sketch's fence is no attribute of a fence.
        self.solution_page('core/map', 'sketches/core-map-sum.cpp', sketch.replace(
            'sketch="core-map-sum.cpp"', 'sketch="core-map-sum.cpp" solution="sketches/core-map-sum.cpp"'))
        self.assertError('a code fence has no attribute "solution"')

    def test_an_internals_page_s_general_section_holds_a_fifth_of_its_words(self):
        text = helpers.body('internals')
        self.page('core/time', text.replace('Approaches.\n', 'Approaches. ' + 'One two three four five. ' * 40 + '\n'))
        errors = self.assertError('the section "## The problem and how engines solve it" holds 201 of the page\'s ')
        self.assertTrue(any('it holds at most a fifth' in error for error in errors))
        self.page('core/time', text)
        errors, _ = self.run_check()
        self.assertFalse(any('holds at most a fifth' in error for error in errors), errors)

    def test_an_exercise_s_solution_exists_and_has_its_download(self):
        for name, download in (('exercise-1.tutorial.json', 'exercise-1.zip'), ('exercise-2.patch', 'exercise-2.patch')):
            solution = 'tutorials/make/first-script/%s' % name
            self.solution_page('make/first-script', solution)
            self.assertError('src/content/docs/make/first-script.md:64: solution="%s": %s does not exist: write the worked solution'
                             % (solution, solution))
            self.book.write(solution, '{}\n')
            notes = self.assertClean()
            pending = 'solution="%s": its download public/downloads/solutions/make/first-script/%s is not written yet: run python -I ' \
                      'tools/tutorials.py compile' % (solution, download)
            self.assertTrue(any(pending in note for note in notes), notes)
            self.assertError(pending, release=True)
            self.book.write('public/downloads/solutions/make/first-script/%s' % download, 'PK')
            errors, notes = self.run_check(release=True)
            self.assertFalse(any('solution=' in item for item in errors + notes), errors + notes)

    def test_the_build_s_rules_on_links_tabs_examples_checkpoints_and_command_steps(self):
        concept = helpers.body('concept')
        self.page('core/map', concept.replace('A story.', 'A story, as [the clock](/core/time/#ticks) tells.'))
        self.assertError('core/map.md:19: "/core/time/#ticks" is an absolute path: link to the page\'s .md file with a relative '
                         'path, time.md#ticks (the base path is added by the build)')
        self.assertEqual(pages.relative_link('make/input', '/gpu/shaders/'), '../gpu/shaders.md')
        self.page('core/map', concept.replace('A story.', 'A story, as [a page](../core/nowhere.md) tells.'))
        self.assertError('"../core/nowhere.md": there is no page core/nowhere.md')
        self.page('core/map', concept.replace('A story.', 'A story.\n\n::::tabs{sync=how}\n:::tab[With a command]\nRun it.\n:::\n::::'))
        errors = self.assertError('a tab set holds at least two tabs')
        self.assertTrue(any('a tab set with sync=how holds the tabs "In the editor", "With a command", in this order (style.md §10); '
                            'this one holds "With a command"' in error for error in errors), errors)
        self.page('core/map', concept.replace('A story.', 'A story.\n\n:::derivation[The steps]\nSteps.\n:::\n\n:::why{icon=star}\nBecause.\n:::'))
        errors = self.assertError(':::derivation[The steps] takes no text in brackets')
        self.assertTrue(any(':::why has no attribute "icon" (it takes none)' in error for error in errors), errors)
        self.book.write('src/generated/reference/values.json', json.dumps({'commands.count': 153}))
        self.page('core/map', concept.replace('A story.', 'A story of :value{key="commands.count"} and :value{key="nope.count"}.'))
        errors = self.assertError(':value{key="nope.count"}: src/generated/reference/values.json has no key "nope.count"')
        self.assertFalse(any('key="commands.count"' in error for error in errors), errors)
        self.page('core/map', concept.replace(':::example\nA worked example.\n:::\n', 'No example.\n'))
        self.assertError('a :::example stands before the bottom strip of a concept page: a worked example comes before the first exercise')
        tutorial = helpers.body('tutorial')
        self.page('make/first-script', tutorial.replace('## Make the ball roll', '## Why balls roll\n\nTheory.\n\n## Make the ball roll'))
        self.assertError('the step section "## Why balls roll" of a tutorial ends with ::checkpoint{stage=…}')
        self.page('make/first-script', tutorial.replace('::figure{id=ball-rolling}\n', '::figure{id=ball-rolling}\n\nA closing note.\n'))
        self.assertError('the step section "## Make the ball roll" of a tutorial ends with ::checkpoint{stage=…}')
        self.book.write('tutorials/make/first-script.tutorial.json', json.dumps({'page': 'make/first-script', 'patch': 'x.patch'}))
        self.assertFalse(any('step section' in error for error in self.run_check()[0]))
        self.page('make/first-script', tutorial.replace('1. Do it.', '1. This step has no menu or button: run a command.'))
        self.assertError('make/commands, which teaches running one, is not in the page\'s Needs closure')

    def test_a_checkpoint_is_followed_by_its_picture(self):
        tutorial = helpers.body('tutorial')
        self.page('make/first-script', tutorial)
        self.assertClean()
        self.page('make/first-script', tutorial.replace('\n::figure{id=ball-rolling}\n', '\nThe ball rolls.\n'))
        self.assertError('src/content/docs/make/first-script.md:31: the checkpoint is followed by its picture, headed "You should now '
                         'have": write ::figure{id=…} on the next line, a recipe of the page\'s figure manifest that shows the project at '
                         'this point (style.md §7.4)')
        self.page('make/first-script', tutorial.replace('::figure{id=ball-rolling}', '::compare{id=ball-rolling}'))
        self.assertError('that shows the project at this point, not a ::compare slider (style.md §7.4)')
        self.page('make/first-script', tutorial.replace('::figure{id=ball-rolling}', '::figure'))
        self.assertError('src/content/docs/make/first-script.md:33: the checkpoint\'s picture names its recipe: ::figure{id=<figure id>}')
        self.page('make/first-script', tutorial.replace('\n::figure{id=ball-rolling}\n', '\n```text\n::figure{id=ball-rolling}\n```\n'))
        self.assertError('the checkpoint is followed by its picture')
        self.page('make/first-script', tutorial.replace('::checkpoint{stage=1}', '```text\n::checkpoint{stage=1}\n```'))
        errors = self.assertError('the step section "## Make the ball roll" of a tutorial ends with ::checkpoint')  # a checkpoint inside a fence is code
        self.assertFalse(any('the checkpoint is followed by its picture' in error for error in errors), errors)
        self.page('core/map', helpers.body('concept').replace('## Common mistakes', '::checkpoint{stage=1}\n\n## Common mistakes'))
        self.assertError('src/content/docs/core/map.md:27: ::checkpoint ends a step section of a tutorial (style.md §7.4), and this page\'s '
                         'kind is concept: remove it')


class GlossaryTests(PagesTestCase):
    def glossary(self, *terms):
        self.book.write('src/content/glossary.json', json.dumps({'terms': list(terms)}, indent='\t'))

    def test_a_good_glossary_and_a_home_not_written_yet(self):
        self.book.row_page('core/map')
        self.glossary({'id': 'frame', 'term': 'frame', 'definition': 'One pass of the loop.', 'home': 'core/map', 'aliases': ['tick'], 'avoid': []},
                      {'id': 'fixed-step', 'term': 'fixed step', 'definition': 'A step of fixed length.', 'home': 'core/time', 'use': 'make/scenes',
                       'known': False})
        _, notes = self.run_check()
        self.assertTrue(any('"fixed step": its home page core/time is not written yet' in note for note in notes), notes)
        self.assertTrue(any('"fixed step": its use home make/scenes is not written yet' in note for note in notes), notes)
        self.assertError('its home page core/time is not written yet', release=True)

    def test_the_entries_schema_and_names(self):
        self.glossary({'id': 'frame', 'term': 'frame', 'definition': 'One pass. Two passes.', 'home': 'core/nope', 'color': 'red'},
                      {'id': 'frame-rate', 'term': "frame's rate", 'definition': 'How many frames a second.', 'home': 'core/map', 'aliases': ['Frame']},
                      {'id': 'tick', 'term': 'tick', 'definition': 'A step.', 'home': 'core/map', 'avoid': ['frame'], 'use': 'core/time'})
        errors = self.assertError('src/content/glossary.json:5: entry 1 has the unknown key "color"')
        for fragment in ('"frame": the definition is one sentence', '"frame": the home "core/nope" is no page of the outline',
                         '"frame\'s rate": "id" is the term in lowercase words joined by "-": write "id": "frames-rate"',
                         'the name "Frame" is also a name of the entry at line 5', '"frame" is a name of this entry and an "avoid" name of entry 3',
                         '"tick": "use" names its use home, a page of part make'):
            self.assertTrue(any(fragment in error for error in errors), '%r not in:\n%s' % (fragment, '\n'.join(errors)))

    def test_ids_from_terms(self):
        self.assertEqual(pages.glossary_id("two's complement"), 'twos-complement')
        self.assertEqual(pages.glossary_id('Rec. 709'), 'rec-709')
        self.assertEqual(pages.glossary_id('C++ reference'), 'c-reference')


class OutlineDataFileTests(PagesTestCase):
    def test_write_check_and_stale(self):
        root = self.book.root
        code, output = quiet(pages.main, 'outline', '--check', '--root', root)
        self.assertEqual(code, 1, output)  # written with the test book's decisions: the real book's rules find problems
        outline_path = self.book.path('src/generated/outline.json')
        os.remove(outline_path)
        errors = self.assertError('src/generated/outline.json:1: the outline\'s data file is missing: run python -I tools/pages.py outline --write')
        self.book.write('src/generated/outline.json', pages.outline_text(self.book.outline))
        self.assertClean()
        self.book.write('src/generated/outline.json', '{}\n')
        self.assertError('src/generated/outline.json:1: the file is not what the outline gives today')

    def test_the_cli_writes_and_checks_the_real_outline(self):
        plan = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'plan')
        if not os.path.isfile(os.path.join(plan, 'outline-1.md')):
            self.skipTest('needs the plan in this checkout')
        code, output = quiet(pages.main, 'outline', '--write', '--root', self.book.root, '--plan', plan)
        self.assertEqual(code, 0, output)
        self.assertEqual(quiet(pages.main, 'outline', '--check', '--root', self.book.root, '--plan', plan)[0], 0)
        data = json.loads(self.book.read('src/generated/outline.json'))
        self.assertEqual(len(data['parts']), 25)
        code, output = quiet(pages.main, 'outline', '--write', '--check', '--root', self.book.root, '--plan', plan)
        self.assertEqual(code, 2, output)

    def test_the_outline_s_own_problems_are_reported(self):
        path = self.book.path('plan/outline-2.md')
        with open(path, encoding='utf-8') as file:
            text = file.read()
        with open(path, 'w', encoding='utf-8', newline='\n') as file:
            file.write(text.replace('| `world/ecs` | Entities and components | I |', '| `world/ecs` | Entities and components | Q |'))
        self.assertError('plan/outline-2.md:24: the outline: outline-2.md:24: `world/ecs`: kind \'Q\' is not one of')

    def test_no_plan_is_a_usage_error(self):
        code, output = quiet(pages.main, 'check', '--root', self.book.root, '--plan', self.book.path('nowhere'))
        self.assertEqual(code, 2)
        self.assertIn('no outline at', output)


if __name__ == '__main__':
    unittest.main()

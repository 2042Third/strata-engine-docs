"""markterms.py (rulings-11.md, R53): the marks and forward links it writes where the lint's term-mark rule reports a
first use, what it never changes, and that a second run changes nothing. Pages of the small book
(tools/tests/fixtures/outline/): world/ecs needs core/time, which needs core/map; gpu/frame and draw/culling come later."""

import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import lint  # noqa: E402
import markterms  # noqa: E402
from booklib import repo  # noqa: E402

c_Glossary = {'terms': [
    {'id': 'accumulator', 'term': 'accumulator', 'definition': 'The time no step has simulated yet.', 'home': 'core/time'},
    {'id': 'step-accumulator', 'term': 'step accumulator', 'definition': 'The accumulator of fixed steps.', 'home': 'core/time'},
    {'id': 'delta-time', 'term': 'delta time', 'definition': 'The time between two frames.', 'home': 'core/time',
     'aliases': ['frame time']},
    {'id': 'render-pass', 'term': 'render pass', 'definition': 'One step of drawing a frame on the GPU.', 'home': 'gpu/frame'},
    {'id': 'occluder', 'term': 'occluder', 'definition': 'A mesh that hides others.', 'home': 'draw/culling'},
    {'id': 'camera', 'term': 'camera', 'definition': 'The point the scene is seen from.', 'home': 'draw/culling'},
    {'id': 'entity', 'term': 'entity', 'definition': 'A thing in a scene.', 'home': 'world/ecs'},
    {'id': 'spline-curve', 'term': 'Spline (curve)', 'definition': 'A smooth curve through points.', 'home': 'basics/tools'},
    {'id': 'spline-path', 'term': 'Spline (path)', 'definition': 'A path an entity follows.', 'home': 'core/map'},
]}


class MarkTermsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = helpers.TempBook(plan=True)
        cls.book.write('src/content/glossary.json', json.dumps(c_Glossary))
        cls.front = helpers.row_frontmatter(cls.book.outline.by_id['world/ecs'])

    @classmethod
    def tearDownClass(cls):
        cls.book.cleanup()

    def run_tool(self, *arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = markterms.main(list(arguments) + ['--root', self.book.root], book=helpers.c_TestBook)
        return code, output.getvalue()

    def mark(self, body, *arguments):
        """Writes world/ecs with the body, runs the tool: (exit code, output, the body afterwards)."""
        self.book.page('world/ecs', self.front + body)
        code, output = self.run_tool('world/ecs', *arguments)
        return code, output, self.book.read('src/content/docs/world/ecs.md')[len(self.front):]

    def unmarked(self):
        context = lint.Terms(repo.Layout(self.book.root), book=helpers.c_TestBook)
        page = lint.PageText(context, 'world/ecs', self.book.path('src/content/docs/world/ecs.md'))
        return [occurrence.entry['id'] for occurrence in lint.unmarked_terms(context, page)]

    def test_a_term_of_the_needs_closure_gets_its_mark(self):
        code, output, body = self.mark('\nThe accumulator holds time. The accumulator grows.\n')
        self.assertEqual(code, 0)
        self.assertEqual(body, '\nThe :term[accumulator]{id=accumulator} holds time. The accumulator grows.\n')
        self.assertIn('world/ecs.md:%d: mark: "accumulator" -> :term[accumulator]{id=accumulator}' % (self.front.count('\n') + 2), output)
        self.assertIn('markterms: 1 written (1 mark)', output)

    def test_a_term_outside_it_is_neither_marked_nor_linked(self):
        # rulings-11.md, R54: the writer says in the sentence what such a term is; the tool writes no link.
        body = '\nEach render pass draws, and the occluder hides it.\n'
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertIn('markterms: 0 written (0 marks)', output)
        self.assertEqual(self.unmarked(), [])

    def test_the_lint_and_the_tool_agree(self):
        body = ('\nThe frame time, the render passes, a spline and the step accumulator differ from the accumulator.\n\n'
                '- The occluder of a list item.\n\n> An entity in a quote, and the delta time.\n\n| Name | What |\n| --- | --- |\n'
                '| camera | the occluder\'s mesh |\n')
        self.book.page('world/ecs', self.front + body)
        before = self.unmarked()
        self.assertIn('spline-path', before)  # the spline of core/map, which world/ecs needs
        code, output = self.run_tool('world/ecs')
        self.assertEqual(code, 0)
        self.assertIn('markterms: %d written' % len(before), output)
        self.assertEqual(self.unmarked(), [])
        text = self.book.read('src/content/docs/world/ecs.md')
        self.assertIn(':term[frame time]{id=delta-time}', text)
        self.assertIn('the render passes,', text)
        self.assertIn(':term[spline]{id=spline-path}', text)
        self.assertIn('the :term[step accumulator]{id=step-accumulator} differ from the :term[accumulator]{id=accumulator}', text)
        self.assertIn('- The occluder of a list item.', text)
        self.assertIn('> An entity in a quote, and the delta time.', text)
        self.assertIn('| camera |', text)  # one everyday word of the common list: no mark (R53)

    def test_what_it_leaves_alone(self):
        # rulings-11.md, R54: the use right after the page's own bold definition, a block quote, the test-out box, the
        # link text of a Further reading entry, and a sentence that already links the term's home.
        body = ('\n::::test-out\n1. Does the accumulator grow?\n\n   :::answer{tests="x"}\n   Yes.\n   :::\n::::\n\n'
                '> The delta time of a quote.\n\n'
                'The **accumulator** is the time no step has used yet. The accumulator grows.\n\n'
                'The [time page](../core/time.md) says how the delta time is measured.\n\n'
                '## Further reading\n\n- [Splines and the step accumulator](https://www.example.com/): curves; beginner.\n')
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertIn('markterms: 0 written', output)
        self.assertNotIn('left for the writer', output)

    def test_a_further_reading_entry_is_left_whole(self):
        # The second pilot (world/ecs): a mark written in an entry that names a source without a link.
        body = ('\n## Further reading\n\n- Robert Nystrom, "Game Programming Patterns", chapter on the accumulator and the'
                ' delta time: why games keep time (beginner).\n')
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertEqual(self.unmarked(), [])

    def test_the_sentence_of_the_pages_own_definition_is_left_alone(self):
        # The second pilot (world/ecs): a mark written in the sentence that holds the page's bold definition.
        body = '\nEach frame feeds the accumulator, and the **accumulator** is the time no step has used yet.\n'
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertEqual(self.unmarked(), [])

    def test_a_second_run_changes_nothing(self):
        self.mark('\nThe accumulator holds the frame\ntime of a render pass.\n')
        first = self.book.read('src/content/docs/world/ecs.md')
        self.assertIn(':term[frame\ntime]{id=delta-time}', first)  # the line end stays inside the mark: no re-wrapping
        self.assertNotIn('](', first)  # never a link
        code, output = self.run_tool('world/ecs')
        self.assertEqual(code, 0)
        self.assertIn('markterms: 0 written', output)
        self.assertEqual(self.book.read('src/content/docs/world/ecs.md'), first)
        code, output = self.run_tool('world/ecs', '--check')
        self.assertEqual((code, output.strip()), (0, 'markterms: nothing to write'))

    def test_check_writes_nothing_and_fails_when_a_run_would_change_the_page(self):
        code, output, body = self.mark('\nThe accumulator holds time.\n', '--check')
        self.assertEqual(code, 1)
        self.assertEqual(body, '\nThe accumulator holds time.\n')
        self.assertIn('mark: "accumulator"', output)
        self.assertIn('markterms: 1 to write (1 mark)', output)

    def test_it_never_touches_headings_code_links_bold_directives_or_front_matter(self):
        body = ('\n## The accumulator\n\n```cpp\nfloat accumulator = 0;\n```\n\n::figure{id=accumulator}\n\n'
                ':::note[The accumulator]{id=accumulator}\nThe `accumulator` and the **accumulator** button come first.\n:::\n\n'
                '## Later\n\nThen the accumulator.\n')
        code, _, after = self.mark(body)
        self.assertEqual(code, 0)
        self.assertEqual(after, body.replace('Then the accumulator.', 'Then the :term[accumulator]{id=accumulator}.'))
        self.assertNotIn(':term', self.front)
        # A first use in a directive's label is the writer's to rephrase.
        body = '\nPress :kbd[accumulator], then read the accumulator.\n'
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertIn('left for the writer: "accumulator"', output)

    def test_a_first_use_inside_another_link_is_left_for_the_writer(self):
        body = '\nRead [the accumulator](../core/map.md) first.\n'
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertIn('left for the writer: "accumulator": its words stand in a link', output)
        self.assertTrue(output.splitlines()[0].endswith('(note)'))
        self.assertIn('markterms: 0 written (0 marks), 1 left for the writer', output)

    def test_a_link_to_the_home_and_a_mark_already_written_are_kept(self):
        body = '\nThe [render pass](../gpu/frame.md) and the :term[accumulator]{id=accumulator} are marked.\n'
        code, output, after = self.mark(body)
        self.assertEqual((code, after), (0, body))
        self.assertIn('markterms: 0 written', output)

    def test_usage_errors(self):
        code, output = self.run_tool('core/nope')
        self.assertEqual(code, 2)
        self.assertIn('no page core/nope', output)


if __name__ == '__main__':
    unittest.main()

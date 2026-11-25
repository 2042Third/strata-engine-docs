"""pagecheck.py (plan/card/checks.md): which tools it runs for a page, how it reads their output, and its summary. The
tools themselves are replaced by a recorded runner: their own tests are test_lint.py, test_names.py and the others."""

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import pagecheck

c_Pin = '1' * 40

c_PageText = '---\nid: core/time\n---\n\nText.\n'
c_SketchText = c_PageText + '\nThe sketch:\n\n```cpp sketch="core-time-hello.cpp"\nint main() { return 0; }\n```\n\nIt returns.\n'

c_LintFailing = '\n'.join([
    'src/content/docs/core/time.md:25: word-list: "loop" (6 uses) is on no word list (style.md §2.3): use a listed word',
    'src/content/docs/core/time.md:30: word-list: "cube" is on no word list (style.md §2.3): use a listed word',
    'src/content/docs/core/time.md:48: sentence-max: this sentence has 47 words, more than 35: make two sentences',
    'src/content/docs/core/time.md:97: passive (warning): "is left" may be the passive voice',
    'src/content/figures/core/time.json:6: word-list: "vertical" is on no word list (style.md §2.3)',
    'tools/booklib/settings.py:5: literal-origin: the address is written only in site.json',
    'lint: 5 failing, 1 warning',
])


class Runner:
    """Answers each tool's run from a table of (code, stdout, stderr) by the tool's name and records the calls."""

    def __init__(self, answers=None):
        self.answers = answers or {}
        self.calls = []

    def __call__(self, argv, cwd, env):
        name = os.path.basename(argv[2])
        if name == 'excerpts.py':
            name = 'excerpts %s' % argv[3]
        if name == 'sketches.py' and argv[3] == 'fill':
            name = 'sketches fill'
        self.calls.append((name, argv, cwd, env))
        return self.answers.get(name, (0, '', ''))

    def names(self):
        return [name for name, _, _, _ in self.calls]

    def argv(self, name):
        return next(argv for called, argv, _, _ in self.calls if called == name)


class ParseTests(unittest.TestCase):
    def test_a_lint_finding_has_its_rule_as_key(self):
        line = pagecheck.parse_line('src/content/docs/core/time.md:48: sentence-max: this sentence has 47 words')
        self.assertEqual((line.kind, line.where, line.key, line.message),
                         ('finding', 'src/content/docs/core/time.md:48', 'sentence-max', 'this sentence has 47 words'))
        self.assertEqual(line.path, 'src/content/docs/core/time.md')

    def test_a_lint_warning_is_a_warning_under_its_rule(self):
        line = pagecheck.parse_line('src/content/docs/core/time.md:97: passive (warning): "is left" may be the passive voice')
        self.assertEqual((line.kind, line.key), ('warning', 'passive'))

    def test_names_groups_by_its_form(self):
        line = pagecheck.parse_line('src/content/docs/make/first-script.md:208: UI name: Play.: the editor has no "Play."')
        self.assertEqual((line.kind, line.key, line.message), ('finding', 'UI name', 'Play.: the editor has no "Play."'))

    def test_notes_infos_and_summaries_are_told_apart(self):
        self.assertEqual(pagecheck.parse_line('src/content/docs/core/time.md:8: note: O2: the Need is not written yet').kind, 'note')
        self.assertEqual(pagecheck.parse_line('src/content/docs/a/b.md:3: a table the dumps lack (note)').kind, 'note')
        self.assertEqual(pagecheck.parse_line('src/content/docs/core/time.md: filled 2 quotes').kind, 'info')
        self.assertEqual(pagecheck.parse_line('src/generated/vendor.json: written').kind, 'info')
        self.assertEqual(pagecheck.parse_line('lint: 58 failing, 7 warnings').kind, 'summary')
        self.assertEqual(pagecheck.parse_line('excerpts: 0 problems, 0 notes in 1 page at engine 822a7a46').kind, 'summary')

    def test_a_message_without_a_short_key_has_none(self):
        line = pagecheck.parse_line('src/content/docs/core/time.md:192: the quote differs from Strata/src/Strata/Scene/Scene.h at the pin: fill it')
        self.assertIsNone(line.key)

    def test_the_page_owns_its_manifest_pictures_sketches_and_tutorial(self):
        for path in ('src/content/docs/core/time.md', 'src/content/figures/core/time.json', 'src/assets/figures/core/time/a.avif',
                     'sketches/core-time-hello.cpp', 'tutorials/core/time.tutorial.json', 'tutorials/core/time/exercise-1.patch'):
            self.assertTrue(pagecheck.is_owned(path, 'core/time'), path)
        for path in ('src/content/docs/core/timeline.md', 'sketches/core-timeline-a.cpp', 'tools/booklib/settings.py', None):
            self.assertFalse(pagecheck.is_owned(path, 'core/time'), path)


class SummaryTests(unittest.TestCase):
    def test_a_whole_book_check_counts_only_the_page_s_files(self):
        outcome = pagecheck.summarize('lint', 1, c_LintFailing, '', 'core/time', whole_book=True)
        self.assertEqual(outcome.failing, 4)
        self.assertEqual(sorted((key, len(lines)) for key, lines in outcome.groups.items()), [('sentence-max', 1), ('word-list', 3)])
        self.assertEqual(outcome.warnings, {'passive': 1})
        self.assertEqual(outcome.outside, {'literal-origin': 1})

    def test_findings_only_in_other_files_pass(self):
        stdout = 'src/sidebar.json:89: O5: track "beginner" entry 30\npages: 1 page, 1 error, 0 notes'
        outcome = pagecheck.summarize('pages', 1, stdout, '', 'core/time', whole_book=True)
        self.assertEqual(outcome.failing, 0)
        self.assertEqual(outcome.outside, {'O5': 1})

    def test_a_check_of_the_page_counts_every_file(self):
        stdout = 'src/generated/vendor.json:1: the file is not what fill writes\nexcerpts: 1 problem, 0 notes in 1 page at engine 11111111'
        outcome = pagecheck.summarize('excerpts check', 1, stdout, '', 'core/time')
        self.assertEqual(outcome.failing, 1)
        self.assertEqual(list(outcome.groups), ['excerpts check'])

    def test_a_tool_that_cannot_run_is_one_failure_with_its_message(self):
        outcome = pagecheck.summarize('sketches', 2, '', 'sketches: glm is not at the commit the pin records\n', 'core/time')
        self.assertEqual(outcome.groups, {'could not run': ['sketches: glm is not at the commit the pin records']})

    def test_a_failure_without_a_finding_is_not_lost(self):
        outcome = pagecheck.summarize('names', 1, 'names: 1 finding', '', 'core/time')
        self.assertEqual(outcome.failing, 1)
        self.assertIn('names failed: names: 1 finding', outcome.groups['names'][0])

    def test_groups_show_at_most_five_lines_and_the_count(self):
        stdout = '\n'.join('src/content/docs/core/time.md:%d: word-list: "w%d" is on no word list %s' % (line, line, 'x' * 200)
                           for line in range(1, 9))
        lines = pagecheck.report_lines(pagecheck.summarize('lint', 1, stdout, '', 'core/time', whole_book=True))
        self.assertEqual(lines[0], 'lint: FAIL (8 failing)')
        self.assertEqual(lines[1], '  word-list: 8')
        shown = [line for line in lines if line.startswith('    src/')]
        self.assertEqual(len(shown), 5)
        self.assertGreater(len(shown[0]), pagecheck.c_Width)  # the first line of a group is whole
        self.assertTrue(all(len(line.strip()) <= pagecheck.c_Width and line.endswith('…') for line in shown[1:]))
        self.assertEqual(lines[7], '    (3 more)')

    def test_the_largest_group_comes_first(self):
        lines = pagecheck.report_lines(pagecheck.summarize('lint', 1, c_LintFailing, '', 'core/time', whole_book=True))
        self.assertEqual([line.strip() for line in lines if line.startswith('  ') and not line.startswith('    ')],
                         ['word-list: 3', 'sentence-max: 1', 'warnings: passive 1', 'other files, not counted: literal-origin 1'])


class EngineTests(unittest.TestCase):
    def test_the_option_then_the_variable_then_the_default_clone(self):
        folder = tempfile.mkdtemp()
        try:
            self.assertEqual(pagecheck.resolve_engine('a', {'STRATA_ENGINE': 'b'}, folder), 'a')
            self.assertEqual(pagecheck.resolve_engine(None, {'STRATA_ENGINE': 'b'}, folder), 'b')
            self.assertEqual(pagecheck.resolve_engine(None, {}, folder), folder)
            self.assertIsNone(pagecheck.resolve_engine(None, {}, os.path.join(folder, 'missing')))
        finally:
            shutil.rmtree(folder)

    def test_a_compiler_beside_the_interpreter_is_used_with_its_folder_on_the_path(self):
        folder = tempfile.mkdtemp()
        try:
            open(os.path.join(folder, 'g++.exe'), 'w').close()
            executable = os.path.join(folder, 'python.exe')
            child, notice, compile_them = pagecheck.compiler_environment({'PATH': 'elsewhere'}, executable, which=lambda name: None)
            self.assertTrue(compile_them)
            self.assertEqual(child['PATH'], folder + os.pathsep + 'elsewhere')
            self.assertIn('beside the Python interpreter', notice)
            self.assertEqual(pagecheck.compiler_environment({'CXX': 'clang++'}, executable, which=lambda name: None), (None, None, True))
            self.assertEqual(pagecheck.compiler_environment({}, executable, which=lambda name: '/usr/bin/g++'), (None, None, True))
            os.remove(os.path.join(folder, 'g++.exe'))
            child, notice, compile_them = pagecheck.compiler_environment({}, executable, which=lambda name: None)
            self.assertEqual((child, compile_them), (None, False))
            self.assertIn('not compiled', notice)
        finally:
            shutil.rmtree(folder)


class MainTests(unittest.TestCase):
    def setUp(self):
        self.book = helpers.TempBook(pin_commit=c_Pin)
        self.engine = tempfile.mkdtemp()
        self.book.write('reference/_dumps/%s/commands.json' % c_Pin, '{}')

    def tearDown(self):
        self.book.cleanup()
        shutil.rmtree(self.engine)

    def run_main(self, runner, page='core/time', *extra, environ=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = pagecheck.main([page, '--root', self.book.root, '--engine', self.engine] + list(extra), runner=runner,
                                  environ=environ or {}, which=lambda name: '/usr/bin/g++')
        return code, output.getvalue()

    def test_a_clean_page_passes_and_runs_the_page_s_tools_in_order(self):
        self.book.page('core/time', c_PageText)
        runner = Runner()
        code, output = self.run_main(runner)
        self.assertEqual(code, 0)
        self.assertEqual(runner.names(), ['markterms.py', 'lint.py', 'pages.py', 'names.py', 'excerpts fill', 'excerpts check'])
        self.assertEqual(output.splitlines()[-1], 'pagecheck: PASS')
        self.assertIn('names: passed', output)
        for name, argv, cwd, _ in runner.calls:
            self.assertEqual(argv[1], '-I')
            self.assertEqual(cwd, os.path.abspath(self.book.root))
            if name not in ('pages.py', 'markterms.py'):  # neither reads the engine
                self.assertEqual(argv[argv.index('--engine') + 1], self.engine)
        self.assertEqual(runner.argv('names.py')[runner.argv('names.py').index('--dumps') + 1],
                         os.path.join(os.path.abspath(self.book.root), 'reference', '_dumps', c_Pin))
        self.assertEqual(runner.argv('excerpts fill')[-1], 'core/time')
        self.assertEqual(runner.argv('markterms.py')[3:], ['core/time', '--root', os.path.abspath(self.book.root)])
        self.assertIn('markterms: 0 written', output)

    def test_markterms_fills_before_the_lint_and_its_count_is_no_failure(self):
        self.book.page('core/time', c_PageText)
        written = '\n'.join([
            'src/content/docs/core/time.md:25: mark: "loop" -> :term[loop]{id=loop}',
            'src/content/docs/core/time.md:30: left for the writer: "frame rate": its words stand in a link (note)',
            'markterms: 1 written (1 mark), 1 left for the writer'])
        code, output = self.run_main(Runner({'markterms.py': (0, written, '')}))
        self.assertEqual(code, 0)
        self.assertIn('markterms: 1 written (1 note)', output.splitlines())
        self.assertEqual(output.splitlines()[-1], 'pagecheck: PASS')
        code, output = self.run_main(Runner({'markterms.py': (2, '', 'markterms: the glossary cannot be read')}))
        self.assertEqual(code, 1)
        self.assertIn('markterms: FAIL (1 failing)', output)

    def test_failures_are_counted_on_the_last_line(self):
        self.book.page('core/time', c_PageText)
        runner = Runner({'lint.py': (1, c_LintFailing, ''), 'names.py': (1, 'src/content/docs/core/time.md:3: UI name: Play.: no "Play."\nnames: 1 finding', '')})
        code, output = self.run_main(runner)
        self.assertEqual(code, 1)
        self.assertEqual(output.splitlines()[-1], 'pagecheck: FAIL (5 failing)')
        self.assertIn('lint: FAIL (4 failing, 1 warning)', output)
        self.assertIn('names: FAIL (1 failing)', output)

    def test_sketches_figures_and_tutorials_run_when_the_page_has_them(self):
        self.book.page('core/time', c_SketchText)
        self.book.write('src/content/figures/core/time.json', '{"figures": []}')
        self.book.write('tutorials/core/time/exercise-2.patch', '')
        self.book.write('tutorials/core/time/exercise-1.tutorial.json', '{}')
        runner = Runner()
        code, _ = self.run_main(runner)
        self.assertEqual(code, 0)
        self.assertEqual(runner.names()[-3:], ['sketches.py', 'figures.py', 'tutorials.py'])
        self.assertNotIn('--no-compile', runner.argv('sketches.py'))
        self.assertEqual(runner.argv('tutorials.py')[-2:], ['core/time/exercise-1', 'core/time/exercise-2'])

    def test_the_sketches_check_counts_only_the_page_s_own_sketches(self):
        # sketches.py check <page> also compiles every other file of sketches/: another page's broken sketch is no
        # failure of this page (wave 1a's writers saw it fail theirs).
        self.book.page('core/time', c_SketchText)
        other = '\n'.join([
            'sketches/basics-bytes-bounds.cpp:1: the compiler refused it: error: missing include',
            'sketches: 1 problem'])
        code, output = self.run_main(Runner({'sketches.py': (1, other, '')}))
        self.assertEqual(code, 0)
        self.assertIn('  other files, not counted: ', output)
        self.assertEqual(output.splitlines()[-1], 'pagecheck: PASS')
        own = '\n'.join([
            'sketches/core-time-hello.cpp:1: the compiler refused it: error: missing include',
            'src/content/docs/core/time.md:9: the fence differs from sketches/core-time-hello.cpp',
            'sketches: 2 problems'])
        code, output = self.run_main(Runner({'sketches.py': (1, own, '')}))
        self.assertEqual(code, 1)
        self.assertEqual(output.splitlines()[-1], 'pagecheck: FAIL (2 failing)')

    def test_the_tutorials_check_counts_only_the_page_s_own_tutorial_files(self):
        # tutorials.py check <page> also reads the tutorial a stage starts from: a finding in that other page's file is
        # no failure of this page (wave 3's writers saw it fail theirs).
        self.book.page('core/time', c_PageText)
        self.book.write('tutorials/core/time/exercise-1.tutorial.json', '{}')
        other = '\n'.join([
            'tutorials/core/files.tutorial.json:12: error: stage 2 names no checkpoint',
            'tutorials: 1 error, 0 notes'])
        code, output = self.run_main(Runner({'tutorials.py': (1, other, '')}))
        self.assertEqual(code, 0)
        self.assertIn('  other files, not counted: ', output)
        self.assertEqual(output.splitlines()[-1], 'pagecheck: PASS')
        own = '\n'.join([
            'tutorials/core/time/exercise-1.tutorial.json:3: error: startsFrom names no tutorial',
            'tutorials: 1 error, 0 notes'])
        code, output = self.run_main(Runner({'tutorials.py': (1, own, '')}))
        self.assertEqual(code, 1)
        self.assertEqual(output.splitlines()[-1], 'pagecheck: FAIL (1 failing)')

    def test_the_prose_words_are_shown_in_every_run(self):
        # rulings-11.md, R54: the lint's own count beside the size's range, also when the page passes.
        self.book.page('core/time', c_PageText)
        words = 'src/content/docs/core/time.md: words: 6353 prose words; size L holds 4,001 to 6,500'
        code, output = self.run_main(Runner({'lint.py': (0, words + '\nlint: 0 failing, 0 warnings', '')}))
        self.assertEqual(code, 0)
        self.assertEqual(output.splitlines()[-2:], ['words: 6353 prose words; size L holds 4,001 to 6,500', 'pagecheck: PASS'])
        self.assertIn('lint: passed', output)  # the count is no finding
        code, output = self.run_main(Runner({'lint.py': (1, c_LintFailing + '\n' + words, '')}))
        self.assertEqual(output.splitlines()[-2], 'words: 6353 prose words; size L holds 4,001 to 6,500')
        code, output = self.run_main(Runner({'lint.py': (2, '', 'lint: the glossary cannot be read')}))
        self.assertEqual(output.splitlines()[-2], "words: not counted: the lint did not report the page's prose words")

    def test_fill_sketches_runs_the_fill_with_the_check_s_compiler(self):
        self.book.page('core/time', c_SketchText)
        runner = Runner()
        self.run_main(runner)
        self.assertNotIn('sketches fill', runner.names())
        runner = Runner()
        code, output = self.run_main(runner, 'core/time', '--fill-sketches')
        self.assertEqual(code, 0)
        self.assertEqual(runner.names()[-2:], ['sketches fill', 'sketches.py'])
        self.assertEqual(runner.argv('sketches fill')[3:5], ['fill', '--engine'])
        self.assertEqual(runner.argv('sketches fill')[-1], 'core/time')
        self.assertIn('sketches fill: passed', output)
        # Without a compiler on the PATH, the one beside the interpreter serves the fill as it serves the check.
        folder = tempfile.mkdtemp()
        try:
            open(os.path.join(folder, 'g++.exe'), 'w').close()
            runner = Runner()
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                pagecheck.main(['core/time', '--root', self.book.root, '--engine', self.engine, '--fill-sketches'], runner=runner,
                               environ={'PATH': 'elsewhere'}, executable=os.path.join(folder, 'python.exe'), which=lambda name: None)
            fill_env = next(env for name, _, _, env in runner.calls if name == 'sketches fill')
            self.assertTrue(fill_env['PATH'].startswith(folder + os.pathsep))
            self.assertNotIn('--no-compile', runner.argv('sketches fill'))
        finally:
            shutil.rmtree(folder)

    def test_the_slangc_of_the_engine_s_toolchain_cache_serves_the_sketches_without_one_on_the_path(self):
        self.book.page('core/time', c_SketchText)
        folder = tempfile.mkdtemp()
        try:
            slangc = os.path.join(folder, 'Strata', 'Toolchains', 'slang-2026.20-windows_x86_64', 'bin', 'slangc.exe')
            os.makedirs(os.path.dirname(slangc))
            open(slangc, 'w').close()
            open(os.path.join(folder, 'g++.exe'), 'w').close()
            runner = Runner()
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                pagecheck.main(['core/time', '--root', self.book.root, '--engine', self.engine, '--fill-sketches'], runner=runner,
                               environ={'PATH': 'elsewhere', 'LOCALAPPDATA': folder}, executable=os.path.join(folder, 'python.exe'),
                               which=lambda name: None)
            for name in ('sketches fill', 'sketches.py'):
                argv = runner.argv(name)
                self.assertEqual(argv[argv.index('--slangc') + 1], slangc)
            self.assertEqual(pagecheck.slangc_arguments({'LOCALAPPDATA': folder}, which=lambda name: '/usr/bin/slangc'), [])
            self.assertEqual(pagecheck.slangc_arguments({}, which=lambda name: None), [])
        finally:
            shutil.rmtree(folder)

    def test_a_tutorial_file_is_checked_by_its_page_id(self):
        self.book.page('core/time', c_PageText)
        self.book.write('tutorials/core/time.tutorial.json', '{}')
        runner = Runner()
        self.run_main(runner)
        self.assertEqual(runner.argv('tutorials.py')[-1], 'core/time')

    def test_without_the_dumps_names_is_skipped_with_a_notice(self):
        self.book.page('core/time', c_PageText)
        helpers.remove_tree(self.book.path('reference/_dumps'))
        runner = Runner()
        code, output = self.run_main(runner)
        self.assertEqual(code, 0)
        self.assertNotIn('names.py', runner.names())
        self.assertIn('names: skipped: no dumps at reference/_dumps/%s' % c_Pin, output)

    def test_a_part_s_index_and_review_pages_are_checked_by_the_tools_names(self):
        # plan/site.md, "Part pages": core/index.md is the page "core" to the tools, under either name.
        self.book.page('core/index', '---\nid: core/index\ngenerated: index\n---\n\nThe part.\n')
        self.book.page('core/review', '---\nid: core/review\ngenerated: review\n---\n\n## Cumulative exercises\n')
        for named in ('core/index', 'core'):
            runner = Runner({'lint.py': (1, 'src/content/docs/core/index.md:7: sentence-max: this sentence has 37 words\nlint: 1 failing', '')})
            code, output = self.run_main(runner, named)
            self.assertEqual(code, 1, output)
            self.assertIn('a part page (generated: index)', output)
            self.assertNotIn('could not run', output)
            self.assertEqual(runner.argv('markterms.py')[3], 'core')
            self.assertEqual(runner.argv('lint.py')[3], 'core')
            self.assertEqual(runner.argv('names.py')[-1], 'core')
            self.assertEqual(runner.argv('excerpts check')[-1], 'core')
            self.assertIn('sentence-max: 1', output)  # the index page's own file counts in the whole-book lint
        runner = Runner()
        code, output = self.run_main(runner, 'core/review')
        self.assertEqual(code, 0, output)
        self.assertIn('a part page (generated: review)', output)
        self.assertEqual(runner.argv('lint.py')[3], 'core/review')

    def test_the_tools_name_a_part_s_index_page_by_its_url(self):
        from booklib import repo
        self.assertEqual([repo.named_page(name) for name in ('core/index', 'core', 'core/index.md', 'core/time', '/core/time/', 'index')],
                         ['core', 'core', 'core', 'core/time', 'core/time', 'index'])

    def test_a_missing_page_or_engine_is_a_usage_error(self):
        code, output = self.run_main(Runner(), 'core/missing')
        self.assertEqual(code, 2)
        self.assertIn('no page src/content/docs/core/missing.md', output)
        self.book.page('core/time', c_PageText)
        output = io.StringIO()
        with mock.patch.object(pagecheck, 'c_PinClone', os.path.join(self.engine, 'missing')),                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = pagecheck.main(['core/time', '--root', self.book.root], runner=Runner(), environ={})
        self.assertEqual(code, 2)
        self.assertIn('--engine', output.getvalue())


if __name__ == '__main__':
    unittest.main()

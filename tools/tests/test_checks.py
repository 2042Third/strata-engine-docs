"""measure.py and budgets.py (figures.py: test_figures.py; sketches.py: test_sketches.py; pages.py: test_pages.py; lint.py:
test_lint.py)."""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import budgets
import measure


def quiet_run(function, *arguments):
    return quiet(function, *arguments)


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


class MeasureTests(unittest.TestCase):
    def test_measures_a_command_and_its_children(self):
        folder = tempfile.mkdtemp()
        try:
            result_file = os.path.join(folder, 'result.jsonl')
            child = 'import subprocess, sys; subprocess.run([sys.executable, "-c", "x = bytearray(80 * 2**20); import time; time.sleep(1)"])'
            with contextlib.redirect_stderr(io.StringIO()):
                code = measure.main(['--label', 'test', '--json', result_file, '--', sys.executable, '-c', child])
            self.assertEqual(code, 0)
            with open(result_file, encoding='utf-8') as file:
                result = json.loads(file.readline())
            self.assertEqual(result['label'], 'test')
            self.assertGreater(result['seconds'], 0.9)
            self.assertGreater(result['peak_tree_bytes'], 80 * 2**20)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_command_s_own_cpu_time_is_not_counted_as_other_programs(self):
        folder = tempfile.mkdtemp()
        try:
            result_file = os.path.join(folder, 'result.jsonl')
            # Two processors busy for 1.5 s in the command's tree: a child and its parent.
            spin = 'import time\nend = time.time() + 1.5\nwhile time.time() < end: pass'
            child = 'import subprocess, sys; p = subprocess.Popen([sys.executable, "-c", %r]); exec(%r); p.wait()' % (spin, spin)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(measure.main(['--json', result_file, '--', sys.executable, '-c', child]), 0)
            with open(result_file, encoding='utf-8') as file:
                result = json.loads(file.readline())
            self.assertGreater(result['cpu_seconds'], 2.4)
            self.assertIsNotNone(result['other_load'])
            self.assertGreaterEqual(result['other_cpu_seconds'], 0)
            self.assertEqual(result['cpu_count'], os.cpu_count())
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_env_reaches_the_command_and_its_exit_code_comes_back(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code = measure.main(['--env', 'BOOK_TEST_VALUE=7', '--', sys.executable, '-c', 'import os, sys; sys.exit(int(os.environ["BOOK_TEST_VALUE"]))'])
        self.assertEqual(code, 7)


class BudgetTests(unittest.TestCase):
    def test_measurements_against_the_budgets(self):
        limits = {'build_cold_seconds': 100, 'build_cached_seconds': 10, 'build_peak_megabytes': 1000, 'site_megabytes': 50,
                  'largest_page_gzip_kilobytes': 100, 'largest_page_kilobytes': 800, 'largest_print_view_gzip_kilobytes': 2000,
                  'search_index_megabytes': 5, 'search_query_kilobytes': 300}
        measure_result = {'seconds': 50, 'peak_tree_bytes': 500 * 2**20}
        crawl = {'summary': {'site_bytes': 40e6, 'search_index_bytes': 6e6, 'seconds': 10, 'largest_pages': [{'url': 'a', 'bytes': 700 * 1024, 'gzip_bytes': 90 * 1024}],
                             'largest_print_pages': [{'url': 'print/a', 'bytes': 9e6, 'gzip_bytes': 1500 * 1024}]}}
        rows, failures, unjudged = budgets.check(limits, measure_result, crawl, {'bytes': 200 * 1024}, False, 1.0)
        self.assertEqual([row[0] for row in failures], ['search index'])
        self.assertEqual(unjudged, [])
        rows, failures, _ = budgets.check(limits, measure_result, None, None, True, 1.0)
        self.assertEqual([row[0] for row in failures], ['build time (cached)'])
        rows, failures, _ = budgets.check(limits, measure_result, None, None, True, 6.0)
        self.assertEqual(failures, [])

    def test_the_raw_page_budget_takes_the_largest_raw_page(self):
        limits = {'site_megabytes': 50, 'largest_page_gzip_kilobytes': 100, 'largest_page_kilobytes': 800, 'largest_print_view_gzip_kilobytes': 2000,
                  'search_index_megabytes': 5}
        # The largest compressed page is not the largest one as it is.
        crawl = {'summary': {'site_bytes': 1e6, 'search_index_bytes': 1e6, 'seconds': 1, 'largest_pages': [{'url': 'a', 'bytes': 300 * 1024, 'gzip_bytes': 90 * 1024}, {'url': 'b', 'bytes': 900 * 1024, 'gzip_bytes': 50 * 1024}]}}
        _, failures, _ = budgets.check(limits, None, crawl, None, False, 1.0)
        self.assertEqual([row[0] for row in failures], ['largest page'])

    def test_a_time_measured_on_a_busy_machine_is_not_judged(self):
        limits = {'build_cold_seconds': 100, 'build_cached_seconds': 70, 'build_peak_megabytes': 1000, 'quiet_other_load': 2.0}
        quiet = {'seconds': 60, 'peak_tree_bytes': 500 * 2**20, 'other_load': 1.4}
        loaded = {'seconds': 80, 'peak_tree_bytes': 500 * 2**20, 'other_load': 3.1}
        _, failures, unjudged = budgets.check(limits, quiet, None, None, True, 1.0)
        self.assertEqual((failures, unjudged), ([], []))
        _, failures, unjudged = budgets.check(limits, loaded, None, None, True, 1.0)
        self.assertEqual(failures, [])
        self.assertEqual([row[0] for row in unjudged], ['build time (cached)'])
        self.assertIn('3.1 processors', unjudged[0][4])
        folder = tempfile.mkdtemp(prefix='budgets-')
        try:
            path = os.path.join(folder, 'measure.jsonl')
            with open(path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(dict(loaded, label='build')) + '\n')
            with open(os.path.join(folder, 'budgets.json'), 'w', encoding='utf-8') as file:
                json.dump(limits, file)
            code, output = quiet_run(budgets.main, '--budgets', os.path.join(folder, 'budgets.json'), '--measure', path, '--cached')
            self.assertEqual(code, 2, output)
            self.assertIn('not judged', output)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()

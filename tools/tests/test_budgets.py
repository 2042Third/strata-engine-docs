"""budgets.py (its first rows are also tested in test_checks.py): the rule of rulings 5, R14 for budgets.json, the
pass marks beside the budgets, the rows of budget rows 9 to 12, and what a busy machine's times count for."""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

# The tools and this folder as packages, however unittest was started (see test_crawl.py).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import budgets  # noqa: E402


class SearchBudgetTests(unittest.TestCase):
    limits = {'search_query_kilobytes': 300, 'search_next_query_kilobytes': 100}

    def test_the_next_search_has_a_budget_of_its_own(self):
        search = {'bytes': 200 * 1024, 'nextBytes': 40 * 1024}
        rows, failures, _ = budgets.check(self.limits, None, None, search, False, 1.0)
        self.assertEqual([(row[0], row[2]) for row in rows], [('one search (two words)', 300), ('the next search', 100)])
        self.assertEqual(failures, [])
        _, failures, _ = budgets.check(self.limits, None, None, dict(search, nextBytes=101 * 1024), False, 1.0)
        self.assertEqual([row[0] for row in failures], ['the next search'])

    def test_a_report_without_a_next_query_checks_the_first_only(self):
        rows, failures, _ = budgets.check(self.limits, None, None, {'bytes': 310 * 1024}, False, 1.0)
        self.assertEqual([row[0] for row in rows], ['one search (two words)'])
        self.assertEqual([row[0] for row in failures], ['one search (two words)'])

    def test_the_committed_budgets_hold_the_next_search_at_its_pass_mark(self):
        with open(budgets.c_Budgets, encoding='utf-8') as file:
            committed = json.load(file)
        # site.md's pass mark; R14 lowers a budget only from a full-scale measurement, which the next query has none of.
        self.assertLessEqual(committed['search_next_query_kilobytes'], 100)
        self.assertLessEqual(committed['search_query_kilobytes'], 300)


class RuleTests(unittest.TestCase):
    """rulings 5, R14: each budget is at most the smaller of its pass mark and 1.5 times the latest full-scale
    measurement, rounded up to two digits."""

    def committed(self):
        with open(budgets.c_Budgets, encoding='utf-8') as file:
            return json.load(file)

    def test_rounding_up_to_two_digits(self):
        cases = {70.5: 71, 4810.5: 4900, 9.45: 9.5, 262.2: 270, 539.7: 540, 48.3: 49, 66: 66, 4800: 4800, 0.123: 0.13, 100: 100}
        for value, expected in cases.items():
            self.assertEqual(budgets.round_up_two_digits(value), expected, value)

    def test_the_committed_budgets_keep_the_rule_and_the_pass_marks_are_site_md_s(self):
        committed = self.committed()
        self.assertEqual(budgets.file_problems(committed), [])
        # plan/site.md's table; only a ruling changes it (R14).
        self.assertEqual(committed['pass_marks'], {
            'build_cached_seconds': 240, 'build_cold_seconds': 1800, 'build_peak_megabytes': 6144, 'site_megabytes': 400,
            'site_files': 15000, 'largest_page_gzip_kilobytes': 300, 'median_page_gzip_kilobytes': 60,
            'scripts_per_page_gzip_kilobytes': 40, 'search_query_kilobytes': 300, 'search_next_query_kilobytes': 100})
        # R14's own example: the site's size is 400 MB, not 540. R61: row 7 passes at 6 GB by its remedy, and 1.5 times
        # the real book's peak (4,828 MiB on ubuntu-latest) is above it, so the pass mark is the budget.
        self.assertEqual(budgets.ceiling(committed, 'site_megabytes'), 400)
        self.assertEqual(budgets.ceiling(committed, 'build_peak_megabytes'), 6144)
        # The scale test's measurements (2,018 files, 115.4 and 78.9 MB of HTML) set the other ceilings.
        self.assertEqual(budgets.ceiling(committed, 'site_files'), 3100)
        self.assertEqual(budgets.ceiling(committed, 'chapter_html_megabytes'), 180)
        self.assertEqual(budgets.ceiling(committed, 'print_html_megabytes'), 120)

    def test_a_budget_above_its_ceiling_or_missing_fails(self):
        committed = self.committed()
        for key, value in (('site_megabytes', 540), ('median_page_gzip_kilobytes', 61), ('largest_page_kilobytes', 2800)):
            with self.subTest(key=key):
                problems = budgets.file_problems(dict(committed, **{key: value}))
                self.assertEqual(len(problems), 1, problems)
                self.assertIn('%s is %s, above' % (key, value), problems[0])
        # A measurement that went down lowers the ceiling: the budget must follow it.
        lower = json.loads(json.dumps(committed))
        lower['measured']['largest_page_kilobytes'] = 1000.0
        self.assertIn('largest_page_kilobytes is 1700, above 1500', budgets.file_problems(lower)[0])
        missing = dict(committed)
        del missing['scripts_per_page_gzip_kilobytes']
        self.assertIn('scripts_per_page_gzip_kilobytes has no budget (its ceiling is 15)', budgets.file_problems(missing))
        extra = dict(committed, pass_marks=dict(committed['pass_marks'], other=1))
        self.assertTrue(any('pass_marks names other, which is no budget' in problem for problem in budgets.file_problems(extra)))

    def test_main_refuses_a_budgets_file_that_breaks_the_rule(self):
        folder = tempfile.mkdtemp(prefix='budgets-rule-')
        try:
            path = os.path.join(folder, 'budgets.json')
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(dict(self.committed(), site_megabytes=540), file)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(budgets.main(['--budgets', path, '--check-file']), 1)
                self.assertEqual(budgets.main(['--budgets', path]), 1)
            self.assertIn('site_megabytes is 540, above 400', output.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(budgets.main(['--check-file']), 0)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class RowTests(unittest.TestCase):
    limits = {'site_megabytes': 400, 'site_files': 100, 'chapter_html_megabytes': 1, 'print_html_megabytes': 1,
              'largest_page_gzip_kilobytes': 300, 'median_page_gzip_kilobytes': 60, 'largest_page_kilobytes': 800,
              'largest_print_view_gzip_kilobytes': 2000, 'scripts_per_page_gzip_kilobytes': 40, 'search_index_megabytes': 5,
              'build_cold_seconds': 100, 'quiet_other_load': 2.0}

    def summary(self, **values):
        summary = {'site_bytes': 1e6, 'site_files': 50, 'chapter_html_bytes': 5e5, 'print_html_bytes': 5e5,
                   'median_page_gzip_bytes': 30 * 1024, 'scripts_per_page_gzip_bytes': 20 * 1024, 'search_index_bytes': 1e6,
                   'seconds': 1, 'largest_pages': [{'url': 'a', 'bytes': 100 * 1024, 'gzip_bytes': 20 * 1024}], 'largest_print_pages': []}
        summary.update(values)
        return {'summary': summary}

    def test_rows_9_to_11_have_budgets_of_their_own(self):
        rows, failures, _ = budgets.check(self.limits, None, self.summary(), None, False, 1.0)
        self.assertEqual(failures, [])
        self.assertIn('HTML of the print views', [row[0] for row in rows])
        over = self.summary(site_files=101, chapter_html_bytes=2e6, print_html_bytes=3e6, median_page_gzip_bytes=61 * 1024, scripts_per_page_gzip_bytes=41 * 1024)
        _, failures, _ = budgets.check(self.limits, None, over, None, False, 1.0)
        self.assertEqual(sorted(row[0] for row in failures), sorted(['site files', 'HTML of the chapter pages', 'HTML of the print views', 'median page (gzip)', 'scripts of a page (gzip)']))
        # An older crawl report without these fields checks the rows it has.
        rows, _, _ = budgets.check(self.limits, None, {'summary': {'site_bytes': 1e6, 'search_index_bytes': 1, 'seconds': 1, 'largest_pages': []}}, None, False, 1.0)
        self.assertNotIn('median page (gzip)', [row[0] for row in rows])

    def test_a_time_within_its_budget_passes_under_load_and_one_over_it_is_not_judged(self):
        # rulings 5, R14: load only makes a build slower, so a time that passes under load passes; one over its mark
        # under load says nothing and is measured again, and it never counts as a pass.
        loaded = {'seconds': 90, 'peak_tree_bytes': 1, 'other_load': 3.0}
        rows, failures, unjudged = budgets.check(self.limits, loaded, None, None, False, 1.0)
        self.assertEqual((failures, unjudged), ([], []))
        self.assertEqual(rows[0][4], None)
        _, failures, unjudged = budgets.check(self.limits, dict(loaded, seconds=120), None, None, False, 1.0)
        self.assertEqual(failures, [])
        self.assertEqual([row[0] for row in unjudged], ['build time (cold)'])
        _, failures, unjudged = budgets.check(self.limits, dict(loaded, seconds=120, other_load=1.0), None, None, False, 1.0)
        self.assertEqual(([row[0] for row in failures], unjudged), (['build time (cold)'], []))

    def test_the_crawl_s_time_is_recorded_and_never_judged(self):
        # rulings 13, R60: the crawl's time, lychee included, is printed as a measurement of the machine that ran it,
        # without a limit; it never fails a run or holds it, whatever the load and whatever budgets.json holds.
        for limits in (self.limits, dict(self.limits, crawl_seconds=48)):
            rows, failures, unjudged = budgets.check(limits, None, self.summary(seconds=500), None, False, 1.0)
            self.assertNotIn('crawl time', [row[0] for row in rows])
            self.assertEqual((failures, unjudged), ([], []))
        lines = budgets.recorded(self.summary(seconds=116.6), {'other_load': 1.26})
        self.assertIn('crawl time (lychee included): 116.6 s on this machine, other load 1.3 (recorded without a limit, rulings 13, R60)', lines)
        self.assertIn('crawl time (lychee included): 116.6 s on this machine (recorded without a limit, rulings 13, R60)', budgets.recorded(self.summary(seconds=116.6)))

    def test_budgets_json_holds_no_crawl_budget_and_refuses_one(self):
        with open(budgets.c_Budgets, encoding='utf-8') as file:
            committed = json.load(file)
        self.assertNotIn('crawl_seconds', committed)
        # The measurement as CI takes it (lychee included, R59), kept beside the budgets as a record.
        self.assertEqual(committed['measured']['crawl_seconds'], [116.6])
        problems = budgets.file_problems(dict(committed, crawl_seconds=48))
        self.assertEqual(problems, ['crawl_seconds is recorded without a limit (rulings 13, R60): budgets.json holds no budget for it'])

    def test_main_prints_the_crawl_s_time_and_passes_a_slow_crawl(self):
        folder = tempfile.mkdtemp(prefix='budgets-crawl-')
        try:
            crawl = os.path.join(folder, 'crawl.json')
            with open(crawl, 'w', encoding='utf-8') as file:
                json.dump(self.summary(seconds=900.0), file)
            limits = os.path.join(folder, 'budgets.json')
            with open(limits, 'w', encoding='utf-8') as file:
                json.dump(self.limits, file)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(budgets.main(['--budgets', limits, '--crawl', crawl]), 0)
            self.assertIn('crawl time (lychee included): 900.0 s on this machine (recorded without a limit, rulings 13, R60)', output.getvalue())
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_build_s_peak_memory_is_recorded_per_program(self):
        lines = budgets.recorded(None, None, {'peak_by_program': {'pagefind': 700 * 2**20, 'node': 4100.25 * 2**20}})
        self.assertEqual(lines, ['build peak memory by program: node 4100.2 MB, pagefind 700.0 MB (each its own peak; recorded)'])
        self.assertEqual(budgets.recorded(None, None, {'peak_tree_bytes': 1}), [])

    def test_the_sidebar_s_share_is_recorded(self):
        lines = budgets.recorded(self.summary(sidebar_bytes=74 * 1024, sidebar_share=0.16))
        self.assertEqual(lines[1:], ['the sidebar: 74.0 KB, 16.0 % of its page (recorded, plan/site.md row 10)'])


if __name__ == '__main__':
    unittest.main()

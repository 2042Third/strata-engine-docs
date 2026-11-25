#!/usr/bin/env python3
"""Check 12: the build's measurements against the regression budgets of tools/budgets.json, beside the pass marks of
plan/site.md's budget table (plan/critique/rulings-5.md, R13 and R14).

    python tools/budgets.py --measure measure.jsonl [--label build] [--cached] --crawl crawl.json --search search.json
    python tools/budgets.py --check-file            only the rule below, for budgets.json itself

The pass marks are the design's: plan/site.md's table holds them, and only a ruling changes them; budgets.json copies
them under "pass_marks". The budgets are what CI enforces: each is at most the smaller of its row's pass mark and 1.5
times the latest full-scale measurement ("measured"), rounded up to two digits, so a budget goes down whenever a
measurement allows it and never stands above that ceiling; a measure without a pass mark (the raw page, the print
views, the search index) has the measurement's ceiling only, one without a measurement its pass mark only. budgets.py
refuses a budgets.json whose budget stands above its ceiling or lacks one (exit 1).

The crawl's time is recorded, not judged (plan/critique/rulings-13.md, R60): it is the seconds of tools/crawl.py's
report, lychee included as CI runs it, printed with the load of the crawl's measurement (--crawl-label, "crawl") as a
measurement of the machine that ran it, without a limit. It never fails a run or holds it, and budgets.json holds no
budget for it (a faster crawl gets one per machine by a ruling).

--measure is what tools/measure.py appended (the last line with the label is used), --crawl the report of
tools/crawl.py --report, --search what scripts/search-payload.mjs --json wrote. Times compare with the cold-build
budget unless --cached says the caches were full. A missing input skips its budgets (and says so). Times and memory
were measured on the reference machine (i7-13700K); a slower machine gets the factor --slower (default 1).

Times and load: tools/measure.py records how many processors other programs kept busy during the run ("other_load").
A time within its budget passes whatever the load, because load only makes it slower; a time over its budget while
the load was above budgets.json's "quiet_other_load" is not judged: the row stays open and is measured again, and
the exit code is 2. A time that is not judged never counts as a pass.

Only the standard library is used. Exit codes: 0 within budget, 1 over budget or a budgets.json that breaks the rule,
2 usage errors or a time over its budget on a busy machine.
"""

import argparse
import decimal
import json
import os
import sys

c_Budgets = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'budgets.json')
# The regression budgets and where plan/site.md's budget table puts each: the row, or None for a measure the table has
# no row for (R14 still gives it a budget from its measurement).
c_BudgetRows = {
    'build_cold_seconds': 3, 'build_cached_seconds': 1, 'build_peak_megabytes': 7,
    'site_megabytes': 9, 'site_files': 9, 'chapter_html_megabytes': 9, 'print_html_megabytes': 9,
    'largest_page_gzip_kilobytes': 10, 'median_page_gzip_kilobytes': 10, 'largest_page_kilobytes': None,
    'largest_print_view_gzip_kilobytes': None, 'scripts_per_page_gzip_kilobytes': 11, 'search_index_megabytes': None,
    'search_query_kilobytes': 12, 'search_next_query_kilobytes': 12,
}
# Rows that are times: only these depend on the load of the machine.
c_Times = ('build_cold_seconds', 'build_cached_seconds')
# Measures that are recorded with every run and never judged, so budgets.json holds no budget for them (R60).
c_Recorded = ('crawl_seconds',)


def round_up_two_digits(value):
    """The smallest number of two significant digits that is not below `value` (70.5 → 71, 4810.5 → 4900, 9.45 → 9.5)."""
    number = decimal.Decimal(repr(float(value)))
    if number <= 0:
        return 0
    step = decimal.Decimal(1).scaleb(number.adjusted() - 1)
    rounded = (number / step).to_integral_value(rounding=decimal.ROUND_CEILING) * step
    result = float(rounded)
    return int(result) if result == int(result) else result


def ceiling(budgets, key):
    """The highest budget R14 allows for `key`: the smaller of the pass mark and 1.5 times the latest full-scale
    measurement (its largest value), rounded up to two digits; None when neither exists."""
    candidates = []
    passes = budgets.get('pass_marks') or {}
    if passes.get(key) is not None:
        candidates.append(passes[key])
    measured = (budgets.get('measured') or {}).get(key)
    if measured is not None:
        values = measured if isinstance(measured, list) else [measured]
        if values:
            candidates.append(round_up_two_digits(1.5 * max(values)))
    return min(candidates) if candidates else None


def file_problems(budgets):
    """What breaks R14 in a budgets.json that holds pass marks: a budget missing, a budget above its ceiling, a pass
    mark for a measure that has no budget."""
    if 'pass_marks' not in budgets:
        return []
    problems = []
    for key in c_BudgetRows:
        limit = ceiling(budgets, key)
        if key not in budgets:
            problems.append('%s has no budget (its ceiling is %s)' % (key, limit))
        elif limit is not None and budgets[key] > limit:
            problems.append('%s is %s, above %s, the smaller of its pass mark and 1.5 times its latest measurement (rulings 5, R14): '
                            'lower it, or ask the planner for a ruling that names what grew' % (key, budgets[key], limit))
    for key in c_Recorded:
        if key in budgets:
            problems.append('%s is recorded without a limit (rulings 13, R60): budgets.json holds no budget for it' % key)
    for key in budgets['pass_marks']:
        if key not in c_BudgetRows:
            problems.append('pass_marks names %s, which is no budget of tools/budgets.py' % key)
    return problems


def load_measure(path, label):
    found = None
    with open(path, encoding='utf-8') as file:
        for line in file:
            if line.strip():
                entry = json.loads(line)
                if entry.get('label') == label:
                    found = entry
    if found is None:
        raise ValueError('%s has no measurement labelled %r' % (path, label))
    return found


def busy(budgets, measure):
    """Why a time over its budget measured with `measure` cannot be judged (other programs kept the machine busy), or
    None."""
    load = (measure or {}).get('other_load')
    quiet = budgets.get('quiet_other_load')
    if load is None or quiet is None or load <= quiet:
        return None
    return 'not judged: other programs kept %.1f processors busy (quiet is %.1f or less); measure again on a quiet machine' % (load, quiet)


def check(budgets, measure, crawl, search, cached, slower):
    """(rows, failures, unjudged): rows are (name, measured, limit, unit, note) of every budget that had a
    measurement; unjudged are the rows whose time was over its budget on a busy machine. A row whose budget the
    file does not hold is left out, and so is the crawl's time, which recorded() prints without a limit (R60)."""
    rows = []

    def add(name, measured, key, unit, factor=1.0, load_measure=None):
        if key not in budgets or key in c_Recorded or measured is None:
            return
        limit = budgets[key] * factor
        note = busy(budgets, load_measure) if key in c_Times and measured > limit else None
        rows.append((name, measured, limit, unit, note))

    if measure:
        key = 'build_cached_seconds' if cached else 'build_cold_seconds'
        add('build time (%s)' % ('cached' if cached else 'cold'), measure['seconds'], key, 's', slower, measure)
        add('build peak memory', measure['peak_tree_bytes'] / 2**20, 'build_peak_megabytes', 'MB')
    if crawl:
        summary = crawl['summary']
        empty = {'bytes': 0, 'gzip_bytes': 0}
        largest = max(summary['largest_pages'], key=lambda page: page['gzip_bytes'], default=empty)
        largest_print = max(summary.get('largest_print_pages', []), key=lambda page: page['gzip_bytes'], default=empty)
        largest_raw = max(summary['largest_pages'], key=lambda page: page['bytes'], default=empty)

        def field(name, divisor):
            return summary[name] / divisor if name in summary else None
        add('site size', summary['site_bytes'] / 1e6, 'site_megabytes', 'MB')
        add('site files', summary.get('site_files'), 'site_files', '')
        add('HTML of the chapter pages', field('chapter_html_bytes', 1e6), 'chapter_html_megabytes', 'MB')
        add('HTML of the print views', field('print_html_bytes', 1e6), 'print_html_megabytes', 'MB')
        add('largest page (gzip)', largest['gzip_bytes'] / 1024, 'largest_page_gzip_kilobytes', 'KB')
        add('median page (gzip)', field('median_page_gzip_bytes', 1024), 'median_page_gzip_kilobytes', 'KB')
        # The largest page as it is, which need not be the largest compressed one.
        add('largest page', largest_raw['bytes'] / 1024, 'largest_page_kilobytes', 'KB')
        add('largest print view (gzip)', largest_print['gzip_bytes'] / 1024, 'largest_print_view_gzip_kilobytes', 'KB')
        add('scripts of a page (gzip)', field('scripts_per_page_gzip_bytes', 1024), 'scripts_per_page_gzip_kilobytes', 'KB')
        add('search index', summary['search_index_bytes'] / 1e6, 'search_index_megabytes', 'MB')
    if search:
        add('one search (two words)', search['bytes'] / 1024, 'search_query_kilobytes', 'KB')
        # The query after it reuses what the first one loaded (site.md, budget row 12); older reports have no such query.
        if 'nextBytes' in search:
            add('the next search', search['nextBytes'] / 1024, 'search_next_query_kilobytes', 'KB')
    unjudged = [row for row in rows if row[4]]
    failures = [row for row in rows if not row[4] and row[1] > row[2]]
    return rows, failures, unjudged


def recorded(crawl, crawl_measure=None):
    """What is recorded without a budget: the crawl's time, lychee included, on the machine that ran it, with the load
    of its measurement when there is one (R60); row 10's share of the sidebar in the page that carries the most of it."""
    summary = (crawl or {}).get('summary') or {}
    lines = []
    if summary.get('seconds') is not None:
        load = (crawl_measure or {}).get('other_load')
        lines.append('crawl time (lychee included): %.1f s on this machine%s (recorded without a limit, rulings 13, R60)' % (
            summary['seconds'], ', other load %.1f' % load if load is not None else ''))
    if 'sidebar_bytes' in summary:
        lines.append('the sidebar: %.1f KB, %.1f %% of its page (recorded, plan/site.md row 10)' % (summary['sidebar_bytes'] / 1024, summary['sidebar_share'] * 100))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description='Checks the build\'s measurements against tools/budgets.json.')
    parser.add_argument('--budgets', default=c_Budgets)
    parser.add_argument('--check-file', action='store_true', help='only check budgets.json against its pass marks and measurements')
    parser.add_argument('--measure', help='JSON lines of tools/measure.py')
    parser.add_argument('--label', default='build', help='the measurement\'s label (default build)')
    parser.add_argument('--crawl-label', default='crawl', help='the label of the crawl\'s measurement in --measure, if any (default crawl)')
    parser.add_argument('--cached', action='store_true', help='the caches were full: compare with the cached-build budget')
    parser.add_argument('--crawl', help='the report of tools/crawl.py --report')
    parser.add_argument('--search', help='the JSON of scripts/search-payload.mjs --json')
    parser.add_argument('--slower', type=float, default=1.0, help='time factor of this machine against the reference machine')
    options = parser.parse_args(argv)
    try:
        with open(options.budgets, encoding='utf-8') as file:
            budgets = json.load(file)
        measure = load_measure(options.measure, options.label) if options.measure else None
        crawl_measure = None
        if options.measure:
            try:
                crawl_measure = load_measure(options.measure, options.crawl_label)
            except ValueError:
                crawl_measure = None
        crawl = None
        search = None
        if options.crawl:
            with open(options.crawl, encoding='utf-8') as file:
                crawl = json.load(file)
        if options.search:
            with open(options.search, encoding='utf-8') as file:
                search = json.loads(file.read())
    except (OSError, ValueError, KeyError) as error:
        print('budgets: %s' % error, file=sys.stderr)
        return 2
    broken = file_problems(budgets)
    for problem in broken:
        print('budgets: %s' % problem)
    if options.check_file:
        print('budgets: %s' % ('%d problem%s in %s' % (len(broken), '' if len(broken) == 1 else 's', options.budgets) if broken else 'every budget is within its ceiling'))
        return 1 if broken else 0
    rows, failures, unjudged = check(budgets, measure, crawl, search, options.cached, options.slower)
    passes = budgets.get('pass_marks') or {}
    for name, measured, limit, unit, note in rows:
        print('%-28s %10.1f %-2s  budget %8.1f %-2s  %s' % (name, measured, unit, limit, unit, note or ('OVER' if measured > limit else 'ok')))
    for line in recorded(crawl, crawl_measure):
        print(line)
    if passes:
        print('pass marks (plan/site.md, rows %s): %s' % (', '.join(str(row) for row in sorted({row for row in c_BudgetRows.values() if row})),
                                                          ', '.join('%s %s' % (key, value) for key, value in sorted(passes.items()))))
    for name, given in (('build', measure), ('crawl', crawl), ('search', search)):
        if given is None:
            print('budgets: no %s measurement given; its budgets were not checked' % name)
    print('budgets: %d of %d over%s' % (len(failures), len(rows), ', %d not judged (over its budget on a busy machine)' % len(unjudged) if unjudged else ''))
    return 1 if failures or broken else 2 if unjudged else 0


if __name__ == '__main__':
    sys.exit(main())

// The CI workflows against plan/site.md's "CI" (scripts/workflows.mjs): the committed book.yml and links.yml pass, and
// each rule fails on a workflow that breaks it, planted by changing one line of the committed file.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bookProblems, c_Book, c_Links, expectedCacheKeys, linksProblems, logicalLines, workflowProblems } from '../../../scripts/workflows.mjs';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));
const c_BookText = readFileSync(path.join(c_Root, c_Book), 'utf8');
const c_LinksText = readFileSync(path.join(c_Root, c_Links), 'utf8');
const c_Playwright = JSON.parse(readFileSync(path.join(c_Root, 'package.json'), 'utf8')).dependencies.playwright;

/** The committed text with `from` replaced by `to`; `from` must occur, so a changed workflow fails here loudly. */
function planted(text, from, to) {
	assert.ok(text.includes(from), `the workflow no longer holds ${JSON.stringify(from)}`);
	return text.replace(from, to);
}

function bookWith(from, to) {
	return bookProblems(planted(c_BookText, from, to), { playwrightVersion: c_Playwright });
}

function assertOne(problems, pattern) {
	assert.equal(problems.filter((problem) => pattern.test(problem)).length, 1, problems.join('\n'));
}

test('the committed workflows follow plan/site.md\'s "CI"', () => {
	assert.deepEqual(workflowProblems(c_Root), []);
});

test('a run script\'s logical lines join continued lines and leave comments out', () => {
	assert.deepEqual(logicalLines('. .tools/env.sh\n# a comment\npython -I tools/cistatus.py step --title "x" -- \\\n  python -I tools/crawl.py\n\n'),
		['. .tools/env.sh', 'python -I tools/cistatus.py step --title "x" -- python -I tools/crawl.py']);
});

test('an action named by a tag, not by its commit, fails', () => {
	const problems = bookWith('actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1', 'actions/checkout@v7');
	assertOne(problems, /jobs\.lint, step 1 .* uses actions\/checkout@v7: pin the action by its full commit SHA/);
	const links = linksProblems(planted(c_LinksText, 'actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0', 'actions/setup-python@main'));
	assertOne(links, /uses actions\/setup-python@main: pin the action/);
});

test('a default permission other than "contents: read" fails, and so does a write outside report and release', () => {
	assertOne(bookWith('permissions:\n  contents: read\n', 'permissions:\n  contents: write\n'), /the default permission must be exactly "contents: read"/);
	assertOne(bookWith('permissions:\n  contents: read\n', 'permissions: write-all\n'), /the default permission must be exactly "contents: read"/);
	assertOne(bookWith('  lint:\n    runs-on: ubuntu-24.04\n', '  lint:\n    runs-on: ubuntu-24.04\n    permissions:\n      contents: write\n'),
		/jobs\.lint may not have "contents: write"; only report and release may write/);
	assertOne(bookWith('      actions: read\n', '      actions: write\n'), /jobs\.report may not have "actions: write"/);
	assertOne(linksProblems(planted(c_LinksText, 'permissions:\n  contents: read\n', 'permissions:\n  contents: read\n  issues: write\n')),
		/the default permission must be exactly "contents: read"/);
	assertOne(linksProblems(planted(c_LinksText, '    runs-on: ubuntu-24.04\n', '    runs-on: ubuntu-24.04\n    permissions:\n      contents: write\n')),
		/jobs\.links may not have "contents: write"; no job of this workflow writes/);
});

test('book.yml runs on every push, pull requests and by hand, and cancels superseded runs except for tags', () => {
	assertOne(bookWith('  push:\n', '  push:\n    branches: [main]\n'), /push is filtered by branches; it runs on every branch and tag/);
	assertOne(bookWith('  workflow_dispatch:\n', ''), /runs on pull_request, push; it runs on push, pull_request and workflow_dispatch/);
	assertOne(bookWith("cancel-in-progress: ${{ !startsWith(github.ref, 'refs/tags/') }}", 'cancel-in-progress: true'), /concurrency\.cancel-in-progress is true, not/);
	assertOne(bookWith('group: book-${{ github.ref }}', 'group: book'), /concurrency\.group is "book"/);
	// GitHub's short forms of `on`: one event's name, or a list of names.
	assertOne(bookWith('on:\n  push:\n  pull_request:\n  workflow_dispatch:\n', 'on: push\n'), /runs on push; it runs on push, pull_request and workflow_dispatch/);
	assert.deepEqual(bookWith('on:\n  push:\n  pull_request:\n  workflow_dispatch:\n', 'on: [push, pull_request, workflow_dispatch]\n'), []);
});

test('the jobs are plan/site.md\'s, with their needs; release runs on book-v* tags and report always but for pull requests', () => {
	assertOne(bookWith('    needs: lint\n', ''), /jobs\.build does not need lint/);
	assertOne(bookWith('    needs: [build, excerpts, serve-test]\n', '    needs: [build, serve-test]\n'), /jobs\.release does not need excerpts/);
	assertOne(bookWith("    if: startsWith(github.ref, 'refs/tags/book-v')\n", ''), /jobs\.release runs only on a book-v\* tag/);
	assertOne(bookWith("    if: always() && github.event_name != 'pull_request'\n", "    if: github.event_name != 'pull_request'\n"), /jobs\.report runs whatever the other jobs did/);
	assertOne(bookWith('    needs: [lint, excerpts, build, serve-test, release]\n', '    needs: [lint, excerpts, build, serve-test]\n'), /jobs\.report does not need release/);
	assertOne(bookWith('  release:\n    needs:', '  publish:\n    needs:'), /has no job release/);
	assertOne(bookWith('  release:\n    needs:', '  publish:\n    needs:'), /the job publish is not one of plan\/site\.md's/);
});

test('a repository variable, a secret or DOCS_SITE in book.yml fails; a comment that names DOCS_SITE does not', () => {
	assert.ok(c_BookText.includes('# The base and the origin are site.json\'s (rulings 6, R24): no DOCS_BASE or DOCS_SITE here'));
	assertOne(bookWith('  DO_NOT_TRACK: "1"\n', '  DO_NOT_TRACK: "1"\n  DOCS_SITE: https://example.com\n'), /env\.DOCS_SITE|names DOCS_SITE/);
	assertOne(bookWith('  DO_NOT_TRACK: "1"\n', '  DO_NOT_TRACK: "1"\n  ORIGIN: ${{ vars.ORIGIN }}\n'), /reads a repository variable/);
	assertOne(bookWith('GH_TOKEN: ${{ github.token }}', 'GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}'), /reads the secret RELEASE_TOKEN/);
	assert.deepEqual(bookWith('GH_TOKEN: ${{ github.token }}', 'GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}'), []);
});

test('a step after the bootstrap that does not source .tools/env.sh fails', () => {
	const problems = bookWith('        run: |\n          . .tools/env.sh\n          python -I tools/cistatus.py step --title "The outline (check 1)"',
		'        run: |\n          python -I tools/cistatus.py step --title "The outline (check 1)"');
	assertOne(problems, /jobs\.lint, step \d+ \(The outline \(check 1\)\) does not source \.tools\/env\.sh/);
	// The step right after the bootstrap, and the bootstrap's own step when it runs more than the bootstrap.
	assertOne(bookWith('        run: |\n          . .tools/env.sh\n          npm ci --no-audit\n', '        run: |\n          npm ci --no-audit\n'),
		/jobs\.lint, step \d+ \(Packages and Chromium .*\) does not source \.tools\/env\.sh/);
	const toolchain = '      - name: Toolchain, packages and Chromium (the drawings\' check measures in it)\n        run: |\n          python -I tools/bootstrap.py\n';
	assertOne(bookWith(`${toolchain}          . .tools/env.sh\n`, toolchain), /jobs\.build, step \d+ \(Toolchain, packages and Chromium .*\) does not source \.tools\/env\.sh/);
	const links = linksProblems(planted(c_LinksText, '          . .tools/env.sh\n          size=$(gh api', '          size=$(gh api'));
	assertOne(links, /The repository's size \(at most 1 GB\)\) does not source \.tools\/env\.sh/);
});

test('a check that does not run through tools/cistatus.py step fails, and so does one continued over two lines', () => {
	assertOne(bookWith('python -I tools/cistatus.py step --title "The outline (check 1)" -- python -I plan/check_outline.py', 'python -I plan/check_outline.py'),
		/runs "python -I plan\/check_outline\.py" without tools\/cistatus\.py step/);
	assertOne(bookWith('python -I tools/cistatus.py step --title "Gate (a) at /" -- python -I tools/crawl.py', 'python -I tools/crawl.py'),
		/runs "python -I tools\/crawl\.py --dist dist-root .*" without tools\/cistatus\.py step/);
	assertOne(bookWith('python -I tools/cistatus.py step --title "Spelling (check 8)" -- typos', 'typos'), /runs "typos" without/);
	assertOne(bookWith('python -I tools/cistatus.py step --title "Unit tests of the build (npm test)" -- timeout -k 20 600 npm test || status=1', 'npm test'), /runs "npm test" without/);
});

test('a cache whose key is not plan/site.md\'s fails, and Playwright\'s key names package.json\'s version', () => {
	assert.equal(expectedCacheKeys('1.2.3')['.tools/ms-playwright'], 'playwright-1.2.3-${{ runner.os }}');
	// The jobs that run Chromium, lint (the browser checks' unit tests), build (the drawings' check) and serve-test, each
	// restore the browsers.
	const stale = bookProblems(c_BookText, { playwrightVersion: '1.66.0' });
	assert.equal(stale.filter((problem) => /has the key playwright-1\.65\.0-\$\{\{ runner\.os \}\}, not playwright-1\.66\.0/.test(problem)).length, 3, stale.join('\n'));
	assertOne(bookWith("key: images-${{ hashFiles('src/assets/figures/**', 'src/lib/images.mjs') }}", "key: images-${{ hashFiles('src/assets/figures/**') }}"),
		/has the key images-\$\{\{ hashFiles\('src\/assets\/figures\/\*\*'\) \}\}, not images-/);
	assertOne(bookWith('          path: .cache/images\n', '          path: .cache/pictures\n'), /caches \.cache\/pictures, which is not a cache of plan\/site\.md's table/);
	assertOne(bookWith('            .tools\n            !.tools/ms-playwright\n', '            .tools\n'), /caches the toolchain with Playwright's browsers/);
});

test('a job that restores Playwright\'s browsers without installing their system libraries fails', () => {
	assertOne(bookWith('          npm ci --no-audit\n          npx playwright install-deps chromium\n          npx playwright install --only-shell chromium\n      - name: Front matter',
		'          npm ci --no-audit\n          npx playwright install --only-shell chromium\n      - name: Front matter'), /jobs\.lint restores Playwright's browsers but does not install their system libraries/);
});

test('a checkout deeper than one commit fails', () => {
	assertOne(bookWith('        with:\n          persist-credentials: false\n          sparse-checkout-cone-mode: false\n',
		'        with:\n          fetch-depth: 0\n          persist-credentials: false\n          sparse-checkout-cone-mode: false\n'), /jobs\.lint, step 1 .* checks out 0 commits deep/);
});

test('links.yml runs on Mondays at 06:00 UTC and by hand, reports lychee\'s findings and fails above 1 GB', () => {
	assert.deepEqual(linksProblems(c_LinksText), []);
	assertOne(linksProblems(planted(c_LinksText, '"0 6 * * 1"', '"0 6 * * *"')), /it runs on Mondays at 06:00 UTC/);
	assertOne(linksProblems(planted(c_LinksText, '  workflow_dispatch:\n', '  workflow_dispatch:\n  push:\n')), /it runs on Mondays at 06:00 UTC/);
	assertOne(linksProblems(planted(c_LinksText, '--exclude "^${repository}" ', '')), /lychee does not leave out the engine's repository/);
	assertOne(linksProblems(planted(c_LinksText, ' && [ "$status" -ne 2 ]', '')), /lychee's findings are only reported/);
	assertOne(linksProblems(planted(c_LinksText, '} >> "$GITHUB_STEP_SUMMARY"', '}')), /not reported in the job summary/);
	assertOne(linksProblems(planted(c_LinksText, '-gt 1048576', '-gt 2097152')), /does not fail the job above 1 GB/);
	assertOne(linksProblems(planted(c_LinksText, '--jq .size', '--jq .stargazers_count')), /no step reads the repository's size/);
});

test('a file that is not YAML fails with its name', () => {
	assert.match(bookProblems('jobs: [', { playwrightVersion: c_Playwright })[0], /^\.github\/workflows\/book\.yml: not YAML/);
	assert.match(linksProblems('')[0], /links\.yml: holds no workflow/);
});

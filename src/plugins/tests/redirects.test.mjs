// Moved pages (plan/site.md, "Moved pages"): src/redirects.json's shape and checks, the test entries a test build adds
// (DOCS_EXTRA_REDIRECTS), and the fallback pages the build writes, at the bases /, /strata-engine-docs and /x/y.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bookProblems, bookRedirects, writeFallbackPages } from '../../integrations/book.mjs';
import { c_MovedMeta, fallbackFile, fallbackPage, loadRedirects, redirectProblems } from '../../lib/redirects.mjs';
import { normalizeBase, readSettings } from '../../lib/settings.mjs';
import { createBookContext } from '../index.mjs';
import { c_BottomStrip, c_ReleaseSite, frontmatter, makeBook } from './helpers.mjs';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));

function withFile(content, run) {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'redirects-'));
	const file = path.join(folder, 'redirects.json');
	try {
		if (content !== undefined) writeFileSync(file, typeof content === 'string' ? content : JSON.stringify(content));
		return run(file);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
}

test('the repository\'s src/redirects.json and its test entry have the shape the build reads', () => {
	const own = loadRedirects(path.join(c_Root, 'src', 'redirects.json'));
	assert.deepEqual(own.problems, []);
	const fixture = loadRedirects(path.join(c_Root, 'tools', 'tests', 'release-redirects.json'));
	assert.deepEqual(fixture.problems, []);
	assert.equal(fixture.entries.length, 1);
});

test('a redirects file of another shape is refused with its name', () => {
	withFile(undefined, (file) => assert.deepEqual(loadRedirects(file), { entries: [], problems: [] }));
	withFile('{', (file) => assert.match(loadRedirects(file, 'r.json').problems.join(), /r\.json: not valid JSON/));
	withFile({ moved: [] }, (file) => assert.match(loadRedirects(file, 'r.json').problems.join(), /r\.json holds \{ "redirects"/));
	withFile({ redirects: [{ from: 'a/b' }, { from: 'a/c', to: 'core/time', note: 'x' }, { from: 'a/d', to: 'core/time' }] }, (file) => {
		const { entries, problems } = loadRedirects(file, 'r.json');
		assert.deepEqual(problems, ['r.json: entry 1 is not { "from": "<old id>", "to": "<new id>" }', 'r.json: entry 2 is not { "from": "<old id>", "to": "<new id>" }']);
		assert.deepEqual(entries.map((entry) => entry.from), ['a/d']);
	});
});

test('an entry moves an old id that is no page to a page of the book, once and without chains', () => {
	const pages = new Map([['core/time', {}], ['core/index', {}], ['world/ecs', {}]]);
	const entry = (from, to, index = 1) => ({ from, to, label: `r.json, entry ${index}` });
	assert.deepEqual(redirectProblems([entry('core/old-time', 'core/time')], pages), []);
	const problems = redirectProblems([
		entry('core/time', 'world/ecs', 1),
		entry('core/gone', 'core/missing', 2),
		entry('core/Old', 'core/time', 3),
		entry('print/core', 'core/time', 4),
		entry('v0/core', 'core/time', 5),
		entry('core/a', 'core/b', 6),
		entry('core/b', 'core/time', 7),
		entry('core/b', 'world/ecs', 8),
		entry('index', 'core/time', 9),
	], pages).join('\n');
	assert.match(problems, /entry 1 \("core\/time" to "world\/ecs"\): "core\/time" is a page of the book, so it has not moved/);
	assert.match(problems, /entry 2 \("core\/gone" to "core\/missing"\): "core\/missing" is not a page of the book/);
	assert.match(problems, /entry 3 .*the old id is not a page id/);
	assert.match(problems, /entry 4 .*"print" is reserved for the site's own files/);
	assert.match(problems, /entry 5 .*reserved for archived versions/);
	assert.match(problems, /entry 6 \("core\/a" to "core\/b"\): "core\/b" has moved itself: point the entry at the page it moved to/);
	assert.match(problems, /entry 8 .*"core\/b" is moved twice \(r\.json, entry 7\)/);
	assert.match(problems, /entry 9 .*the landing page and the 404 page never move/);
});

test('a fallback page sends the reader on under the base, names the new page as canonical and is not indexed', () => {
	for (const [raw, prefix] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
		const base = normalizeBase(raw);
		const html = fallbackPage({ base, site: 'https://example.com', entry: { from: 'core/old', to: 'core/index' }, title: 'Engine <architecture>', copyright: { holder: 'A & B', year: 2026 } });
		assert.match(html, new RegExp(`<meta http-equiv="refresh" content="0; url=${prefix}/core/">`));
		assert.match(html, new RegExp(`<link rel="canonical" href="https://example.com${prefix}/core/">`));
		assert.match(html, new RegExp(`<meta name="${c_MovedMeta}" content="${prefix}/core/">`));
		assert.match(html, /<meta name="robots" content="noindex">/);
		assert.match(html, new RegExp(`<a href="${prefix}/core/">Engine &lt;architecture&gt;</a>`));
		// The footer's line and its two links, as on every page (rulings 6, R20).
		assert.match(html, new RegExp(`<footer><p>Copyright © 2026 A &amp; B\\. All rights reserved\\. <a href="${prefix}/license.txt">License</a> <a href="${prefix}/third-party-notices.txt">Third-party notices</a></p></footer>`));
		assert.doesNotMatch(html, /<script/);
		if (prefix !== '/strata-engine-docs') assert.doesNotMatch(html, /strata-engine-docs/);
	}
	assert.equal(fallbackFile({ from: 'core/old', to: 'core/time' }), 'core/old/index.html');
	assert.equal(fallbackFile({ from: 'old/index', to: 'core/time' }), 'old/index.html');
});

test('the build checks the moved pages, adds a test build\'s entries and writes their fallback pages', async () => {
	const page = `${frontmatter()}\nText.\n${c_BottomStrip}`;
	const book = makeBook({
		pages: { 'core/time': page },
		files: {
			'src/redirects.json': JSON.stringify({ redirects: [{ from: 'core/old-time', to: 'core/time' }] }),
			'extra.json': JSON.stringify({ redirects: [{ from: 'core/test-entry', to: 'core/time' }] }),
			'bad.json': JSON.stringify({ redirects: [{ from: 'core/time', to: 'core/gone' }] }),
		},
	});
	try {
		for (const [raw, prefix] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
			const settings = readSettings({ root: book.root, env: { DOCS_BASE: raw, DOCS_SITE: 'https://example.com', DOCS_EXTRA_REDIRECTS: 'extra.json' } });
			const context = createBookContext(settings);
			assert.deepEqual((await bookProblems(context)).filter((line) => /redirect|moved|extra/.test(line)), []);
			assert.deepEqual(bookRedirects(settings).entries.map((entry) => entry.from), ['core/old-time', 'core/test-entry']);
			const out = path.join(book.root, `dist${prefix.replace(/\//g, '-')}`);
			assert.equal(writeFallbackPages(settings, (await context.index()).pages, out), 2);
			const written = readFileSync(path.join(out, 'core', 'test-entry', 'index.html'), 'utf8');
			assert.match(written, new RegExp(`url=${prefix}/core/time/"`));
			assert.ok(existsSync(path.join(out, 'core', 'old-time', 'index.html')));
			// A file already there is never replaced.
			assert.throws(() => writeFallbackPages(settings, new Map([['core/time', { title: 'Time' }]]), out), /already holds core\/old-time\/index\.html/);
		}
		const bad = readSettings({ root: book.root, env: { DOCS_SITE: 'https://example.com', DOCS_EXTRA_REDIRECTS: 'bad.json' } });
		assert.match((await bookProblems(createBookContext(bad))).join('\n'), /bad\.json, entry 1 \("core\/time" to "core\/gone"\): "core\/time" is a page of the book[\s\S]*"core\/gone" is not a page of the book/);
		const missing = readSettings({ root: book.root, env: { DOCS_SITE: 'https://example.com', DOCS_EXTRA_REDIRECTS: 'none.json' } });
		assert.match(bookRedirects(missing).problems.join(), /DOCS_EXTRA_REDIRECTS names .*none\.json, which does not exist/);
		assert.throws(() => readSettings({ root: book.root, env: { DOCS_SITE: c_ReleaseSite, DOCS_RELEASE: '1', DOCS_EXTRA_REDIRECTS: 'extra.json' } }), /a release build leaves it unset/);
	} finally {
		book.remove();
	}
});

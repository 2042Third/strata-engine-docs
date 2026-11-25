// Gate (b) (scripts/runtime.mjs): what the run visits, read from the build; how it judges the requests, the console,
// the policy's events and a moved page's answer; and the run itself in Chromium against a server of fixture pages, once
// clean at three bases and once with every fault it must catch planted.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { chooseTrack, consoleProblems, c_Kinds, isConditional, pageKind, plan, redirectProblem, requestProblems, runRuntime, searchQueries, sitePages, trackLinks } from '../../../scripts/runtime.mjs';

const c_Bases = ['/', '/docs', '/x/y'];

function prefixOf(base) {
	return base === '/' ? '' : base;
}

/** A page of the fixture site. */
function page(prefix, { kind = null, body = '', head = '' } = {}) {
	return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>t</title><link rel="stylesheet" href="${prefix}/_astro/site.css">${head}</head>`
		+ `<body>${kind ? `<span hidden data-pagefind-meta="kind">${kind}</span>` : ''}${body}</body></html>`;
}

/** The pagination of a page: its default next and one template per track. */
function pagination(next, tracks) {
	const link = (href) => (href ? `<a href="${href}" rel="next"><span>Next</span></a>` : '');
	return `<footer><div class="book-pagination"><div class="pagination-links" dir="ltr">${link(next)}</div>`
		+ Object.entries(tracks).map(([name, href]) => `<template data-book-track="${name}">${link(href)}</template>`).join('') + '</div></footer>';
}

/** A built site with a page of each kind, a glossary, a print view, the track chooser and a moved page. */
function fixtureSite(prefix, extra = {}) {
	const files = {
		'index.html': page(prefix, { body: '<p>The book.</p>' }),
		'404.html': page(prefix, { head: '<meta name="robots" content="noindex">', body: '<p>Not here.</p>' }),
		'_astro/site.css': 'body { margin: 0 }',
		'start/how-to-read/index.html': page(prefix, { kind: 'How-to', body: '<book-track-chooser><button class="book-track__choose" data-track="game">Game</button><button class="book-track__choose" data-track="engine">Engine</button></book-track-chooser>'
			+ pagination(`${prefix}/basics/tools/`, { game: `${prefix}/basics/tools/`, engine: `${prefix}/core/time/` }) }),
		'basics/tools/index.html': page(prefix, { kind: 'Primer' }),
		'core/time/index.html': page(prefix, { kind: 'Concept' }),
		'world/steps/index.html': page(prefix, { kind: 'Internals' }),
		'make/first/index.html': page(prefix, { kind: 'Tutorial' }),
		'reference/glossary/index.html': page(prefix, { kind: 'Reference', body: '<dl class="book-glossary"><dt id="frame">frame</dt><dd>A picture.</dd></dl>' }),
		'print/core/index.html': page(prefix, { body: '<p>All of the part.</p>' }),
		'core/old/index.html': page(prefix, { head: `<meta name="strata-book-moved" content="${prefix}/core/time/">` }),
		'_figures/crop.svg': '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect width="200" height="100" fill="#ccc"/></svg>',
		...extra,
	};
	return files;
}

function writeSite(folder, files) {
	for (const [relative, text] of Object.entries(files)) {
		const file = path.join(folder, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, text);
	}
}

const c_Types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.json': 'application/json' };

/**
 * Serves `folder` under `prefix` as the deployments do, with a policy on every page and the given 301s. With
 * `validators`, every file is no-cache with an ETag, and a request that names it gets 304, as nginx answers; the server
 * counts those in `notModified`. Paths in `broken304` answer 304 to every request, asked or not.
 */
function serve(folder, prefix, { policy, redirects = {}, validators = false, broken304 = [] }) {
	const server = createServer((request, response) => {
		const pathname = decodeURIComponent(new URL(request.url, 'http://fixture').pathname);
		if (redirects[pathname]) {
			response.writeHead(301, { Location: redirects[pathname] });
			return response.end();
		}
		if (broken304.includes(pathname)) {
			response.writeHead(304);
			return response.end();
		}
		const send = (file, status) => {
			const headers = { 'Content-Type': c_Types[path.extname(file)] ?? 'application/octet-stream' };
			if (file.endsWith('.html') && policy) headers['Content-Security-Policy'] = policy;
			if (validators && status === 200) {
				const { size, mtimeMs } = statSync(file);
				const tag = `"${size}-${Math.trunc(mtimeMs)}"`;
				Object.assign(headers, { 'Cache-Control': 'no-cache', ETag: tag });
				if (request.headers['if-none-match'] === tag) {
					server.notModified += 1;
					response.writeHead(304, { 'Cache-Control': 'no-cache', ETag: tag });
					return response.end();
				}
			}
			response.writeHead(status, headers);
			response.end(readFileSync(file));
		};
		if (!pathname.startsWith(`${prefix}/`)) {
			response.writeHead(404, { 'Content-Type': 'text/plain' });
			return response.end('not here');
		}
		let file = path.join(folder, ...pathname.slice(prefix.length + 1).split('/').filter(Boolean));
		try {
			if (statSync(file).isDirectory()) file = path.join(file, 'index.html');
			statSync(file);
			return send(file, 200);
		} catch {
			return send(path.join(folder, '404.html'), 404);
		}
	});
	server.notModified = 0;
	return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

test('the run visits the landing page, a page of each kind, the glossary, a print view and reads the moved pages', () => {
	const folder = mkdtempSync(path.join(tmpdir(), 'runtime-plan-'));
	try {
		writeSite(folder, fixtureSite('/docs'));
		const planned = plan(folder);
		assert.deepEqual(planned.problems, []);
		assert.deepEqual(planned.visits.map((visit) => visit.route), ['', 'basics/tools/', 'core/time/', 'world/steps/', 'make/first/', 'start/how-to-read/', 'reference/glossary/', 'reference/glossary/', 'print/core/']);
		assert.deepEqual(planned.moved, [{ from: 'core/old/', to: '/docs/core/time/' }]);
		assert.equal(planned.chooser, 'start/how-to-read/');
		// The engine track's next differs from the page's own: that track shows the choice at work.
		assert.equal(planned.track, 'engine');
		assert.equal(pageKind(page('', { kind: 'Concept' })), 'Concept');
		assert.equal(sitePages(folder).filter((entry) => entry.route.startsWith('print/')).length, 1);
		assert.deepEqual(trackLinks(pagination('/a/', { game: null, engine: '/b/' })), { next: '/a/', tracks: { game: null, engine: '/b/' } });
		rmSync(path.join(folder, 'make'), { recursive: true });
		rmSync(path.join(folder, 'print'), { recursive: true });
		const short = plan(folder);
		assert.deepEqual(short.problems, ['the build has no page of the kind Tutorial', 'the build has no print view']);
		assert.equal(c_Kinds.length, 6);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('a track whose next only ends earlier is chosen when no track leads elsewhere', () => {
	const chooser = { route: 'a/', html: page('/docs', { body: '<book-track-chooser><button class="book-track__choose" data-track="game">G</button></book-track-chooser>' + pagination('/docs/b/', { game: null }) }) };
	assert.equal(chooseTrack(chooser, new Map()), 'game');
});

test('a request that leaves the prefix or the origin, or is answered other than 2xx, fails at three bases', () => {
	for (const base of c_Bases) {
		const prefix = prefixOf(base);
		const site = `http://127.0.0.1:1${prefix}/`;
		const missing = `${site}a/b/c/`;
		const at = (relative) => `http://127.0.0.1:1${prefix}/${relative}`;
		const clean = [
			{ url: at(''), status: 200, page: 'home', document: true },
			{ url: at('_astro/site.css'), status: 200, page: 'home' },
			{ url: missing, status: 404, page: 'missing', document: true },
			// The browser revalidated a no-cache file it held: the 304 is that file's correct answer.
			{ url: at('pagefind/pagefind.js'), status: 304, conditional: true, page: 'search' },
			{ url: 'data:image/png;base64,AA', status: 200, page: 'home' },
			{ url: at('_astro/lazy.js'), status: null, error: 'net::ERR_ABORTED', page: 'home' },
		];
		assert.deepEqual(requestProblems(clean, { site, missing }), [], base);
		const planted = requestProblems([
			// A 304 to a request that asked for no revalidation, or whose headers could not be read.
			{ url: at('_astro/site.css'), status: 304, page: 'missing' },
			{ url: at('_astro/other.css'), status: 304, conditional: false, page: 'missing' },
			{ url: 'http://127.0.0.1:1/elsewhere/x.svg', status: 200, page: 'p' },
			{ url: `http://localhost:1${prefix}/_figures/a.svg`, status: 200, page: 'p' },
			{ url: at('_figures/none.svg'), status: 404, page: 'p' },
			{ url: missing, status: 200, page: 'missing', document: true },
			{ url: at('_astro/gone.css'), status: 404, page: 'missing' },
			{ url: at('x.js'), status: null, error: 'net::ERR_CONNECTION_REFUSED', page: 'p' },
		], { site, missing });
		if (base === '/') {
			// At the root of a host every path is under the prefix.
			assert.equal(planted.filter((problem) => problem.includes('leaves the prefix')).length, 0);
		} else {
			assert.ok(planted.some((problem) => problem === `p: a request leaves the prefix ${prefix}/: http://127.0.0.1:1/elsewhere/x.svg`), planted.join('\n'));
		}
		assert.ok(planted.includes(`p: a request leaves the origin: http://localhost:1${prefix}/_figures/a.svg`), planted.join('\n'));
		assert.ok(planted.includes(`p: ${at('_figures/none.svg')} answers 404`));
		assert.ok(planted.includes(`${missing} answers 200, not 404 with the book's 404 page`));
		assert.ok(planted.includes(`missing: ${at('_astro/gone.css')} answers 404`));
		assert.ok(planted.includes(`p: ${at('x.js')} got no answer (net::ERR_CONNECTION_REFUSED)`));
		assert.ok(planted.includes(`missing: ${at('_astro/site.css')} answers 304`), planted.join('\n'));
		assert.ok(planted.includes(`missing: ${at('_astro/other.css')} answers 304`), planted.join('\n'));
	}
});

test('a request is conditional when it carries If-None-Match or If-Modified-Since', () => {
	assert.equal(isConditional({ 'if-none-match': '"v1"' }), true);
	assert.equal(isConditional({ 'if-modified-since': 'Tue, 10 Nov 2026 10:00:00 GMT' }), true);
	assert.equal(isConditional({ 'cache-control': 'max-age=0', accept: '*/*' }), false);
	assert.equal(isConditional({}), false);
});

test('a console error, a script that fails and every policy violation fail; the missing page\'s own 404 does not', () => {
	const missing = 'http://127.0.0.1:1/docs/a/b/c/';
	const problems = consoleProblems([
		{ type: 'error', text: 'Failed to load resource: the server responded with a status of 404 (Not Found)', url: missing, page: 'missing' },
		{ type: 'error', text: 'Failed to load resource: the server responded with a status of 404 (Not Found)', url: 'http://127.0.0.1:1/docs/x.css', page: 'p' },
		{ type: 'error', text: 'planted', url: 'http://127.0.0.1:1/docs/_astro/err.js', page: 'p' },
		{ type: 'warning', text: 'a warning', url: '', page: 'p' },
		{ type: 'pageerror', text: 'x is not defined', url: '', page: 'p' },
	], [{ page: 'p', directive: 'script-src-elem', blocked: 'inline' }], { missing });
	assert.deepEqual(problems, [
		'p: a console error: Failed to load resource: the server responded with a status of 404 (Not Found)',
		'p: a console error: planted',
		'p: a script failed: x is not defined',
		'p: the Content Security Policy blocked inline (script-src-elem)',
	]);
});

test('a moved page answers 301 with its new page\'s path, or fails', () => {
	const to = '/docs/core/time/';
	assert.equal(redirectProblem({ status: 301, location: to }, to, 'old'), null);
	assert.equal(redirectProblem({ status: 200 }, to, 'old'), 'old answers 200, not 301 to /docs/core/time/');
	assert.equal(redirectProblem({ status: 302, location: to }, to, 'old'), 'old answers 302, not 301 to /docs/core/time/');
	assert.match(redirectProblem({ status: 301, location: `https://example.com${to}` }, to, 'old'), /not to \/docs\/core\/time\/ \(a path, no scheme or host\)/);
});

test('the two searches are the first written glossary term and engine name', () => {
	const data = { queries: [{ kind: 'term', query: 'unwritten', page: 'a/b' }, { kind: 'term', query: 'fixed step', page: 'core/time' }, { kind: 'name', query: 'ST_SCRIPT_CLASS', page: 'make/first-script' }] };
	assert.deepEqual(searchQueries(data, (route) => route !== 'a/b'), { term: 'fixed step', name: 'ST_SCRIPT_CLASS' });
	assert.deepEqual(searchQueries(data, () => false), { term: null, name: null });
});

const c_Policy = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'";

test('the run in Chromium passes a clean site at three bases', async () => {
	for (const base of c_Bases) {
		const prefix = prefixOf(base);
		const folder = mkdtempSync(path.join(tmpdir(), 'runtime-clean-'));
		writeSite(folder, fixtureSite(prefix));
		const server = await serve(folder, prefix, { policy: c_Policy, redirects: { [`${prefix}/core/old/`]: `${prefix}/core/time/` } });
		try {
			const site = `http://127.0.0.1:${server.address().port}${prefix}/`;
			const result = await runRuntime({ site, distDir: folder, steps: ['pages', 'redirects'] });
			assert.deepEqual(result.problems, [], `${base}:\n${result.problems.join('\n')}`);
			assert.equal(result.counts.moved, 1);
		} finally {
			server.close();
			rmSync(folder, { recursive: true, force: true });
		}
	}
});

test('the run in Chromium passes the browser\'s own revalidations and fails a 304 it did not ask for', async () => {
	const prefix = '/docs';
	const folder = mkdtempSync(path.join(tmpdir(), 'runtime-304-'));
	writeSite(folder, fixtureSite(prefix));
	const redirects = { [`${prefix}/core/old/`]: `${prefix}/core/time/` };
	try {
		// Every page loads the same no-cache style sheet, so each page after the first revalidates it.
		const honest = await serve(folder, prefix, { policy: c_Policy, redirects, validators: true });
		try {
			const result = await runRuntime({ site: `http://127.0.0.1:${honest.address().port}${prefix}/`, distDir: folder, steps: ['pages', 'redirects'] });
			assert.ok(honest.notModified > 0, 'the browser revalidated nothing, so the test shows nothing');
			assert.deepEqual(result.problems, [], result.problems.join('\n'));
		} finally {
			honest.close();
		}
		const broken = await serve(folder, prefix, { policy: c_Policy, redirects, broken304: [`${prefix}/_astro/site.css`] });
		try {
			const result = await runRuntime({ site: `http://127.0.0.1:${broken.address().port}${prefix}/`, distDir: folder, steps: ['pages', 'redirects'] });
			assert.match(result.problems.join('\n'), /\/docs\/_astro\/site\.css answers 304/, result.problems.join('\n'));
		} finally {
			broken.close();
		}
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('the run in Chromium catches every planted fault', async () => {
	const prefix = '/docs';
	const folder = mkdtempSync(path.join(tmpdir(), 'runtime-faults-'));
	const server = await serve(folder, prefix, { policy: c_Policy });
	const port = server.address().port;
	// A label that stands in its box but runs out of it, and a crop shown at 1.5 times its own width.
	const diagram = '<figure class="book-diagram"><div class="book-diagram__svg--light"><svg xmlns="http://www.w3.org/2000/svg" width="300" height="60" role="img" aria-label="A box.">'
		+ '<g><rect x="0" y="0" width="120" height="40" fill="#eeeeee"></rect><text x="4" y="26" font-size="16" fill="#000000">a label that runs out</text></g></svg></div></figure>';
	const crop = `<figure class="book-figure book-figure--crop"><div class="book-crop" style="--book-crop-scale: 4"><img class="book-crop__img" src="${prefix}/_figures/crop.svg" alt="A crop." style="width: 300px; image-rendering: pixelated"></div></figure>`;
	writeSite(folder, fixtureSite(prefix, {
		'core/time/index.html': page(prefix, { kind: 'Concept', body: `${diagram}${crop}<img src="/elsewhere/x.svg" alt="x"><img src="http://localhost:${port}${prefix}/_figures/crop.svg" alt="y">`
			+ `<img src="${prefix}/_figures/none.svg" alt="z"><script>document.title = 'inline'</script><script src="${prefix}/_astro/err.js"></script>` }),
		'_astro/err.js': 'console.error("planted");',
		'404.html': page(prefix, { head: `<link rel="stylesheet" href="${prefix}/_astro/gone.css">`, body: '<p>Not here.</p>' }),
	}));
	try {
		const site = `http://127.0.0.1:${port}${prefix}/`;
		const result = await runRuntime({ site, distDir: folder, steps: ['pages', 'redirects'] });
		const text = result.problems.join('\n');
		const expect = (pattern) => assert.match(text, pattern, text);
		expect(/a request leaves the prefix \/docs\/: http:\/\/127\.0\.0\.1:\d+\/elsewhere\/x\.svg/);
		expect(/a request leaves the origin: http:\/\/localhost:\d+\/docs\/_figures\/crop\.svg/);
		expect(/\/docs\/_figures\/none\.svg answers 404/);
		expect(/\/docs\/_astro\/gone\.css answers 404/);
		expect(/the Content Security Policy blocked inline \(script-src-elem\)/);
		expect(/a console error: planted/);
		expect(/crop\.svg: it is shown 300 px wide, 1\.500 times its own 200 px: not a whole factor/);
		expect(/the diagram label "a label that runs out" leaves its box/);
		expect(/core\/old\/ answers 200, not 301 to \/docs\/core\/time\//);
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
});

test('the run in Chromium fails where a search finds nothing, the theme does not change or "next" leaves the track', async () => {
	const prefix = '/docs';
	const folder = mkdtempSync(path.join(tmpdir(), 'runtime-steps-'));
	const server = await serve(folder, prefix, { policy: c_Policy });
	const client = path.resolve(import.meta.dirname, '..', '..', 'components', 'client');
	// Starlight's controls without Starlight's scripts: a search box that never answers, a theme select that changes
	// nothing. The track chooser and the pagination run the book's own script; core/time, where "next" on the engine
	// track leads, carries no template of that track.
	const controls = '<button data-open-modal>Search</button><input class="pagefind-ui__search-input"><starlight-theme-select><select><option value="dark">Dark</option><option value="light">Light</option></select></starlight-theme-select>';
	const script = `<script type="module" src="${prefix}/_astro/book.js"></script>`;
	writeSite(folder, fixtureSite(prefix, {
		'index.html': page(prefix, { body: controls }),
		'start/how-to-read/index.html': page(prefix, { kind: 'How-to', body: '<book-track-chooser><button class="book-track__choose" data-track="engine" hidden>Engine</button></book-track-chooser>'
			+ pagination(`${prefix}/basics/tools/`, { engine: `${prefix}/core/time/` }) + script }),
		'core/time/index.html': page(prefix, { kind: 'Concept', body: pagination(`${prefix}/world/steps/`, {}) + script }),
		'_astro/book.js': readFileSync(path.join(client, 'book.js'), 'utf8'),
		'_astro/print.js': readFileSync(path.join(client, 'print.js'), 'utf8'),
		'queries.json': JSON.stringify({ queries: [{ kind: 'term', query: 'frame', page: 'reference/glossary' }, { kind: 'name', query: 'ST_SCRIPT_CLASS', page: 'nowhere' }] }),
	}));
	try {
		const site = `http://127.0.0.1:${server.address().port}${prefix}/`;
		const result = await runRuntime({ site, distDir: folder, queriesFile: path.join(folder, 'queries.json'), steps: ['search', 'theme', 'track'], searchWait: 1000 });
		assert.deepEqual(result.problems.filter((problem) => !problem.includes('console error')), [
			'search "frame": no result',
			'no engine name of queries.json has its page in the build: nothing to search for',
			'the theme switch: choosing dark shows undefined',
			'the theme switch: choosing light shows undefined',
			`track engine, ${site}core/time/: the page has no "next" of the track`,
		]);
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
});

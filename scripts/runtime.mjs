// Gate (b), the runtime check (plan/site.md, "The three gates"): Playwright's Chromium against a real server of the
// built site, all of them nginx. It loads the landing page, one page of each kind, the glossary, a print view and the
// missing path <base>/a/b/c/; runs two searches (a glossary term and an engine name) and follows the first result;
// switches the theme; chooses a track and follows "next"; and records every request. It fails when a request leaves
// the prefix or the origin, when a response is not 2xx (the missing path answers 404, and its assets 2xx; a 304 passes
// only as the answer to the browser's own revalidation of a file it holds), when the browser reports a Content Security
// Policy violation or a console error, when a crop is shown at a fractional factor (at 375, 768 and 1280 pixels), when
// a diagram's label leaves its box, or when a moved page's old address (the redirect test entry, src/redirects.json)
// does not answer 301 to its target.
//
//     node scripts/runtime.mjs --url http://127.0.0.1:8080/strata-engine-docs/ [--dist <the served build>]
//         [--root <book folder>] [--json <file>]
//
// --dist is the built site the server serves (default <root>/dist): the pages of each kind, the print views and the
// moved pages are read from it. tools/servertest.py nginx --runtime runs this through each of its servers. Without
// --url it serves the build with tools/crawl.py, which applies no policy and no moved-page rules: that run is a smoke
// test, not the gate.

import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_Kinds = ['Primer', 'Concept', 'Internals', 'Tutorial', 'How-to', 'Reference'];
export const c_MissingPath = 'a/b/c/';
export const c_CropViewports = [375, 768, 1280];
const c_Skipped = new Set(['_astro', '_figures', 'pagefind', 'downloads']);
// How far "next" is followed on the chosen track.
const c_TrackSteps = 3;

/** Every page of a built site: `{ route, html }`, route below the base ("core/time/", "" for the landing page). */
export function sitePages(distDir, relative = '') {
	const pages = [];
	let entries;
	try {
		entries = readdirSync(path.join(distDir, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
		const child = relative ? `${relative}/${entry.name}` : entry.name;
		if (entry.isDirectory()) {
			if (!c_Skipped.has(child)) pages.push(...sitePages(distDir, child));
		} else if (entry.name === 'index.html') {
			pages.push({ route: relative ? `${relative}/` : '', html: readFileSync(path.join(distDir, child), 'utf8') });
		}
	}
	return pages;
}

/** The kind a page names for search (the hidden data-pagefind-meta="kind" span), or null. */
export function pageKind(html) {
	return /<span hidden data-pagefind-meta="kind">([^<]+)</.exec(html)?.[1].trim() ?? null;
}

/** The old address of a moved page and the path its fallback page names (<meta name="strata-book-moved">), or null. */
export function movedTarget(html) {
	return /<meta name="strata-book-moved" content="([^"]+)"/.exec(html)?.[1] ?? null;
}

/** The links of a page's pagination: its default "next" and, per track, the "next" of its template. */
export function trackLinks(html) {
	const next = (text) => /<a href="([^"]+)" rel="next"/.exec(text)?.[1] ?? null;
	const container = /<div class="book-pagination"[\s\S]*?<\/footer>/.exec(html)?.[0] ?? '';
	const links = /<div class="pagination-links[^"]*"[^>]*>([\s\S]*?)<\/div>/.exec(container)?.[1] ?? '';
	const tracks = {};
	for (const match of container.matchAll(/<template data-book-track="([\w-]+)"[^>]*>([\s\S]*?)<\/template>/g)) tracks[match[1]] = next(match[2]);
	return { next: next(links), tracks };
}

/**
 * What the run visits, read from the build: `{ visits: [{ route, what }], chooser, track, moved: [{ from, to }],
 * problems }`. A kind without a built page, a build without a glossary page or a print view is a problem.
 */
export function plan(distDir) {
	const pages = sitePages(distDir);
	const problems = [];
	const byRoute = new Map(pages.map((page) => [page.route, page]));
	const visits = [];
	if (byRoute.has('')) visits.push({ route: '', what: 'the landing page' });
	else problems.push('the build has no landing page (index.html)');
	for (const kind of c_Kinds) {
		const page = pages.find((candidate) => !candidate.route.startsWith('print/') && pageKind(candidate.html) === kind && !movedTarget(candidate.html));
		if (page) visits.push({ route: page.route, what: `a page of the kind ${kind}` });
		else problems.push(`the build has no page of the kind ${kind}`);
	}
	const glossary = pages.find((page) => !page.route.startsWith('print/') && page.html.includes('<dl class="book-glossary"'));
	if (glossary) visits.push({ route: glossary.route, what: 'the glossary' });
	else problems.push('the build has no glossary page');
	const printed = pages.find((page) => page.route.startsWith('print/'));
	if (printed) visits.push({ route: printed.route, what: 'a print view' });
	else problems.push('the build has no print view');
	const moved = pages.filter((page) => movedTarget(page.html)).map((page) => ({ from: page.route, to: movedTarget(page.html) }));
	const chooserPage = pages.find((page) => !page.route.startsWith('print/') && page.html.includes('<book-track-chooser'));
	let chooser = null;
	let track = null;
	if (chooserPage) {
		chooser = chooserPage.route;
		track = chooseTrack(chooserPage, byRoute);
	} else {
		problems.push('the build has no page with the track chooser');
	}
	return { visits, chooser, track, moved, problems };
}

/**
 * The track whose "next" shows that the choice matters: following it from the chooser's page, the first track whose
 * next link differs from the page's default somewhere within c_TrackSteps pages; the chooser's first track when none
 * differs.
 */
export function chooseTrack(chooserPage, byRoute) {
	const names = [...chooserPage.html.matchAll(/class="book-track__choose" data-track="([\w-]+)"/g)].map((match) => match[1]);
	const base = basePath(chooserPage.html);
	let ending = null;
	for (const name of names) {
		let page = chooserPage;
		for (let step = 0; step < c_TrackSteps && page; step++) {
			const links = trackLinks(page.html);
			// A page with a template for the track follows it, even where the track ends (no next); others keep theirs.
			const next = Object.hasOwn(links.tracks, name) ? links.tracks[name] : links.next;
			if (next !== links.next) {
				// Best of all, a track whose next leads elsewhere than the page's own; else one that ends earlier.
				if (next) return name;
				ending ??= name;
				break;
			}
			page = next ? byRoute.get(next.slice(base.length + 1)) : null;
		}
	}
	return ending ?? names[0] ?? null;
}

/** The base a page's links start with ("/strata-engine-docs", "" at the root), read from its stylesheet links. */
export function basePath(html) {
	const match = /<link rel="stylesheet" href="([^"]*?)\/_astro\//.exec(html) ?? /<script type="module" src="([^"]*?)\/_astro\//.exec(html);
	return match ? match[1] : '';
}

/**
 * The problems of the recorded requests: `requests` holds `{ url, status, page, document, conditional }` (status null
 * for a request that got no answer; conditional true when the browser sent If-None-Match or If-Modified-Since), `site`
 * the site's base URL (ending with "/"), `missing` the URL of the missing page.
 *
 * A 304 passes only as the answer to a conditional request: Chromium revalidates a file it holds whose Cache-Control is
 * no-cache (pages, Pagefind's entry files) when a later page loads it again, and the server's 304 is that file's
 * correct answer. A 304 to a request that asked for no revalidation fails like any answer outside 2xx.
 */
export function requestProblems(requests, { site, missing }) {
	const problems = [];
	const base = new URL(site);
	for (const request of requests) {
		let url;
		try {
			url = new URL(request.url);
		} catch {
			problems.push(`${request.page}: a request to ${request.url}, which is no URL`);
			continue;
		}
		if (['data:', 'blob:', 'about:'].includes(url.protocol)) continue;
		if (url.origin !== base.origin) {
			problems.push(`${request.page}: a request leaves the origin: ${request.url}`);
			continue;
		}
		if (!url.pathname.startsWith(base.pathname)) {
			problems.push(`${request.page}: a request leaves the prefix ${base.pathname}: ${request.url}`);
			continue;
		}
		if (request.status === null) {
			// A request the browser cancelled because the page went on (net::ERR_ABORTED) is no answer of the site's.
			if (request.error === 'net::ERR_ABORTED') continue;
			problems.push(`${request.page}: ${request.url} got no answer${request.error ? ` (${request.error})` : ''}`);
		} else if (request.document && request.url === missing) {
			if (request.status !== 404) problems.push(`${request.url} answers ${request.status}, not 404 with the book's 404 page`);
		} else if (request.status === 304 && request.conditional === true) {
			continue;
		} else if (request.status < 200 || request.status > 299) {
			problems.push(`${request.page}: ${request.url} answers ${request.status}`);
		}
	}
	return problems;
}

/**
 * The problems of the browser's console and of the page's policy events: `messages` holds `{ type, text, url, page }`
 * (console messages and page errors), `violations` `{ page, directive, blocked }`. The missing page's own 404 is the
 * one console error that is expected: Chromium reports the status of the document it loads.
 */
export function consoleProblems(messages, violations, { missing }) {
	const problems = [];
	for (const message of messages) {
		if (message.type !== 'error' && message.type !== 'pageerror') continue;
		if (message.url === missing && /\b404\b/.test(message.text)) continue;
		problems.push(`${message.page}: ${message.type === 'pageerror' ? 'a script failed' : 'a console error'}: ${message.text}`);
	}
	for (const violation of violations) problems.push(`${violation.page}: the Content Security Policy blocked ${violation.blocked || 'an inline script or style'} (${violation.directive})`);
	return problems;
}

/** What is wrong with a moved page's answer: `{ status, location }` for the old address, `to` its new page's path. */
export function redirectProblem(answer, to, from) {
	if (answer.status !== 301) return `${from} answers ${answer.status}, not 301 to ${to}`;
	if (answer.location !== to) return `${from} answers 301 to ${answer.location ?? 'nothing'}, not to ${to} (a path, no scheme or host)`;
	return null;
}

/** The two searches: the first written glossary term and engine name of scripts/search-queries.json. */
export function searchQueries(data, written) {
	const first = (kind) => data.queries.find((entry) => entry.kind === kind && written(entry.page))?.query ?? null;
	return { term: first('term'), name: first('name') };
}

/** In the page: the policy's violations since the last call. */
function takeViolations() {
	return (window.bookViolations ?? []).splice(0);
}

/** Whether request headers (lower-case names, as Playwright gives them) ask the server to revalidate a held copy. */
export function isConditional(headers) {
	return Object.hasOwn(headers, 'if-none-match') || Object.hasOwn(headers, 'if-modified-since');
}

/**
 * Records every request, answer, console message and policy violation of a browser context. `pending` holds the reads
 * of a 304's request headers, which the run awaits before it closes the context: the conditional header is added by
 * Chromium's cache, so only the headers it really sent show it.
 */
function recorder(context) {
	const state = { page: '(start)', requests: new Map(), messages: [], violations: [], pending: [] };
	context.on('request', (request) => {
		state.requests.set(request, { url: request.url(), status: null, page: state.page, document: request.resourceType() === 'document' });
	});
	context.on('response', (response) => {
		const entry = state.requests.get(response.request());
		if (!entry) return;
		entry.status = response.status();
		if (entry.status !== 304) return;
		entry.conditional = false;
		state.pending.push(response.request().allHeaders().then((headers) => {
			entry.conditional = isConditional(headers);
		}, () => {
			// Headers that cannot be read leave the 304 unexplained, so it fails.
		}));
	});
	context.on('requestfailed', (request) => {
		const entry = state.requests.get(request);
		if (entry) entry.error = request.failure()?.errorText;
	});
	return state;
}

async function visit(page, state, url, label) {
	state.page = label;
	const response = await page.goto(url, { waitUntil: 'networkidle' });
	for (const violation of await page.evaluate(takeViolations)) state.violations.push({ page: label, ...violation });
	return response;
}

/** Crops on the current page at the three viewports, and the labels of its diagrams in its theme. */
async function measurePage(page, label, problems) {
	const { cropProblem, measureCrops } = await import('./crops.mjs');
	if (await page.$('img.book-crop__img')) {
		for (const width of c_CropViewports) {
			await page.setViewportSize({ width, height: 900 });
			for (const crop of await page.evaluate(measureCrops)) {
				const problem = cropProblem(crop);
				if (problem) problems.push(`${label} [${width} px] ${crop.src}: ${problem}`);
			}
		}
		await page.setViewportSize({ width: 1280, height: 900 });
	}
	if (await page.$('figure.book-diagram')) {
		const { measureDrawing } = await import('./diagram-checks.mjs');
		const theme = await page.evaluate(() => document.documentElement.dataset.theme || 'light');
		for (const handle of await page.$$(`figure.book-diagram .book-diagram__svg--${theme} svg`)) {
			if (!(await handle.isVisible())) continue;
			const { labels } = await measureDrawing(handle);
			for (const item of labels) problems.push(`${label}: the diagram label "${item.text}" leaves its box by ${item.by.toFixed(1)} px`);
		}
	}
}

/** Searches with Starlight's search dialog and follows the first result. */
async function search(page, state, site, query, problems, wait) {
	const label = `search "${query}"`;
	state.page = label;
	await page.goto(site, { waitUntil: 'networkidle' });
	await page.click('button[data-open-modal]');
	await page.fill('.pagefind-ui__search-input', query);
	const first = await page.waitForSelector('a.pagefind-ui__result-link', { timeout: wait }).catch(() => null);
	if (!first) {
		problems.push(`${label}: no result`);
		return;
	}
	const href = await first.evaluate((link) => link.href);
	if (!href.startsWith(site)) problems.push(`${label}: the first result ${href} is not under ${site}`);
	state.page = `${label}, its first result`;
	await Promise.all([page.waitForURL((url) => url.href !== site, { waitUntil: 'networkidle' }), first.click()]);
	for (const violation of await page.evaluate(takeViolations)) state.violations.push({ page: label, ...violation });
}

/** Switches the theme with Starlight's select and checks that the page follows. */
async function switchTheme(page, state, site, problems) {
	await visit(page, state, site, 'the theme switch');
	for (const theme of ['dark', 'light']) {
		await page.selectOption('starlight-theme-select select', theme);
		const shown = await page.evaluate(() => document.documentElement.dataset.theme);
		if (shown !== theme) problems.push(`the theme switch: choosing ${theme} shows ${shown}`);
	}
	for (const violation of await page.evaluate(takeViolations)) state.violations.push({ page: 'the theme switch', ...violation });
}

/** Chooses a track on the chooser's page and follows "next" on it: each page's next must be its track's. */
async function followTrack(page, state, site, chooser, track, problems) {
	await visit(page, state, site + chooser, 'the track chooser');
	await page.click(`.book-track__choose[data-track="${track}"]`);
	for (let step = 0; step < c_TrackSteps; step++) {
		const links = await page.evaluate((name) => {
			const container = document.querySelector('.book-pagination');
			const template = container?.querySelector(`template[data-book-track="${name}"]`);
			// A template's content is a document of its own: its links resolve against this page.
			const href = template?.content.querySelector('a[rel="next"]')?.getAttribute('href');
			return { shown: container?.querySelector('.pagination-links a[rel="next"]')?.href ?? null, expected: template ? (href ? new URL(href, document.baseURI).href : null) : undefined };
		}, track);
		if (links.expected === undefined) {
			// Every page of a track carries its template (src/components/Pagination.astro): "next" led off the track.
			problems.push(`track ${track}, ${page.url()}: the page has no "next" of the track`);
			return;
		}
		if (links.shown !== links.expected) {
			problems.push(`track ${track}, ${page.url()}: "next" leads to ${links.shown ?? 'nothing'}, not to the track's ${links.expected ?? 'end'}`);
			return;
		}
		if (!links.expected) break;
		state.page = `track ${track}, step ${step + 1}`;
		const before = page.url();
		await Promise.all([page.waitForURL((url) => url.href !== before, { waitUntil: 'networkidle' }), page.click('.book-pagination .pagination-links a[rel="next"]')]);
		if (page.url() !== links.expected) problems.push(`track ${track}: "next" opened ${page.url()}, not ${links.expected}`);
	}
}

/** The whole run against `site` (the base URL, ending with "/"): `{ problems, notes, counts }`. */
export async function runRuntime({ site, distDir, queriesFile = path.join(c_Root, 'scripts', 'search-queries.json'), steps = ['pages', 'search', 'theme', 'track', 'redirects'], searchWait = 15000 }) {
	const { chromium } = await import('playwright');
	const planned = plan(distDir);
	const problems = [...planned.problems];
	const notes = [];
	const missing = new URL(c_MissingPath, site).href;
	const browser = await chromium.launch();
	let state;
	try {
		const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
		await context.addInitScript(() => {
			window.bookViolations = [];
			document.addEventListener('securitypolicyviolation', (event) => window.bookViolations.push({ directive: event.violatedDirective, blocked: event.blockedURI }));
		});
		state = recorder(context);
		const page = await context.newPage();
		page.on('console', (message) => state.messages.push({ type: message.type(), text: message.text(), url: message.location()?.url ?? '', page: state.page }));
		page.on('pageerror', (error) => state.messages.push({ type: 'pageerror', text: String(error.message ?? error), url: '', page: state.page }));
		if (steps.includes('pages')) {
			for (const { route, what } of planned.visits) {
				const label = `${route || '(home)'} (${what})`;
				await visit(page, state, site + route, label);
				await measurePage(page, label, problems);
			}
			await visit(page, state, missing, `${c_MissingPath} (the missing path)`);
		}
		if (steps.includes('search')) {
			const written = (route) => existsSync(path.join(distDir, ...route.split('/'), 'index.html'));
			const queries = searchQueries(JSON.parse(readFileSync(queriesFile, 'utf8')), written);
			for (const [kind, query] of Object.entries(queries)) {
				if (query) await search(page, state, site, query, problems, searchWait);
				else problems.push(`no ${kind === 'term' ? 'glossary term' : 'engine name'} of ${path.basename(queriesFile)} has its page in the build: nothing to search for`);
			}
		}
		if (steps.includes('theme')) await switchTheme(page, state, site, problems);
		if (steps.includes('track') && planned.chooser !== null && planned.track) await followTrack(page, state, site, planned.chooser, planned.track, problems);
		if (steps.includes('redirects')) {
			if (planned.moved.length === 0) notes.push('the build has no moved page (src/redirects.json is empty; the build at /x/y adds the test entry): no 301 was checked');
			for (const { from, to } of planned.moved) {
				const response = await context.request.get(site + from, { maxRedirects: 0 });
				const problem = redirectProblem({ status: response.status(), location: response.headers().location }, to, site + from);
				if (problem) problems.push(problem);
			}
		}
		while (state.pending.length > 0) await Promise.all(state.pending.splice(0));
		await context.close();
	} finally {
		await browser.close();
	}
	const requests = [...state.requests.values()];
	problems.push(...requestProblems(requests, { site, missing }), ...consoleProblems(state.messages, state.violations, { missing }));
	return { problems, notes, counts: { requests: requests.length, pages: planned.visits.length + 1, moved: planned.moved.length, track: planned.track } };
}

async function main(argv) {
	const option = (name, fallback = null) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const root = path.resolve(option('--root', c_Root));
	const distDir = path.resolve(option('--dist', path.join(root, 'dist')));
	const { serveSite } = await import('./serve.mjs');
	const served = await serveSite({ argv });
	let result;
	try {
		result = await runRuntime({ site: served.url, distDir });
	} finally {
		await served.stop();
	}
	for (const problem of result.problems) console.log(problem);
	for (const note of result.notes) console.log(`runtime: note: ${note}`);
	console.log(`runtime: ${result.counts.requests} requests from ${result.counts.pages} pages, two searches, the theme, track ${result.counts.track ?? '(none)'}, ${result.counts.moved} moved page${result.counts.moved === 1 ? '' : 's'}; ${result.problems.length} problem${result.problems.length === 1 ? '' : 's'}`);
	const json = option('--json');
	if (json) writeFileSync(json, `${JSON.stringify(result)}\n`);
	return result.problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

// The search test (plan/site.md, "Search"; budget row 13): Pagefind's own script runs in Chromium on the built site,
// under the base path, for each of the fixed queries of scripts/search-queries.json (30 glossary terms, 20 engine names
// and 10 questions, each with the page expected). The test passes when the expected page is among the first three
// results for at least 90 % of the queries and for every engine name.
//
// A query whose page is not written yet is not judged: the book is written in waves, and search can only find what
// exists. The test reports how many queries wait for their page, and with --release (a whole book) every page must
// exist. It fails when it has no query to judge.
//
//     node scripts/search-quality.mjs [--url http://host/strata-engine-docs/] [--root <book folder>] [--release]
//         [--queries <file>] [--glossary <file>] [--json <file>]
//     node scripts/search-quality.mjs --check [--glossary <file>]     the query file only, without a browser
//
// --glossary checks the term queries against another glossary than src/content/glossary.json (the seed, for example).

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { normalizeGlossary } from '../src/lib/glossary.mjs';
import { loadOutline } from '../src/lib/outline.mjs';
import { c_SearchRanking } from '../src/lib/search.mjs';
import { routeIdOf } from '../src/lib/sidebar.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// What the plan fixes (site.md, "Search"): how many queries of each kind, how many results count, the share that must
// find their page, and the kind that must always find it.
export const c_QueryCounts = { term: 30, name: 20, question: 10 };
export const c_TopResults = 3;
export const c_PassShare = 0.9;
export const c_AlwaysFound = 'name';

/**
 * The queries of the file's data, checked: `{ queries, problems }`. Every query names an outline row; a term the
 * glossary holds expects the entry's home page.
 */
export function readQueries(data, { outline, glossary }) {
	const problems = [];
	if (!data || typeof data !== 'object' || !Array.isArray(data.queries)) return { queries: [], problems: ['the file is {"queries": [{"kind", "query", "page"}]}'] };
	const names = new Map();
	for (const term of glossary.terms) {
		for (const name of [term.term, ...term.aliases]) names.set(name.toLowerCase(), term);
	}
	const seen = new Set();
	const queries = [];
	const counts = Object.fromEntries(Object.keys(c_QueryCounts).map((kind) => [kind, 0]));
	data.queries.forEach((entry, index) => {
		const where = `query ${index + 1} (${JSON.stringify(entry?.query ?? '?')})`;
		if (!entry || typeof entry !== 'object' || Object.keys(entry).some((key) => !['kind', 'query', 'page'].includes(key))) {
			problems.push(`${where}: a query is {"kind", "query", "page"}`);
			return;
		}
		if (!Object.hasOwn(c_QueryCounts, entry.kind)) {
			problems.push(`${where}: "kind" is one of ${Object.keys(c_QueryCounts).join(', ')}`);
			return;
		}
		if (typeof entry.query !== 'string' || !entry.query.trim()) {
			problems.push(`${where}: "query" is the words a reader types`);
			return;
		}
		const key = entry.query.trim().toLowerCase();
		if (seen.has(key)) problems.push(`${where}: the query is in the file twice`);
		seen.add(key);
		if (typeof entry.page !== 'string' || !outline.rows.has(entry.page)) {
			problems.push(`${where}: "page" is the id of a row of the outline (src/generated/outline.json), not ${JSON.stringify(entry.page)}`);
			return;
		}
		const term = entry.kind === 'term' ? names.get(key) : null;
		if (term && term.home !== entry.page) problems.push(`${where}: the glossary's entry "${term.term}" has its home on ${term.home}, so the query expects that page, not ${entry.page}`);
		counts[entry.kind]++;
		queries.push({ kind: entry.kind, query: entry.query.trim(), page: entry.page });
	});
	for (const [kind, count] of Object.entries(c_QueryCounts)) {
		if (counts[kind] !== count) problems.push(`the file holds ${counts[kind]} queries of kind "${kind}"; the test has ${count} (site.md, "Search")`);
	}
	return { queries, problems };
}

/** The route id of a result's URL under the base ("/book/core/time/#x" → "core/time"; the landing page is "index"). */
export function resultRoute(url, base) {
	const pathname = new URL(url, 'http://book.invalid').pathname;
	const prefix = `${base}/`;
	if (!pathname.startsWith(prefix)) return null;
	const route = decodeURIComponent(pathname.slice(prefix.length)).replace(/\/(index\.html)?$/, '');
	return route || 'index';
}

/**
 * Judges the results: `queries` with `written(page)` saying whether the page exists and `results` mapping each judged
 * query to the URLs of its results in order. Returns `{ judged, found, waiting, misses, share, passed, problems }`.
 */
export function judgeQueries(queries, results, { base, written, release = false }) {
	const misses = [];
	const waiting = [];
	let judged = 0;
	let found = 0;
	for (const query of queries) {
		if (!written(query.page)) {
			waiting.push(query);
			continue;
		}
		judged++;
		const routes = (results.get(query.query) ?? []).slice(0, c_TopResults).map((url) => resultRoute(url, base));
		if (routes.includes(routeIdOf(query.page))) found++;
		else misses.push({ ...query, routes });
	}
	const share = judged ? found / judged : 0;
	const problems = [];
	if (judged === 0) problems.push('no query has its page written yet: nothing to judge');
	else if (share < c_PassShare) problems.push(`${found} of ${judged} queries find their page among the first ${c_TopResults} results (${(share * 100).toFixed(1)} %); the test needs ${c_PassShare * 100} %`);
	for (const miss of misses.filter((query) => query.kind === c_AlwaysFound)) problems.push(`the engine name ${JSON.stringify(miss.query)} does not find ${miss.page} among the first ${c_TopResults} results: every engine name must`);
	if (release) for (const query of waiting) problems.push(`${JSON.stringify(query.query)} expects ${query.page}, which a release build must hold`);
	return { judged, found, waiting, misses, share, passed: problems.length === 0, problems };
}

function option(argv, name, fallback = null) {
	const index = argv.indexOf(name);
	return index >= 0 ? argv[index + 1] : fallback;
}

function readJson(file) {
	return JSON.parse(readFileSync(file, 'utf8'));
}

async function main(argv) {
	const root = path.resolve(option(argv, '--root', c_Root));
	const queriesFile = path.resolve(option(argv, '--queries', path.join(c_Root, 'scripts', 'search-queries.json')));
	const glossaryFile = path.resolve(option(argv, '--glossary', path.join(root, 'src', 'content', 'glossary.json')));
	const outline = loadOutline(path.join(root, 'src', 'generated', 'outline.json'));
	const glossary = normalizeGlossary(readJson(glossaryFile));
	const { queries, problems } = readQueries(readJson(queriesFile), { outline, glossary });
	if (glossary.problems.length) problems.unshift(...glossary.problems.map((problem) => `${glossaryFile}: ${problem}`));
	if (problems.length) {
		for (const problem of problems) console.log(`search-quality: ${path.relative(c_Root, queriesFile)}: ${problem}`);
		return 1;
	}
	if (argv.includes('--check')) {
		console.log(`search-quality: ${queries.length} queries, every page a row of the outline`);
		return 0;
	}
	const written = (page) => existsSync(path.join(root, 'src', 'content', 'docs', ...`${page}.md`.split('/')));
	const { chromium } = await import('playwright');
	const { serveSite } = await import('./serve.mjs');
	const site = await serveSite({ argv });
	const base = new URL(site.url).pathname.replace(/\/$/, '');
	const browser = await chromium.launch();
	const results = new Map();
	try {
		const page = await browser.newPage();
		await page.goto(site.url, { waitUntil: 'load' });
		// Pagefind's own script, as Starlight's search loads it, with the base as its URLs' prefix and the ranking the
		// site's search is given (src/lib/search.mjs).
		await page.evaluate(async ({ bundle, ranking }) => {
			window.bookPagefind = await import(bundle);
			await window.bookPagefind.options({ baseUrl: new URL('..', bundle).pathname, ranking });
			await window.bookPagefind.init();
		}, { bundle: `${site.url}pagefind/pagefind.js`, ranking: c_SearchRanking });
		for (const query of queries.filter((entry) => written(entry.page))) {
			const urls = await page.evaluate(async ({ words, top }) => {
				const search = await window.bookPagefind.search(words);
				const data = await Promise.all(search.results.slice(0, top).map((result) => result.data()));
				return data.map((result) => result.url);
			}, { words: query.query, top: c_TopResults });
			results.set(query.query, urls);
		}
	} finally {
		await browser.close();
		await site.stop();
	}
	const release = argv.includes('--release') || process.env.DOCS_RELEASE === '1';
	const verdict = judgeQueries(queries, results, { base, written, release });
	for (const miss of verdict.misses) console.log(`  miss (${miss.kind}): ${JSON.stringify(miss.query)} expects ${miss.page}; the first results are ${miss.routes.join(', ') || 'none'}`);
	for (const problem of verdict.problems) console.log(`search-quality: ${problem}`);
	console.log(`search-quality: ${verdict.found} of ${verdict.judged} judged queries find their page among the first ${c_TopResults} results; ${verdict.waiting.length} wait for their page to be written`);
	const json = option(argv, '--json');
	if (json) writeFileSync(json, `${JSON.stringify({ judged: verdict.judged, found: verdict.found, waiting: verdict.waiting.length, share: verdict.share, misses: verdict.misses, passed: verdict.passed })}\n`);
	return verdict.passed ? 0 : 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

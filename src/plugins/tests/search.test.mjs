// What a page tells search (plan/site.md, "Search"): the title of its result with its part and kind, its metadata and
// its filters (src/lib/search.mjs, written into the page by src/components/PageTitle.astro).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { indexOutline } from '../../lib/outline.mjs';
import { searchFacts, titleMeta } from '../../lib/search.mjs';
import { testOutlineOf } from './helpers.mjs';

const outline = indexOutline(testOutlineOf({
	'core/time': { title: 'Time: delta time, fixed steps and time scale', kind: 'concept', tracks: ['E'] },
	'make/first-script': { title: 'Your first script', kind: 'tutorial', tracks: ['G', 'B'] },
	'reference/glossary': { title: 'Glossary', kind: 'reference', tracks: [] },
}), 'test');

test('a result\'s title names the page, its part and its kind, and its filters name its part, kind and tracks', () => {
	const time = searchFacts({ data: { id: 'core/time', title: 'Time: delta time, fixed steps and time scale', kind: 'concept', tracks: ['E'] }, outline });
	assert.deepEqual(time, { title: 'Time: delta time, fixed steps and time scale · Engine architecture · Concept', part: 'Engine architecture', kind: 'Concept', tracks: ['Engine builder'] });
	// The whole title is one inline entry: Pagefind reads it to the end of the attribute, its colon and commas included.
	assert.equal(titleMeta(time), 'title:Time: delta time, fixed steps and time scale · Engine architecture · Concept');
	const script = searchFacts({ data: { id: 'make/first-script', title: 'Your first script', kind: 'tutorial', tracks: ['G', 'B'] }, outline });
	assert.deepEqual(script.tracks, ['Game maker', 'Beginner']);
	assert.equal(script.title, 'Your first script · Making games · Tutorial');
	// A page on no track has no track filter.
	assert.deepEqual(searchFacts({ data: { id: 'reference/glossary', title: 'Glossary', kind: 'reference', tracks: [] }, outline }).tracks, []);
});

test('a part\'s index and review pages are named as such, and pages outside the parts keep search\'s own title', () => {
	assert.equal(searchFacts({ data: { id: 'core/index', title: 'Engine architecture', tracks: ['E'], generated: 'index' }, outline }).title, 'Engine architecture · Engine architecture · Part overview');
	assert.equal(searchFacts({ data: { id: 'core/review', title: 'Review: engine architecture', tracks: ['E'], generated: 'review' }, outline }).kind, 'Part review');
	assert.equal(searchFacts({ data: { title: 'The Strata Engine Book' }, outline }), null);
	assert.equal(searchFacts({ data: { id: 'nowhere/page', title: 'A page', kind: 'concept' }, outline }), null);
	assert.equal(searchFacts({ data: { id: 'core/time', title: 'Time', kind: 'essay' }, outline }), null);
});

// The search test (scripts/search-quality.mjs): its fixed queries, how a result's URL names a page, and the verdict.
const c_Glossary = { terms: [{ id: 'fixed-step', term: 'fixed step', definition: 'A step.', home: 'core/time', aliases: ['tick'], avoid: [], known: false, use: null }] };

function queriesOf(counts, make = (kind, n) => ({ kind, query: `${kind} ${n}`, page: 'core/time' })) {
	return Object.entries(counts).flatMap(([kind, count]) => Array.from({ length: count }, (_, n) => make(kind, n)));
}

test('the query file holds 30 terms, 20 engine names and 10 questions, each expecting a row of the outline', async () => {
	const { c_QueryCounts, readQueries } = await import('../../../scripts/search-quality.mjs');
	assert.deepEqual(c_QueryCounts, { term: 30, name: 20, question: 10 });
	const good = queriesOf(c_QueryCounts);
	assert.deepEqual(readQueries({ queries: good }, { outline, glossary: c_Glossary }).problems, []);
	const read = (queries) => readQueries({ queries }, { outline, glossary: c_Glossary }).problems.join('\n');
	assert.match(read(good.slice(1)), /the file holds 29 queries of kind "term"; the test has 30/);
	assert.match(read([...good.slice(1), { kind: 'term', query: 'name 0', page: 'core/time' }]), /query 60 \("name 0"\): the query is in the file twice/);
	assert.match(read([{ kind: 'guess', query: 'x', page: 'core/time' }]), /"kind" is one of term, name, question/);
	assert.match(read([{ kind: 'term', query: 'x', page: 'core/nowhere' }]), /"page" is the id of a row of the outline \(src\/generated\/outline\.json\), not "core\/nowhere"/);
	assert.match(read([{ kind: 'term', query: 'x', page: 'core/time', weight: 2 }]), /a query is \{"kind", "query", "page"\}/);
	// A term the glossary holds, by its name or another name, expects the entry's home.
	assert.match(read([{ kind: 'term', query: 'Tick', page: 'make/first-script' }]), /the glossary's entry "fixed step" has its home on core\/time, so the query expects that page, not make\/first-script/);
	assert.doesNotMatch(read([{ kind: 'question', query: 'tick', page: 'make/first-script' }]), /glossary/);
});

test('the committed queries fit the outline and the glossary', async () => {
	const { readFileSync } = await import('node:fs');
	const { readQueries } = await import('../../../scripts/search-quality.mjs');
	const { loadGlossary } = await import('../../lib/glossary.mjs');
	const { loadOutline } = await import('../../lib/outline.mjs');
	const root = new URL('../../../', import.meta.url);
	const data = JSON.parse(readFileSync(new URL('scripts/search-queries.json', root), 'utf8'));
	const result = readQueries(data, { outline: loadOutline(new URL('src/generated/outline.json', root)), glossary: loadGlossary(new URL('src/content/glossary.json', root)) });
	assert.deepEqual(result.problems, []);
	assert.equal(result.queries.length, 60);
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`a result's URL names its page under the base ${setting}`, async () => {
		const { resultRoute } = await import('../../../scripts/search-quality.mjs');
		assert.equal(resultRoute(`${base}/core/time/`, base), 'core/time');
		assert.equal(resultRoute(`${base}/core/time/#the-accumulator`, base), 'core/time');
		assert.equal(resultRoute(`${base}/core/`, base), 'core');
		assert.equal(resultRoute(`${base}/`, base), 'index');
		assert.equal(resultRoute(`http://127.0.0.1:4321${base}/world/interpolation/`, base), 'world/interpolation');
		if (base) assert.equal(resultRoute('/elsewhere/core/time/', base), null);
	});
}

test('the verdict: 90 % of the judged queries and every engine name find their page; unwritten pages wait', async () => {
	const { judgeQueries } = await import('../../../scripts/search-quality.mjs');
	const queries = [
		...Array.from({ length: 9 }, (_, n) => ({ kind: 'term', query: `term ${n}`, page: 'core/time' })),
		{ kind: 'question', query: 'why', page: 'core/index' },
		{ kind: 'name', query: 'ST_CORE_ASSERT', page: 'core/conventions' },
		{ kind: 'term', query: 'later', page: 'image/taa' },
	];
	const written = (page) => page !== 'image/taa';
	const results = new Map(queries.map((query) => [query.query, ['/b/reference/glossary/', '/b/world/ecs/', `/b/${query.page.replace(/\/index$/, '')}/#x`, '/b/core/time/']]));
	let verdict = judgeQueries(queries, results, { base: '/b', written });
	assert.deepEqual([verdict.judged, verdict.found, verdict.waiting.length, verdict.passed], [11, 11, 1, true]);
	// The fourth result does not count.
	results.set('why', ['/b/a/', '/b/c/', '/b/d/', '/b/core/']);
	verdict = judgeQueries(queries, results, { base: '/b', written });
	assert.deepEqual([verdict.found, verdict.passed], [10, true]);
	assert.deepEqual(verdict.misses.map((miss) => miss.query), ['why']);
	// Below 90 %, and an engine name that misses, fail.
	results.set('term 0', []);
	verdict = judgeQueries(queries, results, { base: '/b', written });
	assert.match(verdict.problems.join('\n'), /9 of 11 queries find their page among the first 3 results \(81\.8 %\); the test needs 90 %/);
	results.set('term 0', ['/b/core/time/']);
	results.set('why', ['/b/core/']);
	results.set('ST_CORE_ASSERT', ['/b/core/time/']);
	verdict = judgeQueries(queries, results, { base: '/b', written });
	assert.deepEqual(verdict.problems, ['the engine name "ST_CORE_ASSERT" does not find core/conventions among the first 3 results: every engine name must']);
	// A release holds every page; with nothing written there is nothing to judge.
	assert.match(judgeQueries(queries, results, { base: '/b', written: () => true, release: true }).problems.join('\n'), /ST_CORE_ASSERT/);
	assert.match(judgeQueries(queries, new Map(), { base: '/b', written, release: true }).problems.join('\n'), /"later" expects image\/taa, which a release build must hold/);
	assert.deepEqual(judgeQueries(queries, new Map(), { base: '/b', written: () => false }).problems, ['no query has its page written yet: nothing to judge']);
});

test('npm run preview serves the built site with search, through the staged server of tools/crawl.py', async () => {
	const { readFileSync } = await import('node:fs');
	const { previewCommand } = await import('../../../scripts/serve.mjs');
	const manifest = JSON.parse(readFileSync(new URL('../../../package.json', import.meta.url), 'utf8'));
	assert.equal(manifest.scripts.preview, 'node scripts/serve.mjs');
	assert.equal(manifest.scripts['check:search-quality'], 'node scripts/search-quality.mjs');
	const command = previewCommand([], { env: {}, platform: 'linux' });
	assert.equal(command.program, 'python3');
	assert.deepEqual(command.args.slice(2), ['--serve-only', '--root', command.args[4], '--port', '4321']);
	assert.match(command.args[1], /tools[\\/]crawl\.py$/);
	const chosen = previewCommand(['--port', '8000'], { env: { PYTHON: 'C:/Python/python.exe' }, platform: 'win32' });
	assert.equal(chosen.program, 'C:/Python/python.exe');
	assert.equal(chosen.args.at(-1), '8000');
});

test('the transfer test counts bytes as nginx sends them and holds the first and the next query to their budgets', async () => {
	const { budgetProblems, totals, wireBytes } = await import('../../../scripts/search-payload.mjs');
	const text = Buffer.from('x'.repeat(4000));
	assert.ok(wireBytes(text, 'text/javascript') < 100);
	assert.equal(wireBytes(text, 'application/octet-stream'), 4000);
	assert.deepEqual(totals([{ raw: 3, wire: 2 }, { raw: 5, wire: 4 }]), { raw: 8, wire: 6 });
	const limits = { maxKilobytes: 300, maxNextKilobytes: 100 };
	assert.deepEqual(budgetProblems({ first: 300 * 1024, next: 100 * 1024 }, limits), []);
	assert.deepEqual(budgetProblems({ first: 301 * 1024, next: 101 * 1024 }, limits), ['the first query downloaded 301.0 KB, over the budget of 300 KB', 'the next query downloaded 101.0 KB, over the budget of 100 KB']);
	const { readFileSync } = await import('node:fs');
	const budgets = JSON.parse(readFileSync(new URL('../../../tools/budgets.json', import.meta.url), 'utf8'));
	assert.equal(typeof budgets.search_next_query_kilobytes, 'number');
});

test('the search test ranks as the site\'s search does', async () => {
	const { readFileSync: read } = await import('node:fs');
	const book = new URL('../../../', import.meta.url);
	assert.match(read(new URL('astro.config.mjs', book), 'utf8'), /pagefind: \{ ranking: c_SearchRanking \}/);
	assert.match(read(new URL('scripts/search-quality.mjs', book), 'utf8'), /ranking: c_SearchRanking/);
});

test('the build gives Pagefind the book\'s chunk size', async () => {
	const { readFileSync: read } = await import('node:fs');
	const { c_SearchIndexChunkSize, searchIndexEnvironment } = await import('../../lib/search.mjs');
	assert.deepEqual(searchIndexEnvironment(), { PAGEFIND_UNSTABLE_INDEX_CHUNK_SIZE: String(c_SearchIndexChunkSize) });
	const book = new URL('../../../', import.meta.url);
	assert.match(read(new URL('src/integrations/book.mjs', book), 'utf8'), /if \(command === 'build'\) Object\.assign\(process\.env, searchIndexEnvironment\(\)\);/);
});

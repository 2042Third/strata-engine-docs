// The front matter of a page (src/lib/frontmatter.mjs, run by the strips plugin): the keys of style.md §6.1, the outline
// rules one page is checked against (O1 to O8), the bottom strip of each kind and the answers' `tests` (rule P2).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bookProblems, partPagesProblems } from '../../integrations/book.mjs';
import { checkFrontmatter, compareReleases, findNeedCycles } from '../../lib/frontmatter.mjs';
import { indexOutline } from '../../lib/outline.mjs';
import { parsePin, readSettings } from '../../lib/settings.mjs';
import { reservedSegmentProblem } from '../../lib/sidebar.mjs';
import { createBookContext } from '../index.mjs';
import { c_BottomStrip, c_Pin, c_ReferenceStrip, frontmatter, makeBook, primerBody, rejectsWith, render, testOutline, testOutlineOf, testSidebar } from './helpers.mjs';

const c_Learn = [{ id: 'one-thing', text: 'explain one thing' }, { id: 'another-thing', text: 'compute another thing' }];

/** A page of core as the page index holds it, with the front matter `data`. */
function chapter(id, data = {}) {
	return { id, error: null, data: { id, title: 'A page', description: 'A page.', kind: 'concept', size: 'M', tracks: ['E'], needs: [], time: 20, learn: c_Learn, since: '0.3.0', status: 'draft', ...data } };
}

/** The checks' view of a book of `pages` (page index entries); `edit(outline data)` changes the outline first. */
function bookOf(pages, { edit, release = false } = {}) {
	const data = testOutlineOf(Object.fromEntries(pages.map((page) => [page.id, page.data])));
	edit?.(data);
	const outline = indexOutline(data);
	return { outline, sidebar: testSidebar(data, new Set(pages.map((page) => page.id))), pages: new Map(pages.map((page) => [page.id, page])), pin: parsePin(c_Pin), release };
}

const problemsOf = (page, book) => checkFrontmatter(page, book).join('\n');

test('a chapter carries the keys of style.md §6.1 in their shapes', () => {
	const good = chapter('core/time');
	assert.deepEqual(checkFrontmatter(good, bookOf([good])), []);
	const bad = chapter('core/time', { kind: 'essay', size: 'XXL', tracks: ['players'], time: 'soon', status: 'done', description: 'x'.repeat(161) });
	const problems = problemsOf(bad, bookOf([chapter('core/time')]));
	assert.match(problems, /"kind" must be one of primer, concept, internals, tutorial, how-to, reference/);
	assert.match(problems, /"size" must be one of S, M, L, XL/);
	assert.match(problems, /"tracks" holds "players"; a track is one of the letters G, B, E/);
	assert.match(problems, /"time" must be the minutes the page takes/);
	assert.match(problems, /"status" must be one of draft, reviewed, final/);
	assert.match(problems, /"description" is 161 characters; at most 160/);
	// The spike's keys and Starlight's keys that change a page's URL, state, navigation or head are refused; display keys
	// pass; anything else is a typo.
	const keys = chapter('core/time', { level: 2, prerequisites: [], engine: '0.8.0', slug: 'x', prev: false, head: [], editUrl: false, objectives: [], template: 'doc', tableOfContents: false, description: 'No full stop' });
	const refused = problemsOf(keys, bookOf([chapter('core/time')]));
	assert.match(refused, /"level" is not a key of the book's pages: the level is computed from the Needs closure/);
	assert.match(refused, /"prerequisites" is not a key of the book's pages: the key is "needs"/);
	assert.match(refused, /"engine" is not a key of the book's pages: the engine release comes from engine\.pin/);
	assert.match(refused, /"slug" is not a key of the book's pages: a page's URL is its id/);
	assert.match(refused, /"prev" is not a key of the book's pages/);
	assert.match(refused, /"head" is not a key of the book's pages: pages set no head entries/);
	// The book's repository is not public: no page links to it, not even to be edited.
	assert.match(refused, /"editUrl" is not a key of the book's pages: the book's repository is not public/);
	assert.match(refused, /"objectives" is not a key of the book's pages \(style\.md §6\.1; Starlight's display keys: template, hero/);
	assert.doesNotMatch(refused, /"template"|"tableOfContents"/);
	assert.match(refused, /"description" is one sentence: it ends with "\.", "\?" or "!"/);
});

test('objectives: two to five, unique ids, each starting with an observable verb', () => {
	const learn = [
		{ id: 'one', text: 'understand the loop' },
		{ id: 'one', text: 'derive the alpha' },
		{ id: 'Bad Id', text: 'be familiar with steps' },
		{ id: 'four', text: 'explain it', note: 'x' },
	];
	const page = chapter('core/time', { learn });
	const problems = problemsOf(page, bookOf([page]));
	assert.match(problems, /item 1: "understand the loop" starts with "understand", which no reader can be seen doing/);
	assert.match(problems, /item 2: the id "one" is used twice on the page/);
	assert.match(problems, /item 2: "derive the alpha" starts with "derive"; an objective starts with an observable verb: explain, compute/);
	assert.match(problems, /item 3: "id" must be lowercase words joined by hyphens/);
	assert.match(problems, /item 3: "be familiar with steps" starts with "be familiar with"/);
	assert.match(problems, /item 4 holds "note"; an objective has only "id" and "text"/);
	const one = chapter('core/time', { learn: [c_Learn[0]] });
	assert.match(problemsOf(one, bookOf([one])), /"learn" must hold two to five objectives/);
	const strings = chapter('core/time', { learn: ['explain a', 'explain b'] });
	assert.match(problemsOf(strings, bookOf([strings])), /item 1 is not "id: …" and "text: …"/);
});

test('since: on concept, internals, tutorial and how-to pages of parts 1 and 3 to 21, never later than the pin', () => {
	const missing = chapter('core/time', { since: undefined });
	assert.match(problemsOf(missing, bookOf([missing])), /"since" must be the first release whose engine had the subject/);
	const later = chapter('core/time', { since: '0.9.0' });
	assert.match(problemsOf(later, bookOf([later])), /"since" is 0\.9\.0, later than the book's release 0\.8\.0/);
	const older = chapter('core/time', { since: '0.2.9' });
	assert.match(problemsOf(older, bookOf([older])), /"since" is 0\.2\.9; anything older than the engine's first tag is 0\.3\.0/);
	const start = chapter('start/welcome', { since: '0.3.0' });
	assert.match(problemsOf(start, bookOf([start])), /"since" is absent on concept pages of the part "start"/);
	const primer = chapter('basics/numbers', { kind: 'primer', since: undefined });
	assert.deepEqual(checkFrontmatter(primer, bookOf([primer])), []);
	const reference = chapter('reference/commands', { kind: 'reference', since: undefined, time: undefined, learn: undefined });
	assert.deepEqual(checkFrontmatter(reference, bookOf([reference])), []);
	const withTime = chapter('reference/commands', { kind: 'reference', since: undefined });
	assert.match(problemsOf(withTime, bookOf([withTime])), /"time" is absent on reference pages[\s\S]*"learn" is absent on reference pages/);
	assert.ok(compareReleases('0.10.0', '0.9.1') > 0);
	assert.equal(compareReleases('0.8.0', '0.8.0'), 0);
});

test('O1: the id is the file\'s path; reserved first segments are refused', () => {
	const page = chapter('core/time', { id: 'core/clock' });
	assert.match(problemsOf(page, bookOf([chapter('core/time')])), /O1: "id" must be the file's path under src\/content\/docs\/ without \.md: id: core\/time/);
	assert.match(reservedSegmentProblem('print/core'), /reserved for the site's own files/);
	assert.match(reservedSegmentProblem('downloads/tutorials'), /"downloads" is reserved for the site's own files \(print, pagefind, downloads, _astro, _figures, 404\)/);
	assert.match(reservedSegmentProblem('v0/notes'), /reserved for archived versions/);
	assert.equal(reservedSegmentProblem('core/time'), null);
	const nowhere = chapter('nowhere/page');
	assert.match(problemsOf(nowhere, bookOf([chapter('core/time')])), /in no part of the book: its folder "nowhere" is no part's slug/);
});

test('O2 and O3: Needs are rows of the outline, at most five ids; a release links every Need', () => {
	const rows = (data) => {
		for (const id of ['core/map', 'core/jobs', 'core/files', 'core/math', 'core/platform']) data.pages.push({ id, title: id, kind: 'concept', size: 'M', tracks: [], needs: [], part: 'core', level: 1, row: 'test' });
	};
	const page = chapter('core/time', { tracks: [], needs: ['core/map', 'core/jobs|core/files', 'core/math|core/platform', 'core/gone', 'core/time', 'core/map'] });
	const problems = problemsOf(page, bookOf([page], { edit: rows }));
	assert.match(problems, /"needs" lists "core\/map" twice/);
	assert.match(problems, /O2: the Need "core\/gone" is no row of the outline/);
	assert.match(problems, /"needs" names the page itself/);
	assert.match(problems, /O3: "needs" names 8 page ids, alternatives included; at most 5/);
	const draft = chapter('core/time', { tracks: [], needs: ['core/map'] });
	assert.doesNotMatch(problemsOf(draft, bookOf([draft], { edit: rows })), /O2/);
	assert.match(problemsOf(draft, bookOf([draft], { edit: rows, release: true })), /O2: the Need "core\/map" is not written yet, and a release build links every Need/);
});

test('O4, O5 and O7: the page equals its row, its Needs come earlier on its tracks, and its tracks hold it', () => {
	const later = chapter('core/later');
	const time = chapter('core/time', { needs: ['core/later'] });
	// core/time comes before core/later on track E.
	const problems = problemsOf(time, bookOf([time, later]));
	assert.match(problems, /O4: on track E, no alternative of the Need "core\/later" comes before this page/);
	const drift = chapter('core/time');
	const book = bookOf([drift], {
		edit: (data) => Object.assign(data.pages[0], { title: 'Time: the clock', kind: 'internals', size: 'L', tracks: ['E', 'B'], needs: ['core/time-two'] }),
	});
	const drifted = problemsOf(drift, book);
	assert.match(drifted, /O7: "title" is "A page"; its row \(plan\/outline-test\.md:1\) says "Time: the clock"/);
	assert.match(drifted, /O7: "kind" is "concept"; its row \(plan\/outline-test\.md:1\) says "internals"/);
	assert.match(drifted, /O7: "size" is "M"; its row/);
	assert.match(drifted, /O7: "tracks" is \[E\]; its row \(plan\/outline-test\.md:1\) says \[E, B\]/);
	assert.match(drifted, /O7: "needs" is \[\]; its row/);
	// Tracks are compared as a set, in any order.
	const both = chapter('core/time', { tracks: ['E', 'B'] });
	assert.doesNotMatch(problemsOf(both, bookOf([both], { edit: (data) => { data.pages[0].tracks = ['B', 'E']; } })), /O7/);
	const held = chapter('core/time');
	const elsewhere = bookOf([held]);
	elsewhere.sidebar.tracks.engine.sequence = [];
	elsewhere.sidebar.tracks.beginner.sequence = ['core/time'];
	assert.match(problemsOf(held, elsewhere), /O5: "tracks" is \[E\], but the tracks of src\/sidebar\.json that hold the page are \[B\]/);
	const unlisted = chapter('core/extra');
	assert.match(problemsOf(unlisted, bookOf([chapter('core/time')])), /O7: the page has no row in the outline/);
});

test('O6: Needs that form a cycle among the written pages are found', () => {
	const pages = new Map([['a', { needs: ['b'] }], ['b', { needs: ['c|d'] }], ['c', { needs: ['a'] }], ['d', { needs: [] }]]);
	assert.deepEqual(findNeedCycles(pages), [['a', 'b', 'c', 'a']]);
});

test('O8: part pages carry their own keys, stand in parts of eight or more rows and come in pairs', async () => {
	const partPage = (id, data) => ({ id, error: null, data: { id, title: 'Engine architecture', description: 'The part.', tracks: ['E'], status: 'draft', ...data } });
	const index = partPage('core/index', { generated: 'index' });
	const withPages = (data) => { data.parts[3].partPages = true; data.parts[3].tracks = ['E']; };
	assert.deepEqual(checkFrontmatter(index, bookOf([chapter('core/time'), index], { edit: withPages })), []);
	assert.match(problemsOf(index, bookOf([chapter('core/time'), index])), /O8: the part "core" has 1 rows; only parts of eight or more rows have an index and a review page/);
	const wrong = partPage('core/index', { generated: 'review', kind: 'concept', tracks: ['G'] });
	const problems = problemsOf(wrong, bookOf([chapter('core/time'), wrong], { edit: withPages }));
	assert.match(problems, /a part page carries "id", "title", "description", "tracks", "status", "generated", not "kind"/);
	assert.match(problems, /O8: a page with "generated: review" is the file src\/content\/docs\/core\/review\.md/);
	assert.match(problems, /"tracks" of a part page are the part's: \[E\]/);
	const plain = chapter('core/review', { kind: 'concept' });
	assert.match(problemsOf(plain, bookOf([plain], { edit: withPages })), /O8: core\/review\.md is the part's review page: it carries "generated: review"/);
	const outline = indexOutline((() => { const data = testOutline({ 'core/time': frontmatter() }); withPages(data); return data; })());
	assert.match(partPagesProblems(outline, new Map()).join('\n'), /O8: the part "core" has 1 rows, so a release has src\/content\/docs\/core\/index\.md[\s\S]*core\/review\.md/);
	assert.deepEqual(partPagesProblems(outline, new Map([['core/index', {}], ['core/review', {}]])), []);
	// The whole book: an index page without its review page fails.
	const book = makeBook({
		pages: { 'core/time': `${frontmatter()}\nText.\n${c_BottomStrip}`, 'core/index': '---\ntitle: "Engine architecture"\ndescription: "The part."\ntracks: [E]\nstatus: draft\ngenerated: index\n---\n\nThe part.\n' },
		outline: withPages,
	});
	try {
		const settings = readSettings({ root: book.root, env: { DOCS_SITE: 'https://example.com' } });
		const found = (await bookProblems(createBookContext(settings))).join('\n');
		assert.match(found, /O8: the part "core" has src\/content\/docs\/core\/index\.md but not its review page/);
		assert.doesNotMatch(found, /not listed/);
	} finally {
		book.remove();
	}
});

test('the landing and 404 pages carry only a title and a description of the book\'s keys', () => {
	const landing = { id: 'index', error: null, data: { title: 'Home', description: 'The book.', template: 'splash', kind: 'concept', status: 'draft' } };
	assert.match(problemsOf(landing, bookOf([chapter('core/time')])), /the landing page carries only "title" and "description" of the book's keys, not "kind", "status"/);
	const notFound = { id: '404', error: null, data: { title: 'Not found', description: 'Nothing here.', template: 'splash', hero: { title: 'x' } } };
	assert.deepEqual(checkFrontmatter(notFound, bookOf([chapter('core/time')])), []);
});

test('the build reports front matter problems with the rule and the field named', async () => {
	const page = `${frontmatter({ kind: 'essay', tracks: '[players]', needs: '[core/gone]', since: undefined })}\nText.\n${c_BottomStrip}`;
	// The outline's row has a real kind (the test outline copies the page's).
	const book = makeBook({ pages: { 'core/time': page }, outline: (data) => { data.pages[0].kind = 'concept'; } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /front matter: "kind" must be one of/, /"tracks" holds "players"/, /O2: the Need "core\/gone" is no row of the outline/, /O7: "kind" is "essay"; its row \(plan\/outline-test\.md:1\) says "concept"/);
	} finally {
		book.remove();
	}
	const cycle = makeBook({
		pages: {
			'core/a': `${frontmatter({ tracks: '[]', needs: '[core/b]' })}\nA.\n${c_BottomStrip}`,
			'core/b': `${frontmatter({ tracks: '[]', needs: '[core/a]' })}\nB.\n${c_BottomStrip}`,
		},
	});
	try {
		await rejectsWith(render(cycle.root, 'core/b'), /O6: the Needs form a cycle: core\/a → core\/b → core\/a/);
	} finally {
		cycle.remove();
	}
});

test('each kind has its bottom strip, one Summary item per objective, and answers that name what they test', async () => {
	const uses = '- [Counting](../core/count.md) counts with them.\n- [Sums](../core/sum.md) adds them.\n- [Either](../core/either.md) reads them.\n';
	const book = makeBook({
		pages: {
			'basics/numbers': `${frontmatter({ kind: 'primer', tracks: '[B, E]', since: undefined })}\n${primerBody(uses)}`,
			'basics/bytes': `${frontmatter({ kind: 'primer', tracks: '[B, E]', since: undefined })}\nText.\n${c_BottomStrip}`,
			'reference/commands': `${frontmatter({ kind: 'reference', tracks: '[]' })}\nThe table.\n${c_ReferenceStrip}`,
			'core/time': `${frontmatter()}\nText.\n${c_BottomStrip.replace('- Another line.\n', '').replace(':::answer{tests="another-thing"}', ':::answer').replace(':::answer{tests="one-thing another-thing"}', ':::answer{tests="one-thing, missing" note="x"}')}`,
			// The pages that use the primer: through a Need, through a Need's Need, and through one alternative of "a|b".
			'core/count': `${frontmatter({ needs: '[basics/numbers]' })}\nText.\n${c_BottomStrip}`,
			'core/sum': `${frontmatter({ needs: '[core/count]' })}\nText.\n${c_BottomStrip}`,
			'core/either': `${frontmatter({ needs: '[basics/bytes|basics/numbers]' })}\nText.\n${c_BottomStrip}`,
		},
	});
	try {
		await render(book.root, 'basics/numbers');
		await render(book.root, 'reference/commands');
		await rejectsWith(render(book.root, 'basics/bytes'), /P1: a primer page ends with the sections "## Summary", "## Check yourself", "## Practice", "## Where the book uses it", "## Further reading", in this order/, /missing: "## Practice", "## Where the book uses it"/);
		const error = await rejectsWith(
			render(book.root, 'core/time'),
			/P1: "## Summary" holds 1 bulleted items; it holds one per objective of "learn" \(2\), in their order/,
			/an answer under "## Check yourself" names the objectives it tests: :::answer\{tests="<learn ids>"\}/,
			/P2: tests="missing" is not an objective of the page \(its learn ids: one-thing, another-thing\)/,
			/P2: the objective "another-thing" is in the tests of no answer under "## Check yourself"/,
			/:::answer has no attribute "note" \(it takes tests, solution\)/,
		);
		assert.doesNotMatch(error.message, /tests="one-thing"/);
	} finally {
		book.remove();
	}
	const empty = makeBook({ pages: { 'core/time': `${frontmatter()}\nA try-it.\n\n:::answer{tests="" solution=""}\nYes.\n:::\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(empty.root, 'core/time'), /:::answer\{tests=""\} names no objective/, /:::answer\{solution=""\} names no file/);
	} finally {
		empty.remove();
	}
});

test('the first word of a learn line is read without the comma after it, as tools/pages.py reads it', () => {
	const learn = [{ id: 'scenes', text: 'create, save and open scenes' }, { id: 'walls', text: 'build the walls' }];
	const page = chapter('core/time', { learn });
	assert.doesNotMatch(problemsOf(page, bookOf([page])), /starts with/);
});

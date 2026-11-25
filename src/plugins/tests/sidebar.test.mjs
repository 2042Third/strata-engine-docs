// The outline's data and the Needs closure (src/lib/outline.mjs), the sidebar and the tracks (src/lib/sidebar.mjs), the
// top strip (src/lib/strip.mjs) and the track links (src/lib/pagination.mjs). Every URL they write is checked at the
// three bases.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { checkOutlineShape, closureNeeds, indexOutline, needsClosure, trackOrder, trackSideSteps } from '../../lib/outline.mjs';
import { trackLinks, writtenPages } from '../../lib/pagination.mjs';
import { parsePin } from '../../lib/settings.mjs';
import { checkSidebarOutline, checkSidebarPages, checkSidebarShape, routeIdOf, starlightSidebar, trackNeighbours, tracksHolding } from '../../lib/sidebar.mjs';
import { topStrip } from '../../lib/strip.mjs';
import { c_Parts, c_Pin, testSidebar } from './helpers.mjs';

const c_Bases = [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']];

const row = (id, title, kind, tracks, needs, level = 1) => ({ id, title, kind, size: 'M', tracks, needs, part: id.split('/')[0], level, row: `plan/outline-test.md:${id}` });

/** A small outline: four pages of start, two of make (with a side step of track G), three of core, one of audio. */
function outlineData() {
	const rows = [
		row('start/welcome', 'Welcome', 'concept', ['G', 'B', 'E'], []),
		row('start/how-to-read', 'How to read', 'how-to', ['G', 'B', 'E'], []),
		row('start/install', 'Install', 'how-to', ['G', 'B', 'E'], []),
		row('start/coming-from', 'Coming from', 'concept', ['G', 'E'], []),
		row('make/lighting', 'Lighting', 'how-to', ['G', 'B'], ['start/install']),
		row('make/first-script', 'First script', 'tutorial', ['G', 'B'], ['make/lighting', 'basics/tools|start/install']),
		row('basics/tools', 'The tools', 'primer', ['B', 'E'], ['start/install']),
		row('core/map', 'Map', 'concept', ['E'], [], 2),
		row('core/frame-loop', 'Frame loop', 'internals', ['E'], ['core/map'], 2),
		row('core/time', 'Time', 'concept', ['E'], ['core/frame-loop', 'basics/tools'], 2),
		row('audio/why', 'Why audio', 'concept', ['E'], ['core/time'], 3),
		row('audio/mixer', 'The mixer', 'internals', ['E'], [], 3),
	];
	const parts = c_Parts.map(([slug, title], number) => {
		const own = rows.filter((item) => item.part === slug);
		return { number, slug, title, tracks: ['G', 'B', 'E'].filter((letter) => own.some((item) => item.tracks.includes(letter))), needs: [], pages: own.map((item) => item.id), partPages: false };
	});
	parts.find((part) => part.slug === 'core').partPages = true;
	parts.find((part) => part.slug === 'audio').needs = ['core/time', 'core/map|start/welcome'];
	const ids = (...list) => list.map((id) => (id.startsWith('~') ? { id: id.slice(1), sideStep: true } : { id }));
	return {
		generated: 'test',
		parts,
		pages: rows,
		tracks: {
			G: ids('start/welcome', 'start/how-to-read', 'start/install', 'start/coming-from', 'make/lighting', '~basics/tools', 'make/first-script'),
			B: ids('start/welcome', 'start/how-to-read', 'start/install', 'make/lighting', 'basics/tools', 'make/first-script'),
			E: ids('start/welcome', 'start/how-to-read', 'start/install', 'start/coming-from', 'basics/tools', 'core/map', 'core/frame-loop', 'core/time', 'audio/why', 'audio/mixer'),
		},
	};
}

/** Written pages as the components see them: book id → `{ title, route }`. */
function written(...ids) {
	const outline = indexOutline(outlineData());
	return new Map(ids.map((id) => [id, { title: outline.rows.get(id)?.title ?? `Part page ${id}`, route: routeIdOf(id) }]));
}

test('the outline\'s data is read with its shape checked', () => {
	const data = outlineData();
	const outline = indexOutline(data);
	// Every page's components index the one imported object: it is checked and indexed once.
	assert.equal(indexOutline(data), outline);
	assert.equal(outline.parts.length, 25);
	assert.equal(outline.rows.get('core/time').title, 'Time');
	assert.deepEqual(trackOrder(outline, 'G'), ['start/welcome', 'start/how-to-read', 'start/install', 'start/coming-from', 'make/lighting', 'make/first-script']);
	assert.deepEqual(trackSideSteps(outline, 'G'), [{ id: 'basics/tools', before: 'make/first-script' }]);
	assert.deepEqual(trackSideSteps(outline, 'E'), []);
	const broken = outlineData();
	broken.parts[2].number = 7;
	broken.pages[0].kind = 'essay';
	broken.pages[1].needs = ['start/welcome|Bad Id'];
	broken.pages[2].level = 4;
	broken.pages[3].part = 'make';
	broken.tracks.G.push({ id: 'nowhere' });
	broken.tracks.B[0].sideStep = 'yes';
	broken.parts[0].pages.push('start/missing');
	const problems = checkOutlineShape(broken).join('\n');
	assert.match(problems, /parts\[2\]: "number" is 7, not 2/);
	assert.match(problems, /pages\[0\] \(start\/welcome\): "kind" is not one of primer, concept/);
	assert.match(problems, /pages\[1\] \(start\/how-to-read\): "needs" holds "start\/welcome\|Bad Id"/);
	assert.match(problems, /pages\[2\] \(start\/install\): "level" is not 1, 2 or 3/);
	assert.match(problems, /pages\[3\] \(start\/coming-from\): "part" is not the part its id starts with/);
	assert.match(problems, /tracks\.G\[7\]: "id" is not a row of the outline/);
	assert.match(problems, /tracks\.B\[0\]: "sideStep" is true or absent/);
	assert.match(problems, /parts \(start\): "start\/missing" is not one of "pages"/);
	assert.throws(() => indexOutline(broken, 'outline.json'), /outline\.json:\n {2}parts\[2\][\s\S]*tools\/pages\.py outline --write/);
	assert.deepEqual(checkOutlineShape([]), ['the file is not a JSON object']);
});

test('the Needs closure follows every alternative and the "-" rows of a part', () => {
	const outline = indexOutline(outlineData());
	// core/time needs core/frame-loop and basics/tools; core/frame-loop needs core/map; basics/tools needs start/install,
	// whose row has "-": it needs start/welcome, the first page of its part.
	assert.deepEqual([...needsClosure(outline, 'core/time')].sort(), ['basics/tools', 'core/frame-loop', 'core/map', 'start/install', 'start/welcome']);
	// "basics/tools|start/install": both alternatives are followed.
	assert.deepEqual([...needsClosure(outline, 'make/first-script')].sort(), ['basics/tools', 'make/lighting', 'start/install', 'start/welcome']);
	// Each alternative is followed, also one reached no other way.
	const either = outlineData();
	either.pages.find((row) => row.id === 'core/map').needs = ['start/welcome|start/coming-from'];
	assert.deepEqual([...needsClosure(indexOutline(either), 'core/map')].sort(), ['start/coming-from', 'start/welcome']);
	// audio/mixer's row has "-": it needs audio/why, the first page of its part, and all that page needs.
	assert.deepEqual(closureNeeds(outline, 'audio/mixer'), ['audio/why']);
	assert.ok(needsClosure(outline, 'audio/mixer').has('core/map'));
	// The first page of a part with "-" needs nothing, and no page is in its own closure, even through a cycle.
	assert.deepEqual([...needsClosure(outline, 'start/welcome')], []);
	const cycle = outlineData();
	cycle.pages.find((row) => row.id === 'core/map').needs = ['core/time'];
	assert.deepEqual([...needsClosure(indexOutline(cycle), 'core/map')].sort(), ['basics/tools', 'core/frame-loop', 'core/time', 'start/install', 'start/welcome']);
	assert.deepEqual([...needsClosure(outline, 'start/install')], ['start/welcome']);
	assert.deepEqual([...needsClosure(outline, 'nowhere/page')], []);
});

test('the Needs closure gives every row of the outline the level tools/pages.py wrote for it', () => {
	// src/generated/outline.json's levels come from tools/booklib/outline.py's closure; the build's closure (for "Where
	// the book uses it") must be the same, so the levels it gives (style.md §6.2) are compared row by row.
	const data = JSON.parse(readFileSync(new URL('../../generated/outline.json', import.meta.url), 'utf8'));
	const outline = indexOutline(data);
	const numbers = new Map(outline.parts.map((part) => [part.slug, part.number]));
	const levelOf = (row) => {
		const parts = [...needsClosure(outline, row.id)].map((id) => outline.rows.get(id).part);
		if (parts.every((slug) => numbers.get(slug) <= 2)) return 1;
		if (parts.some((slug) => numbers.get(slug) >= 6 && slug !== row.part)) return 3;
		return 2;
	};
	const differ = data.pages.filter((row) => levelOf(row) !== row.level).map((row) => `${row.id}: ${levelOf(row)}, the file says ${row.level}`);
	assert.deepEqual(differ, []);
	// The comparison means something only when the outline has pages of every level.
	assert.deepEqual([...new Set(data.pages.map((row) => row.level))].sort(), [1, 2, 3]);
});

test('the sidebar\'s shape: its keys, the three tracks and their side steps', () => {
	const outline = indexOutline(outlineData());
	const sidebar = testSidebar(outline, new Set(['start/install']));
	assert.deepEqual(checkSidebarShape(sidebar), []);
	const broken = structuredClone(sidebar);
	broken.extra = 1;
	broken.parts[0].filter = 'game';
	delete broken.tracks.beginner;
	broken.tracks.all = broken.tracks.game;
	delete broken.tracks.engine.sideSteps;
	broken.tracks.game.sequence.push(3);
	const problems = checkSidebarShape(broken).join('\n');
	assert.match(problems, /"extra" is not a key of the sidebar/);
	assert.match(problems, /parts\[0\]: "filter" is not a key of a part/);
	assert.match(problems, /tracks\.beginner is missing/);
	assert.match(problems, /tracks: "all" is not a track \(game, beginner, engine\)/);
	assert.match(problems, /tracks\.engine: "sideSteps" must be a list/);
	assert.match(problems, /tracks\.game: "sequence" must be the track's reading order/);
});

test('O9 and O5: the sidebar lists the outline\'s parts in order and the tracks of plan/tracks.md', () => {
	const outline = indexOutline(outlineData());
	const sidebar = testSidebar(outline, new Set());
	assert.deepEqual(checkSidebarOutline(sidebar, outline), []);
	const broken = structuredClone(sidebar);
	[broken.parts[5], broken.parts[6]] = [broken.parts[6], broken.parts[5]];
	broken.parts[3].label = 'The core';
	broken.tracks.engine.sequence.splice(1, 1);
	broken.tracks.game.sequence.push('start/welcome');
	broken.tracks.game.sideSteps = [];
	const problems = checkSidebarOutline(broken, outline).join('\n');
	assert.match(problems, /part 5 is "assets"; the book's part 5 is "gpu"/);
	assert.match(problems, /part "core" is labelled "The core"; the outline calls it "Engine architecture"/);
	assert.match(problems, /track "engine" \(E\): its sequence differs from plan\/tracks\.md: entry 2 is "start\/install", the outline's is "start\/how-to-read"/);
	assert.match(problems, /track "game" lists "start\/welcome" twice/);
	assert.match(problems, /track "game" \(G\): its side steps are \[\]; plan\/tracks\.md gives \[\{"id":"basics\/tools","before":"make\/first-script"\}\]/);
	const short = structuredClone(sidebar);
	short.parts.pop();
	assert.match(checkSidebarOutline(short, outline).join('\n'), /lists 24 parts; the book has 25/);
	const reserved = structuredClone(sidebar);
	reserved.parts[0].slug = 'print';
	assert.match(checkSidebarOutline(reserved, outline).join('\n'), /part "print": "print" is reserved/);
});

test('every written page is listed once, in its part, in the order of the rows with the index first and the review last', () => {
	const outline = indexOutline(outlineData());
	const pages = new Map(['core/index', 'core/map', 'core/time', 'core/review', 'start/install'].map((id) => [id, { relative: `${id}.md` }]));
	const sidebar = testSidebar(outline, new Set(pages.keys()));
	assert.deepEqual(sidebar.parts[3].pages, ['core/index', 'core/map', 'core/time', 'core/review']);
	assert.deepEqual(checkSidebarPages(sidebar, outline, pages), []);
	const broken = structuredClone(sidebar);
	broken.parts[3].pages = ['core/time', 'core/review', 'core/map', 'start/install', 'core/gone'];
	broken.parts[0].pages.push('start/install');
	const problems = checkSidebarPages(broken, outline, pages).join('\n');
	assert.match(problems, /part "core" lists "core\/map" after "core\/review", against the order of the outline's rows/);
	assert.match(problems, /part "core" lists "start\/install", a page of another part/);
	assert.match(problems, /lists "start\/install" twice/);
	assert.match(problems, /lists "core\/gone", which is not a page/);
	assert.match(problems, /core\/index\.md is not listed in src\/sidebar\.json \(part "core"\)/);
	// Starlight serves a part's index page at <base>/<part>/: the sidebar names it by that route; empty parts are left out.
	assert.deepEqual(starlightSidebar(sidebar), [
		{ label: 'Start here', collapsed: true, items: ['start/install'] },
		{ label: 'Engine architecture', collapsed: true, items: ['core', 'core/map', 'core/time', 'core/review'] },
	]);
});

test('previous and next of a track pass over pages not written yet and over side steps', () => {
	const outline = indexOutline(outlineData());
	const pages = written('start/welcome', 'start/install', 'make/lighting', 'make/first-script', 'basics/tools', 'core/time');
	const sidebar = testSidebar(outline, new Set(pages.keys()));
	const around = (id) => Object.fromEntries(trackNeighbours(sidebar, pages, id).map((track) => [track.key, [track.prev, track.next, track.sideStep]]));
	// start/how-to-read and start/coming-from are not written: install's neighbours skip them.
	assert.deepEqual(around('start/install'), { game: ['start/welcome', 'make/lighting', false], beginner: ['start/welcome', 'make/lighting', false], engine: ['start/welcome', 'basics/tools', false] });
	// Track G's next of make/lighting passes over its side step basics/tools.
	assert.deepEqual(around('make/lighting').game, ['start/install', 'make/first-script', false]);
	// On the side step itself, track G leads back to make/lighting and on to make/first-script.
	assert.deepEqual(around('basics/tools'), { game: ['make/lighting', 'make/first-script', true], beginner: ['make/lighting', 'make/first-script', false], engine: ['start/install', 'core/time', false] });
	assert.deepEqual(around('core/time'), { engine: ['basics/tools', null, false] });
	assert.deepEqual(around('start/welcome').game, [null, 'start/install', false]);
	assert.deepEqual(tracksHolding(sidebar, 'basics/tools'), ['B', 'E']);
	assert.deepEqual(tracksHolding(sidebar, 'make/first-script'), ['G', 'B']);
});

for (const [setting, base] of c_Bases) {
	test(`the top strip's links and files are under the base ${setting}`, () => {
		const outline = indexOutline(outlineData());
		const pin = parsePin(c_Pin);
		const pages = written('start/welcome', 'start/install', 'make/lighting', 'make/first-script', 'core/index', 'core/time', 'audio/why', 'audio/mixer');
		const strip = (data) => topStrip({ data, outline, pages, base, pin });
		const time = strip({ id: 'core/time', title: 'Time', kind: 'concept', tracks: ['E'], needs: ['core/frame-loop', 'basics/tools'], time: 45, learn: [{ id: 'a', text: 'explain a' }, { id: 'b', text: 'compute b' }], since: '0.8.0', status: 'draft' });
		assert.deepEqual(time.breadcrumbs, [
			{ label: 'The Strata Engine Book', href: `${base}/` },
			{ label: 'Engine architecture', href: `${base}/core/` },
			{ label: 'Time', href: null },
		]);
		assert.deepEqual(time.kind, { word: 'concept', label: 'Concept' });
		assert.deepEqual(time.tracks, [{ letter: 'E', key: 'engine', name: 'Engine builder' }]);
		assert.deepEqual(time.level, { number: 2, text: "Level 2: also needs the engine's core (parts 3 to 5) or earlier pages of this part." });
		assert.equal(time.minutes, 45);
		assert.equal(time.newIn, '0.8.0');
		assert.equal(time.draft, true);
		assert.deepEqual(time.learn, ['explain a', 'compute b']);
		// Needs not written yet are named by their outline title, without a link.
		assert.deepEqual(time.needs, [
			{ need: 'core/frame-loop', alternatives: [{ id: 'core/frame-loop', title: 'Frame loop', href: null, written: false }] },
			{ need: 'basics/tools', alternatives: [{ id: 'basics/tools', title: 'The tools', href: null, written: false }] },
		]);
		assert.equal(time.beforePart, null);
		assert.deepEqual(time.engine, { release: '0.8.0', prerelease: true, commit: '822a7a46dbcdd86e8e2eafde7e41d003e27260c8', short: '822a7a46', href: 'https://github.com/2042Third/GameEngine/tree/822a7a46dbcdd86e8e2eafde7e41d003e27260c8' });
		assert.deepEqual(time.print, { href: `${base}/print/core/`, label: 'Engine architecture' });
		// An alternative shows as "X or Y", each written one a link.
		const script = strip({ id: 'make/first-script', title: 'First script', kind: 'tutorial', tracks: ['G', 'B'], needs: ['make/lighting', 'basics/tools|start/install'], since: '0.3.0', status: 'reviewed' });
		assert.deepEqual(script.needs[1].alternatives.map((ref) => ref.href), [null, `${base}/start/install/`]);
		assert.equal(script.needs[0].alternatives[0].href, `${base}/make/lighting/`);
		assert.equal(script.newIn, null);
		assert.equal(script.draft, false);
		assert.deepEqual(script.tracks.map((track) => track.name), ['Game maker', 'Beginner']);
		assert.equal(script.breadcrumbs[1].href, `${base}/make/lighting/`);
		// "needs: []" shows the part's first page; the first page itself needs nothing.
		const mixer = strip({ id: 'audio/mixer', title: 'The mixer', kind: 'internals', tracks: ['E'], needs: [], status: 'draft' });
		assert.equal(mixer.needsFirstPage, true);
		assert.deepEqual(mixer.needs[0].alternatives[0], { id: 'audio/why', title: 'Why audio', href: `${base}/audio/why/`, written: true });
		assert.equal(mixer.level.number, 3);
		const welcome = strip({ id: 'start/welcome', title: 'Welcome', kind: 'concept', tracks: ['G', 'B', 'E'], needs: [], status: 'draft' });
		assert.deepEqual(welcome.needs, []);
		assert.equal(welcome.needsFirstPage, false);
		// The first page of a part without part pages shows the part's Needs as "Before this part".
		const why = strip({ id: 'audio/why', title: 'Why audio', kind: 'concept', tracks: ['E'], needs: ['core/time'], status: 'draft' });
		assert.deepEqual(why.beforePart.map((need) => need.alternatives.map((ref) => ref.href)), [[`${base}/core/time/`], [null, `${base}/start/welcome/`]]);
		// A part's index page has no kind, level, time or objectives; core has an index, so its first page has no
		// "Before this part".
		const index = strip({ id: 'core/index', title: 'Engine architecture', tracks: ['E'], status: 'draft', generated: 'index' });
		assert.equal(index.kind, null);
		assert.equal(index.level, null);
		assert.equal(index.needs, null);
		assert.equal(index.print.href, `${base}/print/core/`);
		assert.equal(strip({ title: 'Home' }), null);
		const hrefs = [time, script, mixer, why, index].flatMap((one) => [
			...one.breadcrumbs.map((crumb) => crumb.href),
			...[...(one.needs ?? []), ...(one.beforePart ?? [])].flatMap((need) => need.alternatives.map((ref) => ref.href)),
			one.print.href,
		]).filter(Boolean);
		for (const href of hrefs) {
			assert.ok(href.startsWith(`${base}/`), `${href} is not under ${base}/`);
			if (base !== '/strata-engine-docs') assert.ok(!href.startsWith('/strata-engine-docs/'), `${href} names the default prefix`);
		}
	});

	test(`the track links are under the base ${setting}`, () => {
		const outline = indexOutline(outlineData());
		const entries = [
			{ id: 'start/how-to-read', data: { id: 'start/how-to-read', title: 'How to read' } },
			{ id: 'start/install', data: { id: 'start/install', title: 'Install' } },
			{ id: 'make/lighting', data: { id: 'make/lighting', title: 'Lighting' } },
			{ id: 'core', data: { id: 'core/index', title: 'Engine architecture' } },
			{ id: 'index', data: { title: 'Home' } },
		];
		const pages = writtenPages(entries);
		assert.deepEqual([...pages.keys()], ['start/how-to-read', 'start/install', 'make/lighting', 'core/index']);
		assert.deepEqual(pages.get('core/index'), { title: 'Engine architecture', route: 'core' });
		const sidebar = testSidebar(outline, new Set(pages.keys()));
		const { tracks, chooser } = trackLinks({ sidebar, pages, id: 'start/install', base });
		assert.deepEqual(chooser, { href: `${base}/start/how-to-read/`, title: 'How to read' });
		const game = tracks.find((track) => track.key === 'game');
		assert.deepEqual(game.prev, { href: `${base}/start/how-to-read/`, title: 'How to read' });
		assert.deepEqual(game.next, { href: `${base}/make/lighting/`, title: 'Lighting' });
		assert.equal(tracks.find((track) => track.key === 'engine').next, null);
		for (const link of tracks.flatMap((track) => [track.prev, track.next]).filter(Boolean).concat([chooser])) {
			assert.ok(link.href.startsWith(`${base}/`), `${link.href} is not under ${base}/`);
		}
		assert.equal(trackLinks({ sidebar, pages: new Map([['make/lighting', { title: 'Lighting', route: 'make/lighting' }]]), id: 'make/lighting', base }).chooser, null);
	});
}

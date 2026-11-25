// The generated parts of a part's index and review pages (plan/site.md, "Navigation"; plan/style.md §7.7): the build
// draws them from the outline's data and the written pages, around the part editor's text.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { loadOutline } from '../../lib/outline.mjs';
import { c_IndexHeadings, c_ReviewHeading, needsGraphSource, primerFirstParts, relativeLink } from '../../lib/partpages.mjs';
import { c_BottomStrip, committedDiagram, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

/** Writes files (path relative to the book → content) into a test book made already. */
function writeFiles(root, files) {
	for (const [relative, content] of Object.entries(files)) {
		const file = path.join(root, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	}
}

const partPage = (generated, body) => `---\nid: core/${generated}\ntitle: "${generated === 'index' ? 'Engine architecture' : 'Review: engine architecture'}"\ndescription: "The part's ${generated} page."\ntracks: [E]\nstatus: draft\ngenerated: ${generated}\n---\n\n${body}\n`;
const chapter = (title, needs, extra = '') => `${frontmatter({ title: `"${title}"`, needs })}\nText of ${title}.${extra}\n${c_BottomStrip}`;

/** A book whose part "core" has part pages: four rows, three written, one with a figure in its questions. */
function partBook({ index = 'This part shows how the engine is put together.', review = '## Cumulative exercises\n\n1. **Basic.** Trace a frame.\n\n   :::answer[Worked solution]\n   Start at the loop.\n   :::', extraPages = {}, files = {} } = {}) {
	const timeQuestions = c_BottomStrip.replace('1. One?', '1. One? See [the accumulator](#the-accumulator).');
	const book = makeBook({
		pages: {
			'core/index': partPage('index', index),
			'core/frame-loop': chapter('The frame loop', '[]', '\n\n## The loop\n\nText.'),
			'core/time': `${frontmatter({ title: '"Time"', needs: '[core/frame-loop]' })}\n## The accumulator\n\nText.\n${timeQuestions}`,
			'core/jobs': chapter('Jobs', '[core/frame-loop|core/time]'),
			'core/review': partPage('review', review),
			'world/ecs': chapter('The ECS', '[core/time]', '\n\nSee [the map](../core/index.md#the-map-of-this-part) and [the questions of Time](../core/review.md#time).'),
			...extraPages,
		},
		outline: (data) => {
			const core = data.parts.find((part) => part.slug === 'core');
			core.partPages = true;
			// A row that is not written yet, and a Need of the part outside it.
			data.pages.push({ id: 'core/files', title: 'Files', kind: 'concept', size: 'M', tracks: ['E'], needs: [], part: 'core', level: 2, row: 'plan/outline-test.md:99' });
			core.pages.push('core/files');
			core.needs = ['basics/numbers|basics/bytes'];
			data.pages.push({ id: 'basics/numbers', title: 'Numbers', kind: 'primer', size: 'M', tracks: ['E'], needs: [], part: 'basics', level: 1, row: 'plan/outline-test.md:100' });
			data.parts.find((part) => part.slug === 'basics').pages.push('basics/numbers');
		},
		files,
	});
	// The Needs graph is a diagram: its drawings are committed, as npm run diagrams writes them.
	const outline = loadOutline(path.join(book.root, 'src', 'generated', 'outline.json'));
	const source = needsGraphSource(outline, outline.partBySlug.get('core'));
	writeFiles(book.root, committedDiagram(source).files);
	return { ...book, source };
}

test('the Needs graph: a box per row, an arrow from each Need inside the part, dotted for one of two alternatives', () => {
	const book = partBook();
	try {
		assert.equal(book.source, [
			'flowchart TB',
			'    p0["The frame loop"]',
			'    p1["Time"]',
			'    p2["Jobs"]',
			'    p3["Files"]',
			'    p0 --> p1',
			'    p0 -.-> p2',
			'    p1 -.-> p2',
			// "Files" has the Needs "-": it needs the part's first row (style.md §1.2).
			'    p0 --> p3',
		].join('\n'));
	} finally {
		book.remove();
	}
});

test('the index page holds the editor\'s paragraph, then the map, the Needs outside the part and what the reader can do after it', async () => {
	const book = partBook();
	try {
		const out = await render(book.root, 'core/index');
		assert.ok(out.startsWith('<p>This part shows how the engine is put together.</p>\n<h2>The map of this part</h2>'), out.slice(0, 200));
		// The diagram, with its caption and alternative text, and the same graph as a list.
		assert.match(out, /<figure class="book-diagram"><div class="book-diagram__svg book-diagram__svg--light"><svg role="img" aria-label="A graph of the 4 pages of the part “Engine architecture”\. Each page is a box/);
		assert.match(out, /<figcaption>Each page of this part with the pages of the part it needs/);
		assert.match(out, /<ol>\n<li><a href="\/book\/core\/frame-loop\/">The frame loop<\/a><\/li>\n<li><a href="\/book\/core\/time\/">Time<\/a>: needs <a href="\/book\/core\/frame-loop\/">The frame loop<\/a><\/li>\n<li><a href="\/book\/core\/jobs\/">Jobs<\/a>: needs <a href="\/book\/core\/frame-loop\/">The frame loop<\/a> or <a href="\/book\/core\/time\/">Time<\/a><\/li>\n<li><em>Files \(not written yet\)<\/em>: needs <a href="\/book\/core\/frame-loop\/">The frame loop<\/a><\/li>\n<\/ol>/);
		assert.match(out, /<h2>Before this part<\/h2>\n<p>The pages of this part need these pages of other parts:<\/p>\n<ul>\n<li><em>Numbers \(not written yet\)<\/em> or <em>basics\/bytes \(not written yet\)<\/em><\/li>\n<\/ul>/);
		assert.match(out, /<h2>After this part you can<\/h2>\n<p>Each page of the part says what you can do after it:<\/p>\n<ul>\n<li><a href="\/book\/core\/frame-loop\/">The frame loop<\/a>\n<ul>\n<li>explain one thing<\/li>\n<li>explain another thing<\/li>\n<\/ul>\n<\/li>/);
		assert.match(out, /<p>1 of the part's 4 pages is not written yet\.<\/p>/);
		assert.doesNotMatch(out, /Where each primer is first needed/);
	} finally {
		book.remove();
	}
});

test('the index of a part on no track, the reference, shows no "Before this part" (rulings 7, D9)', async () => {
	const book = partBook();
	try {
		const outlineFile = path.join(book.root, 'src', 'generated', 'outline.json');
		const data = JSON.parse(readFileSync(outlineFile, 'utf8'));
		data.parts.find((part) => part.slug === 'core').tracks = [];
		writeFileSync(outlineFile, JSON.stringify(data));
		// A part page's tracks are its part's.
		for (const name of ['index', 'review']) {
			const file = path.join(book.root, 'src', 'content', 'docs', 'core', `${name}.md`);
			writeFileSync(file, readFileSync(file, 'utf8').replace('tracks: [E]', 'tracks: []'));
		}
		const out = await render(book.root, 'core/index');
		assert.match(out, /<h2>The map of this part<\/h2>/);
		assert.doesNotMatch(out, /Before this part|need these pages of other parts/);
		assert.match(out, /<h2>After this part you can<\/h2>/);
	} finally {
		book.remove();
	}
});

test('the review page holds every "Check yourself" question of the part, by page, then the editor\'s exercises', async () => {
	const book = partBook();
	try {
		const out = await render(book.root, 'core/review');
		assert.ok(out.startsWith(`<h2>${c_ReviewHeading}</h2>`), out.slice(0, 120));
		assert.match(out, /<h3>The frame loop<\/h3>\n<p>From <a href="\/book\/core\/frame-loop\/">The frame loop<\/a>\.<\/p>\n<ol data-pagefind-ignore="">\n<li>\n<p>One\?<\/p>\n<details class="book-answer">/);
		// The copies stay out of the search index (budget row 12); every question is indexed on its own page.
		assert.equal((out.match(/<ol data-pagefind-ignore="">/g) ?? []).length, 3);
		// A link within the page a question comes from leads to that page.
		assert.match(out, /<h3>Time<\/h3>[\s\S]*?One\? See <a href="\/book\/core\/time\/#the-accumulator">the accumulator<\/a>/);
		assert.match(out, /<h3>Jobs<\/h3>/);
		assert.doesNotMatch(out, /<h3>Files<\/h3>/);
		// The editor's exercises come last.
		assert.match(out, /<h2>Cumulative exercises<\/h2>\n<ol>\n<li>\n<p><strong>Basic\.<\/strong> Trace a frame\.<\/p>\n<details class="book-answer"><summary>Worked solution<\/summary>/);
		assert.ok(out.indexOf('<h3>Jobs</h3>') < out.indexOf('<h2>Cumulative exercises</h2>'));
	} finally {
		book.remove();
	}
});

test('links to the generated headings of part pages are checked like any other', async () => {
	const book = partBook();
	try {
		const out = await render(book.root, 'world/ecs');
		assert.match(out, /href="\/book\/core\/#the-map-of-this-part"/);
		assert.match(out, /href="\/book\/core\/review\/#time"/);
	} finally {
		book.remove();
	}
	const wrong = partBook({ extraPages: { 'world/ecs': chapter('The ECS', '[core/time]', '\n\nSee [nothing](../core/review.md#files).') } });
	try {
		await rejectsWith(render(wrong.root, 'world/ecs'), /the page core\/review has no heading or figure with the anchor "files"/);
	} finally {
		wrong.remove();
	}
});

test('a question with a picture keeps its own page\'s figure manifest on the review page', async () => {
	const recipe = { id: 'shot', shows: 'A cube.', kind: 'scene', caption: 'Notice the cube.', alt: 'A grey cube.', size: [1920, 1080] };
	const withFigure = `${frontmatter({ title: '"Time"', needs: '[core/frame-loop]' })}\n## The accumulator\n\nText.\n${c_BottomStrip.replace('1. One?', '1. One?\n\n   ::figure{id=shot}')}`;
	const book = partBook({ extraPages: { 'core/time': withFigure }, files: { 'src/content/figures/core/time.json': JSON.stringify({ figures: [recipe] }) } });
	try {
		const out = await render(book.root, 'core/review');
		assert.match(out, /<figure class="book-figure" id="fig-shot"><div class="book-placeholder" role="img" aria-label="A grey cube\."/);
	} finally {
		book.remove();
	}
});

test('a problem in a copied question names the page it comes from', async () => {
	const broken = `${frontmatter({ title: '"Time"', needs: '[core/frame-loop]' })}\n## The accumulator\n\nText.\n${c_BottomStrip.replace('1. One?', '1. One? :term[thing]{id=nothing}')}`;
	const book = partBook({ extraPages: { 'core/time': broken } });
	try {
		const error = await rejectsWith(render(book.root, 'core/review'), /core\/review\.md:1:1: :term\{id=nothing\}: the glossary has no entry "nothing" \(from src\/content\/docs\/core\/time\.md:\d+:\d+\)/);
		assert.match(error.message, /has 1 problem/);
	} finally {
		book.remove();
	}
});

test('the index of basics names the first part that needs each primer', async () => {
	const book = makeBook({
		pages: {
			'basics/index': `---\nid: basics/index\ntitle: "Foundations"\ndescription: "The part's index page."\ntracks: [E]\nstatus: draft\ngenerated: index\n---\n\nThe primers.\n`,
			'basics/numbers': `${frontmatter({ title: '"Numbers"', since: undefined })}\nText.\n${c_BottomStrip}`,
			'basics/bytes': `${frontmatter({ title: '"Bytes"', since: undefined })}\nText.\n${c_BottomStrip}`,
			'core/time': chapter('Time', '[basics/numbers]'),
			'world/ecs': chapter('The ECS', '[core/time]'),
		},
		outline: (data) => {
			data.parts.find((part) => part.slug === 'basics').partPages = true;
			for (const row of data.pages) if (row.part === 'basics') row.kind = 'primer';
		},
	});
	try {
		const outline = loadOutline(path.join(book.root, 'src', 'generated', 'outline.json'));
		assert.deepEqual(primerFirstParts(outline).map(({ id, part }) => [id, part?.slug ?? null]), [['basics/numbers', 'core'], ['basics/bytes', null]]);
		writeFiles(book.root, committedDiagram(needsGraphSource(outline, outline.partBySlug.get('basics'))).files);
		// The test book's rows are primers by the outline, concept pages by their front matter: only the index is drawn.
		const out = await render(book.root, 'basics/index').catch((error) => error.message);
		assert.match(out, new RegExp(`<h2>${c_IndexHeadings.primers}</h2>`));
		assert.match(out, /<li><a href="\/book\/basics\/numbers\/">Numbers<\/a>: first needed in part 3, Engine architecture<\/li>\n<li><a href="\/book\/basics\/bytes\/">Bytes<\/a>: no page outside this part needs it<\/li>/);
	} finally {
		book.remove();
	}
});

test('relative links from a part page to a page of the book', () => {
	assert.equal(relativeLink('core/review', 'core/time'), 'time.md');
	assert.equal(relativeLink('core/review', 'reference/commands/scene'), '../reference/commands/scene.md');
	assert.equal(relativeLink('core/index', 'core/time', 'the-accumulator'), 'time.md#the-accumulator');
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`the links of the generated parts are under the base ${setting}`, async () => {
		const book = partBook();
		try {
			const env = { DOCS_BASE: setting };
			const out = `${await render(book.root, 'core/index', { env })}\n${await render(book.root, 'core/review', { env })}`;
			const links = [...out.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
			assert.ok(links.length >= 10, links.join(' '));
			for (const link of links) assert.ok(link.startsWith(`${base}/`), `${link} is not under ${base}/`);
		} finally {
			book.remove();
		}
	});
}

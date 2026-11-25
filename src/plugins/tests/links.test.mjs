import { test } from 'node:test';
import assert from 'node:assert/strict';
import { c_BottomStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const target = `${frontmatter({ title: 'Time' })}\n## The accumulator\n\nText.\n${c_BottomStrip}`;

test('a relative .md link becomes the page URL under the base, with its anchor', async () => {
	const book = makeBook({ pages: { 'core/time': target, 'world/ecs': `${frontmatter()}\nSee [time](../core/time.md#the-accumulator) and [it](../core/time.md).\n${c_BottomStrip}` } });
	try {
		const html = await render(book.root, 'world/ecs');
		assert.match(html, /href="\/book\/core\/time\/#the-accumulator"/);
		assert.match(html, /href="\/book\/core\/time\/"/);
	} finally {
		book.remove();
	}
});

test('a link to a part\'s index page and to the landing page leads to the URLs Starlight serves them at', async () => {
	const index = '---\ntitle: "Engine architecture"\ndescription: "The part."\ntracks: [E]\nstatus: draft\ngenerated: index\n---\n\n## The map\n\nThe part.\n';
	const review = '---\ntitle: "Engine architecture: review"\ndescription: "Questions across the part."\ntracks: [E]\nstatus: draft\ngenerated: review\n---\n\nThe questions.\n';
	const book = makeBook({
		pages: {
			index: '---\ntitle: "Home"\ndescription: "The book."\ntemplate: splash\n---\n\nThe book.\n',
			'core/index': index,
			'core/review': review,
			'world/ecs': `${frontmatter()}\nSee [the part](../core/index.md#the-map), [its review](../core/review.md) and [the start](../index.md).\n${c_BottomStrip}`,
		},
		outline: (data) => {
			data.parts[3].partPages = true;
			data.parts[3].tracks = ['E'];
		},
	});
	try {
		for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
			const html = await render(book.root, 'world/ecs', { env: { DOCS_BASE: setting } });
			assert.match(html, new RegExp(`href="${base}/core/#the-map"`));
			assert.match(html, new RegExp(`href="${base}/core/review/"`));
			assert.match(html, new RegExp(`href="${base}/"`));
		}
	} finally {
		book.remove();
	}
});

test('a link to a page that does not exist fails the build with the line', async () => {
	const book = makeBook({ pages: { 'world/ecs': `${frontmatter()}\nSee [time](../core/missing.md).\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'world/ecs'), /world\/ecs\.md:\d+:\d+/, /there is no page core\/missing\.md/);
	} finally {
		book.remove();
	}
});

test('an anchor the target page does not have fails the build', async () => {
	const book = makeBook({ pages: { 'core/time': target, 'world/ecs': `${frontmatter()}\nSee [it](../core/time.md#no-such-heading).\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'world/ecs'), /no heading or figure with the anchor "no-such-heading"/);
	} finally {
		book.remove();
	}
});

test('an anchor of the same page is checked against its headings', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n## Strata's choice\n\nSee [above](#stratas-choice) and [nothing](#nothing).\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /"#nothing": this page has no heading/);
	} finally {
		book.remove();
	}
});

test('absolute paths, query strings and links to other files fail; other hosts pass', async () => {
	const book = makeBook({
		pages: {
			'core/time': `${frontmatter()}\n[a](/core/time/) [b](../world/x.html) [c](time.md?x=1) [d](https://example.org/x) [e](//cdn.example.org/x)\n${c_BottomStrip}`,
		},
	});
	try {
		const error = await rejectsWith(render(book.root, 'core/time'), /absolute path/, /does not name a \.md file/, /query string/, /another host without a scheme/);
		assert.doesNotMatch(error.message, /"https:\/\/example\.org\/x"/);
	} finally {
		book.remove();
	}
});

test('Markdown images fail: pictures come from figure manifests', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n![a cube](cube.png)\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /Markdown images are not used/);
	} finally {
		book.remove();
	}
});

test('a link may not leave the book\'s pages', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n[plan](../../../plan/site.md)\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /leaves the book's pages/);
	} finally {
		book.remove();
	}
});

test('a "%" that is not percent-encoding fails at the link instead of crashing the page', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\nSee [all of it](#100%) and [that](../world/ecs.md#a%zz).\n${c_BottomStrip}`, 'world/ecs': `${frontmatter()}\n## A\n${c_BottomStrip}` } });
	try {
		const error = await rejectsWith(render(book.root, 'core/time'), /core\/time\.md:\d+:\d+: "#100%" holds a "%" that is not percent-encoding/, /"\.\.\/world\/ecs\.md#a%zz" holds a "%"/);
		assert.doesNotMatch(error.message, /URI malformed/);
	} finally {
		book.remove();
	}
});

test('a link to a heading with math is refused: its anchor is KaTeX\'s, not the formula\'s', async () => {
	// Astro slugs the heading as KaTeX draws it ("math-x2x2x2-in-a-heading"); the index cannot know that anchor.
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n## Math $x^2$ in a heading\n\nSee [it](#math-x2-in-a-heading).\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /"#math-x2-in-a-heading": this page has no heading or figure with that anchor \(a heading with math has no anchor/);
	} finally {
		book.remove();
	}
});

test('a preview draws a link to a row of the outline not written yet as text; other builds fail on it', async () => {
	const book = makeBook({
		pages: { 'core/time': target, 'world/ecs': `${frontmatter()}
See [the loop](../core/frame-loop.md) and [time](../core/time.md).
${c_BottomStrip}` },
		outline: (data) => {
			data.pages.push({ ...data.pages.find((row) => row.id === 'core/time'), id: 'core/frame-loop', title: 'The frame loop' });
			data.parts.find((part) => part.slug === 'core').pages.push('core/frame-loop');
		},
	});
	try {
		const html = await render(book.root, 'world/ecs', { env: { DOCS_PREVIEW: '1' } });
		assert.match(html, /<span class="book-unwritten" title="This page is not written yet">the loop<\/span>/);
		assert.match(html, /href="\/book\/core\/time\/"/);
		await rejectsWith(render(book.root, 'world/ecs'), /there is no page core\/frame-loop\.md/);
	} finally {
		book.remove();
	}
});

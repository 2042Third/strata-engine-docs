// ":term[text]{id=…}" (plan/site.md, "Glossary"; plan/style.md §3): the first marked use of a term is a link to its
// glossary entry and a button that opens a native popover with the definition and a link to the term's home page.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { prefixChapter } from '../../lib/print.mjs';
import { c_BottomStrip, c_ReferenceStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Styles = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'styles');
const glossary = { terms: [
	{ id: 'fixed-step', term: 'fixed step', definition: 'A slice of simulated time of one length.', home: 'core/time' },
	{ id: 'draw-call', term: 'draw call', definition: 'One request to the GPU to draw.', home: 'gpu/draw' },
] };
const glossaryPage = `${frontmatter({ title: '"Glossary"', kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\nThe list.\n\n::glossary\n${c_ReferenceStrip}`;

async function withBook(body, run, { env } = {}) {
	const book = makeBook({ glossary, pages: {
		'world/ecs': `${frontmatter()}\n${body}\n${c_BottomStrip}`,
		'core/time': `${frontmatter({ title: '"Time"' })}\nThe **fixed step** is defined here.\n${c_BottomStrip}`,
		'reference/glossary': glossaryPage,
	} });
	try {
		return await run((id = 'world/ecs') => render(book.root, id, { env }));
	} finally {
		book.remove();
	}
}

test('the first marked use is a link and a button that opens the definition, with a link to the home page', async () => {
	await withBook('Each :term[fixed step]{id=fixed-step} runs once. Later :term[fixed steps]{id=fixed-step} are words.', async (page) => {
		const out = await page();
		assert.match(out, /Each <span class="book-term-use"><a class="book-term" href="\/book\/reference\/glossary\/#fixed-step">fixed step<\/a><button type="button" class="book-term__button" popovertarget="book-term-fixed-step" data-pagefind-ignore=""><span aria-hidden="true">\?<\/span><span class="sr-only">Definition of fixed step<\/span><\/button><span id="book-term-fixed-step" popover="auto" class="book-term__popover" data-pagefind-ignore=""><strong>fixed step<\/strong>: A slice of simulated time of one length\. <a href="\/book\/core\/time\/">Read: Time<\/a><\/span><\/span> runs once\./);
		// A later mark of the same term is plain words (style.md §3): one popover per term and page.
		assert.match(out, /Later <span>fixed steps<\/span> are words\./);
		assert.equal(out.match(/popovertarget=/g).length, 1);
		// The link has no title: the definition is in the popover, not a tooltip.
		assert.doesNotMatch(out, /class="book-term"[^>]* title=/);
	});
});

test('a term whose home page is not written yet, or is the page itself, gets no link to it', async () => {
	await withBook('One :term[draw call]{id=draw-call} costs.', async (page) => {
		assert.match(await page(), /<strong>draw call<\/strong>: One request to the GPU to draw\.<\/span>/);
	});
	const book = makeBook({ glossary, pages: { 'core/time': `${frontmatter()}\nA :term[fixed step]{id=fixed-step} here.\n${c_BottomStrip}`, 'reference/glossary': glossaryPage } });
	try {
		assert.doesNotMatch(await render(book.root, 'core/time'), /Read: /);
	} finally {
		book.remove();
	}
});

test('the button and the popover are hidden without popover support and in print; the link stays', () => {
	const book = readFileSync(path.join(c_Styles, 'book.css'), 'utf8');
	const print = readFileSync(path.join(c_Styles, 'print.css'), 'utf8');
	assert.match(book, /\.book-term__button,\n\.book-term__popover \{\n\tdisplay: none;\n\}\n@supports selector\(:popover-open\) \{/);
	assert.match(book, /\.book-term__popover:popover-open \{\n\t\tdisplay: block;/);
	assert.match(print, /\.book-term__button,\n\t\.book-term__popover \{\n\t\tdisplay: none !important;/);
});

test('in a print view the popover and its button keep each other: popovertarget follows the prefixed id', () => {
	const html = '<p><span class="book-term-use"><a class="book-term" href="/book/reference/glossary/#fixed-step">fixed step</a><button type="button" popovertarget="book-term-fixed-step"></button><span id="book-term-fixed-step" popover="auto"></span></span></p>';
	const out = prefixChapter(html, 'world/ecs', new Set(['world/ecs']), '/book');
	assert.match(out, /popovertarget="world--ecs--book-term-fixed-step"/);
	assert.match(out, /id="world--ecs--book-term-fixed-step"/);
});

test('a mark names a glossary entry by its id, and only its id', async () => {
	await withBook('A :term[thing]{id=nothing} here.', async (page) => rejectsWith(page(), /:term\{id=nothing\}: the glossary has no entry "nothing"/));
	await withBook('A :term[thing] here.', async (page) => rejectsWith(page(), /:term\[…\] needs the id of its glossary entry: :term\[text\]\{id=…\}/));
	await withBook('A :term[fixed step]{id=fixed-step lang=en} here.', async (page) => rejectsWith(page(), /:term has no attribute "lang" \(it takes id\)/));
});

test('a mark stands in a sentence: not in a heading, a link, an aside\'s title or an answer\'s summary', async () => {
	await withBook('## The :term[fixed step]{id=fixed-step}\n\nText.', async (page) => rejectsWith(page(), /a :term mark stands in a sentence, not in a heading/));
	await withBook('[A :term[fixed step]{id=fixed-step}](../core/time.md)', async (page) => rejectsWith(page(), /a :term mark does not stand inside a link/));
	await withBook(':::why[Why a :term[fixed step]{id=fixed-step}?]\nBecause.\n:::', async (page) => rejectsWith(page(), /a :term mark does not stand in a title or a summary the book draws/));
	await withBook('A question?\n\n:::answer[The :term[fixed step]{id=fixed-step}]\nYes.\n:::', async (page) => rejectsWith(page(), /a :term mark does not stand in a title or a summary the book draws/));
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`a marked term's link and its home page's link are under the base ${setting}`, async () => {
		await withBook('Each :term[fixed step]{id=fixed-step} runs.', async (page) => {
			const out = await page();
			assert.match(out, new RegExp(`<a class="book-term" href="${base}/reference/glossary/#fixed-step">`));
			assert.match(out, new RegExp(`<a href="${base}/core/time/">Read: Time</a>`));
			for (const match of out.matchAll(/href="([^"#]*)/g)) if (match[1].startsWith('/')) assert.ok(match[1].startsWith(`${base}/`), match[1]);
		}, { env: { DOCS_BASE: setting } });
	});

	test(`the glossary page links each entry's home page and page of use under the base ${setting}`, async () => {
		const terms = { terms: [{ ...glossary.terms[0], use: 'make/first-script' }, glossary.terms[1]] };
		const book = makeBook({ glossary: terms, pages: {
			'core/time': `${frontmatter({ title: '"Time"' })}\nThe **fixed step** is defined here.\n${c_BottomStrip}`,
			'make/first-script': `${frontmatter({ title: '"Your first script"' })}\nText.\n${c_BottomStrip}`,
			'reference/glossary': glossaryPage,
		} });
		try {
			const out = await render(book.root, 'reference/glossary', { env: { DOCS_BASE: setting } });
			assert.match(out, new RegExp(`<a href="${base}/core/time/">Read: Time</a> <a href="${base}/make/first-script/">Used in: Your first script</a>`));
			const links = [...out.matchAll(/href="([^"]*)"/g)].map((match) => match[1]);
			assert.equal(links.length, 2);
			for (const link of links) assert.ok(link.startsWith(`${base}/`), link);
		} finally {
			book.remove();
		}
	});
}

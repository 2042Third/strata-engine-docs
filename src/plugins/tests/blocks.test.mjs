// Asides, answers, tabs, the track chooser and the report of unknown directives.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bottomStrip, c_BottomStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

async function html(body) {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` } });
	try {
		return await render(book.root, 'core/time');
	} finally {
		book.remove();
	}
}

async function fails(body, ...patterns) {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` } });
	try {
		return await rejectsWith(render(book.root, 'core/time'), ...patterns);
	} finally {
		book.remove();
	}
}

test('the book\'s asides render with Starlight\'s markup, their own class and a default or given title', async () => {
	const out = await html(':::why\nBecause.\n:::\n\n:::history[Before 0.8.0]\nIt was different.\n:::');
	assert.match(out, /<aside class="starlight-aside book-aside book-aside--why" aria-label="Why it is so">/);
	assert.match(out, /<p class="starlight-aside__title" aria-hidden="true">Why it is so<\/p>/);
	assert.match(out, /aria-label="Before 0.8.0"/);
	assert.match(out, /<div class="starlight-aside__content"><p>It was different\.<\/p><\/div>/);
});

test('every aside kind of the style guide is known', async () => {
	const out = await html(['why', 'question', 'history', 'elsewhere', 'rule'].map((name) => `:::${name}\nText.\n:::`).join('\n\n'));
	for (const name of ['why', 'question', 'history', 'elsewhere', 'rule']) assert.match(out, new RegExp(`book-aside--${name}`));
});

test('an answer is a details element that works without scripts', async () => {
	const out = await html('Question?\n\n:::answer\nThe answer.\n:::\n\n:::answer[Worked solution]\nSteps.\n:::');
	assert.match(out, /<details class="book-answer"><summary>Answer<\/summary><div class="book-answer__body"><p>The answer\.<\/p><\/div><\/details>/);
	assert.match(out, /<summary>Worked solution<\/summary>/);
});

test('tabs keep every panel under its label in the HTML', async () => {
	const out = await html('::::tabs{sync=shell}\n:::tab[PowerShell]\nOne.\n:::\n:::tab[Shell]\nTwo.\n:::\n::::');
	assert.match(out, /<book-tabs data-sync="shell">/);
	assert.match(out, /<div class="book-tabs__panel" data-label="PowerShell"><p class="book-tabs__label">PowerShell<\/p><p>One\.<\/p><\/div>/);
	assert.match(out, /data-label="Shell"/);
});

test('tab sets need two labelled tabs, and a tab belongs inside a set', async () => {
	await fails('::::tabs\n:::tab[Only]\nOne.\n:::\n::::', /at least two tabs/);
	await fails('::::tabs\n:::tab\nOne.\n:::\n:::tab[Two]\nTwo.\n:::\n::::', /a tab needs a label/);
	await fails(':::tab[Alone]\nText.\n:::', /:::tab belongs inside ::::tabs/);
	await fails('::::tabs{sync=Bad Key}\n:::tab[A]\n1\n:::\n:::tab[B]\n2\n:::\n::::', /lowercase name/);
});

test('an unknown block directive fails the build; text directives such as std::vector stay text', async () => {
	await fails(':::pitfal\nOops.\n:::', /unknown directive :::pitfal/);
	await fails('::figur{id=x}', /unknown directive ::figur/);
	const out = await html('Use std::vector and a:b in prose.');
	assert.match(out, /std:/);
});

test('Starlight\'s own asides pass the report untouched', async () => {
	const out = await html(':::note\nA note.\n:::\n\n:::danger\nCareful.\n:::');
	assert.match(out, /A note\./);
});

test('the track chooser lists the three tracks with their first written page, and only on a page of Start here', async () => {
	const start = (title, tracks, body = 'Text.') => `${frontmatter({ title: `"${title}"`, tracks, kind: 'how-to', since: undefined })}\n${body}\n${bottomStrip('how-to')}`;
	const book = makeBook({
		pages: {
			index: '---\ntitle: Home\ndescription: The book.\ntemplate: splash\n---\n\n::track-chooser\n',
			'start/how-to-read': start('How to read', '[G, B, E]', '::track-chooser'),
			'start/install': start('Install', '[G, B, E]'),
		},
		// The first page of track E is not written yet: the chooser starts it at the first page that is.
		outline: (data) => {
			data.pages.unshift({ id: 'start/welcome', title: 'Welcome', kind: 'concept', size: 'S', tracks: ['E'], needs: [], part: 'start', level: 1, row: 'test' });
			data.parts[0].pages.unshift('start/welcome');
			data.tracks.E.unshift({ id: 'start/welcome' });
		},
	});
	try {
		const out = await render(book.root, 'start/how-to-read');
		assert.match(out, /<book-track-chooser>/);
		assert.match(out, /<li class="book-track" data-track="game"><strong>Games<\/strong> \(G\) the Games track\. <a href="\/book\/start\/how-to-read\/" class="book-track__start">Start with: How to read<\/a>/);
		assert.match(out, /data-track="beginner"/);
		assert.match(out, /<button type="button" class="book-track__choose" data-track="engine" hidden>/);
		assert.doesNotMatch(out, /Welcome/);
		await rejectsWith(render(book.root, 'index'), /::track-chooser belongs on a page of the part "start" \(start\/how-to-read\)/);
	} finally {
		book.remove();
	}
});

test('math renders at build time and broken TeX fails the build', async () => {
	const out = await html('Inline $a + b$ and\n\n$$\n\\frac{1}{2}\n$$');
	assert.match(out, /class="katex"/);
	assert.match(out, /<math/);
	await fails('Broken $\\frac{1}{$ here.', /math:/);
});

test('a formula KaTeX cannot render fails once, at its own line, with the page\'s other problems', async () => {
	const body = 'Inline $\\frac{1}{$ here.\n\n$$\n\\badcommand{x}\n$$\n\n:::pitfal\nOops.\n:::';
	const error = await fails(body, /unknown directive :::pitfal/, /math: KaTeX parse error/);
	const lines = error.message.split('\n').filter((line) => /math:/.test(line));
	assert.equal(lines.length, 2, error.message);
	for (const line of lines) assert.doesNotMatch(line, /:0:0:/);
	// The display formula is reported at the line of its $$ fence, after the inline one.
	const numbers = lines.map((line) => Number(/time\.md:(\d+):/.exec(line)[1]));
	assert.ok(numbers[0] > 0 && numbers[1] > numbers[0], error.message);
});

test('behind the check, rehype-katex\'s warnings fail the build once each, at the nearest known line', async () => {
	const { rehypeBookMath } = await import('../rehype.mjs');
	const { VFile } = await import('vfile');
	const file = new VFile({ path: 'x.md', value: '' });
	const ancestor = { type: 'element', tagName: 'pre', position: { start: { line: 7, column: 1 } }, children: [] };
	file.message('Could not render math with KaTeX', { source: 'rehype-katex', ancestors: [{ type: 'root' }, ancestor], cause: new Error('KaTeX parse error: bad') });
	const tree = { type: 'root', children: [{ type: 'element', tagName: 'span', properties: { className: ['katex-error'], title: 'bad' }, children: [] }] };
	const transformer = rehypeBookMath({ settings: { root: process.cwd() } })();
	assert.throws(() => transformer(tree, file), (error) => /has 1 problem:/.test(error.message) && /x\.md:7:1: math: KaTeX parse error: bad/.test(error.message));
});

test('the formula check and rehype-katex agree on what renders', async () => {
	const { formulaProblem } = await import('../math.mjs');
	assert.equal(formulaProblem('\\frac{a}{b} + \\sqrt{2}', false), null);
	assert.equal(formulaProblem('\\sum_{i=0}^{n} x_i', true), null);
	assert.match(formulaProblem('\\frac{1}{', false), /KaTeX parse error/);
	assert.match(formulaProblem('\\undefinedmacro', true), /Undefined control sequence/);
});

test('search leaves code gutters, KaTeX\'s drawn formulas and the TeX source out, and keeps the MathML', async () => {
	const { rehypeBookSearch } = await import('../rehype.mjs');
	const element = (className, children = []) => ({ type: 'element', tagName: 'span', properties: { className: [className] }, children });
	const annotation = { type: 'element', tagName: 'annotation', properties: { encoding: 'application/x-tex' }, children: [{ type: 'text', value: 'W_{\\text{child}}' }] };
	const semantics = { type: 'element', tagName: 'semantics', properties: {}, children: [{ type: 'element', tagName: 'mi', properties: {}, children: [{ type: 'text', value: 'W' }] }, annotation] };
	const tree = { type: 'root', children: [element('katex', [element('katex-mathml', [semantics]), element('katex-html')]), element('gutter')] };
	rehypeBookSearch()()(tree);
	const [katex, gutter] = tree.children;
	assert.equal(katex.properties.dataPagefindIgnore, undefined);
	assert.equal(katex.children[0].properties.dataPagefindIgnore, undefined);
	assert.equal(semantics.properties.dataPagefindIgnore, undefined);
	assert.equal(semantics.children[0].properties.dataPagefindIgnore, undefined);
	assert.equal(annotation.properties.dataPagefindIgnore, '');
	assert.equal(katex.children[1].properties.dataPagefindIgnore, '');
	assert.equal(gutter.properties.dataPagefindIgnore, '');
});

test('search weighs a code block half as much as prose, and the generated reference\'s code blocks as the reference', async () => {
	const { rehypeBookSearch } = await import('../rehype.mjs');
	const element = (className, children = []) => ({ type: 'element', tagName: 'div', properties: { className: [className] }, children });
	const code = () => element('expressive-code', [element('frame')]);
	const tree = { type: 'root', children: [code(), element('book-reference', [element('table'), code()]), element('book-answer__body', [code()])] };
	rehypeBookSearch()()(tree);
	const [page, reference, answer] = tree.children;
	assert.equal(page.properties.dataPagefindWeight, '0.5');
	assert.equal(page.children[0].properties.dataPagefindWeight, undefined);
	// The reference's own weight (0.3, src/plugins/include.mjs) holds for the code blocks inside it.
	assert.equal(reference.children[1].properties.dataPagefindWeight, undefined);
	assert.equal(answer.children[0].properties.dataPagefindWeight, '0.5');
});

test('the heading links draw their icon from one definition per page, and the print view renames it per chapter', async () => {
	const { rehypeBookAnchorIcons } = await import('../rehype.mjs');
	const { toHtml } = await import('hast-util-to-html');
	const { prefixChapter } = await import('../../lib/print.mjs');
	// Starlight's heading link: a wrapper, the heading and a link holding the icon's SVG and its words.
	const path = { type: 'element', tagName: 'path', properties: { d: 'M1 2h3' }, children: [] };
	// Like Starlight, every link holds one and the same icon node.
	const shared = { type: 'element', tagName: 'span', properties: { ariaHidden: 'true', className: ['sl-anchor-icon'] }, children: [
		{ type: 'element', tagName: 'svg', properties: { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'currentColor' }, children: [path] }] };
	const heading = (id) => ({ type: 'element', tagName: 'div', properties: { className: ['sl-heading-wrapper'] }, children: [
		{ type: 'element', tagName: 'h2', properties: { id }, children: [{ type: 'text', value: id }] },
		{ type: 'element', tagName: 'a', properties: { className: ['sl-anchor-link'], href: `#${id}` }, children: [shared] }] });
	const tree = { type: 'root', children: [heading('one'), heading('two')] };
	rehypeBookAnchorIcons()()(tree);
	const html = toHtml(tree);
	assert.match(html, /<h2 id="one">one<\/h2><a class="sl-anchor-link" href="#one"><span aria-hidden="true" class="sl-anchor-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><g id="book-anchor-icon"><path d="M1 2h3"><\/path><\/g><\/svg>/);
	assert.match(html, /<h2 id="two">two<\/h2><a class="sl-anchor-link" href="#two"><span aria-hidden="true" class="sl-anchor-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><use href="#book-anchor-icon"><\/use><\/svg>/);
	assert.equal(html.match(/M1 2h3/g).length, 1);
	const printed = prefixChapter(html, 'core/time', new Set(), '');
	assert.match(printed, /<use href="#core--time--book-anchor-icon"><\/use>/);
	assert.match(printed, /<g id="core--time--book-anchor-icon">/);
	// A page with one heading keeps its icon inline.
	const single = { type: 'root', children: [heading('only')] };
	rehypeBookAnchorIcons()()(single);
	assert.doesNotMatch(toHtml(single), /<use|book-anchor-icon/);
});

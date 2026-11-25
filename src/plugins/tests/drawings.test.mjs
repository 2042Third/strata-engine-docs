// Drawings (plan/card/drawing.md, scripts/drawings.mjs): what the check reads from a drawing's file (the root, the
// viewBox, the one style block, roles as classes, no script, raster image, outside reference or font of its own), how
// it judges what Chromium measured (text size, text inside the viewBox, contrast), and its command line. No test starts
// a browser: these are the parts that judge.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { c_Classes, c_LeastWidth, c_MaxHeight, c_NarrowColumn, c_NarrowTextSize, c_Roles, c_StyleBlock, c_Width, checkDrawings, drawingFile, measuredProblems, narrowProblems, parseArguments, parseViewBox, printProblems, selectDrawings, siteStyles, skeleton, staticProblems } from '../../../scripts/drawings.mjs';

const c_Figure = 'adding-arrows';
/** A drawing of the figure c_Figure holding `body`, with the root's attributes `root` (the card's by default). */
const drawing = (body, root = `xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 ${c_Width} 300"`) => `<svg ${root}>\n${c_StyleBlock}\n${body}\n</svg>\n`;
const problemsOf = (body, root) => staticProblems(drawing(body, root), c_Figure);

test('the empty drawing start writes passes, and its style block paints every role as a fill and as a stroke', () => {
	assert.deepEqual(staticProblems(skeleton(300), c_Figure), []);
	for (const role of c_Roles) {
		assert.ok(c_StyleBlock.includes(`.${role.name} { fill: var(${role.variable}, ${role.fallback}); }`), role.name);
		assert.ok(c_StyleBlock.includes(`.line-${role.name} { stroke: var(${role.variable}, ${role.fallback}); }`), role.name);
		assert.ok(c_Classes.has(role.name) && c_Classes.has(`line-${role.name}`));
	}
	assert.match(c_StyleBlock, /font-family: var\(--sl-font, 'Inter Variable'/);
});

test('a drawing with roles, a halo, a dashed line, a gradient swatch and its own ids passes', () => {
	const body = [
		'<defs><linearGradient id="adding-arrows-ramp"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>',
		'<rect class="swatch" x="10" y="10" width="100" height="20" fill="url(#adding-arrows-ramp)"/>',
		'<g class="swatch"><rect x="10" y="40" width="20" height="20" fill="#ff8800"/></g>',
		'<g class="line-blue"><line x1="10" y1="80" x2="200" y2="80" stroke-dasharray="4 3"/></g>',
		'<polygon class="blue" points="200,76 210,80 200,84"/>',
		'<text class="small muted halo" x="20" y="120" text-anchor="middle">a + b<tspan class="small" dy="5">1</tspan></text>',
		'<path d="M0 0H10" fill="none" class="line-ink"/>',
		'<use href="#adding-arrows-ramp"/>',
	].join('\n');
	assert.deepEqual(problemsOf(body), []);
});

test('the root: one <svg>, its namespace and class, a viewBox of the column\'s width, no width or height', () => {
	assert.match(staticProblems('<div></div>', c_Figure)[0], /not one <svg> element/);
	assert.match(staticProblems(`${skeleton(300)}<svg></svg>`, c_Figure)[0], /not one <svg> element/);
	assert.ok(problemsOf('', `class="book-drawing" viewBox="0 0 ${c_Width} 300"`).some((problem) => /xmlns/.test(problem)));
	assert.ok(problemsOf('', `xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${c_Width} 300"`).some((problem) => /class="book-drawing"/.test(problem)));
	assert.ok(problemsOf('', `xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 ${c_Width} 300" width="768"`).some((problem) => /width or height/.test(problem)));
	assert.ok(problemsOf('', 'xmlns="http://www.w3.org/2000/svg" class="book-drawing"').some((problem) => /no viewBox/.test(problem)));
	assert.ok(problemsOf('', 'xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 760 300"').some((problem) => /viewBox is "0 0 760 300"/.test(problem)));
	assert.ok(problemsOf('', `xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 ${c_Width} ${c_MaxHeight + 1}"`).some((problem) => /at most/.test(problem)));
	assert.deepEqual(parseViewBox('0,0 768 300'), { x: 0, y: 0, width: 768, height: 300 });
	assert.equal(parseViewBox('0 0 768'), null);
});

test('what a drawing never holds: scripts, events, raster images, HTML, links, titles, fonts, filters, markers', () => {
	const cases = [
		['<script>alert(1)</script>', /a script/],
		['<rect class="ink" width="1" height="1" onclick="alert(1)"/>', /event attribute/],
		['<image href="picture.png" width="10" height="10"/>', /raster image/],
		['<foreignObject width="10" height="10"><div>x</div></foreignObject>', /HTML inside/],
		['<a href="https://example.com"><text>x</text></a>', /a link/],
		['<title>Adding arrows</title>', /a title/],
		['<desc>Arrows</desc>', /a description/],
		['<filter id="adding-arrows-blur"><feGaussianBlur stdDeviation="2"/></filter>', /a filter/],
		['<marker id="adding-arrows-head"><path d="M0 0L5 5"/></marker>', /a marker/],
		['<circle class="ink" r="2"/><animate attributeName="r" to="5"/>', /<animate>/],
		['<text font-family="Comic Sans MS">x</text>', /sets font-family/],
		['<text font-size="11">x</text>', /sets font-size/],
		['<text style="fill: red">x</text>', /style attribute/],
		['<rect class="ink" opacity="0.5" width="1" height="1"/>', /see-through/],
	];
	for (const [body, expected] of cases) assert.ok(problemsOf(body).some((problem) => expected.test(problem)), `${body}: ${problemsOf(body).join('; ')}`);
});

test('references stay inside the drawing and point at ids it defines', () => {
	assert.ok(problemsOf('<use href="other.svg#shape"/>').some((problem) => /outside the drawing/.test(problem)));
	assert.ok(problemsOf('<use xlink:href="#adding-arrows-missing"/>').some((problem) => /does not define/.test(problem)));
	assert.ok(problemsOf('<rect class="swatch" width="1" height="1" fill="url(https://example.com/a.svg#g)"/>').some((problem) => /outside the drawing/.test(problem)));
	assert.ok(problemsOf('<g clip-path="url(#adding-arrows-nowhere)"></g>').some((problem) => /does not define/.test(problem)));
	assert.ok(problemsOf('<rect id="box" class="ink" width="1" height="1"/>').some((problem) => /does not start with "adding-arrows-"/.test(problem)));
	assert.ok(problemsOf('<rect id="adding-arrows-a" class="ink"/><rect id="adding-arrows-a" class="ink"/>').some((problem) => /used twice/.test(problem)));
});

test('colors come only from the roles: a literal color, an unknown class, a color on a text, a stop outside a gradient', () => {
	assert.ok(problemsOf('<rect width="1" height="1" fill="#ffffff"/>').some((problem) => /fill="#ffffff", a color outside the roles/.test(problem)));
	assert.ok(problemsOf('<line x2="5" stroke="currentColor"/>').some((problem) => /stroke="currentColor", a color outside the roles/.test(problem)));
	assert.ok(problemsOf('<g class="swatch"><text fill="#333">x</text></g>').some((problem) => /a text takes its color from a role class/.test(problem)));
	assert.ok(problemsOf('<rect class="blu" width="1" height="1"/>').some((problem) => /class "blu"/.test(problem)));
	assert.ok(problemsOf('<rect class="book-drawing" width="1" height="1"/>').some((problem) => /class "book-drawing"/.test(problem)));
	assert.ok(problemsOf('<g><stop stop-color="#000"/></g>').some((problem) => /outside a gradient/.test(problem)));
	assert.ok(problemsOf('<rect class="ink" width="1" height="1" color="red"/>').some((problem) => /color outside the roles/.test(problem)));
	assert.deepEqual(problemsOf('<rect fill="none" stroke="none" class="line-ink" width="1" height="1"/>'), []);
});

test('the style block is the card\'s, once: none, two, or an edited one fails', () => {
	const bare = `<svg xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 ${c_Width} 300"></svg>`;
	assert.ok(staticProblems(bare, c_Figure).some((problem) => /0 style blocks/.test(problem)));
	assert.ok(problemsOf(c_StyleBlock).some((problem) => /2 style blocks/.test(problem)));
	const edited = drawing('').replace('#17181c', '#000000');
	assert.ok(staticProblems(edited, c_Figure).some((problem) => /not the card's/.test(problem)));
	// Line ends and indentation do not count.
	assert.deepEqual(staticProblems(drawing('').replace(/\n/g, '\r\n\t'), c_Figure), []);
});

test('measured texts: too small, outside the viewBox, or under 4.5:1 in a theme', () => {
	const view = { left: 10, right: 60, top: 20, bottom: 40 };
	const ok = { tag: 'text', text: 'a + b', size: 14, view, ratio: 7, color: { r: 0, g: 0, b: 0 }, background: { r: 255, g: 255, b: 255 } };
	assert.deepEqual(measuredProblems('light', { width: 768, height: 300, texts: [ok] }), []);
	const small = measuredProblems('light', { width: 768, height: 300, texts: [{ ...ok, size: 12 }] });
	assert.match(small[0], /12\.0 px at the column's width \(at least 14\)/);
	const outside = measuredProblems('light', { width: 768, height: 300, texts: [{ ...ok, view: { ...view, right: 770 } }] });
	assert.match(outside[0], /leaves the viewBox by 2\.0/);
	assert.deepEqual(measuredProblems('light', { width: 768, height: 300, texts: [{ ...ok, view: { ...view, left: -0.4 } }] }), []);
	const faint = measuredProblems('dark', { width: 768, height: 300, texts: [{ ...ok, ratio: 3.2, color: { r: 85, g: 89, b: 98 }, background: { r: 23, g: 24, b: 28 } }] });
	assert.match(faint[0], /3\.20:1 .* dark theme .*#555962 on #17181c/);
	// Geometry is the same in both themes: the second theme reports only contrast.
	assert.deepEqual(measuredProblems('dark', { width: 768, height: 300, texts: [{ ...ok, size: 9 }] }, { geometry: false }), []);
});

test('measured shapes: one the viewBox cuts off fails, once', () => {
	const inside = { tag: 'line', view: { left: 72, right: 672, top: 358, bottom: 374 } };
	assert.deepEqual(measuredProblems('light', { width: 768, height: 400, texts: [], shapes: [inside] }), []);
	const cut = measuredProblems('light', { width: 768, height: 360, texts: [], shapes: [inside] });
	assert.match(cut[0], /a <line> is cut off by the viewBox's edge by 14\.0/);
	assert.deepEqual(measuredProblems('light', { width: 768, height: 373.6, texts: [], shapes: [inside] }), []);
	assert.deepEqual(measuredProblems('dark', { width: 768, height: 360, texts: [], shapes: [inside] }, { geometry: false }), []);
});

test('the phone\'s column: a box that leaves the column or does not scroll, or text below the least width\'s size, fails', () => {
	const ok = { column: c_NarrowColumn, box: c_NarrowColumn, drawn: c_LeastWidth, scrolls: true, smallest: c_NarrowTextSize };
	assert.deepEqual(narrowProblems(ok), []);
	assert.deepEqual(narrowProblems({ ...ok, smallest: null }), []);
	assert.match(narrowProblems({ ...ok, box: c_LeastWidth })[0], /the drawing's box is 640 px wide: it leaves the column/);
	assert.match(narrowProblems({ ...ok, scrolls: false })[0], /is 640 px wide and its box does not scroll/);
	assert.match(narrowProblems({ ...ok, drawn: c_NarrowColumn, smallest: 6.2 })[0], /smallest text is 6\.2 px \(at least 11\.7/);
	// A drawing that fits the column needs no scroller.
	assert.deepEqual(narrowProblems({ ...ok, drawn: c_NarrowColumn, scrolls: false }), []);
});

test('printed from the dark theme, a drawing paints as the light theme does on screen', () => {
	const light = [{ tag: 'svg', fill: 'rgb(23, 24, 28)', stroke: 'none' }, { tag: 'text', fill: 'rgb(23, 24, 28)', stroke: 'none' }];
	assert.deepEqual(printProblems(light, light.map((element) => ({ ...element }))), []);
	const dark = [light[0], { ...light[1], fill: 'rgb(255, 255, 255)' }];
	assert.deepEqual(printProblems(light, dark), ["printed from the dark theme a <text>'s fill is rgb(255, 255, 255), not the light theme's rgb(23, 24, 28)"]);
	assert.match(printProblems(light, light.slice(1))[0], /has 1 elements, on screen 2/);
});

test('in Chromium a drawing with small text passes with the site\'s styles, and fails without the least width or Starlight\'s print colors', async () => {
	const root = mkdtempSync(path.join(os.tmpdir(), 'drawings-browser-'));
	try {
		const file = path.join(root, `${c_Figure}.svg`);
		writeFileSync(file, drawing('<rect class="plate" x="10" y="10" width="300" height="80"/>\n<text class="ink small" x="24" y="56">Small words</text>'));
		const drawings = [{ id: `test/chapter/${c_Figure}`, file }];
		const styles = siteStyles();
		assert.deepEqual((await checkDrawings(drawings, { styles })).problems, []);
		const shrinking = styles.replace(/\.book-figure__drawing svg \{\s*min-width: 40rem;\s*\}/, '');
		assert.notEqual(shrinking, styles, 'book.css gives a drawing its least width');
		assert.ok((await checkDrawings(drawings, { styles: shrinking })).problems.some((problem) => /column of 340 px its smallest text is 6\.\d px/.test(problem)));
		// Starlight's print style sheet sets its colors to the light theme's on :root; without it a print from the dark
		// theme would draw light ink on paper.
		const noPrintColors = styles.replace('/* Colours — force light mode when printing */', '}\n:root.book-none {');
		assert.notEqual(noPrintColors, styles, 'Starlight\'s print style sheet is among the styles');
		assert.ok((await checkDrawings(drawings, { styles: noPrintColors })).problems.some((problem) => /printed from the dark theme a <text>'s fill/.test(problem)));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('drawings are named <part>/<chapter>/<figure>, and check picks chapters or figures', () => {
	const root = mkdtempSync(path.join(os.tmpdir(), 'drawings-'));
	try {
		assert.equal(drawingFile('basics/math-vectors/adding-arrows', root), path.join(root, 'basics', 'math-vectors', 'adding-arrows.svg'));
		assert.equal(drawingFile('basics/math-vectors', root), null);
		assert.equal(drawingFile('../x/y', root), null);
		for (const name of ['basics/math-vectors/adding-arrows.svg', 'basics/math-vectors/unit-circle.svg', 'core/time/steps.svg', 'core/time/steps.avif']) {
			mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
			writeFileSync(path.join(root, name), '');
		}
		assert.deepEqual(selectDrawings([], root).drawings.map((item) => item.id), ['basics/math-vectors/adding-arrows', 'basics/math-vectors/unit-circle', 'core/time/steps']);
		assert.deepEqual(selectDrawings(['basics/math-vectors'], root).drawings.map((item) => item.id), ['basics/math-vectors/adding-arrows', 'basics/math-vectors/unit-circle']);
		assert.deepEqual(selectDrawings(['core/time/steps', 'core/time/steps.svg'], root).drawings.map((item) => item.id), ['core/time/steps']);
		assert.deepEqual(selectDrawings(['basics/math'], root).unknown, ['basics/math']);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('the command line', () => {
	assert.match(parseArguments([]).error, /usage/);
	assert.match(parseArguments(['render']).error, /one drawing/);
	assert.match(parseArguments(['render', 'basics/math-vectors']).error, /not <part>\/<chapter>\/<figure>/);
	assert.match(parseArguments(['render', 'a/b/c', '--scale']).error, /needs a value/);
	assert.match(parseArguments(['render', 'a/b/c', '--scale', '0']).error, /positive number/);
	assert.match(parseArguments(['start', 'a/b/c', '--height', String(c_MaxHeight + 1)]).error, /up to/);
	assert.match(parseArguments(['check', '--fast']).error, /unknown option/);
	assert.deepEqual(parseArguments(['render', 'a/b/c', '--out', 'x', '--scale', '2']), { command: 'render', names: ['a/b/c'], out: 'x', scale: 2, height: 400 });
	assert.deepEqual(parseArguments(['check']).names, []);
	assert.deepEqual(parseArguments(['check', 'a/b', 'c/d/e']).names, ['a/b', 'c/d/e']);
});

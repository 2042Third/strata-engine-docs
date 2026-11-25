// The measures of budget row 18 (scripts/diagram-checks.mjs, and `npm run diagrams -- --contrast`): contrast as WCAG 2
// computes it, the color behind a text, a label's ink, labels inside their boxes, a figure's caption and name, and the
// pages of a build that hold a diagram. The browser part runs on the built site; these are the parts that judge.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { c_MinimumContrast, composite, contrastRatio, diagramPages, dominantColor, drawingReport, figureProblems, hex, inkBox, labelProblems, parseColor, relativeLuminance, textContrasts } from '../../../scripts/diagram-checks.mjs';
import { makeBook } from './helpers.mjs';

const black = { r: 0, g: 0, b: 0, a: 1 };
const white = { r: 255, g: 255, b: 255, a: 1 };

test('contrast is WCAG 2\'s ratio of relative luminances', () => {
	assert.equal(relativeLuminance(white), 1);
	assert.equal(relativeLuminance(black), 0);
	assert.equal(contrastRatio(black, white), 21);
	assert.equal(contrastRatio(white, black), 21);
	assert.equal(contrastRatio(white, white), 1);
	// #767676 on white is the darkest gray that passes 4.5:1, #777777 the lightest that does not.
	assert.ok(contrastRatio(parseColor('rgb(118, 118, 118)'), white) >= c_MinimumContrast);
	assert.ok(contrastRatio(parseColor('rgb(119, 119, 119)'), white) < c_MinimumContrast);
});

test('colors as getComputedStyle writes them, and a fill drawn at half opacity', () => {
	assert.deepEqual(parseColor('rgb(1, 2, 3)'), { r: 1, g: 2, b: 3, a: 1 });
	assert.deepEqual(parseColor('rgba(10, 20, 30, 0.5)'), { r: 10, g: 20, b: 30, a: 0.5 });
	assert.deepEqual(parseColor('rgb(10 20 30 / 25%)'), { r: 10, g: 20, b: 30, a: 0.25 });
	assert.equal(parseColor('none'), null);
	assert.equal(parseColor('url(#gradient)'), null);
	assert.deepEqual(composite(white, 0.5, black), { r: 127.5, g: 127.5, b: 127.5, a: 1 });
	assert.equal(hex({ r: 255, g: 16, b: 1.4 }), '#ff1001');
});

/** A raw RGBA picture `width` × `height` of one color, with `paint(x, y)` → [r, g, b] where it returns one. */
function picture(width, height, color, paint = () => null) {
	const data = Buffer.alloc(width * height * 4);
	for (let y = 0; y < height; y++) {
		for (let x = 0; x < width; x++) {
			const [r, g, b] = paint(x, y) ?? color;
			data.set([r, g, b, 255], (y * width + x) * 4);
		}
	}
	return { data, info: { width, height, channels: 4 } };
}

test('the color behind a text is the one most of its box\'s pixels have', () => {
	const { data, info } = picture(20, 10, [200, 200, 200], (x, y) => (x < 4 && y < 3 ? [0, 0, 0] : null));
	assert.deepEqual(dominantColor(data, info, { x: 0, y: 0, width: 10, height: 10 }), { r: 200, g: 200, b: 200, a: 1 });
	assert.deepEqual(dominantColor(data, info, { x: 0, y: 0, width: 3, height: 2 }), { r: 0, g: 0, b: 0, a: 1 });
	// A box outside the picture has no pixel.
	assert.equal(dominantColor(data, info, { x: 30, y: 0, width: 5, height: 5 }), null);
});

test('a label\'s ink is where the pictures with and without the texts differ, inside its text box', () => {
	const hidden = picture(20, 10, [255, 255, 255]);
	const shown = picture(20, 10, [255, 255, 255], (x, y) => (x >= 5 && x < 9 && y >= 2 && y < 7 ? [0, 0, 0] : null));
	assert.deepEqual(inkBox(shown.data, hidden.data, shown.info, { x: 0, y: 0, width: 20, height: 10 }), { x: 5, y: 2, width: 4, height: 5 });
	// Only the text's own box is read: ink of a neighbour outside it is not this text's.
	assert.deepEqual(inkBox(shown.data, hidden.data, shown.info, { x: 7.5, y: 0, width: 10, height: 10 }), { x: 7, y: 2, width: 2, height: 5 });
	assert.equal(inkBox(shown.data, hidden.data, shown.info, { x: 12, y: 0, width: 8, height: 10 }), null);
});

test('a label leaves its box when its ink stands past the box by more than half a pixel', () => {
	const shape = { x: 0, y: 0, width: 100, height: 40 };
	const texts = [
		{ text: 'inside', box: { x: 10, y: 5, width: 50, height: 30 }, shape },
		{ text: 'line box past, ink inside', box: { x: 10, y: -3, width: 50, height: 46 }, ink: { x: 12, y: 8, width: 40, height: 20 }, shape },
		{ text: 'wide', box: { x: 10, y: 5, width: 50, height: 30 }, ink: { x: -2, y: 8, width: 104, height: 20 }, shape },
		{ text: 'rounding', box: { x: 0, y: 0, width: 100.4, height: 40 }, shape },
		{ text: 'no box', box: { x: 500, y: 5, width: 50, height: 30 }, shape: null },
	];
	assert.deepEqual(labelProblems(texts), [{ text: 'wide', by: 2 }]);
	assert.deepEqual(drawingReport('core/time/ [light] diagram 1', { labels: labelProblems(texts), contrasts: [] }), ['core/time/ [light] diagram 1: the label "wide" leaves its box by 2.0 px']);
});

test('each text\'s contrast against what is behind it; a fill that is not opaque is drawn over it first', () => {
	const behind = () => ({ r: 255, g: 255, b: 255, a: 1 });
	const results = textContrasts([
		{ text: 'dark', box: {}, fill: 'rgb(0, 0, 0)', opacity: 1 },
		{ text: 'faint', box: {}, fill: 'rgb(0, 0, 0)', opacity: 0.2 },
		{ text: 'nothing', box: {}, fill: 'none', opacity: 1 },
	], behind);
	assert.deepEqual(results.map((item) => item.text), ['dark', 'faint']);
	assert.equal(results[0].ratio, 21);
	assert.ok(results[1].ratio < c_MinimumContrast);
	assert.deepEqual(drawingReport('x', { labels: [], contrasts: results }), [`x: "faint" stands at ${results[1].ratio.toFixed(2)}:1 against its background (at least 4.5:1): #cccccc on #ffffff`]);
});

test('a diagram\'s figure has a caption and an image with the fence\'s alt text as its name', () => {
	assert.deepEqual(figureProblems({ caption: 'What to notice.', role: 'img', label: 'What it shows.', title: 'What it shows.' }), []);
	assert.match(figureProblems({ caption: ' ', role: 'img', label: 'A.', title: 'A.' })[0], /no caption/);
	assert.match(figureProblems({ caption: 'C.', role: 'graphics-document document', label: 'A.', title: 'A.' })[0], /not an image with an accessible name/);
	assert.match(figureProblems({ caption: 'C.', role: 'img', label: '', title: '' })[0], /not an image with an accessible name/);
	assert.match(figureProblems({ caption: 'C.', role: 'img', label: 'A.', title: 'B.' })[0], /<title> does not say what its aria-label says/);
});

test('the pages of a build that hold a diagram, print views included, outside the build\'s own folders', () => {
	const book = makeBook({});
	try {
		const dist = path.join(book.root, 'dist');
		const files = {
			'index.html': '<p>No diagram.</p>',
			'core/time/index.html': '<figure class="book-diagram"></figure>',
			'print/core/index.html': '<figure class="book-diagram"></figure>',
			'world/ecs/index.html': '<figure class="book-figure"></figure>',
			'_astro/index.html': '<figure class="book-diagram"></figure>',
		};
		for (const [relative, content] of Object.entries(files)) {
			mkdirSync(path.dirname(path.join(dist, relative)), { recursive: true });
			writeFileSync(path.join(dist, relative), content);
		}
		assert.deepEqual(diagramPages(dist), ['core/time/', 'print/core/']);
		assert.deepEqual(diagramPages(path.join(book.root, 'nowhere')), []);
	} finally {
		book.remove();
	}
});

// The sample pages' placeholder pictures (scripts/placeholders.mjs: published as tools/figures.py publishes a picture)
// and the measure of crops at whole factors (scripts/crops.mjs, gate (b)).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { cropPages, cropProblem, expectedFactor } from '../../../scripts/crops.mjs';
import { c_Pictures, encoderArguments, onSlider, placeholderJobs } from '../../../scripts/placeholders.mjs';
import { makeBook } from './helpers.mjs';

test('a crop is shown at the largest whole factor up to its scale that its column holds', () => {
	assert.equal(expectedFactor({ natural: 240, scale: 3, column: 736 }), 3);
	assert.equal(expectedFactor({ natural: 240, scale: 3, column: 632 }), 2);
	assert.equal(expectedFactor({ natural: 240, scale: 3, column: 343 }), 1);
	// Narrower than the crop: its own width, and the box scrolls.
	assert.equal(expectedFactor({ natural: 240, scale: 3, column: 200 }), 1);
	assert.equal(expectedFactor({ natural: 240, scale: 2, column: 2000 }), 2);
	assert.equal(cropProblem({ rendered: 480, natural: 240, scale: 3, column: 632, rendering: 'pixelated' }), null);
	assert.match(cropProblem({ rendered: 400, natural: 240, scale: 3, column: 632, rendering: 'pixelated' }), /1\.667 times its own 240 px: not a whole factor/);
	assert.match(cropProblem({ rendered: 240, natural: 240, scale: 3, column: 632, rendering: 'pixelated' }), /shown at 1 times its own width; its column of 632 px holds 2/);
	assert.match(cropProblem({ rendered: 480, natural: 240, scale: 3, column: 632, rendering: 'auto' }), /smoothed \(image-rendering: auto\)/);
	assert.match(cropProblem({ rendered: 0, natural: 0, scale: 3, column: 632, rendering: 'pixelated' }), /did not load/);
});

test('the pages of a build that show a crop', () => {
	const book = makeBook({});
	try {
		const dist = path.join(book.root, 'dist');
		for (const [relative, content] of Object.entries({ 'make/first-script/index.html': '<img class="book-crop__img">', 'core/time/index.html': '<img>', '_figures/index.html': 'book-crop__img' })) {
			mkdirSync(path.dirname(path.join(dist, relative)), { recursive: true });
			writeFileSync(path.join(dist, relative), content);
		}
		assert.deepEqual(cropPages(dist), ['make/first-script/']);
	} finally {
		book.remove();
	}
});

test('placeholders are published as their recipes say: AVIF at 80, or 90 on a slider, and crops as lossless WebP', () => {
	const recipes = {
		'src/content/figures/core/time.json': JSON.stringify({ figures: [{ id: 'pair', kind: 'live', variants: { off: {}, on: {} } }] }),
		'src/content/figures/make/first-script.json': JSON.stringify({ figures: [{ id: 'cube', kind: 'scene', crops: [{ name: 'edge', rect: [0.4375, 0.5, 0.5625, 0.625], scale: 3 }] }, { id: 'ui', kind: 'editor' }] }),
	};
	const book = makeBook({ files: recipes });
	try {
		const folder = (page) => path.join(book.root, 'src', 'assets', 'figures', ...page.split('/'));
		const slider = placeholderJobs(book.root, { page: 'core/time', figure: 'pair', variant: 'on' }, 'Text.\n\n::compare{id=pair}\n');
		assert.deepEqual(slider.jobs.map((job) => [path.relative(folder('core/time'), job.output), job.publish, job.quality]), [['pair-on.avif', 'lossy', 90]]);
		const cube = placeholderJobs(book.root, { page: 'make/first-script', figure: 'cube', variant: null }, '::figure{id=cube}\n');
		assert.deepEqual(cube.jobs.map((job) => [path.relative(folder('make/first-script'), job.output), job.publish, job.quality, job.crop]), [
			['cube.avif', 'lossy', 80, null],
			['cube-edge.webp', 'lossless', null, { left: 840, top: 540, width: 240, height: 135 }],
		]);
		const ui = placeholderJobs(book.root, { page: 'make/first-script', figure: 'ui', variant: null }, '');
		assert.deepEqual(ui.jobs.map((job) => [job.publish, job.quality]), [['lossless', null]]);
		assert.deepEqual(encoderArguments(cube.jobs[0], 'in.png').slice(1), ['encode', '--publish', 'lossy', '--quality', '80', 'in.png', cube.jobs[0].output]);
		assert.deepEqual(encoderArguments(cube.jobs[1], 'in.png').slice(1), ['encode', '--publish', 'lossless', 'in.png', cube.jobs[1].output]);
		assert.match(encoderArguments(cube.jobs[0], 'in.png')[0], /scripts[\\/]encode-figures\.mjs$/);
		assert.throws(() => placeholderJobs(book.root, { page: 'core/time', figure: 'pair', variant: 'maybe' }, ''), /has no variant "maybe"/);
		assert.throws(() => placeholderJobs(book.root, { page: 'core/time', figure: 'none', variant: null }, ''), /has no figure "none"/);
	} finally {
		book.remove();
	}
});

test('a slider is found in its page however its attributes are written; the sample\'s placeholders name their recipes', () => {
	assert.equal(onSlider('::compare{id=pair}', 'pair'), true);
	assert.equal(onSlider('  ::compare{before=off id="pair" after=on}', 'pair'), true);
	assert.equal(onSlider('::compare{id=pairs}', 'pair'), false);
	assert.equal(onSlider('::figure{id=pair variant=off}', 'pair'), false);
	for (const picture of c_Pictures) assert.ok(picture.page && picture.figure && picture.body && picture.label);
});

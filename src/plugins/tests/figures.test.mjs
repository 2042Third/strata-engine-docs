// Pictures (plan/site.md "Pictures"): one published file per picture, in the format its recipe says, its stamp in
// taken.json, the files the site serves (the published file under its hash, and a 960-pixel AVIF beside a lossy one),
// crops shown at whole factors, sliders, placeholders, and the errors a writer meets.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import sharp from 'sharp';
import { cropPixels, figureAnchor, pictureName, promisedPictures, publishOf, resolveCrop, strayPictures } from '../../lib/figures.mjs';
import { c_EncoderKey, derivedWidths, describePicture, servedAs, servedFiles, sniffFormat } from '../../lib/images.mjs';
import { c_FirstScreenCharacters, c_Sizes } from '../figures.mjs';
import { c_BottomStrip, c_ReferenceStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const recipe = (extra = {}) => ({ id: 'shot', shows: 'A cube.', kind: 'scene', caption: 'Notice the cube.', alt: 'A grey cube.', size: [1920, 1080], ...extra });
const manifest = (...figures) => JSON.stringify({ figures });
const c_Folder = 'src/assets/figures/core/time';

/** Writes a picture into a test book's pictures folder; returns its SHA-256. */
async function writePicture(root, name, { width = 1920, height = 1080, format = path.extname(name).slice(1), lossless = format === 'webp', background = { r: 90, g: 120, b: 160 } } = {}) {
	const file = path.join(root, ...c_Folder.split('/'), name);
	mkdirSync(path.dirname(file), { recursive: true });
	const pipeline = sharp({ create: { width, height, channels: 3, background } });
	if (format === 'avif') await pipeline.avif({ quality: 80, effort: 0 }).toFile(file);
	else if (format === 'webp') await pipeline.webp(lossless ? { lossless: true } : { quality: 80 }).toFile(file);
	else await pipeline.png().toFile(file);
	return createHash('sha256').update(readFileSync(file)).digest('hex');
}

function writeTaken(root, files) {
	const file = path.join(root, ...c_Folder.split('/'), 'taken.json');
	mkdirSync(path.dirname(file), { recursive: true });
	writeFileSync(file, JSON.stringify({ files }));
}

const page = (body, overrides = {}) => `${frontmatter(overrides)}\n${body}\n${c_BottomStrip}`;

test('one format per picture: lossy renders are AVIF, the interface and crops lossless WebP, drawings SVG', () => {
	assert.equal(publishOf(recipe()), 'lossy');
	assert.equal(publishOf(recipe({ publish: 'lossless' })), 'lossless');
	assert.equal(publishOf(recipe({ kind: 'editor' })), 'lossless');
	assert.equal(publishOf(recipe({ kind: 'tool' })), 'lossless');
	// An interface picture that is mostly the engine's image may say lossy (rulings-13, R59); its crops stay lossless.
	assert.equal(publishOf(recipe({ kind: 'editor', publish: 'lossy' })), 'lossy');
	assert.equal(pictureName(recipe({ kind: 'editor', publish: 'lossy' })), 'shot.avif');
	assert.equal(pictureName(recipe({ kind: 'editor', publish: 'lossy' }), null, 'chip'), 'shot-chip.webp');
	assert.equal(publishOf(recipe({ kind: 'diagram' })), 'svg');
	assert.equal(publishOf(recipe({ kind: 'text' })), 'text');
	assert.equal(pictureName(recipe()), 'shot.avif');
	assert.equal(pictureName(recipe(), 'off'), 'shot-off.avif');
	assert.equal(pictureName(recipe(), 'off', 'poles'), 'shot-off-poles.webp');
	assert.equal(pictureName(recipe({ kind: 'editor' })), 'shot.webp');
	assert.equal(pictureName(recipe({ kind: 'diagram' })), 'shot.svg');
	const entry = recipe({ variants: { off: {}, on: {} }, crops: [{ name: 'poles', rect: [0, 0, 0.5, 0.5], scale: 2 }] });
	assert.deepEqual(promisedPictures(entry).map((picture) => picture.name), ['shot-off.avif', 'shot-off-poles.webp', 'shot-on.avif', 'shot-on-poles.webp']);
	assert.deepEqual(promisedPictures(recipe({ kind: 'text' })), []);
});

test('a crop is its rectangle at the picture\'s own pixels, cut as tools/figures.py cuts it', () => {
	assert.deepEqual(cropPixels([0.4375, 0.5, 0.5625, 0.625], 1920, 1080), [840, 540, 1080, 675]);
	// Rounded toward zero, as Python's int() does.
	assert.deepEqual(cropPixels([0.1, 0.1, 0.2, 0.2], 1001, 333), [100, 33, 200, 66]);
});

test('the crop a directive names: by name, or bare when the recipe has one; a shot\'s crops come from taken.json', () => {
	const one = recipe({ crops: [{ name: 'poles', rect: [0, 0, 0.5, 0.5], scale: 2 }] });
	const two = recipe({ crops: [{ name: 'poles', rect: [0, 0, 0.5, 0.5], scale: 2 }, { name: 'fence', rect: [0.5, 0.5, 1, 1], scale: 4 }] });
	assert.equal(resolveCrop(one, '', null, null).crop.name, 'poles');
	assert.equal(resolveCrop(two, 'fence', null, null).crop.scale, 4);
	assert.match(resolveCrop(two, '', null, null).error, /has the crops poles, fence: name one with crop=<name>/);
	assert.match(resolveCrop(two, 'wire', null, null).error, /has no crop "wire" \(it has poles, fence\)/);
	assert.match(resolveCrop(recipe(), 'poles', null, null).error, /has no crops in its recipe/);
	const shot = recipe({ shot: 'lookdev.thin' });
	assert.deepEqual(resolveCrop(shot, 'fence', null, null).crop, { name: 'fence', scale: 4, rect: null });
	const taken = { files: new Map([['shot-fence.webp', { figure: 'shot', variant: null, crop: 'fence', sha256: '0'.repeat(64) }]]) };
	assert.equal(resolveCrop(shot, '', taken, null).crop.name, 'fence');
	assert.match(resolveCrop(shot, '', null, null).error, /takes its crops from the shot lookdev\.thin/);
	assert.deepEqual(promisedPictures(shot, taken).map((picture) => picture.name), ['shot.avif', 'shot-fence.webp']);
});

test('a crop\'s id on its page carries the crop\'s name', () => {
	const used = new Set();
	assert.equal(figureAnchor(used, { name: 'figure', attributes: { id: 'shot' } }), 'fig-shot');
	assert.equal(figureAnchor(used, { name: 'figure', attributes: { id: 'shot', crop: 'poles' } }), 'fig-shot-poles');
	assert.equal(figureAnchor(used, { name: 'figure', attributes: { id: 'shot', variant: 'off', crop: '' } }), 'fig-shot-off-crop');
});

test('the format of a picture is read from its bytes', async () => {
	const avif = await sharp({ create: { width: 8, height: 8, channels: 3, background: '#808080' } }).avif({ effort: 0 }).toBuffer();
	const lossy = await sharp({ create: { width: 8, height: 8, channels: 3, background: '#808080' } }).webp({ quality: 50 }).toBuffer();
	const lossless = await sharp({ create: { width: 8, height: 8, channels: 3, background: '#808080' } }).webp({ lossless: true }).toBuffer();
	const alpha = await sharp({ create: { width: 8, height: 8, channels: 4, background: { r: 1, g: 2, b: 3, alpha: 0.5 } } }).webp({ lossless: true }).toBuffer();
	const png = await sharp({ create: { width: 8, height: 8, channels: 3, background: '#808080' } }).png().toBuffer();
	assert.deepEqual(sniffFormat(avif), { format: 'avif', lossless: null });
	assert.deepEqual(sniffFormat(lossy), { format: 'webp', lossless: false });
	assert.deepEqual(sniffFormat(lossless), { format: 'webp', lossless: true });
	assert.equal(sniffFormat(alpha).lossless, true);
	assert.equal(sniffFormat(png).format, 'png');
	assert.equal(sniffFormat(Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"></svg>')).format, 'svg');
	assert.equal(sniffFormat(Buffer.from('not a picture at all')), null);
});

test('the files served for a picture: the published file under its hash, and the AVIFs derived from a lossy one', () => {
	assert.deepEqual(derivedWidths(1920), [960]);
	assert.deepEqual(derivedWidths(3840), [960, 1920]);
	assert.deepEqual(derivedWidths(960), []);
	const hash = 'abcdef0123456789'.repeat(4);
	const lossy = servedFiles({ base: '/book', cacheDir: '/cache', outputDir: '/dist' }, { file: 'x.avif', hash, width: 1920, height: 1080, format: 'avif' }, 'core/time/shot.avif');
	assert.deepEqual(lossy.map((file) => [file.kind, file.url, file.width, file.height]), [
		['published', '/book/_figures/core/time/shot.abcdef0123.1920.avif', 1920, 1080],
		['derived', '/book/_figures/core/time/shot.abcdef0123.960.avif', 960, 540],
	]);
	assert.equal(lossy[0].output, path.join('/dist', '_figures', 'core', 'time', 'shot.abcdef0123.1920.avif'));
	assert.equal(lossy[1].cache, path.join('/cache', 'images', `${hash}-${c_EncoderKey}-960.avif`));
	const large = servedFiles({ base: '', cacheDir: '/cache' }, { file: 'x.avif', hash, width: 3840, height: 2160, format: 'avif' }, 'core/time/shot.avif');
	assert.deepEqual(large.map((file) => file.width), [3840, 960, 1920]);
	const lossless = servedFiles({ base: '', cacheDir: '/cache' }, { file: 'x.webp', hash, width: 240, height: 135, format: 'webp' }, 'core/time/shot-poles.webp');
	assert.deepEqual(lossless.map((file) => [file.kind, file.url]), [['published', '/_figures/core/time/shot-poles.abcdef0123.240.webp']]);
});

test('pictures with the same bytes are served once, under the name of the first in path order', async () => {
	const root = mkdtempSync(path.join(tmpdir(), 'strata-twins-'));
	try {
		const write = async (relative, background) => {
			const file = path.join(root, ...relative.split('/'));
			mkdirSync(path.dirname(file), { recursive: true });
			await sharp({ create: { width: 64, height: 36, channels: 3, background } }).webp({ lossless: true }).toFile(file);
			return file;
		};
		const twin = (from, relative) => {
			const file = path.join(root, ...relative.split('/'));
			mkdirSync(path.dirname(file), { recursive: true });
			copyFileSync(from, file);
			return file;
		};
		const first = await write('light/sky/after.webp', { r: 90, g: 120, b: 160 });
		const second = twin(first, 'image/grading/off.webp');
		const other = await write('image/grading/on.webp', { r: 200, g: 120, b: 40 });
		assert.equal(await servedAs(root, 'light/sky/after.webp', await describePicture(first)), 'image/grading/off.webp');
		assert.equal(await servedAs(root, 'image/grading/off.webp', await describePicture(second)), 'image/grading/off.webp');
		assert.equal(await servedAs(root, 'image/grading/on.webp', await describePicture(other)), 'image/grading/on.webp');
		// A twin published after the folder was listed is found: the list is made again for a path it lacks.
		const late = twin(first, 'core/time/late.webp');
		assert.equal(await servedAs(root, 'core/time/late.webp', await describePicture(late)), 'core/time/late.webp');
		assert.equal(await servedAs(root, 'light/sky/after.webp', await describePicture(first)), 'core/time/late.webp');
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('a figure whose picture is not taken yet is a labelled placeholder in drafts and fails a release', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(recipe()) } });
	try {
		const out = await render(book.root, 'core/time');
		assert.match(out, /<figure class="book-figure" id="fig-shot"><div class="book-placeholder" role="img" aria-label="A grey cube\." style="aspect-ratio: 1920 \/ 1080">/);
		assert.match(out, /Picture not taken yet/);
		assert.match(out, /<figcaption>Notice the cube\./);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /has no picture src\/assets\/figures\/core\/time\/shot\.avif yet/);
	} finally {
		book.remove();
	}
});

test('a figure no take makes at the pin stays a placeholder in drafts, and a release names the stand-in its page places instead', async () => {
	const waiting = recipe({ waitsFor: 'tier 3: a menu held open; no command opens it', standIn: 'menu-drawing' });
	const blocked = recipe({ id: 'gone', blocked: 'the pin has no wind zone, so no take can show one' });
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}\n\n::figure{id=gone}') }, files: { 'src/content/figures/core/time.json': manifest(waiting, blocked) } });
	try {
		const out = await render(book.root, 'core/time');
		assert.match(out, /Picture not taken yet/);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }),
			/figure "shot" waits for tier 3: a menu held open; no command opens it, so a release would show a placeholder: place its stand-in ::figure\{id=menu-drawing\} in its place/);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /figure "gone" is blocked: the pin has no wind zone, so no take can show one, so a release would show a placeholder/);
	} finally {
		book.remove();
	}
});

test('a lossy picture is its AVIF with the 960-pixel AVIF in its srcset; the first picture of a page loads at once', async () => {
	const entry = recipe({ variants: undefined });
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}\n\n::figure{id=other}') }, files: { 'src/content/figures/core/time.json': manifest(entry, recipe({ id: 'other' })) } });
	try {
		await writePicture(book.root, 'shot.avif');
		// Another picture: one with the same bytes would be served under the first name in path order (servedAs).
		await writePicture(book.root, 'other.avif', { background: { r: 160, g: 120, b: 90 } });
		const out = await render(book.root, 'core/time');
		assert.match(out, /<a class="book-figure__zoom" href="\/book\/_figures\/core\/time\/shot\.[0-9a-f]{10}\.1920\.avif"><img src="\/book\/_figures\/core\/time\/shot\.[0-9a-f]{10}\.1920\.avif" width="1920" height="1080" alt="A grey cube\." decoding="async" loading="eager" fetchpriority="high" srcset="\/book\/_figures\/core\/time\/shot\.[0-9a-f]{10}\.960\.avif 960w, \/book\/_figures\/core\/time\/shot\.[0-9a-f]{10}\.1920\.avif 1920w" sizes="\(min-width: 91\.5rem\) 48rem, [^"]+, calc\(100vw - 2rem\)"><\/a>/);
		assert.match(out, /<img src="\/book\/_figures\/core\/time\/other\.[0-9a-f]{10}\.1920\.avif" width="1920" height="1080" alt="A grey cube\." decoding="async" loading="lazy" srcset=/);
		assert.equal(out.match(/fetchpriority/g).length, 1);
		assert.doesNotMatch(out, /<picture|\.webp/);
		// Without a stamp in taken.json the picture is a placeholder: labelled in a draft, refused by a release.
		assert.match(out, /Placeholder picture/);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /shot\.avif is a placeholder picture: taken\.json has no stamp for it/);
	} finally {
		book.remove();
	}
});

/** The width in CSS pixels that a `sizes` attribute gives at a viewport `width` (rem is 16 px; lengths, rem and calc of vw and rem). */
function sizesWidth(sizes, width) {
	const length = (value) => {
		const sum = value.match(/^calc\((\d+(?:\.\d+)?)vw ([+-]) (\d+(?:\.\d+)?)rem\)$/);
		if (sum) return (Number(sum[1]) * width) / 100 + (sum[2] === '+' ? 1 : -1) * Number(sum[3]) * 16;
		const rem = value.match(/^(\d+(?:\.\d+)?)rem$/);
		if (rem) return Number(rem[1]) * 16;
		throw new Error(`a length this test cannot read: ${value}`);
	};
	for (const candidate of sizes.split(', ')) {
		const condition = candidate.match(/^\(min-width: (\d+(?:\.\d+)?)rem\) (.+)$/);
		if (!condition) return length(candidate);
		if (width >= Number(condition[1]) * 16) return length(condition[2]);
	}
	throw new Error('sizes has no last candidate without a condition');
}

test('sizes gives the width of the content column, so a phone picks a small candidate', () => {
	// The figure's width in the built site (Playwright, 2026-11-25): the whole viewport less its padding up to 50rem,
	// then the sidebar beside it, then the table of contents from 72rem, and at most 48rem.
	const measured = { 320: 288, 412: 380, 640: 608, 799: 767, 800: 468, 1000: 668, 1100: 768, 1151: 768, 1152: 504, 1280: 632, 1368: 720, 1400: 736, 1464: 768, 1600: 768, 1920: 768 };
	for (const [viewport, column] of Object.entries(measured)) assert.equal(sizesWidth(c_Sizes, Number(viewport)), column, `viewport ${viewport}`);
	// A phone of Lighthouse's (412 pixels at 1.75 device pixels per pixel) needs 665 pixels: the 960-pixel candidate.
	assert.ok(sizesWidth(c_Sizes, 412) * 1.75 < 960);
});

test('a first picture in the first screen loads at once at high priority; pictures below it and a slider\'s second side when near', async () => {
	// Lighthouse counts every request that starts before the page's largest paint: a picture below the first screen
	// that loads at once (measured: a 7 MB lossless picture on image/spatial-aa) moves the largest paint by its download.
	const entry = recipe({ variants: { off: {}, on: {} } });
	const prose = (characters) => `${'Words of the page before the picture. '.repeat(Math.ceil(characters / 38))}
`;
	const book = makeBook({
		pages: { 'core/time': page(`${prose(c_FirstScreenCharacters + 100)}
::figure{id=still}

::figure{id=again}`), 'core/frame': page('::compare{id=shot}') },
		files: { 'src/content/figures/core/time.json': manifest(recipe({ id: 'still' }), recipe({ id: 'again' })), 'src/content/figures/core/frame.json': manifest(entry) },
	});
	try {
		await writePicture(book.root, 'still.avif');
		await writePicture(book.root, 'again.avif', { background: { r: 160, g: 120, b: 90 } });
		const out = await render(book.root, 'core/time');
		assert.match(out, /<img src="[^"]+\/still\.[0-9a-f]{10}\.1920\.avif" [^>]*decoding="async" loading="lazy" srcset=/);
		assert.match(out, /<img src="[^"]+\/again\.[0-9a-f]{10}\.1920\.avif" [^>]*decoding="async" loading="lazy" srcset=/);
		assert.doesNotMatch(out, /fetchpriority/);
		const folder = path.join(book.root, 'src', 'assets', 'figures', 'core', 'frame');
		mkdirSync(folder, { recursive: true });
		for (const [side, red] of [['off', 90], ['on', 200]]) {
			await writePicture(book.root, `shot-${side}.avif`, { background: { r: red, g: 120, b: 160 } });
			copyFileSync(path.join(book.root, ...c_Folder.split('/'), `shot-${side}.avif`), path.join(folder, `shot-${side}.avif`));
		}
		const pair = await render(book.root, 'core/frame');
		assert.match(pair, /<img src="[^"]+\/shot-off\.[0-9a-f]{10}\.1920\.avif" [^>]*loading="eager" fetchpriority="high"/);
		assert.match(pair, /<img src="[^"]+\/shot-on\.[0-9a-f]{10}\.1920\.avif" [^>]*loading="lazy"/);
	} finally {
		book.remove();
	}
});

test('a lossless picture is served alone, without derived files', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(recipe({ kind: 'editor' })) } });
	try {
		await writePicture(book.root, 'shot.webp');
		const out = await render(book.root, 'core/time');
		assert.match(out, /<img src="\/book\/_figures\/core\/time\/shot\.[0-9a-f]{10}\.1920\.webp" width="1920" height="1080" alt="A grey cube\." decoding="async" loading="eager" fetchpriority="high">/);
		assert.doesNotMatch(out, /srcset/);
	} finally {
		book.remove();
	}
});

test('a stamped picture is drawn without a label; one whose SHA-256 differs from its stamp fails', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}', { status: 'final' }) }, files: { 'src/content/figures/core/time.json': manifest(recipe()) } });
	try {
		const hash = await writePicture(book.root, 'shot.avif');
		writeTaken(book.root, { 'shot.avif': { figure: 'shot', variant: null, crop: null, sha256: hash } });
		assert.doesNotMatch(await render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /Placeholder picture/);
		writeTaken(book.root, { 'shot.avif': { figure: 'shot', variant: null, crop: null, sha256: '0'.repeat(64) } });
		await rejectsWith(render(book.root, 'core/time'), /is not the file the engine took/);
		writeTaken(book.root, { 'shot.avif': { figure: 'shot' } });
		await rejectsWith(render(book.root, 'core/time'), /the stamp of shot\.avif has no "sha256"/);
		writeFileSync(path.join(book.root, ...c_Folder.split('/'), 'taken.json'), '{ not json');
		await rejectsWith(render(book.root, 'core/time'), /taken\.json is not valid JSON/);
	} finally {
		book.remove();
	}
});

test('a picture in another format than its recipe\'s fails, and PNG is never published', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}\n\n::figure{id=ui}') }, files: { 'src/content/figures/core/time.json': manifest(recipe(), recipe({ id: 'ui', kind: 'editor' })) } });
	try {
		await writePicture(book.root, 'shot.webp');
		await writePicture(book.root, 'shot.png');
		await writePicture(book.root, 'ui.webp', { lossless: false });
		const error = await rejectsWith(render(book.root, 'core/time'), /shot\.webp: figure "shot" is published as shot\.avif \(AVIF \(a lossy picture\)\): remove shot\.webp/, /shot\.png: .*; PNG is not a published format: remove shot\.png/, /ui\.webp is a lossy WebP file: these pictures are lossless WebP/);
		assert.match(error.message, /Picture not taken yet|core\/time/);
		// A file whose bytes are not what its name says.
		await writePicture(book.root, 'shot.avif', { format: 'png' });
		await rejectsWith(render(book.root, 'core/time'), /shot\.avif is a PNG file, not what its name says/);
	} finally {
		book.remove();
	}
});

test('a crop is lossless WebP at its own pixels, enlarged by the style sheet at whole factors up to its scale', async () => {
	const entry = recipe({ crops: [{ name: 'detail', rect: [0.25, 0.25, 0.375, 0.375], scale: 3 }] });
	const book = makeBook({ pages: { 'core/time': page(':::figure{id=shot crop=detail}\nThe edge, closer.\n:::') }, files: { 'src/content/figures/core/time.json': manifest(entry) } });
	try {
		let out = await render(book.root, 'core/time');
		// Not taken yet: the placeholder keeps the crop's shape.
		assert.match(out, /<figure class="book-figure book-figure--crop" id="fig-shot"><div class="book-placeholder" role="img" aria-label="A grey cube\." style="aspect-ratio: 240 \/ 135"><strong class="book-placeholder__title">Crop not taken yet/);
		await writePicture(book.root, 'shot-detail.webp', { width: 240, height: 135 });
		out = await render(book.root, 'core/time');
		assert.match(out, /<div class="book-crop" style="--book-crop-width: 240px; --book-crop-scale: 3"><a class="book-figure__zoom" href="\/book\/_figures\/core\/time\/shot-detail\.[0-9a-f]{10}\.240\.webp"><img src="\/book\/_figures\/core\/time\/shot-detail\.[0-9a-f]{10}\.240\.webp" width="240" height="135" alt="A grey cube\." decoding="async" loading="eager" fetchpriority="high" class="book-crop__img"><\/a><\/div>/);
		// The figure's body follows the recipe's caption, and the draft label comes last.
		assert.match(out, /<figcaption>Notice the cube\. The edge, closer\. <span class="book-draft-label">/);
		const css = readFileSync(new URL('../../styles/book.css', import.meta.url), 'utf8');
		assert.match(css, /\.book-figure--crop \{\s*container-type: inline-size;/);
		assert.match(css, /width: clamp\(var\(--book-crop-width\), round\(down, 100cqi, var\(--book-crop-width\)\), calc\(var\(--book-crop-width\) \* var\(--book-crop-scale\)\)\);/);
		assert.match(css, /image-rendering: pixelated;/);
		assert.match(css, /\.book-crop \{\s*overflow-x: auto;/);
	} finally {
		book.remove();
	}
});

test('a crop must be one of its recipe\'s', async () => {
	const two = recipe({ crops: [{ name: 'a', rect: [0, 0, 0.5, 0.5], scale: 2 }, { name: 'b', rect: [0.5, 0.5, 1, 1], scale: 2 }] });
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot crop}\n\n::figure{id=shot crop=c}\n\n::figure{id=plain crop=a}') }, files: { 'src/content/figures/core/time.json': manifest(two, recipe({ id: 'plain' })) } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /has the crops a, b: name one with crop=<name>/, /has no crop "c" \(it has a, b\)/, /figure "plain" has no crops in its recipe/);
	} finally {
		book.remove();
	}
});

test('a recipe\'s crops are named rectangles with whole scales, and the spike\'s fields are refused with what to write', async () => {
	const bad = recipe({ crops: [{ name: 'Bad Name', rect: [0.5, 0, 0.2, 1], scale: 1.5 }], crop: { rect: [0, 0, 320, 180], scale: 2 }, taken: { sha256: {} } });
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(bad) } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /a crop's "name" is a lowercase word/, /needs "rect": \[x0, y0, x1, y1\] from 0 to 1, with x0 < x1/, /needs a whole "scale" from 1 to 8/, /has the field "crop", which recipes no longer have: crops are named/, /has the field "taken", which recipes no longer have: stamps live in taken\.json/);
	} finally {
		book.remove();
	}
});

test('a drawing passes a release build without a stamp; a stamp, or SVG for a render, fails', async () => {
	// No engine takes a drawing: it is final when its page is (a release refuses draft pages).
	const final = page('::figure{id=drawing}', { status: 'final' });
	const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20"><rect width="40" height="20"/></svg>';
	const drawing = recipe({ id: 'drawing', kind: 'diagram', size: [40, 20] });
	const book = makeBook({ pages: { 'core/time': final }, files: { 'src/content/figures/core/time.json': manifest(drawing), [`${c_Folder}/drawing.svg`]: svg } });
	try {
		const out = await render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } });
		assert.match(out, /<div class="book-figure__drawing" role="img" aria-label="A grey cube\." tabindex="0"><svg/);
		assert.doesNotMatch(out, /Placeholder picture/);
		writeTaken(book.root, { 'drawing.svg': { figure: 'drawing', sha256: '0'.repeat(64) } });
		await rejectsWith(render(book.root, 'core/time'), /is a drawing, which no engine takes: its file needs no stamp/);
	} finally {
		book.remove();
	}
	const notDrawing = makeBook({ pages: { 'core/time': final }, files: { 'src/content/figures/core/time.json': manifest(recipe({ id: 'drawing' })), [`${c_Folder}/drawing.svg`]: svg } });
	try {
		await rejectsWith(render(notDrawing.root, 'core/time'), /drawing\.svg: figure "drawing" is published as drawing\.avif/);
	} finally {
		notDrawing.remove();
	}
});

test('the build\'s own words in placeholders and labels get no glossary links', async () => {
	const glossary = { terms: [{ id: 'picture', term: 'picture', definition: 'An image of the book.', home: 'world/ecs' }, { id: 'engine', term: 'engine', definition: 'The program.', home: 'world/ecs' }] };
	const book = makeBook({
		glossary,
		pages: { 'core/time': page('::figure{id=shot}'), 'reference/glossary': `${frontmatter({ kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\n::glossary\n${c_ReferenceStrip}` },
		files: { 'src/content/figures/core/time.json': manifest(recipe({ shows: 'The engine draws a picture.' })) },
	});
	try {
		const out = await render(book.root, 'core/time');
		assert.match(out, /Picture not taken yet/);
		assert.doesNotMatch(out, /book-term/);
	} finally {
		book.remove();
	}
});

test('compare draws two variants named after the variants; its sides must be the same size and encoded alike', async () => {
	const entry = recipe({ variants: { off: {}, on: {} } });
	const book = makeBook({ pages: { 'core/time': page('::compare{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(entry) } });
	try {
		const off = await writePicture(book.root, 'shot-off.avif');
		const on = await writePicture(book.root, 'shot-on.avif');
		const out = await render(book.root, 'core/time');
		assert.match(out, /<figure class="book-figure book-compare" id="fig-shot"><book-compare><div class="book-compare__pair"><div class="book-compare__item" data-label="off">/);
		assert.match(out, /<span class="book-compare__label">on<\/span>/);
		assert.equal(out.match(/<img /g).length, 2);
		const encoder = (quality) => ({ format: 'avif', lossless: false, quality, chromaSubsampling: '4:4:4', effort: 4 });
		writeTaken(book.root, { 'shot-off.avif': { figure: 'shot', variant: 'off', sha256: off, encoder: encoder(90) }, 'shot-on.avif': { figure: 'shot', variant: 'on', sha256: on, encoder: encoder(80) } });
		await rejectsWith(render(book.root, 'core/time'), /the sides off and on were encoded with different settings/);
		writeTaken(book.root, {});
		await writePicture(book.root, 'shot-on.avif', { width: 1280, height: 720 });
		await rejectsWith(render(book.root, 'core/time'), /the sides off \(1920 × 1080\) and on \(1280 × 720\) differ in size/);
	} finally {
		book.remove();
	}
});

test('figure references must name a recipe, a variant when there are several, and known attributes', async () => {
	const entry = recipe({ variants: { off: {}, on: {} } });
	const body = '::figure{id=shot}\n\n::figure{id=nothing}\n\n::figure{id=shot variant=maybe}\n\n::compare{id=shot before=off after=off}\n\n::figure{name=x}\n\n::compare{id=shot crop=a}';
	const book = makeBook({ pages: { 'core/time': page(body) }, files: { 'src/content/figures/core/time.json': manifest(entry) } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /name one with variant=/, /has no figure "nothing"/, /has no variant "maybe"/, /needs two different variants/, /has no attribute "name"/, /::compare has no attribute "crop"/);
	} finally {
		book.remove();
	}
});

test('a figure without caption or alt text fails', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(recipe({ caption: '', alt: undefined })) } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /has no caption/, /has no alt text/);
	} finally {
		book.remove();
	}
});

test('a recipe used twice on a page gets two ids, as the page index says', async () => {
	const { collectAnchors } = await import('../../lib/pages.mjs');
	const { parseMarkdown } = await import('../../lib/markdown.mjs');
	const body = '::compare{id=shot}\n\n::figure{id=shot variant=off crop=detail}\n\n::figure{id=shot variant=on}\n\n::figure{id=shot variant=on}\n';
	const expected = ['fig-shot', 'fig-shot-off-detail', 'fig-shot-on', 'fig-shot-2'];
	assert.deepEqual([...collectAnchors(parseMarkdown(body))].filter((anchor) => anchor.startsWith('fig-')), expected);
	const entry = recipe({ variants: { off: {}, on: {} }, crops: [{ name: 'detail', rect: [0, 0, 0.25, 0.25], scale: 2 }] });
	const book = makeBook({ pages: { 'core/time': page(body) }, files: { 'src/content/figures/core/time.json': manifest(entry) } });
	try {
		const out = await render(book.root, 'core/time');
		assert.deepEqual([...out.matchAll(/<figure [^>]*id="([^"]+)"/g)].map((match) => match[1]), expected);
	} finally {
		book.remove();
	}
});

test('a leaf figure takes no label: its caption comes from the recipe', async () => {
	const book = makeBook({ pages: { 'core/time': page('::figure[My caption]{id=shot}') }, files: { 'src/content/figures/core/time.json': manifest(recipe()) } });
	try {
		const error = await rejectsWith(render(book.root, 'core/time'), /::figure\[…\] takes no label/);
		assert.doesNotMatch(error.message, /unknown directive/);
	} finally {
		book.remove();
	}
});

test('strayPictures names the files of a picture published in another format', async () => {
	const book = makeBook({});
	try {
		await writePicture(book.root, 'shot.webp');
		await writePicture(book.root, 'shot.png');
		await writePicture(book.root, 'shot-on.avif');
		assert.deepEqual(strayPictures(path.join(book.root, ...c_Folder.split('/')), 'shot.avif'), ['shot.png', 'shot.webp']);
		assert.deepEqual(strayPictures(path.join(book.root, 'nowhere'), 'shot.avif'), []);
	} finally {
		book.remove();
	}
});

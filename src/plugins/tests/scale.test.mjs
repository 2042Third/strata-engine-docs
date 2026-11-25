// The scale test's generator (scripts/scale.mjs): its totals add up, its quotes are in the excerpt tool's normal form,
// every page it writes for a row passes the book's plugins in the shape of its kind, every URL it leads to stays under
// the base at three bases, and its pictures are encoded in one format each, cut at whole pixels, stamped and cached.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cpSync, existsSync, mkdtempSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';
import { c_CodePairProse, c_CropRect, c_DirectiveLikeProse, c_Nouns, c_Totals, deal, generateBook, makePicture, normalizeQuote, planBook, proseWords, relativeLink, sketchOutput, stampRecord } from '../../../scripts/scale.mjs';
import { sniffFormat } from '../../lib/images.mjs';
import { parsePin } from '../../lib/settings.mjs';
import { c_License, c_SiteJson, render } from './helpers.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const c_Outline = JSON.parse(readFileSync(path.join(c_Root, 'src', 'generated', 'outline.json'), 'utf8'));
const c_Sidebar = JSON.parse(readFileSync(path.join(c_Root, 'src', 'sidebar.json'), 'utf8'));
const c_ReferenceDir = path.join(c_Root, 'src', 'generated', 'reference');
// The generated book copies the book's own reference tables, which name the pin they were rendered at: it takes the
// book's engine.pin with them, so that a pin move keeps the two equal.
const c_Pin = readFileSync(path.join(c_Root, 'engine.pin'), 'utf8');
const c_FakeFile = 'Strata/src/Strata/Fake/Fake.cpp';
// A file of the engine as the generator reads it: indented with tabs, with a preprocessor line at column 0 and blank
// lines, which no quote may start or end with (the build refuses them).
const c_FakeLines = Array.from({ length: 120 }, (_, i) => (i % 10 === 0 ? `#if ST_FAKE_${i}` : i % 3 === 1 ? '' : `\t\tint value${i} = ${i}; // line ${i + 1}`));

function inputs({ referenceFiles = new Set(readdirSync(c_ReferenceDir).filter((file) => file.endsWith('.md'))) } = {}) {
	return {
		outline: c_Outline,
		sidebar: c_Sidebar,
		seedTerms: [{ id: 'fixed-step', term: 'fixed step', definition: 'A slice of simulated time of one length.', home: 'core/time', aliases: [], avoid: [] }],
		queries: [{ kind: 'term', query: 'fixed step', page: 'core/time' }, { kind: 'name', query: 'ST_SCRIPT_CLASS', page: 'make/first-script' }, { kind: 'question', query: 'how do I install Strata', page: 'start/install' }],
		engineFiles: [c_FakeFile],
		engineLines: () => c_FakeLines,
		referenceFiles,
		sketchText: () => ['#include <cstdio>', 'int main() { std::puts("hello"); }'],
		sketchFile: () => '#include <cstdio>\nint main() { std::puts("hello"); }\n',
		sketchOutputs: new Map([['core-time-fixed-step.cpp', ['hello']], ['core-time-thirty-frames.cpp', ['hello']], ['world-interpolation-toy.cpp', ['hello']]]),
		pin: parsePin(c_Pin),
	};
}

test('deal splits a total over weights so the counts add up', () => {
	assert.deepEqual(deal(10, [1, 1, 2]), [3, 2, 5]);
	assert.equal(deal(1500, [3, 5, 8, 1.5, 3]).reduce((a, b) => a + b, 0), 1500);
	assert.deepEqual(deal(3, [0, 0]), [0, 0]);
});

test('a quote loses the common leading tabs and nothing else, as tools/excerpts.py fill writes it (pipelines.md §3.4)', () => {
	assert.deepEqual(normalizeQuote(['\t\tint a;', '', '#if X', '\t\t\tint b;']), ['int a;', '', '#if X', '\tint b;']);
	assert.deepEqual(normalizeQuote(['int a;', '\tint b;']), ['int a;', '\tint b;']);
	assert.deepEqual(normalizeQuote(['', '#define A']), ['', '#define A']);
});

test('prose words leave out fences, display math, tables and directive lines', () => {
	assert.equal(proseWords(['## Two words', 'one two three.', '```cpp', 'int a = 1;', '```', '$$', 'x = y', '$$', '| a | b |', ':::note', '- four five']), 7);
});

test('a sample page\'s sketch output is read without its indent', () => {
	const page = 'Text.\n\n   ```text output-of="core-time-thirty-frames.cpp"\n   frames: 30\n     steps: 2\n   ```\n';
	assert.deepEqual(sketchOutput(page, 'core-time-thirty-frames.cpp'), ['frames: 30', '  steps: 2']);
	assert.equal(sketchOutput(page, 'other.cpp'), null);
});

test('the plan of the book reaches every total of plan/site.md at full size', () => {
	const { shares } = planBook(c_Outline.pages, c_Totals, 1);
	const sum = (key) => [...shares.values()].reduce((total, share) => total + share[key], 0);
	assert.equal(sum('quotes'), c_Totals.quotes);
	assert.equal(sum('diagrams'), c_Totals.diagrams);
	const checkpoints = [...shares.values()].flatMap((share) => share.checkpoints);
	const editors = sum('editors') + checkpoints.filter((kind) => kind === 'editor').length;
	const renders = sum('renders') + 2 * sum('compares') + checkpoints.filter((kind) => kind === 'scene').length;
	assert.equal(editors, c_Totals.interface);
	assert.equal(renders, c_Totals.renders);
	assert.equal(sum('compares'), c_Totals.sliderPairs);
	assert.equal(sum('crops'), c_Totals.crops);
	for (const row of c_Outline.pages.filter((candidate) => candidate.kind === 'internals')) assert.ok(shares.get(row.id).quotes >= 3, `${row.id} quotes the engine three times (site.md P4)`);
	for (const row of c_Outline.pages.filter((candidate) => candidate.kind === 'reference')) assert.equal(shares.get(row.id).quotes + shares.get(row.id).renders, 0);
	const blocks = sum('quotes') + sum('fences') + [...shares.values()].reduce((total, share) => total + (share.sketch ? 2 : 0) + (share.tabs ? 3 : 0), 0);
	assert.equal(blocks, c_Totals.codeBlocks);
});

/** Writes a generated book with what the build reads besides its pages: the pin, site.json, the outline, the tables, the drawings. */
function writeBook(book) {
	const root = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'scale-test-'));
	const write = (relative, content) => {
		const file = path.join(root, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	};
	write('engine.pin', c_Pin);
	write('site.json', JSON.stringify(c_SiteJson));
	write('LICENSE', c_License);
	write('src/generated/outline.json', JSON.stringify(c_Outline));
	cpSync(c_ReferenceDir, path.join(root, 'src', 'generated', 'reference'), { recursive: true });
	for (const [relative, text] of book.files) write(relative, text);
	return { root, remove: () => rmSync(root, { recursive: true, force: true }) };
}

test('every page the generator writes for a row passes the book\'s plugins, and leads only to URLs under the base', async () => {
	const book = generateBook(inputs(), { seed: 3, fraction: 0.05 });
	assert.equal(book.counts.pages, c_Outline.pages.length);
	for (const row of c_Outline.pages) assert.ok(book.files.has(`src/content/docs/${row.id}.md`), `${row.id} is written`);
	for (const part of c_Outline.parts.filter((candidate) => candidate.partPages)) {
		assert.ok(book.files.has(`src/content/docs/${part.slug}/index.md`) && book.files.has(`src/content/docs/${part.slug}/review.md`), `${part.slug} has its part pages`);
	}
	const texts = [...book.files].filter(([relative]) => relative.endsWith('.md')).map(([, text]) => text).join('\n');
	assert.doesNotMatch(texts, /\]\(\//, 'no link is written from the root of the host');
	// No noun gets a plural that the spelling gate refuses (a "box" or a "copy" with a bare "s" added).
	const irregular = c_Nouns.filter((noun) => /(x|s|ch|sh|[^aeiou]y)$/.test(noun));
	assert.doesNotMatch(texts, new RegExp(`\\b(${irregular.join('|')})s\\b`));
	for (const match of texts.matchAll(/\]\((https?:\/\/[^)]+)\)/g)) assert.match(match[1], /^https:\/\/(en\.cppreference\.com|learn\.microsoft\.com|git-scm\.com|cmake\.org|gafferongames\.com)\//, `${match[1]} is a host of tools/external-hosts.txt`);
	// The drawings of the diagrams are committed files the build reads; a page with one is checked by the diagram tests.
	const sidebar = JSON.parse(book.files.get('src/sidebar.json'));
	assert.deepEqual(sidebar.tracks, c_Sidebar.tracks);
	const { root, remove } = writeBook(book);
	try {
		const kinds = new Map();
		for (const row of c_Outline.pages) {
			const text = book.files.get(`src/content/docs/${row.id}.md`);
			if (!kinds.has(row.kind) && !text.includes('```mermaid')) kinds.set(row.kind, row.id);
		}
		const pages = [...kinds.values(), 'make/first-script', 'reference/commands', 'reference/settings', 'reference/glossary', 'core/review'];
		for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y/', '/x/y']]) {
			for (const id of pages) {
				const html = await render(root, id, { env: { DOCS_BASE: setting } });
				for (const match of html.matchAll(/\s(?:href|src)="([^"]*)"/g)) {
					const url = match[1];
					if (/^(#|https:\/\/)/.test(url)) continue;
					assert.ok(url.startsWith(`${base}/`), `${id} at ${setting}: ${url} is under the base`);
				}
			}
		}
	} finally {
		remove();
	}
});

test('a tutorial gets one step section per checkpoint, each ending with its checkpoint and picture, and a tutorial file', () => {
	const book = generateBook(inputs(), { seed: 5, fraction: 0.05 });
	const text = book.files.get('src/content/docs/make/first-script.md');
	const tutorial = JSON.parse(book.files.get('tutorials/make/first-script.tutorial.json'));
	const sections = text.split('\n## ').slice(1).map((section) => section.split('\n')[0]);
	const steps = sections.slice(sections.indexOf('What you need') + 1, sections.indexOf('Summary'));
	assert.equal(steps.length, tutorial.stages.length);
	tutorial.stages.forEach((stage, index) => {
		assert.equal(stage.step, index + 1);
		assert.equal(stage.endState, true);
		assert.match(text, new RegExp(`::checkpoint\\{stage=${index + 1}\\}\\n\\n::figure\\{id=checkpoint-${index + 1}\\}`));
	});
	assert.match(text, /### What `ST_SCRIPT_CLASS` is for/, 'a query of a tutorial goes before its steps, as a subsection');
});

test('a reference page includes the tables the tool chain renders, and says so when none is there', () => {
	const book = generateBook(inputs(), { fraction: 0.05 });
	const commands = book.files.get('src/content/docs/reference/commands.md');
	assert.match(commands, /::include\{file="commands-toolsets\.md"\}[\s\S]*::include\{file="commands-world\.md"\}/);
	assert.match(book.files.get('src/content/docs/reference/settings.md'), /## Project settings\n\n::include\{file="settings\.md"\}\n\n## Preferences\n\n::include\{file="preferences\.md"\}/);
	const none = generateBook(inputs({ referenceFiles: new Set() }), { fraction: 0.05 });
	assert.doesNotMatch(none.files.get('src/content/docs/reference/components.md'), /::include/);
	assert.match(none.files.get('src/content/docs/reference/components.md'), /\n## /);
});

test('the renders of the parts on light and the image say how they are published (pipelines.md §5.2)', () => {
	// The tutorials' checkpoints take a render per step whatever the fraction, and the outline's part make holds many
	// tutorials: below about 0.3 they take every render of the scaled total, and the parts on light get none.
	const book = generateBook(inputs(), { seed: 2, fraction: 0.3 });
	const recipes = [...book.files].filter(([relative]) => relative.startsWith('src/content/figures/')).flatMap(([relative, text]) => JSON.parse(text).figures.map((recipe) => [relative.split('/')[3], recipe]));
	const scenes = recipes.filter(([, recipe]) => recipe.kind === 'scene');
	for (const part of ['light', 'image', 'indirect', 'core']) assert.ok(scenes.some(([name]) => name === part), `the generated book has no render in the part ${part}`);
	for (const [part, recipe] of scenes) assert.equal(recipe.publish, ['light', 'image', 'indirect'].includes(part) ? 'lossy' : undefined, `${part}: ${recipe.id}`);
});

test('core/time holds prose that reads like text directives, and two code spans side by side, which a build shows as written (confirm items 2 and 6)', () => {
	const book = generateBook(inputs(), { fraction: 0.05 });
	assert.match(c_DirectiveLikeProse, /std::vector/);
	assert.ok(book.files.get('src/content/docs/core/time.md').includes(`\n${c_DirectiveLikeProse}\n`));
	assert.ok(book.files.get('src/content/docs/core/time.md').includes(`\n${c_CodePairProse}\n`));
});

test('the generator writes the same book from the same seed', () => {
	const first = generateBook(inputs(), { seed: 7, fraction: 0.03 });
	const second = generateBook(inputs(), { seed: 7, fraction: 0.03 });
	assert.deepEqual([...first.files.keys()], [...second.files.keys()]);
	for (const [relative, text] of first.files) assert.equal(second.files.get(relative), text, relative);
	assert.deepEqual(first.pictures, second.pictures);
});

test('relative links name the Markdown file of the other page', () => {
	assert.equal(relativeLink('core/time', 'core/frame-loop'), 'frame-loop.md');
	assert.equal(relativeLink('core/time', 'world/interpolation'), '../world/interpolation.md');
});

test('a picture is encoded in its one format, its crop cut at whole pixels, stamped, and taken from the cache the second time', async () => {
	const cache = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'scale-cache-'));
	try {
		const bytes = await sharp({ create: { width: 96, height: 54, channels: 3, background: { r: 90, g: 120, b: 200 } } }).png().toBuffer();
		const shots = [{ file: 'Samples/A/Screenshots/a.png', bytes, sha256: 'a'.repeat(64) }];
		const job = { page: 'core/time', figure: 'render-1', variant: null, crop: 'detail', kind: 'scene', encoder: 'render', source: 3, size: [1920, 1080] };
		const made = await makePicture(sharp, job, shots, cache);
		assert.deepEqual(made.map((entry) => entry.name), ['render-1.avif', 'render-1-detail.webp']);
		assert.deepEqual(sniffFormat(made[0].bytes), { format: 'avif', lossless: null });
		assert.deepEqual(sniffFormat(made[1].bytes), { format: 'webp', lossless: true });
		const crop = await sharp(made[1].bytes).metadata();
		assert.deepEqual([crop.width, crop.height], [320, 180], `the crop ${c_CropRect.join(', ')} of a 1920 x 1080 render`);
		assert.deepEqual(made[0].encoder, { format: 'avif', lossless: false, quality: 80, chromaSubsampling: '4:4:4', effort: 4, sharp: sharp.versions.sharp, libvips: sharp.versions.vips });
		const stamp = stampRecord(job, made[0], parsePin(c_Pin));
		assert.match(stamp.sha256, /^[0-9a-f]{64}$/);
		assert.equal(stamp.pin, parsePin(c_Pin).commit);
		const again = await makePicture(sharp, job, shots, cache);
		assert.ok(again.every((entry, index) => entry.bytes.equals(made[index].bytes)), 'the cache gives the same bytes');
		// Another figure made from the same pixels (another run's, another page's) gets its own names from the cache.
		const other = await makePicture(sharp, { ...job, page: 'world/ecs', figure: 'checkpoint-2' }, shots, cache);
		assert.deepEqual(other.map((entry) => entry.name), ['checkpoint-2.avif', 'checkpoint-2-detail.webp']);
		assert.ok(other[0].bytes.equals(made[0].bytes));
		const editor = await makePicture(sharp, { ...job, figure: 'interface-1', crop: null, kind: 'editor', encoder: 'lossless' }, shots, cache);
		const metadata = await sharp(editor[0].bytes).metadata();
		assert.equal(editor[0].name, 'interface-1.webp');
		assert.deepEqual([metadata.width, metadata.height], [1600, 900]);
		assert.ok(existsSync(cache));
	} finally {
		rmSync(cache, { recursive: true, force: true });
	}
});

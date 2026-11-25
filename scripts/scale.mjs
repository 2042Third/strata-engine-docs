// The scale test's book (plan/site.md, "Budgets and the spike"): a copy of this project whose content is generated at
// the size of the finished book, written into .tools/scale/site/ (never committed). Every row of the outline
// (src/generated/outline.json, 332 rows) becomes a page of its kind at its size (S 1,500 words, M 3,000, L 5,000,
// XL 8,000) with its id, title, kind, size, tracks and Needs, in the shape style.md gives the kind, so that every check
// of the build runs on it at scale. Each part with part pages gets its index and review page; the site draws a print
// view per part. The book holds:
//
// - 1,500 quotes of the engine at the pin (read with git from the clone given by --engine), about 3,000 code blocks in
//   all (quotes, sketches and their output, pseudocode, commands, tab sets), 400 Mermaid diagrams, math on a third of
//   the pages;
// - 600 pictures made from the twelve sample screenshots at the pin (Samples/<sample>/Screenshots/*.png, 960 x 540),
//   each upscaled once to 1920 x 1080 and varied by its crop, its light and a faint noise: 450 renders published as
//   AVIF (60 of them in 30 slider pairs), 100 crops of 320 x 180 and 50 pictures of the interface as lossless WebP,
//   encoded with scripts/encode-figures.mjs's settings and stamped in taken.json;
// - the generated reference at its real size: the tables of src/generated/reference/ that the tool chain renders,
//   included by the reference pages that hold them; the glossary of plan/glossary/seed.json's beginner vocabulary plus
//   generated terms, 1,892 in all;
// - the words of scripts/search-queries.json on the pages the queries expect, so that the search test measures ranking
//   against pages that hold the words, as the written pages will.
//
//     node scripts/scale.mjs --engine <pin clone> [--out .tools/scale/site] [--cache .tools/scale/cache] [--seed 1]
//         [--fraction 1] [--jobs 4]
//
// --fraction shrinks every page and every total (at least one of each), for a quick look at the generator's output;
// the scale test is --fraction 1. Encoded pictures are kept in --cache, keyed by their source and settings, so a second
// run writes the same files without encoding them again. The project's code is copied so that Astro builds the copy as
// its own project; its packages come from this project's node_modules, found by Node's lookup through parent folders
// (so the copy must stay inside this project; links would need a volume that supports them).
//
// Exit codes: 0 written; 1 an input is missing or unreadable (the message names it); 2 usage.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { c_LearnVerbs } from '../src/lib/frontmatter.mjs';
import { cropPixels } from '../src/lib/figures.mjs';
import { glossaryId } from '../src/lib/glossary.mjs';
import { indexOutline, needsClosure } from '../src/lib/outline.mjs';
import { parsePin } from '../src/lib/settings.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/** The words of a page of each size (plan/site.md, "The spike's content follows the book"). */
export const c_Words = { S: 1500, M: 3000, L: 5000, XL: 8000 };
/** The minutes a reader spends on a page of each size, for its front matter. */
const c_Minutes = { S: 10, M: 20, L: 30, XL: 45 };
/**
 * The book's totals (plan/site.md, "The spike's content follows the book"): quotes, code blocks, diagrams, pictures
 * (renders, of which slider pairs, crops and pictures of the interface) and glossary terms.
 */
export const c_Totals = { quotes: 1500, codeBlocks: 3000, diagrams: 400, renders: 450, sliderPairs: 30, crops: 100, interface: 50, terms: 1892 };
/** The parts whose renders name their publish value (pipelines.md §5.2: dither, grain and noise are what lossy encoding smears). */
const c_PublishParts = ['light', 'image', 'indirect'];
/** Every page whose kind quotes the engine; an internals page quotes it at least this often (site.md P4). */
const c_MinInternalsQuotes = 3;
/** A sentence of prose with words that read like text directives, which the build must leave as they are. */
export const c_DirectiveLikeProse = 'The loop starts at 10:30, a std::vector keeps its steps, and a:b names two of them.';
/** Two inline code spans with one space between them, which compressHTML must keep. */
export const c_CodePairProse = 'Two names stand side by side: `first` `second`.';
/** The size of the pictures: renders and their crops, pictures of the interface. */
export const c_RenderSize = [1920, 1080];
export const c_InterfaceSize = [1600, 900];
/** A crop's rectangle: 320 x 180 pixels of a 1920 x 1080 render (cropPixels cuts at whole pixels, as figures.py). */
export const c_CropRect = [0.25, 0.25, 0.41667, 0.41667];
/** scripts/encode-figures.mjs's settings: lossy AVIF 4:4:4 at effort 4 (quality 90 for a slider's sides), lossless WebP. */
export const c_Encoders = {
	render: { format: 'avif', lossless: false, quality: 80, chromaSubsampling: '4:4:4', effort: 4 },
	slider: { format: 'avif', lossless: false, quality: 90, chromaSubsampling: '4:4:4', effort: 4 },
	lossless: { format: 'webp', lossless: true, effort: 4 },
};
// Which reference page includes which tables of src/generated/reference/. A table that starts at ### gets a ## of its
// own before it (settings, preferences). The command tables all go on the command catalogue, the outline's one row.
const c_ReferenceTables = {
	'reference/script-api': [['script-api.md']],
	'reference/components': [['components.md']],
	'reference/settings': [['settings.md', 'Project settings'], ['preferences.md', 'Preferences']],
	'reference/assets': [['asset-types.md'], ['asset-budgets.md']],
	'reference/renderer': [['renderer.md'], ['gpu-stages.md'], ['render-stats.md'], ['debug-views.md'], ['quality.md']],
	'reference/worlds-runtime': [['options-runtime.md'], ['perf-log.md']],
	'reference/editor': [['options-editor.md']],
	'reference/automation': [['options-cli.md']],
	'reference/scene': [['limits.md']],
	'reference/build': [['build.md']],
	'reference/performance': [['performance.md']],
	'reference/figures': [['figures.md']],
};
// The further reading the pages link: external hosts of tools/external-hosts.txt, a few addresses in all.
const c_FurtherReading = [
	['https://en.cppreference.com/w/cpp/language/classes', 'cppreference, "Classes"'],
	['https://learn.microsoft.com/en-us/powershell/scripting/overview', 'Microsoft, "About PowerShell"'],
	['https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository', 'Pro Git, chapter 2'],
	['https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html', 'CMake, "cmake-presets"'],
	['https://gafferongames.com/post/fix_your_timestep/', 'Glenn Fiedler, "Fix Your Timestep!"'],
];
// Plain words the generated prose is made of, and none of Mermaid's keywords (style.md §11), so that a diagram's names
// never read as one.
export const c_Nouns = ('frame scene entity part system pass light shadow picture buffer mesh material camera step body shape '
	+ 'contact query thread job queue copy memory cache budget file pack stream handle editor command panel view '
	+ 'selection history script field event input action audio sound listener pose blend world cell ground probe tone '
	+ 'filter depth normal color layout barrier order value number table list rule key record page test change '
	+ 'loader owner reader writer count size time rate model clock box line point plane ray grid').split(' ');
const c_Verbs = 'reads writes keeps draws sends checks finds builds loads stores moves turns counts holds asks takes gives runs'.split(' ');
const c_Joiners = ['and', 'then', 'so that', 'because', 'while', 'before', 'after', 'unless', 'when'];
const c_Asides = ['why', 'question', 'history', 'elsewhere', 'rule', 'note', 'tip', 'caution', 'simplified', 'analogy', 'derivation'];
const c_Formulas = [
	'\\alpha = 1 - \\frac{1 - a/h}{n}',
	'\\sum_{i=0}^{n-1} w_i \\, x_i',
	'L_o(\\omega_o) = \\int_{\\Omega} f_r(\\omega_i, \\omega_o) \\, L_i(\\omega_i) \\, (n \\cdot \\omega_i) \\, d\\omega_i',
	'\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix}',
	'q = \\left(\\cos\\frac{\\theta}{2}, \\; \\sin\\frac{\\theta}{2} \\, \\hat{u}\\right)',
	'v_{n+1} = v_n + a \\, \\Delta t, \\qquad x_{n+1} = x_n + v_{n+1} \\, \\Delta t',
];
// The sample sketches whose copies the generated pages show, with the pages that show their output today.
const c_SampleSketches = [
	['core-time-fixed-step.cpp', 'core/time', 'fixed-step'],
	['core-time-thirty-frames.cpp', 'core/time', 'thirty-frames'],
	['world-interpolation-toy.cpp', 'world/interpolation', 'toy'],
];

/** A small deterministic random generator (mulberry32), so that every run writes the same book. */
export function createRandom(seed) {
	let state = seed >>> 0;
	const random = () => {
		state = (state + 0x6d2b79f5) >>> 0;
		let t = state;
		t = Math.imul(t ^ (t >>> 15), t | 1);
		t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
	const between = (low, high) => low + Math.floor(random() * (high - low + 1));
	const pick = (items) => items[Math.floor(random() * items.length)];
	return { random, between, pick };
}

/** Splits `total` over items in proportion to their weights (largest remainder), so the counts add up exactly. */
export function deal(total, weights) {
	const sum = weights.reduce((a, b) => a + b, 0);
	if (sum === 0) return weights.map(() => 0);
	const exact = weights.map((weight) => (total * weight) / sum);
	const counts = exact.map(Math.floor);
	let left = total - counts.reduce((a, b) => a + b, 0);
	const order = exact.map((value, index) => [value - Math.floor(value), index]).sort((a, b) => b[0] - a[0] || a[1] - b[1]);
	for (let i = 0; left > 0; i = (i + 1) % order.length, left--) counts[order[i][1]]++;
	return counts;
}

/** The lines of a quote as tools/excerpts.py fill writes them (pipelines.md §3.4): the common leading tabs removed. */
export function normalizeQuote(lines) {
	const counted = lines.filter((line) => line.trim() && !line.startsWith('#'));
	if (!counted.length) return [...lines];
	const smallest = Math.min(...counted.map((line) => line.length - line.replace(/^\t+/, '').length));
	if (!smallest) return [...lines];
	return lines.map((line) => line.slice(Math.min(line.length - line.replace(/^\t+/, '').length, smallest)));
}

function countWords(text) {
	return text.split(/\s+/).filter(Boolean).length;
}

/** The words of prose in Markdown lines: everything outside fences and display math, without the directive lines. */
export function proseWords(lines) {
	let words = 0;
	let fence = false;
	let math = false;
	for (const line of lines) {
		const trimmed = line.trim();
		if (trimmed.startsWith('```')) {
			fence = !fence;
			continue;
		}
		if (trimmed === '$$') {
			math = !math;
			continue;
		}
		if (fence || math || /^:{2,}/.test(trimmed) || trimmed.startsWith('|') || trimmed.startsWith('---')) continue;
		words += countWords(trimmed.replace(/^#+\s|^[-*]\s|^\d+\.\s/, ''));
	}
	return words;
}

function capitalize(text) {
	return `${text[0].toUpperCase()}${text.slice(1)}`;
}

/** The relative link from page `fromId` to the Markdown file of page `toId`, as a page writes it (site.md rule 1). */
export function relativeLink(fromId, toId) {
	const from = fromId.split('/');
	const to = toId.split('/');
	return from[0] === to[0] ? `${to.slice(1).join('/')}.md` : `../${to.join('/')}.md`;
}

/** A link's text from a page's title: code spans and brackets kept out of it. */
function linkText(title) {
	return title.replace(/[[\]`]/g, '');
}

/** The output a sample page shows for a sketch: the body of its `text output-of="…"` fence, without the indent. */
export function sketchOutput(pageText, name) {
	const lines = pageText.replace(/\r\n/g, '\n').split('\n');
	const start = lines.findIndex((line) => line.trim() === `\`\`\`text output-of="${name}"`);
	if (start < 0) return null;
	const indent = lines[start].length - lines[start].trimStart().length;
	const body = [];
	for (let i = start + 1; i < lines.length; i++) {
		if (lines[i].trim() === '```') return body.map((line) => line.slice(Math.min(indent, line.length - line.trimStart().length)));
		body.push(lines[i]);
	}
	return null;
}

/**
 * The prose of the book: sentences of plain words, with the page's own terms marked (:term) on their first use and
 * the words of its queries (scripts/search-queries.json) where they belong.
 */
class Prose {
	constructor(rng) {
		this.rng = rng;
	}

	sentence() {
		const { between, pick } = this.rng;
		const length = between(9, 17);
		const words = [];
		for (let i = 0; i < length; i++) {
			if (i % 5 === 2) words.push(pick(c_Verbs));
			else if (i % 7 === 4) words.push(pick(c_Joiners));
			else words.push(pick(c_Nouns));
		}
		return `${capitalize(words.join(' '))}.`;
	}

	paragraph(count = this.rng.between(3, 5), extra = []) {
		const sentences = Array.from({ length: count }, () => this.sentence());
		for (const text of extra) sentences.splice(this.rng.between(0, sentences.length), 0, text);
		return sentences.join(' ');
	}

	words(count) {
		return Array.from({ length: count }, () => this.rng.pick(c_Nouns)).join(' ');
	}

	heading(number) {
		return `${capitalize(this.rng.pick(c_Nouns))} ${this.rng.pick(c_Verbs)} the ${this.rng.pick(c_Nouns)} ${number}`;
	}
}

/** A Mermaid diagram of one of the five types the book draws (flowchart, sequence, state, class, ER). */
function diagramSource(rng, index) {
	const { between, pick } = rng;
	const names = Array.from({ length: between(4, 7) }, () => `${pick(c_Nouns)} ${pick(c_Nouns)}`);
	switch (index % 5) {
		case 0: {
			const lines = ['flowchart LR'];
			names.forEach((name, i) => lines.push(`    N${i}["${name}"]`));
			for (let i = 1; i < names.length; i++) lines.push(`    N${between(0, i - 1)} -->|${pick(c_Verbs)}| N${i}`);
			return lines.join('\n');
		}
		case 1: {
			const lines = ['sequenceDiagram'];
			names.slice(0, 3).forEach((name, i) => lines.push(`    participant P${i} as ${capitalize(name)}`));
			for (let i = 0; i < between(4, 7); i++) {
				const from = between(0, 2);
				lines.push(`    P${from}->>P${(from + between(1, 2)) % 3}: ${pick(c_Verbs)} the ${pick(c_Nouns)} ${index}`);
			}
			return lines.join('\n');
		}
		case 2: {
			const lines = ['stateDiagram-v2', '    [*] --> S0'];
			names.forEach((name, i) => lines.push(`    S${i}: ${name}`));
			for (let i = 1; i < names.length; i++) lines.push(`    S${i - 1} --> S${i}: ${pick(c_Verbs)} ${index}`);
			lines.push(`    S${names.length - 1} --> [*]`);
			return lines.join('\n');
		}
		case 3: {
			const lines = ['classDiagram'];
			const classes = names.slice(0, 4).map((name, i) => `${name.split(' ').map(capitalize).join('')}${i}`);
			classes.forEach((name) => lines.push(`    class ${name} {`, `        +int ${pick(c_Nouns)}Count`, `        +${pick(c_Verbs).slice(0, -1)}()`, '    }'));
			for (let i = 1; i < classes.length; i++) lines.push(`    ${classes[i - 1]} --> ${classes[i]} : ${pick(c_Verbs)}`);
			return lines.join('\n');
		}
		default: {
			const lines = ['erDiagram'];
			const entities = names.slice(0, 3).map((name, i) => `E${i}`);
			entities.forEach((entity) => lines.push(`    ${entity} {`, `        int ${pick(c_Nouns)}`, `        string ${pick(c_Nouns)}`, '    }'));
			lines.push(`    E0 ||--o{ E1 : ${pick(c_Verbs)}`, `    E1 ||--|{ E2 : ${pick(c_Verbs)}`);
			return lines.join('\n');
		}
	}
}

/**
 * What each page holds of the book's totals: quotes, diagrams, plain code blocks, pictures and their kinds, math and
 * sketches, each total scaled by `fraction`. Returns `{ shares: Map<page id, share>, counts }`.
 */
export function planBook(rows, totals, fraction) {
	const scaled = (value) => Math.max(1, Math.round(value * fraction));
	const counts = Object.fromEntries(Object.entries(totals).map(([key, value]) => [key, scaled(value)]));
	const shares = new Map(rows.map((row) => [row.id, { quotes: 0, diagrams: 0, fences: 0, renders: 0, compares: 0, crops: 0, checkpoints: [], math: false, sketch: null, tabs: false }]));
	const written = rows.filter((row) => row.kind !== 'reference');
	const weight = (row) => c_Words[row.size] * fraction;
	// Quotes: three on every internals page first, the rest by size over the kinds that quote the engine.
	const quoting = written.filter((row) => row.kind !== 'primer');
	for (const row of quoting) if (row.kind === 'internals') shares.get(row.id).quotes = c_MinInternalsQuotes;
	const already = quoting.filter((row) => row.kind === 'internals').length * c_MinInternalsQuotes;
	deal(Math.max(0, counts.quotes - already), quoting.map(weight)).forEach((count, index) => (shares.get(quoting[index].id).quotes += count));
	deal(counts.diagrams, written.map(weight)).forEach((count, index) => (shares.get(written[index].id).diagrams = count));
	// Tutorials end every step section with a checkpoint and its picture: the first of them are pictures of the
	// interface, the rest renders. Their steps: two on S pages, three on M and L, four on XL.
	let interfaceLeft = counts.interface;
	let checkpointRenders = 0;
	for (const row of written.filter((candidate) => candidate.kind === 'tutorial')) {
		const steps = { S: 2, M: 3, L: 3, XL: 4 }[row.size];
		for (let step = 1; step <= steps; step++) {
			const kind = interfaceLeft > 0 ? 'editor' : 'scene';
			if (kind === 'editor') interfaceLeft--;
			else checkpointRenders++;
			shares.get(row.id).checkpoints.push(kind);
		}
	}
	const others = written.filter((row) => row.kind !== 'tutorial');
	const compares = Math.min(counts.sliderPairs, Math.floor(counts.renders / 2));
	deal(compares, others.map(weight)).forEach((count, index) => (shares.get(others[index].id).compares = count));
	// The pictures of the interface not used by checkpoints go on the other pages as editor figures.
	deal(interfaceLeft, others.map(weight)).forEach((count, index) => (shares.get(others[index].id).editors = count));
	const singles = Math.max(0, counts.renders - 2 * compares - checkpointRenders);
	deal(singles, written.map(weight)).forEach((count, index) => (shares.get(written[index].id).renders = count));
	// Crops: one each on the first renders, spread over the book.
	let cropsLeft = Math.min(counts.crops, singles);
	const withRenders = written.filter((row) => shares.get(row.id).renders > 0);
	for (let pass = 0; cropsLeft > 0 && withRenders.length; pass++) {
		for (const row of withRenders) {
			const share = shares.get(row.id);
			if (cropsLeft > 0 && share.crops < share.renders && share.crops === pass) {
				share.crops++;
				cropsLeft--;
			}
		}
	}
	// Math on every third page, a sketch with its output on every fifth page that teaches with code, a tab set on every
	// fourth page; the plain code blocks fill the total of code blocks.
	written.forEach((row, index) => {
		const share = shares.get(row.id);
		share.math = index % 3 === 0;
		share.tabs = index % 4 === 1;
		if (index % 5 === 2 && row.kind !== 'tutorial') share.sketch = c_SampleSketches[index % c_SampleSketches.length][0];
	});
	const fixed = [...shares.values()].reduce((sum, share) => sum + share.quotes + (share.sketch ? 2 : 0) + (share.tabs ? 3 : 0), 0);
	deal(Math.max(0, counts.codeBlocks - fixed), written.map(weight)).forEach((count, index) => (shares.get(written[index].id).fences = count));
	for (const share of shares.values()) share.editors ??= 0;
	return { shares, counts };
}

/** The objectives of a page: three, each starting with an observable verb (style.md §6.1). */
function objectives(rng) {
	return ['first', 'second', 'third'].map((name, index) => ({ id: `${name}-${rng.pick(c_Nouns)}`, text: `${c_LearnVerbs[(index * 5 + rng.between(0, 4)) % c_LearnVerbs.length]} how the ${rng.pick(c_Nouns)} ${rng.pick(c_Verbs)} the ${rng.pick(c_Nouns)}` }));
}

/** The front matter of a row's page (style.md §6.1), its values equal to the row's (site.md O7). */
function chapterFrontmatter(row, part, learn, rng, pin) {
	const lines = ['---', `id: ${row.id}`, `title: ${JSON.stringify(row.title)}`, `description: ${JSON.stringify(`How the ${rng.pick(c_Nouns)} and the ${rng.pick(c_Nouns)} work together on this page, and the code that does it.`)}`, `kind: ${row.kind}`, `size: ${row.size}`, `tracks: [${row.tracks.join(', ')}]`, `needs: [${row.needs.join(', ')}]`];
	if (row.kind !== 'reference') {
		lines.push(`time: ${c_Minutes[row.size]}`, 'learn:', ...learn.flatMap((item) => [`  - id: ${item.id}`, `    text: ${item.text}`]));
		const takesSince = ['concept', 'internals', 'tutorial', 'how-to'].includes(row.kind) && (part.number === 1 || (part.number >= 3 && part.number <= 21));
		if (takesSince) lines.push(`since: ${row.mark === 'W8' ? pin.release : `0.${rng.between(3, 7)}.0`}`);
	}
	lines.push('status: draft');
	if (row.id === 'reference/glossary') lines.push('tableOfContents: false');
	lines.push('---', '');
	return lines;
}

/** The numbered questions of a section, each followed by its answer naming the objectives it tests (style.md §8). */
function questions(prose, learn, count, label = null) {
	const lines = [];
	for (let q = 0; q < count; q++) {
		const tests = learn[q % learn.length].id;
		lines.push(`${q + 1}. ${label ? `**${label[q % label.length]}.** ` : ''}${prose.sentence().slice(0, -1)}?`, '', `   :::answer{tests="${tests}"}`, `   ${prose.sentence()}`, '   :::', '');
	}
	return lines;
}

/** The bottom strip of a page (style.md §6.3): its kind's sections in order. */
function bottomStrip(row, learn, ctx) {
	const { prose, rng } = ctx;
	if (row.kind === 'reference') return ['## Where it lives in Strata', '', `- \`${rng.pick(ctx.engineFiles)}\`: ${prose.sentence()}`, ''];
	const lines = ['## Summary', '', ...learn.map(() => `- ${prose.sentence()}`), '', '## Check yourself', '', ...questions(prose, learn, 4)];
	if (row.kind === 'primer') {
		lines.push('## Practice', '', ...questions(prose, learn, 4, ['Basic', 'Basic', 'Medium', 'Hard']), '## Where the book uses it', '');
		for (const user of ctx.usersOf(row.id)) lines.push(`- [${linkText(ctx.rows.get(user).title)}](${relativeLink(row.id, user)}) ${prose.sentence().toLowerCase()}`);
		lines.push('');
	} else {
		lines.push('## Exercises', '', ...questions(prose, learn, 2, ['Basic', 'Medium']), '## Where it lives in Strata', '');
		for (let i = 0; i < 2; i++) lines.push(`- \`${rng.pick(ctx.engineFiles)}\`: ${prose.sentence()}`);
		lines.push('');
	}
	const [url, title] = rng.pick(c_FurtherReading);
	lines.push('## Further reading', '', `- [${title}](${url}): ${prose.sentence()}`, '');
	return lines;
}

/** An aside of one of the book's kinds (site.md, "Directives"); an analogy ends with where it breaks. */
function aside(prose, kind) {
	if (kind === 'analogy') return [':::analogy', prose.paragraph(2), '', `**Where it breaks:** ${prose.sentence()}`, ':::', ''];
	if (kind === 'derivation') return [':::derivation', prose.paragraph(2), '', '$$', 'x_{n+1} = x_n + v_n \\, \\Delta t', '$$', ':::', ''];
	return [`:::${kind}`, prose.paragraph(2), ':::', ''];
}

/**
 * The page of an outline row and what it adds to the book: its text, the recipes of its figures, its pictures to make,
 * its diagrams, its tutorial file and its sketches.
 */
function chapterPage(row, share, ctx) {
	const { prose, rng } = ctx;
	const part = ctx.outline.partBySlug.get(row.part);
	const learn = objectives(rng);
	const lines = chapterFrontmatter(row, part, learn, rng, ctx.pin);
	const result = { figures: [], pictures: [], diagrams: [], tutorial: null, sketches: [] };
	const target = Math.round(c_Words[row.size] * ctx.fraction);
	const own = ctx.homeTerms.get(row.id) ?? [];
	const marked = new Set();
	const termSentence = (term) => {
		if (marked.has(term.id)) return `${capitalize(term.term)} ${prose.words(3)} ${rng.pick(c_Verbs)} the ${rng.pick(c_Nouns)}.`;
		marked.add(term.id);
		return `:term[${capitalize(term.term)}]{id="${term.id}"} means ${term.definition[0].toLowerCase()}${term.definition.slice(1)}`;
	};
	const used = [...own, ...Array.from({ length: 6 }, () => rng.pick(ctx.terms))];
	let termIndex = 0;
	const paragraph = () => prose.paragraph(rng.between(3, 5), termIndex < used.length && rng.random() < 0.5 ? [termSentence(used[termIndex++])] : []);

	if (row.kind === 'reference') return referencePage(row, lines, learn, ctx, result, target);

	const blocks = [];
	for (let i = 0; i < share.quotes; i++) blocks.push('quote');
	for (let i = 0; i < share.diagrams; i++) blocks.push('diagram');
	for (let i = 0; i < share.fences; i++) blocks.push(['pseudocode', 'json', 'text'][i % 3]);
	for (let i = 0; i < share.renders; i++) blocks.push(i < share.crops ? 'render-crop' : 'render');
	for (let i = 0; i < share.compares; i++) blocks.push('compare');
	for (let i = 0; i < share.editors; i++) blocks.push('editor');
	if (share.tabs) blocks.push('tabs');
	if (share.sketch) blocks.push('sketch');
	if (share.math) blocks.push('math', 'math');
	// Shuffled, so a page's blocks spread over its sections.
	for (let i = blocks.length - 1; i > 0; i--) {
		const j = rng.between(0, i);
		[blocks[i], blocks[j]] = [blocks[j], blocks[i]];
	}
	let figureNumber = 0;
	const addFigure = (out, kind, { crop = false, variants = null, id = null } = {}) => {
		figureNumber++;
		const figureId = id ?? `${kind === 'editor' ? 'interface' : variants ? 'compare' : 'render'}-${figureNumber}`;
		const recipe = figureRecipe(figureId, kind, crop, variants, prose, rng, row.part);
		result.figures.push(recipe);
		const source = ctx.pictureIndex++;
		if (kind === 'editor') result.pictures.push({ page: row.id, figure: figureId, variant: null, crop: null, kind, encoder: 'lossless', source, size: c_InterfaceSize });
		else if (variants) for (const variant of variants) result.pictures.push({ page: row.id, figure: figureId, variant, crop: null, kind, encoder: 'slider', source, size: c_RenderSize, brighter: variant === variants[1] });
		else result.pictures.push({ page: row.id, figure: figureId, variant: null, crop: crop ? 'detail' : null, kind, encoder: 'render', source, size: c_RenderSize });
		out.push(`${variants ? '::compare' : '::figure'}{id=${figureId}}`, '');
		if (crop) out.push(`It helps to look closer at one part of the picture: ${prose.sentence().toLowerCase()}`, '', `::figure{id=${figureId} crop=detail}`, '');
		return figureId;
	};
	const placeBlock = (out, block, sectionNumber) => {
		switch (block) {
			case 'quote': {
				const file = rng.pick(ctx.engineFiles);
				const source = ctx.engineLines(file);
				const length = rng.between(8, 40);
				let start = rng.between(1, Math.max(1, source.length - length));
				// A quote starts and ends on a line that holds code: the build refuses blank ends, which Expressive Code
				// does not draw.
				const lines = source.slice(start - 1, start - 1 + length);
				while (lines.length > 1 && !lines[0].trim()) {
					lines.shift();
					start++;
				}
				while (lines.length > 1 && !lines.at(-1).trim()) lines.pop();
				const body = normalizeQuote(lines);
				const end = start + body.length - 1;
				const mark = rng.random() < 0.2 ? ` mark="L${start + 1}"` : '';
				out.push(`The engine does it this way, ${prose.sentence().toLowerCase()}`, '', `\`\`\`cpp src="${file}#L${start}-L${end}"${mark}`, ...body, '```', '', prose.paragraph(2), '');
				ctx.counts.quotes++;
				ctx.counts.codeBlocks++;
				break;
			}
			case 'diagram': {
				const source = diagramSource(rng, ctx.counts.diagrams);
				result.diagrams.push(source);
				out.push(`The diagram shows the ${prose.words(2)} and what ${rng.pick(c_Verbs)} it.`, '', `\`\`\`mermaid caption="How the ${rng.pick(c_Nouns)} reaches the ${rng.pick(c_Nouns)}." alt="A diagram of the ${rng.pick(c_Nouns)} and the ${rng.pick(c_Nouns)}, and how one leads to the other."`, source, '```', '');
				ctx.counts.diagrams++;
				break;
			}
			case 'pseudocode':
				out.push(`In plain steps, the ${prose.words(2)} works like this:`, '', '```cpp pseudocode', `for each ${rng.pick(c_Nouns)} in the ${rng.pick(c_Nouns)}:`, `    ${rng.pick(c_Verbs)} its ${rng.pick(c_Nouns)}`, `    if the ${rng.pick(c_Nouns)} is full: ${rng.pick(c_Verbs)} the ${rng.pick(c_Nouns)}`, '```', '', prose.sentence(), '');
				ctx.counts.codeBlocks++;
				break;
			case 'json':
				out.push(`The command for it, as a script of commands writes it:`, '', '```json', `{ "command": "entity.find", "parameters": { "name": "${capitalize(rng.pick(c_Nouns))}" } }`, '```', '', prose.sentence(), '');
				ctx.counts.codeBlocks++;
				break;
			case 'text':
				out.push(`The log then reads:`, '', '```text', `[${rng.pick(c_Nouns)}] ${rng.pick(c_Verbs)} ${rng.between(1, 900)} items of the ${rng.pick(c_Nouns)} in ${rng.between(1, 90)} ms`, '```', '', prose.sentence(), '');
				ctx.counts.codeBlocks++;
				break;
			case 'tabs':
				out.push(`Build it with the preset of your system:`, '', '::::tabs{sync=os}', ':::tab[Windows]', '', '```powershell', 'cmake --preset windows', '```', '', ':::', ':::tab[Linux]', '', '```sh', 'cmake --preset linux', '```', '', ':::', ':::tab[macOS]', '', '```sh', 'cmake --preset macos', '```', '', ':::', '::::', '', prose.sentence(), '');
				ctx.counts.codeBlocks += 3;
				break;
			case 'sketch': {
				const sample = share.sketch;
				const name = `${row.id.replace('/', '-')}-${c_SampleSketches.find(([file]) => file === sample)[2]}.cpp`;
				result.sketches.push({ name, from: sample });
				out.push('A sketch of the idea, small enough to compile on its own:', '', `\`\`\`cpp sketch="${name}"`, ...ctx.sketchText(sample), '```', '', 'It prints:', '', `\`\`\`text output-of="${name}"`, ...ctx.sketchOutputs.get(sample), '```', '', prose.sentence(), '');
				ctx.counts.codeBlocks += 2;
				break;
			}
			case 'math':
				out.push(`With $x_i$ the values of the ${rng.pick(c_Nouns)} and $w_i$ their weights, the ${rng.pick(c_Nouns)} is:`, '', '$$', rng.pick(c_Formulas), '$$', '', prose.sentence(), '');
				ctx.counts.math++;
				break;
			case 'render':
				out.push(`The picture shows the ${prose.words(2)}.`, '');
				addFigure(out, 'scene');
				break;
			case 'render-crop':
				out.push(`The picture shows the ${prose.words(2)}.`, '');
				addFigure(out, 'scene', { crop: true });
				break;
			case 'compare':
				out.push(`Move the slider to compare the ${prose.words(2)} with and without it.`, '');
				addFigure(out, 'scene', { variants: ['off', 'on'] });
				break;
			case 'editor':
				out.push(`In the editor, the ${prose.words(2)} looks like this.`, '');
				addFigure(out, 'editor');
				break;
			default:
				throw new Error(`scale: no block "${block}"`);
		}
		if (sectionNumber % 4 === 3 && rng.random() < 0.7) out.push(...aside(prose, rng.pick(c_Asides)));
	};

	const body = [];
	const words = () => proseWords(lines) + proseWords(body);
	if (row.kind === 'primer') {
		body.push('::::test-out', '');
		for (let q = 0; q < 5; q++) body.push(`${q + 1}. ${prose.sentence().slice(0, -1)}?`, '', `   :::answer{tests="${learn[q % learn.length].id}"}`, `   ${prose.sentence()}`, '   :::', '');
		body.push('::::', '', '## Why you will need this', '', paragraph(), '');
	} else if (row.kind === 'internals') {
		body.push('## The problem and how engines solve it', '', paragraph(), '');
	} else if (row.kind === 'tutorial') {
		body.push('## What you will make', '', paragraph(), '', '## What you need', '', `- ${prose.sentence()}`, `- ${prose.sentence()}`, '');
	}
	if (row.id === 'start/how-to-read') body.push('## Choose a track', '', paragraph(), '', '::track-chooser', '');
	// Confirm items 2 and 6 (site.md, 'Budgets and the spike'): prose that reads like text directives stays as written,
	// and the space between two inline code spans stays.
	if (row.id === 'core/time') body.push(c_DirectiveLikeProse, '', c_CodePairProse, '');
	// The words of the queries that expect this page, in a section of its own as a written page would hold them.
	// A tutorial's sections after "## What you need" are its steps, so its queries go into "## What you will make".
	const level = row.kind === 'tutorial' ? '###' : '##';
	const querySections = [];
	for (const query of ctx.queriesFor(row.id)) {
		const text = query.query;
		if (query.kind === 'question') querySections.push(`${level} ${capitalize(text)}`, '', `${capitalize(text)}? ${prose.paragraph(2)}`, '');
		else if (query.kind === 'name') querySections.push(`${level} What \`${text}\` is for`, '', `The name \`${text}\` ${prose.words(4)}. ${prose.paragraph(2)} Read \`${text}\` where the ${rng.pick(c_Nouns)} ${rng.pick(c_Verbs)} it.`, '');
		else querySections.push(`${level} What the ${text} is for`, '', `The ${text} ${prose.words(4)}. ${prose.paragraph(2)} The ${text} ${prose.words(3)}.`, '');
	}
	if (row.kind === 'tutorial') body.splice(body.indexOf('## What you need'), 0, ...querySections);
	else body.push(...querySections);
	// The section count follows the size, about 400 words a section; a tutorial has one section per step.
	const sections = row.kind === 'tutorial' ? share.checkpoints.length : Math.max(2, Math.round(target / 420));
	const perSection = Math.ceil(blocks.length / sections);
	// The words still to come after the sections (the closing sections and the bottom strip), so the page ends at its size.
	const closing = row.kind === 'tutorial' ? 0 : 120;
	for (let section = 1; section <= sections; section++) {
		const out = [];
		out.push(`## ${prose.heading(section)}`, '', paragraph(), '');
		if (row.kind === 'tutorial') {
			// A step section: its steps, then its checkpoint and the checkpoint's picture (style.md §7.4).
			out.push(':::::steps', '');
			for (let item = 1; item <= 3; item++) out.push(`${item}. ${capitalize(prose.words(3))} ${prose.sentence().toLowerCase()}`, '', `   **You should see:** ${prose.sentence().toLowerCase()}`, '', `   **If you do not see it:** ${prose.sentence().toLowerCase()}`, '');
			out.push(':::::', '');
		}
		if (section % 3 === 2) out.push(`### The ${rng.pick(c_Nouns)} in detail`, '', paragraph(), '');
		if (section % 4 === 0) out.push(`- ${prose.sentence()}`, `- ${prose.sentence()}`, `- ${prose.sentence()}`, '');
		if (section % 5 === 2) out.push(`| ${capitalize(rng.pick(c_Nouns))} | ${capitalize(rng.pick(c_Nouns))} | ${capitalize(rng.pick(c_Nouns))} |`, '| --- | --- | --- |', ...Array.from({ length: 4 }, () => `| ${rng.pick(c_Nouns)} | ${rng.between(1, 900)} ms | ${rng.pick(c_Verbs)} |`), '');
		for (let i = 0; i < perSection && blocks.length; i++) placeBlock(out, blocks.shift(), section);
		const other = ctx.linkTarget(row);
		if (other) out.push(`[${linkText(ctx.rows.get(other).title)}](${relativeLink(row.id, other)}${ctx.rows.get(other).kind === 'reference' ? '' : '#summary'}) ${prose.sentence().toLowerCase()}`, '');
		while (words() + proseWords(out) < ((target - closing) * section) / sections) out.push(paragraph(), '');
		if (row.kind === 'tutorial') {
			out.push(`::checkpoint{stage=${section}}`, '');
			addFigure(out, share.checkpoints[section - 1], { id: `checkpoint-${section}` });
		}
		body.push(...out);
	}
	if (['primer', 'concept', 'internals'].includes(row.kind)) body.push(':::example', prose.paragraph(3), ':::', '');
	if (row.kind === 'primer' || row.kind === 'concept') body.push('## Common mistakes', '', `- **${capitalize(prose.words(3))}.** ${prose.sentence()}`, `- **${capitalize(prose.words(3))}.** ${prose.sentence()}`, '');
	if (row.kind === 'internals') body.push('## Alternatives Strata did not choose', '', `- ${prose.sentence()}`, `- ${prose.sentence()}`, '', '## How it is tested', '', paragraph(), '', '## Changing it safely', '', `- ${prose.sentence()}`, `- ${prose.sentence()}`, '');
	if (row.kind === 'how-to') body.push('## Result', '', paragraph(), '', '## Variations', '', `- ${prose.sentence()}`, `- ${prose.sentence()}`, '');
	if (row.kind === 'tutorial') {
		result.tutorial = { page: row.id, startsFrom: { template: 'basic3d', name: capitalize(rng.pick(c_Nouns)) }, stages: share.checkpoints.map((_, index) => ({ step: index + 1, commands: [{ command: 'editor.status' }], endState: true })) };
	}
	lines.push(...body, ...bottomStrip(row, learn, ctx));
	result.text = `${lines.join('\n').replace(/\n+$/, '')}\n`;
	return result;
}

/** A recipe of pipelines.md §5.2 for a generated picture: a render of the Showcase, a slider pair, or the editor. */
function figureRecipe(id, kind, crop, variants, prose, rng, part) {
	const base = {
		id,
		shows: `The ${prose.words(2)} of the ${rng.pick(c_Nouns)} as the page explains it`,
		caption: `Notice how the ${rng.pick(c_Nouns)} changes the ${rng.pick(c_Nouns)}.`,
		alt: `A rendered scene with a ${rng.pick(c_Nouns)} and a ${rng.pick(c_Nouns)} in the light.`,
		kind,
	};
	if (kind === 'editor') {
		return { ...base, alt: `The editor window with the ${rng.pick(c_Nouns)} panel open beside the Scene view.`, project: { template: 'basic3d' }, editorWindow: { layout: 'layouts/first-script.ini', steps: [{ command: 'editor.showPanel', parameters: { panel: 'Inspector' } }] } };
	}
	const recipe = { ...base, project: { sample: 'Showcase' }, camera: 'scene', size: [...c_RenderSize], quality: 'high', expect: 'complete' };
	// The renders of the parts on light and the image say how they are published (pipelines.md §5.2).
	if (c_PublishParts.includes(part)) recipe.publish = 'lossy';
	if (crop) recipe.crops = [{ name: 'detail', rect: [...c_CropRect], scale: 2 }];
	if (variants) recipe.variants = Object.fromEntries(variants.map((name) => [name, { setup: [{ command: 'project.setSettings', parameters: { section: 'Scene.Timing', value: { Interpolation: name === 'on' } } }] }]));
	return recipe;
}

/** A reference page: its tables from src/generated/reference/ where the tool chain renders them, otherwise prose and tables. */
function referencePage(row, lines, learn, ctx, result, target) {
	const { prose, rng } = ctx;
	const body = [];
	const tables = (c_ReferenceTables[row.id] ?? []).filter(([file]) => ctx.referenceFiles.has(file));
	if (row.id === 'reference/commands') {
		body.push(`The editor has :value{key="commands.count"} commands. ${prose.paragraph(2)}`, '');
		for (const file of ctx.commandTables) body.push(`::include{file="${file}"}`, '');
	} else if (row.id === 'reference/glossary') {
		body.push(prose.paragraph(3), '', '::glossary', '');
	} else if (row.id === 'reference/term-index') {
		body.push(prose.paragraph(3), '', '| Term or name | Page |', '| --- | --- |');
		for (const term of [...ctx.allTerms].sort((a, b) => a.term.localeCompare(b.term))) body.push(`| ${term.term} | [${linkText(ctx.rows.get(term.home).title)}](${relativeLink(row.id, term.home)}) |`);
		body.push('');
	} else if (tables.length) {
		body.push(prose.paragraph(3), '');
		for (const [file, heading] of tables) body.push(...(heading ? [`## ${heading}`, ''] : []), `::include{file="${file}"}`, '');
	}
	// The pages no table is rendered for yet, and the text around the tables, reach their size in prose and tables.
	for (let section = 1; proseWords(body) < target - 100 && !['reference/commands', 'reference/glossary', 'reference/term-index'].includes(row.id) && !tables.length; section++) {
		body.push(`## ${prose.heading(section)}`, '', prose.paragraph(), '', `| ${capitalize(rng.pick(c_Nouns))} | Type | Default |`, '| --- | --- | --- |', ...Array.from({ length: 6 }, () => `| \`${rng.pick(c_Nouns)}${capitalize(rng.pick(c_Nouns))}\` | ${rng.pick(['int', 'float', 'bool', 'string'])} | ${rng.between(0, 512)} |`), '');
	}
	lines.push(...body, ...bottomStrip(row, learn, ctx));
	result.text = `${lines.join('\n').replace(/\n+$/, '')}\n`;
	return result;
}

/** The index and review pages of a part with part pages (site.md, "Navigation"); the build draws their generated parts. */
function partPages(part, prose) {
	const lower = `${part.title[0].toLowerCase()}${part.title.slice(1)}`;
	const front = (id, title, description, generated) => ['---', `id: ${id}`, `title: ${JSON.stringify(title)}`, `description: ${JSON.stringify(description)}`, `tracks: [${part.tracks.join(', ')}]`, 'status: draft', `generated: ${generated}`, '---', ''];
	const index = [...front(`${part.slug}/index`, part.title, `The pages of the part "${part.title}": how they build on each other and what you can do after them.`, 'index'), prose.paragraph(5)];
	const review = [...front(`${part.slug}/review`, `Review: ${lower}`, `The questions of every page of the part "${part.title}", and exercises that use several of its pages together.`, 'review'),
		'## Cumulative exercises', '', prose.paragraph(2), ''];
	['Basic', 'Basic', 'Medium', 'Medium', 'Hard'].forEach((level, q) => review.push(`${q + 1}. **${level}.** ${prose.sentence().slice(0, -1)}?`, '', '   :::answer[Worked solution]', `   ${prose.paragraph(2)}`, '   :::', ''));
	return { index: `${index.join('\n')}\n`, review: `${review.join('\n').replace(/\n+$/, '')}\n` };
}

/**
 * The scale book's files from its inputs, without the pictures' bytes. `inputs`: the outline's data and the project's
 * sidebar; the glossary seed's entries; the engine's quotable files (`engineFiles`, `engineLines(file)`); the
 * reference tables present; the search queries; the sample sketches' text and output; the pin. Returns `{ files:
 * Map<relative path, text>, pictures, diagrams, counts }`.
 */
export function generateBook(inputs, { seed = 1, fraction = 1 } = {}) {
	const rng = createRandom(seed);
	const prose = new Prose(rng);
	const outline = indexOutline(inputs.outline);
	const rows = new Map(inputs.outline.pages.map((row) => [row.id, row]));
	const ordered = inputs.outline.pages;
	const { shares } = planBook(ordered, c_Totals, fraction);

	// The glossary: the seed's entries, then generated terms up to the total, each homed on a page that is no reference.
	const seedTerms = inputs.seedTerms.filter((term) => rows.has(term.home));
	const ids = new Set(seedTerms.map((term) => term.id));
	const queryWords = new Set(inputs.queries.map((query) => query.query.toLowerCase()));
	const homes = ordered.filter((row) => row.kind !== 'reference');
	const generated = [];
	const want = Math.max(seedTerms.length, Math.round(c_Totals.terms * fraction));
	const termNouns = ['map', 'set', 'list', 'rule', 'table', 'view', 'pass', 'path', 'node', 'unit', 'slot', 'key'];
	for (let attempt = 0; seedTerms.length + generated.length < want && attempt < want * 50; attempt++) {
		const term = `${rng.pick(c_Nouns)} ${rng.pick(c_Nouns)} ${rng.pick(termNouns)}`;
		const id = glossaryId(term);
		if (ids.has(id) || queryWords.has(term)) continue;
		ids.add(id);
		generated.push({ id, term, definition: `${prose.sentence().slice(0, -1)} in the ${rng.pick(c_Nouns)} ${rng.pick(c_Nouns)}.`, home: rng.pick(homes).id, aliases: [], avoid: [] });
	}
	const allTerms = [...seedTerms, ...generated];
	const homeTerms = new Map();
	for (const term of allTerms) {
		if (!homeTerms.has(term.home)) homeTerms.set(term.home, []);
		homeTerms.get(term.home).push(term);
	}

	// Who uses a primer: the pages whose Needs closure holds it (style.md §6.3, "Where the book uses it").
	const closures = new Map(ordered.map((row) => [row.id, needsClosure(outline, row.id)]));
	const usersOf = (primer) => {
		const users = ordered.filter((row) => row.id !== primer && closures.get(row.id).has(primer)).map((row) => row.id);
		if (users.length < 3) throw new Error(`scale: the primer ${primer} is in the Needs closure of only ${users.length} rows; "Where the book uses it" links three`);
		return [users[0], users[Math.floor(users.length / 2)], users[users.length - 1]];
	};
	const queriesFor = (id) => inputs.queries.filter((query) => query.page === id);
	// A page links one page per section: one of its Needs, else a page of its part, else any page.
	const linkTarget = (row) => {
		const candidates = row.needs.flatMap((need) => need.split('|')).filter((id) => rows.has(id));
		const same = ordered.filter((other) => other.part === row.part && other.id !== row.id);
		if (candidates.length && rng.random() < 0.5) return rng.pick(candidates);
		const pool = same.length ? same : ordered.filter((other) => other.id !== row.id);
		return pool.length ? rng.pick(pool).id : null;
	};
	const commandTables = [...inputs.referenceFiles].filter((file) => file.startsWith('commands-')).sort((a, b) => (a === 'commands-toolsets.md' ? -1 : b === 'commands-toolsets.md' ? 1 : a.localeCompare(b)));

	const ctx = {
		prose, rng, outline, rows, fraction, pin: inputs.pin, terms: allTerms, allTerms, homeTerms, usersOf, queriesFor,
		linkTarget,
		engineFiles: inputs.engineFiles, engineLines: inputs.engineLines, referenceFiles: inputs.referenceFiles, commandTables,
		sketchText: inputs.sketchText, sketchOutputs: inputs.sketchOutputs,
		pictureIndex: 0, counts: { quotes: 0, codeBlocks: 0, diagrams: 0, math: 0, words: 0 },
	};
	const files = new Map();
	const pictures = [];
	const diagrams = [];
	const sidebarParts = [];
	for (const part of inputs.outline.parts) {
		const pages = [];
		if (part.partPages) {
			const { index, review } = partPages(part, prose);
			files.set(`src/content/docs/${part.slug}/index.md`, index);
			files.set(`src/content/docs/${part.slug}/review.md`, review);
		}
		for (const id of part.pages) {
			const row = rows.get(id);
			const page = chapterPage(row, shares.get(id), ctx);
			files.set(`src/content/docs/${id}.md`, page.text);
			ctx.counts.words += proseWords(page.text.split('\n'));
			if (page.figures.length) files.set(`src/content/figures/${id}.json`, `${JSON.stringify({ figures: page.figures }, null, '\t')}\n`);
			if (page.tutorial) files.set(`tutorials/${id}.tutorial.json`, `${JSON.stringify(page.tutorial, null, '\t')}\n`);
			for (const sketch of page.sketches) files.set(`sketches/${sketch.name}`, inputs.sketchFile(sketch.from));
			pictures.push(...page.pictures);
			diagrams.push(...page.diagrams);
			pages.push(id);
		}
		const label = inputs.sidebar.parts.find((entry) => entry.slug === part.slug)?.label ?? part.title;
		sidebarParts.push({ slug: part.slug, label, pages: part.partPages ? [`${part.slug}/index`, ...pages, `${part.slug}/review`] : pages });
	}
	files.set('src/sidebar.json', `${JSON.stringify({ parts: sidebarParts, tracks: inputs.sidebar.tracks }, null, '\t')}\n`);
	files.set('src/content/glossary.json', `${JSON.stringify({ terms: allTerms }, null, '\t')}\n`);
	return { files, pictures, diagrams, counts: { ...ctx.counts, pages: ordered.length, terms: allTerms.length, pictures: pictures.length, crops: pictures.filter((picture) => picture.crop).length } };
}

// ---------------------------------------------------------------------------------------------------------------------
// Pictures: made from the samples' screenshots at the pin, encoded with scripts/encode-figures.mjs's settings.

/** A second deterministic stream per picture, so that a picture's pixels depend on its own index only. */
function pictureStream(index) {
	let state = ((index + 7) * 2246822519) >>> 0;
	return () => {
		state = (state * 1664525 + 1013904223) >>> 0;
		return state / 4294967296;
	};
}

/**
 * The pixels of a render: a screenshot cropped to 80-100 % of it at a place of its own, upscaled to 1920 x 1080, its
 * brightness and saturation moved a little, and a faint noise of one level, so every picture's bytes differ.
 */
export async function renderPixels(sharp, shot, job) {
	const next = pictureStream(job.source);
	const { width, height } = await sharp(shot.bytes).metadata();
	const scale = 0.8 + next() * 0.2;
	const cropWidth = Math.round(width * scale);
	const cropHeight = Math.min(height, Math.round((cropWidth * 9) / 16));
	const left = Math.floor(next() * (width - cropWidth + 1));
	const top = Math.floor(next() * (height - cropHeight + 1));
	const brightness = 0.92 + next() * 0.16 + (job.brighter ? 0.08 : 0);
	const pixels = await sharp(shot.bytes).extract({ left, top, width: cropWidth, height: cropHeight }).resize(c_RenderSize[0], c_RenderSize[1], { fit: 'fill', kernel: 'lanczos3' })
		.modulate({ brightness, saturation: 0.9 + next() * 0.2 }).removeAlpha().raw().toBuffer();
	let state = (job.source * 2654435761) >>> 0;
	for (let offset = 0; offset < pixels.length; offset++) {
		state = (state * 1664525 + 1013904223) >>> 0;
		const step = state >>> 30;
		if (step === 0 && pixels[offset] > 0) pixels[offset]--;
		else if (step === 3 && pixels[offset] < 255) pixels[offset]++;
	}
	return { pixels, width: c_RenderSize[0], height: c_RenderSize[1] };
}

/** The pixels of a picture of the interface: flat panels around a scene view that shows a screenshot. */
export async function interfacePixels(sharp, shot, job) {
	const [width, height] = c_InterfaceSize;
	const view = { left: 272, top: 40, width: 1056, height: 594 };
	const scene = await sharp(shot.bytes).resize(view.width, view.height, { fit: 'fill' }).removeAlpha().raw().toBuffer();
	const pixels = Buffer.alloc(width * height * 3);
	const next = pictureStream(job.source);
	const panel = 30 + Math.floor(next() * 12);
	for (let y = 0; y < height; y++) {
		for (let x = 0; x < width; x++) {
			const offset = (y * width + x) * 3;
			const header = y < 28;
			const border = x === 270 || x === 1330 || y === 640;
			// Rows of "text": short bars in the side panels, as a list of names would draw them.
			const text = (x < 260 || x > 1340) && y > 40 && (y % 22) > 8 && (y % 22) < 14 && ((x + y * 7) % 180) < 120 + ((y * 13) % 50);
			const value = header ? 22 : border ? 60 : text ? 190 : panel;
			pixels[offset] = value;
			pixels[offset + 1] = value;
			pixels[offset + 2] = value + (header ? 6 : 0);
		}
	}
	for (let y = 0; y < view.height; y++) scene.copy(pixels, ((view.top + y) * width + view.left) * 3, y * view.width * 3, (y + 1) * view.width * 3);
	return { pixels, width, height };
}

function sha256(bytes) {
	return createHash('sha256').update(bytes).digest('hex');
}

/** Encodes one picture as scripts/encode-figures.mjs does, from raw pixels. */
async function encode(sharp, { pixels, width, height }, settings) {
	const image = sharp(pixels, { raw: { width, height, channels: 3 } });
	return settings.lossless
		? image.webp({ lossless: true, effort: settings.effort }).toBuffer()
		: image.avif({ quality: settings.quality, chromaSubsampling: settings.chromaSubsampling, effort: settings.effort, lossless: false }).toBuffer();
}

/**
 * Makes a picture job's files (its published picture and, for a render with a crop, the crop): from the cache when it
 * holds them, otherwise made and encoded and put in the cache. Returns `[{ name, bytes, original, size, encoder }]`.
 */
export async function makePicture(sharp, job, screenshots, cacheDir) {
	const shot = screenshots[job.source % screenshots.length];
	const settings = c_Encoders[job.encoder];
	const versions = { sharp: sharp.versions.sharp, libvips: sharp.versions.vips };
	const key = sha256(JSON.stringify({ v: 1, shot: shot.sha256, job: { source: job.source, kind: job.kind, brighter: !!job.brighter, crop: job.crop }, settings, versions }));
	const recordFile = path.join(cacheDir, `${key}.json`);
	// The names are the job's: the cache keeps only what the pixels decide, which other figures of other runs may share.
	const name = `${[job.figure, job.variant].filter(Boolean).join('-')}.${settings.format}`;
	const names = [name, ...(job.crop ? [`${job.figure}-${job.crop}.webp`] : [])];
	if (existsSync(recordFile)) {
		const record = JSON.parse(readFileSync(recordFile, 'utf8'));
		return record.map((entry, index) => ({ ...entry, name: names[index], bytes: readFileSync(path.join(cacheDir, entry.cache)) }));
	}
	const picture = job.kind === 'editor' ? await interfacePixels(sharp, shot, job) : await renderPixels(sharp, shot, job);
	const original = sha256(await sharp(picture.pixels, { raw: { width: picture.width, height: picture.height, channels: 3 } }).png({ compressionLevel: 1 }).toBuffer());
	const made = [{ name, bytes: await encode(sharp, picture, settings), original, size: [picture.width, picture.height], encoder: { ...settings, ...versions }, crop: null }];
	if (job.crop) {
		const [x0, y0, x1, y1] = cropPixels(c_CropRect, picture.width, picture.height);
		const cropWidth = x1 - x0;
		const cropHeight = y1 - y0;
		const pixels = Buffer.alloc(cropWidth * cropHeight * 3);
		for (let y = 0; y < cropHeight; y++) picture.pixels.copy(pixels, y * cropWidth * 3, ((y0 + y) * picture.width + x0) * 3, ((y0 + y) * picture.width + x1) * 3);
		const cropped = { pixels, width: cropWidth, height: cropHeight };
		const cropOriginal = sha256(await sharp(pixels, { raw: { width: cropWidth, height: cropHeight, channels: 3 } }).png({ compressionLevel: 1 }).toBuffer());
		made.push({ name: names[1], bytes: await encode(sharp, cropped, c_Encoders.lossless), original: cropOriginal, size: [cropWidth, cropHeight], encoder: { ...c_Encoders.lossless, ...versions }, crop: job.crop });
	}
	mkdirSync(cacheDir, { recursive: true });
	const record = made.map((entry, index) => {
		const cache = `${key}-${index}.${path.extname(entry.name).slice(1)}`;
		writeFileSync(path.join(cacheDir, cache), entry.bytes);
		const { bytes, name: own, ...rest } = entry;
		return { ...rest, cache };
	});
	writeFileSync(recordFile, JSON.stringify(record));
	return made;
}

/** A stamp of figures-format.md §4 for a generated picture: taken from the samples' screenshots, not by the editor. */
export function stampRecord(job, made, pin) {
	return {
		figure: job.figure,
		variant: job.variant,
		crop: made.crop,
		kind: job.kind,
		pin: pin.commit,
		build: { kind: 'pin-build', configuration: 'Release', editorSha256: sha256('the scale test: made from the samples\' screenshots, not by an editor') },
		reportedCommit: pin.commit.slice(0, 12),
		os: 'Windows',
		gpu: null,
		size: made.size,
		original: made.original,
		sha256: sha256(made.bytes),
		encoder: made.encoder,
		recorded: {},
		checkedAt: [],
	};
}

// ---------------------------------------------------------------------------------------------------------------------
// The command.

class UsageError extends Error {}

function option(argv, name, fallback) {
	const index = argv.indexOf(name);
	if (index < 0) return fallback;
	if (index + 1 >= argv.length) throw new UsageError(`${name} needs a value`);
	return argv[index + 1];
}

function git(engine, args, encoding = 'utf8') {
	return execFileSync('git', ['-C', engine, ...args], { encoding, maxBuffer: 256 * 1024 * 1024 });
}

/** The engine's quotable files at the pin: the .cpp and .h files of the engine and the editor of 80 lines or more. */
function engineSources(engine, commit, rng, count = 320) {
	const all = git(engine, ['ls-tree', '-r', '--name-only', commit, '--', 'Strata/src', 'StrataEditor/src']).split('\n').filter((file) => /\.(cpp|h)$/.test(file)).sort();
	if (!all.length) throw new Error(`the engine at ${commit} has no files under Strata/src or StrataEditor/src`);
	const chosen = [];
	const lines = new Map();
	for (let attempt = 0; chosen.length < count && attempt < count * 20; attempt++) {
		const file = rng.pick(all);
		if (lines.has(file)) continue;
		const text = git(engine, ['show', `${commit}:${file}`]).replace(/\r\n/g, '\n').replace(/\n$/, '').split('\n');
		lines.set(file, text);
		if (text.length >= 80 && !text.some((line) => line.includes('```'))) chosen.push(file);
	}
	return { files: chosen, lines: (file) => lines.get(file) };
}

/** The samples' screenshots at the pin, as PNG bytes, in the order of their paths. */
function sampleScreenshots(engine, commit) {
	const files = git(engine, ['ls-tree', '-r', '--name-only', commit, '--', 'Samples']).split('\n').filter((file) => /\/Screenshots\/[^/]+\.png$/.test(file)).sort();
	if (!files.length) throw new Error(`the engine at ${commit} has no Samples/*/Screenshots/*.png`);
	return files.map((file) => {
		const bytes = git(engine, ['show', `${commit}:${file}`], 'buffer');
		return { file, bytes, sha256: sha256(bytes) };
	});
}

/** Copies the project's code into the scale site, without its content, pictures, diagrams and tutorials. */
function copyProject(out) {
	const skip = /^(src[\\/](content[\\/](docs|figures|glossary\.json)|assets[\\/]figures|generated[\\/]diagrams)|tutorials|public[\\/]downloads)([\\/]|$)|__pycache__/;
	for (const item of ['astro.config.mjs', 'ec.config.mjs', 'package.json', 'engine.pin', 'site.json', 'LICENSE', '.markdownlint-cli2.jsonc', '_typos.toml', 'public', 'sketches', 'tools', 'scripts', 'src', 'reference']) {
		if (!existsSync(path.join(c_Root, item))) continue;
		cpSync(path.join(c_Root, item), path.join(out, item), { recursive: true, filter: (source) => !skip.test(path.relative(c_Root, source)) });
	}
	for (const page of ['index.md', '404.md']) cpSync(path.join(c_Root, 'src', 'content', 'docs', page), path.join(out, 'src', 'content', 'docs', page));
}

async function main(argv) {
	const engine = option(argv, '--engine', process.env.STRATA_ENGINE);
	if (!engine) throw new UsageError('name the pin clone with --engine <folder> (or set STRATA_ENGINE)');
	const out = path.resolve(option(argv, '--out', path.join(c_Root, '.tools', 'scale', 'site')));
	const cacheDir = path.resolve(option(argv, '--cache', path.join(c_Root, '.tools', 'scale', 'cache')));
	const seed = Number(option(argv, '--seed', '1'));
	const fraction = Number(option(argv, '--fraction', '1'));
	const jobs = Number(option(argv, '--jobs', '4'));
	if (!Number.isInteger(seed) || !(fraction > 0 && fraction <= 1) || !Number.isInteger(jobs) || jobs < 1) throw new UsageError('--seed is a whole number, --fraction a number above 0 and at most 1, --jobs a whole number of 1 or more');
	if (!path.relative(c_Root, out) || path.relative(c_Root, out).startsWith('..')) throw new UsageError(`--out must be a folder inside this project, so that the copy finds its packages: ${out}`);
	const started = Date.now();
	const pin = parsePin(readFileSync(path.join(c_Root, 'engine.pin'), 'utf8'));
	const rng = createRandom(seed + 1000);
	const sources = engineSources(engine, pin.commit, rng);
	const referenceDir = path.join(c_Root, 'src', 'generated', 'reference');
	const referenceFiles = new Set(existsSync(referenceDir) ? readdirSync(referenceDir).filter((file) => file.endsWith('.md')) : []);
	if (!referenceFiles.size) console.log('scale: src/generated/reference/ holds no table; the reference pages hold generated prose only');
	const seedFile = path.join(c_Root, 'plan', 'glossary', 'seed.json');
	const seedTerms = existsSync(seedFile) ? JSON.parse(readFileSync(seedFile, 'utf8')).terms : [];
	if (!seedTerms.length) console.log('scale: plan/glossary/seed.json is absent; the glossary holds generated terms only');
	const sketchOutputs = new Map();
	for (const [name, page] of c_SampleSketches) {
		const output = sketchOutput(readFileSync(path.join(c_Root, 'src', 'content', 'docs', `${page}.md`), 'utf8'), name);
		if (!output) throw new Error(`src/content/docs/${page}.md shows no output of sketches/${name}`);
		sketchOutputs.set(name, output);
	}
	const sketchFile = (name) => readFileSync(path.join(c_Root, 'sketches', name), 'utf8');
	const book = generateBook({
		outline: JSON.parse(readFileSync(path.join(c_Root, 'src', 'generated', 'outline.json'), 'utf8')),
		sidebar: JSON.parse(readFileSync(path.join(c_Root, 'src', 'sidebar.json'), 'utf8')),
		seedTerms,
		queries: JSON.parse(readFileSync(path.join(c_Root, 'scripts', 'search-queries.json'), 'utf8')).queries,
		engineFiles: sources.files,
		engineLines: sources.lines,
		referenceFiles,
		sketchText: (name) => sketchFile(name).replace(/\r\n/g, '\n').replace(/\n+$/, '').split('\n'),
		sketchFile,
		sketchOutputs,
		pin,
	}, { seed, fraction });

	console.log(`scale: writing ${book.counts.pages} pages to ${out}`);
	rmSync(out, { recursive: true, force: true });
	mkdirSync(out, { recursive: true });
	copyProject(out);
	for (const [relative, text] of book.files) {
		const file = path.join(out, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, text);
	}
	const { default: sharp } = await import('sharp');
	const screenshots = sampleScreenshots(engine, pin.commit);
	const stamps = new Map();
	let next = 0;
	let bytes = 0;
	await Promise.all(Array.from({ length: jobs }, async () => {
		while (next < book.pictures.length) {
			const job = book.pictures[next++];
			for (const made of await makePicture(sharp, job, screenshots, cacheDir)) {
				const folder = path.join(out, 'src', 'assets', 'figures', ...job.page.split('/'));
				mkdirSync(folder, { recursive: true });
				writeFileSync(path.join(folder, made.name), made.bytes);
				bytes += made.bytes.length;
				if (!stamps.has(job.page)) stamps.set(job.page, {});
				stamps.get(job.page)[made.name] = stampRecord(job, made, pin);
			}
		}
	}));
	for (const [page, files] of stamps) {
		const sorted = Object.fromEntries(Object.keys(files).sort().map((name) => [name, files[name]]));
		writeFileSync(path.join(out, 'src', 'assets', 'figures', ...page.split('/'), 'taken.json'), `${JSON.stringify({ files: sorted }, null, '\t')}\n`);
	}
	const { counts } = book;
	console.log(`scale: ${counts.pages} pages, ${counts.words} words of prose, ${counts.quotes} quotes, ${counts.codeBlocks} code blocks, ${counts.diagrams} diagrams, ${counts.math} formulas, ${counts.terms} terms, ${counts.pictures} pictures and ${counts.crops} crops (${(bytes / 1048576).toFixed(1)} MB) in ${((Date.now() - started) / 1000).toFixed(0)} s`);
	return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
	try {
		process.exitCode = await main(process.argv.slice(2));
	} catch (error) {
		console.error(`scale: ${error.message}`);
		process.exitCode = error instanceof UsageError ? 2 : 1;
	}
}

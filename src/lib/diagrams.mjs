// Mermaid diagrams (plan/site.md "Diagrams"). `npm run diagrams` (scripts/diagrams.mjs) draws each diagram once, in
// the light theme and in the dark one, in a headless Chromium (mermaid-isomorphic and Playwright), and writes
// src/generated/diagrams/<hash>-light.svg and <hash>-dark.svg, which are committed; the site build reads them and
// starts no browser. <hash> is the first 16 hex digits of the SHA-256 of the renderer's key (the versions and settings
// below) and the diagram's text (LF line ends, trimmed), so that a changed text or a changed setting means new files.
// Each file starts with a stamp line naming the renderer's key, the diagram, the theme and the SHA-256 of the rest of
// the file, so that `npm run diagrams -- --check` tells a drawing of the renderer from a stale or hand-edited one
// without a browser. The dev server draws a missing diagram itself (src/plugins/mermaid.mjs).

import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { mkdir, mkdtemp, readdir, readFile, rename, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);

/** The installed version of a package, read from its package.json (which some packages do not export). */
function packageVersion(name) {
	for (const folder of require.resolve.paths(name) ?? []) {
		try {
			return JSON.parse(readFileSync(path.join(folder, name, 'package.json'), 'utf8')).version;
		} catch (error) {
			if (error.code !== 'ENOENT') throw error;
		}
	}
	throw new Error(`the package ${name} is not installed: run npm ci`);
}

const c_Versions = {
	mermaid: packageVersion('mermaid'),
	renderer: packageVersion('mermaid-isomorphic'),
	// Playwright pins the Chromium that measures the text.
	playwright: packageVersion('playwright'),
	inter: packageVersion('@fontsource-variable/inter'),
};
const c_FontFile = require.resolve('@fontsource-variable/inter/files/inter-latin-wght-normal.woff2');

// Diagrams are drawn in the font the site uses for its interface, loaded into the rendering page, so that the boxes
// Mermaid measures fit the text the reader's browser draws with the page's own Inter; no font is embedded.
export const c_FontFamily = '"Inter Variable", system-ui, sans-serif';
// The themes' own colors where they fall under 4.5:1 (`npm run diagrams -- --contrast` measures them): notes get a
// lighter box with dark text in the light theme, and a darker box with lighter text in the dark one, where Mermaid
// also draws an edge label's box at half opacity, which is drawn solid and darker under lighter text. The label's
// CSS color and background color say the same as its paint: Mermaid's dark theme gives the label's group a CSS
// background of #585858 and its text the color #ccc, which no SVG draws but which axe reads (4.43:1).
export const c_Themes = {
	light: { theme: 'neutral', themeVariables: { noteBkgColor: '#fff5ad', noteTextColor: '#333333' } },
	dark: {
		theme: 'dark',
		themeVariables: { noteBkgColor: '#2e2e2e', noteTextColor: '#e6e6e6' },
		themeCSS: '.edgeLabel { background-color: #2e2e2e !important; } .edgeLabel rect { opacity: 1 !important; fill: #2e2e2e !important; } .edgeLabel text, .edgeLabel tspan { fill: #e6e6e6 !important; color: #e6e6e6 !important; }',
	},
};
// Labels are SVG text (htmlLabels false): no HTML inside the drawing, which the page inlines as SVG. The fixed seed
// makes the shapes Mermaid draws through rough.js the same at every run, so a drawing depends only on its text.
// The box of a sequence diagram's "loop", "alt" or "opt" is 24 pixels high, not Mermaid's 20, which a descender of
// Inter at 16 pixels ("loop", "opt") crosses (`node scripts/diagram-checks.mjs` measures it).
export const c_Common = { fontFamily: c_FontFamily, securityLevel: 'strict', htmlLabels: false, handDrawnSeed: 1, flowchart: { useMaxWidth: true }, sequence: { useMaxWidth: true, labelBoxHeight: 24 } };
// How the ids of a drawing are written (renameDiagramIds); part of the key, so that a change draws every diagram again.
const c_IdScheme = 3;
const c_BatchPrefix = 'strata-diagram-batch';
export const c_ThemeNames = ['light', 'dark'];

export const c_RendererKey = createHash('sha256').update(JSON.stringify({ c_Versions, c_Themes, c_Common, c_IdScheme })).digest('hex').slice(0, 16);

/** A diagram's text as it is hashed and drawn: LF line ends, without the blank space around it. */
export function normalizeSource(source) {
	return String(source).replace(/\r\n?/g, '\n').trim();
}

/** The hash a diagram's files are named by: 16 hex digits of the SHA-256 of the renderer's key and the text. */
export function diagramHash(source, rendererKey = c_RendererKey) {
	return createHash('sha256').update(`${rendererKey}\n${normalizeSource(source)}\n`).digest('hex').slice(0, 16);
}

/** The two files of a diagram: `{ light, dark }`. */
export function diagramFiles(dir, hash) {
	return Object.fromEntries(c_ThemeNames.map((theme) => [theme, path.join(dir, `${hash}-${theme}.svg`)]));
}

/** The prefix of every id inside one drawing ("dg-<hash>-light"): a letter first, so that the drawing's CSS selects it. */
export function idPrefix(hash, theme) {
	return `dg-${hash}-${theme}`;
}

const c_Stamp = /^<!-- drawn by scripts\/diagrams\.mjs; renderer ([0-9a-f]{16}); diagram ([0-9a-f]{16}); theme (light|dark); sha256 ([0-9a-f]{64}); do not edit -->$/;

/** A drawing's file: its stamp line, then the SVG. */
export function drawingFile({ hash, theme, svg, rendererKey = c_RendererKey }) {
	const body = `${svg}\n`;
	const digest = createHash('sha256').update(body).digest('hex');
	return `<!-- drawn by scripts/diagrams.mjs; renderer ${rendererKey}; diagram ${hash}; theme ${theme}; sha256 ${digest}; do not edit -->\n${body}`;
}

/**
 * Reads a drawing's file: `{ stamp: { renderer, diagram, theme, sha256 }, svg, intact }` (intact: the rest of the file
 * has the stamp's SHA-256), or `{ error }` when the first line is no stamp.
 */
export function parseDrawing(text) {
	const newline = text.indexOf('\n');
	const first = newline < 0 ? text : text.slice(0, newline);
	const match = c_Stamp.exec(first);
	if (!match) return { error: 'its first line is not the stamp scripts/diagrams.mjs writes' };
	const body = text.slice(newline + 1);
	const stamp = { renderer: match[1], diagram: match[2], theme: match[3], sha256: match[4] };
	return { stamp, svg: body.replace(/\n$/, ''), intact: createHash('sha256').update(body).digest('hex') === stamp.sha256 };
}

async function readOptional(file) {
	try {
		return await readFile(file, 'utf8');
	} catch (error) {
		if (error.code === 'ENOENT') return null;
		throw error;
	}
}

/**
 * The committed drawings of a diagram: `{ hash, light, dark }` (the SVGs without their stamps), or `{ hash, missing }`
 * (the themes without a file), or `{ hash, error }` when a file is not the drawing of this diagram.
 */
export async function readDrawings(dir, source) {
	const hash = diagramHash(source);
	const files = diagramFiles(dir, hash);
	const result = { hash };
	const missing = [];
	for (const theme of c_ThemeNames) {
		const content = await readOptional(files[theme]);
		if (content === null) {
			missing.push(theme);
			continue;
		}
		const drawing = parseDrawing(content);
		const name = path.basename(files[theme]);
		if (drawing.error) return { hash, error: `src/generated/diagrams/${name}: ${drawing.error}: draw it again with npm run diagrams` };
		if (drawing.stamp.diagram !== hash || drawing.stamp.theme !== theme || drawing.stamp.renderer !== c_RendererKey) return { hash, error: `src/generated/diagrams/${name}: its stamp names another diagram, theme or renderer: draw it again with npm run diagrams` };
		if (!drawing.intact) return { hash, error: `src/generated/diagrams/${name} was edited after it was drawn: draw it again with npm run diagrams` };
		result[theme] = drawing.svg;
	}
	if (missing.length) return { hash, missing };
	return result;
}

/**
 * What the build refuses in a diagram's text, before it is drawn: an accessible name of Mermaid's own (accTitle,
 * accDescr), because the fence's alt="…" is the drawing's name (style.md §11).
 */
export function sourceProblems(source) {
	const problems = [];
	if (/^\s*acc(Title|Descr)\b/m.test(normalizeSource(source))) problems.push('a diagram is named by the fence\'s alt="…" and caption="…": remove accTitle and accDescr from its text');
	// A gantt task's tags stand between its colon and its id: "crit" draws its label under 4.5:1 in both themes.
	if (diagramType(source) === 'gantt' && /^[^:\n]+:\s*(?:\w+\s*,\s*)*crit\b/m.test(normalizeSource(source))) problems.push('a task marked crit draws its label under 4.5:1 in both themes: mark it done or active, or leave it plain');
	return problems;
}

function escapeRegExp(value) {
	return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Gives a rendered SVG ids of its own, all starting with `id` ("dg-<hash>-light"), so that the light and the dark copy
 * of a diagram, and two diagrams of one page, share no id. Mermaid names a diagram "<prefix>-<index in its batch>" and
 * derives most inner ids and style selectors from it; sequence diagrams also write ids of their own ("actor0",
 * "root-0"), which get `id` in front, with every reference to them: url(#…), href="#…", aria-labelledby and
 * aria-describedby, and "#…" selectors in the SVG's style sheets.
 */
export function renameDiagramIds(svg, batchId, id) {
	let result = svg.replace(new RegExp(`${escapeRegExp(batchId)}(?![0-9])`, 'g'), id);
	const others = new Set();
	for (const match of result.matchAll(/\sid="([^"]+)"/g)) if (!match[1].startsWith(id)) others.add(match[1]);
	if (others.size === 0) return result;
	const names = [...others].sort((a, b) => b.length - a.length).map(escapeRegExp).join('|');
	const renamed = (name) => `${id}-${name}`;
	result = result.replace(new RegExp(`(\\sid="|url\\(#|href="#)(${names})(?=["')])`, 'g'), (match, lead, name) => `${lead}${renamed(name)}`);
	result = result.replace(/(aria-(?:labelledby|describedby)=")([^"]*)"/g, (match, lead, list) => `${lead}${list.split(/\s+/).map((name) => (others.has(name) ? renamed(name) : name)).join(' ')}"`);
	const selector = new RegExp(`#(${names})(?![\\w-])`, 'g');
	return result.replace(/(<style[^>]*>)([\s\S]*?)(<\/style>)/g, (match, open, css, close) => `${open}${css.replace(selector, (whole, name) => `#${renamed(name)}`)}${close}`);
}

function escapeHtml(value) {
	return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * Drops the declarations of a drawing's <style> that paint with an element the drawing does not hold. Mermaid's style
 * sheet styles the shapes of every look, and those of the "neo" look paint with a gradient (url(#…-gradient)) that only
 * a drawing in that look defines: in the others it is a reference to nothing, which gate (a)'s link check (lychee
 * --include-fragments) rightly reports as a missing fragment of the page.
 */
export function dropDanglingPaint(svg) {
	const ids = new Set([...svg.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
	const declaration = /[a-z-]+\s*:\s*url\(\s*#([^)\s]+)\s*\)[^;}]*;?/gi;
	return svg.replace(/(<style[^>]*>)([\s\S]*?)(<\/style>)/g, (match, open, css, close) => `${open}${css.replace(declaration, (whole, id) => (ids.has(id) ? whole : ''))}${close}`);
}

/** The rules of a style sheet at its top level: `{ text, selectors, block }` (block: an at-rule with its braces). */
function cssRules(css) {
	const rules = [];
	let position = 0;
	while (position < css.length) {
		const open = css.indexOf('{', position);
		if (open < 0) {
			rules.push({ text: css.slice(position), selectors: null, block: true });
			break;
		}
		let depth = 0;
		let end = open;
		for (; end < css.length; end++) {
			if (css[end] === '{') depth++;
			else if (css[end] === '}' && --depth === 0) break;
		}
		const text = css.slice(position, end + 1);
		const prelude = css.slice(position, open).trim();
		rules.push({ text, prelude, block: prelude.startsWith('@') });
		position = end + 1;
	}
	return rules;
}

/** The selectors of a selector list, split at the commas outside parentheses and brackets. */
function splitSelectors(prelude) {
	const selectors = [];
	let depth = 0;
	let start = 0;
	for (let index = 0; index < prelude.length; index++) {
		const character = prelude[index];
		if (character === '(' || character === '[') depth++;
		else if (character === ')' || character === ']') depth--;
		else if (character === ',' && depth === 0) {
			selectors.push(prelude.slice(start, index));
			start = index + 1;
		}
	}
	selectors.push(prelude.slice(start));
	return selectors;
}

/**
 * A drawing without the markup it never paints with, which the page would otherwise carry twice per diagram (both
 * themes) and again in its part's print view (rulings-13, R59): the rules of its style sheets whose every selector
 * needs a class or an id the drawing does not hold (Mermaid's sheet styles every shape of every diagram type), the
 * keyframes no remaining rule or attribute names, the markers nothing points at (url(#…) or href="#…"), the data-
 * attributes no selector reads (Mermaid keeps the edges' points and ids in them for its scripts, which the book does
 * not run), and empty style attributes. What is drawn stays the same: every element and every rule that can match one
 * is kept.
 */
export function compactDrawing(svg) {
	let result = svg;
	const sheets = () => [...result.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((match) => match[1]).join('\n');
	// Markers that nothing points at.
	for (const match of [...result.matchAll(/<marker\b[^>]*\sid="([^"]+)"[^>]*>[\s\S]*?<\/marker>/g)]) {
		const id = escapeRegExp(match[1]);
		const outside = result.replace(match[0], '');
		if (!new RegExp(`url\\(\\s*#${id}\\s*\\)|href="#${id}"`).test(outside)) result = result.replace(match[0], '');
	}
	// Data attributes that no selector of the style sheets reads.
	const read = new Set([...sheets().matchAll(/\[(data-[\w-]+)/g)].map((match) => match[1]));
	result = result.replace(/\s(data-[\w-]+)="[^"]*"/g, (whole, name) => (read.has(name) ? whole : ''));
	result = result.replace(/\sstyle="\s*;?\s*"/g, '');
	// Rules whose every selector needs a class or an id that no element of the drawing has.
	const classes = new Set();
	for (const match of result.matchAll(/\sclass="([^"]*)"/g)) for (const name of match[1].split(/\s+/)) if (name) classes.add(name);
	const ids = new Set([...result.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
	// A selector with a functional pseudo-class (:not(.x), :is(…)) is kept whole: a class it names may be one it excludes.
	const alive = (selector) => selector.includes('(') || [...selector.matchAll(/\.(-?[_a-zA-Z][\w-]*)/g)].every((match) => classes.has(match[1]))
		&& [...selector.matchAll(/#(-?[_a-zA-Z][\w-]*)/g)].every((match) => ids.has(match[1]));
	result = result.replace(/(<style[^>]*>)([\s\S]*?)(<\/style>)/g, (match, open, css, close) => {
		const kept = cssRules(css).filter((rule) => rule.block || splitSelectors(rule.prelude).some(alive));
		return `${open}${kept.map((rule) => rule.text).join('')}${close}`;
	});
	// Keyframes that no remaining rule or attribute names.
	result = result.replace(/(<style[^>]*>)([\s\S]*?)(<\/style>)/g, (match, open, css, close) => {
		const rules = cssRules(css);
		const kept = rules.filter((rule) => {
			const name = /^@keyframes\s+([\w-]+)/.exec(rule.prelude ?? '')?.[1];
			if (!name) return true;
			const elsewhere = result.replace(rule.text, '');
			return new RegExp(`(^|[^\\w-])${escapeRegExp(name)}([^\\w-]|$)`).test(elsewhere);
		});
		return `${open}${kept.map((rule) => rule.text).join('')}${close}`;
	});
	return result;
}

/**
 * A committed drawing as the page inlines it: the SVG is an image whose accessible name is the fence's alt text
 * (role="img", aria-label and a <title>), instead of Mermaid's document role and its description of the diagram type.
 * `occurrence` (2, 3, …) renames the drawing's ids when the same diagram stands on the page more than once. Paint that
 * names an element the drawing lacks is dropped (dropDanglingPaint), and so is the markup it never paints with
 * (compactDrawing).
 */
export function inlineDrawing(svg, { hash, theme, alt, occurrence = 1 }) {
	let result = compactDrawing(dropDanglingPaint(svg));
	if (occurrence > 1) {
		const prefix = idPrefix(hash, theme);
		result = result.replace(new RegExp(`${escapeRegExp(prefix)}(?![0-9a-z])`, 'g'), `${prefix}-${occurrence}`);
	}
	const open = /<svg\b[^>]*>/.exec(result);
	if (!open) throw new Error(`the drawing ${hash}-${theme}.svg holds no <svg> element`);
	const attributes = open[0]
		.replace(/\s(?:role|aria-roledescription|aria-label|aria-labelledby|aria-describedby)="[^"]*"/g, '')
		.replace(/^<svg\b/, `<svg role="img" aria-label="${escapeHtml(alt)}"`);
	return `${result.slice(0, open.index)}${attributes}<title>${escapeHtml(alt)}</title>${result.slice(open.index + open[0].length)}`;
}

let s_Renderer = null;

async function renderer() {
	if (!s_Renderer) {
		const { createMermaidRenderer } = await import('mermaid-isomorphic');
		s_Renderer = createMermaidRenderer({ launchOptions: { headless: true } });
	}
	return s_Renderer;
}

/**
 * Draws diagrams in both themes, `items` holding `{ source, where: ["core/time.md:42", …] }`: `{ drawn: [{ hash,
 * light, dark, source }], failures: ["<where>: <why>"] }`. The ids of each drawing are renamed (renameDiagramIds). One
 * browser draws them all; nothing is written.
 */
export async function drawDiagrams(items) {
	const failures = [];
	const valid = [];
	for (const item of items) {
		const problems = sourceProblems(item.source);
		if (problems.length) failures.push(...problems.map((problem) => `${item.where.join(', ')}: ${problem}`));
		else valid.push(item);
	}
	if (valid.length === 0) return { drawn: [], failures };
	const folder = await mkdtemp(path.join(tmpdir(), 'strata-diagrams-'));
	try {
		const css = path.join(folder, 'font.css');
		await writeFile(css, `@font-face { font-family: 'Inter Variable'; font-style: normal; font-weight: 100 900; src: url('${pathToFileURL(c_FontFile).href}') format('woff2'); }\n`);
		const render = await renderer();
		const sources = valid.map((item) => normalizeSource(item.source));
		// Both themes in one browser: the renderer keeps its browser open while a call is running.
		const results = await Promise.all(c_ThemeNames.map((theme) => render(sources, { css: pathToFileURL(css), prefix: c_BatchPrefix, mermaidConfig: { ...c_Common, ...c_Themes[theme] } })));
		const drawn = [];
		valid.forEach((item, index) => {
			const rejected = results.map((themed) => themed[index]).find((result) => result.status === 'rejected');
			if (rejected) {
				const message = String(rejected.reason?.message ?? rejected.reason).split('\n').slice(0, 4).join(' ');
				failures.push(`${item.where.join(', ')}: Mermaid cannot draw this diagram: ${message}`);
				return;
			}
			const hash = diagramHash(item.source);
			const entry = { hash, source: item.source };
			c_ThemeNames.forEach((theme, themeIndex) => {
				const value = results[themeIndex][index].value;
				entry[theme] = renameDiagramIds(value.svg, value.id, idPrefix(hash, theme));
			});
			drawn.push(entry);
		});
		return { drawn, failures };
	} finally {
		await rm(folder, { recursive: true, force: true });
	}
}

/** Writes the two files of each drawn diagram into `dir` (each written whole, through a partial file). */
export async function writeDrawings(dir, drawn) {
	await mkdir(dir, { recursive: true });
	for (const entry of drawn) {
		const files = diagramFiles(dir, entry.hash);
		for (const theme of c_ThemeNames) {
			const partial = `${files[theme]}.${process.pid}.partial`;
			await writeFile(partial, drawingFile({ hash: entry.hash, theme, svg: entry[theme] }));
			await rename(partial, files[theme]);
		}
	}
}

/** The diagrams of a book's page index: `{ source, meta, where }` for every fence, generated ones included. */
export function bookDiagrams(index) {
	const diagrams = [];
	for (const page of index.pages.values()) {
		for (const diagram of page.diagrams ?? []) diagrams.push({ source: diagram.source, meta: diagram.meta ?? '', where: `src/content/docs/${page.relative}:${diagram.line}` });
	}
	return diagrams;
}

/** The diagrams grouped by hash: `[{ hash, source, where: [places] }]`, in the order they are first met. */
export function groupDiagrams(diagrams) {
	const groups = new Map();
	for (const diagram of diagrams) {
		const hash = diagramHash(diagram.source);
		if (!groups.has(hash)) groups.set(hash, { hash, source: diagram.source, where: [] });
		groups.get(hash).where.push(diagram.where);
	}
	return [...groups.values()];
}

/** The drawings `dir` holds: `Map<file name, { hash, theme }>` of every "<hash>-<theme>.svg", and the other files. */
export async function listDrawings(dir) {
	let names;
	try {
		names = await readdir(dir);
	} catch (error) {
		if (error.code === 'ENOENT') return { drawings: new Map(), others: [] };
		throw error;
	}
	const drawings = new Map();
	const others = [];
	for (const name of names.sort()) {
		const match = /^([0-9a-f]{16})-(light|dark)\.svg$/.exec(name);
		if (match) drawings.set(name, { hash: match[1], theme: match[2] });
		else others.push(name);
	}
	return { drawings, others };
}

// The diagram types the book draws, each with every kind of element it has, for `npm run diagrams -- --contrast`:
// every text of these, in both themes, must stand at 4.5:1 or more against what lies behind it. A page may use only
// these types (`--check` fails on another), so that every drawing's colors were measured.
export const c_ContrastFixtures = {
	flowchart: [
		'flowchart LR',
		'    A[Rectangle] -->|a label| B(Rounded)',
		'    B --> C([Stadium]) -.->|dotted| D[[Subroutine]]',
		'    D ==>|thick| E[(Database)] --> F((Circle))',
		'    F --- G>Flag] --> H{Decision}',
		'    H -->|yes| I{{Hexagon}} --> J[/Parallel/]',
		'    H -->|no| K[\\Back/] --> L[/Trapezoid\\] --> M(((Double)))',
		'    subgraph S [A group of nodes]',
		'        direction TB',
		'        N[Inside] --> O[Also inside]',
		'    end',
		'    M --> S',
	].join('\n'),
	sequenceDiagram: [
		'sequenceDiagram',
		'    autonumber',
		'    actor U as A person',
		'    participant F as Frame loop',
		'    participant S as Scene',
		'    U->>F: a message',
		'    F-->>U: a dotted reply',
		'    F-)S: an open arrow',
		'    F-xS: a cross',
		'    Note left of U: a note on the left',
		'    Note over F,S: a note over two',
		'    activate S',
		'    loop while steps remain',
		'        S->>S: step',
		'    end',
		'    alt the first case',
		'        S->>F: one',
		'    else the other case',
		'        S->>F: two',
		'    end',
		'    opt only sometimes',
		'        F->>S: three',
		'    end',
		'    par at once',
		'        F->>S: four',
		'    and the other',
		'        F->>U: five',
		'    end',
		'    critical must happen',
		'        S->>F: six',
		'    end',
		'    break when it fails',
		'        S->>U: seven',
		'    end',
		'    rect rgb(128, 128, 128, 0.1)',
		'        F->>S: inside a box',
		'    end',
		'    deactivate S',
	].join('\n'),
	stateDiagram: [
		'stateDiagram-v2',
		'    [*] --> Idle',
		'    Idle --> Running: start',
		'    state Running {',
		'        [*] --> Stepping',
		'        Stepping --> Drawing: a step ran',
		'        Drawing --> Stepping',
		'    }',
		'    state choice <<choice>>',
		'    Running --> choice',
		'    choice --> Paused: paused',
		'    choice --> Stopped: stopped',
		'    state fork <<fork>>',
		'    Paused --> fork',
		'    fork --> Saving',
		'    fork --> Waiting',
		'    state join <<join>>',
		'    Saving --> join',
		'    Waiting --> join',
		'    join --> Stopped',
		'    Stopped --> [*]',
		'    note right of Idle: a note',
	].join('\n'),
	classDiagram: [
		'classDiagram',
		'    class Scene {',
		'        +Registry registry',
		'        +OnUpdate(float deltaTime) void',
		'    }',
		'    class SceneSystem {',
		'        <<interface>>',
		'        +OnFixedUpdate(float step)*',
		'    }',
		'    Scene "1" *-- "many" SceneSystem : holds',
		'    SceneSystem <|-- PhysicsSystem',
		'    Scene ..> AssetManager : asks',
		'    note for Scene "a note"',
	].join('\n'),
	erDiagram: [
		'erDiagram',
		'    SCENE ||--o{ ENTITY : holds',
		'    ENTITY {',
		'        uuid id PK',
		'        string name',
		'    }',
		'    ENTITY }o--o{ COMPONENT : carries',
	].join('\n'),
	// Time charts (start/what-an-engine-is) and line charts (input/gamepads): every kind of bar and label they may draw.
	// A task marked "crit" is not among them: both themes draw its label under 4.5:1, so sourceProblems refuses it.
	gantt: [
		'gantt',
		'    title A chart of time',
		'    dateFormat X',
		'    axisFormat %s',
		'    section Processor',
		'        Frame 1 :done, p1, 0, 10',
		'        Frame 2 :active, p2, 10, 20',
		'        Frame 3 :p3, 20, 30',
		'    section GPU',
		'        Frame 1 :g1, 10, 20',
		'        Waiting :milestone, m1, 20, 20',
	].join('\n'),
	xychart: [
		'xychart-beta',
		'    title "A value against another"',
		'    x-axis "Device value" [0, 0.25, 0.5, 0.75, 1]',
		'    y-axis "Reading" 0 --> 1',
		'    bar [0.1, 0.3, 0.5, 0.7, 0.9]',
		'    line [0, 0.25, 0.5, 0.75, 1]',
		'    line [0, 0.12, 0.41, 0.71, 1]',
	].join('\n'),
};

// The words a diagram's text starts with, by the type of c_ContrastFixtures each is.
const c_DiagramTypes = { flowchart: 'flowchart', graph: 'flowchart', sequenceDiagram: 'sequenceDiagram', stateDiagram: 'stateDiagram', 'stateDiagram-v2': 'stateDiagram', classDiagram: 'classDiagram', 'classDiagram-v2': 'classDiagram', erDiagram: 'erDiagram', gantt: 'gantt', 'xychart-beta': 'xychart', xychart: 'xychart' };

/**
 * The type of a diagram, as c_ContrastFixtures names it, or null for a type the book does not draw. The first line
 * that is not blank, a comment ("%%") or front matter names it.
 */
export function diagramType(source) {
	const lines = normalizeSource(source).split('\n');
	let index = 0;
	if (lines[0]?.trim() === '---') {
		index = lines.findIndex((line, position) => position > 0 && line.trim() === '---') + 1;
		if (index === 0) return null;
	}
	for (; index < lines.length; index++) {
		const line = lines[index].trim();
		if (line === '' || line.startsWith('%%')) continue;
		const word = /^[A-Za-z][\w-]*/.exec(line)?.[0];
		return c_DiagramTypes[word] ?? null;
	}
	return null;
}

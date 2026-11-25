// The book's hand-drawn diagrams (figures of kind "diagram": src/assets/figures/<part>/<chapter>/<figure>.svg, which
// the site inlines into the page) and the rules of plan/card/drawing.md that can be measured.
//
//     node scripts/drawings.mjs start  <part>/<chapter>/<figure> [--height <n>]   writes an empty drawing to start from
//     node scripts/drawings.mjs render <part>/<chapter>/<figure> [--out <dir>] [--scale <n>]
//     node scripts/drawings.mjs check  [<part>/<chapter>[/<figure>] ...]
//
// A drawing colors itself only through the style block this file writes (c_StyleBlock): classes whose colors are
// Starlight's custom properties, so the page's light or dark theme paints it. `render` shows a drawing as the site does,
// in Chromium with the site's own style sheets (Starlight's props.css and src/styles/book.css) and fonts, at the column's
// width, once with data-theme="light" and once with data-theme="dark", and writes <part>-<chapter>-<figure>-light.png
// and -dark.png (default folder G:/GameEngineAI/.worktrees/docs-work/draw/out). `check` fails on what the card forbids
// (read from the file) and on what it measures in Chromium: text smaller than 14 px at the column's width, a text's box
// that leaves the viewBox, a shape the viewBox cuts off, and text under 4.5:1 against what is drawn behind it in either theme (the color most pixels
// under the text's box have when every text is hidden, as scripts/diagram-checks.mjs measures Mermaid's diagrams).
// It also shows the drawing in a phone's column (c_NarrowColumn), where the site keeps it at its least width and lets
// it scroll (book.css), and fails on text smaller there than the least width draws 14 units, and on a box that leaves
// the column instead of scrolling; and it prints the drawing from the dark theme, which must paint every element as
// the light theme does on screen (Starlight's print style sheet and src/styles/print.css), never light ink on paper.

import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { fromHtml } from 'hast-util-from-html';
import sharp from 'sharp';
import { c_MinimumContrast, composite, contrastRatio, dominantColor, hex, parseColor } from './diagram-checks.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
export const c_FiguresDir = path.join(c_Root, 'src', 'assets', 'figures');
export const c_DefaultOut = 'G:/GameEngineAI/.worktrees/docs-work/draw/out';
// The content column is 48rem (src/styles/book.css), 768 CSS pixels, and the site stretches every drawing to it
// (.book-figure__drawing svg { width: 100% }): a viewBox 768 wide draws one unit as one pixel on a wide screen.
export const c_Width = 768;
export const c_MaxHeight = 640;
export const c_MinimumTextSize = 14;
// How far, in viewBox units, a text's box may stand past the viewBox: less is the rounding of the layout.
export const c_Tolerance = 0.5;
export const c_Themes = ['light', 'dark'];
// A phone's column: a 375-pixel screen less Starlight's margins. Below src/styles/book.css's least width of a drawing
// (40rem, 640 pixels) a drawing scrolls instead of shrinking, so its 14-unit text keeps 14 * 640 / 768 pixels.
export const c_NarrowColumn = 340;
export const c_LeastWidth = 640;
export const c_NarrowTextSize = (c_MinimumTextSize * c_LeastWidth) / c_Width;
// The page that shows a drawing is served from this origin by the browser itself (page.route): nothing listens on it.
const c_Origin = 'http://drawing.invalid/';
const c_Fonts = { '/fonts/inter.woff2': '@fontsource-variable/inter/files/inter-latin-wght-normal.woff2', '/fonts/mono.woff2': '@fontsource-variable/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2' };

// The roles a drawing paints with: each a fill class (`ink`) and a stroke class (`line-ink`), drawn with a custom
// property of Starlight's theme; the fallback (the light theme's value) is what a viewer outside the site shows.
export const c_Roles = [
	{ name: 'ink', variable: '--sl-color-white', fallback: '#17181c' },
	{ name: 'muted', variable: '--sl-color-gray-3', fallback: '#555962' },
	{ name: 'faint', variable: '--sl-color-gray-5', fallback: '#c1c3c8' },
	{ name: 'ground', variable: '--sl-color-black', fallback: '#ffffff' },
	{ name: 'plate', variable: '--sl-color-gray-6', fallback: '#edeef3' },
	{ name: 'blue', variable: '--sl-color-blue-high', fallback: '#0f1c8a' },
	{ name: 'blue-area', variable: '--sl-color-blue-low', fallback: '#cfd4fc' },
	{ name: 'green', variable: '--sl-color-green-high', fallback: '#28650b' },
	{ name: 'green-area', variable: '--sl-color-green-low', fallback: '#defbd0' },
	{ name: 'purple', variable: '--sl-color-purple-high', fallback: '#660891' },
	{ name: 'purple-area', variable: '--sl-color-purple-low', fallback: '#edd1fa' },
	{ name: 'orange', variable: '--sl-color-orange-high', fallback: '#73520d' },
	{ name: 'orange-area', variable: '--sl-color-orange-low', fallback: '#fceac5' },
	{ name: 'red', variable: '--sl-color-red-high', fallback: '#8a0f3a' },
	{ name: 'red-area', variable: '--sl-color-red-low', fallback: '#fad1df' },
];
const c_TextClasses = ['small', 'large', 'bold', 'mono', 'halo'];
// Shapes whose colors are data, not roles (a color ramp, a swatch of a color space): the same in both themes.
const c_Swatch = 'swatch';
export const c_Classes = new Set([...c_Roles.flatMap((role) => [role.name, `line-${role.name}`]), ...c_TextClasses, c_Swatch]);

const c_Selector = 'svg.book-drawing';
/** The one style block a drawing holds, line for line. */
export const c_StyleBlock = [
	'<style>',
	`${c_Selector} { font-family: var(--sl-font, 'Inter Variable', system-ui, sans-serif); font-size: 16px; fill: var(--sl-color-white, #17181c); stroke: none; stroke-width: 1.5px; stroke-linejoin: round; }`,
	`${c_Selector} text { stroke: none; }`,
	...c_Roles.flatMap((role) => [
		`${c_Selector} .${role.name} { fill: var(${role.variable}, ${role.fallback}); }`,
		`${c_Selector} .line-${role.name} { stroke: var(${role.variable}, ${role.fallback}); }`,
	]),
	`${c_Selector} .small { font-size: 14px; }`,
	`${c_Selector} .large { font-size: 20px; }`,
	`${c_Selector} .bold { font-weight: 600; }`,
	`${c_Selector} .mono { font-family: var(--sl-font-mono, 'JetBrains Mono Variable', ui-monospace, monospace); }`,
	`${c_Selector} .halo { paint-order: stroke; stroke: var(--sl-color-black, #ffffff); stroke-width: 5px; }`,
	'</style>',
].join('\n');

const c_Elements = new Set(['svg', 'g', 'defs', 'style', 'line', 'polyline', 'polygon', 'path', 'rect', 'circle', 'ellipse', 'text', 'tspan', 'textPath', 'use', 'symbol', 'clipPath', 'mask', 'pattern', 'linearGradient', 'radialGradient', 'stop']);
// Elements a drawing never holds, with the reason the report gives.
const c_Refused = {
	script: 'a script', foreignObject: 'HTML inside the drawing', image: 'a raster image', feImage: 'a raster image', a: 'a link',
	title: 'a title (the manifest\'s alt names the figure)', desc: 'a description (the manifest\'s alt names the figure)',
	font: 'a font', 'font-face': 'a font', filter: 'a filter (its colors follow no role)', marker: 'a marker (draw arrow heads as polygons)',
};
const c_FontProperties = ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'font'];
const c_OpacityProperties = ['opacity', 'fillOpacity', 'strokeOpacity'];
const c_ColorProperties = ['color', 'floodColor', 'lightingColor'];

/** "fontFamily" → "font-family", for the report. */
function attributeName(property) {
	if (property === 'className') return 'class';
	if (property === 'xLinkHref') return 'xlink:href';
	if (property === 'viewBox') return 'viewBox';
	return property.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
}

function elementsOf(node, parents = [], found = []) {
	for (const child of node.children ?? []) {
		if (child.type !== 'element') continue;
		found.push({ node: child, parents });
		elementsOf(child, [...parents, child], found);
	}
	return found;
}

const classesOf = (node) => (Array.isArray(node.properties?.className) ? node.properties.className : []);
const normalize = (text) => text.replace(/\s+/g, ' ').trim();
const textOf = (node) => (node.children ?? []).map((child) => (child.type === 'text' ? child.value : textOf(child))).join('');

/** The viewBox of a drawing's root: `{ x, y, width, height }`, or null. */
export function parseViewBox(value) {
	const numbers = String(value ?? '').trim().split(/[\s,]+/).map(Number);
	if (numbers.length !== 4 || numbers.some((number) => !Number.isFinite(number))) return null;
	return { x: numbers[0], y: numbers[1], width: numbers[2], height: numbers[3] };
}

/**
 * What the card forbids that the file itself shows, for the drawing of figure `figure` (its file's name without .svg):
 * a list of problems (empty when none). It reads the SVG as the HTML parser of the page reads it.
 */
export function staticProblems(text, figure) {
	const problems = [];
	const tree = fromHtml(text, { fragment: true });
	const tops = (tree.children ?? []).filter((child) => child.type === 'element' || (child.type === 'text' && child.value.trim()));
	if (tops.length !== 1 || tops[0].tagName !== 'svg') return ['the file is not one <svg> element (nothing before or after it but comments)'];
	const root = tops[0];
	const properties = root.properties ?? {};
	if (properties.xmlns !== 'http://www.w3.org/2000/svg') problems.push('the <svg> needs xmlns="http://www.w3.org/2000/svg"');
	if (!classesOf(root).includes('book-drawing')) problems.push('the <svg> needs class="book-drawing" (its style block colors only that)');
	if ('width' in properties || 'height' in properties) problems.push('the <svg> has a width or height: the site sizes a drawing to the column; give only the viewBox');
	const view = parseViewBox(properties.viewBox);
	if (!view) problems.push('the <svg> has no viewBox');
	else if (view.x !== 0 || view.y !== 0 || view.width !== c_Width || !(view.height > 0 && view.height <= c_MaxHeight)) problems.push(`the viewBox is "${properties.viewBox}": it is "0 0 ${c_Width} <height>", the height at most ${c_MaxHeight}`);
	const elements = elementsOf(root);
	const ids = new Map();
	for (const { node } of elements) {
		const id = node.properties?.id;
		if (id === undefined) continue;
		if (ids.has(id)) problems.push(`the id "${id}" is used twice`);
		ids.set(id, node);
		if (!String(id).startsWith(`${figure}-`)) problems.push(`the id "${id}" does not start with "${figure}-" (two drawings on one page must not share an id)`);
	}
	const reference = (value, where) => {
		const match = /^#(.+)$/.exec(String(value).trim());
		if (!match) problems.push(`${where} refers to "${value}" outside the drawing: a drawing refers only to its own ids`);
		else if (!ids.has(match[1])) problems.push(`${where} refers to "#${match[1]}", which the drawing does not define`);
	};
	const styles = [];
	for (const { node, parents } of elements) {
		const tag = node.tagName;
		const where = `<${tag}>`;
		if (c_Refused[tag]) {
			problems.push(`the drawing holds ${c_Refused[tag]} (<${tag}>)`);
			continue;
		}
		if (!c_Elements.has(tag)) {
			problems.push(`the drawing holds a <${tag}>, which no drawing uses`);
			continue;
		}
		if (tag === 'style') styles.push(node);
		const swatch = [node, ...parents].some((element) => classesOf(element).includes(c_Swatch));
		const gradientStop = tag === 'stop' && ['linearGradient', 'radialGradient'].includes(parents.at(-1)?.tagName);
		for (const [property, value] of Object.entries(node.properties ?? {})) {
			const name = attributeName(property);
			const values = Array.isArray(value) ? value.join(' ') : String(value);
			if (/^on/i.test(property)) problems.push(`${where} has the event attribute ${name}: a drawing runs no script`);
			else if (property === 'style') problems.push(`${where} has a style attribute: colors and fonts come from the style block's classes`);
			else if (c_FontProperties.includes(property)) problems.push(`${where} sets ${name}: fonts and sizes come from the classes small, large, bold and mono`);
			else if (c_OpacityProperties.includes(property)) problems.push(`${where} sets ${name}: see-through paint makes colors outside the roles`);
			else if (c_ColorProperties.includes(property)) problems.push(`${where} sets ${name}, a color outside the roles`);
			else if (property === 'href' || property === 'xLinkHref' || property === 'src') reference(values, `${where} ${name}`);
			else if (property === 'className') {
				for (const name of value) if (!c_Classes.has(name) && !(node === root && name === 'book-drawing')) problems.push(`${where} has the class "${name}", which the style block does not define`);
			} else if (property === 'fill' || property === 'stroke') {
				const literal = values.trim();
				if (literal === 'none') continue;
				if (tag === 'text' || tag === 'tspan' || tag === 'textPath') problems.push(`${where} sets ${name}="${literal}": a text takes its color from a role class`);
				else if (!swatch) problems.push(`${where} sets ${name}="${literal}", a color outside the roles (use a role class, or class="swatch" for a color that is data)`);
				else if (/url\(/i.test(literal)) {
					const match = /^url\(\s*['"]?(#[^'")\s]+)['"]?\s*\)$/i.exec(literal);
					if (match) reference(match[1], `${where} ${name}`);
					else problems.push(`${where} ${name} refers to "${literal}" outside the drawing`);
				}
			} else if (property === 'stopColor' || property === 'stopOpacity') {
				if (!gradientStop) problems.push(`${where} sets ${name} outside a gradient`);
			} else if (/url\(/i.test(values)) {
				const match = /^url\(\s*['"]?(#[^'")\s]+)['"]?\s*\)$/i.exec(values.trim());
				if (match) reference(match[1], `${where} ${name}`);
				else problems.push(`${where} ${name} refers to "${values}" outside the drawing`);
			}
		}
		if (gradientStop && !parents.slice(0, -1).some((element) => element.tagName === 'defs')) problems.push('a gradient stands outside <defs>');
	}
	if (styles.length !== 1) problems.push(`the drawing holds ${styles.length} style blocks: it holds exactly the one of plan/card/drawing.md (node scripts/drawings.mjs start writes it)`);
	else if (normalize(textOf(styles[0])) !== normalize(c_StyleBlock.replace(/^<style>|<\/style>$/g, ''))) problems.push('the style block is not the card\'s, word for word: copy it from a drawing that start wrote');
	else if (/@import|@font-face|url\(/i.test(textOf(styles[0]))) problems.push('the style block loads something');
	return problems;
}

/**
 * The problems of what was measured in one theme: `measured` is `{ width, height, texts: [{ tag, text, size, view,
 * ratio, color, background }] }` (view: the text's box in viewBox units, only for <text>; ratio: its contrast against
 * what is behind it, when measured). Geometry is the same in both themes, so `geometry` asks for it once.
 */
export function measuredProblems(theme, measured, { geometry = true } = {}) {
	const problems = [];
	for (const item of measured.texts) {
		const label = `"${item.text.length > 40 ? `${item.text.slice(0, 40)}…` : item.text}"`;
		if (geometry && item.size < c_MinimumTextSize - 0.01) problems.push(`${label} is ${item.size.toFixed(1)} px at the column's width (at least ${c_MinimumTextSize})`);
		if (geometry && item.view) {
			const out = Math.max(-item.view.left, -item.view.top, item.view.right - measured.width, item.view.bottom - measured.height);
			if (out > c_Tolerance) problems.push(`${label} leaves the viewBox by ${out.toFixed(1)} (its box runs ${item.view.left.toFixed(0)} to ${item.view.right.toFixed(0)} across, ${item.view.top.toFixed(0)} to ${item.view.bottom.toFixed(0)} down)`);
		}
		if (item.ratio !== undefined && item.ratio < c_MinimumContrast) problems.push(`${label} stands at ${item.ratio.toFixed(2)}:1 against what is behind it in the ${theme} theme (at least ${c_MinimumContrast}:1): ${hex(item.color)} on ${hex(item.background)}`);
	}
	// The page clips a drawing at its viewBox: a shape past the edge is cut off without a word (a viewBox shorter than
	// the plan, a translated group).
	for (const shape of geometry ? measured.shapes ?? [] : []) {
		const out = Math.max(-shape.view.left, -shape.view.top, shape.view.right - measured.width, shape.view.bottom - measured.height);
		if (out > c_Tolerance) problems.push(`a <${shape.tag}> is cut off by the viewBox's edge by ${out.toFixed(1)} (its box, stroke included, runs ${shape.view.left.toFixed(0)} to ${shape.view.right.toFixed(0)} across, ${shape.view.top.toFixed(0)} to ${shape.view.bottom.toFixed(0)} down)`);
	}
	return problems;
}

/** "part/chapter/figure" → the drawing's file, or null when the name has another form. */
export function drawingFile(id, root = c_FiguresDir) {
	const parts = String(id).replace(/\.svg$/, '').split('/');
	if (parts.length !== 3 || parts.some((part) => !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(part))) return null;
	return path.join(root, ...parts) + '.svg';
}

/** The drawings `check` reads: every SVG below `root`, or those of the chapters and figures named. */
export function selectDrawings(names, root = c_FiguresDir) {
	const all = [];
	const walk = (folder, relative) => {
		if (!existsSync(folder)) return;
		for (const entry of readdirSync(folder, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
			if (entry.isDirectory()) walk(path.join(folder, entry.name), relative ? `${relative}/${entry.name}` : entry.name);
			else if (entry.name.endsWith('.svg')) all.push({ id: `${relative}/${entry.name.slice(0, -4)}`, file: path.join(folder, entry.name) });
		}
	};
	walk(root, '');
	if (!names.length) return { drawings: all, unknown: [] };
	const unknown = [];
	const picked = new Map();
	for (const name of names) {
		const clean = name.replace(/\.svg$/, '').replace(/\/$/, '');
		const matches = all.filter((drawing) => drawing.id === clean || drawing.id.startsWith(`${clean}/`));
		if (!matches.length) unknown.push(name);
		for (const drawing of matches) picked.set(drawing.id, drawing);
	}
	return { drawings: [...picked.values()], unknown };
}

/** An empty drawing to start from: the root, the style block and a comment where the drawing goes. */
export function skeleton(height = 400) {
	return `<svg xmlns="http://www.w3.org/2000/svg" class="book-drawing" viewBox="0 0 ${c_Width} ${height}">\n${c_StyleBlock}\n<!-- the drawing: roles as classes (plan/card/drawing.md) -->\n</svg>\n`;
}

export function siteStyles() {
	const props = path.join(c_Root, 'node_modules', '@astrojs', 'starlight', 'dist', 'style', 'props.css');
	if (!existsSync(props)) throw new Error(`${props} is missing: run npm ci in ${c_Root}`);
	// The fonts are served to the page by showDrawing (a page opened from a string may not read files).
	const font = (family, name) => `@font-face { font-family: '${family}'; font-style: normal; font-weight: 100 900; src: url('${c_Origin}fonts/${name}') format('woff2'); }`;
	return [
		font('Inter Variable', 'inter.woff2'),
		font('JetBrains Mono Variable', 'mono.woff2'),
		readFileSync(props, 'utf8'),
		readFileSync(path.join(c_Root, 'src', 'styles', 'book.css'), 'utf8'),
		// Both print style sheets, as the site loads them: Starlight's (on every page, media="print") and the book's.
		readFileSync(path.join(path.dirname(props), 'print.css'), 'utf8'),
		readFileSync(path.join(c_Root, 'src', 'styles', 'print.css'), 'utf8'),
	].join('\n');
}

/** A page that shows one drawing as the site does: the site's styles, the theme, the column's width. */
export function drawingPage(svg, theme, styles, { frame = false, width = c_Width } = {}) {
	const outline = frame ? '.book-figure__drawing svg { outline: 1px dashed var(--sl-color-gray-4); }' : '';
	return `<!DOCTYPE html><html data-theme="${theme}"><head><meta charset="utf-8"><style>${styles}\nhtml, body { margin: 0; background: var(--sl-color-bg); } .book-frame { width: ${width}px; padding: 24px; } .book-frame .book-figure { margin: 0; } ${outline}</style></head><body><div class="book-frame"><figure class="book-figure"><div class="book-figure__drawing" role="img">${svg}</div></figure></div></body></html>`;
}

/** In the page: every <text> and <tspan> of the drawing with words, its size at the column's width, its box and fill. */
function measureInPage(svg) {
	const view = svg.viewBox.baseVal;
	const rect = svg.getBoundingClientRect();
	const scale = rect.width / view.width;
	const toRoot = svg.getScreenCTM().inverse();
	const texts = [];
	for (const element of svg.querySelectorAll('text, tspan')) {
		const words = element.textContent.trim();
		if (!words) continue;
		const style = getComputedStyle(element);
		const matrix = toRoot.multiply(element.getScreenCTM());
		let opacity = Number(style.fillOpacity);
		for (let parent = element; parent && parent !== svg.parentElement; parent = parent.parentElement) opacity *= Number(getComputedStyle(parent).opacity);
		const client = element.getBoundingClientRect();
		const item = { tag: element.tagName, text: words, size: parseFloat(style.fontSize) * Math.hypot(matrix.a, matrix.b) * scale, fill: style.fill, opacity, box: { x: client.left - rect.left, y: client.top - rect.top, width: client.width, height: client.height } };
		if (element.tagName === 'text') {
			const box = element.getBBox();
			const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]].map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
			item.view = { left: Math.min(...corners.map((p) => p.x)) - view.x, right: Math.max(...corners.map((p) => p.x)) - view.x, top: Math.min(...corners.map((p) => p.y)) - view.y, bottom: Math.max(...corners.map((p) => p.y)) - view.y };
		}
		texts.push(item);
	}
	const shapes = [];
	for (const element of svg.querySelectorAll('line, path, rect, circle, ellipse, polygon, polyline')) {
		if (element.closest('defs')) continue;
		const style = getComputedStyle(element);
		const half = style.stroke && style.stroke !== 'none' ? parseFloat(style.strokeWidth) / 2 : 0;
		const box = element.getBBox();
		const matrix = toRoot.multiply(element.getScreenCTM());
		const corners = [[box.x - half, box.y - half], [box.x + box.width + half, box.y - half], [box.x - half, box.y + box.height + half], [box.x + box.width + half, box.y + box.height + half]].map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
		shapes.push({ tag: element.tagName, view: { left: Math.min(...corners.map((p) => p.x)) - view.x, right: Math.max(...corners.map((p) => p.x)) - view.x, top: Math.min(...corners.map((p) => p.y)) - view.y, bottom: Math.max(...corners.map((p) => p.y)) - view.y } });
	}
	return { width: view.width, height: view.height, texts, shapes };
}

async function openBrowser() {
	const { chromium } = await import('playwright');
	return chromium.launch();
}

async function showDrawing(browser, svg, theme, styles, options = {}) {
	const page = await browser.newPage({ viewport: { width: (options.width ?? c_Width) + 48, height: 900 }, deviceScaleFactor: options.scale ?? 1 });
	if (options.media) await page.emulateMedia({ media: options.media });
	const html = drawingPage(svg, theme, styles, options);
	await page.route(`${c_Origin}**`, (route) => {
		const name = new URL(route.request().url()).pathname;
		if (name === '/') return route.fulfill({ contentType: 'text/html; charset=utf-8', body: html });
		const font = c_Fonts[name];
		return font ? route.fulfill({ contentType: 'font/woff2', body: readFileSync(require.resolve(font)) }) : route.fulfill({ status: 404, body: '' });
	});
	await page.goto(c_Origin, { waitUntil: 'load' });
	await page.evaluate(async () => {
		await document.fonts.load("16px 'Inter Variable'");
		await document.fonts.load("16px 'JetBrains Mono Variable'");
		await document.fonts.ready;
	});
	return page;
}

const rawPixels = async (handle) => sharp(await handle.screenshot({ animations: 'disabled' })).ensureAlpha().raw().toBuffer({ resolveWithObject: true });

/** Measures one drawing in one theme: its texts with the contrast of each against what is drawn behind it. */
async function measureTheme(browser, svg, theme, styles) {
	const page = await showDrawing(browser, svg, theme, styles);
	try {
		const handle = await page.$('.book-figure__drawing svg');
		if (!handle) throw new Error('the page shows no <svg>');
		const measured = await handle.evaluate(measureInPage);
		await handle.evaluate((element) => {
			for (const text of element.querySelectorAll('text')) text.style.setProperty('visibility', 'hidden', 'important');
		});
		const hidden = await rawPixels(handle);
		for (const item of measured.texts) {
			const fill = parseColor(item.fill);
			const background = dominantColor(hidden.data, hidden.info, item.box);
			if (!fill || !background) continue;
			const alpha = fill.a * item.opacity;
			item.color = alpha < 1 ? composite(fill, alpha, background) : fill;
			item.background = background;
			item.ratio = contrastRatio(item.color, background);
		}
		return measured;
	} finally {
		await page.close();
	}
}

/** In the page: the drawing's box in the column, and the smallest text of the drawing in pixels. */
function measureBox(svg) {
	const box = svg.closest('.book-figure__drawing');
	const column = getComputedStyle(svg.closest('.book-frame'));
	const view = svg.viewBox.baseVal;
	const scale = svg.getBoundingClientRect().width / view.width;
	const toRoot = svg.getScreenCTM().inverse();
	let smallest = Infinity;
	for (const element of svg.querySelectorAll('text, tspan')) {
		if (!element.textContent.trim()) continue;
		const matrix = toRoot.multiply(element.getScreenCTM());
		smallest = Math.min(smallest, parseFloat(getComputedStyle(element).fontSize) * Math.hypot(matrix.a, matrix.b) * scale);
	}
	const overflow = getComputedStyle(box).overflowX;
	return {
		column: parseFloat(column.width),
		box: box.getBoundingClientRect().width,
		drawn: svg.getBoundingClientRect().width,
		scrolls: overflow === 'auto' || overflow === 'scroll',
		smallest: Number.isFinite(smallest) ? smallest : null,
	};
}

/** In the page: the painted fill and stroke of every element of the drawing, in document order. */
function measurePaint(svg) {
	return [svg, ...svg.querySelectorAll('*')].filter((element) => !element.closest('defs, style')).map((element) => {
		const style = getComputedStyle(element);
		return { tag: element.tagName, fill: style.fill, stroke: style.stroke };
	});
}

/** What the phone's column shows wrong: `measured` is measureBox's result there. */
export function narrowProblems(measured) {
	const problems = [];
	if (measured.box > measured.column + c_Tolerance) problems.push(`in a column of ${measured.column.toFixed(0)} px the drawing's box is ${measured.box.toFixed(0)} px wide: it leaves the column instead of scrolling`);
	if (measured.drawn > measured.box + c_Tolerance && !measured.scrolls) problems.push(`in a column of ${measured.column.toFixed(0)} px the drawing is ${measured.drawn.toFixed(0)} px wide and its box does not scroll`);
	if (measured.smallest !== null && measured.smallest < c_NarrowTextSize - 0.01) problems.push(`in a column of ${measured.column.toFixed(0)} px its smallest text is ${measured.smallest.toFixed(1)} px (at least ${c_NarrowTextSize.toFixed(1)}: a drawing keeps a least width of ${c_LeastWidth} px and scrolls, src/styles/book.css)`);
	return problems;
}

/** Where a print from the dark theme paints otherwise than the light theme on screen. */
export function printProblems(light, printed) {
	if (light.length !== printed.length) return [`printed, the drawing has ${printed.length} elements, on screen ${light.length}`];
	const problems = [];
	light.forEach((element, index) => {
		for (const paint of ['fill', 'stroke']) {
			if (element[paint] !== printed[index][paint]) problems.push(`printed from the dark theme a <${element.tag}>'s ${paint} is ${printed[index][paint]}, not the light theme's ${element[paint]}`);
		}
	});
	return problems;
}

/** Measures one drawing in the phone's column, and its paint on screen in the light theme and printed from the dark. */
async function measureLayouts(browser, svg, styles) {
	const measure = async (theme, options, measureIn) => {
		const page = await showDrawing(browser, svg, theme, styles, options);
		try {
			return await (await page.$('.book-figure__drawing svg')).evaluate(measureIn);
		} finally {
			await page.close();
		}
	};
	return {
		narrow: await measure('light', { width: c_NarrowColumn }, measureBox),
		light: await measure('light', {}, measurePaint),
		printed: await measure('dark', { media: 'print' }, measurePaint),
	};
}

/** Checks drawings: `{ problems: ["<file>: <problem>"], checked }`. `styles` replaces the site's (the tests). */
export async function checkDrawings(drawings, { styles: given = null } = {}) {
	const problems = [];
	let browser = null;
	try {
		const styles = given ?? siteStyles();
		for (const { id, file } of drawings) {
			const relative = path.relative(c_Root, file).split(path.sep).join('/');
			const text = readFileSync(file, 'utf8');
			const found = staticProblems(text, path.basename(file, '.svg'));
			const tree = fromHtml(text, { fragment: true });
			const root = tree.children.find((child) => child.type === 'element' && child.tagName === 'svg');
			if (root && parseViewBox(root.properties?.viewBox)) {
				browser ??= await openBrowser();
				for (const theme of c_Themes) found.push(...measuredProblems(theme, await measureTheme(browser, text, theme, styles), { geometry: theme === c_Themes[0] }));
				const layouts = await measureLayouts(browser, text, styles);
				found.push(...narrowProblems(layouts.narrow), ...printProblems(layouts.light, layouts.printed));
			}
			// One line per kind of fault: a color repeated on twenty lines is one problem to fix.
			const counts = new Map();
			for (const problem of found) counts.set(problem, (counts.get(problem) ?? 0) + 1);
			for (const [problem, count] of counts) problems.push(`${relative}: ${problem}${count > 1 ? ` (${count} times)` : ''}`);
			console.log(`${id}: ${found.length ? `${found.length} problem${found.length === 1 ? '' : 's'}` : 'passes'}`);
		}
	} finally {
		await browser?.close();
	}
	return { problems, checked: drawings.length };
}

/** Renders one drawing as the site shows it in both themes: the PNG files written. */
export async function renderDrawing(id, { out = c_DefaultOut, scale = 1 } = {}) {
	const file = drawingFile(id);
	if (!file || !existsSync(file)) throw new Error(`no drawing ${id}: its file is src/assets/figures/<part>/<chapter>/<figure>.svg`);
	const svg = readFileSync(file, 'utf8');
	const styles = siteStyles();
	mkdirSync(out, { recursive: true });
	const browser = await openBrowser();
	const written = [];
	try {
		for (const theme of c_Themes) {
			const page = await showDrawing(browser, svg, theme, styles, { scale, frame: true });
			try {
				const target = path.join(out, `${id.replace(/\.svg$/, '').split('/').join('-')}-${theme}.png`);
				await (await page.$('.book-frame')).screenshot({ path: target, animations: 'disabled' });
				written.push(target);
			} finally {
				await page.close();
			}
		}
	} finally {
		await browser.close();
	}
	return written;
}

/** The command line: `{ command, names, out, scale, height }`, or `{ error }`. */
export function parseArguments(argv) {
	const [command, ...rest] = argv;
	if (!['start', 'render', 'check'].includes(command)) return { error: 'usage: node scripts/drawings.mjs start|render <part>/<chapter>/<figure> | check [<part>/<chapter>[/<figure>] ...]' };
	const options = { command, names: [], out: c_DefaultOut, scale: 1, height: 400 };
	for (let index = 0; index < rest.length; index++) {
		const argument = rest[index];
		if (argument === '--out' || argument === '--scale' || argument === '--height') {
			const value = rest[++index];
			if (value === undefined) return { error: `${argument} needs a value` };
			if (argument === '--out') options.out = value;
			else {
				const number = Number(value);
				if (!Number.isFinite(number) || number <= 0) return { error: `${argument} takes a positive number, not "${value}"` };
				if (argument === '--height' && (number > c_MaxHeight || !Number.isInteger(number))) return { error: `--height is a whole number up to ${c_MaxHeight}` };
				options[argument.slice(2)] = number;
			}
		} else if (argument.startsWith('--')) return { error: `unknown option ${argument}` };
		else options.names.push(argument);
	}
	if (command !== 'check' && options.names.length !== 1) return { error: `${command} takes one drawing: <part>/<chapter>/<figure>` };
	if (command !== 'check' && !drawingFile(options.names[0])) return { error: `"${options.names[0]}" is not <part>/<chapter>/<figure>` };
	return options;
}

export async function main(argv) {
	const options = parseArguments(argv);
	if (options.error) {
		console.error(options.error);
		return 2;
	}
	if (options.command === 'start') {
		const file = drawingFile(options.names[0]);
		if (existsSync(file)) {
			console.error(`${file} exists: start writes only a new drawing`);
			return 1;
		}
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, skeleton(options.height));
		console.log(`wrote ${file}`);
		return 0;
	}
	if (options.command === 'render') {
		for (const written of await renderDrawing(options.names[0], options)) console.log(written);
		return 0;
	}
	const { drawings, unknown } = selectDrawings(options.names);
	for (const name of unknown) console.error(`no drawing matches ${name}`);
	if (unknown.length) return 2;
	const { problems, checked } = await checkDrawings(drawings);
	for (const problem of problems) console.error(problem);
	console.log(`${checked} drawing${checked === 1 ? '' : 's'} checked, ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
	return problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
	try {
		process.exitCode = await main(process.argv.slice(2));
	} catch (error) {
		console.error(error.message);
		process.exitCode = 1;
	}
}

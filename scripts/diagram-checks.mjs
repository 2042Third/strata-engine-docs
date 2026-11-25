// Budget row 18 (plan/site.md "Budgets and the spike", "Diagrams"): every diagram of the built site, in the light and
// the dark theme, in Chromium with the page's own fonts and styles. It fails when a diagram has no caption or no
// accessible name (role="img", aria-label and <title>, from the fence's alt="…"), when a label's ink leaves the box it
// stands in (a node, a cluster, an edge label's box, an actor, a note), and when a text stands at less than 4.5:1
// against what is drawn behind it. The text's color is its computed fill; what is behind it is read from a picture of
// the drawing taken with every text hidden: the color most of the pixels under the text's box have.
//
//     node scripts/diagram-checks.mjs [--url http://host/strata-engine-docs/] [--root <book folder>] [--pages a/,b/]
//
// It serves the build with tools/crawl.py (name Python in PYTHON where `python` is not on the PATH) unless --url names
// a server that runs. `npm run diagrams -- --contrast` measures the same way on the renderer's fixture diagrams.

import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import sharp from 'sharp';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_MinimumContrast = 4.5;
// How far, in CSS pixels, a label's text box may stand past its box: less than a pixel is the rounding of the layout.
export const c_Tolerance = 0.5;
export const c_Themes = ['light', 'dark'];

/** An "rgb(…)" or "rgba(…)" color of getComputedStyle: `{ r, g, b, a }` (0 to 255, alpha 0 to 1), or null. */
export function parseColor(value) {
	const match = /^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/.exec(String(value).trim());
	if (!match) return null;
	const alpha = match[4] === undefined ? 1 : match[4].endsWith('%') ? Number(match[4].slice(0, -1)) / 100 : Number(match[4]);
	return { r: Number(match[1]), g: Number(match[2]), b: Number(match[3]), a: alpha };
}

/** A color drawn at `alpha` over an opaque background. */
export function composite(color, alpha, background) {
	const mix = (front, back) => front * alpha + back * (1 - alpha);
	return { r: mix(color.r, background.r), g: mix(color.g, background.g), b: mix(color.b, background.b), a: 1 };
}

/** WCAG 2's relative luminance of an sRGB color. */
export function relativeLuminance({ r, g, b }) {
	const channel = (value) => {
		const c = value / 255;
		return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
	};
	return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

/** WCAG 2's contrast ratio of two colors, from 1 to 21. */
export function contrastRatio(one, other) {
	const [light, dark] = [relativeLuminance(one), relativeLuminance(other)].sort((a, b) => b - a);
	return (light + 0.05) / (dark + 0.05);
}

/**
 * The color most pixels of a region have, in a picture's raw pixels (`channels` per pixel, `width` pixels a row):
 * `{ r, g, b, a: 1 }`, or null when the region holds no pixel. `region` is `{ x, y, width, height }` in pixels.
 */
export function dominantColor(data, { width, height, channels }, region) {
	const x0 = Math.max(0, Math.floor(region.x));
	const y0 = Math.max(0, Math.floor(region.y));
	const x1 = Math.min(width, Math.ceil(region.x + region.width));
	const y1 = Math.min(height, Math.ceil(region.y + region.height));
	const counts = new Map();
	let best = null;
	for (let y = y0; y < y1; y++) {
		for (let x = x0; x < x1; x++) {
			const offset = (y * width + x) * channels;
			const key = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2];
			const count = (counts.get(key) ?? 0) + 1;
			counts.set(key, count);
			if (!best || count > best.count) best = { key, count };
		}
	}
	if (!best) return null;
	return { r: (best.key >> 16) & 255, g: (best.key >> 8) & 255, b: best.key & 255, a: 1 };
}

/**
 * The bounding box of a text's ink: the pixels inside its text box (`region`, in the pictures' pixels) where the
 * picture with the texts differs from the one without them. `{ x, y, width, height }`, or null when no pixel differs.
 */
export function inkBox(shown, hidden, { width, height, channels }, region) {
	const x0 = Math.max(0, Math.floor(region.x));
	const y0 = Math.max(0, Math.floor(region.y));
	const x1 = Math.min(width, Math.ceil(region.x + region.width));
	const y1 = Math.min(height, Math.ceil(region.y + region.height));
	let box = null;
	for (let y = y0; y < y1; y++) {
		for (let x = x0; x < x1; x++) {
			const offset = (y * width + x) * channels;
			if (shown[offset] === hidden[offset] && shown[offset + 1] === hidden[offset + 1] && shown[offset + 2] === hidden[offset + 2]) continue;
			if (!box) box = { left: x, top: y, right: x + 1, bottom: y + 1 };
			box.left = Math.min(box.left, x);
			box.top = Math.min(box.top, y);
			box.right = Math.max(box.right, x + 1);
			box.bottom = Math.max(box.bottom, y + 1);
		}
	}
	return box && { x: box.left, y: box.top, width: box.right - box.left, height: box.bottom - box.top };
}

/**
 * The labels of a measured drawing that leave their boxes: `[{ text, by }]`, `by` the largest overhang in pixels. A
 * label is its ink where it was measured (`ink`), else its text box: the line box of a text holds room above and below
 * the letters that no reader sees.
 */
export function labelProblems(texts, tolerance = c_Tolerance) {
	const problems = [];
	for (const item of texts) {
		if (!item.shape) continue;
		const box = item.ink ?? item.box;
		const { shape } = item;
		const by = Math.max(shape.x - box.x, box.x + box.width - (shape.x + shape.width), shape.y - box.y, box.y + box.height - (shape.y + shape.height));
		if (by > tolerance) problems.push({ text: item.text, by });
	}
	return problems;
}

/**
 * The contrast of every measured text against the color behind it: `[{ text, ratio, color, background }]`. `behind`
 * gives the background of a text's box (from the picture with the texts hidden). A text whose fill is no color is
 * left out; a fill that is not opaque is drawn over its background first.
 */
export function textContrasts(texts, behind) {
	const results = [];
	for (const item of texts) {
		const fill = parseColor(item.fill);
		const background = behind(item.box);
		if (!fill || !background) continue;
		const alpha = fill.a * (item.opacity ?? 1);
		const color = alpha < 1 ? composite(fill, alpha, background) : fill;
		results.push({ text: item.text, ratio: contrastRatio(color, background), color, background });
	}
	return results;
}

/** What a diagram's figure lacks: its caption, or its drawing's name (role, aria-label, a <title> that says the same). */
export function figureProblems({ caption, role, label, title }) {
	const problems = [];
	if (!caption?.trim()) problems.push('it has no caption (the fence\'s caption="…")');
	if (role !== 'img' || !label?.trim()) problems.push('its drawing is not an image with an accessible name (role="img" and aria-label, from the fence\'s alt="…")');
	else if (title?.trim() !== label.trim()) problems.push('its drawing\'s <title> does not say what its aria-label says');
	return problems;
}

/** In the page: the texts of one drawing, each with its box, the box it stands in (or null), its fill and opacity. */
export function measureTexts(svg) {
	const boxOf = (element) => {
		const rect = element.getBoundingClientRect();
		return { x: rect.left, y: rect.top, width: rect.width, height: rect.height };
	};
	const painted = (element) => {
		const style = getComputedStyle(element);
		return style.fill !== 'none' && style.visibility !== 'hidden' && style.display !== 'none' && Number(style.opacity) > 0 && Number(style.fillOpacity) > 0;
	};
	const c_Shapes = 'rect, polygon, circle, ellipse, path';
	const results = [];
	for (const text of svg.querySelectorAll('text')) {
		const words = text.textContent.trim();
		if (!words || text.closest('defs, marker, title')) continue;
		const box = boxOf(text);
		if (box.width === 0 || box.height === 0) continue;
		const centre = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
		// The box a label stands in is the smallest painted shape beside it whose area holds the label's centre: a
		// shape in the label's group, or in one of the three groups around it, or in a group of shapes there (Mermaid
		// draws some boxes as a group of paths): a node's shape, a cluster, an edge label's box, an actor, a note, a
		// table's cell. A text with no such shape (a message, a loop's condition) stands on the page: no box to leave.
		// A sequence diagram's activation bar is drawn on a lifeline, under the messages and numbers that cross it, and
		// holds no label.
		let shape = null;
		let group = text.parentElement;
		for (let level = 0; level < 4 && group && group !== svg.parentElement && !shape; level++, group = group.parentElement) {
			const candidates = [];
			for (const child of group.children) {
				if (child.contains(text)) continue;
				if (child.matches(c_Shapes)) candidates.push(child);
				else if (child.matches('g') && !child.querySelector('text')) candidates.push(...child.querySelectorAll(c_Shapes));
			}
			for (const child of candidates) {
				if (child.matches('[class^="activation"], [class*=" activation"]')) continue;
				const candidate = boxOf(child);
				if (candidate.width === 0 || candidate.height === 0 || !painted(child)) continue;
				if (centre.x < candidate.x || centre.x > candidate.x + candidate.width || centre.y < candidate.y || centre.y > candidate.y + candidate.height) continue;
				if (!shape || candidate.width * candidate.height < shape.width * shape.height) shape = candidate;
			}
		}
		// The color of the words: the innermost span that holds them, else the text itself.
		const span = [...text.querySelectorAll('tspan')].find((candidate) => candidate.textContent.trim() && !candidate.querySelector('tspan')) ?? text;
		const style = getComputedStyle(span);
		let opacity = Number(style.fillOpacity);
		for (let element = span; element && element !== svg.parentElement; element = element.parentElement) opacity *= Number(getComputedStyle(element).opacity);
		results.push({ text: words.replace(/\s+/g, ' '), box, shape, fill: style.fill, opacity });
	}
	return results;
}

async function pixels(handle) {
	return sharp(await handle.screenshot({ animations: 'disabled' })).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
}

/**
 * Measures one drawing (an element handle of an <svg> the page shows): its texts, the ink of each (where a picture of
 * the drawing with its texts differs from one without them), and the background behind each, read from the picture
 * without them. Returns `{ labels, contrasts, count }`.
 */
export async function measureDrawing(handle) {
	await handle.evaluate((svg) => svg.scrollIntoView({ block: 'start' }));
	const texts = await handle.evaluate(measureTexts);
	const origin = await handle.evaluate((svg) => {
		const rect = svg.getBoundingClientRect();
		return { x: rect.left, y: rect.top };
	});
	const shown = await pixels(handle);
	await handle.evaluate((svg) => {
		for (const text of svg.querySelectorAll('text')) text.style.setProperty('visibility', 'hidden', 'important');
	});
	let hidden;
	try {
		hidden = await pixels(handle);
	} finally {
		await handle.evaluate((svg) => {
			for (const text of svg.querySelectorAll('text')) text.style.removeProperty('visibility');
		});
	}
	if (shown.info.width !== hidden.info.width || shown.info.height !== hidden.info.height) throw new Error('the drawing changed its size when its texts were hidden');
	const local = (box) => ({ x: box.x - origin.x, y: box.y - origin.y, width: box.width, height: box.height });
	for (const item of texts) {
		const ink = inkBox(shown.data, hidden.data, shown.info, local(item.box));
		item.ink = ink && { x: ink.x + origin.x, y: ink.y + origin.y, width: ink.width, height: ink.height };
	}
	const behind = (box) => dominantColor(hidden.data, hidden.info, local(box));
	return { labels: labelProblems(texts), contrasts: textContrasts(texts, behind), count: texts.length };
}

/** The problems of one measured drawing, as lines of the report. */
export function drawingReport(where, { labels, contrasts }) {
	const lines = [];
	for (const label of labels) lines.push(`${where}: the label "${label.text}" leaves its box by ${label.by.toFixed(1)} px`);
	for (const item of contrasts) if (item.ratio < c_MinimumContrast) lines.push(`${where}: "${item.text}" stands at ${item.ratio.toFixed(2)}:1 against its background (at least ${c_MinimumContrast}:1): ${hex(item.color)} on ${hex(item.background)}`);
	return lines;
}

/** A color as #rrggbb. */
export function hex({ r, g, b }) {
	return `#${[r, g, b].map((value) => Math.round(value).toString(16).padStart(2, '0')).join('')}`;
}

/** The pages of a built site that hold a diagram: their paths below the base ("core/time/", "" for the landing page). */
export function diagramPages(distDir, relative = '') {
	const pages = [];
	let entries;
	try {
		entries = readdirSync(path.join(distDir, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
		const child = relative ? `${relative}/${entry.name}` : entry.name;
		if (entry.isDirectory()) {
			if (!['_astro', '_figures', 'pagefind'].includes(child)) pages.push(...diagramPages(distDir, child));
		} else if (entry.name === 'index.html' && readFileSync(path.join(distDir, child), 'utf8').includes('class="book-diagram"')) {
			pages.push(relative ? `${relative}/` : '');
		}
	}
	return pages;
}

/** In the page: every diagram's figure facts, after opening what hides diagrams (closed answers, other tabs). */
function figureFacts(theme) {
	for (const details of document.querySelectorAll('details')) details.open = true;
	for (const panel of document.querySelectorAll('.book-tabs__panel[hidden]')) panel.hidden = false;
	return [...document.querySelectorAll('figure.book-diagram')].map((figure, index) => {
		figure.dataset.checkIndex = String(index);
		const svg = figure.querySelector(`.book-diagram__svg--${theme} svg`);
		return {
			caption: figure.querySelector(':scope > figcaption')?.textContent ?? '',
			role: svg?.getAttribute('role') ?? null,
			label: svg?.getAttribute('aria-label') ?? null,
			title: svg?.querySelector(':scope > title')?.textContent ?? null,
			shown: Boolean(svg && svg.getBoundingClientRect().width > 0),
		};
	});
}

async function main(argv) {
	const { chromium } = await import('playwright');
	const { serveSite } = await import('./serve.mjs');
	const rootIndex = argv.indexOf('--root');
	const root = rootIndex >= 0 ? path.resolve(argv[rootIndex + 1]) : c_Root;
	const pagesIndex = argv.indexOf('--pages');
	const pages = pagesIndex >= 0 ? argv[pagesIndex + 1].split(',') : diagramPages(path.join(root, 'dist'));
	if (pages.length === 0) {
		console.log('diagram-checks: no page of the build holds a diagram');
		return 1;
	}
	const site = await serveSite({ argv });
	const browser = await chromium.launch();
	const problems = [];
	let drawings = 0;
	let texts = 0;
	let lowest = Infinity;
	try {
		for (const theme of c_Themes) {
			const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
			await context.addInitScript((value) => window.localStorage.setItem('starlight-theme', value), theme);
			const page = await context.newPage();
			for (const relative of pages) {
				const response = await page.goto(site.url + relative, { waitUntil: 'networkidle' });
				if (response?.status() !== 200) {
					problems.push(`${relative || '(home)'} [${theme}]: answered ${response?.status()}`);
					continue;
				}
				await page.evaluate(() => document.fonts.ready);
				const facts = await page.evaluate(figureFacts, theme);
				for (const [index, fact] of facts.entries()) {
					const where = `${relative || '(home)'} [${theme}] diagram ${index + 1}`;
					for (const problem of figureProblems(fact)) problems.push(`${where}: ${problem}`);
					if (!fact.shown) {
						problems.push(`${where}: its ${theme} drawing is not shown in the ${theme} theme`);
						continue;
					}
					const handle = await page.$(`figure.book-diagram[data-check-index="${index}"] .book-diagram__svg--${theme} svg`);
					const measured = await measureDrawing(handle);
					drawings++;
					texts += measured.count;
					for (const item of measured.contrasts) lowest = Math.min(lowest, item.ratio);
					problems.push(...drawingReport(where, measured));
				}
			}
			await context.close();
		}
	} finally {
		await browser.close();
		await site.stop();
	}
	for (const problem of problems) console.log(problem);
	console.log(`diagram-checks: ${drawings} drawings with ${texts} texts on ${pages.length} page${pages.length === 1 ? '' : 's'} in two themes; lowest contrast ${Number.isFinite(lowest) ? `${lowest.toFixed(2)}:1` : 'not measured'}; ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
	return problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

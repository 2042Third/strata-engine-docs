// npm run diagrams: draws the book's Mermaid diagrams into src/generated/diagrams/, which is committed (plan/site.md
// "Diagrams"; src/lib/diagrams.mjs holds the renderer's settings and the files' form). The site build reads those files
// and starts no browser.
//
//     node scripts/diagrams.mjs [--root <book folder>]
//         draws every diagram whose files are missing or are not the renderer's, and removes the files no fence uses
//     node scripts/diagrams.mjs --check [--root <book folder>]
//         fails on a fence without its two files, on a file no fence uses, on a file that is not the renderer's drawing
//         of its text (its stamp), on a fence without caption or alt, and on a type the contrast fixture lacks
//     node scripts/diagrams.mjs --contrast
//         draws the fixture of every diagram type in both themes and fails on a text under 4.5:1 against what is behind
//         it (run it once per change of the settings)
//
// The diagrams are those of every page, the part pages' generated Needs graphs included (the page index). A diagram
// Mermaid cannot draw is never written; the run names its page and line and exits 1. Run it on one machine, the
// integrator's, so that every diagram is drawn with one platform's fonts. Exit codes: 0 done, 1 problems, 2 usage.

import { rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { bookDiagrams, c_ContrastFixtures, c_ThemeNames, diagramFiles, diagramType, drawDiagrams, groupDiagrams, inlineDrawing, listDrawings, readDrawings, sourceProblems, writeDrawings } from '../src/lib/diagrams.mjs';
import { parseMeta } from '../src/lib/markdown.mjs';
import { readSettings } from '../src/lib/settings.mjs';
import { createBookContext } from '../src/plugins/index.mjs';
import { c_MinimumContrast, drawingReport, measureDrawing } from './diagram-checks.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// The page backgrounds of Starlight 0.42's two themes (--sl-color-bg: white, and hsl(224, 10%, 10%)), behind the
// fixture's drawings as behind the book's.
export const c_Backgrounds = { light: '#ffffff', dark: 'hsl(224, 10%, 10%)' };

class UsageError extends Error {}

export function parseArguments(argv) {
	const options = { mode: 'draw', root: c_Root };
	for (let index = 0; index < argv.length; index++) {
		const argument = argv[index];
		if (argument === '--check' || argument === '--contrast') {
			if (options.mode !== 'draw') throw new UsageError('--check and --contrast are two runs: give one of them');
			options.mode = argument.slice(2);
		} else if (argument === '--root') {
			if (index + 1 >= argv.length) throw new UsageError('--root needs the book folder');
			options.root = path.resolve(argv[++index]);
		} else {
			throw new UsageError(`unknown argument ${argument}`);
		}
	}
	return options;
}

/** The book's diagrams, from its page index: `{ settings, diagrams: [{ source, meta, where }] }`. */
export async function loadBook(root) {
	const settings = readSettings({ root, env: {} });
	const context = createBookContext(settings);
	return { settings, diagrams: bookDiagrams(await context.index()) };
}

/**
 * What `--check` finds: lines naming the fence or the file. `diagrams` holds `{ source, meta, where }`; `dir` is
 * src/generated/diagrams/.
 */
export async function checkDiagrams(dir, diagrams) {
	const problems = [];
	const used = new Set();
	for (const diagram of diagrams) {
		const { attributes } = parseMeta(diagram.meta, ['caption', 'alt']);
		if (!attributes.get('caption')) problems.push(`${diagram.where}: the diagram has no caption="…" (what to notice)`);
		if (!attributes.get('alt')) problems.push(`${diagram.where}: the diagram has no alt="…" (what it shows)`);
		for (const problem of sourceProblems(diagram.source)) problems.push(`${diagram.where}: ${problem}`);
		if (diagramType(diagram.source) === null) problems.push(`${diagram.where}: the diagram's type is not one the contrast fixture holds (${Object.keys(c_ContrastFixtures).join(', ')}): add it to c_ContrastFixtures in src/lib/diagrams.mjs and run npm run diagrams -- --contrast`);
	}
	for (const group of groupDiagrams(diagrams)) {
		for (const file of Object.values(diagramFiles(dir, group.hash))) used.add(path.basename(file));
		const drawings = await readDrawings(dir, group.source);
		if (drawings.missing) problems.push(`${group.where.join(', ')}: no committed drawing (${drawings.missing.map((theme) => `${group.hash}-${theme}.svg`).join(', ')}): run npm run diagrams`);
		else if (drawings.error) problems.push(`${group.where.join(', ')}: ${drawings.error}`);
	}
	const { drawings, others } = await listDrawings(dir);
	for (const name of drawings.keys()) if (!used.has(name)) problems.push(`src/generated/diagrams/${name}: no fence of the book draws it: run npm run diagrams, which removes it`);
	for (const name of others) problems.push(`src/generated/diagrams/${name}: not a drawing of npm run diagrams (<hash>-light.svg or <hash>-dark.svg): remove it`);
	return problems;
}

/**
 * Draws what is missing or stale and removes what no fence uses: `{ drawn, removed, failures }` (file names; lines
 * naming the fences Mermaid refused).
 */
export async function drawBook(dir, diagrams) {
	const stale = [];
	const used = new Set();
	for (const group of groupDiagrams(diagrams)) {
		for (const file of Object.values(diagramFiles(dir, group.hash))) used.add(path.basename(file));
		const drawings = await readDrawings(dir, group.source);
		if (drawings.missing || drawings.error) stale.push(group);
	}
	const { drawn, failures } = stale.length ? await drawDiagrams(stale) : { drawn: [], failures: [] };
	await writeDrawings(dir, drawn);
	const removed = [];
	const { drawings } = await listDrawings(dir);
	for (const name of drawings.keys()) {
		if (used.has(name)) continue;
		await rm(path.join(dir, name));
		removed.push(name);
	}
	return { drawn: drawn.flatMap((entry) => c_ThemeNames.map((theme) => `${entry.hash}-${theme}.svg`)), removed, failures };
}

/** A page that shows one drawing on a theme's background, in the font the drawings name. */
export function fixturePage(svg, theme, fontUrl) {
	return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>@font-face { font-family: 'Inter Variable'; font-style: normal; font-weight: 100 900; src: url('${fontUrl}') format('woff2'); } html, body { margin: 0; background: ${c_Backgrounds[theme]}; } div { padding: 16px; }</style></head><body><div>${svg}</div></body></html>`;
}

async function contrast() {
	const { createRequire } = await import('node:module');
	const { chromium } = await import('playwright');
	const require = createRequire(import.meta.url);
	const fontUrl = pathToFileURL(require.resolve('@fontsource-variable/inter/files/inter-latin-wght-normal.woff2')).href;
	const items = Object.entries(c_ContrastFixtures).map(([type, source]) => ({ source, where: [`the ${type} fixture`] }));
	const { drawn, failures } = await drawDiagrams(items);
	if (failures.length) {
		for (const failure of failures) console.log(failure);
		return 1;
	}
	const browser = await chromium.launch();
	const problems = [];
	try {
		const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
		for (const [index, entry] of drawn.entries()) {
			for (const theme of c_ThemeNames) {
				const svg = inlineDrawing(entry[theme], { hash: entry.hash, theme, alt: items[index].where[0] });
				// A file URL page may load the font from a file URL.
				await page.setContent(fixturePage(svg, theme, fontUrl), { waitUntil: 'load' });
				await page.evaluate(() => document.fonts.ready);
				const measured = await measureDrawing(await page.$('svg'));
				const lowest = Math.min(...measured.contrasts.map((item) => item.ratio));
				console.log(`${items[index].where[0]} [${theme}]: ${measured.contrasts.length} texts, lowest contrast ${lowest.toFixed(2)}:1`);
				problems.push(...drawingReport(`${items[index].where[0]} [${theme}]`, { labels: [], contrasts: measured.contrasts }));
			}
		}
	} finally {
		await browser.close();
	}
	for (const problem of problems) console.log(problem);
	console.log(`diagrams --contrast: ${problems.length} text${problems.length === 1 ? '' : 's'} under ${c_MinimumContrast}:1`);
	return problems.length ? 1 : 0;
}

async function main(argv) {
	let options;
	try {
		options = parseArguments(argv);
	} catch (error) {
		if (!(error instanceof UsageError)) throw error;
		console.error(`diagrams: ${error.message}`);
		return 2;
	}
	if (options.mode === 'contrast') return contrast();
	const { settings, diagrams } = await loadBook(options.root);
	if (options.mode === 'check') {
		const problems = await checkDiagrams(settings.diagramsDir, diagrams);
		for (const problem of problems) console.log(problem);
		console.log(`diagrams --check: ${groupDiagrams(diagrams).length} diagrams, ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
		return problems.length ? 1 : 0;
	}
	const { drawn, removed, failures } = await drawBook(settings.diagramsDir, diagrams);
	for (const name of drawn) console.log(`drew src/generated/diagrams/${name}`);
	for (const name of removed) console.log(`removed src/generated/diagrams/${name} (no fence draws it)`);
	for (const failure of failures) console.log(failure);
	console.log(`diagrams: ${groupDiagrams(diagrams).length} diagrams, ${drawn.length / 2} drawn, ${removed.length} files removed, ${failures.length} failure${failures.length === 1 ? '' : 's'}`);
	return failures.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

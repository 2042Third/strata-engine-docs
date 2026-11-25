// Check 9, accessibility (plan/site.md, "Checks"): axe-core (@axe-core/playwright, the rules tagged wcag2a, wcag2aa,
// wcag21a, wcag21aa and best-practice) in Chromium, in the light and the dark theme; it fails on any serious or
// critical violation. Alt text on every picture and diagram is part of axe's rules.
//
//     node scripts/a11y.mjs [--all] [--pages a/,b/] [--url http://host/strata-engine-docs/] [--dist <built site>]
//         [--root <book folder>]
//
// --all checks every page of the build (--dist, default <root>/dist): every chapter, part page, print view and moved
// page's fallback, and the 404 page at a missing address; CI runs it. Without it, a sample: the landing page, one page
// of each kind, the glossary, a print view, the 404 page, and the first page that holds each of the book's components
// (tabs, the slider, a diagram, a formula, an answer, a term's popover, the track chooser, a generated table, a file
// tree, steps, a checkpoint, a test-out box). It serves the build with tools/crawl.py (name Python in PYTHON where
// `python` is not on the PATH) unless --url names a server that runs.

import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { plan, sitePages } from './runtime.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_Failing = new Set(['serious', 'critical']);
export const c_Tags = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'];
export const c_Themes = ['dark', 'light'];
// The address the 404 page is checked at: one that is no page.
export const c_MissingRoute = 'this-page-does-not-exist/';
// Starlight's search button names itself "Search" while it also shows its keyboard hint (Ctrl K), which axe's
// label-content-name-mismatch reports; the button is Starlight's own, so it is left out until Starlight changes it
// (plan/site.md, "Checks", the spike's one exclusion).
export const c_Excluded = 'site-search button[data-open-modal]';
// The book's components, by what marks them in the built HTML.
export const c_Components = {
	tabs: '<book-tabs', slider: '<book-compare', diagram: 'class="book-diagram"', formula: 'class="katex"', answer: 'book-answer',
	popover: 'class="book-term__button"', chooser: '<book-track-chooser', table: 'class="book-reference"', files: 'book-files', steps: 'sl-steps',
	checkpoint: 'book-checkpoint', testOut: 'aria-label="Test out"',
};

/** Every page of the build, as routes below the base, and the 404 page at a missing address. */
export function allPages(distDir) {
	return [...sitePages(distDir).map((page) => page.route), c_MissingRoute];
}

/** The sample: the runtime gate's pages, the first page with each component, and the 404 page. */
export function samplePages(distDir) {
	const pages = sitePages(distDir).filter((page) => !page.route.startsWith('print/'));
	const routes = plan(distDir).visits.map((visit) => visit.route);
	for (const marker of Object.values(c_Components)) {
		const found = pages.find((page) => page.html.includes(marker));
		if (found) routes.push(found.route);
	}
	return [...new Set(routes), c_MissingRoute];
}

/** Runs axe on `routes` below `site` in both themes: `{ failures: [lines], checked }`. */
export async function runAxe({ site, routes, themes = c_Themes, log = console.log }) {
	const { chromium } = await import('playwright');
	const { default: AxeBuilder } = await import('@axe-core/playwright');
	const browser = await chromium.launch();
	const failures = [];
	try {
		for (const theme of themes) {
			const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
			await context.addInitScript((value) => window.localStorage.setItem('starlight-theme', value), theme);
			const page = await context.newPage();
			for (const relative of routes) {
				const where = `${relative || '(home)'} [${theme}]`;
				const response = await page.goto(site + relative, { waitUntil: 'networkidle' });
				const expected = relative === c_MissingRoute ? 404 : 200;
				if (response?.status() !== expected) {
					failures.push(`${where}: answered ${response?.status()}, expected ${expected}`);
					continue;
				}
				// Only violations are read, so the result keeps one node of each other result type: with every node of every
				// passed rule, the result of a large print view (print/basics/, 9 MB of HTML) is more than Playwright can hand
				// back from the page, and analyze fails with "Execution context was destroyed". Legacy mode runs axe in the page
				// alone, since the default mode hands the partial results to a second page in the same way; the book's pages
				// hold no frames, which only the default mode would reach.
				const results = await new AxeBuilder({ page }).setLegacyMode(true).options({ resultTypes: ['violations'] }).withTags(c_Tags)
					.exclude(c_Excluded).analyze();
				const serious = results.violations.filter((violation) => c_Failing.has(violation.impact));
				for (const violation of serious) {
					failures.push(`${where}: ${violation.impact}: ${violation.id}: ${violation.help}`);
					for (const node of violation.nodes.slice(0, 3)) failures.push(`    ${node.target.join(' ')}: ${node.failureSummary?.split('\n')[1]?.trim() ?? ''}`);
				}
				const minor = results.violations.length - serious.length;
				log(`${where}: ${serious.length} serious or critical, ${minor} minor violation${minor === 1 ? '' : 's'}`);
			}
			await context.close();
		}
	} finally {
		await browser.close();
	}
	return { failures, checked: routes.length };
}

async function main(argv) {
	const option = (name, fallback = null) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const root = path.resolve(option('--root', c_Root));
	const distDir = path.resolve(option('--dist', path.join(root, 'dist')));
	const listed = option('--pages');
	const routes = listed ? listed.split(',') : argv.includes('--all') ? allPages(distDir) : samplePages(distDir);
	const { serveSite } = await import('./serve.mjs');
	const site = await serveSite({ argv });
	let result;
	try {
		result = await runAxe({ site: site.url, routes });
	} finally {
		await site.stop();
	}
	const errors = result.failures.filter((line) => !line.startsWith('    ')).length;
	for (const line of result.failures) console.log(line);
	console.log(`a11y: ${errors} failure${errors === 1 ? '' : 's'} on ${result.checked} pages in two themes`);
	return errors ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

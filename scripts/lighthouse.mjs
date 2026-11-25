// Check 9 and budget row 14 (plan/site.md, "Checks" and "Budgets and the spike"): Lighthouse 13.6.0 (package.json) in
// Playwright's Chromium, as a phone (Lighthouse's default mobile settings, with its simulated throttling):
// - accessibility 100 on the landing page, one page of each of the six kinds and the glossary;
// - on the heaviest figure page (the page whose pictures weigh the most), performance at least 90, accessibility 100,
//   cumulative layout shift at most 0.05 and the largest contentful paint at most 2.5 s.
//
//     node scripts/lighthouse.mjs [--url http://host/strata-engine-docs/] [--dist <built site>] [--root <book folder>]
//         [--heaviest <n>] [--json <file>]
//
// Row 14 is judged on ubuntu-latest (CI's serve-test job); on another machine its numbers are measured, not judged
// against the row, and the script says so with --not-row-14. The pages are read from the build (--dist, default
// <root>/dist). With --heaviest <n> (default 1) the next figure pages by weight are measured beside the heaviest, with
// the same four numbers printed, and only the heaviest is judged against row 14 (accessibility 100 holds for all). It
// serves the build with tools/crawl.py (name Python in PYTHON where `python` is not on the PATH) unless --url names a
// server that runs; tools/crawl.py sends every file uncompressed, so row 14's numbers are only a deployment's (gzip,
// deploy/nginx.conf) through --url.

import { statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { plan, sitePages } from './runtime.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Budget row 14's pass marks.
export const c_Row14 = { performance: 0.9, accessibility: 1, cls: 0.05, lcpMilliseconds: 2500 };

/** The sum of the served sizes of the pictures a page shows (its <img> src under _figures/), in bytes. */
export function pictureBytes(html, distDir, base) {
	let total = 0;
	const seen = new Set();
	for (const match of html.matchAll(/<img\b[^>]*\ssrc="([^"]+)"/g)) {
		const src = match[1];
		if (!src.startsWith(`${base}/_figures/`) || seen.has(src)) continue;
		seen.add(src);
		try {
			total += statSync(path.join(distDir, ...src.slice(base.length + 1).split('/'))).size;
		} catch {
			// A picture the build does not hold is the crawl's failure, not this measure's.
		}
	}
	return total;
}

/** The `count` pages whose pictures weigh the most (not print views), heaviest first: `[{ route, bytes }]`. */
export function heaviestFigurePages(distDir, base, count) {
	const pages = [];
	for (const page of sitePages(distDir)) {
		if (page.route.startsWith('print/')) continue;
		const bytes = pictureBytes(page.html, distDir, base);
		if (bytes > 0) pages.push({ route: page.route, bytes });
	}
	pages.sort((a, b) => b.bytes - a.bytes || a.route.localeCompare(b.route));
	return pages.slice(0, count);
}

/** The page whose pictures weigh the most (not a print view), or null when no page shows one. */
export function heaviestFigurePage(distDir, base) {
	return heaviestFigurePages(distDir, base, 1)[0] ?? null;
}

/** The Lighthouse visits of row 14: the heaviest figure page, judged, and the others of `heaviest`, measured only. */
export function row14Pages(heaviest) {
	return heaviest.map((page, index) => ({ route: page.route, row14: true, measuredOnly: index > 0 }));
}

/**
 * What a page's Lighthouse result fails: accessibility on every page; row 14's four marks on the figure page (not on a
 * figure page measured beside it).
 */
export function scoreProblems(where, result, { row14 = false, measuredOnly = false } = {}) {
	const problems = [];
	const accessibility = result.categories.accessibility?.score;
	if (accessibility !== c_Row14.accessibility) {
		const failed = Object.values(result.audits).filter((audit) => audit.score === 0 && audit.scoreDisplayMode === 'binary' && result.categories.accessibility.auditRefs.some((ref) => ref.id === audit.id && ref.weight > 0));
		problems.push(`${where}: accessibility ${Math.round((accessibility ?? 0) * 100)}, not 100${failed.length ? ` (${failed.map((audit) => audit.id).join(', ')})` : ''}`);
	}
	if (row14 && !measuredOnly) {
		const performance = result.categories.performance?.score ?? 0;
		const cls = result.audits['cumulative-layout-shift']?.numericValue;
		const lcp = result.audits['largest-contentful-paint']?.numericValue;
		if (performance < c_Row14.performance) problems.push(`${where}: performance ${Math.round(performance * 100)}, under ${c_Row14.performance * 100}`);
		if (!(cls <= c_Row14.cls)) problems.push(`${where}: cumulative layout shift ${cls}, over ${c_Row14.cls}`);
		if (!(lcp <= c_Row14.lcpMilliseconds)) problems.push(`${where}: largest contentful paint ${Math.round(lcp)} ms, over ${c_Row14.lcpMilliseconds} ms`);
	}
	return problems;
}

function freePort() {
	return new Promise((resolve, reject) => {
		const server = createServer();
		server.on('error', reject);
		server.listen(0, '127.0.0.1', () => {
			const { port } = server.address();
			server.close(() => resolve(port));
		});
	});
}

/** Lighthouse on each `{ route, row14, measuredOnly }` below `site`: `{ problems, measured: [{ route, scores, cls, lcp }] }`. */
export async function runLighthouse({ site, pages }) {
	const { chromium } = await import('playwright');
	const { default: lighthouse } = await import('lighthouse');
	const port = await freePort();
	const browser = await chromium.launch({ args: [`--remote-debugging-port=${port}`] });
	const problems = [];
	const measured = [];
	try {
		for (const { route, row14, measuredOnly = false } of pages) {
			const where = route || '(home)';
			const run = await lighthouse(site + route, { port, output: 'json', logLevel: 'error', onlyCategories: row14 ? ['performance', 'accessibility'] : ['accessibility'] });
			if (!run?.lhr || run.lhr.runtimeError) {
				problems.push(`${where}: Lighthouse did not run: ${run?.lhr?.runtimeError?.message ?? 'no result'}`);
				continue;
			}
			const result = run.lhr;
			measured.push({ route, row14, measuredOnly, accessibility: result.categories.accessibility?.score, performance: result.categories.performance?.score ?? null,
				cls: result.audits['cumulative-layout-shift']?.numericValue ?? null, lcp: result.audits['largest-contentful-paint']?.numericValue ?? null });
			problems.push(...scoreProblems(where, result, { row14, measuredOnly }));
		}
	} finally {
		await browser.close();
	}
	return { problems, measured };
}

async function main(argv) {
	const option = (name, fallback = null) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const root = path.resolve(option('--root', c_Root));
	const distDir = path.resolve(option('--dist', path.join(root, 'dist')));
	const planned = plan(distDir);
	const routes = planned.visits.filter((visit) => !visit.route.startsWith('print/')).map((visit) => visit.route);
	const { serveSite } = await import('./serve.mjs');
	const site = await serveSite({ argv });
	const base = new URL(site.url).pathname.replace(/\/$/, '');
	const count = Number(option('--heaviest', '1'));
	if (!Number.isInteger(count) || count < 1) throw new Error(`--heaviest takes a whole number of pages, at least 1 (not ${option('--heaviest')})`);
	const heaviest = heaviestFigurePages(distDir, base, count);
	const figurePages = row14Pages(heaviest);
	const pages = [...new Set(routes)].filter((route) => !figurePages.some((page) => page.route === route)).map((route) => ({ route, row14: false })).concat(figurePages);
	let result;
	try {
		result = await runLighthouse({ site: site.url, pages });
	} finally {
		await site.stop();
	}
	const problems = [...planned.problems, ...result.problems];
	if (!heaviest.length) problems.push('no page of the build shows a picture: row 14 has no figure page to measure');
	for (const entry of result.measured) {
		console.log(`${entry.route || '(home)'}: accessibility ${Math.round(entry.accessibility * 100)}${entry.row14 ? `, performance ${Math.round(entry.performance * 100)}, CLS ${entry.cls}, LCP ${Math.round(entry.lcp)} ms (${entry.measuredOnly ? 'a heavy figure page, measured' : 'the heaviest figure page, row 14'})` : ''}`);
	}
	for (const problem of problems) console.log(problem);
	if (argv.includes('--not-row-14')) console.log('lighthouse: row 14 is judged on ubuntu-latest; these numbers were measured on another machine');
	console.log(`lighthouse: ${result.measured.length} pages; ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
	const json = option('--json');
	if (json) writeFileSync(json, `${JSON.stringify({ measured: result.measured, problems })}\n`);
	return problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

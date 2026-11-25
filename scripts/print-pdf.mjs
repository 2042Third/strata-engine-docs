// Budget row 19 (plan/site.md, "Budgets and the spike"): the print view of a part, printed to PDF with Playwright's
// Chromium. It loads <base>/print/<part>/ from a server of the built site, counts the ids that stand on more than one
// element (the print view prefixes every chapter's ids, so none may), prints the page to PDF and reports the time, the
// PDF's size and its pages. Run it inside tools/measure.py for the row's memory, which counts Chromium's processes.
//
//     node scripts/print-pdf.mjs [--part make] [--out <file.pdf>] [--json <file>] [--url http://host/strata-engine-docs/]
//         [--root <book folder>]
//
// It serves the build with tools/crawl.py (name Python in PYTHON where `python` is not on the PATH) unless --url names a
// server that runs. Exit codes: 0 printed with no duplicate id; 1 an id is duplicated, or the page did not load or print;
// 2 usage.

import { appendFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { serveSite } from './serve.mjs';

/** The ids of a list that occur more than once, each with its count, in the order they first occur. */
export function duplicateIds(ids) {
	const counts = new Map();
	for (const id of ids) counts.set(id, (counts.get(id) ?? 0) + 1);
	return [...counts].filter(([, count]) => count > 1).map(([id, count]) => ({ id, count }));
}

/** The pages of a PDF file: its page objects (`/Type /Page`, not the `/Pages` tree nodes). */
export function pdfPageCount(bytes) {
	return (bytes.toString('latin1').match(/\/Type\s*\/Page(?![a-zA-Z])/g) ?? []).length;
}

/**
 * Loads `url` in Chromium, reads every id of the page and prints it to `pdf`. Resolves to `{ loadSeconds,
 * printSeconds, ids, duplicates, bytes, pages }`.
 */
export async function printToPdf(url, pdf) {
	const { chromium } = await import('playwright');
	const browser = await chromium.launch();
	try {
		const page = await browser.newPage();
		const started = performance.now();
		const answer = await page.goto(url, { waitUntil: 'load', timeout: 300000 });
		if (!answer || !answer.ok()) throw new Error(`${url} answered ${answer ? answer.status() : 'nothing'}`);
		const loaded = performance.now();
		const ids = await page.evaluate(() => [...document.querySelectorAll('[id]')].map((element) => element.id));
		const printStarted = performance.now();
		await page.emulateMedia({ media: 'print' });
		const bytes = await page.pdf({ path: pdf, format: 'A4', printBackground: true, timeout: 600000 });
		const printed = performance.now();
		return { loadSeconds: (loaded - started) / 1000, printSeconds: (printed - printStarted) / 1000, ids: ids.length, duplicates: duplicateIds(ids), bytes: bytes.length, pages: pdfPageCount(bytes) };
	} finally {
		await browser.close();
	}
}

function option(argv, name, fallback = null) {
	const index = argv.indexOf(name);
	if (index < 0) return fallback;
	if (index + 1 >= argv.length) throw new Error(`${name} needs a value`);
	return argv[index + 1];
}

export async function main(argv) {
	let part;
	try {
		part = option(argv, '--part', 'make');
		if (!/^[a-z0-9-]+$/.test(part)) throw new Error(`--part names a part's slug, such as make: ${part}`);
	} catch (error) {
		console.error(`print-pdf: ${error.message}`);
		return 2;
	}
	const scratch = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'print-pdf-'));
	const pdf = path.resolve(option(argv, '--out', path.join(scratch, `${part}.pdf`)));
	mkdirSync(path.dirname(pdf), { recursive: true });
	const site = await serveSite({ argv });
	try {
		const url = new URL(`print/${part}/`, site.url).href;
		const result = await printToPdf(url, pdf);
		const line = { part, url, ...result, duplicates: result.duplicates.length, duplicated: result.duplicates.slice(0, 20) };
		console.log(`print-pdf: ${url}: loaded in ${result.loadSeconds.toFixed(1)} s, printed in ${result.printSeconds.toFixed(1)} s; ${result.pages} pages, ${(result.bytes / 1048576).toFixed(1)} MB; ${result.ids} ids, ${result.duplicates.length} duplicated`);
		for (const { id, count } of result.duplicates.slice(0, 20)) console.log(`  the id "${id}" stands on ${count} elements: the print view prefixes each chapter's ids (src/lib/print.mjs)`);
		const json = option(argv, '--json');
		if (json) appendFileSync(json, `${JSON.stringify(line)}\n`);
		return result.duplicates.length ? 1 : 0;
	} catch (error) {
		console.error(`print-pdf: ${error.message}`);
		return 1;
	} finally {
		await site.stop();
		if (!argv.includes('--out')) rmSync(scratch, { recursive: true, force: true });
	}
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

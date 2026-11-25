// The search check: Pagefind runs in Chromium on the staged site, under the base path. A two-word query must find
// results, every result's URL must be under the base, and the bytes the query downloads (Pagefind's script, its
// WebAssembly, the index chunks and fragments) are measured against the budget; then the next query, which reuses
// what the first one loaded, is measured against its own budget (plan/site.md, "Search"; budget row 12). The budgets
// count bytes over the wire as the deployments serve them: Pagefind's index, fragments and WebAssembly are compressed
// files already, and its scripts are compressed by nginx (the staged test server sends them as they are, so they are
// gzipped here).
//
//     node scripts/search-payload.mjs [--query "fixed step"] [--next-query "drawn transform"] [--max-kb <budget>]
//         [--max-next-kb <budget>] [--json <file>] [--files] [--url ...] [--root <book folder>]

import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';

/** Bytes over the wire of a response: compressed here when the deployments compress it, as they are otherwise. */
export function wireBytes(body, contentType) {
	const compressible = /javascript|json|css|text/.test(contentType ?? '');
	return compressible ? gzipSync(body).length : body.length;
}

/** The sum of `{ raw, wire }` sizes. */
export function totals(sizes) {
	return [...sizes].reduce((sum, size) => ({ raw: sum.raw + size.raw, wire: sum.wire + size.wire }), { raw: 0, wire: 0 });
}

/** What is over budget: messages for the first and the next query (kilobytes are 1,024 bytes). */
export function budgetProblems({ first, next }, { maxKilobytes, maxNextKilobytes }) {
	const problems = [];
	if (first / 1024 > maxKilobytes) problems.push(`the first query downloaded ${(first / 1024).toFixed(1)} KB, over the budget of ${maxKilobytes} KB`);
	if (next / 1024 > maxNextKilobytes) problems.push(`the next query downloaded ${(next / 1024).toFixed(1)} KB, over the budget of ${maxNextKilobytes} KB`);
	return problems;
}

async function main(argv) {
	const option = (name, fallback) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const query = option('--query', 'fixed step');
	const nextQuery = option('--next-query', 'drawn transform');
	// The budgets of check 9 (tools/budgets.json) unless --max-kb and --max-next-kb say otherwise.
	const budgets = JSON.parse(readFileSync(new URL('../tools/budgets.json', import.meta.url), 'utf8'));
	const maxKilobytes = Number(option('--max-kb', String(budgets.search_query_kilobytes)));
	const maxNextKilobytes = Number(option('--max-next-kb', String(budgets.search_next_query_kilobytes)));
	const { chromium } = await import('playwright');
	const { serveSite } = await import('./serve.mjs');
	const site = await serveSite({ argv });
	const browser = await chromium.launch();
	let failed = false;
	try {
		const page = await browser.newPage();
		await page.goto(site.url, { waitUntil: 'networkidle' });
		let searchBytes = new Map();
		page.on('response', async (response) => {
			const url = response.url();
			if (!url.includes('/pagefind/')) return;
			const sizes = searchBytes;
			try {
				const body = await response.body();
				sizes.set(url, { raw: body.length, wire: wireBytes(body, response.headers()['content-type']) });
			} catch {
				// A response without a body (a redirect) adds nothing.
			}
		});
		const run = async (words) => {
			await page.fill('#starlight__search input', words);
			await page.waitForSelector('#starlight__search .pagefind-ui__result', { timeout: 30000 });
			// Pagefind's UI shows a result as a placeholder until its fragment has loaded: wait until every result has
			// its link, or a result is read without its URL and the fragments' bytes are not yet counted.
			await page.waitForFunction(() => {
				const nodes = [...document.querySelectorAll('#starlight__search .pagefind-ui__result')];
				return nodes.length > 0 && nodes.every((node) => node.querySelector('a[href]'));
			}, null, { timeout: 30000 });
			await page.waitForLoadState('networkidle');
			return page.$$eval('#starlight__search .pagefind-ui__result', (nodes) =>
				nodes.map((node) => ({
					title: node.querySelector('.pagefind-ui__result-title')?.textContent?.trim(),
					url: node.querySelector('a')?.getAttribute('href'),
					tags: [...node.querySelectorAll('.pagefind-ui__result-tag')].map((tag) => tag.textContent.trim()),
				})),
			);
		};
		await page.click('button[data-open-modal]');
		const results = await run(query);
		const firstFiles = searchBytes;
		searchBytes = new Map();
		// The search box is emptied first, so that the results waited for next are the next query's, not the first's.
		await page.fill('#starlight__search input', '');
		await page.waitForSelector('#starlight__search .pagefind-ui__result', { state: 'detached', timeout: 30000 });
		const nextResults = await run(nextQuery);
		const nextFiles = searchBytes;
		const first = totals(firstFiles.values());
		const next = totals(nextFiles.values());
		const base = new URL(site.url).pathname;
		console.log(`search: "${query}" found ${results.length} result${results.length === 1 ? '' : 's'}; downloaded ${(first.wire / 1024).toFixed(1)} KB over the wire (${(first.raw / 1024).toFixed(1)} KB as files) in ${firstFiles.size} files`);
		for (const result of results.slice(0, 5)) console.log(`  ${result.title} (${result.tags.join(', ')}) ${result.url}`);
		console.log(`search: then "${nextQuery}" found ${nextResults.length} result${nextResults.length === 1 ? '' : 's'}; downloaded ${(next.wire / 1024).toFixed(1)} KB over the wire (${(next.raw / 1024).toFixed(1)} KB as files) in ${nextFiles.size} files`);
		if (argv.includes('--files')) {
			for (const [label, files] of [['first', firstFiles], ['next', nextFiles]]) {
				for (const [url, size] of files) console.log(`  ${label} ${String(size.wire).padStart(8)} ${String(size.raw).padStart(8)} ${url.split('/pagefind/')[1]}`);
			}
		}
		for (const [words, found] of [[query, results], [nextQuery, nextResults]]) {
			if (found.length === 0) {
				console.log(`search: "${words}" found no results`);
				failed = true;
			}
			for (const result of found) {
				if (!result.url?.startsWith(base)) {
					console.log(`search: the result ${result.url} is not under ${base}`);
					failed = true;
				}
			}
		}
		for (const problem of budgetProblems({ first: first.wire, next: next.wire }, { maxKilobytes, maxNextKilobytes })) {
			console.log(`search: ${problem}`);
			failed = true;
		}
		const summary = { query, results: results.length, bytes: first.wire, rawBytes: first.raw, files: firstFiles.size, nextQuery, nextResults: nextResults.length, nextBytes: next.wire, nextRawBytes: next.raw, nextFiles: nextFiles.size };
		console.log(JSON.stringify(summary));
		const jsonFile = option('--json', null);
		if (jsonFile) writeFileSync(jsonFile, `${JSON.stringify(summary)}\n`);
	} finally {
		await browser.close();
		await site.stop();
	}
	return failed ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

// Check 9's Lighthouse run and budget row 14 (scripts/lighthouse.mjs): which page is the heaviest figure page, what a
// result fails, and Lighthouse itself in Chromium on a fixture page with a planted accessibility fault.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { c_Row14, heaviestFigurePage, heaviestFigurePages, pictureBytes, row14Pages, runLighthouse, scoreProblems } from '../../../scripts/lighthouse.mjs';

function write(folder, files) {
	for (const [relative, content] of Object.entries(files)) {
		const file = path.join(folder, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	}
}

test('the heaviest figure page is the one whose pictures weigh the most, at three bases', () => {
	for (const base of ['', '/docs', '/x/y']) {
		const folder = mkdtempSync(path.join(tmpdir(), 'lighthouse-pages-'));
		try {
			write(folder, {
				'a/index.html': `<img src="${base}/_figures/a/small.avif" alt="s">`,
				'b/index.html': `<img src="${base}/_figures/b/big.avif" alt="b"><img src="${base}/_figures/b/big.avif" alt="again">`,
				'print/b/index.html': `<img src="${base}/_figures/b/big.avif" alt="b"><img src="${base}/_figures/a/small.avif" alt="s">`,
				'c/index.html': '<img src="https://elsewhere.example/x.avif" alt="x"><p>No picture of its own.</p>',
				'_figures/a/small.avif': Buffer.alloc(100),
				'_figures/b/big.avif': Buffer.alloc(1000),
			});
			assert.deepEqual(heaviestFigurePage(folder, base), { route: 'b/', bytes: 1000 }, base);
			// The heaviest first, then the next ones, never a print view or a page without a picture.
			assert.deepEqual(heaviestFigurePages(folder, base, 3), [{ route: 'b/', bytes: 1000 }, { route: 'a/', bytes: 100 }], base);
			assert.deepEqual(heaviestFigurePages(folder, base, 1), [{ route: 'b/', bytes: 1000 }], base);
			assert.equal(pictureBytes('<img src="/other/_figures/b/big.avif" alt="">', folder, base), 0);
		} finally {
			rmSync(folder, { recursive: true, force: true });
		}
	}
});

test('row 14 is judged on the heaviest figure page, and the next ones named by --heaviest are measured beside it', () => {
	const heaviest = [{ route: 'b/', bytes: 1000 }, { route: 'a/', bytes: 100 }];
	assert.deepEqual(row14Pages(heaviest), [{ route: 'b/', row14: true, measuredOnly: false }, { route: 'a/', row14: true, measuredOnly: true }]);
	assert.deepEqual(row14Pages([]), []);
	assert.deepEqual(scoreProblems('a/', result({ performance: 0.5 }), { row14: true, measuredOnly: true }), []);
});

function result({ accessibility = 1, performance = 1, cls = 0, lcp = 1000, failed = [] } = {}) {
	const audits = { 'cumulative-layout-shift': { numericValue: cls }, 'largest-contentful-paint': { numericValue: lcp } };
	for (const id of failed) audits[id] = { id, score: 0, scoreDisplayMode: 'binary' };
	return { categories: { accessibility: { score: accessibility, auditRefs: failed.map((id) => ({ id, weight: 7 })) }, performance: { score: performance } }, audits };
}

test('a page fails below accessibility 100, and the figure page below row 14\'s four marks', () => {
	assert.deepEqual(scoreProblems('a/', result()), []);
	assert.deepEqual(scoreProblems('a/', result(), { row14: true }), []);
	assert.deepEqual(scoreProblems('a/', result({ accessibility: 0.96, failed: ['image-alt'] })), ['a/: accessibility 96, not 100 (image-alt)']);
	// The figure page's other marks count only for it.
	assert.deepEqual(scoreProblems('a/', result({ performance: 0.5, cls: 1, lcp: 9000 })), []);
	assert.deepEqual(scoreProblems('b/', result({ performance: 0.89, cls: 0.051, lcp: 2501 }), { row14: true }), [
		'b/: performance 89, under 90', 'b/: cumulative layout shift 0.051, over 0.05', 'b/: largest contentful paint 2501 ms, over 2500 ms']);
	assert.deepEqual(scoreProblems('b/', result({ performance: c_Row14.performance, cls: c_Row14.cls, lcp: c_Row14.lcpMilliseconds }), { row14: true }), []);
});

test('Lighthouse in Chromium finds a planted accessibility fault and passes the page without it', async () => {
	const folder = mkdtempSync(path.join(tmpdir(), 'lighthouse-run-'));
	const page = (image) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A page</title></head>`
		+ `<body><main><h1>A page</h1><p>Some words.</p>${image}</main></body></html>`;
	write(folder, {
		'good/index.html': page('<img src="/p.svg" alt="A grey box." width="20" height="10">'),
		'bad/index.html': page('<img src="/p.svg" width="20" height="10">'),
		'p.svg': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="20" height="10" fill="#888"/></svg>',
	});
	const server = createServer((request, response) => {
		let file = path.join(folder, ...new URL(request.url, 'http://fixture').pathname.split('/').filter(Boolean));
		try {
			if (statSync(file).isDirectory()) file = path.join(file, 'index.html');
			response.writeHead(200, { 'Content-Type': file.endsWith('.svg') ? 'image/svg+xml' : 'text/html; charset=utf-8' });
			response.end(readFileSync(file));
		} catch {
			response.writeHead(404);
			response.end();
		}
	});
	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
	try {
		const { problems, measured } = await runLighthouse({ site: `http://127.0.0.1:${server.address().port}/`, pages: [{ route: 'good/', row14: false }, { route: 'bad/', row14: false }] });
		assert.equal(measured.length, 2);
		assert.equal(measured[0].accessibility, 1);
		assert.equal(problems.length, 1, problems.join('\n'));
		assert.match(problems[0], /^bad\/: accessibility \d+, not 100 \(.*image-alt.*\)$/);
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
});

// Check 9's axe run (scripts/a11y.mjs): which pages --all and the sample check, and axe in Chromium failing a planted
// serious violation in one theme and passing the page without it.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { allPages, c_MissingRoute, runAxe, samplePages } from '../../../scripts/a11y.mjs';

function write(folder, files) {
	for (const [relative, content] of Object.entries(files)) {
		const file = path.join(folder, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	}
}

const kind = (name) => `<span hidden data-pagefind-meta="kind">${name}</span>`;

test('--all checks every page with the 404 page, and the sample the gate\'s pages and one page per component', () => {
	const folder = mkdtempSync(path.join(tmpdir(), 'a11y-pages-'));
	try {
		write(folder, {
			'index.html': '<p>home</p>',
			'a/index.html': kind('Primer') + '<details class="book-answer"><summary>x</summary></details>',
			'b/index.html': kind('Concept') + '<book-tabs></book-tabs>',
			'b2/index.html': kind('Concept') + '<book-tabs></book-tabs><span class="katex">x</span>',
			'c/index.html': kind('Internals'), 'd/index.html': kind('Tutorial'), 'e/index.html': kind('How-to') + '<book-track-chooser></book-track-chooser>',
			'g/index.html': kind('Reference') + '<dl class="book-glossary"></dl>', 'print/a/index.html': '<book-compare></book-compare>',
			'z/index.html': '<book-compare></book-compare>',
			'_astro/x/index.html': 'not a page', '404.html': 'missing',
		});
		// In the order of the folder: index.html stands among the folders by its name.
		assert.deepEqual(allPages(folder), ['a/', 'b/', 'b2/', 'c/', 'd/', 'e/', 'g/', '', 'print/a/', 'z/', c_MissingRoute]);
		// The print view's slider does not stand for the slider of a chapter: z/ does.
		assert.deepEqual(samplePages(folder), ['', 'a/', 'b/', 'c/', 'd/', 'e/', 'g/', 'print/a/', 'z/', 'b2/', c_MissingRoute]);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('axe in Chromium fails a serious violation in the theme that has it and passes a clean page', async () => {
	const folder = mkdtempSync(path.join(tmpdir(), 'a11y-run-'));
	// The dark theme (the stored choice that Starlight reads) draws grey words on grey: contrast fails only there.
	const theme = '<script>document.documentElement.dataset.theme = localStorage.getItem("starlight-theme") || "light";</script>'
		+ '<style>[data-theme="dark"] p { color: #777; background: #666; }</style>';
	const page = (body) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>A page</title>${theme}</head><body><main><h1>A page</h1>${body}</main></body></html>`;
	write(folder, {
		'good/index.html': page('<img src="/p.svg" alt="A grey box.">'),
		'bad/index.html': page('<p>Words.</p><img src="/p.svg">'),
		'p.svg': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="20" height="10" fill="#888"/></svg>',
	});
	const server = createServer((request, response) => {
		let file = path.join(folder, ...new URL(request.url, 'http://fixture').pathname.split('/').filter(Boolean));
		try {
			if (statSync(file).isDirectory()) file = path.join(file, 'index.html');
			response.writeHead(200, { 'Content-Type': file.endsWith('.svg') ? 'image/svg+xml' : 'text/html; charset=utf-8' });
			response.end(readFileSync(file));
		} catch {
			response.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
			response.end('<!doctype html><html lang="en"><head><title>Not found</title></head><body><main><h1>Not found</h1></main></body></html>');
		}
	});
	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
	try {
		const site = `http://127.0.0.1:${server.address().port}/`;
		const { failures } = await runAxe({ site, routes: ['good/', 'bad/', c_MissingRoute], log: () => {} });
		const lines = failures.filter((line) => !line.startsWith('    '));
		assert.ok(lines.includes('bad/ [dark]: critical: image-alt: Images must have alternative text'), lines.join('\n'));
		assert.ok(lines.includes('bad/ [light]: critical: image-alt: Images must have alternative text'), lines.join('\n'));
		assert.ok(lines.includes('bad/ [dark]: serious: color-contrast: Elements must meet minimum color contrast ratio thresholds'), lines.join('\n'));
		assert.ok(!lines.some((line) => line.startsWith('bad/ [light]: serious: color-contrast')), lines.join('\n'));
		// The themes are checked at the same time, and their failures still come in the order of the themes.
		assert.ok(lines.findLastIndex((line) => line.includes(' [dark]: ')) < lines.findIndex((line) => line.includes(' [light]: ')), lines.join('\n'));
		assert.ok(!lines.some((line) => line.startsWith('good/') || line.startsWith(c_MissingRoute)), lines.join('\n'));
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
});

test('axe waits until a page is parsed: a heading link whose words come late is not found empty', async () => {
	// Busy scripts inside the link hold the parser for 8 s after every byte has arrived, as a 7 MB print view does in
	// Chromium: the network is quiet long before the link's words are parsed.
	const busy = '<script>{ const end = Date.now() + 250; while (Date.now() < end); }</script>';
	const html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>A page</title></head><body><main><h1>A page</h1>'
		+ `<h2 id="end">The end</h2><a href="#end">${busy.repeat(32)}<span>Section titled “The end”</span></a></main></body></html>`;
	const server = createServer((request, response) => {
		const found = new URL(request.url, 'http://fixture').pathname === '/slow/';
		response.writeHead(found ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
		response.end(found ? html : '<!doctype html><html lang="en"><head><title>Not found</title></head><body><main><h1>Not found</h1></main></body></html>');
	});
	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
	try {
		const site = `http://127.0.0.1:${server.address().port}/`;
		const { failures } = await runAxe({ site, routes: ['slow/'], themes: ['light'], log: () => {} });
		assert.deepEqual(failures, []);
	} finally {
		server.close();
	}
});

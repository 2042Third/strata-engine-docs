// The two measuring scripts of budget rows 6 and 19: scripts/dev-timing.mjs (the dev server's start and its refresh
// after an edit, with the page put back and the server ended) and scripts/print-pdf.mjs (a print view printed to PDF in
// Chromium, failing on an id that stands on two elements).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { devCommand, measureDev, until, withMarker } from '../../../scripts/dev-timing.mjs';
import { duplicateIds, pdfPageCount, printToPdf } from '../../../scripts/print-pdf.mjs';

test('the marker paragraph goes after the front matter, and at the top of a page without one', () => {
	assert.equal(withMarker('---\nid: core/time\n---\n\nText.\n', 'w1'), '---\nid: core/time\n---\n\nThe word w1 marks this change.\n\nText.\n');
	assert.equal(withMarker('Text.\n', 'w2'), 'The word w2 marks this change.\n\nText.\n');
	assert.equal(withMarker('---\r\nid: a\r\n---\r\nText.\r\n', 'w3'), '---\r\nid: a\r\n---\r\n\nThe word w3 marks this change.\n\nText.\r\n');
});

test('the dev server is the book\'s own Astro, on the port given, for the root given', () => {
	const { program, args } = devCommand('/book', 4399);
	assert.equal(program, process.execPath);
	assert.match(args[0], /node_modules[\\/]astro[\\/]bin[\\/]astro\.mjs$/);
	assert.deepEqual(args.slice(1), ['dev', '--root', '/book', '--port', '4399', '--host', '127.0.0.1']);
});

// A stand-in dev server: it starts after a short delay and serves the page file as it is on every request, as astro dev
// renders a page again after a change.
const c_StandIn = `
const { createServer } = require('node:http');
const { readFileSync } = require('node:fs');
const [file, port] = process.argv.slice(1);
setTimeout(() => createServer((request, response) => response.end(readFileSync(file, 'utf8'))).listen(Number(port), '127.0.0.1'), 300);
`;

function freePort() {
	return new Promise((resolve) => {
		const server = createServer();
		server.listen(0, '127.0.0.1', () => {
			const { port } = server.address();
			server.close(() => resolve(port));
		});
	});
}

test('the start and the refresh are measured, the page is put back and the server is ended', async () => {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'dev-timing-'));
	try {
		const file = path.join(folder, 'time.md');
		const original = '---\nid: core/time\n---\n\nText.\n';
		writeFileSync(file, original);
		const port = await freePort();
		let child;
		const result = await measureDev({ start: () => (child = spawn(process.execPath, ['-e', c_StandIn, file, String(port)], { stdio: ['ignore', 'pipe', 'pipe'] })), url: `http://127.0.0.1:${port}/core/time/`, file, startLimit: 20, refreshLimit: 10 });
		assert.deepEqual(result.problems, []);
		assert.ok(result.startSeconds >= 0.2, `the start waited for the server (${result.startSeconds} s)`);
		assert.ok(result.refreshSeconds >= 0 && result.refreshSeconds < 10);
		assert.equal(readFileSync(file, 'utf8'), original, 'the page is put back');
		await new Promise((resolve) => (child.exitCode !== null || child.signalCode !== null ? resolve() : child.once('exit', resolve)));
		assert.ok(child.exitCode !== null || child.signalCode !== null, 'the server is ended');
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('a server that never answers is a problem, and the page is put back', async () => {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'dev-timing-'));
	try {
		const file = path.join(folder, 'time.md');
		writeFileSync(file, 'Text.\n');
		const port = await freePort();
		const result = await measureDev({ start: () => spawn(process.execPath, ['-e', 'setTimeout(() => {}, 60000)'], { stdio: 'ignore' }), url: `http://127.0.0.1:${port}/`, file, startLimit: 1, refreshLimit: 1 });
		assert.equal(result.startSeconds, null);
		assert.match(result.problems[0], /did not answer 200 within 1 s/);
		assert.equal(readFileSync(file, 'utf8'), 'Text.\n');
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('until gives up after its limit', async () => {
	const port = await freePort();
	assert.equal(await until(`http://127.0.0.1:${port}/`, (answer) => answer.status === 200, 0.3, 50), null);
});

test('duplicate ids are counted, and a PDF\'s pages are its page objects', () => {
	assert.deepEqual(duplicateIds(['a', 'b', 'a', 'c', 'b', 'a']), [{ id: 'a', count: 3 }, { id: 'b', count: 2 }]);
	assert.deepEqual(duplicateIds(['a', 'b']), []);
	assert.equal(pdfPageCount(Buffer.from('<< /Type /Pages /Kids [1 0 R 2 0 R] >> << /Type /Page >> << /Type/Page /Parent 3 0 R >>')), 2);
});

test('a print view is printed to PDF in Chromium, and its duplicated ids are found', async () => {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'print-pdf-'));
	const pages = {
		'/print/clean/': '<!doctype html><html lang="en"><title>Clean</title><h1 id="a">A</h1><p id="b">B</p></html>',
		'/print/twice/': '<!doctype html><html lang="en"><title>Twice</title><h2 id="core-time--summary">A</h2><h2 id="core-time--summary">B</h2></html>',
	};
	const server = createServer((request, response) => {
		const html = pages[request.url];
		response.writeHead(html ? 200 : 404, { 'content-type': 'text/html' });
		response.end(html ?? 'missing');
	});
	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
	const site = `http://127.0.0.1:${server.address().port}`;
	try {
		mkdirSync(folder, { recursive: true });
		const clean = await printToPdf(`${site}/print/clean/`, path.join(folder, 'clean.pdf'));
		assert.deepEqual(clean.duplicates, []);
		assert.equal(clean.ids, 2);
		assert.ok(clean.pages >= 1 && clean.bytes > 0);
		assert.equal(readFileSync(path.join(folder, 'clean.pdf')).subarray(0, 5).toString(), '%PDF-');
		const twice = await printToPdf(`${site}/print/twice/`, path.join(folder, 'twice.pdf'));
		assert.deepEqual(twice.duplicates, [{ id: 'core-time--summary', count: 2 }]);
		await assert.rejects(printToPdf(`${site}/print/none/`, path.join(folder, 'none.pdf')), /answered 404/);
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
});

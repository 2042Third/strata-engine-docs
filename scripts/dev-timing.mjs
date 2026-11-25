// Budget row 6 (plan/site.md, "Budgets and the spike"): how long `astro dev` takes to serve a page after it starts, and
// how long a change to that page takes to reach a request for it. It starts the dev server of a book, waits for the
// page's first answer (the start), then adds a paragraph with a word of its own after the page's front matter and asks
// for the page until its HTML holds the word (the refresh after an edit). The page is put back as it was, and the
// server is ended with its process tree, whatever happens.
//
//     node scripts/dev-timing.mjs [--root <book folder>] [--page core/time] [--port 4399] [--json <file>]
//         [--start-limit 300] [--refresh-limit 60]
//
// Exit codes: 0 measured; 1 the server did not answer, the change did not arrive within its limit, or the page could
// not be read or put back; 2 usage.

import { execFileSync, spawn } from 'node:child_process';
import { appendFileSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { readSettings } from '../src/lib/settings.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/** The page with a paragraph that holds `marker` after its front matter (or at its top when it has none). */
export function withMarker(text, marker) {
	const paragraph = `The word ${marker} marks this change.\n\n`;
	const match = /^---\r?\n[\s\S]*?\r?\n---\r?\n/.exec(text);
	if (!match) return `${paragraph}${text}`;
	return `${match[0]}\n${paragraph}${text.slice(match[0].length).replace(/^\r?\n/, '')}`;
}

/** The program and arguments that start a book's dev server on a port. */
export function devCommand(root, port) {
	return { program: process.execPath, args: [path.join(c_Root, 'node_modules', 'astro', 'bin', 'astro.mjs'), 'dev', '--root', root, '--port', String(port), '--host', '127.0.0.1'] };
}

/** Ends a process and every process it started. */
export function endTree(child) {
	if (child.exitCode !== null || child.signalCode !== null) return;
	try {
		if (process.platform === 'win32') execFileSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
		else process.kill(-child.pid, 'SIGKILL');
	} catch {
		// The process ended between the check and the call.
	}
}

async function fetchText(url) {
	try {
		const answer = await fetch(url, { signal: AbortSignal.timeout(30000) });
		return { status: answer.status, text: await answer.text() };
	} catch {
		return { status: 0, text: '' };
	}
}

/** Asks for `url` every `interval` ms until `done(answer)` holds or `limit` seconds pass; resolves to the seconds taken or null. */
export async function until(url, done, limit, interval = 100) {
	const started = performance.now();
	while ((performance.now() - started) / 1000 < limit) {
		if (done(await fetchText(url))) return (performance.now() - started) / 1000;
		await new Promise((resolve) => setTimeout(resolve, interval));
	}
	return null;
}

/**
 * Starts the server (`start()` returns its child process), measures the start and the refresh of the page file `file`
 * served at `url`, puts the file back and ends the server. Resolves to `{ startSeconds, refreshSeconds, problems }`.
 */
export async function measureDev({ start, url, file, startLimit = 300, refreshLimit = 60 }) {
	const original = readFileSync(file);
	const problems = [];
	const began = performance.now();
	const child = start();
	let output = '';
	child.stdout?.on('data', (chunk) => (output = `${output}${chunk}`.slice(-4000)));
	child.stderr?.on('data', (chunk) => (output = `${output}${chunk}`.slice(-4000)));
	let startSeconds = null;
	let refreshSeconds = null;
	try {
		const waited = await until(url, (answer) => answer.status === 200, startLimit, 250);
		if (waited === null) problems.push(`${url} did not answer 200 within ${startLimit} s of the start; the server printed:\n${output}`);
		else {
			startSeconds = (performance.now() - began) / 1000;
			const marker = `scalemark${Date.now().toString(36)}`;
			writeFileSync(file, withMarker(original.toString('utf8'), marker));
			refreshSeconds = await until(url, (answer) => answer.status === 200 && answer.text.includes(marker), refreshLimit);
			if (refreshSeconds === null) problems.push(`the change to ${file} did not reach ${url} within ${refreshLimit} s`);
		}
	} finally {
		writeFileSync(file, original);
		endTree(child);
	}
	return { startSeconds, refreshSeconds, problems };
}

function option(argv, name, fallback) {
	const index = argv.indexOf(name);
	if (index < 0) return fallback;
	if (index + 1 >= argv.length) throw new Error(`${name} needs a value`);
	return argv[index + 1];
}

export async function main(argv) {
	let root;
	let page;
	let port;
	let limits;
	try {
		root = path.resolve(option(argv, '--root', c_Root));
		page = option(argv, '--page', 'core/time');
		port = Number(option(argv, '--port', '4399'));
		limits = { startLimit: Number(option(argv, '--start-limit', '300')), refreshLimit: Number(option(argv, '--refresh-limit', '60')) };
		if (!/^[a-z0-9-]+(\/[a-z0-9-]+)*$/.test(page) || !Number.isInteger(port) || !(limits.startLimit > 0 && limits.refreshLimit > 0)) throw new Error('--page is a page id, --port a whole number, the limits seconds above 0');
	} catch (error) {
		console.error(`dev-timing: ${error.message}`);
		return 2;
	}
	const settings = readSettings({ root });
	const base = settings.base === '/' ? '' : settings.base.replace(/\/$/, '');
	const url = `http://127.0.0.1:${port}${base}/${page}/`;
	const file = path.join(settings.docsDir, ...`${page}.md`.split('/'));
	const { program, args } = devCommand(root, port);
	const result = await measureDev({ start: () => spawn(program, args, { cwd: root, stdio: ['ignore', 'pipe', 'pipe'], detached: process.platform !== 'win32' }), url, file, ...limits });
	for (const problem of result.problems) console.error(`dev-timing: ${problem}`);
	console.log(`dev-timing: ${page}: start ${result.startSeconds?.toFixed(1) ?? 'not reached'} s, refresh after an edit ${result.refreshSeconds?.toFixed(2) ?? 'not reached'} s`);
	const json = option(argv, '--json', null);
	if (json) appendFileSync(json, `${JSON.stringify({ page, url, ...result })}\n`);
	return result.problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));

// Check 9's keyboard tests (scripts/keyboard.mjs) in Chromium: the book's own client script on fixture pages passes
// every check, and markup that breaks each pattern fails it.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { keyboardPages, runKeyboard } from '../../../scripts/keyboard.mjs';

const c_Client = path.resolve(import.meta.dirname, '..', '..', 'components', 'client');
const c_Types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript' };

function serve(folder) {
	const server = createServer((request, response) => {
		let file = path.join(folder, ...decodeURIComponent(new URL(request.url, 'http://fixture').pathname).split('/').filter(Boolean));
		try {
			if (statSync(file).isDirectory()) file = path.join(file, 'index.html');
			const body = readFileSync(file);
			response.writeHead(200, { 'Content-Type': c_Types[path.extname(file)] ?? 'application/octet-stream' });
			response.end(body);
		} catch {
			response.writeHead(404, { 'Content-Type': 'text/plain' });
			response.end('not here');
		}
	});
	return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function site(files) {
	const folder = mkdtempSync(path.join(tmpdir(), 'keyboard-'));
	const all = { '_astro/book.js': readFileSync(path.join(c_Client, 'book.js'), 'utf8'), '_astro/print.js': readFileSync(path.join(c_Client, 'print.js'), 'utf8'), ...files };
	for (const [relative, text] of Object.entries(all)) {
		const file = path.join(folder, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, text);
	}
	return folder;
}

function page(body, script = true) {
	return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>t</title></head><body><main><a href="#x">a link first</a>${body}</main>`
		+ `${script ? '<script type="module" src="/_astro/book.js"></script>' : ''}</body></html>`;
}

const c_Pagination = '<div class="book-pagination"><div class="pagination-links"><a href="/next/" rel="next">Next</a></div>'
	+ '<template data-book-track="game"><a href="/game-next/" rel="next">Next on the track</a></template><template data-book-track="engine"><a href="/engine-next/" rel="next">Next on the track</a></template></div>';

const c_Good = {
	'tabs/index.html': page('<book-tabs data-sync="os"><div class="book-tabs__panel" data-label="Windows"><p>w</p></div><div class="book-tabs__panel" data-label="Linux"><p>l</p></div><div class="book-tabs__panel" data-label="macOS"><p>m</p></div></book-tabs>'),
	'slider/index.html': page('<book-compare><figure class="book-compare__item" data-label="off">a</figure><figure class="book-compare__item" data-label="on">b</figure></book-compare>'),
	'answer/index.html': page('<details class="book-answer"><summary>Answer</summary><p>Yes.</p></details>'),
	'popover/index.html': page('<p>A <a href="/g/#frame">frame</a><button type="button" class="book-term__button" popovertarget="book-term-frame">Definition of frame</button></p><div id="book-term-frame" popover="auto"><p>A picture.</p></div>'),
	'chooser/index.html': page(`<book-track-chooser><button type="button" class="book-track__choose" data-track="game" hidden>Follow</button><button type="button" class="book-track__choose" data-track="engine" hidden>Follow</button></book-track-chooser>${c_Pagination}`),
};

async function run(files) {
	const folder = site(files);
	const server = await serve(folder);
	try {
		const pages = { tabs: 'tabs/', slider: 'slider/', answer: 'answer/', popover: 'popover/', chooser: 'chooser/' };
		return (await runKeyboard({ site: `http://127.0.0.1:${server.address().port}/`, pages })).problems;
	} finally {
		server.close();
		rmSync(folder, { recursive: true, force: true });
	}
}

test('the book\'s client script passes every keyboard check', async () => {
	assert.deepEqual(await run(c_Good), []);
});

test('markup that breaks each pattern fails its check', async () => {
	const problems = await run({
		// A tab list whose tabs do not answer the arrow keys, Home or End.
		'tabs/index.html': page('<book-tabs><div role="tablist"><button role="tab" id="x0" aria-selected="true">A</button><button role="tab" id="x1" aria-selected="false">B</button></div>'
			+ '<div role="tabpanel">a</div></book-tabs>', false),
		// A slider without a label (book.js would give it one).
		'slider/index.html': page('<book-compare data-enhanced="true"><input type="range" min="0" max="100" value="50"></book-compare>'),
		// An answer that is no <details>.
		'answer/index.html': page('<div class="book-answer"><p>Yes.</p></div>'),
		// A popover that Escape does not close.
		'popover/index.html': page('<button type="button" class="book-term__button" popovertarget="book-term-frame">Definition of frame</button><div id="book-term-frame" popover="manual"><p>A picture.</p></div>'),
		// Chooser buttons out of the tab order.
		'chooser/index.html': page(`<book-track-chooser><button type="button" class="book-track__choose" data-track="game" hidden tabindex="-1">Follow</button></book-track-chooser>${c_Pagination}`.replace('<button', '<button onfocus=""')),
	});
	assert.deepEqual(problems, [
		'tabs/: tabs: ArrowRight selects tab 1 with the focus on "x0", not tab 2',
		'slider/: the slider has no label (aria-label or a <label>)',
		'answer/: an answer: no closed <details class="book-answer"> with a <summary>',
		'popover/: a term: Escape does not close the popover #book-term-frame',
		'chooser/: the track chooser: Tab never reaches the button of the track game',
	]);
});

// A tab list that answers the arrow keys, Home and End, but keeps every tab in the tab order, so Tab stays in it.
const c_TabsKeptInOrder = '<book-tabs><div role="tablist"><button role="tab" id="t0" aria-selected="true">A</button><button role="tab" id="t1" aria-selected="false">B</button></div><div role="tabpanel">a</div></book-tabs>'
	+ '<script>const tabs = [...document.querySelectorAll(\'[role="tab"]\')];'
	+ 'document.querySelector(\'[role="tablist"]\').addEventListener(\'keydown\', (event) => {'
	+ 'const at = tabs.indexOf(document.activeElement); const to = { ArrowRight: (at + 1) % tabs.length, ArrowLeft: (at + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1 }[event.key];'
	+ 'if (to === undefined) return; event.preventDefault(); tabs.forEach((tab, index) => tab.setAttribute(\'aria-selected\', String(index === to))); tabs[to].focus(); });</script>';

test('each part of each check fails on its own fault, with the others intact', async () => {
	// book.js with the choice no longer applied to the pagination: "next" keeps the parts' order.
	const client = readFileSync(path.join(c_Client, 'book.js'), 'utf8');
	const unapplied = client.replace('\t\t\t\tthis.update();\n\t\t\t\tapplyTrack();\n', '\t\t\t\tthis.update();\n');
	assert.notEqual(unapplied, client, 'book.js changed: the planted fault no longer applies');
	const problems = await run({
		'tabs/index.html': page(c_TabsKeptInOrder, false),
		// A labelled slider whose arrow keys do nothing.
		'slider/index.html': page('<book-compare data-enhanced="true"><input type="range" min="0" max="100" value="50" aria-label="Position" onkeydown="event.preventDefault()"></book-compare>'),
		// An answer that Enter opens and Space does not.
		'answer/index.html': page('<details class="book-answer"><summary onkeydown="if (event.key === \' \') event.preventDefault()" onkeyup="if (event.key === \' \') event.preventDefault()">Answer</summary><p>Yes.</p></details>'),
		// A popover that Escape closes, but that puts the focus elsewhere as it closes (beforetoggle runs within the
		// closing; toggle would come a task later).
		'popover/index.html': page('<button type="button" class="book-term__button" popovertarget="book-term-frame">Definition of frame</button>'
			+ '<div id="book-term-frame" popover="auto" onbeforetoggle="if (event.newState === \'closed\') document.querySelector(\'a\').focus()"><p>A picture.</p></div>'),
		'chooser/index.html': c_Good['chooser/index.html'],
		'_astro/book.js': unapplied,
	});
	// The fixture server's port differs from run to run.
	assert.deepEqual(problems.map((line) => line.replace(/127\.0\.0\.1:\d+/g, '127.0.0.1:<port>')), [
		'tabs/: tabs: Tab does not leave the tab list (only the selected tab is in the tab order)',
		'slider/: the slider: ArrowRight leaves it at 50 (it was 50)',
		'slider/: the slider: ArrowLeft leaves it at 50 (it was 50)',
		'answer/: an answer does not open with Space',
		'popover/: a term: after Escape the focus is on "a link first", not on the term\'s button',
		'chooser/: the track chooser: after choosing engine, "next" leads to http://127.0.0.1:<port>/next/, not to the track\'s http://127.0.0.1:<port>/engine-next/',
	]);
});

test('a chooser page without the chosen track\'s "next" fails instead of passing by finding nothing', async () => {
	const withoutEngine = c_Pagination.replace(/<template data-book-track="engine">.*?<\/template>/, '');
	assert.notEqual(withoutEngine, c_Pagination);
	const problems = await run({
		...c_Good,
		'chooser/index.html': page(`<book-track-chooser><button type="button" class="book-track__choose" data-track="game" hidden>Follow</button><button type="button" class="book-track__choose" data-track="engine" hidden>Follow</button></book-track-chooser>${withoutEngine}`),
	});
	assert.deepEqual(problems, ['chooser/: the track chooser: its page holds no "next" of the track engine (no <template data-book-track="engine"> in its pagination)']);
});

test('each check runs on the first page that holds its component, and a component no page holds fails', async () => {
	const folder = site({ ...c_Good, 'print/x/index.html': c_Good['tabs/index.html'] });
	try {
		assert.deepEqual(keyboardPages(folder), { tabs: 'tabs/', slider: 'slider/', answer: 'answer/', popover: 'popover/', chooser: 'chooser/' });
		rmSync(path.join(folder, 'slider'), { recursive: true });
		assert.equal(keyboardPages(folder).slider, null);
		const problems = (await runKeyboard({ site: 'http://127.0.0.1:1/', pages: { slider: null } })).problems;
		assert.deepEqual(problems, ['slider: no page of the build holds it, so it was not checked']);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

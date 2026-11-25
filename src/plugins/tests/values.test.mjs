// ":value{key=…}" (plan/pipelines.md §7.3; plan/style.md §13): a count the engine can change comes from
// src/generated/reference/values.json, never typed by hand. Its markup, where it may stand, and its failure messages,
// which name the page and the line.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parsePin } from '../../lib/settings.mjs';
import { loadValues, nearKeys, valueText } from '../../lib/values.mjs';
import { c_BottomStrip, c_ReferenceStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Commit = '822a7a46dbcdd86e8e2eafde7e41d003e27260c8';
const c_Values = JSON.stringify({ 'commands.count': 151, 'components.count': 38, 'engine.commit': c_Commit, 'quality.shadowScale.Medium': 0.6, 'importer.texture.version': '7' });

async function withPage(body, files = { 'src/generated/reference/values.json': c_Values }) {
	const book = makeBook({ pages: { 'editor/commands': `${frontmatter()}\n${body}\n${c_BottomStrip}` }, files });
	return {
		html: () => render(book.root, 'editor/commands'),
		remove: book.remove,
	};
}

async function html(body, files) {
	const page = await withPage(body, files);
	try {
		return await page.html();
	} finally {
		page.remove();
	}
}

async function fails(body, files, ...patterns) {
	const page = await withPage(body, files);
	try {
		return await rejectsWith(page.html(), ...patterns);
	} finally {
		page.remove();
	}
}

/** The line of the page a message names ("src/content/docs/editor/commands.md:14:5: …"). */
function lineOf(message, pattern) {
	const line = message.split('\n').find((candidate) => pattern.test(candidate));
	assert.ok(line, `no line matches ${pattern}:\n${message}`);
	return Number(/commands\.md:(\d+):\d+:/.exec(line)?.[1]);
}

test('a value takes the place of its mark, as the file writes it', async () => {
	const out = await html('## Counting\n\nThe editor has :value{key="commands.count"} commands and :value{key=components.count} components. Medium scales shadows by :value{key="quality.shadowScale.Medium"}; the texture importer is at version :value{key="importer.texture.version"}.');
	assert.match(out, /<p>The editor has <span class="book-value">151<\/span> commands and <span class="book-value">38<\/span> components\. Medium scales shadows by <span class="book-value">0\.6<\/span>; the texture importer is at version <span class="book-value">7<\/span>\.<\/p>/);
	assert.doesNotMatch(out, /:value/);
});

test('a value reads as plain words: in a title it names the aside, and a bare :value is prose', async () => {
	const out = await html(':::why[Why :value{key="commands.count"} commands?]\nBecause each is one thing an agent can do.\n:::\n\nThe word :value stays, as a:b does.');
	assert.match(out, /<aside class="starlight-aside book-aside book-aside--why" aria-label="Why 151 commands\?"><p class="starlight-aside__title" aria-hidden="true">Why <span class="book-value">151<\/span> commands\?<\/p>/);
	// A bare ":value" is prose, as "a:b" is: the page builds, and nothing takes its place. (Starlight writes such prose
	// back as text after the book's plugins; the tests run without Starlight.)
	assert.equal(out.match(/class="book-value"/g).length, 1);
});

test('the words of a value are the engine\'s, so the glossary links no term in them', async () => {
	const glossary = { terms: [{ id: 'frame', term: 'frame', definition: 'One pass of the engine\'s loop.', home: 'core/loop' }] };
	const book = makeBook({
		glossary,
		pages: {
			'editor/commands': `${frontmatter()}\n## Units\n\nThe step counts in :value{key="time.unit"}s.\n${c_BottomStrip}`,
			'reference/glossary': `${frontmatter({ kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\nThe list.\n\n::glossary\n${c_ReferenceStrip}`,
		},
		files: { 'src/generated/reference/values.json': JSON.stringify({ 'engine.commit': c_Commit, 'time.unit': 'frame' }) },
	});
	try {
		const out = await render(book.root, 'editor/commands');
		assert.match(out, /The step counts in <span class="book-value">frame<\/span>s\./);
		assert.doesNotMatch(out, /book-term/);
	} finally {
		book.remove();
	}
});

test('an unknown key fails at its line and names the keys it may have meant', async () => {
	const book = makeBook({
		pages: { 'editor/commands': `${frontmatter()}\n## Counting\n\nText.\n\nThe editor has :value{key="commands.cuont"} commands and :value{key="hosts.count"} hosts.\n${c_BottomStrip}` },
		files: { 'src/generated/reference/values.json': c_Values },
	});
	try {
		const error = await rejectsWith(render(book.root, 'editor/commands'),
			/:value\{key="commands\.cuont"\}: src\/generated\/reference\/values\.json has no key "commands\.cuont": did you mean "commands\.count"\?/,
			/:value\{key="hosts\.count"\}: src\/generated\/reference\/values\.json has no key "hosts\.count"; tools\/reference\.py render lists the keys it writes/);
		// The line of the file that holds both marks, as written (front matter included), and the column of each.
		const lines = readFileSync(path.join(book.root, 'src', 'content', 'docs', 'editor', 'commands.md'), 'utf8').split('\n');
		const line = lines.findIndex((candidate) => candidate.startsWith('The editor has')) + 1;
		assert.equal(lineOf(error.message, /commands\.cuont/), line);
		assert.equal(lineOf(error.message, /hosts\.count/), line);
		assert.match(error.message, new RegExp(`editor/commands\\.md:${line}:16: :value\\{key="commands\\.cuont"\\}`));
		assert.match(error.message, new RegExp(`editor/commands\\.md:${line}:${lines[line - 1].indexOf(':value{key="hosts') + 1}: :value\\{key="hosts\\.count"\\}`));
	} finally {
		book.remove();
	}
});

test('a mark needs its key, takes no text in brackets and no other attribute', async () => {
	await fails('## A\n\nThere are :value{key=""} commands.', undefined, /:value needs the key of the value it shows: :value\{key="commands\.count"\}/);
	await fails('## A\n\nThere are :value[151]{key="commands.count"} commands.', undefined, /:value\[151\] takes no text in brackets/);
	const error = await fails('## A\n\nThere are :value{name="commands.count"} commands.', undefined, /:value has no attribute "name" \(it takes key\)/);
	// The table's problem is the only one: the plugin does not add "needs the key" to it.
	assert.doesNotMatch(error.message, /needs the key/);
});

test('a heading holds no value, because its anchor would change with the engine', async () => {
	await fails('## The :value{key="commands.count"} commands\n\nText.', undefined, /a heading holds no :value: its anchor would change with the engine/);
});

test('a missing or broken values.json fails every mark, and a page without marks does not need it', async () => {
	await fails('## A\n\nThere are :value{key="commands.count"} commands.', {}, /:value\{key="commands\.count"\}: src\/generated\/reference\/values\.json does not exist; tools\/reference\.py render writes it from the engine at the pin/);
	await fails('## A\n\nThere are :value{key="commands.count"} commands.', { 'src/generated/reference/values.json': '{"commands.count": ' }, /src\/generated\/reference\/values\.json is not valid JSON: .*; write it again with python -I tools\/reference\.py render/);
	await fails('## A\n\nThere are :value{key="commands.count"} commands.', { 'src/generated/reference/values.json': '{"commands.count": [151]}' }, /the value of "commands\.count" is \[151\]; every value is a number or a string/);
	// A file rendered at another pin, or naming none, is as stale as a generated table with another stamp.
	await fails('## A\n\nThere are :value{key="commands.count"} commands.', { 'src/generated/reference/values.json': JSON.stringify({ 'commands.count': 151, 'engine.commit': 'a'.repeat(40) }) }, /:value\{key="commands\.count"\}: src\/generated\/reference\/values\.json was rendered from engine a{40}, but engine\.pin names 822a7a46dbcdd86e8e2eafde7e41d003e27260c8; write it again with python -I tools\/reference\.py render/);
	await fails('## A\n\nThere are :value{key="commands.count"} commands.', { 'src/generated/reference/values.json': '{"commands.count": 151}' }, /values\.json names no "engine\.commit"/);
	assert.match(await html('## A\n\nThere are many commands.', {}), /There are many commands\./);
});

test('loadValues reads a flat map of numbers and strings, and refuses anything else', () => {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'book-values-'));
	try {
		const file = path.join(folder, 'values.json');
		assert.deepEqual(loadValues(file), { missing: true });
		const read = (text, pin) => {
			writeFileSync(file, text);
			return loadValues(file, pin);
		};
		assert.deepEqual([...read(c_Values).values], [['commands.count', 151], ['components.count', 38], ['engine.commit', c_Commit], ['quality.shadowScale.Medium', 0.6], ['importer.texture.version', '7']]);
		// With the pin, the file must name the engine commit it was rendered from (it has no stamp line).
		assert.equal(read(c_Values, c_Commit).values.get('commands.count'), 151);
		assert.match(read(c_Values, 'f'.repeat(40)).error, /values\.json was rendered from engine 822a7a46dbcdd86e8e2eafde7e41d003e27260c8, but engine\.pin names f{40}/);
		assert.match(read('{"commands.count": 151}', c_Commit).error, /values\.json names no "engine\.commit", the engine commit its values come from/);
		assert.match(read('[1, 2]').error, /is not a JSON object of keys and values/);
		assert.match(read('null').error, /is not a JSON object of keys and values/);
		assert.match(read('{"": 1}').error, /has an empty key/);
		assert.match(read('{"a.b": true}').error, /the value of "a\.b" is true/);
		assert.match(read('{"a.b": {"c": 1}}').error, /the value of "a\.b" is \{"c":1\}/);
		assert.match(read('{"a.b": null}').error, /the value of "a\.b" is null/);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
	assert.equal(valueText(151), '151');
	assert.equal(valueText(0.6), '0.6');
	assert.equal(valueText('1.4.352'), '1.4.352');
	const values = new Map([['commands.count', 1], ['commands.groups', 2], ['components.count', 3]]);
	assert.deepEqual(nearKeys(values, 'commands.cuont'), ['commands.count', 'commands.groups']);
	assert.deepEqual(nearKeys(values, 'hosts.count'), []);
});

test('a values.json the build read is part of the inputs digest, so a new value renders every page again', async () => {
	const { createBookContext, inputsDigest } = await import('../index.mjs');
	const { readSettings } = await import('../../lib/settings.mjs');
	const book = makeBook({ pages: { 'editor/commands': `${frontmatter()}\nText.\n${c_BottomStrip}` }, files: { 'src/generated/reference/values.json': c_Values } });
	try {
		const settings = readSettings({ root: book.root, env: { DOCS_BASE: '/book' } });
		const index = await createBookContext(settings).index();
		const before = inputsDigest(settings, index);
		assert.equal(inputsDigest(settings, index), before);
		writeFileSync(settings.valuesFile, JSON.stringify({ 'commands.count': 152 }));
		assert.notEqual(inputsDigest(settings, index), before);
	} finally {
		book.remove();
	}
});

// The file tools/reference.py render committed: a change of render the build does not accept (another stamp key, a
// value that is neither a number nor a string) fails here before it fails a build.
test('the committed values.json names the clone\'s pin, and every value is one a mark can show', async () => {
	const repository = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
	const pinText = readFileSync(path.join(repository, 'engine.pin'), 'utf8');
	const valuesText = readFileSync(path.join(repository, 'src', 'generated', 'reference', 'values.json'), 'utf8');
	const record = loadValues(path.join(repository, 'src', 'generated', 'reference', 'values.json'), parsePin(pinText).commit);
	assert.equal(record.error, undefined);
	assert.ok(record.values?.size > 1, 'values.json holds values besides engine.commit');
	const values = await html(':value{key="commands.count"} commands.', { 'engine.pin': pinText, 'src/generated/reference/values.json': valuesText });
	assert.match(values, new RegExp(`<span class="book-value">${record.values.get('commands.count')}</span> commands\\.`));
});

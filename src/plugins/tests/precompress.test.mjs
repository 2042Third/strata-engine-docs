// scripts/precompress.mjs: a .gz beside every text file of 1 KB or more of the built site, the same bytes on every
// machine, nothing for Pagefind's own files, and no .br (plan/site.md, "What a release holds"; rulings 6, R23).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { gzipOf, main, precompress, wantsGzip } from '../../../scripts/precompress.mjs';

function site(files) {
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'precompress-'));
	for (const [relative, content] of Object.entries(files)) {
		const file = path.join(folder, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	}
	return folder;
}

const c_Big = 'x'.repeat(2048);

test('which files get a .gz: text files of the listed kinds from 1 KB on', () => {
	for (const name of ['a.html', 'a.css', 'a.js', 'a.mjs', 'a.json', 'a.svg', 'a.xml', 'a.txt', 'manifest.webmanifest', 'A.HTML']) assert.equal(wantsGzip(name, 1024), true, name);
	assert.equal(wantsGzip('a.html', 1023), false);
	for (const name of ['pagefind.en_1.pf_meta', 'index/en_1.pf_index', 'wasm.en.pagefind', 'a.avif', 'a.webp', 'a.woff2', 'a.zip', 'a.patch']) assert.equal(wantsGzip(name, 1 << 20), false, name);
});

test('a .gz holds its file, and its bytes depend on nothing but the file', () => {
	const data = Buffer.from(c_Big);
	const packed = gzipOf(data);
	assert.deepEqual(gunzipSync(packed), data);
	assert.deepEqual([...packed.subarray(4, 8)], [0, 0, 0, 0], 'no time stamp');
	assert.equal(packed[3] & 0x08, 0, 'no file name');
	assert.equal(packed[9], 255, 'the system is "unknown"');
	assert.deepEqual(gzipOf(data), packed);
});

test('the site gets its .gz files; Pagefind\'s own files and small files get none; a second run changes nothing', () => {
	const folder = site({
		'index.html': c_Big, 'core/time/index.html': c_Big, '_astro/page.js': c_Big, '_astro/small.css': 'a{}',
		'pagefind/pagefind.js': c_Big, 'pagefind/pagefind-entry.json': c_Big, 'pagefind/index/en_1.pf_index': c_Big,
		'pagefind/wasm.en.pagefind': c_Big, '_figures/a.0123456789.960.avif': c_Big, 'license.txt': c_Big,
		'_astro/was-big.css': 'b{}', '_astro/was-big.css.gz': 'stale',
	});
	try {
		const first = precompress(folder);
		assert.deepEqual(first.problems, []);
		assert.deepEqual(first.written, ['_astro/page.js.gz', 'core/time/index.html.gz', 'index.html.gz', 'license.txt.gz', 'pagefind/pagefind-entry.json.gz', 'pagefind/pagefind.js.gz']);
		assert.deepEqual(first.removed, ['_astro/was-big.css.gz']);
		assert.equal(existsSync(path.join(folder, '_astro', 'small.css.gz')), false);
		assert.equal(existsSync(path.join(folder, 'pagefind', 'wasm.en.pagefind.gz')), false);
		assert.equal(gunzipSync(readFileSync(path.join(folder, 'index.html.gz'))).toString(), c_Big);
		const second = precompress(folder);
		assert.deepEqual(second.written, []);
		assert.equal(second.kept.length, 6);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

test('a .br, or a .gz beside no file of its name, is refused and nothing is written', () => {
	const folder = site({ 'index.html': c_Big, 'index.html.br': 'b', 'gone.css.gz': 'g' });
	try {
		const result = precompress(folder);
		assert.match(result.problems.join('\n'), /index\.html\.br: the release holds no \.br file/);
		assert.match(result.problems.join('\n'), /gone\.css\.gz: a \.gz beside no file of its name/);
		assert.equal(existsSync(path.join(folder, 'index.html.gz')), false);
		const errors = [];
		const original = console.error;
		console.error = (line) => errors.push(line);
		try {
			assert.equal(main(['--dist', folder]), 1);
			assert.equal(main(['--dist', path.join(folder, 'missing')]), 2);
			assert.equal(main(['--other']), 2);
		} finally {
			console.error = original;
		}
		assert.match(errors.join('\n'), /has no index\.html/);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
});

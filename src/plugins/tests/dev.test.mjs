// The dev server (budget row 6). The configureServer of its plugin (src/integrations/book.mjs) adds the pictures'
// middleware and returns nothing, since Vite calls a function it returns after its own middlewares, with no request
// (connect's use() returns the app, a function, which then failed on every request with "Cannot read properties of
// undefined (reading 'url')"). And the folders it leaves unwatched (src/lib/watch.mjs).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { devFiguresPlugin } from '../../integrations/book.mjs';
import { readSettings } from '../../lib/settings.mjs';
import { c_UnwatchedFolders, watchIgnored } from '../../lib/watch.mjs';
import { createBookContext } from '../index.mjs';
import { c_BottomStrip, frontmatter, makeBook } from './helpers.mjs';

test('the dev plugin adds one middleware and returns nothing to Vite', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\nText.\n${c_BottomStrip}` } });
	try {
		const context = createBookContext(readSettings({ root: book.root, env: { DOCS_BASE: '/book', DOCS_SITE: 'https://example.com' } }));
		const plugin = devFiguresPlugin(context);
		const used = [];
		const app = () => {
			throw new Error('Vite called the app with no request');
		};
		const server = { middlewares: { use: (handler) => (used.push(handler), app) } };
		assert.equal(plugin.configureServer(server), undefined);
		assert.equal(used.length, 1);
		// A request that is no picture goes on to Astro's own middlewares.
		let passed = false;
		await used[0]({ url: '/book/core/time/' }, {}, () => (passed = true));
		assert.ok(passed);
	} finally {
		book.remove();
	}
});

test('the dev server leaves the ignored folders of tools and output unwatched, below its own root only', () => {
	const root = path.resolve('book-root');
	const ignored = watchIgnored(root);
	for (const name of c_UnwatchedFolders) {
		assert.ok(ignored(path.join(root, name)), name);
		assert.ok(ignored(path.join(root, name, 'a', 'b.txt')), `${name}/a/b.txt`);
	}
	for (const file of ['src/content/docs/core/time.md', 'src/generated/outline.json', 'astro.config.mjs', 'distant/a.md', '.toolsy/a', 'src/dist/a.md']) assert.equal(ignored(path.join(root, file)), false, file);
	// The scale test's book lies inside the project's .tools/: its own sources are watched, its output is not.
	const scale = path.join(root, '.tools', 'scale', 'site');
	const own = watchIgnored(scale);
	assert.equal(own(path.join(scale, 'src', 'content', 'docs', 'core', 'time.md')), false);
	assert.ok(own(path.join(scale, 'dist', 'index.html')));
	assert.ok(own(path.join(scale, '.cache', 'astro', 'a')));
});

test('astro.config.mjs gives Vite the unwatched folders of its own root', () => {
	const config = readFileSync(fileURLToPath(new URL('../../../astro.config.mjs', import.meta.url)), 'utf8');
	assert.match(config, /import \{ watchIgnored \} from '\.\/src\/lib\/watch\.mjs';/);
	assert.match(config, /server: \{ watch: \{ ignored: watchIgnored\(root\) \} \}/);
});

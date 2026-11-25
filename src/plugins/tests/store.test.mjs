// The content store: Astro keeps every page's rendered HTML in one store, which a build of the whole book makes about
// 136 MB. Kept in one file, the build inlines it into a single module, JSON.parse("…") of the whole store, and V8 aborts
// while compiling it ("FATAL ERROR: Zone Allocation failed" at "Building static entrypoints"); split into chunks, each
// part is a module of its own, loaded when a page asks for it.

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));

test('astro.config.mjs keeps the content store in chunks', () => {
	const config = readFileSync(`${c_Root}astro.config.mjs`, 'utf8').replace(/^\s*\/\/.*$/gm, '');
	assert.match(config, /experimental:\s*\{\s*collectionStorage:\s*'chunked'\s*\}/);
});

test('the installed Astro splits a chunked store into modules of their own', () => {
	// The option is experimental: a version of Astro that drops it would bring the single module, and the abort, back.
	const paths = readFileSync(`${c_Root}node_modules/astro/dist/content/paths.js`, 'utf8');
	assert.match(paths, /experimental\.collectionStorage/);
	assert.match(paths, /storage === "chunked"/);
	const plugin = readFileSync(`${c_Root}node_modules/astro/dist/content/vite-plugin-content-virtual-mod.js`, 'utf8');
	assert.match(plugin, /getDataStoreChunkSize\(settings\) !== undefined/);
});

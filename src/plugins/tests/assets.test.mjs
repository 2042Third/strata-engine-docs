// src/lib/assets.mjs: Vite inlines no font as a data: URL, which the release's policy (font-src 'self') would block
// (rulings 6, R23); other files keep Vite's own rule.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { assetsInlineLimit, katexWoff2Only, woff2Only } from '../../lib/assets.mjs';

test('no font is inlined; every other file is left to Vite', () => {
	for (const file of ['/a/KaTeX_Size1-Regular.woff2', 'b/jetbrains-mono-latin.woff', 'c/x.TTF', 'd/x.otf', 'e/x.eot', '/f/x.woff2?url']) assert.equal(assetsInlineLimit(file), false, file);
	for (const file of ['/a/icon.svg', 'b/x.png', 'c/x.css', 'd/woff2.js']) assert.equal(assetsInlineLimit(file), undefined, file);
});

test('astro.config.mjs gives Vite that limit', () => {
	const config = readFileSync(fileURLToPath(new URL('../../../astro.config.mjs', import.meta.url)), 'utf8');
	assert.match(config, /import \{ assetsInlineLimit, katexWoff2Only \} from '\.\/src\/lib\/assets\.mjs';/);
	assert.match(config, /plugins: \[katexWoff2Only\(\)\]/);
	assert.match(config, /vite: \{ build: \{ assetsInlineLimit \}[ ,]/);
});

test('KaTeX\'s fonts are served as WOFF2 only, and a sheet of another form fails the build', async () => {
	const { createRequire } = await import('node:module');
	const sheet = createRequire(import.meta.url).resolve('katex/dist/katex.min.css');
	const css = readFileSync(sheet, 'utf8');
	const result = woff2Only(css);
	assert.equal((result.match(/@font-face/g) ?? []).length, (css.match(/@font-face/g) ?? []).length);
	assert.equal((result.match(/\.woff2\) format\("woff2"\)/g) ?? []).length, (css.match(/@font-face/g) ?? []).length);
	assert.doesNotMatch(result, /\.woff\)|\.ttf\)/);
	assert.throws(() => woff2Only('@font-face{src:url(a.otf) format("opentype")}'), /not "woff2, woff, truetype"/);
	const plugin = katexWoff2Only();
	assert.equal(plugin.transform(css, sheet.replace(/\\/g, '/')).code, result);
	assert.equal(plugin.transform(css, sheet.replace(/\//g, '\\')).code, result);
	assert.equal(plugin.transform(css, `${sheet}?direct`).code, result);
	assert.equal(plugin.transform('a{}', '/x/book.css'), null);
});

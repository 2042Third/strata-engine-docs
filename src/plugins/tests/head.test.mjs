// The head of every page (src/components/Head.astro): Starlight's head with the first screen's two fonts preloaded,
// so that a fast first paint does not draw the fallback font and move the text when the font swaps in (budget row 14's
// layout shift).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));
const c_Head = readFileSync(path.join(c_Root, 'src', 'components', 'Head.astro'), 'utf8');

test('astro.config.mjs puts the book\'s head in place of Starlight\'s', () => {
	const config = readFileSync(path.join(c_Root, 'astro.config.mjs'), 'utf8');
	assert.match(config, /\bHead: '\.\/src\/components\/Head\.astro'/);
});

test('the head keeps Starlight\'s and preloads the Latin files that the fonts\' style sheets name, as fonts, crossorigin', () => {
	assert.match(c_Head, /import Default from '@astrojs\/starlight\/components\/Head\.astro';/);
	assert.match(c_Head, /\n<Default \/>\n/);
	const fonts = [
		['@fontsource-variable/inter', 'inter-latin-wght-normal.woff2', 'interLatin'],
		['@fontsource-variable/source-serif-4', 'source-serif-4-latin-wght-normal.woff2', 'serifLatin'],
	];
	for (const [module, file, name] of fonts) {
		assert.ok(c_Head.includes(`import ${name} from '${module}/files/${file}?url';`), `${name} imports ${file}`);
		assert.ok(c_Head.includes(`<link rel="preload" href={${name}} as="font" type="font/woff2" crossorigin />`), `${name} is preloaded`);
		const folder = path.join(c_Root, 'node_modules', ...module.split('/'));
		assert.ok(existsSync(path.join(folder, 'files', file)), `${module} has ${file}`);
		// The file is the one the font's own style sheet (astro.config.mjs's customCss) uses for Latin text.
		assert.match(readFileSync(path.join(folder, 'index.css'), 'utf8'), new RegExp(`url\\(\\./files/${file.replace(/\./g, '\\.')}\\)`));
	}
	// Only the two first-screen fonts: the code font and the italics wait until a text uses them.
	assert.equal(c_Head.match(/<link rel="preload"/g).length, 2);
});

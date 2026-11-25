// Every URL the plugins write is under the base, at the root of a host, at the default prefix and at a deeper one
// (plan/site.md, "The base path", rule 2): links between pages, pictures (a lossy one with its derived AVIF in its
// srcset, a crop) and the links to their full size, glossary links, the glossary's list. A URL of the site that leaves
// the base, or names another base, fails.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';
import { bottomStrip, c_BottomStrip, c_ReferenceStrip, frontmatter, makeBook, render } from './helpers.mjs';

const c_Bases = [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/a/b/', '/a/b']];
const glossary = { terms: [{ id: 'fixed-step', term: 'fixed step', definition: 'A slice of simulated time of one length.', home: 'core/time' }] };
const recipe = { id: 'shot', shows: 'A cube on the ground.', kind: 'scene', caption: 'Notice the cube.', alt: 'A grey cube.', size: [1920, 1080], crops: [{ name: 'detail', rect: [0.25, 0.25, 0.375, 0.375], scale: 2 }] };

/** Every URL of an attribute that names one (href, src, each srcset candidate). */
function urls(html) {
	const found = [];
	for (const match of html.matchAll(/\s(href|src|srcset)="([^"]*)"/g)) {
		if (match[1] === 'srcset') found.push(...match[2].split(',').map((candidate) => candidate.trim().split(/\s+/)[0]).filter(Boolean));
		else found.push(match[2]);
	}
	return found;
}

for (const [setting, base] of c_Bases) {
	test(`every URL the plugins write is under the base ${setting}`, async () => {
		const page = `${frontmatter()}\nEach :term[fixed step]{id=fixed-step} is one step. See [the loop](../world/ecs.md#the-loop) and [here](#a-section).\n\n## A section\n\n::figure{id=shot}\n\n::figure{id=shot crop=detail}\n${c_BottomStrip}`;
		const book = makeBook({
			glossary,
			pages: {
				'core/probe': page,
				'world/ecs': `${frontmatter()}\n## The loop\n${c_BottomStrip}`,
				'core/time': `${frontmatter()}\nThe **fixed step** is defined here.\n${c_BottomStrip}`,
				'start/how-to-read': `${frontmatter({ kind: 'how-to', tracks: '[G, B, E]', since: undefined })}\n::track-chooser\n${bottomStrip('how-to')}`,
				'reference/glossary': `${frontmatter({ kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\n::glossary\n${c_ReferenceStrip}`,
			},
			files: { 'src/content/figures/core/probe.json': JSON.stringify({ figures: [recipe] }) },
		});
		try {
			const folder = path.join(book.root, 'src', 'assets', 'figures', 'core', 'probe');
			mkdirSync(folder, { recursive: true });
			await sharp({ create: { width: 1920, height: 1080, channels: 3, background: { r: 90, g: 120, b: 160 } } }).avif({ quality: 80, effort: 0 }).toFile(path.join(folder, 'shot.avif'));
			await sharp({ create: { width: 240, height: 135, channels: 3, background: { r: 90, g: 120, b: 160 } } }).webp({ lossless: true }).toFile(path.join(folder, 'shot-detail.webp'));
			const env = { DOCS_BASE: setting };
			const outputs = [await render(book.root, 'core/probe', { env }), await render(book.root, 'reference/glossary', { env }), await render(book.root, 'start/how-to-read', { env })];
			const site = outputs.flatMap(urls).filter((url) => !/^(https?:)?\/\//.test(url));
			assert.ok(site.length >= 11, site.join(' '));
			for (const url of site) {
				if (url.startsWith('#')) continue;
				assert.ok(url.startsWith(`${base}/`), `${url} is not under ${base}/`);
				if (base !== '/strata-engine-docs') assert.ok(!url.startsWith('/strata-engine-docs/'), `${url} names the default prefix`);
			}
			const html = outputs.join('\n');
			assert.match(html, new RegExp(`href="${base}/world/ecs/#the-loop"`));
			assert.match(html, new RegExp(`href="${base}/reference/glossary/#fixed-step"`));
			assert.match(html, new RegExp(`<a class="book-figure__zoom" href="${base}/_figures/core/probe/shot\\.[0-9a-f]{10}\\.1920\\.avif"><img src="${base}/_figures/core/probe/shot\\.[0-9a-f]{10}\\.1920\\.avif"`));
			assert.match(html, new RegExp(`srcset="${base}/_figures/core/probe/shot\\.[0-9a-f]{10}\\.960\\.avif 960w, ${base}/_figures/core/probe/shot\\.[0-9a-f]{10}\\.1920\\.avif 1920w"`));
			assert.match(html, new RegExp(`href="${base}/_figures/core/probe/shot-detail\\.[0-9a-f]{10}\\.240\\.webp"><img src="${base}/_figures/core/probe/shot-detail\\.[0-9a-f]{10}\\.240\\.webp"`));
			assert.match(html, new RegExp(`href="${base}/core/time/"`));
			// The track chooser links the first written page of each track.
			assert.match(html, new RegExp(`<a href="${base}/start/how-to-read/" class="book-track__start">`));
		} finally {
			book.remove();
		}
	});
}

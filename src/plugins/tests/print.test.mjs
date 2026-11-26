// The print views (src/lib/print.mjs): every chapter's ids are its own and every reference follows them; what a page
// hides is shown; the views stay out of search and of the sitemap (src/lib/sitemap.mjs).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { anchorOf, prefixChapter, printFrontmatter } from '../../lib/print.mjs';
import { sitemapFilter } from '../../lib/sitemap.mjs';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));

const ids = (html) => [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);

test('footnotes, headings and figures of two chapters share no id in the print view', () => {
	const chapter = (word) => `<h2 id="summary">Summary</h2><p>${word}<sup><a href="#user-content-fn-1" id="user-content-fnref-1" aria-describedby="footnote-label">1</a></sup></p>`
		+ '<section data-footnotes class="footnotes"><h2 id="footnote-label" class="sr-only">Footnotes</h2><ol><li id="user-content-fn-1"><p>Note <a href="#user-content-fnref-1">↩</a></p></li></ol></section>';
	const pages = new Set(['core/time', 'core/probe']);
	const first = prefixChapter(chapter('One'), 'core/time', pages, '/book');
	const second = prefixChapter(chapter('Two'), 'core/probe', pages, '/book');
	const all = [...ids(first), ...ids(second)];
	assert.equal(new Set(all).size, all.length, all.join(' '));
	assert.match(first, /<a href="#core--time--user-content-fn-1" id="core--time--user-content-fnref-1" aria-describedby="core--time--footnote-label">/);
	assert.match(second, /<li id="core--probe--user-content-fn-1"><p>Note <a href="#core--probe--user-content-fnref-1">/);
});

test('anchors written percent-encoded and links to the part\'s pages find their ids', () => {
	const html = '<h2 id="über-die-zeit">Über die Zeit</h2><a href="#%C3%BCber-die-zeit">here</a>'
		+ '<a href="/book/core/probe/#the-loop">there</a><a href="/book/core/probe/">the page</a><a href="/book/world/ecs/#x">elsewhere</a>';
	const out = prefixChapter(html, 'core/time', new Set(['core/time', 'core/probe']), '/book');
	assert.match(out, /<h2 id="core--time--über-die-zeit">/);
	assert.match(out, /<a href="#core--time--%C3%BCber-die-zeit">here<\/a>/);
	assert.match(out, /<a href="#core--probe--the-loop">there<\/a>/);
	assert.match(out, /<a href="#core--probe">the page<\/a>/);
	assert.match(out, /<a href="\/book\/world\/ecs\/#x">elsewhere<\/a>/);
	assert.equal(anchorOf('core/time'), 'core--time');
});

test('a diagram\'s ids get the chapter\'s name in front everywhere its SVG names them, so two chapters may show one diagram', () => {
	const prefix = 'dg-0123456789abcdef-light';
	const html = `<div><svg id="${prefix}" aria-labelledby="${prefix}-title"><title id="${prefix}-title">A</title><style>#${prefix} .a{}</style><marker id="${prefix}-arrowhead"></marker><line marker-end="url(#${prefix}-arrowhead)"></line><use href="#${prefix}-arrowhead"></use></svg></div>`;
	const time = prefixChapter(html, 'core/time', new Set(['core/time', 'core/loop']), '');
	const loop = prefixChapter(html, 'core/loop', new Set(['core/time', 'core/loop']), '');
	assert.match(time, new RegExp(`<svg id="core--time--${prefix}" aria-labelledby="core--time--${prefix}-title">`));
	assert.match(time, new RegExp(`<style>#core--time--${prefix} \\.a\\{\\}</style>`));
	assert.match(time, new RegExp(`url\\(#core--time--${prefix}-arrowhead\\)`));
	assert.match(time, new RegExp(`href="#core--time--${prefix}-arrowhead"`));
	assert.doesNotMatch(time, /core--time--core--time--/);
	const ids = (out) => [...out.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
	assert.equal(ids(time).filter((id) => ids(loop).includes(id)).length, 0);
});

test('a print view shows what a page hides: every <details> is open and every picture loads at once', () => {
	const html = '<details class="book-answer"><summary>Answer</summary><p>Yes.</p></details><details open><summary>Schema</summary></details>'
		+ '<figure><picture><source type="image/avif" srcset="/book/_figures/a.avif"><img src="/book/_figures/a.webp" loading="lazy" decoding="async" alt="A cube."></picture></figure>'
		+ '<template><details><summary>Inside a template</summary></details></template>';
	const out = prefixChapter(html, 'core/time', new Set(['core/time']), '/book');
	assert.equal(out.match(/<details[^>]*>/g).length, 3);
	for (const tag of out.match(/<details[^>]*>/g)) assert.match(tag, /\sopen(\s|>|=)/, tag);
	assert.match(out, /<img src="\/book\/_figures\/a\.webp" loading="eager" decoding="async" alt="A cube\.">/);
	assert.doesNotMatch(out, /loading="lazy"/);
});

test('a print view loads each external script once, where its first chapter names it, and keeps inline scripts', () => {
	const chapter = (word) => `<p>${word}</p><script type="module" src="/book/_astro/ec.abc.js"></script><script>window.seen = true;</script>`;
	const scripts = new Set();
	const first = prefixChapter(chapter('One') + '<div><script type="module" src="/book/_astro/ec.abc.js"></script></div>', 'core/time', new Set(['core/time']), '/book', scripts);
	const second = prefixChapter(`<section>${chapter('Two')}</section><script type="module" src="/book/_astro/other.js"></script>`, 'core/probe', new Set(['core/probe']), '/book', scripts);
	assert.equal(first.match(/src="\/book\/_astro\/ec\.abc\.js"/g).length, 1);
	assert.doesNotMatch(second, /ec\.abc\.js/);
	assert.match(second, /<section><p>Two<\/p><script>window\.seen = true;<\/script><\/section><script type="module" src="\/book\/_astro\/other\.js"><\/script>/);
	assert.equal(first.match(/<script>window\.seen = true;<\/script>/g).length, 1);
	assert.deepEqual([...scripts], ['/book/_astro/ec.abc.js', '/book/_astro/other.js']);
	// Without a set of its own, a chapter keeps the first of its scripts.
	assert.equal(prefixChapter(chapter('Alone'), 'core/time', new Set(['core/time']), '/book').match(/ec\.abc\.js/g).length, 1);
});

test('a print view is left out of the book\'s search and asks search engines not to index it', () => {
	const frontmatter = printFrontmatter('Engine architecture');
	assert.equal(frontmatter.pagefind, false);
	assert.deepEqual(frontmatter.head, [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } }]);
	assert.equal(frontmatter.title, 'Engine architecture: the whole part');
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`the sitemap lists the pages and leaves out the print views and the 404 page, under the base ${setting}`, () => {
		const keep = sitemapFilter({ site: 'https://example.com', base });
		const url = (rest) => `https://example.com${base}/${rest}`;
		for (const page of ['', 'core/time/', 'core/', 'reference/glossary/', 'printing/press/']) assert.equal(keep(url(page)), true, url(page));
		for (const page of ['print/core/', 'print/reference/', '404/']) assert.equal(keep(url(page)), false, url(page));
	});
}

test('astro.config.mjs adds the book\'s own sitemap with its filter, so Starlight adds none', () => {
	const config = readFileSync(path.join(c_Root, 'astro.config.mjs'), 'utf8');
	assert.match(config, /^import sitemap from '@astrojs\/sitemap';$/m);
	assert.match(config, /^\t\tsitemap\(\{ filter: sitemapFilter\(settings\) \}\),$/m);
	const manifest = JSON.parse(readFileSync(path.join(c_Root, 'package.json'), 'utf8'));
	assert.equal(manifest.dependencies['@astrojs/sitemap'], '3.7.4');
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`a print view under the base ${setting} links its own chapters within the page and the rest under the base`, () => {
		const html = `<a href="${base}/core/probe/#the-loop">loop</a><a href="${base}/core/">part</a><a href="${base}/world/ecs/">elsewhere</a><img src="${base}/_figures/a.webp" loading="lazy">`;
		const out = prefixChapter(html, 'core/time', new Set(['core/time', 'core/probe', 'core']), base);
		assert.match(out, /<a href="#core--probe--the-loop">loop<\/a>/);
		assert.match(out, /<a href="#core">part<\/a>/);
		assert.match(out, new RegExp(`<a href="${base}/world/ecs/">elsewhere</a>`));
		assert.match(out, new RegExp(`<img src="${base}/_figures/a\\.webp" loading="eager">`));
	});
}

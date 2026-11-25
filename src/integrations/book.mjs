// The book's Astro integration: the checks that look at the whole book at once (the sidebar against the outline and the
// pages, rules O5, O8 and O9; the glossary's home pages; the moved pages), the published pictures copied into the built
// site with the AVIFs derived from the lossy ones, the same files served by the dev server, the fallback pages of the
// moved pages, and LICENSE served as <base>/license.txt (rulings 6, R20). Diagrams are not drawn here: the build reads the committed drawings of src/generated/diagrams/ (npm
// run diagrams draws them; src/plugins/mermaid.mjs).

import { copyFileSync, createReadStream, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { isFile, loadManifest, loadTaken, promisedPictures } from '../lib/figures.mjs';
import { bytesOf, c_Types, describePicture, ensureEncoded, publishServed, servedAs, servedFiles } from '../lib/images.mjs';
import { fallbackFile, fallbackPage, loadRedirects, redirectProblems } from '../lib/redirects.mjs';
import { searchIndexEnvironment } from '../lib/search.mjs';
import { licenseProblem, withBase } from '../lib/settings.mjs';
import { checkSidebarOutline, checkSidebarPages } from '../lib/sidebar.mjs';
import { rehypeBookAnchorIcons, rehypeBookSearch } from '../plugins/rehype.mjs';

function listManifests(folder, relative = '') {
	let entries;
	try {
		entries = readdirSync(path.join(folder, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	return entries.flatMap((entry) => {
		const child = path.join(relative, entry.name);
		if (entry.isDirectory()) return listManifests(folder, child);
		return entry.name.endsWith('.json') ? [child.replace(/\.json$/, '').split(path.sep).join('/')] : [];
	});
}

/**
 * Every file the site serves for the published pictures: `{ kind, format, width, url, output, source, cache }` (the
 * published file of each picture and crop its recipe promises, and the AVIFs derived from the lossy ones). Drawings are
 * inlined into their pages, and a picture that is not published yet has nothing to serve. Pictures with the same bytes
 * share one served file (servedAs), listed once.
 */
export async function planPictures(settings, outputDir) {
	const files = [];
	const urls = new Set();
	for (const pageId of listManifests(settings.figuresDir)) {
		const manifest = loadManifest(settings.figuresDir, pageId);
		const taken = loadTaken(settings.picturesDir, pageId);
		for (const entry of manifest?.figures.values() ?? []) {
			for (const promised of promisedPictures(entry, taken)) {
				if (promised.name.endsWith('.svg')) continue;
				const published = path.join(settings.picturesDir, ...pageId.split('/'), promised.name);
				if (!isFile(published)) continue;
				const description = await describePicture(published);
				// A file of another format than its name says is reported by the page that shows it; it is not served.
				if (description.format !== path.extname(promised.name).slice(1)) continue;
				const relative = path.relative(settings.picturesDir, published).split(path.sep).join('/');
				const name = await servedAs(settings.picturesDir, relative, description);
				for (const served of servedFiles({ base: settings.base, cacheDir: settings.cacheDir, outputDir }, description, name)) {
					if (urls.has(served.url)) continue;
					urls.add(served.url);
					files.push(served);
				}
			}
		}
	}
	return files;
}

/**
 * O8 in a release build: every part of eight or more rows has its index and review page. A draft build has parts
 * whose edit pass has not run yet; the strips plugin checks the part pages that exist.
 */
export function partPagesProblems(outline, pages) {
	const problems = [];
	for (const part of outline.parts) {
		if (!part.partPages) continue;
		for (const name of ['index', 'review']) {
			if (!pages.has(`${part.slug}/${name}`)) problems.push(`O8: the part "${part.slug}" has ${part.pages.length} rows, so a release has src/content/docs/${part.slug}/${name}.md`);
		}
	}
	return problems;
}

/**
 * The .mdx files under a folder, relative to it. The book is plain Markdown (site.md, "The Markdown the build reads"):
 * without Astro's MDX integration the content loader would leave such a file out without a word.
 */
export function mdxFiles(folder, relative = '') {
	let entries;
	try {
		entries = readdirSync(path.join(folder, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	return entries.flatMap((entry) => {
		const child = path.join(relative, entry.name);
		if (entry.isDirectory()) return mdxFiles(folder, child);
		return entry.name.toLowerCase().endsWith('.mdx') ? [child.split(path.sep).join('/')] : [];
	});
}

/**
 * The moved pages of this build: src/redirects.json's entries, and in a test build those of DOCS_EXTRA_REDIRECTS.
 * Returns `{ entries, problems }`.
 */
export function bookRedirects(settings) {
	const own = loadRedirects(settings.redirectsFile, 'src/redirects.json');
	if (!settings.extraRedirectsFile) return own;
	if (!existsSync(settings.extraRedirectsFile)) return { entries: own.entries, problems: [...own.problems, `DOCS_EXTRA_REDIRECTS names ${settings.extraRedirectsFile}, which does not exist`] };
	const extra = loadRedirects(settings.extraRedirectsFile, path.relative(settings.root, settings.extraRedirectsFile).split(path.sep).join('/'));
	return { entries: [...own.entries, ...extra.entries], problems: [...own.problems, ...extra.problems] };
}

/** Writes the fallback page of every moved page into the built site; returns how many. */
export function writeFallbackPages(settings, pages, outputDir) {
	const { entries } = bookRedirects(settings);
	for (const entry of entries) {
		const file = path.join(outputDir, ...fallbackFile(entry).split('/'));
		// The checks refuse an old id that is a page; a file there now came from somewhere else and is not replaced.
		if (existsSync(file)) throw new Error(`${entry.label}: the build already holds ${fallbackFile(entry)}, so the fallback page of "${entry.from}" cannot be written`);
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, fallbackPage({ base: settings.base, site: settings.site, entry, title: pages.get(entry.to).title, copyright: settings.siteFile.copyright }));
	}
	return entries.length;
}

/** LICENSE's text, or null when the repository has none. */
export function readLicense(root) {
	try {
		return readFileSync(path.join(root, 'LICENSE'), 'utf8');
	} catch (error) {
		if (error.code === 'ENOENT') return null;
		throw error;
	}
}

/** Problems that only the whole book shows. */
export async function bookProblems(context) {
	const index = await context.index();
	const license = licenseProblem(readLicense(context.settings.root), context.settings.siteFile.copyright);
	const problems = [...(license ? [license] : []), ...checkSidebarOutline(context.sidebar, context.outline), ...checkSidebarPages(context.sidebar, context.outline, index.pages)];
	for (const file of mdxFiles(path.join(context.settings.root, 'src', 'content'))) problems.push(`src/content/${file}: the book's pages are plain Markdown (.md); MDX is not read (site.md, "What MDX would have given")`);
	for (const page of index.pages.values()) {
		if (page.error) problems.push(`${page.relative}: ${page.error}`);
	}
	const redirects = bookRedirects(context.settings);
	problems.push(...redirects.problems, ...redirectProblems(redirects.entries, index.pages));
	for (const slug of context.outline.parts.filter((part) => part.partPages).map((part) => part.slug)) {
		const written = ['index', 'review'].filter((name) => index.pages.has(`${slug}/${name}`));
		if (written.length === 1) problems.push(`O8: the part "${slug}" has src/content/docs/${slug}/${written[0]}.md but not its ${written[0] === 'index' ? 'review' : 'index'} page: the part editor writes both`);
	}
	if (context.settings.release) {
		problems.push(...partPagesProblems(context.outline, index.pages));
		for (const term of context.glossary.terms) {
			if (!term.home) problems.push(`glossary: "${term.term}" has no home page`);
			else if (!index.pages.has(term.home)) problems.push(`glossary: the home page of "${term.term}" (${term.home}) does not exist`);
		}
	}
	return problems;
}

function figuresMiddleware(context) {
	const prefix = withBase(context.settings.base, '/_figures/');
	let plan = null;
	return async (request, response, next) => {
		const url = decodeURIComponent((request.url ?? '').split('?')[0]);
		if (!url.startsWith(prefix)) return next();
		try {
			let served = plan?.get(url);
			if (!served) {
				plan = new Map((await planPictures(context.settings, null)).map((file) => [file.url, file]));
				served = plan.get(url);
			}
			if (!served) return next();
			await ensureEncoded(served);
			response.setHeader('Content-Type', c_Types[served.format]);
			createReadStream(bytesOf(served)).pipe(response);
		} catch (error) {
			next(error);
		}
	};
}

/**
 * The dev server's Vite plugin: it serves the pictures under <base>/_figures/ as the build does. Its configureServer
 * returns nothing: Vite calls a function it returns after its own middlewares, with no request, and connect's use()
 * returns the server's app, which is a function.
 */
export function devFiguresPlugin(context) {
	return {
		name: 'strata-book-figures',
		configureServer(server) {
			server.middlewares.use(figuresMiddleware(context));
		},
	};
}

export function bookIntegration(context) {
	return {
		name: 'strata-book',
		hooks: {
			'astro:config:setup': async ({ config, addWatchFile, updateConfig, command }) => {
				// After Expressive Code's own plugin (Starlight adds it before this integration runs).
				config.markdown.processor.options.rehypePlugins.push(rehypeBookSearch(), rehypeBookAnchorIcons());
				for (const file of [context.settings.glossaryFile, context.settings.outlineFile, context.settings.sidebarFile, context.settings.redirectsFile, path.join(context.settings.root, 'engine.pin')]) addWatchFile(file);
				const problems = await bookProblems(context);
				if (problems.length) throw new Error(`The book has ${problems.length} problem${problems.length === 1 ? '' : 's'}:\n  ${problems.join('\n  ')}`);
				if (command === 'dev') updateConfig({ vite: { plugins: [devFiguresPlugin(context)] } });
				// Starlight runs Pagefind after the build, in a process that inherits this one's environment, and Pagefind
				// 1.6 takes its index's chunk size from the environment only (src/lib/search.mjs).
				if (command === 'build') Object.assign(process.env, searchIndexEnvironment());
			},
			'astro:build:done': async ({ dir, logger }) => {
				const started = performance.now();
				const files = await planPictures(context.settings, fileURLToPath(dir));
				let last = 0;
				const { encoded, total } = await publishServed(files, {
					concurrency: Number(process.env.DOCS_IMAGE_JOBS ?? 4),
					onProgress: (done, count) => {
						if (done - last >= 200 || done === count) {
							last = done;
							logger.info(`pictures: ${done} of ${count} files`);
						}
					},
				});
				logger.info(`Served ${total} picture files (${encoded} AVIFs derived, the others copied or from the cache) in ${((performance.now() - started) / 1000).toFixed(1)} s.`);
				const moved = writeFallbackPages(context.settings, (await context.index()).pages, fileURLToPath(dir));
				if (moved) logger.info(`Wrote the fallback pages of ${moved} moved page${moved === 1 ? '' : 's'}.`);
				// Every page's footer links it (src/components/Footer.astro); bookProblems checked its first line.
				copyFileSync(path.join(context.settings.root, 'LICENSE'), path.join(fileURLToPath(dir), 'license.txt'));
			},
		},
	};
}

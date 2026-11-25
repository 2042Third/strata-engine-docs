// The Strata Engine Book's site. Where it is served is the only thing that changes between places, and site.json holds
// it: its base (the path prefix of every URL; "/" for a domain of its own) and its origin (for canonical links and the
// sitemap). For one build (another base, a test server) DOCS_BASE and DOCS_SITE override the two values.
//   DOCS_RELEASE=1   a release build: placeholders, unshot pictures and draft pages fail it, and so does an origin
//                    that is not a real https one
// Content never writes the prefix: links are relative .md paths that src/plugins/links.mjs turns into URLs.

import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';
import { unified } from '@astrojs/markdown-remark';
import { fileURLToPath } from 'node:url';
import { assetsInlineLimit, katexWoff2Only } from './src/lib/assets.mjs';
import { c_SearchRanking } from './src/lib/search.mjs';
import { readSettings, withBase } from './src/lib/settings.mjs';
import { starlightSidebar } from './src/lib/sidebar.mjs';
import { sitemapFilter } from './src/lib/sitemap.mjs';
import { watchIgnored } from './src/lib/watch.mjs';
import { bookMarkdown, createBookContext, inputsDigest } from './src/plugins/index.mjs';
import { bookIntegration } from './src/integrations/book.mjs';

const root = fileURLToPath(new URL('.', import.meta.url));
const command = process.argv.slice(2).includes('dev') ? 'dev' : 'build';
const settings = readSettings({ root, command });
const context = createBookContext(settings);
const index = await context.index();
const markdown = bookMarkdown(context, { digest: inputsDigest(settings, index) });

export default defineConfig({
	site: settings.site,
	base: settings.base || '/',
	trailingSlash: 'always',
	build: { format: 'directory' },
	// Astro's own cache (the rendered pages it reuses) beside the book's (.cache/images, .cache/diagrams): one folder to
	// keep between builds, and never shared through node_modules with another copy of the project. A build for another
	// base renders every page anew (the base is part of the inputs digest), so it keeps its pages in a folder of its
	// own: CI's builds at "/" and "/x/y" leave the cache of site.json's base as they found it.
	cacheDir: settings.base === settings.siteFile.base ? './.cache/astro' : `./.cache/astro-base${settings.base.replace(/\//g, '-') || '-root'}`,
	// Astro 7's default ('jsx') may drop the space between inline elements; prose needs it kept.
	compressHTML: true,
	// The content store (every page's rendered HTML, about 136 MB for the whole book) is kept in chunks of 20 MB. In one
	// file the build inlines it into a single module, JSON.parse("…") of the whole store, and V8 aborts compiling it
	// ("Zone Allocation failed" at "Building static entrypoints"); a build that leaves a few pages out stays below that.
	experimental: { collectionStorage: 'chunked' },
	// No font becomes a data: URL, which the release's policy (font-src 'self') would block (src/lib/assets.mjs). The dev
	// server leaves the ignored folders of tools and output unwatched (src/lib/watch.mjs). KaTeX's fonts are served as
	// WOFF2 only (src/lib/assets.mjs).
	vite: { build: { assetsInlineLimit }, plugins: [katexWoff2Only()], server: { watch: { ignored: watchIgnored(root) } } },
	markdown: {
		processor: unified({ remarkPlugins: markdown.remarkPlugins, rehypePlugins: markdown.rehypePlugins }),
	},
	integrations: [
		starlight({
			title: 'The Strata Engine Book',
			description: 'How a game engine works, and how to make games with one.',
			favicon: '/favicon.svg',
			defaultLocale: 'root',
			locales: { root: { label: 'English', lang: 'en' } },
			sidebar: starlightSidebar(context.sidebar),
			// No editLink and no social links: the book's repository is not public, so the site links nowhere in it.
			pagination: true,
			lastUpdated: false,
			// Search's ranking, which the search test ranks with too (src/lib/search.mjs).
			pagefind: { ranking: c_SearchRanking },
			tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
			markdown: { headingLinks: true },
			head: [{ tag: 'link', attrs: { rel: 'manifest', href: withBase(settings.base, '/manifest.webmanifest') } }],
			customCss: [
				'@fontsource-variable/source-serif-4',
				'@fontsource-variable/inter',
				'@fontsource-variable/jetbrains-mono',
				'katex/dist/katex.min.css',
				'./src/styles/book.css',
				'./src/styles/print.css',
			],
			components: {
				PageTitle: './src/components/PageTitle.astro',
				// The sidebar's markup without Starlight's scoped classes and inline carets (rulings-13, R59).
				Sidebar: './src/components/Sidebar.astro',
				Pagination: './src/components/Pagination.astro',
				Footer: './src/components/Footer.astro',
			},
			// The 404 page names no canonical URL and is not indexed (src/routeData.mjs).
			routeMiddleware: './src/routeData.mjs',
		}),
		// The book's own sitemap, without the print views and the 404 page; with it present, Starlight adds none.
		sitemap({ filter: sitemapFilter(settings) }),
		bookIntegration(context),
	],
});

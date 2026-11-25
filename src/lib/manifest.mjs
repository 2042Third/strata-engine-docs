// The web manifest (site.md, "The base path", rule 6): its start URL and scope are the book's root under the base and
// its icon the favicon, all built by src/lib/settings.mjs. src/pages/manifest.webmanifest.ts serves it as
// application/manifest+json.

import { pageUrl, withBase } from './settings.mjs';

/** The manifest of the book served under `base` ("" for the root of a host, "/a/b" otherwise). */
export function webManifest(base) {
	return {
		name: 'The Strata Engine Book',
		short_name: 'Strata Book',
		description: 'How a game engine works, and how to make games with one.',
		lang: 'en',
		start_url: pageUrl(base, 'index'),
		scope: pageUrl(base, 'index'),
		display: 'standalone',
		background_color: '#17181c',
		theme_color: '#17181c',
		icons: [{ src: withBase(base, '/favicon.svg'), sizes: 'any', type: 'image/svg+xml' }],
	};
}

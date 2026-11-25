// Starlight's route middleware (src/routeData.mjs).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { notFoundHead } from '../../routeData.mjs';

test('the 404 page names no canonical URL and is not indexed', () => {
	const head = notFoundHead([
		{ tag: 'link', attrs: { rel: 'canonical', href: 'https://example.com/strata-engine-docs/404/' } },
		{ tag: 'meta', attrs: { property: 'og:url', content: 'https://example.com/strata-engine-docs/404/' } },
		{ tag: 'meta', attrs: { property: 'og:title', content: 'Page not found' } },
	]);
	assert.deepEqual(head, [
		{ tag: 'meta', attrs: { property: 'og:title', content: 'Page not found' } },
		{ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } },
	]);
});

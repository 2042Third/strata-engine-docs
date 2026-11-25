// Starlight's route middleware: changes to a page's route data before it renders. The 404 page is served for every
// address that is not a page, so the canonical link and og:url Starlight gives it (<site><base>/404/) name an address
// that itself answers 404; it gets neither, and robots are asked not to index it.

import { defineRouteMiddleware } from '@astrojs/starlight/route-data';

/** The head entries of the 404 page: without canonical and og:url, with "noindex". */
export function notFoundHead(head) {
	const kept = head.filter((item) => !(item.tag === 'link' && item.attrs?.rel === 'canonical') && !(item.tag === 'meta' && item.attrs?.property === 'og:url'));
	kept.push({ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } });
	return kept;
}

export const onRequest = defineRouteMiddleware((context) => {
	const route = context.locals.starlightRoute;
	if (route.entry.id === '404') route.head = notFoundHead(route.head);
});

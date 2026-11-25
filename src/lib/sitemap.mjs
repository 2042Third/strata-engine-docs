// The sitemap (plan/site.md, "Framework and versions" and "Navigation"): the book adds its own @astrojs/sitemap
// instance, so Starlight adds none, and this filter leaves out the pages that are not for finding: the print views
// (one long page per part, "noindex") and the 404 page. The sitemap's URLs are the origin, the base and the page's
// path, like every canonical link.

const c_Unlisted = ['print', '404'];

/** The sitemap's filter for the build's settings: true for a URL the sitemap lists. */
export function sitemapFilter({ site, base }) {
	const root = `${site}${base}/`;
	return (url) => {
		if (!url.startsWith(root)) return true;
		return !c_Unlisted.includes(url.slice(root.length).split('/')[0]);
	};
}

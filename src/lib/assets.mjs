// How Vite treats the files the site's style sheets and scripts load. The Content Security Policy that the release
// sends (tools/release.py) allows fonts only from the site itself (`font-src 'self'`), and Vite inlines small files as
// `data:` URLs: a font inlined that way would be blocked on every page that needs it (rulings 6, R23). So no font is
// ever inlined; every other file keeps Vite's own rule (its 4 KB limit).

export const c_FontFile = /\.(woff2?|ttf|otf|eot)$/i;

/**
 * Vite's `build.assetsInlineLimit` as a function: false (never inline) for a font file, undefined (Vite decides) for any
 * other file. The file may carry a query (`?url`).
 */
export function assetsInlineLimit(filePath) {
	return c_FontFile.test(String(filePath).split('?')[0]) ? false : undefined;
}

// KaTeX's style sheet offers each of its 20 fonts as WOFF2, WOFF and TrueType. Every browser the book serves (one that
// shows AVIF) loads the WOFF2 and never asks for the others, which were 0.8 MB of every release (rulings-13, R59).
const c_KatexSheet = /[\\/]katex[\\/]dist[\\/]katex(\.min)?\.css$/;
const c_OlderFormats = /,url\([^)]*\.(?:woff|ttf)\) format\("(?:woff|truetype)"\)/g;

/** KaTeX's style sheet with only the WOFF2 file of each font; throws when the sheet's form is not the one expected. */
export function woff2Only(css) {
	const result = css.replace(c_OlderFormats, '');
	if (/\.(woff|ttf)\)/.test(result) || !/\.woff2\) format\("woff2"\)/.test(result)) {
		throw new Error('katex.min.css: its @font-face rules are not "woff2, woff, truetype": update woff2Only in src/lib/assets.mjs');
	}
	return result;
}

/** A Vite plugin that serves KaTeX's style sheet through woff2Only, so the WOFF and TrueType files are not emitted. */
export function katexWoff2Only() {
	return {
		name: 'strata-book-katex-woff2',
		enforce: 'pre',
		transform(code, id) {
			return c_KatexSheet.test(String(id).split('?')[0]) ? { code: woff2Only(code), map: null } : null;
		},
	};
}

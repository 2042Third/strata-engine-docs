// What `astro dev` does not watch (plan/site.md, budget row 6): the project's ignored folders of tools and output.
// Vite watches the whole project, and here that includes .tools/ (the toolchain, Playwright's browsers, npm's cache, the
// scale test's book), dist/, stage/, release/, originals/ and .cache/: walking them kept the dev server from starting,
// and its handles on them kept builds and crawls of the scale book from removing their folders.

import path from 'node:path';

/** The folders of a book's root that the dev server leaves unwatched, as .gitignore lists them. */
export const c_UnwatchedFolders = ['.tools', 'dist', 'stage', 'release', 'originals', '.cache'];

/**
 * Vite's `server.watch.ignored` for a book at `root`: a function that is true for a path inside one of the root's
 * unwatched folders. It compares paths below this root only, so a book whose root lies inside another project's
 * .tools/ (the scale test's) still watches its own sources.
 */
export function watchIgnored(root) {
	const folders = c_UnwatchedFolders.map((name) => path.resolve(root, name));
	const key = (file) => (process.platform === 'win32' ? file.toLowerCase() : file);
	const prefixes = folders.map((folder) => key(folder));
	return (file) => {
		const resolved = key(path.resolve(String(file)));
		return prefixes.some((prefix) => resolved === prefix || resolved.startsWith(`${prefix}${path.sep}`));
	};
}

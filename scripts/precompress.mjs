// Writes a gzip copy beside every text file of 1 KB or more of a built site, for nginx's gzip_static (plan/site.md,
// "What a release holds"; rulings 6, R23):
//
//     node scripts/precompress.mjs [--dist dist]
//
// The text files are those of c_Extensions; Pagefind's own files (.pf_*, .pagefind) are compressed by Pagefind and get
// none. No .br file is written: no stock nginx serves brotli. A .gz is written only when its bytes change, so a second
// run changes nothing, and every .gz is the same on every machine (no time stamp, no file name, the "unknown" system
// byte): two releases of one build are byte for byte equal. A .gz beside a file that no longer needs one (a file under
// 1 KB) is removed. A .br in the site, or a .gz beside no file of its name, is refused: something else wrote it.
// tools/release.py checks the result before it packs the site. Exit codes: 0 written, 1 refused, 2 usage errors.

import { existsSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { constants, gzipSync } from 'node:zlib';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_Extensions = ['.html', '.css', '.js', '.mjs', '.json', '.svg', '.xml', '.txt', '.webmanifest'];
export const c_MinimumBytes = 1024;
// Byte 9 of a gzip header names the system that wrote it; zlib writes its own (3 on Linux, 10 on Windows). 255 is
// "unknown", so the file does not depend on where the release was made.
const c_UnknownSystem = 255;

/** Whether a file of the site gets a .gz beside it: a text file of c_Extensions with at least c_MinimumBytes. */
export function wantsGzip(name, size) {
	return c_Extensions.includes(path.extname(name).toLowerCase()) && size >= c_MinimumBytes;
}

/** The gzip bytes of `data`: the best compression, no time stamp, no name, the "unknown" system. */
export function gzipOf(data) {
	const packed = gzipSync(data, { level: constants.Z_BEST_COMPRESSION });
	packed[9] = c_UnknownSystem;
	return packed;
}

function listFiles(folder, relative = '') {
	return readdirSync(path.join(folder, relative), { withFileTypes: true }).flatMap((entry) => {
		const child = relative ? `${relative}/${entry.name}` : entry.name;
		return entry.isDirectory() ? listFiles(folder, child) : [child];
	});
}

/**
 * Precompresses the site in `folder`. Returns `{ written, kept, removed, problems }`: the .gz files written and kept
 * unchanged, those removed, and what is refused (a .br file, a .gz without its file). Nothing is written when there are
 * problems.
 */
export function precompress(folder) {
	const files = listFiles(folder).sort();
	const present = new Set(files);
	const problems = [];
	for (const file of files) {
		if (file.endsWith('.br')) problems.push(`${file}: the release holds no .br file (no stock nginx serves brotli); remove it`);
		if (file.endsWith('.gz') && !present.has(file.slice(0, -3))) problems.push(`${file}: a .gz beside no file of its name; remove it`);
	}
	const result = { written: [], kept: [], removed: [], problems };
	if (problems.length) return result;
	for (const file of files) {
		if (file.endsWith('.gz')) continue;
		const source = path.join(folder, ...file.split('/'));
		const target = `${source}.gz`;
		if (!wantsGzip(file, statSync(source).size)) {
			if (existsSync(target)) {
				rmSync(target);
				result.removed.push(`${file}.gz`);
			}
			continue;
		}
		const packed = gzipOf(readFileSync(source));
		if (existsSync(target) && readFileSync(target).equals(packed)) {
			result.kept.push(`${file}.gz`);
			continue;
		}
		writeFileSync(target, packed);
		result.written.push(`${file}.gz`);
	}
	return result;
}

export function main(argv) {
	let dist = path.join(c_Root, 'dist');
	for (let index = 0; index < argv.length; index += 1) {
		const argument = argv[index];
		if (argument === '--dist' && argv[index + 1]) dist = path.resolve(argv[(index += 1)]);
		else if (argument.startsWith('--dist=')) dist = path.resolve(argument.slice('--dist='.length));
		else {
			console.error(`precompress: unknown argument ${argument}\nusage: node scripts/precompress.mjs [--dist <built site>]`);
			return 2;
		}
	}
	if (!existsSync(path.join(dist, 'index.html'))) {
		console.error(`precompress: ${dist} has no index.html: build the site first`);
		return 2;
	}
	const { written, kept, removed, problems } = precompress(dist);
	for (const problem of problems) console.error(`precompress: ${problem}`);
	if (problems.length) return 1;
	console.log(`precompress: ${written.length} .gz written, ${kept.length} unchanged, ${removed.length} removed in ${dist}`);
	return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = main(process.argv.slice(2));

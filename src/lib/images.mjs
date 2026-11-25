// The pictures the site serves (plan/site.md "Pictures"). A published picture (src/assets/figures/…) is served
// unchanged, under a name that carries the first 10 hex digits of its SHA-256, the only hash in a picture's name:
// <base>/_figures/<part>/<chapter>/<figure>[-<variant>][-<crop>].<hash>.<width>.<ext>. A lossy picture (AVIF) also gets
// an AVIF 960 pixels wide made from it, and one 1920 wide when it is wider still (a 3840 capture), at quality 80 and
// effort 2 (rulings-5 R15); they are kept in .cache/images/ between builds. Lossless pictures (WebP) get no derived
// file, and drawings (SVG) are inlined into the page. Published pictures with the same bytes (one capture shown by two
// figures) are served once, under the name of the first of them in path order (servedAs; rulings-13 R59).

import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, rename, stat, unlink } from 'node:fs/promises';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';
import { withBase } from './settings.mjs';

export const c_DerivedWidths = [960, 1920];
// Effort 2, not the published files' 4: on 1920-pixel renders effort 4 took 3.8 s a picture against 0.39 s, for files
// about 15 % smaller, and a cold build of the full book's pictures 26 minutes instead of under three (rulings-5 R15).
export const c_DerivedAvif = { quality: 80, effort: 2, chromaSubsampling: '4:4:4' };
// Part of a derived file's name in the cache (not of its served name, which the plan gives): a change of the settings
// or of sharp's version encodes every derived file again.
export const c_EncoderKey = createHash('sha256').update(JSON.stringify({ c_DerivedAvif, sharp: sharp.versions })).digest('hex').slice(0, 8);
export const c_Types = { avif: 'image/avif', webp: 'image/webp' };

const s_Descriptions = new Map();
// Pictures folder: { sizes: Map<relative path, bytes>, bySize: Map<bytes, [relative paths, in path order]> }.
const s_Published = new Map();

/**
 * The format of a picture's bytes, read from its first bytes: "avif", "webp" (with `lossless`, true for VP8L), "png",
 * "jpeg", "gif", "svg", or null.
 */
export function sniffFormat(bytes) {
	const ascii = (start, end) => bytes.subarray(start, end).toString('latin1');
	if (bytes.length >= 16 && ascii(4, 8) === 'ftyp') {
		// The file type box: its major brand, a minor version, then the compatible brands, four bytes each.
		const end = Math.min(bytes.readUInt32BE(0), bytes.length);
		const brands = [ascii(8, 12)];
		for (let offset = 16; offset + 4 <= end; offset += 4) brands.push(ascii(offset, offset + 4));
		if (brands.some((brand) => brand === 'avif' || brand === 'avis')) return { format: 'avif', lossless: null };
	}
	if (bytes.length >= 16 && ascii(0, 4) === 'RIFF' && ascii(8, 12) === 'WEBP') {
		// A simple file is one VP8 (lossy) or VP8L (lossless) chunk; an extended one (VP8X) lists its chunks after it.
		for (let offset = 12; offset + 8 <= bytes.length;) {
			const chunk = ascii(offset, offset + 4);
			if (chunk === 'VP8L') return { format: 'webp', lossless: true };
			if (chunk === 'VP8 ') return { format: 'webp', lossless: false };
			const size = bytes.readUInt32LE(offset + 4);
			offset += 8 + size + (size % 2);
		}
		return { format: 'webp', lossless: null };
	}
	if (bytes.length >= 8 && bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return { format: 'png', lossless: true };
	if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return { format: 'jpeg', lossless: false };
	if (bytes.length >= 6 && ['GIF87a', 'GIF89a'].includes(ascii(0, 6))) return { format: 'gif', lossless: true };
	if (/<svg\b/i.test(bytes.subarray(0, 4096).toString('utf8'))) return { format: 'svg', lossless: null };
	return null;
}

/** Size, format and SHA-256 of a published picture (cached by modification time and size). */
export async function describePicture(file) {
	const info = await stat(file);
	const cached = s_Descriptions.get(file);
	if (cached && cached.mtimeMs === info.mtimeMs && cached.size === info.size) return cached.description;
	const bytes = await readFile(file);
	const hash = createHash('sha256').update(bytes).digest('hex');
	const sniffed = sniffFormat(bytes) ?? { format: null, lossless: null };
	let width = null;
	let height = null;
	if (sniffed.format === 'svg') {
		({ width, height } = svgSize(bytes.toString('utf8'), file));
	} else if (sniffed.format) {
		const metadata = await sharp(bytes).metadata();
		width = metadata.width;
		height = metadata.height;
	}
	const description = { file, hash, width, height, format: sniffed.format, lossless: sniffed.lossless, svg: sniffed.format === 'svg' };
	s_Descriptions.set(file, { mtimeMs: info.mtimeMs, size: info.size, description });
	return description;
}

/** The width and height of an SVG drawing from its viewBox (or width and height attributes). */
export function svgSize(text, file = 'drawing') {
	const open = /<svg\b[^>]*>/i.exec(text)?.[0];
	if (!open) throw new Error(`${file}: not an SVG drawing`);
	const viewBox = /\sviewBox\s*=\s*["']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*["']/i.exec(open);
	if (viewBox) return { width: Math.round(Number(viewBox[1])), height: Math.round(Number(viewBox[2])) };
	const width = /\swidth\s*=\s*["']([\d.]+)(px)?["']/i.exec(open);
	const height = /\sheight\s*=\s*["']([\d.]+)(px)?["']/i.exec(open);
	if (width && height) return { width: Math.round(Number(width[1])), height: Math.round(Number(height[1])) };
	throw new Error(`${file}: the drawing needs a viewBox`);
}

/** The published pictures (AVIF and WebP) below `picturesDir`, by relative path and by size. */
function listPublished(picturesDir) {
	const sizes = new Map();
	const bySize = new Map();
	const walk = (folder, prefix) => {
		for (const entry of readdirSync(folder, { withFileTypes: true })) {
			const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
			if (entry.isDirectory()) walk(path.join(folder, entry.name), relative);
			else if (/\.(avif|webp)$/.test(entry.name)) {
				const size = statSync(path.join(folder, entry.name)).size;
				sizes.set(relative, size);
				if (!bySize.has(size)) bySize.set(size, []);
				bySize.get(size).push(relative);
			}
		}
	};
	walk(picturesDir, '');
	for (const list of bySize.values()) list.sort();
	return { sizes, bySize };
}

/**
 * The relative path whose name a published picture is served under: the first, in path order, of the published
 * pictures with its bytes, so that a file two figures publish (one capture shown twice) is served and downloaded once.
 * Only files of the same size are read. The folder is listed once, and again when it holds a picture the list lacks;
 * a list that is out of date (the dev server, after a retake) can only miss a twin, which then serves under its own name.
 */
export async function servedAs(picturesDir, relative, description) {
	let published = s_Published.get(picturesDir);
	if (!published || !published.sizes.has(relative)) {
		published = listPublished(picturesDir);
		s_Published.set(picturesDir, published);
	}
	for (const candidate of published.bySize.get(published.sizes.get(relative)) ?? []) {
		if (candidate >= relative) break;
		if ((await describePicture(path.join(picturesDir, ...candidate.split('/')))).hash === description.hash) return candidate;
	}
	return relative;
}

/** The widths of the AVIFs derived from a lossy picture `width` pixels wide: 960, and 1920, each when narrower. */
export function derivedWidths(width) {
	return c_DerivedWidths.filter((candidate) => candidate < width);
}

/**
 * The files the site serves for a published picture: `{ kind, format, width, height, url, output, source, cache }`,
 * the published file itself first (kind "published", copied unchanged), then the derived AVIFs of a lossy picture
 * (kind "derived", narrowest first). `relative` is the path below the pictures folder whose name the picture is served
 * under ("core/time/fixed-step-off.avif"; servedAs); `outputDir` is the built site (null for the dev server).
 */
export function servedFiles({ base, cacheDir, outputDir }, description, relative) {
	const extension = path.extname(relative).slice(1);
	const stemPath = relative.slice(0, -(extension.length + 1));
	const short = description.hash.slice(0, 10);
	const served = (width) => {
		const name = `${stemPath}.${short}.${width}.${extension}`;
		return { url: withBase(base, `/_figures/${name}`), output: outputDir ? path.join(outputDir, '_figures', ...name.split('/')) : null };
	};
	const files = [{ kind: 'published', format: extension, width: description.width, height: description.height, source: description.file, cache: null, ...served(description.width) }];
	if (description.format !== 'avif') return files;
	for (const width of derivedWidths(description.width)) {
		files.push({
			kind: 'derived',
			format: 'avif',
			width,
			height: Math.round((description.height * width) / description.width),
			source: description.file,
			cache: path.join(cacheDir, 'images', `${description.hash}-${c_EncoderKey}-${width}.avif`),
			...served(width),
		});
	}
	return files;
}

async function exists(file) {
	try {
		await stat(file);
		return true;
	} catch (error) {
		if (error.code === 'ENOENT') return false;
		throw error;
	}
}

/** Encodes one derived file into the cache unless it is there already; returns true when it encoded. */
export async function ensureEncoded(derived) {
	if (derived.kind !== 'derived') return false;
	if (await exists(derived.cache)) return false;
	await mkdir(path.dirname(derived.cache), { recursive: true });
	const partial = `${derived.cache}.${process.pid}.partial`;
	try {
		await sharp(derived.source).resize({ width: derived.width, kernel: 'lanczos3' }).avif(c_DerivedAvif).toFile(partial);
		await rename(partial, derived.cache);
	} catch (error) {
		await unlink(partial).catch(() => {});
		throw new Error(`cannot derive a ${derived.width}-pixel AVIF from ${derived.source}: ${error.message}`);
	}
	return true;
}

/** The file whose bytes a served file has: the published file itself, or its derived file in the cache. */
export function bytesOf(served) {
	return served.kind === 'derived' ? served.cache : served.source;
}

/** Runs `task` over `items` with at most `limit` running at once; rejects with the first failure after all settle. */
export async function runLimited(items, limit, task) {
	let next = 0;
	const failures = [];
	const worker = async () => {
		while (next < items.length) {
			const item = items[next++];
			try {
				await task(item);
			} catch (error) {
				failures.push(error);
			}
		}
	};
	await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
	if (failures.length) throw new AggregateError(failures, failures.map((error) => error.message).join('\n'));
}

/** Copies every served file into the built site, deriving (or taking from the cache) the AVIFs of lossy pictures. */
export async function publishServed(files, { concurrency = 4, onProgress } = {}) {
	// libvips threads per encode: with `concurrency` encodes at once this keeps the build to about `concurrency` cores.
	sharp.concurrency(1);
	let encoded = 0;
	let done = 0;
	await runLimited(files, concurrency, async (served) => {
		if (await ensureEncoded(served)) encoded++;
		await mkdir(path.dirname(served.output), { recursive: true });
		await copyFile(bytesOf(served), served.output);
		done++;
		onProgress?.(done, files.length);
	});
	return { encoded, total: files.length };
}

/** Reads a whole file synchronously (inlined SVG drawings). */
export function readText(file) {
	return readFileSync(file, 'utf8');
}

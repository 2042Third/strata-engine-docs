// Encodes the book's published pictures and compares two of them (plan/pipelines.md §5.7, plan/site.md "Pictures").
// tools/figures.py publish calls it: Python's standard library encodes neither AVIF nor WebP.
//
//     node scripts/encode-figures.mjs encode --publish <lossy|lossless> [--quality <n>] [--effort <n>] <png> <output>
//     node scripts/encode-figures.mjs diff <published file> <published file>
//
// encode  One format per picture, nothing resized: lossy is AVIF at --quality (80; 90 for both sides of a ::compare,
//         which the caller passes), chroma 4:4:4, effort 4; lossless is lossless WebP, effort 4. The output's extension
//         must be .avif for lossy and .webp for lossless. The input must be a PNG. It prints one line of JSON, the stamp's
//         encoder settings with sharp's and libvips' versions and the result:
//         {"format", "lossless", "quality", "chromaSubsampling", "effort", "sharp", "libvips", "width", "height", "bytes"}
//         (quality and chromaSubsampling only for AVIF).
// diff    Decodes two published files (as RGBA, 8 bits per channel) and prints {"mean", "largestBlockMean", "width",
//         "height"}: the mean absolute difference over all pixels and channels, and the largest such mean over a 16 x 16
//         block (blocks at the right and bottom edges hold what is left). tools/figures.py applies site.md's thresholds.
//
// Exit codes: 0 done; 1 a file could not be read, encoded or written, or the two pictures differ in size; 2 usage.

import { rename, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const c_Defaults = { lossy: { quality: 80, effort: 4 }, lossless: { effort: 4 } };
const c_Block = 16;

class UsageError extends Error {}

function parse(argv) {
	const [command, ...rest] = argv;
	if (command !== 'encode' && command !== 'diff') throw new UsageError('the first argument is encode or diff');
	const options = {};
	const files = [];
	for (let index = 0; index < rest.length; index++) {
		const argument = rest[index];
		if (argument === '--publish' || argument === '--quality' || argument === '--effort') {
			if (index + 1 >= rest.length) throw new UsageError(`${argument} needs a value`);
			options[argument.slice(2)] = rest[++index];
		} else if (argument.startsWith('--')) {
			throw new UsageError(`unknown option ${argument}`);
		} else {
			files.push(argument);
		}
	}
	if (files.length !== 2) throw new UsageError(`${command} takes two files`);
	return { command, options, files };
}

function integer(value, name, low, high) {
	if (!/^\d+$/.test(value)) throw new UsageError(`--${name} takes a whole number from ${low} to ${high}`);
	const number = Number(value);
	if (number < low || number > high) throw new UsageError(`--${name} takes a whole number from ${low} to ${high}`);
	return number;
}

/** The encoder settings of a picture: what the stamp records. */
function settingsFor(options) {
	const publish = options.publish;
	if (publish !== 'lossy' && publish !== 'lossless') throw new UsageError('--publish is lossy or lossless');
	const defaults = c_Defaults[publish];
	const effort = options.effort === undefined ? defaults.effort : integer(options.effort, 'effort', 0, publish === 'lossy' ? 9 : 6);
	if (publish === 'lossless') {
		if (options.quality !== undefined) throw new UsageError('--quality belongs to lossy pictures: lossless WebP has none');
		return { format: 'webp', lossless: true, effort };
	}
	const quality = options.quality === undefined ? defaults.quality : integer(options.quality, 'quality', 1, 100);
	return { format: 'avif', lossless: false, quality, chromaSubsampling: '4:4:4', effort };
}

async function encode(options, input, output) {
	const settings = settingsFor(options);
	const extension = path.extname(output).toLowerCase();
	if (extension !== `.${settings.format}`) throw new UsageError(`a ${options.publish} picture is published as .${settings.format}, not ${extension || 'a file without an extension'}`);
	const metadata = await sharp(input).metadata();
	if (metadata.format !== 'png') throw new Error(`${input} is not a PNG file (sharp reads it as ${metadata.format})`);
	let pipeline = sharp(input);
	pipeline = settings.lossless
		? pipeline.webp({ lossless: true, effort: settings.effort })
		: pipeline.avif({ quality: settings.quality, chromaSubsampling: settings.chromaSubsampling, effort: settings.effort, lossless: false });
	// Written beside the output first, so that a failed encode never leaves half a file under the published name.
	const partial = `${output}.partial`;
	try {
		const info = await pipeline.toFile(partial);
		await rename(partial, output);
		const bytes = (await stat(output)).size;
		return { ...settings, sharp: sharp.versions.sharp, libvips: sharp.versions.vips, width: info.width, height: info.height, bytes };
	} catch (error) {
		await rm(partial, { force: true });
		throw error;
	}
}

async function pixels(file) {
	const { data, info } = await sharp(file).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
	if (info.channels !== 4) throw new Error(`${file}: decoded with ${info.channels} channels, not 4`);
	return { data, width: info.width, height: info.height };
}

/** The mean absolute difference of two RGBA pictures of one size, and the largest mean over a 16 x 16 block. */
function difference(first, second) {
	const { width, height } = first;
	const columns = Math.ceil(width / c_Block);
	const rows = Math.ceil(height / c_Block);
	const sums = new Float64Array(columns * rows);
	const counts = new Float64Array(columns * rows);
	let total = 0;
	for (let y = 0; y < height; y++) {
		const row = Math.floor(y / c_Block) * columns;
		for (let x = 0; x < width; x++) {
			const offset = (y * width + x) * 4;
			let pixel = 0;
			for (let channel = 0; channel < 4; channel++) pixel += Math.abs(first.data[offset + channel] - second.data[offset + channel]);
			const block = row + Math.floor(x / c_Block);
			sums[block] += pixel;
			counts[block] += 4;
			total += pixel;
		}
	}
	let largest = 0;
	for (let block = 0; block < sums.length; block++) largest = Math.max(largest, sums[block] / counts[block]);
	return { mean: total / (width * height * 4), largestBlockMean: largest, width, height };
}

async function diff(firstFile, secondFile) {
	const [first, second] = await Promise.all([pixels(firstFile), pixels(secondFile)]);
	if (first.width !== second.width || first.height !== second.height) {
		throw new Error(`the pictures differ in size: ${firstFile} is ${first.width} x ${first.height}, ${secondFile} ${second.width} x ${second.height}`);
	}
	return difference(first, second);
}

async function main(argv) {
	let parsed;
	try {
		parsed = parse(argv);
		if (parsed.command === 'encode') {
			console.log(JSON.stringify(await encode(parsed.options, parsed.files[0], parsed.files[1])));
		} else {
			if (Object.keys(parsed.options).length) throw new UsageError('diff takes no options');
			console.log(JSON.stringify(await diff(parsed.files[0], parsed.files[1])));
		}
		return 0;
	} catch (error) {
		console.error(`encode-figures: ${error.message}`);
		return error instanceof UsageError ? 2 : 1;
	}
}

process.exitCode = await main(process.argv.slice(2));

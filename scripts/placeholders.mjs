// Draws the placeholder pictures of the sample pages' figures: simple drawings, labelled "placeholder" in the picture
// itself, that stand in for the engine's renders until the pictures are taken from their recipes (tools/figures.py
// take and publish, after engine release 0.8.0). Each is drawn as a PNG of its recipe's size and published the way
// tools/figures.py publish publishes a picture (plan/pipelines.md §5.7), through scripts/encode-figures.mjs: a lossy
// render as AVIF at quality 80 (90 when the page shows the recipe on a ::compare slider), a lossless one as lossless
// WebP, and every crop of the recipe cut from the PNG at its own pixels, never resampled, as lossless WebP. Nothing
// stamps them in taken.json, so a draft labels them as placeholders and a release build refuses them. The PNG files are
// drawn in a temporary folder and removed: a placeholder is drawn again from this file, not kept as an original.
//
//     node scripts/placeholders.mjs [--root <book folder>]

import { execFile } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { promisify } from 'node:util';
import sharp from 'sharp';
import { captureSize, cropPixels, loadManifest, pictureName, publishOf, recipeCrops } from '../src/lib/figures.mjs';

const c_Here = path.dirname(fileURLToPath(import.meta.url));
const c_Encoder = path.join(c_Here, 'encode-figures.mjs');
export const c_LossyQuality = 80;
export const c_CompareQuality = 90;

function frame(width, height, body, label) {
	return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 1920 1080" preserveAspectRatio="none">
	<defs>
		<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d6fa8"/><stop offset="1" stop-color="#a9c6e0"/></linearGradient>
		<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4640"/><stop offset="1" stop-color="#26241f"/></linearGradient>
	</defs>
	<rect width="1920" height="700" fill="url(#sky)"/>
	<rect y="700" width="1920" height="380" fill="url(#ground)"/>
	${body}
	<rect x="40" y="40" width="760" height="120" rx="16" fill="#000" fill-opacity="0.65"/>
	<text x="70" y="92" font-family="Arial, Helvetica, sans-serif" font-size="44" font-weight="700" fill="#fff">PLACEHOLDER PICTURE</text>
	<text x="70" y="140" font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#ddd">${label}</text>
</svg>`;
}

function robot(x, opacity) {
	return `<g opacity="${opacity}"><rect x="${x - 60}" y="420" width="120" height="200" rx="30" fill="#d8dde3"/><circle cx="${x}" cy="370" r="55" fill="#d8dde3"/>
		<rect x="${x - 50}" y="620" width="40" height="90" fill="#9aa3ad"/><rect x="${x + 10}" y="620" width="40" height="90" fill="#9aa3ad"/></g>`;
}

// The pictures drawn: the page, the recipe, its variant, and the drawing (in a 1920 x 1080 view, scaled to the size).
export const c_Pictures = [
	{ page: 'core/time', figure: 'interpolation-off-on', variant: 'off', body: `${robot(760, 0.5)}${robot(760, 0.5)}${robot(760, 0.5)}${robot(1160, 0.85)}`, label: 'Not rendered by the engine: four frames without interpolation' },
	{ page: 'core/time', figure: 'interpolation-off-on', variant: 'on', body: `${robot(860, 0.45)}${robot(960, 0.55)}${robot(1060, 0.7)}${robot(1160, 0.85)}`, label: 'Not rendered by the engine: four frames with interpolation' },
	{
		page: 'make/first-script',
		figure: 'spinning-cube',
		variant: null,
		body: `<polygon points="860,560 1060,520 1160,600 960,640" fill="#b9bec4"/><polygon points="860,560 960,640 960,820 860,740" fill="#8c9197"/>
			<polygon points="960,640 1160,600 1160,780 960,820" fill="#a3a8ae"/>
			<path d="M 820 470 A 220 70 0 0 1 1200 470" fill="none" stroke="#f4b860" stroke-width="10" marker-end="url(#arrow)"/>
			<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#f4b860"/></marker></defs>`,
		label: 'Not rendered by the engine: the spinning cube',
	},
];

/** Whether a page shows the recipe `figure` with ::compare (both sides of a slider are encoded at quality 90). */
export function onSlider(pageText, figure) {
	return new RegExp(`^\\s*:{2,}compare\\{[^}]*\\bid=["']?${figure.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["']?[\\s}]`, 'm').test(pageText);
}

/**
 * What placeholders.mjs writes for one picture: `[{ output, publish, quality, crop }]`, the picture itself first, then
 * each crop of its recipe (`crop`: the rectangle in the picture's pixels). Throws when the recipe is missing or does
 * not have the variant.
 */
export function placeholderJobs(root, picture, pageText) {
	const figuresDir = path.join(root, 'src', 'content', 'figures');
	const entry = loadManifest(figuresDir, picture.page)?.figures.get(picture.figure);
	if (!entry) throw new Error(`src/content/figures/${picture.page}.json has no figure "${picture.figure}"`);
	if (picture.variant && !Object.hasOwn(entry.variants ?? {}, picture.variant)) throw new Error(`figure "${picture.figure}" has no variant "${picture.variant}"`);
	const publish = publishOf(entry);
	if (publish !== 'lossy' && publish !== 'lossless') throw new Error(`figure "${picture.figure}" is published as ${publish}, not as a picture`);
	const folder = path.join(root, 'src', 'assets', 'figures', ...picture.page.split('/'));
	const [width, height] = captureSize(entry);
	const jobs = [{ output: path.join(folder, pictureName(entry, picture.variant)), publish, quality: publish === 'lossy' ? (onSlider(pageText, picture.figure) ? c_CompareQuality : c_LossyQuality) : null, crop: null, width, height }];
	for (const crop of recipeCrops(entry)) {
		const [x0, y0, x1, y1] = cropPixels(crop.rect, width, height);
		jobs.push({ output: path.join(folder, pictureName(entry, picture.variant, crop.name)), publish: 'lossless', quality: null, crop: { left: x0, top: y0, width: x1 - x0, height: y1 - y0 }, width, height });
	}
	return { entry, jobs };
}

/** The arguments of scripts/encode-figures.mjs for one job. */
export function encoderArguments(job, png) {
	return [c_Encoder, 'encode', '--publish', job.publish, ...(job.quality === null ? [] : ['--quality', String(job.quality)]), png, job.output];
}

async function main(argv) {
	const rootIndex = argv.indexOf('--root');
	const root = rootIndex >= 0 ? path.resolve(argv[rootIndex + 1]) : path.resolve(c_Here, '..');
	const run = promisify(execFile);
	const work = await mkdtemp(path.join(tmpdir(), 'strata-placeholders-'));
	try {
		for (const picture of c_Pictures) {
			const pageText = await readFile(path.join(root, 'src', 'content', 'docs', `${picture.page}.md`), 'utf8');
			const { jobs } = placeholderJobs(root, picture, pageText);
			const original = path.join(work, `${path.basename(jobs[0].output)}.png`);
			await sharp(Buffer.from(frame(jobs[0].width, jobs[0].height, picture.body, picture.label))).png().toFile(original);
			for (const job of jobs) {
				let png = original;
				if (job.crop) {
					png = path.join(work, `${path.basename(job.output)}.png`);
					await sharp(original).extract(job.crop).png().toFile(png);
				}
				await mkdir(path.dirname(job.output), { recursive: true });
				const { stdout } = await run(process.execPath, encoderArguments(job, png));
				console.log(`wrote ${path.relative(root, job.output).split(path.sep).join('/')}: ${stdout.trim()}`);
			}
		}
	} finally {
		await rm(work, { recursive: true, force: true });
	}
	return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
	try {
		process.exitCode = await main(process.argv.slice(2));
	} catch (error) {
		console.error(`placeholders: ${error.message}`);
		process.exitCode = 1;
	}
}

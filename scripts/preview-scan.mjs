// Preview only (PREVIEW.md): renders every page through the book's Markdown plugins, as a preview build does, and
// prints every page's problems in one run (a build stops at the first failing page). The pages of
// scripts/preview-omit.txt are skipped. Run from the book's folder: node scripts/preview-scan.mjs
import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { render } from '../src/plugins/tests/helpers.mjs';

const root = process.cwd();
const docs = path.join(root, 'src', 'content', 'docs');
const omitted = readFileSync(path.join(root, 'scripts', 'preview-omit.txt'), 'utf8').split('\n').map((line) => line.trim()).filter((line) => line && !line.startsWith('#'));
const env = { DOCS_PREVIEW: '1', DOCS_PREVIEW_OMIT: omitted.join(','), DOCS_BASE: '/strata-engine-docs' };
const ids = [];
const walk = (folder) => {
	for (const name of readdirSync(folder)) {
		const file = path.join(folder, name);
		if (statSync(file).isDirectory()) walk(file);
		else if (name.endsWith('.md') && !name.startsWith('_')) ids.push(path.relative(docs, file).split(path.sep).join('/').slice(0, -'.md'.length));
	}
};
walk(docs);
let failing = 0;
for (const id of ids.sort().filter((page) => !omitted.includes(page))) {
	try {
		await render(root, id, { env });
	} catch (error) {
		failing++;
		console.log(String(error.message));
	}
}
console.log(`preview-scan: ${ids.length} pages, ${omitted.length} left out, ${failing} failing`);
process.exitCode = failing ? 1 : 0;

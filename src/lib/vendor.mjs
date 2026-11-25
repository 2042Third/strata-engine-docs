// The libraries the engine vendors, as the build knows them (.tools/handover/vendor-format.md; plan/pipelines.md §3.2;
// plan/critique/rulings-6.md, R22 and R26 point 13). The build has no engine: the tool chain commits
// src/generated/vendor.json, which gives each folder of Strata/vendor/ the library's name, the version and the license
// that the engine's ThirdPartyNotices.md records at the pin, and the repository and commit of its submodule there. A
// quote of `vendor:<lib>/<path>` names them in its header and links the file at that commit.

import { readFileSync } from 'node:fs';

const c_Commit = /^[0-9a-f]{40}$/;

/**
 * The record of src/generated/vendor.json: `{ missing: true }`, `{ error }`, or `{ pin, libraries: Map<lib, { name,
 * version, license, repository, commit }> }`.
 */
export function loadVendor(file) {
	let text;
	try {
		text = readFileSync(file, 'utf8');
	} catch (error) {
		if (error.code === 'ENOENT') return { missing: true };
		throw error;
	}
	let data;
	try {
		data = JSON.parse(text);
	} catch (error) {
		return { error: `src/generated/vendor.json is not valid JSON: ${error.message}` };
	}
	if (!data || typeof data !== 'object' || Array.isArray(data)) return { error: 'src/generated/vendor.json is not a JSON object' };
	if (typeof data.pin !== 'string' || !c_Commit.test(data.pin)) return { error: 'src/generated/vendor.json has no "pin": the 40 hex digits of the engine commit it was written for' };
	if (!data.libraries || typeof data.libraries !== 'object' || Array.isArray(data.libraries)) return { error: 'src/generated/vendor.json has no "libraries": the folders of Strata/vendor/ and what the notices record of each' };
	const libraries = new Map();
	for (const [lib, entry] of Object.entries(data.libraries)) {
		const fields = ['name', 'version', 'license', 'repository', 'commit'];
		const missing = fields.filter((field) => typeof entry?.[field] !== 'string' || !entry[field].trim());
		if (missing.length) return { error: `src/generated/vendor.json: the library "${lib}" has no ${missing.join(', ')}` };
		if (!/^https:\/\/[^\s/]+\/\S+$/.test(entry.repository) || entry.repository.endsWith('/')) return { error: `src/generated/vendor.json: the repository of "${lib}" is not an https address of a repository: ${entry.repository}` };
		if (!c_Commit.test(entry.commit)) return { error: `src/generated/vendor.json: the commit of "${lib}" is not 40 hex digits` };
		libraries.set(lib, { name: entry.name, version: entry.version, license: entry.license, repository: entry.repository, commit: entry.commit });
	}
	return { pin: data.pin, libraries };
}

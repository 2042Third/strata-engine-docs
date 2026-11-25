// tabs: "::::tabs" holding ":::tab[Label]" blocks shows one panel at a time (the editor's UI, the command, the script;
// PowerShell and a POSIX shell). Without scripts every panel shows, each under its label. sync=<key> makes all tab sets
// with that key on the site follow the reader's last choice (stored in the browser, by the tab's label), so the two
// keys of the style guide have fixed labels (plan/style.md §10): sync=how ("In the editor", "With a command") and
// sync=os ("Windows", "Linux", "macOS").

import { element, report, takeDirectiveLabel, text } from './shared.mjs';

export const c_SyncLabels = { how: ['In the editor', 'With a command'], os: ['Windows', 'Linux', 'macOS'] };

export function remarkBookTabs() {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (parent, insideTabs) => {
				(parent.children ?? []).forEach((node, index) => {
					if (node.type === 'containerDirective' && node.name === 'tabs') {
						parent.children[index] = tabSet(file, node);
						return;
					}
					if (node.name === 'tab' && (node.type === 'containerDirective' || node.type === 'leafDirective') && !insideTabs) {
						report(file, node, ':::tab belongs inside ::::tabs (four colons around the set, three around each tab)');
						return;
					}
					visit(node, false);
				});
			};
			const tabSet = (file, node) => {
				const sync = node.attributes?.sync;
				if (sync !== undefined && !/^[a-z][a-z0-9-]*$/.test(sync)) report(file, node, `tabs sync="${sync}" must be a lowercase name such as os or how`);
				const panels = [];
				const labels = new Set();
				for (const child of node.children) {
					if (child.type !== 'containerDirective' || child.name !== 'tab') {
						report(file, child, 'a tab set holds only :::tab[Label] blocks');
						continue;
					}
					const label = takeDirectiveLabel(child);
					if (!label?.text.trim()) {
						report(file, child, 'a tab needs a label: :::tab[PowerShell]');
						continue;
					}
					if (labels.has(label.text)) report(file, child, `two tabs of one set are labelled "${label.text}"`);
					labels.add(label.text);
					visit(child, true);
					panels.push(element('div', { className: ['book-tabs__panel'], dataLabel: label.text }, [
						element('p', { className: ['book-tabs__label'] }, [text(label.text)]),
						...child.children,
					]));
				}
				if (panels.length < 2) report(file, node, 'a tab set holds at least two tabs');
				const fixed = c_SyncLabels[sync];
				if (fixed && JSON.stringify([...labels]) !== JSON.stringify(fixed)) report(file, node, `a tab set with sync=${sync} holds the tabs ${fixed.map((label) => `"${label}"`).join(', ')}, in this order (style.md §10); this one holds ${[...labels].map((label) => `"${label}"`).join(', ') || 'none'}`);
				return element('book-tabs', sync ? { dataSync: sync } : {}, panels);
			};
			visit(tree, false);
		};
	};
}

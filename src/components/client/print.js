// What printing a page opens: every closed answer and derivation (they are <details> elements, whose content a printer
// would leave out), closed again after printing so that the reader's page is as it was. book.js calls this on the
// browser's beforeprint and afterprint events; it touches nothing else and needs no browser to be tested.

export const c_PrintedDetails = 'details.book-answer, details.book-derivation';

/** Opens every closed answer and derivation under `root`; returns the function that closes them again. */
export function openForPrint(root) {
	const opened = [];
	for (const details of root.querySelectorAll(c_PrintedDetails)) {
		if (details.open) continue;
		details.open = true;
		opened.push(details);
	}
	return () => {
		for (const details of opened) details.open = false;
	};
}

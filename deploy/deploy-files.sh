#!/bin/sh
# Copies a new build over the served book without breaking a reader's open page:
#     deploy/deploy-files.sh <unpacked strata-engine-docs/ folder> <served folder>
# Pass 1 adds new files and deletes nothing, so a page loaded before the copy still finds its hashed files.
# Pass 2 deletes old files, but never archived versions (v0.8/ ...) or versions.json.
# rsync writes each file beside the old one and renames it over it, so a reader gets the old file or the new one,
# never half of one. Exit codes: 0 copied, 1 a copy failed, 2 wrong arguments or no rsync.
set -eu

if [ "$#" -ne 2 ]; then
	echo "usage: $0 <unpacked strata-engine-docs/ folder> <served folder>" >&2
	exit 2
fi
if ! command -v rsync >/dev/null 2>&1; then
	echo "$0: rsync is not installed (Debian and Ubuntu: apt install rsync)" >&2
	exit 2
fi
if [ ! -f "$1/index.html" ]; then
	echo "$0: $1 is not a built site: it has no index.html" >&2
	exit 2
fi
new="${1%/}/"
served="${2%/}/"
mkdir -p "$served"
if [ "$(cd "$new" && pwd -P)" = "$(cd "$served" && pwd -P)" ]; then
	echo "$0: the new site and the served folder are the same folder" >&2
	exit 2
fi

rsync -a "$new" "$served" || exit 1
rsync -a --delete --exclude '/v[0-9]*/' --exclude '/versions.json' "$new" "$served" || exit 1
echo "$0: copied $new over $served"

#!/bin/bash
set -euo pipefail

# Faithfully copy this directory into the destination repo (used by the public
# mirror). No name substitution: identifiers like the docker-compose service
# name and "computation-example" AEA hostname/routes are preserved as-is so the
# public repo stays consistent with the internal source and the smoke tests.

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <relative-path-to-destination-repo>"
    exit 1
fi

DEST_REPO_PATH=$1

if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude='.git' ./ "$DEST_REPO_PATH/"
else
    echo "rsync not found; using tar fallback (excluding .git)."
    tar --exclude='./.git' -cf - . | tar -xf - -C "$DEST_REPO_PATH"
fi

echo "Copy completed successfully."
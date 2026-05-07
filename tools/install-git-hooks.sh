#!/usr/bin/env bash
# Install the project's git hooks into .git/hooks/ for any fresh clone.
# Currently installs:
#   - commit-msg: rejects AI co-author trailers (see CONTRIBUTING.md).
set -euo pipefail
src="$(cd "$(dirname "$0")/.." && pwd)/tools/hooks"
dst="$(git rev-parse --git-path hooks)"
for h in "$src"/*; do
  base="$(basename "$h")"
  cp "$h" "$dst/$base"
  chmod +x "$dst/$base"
  echo "installed $base → $dst/"
done

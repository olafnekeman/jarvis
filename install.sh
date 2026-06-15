#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${JARVIS_REPO_URL:-https://github.com/olafnekeman/jarvis.git}"
INSTALL_DIR="${JARVIS_INSTALL_DIR:-/tmp/jarvis}"

echo "Cloning jarvis from ${REPO_URL}..."
git clone "$REPO_URL" "$INSTALL_DIR"

exec "$INSTALL_DIR/scripts/setup.sh"

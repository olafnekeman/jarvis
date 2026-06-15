#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== jarvis setup ==="

"$REPO_ROOT/scripts/preflight.sh"
"$REPO_ROOT/scripts/install-ollama.sh"
"$REPO_ROOT/scripts/configure-ollama.sh"

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

cd "$REPO_ROOT"
uv sync

uv run jarvis setup
uv run jarvis doctor

echo ""
echo "Setup complete. Run 'uv run jarvis run' to start jarvis."

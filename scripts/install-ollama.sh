#!/usr/bin/env bash
set -euo pipefail

if [[ "${OLLAMA_SKIP_INSTALL:-}" == "1" ]]; then
  echo "Skipping Ollama install (OLLAMA_SKIP_INSTALL=1)"
  exit 0
fi

if command -v ollama >/dev/null 2>&1; then
  echo "Ollama already installed: $(ollama --version)"
else
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl enable --now ollama
  echo "Ollama service enabled and started."
else
  echo "warning: systemctl not found — start Ollama manually with 'ollama serve'"
fi
